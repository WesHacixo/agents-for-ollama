"""Fixture-only governance e2e loop (no Ollama, no MacOS-CAS required)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .bhrt_projection import project_bhrt_packet
from .layered_verify import evaluate_layers
from .manifest import MANIFEST_REL_PATH, verify_manifest
from .pim0_emit import emit_pim0_from_proposal
from .proposal_emitter import emit_proposal_packet
from .verification_bridge import bridge_verification_result
from .ztna_local import issue_receipt, verify_receipt


GOVERNANCE_E2E_SCHEMA_VERSION = "detached-membrane-governance-e2e-0_1"
FIXTURE_REL = Path("fixtures/detached_membrane/governance_e2e_source_v0.json")
HOST_ACK_FIXTURE_REL = Path("fixtures/detached_membrane/macos_validator_ack_shape.json")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_governance_e2e(root: Path | None = None) -> dict[str, Any]:
    """Run fixture-only propose → ztna → layered verify → projection loop."""
    root = root or _repo_root()
    fixture = _load_json(root / FIXTURE_REL)
    host_ack = _load_json(root / HOST_ACK_FIXTURE_REL)

    manifest_ok, manifest_reasons = verify_manifest(root / MANIFEST_REL_PATH, root)
    if not manifest_ok:
        raise RuntimeError("manifest verify failed: " + "; ".join(manifest_reasons))

    source_packet_id = fixture["source_packet_id"]
    executor_profile_id = fixture.get("executor_profile_id", "python_agents_sdk")
    packet = emit_proposal_packet(
        source_packet_id=source_packet_id,
        executor_profile_id=executor_profile_id,
        summary=fixture.get("hint", "Governance e2e fixture proposal"),
    )

    policy_path = root / "packages/detached_membrane_sdk/policy/local_ztna_policy_v0.json"
    receipt_path = Path("/tmp/detached-membrane-governance-e2e-ztna.json")
    identity_ref = fixture.get("identity_ref", "detached_membrane_agent_local")
    ztna_receipt = issue_receipt(
        policy_path=policy_path,
        identity_ref=identity_ref,
        action="membrane_propose",
        resource="cas_return_packet",
        context_ref=source_packet_id,
        out_path=receipt_path,
    )
    ztna_verify_ok = verify_receipt(
        receipt=ztna_receipt,
        action="membrane_propose",
        resource="cas_return_packet",
        context_ref=source_packet_id,
    )

    packet["ztna"] = {
        "identity_ref": ztna_receipt.get("identity_ref"),
        "policy_decision_ref": ztna_receipt.get("decision_ref"),
        "decision_ttl_seconds": 900,
        "receipt_path": str(receipt_path),
        "authority_status": "advisory_only",
        "execution_permitted": False,
    }

    bridged = bridge_verification_result(packet=packet, host_ack=host_ack)
    layered = evaluate_layers(
        packet=packet,
        ztna=packet["ztna"],
        host_ack=host_ack,
        ztna_verify_ok=ztna_verify_ok,
        policy_assertions_ok=True,
        strict_legality=True,
    )
    pim0_envelope = emit_pim0_from_proposal(packet=packet)
    bhrt_projection = project_bhrt_packet(
        packet=packet,
        verification=bridged,
        ztna=packet["ztna"],
        pim0_envelope=pim0_envelope,
        parent_receipt_id=packet["ztna"].get("policy_decision_ref"),
    )

    return {
        "object": "DetachedMembraneGovernanceE2EReport",
        "schema_version": GOVERNANCE_E2E_SCHEMA_VERSION,
        "accepted": layered["accepted"] and bridged["accepted"] and manifest_ok,
        "manifest_reasons": manifest_reasons,
        "layered_verification": layered,
        "bridged_verification": bridged,
        "wyrm_trace_ref": bhrt_projection.get("wyrm_trace_ref"),
        "source_packet_id": source_packet_id,
        "fixture_mode": "no_ollama_no_macos_cas",
    }


def main() -> int:
    report = run_governance_e2e()
    print(json.dumps(report, indent=2))
    return 0 if report.get("accepted") else 1


if __name__ == "__main__":
    raise SystemExit(main())
