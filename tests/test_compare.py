from __future__ import annotations

import unittest

from frontier_eval.compare import compare_reports


def _report(correct: int, failures: list[str], macro_f1: float, ci: list[float]) -> dict:
    return {
        "examples": 4,
        "correct": correct,
        "accuracy": correct / 4,
        "accuracy_ci95": ci,
        "macro_f1": macro_f1,
        "protocol": "test",
        "failures": [{"id": item} for item in failures],
    }


class CompareReportsTests(unittest.TestCase):
    def test_identifies_recovered_and_new_failures(self) -> None:
        comparison = compare_reports(
            _report(3, ["ticket-005", "ticket-012"], 0.8, [0.64, 0.93]),
            _report(2, ["ticket-012", "ticket-002"], 0.4, [0.15, 0.49]),
            _report(4, [], 1.0, [0.5, 1.0]),
        )

        self.assertEqual(comparison["recovered_by_tfidf"], ["ticket-005"])
        self.assertEqual(comparison["new_tfidf_failures"], ["ticket-002"])
        self.assertEqual(comparison["shared_failures"], ["ticket-012"])
        self.assertTrue(comparison["keyword_wins_macro_f1"])
        self.assertFalse(comparison["accuracy_intervals_overlap"])
        self.assertFalse(comparison["tfidf_in_sample_invalid"]["valid"])


if __name__ == "__main__":
    unittest.main()
