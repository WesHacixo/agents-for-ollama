# BIS-CP0 pattern alignment

**Status:** pattern source only — no default runtime coupling to [BIS-CP0](https://github.com/WesHacixo/BIS-CP0).

Atlas classifies BIS-CP0 as a **pattern source for BHRT** (layered gates, manifest checksums, governance e2e). This repo adopts the same *operational excellence* shapes for the **detached membrane SDK** without importing CP0 code or Bun/TypeScript runtime.

## What we borrowed

| CP0 pattern | Detached membrane analogue | Verify path |
|-------------|---------------------------|-------------|
| `spec/cp0-mathematics-stack-manifest.v1.json` | `packages/detached_membrane_sdk/spec/detached-membrane-manifest.v1.json` | `./scripts/verify_membrane_manifest.sh` |
| `bun run verify:mathematics-stack-contract` | `./scripts/refresh_membrane_manifest_checksum.sh` (after edits) | quality gate |
| Layered gate with named reasons (`gate-integration.ts`) | `evaluate_layers()` in `layered_verify.py` | `membrane_verify.sh` output `layer_reasons` |
| `bun run governance:e2e` | `./scripts/membrane_governance_e2e.sh` | portfolio verify (fixture-only) |
| `CONTEXT-PACKET.v1.json` invariants | manifest `invariants` block | manifest verify |
| Honey authority recurrence bridge | `wyrm_trace_ref` + receipt chain (BHRT lane) | `membrane_ops.sh --chain-receipts` |

## What we did **not** borrow

- CP0 mathematics stack (ontic/epistemic/causal layers) — out of scope for Python executor membrane
- BLAKE3 checksums — Python stdlib **SHA256** over canonical artifact records (documented in manifest)
- Default runtime coupling — MacOS-CAS remains the live host validator; governance e2e uses fixtures when host is absent

## Layer map (L0–L4)

```text
L0 contracts          → JSON schemas (proposal, PIM0, verification, public_safe)
L1 policy_compiler    → registry + compiled assertions + leak patterns
L2 ztna_gate          → local ZTNA issue/verify before propose
L3 host_validation    → MacOS-CAS validate-return-packet (live) or fixture ack (e2e)
L4 lineage_projection → BHRT + PIM0 emit + optional receipt chain
```

`membrane_verify.sh` emits `layer_reasons` with `layer_id`, `name`, `passed`, and `reason` for each layer — same audit ergonomics as CP0 gate integration.

## Commands

```bash
# Manifest checksum verify (included in quality gate)
./scripts/verify_membrane_manifest.sh

# After intentional manifest or artifact edits
./scripts/refresh_membrane_manifest_checksum.sh

# Fixture-only governance loop (no Ollama, no MacOS-CAS)
./scripts/membrane_governance_e2e.sh

# Full portfolio loop (gate + e2e + unit tests + optional smoke)
./scripts/verify_portfolio.sh
```

## Invariants (manifest-declared)

| ID | Rule |
|----|------|
| `INV.PROPOSAL.ONLY` | `status=proposed`, `execution_permitted=false` |
| `INV.ADVISORY.AUTHORITY` | `authority_status=advisory_only` |
| `INV.NO.HOST.APPLY` | `deviations_from_scope` includes `proposal_only:no_host_apply` |

## Related docs

- [Detached membrane boundary spec](../detached-membrane-boundary-spec.md)
- [Detached membrane ops pack](../detached-membrane-ops-pack.md)
- [Portfolio state (Bluehand alignment)](../portfolio-state-bluehand-alignment.md)
- [MacOS-CAS integration](macos-cas.md)
