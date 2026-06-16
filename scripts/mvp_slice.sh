#!/usr/bin/env bash
# MVP slice — one command, self-explaining value demo (no ops runbook required).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ARGS=()
for arg in "$@"; do
  case "$arg" in
    --fast|--with-host|--offline-context|--json)
      ARGS+=("$arg")
      ;;
    -h|--help)
      echo "Usage: $0 [--fast] [--with-host] [--offline-context] [--json]"
      echo
      echo "  Default: taste context → Ollama agent → CAS proposal → narrative report"
      echo "  --fast:            use gemma2:2b"
      echo "  --with-host:       also run MacOS-CAS validate-return-packet"
      echo "  --offline-context: skip SigMem0 probe, use fixture"
      exit 0
      ;;
    *) echo "Unknown flag: $arg" >&2; exit 1 ;;
  esac
done

exec uv run agents-ollama-mvp "${ARGS[@]}"
