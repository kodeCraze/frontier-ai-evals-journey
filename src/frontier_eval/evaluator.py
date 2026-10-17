"""Metrics and failure analysis for single-label classification."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from frontier_eval.models import ALLOWED_LABELS, Example


def _safe_divide(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def evaluate(examples: Iterable[Example], predict: Callable[[str], str]) -> dict[str, Any]:
    """Evaluate a predictor and retain aggregate and example-level evidence."""

    rows = list(examples)
    if not rows:
        raise ValueError("At least one example is required")

    confusion = {
        expected: {predicted: 0 for predicted in ALLOWED_LABELS} for expected in ALLOWED_LABELS
    }
    failures: list[dict[str, str]] = []
    correct = 0

    for example in rows:
        predicted = predict(example.text)
        if predicted not in ALLOWED_LABELS:
            raise ValueError(f"Predictor returned unsupported label: {predicted!r}")
        confusion[example.label][predicted] += 1
        if predicted == example.label:
            correct += 1
        else:
            failures.append(
                {
                    "id": example.id,
                    "text": example.text,
                    "expected": example.label,
                    "predicted": predicted,
                }
            )

    per_label: dict[str, dict[str, float | int]] = {}
    f1_scores: list[float] = []
    for label in ALLOWED_LABELS:
        true_positive = confusion[label][label]
        predicted_total = sum(confusion[expected][label] for expected in ALLOWED_LABELS)
        actual_total = sum(confusion[label].values())
        precision = _safe_divide(true_positive, predicted_total)
        recall = _safe_divide(true_positive, actual_total)
        f1 = _safe_divide(2 * precision * recall, precision + recall)
        f1_scores.append(f1)
        per_label[label] = {
            "support": actual_total,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        }

    return {
        "examples": len(rows),
        "correct": correct,
        "accuracy": round(correct / len(rows), 4),
        "macro_f1": round(sum(f1_scores) / len(f1_scores), 4),
        "per_label": per_label,
        "confusion_matrix": confusion,
        "failures": failures,
    }
