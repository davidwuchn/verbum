#!/usr/bin/env python3
"""
M-Space Noise-Based Zero Placement — Micro Model Experiment 2.

Hypothesis: sign-quantizing attention weights to ternary {-1,+1} blurs the
attention kernel M = W_q^T @ W_k. The float32 model concentrates 90% of
M's energy in ~13 modes (layer 2); ternary quantization spreads this to ~35
modes (the "gem" degrades). Inserting zeros at the RIGHT positions can
sharpen the gem back by removing weight positions that contribute mostly to
high-rank (noise) modes.

Three zero-placement strategies are compared:
  A. Magnitude threshold  — zero positions where |w[h,i]| < threshold * mean(|w|)
  B. M-space noise score  — zero positions whose contribution to M lands mostly in
                            noise modes (rank > K where K captures 90% energy)
  C. Random              — baseline: zero random positions

For each strategy, sweep zero-fraction 0%→60%, measure:
  • Energy concentration in top-K modes of M_zeroed
  • Mode alignment: cosine similarity of top-3 singular vectors vs float32 reference
  • Eval loss: replace Q/K with sign(zeroed_weights) * per_row_gamma, measure loss

Detailed analysis on layer 2 (most structured); all layers reported in summary.

Key formula for M-space noise score of W_q position (h, i):
  Zeroing W_q[h,i] changes M by: ΔM[i, j] = -W_q[h,i] * W_k[h, j]
  Equivalently: ΔM = s * e_i ⊗ W_k[h,:]  where s = W_q[h,i]
  Using the float32 M SVD: M = U Σ V^T
    u_k^T ΔM v_k = s * U[i, k] * (W_k[h,:] @ V[:, k])
  Signal energy = Σ_{k ≤ K}  (s * U[i,k] * (W_k[h,:] @ V[:,k]))²
  Noise energy  = Σ_{k > K}  (s * U[i,k] * (W_k[h,:] @ V[:,k]))²
  noise_score[h,i] = noise_energy / (signal_energy + 1e-10)

  Same logic applies to W_k positions (swap roles of U, V, W_q, W_k).

License: MIT
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import mlx.core as mx
import mlx.nn as nn

sys.path.insert(0, str(Path(__file__).parent))
from micro_model import MicroModel, MicroConfig


# ══════════════════════════════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════════════════════════════

CHECKPOINT_PATH = Path("checkpoints/micro/final/model.npz")
TRAIN_FILE = "data/compile-train.jsonl"
EVAL_FILE = "data/compile-eval.jsonl"
RESULTS_PATH = Path("results/mspace-zeros/summary.json")

# Zero-fraction sweep: 0% to 60% in steps of 5%
ZERO_FRACTIONS = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]

# Magnitude threshold sweep
MAGNITUDE_THRESHOLDS = np.linspace(0.0, 1.5, 16)  # 16 threshold values


# ══════════════════════════════════════════════════════════════════════
# Data loading
# ══════════════════════════════════════════════════════════════════════

def load_examples(path: str) -> list[dict]:
    """Load JSONL compile examples."""
    examples = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(json.loads(line))
    return examples


def tokenize_examples(examples: list[dict], tokenizer, max_len: int = 256, eod_id: int = 151643) -> list[np.ndarray]:
    """Tokenize input+output pairs to integer sequences."""
    sequences = []
    for ex in examples:
        text = f"{ex['input']}\n{ex['output']}"
        ids = tokenizer.encode(text, add_special_tokens=False)
        ids.append(eod_id)
        if len(ids) > max_len:
            ids = ids[:max_len]
        sequences.append(np.array(ids, dtype=np.int32))
    return sequences


def make_eval_batch(sequences: list[np.ndarray], max_seq_len: int = 256) -> tuple[mx.array, mx.array]:
    """Pack all sequences into a single contiguous eval batch."""
    stream = np.concatenate(sequences)
    T = min(max_seq_len, len(stream) - 1)
    return mx.array(stream[:T].reshape(1, T)), mx.array(stream[1:T+1].reshape(1, T))


# ══════════════════════════════════════════════════════════════════════
# SVD helpers
# ══════════════════════════════════════════════════════════════════════

def svd_energy_rank(singular_values: np.ndarray, target_frac: float = 0.90) -> int:
    """Return smallest k such that top-k modes capture >= target_frac of total energy."""
    energy = singular_values ** 2
    total = energy.sum()
    if total < 1e-30:
        return len(singular_values)
    cumulative = np.cumsum(energy) / total
    k = int(np.searchsorted(cumulative, target_frac)) + 1
    return min(k, len(singular_values))


def energy_concentration(singular_values: np.ndarray, k: int) -> float:
    """Fraction of total energy in top-k modes."""
    energy = singular_values ** 2
    total = energy.sum()
    if total < 1e-30:
        return 1.0
    return float(energy[:k].sum() / total)


def mode_alignment(U_ref: np.ndarray, U_new: np.ndarray, n_modes: int = 3) -> list[float]:
    """Cosine similarity of top n_modes singular vectors between two SVDs.

    Each singular vector sign is arbitrary, so we take |cosine|.
    """
    n = min(n_modes, U_ref.shape[1], U_new.shape[1])
    aligns = []
    for k in range(n):
        cos = abs(float(np.dot(U_ref[:, k], U_new[:, k])))
        aligns.append(cos)
    return aligns


# ══════════════════════════════════════════════════════════════════════
# Zeroing strategies
# ══════════════════════════════════════════════════════════════════════

def apply_magnitude_threshold(W: np.ndarray, threshold: float) -> np.ndarray:
    """Zero positions where |w[h,i]| < threshold * mean(|w[h,:]|) per row."""
    W_out = W.copy()
    per_row_mean = np.abs(W).mean(axis=1, keepdims=True)  # (d_out, 1)
    mask = np.abs(W) < threshold * per_row_mean
    W_out[mask] = 0.0
    return W_out


def magnitude_threshold_for_fraction(W: np.ndarray, target_frac: float) -> float:
    """Binary-search for the threshold value that zeros approximately target_frac of positions.

    Returns the threshold in units of per-row mean (not absolute magnitude).
    """
    if target_frac <= 0.0:
        return 0.0

    n_total = W.size
    target_n = int(target_frac * n_total)

    # Compute each position's ratio |w[h,i]| / mean(|w[h,:]|)
    per_row_mean = np.abs(W).mean(axis=1, keepdims=True)
    ratios = np.abs(W) / (per_row_mean + 1e-12)  # (d_out, d_in)
    flat_ratios = ratios.flatten()

    # Sort ascending; zero the smallest ratios = lowest threshold positions
    sorted_ratios = np.sort(flat_ratios)
    if target_n >= len(sorted_ratios):
        return sorted_ratios[-1] + 1e-6
    return float(sorted_ratios[target_n])


def compute_mspace_noise_scores(
    W_q: np.ndarray,   # (d_out, d_in) float32 original weights
    W_k: np.ndarray,   # (d_out, d_in) float32 original weights
    U: np.ndarray,     # (d_in, d_in) left singular vectors of M_float
    V: np.ndarray,     # (d_in, d_in) right singular vectors of M_float (V = Vt.T)
    K: int,            # number of signal modes (90%-energy threshold)
) -> tuple[np.ndarray, np.ndarray]:
    """Compute M-space noise scores for every position in W_q and W_k.

    For W_q position (h, i):
      Zeroing W_q[h,i] changes M by: ΔM = W_q[h,i] * e_i ⊗ W_k[h,:]
      (sign: zeroing removes the contribution, so ΔM = -W_q[h,i] * e_i ⊗ W_k[h,:],
       but for scoring purposes the sign of the contribution doesn't matter, only
       how it projects onto signal vs noise subspaces.)

      u_k^T ΔM v_k = W_q[h,i] * U[i,k] * (W_k[h,:] @ V[:,k])

      noise_score[h,i]  = Σ_{k > K}  (W_q[h,i] * U[i,k] * (W_k[h,:] @ V[:,k]))²
                         / (Σ_{k ≤ K} (...)² + 1e-10)

    Returns:
      noise_q : (d_out, d_in) noise ratio for each W_q position
      noise_k : (d_out, d_in) noise ratio for each W_k position
    """
    d_out, d_in = W_q.shape
    n_modes = U.shape[1]  # full rank (d_in)

    # ── W_q noise scores ──
    # Precompute: for each head h, the projection of W_k[h,:] onto each singular vector v_k
    # shape: (d_out, n_modes)  [h, k] = W_k[h,:] @ V[:,k]
    Vk_proj = W_k @ V           # (d_out, n_modes), V[:,k] is k-th right singular vector
    # For each position (h,i): coefficient = W_q[h,i] * U[i,k] * Vk_proj[h,k]
    # U[i, k]: (d_in, n_modes)  — left singular vectors indexed by (row, mode)
    # coefficient[h, i, k] = W_q[h,i] * U[i,k] * Vk_proj[h,k]
    # We want signal/noise split, so compute squared projections and sum over signal/noise bands

    # noise_q[h, i] = Σ_{k>K} (W_q[h,i] * U[i,k] * Vk_proj[h,k])²
    #               = W_q[h,i]² * Σ_{k>K} U[i,k]² * Vk_proj[h,k]²

    # Break into signal (modes 0..K-1) and noise (modes K..end)
    # Shape gymnastics: we want a (d_out, d_in) result

    # U²: (d_in, n_modes); Vk_proj²: (d_out, n_modes)
    U2 = U ** 2            # (d_in, n_modes)
    Vk2 = Vk_proj ** 2    # (d_out, n_modes)

    # Σ_{k > K} U[i,k]² * Vk_proj[h,k]²
    # = sum over noise modes of outer product at each (h,i)
    # For fixed h,i: Σ_k U2[i,k] * Vk2[h,k]
    # This is: Vk2 @ U2.T  →  (d_out, d_in) where [h,i] = Σ_k Vk2[h,k]*U2[i,k]

    signal_energy_q = (Vk2[:, :K] @ U2[:, :K].T)   # (d_out, d_in)
    noise_energy_q  = (Vk2[:, K:] @ U2[:, K:].T)   # (d_out, d_in)

    # Multiply by W_q² (sign doesn't matter, it cancels in ratio)
    W_q2 = W_q ** 2
    signal_energy_q *= W_q2
    noise_energy_q  *= W_q2

    noise_score_q = noise_energy_q / (signal_energy_q + 1e-10)

    # ── W_k noise scores ──
    # For W_k position (h, j):
    #   ΔM[i, j] = W_k[h, j] * W_q[h, i]   — affects column j of M
    #   u_k^T ΔM v_k = W_k[h,j] * (W_q[h,:] @ U[:,k]) * V[j,k]
    #   noise_score[h,j] = Σ_{k>K} (W_k[h,j] * Uq_proj[h,k] * V[j,k])²
    #                    / (Σ_{k≤K} (...)²  + 1e-10)
    # where Uq_proj[h,k] = W_q[h,:] @ U[:,k]

    Uq_proj = W_q @ U           # (d_out, n_modes), [h,k] = W_q[h,:] @ U[:,k]
    V2 = V ** 2                 # (d_in, n_modes)
    Uq2 = Uq_proj ** 2          # (d_out, n_modes)

    signal_energy_k = (Uq2[:, :K] @ V2[:, :K].T)   # (d_out, d_in)
    noise_energy_k  = (Uq2[:, K:] @ V2[:, K:].T)   # (d_out, d_in)

    W_k2 = W_k ** 2
    signal_energy_k *= W_k2
    noise_energy_k  *= W_k2

    noise_score_k = noise_energy_k / (signal_energy_k + 1e-10)

    return noise_score_q.astype(np.float32), noise_score_k.astype(np.float32)


def apply_zero_fraction_by_scores(W: np.ndarray, scores: np.ndarray, frac: float) -> np.ndarray:
    """Zero the fraction `frac` of positions with the HIGHEST noise scores.

    Args:
        W:      original weight matrix (d_out, d_in)
        scores: noise score per position (d_out, d_in); higher = more noise
        frac:   fraction of total positions to zero (0.0 to 1.0)

    Returns: copy of W with highest-score positions zeroed.
    """
    W_out = W.copy()
    if frac <= 0.0:
        return W_out
    n_zero = int(frac * W.size)
    if n_zero == 0:
        return W_out
    flat_scores = scores.flatten()
    # argsort descending — take top n_zero
    idx = np.argsort(-flat_scores)[:n_zero]
    W_flat = W_out.flatten()
    W_flat[idx] = 0.0
    return W_flat.reshape(W_out.shape)


def apply_random_zeros(W: np.ndarray, frac: float, rng: np.random.RandomState) -> np.ndarray:
    """Zero a random fraction of positions (baseline)."""
    W_out = W.copy()
    if frac <= 0.0:
        return W_out
    n_zero = int(frac * W.size)
    if n_zero == 0:
        return W_out
    idx = rng.choice(W.size, size=n_zero, replace=False)
    W_flat = W_out.flatten()
    W_flat[idx] = 0.0
    return W_flat.reshape(W_out.shape)


# ══════════════════════════════════════════════════════════════════════
# Ternary conversion with per-row gamma scaling
# ══════════════════════════════════════════════════════════════════════

def to_ternary_with_gamma(W: np.ndarray) -> np.ndarray:
    """Convert W to sign(W) * gamma, where gamma = mean(|w_row|) per row.

    Zeros in W remain zero (ternary with holes). Non-zeros become ±gamma.
    This preserves the per-row L1 scale.
    """
    W_out = W.copy()
    per_row_gamma = np.abs(W).mean(axis=1, keepdims=True)  # (d_out, 1)
    signs = np.sign(W)
    # Apply scaling where weight is non-zero
    nonzero_mask = W != 0.0
    W_out[nonzero_mask] = (signs * per_row_gamma).flatten()[
        nonzero_mask.flatten()
    ]
    return W_out.astype(np.float32)


# ══════════════════════════════════════════════════════════════════════
# Loss measurement with temporary weight replacement
# ══════════════════════════════════════════════════════════════════════

def measure_eval_loss(
    model: MicroModel,
    layer_idx: int,
    W_q_new: np.ndarray,
    W_k_new: np.ndarray,
    eval_input: mx.array,
    eval_target: mx.array,
) -> float:
    """Replace Q/K weights for one layer, measure eval loss, restore.

    Both W_q_new and W_k_new should already be in the "effective" form
    (e.g. ternary × gamma), so this is a straight weight swap.
    """
    block = model.blocks[layer_idx]
    attn = block.attn

    # Save original weights
    orig_q = np.array(attn.q_proj.weight)
    orig_k = np.array(attn.k_proj.weight)

    try:
        # Set new weights
        attn.q_proj.weight = mx.array(W_q_new)
        attn.k_proj.weight = mx.array(W_k_new)
        mx.eval(attn.q_proj.weight, attn.k_proj.weight)

        # Forward pass (no target → get logits, compute CE manually to avoid crystal loss)
        logits, _ = model(eval_input)
        mx.eval(logits)

        # Manual CE loss (targets shifted by 1 inside eval_target)
        loss_val = nn.losses.cross_entropy(
            logits.reshape(-1, model.cfg.vocab_size),
            eval_target.reshape(-1),
        ).mean()
        mx.eval(loss_val)
        loss = float(loss_val.item())
    finally:
        # Always restore
        attn.q_proj.weight = mx.array(orig_q)
        attn.k_proj.weight = mx.array(orig_k)
        mx.eval(attn.q_proj.weight, attn.k_proj.weight)

    return loss


# ══════════════════════════════════════════════════════════════════════
# Per-layer experiment
# ══════════════════════════════════════════════════════════════════════

def run_layer_experiment(
    model: MicroModel,
    layer_idx: int,
    eval_input: mx.array,
    eval_target: mx.array,
    baseline_loss: float,
    rng: np.random.RandomState,
    verbose: bool = False,
) -> dict:
    """Run all three zeroing strategies on one attention layer.

    Returns a dict with sweep results for magnitude, mspace, and random strategies.
    """
    block = model.blocks[layer_idx]
    attn = block.attn
    W_q = np.array(attn.q_proj.weight).astype(np.float64)   # (128, 128)
    W_k = np.array(attn.k_proj.weight).astype(np.float64)   # (128, 128)

    # ── Float32 M kernel and SVD ──
    M_float = (W_q.T @ W_k).astype(np.float64)              # (128, 128)
    U_f, s_f, Vt_f = np.linalg.svd(M_float, full_matrices=False)
    V_f = Vt_f.T  # (d_in, n_modes) — right singular vectors as columns

    K = svd_energy_rank(s_f, target_frac=0.90)
    energy_float = energy_concentration(s_f, K)

    if verbose:
        print(f"\n  Float32 M: rank-90 = {K}, top-{K} energy = {energy_float*100:.1f}%")
        print(f"  Singular values (top-10): {s_f[:10].round(3)}")

    # ── M-space noise scores (computed from float32 W, not ternary) ──
    # We use the float32 weights to estimate which positions contribute to noise modes.
    # This tells us: which weight values, when removed, would reduce noise-mode energy?
    if verbose:
        print(f"  Computing M-space noise scores...")

    noise_q, noise_k = compute_mspace_noise_scores(
        W_q.astype(np.float32),
        W_k.astype(np.float32),
        U_f.astype(np.float32),
        V_f.astype(np.float32),
        K,
    )

    if verbose:
        print(f"  Noise scores Q: mean={noise_q.mean():.4f}, max={noise_q.max():.4f}, "
              f"median={np.median(noise_q):.4f}")
        print(f"  Noise scores K: mean={noise_k.mean():.4f}, max={noise_k.max():.4f}, "
              f"median={np.median(noise_k):.4f}")

    # ── Sweep zero fractions for all three strategies ──
    results_mag   = []  # magnitude-threshold strategy
    results_noise = []  # M-space noise strategy
    results_rand  = []  # random baseline

    # We do the random strategy multiple times and average to reduce variance
    N_RANDOM_TRIALS = 5

    for frac in ZERO_FRACTIONS:
        # ── Strategy A: Magnitude threshold ──
        # Find the threshold value that achieves ~frac zeros in EACH of W_q and W_k
        thresh_q = magnitude_threshold_for_fraction(W_q.astype(np.float32), frac)
        thresh_k = magnitude_threshold_for_fraction(W_k.astype(np.float32), frac)
        # Use the mean threshold (or separately for q and k)
        W_q_mag = apply_magnitude_threshold(W_q.astype(np.float32), thresh_q)
        W_k_mag = apply_magnitude_threshold(W_k.astype(np.float32), thresh_k)
        actual_frac_q_mag = float((W_q_mag == 0).mean())
        actual_frac_k_mag = float((W_k_mag == 0).mean())

        # Ternary + gamma scaling
        W_q_mag_t = to_ternary_with_gamma(W_q_mag)
        W_k_mag_t = to_ternary_with_gamma(W_k_mag)

        M_mag = (W_q_mag_t.T @ W_k_mag_t).astype(np.float64)
        _, s_mag, _ = np.linalg.svd(M_mag, full_matrices=False)
        U_mag, _, _ = np.linalg.svd(M_mag, full_matrices=False)

        # Actually get U and V together
        U_mag, s_mag_v, Vt_mag = np.linalg.svd(M_mag, full_matrices=False)

        conc_mag = energy_concentration(s_mag_v, K)
        align_mag = mode_alignment(U_f, U_mag, n_modes=3)
        loss_mag = measure_eval_loss(model, layer_idx, W_q_mag_t, W_k_mag_t, eval_input, eval_target)

        results_mag.append({
            "frac": frac,
            "actual_frac_q": actual_frac_q_mag,
            "actual_frac_k": actual_frac_k_mag,
            "energy_concentration": conc_mag,
            "mode_alignment_top3": align_mag,
            "eval_loss": loss_mag,
            "loss_delta": loss_mag - baseline_loss,
        })

        # ── Strategy B: M-space noise ──
        W_q_nz = apply_zero_fraction_by_scores(W_q.astype(np.float32), noise_q, frac)
        W_k_nz = apply_zero_fraction_by_scores(W_k.astype(np.float32), noise_k, frac)
        actual_frac_q_nz = float((W_q_nz == 0).mean())
        actual_frac_k_nz = float((W_k_nz == 0).mean())

        W_q_nz_t = to_ternary_with_gamma(W_q_nz)
        W_k_nz_t = to_ternary_with_gamma(W_k_nz)

        M_nz = (W_q_nz_t.T @ W_k_nz_t).astype(np.float64)
        U_nz, s_nz, Vt_nz = np.linalg.svd(M_nz, full_matrices=False)

        conc_nz = energy_concentration(s_nz, K)
        align_nz = mode_alignment(U_f, U_nz, n_modes=3)
        loss_nz = measure_eval_loss(model, layer_idx, W_q_nz_t, W_k_nz_t, eval_input, eval_target)

        results_noise.append({
            "frac": frac,
            "actual_frac_q": actual_frac_q_nz,
            "actual_frac_k": actual_frac_k_nz,
            "energy_concentration": conc_nz,
            "mode_alignment_top3": align_nz,
            "eval_loss": loss_nz,
            "loss_delta": loss_nz - baseline_loss,
        })

        # ── Strategy C: Random (average N_RANDOM_TRIALS trials) ──
        rand_conc = []
        rand_align = [[], [], []]
        rand_loss = []
        for trial in range(N_RANDOM_TRIALS):
            W_q_rnd = apply_random_zeros(W_q.astype(np.float32), frac, rng)
            W_k_rnd = apply_random_zeros(W_k.astype(np.float32), frac, rng)
            W_q_rnd_t = to_ternary_with_gamma(W_q_rnd)
            W_k_rnd_t = to_ternary_with_gamma(W_k_rnd)

            M_rnd = (W_q_rnd_t.T @ W_k_rnd_t).astype(np.float64)
            U_rnd, s_rnd, _ = np.linalg.svd(M_rnd, full_matrices=False)

            rand_conc.append(energy_concentration(s_rnd, K))
            aligns = mode_alignment(U_f, U_rnd, n_modes=3)
            for m_i in range(3):
                rand_align[m_i].append(aligns[m_i])
            loss_rnd = measure_eval_loss(model, layer_idx, W_q_rnd_t, W_k_rnd_t, eval_input, eval_target)
            rand_loss.append(loss_rnd)

        mean_loss_rnd = float(np.mean(rand_loss))
        results_rand.append({
            "frac": frac,
            "energy_concentration": float(np.mean(rand_conc)),
            "energy_concentration_std": float(np.std(rand_conc)),
            "mode_alignment_top3": [float(np.mean(rand_align[m])) for m in range(3)],
            "eval_loss": mean_loss_rnd,
            "eval_loss_std": float(np.std(rand_loss)),
            "loss_delta": mean_loss_rnd - baseline_loss,
        })

    return {
        "layer": layer_idx,
        "float_K": K,
        "float_energy_at_K": float(energy_float),
        "float_singular_values_top10": s_f[:10].tolist(),
        "noise_score_q_stats": {
            "mean": float(noise_q.mean()),
            "std": float(noise_q.std()),
            "max": float(noise_q.max()),
            "median": float(np.median(noise_q)),
        },
        "noise_score_k_stats": {
            "mean": float(noise_k.mean()),
            "std": float(noise_k.std()),
            "max": float(noise_k.max()),
            "median": float(np.median(noise_k)),
        },
        "magnitude": results_mag,
        "mspace_noise": results_noise,
        "random": results_rand,
    }


# ══════════════════════════════════════════════════════════════════════
# Table printing
# ══════════════════════════════════════════════════════════════════════

def print_layer_table(layer_result: dict):
    """Print a formatted table for one layer's sweep results."""
    layer = layer_result["layer"]
    K = layer_result["float_K"]
    e0 = layer_result["float_energy_at_K"]

    print(f"\n{'─'*92}")
    print(f"  LAYER {layer}  │  Float32 K={K} modes capture {e0*100:.1f}% energy")
    print(f"{'─'*92}")
    print(f"  {'Strategy':<12} {'Zero%':>6} {'E_conc':>8} {'Align0':>7} {'Align1':>7} "
          f"{'Align2':>7} {'Eval Loss':>10} {'ΔLoss':>9}")
    print(f"  {'─'*88}")

    fracs = ZERO_FRACTIONS

    for i, frac in enumerate(fracs):
        for strategy, label in [
            ("magnitude",    "Magnitude"),
            ("mspace_noise", "M-noise  "),
            ("random",       "Random   "),
        ]:
            r = layer_result[strategy][i]
            ec = r["energy_concentration"]
            am = r["mode_alignment_top3"]
            al = [am[j] if j < len(am) else float("nan") for j in range(3)]
            ev = r["eval_loss"]
            dl = r["loss_delta"]

            # Indicator: is this better than random?
            marker = ""
            if strategy == "mspace_noise" and i > 0:
                rand_r = layer_result["random"][i]
                if ec > rand_r["energy_concentration"] + 0.005:
                    marker = " ✓"
            if strategy == "magnitude" and i > 0:
                rand_r = layer_result["random"][i]
                if ec > rand_r["energy_concentration"] + 0.005:
                    marker = " ✓"

            # Only print strategy name on first row per zero-fraction group
            if strategy == "magnitude":
                print(f"  {'':<12} {frac*100:>5.0f}%", end="")
                print()
            print(f"  {label:<12} {'':>6} {ec*100:>7.1f}% {al[0]:>7.3f} {al[1]:>7.3f} "
                  f"{al[2]:>7.3f} {ev:>10.4f} {dl:>+9.4f}{marker}")

        if i < len(fracs) - 1:
            print()


