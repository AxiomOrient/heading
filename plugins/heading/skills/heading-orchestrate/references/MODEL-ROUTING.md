# Heading model routing

Policy `2026-09-10.5`: **CANDIDATE_NOT_BENCHMARKED**. `model-policy.json` owns route values; this file owns selection and dispatch semantics. Lead owns acceptance; the host owns effective execution identity. Role files own authority and sandbox, never model overrides.

## Choose work before model

Use the least expensive route likely to meet the acceptance rule on the whole outcome. Minimize Astra input/reasoning and avoidable rework subject to correctness; cheap token prices alone do not establish accepted-outcome cost. Do not run every task through every tier.

| Work | Candidate request |
| --- | --- |
| Exact listing, search, parsing, filtering, diff, test discovery | `DIRECT_TOOLS`; no additional model request |
| Fixed extraction; local evidence collection with a strong oracle | Luna `high` |
| Broad/cross-boundary source discovery or weak-oracle evidence scan | Terra `medium` |
| Clear implementation with a strong regression oracle | Terra `medium` |
| Bounded decision, integration, or unknown work shape | Astra `low` |
| Critical risk or irreversible material change | Astra `high` floor |

`clarity` describes whether the question and task contract are clear, not whether its answer is known. A clear request to discover an unknown owner is broad exploration; an unclear requested outcome still needs Lead qualification. Specialist routes require clear, routine, reversible work; fixed extraction and implementation also require a strong oracle. `local` means a bounded question with independently checkable coverage, not merely one directory. Unknown reachability or conflicting state ownership belongs in broad exploration or Astra judgment. Sol is excluded from active defaults and retry routes to simplify this user's Luna–Terra–Astra policy; this is not a claim that Sol is universally inferior.

## Select effort before expensive work

Luna starts at **high**. Choose **xhigh** upfront for coupled evidence, multi-hop references, or expensive omissions within its bounded scope; **max** is also authorized when that bounded question benefits from more reasoning. Terra starts at **medium** for both broad exploration and implementation; use **high** for complex local logic, edge cases, or costly rework. Increasing effort does not widen the role or give Luna architectural authority.

For these choices, set `specialistEffort` and include `effortReason` and `effortEvidence`. It changes only the specialist model selected for this packet, including its next route after a failure; it cannot choose another model or override an Astra requirement. Valid current values are Luna high/xhigh/max and Terra medium/high. Luna max is authorized by the user's policy and does **not** require `maxBudgetAuthorized` or another approval. That existing flag is specific to Astra max. Do not combine `specialistEffort` with `astraEffort` or `allowUltra`. Environment repairs, exhausted routes, and the two-failure automatic budget still take precedence.

Old Luna low/medium and Terra low route IDs remain readable for existing failure history and explicit benchmark controls. They are never selected as new defaults or specialist overrides. Judge default effort by first-pass acceptance and the total tokens/cost of all attempts and reviews, not one request's token count. The higher defaults reflect the user's rework preference; savings remain unmeasured.

Astra low is a coordination default, not a required first attempt. Use medium for several interacting but bounded constraints, high for difficult RCA, concurrency, security, recovery, or important acceptance decisions, and xhigh for exceptionally coupled constraints or expensive-to-reverse decisions. A demand to be accurate alone does not make every lookup high. Verify information and access before adding compute.

To request Astra effort upfront, supply `astraEffort` (`low`, `medium`, `high`, `xhigh`, or `max`), a task-specific `effortReason`, and a source/constraint `effortEvidence`. Higher risk and already-failed capability set a floor: an explicit lower effort cannot bypass them. No cheap failure is required. Astra max additionally needs `maxBudgetAuthorized: true`. The existing ultra contract is `allowUltra: true`, non-empty `ultraReason`, and `ultraBudgetAuthorized: true`; do not combine the two request mechanisms. Budget authorization can come from the existing session; do not ask again when it is already supplied. Astra max/ultra also require observed host support. They are exceptional requests, not automatic retries or API aliases.

```bash
python3 -B scripts/model_routing.py <<'JSON'
{
  "task": {
    "clarity": "clear", "scope": "cross-boundary", "reversible": false,
    "oracle": "weak", "risk": "material", "shape": "cross-boundary-decision"
  },
  "astraEffort": "xhigh",
  "effortReason": "One recovery decision couples transaction ownership and replay ordering",
  "effortEvidence": "src/recovery.py:88; tests/replay_failure.py:41"
}
JSON
```

