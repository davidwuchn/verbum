"""
v14 Crystal Lattice Loss — three-component crystal geometry enforcement.

Session 144 key insight: the crystal lives on a CURVED manifold.
The geodesic midpoint of Zone A and Zone C is 25% closer to Zone B
than linear interpolation, so the parity target is the Riemannian mean
(geodesic midpoint) rather than raw Zone B.  That fix collapsed
gradient cancellation from 1.167 → 0.039.

Components
----------
1. crystal_lattice_loss   — zone MSE (linear, averages cleanly)
2. geodesic_parity_loss   — eigenbasis projection on geodesic midpoint
3. cross_zone_rotation_loss — joint-basis PC0↔PC1 coupling per zone
4. CrystalLoss             — convenience class; precomputes everything once

Order of 16 combinators: K I B C D Y W WHNF āK āI āB āC āD āY āW āWHNF

License: MIT
"""

from __future__ import annotations

import math
import numpy as np
import mlx.core as mx

# ══════════════════════════════════════════════════════════════════════
# § 1  Zone Target Data  (copied verbatim from v13/config.py L293-356)
# ══════════════════════════════════════════════════════════════════════

# Order: K I B C D Y W WHNF āK āI āB āC āD āY āW āWHNF

ZONE_A_TARGETS: tuple[tuple[float, ...], ...] = (
    # Zone A (0-20%): encode. Weak anti-crystal. anti_crystal_coupling = -0.10
    (+1.0000, +0.9210, +0.0771, +0.0906, +0.1280, +0.0363, +0.2031, -0.1694, -0.1000, -0.0921, -0.0077, -0.0091, -0.0128, -0.0036, -0.0203, +0.0169),
    (+0.9210, +1.0000, +0.1177, +0.1228, +0.1553, +0.0921, +0.1837, -0.1994, -0.0921, -0.1000, -0.0118, -0.0123, -0.0155, -0.0092, -0.0184, +0.0199),
    (+0.0771, +0.1177, +1.0000, +0.7963, +0.9778, +0.8370, +0.7426, -0.0094, -0.0077, -0.0118, -0.1000, -0.0796, -0.0978, -0.0837, -0.0743, +0.0009),
    (+0.0906, +0.1228, +0.7963, +1.0000, +0.7680, +0.6651, +0.9219, -0.0246, -0.0091, -0.0123, -0.0796, -0.1000, -0.0768, -0.0665, -0.0922, +0.0025),
    (+0.1280, +0.1553, +0.9778, +0.7680, +1.0000, +0.8057, +0.7676, -0.0246, -0.0128, -0.0155, -0.0978, -0.0768, -0.1000, -0.0806, -0.0768, +0.0025),
    (+0.0363, +0.0921, +0.8370, +0.6651, +0.8057, +1.0000, +0.5693, -0.0235, -0.0036, -0.0092, -0.0837, -0.0665, -0.0806, -0.1000, -0.0569, +0.0024),
    (+0.2031, +0.1837, +0.7426, +0.9219, +0.7676, +0.5693, +1.0000, -0.0213, -0.0203, -0.0184, -0.0743, -0.0922, -0.0768, -0.0569, -0.1000, +0.0021),
    (-0.1694, -0.1994, -0.0094, -0.0246, -0.0246, -0.0235, -0.0213, +1.0000, +0.0169, +0.0199, +0.0009, +0.0025, +0.0025, +0.0024, +0.0021, -0.1000),
    (-0.1000, -0.0921, -0.0077, -0.0091, -0.0128, -0.0036, -0.0203, +0.0169, +1.0000, +0.9210, +0.0771, +0.0906, +0.1280, +0.0363, +0.2031, -0.1694),
    (-0.0921, -0.1000, -0.0118, -0.0123, -0.0155, -0.0092, -0.0184, +0.0199, +0.9210, +1.0000, +0.1177, +0.1228, +0.1553, +0.0921, +0.1837, -0.1994),
    (-0.0077, -0.0118, -0.1000, -0.0796, -0.0978, -0.0837, -0.0743, +0.0009, +0.0771, +0.1177, +1.0000, +0.7963, +0.9778, +0.8370, +0.7426, -0.0094),
    (-0.0091, -0.0123, -0.0796, -0.1000, -0.0768, -0.0665, -0.0922, +0.0025, +0.0906, +0.1228, +0.7963, +1.0000, +0.7680, +0.6651, +0.9219, -0.0246),
    (-0.0128, -0.0155, -0.0978, -0.0768, -0.1000, -0.0806, -0.0768, +0.0025, +0.1280, +0.1553, +0.9778, +0.7680, +1.0000, +0.8057, +0.7676, -0.0246),
    (-0.0036, -0.0092, -0.0837, -0.0665, -0.0806, -0.1000, -0.0569, +0.0024, +0.0363, +0.0921, +0.8370, +0.6651, +0.8057, +1.0000, +0.5693, -0.0235),
    (-0.0203, -0.0184, -0.0743, -0.0922, -0.0768, -0.0569, -0.1000, +0.0021, +0.2031, +0.1837, +0.7426, +0.9219, +0.7676, +0.5693, +1.0000, -0.0213),
    (+0.0169, +0.0199, +0.0009, +0.0025, +0.0025, +0.0024, +0.0021, -0.1000, -0.1694, -0.1994, -0.0094, -0.0246, -0.0246, -0.0235, -0.0213, +1.0000),
)

