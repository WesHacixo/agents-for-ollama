"""Example 10 — agent run mapped to CASReturnPacket JSON (MacOS-CAS bridge stub)."""

from __future__ import annotations

import asyncio
import json
import os

from agents import Agent, ModelSettings, Runner

from agents_ollama import (
    build_cas_return_packet,
    build_ollama_model,
    configure_ollama_runtime,
    validate_packet_structure,
)

MODEL = os.getenv("OLLAMA_MODEL", "gemma4:12b-mlx")
HINT = os.getenv("CAS_HINT", "Summarize next governed harness step for MacOS-CAS")
SOURCE_PACKET_ID = os.getenv("CAS_SOURCE_PACKET_ID", "cas1_python_agents_sdk_stub")


async def main() -> None:
    configure_ollama_runtime()
    model = build_ollama_model(MODEL)

    agent = Agent(
        name="CASProposalAgent",
        instructions=(
            "You produce proposal-only summaries for a governed Mac agent harness. "
            "No repo writes, no shell, no truth promotion. Reply in 2-3 sentences."
        ),
        model=model,
        model_settings=ModelSettings(temperature=0.3),
    )

    result = await Runner.run(
        agent,
        f"{HINT} (proposal only, local Ollama).",
    )

    packet = build_cas_return_packet(
        agent_output=result.final_output,
        hint=HINT,
        source_packet_id=SOURCE_PACKET_ID,
    )

    errors = validate_packet_structure(packet)
    if errors:
        raise SystemExit(f"Packet structure invalid: {errors}")

    print(json.dumps(packet, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
