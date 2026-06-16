#!/usr/bin/env python3
# register: ORDER-COST / softmax-over-V surprisal (is B the native order?)
"""Kernel-ref ORDER-COST read — is B the NATIVE softmax-over-V order? (s235 prong 2).

Michael (s235): "if B is an ordering of operations then maybe it defaults to the order
the softmax over all V uses natively?" Grounded in ffn-reduction-trace.md: attention
executes the FFN-compiled program via softmax over V = beta-reduction by weighted
combination. So softmax-over-V IS the execution order. Hypothesis: B has no amplitude
in ANY register (FFN gate / attn / per-head / gradient flat; only faint-rising in
curvature, s235 1c-ii) because B = COMPOSITION = the model's DEFAULT autoregressive
order — it rides the native left-to-right copy/induction order for free, so it carries
no marked feature.

BCKW = the structural rules of logic: B=associativity/COMPOSITION (preserves order),
C=exchange/PERMUTATION (swaps), K=weakening/DELETION (drops), W=contraction (copies).
The DETECTABLE combinators ({C,I,K,Y}) BREAK the native order; B RESPECTS it. So B is
invisible-as-amplitude because it IS the substrate the others deviate from.

THE TEST (no amplitude classifier — pure softmax over V): take a composite CL program,
get its CERTIFIED reduction trace (step_fired -> contractum + opcode per step),
teacher-force the trace "t0 -> t1 -> ... -> tn", read per-step SURPRISAL (mean -log p
under the LM softmax over V) of each contractum term.
  - B-step (order-preserving): contractum tokens stay in SOURCE order -> native copy
    order predicts them -> LOW surprisal. Composition is "free".
  - C-step (permutation): contractum SWAPS tokens -> fights native order -> HIGH
    surprisal. C is detectable precisely as the deviation.
THE MINIMAL PAIR (headline): "B f a b -> f (a b)" (order kept) vs "C f a b -> f b a"
(swapped) — same input shape, ONLY difference is permutation. paired by atom-set.

VERDICT LOGIC (lambda measure, two-sided):
  - surprisal(B) < surprisal(C) (and < marked), within-program/minimal-pair paired ->
    B = NATIVE softmax order CONFIRMED; composition is the free autoregressive default,
    explaining its amplitude-absence everywhere AND unifying with the 1c-ii curvature
    climb (same composition: gradient-side a product/2nd-order, token-side the order).
  - surprisal(B) ~ surprisal(marked) -> B is NOT native default; absence is genuine
    diffuseness; fall back to the amplitude trace-order bridge.

Usage:
    uv run python scripts/experiments/kernel_reference_order_cost_v8.py --smoke
    uv run python scripts/experiments/kernel_reference_order_cost_v8.py            # 14B

License: MIT
"""

from __future__ import annotations

import argparse
import json
import random
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

from verbum.lambda_ast import parse, pretty, size, step_fired  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "kernel-reference-audit"
SEP = " -> "
ORDER_PRESERVING = {"B", "I", "D"}   # output keeps source left-to-right order
ORDER_BREAKING = {"C", "K", "W", "S", "M"}  # permute / delete / duplicate
ATOM_POOL = ["f", "g", "h", "p", "q", "u", "v", "a", "b", "c", "d", "e", "m", "n"]
ATOM_SET = set(ATOM_POOL)  # order-bearing leaves; de-confounds parens/length
MAX_TRACE_STEPS = 8
MAX_TERM_SIZE = 60


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


# ── program generators (controlled opcode mixes) ─────────────────────────────────
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


# ── per-step surprisal under the LM softmax over V ───────────────────────────────
def score_program(prog, model, tok, torch_mod):
    """Teacher-force the trace; per contractum term, mean -log p(token) over its span.

    One forward (no_grad). Token/char alignment via offset_mapping (fast tokenizer)."""
    terms, ops = prog["terms"], prog["ops"]
    # build the full string + char span of each contractum term (i>=1)
    spans = []
    buf = terms[0]
    for i in range(1, len(terms)):
        buf += SEP
        c0 = len(buf)
        buf += terms[i]
        spans.append((c0, len(buf), ops[i]))
    full = buf

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

    rows = []
    for (c0, c1, op), term_idx in zip(spans, range(1, len(terms)), strict=True):
        tok_js = [j for j, (s, e) in enumerate(offsets)
                  if e > s and s >= c0 and s < c1 and j >= 1]
        vals = [nll[j] for j in tok_js if not np.isnan(nll[j])]
        # de-confounded: order-bearing ATOM tokens only (drop parens/structure/length)
        atom_vals = [nll[j] for j in tok_js if not np.isnan(nll[j])
                     and tok.decode([int(ids_cpu[j])]).strip() in ATOM_SET]
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
    ap = argparse.ArgumentParser(description="Kernel-ref order-cost (B native order?)")
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--n-each", type=int, default=24, help="instances per template")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    model_name = args.model
    n_each = args.n_each
    if args.smoke:
        # 8B = smallest model where the full lambda function has formed/concentrated
        # (0.6B cannot carry the crystal -> meaningless). 8B = the testing floor.
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-8B"
        n_each = 8
        print("[order] SMOKE MODE (Qwen3-8B = smallest meaningful)")

    progs = gen_programs(n_each, args.seed)
    print(f"[order] {len(progs)} programs (from n_each={n_each})")

    model, tok, torch_mod = load_model_and_tokenizer(model_name)

    per_prog = []
    for i, prog in enumerate(progs):
        if i % 25 == 0:
            print(f"[order]   scoring {i}/{len(progs)} ...")
        rows = score_program(prog, model, tok, torch_mod)
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

    # de-confounded headline: atom-only B<C minimal pair
    bc_a = contrasts_atoms["B_vs_C_minpair"]
    b_is_native = bool(bc_a and bc_a["significant"] and bc_a["mean_delta"] < 0)
    verdict = {
        "register": "order-cost (softmax-over-V surprisal of certified trace)",
        "op_surprisal": op_means, "op_surprisal_atoms": op_means_atoms,
        "minimal_pair_contrasts": contrasts,
        "minimal_pair_contrasts_atoms": contrasts_atoms,
        "order_preserving_vs_breaking": pooled,
        "order_preserving_vs_breaking_atoms": pooled_atoms,
        "b_is_native_order": b_is_native,  # de-confounded (atom-only)
        "n_programs": len(progs),
    }

    role = {**{o: "preserve" for o in ORDER_PRESERVING},
            **{o: "BREAK" for o in ORDER_BREAKING}}
    print("\n" + "═" * 74)
    print("KERNEL-REF ORDER-COST — is B the NATIVE softmax-over-V order?")
    print("═" * 74)
    print(f"  programs={len(progs)}   surprisal=mean -log p ; atoms=order-bearing only")
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
    print(f"\n  * B native order [DE-CONFOUNDED B<C atom minpair, sig]: {b_is_native}")
    print("═" * 74 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    out = {"verdict": verdict,
           "per_program": [{"id": p["id"], "src": p["src"], "kind": p["kind"],
                            "rows": rows} for p, rows in per_prog]}
    (RESULTS_DIR / f"order_cost_v8_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(out), indent=2), encoding="utf-8")
    meta = {"model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "transformers_version": _transformers_version(),
            "n_each": n_each, "n_programs": len(progs), "seed": args.seed,
            "register": "ORDER-COST softmax-over-V surprisal of certified trace"}
    (RESULTS_DIR / f"order_cost_v8_meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[order] wrote {RESULTS_DIR}/order_cost_v8_verdict_{slug}.json")


if __name__ == "__main__":
    main()
