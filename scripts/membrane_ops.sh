#!/usr/bin/env bash
# Detached membrane one-command workflow: preflight -> propose -> verify.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PACKET_OUT="${TMPDIR:-/tmp}/detached-membrane-return.json"
HINT="${CAS_HINT:-Propose the next bounded step for detached membrane intelligence operations.}"
SOURCE_PACKET_ID="${CAS_SOURCE_PACKET_ID:-}"
ALLOW_DEGRADED="false"

usage() {
  echo "Usage: $0 [--hint \"...\"] [--source-packet-id cas1_...] [--out /tmp/file.json] [--allow-degraded]"
  echo
  echo "Runs membrane_preflight.sh -> membrane_propose.sh -> membrane_verify.sh"
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
      PACKET_OUT="$2"
      shift 2
      ;;
    --allow-degraded)
      ALLOW_DEGRADED="true"
      shift
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

echo "== preflight =="
set +e
"$ROOT/scripts/membrane_preflight.sh"
PRE_STATUS=$?
set -e

if [[ $PRE_STATUS -eq 1 ]]; then
  echo "FAIL: preflight hard-failed; aborting." >&2
  exit 1
fi
if [[ $PRE_STATUS -eq 2 && "$ALLOW_DEGRADED" != "true" ]]; then
  echo "FAIL: preflight degraded. Re-run with --allow-degraded to continue propose-only flow." >&2
  exit 2
fi

echo
echo "== propose =="
PROPOSE_ARGS=(--hint "$HINT" --out "$PACKET_OUT")
if [[ -n "$SOURCE_PACKET_ID" ]]; then
  PROPOSE_ARGS+=(--source-packet-id "$SOURCE_PACKET_ID")
fi
"$ROOT/scripts/membrane_propose.sh" "${PROPOSE_ARGS[@]}"

echo
echo "== verify =="
"$ROOT/scripts/membrane_verify.sh" "$PACKET_OUT"

echo
echo "PASS: detached membrane workflow accepted by host."
