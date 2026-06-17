#!/usr/bin/env python3
# register: ORDER-COST softmax-over-V surprisal — FRAME ROBUSTNESS (3rd render frame)
"""Kernel-ref ORDER-COST read, FRAME-ROBUSTNESS — is the flat B<C native-order result
robust to a DIFFERENT render frame, or specific to the "applied to" infix?
(s238 first-action path 1 / s237 fork path 2; clean FRAME-swap of v9.)

THE QUESTION THIS ANSWERS (λ measure, two-sided): v9 found flat B<C decisive at 14B
(atom minpair t=-8.05, b_is_native_order=True) and scale-universal across Qwen, with the
gross signal universal across Qwen⊗OLMo⊗Gemma but the SHARP single-step expression
Qwen-specific. The v9 surface frame was the infix " applied to " — a string-associative
connector that lets FLAT mode collapse B (f a b) and C (f b a) to a flat token chain
differing ONLY in atom order. Is the win a property of COMPOSITION-ORDER, or an artifact
of that one infix? This re-runs the same certified traces under a SECOND frame:

    applied_to  App(f,x) -> "<f> applied to <x>"        (v9, the baseline)
    result_of   App(f,x) -> "the result of <f> on <x>"  (the 3rd frame)

FLAT realization of result_of (the de-confounded headline, analogous to v9 flat):
    prefix "the result of " applied ONCE at the top + leaves joined by the " on " infix
      B  f (a b) -> "the result of f on a on b"   atoms f,a,b   order KEPT
      C  f b a   -> "the result of f on b on a"   atoms f,b,a   SWAPPED
    -> leaves differ ONLY in order; a pure order test under a NEW lexicon+syntax.

NESTED realization (faithful circumfix): App(f,x) -> "the result of <f> on <x>"
    recursively, so the inner application sits in a nested clause (confounded by
    nest POSITION, kept for the faithful complement — see CAVEAT).

CAVEAT (λ measure, honest): the "result of...on" frame is a CIRCUMFIX, not a flat infix
like "applied to". In FLAT mode the single " the result of " prefix + chained " on "
makes B/C surface-identical-structure differing only in atom order (the clean analog).
In NESTED mode B's inner clause sits at the TAIL ("...on the result of a on b") and C's
at the HEAD ("the result of the result of f on b on a"); both have EQUAL nesting DEPTH
(unlike the v9 nested confound where B nested and C was flat = unequal depth), but the
nest POSITION differs -> nested result_of conflates atom-order with nest-position. The
FLAT result_of is the load-bearing frame-robustness read; nested is the faithful comp.

VERDICT LOGIC:
  - flat B<C under result_of (atoms, sig negative) -> the native-order result is
    FRAME-ROBUST: composition-order preference is not an "applied to" artifact.
  - flat B~C under result_of -> the v9 win is (partly) frame-specific; weakens the
    surface-frame generality of the native-order claim (the order direction may be
    carried by the specific infix's induction/copy dynamics).
  - off-Qwen (OLMo/Gemma): does the SINGLE-STEP minpair SHARPEN under result_of where
    it was near-symmetric under applied_to (s237)? frame may unlock the sharp read.

Usage:
    uv run python scripts/experiments/kernel_reference_order_cost_v10_frame.py --smoke
    uv run python scripts/experiments/kernel_reference_order_cost_v10_frame.py \
        --render-frame result_of                       # 14B, flat result_of
    uv run python scripts/experiments/kernel_reference_order_cost_v10_frame.py \
        --model allenai/OLMo-2-1124-13B --render-frame result_of

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))
sys.path.insert(0, str(_ROOT / "scripts" / "instruments"))

# Frame-independent machinery is REUSED verbatim from v9 (DRY; v9 stays immutable for
# reproducibility). Only the render + per-frame scoring is redefined here.
from kernel_reference_order_cost_v9_prose import (  # noqa: E402
    ORDER_BREAKING,
    ORDER_PRESERVING,
    RESULTS_DIR,
    SEP,
    _content_spans,
    _leaf,
    gen_programs,
    paired_contrast,
    reduce_trace,  # noqa: F401  (re-exported for parity / interactive use)
)
from opcode_monitor_v2 import (  # noqa: E402
    _git_sha,
    _json_safe,
    _transformers_version,
    load_model_and_tokenizer,
)

from verbum.lambda_ast import App, parse  # noqa: E402

# ── render frames: how App(fn, arg) becomes prose ────────────────────────────────
# Each frame: prefix (flat, applied ONCE at top), infix (flat leaf connector), and a
# nested(fn, arg, arg_is_app) realizer (faithful circumfix). New frames slot in here
# (open slot > closed dispatch).
FRAMES = {
    "applied_to": {  # v9 baseline — string-associative infix
        "prefix": "",
        "infix": " applied to ",
        "nested": lambda fn, arg, is_app: (
            f"{fn} applied to ( {arg} )" if is_app else f"{fn} applied to {arg}"
        ),
    },
    "result_of": {  # 3rd frame — circumfix; flat uses one prefix + chained " on "
        "prefix": "the result of ",
        "infix": " on ",
        "nested": lambda fn, arg, is_app: f"the result of {fn} on {arg}",
    },
}


def _walk(t, frame: dict, mode: str) -> str:
    leaf = _leaf(t)
    if leaf is not None:
        return leaf
    if isinstance(t, App):
        fn = _walk(t.fn, frame, mode)
        arg = _walk(t.arg, frame, mode)
        if mode == "nested":
            return frame["nested"](fn, arg, isinstance(t.arg, App))
        return f"{fn}{frame['infix']}{arg}"  # flat: leaves joined by infix, no brackets
    raise TypeError(f"unexpected node {type(t)}")


def render_term(term_str: str, frame: dict, mode: str = "flat") -> str:
    """Order-faithful prose under `frame`. flat: prefix once + leaves joined by infix
    (de-confounded order test); nested: recursive circumfix (faithful, nest-position-
    confounded). applied_to+flat reproduces v9 exactly (prefix='')."""
    body = _walk(parse(term_str), frame, mode)
    return frame["prefix"] + body if mode == "flat" else body


# ── per-step surprisal under the LM softmax over V — frame-rendered terms ─────────
# (Spine identical to v9.score_program; the only change is render_term(..., frame).)
def score_program(prog, model, tok, torch_mod, frame, render_mode="flat"):
    terms, ops = prog["terms"], prog["ops"]
    spans = []
    buf = render_term(terms[0], frame, render_mode)
    for i in range(1, len(terms)):
        buf += SEP
        c0 = len(buf)
        buf += render_term(terms[i], frame, render_mode)
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
    nll = np.full(ids_cpu.shape[0], np.nan)
    for j in range(1, ids_cpu.shape[0]):
        nll[j] = -float(logp[j - 1, ids_cpu[j]])

    def _is_content(ts: int, te: int) -> bool:
        return any(ts < e and te > s for s, e in content_ranges)

    rows = []
    for (c0, c1, op), term_idx in zip(spans, range(1, len(terms)), strict=True):
        tok_js = [j for j, (s, e) in enumerate(offsets)
                  if e > s and s >= c0 and s < c1 and j >= 1]
        vals = [nll[j] for j in tok_js if not np.isnan(nll[j])]
        atom_vals = [nll[j] for j in tok_js if not np.isnan(nll[j])
                     and _is_content(offsets[j][0], offsets[j][1])]
        if not vals:
            continue
        rows.append({"op": op, "surprisal": float(np.mean(vals)), "n_tok": len(vals),
                     "surprisal_atoms": (float(np.mean(atom_vals)) if atom_vals
                                         else None), "n_atoms": len(atom_vals),
                     "term_idx": term_idx, "term_size": len(terms[term_idx])})
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description="Kernel-ref order-cost FRAME robustness")
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--n-each", type=int, default=24, help="instances per template")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--render-frame", choices=sorted(FRAMES), default="result_of",
                    help="applied_to=v9 baseline infix; result_of=3rd frame circumfix")
    ap.add_argument("--render-mode", choices=["flat", "nested"], default="flat",
                    help="flat=de-confounded order test; nested=faithful (see CAVEAT)")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    render_mode = args.render_mode
    frame_name = args.render_frame
    frame = FRAMES[frame_name]

    model_name = args.model
    n_each = args.n_each
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-8B"
        n_each = 8
        print("[order-frame] SMOKE MODE (Qwen3-8B = smallest meaningful)")

    progs = gen_programs(n_each, args.seed)
    print(f"[order-frame] {len(progs)} programs (n_each={n_each}) "
          f"frame={frame_name} mode={render_mode}")
    # show both halves of one B/C minimal pair (same atoms, order differs)
    for kk in ("B ", "C "):
        for p in progs:
            if p["kind"] == "minpair_BC" and p["src"].startswith(kk):
                print(f"[order-frame]   sample {p['src']!r}: "
                      f"{render_term(p['terms'][-1], frame, render_mode)!r}")
                break

    model, tok, torch_mod = load_model_and_tokenizer(model_name)

    per_prog = []
    for i, prog in enumerate(progs):
        if i % 25 == 0:
            print(f"[order-frame]   scoring {i}/{len(progs)} ...")
        rows = score_program(prog, model, tok, torch_mod, frame, render_mode)
        per_prog.append((prog, rows))

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

    bc_a = contrasts_atoms["B_vs_C_minpair"]
    b_is_native = bool(bc_a and bc_a["significant"] and bc_a["mean_delta"] < 0)
    verdict = {
        "register": "order-cost FRAME robustness (softmax-over-V surprisal, rendered)",
        "render_frame": frame_name,
        "render_mode": render_mode,
        "frame_template": ("App(f,x) -> 'the result of <f> on <x>'"
                           if frame_name == "result_of"
                           else "App(f,x) -> '<f> applied to <x>'"),
        "op_surprisal": op_means, "op_surprisal_atoms": op_means_atoms,
        "minimal_pair_contrasts": contrasts,
        "minimal_pair_contrasts_atoms": contrasts_atoms,
        "order_preserving_vs_breaking": pooled,
        "order_preserving_vs_breaking_atoms": pooled_atoms,
        # de-confounded (content-word-only), THIS frame:
        "b_is_native_order": b_is_native,
        "n_programs": len(progs),
    }

    role = {**{o: "preserve" for o in ORDER_PRESERVING},
            **{o: "BREAK" for o in ORDER_BREAKING}}
    print("\n" + "═" * 74)
    print(f"KERNEL-REF ORDER-COST [FRAME={frame_name}/{render_mode}] — B<C robust?")
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
    print(f"\n  * B native order [{frame_name}/{render_mode}, B<C atom minpair]: "
          f"{b_is_native}")
    print("═" * 74 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = (f"{model_name.split('/')[-1].lower().replace('.', '-')}"
            f"_{frame_name}_{render_mode}")
    out = {"verdict": verdict,
           "per_program": [{"id": p["id"], "src": p["src"], "kind": p["kind"],
                            "rows": rows} for p, rows in per_prog]}
    (RESULTS_DIR / f"order_cost_v10_frame_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(out), indent=2), encoding="utf-8")
    meta = {"model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "transformers_version": _transformers_version(),
            "n_each": n_each, "n_programs": len(progs), "seed": args.seed,
            "render_frame": frame_name, "render_mode": render_mode,
            "register": "ORDER-COST FRAME robustness softmax-over-V surprisal"}
    (RESULTS_DIR / f"order_cost_v10_frame_meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[order-frame] wrote {RESULTS_DIR}/order_cost_v10_frame_verdict_{slug}.json")


if __name__ == "__main__":
    main()
