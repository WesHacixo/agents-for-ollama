#!/usr/bin/env bash
# Detached membrane verify: host-validate proposal and emit a concise verdict.
set -euo pipefail

MACOS_CAS="${MACOS_CAS_ROOT:-$HOME/Development/UltraViolet/MacOS-CAS}"
INPUT_JSON="${1:-${TMPDIR:-/tmp}/detached-membrane-return.json}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STRICT_LEGALITY="${STRICT_LEGALITY:-false}"
BHRTPROJ="${BHRT_PROJECTION_OUT:-${TMPDIR:-/tmp}/detached-membrane-bhrt-projection.json}"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  echo "Usage: $0 [packet.json]"
  echo "Validate a detached membrane CAS return packet with MacOS-CAS host checks."
  echo "Env: STRICT_LEGALITY=true enables additional legality assertions."
  exit 0
fi

if [[ ! -f "$INPUT_JSON" ]]; then
  echo "FAIL: input packet not found at $INPUT_JSON" >&2
  echo "Usage: $0 [packet.json]" >&2
  exit 1
fi

if [[ ! -d "$MACOS_CAS" ]]; then
  echo "FAIL: MacOS-CAS not found at $MACOS_CAS" >&2
  exit 1
fi

ACK_JSON="${TMPDIR:-/tmp}/detached-membrane-ack.json"

(cd "$MACOS_CAS" && swift run MacOSAppCLI validate-return-packet --input "$INPUT_JSON" --json 2>/dev/null) > "$ACK_JSON"

python3 - <<PY
import json
from pathlib import Path
import subprocess

ack = json.loads(Path("$ACK_JSON").read_text(encoding="utf-8"))
packet = json.loads(Path("$INPUT_JSON").read_text(encoding="utf-8"))
ztna = packet.get("ztna", {})
receipt_path = ztna.get("receipt_path")
if not receipt_path:
    raise SystemExit("FAIL: missing ztna.receipt_path in packet")
if not Path(receipt_path).exists():
    raise SystemExit(f"FAIL: ztna receipt not found at {receipt_path}")

verify_cmd = [
    "python3",
    "$ROOT/scripts/ztna_decide_local.py",
    "verify",
    "--receipt",
    receipt_path,
    "--action",
    "membrane_propose",
    "--resource",
    "cas_return_packet",
    "--context-ref",
    packet.get("source_packet_id", ""),
]
verify_proc = subprocess.run(verify_cmd, capture_output=True, text=True)
if verify_proc.returncode != 0:
    raise SystemExit("FAIL: ztna verification failed: " + verify_proc.stdout + verify_proc.stderr)

if "$STRICT_LEGALITY" == "true":
    if packet.get("status") != "proposed":
        raise SystemExit("FAIL: strict legality requires status=proposed")
    if not packet.get("source_packet_id"):
        raise SystemExit("FAIL: strict legality requires source_packet_id")
    if not packet.get("actions_taken"):
        raise SystemExit("FAIL: strict legality requires non-empty actions_taken")
    if not ztna.get("policy_decision_ref"):
        raise SystemExit("FAIL: strict legality requires policy_decision_ref")
    if ztna.get("decision_ttl_seconds", 0) <= 0:
        raise SystemExit("FAIL: strict legality requires positive decision_ttl_seconds")

result = {
    "object": "DetachedMembraneVerification",
    "packet_file": "$INPUT_JSON",
    "accepted": bool(ack.get("accepted", False)),
    "errors": ack.get("errors", []),
    "status": packet.get("status"),
    "executor_profile_id": packet.get("executor_profile_id"),
    "policy_decision_ref": ztna.get("policy_decision_ref"),
}

print(json.dumps(result, indent=2))

bhrt_projection = {
    "object": "BHRTDetachedMembraneProjection",
    "schema_version": "bhrt-projection-0_1",
    "authority": {
        "authority_class": "proposal",
        "policy_decision_ref": ztna.get("policy_decision_ref"),
    },
    "lineage": {
        "source_packet_id": packet.get("source_packet_id"),
        "return_id": packet.get("return_id"),
    },
    "coverage_snapshot": {
        "actions_taken_count": len(packet.get("actions_taken", [])),
        "artifacts_count": len(packet.get("artifacts", [])),
    },
    "state_delta_refs": packet.get("artifacts", []),
    "external_lineage_refs": [ztna.get("policy_decision_ref")],
}
Path("$BHRTPROJ").write_text(json.dumps(bhrt_projection, indent=2), encoding="utf-8")
if result["accepted"]:
    raise SystemExit(0)
raise SystemExit(1)
PY
