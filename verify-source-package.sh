#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHONDONTWRITEBYTECODE=1 "$ROOT/scripts/validate.sh"
PYTHONOPTIMIZE=1 PYTHONDONTWRITEBYTECODE=1 "$ROOT/scripts/validate.sh"
PYTHONDONTWRITEBYTECODE=1 python3 -B "$ROOT/scripts/run-tests.py"
