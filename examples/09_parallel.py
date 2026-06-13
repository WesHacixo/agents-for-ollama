"""Example 9 — parallel independent agent runs with asyncio.gather."""

from __future__ import annotations

import asyncio
import os

from agents import Agent, Runner

from agents_ollama import build_ollama_model, configure_ollama_runtime

# Fast chat-only model keeps parallel demo under ~30s on one Ollama daemon.
MODEL = os.getenv("OLLAMA_PARALLEL_MODEL", "gemma2:2b")


async def ask(agent: Agent, prompt: str) -> str:
    result = await Runner.run(agent, prompt)
    return result.final_output.strip()


async def main() -> None:
    configure_ollama_runtime()
    model = build_ollama_model(MODEL)

    sky_agent = Agent(
        name="Sky",
        instructions="Answer in one word only.",
        model=model,
    )
    grass_agent = Agent(
        name="Grass",
        instructions="Answer in one word only.",
        model=model,
    )

    sky, grass = await asyncio.gather(
        ask(sky_agent, "What color is the sky on a clear day?"),
        ask(grass_agent, "What color is healthy grass?"),
    )

    print(f"sky={sky!r}")
    print(f"grass={grass!r}")


if __name__ == "__main__":
    asyncio.run(main())
