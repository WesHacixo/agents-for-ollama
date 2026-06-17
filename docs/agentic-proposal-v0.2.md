# Agentic use proposal v0.2

Portfolio-aligned plan for **OpenAI Agents SDK + Ollama** on the Mac, grounded in Atlas orientation (2026-06-16) and long-horizon agent research (Xiaomi **MiMo Code**).

**Audience:** operators and agents working across **agents-for-ollama**, **MacOS-CAS**, **SigMem0**, and **BHOK**.

---

## 1. Atlas state (2026-06-16)

**Source:** `~/Documents/Atlas-CAI/capsule/capsule.state.json` · `msg-2026-06-16` · *projection_not_truth — siblings own execution.*

| Signal | Status |
|--------|--------|
| Capsule | **refreshed** (`hon_status`) |
| Coherence | **fail** (1 fail, 4 warn) |
| Atlas validation | **fail** — `validate-atlas.py` not passing |
| MacOS-CAS worktree | **clean** @ `main` |
| BHRT-0 / BHOK / SigMem0 | **dirty** — stale-validation warnings |
| Critical path `sigmem0_s3_to_mac_m4_1` | **wired_read_only** |
| Morning scene issuance | **closed** on main |
| Organizational ontology | **Stage 3 structural**; Stage 4 gate = boundary coherence pilot |
| `cas_return_packet_v0_1` | **registered** in Atlas bridge-objects |

**Blockers (portfolio):**

1. Run `make compile-atlas` + `make validate` in Atlas-CAI before `make orient-commit`.
2. Reconcile dirty sibling worktrees (BHRT-0, BHOK, SigMem0) and re-run repo oracles.

**Where this repo fits:** agents-for-ollama is **not** in the five-root `portfolio-spine` yet. It is a **sibling executor reference** wired into MacOS-CAS via `python_agents_sdk` (Phase 4 shipped). Atlas registers `cas_return_packet_v0_1`; harness hub policy should treat Python agent loops as **proposal-only**, same as Ollama HTTP rehearsal.

**Read next (Atlas):**

