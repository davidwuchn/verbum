"""Tracer cross-notation v2 — common-mode removal (the fidelity fix).

v1 + isa_decoder_v2 both project activations onto the raw opcode
fingerprints and take argmax. But the 8 fingerprints share a large
common mode (a generic "language composition" direction), so the raw
projection is dominated by it: every probe reports the same primary_op
at a given layer — an ILLUSION of universal opcode firing. The
combinator-specific signal is a small residual underneath.

This script removes the per-layer common mode from the fingerprints
(fp_op − mean_op(fp), renormalized) and asks again: does the residual,
combinator-discriminative fingerprint classify pure prose by combinator?

Reports RAW vs COMMON-MODE-REMOVED (CMR) for:
  - nearest-centroid leave-one-out classification accuracy (+ perm null)
  - prose vs lambda amplitude

If CMR rescues classification at 14B, the combinator structure is real
and was merely masked by measurement fidelity (the common mode). If not,
the combinator distinction genuinely isn't recoverable from prose.

Usage:
    uv run python scripts/experiments/tracer_cross_notation_v2.py \
        --model Qwen/Qwen3-14B --device mps --n-perm 2000

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from verbum.probes.library import crystal_probes  # noqa: E402

CRYSTAL_OPS = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]
RESULTS_DIR = _ROOT / "results" / "tracer-cross-notation"


def log(m):
    print(m, file=sys.stderr, flush=True)


def is_prose(p):
    return ("λ" not in p.prompt) and ("lambda" not in p.prompt.lower())


def load_fingerprints(slug):
    d = np.load(_ROOT / "results" / "hologram-reader" / slug / "opcode_map.npz")
    return np.stack([d[f"fp_{op}"] for op in CRYSTAL_OPS], 0)  # (n_ops, n_layers, d_model)


def remove_common_mode(fps):
    """Per layer, subtract the across-op mean fingerprint, renormalize."""
    common = fps.mean(0, keepdims=True)              # (1, n_layers, d_model)
    resid = fps - common
    norm = np.linalg.norm(resid, axis=2, keepdims=True)
    return resid / np.maximum(norm, 1e-9)


def capture_ffn_output(model, tok, prompts, device, n_layers):
    caps = {li: [] for li in range(n_layers)}
    hooks = []
    for li in range(n_layers):
        def mk(layer):
            def fn(m, i, o):
                caps[layer].append(o[:, -1, :].detach().cpu().float().numpy())
            return fn
        hooks.append(model.model.layers[li].mlp.down_proj.register_forward_hook(mk(li)))
    for pi, prompt in enumerate(prompts):
        ids = tok.encode(prompt, return_tensors="pt", truncation=True, max_length=128).to(device)
        with torch.no_grad():
            model(ids)
        if (pi + 1) % 150 == 0:
            log(f"    {pi+1}/{len(prompts)}")
    for h in hooks:
        h.remove()
    return np.stack([np.concatenate([caps[li][p] for li in range(n_layers)], 0)
                     for p in range(len(prompts))], 0)  # (n_probes, n_layers, d_model)


def opcode_energy(ffn, fps):
    """ffn (P,L,D) · fps (O,L,D) → (P,O) summed over layers."""
    return np.einsum("pld,old->po", ffn, fps)


def nearest_centroid_loo(X, y, n_classes):
    """Leave-one-out nearest-(class-centroid) accuracy. X standardized."""
    Xs = (X - X.mean(0)) / (X.std(0) + 1e-9)
    correct = 0
    for i in range(len(y)):
        best, bd = -1, np.inf
        for c in range(n_classes):
            idx = [j for j in range(len(y)) if y[j] == c and j != i]
            if not idx:
                continue
            cen = Xs[idx].mean(0)
            d = np.sum((Xs[i] - cen) ** 2)
            if d < bd:
                bd, best = d, c
        correct += int(best == y[i])
    return correct / len(y)


def classify_block(E, y, n_perm, rng, n_classes):
    acc = nearest_centroid_loo(E, y, n_classes)
    null = []
    for _ in range(n_perm):
        yp = y.copy()
        rng.shuffle(yp)
        null.append(nearest_centroid_loo(E, yp, n_classes))
    null = np.array(null)
    p = float((np.sum(null >= acc) + 1) / (n_perm + 1))
    return {"accuracy": acc, "null_mean": float(null.mean()),
            "null_std": float(null.std()), "p_value": p}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--n-perm", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    n_classes = len(CRYSTAL_OPS)

    from transformers import AutoModelForCausalLM, AutoTokenizer
    slug = args.model.replace("/", "_")
    fps_raw = load_fingerprints(slug)
    fps_cmr = remove_common_mode(fps_raw)
    # mean pairwise cosine of raw fingerprints (the common-mode magnitude)
    flat = fps_raw.reshape(n_classes, -1)
    flat = flat / np.maximum(np.linalg.norm(flat, axis=1, keepdims=True), 1e-9)
    cm = flat @ flat.T
    mean_fp_cos = float(cm[~np.eye(n_classes, dtype=bool)].mean())

    probes = [p for p in crystal_probes() if p.combinator in CRYSTAL_OPS]
    prose = [p for p in probes if is_prose(p)]
    lam = [p for p in probes if not is_prose(p)]
    log(f"  prose={len(prose)} lambda={len(lam)}  mean fingerprint pairwise cosine={mean_fp_cos:+.3f}")

    tok = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=torch.float16,
        device_map=args.device if args.device != "mps" else None,
        trust_remote_code=True)
    if args.device == "mps":
        model = model.to(args.device)
    model.eval()
    nL = model.config.num_hidden_layers

    log("  capturing prose ...")
    ffn_prose = capture_ffn_output(model, tok, [p.prompt for p in prose], args.device, nL)
    log("  capturing lambda ...")
    ffn_lam = capture_ffn_output(model, tok, [p.prompt for p in lam], args.device, nL)
    del model, tok

    y_prose = np.array([CRYSTAL_OPS.index(p.combinator) for p in prose])

    out = {"model": args.model, "n_prose": len(prose), "n_lambda": len(lam),
           "mean_fingerprint_pairwise_cosine": mean_fp_cos, "chance": 1.0 / n_classes}

    for tag, fps in [("raw", fps_raw), ("common_mode_removed", fps_cmr)]:
        Ep = opcode_energy(ffn_prose, fps)
        El = opcode_energy(ffn_lam, fps)
        cls = classify_block(Ep, y_prose.copy(), args.n_perm, rng, n_classes)
        amp_p = float(np.median(np.abs(Ep).sum(1)))
        amp_l = float(np.median(np.abs(El).sum(1)))
        out[tag] = {"classification": cls,
                    "amplitude_prose_median": amp_p,
                    "amplitude_lambda_median": amp_l,
                    "prose_lower_than_lambda": bool(amp_p < amp_l)}
        log(f"\n  [{tag}] classify prose: acc={cls['accuracy']:.3f} "
            f"chance={1/n_classes:.3f} null={cls['null_mean']:.3f} p={cls['p_value']:.4f}")
        log(f"         amplitude prose={amp_p:.1f} lambda={amp_l:.1f} "
            f"prose<lambda={out[tag]['prose_lower_than_lambda']}")

    with open(RESULTS_DIR / f"{slug}_v2.json", "w") as f:
        json.dump(out, f, indent=2)
    log(f"\n  saved → {RESULTS_DIR / f'{slug}_v2.json'}")


if __name__ == "__main__":
    main()
