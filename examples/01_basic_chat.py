"""Example 1 — basic chat with no tools."""

from __future__ import annotations

import asyncio

from agents import Runner

from agents_ollama import build_agent, configure_ollama_runtime


async def main() -> None:
    configure_ollama_runtime()

    # Fast chat-only model; see docs/models-macos-m4.md for tool-capable models.
    agent = build_agent(
        name="LocalHelper",
        instructions="You are a helpful local-only assistant.",
        model="gemma2:2b",
    )

    result = await Runner.run(
        agent,
        "Explain what the OpenAI Agents SDK is, in 3 bullet points.",
    )
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
