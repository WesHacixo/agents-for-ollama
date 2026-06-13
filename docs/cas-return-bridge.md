# CAS return bridge (Python Agents SDK → MacOS-CAS)

How agent runs in **agents-for-ollama** map to **`CASReturnPacket`** JSON for the MacOS-CAS harness.

## Status

| Item | Status |
|------|--------|
| `agents_ollama.cas_return.build_cas_return_packet` | Builder + structural validator |
| `agents-ollama-cas-return` CLI | Subprocess entry for MacOS-CAS |
| `examples/10_cas_return_stub.py` | Runnable demo |
| MacOS-CAS `python_agents_sdk` profile | Registered in `ExecutorManifold` |
| MacOS-CAS host apply | **`python-agents-rehearse-print --live`** + `apply-return` |

## Subprocess CLI (MacOS-CAS spawn target)

```bash
uv run agents-ollama-cas-return \
  --source-packet-id "$CAS_SOURCE_PACKET_ID" \
  "Summarize next governed harness step"
```

| Stream | Content |
|--------|---------|
| stdout | Single compact JSON `CASReturnPacket` |
| stderr | Progress / errors |
| exit 0 | Valid packet emitted |

Env: `CAS_HINT`, `CAS_SOURCE_PACKET_ID`, `CAS_EXECUTOR_PROFILE_ID` (default `python_agents_sdk`), `OLLAMA_MODEL`, `OLLAMA_BASE_URL`.

## Shape

```json
{
  "object": "CASReturnPacket",
  "schema_version": "cas-return-0_1",
  "executor_profile_id": "python_agents_sdk",
  "executor_family": "local_model_runtime",
  "executor_lane": "local_model",
  "status": "proposed",
  ...
}
```

## MacOS-CAS operator flow

```bash
# Validate only (Python subprocess → host validator)
./scripts/validate_cas_return.sh

# Live rehearsal + host apply (requires MacOS-CAS checkout)
./scripts/python_agents_apply_smoke.sh
```

Manual MacOS-CAS commands:

```bash
cd ~/Development/UltraViolet/MacOS-CAS
export AGENTS_FOR_OLLAMA_ROOT=~/Development/agents-for-ollama
swift run MacOSAppCLI python-agents-rehearse-print --live --hint "Your task"
swift run MacOSAppCLI apply-return \
  --rehearse-first --live --profile python_agents_sdk --hint "Your task" --json
```

## Library usage

```python
from agents_ollama.cas_runner import run_cas_return, emit_cas_return

packet = await run_cas_return(
    hint="my task",
    source_packet_id="cas1_...",
    model="gemma4:12b-mlx",
    executor_profile_id="python_agents_sdk",
)
emit_cas_return(packet)
```

## Related

- [agentic-patterns.md](agentic-patterns.md)
- [portfolio-integration/macos-cas.md](portfolio-integration/macos-cas.md)
- [MacOS-CAS bridge spec](https://github.com/WesHacixo/MacOS-CAS/blob/main/docs/integration/agents-sdk-ollama-bridge-v0.1.md)
