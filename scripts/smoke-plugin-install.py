#!/usr/bin/env python3
"""Install Heading in an isolated Codex home and verify its enabled cache contract."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = ROOT / "plugins" / "heading"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
PLUGIN_ID = "heading@heading"


class SmokeError(RuntimeError):
    """An installed plugin did not match the expected local package."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeError(message)


def bounded_output(completed: subprocess.CompletedProcess[str]) -> str:
    text = (completed.stdout + completed.stderr).strip()
    return text[:1600] if text else "no command output"


def run(command: list[str], env: dict[str, str]) -> str:
    completed = subprocess.run(command, env=env, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise SmokeError(f"command failed ({completed.returncode}): {' '.join(command[:4])}: {bounded_output(completed)}")
    return completed.stdout


def load_plugin_list(text: str, section: str) -> dict[str, Any]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as error:
        raise SmokeError(f"invalid plugin list JSON: {error}") from error
    require(isinstance(payload, dict), "plugin list JSON root must be an object")
    items = payload.get(section)
    require(isinstance(items, list), f"plugin list missing {section}")
    matches = [item for item in items if isinstance(item, dict) and item.get("pluginId") == PLUGIN_ID]
    require(len(matches) == 1, f"expected exactly one {section} {PLUGIN_ID} entry")
    return matches[0]


def validate_entry(entry: dict[str, Any], *, installed: bool) -> None:
    require(entry.get("name") == "heading", "installed plugin name mismatch")
    require(entry.get("marketplaceName") == "heading", "installed plugin marketplace mismatch")
    require(entry.get("version") == VERSION, "installed plugin version mismatch")
    require(entry.get("installed") is installed, "installed state mismatch")
    require(entry.get("enabled") is installed, "enabled state mismatch")
    source = entry.get("source")
    require(isinstance(source, dict) and source.get("source") == "local", "plugin source must be local")
    require(Path(str(source.get("path", ""))).resolve() == PLUGIN_ROOT.resolve(), "plugin source path mismatch")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-bin", default="codex", help="Codex CLI executable (default: codex)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    codex = shutil.which(args.codex_bin)
    if codex is None:
        print(f"smoke-plugin-install: Codex CLI not found: {args.codex_bin}", file=sys.stderr)
        return 2
    try:
        with tempfile.TemporaryDirectory(prefix="heading-plugin-smoke-") as temporary:
            home = Path(temporary) / "home"
            codex_home = home / ".codex"
            codex_home.mkdir(parents=True)
            env = os.environ.copy()
            env.update({"HOME": str(home), "CODEX_HOME": str(codex_home)})

            run([codex, "plugin", "marketplace", "add", str(ROOT)], env)
            available = load_plugin_list(run([codex, "plugin", "list", "--marketplace", "heading", "--available", "--json"], env), "available")
            validate_entry(available, installed=False)
            installed_payload = json.loads(run([codex, "plugin", "add", PLUGIN_ID, "--json"], env))
            require(isinstance(installed_payload, dict) and installed_payload.get("pluginId") == PLUGIN_ID, "plugin add response mismatch")
            installed = load_plugin_list(run([codex, "plugin", "list", "--marketplace", "heading", "--json"], env), "installed")
            validate_entry(installed, installed=True)

            cache = codex_home / "plugins" / "cache" / "heading" / "heading" / VERSION
            require(cache.is_dir(), "installed plugin cache is missing")
            for relative in (Path("plugin.json"), Path(".codex-plugin/plugin.json")):
                require((cache / relative).read_bytes() == (PLUGIN_ROOT / relative).read_bytes(), f"cached manifest drift: {relative}")
    except (OSError, json.JSONDecodeError, SmokeError) as error:
        print(f"smoke-plugin-install: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "PASS", "plugin": "heading", "version": VERSION, "marketplace": "heading", "installed": True, "enabled": True, "cacheManifests": "MATCH"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
