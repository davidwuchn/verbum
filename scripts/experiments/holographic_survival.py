#!/usr/bin/env python3
"""Holographic self-similarity — does the model survive compression because
it is HOLOGRAPHIC (self-similar, scale-invariant), or merely because it is
DISTRIBUTED + REDUNDANT (the flat-minima null)?

THE CLAIM (crystal-validity-and-fidelity.md §5, audit-registry.md #2, load:
CRITICAL — the compression thesis):
  "Quantization/pruning survive because the model is holographic-self-similar
   — any fragment reconstructs the whole at reduced resolution."

THE NULL we must rule out:
  Distributed superposition + flat minima ALSO predict graceful survival,
  with NO holography. Survival alone is not evidence. So we need the two
  discriminating signatures that the null does NOT predict:

  (a) GRACEFUL-VS-CONTROLS — the trained model degrades more gracefully than
      matched controls (random-init, shuffled-weights) at equal compression.
  (b) SCALE-INVARIANT SHAPE — the degradation d(c)=1−fidelity(c) follows a
      POWER LAW d(c)=A·c^α (self-similar: d(λc)=λ^α d(c)), better than an
      exponential, and more cleanly so than the controls.

  null predicts survival but NOT (necessarily) a power-law self-similar shape
  specific to the trained model. If only (a) holds → distributed+redundant.
  If (a)+(b) → holographic-self-similar. If neither → survival is something else.

METRIC: PPL-ratio is ill-defined for a random-init net (already at ceiling),
so we use a cross-comparable representational metric — the final-layer,
last-token hidden-state cosine of the COMPRESSED model vs its OWN uncompressed
baseline, averaged over eval text. Works identically for trained / random /
shuffled. (We also report trained-model PPL ratio where it is meaningful.)

COMPRESSION AXES:
  - prune: zero the bottom-fraction c of each FFN matrix by |w| (the sieve axis)
  - quant: symmetric per-matrix b-bit quantization (the Q axis)

Usage:
    uv run python scripts/experiments/holographic_survival.py \
        --model Qwen/Qwen3-8B --device mps --dtype bfloat16 \
        --variants trained random shuffled

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "holographic-survival"

FFN_WTYPES = ["gate_proj", "up_proj", "down_proj"]
PRUNE_RATES = [0.0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
QUANT_BITS = [16, 8, 6, 4, 3, 2, 1]
# Rank-truncation axis: keep top fraction of singular components. Probes
# SPECTRAL self-similarity (A) — distinct from magnitude pruning (probes
# distributed redundancy C). A φ-geometric spectrum should degrade power-law
# (scale-invariant) under rank truncation; a random (Marchenko–Pastur) spectrum
# should not. This is the proper test of the SVD self-similarity finding.
RANK_FRACTIONS = [1.0, 0.9, 0.7, 0.5, 0.3, 0.2, 0.1, 0.05, 0.02, 0.01]

EVAL_TEXTS = [
    "The theory of general relativity describes gravity as the curvature of spacetime caused by mass and energy.",
    "In a large mixing bowl, combine the flour, sugar, and baking powder, then add the eggs and milk.",
    "The committee voted unanimously to approve the new environmental regulations for manufacturing plants.",
    "She walked through the ancient forest, her footsteps muffled by centuries of fallen leaves.",
    "The function takes two arguments and returns their composition as a new callable object.",
    "During the Cambrian explosion, roughly 541 million years ago, most major animal phyla appeared.",
    "To solve this equation, first isolate the variable on one side by subtracting three from both sides.",
    "Photosynthesis converts carbon dioxide and water into glucose and oxygen using sunlight as energy.",
    "Machine learning algorithms can be broadly categorized as supervised, unsupervised, or reinforcement.",
    "The Renaissance began in Italy in the fourteenth century and gradually spread across all of Europe.",
    "def compose(f, g):\n    return lambda x: f(g(x))\nresult = compose(square, increment)(5)",
    "Quantum mechanics describes the probabilistic behavior of particles at the atomic and subatomic scale.",
    "Shakespeare wrote thirty-seven plays and one hundred fifty-four sonnets during his literary career.",
    "DNA carries genetic information encoded in sequences of four nucleotide bases along a double helix.",
    "The Pythagorean theorem states that a squared plus b squared equals c squared for right triangles.",
    "Mount Everest is the tallest mountain above sea level, standing at eight thousand eight hundred meters.",
]


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def get_layers(model):
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    if hasattr(model, "gpt_neox") and hasattr(model.gpt_neox, "layers"):
        return model.gpt_neox.layers
    raise RuntimeError(f"Cannot find layers in {type(model).__name__}")


def ffn_weights(model):
    """Yield (name, Linear) for every FFN projection in every layer."""
    for li, layer in enumerate(get_layers(model)):
        for wt in FFN_WTYPES:
            yield f"L{li}.{wt}", getattr(layer.mlp, wt)


def prune_(W: torch.Tensor, rate: float) -> torch.Tensor:
    """Zero the bottom `rate` fraction of |W| per matrix."""
    if rate <= 0:
        return W
    thr = torch.quantile(W.abs().float().flatten()[:5_000_000], rate)
    return torch.where(W.abs() >= thr, W, torch.zeros_like(W))


def quantize_(W: torch.Tensor, bits: int) -> torch.Tensor:
    """Symmetric per-matrix quantize to `bits`, dequantize. bits>=16 = passthrough."""
    if bits >= 16:
        return W
    Wf = W.float()
    qmax = (1 << (bits - 1)) - 1 if bits > 1 else 1  # bits=1 → {-1,+1}·scale (ternary-ish, no 0)
    scale = Wf.abs().amax().clamp(min=1e-10)
    if bits == 1:
        return (torch.sign(Wf) * scale).to(W.dtype)
    q = (Wf / scale * qmax).round().clamp(-qmax, qmax)
    return (q / qmax * scale).to(W.dtype)


@torch.no_grad()
def final_repr(model, tokenizer, device) -> torch.Tensor:
    """Final-layer, last-token hidden state for each eval text → [n, hidden]."""
    vecs = []
    for text in EVAL_TEXTS:
        enc = tokenizer(text, return_tensors="pt", truncation=True, max_length=64)
        enc = {k: v.to(device) for k, v in enc.items()}
        out = model(**enc, output_hidden_states=True)
        h = out.hidden_states[-1][0, -1, :].float().cpu()  # [hidden]
        vecs.append(h)
    return torch.stack(vecs)  # [n, hidden]


def fidelity(Hc: torch.Tensor, H0: torch.Tensor) -> float:
    """Mean per-text cosine between compressed repr Hc and baseline H0."""
    num = (Hc * H0).sum(dim=1)
    den = Hc.norm(dim=1) * H0.norm(dim=1) + 1e-12
    return float((num / den).mean())


def fit_shapes(c: np.ndarray, d: np.ndarray) -> dict:
    """Fit degradation d(c) to power-law (d=A c^α) and exponential
    (d=A(e^{βc}-1)) on c>0, d>0. Return R² of each (power-law in log-log)."""
    m = (c > 1e-9) & (d > 1e-9)
    if m.sum() < 3:
        return {"powerlaw_r2": None, "exp_r2": None, "alpha": None,
                "better": None, "n_points": int(m.sum())}
    cc, dd = c[m], d[m]
    # Power law: log d = log A + α log c  → linear in log-log
    lx, ly = np.log(cc), np.log(dd)
    A = np.vstack([lx, np.ones_like(lx)]).T
    (alpha, _), *_ = np.linalg.lstsq(A, ly, rcond=None)
    pred = A @ np.linalg.lstsq(A, ly, rcond=None)[0]
    ss_res = ((ly - pred) ** 2).sum()
    ss_tot = ((ly - ly.mean()) ** 2).sum() + 1e-12
    pl_r2 = float(1 - ss_res / ss_tot)
    # Exponential: log d vs c (since d≈A(e^{βc}-1)≈Aβc small c; use log on d)
    Ae = np.vstack([cc, np.ones_like(cc)]).T
    coef_e = np.linalg.lstsq(Ae, ly, rcond=None)[0]
    pred_e = Ae @ coef_e
    ss_res_e = ((ly - pred_e) ** 2).sum()
    exp_r2 = float(1 - ss_res_e / ss_tot)
    return {
        "powerlaw_r2": pl_r2, "exp_r2": exp_r2, "alpha": float(alpha),
        "better": "powerlaw" if pl_r2 > exp_r2 else "exponential",
        "n_points": int(m.sum()),
    }


def set_variant(model, variant: str, originals: dict, seed: int = 0):
    """Restore FFN weights to a variant: trained | random | shuffled."""
    g = torch.Generator(device="cpu").manual_seed(seed)
    for name, lin in ffn_weights(model):
        W0 = originals[name]
        if variant == "trained":
            lin.weight.data.copy_(W0)
        elif variant == "random":
            std = W0.float().std().item()
            lin.weight.data.copy_(
                (torch.randn(W0.shape, generator=g) * std).to(W0.dtype))
        elif variant == "shuffled":
            flat = W0.flatten()
            perm = torch.randperm(flat.numel(), generator=g)
            lin.weight.data.copy_(flat[perm].reshape(W0.shape))
        else:
            raise ValueError(variant)


def sweep_axis(model, tokenizer, device, originals, axis: str):
    """Compute fidelity curve over the compression axis (current FFN weights
    are the variant baseline). Returns (levels, fidelities)."""
    # snapshot the variant's current weights as ITS baseline
    base = {name: lin.weight.data.clone() for name, lin in ffn_weights(model)}
    H0 = final_repr(model, tokenizer, device)

    if axis == "rank":
        # Cache full SVD per matrix once (CPU float32), then reconstruct top-r.
        svds = {}
        for name, lin in ffn_weights(model):
            U, S, Vt = torch.linalg.svd(base[name].float().cpu(),
                                        full_matrices=False)
            svds[name] = (U, S, Vt)
        levels = RANK_FRACTIONS
        fids = []
        for frac in levels:
            for name, lin in ffn_weights(model):
                U, S, Vt = svds[name]
                r = max(1, int(frac * S.numel()))
                W_r = (U[:, :r] * S[:r]) @ Vt[:r]
                lin.weight.data.copy_(W_r.to(base[name].dtype).to(device))
            Hc = final_repr(model, tokenizer, device)
            fids.append(fidelity(Hc, H0))
            del Hc
        for name, lin in ffn_weights(model):
            lin.weight.data.copy_(base[name])
        del svds, base, H0
        gc.collect()
        return list(levels), fids

    levels = PRUNE_RATES if axis == "prune" else QUANT_BITS
    fids = []
    for lv in levels:
        for name, lin in ffn_weights(model):
            W0 = base[name]
            if axis == "prune":
                lin.weight.data.copy_(prune_(W0, lv))
            else:
                lin.weight.data.copy_(quantize_(W0, lv))
        Hc = final_repr(model, tokenizer, device)
        fids.append(fidelity(Hc, H0))
        del Hc
    # restore variant baseline
    for name, lin in ffn_weights(model):
        lin.weight.data.copy_(base[name])
    del base, H0
    gc.collect()
    return list(levels), fids


def run(model_id, device, dtype, variants, axes):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    log("=" * 72)
    log("HOLOGRAPHIC SURVIVAL — self-similar or just distributed+redundant?")
    log("=" * 72)
    log(f"Model: {model_id}  device={device}  dtype={dtype}  variants={variants}")
    torch_dtype = {"float32": torch.float32, "bfloat16": torch.bfloat16,
                   "float16": torch.float16}[dtype]

    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True).to(device)
    model.eval()
    log(f"Loaded in {time.time()-t0:.1f}s, {len(get_layers(model))} layers")

    # Snapshot trained FFN weights once (CPU) — the source for all variants.
    originals = {name: lin.weight.data.detach().cpu().clone()
                 for name, lin in ffn_weights(model)}

    out = {"model": model_id, "dtype": dtype, "variants": {}}
    for variant in variants:
        log(f"\n── variant: {variant} ──")
        set_variant(model, variant, originals)
        vres = {}
        for axis in axes:
            levels, fids = sweep_axis(model, tokenizer, device, originals, axis)
            c = np.array(levels, dtype=float)
            if axis == "quant":  # compression severity grows as bits shrink
                c = (16.0 - c) / 16.0
            elif axis == "rank":  # severity grows as kept fraction shrinks
                c = 1.0 - c
            d = 1.0 - np.array(fids)
            shape = fit_shapes(c, d)
            vres[axis] = {"levels": levels, "fidelity": fids,
                          "fid_at_half": None, "shape": shape}
            # gracefulness summary: AUC of fidelity over normalized severity
            sev = c
            order = np.argsort(sev)
            auc = float(np.trapezoid(np.array(fids)[order], sev[order]))
            vres[axis]["auc_fidelity"] = auc
            log(f"  {axis:5s}: AUC(fid)={auc:.4f}  "
                f"shape={shape['better']} (pl_r²={shape['powerlaw_r2']}, "
                f"exp_r²={shape['exp_r2']}, α={shape['alpha']})")
            log("         fid: " + " ".join(
                f"{lv}:{fv:.3f}" for lv, fv in zip(levels, fids, strict=False)))
        out["variants"][variant] = vres
        gc.collect()

    # ── Verdict ──────────────────────────────────────────────────────
    log("\n" + "=" * 72)
    log("VERDICT")
    log("=" * 72)
    for axis in axes:
        log(f"  [{axis}] AUC(fidelity) — higher = more graceful:")
        for v in variants:
            a = out["variants"][v][axis]
            log(f"    {v:9s} AUC={a['auc_fidelity']:.4f}  "
                f"shape={a['shape']['better']} "
                f"pl_r²={a['shape']['powerlaw_r2']}")
    out["interpretation"] = (
        "graceful-vs-controls: trained AUC > random/shuffled AUC ⇒ structure "
        "aids survival. self-similar: trained power-law R² high AND > controls "
        "⇒ holographic. If trained≈controls in shape ⇒ distributed+redundant null."
    )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    suffix = "" if set(axes) == {"prune", "quant"} else "_" + "-".join(axes)
    p = RESULTS_DIR / (model_id.replace("/", "_") + suffix + ".json")
    with open(p, "w") as f:
        json.dump(out, f, indent=2)
    log(f"\nsaved → {p}\ntotal {time.time()-t0:.1f}s")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--dtype", default="float32",
                    choices=["float32", "bfloat16", "float16"])
    ap.add_argument("--variants", nargs="+",
                    default=["trained", "random", "shuffled"])
    ap.add_argument("--axes", nargs="+", default=["prune", "quant"],
                    choices=["prune", "quant", "rank"])
    args = ap.parse_args()
    run(args.model, args.device, args.dtype, args.variants, args.axes)


if __name__ == "__main__":
    main()
