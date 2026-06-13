# Agentic patterns with Ollama

Patterns the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) supports that work (or can work) with **local Ollama** on Apple Silicon — especially **`gemma4:12b-mlx`** on M4 Pro / 24 GB.

**Status:** preliminary — examples `04`–`07` + `scripts/test_patterns.sh`. See [pattern-verification-log.md](pattern-verification-log.md).

## Prerequisites

| Requirement | Detail |
|-------------|--------|
| Model (tools / handoffs) | `gemma4:12b-mlx` or `gemma4:e4b-mlx` — must list `tools` in `ollama show` |
| Model (chat-only) | `gemma2:2b` — **no** tools, handoffs with tools, or structured tool loops |
| Endpoint | `OLLAMA_BASE_URL=http://localhost:11434/v1` |
| Tracing | Disabled (`configure_ollama_runtime()`) |

Run all pattern examples:

```bash
./scripts/test_patterns.sh
```

---

## Pattern matrix

| Pattern | Example | Ollama fit | Verified |
|---------|---------|------------|----------|
| Single agent + tools | `02_tool_calling.py` | ✅ Required tool model | Yes |
| Handoffs (triage → specialist) | `04_handoffs.py` | ✅ Good on Gemma4 12B | Yes |
| Agent-as-tool (orchestrator) | `05_agent_as_tool.py` | ✅ Bounded sub-runs | Yes |
| Sessions (multi-turn memory) | `06_session_chat.py` | ✅ SDK-side SQLite | Yes |
| Structured output (Pydantic) | `07_structured_output.py` | ⚠️ Needs `json_object` + small schema | Yes |
| Guardrails (input) | `08_guardrails.py` | ✅ Rule-based | Yes |
| Parallel agents | `09_parallel.py` | ✅ Use `gemma2:2b` | Yes |
| CAS return stub | `10_cas_return_stub.py` | ✅ Proposal JSON | Yes |
| Guardrails (LLM judge) | — | ⚠️ 2× latency | Planned |
| Voice | — | ❌ Not for local Ollama | Out of scope |

---

## 1. Single agent + tools (ReAct loop)

**What:** `Runner.run` loops: model → tool call → model → final text.

**When:** Any local action (files, APIs, shell stubs, Mac-adjacent helpers).

**Ollama notes:**

