"""Example 5 — orchestrator calls specialist agents via as_tool."""

from __future__ import annotations

import asyncio
import os

from agents import Agent, Runner

from agents_ollama import build_ollama_model, configure_ollama_runtime

MODEL = os.getenv("OLLAMA_MODEL", "gemma4:12b-mlx")


async def main() -> None:
    configure_ollama_runtime()
    model = build_ollama_model(MODEL)

    spanish_agent = Agent(
        name="Spanish agent",
        instructions="Translate the user's message to Spanish. Reply with translation only.",
        model=model,
    )

    orchestrator = Agent(
        name="Orchestrator",
        instructions=(
            "You are a translation helper. When asked for Spanish, call translate_to_spanish. "
            "Return the tool result without extra commentary."
        ),
        model=model,
        tools=[
            spanish_agent.as_tool(
                tool_name="translate_to_spanish",
                tool_description="Translate the user's message to Spanish.",
            ),
        ],
    )

    result = await Runner.run(
        orchestrator,
        "Say 'Good morning, the local agent is working.' in Spanish.",
    )
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
