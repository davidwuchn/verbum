"""(a) MULTI-HOP composition — chained f(g(X)) over ONE installed operand.

Pre-registration: mementum/knowledge/explore/multihop-composition-prereg.md.
The sharper prize / successor to general-composition (s278). Arm-2 there showed ONE
resident op over the installed operand. This asks: does the resident routing chain TWO
sequential ops — g(X) = the animal CLASS (an UNSTATED intermediate, bird/fish/mammal
inferred from d_E), then f(class) = the class COVERING (feathers/scales/fur) — so the
answer f(g(X)) is MEDIATED by a latent category bridge never present in the prompt?

Gates (frozen in the pre-reg, verdict = Gate-1 AND >=2 of {2a,2b,2c}):
  Gate 1  BEHAVIORAL  : install E, "A {nonce} is covered in __" -> covering; +content.
  Gate 2a DEPTH-ORDER : logit-lens the readout per layer -> class token peaks EARLIER
                        than the covering token (intermediate first). shuffled-null.
  Gate 2b CENTROID    : install the CLASS centroid (individual identity averaged out) ->
                        covering still resolves = property reached via CLASS not lookup.
  Gate 2c BRIDGE-SWAP : with E installed at L, add a class-axis swap (centroid diff)
                        at a LATE layer -> covering flips to the swapped class, content-
                        specifically; random matched-norm late add does NOT flip = hop-2
                        reads a class variable that persists late (hop-1's product).

`λ measure`: operand = VALUE (d_E, d_class); g,f = ROUTING; readout = logits; bridge
localized by DEPTH (2a) + LATE zone-steer (2c), never single-head (P-DSP-1: 0/128).
`λ yardstick`: nulls beside every number; real-word ceiling gates each cell; predict
a-priori, gate on nulls, no forced fit. 4B (0.6B squish). Category-MEDIATION, not a
of a literal traced two-node circuit. A RUNG, hook-not-weight, not scale-final.

License: MIT (`λ provenance`; SuperBake method-reference only).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# entity -> class -> covering. Balanced 3 classes x 6 entities. Covering = closed 3-way.
CLASS_ENT = {
    "bird": ["eagle", "hawk", "owl", "crow", "sparrow", "robin"],
    "fish": ["salmon", "shark", "tuna", "trout", "cod", "carp"],
    "mammal": ["wolf", "fox", "bear", "tiger", "rabbit", "cat"],
}
COVER = {"bird": "feathers", "fish": "scales", "mammal": "fur"}
ENT_CLASS = {e: c for c, es in CLASS_ENT.items() for e in es}
ENTS = list(ENT_CLASS)
CLASSES = list(CLASS_ENT)
COVER_LABELS = list(COVER.values())          # [feathers, scales, fur]
NONCE = "zorp"

# covering cloze: held-out exemplars (parrot/goat/bass) disjoint from the test entities.
COVER_PREFIXES = [
    "A parrot is covered in feathers.\nA goat is covered in fur.\n"
    "A bass is covered in scales.\n",
    "A pigeon is covered in feathers.\nA sheep is covered in fur.\n"
    "A perch is covered in scales.\n",
]
COVER_QUERY = "A {x} is covered in"

# d_E build: cross-task declaratives (disjoint frames)
FRAMES = [("The farmer", "saw"), ("The child", "drew"), ("The hunter", "tracked"),
          ("A woman", "bought"), ("The boy", "chased"), ("A man", "found"),
          ("The girl", "wanted"), ("The old sailor", "watched")]


def tid(tok, w):
    return tok(" " + w, add_special_tokens=False).input_ids[0]


def cap_hook(store, li):
    def hook(_m, _i, out):
        h = out[0] if isinstance(out, tuple) else out
        store[li] = h.detach().float().cpu().numpy()
    return hook


def add_hook_at(vec_t, pos):
    def hook(_m, _i, out):
        h = out[0] if isinstance(out, tuple) else out
        if 0 <= pos < h.shape[1]:
            h[0, pos, :] = h[0, pos, :] + vec_t.to(h.dtype)
        return out
    return hook


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--layer", type=int, default=9)          # install layer
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--swap-layers", type=int, nargs="+", default=[15, 18, 20])
    ap.add_argument("--dtype", default="bfloat16", choices=["float32", "bfloat16"])
    ap.add_argument("--device", default="mps")
    ap.add_argument("--mode", default="full", choices=["ceiling", "full"])
    ap.add_argument("--out", default="results/ffn-bake/operand-multihop-qwen3-4b")
    args = ap.parse_args()

    L = args.layer
    dev = (args.device if (args.device != "mps" or torch.backends.mps.is_available())
           else "cpu")
    rng = np.random.default_rng(0)
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    dec = model.model.layers
    cover_ids = {lb: tid(tok, lb) for lb in COVER_LABELS}
    class_ids = {c: tid(tok, c) for c in CLASSES}          # bridge tokens
    nonce_last = tok(" " + NONCE, add_special_tokens=False).input_ids[-1]
    print(f"[multihop] {args.model_id} L={L} scale={args.scale} dev={dev} n={NONCE!r} "
          f"mode={args.mode}")

    def find_slot(ids_list):
        idx = [i for i, t in enumerate(ids_list) if t == nonce_last]
        return idx[-1] if idx else len(ids_list) - 1

    def cover_pred(word, adds=None):
        """predict covering for 'A {word} is covered in __'. adds=[(layer,vec),...]."""
        preds = []
        for pfx in COVER_PREFIXES:
            prompt = pfx + COVER_QUERY.format(x=word)
            ids = tok(prompt, return_tensors="pt").to(dev)
            slot = find_slot(ids.input_ids[0].tolist())
            handles = []
            for (li, vec) in (adds or []):
                vt = torch.tensor(vec, dtype=torch.float32, device=dev)
                handles.append(dec[li].register_forward_hook(add_hook_at(vt, slot)))
            with torch.no_grad():
                lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
            for hd in handles:
                hd.remove()
            preds.append(max(COVER_LABELS, key=lambda lb: lo[cover_ids[lb]]))
        return max(COVER_LABELS, key=lambda lb: sum(p == lb for p in preds))

    # ── real-word ceiling: does the model know the real class covering? ───────────
    ceiling = {e: int(cover_pred(e) == COVER[ENT_CLASS[e]]) for e in ENTS}
    ceil_by_class = {c: round(float(np.mean([ceiling[e] for e in CLASS_ENT[c]])), 3)
                     for c in CLASSES}
    ceil_rate = round(float(np.mean(list(ceiling.values()))), 3)
    print(f"[multihop] ceiling overall={ceil_rate}  per-class={ceil_by_class}")
    print(f"[multihop] ceiling per-entity="
          f"{ {e: ceiling[e] for e in ENTS} }")
    valid = [e for e in ENTS if ceiling[e]]
    if args.mode == "ceiling":
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "ceiling.json").write_text(json.dumps(
            {"ceiling_rate": ceil_rate, "per_class": ceil_by_class,
             "per_entity": ceiling}, indent=2))
        print(f"[multihop] ceiling mode: wrote {out}/ceiling.json")
        return

    # ── d_E per entity (full content) + d_class centroids (identity averaged out) ──
    def decl(fr, obj):
        s, v = fr
        return f"{s} {v} a {obj}."

    per_e = {e: [] for e in ENTS}
    for fr in FRAMES:
        for e in ENTS:
            store: dict[int, np.ndarray] = {}
            h = dec[L].register_forward_hook(cap_hook(store, L))
            ids = tok(decl(fr, e), return_tensors="pt").to(dev)
            with torch.no_grad():
                model(**ids)
            h.remove()
            per_e[e].append(store[L][0, -2, :])
    e_mean = {e: np.mean(per_e[e], axis=0) for e in ENTS}
    g_mean = np.mean([e_mean[e] for e in ENTS], axis=0)
    d_E = {e: e_mean[e] - g_mean for e in ENTS}
    d_class = {c: np.mean([d_E[e] for e in CLASS_ENT[c]], axis=0) for c in CLASSES}
    dim = g_mean.shape[0]

    def rand_vec(norm):
        v = rng.standard_normal(dim)
        return v / (np.linalg.norm(v) + 1e-9) * norm

    S = args.scale

    # ══ GATE 1 — BEHAVIORAL COMPOSITION ══════════════════════════════════════════
    def install_acc(use_rand=False, scale=S):
        hits, n, cells = 0, 0, {}
        for e in valid:
            dv = (rand_vec(np.linalg.norm(d_E[e]) * scale) if use_rand
                  else d_E[e] * scale)
            pred = cover_pred(NONCE, adds=[(L, dv)])
            ok = int(pred == COVER[ENT_CLASS[e]])
            cells[e] = {"pred": pred, "truth": COVER[ENT_CLASS[e]], "ok": ok}
            hits += ok
            n += 1
        return (hits / n if n else 0.0), cells, n

    g1_acc, g1_cells, g1_n = install_acc()
    g1_rand, _, _ = install_acc(use_rand=True)
    # baseline: bare nonce, no install
    base_hits = sum(int(cover_pred(NONCE) == COVER[ENT_CLASS[e]]) for e in valid)
    g1_base = base_hits / len(valid) if valid else 0.0
    print(f"\n[GATE1] install acc={g1_acc:.3f} (rand {g1_rand:.3f}, baseline "
          f"{g1_base:.3f}, n={g1_n})")

    # content-specificity: install E vs E' of DIFFERENT class -> covering follows class
    spec = []
    for e in valid:
        for ep in valid:
            if ENT_CLASS[e] == ENT_CLASS[ep]:
                continue
            pe = cover_pred(NONCE, adds=[(L, d_E[e] * S)])
            pep = cover_pred(NONCE, adds=[(L, d_E[ep] * S)])
            spec.append(int(pe == COVER[ENT_CLASS[e]] and pep == COVER[ENT_CLASS[ep]]))
    g1_spec = round(float(np.mean(spec)), 3) if spec else None
    print(f"[GATE1] content-specificity (both follow installed class)={g1_spec} "
          f"(n={len(spec)})")

    # ══ GATE 2b — CENTROID (individual-independence) ══════════════════════════════
    # install the class centroid on the nonce; covering should still resolve by class.
    cen_hits, cen_n, cen_cells = 0, 0, {}
    cen_rand_hits = 0
    for c in CLASSES:
        # only count classes with >=1 valid ceiling member (fair vs full-content acc)
        if not any(ceiling[e] for e in CLASS_ENT[c]):
            continue
        pred = cover_pred(NONCE, adds=[(L, d_class[c] * S)])
        ok = int(pred == COVER[c])
        cen_hits += ok
        cen_n += 1
        cen_cells[c] = {"pred": pred, "truth": COVER[c], "ok": ok}
        rpred = cover_pred(NONCE, adds=[(L, rand_vec(np.linalg.norm(d_class[c]) * S))])
        cen_rand_hits += int(rpred == COVER[c])
    g2b_acc = cen_hits / cen_n if cen_n else 0.0
    g2b_rand = cen_rand_hits / cen_n if cen_n else 0.0
    print(f"[GATE2b] centroid acc={g2b_acc:.3f} (rand {g2b_rand:.3f}, n={cen_n}) "
          f"cells={cen_cells}")

    # ══ GATE 2c — CAUSAL LATE BRIDGE-SWAP ════════════════════════════════════════
    # install E (class c) at L; ALSO add class-axis swap (d_class[c'] - d_class[c]) at a
    # LATE layer -> covering should flip to c'. random matched-norm late add must NOT.
    swap_results = {}
    for lb in args.swap_layers:
        flips, rand_flips, swn = [], [], 0
        for e in valid:
            c = ENT_CLASS[e]
            for cp in CLASSES:
                if cp == c:
                    continue
                swap = (d_class[cp] - d_class[c]) * S
                pred = cover_pred(NONCE, adds=[(L, d_E[e] * S), (lb, swap)])
                flips.append(int(pred == COVER[cp]))         # follows swapped class
                rnd = rand_vec(np.linalg.norm(swap))
                rpred = cover_pred(NONCE, adds=[(L, d_E[e] * S), (lb, rnd)])
                rand_flips.append(int(rpred == COVER[cp]))
                swn += 1
        swap_results[str(lb)] = {
            "flip_to_swapped": round(float(np.mean(flips)), 3),
            "random_late_flip": round(float(np.mean(rand_flips)), 3), "n": swn}
        sr = swap_results[str(lb)]
        print(f"[GATE2c] L_b={lb}: flip_to_swapped={sr['flip_to_swapped']} "
              f"(random {sr['random_late_flip']}, n={swn})")
    best_swap = max(swap_results.values(), key=lambda r: r["flip_to_swapped"])

    # ══ GATE 2a — DEPTH ORDER (logit-lens: class token peaks before covering) ══════
    norm_f = model.model.norm
    unembed = model.lm_head

    def logit_lens_peaks(word, dv):
        """per-layer margin of class vs covering tokens at readout (installed nonce)."""
        pfx = COVER_PREFIXES[0]
        prompt = pfx + COVER_QUERY.format(x=word)
        ids = tok(prompt, return_tensors="pt").to(dev)
        slot = find_slot(ids.input_ids[0].tolist())
        vt = torch.tensor(dv, dtype=torch.float32, device=dev)
        hd = dec[L].register_forward_hook(add_hook_at(vt, slot))
        with torch.no_grad():
            out = model(**ids, output_hidden_states=True)
        hd.remove()
        hs = out.hidden_states                      # tuple len n_layers+1, [1,T,d]
        cls_marg, cov_marg = [], []
        for h in hs:
            last = h[0, -1, :]
            with torch.no_grad():
                lg = unembed(norm_f(last.unsqueeze(0))).float().cpu().numpy()[0]
            cls_marg.append([lg[class_ids[c]] for c in CLASSES])
            cov_marg.append([lg[cover_ids[COVER[c]]] for c in CLASSES])
        return np.array(cls_marg), np.array(cov_marg)   # [n_layer+1, 3]

    bridge_peaks, prop_peaks, shuf_bridge, shuf_prop = [], [], [], []
    for e in valid:
        c = ENT_CLASS[e]
        ci = CLASSES.index(c)
        cls_m, cov_m = logit_lens_peaks(NONCE, d_E[e] * S)
        # margin for the TRUE class = target - max(others)
        def marg(arr, i):
            others = [arr[:, j] for j in range(3) if j != i]
            return arr[:, i] - np.max(others, axis=0)
        bp = int(np.argmax(marg(cls_m, ci)))
        pp = int(np.argmax(marg(cov_m, ci)))
        bridge_peaks.append(bp)
        prop_peaks.append(pp)
        # shuffled-label control: swap which array is bridge vs property
        shuf_bridge.append(int(np.argmax(marg(cov_m, ci))))
        shuf_prop.append(int(np.argmax(marg(cls_m, ci))))
    med_b = float(np.median(bridge_peaks))
    med_p = float(np.median(prop_peaks))
    gap = med_p - med_b                               # positive = bridge earlier
    shuf_gap = float(np.median(shuf_prop)) - float(np.median(shuf_bridge))
    print(f"[GATE2a] median bridge-peak L={med_b} property-peak L={med_p} "
          f"gap={gap:+.1f} (shuffled gap={shuf_gap:+.1f})")

    # ══ VERDICT (pre-registered, frozen) ═════════════════════════════════════════
    gate1 = bool(g1_acc > 0.66 and g1_acc > g1_rand + 0.20
                 and g1_acc > g1_base + 0.20 and (g1_spec or 0) > 0.5)
    g2a = bool(gap > 0 and gap > shuf_gap)
    g2b = bool(g2b_acc >= 0.66 * g1_acc and g2b_acc > g2b_rand + 0.20)
    g2c = bool(best_swap["flip_to_swapped"] >= 0.66
               and best_swap["random_late_flip"] < 0.34)
    n_g2 = sum([g2a, g2b, g2c])
    verdict = bool(gate1 and n_g2 >= 2)
    print(f"\n[VERDICT] Gate1={gate1} | 2a={g2a} 2b={g2b} 2c={g2c} (n_gate2={n_g2})")
    print(f"[VERDICT] MULTI-HOP SUPPORTED = {verdict}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    res = {"model": args.model_id, "device": dev, "layer": L, "scale": S,
           "nonce": NONCE, "class_ent": CLASS_ENT, "cover": COVER,
           "ceiling_rate": ceil_rate, "ceiling_per_class": ceil_by_class,
           "ceiling_per_entity": ceiling,
           "gate1": {"install_acc": round(g1_acc, 3), "random": round(g1_rand, 3),
                     "baseline": round(g1_base, 3), "content_specificity": g1_spec,
                     "n": g1_n, "cells": g1_cells, "pass": gate1},
           "gate2a_depth": {"median_bridge_peak": med_b, "median_property_peak": med_p,
                            "gap": round(gap, 2), "shuffled_gap": round(shuf_gap, 2),
                            "bridge_peaks": bridge_peaks, "property_peaks": prop_peaks,
                            "pass": g2a},
           "gate2b_centroid": {"acc": round(g2b_acc, 3), "random": round(g2b_rand, 3),
                               "n": cen_n, "cells": cen_cells, "pass": g2b},
           "gate2c_bridge_swap": {"by_layer": swap_results, "best": best_swap,
                                  "pass": g2c},
           "verdict": {"gate1": gate1, "gate2a": g2a, "gate2b": g2b, "gate2c": g2c,
                       "n_gate2": n_g2, "MULTI_HOP_SUPPORTED": verdict}}
    (out / "operand_multihop.json").write_text(json.dumps(res, indent=2))
    print(f"[multihop] wrote {out}/operand_multihop.json")


if __name__ == "__main__":
    main()
