"""Shared wiring for OpenAI Agents SDK + Ollama on macOS."""

from agents_ollama.client import (
    OllamaSettings,
    build_agent,
    build_ollama_client,
    build_ollama_model,
    configure_ollama_runtime,
)

__all__ = [
    "OllamaSettings",
    "build_agent",
    "build_ollama_client",
    "build_ollama_model",
    "configure_ollama_runtime",
]
