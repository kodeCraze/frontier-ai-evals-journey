# Changelog

All notable changes to the **suite** (items, schema, scoring) are recorded here.
Format: [Keep a Changelog](https://keepachangelog.com/). Versioning: [SemVer](https://semver.org/).

## [Unreleased]

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
