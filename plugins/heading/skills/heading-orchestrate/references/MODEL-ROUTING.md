# Heading task-based model routing

Policy version: `2026-09-08.1`. State: **candidate, not benchmark-proven**.

## Owners

`model-policy.json` owns native model IDs, permitted efforts, route defaults and retry limits. This file owns their meaning and dispatch protocol. Lead owns task classification and dispatch. The host owns effective runtime identity. Role files own role and sandbox only. Track methods own product acceptance. No model output can grant permission or certify itself.

Reading this shared reference does not activate `heading-orchestrate`. All five product tracks can use it without delegation. A skill cannot switch an already running parent model. The optional profile requests Astra low for a new Lead session. Product work on the current host remains available when a model-switch API is absent, but its requested-route proof stays `NOT_PROVEN`.

## Decision table

| Observed task | Request | Reason |
| --- | --- | --- |
| Clear requirement, local scope, reversible, strong oracle, routine risk—all five | Luna xhigh | Smaller-model candidate for a fixed, checkable task. |
| Same easy task; one evidenced reasoning failure; bounded search; max budget authorized | Luna max once | More search within a stable task, not a substitute for architectural judgment. |
| Ambiguity, weak oracle, nonlocal state/ownership, recovery/security/contracts, or unknown difficulty | Astra low | Capability first; narrow effort until evidence requires more. |
| risk=critical, or risk=material with reversible=false | Astra medium | Risk-sensitive exception to the low starting effort. |
| Astra low reasoning failure with concrete counterexample | Astra medium | Preserve the same acceptance oracle. |
| Exceptionally difficult task with concrete justification and authorized ultra budget | Astra ultra | Optional direct exception or a justified retry after medium; native host support required. |
| Astra medium failure without an ultra exception | NEEDS_NEW_EVIDENCE | Do not automatically spend more reasoning budget. |
| Missing tool/platform, unavailable model, denied permission, or transient service failure | Repair that boundary | More reasoning is not an environment repair. |

These are Heading choices informed by official capability descriptions, not OpenAI's measured recommendation for this exact workload. Low is not always sufficient for hard work; xhigh is not always the cheapest setting for easy work. Measure cost and latency per **accepted outcome**, including failures, repairs and review. Do not infer performance equivalence across different models from effort names.

A short prompt can be hard. A large repetitive edit can be easy. A read-only security review can be critical. Label the actual risk, not the role name, file count, task length or user's adjective. Unknown facts never qualify a task for the easy route. Lack of an environment alone must not trigger escalation.

## Deterministic helper

From the installed `heading-orchestrate` skill directory:

```bash
python3 -B scripts/model_routing.py <<'JSON'
{
  "task": {
    "clarity": "clear", "scope": "local", "reversible": true,
    "oracle": "strong", "risk": "routine"
  },
  "history": [], "allowMax": false, "boundedSearch": false,
  "allowUltra": false, "ultraReason": ""
}
JSON
```

Astra normally uses only `low` (Light) and `medium`; `high`, `xhigh`, and `max` are excluded from Heading routes. `allowMax` applies only to Luna's existing bounded retry. `allowUltra: true` requires a non-empty `ultraReason` describing why this particular outcome is exceptionally difficult and a budget already authorized by the user/session. Existing authorization is sufficient; do not ask again. This permits a direct ultra exception without forcing an intentionally inadequate medium attempt. Otherwise a medium failure returns `NEEDS_NEW_EVIDENCE`, never an automatic ultra dispatch. Environment failures still require repair, even with an ultra exception. An exhausted ultra attempt cannot be reset by an exception or a Luna retry.

Policy `2026-09-08.1` retires `astra-high`, `astra-xhigh`, and `astra-max`; old history entries with those keys are rejected. Preserve their original evidence and obtain a new Lead decision for the current outcome instead of silently relabeling or discarding failures.

The helper reads facts supplied by Lead; it does not classify natural language, authenticate evidence, call an API, select the current chat model, or launch an agent. It emits a **request**, with `effectiveModel` and `effectiveReasoningEffort` unset. Invalid facts fail explicitly. If Python is absent, apply this same table as instructions and distinguish manual selection from automated selection.

A failed-attempt entry is `{ "route": "luna-xhigh", "failure": "reasoning", "evidence": "tests/output-shape.log: expected three fields, got two" }`. Allowed failure classes are in the policy and helper. `evidence` must reference an actual observation, not a fixture passed off as production behavior. Retain the entire current-outcome attempt history. Do not clear it to evade the retry budget. New evidence and a new Lead decision are needed when the ladder is exhausted.

`REPAIR_REQUIRED` and `NEEDS_NEW_EVIDENCE` are routing states, not permission to dispatch the returned pair. Only `REQUESTED` advances to the host check. All three can coexist with other useful, already-authorized work.

