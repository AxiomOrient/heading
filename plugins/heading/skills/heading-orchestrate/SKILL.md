---
name: heading-orchestrate
description: Coordinate an already-locked Heading outcome across direct work, native agents, or an explicitly authorized user-visible task with observable ownership, verification, and acceptance.
---

Use this skill only after a Heading product track has locked the outcome, scope, proof, and acceptance rule. It coordinates work; it does not replace `heading-prototype`, `heading-build`, `heading-sweep`, `heading-grow`, or `heading-maintain`.

## Inputs to lock

Write one task packet before any delegation:

- outcome, track, mode, and acceptance rule;
- owned files or interfaces, non-goals, base revision, and integration owner;
- evidence to inspect, commands to run, failure/rollback boundary, and expected report;
- default model/effort, any requested model escalation and reason, and the requested/effective runtime values to record;
- whether the request authorizes a separate user-visible task.

If any missing field would let two workers edit the same boundary or make an unverifiable claim, ask one material question. Otherwise continue in the current conversation.

## Choose one lane

1. **Direct lane.** The primary agent performs the bounded work and reports the actual evidence. Use this when no independent worker is necessary.
2. **Native lane.** Use a configured native implementer only after observing its exact identity, model/reasoning setting, write boundary, and task identity from the live runtime. Do not infer those facts from a template or documentation.
3. **User-visible task lane.** Create a separate task only when the user explicitly authorizes it and the exposed task tools can provide a non-empty task identity, bounded ownership, and observable completion.

A higher model tier or effort is allowed only when Lead records a task-based routing reason. Never silently substitute a different model, role, task surface, write boundary, or reviewer. If the requested lane or model is unavailable or cannot be observed, mark that lane or escalation `NOT_PROVEN` or `BLOCKED`; offer the direct lane only as a separately stated option.

## Task-based model routing

Read `references/MODEL-ROUTING.md` and `references/model-policy.json`; read `references/EVIDENCE-CAPSULE.md` only for evidence handoff. Classify the bounded **work shape**, independently of role: exact inspection uses direct tools; fixed extraction or local evidence with a strong oracle uses Luna `high`; broad or weak-oracle exploration uses Terra `medium`; clear implementation uses Terra `medium`; decisions use Astra `low`; critical or irreversible material risk starts at Astra `high`. For complex judgments choose `high` or `xhigh` upfront using `astraEffort`, `effortReason`, and `effortEvidence`, without a mandatory cheaper failure. Astra `max`/`ultra` require a concrete reason and authorized exceptional budget. These are candidate defaults, not measured optimality claims. Sol is outside the active routing policy.

Use `specialistEffort` with `effortReason` and `effortEvidence` for Luna `xhigh`/`max` or Terra `high` upfront. Luna `high` and Terra `medium` are the defaults; Luna max is already authorized by policy and needs no extra budget approval. Preserve role boundaries and failed-route limits.

Use `scripts/model_routing.py` for deterministic selection when available. It never calls a model, starts a worker, or changes the host. A `DIRECT_TOOLS` result has `modelEscalation: NOT_APPLICABLE`; a requested model route has `modelEscalation: NOT_PROVEN` until host metadata records effective values. Record `riskBand`, `workShape`, `requestedModel`, `requestedReasoningEffort`, `effectiveModel`, `effectiveReasoningEffort`, and `modelEscalationReason` separately. Every 0.5.0 task packet must declare `shape`; malformed packets fail explicitly. Native dispatch must pass both requested values. The four Heading role files contain no model/effort overrides because custom-file values take precedence over explicit spawn settings in current Codex.

Use one authorized read-only scout when synthesis justifies delegation, at most two for independent questions. Default to `fork_turns="none"` with a self-contained scope, constraints, evidence, and done rule. Each returns a validated evidence capsule with source references and unresolved questions. Lead checks decisive sources and coverage gaps without redoing the whole scan. A capsule is not a prompt, write grant, runtime proof, or final acceptance. Never silently substitute a lower tier or claim model execution from a prompt, UI label, template, or self-report. If a material task needs an unavailable route, continue safe inspection and preserve its candidate without claiming the gated proof.

## Native lane protocol

1. Confirm the task packet, requested/effective model fields, and designate exactly one writer.
2. Give the implementer the packet and require: changed files, commands actually run, results, unresolved risk, model escalation evidence, and `EXECUTOR_RESULT`. Give a research scout only read-only evidence ownership and require a validated evidence capsule.
3. Observe completion using the concrete task identity. Never wait with an empty target list; do not claim completion from a timeout or missing report.
4. Keep correction in the same implementer task. If the host cannot change a required route in place, checkpoint the candidate, observe the old writer stopped, and hand the same bounded outcome to exactly one replacement. Ownership changes require a new outcome.
5. A primary reviewer independently inspects the actual candidate and reports severity-ranked findings. The implementer does not self-accept.
6. The primary agent alone integrates, decides whether the proof meets the locked rule, and reports `PASS`, `PARTIAL`, `NOT_PROVEN`, or `BLOCKED`.

## User-visible task lane protocol

Use only tools that are actually exposed in the current host. Before creation, confirm the base revision and the task's file ownership. After creation, record the returned non-empty task ID and the exact packet. Observe the task through that ID. Do not create background work for research, review, or a task that can be completed directly without parallel ownership.

## Output

Return a concise coordination record:

- lane and why it was eligible;
- task packet summary and owner;
- observed task/runtime identity when delegation was used;
- requested/effective model and reasoning effort plus escalation reason, if any;
- evidence, reviewer findings, and integration decision;
- final status plus every remaining uncertainty.

Do not expose raw runtime secrets, full tool payloads, or unobserved claims as evidence.
