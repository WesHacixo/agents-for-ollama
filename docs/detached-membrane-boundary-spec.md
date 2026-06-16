# Detached membrane boundary spec

Short, enforceable spec for incubating detached membrane work in this repo while preserving clean extraction into Wyrm.

---

## Incubation decision

`agents-for-ollama` remains the **research lane**.
`packages/detached_membrane_sdk/` is the **extractable membrane core**.

Non-negotiable: membrane core stays contract-first and repo-agnostic.

---

## Module boundary (required)

Core package path:

- `packages/detached_membrane_sdk/detached_membrane_sdk/`

Stable interfaces only:

- `envelope_adapter.py` → `adapt_event_envelope()` (`PIM0_EVENT_ENVELOPE_V1`)
- `proposal_emitter.py` → `emit_proposal_packet()` (proposal packet schema)
- `verification_bridge.py` → `bridge_verification_result()` (verification schema)
- `receipt_formatter.py` → `format_receipt()` (operator receipt string)

Contracts:

- `packages/detached_membrane_sdk/contracts/pim0_event_envelope_v1.json`
- `packages/detached_membrane_sdk/contracts/proposal_packet_schema.json`
- `packages/detached_membrane_sdk/contracts/verification_result_schema.json`

Research-only assets must remain outside core package (`scripts/`, `examples/`, repo docs).

---

## Compatibility contract v1

Required schemas:

1. `PIM0_EVENT_ENVELOPE_V1`
2. Proposal packet schema (`CASReturnPacket`, `status=proposed`)
3. Verification result schema (`DetachedMembraneVerificationResult`)
4. Local ZTNA decision receipt schema (`LocalZTNADecisionReceipt`, script-enforced)

Required fixtures:

- `fixtures/detached_membrane/atlas_endpoint_shape.json`
- `fixtures/detached_membrane/macos_validator_ack_shape.json`

---

## Portability gates (must pass before “extractable”)

1. **No repo-local imports in core**
   - Core package must not import `agents_ollama` or scripts.
2. **Deterministic fixtures pass**
   - `tests/test_detached_membrane_sdk.py` green.
3. **Atlas shape compatibility**
   - Envelope fixture validates expected Atlas endpoint shape.
4. **MacOS-CAS validator compatibility**
   - Ack fixture bridges cleanly into verification schema.
5. **Export command works**
   - `scripts/export_detached_membrane.sh` creates standalone bundle.
6. **Leak gate passes**
   - `scripts/check_membrane_leaks.sh` reports no authority/import leakage.
7. **Policy assertions pass**
   - `scripts/verify_membrane_policy.sh` confirms generated policy constraints match live contracts.
8. **Local ZTNA gate passes**
   - `scripts/ztna_decide_local.py issue/verify` confirms action/resource/context identity checks.

---

## Extraction checklist

Before lift-out:

- [ ] Core interfaces unchanged or version-bumped.
- [ ] Contract schemas updated and reviewed.
- [ ] Fixture tests pass in clean environment.
- [ ] Export bundle generated and smoke-tested.
- [ ] Integration consumer confirms no hidden repo assumptions.

---

## Required commands

```bash
./scripts/membrane_quality_gate.sh
PYTHONPATH=packages/detached_membrane_sdk python3 -m unittest -v tests/test_detached_membrane_sdk.py
./scripts/export_detached_membrane.sh
```

If either fails, change stays experimental and does not enter membrane core.
