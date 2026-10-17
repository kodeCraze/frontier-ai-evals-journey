"""Command-line interface for reproducible evaluation runs."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from frontier_eval.baseline import KeywordRouter
from frontier_eval.evaluator import evaluate
from frontier_eval.models import ALLOWED_LABELS, load_jsonl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate the transparent keyword-routing baseline."
    )
    parser.add_argument("dataset", type=Path, help="Path to a JSON Lines evaluation dataset")
    parser.add_argument("--output", type=Path, help="Optional path for the JSON report")
    return parser


def render_summary(report: dict[str, Any]) -> str:
    lines = [
        "Frontier AI evaluation — keyword baseline",
        f"Examples: {report['examples']}",
        f"Accuracy: {report['accuracy']:.1%}",
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


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.output is not None:
        same_resolved_path = args.dataset.resolve() == args.output.resolve()
        same_existing_file = (
            args.dataset.exists() and args.output.exists() and args.dataset.samefile(args.output)
        )
        if same_resolved_path or same_existing_file:
            parser.error("dataset and output paths must be different")

    examples = load_jsonl(args.dataset)
    report = evaluate(examples, KeywordRouter().predict)
    print(render_summary(report))

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"\nJSON report written to {args.output}")
    return 0
