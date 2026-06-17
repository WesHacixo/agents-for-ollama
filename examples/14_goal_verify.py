"""Example 14 — goal verification before CAS return (Phase 8)."""

from __future__ import annotations

import asyncio
import json
import os
import sys

from agents import Agent, ModelSettings, Runner

from agents_ollama.cas_return import build_cas_return_packet, validate_packet_structure
from agents_ollama.client import build_ollama_model, configure_ollama_runtime
from agents_ollama.goal_verify import verify_goal

MAIN_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:12b-mlx")
GOAL_MODEL = os.getenv("OLLAMA_GOAL_MODEL", "gemma2:2b")
HINT = os.getenv(
    "CAS_HINT",
    "Summarize in one sentence why proposal-only CAS returns matter for MacOS-CAS.",
)
SOURCE_PACKET_ID = os.getenv("CAS_SOURCE_PACKET_ID", "cas1_python_agents_sdk_stub")


async def main() -> None:
    configure_ollama_runtime()
    worker = Agent(
        name="ProposalWorker",
        instructions=(
            "You produce short proposal-only answers for a governed Mac harness. "
            "Reply in 1-2 sentences. No shell, no repo writes."
        ),
        model=build_ollama_model(MAIN_MODEL),
        model_settings=ModelSettings(temperature=0.2),
    )
    result = await Runner.run(worker, f"{HINT} (proposal only).")
    output = (result.final_output or "").strip()

    verdict = await verify_goal(
        operator_hint=HINT,
        agent_output=output,
        model=GOAL_MODEL,
    )
    print(f"goal_verdict: satisfied={verdict.satisfied} gap={verdict.gap!r}")

    if not verdict.satisfied:
        print("Goal not satisfied — skipping CAS return emission.", file=sys.stderr)
        raise SystemExit(2)

    packet = build_cas_return_packet(
        agent_output=output,
        hint=HINT,
        source_packet_id=SOURCE_PACKET_ID,
    )
    packet["actions_taken"].append(f"goal_verify:yes:{GOAL_MODEL}")
    errors = validate_packet_structure(packet)
    if errors:
        raise SystemExit(f"Invalid packet: {errors}")

    print(json.dumps(packet, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
