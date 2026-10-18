"""
validate.py — schema + integrity checks for the suite.

Run:  python validate.py          (exits 0 if the data is sound, 1 otherwise)

This is the guardrail described in AGENTS.md §5 ("validate before you commit"). CI runs it on
every push and PR. It checks structure, enums, uniqueness, and — importantly — the integrity rules
we promised: no unsourced factual items, no missing licences, no copied/duplicate items.
"""

from __future__ import annotations

import sys
from collections import Counter

import schema


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    files = schema.data_files()
    if not files:
        print("validate: no data/*.jsonl files found")
        return 1

    seen_ids: dict[str, str] = {}          # id -> source
    seen_prompts: dict[str, str] = {}      # normalised prompt -> id
    per_lang = Counter()
    per_cat = Counter()
    per_scoring = Counter()
    per_lang_cat: Counter = Counter()

    for path in files:
        lang_from_name = path.stem
        if lang_from_name not in schema.LANGUAGES:
            warnings.append(f"{path.name}: filename is not a known language code "
                            f"({', '.join(schema.LANGUAGES)})")

        for lineno, item in schema.iter_jsonl(path):
            where = f"{path.name}:{lineno}"

            # --- required fields (if any are missing, the rest of this item is uncheckable) ---
            # `reference` must be *present* but may be "" for open-ended rubric items; the
            # scoring-specific check further below enforces a non-empty reference for the
            # exact_match / reference_based modes.
            missing = [f for f in schema.REQUIRED_FIELDS if f != "reference"
                       if f not in item or item[f] in (None, "", [])]
            if "reference" not in item:
                missing.append("reference")
            for field in missing:
                errors.append(f"{where}: missing required field '{field}'")
            if missing:
                continue

            # --- unexpected fields (documented schema only) ---
            allowed = set(schema.REQUIRED_FIELDS) | set(schema.OPTIONAL_FIELDS) | {"_source"}
            for field in item:
                if field not in allowed:
                    warnings.append(f"{where}: unexpected field '{field}' (not in schema)")

            lang = item.get("language")
            cat = item.get("category")
            scoring = item.get("scoring")
            difficulty = item.get("difficulty")
            item_id = item.get("id", "")
            prompt = item.get("prompt", "")

            # --- enums ---
            if lang not in schema.LANGUAGES:
                errors.append(f"{where}: unknown language '{lang}'")
            elif lang != lang_from_name:
                errors.append(f"{where}: language '{lang}' does not match filename '{path.stem}'")
            if cat not in schema.CATEGORIES:
                errors.append(f"{where}: unknown category '{cat}'")
            if scoring not in schema.SCORING_MODES:
                errors.append(f"{where}: unknown scoring mode '{scoring}'")
            if difficulty not in schema.DIFFICULTIES:
                errors.append(f"{where}: unknown difficulty '{difficulty}'")

            # --- id format + uniqueness ---
            if not schema.ID_PATTERN.match(str(item_id)):
                errors.append(f"{where}: id '{item_id}' does not match "
                              f"pattern <lang>-<cat3>-<NNN>")
            if item_id in seen_ids:
                errors.append(f"{where}: duplicate id '{item_id}' (also {seen_ids[item_id]})")
            else:
                seen_ids[item_id] = where

            # --- duplicate prompt detection (no near-identical items) ---
            nprompt = schema.normalize(prompt)
            if nprompt and nprompt in seen_prompts:
                errors.append(f"{where}: duplicate prompt (same as {seen_prompts[nprompt]})")
            elif nprompt:
                seen_prompts[nprompt] = where

            # --- scoring-mode requirements ---
            if scoring in ("exact_match", "reference_based") and not str(item.get("reference", "")).strip():
                errors.append(f"{where}: scoring='{scoring}' needs a non-empty 'reference'")
            if scoring == "rubric":
                if not str(item.get("rubric", "")).strip():
                    errors.append(f"{where}: rubric item needs a 'rubric' string")

            # --- integrity rules (AGENTS.md §1 and §2) ---
            source_note = str(item.get("source_note", "")).strip()
            if len(source_note) < 15:
                errors.append(f"{where}: 'source_note' too short/vague (need a checkable source)")
            if cat == "culture_knowledge" and "authored" not in source_note.lower() \
                    and "verified" not in source_note.lower() and "per " not in source_note.lower():
                warnings.append(f"{where}: culture item source_note lacks a verification phrase")

            if item.get("license") != schema.DEFAULT_LICENSE:
                warnings.append(f"{where}: licence is '{item.get('license')}' "
                                f"(suite default is {schema.DEFAULT_LICENSE})")

            accept = item.get("accept")
            if accept is not None:
                if not isinstance(accept, list) or not all(isinstance(a, str) for a in accept):
                    errors.append(f"{where}: 'accept' must be a list of strings")

            status = item.get("status", "verified")
            if status not in schema.STATUSES:
                errors.append(f"{where}: unknown status '{status}'")
            if status == "unverified":
                warnings.append(f"{where}: item marked 'unverified' — must not count in headline "
                                f"numbers (AGENTS.md §1)")

            # --- tally ---
            per_lang[lang] += 1
            per_cat[cat] += 1
            per_scoring[scoring] += 1
            per_lang_cat[(lang, cat)] += 1

    # --- report ---
    total = sum(per_lang.values())
    print(f"validate: {total} items across {len(files)} file(s)")
    print("\nper language:")
    for lang, name in schema.LANGUAGES.items():
        if per_lang[lang]:
            print(f"  {lang} ({name}): {per_lang[lang]}")
    print("\nper category:")
    for cat, label in schema.CATEGORIES.items():
        print(f"  {label}: {per_cat[cat]}")
    print("\nper scoring mode:")
    for mode in schema.SCORING_MODES:
        print(f"  {mode}: {per_scoring[mode]}")

    if warnings:
        print(f"\n{len(warnings)} warning(s):")
        for w in warnings:
            print(f"  ! {w}")

    if errors:
        print(f"\n{len(errors)} ERROR(s):")
        for e in errors:
            print(f"  x {e}")
        print("\nvalidate: FAILED")
        return 1

    print("\nvalidate: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
