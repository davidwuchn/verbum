"""verbum.dsp.nulls — the yardstick layer: null constructors + the gate.

L1: pure numpy. No torch, no I/O, no model, no experiment logic.

Structural yardstick (λ yardstick, by construction):
- you cannot obtain a p-value from this library without declaring BOTH the
  null (a NullDraws) and the predicted direction ('greater' | 'less') first;
- sign discipline is enforced by shape: a significant p with the WRONG sign is
  verdict=False, never flipped, never rescued;
- register tags (λ measure) are warning-only: a mismatch writes to the
  warnings field and stderr — it NEVER mutates value, p, or verdict inputs.

Constructors return draws + provenance; the caller computes the observed
statistic; gate() compares. Nothing here decides what an experiment means —
verdict semantics beyond pass/fail belong to the instrument (design decision 3).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from enum import Enum

import numpy as np

__all__ = [
    "Gated",
    "NullDraws",
    "Register",
    "gate",
    "matched_random",
    "matched_range",
    "paired_permutation",
    "shuffled_label",
    "sign_flip",
]


class Register(Enum):
    """λ measure verbatim: name the register before you build the probe."""
    routing = "routing"        # crisp/discrete: attention patterns, head selection
    value = "value"            # continuous/graded: residual content, subspaces
    contrast = "contrast"      # dark-field / difference channels (Q/M)
    magnitude = "magnitude"    # norms, energies, doses
    spectral = "spectral"      # eigen/singular structure
    causal = "causal"          # intervention -> outcome


@dataclass(frozen=True)
class NullDraws:
    """Draws from a declared null + provenance (recorded at construction)."""
    name: str
    draws: np.ndarray
    provenance: dict = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self, "draws", np.asarray(self.draws, dtype=float))
        if self.draws.size == 0:
            raise ValueError(f"null '{self.name}' produced zero draws")


@dataclass(frozen=True)
class Gated:
    """The only object that carries a p-value. warnings NEVER alter data."""
    name: str
    value: float
    null_name: str
    null_mean: float
    null_std: float
    n_draws: int
    predict: str
    alpha: float
    p: float
    sign_ok: bool
    verdict: bool
    warnings: tuple[str, ...] = ()


def gate(value: float, null: NullDraws, predict: str, alpha: float = 0.05,
         name: str = "", claim_register: Register | None = None,
         probe_register: Register | None = None) -> Gated:
    """Compare an observed statistic against a declared null, directionally.

    predict: 'greater' (value predicted above null) or 'less'. Mandatory —
    there is no two-sided option (a prediction has a sign; λ yardstick).
    p is the add-one permutation p in the PREDICTED direction.
    verdict = (p < alpha) AND sign_ok. Wrong-sign extremity is a failure,
    reported verbatim, never flipped."""
    if not isinstance(null, NullDraws):
        raise TypeError("gate() requires a declared NullDraws (no null, no p)")
    if predict not in ("greater", "less"):
        raise ValueError("predict must be 'greater' or 'less' (declared a priori)")
    draws = null.draws
    v = float(value)
    if predict == "greater":
        p = float((1 + np.sum(draws >= v)) / (1 + draws.size))
        sign_ok = v > float(draws.mean())
    else:
        p = float((1 + np.sum(draws <= v)) / (1 + draws.size))
        sign_ok = v < float(draws.mean())
    warnings: list[str] = []
    if claim_register is not None and probe_register is not None \
            and claim_register is not probe_register:
        w = (f"register mismatch: claim={claim_register.value} "
             f"probe={probe_register.value} (s206 scar — verify the probe "
             f"measures the claimed quantity)")
        warnings.append(w)
        print(f"[dsp.gate] WARNING {name}: {w}", file=sys.stderr)
    return Gated(
        name=name, value=v, null_name=null.name,
        null_mean=float(draws.mean()), null_std=float(draws.std()),
        n_draws=int(draws.size), predict=predict, alpha=float(alpha),
        p=p, sign_ok=sign_ok, verdict=bool(p < alpha and sign_ok),
        warnings=tuple(warnings),
    )


# ── constructors ──────────────────────────────────────────────────────────────
def shuffled_label(stat, y: np.ndarray, rng: np.random.Generator,
                   n_iter: int = 200) -> NullDraws:
    """Full shuffled-label pipeline null: stat(permuted labels), n_iter times.

    stat: callable(label_array) -> float. The stat must RERUN the whole
    downstream pipeline on the shuffled labels (the QK lesson: shuffle ->
    centroids -> subspace -> same mapping -> same statistic), not just
    re-score cached intermediates. NaN draws are dropped (recorded)."""
    draws = []
    for _ in range(n_iter):
        v = float(stat(rng.permutation(y)))
        if not np.isnan(v):
            draws.append(v)
    return NullDraws("shuffled_label", np.array(draws),
                     {"n_iter": n_iter, "n_kept": len(draws)})


def matched_random(stat, dim: int, norm: float, rng: np.random.Generator,
                   n_iter: int = 200) -> NullDraws:
    """Matched-norm random-direction null: stat(random unit vector * norm).

    The exact 3b/P-ATT-MED null family: same norm, isotropic direction."""
    draws = []
    for _ in range(n_iter):
        v = rng.standard_normal(dim)
        v *= norm / (np.linalg.norm(v) + 1e-12)
        draws.append(float(stat(v)))
    return NullDraws("matched_random", np.array(draws),
                     {"n_iter": n_iter, "dim": dim, "norm": float(norm)})


def paired_permutation(a: np.ndarray, b: np.ndarray, rng: np.random.Generator,
                       n_iter: int = 10000) -> NullDraws:
    """Paired sign-flip permutation null over mean(a - b) (paired by index).

    The P-TYPE-SWAP s288 arm-vs-arm statistic. Observed value = mean(a - b),
    computed by the caller; draws = mean under random per-pair sign flips."""
    diffs = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(n_iter, diffs.size))
    draws = (signs * diffs[None, :]).mean(axis=1)
    return NullDraws("paired_permutation", draws,
                     {"n_iter": n_iter, "n_pairs": int(diffs.size)})


def sign_flip(values: np.ndarray, rng: np.random.Generator,
              n_iter: int = 10000) -> NullDraws:
    """One-sample sign-flip null over mean(values) (H0: symmetric about 0).

    The 1c residual-sign discipline. Observed value = mean(values)."""
    v = np.asarray(values, dtype=float)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(n_iter, v.size))
    draws = (signs * v[None, :]).mean(axis=1)
    return NullDraws("sign_flip", draws,
                     {"n_iter": n_iter, "n": int(v.size)})


def matched_range(stat, target: np.ndarray, rng: np.random.Generator,
                  n_iter: int = 200) -> NullDraws:
    """Matched-range null for geometric/spectral fits (λ yardstick MANDATORY
    gate for any approximate fit claim): stat(uniform draws over the target's
    observed range, same shape). If random values in the same range fit as
    well, describability != discovery (the s247 φ-ladder lesson)."""
    t = np.asarray(target, dtype=float)
    lo, hi = float(t.min()), float(t.max())
    draws = []
    for _ in range(n_iter):
        draws.append(float(stat(rng.uniform(lo, hi, size=t.shape))))
    return NullDraws("matched_range", np.array(draws),
                     {"n_iter": n_iter, "lo": lo, "hi": hi,
                      "shape": list(t.shape)})
