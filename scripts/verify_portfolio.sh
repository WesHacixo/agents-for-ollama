#!/usr/bin/env bash
# Portfolio verify loop: TS local gate + unit tests + optional MacOS-CAS smoke.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MACOS_CAS="${MACOS_CAS_ROOT:-$HOME/Development/UltraViolet/MacOS-CAS}"
RUN_SMOKE="${PORTFOLIO_VERIFY_SMOKE:-auto}"

QUALITY_GATE_STATUS="fail"
UNIT_TESTS_STATUS="fail"
SMOKE_STATUS="skipped"

echo "== portfolio verify: membrane local gate (TS) =="
if ./scripts/membrane_local_gate.sh --strict-legality; then
  QUALITY_GATE_STATUS="pass"
else
  exit 1
fi

echo
echo "== portfolio verify: unit tests =="
if PYTHONPATH=packages/detached_membrane_sdk:. uv run python -m unittest discover -s tests -p 'test_*.py' -q; then
  UNIT_TESTS_STATUS="pass"
else
  exit 1
fi

should_smoke() {
  case "$RUN_SMOKE" in
    true|1|yes) return 0 ;;
    false|0|no) return 1 ;;
    auto)
      [[ -d "$MACOS_CAS" ]] && curl -sf http://localhost:11434/api/tags >/dev/null 2>&1
      ;;
    *) return 1 ;;
  esac
}

if should_smoke; then
  echo
  echo "== portfolio verify: python_agents_apply_smoke =="
  if ./scripts/python_agents_apply_smoke.sh; then
    SMOKE_STATUS="pass"
  else
    exit 1
  fi
else
  echo
  echo "SKIP: MacOS-CAS live smoke (set PORTFOLIO_VERIFY_SMOKE=true or start Ollama + MacOS-CAS)"
  SMOKE_STATUS="skipped_ollama_down"
fi

echo
echo "PASS: portfolio verify loop complete."

if [[ -n "${AGENTS_FOR_OLLAMA_ROOT:-}" ]] || [[ -f "$ROOT/scripts/atlas_portfolio_digest.sh" ]]; then
  echo
  echo "== portfolio digest (Atlas orientation) =="
  MEMBRANE_DIGEST_QUALITY_GATE="$QUALITY_GATE_STATUS" \
  MEMBRANE_DIGEST_UNIT_TESTS="$UNIT_TESTS_STATUS" \
  MEMBRANE_DIGEST_PYTHON_AGENTS_SMOKE="$SMOKE_STATUS" \
  MEMBRANE_DIGEST_TS_GOVERNANCE="pass" \
    "$ROOT/scripts/atlas_portfolio_digest.sh"
fi
