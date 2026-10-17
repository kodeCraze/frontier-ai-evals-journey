"""An inspectable baseline used to anchor future model comparisons."""

from __future__ import annotations

import re
from collections import Counter

TOKEN_PATTERN = re.compile(r"[a-z0-9']+")

KEYWORDS: dict[str, frozenset[str]] = {
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

    def predict(self, text: str) -> str:
        """Return the unique highest-scoring label, or `general` for ties and no match."""

        tokens = TOKEN_PATTERN.findall(text.lower())
        scores = Counter(
            {
                label: sum(token in label_keywords for token in tokens)
                for label, label_keywords in KEYWORDS.items()
            }
        )
        best_score = max(scores.values(), default=0)
        if best_score == 0:
            return "general"

        winners = [label for label, score in scores.items() if score == best_score]
        return winners[0] if len(winners) == 1 else "general"