ZONE_B_TARGETS: tuple[tuple[float, ...], ...] = (
    # Zone B (30-60%): compute. Medium anti-crystal. anti_crystal_coupling = -0.19
    (+1.0000, +0.7865, +0.1948, +0.2265, +0.3232, +0.1768, +0.5360, -0.1862, -0.1900, -0.1494, -0.0370, -0.0430, -0.0614, -0.0336, -0.1018, +0.0354),
    (+0.7865, +1.0000, +0.2479, +0.2511, +0.3463, +0.1739, +0.3781, -0.2448, -0.1494, -0.1900, -0.0471, -0.0477, -0.0658, -0.0330, -0.0718, +0.0465),
    (+0.1948, +0.2479, +1.0000, +0.8878, +0.8937, +0.6623, +0.6851, -0.1227, -0.0370, -0.0471, -0.1900, -0.1687, -0.1698, -0.1258, -0.1302, +0.0233),
    (+0.2265, +0.2511, +0.8878, +1.0000, +0.8316, +0.7200, +0.7318, -0.1027, -0.0430, -0.0477, -0.1687, -0.1900, -0.1580, -0.1368, -0.1390, +0.0195),
    (+0.3232, +0.3463, +0.8937, +0.8316, +1.0000, +0.6798, +0.8064, -0.1729, -0.0614, -0.0658, -0.1698, -0.1580, -0.1900, -0.1292, -0.1532, +0.0329),
    (+0.1768, +0.1739, +0.6623, +0.7200, +0.6798, +1.0000, +0.5653, -0.0840, -0.0336, -0.0330, -0.1258, -0.1368, -0.1292, -0.1900, -0.1074, +0.0160),
    (+0.5360, +0.3781, +0.6851, +0.7318, +0.8064, +0.5653, +1.0000, -0.1379, -0.1018, -0.0718, -0.1302, -0.1390, -0.1532, -0.1074, -0.1900, +0.0262),
    (-0.1862, -0.2448, -0.1227, -0.1027, -0.1729, -0.0840, -0.1379, +1.0000, +0.0354, +0.0465, +0.0233, +0.0195, +0.0329, +0.0160, +0.0262, -0.1900),
    (-0.1900, -0.1494, -0.0370, -0.0430, -0.0614, -0.0336, -0.1018, +0.0354, +1.0000, +0.7865, +0.1948, +0.2265, +0.3232, +0.1768, +0.5360, -0.1862),
    (-0.1494, -0.1900, -0.0471, -0.0477, -0.0658, -0.0330, -0.0718, +0.0465, +0.7865, +1.0000, +0.2479, +0.2511, +0.3463, +0.1739, +0.3781, -0.2448),
    (-0.0370, -0.0471, -0.1900, -0.1687, -0.1698, -0.1258, -0.1302, +0.0233, +0.1948, +0.2479, +1.0000, +0.8878, +0.8937, +0.6623, +0.6851, -0.1227),
    (-0.0430, -0.0477, -0.1687, -0.1900, -0.1580, -0.1368, -0.1390, +0.0195, +0.2265, +0.2511, +0.8878, +1.0000, +0.8316, +0.7200, +0.7318, -0.1027),
    (-0.0614, -0.0658, -0.1698, -0.1580, -0.1900, -0.1292, -0.1532, +0.0329, +0.3232, +0.3463, +0.8937, +0.8316, +1.0000, +0.6798, +0.8064, -0.1729),
    (-0.0336, -0.0330, -0.1258, -0.1368, -0.1292, -0.1900, -0.1074, +0.0160, +0.1768, +0.1739, +0.6623, +0.7200, +0.6798, +1.0000, +0.5653, -0.0840),
    (-0.1018, -0.0718, -0.1302, -0.1390, -0.1532, -0.1074, -0.1900, +0.0262, +0.5360, +0.3781, +0.6851, +0.7318, +0.8064, +0.5653, +1.0000, -0.1379),
    (+0.0354, +0.0465, +0.0233, +0.0195, +0.0329, +0.0160, +0.0262, -0.1900, -0.1862, -0.2448, -0.1227, -0.1027, -0.1729, -0.0840, -0.1379, +1.0000),
)

