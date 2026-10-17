from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from frontier_eval.cli import main


class CliTests(unittest.TestCase):
    def assert_output_alias_rejected(self, dataset: Path, output: Path, original: str) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaisesRegex(SystemExit, "2"):
                main([str(dataset), "--output", str(output)])

        self.assertEqual(dataset.read_text(encoding="utf-8"), original)

    def test_writes_report_and_prints_summary(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            root = Path(directory)
            dataset = root / "dataset.jsonl"
            output = root / "report.json"
            dataset.write_text(
                '{"id":"1","text":"refund my charge","label":"billing"}\n'
                '{"id":"2","text":"api error","label":"technical"}\n',
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main([str(dataset), "--output", str(output)])

            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["accuracy"], 1.0)
            self.assertIn("Accuracy: 100.0%", stdout.getvalue())

    def test_rejects_same_output_path_as_dataset(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            root = Path(directory)
            dataset = root / "dataset.jsonl"
            original = '{"id":"1","text":"hello","label":"general"}\n'
            dataset.write_text(original, encoding="utf-8")

            self.assert_output_alias_rejected(dataset, dataset, original)

    def test_rejects_normalized_output_path_alias(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            root = Path(directory)
            dataset = root / "dataset.jsonl"
            original = '{"id":"1","text":"hello","label":"general"}\n'
            dataset.write_text(original, encoding="utf-8")
            equivalent_output = root / "nested" / ".." / "dataset.jsonl"

            self.assert_output_alias_rejected(dataset, equivalent_output, original)

    def test_rejects_hard_link_output_alias(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            root = Path(directory)
            dataset = root / "dataset.jsonl"
            output = root / "report.json"
            original = '{"id":"1","text":"hello","label":"general"}\n'
            dataset.write_text(original, encoding="utf-8")
            try:
                os.link(dataset, output)
            except OSError as error:
                self.skipTest(f"hard links are unavailable: {error}")

            self.assert_output_alias_rejected(dataset, output, original)


if __name__ == "__main__":
    unittest.main()