def print_layer_table_compact(layer_result: dict):
    """Print a compact comparison table (one row per zero-fraction, three strategies side-by-side)."""
    layer = layer_result["layer"]
    K = layer_result["float_K"]
    e0 = layer_result["float_energy_at_K"]

    print(f"\n  LAYER {layer}  │  Float32 K={K} → {e0*100:.1f}% energy in top-{K} modes")
    print(f"  {'Zero%':>5} │"
          f" {'Mag Econ':>8} {'Mag ΔL':>8} │"
          f" {'Msp Econ':>8} {'Msp ΔL':>8} │"
          f" {'Rnd Econ':>8} {'Rnd ΔL':>8}")
    print(f"  {'─'*64}")

    for i, frac in enumerate(ZERO_FRACTIONS):
        m = layer_result["magnitude"][i]
        n = layer_result["mspace_noise"][i]
        r = layer_result["random"][i]

        # Mark rows where mspace outperforms random on energy concentration
        msp_beats_rnd = n["energy_concentration"] > r["energy_concentration"] + 0.005
        mag_beats_rnd = m["energy_concentration"] > r["energy_concentration"] + 0.005
        flag = "◀" if msp_beats_rnd else ""

        print(f"  {frac*100:>5.0f}% │"
              f" {m['energy_concentration']*100:>7.1f}% {m['loss_delta']:>+8.4f} │"
              f" {n['energy_concentration']*100:>7.1f}% {n['loss_delta']:>+8.4f} │"
              f" {r['energy_concentration']*100:>7.1f}% {r['loss_delta']:>+8.4f} {flag}")