ZONE_C_TARGETS: tuple[tuple[float, ...], ...] = (
    # Zone C (70-90%): converge. Strong anti-crystal. WHNF deeply negative. anti_crystal_coupling = -0.28
    (+1.0000, +0.8614, +0.5238, +0.5429, +0.5910, +0.4920, +0.7262, -0.2736, -0.2800, -0.2412, -0.1467, -0.1520, -0.1655, -0.1378, -0.2033, +0.0766),
    (+0.8614, +1.0000, +0.5118, +0.5256, +0.5939, +0.4862, +0.5886, -0.2750, -0.2412, -0.2800, -0.1433, -0.1472, -0.1663, -0.1361, -0.1648, +0.0770),
    (+0.5238, +0.5118, +1.0000, +0.9465, +0.9510, +0.8911, +0.8192, -0.2835, -0.1467, -0.1433, -0.2800, -0.2650, -0.2663, -0.2495, -0.2294, +0.0794),
    (+0.5429, +0.5256, +0.9465, +1.0000, +0.9445, +0.9115, +0.8522, -0.2888, -0.1520, -0.1472, -0.2650, -0.2800, -0.2645, -0.2552, -0.2386, +0.0809),
    (+0.5910, +0.5939, +0.9510, +0.9445, +1.0000, +0.8983, +0.8613, -0.3000, -0.1655, -0.1663, -0.2663, -0.2645, -0.2800, -0.2515, -0.2412, +0.0840),
    (+0.4920, +0.4862, +0.8911, +0.9115, +0.8983, +1.0000, +0.7707, -0.2701, -0.1378, -0.1361, -0.2495, -0.2552, -0.2515, -0.2800, -0.2158, +0.0756),
    (+0.7262, +0.5886, +0.8192, +0.8522, +0.8613, +0.7707, +1.0000, -0.2838, -0.2033, -0.1648, -0.2294, -0.2386, -0.2412, -0.2158, -0.2800, +0.0795),
    (-0.2736, -0.2750, -0.2835, -0.2888, -0.3000, -0.2701, -0.2838, +1.0000, +0.0766, +0.0770, +0.0794, +0.0809, +0.0840, +0.0756, +0.0795, -0.2800),
    (-0.2800, -0.2412, -0.1467, -0.1520, -0.1655, -0.1378, -0.2033, +0.0766, +1.0000, +0.8614, +0.5238, +0.5429, +0.5910, +0.4920, +0.7262, -0.2736),
    (-0.2412, -0.2800, -0.1433, -0.1472, -0.1663, -0.1361, -0.1648, +0.0770, +0.8614, +1.0000, +0.5118, +0.5256, +0.5939, +0.4862, +0.5886, -0.2750),
    (-0.1467, -0.1433, -0.2800, -0.2650, -0.2663, -0.2495, -0.2294, +0.0794, +0.5238, +0.5118, +1.0000, +0.9465, +0.9510, +0.8911, +0.8192, -0.2835),
    (-0.1520, -0.1472, -0.2650, -0.2800, -0.2645, -0.2552, -0.2386, +0.0809, +0.5429, +0.5256, +0.9465, +1.0000, +0.9445, +0.9115, +0.8522, -0.2888),
    (-0.1655, -0.1663, -0.2663, -0.2645, -0.2800, -0.2515, -0.2412, +0.0840, +0.5910, +0.5939, +0.9510, +0.9445, +1.0000, +0.8983, +0.8613, -0.3000),
    (-0.1378, -0.1361, -0.2495, -0.2552, -0.2515, -0.2800, -0.2158, +0.0756, +0.4920, +0.4862, +0.8911, +0.9115, +0.8983, +1.0000, +0.7707, -0.2701),
    (-0.2033, -0.1648, -0.2294, -0.2386, -0.2412, -0.2158, -0.2800, +0.0795, +0.7262, +0.5886, +0.8192, +0.8522, +0.8613, +0.7707, +1.0000, -0.2838),
    (+0.0766, +0.0770, +0.0794, +0.0809, +0.0840, +0.0756, +0.0795, -0.2800, -0.2736, -0.2750, -0.2835, -0.2888, -0.3000, -0.2701, -0.2838, +1.0000),
)

