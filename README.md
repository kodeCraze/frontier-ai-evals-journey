# frontier-ai-evals-journey

**A small, honest, reproducible evaluation suite for Indian-language LLMs — and my public
lab notebook for learning how frontier evaluations are actually designed.**

Part measurement suite, part learning journal. Built in public, method first.

---

## What this is

- A **curated evaluation suite** for Indian languages (v1: **Hindi**, with Bengali and Tamil next)
  that tests what general benchmarks miss: native grammar, culturally grounded knowledge,
  reasoning in-script, translation, instruction-following, and **multilingual safety/refusal
  behaviour**.
- A **reproducible harness** (`evaluate.py`) that runs open and API models under fixed decoding,
  scores each item, and emits a table anyone can rerun.
- A **record of how I work**: every design decision, run, and failure is logged in `notes/`.

## What this is *not*

- **Not** a claim to beat Indic LLM-Arena, MILU, IndicGLUE, or MMLU. It is deliberately *small and
  meticulous*; its value is trustworthy methodology, not scale or leaderboard rank.
- **Not** a training project. Everything here runs on inference — a 6 GB laptop GPU and public APIs.
- **Not** finished. This is v1-in-progress. See **Status** below for exactly what exists.

## Status (read this before quoting anything)

| Piece | State |
|---|---|
| **30 Hindi items** (`data/hi.jsonl`) | ✅ authored, sourced, validated |
| Bengali + Tamil items | ⏳ planned |
| `validate.py` (schema + integrity checks) | ✅ working |
| `evaluate.py` (mock + HF + OpenAI + Anthropic backends) | ✅ working |
| Judge prompts published (`judges/`) | ✅ v1 |
| **Real model results** | ⏳ **none yet** — the only table so far is a labelled `mock` smoke test |

> The headline result of this repo, today, is: **the pipeline runs end-to-end and every item is
> sourced and validated.** Real numbers land as models are run; until then, no number here is a
> performance claim. See `results/summary.md`.

## Rerun it in one command

```bash
# 1) verify the data
python validate.py

# 2) smoke-test the whole pipeline (instant, no downloads; NOT real model results)
python evaluate.py --backend mock --langs hi

# 3) run a real small model on the GPU (needs: pip install -r requirements.txt)
python evaluate.py --backend hf --models Qwen/Qwen2.5-0.5B-Instruct --langs hi --limit 10

# 4) run an API model (needs an API key, or use --judge/--backend)
set OPENAI_API_KEY=sk-...
python evaluate.py --backend openai --models gpt-4o-mini --langs hi
```

Outputs go to `results/<backend>/<model>/<lang>.jsonl` (per item) and
`results/<backend>/summary.md` (the table).

## Repository layout

```
frontier-ai-evals-journey/
├─ README.md            ← you are here
├─ AGENTS.md            ← BINDING rules for every agent/human (read before working)
├─ CLAUDE.md            ← pointer + must-follow summary for Claude tools
├─ schema.py            ← single source of truth: fields, categories, languages, scoring
├─ validate.py          ← schema + integrity checks (run before every commit)
├─ evaluate.py          ← the one entrypoint: generate → score → summarise
├─ data/                ← items (hi.jsonl, …) + data card + licences + authors
├─ judges/              ← published judge prompts and the 0–2 rubric
├─ results/             ← summary.md + per-model per-item outputs
├─ notes/               ← dated lab log
├─ CITATION.cff         ← how to cite the suite
├─ CHANGELOG.md         ← suite versions
└─ .github/workflows/   ← CI: validate on every push/PR
```

## How items are scored

| Mode | Used for | How |
|---|---|---|
| `exact_match` | reasoning, math, single-answer knowledge | normalised string match against `reference` + `accept` aliases |
| `reference_based` | translation | **chrF** (character n-gram F-score), optional judge |
| `rubric` | knowledge, instruction-following, safety | published 0–2 rubric in `judges/rubric.md` |

Scoring rules that make this *science* and not a hobby: temperature 0 for exact-match, judge
prompts published, judges re-run to measure their own consistency, and failures shown, not hidden.

## Method (the short version)

1. Author items **for this suite** — never copy from another benchmark.
2. Attach a **verifiable source note** to every factual item.
3. **Validate** the data (`python validate.py`).
4. **Run** under fixed decoding; **log** the run in `notes/`.
5. **Publish** the judge and the failures; only then publish the table.

## Contributing / using this

Issues and PRs welcome — read `AGENTS.md` first, that is the contract. Want to add a language or a
category? Open an issue with the plan before writing 100 items.

## Licence

Code: **MIT** (`LICENSE`). Data and judge prompts: **CC-BY-4.0** (`data/LICENSE`). See
`LICENSES.md` for details. Cite via `CITATION.cff`.
