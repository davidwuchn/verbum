"""Magnitude Universality — Is the magnitude crystal universal across models?

If the 8×8 combinator cosine matrix is universal (0.91-0.94 cross-model),
and the crystal is a consequence of the magnitude profile, then the
magnitude profile must be universal too.

Test: extract SVD spectra of W_q and W_up at depth 0.5 from 4 models.
Compare the SHAPE of the spectra (normalized) and the crossing angles.

Models:
  - Pythia-2.8b (d_model=2560, 32 layers)
  - Mistral-7B-v0.3 (d_model=4096, 32 layers)
  - Qwen3-14B (d_model=5120, 40 layers)
  - OLMo-2-1124-13B (d_model=5120, 40 layers)

Measurements:
  1. Normalized SVD spectrum shape (cumulative variance vs fractional rank)
  2. Effective rank as fraction of d_model at 50/80/90/95% thresholds
  3. Crossing angles between W_q and W_up (should be ~68° in all models)
  4. Pairwise spectrum shape correlation across models
  5. Spectral decay rate comparison

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/magnitude_universality_exp.py

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from pathlib import Path

import numpy as np

MODELS = {
    "pythia-2.8b": {
        "name": "EleutherAI/pythia-2.8b-deduped",
        "n_layers": 32, "d_model": 2560, "d_ffn": 10240,
        "arch": "gpt_neox",
    },
    "mistral-7b": {
        "name": "mistralai/Mistral-7B-v0.3",
        "n_layers": 32, "d_model": 4096, "d_ffn": 14336,
        "arch": "llama",
    },
    "qwen3-14b": {
        "name": "Qwen/Qwen3-14B",
        "n_layers": 40, "d_model": 5120, "d_ffn": 17408,
        "arch": "qwen",
    },
    "olmo-2-13b": {
        "name": "allenai/OLMo-2-1124-13B",
        "n_layers": 40, "d_model": 5120, "d_ffn": 13824,
        "arch": "llama",
    },
}

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "magnitude-universality"
SVD_K = 128  # for crossing angle comparison


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def principal_angles_deg(A, B):
    Qa, _ = np.linalg.qr(A)
    Qb, _ = np.linalg.qr(B)
    svals = np.linalg.svd(Qa.T @ Qb, compute_uv=False)
    return np.degrees(np.arccos(np.clip(svals, 0, 1)))


def extract_layer_weights(model_key: str, depth_frac: float = 0.5):
    """Load model, extract W_q and W_up at target depth, delete model."""
    import torch
    from transformers import AutoModelForCausalLM

    cfg = MODELS[model_key]
    layer_idx = min(int(round(depth_frac * (cfg["n_layers"] - 1))), cfg["n_layers"] - 1)

    log(f"\n  Loading {cfg['name']} (layer {layer_idx})...")
    model = AutoModelForCausalLM.from_pretrained(
        cfg["name"], torch_dtype=torch.bfloat16, device_map="cpu",
        trust_remote_code=True,
    )
    model.eval()

    if cfg["arch"] == "gpt_neox":
        layer = model.gpt_neox.layers[layer_idx]
        qkv = layer.attention.query_key_value.weight.detach().float().numpy()
        W_q = qkv[:cfg["d_model"], :]
        W_up = layer.mlp.dense_h_to_4h.weight.detach().float().numpy()
    elif cfg["arch"] in ("llama", "qwen"):
        if hasattr(model, 'model'):
            layer = model.model.layers[layer_idx]
        else:
            layer = model.layers[layer_idx]
        W_q = layer.self_attn.q_proj.weight.detach().float().numpy()
        W_up = layer.mlp.up_proj.weight.detach().float().numpy()
    else:
        raise ValueError(f"Unknown arch: {cfg['arch']}")

    log(f"    W_q: {W_q.shape}, W_up: {W_up.shape}")

    del model
    gc.collect()
    import torch as _t
    if _t.backends.mps.is_available():
        _t.mps.empty_cache()

    return W_q, W_up, layer_idx


def analyze_spectrum(W: np.ndarray, name: str) -> dict:
    """Compute normalized SVD spectrum and derived metrics."""
    _, S, _ = np.linalg.svd(W, full_matrices=False)

    total_var = np.sum(S ** 2)
    s_normalized = S / S[0]  # normalize by largest
    cumvar = np.cumsum(S ** 2) / total_var
    d = len(S)

    # Effective ranks as FRACTIONS of total dimensions
    ranks = {}
    for threshold in [0.50, 0.80, 0.90, 0.95]:
        rank = int(np.searchsorted(cumvar, threshold)) + 1
        ranks[f"{int(threshold*100)}pct"] = rank
        ranks[f"{int(threshold*100)}pct_frac"] = rank / d

    # Cumulative variance at fractional rank points (for cross-model comparison)
    frac_points = np.linspace(0, 1, 101)  # 0%, 1%, 2%, ..., 100%
    cumvar_at_frac = np.interp(frac_points, np.arange(len(cumvar)) / (len(cumvar) - 1), cumvar)

    # Spectral decay: ratio of S[k]/S[0] at various fractional positions
    decay = {}
    for frac in [0.01, 0.05, 0.10, 0.25, 0.50]:
        idx = min(int(frac * d), d - 1)
        decay[f"s_{int(frac*100)}pct"] = float(s_normalized[idx])

    return {
        "name": name,
        "shape": list(W.shape),
        "d": d,
        "total_frobenius": float(np.sqrt(total_var)),
        "effective_ranks": ranks,
        "spectral_decay": decay,
        "cumvar_at_frac": cumvar_at_frac.tolist(),
        "top_singular_values": S[:20].tolist(),
        "s_normalized_100": s_normalized[:100].tolist(),
    }


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    all_results = {}
    spectra = {}  # model_key → {"q": cumvar_at_frac, "up": cumvar_at_frac}

    for model_key in MODELS:
        log(f"\n{'═'*60}")
        log(f"MODEL: {model_key}")
        log(f"{'═'*60}")

        W_q, W_up, layer_idx = extract_layer_weights(model_key)

        # SVD spectra
        q_spec = analyze_spectrum(W_q, f"{model_key}_W_q")
        up_spec = analyze_spectrum(W_up, f"{model_key}_W_up")

        # Crossing angle
        _, _, Vt_q = np.linalg.svd(W_q, full_matrices=False)
        _, _, Vt_up = np.linalg.svd(W_up, full_matrices=False)
        k = min(SVD_K, Vt_q.shape[0], Vt_up.shape[0])
        angles = principal_angles_deg(Vt_q[:k, :].T, Vt_up[:k, :].T)

        crossing = {
            "k": k,
            "mean_angle": float(angles.mean()),
            "median_angle": float(np.median(angles)),
            "min_angle": float(angles.min()),
            "angle_quartiles": [float(np.percentile(angles, q)) for q in [25, 50, 75]],
        }

        all_results[model_key] = {
            "layer_idx": layer_idx,
            "W_q_spectrum": q_spec,
            "W_up_spectrum": up_spec,
            "crossing_angle": crossing,
        }

        spectra[model_key] = {
            "q": np.array(q_spec["cumvar_at_frac"]),
            "up": np.array(up_spec["cumvar_at_frac"]),
        }

        log(f"  W_q effective rank (90%): {q_spec['effective_ranks']['90pct']} "
            f"({q_spec['effective_ranks']['90pct_frac']:.3f} of d)")
        log(f"  W_up effective rank (90%): {up_spec['effective_ranks']['90pct']} "
            f"({up_spec['effective_ranks']['90pct_frac']:.3f} of d)")
        log(f"  Crossing angle: mean={crossing['mean_angle']:.1f}°, "
            f"median={crossing['median_angle']:.1f}°")

        del W_q, W_up
        gc.collect()

    # ── Cross-model comparison ──
    log(f"\n{'═'*60}")
    log(f"CROSS-MODEL COMPARISON")
    log(f"{'═'*60}")

    model_keys = list(MODELS.keys())

    # Pairwise spectrum correlation (cumvar curve similarity)
    q_corrs = np.zeros((len(model_keys), len(model_keys)))
    up_corrs = np.zeros((len(model_keys), len(model_keys)))

    for i, a in enumerate(model_keys):
        for j, b in enumerate(model_keys):
            q_corrs[i, j] = float(np.corrcoef(spectra[a]["q"], spectra[b]["q"])[0, 1])
            up_corrs[i, j] = float(np.corrcoef(spectra[a]["up"], spectra[b]["up"])[0, 1])

    # Off-diagonal mean
    mask = ~np.eye(len(model_keys), dtype=bool)
    q_mean_corr = float(q_corrs[mask].mean())
    up_mean_corr = float(up_corrs[mask].mean())

    all_results["cross_model"] = {
        "q_spectrum_correlations": q_corrs.tolist(),
        "up_spectrum_correlations": up_corrs.tolist(),
        "q_mean_cross_corr": q_mean_corr,
        "up_mean_cross_corr": up_mean_corr,
        "model_order": model_keys,
    }

    log(f"\n  W_q spectrum cross-model correlations:")
    log(f"  {'':>14s}  " + "  ".join(f"{k:>12s}" for k in model_keys))
    for i, a in enumerate(model_keys):
        row = f"  {a:>14s}  " + "  ".join(f"{q_corrs[i,j]:12.6f}" for j in range(len(model_keys)))
        log(row)
    log(f"  Mean off-diagonal: {q_mean_corr:.6f}")

    log(f"\n  W_up spectrum cross-model correlations:")
    log(f"  {'':>14s}  " + "  ".join(f"{k:>12s}" for k in model_keys))
    for i, a in enumerate(model_keys):
        row = f"  {a:>14s}  " + "  ".join(f"{up_corrs[i,j]:12.6f}" for j in range(len(model_keys)))
        log(row)
    log(f"  Mean off-diagonal: {up_mean_corr:.6f}")

    # Effective rank comparison
    log(f"\n  Effective rank (90%) as fraction of d_model:")
    log(f"  {'Model':>14s}  {'W_q':>8s}  {'W_up':>8s}  {'Crossing':>10s}")
    log(f"  {'─'*14}  {'─'*8}  {'─'*8}  {'─'*10}")
    for mk in model_keys:
        r = all_results[mk]
        q_frac = r["W_q_spectrum"]["effective_ranks"]["90pct_frac"]
        up_frac = r["W_up_spectrum"]["effective_ranks"]["90pct_frac"]
        angle = r["crossing_angle"]["mean_angle"]
        log(f"  {mk:>14s}  {q_frac:8.4f}  {up_frac:8.4f}  {angle:9.1f}°")

    # ── Save ──
    elapsed = time.time() - t_start
    all_results["meta"] = {"elapsed_seconds": elapsed}

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)

    log(f"\n{'═'*60}")
    log(f"SUMMARY")
    log(f"{'═'*60}")
    log(f"  Time: {elapsed:.0f}s")
    log(f"  W_q spectrum universality: {q_mean_corr:.6f}")
    log(f"  W_up spectrum universality: {up_mean_corr:.6f}")
    log(f"  Results saved to {out_path}")


if __name__ == "__main__":
    main()
