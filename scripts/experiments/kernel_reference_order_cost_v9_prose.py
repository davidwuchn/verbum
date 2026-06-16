#!/usr/bin/env python3
# register: ORDER-COST softmax-over-V surprisal — PROSE bridge (kills symbol caveat)
"""Kernel-ref ORDER-COST read, PROSE BRIDGE — is B the NATIVE softmax-over-V order
when the certified trace is rendered as PROSE? (s236 prong 2, path 2).

THE CAVEAT THIS KILLS (s236, λ measure): v8 fed BARE symbolic CL ("B f a b -> f (a b)").
The decisive 14B win (B atom-surprisal 0.81 << C 2.14, t=-7.02) may PARTLY reflect a
generic copy/induction-head preference for source-order atoms rather than composition
SEMANTICS — and (s233 lead 2) the routing register reads PROSE SEMANTICS not CL SYNTAX:
bare symbols collapse to common-mode/gauge. This script re-runs the order-cost read on
the SAME certified traces rendered as PROSE.

WHY DETERMINISTIC RENDER (not the model decompile gate): the order-cost test measures
whether the model finds the ORDER-PRESERVING contractum cheaper than the PERMUTED one.
If the MODEL chooses the word order (decompile gate), we read our own confound back.
So we use a FIXED, order-faithful compositional renderer we control -> the certified
lambda_ast alignment is preserved end-to-end. App(f, x) -> "<f> applied to <x>",
left-to-right; atoms -> fixed content words; the left-to-right CL structure maps
directly to word order.

  B f a b -> f (a b)   "F applied to ( A applied to B )"   order KEPT  (atoms F,A,B)
  C f a b -> f b a      "F applied to B applied to A"        SWAPPED    (atoms F,B,A)

The de-confounded headline = the atom-only (content-word-only) B<C minimal pair,
paired by pair_id with the SAME atom->word map for both partners (the pairing IS the
common-mode subtraction; carries over the s233 gauge-domination lesson).

VERDICT LOGIC (λ measure, two-sided):
  - B<C in PROSE (atom-only, paired, sig) -> composition-order preference lives in
    the SEMANTIC register the model uses, NOT a bare-symbol copy artifact. The s236
    caveat is KILLED; the 14B native-order result becomes confound-free. Unifies with
    the s235 curvature face.
  - B~C in PROSE (collapses) -> the symbolic win was partly the copy-confound; the
    native-order claim weakens; lean on the curvature face (s235 1c-ii).

Usage:
    uv run python scripts/experiments/kernel_reference_order_cost_v9_prose.py --smoke
    uv run python scripts/experiments/kernel_reference_order_cost_v9_prose.py    # 14B

License: MIT
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))
sys.path.insert(0, str(_ROOT / "scripts" / "instruments"))

from opcode_monitor_v2 import (  # noqa: E402
    _git_sha,
    _json_safe,
    _transformers_version,
    load_model_and_tokenizer,
)

from verbum.lambda_ast import (  # noqa: E402
    App,
    Atom,
    Comb,
    parse,
    pretty,
    size,
    step_fired,
)

RESULTS_DIR = _ROOT / "results" / "kernel-reference-audit"
SEP = " then "
ORDER_PRESERVING = {"B", "I", "D"}   # output keeps source left-to-right order
ORDER_BREAKING = {"C", "K", "W", "S", "M"}  # permute / delete / duplicate
ATOM_POOL = ["f", "g", "h", "p", "q", "u", "v", "a", "b", "c", "d", "e", "m", "n"]
MAX_TRACE_STEPS = 8
MAX_TERM_SIZE = 60

# ── deterministic, order-faithful prose renderer ─────────────────────────────────
# Fixed CL-atom -> content word (stable across the WHOLE run -> pair partners that
# share atom letters share words; the only paired difference is ORDER, not lexicon).
# Distinct, common, mostly single-token nouns to minimise sub-word drift.
CONTENT_WORDS = ["dog", "cat", "bird", "fish", "wolf", "bear", "deer", "eagle",
                 "rabbit", "fox", "owl", "hawk", "seal", "crane"]
ATOM2WORD = dict(zip(ATOM_POOL, CONTENT_WORDS, strict=True))
CONTENT_SET = set(CONTENT_WORDS)
# combinators (operators) -> verbal name; NOT in CONTENT_SET, so excluded from the
# atom-only de-confound. Keeps the rendered string prose, no OOD symbols.
COMB_WORDS = {"B": "compose", "C": "swap", "K": "keep", "I": "self", "W": "double",
              "D": "chain", "S": "share", "M": "mirror", "Y": "loop"}
APPLY = " applied to "


def render_term(term_str: str, mode: str = "flat") -> str:
    """Order-faithful prose for a CL term. App(fn, arg) -> '<fn> applied to <arg>'.

    mode='nested': parenthesise an arg that is itself an application (mirrors
        lambda_ast.pretty) — STRUCTURALLY faithful but B (f (a b)) nests while C
        (f b a) is flat, so the B-vs-C contrast is CONFOUNDED by nesting depth.
    mode='flat' (default, DE-CONFOUNDED): linearise leaves left-to-right with NO
        parens, so B and C render as identical flat chains differing ONLY in atom
        ORDER (B: f a b ; C: f b a) — nesting held constant, the pure order test."""
    return _walk(parse(term_str), mode)


def _leaf(t) -> str | None:
    if isinstance(t, Atom):
        return ATOM2WORD.get(t.name, t.name)
    if isinstance(t, Comb):
        return COMB_WORDS.get(t.name, t.name)
    return None


def _walk(t, mode: str) -> str:
    leaf = _leaf(t)
    if leaf is not None:
        return leaf
    if isinstance(t, App):
        fn = _walk(t.fn, mode)
        arg = _walk(t.arg, mode)
        if mode == "nested" and isinstance(t.arg, App):
            arg = f"( {arg} )"
        return f"{fn}{APPLY}{arg}"
    raise TypeError(f"unexpected node {type(t)}")


def _content_spans(text: str) -> list[tuple[int, int]]:
    """Char [start,end) ranges of every content word occurrence in `text`."""
    spans = []
    for w in CONTENT_SET:
        for m in re.finditer(rf"\b{re.escape(w)}\b", text):
            spans.append((m.start(), m.end()))
    return spans


# ── certified reduction trace (terms + fired opcodes) ────────────────────────────
def reduce_trace(term, max_steps=MAX_TRACE_STEPS):
    """Return (term_strings, fired_ops). term_strings[0] = start (no op); each later
    term_strings[i] is the contractum produced by fired_ops[i] (i>=1, ops[0]=None)."""
    terms = [pretty(term)]
    ops: list[str | None] = [None]
    cur = term
    for _ in range(max_steps):
        nxt, fired = step_fired(cur)
        if nxt is None or size(nxt) > MAX_TERM_SIZE:
            break
        terms.append(pretty(nxt))
        ops.append(fired)
        cur = nxt
    return terms, ops


# ── program generators (controlled opcode mixes) — IDENTICAL to v8 ───────────────
def gen_programs(n_each, seed):
    """Build CL programs: minimal pairs (B vs C, B vs S) + multi-step composites.

    Returns list of {id, src, terms, ops, kind, pair_id}. Each is verified to reduce
    and to contain its target opcode(s) via the CERTIFIED trace."""
    rng = random.Random(seed)
    pool = ATOM_POOL
    progs = []
    pid = 0

    def add(src, kind, pair_id=None):
        nonlocal pid
        t = parse(src)
        terms, ops = reduce_trace(t)
        fired = [o for o in ops if o]
        if not fired:
            return False
        progs.append({"id": f"p{pid}", "src": src, "terms": terms, "ops": ops,
                      "kind": kind, "pair_id": pair_id})
        pid += 1
        return True

    for k in range(n_each):
        f, a, b, c, z = rng.sample(pool, 5)
        # ── MINIMAL PAIRS — identical input shape, differ only in order ───────────
        add(f"B {f} {a} {b}", "minpair_BC", pair_id=f"bc{k}")   # f (a b)  order kept
        add(f"C {f} {a} {b}", "minpair_BC", pair_id=f"bc{k}")   # f b a    swapped
        add(f"B {f} {a} {b}", "minpair_BS", pair_id=f"bs{k}")   # f (a b)
        add(f"S {f} {a} {b}", "minpair_BS", pair_id=f"bs{k}")   # f b (a b) dup+distrib
        add(f"D {f} {a} {b} {c}", "minpair_DK", pair_id=f"dk{k}")  # f (a (b c)) kept
        add(f"K ({f} {a} {b}) {z}", "minpair_DK", pair_id=f"dk{k}")  # f a b   drop z
        # ── MULTI-STEP COMPOSITES — within-program B + marked ────────────────────
        add(f"C (B {f} {a}) {b} {z}", "multi_CB", pair_id=f"cb{k}")  # C then B
        add(f"K (B {f} {a} {b}) {z}", "multi_KB", pair_id=f"kb{k}")  # K then B
        add(f"W (B {f} {a}) {b}", "multi_WB", pair_id=f"wb{k}")      # W then B
    return progs


# ── per-step surprisal under the LM softmax over V — PROSE-rendered terms ─────────
def score_program(prog, model, tok, torch_mod, render_mode="flat"):
    """Teacher-force the PROSE trace; per contractum, mean -log p over its span.

    Same spine as v8 (one no_grad forward, offset_mapping alignment); the only change is
    each term is render_term()'d and the atom-only de-confound matches CONTENT words by
    char-span (robust to multi-subword tokens)."""
    terms, ops = prog["terms"], prog["ops"]
    # build the full PROSE string + char span of each rendered contractum (i>=1)
    spans = []
    buf = render_term(terms[0], render_mode)
    for i in range(1, len(terms)):
        buf += SEP
        c0 = len(buf)
        buf += render_term(terms[i], render_mode)
        spans.append((c0, len(buf), ops[i]))
    full = buf
    content_ranges = _content_spans(full)

    enc = tok(full, return_tensors="pt", return_offsets_mapping=True)
    dev = next(model.parameters()).device
    ids = enc["input_ids"][0]
    offsets = enc["offset_mapping"][0].tolist()
    import torch.nn.functional as func
    with torch_mod.no_grad():
        logits = model(input_ids=ids.unsqueeze(0).to(dev),
                       attention_mask=enc["attention_mask"].to(dev)).logits[0]
    logp = func.log_softmax(logits.float(), dim=-1).cpu()
    ids_cpu = ids.cpu()
    # nll[j] = -log p(token_j | prefix), defined for j>=1
    nll = np.full(ids_cpu.shape[0], np.nan)
    for j in range(1, ids_cpu.shape[0]):
        nll[j] = -float(logp[j - 1, ids_cpu[j]])

    def _is_content(ts: int, te: int) -> bool:
        # token [ts,te) is a content token if it OVERLAPS any content-word range.
        # (overlap, not start-containment: the tokenizer attaches the leading space
        # to a word token, putting its start char on the space before the \bword\b.)
        return any(ts < e and te > s for s, e in content_ranges)

    rows = []
    for (c0, c1, op), term_idx in zip(spans, range(1, len(terms)), strict=True):
        tok_js = [j for j, (s, e) in enumerate(offsets)
                  if e > s and s >= c0 and s < c1 and j >= 1]
        vals = [nll[j] for j in tok_js if not np.isnan(nll[j])]
        # de-confounded: order-bearing CONTENT-word tokens only (by char-span;
        # robust to multi-subword content words AND leading-space tokens)
        atom_vals = [nll[j] for j in tok_js if not np.isnan(nll[j])
                     and _is_content(offsets[j][0], offsets[j][1])]
        if not vals:
            continue
        rows.append({"op": op, "surprisal": float(np.mean(vals)), "n_tok": len(vals),
                     "surprisal_atoms": (float(np.mean(atom_vals)) if atom_vals
                                         else None), "n_atoms": len(atom_vals),
                     "term_idx": term_idx, "term_size": len(terms[term_idx])})
    return rows


def paired_contrast(per_prog, kind, op_a, op_b, field="surprisal"):
    """Within-pair (op_a minus op_b) delta over programs sharing pair_id, on `field`."""
    by_pair: dict[str, dict[str, list]] = defaultdict(lambda: {op_a: [], op_b: []})
    for prog, rows in per_prog:
        if prog["kind"] != kind:
            continue
        for r in rows:
            if r["op"] in (op_a, op_b) and r.get(field) is not None:
                by_pair[prog["pair_id"]][r["op"]].append(r[field])
    deltas = []
    for d in by_pair.values():
        if d[op_a] and d[op_b]:
            deltas.append(float(np.mean(d[op_a]) - np.mean(d[op_b])))
    if len(deltas) < 2:
        return None
    arr = np.array(deltas)
    mean = float(arr.mean())
    se = float(arr.std(ddof=1) / np.sqrt(len(arr)))
    t = mean / se if se > 0 else 0.0
    return {"op_a": op_a, "op_b": op_b, "n_pairs": len(deltas),
            "mean_delta": round(mean, 4), "t": round(t, 3),
            "significant": bool(abs(t) > 2.0),
            "direction": "a<b" if mean < 0 else "a>b"}


def main() -> None:
    ap = argparse.ArgumentParser(description="Kernel-ref order-cost PROSE bridge")
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--n-each", type=int, default=24, help="instances per template")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--render-mode", choices=["flat", "nested"], default="flat",
                    help="flat=de-confounded order test (nesting held constant); "
                         "nested=structurally faithful (confounded by nesting depth)")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    render_mode = args.render_mode

    model_name = args.model
    n_each = args.n_each
    if args.smoke:
        # 8B = smallest model where the full lambda function has formed/concentrated
        # (0.6B cannot carry the crystal -> meaningless). 8B = the testing floor.
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-8B"
        n_each = 8
        print("[order-prose] SMOKE MODE (Qwen3-8B = smallest meaningful)")

    progs = gen_programs(n_each, args.seed)
    print(f"[order-prose] {len(progs)} programs (from n_each={n_each}) "
          f"render_mode={render_mode}")
    # show both halves of one B/C minimal pair for sanity (same atoms, order differs)
    for kk in ("B ", "C "):
        for p in progs:
            if p["kind"] == "minpair_BC" and p["src"].startswith(kk):
                print(f"[order-prose]   sample {p['src']!r}: "
                      f"{render_term(p['terms'][-1], render_mode)!r}")
                break

    model, tok, torch_mod = load_model_and_tokenizer(model_name)

    per_prog = []
    for i, prog in enumerate(progs):
        if i % 25 == 0:
            print(f"[order-prose]   scoring {i}/{len(progs)} ...")
        rows = score_program(prog, model, tok, torch_mod, render_mode)
        per_prog.append((prog, rows))

    # ── aggregate: mean surprisal per opcode (full AND atom-only de-confounded) ───
    def op_means_for(field):
        acc: dict[str, list] = defaultdict(list)
        for _prog, rows in per_prog:
            for r in rows:
                if r.get(field) is not None:
                    acc[r["op"]].append(r[field])
        return {op: {"mean": round(float(np.mean(v)), 4),
                     "sd": round(float(np.std(v)), 4), "n": len(v)}
                for op, v in sorted(acc.items())}, acc

    op_means, by_op = op_means_for("surprisal")
    op_means_atoms, by_op_atoms = op_means_for("surprisal_atoms")

    # ── minimal-pair / within-program contrasts, on BOTH metrics ─────────────────
    KINDS = {"B_vs_C_minpair": ("minpair_BC", "B", "C"),
             "B_vs_S_minpair": ("minpair_BS", "B", "S"),
             "D_vs_K_minpair": ("minpair_DK", "D", "K"),
             "B_vs_C_multi": ("multi_CB", "B", "C"),
             "B_vs_K_multi": ("multi_KB", "B", "K"),
             "B_vs_W_multi": ("multi_WB", "B", "W")}
    contrasts = {n: paired_contrast(per_prog, k, a, b)
                 for n, (k, a, b) in KINDS.items()}
    contrasts_atoms = {n: paired_contrast(per_prog, k, a, b, field="surprisal_atoms")
                       for n, (k, a, b) in KINDS.items()}

    def pooled_for(acc):
        presv = [s for op in ORDER_PRESERVING for s in acc.get(op, [])]
        brk = [s for op in ORDER_BREAKING for s in acc.get(op, [])]
        if not (presv and brk):
            return None
        mp, mb = float(np.mean(presv)), float(np.mean(brk))
        return {"order_preserving_mean": round(mp, 4), "n_preserving": len(presv),
                "order_breaking_mean": round(mb, 4), "n_breaking": len(brk),
                "delta": round(mp - mb, 4), "preserving_cheaper": bool(mp < mb)}

    pooled, pooled_atoms = pooled_for(by_op), pooled_for(by_op_atoms)

    # de-confounded headline: atom-only (content-word) B<C minimal pair, IN PROSE
    bc_a = contrasts_atoms["B_vs_C_minpair"]
    b_is_native = bool(bc_a and bc_a["significant"] and bc_a["mean_delta"] < 0)
    verdict = {
        "register": "order-cost PROSE bridge (softmax-over-V surprisal, rendered)",
        "render": "deterministic order-faithful: App(f,x)->'<f> applied to <x>'",
        "render_mode": render_mode,  # flat=de-confounded(nesting held), nested=faithful
        "op_surprisal": op_means, "op_surprisal_atoms": op_means_atoms,
        "minimal_pair_contrasts": contrasts,
        "minimal_pair_contrasts_atoms": contrasts_atoms,
        "order_preserving_vs_breaking": pooled,
        "order_preserving_vs_breaking_atoms": pooled_atoms,
        "b_is_native_order": b_is_native,  # de-confounded (content-word-only), PROSE
        "n_programs": len(progs),
    }

    role = {**{o: "preserve" for o in ORDER_PRESERVING},
            **{o: "BREAK" for o in ORDER_BREAKING}}
    print("\n" + "═" * 74)
    print("KERNEL-REF ORDER-COST [PROSE] — is B the NATIVE softmax-over-V order?")
    print("═" * 74)
    print(f"  programs={len(progs)}   surprisal=mean -log p ; atoms=content-words only")
    print(f"\n  {'op':<4}{'full':>10}{'atoms':>10}{'n':>6}   role")
    for op in sorted(set(op_means) | set(op_means_atoms)):
        fm = op_means.get(op, {}).get("mean", float("nan"))
        am = op_means_atoms.get(op, {}).get("mean", float("nan"))
        nn = op_means.get(op, {}).get("n", 0)
        print(f"  {op:<4}{fm:>10}{am:>10}{nn:>6}   {role.get(op, '?')}")
    for tag, pl in (("full", pooled), ("ATOMS", pooled_atoms)):
        if pl:
            print(f"  [{tag:>5}] preserve {pl['order_preserving_mean']} vs break "
                  f"{pl['order_breaking_mean']}  (Δ={pl['delta']}, "
                  f"cheaper={pl['preserving_cheaper']})")

    def show(title, cs):
        print(f"\n  {title} (a-b; a<b means a cheaper / more native):")
        for name, c in cs.items():
            if c is None:
                print(f"    {name:<18} (insufficient pairs)")
                continue
            sig = "✓" if c["significant"] else " "
            print(f"    {name:<18} d={c['mean_delta']:>8}  t={c['t']:>7}  "
                  f"n={c['n_pairs']:>3}  {c['direction']}  {sig}")
    show("FULL contrasts (confounded by parens/length)", contrasts)
    show("ATOM-ONLY contrasts (DE-CONFOUNDED — the headline)", contrasts_atoms)
    print(f"\n  * B native order [PROSE, B<C atom minpair]: {b_is_native}")
    print("═" * 74 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = f"{model_name.split('/')[-1].lower().replace('.', '-')}_{render_mode}"
    out = {"verdict": verdict,
           "per_program": [{"id": p["id"], "src": p["src"], "kind": p["kind"],
                            "rows": rows} for p, rows in per_prog]}
    (RESULTS_DIR / f"order_cost_v9_prose_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(out), indent=2), encoding="utf-8")
    meta = {"model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "transformers_version": _transformers_version(),
            "n_each": n_each, "n_programs": len(progs), "seed": args.seed,
            "render_mode": render_mode,
            "register": "ORDER-COST PROSE bridge softmax-over-V surprisal"}
    (RESULTS_DIR / f"order_cost_v9_prose_meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[order-prose] wrote {RESULTS_DIR}/order_cost_v9_prose_verdict_{slug}.json")


if __name__ == "__main__":
    main()
