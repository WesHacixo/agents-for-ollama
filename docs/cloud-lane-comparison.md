# Cloud lane comparison (Phase 10 orientation)

**Out of scope for default Ollama-only workflows** — this doc orients A/B experiments with remote OpenAI-compatible APIs (e.g. MiMo-V2.5) using the same CAS harness shape.

**Authority:** proposal-only — cloud models do not gain execution authority by proximity.

---

## When to use

| Lane | Use when |
|------|----------|
| **Local Ollama** (default) | Day-to-day dev, MacOS-CAS rehearsal, privacy, 24 GB RAM constraints |
| **Cloud OpenAI-compatible** | Long-context horizon experiments, quality A/B vs local 12B |

Keep **local Ollama as default**. Cloud is for bounded experiments, not production truth writes.

---

## Wiring pattern (same harness)

The repo already routes all agent calls through `AsyncOpenAI` with configurable `base_url`:

```python
# agents_ollama/client.py — OllamaSettings.from_env()
OLLAMA_BASE_URL=http://localhost:11434/v1   # default
OLLAMA_API_KEY=ollama
OLLAMA_MODEL=gemma4:12b-mlx
```

For a cloud A/B run, override env only — **no code fork**:

```bash
export OLLAMA_BASE_URL="https://api.example.com/v1"   # MiMo or other OpenAI-compatible endpoint
export OLLAMA_API_KEY="your-key"
export OLLAMA_MODEL="mimo-v2.5"                     # provider-specific name
export CAS_EXECUTOR_PROFILE_ID="python_agents_sdk"

uv run agents-ollama-cas-return --hint "Your task" --pretty
```

MacOS-CAS subprocess path uses the same env when `AGENTS_FOR_OLLAMA_ROOT` is set:

```bash
export AGENTS_FOR_OLLAMA_ROOT=~/Development/agents-for-ollama
cd ~/Development/UltraViolet/MacOS-CAS
swift run MacOSAppCLI python-agents-rehearse-print --live --hint "Cloud A/B task"
```

---

## What stays the same

- `CASReturnPacket` shape and `status: proposed`
- `authority_status: advisory_only`, `execution_permitted: false`
- MacOS-CAS `validate-return-packet` host gate
- SigMem0 recall remains **wired_read_only** (no auto-promotion)
- Tracing disabled (`configure_ollama_runtime()`)

---

## What to compare

| Dimension | Local (`gemma4:12b-mlx`) | Cloud (e.g. MiMo) |
|-----------|--------------------------|-------------------|
| Context horizon | ~8–32K practical on 24 GB | Often 128K+ |
| Latency | Low on Apple Silicon | Network-bound |
| Cost | Free local | Per-token |
| Tool calling | Verified on M4 | Re-verify per provider |
| Goal verify / Max Mode | `gemma2:2b` + 12B judge | May use same judge locally |

Run paired hints through `./scripts/verify_portfolio.sh` (local) and cloud env override (manual log).

---

## Anti-goals

| Do not | Why |
|--------|-----|
| Store cloud API keys in repo | Secrets hygiene |
| Treat cloud output as session truth | BHOK / CAS proposal-only |
| Port MiMo Dream into this repo | SigMem0 P8 owns evolution layer |
| Replace Ollama defaults in docs without re-verification | `docs/models-macos-m4.md` matrix |

---

## Related

- [agentic-proposal-v0.2.md](agentic-proposal-v0.2.md) — Phase 10 roadmap
- [configuration.md](configuration.md) — env vars
- [cas-return-bridge.md](cas-return-bridge.md) — subprocess CLI
- [building-agentic-software.md](building-agentic-software.md) — methodology