- BHOK canonical [ATLAS.md](https://github.com/WesHacixo/bluehand-orchestration-kernel/blob/main/docs/operations/ATLAS.md)
- [organizational-ontology-portfolio-state.md](https://github.com/WesHacixo/Atlas-CAI/blob/main/docs/operations/organizational-ontology-portfolio-state.md)
- Mac mirror: [MacOS-CAS ATLAS.md](https://github.com/WesHacixo/MacOS-CAS/blob/main/docs/operations/ATLAS.md)

---

## 2. What we have shipped (Phases 0–5)

| Phase | Deliverable | Portfolio role |
|-------|-------------|----------------|
| 0–1 | Tools, handoffs, sessions, structured output | SDK reference on local Ollama |
| 2 | Guardrails + parallel (`08`–`09`) | Safety + latency patterns |
| 3 | CAS return stub (`10`) | `CASReturnPacket` shape |
| 4 | `agents-ollama-cas-return` + MacOS-CAS subprocess apply | **`python_agents_sdk` executor** |
| 5 | LLM guardrails (`11`) | Classifier agent on fast local model |

**Verified stack (M4 Pro / 24 GB):** `gemma4:12b-mlx` (tools, handoffs, CAS runs) · `gemma2:2b` (chat, parallel, guardrail classifier).

**Operator smoke:**

```bash
./scripts/validate_cas_return.sh
./scripts/python_agents_apply_smoke.sh
./scripts/test_patterns.sh
```

---

## 3. Xiaomi MiMo Code — what it is

**Released:** June 2026 (v0.1.0) · MIT · terminal-native coding agent from Xiaomi MiMo team.

| Layer | Idea | Claimed benefit |
|-------|------|-----------------|
| **Computation** | Max Mode (N=5 parallel samples + judge), Goal self-verification | +10–20% on long SWE tasks; fewer premature stops |
| **Memory** | Checkpoint writer subagent at 20/45/70% context; session / project / global markdown memory; rebuild injection near limit | 200+ step tasks; win rate >65% vs Claude Code on long jobs |
| **Evolution** | Dream (7d) + Distill (30d) agents consolidate memory; Dynamic Workflow → JS sandbox | Cross-session learning without corrupting live state |

**Models:** MiMo-V2.5 / V2.5-Pro — MoE, up to ~1M context; optional cloud via “MiMo Auto” channel.

**Relevance to us:** MiMo optimizes **harness + memory**, not just the base model. Same model in MiMo Code vs Claude Code reportedly gains ~5pp on benchmarks — the agent loop matters.

**Sources:** [MiMo blog — MiMo Code](https://mimo.xiaomi.com/) · [VentureBeat coverage](https://venturebeat.com/technology/xiaomis-new-open-source-agentic-ai-coding-harness-mimo-code-beats-claude-code-at-ultra-long-200-step-tasks)

---

## 4. MiMo → portfolio mapping (governed, not copied)

We **cannot** adopt MiMo’s free-form memory writes: MacOS-CAS and BHOK deny **truth promotion** and **session_truth** on local_model lanes. Map MiMo concepts to existing seams:

| MiMo concept | Portfolio analog | Gap |
|--------------|------------------|-----|
| Session checkpoint | `CAS1Packet` + `CAS_SOURCE_PACKET_ID` + governed handoff export | No automatic checkpoint cadence |
| Checkpoint writer (single writer) | Dedicated “writer” agent → `build_cas_return_packet()` only | Main agent still co-writes actions_taken |
| Rebuild injection | Re-prompt from handoff + SigMem0 recall slice + last CAS return | Not implemented |
| Project / global memory | SigMem0 + Membrane (read-only ingest on Mac) | Python agent has no SigMem0 tool yet |
| Dream / Distill | SigMem0 `p8_dream_memory_phase4` (Atlas: integration_complete_edge_deferred) | Align harvest cadence, don’t duplicate |
| Max Mode | `09_parallel` + judge agent | No scoring / selection loop |
| Goal verification | Second-pass “done?” agent before CAS emit | Not implemented |
| Dynamic Workflow | CAS `actions_taken` → reusable Bun/Swift script proposals | Future harness normalizer |

**Design rule (from MiMo, adapted):** *one writer per structured artifact* — executor proposes; host validates and applies; SigMem0 ingests only through governed adapters.

---

## 5. Proposed phases (v0.2 roadmap)

### Phase 6 — Long-horizon session cycling

**Problem:** Local 12B models lose thread on deep tool chains; MiMo solves with checkpoints before degradation.

**Proposal:**

1. **Checkpoint cadence** — after N tool turns or token budget thresholds, spawn a **writer-only** mini-agent that outputs a structured checkpoint (intent, files, blockers) — never mutates repo.
2. **Rebuild injection** — on context pressure, new `Runner.run` with: active `CAS1` handoff + checkpoint + last K user turns.
3. **MacOS-CAS** — optional `python-agents-rehearse-print --checkpoint` that emits intermediate `CASReturnPacket` with `status: proposed` without apply.

**Success:** 50+ step tool demo completes without manual restart on `gemma4:12b-mlx`.

### Phase 7 — SigMem0-aware tool agent (read-only)

**Problem:** Agents lack portfolio memory; Membrane/SigMem0 already hold morning context.

**Proposal:**

1. `@function_tool` `recall_sigmem0(query)` — HTTP to local SigMem0 recall API (fixture fallback).
2. Guardrail: tool returns are **untrusted context**, never commands.
3. Document admissibility alignment with `sigmem0_s3_to_mac_m4_1` (**wired_read_only**).

**Success:** Example `13_sigmem0_recall_agent.py` + note in MacOS-CAS development spine.

### Phase 8 — Goal verification + Max Mode lite

**Problem:** Agents stop early or pick weak tool paths.

**Proposal:**

1. **Goal guard** — before `build_cas_return_packet`, a fast model answers: “Is the operator hint satisfied? YES/NO + gap.”
2. **Max Mode lite** — `asyncio.gather` 3 candidates on `gemma2:2b`, judge with `gemma4:12b-mlx`, pick one (pattern from MiMo, scaled down for 24 GB RAM).

**Success:** Example `14_goal_verify.py`; measurable reduction in incomplete CAS returns in smoke script.

### Phase 9 — Atlas + harness registration

**Problem:** agents-for-ollama sits outside portfolio-spine orientation.

**Proposal:**

1. BHOK ATLAS entry: sibling repo, critical path **consumer** of `cas_return_packet_v0_1`.
2. `atlas-portfolio-digest` includes Python executor smoke status when `AGENTS_FOR_OLLAMA_ROOT` set.
3. Joint verify in `verify_portfolio.sh` gates on `python_agents_apply_smoke.sh`.

**Success:** Atlas coherence node for agents-for-ollama; no new truth-write surfaces.

**Status (2026-06-17):** `python_agents_sdk_cas_return_v0` bridge object + machine-state seam registered in Atlas-CAI; BHOK `ATLAS.md` sibling executor table; `./scripts/atlas_portfolio_digest.sh` for orientation JSON.

### Phase 10 — Optional cloud lane (MiMo-V2.5)

**Out of scope for Ollama-only repo** but worth a **comparison doc**:

- Same harness (`agents-ollama-cas-return` pattern) with `OPENAI_BASE_URL` → MiMo API for long-context A/B.
- Keeps local Ollama as default; cloud for horizon experiments only.

---

## 6. Anti-goals (portfolio constraints)

| Do not | Why |
|--------|-----|
| Let Python agents self-write SigMem0 / session truth | BHOK + CAS denied capabilities |
| Skip `CAS_SOURCE_PACKET_ID` match | Host validation fails closed |
| Treat Atlas capsule as execution authority | `projection_not_truth` |
| Port MiMo Dream into repo without SigMem0 P8 alignment | Duplicate evolution layer |
| Run 27B+ models on 24 GB for Max Mode | RAM / latency — use 2B judge + 12B worker |

---

## 7. Immediate next actions

| Priority | Action | Owner surface |
|----------|--------|---------------|
| P0 | Reconcile Atlas: `make compile-atlas && make validate` in Atlas-CAI | Portfolio ops |
| P0 | Commit/push dirty BHOK/SigMem0/BHRT worktrees or refresh capsule | Portfolio ops |
| P1 | Implement Phase 6 checkpoint writer example | **Done** (`12_session_checkpoint.py`, `agents_ollama/checkpoint.py`) |
| P1 | Register agents-for-ollama in BHOK ATLAS sibling table | **Done** (BHOK ATLAS.md + Atlas yaml) |
| P2 | SigMem0 recall tool (Phase 7) behind fixture gate | **Done** (`13_sigmem0_recall_agent.py`) |
| P2 | Phase 8 goal verification | **Done** (`14_goal_verify.py`) |
| P2 | Phase 8 Max Mode lite | **Done** (`15_max_mode_lite.py`) |
| P2 | Portfolio verify + Atlas digest | **Done** (`verify_portfolio.sh`, `atlas_portfolio_digest.sh`) |

---

## Related

- [building-agentic-software.md](building-agentic-software.md) — methodology guide for builders
- [agentic-patterns.md](agentic-patterns.md) — pattern catalog
- [cas-return-bridge.md](cas-return-bridge.md) — subprocess CLI
- [portfolio-integration/macos-cas.md](portfolio-integration/macos-cas.md)
- [MacOS-CAS agents-sdk-ollama-bridge](https://github.com/WesHacixo/MacOS-CAS/blob/main/docs/integration/agents-sdk-ollama-bridge-v0.1.md)
