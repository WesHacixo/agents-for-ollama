#!/usr/bin/env bash
# Detached membrane propose: generate a governed CAS return packet only.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MACOS_CAS="${MACOS_CAS_ROOT:-$HOME/Development/UltraViolet/MacOS-CAS}"
OUT_JSON="${TMPDIR:-/tmp}/detached-membrane-return.json"
HINT="${CAS_HINT:-Propose the next bounded step for detached membrane intelligence operations.}"
SOURCE_PACKET_ID="${CAS_SOURCE_PACKET_ID:-}"
ZTNA_POLICY="${ZTNA_POLICY_PATH:-$ROOT/packages/detached_membrane_sdk/policy/local_ztna_policy_v0.json}"
ZTNA_RECEIPT="${ZTNA_RECEIPT_PATH:-${TMPDIR:-/tmp}/detached-membrane-ztna-receipt.json}"
IDENTITY_REF="${MEMBRANE_AGENT_ID:-detached_membrane_agent_local}"

usage() {
  echo "Usage: $0 [--hint \"...\"] [--source-packet-id cas1_...] [--out /tmp/file.json] [--ztna-receipt /tmp/r.json]"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --hint)
      HINT="$2"
      shift 2
      ;;
    --source-packet-id)
      SOURCE_PACKET_ID="$2"
      shift 2
      ;;
    --out)
      OUT_JSON="$2"
      shift 2
      ;;
    --ztna-receipt)
      ZTNA_RECEIPT="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$SOURCE_PACKET_ID" ]]; then
  if [[ -d "$MACOS_CAS" ]]; then
    CAS1_JSON="${TMPDIR:-/tmp}/detached-membrane-cas1.json"
    (cd "$MACOS_CAS" && swift run MacOSAppCLI cas1-export --output "$CAS1_JSON" 2>/dev/null)
    SOURCE_PACKET_ID="$(python3 -c "import json; print(json.load(open('$CAS1_JSON'))['packet_id'])")"
  else
    echo "FAIL: --source-packet-id required when MacOS-CAS is unavailable." >&2
    exit 1
  fi
fi

cd "$ROOT"
export CAS_SOURCE_PACKET_ID="$SOURCE_PACKET_ID"
export CAS_EXECUTOR_PROFILE_ID="${CAS_EXECUTOR_PROFILE_ID:-python_agents_sdk}"
export CAS_HINT="$HINT"

python3 "$ROOT/scripts/ztna_decide_local.py" issue \
  --policy "$ZTNA_POLICY" \
  --identity-ref "$IDENTITY_REF" \
  --action "membrane_propose" \
  --resource "cas_return_packet" \
  --context-ref "$SOURCE_PACKET_ID" \
  --out "$ZTNA_RECEIPT" >/dev/null

uv run agents-ollama-cas-return --source-packet-id "$SOURCE_PACKET_ID" "$HINT" > "$OUT_JSON"

python3 - <<PY
import json
from pathlib import Path

packet = json.loads(Path("$OUT_JSON").read_text(encoding="utf-8"))
ztna = json.loads(Path("$ZTNA_RECEIPT").read_text(encoding="utf-8"))
if packet.get("status") != "proposed":
    raise SystemExit("FAIL: packet status must remain 'proposed'")
if packet.get("source_packet_id") != "$SOURCE_PACKET_ID":
    raise SystemExit("FAIL: source_packet_id mismatch")

packet["ztna"] = {
    "identity_ref": ztna.get("identity_ref"),
    "policy_decision_ref": ztna.get("decision_ref"),
    "decision_ttl_seconds": 900,
    "receipt_path": "$ZTNA_RECEIPT",
}
Path("$OUT_JSON").write_text(json.dumps(packet), encoding="utf-8")

summary = {
    "object": "DetachedMembraneProposalSummary",
    "packet_file": "$OUT_JSON",
    "ztna_receipt_file": "$ZTNA_RECEIPT",
    "status": packet.get("status"),
    "source_packet_id": packet.get("source_packet_id"),
    "executor_profile_id": packet.get("executor_profile_id"),
    "actions_taken_count": len(packet.get("actions_taken", [])),
    "artifacts_count": len(packet.get("artifacts", [])),
}
print(json.dumps(summary, indent=2))
PY
