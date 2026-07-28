"""FFN-function bake — STAGE 0 (b): the operand WRITE / causal gate.

The operand-map read (operand_map.py) proved operand rows are SEPARABLE/addressable in
the value register (M3 pass). But readable != writeable (s250 scar: the C-field was 92%
decodable yet a causally-inert READOUT register). This is the gate that decides whether
an operand `INSERT` can work: is the addressable operand row CAUSALLY load-bearing?

Frame-invariance (s275) licenses doing the write in HF transformers on Qwen3-0.6B, where
we have full hook access (the llama.cpp tap is read-only; the DRIVER cvec-write tier is
unbuilt). The two frames agree (Gram corr 0.9997), so a causal result here transfers.

DESIGN (pre-registered; `λ measure` / `λ yardstick`).
  Register: VALUE (the operand row is a value claim, s206). Read = next-token logits.
  Direction: d(A->B)[L] = mean_B - mean_A, diff-of-means over contexts of the
    OBJECT-token residual in the DECLARATIVE ("... a <obj>."). Built at the object
    position, NOT the recall answer position, to avoid the trivial "d ~= unembed[B]"
    last-position confound.
  Probe (readout): a RECALL cloze "<decl> <subj> <verb> a" whose clean next token is
    the operand. Operand-determined output => a clean causal handle.
  Intervention: add d(A->B)[L] at layer L across ALL positions during the recall
    forward; read logit(A), logit(B), logit(bystander C).
  Nulls (beside every number): (N-rand) matched-random direction of equal norm;
    (N-spec) bystander operand C -- a writeable row raises B, not any operand.
  ANTI-TRIVIALITY DISCRIMINATOR (the load-bearing control): the LAYER PROFILE. A
    late-only effect is consistent with d aligning with the unembedding (a logit-lens
    nudge, i.e. a READOUT register, s250-shape). A genuine writeable row shows the flip
    when injected UPSTREAM (mid-stack) and PROPAGATED through the remaining layers.

VERDICT (two-sided):
  WRITEABLE     <=> steering flips A->B (argmax) >> random null, B-specific,
                    AND the effect survives mid-stack injection (not late-only).
  READOUT-ONLY  <=> flips only at late layers / not above random / not B-specific
                    => operand row is readable-not-writeable, like the C-field (s250).

License: MIT. Written from this project's instruments (`λ provenance`).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

OBJECTS = ["dog", "bird", "fish", "horse", "mouse", "snake",
           "wolf", "sheep", "duck", "bear", "goat", "frog"]

# (subject, verb) frames; the declarative ends "a <obj>." and the recall cue repeats the
# frame ending in "a" so the clean next token is the operand.
FRAMES = [
    ("The farmer", "saw"),
    ("The child", "drew"),
    ("The hunter", "tracked"),
    ("A woman", "bought"),
    ("The boy", "chased"),
    ("A man", "found"),
    ("The girl", "wanted"),
    ("The old sailor", "watched"),
]


def decl(frame, obj):
    s, v = frame
    return f"{s} {v} a {obj}."


def recall(frame, obj):
    s, v = frame
    return f"{s} {v} a {obj}. {s} {v} a"


def obj_token_id(tok, obj):
    ids = tok(" " + obj, add_special_tokens=False).input_ids
    return ids[0]


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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--layers", default="2,7,13,20,26")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--out", default="results/ffn-bake/operand-write-qwen3-0-6b")
    args = ap.parse_args()

    layers = [int(x) for x in args.layers.split(",")]
    dev = (args.device if (args.device != "mps" or torch.backends.mps.is_available())
           else "cpu")
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, torch_dtype=torch.float32).to(dev).eval()
    dec = model.model.layers
    tid = {o: obj_token_id(tok, o) for o in OBJECTS}

    # ── 1. build per-operand mean OBJECT-token residual per layer (declaratives) ──
    means = {li: {o: [] for o in OBJECTS} for li in layers}
    for fr in FRAMES:
        for o in OBJECTS:
            store: dict[int, np.ndarray] = {}
            hs = [dec[li].register_forward_hook(resid_hook_capture(store, li))
                  for li in layers]
            ids = tok(decl(fr, o), return_tensors="pt").to(dev)
            with torch.no_grad():
                model(**ids)
            for h in hs:
                h.remove()
            # object token = second-to-last (… "a" "obj" ".")
            for li in layers:
                means[li][o].append(store[li][0, -2, :])
    mean_op = {li: {o: np.mean(means[li][o], axis=0) for o in OBJECTS} for li in layers}

    # ── 2. pairs (A -> B cyclic) + bystander C two ahead ──
    pairs = [(OBJECTS[i], OBJECTS[(i + 1) % len(OBJECTS)],
              OBJECTS[(i + 2) % len(OBJECTS)]) for i in range(len(OBJECTS))]
    rng = np.random.default_rng(0)

    def logits_last(text, hook_layer=None, add_vec=None):
        handle = None
        if hook_layer is not None:
            vt = torch.tensor(add_vec, dtype=torch.float32, device=dev)
            handle = dec[hook_layer].register_forward_hook(resid_hook_add(vt))
        ids = tok(text, return_tensors="pt").to(dev)
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        if handle:
            handle.remove()
        return lo

    # ── 3. clean recall accuracy gate ──
    clean_hits = 0
    for fr in FRAMES:
        for (A, _B, _C) in pairs:
            lo = logits_last(recall(fr, A))
            if int(lo.argmax()) == tid[A]:
                clean_hits += 1
    n_trials = len(FRAMES) * len(pairs)
    clean_acc = clean_hits / n_trials
    print(f"[operand-write] clean recall acc = {clean_acc:.3f} "
          f"({clean_hits}/{n_trials})  layers={layers}  device={dev}")
    if clean_acc < 0.7:
        print("[operand-write] WARNING: recall readout weak; verdict uninformative")

    # ── 4. per-layer causal steering: real d(A->B) vs matched-random ──
    print("\n layer | d(B-A) real | flip real | d(B-A) rand | flip rand | B-spec")
    print("-------+--------------+---------+--------------+-----------+------------------")
    per_layer = []
    for li in layers:
        d_real, d_rand, flips, flips_r, bspec = [], [], 0, 0, []
        for fr in FRAMES:
            for (A, B, C) in pairs:
                d = mean_op[li][B] - mean_op[li][A]
                rv = rng.standard_normal(d.shape)
                rv = rv / (np.linalg.norm(rv) + 1e-9) * np.linalg.norm(d)
                base = logits_last(recall(fr, A))
                pr = logits_last(recall(fr, A), hook_layer=li, add_vec=d)
                pr_r = logits_last(recall(fr, A), hook_layer=li, add_vec=rv)
                # steering effect = gain of (B - A) margin
                d_real.append((pr[tid[B]] - pr[tid[A]]) - (base[tid[B]] - base[tid[A]]))
                d_rand.append((pr_r[tid[B]] - pr_r[tid[A]])
                              - (base[tid[B]] - base[tid[A]]))
                if pr[tid[B]] > pr[tid[A]]:
                    flips += 1
                if pr_r[tid[B]] > pr_r[tid[A]]:
                    flips_r += 1
                # B-specificity: B gain vs bystander C gain (both under real steering)
                bspec.append((pr[tid[B]] - base[tid[B]]) - (pr[tid[C]] - base[tid[C]]))
        n = len(FRAMES) * len(pairs)
        row = {"layer": li, "d_margin_real": round(float(np.mean(d_real)), 3),
               "flip_real": round(flips / n, 3),
               "d_margin_rand": round(float(np.mean(d_rand)), 3),
               "flip_rand": round(flips_r / n, 3),
               "b_specificity": round(float(np.mean(bspec)), 3)}
        per_layer.append(row)
        print(f" {li:5d} | {row['d_margin_real']:12.3f} | {row['flip_real']:.3f}   | "
              f"{row['d_margin_rand']:12.3f} | {row['flip_rand']:.3f}     | "
              f"{row['b_specificity']:.3f}")

    late = per_layer[-1]
    mid = per_layer[len(per_layer) // 2]
    writeable = (late["flip_real"] > late["flip_rand"] + 0.2
                 and late["b_specificity"] > 0
                 and mid["flip_real"] > mid["flip_rand"] + 0.2)  # not late-only
    verdict = ("WRITEABLE (operand row causally load-bearing incl. mid-stack)"
               if writeable else
               "READOUT-ONLY / late-confound (readable != writeable, s250-shape)")
    print(f"\n[operand-write] VERDICT: {verdict}")
    print("  (mid-stack flip vs random is the anti-triviality discriminator; "
          "late-only => likely unembed-alignment, not a rewrite)")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    res = {"model": args.model_id, "device": dev,
           "clean_recall_acc": round(clean_acc, 3),
           "n_trials": n_trials, "layers": layers, "verdict": verdict,
           "per_layer": per_layer}
    (out / "operand_write.json").write_text(json.dumps(res, indent=2))
    print(f"[operand-write] wrote {out}/operand_write.json")


if __name__ == "__main__":
    main()
