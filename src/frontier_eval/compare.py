"""Compare two evaluation reports without hiding disagreements."""

from __future__ import annotations

from typing import Any


def _summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "examples": report["examples"],
        "correct": report["correct"],
        "accuracy": report["accuracy"],
        "accuracy_ci95": report["accuracy_ci95"],
        "macro_f1": report["macro_f1"],
        "protocol": report.get("protocol"),
        "failure_ids": [failure["id"] for failure in report["failures"]],
    }


def compare_reports(
    keyword_report: dict[str, Any],
    tfidf_report: dict[str, Any],
    tfidf_in_sample: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Describe where the representation baseline helps, hurts, or leaks."""

    keyword_failures = {failure["id"] for failure in keyword_report["failures"]}
    tfidf_failures = {failure["id"] for failure in tfidf_report["failures"]}
    keyword_low, keyword_high = keyword_report["accuracy_ci95"]
    tfidf_low, tfidf_high = tfidf_report["accuracy_ci95"]
    comparison = {
        "keyword": _summary(keyword_report),
        "tfidf_leave_one_out": _summary(tfidf_report),
        "recovered_by_tfidf": sorted(keyword_failures - tfidf_failures),
        "new_tfidf_failures": sorted(tfidf_failures - keyword_failures),
        "shared_failures": sorted(keyword_failures & tfidf_failures),
        "keyword_wins_macro_f1": keyword_report["macro_f1"] > tfidf_report["macro_f1"],
        "accuracy_intervals_overlap": not (keyword_high < tfidf_low or tfidf_high < keyword_low),
    }
    if tfidf_in_sample is not None:
        comparison["tfidf_in_sample_invalid"] = {
            **_summary(tfidf_in_sample),
            "valid": False,
            "reason": (
                "Training and evaluating on the same examples leaks each ticket "
                "into the representation, so in-sample accuracy is not evidence."
            ),
        }
    return comparison
