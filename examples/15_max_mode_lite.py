"""Example 15 — Max Mode lite: parallel candidates + judge selection."""

from __future__ import annotations

import asyncio
import json
import os

from agents_ollama.cas_return import build_cas_return_packet, validate_packet_structure
from agents_ollama.max_mode_lite import run_max_mode_lite

CANDIDATE_MODEL = os.getenv("OLLAMA_PARALLEL_MODEL", "gemma2:2b")
JUDGE_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:12b-mlx")
HINT = os.getenv(
    "CAS_HINT",
    "Explain in one sentence why parallel candidates help local agent quality.",
)
SOURCE_PACKET_ID = os.getenv("CAS_SOURCE_PACKET_ID", "cas1_python_agents_sdk_stub")


async def main() -> None:
    result = await run_max_mode_lite(
        hint=HINT,
        candidate_model=CANDIDATE_MODEL,
        judge_model=JUDGE_MODEL,
    )
    print(f"winner={result.winner_index + 1} text={result.winner_text!r}")
    print(f"judge={result.judge_verdict}")

    packet = build_cas_return_packet(
        agent_output=result.winner_text,
        hint=HINT,
        source_packet_id=SOURCE_PACKET_ID,
    )
    packet["actions_taken"].append(
        f"max_mode_lite:winner={result.winner_index + 1}:candidates={len(result.candidates)}"
    )
    errors = validate_packet_structure(packet)
    if errors:
        raise SystemExit(f"Invalid packet: {errors}")
    print(json.dumps(packet, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
