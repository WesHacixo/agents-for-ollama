#!/usr/bin/env bash
# Joint portfolio smoke: agents-for-ollama + MacOS-CAS Ollama harness.
set -euo pipefail

AGENTS_REPO="${AGENTS_REPO:-$HOME/Development/agents-for-ollama}"
CAS_REPO="${CAS_REPO:-$HOME/Development/UltraViolet/MacOS-CAS}"
export OLLAMA_MODEL="${OLLAMA_MODEL:-gemma4:12b-mlx}"

echo "== Joint verify (OLLAMA_MODEL=$OLLAMA_MODEL) =="
echo

echo ">> agents-for-ollama"
cd "$AGENTS_REPO"
./scripts/verify_setup.sh
echo

echo ">> MacOS-CAS operator-loop-proof"
cd "$CAS_REPO"
swift run MacOSAppCLI operator-loop-proof --json
echo

echo "Joint verification complete."
