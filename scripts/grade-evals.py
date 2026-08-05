#!/usr/bin/env python3
"""Grade Heading intake-eval JSON results without third-party dependencies."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TRACKS = ("prototype", "build", "sweep", "grow", "maintain")
ACTIONS = ("PROCEED", "ASK", "REFUSE")
MODES = {
    "prototype": {"desirability", "workflow", "feasibility", "viability", "generative-quality"},
    "build": {"product-slice", "library-api", "service", "adapter", "data-change", "delivery-infra"},
    "sweep": {"delete", "collapse", "refactor", "ui", "performance"},
    "grow": {"randomized", "sequential", "switchback", "holdout-rollout", "observational"},
    "maintain": {"incident", "defect", "security", "reliability-capacity", "planned-change", "data-repair"},
}
FIELDS = {
    "action",
    "track",
    "routedFrom",
    "mode",
    "normalizedRequest",
    "question",
    "reason",
    "assumptions",
    "adjustments",
    "safeAlternative",
    "evidenceToInspect",
}


@dataclass(frozen=True)
class Grade:
    identifier: str
    passed: bool
    errors: tuple[str, ...]


def _text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True).casefold()


def validate_shape(result: Any) -> list[str]:
    if not isinstance(result, dict):
        return ["result is not an object"]
    errors: list[str] = []
    actual = set(result)
    if actual != FIELDS:
        return [f"result fields mismatch: missing={sorted(FIELDS - actual)} extra={sorted(actual - FIELDS)}"]

    for field in ("action", "track", "routedFrom", "mode", "normalizedRequest", "question", "reason", "safeAlternative"):
        if not isinstance(result[field], str):
            errors.append(f"{field} must be a string")
    for field, maximum in (("assumptions", 5), ("adjustments", 5), ("evidenceToInspect", 8)):
        value = result[field]
        if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
            errors.append(f"{field} must be a list of non-empty strings")
        elif len(value) > maximum:
            errors.append(f"{field} exceeds {maximum} items")
        elif len(value) != len(set(value)):
            errors.append(f"{field} must not contain duplicate items")
    if errors:
        return errors

    if result["action"] not in ACTIONS:
        errors.append(f"unknown action: {result['action']}")
    if result["track"] not in TRACKS:
        errors.append(f"unknown track: {result['track']}")
    if result["routedFrom"] not in {"", *TRACKS}:
        errors.append(f"unknown routedFrom: {result['routedFrom']}")
    if result["mode"] and result["mode"] not in set().union(*MODES.values()):
        errors.append(f"unknown mode: {result['mode']}")
    if not result["reason"].strip():
        errors.append("reason is empty")
    return errors


def grade_result(case: dict[str, Any], result: Any) -> Grade:
    identifier = str(case.get("id", "<unknown>"))
    errors = validate_shape(result)
    if errors or not isinstance(result, dict):
        return Grade(identifier, False, tuple(errors))

    expected = case["expected"]
    if result["action"] != expected["action"]:
        errors.append(f"action: expected {expected['action']}, got {result['action']}")
    if result["track"] != expected["track"]:
        errors.append(f"track: expected {expected['track']}, got {result['track']}")
    if result["routedFrom"] != expected["routedFrom"]:
        errors.append(f"routedFrom: expected {expected['routedFrom']!r}, got {result['routedFrom']!r}")
    if result["mode"] != expected["mode"]:
        errors.append(f"mode: expected {expected['mode']!r}, got {result['mode']!r}")

    policy = expected["question"]
    question = result["question"].strip()
    if policy == "required":
        if not question:
            errors.append("one focused question is required")
        else:
            if "\n" in question or re.search(r"(^|\s)(?:[-*]|\d+[.)])\s", question):
                errors.append("question must not be a list or multi-part form")
            if question.count("?") > 1:
                errors.append("question contains more than one question mark")
    elif policy == "forbidden" and question:
        errors.append("question is forbidden for this case")

    action = result["action"]
    if action == "PROCEED":
        if not result["normalizedRequest"].strip():
            errors.append("PROCEED requires a normalizedRequest")
        if not result["mode"] or result["mode"] not in MODES[result["track"]]:
            errors.append("PROCEED requires a valid mode for the effective track")
        if result["safeAlternative"].strip():
            errors.append("PROCEED must not set safeAlternative")
        if result["routedFrom"] and result["routedFrom"] == result["track"]:
            errors.append("routedFrom must differ from the effective track")
        if result["routedFrom"] and not result["adjustments"]:
            errors.append("route correction must be surfaced in adjustments")
    elif action == "ASK":
        if not question:
            errors.append("ASK requires question")
        if result["routedFrom"]:
            errors.append("ASK must not route before the material ambiguity is resolved")
        if result["safeAlternative"].strip():
            errors.append("ASK must not set safeAlternative")
    elif action == "REFUSE":
        if not result["safeAlternative"].strip():
            errors.append("REFUSE requires a safeAlternative")
        if result["mode"]:
            errors.append("REFUSE must not set a mode")
        if result["routedFrom"]:
            errors.append("REFUSE must not route")

    corpus = _text(result)
    for token in expected["mustInclude"]:
        if token in FIELDS:
            value = result[token]
            if not value or (isinstance(value, str) and not value.strip()):
                errors.append(f"required field is empty: {token}")
        elif token.casefold() not in corpus:
            errors.append(f"required token missing: {token}")
    for token in expected["mustExclude"]:
        if token.casefold() in corpus:
            errors.append(f"forbidden token present: {token}")

    return Grade(identifier, not errors, tuple(errors))


def load_cases(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schemaVersion") != 1 or not isinstance(payload.get("cases"), list):
        raise ValueError(f"invalid cases file: {path}")
    return payload["cases"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", choices=("intake", "dialogue"), required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--case", action="append", default=[])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cases_path = ROOT / "evals" / ("intake_cases.json" if args.suite == "intake" else "dialogue_cases.json")
    cases = load_cases(cases_path)
    selected = set(args.case)
    if selected:
        cases = [case for case in cases if case["id"] in selected]
        missing = selected - {case["id"] for case in cases}
        if missing:
            print(f"grade: unknown cases: {sorted(missing)}", file=sys.stderr)
            return 2

    grades: list[Grade] = []
    for case in cases:
        path = args.results_dir / f"{case['id']}.json"
        if not path.is_file():
            grades.append(Grade(case["id"], False, (f"result missing: {path}",)))
            continue
        try:
            result = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            grades.append(Grade(case["id"], False, (f"invalid result: {error}",)))
            continue
        grades.append(grade_result(case, result))

    failures = [grade for grade in grades if not grade.passed]
    payload = {
        "status": "PASS" if not failures else "FAIL",
        "suite": args.suite,
        "cases": len(grades),
        "passed": len(grades) - len(failures),
        "failed": len(failures),
        "failures": [{"id": grade.identifier, "errors": list(grade.errors)} for grade in failures],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
