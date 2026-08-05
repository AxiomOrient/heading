# Heading 0.1.0

Heading provides five explicit Codex skills for product work.

```text
$heading-prototype  decide what should be built
$heading-build      turn accepted behavior into a complete product outcome
$heading-sweep      remove complexity while preserving behavior
$heading-grow       measure the product impact of a shipped treatment
$heading-maintain   control risk, incidents, and change in an existing system
```

## Usage

A one-line request is enough.

```text
$heading-prototype Test whether this feature is worth building.
$heading-build Complete the attached repository for release.
$heading-sweep Preserve behavior and make the system as simple as possible.
$heading-grow Improve first-task success.
$heading-maintain Fix the intermittent data loss safely.
```

Adding one non-negotiable constraint improves precision:

```text
$heading-sweep Preserve the public API and simplify only the internals.
```

## Wrong track selection

The invoked skill is a **routing hint**. Heading infers the effective track from the request and evidence before work starts.

```text
$heading-build Test whether users want this idea.
```

This request is corrected to `prototype` and continues in the same conversation. The user does not need to invoke another skill or start a new session. The corrected track is locked only for the current outcome.

## Default behavior

- `PROCEED` is the default. Missing details are inferred from artifacts, repository evidence, tests, logs, prior decisions, and conservative defaults.
- Odd or impossible wording is normalized to the nearest useful testable outcome.
- When only the requested method is invalid, Heading replaces that method and continues toward the legitimate goal.
- `ASK` is one focused question only when evidence cannot resolve a choice that materially changes the result.
- `REFUSE` is reserved for an essential goal with no safe, authorized, honest, useful form.
- Missing tools or platforms downgrade only the affected proof to `NOT_PROVEN`. Execution becomes `BLOCKED` only when inspection finds no faithful useful work.

## Roles

```text
Lead       GPT-5.6 Sol high    routing, scope, integration, final judgment
Planner    GPT-5.6 Luna max    read-only discovery, research, planning
Executor   GPT-5.6 Luna max    sole product writer
Reviewer   GPT-5.6 Terra high  independent read-only review
Architect  GPT-5.6 Terra xhigh irreducible boundary advice
```

- Only one writable outcome is active at a time.
- Implementation, accepted repair, and re-verification for one outcome stay in the same Executor thread.
- Reviewer never edits or directs Executor; it reports to Lead only.
- There is no fixed Luna/Terra quota.

## Install

Requirements: POSIX and Python 3.11 or later. Installation contains 20 files.

```bash
./verify-source-package.sh

./scripts/install.sh --dry-run
./scripts/install.sh
./scripts/install.sh --check

codex --profile heading
```

The installer is non-destructive: it never removes existing files or namespaces. Resolve any Heading namespace conflict before installing.

Heading keeps execution evidence internally, but its response detail follows the task: simple work is brief, while complex or risky work includes the evidence needed to decide. Ask for raw result fields when you need them.

See [PLAYBOOK.md](PLAYBOOK.md) for the best use of each skill.

## Distribution boundary

The distributable source is the five skills, their references, tests, installer,
and validation scripts. Installation writes into the caller's selected Codex
profile; it does not package a runtime binary or silently replace an existing
namespace. `./verify-source-package.sh` proves the deterministic source package.
Native Codex execution, model behavior, and authenticated evaluation remain
separate evidence and are not implied by source validation.
