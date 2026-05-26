#!/usr/bin/env python3
"""
Composed Relational Transform Probe — Can Zone A be one ternary plate?

Test: capture teacher residuals at zone boundaries (embed, L15, L47, L63),
compute the effective linear transformation between them, and check if
sign(T) captures the mapping.

If sign(T_compress) @ input ≈ T_compress @ input with r > 0.84, then
the entire 16-layer Zone A can be replaced by ONE ternary plate.

Usage:
    cd verbum
    uv run python scripts/explore/probe_composed_transform.py

License: MIT
"""

from __future__ import annotations

import sys
import time
import json
from pathlib import Path

import numpy as np
import torch

DEVICE = "mps"
DTYPE = torch.bfloat16
MODEL_NAME = "Qwen/Qwen3.6-27B"

PROBE_TEXTS = [
    "The cat sits on the mat while the dog runs through the garden chasing butterflies in the warm afternoon sun.",
    "Every student reads a book about mathematics before the final exam, hoping to understand the key concepts.",
    "Lambda calculus is a formal system in mathematical logic for expressing computation based on function abstraction.",
    "The president announced that the committee would review the proposal before the deadline expires next month.",
    "According to Church's theorem, there exists no general effective decision procedure for statements of arithmetic.",
    "John, who Mary likes, runs quickly through the dense forest while the sun sets behind the distant mountains.",
]


def load_model():
    from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig

    print(f"\n  Loading {MODEL_NAME}...", flush=True)
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=DTYPE, device_map=DEVICE,
        trust_remote_code=True, attn_implementation="eager",
    )
    model.eval()
    print(f"  Loaded in {time.time()-t0:.1f}s", flush=True)
    return model, tokenizer


def get_layers(model):
    if hasattr(model, 'model') and hasattr(model.model, 'language_model'):
        lm = model.model.language_model
        if hasattr(lm, 'model') and hasattr(lm.model, 'layers'):
            return lm.model.layers
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        return model.model.layers
    raise ValueError(f"Cannot find layers in {type(model).__name__}")


def get_embed(model):
    if hasattr(model, 'model') and hasattr(model.model, 'language_model'):
        lm = model.model.language_model
        if hasattr(lm, 'model') and hasattr(lm.model, 'embed_tokens'):
            return lm.model.embed_tokens
    if hasattr(model, 'model') and hasattr(model.model, 'embed_tokens'):
        return model.model.embed_tokens
    return None


def capture_zone_boundaries(model, tokenizer, text, boundary_layers):
    """Capture residuals at zone boundary layers."""
    layers = get_layers(model)
    residuals = {}
    hooks = []

    embed = get_embed(model)
    if embed is not None:
        def eh(m, a, o):
            h = o[0] if isinstance(o, tuple) else o
            residuals["embed"] = h[0].detach().cpu().float().numpy()
        hooks.append(embed.register_forward_hook(eh))

    for idx in boundary_layers:
        def make_hook(layer_idx):
            def hf(m, a, o):
                h = o[0] if isinstance(o, tuple) else o
                residuals[f"L{layer_idx}"] = h[0].detach().cpu().float().numpy()
            return hf
        hooks.append(layers[idx].register_forward_hook(make_hook(idx)))

    try:
        inputs = tokenizer(text, return_tensors="pt")
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            model(**inputs, output_attentions=False)
    finally:
        for h in hooks:
            h.remove()

    return residuals


def compute_linear_transform(X, Y):
    """Compute the least-squares linear transform Y ≈ T @ X.

    X: (n_tokens, d_in)
    Y: (n_tokens, d_out)
    Returns: T (d_out, d_in), residual stats
    """
    # Solve Y = X @ T^T  →  T^T = (X^T X)^{-1} X^T Y
    # Using numpy lstsq for numerical stability
    T_t, residuals, rank, sv = np.linalg.lstsq(X, Y, rcond=None)
    T = T_t.T  # (d_out, d_in)

    # Reconstruction quality
    Y_pred = X @ T_t
    error = Y - Y_pred
    r2 = 1.0 - np.sum(error**2) / (np.sum((Y - Y.mean(axis=0))**2) + 1e-10)

    return T, {
        "r2": float(r2),
        "rank": int(rank) if not isinstance(rank, np.ndarray) else int(rank),
        "sv_top5": sv[:5].tolist() if sv is not None and len(sv) > 0 else [],
    }


