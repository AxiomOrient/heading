from __future__ import annotations

import fcntl
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = ROOT / "plugins" / "heading"
INSTALLER = ROOT / "scripts" / "install.py"
VALIDATOR = ROOT / "scripts" / "validate.py"
PLUGIN_VALIDATOR = ROOT / "scripts" / "validate-plugin.py"
PLUGIN_SMOKE = ROOT / "scripts" / "smoke-plugin-install.py"
TRACKS = ("prototype", "build", "sweep", "grow", "maintain")


class HeadingTests(unittest.TestCase):
    maxDiff = None

    def run_python(
        self,
        script: Path,
        *args: str,
        env: dict[str, str] | None = None,
        cwd: Path = ROOT,
        preexec_fn=None,
    ) -> subprocess.CompletedProcess[str]:
        runtime_env = os.environ.copy()
        runtime_env["PYTHONDONTWRITEBYTECODE"] = "1"
        if env:
            runtime_env.update(env)
        return subprocess.run(
            [sys.executable, "-B", str(script), *args],
            cwd=cwd,
            env=runtime_env,
            capture_output=True,
            text=True,
            check=False,
            preexec_fn=preexec_fn,
        )

    def install(
        self,
        codex: Path,
        *extra: str,
        env: dict[str, str] | None = None,
        preexec_fn=None,
    ) -> subprocess.CompletedProcess[str]:
        return self.run_python(
            INSTALLER,
            *extra,
            "--codex-home",
            str(codex),
            env=env,
            preexec_fn=preexec_fn,
        )

    def copy_source(self, destination: Path) -> Path:
        source = destination / "source"
        shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(".git", "__pycache__", "eval-results"))
        return source

    def run_fault_injected(self, codex: Path, patch: str) -> subprocess.CompletedProcess[str]:
        code = "\n".join(
            (
                "import importlib.util",
                "import pathlib",
                "import sys",
                f"installer = pathlib.Path({str(INSTALLER)!r})",
                'spec = importlib.util.spec_from_file_location("heading_install_fault", installer)',
                "module = importlib.util.module_from_spec(spec)",
                "sys.modules[spec.name] = module",
                "spec.loader.exec_module(module)",
                textwrap.dedent(patch).strip(),
                f'sys.argv = [str(installer), "--codex-home", {str(codex)!r}]',
                "raise SystemExit(module.main())",
            )
        )
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, "-B", "-c", code],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def assert_no_active_profile(self, codex: Path) -> None:
        self.assertFalse((codex / "heading.config.toml").exists())
        agents = codex / "agents"
        self.assertEqual(list(agents.glob("heading-*")) if agents.is_dir() else [], [])

    # Source and packaging contracts

    def test_bundle_validation(self) -> None:
        result = self.run_python(VALIDATOR)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["version"], "0.5.0")
        self.assertEqual(payload["tracks"], 5)
        self.assertEqual(payload["skills"], 6)
        self.assertEqual(payload["childRoles"], 4)
        self.assertEqual(payload["modelRoutingEvals"], 17)
        self.assertEqual(payload["routeBenchmarks"], 4)

    def test_bundle_validation_with_python_optimize(self) -> None:
        result = self.run_python(VALIDATOR, env={"PYTHONOPTIMIZE": "1"})
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_each_track_skill_mutation_is_rejected(self) -> None:
        spec = importlib.util.spec_from_file_location("heading_validate_skill_mutation", VALIDATOR)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        validator = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = validator
        spec.loader.exec_module(validator)
        with tempfile.TemporaryDirectory() as temporary:
            for track in TRACKS:
                source = self.copy_source(Path(temporary) / track)
                skill = source / "plugins" / "heading" / "skills" / f"heading-{track}" / "SKILL.md"
                skill.write_text(skill.read_text(encoding="utf-8") + "\nmutated contract\n", encoding="utf-8")
                validator.ROOT = source
                validator.PLUGIN_ROOT = source / "plugins" / "heading"
                validator.SKILLS_ROOT = validator.PLUGIN_ROOT / "skills"
                validator.RUNTIME_ROOT = source / "runtime" / "heading"
                with self.subTest(track=track), self.assertRaisesRegex(validator.ValidationError, "skill content mismatch"):
                    validator.validate_skills()

    def test_each_track_method_mutation_is_rejected(self) -> None:
        spec = importlib.util.spec_from_file_location("heading_validate_method_mutation", VALIDATOR)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        validator = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = validator
        spec.loader.exec_module(validator)
        with tempfile.TemporaryDirectory() as temporary:
            for track in TRACKS:
                source = self.copy_source(Path(temporary) / track)
                method = source / "plugins" / "heading" / "skills" / f"heading-{track}" / "references" / "METHOD.md"
                method.write_text(method.read_text(encoding="utf-8") + "\nmutated method\n", encoding="utf-8")
                validator.ROOT = source
                validator.PLUGIN_ROOT = source / "plugins" / "heading"
                validator.SKILLS_ROOT = validator.PLUGIN_ROOT / "skills"
                validator.RUNTIME_ROOT = source / "runtime" / "heading"
                with self.subTest(track=track), self.assertRaisesRegex(validator.ValidationError, "method content mismatch"):
                    validator.validate_skills()

    def test_source_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = self.copy_source(Path(temporary))
            target = source / "DESIGN.md"
            target.unlink()
            target.symlink_to("README.md")
            result = self.run_python(source / "scripts" / "validate.py", cwd=source)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source symlink", result.stderr)

    def test_plugin_package_rejects_portable_manifest_drift(self) -> None:
        result = self.run_python(PLUGIN_VALIDATOR)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["skills"], 6)
        with tempfile.TemporaryDirectory() as temporary:
            source = self.copy_source(Path(temporary))
            manifest = source / "plugins" / "heading" / "plugin.json"
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["skills"] = "./skills/"
            manifest.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            result = self.run_python(source / "scripts" / "validate-plugin.py", cwd=source)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unsupported keys", result.stderr)

    def test_plugin_smoke_accepts_base_or_cachebusted_codex_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fake = Path(temporary) / "codex"
            fake.write_text(
                "#!/usr/bin/env python3\n"
                "import json, os, pathlib, shutil, sys\n"
                "args = sys.argv[1:]\n"
                "root = pathlib.Path(os.environ['HEADING_TEST_PLUGIN_ROOT'])\n"
                "version = (root / 'VERSION').read_text(encoding='utf-8').strip()\n"
                "plugin = root / 'plugins/heading'\n"
                "entry = {'pluginId': 'heading@heading', 'name': 'heading', 'marketplaceName': 'heading', 'version': version, 'source': {'source': 'local', 'path': str(plugin)}}\n"
                "if args[:3] == ['plugin', 'marketplace', 'add']:\n"
                "    print('marketplace added')\n"
                "elif args[:2] == ['plugin', 'list'] and '--available' in args:\n"
                "    entry.update({'installed': False, 'enabled': False})\n"
                "    print(json.dumps({'installed': [], 'available': [entry]}))\n"
                "elif args[:2] == ['plugin', 'add']:\n"
                "    cache = pathlib.Path(os.environ['CODEX_HOME']) / 'plugins/cache/heading/heading' / version\n"
                "    cache.parent.mkdir(parents=True, exist_ok=True)\n"
                "    shutil.copytree(plugin, cache)\n"
                "    print(json.dumps({'pluginId': 'heading@heading'}))\n"
                "elif args[:2] == ['plugin', 'list']:\n"
                "    entry.update({'installed': True, 'enabled': True})\n"
                "    print(json.dumps({'installed': [entry], 'available': []}))\n"
                "else:\n"
                "    raise SystemExit(91)\n",
                encoding="utf-8",
            )
            fake.chmod(0o755)
            smoke = self.run_python(PLUGIN_SMOKE, "--codex-bin", str(fake), env={"HEADING_TEST_PLUGIN_ROOT": str(ROOT)})
            self.assertEqual(smoke.returncode, 0, smoke.stderr)
            self.assertEqual(json.loads(smoke.stdout)["cacheManifests"], "MATCH")

    # Optional profile installation: one root, five files, no copied skills

    def test_profile_install_is_idempotent_and_does_not_copy_global_skills(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            codex = Path(temporary) / "codex"
            plan = self.install(codex, "--dry-run")
            self.assertEqual(plan.returncode, 0, plan.stderr)
            payload = json.loads(plan.stdout)
            self.assertEqual((payload["mode"], len(payload["install"]), payload["remove"]), ("plan", 5, []))
            self.assertFalse(codex.exists())
            first = self.install(codex)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(json.loads(first.stdout)["files"], 5)
            self.assertFalse((codex / "skills").exists())
            self.assertEqual(self.install(codex).returncode, 0)
            self.assertEqual(self.install(codex, "--check").returncode, 0)

    def test_unknown_profile_option_is_rejected_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            codex = Path(temporary) / "codex"
            result = self.install(codex, "--retired-option")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unrecognized arguments", result.stderr)
            self.assert_no_active_profile(codex)

    def test_shadowing_global_heading_namespace_is_rejected_non_destructively(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            codex = Path(temporary) / "codex"
            foreign = codex / "skills" / "heading-build" / "foreign.txt"
            foreign.parent.mkdir(parents=True)
            foreign.write_text("keep\n", encoding="utf-8")
            result = self.install(codex)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unexpected Heading namespace remains", result.stderr)
            self.assertEqual(foreign.read_text(encoding="utf-8"), "keep\n")

    def test_unrelated_heading_note_does_not_block_install(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            codex = Path(temporary) / "codex"
            codex.mkdir()
            note = codex / "heading-runtime-audit.md"
            note.write_text("keep\n", encoding="utf-8")
            result = self.install(codex)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(note.read_text(encoding="utf-8"), "keep\n")

    def test_mode_and_content_drift_are_handled_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            codex = Path(temporary) / "codex"
            self.assertEqual(self.install(codex).returncode, 0)
            profile = codex / "heading.config.toml"
            profile.chmod(0o600)
            self.assertNotEqual(self.install(codex, "--check").returncode, 0)
            self.assertEqual(self.install(codex).returncode, 0)
            self.assertEqual(stat.S_IMODE(profile.stat().st_mode), 0o644)
            agent = codex / "agents" / "heading-executor.toml"
            agent.write_text("changed\n", encoding="utf-8")
            conflict = self.install(codex)
            self.assertNotEqual(conflict.returncode, 0)
            self.assertEqual(agent.read_text(encoding="utf-8"), "changed\n")

    # Filesystem safety and rollback

    def test_root_and_internal_symlinks_are_rejected_without_external_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            external = base / "external"
            external.mkdir()
            alias = base / "alias"
            alias.symlink_to(external, target_is_directory=True)
            root_result = self.install(alias / "codex")
            self.assertNotEqual(root_result.returncode, 0)
            self.assertIn("symlink", root_result.stderr)
            self.assertEqual(list(external.iterdir()), [])

            codex = base / "codex"
            codex.mkdir()
            (codex / "agents").symlink_to(external, target_is_directory=True)
            internal_result = self.install(codex)
            self.assertNotEqual(internal_result.returncode, 0)
            self.assertEqual(list(external.iterdir()), [])

    def test_destination_symlink_and_hardlink_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            for kind in ("symlink", "hardlink"):
                with self.subTest(kind=kind):
                    case = base / kind
                    codex = case / "codex"
                    codex.mkdir(parents=True)
                    outside = case / "outside.toml"
                    outside.write_text("outside\n", encoding="utf-8")
                    destination = codex / "heading.config.toml"
                    if kind == "symlink":
                        destination.symlink_to(outside)
                    else:
                        os.link(outside, destination)
                    result = self.install(codex)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(outside.read_text(encoding="utf-8"), "outside\n")

    def test_stale_lock_mode_converges_and_active_lock_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            codex = Path(temporary) / "codex"
            codex.mkdir()
            lock = codex / ".heading-deploy.lock"
            lock.write_text("stale\n", encoding="utf-8")
            lock.chmod(0o777)
            installed = self.install(codex)
            self.assertEqual(installed.returncode, 0, installed.stderr)
            self.assertEqual(stat.S_IMODE(lock.stat().st_mode), 0o600)
            descriptor = os.open(lock, os.O_RDWR)
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                blocked = self.install(codex)
                self.assertNotEqual(blocked.returncode, 0)
                self.assertIn("another Heading deployment is active", blocked.stderr)
            finally:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
                os.close(descriptor)

    def test_mid_install_failure_rolls_back_new_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            codex = Path(temporary) / "codex"
            patch = """
real_link = module.os.link
state = {"calls": 0, "failed": False}
def injected_link(*args, **kwargs):
    state["calls"] += 1
    if state["calls"] == 3 and not state["failed"]:
        state["failed"] = True
        raise OSError("injected link failure")
    return real_link(*args, **kwargs)
module.os.link = injected_link
"""
            result = self.run_fault_injected(codex, patch)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("injected link failure", result.stderr)
            self.assert_no_active_profile(codex)

    def test_unicode_deep_root_and_restrictive_umask(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary) / "공백 dir\nline"
            codex = base.joinpath(*[f"d{index}" for index in range(48)]) / "코덱스"
            result = self.install(codex, preexec_fn=lambda: os.umask(0o077))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(stat.S_IMODE((codex / "heading.config.toml").stat().st_mode), 0o644)
            self.assertEqual(self.install(codex, "--check").returncode, 0)

    def test_installed_validator_uses_only_codex_home(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            codex = Path(temporary) / "codex"
            self.assertEqual(self.install(codex).returncode, 0)
            result = self.run_python(VALIDATOR, "--installed", "--codex-home", str(codex))
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
