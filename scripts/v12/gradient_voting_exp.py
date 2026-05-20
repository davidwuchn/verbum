"""Gradient Voting Experiment — How does GD write beta reductions into FFNs?

Central question: if sign(W) captures 97.4% of the Q crystal, and the FFN
is 77% self-similar across layers... what does the cross-layer sign structure
look like? How does gradient descent "vote" on each weight position across
billions of training examples?

Four measurements on Pythia-2.8b (all 32 layers):

1. CROSS-LAYER SIGN CONSENSUS
   For each position (i,j) in W_q, how many of the 32 layers agree on sign?
   If beta reductions are universal, many positions should be unanimous.
   Also measure for W_up (the FFN crystal matrix).

2. MAGNITUDE AS VOTE STRENGTH
   Correlation between |W_ij| and cross-layer sign unanimity.
   Hypothesis: high magnitude = strong GD consensus on this position.

3. SIGN SPECTRUM PER LAYER
   SVD of sign(W_q) at each layer. How many components capture the structure?
   Low effective rank → compressible → dimensional bridge is feasible.

4. COMPRESSION FIDELITY CURVE
   For layer 16 (50% depth): project W_q to k dimensions via SVD, take sign,
   measure crystal fidelity via activation RDM. Sweep k from full down to 64.
   This directly answers: how much dimension can we lose?

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/gradient_voting_exp.py

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from pathlib import Path

import numpy as np

# ── Config ──────────────────────────────────────────────────────────
MODEL_NAME = "EleutherAI/pythia-2.8b-deduped"
N_LAYERS = 32
D_MODEL = 2560
D_FFN = 10240
TARGET_LAYER = 16  # 50% depth for compression sweep

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "gradient-voting"


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def cosine_rdm(X: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(X, axis=1, keepdims=True) + 1e-8
    Xn = X / norms
    return Xn @ Xn.T


def rdm_correlation(A: np.ndarray, B: np.ndarray) -> float:
    """Upper-triangle Pearson correlation between two RDMs."""
    n = A.shape[0]
    idx = np.triu_indices(n, k=1)
    a = A[idx]
    b = B[idx]
    a_c = a - a.mean()
    b_c = b - b.mean()
    denom = np.sqrt(np.sum(a_c**2)) * np.sqrt(np.sum(b_c**2))
    if denom < 1e-10:
        return 0.0
    return float(np.sum(a_c * b_c) / denom)


def load_probes() -> list[dict]:
    probe_path = Path(__file__).parent.parent.parent / "lattice" / "basin_probes.json"
    with open(probe_path) as f:
        data = json.load(f)
        return data if isinstance(data, list) else data["probes"]


# ══════════════════════════════════════════════════════════════════════
# PART 0: Extract ALL weight matrices from ALL layers
# ══════════════════════════════════════════════════════════════════════

def extract_all_weights():
    """Load Pythia-2.8b, extract W_q and W_up from every layer."""
    import torch
    from transformers import AutoModelForCausalLM

    log(f"\n  Loading {MODEL_NAME}...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.float32, device_map="cpu",
    )
    model.eval()

    all_W_q = []  # list of (D_MODEL, D_MODEL) arrays
    all_W_up = []  # list of (D_FFN, D_MODEL) arrays
    all_W_q_magnitudes = []

    for i in range(N_LAYERS):
        layer = model.gpt_neox.layers[i]

        # Pythia fused QKV: (3*d_model, d_model)
        qkv = layer.attention.query_key_value.weight.detach().float().numpy()
        W_q = qkv[:D_MODEL, :]  # (2560, 2560)

        # FFN: dense_h_to_4h (d_ffn, d_model)
        W_up = layer.mlp.dense_h_to_4h.weight.detach().float().numpy()

        all_W_q.append(W_q)
        all_W_up.append(W_up)
        all_W_q_magnitudes.append(np.abs(W_q))

        if (i + 1) % 8 == 0:
            log(f"    Extracted {i+1}/{N_LAYERS} layers")

    del model
    gc.collect()

    return all_W_q, all_W_up, all_W_q_magnitudes


# ══════════════════════════════════════════════════════════════════════
# PART 1: Cross-layer sign consensus
# ══════════════════════════════════════════════════════════════════════

def measure_sign_consensus(all_W: list[np.ndarray], name: str) -> dict:
    """For each position (i,j), count how many layers agree on sign.

    Returns histogram + summary stats.
    """
    log(f"\n{'='*60}")
    log(f"PART 1: Cross-layer sign consensus — {name}")
    log(f"{'='*60}")

    n_layers = len(all_W)
    shape = all_W[0].shape

    # Stack signs: (n_layers, rows, cols)
    signs = np.stack([np.sign(W) for W in all_W], axis=0)  # {-1, 0, +1}

    # For each position, count the dominant sign
    # positive votes = count of layers with sign > 0
    # negative votes = count of layers with sign < 0
    pos_votes = np.sum(signs > 0, axis=0)   # (rows, cols)
    neg_votes = np.sum(signs < 0, axis=0)   # (rows, cols)
    zero_votes = np.sum(signs == 0, axis=0)  # (rows, cols)

    # Unanimity = max(pos, neg) / (pos + neg), ignoring zeros
    total_nonzero = pos_votes + neg_votes
    dominant = np.maximum(pos_votes, neg_votes)
    # Avoid division by zero for positions that are always exactly 0
    unanimity = np.where(total_nonzero > 0, dominant / total_nonzero, 0.0)

    # Histogram of unanimity
    bins = np.linspace(0.5, 1.0, 26)  # 0.50 to 1.00 in 0.02 steps
    hist, edges = np.histogram(unanimity.flatten(), bins=bins)

    # Summary stats
    n_total = unanimity.size
    pct_above_75 = float(np.mean(unanimity >= 0.75)) * 100
    pct_above_90 = float(np.mean(unanimity >= 0.90)) * 100
    pct_above_95 = float(np.mean(unanimity >= 0.95)) * 100
    pct_unanimous = float(np.mean(unanimity >= 1.0)) * 100
    mean_unanimity = float(np.mean(unanimity))
    median_unanimity = float(np.median(unanimity))

    # Spatial structure: is consensus correlated with row/col position?
    row_means = np.mean(unanimity, axis=1)  # average unanimity per output dim
    col_means = np.mean(unanimity, axis=0)  # average unanimity per input dim

    results = {
        "name": name,
        "shape": list(shape),
        "n_layers": n_layers,
        "n_positions": n_total,
        "mean_unanimity": mean_unanimity,
        "median_unanimity": median_unanimity,
        "pct_above_75": pct_above_75,
        "pct_above_90": pct_above_90,
        "pct_above_95": pct_above_95,
        "pct_unanimous": pct_unanimous,
        "pct_always_zero": float(np.mean(total_nonzero == 0)) * 100,
        "histogram": {
            "bins": edges.tolist(),
            "counts": hist.tolist(),
        },
        "row_unanimity_stats": {
            "min": float(row_means.min()),
            "max": float(row_means.max()),
            "std": float(row_means.std()),
        },
        "col_unanimity_stats": {
            "min": float(col_means.min()),
            "max": float(col_means.max()),
            "std": float(col_means.std()),
        },
    }

    log(f"  Shape: {shape} × {n_layers} layers = {n_total:,} positions")
    log(f"  Mean unanimity:  {mean_unanimity:.4f}")
    log(f"  Median unanimity: {median_unanimity:.4f}")
    log(f"  ≥75% agreement:  {pct_above_75:.1f}%")
    log(f"  ≥90% agreement:  {pct_above_90:.1f}%")
    log(f"  ≥95% agreement:  {pct_above_95:.1f}%")
    log(f"  100% unanimous:  {pct_unanimous:.1f}%")

    return results, unanimity, pos_votes, neg_votes


# ══════════════════════════════════════════════════════════════════════
# PART 2: Magnitude as vote strength
# ══════════════════════════════════════════════════════════════════════

def measure_magnitude_consensus(
    all_W: list[np.ndarray],
    unanimity: np.ndarray,
    name: str,
) -> dict:
    """Correlation between average |W_ij| across layers and sign unanimity."""
    log(f"\n{'='*60}")
    log(f"PART 2: Magnitude ↔ sign consensus — {name}")
    log(f"{'='*60}")

    # Average magnitude at each position across layers
    avg_magnitude = np.mean([np.abs(W) for W in all_W], axis=0)

    # Flatten for correlation
    mag_flat = avg_magnitude.flatten()
    unan_flat = unanimity.flatten()

    # Overall Pearson correlation
    corr = float(np.corrcoef(mag_flat, unan_flat)[0, 1])

    # Binned analysis: group by magnitude percentile, measure mean unanimity
    n_bins = 20
    percentiles = np.linspace(0, 100, n_bins + 1)
    mag_bins = np.percentile(mag_flat, percentiles)
    binned = []
    for i in range(n_bins):
        lo, hi = mag_bins[i], mag_bins[i + 1]
        if i < n_bins - 1:
            mask = (mag_flat >= lo) & (mag_flat < hi)
        else:
            mask = (mag_flat >= lo) & (mag_flat <= hi)
        if np.any(mask):
            binned.append({
                "magnitude_pct_lo": float(percentiles[i]),
                "magnitude_pct_hi": float(percentiles[i + 1]),
                "magnitude_range": [float(lo), float(hi)],
                "mean_unanimity": float(unan_flat[mask].mean()),
                "n_positions": int(mask.sum()),
            })

    results = {
        "name": name,
        "pearson_correlation": corr,
        "magnitude_stats": {
            "mean": float(mag_flat.mean()),
            "median": float(np.median(mag_flat)),
            "std": float(mag_flat.std()),
        },
        "binned_analysis": binned,
    }

    log(f"  Pearson(|W|, unanimity): {corr:.4f}")
    log(f"  Bottom 5% magnitude → unanimity: {binned[0]['mean_unanimity']:.4f}")
    log(f"  Top 5% magnitude → unanimity: {binned[-1]['mean_unanimity']:.4f}")
    log(f"  Magnitude range: [{mag_flat.min():.4f}, {mag_flat.max():.4f}]")

    return results


# ══════════════════════════════════════════════════════════════════════
# PART 3: Sign spectrum — SVD of sign(W) per layer
# ══════════════════════════════════════════════════════════════════════

def measure_sign_spectrum(all_W: list[np.ndarray], name: str) -> dict:
    """SVD of sign(W) at each layer. How compressible is the sign structure?"""
    log(f"\n{'='*60}")
    log(f"PART 3: Sign spectrum — {name}")
    log(f"{'='*60}")

    layer_results = []
    all_effective_ranks = {"50pct": [], "80pct": [], "90pct": [], "95pct": []}

    for i, W in enumerate(all_W):
        S_w = np.sign(W).astype(np.float32)  # ternary → float
        _, svals, _ = np.linalg.svd(S_w, full_matrices=False)

        total_var = float(np.sum(svals ** 2))
        cumvar = np.cumsum(svals ** 2) / total_var

        # Effective rank at various thresholds
        ranks = {}
        for threshold in [0.50, 0.80, 0.90, 0.95]:
            rank = int(np.searchsorted(cumvar, threshold)) + 1
            ranks[f"{int(threshold*100)}pct"] = rank
            all_effective_ranks[f"{int(threshold*100)}pct"].append(rank)

        # Top singular value fraction
        top1_frac = float(svals[0]**2 / total_var)
        top10_frac = float(np.sum(svals[:10]**2) / total_var)
        top50_frac = float(np.sum(svals[:50]**2) / total_var)

        layer_results.append({
            "layer": i,
            "depth_frac": i / (N_LAYERS - 1),
            "effective_ranks": ranks,
            "top1_variance_fraction": top1_frac,
            "top10_variance_fraction": top10_frac,
            "top50_variance_fraction": top50_frac,
        })

        if (i + 1) % 8 == 0 or i == 0:
            log(f"  Layer {i:2d}: rank(90%)={ranks['90pct']:4d}, "
                f"top10={top10_frac:.3f}, top50={top50_frac:.3f}")

    # Summary across layers
    summary = {}
    for key, vals in all_effective_ranks.items():
        summary[key] = {
            "mean": float(np.mean(vals)),
            "min": int(np.min(vals)),
            "max": int(np.max(vals)),
            "std": float(np.std(vals)),
        }

    results = {
        "name": name,
        "n_layers": len(all_W),
        "per_layer": layer_results,
        "summary": summary,
    }

    log(f"\n  Summary — effective rank of sign(W):")
    for key, s in summary.items():
        log(f"    {key}: mean={s['mean']:.0f}, min={s['min']}, max={s['max']}")

    return results


# ══════════════════════════════════════════════════════════════════════
# PART 4: Compression fidelity curve (probe-free, weight-space RDM)
# ══════════════════════════════════════════════════════════════════════

def measure_compression_fidelity(W_q: np.ndarray, W_up: np.ndarray) -> dict:
    """Project W to k dims via SVD, take sign, measure crystal fidelity.

    Crystal fidelity = RDM correlation between full sign(W) and
    sign(SVD_project(W, k)). This is probe-free — purely weight-space.

    ALSO: measure row-sign agreement: for each row, what fraction of
    sign(full_row) matches sign(projected_row)?
    """
    log(f"\n{'='*60}")
    log(f"PART 4: Compression fidelity curve — layer {TARGET_LAYER}")
    log(f"{'='*60}")

    results = {}

    for W, name in [(W_q, "W_q"), (W_up, "W_up")]:
        log(f"\n  --- {name} {W.shape} ---")

        # Full sign baseline
        sign_full = np.sign(W).astype(np.float32)
        rdm_full = cosine_rdm(sign_full)

        # SVD of W (not sign(W) — project in continuous space, THEN sign)
        U, S, Vt = np.linalg.svd(W, full_matrices=False)

        k_values = [2560, 2048, 1536, 1024, 768, 512, 384, 256, 192, 128, 96, 64]
        if name == "W_up":
            # W_up is (10240, 2560) — max k is 2560
            k_values = [k for k in k_values if k <= min(W.shape)]

        sweep_results = []
        for k in k_values:
            if k > len(S):
                continue

            # Project: W_k = U[:,:k] @ diag(S[:k]) @ Vt[:k,:]
            W_k = (U[:, :k] * S[:k]) @ Vt[:k, :]
            sign_k = np.sign(W_k).astype(np.float32)

            # RDM fidelity
            rdm_k = cosine_rdm(sign_k)
            fidelity = rdm_correlation(rdm_full, rdm_k)

            # Element-wise sign agreement
            agree = np.mean(sign_full == sign_k)
            # Only count non-zero positions
            nonzero_mask = (sign_full != 0) & (sign_k != 0)
            agree_nonzero = np.mean(sign_full[nonzero_mask] == sign_k[nonzero_mask]) if nonzero_mask.any() else 0.0

            # Frobenius reconstruction error
            frob_err = np.linalg.norm(W - W_k) / np.linalg.norm(W)

            sweep_results.append({
                "k": k,
                "rdm_fidelity": float(fidelity),
                "sign_agreement": float(agree),
                "sign_agreement_nonzero": float(agree_nonzero),
                "frobenius_error": float(frob_err),
                "variance_explained": float(np.sum(S[:k]**2) / np.sum(S**2)),
            })

            log(f"    k={k:5d}: RDM fidelity={fidelity:.4f}, "
                f"sign_agree={agree:.4f}, frob_err={frob_err:.4f}")

        results[name] = {
            "shape": list(W.shape),
            "sweep": sweep_results,
        }

    return results


# ══════════════════════════════════════════════════════════════════════
# PART 5: Cross-layer sign correlation matrix
# ══════════════════════════════════════════════════════════════════════

def measure_cross_layer_sign_correlation(all_W: list[np.ndarray], name: str) -> dict:
    """Pairwise correlation of sign patterns between layers.

    This directly measures: do different layers write the same signs?
    The 77% self-similarity was measured at the activation level.
    What is it at the weight-sign level?
    """
    log(f"\n{'='*60}")
    log(f"PART 5: Cross-layer sign correlation — {name}")
    log(f"{'='*60}")

    n = len(all_W)
    # Flatten sign patterns
    flat_signs = np.stack([np.sign(W).flatten() for W in all_W])  # (n_layers, n_positions)

    # Pairwise Pearson correlation
    corr_matrix = np.corrcoef(flat_signs)  # (n_layers, n_layers)

    # Summary: mean off-diagonal correlation
    mask = ~np.eye(n, dtype=bool)
    off_diag = corr_matrix[mask]

    # Adjacent layer correlation
    adjacent = [float(corr_matrix[i, i+1]) for i in range(n - 1)]

    results = {
        "name": name,
        "cross_layer_corr_matrix": corr_matrix.tolist(),
        "mean_off_diagonal": float(off_diag.mean()),
        "min_off_diagonal": float(off_diag.min()),
        "max_off_diagonal": float(off_diag.max()),
        "std_off_diagonal": float(off_diag.std()),
        "mean_adjacent": float(np.mean(adjacent)),
        "adjacent_correlations": adjacent,
    }

    log(f"  Mean off-diagonal sign correlation: {off_diag.mean():.4f}")
    log(f"  Min: {off_diag.min():.4f}, Max: {off_diag.max():.4f}")
    log(f"  Mean adjacent-layer: {np.mean(adjacent):.4f}")
    log(f"  This is the WEIGHT-SIGN level self-similarity (cf. 0.77 at activation level)")

    return results


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    # ── Extract weights ──
    log("\n" + "═"*60)
    log("EXTRACTING WEIGHTS FROM ALL 32 LAYERS")
    log("═"*60)
    all_W_q, all_W_up, _ = extract_all_weights()

    results = {}

    # ── Part 1: Sign consensus (W_q only to save memory; W_up is 4× larger) ──
    q_consensus, q_unanimity, q_pos, q_neg = measure_sign_consensus(all_W_q, "W_q")
    results["sign_consensus_W_q"] = q_consensus

    # W_up consensus: sample columns to stay in memory
    # W_up is (10240, 2560) per layer × 32 layers = 3.2GB in float32
    # Instead, compute sign consensus on the d_model dimension (columns)
    # by looking at the (10240,) sign vector for each of the 2560 input dims
    log("\n  Computing W_up sign consensus (column-wise to manage memory)...")
    up_signs = np.stack([np.sign(W) for W in all_W_up])  # (32, 10240, 2560)
    up_pos = np.sum(up_signs > 0, axis=0)
    up_neg = np.sum(up_signs < 0, axis=0)
    up_total = up_pos + up_neg
    up_dominant = np.maximum(up_pos, up_neg)
    up_unanimity = np.where(up_total > 0, up_dominant / up_total, 0.0)

    up_pct_75 = float(np.mean(up_unanimity >= 0.75)) * 100
    up_pct_90 = float(np.mean(up_unanimity >= 0.90)) * 100
    up_pct_95 = float(np.mean(up_unanimity >= 0.95)) * 100
    up_mean = float(np.mean(up_unanimity))

    results["sign_consensus_W_up"] = {
        "name": "W_up",
        "shape": list(all_W_up[0].shape),
        "n_layers": N_LAYERS,
        "mean_unanimity": up_mean,
        "pct_above_75": up_pct_75,
        "pct_above_90": up_pct_90,
        "pct_above_95": up_pct_95,
    }

    log(f"  W_up sign consensus:")
    log(f"    Mean unanimity: {up_mean:.4f}")
    log(f"    ≥75%: {up_pct_75:.1f}%, ≥90%: {up_pct_90:.1f}%, ≥95%: {up_pct_95:.1f}%")

    del up_signs, up_pos, up_neg, up_total, up_dominant, up_unanimity
    gc.collect()

    # ── Part 2: Magnitude ↔ consensus ──
    results["magnitude_consensus_W_q"] = measure_magnitude_consensus(
        all_W_q, q_unanimity, "W_q"
    )

    del q_unanimity, q_pos, q_neg
    gc.collect()

    # ── Part 3: Sign spectrum ──
    results["sign_spectrum_W_q"] = measure_sign_spectrum(all_W_q, "W_q")

    # ── Part 4: Compression fidelity ──
    results["compression_fidelity"] = measure_compression_fidelity(
        all_W_q[TARGET_LAYER], all_W_up[TARGET_LAYER]
    )

    # ── Part 5: Cross-layer sign correlation ──
    results["cross_layer_sign_W_q"] = measure_cross_layer_sign_correlation(all_W_q, "W_q")

    # W_up: compute on transposed column-samples to manage memory
    # Actually for W_up we can do the same thing if we flatten
    log("\n  Computing W_up cross-layer sign correlation...")
    # Sample 2560 rows from each W_up to match W_q dimensions
    np.random.seed(42)
    sample_rows = np.random.choice(D_FFN, D_MODEL, replace=False)
    sampled_W_up = [W[sample_rows, :] for W in all_W_up]
    results["cross_layer_sign_W_up"] = measure_cross_layer_sign_correlation(sampled_W_up, "W_up (sampled rows)")

    del sampled_W_up
    gc.collect()

    # ── Save ──
    elapsed = time.time() - t_start
    results["meta"] = {
        "model": MODEL_NAME,
        "n_layers": N_LAYERS,
        "d_model": D_MODEL,
        "d_ffn": D_FFN,
        "target_layer": TARGET_LAYER,
        "elapsed_seconds": elapsed,
    }

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    log(f"\n  Results saved to {out_path}")

    # ── Final summary ──
    log(f"\n{'═'*60}")
    log(f"SUMMARY — Gradient Voting in Pythia-2.8b")
    log(f"{'═'*60}")
    log(f"  Time: {elapsed:.0f}s")
    log(f"")
    log(f"  SIGN CONSENSUS (W_q):")
    log(f"    Mean unanimity: {q_consensus['mean_unanimity']:.4f}")
    log(f"    ≥75% agreement: {q_consensus['pct_above_75']:.1f}%")
    log(f"    ≥90% agreement: {q_consensus['pct_above_90']:.1f}%")
    log(f"    100% unanimous: {q_consensus['pct_unanimous']:.1f}%")
    log(f"")
    log(f"  MAGNITUDE ↔ CONSENSUS (W_q):")
    mag = results["magnitude_consensus_W_q"]
    log(f"    Pearson(|W|, unanimity): {mag['pearson_correlation']:.4f}")
    log(f"    Bottom 5% mag → unanimity: {mag['binned_analysis'][0]['mean_unanimity']:.4f}")
    log(f"    Top 5% mag → unanimity: {mag['binned_analysis'][-1]['mean_unanimity']:.4f}")
    log(f"")
    log(f"  SIGN SPECTRUM (W_q):")
    spec = results["sign_spectrum_W_q"]["summary"]
    log(f"    Effective rank (90%): mean={spec['90pct']['mean']:.0f}")
    log(f"    Effective rank (50%): mean={spec['50pct']['mean']:.0f}")
    log(f"")
    log(f"  COMPRESSION FIDELITY (layer {TARGET_LAYER}):")
    for name in ["W_q", "W_up"]:
        sweep = results["compression_fidelity"][name]["sweep"]
        for pt in sweep:
            if pt["k"] == 512:
                log(f"    {name} k=512: RDM fidelity={pt['rdm_fidelity']:.4f}, "
                    f"sign_agree={pt['sign_agreement']:.4f}")
    log(f"")
    log(f"  CROSS-LAYER SIGN CORRELATION:")
    log(f"    W_q mean off-diagonal: {results['cross_layer_sign_W_q']['mean_off_diagonal']:.4f}")
    log(f"    W_up mean off-diagonal: {results['cross_layer_sign_W_up']['mean_off_diagonal']:.4f}")
    log(f"    (cf. 0.77 self-similarity at activation level)")


if __name__ == "__main__":
    main()
