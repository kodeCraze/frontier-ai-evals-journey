# Evaluation card: support ticket routing v0.1

## Intended use

This evaluation is an educational benchmark for comparing routing approaches.
It is designed to teach evaluation discipline and provide a stable interface
for future deterministic and model-based experiments.

It is **not** suitable for production support automation or for making decisions
about real customers.

## Labels

| Label | Intended meaning |
| --- | --- |
| `account` | Login, identity, profile, password, or access issues |
| `billing` | Charges, invoices, refunds, subscriptions, or payments |
| `technical` | Bugs, errors, crashes, performance, integrations, or outages |
| `general` | Product questions, feedback, documentation, or uncategorized requests |

## Dataset

The initial dataset is hand-authored and contains synthetic English-language
support messages. It contains no private customer information.

Known limitations:

- Small sample size
- English only
- Synthetic rather than naturally occurring messages
- Single-label classification despite realistic overlap
- Initial labels and baseline were created by the same authoring process
- No demographic or linguistic robustness analysis yet

## Metrics

- Accuracy gives the overall fraction classified correctly.
- Per-label precision measures how often predictions for a label are correct.
- Per-label recall measures how much of a label the router finds.
- Per-label F1 balances precision and recall.
- Macro F1 gives every label equal weight.
- The confusion matrix and failure list retain information hidden by aggregates.

## Baseline result

On the 24 versioned examples, the keyword router produced 20 correct predictions,
for **0.8333 accuracy** and **0.8420 macro F1**. The confusion matrix is:

| Expected \\ predicted | account | billing | general | technical |
| --- | ---: | ---: | ---: | ---: |
| account | 4 | 0 | 2 | 0 |
| billing | 0 | 5 | 1 | 0 |
| general | 0 | 0 | 6 | 0 |
| technical | 0 | 0 | 1 | 5 |

The four failures are `ticket-005`, `ticket-006`, `ticket-012`, and
`ticket-018`. All fell back to `general` because their phrasing contained no
recognized keyword. The complete per-label metrics and failed-example records
are preserved in [`reports/baseline.json`](../reports/baseline.json).

## Decision supported

The evaluation can determine whether a future approach improves on the simple
baseline on this dataset. It cannot establish production readiness or general
language understanding.

## Planned improvements

1. Independent label review and ambiguity flags
2. Held-out and adversarial examples
3. Confidence intervals
4. Dataset slices for message length, indirect phrasing, and overlapping intent
5. Latency and cost measurements
6. Human review of model disagreements

