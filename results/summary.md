# Results index

> **No real model results exist yet.** This file is the human-facing index; per-run tables live in
> `results/<backend>/summary.md`.

## What exists today

| Output | Meaning | Is it a real result? |
|---|---|---|
| `results/mock/summary.md` | Pipeline smoke test with synthetic answers | ❌ **No — `MOCK — NOT REAL MODEL RESULTS`** |
| `results/hf/summary.md` | Local open-model runs | ✅ once produced by a real run |
| `results/openai/summary.md` | API-model runs | ✅ once produced by a real run |
| `results/anthropic/summary.md` | API-model runs | ✅ once produced by a real run |

## How to produce a real table

```bash
python validate.py
python evaluate.py --backend hf      --models Qwen/Qwen2.5-0.5B-Instruct --langs hi
python evaluate.py --backend openai  --models gpt-4o-mini --langs hi
```

Each run writes `results/<backend>/<model>/<lang>.jsonl` (per item) and
`results/<backend>/summary.md` (the table + failure gallery).

## Rules for this folder (from `AGENTS.md` §4)

- **Never present `mock` output as a real result.** Mock files are labelled and must stay labelled.
- **Only real runs go in a headline table.** If there is no real run, say so.
- **Report failures**, not just successes — every summary includes a failure gallery by design.
- **Keep provenance** — each result row records backend, model id, seed, timestamp, and git commit.
