#!/usr/bin/env bash
# Fail-closed leak checks for detached membrane core.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CORE="$ROOT/packages/detached_membrane_sdk/detached_membrane_sdk"
GEN_DIR="$ROOT/packages/detached_membrane_sdk/policy/generated"
ASSERTIONS_JSON="$GEN_DIR/verification_assertions.json"
LEAK_PATTERNS_FILE="$GEN_DIR/leak_patterns.txt"

if [[ ! -f "$ASSERTIONS_JSON" || ! -f "$LEAK_PATTERNS_FILE" ]]; then
  echo "FAIL: compiled policy artifacts missing. Run ./scripts/compile_membrane_policy.sh first." >&2
  exit 1
fi

echo "== detached membrane leak gate =="

echo "-- import boundary check"
IMPORT_PATTERN="$(python3 - <<PY
import json
from pathlib import Path
data = json.loads(Path("$ASSERTIONS_JSON").read_text(encoding="utf-8"))
print("|".join(data.get("forbidden_imports", [])))
PY
)"
if rg -n "$IMPORT_PATTERN" "$CORE"; then
  echo "FAIL: repo-local imports detected in membrane core." >&2
  exit 1
fi

echo "-- authority leak keyword check"
LEAK_PATTERN="$(python3 - <<PY
import json
from pathlib import Path
data = json.loads(Path("$ASSERTIONS_JSON").read_text(encoding="utf-8"))
print("|".join(data.get("forbidden_markers", [])))
PY
)"
if rg -n "$LEAK_PATTERN" "$CORE"; then
  echo "FAIL: authority/direct-write leak markers detected in membrane core." >&2
  exit 1
fi

echo "-- plane separation assertion check"
python3 - <<PY
import json
from pathlib import Path

core = Path("$CORE")
data = json.loads(Path("$ASSERTIONS_JSON").read_text(encoding="utf-8"))
markers = data.get("plane_separation", {}).get("forbidden_execution_markers", [])
violations = []
for py_file in core.glob("*.py"):
    text = py_file.read_text(encoding="utf-8")
    for marker in markers:
        if marker in text:
            violations.append(f"{py_file}:{marker}")
if violations:
    raise SystemExit("FAIL: execution-plane markers detected: " + "; ".join(violations))
PY

echo "-- contract coverage check"
python3 - <<PY
import json
from pathlib import Path
root = Path("$ROOT")
data = json.loads(Path("$ASSERTIONS_JSON").read_text(encoding="utf-8"))
for rel in data.get("required_contracts", []):
    p = root / rel
    if not p.exists():
        raise SystemExit(f"FAIL: missing contract file {p}")
PY

echo "PASS: no membrane core leaks detected."
