from __future__ import annotations

import fcntl
import importlib.util
import json
import os
import resource
from pathlib import Path
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import textwrap
import unicodedata
import unittest


ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = ROOT / "plugins" / "heading"
INSTALLER = ROOT / "scripts/install.py"
VALIDATOR = ROOT / "scripts/validate.py"
PLUGIN_VALIDATOR = ROOT / "scripts/validate-plugin.py"
PLUGIN_SMOKE = ROOT / "scripts/smoke-plugin-install.py"
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
        skills: Path,
        *extra: str,
        env: dict[str, str] | None = None,
        preexec_fn=None,
    ) -> subprocess.CompletedProcess[str]:
        return self.run_python(
            INSTALLER,
            *extra,
            "--install-legacy-skills",
            "--codex-home",
            str(codex),
            "--skills-root",
            str(skills),
            env=env,
            preexec_fn=preexec_fn,
        )

    def seed_namespace(self, codex: Path, skills: Path, identity: str, *, content: str = "old\n") -> list[Path]:
        profile = codex / f"{identity}.config.toml"
        agent = codex / "agents" / f"{identity}-agent.toml"
        skill_file = skills / f"{identity}-skill" / "nested" / "state.txt"
        profile.parent.mkdir(parents=True, exist_ok=True)
        agent.parent.mkdir(parents=True, exist_ok=True)
        skill_file.parent.mkdir(parents=True, exist_ok=True)
        profile.write_text(content, encoding="utf-8")
        agent.write_text(content, encoding="utf-8")
        skill_file.write_text(content, encoding="utf-8")
        return [profile, agent, skill_file]

    def copy_source(self, destination: Path) -> Path:
        source = destination / "source"
        shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(".git"))
        return source

    def run_fault_injected(
        self,
        codex: Path,
        skills: Path,
        patch: str,
    ) -> subprocess.CompletedProcess[str]:
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
                f'sys.argv = [str(installer), "--install-legacy-skills", "--codex-home", {str(codex)!r}, "--skills-root", {str(skills)!r}]',
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

    def assert_no_active_product(self, codex: Path, skills: Path) -> None:
        self.assertFalse((codex / "heading.config.toml").exists())
        self.assertEqual(list((codex / "agents").glob("heading-*")) if (codex / "agents").is_dir() else [], [])
        self.assertEqual(list(skills.glob("heading-*")) if skills.is_dir() else [], [])

    # Source and semantic contracts

    def test_bundle_validation(self) -> None:
        result = self.run_python(VALIDATOR)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload, {"status": "PASS", "version": "0.3.1", "files": 53, "tracks": 5, "skills": 6, "childRoles": 4, "modes": 27, "evals": 182, "modeEvals": 32, "intakeEvals": 125, "dialogueEvals": 25})

    def test_bundle_validation_with_python_optimize(self) -> None:
        result = self.run_python(VALIDATOR, env={"PYTHONOPTIMIZE": "1"})
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_profile_only_install_never_copies_plugin_skill_namespaces(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codex, skills = base / "codex", base / "skills"
            result = self.run_python(
                INSTALLER, "--codex-home", str(codex), "--skills-root", str(skills), "--dry-run",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(len(payload["install"]), 5)
            self.assertFalse(any("heading-build" in path for path in payload["install"]))
            installed = self.run_python(INSTALLER, "--codex-home", str(codex), "--skills-root", str(skills))
            self.assertEqual(installed.returncode, 0, installed.stderr)
            self.assertFalse(skills.exists())

    def test_each_track_skill_mutation_is_rejected(self) -> None:
        spec = importlib.util.spec_from_file_location("heading_validate_skill_mutation", VALIDATOR)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        validator = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = validator
        spec.loader.exec_module(validator)
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            for track in TRACKS:
                source = self.copy_source(base / track)
                skill = source / "plugins/heading/skills" / f"heading-{track}" / "SKILL.md"
                skill.write_text(skill.read_text(encoding="utf-8") + "\nmutated runtime contract\n", encoding="utf-8")
                validator.ROOT = source
                validator.PLUGIN_ROOT = source / "plugins/heading"
                validator.SKILLS_ROOT = validator.PLUGIN_ROOT / "skills"
                validator.RUNTIME_ROOT = source / "runtime/heading"
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
            base = Path(temporary)
            for track in TRACKS:
                source = self.copy_source(base / track)
                method = source / "plugins/heading/skills" / f"heading-{track}" / "references/METHOD.md"
                method.write_text(method.read_text(encoding="utf-8") + "\nmutated method\n", encoding="utf-8")
                validator.ROOT = source
                validator.PLUGIN_ROOT = source / "plugins/heading"
                validator.SKILLS_ROOT = validator.PLUGIN_ROOT / "skills"
                validator.RUNTIME_ROOT = source / "runtime/heading"
                with self.subTest(track=track), self.assertRaisesRegex(validator.ValidationError, "method content mismatch"):
                    validator.validate_skills()

    def test_eval_corpus_and_semantic_coverage_mutations_are_rejected(self) -> None:
        spec = importlib.util.spec_from_file_location("heading_validate_eval_mutation", VALIDATOR)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        validator = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = validator
        spec.loader.exec_module(validator)
        with tempfile.TemporaryDirectory() as temporary:
            source = self.copy_source(Path(temporary))
            cases_path = source / "evals/cases.json"
            original = json.loads(cases_path.read_text(encoding="utf-8"))
            validator.ROOT = source
            validator.PLUGIN_ROOT = source / "plugins/heading"
            validator.SKILLS_ROOT = validator.PLUGIN_ROOT / "skills"
            validator.RUNTIME_ROOT = source / "runtime/heading"

            mutations = []
            duplicate_mode = json.loads(json.dumps(original))
            duplicate_mode["cases"][1]["mode"] = duplicate_mode["cases"][0]["mode"]
            mutations.append(("duplicate positive eval mode", duplicate_mode))

            wrong_invocation = json.loads(json.dumps(original))
            boundary = next(case for case in wrong_invocation["cases"] if case["kind"] == "boundary")
            boundary["prompt"] = boundary["prompt"].replace(f"${boundary['skill']}", "$heading-build")
            mutations.append(("eval prompt invocation mismatch", wrong_invocation))

            missing_auto_route = json.loads(json.dumps(original))
            boundary = next(case for case in missing_auto_route["cases"] if case["kind"] == "boundary")
            boundary["must"] = ["BLOCKED" if value == "AUTO_ROUTE" else value for value in boundary["must"]]
            mutations.append(("boundary route contract mismatch", missing_auto_route))

            for expected, payload in mutations:
                with self.subTest(expected=expected):
                    encoded = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
                    cases_path.write_text(encoded, encoding="utf-8")
                    validator.EVALS_DIGEST = __import__("hashlib").sha256(encoded.encode("utf-8")).hexdigest()
                    with self.assertRaisesRegex(validator.ValidationError, expected):
                        validator.validate_evals()

            cases_path.write_text(json.dumps(original, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def test_skill_contract_requires_auto_routing_and_three_intake_actions(self) -> None:
        for track in TRACKS:
            text = (PLUGIN_ROOT / "skills" / f"heading-{track}" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("The invoked skill is a hint.", text)
            self.assertIn("continue in this conversation", text)
            self.assertIn("`PROCEED`, `ASK`, or `REFUSE`", text)
            self.assertIn("Report a route correction only when the effective track differs from the invoked track: append one concise correction to `adjustments`", text)
            self.assertIn("Before writable work, lock `outcome_id`, `owned_surface`, `done`, and `evidence`", text)
            self.assertIn("non-empty child thread ID", text)
            self.assertIn("executionMode: DIRECT", text)
            self.assertIn("independentReview: NOT_PROVEN", text)
            self.assertIn("Only Lead makes final claims.", text)
            self.assertIn("User-facing result", text)
            self.assertIn("plain words and a Feynman-style explanation", text)
            self.assertIn("Choose detail by task shape, not by a fixed line or word limit", text)
            self.assertIn("Start with the conclusion and use progressive disclosure", text)
            self.assertIn("Do not print full YAML/JSON", text)
            self.assertNotIn("at most six short lines", text)
            self.assertNotIn("no more than four lines", text)
            self.assertNotIn("`HANDOFF`", text)
        prototype = (PLUGIN_ROOT / "skills" / "heading-prototype" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("A request to test an otherwise unspecified idea is still a usable desirability decision", prototype)
        lifecycle = (PLUGIN_ROOT / "skills" / "heading-maintain" / "references" / "PROCESS-LIFECYCLE.md").read_text(encoding="utf-8")
        self.assertIn("Never reconstruct a kill scope from a late PGID", lifecycle)
        self.assertIn("no owned descendant", lifecycle)

    def test_source_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = self.copy_source(Path(temporary))
            target = source / "DESIGN.md"
            target.unlink()
            target.symlink_to("README.md")
            result = self.run_python(source / "scripts/validate.py", cwd=source)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source symlink", result.stderr)

    def test_plugin_package_is_valid_and_rejects_portable_manifest_drift(self) -> None:
        result = self.run_python(PLUGIN_VALIDATOR)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["skills"], 6)
        with tempfile.TemporaryDirectory() as temporary:
            source = self.copy_source(Path(temporary))
            manifest = source / "plugins/heading/plugin.json"
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["skills"] = "./skills/"
            manifest.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            result = self.run_python(source / "scripts/validate-plugin.py", cwd=source)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unsupported keys", result.stderr)

    def test_plugin_validator_rejects_directory_ineligible_default_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = self.copy_source(Path(temporary))
            manifest = source / "plugins/heading/.codex-plugin/plugin.json"
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["interface"]["defaultPrompt"] = "x" * 129
            manifest.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            result = self.run_python(source / "scripts/validate-plugin.py", cwd=source)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("exceeds 128 characters", result.stderr)

            payload["interface"]["defaultPrompt"] = "Use $heading-build for this request."
            manifest.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            result = self.run_python(source / "scripts/validate-plugin.py", cwd=source)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must not require explicit skill invocation", result.stderr)

    def test_plugin_validator_rejects_invocation_policy_drift_and_smoke_verifies_enabled_install(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = self.copy_source(Path(temporary))
            metadata = source / "plugins/heading/skills/heading-build/agents/openai.yaml"
            metadata.write_text(metadata.read_text(encoding="utf-8").replace("allow_implicit_invocation: true", "allow_implicit_invocation: false"), encoding="utf-8")
            rejected = self.run_python(source / "scripts/validate-plugin.py", cwd=source)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("core skill must allow implicit invocation", rejected.stderr)

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
            self.assertEqual(json.loads(smoke.stdout)["enabled"], True)

    def test_ignored_workspace_artifacts_do_not_break_source_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = self.copy_source(Path(temporary))
            (source / ".DS_Store").write_text("finder\n", encoding="utf-8")
            (source / ".pytest_cache").mkdir()
            (source / ".pytest_cache" / "state").write_text("cache\n", encoding="utf-8")
            (source / "eval-results").mkdir()
            (source / "eval-results" / "result.json").write_text("{}\n", encoding="utf-8")
            result = self.run_python(source / "scripts/validate.py", cwd=source)
            self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(sys.platform == "darwin", "macOS system aliases only")
    def test_macos_system_aliases_are_canonicalized_but_custom_symlinks_remain_unsafe(self) -> None:
        spec = importlib.util.spec_from_file_location("heading_install_macos_alias", INSTALLER)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        installer = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = installer
        spec.loader.exec_module(installer)

        self.assertEqual(
            installer.normalize_root(Path("/var/folders/heading-test")),
            Path("/private/var/folders/heading-test"),
        )
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            external = base / "external"
            external.mkdir()
            alias = base / "alias"
            alias.symlink_to(external, target_is_directory=True)
            with self.assertRaisesRegex(installer.InstallError, "symlink"):
                installer.assert_safe_root(installer.normalize_root(alias / "codex"), "codex")

    def test_plain_install_is_idempotent_only_in_current_clean_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codex, skills = base / "codex", base / "skills"
            first = self.install(codex, skills)
            self.assertEqual(first.returncode, 0, first.stderr)
            second = self.install(codex, skills)
            self.assertEqual(second.returncode, 0, second.stderr)
            checked = self.install(codex, skills, "--check")
            self.assertEqual(checked.returncode, 0, checked.stderr)

    def test_removed_option_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codex, skills = base / "codex", base / "skills"
            removed_option = "--" + "clean" + "-break"
            result = self.install(codex, skills, removed_option)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unrecognized arguments", result.stderr)
            self.assert_no_active_product(codex, skills)

    def test_heading_namespace_conflict_is_non_destructive(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codex, skills = base / "codex", base / "skills"
            foreign = skills / "heading-build/foreign.txt"
            foreign.parent.mkdir(parents=True)
            foreign.write_text("keep\n", encoding="utf-8")
            result = self.install(codex, skills)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unexpected file in managed skill namespace", result.stderr)
            self.assertEqual(foreign.read_text(encoding="utf-8"), "keep\n")

    def test_dry_run_reports_plan_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codex, skills = base / "codex", base / "skills"
            result = self.install(codex, skills, "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["mode"], "plan")
            self.assertEqual(len(payload["install"]), 24)
            self.assertEqual(payload["remove"], [])
            self.assertFalse((codex / ".heading-deploy.lock").exists())
            self.assertFalse((skills / ".heading-deploy.lock").exists())

    # Path and filesystem adversaries

    def test_root_ancestor_symlink_is_rejected_without_external_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            external = base / "external"
            external.mkdir()
            alias = base / "alias"
            alias.symlink_to(external, target_is_directory=True)
            result = self.install(alias / "codex", alias / "skills")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("symlink", result.stderr)
            self.assertEqual(list(external.iterdir()), [])

    def test_internal_ancestor_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codex, skills, external = base / "codex", base / "skills", base / "external"
            codex.mkdir()
            external.mkdir()
            (codex / "agents").symlink_to(external, target_is_directory=True)
            result = self.install(codex, skills)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(list(external.iterdir()), [])

    def test_destination_symlink_and_hardlink_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            for kind in ("symlink", "hardlink"):
                with self.subTest(kind=kind):
                    case = base / kind
                    codex, skills = case / "codex", case / "skills"
                    codex.mkdir(parents=True)
                    outside = case / "outside.toml"
                    outside.write_text("outside\n", encoding="utf-8")
                    destination = codex / "heading.config.toml"
                    if kind == "symlink":
                        destination.symlink_to(outside)
                    else:
                        os.link(outside, destination)
                    result = self.install(codex, skills)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(outside.read_text(encoding="utf-8"), "outside\n")

    def test_overlapping_roots_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            for codex, skills in ((base / "root", base / "root/skills"), (base / "root/codex", base / "root")):
                with self.subTest(codex=codex, skills=skills):
                    result = self.install(codex, skills)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("must not be inside", result.stderr)

    def test_unicode_space_newline_and_deep_roots(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary) / "공백 dir\nline"
            deep = base.joinpath(*[f"d{i}" for i in range(80)])
            codex, skills = deep / "코덱스", deep / "스킬"
            result = self.install(codex, skills)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(self.install(codex, skills, "--check").returncode, 0)

    def test_external_tmpdir_and_missing_home_do_not_affect_explicit_roots(self) -> None:
        shared_memory = Path("/dev/shm")
        with tempfile.TemporaryDirectory() as temporary:
            other_parent = shared_memory if shared_memory.is_dir() and os.access(shared_memory, os.W_OK) else None
            with tempfile.TemporaryDirectory(dir=other_parent) as other:
                base = Path(temporary)
                result = self.install(
                    base / "codex",
                    base / "skills",
                    env={"TMPDIR": other, "HOME": "/definitely/missing"},
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_relative_roots_hostile_locale_and_stale_lock_modes_converge(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codex, skills = Path("relative-codex"), Path("relative-skills")
            for root in (base / codex, base / skills):
                root.mkdir()
                lock = root / ".heading-deploy.lock"
                lock.write_text("stale\n", encoding="utf-8")
                lock.chmod(0o777)
            result = self.run_python(
                INSTALLER,
                "--install-legacy-skills",
                "--codex-home",
                str(codex),
                "--skills-root",
                str(skills),
                cwd=base,
                env={
                    "LC_ALL": "C",
                    "LANG": "C",
                    "TZ": "Pacific/Kiritimati",
                    "PYTHONHASHSEED": "random",
                    "HOME": "/missing-home",
                },
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(stat.S_IMODE((base / codex / ".heading-deploy.lock").stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE((base / skills / ".heading-deploy.lock").stat().st_mode), 0o600)
            checked = self.run_python(
                INSTALLER,
                "--check",
                "--install-legacy-skills",
                "--codex-home",
                str(codex),
                "--skills-root",
                str(skills),
                cwd=base,
                env={"LC_ALL": "C", "LANG": "C", "HOME": "/missing-home"},
            )
            self.assertEqual(checked.returncode, 0, checked.stderr)

    def test_unicode_normalization_distinct_roots_are_not_collapsed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            nfc = unicodedata.normalize("NFC", "e\u0301")
            nfd = unicodedata.normalize("NFD", "é")
            if nfc == nfd:
                self.skipTest("normalization forms are not distinct")
            codex, skills = base / nfc / "codex", base / nfd / "skills"
            result = self.install(codex, skills)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotEqual(codex, skills)
            self.assertTrue((codex / "heading.config.toml").is_file())
            self.assertTrue((skills / "heading-build/SKILL.md").is_file())
            self.assertEqual(self.install(codex, skills, "--check").returncode, 0)

    def test_non_directory_root_objects_are_rejected_unchanged(self) -> None:
        if not hasattr(os, "mkfifo") or not hasattr(socket, "AF_UNIX"):
            self.skipTest("required special files are unavailable")
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            for kind in ("file", "fifo", "socket", "dangling-symlink"):
                with self.subTest(kind=kind):
                    case = base / kind
                    case.mkdir()
                    root = case / "codex"
                    skills = case / "skills"
                    handle = None
                    if kind == "file":
                        root.write_text("unchanged\n", encoding="utf-8")
                    elif kind == "fifo":
                        os.mkfifo(root)
                    elif kind == "socket":
                        handle = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                        handle.bind(str(root))
                    else:
                        root.symlink_to(case / "missing-target", target_is_directory=True)
                    try:
                        before = root.lstat()
                        result = self.install(root, skills)
                        self.assertNotEqual(result.returncode, 0)
                        after = root.lstat()
                        self.assertEqual((before.st_mode, before.st_ino), (after.st_mode, after.st_ino))
                        self.assertFalse(skills.exists())
                    finally:
                        if handle is not None:
                            handle.close()

    def test_low_file_descriptor_limit_still_installs(self) -> None:
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        if hard < 32:
            self.skipTest("file descriptor hard limit is below test threshold")
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codex, skills = base / "codex", base / "skills"

            def limit_descriptors() -> None:
                resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))

            result = self.install(codex, skills, preexec_fn=limit_descriptors)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(self.install(codex, skills, "--check").returncode, 0)

    def test_restrictive_umask_does_not_change_managed_modes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codex, skills = base / "codex", base / "skills"
            result = self.install(codex, skills, preexec_fn=lambda: os.umask(0o077))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(stat.S_IMODE((codex / "heading.config.toml").stat().st_mode), 0o644)
            self.assertEqual(stat.S_IMODE((skills / "heading-build/SKILL.md").stat().st_mode), 0o644)
            self.assertEqual(stat.S_IMODE((codex / ".heading-deploy.lock").stat().st_mode), 0o600)

    # Concurrency, rollback, and drift

    def test_each_root_lock_prevents_concurrent_deployment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            for locked_root in ("codex", "skills"):
                with self.subTest(locked_root=locked_root):
                    case = base / locked_root
                    codex, skills = case / "codex", case / "skills"
                    codex.mkdir(parents=True)
                    skills.mkdir(parents=True)
                    lock_path = (codex if locked_root == "codex" else skills) / ".heading-deploy.lock"
                    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
                    try:
                        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        result = self.install(codex, skills)
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn("another Heading deployment is active", result.stderr)
                    finally:
                        fcntl.flock(fd, fcntl.LOCK_UN)
                        os.close(fd)

    def test_mid_install_failure_rolls_back_new_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codex, skills = base / "codex", base / "skills"
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
            result = self.run_fault_injected(codex, skills, patch)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("injected link failure", result.stderr)
            self.assert_no_active_product(codex, skills)
    def test_mode_and_content_drift_are_handled_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codex, skills = base / "codex", base / "skills"
            self.assertEqual(self.install(codex, skills).returncode, 0)
            profile = codex / "heading.config.toml"
            profile.chmod(0o600)
            self.assertNotEqual(self.install(codex, skills, "--check").returncode, 0)
            repaired = self.install(codex, skills)
            self.assertEqual(repaired.returncode, 0, repaired.stderr)
            self.assertEqual(stat.S_IMODE(profile.stat().st_mode), 0o644)
            target = skills / "heading-build/SKILL.md"
            target.write_text("changed\n", encoding="utf-8")
            conflict = self.install(codex, skills)
            self.assertNotEqual(conflict.returncode, 0)
            self.assertEqual(target.read_text(encoding="utf-8"), "changed\n")
            self.assertEqual(target.read_text(encoding="utf-8"), "changed\n")

    def test_unexpected_managed_file_is_rejected_non_destructively(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codex, skills = base / "codex", base / "skills"
            foreign = skills / "heading-build/foreign.txt"
            foreign.parent.mkdir(parents=True)
            foreign.write_text("old product-owned content\n", encoding="utf-8")
            normal = self.install(codex, skills)
            self.assertNotEqual(normal.returncode, 0)
            self.assertEqual(foreign.read_text(encoding="utf-8"), "old product-owned content\n")
            self.assertTrue(foreign.exists())

    def test_installed_validator(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codex, skills = base / "codex", base / "skills"
            self.assertEqual(self.install(codex, skills).returncode, 0)
            result = self.run_python(
                VALIDATOR,
                "--installed",
                "--codex-home",
                str(codex),
                "--skills-root",
                str(skills),
            )
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
