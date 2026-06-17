# Examples walkthrough

Annotated tour of the scripts in `examples/`.

For **how to combine** these into governed agentic software (CAS proposals, portfolio seams), see [building-agentic-software.md](building-agentic-software.md).

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

### `11_llm_guardrails.py` — classifier guardrail

| Piece | Value |
|-------|-------|
| Model | `gemma2:2b` classifier + `gemma4:12b-mlx` main |
| Pattern | LLM `@input_guardrail` before main agent |
| **Expected** | Safe prompt runs; injection tripwire on bad input |

### `12_session_checkpoint.py` — long-horizon checkpoint (Phase 6)

| Piece | Value |
|-------|-------|
| Model | `gemma4:12b-mlx` worker + checkpoint writer |
| Pattern | Multi-step tool loop → writer-only `SessionCheckpoint` → `CASReturnPacket` |
| **Expected** | Pretty-printed packet with `proposed_next_state.session_checkpoint` |

### `13_sigmem0_recall_agent.py` — SigMem0 recall tool (Phase 7)

| Piece | Value |
|-------|-------|
| Model | `gemma4:12b-mlx` |
| Pattern | `@function_tool recall_sigmem0` → live export or fixture (`wired_read_only`) |
| **Expected** | Answer grounded in recall lines; fixture works when `:8741` is down |

### `14_goal_verify.py` — goal guard before CAS return (Phase 8)

| Piece | Value |
|-------|-------|
| Model | `gemma2:2b` verifier + `gemma4:12b-mlx` worker |
| Pattern | Fast-model YES/NO on hint satisfaction before `build_cas_return_packet` |
| **Expected** | CAS JSON only when goal satisfied; exit 2 on gap |

## Shared module: `agents_ollama/`

| Module | Purpose |
|--------|---------|
| `client.py` | `OllamaSettings`, `build_ollama_client`, `build_ollama_model`, `build_agent` |
| `cas_return.py` | `build_cas_return_packet` for MacOS-CAS bridge |
| `checkpoint.py` | `write_session_checkpoint`, `build_checkpoint_cas_return` (Phase 6) |
| `sigmem0_recall.py` | `recall_sigmem0_context` — read-only recall with fixture fallback (Phase 7) |
| `goal_verify.py` | `verify_goal` — fast-model goal guard before CAS emit (Phase 8) |
| `cas_runner.py` | `run_cas_return`, `emit_cas_return` for subprocess CLI |
| `mvp_slice.py` | Self-explaining taste → propose → validate demo |
| `cli.py` | `agents-ollama-chat`, `agents-ollama-verify`, `agents-ollama-cas-return` |

Import in your own code:

```python
from agents_ollama import build_agent, configure_ollama_runtime
```

## Extending to multi-agent workflows

Handoffs, agent-as-tool, sessions, structured output, guardrails, CAS returns, session checkpoints, SigMem0 recall, and goal verification are documented in [agentic-patterns.md](agentic-patterns.md) with examples `04`–`14`.

## Suggested learning order

1. `./scripts/mvp_slice.sh --fast` — see the full methodology once ([building-agentic-software.md](building-agentic-software.md))
2. `01_basic_chat.py`
3. `02_tool_calling.py`
4. `10_cas_return_stub.py` — proposal envelope
5. Read [agentic-patterns.md](agentic-patterns.md) and run `./scripts/test_patterns.sh`
6. Read [configuration.md](configuration.md)
7. `03_global_client.py` (optional wiring style)
8. `./scripts/verify_setup.sh`
