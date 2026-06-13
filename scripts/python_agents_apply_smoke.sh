#!/usr/bin/env bash
# MacOS-CAS: live Python Agents SDK rehearsal + host apply smoke.
set -euo pipefail

MACOS_CAS="${MACOS_CAS_ROOT:-$HOME/Development/UltraViolet/MacOS-CAS}"
AGENTS_ROOT="${AGENTS_FOR_OLLAMA_ROOT:-$HOME/Development/agents-for-ollama}"
HINT="${CAS_HINT:-Summarize next governed harness step for MacOS-CAS}"

if [[ ! -d "$MACOS_CAS" ]]; then
  echo "FAIL: MacOS-CAS not found at $MACOS_CAS" >&2
  exit 1
fi
if [[ ! -f "$AGENTS_ROOT/pyproject.toml" ]]; then
  echo "FAIL: agents-for-ollama not found at $AGENTS_ROOT" >&2
  exit 1
fi

export AGENTS_FOR_OLLAMA_ROOT="$AGENTS_ROOT"

echo "== python-agents-rehearse-print --live =="
(cd "$MACOS_CAS" && swift run MacOSAppCLI python-agents-rehearse-print --live --hint "$HINT" 2>/dev/null) | head -20

echo
echo "== apply-return --rehearse-first --live --profile python_agents_sdk =="
(cd "$MACOS_CAS" && swift run MacOSAppCLI apply-return \
  --rehearse-first --live --profile python_agents_sdk --hint "$HINT" --json 2>/dev/null)

echo
echo "PASS: python agents subprocess rehearsal + host apply smoke completed."
