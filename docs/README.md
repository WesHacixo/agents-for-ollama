# Documentation

Reference guides for running the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) against [Ollama](https://ollama.com) on **macOS Apple Silicon**.

## Start here

| Doc | What you'll learn |
|-----|-------------------|
| **[Building agentic software](building-agentic-software.md)** | **Methodology guide** — taste → propose → validate, adoption levels, design checklist |
| **[Detached membrane ops pack](detached-membrane-ops-pack.md)** | **Operational pack** — preflight, propose, verify for governed membrane runs |
| **[Detached membrane boundary spec](detached-membrane-boundary-spec.md)** | **Extraction rules** — package boundary, contracts, portability gates |
| **[Detached membrane policy adoption](detached-membrane-policy-adoption.md)** | **Uber-policy stamp** — adoption metadata for Atlas-style policy audits |
| **[Portfolio state (Bluehand alignment)](portfolio-state-bluehand-alignment.md)** | **Cross-repo state** — Atlas `.dev` + BHRT Wyrm alignment and packet roadmap |
| **[Public-safe schema slice](public-safe-schema-slice.md)** | **docs.bluehand.dev export** — `public_safe.v1` field allowlist |
| [Getting started](getting-started.md) | Install Ollama, Python deps, first agent run |
| [Configuration](configuration.md) | Env vars, wiring patterns, SDK settings |
| [Models on macOS M4](models-macos-m4.md) | Verified model matrix for 24 GB RAM |
| [Examples walkthrough](examples-walkthrough.md) | Annotated tour of `examples/` |
| [Troubleshooting](troubleshooting.md) | Errors we hit and how to fix them |
| [Verification log](verification-log.md) | What was tested, when, and on what hardware |
| [MacOS-CAS integration](portfolio-integration/macos-cas.md) | Sibling Swift host — shared Ollama, API split, joint verify |
| [Atlas sibling registration](portfolio-integration/atlas-sibling-registration.md) | Index fixture + promotion checklist for portfolio spine |
| [Agentic patterns](agentic-patterns.md) | Handoffs, agent-as-tool, sessions, structured output on Ollama |
| [Agentic proposal v0.2](agentic-proposal-v0.2.md) | Atlas state, MiMo Code lessons, Phases 6–10 roadmap |
| [Programmatic intelligence seams](programmatic-intelligence-seams.md) | SigMem0 × Atlas × agentic harness — deep seam map |
| **MVP slice** | `./scripts/mvp_slice.sh` — self-explaining demo ([methodology](building-agentic-software.md)) |
| [CAS return bridge](cas-return-bridge.md) | CASReturnPacket stub for MacOS-CAS |
| [Pattern verification log](pattern-verification-log.md) | Live test results for examples 04–10 |

## Quick commands

```bash
uv sync
./scripts/mvp_slice.sh              # start here — self-explaining value demo
./scripts/membrane_preflight.sh     # detached membrane readiness gate
./scripts/verify_setup.sh
uv run python examples/01_basic_chat.py
uv run python examples/02_tool_calling.py
```

## Architecture (one paragraph)

Ollama exposes an **OpenAI-compatible Chat Completions API** at `http://localhost:11434/v1`. The Agents SDK does not need a special Ollama plugin — you pass an `AsyncOpenAI` client with that `base_url` into `OpenAIChatCompletionsModel`, then into `Agent`. From the SDK's perspective it is a normal chat-completions backend.
