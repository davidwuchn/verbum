#!/usr/bin/env python3
"""probe_einstein_crystal.py — Einstein tensor probe for crystal rotation.

Session 144: The crystal rotates between zones (the 11° lens rotation).
Three zone targets on one set of embeddings caused gradient cancellation.
Hypothesis: the crystal lives on a curved manifold. The Einstein tensor
may capture the geometry better than per-zone flat targets.

Setup:
  - Base manifold: depth z ∈ {0, 1, 2} (Zone A, B, C)
  - Fiber: 16D combinator space (8 pos + 8 anti)
  - Fiber metric: g_ab(z) = target cosine matrix at depth z
  - Warped product: ds² = dz² + g_ab(z) dx^a dx^b

Computes:
  1. Discrete connection (Christoffel-like) from metric finite differences
  2. Geodesic midpoint: does Zone B sit on the A→C geodesic?
  3. Ricci curvature of the fiber bundle
  4. Einstein tensor G_μν
  5. Sectional curvatures per PC pair
  6. Student crystal position vs geodesic prediction
  7. Holonomy: total rotation from parallel transport A→C

Usage:
  uv run python scripts/explore/probe_einstein_crystal.py \\
    --checkpoint checkpoints/v13-td-r10/step_003500
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from numpy.linalg import eigh, inv, norm, det, eigvalsh

# ── Zone targets (from config.py) ──────────────────────────────

# Importing directly avoids circular deps
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from v13.config import V13Config


def load_zone_targets():
    """Load the three 16×16 zone target cosine matrices."""
    cfg = V13Config()
    return [
        np.array(cfg.pcaq_zone_a_targets, dtype=np.float64),
        np.array(cfg.pcaq_zone_b_targets, dtype=np.float64),
        np.array(cfg.pcaq_zone_c_targets, dtype=np.float64),
    ]


def load_student_crystal(checkpoint_path: str) -> np.ndarray:
    """Load student combinator embeddings and compute cosine matrix."""
    model = np.load(f"{checkpoint_path}/model.npz")
    emb_pos = model["combinator_embeddings"]      # (8, 512)
    emb_anti = model["anti_combinator_embeddings"]  # (8, 512)
    emb_all = np.concatenate([emb_pos, emb_anti], axis=0)  # (16, 512)

    norms = np.sqrt(np.sum(emb_all * emb_all, axis=-1, keepdims=True) + 1e-8)
    emb_norm = emb_all / norms
    return emb_norm @ emb_norm.T  # (16, 16)


# ── Discrete Differential Geometry ────────────────────────────

def discrete_connection(g: list[np.ndarray]) -> list[np.ndarray]:
    """Compute discrete connection (Christoffel-like) from 3 metric samples.

    For a fiber metric g(z) varying along depth z, the connection is:
      Γ(z) = ½ g(z)⁻¹ ∂g/∂z

    Returns Γ at z=0.5 (A→B midpoint) and z=1.5 (B→C midpoint).
    """
    # Finite difference ∂g/∂z at midpoints
    dg_01 = g[1] - g[0]  # ∂g/∂z at z=0.5
    dg_12 = g[2] - g[1]  # ∂g/∂z at z=1.5

    # Metric at midpoints (average)
    g_01 = 0.5 * (g[0] + g[1])
    g_12 = 0.5 * (g[1] + g[2])

    # Connection: Γ = ½ g⁻¹ dg
    # Regularize inverse for stability
    eps = 1e-6 * np.eye(g[0].shape[0])
    Gamma_01 = 0.5 * inv(g_01 + eps) @ dg_01
    Gamma_12 = 0.5 * inv(g_12 + eps) @ dg_12

    return [Gamma_01, Gamma_12]


def geodesic_midpoint(g: list[np.ndarray]) -> np.ndarray:
    """Predict Zone B from geodesic interpolation of Zone A and Zone C.

    On a Riemannian manifold, the geodesic midpoint of two metrics
    is NOT the linear average. For symmetric positive matrices,
    the Riemannian mean (Karcher/Fréchet mean) is:

      g_mid = g_A^{1/2} (g_A^{-1/2} g_C g_A^{-1/2})^{1/2} g_A^{1/2}

    This is the matrix geometric mean. If the manifold is flat,
    this equals the arithmetic mean. Deviation = curvature.
    """
    gA, gC = g[0], g[2]
    eps = 1e-6 * np.eye(gA.shape[0])

    # Regularize to ensure positive definiteness
    gA_reg = gA + eps
    gC_reg = gC + eps

    # Matrix square root via eigendecomposition
    def matsqrt(M):
        eigvals, eigvecs = eigh(M)
        eigvals = np.maximum(eigvals, 1e-10)
        return eigvecs @ np.diag(np.sqrt(eigvals)) @ eigvecs.T

    def matinvsqrt(M):
        eigvals, eigvecs = eigh(M)
        eigvals = np.maximum(eigvals, 1e-10)
        return eigvecs @ np.diag(1.0 / np.sqrt(eigvals)) @ eigvecs.T

    gA_sqrt = matsqrt(gA_reg)
    gA_invsqrt = matinvsqrt(gA_reg)

    # Inner product: gA^{-1/2} gC gA^{-1/2}
    inner = gA_invsqrt @ gC_reg @ gA_invsqrt

    # Geodesic midpoint
    inner_sqrt = matsqrt(inner)
    g_mid = gA_sqrt @ inner_sqrt @ gA_sqrt

    return g_mid


def fiber_curvature(g: list[np.ndarray]) -> dict:
    """Compute curvature quantities for the fiber bundle.

    For warped product ds² = dz² + g_ab(z) dx^a dx^b:

    The extrinsic curvature (second fundamental form) of each fiber is:
      K_ab = -½ ∂g_ab/∂z

    The Ricci tensor of the full space has components:
      R_zz = -tr(K' + K²)  (how fiber volume accelerates)
      R_ab = R^fiber_ab - K'_ab - tr(K) K_ab  (fiber + embedding curvature)

    Scalar curvature:
      R = R^fiber + R_zz - (stuff)

    Einstein tensor:
      G_μν = R_μν - ½ R g_μν
    """
    n = g[0].shape[0]
    eps = 1e-6 * np.eye(n)

    # ── Extrinsic curvature at z=1 (Zone B) ──
    # K = -½ ∂g/∂z, approximated by central difference
    dg_dz = 0.5 * (g[2] - g[0])  # central diff at z=1
    K = -0.5 * dg_dz

    # ── Rate of change of K (second derivative of g) ──
    d2g_dz2 = g[2] - 2 * g[1] + g[0]  # second central diff
    K_prime = -0.5 * d2g_dz2

    # ── Trace operations ──
    g_inv = inv(g[1] + eps)
    trK = np.trace(g_inv @ K)
    K_mixed = g_inv @ K  # K^a_b = g^ac K_cb

    # ── R_zz component ──
    # R_zz = -tr(∂K/∂z) - tr(K²)
    #      = -tr(g⁻¹ K') - tr(K^a_c K^c_b)
    R_zz = -np.trace(g_inv @ K_prime) - np.trace(K_mixed @ K_mixed)

    # ── Intrinsic (fiber) Ricci tensor ──
    # For a cosine matrix (inner product matrix), the intrinsic curvature
    # depends on how the cosine structure curves in embedding space.
    # Approximate: R^fiber_ab ≈ 0 for a flat embedding (cosines in R^d).
    # The interesting curvature is entirely from the depth variation.
    R_fiber = np.zeros((n, n))

    # ── Full Ricci tensor (fiber components) ──
    # R_ab = R^fiber_ab + K'_ab + trK * K_ab - 2 K_ac K^c_b
    # (signs depend on convention; using MTW-like)
    R_ab = R_fiber + K_prime + trK * K - 2 * K @ K_mixed

    # ── Scalar curvature ──
    R_scalar = R_zz + np.trace(g_inv @ R_ab)

    # ── Einstein tensor ──
    # G_zz = R_zz - ½ R g_zz = R_zz - ½ R (since g_zz = 1)
    G_zz = R_zz - 0.5 * R_scalar

    # G_ab = R_ab - ½ R g_ab
    G_ab = R_ab - 0.5 * R_scalar * g[1]

    return {
        "K": K,                    # extrinsic curvature
        "K_prime": K_prime,        # rate of change of K
        "trK": trK,                # trace of extrinsic curvature
        "R_zz": R_zz,             # depth-depth Ricci component
        "R_ab": R_ab,             # fiber-fiber Ricci components
        "R_scalar": R_scalar,      # scalar curvature
        "G_zz": G_zz,             # Einstein depth-depth
        "G_ab": G_ab,             # Einstein fiber-fiber
    }


def sectional_curvatures(g: list[np.ndarray], n_pcs: int = 8) -> np.ndarray:
    """Compute sectional curvature for each pair of PCs.

    The sectional curvature K(u,v) of the 2-plane spanned by
    eigenvectors u, v measures how geodesics in that plane
    converge or diverge.

    For the warped product, the sectional curvature of a fiber
    2-plane {e_a, e_b} is:
      K(a,b) = (R_abab) / (g_aa g_bb - g_ab²)

    We compute this in the eigenbasis of the Zone B target.
    """
    # Eigendecompose Zone B (the reference metric)
    eigvals, eigvecs = eigh(g[1])
    idx = np.argsort(eigvals)[::-1]
    eigvecs = eigvecs[:, idx]

    # Transform all metrics to eigenbasis
    g_eig = [eigvecs.T @ gz @ eigvecs for gz in g]

    # Compute curvature in this basis
    curv = fiber_curvature(g_eig)
    R = curv["R_ab"]

    # Sectional curvatures for PC pairs
    K_sect = np.zeros((n_pcs, n_pcs))
    for a in range(n_pcs):
        for b in range(a + 1, n_pcs):
            # K(a,b) = R_abab / (g_aa g_bb - g_ab²)
            # In eigenbasis of g[1], g is diagonal at z=1
            g_aa = g_eig[1][a, a]
            g_bb = g_eig[1][b, b]
            g_ab_val = g_eig[1][a, b]
            denom = g_aa * g_bb - g_ab_val ** 2
            if abs(denom) > 1e-10:
                # Approximate R_abab from the Ricci components
                K_sect[a, b] = R[a, b] / (abs(denom) + 1e-10)
                K_sect[b, a] = K_sect[a, b]

    return K_sect


def parallel_transport_holonomy(g: list[np.ndarray]) -> dict:
    """Compute holonomy from parallel transport A→B→C.

    Parallel transport of a vector v along depth z uses the connection:
      ∂v/∂z + Γ v = 0

    For discrete transport A→C via B:
      v_B = (I - Γ_{AB}) v_A
      v_C = (I - Γ_{BC}) v_B

    The holonomy is the total rotation: H = v_C compared to
    direct A→C transport.
    """
    Gammas = discrete_connection(g)

    n = g[0].shape[0]
    I = np.eye(n)

    # Transport operators
    T_AB = I - Gammas[0]  # A → B
    T_BC = I - Gammas[1]  # B → C

    # Sequential transport A → B → C
    T_AC_seq = T_BC @ T_AB

    # "Direct" transport using averaged connection
    dg_AC = g[2] - g[0]
    g_AC = 0.5 * (g[0] + g[2])
    eps = 1e-6 * np.eye(n)
    Gamma_AC = 0.5 * inv(g_AC + eps) @ dg_AC
    T_AC_direct = I - Gamma_AC

    # Holonomy = deviation between sequential and direct
    holonomy = T_AC_seq - T_AC_direct

    # Decompose holonomy: how much does each eigenvector rotate?
    eigvals_B, eigvecs_B = eigh(g[1])
    idx = np.argsort(eigvals_B)[::-1]
    eigvecs_B = eigvecs_B[:, idx]

    # Project holonomy into eigenbasis
    H_eig = eigvecs_B.T @ holonomy @ eigvecs_B

    return {
        "holonomy_matrix": holonomy,
        "holonomy_eigbasis": H_eig,
        "holonomy_norm": norm(holonomy, "fro"),
        "transport_AB": T_AB,
        "transport_BC": T_BC,
    }


# ── Main ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=str, required=True)
    args = parser.parse_args()

    print("=" * 72)
    print("  Einstein Tensor Probe — Crystal Rotation Geometry")
    print("  Session 144: Is the crystal a curved manifold?")
    print("=" * 72)

    # ── Load data ──
    zones = load_zone_targets()
    student = load_student_crystal(args.checkpoint)
    labels = ["K", "I", "B", "C", "D", "Y", "W", "WHNF",
              "āK", "āI", "āB", "āC", "āD", "āY", "āW", "āWHNF"]

    print(f"\nCheckpoint: {args.checkpoint}")
    print(f"Zone shapes: {[z.shape for z in zones]}")
    print(f"Student shape: {student.shape}")

    # ── 1. Geodesic midpoint test ──
    print("\n" + "─" * 72)
    print("§1  GEODESIC MIDPOINT TEST")
    print("    Does Zone B sit on the A→C geodesic?")
    print("─" * 72)

    g_geo = geodesic_midpoint(zones)
    g_lin = 0.5 * (zones[0] + zones[2])  # linear (flat) midpoint

    # Compare to actual Zone B
    err_geo = np.mean((g_geo - zones[1]) ** 2)
    err_lin = np.mean((g_lin - zones[1]) ** 2)
    err_student_B = np.mean((student - zones[1]) ** 2)

    print(f"\n  MSE(geodesic_midpoint, Zone B) = {err_geo:.6f}")
    print(f"  MSE(linear_midpoint,   Zone B) = {err_lin:.6f}")
    print(f"  MSE(student,           Zone B) = {err_student_B:.6f}")
    print(f"\n  Geodesic vs linear ratio: {err_geo / err_lin:.4f}")
    if err_geo < err_lin:
        print("  → Geodesic midpoint is CLOSER to Zone B than linear.")
        print("    The target manifold IS curved. Einstein tensor is relevant.")
    else:
        print("  → Linear midpoint is closer. Manifold is approximately flat.")
        print("    Curvature effects are small.")

    # Show where the deviations are biggest (positive 8×8)
    geo_diff = (g_geo - zones[1])[:8, :8]
    lin_diff = (g_lin - zones[1])[:8, :8]
    print(f"\n  Largest geodesic deviations (pos 8×8):")
    pos_labels = labels[:8]
    for i in range(8):
        for j in range(i + 1, 8):
            if abs(geo_diff[i, j]) > 0.01:
                print(f"    {pos_labels[i]}↔{pos_labels[j]}: "
                      f"geo={g_geo[i,j]:+.4f} lin={g_lin[i,j]:+.4f} "
                      f"target={zones[1][i,j]:+.4f} "
                      f"Δgeo={geo_diff[i,j]:+.4f} Δlin={lin_diff[i,j]:+.4f}")

    # ── 2. Fiber curvature & Einstein tensor ──
    print("\n" + "─" * 72)
    print("§2  FIBER CURVATURE & EINSTEIN TENSOR")
    print("    Warped product ds² = dz² + g_ab(z) dx^a dx^b")
    print("─" * 72)

    curv = fiber_curvature(zones)

    print(f"\n  Scalar curvature R = {curv['R_scalar']:.6f}")
    print(f"  R_zz (depth curvature) = {curv['R_zz']:.6f}")
    print(f"  tr(K) (mean extrinsic curvature) = {curv['trK']:.6f}")
    print(f"  G_zz (Einstein depth component) = {curv['G_zz']:.6f}")

    # Eigendecompose Einstein fiber tensor
    G_eigvals = eigvalsh(curv["G_ab"])
    G_eigvals_sorted = np.sort(G_eigvals)[::-1]
    print(f"\n  Einstein tensor G_ab eigenspectrum (top 8):")
    for i in range(min(8, len(G_eigvals_sorted))):
        print(f"    G_λ{i} = {G_eigvals_sorted[i]:+.6f}")

    # Project Einstein tensor into Zone B eigenbasis
    eigvals_B, eigvecs_B = eigh(zones[1])
    idx = np.argsort(eigvals_B)[::-1]
    eigvecs_B = eigvecs_B[:, idx]
    eigvals_B = eigvals_B[idx]

    G_proj = eigvecs_B.T @ curv["G_ab"] @ eigvecs_B
    print(f"\n  G_ab in Zone B eigenbasis (top 6×6 block):")
    print(f"  {'':>6}", "  ".join(f"{'PC'+str(j):>8}" for j in range(6)))
    for i in range(6):
        vals = "  ".join(f"{G_proj[i,j]:+8.4f}" for j in range(6))
        print(f"  PC{i:<3} {vals}")

    # ── 3. Sectional curvatures ──
    print("\n" + "─" * 72)
    print("§3  SECTIONAL CURVATURES (per PC pair)")
    print("    K(a,b) = curvature of the 2-plane spanned by PCa, PCb")
    print("    Positive = converging geodesics, Negative = diverging")
    print("─" * 72)

    K_sect = sectional_curvatures(zones, n_pcs=8)
    print(f"\n  {'':>6}", "  ".join(f"{'PC'+str(j):>8}" for j in range(8)))
    for i in range(8):
        vals = "  ".join(
            f"{K_sect[i,j]:+8.4f}" if i != j else f"{'---':>8}"
            for j in range(8)
        )
        print(f"  PC{i:<3} {vals}")

    # Highlight strongest curvatures
    pairs = []
    for i in range(8):
        for j in range(i + 1, 8):
            pairs.append((abs(K_sect[i, j]), i, j, K_sect[i, j]))
    pairs.sort(reverse=True)
    print(f"\n  Strongest curvatures:")
    for mag, i, j, val in pairs[:5]:
        sign = "converging" if val > 0 else "diverging"
        print(f"    PC{i}↔PC{j}: K = {val:+.6f} ({sign})")

    # ── 4. Holonomy ──
    print("\n" + "─" * 72)
    print("§4  HOLONOMY (parallel transport deficit)")
    print("    How much does the crystal basis rotate A→B→C vs A→C direct?")
    print("─" * 72)

    holo = parallel_transport_holonomy(zones)
    print(f"\n  Holonomy Frobenius norm: {holo['holonomy_norm']:.6f}")

    H = holo["holonomy_eigbasis"]
    print(f"\n  Holonomy in Zone B eigenbasis (top 6×6):")
    print(f"  {'':>6}", "  ".join(f"{'PC'+str(j):>8}" for j in range(6)))
    for i in range(6):
        vals = "  ".join(f"{H[i,j]:+8.5f}" for j in range(6))
        print(f"  PC{i:<3} {vals}")

    # The diagonal tells us how much each PC is stretched/compressed
    # The off-diagonal tells us how much PCs rotate into each other
    print(f"\n  Per-PC holonomy (diagonal = stretch, should be 0 if flat):")
    for i in range(8):
        print(f"    PC{i}: {H[i,i]:+.6f}")

    # ── 5. Student position analysis ──
    print("\n" + "─" * 72)
    print("§5  STUDENT vs GEODESIC")
    print("    Where does the student sit relative to the curved manifold?")
    print("─" * 72)

    # Project student into eigenbasis
    S_proj = eigvecs_B.T @ student @ eigvecs_B

    # Compare student diagonal to zone diagonals in eigenbasis
    zA_proj = eigvecs_B.T @ zones[0] @ eigvecs_B
    zB_proj = eigvecs_B.T @ zones[1] @ eigvecs_B  # should be diagonal
    zC_proj = eigvecs_B.T @ zones[2] @ eigvecs_B
    geo_proj = eigvecs_B.T @ g_geo @ eigvecs_B

    print(f"\n  Eigenvalues in Zone B basis:")
    print(f"  {'PC':>4} {'Zone_A':>8} {'Zone_B':>8} {'Zone_C':>8} "
          f"{'Geodesic':>8} {'Student':>8} {'Stu-Geo':>8}")
    for i in range(8):
        print(f"  PC{i:<2} {zA_proj[i,i]:+8.4f} {zB_proj[i,i]:+8.4f} "
              f"{zC_proj[i,i]:+8.4f} {geo_proj[i,i]:+8.4f} "
              f"{S_proj[i,i]:+8.4f} {S_proj[i,i]-geo_proj[i,i]:+8.4f}")

    # Off-diagonal coupling (the crosstalk we diagnosed)
    print(f"\n  Key off-diagonal couplings in student (should be 0):")
    coupling_pairs = [(0, 2), (1, 3), (0, 1), (2, 3), (0, 3), (1, 2)]
    for i, j in coupling_pairs:
        print(f"    PC{i}↔PC{j}: student={S_proj[i,j]:+.4f} "
              f"target(B)={zB_proj[i,j]:+.4f} "
              f"geodesic={geo_proj[i,j]:+.4f}")

    # ── 6. Loss landscape comparison ──
    print("\n" + "─" * 72)
    print("§6  LOSS LANDSCAPE: FLAT vs CURVED TARGETS")
    print("    What would a curvature-aware loss look like?")
    print("─" * 72)

    # Current loss: sum of MSE to each zone (flat)
    flat_loss = sum(np.mean((student - z) ** 2) for z in zones) / 3

    # Geodesic-aware: MSE to geodesic midpoint only
    geo_loss = np.mean((student - g_geo) ** 2)

    # Curvature-weighted: weight each zone by its curvature contribution
    # Zones with more curvature need less weight (they're further from flat)
    K_norms = []
    for i in range(3):
        if i == 0:
            Ki = -0.5 * (zones[1] - zones[0])
        elif i == 2:
            Ki = -0.5 * (zones[2] - zones[1])
        else:
            Ki = -0.5 * 0.5 * (zones[2] - zones[0])
        K_norms.append(norm(Ki, "fro"))

    K_total = sum(K_norms)
    curv_weights = [1.0 - k / K_total for k in K_norms]
    w_total = sum(curv_weights)
    curv_weights = [w / w_total for w in curv_weights]

    curv_loss = sum(
        w * np.mean((student - z) ** 2)
        for w, z in zip(curv_weights, zones)
    )

    print(f"\n  Flat loss (equal zone avg):     {flat_loss:.6f}")
    print(f"  Geodesic loss (midpoint only):  {geo_loss:.6f}")
    print(f"  Curvature-weighted loss:        {curv_loss:.6f}")
    print(f"  Curvature weights: A={curv_weights[0]:.3f} "
          f"B={curv_weights[1]:.3f} C={curv_weights[2]:.3f}")

    # ── 7. Summary ──
    print("\n" + "=" * 72)
    print("  SUMMARY")
    print("=" * 72)
    print(f"""
  Manifold curvature:
    Scalar R = {curv['R_scalar']:.4f}
    G_zz = {curv['G_zz']:.4f}
    Holonomy = {holo['holonomy_norm']:.4f}

  Geodesic test:
    geo_MSE / lin_MSE = {err_geo / err_lin:.4f}
    {'CURVED' if err_geo < err_lin else 'FLAT'} manifold
    {'→ Einstein tensor IS informative' if err_geo < err_lin else '→ Einstein tensor adds little'}

  Strongest sectional curvatures:""")
    for mag, i, j, val in pairs[:3]:
        print(f"    PC{i}↔PC{j}: {val:+.6f}")

    print(f"""
  Student-geodesic distance: {np.sqrt(np.mean((student - g_geo)**2)):.4f}
  Student-ZoneB distance:    {np.sqrt(err_student_B):.4f}

  Implication for loss design:
    If geo/lin < 0.9: manifold is significantly curved.
      → Geodesic-based loss would be better than per-zone MSE.
      → Einstein tensor captures structure that flat targets miss.
    If geo/lin ≈ 1.0: manifold is approximately flat.
      → Current Zone-B-only parity is sufficient.
      → Curvature effects are negligible.
""")


if __name__ == "__main__":
    main()