## Host dispatch and observation

1. Lock Goal, Context, Owned surface, Constraints, Done and Evidence. Put taskClass, route reason and requested settings in Constraints. Do not add extra unowned writers.
2. Read the host's actual tool schema and supported model/effort catalog. The native Codex documentation lists `ultra` only where the model supports it. The Responses API Astra effort list does not include `ultra`; do not send this native route to the API or silently map it to `max`. For ChatGPT Work, Ultra is a product mode with maximum reasoning and proactive delegation, not simply an API effort. Unsupported native ultra stays `NOT_PROVEN`/`BLOCKED` for that lane. `astra-low` and `luna-xhigh` are Heading route keys, **not** API model IDs. `Light` is the UI label corresponding to `low`; do not send `light` as API effort. Never invent dated snapshot IDs.
3. Native dispatch supplies both `model` and the host's effort field. API Responses uses `model` and `reasoning.effort`; Codex config uses `model` and `model_reasoning_effort`. Do not guess a spawn field name. `agents/openai.yaml` is UI/invocation metadata, not model execution configuration.
4. Current Codex custom-agent file values override dispatch settings. Heading's four files therefore omit both model keys. Do not edit installed role files during work. Do not silently inherit a parent setting in place of a required explicit route.
5. Record requested/effective model and effort separately, plus source of host observation, task ID, role, sandbox, candidate revision and reason. Do not use the worker's answer or role template as runtime proof. The helper's observation comparator checks model/effort and the separately locked taskId/role/sandbox; the caller must still authenticate their provenance and final state. Matching fields is not a signed host attestation.
6. Require an observed role/permission boundary before delegated writes. Missing route observation blocks claims about that route. Material work needing a stronger route must not continue under an unverified weaker one; preserve the candidate and continue safe inspection. A declared direct lane is a separate decision, not a silent fallback.
7. Keep accepted repairs in the same Executor when the host honors the selected pair in place. Otherwise checkpoint base/candidate revisions, dirty diff, owned processes, done/oracle, evidence, pending repairs and route reason. Observe old writer and owned processes stopped before one replacement accepts the unchanged outcome. Unknown stop state prohibits a replacement writer.
8. A fresh read-only Reviewer checks the actual candidate. Independence means separate judgment and no write authority, not a different model brand. Lead alone accepts the outcome. Missing independent review is `NOT_PROVEN`.

## Model-specific task packets

### Astra: complete outcome, explicit boundaries

```text
Goal: [one complete outcome]
Context: [actual entry path, decisive sources and current evidence]
Owned surface: [files/interfaces and writer]
Constraints: [invariants, authority/approval boundary, route request and reason]
Done: [observable acceptance criterion]
Evidence: [commands, counterexamples, read-back and candidate revision]

Complete the authorized reversible work. Resolve routine gaps from evidence;
ask only about an unresolved choice that materially changes the outcome.
Follow the user's requirements within higher-priority instructions and permissions.
Keep the domain decision and I/O boundary explicit. Return observed results and
unknowns; do not use an explanation of reasoning as verification.
```

Do not prescribe hidden reasoning steps or repeat the same policy across every packet. Read only relevant methods/references. A short handover must retain public contracts and decisive counterexamples; it must not invent absent history. Keep updates brief and proportionate. Expand testing for actual dependency risk rather than automatically running all suites.

### Luna: fixed task, strong oracle

```text
Goal: [one bounded transformation or implementation slice]
Context: [exact source paths and facts needed]
Owned surface: [only allowed files/interfaces]
Constraints: [public shape, forbidden changes, requested model and effort]
Done: [exact observable behavior; examples only when genuinely useful]
Evidence: [local command or deterministic oracle]

Do not redesign surrounding architecture. Complete the slice and run its oracle.
If the assumption or scope proves wrong, preserve the candidate and return the
counterexample to Lead. Do not compensate with an unbounded search or hidden fallback.
```

## Verification and refresh

See [RESEARCH-2026-09-07.md](RESEARCH-2026-09-07.md) for dated primary sources, API limitations and source conflicts. Refresh model IDs, supported efforts, custom-agent precedence and account availability before deployment after a client/catalog change. Do not auto-rewrite policy from an untrusted webpage. The packaged policy is a versioned snapshot; a change requires review and regression tests.

Before claiming this routing is optimal: compare easy tasks on Luna high/xhigh/max and hard tasks on Astra low/medium, adding native ultra only for justified exceptional tasks, with the same input, oracle, tools, revision and independent acceptance. Keep failed and blocked runs in denominators. Separate routing decision quality, actual route application and completed-product quality. The supplied native intake runner measures intake behavior, **not** complex end-to-end implementation quality.
