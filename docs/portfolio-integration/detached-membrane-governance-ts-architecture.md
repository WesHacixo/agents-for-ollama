# Detached membrane governance — TypeScript architecture (ADR)

**Status:** accepted direction · **Authority:** orientation + implementation plan  
**Epic:** GitHub issue tracker below (created 2026-06-17)  
**Pattern sources:** [BIS-CP0 pattern alignment](bis-cp0-pattern-alignment.md), [detached membrane boundary spec](../detached-membrane-boundary-spec.md)

---

## Problem

The detached membrane stack grew a **governance spine in Python + bash** (policy compile, manifest checksums, layered gates, leak grep, governance e2e) while the **executor runtime is correctly Python** (OpenAI Agents SDK + Ollama + MacOS-CAS `python_agents_sdk`).

That split works but caps operational excellence:

- Contract drift is caught late (JSON + shell, not typecheck)
- Gate logic is split across heredocs, Python modules, and `rg`
- ZTNA is duplicated (`ztna_decide_local.py` vs `ztna_local.py`)
- Portfolio siblings (Atlas, BIS-CP0, PIM-0 worker) are **TypeScript/Bun-native**
- TDD bar is lighter than CP0 `local:gate` / `validate:100`

## Decision

**Polyglot by seam — not a Python→TS rewrite.**

| Seam | Language | Owns |
|------|----------|------|
| **Executor runtime** | Python | Agent loops, Ollama wiring, examples, MacOS-CAS subprocess propose |
| **Governance spine** | TypeScript (Bun) | Contracts, policy compile, manifest, layered gates, leak analysis, ZTNA, governance e2e, portfolio digest |
| **Host validation** | Swift (MacOS-CAS) | `validate-return-packet` acceptance truth |
| **Portfolio index** | Atlas / BHRT (mixed) | Bridge objects, Wyrm traces, coherence |

```text
┌─────────────────────────────────────────────────────────────┐
│  detached-membrane-governance (TS / Bun / Vitest)           │
│  contracts · policy · manifest · gates · ztna · e2e       │
└──────────────────────────┬──────────────────────────────────┘
                           │ validates shape before/after
┌──────────────────────────▼──────────────────────────────────┐
│  detached-membrane-sdk-py (Python — slim executor transforms) │
│  emit proposal · BHRT projection · PIM0 emit · receipt chain │
└──────────────────────────┬──────────────────────────────────┘
                           │ CASReturnPacket (proposed)
┌──────────────────────────▼──────────────────────────────────┐
│  agents_ollama + examples (Python — verified M4 executor)    │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│  MacOS-CAS (Swift host validator)                            │
└─────────────────────────────────────────────────────────────┘
```

**Non-negotiable invariants** (unchanged):

- `status=proposed`, `authority_status=advisory_only`, `execution_permitted=false`
- No host apply from agent process
- Tracing disabled for Ollama

## What moves to TypeScript

| Component | Today | Target |
|-----------|-------|--------|
| Manifest verify + checksum refresh | `manifest.py` + shell | `packages/detached-membrane-governance/src/manifest/` |
| Policy compile | `compile_membrane_policy.sh` (embedded Python) | `policy/compile.ts` |
| Layered gate L0–L4 | `layered_verify.py` | `gates/layered-verify.ts` |
| Governance e2e | `governance_e2e.py` | `e2e/governance-e2e.ts` |
| ZTNA issue/verify | duplicated Python | `ztna/local.ts` (single source) |
| Leak gate | `rg` + forbidden strings | `gates/leak-ast.ts` (AST, Phase C) |
| Contract validation | JSON files only | Zod → JSON Schema (Phase D) |
| Portfolio digest | bash JSON | `cli/portfolio-digest.ts` |
| Local gate entry | multiple shell scripts | `bun run membrane:local-gate` |

## What stays Python

- `agents_ollama/client.py` and Ollama model defaults
- Examples `01`–`15` and pattern verification on M4 hardware
- `agents-ollama-cas-return` CLI (executor subprocess for MacOS-CAS)
- BHRT/PIM0 emit helpers **until** TS contracts prove parity (then slim to thin wrappers or deprecate)

## Optional future lane

**`agents-ollama-ts`** — only when a concrete use case exists:

