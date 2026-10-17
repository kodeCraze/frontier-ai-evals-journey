from __future__ import annotations

import unittest

from frontier_eval.evaluator import evaluate
from frontier_eval.models import Example


class EvaluatorTests(unittest.TestCase):
    def test_reports_metrics_confusion_and_failures(self) -> None:
        examples = [
            Example("1", "one", "account"),
            Example("2", "two", "billing"),
            Example("3", "three", "general"),
            Example("4", "four", "technical"),
        ]
        predictions = {
            "one": "account",
            "two": "general",
            "three": "general",
            "four": "technical",
        }

        report = evaluate(examples, predictions.__getitem__)

        self.assertEqual(report["examples"], 4)
        self.assertEqual(report["correct"], 3)
        self.assertEqual(report["accuracy"], 0.75)
        self.assertEqual(report["confusion_matrix"]["billing"]["general"], 1)
        self.assertEqual(report["failures"][0]["id"], "2")
        self.assertEqual(report["per_label"]["billing"]["recall"], 0.0)

    def test_rejects_empty_evaluation(self) -> None:
        with self.assertRaisesRegex(ValueError, "At least one example"):
            evaluate([], lambda _: "general")

    def test_rejects_unknown_predictor_label(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported label"):
            evaluate([Example("1", "hello", "general")], lambda _: "other")


if __name__ == "__main__":
    unittest.main()
