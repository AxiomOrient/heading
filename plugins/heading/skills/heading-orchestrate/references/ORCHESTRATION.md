# Heading orchestration contract

## Non-negotiable boundaries

- A task packet comes before delegation.
- There is exactly one writer for a file or interface boundary.
- Runtime identity, write boundary, and completion are observed facts, not template assumptions.
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
| Recovery | Rollback or stop condition where the change can affect users or data. |
| Report | Files changed, evidence, open risks, and result token. |

## Status meanings

- `PASS`: the locked proof passed and the primary agent accepted the candidate.
- `PARTIAL`: useful work completed, but a stated acceptance condition is incomplete.
- `NOT_PROVEN`: a required environment, tool, or observation was unavailable.
- `BLOCKED`: a material decision or safety condition prevents responsible continuation.
