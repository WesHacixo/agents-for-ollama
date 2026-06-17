#!/usr/bin/env bash
# Fixture-only governance e2e — thin wrapper around TS CLI.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/packages/detached-membrane-governance"

if ! command -v bun >/dev/null 2>&1; then
  echo "FAIL: bun required" >&2
  exit 1
fi

[[ -d node_modules ]] || bun install

echo "== membrane governance e2e (fixture-only) =="
exec bun run membrane:governance-e2e
