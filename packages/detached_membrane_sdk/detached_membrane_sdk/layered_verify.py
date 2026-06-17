"""Layered verification with named reasons (CP0 gate-integration pattern)."""

from __future__ import annotations

from typing import Any


LAYERED_VERIFY_SCHEMA_VERSION = "detached-membrane-layered-verify-0_1"


def _layer(
    layer_id: str,
    name: str,
    passed: bool,
    reason: str,
    *,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "layer_id": layer_id,
        "name": name,
        "passed": passed,
        "reason": reason,
    }
    if details:
        entry["details"] = details
    return entry


def evaluate_layers(
    *,
    packet: dict[str, Any],
    ztna: dict[str, Any] | None = None,
    host_ack: dict[str, Any] | None = None,
    ztna_verify_ok: bool | None = None,
    policy_assertions_ok: bool | None = None,
    strict_legality: bool = False,
) -> dict[str, Any]:
    """Evaluate membrane verification as ordered layers with explicit reasons."""
    ztna = ztna or packet.get("ztna") or {}
    layers: list[dict[str, Any]] = []

    contract_ok = (
        packet.get("object") == "CASReturnPacket"
        and packet.get("status") == "proposed"
        and packet.get("authority_status") == "advisory_only"
        and packet.get("execution_permitted") is False
        and bool(packet.get("source_packet_id"))
    )
    layers.append(
        _layer(
            "L0",
            "contracts",
            contract_ok,
            "proposal packet satisfies advisory-only contract surface"
            if contract_ok
            else "packet missing required proposal-only contract fields",
            details={
                "object": packet.get("object"),
                "status": packet.get("status"),
                "authority_status": packet.get("authority_status"),
                "execution_permitted": packet.get("execution_permitted"),
            },
        )
    )

    if policy_assertions_ok is None:
        policy_passed = True
        policy_reason = "policy assertions not evaluated in this path"
    else:
        policy_passed = policy_assertions_ok
        policy_reason = (
            "compiled policy assertions match live contracts"
            if policy_passed
            else "compiled policy assertions failed"
        )
    layers.append(_layer("L1", "policy_compiler", policy_passed, policy_reason))

    ztna_present = bool(ztna.get("policy_decision_ref")) and bool(ztna.get("receipt_path"))
    if ztna_verify_ok is None:
        ztna_passed = ztna_present
        ztna_reason = (
            "ztna receipt metadata present"
            if ztna_passed
            else "ztna receipt metadata missing"
        )
    else:
        ztna_passed = ztna_present and ztna_verify_ok
        ztna_reason = (
            "ztna receipt verified for membrane_propose action"
            if ztna_passed
            else "ztna receipt verification failed or metadata missing"
        )
    layers.append(
        _layer(
            "L2",
            "ztna_gate",
            ztna_passed,
            ztna_reason,
            details={"policy_decision_ref": ztna.get("policy_decision_ref")},
        )
    )

    if host_ack is None:
        host_passed = False
        host_reason = "host validator acknowledgement not available"
    else:
        host_passed = bool(host_ack.get("accepted", False))
        errors = host_ack.get("errors", [])
        host_reason = (
            "host validator accepted proposal packet"
            if host_passed
            else f"host validator rejected proposal: {errors}"
        )
    layers.append(
        _layer(
            "L3",
            "host_validation",
            host_passed,
            host_reason,
            details={"accepted": host_ack.get("accepted") if host_ack else None},
        )
    )

    lineage_ready = bool(packet.get("layering_chain")) and bool(packet.get("actions_taken"))
    if strict_legality:
        strict_ok = (
            lineage_ready
            and bool(ztna.get("policy_decision_ref"))
            and int(ztna.get("decision_ttl_seconds") or 0) > 0
        )
        lineage_reason = (
            "strict legality lineage and ztna TTL satisfied"
            if strict_ok
            else "strict legality requirements not met"
        )
    else:
        strict_ok = lineage_ready
        lineage_reason = (
            "projection lineage fields present"
            if strict_ok
            else "missing layering_chain or actions_taken for projection"
        )
    layers.append(
        _layer(
            "L4",
            "lineage_projection",
            strict_ok,
            lineage_reason,
            details={"layering_chain_len": len(packet.get("layering_chain") or [])},
        )
    )

    accepted = all(layer["passed"] for layer in layers)
    return {
        "object": "DetachedMembraneLayeredVerification",
        "schema_version": LAYERED_VERIFY_SCHEMA_VERSION,
        "accepted": accepted,
        "layer_reasons": layers,
    }
