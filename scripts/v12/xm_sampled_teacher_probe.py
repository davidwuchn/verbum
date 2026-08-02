"""XM Sampled-Teacher — STAGE 1: characterize Qwen3-4B as a multimodal KIBC teacher.

Session 298. Port 3 of the s296 gated list (knowledge/explorative-modeling.md
§XM gated-next-ports). The s296-297 triangulated close showed exploration
cannot improve holographic distillation from a DETERMINISTIC teacher (no
multimodality to explore). Port 3 breaks that hinge with a genuinely multimodal
target source: a real LLM (Qwen3-4B) SAMPLED at temperature>0.

Design 1 (Michael-approved s298): keep the toy 26-token KIBC task + the mini_holo
student UNCHANGED; source multimodality by having Qwen3-4B reduce combinator
expressions, sampled K times per input. Map generations back into the toy vocab.
The etch's best-of-K then selects the sample closest to the GROUND-TRUTH reduction
(mass-covering; selector = loss vs truth, NOT model probability rank).

THIS SCRIPT IS CHARACTERIZATION ONLY — no frozen gates, no verdict. It answers
the load-bearing precondition of Design 1: is Qwen3-4B sampled on KIBC USEFULLY
multimodal? (not perfectly-right = unimodal, not garbage = unparseable). It
measures:
  (a) parse_rate     — fraction of generations that map to valid toy-vocab exprs
  (b) mode_spread    — distinct canonical outputs per input (the # of modes)
  (c) contains_gt    — fraction of K-sets whose parsed+reduced set contains truth
  (d) foothold/density — how many of K samples equal ground truth
and CACHES the sampled+parsed targets to results/.../teacher_cache.json for the
etch stage to consume (generate-once, reuse across arms/seeds; lambda record).

License: MIT
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "v12"))

import numpy as np  # noqa: E402
from mini_holo_d_sweep_v2 import (  # noqa: E402
    App,
    Comb,
    Var,
    full_reduce,
    generate_example,
)

# ── toy-vocab token classes (all single-char; robust char tokenizer) ──
COMBINATORS = {"K", "I", "B", "C"}
ATOM_VARS = {"a", "b", "c", "d", "e", "f", "g", "h", "x", "y", "z"}
ALLOWED = COMBINATORS | ATOM_VARS | {"(", ")"}


# ══════════════════════════════════════════════════════════════════════
# Parser: Qwen text  ->  Expr  (left-assoc juxtaposition, single-char toks)
# ══════════════════════════════════════════════════════════════════════

class ParseError(Exception):
    pass


def _tokenize(text: str) -> list[str]:
    """Char-scan into single-char toks; whitespace separates, unknown chars fail.

    Every combinator/variable/paren in the toy vocab is exactly one char, so we
    can tokenize Qwen's (arbitrarily-spaced) output character by character. Any
    character outside ALLOWED or whitespace raises ParseError -> counts as a
    non-parse (that is the honest signal we want to measure).
    """
    toks = []
    for ch in text:
        if ch.isspace():
            continue
        if ch not in ALLOWED:
            raise ParseError(f"bad char {ch!r}")
        toks.append(ch)
    if not toks:
        raise ParseError("empty")
    return toks


def _parse_term(toks: list[str], i: int) -> tuple[object, int]:
    if i >= len(toks):
        raise ParseError("unexpected end")
    t = toks[i]
    if t == "(":
        node, j = _parse_app(toks, i + 1)
        if j >= len(toks) or toks[j] != ")":
            raise ParseError("missing )")
        return node, j + 1
    if t == ")":
        raise ParseError("unexpected )")
    node = Comb(t) if t in COMBINATORS else Var(t)
    return node, i + 1


def _parse_app(toks: list[str], i: int) -> tuple[object, int]:
    node, i = _parse_term(toks, i)
    while i < len(toks) and toks[i] != ")":
        rhs, i = _parse_term(toks, i)
        node = App(node, rhs)
    return node, i


def parse_expr(text: str) -> object:
    """Parse a combinator-expression string into an Expr tree, or raise."""
    toks = _tokenize(text)
    node, i = _parse_app(toks, 0)
    if i != len(toks):
        raise ParseError(f"trailing tokens at {i}")
    return node


def canonical(expr: object) -> str:
    """Normal-form canonical token string (reduce, then serialize)."""
    return " ".join(full_reduce(expr).to_tokens())


# ══════════════════════════════════════════════════════════════════════
# Answer extraction from a raw Qwen generation
# ══════════════════════════════════════════════════════════════════════

def extract_answer(raw: str) -> str | None:
    """Best-effort pull of the reduced expression from a Qwen completion.

    Strategy (strict-ish): scan lines; for each candidate line take the part
    after the last '=' if present; try to parse. Return the FIRST line that
    parses to a valid in-vocab Expr. None if nothing parses.
    """
    for line in raw.splitlines():
        s = line.strip()
        if not s:
            continue
        if "=" in s:
            s = s.rsplit("=", 1)[1].strip()
        # strip common wrappers/quotes/trailing punctuation
        s = s.strip("`*.\"' \t")
        try:
            parse_expr(s)
            return s
        except ParseError:
            continue
    # last resort: try the whole thing after last '='
    whole = raw.rsplit("=", 1)[-1].strip().strip("`*.\"' \t")
    try:
        parse_expr(whole)
        return whole
    except ParseError:
        return None


# ══════════════════════════════════════════════════════════════════════
# Prompt construction
# ══════════════════════════════════════════════════════════════════════

RULES = (
    "You reduce combinator-calculus expressions to normal form.\n"
    "Application is left-associative: 'f x y' means '((f x) y)'.\n"
    "The reduction rules are:\n"
    "  K x y    -> x\n"
    "  I x      -> x\n"
    "  B f g x  -> f (g x)\n"
    "  C f x y  -> f y x\n"
    "Reduce fully. Output ONLY the final reduced expression on a single line, "
    "using the same notation (letters, spaces, parentheses). No explanation."
)


def render_expr(inp_toks: list[str]) -> str:
    """input token list (without <bos>/=) -> readable expression string."""
    return " ".join(inp_toks)


def build_messages(fewshot: list[tuple[str, str]], expr_str: str) -> list[dict]:
    lines = [RULES, "", "Examples:"]
    for q, a in fewshot:
        lines.append(f"  {q}  =  {a}")
    lines.append("")
    lines.append(f"Reduce: {expr_str} =")
    return [{"role": "user", "content": "\n".join(lines)}]


def to_chat(tok, messages: list[dict]) -> str:
    try:
        return tok.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=False,
            enable_thinking=False)
    except TypeError:
        return tok.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=False)


# ══════════════════════════════════════════════════════════════════════
# Example bank
# ══════════════════════════════════════════════════════════════════════

def make_examples(n: int, rng: np.random.RandomState, max_depth: int = 4):
    """Return list of dicts {inp_toks, expr_str, gt_toks, gt_canon, depth}."""
    out, seen = [], set()
    tries = 0
    while len(out) < n and tries < n * 50:
        tries += 1
        ex = generate_example(rng, max_depth=max_depth)
        if ex is None:
            continue
        full_input, full_output, depth = ex
        inp_toks = full_input[1:-1]            # drop <bos> and trailing '='
        gt_toks = full_output[:-1]             # drop <eos>
        expr_str = render_expr(inp_toks)
        if expr_str in seen:
            continue
        seen.add(expr_str)
        # canonical ground truth (idempotent reduce of the emitted normal form)
        gt_canon = canonical(parse_expr(" ".join(gt_toks)))
        out.append({
            "inp_toks": inp_toks, "expr_str": expr_str,
            "gt_toks": gt_toks, "gt_canon": gt_canon, "depth": depth,
        })
    return out


# ══════════════════════════════════════════════════════════════════════
# Generation
# ══════════════════════════════════════════════════════════════════════

def generate_k(model, tok, prompt_text: str, k: int, temp: float,
               top_p: float, device: str, max_new_tokens: int = 32) -> list[str]:
    import torch
    enc = tok(prompt_text, return_tensors="pt").to(device)
    with torch.no_grad():
        out = model.generate(
            **enc, max_new_tokens=max_new_tokens, do_sample=True,
            temperature=temp, top_p=top_p, num_return_sequences=k,
            pad_token_id=tok.pad_token_id or tok.eos_token_id)
    plen = enc["input_ids"].shape[1]
    return [tok.decode(out[j][plen:], skip_special_tokens=True) for j in range(k)]


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--n-exprs", type=int, default=60)
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--temps", default="0.7,1.0")
    ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--max-depth", type=int, default=4)
    ap.add_argument("--n-fewshot", type=int, default=4)
    ap.add_argument("--max-new-tokens", type=int, default=32)
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--device", default="mps")
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--checkpoint-dir",
                    default="results/xm-sampled-teacher-probe")
    args = ap.parse_args()

    if args.smoke:
        args.n_exprs, args.k, args.temps = 6, 4, "1.0"

    temps = [float(t) for t in args.temps.split(",")]
    out_dir = ROOT / args.checkpoint_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.RandomState(args.seed)
    fewshot_rng = np.random.RandomState(args.seed + 7)
    fs_bank = make_examples(args.n_fewshot, fewshot_rng, args.max_depth)
    fewshot = [(e["expr_str"], " ".join(e["gt_toks"])) for e in fs_bank]
    fs_strs = {e["expr_str"] for e in fs_bank}

    exprs = [e for e in make_examples(args.n_exprs + args.n_fewshot, rng,
                                      args.max_depth)
             if e["expr_str"] not in fs_strs][:args.n_exprs]

    print("=" * 70)
    print(f"  XM SAMPLED-TEACHER PROBE (stage 1)  model={args.model}")
    print(f"  n_exprs={len(exprs)} k={args.k} temps={temps} "
          f"top_p={args.top_p} max_new={args.max_new_tokens}")
    print("=" * 70, flush=True)
    print("  few-shot examples:")
    for q, a in fewshot:
        print(f"    {q}  =  {a}")
    print(flush=True)

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[args.dtype]
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)
    model.to(args.device).eval()
    print(f"  [model loaded {time.time()-t0:.1f}s]", flush=True)

    cache = {"meta": {
        "run_id": f"xm-sampled-teacher-probe-{'smoke' if args.smoke else 'full'}",
        "timestamp": datetime.now(UTC).isoformat(),
        "model": args.model, "dtype": args.dtype, "device": args.device,
        "n_exprs": len(exprs), "k": args.k, "temps": temps,
        "top_p": args.top_p, "max_new_tokens": args.max_new_tokens,
        "max_depth": args.max_depth, "seed": args.seed,
        "n_fewshot": args.n_fewshot, "fewshot": fewshot,
        "python": platform.python_version(), "torch": torch.__version__,
        "note": "CHARACTERIZATION ONLY — no frozen gates, no verdict.",
    }}

    per_temp = {}
    for temp in temps:
        records = []
        agg = {"n_gen": 0, "n_parse": 0, "n_correct": 0,
               "spread_sum": 0, "contains_gt": 0, "unimodal": 0,
               "all_correct": 0, "all_wrong": 0}
        by_depth = {}
        tt0 = time.time()
        for idx, e in enumerate(exprs):
            msgs = build_messages(fewshot, e["expr_str"])
            prompt = to_chat(tok, msgs)
            raws = generate_k(model, tok, prompt, args.k, temp, args.top_p,
                              args.device, args.max_new_tokens)
            parsed, canons, correct = [], [], 0
            for raw in raws:
                ans = extract_answer(raw)
                if ans is None:
                    parsed.append(None)
                    continue
                try:
                    canon = canonical(parse_expr(ans))
                except ParseError:
                    parsed.append(None)
                    continue
                parsed.append(ans)
                canons.append(canon)
                if canon == e["gt_canon"]:
                    correct += 1
            n_parse = len(canons)
            distinct = len(set(canons))
            has_gt = int(e["gt_canon"] in set(canons))
            agg["n_gen"] += args.k
            agg["n_parse"] += n_parse
            agg["n_correct"] += correct
            agg["spread_sum"] += distinct
            agg["contains_gt"] += has_gt
            agg["unimodal"] += int(distinct == 1 and n_parse > 0)
            agg["all_correct"] += int(correct == args.k)
            agg["all_wrong"] += int(correct == 0)
            d = e["depth"]
            bd = by_depth.setdefault(
                d, {"n": 0, "parse": 0, "correct": 0, "spread": 0, "gt": 0})
            bd["n"] += 1
            bd["parse"] += n_parse
            bd["correct"] += correct
            bd["spread"] += distinct
            bd["gt"] += has_gt
            records.append({
                "expr": e["expr_str"], "depth": d, "gt": e["gt_canon"],
                "raws": raws, "parsed": parsed, "canons": canons,
                "n_parse": n_parse, "distinct": distinct,
                "correct": correct, "contains_gt": has_gt,
            })
            if (idx + 1) % 10 == 0:
                print(f"    temp={temp} {idx+1}/{len(exprs)} "
                      f"[{time.time()-tt0:.0f}s]", flush=True)

        n = len(exprs)
        kk = args.k
        summ = {
            "temperature": temp,
            "parse_rate": round(agg["n_parse"] / max(agg["n_gen"], 1), 4),
            "correct_density": round(agg["n_correct"] / max(agg["n_gen"], 1), 4),
            "mean_mode_spread": round(agg["spread_sum"] / n, 3),
            "contains_gt_rate": round(agg["contains_gt"] / n, 4),
            "unimodal_rate": round(agg["unimodal"] / n, 4),
            "all_correct_rate": round(agg["all_correct"] / n, 4),
            "all_wrong_rate": round(agg["all_wrong"] / n, 4),
            "by_depth": {
                str(d): {
                    "parse_rate": round(v["parse"] / max(v["n"] * kk, 1), 3),
                    "correct_density": round(v["correct"] / max(v["n"] * kk, 1), 3),
                    "mean_spread": round(v["spread"] / max(v["n"], 1), 2),
                    "contains_gt": round(v["gt"] / max(v["n"], 1), 3),
                    "n": v["n"],
                } for d, v in sorted(by_depth.items())},
        }
        per_temp[f"t{temp}"] = {"summary": summ, "records": records}
        print(f"\n  ── temp={temp} SUMMARY ──")
        print(f"    parse_rate       : {summ['parse_rate']:.1%}")
        print(f"    correct_density  : {summ['correct_density']:.1%} "
              f"(fraction of samples == ground truth)")
        print(f"    mean_mode_spread : {summ['mean_mode_spread']:.2f} "
              f"distinct canon forms / input (of k={kk})")
        print(f"    contains_gt_rate : {summ['contains_gt_rate']:.1%} "
              f"(≥1 of k samples is correct — the best-of-K ceiling)")
        print(f"    unimodal_rate    : {summ['unimodal_rate']:.1%} "
              f"(all parsed samples identical — NO modes to explore)")
        print(f"    all_correct/all_wrong: {summ['all_correct_rate']:.1%} / "
              f"{summ['all_wrong_rate']:.1%}", flush=True)

    cache["per_temp"] = per_temp
    with open(out_dir / "teacher_cache.json", "w") as f:
        json.dump(cache, f, indent=2, default=str)
    print(f"\n  saved -> {out_dir}/teacher_cache.json  "
          f"[total {time.time()-t0:.0f}s]", flush=True)

    # ── the read: is Qwen USEFULLY multimodal on KIBC? ──
    print(f"\n{'═' * 70}\n  READ (characterization, no gates):")
    for temp in temps:
        s = per_temp[f"t{temp}"]["summary"]
        useful = (s["parse_rate"] >= 0.5 and s["contains_gt_rate"] >= 0.3
                  and s["mean_mode_spread"] >= 1.5 and s["unimodal_rate"] <= 0.6)
        verdict = "USEFULLY-MULTIMODAL" if useful else "MARGINAL/CHECK"
        print(f"    temp={temp}: parse={s['parse_rate']:.0%} "
              f"spread={s['mean_mode_spread']:.1f} "
              f"gt_ceiling={s['contains_gt_rate']:.0%} "
              f"unimodal={s['unimodal_rate']:.0%}  -> {verdict}")
    print("  (heuristic only; Michael reads the numbers, not the label.)")


if __name__ == "__main__":
    main()