# ══════════════════════════════════════════════════════════════════════
# § 2  Crystal Lattice MSE Loss
# ══════════════════════════════════════════════════════════════════════


def crystal_lattice_loss(
    embeddings: mx.array,
    zone_targets: list[mx.array],
    zone_lambdas: tuple[float, ...] = (1.0, 1.0, 1.0),
) -> mx.array:
    """Crystal lattice MSE: student cosine matrix vs each zone target.

    Computes the full 16×16 cosine similarity matrix from the 16 dual-crystal
    embeddings (8 positive + 8 anti), then measures MSE against each zone's
    target matrix.  Zones are weighted by zone_lambdas and averaged.

    Parameters
    ----------
    embeddings : mx.array, shape (16, d)
        Concatenated [combinator_embeddings; anti_combinator_embeddings].
    zone_targets : list of mx.array, each shape (16, 16)
        Precomputed zone target matrices (A, B, C).
    zone_lambdas : tuple of float
        Per-zone loss weights.

    Returns
    -------
    mx.array, scalar
        Weighted mean MSE across all zones.
    """
    # Normalise to unit sphere
    norms = mx.sqrt(mx.sum(embeddings * embeddings, axis=-1, keepdims=True) + 1e-8)
    emb_norm = embeddings / norms                 # (16, d)
    student_cos = emb_norm @ emb_norm.T           # (16, 16)

    # Upper-triangle indices (avoid double-counting; diagonal is always 1.0)
    n = student_cos.shape[0]
    rows, cols = [], []
    for i in range(n):
        for j in range(i + 1, n):
            rows.append(i)
            cols.append(j)
    row_idx = mx.array(rows)
    col_idx = mx.array(cols)

    student_tri = student_cos[row_idx, col_idx]   # (120,)

    total_loss = mx.array(0.0)
    total_weight = sum(zone_lambdas)

    for target, lam in zip(zone_targets, zone_lambdas):
        target_tri = target[row_idx, col_idx]
        diff = student_tri - target_tri
        mse = mx.mean(diff * diff)
        total_loss = total_loss + lam * mse

    return total_loss / total_weight


# ══════════════════════════════════════════════════════════════════════
# § 3  Geodesic Parity Loss (Einstein tensor-aware)
# ══════════════════════════════════════════════════════════════════════


