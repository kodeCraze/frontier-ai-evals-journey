"""
schema.py — the single source of truth for the suite's data model.

Per AGENTS.md §5: this file defines fields, categories, languages, and scoring modes. Change it
here in one place, then update `validate.py` and the docs together. `evaluate.py` imports the same
constants, so the validator and the harness can never drift apart.

Pure standard library. No dependencies.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Iterable, Iterator

# ---------------------------------------------------------------------------
# Suite identity
# ---------------------------------------------------------------------------
SUITE_NAME = "frontier-ai-evals-journey"
SUITE_VERSION = "0.1.0"

# ---------------------------------------------------------------------------
# Enumerations (closed sets — a validator failure if an item uses anything else)
# ---------------------------------------------------------------------------
LANGUAGES: dict[str, str] = {
    "hi": "Hindi",
    "bn": "Bengali",
    "ta": "Tamil",
}

CATEGORIES: dict[str, str] = {
    "grammar_understanding": "Understanding & grammar",
    "culture_knowledge": "Culture & knowledge",
    "reasoning_math": "Reasoning & math",
    "translation": "Translation",
    "instruction_following": "Instruction-following",
    "safety_refusal": "Safety / refusal",
}

SCORING_MODES: tuple[str, ...] = ("exact_match", "reference_based", "rubric")

DIFFICULTIES: tuple[str, ...] = ("easy", "medium", "hard")

STATUSES: tuple[str, ...] = ("verified", "unverified")

DEFAULT_LICENSE = "CC-BY-4.0"

# Fields every item must carry (the key must exist).
# Note: `reference` may be an empty string for open-ended `rubric` items (e.g. safety/refusal
# probes, where the correct behaviour is a refusal and there is no single expected answer).
# For `exact_match` and `reference_based` items a non-empty `reference` is mandatory — enforced
# by validate.py.
REQUIRED_FIELDS: tuple[str, ...] = (
    "id",
    "language",
    "category",
    "difficulty",
    "prompt",
    "reference",
    "scoring",
    "source_note",
    "license",
    "author",
)

# Optional fields (documented so agents do not invent new ones silently).
OPTIONAL_FIELDS: tuple[str, ...] = ("accept", "rubric", "status", "notes")

ID_PATTERN = re.compile(r"^[a-z]{2}-[a-z]{3}-\d{3}$")  # e.g. hi-cul-006

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = REPO_ROOT / "data"
JUDGES_DIR = REPO_ROOT / "judges"


# ---------------------------------------------------------------------------
# Text normalisation — shared by exact-match scoring AND the validator
# ---------------------------------------------------------------------------
# Keeps Unicode letters, combining marks, and numbers (so Devanagari/Bengali/Tamil matras
# survive), turns everything else (punctuation, symbols, brackets, dandas) into spaces, and
# collapses whitespace. Lowercases.
#   "(B)"         -> "b"
#   "I like tea." -> "i like tea"
#   "स्त्रीलिंग"    -> "स्त्रीलिंग"   (matras preserved!)
#   "100 °C"      -> "100 c"
_WS = re.compile(r"\s+", flags=re.UNICODE)


def _is_kept(ch: str) -> bool:
    # L* = letters, M* = marks (vowel signs/matras), N* = numbers. Everything else is a separator.
    return ch.isspace() or unicodedata.category(ch)[0] in ("L", "M", "N")


def normalize(text: object) -> str:
    """Canonical form for string comparison. Deterministic and dependency-free.

    Note: we cannot use ``re.\\w`` here — Python's ``\\w`` excludes combining marks, which would
    strip Devanagari matras (e.g. ``स्त्रीलिंग`` -> ``स त र ल ग``) and corrupt every comparison.
    """
    if text is None:
        return ""
    t = unicodedata.normalize("NFC", str(text)).casefold()
    t = t.replace("।", " ").replace("॥", " ")  # Devanagari danda
    t = "".join(ch if _is_kept(ch) else " " for ch in t)
    return _WS.sub(" ", t).strip()


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def iter_jsonl(path: Path) -> Iterator[tuple[int, dict]]:
    """Yield (line_number, object) for a JSONL file. Raises ValueError on bad JSON."""
    with path.open("r", encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                yield lineno, json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path.name}:{lineno}: invalid JSON ({exc})") from exc


def data_files(langs: Iterable[str] | None = None) -> list[Path]:
    """All data/<lang>.jsonl files, optionally filtered to specific language codes."""
    files = sorted(DATA_DIR.glob("*.jsonl"))
    if langs is not None:
        wanted = {l.strip() for l in langs if l.strip()}
        files = [f for f in files if f.stem in wanted]
    return files


def load_items(langs: Iterable[str] | None = None) -> list[dict]:
    """Load every item, stamping each with its source file for error messages."""
    items: list[dict] = []
    for path in data_files(langs):
        for lineno, obj in iter_jsonl(path):
            obj.setdefault("_source", f"{path.name}:{lineno}")
            items.append(obj)
    return items
