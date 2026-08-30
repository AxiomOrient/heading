# Heading orchestration contract

## Non-negotiable boundaries

- A task packet comes before delegation.
- There is exactly one writer for a file or interface boundary.
- Runtime identity, write boundary, and completion are observed facts, not template assumptions.
- A higher model tier may be explicitly requested for material risk, but the requested and effective model must be recorded.
- Native and user-visible task lanes are opt-in capabilities, not a quota.
- The primary agent owns acceptance and never treats an implementer report as acceptance.
- A missing tool or runtime fact reduces only that delegated proof to `NOT_PROVEN`; it never becomes a fabricated success.

## Task packet schema

| Field | Required content |
| --- | --- |
| Outcome | One user-visible result and its Heading track/mode. |
| Contract | Public interfaces, invariants, and non-goals. |
| Ownership | Writer, owned paths, base revision, and integration owner. |
| Proof | Commands, observations, failure paths, and acceptance threshold. |
| Runtime | Requested/effective model and reasoning effort, escalation reason, sandbox, and task identity. |
| Recovery | Rollback or stop condition where the change can affect users or data. |
| Report | Files changed, evidence, open risks, and result token. |

## Status meanings

- `PASS`: the locked proof passed and the primary agent accepted the candidate.
- `PARTIAL`: useful work completed, but a stated acceptance condition is incomplete.
- `NOT_PROVEN`: a required environment, tool, or observation was unavailable.
- `BLOCKED`: a material decision or safety condition prevents responsible continuation.

## Model tier escalation

- The default model ladder is `gpt-5.6-luna` -> `gpt-5.6-terra` -> `gpt-5.6-sol`; escalation is permitted only by an explicit Lead decision for material risk.
- Planner and Executor may request Luna `max` or move from Luna to Terra with `high`/`xhigh`; critical or irreversible risk may request Sol `high` directly. Reviewer (`high`) and Architect (`xhigh`) may move from Terra to Sol `high`. Lead is already Sol and escalates reasoning effort instead.
- When the native task surface exposes model and effort overrides, pass the requested values in the dispatch call; a role template's `model` field is only the default and never proof of the effective runtime.
- Model escalation does not change role, sandbox, owned surface, writer count, or review independence.
- Record `requestedModel`, `effectiveModel`, `requestedReasoningEffort`, `effectiveReasoningEffort`, and `modelEscalationReason`. If the host cannot provide the requested tier, keep the base model and record `modelEscalation: NOT_PROVEN`; never silently substitute an unrecorded model.
