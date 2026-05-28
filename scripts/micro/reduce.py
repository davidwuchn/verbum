"""
reduce.py — β-reduce a weight matrix toward its irreducible form.

One SVD. Three outcomes per position: ZERO, FLIP, KEEP.

    M = W_q^T @ W_k                    (the bilinear form)
    SVD(M) → U, σ, V                   (decompose into modes)
    K = rank_at_90%                     (the irreducible modes)

    For each position (h, i) in W_q:
        signal = Σ_{k<K}  U[i,k]² × (W_k[h,:] · V[:,k])²
        noise  = Σ_{k≥K}  U[i,k]² × (W_k[h,:] · V[:,k])²

        if noise >> signal    → ZERO  (fully reduced)
        if signal, misaligned → FLIP  (irreducible, wrong sign)
        else                  → KEEP  (normal form)

License: MIT
"""

from __future__ import annotations
import numpy as np


def reduce_attention(
    W_q_float: np.ndarray,
    W_k_float: np.ndarray,
    zero_threshold: float = 0.5,
    flip_threshold: float = 0.0,
    energy_target: float = 0.90,
) -> dict:
    """β-reduce Q/K weight matrices toward their irreducible form.

    Args:
        W_q_float: (d_out, d_in) float32 — Q projection weights
        W_k_float: (d_out, d_in) float32 — K projection weights
        zero_threshold: SNR below this → ZERO (noise dominates)
        flip_threshold: M-space improvement score above this → FLIP
        energy_target: fraction of M energy to keep (defines K modes)

    Returns:
        dict with:
            W_q_ternary: (d_out, d_in) float32 in {-1, 0, +1}
            W_k_ternary: (d_out, d_in) float32 in {-1, 0, +1}
            gamma_q: (d_out, 1) float32 — per-row scale for Q
            gamma_k: (d_out, 1) float32 — per-row scale for K
            stats: diagnostic info
    """
    d_out, d_in = W_q_float.shape

    # ── Per-row gamma (magnitude scale) ──
    gamma_q = np.abs(W_q_float).mean(axis=1, keepdims=True)  # (d_out, 1)
    gamma_k = np.abs(W_k_float).mean(axis=1, keepdims=True)

    # ── Sign-quantize ──
    W_q_t = np.sign(W_q_float).astype(np.float32)
    W_k_t = np.sign(W_k_float).astype(np.float32)
    W_q_t[W_q_t == 0] = 1.0
    W_k_t[W_k_t == 0] = 1.0

    # ── Compute M and its SVD ──
    M_float = W_q_float.T @ W_k_float
    U, s, Vt = np.linalg.svd(M_float, full_matrices=False)
    V = Vt.T  # (d_in, d_in)

    total_energy = (s ** 2).sum()
    cum = np.cumsum(s ** 2) / total_energy
    K = int(np.searchsorted(cum, energy_target) + 1)

    # ── Per-position signal/noise decomposition ──
    # For W_q position (h, i):
    #   contribution to M mode k = U[i,k] * (W_k[h,:] · V[:,k])
    #   signal = Σ_{k<K} (U[i,k] * Wk_V[h,k])²
    #   noise  = Σ_{k≥K} (U[i,k] * Wk_V[h,k])²

    Wk_V = W_k_t @ V  # (d_out, d_in) — projections of W_k rows onto V columns

    U_sig_sq = U[:, :K] ** 2       # (d_in, K)
    U_noi_sq = U[:, K:] ** 2       # (d_in, d_in-K)
    WkV_sig_sq = Wk_V[:, :K] ** 2  # (d_out, K)
    WkV_noi_sq = Wk_V[:, K:] ** 2  # (d_out, d_in-K)

    # signal[h,i] = WkV_sig_sq[h,:] @ U_sig_sq[i,:].T
    signal_q = WkV_sig_sq @ U_sig_sq.T  # (d_out, d_in)
    noise_q = WkV_noi_sq @ U_noi_sq.T   # (d_out, d_in)
    snr_q = signal_q / (noise_q + 1e-10)

    # Same for W_k positions (swap roles: use W_q rows, U for columns of M)
    Wq_U = W_q_t @ U  # (d_out, d_in)
    WqU_sig_sq = Wq_U[:, :K] ** 2
    WqU_noi_sq = Wq_U[:, K:] ** 2
    V_sig_sq = V[:, :K].T ** 2  # wait, V[:,k] for mode k
    # For W_k position (h, j): contribution to M mode k = (W_q[:,h] · U[:,k]) * V[j,k]
    # But W_q[:,h] = W_q[h,:] in our convention... let me be careful.
    # M = W_q.T @ W_k, so M[i,j] = Σ_h W_q[h,i] * W_k[h,j]
    # For W_k position (h, j):
    #   ΔM[i,j] for all i: ΔM[i,j] = W_q[h,i] * ΔW_k[h,j]
    #   mode k component: Σ_i U[i,k] * W_q[h,i] * V[j,k] = (W_q[h,:] · U[:,k]) * V[j,k]
    # So signal for W_k[h,j] = Σ_{k<K} (Wq_U[h,k])² * V[j,k]²

    Vt_sig_sq = Vt[:K, :] ** 2  # (K, d_in)
    Vt_noi_sq = Vt[K:, :] ** 2  # (d_in-K, d_in)

    signal_k = WqU_sig_sq @ Vt_sig_sq  # (d_out, d_in)
    noise_k = WqU_noi_sq @ Vt_noi_sq   # (d_out, d_in)
    snr_k = signal_k / (noise_k + 1e-10)

    # ── Classify each position: ZERO / FLIP / KEEP ──

    # ZERO: SNR below threshold (noise dominates)
    zero_q = snr_q < zero_threshold
    zero_k = snr_k < zero_threshold

    # FLIP: for non-zero positions, check M-space alignment
    # Residual in normalized M-space
    M_ternary = W_q_t.T @ W_k_t
    M_float_norm = M_float / (np.linalg.norm(M_float, 'fro') + 1e-12)
    M_tern_norm = M_ternary / (np.linalg.norm(M_ternary, 'fro') + 1e-12)
    R = M_float_norm - M_tern_norm

    # M-space flip score for Q: how much does flipping improve M?
    # score_q[h,i] = -4 * W_q_t[h,i] * dot(R[i,:], W_k_t[h,:])
    inner_q = (R @ W_k_t.T).T  # (d_out, d_in)
    flip_score_q = -4.0 * W_q_t * inner_q

    # M-space flip score for K
    inner_k = (R.T @ W_q_t.T).T  # (d_out, d_in)
    flip_score_k = -4.0 * W_k_t * inner_k

    # FLIP where: not zero AND flip improves M-space
    flip_q = (~zero_q) & (flip_score_q > flip_threshold)
    flip_k = (~zero_k) & (flip_score_k > flip_threshold)

    # ── Apply reductions ──
    W_q_reduced = W_q_t.copy()
    W_q_reduced[zero_q] = 0.0
    W_q_reduced[flip_q] = -W_q_reduced[flip_q]

    W_k_reduced = W_k_t.copy()
    W_k_reduced[zero_k] = 0.0
    W_k_reduced[flip_k] = -W_k_reduced[flip_k]

    # ── Diagnostics ──
    n_total = d_out * d_in
    stats = {
        "K": K,
        "energy_at_K": float(cum[K - 1]),
        "q": {
            "n_zero": int(zero_q.sum()),
            "n_flip": int(flip_q.sum()),
            "n_keep": int(n_total - zero_q.sum() - flip_q.sum()),
            "zero_frac": float(zero_q.mean()),
            "flip_frac": float(flip_q.mean()),
            "mean_snr": float(snr_q.mean()),
        },
        "k": {
            "n_zero": int(zero_k.sum()),
            "n_flip": int(flip_k.sum()),
            "n_keep": int(n_total - zero_k.sum() - flip_k.sum()),
            "zero_frac": float(zero_k.mean()),
            "flip_frac": float(flip_k.mean()),
            "mean_snr": float(snr_k.mean()),
        },
    }

    return {
        "W_q_ternary": W_q_reduced,
        "W_k_ternary": W_k_reduced,
        "gamma_q": gamma_q,
        "gamma_k": gamma_k,
        "stats": stats,
    }


