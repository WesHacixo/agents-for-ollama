# Verification log

Record of live tests against the reference hardware. Re-run `./scripts/verify_setup.sh` after Ollama or SDK upgrades.

## Environment

| Field | Value |
|-------|-------|
| Date | 2026-06-12 |
| Machine | Apple M4 Pro |
| RAM | 24 GB |
| macOS | 27.0 (build 26A5353q) |
| Ollama client | 0.30.7 |
| Python | 3.13.11 (uv-managed) |
| openai-agents | 0.17.5 |
| openai | 2.41.1 |
| Endpoint | `http://localhost:11434/v1` |

## Test commands

```bash
# Chat — gemma2:2b
uv run agents-ollama-chat "Say hello in one sentence." gemma2:2b

# Chat — gemma4:12b-mlx
uv run agents-ollama-chat "Say hello in one sentence." gemma4:12b-mlx

# Chat — gemma4:e4b-mlx
uv run agents-ollama-chat "Say hello in one sentence." gemma4:e4b-mlx

# Tools — gemma4:12b-mlx
uv run python examples/02_tool_calling.py

# Tools — gemma4:e4b-mlx (via tools_test before refactor)
# Result: "The weather in Tokyo is sunny and 22°C."

# Full verify script
./scripts/verify_setup.sh
```

## Results summary

| Model | Chat | Tools | Notes |
|-------|------|-------|-------|
| `gemma4:12b-mlx` | PASS | PASS | Default recommendation |
| `gemma4:e4b-mlx` | PASS | PASS | Slightly slower chat |
| `gemma2:2b` | PASS | N/A (400 if tools attached) | Fast smoke test |
| `qwen3.6:27b-mlx` | FAIL | — | RAM: 18.4 GiB required |
| `bce-architect-fused-test:latest` | FAIL | — | MLX architecture error |
| `bce-architect-governance-e4b-fused-v1:latest` | FAIL | — | MLX weight error |
| `gemma4:26b-mlx` | PARTIAL | — | Loads (~16 GB) but very slow |

## How to re-verify

1. Update this file's date and package versions.
2. Run `./scripts/verify_setup.sh`.
3. Optionally test additional models with `uv run agents-ollama-chat "…" <model>`.
4. Update [models-macos-m4.md](models-macos-m4.md) if results change.
