# Heading 0.3.0

Heading is a portable skills plugin with five product-work tracks and one optional orchestration track.

```text
$heading-prototype  decide what should be built
$heading-build      turn accepted behavior into a complete product outcome
$heading-sweep      remove complexity while preserving behavior
$heading-grow       measure the product impact of a shipped treatment
$heading-maintain   control risk, incidents, and change in an existing system
$heading-orchestrate coordinate an already locked outcome with observable delegation
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
Reviewer   GPT-5.6 Terra high/xhigh  independent read-only review; xhigh for material risk
Architect  GPT-5.6 Terra xhigh irreducible boundary advice
```

- Only one writable outcome is active at a time.
- Implementation, accepted repair, and re-verification for one outcome stay in the same Executor thread. If delegation is unavailable, disallowed, or disproportionate for a small local change, the Lead may use declared `executionMode: DIRECT` with the same ownership and evidence lock.
- Reviewer never edits or directs Executor; it reports to Lead only.
- There is no fixed Luna/Terra quota.

## Install as a plugin

The primary distribution is the plugin at `plugins/heading/`. It has both the portable Agent Plugins `plugin.json` and the Codex `.codex-plugin/plugin.json`; both manifests point at the same six skill folders.

```bash
./verify-source-package.sh

codex plugin marketplace add /absolute/path/to/heading
codex plugin add heading@heading
codex plugin list --json
```

For a Git checkout, replace the local path with `AxiomOrient/heading --ref main`. Restart the desktop app after adding a repo marketplace, choose **Heading Plugins**, and install **Heading**. The repository marketplace is `.agents/plugins/marketplace.json`; it resolves `./plugins/heading` relative to the repository root.

## Optional execution profile

Requirements: POSIX and Python 3.11 or later. The compatibility profile installation contains 5 files and never copies plugin skill folders into a global skill namespace.

```bash
./scripts/install.sh --dry-run
./scripts/install.sh
./scripts/install.sh --check

codex --profile heading
```

This profile is a task-stage runtime choice, not the plugin distribution mechanism. Its installer is non-destructive: it never removes existing files or namespaces. `--install-legacy-skills` is an explicit compatibility escape hatch only; it can shadow an installed plugin with the same skill name and should not be used for normal plugin deployment.

Heading keeps execution evidence internally, but its response detail follows the task: simple work is brief, while complex or risky work includes the evidence needed to decide. Ask for raw result fields when you need them.

See [PLAYBOOK.md](PLAYBOOK.md) for the best use of each skill.

## Delegation boundary

Use `$heading-orchestrate` only after one of the five tracks locks the outcome and proof. It has three explicit lanes: direct work, an observed native role, or a user-authorized user-visible task. It never silently substitutes a requested model, role, reviewer, write boundary, or task surface. A missing runtime fact is `NOT_PROVEN`, not a completed delegated result. An unavailable optional delegation path does not block bounded direct work unless the user specifically required that unavailable lane.

## Distribution boundary

The distributable source is `plugins/heading/`: the six skills, their references, and the portable/Codex manifests. `runtime/heading/` contains the separate optional profile and role templates. The repository marketplace supports local and team testing; public directory submission remains a separate publisher review step. The optional profile installer writes into the caller's selected Codex profile and does not replace the plugin package.

`./verify-source-package.sh` proves the deterministic source package and both manifest contracts. Native Codex execution, model behavior, authenticated evaluation, and public-directory approval remain separate evidence.

## Third-party notices

Heading bundles no third-party source, vendored library, or external package.
Its Python source and validation scripts use the Python standard library only;
there is no project manifest declaring a third-party runtime or build-time
dependency to enumerate. The Python interpreter and the Codex host are runtime
boundaries, not redistributed dependencies. Heading does not ship either one,
and this statement does not make a claim about their separate licenses or
availability.

The source-only publication contains the plugin, references, tests, optional
profile installer, and validation scripts. No third-party package or generated
runtime artifact is bundled here.
