# Learning log

## 2026-10-16 — Experiment 001: establish the baseline

### Question

Can a transparent keyword system provide a meaningful baseline for routing
support tickets before introducing a language model?

### Hypothesis

A keyword baseline should classify obvious examples reliably but fail on
indirect language, overlapping concepts, and messages without explicit clues.
Those failures will show what a model-based approach must improve.

### Method

1. Define four mutually exclusive routing labels.
2. Store labeled examples in versioned JSON Lines.
3. Score tokens using an inspectable label-to-keyword mapping.
4. Use a stable fallback for ties and no-match cases.
5. Report accuracy, macro F1, per-label metrics, a confusion matrix, and all
   failed examples.
6. Lock the public behavior with tests.

### Guardrails

- No model is called in this version.
- The dataset is a learning dataset, not production customer data.
- The same person authored the initial examples and baseline, so the result may
  be biased. Independent review and a held-out set are future work.
- Accuracy alone will not be treated as sufficient evidence.

### Result

The baseline classified 20 of 24 examples correctly: accuracy **0.8333** and
macro F1 **0.8420**. The confusion matrix (rows are expected labels, columns are
predictions in `account`, `billing`, `general`, `technical` order) was:

| Expected | account | billing | general | technical |
| --- | ---: | ---: | ---: | ---: |
| account | 4 | 0 | 2 | 0 |
| billing | 0 | 5 | 1 | 0 |
| general | 0 | 0 | 6 | 0 |
| technical | 0 | 0 | 1 | 5 |

The failed examples were `ticket-005`, `ticket-006`, `ticket-012`, and
`ticket-018`; each lacked a recognized label keyword and fell back to `general`.
The complete metrics and failure records are preserved in
[`reports/baseline.json`](reports/baseline.json). Run
`frontier-eval data/support_tickets.jsonl --output reports/baseline.json` to
reproduce them.

### Next experiment

Add an embedding-based classifier behind the same `predict(text)` interface and
compare it with the deterministic baseline. Preserve failures where the simpler
system wins.

