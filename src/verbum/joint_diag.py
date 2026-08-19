"""Orthogonal joint (simultaneous) diagonalization of real symmetric matrices.

Textbook Jacobi-angle method: Cardoso & Souloumiac, "Jacobi angles for
simultaneous diagonalization" (SIAM J. Matrix Anal. Appl. 17(1), 1996), reduced
to the real-symmetric case via the two-sided Givens sweep (Golub & Van Loan,
Matrix Computations, sec. 8.5). Public-domain linear algebra written as our own
function; NO CBLL code (operator-geometry-la-toolkit.md sec 0b, FTO-clean).

Given a stack of real symmetric matrices {A_k}, find one orthogonal V that
minimises the total off-diagonal energy Sum_k offdiag(V^T A_k V)^2. If the A_k
share a common eigenframe, V recovers it and the residual is ~0; the residual
measures departure from a common frame (= the "invariant switch basis" the route
map needs, gram-registers-and-the-route-map.md sec route-map).

License: MIT.
"""

from __future__ import annotations

import numpy as np


def _offdiag_energy(a: np.ndarray) -> float:
    """Sum over the stack of squared off-diagonal entries."""
    n = a.shape[-1]
    mask = ~np.eye(n, dtype=bool)
    return float(np.sum(a[:, mask] ** 2))


def joint_diagonalize(
    mats: np.ndarray, tol: float = 1e-10, max_sweeps: int = 200
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Orthogonal joint diagonalization of a stack of real symmetric matrices.

    mats: (K, n, n) real symmetric. Returns (V (n,n) orthogonal, A_out (K,n,n)
    = V^T mats V, info). Per Jacobi pair (p,q) the off-diagonal element after a
    Givens rotation by theta is  cos2t * a_k - sin2t * d_k  with a_k = A_k[p,q],
    d_k = (A_k[p,p]-A_k[q,q])/2, for the two-sided Givens G=[[c,s],[-s,c]] used
    below (A'[p,q] = a_k*cos2t + d_k*sin2t). Minimising Sum_k that^2 over unit
    (cos2t,sin2t) is the smallest eigenvector of M = Sum_k [a_k,d_k][a_k,d_k]^T.
    """
    a = np.array(mats, dtype=np.float64, copy=True)
    if a.ndim != 3 or a.shape[1] != a.shape[2]:
        raise ValueError(f"expected (K,n,n), got {a.shape}")
    _, n, _ = a.shape
    v = np.eye(n)
    n_sweeps = 0
    active = np.inf
    for sweep in range(max_sweeps):
        n_sweeps = sweep + 1
        active = 0.0
        for p in range(n - 1):
            for q in range(p + 1, n):
                apq = a[:, p, q]
                d = 0.5 * (a[:, p, p] - a[:, q, q])
                m00 = float(apq @ apq)
                m01 = float(apq @ d)
                m11 = float(d @ d)
                m = np.array([[m00, m01], [m01, m11]])
                _, uu = np.linalg.eigh(m)             # ascending; col 0 smallest
                c2, s2 = uu[0, 0], uu[1, 0]
                if c2 < 0.0:                          # cos2t >= 0 branch
                    c2, s2 = -c2, -s2
                theta = 0.5 * np.arctan2(s2, c2)
                if abs(theta) < 1e-14:
                    continue
                c, s = np.cos(theta), np.sin(theta)
                active = max(active, abs(s))
                # two-sided Givens A <- G^T A G ; columns then rows ; V <- V G
                cp = a[:, :, p].copy()
                cq = a[:, :, q].copy()
                a[:, :, p] = c * cp - s * cq
                a[:, :, q] = s * cp + c * cq
                rp = a[:, p, :].copy()
                rq = a[:, q, :].copy()
                a[:, p, :] = c * rp - s * rq
                a[:, q, :] = s * rp + c * rq
                vp = v[:, p].copy()
                vq = v[:, q].copy()
                v[:, p] = c * vp - s * vq
                v[:, q] = s * vp + c * vq
        if active < tol:
            break
    return v, a, {
        "sweeps": n_sweeps,
        "converged": bool(active < tol),
        "final_active": float(active),
        "offdiag_energy": _offdiag_energy(a),
    }


def diag_energy_fraction(v: np.ndarray, mats: np.ndarray) -> float:
    """Mean over the stack of Sum_i (V^T A_k V)_ii^2 / ||A_k||_F^2 in [0, 1].

    1.0 iff V is a common eigenframe; near the random-rotation floor iff there
    is no shared frame. Normalised per-matrix so the mean is not dominated by
    the largest-norm gram.
    """
    a = np.asarray(mats, dtype=np.float64)
    fracs = []
    for ak in a:
        b = v.T @ ak @ v
        den = float(np.sum(ak * ak))
        if den > 0.0:
            fracs.append(float(np.sum(np.diag(b) ** 2)) / den)
    return float(np.mean(fracs)) if fracs else 0.0


def dc_remove(grams: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Project the shared DC ('everything-correlates') mode out of a gram stack.

    The top eigenvector of the MEAN gram is the common all-positive direction
    (eigval ~2.4-3.9 >> 1 for the route grams); it is a trivial shared frame
    axis carrying no routing structure. Returns the stack expressed in the
    (n-1)-dim orthonormal complement Q (columns = the mean gram's non-top
    eigenvectors) plus Q itself. Same discipline as the s341 mean-centering.
    """
    g = np.asarray(grams, dtype=np.float64)
    gbar = g.mean(axis=0)
    _, u = np.linalg.eigh(gbar)                       # ascending eigenvalues
    q = u[:, :-1]                                      # drop top (DC) eigenvector
    gp = np.einsum("ij,kjl,lm->kim", q.T, g, q)        # (K, n-1, n-1)
    gp = 0.5 * (gp + np.transpose(gp, (0, 2, 1)))      # re-symmetrize
    return gp, q


def random_orthogonal(n: int, rng: np.random.Generator) -> np.ndarray:
    """Haar-ish random orthogonal n x n via QR of a Gaussian (sign-fixed)."""
    a = rng.standard_normal((n, n))
    qm, rm = np.linalg.qr(a)
    qm *= np.sign(np.diag(rm))
    return qm


def common_frame_fraction(grams: np.ndarray) -> tuple[float, dict]:
    """D_joint on the DC-removed stack: (fraction in [0,1], info)."""
    gp, q = dc_remove(grams)
    v, _, info = joint_diagonalize(gp)
    d = diag_energy_fraction(v, gp)
    return d, {"jd": info, "n_sub": int(gp.shape[1]), "V": v, "Q": q, "Gp": gp}
