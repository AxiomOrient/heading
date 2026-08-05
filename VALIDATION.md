# Heading 0.1.0 validation

## Verified

- Source validator: PASS in normal mode and with `PYTHONOPTIMIZE=1`.
- Behavioral and deployment tests: **38/38 PASS** in 5 isolated batches.
- Native Codex CLI 0.144.1 representative intake evaluation: five direct-track and five wrong-track cases executed in isolated read-only sessions; the initial 9/10 result exposed one missing route-correction field, and the repaired case passed on re-execution.
- Five track contracts, 27 niche modes, and 5 wrong-track auto-routing boundaries.
- 125 intake cases: 100 `PROCEED`, 20 `ASK`, 5 `REFUSE`; this is test coverage, not a runtime quota.
- 25 dialogue cases: one-question completion, no clarification loop, in-place track correction, untrusted instructions, and repeated invalid goals.
- All 150 intake/dialogue reference results pass the deterministic grader.
- Invalid methods are repaired while legitimate goals continue; only five essentially deceptive or unauthorized goals are refused.
- JSON output schema, native command construction, isolated authentication staging, and secret non-disclosure tests pass.
- Native Executor smoke on Codex CLI 0.144.1: a real `collab spawn failed: no thread with id` was converted to `executorState: SPAWN_FAILED`, `releaseState: BLOCKED`, and `runtimeObserved: NOT_PROVEN`; no smoke file was created.
- Native user-facing response smoke on Codex CLI 0.144.1: the final answer used plain Korean, progressive disclosure, and emitted no YAML or JSON.
- The adversarial deployment matrix covers non-destructive collision handling, symlinks, hard links, special files, rollback, mode drift, locks, deep and Unicode paths, restrictive umask, low file-descriptor limits, and cross-filesystem `TMPDIR`.

Run the same checks:

```bash
./verify-source-package.sh
python3 -B scripts/run-evals.py --dry-run
```

## native Codex eval

The native runner installs Heading into an isolated home and invokes Codex in an ephemeral read-only evaluation session:

```bash
CODEX_API_KEY=<key> python3 -B scripts/run-evals.py --suite all
```

or:

```bash
python3 -B scripts/run-evals.py --suite all \
  --auth-file "${CODEX_HOME:-$HOME/.codex}/auth.json"
```

The authentication file is copied only into the temporary evaluation home with mode `0600` and is never printed.

## Evidence boundary

`[NOT_PROVEN]` Native Codex CLI compatibility and representative model execution must be rechecked for every CLI release. The Executor failure gate is runtime-verified, but successful Sol/Luna/Terra spawning, effective effort, sandbox enforcement, Executor thread continuation, and stochastic model behavior for the full 150 cases remain separate evidence.

The static behavior suite and adversarial deployment tests prove package contracts and deterministic tooling. Native execution evidence is recorded separately by `scripts/run-evals.py`.
