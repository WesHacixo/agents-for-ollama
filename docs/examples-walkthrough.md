# Examples walkthrough

Annotated tour of the scripts in `examples/`.

## Run any example

```bash
uv sync
uv run python examples/01_basic_chat.py
```

## `01_basic_chat.py` — minimal agent

**Goal:** Confirm SDK + Ollama chat works with the fastest model.

| Piece | Value |
|-------|-------|
| Model | `gemma2:2b` (chat-only) |
| Tools | None |
| Pattern | Shared helpers (`build_agent`, `configure_ollama_runtime`) |

**Expected:** Three bullet points about the Agents SDK in a few seconds.

## `02_tool_calling.py` — function tool

**Goal:** Confirm Ollama tool / function calling works end-to-end.

| Piece | Value |
|-------|-------|
| Model | `gemma4:12b-mlx` (must support tools) |
| Tool | `get_weather(city)` — returns fake weather |
| Pattern | Shared helpers + `@function_tool` |

**Expected:** `The weather in Tokyo is sunny and 22°C.`

If you see HTTP 400 mentioning tools, switch to a model with `tools` in `ollama show`.

## `03_global_client.py` — alternative wiring

**Goal:** Show the official "global client" pattern from the Agents SDK docs.

| Piece | Value |
|-------|-------|
| Model | `gemma4:12b-mlx` (string name on `Agent`) |
| Extra setup | `set_default_openai_client`, `set_default_openai_api("chat_completions")` |

Use this when multiple agents share one Ollama endpoint and you prefer string model names.

## Shared module: `agents_ollama/`

| Module | Purpose |
|--------|---------|
| `client.py` | `OllamaSettings`, `build_ollama_client`, `build_ollama_model`, `build_agent` |
| `cli.py` | `agents-ollama-chat`, `agents-ollama-verify` entrypoints |

Import in your own code:

```python
from agents_ollama import build_agent, configure_ollama_runtime
```

## Extending to multi-agent workflows

The same Ollama model object can back multiple agents. For handoffs, guardrails, and sessions, see the [OpenAI Agents SDK docs](https://openai.github.io/openai-agents-python/) — no Ollama-specific changes beyond model wiring and tool-capable model selection.

## Suggested learning order

1. `01_basic_chat.py`
2. `02_tool_calling.py`
3. Read [configuration.md](configuration.md)
4. `03_global_client.py`
5. `./scripts/verify_setup.sh`
