# Detached membrane ops pack

How to explain, justify, and adopt the detached membrane scripting pack as the default path for governed agentic execution.

**Audience:** your primary coding agent (and operators guiding it).

---

## The short pitch

Traditional agent automation is optimized for speed of output.  
Detached membrane automation is optimized for **quality of authority**.

The ops pack makes this practical by giving your agent a strict, repeatable path:

1. `membrane_preflight.sh` — verify operational truth before reasoning
2. `membrane_propose.sh` — emit proposal-only `CASReturnPacket` with local ZTNA decision receipt
3. `membrane_verify.sh` — host-validate and report accepted/rejected

This transforms “agent said X” into “host-validated proposal with lineage.”

---

## Why this beats the traditional path

| Traditional path | Detached membrane path |
|---|---|
| Agent writes files/actions directly | Agent emits proposal packet only |
| Success judged by plausible text | Success judged by host acceptance |
| Context treated as trustworthy by default | Context explicitly treated as untrusted input |
| Failures discovered late in manual review | Failures fail-fast in preflight/verify |
| Hard to compare runs | Structured receipts enable diffable outcomes |

**Net effect:** fewer silent authority leaks, clearer audit trails, and safer iteration.

---

## Mechanics (what your agent should actually do)

### Step 1: preflight (fail-fast)

```bash
./scripts/membrane_preflight.sh
```

What it checks:

- Ollama API availability
- SigMem0 context-export availability (advisory)
- MacOS-CAS root and `python_agents_sdk` profile
- local ZTNA policy file presence
- readiness flags (`ready_for_propose`, `degraded_mode_available`)

Contract:

- `exit 0`: fully ready
- `exit 2`: degraded (proposal path possible; host profile not fully ready)
- `exit 1`: hard fail (no Ollama)

### Step 2: propose (no side effects)

```bash
./scripts/membrane_propose.sh \
  --hint "Propose next detached membrane integration step" \
  --out /tmp/detached-membrane-return.json
```

What it guarantees:

- packet remains `status: proposed`
- `source_packet_id` is present and checked
- local ZTNA decision receipt is issued and linked (`policy_decision_ref`)
- summary includes artifact/action counts for quick triage

### Step 3: verify (host is source of acceptance truth)

```bash
./scripts/membrane_verify.sh /tmp/detached-membrane-return.json
```

What it returns:

- `accepted: true|false`
- host errors (if any)
- ZTNA decision linkage (`policy_decision_ref`)
- packet metadata for operator traceability

---

## Operator ramp (adoption in 3 passes)

### Pass A — prove safety envelope

- Run preflight and verify failures are explicit.
- Confirm no direct apply occurs from the agent process.

### Pass B — prove utility

- Use `membrane_propose.sh` on real hints.
- Compare packet consistency across multiple prompts.

### Pass C — standardize

- Make the three scripts your default runbook for membrane-related tasks.
- Require host `accepted=true` before promoting any outcome downstream.

---

## Reflexive loop upgrades used here

This pack already includes two improvement loops beyond a first-cut script set:

### Loop 1 — from “works” to “governable”

Initial approach: run CLI and trust output.  
Upgrade applied: enforce packet invariants (`status=proposed`, `source_packet_id` match) before calling it done.

**Benefit:** catches authority-shape regressions immediately.

### Loop 2 — from “human-readable” to “machine-auditable”

Initial approach: print logs only.  
Upgrade applied: emit compact JSON summaries and verification objects (`DetachedMembranePreflight`, `DetachedMembraneProposalSummary`, `DetachedMembraneVerification`).

**Benefit:** enables future CI gates and cross-run diffing without log scraping.

### Loop 3 — from “safe by convention” to “safe by gate”

Initial approach: rely on developer discipline for boundary integrity.  
Upgrade applied: `scripts/check_membrane_leaks.sh` enforces fail-closed checks for:

- repo-local imports in membrane core
- authority leak markers (`service_role`, direct apply surfaces, promotion paths)
- contract file presence

**Benefit:** critical leakage classes are blocked before extraction.

### Loop 4 — from “policy docs” to “compiled policy”

Initial approach: manually keep contracts and leak rules in sync.  
Upgrade applied: `scripts/compile_membrane_policy.sh` compiles one policy source into:

