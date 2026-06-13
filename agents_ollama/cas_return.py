"""Map OpenAI Agents SDK run results to CASReturnPacket-shaped JSON (stub)."""

from __future__ import annotations

import time
import uuid
from typing import Any


def new_return_id(prefix: str = "ollama_agents_sdk") -> str:
    return f"casreturn_{prefix}_{int(time.time())}"


def build_cas_return_packet(
    *,
    agent_output: str,
    source_packet_id: str = "cas1_python_agents_sdk_stub",
    hint: str = "",
    status: str = "proposed",
    executor_profile_id: str = "ollama_http_api",
) -> dict[str, Any]:
    """Build a proposal-only CASReturnPacket compatible with MacOS-CAS v0.1 shape.

    Uses ``ollama_http_api`` by default — the profile registered in MacOS-CAS
    ``ExecutorManifold``. Logical tag ``python_agents_sdk`` appears in actions_taken.
    """
    summary_action = agent_output.strip().replace("\n", " ")
    if len(summary_action) > 240:
        summary_action = summary_action[:237] + "..."

    hint_label = hint.strip() or "local_agents_sdk_run"
    artifact_id = str(uuid.uuid4()).upper()

    return {
        "object": "CASReturnPacket",
        "schema_version": "cas-return-0_1",
        "return_id": new_return_id(),
        "source_packet_id": source_packet_id,
        "executor_profile_id": executor_profile_id,
        "executor_family": "local_model_runtime",
        "executor_lane": "local_model",
        "status": status,
        "actions_taken": [
            f"summarize:{hint_label}",
            f"agent_output:{summary_action}",
            "classify:python_openai_agents_sdk",
        ],
        "artifacts": [f"proposal:agents_sdk/{artifact_id}"],
        "validation": {
            "commands_run": [],
            "result": "not_run",
        },
        "deviations_from_scope": [
            "none: python agents sdk stub; proposal only; no host apply",
        ],
        "risks": [
            "local_output_not_promoted_to_session_truth",
            "python_agents_sdk_not_host_validated",
        ],
        "proposed_next_state": {
            "macos_session_status": "running",
            "cp0_topology_state": "gate_passed",
        },
        "writeback_proposal": {
            "sigmem0": "none",
            "rationale": "",
        },
    }


def validate_packet_structure(packet: dict[str, Any]) -> list[str]:
    """Lightweight structural checks before MacOS-CAS host validation."""
    errors: list[str] = []
    required = (
        "object",
        "schema_version",
        "return_id",
        "source_packet_id",
        "executor_profile_id",
        "executor_family",
        "executor_lane",
        "status",
        "actions_taken",
        "artifacts",
        "deviations_from_scope",
    )
    for key in required:
        if key not in packet:
            errors.append(f"missing key: {key}")
    if packet.get("object") != "CASReturnPacket":
        errors.append("object must be CASReturnPacket")
    if packet.get("schema_version") != "cas-return-0_1":
        errors.append("schema_version must be cas-return-0_1")
    if packet.get("status") == "completed" and not packet.get("artifacts"):
        errors.append("completed status requires artifacts")
    if packet.get("actions_taken") and not packet.get("deviations_from_scope"):
        errors.append("deviations_from_scope required when actions_taken is non-empty")
    return errors
