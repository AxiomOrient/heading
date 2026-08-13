# Heading 0.3.1 validation

## Verified

- Source validator: PASS in normal mode and with `PYTHONOPTIMIZE=1`.
- Behavioral, deployment, and plugin packaging tests: **43/43 PASS** in 6 isolated batches for 0.3.1.
- Source and plugin validators passed for 0.3.1: 53 source files, five implicit product tracks, one explicit-only orchestration skill, four child-role templates, 27 modes, and 182 deterministic evaluation cases.
- Native Codex CLI 0.144.1 representative intake evaluation: prior five direct-track and five wrong-track cases executed in isolated read-only sessions; the initial 9/10 result exposed one missing route-correction field, and the repaired case passed on re-execution. This is historical 0.2.0 evidence, not native-model proof for 0.3.1.
- Five track contracts, 27 niche modes, and 5 wrong-track auto-routing boundaries.
- 125 intake cases: 100 `PROCEED`, 20 `ASK`, 5 `REFUSE`; this is test coverage, not a runtime quota.
- 25 dialogue cases: one-question completion, no clarification loop, in-place track correction, untrusted instructions, and repeated invalid goals.
- All 150 intake/dialogue reference results pass the deterministic grader.
- Invalid methods are repaired while legitimate goals continue; only five essentially deceptive or unauthorized goals are refused.
- JSON output schema, native command construction, isolated authentication staging, and secret non-disclosure tests pass.
- Historical native Executor smoke on Codex CLI 0.144.1: a real `collab spawn failed: no thread with id` was converted to `executorState: SPAWN_FAILED`, `releaseState: BLOCKED`, and `runtimeObserved: NOT_PROVEN`; no smoke file was created. Version 0.3.1 permits a declared direct writer for bounded work when delegation is unavailable, but requires independent review or `independentReview: NOT_PROVEN` for material results.
- Native user-facing response smoke on Codex CLI 0.144.1: the final answer used plain Korean, progressive disclosure, and emitted no YAML or JSON.
- The adversarial deployment matrix covers non-destructive collision handling, symlinks, hard links, special files, rollback, mode drift, locks, deep and Unicode paths, restrictive umask, low file-descriptor limits, and cross-filesystem `TMPDIR`.
- Plugin packaging validator: portable Agent Plugins manifest, Codex manifest, marketplace source containment, six immediate skill folders, and symlink rejection.
- Codex CLI plugin smoke: `scripts/smoke-plugin-install.py` uses a temporary `HOME` and `CODEX_HOME`, registers the repository marketplace, installs `heading@heading`, confirms `enabled: true`, and compares the two cached manifests with source. It does not claim model selection in a chat.

Run the same checks:

```bash
./verify-source-package.sh
python3 -B scripts/validate-plugin.py
python3 -B scripts/smoke-plugin-install.py --codex-bin /absolute/path/to/codex
python3 -B scripts/run-evals.py --dry-run
```

## native Codex eval

The native runner copies the packaged skill source into an isolated temporary skill scope and invokes Codex in an ephemeral read-only evaluation session. It validates skill behavior, not interactive plugin activation:

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

`[NOT_PROVEN]` Authenticated native-model evaluation and interactive implicit-selection E2E are not established by the deterministic suite or installation smoke. `scripts/run-evals.py --dry-run` proves only native command construction. A complete implicit-selection E2E requires a newly started interactive Codex CLI session or desktop chat with the plugin enabled; `codex exec` does not prove that activation surface. Native Codex CLI compatibility and representative model execution must be rechecked for every CLI release. Successful Sol/Luna/Terra spawning, effective effort, sandbox enforcement, direct-writer review behavior, Executor thread continuation, and stochastic model behavior for the full 150 cases remain separate evidence.

The static behavior suite and adversarial deployment tests prove package contracts and deterministic tooling. Native execution evidence is recorded separately by `scripts/run-evals.py`.
