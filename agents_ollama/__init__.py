"""Shared wiring for OpenAI Agents SDK + Ollama on macOS."""

from agents_ollama.cas_return import build_cas_return_packet, new_return_id, validate_packet_structure
from agents_ollama.checkpoint import (
    SessionCheckpoint,
    build_checkpoint_cas_return,
    write_session_checkpoint,
)
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
    "build_cas_return_packet",
    "build_checkpoint_cas_return",
    "build_ollama_client",
    "build_ollama_model",
    "configure_ollama_runtime",
    "new_return_id",
    "SessionCheckpoint",
    "validate_packet_structure",
    "write_session_checkpoint",
]
