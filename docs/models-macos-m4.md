# Models on macOS M4 (24 GB)

Verified model behavior on **Apple M4 Pro, 24 GB RAM, Ollama 0.30.7**, using the OpenAI Agents SDK via Ollama's OpenAI-compatible API.

Last verified: **2026-06-12**. See [verification-log.md](verification-log.md) for test commands.

## Recommended defaults

| Role | Model | Why |
|------|-------|-----|
| **Agents with tools** | `gemma4:12b-mlx` | Tool calling works; ~10 GB fits in 24 GB RAM |
| **Tool agent + thinking** | `gemma4:e4b-mlx` | Smaller Gemma4; supports `tools` + `thinking` |
| **Fast chat, no tools** | `gemma2:2b` | ~1.5 s response; smallest footprint |

Set the default in `.env`:

```bash
OLLAMA_MODEL=gemma4:12b-mlx
```

## Full matrix (installed models)

| Model | Size | Chat | Tools | Latency | Verdict |
|-------|------|------|-------|---------|---------|
| `gemma4:12b-mlx` | 10 GB | ✅ | ✅ | ~18 s | **Default for agents** |
| `gemma4:e4b-mlx` | 9.6 GB | ✅ | ✅ | ~23 s | Good alternative |
| `gemma2:2b` | 1.6 GB | ✅ | ❌ | ~1.5 s | Chat-only |
| `gemma4:26b-mlx` | 16 GB | ⚠️ | ✅ | Very slow | Loads but tight on RAM |
| `qwen3.6:27b-mlx` | 19 GB | ❌ | — | — | RAM error (18.4 GiB needed) |
| `bce-architect-fused-test:latest` | 1.5 GB | ❌ | — | — | MLX: unsupported architecture |
| `bce-architect-governance-e4b-fused-v1:latest` | 5.9 GB | ❌ | — | — | MLX: corrupt/incomplete weights |
| `bce-architect-governance-review-*` | 9.6 GB | ⚠️ | unknown | Slow | Custom; not validated for SDK |

## How to check a model yourself

```bash
# Capabilities (look for "tools")
ollama show gemma4:12b-mlx

# List installed models
ollama list

# Raw API smoke test
curl -s http://localhost:11434/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"gemma2:2b","messages":[{"role":"user","content":"OK"}]}'
```

## RAM planning on 24 GB

Ollama reports exact memory requirements in 500 errors, for example:

```text
model requires 18.4 GiB but only 17.3 GiB are available (after 512.0 MiB overhead)
```

Rules of thumb on this machine:

- Stay near **≤ 12–14 GB model size** for comfortable headroom with macOS and IDE open.
- Only one large MLX model loaded at a time.
- First request pays a **cold-load penalty** (10–30+ seconds); keep the model warm with `ollama run <model>` or a preload.

## Tool-capable vs chat-only

**Tool-capable** (`ollama show` lists `tools`):

- `gemma4:12b-mlx`
- `gemma4:e4b-mlx`
- `gemma4:26b-mlx` (if it loads)

**Chat-only** (do not attach `@function_tool`):

- `gemma2:2b` → HTTP 400: `does not support tools`

## Models to avoid for Agents SDK (today)

| Model | Problem |
|-------|---------|
| `qwen3.6:27b-mlx` | Exceeds available RAM on 24 GB host |
| Custom `bce-*` fused MLX builds | MLX runner errors; not general-purpose chat |
| Models without `tools` | Cannot run function-tool agents |

## Optional pulls (not tested in this repo)

Community tutorials often use these; they may work but are **not verified here**:

```bash
ollama pull qwen2.5:7b
ollama pull llama3.2
```

After pulling, run `./scripts/verify_setup.sh` and add a row to [verification-log.md](verification-log.md).

## MacOS-CAS alignment

These defaults are shared with the native Mac host ([MacOS-CAS](https://github.com/WesHacixo/MacOS-CAS)) when both use the same Ollama daemon:

- Set `OLLAMA_MODEL=gemma4:12b-mlx` for harness CLI and Python tool agents.
- Mac native client uses `OLLAMA_HOST` without `/v1`; this repo uses `OLLAMA_BASE_URL` **with** `/v1`.

Bridge spec: [agents-sdk-ollama-bridge-v0.1.md](https://github.com/WesHacixo/MacOS-CAS/blob/main/docs/integration/agents-sdk-ollama-bridge-v0.1.md) (MacOS-CAS) · [macos-cas.md](portfolio-integration/macos-cas.md) (this repo).
