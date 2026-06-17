"""Emit thin PIM0 envelopes from detached membrane proposals."""

from __future__ import annotations

from typing import Any

from .envelope_adapter import adapt_event_envelope


def emit_pim0_from_proposal(
    *,
    packet: dict[str, Any],
    source_repo: str = "agents-for-ollama",
    policy_version: str = "detached-membrane-policy-v1",
    envelope_id: str | None = None,
) -> dict[str, Any]:
    """Create a thin PIM0 envelope reference for a CAS proposal packet."""
    return_id = packet.get("return_id", "unknown_return")
    source_packet_id = packet.get("source_packet_id", "unknown_source")
    envelope = envelope_id or f"evt_dm_{return_id}"

    return adapt_event_envelope(
        source_repo=source_repo,
        source_object_type="CASReturnPacket",
        source_schema_ref="cas-return-0_1",
        source_object_ref=return_id,
        source_hash=f"b3:{return_id}",
        authority_class="presentation_only",
        lineage_ref=source_packet_id,
        policy_version=policy_version,
        mutation_allowed=False,
        receipt_ref=packet.get("ztna", {}).get("policy_decision_ref"),
        envelope_id=envelope,
    )
