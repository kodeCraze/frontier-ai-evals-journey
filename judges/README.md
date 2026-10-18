# Judge prompts & rubric

> These files are **published on purpose** (AGENTS.md §3). A hidden judge cannot be audited, and an
> unaudited judge is not a measurement.

## Contents

| File | Purpose |
|---|---|
| `rubric.md` | The 0–2 scoring rubric used for `rubric`-mode items |
| `judge_prompt.md` | The exact prompt template fed to a judge model (`evaluate.py --judge …`) |

## Judge rules

1. **Exact prompt, no improvisation.** `evaluate.py` loads `judge_prompt.md` and substitutes the
   `{{…}}` tokens. Edit the template here, never inline in code.
2. **No judge, no rubric score.** Without a judge model, `evaluate.py` falls back to a *heuristic*
   that is explicitly labelled "not a real score" in every output. Never report heuristic rubric
   numbers as results (AGENTS.md §4).
3. **Measure the judge.** Any judged run should be repeated (e.g. 3 seeds at temperature 0.7) and
   its self-consistency reported. Judge reliability in Indian languages is itself research
   question #2 for this project — do not assume the judge is trustworthy.
4. **Publish disagreements.** Where the judge and a human disagree, that example goes in `notes/`.

## Known limitations (state these in any report)

- Judges inherit the biases of their base model, and those biases are under-studied in Indian
  languages. A judge may, for example, over-reward fluent-but-wrong Devanagari output.
- A 0–2 rubric is coarse; it cannot express "right reasoning, wrong final answer".
- Rubric scores are **not** comparable across judge models. Report which judge produced them.
