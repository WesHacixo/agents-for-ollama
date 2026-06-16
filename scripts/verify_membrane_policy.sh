#!/usr/bin/env bash
# Verify compiled policy assertions against live contracts.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GEN_DIR="$ROOT/packages/detached_membrane_sdk/policy/generated"
ASSERTIONS_JSON="$GEN_DIR/schema_constraints.json"
ENVELOPE_SCHEMA="$ROOT/packages/detached_membrane_sdk/contracts/pim0_event_envelope_v1.json"
PROPOSAL_SCHEMA="$ROOT/packages/detached_membrane_sdk/contracts/proposal_packet_schema.json"

if [[ ! -f "$ASSERTIONS_JSON" ]]; then
  echo "FAIL: missing compiled schema assertions. Run ./scripts/compile_membrane_policy.sh first." >&2
  exit 1
fi

python3 - <<PY
import json
from pathlib import Path

assertions = json.loads(Path("$ASSERTIONS_JSON").read_text(encoding="utf-8"))["schema_assertions"]
envelope = json.loads(Path("$ENVELOPE_SCHEMA").read_text(encoding="utf-8"))
proposal = json.loads(Path("$PROPOSAL_SCHEMA").read_text(encoding="utf-8"))

required = assertions["pim0_required_fields"]
enum_required = set(assertions["authority_class_enum"])
proposal_status = assertions["proposal_status_const"]

actual_required = set(envelope.get("required", []))
missing_required = [x for x in required if x not in actual_required]
if missing_required:
    raise SystemExit(f"FAIL: envelope schema missing required fields: {missing_required}")

actual_enum = set(envelope["properties"]["authority_class"]["enum"])
if enum_required != actual_enum:
    raise SystemExit(f"FAIL: authority_class enum mismatch: expected={sorted(enum_required)} actual={sorted(actual_enum)}")

actual_proposal_status = proposal["properties"]["status"]["const"]
if actual_proposal_status != proposal_status:
    raise SystemExit(f"FAIL: proposal status const mismatch: expected={proposal_status} actual={actual_proposal_status}")

print("PASS: compiled policy assertions match live contracts.")
PY
