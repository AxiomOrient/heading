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
- whether the request authorizes a separate user-visible task.

If any missing field would let two workers edit the same boundary or make an unverifiable claim, ask one material question. Otherwise continue in the current conversation.

## Choose one lane

1. **Direct lane.** The primary agent performs the bounded work and reports the actual evidence. Use this when no independent worker is necessary.
2. **Native lane.** Use a configured native implementer only after observing its exact identity, model/reasoning setting, write boundary, and task identity from the live runtime. Do not infer those facts from a template or documentation.
3. **User-visible task lane.** Create a separate task only when the user explicitly authorizes it and the exposed task tools can provide a non-empty task identity, bounded ownership, and observable completion.

Never silently substitute a different model, role, task surface, write boundary, or reviewer. If the requested lane is unavailable or cannot be observed, mark that lane `NOT_PROVEN` or `BLOCKED`; offer the direct lane only as a separately stated option.

## Native lane protocol

1. Confirm the task packet and designate exactly one writer.
2. Give the implementer the packet and require: changed files, commands actually run, results, unresolved risk, and `EXECUTOR_RESULT`.
3. Observe completion using the concrete task identity. Never wait with an empty target list; do not claim completion from a timeout or missing report.
4. Keep correction in the same implementer task unless the packet's ownership changes materially.
5. A primary reviewer independently inspects the actual candidate and reports severity-ranked findings. The implementer does not self-accept.
6. The primary agent alone integrates, decides whether the proof meets the locked rule, and reports `PASS`, `PARTIAL`, `NOT_PROVEN`, or `BLOCKED`.

## User-visible task lane protocol

Use only tools that are actually exposed in the current host. Before creation, confirm the base revision and the task's file ownership. After creation, record the returned non-empty task ID and the exact packet. Observe the task through that ID. Do not create background work for research, review, or a task that can be completed directly without parallel ownership.

## Output

Return a concise coordination record:

- lane and why it was eligible;
- task packet summary and owner;
- observed task/runtime identity when delegation was used;
- evidence, reviewer findings, and integration decision;
- final status plus every remaining uncertainty.

Do not expose raw runtime secrets, full tool payloads, or unobserved claims as evidence.
