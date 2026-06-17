"""Example 12 — long-horizon session checkpoint (Phase 6, proposal-only CAS return)."""

from __future__ import annotations

import asyncio
import json
import os

from agents import Runner, function_tool

from agents_ollama import build_agent, configure_ollama_runtime
from agents_ollama.cas_return import validate_packet_structure
from agents_ollama.checkpoint import build_checkpoint_cas_return, write_session_checkpoint

MODEL = os.getenv("OLLAMA_MODEL", "gemma4:12b-mlx")
HINT = os.getenv(
    "CAS_HINT",
    "Research three cities for a weather report deck (proposal only)",
)
SOURCE_PACKET_ID = os.getenv("CAS_SOURCE_PACKET_ID", "cas1_python_agents_sdk_stub")
CHECKPOINT_AFTER_TURNS = int(os.getenv("CHECKPOINT_AFTER_TURNS", "3"))

TOOL_TRACE: list[dict[str, str]] = []


@function_tool
def lookup_city_fact(city: str) -> str:
    """Return a one-line fact about a city (fixture data for demo)."""
    facts = {
        "tokyo": "Tokyo is the capital of Japan.",
        "paris": "Paris is on the Seine in northern France.",
        "sydney": "Sydney is the capital of New South Wales, Australia.",
    }
    key = city.strip().lower()
    result = facts.get(key, f"No fixture fact for {city}.")
    TOOL_TRACE.append({"tool": "lookup_city_fact", "input": city, "result": result})
    return result


async def run_tool_loop() -> None:
    configure_ollama_runtime()
    worker = build_agent(
        name="ResearchWorker",
        instructions=(
            "Use lookup_city_fact for each city the user names. "
            "One city per step. Reply briefly after each lookup."
        ),
        model=MODEL,
        tools=[lookup_city_fact],
    )
    for city in ("Tokyo", "Paris", "Sydney"):
        await Runner.run(worker, f"Look up {city} and note one fact.")


async def main() -> None:
    await run_tool_loop()
    if len(TOOL_TRACE) < CHECKPOINT_AFTER_TURNS:
        raise SystemExit(
            f"Expected at least {CHECKPOINT_AFTER_TURNS} tool turns; got {len(TOOL_TRACE)}"
        )

    checkpoint = await write_session_checkpoint(
        operator_hint=HINT,
        tool_trace=TOOL_TRACE,
        model=MODEL,
    )
    packet = build_checkpoint_cas_return(
        checkpoint,
        operator_hint=HINT,
        source_packet_id=SOURCE_PACKET_ID,
    )
    errors = validate_packet_structure(packet)
    if errors:
        raise SystemExit(f"Invalid checkpoint packet: {errors}")

    print(json.dumps(packet, indent=2))
    print(
        f"\nCheckpoint OK: turns={checkpoint.tool_turns} "
        f"resume={checkpoint.resume_hint!r}"
    )


if __name__ == "__main__":
    asyncio.run(main())
