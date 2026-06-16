"""Receipt formatter for concise operator-facing summaries."""

from __future__ import annotations

from typing import Any


def format_receipt(verification: dict[str, Any]) -> str:
    """Format normalized verification result as compact multi-line receipt."""
    ref = verification.get("packet_ref", {})
    accepted = bool(verification.get("accepted", False))
    status_word = "ACCEPTED" if accepted else "REJECTED"
    errors = verification.get("errors", [])
    error_tail = "none" if not errors else "; ".join(str(e) for e in errors)

    return (
        f"detached_membrane={status_word}\n"
        f"return_id={ref.get('return_id', 'unknown')}\n"
        f"source_packet_id={ref.get('source_packet_id', 'unknown')}\n"
        f"executor_profile_id={ref.get('executor_profile_id', 'unknown')}\n"
        f"errors={error_tail}"
    )
