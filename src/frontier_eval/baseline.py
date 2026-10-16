"""An inspectable baseline used to anchor future model comparisons."""

from __future__ import annotations

import re
from collections import Counter

TOKEN_PATTERN = re.compile(r"[a-z0-9']+")

DEFAULT_KEYWORDS: dict[str, frozenset[str]] = {
    "account": frozenset(
        {
            "account",
            "email",
            "identity",
            "login",
            "password",
            "profile",
            "signin",
            "username",
            "verification",
        }
    ),
    "billing": frozenset(
        {
            "bill",
            "billing",
            "card",
            "charge",
            "charged",
            "invoice",
            "payment",
            "price",
            "receipt",
            "refund",
            "subscription",
        }
    ),
    "technical": frozenset(
        {
            "api",
            "bug",
            "crash",
            "error",
            "failed",
            "integration",
            "latency",
            "loading",
            "outage",
            "slow",
            "timeout",
            "website",
        }
    ),
    "general": frozenset(
        {
            "documentation",
            "feedback",
            "feature",
            "guide",
            "hello",
            "hours",
            "question",
            "roadmap",
            "support",
            "tutorial",
        }
    ),
}


class KeywordRouter:
    """Route text by counting label-specific keyword matches."""

    def __init__(
        self,
        keywords: dict[str, frozenset[str]] | None = None,
        fallback_label: str = "general",
    ) -> None:
        self.keywords = keywords or DEFAULT_KEYWORDS
        if fallback_label not in self.keywords:
            raise ValueError("Fallback label must be present in the keyword mapping")
        self.fallback_label = fallback_label

    def predict(self, text: str) -> str:
        """Return the highest-scoring label with a stable fallback for ties."""

        tokens = TOKEN_PATTERN.findall(text.lower())
        scores = Counter(
            {
                label: sum(token in label_keywords for token in tokens)
                for label, label_keywords in self.keywords.items()
            }
        )
        best_score = max(scores.values(), default=0)
        if best_score == 0:
            return self.fallback_label

        winners = sorted(label for label, score in scores.items() if score == best_score)
        if self.fallback_label in winners:
            return self.fallback_label
        return winners[0]

