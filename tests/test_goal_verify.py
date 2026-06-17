from __future__ import annotations

import unittest

from agents_ollama.goal_verify import GoalVerdict, parse_goal_verdict_line


class GoalVerifyTests(unittest.TestCase):
    def test_parse_yes(self) -> None:
        verdict = parse_goal_verdict_line("YES")
        self.assertTrue(verdict.satisfied)
        self.assertEqual(verdict.gap, "")

    def test_parse_no_with_gap(self) -> None:
        verdict = parse_goal_verdict_line("NO: missing Tokyo weather")
        self.assertFalse(verdict.satisfied)
        self.assertIn("Tokyo", verdict.gap)


if __name__ == "__main__":
    unittest.main()
