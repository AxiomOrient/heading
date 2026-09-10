#!/usr/bin/env python3
"""Validate the Heading source package or an installed copy."""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import stat
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = ROOT / "plugins" / "heading"
SKILLS_ROOT = PLUGIN_ROOT / "skills"
RUNTIME_ROOT = ROOT / "runtime" / "heading"
VERSION = "0.5.0"
TRACK_ORDER = ("prototype", "build", "sweep", "grow", "maintain")
# Version-control metadata is not part of the package and never installed.
IGNORED_ROOT_ENTRIES = (".git", ".DS_Store", ".coverage", ".pytest_cache", "eval-results")
EVALS_DIGEST = "dcf9a9b55f9ea8869fd24029bb33cdf64af0ace3b4a919e88674fb3ea53ea376"
INTAKE_EVALS_DIGEST = "87ca287ac7df3ce686b098042adeaa4c3c3ea42e8518468bd47d0eaae01e9967"
DIALOGUE_EVALS_DIGEST = "d050367a4004a7f541a88bd7bce50476c1c728c49e5a715d37d308bc80dc5442"
MODEL_POLICY_DIGEST = "8ae5f9842e08aa9397f3a4c515f2f1f3b4ad5ecc87a4f1a27ed37fe800a1e8e3"
MODEL_ROUTING_EVALS_DIGEST = "a3638d9f4108e0be5a4c363d6303798435e417fe3b5ebe1699ef6f6c3a202fb6"
ROUTE_BENCHMARK_PLAN_DIGEST = "e5aef80836f205ebaa11c72fad56b8eb3e4861c94941af355b26936f698cc941"
INTAKE_SCHEMA_DIGEST = "c200842fdd1249962194354110c1b8fcb992d68df24a80ca16b4f105909ce5dd"


class ValidationError(RuntimeError):
    """A package invariant failed."""


@dataclass(frozen=True)
class AgentSpec:
    name: str
    sandbox: str
    required: tuple[str, ...]


@dataclass(frozen=True)
class TrackSpec:
    title: str
    description: str
    purpose: str
    use_when: str
    not_when: str
    lock: str
    guardrail: str
    done: str
    flow: str
    modes: tuple[str, ...]
    skill_digest: str
    method_digest: str
    method_required: tuple[str, ...]


ROUTING_AGENT_REQUIRED = (
    "requestedModel", "requestedReasoningEffort", "riskBand", "workShape", "modelEscalationReason",
    "effectiveModel", "effectiveReasoningEffort", "modelEscalation: NOT_PROVEN", "evidence capsule",
    "missing routing input permits read-only inspection only", "observable host metadata",
    "Do not change model, sandbox, owned surface, or writer ownership yourself",
)

AGENTS = {
    "heading-planner": AgentSpec("heading_planner", "read-only", ROUTING_AGENT_REQUIRED + (
        "actual repository evidence", "primary sources", "report the mismatch to Lead",
        "Do not edit files", "spawn agents", "direct another agent")),
    "heading-executor": AgentSpec("heading_executor", "workspace-write", ROUTING_AGENT_REQUIRED + (
        "delegated outcome", "complete change", "strongest faithful verification", "safe in-scope method",
        "Preserve unrelated behavior", "report the mismatch to Lead", "EXECUTOR_ACCEPTED", "EXECUTOR_RESULT",
        "Do not wait", "Never claim `PASS` or `READY`")),
    "heading-reviewer": AgentSpec("heading_reviewer", "read-only", ROUTING_AGENT_REQUIRED + (
        "actual candidate", "severity-ranked findings", "Lead only", "Do not edit files",
        "contact the Executor", "direct another agent")),
    "heading-architect": AgentSpec("heading_architect", "read-only", ROUTING_AGENT_REQUIRED + (
        "bounded architecture question", "failure modes", "implementation constraints",
        "track or outcome mismatch", "Do not edit files", "spawn agents")),
}


