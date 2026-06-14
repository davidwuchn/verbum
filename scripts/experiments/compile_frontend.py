#!/usr/bin/env python3
# register: functional (the learned compile step, kernel-verified)
"""Compile front-end — can a model do prose→logical-form? (stage 2 leg 1).

THE QUESTION (session 226). Stage 2 = learned compile front-end + exact kernel back-
end. The formal halves (bracket abstraction, reduction) are certified exact (results/
compile-roundtrip). This measures the ONLY learned step in isolation: few-shot a model
to map a natural-language dataflow description → a logical form (expression), then let
the EXACT kernel grade it by REDUCTION-EQUALITY against gold.

  correct ⇔ normal_form(parse(model_output)) ≡ normal_form(parse(gold))

Representation-invariant: the model may answer with the direct expression `f (g x)` OR
an equivalent combinator term `B f g x` — the kernel normalizes both. Parse failure or
non-reduction counts as incorrect (a compile failure). This is the stage-2 thesis test:
is the learned surface (prose→logical-form) actually doable?

Usage:
  uv run python scripts/experiments/compile_frontend.py --model Qwen/Qwen3-32B
  uv run python scripts/experiments/compile_frontend.py --mode aggregate

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import subprocess
import sys
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
from verbum.lambda_ast import normal_form, parse, pretty
from verbum.probes.compile_tasks import compile_tasks, pattern_names

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "compile-frontend"

INSTRUCTION = (
    "You translate a described data-flow into a tiny expression language.\n"
    "Rules: function application is written by juxtaposition and is left-"
    "associative; use parentheses only to group; tokens are single lowercase "
    "letters naming functions or values.\n"
    "Output ONLY the final expression on a single line, nothing else."
)

# Few-shot examples — names {s,t,m,n} are HELD OUT from the test assignments.
FEWSHOT: list[tuple[str, str]] = [
    ("Take m and return it unchanged.", "m"),
    ("First apply t to m, then apply s to that result.", "s (t m)"),
    ("Apply s to m, passing m as both of its arguments.", "s m m"),
    ("Apply s to m and to the result of applying t to m.", "s m (t m)"),
]


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


def build_prompt(prose: str) -> str:
    lines = [INSTRUCTION, ""]
    for d, e in FEWSHOT:
        lines += [f"Description: {d}", f"Expression: {e}", ""]
    lines += [f"Description: {prose}", "Expression:"]
    return "\n".join(lines)


def clean_output(text: str) -> str:
    """Extract the candidate expression from the model's generation."""
    t = text.strip()
    if "Expression:" in t:
        t = t.split("Expression:")[-1]
    t = t.replace("`", "")
    for line in t.splitlines():
        line = line.strip()
        if line:
            return line.rstrip(".").strip()
    return ""


def nf_str(s: str) -> str | None:
    """Canonical normal-form string, or None if unparseable / non-terminating."""
    try:
        return pretty(normal_form(parse(s)))
    except Exception:
        return None


