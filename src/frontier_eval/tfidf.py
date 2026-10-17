"""Inspectable TF-IDF representations used as a second routing baseline."""

from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Sequence

from frontier_eval.models import ALLOWED_LABELS, Example

TOKEN_PATTERN = re.compile(r"[a-z0-9']+")


def tokenize(text: str) -> list[str]:
    """Split text into lowercase word tokens."""

    return TOKEN_PATTERN.findall(text.lower())


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    """Return cosine similarity, or 0.0 when either vector has no magnitude."""

    dot = sum(left_value * right_value for left_value, right_value in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot / (left_norm * right_norm)


def _mean_vector(vectors: Sequence[Sequence[float]]) -> list[float]:
    dimension = len(vectors[0])
    totals = [0.0] * dimension
    for vector in vectors:
        for index, value in enumerate(vector):
            totals[index] += value
    count = len(vectors)
    return [value / count for value in totals]


class TfidfVectorizer:
    """Fit smoothed inverse-document-frequency weights on a training corpus."""

    def __init__(self) -> None:
        self.vocabulary: tuple[str, ...] = ()
        self.idf: tuple[float, ...] = ()
        self._index: dict[str, int] = {}

    def fit(self, texts: Sequence[str]) -> None:
        if not texts:
            raise ValueError("At least one training document is required")

        document_frequency: Counter[str] = Counter()
        for text in texts:
            document_frequency.update(set(tokenize(text)))

        vocabulary = tuple(sorted(document_frequency))
        document_count = len(texts)
        self.vocabulary = vocabulary
        self._index = {term: index for index, term in enumerate(vocabulary)}
        self.idf = tuple(
            math.log((document_count + 1) / (document_frequency[term] + 1)) + 1.0
            for term in vocabulary
        )

    def transform(self, text: str) -> list[float]:
        if not self.vocabulary:
            raise RuntimeError("TfidfVectorizer.transform called before fit")

        counts = Counter(tokenize(text))
        vector = [0.0] * len(self.vocabulary)
        for term, count in counts.items():
            index = self._index.get(term)
            if index is not None:
                vector[index] = count * self.idf[index]
        return vector


class TfidfCentroidRouter:
    """Route text to the nearest label centroid in TF-IDF space."""

    def __init__(self) -> None:
        self._vectorizer = TfidfVectorizer()
        self._centroids: dict[str, list[float]] = {}

    def fit(self, examples: Sequence[Example]) -> None:
        """Learn label centroids from training examples only."""

        rows = list(examples)
        if not rows:
            raise ValueError("At least one training example is required")

        self._vectorizer.fit([example.text for example in rows])
        grouped: dict[str, list[list[float]]] = {label: [] for label in ALLOWED_LABELS}
        for example in rows:
            grouped[example.label].append(self._vectorizer.transform(example.text))
        self._centroids = {
            label: _mean_vector(vectors) for label, vectors in grouped.items() if vectors
        }

    def predict(self, text: str) -> str:
        """Return the unique nearest centroid, or `general` for ties and no signal."""

        if not self._centroids:
            raise RuntimeError("TfidfCentroidRouter.predict called before fit")

        query = self._vectorizer.transform(text)
        scores = {
            label: cosine_similarity(query, centroid) for label, centroid in self._centroids.items()
        }
        best_score = max(scores.values(), default=0.0)
        if best_score <= 0.0:
            return "general"

        winners = [label for label, score in scores.items() if math.isclose(score, best_score)]
        return winners[0] if len(winners) == 1 else "general"


def leave_one_out_predictions(examples: Sequence[Example]) -> list[str]:
    """Predict each example from a router trained on every other example."""

    rows = list(examples)
    if len(rows) < 2:
        raise ValueError("Leave-one-out evaluation requires at least two examples")

    predictions: list[str] = []
    for index, held_out in enumerate(rows):
        trainer = TfidfCentroidRouter()
        trainer.fit([example for skip, example in enumerate(rows) if skip != index])
        predictions.append(trainer.predict(held_out.text))
    return predictions
