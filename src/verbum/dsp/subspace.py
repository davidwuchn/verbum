"""verbum.dsp.subspace — centroids, participation ratio, role subspaces, energy.

L0: pure numpy. No torch, no I/O, no model, no experiment logic.

Harvested (>=2 users each):
- participation_ratio, centroids, centroid_pr, nearest_centroid_acc
      <- scripts/explore/type_lattice_geometry.py (1a)
- role_subspace, subspace_energy, layer_geometry
      <- wrapper/type_zone_ablation.py (1b; layer_geometry reused verbatim by
         type_qk_alignment.py through a sys.path hack — the import-topology
         smell the design page counts)
"""
from __future__ import annotations

import numpy as np

__all__ = [
    "centroid_pr",
    "centroids",
    "layer_geometry",
    "nearest_centroid_acc",
    "participation_ratio",
    "role_subspace",
    "subspace_energy",
]


def participation_ratio(sv: np.ndarray) -> float:
    """Effective number of components from singular values (scale-free)."""
    sv = sv[sv > 1e-12]
    if sv.size == 0:
        return 0.0
    return float((sv.sum() ** 2) / (sv ** 2).sum())


def centroids(x: np.ndarray, y: np.ndarray, labels: list[str]):
    """Per-label mean rows (labels present only, >=2 items). -> (C, present)."""
    rows, present = [], []
    for lab in labels:
        m = y == lab
        if m.sum() >= 2:
            rows.append(x[m].mean(axis=0))
            present.append(lab)
    return np.array(rows), present


def centroid_pr(x: np.ndarray, y: np.ndarray, labels: list[str]) -> float:
    """PR of the centered centroid cloud (needs >=3 present labels)."""
    c, present = centroids(x, y, labels)
    if len(present) < 3:
        return float("nan")
    cc = c - c.mean(axis=0, keepdims=True)
    sv = np.linalg.svd(cc, compute_uv=False)
    return participation_ratio(sv)


def nearest_centroid_acc(x: np.ndarray, y: np.ndarray, labels: list[str]) -> float:
    """Leave-nothing-out nearest-centroid accuracy (separation sanity, not CV)."""
    c, present = centroids(x, y, labels)
    if len(present) < 2:
        return float("nan")
    idx = {lab: i for i, lab in enumerate(present)}
    mask = np.array([t in idx for t in y])
    xs, ys = x[mask], y[mask]
    d = np.linalg.norm(xs[:, None, :] - c[None, :, :], axis=2)
    pred = np.array(present)[d.argmin(axis=1)]
    return float((pred == ys).mean())


def role_subspace(geo: dict, types: list[str]) -> np.ndarray | None:
    """Orthonormal basis (k, D) of span{c_type - grand_mean} in std space.

    geo needs keys: present (list[str]), centroids ((n, D) array)."""
    present = geo["present"]
    idx = {t: i for i, t in enumerate(present)}
    if not all(t in idx for t in types):
        return None
    c = geo["centroids"]
    grand = c.mean(axis=0)
    rows = np.stack([c[idx[t]] - grand for t in types])
    q, _ = np.linalg.qr(rows.T)          # (D, k) orthonormal columns
    return q.T                            # (k, D)


def subspace_energy(z: np.ndarray, sd: np.ndarray, q: np.ndarray) -> float:
    """Full-projection REMOVED energy per token: mean ||((z Q^T) Q) * sd||^2.

    Realized (not planned) energy accounting — the 1b dose-matching lesson."""
    delta = (z @ q.T) @ q                 # (N, D) std-space removal
    return float(np.mean(np.sum((delta * sd) ** 2, axis=1)))


def layer_geometry(x: np.ndarray, y: np.ndarray, rng, n_null: int,
                   label_order: list[str] | None = None) -> dict:
    """Standardize -> centroid SVD -> PR + shuffled-label null; keep z for energy.

    The 1b-v4 form, verbatim, with the label set parameterized (the harvested
    original closed over TYPE_ORDER). Returns the geo dict consumed by
    role_subspace / subspace_energy / map_basis downstream."""
    labels = label_order if label_order is not None else sorted(set(y.tolist()))
    mu = x.mean(axis=0)
    sd = x.std(axis=0) + 1e-6
    z = (x - mu) / sd

    def pr_of(lab_arr):
        c, present = centroids(z, lab_arr, labels)
        if len(present) < 3:
            return float("nan"), None, None
        cc = c - c.mean(axis=0, keepdims=True)
        sv = np.linalg.svd(cc, compute_uv=False)
        return participation_ratio(sv), present, c

    pr_real, present, c = pr_of(y)
    null = []
    for _ in range(n_null):
        prn, _, _ = pr_of(rng.permutation(y))
        if not np.isnan(prn):
            null.append(prn)
    null = np.array(null)
    p = float(np.mean(null <= pr_real)) if null.size else None
    return {"mu": mu, "sd": sd, "z": z, "present": present, "centroids": c,
            "pr_real": float(pr_real), "p_lowrank": p,
            "pr_null_mean": float(null.mean()) if null.size else None}