@torch.no_grad()
def run_model(args) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    safe = args.model.replace("/", "_")
    t0 = time.time()
    tasks = compile_tasks()
    gold_nf = {t.id: nf_str(t.gold) for t in tasks}

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[args.dtype]
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)
    model.to(args.device).eval()
    log(f"[{args.model}] {len(tasks)} compile tasks")

    records = []
    for i, task in enumerate(tasks):
        prompt = build_prompt(task.prose)
        try:
            text = tok.apply_chat_template(
                [{"role": "user", "content": prompt}],
                tokenize=False, add_generation_prompt=True,
                enable_thinking=False)
        except (TypeError, ValueError):
            text = tok.apply_chat_template(
                [{"role": "user", "content": prompt}],
                tokenize=False, add_generation_prompt=True)
        enc = tok(text, return_tensors="pt").to(args.device)
        out = model.generate(**enc, max_new_tokens=24, do_sample=False,
                             pad_token_id=tok.pad_token_id or tok.eos_token_id)
        gen = tok.decode(out[0][enc["input_ids"].shape[1]:],
                         skip_special_tokens=True)
        cand = clean_output(gen)
        cand_nf = nf_str(cand)
        correct = cand_nf is not None and cand_nf == gold_nf[task.id]
        records.append({
            "id": task.id, "pattern": task.pattern, "complexity": task.complexity,
            "prose": task.prose, "gold": task.gold,
            "model_output": cand, "model_nf": cand_nf,
            "parsed": cand_nf is not None, "correct": correct,
        })
        if (i + 1) % 10 == 0:
            log(f"    {i + 1}/{len(tasks)}")

    del model
    gc.collect()
    if args.device == "mps":
        torch.mps.empty_cache()

    n = len(records)
    n_ok = sum(r["correct"] for r in records)
    n_parsed = sum(r["parsed"] for r in records)
    by_pat = {}
    for p in pattern_names():
        rs = [r for r in records if r["pattern"] == p]
        by_pat[p] = {"n": len(rs), "correct": sum(r["correct"] for r in rs),
                     "rate": round(sum(r["correct"] for r in rs) / max(len(rs), 1), 3)}
    out = {
        "model": args.model, "dtype": args.dtype,
        "register": "functional (learned compile, kernel-verified)",
        "n": n, "accuracy": round(n_ok / n, 4),
        "parse_rate": round(n_parsed / n, 4),
        "by_pattern": by_pat,
        "failures": [r for r in records if not r["correct"]],
        "records": records,
        "git_sha": git_sha(), "elapsed_s": round(time.time() - t0, 1),
    }
    (RESULTS_DIR / f"{safe}.json").write_text(json.dumps(out, indent=2))

    log("")
    log(f"  === {args.model} compile front-end (prose -> logical form) ===")
    log(f"  accuracy {out['accuracy']:.3f} ({n_ok}/{n}); "
        f"parse-rate {out['parse_rate']:.3f}")
    for p in pattern_names():
        v = by_pat[p]
        log(f"    {p:9} {v['correct']:>2}/{v['n']:<2} {v['rate']:.2f}")
    if out["failures"]:
        log("  failures (e.g.): ")
        for r in out["failures"][:6]:
            log(f"    [{r['pattern']}] {r['prose']}")
            log(f"        gold={r['gold']!r} got={r['model_output']!r} "
                f"nf={r['model_nf']!r}")
    log(f"  wrote {safe}.json  ({out['elapsed_s']}s)")


def run_aggregate(args) -> None:
    files = sorted(f for f in RESULTS_DIR.glob("*.json") if f.stem != "aggregate")
    if args.models:
        want = {m.replace("/", "_") for m in args.models}
        files = [f for f in files if f.stem in want]
    if not files:
        log(f"no model jsons in {RESULTS_DIR}")
        sys.exit(1)
    models = [json.loads(f.read_text()) for f in files]
    rows = [{"model": m["model"], "accuracy": m["accuracy"],
             "parse_rate": m["parse_rate"]} for m in models]
    out = {"models": [m["model"] for m in models], "rows": rows,
           "git_sha": git_sha()}
    (RESULTS_DIR / "aggregate.json").write_text(json.dumps(out, indent=2))
    log("")
    log("  === COMPILE FRONT-END (prose -> logical form, kernel-verified) ===")
    log(f"  {'model':>26} {'acc':>6} {'parse':>6}")
    for r in rows:
        log(f"  {r['model']:>26} {r['accuracy']:>6.3f} {r['parse_rate']:>6.3f}")
    log("  wrote aggregate.json")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["model", "aggregate"], default="model")
    ap.add_argument("--model", default="Qwen/Qwen3-32B")
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    args = ap.parse_args()
    if args.mode == "model":
        run_model(args)
    else:
        run_aggregate(args)


if __name__ == "__main__":
    main()
