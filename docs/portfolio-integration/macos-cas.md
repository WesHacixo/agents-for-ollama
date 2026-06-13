# MacOS-CAS integration

How the **OpenAI Agents SDK + Ollama** reference repo relates to the native Mac capability host.

| Repo | Role |
| ---- | ---- |
| **agents-for-ollama** (this repo) | Python SDK wiring, verified models, examples |
| **[MacOS-CAS](https://github.com/WesHacixo/MacOS-CAS)** | Swift host — inference router, Membrane, CAS harness, MCP |

Both share the **same Ollama daemon** on the Mac. They use **different HTTP paths** for different jobs.

## API split (read this first)

| Need | Repo | Ollama endpoint |
| ---- | ---- | --------------- |
| Python agent + tools | agents-for-ollama | `POST /v1/chat/completions` |
| Mac `run_task` / harness rehearsal | MacOS-CAS | `POST /api/generate` |
| Membrane multi-turn chat | MacOS-CAS | `POST /api/chat` |
| Mac OpenAI-compatible provider | MacOS-CAS Settings | `POST /v1/chat/completions` |

The Agents SDK **requires** Chat Completions (`/v1`). MacOS-CAS native Ollama adapter does **not** replace that for tool loops.

Authoritative bridge spec (MacOS-CAS side):  
[agents-sdk-ollama-bridge-v0.1.md](https://github.com/WesHacixo/MacOS-CAS/blob/main/docs/integration/agents-sdk-ollama-bridge-v0.1.md)

## Shared model names

Use the **same** `OLLAMA_MODEL` on both repos when testing one machine:

| Task | Model (M4 Pro / 24 GB verified) |
| ---- | ------------------------------- |
| Tool agents (Python) | `gemma4:12b-mlx` |
| Fast chat smoke | `gemma2:2b` |

MacOS-CAS: `export OLLAMA_MODEL=gemma4:12b-mlx` before harness CLI.  
This repo: set in `.env` or pass as CLI arg.

See [models-macos-m4.md](../models-macos-m4.md) for the full matrix.

## Environment mapping

| agents-for-ollama | MacOS-CAS | Notes |
| ----------------- | --------- | ----- |
| `OLLAMA_BASE_URL=http://localhost:11434/v1` | `OLLAMA_HOST=http://127.0.0.1:11434` | Python needs `/v1`; Swift native does not |
| `OLLAMA_API_KEY=ollama` | _(none)_ | Dummy key for OpenAI client only |
| `OLLAMA_MODEL=gemma4:12b-mlx` | `OLLAMA_MODEL=gemma4:12b-mlx` | Exact name from `ollama list` |

## Joint verification

On the Mac host with Ollama running:

```bash
# Both repos (from agents-for-ollama)
./scripts/verify_portfolio.sh

# Or separately:
cd ~/Development/agents-for-ollama && ./scripts/verify_setup.sh
cd ~/Development/UltraViolet/MacOS-CAS
export OLLAMA_MODEL=gemma4:12b-mlx
swift run MacOSAppCLI operator-loop-proof --json
```

## When to use which

| You want… | Start in… |
| --------- | --------- |
| `@function_tool` agent loops, handoffs, SDK examples | **agents-for-ollama** |
| Native UI, MCP, CAS-1 returns, Membrane | **MacOS-CAS** |
| Document model RAM limits for Apple Silicon | **agents-for-ollama** `models-macos-m4.md` |
| Governed executor rehearsal + host apply | **MacOS-CAS** harness |

## Future: CAS subprocess executor

MacOS-CAS may eventually invoke this repo as a **`local_model` executor** that emits `CASReturnPacket` JSON. That is **not implemented** — run Python agents standalone until the bridge spec lands in MacOS-CAS.

## MacOS-CAS doc index (inference + agents)

- [Inference router v0.1](https://github.com/WesHacixo/MacOS-CAS/blob/main/docs/integration/inference-router-v0.1.md)
- [CAS agent harness v0.1](https://github.com/WesHacixo/MacOS-CAS/blob/main/docs/integration/cas-agent-harness-v0.1.md)
- [Executor lane registry v0.1](https://github.com/WesHacixo/MacOS-CAS/blob/main/docs/integration/executor-lane-registry-v0.1.md)
- [Lane strategy](https://github.com/WesHacixo/MacOS-CAS/blob/main/docs/lane-strategy.md)
- [Operator loop proof](https://github.com/WesHacixo/MacOS-CAS/blob/main/docs/operations/OPERATOR-LOOP-PROOF-2026-05-20.md)
