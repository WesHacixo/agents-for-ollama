# Getting started (macOS)

This guide gets you from zero to a working local agent on **Apple Silicon macOS** using Ollama and the OpenAI Agents SDK.

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| macOS on Apple Silicon | Tested on M4 Pro; MLX models are the fast path |
| 24 GB RAM (recommended) | Smaller RAM works with smaller models |
| [Ollama](https://ollama.com/download) | Menu-bar app or CLI |
| [uv](https://docs.astral.sh/uv/) | Python env management (or use pip/venv) |
| Python 3.11+ | Repo targets 3.11–3.13 |

## 1. Install and start Ollama

1. Download Ollama for macOS and install.
2. Confirm the server is running:

```bash
curl -s http://localhost:11434/api/tags | head
```

If that fails, open the Ollama app or run `ollama serve`.

## 2. Pull a verified model

This repo was validated with models already on the host. Recommended pulls if you need them:

```bash
# Tool-capable agent (recommended default)
ollama pull gemma4:12b-mlx

# Fast chat-only smoke tests
ollama pull gemma2:2b
```

See [models-macos-m4.md](models-macos-m4.md) for the full tested matrix.

## 3. Clone and install Python deps

```bash
cd "/path/to/Agents exploration"
uv sync
```

Optional environment file:

```bash
cp .env.example .env
```

## 4. Run your first agent

**Fast chat (no tools):**

```bash
uv run python examples/01_basic_chat.py
```

**Agent with a tool:**

```bash
uv run python examples/02_tool_calling.py
```

**CLI shortcut:**

```bash
uv run agents-ollama-chat "What is a vector database?"
uv run agents-ollama-chat "Hello" gemma2:2b
```

## 5. Verify the full stack

```bash
chmod +x scripts/verify_setup.sh
./scripts/verify_setup.sh
```

This checks Ollama connectivity and runs chat + tool smoke tests.

## What happens under the hood

1. `AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama")` points the OpenAI Python client at Ollama.
2. `OpenAIChatCompletionsModel(model="…", openai_client=client)` wraps that client for the Agents SDK.
3. `Agent(…, model=…)` and `Runner.run(agent, prompt)` execute the agent loop locally.

No OpenAI API key is required. Ollama ignores the dummy `api_key` but the SDK requires a non-empty string.

## Next steps

- [Configuration](configuration.md) — env vars and alternative wiring
- [Models on macOS M4](models-macos-m4.md) — which models to use when
- [Examples walkthrough](examples-walkthrough.md) — learn from the sample scripts
- [Troubleshooting](troubleshooting.md) — if something breaks
