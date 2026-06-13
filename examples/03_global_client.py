"""Example 3 — global OpenAI client configuration (alternative wiring style)."""

from __future__ import annotations

import asyncio

from agents import Agent, Runner, function_tool, set_default_openai_api, set_default_openai_client, set_tracing_disabled
from openai import AsyncOpenAI


@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny and 22°C."


async def main() -> None:
    client = AsyncOpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
    )
    set_default_openai_client(client, use_for_tracing=False)
    set_default_openai_api("chat_completions")
    set_tracing_disabled(disabled=True)

    agent = Agent(
        name="WeatherBot",
        instructions="Use get_weather for weather questions. Reply briefly.",
        model="gemma4:12b-mlx",
        tools=[get_weather],
    )

    result = await Runner.run(agent, "What's the weather in Tokyo?")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
