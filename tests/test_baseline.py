from __future__ import annotations

import unittest

from frontier_eval.baseline import KeywordRouter


class KeywordRouterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.router = KeywordRouter()

    def test_routes_clear_billing_language(self) -> None:
        self.assertEqual(self.router.predict("Please refund the duplicate charge"), "billing")

    def test_routes_clear_technical_language(self) -> None:
        self.assertEqual(self.router.predict("The API times out with an error"), "technical")

    def test_uses_general_for_unknown_language(self) -> None:
        self.assertEqual(self.router.predict("I need help choosing a plan"), "general")

    def test_tie_with_general_uses_safe_fallback(self) -> None:
        self.assertEqual(self.router.predict("password question"), "general")

    def test_tie_without_general_uses_safe_fallback(self) -> None:
        self.assertEqual(self.router.predict("password charge"), "general")


if __name__ == "__main__":
    unittest.main()
