> ## ⚠️ MOCK — NOT REAL MODEL RESULTS
>
> The `mock` backend returns **synthetic** answers to exercise the pipeline.
> **No number below is a performance claim.** Run a real backend before quoting anything.

# Results — backend `mock`

## Run metadata

- backend: `mock`  ·  judge: `heuristic`
- suite version: `0.1.0`  ·  git: `8976f7c`
- timestamp: `2026-10-18T08:32:02+00:00`  ·  seed: `0`  ·  temperature: 0
- disclaimer: MOCK — NOT REAL MODEL RESULTS
- ⚠️ rubric scores used the **heuristic** judge (not a real rubric score); run with `--judge <model>` for LLM-judged rubric items.

## Overall

| Model | Language | N | overall | exact-match | chrF | rubric (0–2) |
|---|---|---|---|---|---|---|
| `mock-model` | Hindi (`hi`) | 30 | 75.0% | 66.7% | 100.0% | 1.50 |
| **`mock-model`** | **All** | 30 | 75.0% | 66.7% | 100.0% | 1.50 |

## By category (overall score)

| Model | Understanding & grammar | Culture & knowledge | Reasoning & math | Translation | Instruction-following | Safety / refusal |
|---|---|---|---|---|---|---|
| `mock-model` | 60.0% | 66.7% | 66.7% | 100.0% | 100.0% | 50.0% |

## Failure gallery

Failures are shown on purpose (AGENTS.md §4) — they are the most informative part.

### `mock-model` — 6 zero-scored item(s)

- **`hi-grm-001`** (grammar_understanding) — response: `(A) कागज़`
- **`hi-grm-004`** (grammar_understanding) — response: `(A) जाती है`
- **`hi-cul-008`** (culture_knowledge) — response: `(B) दिल्ली`
- **`hi-cul-010`** (culture_knowledge) — response: `(A) गंगा`
- **`hi-rea-014`** (reasoning_math) — response: `«mock: deliberately wrong answer»`
- **`hi-rea-016`** (reasoning_math) — response: `«mock: deliberately wrong answer»`

