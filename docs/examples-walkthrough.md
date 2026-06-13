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

## Agentic patterns (`04`–`07`)

See [agentic-patterns.md](agentic-patterns.md) for the full pattern matrix. Run all:

```bash
./scripts/test_patterns.sh
```

### `04_handoffs.py` — triage handoff

| Piece | Value |
|-------|-------|
| Model | `gemma4:12b-mlx` |
| Pattern | Triage → Researcher with `lookup_fact` tool |
| **Expected** | Answer mentions San Francisco / California |

### `05_agent_as_tool.py` — orchestrator

| Piece | Value |
|-------|-------|
| Model | `gemma4:12b-mlx` |
| Pattern | Spanish sub-agent exposed via `as_tool` |
| **Expected** | Spanish translation of the English phrase |

### `06_session_chat.py` — session memory

| Piece | Value |
|-------|-------|
| Model | `gemma4:12b-mlx` |
| Pattern | `SQLiteSession` — pronoun follow-up without re-stating city |
| **Expected** | Turn 2 answers `California` (or equivalent) |

### `07_structured_output.py` — Pydantic output

| Piece | Value |
|-------|-------|
| Model | `gemma4:12b-mlx` |
| Pattern | `output_type=LocalAgentBrief` |
| **Expected** | Printed `topic` and `summary` (requires `response_format: json_object`) |

### `08_guardrails.py` — input guardrail

| Piece | Value |
|-------|-------|
| Model | `gemma4:12b-mlx` |
| Pattern | Rule-based `@input_guardrail` tripwire |
| **Expected** | Safe hello; then `Guardrail tripped as expected` |

### `09_parallel.py` — parallel runs

| Piece | Value |
|-------|-------|
| Model | `gemma2:2b` via `OLLAMA_PARALLEL_MODEL` |
| Pattern | `asyncio.gather` on two one-word prompts |
| **Expected** | `sky='...'` and `grass='...'` |

### `10_cas_return_stub.py` — CAS return JSON

| Piece | Value |
|-------|-------|
| Model | `gemma4:12b-mlx` |
| Pattern | `build_cas_return_packet()` after agent run |
| **Expected** | Pretty-printed `CASReturnPacket` JSON |

## Shared module: `agents_ollama/`

| Module | Purpose |
|--------|---------|
| `client.py` | `OllamaSettings`, `build_ollama_client`, `build_ollama_model`, `build_agent` |
| `cas_return.py` | `build_cas_return_packet` for MacOS-CAS bridge stub |
| `cli.py` | `agents-ollama-chat`, `agents-ollama-verify` entrypoints |

Import in your own code:

```python
from agents_ollama import build_agent, configure_ollama_runtime
```

## Extending to multi-agent workflows

Handoffs, agent-as-tool, sessions, and structured output are documented in [agentic-patterns.md](agentic-patterns.md) with examples `04`–`07`.

## Suggested learning order

1. `01_basic_chat.py`
2. `02_tool_calling.py`
3. Read [configuration.md](configuration.md)
4. Read [agentic-patterns.md](agentic-patterns.md)
5. `./scripts/test_patterns.sh` (examples `04`–`07`)
6. `03_global_client.py`
7. `./scripts/verify_setup.sh`
