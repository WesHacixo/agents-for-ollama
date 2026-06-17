#!/usr/bin/env bash
# Fail-closed leak checks — delegates to TypeScript AST gate (Phase C).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/packages/detached-membrane-governance"

if ! command -v bun >/dev/null 2>&1; then
  echo "FAIL: bun required for leak AST gate" >&2
  exit 1
fi

[[ -d node_modules ]] || bun install

exec bun run membrane:leak-gate
