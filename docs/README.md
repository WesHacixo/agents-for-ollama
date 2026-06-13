# Documentation

Reference guides for running the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) against [Ollama](https://ollama.com) on **macOS Apple Silicon**.

## Start here

| Doc | What you'll learn |
|-----|-------------------|
| [Getting started](getting-started.md) | Install Ollama, Python deps, first agent run |
| [Configuration](configuration.md) | Env vars, wiring patterns, SDK settings |
| [Models on macOS M4](models-macos-m4.md) | Verified model matrix for 24 GB RAM |
| [Examples walkthrough](examples-walkthrough.md) | Annotated tour of `examples/` |
| [Troubleshooting](troubleshooting.md) | Errors we hit and how to fix them |
| [Verification log](verification-log.md) | What was tested, when, and on what hardware |

## Quick commands

```bash
uv sync
./scripts/verify_setup.sh
uv run python examples/01_basic_chat.py
uv run python examples/02_tool_calling.py
```

## Architecture (one paragraph)

Ollama exposes an **OpenAI-compatible Chat Completions API** at `http://localhost:11434/v1`. The Agents SDK does not need a special Ollama plugin — you pass an `AsyncOpenAI` client with that `base_url` into `OpenAIChatCompletionsModel`, then into `Agent`. From the SDK's perspective it is a normal chat-completions backend.
