# Pattern verification log

Live runs of `examples/04`–`07` via `./scripts/test_patterns.sh`.

## Environment

| Field | Value |
|-------|-------|
| Date | 2026-06-13 |
| Hardware | Apple M4 Pro, 24 GB RAM |
| Model | `gemma4:12b-mlx` |
| Command | `./scripts/test_patterns.sh` |

## Results

| Example | Pattern | Result | Notes |
|---------|---------|--------|-------|
| `04_handoffs.py` | Handoffs | **PASS** | Correct bridge answer; may answer without strict handoff/tool use |
| `05_agent_as_tool.py` | Agent-as-tool | **PASS** | Spanish: `Buenos días, el agente local está trabajando.` |
| `06_session_chat.py` | Sessions | **PASS** | Turn 1: San Francisco; Turn 2: California |
| `07_structured_output.py` | Structured output | **PASS** | Requires `response_format: json_object`; minimal 2-field schema |

### Structured output learnings

1. Without `ModelSettings(extra_body={"response_format": {"type": "json_object"}})`, Gemma4 returns markdown.
2. Enum/literal fields (e.g. `confidence: Literal[...]`) often fail — model may emit `0.95` instead of `"high"`.
3. Prefer **small string-only schemas** for local models.

## How to re-verify

```bash
./scripts/test_patterns.sh
```

Update this table after Ollama or SDK upgrades.
