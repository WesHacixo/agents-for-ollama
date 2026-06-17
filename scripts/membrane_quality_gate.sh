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
STRICT_LEGALITY="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --strict-legality)
      STRICT_LEGALITY="true"
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [--strict-legality]"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

echo "== membrane quality gate =="
echo "-- compile policy"
./scripts/compile_membrane_policy.sh

echo "-- verify policy assertions"
./scripts/verify_membrane_policy.sh

echo "-- verify manifest checksums"
./scripts/verify_membrane_manifest.sh

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

if [[ "$STRICT_LEGALITY" == "true" ]]; then
  echo "-- strict legality checks"
  python3 - <<'PY'
from pathlib import Path
import json

adoption = Path("docs/detached-membrane-policy-adoption.md").read_text(encoding="utf-8")
if "uber_policy: detached_membrane_policy_v1@0.1.0" not in adoption:
    raise SystemExit("FAIL: missing detached membrane uber_policy stamp")

registry = Path("packages/detached_membrane_sdk/policy/policy_registry.yaml").read_text(encoding="utf-8")
if "detached_membrane_policy_v1@0.1.0" not in registry:
    raise SystemExit("FAIL: policy registry stamp mismatch")

constraints = json.loads(Path("packages/detached_membrane_sdk/policy/generated/schema_constraints.json").read_text(encoding="utf-8"))
required_lineage = constraints["schema_assertions"].get("proposal_requires_lineage", False)
if not required_lineage:
    raise SystemExit("FAIL: strict legality requires proposal lineage assertion")

print("PASS: strict legality metadata checks")
PY
fi

echo "PASS: membrane quality gate complete."
