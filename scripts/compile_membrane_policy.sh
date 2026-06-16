#!/usr/bin/env bash
# Compile detached membrane policy source into generated gates/assertions.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
POLICY_SRC="$ROOT/packages/detached_membrane_sdk/policy/policy_source.json"
GEN_DIR="$ROOT/packages/detached_membrane_sdk/policy/generated"

mkdir -p "$GEN_DIR"

python3 - <<PY
import json
from pathlib import Path

src = Path("$POLICY_SRC")
gen_dir = Path("$GEN_DIR")
policy = json.loads(src.read_text(encoding="utf-8"))

forbidden_terms = policy.get("forbidden_imports", []) + policy.get("forbidden_markers", [])
(gen_dir / "leak_patterns.txt").write_text("|".join(forbidden_terms), encoding="utf-8")

schema_constraints = {
    "policy_id": policy["policy_id"],
    "schema_assertions": policy.get("schema_assertions", {}),
}
(gen_dir / "schema_constraints.json").write_text(
    json.dumps(schema_constraints, indent=2), encoding="utf-8"
)

verification_assertions = {
    "policy_id": policy["policy_id"],
    "required_contracts": policy.get("required_contracts", []),
    "forbidden_imports": policy.get("forbidden_imports", []),
    "forbidden_markers": policy.get("forbidden_markers", []),
}
(gen_dir / "verification_assertions.json").write_text(
    json.dumps(verification_assertions, indent=2), encoding="utf-8"
)

print(f"Compiled policy: {policy['policy_id']}")
print(f"Generated: {gen_dir / 'leak_patterns.txt'}")
print(f"Generated: {gen_dir / 'schema_constraints.json'}")
print(f"Generated: {gen_dir / 'verification_assertions.json'}")
PY
