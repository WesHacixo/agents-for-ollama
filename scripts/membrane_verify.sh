#!/usr/bin/env bash
# Detached membrane verify: host-validate proposal and emit a concise verdict.
set -euo pipefail

MACOS_CAS="${MACOS_CAS_ROOT:-$HOME/Development/UltraViolet/MacOS-CAS}"
INPUT_JSON="${1:-${TMPDIR:-/tmp}/detached-membrane-return.json}"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  echo "Usage: $0 [packet.json]"
  echo "Validate a detached membrane CAS return packet with MacOS-CAS host checks."
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

ack = json.loads(Path("$ACK_JSON").read_text(encoding="utf-8"))
packet = json.loads(Path("$INPUT_JSON").read_text(encoding="utf-8"))

result = {
    "object": "DetachedMembraneVerification",
    "packet_file": "$INPUT_JSON",
    "accepted": bool(ack.get("accepted", False)),
    "errors": ack.get("errors", []),
    "status": packet.get("status"),
    "executor_profile_id": packet.get("executor_profile_id"),
}

print(json.dumps(result, indent=2))
if result["accepted"]:
    raise SystemExit(0)
raise SystemExit(1)
PY
