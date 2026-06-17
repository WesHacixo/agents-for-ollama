#!/usr/bin/env bash
# Canonical detached membrane local gate (TypeScript / Bun).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/packages/detached-membrane-governance"

if ! command -v bun >/dev/null 2>&1; then
  echo "FAIL: bun is required for membrane local gate (https://bun.sh)" >&2
  exit 1
fi

if [[ ! -d node_modules ]]; then
  bun install
fi

exec bun run membrane:local-gate "$@"
