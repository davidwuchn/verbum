"""(d0) DEPTH BUDGET — how many layers does each hop cost; is there room for a third?

Pre-reg: multihop-composition-prereg.md §Depth-budget (s280, gates FROZEN before run).
Gates the 3-hop d1 design. The s279 pipeline occupies nearly the whole 36-layer stack
(install L9 -> bridge causally live L15-20 -> class legible L30 -> covering L33). The
s279 layersweep is confounded for budget purposes (varied install AND build layer,
read only the final hop). This instrument deconfounds by STAGE-RESOLVED reads:

  Arm A  install-layer sweep {5,9,13,17,21,25,29,33}, matched-build d_E (ALL sweep
         layers captured in ONE pass per declarative), per install layer:
           hop-1 behavioral = class query "A {x} is a kind of ___" (bird/fish/mammal)
           hop-2 behavioral = covering query (s279 instrument unchanged)
           logit-lens class+covering peak layers (6 strong entities; weak mammal trio
           excluded so install-strength cannot masquerade as budget)
         + basis-drift covariate cos(d_E@L, d_E@9).
  Arm B  bridge read-window fine sweep: install L9, class-axis swap (2c machinery) at
         L_edit in {11,13,...,33}, 6 strong entities x 2 targets, matched-norm random
         null beside, single prefix (granularity read).

Frozen accounting: L_max_1hop / L_max_2hop (>= 0.7 of ceiling / of @L9 value),
D_hop2 = L_max_1hop - L_max_2hop, L_close = first edit layer where flip <= rand+0.10.
Verdicts: BUDGET-VISIBLE / DEPTH-BUDGET-UNMEASURED / PIPELINE-SLIDES (Spearman rho of
class peak vs install L > 0.8) / 3-HOP-ROOM-AT-4B iff L_max_2hop - 9 >= D_hop2.

`lambda measure`: budget = fuel (layers remaining), NOT install strength — the class
read discriminates. `lambda yardstick`: predictions frozen a-priori in the pre-reg;
random null beside every swap; ceilings gate every behavioral read.

License: MIT (`lambda provenance`).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from operand_multihop import (
    CLASS_ENT,
    CLASSES,
    COVER,
    COVER_LABELS,
    COVER_PREFIXES,
    COVER_QUERY,
    ENT_CLASS,
    ENTS,
    FRAMES,
    NONCE,
    add_hook_at,
    tid,
)
from transformers import AutoModelForCausalLM, AutoTokenizer

CLASS_PREFIXES = [
    "A parrot is a kind of bird.\nA goat is a kind of mammal.\n"
    "A bass is a kind of fish.\n",
    "A pigeon is a kind of bird.\nA sheep is a kind of mammal.\n"
    "A perch is a kind of fish.\n",
]
CLASS_QUERY = "A {x} is a kind of"
STRONG = ["eagle", "hawk", "salmon", "shark", "bear", "cat"]


def spearman(x, y):
    """rank correlation, small-n, numpy only."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return None
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--install-layers", type=int, nargs="+",
                    default=[5, 9, 13, 17, 21, 25, 29, 33])
    ap.add_argument("--swap-layers", type=int, nargs="+",
                    default=[11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33])
    ap.add_argument("--ref-layer", type=int, default=9,
                    help="standard-install reference layer (scales with model depth; "
                         "9 for 36-layer 4B, ~16 for 64-layer 32B). Used for Arm B and "
                         "as the cover-acc accounting reference.")
    ap.add_argument("--dtype", default="bfloat16", choices=["float32", "bfloat16"])
    ap.add_argument("--device", default="mps")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--out", default="results/ffn-bake/operand-depthbudget-qwen3-4b")
    args = ap.parse_args()

    if args.smoke:
        args.install_layers = [9, 21]
        args.swap_layers = [15, 25]
    S = args.scale
    REF_L = args.ref_layer                                 # standard install (depth-scaled)
    if REF_L not in args.install_layers:
        args.install_layers = sorted([*args.install_layers, REF_L])
    dev = (args.device if (args.device != "mps" or torch.backends.mps.is_available())
           else "cpu")
    rng = np.random.default_rng(0)
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    dec = model.model.layers
    n_layers = len(dec)
    cover_ids = {lb: tid(tok, lb) for lb in COVER_LABELS}
    class_ids = {c: tid(tok, c) for c in CLASSES}
    nonce_last = tok(" " + NONCE, add_special_tokens=False).input_ids[-1]
    print(f"[depth] {args.model_id} layers={n_layers} install={args.install_layers} "
          f"swap={args.swap_layers} dev={dev}")

    def find_slot(ids_list):
        idx = [i for i, t in enumerate(ids_list) if t == nonce_last]
        return idx[-1] if idx else len(ids_list) - 1

    def pred_label(word, prefixes, query, label_ids, adds=None, first_only=False):
        preds = []
        for pfx in (prefixes[:1] if first_only else prefixes):
            ids = tok(pfx + query.format(x=word), return_tensors="pt").to(dev)
            slot = find_slot(ids.input_ids[0].tolist())
            handles = []
            for (li, vec) in (adds or []):
                vt = torch.tensor(vec, dtype=torch.float32, device=dev)
                handles.append(dec[li].register_forward_hook(add_hook_at(vt, slot)))
            with torch.no_grad():
                lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
            for hd in handles:
                hd.remove()
            preds.append(max(label_ids, key=lambda lb: lo[label_ids[lb]]))
        return max(label_ids, key=lambda lb: sum(p == lb for p in preds))

    def cover_pred(word, adds=None, first_only=False):
        return pred_label(word, COVER_PREFIXES, COVER_QUERY, cover_ids,
                          adds, first_only)

    def class_pred(word, adds=None):
        return pred_label(word, CLASS_PREFIXES, CLASS_QUERY, class_ids, adds)

    # ── ceilings (real words, no install) ─────────────────────────────────────────
    cover_ceil = {e: int(cover_pred(e) == COVER[ENT_CLASS[e]]) for e in ENTS}
    class_ceil = {e: int(class_pred(e) == ENT_CLASS[e]) for e in ENTS}
    valid_cov = [e for e in ENTS if cover_ceil[e]]
    valid_cls = [e for e in ENTS if class_ceil[e]]
    ceil_cls_rate = round(float(np.mean(list(class_ceil.values()))), 3)
    base_cover = cover_pred(NONCE)
    base_class = class_pred(NONCE)
    print(f"[depth] ceilings: cover={np.mean(list(cover_ceil.values())):.3f} "
          f"class={ceil_cls_rate} | bare-nonce cover={base_cover} class={base_class}")

    # ── build d_E at ALL sweep layers in ONE pass per declarative ─────────────────
    def decl(fr, obj):
        s, v = fr
        return f"{s} {v} a {obj}."

    caps = sorted(set(args.install_layers))
    per = {L: {e: [] for e in ENTS} for L in caps}
    for fr in FRAMES:
        for e in ENTS:
            store: dict[int, np.ndarray] = {}
            handles = []
            for L in caps:
                def mk(L_, store=store):
                    def hook(_m, _i, out):
                        h = out[0] if isinstance(out, tuple) else out
                        store[L_] = h[0, -2, :].detach().float().cpu().numpy()
                    return hook
                handles.append(dec[L].register_forward_hook(mk(L)))
            ids = tok(decl(fr, e), return_tensors="pt").to(dev)
            with torch.no_grad():
                model(**ids)
            for hd in handles:
                hd.remove()
            for L in caps:
                per[L][e].append(store[L])
    d_E, d_class, drift = {}, {}, {}
    for L in caps:
        em = {e: np.mean(per[L][e], axis=0) for e in ENTS}
        gm = np.mean([em[e] for e in ENTS], axis=0)
        d_E[L] = {e: em[e] - gm for e in ENTS}
        d_class[L] = {c: np.mean([d_E[L][e] for e in CLASS_ENT[c]], axis=0)
                      for c in CLASSES}
    for L in caps:
        cs = []
        for e in ENTS:
            a, b = d_E[L][e], d_E[REF_L][e]
            cs.append(float(a @ b / ((np.linalg.norm(a) * np.linalg.norm(b)) + 1e-9)))
        drift[L] = round(float(np.mean(cs)), 4)

    # ── logit-lens peaks (class + covering) with install at L ─────────────────────
    norm_f = model.model.norm
    unembed = model.lm_head

    def lens_peaks(e, L):
        pfx = COVER_PREFIXES[0]
        ids = tok(pfx + COVER_QUERY.format(x=NONCE), return_tensors="pt").to(dev)
        slot = find_slot(ids.input_ids[0].tolist())
        vt = torch.tensor(d_E[L][e] * S, dtype=torch.float32, device=dev)
        hd = dec[L].register_forward_hook(add_hook_at(vt, slot))
        with torch.no_grad():
            out = model(**ids, output_hidden_states=True)
        hd.remove()
        ci = CLASSES.index(ENT_CLASS[e])
        cls_m, cov_m = [], []
        for h in out.hidden_states:
            last = h[0, -1, :]
            with torch.no_grad():
                lg = unembed(norm_f(last.unsqueeze(0))).float().cpu().numpy()[0]
            cls_m.append([lg[class_ids[c]] for c in CLASSES])
            cov_m.append([lg[cover_ids[COVER[c]]] for c in CLASSES])
        cls_m, cov_m = np.array(cls_m), np.array(cov_m)

        def marg(arr):
            others = [arr[:, j] for j in range(3) if j != ci]
            return arr[:, ci] - np.max(others, axis=0)
        # restrict the peak search to POST-install layers: before L the injected
        # content does not exist, so early "peaks" are the bare-nonce prior
        # (smoke-surfaced: install@21 read a spurious class peak at L12).
        off = L + 1
        return (off + int(np.argmax(marg(cls_m)[off:])),
                off + int(np.argmax(marg(cov_m)[off:])))

    # ── Arm A: stage-resolved install sweep ───────────────────────────────────────
    strong = [e for e in STRONG if cover_ceil[e] and class_ceil[e]]
    armA = {}
    for L in args.install_layers:
        cls_hits = [int(class_pred(NONCE, adds=[(L, d_E[L][e] * S)]) == ENT_CLASS[e])
                    for e in valid_cls]
        cov_hits = [int(cover_pred(NONCE, adds=[(L, d_E[L][e] * S)])
                        == COVER[ENT_CLASS[e]]) for e in valid_cov]
        peaks = [lens_peaks(e, L) for e in strong]
        armA[str(L)] = {
            "class_acc": round(float(np.mean(cls_hits)), 3),
            "cover_acc": round(float(np.mean(cov_hits)), 3),
            "class_peak_median": float(np.median([p[0] for p in peaks])),
            "cover_peak_median": float(np.median([p[1] for p in peaks])),
            "drift_cos_vs_L9": drift[L]}
        a = armA[str(L)]
        print(f"  [A] L={L:2d} class={a['class_acc']} cover={a['cover_acc']} "
              f"peaks cls={a['class_peak_median']} cov={a['cover_peak_median']} "
              f"drift={a['drift_cos_vs_L9']}")

    # ── Arm B: bridge read-window fine sweep (install fixed at REF_L) ─────────────
    dim = d_E[REF_L][ENTS[0]].shape[0]

    def rand_vec(norm):
        v = rng.standard_normal(dim)
        return v / (np.linalg.norm(v) + 1e-9) * norm

    armB = {}
    for lb in args.swap_layers:
        flips, rands = [], []
        for e in strong:
            c = ENT_CLASS[e]
            for cp in CLASSES:
                if cp == c:
                    continue
                swap = (d_class[REF_L][cp] - d_class[REF_L][c]) * S
                pred = cover_pred(NONCE, adds=[(REF_L, d_E[REF_L][e] * S),
                                               (lb, swap)], first_only=True)
                flips.append(int(pred == COVER[cp]))
                rpred = cover_pred(NONCE, adds=[(REF_L, d_E[REF_L][e] * S),
                                                (lb, rand_vec(np.linalg.norm(swap)))],
                                   first_only=True)
                rands.append(int(rpred == COVER[cp]))
        armB[str(lb)] = {"flip": round(float(np.mean(flips)), 3),
                         "random": round(float(np.mean(rands)), 3),
                         "n": len(flips)}
        b = armB[str(lb)]
        print(f"  [B] L_edit={lb:2d} flip={b['flip']} random={b['random']}")

    # ── frozen accounting + verdicts ──────────────────────────────────────────────
    Ls = sorted(args.install_layers)
    ref = armA[str(REF_L)]
    ok1 = [L for L in Ls if armA[str(L)]["class_acc"] >= 0.7 * ceil_cls_rate]
    ok2 = [L for L in Ls if armA[str(L)]["cover_acc"] >= 0.7 * ref["cover_acc"]]
    L_max_1hop = max(ok1) if ok1 else None
    L_max_2hop = max(ok2) if ok2 else None
    d_hop2 = (L_max_1hop - L_max_2hop
              if L_max_1hop is not None and L_max_2hop is not None else None)
    budget_visible = any(
        armA[str(L)]["class_acc"] >= 0.7 * ceil_cls_rate
        and armA[str(L)]["cover_acc"] <= 0.5 * ref["cover_acc"] for L in Ls)
    fail_band = [L for L in Ls if armA[str(L)]["cover_acc"] < 0.5 * ref["cover_acc"]]
    unmeasured = (not budget_visible) and all(
        armA[str(L)]["class_acc"] < 0.7 * ceil_cls_rate for L in fail_band)
    surv = [L for L in Ls if armA[str(L)]["cover_acc"] >= 0.7 * ref["cover_acc"]]
    rho = spearman(surv, [armA[str(L)]["class_peak_median"] for L in surv])
    slides = bool(rho is not None and rho > 0.8)
    closes = [int(lb) for lb in args.swap_layers
              if armB[str(lb)]["flip"] <= armB[str(lb)]["random"] + 0.10]
    L_close = min(closes) if closes else None
    room = (L_max_2hop is not None and d_hop2 is not None
            and (L_max_2hop - REF_L) >= d_hop2)
    print(f"\n[depth] L_max_1hop={L_max_1hop} L_max_2hop={L_max_2hop} "
          f"D_hop2={d_hop2} L_close={L_close} slide_rho={rho}")
    print(f"[depth] VERDICT BUDGET-VISIBLE   = {budget_visible}")
    print(f"[depth] VERDICT UNMEASURED       = {unmeasured}")
    print(f"[depth] VERDICT PIPELINE-SLIDES  = {slides}")
    print(f"[depth] VERDICT 3-HOP-ROOM-AT-4B = {room}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    res = {"model": args.model_id, "scale": S, "n_layers": n_layers,
           "ref_layer": REF_L,
           "install_layers": Ls, "swap_layers": args.swap_layers,
           "class_ceiling": ceil_cls_rate,
           "cover_ceiling": round(float(np.mean(list(cover_ceil.values()))), 3),
           "bare_nonce": {"cover": base_cover, "class": base_class},
           "strong_entities": strong, "armA": armA, "armB": armB,
           "L_max_1hop": L_max_1hop, "L_max_2hop": L_max_2hop,
           "D_hop2": d_hop2, "L_close": L_close, "slide_spearman": rho,
           "verdict_BUDGET_VISIBLE": budget_visible,
           "verdict_UNMEASURED": unmeasured,
           "verdict_PIPELINE_SLIDES": slides,
           "verdict_3HOP_ROOM_AT_4B": bool(room)}
    (out / "depth_budget.json").write_text(json.dumps(res, indent=2))
    print(f"[depth] wrote {out}/depth_budget.json")


if __name__ == "__main__":
    main()
