from __future__ import annotations

import unittest

from frontier_eval.evaluator import wilson_interval


class WilsonIntervalTests(unittest.TestCase):
    def test_known_interval_for_twenty_of_twenty_four(self) -> None:
        self.assertEqual(wilson_interval(20, 24), (0.6415, 0.9332))

    def test_known_interval_for_seven_of_twenty_four(self) -> None:
        self.assertEqual(wilson_interval(7, 24), (0.1491, 0.4917))

    def test_rejects_invalid_counts(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive"):
            wilson_interval(0, 0)
        with self.assertRaisesRegex(ValueError, "between 0 and n"):
            wilson_interval(5, 4)


if __name__ == "__main__":
    unittest.main()
