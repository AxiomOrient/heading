# Sweep method

## Selection and defaults

- Infer preserved behavior and the strongest oracle from tests, runtime, public contracts, tasks, screenshots, traces, or fixtures before editing.
- Default to preserving public behavior, state transitions, failure semantics, accessibility, and durable data. Prefer delete, collapse, direct paths, refactor, then measured optimization.
- Ask only when two incompatible public meanings are equally plausible and repository evidence cannot resolve them.
- Repair invalid methods while preserving the goal: fix causes instead of deleting tests; preserve explicit failures instead of returning success; measure performance instead of inventing numbers; optimize around authorization instead of removing it.
- Refuse only when concealment or destructive behavior loss is the essential goal and no transparent, behavior-preserving outcome remains.

## Modes

| Mode | Objective | Mandatory proof |
|---|---|---|
| `delete` | remove unreachable or unnecessary behavior or assets | classification, reachability, usage, external-contract and package check, replacement oracle, before/after inventory |
| `collapse` | remove duplicate state, conversion, wrappers, or interfaces | ownership map, same outputs and failures, net reduction |
| `refactor` | clarify responsibility without changing behavior | differential or semantic comparison, state and failure equivalence |
| `ui` | simplify interaction and visual hierarchy | task success, accessibility, interaction, and visual comparison |
| `performance` | reduce latency, memory, CPU, I/O, or resource cost | correctness oracle, same environment, warmup and repeated samples, bottleneck evidence |

## Required lock

- `mode`
- `preserved_oracle`
- `representative_corpus`
- `baseline`
- `subtractive_seam`
- `target_delta`
- `non_goals`
- `revert_rule`
- `canonical_workspace_identity`
- `input_output_artifact_ledger`
- `evidence_freshness`

## Protocol

1. **Observe:** Bind the canonical workspace; classify each candidate as input authority, product output, proof artifact, test oracle, or generated residue; then capture the oracle and baseline.
2. **Rank:** Choose the highest-confidence removable cost.
3. **Cut:** Apply one complete subtractive seam; avoid broad rewrites and speculative abstractions.
4. **Differential:** Compare the same inputs and environment; use properties or fuzzing for broad deterministic input spaces and semantic tools when textual line diff alone is insufficient.
5. **Judge:** Confirm complexity was removed rather than moved.
6. **Keep or revert:** Revert if the oracle weakens, complexity moves elsewhere, or gains are noise. Runtime non-use alone is insufficient for deletion. Compatibility shims and dead flags are removed only when their contract is gone and a replacement oracle or explicit no-consumer proof exists.

## Result schema

- `mode`
- `preservedOracle`
- `removed`
- `before`
- `after`
- `decision`: `KEEP | REVERT | PARTIAL`
- `residualComplexity`
- `artifactLedger`
- `evidenceFreshness`
- `unknowns`
