from __future__ import annotations

import unittest

from agents_ollama.max_mode_lite import parse_winner_index


class MaxModeLiteTests(unittest.TestCase):
    def test_parse_winner_index(self) -> None:
        self.assertEqual(parse_winner_index("WINNER 2 — best coverage", 3), 1)
        self.assertEqual(parse_winner_index("winner 1", 3), 0)
        self.assertEqual(parse_winner_index("ambiguous", 3), 0)
        self.assertEqual(parse_winner_index("WINNER 9", 3), 0)


if __name__ == "__main__":
    unittest.main()
