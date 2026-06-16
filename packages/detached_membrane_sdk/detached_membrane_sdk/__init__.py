"""Detached membrane SDK: contract-first, repo-agnostic membrane primitives."""

from .envelope_adapter import adapt_event_envelope
from .proposal_emitter import emit_proposal_packet
from .receipt_formatter import format_receipt
from .verification_bridge import bridge_verification_result

__all__ = [
    "adapt_event_envelope",
    "emit_proposal_packet",
    "bridge_verification_result",
    "format_receipt",
]
