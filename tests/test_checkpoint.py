from __future__ import annotations

import unittest

from agents_ollama.checkpoint import SessionCheckpoint, build_checkpoint_cas_return


class CheckpointTests(unittest.TestCase):
    def test_build_checkpoint_cas_return_structure(self) -> None:
        checkpoint = SessionCheckpoint(
            intent="Finish weather deck research",
            files_touched=["notes/weather.md"],
            blockers=["Need operator approval before apply"],
            resume_hint="Summarize Tokyo, Paris, Sydney into one paragraph",
            tool_turns=3,
        )
        packet = build_checkpoint_cas_return(
            checkpoint,
            operator_hint="Research cities",
            source_packet_id="cas1_checkpoint_test",
        )
        self.assertEqual(packet["object"], "CASReturnPacket")
        self.assertEqual(packet["status"], "proposed")
        self.assertFalse(packet["execution_permitted"])
        session_cp = packet["proposed_next_state"]["session_checkpoint"]
        self.assertEqual(session_cp["tool_turns"], 3)
        self.assertTrue(any(a.startswith("checkpoint:") for a in packet["actions_taken"]))


if __name__ == "__main__":
    unittest.main()
