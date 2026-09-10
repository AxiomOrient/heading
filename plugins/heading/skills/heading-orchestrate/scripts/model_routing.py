#!/usr/bin/env python3
"""Select a Heading model request from observed task facts. Never dispatch a model."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

POLICY_PATH = Path(__file__).resolve().parent.parent / "references/model-policy.json"
INPUT_FIELDS = {
    "task", "history", "allowUltra", "ultraReason",
    "ultraBudgetAuthorized", "allowEvidenceScouts", "parallelism",
    "astraEffort", "specialistEffort", "effortReason", "effortEvidence", "maxBudgetAuthorized",
}
DEFAULTS = {
    "lead", "critical", "fixedExtraction",
    "readHeavyExploration", "broadExploration", "implementation", "decision",
}


class RoutingError(ValueError):
    """Malformed facts or policy, not an unavailable-model fallback."""


def require(value: bool, message: str) -> None:
    if not value:
        raise RoutingError(message)


def load_policy() -> dict[str, Any]:
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    require(policy["schemaVersion"] == 2, "unsupported policy schema")
    require(set(policy["defaults"]) == DEFAULTS, "policy defaults mismatch")
    require(isinstance(policy["taskShapes"], list) and set(policy["taskShapes"]) == {
        "deterministic", "fixed-extraction", "read-heavy-exploration", "implementation",
        "cross-boundary-decision", "unknown",
    }, "task shape policy mismatch")
    for key, route in policy["routes"].items():
        require(set(route) == {"model", "effort"}, f"route fields mismatch: {key}")
        require(route["model"] in policy["models"], f"unknown model: {key}")
        require(route["effort"] in policy["models"][route["model"]], f"unsupported effort: {key}")
    for key in (*policy["defaults"].values(), *policy["astraLadder"]):
        require(key in policy["routes"], f"unknown policy route: {key}")
    for model, efforts in policy["specialistEfforts"].items():
        require(model in policy["models"] and isinstance(efforts, list) and bool(efforts),
                "invalid specialist effort policy")
        require(all(effort in policy["models"][model] for effort in efforts),
                "unsupported specialist effort policy")
    require(type(policy["maxReasoningFailuresPerRoute"]) is int and policy["maxReasoningFailuresPerRoute"] > 0,
            "maxReasoningFailuresPerRoute must be a positive integer")
    require(type(policy["maxAutomaticReasoningEscalations"]) is int and policy["maxAutomaticReasoningEscalations"] > 0,
            "maxAutomaticReasoningEscalations must be a positive integer")
    require(isinstance(policy["facts"], dict) and set(policy["facts"]) == {"clarity", "scope", "oracle", "risk"},
            "task facts policy mismatch")
    return policy


def validate_pair(model: str, effort: str, policy: dict[str, Any]) -> None:
    """Native host IDs only; this policy is not an API effort catalog."""
    require(model in policy["models"], f"model is not in the verified policy: {model}")
    require(effort in policy["models"][model], f"unsupported effort for {model}: {effort}")


def validate_history(payload: dict[str, Any], policy: dict[str, Any]) -> tuple[list[dict[str, str]], dict[str, int]]:
    history = payload.get("history", [])
    require(isinstance(history, list), "history must be an array")
    counts: dict[str, int] = {}
    failure_kinds = {"reasoning", *policy["nonReasoningFailures"]}
    for entry in history:
        require(isinstance(entry, dict) and set(entry) == {"route", "failure", "evidence"},
                "history entry fields mismatch")
        require(isinstance(entry["route"], str) and entry["route"] in policy["routes"], "unknown history route")
        require(isinstance(entry["failure"], str) and entry["failure"] in failure_kinds, "invalid failure class")
        require(isinstance(entry["evidence"], str) and bool(entry["evidence"].strip()), "failure evidence required")
        if entry["failure"] == "reasoning":
            counts[entry["route"]] = counts.get(entry["route"], 0) + 1
            require(counts[entry["route"]] <= policy["maxReasoningFailuresPerRoute"], "per-route retry limit exceeded")
    return history, counts


def initial_route(task: dict[str, Any], *, shape: str, policy: dict[str, Any]) -> tuple[str | None, str, str]:
    critical = task["risk"] == "critical" or (task["risk"] == "material" and task["reversible"] is False)
    qualified_routine = task["clarity"] == "clear" and task["risk"] == "routine" and task["reversible"] is True
    risk_band = "critical" if critical else "routine" if qualified_routine else "qualification-required"
    if shape == "deterministic":
        return None, risk_band, "deterministic_preflight"
    if critical:
        return policy["defaults"]["critical"], risk_band, "critical_risk_requires_capability"
    if shape == "fixed-extraction" and qualified_routine and task["oracle"] == "strong":
        return policy["defaults"]["fixedExtraction"], risk_band, "shape:fixed_extraction"
    if shape == "read-heavy-exploration" and qualified_routine:
        if task["scope"] != "local" or task["oracle"] != "strong":
            return policy["defaults"]["broadExploration"], risk_band, "shape:broad_exploration"
        return policy["defaults"]["readHeavyExploration"], risk_band, "shape:read_heavy_exploration"
    if shape == "implementation" and qualified_routine and task["oracle"] == "strong":
        return policy["defaults"]["implementation"], risk_band, "shape:implementation"
    if shape in {"cross-boundary-decision", "unknown"}:
        return policy["defaults"]["decision"], risk_band, f"shape:{shape.replace('-', '_')}"
    return policy["defaults"]["decision"], risk_band, "shape_not_safe_for_specialist_route"


def select(payload: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    """Pure transition: task facts + failed-attempt evidence -> next request, no I/O."""
    require(isinstance(payload, dict), "input must be an object")
    require(set(payload) <= INPUT_FIELDS, "unknown input field")
    task = payload.get("task")
    require(isinstance(task, dict), "task must be an object")
    required_task_fields = {*policy["facts"], "reversible", "shape"}
    require(set(task) == required_task_fields, "task fields mismatch")
    for field, options in policy["facts"].items():
        require(isinstance(task[field], str) and task[field] in options, f"invalid task.{field}")
    require(task["reversible"] is None or type(task["reversible"]) is bool,
            "task.reversible must be boolean or null")
    shape = task["shape"]
    require(isinstance(shape, str) and shape in policy["taskShapes"], "invalid task.shape")
    for field in ("allowUltra", "ultraBudgetAuthorized", "allowEvidenceScouts", "maxBudgetAuthorized"):
        require(type(payload.get(field, False)) is bool, f"{field} must be boolean")
    parallelism = payload.get("parallelism", "none")
    require(isinstance(parallelism, str) and parallelism in {"none", "independent"},
            "parallelism must be none or independent")
    allow_scouts = payload.get("allowEvidenceScouts", False)
    require(not allow_scouts or shape == "read-heavy-exploration",
            "evidence scouts require an explicit read-heavy-exploration shape")
    require(parallelism != "independent" or allow_scouts,
            "independent parallelism requires evidence-scout authorization")
    allow_ultra = payload.get("allowUltra", False)
    ultra_reason = payload.get("ultraReason", "")
    require(isinstance(ultra_reason, str), "ultraReason must be text")
    require(not ultra_reason.strip() or allow_ultra, "ultraReason requires allowUltra")
    require(not payload.get("ultraBudgetAuthorized", False) or allow_ultra,
            "budget authorization requires allowUltra")
    require(not allow_ultra or bool(ultra_reason.strip()), "ultra requires an exceptional-task reason")
    require(not allow_ultra or payload.get("ultraBudgetAuthorized", False),
            "ultra requires explicit budget authorization")
    effort = payload.get("astraEffort")
    specialist_effort = payload.get("specialistEffort")
    effort_fields = {"astraEffort", "specialistEffort", "effortReason", "effortEvidence"}
    if effort_fields & set(payload):
        require(("astraEffort" in payload) != ("specialistEffort" in payload),
                "choose exactly one upfront effort target")
        require({"effortReason", "effortEvidence"} <= set(payload),
                "upfront effort requires effort, reason, and evidence")
        if "astraEffort" in payload:
            require(isinstance(effort, str) and effort in {"low", "medium", "high", "xhigh", "max"},
                    "invalid astraEffort")
        else:
            require(isinstance(specialist_effort, str) and specialist_effort in {"medium", "high", "xhigh", "max"},
                    "invalid specialistEffort")
        for field in ("effortReason", "effortEvidence"):
            require(isinstance(payload[field], str) and bool(payload[field].strip()), f"{field} required")
        require(not allow_ultra, "choose one upfront effort mechanism")
    require(not payload.get("maxBudgetAuthorized", False) or effort == "max",
            "max budget authorization requires astraEffort=max")
    require(effort != "max" or payload.get("maxBudgetAuthorized", False),
            "max requires explicit budget authorization")
    history, counts = validate_history(payload, policy)
    selected, risk_band, reason = initial_route(task, shape=shape, policy=policy)
    if selected is None:
        require(not history, "deterministic work cannot contain model failure history")
        require(not allow_ultra, "ultra does not apply to deterministic work")
        require(effort is None, "astraEffort does not apply to deterministic work")
        require(specialist_effort is None, "specialistEffort does not apply to deterministic work")
        return {
            "routingStatus": "DIRECT_TOOLS", "policyVersion": policy["policyVersion"],
            "riskBand": risk_band.upper(), "workShape": shape, "routeKey": "deterministic-tools",
            "requestedModel": None, "requestedReasoningEffort": None,
            "effectiveModel": None, "effectiveReasoningEffort": None,
            "modelEscalationReason": reason, "modelEscalation": "NOT_APPLICABLE",
            "executionMode": "DETERMINISTIC", "evidenceScoutCount": 0, "evidenceCapsuleRequired": False,
            "requestedForkTurns": None,
        }
    status = "REQUESTED"
    if history:
        last = history[-1]
        if last["failure"] in policy["nonReasoningFailures"]:
            selected = last["route"]
            status = "REPAIR_REQUIRED"
            reason = f"repair_{last['failure']};more_reasoning_is_not_a_fix"
        elif last["route"] in policy["astraLadder"]:
            ladder = policy["astraLadder"]
            floor = ladder.index(policy["defaults"]["critical"]) if risk_band == "critical" else 0
            next_index = max(ladder.index(last["route"]) + 1, floor)
            if next_index >= len(ladder):
                selected, status, reason = last["route"], "NEEDS_NEW_EVIDENCE", "reasoning_ladder_exhausted"
            else:
                selected, reason = ladder[next_index], "evidenced_reasoning_failure"
        elif risk_band == "critical":
            selected, reason = policy["defaults"]["critical"], "critical_risk_requires_capability"
        elif last["route"].startswith("luna-") and shape in {"fixed-extraction", "read-heavy-exploration"}:
            selected, reason = policy["defaults"]["broadExploration"], "bounded_extraction_failure_requires_terra"
        else:
            selected, reason = policy["defaults"]["decision"], "specialist_failure_requires_stronger_evidence"
    if status == "REQUESTED" and specialist_effort is not None:
        model = policy["routes"][selected]["model"]
        require(model in policy["specialistEfforts"], "specialistEffort cannot override an Astra route")
        require(specialist_effort in policy["specialistEfforts"][model],
                f"unsupported specialistEffort for {model}: {specialist_effort}")
        selected = f"{selected.split('-')[0]}-{specialist_effort}"
        reason = f"upfront_specialist:{payload['effortReason'].strip()};evidence:{payload['effortEvidence'].strip()}"
    if status == "REQUESTED" and effort is not None:
        ladder = policy["astraLadder"]
        requested = f"astra-{effort}"
        floor = ladder.index(selected) if selected in ladder else 0
        selected = ladder[max(floor, ladder.index(requested))]
        reason = f"upfront_judgment:{payload['effortReason'].strip()};evidence:{payload['effortEvidence'].strip()}"
    if status == "REQUESTED" and allow_ultra:
        selected, reason = "astra-ultra", f"exceptional_task:{ultra_reason.strip()}"
    if status == "REQUESTED":
        ladder = policy["astraLadder"]
        failed_astra = [ladder.index(key) for key in counts if key in ladder]
        if failed_astra:
            floor = max(failed_astra) + 1
            if floor >= len(ladder):
                selected, status, reason = ladder[-1], "NEEDS_NEW_EVIDENCE", "reasoning_ladder_exhausted"
            elif selected not in ladder or ladder.index(selected) < floor:
                selected, reason = ladder[floor], "preserve_strongest_failed_capability"
    if status == "REQUESTED":
        # Exhausted weaker tiers must not be revisited after an interleaved failure.
        if not selected.startswith("astra-") and any(key.startswith("terra-") for key in counts):
            selected, reason = policy["defaults"]["decision"], "preserve_strongest_failed_capability"
        if counts.get(selected, 0) >= policy["maxReasoningFailuresPerRoute"]:
            status, reason = "NEEDS_NEW_EVIDENCE", "selected_route_already_failed"
        elif len(counts) >= policy["maxAutomaticReasoningEscalations"] and effort is None and not allow_ultra:
            status, reason = "NEEDS_NEW_EVIDENCE", "automatic_escalation_budget_exhausted"
        elif selected == "astra-max" and effort != "max":
            status, reason = "NEEDS_NEW_EVIDENCE", "max_requires_task_reason_evidence_and_budget"
        elif policy["routes"][selected]["effort"] == "ultra" and not allow_ultra:
            status, reason = "NEEDS_NEW_EVIDENCE", "ultra_requires_exceptional_task_reason_and_budget"
    route = policy["routes"][selected]
    scout_count = (2 if parallelism == "independent" else 1) if (
        status == "REQUESTED" and shape == "read-heavy-exploration"
        and allow_scouts and risk_band == "routine" and not selected.startswith("astra-")
    ) else 0
    return {
        "routingStatus": status, "policyVersion": policy["policyVersion"],
        "riskBand": risk_band.upper(), "workShape": shape, "routeKey": selected,
        "requestedModel": route["model"], "requestedReasoningEffort": route["effort"],
        "effectiveModel": None, "effectiveReasoningEffort": None,
        "modelEscalationReason": reason, "modelEscalation": "NOT_PROVEN",
        "executionMode": "MODEL", "evidenceScoutCount": scout_count,
        "evidenceCapsuleRequired": shape == "read-heavy-exploration",
        "requestedForkTurns": "none" if status == "REQUESTED" else None,
    }


def observation_status(request: dict[str, Any], observation: dict[str, Any], *,
                       expected: dict[str, str]) -> str:
    """Compare host-sourced facts; this does not authenticate caller-provided evidence."""
    required = {"source", "taskId", "model", "effort", "role", "sandbox", "evidenceRef"}
    if (not isinstance(request, dict) or not isinstance(expected, dict)
            or set(expected) != {"taskId", "role", "sandbox"}
            or not all(isinstance(v, str) and v.strip() for v in expected.values())):
        return "NOT_PROVEN"
    if not isinstance(observation, dict) or not required <= set(observation):
        return "NOT_PROVEN"
    if observation["source"] != "host-metadata" or not all(isinstance(observation[k], str) and observation[k].strip() for k in required):
        return "NOT_PROVEN"
    if (request.get("routingStatus") != "REQUESTED"
            or observation["model"] != request.get("requestedModel")
            or observation["effort"] != request.get("requestedReasoningEffort")):
        return "NOT_PROVEN"
    if any(observation[key] != value for key, value in expected.items()):
        return "NOT_PROVEN"
    return "MATCHED_HOST_FIELDS"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Task facts JSON; defaults to stdin")
    args = parser.parse_args()
    try:
        raw = args.input.read_text(encoding="utf-8") if args.input else sys.stdin.read()
        result = select(json.loads(raw), load_policy())
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"model-routing: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
