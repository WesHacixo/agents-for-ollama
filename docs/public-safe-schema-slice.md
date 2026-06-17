# Public-safe schema slice (docs.bluehand.dev)

Export profile: **`public_safe.v1`** — safe fields for public implement bridge.

## Included artifacts

| Artifact | Public fields |
|----------|---------------|
| `CASReturnPacket` | `object`, `schema_version`, `status`, `authority_status`, `execution_permitted`, `executor_profile_id`, `source_packet_id`, `layering_chain` |
| `BHRTDetachedMembraneProjection` | `object`, `schema_version`, `authority_status`, `execution_permitted`, `layering_chain`, `lane_separation`, `wyrm_trace_ref` |
| `PIM0_EVENT_ENVELOPE_V1` | thin projection fields only (`envelope_version`, `source_*`, `authority_class`, `lineage_ref`, `mutation_allowed`) |

## Excluded (never public)

- ZTNA raw receipts/tokens
- operator secrets (`service_role`, keys)
- full machine-state capsule payloads
- host apply internals
- Supabase canonical mutation details

## Machine contract

- `packages/detached_membrane_sdk/contracts/public_safe_slice_v0.json`

## Verification

```bash
./scripts/membrane_quality_gate.sh --strict-legality
```
