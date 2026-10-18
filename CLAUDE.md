# CLAUDE.md

**The binding rules for this repository live in [`AGENTS.md`](./AGENTS.md). Read it first — it is
mandatory for every agent, including you.**

This file exists only so that Claude-based tools pick the rules up automatically. Keep it short and
keep it in sync with `AGENTS.md`. If the two ever disagree, **`AGENTS.md` wins**.

## Must-follow summary (see `AGENTS.md` for the full text)

1. **Read `AGENTS.md`, then `README.md`, before doing any work.**
2. **Never fabricate** results, metrics, citations, or item sources. If you didn't run it, it
   didn't happen.
3. **Every factual item needs a verifiable `source_note`.** No source → `"status": "unverified"`.
4. **No copied benchmark items, no PII, no politics/religion/caste/gender preference items.**
   Safety probes are fine only when the correct behaviour is a refusal/redirect.
5. **Publish judge prompts** in `judges/`. Fixed seeds and decoding; log every run in `notes/`.
6. **Never present `mock`/dry-run output as a real result** — label it `MOCK — NOT REAL MODEL
   RESULTS`.
7. **Never commit secrets or model weights.** Use env vars (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`).
8. **Run `python validate.py` before committing.** It must exit 0.
9. **Conventional Commits**, branch for non-trivial work, **never force-push `main`**, never run
   destructive git without confirmation.
10. **When in doubt, stop and ask.** Do not silently break a rule.

## Commands

```bash
python validate.py                               # verify data files
python evaluate.py --backend mock --langs hi     # pipeline smoke test (not real results)
python evaluate.py --backend hf --models Qwen/Qwen2.5-0.5B-Instruct --langs hi
python evaluate.py --backend openai --models gpt-4o-mini --langs hi
```

## Definition of Done

`validate.py` exits 0 · `evaluate.py --backend mock` runs · new items are sourced and licensed ·
no secrets/weights/PII · docs updated · Conventional Commit message.
