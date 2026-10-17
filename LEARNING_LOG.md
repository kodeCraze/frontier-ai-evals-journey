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
4. Route every multi-label tie and no-match case to the `general` fallback.
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
macro F1 **0.8420**. The 95% Wilson interval is **[0.6415, 0.9332]**. The
confusion matrix (rows are expected labels, columns are predictions in
`account`, `billing`, `general`, `technical` order) was:

| Expected | account | billing | general | technical |
| --- | ---: | ---: | ---: | ---: |
| account | 4 | 0 | 2 | 0 |
| billing | 0 | 5 | 1 | 0 |
| general | 0 | 0 | 6 | 0 |
| technical | 0 | 0 | 1 | 5 |

The failed examples were `ticket-005`, `ticket-006`, `ticket-012`, and
`ticket-018`; each lacked a recognized label keyword and fell back to `general`.
The complete metrics and failure records are preserved in
[`reports/baseline.json`](reports/baseline.json).

### Next experiment

Add a representation baseline behind the same `predict(text)` interface and
compare it with the deterministic baseline. Preserve failures where the simpler
system wins.

## 2026-10-17 — Experiment 002: TF-IDF leave-one-out comparison

### Question

Does a TF-IDF nearest-centroid router beat the keyword baseline when it cannot
train on the ticket it is scoring?

### Hypothesis

A bag-of-words representation should recover some indirect tickets that lack
exact keywords. On a 24-example set, it may also overfit if training and
evaluation use the same text.

### Method

1. Keep the same 24 versioned tickets and label set.
2. Implement TF-IDF with smoothed inverse document frequency and cosine
   similarity. No external embedding API is used.
3. Fit one centroid per label.
4. Evaluate with leave-one-out: each ticket is scored by a router trained on the
   other 23 tickets.
5. Also compute the invalid in-sample score to show leakage.
6. Add Wilson 95% confidence intervals and a comparison report.
7. Pre-register word-level TF-IDF centroids. Informal k-NN and character-ngram
   checks were inspected only after the official method was chosen; none beat
   the keyword baseline, so they were not used to pick a winner.

### Guardrails

- The official TF-IDF number is leave-one-out, not in-sample.
- Ties and zero-similarity queries fall back to `general`.
- The dataset is still small, synthetic, and author-labeled.
- A better score on a different representation would not have been accepted
  after seeing the results.

### Result

| Method | Protocol | Correct | Accuracy | 95% CI | Macro F1 |
| --- | --- | ---: | ---: | --- | ---: |
| Keyword | full | 20 / 24 | 0.8333 | [0.6415, 0.9332] | 0.8420 |
| TF-IDF | leave-one-out | 7 / 24 | 0.2917 | [0.1491, 0.4917] | 0.2932 |
| TF-IDF | in-sample | 24 / 24 | 1.0000 | [0.8620, 1.0000] | 1.0000 |

The valid intervals do not overlap. TF-IDF recovered only `ticket-006` and
still missed `ticket-005`, `ticket-012`, and `ticket-018`. It added 14 new
failures, including every billing ticket.

The 100% in-sample score is invalid: each ticket's own wording becomes part of
its label centroid. A behavioral test locks that distinction by using a unique
token that is predictive only when leaked.

Hosted verification moves to CircleCI because GitHub Actions on this account is
blocked by billing. The GitHub workflow remains for later use.

Reports:

- [`reports/baseline.json`](reports/baseline.json)
- [`reports/tfidf-loo.json`](reports/tfidf-loo.json)
- [`reports/comparison.json`](reports/comparison.json)

### Decision

Do not replace the keyword baseline. A representation method that cannot beat
keywords on this dataset is not ready to be swapped for an API model. The next
useful work is a larger, independently reviewed dataset and then a small open
model with the same leave-one-out or held-out discipline.

### Next experiment

Expand the dataset with independently reviewed examples, add slices for
indirect phrasing and overlapping intent, and only then introduce a small
open-model adapter.
