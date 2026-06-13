"""Example 2 — agent with a function tool (requires a tool-capable Ollama model)."""

from __future__ import annotations

import asyncio

from agents import Runner, function_tool

from agents_ollama import build_agent, configure_ollama_runtime


@function_tool
def get_weather(city: str) -> str:
    """Return fake weather for a city."""
    return f"The weather in {city} is sunny and 22°C."


async def main() -> None:
    configure_ollama_runtime()

    agent = build_agent(
        name="WeatherBot",
        instructions="Use get_weather when asked about weather. Reply briefly.",
        model="gemma4:12b-mlx",
        tools=[get_weather],
    )

    result = await Runner.run(agent, "What's the weather in Tokyo?")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
