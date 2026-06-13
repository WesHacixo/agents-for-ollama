#!/usr/bin/env bash
# Quick environment check: Ollama reachable + Agents SDK smoke tests.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== Ollama =="
if ! curl -sf http://localhost:11434/api/tags >/dev/null; then
  echo "FAIL: Ollama is not reachable at http://localhost:11434"
  echo "Start Ollama (menu bar app or: ollama serve)"
  exit 1
fi
echo "OK: Ollama is running"

echo
echo "== Installed models (first 10) =="
curl -s http://localhost:11434/api/tags | python3 -c "
import json, sys
data = json.load(sys.stdin)
for m in data.get('models', [])[:10]:
    print(' -', m['name'])
"

echo
echo "== Agents SDK verification =="
uv run agents-ollama-verify
