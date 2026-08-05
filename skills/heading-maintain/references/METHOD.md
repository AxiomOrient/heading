# Maintain method

## Selection and defaults

- For “broken,” “slow,” or “upgrade,” inspect impact, logs, tests, recent changes, versions, runtime state, and durable data before asking. Preserve evidence.
- Default active impact to containment first; defects to reproduction; security to reachability; data repair to snapshot and dry-run; planned change to one candidate, stop signals, rollback, and post-change watch.
- Ask only when the affected target is genuinely unknown, production authority is required, or an irreversible action cannot be replaced by a safe reversible path.
- Repair invalid methods while preserving the operational goal: retain logs and investigate instead of concealment; repair alerts instead of disabling them; use authorized access instead of bypass; create backup and idempotent repair instead of blind edits; use bounded approved fault injection or simulation instead of uncontrolled production chaos.
- Missing production access does not block reproduction, local patching, regression tests, rollback planning, or a runbook; mark production observation `NOT_PROVEN`.
- Refuse only when concealment, unauthorized access, or destructive interference is the essential goal and no protective outcome remains.

## Modes

| Mode | Objective | Mandatory proof |
|---|---|---|
| `incident` | reduce active impact | timeline, preserved evidence, containment or restoration, cause hypothesis, regression, watch |
| `defect` | correct a reproducible fault | reproduction, causal boundary, regression test, smallest fix, affected versions |
| `security` | contain or remove exposure | advisory or threat evidence, affected assets, reachability, credential action, residual exposure |
| `reliability-capacity` | protect SLO, latency, throughput, saturation, or headroom | baseline, representative load or failure, bottleneck, bounded degradation, watch |
| `planned-change` | upgrade dependency, config, platform, topology, or procedure | compatibility, one active candidate, stop threshold, rollback, candidate/control signals |
| `data-repair` | restore corrupted or inconsistent durable state | immutable backup or snapshot, dry-run, deterministic idempotent plan, counts or checksums, partial recovery |

## Required lock

- `mode`
- `impact_and_urgency`
- `evidence_and_timeline`
- `invariants`
- `affected_version_config_data`
- `blast_radius`
- `containment`
- `rollback_or_recovery`
- `stop_conditions`
- `post_change_watch`

## Protocol

1. **Triage:** Separate active impact from planned work and preserve evidence.
2. **Contain:** Contain harm before an elegant permanent fix.
3. **Diagnose:** Reproduce or correlate the issue to a causal boundary.
4. **Change:** Apply the smallest complete correction and defer unrelated cleanup.
5. **Recover:** Verify durable state, retry, restart, rollback, degraded mode, security, and capacity semantics that apply.
6. **Watch:** Compare post-change signals with baseline. Controlled fault injection or history checking requires an approved bounded environment.

## Result schema

- `mode`
- `status`: `RESTORED | STABILIZED | CHANGED | PARTIAL | BLOCKED`
- `impact`
- `causeOrRationale`
- `containment`
- `change`
- `recoveryEvidence`
- `postChangeObservation`
- `residualRisk`
