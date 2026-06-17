from __future__ import annotations

import unittest

from agents_ollama.sigmem0_recall import (
    format_recall_for_agent,
    load_recall_fixture,
    recall_sigmem0_context,
)


class SigMem0RecallTests(unittest.TestCase):
    def test_fixture_recall_contains_untrusted_banner(self) -> None:
        text = recall_sigmem0_context("python_agents_sdk atlas")
        self.assertIn("UNTRUSTED RECALL", text)
        self.assertIn("proposal_context_only", text)
        self.assertIn("python_agents_sdk", text.lower())

    def test_fixture_loads_matches(self) -> None:
        fixture = load_recall_fixture()
        self.assertEqual(fixture["authority_status"], "proposal_context_only")
        self.assertGreaterEqual(len(fixture["matches"]), 2)

    def test_format_recall_for_agent(self) -> None:
        text = format_recall_for_agent(
            query="test",
            source="unit",
            lines=["one", "two"],
            limitations=["fixture only"],
        )
        self.assertIn("source=unit", text)
        self.assertIn("- one", text)


if __name__ == "__main__":
    unittest.main()
