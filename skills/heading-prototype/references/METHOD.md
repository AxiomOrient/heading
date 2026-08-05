# Prototype method

## Selection and defaults

- Infer the decision, mode, and riskiest assumption from the request, artifacts, prior decisions, and repository evidence.
- Default to synthetic, anonymized, or private data and a reversible probe. If real users are unavailable, use representative proxies and downgrade the evidence claim.
- Set a conservative threshold before the probe when none is supplied. Ask only when no decision can be inferred or two mutually exclusive decisions remain equally supported.
- Repair the method instead of rejecting a valid goal: replace fabricated interviews with labeled synthetic exploration or a real research plan; deceptive charges with non-binding commitment signals; cherry-picking with a locked corpus and rubric; unauthorized data with consented or synthetic data.
- Refuse only when deception, unauthorized collection, or financial action is the essential goal and no safe equivalent remains.

## Modes

| Mode | Risky assumption | Mandatory proof |
|---|---|---|
| `desirability` | target users understand, want, or can use it | observed representative task behavior; behavior separated from stated preference |
| `workflow` | a human-system process works | Wizard-of-Oz or concierge run, operator burden, handoff failures, completion evidence |
| `feasibility` | a technical boundary can satisfy a hard constraint | real dependency or representative workload, measured limits, failures, environment |
| `viability` | demand, cost, or operating economics can support the choice | ethical commitment signal, explicit cost assumptions, no deceptive charge or unauthorized data capture |
| `generative-quality` | generated output is consistently acceptable | locked corpus, rubric, holdout cases, repeated samples, failure slices, variance, versioned system |

## Required lock

- `decision`
- `mode`
- `target_context`
- `riskiest_assumption`
- `representative_sample`
- `decision_threshold`
- `fidelity_budget`
- `isolation`
- `disposal_rule`

## Protocol

1. **Frame:** State one falsifiable assumption and the decision it controls.
2. **Design:** Preserve only fidelity needed to expose the assumption.
3. **Run:** Execute representative inputs or tasks and log observations before interpretation.
4. **Compare:** Compare materially different candidates under the same rule only when it can change the decision.
5. **Decide:** Apply the precommitted threshold once.
6. **Transfer:** Preserve accepted contracts, fixtures, rubrics, or learning. Disposable implementation does not merge by default.

## Stop

A demo, one favorable example, aggregate-only score, self-review, or fabricated evidence is not decision evidence. Missing ideal evidence yields `INCONCLUSIVE` or downgraded evidence, not fabricated certainty.

## Result schema

- `mode`
- `decision`: `ADOPT | REJECT | ITERATE | INCONCLUSIVE`
- `assumptionResult`: `SUPPORTED | FALSIFIED | UNRESOLVED`
- `observations`
- `thresholdResult`
- `transferAsset`
- `discard`
- `unknowns`
