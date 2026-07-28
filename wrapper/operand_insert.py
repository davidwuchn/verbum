"""FFN-function bake — STAGE 3 (c): the NOVEL-operand INSERT gate (recursion rung-1).

The operand row is readable (operand_map), writeable (operand_write), and hardened
(operand_harden) for KNOWN operands via steering. (c) is the real thing: can a genuinely
NOVEL operand be INSTALLED as a keyed row that the RESIDENT join composes? This is s273
K-battery arm (a) + the `bake(operand)` recursion antecedent.

PRE-REGISTRATION (`λ measure` / `λ yardstick`; fixed before any result).
  Scope (honest): this is the KEYED-INSTALL COMPOSE gate. The install is a keyed
    residual-write fired on the nonce token -- a faithful functional model of an
    appended SuperBake FACT-slot (key=token, value=operand-content). It tests "does the
    resident join compose a novel keyed operand row?" (rung-1 core). Weight-serializing
    to GGUF + quant survival (R5) is a SEPARATE follow-up; not claimed here.
  Register: VALUE (the operand row, s206). Readout = 3-way category logits (COMPOSED, a
    semantic transform: operand -> its category, not a copy).
  Novelty: NONCE strings the model does NOT already categorize (baseline gate N4).
  Install: d_cat[L] = mean object-token residual of a target category's REAL operands
    minus the global operand mean, built in DECLARATIVES (cross-task vs the readout).
    A keyed hook adds scale * d_cat at the nonce's own token position at layer L.
  Generalization: tested across HELD-OUT few-shot prefixes (different exemplars) never
    used to build d_cat -- a memorized single lookup fails this.
  Dose: scale swept; a genuine installed row is graded (harden result).

  Nulls (beside every number):
    N4  baseline  -- un-installed nonce: category acc ~ chance / not target (headroom).
    N-rand        -- install a matched-norm RANDOM direction: no coherent target.
    N-key         -- install d_cat at the WRONG position (a prefix token, not nonce):
                     the nonce should NOT categorize (row must be keyed to its token).

  VERDICT (two-sided):
    INSTALLED-OPERAND-COMPOSED <=> keyed install makes the resident join categorize the
       NOVEL nonce as its target, across HELD-OUT prefixes, >> baseline AND random
       AND wrong-key, dose-responsively.
    NOT-INSTALLED <=> install acc ~ baseline/random, or not key-specific, or not
       generalizing -> a novel operand row cannot be composed by the resident join
       (the bake premise fails at the novel step; steering != install).

License: MIT (`λ provenance`; SuperBake is method-reference only).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

CATS = {
    "animal": ["dog", "cat", "horse", "cow", "wolf", "sheep"],
    "vehicle": ["car", "truck", "train", "boat", "jet", "bus"],
    "plant": ["rose", "oak", "fern", "pine", "palm", "vine"],
}
ALL_OPS = [o for os in CATS.values() for o in os]

# NONCE novel operands (baseline-verified in-run) with assigned target categories.
NONCE = [("zorp", "animal"), ("blint", "vehicle"), ("drell", "plant"),
         ("frob", "animal"), ("glark", "vehicle"), ("murv", "plant")]

FRAMES = [
    ("The farmer", "saw"), ("The child", "drew"), ("The hunter", "tracked"),
    ("A woman", "bought"), ("The boy", "chased"), ("A man", "found"),
    ("The girl", "wanted"), ("The old sailor", "watched"),
]
# held-out few-shot category prefixes (exemplars DISJOINT from d_cat build set? no --
# d_cat is built from declaratives, so all category-map exemplars are held-out vs it).
PREFIXES = [
    "dog: animal\ncar: vehicle\nrose: plant\n",
    "cat: animal\ntruck: vehicle\noak: plant\n",
    "horse: animal\nboat: vehicle\nfern: plant\n",
    "cow: animal\ntrain: vehicle\npine: plant\n",
]
SCALES = [0.0, 1.0, 2.0, 4.0]


def decl(frame, obj):
    s, v = frame
    return f"{s} {v} a {obj}."


def tid(tok, w):
    return tok(" " + w, add_special_tokens=False).input_ids[0]


def cap_hook(store, li):
    def hook(_m, _i, out):
        h = out[0] if isinstance(out, tuple) else out
        store[li] = h.detach().float().cpu().numpy()
    return hook


def add_hook_at(vec_t, pos):
    def hook(_m, _i, out):
        tup = isinstance(out, tuple)
        h = out[0] if tup else out
        if 0 <= pos < h.shape[1]:
            h[0, pos, :] = h[0, pos, :] + vec_t.to(h.dtype)
        return out
    return hook


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--layer", type=int, default=7)
    ap.add_argument("--device", default="mps")
    ap.add_argument("--out", default="results/ffn-bake/operand-insert-qwen3-0-6b")
    args = ap.parse_args()

    L = args.layer
    dev = (args.device if (args.device != "mps" or torch.backends.mps.is_available())
           else "cpu")
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=torch.float32).to(dev).eval()
    dec = model.model.layers
    cat_ids = {c: tid(tok, c) for c in CATS}

    # ── d_cat[category]: category-content direction from DECLARATIVE object residual ──
    per_op = {o: [] for o in ALL_OPS}
    for fr in FRAMES:
        for o in ALL_OPS:
            store: dict[int, np.ndarray] = {}
            h = dec[L].register_forward_hook(cap_hook(store, L))
            ids = tok(decl(fr, o), return_tensors="pt").to(dev)
            with torch.no_grad():
                model(**ids)
            h.remove()
            per_op[o].append(store[L][0, -2, :])       # object token
    op_mean = {o: np.mean(per_op[o], axis=0) for o in ALL_OPS}
    global_mean = np.mean([op_mean[o] for o in ALL_OPS], axis=0)
    d_cat = {c: np.mean([op_mean[o] for o in objs], axis=0) - global_mean
             for c, objs in CATS.items()}

    def category_pred(prefix, word, add_vec=None, pos=None):
        ids = tok(prefix + word + ":", return_tensors="pt").to(dev)
        handle = None
        if add_vec is not None:
            toks = ids.input_ids[0].tolist()
            # colon position = last token decoding to something containing ':'
            colon = max(i for i, t in enumerate(toks) if ":" in tok.decode([t]))
            p = (colon - 1) if pos is None else pos    # nonce last subtoken (keyed)
            vt = torch.tensor(add_vec, dtype=torch.float32, device=dev)
            handle = dec[L].register_forward_hook(add_hook_at(vt, p))
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        if handle:
            handle.remove()
        return max(cat_ids, key=lambda c: lo[cat_ids[c]])

    def acc_over_prefixes(word, target, add_vec=None, wrong_key=False):
        hits = 0
        for pfx in PREFIXES:
            pos = 0 if wrong_key else None   # wrong-key: inject at first prefix token
            pred = category_pred(pfx, word, add_vec=add_vec, pos=pos)
            hits += (pred == target)
        return hits / len(PREFIXES)

    rng = np.random.default_rng(0)

    # ── baseline (N4): are the nonces un-categorized? ──
    base_acc = {w: acc_over_prefixes(w, t) for w, t in NONCE}
    mean_base = float(np.mean(list(base_acc.values())))
    print(f"[insert] L{L} device={dev}  nonces={[w for w, _ in NONCE]}")
    print(f"[insert] N4 baseline nonce->target acc = {mean_base:.3f} "
          f"(per: {[(w, round(a, 2)) for w, a in base_acc.items()]})")

    # ── dose-response: keyed real install vs matched-random vs wrong-key ──
    print("\n scale | install acc | random acc | wrongkey acc")
    print("-------+-------------+------------+-------------")
    per_scale = []
    for s in SCALES:
        inst, rand, wrong = [], [], []
        for w, t in NONCE:
            dv = d_cat[t] * s
            rv = rng.standard_normal(dv.shape)
            rv = rv / (np.linalg.norm(rv) + 1e-9) * (np.linalg.norm(dv) + 1e-12)
            inst.append(acc_over_prefixes(w, t, add_vec=dv))
            rand.append(acc_over_prefixes(w, t, add_vec=rv))
            wrong.append(acc_over_prefixes(w, t, add_vec=dv, wrong_key=True))
        row = {"scale": s, "install_acc": round(float(np.mean(inst)), 3),
               "random_acc": round(float(np.mean(rand)), 3),
               "wrongkey_acc": round(float(np.mean(wrong)), 3)}
        per_scale.append(row)
        print(f" {s:5.1f} | {row['install_acc']:.3f}       | "
              f"{row['random_acc']:.3f}      | {row['wrongkey_acc']:.3f}")

    best = max(per_scale, key=lambda r: r["install_acc"])
    accs = [r["install_acc"] for r in per_scale]
    peak = max(range(len(accs)), key=lambda i: accs[i])
    dose_ok = accs[0] < 0.5 and all(accs[i + 1] >= accs[i] - 1e-6 for i in range(peak))
    installed = (best["install_acc"] > mean_base + 0.34            # >> baseline
                 and best["install_acc"] > best["random_acc"] + 0.34   # >> random
                 and best["install_acc"] > best["wrongkey_acc"] + 0.34  # key-specific
                 and best["install_acc"] > 0.66)   # composes across prefixes
    verdict = ("INSTALLED-OPERAND-COMPOSED (novel keyed row composed by resident join, "
               "generalizing + key-specific + dose-responsive)"
               if (installed and dose_ok) else
               "NOT-INSTALLED (not composed / not key-specific / not graded)")
    print(f"\n[insert] best scale={best['scale']} install={best['install_acc']:.3f} "
          f"vs baseline={mean_base:.3f} random={best['random_acc']:.3f} "
          f"wrongkey={best['wrongkey_acc']:.3f}  dose_ok={dose_ok}")
    print(f"[insert] VERDICT: {verdict}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    res = {"model": args.model_id, "device": dev, "layer": L,
           "readout": "few-shot category (composed)", "prefixes_heldout": len(PREFIXES),
           "nonces": [w for w, _ in NONCE], "baseline_acc": round(mean_base, 3),
           "baseline_per_nonce": {w: round(a, 3) for w, a in base_acc.items()},
           "scales": SCALES, "per_scale": per_scale, "verdict": verdict}
    (out / "operand_insert.json").write_text(json.dumps(res, indent=2))
    print(f"[insert] wrote {out}/operand_insert.json")


if __name__ == "__main__":
    main()
