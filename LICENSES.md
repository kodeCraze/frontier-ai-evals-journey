# Licences

This project uses a **split licence**: permissive for code, share-alike-friendly attribution for
data and prompts.

| What | Files | Licence |
|---|---|---|
| **Code** | `*.py`, CI config, scripts | **MIT** (see `LICENSE`) |
| **Data** | `data/**` (`.jsonl`, data card) | **CC-BY-4.0** (see `data/LICENSE`) |
| **Judge prompts & rubric** | `judges/**` | **CC-BY-4.0** |
| **Docs / notes** | `README.md`, `notes/**`, `AGENTS.md`, `CLAUDE.md` | **CC-BY-4.0** |

## Attribution

> Sharma, Sahil (kodeCraze). *frontier-ai-evals-journey: an evaluation suite for Indian-language
> LLMs.* 2026. CC-BY-4.0. https://github.com/kodeCraze/frontier-ai-evals-journey

If you use the suite, please cite via `CITATION.cff`.

## Third-party content

**None, by design.** Every evaluation item is authored for this suite. We do **not** copy items from
Indic LLM-Arena, IndicGLUE, MILU, MMLU, or any other benchmark. Where our items overlap
conceptually with existing benchmarks, that overlap is documented in `data/README.md` as
"complementary, not duplicative".

If third-party content is ever added, it must be (a) licence-compatible with redistribution under
this repo's terms and (b) listed here with its source and licence. See `AGENTS.md` §2.

## Model outputs

Model generations stored under `results/` are outputs of the respective models and remain subject
to those models' own licences and terms of use. They are recorded here for reproducibility only.
