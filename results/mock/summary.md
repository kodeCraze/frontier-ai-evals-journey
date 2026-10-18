> ## ⚠️ MOCK — NOT REAL MODEL RESULTS
>
> The `mock` backend returns **synthetic** answers to exercise the pipeline.
> **No number below is a performance claim.** Run a real backend before quoting anything.

# Results — `mock` / `mock-model`

## Run metadata

- backend: `mock`  ·  model: `mock-model`
- judge: `heuristic` (heuristic judges are **not** real rubric scores)
- suite version: `0.1.0`  ·  git: `unknown`
- timestamp: `2026-10-18T07:38:43+00:00`  ·  seed: `0`  ·  temperature: 0
- disclaimer: MOCK — NOT REAL MODEL RESULTS

## Overall

| Language | N | overall | exact-match | chrF | rubric (0–2) |
|---|---|---|---|---|---|
| Hindi (`hi`) | 30 | 75.0% | 66.7% | 100.0% | 1.50 |
| **All** | 30 | 75.0% | 66.7% | 100.0% | 1.50 |

## By category

| Category | N | overall |
|---|---|---|
| Culture & knowledge | 6 | 66.7% |
| Understanding & grammar | 5 | 60.0% |
| Instruction-following | 4 | 100.0% |
| Reasoning & math | 6 | 66.7% |
| Safety / refusal | 3 | 50.0% |
| Translation | 6 | 100.0% |

## Failure gallery (6 zero-scored items)

Failures are shown on purpose (AGENTS.md §4) — they are the most informative part.

- **`hi-grm-001`** (grammar_understanding) — response: `(A) कागज़`
- **`hi-grm-004`** (grammar_understanding) — response: `(D) जाना`
- **`hi-cul-008`** (culture_knowledge) — response: `(B) दिल्ली`
- **`hi-cul-010`** (culture_knowledge) — response: `(A) गंगा`
- **`hi-rea-014`** (reasoning_math) — response: `«mock: deliberately wrong answer»`
- **`hi-rea-016`** (reasoning_math) — response: `«mock: deliberately wrong answer»`
