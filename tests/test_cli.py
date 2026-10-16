from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from frontier_eval.cli import main


class CliTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()

