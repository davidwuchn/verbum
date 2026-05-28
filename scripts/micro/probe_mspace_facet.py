#!/usr/bin/env python3
"""
Single-Facet Cutting — Experiment 3.

Core question: Can a COORDINATED set of sign-flips change ONE SVD mode
of the attention kernel M = W_q^T @ W_k without disturbing other modes?

Background
----------
Layer 2 of the micro model has a highly structured attention kernel:
  - Float32 rank90 = 13  (13 modes capture 90% of energy)
  - Ternary rank90 = 35  (sign-quantization blurs this to 35)
  - Mode 0 dominance: 69% of energy, σ0/σ1 = 3.51

Experiment 1 showed M-space scoring finds better flip candidates than
gradient-heat scoring.  Now we ask the deeper question: can we sculpt
the ternary M to match individual modes of the float32 target — one
facet at a time — using greedy coordinated flip selection?

Protocol for each target mode k ∈ {0, 1, 2, 3, 4}
----------------------------------------------------
1. Start from the base ternary W_q_t, W_k_t (sign-quantized float32).
2. Score every possible flip for:
     - mode_k improvement = Δ(u_k^T M v_k)
     - cross-mode damage   = Σ_{j≠k} (Δ(u_j^T M v_j))^2
     - selectivity score   = |mode_k_improvement| / sqrt(cross_damage + ε)
3. Greedily apply flips in selectivity order, up to set sizes {1,5,10,20,50}.
4. At each set size, measure:
     - Mode k energy change (% progress toward target)
     - Worst-other-mode damage (max |Δσ_j| across j ≠ k)
     - Overall Frobenius error to M_target (normalised)
     - Actual eval loss delta (flip ternary q_proj, measure CE)
5. Baselines at each set size:
     - Random flips (same count, random positions)
     - Gradient-top flips (routing score from one backward pass)
6. Global greedy: minimize overall ||M_target - M_current||_F (no facet bias).
   Tests whether global M-space optimisation beats mode-targeted optimisation.

Analytic derivation of flip effects
-------------------------------------
M = W_q_t^T @ W_k_t  (both matrices are d_out × d_in)

Flip at W_q[h, i]:
  ΔM[i_row, :] = -2 * W_q_t[h,i] * W_k_t[h,:]  (rank-1 update, row i)
  Δ(u_k^T M v_k) = -2 * W_q_t[h,i] * U_f[i,k] * (W_k_t[h,:] @ Vt_f[k,:])

  More precisely, the SVD is of M = W_q_t^T @ W_k_t  (shape d_in × d_in),
  where W_q_t has shape (d_out, d_in).  In the transpose W_q_t^T the i-th
  ROW corresponds to the i-th column of W_q_t, i.e. position index i across
  all heads.  A flip at [h, i] changes the h-th row of W_q_t, which changes
  the i-th column of W_q_t^T.  That column contributes a rank-1 update:
    ΔM = e_i (outer) (-2 * W_q_t[h,i] * W_k_t[h,:])
  So ΔM is nonzero only in row i (0-indexed) of the d_in × d_in matrix.
  u_k^T ΔM v_k = U_f[i, k] * (-2 * W_q_t[h,i]) * (W_k_t[h,:] @ Vt_f[k,:])

Flip at W_k[h, j]:
  ΔM[:, j_col] = -2 * W_k_t[h,j] * W_q_t[h,:]^T  (rank-1 update, col j)
  u_k^T ΔM v_k = (U_f[:,k] @ W_q_t[h,:]) * (-2 * W_k_t[h,j]) * Vt_f[k, j]
  = (W_q_t[h,:] @ U_f[:,k]) * (-2 * W_k_t[h,j]) * Vt_f[k, j]

License: MIT
"""

from __future__ import annotations

import json
import os
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

TARGET_LAYER   = 2          # most structured layer (rank90=13, σ0/σ1=3.51)
TOP_K_MODES    = 5          # analyse modes 0–4
FLIP_SET_SIZES = [1, 5, 10, 20, 50]
N_RANDOM_SEEDS = 5          # for random-baseline averaging
EPS            = 1e-12      # numerical guard


# ══════════════════════════════════════════════════════════════════════
# Data utilities (identical to probe_mspace.py)
# ══════════════════════════════════════════════════════════════════════

def load_compile_examples(path: str) -> list[dict]:
    examples = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(json.loads(line))
    return examples


def tokenize_examples(examples, tokenizer, max_len=256, eod_id=151643):
    sequences = []
    for ex in examples:
        text = f"{ex['input']}\n{ex['output']}"
        token_ids = tokenizer.encode(text, add_special_tokens=False)
        token_ids.append(eod_id)
        if len(token_ids) > max_len:
            token_ids = token_ids[:max_len]
        sequences.append(np.array(token_ids, dtype=np.int32))
    return sequences


def make_eval_batch(sequences, max_seq_len=256, eod_id=151643):
    """Pack all eval sequences into one fixed batch for consistent loss measurement."""
    stream = np.concatenate(sequences)
    T = min(max_seq_len, len(stream) - 1)
    input_ids = stream[:T].reshape(1, T)
    targets   = stream[1:T+1].reshape(1, T)
    return mx.array(input_ids), mx.array(targets)


# ══════════════════════════════════════════════════════════════════════
# Sign quantization
# ══════════════════════════════════════════════════════════════════════

def sign_quantize(W: np.ndarray) -> np.ndarray:
    """Binarise to ±1, resolving zeros to +1."""
    T = np.sign(W).astype(np.float64)
    T[T == 0] = 1.0
    return T


# ══════════════════════════════════════════════════════════════════════
# Per-mode flip scoring
# ══════════════════════════════════════════════════════════════════════

