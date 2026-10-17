"""Command-line interface for reproducible evaluation runs."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from frontier_eval.baseline import KeywordRouter
from frontier_eval.compare import compare_reports
from frontier_eval.evaluator import evaluate
from frontier_eval.models import ALLOWED_LABELS, Example, load_jsonl
from frontier_eval.tfidf import TfidfCentroidRouter, leave_one_out_predictions

METHODS = ("keyword", "tfidf")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate ticket-routing baselines and compare them honestly."
    )
    parser.add_argument("dataset", type=Path, help="Path to a JSON Lines evaluation dataset")
    parser.add_argument("--output", type=Path, help="Optional path for the JSON report")
    parser.add_argument(
        "--method",
        choices=METHODS,
        default="keyword",
        help="Single method to evaluate. keyword is the default transparent baseline.",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Evaluate keyword and TF-IDF together, including the invalid in-sample leak.",
    )
    return parser


def reject_dataset_overwrite(parser: argparse.ArgumentParser, dataset: Path, output: Path) -> None:
    same_resolved_path = dataset.resolve() == output.resolve()
    same_existing_file = dataset.exists() and output.exists() and dataset.samefile(output)
    if same_resolved_path or same_existing_file:
        parser.error("dataset and output paths must be different")


def evaluate_keyword(examples: Sequence[Example]) -> dict[str, Any]:
    report = evaluate(examples, KeywordRouter().predict)
    report["method"] = "keyword"
    report["protocol"] = "full"
    return report


def evaluate_tfidf_leave_one_out(examples: Sequence[Example]) -> dict[str, Any]:
    report = evaluate(examples, predictions=leave_one_out_predictions(examples))
    report["method"] = "tfidf"
    report["protocol"] = "leave-one-out"
    return report


def evaluate_tfidf_in_sample(examples: Sequence[Example]) -> dict[str, Any]:
    router = TfidfCentroidRouter()
    router.fit(examples)
    report = evaluate(examples, router.predict)
    report["method"] = "tfidf"
    report["protocol"] = "in-sample"
    return report


def render_summary(report: dict[str, Any]) -> str:
    title = {
        "keyword": "Frontier AI evaluation — keyword baseline",
        "tfidf": "Frontier AI evaluation — TF-IDF centroid",
    }.get(report.get("method", "keyword"), "Frontier AI evaluation")
    lines = [
        title,
        f"Protocol: {report.get('protocol', 'full')}",
        f"Examples: {report['examples']}",
        f"Accuracy: {report['accuracy']:.1%}",
        (
            "Accuracy 95% CI: "
            f"[{report['accuracy_ci95'][0]:.3f}, {report['accuracy_ci95'][1]:.3f}]"
        ),
        f"Macro F1: {report['macro_f1']:.3f}",
        "",
        "Per-label metrics:",
    ]
    for label in ALLOWED_LABELS:
        metrics = report["per_label"][label]
        lines.append(
            f"  {label:<10} precision={metrics['precision']:.3f} "
            f"recall={metrics['recall']:.3f} f1={metrics['f1']:.3f} "
            f"support={metrics['support']}"
        )
    lines.extend(["", f"Failures: {len(report['failures'])}"])
    for failure in report["failures"]:
        lines.append(
            f"  {failure['id']}: expected={failure['expected']} "
            f"predicted={failure['predicted']} — {failure['text']}"
        )
    return "\n".join(lines)


def render_comparison(comparison: dict[str, Any]) -> str:
    keyword = comparison["keyword"]
    tfidf = comparison["tfidf_leave_one_out"]
    leaked = comparison.get("tfidf_in_sample_invalid")
    lines = [
        "Frontier AI evaluation — method comparison",
        (
            f"Keyword: {keyword['accuracy']:.1%} accuracy, "
            f"macro F1 {keyword['macro_f1']:.3f}, "
            f"CI [{keyword['accuracy_ci95'][0]:.3f}, {keyword['accuracy_ci95'][1]:.3f}]"
        ),
        (
            f"TF-IDF leave-one-out: {tfidf['accuracy']:.1%} accuracy, "
            f"macro F1 {tfidf['macro_f1']:.3f}, "
            f"CI [{tfidf['accuracy_ci95'][0]:.3f}, {tfidf['accuracy_ci95'][1]:.3f}]"
        ),
    ]
    if leaked is not None:
        lines.append(
            f"TF-IDF in-sample (invalid): {leaked['accuracy']:.1%} accuracy — not a valid result"
        )
    lines.extend(
        [
            f"Recovered by TF-IDF: {', '.join(comparison['recovered_by_tfidf']) or 'none'}",
            f"New TF-IDF failures: {', '.join(comparison['new_tfidf_failures']) or 'none'}",
            f"Shared failures: {', '.join(comparison['shared_failures']) or 'none'}",
            (
                "Keyword remains the better measured baseline"
                if comparison["keyword_wins_macro_f1"]
                else "TF-IDF leave-one-out improved macro F1"
            ),
        ]
    )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.output is not None:
        reject_dataset_overwrite(parser, args.dataset, args.output)

    examples = load_jsonl(args.dataset)
    if args.compare:
        keyword_report = evaluate_keyword(examples)
        tfidf_report = evaluate_tfidf_leave_one_out(examples)
        leaked_report = evaluate_tfidf_in_sample(examples)
        payload = compare_reports(keyword_report, tfidf_report, leaked_report)
        print(render_comparison(payload))
        report: dict[str, Any] = payload
    elif args.method == "tfidf":
        report = evaluate_tfidf_leave_one_out(examples)
        print(render_summary(report))
    else:
        report = evaluate_keyword(examples)
        print(render_summary(report))

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"\nJSON report written to {args.output}")
    return 0
