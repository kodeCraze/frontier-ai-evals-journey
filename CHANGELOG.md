# Changelog

All notable changes to the **suite** (items, schema, scoring) are recorded here.
Format: [Keep a Changelog](https://keepachangelog.com/). Versioning: [SemVer](https://semver.org/).

## [Unreleased]

### Added
- **First real model results** on the 30 Hindi items: `Qwen/Qwen3-0.6B` (60.1%) and
  `Qwen/Qwen3.5-0.8B` (66.2%), temperature 0. Tables in `results/hf/summary.md`; run log in
  `notes/2026-10-18-first-real-runs.md`.
- CircleCI config (`.circleci/config.yml`) as a CI fallback.
- `--max-new-tokens` flag for the `hf`/`openai`/`anthropic` backends.

### Fixed
- **`schema.normalize()` corrupted non-Latin scripts.** It used `re.\w`, which excludes Unicode
  combining marks, silently deleting Devanagari matras (`स्त्रीलिंग` → `स त र ल ग`) and invalidating
  every string comparison. Now keeps Unicode categories L/M/N.
- `summary.md` now aggregates **all** models from disk instead of showing only the last run.
- HF backend made robust to transformers v5 (`dtype` arg, `BatchEncoding` from
  `apply_chat_template`) and to missing `accelerate`.

### Planned
- Bengali (`bn`) and Tamil (`ta`) items (100 each).
- LLM-judge reliability study (run the judge twice; report agreement).
- Contamination checks against common pretraining corpora.

## [0.1.0] — 2026-10-18

### Added
- Initial suite: **30 Hindi items** across six categories
  (grammar/understanding 5, culture/knowledge 6, reasoning/math 6, translation 6,
  instruction-following 4, safety/refusal 3).
- `schema.py` — single source of truth for fields, categories, languages, scoring modes.
- `validate.py` — schema + integrity checks; wired into CI.
- `evaluate.py` — generation + scoring harness with `mock`, `hf`, `openai`, `anthropic` backends;
  `exact_match`, `reference_based` (chrF), and `rubric` scoring.
- `judges/` — published 0–2 rubric and judge prompt templates.
- Governance: `AGENTS.md` (binding rules) and `CLAUDE.md`.

### Notes
- No real model results yet. `results/summary.md` ships a labelled `mock` smoke test only.
