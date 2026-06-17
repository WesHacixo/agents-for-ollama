#!/usr/bin/env bash
# Fixture-only governance e2e: manifest → policy → ztna → layered verify → projection.
# No Ollama or MacOS-CAS required (CP0 governance:e2e analogue).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== membrane governance e2e (fixture-only) =="
echo "-- compile policy"
./scripts/compile_membrane_policy.sh

echo "-- verify manifest checksums"
./scripts/verify_membrane_manifest.sh

echo "-- verify policy assertions"
./scripts/verify_membrane_policy.sh

echo "-- leak gate"
./scripts/check_membrane_leaks.sh

echo "-- fixture governance loop"
PYTHONPATH=packages/detached_membrane_sdk python3 -c "from detached_membrane_sdk.governance_e2e import main; raise SystemExit(main())"

echo "PASS: membrane governance e2e complete."
