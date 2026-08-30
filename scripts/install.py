#!/usr/bin/env python3
"""Install Heading with an explicit, non-destructive deployment."""

from __future__ import annotations

import argparse
from contextlib import AbstractContextManager, ExitStack
from dataclasses import dataclass
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
from typing import Iterable


ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = ROOT / "plugins" / "heading"
RUNTIME_ROOT = ROOT / "runtime" / "heading"
PRODUCT = "heading"
SKILLS = (
    "heading-prototype",
    "heading-build",
    "heading-sweep",
    "heading-grow",
    "heading-maintain",
    "heading-orchestrate",
)
LOCK_NAME = ".heading-deploy.lock"
MACOS_SYSTEM_ALIASES = {
    "/var": "/private/var",
    "/tmp": "/private/tmp",
    "/etc": "/private/etc",
}


class InstallError(RuntimeError):
    """An installation invariant failed."""


@dataclass(frozen=True)
class Item:
    root: str
    source: Path
    relative: Path
    mode: int
    digest: str


@dataclass(frozen=True)
class Action:
    kind: str
    path: Path
    digest: str | None = None
    previous_mode: int | None = None


class DeploymentLock(AbstractContextManager["DeploymentLock"]):
    def __init__(self, path: Path, *, create: bool) -> None:
        self.path = path
        self.create = create
        self.fd: int | None = None

    def __enter__(self) -> "DeploymentLock":
        flags = os.O_RDWR | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        if self.create:
            flags |= os.O_CREAT
        try:
            self.fd = os.open(self.path, flags, 0o600)
        except FileNotFoundError as error:
            raise InstallError(f"deployment lock is missing: {self.path}") from error
        except OSError as error:
            raise InstallError(f"cannot open deployment lock {self.path}: {error}") from error

        try:
            value = os.fstat(self.fd)
            require(stat.S_ISREG(value.st_mode), f"deployment lock is not a regular file: {self.path}")
            require(value.st_nlink == 1, f"deployment lock has multiple hard links: {self.path}")
            os.fchmod(self.fd, 0o600)
            try:
                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise InstallError(f"another Heading deployment is active: {self.path}") from error
        except Exception:
            os.close(self.fd)
            self.fd = None
            raise
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if self.fd is not None:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_UN)
            finally:
                os.close(self.fd)
                self.fd = None


class DeploymentLocks(AbstractContextManager["DeploymentLocks"]):
    """Hold both target-root locks in a stable order."""

    def __init__(self, roots: dict[str, Path], *, create: bool) -> None:
        self.paths = sorted({root / LOCK_NAME for root in roots.values()}, key=os.fspath)
        self.create = create
        self.stack: ExitStack | None = None

    def __enter__(self) -> "DeploymentLocks":
        stack = ExitStack()
        try:
            for path in self.paths:
                stack.enter_context(DeploymentLock(path, create=self.create))
        except Exception:
            stack.close()
            raise
        self.stack = stack
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if self.stack is not None:
            self.stack.close()
            self.stack = None


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InstallError(message)


def path_kind(path: Path) -> str:
    try:
        value = path.lstat()
    except FileNotFoundError:
        return "missing"
    if stat.S_ISLNK(value.st_mode):
        return "symlink"
    if stat.S_ISDIR(value.st_mode):
        return "directory"
    if stat.S_ISREG(value.st_mode):
        return "file"
    return "special"


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_root(path: Path) -> Path:
    expanded = os.path.expanduser(os.fspath(path))
    absolute = os.path.abspath(expanded)
    if sys.platform != "darwin":
        return Path(absolute)

    # macOS exposes a small, OS-owned set of aliases such as /var -> /private/var.
    # Canonicalize only these exact aliases after proving the installed alias still
    # names the expected physical directory. All user-controlled ancestors remain
    # subject to assert_safe_root's no-symlink rule.
    for alias, physical in MACOS_SYSTEM_ALIASES.items():
        if absolute != alias and not absolute.startswith(alias + os.sep):
            continue
        try:
            trusted_alias = os.path.islink(alias) and os.path.samefile(alias, physical)
        except OSError:
            trusted_alias = False
        if trusted_alias:
            return Path(physical + absolute[len(alias):])
        break
    return Path(absolute)


def assert_safe_root(root: Path, label: str) -> None:
    require(root.is_absolute(), f"{label} root is not absolute: {root}")
    require(root != Path(root.anchor), f"refusing filesystem root as {label} root")

    parts = root.parts
    current = Path(parts[0])
    missing_seen = False
    for part in parts[1:]:
        current /= part
        kind = path_kind(current)
        if kind == "missing":
            missing_seen = True
            continue
        require(not missing_seen, f"{label} path appeared below a missing ancestor: {current}")
        require(kind == "directory", f"{label} path component is {kind}: {current}")


