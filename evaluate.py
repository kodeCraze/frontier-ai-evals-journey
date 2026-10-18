#!/usr/bin/env python3
"""
evaluate.py — the single entrypoint (AGENTS.md §5): generate → score → summarise.

Examples
--------
  # Smoke-test the whole pipeline, instantly, with no downloads or keys.
  python evaluate.py --backend mock --langs hi

  # Run a real small open model on your GPU (needs `pip install -r requirements.txt`).
  python evaluate.py --backend hf --models Qwen/Qwen2.5-0.5B-Instruct --langs hi

  # Run an API model (needs OPENAI_API_KEY / ANTHROPIC_API_KEY in the environment).
  python evaluate.py --backend openai    --models gpt-4o-mini --langs hi
  python evaluate.py --backend anthropic --models claude-3-5-haiku-latest --langs hi

  # See what would run, without running it.
  python evaluate.py --backend hf --models Qwen/Qwen2.5-0.5B-Instruct --dry-run

Scoring
-------
  exact_match     : normalised string match against `reference` + `accept` aliases.
  reference_based : chrF (character n-gram F-score) against `reference`; optional LLM judge.
  rubric          : published 0–2 rubric in judges/ ; scored by an LLM judge, or a clearly-labelled
                    *heuristic* fallback when no judge model is available.

Honesty rule (AGENTS.md §4): the `mock` backend produces synthetic answers. Its output is
labelled MOCK everywhere and is never a real model result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import schema

# Devanagari and other scripts must not crash the Windows console.
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    pass

MOCK_WARNING = "MOCK — NOT REAL MODEL RESULTS"


# ===========================================================================
# Scoring primitives
# ===========================================================================
def _ngrams(text: str, n: int) -> Counter:
    return Counter(text[i:i + n] for i in range(len(text) - n + 1))


def chrf(pred: str, ref: str, n_max: int = 6, beta: float = 2.0) -> float:
    """Character n-gram F-score (chrF). Standard-library only, deterministic."""
    p, r = schema.normalize(pred), schema.normalize(ref)
    if not p and not r:
        return 1.0
    if not p or not r:
        return 0.0
    precs, recs = [], []
    for n in range(1, n_max + 1):
        pc, rc = _ngrams(p, n), _ngrams(r, n)
        if not pc or not rc:
            continue
        overlap = sum((pc & rc).values())
        precs.append(overlap / sum(pc.values()))
        recs.append(overlap / sum(rc.values()))
    if not precs:
        return 0.0
    p_avg, r_avg = sum(precs) / len(precs), sum(recs) / len(recs)
    if p_avg + r_avg == 0:
        return 0.0
    b2 = beta * beta
    return (1 + b2) * p_avg * r_avg / (b2 * p_avg + r_avg)


def score_exact(pred: str, item: dict) -> float:
    """1.0 on a normalised match to the reference or an accepted alias, else 0.0."""
    npred = schema.normalize(pred)
    if not npred:
        return 0.0
    cands = [schema.normalize(c) for c in [item.get("reference", ""), *item.get("accept", [])]]
    cands = [c for c in cands if c]
    if npred in cands:
        return 1.0
    tokens = set(npred.split())
    return 1.0 if any(c in tokens for c in cands) else 0.0


def heuristic_rubric(pred: str, item: dict) -> tuple[float, str]:
    """Last-resort rubric score WITHOUT a judge. Deliberately conservative and loud about it."""
    npred = schema.normalize(pred)
    if not npred:
        return 0.0, "heuristic: empty response"
    ref = schema.normalize(item.get("reference", ""))
    if ref and npred == ref:
        return 2.0, "heuristic: exact normalised match"
    if ref:
        rt, pt = set(ref.split()), set(npred.split())
        if rt:
            overlap = len(rt & pt) / len(rt)
            if overlap >= 0.6:
                return 2.0, f"heuristic: token overlap {overlap:.2f} vs reference"
            if overlap >= 0.25:
                return 1.0, f"heuristic: token overlap {overlap:.2f} vs reference"
    return 1.0, "heuristic: non-empty but unassessable without a judge (not a real score)"


# ===========================================================================
# Backends — each exposes .name, .model, .generate(prompt, item) -> str
# ===========================================================================
class MockBackend:
    """Deterministic synthetic answers for PIPELINE TESTING ONLY. Never a real result."""

    name = "mock"

    def __init__(self, model: str = "mock-model", seed: int = 0, **_):
        self.model = model
        self.seed = seed

    @staticmethod
    def _distractor(prompt: str, item: dict) -> str:
        ref_n = schema.normalize(item.get("reference", ""))
        for letter, text in re.findall(r"\(([A-D])\)\s*([^\n]+)", prompt):
            if schema.normalize(text) != ref_n:
                return f"({letter}) {text.strip()}"
        return "«mock: deliberately wrong answer»"

    def generate(self, prompt: str, item: dict | None = None) -> str:
        # If we're being used as a *judge*, emit a valid judge response so the parsing path is
        # exercised by the smoke test too.
        if "SCORE:" in prompt:
            return "SCORE: 2\nREASON: mock judge (synthetic)"
        key = (item or {}).get("id", prompt) + str(self.seed)
        correct = int(hashlib.sha256(key.encode("utf-8")).hexdigest(), 16) % 10 >= 3  # ~70%
        if correct:
            ref = str((item or {}).get("reference", "")).strip()
            # Open-ended items (e.g. safety probes) have no reference; return a neutral
            # placeholder rather than an empty string, which would look like "no answer".
            return ref or "«mock: neutral refusal-style answer»"
        return self._distractor(prompt, item or {})


class HFBackend:
    """Local open model via transformers. Requires `pip install -r requirements.txt`."""

    name = "hf"

    def __init__(self, model: str, seed: int = 0, max_new_tokens: int = 256, **_):
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:  # pragma: no cover
            raise SystemExit(
                "The 'hf' backend needs torch + transformers:\n"
                "  pip install -r requirements.txt"
            ) from exc
        self._torch = torch
        torch.manual_seed(seed)
        self.model = model
        self.seed = seed
        self.max_new_tokens = max_new_tokens
        self.tok = AutoTokenizer.from_pretrained(model)
        self.net = AutoModelForCausalLM.from_pretrained(
            model,
            torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
        )
        self.net.eval()

    def generate(self, prompt: str, item: dict | None = None) -> str:
        torch = self._torch
        if getattr(self.tok, "chat_template", None):
            ids = self.tok.apply_chat_template(
                [{"role": "user", "content": prompt}],
                add_generation_prompt=True, return_tensors="pt",
            ).to(self.net.device)
        else:
            ids = self.tok(prompt, return_tensors="pt").input_ids.to(self.net.device)
        with torch.no_grad():
            out = self.net.generate(
                ids, max_new_tokens=self.max_new_tokens,
                do_sample=False,                 # temperature 0 for reproducible exact-match
                pad_token_id=self.tok.eos_token_id,
            )
        return self.tok.decode(out[0][ids.shape[-1]:], skip_special_tokens=True).strip()


def _post_json(url: str, payload: dict, headers: dict, timeout: int = 120) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:  # pragma: no cover - network dependent
        body = exc.read().decode("utf-8", errors="replace")[:500]
        raise SystemExit(f"HTTP {exc.code} from {url}: {body}") from exc


class OpenAIBackend:
    name = "openai"

    def __init__(self, model: str, seed: int = 0, max_new_tokens: int = 256, **_):
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise SystemExit("OPENAI_API_KEY is not set (see AGENTS.md §5: never hard-code keys).")
        self.model, self.seed, self.max_new_tokens = model, seed, max_new_tokens
        self.base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    def generate(self, prompt: str, item: dict | None = None) -> str:
        out = _post_json(
            f"{self.base}/chat/completions",
            {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "seed": self.seed,
                "max_tokens": self.max_new_tokens,
            },
            self.headers,
        )
        return out["choices"][0]["message"]["content"].strip()


class AnthropicBackend:
    name = "anthropic"

    def __init__(self, model: str, seed: int = 0, max_new_tokens: int = 256, **_):
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise SystemExit("ANTHROPIC_API_KEY is not set (see AGENTS.md §5).")
        self.model, self.max_new_tokens = model, max_new_tokens
        self.headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

    def generate(self, prompt: str, item: dict | None = None) -> str:
        out = _post_json(
            "https://api.anthropic.com/v1/messages",
            {
                "model": self.model,
                "max_tokens": self.max_new_tokens,
                "temperature": 0,
                "messages": [{"role": "user", "content": prompt}],
            },
            self.headers,
        )
        return "".join(b.get("text", "") for b in out.get("content", [])).strip()


BACKENDS = {
    "mock": MockBackend,
    "hf": HFBackend,
    "openai": OpenAIBackend,
    "anthropic": AnthropicBackend,
}


# ===========================================================================
# Judge (rubric scoring)
# ===========================================================================
class Judge:
    """Scores rubric items 0–2. Uses a published prompt (judges/judge_prompt.md)."""

    def __init__(self, client=None):
        self.client = client
        tpl_path = schema.JUDGES_DIR / "judge_prompt.md"
        self.template = tpl_path.read_text(encoding="utf-8") if tpl_path.exists() else ""

    def score(self, pred: str, item: dict) -> tuple[float, str]:
        if self.client is None or not self.template:
            return heuristic_rubric(pred, item)
        prompt = (self.template
                  .replace("{{LANGUAGE}}", schema.LANGUAGES.get(item.get("language", ""), ""))
                  .replace("{{PROMPT}}", str(item.get("prompt", "")))
                  .replace("{{REFERENCE}}", str(item.get("reference", "")))
                  .replace("{{RUBRIC}}", str(item.get("rubric", "")))
                  .replace("{{RESPONSE}}", str(pred)))
        raw = self.client.generate(prompt, {"id": f"judge-{item.get('id')}"})
        return _parse_judge(raw), f"judge: {raw.strip()[:200]}"


def _parse_judge(raw: str) -> float:
    """Extract a 0–2 score from a judge response. Looks for 'score: N', else a lone digit."""
    m = re.search(r"score\s*[:=\-]?\s*([0-2])", raw, flags=re.IGNORECASE)
    if m:
        return float(m.group(1))
    m = re.search(r"\b([0-2])\b", raw)
    return float(m.group(1)) if m else 0.0


# ===========================================================================
# Running one item
# ===========================================================================
def run_item(item: dict, backend, judge: Judge) -> dict:
    t0 = time.time()
    response = backend.generate(item["prompt"], item)
    latency = round(time.time() - t0, 3)

    mode = item["scoring"]
    notes = ""
    if mode == "exact_match":
        raw = score_exact(response, item)
        score = raw
    elif mode == "reference_based":
        raw = chrf(response, item.get("reference", ""))
        score = raw
    else:  # rubric
        raw, notes = judge.score(response, item)
        score = raw / 2.0
    if not notes:
        notes = f"{mode}"

    return {
        "id": item["id"],
        "language": item["language"],
        "category": item["category"],
        "difficulty": item["difficulty"],
        "scoring": mode,
        "prompt": item["prompt"],
        "reference": item.get("reference", ""),
        "response": response,
        "score": round(float(score), 4),
        "raw_score": round(float(raw), 4),
        "judge_notes": notes,
        "latency_s": latency,
    }


# ===========================================================================
# Aggregation + reporting
# ===========================================================================
def _agg(records: list[dict]) -> dict:
    if not records:
        return {"n": 0, "overall": 0.0, "exact": None, "chrf": None, "rubric": None}
    by_mode = defaultdict(list)
    for r in records:
        by_mode[r["scoring"]].append(r)
    exact = [r["score"] for r in by_mode["exact_match"]]
    chrf_s = [r["score"] for r in by_mode["reference_based"]]
    rub = [r["raw_score"] for r in by_mode["rubric"]]
    return {
        "n": len(records),
        "overall": sum(r["score"] for r in records) / len(records),
        "exact": (sum(exact) / len(exact)) if exact else None,
        "chrf": (sum(chrf_s) / len(chrf_s)) if chrf_s else None,
        "rubric": (sum(rub) / len(rub)) if rub else None,
    }


def _fmt(v, pct: bool = True) -> str:
    if v is None:
        return "—"
    return f"{v * 100:.1f}%" if pct else f"{v:.2f}"


def git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, cwd=schema.REPO_ROOT)
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def write_summary(out_dir: Path, backend_name: str, model: str, is_mock: bool,
                  meta: dict, by_lang: dict, records: list[dict],
                  judge_mode: str) -> None:
    langs = sorted(by_lang)
    lines: list[str] = []
    lines.append(f"# Results — `{backend_name}` / `{model}`\n")
    if is_mock:
        lines.insert(0, f"> ## ⚠️ {MOCK_WARNING}\n>\n"
                        f"> The `mock` backend returns **synthetic** answers to exercise the "
                        f"pipeline.\n> **No number below is a performance claim.** Run a real "
                        f"backend before quoting anything.\n")
    lines.append("## Run metadata\n")
    lines.append(f"- backend: `{backend_name}`  ·  model: `{model}`")
    lines.append(f"- judge: `{judge_mode}` (heuristic judges are **not** real rubric scores)")
    lines.append(f"- suite version: `{schema.SUITE_VERSION}`  ·  git: `{meta['git']}`")
    lines.append(f"- timestamp: `{meta['timestamp']}`  ·  seed: `{meta['seed']}`  ·  "
                 f"temperature: 0")
    lines.append(f"- disclaimer: {MOCK_WARNING if is_mock else 'real model runs'}\n")

    lines.append("## Overall\n")
    lines.append("| Language | N | overall | exact-match | chrF | rubric (0–2) |")
    lines.append("|---|---|---|---|---|---|")
    for lang in langs:
        a = _agg(by_lang[lang])
        lines.append(f"| {schema.LANGUAGES.get(lang, lang)} (`{lang}`) | {a['n']} | "
                     f"{_fmt(a['overall'])} | {_fmt(a['exact'])} | {_fmt(a['chrf'])} | "
                     f"{_fmt(a['rubric'], pct=False)} |")
    all_a = _agg(records)
    lines.append(f"| **All** | {all_a['n']} | {_fmt(all_a['overall'])} | {_fmt(all_a['exact'])} | "
                 f"{_fmt(all_a['chrf'])} | {_fmt(all_a['rubric'], pct=False)} |\n")

    lines.append("## By category\n")
    cats = sorted({r["category"] for r in records})
    lines.append("| Category | N | overall |")
    lines.append("|---|---|---|")
    by_cat = defaultdict(list)
    for r in records:
        by_cat[r["category"]].append(r)
    for cat in cats:
        a = _agg(by_cat[cat])
        lines.append(f"| {schema.CATEGORIES.get(cat, cat)} | {a['n']} | {_fmt(a['overall'])} |")
    lines.append("")

    failures = [r for r in records if r["score"] == 0.0]
    lines.append(f"## Failure gallery ({len(failures)} zero-scored items)\n")
    lines.append("Failures are shown on purpose (AGENTS.md §4) — they are the most informative part.\n")
    for r in failures[:12]:
        resp = r["response"].replace("\n", " ")[:160]
        lines.append(f"- **`{r['id']}`** ({r['category']}) — response: `{resp}`")

    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ===========================================================================
# Main
# ===========================================================================
def make_client(kind: str, model: str, seed: int):
    return BACKENDS[kind](model=model, seed=seed)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Run the suite, score, and summarise.")
    p.add_argument("--backend", choices=sorted(BACKENDS), default="mock")
    p.add_argument("--judge", choices=["heuristic", *sorted(BACKENDS)], default="heuristic",
                   help="Model used to score rubric items (default: heuristic, clearly-labelled).")
    p.add_argument("--models", default="", help="Comma-separated model ids (default: mock-model).")
    p.add_argument("--langs", default="", help="Comma-separated language codes (default: all).")
    p.add_argument("--limit", type=int, default=0, help="Max items per language (0 = all).")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default="", help="Results directory (default: results/<backend>).")
    p.add_argument("--dry-run", action="store_true", help="Print the plan and exit.")
    args = p.parse_args(argv)

    langs = [l.strip() for l in args.langs.split(",") if l.strip()] or sorted(schema.LANGUAGES)
    models = [m.strip() for m in args.models.split(",") if m.strip()] or ["mock-model"]

    items = schema.load_items(langs)
    if not items:
        print(f"evaluate: no items found for langs={langs}. "
              f"Add data/<lang>.jsonl (see AGENTS.md §2).")
        return 1
    by_lang: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        by_lang[it["language"]].append(it)
    if args.limit:
        by_lang = {k: v[:args.limit] for k, v in by_lang.items()}

    plan = {lang: len(v) for lang, v in by_lang.items()}
    print(f"evaluate: backend={args.backend} judge={args.judge} models={models}")
    print(f"evaluate: items per language = {plan}")
    if args.dry_run:
        print("evaluate: --dry-run, nothing executed.")
        return 0

    is_mock = args.backend == "mock"
    if is_mock:
        print(f"evaluate: ⚠️  {MOCK_WARNING} — pipeline smoke test only.")

    judge_client = None
    if args.judge != "heuristic":
        judge_client = make_client(args.judge, models[0] if args.judge == args.backend else "judge",
                                   args.seed)
    judge = Judge(judge_client)

    meta = {"timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "git": git_commit(), "seed": args.seed}

    out_root = Path(args.out) if args.out else schema.REPO_ROOT / "results" / args.backend

    for model in models:
        backend = make_client(args.backend, model, args.seed)
        safe = model.replace("/", "__")
        model_records: list[dict] = []
        m_by_lang: dict[str, list[dict]] = {}

        for lang, lang_items in sorted(by_lang.items()):
            records = []
            for item in lang_items:
                rec = run_item(item, backend, judge)
                records.append(rec)
                mark = "✓" if rec["score"] >= 0.5 else "✗"
                print(f"  {mark} {item['id']:<12} {rec['score']:.2f}  {rec['scoring']}")
            m_by_lang[lang] = records
            model_records.extend(records)
            lang_dir = out_root / safe
            lang_dir.mkdir(parents=True, exist_ok=True)
            with (lang_dir / f"{lang}.jsonl").open("w", encoding="utf-8") as fh:
                for rec in records:
                    fh.write(json.dumps({"model": model, "backend": args.backend,
                                         "judge": args.judge, **meta, **rec},
                                        ensure_ascii=False) + "\n")

        write_summary(out_root, args.backend, model, is_mock, meta, m_by_lang,
                      model_records, args.judge)
        a = _agg(model_records)
        print(f"evaluate: {model} → overall {_fmt(a['overall'])} over {a['n']} items")
        print(f"evaluate: wrote {out_root / 'summary.md'}")

    if is_mock:
        print(f"evaluate: remember — {MOCK_WARNING}. Run a real backend before quoting numbers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
