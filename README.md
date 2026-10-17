# Frontier AI Evals Journey

This repository is a public, evidence-based path toward frontier-AI
engineering. Each experiment has to beat a measured baseline on a versioned
dataset. Impressive demos do not count.

Version 0.2 compares two inspectable routers on the same 24 support tickets:

1. A deterministic keyword baseline
2. A TF-IDF nearest-centroid representation baseline, evaluated with
   leave-one-out so the held-out ticket cannot leak into training

The keyword router remains ahead: **83.33% accuracy / 0.842 macro F1**. Honest
TF-IDF leave-one-out scores **29.17% accuracy / 0.293 macro F1**. Training and
testing TF-IDF on the same tickets produces a perfect 100% score; that result is
recorded only as a leakage warning.

## What this proves

- A shared `predict(text)` interface for later model adapters
- Versioned evaluation data
- Reproducible metrics without external APIs or GPUs
- Confidence intervals, not just point estimates
- Failure analysis and method comparison
- A rejected invalid evaluation protocol
- Behavioral tests for success, ties, leakage, and invalid input
- Hosted CI on CircleCI, plus a GitHub Actions workflow if that account is usable

## Run the evaluation

Python 3.11 or newer is required.

```bash
python -m pip install -e .
frontier-eval data/support_tickets.jsonl
```

Save the keyword report:

```bash
frontier-eval data/support_tickets.jsonl --output reports/baseline.json
```

Evaluate the TF-IDF leave-one-out baseline:

```bash
frontier-eval data/support_tickets.jsonl --method tfidf --output reports/tfidf-loo.json
```

Compare both methods, including the invalid in-sample leak:

```bash
frontier-eval data/support_tickets.jsonl --compare --output reports/comparison.json
```

The output must be a different file from the input dataset, including through
normalized-path or hard-link aliases.

Committed evidence:

| Method | Protocol | Accuracy | 95% CI | Macro F1 |
| --- | --- | ---: | --- | ---: |
| Keyword | full | 83.33% | [0.6415, 0.9332] | 0.8420 |
| TF-IDF | leave-one-out | 29.17% | [0.1491, 0.4917] | 0.2932 |
| TF-IDF | in-sample | 100% | [0.8620, 1.0000] | 1.0000 |

The in-sample row is not a valid comparison. The two valid confidence intervals
do not overlap, so the keyword baseline remains the better measured system on
this dataset.

To run the behavioral tests:

```bash
python -m unittest discover -s tests -v
```

The project uses only Python's standard library at runtime. That keeps both
baselines inspectable and cheap to reproduce.

## Current experiments

**Question 001:** How well can a transparent keyword router categorize support
tickets into `account`, `billing`, `technical`, and `general`?

**Question 002:** Does a TF-IDF nearest-centroid router beat that baseline when
it cannot train on the ticket it is scoring?

**Why these first:** The evaluation loop has to exist before a language model is
introduced. A representation baseline is the next honest step: it uses vectors
and cosine similarity, but still has no hidden API behavior.

**Success criteria:**

1. The evaluator produces reproducible metrics, a confusion matrix, and a 95%
   Wilson interval.
2. Invalid or duplicate evaluation data fails loudly.
3. Every incorrect prediction remains visible.
4. Train/test leakage is demonstrated and rejected.
5. Future model-based routers use this exact interface and dataset.

See [the evaluation card](docs/evaluation-card.md) for assumptions and
limitations, and [the learning log](LEARNING_LOG.md) for experiment history.

## Roadmap

- [x] Deterministic baseline and reusable evaluator
- [x] Representation baseline with leave-one-out comparison
- [x] Confidence intervals
- [ ] Expand and independently review the dataset
- [ ] Add a small open-model adapter
- [ ] Validate an automated grader against human labels
- [ ] Add meaningful dataset slices
- [ ] Track latency and cost alongside quality
- [ ] Add prompt-injection and adversarial examples

## Resume evidence target

Current honest evidence:

> Built a versioned evaluation harness for support-ticket routing and compared a
> keyword baseline (83.33% accuracy, 0.842 macro F1, 95% CI 64–93%) with a
> TF-IDF centroid router. Leave-one-out TF-IDF scored 29.17% (CI 15–49%) and
> recovered only 1 of 4 keyword failures while adding 14 new errors; a 100%
> in-sample TF-IDF score was rejected as leakage.

That is stronger than claiming an embedding upgrade that was never measured
honestly.

## License

MIT
