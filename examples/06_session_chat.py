"""Example 6 — multi-turn chat with SQLiteSession memory."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from agents import Agent, Runner
from agents.memory import SQLiteSession

from agents_ollama import build_ollama_model, configure_ollama_runtime

MODEL = os.getenv("OLLAMA_MODEL", "gemma4:12b-mlx")
DB_PATH = Path(__file__).resolve().parent / ".session_demo.db"


async def main() -> None:
    configure_ollama_runtime()
    model = build_ollama_model(MODEL)

    agent = Agent(
        name="Assistant",
        instructions="Reply very concisely. Remember prior turns in the session.",
        model=model,
    )

    session = SQLiteSession("handoff_demo", DB_PATH)

    first = await Runner.run(
        agent,
        "What city is the Golden Gate Bridge in? One word answer.",
        session=session,
    )
    print(f"Turn 1: {first.final_output.strip()}")

    second = await Runner.run(
        agent,
        "What state is it in? One word answer.",
        session=session,
    )
    print(f"Turn 2: {second.final_output.strip()}")


if __name__ == "__main__":
    asyncio.run(main())
