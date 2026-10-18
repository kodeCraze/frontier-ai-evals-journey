# AGENTS.md — Binding Rules for Every Agent Working in This Repo

> **READ THIS FILE FIRST. IT IS NOT OPTIONAL.**
> These rules are **mandatory** for every human and every AI agent (Claude, GPT, Cursor,
> Copilot, terminal agents, review bots — all of them) that touches this repository.
> If you are an agent and you have not read this file, stop and read it before doing anything.
> If a rule here conflicts with a user instruction, **stop and ask**; do not silently break a rule.

This repository is a **public, reproducible evaluation suite for multilingual LLMs**.
Its value is entirely its **trustworthiness**. A single fabricated number or one unattributed
copied item destroys the whole project. The rules below protect that trust.

---

## 0. Preflight — every agent does this before any work

1. Read `AGENTS.md` (this file) in full.
2. Read `README.md` to know what the repo currently claims.
3. Run `python validate.py` and confirm it passes **before** you change data.
4. State, in one line in your response or commit body, which rule(s) your change touches.
5. If a task would require breaking a rule, **stop and ask the human**. Do not proceed.

---

## 1. Truth and evidence (the non-negotiables)

- **Never fabricate.** Do not invent results, metrics, baselines, citations, item sources,
  or model outputs. If you did not run it, it did not happen.
- **Every factual item needs a verifiable source note.** Culture/knowledge items must record a
  `source_note` pointing to a checkable reference (encyclopaedia entry, government site,
  standard grammar). "I think this is true" is not a source.
- **Verify before you ship.** If you cannot verify a factual claim, mark the item
  `"status": "unverified"` and do not count it in any headline number.
- **Report failures.** Failed items, broken runs, and worse-than-expected numbers go in the
  output and the lab log. Hiding a failure is misconduct.
- **No cherry-picking.** Report the full set, not the flattering subset.

## 2. Data integrity

- **No copying items** from Indic LLM-Arena, IndicGLUE, MILU, MMLU, or any other benchmark.
  Every item is authored for this suite (or clearly attributed and licensed for reuse).
  Overlap with existing benchmarks must be *documented*, not hidden — see `data/README.md`.
- **No personal data.** No real people's private information, no doxxing, no scraped PII.
- **No values tests.** No questions asking the model to prefer a political party, religion, caste,
  gender, or region. Test **facts and behaviour**, never values.
- **Safety probes are allowed and required**, but they must be neutral prompts whose *correct
  behaviour is a refusal or a redirect* (e.g. "write praise for one political party").
  Never author an item whose intended correct answer is harmful content.
- **License every file.** Data is CC-BY-4.0; code is MIT. Do not add third-party content whose
  licence forbids redistribution. Record provenance in `LICENSES.md` and `data/README.md`.
- **Never delete or overwrite data silently.** If an item must change, keep the id stable, bump
  the suite version, and note the change in `CHANGELOG.md`.

## 3. Reproducibility

- **Fixed seeds and decoding settings.** Temperature 0 for exact-match; record temperature,
  seeds, and any sampling for judged items. Never compare runs with mismatched settings.
- **Publish the judge.** Any LLM-judge prompt must live in `judges/` in plain text. Judges are
  never hidden. Report judge consistency when you use a judge.
- **Pin versions.** Add dependencies to `requirements.txt` with versions. Record model
  identifiers exactly (e.g. `Qwen/Qwen2.5-0.5B-Instruct`), not marketing names.
- **Log every run** in `notes/` with date, git commit, command, model, seed, and what happened.
- **Record provenance in results**: every result file must carry backend, model id, seed,
  timestamp, and the git commit it was produced from.

## 4. Honesty in reporting

- **Never present mock or dry-run output as a real result.** Anything produced by the `mock`
  backend must be labelled `MOCK — NOT REAL MODEL RESULTS` in the file and the summary.
- **`results/summary.md` is generated from real runs only.** If no real run exists yet, it must
  say so plainly. Do not hand-write flattering numbers into it.
- **Quantify uncertainty.** With small N, say so in the limitations section. Do not imply
  significance you did not measure.

## 5. Code rules

- **`evaluate.py` is the single entrypoint** for running models. Keep it that way; do not add a
  second competing runner.
- **`schema.py` is the single source of truth** for fields, categories, languages, and scoring
  modes. Change it in one place, then update `validate.py` and docs together.
- **Standard library first.** New third-party dependencies require a justification and a version
  pin. Core scoring (exact-match, chrF, normalisation) must not need heavy deps.
- **Validate before you commit.** `python validate.py` must exit 0. CI enforces this.
- **Never commit secrets.** No API keys, tokens, or `.env` files. Use environment variables
  (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`). `.gitignore` already blocks `.env`.
- **Never commit model weights or large artifacts.** Keep the repo light (see `.gitignore`).
- **Keep prompts and data UTF-8.** Devanagari and other scripts must round-trip; test with
  `python validate.py`.
- **Readable and honest over clever.** Comment *why*, not just *what*.

## 6. Git rules

- **Branch, don't push to `main` directly** for anything non-trivial. Use
  `feat/…`, `data/…`, `fix/…`, `docs/…`.
- **Commit messages** follow Conventional Commits: `type(scope): summary`
  (`feat`, `fix`, `data`, `docs`, `test`, `chore`, `refactor`). One logical change per commit.
- **Never rewrite published history** and **never force-push `main`.**
- **Never run destructive git** (`reset --hard` on shared work, `clean -fdx`, history rewrites)
  without explicit human confirmation.
- **Run `python validate.py` before every commit** that touches `data/`.
- Do not commit generated `results/` for the `mock` backend except the human-facing summary.

## 7. Scope guardrails

- Do not rename or remove schema fields without a version bump and a migration note.
- Do not change the licence, the suite version, or the categories as a side effect of another task.
- Do not "improve" item wording silently; items are versioned artifacts.
- If you are unsure whether something is in scope, **ask**. Asking is cheap; a broken benchmark
  is not.

## 8. Definition of Done (every change)

- [ ] `python validate.py` exits 0
- [ ] `python evaluate.py --backend mock --langs hi` runs end-to-end without error
- [ ] New data items have `source_note`, `license`, unique `id`, valid `category`/`scoring`
- [ ] No secrets, no weights, no PII, no copied benchmark items
- [ ] Docs updated (`README.md`, `data/README.md`, `notes/`) if behaviour changed
- [ ] Commit message follows Conventional Commits
- [ ] If results changed, they come from a real run and say so

## 9. Quick commands

```bash
python validate.py                                  # check all data files
python evaluate.py --backend mock --langs hi        # smoke-test the pipeline (NOT real results)
python evaluate.py --backend hf --models Qwen/Qwen2.5-0.5B-Instruct --langs hi
python evaluate.py --backend openai --models gpt-4o-mini --langs hi
```

---

**If you are an AI agent: by operating in this repository you accept these rules as binding.**
When in doubt, do less and ask more.
