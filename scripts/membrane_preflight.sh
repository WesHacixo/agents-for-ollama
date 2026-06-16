#!/usr/bin/env bash
# Detached membrane preflight: verify local prerequisites before proposal runs.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MACOS_CAS="${MACOS_CAS_ROOT:-$HOME/Development/UltraViolet/MacOS-CAS}"
SIGMEM0_URL="${SIGMEM0_EXPORT_URL:-http://127.0.0.1:8741/v1/context-pack/export}"
OUT_JSON="${TMPDIR:-/tmp}/membrane-preflight.json"
ZTNA_POLICY="${ZTNA_POLICY_PATH:-$ROOT/packages/detached_membrane_sdk/policy/local_ztna_policy_v0.json}"
ZTNA_OK="false"

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "FAIL: missing required command '$cmd'" >&2
    exit 1
  fi
}

check_url() {
  local url="$1"
  curl -sS -m 2 "$url" >/dev/null 2>&1
}

require_cmd uv
require_cmd python3
require_cmd curl

cd "$ROOT"

OLLAMA_OK="false"
SIGMEM0_OK="false"
MACOS_CAS_OK="false"
PROFILE_OK="false"

if check_url "http://127.0.0.1:11434/api/tags"; then
  OLLAMA_OK="true"
fi

if check_url "$SIGMEM0_URL"; then
  SIGMEM0_OK="true"
fi

if [[ -d "$MACOS_CAS" ]]; then
  MACOS_CAS_OK="true"
  if (cd "$MACOS_CAS" && swift run MacOSAppCLI list-profiles 2>/dev/null | rg -q "python_agents_sdk"); then
    PROFILE_OK="true"
  fi
fi

if [[ -f "$ZTNA_POLICY" ]]; then
  ZTNA_OK="true"
fi

python3 - <<PY > "$OUT_JSON"
import json

result = {
    "object": "DetachedMembranePreflight",
    "schema_version": "detached-membrane-preflight-0_1",
    "checks": {
        "ollama_api": {"ok": "$OLLAMA_OK" == "true"},
        "sigmem0_context_export": {"ok": "$SIGMEM0_OK" == "true"},
        "macos_cas_root": {"ok": "$MACOS_CAS_OK" == "true"},
        "python_agents_sdk_profile": {"ok": "$PROFILE_OK" == "true"},
        "ztna_policy": {"ok": "$ZTNA_OK" == "true"},
    },
}

all_required = (
    result["checks"]["ollama_api"]["ok"]
    and result["checks"]["macos_cas_root"]["ok"]
    and result["checks"]["python_agents_sdk_profile"]["ok"]
)

result["ready_for_propose"] = all_required
result["degraded_mode_available"] = result["checks"]["ollama_api"]["ok"]

print(json.dumps(result, indent=2))
PY

cat "$OUT_JSON"

if [[ "$OLLAMA_OK" != "true" ]]; then
  echo "FAIL: Ollama API unavailable at http://127.0.0.1:11434" >&2
  exit 1
fi

if [[ "$ZTNA_OK" != "true" ]]; then
  echo "FAIL: local ZTNA policy missing at $ZTNA_POLICY" >&2
  exit 1
fi

if [[ "$MACOS_CAS_OK" != "true" || "$PROFILE_OK" != "true" ]]; then
  echo "WARN: MacOS-CAS profile checks failed; propose-only mode still possible." >&2
  exit 2
fi
