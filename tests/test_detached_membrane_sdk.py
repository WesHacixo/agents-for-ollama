from __future__ import annotations

import json
import unittest
from pathlib import Path

from detached_membrane_sdk import (
    adapt_event_envelope,
    bridge_verification_result,
    derive_wyrm_trace_ref,
    emit_pim0_from_proposal,
    emit_proposal_packet,
    format_receipt,
    project_bhrt_packet,
)


ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "detached_membrane"


class DetachedMembraneSdkTests(unittest.TestCase):
    def test_adapt_event_envelope_contract(self) -> None:
        env = adapt_event_envelope(
            source_repo="Atlas-CAI",
            source_object_type="organizational_state_event_v0",
            source_schema_ref="atlas/contracts/organizational_state_event_v0",
            source_object_ref="ose_test_001",
            source_hash="b3:test-hash",
            authority_class="canonical",
            lineage_ref="trace_test_001",
            policy_version="atlas-envelope-policy-v1",
            mutation_allowed=False,
            receipt_ref=None,
            envelope_id="evt_test_001",
            observed_at="2026-06-16T00:00:00Z",
        )
        self.assertEqual(env["envelope_version"], "PIM0_EVENT_ENVELOPE_V1")
        self.assertEqual(env["source_repo"], "Atlas-CAI")
        self.assertEqual(env["authority_class"], "canonical")
        self.assertFalse(env["mutation_allowed"])

    def test_emit_proposal_packet_contract(self) -> None:
        packet = emit_proposal_packet(
            source_packet_id="cas1_example_001",
            executor_profile_id="python_agents_sdk",
            summary="Propose next detached membrane step",
        )
        self.assertEqual(packet["object"], "CASReturnPacket")
        self.assertEqual(packet["schema_version"], "cas-return-0_1")
        self.assertEqual(packet["status"], "proposed")
        self.assertEqual(packet["authority_status"], "advisory_only")
        self.assertFalse(packet["execution_permitted"])
        self.assertEqual(packet["source_packet_id"], "cas1_example_001")
        self.assertGreaterEqual(len(packet["artifacts"]), 1)

    def test_bhrt_projection_alignment(self) -> None:
        packet = emit_proposal_packet(
            source_packet_id="cas1_example_004",
            executor_profile_id="python_agents_sdk",
            summary="BHRT projection alignment",
        )
        projection = project_bhrt_packet(
            packet=packet,
            verification={"accepted": True},
            ztna={"policy_decision_ref": "ztna_decision_test"},
            parent_receipt_id="ztna_decision_test",
        )
        self.assertEqual(projection["authority_status"], "advisory_only")
        self.assertFalse(projection["execution_permitted"])
        self.assertIn("layering_chain", projection)
        self.assertIn("lane_separation", projection)
        self.assertEqual(projection["lineage"]["parent_receipt_id"], "ztna_decision_test")
        self.assertTrue(projection["wyrm_trace_ref"].startswith("wyrm-"))

    def test_c067_boundary_witness_fixture(self) -> None:
        witness = json.loads((FIXTURES / "c067_boundary_witness_v0.json").read_text(encoding="utf-8"))
        self.assertEqual(witness["authority_status"], "advisory_only")
        self.assertFalse(witness["execution_permitted"])
        self.assertIn("symmetry_witnesses", witness)

    def test_derive_wyrm_trace_ref(self) -> None:
        ref = derive_wyrm_trace_ref("ztna_decision_test")
        self.assertIsNotNone(ref)
        self.assertTrue(ref.startswith("wyrm-"))
        self.assertEqual(len(ref), len("wyrm-") + 24)
        self.assertIsNone(derive_wyrm_trace_ref(None))

    def test_receipt_chain_parent_resolution(self) -> None:
        from detached_membrane_sdk.receipt_chain import (
            append_receipt_link,
            load_receipt_chain,
            resolve_parent_receipt_id,
        )

        chain = load_receipt_chain()
        chain = append_receipt_link(
            chain,
            source_packet_id="cas1_a",
            return_id="ret_a",
            policy_decision_ref="ztna_a",
            wyrm_trace_ref="wyrm-aaa",
        )
        parent = resolve_parent_receipt_id(chain=chain, fallback="ztna_b", enabled=True)
        self.assertEqual(parent, "wyrm-aaa")
        chain = append_receipt_link(
            chain,
            source_packet_id="cas1_b",
            return_id="ret_b",
            policy_decision_ref="ztna_b",
            wyrm_trace_ref="wyrm-bbb",
        )
        parent = resolve_parent_receipt_id(chain=chain, fallback=None, enabled=True)
        self.assertEqual(parent, "wyrm-bbb")
        self.assertEqual(resolve_parent_receipt_id(chain=chain, fallback="x", enabled=False), "x")

    def test_emit_pim0_from_proposal(self) -> None:
        packet = emit_proposal_packet(
            source_packet_id="cas1_example_005",
            executor_profile_id="python_agents_sdk",
            summary="PIM0 envelope emit",
        )
        envelope = emit_pim0_from_proposal(packet=packet)
        self.assertEqual(envelope["envelope_version"], "PIM0_EVENT_ENVELOPE_V1")
        self.assertEqual(envelope["source_object_type"], "CASReturnPacket")
        self.assertEqual(envelope["authority_class"], "presentation_only")
        self.assertFalse(envelope["mutation_allowed"])

    def test_bridge_and_receipt(self) -> None:
        packet = emit_proposal_packet(
            source_packet_id="cas1_example_002",
            executor_profile_id="python_agents_sdk",
            summary="Bridge host ack",
        )
        bridged = bridge_verification_result(packet=packet, host_ack={"accepted": True, "errors": []})
        receipt = format_receipt(bridged)
        self.assertTrue(bridged["accepted"])
        self.assertIn("detached_membrane=ACCEPTED", receipt)
        self.assertIn("source_packet_id=cas1_example_002", receipt)

    def test_atlas_endpoint_shape_fixture(self) -> None:
        atlas_shape = json.loads((FIXTURES / "atlas_endpoint_shape.json").read_text(encoding="utf-8"))
        self.assertEqual(atlas_shape["envelope_version"], "PIM0_EVENT_ENVELOPE_V1")
        self.assertEqual(atlas_shape["source_repo"], "Atlas-CAI")
        self.assertEqual(atlas_shape["authority_class"], "canonical")
        self.assertIn("source_object_ref", atlas_shape)

    def test_macos_validator_shape_fixture(self) -> None:
        ack_shape = json.loads((FIXTURES / "macos_validator_ack_shape.json").read_text(encoding="utf-8"))
        packet = emit_proposal_packet(
            source_packet_id="cas1_example_003",
            executor_profile_id="python_agents_sdk",
            summary="Validator shape compatibility",
        )
        bridged = bridge_verification_result(packet=packet, host_ack=ack_shape)
        self.assertIn("accepted", bridged)
        self.assertIn("errors", bridged)
        self.assertEqual(bridged["schema_version"], "detached-membrane-verify-0_1")


if __name__ == "__main__":
    unittest.main()
