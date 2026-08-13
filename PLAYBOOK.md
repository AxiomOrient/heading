# Best use of each Heading skill

## Common rule

The best request is **skill + desired outcome + one non-negotiable constraint**.

```text
$heading-<track> <desired outcome>. <critical constraint>.
```

No form is required. A wrong track is corrected before work starts.

## Prototype

Use when the product decision is unresolved.

```text
$heading-prototype Test whether on-demand sync increases trust. Do not use live customer data.
```

Modes: `desirability`, `workflow`, `feasibility`, `viability`, `generative-quality`

Best method: one risky assumption → cheapest reversible probe → representative observation → `ADOPT | REJECT | ITERATE | INCONCLUSIVE`.

## Build

Use when product meaning is accepted and implementation, integration, or release must be completed.

```text
$heading-build Complete the accepted sync path from the real iOS entry point through durable storage and recovery. Preserve existing data.
```

Modes: `product-slice`, `library-api`, `service`, `adapter`, `data-change`, `delivery-infra`

Best method: trace the real entry → implement the smallest complete vertical slice → harden only applicable risks → prove the actual target or an authoritative fixture.

## Sweep

Use for behavior-preserving deletion, consolidation, refactoring, UI simplification, or measured optimization.

```text
$heading-sweep Preserve the public API and failure semantics; remove duplicate state and wrappers.
```

Modes: `delete`, `collapse`, `refactor`, `ui`, `performance`

Best method: lock an oracle and baseline → change one complete seam → compare the same inputs → keep only proven net simplification.

## Grow

Use when a shipped product and measurable data exist.

```text
$heading-grow Improve first-task success for new users. Preserve D7 retention as a guardrail.
```

Modes: `randomized`, `sequential`, `switchback`, `holdout-rollout`, `observational`

Best method: one hypothesis and primary metric → prove instrumentation and data quality → ship a small treatment → apply the precommitted decision rule.

## Maintain

Use for incidents, defects, security, capacity, planned change, or data repair in an existing system.

```text
$heading-maintain Reproduce and fix intermittent data loss. Data preservation is the priority.
```

Modes: `incident`, `defect`, `security`, `reliability-capacity`, `planned-change`, `data-repair`

Best method: assess impact → contain active harm → fix the causal boundary → recover and regress → observe after change.

## Orchestrate

Use only after a product track locks one outcome, owner, and proof requirement.

```text
$heading-orchestrate Coordinate the locked build outcome. Keep one writer per file boundary and do not create a separate task unless I explicitly authorize it.
```

Best method: write the task packet → choose one observable lane → observe the actual worker/task identity → independently review → let the primary agent accept or reject the evidence. Native roles and user-visible tasks are optional capabilities, never a quota or silent fallback.

## Invalid requested methods

Heading preserves a legitimate goal whenever possible:

```text
"Delete tests so it passes"     → keep verification and fix the cause
"Make the metrics look good"    → use an honest measurement design
"Disable auth to fix it"        → use authorized least privilege, containment, and recovery
"The target tool is unavailable" → continue faithful work; mark only that proof NOT_PROVEN
```

It returns `REFUSE` only when the essential goal is deception, unauthorized access, or evidence destruction with no safe useful equivalent.
