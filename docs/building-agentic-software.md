# Building agentic software with this methodology

Practical guidance for designing, implementing, and operating **governed agentic software** on local Ollama — using the patterns, seams, and verification paths in this repository.

**Audience:** engineers and coding agents building features that reason, use tools, and propose outcomes — without treating model output as execution truth.

---

## What this methodology is

Most agent tutorials stop at “call the model in a loop.” This repo encodes a **portfolio-grade** variant:

| Principle | Meaning |
|-----------|---------|
| **Proposal-only** | Agents emit structured *proposals* (`CASReturnPacket`). A host validates and applies. |
| **Taste before think** | Ground runs in read-only context (SigMem0, fixtures, handoff packs) — labeled as context, not commands. |
| **Guardrails before side effects** | Rule-based or classifier checks run before expensive or risky tool loops. |
| **One writer per artifact** | The executor proposes; MacOS-CAS applies; SigMem0 digests through governed adapters. |
| **Projection not truth** | Atlas orients the portfolio; it does not become execution authority. |

The **reference loop** is implemented in `./scripts/mvp_slice.sh`:

```text
Taste  → read portfolio context (SigMem0 live or fixture)
Think  → OpenAI Agents SDK + Ollama tool/ReAct run
Propose → CASReturnPacket (status: proposed)
Validate → optional MacOS-CAS validate-return-packet
```

Run it first — it prints a narrative report explaining each step’s utility:

```bash
uv sync
./scripts/mvp_slice.sh              # full demo
./scripts/mvp_slice.sh --fast       # smaller model, fixture context OK
./scripts/mvp_slice.sh --with-host  # includes MacOS-CAS validation
```

---

## When to use this methodology

**Use it when:**

- Software must **act** (files, APIs, host capabilities) and you need an audit trail.
- Multiple systems (memory, host, orientation) must stay **separated by authority**.
- Local Ollama is the inference backend but **governance** matters as much as latency.
- You want agents that **integrate** with MacOS-CAS, SigMem0, or Atlas without breaching their contracts.

**Skip or simplify when:**

- You only need a chat UI with no tools and no host apply → start with `examples/01_basic_chat.py`.
- Prototypes are throwaway and never touch portfolio repos → use SDK patterns without CAS returns.
- Cloud models with managed guardrails are acceptable → this repo still documents patterns, but Ollama wiring is optional.

---

## Adoption path

### Level 0 — Local agent (no portfolio)

**Goal:** Confirm Ollama + Agents SDK wiring.

```bash
./scripts/verify_setup.sh
uv run python examples/01_basic_chat.py
uv run python examples/02_tool_calling.py
```

