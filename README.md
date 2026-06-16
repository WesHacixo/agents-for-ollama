# Agents for Ollama

Reference repository for running the **OpenAI Agents SDK** against **Ollama** on **macOS Apple Silicon**.

Ollama exposes an OpenAI-compatible Chat Completions API. This repo documents the wiring, verified models, examples, and troubleshooting for a local-only agent stack — no OpenAI API key required.

## Status

| Item | Detail |
|------|--------|
| Validated hardware | Apple M4 Pro, 24 GB RAM |
| Ollama | 0.30.7 (MLX models) |
| Default agent model | `gemma4:12b-mlx` (tool calling) |
| Default chat model | `gemma2:2b` (fast, no tools) |

## Quick start

```bash
uv sync
./scripts/mvp_slice.sh    # self-explaining MVP — taste → agent → CAS proposal
./scripts/membrane_preflight.sh   # detached membrane readiness gate
./scripts/verify_setup.sh
```

## Documentation

| Guide | Description |
|-------|-------------|
| [docs/README.md](docs/README.md) | Documentation index |
| **[Building agentic software](docs/building-agentic-software.md)** | **Methodology** — governed agents, CAS proposals, portfolio seams |
| **[Detached membrane ops pack](docs/detached-membrane-ops-pack.md)** | **Agent playbook** — why and how to use preflight/propose/verify |
| **[Detached membrane boundary spec](docs/detached-membrane-boundary-spec.md)** | **Extraction boundary** — contracts and portability gates for Wyrm handoff |
| **[Detached membrane policy adoption](docs/detached-membrane-policy-adoption.md)** | **Policy ubiquity** — atlas-style stamp + local enforcement metadata |
| [Getting started](docs/getting-started.md) | Install Ollama, deps, first run |
| [Configuration](docs/configuration.md) | Env vars and SDK wiring patterns |
| [Models (macOS M4)](docs/models-macos-m4.md) | Verified model matrix |
| [Examples](docs/examples-walkthrough.md) | Walkthrough of `examples/` |
| [Troubleshooting](docs/troubleshooting.md) | Common errors and fixes |
| [Verification log](docs/verification-log.md) | Test record for this hardware |
| [MacOS-CAS integration](docs/portfolio-integration/macos-cas.md) | Native Mac host — shared Ollama, API split |
| [Agentic patterns](docs/agentic-patterns.md) | Handoffs, orchestrator, sessions, structured output |

## Portfolio context

This repo complements **[MacOS-CAS](https://github.com/WesHacixo/MacOS-CAS)** (native Swift capability host). MacOS-CAS uses Ollama `/api/generate` and `/api/chat`; this repo uses **`/v1/chat/completions`** for OpenAI Agents SDK tool loops. See [docs/portfolio-integration/macos-cas.md](docs/portfolio-integration/macos-cas.md).

## Project layout

```text
agents_ollama/          Shared client helpers, CAS runner, MVP slice
examples/               Runnable examples (01 → 11)
docs/                   Reference + building-agentic-software.md methodology
scripts/mvp_slice.sh      Self-explaining taste → propose → validate demo
scripts/membrane_*.sh     Detached membrane preflight/propose/verify ops pack
scripts/membrane_ops.sh   One-command detached membrane orchestration
scripts/verify_setup.sh Ollama + SDK smoke test
.env.example            Environment template
```

## Minimal wiring

```python
from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from openai import AsyncOpenAI

set_tracing_disabled(disabled=True)
client = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
model = OpenAIChatCompletionsModel(model="gemma4:12b-mlx", openai_client=client)
agent = Agent(name="LocalHelper", instructions="…", model=model)
result = await Runner.run(agent, "Your prompt")
```

Or use the shared module:

```python
from agents import Runner
from agents_ollama import build_agent, configure_ollama_runtime

configure_ollama_runtime()
result = await Runner.run(build_agent(), "Your prompt")
```

## CLI

```bash
uv run agents-ollama-chat "Explain vector databases briefly."
uv run agents-ollama-verify
```

## Key constraints

- **`base_url` must end with `/v1`**
- **Tool agents need tool-capable models** (`ollama show` → `tools`)
- **Disable tracing** for local-only Ollama runs
- **24 GB RAM:** prefer models ≤ ~12 GB for agents with headroom

## References

- [OpenAI Agents SDK (Python)](https://github.com/openai/openai-agents-python)
- [OpenAI Agents SDK — custom models](https://openai.github.io/openai-agents-python/models/)
- [Ollama](https://ollama.com)
- [Community walkthrough: Agents SDK + Ollama](https://medium.com/@sabaybiometzger/build-a-local-agent-system-with-the-openai-agents-sdk-and-ollama-3901e2550ed9)

## License

MIT
