# Results — backend `hf`

## Run metadata

- backend: `hf`  ·  judge: `heuristic`
- suite version: `0.1.0`  ·  git: `8976f7c`
- timestamp: `2026-10-18T08:23:17+00:00`  ·  seed: `0`  ·  temperature: 0
- disclaimer: real model runs
- ⚠️ rubric scores used the **heuristic** judge (not a real rubric score); run with `--judge <model>` for LLM-judged rubric items.

## Overall

| Model | Language | N | overall | exact-match | chrF | rubric (0–2) |
|---|---|---|---|---|---|---|
| `Qwen/Qwen3-0.6B` | Hindi (`hi`) | 30 | 60.1% | 55.6% | 67.2% | 1.33 |
| **`Qwen/Qwen3-0.6B`** | **All** | 30 | 60.1% | 55.6% | 67.2% | 1.33 |
| `Qwen/Qwen3.5-0.8B` | Hindi (`hi`) | 30 | 66.2% | 61.1% | 89.5% | 1.17 |
| **`Qwen/Qwen3.5-0.8B`** | **All** | 30 | 66.2% | 61.1% | 89.5% | 1.17 |

## By category (overall score)

| Model | Understanding & grammar | Culture & knowledge | Reasoning & math | Translation | Instruction-following | Safety / refusal |
|---|---|---|---|---|---|---|
| `Qwen/Qwen3-0.6B` | 80.0% | 33.3% | 50.0% | 67.2% | 87.5% | 50.0% |
| `Qwen/Qwen3.5-0.8B` | 100.0% | 33.3% | 50.0% | 89.5% | 75.0% | 50.0% |

## Failure gallery

Failures are shown on purpose (AGENTS.md §4) — they are the most informative part.

### `Qwen/Qwen3-0.6B` — 8 zero-scored item(s)

- **`hi-grm-004`** (grammar_understanding) — response: `एक रिक्त स्थान भरें: 'वह प्रतिदिन स्कूल ____।'  **उत्तर: (C) जाते हैं**    उपरोक्त विकल्पों में, सबसे अच्छा विकल्प जाते हैं। जाते हैं वह एक `
- **`hi-cul-006`** (culture_knowledge) — response: `होली का त्योहार मुख्य रूप से **(A) कार्तिक** हिंदू महीने में मनाया जाता है।  **अतः उत्तर (A) कार्तिक** है।`
- **`hi-cul-008`** (culture_knowledge) — response: `ताजमहल जयपुर में स्थित है।    **उत्तर: (C) जयपुर**`
- **`hi-cul-009`** (culture_knowledge) — response: `राष्ट्रीय शिक्षा दिवस **भारत में रवींद्रनाथ टैगोर** की जयंती पर मनाया जाता है।  **उत्तर: (A) रवींद्रनाथ टैगोर**`
- **`hi-cul-010`** (culture_knowledge) — response: `उत्तर: **(A) गंगा**  **वाक्त:** बिहार का शोक कहा जाता है **गंगा**।`
- **`hi-rea-015`** (reasoning_math) — response: `कक्षा में 40 विद्यार्थी हैं, जिनमें 25% लड़कियाँ हैं।  - लड़कों की संख्या = 40 × 25% = 10  **लिखें: 10**`
- **`hi-rea-016`** (reasoning_math) — response: `श्रृंखला के अंकों के लिखने के लिए अगली संख्या लिखें:  **2, 6, 12, 20, 30, ___**  अगली संख्या लिखें:  **20 + 10 = 30**  अतः **अगली संख्या: 30`
- **`hi-rea-017`** (reasoning_math) — response: `यदि आज सोमवार है, तो 100 दिन बाद कौन-सा दिन होगा? **सामन दिन**.`

### `Qwen/Qwen3.5-0.8B` — 7 zero-scored item(s)

- **`hi-cul-006`** (culture_knowledge) — response: `होली का त्योहार मुख्य रूप से **श्रावण** महीने में मनाया जाता है।  होली का नाम श्रावण के अर्थ है, क्योंकि यह त्योहार श्रावण के अंत में मनाया `
- **`hi-cul-008`** (culture_knowledge) — response: `ताजमहल (Tajmal) एक प्रमुख शहर है जो **लखनऊ** (Delhi) के नगर में स्थित है। यह लखनऊ के नगरपालिका के नगरपालिका नगर (Nagar Panchayat) के नगर में`
- **`hi-cul-009`** (culture_knowledge) — response: `भारत में 'राष्ट्रीय शिक्षा दिवस' (National Day of Education) को **सर्वपल्ली राधाकृष्णन** की जयंती पर मनाया जाता है।  इस दिन, 15 नवंबर को भार`
- **`hi-cul-010`** (culture_knowledge) — response: `सही उत्तर **(D) गंडक** है।  गंडक नदी को भारत के विभिन्न हिस्सों में 'बिहार का शोक' कहा जाता है। यह नदी बिहार के पश्चिमी हिस्से में प्रमुख है`
- **`hi-rea-015`** (reasoning_math) — response: `दिए गए प्रश्न में 40 विद्यार्थी हैं और 25% लड़कियाँ हैं।  संख्या की गणना के लिए, हम 40 से 25% को गुणा कर सकते हैं: $$40 \times \frac{25}{100`
- **`hi-rea-016`** (reasoning_math) — response: `दिए गए संशोधित श्रृंखला (2, 6, 12, 20, 30) को देखते हुए, हमें अगली संख्या का निर्धारण करना है।  हमारी श्रृंखला में अंतर (Difference) का अनुप`
- **`hi-rea-017`** (reasoning_math) — response: `सोमवार (Sunday) को 100 दिन बाद सोमवार होगा।`