def assert_disjoint_roots(codex: Path, skills: Path) -> None:
    require(codex != skills, "codex and skills roots must differ")
    require(codex not in skills.parents, f"skills root must not be inside codex root: {skills}")
    require(skills not in codex.parents, f"codex root must not be inside skills root: {codex}")


def ensure_directory_chain(path: Path, created_dirs: list[Path]) -> None:
    assert_safe_root(path, "target")
    current = Path(path.parts[0])
    for part in path.parts[1:]:
        current /= part
        kind = path_kind(current)
        if kind == "missing":
            try:
                current.mkdir(mode=0o755)
            except FileExistsError:
                pass
            else:
                created_dirs.append(current)
            kind = path_kind(current)
        require(kind == "directory", f"unsafe directory component: {current} ({kind})")
    assert_safe_root(path, "target")


def fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0)
    try:
        fd = os.open(path, flags)
    except OSError:
        return
    try:
        try:
            os.fsync(fd)
        except OSError:
            pass
    finally:
        os.close(fd)


def source_item(root: str, source: Path, relative: Path) -> Item:
    require(not relative.is_absolute(), f"absolute install path: {relative}")
    require(all(part not in {"", ".", ".."} for part in relative.parts), f"unsafe install path: {relative}")
    require(path_kind(source) == "file", f"unsafe source file: {source}")
    value = source.lstat()
    require(value.st_nlink == 1, f"source file has multiple hard links: {source}")
    mode = 0o755 if value.st_mode & 0o111 else 0o644
    return Item(root, source, relative, mode, digest_file(source))


def source_files(directory: Path) -> Iterable[Path]:
    require(path_kind(directory) == "directory", f"missing source directory: {directory}")
    for path in sorted(directory.rglob("*")):
        require(not path.is_symlink(), f"source symlink is not allowed: {path}")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
            yield path


def inventory(*, include_legacy_skills: bool) -> list[Item]:
    items = [source_item("codex", RUNTIME_ROOT / "profile/heading.config.toml", Path("heading.config.toml"))]
    agent_files = sorted((RUNTIME_ROOT / "agents").glob("heading-*.toml"))
    require(len(agent_files) == 4, "expected four agent files")
    for source in agent_files:
        items.append(source_item("codex", source, Path("agents") / source.name))

    if include_legacy_skills:
        for skill in SKILLS:
            base = PLUGIN_ROOT / "skills" / skill
            for source in source_files(base):
                items.append(source_item("skills", source, Path(skill) / source.relative_to(base)))

    keys = [(item.root, item.relative.as_posix()) for item in items]
    require(len(keys) == len(set(keys)), "duplicate install destination")
    return sorted(items, key=lambda item: (item.root, item.relative.as_posix()))


def assert_directory_or_missing(path: Path, label: str) -> None:
    kind = path_kind(path)
    require(kind in {"missing", "directory"}, f"{label} is {kind}: {path}")


def heading_namespace_entries(roots: dict[str, Path]) -> list[Path]:
    """Return only filesystem entries that can be Heading-managed paths.

    Unrelated notes in the Codex home (for example, a report whose filename
    starts with ``heading-``) are not part of the Heading namespace and must
    not block a non-destructive deployment.
    """
    values: set[Path] = set()
    codex = roots["codex"]
    skills = roots.get("skills")

    assert_directory_or_missing(codex, "codex root")
    if path_kind(codex) == "directory":
        values.update(entry for entry in codex.iterdir() if entry.name.casefold() == f"{PRODUCT}.config.toml")

    agents = codex / "agents"
    assert_directory_or_missing(agents, "agents namespace")
    if path_kind(agents) == "directory":
        values.update(
            entry
            for entry in agents.iterdir()
            if entry.name.casefold().startswith(f"{PRODUCT}-") and entry.suffix.casefold() == ".toml"
        )

    if skills is not None:
        assert_directory_or_missing(skills, "skills root")
    if skills is not None and path_kind(skills) == "directory":
        values.update(
            entry
            for entry in skills.iterdir()
            if entry.name.casefold().startswith(f"{PRODUCT}-") and path_kind(entry) in {"directory", "symlink"}
        )

    historical = codex / "skills"
    assert_directory_or_missing(historical, "historical skills root")
    if path_kind(historical) == "directory":
        values.update(
            entry
            for entry in historical.iterdir()
            if entry.name.casefold().startswith(f"{PRODUCT}-") and path_kind(entry) in {"directory", "symlink"}
        )

    return sorted(values, key=os.fspath)


def expected_namespace_paths(roots: dict[str, Path], items: list[Item]) -> set[Path]:
    return {roots[item.root].joinpath(*item.relative.parts) for item in items if len(item.relative.parts) == 1 or item.relative.parts[0] == "agents"}


