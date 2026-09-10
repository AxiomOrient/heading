#!/usr/bin/env python3
"""Validate Heading's portable and Codex plugin packaging without dependencies."""

from __future__ import annotations

import json
from pathlib import Path
import re
import stat
import sys
import unicodedata


ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = ROOT / "plugins" / "heading"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
PORTABLE_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
PORTABLE_KEYS = {
    "$schema", "name", "version", "description", "author", "homepage",
    "repository", "license", "keywords", "extensions",
}


class ValidationError(RuntimeError):
    """A plugin packaging invariant failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def load_json(path: Path) -> dict[str, object]:
    require(path.is_file() and not path.is_symlink(), f"missing or unsafe JSON file: {path.relative_to(ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(payload, dict), f"JSON root must be an object: {path.relative_to(ROOT)}")
    return payload


def relative_inside_plugin(value: object, label: str, *, directory: bool = False) -> Path:
    require(isinstance(value, str) and value.startswith("./"), f"{label} must start with ./: {value!r}")
    candidate = Path(value)
    require(not candidate.is_absolute() and all(part not in {"", ".", ".."} for part in candidate.parts[1:]), f"unsafe {label}: {value!r}")
    resolved = (PLUGIN_ROOT / candidate).resolve(strict=False)
    root = PLUGIN_ROOT.resolve()
    require(resolved == root or root in resolved.parents, f"{label} escapes plugin root: {value!r}")
    if directory:
        require(resolved.is_dir(), f"{label} directory missing: {value!r}")
    else:
        require(resolved.is_file(), f"{label} file missing: {value!r}")
    return resolved


def validate_tree() -> None:
    allowed_top_level = {".codex-plugin", "plugin.json", "skills"}
    actual_top_level = {path.name for path in PLUGIN_ROOT.iterdir()}
    require(actual_top_level == allowed_top_level, f"plugin root entries mismatch: {sorted(actual_top_level)}")
    for path in PLUGIN_ROOT.rglob("*"):
        relative = path.relative_to(PLUGIN_ROOT)
        value = path.lstat()
        require(not stat.S_ISLNK(value.st_mode), f"plugin symlink is not allowed: {relative}")
        require(stat.S_ISDIR(value.st_mode) or stat.S_ISREG(value.st_mode), f"plugin special file is not allowed: {relative}")


def validate_portable() -> None:
    payload = load_json(PLUGIN_ROOT / "plugin.json")
    require(set(payload).issubset(PORTABLE_KEYS), f"portable manifest has unsupported keys: {sorted(set(payload) - PORTABLE_KEYS)}")
    require(payload.get("$schema") == PORTABLE_SCHEMA, "portable schema URL mismatch")
    require(payload.get("name") == "heading", "portable plugin name mismatch")
    require(payload.get("version") == VERSION, "portable plugin version mismatch")
    require(isinstance(payload.get("description"), str) and payload["description"], "portable description missing")
    require(re.fullmatch(r"[a-z][a-z0-9-]{0,63}", str(payload["name"])) is not None, "portable name format mismatch")
    require(re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", str(payload["version"])) is not None, "portable version format mismatch")
    author = payload.get("author")
    require(isinstance(author, dict) and author.get("name") == "AxiomOrient", "portable author mismatch")


def validate_codex() -> None:
    payload = load_json(PLUGIN_ROOT / ".codex-plugin" / "plugin.json")
    version = payload.get("version")
    cachebusted = isinstance(version, str) and re.fullmatch(re.escape(VERSION) + r"\+codex\.[a-z0-9-]+", version) is not None
    require(payload.get("name") == "heading" and (version == VERSION or cachebusted), "Codex manifest identity mismatch")
    skills = relative_inside_plugin(payload.get("skills"), "Codex skills", directory=True)
    interface = payload.get("interface")
    require(isinstance(interface, dict), "Codex interface missing")
    for key in ("displayName", "shortDescription", "longDescription", "developerName", "category", "defaultPrompt"):
        require(isinstance(interface.get(key), str) and interface[key], f"Codex interface field missing: {key}")
    require(interface.get("capabilities") == [], "skills-only plugin must not claim capabilities")
    prompts = interface["defaultPrompt"]
    prompt_items = [prompts] if isinstance(prompts, str) else prompts
    require(isinstance(prompt_items, list) and 1 <= len(prompt_items) <= 3, "Codex default prompts must contain one to three entries")
    normalized: set[str] = set()
    for prompt in prompt_items:
        require(isinstance(prompt, str) and prompt.strip(), "Codex default prompt must be non-empty text")
        require("\n" not in prompt and "\r" not in prompt, "Codex default prompt must be one line")
        require(len(prompt) <= 128, "Codex default prompt exceeds 128 characters")
        require("$heading-" not in prompt, "plugin default prompt must not require explicit skill invocation")
        key = " ".join(unicodedata.normalize("NFC", prompt).split())
        require(key not in normalized, "Codex default prompts must be unique after normalization")
        normalized.add(key)
    skill_dirs = sorted(path for path in skills.iterdir() if path.is_dir())
    require(len(skill_dirs) == 6, f"expected six bundled skills, found {len(skill_dirs)}")
    for skill in skill_dirs:
        require((skill / "SKILL.md").is_file(), f"skill entry missing SKILL.md: {skill.name}")


def validate_invocation_policy() -> None:
    implicit_tracks = ("prototype", "build", "sweep", "grow", "maintain")
    for track in implicit_tracks:
        metadata = (PLUGIN_ROOT / "skills" / f"heading-{track}" / "agents" / "openai.yaml").read_text(encoding="utf-8")
        require("allow_implicit_invocation: true" in metadata, f"core skill must allow implicit invocation: heading-{track}")
    metadata = (PLUGIN_ROOT / "skills" / "heading-orchestrate" / "agents" / "openai.yaml").read_text(encoding="utf-8")
    require("allow_implicit_invocation: false" in metadata, "orchestration skill must remain explicit-only")


def validate_marketplace() -> None:
    payload = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
    require(payload.get("name") == "heading", "marketplace name mismatch")
    interface = payload.get("interface")
    require(isinstance(interface, dict) and interface.get("displayName") == "Heading Plugins", "marketplace display name mismatch")
    plugins = payload.get("plugins")
    require(isinstance(plugins, list) and len(plugins) == 1, "marketplace must expose one Heading plugin")
    item = plugins[0]
    require(isinstance(item, dict) and item.get("name") == "heading", "marketplace plugin identity mismatch")
    source = item.get("source")
    require(isinstance(source, dict) and source == {"source": "local", "path": "./plugins/heading"}, "marketplace source mismatch")
    resolved = (ROOT / source["path"]).resolve(strict=False)
    require(resolved == PLUGIN_ROOT.resolve(), "marketplace source does not resolve to plugin root")
    policy = item.get("policy")
    require(policy == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "marketplace policy mismatch")


def main() -> int:
    try:
        validate_tree(); validate_portable(); validate_codex(); validate_invocation_policy(); validate_marketplace()
    except (OSError, json.JSONDecodeError, ValidationError) as error:
        print(f"validate-plugin: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "PASS", "plugin": "heading", "version": VERSION, "skills": 6, "portable": True, "codex": True}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
