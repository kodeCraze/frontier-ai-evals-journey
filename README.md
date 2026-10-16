# Frontier AI Evals Journey

This repository is the first public artifact in a practical, evidence-based
journey toward frontier-AI engineering.

The first lesson is deliberately simple: **measure a transparent baseline
before adding a language model**. Version 0.1 evaluates a deterministic support
ticket router on a versioned dataset. It reports accuracy, macro F1, per-label
precision/recall/F1, a confusion matrix, and every failed example.

That creates a trustworthy foundation for later experiments with embeddings,
small open models, and API-based models. Future approaches will have to beat
the baseline on the same dataset instead of merely looking impressive in a
demo.

## What this proves

- A testable prediction interface
- Versioned evaluation data
- Reproducible metrics without external dependencies
- Failure analysis rather than accuracy alone
- Behavioral tests for success and invalid-input cases
- Continuous integration on Python 3.11 and 3.12
- An honest evaluation card documenting limitations

## Run the evaluation

Python 3.11 or newer is required.

```bash
python -m pip install -e .
frontier-eval data/support_tickets.jsonl
```

To save the machine-readable report:

```bash
frontier-eval data/support_tickets.jsonl --output reports/baseline.json
```

To run the behavioral tests:

```bash
python -m unittest discover -s tests -v
```

The project intentionally uses only Python's standard library at runtime. This
keeps the first experiment inspectable and makes the baseline easy to reproduce.

## Current experiment

**Question:** How well can a transparent keyword router categorize support
tickets into `account`, `billing`, `technical`, and `general`?

**Why begin here:** A deterministic baseline exposes the complete evaluation
loop—dataset, prediction, metric, failure analysis, and iteration—without hiding
behavior behind a remote model.

**Success criteria:**

1. The evaluator produces reproducible metrics and a confusion matrix.
2. Invalid or duplicate evaluation data fails loudly.
3. Every incorrect prediction remains visible for analysis.
4. Future model-based routers use this exact interface and dataset.

See [the evaluation card](docs/evaluation-card.md) for assumptions and
limitations, and [the learning log](LEARNING_LOG.md) for experiment history.

## Roadmap

- [x] Deterministic baseline and reusable evaluator
- [ ] Expand and independently review the dataset
- [ ] Add an embedding-based baseline
- [ ] Add a small open-model adapter
- [ ] Validate an automated grader against human labels
- [ ] Add confidence intervals and meaningful dataset slices
- [ ] Track latency and cost alongside quality
- [ ] Add prompt-injection and adversarial examples

## Resume evidence target

The repository will earn a résumé bullet only when it contains enough evidence.
The target format is:

> Built a versioned evaluation harness for support-ticket routing, measuring
> per-class quality and failure modes across multiple baselines; improved macro
> F1 from **N** to **M** while reporting latency and cost tradeoffs.

Numbers will be filled in only after they are measured.

## License

MIT

