"""Envelope adapter for PIM0_EVENT_ENVELOPE_V1 thin-projection compatibility."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

PIM0_ENVELOPE_VERSION = "PIM0_EVENT_ENVELOPE_V1"
VALID_AUTHORITY_CLASSES = {
    "advisory",
    "proposal",
    "governed",
    "canonical",
    "presentation_only",
}


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def adapt_event_envelope(
    *,
    source_repo: str,
    source_object_type: str,
    source_schema_ref: str,
    source_object_ref: str,
    source_hash: str,
    authority_class: str,
    lineage_ref: str,
    policy_version: str,
    mutation_allowed: bool,
    receipt_ref: str | None,
    envelope_id: str,
    observed_at: str | None = None,
) -> dict[str, Any]:
    """Return a thin-projection event envelope aligned to Atlas matrix v1.

    The envelope is intentionally reference-heavy and payload-light to avoid
    semantic duplication and reduce IO overhead.
    """
    required_text = {
        "source_repo": source_repo,
        "source_object_type": source_object_type,
        "source_schema_ref": source_schema_ref,
        "source_object_ref": source_object_ref,
        "source_hash": source_hash,
        "lineage_ref": lineage_ref,
        "policy_version": policy_version,
        "envelope_id": envelope_id,
    }
    for key, value in required_text.items():
        if not value.strip():
            raise ValueError(f"{key} must be non-empty")

    if authority_class not in VALID_AUTHORITY_CLASSES:
        valid = ", ".join(sorted(VALID_AUTHORITY_CLASSES))
        raise ValueError(f"authority_class must be one of: {valid}")

    return {
        "envelope_version": PIM0_ENVELOPE_VERSION,
        "envelope_id": envelope_id,
        "source_repo": source_repo,
        "source_object_type": source_object_type,
        "source_schema_ref": source_schema_ref,
        "source_object_ref": source_object_ref,
        "source_hash": source_hash,
        "authority_class": authority_class,
        "lineage_ref": lineage_ref,
        "policy_version": policy_version,
        "mutation_allowed": bool(mutation_allowed),
        "receipt_ref": receipt_ref,
        "observed_at": observed_at or _iso_now(),
    }
