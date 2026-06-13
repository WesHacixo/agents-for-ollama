#!/usr/bin/env bash
# End-to-end CAS return validation against MacOS-CAS (structural + host accept).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MACOS_CAS="${MACOS_CAS_ROOT:-$HOME/Development/UltraViolet/MacOS-CAS}"
CAS1_JSON="${TMPDIR:-/tmp}/agents-for-ollama-cas1.json"
RETURN_JSON="${TMPDIR:-/tmp}/agents-sdk-return.json"

if [[ ! -d "$MACOS_CAS" ]]; then
  echo "FAIL: MacOS-CAS not found at $MACOS_CAS (set MACOS_CAS_ROOT)" >&2
  exit 1
fi

echo "== Export CAS-1 handoff =="
(cd "$MACOS_CAS" && swift run MacOSAppCLI cas1-export --output "$CAS1_JSON" 2>/dev/null)

PACKET_ID="$(python3 -c "import json; print(json.load(open('$CAS1_JSON'))['packet_id'])")"
echo "source_packet_id=$PACKET_ID"

echo "== Run agents-ollama-cas-return =="
export CAS_SOURCE_PACKET_ID="$PACKET_ID"
export CAS_EXECUTOR_PROFILE_ID="${CAS_EXECUTOR_PROFILE_ID:-python_agents_sdk}"
(cd "$ROOT" && uv run agents-ollama-cas-return > "$RETURN_JSON")

echo "== MacOS-CAS validate-return-packet =="
(cd "$MACOS_CAS" && swift run MacOSAppCLI validate-return-packet --input "$RETURN_JSON" --json 2>/dev/null) | tee /dev/stderr | python3 -c "
import json, sys
ack = json.load(sys.stdin)
if ack.get('accepted'):
    print('PASS: host accepted return packet')
    sys.exit(0)
print('FAIL:', ack.get('errors', ack))
sys.exit(1)
"