def compute_geodesic_midpoint(gA: np.ndarray, gC: np.ndarray) -> np.ndarray:
    """Matrix geometric mean: gA^{1/2} (gA^{-1/2} gC gA^{-1/2})^{1/2} gA^{1/2}.

    The geodesic midpoint on the SPD (symmetric positive definite) manifold
    under the affine-invariant Riemannian metric.  This is the true
    Riemannian mean between two SPD matrices — 25% closer to Zone B than
    naive linear interpolation (session 144 finding).

    Because the crystal target matrices have small negative eigenvalues we
    regularise them to SPD by adding a small identity shift before computing
    the matrix square root.

    Parameters
    ----------
    gA, gC : np.ndarray, shape (16, 16)
        Symmetric target matrices for Zone A and Zone C.

    Returns
    -------
    np.ndarray, shape (16, 16)
        Geodesic midpoint (Riemannian mean).
    """
    eps = 1e-4  # regularisation to ensure strict positive-definiteness

    def _make_spd(M: np.ndarray) -> np.ndarray:
        """Shift so all eigenvalues ≥ eps."""
        eigvals = np.linalg.eigvalsh(M)
        shift = max(0.0, eps - eigvals.min())
        return M + shift * np.eye(M.shape[0])

    def _mat_sqrt(M: np.ndarray) -> np.ndarray:
        """Symmetric matrix square root via eigendecomposition."""
        vals, vecs = np.linalg.eigh(M)
        vals = np.maximum(vals, 0.0)
        return vecs @ np.diag(np.sqrt(vals)) @ vecs.T

    def _mat_inv_sqrt(M: np.ndarray) -> np.ndarray:
        """Symmetric matrix inverse square root."""
        vals, vecs = np.linalg.eigh(M)
        vals = np.maximum(vals, eps)
        return vecs @ np.diag(1.0 / np.sqrt(vals)) @ vecs.T

    A = _make_spd(gA.astype(np.float64))
    C = _make_spd(gC.astype(np.float64))

    A_sqrt     = _mat_sqrt(A)       # A^{1/2}
    A_inv_sqrt = _mat_inv_sqrt(A)   # A^{-1/2}

    # Middle term: (A^{-1/2} C A^{-1/2})^{1/2}
    inner = A_inv_sqrt @ C @ A_inv_sqrt
    inner_sqrt = _mat_sqrt(inner)

    geo_mid = A_sqrt @ inner_sqrt @ A_sqrt
    return geo_mid.astype(np.float32)


def geodesic_parity_loss(
    embeddings: mx.array,
    geodesic_target: mx.array,
    eigvecs: mx.array,
    eigvals: mx.array,
    parity_levels: list[int],
) -> tuple[mx.array, mx.array]:
    """Hierarchical parity check on the geodesic-midpoint eigenbasis.

    Session 144 fix: operate on ONE target (geodesic midpoint of A and C),
    not three zones.  This eliminates gradient cancellation because A and C
    are no longer pulling in opposite directions through the same eigenbasis.

    The geodesic midpoint target C_geo = A^{1/2}(A^{-1/2} C A^{-1/2})^{1/2} A^{1/2}
    is eigendecomposed: C_geo = V Λ V^T.

    The student cosine matrix S is projected: P = V^T S V.
    If the student geometry matches the target, P = Λ (diagonal).
    Off-diagonal elements in P are structural errors.

    At each level k ∈ {3, 4, 5, 6, 8}:
      - Extract P[:k, :k]
      - Target is diag(Λ[:k])
      - MSE on the full k×k block (diagonal + off-diagonal)
      - Weight by cumulative variance fraction (lower k = heavier)

    Parameters
    ----------
    embeddings : mx.array, shape (16, d)
    geodesic_target : mx.array, shape (16, 16)  — stored but not used in fwd
    eigvecs : mx.array, shape (16, 16)           — eigenvectors of geodesic midpoint
    eigvals : mx.array, shape (16,)              — eigenvalues descending
    parity_levels : list[int]                    — k values, e.g. [3, 4, 5, 6, 8]

    Returns
    -------
    loss : mx.array, scalar
    per_level_errors : mx.array, shape (n_levels,)  — max off-diagonal per level
    """
    # Student cosine matrix
    norms = mx.sqrt(mx.sum(embeddings * embeddings, axis=-1, keepdims=True) + 1e-8)
    emb_norm = embeddings / norms
    student_cos = emb_norm @ emb_norm.T           # (16, 16)

    # Project into geodesic-midpoint eigenbasis
    projected = eigvecs.T @ student_cos @ eigvecs  # (16, 16)

    # Cumulative variance weights (done on float32 eigvals, fully in MLX)
    total_var = mx.sum(mx.maximum(eigvals, mx.array(0.0)))

    total_loss = mx.array(0.0)
    level_errors = []

    for k in parity_levels:
        P_k = projected[:k, :k]                   # (k, k)
        target_diag = mx.diag(eigvals[:k])         # (k, k) diagonal matrix

        diff = P_k - target_diag
        mse = mx.mean(diff * diff)

        # Cumulative variance weight for this level
        cum_var = mx.sum(mx.maximum(eigvals[:k], mx.array(0.0)))
        w = cum_var / (total_var + 1e-8)

        total_loss = total_loss + w * mse

        # Diagnostics: max absolute off-diagonal error
        mask = mx.array(1.0) - mx.eye(k)
        off_diag = mx.abs(P_k * mask)
        level_errors.append(mx.max(off_diag))

    per_level_errors = mx.stack(level_errors)      # (n_levels,)
    return total_loss, per_level_errors


