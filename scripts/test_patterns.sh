#!/usr/bin/env bash
# Run agentic pattern examples (04–10) against local Ollama.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export OLLAMA_MODEL="${OLLAMA_MODEL:-gemma4:12b-mlx}"
export OLLAMA_PARALLEL_MODEL="${OLLAMA_PARALLEL_MODEL:-gemma2:2b}"

if ! curl -sf http://localhost:11434/api/tags >/dev/null; then
  echo "FAIL: Ollama not reachable at http://localhost:11434"
  exit 1
fi

echo "== Pattern tests (model=$OLLAMA_MODEL parallel=$OLLAMA_PARALLEL_MODEL) =="
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
run_example "08_guardrails"
run_example "09_parallel"
run_example "10_cas_return_stub"
run_example "11_llm_guardrails"
run_example "12_session_checkpoint"
run_example "13_sigmem0_recall_agent"
run_example "14_goal_verify"

echo "All pattern examples completed."
