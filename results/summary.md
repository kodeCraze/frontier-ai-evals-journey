> **Status update:** real model results now exist (2 open models, Hindi). This file remains the
> index; the live tables are in `results/hf/summary.md`.

# Results index

The per-run tables live in `results/<backend>/summary.md`. This file says which are real.

## What exists today

| Output | Meaning | Is it a real result? |
|---|---|---|
| `results/hf/summary.md` | Local open models (Qwen3-0.6B, Qwen3.5-0.8B) on 30 Hindi items | ✅ **Yes** (rubric column used the heuristic judge) |
| `results/mock/summary.md` | Pipeline smoke test with synthetic answers | ❌ **No — `MOCK — NOT REAL MODEL RESULTS`** |
| `results/openai/summary.md` | API-model runs | ⏳ not yet produced |
| `results/anthropic/summary.md` | API-model runs | ⏳ not yet produced |

## First real result — Hindi, 30 items, temperature 0, seed 0

| Model | overall | exact-match | chrF | rubric (0–2)\* |
|---|---|---|---|---|
| `Qwen/Qwen3-0.6B` | 60.1% | 55.6% | 67.2% | 1.33 |
| `Qwen/Qwen3.5-0.8B` | 66.2% | 61.1% | 89.5% | 1.17 |

\* Heuristic judge — not a real rubric score. Reproduce with:

```bash
python validate.py
python evaluate.py --backend hf --models "Qwen/Qwen3-0.6B,Qwen/Qwen3.5-0.8B" --langs hi
```

Run log: `../notes/2026-10-18-first-real-runs.md`.

## Honest limitations (AGENTS.md §4)

- **Small N** (30 items): per-category numbers rest on 4–6 items each. Treat as directional.
- **Heuristic rubric**: instruction-following and safety scores are not LLM-judged yet.
- **One language**: Hindi only. Bengali and Tamil are not yet written.
- **Not native-reviewed**: items are authored and sourced but not yet reviewed by a native speaker
  (`../AUTHORS.md`).

## Rules for this folder (from `AGENTS.md` §4)

- **Never present `mock` output as a real result.** Mock files are labelled and must stay labelled.
- **Only real runs go in a headline table.** If there is no real run, say so.
- **Report failures**, not just successes — every summary includes a failure gallery by design.
- **Keep provenance** — each result row records backend, model id, seed, timestamp, and git commit.
