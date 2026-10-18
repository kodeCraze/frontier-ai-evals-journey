# Data card — `data/`

This folder holds the evaluation items. One JSONL file per language. Every item is authored **for
this suite**; nothing is copied from another benchmark (AGENTS.md §2).

## Files

| File | Language | Items | Status |
|---|---|---|---|
| `hi.jsonl` | Hindi (`hi`) | 30 | ✅ v1 (first batch) |
| `bn.jsonl` | Bengali (`bn`) | 0 | ⏳ planned |
| `ta.jsonl` | Tamil (`ta`) | 0 | ⏳ planned |

Licence for everything here: **CC-BY-4.0** (see `LICENSE` in this folder). Attribution in
`../AUTHORS.md`.

## Item format

One JSON object per line. UTF-8, LF line endings.

```json
{
  "id": "hi-cul-006",
  "language": "hi",
  "category": "culture_knowledge",
  "difficulty": "medium",
  "prompt": "…question, with options on separate lines…",
  "reference": "…the canonical expected answer…",
  "accept": ["…alias 1…", "B", "(B)"],
  "scoring": "exact_match",
  "rubric": "…only for rubric items…",
  "source_note": "authored for this suite; …verified against <source>…",
  "license": "CC-BY-4.0",
  "author": "kodeCraze",
  "status": "verified"
}
```

### Fields

| Field | Required | Notes |
|---|---|---|
| `id` | ✅ | `<lang>-<cat3>-<NNN>`, e.g. `hi-cul-006`. Unique, stable. |
| `language` | ✅ | `hi`, `bn`, `ta` — must match the filename. |
| `category` | ✅ | one of the six categories below |
| `difficulty` | ✅ | `easy` \| `medium` \| `hard` |
| `prompt` | ✅ | the question, in the target language; MC options on their own lines |
| `reference` | ✅ | canonical answer. **May be `""`** for open-ended `rubric` items (safety). Must be non-empty for `exact_match` / `reference_based`. |
| `accept` | optional | aliases for `exact_match` (e.g. the option letter `"B"`) |
| `scoring` | ✅ | `exact_match` \| `reference_based` \| `rubric` |
| `rubric` | for `rubric` | the 0–2 criterion for this specific item |
| `source_note` | ✅ | a **checkable** source. Vague notes fail validation. |
| `license` | ✅ | `CC-BY-4.0` |
| `author` | ✅ | attribution |
| `status` | optional | `verified` (default) \| `unverified` (excluded from headline numbers) |

## Categories (v1 scope)

| Code | Label | Per language (target) |
|---|---|---|
| `grammar_understanding` | Understanding & grammar | 5 before review, 20 target |
| `culture_knowledge` | Culture & knowledge | 6 / 20 |
| `reasoning_math` | Reasoning & math | 6 / 20 |
| `translation` | Translation | 6 / 20 |
| `instruction_following` | Instruction-following | 4 / 20 |
| `safety_refusal` | Safety / refusal | 3 / (probe set) |

## Sourcing policy

- **Facts:** every culture/knowledge item carries a verifiable `source_note` (encyclopaedia,
  government source, standard grammar). Unverifiable → `"status": "unverified"` and excluded.
- **Originals only:** no copying from Indic LLM-Arena, IndicGLUE, MILU, MMLU, or any other suite.
- **No PII, no values questions.** Safety probes are neutral prompts whose correct behaviour is a
  refusal/redirect.
- **Native review:** items count as fully verified only after a native speaker reviews them (see
  `../AUTHORS.md`). Until then they are `authored` but not reviewed.

## Relationship to existing benchmarks (complementary, not duplicative)

This suite deliberately overlaps *conceptually* with — but does not copy — established resources:

- **Indic LLM-Arena / AI4Bharat:** large-scale arena-style preference measurement and Indic eval.
  We are smaller and rubric-first; our additions are (a) published judge prompts, (b) explicit
  safety/refusal probes, (c) item-level provenance for every fact.
- **IndicGLUE / MILU:** broad NLU / knowledge benchmarks. We add culturally grounded, source-noted
  knowledge items and in-script reasoning rather than translating English benchmarks.
- **MMLU / HELM / BIG-bench:** general capability and holistic evaluation. Our contribution is
  *methodology and provenance* at small scale, not coverage.

Our additions, stated plainly: **provenance-per-item, published judges, and multilingual safety
probes.** If our items turn out to duplicate an existing item, that is a bug — report it.

## Adding items (read `../AGENTS.md` first)

1. Write items in the target language, with a real `source_note`.
2. Add them to the correct `data/<lang>.jsonl`.
3. Run `python validate.py` — it must exit 0.
4. Update `../CHANGELOG.md` if this is a new version.
