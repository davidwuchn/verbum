"""verbum.dsp.gain — matched-filter gains, gain laws, dose accounting.

L0: pure numpy. No torch, no I/O, no model, no experiment logic.

Harvested:
- head_gain_ratios <- scripts/explore/type_qk_alignment.py (QK; the per-head
  Frobenius-normalized matched-filter statistic, rho=1 == analytic
  random-direction expectation)
- gain_law / g_of  <- scripts/explore/analyze_type1c_darkfield.py (1c),
  de-experiment-ified: the harvested fit_gain_law read the 1c verdict JSON;
  here anchors are passed as arrays (dsp = tools, not experiment logic).
  Frozen 1c semantics preserved: anchors from a DECLARED reference condition
  only, piecewise-linear interpolation in log realized E, clamped outside.
"""
from __future__ import annotations

import numpy as np

__all__ = ["g_of", "gain_law", "head_gain_ratios"]


def head_gain_ratios(w: np.ndarray, bases: list[np.ndarray],
                     head_dim: int) -> list[float]:
    """Frobenius-normalized per-head gain, one scalar per basis.

    w: (H*head_dim, D). Each basis: (k, D) orthonormal rows in the space w reads.
    rho(head, vec) = D*||w_h v||^2/||w_h||^2_F; mean over heads AND basis rows
    (rho = 1 == analytic random-direction expectation). One stacked GEMM."""
    n_out, d = w.shape
    h = n_out // head_dim
    stack = np.concatenate(bases, axis=0)                       # (K, D)
    proj = (w @ stack.T).reshape(h, head_dim, -1)               # (H, dh, K)
    ph = (proj ** 2).sum(axis=1)                                # (H, K)
    fro = (w.reshape(h, head_dim, d) ** 2).sum(axis=(1, 2)) + 1e-12
    rho = (d * ph / fro[:, None]).mean(axis=0)                  # (K,) mean over heads
    out, i = [], 0
    for b in bases:
        k = b.shape[0]
        out.append(float(rho[i:i + k].mean()))
        i += k
    return out


def gain_law(realized_e: np.ndarray, retention: np.ndarray
             ) -> tuple[np.ndarray, np.ndarray]:
    """Anchor points (log_e, ret) for g(E), sorted by E.

    realized_e: REALIZED energies of the reference condition (the 1c frozen
    rule: the reference/anchor condition is declared by the caller — e.g.
    'random only' — the library does not choose it). retention: matching
    retention values. Returns arrays ready for g_of."""
    e = np.asarray(realized_e, dtype=float)
    r = np.asarray(retention, dtype=float)
    order = np.argsort(e)
    return np.log(e[order]), r[order]


def g_of(log_e_anchors: np.ndarray, ret_anchors: np.ndarray, e: float) -> float:
    """Monotone (piecewise-linear, clamped) interpolation in log E."""
    return float(np.interp(np.log(e), log_e_anchors, ret_anchors))
