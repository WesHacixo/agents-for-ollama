"""Shared wiring for OpenAI Agents SDK + Ollama on macOS."""

from agents_ollama.cas_return import build_cas_return_packet, new_return_id, validate_packet_structure
from agents_ollama.checkpoint import (
    SessionCheckpoint,
    build_checkpoint_cas_return,
    write_session_checkpoint,
)
from agents_ollama.goal_verify import GoalVerdict, parse_goal_verdict_line, verify_goal
from agents_ollama.max_mode_lite import MaxModeLiteResult, run_max_mode_lite
from agents_ollama.sigmem0_recall import recall_sigmem0_context
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
    "GoalVerdict",
    "parse_goal_verdict_line",
    "verify_goal",
    "MaxModeLiteResult",
    "run_max_mode_lite",
    "new_return_id",
    "recall_sigmem0_context",
    "SessionCheckpoint",
    "validate_packet_structure",
    "write_session_checkpoint",
]
