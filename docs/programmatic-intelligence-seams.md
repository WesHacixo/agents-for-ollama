# Programmatic intelligence — seam map (SigMem0 × Atlas × agentic harness)

*Where the agentic mechanism touches memory metabolism and portfolio orientation — without becoming truth.*

---

## The shape (one picture)

```text
                    ┌─────────────────────────────────────┐
                    │  Atlas-CAI (proprioception / map)    │
                    │  capsule · machine-state graph ·     │
                    │  coherence · bridge-objects registry │
                    │  authority: projection_not_truth     │
                    └──────────────┬──────────────────────┘
                                   │ indexes / validates / downgrades
                    ┌──────────────▼──────────────────────┐
                    │  MacOS-CAS (host nervous system)     │
                    │  CAS-1 handoff · validate · apply    │
                    │  python_agents_sdk subprocess        │
                    └──────┬──────────────────┬───────────┘
                           │ read              │ CASReturnPacket
              ┌────────────▼────────────┐      │ (proposed)
              │  SigMem0 :8741           │◄─────┘ trace_receipt seam
              │  recall · morning · dream │
              │  System1 read / System2   │
              │  dream writes             │
              └────────────┬──────────────┘
                           │
              ┌────────────▼────────────┐
              │  agents-for-ollama       │
              │  OpenAI Agents SDK loop  │
              │  Ollama /v1 tool ReAct   │
              └──────────────────────────┘
```

**Digestive metaphor (intentional):** SigMem0 **metabolizes** experience into tiers; MacOS-CAS **peristalses** proposals through validators; Atlas **feels** whether the organism is coherent. The Python agent is a **enzyme** — it catalyzes transforms in a bounded tube, never dumps product straight into doctrine.

---

## SigMem0 — what the agentic mechanism can *feed* and *taste*

### Taste (read-only, System 1)

| Surface | What the agent gets | Contract posture |
|---------|---------------------|------------------|
| `POST /v1/recall` | Macro recall pack (session + retrieval + context) | contextual, not proof |
| `GET /v1/context-pack/export` | Morning / fixture context envelope | `proposal_context_only` |
| `GET /v1/temporal-context-pack/export` | Obligations, threads, schedule pressure | `approval_required: true` |
| `GET /v1/cas/morning-handoff` | Full M4 envelope for Mac spine | consumed by Mac, agent can mirror |
| `GET /scene/context` | Morning continuity scene | presentation |
| `GET /v1/operational-reasoning/from-scene` | ORO + **lane proposals** | ranked suggestions, not dispatch |

**Agentic use:** `@function_tool recall_portfolio(query)` → inject into prompt before `Runner.run`. Treat `evidence_limitations` as mandatory skepticism.

**Lane routing curiosity:** SigMem0 `propose_execution_lanes_from_registry()` scores morning scene text against registry profiles — keyword `ollama` boosts `local.ollama`. A future hook: when scene mentions "governed harness" + "tool loop", also boost a **`local.python_agents_sdk`** lane (not in registry yet) as sibling to `local.ollama`.

### Feed (propose-only, never doctrine)

| Path | What crosses the membrane | Gate |
|------|---------------------------|------|
| `CASReturnPacket` → Mac apply | `status: proposed`, `writeback_proposal.sigmem0` | Mac validator; not auto-ingest |
| `POST /v1/pieces/poll` | `MemoryInputRecord` proposals | ledger only |
| P8 `dream_receipt` | `promotion_status: proposal` | `BND-PROM-P8-REVIEW` fence |
| Edge MCP `memory_working_note` | KV scratchpad | not semantic tier |
| `POST /v1/turns` | harness log append | requires `SIGLENT_AGENT_ID` |

**Bridge-object rule (Atlas registry):** `cas_return_packet_v0_1` **must_not_do:** `silently_promote_memory`, `bypass_trace_validation`.

### Dream (System 2 — where MiMo's "Dream" already lives)

SigMem0 P8 dual-speed (`dreaming/dual_speed.py`):

- **System 1:** `load_semantic_snapshot()` — agents may read
- **System 2:** `apply_ops()` under `system2_write_guard()` — **online agents must not call**

MiMo Code's 7-day Dream cycle ≈ SigMem0's dream metabolism consolidating episodic → semantic. **Do not duplicate** in agents-for-ollama. Instead:

1. Agent emits rich `actions_taken` + `artifacts` in CAS return  
2. Mac host apply creates session trace  
3. SigMem0 dream cycle (offline) distills — if promoted through gates  

**Emergent pattern:** *Agent proposes → host receipts → dream digests → semantic snapshot updates.* The agent never writes semantic YAML.

### Critical path alignment

Atlas capsule: `sigmem0_s3_to_mac_m4_1` = **wired_read_only**.

Agentic mechanism supports this by:

- Reading `TemporalContextPack` from handoff as **input** to local agent runs  
- Returning proposals that reference `source_packet_id` + `boundary_refs` (future)  
- Never calling `POST /v1/cas/pieces/promote` without human + `SIGLENT_AGENT_ID`

---

## Atlas — what the agentic mechanism can *illuminate* (not own)

### The intelligence triad (entrails exposed)

| Organ | File | Function |
|-------|------|----------|
| **Stomach summary** | `capsule/capsule.state.json` | Compressed "what matters now" |
| **Connective tissue** | `capsule/reports/latest-machine-state-graph.json` | 90+ nodes: systems, artifacts, boundaries, validations |
| **Immune report** | `capsule/reports/latest-coherence-report.json` | stale / broken / drift / downgrade |

**Compilers (the actual entrails):**

```text
repo oracles + boundary-map + bridge-objects + active-contracts
    → write-machine-state-report.py
    → compile-machine-state-graph.py
    → write-coherence-report.py
    → write-capsule-state.py
    → validate-atlas.py (master gate)
```

