"""Example 7 — Pydantic structured final output."""

from __future__ import annotations

import asyncio
import os

from agents import Agent, AgentOutputSchema, ModelSettings, Runner
from pydantic import BaseModel, Field

from agents_ollama import build_ollama_model, configure_ollama_runtime

MODEL = os.getenv("OLLAMA_MODEL", "gemma4:12b-mlx")


class LocalAgentBrief(BaseModel):
    """Minimal schema — local models handle two string fields more reliably than enums."""

    topic: str = Field(default="general", description="Short topic label")
    summary: str = Field(description="Two sentence summary max")


async def main() -> None:
    configure_ollama_runtime()
    model = build_ollama_model(MODEL)

    agent = Agent(
        name="Briefing agent",
        instructions=(
            "Produce a brief structured summary of the user's topic. "
            "Respond with JSON object containing keys: topic, summary. "
            "No markdown fences. Keep summary under 40 words."
        ),
        model=model,
        output_type=AgentOutputSchema(LocalAgentBrief, strict_json_schema=False),
        model_settings=ModelSettings(
            extra_body={"response_format": {"type": "json_object"}},
        ),
    )

    result = await Runner.run(
        agent,
        "Summarize what Ollama provides for local LLM developers.",
    )
    brief = result.final_output
    print(f"topic={brief.topic!r}")
    print(f"summary={brief.summary!r}")


if __name__ == "__main__":
    asyncio.run(main())
