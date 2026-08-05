# Grow method

## Selection and defaults

- Infer the target segment, product stage, candidate funnel, and strongest measurable outcome from telemetry, product contracts, and prior decisions.
- Default to one primary metric, explicit guardrails, a reversible treatment, privacy-preserving measurement, and a precommitted threshold and stopping rule.
- Ask only when no evidence distinguishes two materially different outcomes, assignment units, or irreversible tracking choices.
- Repair invalid methods while preserving the growth goal: replace dark patterns with value-creating treatments; unauthorized tracking with consented or aggregate telemetry; cherry-picking with locked metrics and full slices; guarantees with a falsifiable hypothesis and evidence grade.
- If no product exists, auto-realign before lock. If telemetry or observation is incomplete, implement useful measurement and return effect `NOT_PROVEN`; do not fabricate or stop all work.
- Refuse only when fabricated reporting, coercion, or unauthorized surveillance is the essential goal and no honest growth outcome remains.

## Evidence designs

| Design | Use when | Mandatory proof |
|---|---|---|
| `randomized` | stable randomized assignment is possible | assignment and analysis units, exposure, sample-ratio check, contamination, effect and uncertainty |
| `sequential` | valid repeated looks or early stopping are needed | precommitted sequential method, boundary rule, maximum sample or time, full trace |
| `switchback` | shared capacity or marketplace interference dominates | randomized time blocks, washout, carryover and interference analysis |
| `holdout-rollout` | staged rollout or long-term effect needs a control | persistent control, eligibility, ramp stages, contamination, stop and rollback |
| `observational` | randomization is unavailable | explicit confounders, cohort and time definitions, sensitivity checks, associational wording |

## Required lock

- `segment`
- `evidence_design`
- `assignment_and_analysis_unit`
- `exposure`
- `hypothesis_and_falsifier`
- `primary_metric`
- `guardrails`
- `data_quality_checks`
- `effect_threshold`
- `observation_window`
- `stopping_rule`
- `rollback`

## Protocol

1. **Design:** State one hypothesis, mechanism, falsifier, primary metric, guardrails, and evidence design.
2. **Instrument:** Verify assignment, exposure, metric semantics, missingness, sample ratio, contamination, and baseline.
3. **Ship:** Implement the smallest attributable reversible treatment.
4. **Analyze:** Apply the precommitted method; a post-hoc segment, metric switch, or peeking rule is invalid.
5. **Decide:** Separate implementation, data quality, effect, evidence grade, and guardrail result. Bandit allocation alone is not causal evidence. Product-market fit is not proven by one treatment.

## Result schema

- `evidenceDesign`
- `implementationStatus`
- `dataQualityStatus`
- `effect`
- `evidenceGrade`: `CAUSAL | QUASI_CAUSAL | ASSOCIATIONAL | NOT_PROVEN`
- `decision`: `KEEP | ROLLBACK | ITERATE | NOT_PROVEN`
- `guardrailResult`
- `unknowns`