Agents don't write these. They **change inputs** that the next `make orient` digests.

### Registered bridge objects (typing the tubes)

Relevant to agentic harness:

| ID | Producer | Authority | Agentic role |
|----|----------|-----------|--------------|
| `capability_request_v0_1` | Mac | request, not execution | Agent asks BHOK "may I?" before actuation |
| `admissibility_packet_v0_1` | BHOK | classification | Agent reads allowed/denied surfaces |
| `cas_return_packet_v0_1` | Mac | reported, subject to validation | **Primary agent output envelope** |
| `execution_trace_skeleton_v0_1` | BHOK | trace frame | Lineage after approved run |
| `temporal_context_pack_v0` | SigMem0 | proposal context | Agent **input** from morning |
| `dream_receipt_v0` | SigMem0 | review candidate | Downstream of promotion, not agent stdout |
| `organizational_ontology_program_v0` | Atlas | ontology validator | Boundaries/obligations/arcs as **types** |

Seam `mac_return_to_portfolio`: pipeline `trace_receipt`, status `registered`.

### What a python_agents_sdk return does in Atlas (advisory only)

| Effect | Mechanism | Not allowed |
|--------|-----------|-------------|
| Clear `stale_validations` for Mac | Return `validation.commands_run` cites green oracles | Auto-edit capsule |
| Boundary pilot echo | `artifacts[]` cite `boundary_id`+hash matching pilot fixture | Mint new `boundary_v0` |
| Coherence `actionable[]` | Return violated `invalid_if` (e.g. completed without artifacts) | Grant execution |
| Graph node freshness | Mac `clean@main` + successful smoke → `risk:dirty-macos_cas` clears on orient | Add obligation nodes from agent text |
| Harness hub read order | Policy misalignment surfaced in `derived_recommendations` | Enforce policy (repos enforce locally) |

### Organizational ontology (Stage 3→4)

Atlas owns **types** (`obligation_v0`, `boundary_v0`, `arc_v0`). Mac projects `evidenceBoundary` presentation-only.

**Agentic contribution:** CAS returns carry `deviations_from_scope` and `risks` — natural fit for **arc pressure signals** without creating ontology instances:

```text
agent run → CASReturnPacket.risks[]
         → Mac ingest (session truth)
         → optional export fixture for boundary-coherence pilot
         → Atlas validate-boundary-coherence-pilot.py (ref match only)
```

---

## Emergent capabilities (curious combinations)

### 1. Morning-informed local agent

```text
SigMem0 morning-handoff
  → TemporalContextPack.unresolved_threads
  → python_agents_sdk hint: "Propose next step for thread X"
  → CASReturnPacket
  → Mac apply (running session)
  → Atlas orient sees Mac oracle fresh
```

### 2. Recall-grounded tool agent

```text
POST /v1/recall (harness session)
  → citations in agent tools
  → multi-step ReAct on gemma4:12b-mlx
  → structured CAS return with artifact refs to recall chunk IDs
  → writeback_proposal.sigmem0: proposal_only + rationale
```

### 3. Lane arbitration (SigMem0 brain → Mac muscle)

```text
GET /v1/operational-reasoning/from-scene
  → ExecutionLaneProposal[] (local.ollama scores high)
  → Mac CASDelegationDraft.lane = local_model
  → profile python_agents_sdk vs ollama_http_api chosen by operator
```

### 4. Coherence-closed loop

```text
Atlas coherence: fail (validate-atlas.py)
  → operator runs python_agents_apply_smoke.sh
  → if applied=true, commit Mac
  → make orient-commit in Atlas-CAI
  → coherence may clear atlas-validate-fail finding
```

### 5. Dream-fed second session (MiMo-like, governed)

```text
Session A: long tool run with checkpoint CAS returns (Phase 6)
  → episodic append only
  → P8 dream cycle (7d) OR operator-triggered distill
  → semantic snapshot update
Session B: agent System-1-reads snapshot, continues with rebuild injection
```

---

## Anti-patterns (membrane breaches)

| Breach | Why it rots the entrails |
|--------|--------------------------|
| Agent writes semantic tier directly | Breaks P8 System1/System2 split |
| CAS return → capsule.state.json | Atlas becomes execution truth |
| Skip `source_packet_id` | Host fail-closed; graph shows validation fail |
| Treat recall as admissibility | BHOK owns classification |
| MiMo-style free global memory file | Conflicts with SigMem0 tiers + promotion fence |

---

## Research vectors (next curiosity)

1. **`local.python_agents_sdk` lane** in SigMem0 executor registry — sibling to `local.ollama`  
2. **Recall tool example** (`12_sigmem0_recall_agent.py`) — wired_read_only seam proof  
3. **CAS return → boundary_ref artifact** — extend Atlas boundary-coherence pilot  
4. **Checkpoint writer agent** — MiMo single-writer, outputs intermediate CAS proposals only  
5. **Atlas graph query MCP** — read-only traverse `blocks` / `stale_validations` for harness agents  
6. **MiMo-V2.5 cloud lane** — same harness, compare horizon vs local Ollama (Phase 10)

---

## Related

- [agentic-proposal-v0.2.md](agentic-proposal-v0.2.md) — phased roadmap  
- [cas-return-bridge.md](cas-return-bridge.md) — subprocess CLI  
- SigMem0: `configs/surface_authority_registry.v0.yaml`, `dreaming/`, `cas_morning_handoff.py`  
- Atlas: `atlas/bridge-objects.yaml`, `docs/operations/machine-state-graph.md`  
- MacOS-CAS: `docs/integration/organizational-ontology-consumer-v0.1.md`
