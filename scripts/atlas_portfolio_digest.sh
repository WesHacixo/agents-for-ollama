#!/usr/bin/env bash
# Emit portfolio digest lines for Atlas orientation (stdout JSON).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AGENTS_ROOT="${AGENTS_FOR_OLLAMA_ROOT:-$ROOT}"
MACOS_CAS="${MACOS_CAS_ROOT:-$HOME/Development/UltraViolet/MacOS-CAS}"

python3 - <<PY
import json
import os
import subprocess
from pathlib import Path

root = Path("${AGENTS_ROOT}")
macos = Path("${MACOS_CAS}")
digest = {
    "object": "AgentsForOllamaPortfolioDigestV0",
    "authority_status": "projection_not_truth",
    "repo_root": str(root),
    "git_head": None,
    "verify": {
        "quality_gate": "unknown",
        "unit_tests": "unknown",
        "python_agents_smoke": "skipped",
    },
    "bridge_objects": ["cas_return_packet_v0_1", "python_agents_sdk_cas_return_v0"],
    "critical_path": "sigmem0_s3_to_mac_m4_1",
    "posture": "wired_read_only",
}

if (root / ".git").is_dir():
    proc = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        digest["git_head"] = proc.stdout.strip()

gate = subprocess.run(
    [str(root / "scripts/membrane_quality_gate.sh"), "--strict-legality"],
    cwd=root,
    capture_output=True,
    text=True,
)
digest["verify"]["quality_gate"] = "pass" if gate.returncode == 0 else "fail"

tests = subprocess.run(
    ["uv", "run", "python", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-q"],
    cwd=root,
    env={**os.environ, "PYTHONPATH": f"{root}/packages/detached_membrane_sdk:{root}"},
    capture_output=True,
    text=True,
)
digest["verify"]["unit_tests"] = "pass" if tests.returncode == 0 else "fail"

if macos.is_dir() and (root / "scripts/python_agents_apply_smoke.sh").is_file():
  import urllib.request
  try:
      with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2):
          smoke = subprocess.run(
              [str(root / "scripts/python_agents_apply_smoke.sh")],
              cwd=root,
              capture_output=True,
              text=True,
          )
          digest["verify"]["python_agents_smoke"] = "pass" if smoke.returncode == 0 else "fail"
  except OSError:
      digest["verify"]["python_agents_smoke"] = "skipped_ollama_down"

print(json.dumps(digest, indent=2))
PY