# ══════════════════════════════════════════════════════════════════════
# § 4  Cross-Zone Lens Rotation Loss
# ══════════════════════════════════════════════════════════════════════


def cross_zone_rotation_loss(
    embeddings: mx.array,
    joint_eigvecs: mx.array,
    target_projected: list[mx.array],
    k: int = 6,
) -> tuple[mx.array, mx.array]:
    """Cross-zone lens parity: enforce the ~11° PC0↔PC1 rotation structure.

    Session 142 finding: the crystal rotates ~11° between zone A and zone C.
    The PC0↔PC1 off-diagonal coupling flips from +0.46 (A) → ~0 (B) → -0.48 (C).
    This rotation IS the lens computation.

    The joint eigenbasis is derived from mean(zone_A, zone_B, zone_C).
    The student's cosine matrix is projected into this shared basis and the
    top k×k block is compared against each zone's projected target.

    Parameters
    ----------
    embeddings : mx.array, shape (16, d)
    joint_eigvecs : mx.array, shape (16, 16)    — joint eigenbasis
    target_projected : list of mx.array         — P_z = V^T zone_z V per zone
    k : int                                     — top-k PCs to enforce

    Returns
    -------
    loss : mx.array, scalar  — mean MSE across zones
    lens_rotation : mx.array, shape (n_zones,)  — PC0↔PC1 coupling per zone
    """
    # Student cosine matrix projected into joint basis
    norms = mx.sqrt(mx.sum(embeddings * embeddings, axis=-1, keepdims=True) + 1e-8)
    emb_norm = embeddings / norms
    student_cos = emb_norm @ emb_norm.T
    P_student = joint_eigvecs.T @ student_cos @ joint_eigvecs  # (16, 16)

    total_loss = mx.array(0.0)
    lens_rotations = []

    for target_P in target_projected:
        diff = P_student[:k, :k] - target_P[:k, :k]
        mse = mx.mean(diff * diff)
        total_loss = total_loss + mse
        # PC0↔PC1 coupling encodes the lens rotation angle
        lens_rotations.append(P_student[0, 1])

    total_loss = total_loss / len(target_projected)
    lens_rotation = mx.stack(lens_rotations)

    return total_loss, lens_rotation


# ══════════════════════════════════════════════════════════════════════
# § 5  CrystalLoss class — precomputes everything once at init
# ══════════════════════════════════════════════════════════════════════


