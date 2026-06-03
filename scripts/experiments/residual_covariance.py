#!/usr/bin/env python3
"""Residual covariance rank — how many dimensions does the residual stream occupy?

THE QUESTION:
  Can the per-layer eigenvector rotation U be derived from equations?
  Session 184 showed U is constrained to the null space of the accumulated
  residual. But constraining against the MEAN direction only eliminates
  1 dimension per layer (36 of 4096 = 1%).

  The FULL COVARIANCE captures the subspace the residual actually occupies.
  If the residual uses 500 effective dims by layer 22, then U at layer 22
  must map to the remaining 3596 dims. That's a much tighter constraint.

MEASUREMENTS:
  1. Full covariance Cov(h_l) at each layer
  2. Effective rank: how many eigenvalues above noise floor
  3. Cumulative subspace: union of all prior layers' covariance subspaces
  4. V-subspace overlap: project weight matrix V onto covariance subspace
  5. Growth curve: does effective rank grow linearly, as φ^l, or ?

Usage:
  uv run python scripts/experiments/residual_covariance.py
  uv run python scripts/experiments/residual_covariance.py --model Qwen/Qwen3-8B
  uv run python scripts/experiments/residual_covariance.py --n-calib 30

License: MIT
"""

from __future__ import annotations

import argparse
import math
import os
import time

os.environ.setdefault('PYTHONUNBUFFERED', '1')

import numpy as np
import torch
import torch.nn.functional as F

PHI = (1 + math.sqrt(5)) / 2


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


def effective_rank(eigenvalues: np.ndarray, threshold: float = 0.99) -> int:
    """Number of eigenvalues needed to capture `threshold` fraction of total variance."""
    total = eigenvalues.sum()
    if total < 1e-12:
        return 0
    cumsum = np.cumsum(eigenvalues) / total
    return int(np.searchsorted(cumsum, threshold) + 1)


def effective_rank_entropy(eigenvalues: np.ndarray) -> float:
    """Roy's effective rank: exp(entropy of normalized eigenvalues).
    
    More robust than threshold-based — gives continuous measure.
    """
    eigs = eigenvalues[eigenvalues > 1e-12]
    if len(eigs) == 0:
        return 0.0
    p = eigs / eigs.sum()
    entropy = -np.sum(p * np.log(p))
    return float(np.exp(entropy))