- Cloudflare Worker / PIM-0 edge co-location
- `@openai/agents/sandbox` filesystem agents
- Realtime / voice (`@openai/agents/realtime`)

Not in scope for Phases A–D.

## TDD and quality bar (CP0-aligned)

Borrow from BIS-CP0 [TDD and quality gates](https://github.com/WesHacixo/BIS-CP0/blob/main/docs/TDD-AND-QUALITY-GATES.md):

1. **Negative test per gate layer** — each L0–L4 has at least one fail fixture
2. **Golden JSON vectors** — receipts, packets, manifest checksums committed
3. **Pure gate functions** — no I/O inside `evaluate*`; inject in e2e only
4. **Fast default** — `bun test` unit suite &lt; few seconds for governance package
5. **Pre-merge command** — `bun run membrane:validate` = lint + typecheck + tests
6. **No silent skips** — governance e2e must fail closed if a layer is not evaluated

## Phased delivery

| Phase | GitHub issue | Outcome |
|-------|--------------|---------|
| **Epic** | [#1](https://github.com/WesHacixo/agents-for-ollama/issues/1) | Track polyglot governance migration end-to-end |
| **A** | [#2](https://github.com/WesHacixo/agents-for-ollama/issues/2) | `packages/detached-membrane-governance` scaffold + port manifest/policy/layers/ztna/e2e |
| **A.1** | [#7](https://github.com/WesHacixo/agents-for-ollama/issues/7) | Golden fixtures + negative gate vectors (TDD first) |
| **A.2** | [#8](https://github.com/WesHacixo/agents-for-ollama/issues/8) | ZTNA single source in TS; thin Python CLI wrapper |
| **B** | [#3](https://github.com/WesHacixo/agents-for-ollama/issues/3) | `verify_portfolio.sh` + quality gate delegate to Bun local gate |
| **B.1** | [#9](https://github.com/WesHacixo/agents-for-ollama/issues/9) | Portfolio digest typed CLI |
| **C** | [#4](https://github.com/WesHacixo/agents-for-ollama/issues/4) | AST leak gate replaces `rg` plane-separation check |
| **D** | [#5](https://github.com/WesHacixo/agents-for-ollama/issues/5) | Zod contracts → JSON Schema; public-safe build validator |
| **E** | [#6](https://github.com/WesHacixo/agents-for-ollama/issues/6) | Optional `agents-ollama-ts` executor lane (founder-triggered) |

Filter: [governance-ts issues](https://github.com/WesHacixo/agents-for-ollama/issues?q=is%3Aissue+label%3Agovernance-ts)

**Agent pickup order:** #7 → #2 (+ #8) → #3 (+ #9) → #4 → #5 → #6

## Success criteria (epic complete)

- [x] Phase A: `packages/detached-membrane-governance` with `bun run membrane:validate` (11 tests)
- [x] Phase B: `bun run membrane:local-gate` / `./scripts/membrane_local_gate.sh` in `verify_portfolio.sh`
- [x] Phase C: AST leak gate (`membrane:leak-gate`) replaces `rg` in local gate
- [ ] Python SDK leak gate still passes; no `subprocess` / execution markers in extractable core
- [ ] Single ZTNA implementation; shell scripts call TS CLI
- [ ] Layered verify has ≥5 negative fixtures (one per layer minimum)
- [ ] Manifest checksum verified on every quality gate run
- [ ] Docs index + portfolio backlog reference this ADR
- [ ] Python executor path unchanged for `membrane_ops.sh` propose/verify on M4

## Agent execution notes

Issues are written for **coding-agent pickup**:

- Each issue lists acceptance criteria and verify commands
- Dependencies reference parent phase issue
- Do not migrate examples or Ollama wiring in Phases A–D
- Prefer read-only port first (TS gates validate same fixtures as Python), then switch default gate

## Related docs

- [bis-cp0-pattern-alignment.md](bis-cp0-pattern-alignment.md)
- [detached-membrane-boundary-spec.md](../detached-membrane-boundary-spec.md)
- [detached-membrane-ops-pack.md](../detached-membrane-ops-pack.md)
- [portfolio-state-bluehand-alignment.md](../portfolio-state-bluehand-alignment.md)
