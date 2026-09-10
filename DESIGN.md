# Heading 0.5.0 design

## Core model

Heading separates **product direction** from **execution roles** and from the **distribution package**.

```text
Prototype  decide
Build      deliver
Sweep      subtract
Grow       measure impact
Maintain   control existing-system risk
```

```text
Lead       routing, lock, integration and final acceptance
Planner    bounded read-only discovery
Executor   sole delegated writer
Reviewer   independent read-only candidate review
Architect  irreducible read-only boundary analysis
```

Task capability is orthogonal: deterministic preflight -> direct tools; fixed extraction -> Luna high; bounded evidence -> Luna high; broad/weak-oracle evidence -> Terra medium; clear implementation -> Terra medium; cross-boundary/unknown -> Astra low; critical -> Astra high. Astra ultra is an exceptional native-host route with a task-specific reason and explicit budget authorization. Every task must declare its work shape and satisfy the closed packet schema. The versioned `model-policy.json` is the routing-value owner; `MODEL-ROUTING.md` owns meaning and `EVIDENCE-CAPSULE.md` owns research handoff. These defaults are candidates, not measured quality equivalence.

The product tracks are six portable skill folders under `plugins/heading/skills/`. `plugins/heading/plugin.json` is the portable Agent Plugins manifest, while `.codex-plugin/plugin.json` is the Codex host manifest. The separate `runtime/heading/profile/heading.config.toml` file is an optional task-stage profile; it does not define package distribution.

## Routing before lock

The explicit skill is a routing hint. Intake performs three operations:

```text
INFER effective track
→ REPAIR invalid wording or method while preserving the valid goal
→ LOCK one track and one outcome
```

A clear mismatch is auto-routed in the same conversation. For a multi-stage request, Heading starts with the earliest unresolved decision or risk gate and queues later outcomes. A question is reserved for one unresolved choice that materially changes the outcome. One outcome never changes tracks after writing begins.

The dated official-source analysis is in `RESEARCH-2026-09-10.md`. Astra-specific guidance is translated into authorized reversible completion, material questions only, concise evidence and selective delegation—not weaker authority boundaries or hidden reasoning requirements.

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

## Capability-gated concurrency and review

- One active writable outcome.
- Read-heavy discovery may run independently; write-heavy work is serialized.
- One outcome keeps the same Executor thread where the route can be honored; otherwise an observed stopped-writer handover preserves the exact candidate and evidence.
- Lead locks `outcome_id`, owned surface, done condition, and evidence before any writable work. When a native executor is available and allowed, it delegates exactly one `heading_executor`; a missing child thread ID never enters a wait.
- If delegation is unavailable, disallowed, or disproportionate for a small local change, Lead declares `executionMode: DIRECT`, remains the sole writer, and preserves the same ownership and evidence lock. A requested but unobservable native or user-visible lane remains `NOT_PROVEN` or `BLOCKED`; it is never silently replaced.
- Waits are bounded and target one named child. A timeout or missing notification is not proof of failure; inspect the same writer's state before deciding recovery or replacement.
- The Executor contract refuses a second writer and does not assume a version-sensitive global concurrency setting. A direct writer cannot self-certify material work; only Lead makes final claims.
- Reviewer sees the actual candidate and evidence, reports only to Lead, and never edits or directs Executor.
- Architect is used only when an ownership, state, security, concurrency, recovery, or public-contract boundary cannot be localized.
- `$heading-orchestrate` runs only after a track locks an outcome. It selects a direct lane, an observed native lane, or an explicitly authorized user-visible task lane.
- Native role templates are intent, not runtime proof. Identity, model/effort, write boundary, task ID, and completion must be observed before a delegated result can support acceptance.
- Task facts, not role names, select model capability. Explicit dispatch supplies model and effort together. Custom role files omit both values to avoid overriding the requested route. Host observations alone establish effective values. Missing proof does not authorize an unverified weaker route for material work. A model change preserves the locked outcome, role, permissions and reviewer independence.
- There is no capability-gated fallback: an unavailable requested lane is `NOT_PROVEN` or `BLOCKED`; direct work is a separately stated lane rather than an invisible replacement.

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

## Deterministic route selection versus runtime proof

`model_routing.py` is a pure transition behind a small JSON CLI, not a dispatcher. Missing or omitted work shape is rejected. Deterministic work returns `DIRECT_TOOLS` with no model request. Critical or irreversible material-risk work has a higher effort floor. Environment and permission failures enter `REPAIR_REQUIRED`; they are not reasons to spend more reasoning. Failed higher-capability history cannot silently downgrade to a lower route.

The native intake runner accepts `--route` and emits both CLI settings. It records duration, exit/timeout/spawn status and retained output without copying requested values into effective values. The current route benchmark plan is explicitly unexecuted. A successful intake evaluation is not a complex implementation benchmark. Production routing needs actual host metadata and independent final-state evidence.
