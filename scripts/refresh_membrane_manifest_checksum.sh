#!/usr/bin/env bash
# Refresh declared_checksum in detached-membrane-manifest.v1.json after intentional edits.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MANIFEST="$ROOT/packages/detached_membrane_sdk/spec/detached-membrane-manifest.v1.json"

python3 - <<PY
import sys
from pathlib import Path

sys.path.insert(0, "$ROOT/packages/detached_membrane_sdk")
from detached_membrane_sdk.manifest import refresh_declared_checksum

checksum = refresh_declared_checksum(Path("$MANIFEST"), Path("$ROOT"))
print(f"updated declared_checksum={checksum}")
PY
