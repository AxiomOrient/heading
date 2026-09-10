# Heading 0.5.0

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

The five product tracks (`prototype`, `build`, `sweep`, `grow`, and `maintain`) are eligible for implicit invocation: describe the work naturally and Codex can choose the matching track from its description. Use `$heading-…` to request a starting track; Heading still corrects it when the request and evidence show another track fits. `$heading-orchestrate` is deliberately explicit-only because delegation is valid only after an outcome and its proof are locked.

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

## Roles and task-based models

Role controls authority; task evidence selects the model. The optional Lead profile pins the host-compatible GPT-5.6 Luna at low effort and supplies Luna high subagent defaults. A skill alone does not switch the current chat model.

| Work shape | Candidate request |
| --- | --- |
| Deterministic preflight or mechanical inspection | Direct tools; no model request |
| Fixed extraction with a strong oracle | GPT-5.6 Luna `high` |
| Bounded local evidence / broad or weak-oracle exploration | Luna `high` / Terra `medium`; evidence capsule required |
| Clear implementation with a strong oracle | GPT-5.6 Terra `medium` |
| Cross-boundary decision or unknown shape | GPT-6 Astra `low` |
| Critical risk, including irreversible high-impact work | Astra `high` |

Luna defaults to high, with xhigh/max allowed upfront; Terra defaults to medium, with high allowed. Luna max is already authorized and needs no extra approval. Sol is excluded from active routing. Select Astra `high`/`xhigh` upfront when complexity warrants it, with `astraEffort`, `effortReason`, and `effortEvidence`; no cheap failed attempt is required. Astra `max` and `ultra` require their exceptional budget contracts and host support. The optional profile uses GPT-5.6 Luna low as a host-compatible baseline, defaults children to Luna high, and caps them at two; it does not alter an existing session.

Every 0.5.0 packet declares a work `shape` and uses the closed current packet schema. The benchmark plan contains only current route keys. These are candidate defaults, not a benchmark-proven optimum. `Light` is the UI label for `low`; use exact model IDs and permitted effort values from the [versioned policy](plugins/heading/skills/heading-orchestrate/references/model-policy.json).

Lead owns acceptance; Planner, Reviewer and Architect are read-only; Executor is the sole delegated writer. A fresh Reviewer checks material changes and reports only to Lead. Role files intentionally omit model and effort: current Codex custom-role values would otherwise override dispatch. Supply both settings per task and separate requested settings from actual host metadata. Missing evidence is `modelEscalation: NOT_PROVEN`, not successful model switching; direct deterministic work is `NOT_APPLICABLE` rather than a hidden model call.

Preserve the same Executor for one outcome while the requested route can be honored. A required route change that cannot happen in place needs an exact-candidate checkpoint, an observed stop of the old writer and its processes, then one replacement writer. Missing optional delegation does not block a separately declared direct lane; never silently substitute a required route or weaken permissions.

Use zero scouts for exact tool lookups, one authorized scout for useful synthesis, and at most two for independent questions. Use `fork_turns="none"` with a self-contained packet. Each returns a bounded [evidence capsule](plugins/heading/skills/heading-orchestrate/references/EVIDENCE-CAPSULE.md), never raw context, write authority, or final acceptance.

See [routing and task packets](plugins/heading/skills/heading-orchestrate/references/MODEL-ROUTING.md), [dated official research](plugins/heading/skills/heading-orchestrate/references/RESEARCH-2026-09-10.md), and the [unexecuted benchmark plan](evals/route-benchmark-plan.json).

## Install as a plugin

The primary distribution is the plugin at `plugins/heading/`. It has both the portable Agent Plugins `plugin.json` and the Codex `.codex-plugin/plugin.json`; both manifests point at the same six skill folders.

```bash
./verify-source-package.sh
python3 -B scripts/smoke-plugin-install.py

codex plugin marketplace add /absolute/path/to/heading
codex plugin add heading@heading
codex plugin list --json
```

