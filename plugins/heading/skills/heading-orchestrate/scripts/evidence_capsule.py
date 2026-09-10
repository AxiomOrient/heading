#!/usr/bin/env python3
"""Validate a bounded Heading evidence capsule. Never dispatch work or a model."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

SCHEMA_VERSION = 1
SOURCES = {"repository", "primary-web", "runtime"}
CONFIDENCE = {"observed", "inferred"}
CAPSULE_FIELDS = {"schemaVersion", "outcomeId", "baseRevision", "purpose", "facts", "openQuestions", "constraints"}
FACT_FIELDS = {"id", "source", "reference", "observation", "confidence"}


class CapsuleError(ValueError):
    """A capsule is malformed or exceeds its bounded handoff contract."""


def require(value: bool, message: str) -> None:
    if not value:
        raise CapsuleError(message)


def text(value: object, label: str, *, limit: int) -> str:
    require(isinstance(value, str) and value.strip() == value and bool(value), f"{label} must be non-empty text")
    require("\n" not in value and "\r" not in value and len(value) <= limit, f"{label} exceeds its bounded format")
    return value


def text_list(value: object, label: str, *, limit: int, item_limit: int) -> list[str]:
    require(isinstance(value, list) and len(value) <= limit, f"{label} must be a bounded array")
    result = [text(item, f"{label} item", limit=item_limit) for item in value]
    require(len(result) == len(set(result)), f"{label} items must be distinct")
    return result


def validate_capsule(payload: object) -> dict[str, Any]:
    require(isinstance(payload, dict) and set(payload) == CAPSULE_FIELDS, "capsule fields mismatch")
    require(payload["schemaVersion"] == SCHEMA_VERSION, "unsupported capsule schema")
    outcome_id = text(payload["outcomeId"], "outcomeId", limit=96)
    require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,95}", outcome_id) is not None, "outcomeId format mismatch")
    base_revision = text(payload["baseRevision"], "baseRevision", limit=128)
    require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/@-]{0,127}", base_revision) is not None,
            "baseRevision format mismatch")
    text(payload["purpose"], "purpose", limit=280)
    facts = payload["facts"]
    require(isinstance(facts, list) and 1 <= len(facts) <= 12, "facts must contain one to twelve items")
    identifiers: set[str] = set()
    for fact in facts:
        require(isinstance(fact, dict) and set(fact) == FACT_FIELDS, "fact fields mismatch")
        identifier = text(fact["id"], "fact.id", limit=64)
        require(re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", identifier) is not None and identifier not in identifiers,
                "fact.id must be a unique lowercase identifier")
        identifiers.add(identifier)
        require(fact["source"] in SOURCES, "invalid fact.source")
        text(fact["reference"], "fact.reference", limit=512)
        text(fact["observation"], "fact.observation", limit=1000)
        require(fact["confidence"] in CONFIDENCE, "invalid fact.confidence")
    open_questions = text_list(payload["openQuestions"], "openQuestions", limit=8, item_limit=280)
    constraints = text_list(payload["constraints"], "constraints", limit=8, item_limit=280)
    return {
        "status": "VALID", "schemaVersion": SCHEMA_VERSION, "outcomeId": outcome_id,
        "baseRevision": base_revision, "facts": len(facts),
        "openQuestions": len(open_questions), "constraints": len(constraints),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Capsule JSON; defaults to stdin")
    args = parser.parse_args()
    try:
        raw = args.input.read_text(encoding="utf-8") if args.input else sys.stdin.read()
        result = validate_capsule(json.loads(raw))
    except (OSError, ValueError, TypeError) as error:
        print(f"evidence-capsule: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
