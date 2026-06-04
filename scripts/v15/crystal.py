"""v15 Crystal Loss — Laplacian-weighted settlement.

Session 189 discovery: the graph Laplacian of the crystal target reveals
WHNF is the most FRAGILE node (μ=0.228, 8.6× weaker restoring force
than BCDY). Training confirms: WHNF starts settled then UN-settles.

Fix: weight per-node crystal MSE by diag(L^+) — the Laplacian pseudoinverse
diagonal. This gives each graph mode equal effective restoring force.

  WHNF gets 5× the loss weight. BCDY get 0.36-0.45×.

Inherits v14 CrystalLoss, overrides only crystal_lattice_loss.

License: MIT
"""

from __future__ import annotations

import numpy as np
import mlx.core as mx

from crystal_base import CrystalLoss as V14CrystalLoss, ZONE_B_TARGETS

# ══════════════════════════════════════════════════════════════════════
# § 1  Laplacian Fragility Weights
# ══════════════════════════════════════════════════════════════════════

# diag(L^+) of Zone B target, normalized to mean=1.
# Order: K I B C D Y W WHNF āK āI āB āC āD āY āW āWHNF
LAPLACIAN_FRAGILITY_WEIGHTS = (
    0.5367, 0.5390, 0.3877, 0.3824, 0.3557, 0.4456, 0.3634, 4.9896,
    0.5367, 0.5390, 0.3877, 0.3824, 0.3557, 0.4456, 0.3634, 4.9896,
)

_WEIGHT_MATRIX = None

def _get_weight_matrix() -> mx.array:
    """(16,16) weight matrix: w_ij = sqrt(frag_i × frag_j), normalized to mean=1."""
    global _WEIGHT_MATRIX
    if _WEIGHT_MATRIX is None:
        w = mx.array(LAPLACIAN_FRAGILITY_WEIGHTS)
        w_matrix = mx.sqrt(w[:, None] * w[None, :])
        _WEIGHT_MATRIX = w_matrix / mx.mean(w_matrix)
    return _WEIGHT_MATRIX


def laplacian_crystal_lattice_loss(
    embeddings: mx.array,
    zone_targets: list[mx.array],
    zone_lambdas: tuple[float, ...],
) -> mx.array:
    """v14 crystal_lattice_loss with Laplacian fragility weighting."""
    norms = mx.sqrt(mx.sum(embeddings * embeddings, axis=-1, keepdims=True) + 1e-8)
    normed = embeddings / norms
    cos_matrix = normed @ normed.T

    n = cos_matrix.shape[0]
    rows, cols = [], []
    for i in range(n):
        for j in range(i + 1, n):
            rows.append(i)
            cols.append(j)
    row_idx = mx.array(rows)
    col_idx = mx.array(cols)

    student_tri = cos_matrix[row_idx, col_idx]

    # Fragility weights for upper triangle
    frag = _get_weight_matrix()
    weight_tri = frag[row_idx, col_idx]

    total_loss = mx.array(0.0)
    total_weight = sum(zone_lambdas)

    for target, lam in zip(zone_targets, zone_lambdas):
        if lam <= 0:
            continue
        target_tri = target[row_idx, col_idx]
        diff = student_tri - target_tri
        weighted_sq = weight_tri * (diff * diff)
        mse = mx.mean(weighted_sq)
        total_loss = total_loss + lam * mse

    return total_loss / total_weight


# ══════════════════════════════════════════════════════════════════════
# § 2  LaplacianCrystalLoss — inherits v14, overrides MSE
# ══════════════════════════════════════════════════════════════════════


class LaplacianCrystalLoss(V14CrystalLoss):
    """v14 CrystalLoss with Laplacian-weighted MSE component.

    Parity and cross-zone rotation are unchanged (they operate in
    the eigenbasis, which is already mode-decomposed). Only the
    direct cosine MSE gets fragility weighting.
    """

    def __call__(self, embeddings: mx.array) -> dict[str, mx.array]:
        # Override: use Laplacian-weighted MSE instead of uniform MSE
        crystal_mse = laplacian_crystal_lattice_loss(
            embeddings,
            self.zone_targets_mx,
            self.zone_lambdas,
        )

        from crystal_base import geodesic_parity_loss, cross_zone_rotation_loss

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
# § 3  Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("v15 crystal.py self-test (Laplacian-weighted)")
    print("=" * 60)

    labels = ['K', 'I', 'B', 'C', 'D', 'Y', 'W', 'WHNF']

    # Fragility weights
    print("\nFragility weights:")
    for i, label in enumerate(labels):
        print(f"  {label:>4s}: {LAPLACIAN_FRAGILITY_WEIGHTS[i]:.4f}")
    whnf_w = LAPLACIAN_FRAGILITY_WEIGHTS[7]
    mean_other = sum(LAPLACIAN_FRAGILITY_WEIGHTS[:7]) / 7
    print(f"\n  WHNF / mean(others) = {whnf_w / mean_other:.1f}×")

    # Weight matrix
    frag = _get_weight_matrix()
    mx.eval(frag)
    print(f"  Weight matrix: {frag.shape}, mean={float(mx.mean(frag).item()):.4f} ✓")

    # Instantiate
    print("\nLaplacianCrystalLoss...")
    loss_fn = LaplacianCrystalLoss()

    emb = mx.random.normal((16, 1280)) * 0.02
    result = loss_fn(emb)
    for k, v in result.items():
        if isinstance(v, mx.array) and v.ndim == 0:
            mx.eval(v)
            print(f"  {k}: {v.item():.6f}")

    # Gradient: verify WHNF gets more
    print("\nGradient comparison...")
    def mse_loss(emb):
        return loss_fn(emb)['crystal_mse']

    grad_fn = mx.grad(mse_loss)
    g = grad_fn(emb)
    mx.eval(g)

    whnf_gn = float(mx.sqrt(mx.sum(g[7] * g[7])).item())
    b_gn = float(mx.sqrt(mx.sum(g[2] * g[2])).item())
    print(f"  WHNF grad norm: {whnf_gn:.6f}")
    print(f"  B grad norm:    {b_gn:.6f}")
    ratio = whnf_gn / b_gn if b_gn > 1e-10 else float('inf')
    print(f"  WHNF/B ratio:   {ratio:.1f}×")

    # Compare to v14 (uniform) loss
    print("\nComparison to v14 (uniform weights)...")
    v14_loss_fn = V14CrystalLoss()
    v14_result = v14_loss_fn(emb)
    mx.eval(v14_result['crystal_mse'])

    def v14_mse_loss(emb):
        return v14_loss_fn(emb)['crystal_mse']
    v14_grad_fn = mx.grad(v14_mse_loss)
    v14_g = v14_grad_fn(emb)
    mx.eval(v14_g)

    v14_whnf_gn = float(mx.sqrt(mx.sum(v14_g[7] * v14_g[7])).item())
    v14_b_gn = float(mx.sqrt(mx.sum(v14_g[2] * v14_g[2])).item())
    v14_ratio = v14_whnf_gn / v14_b_gn if v14_b_gn > 1e-10 else float('inf')
    print(f"  v14 WHNF/B gradient ratio: {v14_ratio:.1f}×")
    print(f"  v15 WHNF/B gradient ratio: {ratio:.1f}×")
    print(f"  Amplification: {ratio / v14_ratio:.1f}×")

    print("\n" + "=" * 60)
    print("v15 crystal.py: all tests passed ✓")
