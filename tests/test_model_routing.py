"""Deterministic routing/capsule contracts; these are not model-quality benchmarks."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import itertools
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "plugins/heading/skills/heading-orchestrate"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ROUTER = load("heading_routing_tests", BASE / "scripts/model_routing.py")
CAPSULE = load("heading_capsule_tests", BASE / "scripts/evidence_capsule.py")
RUNNER = load("heading_eval_tests", ROOT / "scripts/run-evals.py")
POLICY = ROUTER.load_policy()
TASK_FACTS = {"clarity": "clear", "scope": "local", "reversible": True, "oracle": "strong", "risk": "routine"}


def shaped(shape: str, **overrides: object) -> dict[str, object]:
    return {**TASK_FACTS, "shape": shape, **overrides}


def valid_capsule() -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "outcomeId": "routing-v050",
        "baseRevision": "d7561c5",
        "purpose": "Choose a route from observed sources.",
        "facts": [{
            "id": "policy-owner", "source": "repository",
            "reference": "references/model-policy.json:1",
            "observation": "The policy owns route IDs.", "confidence": "observed",
        }],
        "openQuestions": [],
        "constraints": ["Read-only evidence collection."],
    }


class ModelRoutingTests(unittest.TestCase):
    def test_specialist_upfront_efforts_keep_model_and_need_no_luna_max_approval(self):
        for shape, extra, model, efforts in (
            ("fixed-extraction", {}, "gpt-5.6-luna", ("high", "xhigh", "max")),
            ("read-heavy-exploration", {}, "gpt-5.6-luna", ("high", "xhigh", "max")),
            ("read-heavy-exploration", {"scope": "cross-boundary"}, "gpt-5.6-terra", ("medium", "high")),
            ("implementation", {}, "gpt-5.6-terra", ("medium", "high")),
        ):
            for effort in efforts:
                payload = {"task": shaped(shape, **extra), "specialistEffort": effort,
                    "effortReason": "Avoid omission across bounded references", "effortEvidence": "sources/index:12"}
                result = ROUTER.select(payload, POLICY)
                self.assertEqual((result["requestedModel"], result["requestedReasoningEffort"],
                                  result["routingStatus"]), (model, effort, "REQUESTED"))
                self.assertIsNone(result["effectiveModel"])
                self.assertIsNone(result["effectiveReasoningEffort"])
        cli = subprocess.run([sys.executable, "-B", str(BASE / "scripts/model_routing.py")],
            input=json.dumps({"task": shaped("fixed-extraction"), "specialistEffort": "max",
                "effortReason": "Bounded extraction needs more reasoning", "effortEvidence": "input:12"}),
            capture_output=True, text=True)
        self.assertEqual(cli.returncode, 0, cli.stderr)
        self.assertEqual(json.loads(cli.stdout)["routeKey"], "luna-max")

    def test_specialist_effort_cannot_lower_floor_or_override_decision(self):
        common = {"effortReason": "Bounded question", "effortEvidence": "input:12"}
        for task, effort in ((shaped("fixed-extraction"), "medium"), (shaped("implementation"), "xhigh"),
                (shaped("implementation"), "max"), (shaped("unknown"), "high"),
                (shaped("read-heavy-exploration", risk="critical"), "max"),
                (shaped("deterministic"), "high")):
            with self.subTest(task=task, effort=effort), self.assertRaises(ROUTER.RoutingError):
                ROUTER.select({"task": task, "specialistEffort": effort, **common}, POLICY)
        for extra in ({"specialistEffort": None}, {"specialistEffort": "low"},
                      {"specialistEffort": "high", "astraEffort": "high"},
                      {"specialistEffort": "max", "maxBudgetAuthorized": True}):
            with self.subTest(extra=extra), self.assertRaises(ROUTER.RoutingError):
                ROUTER.select({"task": shaped("fixed-extraction"), **common, **extra}, POLICY)
        with self.assertRaises(ROUTER.RoutingError):
            ROUTER.select({"task": shaped("fixed-extraction"), "specialistEffort": "high"}, POLICY)

    def test_specialist_override_preserves_repairs_and_failure_budget(self):
        common = {"task": shaped("read-heavy-exploration"), "specialistEffort": "high",
            "effortReason": "Coupled evidence", "effortEvidence": "sources:12"}
        for failure in ("environment", "permission", "transient"):
            result = ROUTER.select({**common, "history": [{"route": "luna-max", "failure": failure,
                "evidence": "host.log:1"}]}, POLICY)
            self.assertEqual((result["routeKey"], result["routingStatus"]), ("luna-max", "REPAIR_REQUIRED"))
        history = [{"route": key, "failure": "reasoning", "evidence": "coverage:12"}
                   for key in ("luna-high", "luna-xhigh")]
        result = ROUTER.select({**common, "history": history}, POLICY)
        self.assertEqual((result["routeKey"], result["routingStatus"]), ("terra-high", "NEEDS_NEW_EVIDENCE"))

    def test_new_defaults_and_failure_transitions_never_select_old_low_routes(self):
        for shape in POLICY["taskShapes"]:
            result = ROUTER.select({"task": shaped(shape)}, POLICY)
            self.assertNotIn(result["routeKey"], {"luna-low", "luna-medium", "terra-low"})
        for old in ("luna-low", "luna-medium", "luna-high", "luna-xhigh", "luna-max"):
            result = ROUTER.select({"task": shaped("fixed-extraction"), "history": [{"route": old,
                "failure": "reasoning", "evidence": "coverage:12"}]}, POLICY)
            self.assertEqual((result["routeKey"], result["routingStatus"]), ("terra-medium", "REQUESTED"))

    def test_bounded_evidence_uses_luna_and_broad_evidence_uses_terra(self):
        for facts, route in (({}, "luna-high"), ({"scope": "cross-boundary"}, "terra-medium"),
                             ({"oracle": "weak"}, "terra-medium"), ({"scope": "unknown"}, "terra-medium")):
            result = ROUTER.select({"task": shaped("read-heavy-exploration", **facts),
                                    "allowEvidenceScouts": True}, POLICY)
            self.assertEqual(result["routeKey"], route)
            self.assertEqual(result["evidenceScoutCount"], 1)
            self.assertEqual(result["requestedForkTurns"], "none")
        result = ROUTER.select({"task": shaped("read-heavy-exploration", clarity="uncertain"),
                                "allowEvidenceScouts": True, "parallelism": "independent"}, POLICY)
        self.assertEqual(result["evidenceScoutCount"], 0)

    def test_upfront_effort_skips_failures_but_preserves_risk_floor(self):
        for effort in ("low", "medium", "high", "xhigh"):
            for risk in ("routine", "critical"):
                result = ROUTER.select({"task": shaped("cross-boundary-decision", risk=risk),
                    "astraEffort": effort, "effortReason": "Coupled replay and ownership constraints",
                    "effortEvidence": "src/replay.py:42"}, POLICY)
                expected = "high" if risk == "critical" and effort in ("low", "medium") else effort
                self.assertEqual((result["requestedReasoningEffort"], result["routingStatus"]), (expected, "REQUESTED"))
                self.assertIsNone(result["effectiveReasoningEffort"])

    def test_effort_hints_require_evidence_and_max_budget(self):
        task = shaped("cross-boundary-decision")
        valid = {"astraEffort": "max", "effortReason": "Recovery proof", "effortEvidence": "replay.py:42"}
        for extra in ({"astraEffort": "high"}, {"effortReason": "hard"}, valid,
                      {**valid, "effortEvidence": " "}, {**valid, "astraEffort": "none"},
                      {**valid, "maxBudgetAuthorized": 1}, {"parallelism": []}):
            with self.subTest(extra=extra), self.assertRaises(ROUTER.RoutingError):
                ROUTER.select({"task": task, **extra}, POLICY)
        result = ROUTER.select({"task": task, **valid, "maxBudgetAuthorized": True}, POLICY)
        self.assertEqual((result["routeKey"], result["routingStatus"]), ("astra-max", "REQUESTED"))
        with self.assertRaises(ROUTER.RoutingError):
            ROUTER.select({"task": shaped("deterministic"), **valid, "maxBudgetAuthorized": True}, POLICY)

    def test_no_blind_ladder_or_retry_of_failed_weaker_model(self):
        history = [{"route": route, "failure": "reasoning", "evidence": "failure.log:1"}
                   for route in ("luna-low", "terra-low")]
        task = shaped("read-heavy-exploration")
        result = ROUTER.select({"task": task, "history": history[:1]}, POLICY)
        self.assertEqual(result["routeKey"], "terra-medium")
        for attempts in (history, list(reversed(history))):
            result = ROUTER.select({"task": task, "history": attempts}, POLICY)
            self.assertEqual((result["routeKey"], result["routingStatus"]), ("astra-low", "NEEDS_NEW_EVIDENCE"))
        result = ROUTER.select({"task": task, "history": history, "astraEffort": "high",
            "effortReason": "Resolve observed owner conflict", "effortEvidence": "conflict.log:1"}, POLICY)
        self.assertEqual((result["routeKey"], result["routingStatus"]), ("astra-high", "REQUESTED"))

    def test_upfront_effort_does_not_bypass_environment_or_exhaustion(self):
        task = shaped("cross-boundary-decision")
        for failure in ("environment", "permission", "transient"):
            result = ROUTER.select({"task": task, "astraEffort": "xhigh", "effortReason": "Replay proof",
                "effortEvidence": "replay.py:42", "history": [{"route": "terra-low", "failure": failure,
                                                               "evidence": "host.log:1"}]}, POLICY)
            self.assertEqual((result["routeKey"], result["routingStatus"]), ("terra-low", "REPAIR_REQUIRED"))
        for route, expected in (("astra-high", "astra-xhigh"), ("astra-xhigh", "astra-max")):
            result = ROUTER.select({"task": task, "history": [{"route": route, "failure": "reasoning",
                                                               "evidence": "tests.log:1"}]}, POLICY)
            self.assertEqual(result["routeKey"], expected)
            self.assertEqual(result["routingStatus"], "REQUESTED" if route == "astra-high" else "NEEDS_NEW_EVIDENCE")

    def test_three_model_policy_and_optional_profile_defaults(self):
        self.assertEqual(set(POLICY["models"]), {"gpt-5.6-luna", "gpt-5.6-terra", "gpt-6-astra"})
        profile = tomllib.loads((ROOT / "runtime/heading/profile/heading.config.toml").read_text())
        self.assertEqual(profile["tools"], {"default_subagent_model": "gpt-5.6-luna",
            "default_subagent_reasoning_effort": "high", "max_concurrent_threads_per_session": 2})

    def test_pinned_routing_vectors(self):
        corpus = json.loads((ROOT / "evals/model-routing-cases.json").read_text())
        self.assertEqual(corpus["schemaVersion"], 2)
        self.assertEqual(len(corpus["cases"]), 17)
        for case in corpus["cases"]:
            with self.subTest(case=case["id"]):
                actual = ROUTER.select(case["input"], POLICY)
                for key, value in case["expected"].items():
                    self.assertEqual(actual[key], value)
                self.assertIsNone(actual["effectiveModel"])
                self.assertIsNone(actual["effectiveReasoningEffort"])
                expected_escalation = "NOT_APPLICABLE" if actual["routingStatus"] == "DIRECT_TOOLS" else "NOT_PROVEN"
                self.assertEqual(actual["modelEscalation"], expected_escalation)

    def test_every_declared_shape_accepts_every_supported_fact_combination(self):
        facts = list(POLICY["facts"]) + ["reversible"]
        options = [POLICY["facts"][key] for key in facts[:-1]] + [[True, False, None]]
        count = 0
        for shape in POLICY["taskShapes"]:
            for values in itertools.product(*options):
                task = {**dict(zip(facts, values)), "shape": shape}
                result = ROUTER.select({"task": task}, POLICY)
                self.assertEqual(result["workShape"], shape)
                if shape == "deterministic":
                    self.assertEqual((result["routeKey"], result["routingStatus"]), ("deterministic-tools", "DIRECT_TOOLS"))
                else:
                    self.assertIn(result["routeKey"], POLICY["routes"])
                count += 1
        self.assertEqual(count, 1296)

    def test_shape_routes_are_explicit_and_risk_gated(self):
        cases = [
            (shaped("deterministic"), "deterministic-tools", "DIRECT_TOOLS"),
            (shaped("fixed-extraction"), "luna-high", "REQUESTED"),
            (shaped("read-heavy-exploration", scope="cross-boundary", oracle="weak"), "terra-medium", "REQUESTED"),
            (shaped("implementation", scope="cross-boundary"), "terra-medium", "REQUESTED"),
            (shaped("cross-boundary-decision"), "astra-low", "REQUESTED"),
            (shaped("unknown"), "astra-low", "REQUESTED"),
            (shaped("read-heavy-exploration", risk="critical"), "astra-high", "REQUESTED"),
            (shaped("implementation", oracle="weak"), "astra-low", "REQUESTED"),
        ]
        for task, route, status in cases:
            with self.subTest(task=task):
                actual = ROUTER.select({"task": task}, POLICY)
                self.assertEqual((actual["routeKey"], actual["routingStatus"]), (route, status))

    def test_evidence_scouts_are_explicit_and_bounded(self):
        task = shaped("read-heavy-exploration", scope="cross-boundary", oracle="weak")
        for payload, expected in (
            ({"task": task}, 0),
            ({"task": task, "allowEvidenceScouts": True}, 1),
            ({"task": task, "allowEvidenceScouts": True, "parallelism": "independent"}, 2),
        ):
            actual = ROUTER.select(payload, POLICY)
            self.assertEqual(actual["evidenceScoutCount"], expected)
            self.assertTrue(actual["evidenceCapsuleRequired"])
        invalid = [
            {"task": shaped("implementation"), "allowEvidenceScouts": True, "parallelism": "independent"},
            {"task": task, "allowEvidenceScouts": True, "parallelism": "parallel"},
        ]
        for payload in invalid:
            with self.subTest(payload=payload), self.assertRaises(ROUTER.RoutingError):
                ROUTER.select(payload, POLICY)

    def test_transition_is_pure_and_repeatable(self):
        payload = {"task": shaped("implementation")}
        before = deepcopy(payload), deepcopy(POLICY)
        self.assertEqual(ROUTER.select(payload, POLICY), ROUTER.select(payload, POLICY))
        self.assertEqual((payload, POLICY), before)

    def test_missing_unknown_and_wrongly_typed_facts_fail(self):
        invalid: list[object] = [None, [], {}, {"task": {}}, {"task": TASK_FACTS, "model": "gpt-6-astra"}]
        for key in TASK_FACTS:
            task = deepcopy(TASK_FACTS)
            task.pop(key)
            invalid.append({"task": task})
        for key, value in (("reversible", 1), ("reversible", "true"), ("risk", []), ("scope", "small"), ("shape", "fanout")):
            task = shaped("implementation")
            task[key] = value
            invalid.append({"task": task})
        for option in ("allowUltra", "ultraBudgetAuthorized", "allowEvidenceScouts"):
            invalid.append({"task": shaped("fixed-extraction"), option: 1})
        invalid.append({"task": shaped("fixed-extraction"), "obsoleteInput": True})
        invalid.extend((
            {"task": shaped("fixed-extraction"), "ultraReason": "unpaired exception reason"},
            {"task": shaped("fixed-extraction"), "ultraBudgetAuthorized": True},
            {"task": shaped("read-heavy-exploration"), "parallelism": "independent"},
        ))
        for payload in invalid:
            with self.subTest(payload=payload), self.assertRaises(ROUTER.RoutingError):
                ROUTER.select(payload, POLICY)

    def test_history_requires_observed_failure_reference(self):
        invalid = [None, {}, [None], [{}], [{"route": "luna-low", "failure": "reasoning", "evidence": ""}],
                   [{"route": "unknown", "failure": "reasoning", "evidence": "log:1"}],
                   [{"route": "luna-low", "failure": "success", "evidence": "log:1"}]]
        for history in invalid:
            with self.subTest(history=history), self.assertRaises(ROUTER.RoutingError):
                ROUTER.select({"task": shaped("fixed-extraction"), "history": history}, POLICY)

    def test_specialist_failure_moves_to_astra_and_unknown_inputs_are_rejected(self):
        specialist = ROUTER.select({
            "task": shaped("read-heavy-exploration", scope="cross-boundary", oracle="weak"),
            "history": [{"route": "terra-low", "failure": "reasoning", "evidence": "scan.log:4"}],
        }, POLICY)
        self.assertEqual((specialist["routeKey"], specialist["routingStatus"]), ("astra-low", "REQUESTED"))
        with self.assertRaises(ROUTER.RoutingError):
            ROUTER.select({"task": shaped("fixed-extraction"), "obsoleteInput": True}, POLICY)

    def test_retry_limit_cannot_be_evaded_by_repeating_failure(self):
        entry = {"route": "luna-low", "failure": "reasoning", "evidence": "tests/log:1"}
        with self.assertRaises(ROUTER.RoutingError):
            ROUTER.select({"task": shaped("fixed-extraction"), "history": [entry, entry]}, POLICY)

    def test_policy_allows_only_current_route_efforts(self):
        invalid = [
            ("gpt-6-astra", "minimal"), ("gpt-6-astra", "none"), ("gpt-6-astra", "light"),
            ("astra-low", "low"), ("gpt-6-astra-pro", "low"), ("gpt-5.6-luna", "ultra"),
            ("gpt-5.6-terra", "none"), ("gpt-5.6-sol", "low"),
        ]
        for model, effort in invalid:
            with self.subTest(model=model, effort=effort), self.assertRaises(ROUTER.RoutingError):
                ROUTER.validate_pair(model, effort, POLICY)
        for model, efforts in POLICY["models"].items():
            for effort in efforts:
                ROUTER.validate_pair(model, effort, POLICY)

    def test_observed_fields_must_match_model_and_locked_authority(self):
        request = ROUTER.select({"task": shaped("implementation")}, POLICY)
        expected = {"taskId": "child-1", "role": "heading_executor", "sandbox": "workspace-write"}
        observation = {**expected, "source": "host-metadata", "model": request["requestedModel"],
                       "effort": request["requestedReasoningEffort"], "evidenceRef": "host/session.json:1"}
        self.assertEqual(ROUTER.observation_status(request, observation, expected=expected), "MATCHED_HOST_FIELDS")
        for key in observation:
            bad = deepcopy(observation)
            bad[key] = "" if key == "evidenceRef" else "wrong"
            self.assertEqual(ROUTER.observation_status(request, bad, expected=expected), "NOT_PROVEN", key)
        direct = ROUTER.select({"task": shaped("deterministic")}, POLICY)
        self.assertEqual(ROUTER.observation_status(direct, observation, expected=expected), "NOT_PROVEN")
        self.assertIsNone(request["effectiveModel"])

    def test_role_files_cannot_override_task_route(self):
        for path in (ROOT / "runtime/heading/agents").glob("*.toml"):
            role = tomllib.loads(path.read_text())
            self.assertNotIn("model", role)
            self.assertNotIn("model_reasoning_effort", role)
            expected = "workspace-write" if role["name"] == "heading_executor" else "read-only"
            self.assertEqual(role["sandbox_mode"], expected)

    def test_profile_matches_single_policy_lead_default(self):
        profile = tomllib.loads((ROOT / "runtime/heading/profile/heading.config.toml").read_text())
        self.assertEqual((profile["model"], profile["model_reasoning_effort"]), ("gpt-5.6-luna", "low"))

    def test_policy_or_role_drift_is_rejected(self):
        paths = [
            ("plugins/heading/skills/heading-orchestrate/references/model-policy.json",
             lambda text: text.replace('"fixedExtraction": "luna-high"', '"fixedExtraction": "astra-low"')),
            ("runtime/heading/agents/heading-executor.toml", lambda text: 'model = "gpt-5.6-luna"\n' + text),
        ]
        for relative, mutate in paths:
            with self.subTest(path=relative), tempfile.TemporaryDirectory() as temporary:
                copy = Path(temporary) / "source"
                shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", "__pycache__", "eval-results"))
                path = copy / relative
                path.write_text(mutate(path.read_text()))
                result = subprocess.run([sys.executable, "-B", str(copy / "scripts/validate.py")], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue("digest mismatch" in result.stderr or "agent fields mismatch" in result.stderr, result.stderr)

    def test_real_helper_cli_and_error_exit(self):
        command = [sys.executable, "-B", str(BASE / "scripts/model_routing.py")]
        result = subprocess.run(command, input=json.dumps({"task": shaped("fixed-extraction")}), text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["routeKey"], "luna-high")
        for raw in ("{", "null", '{"task":{}}'):
            result = subprocess.run(command, input=raw, text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertIn("model-routing:", result.stderr)

    def test_evidence_capsule_validator_rejects_unbounded_or_ambiguous_handoffs(self):
        capsule = valid_capsule()
        result = CAPSULE.validate_capsule(capsule)
        self.assertEqual(result["status"], "VALID")
        self.assertEqual(result["facts"], 1)
        invalid = []
        extra = deepcopy(capsule)
        extra["instructions"] = ["write files"]
        invalid.append(extra)
        duplicate = deepcopy(capsule)
        duplicate["facts"].append(deepcopy(duplicate["facts"][0]))
        invalid.append(duplicate)
        stale = deepcopy(capsule)
        stale["baseRevision"] = "bad revision"
        invalid.append(stale)
        raw = deepcopy(capsule)
        raw["facts"][0]["observation"] = "x\n" + "y"
        invalid.append(raw)
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(CAPSULE.CapsuleError):
                CAPSULE.validate_capsule(value)
        command = [sys.executable, "-B", str(BASE / "scripts/evidence_capsule.py")]
        cli = subprocess.run(command, input=json.dumps(capsule), text=True, capture_output=True)
        self.assertEqual(cli.returncode, 0, cli.stderr)
        self.assertEqual(json.loads(cli.stdout)["status"], "VALID")
        rejected = subprocess.run(command, input="null", text=True, capture_output=True)
        self.assertEqual(rejected.returncode, 2)
        self.assertIn("evidence-capsule:", rejected.stderr)

    def test_native_eval_command_sets_model_and_effort_together(self):
        for route in POLICY["routes"].values():
            command = RUNNER.command_for("codex", Path("/repo"), Path("/result"), "prompt", route)
            self.assertEqual(command[command.index("--model") + 1], route["model"])
            self.assertEqual(command[command.index("-c") + 1], f'model_reasoning_effort="{route["effort"]}"')
            self.assertEqual(command[command.index("--sandbox") + 1], "read-only")
        self.assertNotIn("--model", RUNNER.command_for("codex", Path("/repo"), Path("/result"), "prompt"))

    def test_native_eval_route_dry_run_is_not_execution(self):
        result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/run-evals.py"),
                                 "--dry-run", "--limit", "1", "--route", "terra-low"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "DRY_RUN")
        self.assertIn("gpt-5.6-terra", payload["plan"][0]["command"])

    def test_timeout_keeps_bytes_evidence_and_never_claims_success(self):
        error = subprocess.TimeoutExpired(["codex"], 1, output=b'{"event":"partial"}\n', stderr=b"partial error")
        with patch.object(RUNNER.subprocess, "run", side_effect=error):
            stdout, stderr, meta = RUNNER.execute_case(["codex"], ROOT, {}, 1)
        self.assertIn("partial", stdout)
        self.assertIn("TIMEOUT", stderr)
        self.assertIsNone(meta["exitCode"])
        self.assertEqual(meta["executionStatus"], "TIMEOUT")
        self.assertGreaterEqual(meta["durationSeconds"], 0)

    def test_missing_executable_returns_observed_spawn_failure(self):
        stdout, stderr, meta = RUNNER.execute_case(["/nonexistent/heading-codex"], ROOT, dict(os.environ), 1)
        self.assertEqual(stdout, "")
        self.assertTrue(stderr)
        self.assertEqual(meta["executionStatus"], "SPAWN_FAILED")
        self.assertIsNone(meta["exitCode"])

    def test_actual_subprocess_exit_is_preserved(self):
        stdout, stderr, meta = RUNNER.execute_case([sys.executable, "-c", 'print("observed");raise SystemExit(7)'], ROOT, dict(os.environ), 2)
        self.assertEqual(stdout.strip(), "observed")
        self.assertEqual(meta["exitCode"], 7)
        self.assertEqual(meta["executionStatus"], "EXITED")
        stdout, stderr, meta = RUNNER.execute_case(
            [sys.executable, "-c", 'import time;print("partial",flush=True);time.sleep(2)'], ROOT, dict(os.environ), 1)
        self.assertIn("partial", stdout)
        self.assertIn("TIMEOUT", stderr)
        self.assertEqual(meta["executionStatus"], "TIMEOUT")
        self.assertIsNone(meta["exitCode"])

    def test_invalid_eval_timeout_fails_before_execution(self):
        result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/run-evals.py"), "--timeout", "0", "--dry-run"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("positive", result.stderr)

    def test_ultra_requires_explicit_exception_and_budget_authorization(self):
        task = shaped("cross-boundary-decision", scope="cross-boundary")
        failed = {"route": "astra-xhigh", "failure": "reasoning", "evidence": "recovery.log:4"}
        result = ROUTER.select({"task": task, "history": [failed]}, POLICY)
        self.assertEqual(result["routingStatus"], "NEEDS_NEW_EVIDENCE")
        for extra in ({"ultraReason": "Very difficult recovery proof"}, {"ultraBudgetAuthorized": True}):
            with self.subTest(extra=extra), self.assertRaises(ROUTER.RoutingError):
                ROUTER.select({"task": task, "history": [failed], **extra}, POLICY)
        for reason in ("", "  ", None, 1):
            with self.subTest(reason=reason), self.assertRaises(ROUTER.RoutingError):
                ROUTER.select({"task": task, "allowUltra": True, "ultraBudgetAuthorized": True, "ultraReason": reason}, POLICY)
        for history in ([], [failed]):
            result = ROUTER.select({"task": task, "history": history, "allowUltra": True, "ultraBudgetAuthorized": True,
                                   "ultraReason": "Coupled recovery proof; session budget authorized"}, POLICY)
            self.assertEqual((result["routeKey"], result["routingStatus"]), ("astra-ultra", "REQUESTED"))
            self.assertEqual(result["requestedReasoningEffort"], "ultra")
            self.assertIsNone(result["effectiveReasoningEffort"])

    def test_ultra_exception_cannot_bypass_environment_or_exhaustion(self):
        payload = {"task": shaped("cross-boundary-decision", scope="cross-boundary"), "allowUltra": True, "ultraBudgetAuthorized": True,
                   "ultraReason": "Coupled recovery proof; session budget authorized"}
        for failure in ("environment", "permission", "transient"):
            result = ROUTER.select({**payload, "history": [
                {"route": "astra-medium", "failure": failure, "evidence": "host.log:2"}]}, POLICY)
            self.assertEqual((result["routeKey"], result["routingStatus"]), ("astra-medium", "REPAIR_REQUIRED"))
        for suffix in ([], [{"route": "luna-medium", "failure": "reasoning", "evidence": "tests.log:5"}]):
            result = ROUTER.select({**payload, "history": [
                {"route": "astra-ultra", "failure": "reasoning", "evidence": "tests.log:4"}, *suffix]}, POLICY)
            self.assertEqual(result["routingStatus"], "NEEDS_NEW_EVIDENCE")

    def test_unlisted_routes_fail_in_history_and_native_eval(self):
        self.assertEqual(POLICY["models"]["gpt-6-astra"], ["low", "medium", "high", "xhigh", "max", "ultra"])
        self.assertEqual(POLICY["astraLadder"], ["astra-low", "astra-medium", "astra-high", "astra-xhigh", "astra-max", "astra-ultra"])
        for route in ("astra-unlisted", "luna-unlisted"):
            with self.subTest(route=route), self.assertRaises(ROUTER.RoutingError):
                ROUTER.select({"task": shaped("fixed-extraction"), "history": [
                    {"route": route, "failure": "reasoning", "evidence": "policy.log:1"}]}, POLICY)
            result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/run-evals.py"),
                                     "--dry-run", "--limit", "1", "--route", route], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("invalid choice", result.stderr)
