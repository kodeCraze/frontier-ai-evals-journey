# Lab log — 2026-10-18 — first real model runs (Hindi)

Per AGENTS.md §3 ("log every run"), this records the first **real** evaluation runs on the suite.

## Command

```bash
python validate.py
python evaluate.py --backend hf --models "Qwen/Qwen3-0.6B,Qwen/Qwen3.5-0.8B" --langs hi --max-new-tokens 200
```

## Provenance

| Field | Value |
|---|---|
| backend | `hf` (transformers, local GPU) |
| models | `Qwen/Qwen3-0.6B`, `Qwen/Qwen3.5-0.8B` |
| items | 30 Hindi (`data/hi.jsonl`), suite v0.1.0 |
| decoding | temperature 0, `do_sample=False`, max_new_tokens 200, seed 0 |
| thinking mode | disabled via `enable_thinking=False` where the chat template supports it |
| judge | `heuristic` (rubric column is indicative only) |
| git commit | `8976f7c` |
| hardware | RTX 3060 Laptop 6 GB, CUDA 12.4, PyTorch 2.6, transformers 5.20.1 |
| outputs | `results/hf/Qwen__Qwen3-0.6B/hi.jsonl`, `results/hf/Qwen__Qwen3.5-0.8B/hi.jsonl` |

## Results

| Model | overall | exact-match | chrF | rubric (0–2)* |
|---|---|---|---|---|
| `Qwen/Qwen3-0.6B` | 60.1% | 55.6% | 67.2% | 1.33 |
| `Qwen/Qwen3.5-0.8B` | 66.2% | 61.1% | 89.5% | 1.17 |

By category (overall score):

| Model | Grammar | Culture | Reasoning | Translation | Instruction | Safety |
|---|---|---|---|---|---|---|
| `Qwen/Qwen3-0.6B` | 80.0% | 33.3% | 50.0% | 67.2% | 87.5% | 50.0% |
| `Qwen/Qwen3.5-0.8B` | 100.0% | 33.3% | 50.0% | 89.5% | 75.0% | 50.0% |

\* Heuristic judge — **not** a real rubric score.

## What happened / what I learned

1. **Bug found and fixed before trusting any number.** `schema.normalize()` used `re.\w`, which in
   Python excludes Unicode combining marks — it was silently deleting Devanagari matras
   (`स्त्रीलिंग` → `स त र ल ग`). Every string comparison was corrupted. Fixed to keep Unicode
   categories L/M/N (`schema.py`). Lesson: test normalisation on the actual script, not on ASCII.

2. **The headline is a failure pattern, not a score.** Both small models are *confidently wrong* on
   culturally grounded knowledge:
   - Holi's month → answered कार्तिक (0.6B) / श्रावण (0.8B); correct is फाल्गुन.
   - Taj Mahal's city → answered जयपुर (0.6B) / लखनऊ (0.8B); correct is आगरा.
   - National Education Day → answered रवींद्रनाथ टैगोर / सर्वपल्ली राधाकृष्णन; correct is
     मौलाना अबुल कलाम आज़ाद.
   - The 0.8B model invented an English-ified city name "Tajmal" — a hallucination that chrF still
     rewarded (89.5% chrF vs 61.1% exact-match), i.e. **chrF over-rewards fluent-but-wrong output**.

3. **In-script reasoning is weak.** Both failed the "40 students, 25% girls → boys" item (computed
   25% instead of 75%) and the weekday item.

4. **Grammar is comparatively strong** (80–100%), which is consistent with Hindi being a
   well-represented language relative to the knowledge/reasoning content we test.

## Caveats (do not over-read)

- N = 30; per-category cells rest on 4–6 items.
- Rubric items were scored by the heuristic, not an LLM judge.
- Single language, single seed, two models — directional only, no significance claimed.

## Next

- Add a real LLM judge and measure its consistency (paper #2 seed).
- Grow Hindi to 100 items; then Bengali and Tamil.
- Test whether chrF over-rewards hallucinated translations by corrupting references deliberately.