def run_experiment(model_id: str, n_calib: int = 20, seq_len: int = 256):
    log("=" * 72)
    log("RESIDUAL COVARIANCE RANK EXPERIMENT")
    log("=" * 72)
    log(f"Model: {model_id}")
    log(f"Calibration: {n_calib} sequences, {seq_len} tokens each")
    log()

    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float32, device_map="cpu",
        low_cpu_mem_usage=True)
    model.eval()

    n_layers = model.config.num_hidden_layers
    hidden_size = model.config.hidden_size
    log(f"Loaded: {n_layers} layers, hidden={hidden_size}")

    # Calibration data
    try:
        from datasets import load_dataset
        dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="train")
        texts = [t for t in dataset["text"] if len(t.strip()) > 100]
    except Exception:
        texts = ["Language models process text by applying compositional operations. " * 20] * 100

    calib_ids = []
    for text in texts:
        ids = tokenizer.encode(text, add_special_tokens=False, truncation=True, max_length=seq_len)
        if len(ids) >= 64:
            calib_ids.append(torch.tensor(ids[:seq_len]))
        if len(calib_ids) >= n_calib:
            break
    log(f"Using {len(calib_ids)} calibration sequences\n")

    # ═══════════════════════════════════════════════════════════
    # Phase 1: Collect hidden states and compute covariances
    # ═══════════════════════════════════════════════════════════
    log("Phase 1: Collecting hidden states...")
    t0 = time.time()

    # Accumulate running mean and covariance (Welford-style)
    # For each layer: mean vector and covariance matrix
    means = [np.zeros(hidden_size) for _ in range(n_layers + 1)]
    covs = [np.zeros((hidden_size, hidden_size)) for _ in range(n_layers + 1)]
    total_tokens = 0

    with torch.no_grad():
        for batch_idx, ids in enumerate(calib_ids):
            outputs = model(ids.unsqueeze(0), output_hidden_states=True)

            for l in range(n_layers + 1):
                h = outputs.hidden_states[l].squeeze(0).float().cpu().numpy()  # (seq, hidden)
                n_tok = h.shape[0]

                # Running accumulation (not Welford, just sum — we normalize after)
                means[l] += h.sum(axis=0)
                covs[l] += h.T @ h  # outer product accumulation

                if l == 0:
                    total_tokens += n_tok

            if (batch_idx + 1) % 5 == 0:
                log(f"  batch {batch_idx + 1}/{len(calib_ids)}")

    # Finalize: mean and centered covariance
    for l in range(n_layers + 1):
        means[l] /= total_tokens
        covs[l] = covs[l] / total_tokens - np.outer(means[l], means[l])

    elapsed = time.time() - t0
    log(f"  Done in {elapsed:.1f}s ({total_tokens} tokens)\n")

    # ═══════════════════════════════════════════════════════════
    # Phase 2: Eigendecompose each covariance
    # ═══════════════════════════════════════════════════════════
    log("Phase 2: Eigendecomposing covariances...")

    layer_eigenvalues = []
    layer_eigenvectors = []  # top-k eigenvectors per layer

    for l in range(n_layers + 1):
        eigenvalues, eigenvectors = np.linalg.eigh(covs[l])
        # Sort descending
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]

        # Clamp negatives (numerical noise)
        eigenvalues = np.maximum(eigenvalues, 0)

        layer_eigenvalues.append(eigenvalues)
        layer_eigenvectors.append(eigenvectors)

    log("  Done.\n")

    # ═══════════════════════════════════════════════════════════
    # Phase 3: Effective rank per layer
    # ═══════════════════════════════════════════════════════════
    log("=" * 72)
    log("EFFECTIVE RANK PER LAYER")
    log("=" * 72)

    log(f"\n  {'Layer':>5s} {'Phase':>8s} {'Rank99%':>8s} {'Rank95%':>8s} "
        f"{'Rank90%':>8s} {'RoyRank':>8s} {'TopEig':>12s} {'EigDecay':>10s}")
    log(f"  {'─'*5} {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*12} {'─'*10}")

    ranks_99 = []
    ranks_95 = []
    ranks_90 = []
    roy_ranks = []

    for l in range(n_layers + 1):
        eigs = layer_eigenvalues[l]

        r99 = effective_rank(eigs, 0.99)
        r95 = effective_rank(eigs, 0.95)
        r90 = effective_rank(eigs, 0.90)
        roy = effective_rank_entropy(eigs)

        ranks_99.append(r99)
        ranks_95.append(r95)
        ranks_90.append(r90)
        roy_ranks.append(roy)

        # Phase classification
        if l <= 6:
            phase = "EXPAND"
        elif l <= 22:
            phase = "ORTHO"
        elif l <= 34:
            phase = "ALIGN"
        elif l <= 35:
            phase = "COLLAPSE"
        else:
            phase = "OUTPUT"

        # Eigenvalue decay ratio (first/second)
        decay = eigs[0] / (eigs[1] + 1e-12) if len(eigs) > 1 else float('inf')

        log(f"  {l:5d} {phase:>8s} {r99:8d} {r95:8d} {r90:8d} "
            f"{roy:8.1f} {eigs[0]:12.2f} {decay:10.4f}")

    # ═══════════════════════════════════════════════════════════
    # Phase 4: Cumulative subspace — union across layers
    # ═══════════════════════════════════════════════════════════
    log(f"\n{'=' * 72}")
    log("CUMULATIVE SUBSPACE RANK (union of all prior layers)")
    log(f"{'=' * 72}")

    log(f"\n  {'Layer':>5s} {'Phase':>8s} {'CumRank99':>10s} {'CumRank95':>10s} "
        f"{'CumRoy':>10s} {'NullDims':>10s}")
    log(f"  {'─'*5} {'─'*8} {'─'*10} {'─'*10} {'─'*10} {'─'*10}")

    # Build cumulative covariance: sum of all per-layer covariances up to l
    cum_cov = np.zeros((hidden_size, hidden_size))
    cum_ranks_99 = []
    cum_ranks_95 = []
    cum_roys = []

    for l in range(n_layers + 1):
        cum_cov = cum_cov + covs[l]

        # Eigendecompose the cumulative covariance
        cum_eigs, _ = np.linalg.eigh(cum_cov)
        cum_eigs = np.maximum(cum_eigs[::-1], 0)  # descending, non-negative

        cr99 = effective_rank(cum_eigs, 0.99)
        cr95 = effective_rank(cum_eigs, 0.95)
        croy = effective_rank_entropy(cum_eigs)

        cum_ranks_99.append(cr99)
        cum_ranks_95.append(cr95)
        cum_roys.append(croy)

        null_dims = hidden_size - cr99

        phase = "EXPAND" if l <= 6 else "ORTHO" if l <= 22 else "ALIGN" if l <= 34 else "COLLAPSE" if l <= 35 else "OUTPUT"

        log(f"  {l:5d} {phase:>8s} {cr99:10d} {cr95:10d} "
            f"{croy:10.1f} {null_dims:10d}")

    # ═══════════════════════════════════════════════════════════
    # Phase 5: V-subspace overlap (weight SVD V vs residual covariance)
    # ═══════════════════════════════════════════════════════════
    log(f"\n{'=' * 72}")
    log("V-SUBSPACE OVERLAP (weight V vs residual covariance subspace)")
    log(f"{'=' * 72}")

    log(f"\n  {'Layer':>5s} {'Phase':>8s} {'V_in_res%':>10s} {'V_out_res%':>10s} "
        f"{'MeanProj':>10s} {'CumNullDim':>10s}")
    log(f"  {'─'*5} {'─'*8} {'─'*10} {'─'*10} {'─'*10} {'─'*10}")

    # For each layer, take the gate_proj weight V and see how much
    # of it falls within vs outside the CUMULATIVE residual subspace
    cum_cov_running = np.zeros((hidden_size, hidden_size))

    for l in range(n_layers):
        cum_cov_running = cum_cov_running + covs[l]

        # Get top eigenvectors of cumulative covariance
        cum_eigs, cum_vecs = np.linalg.eigh(cum_cov_running)
        idx = np.argsort(cum_eigs)[::-1]
        cum_eigs = np.maximum(cum_eigs[idx], 0)
        cum_vecs = cum_vecs[:, idx]

        # Residual subspace: top-k eigenvectors capturing 99%
        k_res = effective_rank(cum_eigs, 0.99)
        res_basis = cum_vecs[:, :k_res]  # (hidden, k_res)

        # Get gate_proj SVD
        W = model.model.layers[l].mlp.gate_proj.weight.data.float().cpu()
        k_svd = min(64, min(W.shape))
        _, _, V = torch.svd_lowrank(W, q=k_svd, niter=3)
        V_np = V.numpy()  # (hidden, k_svd) — right singular vectors

        # Project each V column onto the residual subspace
        # projection coefficient = ||P_res @ v_i|| / ||v_i||
        proj_coeffs = []
        for i in range(V_np.shape[1]):
            v = V_np[:, i]
            # Project onto residual subspace
            proj = res_basis @ (res_basis.T @ v)
            proj_frac = np.linalg.norm(proj) / (np.linalg.norm(v) + 1e-10)
            proj_coeffs.append(proj_frac)

        proj_coeffs = np.array(proj_coeffs)
        in_pct = (proj_coeffs > 0.5).mean() * 100  # fraction with >50% in residual
        out_pct = (proj_coeffs < 0.5).mean() * 100
        mean_proj = proj_coeffs.mean()

        phase = "EXPAND" if l <= 6 else "ORTHO" if l <= 22 else "ALIGN" if l <= 34 else "COLLAPSE"

        log(f"  {l:5d} {phase:>8s} {in_pct:10.1f} {out_pct:10.1f} "
            f"{mean_proj:10.4f} {hidden_size - k_res:10d}")

    # ═══════════════════════════════════════════════════════════
    # Phase 6: Growth curve analysis
    # ═══════════════════════════════════════════════════════════
    log(f"\n{'=' * 72}")
    log("GROWTH CURVE ANALYSIS")
    log(f"{'=' * 72}")

    # Does cumulative rank grow linearly, exponentially, or as φ^l?
    layers = np.arange(1, n_layers + 1, dtype=float)
    crs = np.array(cum_ranks_99[1:], dtype=float)  # skip layer 0 (embedding)

    # Fit log(rank) vs layer for exponential growth
    valid = crs > 0
    if valid.sum() > 2:
        log_crs = np.log(crs[valid])
        slope, intercept = np.polyfit(layers[valid], log_crs, 1)
        exp_base = np.exp(slope)
        log(f"\n  Exponential fit: rank ≈ {np.exp(intercept):.1f} × {exp_base:.4f}^layer")
        log(f"  If φ-growth: base would be {PHI:.4f}")
        log(f"  Actual base: {exp_base:.4f}")
        log(f"  Ratio actual/φ: {exp_base/PHI:.4f}")

    # Linear fit
    if valid.sum() > 2:
        slope_lin, intercept_lin = np.polyfit(layers[valid], crs[valid], 1)
        log(f"\n  Linear fit: rank ≈ {intercept_lin:.1f} + {slope_lin:.1f} × layer")
        log(f"  Rank at layer 36: {intercept_lin + slope_lin * 36:.0f}")
        log(f"  Null dims at layer 36: {hidden_size - (intercept_lin + slope_lin * 36):.0f}")

    # Saturation check: does rank plateau?
    if len(crs) > 10:
        early_growth = (crs[5] - crs[0]) / 5 if crs[0] > 0 else 0
        late_growth = (crs[-1] - crs[-6]) / 5 if crs[-6] > 0 else 0
        log(f"\n  Early growth rate (L1-6): {early_growth:.1f} dims/layer")
        log(f"  Late growth rate (L{n_layers-4}-{n_layers}): {late_growth:.1f} dims/layer")
        if late_growth < early_growth * 0.5:
            log(f"  ⚠️  Growth is SATURATING — rank plateaus before using all dims")
        elif late_growth > early_growth * 1.5:
            log(f"  📈 Growth is ACCELERATING")
        else:
            log(f"  ≈  Growth is roughly LINEAR")

    log(f"\n{'=' * 72}")
    log("SUMMARY")
    log(f"{'=' * 72}")
    log(f"\n  Hidden dim: {hidden_size}")
    log(f"  Final cumulative rank (99%): {cum_ranks_99[-1]}")
    log(f"  Final null space dims: {hidden_size - cum_ranks_99[-1]}")
    log(f"  Null space fraction: {(hidden_size - cum_ranks_99[-1]) / hidden_size:.3f}")
    log(f"\n  If null space is large → U is WEAKLY constrained → more room for data-dependence")
    log(f"  If null space is small → U is TIGHTLY constrained → more derivable")

    log(f"\n{'=' * 72}")
    log("DONE")
    log(f"{'=' * 72}")

    # Save results
    import json
    out_dir = "results/residual-covariance"
    os.makedirs(out_dir, exist_ok=True)

    summary = {
        'model': model_id,
        'hidden_size': hidden_size,
        'n_layers': n_layers,
        'total_tokens': total_tokens,
        'per_layer_rank_99': ranks_99,
        'per_layer_rank_95': ranks_95,
        'per_layer_rank_90': ranks_90,
        'per_layer_roy_rank': roy_ranks,
        'cumulative_rank_99': cum_ranks_99,
        'cumulative_rank_95': cum_ranks_95,
        'cumulative_roy_rank': cum_roys,
    }

    with open(f"{out_dir}/summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    log(f"\nResults saved to {out_dir}/summary.json")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-8B")
    parser.add_argument("--n-calib", type=int, default=20)
    parser.add_argument("--seq-len", type=int, default=256)
    args = parser.parse_args()

    run_experiment(args.model, args.n_calib, args.seq_len)


if __name__ == "__main__":
    main()
