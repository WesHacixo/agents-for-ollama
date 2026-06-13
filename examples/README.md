# Examples

Runnable scripts demonstrating OpenAI Agents SDK + Ollama patterns.

| Script | Pattern | Model |
|--------|---------|-------|
| [01_basic_chat.py](01_basic_chat.py) | Minimal chat | `gemma2:2b` |
| [02_tool_calling.py](02_tool_calling.py) | Function tools | `gemma4:12b-mlx` |
| [03_global_client.py](03_global_client.py) | Global client wiring | `gemma4:12b-mlx` |
| [04_handoffs.py](04_handoffs.py) | Triage → specialist handoff | `gemma4:12b-mlx` |
| [05_agent_as_tool.py](05_agent_as_tool.py) | Orchestrator + `as_tool` | `gemma4:12b-mlx` |
| [06_session_chat.py](06_session_chat.py) | `SQLiteSession` memory | `gemma4:12b-mlx` |
| [07_structured_output.py](07_structured_output.py) | Pydantic output | `gemma4:12b-mlx` |
| [08_guardrails.py](08_guardrails.py) | Input guardrail | `gemma4:12b-mlx` |
| [09_parallel.py](09_parallel.py) | Parallel runs | `gemma2:2b` (`OLLAMA_PARALLEL_MODEL`) |
| [10_cas_return_stub.py](10_cas_return_stub.py) | CASReturnPacket stub | `gemma4:12b-mlx` |

Run pattern suite:

```bash
./scripts/test_patterns.sh
```

See [docs/agentic-patterns.md](../docs/agentic-patterns.md), [docs/cas-return-bridge.md](../docs/cas-return-bridge.md), and [docs/examples-walkthrough.md](../docs/examples-walkthrough.md).