def expected_skill_roots(roots: dict[str, Path]) -> set[Path]:
    skills = roots.get("skills")
    return set() if skills is None else {skills / skill for skill in SKILLS}


def validate_heading_namespace(roots: dict[str, Path], items: list[Item]) -> None:
    allowed = expected_namespace_paths(roots, items) | expected_skill_roots(roots)
    unexpected = sorted(
        (path for path in heading_namespace_entries(roots) if path not in allowed),
        key=os.fspath,
    )
    if unexpected:
        raise InstallError(f"unexpected Heading namespace remains: {unexpected[0]}; remove it before installing")


def classify(root: Path, item: Item) -> str:
    current = root
    for part in item.relative.parts[:-1]:
        current /= part
        kind = path_kind(current)
        if kind == "missing":
            return "missing"
        if kind != "directory":
            return f"unsafe-ancestor-{kind}"

    destination = root.joinpath(*item.relative.parts)
    kind = path_kind(destination)
    if kind == "missing":
        return "missing"
    if kind != "file":
        return f"unsafe-destination-{kind}"
    value = destination.lstat()
    if value.st_nlink != 1:
        return "unsafe-destination-hardlink"
    if digest_file(destination) != item.digest:
        return "conflict"
    mode = stat.S_IMODE(value.st_mode)
    return "current" if mode == item.mode else "mode-drift"


def walk_no_follow(base: Path) -> Iterable[tuple[Path, str]]:
    for entry in sorted(base.iterdir(), key=lambda path: path.name):
        kind = path_kind(entry)
        yield entry, kind
        if kind == "directory":
            yield from walk_no_follow(entry)


def validate_skill_namespaces(skills_root: Path, items: list[Item]) -> None:
    allowed_files: dict[str, set[Path]] = {skill: set() for skill in SKILLS}
    for item in items:
        if item.root != "skills":
            continue
        skill, *rest = item.relative.parts
        allowed_files[skill].add(Path(*rest))

    for skill, files in allowed_files.items():
        base = skills_root / skill
        kind = path_kind(base)
        if kind == "missing":
            continue
        require(kind == "directory", f"managed skill path is {kind}: {base}")
        allowed_dirs = {Path(".")}
        for relative in files:
            parent = relative.parent
            while parent != Path("."):
                allowed_dirs.add(parent)
                parent = parent.parent
        for entry, entry_kind in walk_no_follow(base):
            relative = entry.relative_to(base)
            require(entry_kind != "symlink", f"symlink in managed skill namespace: {entry}")
            if entry_kind == "directory":
                require(relative in allowed_dirs, f"unexpected directory in managed skill namespace: {entry}")
            elif entry_kind == "file":
                require(relative in files, f"unexpected file in managed skill namespace: {entry}")
                require(entry.lstat().st_nlink == 1, f"hard link in managed skill namespace: {entry}")
            else:
                raise InstallError(f"special file in managed skill namespace: {entry}")


def preflight(
    roots: dict[str, Path],
    items: list[Item],
    *,
    check: bool,
) -> list[tuple[Item, str]]:
    for label, root in roots.items():
        assert_safe_root(root, label)
        kind = path_kind(root)
        require(kind in {"missing", "directory"}, f"{label} root is {kind}: {root}")

    validate_heading_namespace(roots, items)
    if "skills" in roots:
        validate_skill_namespaces(roots["skills"], items)
    allowed = {"current"} if check else {"missing", "current", "mode-drift"}
    plan: list[tuple[Item, str]] = []
    destinations: set[Path] = set()
    for item in items:
        destination = roots[item.root].joinpath(*item.relative.parts)
        require(destination not in destinations, f"duplicate absolute destination: {destination}")
        destinations.add(destination)
        state = classify(roots[item.root], item)
        require(state in allowed, f"destination {destination} is {state}")
        plan.append((item, state))
    return plan


def ensure_parent(root: Path, relative: Path, created_dirs: list[Path]) -> Path:
    current = root
    for part in relative.parts[:-1]:
        current /= part
        kind = path_kind(current)
        if kind == "missing":
            try:
                current.mkdir(mode=0o755)
            except FileExistsError:
                pass
            else:
                created_dirs.append(current)
            kind = path_kind(current)
        require(kind == "directory", f"unsafe install ancestor: {current} ({kind})")
    return current


