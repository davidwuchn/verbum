"""Textbook Dynamic Mode Decomposition (DMD) for residual-stream trajectories.

Exact DMD after Schmid, "Dynamic mode decomposition of numerical and
experimental data", J. Fluid Mech. 656 (2010) 5-28, and Tu, Rowley, Luchtenburg,
Brunton & Kutz, "On dynamic mode decomposition: theory and applications",
J. Comput. Dyn. 1 (2014) 391-421. Economy SVD / pseudoinverse per Golub &
Van Loan, "Matrix Computations" (4th ed., 2013).

This module is written for verbum directly from those textbook sources. It is
NOT derived from, and does not vendor, any third-party implementation (see
operator-geometry-la-toolkit.md §0b FTO rule). All operations are public-domain
linear algebra (SVD, eig, least squares) that predate any branded pipeline by
decades.

Given snapshot pairs X' ~ T X (columns = consecutive states), we estimate the
transport operator T in a rank-r POD (SVD) subspace:

    X = U S V^T  (economy) ;  A_tilde = U_r^T X' V_r S_r^{-1} ;  eig(A_tilde)

The DMD eigenvalues are eig(A_tilde); |lambda|<1 = contracting, |lambda|~1 =
persistent, phase(lambda) = per-step rotation.

License: MIT.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "economy_svd",
    "lstsq_operator",
    "operator_cosine",
    "pca_basis",
    "reduced_dmd",
    "reduced_rel_from_grams",
    "rel_residual",
]


def economy_svd(X: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Economy SVD X = U S Vt (Golub & Van Loan)."""
    return np.linalg.svd(X, full_matrices=False)


def rel_residual(X: np.ndarray, Xp: np.ndarray, T: np.ndarray) -> float:
    """Relative Frobenius residual ||X' - T X||_F / ||X'||_F."""
    denom = float(np.linalg.norm(Xp))
    if denom == 0.0:
        return 0.0
    return float(np.linalg.norm(Xp - T @ X) / denom)


def reduced_dmd(X: np.ndarray, Xp: np.ndarray, rank: int) -> dict:
    """Exact reduced DMD of the pair (X, X') at truncation `rank`.

    X, Xp: (n_features, n_pairs), real. Returns a dict with:
      eigvals   : complex DMD eigenvalues (rank r)
      abs_eig   : |eigvals|
      phase     : angle(eigvals)
      rel_resid : ||X' - A_proj X||_F / ||X'||_F, A_proj = U_r A_tilde U_r^T
      r         : effective rank used
      A_tilde   : (r, r) reduced operator
      Ur        : (n_features, r) POD basis
    """
    U, s, Vt = economy_svd(X)
    r = int(min(rank, np.count_nonzero(s > s.max() * 1e-10))) if s.size else 0
    if r == 0:
        return {
            "eigvals": np.zeros(0, complex), "abs_eig": np.zeros(0),
            "phase": np.zeros(0), "rel_resid": 1.0, "r": 0,
            "A_tilde": np.zeros((0, 0)), "Ur": np.zeros((X.shape[0], 0)),
        }
    Ur = U[:, :r]
    sr = s[:r]
    Vr = Vt[:r].conj().T
    A_tilde = Ur.conj().T @ Xp @ Vr @ np.diag(1.0 / sr)
    eigvals = np.linalg.eigvals(A_tilde)
    A_proj = Ur @ A_tilde @ Ur.conj().T
    rel = rel_residual(X, Xp, A_proj)
    return {
        "eigvals": eigvals,
        "abs_eig": np.abs(eigvals),
        "phase": np.angle(eigvals),
        "rel_resid": rel,
        "r": r,
        "A_tilde": A_tilde,
        "Ur": Ur,
    }


def lstsq_operator(X: np.ndarray, Xp: np.ndarray, ridge: float = 0.0) -> np.ndarray:
    """Full least-squares operator T = X' X^+ (optionally ridge-regularised).

    Used for per-layer operators expressed in a COMMON fixed basis so that
    T_layer and T_global are directly comparable (operator_cosine). Requires
    n_pairs >= n_features for a well-posed fit.
    """
    XtX = X @ X.T
    if ridge > 0.0:
        XtX = XtX + ridge * np.eye(XtX.shape[0])
    return Xp @ X.T @ np.linalg.pinv(XtX)


def operator_cosine(A: np.ndarray, B: np.ndarray) -> float:
    """Cosine similarity of two operators, vectorised (Frobenius inner prod)."""
    a = A.ravel()
    b = B.ravel()
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def reduced_rel_from_grams(
    Cxx: np.ndarray, Cxpx: np.ndarray, Cxpxp: np.ndarray, rank: int
) -> float:
    """Rank-r reduced-DMD relative residual from Gram matrices (P x P).

    Method-of-snapshots on the small feature dimension P: the POD basis is the
    top eigenvectors of Cxx = X X^T (P x P), so the whole rank-r residual
    ||X' - U_r A_tilde U_r^T X||_F / ||X'||_F is computed in P x P work with no
    P x N SVD. Mathematically identical to reduced_dmd's rel_resid; used for the
    O(n_perm) shuffled-layer null where a per-permutation SVD is prohibitive.

    Cxx = X X^T, Cxpx = X' X^T, Cxpxp = X' X'^T (all P x P).
    """
    w, Q = np.linalg.eigh(Cxx)  # ascending, symmetric PSD
    order = np.argsort(w)[::-1]
    w = w[order]
    Q = Q[:, order]
    wmax = float(w[0]) if w.size else 0.0
    npos = int(np.count_nonzero(w > wmax * 1e-10)) if wmax > 0 else 0
    r = int(min(rank, npos))
    if r == 0:
        return 1.0
    Ur = Q[:, :r]
    s2 = w[:r]
    A_tilde = (Ur.T @ Cxpx @ Ur) / s2[np.newaxis, :]  # r x r
    A_proj = Ur @ A_tilde @ Ur.T                        # P x P
    num = (
        float(np.trace(Cxpxp))
        - 2.0 * float(np.sum(Cxpx * A_proj))
        + float(np.sum((A_proj @ Cxx) * A_proj))
    )
    den = float(np.trace(Cxpxp))
    if den <= 0.0:
        return 0.0
    return float(np.sqrt(max(0.0, num)) / np.sqrt(den))


def pca_basis(
    S: np.ndarray, n_components: int, seed: int = 0
) -> tuple[np.ndarray, np.ndarray, float]:
    """Deterministic PCA basis of snapshot matrix S (n_snapshots, n_features).

    Returns (components (n_features, P), mean (n_features,), var_explained).
    Centres S, takes the top-P right singular vectors. Deterministic (no
    randomness; `seed` reserved for API symmetry).
    """
    mean = S.mean(axis=0)
    Sc = S - mean
    _, sv, Vt = np.linalg.svd(Sc, full_matrices=False)
    p = int(min(n_components, Vt.shape[0]))
    comps = Vt[:p].T  # (n_features, P)
    total = float(np.sum(sv**2))
    var_explained = float(np.sum(sv[:p] ** 2) / total) if total > 0 else 0.0
    return comps, mean, var_explained
