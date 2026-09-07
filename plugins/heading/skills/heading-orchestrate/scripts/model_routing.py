#!/usr/bin/env python3
"""Select a Heading model request from observed task facts. Never dispatch a model."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

POLICY_PATH = Path(__file__).resolve().parent.parent / "references/model-policy.json"


class RoutingError(ValueError):
    """Malformed facts or policy, not an unavailable-model fallback."""


def require(value: bool, message: str) -> None:
    if not value:
        raise RoutingError(message)


def load_policy() -> dict[str, Any]:
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    require(policy["schemaVersion"] == 1, "unsupported policy schema")
    for key, route in policy["routes"].items():
        require(route["model"] in policy["models"], f"unknown model: {key}")
        require(route["effort"] in policy["models"][route["model"]], f"unsupported effort: {key}")
    for key in (*policy["defaults"].values(), *policy["astraLadder"], policy["lunaRetry"]):
        require(key in policy["routes"], f"unknown policy route: {key}")
    require(type(policy["maxReasoningFailuresPerRoute"]) is int and policy["maxReasoningFailuresPerRoute"] > 0,
            "maxReasoningFailuresPerRoute must be a positive integer")
    return policy


def validate_pair(model: str, effort: str, policy: dict[str, Any]) -> None:
    """API/CLI IDs only. A UI label is never silently used as an API value."""
    require(model in policy["models"], f"model is not in the verified policy: {model}")
    require(effort in policy["models"][model], f"unsupported effort for {model}: {effort}")


def select(payload: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    """Pure transition: task facts + failed-attempt evidence -> next request, no I/O."""
    require(isinstance(payload, dict), "input must be an object")
    require(set(payload) <= {"task", "history", "allowMax", "boundedSearch"}, "unknown input field")
    task = payload.get("task")
    require(isinstance(task, dict), "task must be an object")
    require(set(task) == {*policy["facts"], "reversible"}, "task fields mismatch")
    for field, options in policy["facts"].items():
        require(isinstance(task[field], str) and task[field] in options, f"invalid task.{field}")
    require(task["reversible"] is None or type(task["reversible"]) is bool,
            "task.reversible must be boolean or null")
    for field in ("allowMax", "boundedSearch"):
        require(type(payload.get(field, False)) is bool, f"{field} must be boolean")
    allow_max = payload.get("allowMax", False)
    bounded = payload.get("boundedSearch", False)
    easy = (task["clarity"] == "clear" and task["scope"] == "local"
            and task["reversible"] is True and task["oracle"] == "strong"
            and task["risk"] == "routine")
    critical = task["risk"] == "critical" or (task["risk"] == "material" and task["reversible"] is False)
    task_class = "critical" if critical else "easy" if easy else "hard"
    selected = policy["defaults"][task_class]
    status = "REQUESTED"
    reason = f"task_class:{task_class}"
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
        # Environmental attempts do not spend the model-quality retry budget.
        if entry["failure"] == "reasoning":
            counts[entry["route"]] = counts.get(entry["route"], 0) + 1
            require(counts[entry["route"]] <= policy["maxReasoningFailuresPerRoute"], "per-route retry limit exceeded")
    if history:
        last = history[-1]
        if last["failure"] in policy["nonReasoningFailures"]:
            selected = last["route"]
            status = "REPAIR_REQUIRED"
            reason = f"repair_{last['failure']};more_reasoning_is_not_a_fix"
        elif last["route"] in policy["astraLadder"]:
            ladder = policy["astraLadder"]
            floor = ladder.index(policy["defaults"]["critical"]) if task_class == "critical" else 0
            next_index = max(ladder.index(last["route"]) + 1, floor)
            if next_index >= len(ladder):
                selected, status, reason = last["route"], "NEEDS_NEW_EVIDENCE", "reasoning_ladder_exhausted"
            else:
                selected, reason = ladder[next_index], "evidenced_reasoning_failure"
        elif task_class == "critical":
            selected, reason = policy["defaults"]["critical"], "critical_risk_requires_capability"
        elif easy and bounded and allow_max and last["route"] == policy["defaults"]["easy"]:
            selected, reason = policy["lunaRetry"], "bounded_search_with_reasoning_failure"
        else:
            selected, reason = policy["defaults"]["hard"], "luna_failure_or_task_no_longer_easy"
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
        # Never send a task back to an already failed setting or silently downgrade.
        if counts.get(selected, 0) >= policy["maxReasoningFailuresPerRoute"]:
            status, reason = "NEEDS_NEW_EVIDENCE", "selected_route_already_failed"
        elif policy["routes"][selected]["effort"] == "max" and not allow_max:
            status, reason = "NEEDS_NEW_EVIDENCE", "max_requires_explicit_budget"
    route = policy["routes"][selected]
    return {
        "routingStatus": status,
        "policyVersion": policy["policyVersion"],
        "taskClass": task_class.upper(),
        "routeKey": selected,
        "requestedModel": route["model"],
        "requestedReasoningEffort": route["effort"],
        "effectiveModel": None,
        "effectiveReasoningEffort": None,
        "modelEscalationReason": reason,
        "modelEscalation": "NOT_PROVEN",
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
    # Matching fields does not authenticate their origin or accept the product result.
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