TRACKS = {
    "prototype": TrackSpec(
        "Prototype",
        "Use when a product decision needs a reversible, evidence-backed probe before building. A mismatched requested track is corrected before work starts.",
        "Resolve one product decision by testing the riskiest assumption with the cheapest faithful reversible probe.",
        "The primary uncertainty is desirability, workflow, feasibility, viability, or generative quality.",
        "The behavior is already accepted and the primary outcome is production delivery, simplification, measured growth, or mature-system control.",
        "Decision, mode, target context, riskiest assumption, representative sample, threshold, fidelity budget, isolation, and disposal rule.",
        "No production-ready claim, irreversible integration, deceptive live test, or cherry-picked evidence.",
        "Actual observations cross the locked threshold and support `ADOPT`, `REJECT`, `ITERATE`, or `INCONCLUSIVE`; only transferable learning survives.",
        "FRAME -> SELECT -> PROBE -> OBSERVE -> DECIDE",
        ("desirability", "workflow", "feasibility", "viability", "generative-quality"),
        "af83581ebfa3a6fc60665b205c41eb848cb68315823e6acc9d583ec2276c6641",
        "ea9a14d20d3cf0bc742d896e5fd9e0a65f15fddab25fa1e2299d57f885e295de",
        ("Repair the method instead of rejecting a valid goal", "Wizard-of-Oz or concierge run", "locked corpus, rubric, holdout cases", "Refuse only when deception"),
    ),
    "build": TrackSpec(
        "Build",
        "Use when accepted behavior needs one complete, evidence-backed production outcome. A mismatched requested track is corrected before work starts.",
        "Turn accepted behavior into one integrated, deployable, operable outcome.",
        "Product meaning is decided and the remaining uncertainty is implementation, integration, or delivery.",
        "The main question is whether to build it, whether it improves a product metric, or how to simplify existing behavior.",
        "Delivery class, accepted behavior, real entry and environment, public contracts, owned boundaries, non-goals, applicable proof packs, and release evidence.",
        "No disconnected scaffolds, fake success, speculative scope, or production-grade claim without critical-path evidence.",
        "The entry-to-effect-to-durable-output path and every applicable failure, recovery, release, and operational proof pack pass.",
        "CLASSIFY -> CONTRACT -> SLICE -> PROVE -> RELEASE",
        ("product-slice", "library-api", "service", "adapter", "data-change", "delivery-infra"),
        "dd60a3d93c073e3bc56aac5d97f21b50180096fd5309a1b8727d613fe0f2c9fd",
        "780e44b75f2f8a96fe38b482568cbec4f4a0e5f71c90d155b2d9754a97430988",
        ("Repair invalid methods while preserving the build goal", "native or authoritative fixture", "versioned model, prompt, tool", "Refuse only when bypass"),
    ),
    "sweep": TrackSpec(
        "Sweep",
        "Use when complexity, code, UI, or cost should be reduced while locked behavior stays intact. A mismatched requested track is corrected before work starts.",
        "Reduce code, UI, state, interfaces, dependencies, or resource cost while preserving locked product meaning.",
        "The primary outcome is deletion, collapse, behavior-preserving refactor, UI simplification, or measured performance improvement.",
        "The change adds product behavior, repairs an active reliability risk, or tests a market hypothesis.",
        "Mode, preserved oracle, representative corpus, baseline, one subtractive seam, target delta, non-goals, and revert rule.",
        "No broad rewrite, compatibility shim, speculative abstraction, or benchmark claim from incomparable or noisy runs.",
        "The same oracle passes before and after, and evidence shows net deletion, simpler ownership, clearer interaction, or measured resource gain.",
        "ORACLE -> CUT -> COMPARE -> KEEP_OR_REVERT",
        ("delete", "collapse", "refactor", "ui", "performance"),
        "0bad44d1b72f048cc993a272632048e5e0c9608c3202ded396cb79efabb242c3",
        "44b804d9788efacd3cc880e0e7f72439517be614a131454c42b3ea773a544cd7",
        ("Repair invalid methods while preserving the goal", "same outputs and failures", "warmup and repeated samples", "Refuse only when concealment"),
    ),
    "grow": TrackSpec(
        "Grow",
        "Use when a shipped product outcome needs a decision-grade growth experiment and measurement. A mismatched requested track is corrected before work starts.",
        "Improve one shipped-product outcome with a precommitted measurement and decision design.",
        "A usable product exists and behavior can be measured through randomized, sequential, switchback, holdout, or observational evidence.",
        "The need is qualitative discovery, initial product construction, elective simplification, or operational repair.",
        "Segment, evidence design, assignment and analysis unit, exposure, hypothesis and falsifier, primary metric, guardrails, data-quality checks, threshold, window, stopping rule, and rollback.",
        "No fabricated metric, dark pattern, unauthorized tracking, peeking under fixed-horizon analysis, metric switching, or causal claim from associational evidence.",
        "Implementation and data quality are separately proven; completed evidence supports `KEEP`, `ROLLBACK`, `ITERATE`, or `NOT_PROVEN` with an explicit evidence grade.",
        "DESIGN -> INSTRUMENT -> SHIP -> ANALYZE -> DECIDE",
        ("randomized", "sequential", "switchback", "holdout-rollout", "observational"),
        "aeeda15e19bc03169f62eda0a5c44c17eb780a4cee022016f34d75fca89eabda",
        "556451dba4dbd12537e9295e94d6316b7c42c62f4711e5203ecae701a9955174",
        ("Repair invalid methods while preserving the growth goal", "sample-ratio check", "precommitted sequential method", "Refuse only when fabricated reporting"),
    ),
    "maintain": TrackSpec(
        "Maintain",
        "Use when an existing system needs risk control, repair, incident response, or safe operational change. A mismatched requested track is corrected before work starts.",
        "Restore, protect, or safely change a mature system while preserving explicit invariants and recovery control.",
        "The primary outcome is incident response, defect repair, security remediation, reliability or capacity work, planned operational change, or data repair.",
        "The primary outcome is a new product slice, discovery experiment, growth experiment, or elective simplification.",
        "Mode, impact and urgency, evidence and timeline, invariants, affected version or data, blast radius, containment, rollback or recovery, stop conditions, and post-change watch.",
        "No silent fallback, mock success, opportunistic incident refactor, uncontrolled fault injection, or irreversible repair without backup and verification.",
        "Impact is controlled; cause or rationale is evidenced; change, recovery, regression, and post-change observations support `RESTORED`, `STABILIZED`, `CHANGED`, `PARTIAL`, or `BLOCKED`.",
        "TRIAGE -> CONTAIN -> CHANGE -> RECOVER -> WATCH",
        ("incident", "defect", "security", "reliability-capacity", "planned-change", "data-repair"),
        "714032bee410488a3dd4af2ed250c259b6d7af589c0837d10f33350c621101cb",
        "f4f2734c8770d092f3018c78667186d926043ad931686ab8484c4e378d8b0318",
        ("Repair invalid methods while preserving the operational goal", "Contain harm before", "immutable backup or snapshot", "Refuse only when concealment"),
    ),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_files() -> set[Path]:
    files = {
        Path(".gitignore"), Path("DESIGN.md"), Path("LICENSE"), Path("PLAYBOOK.ko.md"), Path("PLAYBOOK.md"),
        Path("README.ko.md"), Path("README.md"), Path("VALIDATION.md"), Path("VERSION"),
        Path(".agents/plugins/marketplace.json"), Path("verify-source-package.sh"),
        Path("evals/cases.json"), Path("evals/dialogue_cases.json"), Path("evals/intake-output.schema.json"), Path("evals/intake_cases.json"), Path("evals/route-benchmark-plan.json"),
        Path("scripts/grade-evals.py"), Path("scripts/install.py"), Path("scripts/install.sh"), Path("scripts/run-evals.py"),
        Path("scripts/run-tests.py"), Path("scripts/smoke-plugin-install.py"), Path("scripts/validate.py"), Path("scripts/validate-plugin.py"), Path("scripts/validate.sh"),
        Path("tests/__init__.py"), Path("tests/test_heading.py"), Path("tests/test_intake.py"),
    }
    files.update({
        Path("plugins/heading/plugin.json"),
        Path("plugins/heading/.codex-plugin/plugin.json"),
        Path("runtime/heading/profile/heading.config.toml"),
    })
    for name in AGENTS:
        files.add(Path("runtime/heading/agents") / f"{name}.toml")
    for track in TRACK_ORDER:
        base = Path("plugins/heading/skills") / f"heading-{track}"
        files.update({base / "SKILL.md", base / "agents/openai.yaml", base / "references/METHOD.md"})
    files.add(Path("plugins/heading/skills/heading-maintain/references/PROCESS-LIFECYCLE.md"))
    orchestrate = Path("plugins/heading/skills/heading-orchestrate")
    files.update({orchestrate / "SKILL.md", orchestrate / "agents/openai.yaml", orchestrate / "references/ORCHESTRATION.md"})
    files.update(Path(name) for name in (
        "IDENTITY_AND_EVOLUTION.md", "SPEC.md", "ARCHITECTURE.md", "ANALYSIS.md",
        "IMPLEMENTATION_STATUS.md", "PLAN.md", "docs/adr/0001-task-based-model-routing.md",
        "evals/model-routing-cases.json", "tests/test_model_routing.py",
    ))
    files.update(orchestrate / name for name in (
        "references/EVIDENCE-CAPSULE.md", "references/MODEL-ROUTING.md", "references/RESEARCH-2026-09-10.md",
        "references/model-policy.json", "scripts/evidence_capsule.py", "scripts/model_routing.py",
    ))
    return files


def validate_layout() -> None:
    require((ROOT / "VERSION").read_text(encoding="utf-8").strip() == VERSION, "version mismatch")
    actual: set[Path] = set()
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if relative.parts[0] in IGNORED_ROOT_ENTRIES:
            continue
        require(not path.is_symlink(), f"source symlink is not allowed: {relative}")
        if path.is_file():
            value = path.lstat()
            require(stat.S_ISREG(value.st_mode), f"source special file is not allowed: {relative}")
            require(value.st_nlink == 1, f"source hard link is not allowed: {relative}")
            require("__pycache__" not in path.parts and path.suffix != ".pyc", f"generated Python output is not allowed: {relative}")
            actual.add(relative)
    expected = expected_files()
    require(actual == expected, f"source layout mismatch: missing={sorted(map(str, expected-actual))} extra={sorted(map(str, actual-expected))}")
    for relative in expected:
        path = ROOT / relative
        executable = relative == Path("verify-source-package.sh") or "scripts" in relative.parts and relative.suffix in {".py", ".sh"}
        expected_mode = 0o755 if executable else 0o644
        actual_mode = stat.S_IMODE(path.stat().st_mode)
        require(actual_mode == expected_mode, f"source mode mismatch: {relative}: {oct(actual_mode)} != {oct(expected_mode)}")


def validate_profile() -> None:
    payload = tomllib.loads((RUNTIME_ROOT / "profile/heading.config.toml").read_text(encoding="utf-8"))
    require(payload == {
        "model": "gpt-6-astra", "model_reasoning_effort": "low", "sandbox_mode": "workspace-write", "approval_policy": "on-request",
        "agents": {"default_subagent_model": "gpt-5.6-luna", "default_subagent_reasoning_effort": "high",
                   "max_concurrent_threads_per_session": 2},
    }, "profile contract mismatch")


def validate_agents() -> None:
    writable = 0
    for key, spec in AGENTS.items():
        path = RUNTIME_ROOT / "agents" / f"{key}.toml"
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
        require(set(payload) == {"name", "description", "sandbox_mode", "developer_instructions"}, f"agent fields mismatch: {key}")
        require(payload["name"] == spec.name, f"agent name mismatch: {key}")
        require(payload["sandbox_mode"] == spec.sandbox, f"agent sandbox mismatch: {key}")
        instructions = payload["developer_instructions"]
        require(isinstance(instructions, str), f"agent instructions missing: {key}")
        for phrase in spec.required:
            require(phrase in instructions, f"agent instruction missing: {key}: {phrase}")
        if spec.sandbox == "workspace-write":
            writable += 1
    require(writable == 1, f"expected one writable child role, found {writable}")


def parse_frontmatter(text: str, path: Path) -> dict[str, str]:
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    require(match is not None, f"skill frontmatter missing: {path}")
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        require(":" in line, f"invalid skill frontmatter: {path}: {line}")
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def validate_skills() -> None:
    common = (
        "A one-line request is enough.",
        "The optional `heading` profile is a separate local runtime setting and is not required for this skill.",
        "The invoked skill is a hint.",
        "continue in this conversation",
        "Never ask the user to invoke another skill.",
        "PROCEED`, `ASK`, or `REFUSE",
        "PROCEED` by default",
        "reject only that method",
        "REFUSE` only when the essential goal itself",
        "Missing tools or platforms reduce only the affected proof to `NOT_PROVEN`",
        "MODEL-ROUTING.md",
        "model-policy.json",
        "Choose by work shape, not role",
        "Astra `low`",
        "Luna `high`",
        "Terra `medium`",
        "Terra `medium`",
        "evidence capsule",
        "Role files intentionally omit model and effort; dispatch must supply both",
        "observe the old writer and its processes stopped",
        "## Verification scope",
        "requestedModel",
        "effectiveModel",
        "requestedReasoningEffort",
        "effectiveReasoningEffort",
        "modelEscalationReason",
        "modelEscalation: NOT_PROVEN",
        "without changing role or sandbox",
        "same Executor thread",
        "There is no fixed model quota.",
        "Report a route correction only when the effective track differs from the invoked track: append one concise correction to `adjustments`",
        "Before writable work, lock `outcome_id`, `owned_surface`, `done`, and `evidence`",
        "non-empty child thread ID",
        "executionMode: DIRECT",
        "independentReview: NOT_PROVEN",
        "Only Lead makes final claims.",
        "User-facing result",
        "Use the method schema and proof fields to decide the claim",
        "plain words and a Feynman-style explanation",
        "Choose detail by task shape, not by a fixed line or word limit",
        "Start with the conclusion and use progressive disclosure",
        "Do not print full YAML/JSON",
        "Never make a response shorter by omitting material evidence",
    )
    for track, spec in TRACKS.items():
        base = SKILLS_ROOT / f"heading-{track}"
        skill = base / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        require(digest_file(skill) == spec.skill_digest, f"skill content mismatch: {track}")
        require("at most six short lines" not in text, f"fixed response line limit leaked: {track}")
        require("no more than four lines" not in text, f"blocked response line limit leaked: {track}")
        frontmatter = parse_frontmatter(text, skill.relative_to(ROOT))
        require(frontmatter == {"name": f"heading-{track}", "description": spec.description}, f"skill frontmatter mismatch: {track}")
        contracts = {
            "Purpose": spec.purpose, "Use when": spec.use_when, "Do not use when": spec.not_when,
            "Lock": spec.lock, "Guardrail": spec.guardrail, "Done": spec.done,
        }
        for label, value in contracts.items():
            require(f"- **{label}:** {value}" in text, f"track contract mismatch: {track}/{label}")
        require(f"`{spec.flow}`" in text, f"track flow mismatch: {track}")
        for phrase in common:
            require(phrase in text, f"common skill contract missing: {track}: {phrase}")
        require("HANDOFF" not in text, f"obsolete HANDOFF intake leaked into skill: {track}")
        method = base / "references/METHOD.md"
        method_text = method.read_text(encoding="utf-8")
        require(digest_file(method) == spec.method_digest, f"method content mismatch: {track}")
        for mode in spec.modes:
            require(f"`{mode}`" in method_text, f"method mode missing: {track}/{mode}")
        for phrase in spec.method_required:
            require(phrase in method_text, f"method requirement missing: {track}: {phrase}")

        metadata = (base / "agents/openai.yaml").read_text(encoding="utf-8")
        require(f'display_name: "Heading {spec.title}"' in metadata, f"skill display name mismatch: {track}")
        require(f'default_prompt: "Use $heading-{track}. Bind the canonical workspace and evidence freshness first;' in metadata, f"skill default prompt mismatch: {track}")
        require("auto-correct the effective track before lock" in metadata, f"skill auto-route prompt missing: {track}")
        require("allow_implicit_invocation: true" in metadata, f"skill must allow implicit invocation: {track}")

    prototype = (SKILLS_ROOT / "heading-prototype" / "SKILL.md").read_text(encoding="utf-8")
    require(
        "A request to test an otherwise unspecified idea is still a usable desirability decision" in prototype,
        "prototype default-probe rule missing",
    )
    maintain = SKILLS_ROOT / "heading-maintain"
    lifecycle = (maintain / "references/PROCESS-LIFECYCLE.md").read_text(encoding="utf-8")
    for phrase in ("Immediately after\nspawn succeeds", "Never reconstruct a kill scope from a late PGID", "runtimeObserved: NOT_PROVEN", "Exact-scope teardown", "no owned descendant"):
        require(phrase in lifecycle, f"process lifecycle contract missing: {phrase}")
    orchestrate = SKILLS_ROOT / "heading-orchestrate"
    orchestrate_skill = (orchestrate / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(orchestrate_skill, orchestrate.relative_to(ROOT) / "SKILL.md")
    require(frontmatter["name"] == "heading-orchestrate", "orchestration skill name mismatch")
    for phrase in ("task packet", "Direct lane", "Native lane", "User-visible task lane", "Never silently substitute", "higher model tier", "Task-based model routing", "MODEL-ROUTING.md", "model-policy.json", "EVIDENCE-CAPSULE.md", "work shape", "DIRECT_TOOLS", "requestedModel", "effectiveModel", "requestedReasoningEffort", "effectiveReasoningEffort", "modelEscalationReason", "modelEscalation: NOT_PROVEN", "modelEscalation: NOT_APPLICABLE", "non-empty task ID", "primary reviewer", "NOT_PROVEN", "BLOCKED"):
        require(phrase in orchestrate_skill, f"orchestration contract missing: {phrase}")
    metadata = (orchestrate / "agents/openai.yaml").read_text(encoding="utf-8")
    require('display_name: "Heading Orchestrate"' in metadata and "allow_implicit_invocation: false" in metadata, "orchestration metadata mismatch")
    reference = (orchestrate / "references/ORCHESTRATION.md").read_text(encoding="utf-8")
    for phrase in ("exactly one writer", "observed facts", "Task packet schema", "higher model tier", "Task-based model routing", "model-policy.json", "MODEL-ROUTING.md", "EVIDENCE-CAPSULE.md", "work shape", "DIRECT_TOOLS", "modelEscalation: NOT_PROVEN", "modelEscalation: NOT_APPLICABLE", "PASS", "PARTIAL", "NOT_PROVEN", "BLOCKED"):
        require(phrase in reference, f"orchestration reference missing: {phrase}")


def load_pinned_json(relative: str, digest: str) -> dict:
    path = ROOT / relative
    require(digest_file(path) == digest, f"pinned eval digest mismatch: {relative}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(payload, dict), f"JSON root must be an object: {relative}")
    return payload


def validate_context(context: object, identifier: str) -> None:
    require(isinstance(context, dict) and set(context) == {"files", "note"}, f"context keys mismatch: {identifier}")
    files = context["files"]
    require(isinstance(files, dict), f"context files must be an object: {identifier}")
    for raw, content in files.items():
        path = Path(raw)
        require(isinstance(raw, str) and not path.is_absolute() and path.parts and all(part not in {"", ".", ".."} for part in path.parts), f"unsafe context path: {identifier}/{raw}")
        require(isinstance(content, str), f"context file content must be text: {identifier}/{raw}")
    require(isinstance(context["note"], str), f"context note must be text: {identifier}")


def validate_mode_evals() -> int:
    payload = load_pinned_json("evals/cases.json", EVALS_DIGEST)
    require(set(payload) == {"schemaVersion", "cases"} and payload["schemaVersion"] == 1, "mode eval schema mismatch")
    cases = payload["cases"]
    require(isinstance(cases, list) and len(cases) == 32, "mode eval count mismatch")
    ids: set[str] = set()
    positives: dict[str, set[str]] = {track: set() for track in TRACK_ORDER}
    boundaries: set[str] = set()
    boundary_targets = {
        "prototype": "build",
        "build": "prototype",
        "sweep": "build",
        "grow": "prototype",
        "maintain": "build",
    }
    for case in cases:
        require(isinstance(case, dict) and set(case) == {"id", "kind", "mode", "must", "mustNot", "prompt", "skill"}, f"mode eval keys mismatch: {case}")
        identifier = case["id"]
        require(isinstance(identifier, str) and re.fullmatch(r"[a-z0-9-]+", identifier) and identifier not in ids, f"invalid mode eval id: {identifier}")
        ids.add(identifier)
        skill = case["skill"]
        require(skill in {f"heading-{track}" for track in TRACK_ORDER}, f"unknown mode eval skill: {identifier}")
        source = skill.removeprefix("heading-")
        invocations = set(re.findall(r"\$heading-[a-z-]+", case["prompt"]))
        require(invocations == {f"$heading-{source}"}, f"eval prompt invocation mismatch: {identifier}")
        require(isinstance(case["must"], list) and isinstance(case["mustNot"], list), f"mode eval assertions must be lists: {identifier}")
        if case["kind"] == "positive":
            mode = case["mode"]
            require(mode in TRACKS[source].modes, f"positive eval mode mismatch: {identifier}")
            require(mode not in positives[source], f"duplicate positive eval mode: {source}/{mode}")
            positives[source].add(mode)
            require(len(case["must"]) >= 3, f"positive eval proof too weak: {identifier}")
        elif case["kind"] == "boundary":
            boundaries.add(source)
            target = boundary_targets[source]
            require(case["mode"] == "", f"boundary eval must not pin source mode: {identifier}")
            require(set(case["must"]) == {"AUTO_ROUTE", f"effective track: {target}", "continue in the same conversation"}, f"boundary route contract mismatch: {identifier}")
            require(set(case["mustNot"]) == {"ask the user to repeat", "ask the user to invoke another skill", "stop at route mismatch"}, f"boundary stop behavior missing: {identifier}")
            require("HANDOFF" not in json.dumps(case, ensure_ascii=False), f"obsolete HANDOFF boundary leaked: {identifier}")
        else:
            raise ValidationError(f"unknown mode eval kind: {identifier}")
    for track, spec in TRACKS.items():
        require(positives[track] == set(spec.modes), f"positive mode coverage mismatch: {track}")
    require(boundaries == set(TRACK_ORDER), f"boundary track coverage mismatch: {sorted(boundaries)}")
    return len(cases)


def validate_intake_expected(expected: object, invoked: str, identifier: str) -> str:
    keys = {"action", "track", "routedFrom", "mode", "question", "mustInclude", "mustExclude"}
    require(isinstance(expected, dict) and set(expected) == keys, f"intake expected keys mismatch: {identifier}")
    action = expected["action"]
    effective = expected["track"]
    routed_from = expected["routedFrom"]
    mode = expected["mode"]
    require(action in {"PROCEED", "ASK", "REFUSE"}, f"invalid intake action: {identifier}: {action}")
    require(effective in TRACKS and routed_from in {"", *TRACK_ORDER}, f"invalid intake route: {identifier}")
    require(expected["question"] in {"required", "forbidden"}, f"invalid question policy: {identifier}")
    require(isinstance(expected["mustInclude"], list) and isinstance(expected["mustExclude"], list), f"invalid intake tokens: {identifier}")
    require(all(isinstance(value, str) and value for value in expected["mustInclude"] + expected["mustExclude"]), f"empty intake token: {identifier}")

    if action == "PROCEED":
        require(mode in TRACKS[effective].modes, f"PROCEED mode mismatch: {identifier}")
        require(expected["question"] == "forbidden", f"PROCEED cannot ask: {identifier}")
        if effective == invoked:
            require(routed_from == "", f"same-track PROCEED must not set routedFrom: {identifier}")
        else:
            require(routed_from == invoked, f"route target mismatch: {identifier}")
            require("adjustments" in expected["mustInclude"], f"route correction must be surfaced: {identifier}")
    elif action == "ASK":
        require(effective == invoked and routed_from == "", f"ASK cannot pre-emptively route: {identifier}")
        require(mode == "" or mode in TRACKS[invoked].modes, f"ASK mode mismatch: {identifier}")
        require(expected["question"] == "required", f"ASK requires one question: {identifier}")
    else:
        require(effective == invoked and routed_from == "" and mode == "", f"REFUSE route or mode mismatch: {identifier}")
        require(expected["question"] == "forbidden" and "safeAlternative" in expected["mustInclude"], f"REFUSE safe alternative missing: {identifier}")
    return action


def validate_intake_evals() -> int:
    payload = load_pinned_json("evals/intake_cases.json", INTAKE_EVALS_DIGEST)
    require(set(payload) == {"schemaVersion", "cases"} and payload["schemaVersion"] == 1, "intake corpus schema mismatch")
    cases = payload["cases"]
    require(isinstance(cases, list) and len(cases) == 125, "intake case count mismatch")
    keys = {"id", "track", "persona", "language", "style", "request", "context", "expected"}
    ids: set[str] = set()
    requests: set[str] = set()
    personas: set[str] = set()
    languages: set[str] = set()
    styles: set[str] = set()
    short_requests = 0
    action_totals: dict[str, int] = {}
    per_track: dict[str, dict[str, int]] = {track: {} for track in TRACK_ORDER}
    routes: dict[str, set[str]] = {track: set() for track in TRACK_ORDER}
    effective_modes: dict[str, set[str]] = {track: set() for track in TRACK_ORDER}
    adjusted: dict[str, int] = {track: 0 for track in TRACK_ORDER}
    not_proven = 0
    for case in cases:
        require(isinstance(case, dict) and set(case) == keys, f"intake case keys mismatch: {case}")
        identifier = case["id"]
        track = case["track"]
        request = case["request"]
        require(isinstance(identifier, str) and re.fullmatch(r"[a-z0-9-]+", identifier) and identifier not in ids, f"invalid intake id: {identifier}")
        require("handoff" not in identifier, f"obsolete handoff intake id: {identifier}")
        ids.add(identifier)
        require(track in TRACKS and identifier.startswith(f"{track}-"), f"intake track mismatch: {identifier}")
        for field, values in (("persona", personas), ("language", languages), ("style", styles)):
            value = case[field]
            require(isinstance(value, str) and value.strip() == value and value, f"invalid {field}: {identifier}")
            values.add(value)
        require(isinstance(request, str) and request.strip() == request and len(request) >= 4 and request not in requests, f"duplicate or invalid intake request: {identifier}")
        requests.add(request)
        require(set(re.findall(r"\$heading-[a-z-]+", request)) == {f"$heading-{track}"}, f"intake invocation mismatch: {identifier}")
        short_requests += int(len(request) <= 30)
        validate_context(case["context"], identifier)
        action = validate_intake_expected(case["expected"], track, identifier)
        action_totals[action] = action_totals.get(action, 0) + 1
        per_track[track][action] = per_track[track].get(action, 0) + 1
        expected = case["expected"]
        if expected["routedFrom"]:
            routes[track].add(expected["track"])
        if action == "PROCEED":
            effective_modes[expected["track"]].add(expected["mode"])
        if "adjustments" in expected["mustInclude"]:
            adjusted[track] += 1
        if "NOT_PROVEN" in expected["mustInclude"]:
            not_proven += 1
        if case["style"] == "prompt-injection":
            require(expected["mustExclude"], f"prompt-injection case must exclude the injected instruction: {identifier}")
        if "-refuse-" in identifier:
            require(action == "REFUSE", f"refuse-labelled case must refuse: {identifier}")
        if "-repair-" in identifier:
            require(action == "PROCEED" and "adjustments" in expected["mustInclude"], f"repair-labelled case must proceed with adjustment: {identifier}")
    require(action_totals == {"PROCEED": 100, "ASK": 20, "REFUSE": 5}, f"intake corpus action totals mismatch: {action_totals}")
    for track in TRACK_ORDER:
        count = sum(per_track[track].values())
        require(count == 25, f"intake track case count mismatch: {track}: {count}")
        require(per_track[track].get("PROCEED", 0) >= 18, f"intake must bias to useful execution: {track}: {per_track[track]}")
        require(per_track[track].get("ASK", 0) >= 1, f"material-question coverage missing: {track}")
        require(per_track[track].get("REFUSE", 0) == 1, f"narrow-refusal coverage mismatch: {track}")
        require(routes[track] == set(TRACK_ORDER) - {track}, f"intake auto-route coverage mismatch: {track}: {sorted(routes[track])}")
        require(adjusted[track] >= 8, f"safe-method repair coverage too small: {track}: {adjusted[track]}")
    for track, spec in TRACKS.items():
        require(effective_modes[track] == set(spec.modes), f"effective mode coverage mismatch: {track}: {sorted(effective_modes[track])}")
    require(short_requests >= 20, f"ordinary short-request coverage too small: {short_requests}")
    require(len(personas) >= 15 and len(languages) >= 3 and len(styles) >= 12, "intake diversity too small")
    require(sum(1 for case in cases if case["style"] == "prompt-injection") >= 5, "prompt-injection coverage missing")
    require(not_proven >= 4, "partial-proof coverage missing")
    return len(cases)


def validate_dialogue_evals() -> int:
    payload = load_pinned_json("evals/dialogue_cases.json", DIALOGUE_EVALS_DIGEST)
    require(set(payload) == {"schemaVersion", "cases"} and payload["schemaVersion"] == 1, "dialogue corpus schema mismatch")
    cases = payload["cases"]
    require(isinstance(cases, list) and len(cases) == 25, "dialogue case count mismatch")
    keys = {"id", "track", "persona", "language", "style", "history", "request", "context", "expected"}
    ids: set[str] = set()
    suffixes: dict[str, set[str]] = {track: set() for track in TRACK_ORDER}
    per_track: dict[str, dict[str, int]] = {track: {} for track in TRACK_ORDER}
    for case in cases:
        require(isinstance(case, dict) and set(case) == keys, f"dialogue case keys mismatch: {case}")
        identifier = case["id"]
        track = case["track"]
        require(isinstance(identifier, str) and re.fullmatch(r"[a-z0-9-]+", identifier) and identifier not in ids, f"invalid dialogue id: {identifier}")
        require("handoff" not in identifier, f"obsolete handoff dialogue id: {identifier}")
        ids.add(identifier)
        require(track in TRACKS and identifier.startswith(f"{track}-"), f"dialogue track mismatch: {identifier}")
        suffixes[track].add(identifier.removeprefix(f"{track}-"))
        history = case["history"]
        require(isinstance(history, list) and len(history) == 2 and history[0].get("role") == "user" and history[1].get("role") == "assistant", f"dialogue history mismatch: {identifier}")
        require(all(isinstance(turn.get("content"), str) for turn in history), f"dialogue content mismatch: {identifier}")
        require(set(re.findall(r"\$heading-[a-z-]+", history[0]["content"] + "\n" + case["request"])) == {f"$heading-{track}"}, f"dialogue invocation mismatch: {identifier}")
        validate_context(case["context"], identifier)
        action = validate_intake_expected(case["expected"], track, identifier)
        require(action != "ASK", f"dialogue must not repeat clarification: {identifier}")
        if identifier.endswith("untrusted-injection"):
            require(case["expected"]["mustExclude"], f"untrusted-instruction case must exclude the injected instruction: {identifier}")
        per_track[track][action] = per_track[track].get(action, 0) + 1
        if identifier.endswith("mid-session-realign"):
            require(action == "PROCEED" and case["expected"]["routedFrom"] == track, f"dialogue track shift must auto-route: {identifier}")
    expected_suffixes = {"answer-once", "vague-answer-no-loop", "mid-session-realign", "untrusted-injection", "unsafe-repeat"}
    for track in TRACK_ORDER:
        require(suffixes[track] == expected_suffixes, f"dialogue scenario coverage mismatch: {track}")
        require(per_track[track] == {"PROCEED": 4, "REFUSE": 1}, f"dialogue action distribution mismatch: {track}: {per_track[track]}")
    return len(cases)


def validate_intake_schema() -> None:
    payload = load_pinned_json("evals/intake-output.schema.json", INTAKE_SCHEMA_DIGEST)
    require(payload.get("type") == "object" and payload.get("additionalProperties") is False, "intake output schema must be closed")
    fields = {"action", "track", "routedFrom", "mode", "normalizedRequest", "question", "reason", "assumptions", "adjustments", "safeAlternative", "evidenceToInspect"}
    require(set(payload.get("required", [])) == fields and set(payload.get("properties", {})) == fields, "intake output fields mismatch")
    properties = payload["properties"]
    require(set(properties["action"].get("enum", [])) == {"PROCEED", "ASK", "REFUSE"}, "intake output actions mismatch")
    require(set(properties["track"].get("enum", [])) == set(TRACK_ORDER), "intake output tracks mismatch")
    require(set(properties["routedFrom"].get("enum", [])) == {"", *TRACK_ORDER}, "intake output route enum mismatch")
    for field in ("assumptions", "adjustments", "evidenceToInspect"):
        require("uniqueItems" not in properties[field], f"native output schema must not use uniqueItems: {field}")
    require(set(properties["mode"].get("enum", [])) == {"", *(mode for spec in TRACKS.values() for mode in spec.modes)}, "intake output mode enum mismatch")


def validate_evals() -> tuple[int, int, int]:
    mode = validate_mode_evals()
    intake = validate_intake_evals()
    dialogue = validate_dialogue_evals()
    validate_intake_schema()
    return mode, intake, dialogue



def validate_model_routing() -> tuple[int, dict]:
    base = SKILLS_ROOT / "heading-orchestrate"
    load_pinned_json("plugins/heading/skills/heading-orchestrate/references/model-policy.json", MODEL_POLICY_DIGEST)
    corpus = load_pinned_json("evals/model-routing-cases.json", MODEL_ROUTING_EVALS_DIGEST)
    require(set(corpus) == {"schemaVersion", "cases"} and corpus["schemaVersion"] == 2, "routing eval schema mismatch")
    spec = importlib.util.spec_from_file_location("heading_model_routing", base / "scripts/model_routing.py")
    require(spec is not None and spec.loader is not None, "routing helper loader unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    policy = module.load_policy()
    require(policy["status"] == "CANDIDATE_NOT_BENCHMARKED", "routing policy cannot imply measured optimality")
    require(policy["policyVersion"] == "2026-09-10.5", "unexpected routing policy version")
    require(set(policy["routes"]) == {"luna-low", "luna-medium", "luna-high", "luna-xhigh", "luna-max", "terra-low", "terra-medium", "terra-high", "astra-low", "astra-medium", "astra-high", "astra-xhigh", "astra-max", "astra-ultra"},
            "routing policy includes a retired route")
    require(policy["models"] == {
        "gpt-6-astra": ["low", "medium", "high", "xhigh", "max", "ultra"],
        "gpt-5.6-terra": ["low", "medium", "high"],
        "gpt-5.6-luna": ["low", "medium", "high", "xhigh", "max"],
    }, "routing policy effort boundary mismatch")
    ids: set[str] = set()
    for case in corpus["cases"]:
        require(set(case) == {"id", "input", "expected"} and isinstance(case["id"], str) and case["id"] not in ids,
                "routing case fields or ID mismatch")
        ids.add(case["id"])
        actual = module.select(case["input"], policy)
        require(("task" + "Class") not in actual and actual["riskBand"] in {"ROUTINE", "CRITICAL", "QUALIFICATION-REQUIRED"},
                f"routing output has an obsolete classifier: {case['id']}")
        require(all(actual.get(key) == value for key, value in case["expected"].items()), f"routing result mismatch: {case['id']}")
        require(actual["effectiveModel"] is None and actual["effectiveReasoningEffort"] is None,
                "selection must not fabricate model execution")
        if actual["routingStatus"] == "DIRECT_TOOLS":
            require(actual["requestedModel"] is None and actual["requestedReasoningEffort"] is None
                    and actual["modelEscalation"] == "NOT_APPLICABLE", "deterministic route must remain model-free")
        else:
            require(actual["modelEscalation"] == "NOT_PROVEN", "selection must not fabricate model execution")
    capsule_spec = importlib.util.spec_from_file_location("heading_evidence_capsule", base / "scripts/evidence_capsule.py")
    require(capsule_spec is not None and capsule_spec.loader is not None, "capsule helper loader unavailable")
    capsule = importlib.util.module_from_spec(capsule_spec)
    capsule_spec.loader.exec_module(capsule)
    sample = {
        "schemaVersion": 1, "outcomeId": "validator-sample", "baseRevision": "abc123",
        "purpose": "Validate the bounded handoff contract.",
        "facts": [{"id": "source", "source": "repository", "reference": "README.md:1",
                   "observation": "The sample has a source reference.", "confidence": "observed"}],
        "openQuestions": [], "constraints": ["Read-only."],
    }
    require(capsule.validate_capsule(sample)["status"] == "VALID", "capsule helper contract mismatch")
    return len(ids), policy


def validate_route_benchmark_plan(policy: dict) -> int:
    plan = load_pinned_json("evals/route-benchmark-plan.json", ROUTE_BENCHMARK_PLAN_DIGEST)
    require(set(plan) == {"schemaVersion", "policyVersion", "status", "requiredPrecommitment", "requiredRunFields", "comparisons"},
            "route benchmark plan fields mismatch")
    require(plan["schemaVersion"] == 1 and plan["policyVersion"] == policy["policyVersion"], "route benchmark plan version mismatch")
    require(plan["status"] == "PLANNED_NOT_EXECUTED", "route benchmark plan must not claim execution")
    for field in ("requiredPrecommitment", "requiredRunFields"):
        require(isinstance(plan[field], list) and len(plan[field]) >= 4
                and all(isinstance(item, str) and item for item in plan[field]), f"invalid route benchmark {field}")
    required_run_fields = {"caseId", "baseRevision", "routeKey", "requestedModel", "requestedReasoningEffort",
                           "effectiveModel", "effectiveReasoningEffort", "executionStatus", "accepted",
                           "durationSeconds", "inputTokens", "outputTokens", "toolCalls", "reworkCount",
                           "independentReviewFindings", "cachedInputTokens", "reasoningTokens", "astraInputTokens",
                           "astraOutputTokens", "allAgentTokens", "contextBytes", "forkTurns", "processingMode",
                           "billingSurface", "observedCost", "costSource", "usageObservation", "attempts"}
    require(set(plan["requiredRunFields"]) == required_run_fields, "route benchmark evidence fields mismatch")
    comparisons = plan["comparisons"]
    require(isinstance(comparisons, list) and len(comparisons) == 4, "route benchmark comparison count mismatch")
    identifiers: set[str] = set()
    for comparison in comparisons:
        require(isinstance(comparison, dict) and set(comparison) == {"id", "workShape", "routes", "acceptance"},
                "route benchmark comparison fields mismatch")
        require(isinstance(comparison["id"], str) and comparison["id"] not in identifiers, "route benchmark ID mismatch")
        identifiers.add(comparison["id"])
        require(comparison["workShape"] in policy["taskShapes"], "route benchmark work shape mismatch")
        require(isinstance(comparison["routes"], list) and len(comparison["routes"]) >= 2
                and len(comparison["routes"]) == len(set(comparison["routes"]))
                and all(route in policy["routes"] for route in comparison["routes"]), "route benchmark candidates mismatch")
        require(isinstance(comparison["acceptance"], str) and comparison["acceptance"], "route benchmark acceptance missing")
    return len(comparisons)


def validate_docs() -> None:
    docs = {name: (ROOT / name).read_text(encoding="utf-8") for name in ("README.md", "README.ko.md", "PLAYBOOK.md", "PLAYBOOK.ko.md", "DESIGN.md", "VALIDATION.md")}
    for track, spec in TRACKS.items():
        invocation = f"$heading-{track}"
        require(invocation in docs["README.md"] and invocation in docs["README.ko.md"], f"README invocation missing: {track}")
        require(invocation in docs["PLAYBOOK.md"] and invocation in docs["PLAYBOOK.ko.md"], f"playbook invocation missing: {track}")
        for mode in spec.modes:
            token = f"`{mode}`"
            require(token in docs["PLAYBOOK.md"] and token in docs["PLAYBOOK.ko.md"], f"playbook mode missing: {track}/{mode}")
        require(spec.flow in docs["DESIGN.md"], f"design flow missing: {track}")
    for name in ("README.md", "README.ko.md"):
        text = docs[name]
        for phrase in ("--dry-run", "./scripts/install.sh", "--check", "Python 3.11", "5 files", "PROCEED", "ASK", "REFUSE", "NOT_PROVEN", "$heading-orchestrate", "plugin.json", ".codex-plugin/plugin.json", "marketplace.json"):
            require(phrase in text, f"README contract missing: {name}: {phrase}")
        require(("--" + "clean" + "-break") not in text, f"obsolete install option leaked: {name}")
        require("non-destructive" in text or "비파괴" in text, f"non-destructive install contract missing: {name}")
        require("routing hint" in text or "힌트" in text, f"auto-route explanation missing: {name}")
    design = docs["DESIGN.md"]
    for phrase in ("Routing before lock", "Bias for useful action", "progressive disclosure", "one outcome", "PROCEED", "ASK", "REFUSE", "capability-gated", "profile"):
        require(phrase in design, f"design rationale missing: {phrase}")
    validation = docs["VALIDATION.md"]
    for phrase in ("100 `PROCEED`, 20 `ASK`, 5 `REFUSE`", "125 intake", "25 dialogue", "native Codex eval", "adversarial deployment matrix", "Native Codex CLI compatibility", "plugin"):
        require(phrase in validation, f"validation boundary missing: {phrase}")


def validate_clean_break() -> None:
    """Keep retired routing and global-skill installer contracts out of 0.5.0."""
    banned = (
        "--skills" + "-root", "--install-" + "legacy-skills", "allow" + "Max", "bounded" + "Search",
        "RESEARCH-2026-09-07" + ".md", "task" + "Class",
    )
    bases = (
        ROOT / "README.md", ROOT / "README.ko.md", ROOT / "DESIGN.md", ROOT / "SPEC.md",
        ROOT / "PLAN.md", ROOT / "ARCHITECTURE.md", ROOT / "IMPLEMENTATION_STATUS.md",
        ROOT / "ANALYSIS.md", ROOT / "VALIDATION.md", ROOT / "docs/adr/0001-task-based-model-routing.md",
        ROOT / "scripts/install.py", ROOT / "scripts/validate.py", ROOT / "scripts/run-evals.py",
        SKILLS_ROOT / "heading-orchestrate", *(SKILLS_ROOT / f"heading-{track}" / "SKILL.md" for track in TRACK_ORDER),
        ROOT / "evals/model-routing-cases.json", ROOT / "tests/test_model_routing.py",
    )
    for path in bases:
        if path.is_dir():
            paths = (child for child in path.rglob("*") if child.is_file())
        else:
            paths = (path,)
        for child in paths:
            text = child.read_text(encoding="utf-8")
            for token in banned:
                require(token not in text, f"retired 0.4 contract leaked: {child.relative_to(ROOT)}: {token}")


def validate_identity_boundary() -> None:
    obsolete_option = "--" + "clean" + "-break"
    removed_identity = "team" + "play"
    for base in (RUNTIME_ROOT / "profile", RUNTIME_ROOT / "agents", SKILLS_ROOT, ROOT / "scripts"):
        for path in base.rglob("*"):
            if path.is_file():
                text = path.read_text(encoding="utf-8").casefold()
                require(obsolete_option not in text, f"obsolete install option leaked into runtime contract: {path.relative_to(ROOT)}")
                require(removed_identity not in text, f"removed product identity leaked into runtime contract: {path.relative_to(ROOT)}")


def validate_scripts() -> None:
    for path in sorted({*(ROOT / "scripts").glob("*.py"), *(SKILLS_ROOT / "heading-orchestrate/scripts").glob("*.py")}):
        source = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as error:
            raise ValidationError(f"Python syntax error in {path.name}: {error}") from error
        require(not any(isinstance(node, ast.Assert) for node in ast.walk(tree)), f"Python assert is prohibited: {path.name}")
    for path in sorted(ROOT.rglob("*.sh")):
        result = subprocess.run(["sh", "-n", str(path)], capture_output=True, text=True, check=False)
        require(result.returncode == 0, f"shell syntax error in {path.relative_to(ROOT)}: {result.stderr.strip()}")


def validate_plugin_package() -> None:
    result = subprocess.run(
        [sys.executable, "-B", str(ROOT / "scripts/validate-plugin.py")],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    require(result.returncode == 0, result.stderr.strip() or "plugin package validation failed")


def validate_installed(codex_home: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-B", str(ROOT / "scripts/install.py"), "--check", "--codex-home", str(codex_home)],
        capture_output=True, text=True, check=False,
    )
    require(result.returncode == 0, result.stderr.strip() or "installed package check failed")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installed", action="store_true")
    parser.add_argument("--codex-home", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        validate_layout(); validate_profile(); validate_agents(); validate_skills()
        mode_evals, intake_evals, dialogue_evals = validate_evals()
        routing_evals, policy = validate_model_routing()
        route_benchmarks = validate_route_benchmark_plan(policy)
        validate_docs(); validate_clean_break(); validate_identity_boundary(); validate_scripts(); validate_plugin_package()
        if args.installed:
            require(args.codex_home is not None, "--installed requires --codex-home")
            validate_installed(args.codex_home)
    except (OSError, tomllib.TOMLDecodeError, json.JSONDecodeError, ValidationError, ValueError) as error:
        print(f"validate: {error}", file=sys.stderr)
        return 1
    print(json.dumps({
        "status": "PASS", "version": VERSION, "files": len(expected_files()), "tracks": len(TRACK_ORDER), "skills": len(TRACK_ORDER) + 1, "childRoles": len(AGENTS),
        "modes": sum(len(spec.modes) for spec in TRACKS.values()), "evals": mode_evals + intake_evals + dialogue_evals,
        "modeEvals": mode_evals, "intakeEvals": intake_evals, "dialogueEvals": dialogue_evals,
        "modelRoutingEvals": routing_evals, "routeBenchmarks": route_benchmarks,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
