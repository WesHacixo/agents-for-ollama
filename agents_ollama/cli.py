"""CLI entrypoints for chat and environment verification."""

from __future__ import annotations

import asyncio
import sys

from agents import Runner, function_tool

from agents_ollama.client import (
    DEFAULT_MODEL,
    DEFAULT_MODEL_CHAT_ONLY,
    OllamaSettings,
    build_agent,
    configure_ollama_runtime,
)


async def run_chat(prompt: str, model: str | None = None) -> str:
    configure_ollama_runtime()
    agent = build_agent(model=model)
    result = await Runner.run(agent, prompt)
    return result.final_output


async def run_verify() -> int:
    """Smoke-test chat and tool calling against the configured Ollama model."""
    configure_ollama_runtime()
    settings = OllamaSettings.from_env()

    print(f"Ollama base URL: {settings.base_url}")
    print(f"Default model:   {settings.model}")
    print()

    @function_tool
    def ping() -> str:
        return "pong"

    chat_agent = build_agent(
        name="VerifyChat",
        instructions="Reply briefly.",
        model=DEFAULT_MODEL_CHAT_ONLY,
    )
    print(f"[1/2] Chat test ({DEFAULT_MODEL_CHAT_ONLY})…")
    chat_result = await Runner.run(chat_agent, "Reply with exactly: OK")
    print(f"      → {chat_result.final_output.strip()[:80]}")
    print()

    tool_agent = build_agent(
        name="VerifyTools",
        instructions="Call ping when asked to ping.",
        model=settings.model,
        tools=[ping],
    )
    print(f"[2/2] Tool test ({settings.model})…")
    tool_result = await Runner.run(tool_agent, "Please ping.")
    print(f"      → {tool_result.final_output.strip()[:80]}")
    print()
    print("Verification passed.")
    return 0


def chat_main() -> None:
    prompt = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "Explain what the OpenAI Agents SDK is, in 3 bullet points."
    )
    model = sys.argv[2] if len(sys.argv) > 2 else None
    output = asyncio.run(run_chat(prompt, model=model))
    print(output)


def verify_main() -> None:
    raise SystemExit(asyncio.run(run_verify()))