# ══════════════════════════════════════════════════════════════════════
# Main experiment
# ══════════════════════════════════════════════════════════════════════

def run_experiment():
    t0 = time.time()
    print("=" * 78)
    print("  M-SPACE NOISE ZERO PLACEMENT — Micro Model Experiment 2")
    print("=" * 78)
    print()
    print("Question: Can M-space noise scores guide zero placement to sharpen")
    print("          the ternary attention kernel back toward the float32 gem?")
    print()

    # ── Load model ──
    cfg = MicroConfig()
    model = MicroModel(cfg)

    ckpt = Path(CHECKPOINT_PATH)
    if not ckpt.exists():
        # Fallback to last step checkpoint
        fallback = Path("checkpoints/micro/step_005000/model.npz")
        if fallback.exists():
            ckpt = fallback
        else:
            raise FileNotFoundError(f"No checkpoint found at {CHECKPOINT_PATH} or fallback.")

    print(f"Loading model from {ckpt} ...")
    weights = mx.load(str(ckpt))
    model.load_weights(list(weights.items()))
    mx.eval(model.parameters())
    print(f"  {cfg.n_layers} layers, {cfg.n_heads} heads, d_model={cfg.d_model}, "
          f"d_head={cfg.d_head}, d_ff={cfg.d_ff}")
    print()

    # ── Load tokenizer and data ──
    print("Loading tokenizer (Qwen/Qwen3-0.6B) ...")
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    print("  Tokenizer ready.")
    print()

    print(f"Loading eval data from {EVAL_FILE} ...")
    eval_examples = load_examples(EVAL_FILE)
    eval_seqs = tokenize_examples(eval_examples, tokenizer, cfg.max_seq_len, cfg.eod_id)
    eval_input, eval_target = make_eval_batch(eval_seqs, cfg.max_seq_len)
    print(f"  {len(eval_examples)} examples, packed into sequence of length {eval_input.shape[1]}.")
    print()

    # ── Baseline loss (float32 model, all layers intact) ──
    print("Measuring baseline eval loss (float32 model) ...")
    # Use manual CE (without crystal loss) for fair comparison
    logits_base, _ = model(eval_input)
    mx.eval(logits_base)
    loss_base_val = nn.losses.cross_entropy(
        logits_base.reshape(-1, cfg.vocab_size),
        eval_target.reshape(-1),
    ).mean()
    mx.eval(loss_base_val)
    baseline_loss = float(loss_base_val.item())
    print(f"  Baseline eval loss (CE only): {baseline_loss:.4f}")
    print()

    # ── RNG for random strategy ──
    rng = np.random.RandomState(42)

    # ── Per-layer experiments ──
    all_results = {}
    DETAIL_LAYER = 2  # most structured layer — print verbose output

    for layer_idx in range(cfg.n_layers):
        verbose = (layer_idx == DETAIL_LAYER)
        print(f"{'='*78}")
        print(f"  Running layer {layer_idx} ...")
        if verbose:
            print(f"  (verbose output — this is the most structured layer)")
        t_layer = time.time()

        layer_result = run_layer_experiment(
            model, layer_idx, eval_input, eval_target,
            baseline_loss, rng, verbose=verbose,
        )
        all_results[str(layer_idx)] = layer_result

        print_layer_table_compact(layer_result)
        print(f"\n  Layer {layer_idx} done in {time.time() - t_layer:.1f}s")
        print()

    # ── Cross-layer summary ──
    print("=" * 78)
    print("  CROSS-LAYER SUMMARY — at 30% zero fraction")
    print("=" * 78)

    TARGET_FRAC = 0.30
    idx_30 = ZERO_FRACTIONS.index(TARGET_FRAC) if TARGET_FRAC in ZERO_FRACTIONS else None
    if idx_30 is None:
        # Find closest
        idx_30 = int(np.argmin(np.abs(np.array(ZERO_FRACTIONS) - TARGET_FRAC)))

    print(f"\n  {'Layer':>5} │ {'K':>4} │"
          f" {'Float E':>7} │"
          f" {'Mag Econ':>8} {'Mag ΔL':>8} │"
          f" {'Msp Econ':>8} {'Msp ΔL':>8} │"
          f" {'Rnd Econ':>8} {'Rnd ΔL':>8}")
    print(f"  {'─'*82}")

    for layer_idx in range(cfg.n_layers):
        lr = all_results[str(layer_idx)]
        K = lr["float_K"]
        ef = lr["float_energy_at_K"]
        m  = lr["magnitude"][idx_30]
        n  = lr["mspace_noise"][idx_30]
        r  = lr["random"][idx_30]

        msp_wins = n["energy_concentration"] > r["energy_concentration"] + 0.005
        flag = " ◀" if msp_wins else ""

        print(f"  {layer_idx:>5} │ {K:>4} │"
              f" {ef*100:>6.1f}% │"
              f" {m['energy_concentration']*100:>7.1f}% {m['loss_delta']:>+8.4f} │"
              f" {n['energy_concentration']*100:>7.1f}% {n['loss_delta']:>+8.4f} │"
              f" {r['energy_concentration']*100:>7.1f}% {r['loss_delta']:>+8.4f}{flag}")

    # ── Layer 2 detailed breakout ──
    print()
    print("=" * 78)
    print("  LAYER 2 DETAIL — Mode alignment at each zero fraction")
    print("=" * 78)
    lr2 = all_results["2"]
    print(f"\n  {'Zero%':>5} │ {'Strategy':>12} │"
          f" {'Econ':>7} │ {'Align-0':>8} {'Align-1':>8} {'Align-2':>8} │ {'ΔLoss':>8}")
    print(f"  {'─'*76}")

    for i, frac in enumerate(ZERO_FRACTIONS):
        for strat_key, strat_label in [
            ("magnitude",    "Magnitude  "),
            ("mspace_noise", "M-noise    "),
            ("random",       "Random     "),
        ]:
            r = lr2[strat_key][i]
            ec = r["energy_concentration"]
            am = r["mode_alignment_top3"]
            dl = r["loss_delta"]
            prefix = f"  {frac*100:>5.0f}% │" if strat_key == "magnitude" else "         │"
            print(f"  {frac*100:>5.0f}% │ {strat_label:<12} │"
                  f" {ec*100:>6.1f}% │"
                  f" {am[0]:>8.3f} {am[1]:>8.3f} {am[2]:>8.3f} │"
                  f" {dl:>+8.4f}")

    # ── Best operating point per layer ──
    print()
    print("=" * 78)
    print("  BEST OPERATING POINT — lowest eval loss per layer per strategy")
    print("=" * 78)
    print(f"\n  {'Layer':>5} │ {'Strategy':>12} │ {'Best Frac':>9} │ "
          f"{'Best Econ':>9} │ {'Best Loss':>10} │ {'Best ΔL':>9}")
    print(f"  {'─'*72}")

    for layer_idx in range(cfg.n_layers):
        lr = all_results[str(layer_idx)]
        for strat_key, strat_label in [
            ("magnitude",    "Magnitude  "),
            ("mspace_noise", "M-noise    "),
            ("random",       "Random     "),
        ]:
            sweep = lr[strat_key]
            losses = [r["eval_loss"] for r in sweep]
            best_i = int(np.argmin(losses))
            best_r = sweep[best_i]
            print(f"  {layer_idx:>5} │ {strat_label:<12} │ "
                  f"{ZERO_FRACTIONS[best_i]*100:>8.0f}% │ "
                  f"{best_r['energy_concentration']*100:>8.1f}% │ "
                  f"{best_r['eval_loss']:>10.4f} │ "
                  f"{best_r['loss_delta']:>+9.4f}")
        print(f"  {'─'*72}")

    # ── Elapsed ──
    elapsed = time.time() - t0
    print(f"\n  Total elapsed: {elapsed:.1f}s")

    # ── Save results ──
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "experiment": "mspace_zeros_experiment2",
        "baseline_loss": baseline_loss,
        "config": {
            "d_model": cfg.d_model,
            "n_layers": cfg.n_layers,
            "n_heads": cfg.n_heads,
            "d_head": cfg.d_head,
        },
        "zero_fractions": ZERO_FRACTIONS,
        "layers": all_results,
    }
    with open(RESULTS_PATH, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n  Results saved to {RESULTS_PATH}")


if __name__ == "__main__":
    run_experiment()
