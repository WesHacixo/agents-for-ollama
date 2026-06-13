# CAS return bridge (Python Agents SDK → MacOS-CAS)

How agent runs in **agents-for-ollama** map to **`CASReturnPacket`** JSON for the MacOS-CAS harness.

## Status

| Item | Status |
|------|--------|
| `agents_ollama.cas_return.build_cas_return_packet` | Stub builder |
| `examples/10_cas_return_stub.py` | Runnable demo |
| MacOS-CAS host apply | Not wired — proposal-only |

## Shape

Output matches `cas-return-0_1` fields used in MacOS-CAS operator loop proofs:

```json
{
  "object": "CASReturnPacket",
  "schema_version": "cas-return-0_1",
  "executor_profile_id": "ollama_http_api",
  "executor_family": "local_model_runtime",
  "executor_lane": "local_model",
  "status": "proposed",
  ...
}
```

Reference packet: [MacOS-CAS operator loop proof](https://github.com/WesHacixo/MacOS-CAS/blob/main/docs/operations/operator-loop-proof-2026-05-20/03-return-packet.json)

## Run the stub

```bash
uv run python examples/10_cas_return_stub.py
export CAS_HINT="Draft proposal for inference router docs"
uv run python examples/10_cas_return_stub.py
```

## Code

```python
from agents import Runner
from agents_ollama import build_agent, build_cas_return_packet, configure_ollama_runtime

configure_ollama_runtime()
result = await Runner.run(build_agent(), "Your task")
packet = build_cas_return_packet(agent_output=result.final_output, hint="my_task")
```

## MacOS-CAS validation

**Structural (local):** `validate_packet_structure()` in `agents_ollama/cas_return.py`

**Host accept:** MacOS-CAS `return-validate` / `validate-return-packet` also require
`source_packet_id` to match the active governed handoff (`cas1-print`). For a full accept path:

```bash
# One-shot (requires MacOS-CAS checkout)
./scripts/validate_cas_return.sh

# Manual steps
cd ~/Development/UltraViolet/MacOS-CAS
swift run MacOSAppCLI cas1-export --output /tmp/cas1.json 2>/dev/null
export CAS_SOURCE_PACKET_ID=$(python3 -c "import json; print(json.load(open('/tmp/cas1.json'))['packet_id'])")
cd ~/Development/agents-for-ollama
uv run python examples/10_cas_return_stub.py > /tmp/agents-sdk-return.json
cd ~/Development/UltraViolet/MacOS-CAS
swift run MacOSAppCLI validate-return-packet --input /tmp/agents-sdk-return.json --json 2>/dev/null
```

Default `executor_profile_id` is **`ollama_http_api`** (registered in MacOS-CAS). The Python SDK path is tagged in `actions_taken` via `classify:python_openai_agents_sdk`.

Host apply remains **off** until subprocess executor wiring lands.

## Related

- [agentic-patterns.md](../agentic-patterns.md)
- [portfolio-integration/macos-cas.md](macos-cas.md)
- [MacOS-CAS bridge spec](https://github.com/WesHacixo/MacOS-CAS/blob/main/docs/integration/agents-sdk-ollama-bridge-v0.1.md)
