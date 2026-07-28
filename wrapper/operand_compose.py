"""(h) GENERAL-COMPOSITION gate — is an installed operand a REUSABLE TERM?

Pre-registration: mementum/knowledge/explore/general-composition-prereg.md.
The load-bearing IOU (s273 K-battery arm b). s277 installed a novel operand the resident
join CATEGORIZED (one fixed transform ~ a memorized tag). This asks the harder question:
does the RESIDENT routing compose an installed operand under MULTIPLE distinct resident
functions (Arm 1, reusable term) and into a NOVEL relational result (Arm 2)?

Setup: install a real entity E's FULL content d_E (object-token residual diff-of-means,
built cross-task in declaratives) onto a fixed nonce carrier via the keyed residual
write hook (add scale*d_E at the nonce slot at layer L~7). Test the nonce across the
resident functions on HELD-OUT few-shot prefixes (exemplars disjoint from test entity).

`λ measure`: operand = VALUE register (d_E); the resident functions = ROUTING; readout
= logits. `λ yardstick`: nulls beside every number. The decisive discriminator = a
WRONG-CONTENT install must flip ALL functions (a memorized tag cannot). The real-word
ceiling gates each cell (cannot test composition where the model lacks the real answer).
0.6B = a RUNG, not the claim.

License: MIT (`λ provenance`; SuperBake method-reference only).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# entity → resident-function ground truth. BALANCED set (s278 rerun): 10 fliers + 10
# aquatic animals, ~50/50 on fly / water / size, so the random-install null → chance.
# `cat` dropped (all animals now): the reusable-term test uses only CATEGORY-ORTHOGONAL
# functions (can-fly / lives-in-water / size) — stronger than re-showing category-swap.
ENT = {
    # fliers (fly=yes, water=no) — 5 bigger, 5 smaller than a mouse
    "eagle": {"fly": "yes", "water": "no", "size": "bigger"},
    "hawk": {"fly": "yes", "water": "no", "size": "bigger"},
    "owl": {"fly": "yes", "water": "no", "size": "bigger"},
    "goose": {"fly": "yes", "water": "no", "size": "bigger"},
    "crow": {"fly": "yes", "water": "no", "size": "bigger"},
    "bee": {"fly": "yes", "water": "no", "size": "smaller"},
    "moth": {"fly": "yes", "water": "no", "size": "smaller"},
    "dragonfly": {"fly": "yes", "water": "no", "size": "smaller"},
    "wasp": {"fly": "yes", "water": "no", "size": "smaller"},
    "butterfly": {"fly": "yes", "water": "no", "size": "smaller"},
    # aquatic (fly=no, water=yes) — 5 bigger, 5 smaller
    "salmon": {"fly": "no", "water": "yes", "size": "bigger"},
    "shark": {"fly": "no", "water": "yes", "size": "bigger"},
    "whale": {"fly": "no", "water": "yes", "size": "bigger"},
    "dolphin": {"fly": "no", "water": "yes", "size": "bigger"},
    "tuna": {"fly": "no", "water": "yes", "size": "bigger"},
    "frog": {"fly": "no", "water": "yes", "size": "smaller"},
    "crab": {"fly": "no", "water": "yes", "size": "smaller"},
    "shrimp": {"fly": "no", "water": "yes", "size": "smaller"},
    "minnow": {"fly": "no", "water": "yes", "size": "smaller"},
    "seahorse": {"fly": "no", "water": "yes", "size": "smaller"},
}
ENTS = list(ENT)
NONCE = "zorp"

# resident functions: held-out few-shot prefixes (exemplars disjoint from ENT test set),
# a query template with {x}, and the label vocabulary (read the next token).
FUNCS = {
    "fly": {
        "labels": ["yes", "no"],
        "prefixes": ["Can a bird fly? yes\nCan a dog fly? no\n",
                     "Can a bee fly? yes\nCan a pig fly? no\n"],
        "query": "Can a {x} fly?",
    },
    "water": {
        "labels": ["yes", "no"],
        "prefixes": ["Does a fish live in water? yes\nDoes a dog live in water? no\n",
                     "Does a crab live in water? yes\nDoes a cat live in water? no\n"],
        "query": "Does a {x} live in water?",
    },
    "size": {   # Arm 2 — relational (bigger/smaller than a mouse)
        "labels": ["bigger", "smaller"],
        "prefixes": [
            "A horse is bigger than a mouse.\nA flea is smaller than a mouse.\n",
            "A cow is bigger than a mouse.\nA gnat is smaller than a mouse.\n"],
        "query": "A {x} is",
    },
}
ARM1 = ["fly", "water", "size"]   # three category-orthogonal balanced functions
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
    ap.add_argument("--model-id", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--layer", type=int, default=7)
    ap.add_argument("--scales", type=float, nargs="+", default=[2.0, 4.0])
    ap.add_argument("--dtype", default="float32", choices=["float32", "bfloat16"])
    ap.add_argument("--device", default="mps")
    ap.add_argument("--out", default="results/ffn-bake/operand-compose-qwen3-0-6b")
    args = ap.parse_args()

    L = args.layer
    dev = (args.device if (args.device != "mps" or torch.backends.mps.is_available())
           else "cpu")
    rng = np.random.default_rng(0)
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    dec = model.model.layers
    lab_ids = {f: {lb: tid(tok, lb) for lb in FUNCS[f]["labels"]} for f in FUNCS}
    nonce_last = tok(" " + NONCE, add_special_tokens=False).input_ids[-1]
    print(f"[compose] {args.model_id} L={L} dev={dev} nonce={NONCE!r} entities={ENTS}")

    # ── d_E: full-content direction per entity from declaratives ──────────────────
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

    def predict(func, word, add_vec=None):
        """predict the label for `word` under resident function `func`."""
        spec = FUNCS[func]
        preds = []
        for pfx in spec["prefixes"]:
            prompt = pfx + spec["query"].format(x=word)
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
            preds.append(max(spec["labels"], key=lambda lb: lo[lab_ids[func][lb]]))
        # majority over held-out prefixes
        return max(spec["labels"], key=lambda lb: sum(p == lb for p in preds))

    def rand_vec(norm):
        v = rng.standard_normal(dim)
        return v / (np.linalg.norm(v) + 1e-9) * norm

    # ── real-word ceiling: does the model know the real answers? (gates each cell) ──
    ceiling = {f: {} for f in FUNCS}
    for e in ENTS:
        for f in FUNCS:
            ceiling[f][e] = int(predict(f, e) == ENT[e][f])
    ceil_rate = {f: round(float(np.mean(list(ceiling[f].values()))), 3) for f in FUNCS}
    print(f"[compose] real-word ceiling (per func): {ceil_rate}")

    # ── install E's content on the nonce; test each function (scale sweep) ─────────
    def install_acc(scale, funcs, use_rand=False):
        """mean composed accuracy over entity-func cells where ceiling held."""
        hits, n = 0, 0
        per_cell = {}
        for e in ENTS:
            dnorm = np.linalg.norm(d_E[e]) * scale
            dv = rand_vec(dnorm) if use_rand else d_E[e] * scale
            for f in funcs:
                if not ceiling[f][e]:
                    continue          # void: model doesn't know real answer
                pred = predict(f, NONCE, add_vec=dv)
                ok = int(pred == ENT[e][f])
                per_cell[f"{e}/{f}"] = {"pred": pred, "truth": ENT[e][f], "ok": ok}
                hits += ok
                n += 1
        return (hits / n if n else 0.0), per_cell, n

    baseline_acc, _, _ = install_acc(0.0, list(FUNCS))     # scale 0 = no add (baseline)
    results = {"scales": {}}
    for s in args.scales:
        a1, cells1, n1 = install_acc(s, ARM1)
        a2, cells2, n2 = install_acc(s, ["size"])
        ar1, _, _ = install_acc(s, ARM1, use_rand=True)
        ar2, _, _ = install_acc(s, ["size"], use_rand=True)
        results["scales"][f"{s}"] = {
            "arm1_reusable_acc": round(a1, 3), "arm1_random_null": round(ar1, 3),
            "arm1_n": n1, "arm2_size_acc": round(a2, 3),
            "arm2_random_null": round(ar2, 3),
            "arm2_n": n2, "arm1_cells": cells1, "arm2_cells": cells2}
        print(f"  scale {s}: ARM1 reusable={a1:.3f} (rand {ar1:.3f}, n={n1})  "
              f"ARM2 size={a2:.3f} (rand {ar2:.3f}, n={n2})")

    best_s = max(args.scales,
                 key=lambda s: results["scales"][f"{s}"]["arm1_reusable_acc"])
    best = results["scales"][f"{best_s}"]

    # ── content-specificity (decisive): wrong-content install flips ALL functions ──
    # for each ordered pair (E,E') differing on function f (both ceilings hold), install
    # E vs E' on the nonce and check the answer FOLLOWS the installed content.
    flip_by_func = {}
    for f in FUNCS:
        flips = []
        for e in ENTS:
            for ep in ENTS:
                if e == ep or ENT[e][f] == ENT[ep][f]:
                    continue
                if not (ceiling[f][e] and ceiling[f][ep]):
                    continue
                pe = predict(f, NONCE, add_vec=d_E[e] * best_s)
                pep = predict(f, NONCE, add_vec=d_E[ep] * best_s)
                flips.append(int(pe == ENT[e][f] and pep == ENT[ep][f]))
        flip_by_func[f] = round(float(np.mean(flips)), 3) if flips else None
    print(f"[compose] content-specificity (both follow install): {flip_by_func}")

    # ── verdicts (pre-registered) ─────────────────────────────────────────────────
    arm1_specific = np.mean([flip_by_func[f] for f in ARM1
                             if flip_by_func[f] is not None])
    reusable = (best["arm1_reusable_acc"] > 0.66
                and best["arm1_reusable_acc"] > best["arm1_random_null"] + 0.34
                and best["arm1_reusable_acc"] > baseline_acc + 0.20
                and arm1_specific > 0.5)
    novel = (best["arm2_size_acc"] > 0.66
             and best["arm2_size_acc"] > best["arm2_random_null"] + 0.34
             and (flip_by_func["size"] or 0) > 0.5)
    verdicts = {
        "REUSABLE_TERM": bool(reusable),
        "NOVEL_COMPOSITION": bool(novel),
        "arm1_content_specificity": round(float(arm1_specific), 3),
        "baseline_acc": round(baseline_acc, 3), "best_scale": best_s}
    print(f"\n[compose] baseline={baseline_acc:.3f}  best_scale={best_s}")
    print(f"[compose] Arm1 reusable-term specificity={arm1_specific:.3f}")
    print(f"[compose] VERDICTS: REUSABLE_TERM={reusable}  NOVEL_COMPOSITION={novel}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    res = {"model": args.model_id, "device": dev, "layer": L, "nonce": NONCE,
           "entities": ENT, "ceiling_rate": ceil_rate, "ceiling": ceiling,
           "baseline_acc": round(baseline_acc, 3), "content_specificity": flip_by_func,
           "results": results, "verdicts": verdicts}
    (out / "operand_compose.json").write_text(json.dumps(res, indent=2))
    print(f"[compose] wrote {out}/operand_compose.json")


if __name__ == "__main__":
    main()
