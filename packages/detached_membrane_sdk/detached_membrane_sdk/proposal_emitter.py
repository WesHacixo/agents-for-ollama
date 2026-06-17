"""Proposal packet emitter with contract-first defaults."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid

PROPOSAL_SCHEMA_VERSION = "cas-return-0_1"


def _return_id(prefix: str = "detached_membrane") -> str:
    stamp = int(datetime.now(timezone.utc).timestamp())
    return f"casreturn_{prefix}_{stamp}"


def emit_proposal_packet(
    *,
    source_packet_id: str,
    executor_profile_id: str,
    summary: str,
    action_tags: list[str] | None = None,
    artifacts: list[str] | None = None,
) -> dict[str, Any]:
    """Emit a proposal-only packet compatible with host validators."""
    if not source_packet_id.strip():
        raise ValueError("source_packet_id must be non-empty")
    if not executor_profile_id.strip():
        raise ValueError("executor_profile_id must be non-empty")

    compact_summary = summary.strip().replace("\n", " ")
    if len(compact_summary) > 240:
        compact_summary = compact_summary[:237] + "..."

    artifact_values = artifacts[:] if artifacts else [f"proposal:{uuid.uuid4().hex}"]
    actions = action_tags[:] if action_tags else ["detached_membrane:proposal_emit"]
    actions.append(f"summary:{compact_summary}")

    return {
        "object": "CASReturnPacket",
        "schema_version": PROPOSAL_SCHEMA_VERSION,
        "return_id": _return_id(),
        "source_packet_id": source_packet_id,
        "executor_profile_id": executor_profile_id,
        "executor_family": "local_model_runtime",
        "executor_lane": "local_model",
        "status": "proposed",
        "authority_status": "advisory_only",
        "execution_permitted": False,
        "actions_taken": actions,
        "artifacts": artifact_values,
        "validation": {"commands_run": [], "result": "not_run"},
        "deviations_from_scope": ["proposal_only:no_host_apply"],
        "risks": [
            "requires_host_validation",
            "output_is_proposal_only",
        ],
        "proposed_next_state": {"macos_session_status": "running"},
        "writeback_proposal": {"sigmem0": "none", "rationale": ""},
        "layering_chain": [
            "agents_for_ollama_executor",
            "macos_cas_validate",
            "bhrt_projection",
            "pim0_envelope_index",
        ],
    }