- Requires `/v1/chat/completions` and a tool-capable model.
- Avoid `tool_choice="required"` unless necessary ([SDK #191](https://github.com/openai/openai-agents-python/issues/191)).

**MacOS-CAS:** Complements native `/api/generate` — use Python for **tool loops**; Mac host for UI, MCP, CAS apply ([macos-cas.md](portfolio-integration/macos-cas.md)).

---

## 2. Handoffs

**What:** A triage agent delegates to specialists via `handoffs=[...]`. The receiving agent **owns** the conversation from that point.

**When:** Separate concerns (research vs writing vs support tiers).

**Example:** `examples/04_handoffs.py`

```python
researcher = Agent(
    name="Researcher",
    handoff_description="Looks up facts with tools.",
    instructions="Use lookup_fact for factual questions.",
    model=ollama_model,
    tools=[lookup_fact],
)
triage = Agent(
    name="Triage",
    instructions="Hand off factual questions to Researcher.",
    model=ollama_model,
    handoffs=[researcher],
)
```

**Ollama notes:**

- Specialists with tools need a tool-capable model.
- Keep chains **shallow** (1 hop) on local MLX models.
- Clear `handoff_description` on each specialist improves routing.

**Risks:** Wrong handoff target, extra latency (~18s per hop on 12B MLX).

---

## 3. Agent-as-tool (orchestrator)

**What:** Sub-agents exposed via `agent.as_tool(...)`; orchestrator calls them like function tools and **stays in control**.

**When:** Parallel translations, reviewer + drafter, fan-out then merge — unlike handoffs, the parent retains the thread.

**Example:** `examples/05_agent_as_tool.py`

```python
orchestrator = Agent(
    name="Orchestrator",
    instructions="Use translate_to_spanish when asked for Spanish.",
    model=ollama_model,
    tools=[
        spanish_agent.as_tool(
            tool_name="translate_to_spanish",
            tool_description="Translate text to Spanish.",
        ),
    ],
)
```

**Ollama notes:** Each tool invocation is a full sub-`Runner.run` — budget for **multiple cold-ish LLM calls**.

**vs handoffs:** Handoff = transfer ownership. Agent-as-tool = delegate subtask, keep orchestrator.

---

## 4. Sessions (conversation memory)

**What:** `SQLiteSession` stores turn history; the SDK injects prior messages on each `Runner.run`.

**When:** Local assistant with pronoun follow-ups without re-prompting full context manually.

**Example:** `examples/06_session_chat.py`

```python
from agents.memory import SQLiteSession

session = SQLiteSession("demo", "examples/.session_demo.db")
await Runner.run(agent, "What city is the Golden Gate Bridge in?", session=session)
await Runner.run(agent, "What state is it in?", session=session)
```

**Ollama notes:** Memory is **SDK-side** — no Ollama-specific config. Model must follow conversational context (Gemma4 12B is fine).

**MacOS-CAS:** Overlaps Membrane `/api/chat` for native UI; sessions are for **Python agent** continuity and CAS-bridge prototypes.

---

## 5. Structured output

**What:** `output_type=MyPydanticModel` constrains the final response shape.

**When:** Plans, checklists, JSON handoff payloads, future `CASReturnPacket`-like drafts.

**Example:** `examples/07_structured_output.py`

**Ollama notes:**

- Start with **small** schemas (2–4 fields).
- Prefer `strict_json_schema=False` if the model struggles.
- Set `ModelSettings(extra_body={"response_format": {"type": "json_object"}})` — Ollama supports this on `/v1/chat/completions`; without it, models often return markdown.
- Validate output in code; do not trust local models for complex nested JSON.

**MacOS-CAS bridge (future):** Structured agent output → validate → map to `CASReturnPacket` before host apply.

---

## 6. Guardrails

**What:** `@input_guardrail` / `@output_guardrail` functions run checks before or after the main agent. Tripwires halt execution (`InputGuardrailTripwireTriggered`).

**When:** Block prompt injection, off-topic input, or invalid output before side effects.

**Example:** `examples/08_guardrails.py` — rule-based input guardrail (no extra LLM call).

**Ollama notes:**

- Rule-based guardrails are **fast and reliable** locally.
- LLM-as-judge guardrails work but add **full extra model runs** — use sparingly on MLX.

---

## 7. Parallel agents

**What:** `asyncio.gather` on multiple `Runner.run` calls.

**When:** Independent subtasks (labels, classifiers, multi-field extraction).

**Example:** `examples/09_parallel.py` — uses `gemma2:2b` via `OLLAMA_PARALLEL_MODEL` for speed.

**Ollama notes:** One daemon serializes heavy loads; parallel helps **latency when tasks are small**, not for two 12B cold loads on 24 GB RAM.

---

## 8. CAS return stub (MacOS-CAS bridge)

**What:** Map `Runner.run` output to `CASReturnPacket` JSON via `build_cas_return_packet()`.

**When:** Prototyping Python executor returns for MacOS-CAS validate/apply pipeline.

**Example:** `examples/10_cas_return_stub.py` · [cas-return-bridge.md](cas-return-bridge.md)

**Status:** Wired via `python_agents_sdk` profile and `agents-ollama-cas-return` subprocess CLI.

---

## 9. LLM guardrails (classifier agent)

**What:** Use a small local model inside `@input_guardrail` to classify ALLOW vs BLOCK before the main agent runs.

**When:** Heuristic string checks are too brittle; you want semantic injection detection on Ollama.

**Example:** `examples/11_llm_guardrails.py` — classifier on `gemma2:2b`, main agent on `gemma4:12b-mlx`.

**Ollama notes:** Guardrail adds one extra inference per turn; use a fast model for the classifier.

---

## Anti-patterns on local Ollama

| Avoid | Why |
|-------|-----|
| Tools on `gemma2:2b` | HTTP 400 — no tool support |
| Deep handoff chains (3+) | Context loss, multi-minute runs |
| `tool_choice="required"` | Tool loops until max turns |
| 10+ tools on one agent | Weak tool selection vs cloud models |
| Voice pipeline + Ollama | SDK voice expects capable cloud stack |
| Same repo's `bce-*` broken MLX models | Documented MLX runner failures |

---

## MacOS-CAS alignment

| Agents SDK pattern | MacOS-CAS role |
|--------------------|----------------|
| Tool agent | Python executor; Mac MCP + approvals |
| Structured output | Proposal payload for CAS validate/apply |
| Sessions | Python-side continuity vs Membrane chat |
| Handoffs / orchestrator | `python_agents_sdk` subprocess profile |

Bridge spec: [MacOS-CAS agents-sdk-ollama-bridge-v0.1.md](https://github.com/WesHacixo/MacOS-CAS/blob/main/docs/integration/agents-sdk-ollama-bridge-v0.1.md)

---

## Implementation roadmap

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 0 | Tools (`02`) | ✅ Done |
| 1 | Docs + examples `04`–`07` + `test_patterns.sh` | ✅ Done |
| 2 | Guardrails + parallel (`08`–`09`) | ✅ Done |
| 3 | CAS return stub (`10`) + bridge doc | ✅ Done |
| 4 | MacOS-CAS subprocess executor + host apply | ✅ Done |
| 5 | LLM guardrails example (`11`) | ✅ Done |

---

## Related

- [Configuration](configuration.md)
- [Models (macOS M4)](models-macos-m4.md)
- [Examples walkthrough](examples-walkthrough.md)
- [SDK agent patterns (upstream)](https://github.com/openai/openai-agents-python/tree/main/examples/agent_patterns)
