#!/usr/bin/env python3
"""Sign-topology null — is `cos(sign(W)@x, W@x) ≈ 0.84` crystal-specific,
or generic to ANY matrix with that entry distribution?

THE CLAIM (crystal-universality.md §"Why Ternary Works"):
  "Sign captures topology. `sign(W) @ x` correlates 0.84 with `W @ x`.
   The sign captures the routing decision; magnitude is calibration.
   Ternary IS topology."

This is load-bearing claim #1 in audit-registry.md (load: CRITICAL — the
whole sieve program). The suspected confound:

  cos(sign(W)@x, W@x) may be high for ANY matrix, because sign(W_ij) and
  W_ij are PERFECTLY correlated entry-wise — the large-|x_j| input
  dimensions dominate both Σ_j W_ij x_j and Σ_j sign(W_ij) x_j regardless
  of whether W has crystalline structure. If so, 0.84 is a generic
  property of high-dim linear maps, not evidence of a discrete crystal.

THE DISCRIMINATING CONTROL:
  Hold the REAL activations x fixed (the inputs the true model actually
  produces). Compute cos(sign(W)@x, W@x) for three weight variants:
    (model)    — the trained weight W
    (random)   — iid Gaussian, matched global std, N seeds
    (shuffled) — entries of W permuted, N seeds (identical sign-sparsity
                 and magnitude marginal, structure destroyed)

  If model ≈ random ≈ shuffled  → 0.84 is GENERIC; sign-topology evidence
                                   REFUTED as crystal-specific.
  If model ≫ controls            → crystal signs carry structure the
                                   marginal distribution does not → REAL.

We report mean ± std over seeds for each control, plus the separation
(model − control_mean) in units of control std (z-score), per layer and
weight type, then a one-line verdict.

Usage:
    uv run python scripts/experiments/sign_topology_null.py \
        --model Qwen/Qwen3-0.6B --device mps --n-seed 20

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("PYTHONUNBUFFERED", "1")

import numpy as np
import torch

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "sign-topology-null"

WEIGHT_TYPES = ["gate_proj", "up_proj", "down_proj"]
DEPTH_FRACTIONS = [0.1, 0.3, 0.5, 0.7, 0.9]

# Same calibration register as multilayer_ternary_replace.py — diverse prose,
# code, math, fact, narrative. The x must be REAL routing inputs.
CALIBRATION_TEXTS = [
    "The theory of general relativity describes gravity as the curvature of spacetime.",
    "In a large mixing bowl, combine the flour, sugar, and baking powder.",
    "The committee voted unanimously to approve the new environmental regulations.",
    "She walked through the ancient forest, her footsteps muffled by fallen leaves.",
    "The function takes two arguments and returns their composition.",
    "During the Cambrian explosion, most major animal phyla appeared in the fossil record.",
    "The patient was admitted with acute respiratory distress and fever.",
    "To solve this equation, first isolate the variable on one side.",
    "The Renaissance began in Italy in the 14th century and spread across Europe.",
    "Photosynthesis converts carbon dioxide and water into glucose and oxygen.",
    "Machine learning algorithms can be categorized as supervised or unsupervised.",
    "The Amazon rainforest produces approximately 20 percent of the world's oxygen.",
    "Shakespeare wrote 37 plays and 154 sonnets during his literary career.",
    "The Pythagorean theorem states that a squared plus b squared equals c squared.",
    "The human brain contains approximately 86 billion neurons.",
    "DNA carries genetic information in a double helix structure.",
    "Quantum mechanics describes the behavior of particles at the atomic scale.",
    "def compose(f, g):\n    return lambda x: f(g(x))",
    "import numpy as np\narr = np.zeros((4, 4))\nfor i in range(4):\n    arr[i, i] = 1.0",
    "K I B C — the combinator basis. λx.λy.x is K; λx.x is I; composition is B.",
]


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def get_layers(model):
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    if hasattr(model, "gpt_neox") and hasattr(model.gpt_neox, "layers"):
        return model.gpt_neox.layers
    raise RuntimeError(f"Cannot find layers in {type(model).__name__}")


def get_linear(layer, wtype: str):
    return getattr(layer.mlp, wtype)


def per_token_sign_cosine(W: torch.Tensor, X: torch.Tensor) -> np.ndarray:
    """cos(sign(W)@x, W@x) per token (row of X), averaged over output dim.

    W: [out, in] float32.  X: [tokens, in] float32 (real activations).
    Returns: [tokens] cosine values.
    """
    Y = X @ W.t()                       # [tokens, out]  true action
    Ys = X @ torch.sign(W).t()          # [tokens, out]  sign action
    num = (Y * Ys).sum(dim=1)
    den = Y.norm(dim=1) * Ys.norm(dim=1) + 1e-12
    return (num / den).cpu().numpy()


def shuffled_like(W: torch.Tensor, g: torch.Generator) -> torch.Tensor:
    """Permute ALL entries of W — identical magnitude+sign marginal,
    structure (row/col correlations) destroyed."""
    flat = W.flatten()
    perm = torch.randperm(flat.numel(), generator=g, device=flat.device)
    return flat[perm].reshape(W.shape)


def random_like(W: torch.Tensor, g: torch.Generator) -> torch.Tensor:
    """iid Gaussian matched to W's global std (and zero mean)."""
    std = W.std().item()
    return torch.randn(W.shape, generator=g, device=W.device, dtype=W.dtype) * std


