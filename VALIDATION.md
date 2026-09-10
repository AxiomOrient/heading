# Heading 0.5.0 — validation record

Date: 2026-09-10. Scope: deterministic source package behavior and local filesystem/plugin adapter contracts. Native model behavior and actual host routing are separate evidence.

## Executed source checks — 2026-09-10

### Current policy 2026-09-10.5

The user-directed effort revision passed `./verify-source-package.sh`: all 63 tests in 8 batches, normal and optimized validators, 17 routing vectors, all 1,296 fact/shape combinations, and the unchanged 182 intake/mode/dialogue cases. The four added tests exercise all Luna high/xhigh/max and Terra medium/high specialist choices, Luna max without another budget approval, invalid mixtures/model downgrades, preserved repair/failure limits, legacy history, and the actual router CLI. Test output: `/tmp/heading-effort-check.log` for this session.

All six skill validators, the plugin validator, and `git diff --check` passed. Real isolated Codex install smoke and local reinstall passed at `0.5.0+codex.20260910035021`; all 27 installed plugin files matched the source. The existing optional profile was backed up and changed only from Luna low to Luna high for default children. The five-file runtime passed its installation check. No global config was edited. This verifies policy and installation, not effective per-model execution, first-pass model quality, or token savings. No additional model-quality benchmark or independent model review was performed for this focused revision.

Authenticated live host smokes then ran through the installed `heading@heading` plugin with `codex exec --sandbox read-only --ephemeral --json` and, after the profile repair, `codex exec --profile heading --sandbox read-only --ephemeral --json`, each with an explicit `$heading-sweep` request. The first run observed the installed skill auto-correcting the release-readiness request to `heading-maintain` and exited 0; thread id: `01a08978-d560-70c1-89a9-90e331438239`. The repaired profile then loaded with `[tools]`, GPT-5.6 Luna at low effort, and exited 0 after inspecting `VERSION` and `git status`; thread id: `01a08987-521d-7b52-ba33-d4dbe7f6dedc`. Both runs made no files, commits, tags, or network writes. Effective model/effort metadata and model-quality qualification remain `NOT_PROVEN`.

### Previous policy 2026-09-10.4

Policy `2026-09-10.4`: `./verify-source-package.sh` passed. Normal and optimized validators reported 69 files, 6 skills, 4 child roles, 17 routing vectors, 4 benchmark-plan groups, and the unchanged 182 intake/mode/dialogue contract cases. All 59 tests passed in 8 batches. Six skill-creator validators, the plugin-creator validator, the repository plugin validator, and `git diff --check` passed.

The run covered all 1,296 fact/shape combinations plus upfront high/xhigh selection, critical high floors, max budget requirements, refusal to disguise environment failures as reasoning failures, automatic retry limits, no return to a failed weaker tier, one/two-scout selection, and the optional profile defaults. Full test output was captured in `/tmp/heading-source-check.log` during this session.

A separate read-only forward-test exercised the actual router CLI on evidence retrieval, broad scans, implementation, recovery judgment, and failed-attempt/permission combinations. An initial ambiguity report was reassessed and withdrawn: `clarity` describes the question, not knowledge of the answer. That distinction is now explicit. No confirmed routing defect remained. The review requested Terra medium with no inherited conversation; its effective model was not independently attested, so this is behavioral evidence rather than routing-identity or model-quality proof.

The real Codex CLI isolated marketplace smoke passed with matching enabled cache manifests at `0.5.0+codex.20260910033840`. `codex plugin add heading@heading` then updated the user's existing local installation; CLI read-back confirmed enabled status and the local source. The installed skill files were compared with the source. The existing optional five-file Heading runtime was updated and passed `scripts/install.py --check --codex-home /Users/ax/.codex`. The non-destructive installer initially refused older role content; a backup and exact-content-checked migration changed only the old Heading routing clause and the Heading profile's agent defaults. It did not alter global `config.toml`.

The route benchmark plan remains `PLANNED_NOT_EXECUTED`. None of these checks demonstrates production model quality, a specific allowance saving, or actual model switching in this already-running task.

## Static corpus boundary

- 32 mode cases.
- 125 intake cases with 100 `PROCEED`, 20 `ASK`, 5 `REFUSE`.
- 25 dialogue cases.

These corpora validate the skill contract and intake evaluator shape. They are not 182 successful model executions.

## Deployment and package boundary

The adversarial deployment matrix covers explicit roots, symlink/hardlink rejection, content and mode drift, locks, rollback, hostile Unicode paths, and non-destructive checks. The plugin smoke test uses an isolated Codex home and simulated command adapter when a real host is not intentionally invoked; it proves the adapter contract, not a public installation.

## Native Codex CLI compatibility

`NOT_PROVEN` until an authenticated host run records actual task ID, role, sandbox, requested/effective model and effort, candidate revision, and acceptance evidence. The native Codex eval installs the local plugin through an isolated marketplace before it evaluates intake. It preserves trace, stderr, exit/timeout/spawn status, and keeps requested fields separate from unobserved effective fields.

## Reproduction

```bash
./verify-source-package.sh
python3 -B scripts/validate-plugin.py
python3 -B scripts/smoke-plugin-install.py
python3 -B scripts/run-evals.py --dry-run --limit 1 --route terra-low
```

The source result does not prove native model dispatch, account availability, host support for Ultra, or benchmark optimality.
