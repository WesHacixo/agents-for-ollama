#!/usr/bin/env bash
# Run agentic pattern examples (04–07) against local Ollama.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export OLLAMA_MODEL="${OLLAMA_MODEL:-gemma4:12b-mlx}"

if ! curl -sf http://localhost:11434/api/tags >/dev/null; then
  echo "FAIL: Ollama not reachable at http://localhost:11434"
  exit 1
fi

echo "== Pattern tests (model=$OLLAMA_MODEL) =="
echo

run_example() {
  local name="$1"
  echo ">> $name"
  uv run python "examples/${name}.py"
  echo
}

run_example "04_handoffs"
run_example "05_agent_as_tool"
run_example "06_session_chat"
run_example "07_structured_output"

echo "All pattern examples completed."
