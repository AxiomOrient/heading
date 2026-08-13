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
- `runtime_custody` (when a command, session, worker, kernel, service, or process is in scope: owner/session token, leader and group/job identity, monotonic operation deadline, teardown budget, exact cleanup scope, reap/no-survivor proof)
- `canonical_workspace_identity`
- `input_output_artifact_ledger`
- `evidence_freshness`

## Protocol

1. **Triage:** Bind the canonical workspace and distinguish runner failure from stale workdir/mount failure before diagnosing the product. Separate active impact from planned work and preserve bounded evidence. If external work is in scope, record its custody identity before changing it.
2. **Contain:** Contain harm before an elegant permanent fix. For a timeout or cancellation, use the exact-scope bounded teardown in [`PROCESS-LIFECYCLE.md`](PROCESS-LIFECYCLE.md); timeout is not proof of exit.
3. **Diagnose:** Reproduce or correlate the issue to a causal boundary without duplicating a live command or session.
4. **Change:** Apply the smallest complete correction and defer unrelated cleanup.
5. **Recover:** Verify durable state, retry, restart, rollback, degraded mode, security, and capacity semantics that apply. Retry only with an explicit idempotency and quota/transport policy. Do not hand off or start a replacement until owned processes/sessions are stopped and reaped; otherwise record `runtimeObserved: NOT_PROVEN` and use the appropriate non-success status.
6. **Watch:** Compare post-change signals with baseline, including immediate and delayed no-survivor/reap checks and owned output-handle closure. Controlled fault injection or history checking requires an approved bounded environment.

## Result schema

- `mode`
- `status`: `RESTORED | STABILIZED | CHANGED | PARTIAL | BLOCKED`
- `impact`
- `causeOrRationale`
- `containment`
- `change`
- `recoveryEvidence`
- `postChangeObservation`
- `runtimeObserved`: `PROVEN | NOT_PROVEN | NOT_APPLICABLE`
- `runtimeCustodyEvidence` (when applicable: identity, deadline/teardown sequence, bounded wait/reap, pipe/handle closure, immediate and delayed no-survivor watch)
- `residualRisk`

When an external command, session, worker, kernel, service, or process is material to the
claim, `RESTORED`, `STABILIZED`, and `CHANGED` require `runtimeObserved: PROVEN` with
bounded cleanup, reap, and no-survivor evidence. Otherwise use `PARTIAL` or `BLOCKED` as
appropriate; `NOT_PROVEN` is an observation state, not a sixth result status.
