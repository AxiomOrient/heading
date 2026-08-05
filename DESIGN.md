# Heading 0.1.0 design

## Core model

Heading separates **product direction** from **execution roles**.

```text
Prototype  decide
Build      deliver
Sweep      subtract
Grow       measure impact
Maintain   control existing-system risk
```

```text
Lead       Sol high
Planner    Luna max, read-only
Executor   Luna max, sole writer
Reviewer   Terra high, read-only
Architect  Terra xhigh, read-only
```

## Routing before lock

The explicit skill is a routing hint. Intake performs three operations:

```text
INFER effective track
→ REPAIR invalid wording or method while preserving the valid goal
→ LOCK one track and one outcome
```

A clear mismatch is auto-routed in the same conversation. For a multi-stage request, Heading starts with the earliest unresolved decision or risk gate and queues later outcomes. A question is reserved for one unresolved choice that materially changes the outcome. One outcome never changes tracks after writing begins.

This follows GPT-5.6 guidance to state domain context, hard constraints, approval boundaries, and success criteria while relying on stronger intent inference rather than prescribing every internal step. It also follows clarification research that favors selective questions over either always asking or never asking.

## Bias for useful action

Intake has only three actions:

```text
PROCEED  default; includes route correction and method repair
ASK      one material question
REFUSE   essential goal has no safe, authorized, honest, useful form
```

`BLOCKED` is an execution result, not an intake choice. Missing native or external proof becomes `NOT_PROVEN` while other faithful work continues.

## Track protocols

```text
Prototype  FRAME -> SELECT -> PROBE -> OBSERVE -> DECIDE
Build      CLASSIFY -> CONTRACT -> SLICE -> PROVE -> RELEASE
Sweep      ORACLE -> CUT -> COMPARE -> KEEP_OR_REVERT
Grow       DESIGN -> INSTRUMENT -> SHIP -> ANALYZE -> DECIDE
Maintain   TRIAGE -> CONTAIN -> CHANGE -> RECOVER -> WATCH
```

Each track keeps its own modes, lock, proof, stop rule, and result schema in `references/METHOD.md`. This is progressive disclosure: short routing and authority rules stay in `SKILL.md`; detailed niche method is loaded only after selection.

## Concurrency and review

- One active writable outcome.
- Read-heavy discovery may run independently; write-heavy work is serialized.
- One outcome keeps the same Executor thread through accepted repair and re-verification.
- Lead delegates exactly one `heading_executor` only after locking `outcome_id`, owned surface, done condition, and evidence. A missing child thread ID never enters a wait.
- Waits are bounded and target one named child. Spawn, role/sandbox observation, or wait failure stops the outcome as `BLOCKED` with runtime proof `NOT_PROVEN`; no second writer is started.
- The Executor contract refuses a second writer and does not assume a version-sensitive global concurrency setting. Only Lead can integrate or claim `PASS`/`READY`.
- Reviewer sees the actual candidate and evidence, reports only to Lead, and never edits or directs Executor.
- Architect is used only when an ownership, state, security, concurrency, recovery, or public-contract boundary cannot be localized.

## Prompt contract

Every child receives only:

```text
Goal
Context
Owned surface
Constraints
Done
Evidence
```

This keeps prompts short while preserving authority, success, and evidence boundaries.

## Human-facing result

Method schemas and proof fields are decision inputs, not the default user interface. Response detail adapts to task complexity: simple work gets a short summary; complex, risky, or blocked work gets enough evidence and caveats to support a decision. Raw YAML/JSON, logs, routing fields, and long file lists appear only when requested or when exact evidence is material.

## Evaluation design

- 27 positive niche-mode cases.
- 5 wrong-track cases requiring automatic same-session routing.
- 125 single-turn intake cases across ordinary, vague, hostile, impossible, missing-environment, multilingual, typo, Unicode, and prompt-injection inputs.
- 25 dialogue cases covering one-question completion, no clarification loop, mid-conversation rerouting, untrusted instructions, and repeated invalid goals.

The static corpus verifies the contract and runner. Native Codex model behavior remains separate evidence and must be measured with `scripts/run-evals.py`.