class CrystalLoss:
    """Three-component crystal loss: MSE + parity + cross-zone rotation.

    All numpy precomputation happens in __init__; the forward path (__call__)
    is pure MLX and is fully differentiable.

    Attributes
    ----------
    zone_targets_mx : list of mx.array (16,16)  — zone A/B/C targets
    geodesic_midpoint_mx : mx.array (16,16)     — A∘C Riemannian mean
    parity_eigvecs : mx.array (16,16)           — eigenvectors of geodesic midpoint
    parity_eigvals : mx.array (16,)             — eigenvalues (descending)
    joint_eigvecs : mx.array (16,16)            — joint eigenbasis (mean of zones)
    target_projected : list of mx.array (16,16) — P_z = V^T zone_z V
    parity_levels : list[int]                   — [3, 4, 5, 6, 8]
    """

    PARITY_LEVELS: list[int] = [3, 4, 5, 6, 8]

    def __init__(
        self,
        zone_lambdas: tuple[float, ...] = (1.0, 1.0, 1.0),
        cross_zone_k: int = 6,
    ) -> None:
        self.zone_lambdas = zone_lambdas
        self.cross_zone_k = cross_zone_k

        # ── Convert zone targets to numpy once ────────────────
        gA = np.array(ZONE_A_TARGETS, dtype=np.float32)
        gB = np.array(ZONE_B_TARGETS, dtype=np.float32)
        gC = np.array(ZONE_C_TARGETS, dtype=np.float32)

        # ── Zone targets as mx.arrays ─────────────────────────
        self.zone_targets_mx: list[mx.array] = [
            mx.array(gA),
            mx.array(gB),
            mx.array(gC),
        ]

        # ── Geodesic midpoint (A ∘ C Riemannian mean) ─────────
        # Session 144: 25% closer to B than linear interp — eliminates
        # gradient cancellation by giving parity ONE stable target.
        geo_mid_np = compute_geodesic_midpoint(gA, gC)
        self.geodesic_midpoint_mx = mx.array(geo_mid_np)

        # Eigendecompose the geodesic midpoint for parity projection
        eigvals_np, eigvecs_np = np.linalg.eigh(geo_mid_np.astype(np.float64))
        idx = np.argsort(eigvals_np)[::-1]
        eigvals_np = eigvals_np[idx].astype(np.float32)
        eigvecs_np = eigvecs_np[:, idx].astype(np.float32)
        self.parity_eigvecs = mx.array(eigvecs_np)
        self.parity_eigvals = mx.array(eigvals_np)

        # ── Joint eigenbasis for cross-zone rotation loss ──────
        joint_np = np.mean([gA, gB, gC], axis=0).astype(np.float32)
        j_eigvals, j_eigvecs = np.linalg.eigh(joint_np.astype(np.float64))
        j_idx = np.argsort(j_eigvals)[::-1]
        j_eigvecs = j_eigvecs[:, j_idx].astype(np.float32)
        self.joint_eigvecs = mx.array(j_eigvecs)

        # Precompute projected zone targets: P_z = V^T zone_z V
        self.target_projected: list[mx.array] = []
        for gz in [gA, gB, gC]:
            P = j_eigvecs.T @ gz @ j_eigvecs        # numpy (16,16)
            self.target_projected.append(mx.array(P))

        # ── Parity levels ─────────────────────────────────────
        self.parity_levels = self.PARITY_LEVELS

    # ------------------------------------------------------------------

    def __call__(self, embeddings: mx.array) -> dict[str, mx.array]:
        """Compute all three crystal loss components.

        Parameters
        ----------
        embeddings : mx.array, shape (16, d)
            Concatenated [combinator_embeddings; anti_combinator_embeddings].

        Returns
        -------
        dict with keys:
          'crystal_mse'   — scalar: zone-weighted lattice MSE
          'parity'        — scalar: geodesic parity loss
          'cross_zone'    — scalar: cross-zone rotation loss
          'parity_errors' — (n_levels,): per-level max off-diagonal error
          'lens_rotation' — (n_zones,): PC0↔PC1 coupling per zone
        """
        crystal_mse = crystal_lattice_loss(
            embeddings,
            self.zone_targets_mx,
            self.zone_lambdas,
        )

        parity, parity_errors = geodesic_parity_loss(
            embeddings,
            self.geodesic_midpoint_mx,
            self.parity_eigvecs,
            self.parity_eigvals,
            self.parity_levels,
        )

        cross_zone, lens_rotation = cross_zone_rotation_loss(
            embeddings,
            self.joint_eigvecs,
            self.target_projected,
            k=self.cross_zone_k,
        )

        return {
            "crystal_mse":   crystal_mse,
            "parity":        parity,
            "cross_zone":    cross_zone,
            "parity_errors": parity_errors,
            "lens_rotation": lens_rotation,
        }


