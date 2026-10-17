from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from frontier_eval.models import load_jsonl


class DatasetLoadingTests(unittest.TestCase):
    def write_dataset(self, content: str) -> Path:
        temporary_directory = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(temporary_directory.cleanup)
        path = Path(temporary_directory.name) / "dataset.jsonl"
        path.write_text(content, encoding="utf-8")
        return path

    def test_loads_valid_examples(self) -> None:
        path = self.write_dataset('{"id":"1","text":"hello","label":"general"}\n')

        examples = load_jsonl(path)

        self.assertEqual(len(examples), 1)
        self.assertEqual(examples[0].text, "hello")

    def test_rejects_duplicate_ids(self) -> None:
        path = self.write_dataset(
            '{"id":"1","text":"hello","label":"general"}\n'
            '{"id":"1","text":"again","label":"general"}\n'
        )

        with self.assertRaisesRegex(ValueError, "Duplicate example id"):
            load_jsonl(path)

    def test_rejects_unknown_labels(self) -> None:
        path = self.write_dataset('{"id":"1","text":"hello","label":"mystery"}\n')

        with self.assertRaisesRegex(ValueError, "Unsupported label"):
            load_jsonl(path)

    def test_rejects_non_string_fields(self) -> None:
        records = {
            "id": '{"id":null,"text":"hello","label":"general"}\n',
            "text": '{"id":"1","text":{},"label":"general"}\n',
            "label": '{"id":"1","text":"hello","label":7}\n',
        }

        for field, content in records.items():
            with self.subTest(field=field):
                path = self.write_dataset(content)
                with self.assertRaisesRegex(ValueError, "fields must be strings"):
                    load_jsonl(path)


if __name__ == "__main__":
    unittest.main()

