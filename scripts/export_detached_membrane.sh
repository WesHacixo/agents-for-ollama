#!/usr/bin/env bash
# Export detached membrane SDK package + contracts for extraction.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${1:-$ROOT/dist/detached-membrane-export}"
STAMP="$(date +%Y%m%d-%H%M%S)"
EXPORT_DIR="$OUT_DIR/$STAMP"

mkdir -p "$EXPORT_DIR"

cp -R "$ROOT/packages/detached_membrane_sdk" "$EXPORT_DIR/"
cp -R "$ROOT/fixtures/detached_membrane" "$EXPORT_DIR/fixtures"
cp "$ROOT/tests/test_detached_membrane_sdk.py" "$EXPORT_DIR/"
cp "$ROOT/scripts/check_membrane_leaks.sh" "$EXPORT_DIR/"
cp "$ROOT/scripts/compile_membrane_policy.sh" "$EXPORT_DIR/"
cp "$ROOT/scripts/verify_membrane_policy.sh" "$EXPORT_DIR/"
cp "$ROOT/scripts/ztna_decide_local.py" "$EXPORT_DIR/"
cp "$ROOT/scripts/membrane_quality_gate.sh" "$EXPORT_DIR/"
cp "$ROOT/packages/detached_membrane_sdk/policy/local_ztna_policy_v0.json" "$EXPORT_DIR/"

cat > "$EXPORT_DIR/README-export.txt" <<'EOF'
Detached membrane SDK export bundle.

Contents:
- package core: packages/detached_membrane_sdk
- contract fixtures: fixtures/detached_membrane
- compatibility tests: test_detached_membrane_sdk.py

Verification (from bundle root):
./membrane_quality_gate.sh
PYTHONPATH=packages/detached_membrane_sdk python3 -m unittest -v test_detached_membrane_sdk.py
EOF

echo "Exported detached membrane bundle to: $EXPORT_DIR"
