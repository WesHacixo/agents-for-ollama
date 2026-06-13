"""Run OpenAI Agents SDK and emit CASReturnPacket JSON for MacOS-CAS subprocess ingest."""

from __future__ import annotations

import json
import sys
from typing import Any

from agents import Agent, ModelSettings, Runner

from agents_ollama.cas_return import build_cas_return_packet, validate_packet_structure
from agents_ollama.client import configure_ollama_runtime, build_ollama_model

DEFAULT_HINT = "Summarize next governed harness step for MacOS-CAS"
DEFAULT_SOURCE_PACKET_ID = "cas1_python_agents_sdk_stub"
DEFAULT_MODEL = "gemma4:12b-mlx"
DEFAULT_EXECUTOR_PROFILE_ID = "python_agents_sdk"


async def run_cas_return(
    *,
    hint: str,
    source_packet_id: str,
    model: str,
    executor_profile_id: str,
) -> dict[str, Any]:
    configure_ollama_runtime()
    ollama_model = build_ollama_model(model)

    agent = Agent(
        name="CASProposalAgent",
        instructions=(
            "You produce proposal-only summaries for a governed Mac agent harness. "
            "No repo writes, no shell, no truth promotion. Reply in 2-3 sentences."
        ),
        model=ollama_model,
        model_settings=ModelSettings(temperature=0.3),
    )

    result = await Runner.run(
        agent,
        f"{hint} (proposal only, local Ollama).",
    )

    return build_cas_return_packet(
        agent_output=result.final_output,
        hint=hint,
        source_packet_id=source_packet_id,
        executor_profile_id=executor_profile_id,
    )


def emit_cas_return(packet: dict[str, Any], *, pretty: bool = False) -> None:
    errors = validate_packet_structure(packet)
    if errors:
        print(f"Packet structure invalid: {errors}", file=sys.stderr)
        raise SystemExit(1)
    if pretty:
        print(json.dumps(packet, indent=2))
    else:
        print(json.dumps(packet), flush=True)
