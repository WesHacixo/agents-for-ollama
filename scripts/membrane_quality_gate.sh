#!/usr/bin/env bash
# Single detached membrane governance gate.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ZTNA_POLICY="${ZTNA_POLICY_PATH:-packages/detached_membrane_sdk/policy/local_ztna_policy_v0.json}"
ZTNA_RECEIPT="${TMPDIR:-/tmp}/membrane-quality-gate-ztna-receipt.json"
ZTNA_IDENTITY_REF="${ZTNA_IDENTITY_REF:-detached_membrane_agent_local}"
ZTNA_ACTION="${ZTNA_ACTION:-membrane_propose}"
ZTNA_RESOURCE="${ZTNA_RESOURCE:-cas_return_packet}"
ZTNA_CONTEXT="${ZTNA_CONTEXT:-cas1_quality_gate}"

echo "== membrane quality gate =="
echo "-- compile policy"
./scripts/compile_membrane_policy.sh

echo "-- verify policy assertions"
./scripts/verify_membrane_policy.sh

echo "-- leak gate"
./scripts/check_membrane_leaks.sh

echo "-- local ztna issue"
python3 ./scripts/ztna_decide_local.py issue \
  --policy "$ZTNA_POLICY" \
  --identity-ref "$ZTNA_IDENTITY_REF" \
  --action "$ZTNA_ACTION" \
  --resource "$ZTNA_RESOURCE" \
  --context-ref "$ZTNA_CONTEXT" \
  --out "$ZTNA_RECEIPT" >/dev/null

echo "-- local ztna verify"
python3 ./scripts/ztna_decide_local.py verify \
  --receipt "$ZTNA_RECEIPT" \
  --action "$ZTNA_ACTION" \
  --resource "$ZTNA_RESOURCE" \
  --context-ref "$ZTNA_CONTEXT"

echo "-- detached membrane sdk tests"
PYTHONPATH=packages/detached_membrane_sdk python3 -m unittest -v tests/test_detached_membrane_sdk.py

echo "PASS: membrane quality gate complete."
