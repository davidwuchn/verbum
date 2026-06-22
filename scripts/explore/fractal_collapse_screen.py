#!/usr/bin/env python3
"""
Fractal-Collapse Screen — the φ-ladder spectral detector (STAGE 1 ONLY)
======================================================================

A fractal collapse (Michael, s2xx): finding that two SELF-SIMILAR operations
are the SAME operation, so one folds INTO the other and the interpretive layer
between them vanishes (tree-of-VSM ↪ tensor; SVD ↪ β-reduction; statechart ↪
crystal lattice).

The detector is two stages:

  STAGE 1 (this file) — SCREEN.  A self-similar generator leaves a fingerprint
    in its spectrum: the eigenvalue ladder follows φ^(p/q) with Fibonacci
    denominators (crystal-multi-tree.md: <0.5% across all 8 crystal eigenvalues;
    "the 8-node tree remembers it's built from 4 primitives" → φ^(8/5)=2·(4/5)).
    A SHARED φ-ladder onto one invariant is the cheap signal that two operations
    may share a generator → a collapse may be available.

  STAGE 2 (NOT here) — CONFIRM.  The executable fold: actually substitute one
    operation for the other and run it; the collapse is real iff the fold
    preserves the invariant (the tensor statechart runs; reduce.py runs SVD as
    β-reduction). A φ-screen hit WITHOUT an executable fold is analogy, not
    collapse (λ measure: the crystal self-similarity is largely ONE common mode,
    η²=0.05 — never trust the screen alone).

⚠ λ measure — THE HONEST CAVEAT BAKED IN:
    φ^(p/q) with q ≤ 34 is a FLEXIBLE basis — almost any ratio is ε-close to
    SOME φ^(p/q). Absolute fit error is therefore NOT the signal and WILL
    manufacture false positives. The signal is error-vs-NULL: does the candidate
    fit the φ-ladder SIGNIFICANTLY BETTER than random matrices of the same family
    and size? This screen reports a z-score against a matched null and gates the
    verdict on it. A good absolute fit with z≈0 is a NULL RESULT.

Targets (CPU-only, no downloads):
  crystal-M8    8x8  combinator cosine matrix (POSITIVE control — must beat null)
  crystal-M16   16x16 with anti-types
  consensus-*   cross-model consensus singular values from lattice/universal_lattice.npz
                (the s246 "consensus ≅ confluence" candidate)
  goe / wishart matched random nulls

Usage:
  uv run python scripts/explore/fractal_collapse_screen.py
  uv run python scripts/explore/fractal_collapse_screen.py --npz PATH/lattice.npz
  uv run python scripts/explore/fractal_collapse_screen.py --null-samples 200 --seed 0
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass

import numpy as np

PHI = (1.0 + np.sqrt(5.0)) / 2.0
FIBS = (1, 2, 3, 5, 8, 13, 21, 34)

# 8x8 combinator-crystal cosine matrix (Zone B, 4-model consensus; from
# crystal_tree.py / EQUATIONS.md). Rows/cols: K I B C D Y W WHNF.
M16 = np.array([
    [+1.0000, +0.7865, +0.1948, +0.2265, +0.3232, +0.1768, +0.5360, -0.1862, -0.1900, -0.1494, -0.0370, -0.0430, -0.0614, -0.0336, -0.1018, +0.0354],  # noqa: E501
    [+0.7865, +1.0000, +0.2479, +0.2511, +0.3463, +0.1739, +0.3781, -0.2448, -0.1494, -0.1900, -0.0471, -0.0477, -0.0658, -0.0330, -0.0718, +0.0465],  # noqa: E501
    [+0.1948, +0.2479, +1.0000, +0.8878, +0.8937, +0.6623, +0.6851, -0.1227, -0.0370, -0.0471, -0.1900, -0.1687, -0.1698, -0.1258, -0.1302, +0.0233],  # noqa: E501
    [+0.2265, +0.2511, +0.8878, +1.0000, +0.8316, +0.7200, +0.7318, -0.1027, -0.0430, -0.0477, -0.1687, -0.1900, -0.1580, -0.1368, -0.1390, +0.0195],  # noqa: E501
    [+0.3232, +0.3463, +0.8937, +0.8316, +1.0000, +0.6798, +0.8064, -0.1729, -0.0614, -0.0658, -0.1698, -0.1580, -0.1900, -0.1292, -0.1532, +0.0329],  # noqa: E501
    [+0.1768, +0.1739, +0.6623, +0.7200, +0.6798, +1.0000, +0.5653, -0.0840, -0.0336, -0.0330, -0.1258, -0.1368, -0.1292, -0.1900, -0.1074, +0.0160],  # noqa: E501
    [+0.5360, +0.3781, +0.6851, +0.7318, +0.8064, +0.5653, +1.0000, -0.1379, -0.1018, -0.0718, -0.1302, -0.1390, -0.1532, -0.1074, -0.1900, +0.0262],  # noqa: E501
    [-0.1862, -0.2448, -0.1227, -0.1027, -0.1729, -0.0840, -0.1379, +1.0000, +0.0354, +0.0465, +0.0233, +0.0195, +0.0329, +0.0160, +0.0262, -0.1900],  # noqa: E501
    [-0.1900, -0.1494, -0.0370, -0.0430, -0.0614, -0.0336, -0.1018, +0.0354, +1.0000, +0.7865, +0.1948, +0.2265, +0.3232, +0.1768, +0.5360, -0.1862],  # noqa: E501
    [-0.1494, -0.1900, -0.0471, -0.0477, -0.0658, -0.0330, -0.0718, +0.0465, +0.7865, +1.0000, +0.2479, +0.2511, +0.3463, +0.1739, +0.3781, -0.2448],  # noqa: E501
    [-0.0370, -0.0471, -0.1900, -0.1687, -0.1698, -0.1258, -0.1302, +0.0233, +0.1948, +0.2479, +1.0000, +0.8878, +0.8937, +0.6623, +0.6851, -0.1227],  # noqa: E501
    [-0.0430, -0.0477, -0.1687, -0.1900, -0.1580, -0.1368, -0.1390, +0.0195, +0.2265, +0.2511, +0.8878, +1.0000, +0.8316, +0.7200, +0.7318, -0.1027],  # noqa: E501
    [-0.0614, -0.0658, -0.1698, -0.1580, -0.1900, -0.1292, -0.1532, +0.0329, +0.3232, +0.3463, +0.8937, +0.8316, +1.0000, +0.6798, +0.8064, -0.1729],  # noqa: E501
    [-0.0336, -0.0330, -0.1258, -0.1368, -0.1292, -0.1900, -0.1074, +0.0160, +0.1768, +0.1739, +0.6623, +0.7200, +0.6798, +1.0000, +0.5653, -0.0840],  # noqa: E501
    [-0.1018, -0.0718, -0.1302, -0.1390, -0.1532, -0.1074, -0.1900, +0.0262, +0.5360, +0.3781, +0.6851, +0.7318, +0.8064, +0.5653, +1.0000, -0.1379],  # noqa: E501
    [+0.0354, +0.0465, +0.0233, +0.0195, +0.0329, +0.0160, +0.0262, -0.1900, -0.1862, -0.2448, -0.1227, -0.1027, -0.1729, -0.0840, -0.1379, +1.0000],  # noqa: E501
], dtype=np.float64)
M8 = M16[:8, :8]


@dataclass
class LadderFit:
    """Result of fitting the φ^(p/q) ladder to a spectrum."""
    n_eig: int
    pq: list[tuple[int, int]]          # best (p, q) per eigenvalue (vs λ0)
    rel_errors: list[float]            # |λ_pred - λ| / λ per eigenvalue
    median_rel_error: float            # the scalar fit score (lower = tighter)


def phi_ladder_fit(eigs: np.ndarray, max_fib: int = 34) -> LadderFit:
    """Fit each eigenvalue as λ0·φ^(-p/q) with Fibonacci q; return per-eig error.

    The spectrum is sorted descending, normalised to λ0. For each λk we find the
    p/q (q ∈ Fibonacci ≤ max_fib) whose φ-power best matches log_φ(λ0/λk), then
    measure the relative error of the reconstructed eigenvalue.
    """
    fibs = [q for q in FIBS if q <= max_fib]
    e = np.sort(np.asarray(eigs, dtype=np.float64))[::-1]
    e = e[e > 1e-9]
    lam0 = e[0]
    pq: list[tuple[int, int]] = []
    rel: list[float] = []
    for k in range(len(e)):
        ratio = lam0 / e[k]
        log_phi = np.log(ratio) / np.log(PHI)
        best_err, best_pq = np.inf, (0, 1)
        for q in fibs:
            p = round(log_phi * q)
            if p < 0:
                continue
            err = abs(log_phi - p / q)
            if err < best_err:
                best_err, best_pq = err, (p, q)
        p, q = best_pq
        pred = lam0 * PHI ** (-p / q)
        pq.append((p, q))
        rel.append(abs(pred - e[k]) / e[k])
    return LadderFit(len(e), pq, rel, float(np.median(rel)))


def top_spectrum(mat: np.ndarray, k: int) -> np.ndarray:
    """Top-k eigenvalues (symmetric) or singular values (otherwise), descending."""
    mat = np.asarray(mat, dtype=np.float64)
    if mat.ndim == 1:
        vals = np.abs(mat)
    elif np.allclose(mat, mat.T, atol=1e-6):
        vals = np.abs(np.linalg.eigvalsh(mat))
    else:
        vals = np.linalg.svd(mat, compute_uv=False)
    vals = np.sort(vals)[::-1]
    return vals[:k]


def null_random_ratios(
    spectrum: np.ndarray, samples: int, rng: np.random.Generator
) -> np.ndarray:
    """THE FAIR NULL: matched dynamic range, RANDOM ratios.

    Isolates the only question that matters — are the candidate's eigenvalue
    RATIOS specifically close to phi^(p/q), or would ANY spectrum of the same
    spread fit the (very flexible) phi-ladder just as well? Draw k eigenvalues
    log-uniformly between the candidate's own min and max, so the dynamic range
    is matched and ONLY the ratio structure is randomised.

    A structural null (random cosine/Wishart matrices) is UNFAIR here: its
    spectrum has the wrong spread (near-1 eigenvalues for near-orthogonal rows),
    which changes the fit for the wrong reason. Match the range; randomise ratios.
    """
    e = np.sort(np.abs(np.asarray(spectrum, dtype=np.float64)))[::-1]
    e = e[e > 1e-9]
    k = len(e)
    lo, hi = np.log(e[-1]), np.log(e[0])
    out = np.empty(samples)
    for s in range(samples):
        out[s] = phi_ladder_fit(np.exp(rng.uniform(lo, hi, k))).median_rel_error
    return out


@dataclass
class ScreenResult:
    name: str
    k: int
    median_rel_error: float
    null_mean: float
    null_std: float
    z: float                 # (null_mean - cand)/null_std ; >0 ⇒ fits better than null
    p_random: float          # P(a random same-range spectrum fits AT LEAST as well)
    pq: list[tuple[int, int]]
    rel_errors: list[float]
    null_family: str
    verdict: str


def verdict_for(z: float) -> str:
    if z >= 3.0:
        return "φ-LADDER SIGNATURE (strong collapse candidate — run the fold)"
    if z >= 2.0:
        return "φ-ladder signature (weak — needs the executable fold)"
    if z <= -2.0:
        return "ANTI-signature (fits φ-ladder WORSE than random)"
    return "NULL (fit no better than chance — NOT a collapse signal)"


def screen(
    name: str, spectrum: np.ndarray, null: np.ndarray, null_family: str
) -> ScreenResult:
    fit = phi_ladder_fit(spectrum)
    nmean, nstd = float(np.mean(null)), float(np.std(null) + 1e-12)
    z = (nmean - fit.median_rel_error) / nstd
    p_random = float(np.mean(null <= fit.median_rel_error))
    return ScreenResult(
        name=name, k=fit.n_eig, median_rel_error=fit.median_rel_error,
        null_mean=nmean, null_std=nstd, z=z, p_random=p_random,
        pq=fit.pq, rel_errors=fit.rel_errors,
        null_family=null_family, verdict=verdict_for(z),
    )


def print_result(r: ScreenResult) -> None:
    print(f"\n  ── {r.name}  (k={r.k} eigenvalues, null={r.null_family}) ──")
    ladder = "  ".join(f"φ^-{p}/{q}" for p, q in r.pq[:8])
    print(f"     ladder: {ladder}")
    errs = "  ".join(f"{e * 100:.2f}%" for e in r.rel_errors[:8])
    print(f"     per-λ:  {errs}")
    print(f"     median fit error: {r.median_rel_error * 100:.3f}%"
          f"   null: {r.null_mean * 100:.3f}% ± {r.null_std * 100:.3f}%"
          f"   z = {r.z:+.2f}   P(random fits ≥ as well) = {r.p_random:.2f}")
    print(f"     → {r.verdict}")


def main() -> None:
    ap = argparse.ArgumentParser(description="phi-ladder collapse screen (stage 1)")
    ap.add_argument("--npz", default="lattice/universal_lattice.npz",
                    help="consensus lattice npz (for consensus singular values)")
    ap.add_argument("--null-samples", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/fractal-collapse-screen/screen.json")
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)

    print("=" * 72)
    print("  FRACTAL-COLLAPSE SCREEN — φ-ladder spectral detector (STAGE 1)")
    print("  λ measure: verdict gated on z vs matched null, NOT absolute fit.")
    print("=" * 72)

    results: list[ScreenResult] = []
    ns, nf = args.null_samples, "matched-range random ratios"

    def add(name: str, spectrum: np.ndarray) -> None:
        nul = null_random_ratios(spectrum, ns, rng)
        results.append(screen(name, spectrum, nul, nf))

    # Positive control: the combinator crystal (the famous φ^(p/q) <0.5% claim).
    add("crystal-M8 [+control]", top_spectrum(M8, 8))
    add("crystal-M16", top_spectrum(M16, 16))

    # Negative control: a single random spectrum (should land at NULL).
    add("random-spectrum-8 [-control]", np.sort(rng.uniform(0.05, 5.0, 8))[::-1])

    # The s246 target: cross-model consensus operator spectrum.
    if os.path.exists(args.npz):
        d = np.load(args.npz)
        sv_keys = sorted(k for k in d.files if k.endswith("singular_values"))
        for key in sv_keys:
            add(f"consensus[{key.replace('_singular_values', '')}]", d[key])
    else:
        print(f"\n  (npz not found at {args.npz} — skipping consensus targets)")

    for r in results:
        print_result(r)

    print("\n" + "=" * 72)
    print("  READING THE RESULT")
    print("=" * 72)
    print("""
  z ≥ 3  → strong φ-ladder signature: the spectrum is self-similar BEYOND
           what the flexible φ-basis fakes on random matrices. A collapse MAY
           be available — but this is STAGE 1. Confirm with the executable fold
           (substitute the operation, run it, check the invariant is preserved).
  z ≈ 0  → NULL. A good absolute fit here is the φ-basis flexibility, not signal.
  z ≤ -2 → anti-signature (less self-similar than chance).

  No verdict here is a collapse. The screen only says WHERE to spend the
  expensive fold test. λ measure: screen ⇒ candidate; fold ⇒ collapse.
""")

    out = args.out
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump({"seed": args.seed, "null_samples": args.null_samples,
                   "phi": PHI, "results": [asdict(r) for r in results]}, f, indent=2)
    print(f"  saved → {out}")


if __name__ == "__main__":
    main()
