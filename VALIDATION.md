# Heading 0.4.1 — validation record

Date: 2026-09-07. Scope: source package and deterministic behavior in this Linux/Python environment. Model quality and actual host routing are separate.

## 2026-09-08 policy revision verification

On macOS, policy `2026-09-08.1` was verified with the uninterrupted `./verify-source-package.sh`: both normal and optimized source validators passed, and all 65 tests passed in 9 batches with no skips. The separate plugin manifest validator and `git diff --check` passed. The 33 revised routing vectors and 216 task-fact combinations passed.

New regression checks cover exceptional ultra justification, separation from Luna max authorization, environment/permission/transient repair precedence, exhaustion preservation, and rejection of retired Astra high/xhigh/max routes in history and native eval arguments. Astra normally requests low/medium; ultra is a reasoned, budgeted native-host exception. No authenticated model execution, live ultra support, benchmark optimality or installed-cache refresh was verified in this revision. The earlier record below describes the September 7 run.

## Executed source checks

| Check | Observed result |
| --- | --- |
| Source validator, Python normal | PASS: 66 files, 6 skills, 4 child roles |
| Source validator, PYTHONOPTIMIZE=1 | PASS |
| Portable/Codex plugin manifest validator | PASS |
| Python syntax / shell syntax / production assert prohibition | PASS through source validator |
| Unittest suite | 62 discovered; 61 passed; 1 macOS-only skip; 0 failures/errors |
| Routing vectors | 33/33 passed |
| Exhaustive supported task facts | 216/216 passed |
| Non-destructive fresh install / check / drift rejection | PASS in isolated temporary roots |
| Actual local subprocess exit / timeout evidence | PASS; not a model execution |
| Native smoke / native model eval | NOT_PROVEN: both exit 2, Codex CLI not found |
| Working-tree whitespace validation | git diff --check passed |

The convenience full-suite command exceeded this tool's execution window. All 62 tests were then observed in four bounded slices (0–16, 16–24, 24–44, 44–62); no test was omitted. This is not a claim that the uninterrupted convenience command completed here. Linux skipped only `test_macos_system_aliases_are_canonicalized_but_custom_symlinks_remain_unsafe`.


The retained adversarial deployment matrix covers non-destructive install, symlink/hardlink rejection, managed-content drift, namespace conflicts, permissions, locks, rollback, hostile paths and explicit roots. Tests that use simulated plugin commands verify adapter contracts only; they do not prove a real Codex plugin installation.

The original corpus remains 32 mode cases, 125 intake cases and 25 dialogue cases: 182 contract cases. The intake distribution is 100 `PROCEED`, 20 `ASK`, 5 `REFUSE`. These corpora are structurally/semantically validated, not 182 successful LLM runs.

New routing verification: 33 reviewed request/transition vectors, all 216 supported fact combinations, malformed-input rejection, max authorization, critical-risk floor, failed-route history preservation, environmental-failure handling, requested/observed separation and locked task/role/sandbox matching. The helper runs locally without calling a model.

## Native Codex CLI compatibility

NOT_PROVEN. No Codex CLI is installed in this execution environment. Official-source compatibility is documented, but no authenticated model execution, live role dispatch, account availability, in-place effort switch or stopped-writer handover is claimed. The macOS-specific filesystem-alias test requires macOS and is separately skipped on Linux.

`scripts/run-evals.py --route ... --dry-run` proves command construction, not invocation or model adherence. A native Codex eval requires an actual CLI and explicit credentials. The runner evaluates intake only, retains raw trace and records requested model/effort separately from unobserved effective values. Real execution failures must remain failures, even if a partial result JSON exists.

## Reproduction

```bash
./verify-source-package.sh
python3 -B scripts/validate-plugin.py
python3 -B scripts/run-evals.py --dry-run --limit 1 --route astra-low
```

A successful source check is not proof that Astra low and Luna xhigh/max are the fastest, cheapest or most accurate settings. The policy remains CANDIDATE_NOT_BENCHMARKED until the outcome comparisons in PLAN.md are observed.
