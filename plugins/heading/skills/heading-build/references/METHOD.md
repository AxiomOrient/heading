# Build method

## Selection and defaults

- Infer the delivery class, entry, environment, contracts, owned boundaries, and applicable proof packs from actual code, tests, configuration, runtime paths, and prior decisions.
- Default to preserving public contracts and durable data. Implement the smallest complete vertical outcome; do not confuse scaffolding, mocks, or a terminal success marker with product behavior.
- Ask only when one unresolved public contract, destructive data decision, target platform, or authorization choice materially changes the product.
- Repair invalid methods while preserving the build goal: fix tests instead of deleting them, implement real adapters instead of fake success, use secret injection instead of hardcoding, and add dry-run or recovery instead of blind destructive change.
- Refuse only when bypass, exfiltration, destructive loss, or fabricated completion is the essential goal and no safe product outcome remains.

## Delivery classes

| Class | Primary boundary | Mandatory class proof |
|---|---|---|
| `product-slice` | user-visible path | real entry, state/effect, durable output, failure and recovery |
| `library-api` | public API or protocol | actual consumer, compatibility, errors, versioned contract |
| `service` | network or background service | request lifecycle, concurrency, restart, resource and observability behavior |
| `adapter` | external platform or provider | native or authoritative fixture, error translation, capability and version behavior |
| `data-change` | schema or durable data | dry-run, rollback, idempotency, partial failure, count or checksum |
| `delivery-infra` | build, package, deploy, or supply chain | clean or reproducible build, artifact identity, install or rollback path |

## Required lock

- `delivery_class`
- `accepted_behavior`
- `entry_and_target`
- `contract_path`
- `owned_boundaries`
- `non_goals`
- `proof_packs`
- `release_evidence`
- `canonical_workspace_identity`
- `input_output_artifact_ledger`
- `evidence_freshness`

## Protocol

1. **Map:** Bind the canonical workspace, classify inputs/outputs/proof artifacts, then trace entry, validation, state, effect, durable output, failure, and recovery.
2. **Slice:** Implement the smallest complete vertical outcome.
3. **Harden:** Select only packs triggered by the outcome; every selected pack is mandatory.
4. **Verify:** Run real or closest faithful proof; a stub, mock-only path, terminal success marker, or unobserved advertised platform is not proof.
5. **Release:** Inspect diff and artifacts, preserve contract truth, invalidate evidence made stale by changed inputs, and mark unavailable proof `NOT_PROVEN`.

## Proof packs

`contract`, `data`, `concurrency`, `security`, `resource`, `external`, `model`, `operations`. The `model` pack pins the versioned model, prompt, tool and retrieval contract plus representative repeated eval, latency, cost, and fallback.

## Result schema

- `deliveryClass`
- `contractPath`
- `proofPacks`
- `artifacts`
- `releaseState`: `READY | PARTIAL | BLOCKED`
- `residualRisk`
- `unknowns`
