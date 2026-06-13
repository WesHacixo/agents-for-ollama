"""Example 4 — triage agent with handoff to a tool-equipped specialist."""

from __future__ import annotations

import asyncio
import os

from agents import Agent, Runner, function_tool

from agents_ollama import build_ollama_model, configure_ollama_runtime

MODEL = os.getenv("OLLAMA_MODEL", "gemma4:12b-mlx")


@function_tool
def lookup_fact(topic: str) -> str:
    """Return a stub fact for a topic (local demo data only)."""
    facts = {
        "golden gate bridge": "The Golden Gate Bridge is in San Francisco, California.",
        "ollama": "Ollama runs local LLMs and exposes an OpenAI-compatible API at /v1.",
    }
    key = topic.strip().lower()
    for label, fact in facts.items():
        if label in key or key in label:
            return fact
    return f"No local stub fact for '{topic}'. Try 'Golden Gate Bridge' or 'Ollama'."


async def main() -> None:
    configure_ollama_runtime()
    model = build_ollama_model(MODEL)

    researcher = Agent(
        name="Researcher",
        handoff_description="Looks up facts using lookup_fact.",
        instructions=(
            "You answer factual questions. Always call lookup_fact first, "
            "then reply in one or two sentences."
        ),
        model=model,
        tools=[lookup_fact],
    )

    triage = Agent(
        name="Triage",
        instructions=(
            "You route questions. For factual lookups about places, products, or "
            "technical topics, hand off to Researcher. Otherwise answer briefly yourself."
        ),
        model=model,
        handoffs=[researcher],
    )

    result = await Runner.run(
        triage,
        "Use research: what do you know about the Golden Gate Bridge?",
    )
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