**Patterns:** single agent + tools ([agentic-patterns.md §1](agentic-patterns.md#1-single-agent--tools-react-loop)).

**Design rule:** Disable tracing; use `/v1` base URL; pick tool-capable models for tool loops.

---

### Level 1 — Agentic patterns (SDK catalog)

**Goal:** Handoffs, orchestration, memory, structured output, safety, parallelism.

```bash
./scripts/test_patterns.sh
```

| Need | Example | Doc |
|------|---------|-----|
| Delegate to a specialist | `04_handoffs.py` | [§2 Handoffs](agentic-patterns.md#2-handoffs) |
| Parent keeps control | `05_agent_as_tool.py` | [§3 Agent-as-tool](agentic-patterns.md#3-agent-as-tool-orchestrator) |
| Multi-turn chat | `06_session_chat.py` | [§4 Sessions](agentic-patterns.md#4-sessions-conversation-memory) |
| Typed final output | `07_structured_output.py` | [§5 Structured output](agentic-patterns.md#5-structured-output) |
| Block bad input fast | `08_guardrails.py` | [§6 Guardrails](agentic-patterns.md#6-guardrails) |
| Parallel subtasks | `09_parallel.py` | [§7 Parallel agents](agentic-patterns.md#7-parallel-agents) |
| Semantic input filter | `11_llm_guardrails.py` | [§9 LLM guardrails](agentic-patterns.md#9-llm-guardrails-classifier-agent) |

**Design rule:** Keep handoff chains shallow on local MLX; use `gemma2:2b` for classifiers and parallel fan-out; reserve `gemma4:12b-mlx` for tool-heavy work.

---

### Level 2 — Governed proposals (CAS returns)

**Goal:** Every meaningful run ends in a **host-validatable envelope**, not free-form stdout.

```bash
uv run python examples/10_cas_return_stub.py
./scripts/validate_cas_return.sh
```

**Library path:**

```python
from agents_ollama.cas_runner import run_cas_return, emit_cas_return

packet = await run_cas_return(
    hint="Propose next step for boundary pilot",
    source_packet_id="cas1_...",
    model="gemma4:12b-mlx",
)
emit_cas_return(packet)  # compact JSON on stdout for subprocess hosts
```

**CLI for MacOS-CAS subprocess:**

```bash
uv run agents-ollama-cas-return \
  --source-packet-id "$CAS_SOURCE_PACKET_ID" \
  "Your governed task hint"
```

See [cas-return-bridge.md](cas-return-bridge.md) and [portfolio-integration/macos-cas.md](portfolio-integration/macos-cas.md).

**Design rules:**

- Always set `status: proposed` — never `applied` from the agent process.
- Pass `CAS_SOURCE_PACKET_ID` matching the active handoff; host fails closed on mismatch.
- Put reasoning in `actions_taken` and deliverables in `artifacts[]` for downstream dream/trace seams.

---

### Level 3 — Portfolio integration (taste + validate)

**Goal:** Agent runs informed by SigMem0 context and validated by MacOS-CAS.

```bash
# Optional: live taste
cd ~/Development/UltraViolet/SigMem0 && uv run siglent-runtime serve   # :8741

./scripts/mvp_slice.sh --with-host
./scripts/python_agents_apply_smoke.sh   # full MacOS-CAS apply path
```

**Seam map (read-only vs propose-only):**

| System | Agent may | Agent must not |
|--------|-----------|----------------|
| **SigMem0** | Read recall, context-pack export, morning handoff | Write semantic tier, promote pieces, bypass P8 gates |
| **MacOS-CAS** | Emit `CASReturnPacket`; subprocess via `python_agents_sdk` | Apply returns itself; skip validation |
| **Atlas** | Consume orientation as *context*; cite boundaries in artifacts | Edit `capsule.state.json`; treat graph as execution truth |

Deep reference: [programmatic-intelligence-seams.md](programmatic-intelligence-seams.md).

---

## Design checklist (before you ship a feature)

Use this as a pre-merge gate for new agentic features:

1. **Input grounding** — Where does context come from? Is it labeled untrusted?
2. **Guardrails** — What blocks prompt injection or off-topic runs before tools?
3. **Output shape** — Is the final artifact a Pydantic model or `CASReturnPacket`, not markdown hope?
4. **Authority** — Who applies side effects? (Answer: host, not the agent process.)
5. **Lineage** — Does output reference `source_packet_id`, session, or recall chunk IDs?
6. **Degradation** — What happens when SigMem0 or Ollama is down? (Fixture fallback? Fail closed?)
7. **Verification** — Is there a script or example that proves the path in CI or smoke?

---

## Pattern selection guide

```text
                    ┌─────────────────────────────────┐
                    │  Need side effects on Mac/host? │
                    └────────────┬────────────────────┘
                          yes    │    no
                    ┌────────────▼────────────┐
                    │  CASReturnPacket + host │
                    │  validate/apply         │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
     ┌────────▼────────┐ ┌───────▼───────┐ ┌────────▼────────┐
     │ Multi-step tools │ │ Need memory?  │ │ One-shot answer │
     │ 02, 04–05, 11   │ │ 06 sessions   │ │ 01 or 07        │
     └─────────────────┘ └───────────────┘ └─────────────────┘

     Portfolio context? → taste via SigMem0 export or fixture (mvp_slice)
     Long horizon? → Phase 6 checkpoints (see agentic-proposal-v0.2.md)
     Quality gate? → 08/11 guardrails + future goal-verify (Phase 8)
```

---

## Model roles (M4 Pro / 24 GB reference)

| Role | Model | Examples |
|------|-------|----------|
| Tool agent / CAS runs | `gemma4:12b-mlx` | `02`, `04`–`11`, `mvp_slice`, `agents-ollama-cas-return` |
| Fast chat / parallel / classifier | `gemma2:2b` | `01`, `09`, `11` guardrail judge |
| Override | `OLLAMA_MODEL`, `OLLAMA_PARALLEL_MODEL` env vars | `scripts/test_patterns.sh` |

See [models-macos-m4.md](models-macos-m4.md) for the verified matrix.

---

## Emergent compositions (recipes)

These combine patterns from [programmatic-intelligence-seams.md](programmatic-intelligence-seams.md) — copy the shape, not ad hoc integrations.

### Morning-informed proposal

```text
SigMem0 GET /v1/context-pack/export
  → hint for agents-ollama-cas-return
  → CASReturnPacket
  → MacOS-CAS apply-return
```

### Recall-grounded ReAct

```text
POST /v1/recall (fixture or live)
  → inject into agent instructions or @function_tool
  → tool loop on gemma4:12b-mlx
  → CAS return with artifact refs to citation IDs
```

### Coherence-driven smoke

```text
Atlas coherence: fail
  → operator runs python_agents_apply_smoke.sh
  → Mac commit + make orient-commit
  → stale validation may clear on next orient
```

Future phases (checkpoint writer, SigMem0 recall tool, goal verify): [agentic-proposal-v0.2.md](agentic-proposal-v0.2.md).

---

## Anti-patterns

| Avoid | Why | Instead |
|-------|-----|---------|
| Agent writes repo files directly in portfolio flows | No validation lineage | `CASReturnPacket` → host apply |
| Treat recall/context as admissibility | BHOK classifies surfaces | Read as untrusted context |
| Deep handoff chains (3+) on 12B MLX | Context loss, minutes of latency | Agent-as-tool or shallow handoff |
| MiMo-style global memory files | Conflicts with SigMem0 tiers | Session traces + P8 dream path |
| Skipping guardrails before tools | Injection reaches actuators | `08` / `11` patterns |
| `tool_choice="required"` without care | Infinite tool loops | Default tool choice; cap turns |
| Same 12B model for parallel + main | RAM pressure | `gemma2:2b` for parallel/classifier |

---

## Verification commands

| Command | Proves |
|---------|--------|
| `./scripts/mvp_slice.sh` | End-to-end methodology narrative |
| `./scripts/membrane_preflight.sh` | Detached membrane prerequisites + degradation posture |
| `./scripts/membrane_propose.sh` | Proposal-only packet emission with invariant checks |
| `./scripts/membrane_verify.sh` | Host acceptance/rejection as operational truth |
| `./scripts/membrane_ops.sh` | One-command detached membrane flow (preflight → propose → verify) |
| `./scripts/mvp_slice.sh --with-host` | CAS packet + MacOS-CAS validation |
| `./scripts/test_patterns.sh` | Examples 04–11 |
| `./scripts/validate_cas_return.sh` | Subprocess JSON shape |
| `./scripts/python_agents_apply_smoke.sh` | Live apply on Mac host |
| `uv run agents-ollama-verify` | Ollama + SDK smoke |

Record results in [pattern-verification-log.md](pattern-verification-log.md) when adding new examples.

---

## Documentation map

| Doc | Use when |
|-----|----------|
| **This guide** | Designing a new agentic feature or onboarding |
| [detached-membrane-ops-pack.md](detached-membrane-ops-pack.md) | Operating detached membrane flows via preflight/propose/verify |
| [agentic-patterns.md](agentic-patterns.md) | Picking an SDK pattern with Ollama constraints |
| [programmatic-intelligence-seams.md](programmatic-intelligence-seams.md) | Wiring SigMem0 × Atlas × MacOS-CAS |
| [agentic-proposal-v0.2.md](agentic-proposal-v0.2.md) | Roadmap Phases 6–10, MiMo mapping |
| [cas-return-bridge.md](cas-return-bridge.md) | Subprocess CLI and packet fields |
| [portfolio-integration/macos-cas.md](portfolio-integration/macos-cas.md) | Host executor profiles and joint verify |
| [examples-walkthrough.md](examples-walkthrough.md) | Per-file example annotations |

---

## Suggested learning order

1. `./scripts/mvp_slice.sh` — see the full methodology once.
2. `examples/02_tool_calling.py` — tools on Ollama.
3. `examples/10_cas_return_stub.py` — proposal envelope.
4. `examples/08_guardrails.py` — safety before actuation.
5. [programmatic-intelligence-seams.md](programmatic-intelligence-seams.md) — where it plugs into the portfolio.
6. `./scripts/python_agents_apply_smoke.sh` — host apply (if MacOS-CAS checkout present).

**Next step:** Implement your feature at Level 1 or 2 first, then add portfolio taste/validate only when the proposal path is stable.