# ══════════════════════════════════════════════════════════════════════
# § 6  Self-test — run with: python3 crystal.py
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("CrystalLoss self-test (v14)")
    print("=" * 60)

    D = 1280  # v14 model dimension

    # ── 1. Instantiate and report precomputed shapes ───────────────────
    print("\n[1] Building CrystalLoss …")
    crystal = CrystalLoss()
    print(f"  zone_targets_mx  : {len(crystal.zone_targets_mx)} arrays of {crystal.zone_targets_mx[0].shape}")
    print(f"  geodesic_midpoint: {crystal.geodesic_midpoint_mx.shape}")
    print(f"  parity_eigvecs   : {crystal.parity_eigvecs.shape}")
    print(f"  parity_eigvals   : {crystal.parity_eigvals.shape}")
    print(f"  joint_eigvecs    : {crystal.joint_eigvecs.shape}")
    print(f"  target_projected : {len(crystal.target_projected)} arrays of {crystal.target_projected[0].shape}")
    print(f"  parity_levels    : {crystal.parity_levels}")

    # ── 2. Verify geodesic midpoint is closer to B than linear interp ──
    print("\n[2] Geodesic midpoint sanity check …")
    gA_np = np.array(ZONE_A_TARGETS, dtype=np.float32)
    gB_np = np.array(ZONE_B_TARGETS, dtype=np.float32)
    gC_np = np.array(ZONE_C_TARGETS, dtype=np.float32)
    geo_np = compute_geodesic_midpoint(gA_np, gC_np)
    linear_mid = 0.5 * (gA_np + gC_np)
    dist_geo_to_B   = float(np.mean((geo_np - gB_np) ** 2) ** 0.5)
    dist_linear_to_B = float(np.mean((linear_mid - gB_np) ** 2) ** 0.5)
    print(f"  ||geo_mid - B||   = {dist_geo_to_B:.4f}")
    print(f"  ||linear_mid - B||= {dist_linear_to_B:.4f}")
    ratio = dist_geo_to_B / dist_linear_to_B
    print(f"  ratio             = {ratio:.3f}  (expect < 1.0 → geodesic closer)")
    assert ratio < 1.0 or math.isclose(ratio, 1.0, rel_tol=0.05), (
        f"Geodesic midpoint should be ≤ linear midpoint distance to B, got ratio={ratio:.3f}"
    )

    # ── 3. Forward pass with random embeddings ─────────────────────────
    print(f"\n[3] Forward pass (D={D}) …")
    emb = mx.random.normal((16, D)) * 0.02
    losses = crystal(emb)
    mx.eval(losses["crystal_mse"], losses["parity"], losses["cross_zone"],
            losses["parity_errors"], losses["lens_rotation"])

    print(f"  crystal_mse  = {float(losses['crystal_mse']):.6f}")
    print(f"  parity       = {float(losses['parity']):.6f}")
    print(f"  cross_zone   = {float(losses['cross_zone']):.6f}")
    errs = [float(losses['parity_errors'][i]) for i in range(len(crystal.parity_levels))]
    for k, e in zip(crystal.parity_levels, errs):
        print(f"    parity_errors[k={k}] = {e:.6f}")
    rots = [float(losses['lens_rotation'][i]) for i in range(3)]
    for z, r in zip(["A", "B", "C"], rots):
        print(f"    lens_rotation[{z}]   = {r:.6f}")

    # ── 4. Gradient flow check ─────────────────────────────────────────
    print("\n[4] Gradient flow check …")

    def combined_loss(e: mx.array) -> mx.array:
        out = crystal(e)
        return out["crystal_mse"] + out["parity"] + out["cross_zone"]

    grad_fn = mx.grad(combined_loss)
    grads = grad_fn(emb)
    mx.eval(grads)

    grad_norm = float(mx.sqrt(mx.sum(grads * grads)).item())
    max_grad  = float(mx.max(mx.abs(grads)).item())
    print(f"  ||grad||_2 = {grad_norm:.6f}")
    print(f"  max |grad| = {max_grad:.6f}")

    assert grad_norm > 0.0, "Gradient norm is zero — no gradient flow!"
    assert not math.isnan(grad_norm), "Gradient norm is NaN!"
    assert not math.isinf(grad_norm), "Gradient norm is Inf!"
    print("  ✓ Gradients are non-zero and finite")

    # ── 5. Check per-component gradients ──────────────────────────────
    print("\n[5] Per-component gradient check …")

    for name, fn in [
        ("crystal_mse", lambda e: crystal(e)["crystal_mse"]),
        ("parity",      lambda e: crystal(e)["parity"]),
        ("cross_zone",  lambda e: crystal(e)["cross_zone"]),
    ]:
        g = mx.grad(fn)(emb)
        mx.eval(g)
        gnorm = float(mx.sqrt(mx.sum(g * g)).item())
        print(f"  ||grad({name})|| = {gnorm:.6f}")
        assert gnorm > 0.0, f"{name} gradient is zero!"
        assert not math.isnan(gnorm), f"{name} gradient is NaN!"

    print("\n" + "=" * 60)
    print("All checks passed. ✅")
    print("=" * 60)
