# Configuration

How to connect the OpenAI Agents SDK to Ollama on macOS.

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434/v1` | **Must include `/v1`** |
| `OLLAMA_API_KEY` | `ollama` | Any non-empty string; Ollama ignores it |
| `OLLAMA_MODEL` | `gemma4:12b-mlx` | Exact name from `ollama list` |

Copy `.env.example` to `.env` and edit as needed. The shared module reads these via `OllamaSettings.from_env()`.

## Wiring pattern A — explicit model object (recommended)

Used in `agents_ollama/client.py` and `examples/01_basic_chat.py`.

```python
from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from openai import AsyncOpenAI

set_tracing_disabled(disabled=True)

client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)
model = OpenAIChatCompletionsModel(
    model="gemma4:12b-mlx",
    openai_client=client,
)

agent = Agent(
    name="LocalHelper",
    instructions="You are a helpful local-only assistant.",
    model=model,
)

result = await Runner.run(agent, "Your prompt")
print(result.final_output)
```

**Why this pattern:** No global SDK state; easy to test; clear which client and model each agent uses.

## Wiring pattern B — shared helpers

```python
from agents import Runner
from agents_ollama import build_agent, configure_ollama_runtime

configure_ollama_runtime()
agent = build_agent(model="gemma4:12b-mlx")
result = await Runner.run(agent, "Your prompt")
```

## Wiring pattern C — global default client

Used in `examples/03_global_client.py`. Matches the [official custom provider example](https://github.com/openai/openai-agents-python/blob/main/examples/model_providers/custom_example_global.py).

```python
from agents import (
    Agent,
    Runner,
    set_default_openai_api,
    set_default_openai_client,
    set_tracing_disabled,
)
from openai import AsyncOpenAI

client = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
set_default_openai_client(client, use_for_tracing=False)
set_default_openai_api("chat_completions")
set_tracing_disabled(disabled=True)

agent = Agent(
    name="Assistant",
    instructions="…",
    model="gemma4:12b-mlx",  # string model name uses the default client
)
```

**When to use:** Multiple agents sharing one Ollama endpoint and you prefer passing model names as strings.

## Required SDK settings for Ollama

| Setting | Value | Reason |
|---------|-------|--------|
| API shape | Chat Completions | Ollama implements `/v1/chat/completions`, not the Responses API |
| Tracing | Disabled | Ollama cannot receive OpenAI trace exports |
| `base_url` | `…/v1` | Omitting `/v1` breaks routing |

Pattern A sets tracing off explicitly. Pattern C also calls `set_default_openai_api("chat_completions")` because the SDK defaults to the Responses API when using string model names.

## Tool calling requirements

- The Ollama model must list **`tools`** under Capabilities (`ollama show <model>`).
- Do not attach `@function_tool` handlers to chat-only models — Ollama returns HTTP 400.
- Avoid `tool_choice="required"` unless necessary; it can cause tool loops with some local models ([SDK issue #191](https://github.com/openai/openai-agents-python/issues/191)).

## Remote Ollama (optional)

If Ollama runs on another machine:

```bash
export OLLAMA_BASE_URL="http://192.168.1.50:11434/v1"
```

Ensure the port is reachable and Ollama is bound to the network interface (see Ollama docs for `OLLAMA_HOST`).

## Package entrypoints

After `uv sync`:

| Command | Purpose |
|---------|---------|
| `uv run agents-ollama-chat [prompt] [model]` | Run a one-shot chat agent |
| `uv run agents-ollama-verify` | Chat + tool smoke tests |
