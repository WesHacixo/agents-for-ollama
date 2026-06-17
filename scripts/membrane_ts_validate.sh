#!/usr/bin/env bash
# Run detached-membrane-governance TypeScript validate suite (Phase A).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/packages/detached-membrane-governance"

if ! command -v bun >/dev/null 2>&1; then
  echo "FAIL: bun is required for membrane TS governance (https://bun.sh)" >&2
  exit 1
fi

if [[ ! -d node_modules ]]; then
  bun install
fi

bun run membrane:validate
