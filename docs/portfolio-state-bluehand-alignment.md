# Portfolio state — Bluehand alignment (2026-06-17)

State snapshot after reconnaissance of **Atlas-CAI** `.dev` developments and **BHRT-0** Wyrm maturation posture.

**Authority:** orientation only (`projection_not_truth`) — not execution permission.

---

## Atlas-CAI: bluehand.dev surface split (accepted direction)

Source: `Atlas-CAI/docs/operations/bluehand-dev-surface-architecture-v0.md`

| Layer | Host | Posture | Role for detached membrane |
|------|------|---------|----------------------------|
| Doctrine | `blue-hand.org` | Public | Why/evidence only |
| Implement bridge | `docs.bluehand.dev` | Public (`public_safe.v1`) | Contracts/schemas/examples |
| Operate | `bluehand.dev`, `atlas.*`, `state.*`, `ops.*` | Access-gated | Machine-state + issuance |
| Runtime edge | `pim0.blue-hand.org`, `api/mcp.bluehand.dev` | mTLS + Access | DMI ingress + advisory MCP |
| Wyrm edge | `wyrm.bluehand.dev` (planned) | Access-gated | Registry/docs; local stdio alpha primary |

**Rule:** each surface links down-chain; no duplicate canonical schemas.

---

## Atlas-CAI: DMI / Nexus / PIM-0 boundary (C067)

Source: `Atlas-CAI/docs/operations/dmi-nexus-pim0-boundary-v0.md`

```text
Cloudflare edge
  → DMI membrane (PIM-0 worker)
  → MCP tunnel transport (governed execution lane — retained)
  → SecGate / Wyrm admission
  → BHRT runtime semantics
  → Supabase ledger (canonical index)
```

Hard boundaries:

- DMI may observe/validate/synthesize/project/propose
- DMI must not directly execute tools, mutate repos, or mutate canonical Supabase state
- Nexus lane (`api/mcp.bluehand.dev`) is advisory-only orientation, not PIM-0 ingress
- Canonical detached-membrane events remain on `pim0.blue-hand.org`

---

## BHRT-0: Wyrm state and expectations

Sources:

- `BHRT-0/docs/operations/remote-mcp/T1_WYRM_LOCAL_GATE.md`
- `BHRT-0/docs/wyrm_maturation/00_scope_and_status.md`
- `BHRT-0/docs/wyrm_maturation/index.json`

### Current posture

| Signal | Status |
|--------|--------|
| Wyrm maturation bundle | Active (`v2.0.0`, docs-mvp) |
| `wyrm_gate` implementation | In progress (`src/wyrm_gate/`) |
| T1 local gate design | Conditionally approved; oracles required before remote proxy |
| Remote execution | Disabled until enablement blockers pass |
| M7 competency assembly | Shipped on BHRT main (Atlas seam note) |

### Non-negotiables for our packet

1. **No execution authority by proximity** (`BHRT-AUTH-INVARIANT-001`)
2. **Advisory-only traces** (`advisory_only: true`, `execution_permitted: false`)
3. **Receipt chain** with `parent_receipt_id` lineage
4. **Lease-bound authority** for remote-origin (T1); localhost ≠ safe
5. **Catalog visible, capability dark** — list/describe ≠ invoke/actuate

---

## Packet optimization applied in this repo

To align with Atlas `.dev` + BHRT Wyrm expectations, detached membrane packets now include:

| Field / artifact | Purpose |
|------------------|---------|
| `authority_status: advisory_only` | Explicit non-actuation posture |
| `execution_permitted: false` | BHRT/Wyrm legality stamp |
| `ztna.policy_decision_ref` | Local ZTNA decision linkage |
| `layering_chain[]` | C067 layering witness |
| `BHRTDetachedMembraneProjection` (`bhrt-projection-0_2`) | BHRT receipt vocabulary bridge |
| `PIM0_EVENT_ENVELOPE_V1` thin projection | Atlas index-friendly envelope refs |
| `lane_separation` metadata | docs vs pim0 vs nexus vs wyrm boundaries |

| `wyrm_trace_ref` / `wyrm_trace_refs[]` | BHRT trace corpus linkage (derived from ZTNA decision ref) |
| `public_safe_slice_v0.json` | docs.bluehand.dev export profile contract |
| C067 witness fixture | `fixtures/detached_membrane/c067_boundary_witness_v0.json` |

New SDK surfaces:

- `derive_wyrm_trace_ref()` in `bhrt_projection.py`
- `project_bhrt_packet()` in `bhrt_projection.py`
- `emit_pim0_from_proposal()` in `pim0_emit.py`

Verify path now emits:

- `/tmp/detached-membrane-bhrt-projection.json`
- `/tmp/detached-membrane-pim0-envelope.json`
- `wyrm_trace_ref` on verification result JSON

---

## Optimization backlog (next)

| Priority | Enhancement | Status |
|----------|-------------|--------|
| P1 | Register `local.python_agents_sdk` lane in SigMem0 executor registry | **Done** (SigMem0 `registry_revision: 3`) |
| P1 | Add `wyrm_trace_ref` capture hook post-verify | **Done** (`derive_wyrm_trace_ref` + verify output) |
| P2 | Publish `public_safe` schema slice to `docs.bluehand.dev` index | **Done locally** (`public_safe_slice_v0.json` + doc) |
| P2 | Add C067 witness fixture in `fixtures/detached_membrane/` | **Done** (`c067_boundary_witness_v0.json`) |
| P3 | Optional `parent_receipt_id` chaining across multi-step membrane ops | **Done** (`receipt_chain.py`, `--chain-receipts`) |
| P3 | Atlas sibling registration for agents-for-ollama on docs index | **Done** (Atlas bridge + BHOK ATLAS seam) |
| — | Phase 8 goal verification (`14_goal_verify.py`) | **Done** |
| — | Phase 8 Max Mode lite (`15_max_mode_lite.py`) | **Done** |
| — | Portfolio verify loop (`verify_portfolio.sh`) | **Done** |
| — | Atlas portfolio digest (`atlas_portfolio_digest.sh`) | **Done** |
| — | Phase 10 cloud lane comparison doc | **Done** (`cloud-lane-comparison.md`) |
| P2 | BIS-CP0 pattern alignment (manifest checksums, layered verify) | **Done** (`detached-membrane-manifest.v1.json`, `layered_verify.py`) |
| P2 | Fixture-only governance e2e (no Ollama / MacOS-CAS) | **Done** (`membrane_governance_e2e.sh`) |
| — | BIS-CP0 alignment doc | **Done** (`portfolio-integration/bis-cp0-pattern-alignment.md`) |

---

## Operator checks

```bash
./scripts/membrane_quality_gate.sh --strict-legality
./scripts/membrane_governance_e2e.sh          # fixture-only governance loop
./scripts/verify_portfolio.sh                 # gate + e2e + unit tests + optional smoke
./scripts/membrane_ops.sh --allow-degraded   # when Ollama/Mac host available
```

Atlas oracles (sibling):

```bash
cd ~/Documents/Atlas-CAI/runtime/pim0-worker && bun run pim0:transport-gate
```

BHRT oracles (sibling):

```bash
cd ~/Development/BHRT-0 && uv run pytest tests/wyrm_gate -q
```

---

## Related docs in this repo

- [detached-membrane-ops-pack.md](detached-membrane-ops-pack.md)
- [detached-membrane-boundary-spec.md](detached-membrane-boundary-spec.md)
- [programmatic-intelligence-seams.md](programmatic-intelligence-seams.md)
