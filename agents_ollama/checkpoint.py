"""Long-horizon session checkpoint writer (proposal-only, no repo mutation)."""

from __future__ import annotations

import json
import uuid
from typing import Any

from agents import Agent, AgentOutputSchema, ModelSettings, Runner
from pydantic import BaseModel, Field

from agents_ollama.cas_return import build_cas_return_packet, new_return_id
from agents_ollama.client import build_ollama_model, configure_ollama_runtime

DEFAULT_CHECKPOINT_MODEL = "gemma4:12b-mlx"


class SessionCheckpoint(BaseModel):
    """Structured resume point for a long tool-loop session."""

    intent: str = Field(description="Operator goal in one sentence")
    files_touched: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    resume_hint: str = Field(description="Next action if the session restarts")
    tool_turns: int = Field(default=0, ge=0)


def format_tool_trace(tool_trace: list[dict[str, Any]]) -> str:
    """Serialize tool trace for the checkpoint writer prompt."""
    return json.dumps(tool_trace, indent=2)


async def write_session_checkpoint(
    *,
    operator_hint: str,
    tool_trace: list[dict[str, Any]],
    model: str = DEFAULT_CHECKPOINT_MODEL,
) -> SessionCheckpoint:
    """Writer-only mini-agent: summarize session state without mutating repo."""
    configure_ollama_runtime()
    ollama_model = build_ollama_model(model)
    writer = Agent(
        name="CheckpointWriter",
        instructions=(
            "You write session checkpoints for a governed local agent harness. "
            "Given operator hint and tool trace JSON, output structured JSON with keys: "
            "intent, files_touched (array), blockers (array), resume_hint, tool_turns. "
            "Never invent repo writes or execution authority. Proposal-only."
        ),
        model=ollama_model,
        output_type=AgentOutputSchema(SessionCheckpoint, strict_json_schema=False),
        model_settings=ModelSettings(
            temperature=0.2,
            extra_body={"response_format": {"type": "json_object"}},
        ),
    )
    prompt = (
        f"Operator hint: {operator_hint}\n\n"
        f"Tool trace ({len(tool_trace)} turns):\n{format_tool_trace(tool_trace)}\n\n"
        "Summarize checkpoint for session resume."
    )
    result = await Runner.run(writer, prompt)
    checkpoint = result.final_output
    if checkpoint.tool_turns == 0 and tool_trace:
        checkpoint = checkpoint.model_copy(update={"tool_turns": len(tool_trace)})
    return checkpoint


def build_checkpoint_cas_return(
    checkpoint: SessionCheckpoint,
    *,
    operator_hint: str,
    source_packet_id: str,
    executor_profile_id: str = "python_agents_sdk",
) -> dict[str, Any]:
    """Wrap a session checkpoint in a proposal-only CASReturnPacket."""
    checkpoint_id = str(uuid.uuid4()).upper()
    summary = (
        f"checkpoint intent={checkpoint.intent!r} "
        f"turns={checkpoint.tool_turns} blockers={len(checkpoint.blockers)}"
    )
    packet = build_cas_return_packet(
        agent_output=summary,
        hint=operator_hint,
        source_packet_id=source_packet_id,
        status="proposed",
        executor_profile_id=executor_profile_id,
    )
    packet["return_id"] = new_return_id("checkpoint")
    packet["actions_taken"].extend(
        [
            f"checkpoint:turns={checkpoint.tool_turns}",
            f"checkpoint:resume={checkpoint.resume_hint[:120]}",
        ]
    )
    packet["artifacts"].append(f"checkpoint:session/{checkpoint_id}")
    packet["proposed_next_state"] = {
        "macos_session_status": "running",
        "cp0_topology_state": "gate_passed",
        "session_checkpoint": checkpoint.model_dump(),
    }
    packet["risks"].append("checkpoint_is_proposal_only_not_session_truth")
    return packet
