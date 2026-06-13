# Troubleshooting

Common failures when running the OpenAI Agents SDK against Ollama on macOS.

## Ollama not reachable

**Symptom:** Connection refused to `localhost:11434`.

**Fix:**

1. Open the Ollama menu-bar app, or run `ollama serve`.
2. Confirm: `curl -s http://localhost:11434/api/tags`

## Wrong `base_url`

**Symptom:** 404 or unexpected HTML responses.

**Fix:** Use `http://localhost:11434/v1` — the `/v1` suffix is required for the OpenAI-compatible API.

```bash
export OLLAMA_BASE_URL=http://localhost:11434/v1
```

## Model not found

**Symptom:** `model 'foo' not found`

**Fix:**

```bash
ollama list
ollama pull gemma4:12b-mlx
```

Use the **exact** name from `ollama list` (including tags like `:latest` or `-mlx`).

## RAM / memory errors

**Symptom:**

```text
model requires 18.4 GiB but only 17.3 GiB are available
```

**Fix:**

- Use a smaller model (`gemma4:12b-mlx`, `gemma2:2b`).
- Quit other memory-heavy apps.
- Unload models: `ollama ps` then stop unused models.

See [models-macos-m4.md](models-macos-m4.md).

## Tools not supported (HTTP 400)

**Symptom:**

```text
registry.ollama.ai/library/gemma2:2b does not support tools
```

**Fix:** Use a model with `tools` in capabilities:

```bash
ollama show gemma4:12b-mlx | rg -i capabilities
```

Do not attach `@function_tool` to chat-only models.

## MLX runner errors (custom models)

**Symptoms:**

```text
mlx runner failed: unsupported architecture: Gemma2ForCausalLM
mlx runner failed: missing attention k projection
```

**Fix:** Custom or partially fused MLX models may not run in Ollama's MLX backend. Use official library models (`gemma4:*-mlx`, `gemma2:2b`) instead.

## Very slow first response

**Symptom:** 30–120+ seconds before first token.

**Cause:** Cold model load into memory.

**Fix:**

- Wait for the first load; subsequent requests are faster.
- Preload: `ollama run gemma4:12b-mlx` (then exit).
- Use `gemma2:2b` for quick smoke tests.

## Tool call loops / max turns

**Symptom:** Agent keeps calling the same tool until max turns.

**Fix:**

- Do not set `tool_choice="required"` unless necessary ([SDK #191](https://github.com/openai/openai-agents-python/issues/191)).
- Improve tool docstrings and agent instructions so the model knows when to stop.
- Try a different tool-capable model.

## Tracing warnings or errors

**Symptom:** Errors related to trace export or OpenAI platform.

**Fix:** Disable tracing for local-only runs:

```python
from agents import set_tracing_disabled
set_tracing_disabled(disabled=True)
```

Or call `configure_ollama_runtime()` from `agents_ollama`.

## Responses API errors

**Symptom:** Errors mentioning Responses API when using string model names on `Agent`.

**Fix:** When using the global client pattern, set chat completions explicitly:

```python
from agents import set_default_openai_api
set_default_openai_api("chat_completions")
```

Or use `OpenAIChatCompletionsModel` directly (recommended in this repo).

## Still stuck?

1. Run `./scripts/verify_setup.sh` and note which step fails.
2. Check [verification-log.md](verification-log.md) for known-good commands.
3. Compare your model to [models-macos-m4.md](models-macos-m4.md).
