#!/usr/bin/env bash
# Single detached membrane governance gate — delegates to TS local gate.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

exec ./scripts/membrane_local_gate.sh "$@"