For a Git checkout, replace the local path with `AxiomOrient/heading --ref main`. Restart the desktop app after adding a repo marketplace, choose **Heading Plugins**, and install **Heading**. The repository marketplace is `.agents/plugins/marketplace.json`; it resolves `./plugins/heading` relative to the repository root.

## Optional execution profile

Requirements: POSIX and Python 3.11 or later. The optional profile installation contains 5 files and never copies plugin skill folders into a global skill namespace.

Use this section only when you intentionally want the separate local `heading` runtime profile. It is not required to install, discover, or implicitly invoke the plugin skills.

```bash
./scripts/install.sh --dry-run
./scripts/install.sh
./scripts/install.sh --check

codex --profile heading
```

This profile is a task-stage runtime choice, not the plugin distribution mechanism. Plugin users do not need to install it: the five product skills work from the installed plugin alone. Its installer is non-destructive: it never removes existing files or namespaces, and it never copies skill folders into a second global namespace.

Heading keeps execution evidence internally, but its response detail follows the task: simple work is brief, while complex or risky work includes the evidence needed to decide. Ask for raw result fields when you need them.

See [PLAYBOOK.md](PLAYBOOK.md) for the best use of each skill.

## Delegation boundary

Use `$heading-orchestrate` only after one of the five tracks locks the outcome and proof. It has three explicit lanes: direct work, an observed native role, or a user-authorized user-visible task. It never silently substitutes a requested model, role, reviewer, write boundary, or task surface. A missing runtime fact is `NOT_PROVEN`, not a completed delegated result. An unavailable optional delegation path does not block bounded direct work unless the user specifically required that unavailable lane.

## Distribution boundary

The distributable source is `plugins/heading/`: the six skills, their references, and the portable/Codex manifests. `plugin.json` is the portable Agent Plugins manifest; `.codex-plugin/plugin.json` is the Codex manifest; both identify the same `heading` base release and the Codex manifest alone points to `./skills/`. A local Codex cachebuster may add a `+codex.*` suffix to the Codex manifest without changing the portable release. `runtime/heading/` contains the separate optional profile and role templates. The repository marketplace supports local and team testing; public directory submission remains a separate publisher review step. The optional profile installer writes into the caller's selected Codex profile and does not replace the plugin package.

`./verify-source-package.sh` proves the deterministic source package and both manifest contracts. `scripts/smoke-plugin-install.py` separately proves local marketplace registration, installation, enabled state, and cached-manifest equivalence in an isolated Codex home. A fresh interactive chat is still required to observe stochastic implicit selection; native model behavior, authenticated evaluation, and public-directory approval remain separate evidence.

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

## Upgrading an existing installation

The source is upgraded; your account and local installation are not modified by this ZIP. The non-destructive installer rejects differing existing managed files rather than overwriting them. Stage into fresh explicit roots, inspect the five profile/role files, preserve your local edits, stop active writers, and deliberately replace only the reviewed managed files. Do not delete the entire Codex home. Old role files with model keys defeat task-level routing.

```bash
STAGE="$(mktemp -d)"
./scripts/install.sh --dry-run --codex-home "$STAGE/codex"
./scripts/install.sh --codex-home "$STAGE/codex"
./scripts/install.sh --check --codex-home "$STAGE/codex"
```

Keep staging outside the verified source tree and inspect it before touching the live installation. No automatic migration or destructive force option is introduced.

## Canonical documents

- [Identity and evolution](IDENTITY_AND_EVOLUTION.md): identity, invariants and permitted change.
- [Specification](SPEC.md) · [Architecture](ARCHITECTURE.md): contracts and authoritative owners.
- [Analysis](ANALYSIS.md) · [Implementation status](IMPLEMENTATION_STATUS.md): observed defects, changes and remaining proof.
- [Validation](VALIDATION.md) · [Plan](PLAN.md) · [Routing decision](docs/adr/0001-task-based-model-routing.md).
