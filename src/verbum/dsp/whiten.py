"""verbum.dsp.whiten — conditioning: standardization, whitening, space transport.

L0: pure numpy. No torch, no I/O, no model, no experiment logic.

Harvested (>=2 users each, per the design contract):
- standardize        <- scripts/explore/type_lattice_geometry.py (1a; the
                        massive-activation / rogue-dimension lesson, once)
- standardize_stats  <- wrapper/type_zone_ablation.py layer_geometry inline (1b)
- whiten_cov         <- scripts/v12/basin_whitened_exp.py
- map_basis          <- scripts/explore/type_qk_alignment.py (QK; std-space ->
                        attention-read-in-space direction transport)
"""
from __future__ import annotations

import numpy as np

__all__ = ["map_basis", "standardize", "standardize_stats", "whiten_cov"]


def standardize(x: np.ndarray) -> np.ndarray:
    """Per-dimension z-score (diagonal whitening).

    Removes the massive-activation / rogue-dimension artifact that dominates raw
    mid/late residual norms and collapses Euclidean centroid geometry
    (λ measure: match the space the linear probe uses)."""
    mu = x.mean(axis=0, keepdims=True)
    sd = x.std(axis=0, keepdims=True) + 1e-6
    return (x - mu) / sd


def standardize_stats(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """standardize + the (mu, sd) needed to transport directions back to raw
    space (the 1b layer_geometry form). Returns (z, mu, sd), 1-D mu/sd."""
    mu = x.mean(axis=0)
    sd = x.std(axis=0) + 1e-6
    return (x - mu) / sd, mu, sd


def whiten_cov(x: np.ndarray, reg: float = 1e-6) -> np.ndarray:
    """Full-covariance (ZCA-style, eigendecomposition) whitening.

    Heavier than standardize(); use when off-diagonal correlations matter
    (basin/v12 lineage). reg regularizes small eigenvalues."""
    mu = x.mean(axis=0, keepdims=True)
    xc = x - mu
    cov = (xc.T @ xc) / max(len(xc) - 1, 1)
    w, v = np.linalg.eigh(cov)
    w = np.maximum(w, reg)
    return xc @ (v / np.sqrt(w)) @ v.T


def map_basis(basis_std: np.ndarray, sd: np.ndarray, gamma: np.ndarray) -> np.ndarray:
    """Std-space orthonormal basis (k, D) -> attention-input-space orthonormal basis.

    A std-space direction v corresponds to raw displacement v * sd; RMSNorm maps
    a displacement to (delta/rms) * gamma and the scalar rms drops out of a
    direction, so v_attn prop-to (v * sd) * gamma. Rows mapped then QR'd."""
    m = basis_std * (sd * gamma)[None, :]
    q, _ = np.linalg.qr(m.T)                  # (D, k) orthonormal columns
    return np.ascontiguousarray(q.T)          # (k, D)
