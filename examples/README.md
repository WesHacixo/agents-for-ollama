# Examples

Runnable scripts demonstrating OpenAI Agents SDK + Ollama patterns.

| Script | Description |
|--------|-------------|
| [01_basic_chat.py](01_basic_chat.py) | Minimal chat agent (`gemma2:2b`) |
| [02_tool_calling.py](02_tool_calling.py) | Function tool agent (`gemma4:12b-mlx`) |
| [03_global_client.py](03_global_client.py) | Global `AsyncOpenAI` client pattern |

See [docs/examples-walkthrough.md](../docs/examples-walkthrough.md) for details.

```bash
uv run python examples/01_basic_chat.py
```
