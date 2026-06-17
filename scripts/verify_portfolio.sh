#!/usr/bin/env bash
# Portfolio verify loop: membrane gate + unit tests + optional MacOS-CAS smoke.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MACOS_CAS="${MACOS_CAS_ROOT:-$HOME/Development/UltraViolet/MacOS-CAS}"
RUN_SMOKE="${PORTFOLIO_VERIFY_SMOKE:-auto}"

echo "== portfolio verify: membrane quality gate =="
./scripts/membrane_quality_gate.sh --strict-legality

echo
echo "== portfolio verify: membrane governance e2e (fixture-only) =="
./scripts/membrane_governance_e2e.sh

echo
echo "== portfolio verify: unit tests =="
PYTHONPATH=packages/detached_membrane_sdk:. uv run python -m unittest discover -s tests -p 'test_*.py' -q

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
  ./scripts/python_agents_apply_smoke.sh
else
  echo
  echo "SKIP: MacOS-CAS live smoke (set PORTFOLIO_VERIFY_SMOKE=true or start Ollama + MacOS-CAS)"
fi

echo
echo "PASS: portfolio verify loop complete."

if [[ -n "${AGENTS_FOR_OLLAMA_ROOT:-}" ]] || [[ -f "$ROOT/scripts/atlas_portfolio_digest.sh" ]]; then
  echo
  echo "== portfolio digest (Atlas orientation) =="
  "$ROOT/scripts/atlas_portfolio_digest.sh"
fi
