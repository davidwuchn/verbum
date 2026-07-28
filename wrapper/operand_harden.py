"""FFN-function bake — STAGE 0 (d): HARDEN the operand-write result.

operand_write.py showed the operand row is causally writeable on a RECALL (copy)
readout. (d) bulletproofs it against two over-claim risks before the bake:

  1. DOSE-RESPONSE — a genuine load-bearing rewrite should be GRADED: flip-rate/margin
     rise monotonically with the injected dose alpha. An all-or-nothing or flat response
     would suggest a threshold artifact, not the join reading the operand content.
  2. COMPOSED (not copied) readout — recall could be pure copy. Here the operand must be
     TRANSFORMED: a few-shot CATEGORY map (operand -> its category: dog->animal,
     car->vehicle, rose->plant). The output token is NOT the operand; it is a semantic
     function of it. If steering A->B flips category(A)->category(B), the operand row is
     used in COMPUTATION, not just relayed.

Extra robustness: the steering direction d(A->B) is built from the OBJECT position in a
DECLARATIVE ("<frame> a <obj>.") and injected into the CATEGORY task — a cross-task
transfer. A direction learned in one context that rewrites the composed output in
another is operand CONTENT, not a task-local logit trick.

Frame-invariance (s275) licenses the HF write on Qwen3-0.6B. `λ measure` register =
VALUE (the operand row); readout = 3-way category logits. Null = matched-random
direction at the same norm, per dose.

VERDICT: HARDENED-WRITEABLE <=> composed flip(A->B) >> random at matched dose,
  B-specific (raises category(B) over the bystander), AND monotone dose-response.

License: MIT.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def obj_token_id(tok, obj):
    return tok(" " + obj, add_special_tokens=False).input_ids[0]


def resid_hook_capture(store, layer_idx):
    def hook(_m, _i, out):
        h = out[0] if isinstance(out, tuple) else out
        store[layer_idx] = h.detach().float().cpu().numpy()
    return hook


def resid_hook_add(vec_t):
    def hook(_m, _i, out):
        if isinstance(out, tuple):
            out[0][:] = out[0] + vec_t.to(out[0].dtype)
            return out
        return out + vec_t.to(out.dtype)
    return hook

# cross-category operands (6 each); interleaved so cyclic next is a DIFFERENT category
CATS = {
    "animal": ["dog", "cat", "horse", "cow", "wolf", "sheep"],
    "vehicle": ["car", "truck", "train", "boat", "jet", "bus"],
    "plant": ["rose", "oak", "fern", "pine", "palm", "vine"],
}
ORDER = []  # dog,car,rose,cat,truck,oak,... -> A,B,C always span the 3 categories
for i in range(6):
    ORDER += [CATS["animal"][i], CATS["vehicle"][i], CATS["plant"][i]]
OP2CAT = {o: c for c, os in CATS.items() for o in os}

FRAMES = [
    ("The farmer", "saw"), ("The child", "drew"), ("The hunter", "tracked"),
    ("A woman", "bought"), ("The boy", "chased"), ("A man", "found"),
    ("The girl", "wanted"), ("The old sailor", "watched"),
]
PREFIX = "dog: animal\ncar: vehicle\nrose: plant\n"   # few-shot category map
ALPHAS = [0.0, 0.25, 0.5, 1.0, 1.5, 2.0]


def decl(frame, obj):
    s, v = frame
    return f"{s} {v} a {obj}."


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--layers", default="7,13,20")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--out", default="results/ffn-bake/operand-harden-qwen3-0-6b")
    args = ap.parse_args()

    layers = [int(x) for x in args.layers.split(",")]
    dev = (args.device if (args.device != "mps" or torch.backends.mps.is_available())
           else "cpu")
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=torch.float32).to(dev).eval()
    dec = model.model.layers
    cat_ids = {c: obj_token_id(tok, c) for c in CATS}

    # ── direction source: object-token residual in DECLARATIVES (cross-task) ──
    means = {li: {o: [] for o in ORDER} for li in layers}
    for fr in FRAMES:
        for o in ORDER:
            store: dict[int, np.ndarray] = {}
            hs = [dec[li].register_forward_hook(resid_hook_capture(store, li))
                  for li in layers]
            ids = tok(decl(fr, o), return_tensors="pt").to(dev)
            with torch.no_grad():
                model(**ids)
            for h in hs:
                h.remove()
            for li in layers:
                means[li][o].append(store[li][0, -2, :])   # object token
    mean_op = {li: {o: np.mean(means[li][o], axis=0) for o in ORDER} for li in layers}

    # pairs: A -> B (next, different category), bystander C (third category)
    triples = [(ORDER[i], ORDER[(i + 1) % len(ORDER)], ORDER[(i + 2) % len(ORDER)])
               for i in range(len(ORDER))]
    rng = np.random.default_rng(0)

    def cat_logits(obj, hook_layer=None, add_vec=None):
        handle = None
        if hook_layer is not None:
            vt = torch.tensor(add_vec, dtype=torch.float32, device=dev)
            handle = dec[hook_layer].register_forward_hook(resid_hook_add(vt))
        ids = tok(PREFIX + obj + ":", return_tensors="pt").to(dev)
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        if handle:
            handle.remove()
        return {c: float(lo[cat_ids[c]]) for c in CATS}

    # clean composed accuracy gate
    clean_hits = sum(max(cat_logits(o), key=cat_logits(o).get) == OP2CAT[o]
                     for o in ORDER)
    clean_acc = clean_hits / len(ORDER)
    print(f"[harden] composed(category) clean acc = {clean_acc:.3f} "
          f"({clean_hits}/{len(ORDER)})  layers={layers}  device={dev}")

    # ── dose-response on the COMPOSED task ──
    results = {}
    for li in layers:
        print(f"\n L{li}: alpha | flip real | flip rand | margin(B-A) real | "
              f"B-spec(B-C)")
        print("       -------+-----------+-----------+------------------+-----------")
        rows = []
        for a in ALPHAS:
            flips, flips_r, margins, bspec = 0, 0, [], []
            for (A, B, C) in triples:
                fA, fB, fC = OP2CAT[A], OP2CAT[B], OP2CAT[C]
                d = (mean_op[li][B] - mean_op[li][A]) * a
                rv = rng.standard_normal(d.shape)
                rv = rv / (np.linalg.norm(rv) + 1e-9) * (np.linalg.norm(d) + 1e-12)
                base = cat_logits(A)
                pr = cat_logits(A, hook_layer=li, add_vec=d)
                pr_r = cat_logits(A, hook_layer=li, add_vec=rv)
                if max(pr, key=pr.get) == fB:
                    flips += 1
                if max(pr_r, key=pr_r.get) == fB:
                    flips_r += 1
                margins.append((pr[fB] - pr[fA]) - (base[fB] - base[fA]))
                bspec.append((pr[fB] - base[fB]) - (pr[fC] - base[fC]))
            n = len(triples)
            row = {"alpha": a, "flip_real": round(flips / n, 3),
                   "flip_rand": round(flips_r / n, 3),
                   "margin_real": round(float(np.mean(margins)), 3),
                   "b_specificity": round(float(np.mean(bspec)), 3)}
            rows.append(row)
            print(f"       {a:5.2f} | {row['flip_real']:.3f}     | "
                  f"{row['flip_rand']:.3f}     | {row['margin_real']:16.3f} | "
                  f"{row['b_specificity']:.3f}")
        results[li] = rows

    # verdict: graded dose-response (monotone RISE to a >=0.9 peak; saturation
    # beyond allowed -- flip cannot exceed 1.0) + composed flip >> random + B-specific.
    def rising(vals):
        peak = max(range(len(vals)), key=lambda i: vals[i])  # first argmax
        prefix_mono = all(vals[i + 1] >= vals[i] - 1e-6 for i in range(peak))
        return vals[0] < 0.1 and prefix_mono and vals[peak] >= 0.9
    best = {li: max(rows, key=lambda r: r["flip_real"])
            for li, rows in results.items()}
    dose_ok = any(rising([r["flip_real"] for r in rows])
                  for rows in results.values())
    sep_ok = all(b["flip_real"] > b["flip_rand"] + 0.2 and b["b_specificity"] > 0
                 for b in best.values())
    verdict = ("HARDENED-WRITEABLE (composed rewrite, dose-responsive, B-specific)"
               if (dose_ok and sep_ok) else
               "NOT-HARDENED (weak / not dose-responsive / not B-specific)")
    print(f"\n[harden] VERDICT: {verdict}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    res = {"model": args.model_id, "device": dev,
           "readout": "few-shot category (composed)",
           "clean_acc": round(clean_acc, 3), "alphas": ALPHAS, "layers": layers,
           "verdict": verdict,
           "per_layer": {str(li): rows for li, rows in results.items()}}
    (out / "operand_harden.json").write_text(json.dumps(res, indent=2))
    print(f"[harden] wrote {out}/operand_harden.json")


if __name__ == "__main__":
    main()
