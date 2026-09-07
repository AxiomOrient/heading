#!/usr/bin/env python3
"""Run Heading tests in isolated bounded batches."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_TESTS = 62


def flatten(suite: unittest.TestSuite) -> list[str]:
    values: list[str] = []
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            values.extend(flatten(test))
        else:
            values.append(test.id())
    return values


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--timeout", type=int, default=180)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.batch_size < 1 or args.timeout < 1:
        print("run-tests: batch size and timeout must be positive", file=sys.stderr)
        return 2
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(ROOT / "tests"),
        pattern="test_*.py",
        top_level_dir=str(ROOT),
    )
    identifiers = sorted(flatten(suite))
    if len(identifiers) != EXPECTED_TESTS or len(set(identifiers)) != len(identifiers):
        print(f"run-tests: expected {EXPECTED_TESTS} unique tests, found {len(identifiers)}", file=sys.stderr)
        return 2

    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    batches = [identifiers[index:index + args.batch_size] for index in range(0, len(identifiers), args.batch_size)]
    for index, batch in enumerate(batches, start=1):
        print(f"[batch {index}/{len(batches)}] {len(batch)} tests", flush=True)
        try:
            result = subprocess.run(
                [sys.executable, "-B", "-m", "unittest", "-v", *batch],
                cwd=ROOT,
                env=env,
                check=False,
                timeout=args.timeout,
            )
        except subprocess.TimeoutExpired:
            print(f"run-tests: batch {index} timed out", file=sys.stderr)
            return 1
        if result.returncode != 0:
            print(f"run-tests: batch {index} failed with exit {result.returncode}", file=sys.stderr)
            return result.returncode

    print(json.dumps({"status": "PASS", "tests": len(identifiers), "batches": len(batches)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