- generated leak patterns
- generated verification assertions
- generated schema constraints

`scripts/verify_membrane_policy.sh` then checks live schemas against compiled assertions.

**Benefit:** policy drift becomes mechanically detectable rather than human memory-dependent.

### Loop 5 — CP0-inspired manifest + governance e2e (BIS-CP0 pattern alignment)

Pattern source: [BIS-CP0](portfolio-integration/bis-cp0-pattern-alignment.md) (no runtime coupling).

Upgrade applied:

- `packages/detached_membrane_sdk/spec/detached-membrane-manifest.v1.json` with SHA256 artifact checksums
- `./scripts/verify_membrane_manifest.sh` in quality gate
- `./scripts/membrane_governance_e2e.sh` — fixture-only propose → ztna → layered verify (no Ollama, no MacOS-CAS)
- `membrane_verify.sh` emits `layer_reasons` (L0–L4) for audit ergonomics

**Benefit:** contract spine integrity and offline governance truth path without live host dependencies.

### Loop 6 — from “bash spine” to `membrane:local-gate` (Phase B)

Upgrade applied:

- `bun run membrane:local-gate` — single TS entry: compile → manifest → policy → leak → ztna → e2e → vitest → python sdk tests
- `./scripts/membrane_local_gate.sh` wired into `verify_portfolio.sh` and `membrane_quality_gate.sh`
- `MEMBRANE_GATE_QUICK=1` skips governance e2e + python sdk tests (dev feedback)
- Portfolio digest via `membrane:portfolio-digest` (no re-run of gates inside digest)

**Benefit:** one canonical governance truth path aligned with BIS-CP0 `local:gate`.

### Loop 7 — from `rg` leak grep to AST leak gate (Phase C)

Upgrade applied:

- `src/gates/leak-ast.ts` + `leak_ast_scan.py` — Python `ast` walk for imports, execution calls, and markers
- `bun run membrane:leak-gate` / `./scripts/check_membrane_leaks.sh`
- Negative fixtures under `fixtures/leak_ast/` with vitest coverage

**Benefit:** structured violations `{ file, line, rule_id, snippet }` instead of brittle substring grep.

---

## How your primary coding agent should reason

When asked to “implement with detached membrane intelligence,” the agent should default to:

1. run `membrane_preflight.sh`
2. if ready/degraded, run `membrane_propose.sh`
3. run `membrane_verify.sh`
4. report:
   - what was proposed
   - whether host accepted
   - what blocked acceptance (if rejected)
   - next smallest safe step

This creates a stable cognitive loop: **observe → propose → validate → adapt**.

---

## Quickstart

```bash
./scripts/membrane_preflight.sh
./scripts/membrane_propose.sh --hint "Propose next detached membrane integration step"
./scripts/membrane_verify.sh
```

Or run the one-command orchestrator:

```bash
./scripts/membrane_ops.sh --hint "Propose next detached membrane integration step"
./scripts/membrane_ops.sh --chain-receipts --hint "Step two with receipt lineage"
```

Useful flags:

- `--allow-degraded` to continue when preflight returns degraded (`exit 2`)
- `--chain-receipts` to thread `parent_receipt_id` across verify steps via receipt chain file
- `--source-packet-id` to pin lineage explicitly
- `--out` to control packet output path

Governance gate (run before extracting or promoting membrane core changes):

```bash
./scripts/membrane_local_gate.sh --strict-legality
./scripts/verify_portfolio.sh          # local gate + unit tests + optional smoke
```

---

## Related docs

- [building-agentic-software.md](building-agentic-software.md)
- [detached-membrane-boundary-spec.md](detached-membrane-boundary-spec.md)
- [programmatic-intelligence-seams.md](programmatic-intelligence-seams.md)
- [cas-return-bridge.md](cas-return-bridge.md)
- [portfolio-integration/bis-cp0-pattern-alignment.md](portfolio-integration/bis-cp0-pattern-alignment.md)
- [portfolio-integration/detached-membrane-governance-ts-architecture.md](portfolio-integration/detached-membrane-governance-ts-architecture.md) · [Epic #1](https://github.com/WesHacixo/agents-for-ollama/issues/1)
