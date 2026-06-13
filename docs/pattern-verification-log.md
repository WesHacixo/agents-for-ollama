# Pattern verification log

Live runs of `examples/04`–`10` via `./scripts/test_patterns.sh`.

## Environment

| Field | Value |
|-------|-------|
| Date | 2026-06-13 |
| Hardware | Apple M4 Pro, 24 GB RAM |
| Model | `gemma4:12b-mlx` (parallel: `gemma2:2b`) |
| Command | `./scripts/test_patterns.sh` |

## Results

| Example | Pattern | Result | Notes |
|---------|---------|--------|-------|
| `04_handoffs.py` | Handoffs | **PASS** | Correct bridge answer |
| `05_agent_as_tool.py` | Agent-as-tool | **PASS** | Spanish translation OK |
| `06_session_chat.py` | Sessions | **PASS** | San Francisco → California |
| `07_structured_output.py` | Structured output | **PASS** | `json_object` + 2-field schema |
| `08_guardrails.py` | Input guardrail | **PASS** | Tripwire on injection phrase |
| `09_parallel.py` | Parallel | **PASS** | `sky='Blue'` `grass='Green'` |
| `10_cas_return_stub.py` | CAS return | **PASS** | Profile `python_agents_sdk` |
| `11_llm_guardrails.py` | LLM guardrail | **PASS** | Classifier `gemma2:2b` tripped injection |

### Phase 4 (MacOS-CAS subprocess)

| Check | Result |
|-------|--------|
| `validate_cas_return.sh` | **PASS** — host `accepted=true` |
| `python_agents_apply_smoke.sh` | **PASS** — `applied=true`, live subprocess |

### Structured output learnings

1. Requires `ModelSettings(extra_body={"response_format": {"type": "json_object"}})`.
2. Avoid enum/literal fields locally — use small string schemas.

### CAS return learnings

1. Default profile **`ollama_http_api`** matches MacOS-CAS `ExecutorManifold`.
2. Full host **accept** needs `CAS_SOURCE_PACKET_ID` from active `cas1-print` handoff.
3. Tag Python SDK runs via `classify:python_openai_agents_sdk` in `actions_taken`.
4. Full host **accept** verified via `./scripts/validate_cas_return.sh` (requires MacOS-CAS checkout).

## How to re-verify

```bash
./scripts/test_patterns.sh
```

Update this table after Ollama or SDK upgrades.