def install_missing(root: Path, item: Item, actions: list[Action], created_dirs: list[Path]) -> None:
    parent = ensure_parent(root, item.relative, created_dirs)
    destination = root.joinpath(*item.relative.parts)
    fd, temporary_name = tempfile.mkstemp(prefix=".heading-install-", dir=parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "wb") as target, item.source.open("rb") as source:
            shutil.copyfileobj(source, target)
            target.flush()
            os.fsync(target.fileno())
        os.chmod(temporary, item.mode, follow_symlinks=False)
        require(path_kind(destination) == "missing", f"destination appeared during install: {destination}")
        try:
            os.link(temporary, destination, follow_symlinks=False)
        except FileExistsError as error:
            raise InstallError(f"destination appeared during install: {destination}") from error
        except OSError as error:
            raise InstallError(f"cannot commit {destination}: {error}") from error
        actions.append(Action("created", destination, digest=item.digest))
        fsync_directory(parent)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def repair_mode(root: Path, item: Item, actions: list[Action]) -> None:
    destination = root.joinpath(*item.relative.parts)
    require(path_kind(destination) == "file", f"mode target changed: {destination}")
    require(destination.lstat().st_nlink == 1, f"mode target has multiple hard links: {destination}")
    require(digest_file(destination) == item.digest, f"mode target content changed: {destination}")
    old_mode = stat.S_IMODE(destination.lstat().st_mode)
    actions.append(Action("mode", destination, digest=item.digest, previous_mode=old_mode))
    os.chmod(destination, item.mode, follow_symlinks=False)


def rollback_actions(actions: list[Action], created_dirs: list[Path]) -> list[str]:
    errors: list[str] = []
    for action in reversed(actions):
        try:
            if action.kind == "created":
                if path_kind(action.path) == "file" and action.digest is not None and digest_file(action.path) == action.digest:
                    action.path.unlink()
                    fsync_directory(action.path.parent)
            elif action.kind == "mode" and action.previous_mode is not None:
                if path_kind(action.path) == "file" and action.digest is not None and digest_file(action.path) == action.digest:
                    os.chmod(action.path, action.previous_mode, follow_symlinks=False)
        except OSError as error:
            errors.append(f"{action.path}: {error}")
    for directory in reversed(created_dirs):
        try:
            directory.rmdir()
        except FileNotFoundError:
            pass
        except OSError:
            continue
    return errors


def plan_payload(roots: dict[str, Path], items: list[Item]) -> dict[str, object]:
    validate_heading_namespace(roots, items)
    return {
        "status": "PASS",
        "mode": "plan",
        "remove": [],
        "install": [os.fspath(roots[item.root].joinpath(*item.relative.parts)) for item in items],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="print the non-destructive install plan without changing files")
    parser.add_argument("--check", action="store_true", help="verify the current Heading installation")
    parser.add_argument("--codex-home", type=Path, default=Path(os.environ.get("CODEX_HOME", "~/.codex")))
    parser.add_argument("--skills-root", type=Path, default=Path("~/.agents/skills"), help="legacy skill destination; used only with --install-legacy-skills")
    parser.add_argument("--install-legacy-skills", action="store_true", help="also copy skill folders to --skills-root; this can shadow the plugin and is not the default")
    args = parser.parse_args()
    require(not (args.check and args.dry_run), "--check and --dry-run are mutually exclusive")
    return args


def main() -> int:
    actions: list[Action] = []
    created_dirs: list[Path] = []
    committed = False
    try:
        args = parse_args()
        roots = {"codex": normalize_root(args.codex_home)}
        if args.install_legacy_skills:
            roots["skills"] = normalize_root(args.skills_root)
            assert_disjoint_roots(roots["codex"], roots["skills"])
        for label, root in roots.items():
            assert_safe_root(root, label)

        items = inventory(include_legacy_skills=args.install_legacy_skills)
        if args.dry_run:
            print(json.dumps(plan_payload(roots, items), ensure_ascii=False, sort_keys=True))
            return 0

        if args.check:
            for label, root in roots.items():
                require(path_kind(root) == "directory", f"{label} root is not installed: {root}")
            with DeploymentLocks(roots, create=False):
                plan = preflight(roots, items, check=True)
            print(json.dumps({"status": "PASS", "mode": "check", "files": len(plan), "namespaceClean": True}, sort_keys=True))
            return 0

        for root in roots.values():
            ensure_directory_chain(root, created_dirs)
        with DeploymentLocks(roots, create=True):
            for label, root in roots.items():
                assert_safe_root(root, label)
            plan = preflight(roots, items, check=False)
            for item, state in plan:
                if state == "missing":
                    install_missing(roots[item.root], item, actions, created_dirs)
                elif state == "mode-drift":
                    repair_mode(roots[item.root], item, actions)
            preflight(roots, items, check=True)
            committed = True
            preflight(roots, items, check=True)

        print(
            json.dumps(
                {
                    "status": "PASS",
                    "mode": "install",
                    "files": len(plan),
                    "namespaceClean": True,
                },
                sort_keys=True,
            )
        )
        return 0
    except (InstallError, OSError) as error:
        rollback_errors: list[str] = []
        if not committed:
            rollback_errors.extend(rollback_actions(actions, created_dirs))
        detail = f"; rollback errors: {' | '.join(rollback_errors)}" if rollback_errors else ""
        print(f"install: {error}{detail}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
