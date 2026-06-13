"""Example 10 — agent run mapped to CASReturnPacket JSON (MacOS-CAS bridge stub)."""

from __future__ import annotations

import asyncio
import json
import os

from agents_ollama.cas_runner import emit_cas_return, run_cas_return

MODEL = os.getenv("OLLAMA_MODEL", "gemma4:12b-mlx")
HINT = os.getenv("CAS_HINT", "Summarize next governed harness step for MacOS-CAS")
SOURCE_PACKET_ID = os.getenv("CAS_SOURCE_PACKET_ID", "cas1_python_agents_sdk_stub")
EXECUTOR_PROFILE_ID = os.getenv("CAS_EXECUTOR_PROFILE_ID", "python_agents_sdk")


async def main() -> None:
    packet = await run_cas_return(
        hint=HINT,
        source_packet_id=SOURCE_PACKET_ID,
        model=MODEL,
        executor_profile_id=EXECUTOR_PROFILE_ID,
    )
    emit_cas_return(packet, pretty=True)


if __name__ == "__main__":
    asyncio.run(main())
