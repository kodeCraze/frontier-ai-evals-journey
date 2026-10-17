from __future__ import annotations

import unittest

from frontier_eval.models import Example
from frontier_eval.tfidf import TfidfCentroidRouter, leave_one_out_predictions


class TfidfCentroidRouterTests(unittest.TestCase):
    def fit_router(self) -> TfidfCentroidRouter:
        router = TfidfCentroidRouter()
        router.fit(
            [
                Example("a1", "password login email", "account"),
                Example("b1", "invoice payment refund", "billing"),
                Example("g1", "documentation question tutorial", "general"),
                Example("t1", "api error timeout", "technical"),
            ]
        )
        return router

    def test_routes_clear_account_language(self) -> None:
        self.assertEqual(self.fit_router().predict("reset password login"), "account")

    def test_uses_general_when_query_has_no_trained_tokens(self) -> None:
        self.assertEqual(self.fit_router().predict("zzzz unknown tokens"), "general")

    def test_uses_general_for_equal_cosine_scores(self) -> None:
        router = TfidfCentroidRouter()
        router.fit(
            [
                Example("a1", "sharedtoken", "account"),
                Example("b1", "sharedtoken", "billing"),
            ]
        )

        self.assertEqual(router.predict("sharedtoken"), "general")

    def test_predict_before_fit_fails(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "before fit"):
            TfidfCentroidRouter().predict("password login")

    def test_empty_training_set_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "At least one training example"):
            TfidfCentroidRouter().fit([])


class LeaveOneOutTests(unittest.TestCase):
    def test_does_not_use_held_out_tokens(self) -> None:
        examples = [
            Example("a1", "password login email", "account"),
            Example("b1", "invoice payment refund", "billing"),
            Example("g1", "documentation question tutorial", "general"),
            Example("t1", "api error timeout", "technical"),
            Example("t2", "uniqueklaxon uniqueklaxon uniqueklaxon", "technical"),
        ]
        router = TfidfCentroidRouter()
        router.fit(examples)

        self.assertEqual(router.predict("uniqueklaxon uniqueklaxon uniqueklaxon"), "technical")
        self.assertEqual(leave_one_out_predictions(examples)[4], "general")

    def test_requires_two_examples(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least two examples"):
            leave_one_out_predictions([Example("1", "password login", "account")])


if __name__ == "__main__":
    unittest.main()
