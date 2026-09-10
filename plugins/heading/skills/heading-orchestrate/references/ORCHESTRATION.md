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

## Task-based model routing

`MODEL-ROUTING.md` owns the routing protocol; `model-policy.json` owns model IDs, supported efforts, work-shape defaults, and bounded escalation constants; `EVIDENCE-CAPSULE.md` owns the read-only evidence handoff. Reading them is not invoking the orchestration skill.

The declared work shape selects capability. The role selects authority. Deterministic preflight is `DIRECT_TOOLS` with no model request. Fixed extraction and bounded local evidence start at Luna high; broad or weak-oracle exploration at Terra medium; implementation at Terra medium; judgment at Astra low. Critical work starts high. Complex decisions can request high/xhigh upfront with a reason and evidence; two automatic failures stop escalation. Native dispatch explicitly supplies both settings; role templates do not override them. Preserve role, sandbox, owned surface, writer count, capsule boundary, and review independence through every route change.

Requested/effective model and effort are distinct. Missing model observation is `modelEscalation: NOT_PROVEN`; deterministic work is `modelEscalation: NOT_APPLICABLE`; neither is inferred success. Environment failures are not model-quality failures. One authorized scout is the default; two require independent read-only questions with self-contained fork-none packets, and they return capsules rather than raw context. The same outcome normally stays in the same Executor thread; a required model change that the host cannot apply in place needs an observed stop, exact-candidate checkpoint and single-writer handover.