def score_flips_for_mode(
    W_q_t:  np.ndarray,   # (d_out, d_in) ternary ±1
    W_k_t:  np.ndarray,   # (d_out, d_in) ternary ±1
    U_f:    np.ndarray,   # (d_in, d_in) left singular vectors of M_target
    Vt_f:   np.ndarray,   # (d_in, d_in) right singular vectors (V^T)
    mode_k: int,
    n_modes_total: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Score every possible flip (in both W_q and W_k) for mode k selectivity.

    Returns
    -------
    q_mode_improvement : (d_out, d_in)  signed improvement to mode k projection
    q_cross_damage     : (d_out, d_in)  sum-of-squares damage to other modes
    k_mode_improvement : (d_out, d_in)  same for W_k flips
    k_cross_damage     : (d_out, d_in)
    """
    d_out, d_in = W_q_t.shape

    # ── Pre-compute per-head dot products for all modes at once ──
    # For W_q flip at [h, i]:
    #   Δ(u_j^T M v_j) = -2 * W_q_t[h,i] * U_f[i,j] * (W_k_t[h,:] @ Vt_f[j,:])
    #
    # Factor 1: -2 * W_q_t[h,i]  →  shape (d_out, d_in), elementwise
    # Factor 2: U_f[i, j]         →  depends on (i, j), not h
    # Factor 3: W_k_t[h,:] @ Vt_f[j,:]  →  shape (d_out, n_modes)
    #
    # Batch over all j simultaneously:
    #   proj_k_h = W_k_t @ Vt_f.T  →  (d_out, n_modes), element [h,j]

    proj_k_over_modes = W_k_t @ Vt_f[:n_modes_total].T   # (d_out, n_modes)
    # W_k_t: (d_out, d_in), Vt_f[:n_modes_total]: (n_modes, d_in)
    # result[h, j] = W_k_t[h,:] @ Vt_f[j,:]

    # For flip at W_q[h, i], mode j:
    #   delta_j = -2 * W_q_t[h,i] * U_f[i,j] * proj_k_over_modes[h,j]
    # We want, for each (h, i):
    #   delta_k  = -2 * W_q_t[h,i] * U_f[i, mode_k] * proj_k_over_modes[h, mode_k]
    #   sum_j!=k delta_j^2

    # U_f[:, mode_k]: (d_in,)  — left singular vector for mode k
    u_k = U_f[:, mode_k]  # (d_in,)
    v_k = Vt_f[mode_k, :]  # (d_in,)

    # mode_k improvement for Q flips:
    #   q_imp[h, i] = -2 * W_q_t[h,i] * u_k[i] * proj_k_over_modes[h, mode_k]
    q_imp_mode = (
        -2.0
        * W_q_t                                      # (d_out, d_in)
        * u_k[np.newaxis, :]                         # broadcast over h
        * proj_k_over_modes[:, mode_k:mode_k+1]      # (d_out, 1) broadcast over i
    )  # shape (d_out, d_in)

    # Cross-mode damage for Q flips:
    #   For mode j ≠ mode_k:
    #     delta_j[h, i]^2 = (-2 * W_q_t[h,i] * U_f[i,j] * proj_k_over_modes[h,j])^2
    #                      = 4 * U_f[i,j]^2 * proj_k_over_modes[h,j]^2
    #                          (W_q_t[h,i]^2 = 1 since ternary ±1)
    # Summed over j ≠ mode_k:
    modes_all = np.arange(n_modes_total)
    other_modes = modes_all[modes_all != mode_k]

    # U_f[:, other_modes]: (d_in, n_other)
    U_other = U_f[:, other_modes]                      # (d_in, n_other)
    proj_k_other = proj_k_over_modes[:, other_modes]   # (d_out, n_other)

    # For each (h, i): sum_j (U_f[i,j]^2 * proj_k_over_modes[h,j]^2)
    # = (U_other^2) (d_in, n_other) · (proj_k_other^2)^T (n_other, d_out)
    # → (d_in, d_out), then transpose
    U_other_sq       = U_other ** 2                    # (d_in, n_other)
    proj_other_sq    = proj_k_other ** 2               # (d_out, n_other)

    q_cross_raw = U_other_sq @ proj_other_sq.T         # (d_in, d_out)
    q_cross_damage = 4.0 * q_cross_raw.T               # (d_out, d_in)

    # ── W_k flips ──
    # For flip at W_k[h, j], mode m:
    #   delta_m = -2 * W_k_t[h,j] * (W_q_t[h,:] @ U_f[:,m]) * Vt_f[m, j]
    #
    # Batch factor:  (W_q_t @ U_f)  →  (d_out, n_modes), element [h,m]

    proj_q_over_modes = W_q_t @ U_f[:, :n_modes_total]   # (d_out, n_modes)
    # element [h, m] = W_q_t[h,:] @ U_f[:,m]

    # mode_k improvement for K flips:
    #   k_imp[h, j] = -2 * W_k_t[h,j] * proj_q_over_modes[h, mode_k] * v_k[j]
    k_imp_mode = (
        -2.0
        * W_k_t                                          # (d_out, d_in)
        * proj_q_over_modes[:, mode_k:mode_k+1]         # (d_out, 1) broadcast
        * v_k[np.newaxis, :]                             # (1, d_in) broadcast over h
    )  # shape (d_out, d_in)

    # Cross-mode damage for K flips:
    #   For mode m ≠ mode_k:
    #     delta_m[h,j]^2 = 4 * proj_q_over_modes[h,m]^2 * Vt_f[m,j]^2
    # Sum over m ≠ mode_k:
    V_other = Vt_f[other_modes, :]                      # (n_other, d_in)
    proj_q_other = proj_q_over_modes[:, other_modes]    # (d_out, n_other)

    V_other_sq    = V_other ** 2                        # (n_other, d_in)
    proj_q_sq     = proj_q_other ** 2                   # (d_out, n_other)

    k_cross_raw    = proj_q_sq @ V_other_sq             # (d_out, d_in)
    k_cross_damage = 4.0 * k_cross_raw                  # (d_out, d_in)

    return q_imp_mode, q_cross_damage, k_imp_mode, k_cross_damage


def selectivity_scores(
    imp:    np.ndarray,   # (d_out, d_in) mode improvement (signed)
    cross:  np.ndarray,   # (d_out, d_in) cross-mode damage (positive)
) -> np.ndarray:
    """Selectivity = |improvement| / sqrt(cross_damage + ε).

    Favours flips that improve the target mode with minimal collateral.
    """
    return np.abs(imp) / np.sqrt(cross + EPS)


# ══════════════════════════════════════════════════════════════════════
# Global M-space score (from probe_mspace.py)
# ══════════════════════════════════════════════════════════════════════

def compute_global_mspace_scores(
    W_q_t: np.ndarray,
    W_k_t: np.ndarray,
    R: np.ndarray,         # M_target_norm - M_current_norm (residual)
) -> tuple[np.ndarray, np.ndarray]:
    """Global Frobenius improvement scores for Q and K flips."""
    # Q score: -4 * W_q_t[h,i] * dot(R[i,:], W_k_t[h,:])
    inner_q = (R @ W_k_t.T).T     # (d_out, d_in): inner[h,i] = R[i,:] · W_k_t[h,:]
    scores_q = -4.0 * W_q_t * inner_q

    # K score: -4 * W_k_t[h,j] * dot(R[:,j], W_q_t[h,:])
    inner_k = (R.T @ W_q_t.T).T   # (d_out, d_in): inner[h,j] = R[:,j] · W_q_t[h,:]
    scores_k = -4.0 * W_k_t * inner_k

    return scores_q, scores_k


def normalize_frobenius(M: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(M, 'fro')
    if norm < EPS:
        return M
    return M / norm


# ══════════════════════════════════════════════════════════════════════
# Gradient-based flip scoring
# ══════════════════════════════════════════════════════════════════════

def compute_gradient_scores(
    model: MicroModel,
    input_ids: mx.array,
    targets: mx.array,
    layer_idx: int,
) -> tuple[np.ndarray, np.ndarray, float]:
    """One backward pass → routing scores for Q and K at layer_idx.

    Returns (grad_q, grad_k, train_loss).
    Routing score = -grad * sign(W) > 0 when gradient wants a sign flip.
    """
    def loss_fn(m, x, t):
        _, loss = m(x, t)
        return loss

    loss_val, grads = nn.value_and_grad(model, loss_fn)(model, input_ids, targets)
    mx.eval(loss_val, grads)

    block_grads = grads["blocks"][layer_idx]
    grad_q = np.array(block_grads["attn"]["q_proj"]["weight"])
    grad_k = np.array(block_grads["attn"]["k_proj"]["weight"])

    W_q = np.array(model.blocks[layer_idx].attn.q_proj.weight)
    W_k = np.array(model.blocks[layer_idx].attn.k_proj.weight)

    sign_q = np.sign(W_q); sign_q[sign_q == 0] = 1
    sign_k = np.sign(W_k); sign_k[sign_k == 0] = 1

    routing_q = -grad_q * sign_q
    routing_k = -grad_k * sign_k

    return routing_q, routing_k, float(loss_val.item())


# ══════════════════════════════════════════════════════════════════════
# Mode energy measurement helpers
# ══════════════════════════════════════════════════════════════════════

def mode_projections(M: np.ndarray, U_f: np.ndarray, Vt_f: np.ndarray,
                     n_modes: int) -> np.ndarray:
    """Return projections u_k^T M v_k for k = 0..n_modes-1."""
    projs = np.zeros(n_modes)
    for k in range(n_modes):
        projs[k] = U_f[:, k] @ M @ Vt_f[k, :]
    return projs


def frob_error_normalized(M_cur: np.ndarray, M_tgt: np.ndarray) -> float:
    """Normalised Frobenius distance: ||M_cur - M_tgt||_F / ||M_tgt||_F."""
    diff = M_cur - M_tgt
    denom = np.linalg.norm(M_tgt, 'fro')
    if denom < EPS:
        return float(np.linalg.norm(diff, 'fro'))
    return float(np.linalg.norm(diff, 'fro') / denom)


# ══════════════════════════════════════════════════════════════════════
# Loss measurement (apply ternary weight to model, measure eval loss)
# ══════════════════════════════════════════════════════════════════════

def measure_loss_with_ternary_q(
    model: MicroModel,
    layer_idx: int,
    W_q_modified: np.ndarray,    # (d_out, d_in) ternary ±1
    eval_input: mx.array,
    eval_target: mx.array,
    baseline_loss: float,
    gamma: float = 1.0,
) -> float:
    """Temporarily apply W_q_modified * gamma to q_proj.weight, measure loss delta.

    Returns loss_delta = measured_loss - baseline_loss.
    """
    attn = model.blocks[layer_idx].attn
    W_orig = np.array(attn.q_proj.weight)

    attn.q_proj.weight = mx.array((W_q_modified * gamma).astype(np.float32))
    mx.eval(attn.q_proj.weight)

    _, loss_val = model(eval_input, eval_target)
    mx.eval(loss_val)
    loss = float(loss_val.item())

    # Restore
    attn.q_proj.weight = mx.array(W_orig)
    mx.eval(attn.q_proj.weight)

    return loss - baseline_loss


# ══════════════════════════════════════════════════════════════════════
# Greedy coordinated flip selection
# ══════════════════════════════════════════════════════════════════════

def greedy_facet_flips(
    W_q_t_init: np.ndarray,
    W_k_t_init: np.ndarray,
    U_f: np.ndarray,
    S_f: np.ndarray,
    Vt_f: np.ndarray,
    M_target: np.ndarray,
    mode_k: int,
    max_flips: int,
    strategy: str = "facet",   # "facet" | "global"
    n_modes_total: int = None,
) -> tuple[list[tuple], list[tuple[str, int, int]]]:
    """
    Greedily select up to max_flips single-bit changes to W_q_t or W_k_t
    that improve mode k (or global M) with minimum cross-mode damage.

    At each step:
      1. Score all remaining candidates under current W_q_t, W_k_t.
      2. Pick the highest-scoring candidate.
      3. Apply the flip in-place.
      4. Repeat.

    Returns
    -------
    snapshots : list of dicts (one entry per flip applied):
        {
          "n_flips":        int,
          "proj_k":         float,   projection onto mode k
          "target_proj_k":  float,   σ_k from M_target SVD
          "mode_k_pct":     float,   % progress toward target projection
          "other_mode_damage": float, max |Δproj_j| for j ≠ mode_k from base
          "frob_error":     float,   normalised Frobenius vs M_target
          "M_current":      np.ndarray  (returned only at FLIP_SET_SIZES)
        }
    flip_log : list of ("q"|"k", h, i_or_j) describing what was flipped
    """
    if n_modes_total is None:
        n_modes_total = TOP_K_MODES

    W_q_t = W_q_t_init.copy()
    W_k_t = W_k_t_init.copy()

    d_out, d_in = W_q_t.shape

    # Target projection for mode k
    target_proj_k = float(S_f[mode_k])  # = u_k^T M_target v_k in the SVD

    # Base projections to compute "other-mode damage" relative to start
    M_current = W_q_t.T @ W_k_t
    base_projs = mode_projections(M_current, U_f, Vt_f, n_modes_total)

    snapshots = []
    flip_log  = []

    for flip_idx in range(max_flips):
        if strategy == "facet":
            q_imp, q_cross, k_imp, k_cross = score_flips_for_mode(
                W_q_t, W_k_t, U_f, Vt_f, mode_k, n_modes_total)

            q_sel = selectivity_scores(q_imp, q_cross)
            k_sel = selectivity_scores(k_imp, k_cross)

            # Only consider flips that actually improve mode k (positive improvement)
            q_sel_masked = np.where(q_imp > 0, q_sel, -1.0)
            k_sel_masked = np.where(k_imp > 0, k_sel, -1.0)

        else:  # global
            M_current = W_q_t.T @ W_k_t
            M_target_n = normalize_frobenius(M_target)
            M_current_n = normalize_frobenius(M_current)
            R = M_target_n - M_current_n
            q_sel_masked, k_sel_masked = compute_global_mspace_scores(W_q_t, W_k_t, R)
            q_sel = q_sel_masked
            k_sel = k_sel_masked

        best_q = q_sel_masked.max() if q_sel_masked.max() > -1.0 else float('-inf')
        best_k = k_sel_masked.max() if k_sel_masked.max() > -1.0 else float('-inf')

        if best_q >= best_k:
            h, i = np.unravel_index(np.argmax(q_sel_masked), q_sel_masked.shape)
            W_q_t[h, i] = -W_q_t[h, i]
            flip_log.append(("q", int(h), int(i)))
        else:
            h, j = np.unravel_index(np.argmax(k_sel_masked), k_sel_masked.shape)
            W_k_t[h, j] = -W_k_t[h, j]
            flip_log.append(("k", int(h), int(j)))

        # Record snapshot at desired set sizes
        n_applied = flip_idx + 1
        if n_applied in FLIP_SET_SIZES:
            M_current = W_q_t.T @ W_k_t
            cur_projs = mode_projections(M_current, U_f, Vt_f, n_modes_total)
            proj_k = float(cur_projs[mode_k])

            # % progress: how much of the gap (target - base) has been closed?
            gap = target_proj_k - float(base_projs[mode_k])
            improvement = proj_k - float(base_projs[mode_k])
            pct = (improvement / gap * 100.0) if abs(gap) > EPS else 0.0

            # Other-mode damage: max absolute change across non-k modes
            other_modes = [j for j in range(n_modes_total) if j != mode_k]
            damage = max(
                abs(float(cur_projs[j]) - float(base_projs[j]))
                for j in other_modes
            ) if other_modes else 0.0

            fe = frob_error_normalized(M_current, M_target)

            snapshots.append({
                "n_flips": n_applied,
                "proj_k": proj_k,
                "target_proj_k": target_proj_k,
                "base_proj_k": float(base_projs[mode_k]),
                "mode_k_pct": pct,
                "other_mode_damage": damage,
                "frob_error": fe,
                # Store modified W_q_t for loss measurement (caller decides)
                "_W_q_t": W_q_t.copy(),
                "_W_k_t": W_k_t.copy(),
            })

    return snapshots, flip_log


def random_flips_snapshots(
    W_q_t_init: np.ndarray,
    W_k_t_init: np.ndarray,
    U_f: np.ndarray,
    S_f: np.ndarray,
    Vt_f: np.ndarray,
    M_target: np.ndarray,
    mode_k: int,
    max_flips: int,
    rng: np.random.RandomState,
    n_modes_total: int = None,
) -> list[dict]:
    """Apply random flips, return snapshots at FLIP_SET_SIZES."""
    if n_modes_total is None:
        n_modes_total = TOP_K_MODES

    W_q_t = W_q_t_init.copy()
    W_k_t = W_k_t_init.copy()
    d_out, d_in = W_q_t.shape
    n_total = 2 * d_out * d_in

    target_proj_k = float(S_f[mode_k])
    M_base = W_q_t.T @ W_k_t
    base_projs = mode_projections(M_base, U_f, Vt_f, n_modes_total)

    # Sample positions without replacement
    perm = rng.permutation(n_total)
    snapshots = []

    for flip_idx in range(max_flips):
        pos = perm[flip_idx]
        if pos < d_out * d_in:
            h, i = pos // d_in, pos % d_in
            W_q_t[h, i] = -W_q_t[h, i]
        else:
            pos2 = pos - d_out * d_in
            h, j = pos2 // d_in, pos2 % d_in
            W_k_t[h, j] = -W_k_t[h, j]

        n_applied = flip_idx + 1
        if n_applied in FLIP_SET_SIZES:
            M_current = W_q_t.T @ W_k_t
            cur_projs = mode_projections(M_current, U_f, Vt_f, n_modes_total)
            proj_k = float(cur_projs[mode_k])
            gap = target_proj_k - float(base_projs[mode_k])
            improvement = proj_k - float(base_projs[mode_k])
            pct = (improvement / gap * 100.0) if abs(gap) > EPS else 0.0
            other_modes = [j for j in range(n_modes_total) if j != mode_k]
            damage = max(
                abs(float(cur_projs[j]) - float(base_projs[j]))
                for j in other_modes
            ) if other_modes else 0.0
            fe = frob_error_normalized(M_current, M_target)
            snapshots.append({
                "n_flips": n_applied,
                "proj_k": proj_k,
                "target_proj_k": target_proj_k,
                "base_proj_k": float(base_projs[mode_k]),
                "mode_k_pct": pct,
                "other_mode_damage": damage,
                "frob_error": fe,
                "_W_q_t": W_q_t.copy(),
            })

    return snapshots


def gradient_top_snapshots(
    W_q_t_init: np.ndarray,
    W_k_t_init: np.ndarray,
    U_f: np.ndarray,
    S_f: np.ndarray,
    Vt_f: np.ndarray,
    M_target: np.ndarray,
    mode_k: int,
    grad_q: np.ndarray,
    grad_k: np.ndarray,
    max_flips: int,
    n_modes_total: int = None,
) -> list[dict]:
    """Apply top-gradient-score flips (precomputed scores), snapshots at FLIP_SET_SIZES."""
    if n_modes_total is None:
        n_modes_total = TOP_K_MODES

    d_out, d_in = W_q_t_init.shape

    # Rank all gradient positions globally (Q and K combined)
    flat_q = grad_q.flatten()
    flat_k = grad_k.flatten()
    all_scores = np.concatenate([flat_q, flat_k])
    sorted_idx = np.argsort(-all_scores)  # descending

    W_q_t = W_q_t_init.copy()
    W_k_t = W_k_t_init.copy()

    target_proj_k = float(S_f[mode_k])
    M_base = W_q_t.T @ W_k_t
    base_projs = mode_projections(M_base, U_f, Vt_f, n_modes_total)

    snapshots = []
    applied = 0

    for idx in sorted_idx:
        if applied >= max_flips:
            break
        if idx < d_out * d_in:
            h, i = idx // d_in, idx % d_in
            W_q_t[h, i] = -W_q_t[h, i]
        else:
            pos2 = idx - d_out * d_in
            h, j = pos2 // d_in, pos2 % d_in
            W_k_t[h, j] = -W_k_t[h, j]
        applied += 1

        if applied in FLIP_SET_SIZES:
            M_current = W_q_t.T @ W_k_t
            cur_projs = mode_projections(M_current, U_f, Vt_f, n_modes_total)
            proj_k = float(cur_projs[mode_k])
            gap = target_proj_k - float(base_projs[mode_k])
            improvement = proj_k - float(base_projs[mode_k])
            pct = (improvement / gap * 100.0) if abs(gap) > EPS else 0.0
            other_modes = [j for j in range(n_modes_total) if j != mode_k]
            damage = max(
                abs(float(cur_projs[j]) - float(base_projs[j]))
                for j in other_modes
            ) if other_modes else 0.0
            fe = frob_error_normalized(M_current, M_target)
            snapshots.append({
                "n_flips": applied,
                "proj_k": proj_k,
                "target_proj_k": target_proj_k,
                "base_proj_k": float(base_projs[mode_k]),
                "mode_k_pct": pct,
                "other_mode_damage": damage,
                "frob_error": fe,
                "_W_q_t": W_q_t.copy(),
            })

    return snapshots


# ══════════════════════════════════════════════════════════════════════
# Pretty printing helpers
# ══════════════════════════════════════════════════════════════════════

def bar(pct: float, width: int = 20, fill: str = "█") -> str:
    """ASCII progress bar for a percentage value (can be negative)."""
    pct_clamp = max(-100.0, min(100.0, pct))
    filled = int(abs(pct_clamp) / 100.0 * width)
    sign = "+" if pct_clamp >= 0 else "-"
    return f"{sign}[{fill * filled}{' ' * (width - filled)}] {pct:+6.1f}%"


def print_snapshot_table(
    method: str,
    snapshots: list[dict],
    loss_deltas: list[float],
    target_proj_k: float,
) -> None:
    print(f"\n    {method}:")
    print(f"    {'N':>4} │ {'mode_k_proj':>11} {'target':>8} │ "
          f"{'mode_k%':>8} │ {'max_dmg':>8} │ {'frob_err':>9} │ {'Δloss':>8}")
    print("    " + "─" * 76)
    for snap, dl in zip(snapshots, loss_deltas):
        n = snap["n_flips"]
        pk = snap["proj_k"]
        tpk = snap["target_proj_k"]
        pct = snap["mode_k_pct"]
        dmg = snap["other_mode_damage"]
        fe  = snap["frob_error"]
        print(f"    {n:>4} │ {pk:>11.4f} {tpk:>8.4f} │ "
              f"{pct:>+8.1f}% │ {dmg:>8.4f} │ {fe:>9.6f} │ {dl:>+8.5f}")


# ══════════════════════════════════════════════════════════════════════
# Main experiment
# ══════════════════════════════════════════════════════════════════════

def run_experiment():
    t0 = time.time()

    print("=" * 72)
    print("SINGLE-FACET CUTTING — Experiment 3")
    print("Can coordinated flips change ONE mode of M without disturbing others?")
    print("=" * 72)
    print()

    # ── Load model ──
    cfg = MicroConfig()
    model = MicroModel(cfg)

    ckpt_path = Path("checkpoints/micro/final/model.npz")
    if not ckpt_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {ckpt_path}")
    print(f"Loading model from {ckpt_path}")
    weights = mx.load(str(ckpt_path))
    model.load_weights(list(weights.items()))
    mx.eval(model.parameters())
    print(f"  {cfg.n_layers} layers, {cfg.n_heads} heads, "
          f"d_model={cfg.d_model}, d_head={cfg.d_head}")

    # ── Load data & tokenizer ──
    from transformers import AutoTokenizer
    print("\nLoading tokenizer and eval data...")
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")

    eval_examples  = load_compile_examples(cfg.eval_file)
    train_examples = load_compile_examples(cfg.train_file)
    eval_seqs  = tokenize_examples(eval_examples,  tokenizer, cfg.max_seq_len, cfg.eod_id)
    train_seqs = tokenize_examples(train_examples, tokenizer, cfg.max_seq_len, cfg.eod_id)

    eval_input, eval_target = make_eval_batch(eval_seqs, cfg.max_seq_len, cfg.eod_id)

    # Gradient batch: 8 random train windows
    rng_global = np.random.RandomState(42)
    all_train = np.concatenate(train_seqs)
    train_ins, train_tgts = [], []
    for _ in range(8):
        start = rng_global.randint(0, len(all_train) - cfg.max_seq_len - 1)
        chunk = all_train[start:start + cfg.max_seq_len + 1]
        train_ins.append(chunk[:cfg.max_seq_len])
        train_tgts.append(chunk[1:cfg.max_seq_len + 1])
    grad_input  = mx.array(np.stack(train_ins))
    grad_target = mx.array(np.stack(train_tgts))

    # ── Baseline loss ──
    _, bl_val = model(eval_input, eval_target)
    mx.eval(bl_val)
    baseline_loss = float(bl_val.item())
    print(f"  Baseline eval loss: {baseline_loss:.4f}")

    # ── Focus on layer 2 ──
    layer_idx = TARGET_LAYER
    print(f"\n{'='*72}")
    print(f"TARGET: Layer {layer_idx}  (rank90_float=13, σ0/σ1=3.51, 69% mode-0 energy)")
    print(f"{'='*72}")

    block = model.blocks[layer_idx]
    W_q_f = np.array(block.attn.q_proj.weight).astype(np.float64)  # (128,128) float
    W_k_f = np.array(block.attn.k_proj.weight).astype(np.float64)

    # Sign-quantize
    W_q_t = sign_quantize(W_q_f)
    W_k_t = sign_quantize(W_k_f)

    # ── Compute attention kernels ──
    M_target  = W_q_f.T @ W_k_f          # float32 gem   (d_in × d_in)
    M_current = W_q_t.T @ W_k_t          # ternary rough stone

    # ── SVD of M_target (defines the facets) ──
    print("\nComputing SVD of M_target...")
    U_f, S_f, Vt_f = np.linalg.svd(M_target, full_matrices=False)
    # U_f : (d_in, d_in), S_f : (d_in,), Vt_f : (d_in, d_in)
    # Note: U_f columns = left singular vectors,  Vt_f rows = right singular vectors

    total_energy = (S_f**2).sum()
    cum_energy = np.cumsum(S_f**2) / total_energy

    print(f"  M_target   shape: {M_target.shape}")
    print(f"  Float32 rank90  : {int(np.searchsorted(cum_energy, 0.90)+1)}")
    print(f"  Singular values (top 10): {np.array2string(S_f[:10], precision=2, separator=', ')}")
    print(f"  Mode energies   (top 5) : "
          f"{', '.join(f'{(S_f[k]**2/total_energy)*100:.1f}%' for k in range(5))}")
    print(f"  σ0/σ1 ratio     : {S_f[0]/S_f[1]:.3f}")

    U_c, S_c, Vt_c = np.linalg.svd(M_current, full_matrices=False)
    print(f"\n  Ternary M_current:")
    print(f"    Singular values (top 10): "
          f"{np.array2string(S_c[:10], precision=2, separator=', ')}")

    # Base M-space projections
    base_projs = mode_projections(M_current, U_f, Vt_f, TOP_K_MODES)
    target_projs = S_f[:TOP_K_MODES]  # u_k^T M_target v_k = σ_k by SVD construction

    print(f"\n  Mode projections (u_k^T M v_k):")
    print(f"  {'Mode':>4} │ {'Target σk':>10} │ {'Current':>10} │ {'Gap':>10} │ {'Energy%':>8}")
    print("  " + "─" * 52)
    for k in range(TOP_K_MODES):
        gap = target_projs[k] - base_projs[k]
        epct = (S_f[k]**2 / total_energy) * 100
        print(f"  {k:>4} │ {target_projs[k]:>10.4f} │ {base_projs[k]:>10.4f} │ "
              f"{gap:>+10.4f} │ {epct:>7.1f}%")

    base_frob = frob_error_normalized(M_current, M_target)
    print(f"\n  Normalised Frobenius error (ternary vs float): {base_frob:.6f}")

    # ── Gradient scores (one backward pass) ──
    print("\nComputing gradient scores (one backward pass)...")
    grad_q, grad_k, train_loss = compute_gradient_scores(
        model, grad_input, grad_target, layer_idx)
    print(f"  Train loss: {train_loss:.4f}")

    # ══════════════════════════════════════════════════════════════════
    # Per-mode experiments
    # ══════════════════════════════════════════════════════════════════

    results = {
        "config": {
            "target_layer": TARGET_LAYER,
            "top_k_modes": TOP_K_MODES,
            "flip_set_sizes": FLIP_SET_SIZES,
            "n_random_seeds": N_RANDOM_SEEDS,
        },
        "baseline_loss": baseline_loss,
        "train_loss": train_loss,
        "base_frob_error": base_frob,
        "M_target_singular_values": S_f[:20].tolist(),
        "base_mode_projections": base_projs.tolist(),
        "target_mode_projections": target_projs.tolist(),
        "modes": {},
        "global_greedy": {},
    }

    max_set = max(FLIP_SET_SIZES)

    for mode_k in range(TOP_K_MODES):
        print(f"\n{'─'*72}")
        print(f"MODE {mode_k}  (σ_{mode_k} = {S_f[mode_k]:.4f}, "
              f"{(S_f[mode_k]**2/total_energy)*100:.1f}% energy)")
        print(f"  Gap to close: {target_projs[mode_k] - base_projs[mode_k]:+.4f}")
        print(f"{'─'*72}")

        mode_results = {"mode_k": mode_k, "strategies": {}}

        # ── 1. Facet greedy (selectivity-scored) ──
        print(f"\n  [1/4] Facet-greedy (mode-{mode_k} selectivity scoring)...")
        t1 = time.time()
        facet_snaps, facet_log = greedy_facet_flips(
            W_q_t, W_k_t, U_f, S_f, Vt_f, M_target,
            mode_k, max_set, strategy="facet",
            n_modes_total=TOP_K_MODES,
        )
        print(f"    {len(facet_log)} flips computed in {time.time()-t1:.1f}s")

        # Measure eval loss for each snapshot
        facet_loss_deltas = []
        for snap in facet_snaps:
            dl = measure_loss_with_ternary_q(
                model, layer_idx, snap["_W_q_t"],
                eval_input, eval_target, baseline_loss)
            facet_loss_deltas.append(dl)

        # ── 2. Global greedy ──
        print(f"\n  [2/4] Global M-space greedy (Frobenius minimisation)...")
        t2 = time.time()
        global_snaps, global_log = greedy_facet_flips(
            W_q_t, W_k_t, U_f, S_f, Vt_f, M_target,
            mode_k, max_set, strategy="global",
            n_modes_total=TOP_K_MODES,
        )
        print(f"    {len(global_log)} flips computed in {time.time()-t2:.1f}s")

        global_loss_deltas = []
        for snap in global_snaps:
            dl = measure_loss_with_ternary_q(
                model, layer_idx, snap["_W_q_t"],
                eval_input, eval_target, baseline_loss)
            global_loss_deltas.append(dl)

        # ── 3. Random baseline (averaged over N_RANDOM_SEEDS) ──
        print(f"\n  [3/4] Random baseline ({N_RANDOM_SEEDS} seeds)...")
        random_snaps_all = []
        for seed in range(N_RANDOM_SEEDS):
            rng_seed = np.random.RandomState(1000 + seed)
            rsnaps = random_flips_snapshots(
                W_q_t, W_k_t, U_f, S_f, Vt_f, M_target,
                mode_k, max_set, rng_seed,
                n_modes_total=TOP_K_MODES,
            )
            random_snaps_all.append(rsnaps)

        # Average over seeds at each set size
        rand_avg_snaps = []
        rand_avg_losses = []
        for si, n_flips in enumerate(FLIP_SET_SIZES):
            snaps_at_n = [seed_snaps[si] for seed_snaps in random_snaps_all]
            avg_pct   = np.mean([s["mode_k_pct"] for s in snaps_at_n])
            avg_dmg   = np.mean([s["other_mode_damage"] for s in snaps_at_n])
            avg_frob  = np.mean([s["frob_error"] for s in snaps_at_n])
            avg_proj  = np.mean([s["proj_k"] for s in snaps_at_n])

            # Measure loss for first seed only (representative, saves time)
            dl = measure_loss_with_ternary_q(
                model, layer_idx, snaps_at_n[0]["_W_q_t"],
                eval_input, eval_target, baseline_loss)

            rand_avg_snaps.append({
                "n_flips": n_flips,
                "proj_k": avg_proj,
                "target_proj_k": target_projs[mode_k],
                "base_proj_k": base_projs[mode_k],
                "mode_k_pct": avg_pct,
                "other_mode_damage": avg_dmg,
                "frob_error": avg_frob,
            })
            rand_avg_losses.append(dl)

        # ── 4. Gradient-top baseline ──
        print(f"\n  [4/4] Gradient-top baseline...")
        grad_snaps = gradient_top_snapshots(
            W_q_t, W_k_t, U_f, S_f, Vt_f, M_target,
            mode_k, grad_q, grad_k, max_set,
            n_modes_total=TOP_K_MODES,
        )
        grad_loss_deltas = []
        for snap in grad_snaps:
            dl = measure_loss_with_ternary_q(
                model, layer_idx, snap["_W_q_t"],
                eval_input, eval_target, baseline_loss)
            grad_loss_deltas.append(dl)

        # ── Print results for this mode ──
        print(f"\n  Results for mode {mode_k} (σ_{mode_k}={S_f[mode_k]:.4f}, "
              f"target_proj={target_projs[mode_k]:.4f}, "
              f"base_proj={base_projs[mode_k]:.4f}):")

        print_snapshot_table(
            f"Facet-greedy (mode-{mode_k} selectivity)",
            facet_snaps, facet_loss_deltas, target_projs[mode_k])
        print_snapshot_table(
            "Global M-space greedy",
            global_snaps, global_loss_deltas, target_projs[mode_k])
        print_snapshot_table(
            f"Random (avg over {N_RANDOM_SEEDS} seeds)",
            rand_avg_snaps, rand_avg_losses, target_projs[mode_k])
        print_snapshot_table(
            "Gradient-top",
            grad_snaps, grad_loss_deltas, target_projs[mode_k])

        # Summary comparison at n=50
        def snap_at(snaps, n):
            for s in snaps:
                if s["n_flips"] == n:
                    return s
            return None

        n_compare = FLIP_SET_SIZES[-1]
        s_f50 = snap_at(facet_snaps,    n_compare)
        s_g50 = snap_at(global_snaps,   n_compare)
        s_r50 = snap_at(rand_avg_snaps, n_compare)
        s_gr50 = snap_at(grad_snaps,    n_compare)

        if s_f50 and s_g50 and s_r50 and s_gr50:
            print(f"\n  ── Summary at n={n_compare} flips ──")
            print(f"  {'Strategy':>26} │ {'mode_k%':>8} │ {'max_dmg':>8} │ "
                  f"{'frob_err':>9} │ {'Δloss':>8}")
            print("  " + "─" * 72)
            for name, snap, dl in [
                (f"Facet-greedy (mode {mode_k})", s_f50,
                 facet_loss_deltas[-1]),
                ("Global M-space greedy",  s_g50,  global_loss_deltas[-1]),
                ("Random",                 s_r50,  rand_avg_losses[-1]),
                ("Gradient-top",           s_gr50, grad_loss_deltas[-1]),
            ]:
                print(f"  {name:>26} │ {snap['mode_k_pct']:>+8.1f}% │ "
                      f"{snap['other_mode_damage']:>8.4f} │ "
                      f"{snap['frob_error']:>9.6f} │ {dl:>+8.5f}")

        # ── Store serialisable results ──
        def clean_snaps(snaps, losses):
            out = []
            for snap, dl in zip(snaps, losses):
                s = {k: v for k, v in snap.items() if not k.startswith("_")}
                s["loss_delta"] = dl
                out.append(s)
            return out

        mode_results["strategies"]["facet_greedy"] = {
            "snapshots": clean_snaps(facet_snaps, facet_loss_deltas),
            "flip_log": facet_log[:n_compare],
        }
        mode_results["strategies"]["global_greedy"] = {
            "snapshots": clean_snaps(global_snaps, global_loss_deltas),
            "flip_log": global_log[:n_compare],
        }
        mode_results["strategies"]["random_avg"] = {
            "snapshots": clean_snaps(rand_avg_snaps, rand_avg_losses),
        }
        mode_results["strategies"]["gradient_top"] = {
            "snapshots": clean_snaps(grad_snaps, grad_loss_deltas),
        }

        results["modes"][str(mode_k)] = mode_results

    # ══════════════════════════════════════════════════════════════════
    # Global greedy summary (strategy comparison across all modes)
    # ══════════════════════════════════════════════════════════════════

    print(f"\n{'='*72}")
    print("GLOBAL GREEDY vs FACET GREEDY — Mode-targeting power")
    print(f"  Do facet-targeted flips win on mode accuracy AND loss?")
    print(f"{'='*72}")

    print(f"\n  At n={FLIP_SET_SIZES[-1]} flips per mode:")
    print(f"  {'Mode':>4} │ {'Facet mode_k%':>14} │ {'Global mode_k%':>15} │ "
          f"{'Facet Δloss':>12} │ {'Global Δloss':>12}")
    print("  " + "─" * 68)

    global_summary = {}
    for mode_k in range(TOP_K_MODES):
        mr = results["modes"][str(mode_k)]["strategies"]
        fs = mr["facet_greedy"]["snapshots"]
        gs = mr["global_greedy"]["snapshots"]
        fl = fs[-1]["loss_delta"] if fs else 0.0
        gl = gs[-1]["loss_delta"] if gs else 0.0
        fp = fs[-1]["mode_k_pct"] if fs else 0.0
        gp = gs[-1]["mode_k_pct"] if gs else 0.0
        print(f"  {mode_k:>4} │ {fp:>+14.1f}% │ {gp:>+15.1f}% │ "
              f"{fl:>+12.5f} │ {gl:>+12.5f}")
        global_summary[str(mode_k)] = {
            "facet_mode_pct": fp, "global_mode_pct": gp,
            "facet_loss_delta": fl, "global_loss_delta": gl,
        }
    results["global_summary"] = global_summary

    # ── Key findings ──
    print(f"\n{'='*72}")
    print("KEY FINDINGS")
    print(f"{'='*72}")

    n_last = FLIP_SET_SIZES[-1]
    facet_wins_mode = 0
    facet_wins_loss = 0
    for mode_k in range(TOP_K_MODES):
        gs = global_summary[str(mode_k)]
        if gs["facet_mode_pct"] > gs["global_mode_pct"]:
            facet_wins_mode += 1
        if gs["facet_loss_delta"] < gs["global_loss_delta"]:
            facet_wins_loss += 1

    print(f"\n  Facet > Global on mode accuracy (n={n_last}): "
          f"{facet_wins_mode}/{TOP_K_MODES} modes")
    print(f"  Facet > Global on loss improvement (n={n_last}): "
          f"{facet_wins_loss}/{TOP_K_MODES} modes")

    # Best strategy per mode at n=50
    print(f"\n  Best strategy per mode at n={n_last}:")
    print(f"  {'Mode':>4} │ {'Best mode%':>10} │ {'Strategy':>26} │ {'min damage':>10}")
    print("  " + "─" * 58)
    for mode_k in range(TOP_K_MODES):
        strategies = results["modes"][str(mode_k)]["strategies"]
        candidates = {
            "Facet":    strategies["facet_greedy"]["snapshots"][-1]
                        if strategies["facet_greedy"]["snapshots"] else None,
            "Global":   strategies["global_greedy"]["snapshots"][-1]
                        if strategies["global_greedy"]["snapshots"] else None,
            "Gradient": strategies["gradient_top"]["snapshots"][-1]
                        if strategies["gradient_top"]["snapshots"] else None,
            "Random":   strategies["random_avg"]["snapshots"][-1]
                        if strategies["random_avg"]["snapshots"] else None,
        }
        best_name = max(
            (k for k, v in candidates.items() if v is not None),
            key=lambda k: candidates[k]["mode_k_pct"]
        )
        best = candidates[best_name]
        print(f"  {mode_k:>4} │ {best['mode_k_pct']:>+10.1f}% │ "
              f"{best_name:>26} │ {best['other_mode_damage']:>10.4f}")

    # ── Elapsed ──
    elapsed = time.time() - t0
    print(f"\nElapsed: {elapsed:.1f}s")
    results["elapsed_s"] = elapsed

    # ── Save ──
    out_dir = Path("results/mspace-facet")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "summary.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")
    print("=" * 72)


if __name__ == "__main__":
    run_experiment()