This emits a request; it never calls a model or switches the active parent. The optional profile starts a new Lead at Astra low and supplies Luna high subagent defaults with a two-child ceiling. Existing sessions and global settings are not changed by reading a skill. If in-place switching is unavailable, send only the bounded hard question to an observed Astra high/xhigh child, or retain the active capable route and disclose its actual setting; never claim the parent changed.

## Prevent repeated work

1. Use `rg`/git/LSP/parsers to narrow candidate paths and line ranges before semantic reading. A tool calculation needs no LLM inference internally, but tool instructions, results, and follow-up still use model context. Keep full logs in an artifact; return exit status, diagnostic excerpts, and a path. Never truncate away a failure and call it success.
2. For a useful read-only synthesis, use one authorized scout; only independent questions justify two. `allowEvidenceScouts: true` requests one by default; `parallelism: "independent"` requests two. Neither field grants permission or creates workers. Exact one-tool lookups remain direct.
3. Default delegated packets to `fork_turns="none"`, as the actual host schema permits. Include outcome, base revision, scoped paths, constraints, existing evidence, requested model/effort, oracle, and done rule explicitly. Use recent bounded turns only when needed. Full-history forks cannot carry model overrides on the current host; do not inherit the entire conversation accidentally.
4. Reuse the scout for a related missing fact. Do not ask several scouts to read the same files. Do not resend a full transcript during escalation: reuse the evidence and candidate, adding the failed claim, decisive excerpt, and unresolved question.
5. Use an [evidence capsule](EVIDENCE-CAPSULE.md): sources, facts, uncertainty, and coverage limits, not essays. Lead spot-checks decisive claims, contradictory sources, reachability, and changed regions. A failed check expands only the affected slice; it does not force a duplicate repository scan.
6. Preserve stable instructions and reuse existing work. Do not automatically enable Fast mode or alter unrelated MCP/plugin settings for cost optimization. Caching reduces billed/compute cost, not raw input count; actual native-host controls take precedence over API examples.

## Failure transitions

Retain the whole observed history: `{ "route": "luna-high", "failure": "reasoning", "evidence": "coverage.log:4" }`. Only a demonstrated reasoning/coverage failure is a capability miss; missing files, missing access, environment errors, and transient failures need repair or evidence acquisition.

- Environment/permission/transient failures return `REPAIR_REQUIRED` at the failed route; effort overrides cannot bypass repair.
- A bounded Luna extraction/exploration failure can move to Terra medium. Terra failure or an unresolved semantic decision moves to Astra; critical work keeps the high floor. Never revisit a failed lower capability after an interleaved failure.
- Astra effort can advance low → medium → high → xhigh, but after two evidenced route failures automatic escalation stops with `NEEDS_NEW_EVIDENCE`. Do not blindly walk a ladder. A deliberate higher request with a reason and evidence may skip levels; each failed route remains exhausted once.
- Astra max/ultra require their explicit exceptional contracts. Exhausted ultra remains exhausted. `REPAIR_REQUIRED` and `NEEDS_NEW_EVIDENCE` are not dispatchable requests.

## Dispatch and proof

Read actual host model/effort and tool schemas. Current native support starts at low for Luna even though its API also documents none; never infer host support from API documentation. For `REQUESTED`, pass both model and effort, use the declared authority boundary, and record the non-empty task ID and requested/effective fields separately. `requestedForkTurns` is a request, not context-inheritance proof. `DIRECT_TOOLS` has null model fields and `NOT_APPLICABLE`; model requests remain `NOT_PROVEN` until host metadata supplies matching values. Self-reports and templates are not host evidence.

Keep exactly one writer. When a required route cannot change in the same Executor, checkpoint the candidate, observe the old writer and its processes stopped, and transfer the unchanged outcome to one replacement. A fresh read-only Reviewer checks material changes independently. Lead alone accepts; unavailable independent review leaves that proof `NOT_PROVEN`.

Read [RESEARCH-2026-09-10.md](RESEARCH-2026-09-10.md) when auditing sources or choosing a new policy. Repository maintainers can use `evals/route-benchmark-plan.json` for paired evaluation; that file is not included in the installed plugin. Deterministic routing tests prove transitions, not model quality or savings.
