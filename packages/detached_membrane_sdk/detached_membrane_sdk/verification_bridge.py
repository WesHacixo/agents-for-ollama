"""Verification bridge for host validator acknowledgements."""

from __future__ import annotations

from typing import Any

VERIFICATION_SCHEMA_VERSION = "detached-membrane-verify-0_1"


def bridge_verification_result(
    *,
    packet: dict[str, Any],
    host_ack: dict[str, Any],
) -> dict[str, Any]:
    """Normalize host validator output into stable verification schema."""
    accepted = bool(host_ack.get("accepted", False))
    errors = host_ack.get("errors", [])
    if not isinstance(errors, list):
        errors = [str(errors)]

    return {
        "object": "DetachedMembraneVerificationResult",
        "schema_version": VERIFICATION_SCHEMA_VERSION,
        "accepted": accepted,
        "errors": errors,
        "packet_ref": {
            "return_id": packet.get("return_id"),
            "source_packet_id": packet.get("source_packet_id"),
            "executor_profile_id": packet.get("executor_profile_id"),
            "status": packet.get("status"),
        },
    }
