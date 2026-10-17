"""Domain models and dataset validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ALLOWED_LABELS = ("account", "billing", "general", "technical")


@dataclass(frozen=True, slots=True)
class Example:
    """A single labeled evaluation example."""

    id: str
    text: str
    label: str


def load_jsonl(path: Path) -> list[Example]:
    """Load and validate evaluation examples from a JSON Lines file."""

    examples: list[Example] = []
    seen_ids: set[str] = set()

    with path.open(encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            if not raw_line.strip():
                continue
            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSON on line {line_number}: {error.msg}") from error

            if not isinstance(record, dict):
                raise ValueError(f"Line {line_number} must contain a JSON object")

            missing = {"id", "text", "label"} - record.keys()
            if missing:
                missing_text = ", ".join(sorted(missing))
                raise ValueError(f"Line {line_number} is missing fields: {missing_text}")

            non_string_fields = [
                field for field in ("id", "text", "label") if not isinstance(record[field], str)
            ]
            if non_string_fields:
                fields_text = ", ".join(non_string_fields)
                raise ValueError(f"Line {line_number} fields must be strings: {fields_text}")

            example = Example(
                id=record["id"].strip(),
                text=record["text"].strip(),
                label=record["label"].strip(),
            )
            if not example.id or not example.text:
                raise ValueError(f"Line {line_number} has an empty id or text")
            if example.id in seen_ids:
                raise ValueError(f"Duplicate example id: {example.id}")
            if example.label not in ALLOWED_LABELS:
                raise ValueError(
                    f"Unsupported label {example.label!r} on line {line_number}; "
                    f"expected one of {', '.join(ALLOWED_LABELS)}"
                )

            seen_ids.add(example.id)
            examples.append(example)

    if not examples:
        raise ValueError("Evaluation dataset is empty")
    return examples
