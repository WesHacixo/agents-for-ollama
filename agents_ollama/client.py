"""Ollama client and model wiring for the OpenAI Agents SDK."""

from __future__ import annotations

import os
from dataclasses import dataclass

from agents import Agent, OpenAIChatCompletionsModel, set_tracing_disabled
from openai import AsyncOpenAI

# Verified defaults for Apple M4 Pro / 24 GB (see docs/models-macos-m4.md).
DEFAULT_BASE_URL = "http://localhost:11434/v1"
DEFAULT_API_KEY = "ollama"
DEFAULT_MODEL = "gemma4:12b-mlx"
DEFAULT_MODEL_CHAT_ONLY = "gemma2:2b"


@dataclass(frozen=True)
class OllamaSettings:
    """Connection settings for a local Ollama OpenAI-compatible endpoint."""

    base_url: str = DEFAULT_BASE_URL
    api_key: str = DEFAULT_API_KEY
    model: str = DEFAULT_MODEL

    @classmethod
    def from_env(cls) -> OllamaSettings:
        return cls(
            base_url=os.getenv("OLLAMA_BASE_URL", DEFAULT_BASE_URL),
            api_key=os.getenv("OLLAMA_API_KEY", DEFAULT_API_KEY),
            model=os.getenv("OLLAMA_MODEL", DEFAULT_MODEL),
        )


def configure_ollama_runtime(*, disable_tracing: bool = True) -> None:
    """Apply runtime defaults required for Ollama-backed agents."""
    if disable_tracing:
        # Ollama does not accept OpenAI trace exports.
        set_tracing_disabled(disabled=True)


def build_ollama_client(settings: OllamaSettings | None = None) -> AsyncOpenAI:
    settings = settings or OllamaSettings.from_env()
    return AsyncOpenAI(
        base_url=settings.base_url,
        api_key=settings.api_key,
    )


def build_ollama_model(
    model: str | None = None,
    *,
    settings: OllamaSettings | None = None,
    client: AsyncOpenAI | None = None,
) -> OpenAIChatCompletionsModel:
    settings = settings or OllamaSettings.from_env()
    return OpenAIChatCompletionsModel(
        model=model or settings.model,
        openai_client=client or build_ollama_client(settings),
    )


def build_agent(
    *,
    name: str = "LocalHelper",
    instructions: str = "You are a helpful local-only assistant.",
    model: str | None = None,
    settings: OllamaSettings | None = None,
    tools: list | None = None,
) -> Agent:
    return Agent(
        name=name,
        instructions=instructions,
        model=build_ollama_model(model, settings=settings),
        tools=tools or [],
    )
