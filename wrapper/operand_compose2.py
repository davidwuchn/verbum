"""(h) Arm-2 — NOVEL COMPOSITION: computed-not-stored via a 2-operand relational.

Pre-registration: general-composition-prereg.md (Arm 2). Arm 1 showed an installed row
is a reusable term (composes under multiple resident functions). Arm 2 asks the sharper
question: does the resident routing COMBINE the installed operand with a GIVEN second
operand into a COMPUTED result that is neither the operand nor a stored tag?

Design: install entity E's content d_E on a fixed nonce; ask a 2-operand comparison
"Compared to a {Y}, a {nonce} is [bigger/smaller]" with Y VARIED over a size ladder.
The decisive computed signature: for a FIXED installed E, the answer must FLIP correctly
across Y (bigger when Y < E, smaller when Y > E), crossing at E's true size. A stored
size TAG would give a CONSTANT answer regardless of Y; only a resident comparison that
combines installed-E-size with the given Y-size flips correctly. Content-specific + the
flip-with-Y is the "computed, not stored" proof.

`λ measure`: operand = VALUE (d_E); the comparison = ROUTING; readout = logits.
`λ yardstick`: nulls beside every number (random install, baseline, constant-tag check);
real-word ceiling gates each cell. 4B (0.6B too weak). A RUNG, not the claim.

License: MIT (`λ provenance`).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# install entities with a size RANK (bigger rank = physically larger); model-known sizes
ENT_RANK = {"ant": 1, "rabbit": 3, "eagle": 4, "wolf": 5,
            "horse": 7, "shark": 8, "elephant": 9, "whale": 10}
# reference second-operands Y with ranks on the same scale (held-out from install set)
Y_REF = {"mouse": 2, "cat": 3, "dog": 4, "pig": 5, "cow": 7, "whale": 10}
ENTS = list(ENT_RANK)
NONCE = "zorp"
LABELS = ["bigger", "smaller"]
# held-out few-shot exemplars (words disjoint from ENT_RANK and Y_REF)
PREFIXES = [
    "Compared to a duck, a bear is bigger.\nCompared to a bear, a snail is smaller.\n",
    "Compared to a rat, a lion is bigger.\nCompared to a lion, a moth is smaller.\n",
]
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
    ap.add_argument("--layer", type=int, default=9)
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--dtype", default="bfloat16", choices=["float32", "bfloat16"])
    ap.add_argument("--device", default="mps")
    ap.add_argument("--out", default="results/ffn-bake/operand-compose2-qwen3-4b")
    args = ap.parse_args()

    L = args.layer
    dev = (args.device if (args.device != "mps" or torch.backends.mps.is_available())
           else "cpu")
    rng = np.random.default_rng(0)
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    dec = model.model.layers
    lab_ids = {lb: tid(tok, lb) for lb in LABELS}
    nonce_last = tok(" " + NONCE, add_special_tokens=False).input_ids[-1]
    print(f"[compose2] {args.model_id} L={L} scale={args.scale} dev={dev} n={NONCE!r}")

    # ── d_E per entity from declaratives (full content) ──────────────────────────
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
    dim = g_mean.shape[0]

    def find_slot(ids_list):
        idx = [i for i, t in enumerate(ids_list) if t == nonce_last]
        return idx[-1] if idx else len(ids_list) - 1

    def cmp_pred(word, yref, add_vec=None):
        """predict bigger/smaller for 'compared to a {yref}, a {word} is __'."""
        preds = []
        for pfx in PREFIXES:
            prompt = f"{pfx}Compared to a {yref}, a {word} is"
            ids = tok(prompt, return_tensors="pt").to(dev)
            handle = None
            if add_vec is not None:
                slot = find_slot(ids.input_ids[0].tolist())
                vt = torch.tensor(add_vec, dtype=torch.float32, device=dev)
                handle = dec[L].register_forward_hook(add_hook_at(vt, slot))
            with torch.no_grad():
                lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
            if handle:
                handle.remove()
            preds.append(max(LABELS, key=lambda lb: lo[lab_ids[lb]]))
        return max(LABELS, key=lambda lb: sum(p == lb for p in preds))

    def truth(erank, yrank):
        return "bigger" if erank > yrank else "smaller"

    def rand_vec(norm):
        v = rng.standard_normal(dim)
        return v / (np.linalg.norm(v) + 1e-9) * norm

    # cells: (E, Y) with distinct ranks (skip ties). truth by rank comparison.
    cells = [(e, y) for e in ENTS for y in Y_REF if ENT_RANK[e] != Y_REF[y]]

    # ── real-word ceiling: does the model compare the REAL word correctly? ────────
    ceil = {}
    for e, y in cells:
        ceil[(e, y)] = int(cmp_pred(e, y) == truth(ENT_RANK[e], Y_REF[y]))
    ceil_by_e = {e: np.mean([ceil[(e, y)] for y in Y_REF if (e, y) in ceil])
                 for e in ENTS}
    ceil_rate = float(np.mean(list(ceil.values())))
    print(f"[compose2] real-word ceiling overall={ceil_rate:.3f}  per-E="
          f"{ {e: round(v, 2) for e, v in ceil_by_e.items()} }")

    # ── install E on nonce; accuracy + the FLIP signature across Y ────────────────
    def run(scale, use_rand=False):
        hits, n = 0, 0
        per_e_seq = {}      # E -> list of (yrank, pred, truth) over ceiling-valid cells
        for e in ENTS:
            dv = (rand_vec(np.linalg.norm(d_E[e]) * scale) if use_rand
                  else d_E[e] * scale)
            seq = []
            for y in Y_REF:
                if (e, y) not in ceil or not ceil[(e, y)]:
                    continue      # void where the real word itself failed
                pred = cmp_pred(NONCE, y, add_vec=dv)
                tr = truth(ENT_RANK[e], Y_REF[y])
                hits += int(pred == tr)
                n += 1
                seq.append((Y_REF[y], pred, tr))
            per_e_seq[e] = seq
        acc = hits / n if n else 0.0
        # FLIP signature: fraction of E whose predicted labels VARY across Y AND whose
        # accuracy over its Y-ladder is high (a constant-tag would not vary correctly).
        flips, varied = [], []
        for seq in per_e_seq.values():
            if len(seq) < 2:
                continue
            preds = [p for _, p, _ in seq]
            trs = [t for _, _, t in seq]
            has_both_truth = len(set(trs)) > 1     # E's ladder actually crosses
            varied.append(int(len(set(preds)) > 1))
            if has_both_truth:
                ok = [p == t for p, t in zip(preds, trs, strict=False)]
                flips.append(float(np.mean(ok)))
        return {"acc": round(acc, 3), "n": n,
                "flip_correct": round(float(np.mean(flips)), 3) if flips else None,
                "frac_varied": round(float(np.mean(varied)), 3) if varied else None,
                "per_e_seq": {e: [[r, p, t] for r, p, t in s]
                              for e, s in per_e_seq.items()}}

    install = run(args.scale)
    randomn = run(args.scale, use_rand=True)
    baseline = {"acc": None}
    # baseline: bare nonce, no install
    bh, bn = 0, 0
    for e, y in cells:
        if not ceil.get((e, y)):
            continue
        bh += int(cmp_pred(NONCE, y) == truth(ENT_RANK[e], Y_REF[y]))
        bn += 1
    baseline = {"acc": round(bh / bn, 3) if bn else None, "n": bn}

    print(f"\n  install : acc={install['acc']} flip_correct={install['flip_correct']} "
          f"frac_varied={install['frac_varied']} (n={install['n']})")
    print(f"  random  : acc={randomn['acc']} flip_correct={randomn['flip_correct']} "
          f"frac_varied={randomn['frac_varied']}")
    print(f"  baseline: acc={baseline['acc']} (bare nonce, n={baseline['n']})")

    # ── content-specificity: install E vs E' (diff rank), a Y between them ─────────
    spec = []
    for e in ENTS:
        for ep in ENTS:
            if ENT_RANK[e] <= ENT_RANK[ep]:
                continue
            for y in Y_REF:
                if not (ENT_RANK[ep] < Y_REF[y] < ENT_RANK[e]):
                    continue      # Y brackets: E bigger than Y, E' smaller than Y
                if not (ceil.get((e, y)) and ceil.get((ep, y))):
                    continue
                pe = cmp_pred(NONCE, y, add_vec=d_E[e] * args.scale)
                pep = cmp_pred(NONCE, y, add_vec=d_E[ep] * args.scale)
                spec.append(int(pe == "bigger" and pep == "smaller"))
    content_spec = round(float(np.mean(spec)), 3) if spec else None
    print(f"[compose2] content-specificity (bracketing Y flips by install): "
          f"{content_spec} (n={len(spec)})")

    # ── verdict (pre-registered) ──────────────────────────────────────────────────
    novel = bool(install["acc"] and install["acc"] > 0.66
                 and install["acc"] > (randomn["acc"] or 0) + 0.15
                 and install["acc"] > (baseline["acc"] or 0) + 0.15
                 and (install["flip_correct"] or 0) > 0.66
                 and (content_spec or 0) > 0.5)
    print(f"\n[compose2] VERDICT NOVEL_COMPOSITION (computed-not-stored) = {novel}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    res = {"model": args.model_id, "device": dev, "layer": L, "scale": args.scale,
           "nonce": NONCE, "ent_rank": ENT_RANK, "y_ref": Y_REF,
           "ceiling_rate": round(ceil_rate, 3),
           "ceiling_per_e": {e: round(v, 3) for e, v in ceil_by_e.items()},
           "install": install, "random": randomn, "baseline": baseline,
           "content_specificity": content_spec, "verdict_novel": novel}
    (out / "operand_compose2.json").write_text(json.dumps(res, indent=2))
    print(f"[compose2] wrote {out}/operand_compose2.json")


if __name__ == "__main__":
    main()
