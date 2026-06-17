# Atlas sibling registration (agents-for-ollama)

Orientation slice for **docs.bluehand.dev** / Atlas bridge indexing — not execution authority.

**Authority:** `projection_not_truth` — Atlas-CAI owns canonical registration in `atlas/bridge-objects.yaml`.

---

## Role in portfolio

| Field | Value |
|-------|-------|
| Repo | [WesHacixo/agents-for-ollama](https://github.com/WesHacixo/agents-for-ollama) |
| Role | Sibling **executor reference** (Python Agents SDK + Ollama) |
| Spine status | Candidate (`aosg:repo:candidate:agents-for-ollama` in Atlas AOSG) |
| Critical path | Consumer of `sigmem0_s3_to_mac_m4_1` (**wired_read_only**) |

## Bridge objects

| Direction | Object | Notes |
|-----------|--------|-------|
| **Produces** | `cas_return_packet_v0_1` | Via `python_agents_sdk` MacOS-CAS profile |
| **Consumes** | SigMem0 context-pack export | `GET /v1/context-pack/export` (taste only) |
| **Consumes** | MacOS-CAS handoff | `CAS_SOURCE_PACKET_ID` host validation |

Atlas already registers `cas_return_packet_v0_1` with consumers `sigmem0`, `bhok`, `bhrt_0`. This repo is an additional **producer lane** for that envelope.

## Machine index fixture

Public-safe registration payload for implement-bridge indexing:

- `fixtures/atlas/sibling_index_entry_v0.json`

## Verification hooks (this repo)

```bash
./scripts/verify_portfolio.sh
./scripts/membrane_quality_gate.sh --strict-legality
```

Optional live harness (requires Ollama + MacOS-CAS):

```bash
./scripts/python_agents_apply_smoke.sh
```

## Promotion checklist (Atlas operator)

1. Human boundary review of executor vs doctrine surfaces
2. Add explicit producer note under `cas_return_packet_v0_1` in `atlas/bridge-objects.yaml` (optional)
3. Promote AOSG candidate → `atlas-workspace.yaml` entry when spine accepts sixth sibling
4. Run `make compile-atlas && make validate` in Atlas-CAI

## Related

- [macos-cas.md](macos-cas.md)
- [programmatic-intelligence-seams.md](../programmatic-intelligence-seams.md)
- [portfolio-state-bluehand-alignment.md](../portfolio-state-bluehand-alignment.md)
