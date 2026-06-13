# Agent instructions — Agents for Ollama

This repo is a **reference implementation and documentation** for OpenAI Agents SDK + Ollama on macOS Apple Silicon. It is not a production service.

## Purpose

- Document verified wiring between the OpenAI Agents SDK and Ollama's OpenAI-compatible API
- Provide runnable examples and smoke tests for the maintainer's M4 Pro / 24 GB setup
- Capture model compatibility and troubleshooting knowledge

## Before making changes

1. Read [docs/README.md](docs/README.md) for doc structure.
2. Check [docs/models-macos-m4.md](docs/models-macos-m4.md) before changing default models.
3. Run `./scripts/verify_setup.sh` after changing client wiring or dependencies.

## Code conventions

- **Shared wiring** lives in `agents_ollama/client.py` — do not duplicate Ollama client setup in examples unless demonstrating an alternative pattern (see `examples/03_global_client.py`).
- **Examples** in `examples/` should be minimal, runnable, and documented in [docs/examples-walkthrough.md](docs/examples-walkthrough.md).
- **Imports** at top of file; no inline imports.
- **Tracing** must stay disabled for Ollama (`configure_ollama_runtime()` or `set_tracing_disabled(True)`).

## Default models (do not change without re-verification)

| Use case | Model |
|----------|-------|
| Tool agents | `gemma4:12b-mlx` |
| Fast chat | `gemma2:2b` |

After changing defaults, update:

- `agents_ollama/client.py` constants
- `.env.example`
- `docs/models-macos-m4.md`
- `docs/verification-log.md`

## Documentation rules

- User-facing docs go in `docs/`; keep `README.md` as a short index + quick start.
- When adding a verified model result, update the matrix in `docs/models-macos-m4.md` and log the test in `docs/verification-log.md`.
- When adding a new failure mode, add it to `docs/troubleshooting.md`.

## Dependencies

- Python ≥ 3.11, managed with **uv**
- `openai-agents`, `openai` — see `pyproject.toml`

## Commands agents should use

```bash
uv sync
./scripts/verify_setup.sh
uv run python examples/01_basic_chat.py
uv run python examples/02_tool_calling.py
uv run agents-ollama-verify
```

## Out of scope

- Cloud OpenAI API usage (no API key in this repo)
- Training or fine-tuning Ollama models
- Fixing broken custom MLX model weights (`bce-*` failures are documented, not patched here)

## Commit guidance

Use conventional commits when the user asks to commit, e.g. `docs: …`, `feat: …`, `fix: …`. Do not commit `.env` or `.venv/`.
