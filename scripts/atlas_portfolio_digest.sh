#!/usr/bin/env bash
# Emit portfolio digest JSON for Atlas orientation (TypeScript).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AGENTS_ROOT="${AGENTS_FOR_OLLAMA_ROOT:-$ROOT}"

cd "$ROOT/packages/detached-membrane-governance"

if ! command -v bun >/dev/null 2>&1; then
  echo "FAIL: bun required for portfolio digest" >&2
  exit 1
fi

if [[ ! -d node_modules ]]; then
  bun install
fi

AGENTS_FOR_OLLAMA_ROOT="$AGENTS_ROOT" \
  MEMBRANE_DIGEST_QUALITY_GATE="${MEMBRANE_DIGEST_QUALITY_GATE:-unknown}" \
  MEMBRANE_DIGEST_UNIT_TESTS="${MEMBRANE_DIGEST_UNIT_TESTS:-unknown}" \
  MEMBRANE_DIGEST_PYTHON_AGENTS_SMOKE="${MEMBRANE_DIGEST_PYTHON_AGENTS_SMOKE:-skipped}" \
  MEMBRANE_DIGEST_TS_GOVERNANCE="${MEMBRANE_DIGEST_TS_GOVERNANCE:-unknown}" \
  bun src/cli.ts portfolio-digest
