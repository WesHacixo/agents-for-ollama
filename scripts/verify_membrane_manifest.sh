#!/usr/bin/env bash
# Verify detached membrane manifest artifact checksums.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MANIFEST="$ROOT/packages/detached_membrane_sdk/spec/detached-membrane-manifest.v1.json"

python3 - <<PY
import sys
from pathlib import Path

sys.path.insert(0, "$ROOT/packages/detached_membrane_sdk")
from detached_membrane_sdk.manifest import verify_manifest

ok, reasons = verify_manifest(Path("$MANIFEST"), Path("$ROOT"))
for reason in reasons:
    print(reason)
if not ok:
    raise SystemExit("FAIL: membrane manifest checksum verification failed")
print("PASS: membrane manifest checksums verified")
PY
