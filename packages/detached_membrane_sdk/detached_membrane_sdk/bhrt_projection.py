"""BHRT / Wyrm-aligned projection from detached membrane artifacts."""

from __future__ import annotations

import hashlib
from typing import Any

PROJECTION_SCHEMA_VERSION = "bhrt-projection-0_2"

DEFAULT_LAYERING_CHAIN = [
    "cloudflare_edge",
    "dmi_membrane_pim0_worker",
    "mcp_tunnel_transport",
    "secgate_wyrm_admission",
    "bhrt_runtime_semantics",
    "supabase_ledger",
]


def derive_wyrm_trace_ref(policy_decision_ref: str | None) -> str | None:
    """Derive a stable Wyrm trace ref from a policy decision receipt."""
    if not policy_decision_ref:
        return None
    digest = hashlib.sha256(policy_decision_ref.encode("utf-8")).hexdigest()[:24]
    return f"wyrm-{digest}"


def project_bhrt_packet(
    *,
    packet: dict[str, Any],
    verification: dict[str, Any] | None = None,
    ztna: dict[str, Any] | None = None,
    pim0_envelope: dict[str, Any] | None = None,
    wyrm_trace_refs: list[str] | None = None,
    parent_receipt_id: str | None = None,
) -> dict[str, Any]:
    """Project membrane artifacts into BHRT/Wyrm-friendly receipt vocabulary."""
    ztna_data = ztna or packet.get("ztna", {})
    policy_decision_ref = ztna_data.get("policy_decision_ref")
    accepted = bool((verification or {}).get("accepted", False))
    trace_refs = wyrm_trace_refs or []
    if not trace_refs:
        derived = derive_wyrm_trace_ref(policy_decision_ref)
        if derived:
            trace_refs = [derived]

    return {
        "object": "BHRTDetachedMembraneProjection",
        "schema_version": PROJECTION_SCHEMA_VERSION,
        "authority_status": "advisory_only",
        "execution_permitted": False,
        "authority": {
            "authority_class": "proposal",
            "policy_decision_ref": policy_decision_ref,
            "advisory_only": True,
        },
        "lineage": {
            "source_packet_id": packet.get("source_packet_id"),
            "return_id": packet.get("return_id"),
            "parent_receipt_id": parent_receipt_id,
        },
        "layering_chain": DEFAULT_LAYERING_CHAIN,
        "lane_separation": {
            "dmi_ingress": "pim0.blue-hand.org",
            "nexus_advisory": "api.bluehand.dev / mcp.bluehand.dev",
            "public_implement_bridge": "docs.bluehand.dev",
            "wyrm_admission": "local wyrm_gate (T1 lease broker)",
        },
        "coverage_snapshot": {
            "actions_taken_count": len(packet.get("actions_taken", [])),
            "artifacts_count": len(packet.get("artifacts", [])),
            "host_accepted": accepted,
        },
        "state_delta_refs": packet.get("artifacts", []),
        "external_lineage_refs": [x for x in [policy_decision_ref] if x],
        "wyrm_trace_refs": trace_refs,
        "wyrm_trace_ref": trace_refs[0] if trace_refs else None,
        "pim0_envelope_ref": (pim0_envelope or {}).get("envelope_id"),
        "receipt": {
            "boundary": "detached_membrane.local",
            "decision": "admitted" if accepted else "denied",
            "execution_permitted": False,
            "reason_code": "proposal_only" if accepted else "host_validation_failed",
        },
    }