def collect_ffn_inputs(model, tokenizer, layer_indices, wtypes, device, max_tokens=2048):
    """Run calibration text, capture the REAL input x to each (layer, wtype)
    Linear via forward-pre-hooks. Returns {(layer, wtype): X[tokens,in]}."""
    layers = get_layers(model)
    store: dict[tuple[int, str], list[torch.Tensor]] = {}
    handles = []

    def make_hook(key):
        def hook(_module, args):
            x = args[0]
            store.setdefault(key, []).append(x.detach().reshape(-1, x.shape[-1]).float().cpu())
        return hook

    for li in layer_indices:
        for wt in wtypes:
            lin = get_linear(layers[li], wt)
            handles.append(lin.register_forward_pre_hook(make_hook((li, wt))))

    with torch.no_grad():
        for text in CALIBRATION_TEXTS:
            enc = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
            enc = {k: v.to(device) for k, v in enc.items()}
            model(**enc)

    for h in handles:
        h.remove()

    out = {}
    for key, chunks in store.items():
        X = torch.cat(chunks, dim=0)
        if X.shape[0] > max_tokens:
            idx = torch.randperm(X.shape[0])[:max_tokens]
            X = X[idx]
        out[key] = X
    return out


def run(model_id: str, device: str, n_seed: int, max_tokens: int, dtype: str):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    log("=" * 72)
    log("SIGN-TOPOLOGY NULL — is cos(sign(W)@x, W@x) crystal-specific?")
    log("=" * 72)
    log(f"Model: {model_id}  device={device}  n_seed={n_seed}  dtype={dtype}")

    torch_dtype = {"float32": torch.float32, "bfloat16": torch.bfloat16,
                   "float16": torch.float16}[dtype]
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True
    ).to(device)
    model.eval()
    layers = get_layers(model)
    n_layers = len(layers)
    layer_indices = sorted({max(0, min(n_layers - 1, int(f * n_layers))) for f in DEPTH_FRACTIONS})
    log(f"Loaded {n_layers} layers in {time.time()-t0:.1f}s. Probing layers {layer_indices}")

    log("Collecting REAL FFN input activations from calibration text ...")
    inputs = collect_ffn_inputs(model, tokenizer, layer_indices, WEIGHT_TYPES, device, max_tokens)

    records = []
    for li in layer_indices:
        for wt in WEIGHT_TYPES:
            X = inputs[(li, wt)].to(device)
            W = get_linear(layers[li], wt).weight.data.float().to(device)

            model_cos = float(per_token_sign_cosine(W, X).mean())

            rand_vals, shuf_vals = [], []
            for s in range(n_seed):
                g = torch.Generator(device=device).manual_seed(1000 + s)
                rand_vals.append(float(per_token_sign_cosine(random_like(W, g), X).mean()))
                g2 = torch.Generator(device=device).manual_seed(5000 + s)
                shuf_vals.append(float(per_token_sign_cosine(shuffled_like(W, g2), X).mean()))

            rand = np.array(rand_vals)
            shuf = np.array(shuf_vals)

            def z(model_v, ctrl):
                sd = ctrl.std()
                return float((model_v - ctrl.mean()) / sd) if sd > 1e-9 else float("inf")

            rec = {
                "layer": li,
                "wtype": wt,
                "shape": list(W.shape),
                "model_cos": model_cos,
                "random_mean": float(rand.mean()),
                "random_std": float(rand.std()),
                "shuffled_mean": float(shuf.mean()),
                "shuffled_std": float(shuf.std()),
                "z_vs_random": z(model_cos, rand),
                "z_vs_shuffled": z(model_cos, shuf),
            }
            records.append(rec)
            log(
                f"  L{li:>2} {wt:<10} model={model_cos:.4f}  "
                f"rand={rand.mean():.4f}±{rand.std():.4f} (z={rec['z_vs_random']:+.1f})  "
                f"shuf={shuf.mean():.4f}±{shuf.std():.4f} (z={rec['z_vs_shuffled']:+.1f})"
            )
            del X, W
            gc.collect()

    # ── Verdict ──────────────────────────────────────────────────────
    m = np.array([r["model_cos"] for r in records])
    rmean = np.array([r["random_mean"] for r in records])
    smean = np.array([r["shuffled_mean"] for r in records])
    zr = np.array([r["z_vs_random"] for r in records])
    zs = np.array([r["z_vs_shuffled"] for r in records])

    gap_random = float((m - rmean).mean())
    gap_shuffled = float((m - smean).mean())

    # Per-weight-type split — the real story (gate vs value projections).
    by_wtype = {}
    for wt in WEIGHT_TYPES:
        sub = [r for r in records if r["wtype"] == wt]
        mm = np.array([r["model_cos"] for r in sub])
        rr = np.array([r["random_mean"] for r in sub])
        by_wtype[wt] = {
            "model_cos_mean": float(mm.mean()),
            "random_cos_mean": float(rr.mean()),
            "gap_model_minus_random": float((mm - rr).mean()),
            "model_above_random": bool((mm - rr).mean() > 0),
        }

    summary = {
        "model": model_id,
        "n_records": len(records),
        "model_cos_mean": float(m.mean()),
        "random_cos_mean": float(rmean.mean()),
        "shuffled_cos_mean": float(smean.mean()),
        "gap_model_minus_random": gap_random,
        "gap_model_minus_shuffled": gap_shuffled,
        "by_wtype": by_wtype,
        "median_z_vs_random": float(np.median(zr[np.isfinite(zr)])) if np.isfinite(zr).any() else None,
        "median_z_vs_shuffled": float(np.median(zs[np.isfinite(zs)])) if np.isfinite(zs).any() else None,
    }

    log("")
    log("=" * 72)
    log("VERDICT")
    log("=" * 72)
    log(f"  model    cos = {summary['model_cos_mean']:.4f}")
    log(f"  random   cos = {summary['random_cos_mean']:.4f}  (gap {gap_random:+.4f})")
    log(f"  shuffled cos = {summary['shuffled_cos_mean']:.4f}  (gap {gap_shuffled:+.4f})")
    log(f"  median z: vs-random={summary['median_z_vs_random']}, vs-shuffled={summary['median_z_vs_shuffled']}")
    log("  per weight type (model vs random null):")
    for wt in WEIGHT_TYPES:
        b = by_wtype[wt]
        arrow = "ABOVE" if b["model_above_random"] else "BELOW"
        log(f"    {wt:<10} model={b['model_cos_mean']:.4f} "
            f"random={b['random_cos_mean']:.4f} gap={b['gap_model_minus_random']:+.4f} → {arrow} null")
    log("  NOTE: random/shuffled null ≈0.80 ⇒ 'sign preserves linear action'")
    log("        is GENERIC to any matrix. Crystal-specificity lives only in")
    log("        the per-wtype gap, not in the absolute ~0.8 correlation.")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / (model_id.replace("/", "_") + ".json")
    with open(out_path, "w") as f:
        json.dump({"summary": summary, "records": records}, f, indent=2)
    log(f"\nsaved → {out_path}")
    log(f"total {time.time()-t0:.1f}s")
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--n-seed", type=int, default=20)
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--dtype", default="float32",
                    choices=["float32", "bfloat16", "float16"])
    args = ap.parse_args()
    run(args.model, args.device, args.n_seed, args.max_tokens, args.dtype)


if __name__ == "__main__":
    main()