def analyze_ternary_transform(T, X, Y, label):
    """Check if sign(T) captures the transformation."""
    d_out, d_in = T.shape

    # sign(T) as ternary plate
    T_ternary = np.sign(T)  # {-1, 0, +1}
    n_zero = np.sum(T_ternary == 0)
    n_pos = np.sum(T_ternary == 1)
    n_neg = np.sum(T_ternary == -1)

    # Apply ternary transform
    Y_ternary = X @ T_ternary.T

    # Correlation between T@X and sign(T)@X (per-token, averaged)
    Y_full = X @ T.T
    # Flatten for correlation
    corr = np.corrcoef(Y_full.flatten(), Y_ternary.flatten())[0, 1]

    # Per-dimension correlation (more meaningful)
    per_dim_corr = []
    for d in range(min(d_out, Y.shape[1])):
        if Y_full[:, d].std() > 1e-10:
            c = np.corrcoef(Y_full[:, d], Y_ternary[:, d])[0, 1]
            if not np.isnan(c):
                per_dim_corr.append(c)
    mean_dim_corr = np.mean(per_dim_corr) if per_dim_corr else 0.0

    # Cosine similarity (per-token, averaged)
    y_full_norms = np.linalg.norm(Y_full, axis=1, keepdims=True) + 1e-10
    y_tern_norms = np.linalg.norm(Y_ternary, axis=1, keepdims=True) + 1e-10
    cos_sim = np.mean(np.sum(
        (Y_full / y_full_norms) * (Y_ternary / y_tern_norms), axis=1
    ))

    # How much of T is effectively ternary already?
    # Measure: what fraction of T's energy is in the signs vs magnitudes?
    T_sign_energy = np.sum(np.abs(T))  # L1 norm = sum of |sign × magnitude| where sign contributes 1
    T_total_energy = np.sqrt(np.sum(T**2))  # L2 norm

    # SVD of T to check rank structure
    _, S_T, _ = np.linalg.svd(T, full_matrices=False)
    S_T = S_T[:min(256, len(S_T))]
    energy_T = S_T**2
    total_energy_T = energy_T.sum()
    rank_90_T = int(np.searchsorted(np.cumsum(energy_T) / total_energy_T, 0.90)) + 1

    result = {
        "label": label,
        "shape": [d_out, d_in],
        "global_correlation": float(corr),
        "mean_per_dim_correlation": float(mean_dim_corr),
        "cosine_similarity": float(cos_sim),
        "sign_distribution": {
            "positive": int(n_pos),
            "negative": int(n_neg),
            "zero": int(n_zero),
        },
        "transform_rank90": rank_90_T,
        "transform_top5_sv": S_T[:5].tolist(),
    }

    print(f"\n    {label}:")
    print(f"      Shape: {T.shape}")
    print(f"      Transform rank90: {rank_90_T}")
    print(f"      sign(T)@x vs T@x correlation: {corr:.4f}")
    print(f"      Per-dim correlation: {mean_dim_corr:.4f}")
    print(f"      Cosine similarity: {cos_sim:.4f}")
    print(f"      Sign distribution: +{n_pos/T.size:.1%} / -{n_neg/T.size:.1%} / 0={n_zero/T.size:.1%}")

    return result