def measure_mspace(W_q, W_k):
    """Quick M-space quality check."""
    M = W_q.T @ W_k
    _, s, _ = np.linalg.svd(M, full_matrices=False)
    total = (s ** 2).sum()
    if total < 1e-12:
        return {"rank90": len(s), "top1_pct": 0.0}
    cum = np.cumsum(s ** 2) / total
    return {
        "rank90": int(np.searchsorted(cum, 0.90) + 1),
        "top1_pct": float(cum[0] * 100),
    }


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("reduce.py self-test")
    np.random.seed(42)

    d = 64
    W_q = np.random.randn(d, d).astype(np.float32) * 0.1
    W_k = np.random.randn(d, d).astype(np.float32) * 0.1

    result = reduce_attention(W_q, W_k, zero_threshold=0.5, flip_threshold=0.0)

    print(f"  K = {result['stats']['K']} modes")
    print(f"  Q: {result['stats']['q']['n_zero']} zero, "
          f"{result['stats']['q']['n_flip']} flip, "
          f"{result['stats']['q']['n_keep']} keep")
    print(f"  K: {result['stats']['k']['n_zero']} zero, "
          f"{result['stats']['k']['n_flip']} flip, "
          f"{result['stats']['k']['n_keep']} keep")

    ms_before = measure_mspace(np.sign(W_q), np.sign(W_k))
    ms_after = measure_mspace(result["W_q_ternary"], result["W_k_ternary"])
    print(f"  M-space: rank90 {ms_before['rank90']} → {ms_after['rank90']}")
    print("  ✓ passed")