def main():
    model, tokenizer = load_model()

    # Zone boundaries: embed(-1), L15 (end Zone A), L47 (end Zone B), L63 (end Zone C)
    boundary_layers = [15, 47, 63]

    print(f"\n{'='*80}")
    print(f"  Composed Relational Transform Probe")
    print(f"  Testing: can zones be extracted as single ternary plates?")
    print(f"{'='*80}")

    # Collect residuals across all texts
    all_X_embed = []
    all_Y_L15 = []
    all_Y_L47 = []
    all_Y_L63 = []

    for i, text in enumerate(PROBE_TEXTS):
        print(f"\n  Probe {i+1}/{len(PROBE_TEXTS)}: \"{text[:60]}...\"", flush=True)
        residuals = capture_zone_boundaries(model, tokenizer, text, boundary_layers)

        # Skip position 0 (attention sink)
        embed = residuals.get("embed")
        l15 = residuals.get("L15")
        l47 = residuals.get("L47")
        l63 = residuals.get("L63")

        if embed is not None and l15 is not None:
            all_X_embed.append(embed[1:])  # skip pos 0
            all_Y_L15.append(l15[1:])
        if l15 is not None and l47 is not None:
            all_Y_L47.append(l47[1:])
        if l47 is not None and l63 is not None:
            all_Y_L63.append(l63[1:])

        print(f"    tokens: {embed.shape[0] if embed is not None else 0}", flush=True)

    # Concatenate
    X_embed = np.concatenate(all_X_embed, axis=0)
    Y_L15 = np.concatenate(all_Y_L15, axis=0)
    Y_L47 = np.concatenate(all_Y_L47, axis=0)
    Y_L63 = np.concatenate(all_Y_L63, axis=0)

    print(f"\n  Total tokens: {X_embed.shape[0]}")
    print(f"  d_model: {X_embed.shape[1]}")

    # Free model memory
    del model
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    results = []

    # ── Zone A: embed → L15 (compress) ──
    print(f"\n{'─'*80}")
    print(f"  ZONE A (compress): embed → L15 (16 layers)")
    print(f"{'─'*80}")

    T_A, stats_A = compute_linear_transform(X_embed, Y_L15)
    print(f"    Linear fit R² = {stats_A['r2']:.4f}")
    r = analyze_ternary_transform(T_A, X_embed, Y_L15, "Zone_A_compress")
    r["linear_r2"] = stats_A["r2"]
    results.append(r)

    # ── Zone B: L15 → L47 (compute) ──
    print(f"\n{'─'*80}")
    print(f"  ZONE B (compute): L15 → L47 (32 layers)")
    print(f"{'─'*80}")

    T_B, stats_B = compute_linear_transform(Y_L15, Y_L47)
    print(f"    Linear fit R² = {stats_B['r2']:.4f}")
    r = analyze_ternary_transform(T_B, Y_L15, Y_L47, "Zone_B_compute")
    r["linear_r2"] = stats_B["r2"]
    results.append(r)

    # ── Zone C: L47 → L63 (expand) ──
    print(f"\n{'─'*80}")
    print(f"  ZONE C (expand): L47 → L63 (16 layers)")
    print(f"{'─'*80}")

    T_C, stats_C = compute_linear_transform(Y_L47, Y_L63)
    print(f"    Linear fit R² = {stats_C['r2']:.4f}")
    r = analyze_ternary_transform(T_C, Y_L47, Y_L63, "Zone_C_expand")
    r["linear_r2"] = stats_C["r2"]
    results.append(r)

    # ── Full model: embed → L63 ──
    print(f"\n{'─'*80}")
    print(f"  FULL MODEL: embed → L63 (64 layers)")
    print(f"{'─'*80}")

    T_full, stats_full = compute_linear_transform(X_embed, Y_L63)
    print(f"    Linear fit R² = {stats_full['r2']:.4f}")
    r = analyze_ternary_transform(T_full, X_embed, Y_L63, "Full_model")
    r["linear_r2"] = stats_full["r2"]
    results.append(r)

    # ── Verdict ──
    print(f"\n{'='*80}")
    print(f"  VERDICT")
    print(f"{'='*80}")

    for r in results:
        label = r["label"]
        corr = r["global_correlation"]
        cos = r["cosine_similarity"]
        r2 = r["linear_r2"]
        rank = r["transform_rank90"]

        status = "★ TERNARY VIABLE" if corr > 0.80 else ("◎ PARTIAL" if corr > 0.60 else "✗ NEEDS FULL")
        print(f"\n  {label}:")
        print(f"    Linear R²: {r2:.4f}  |  sign(T) correlation: {corr:.4f}  |  cos: {cos:.4f}")
        print(f"    Rank90: {rank}  |  {status}")

    # ── Save ──
    out_dir = Path("results/composed-transform-probe")
    out_dir.mkdir(parents=True, exist_ok=True)

    def clean(obj):
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: clean(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [clean(v) for v in obj]
        return obj

    with open(out_dir / "results.json", "w") as f:
        json.dump(clean(results), f, indent=2)

    print(f"\n  Results saved to {out_dir}/results.json\n")


if __name__ == "__main__":
    main()
