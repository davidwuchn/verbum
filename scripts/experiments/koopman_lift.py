#!/usr/bin/env python3
"""P-DMD-KOOPMAN-LIFT - lift the trajectory before DMD (frozen s340, Michael GO).

Near-free re-analysis of the s338 P-DMD-TRANSPORT trajectories (H saved). No new
inference. s338 left two linked caveats (operator-geometry-la-toolkit.md sec 5a):
  (1) rel_resid 0.476 @ rank 40 -> ~half the transition is nonlinear;
  (2) NO persistent |lambda|~1 modes (top ~0.92, all contracting) -> the
      pre-registered "persistent-mode == sign-is-the-decision" had no train to
      land on.
This probe lifts h through nonlinear observables Psi(h) BEFORE DMD (Koopman /
EDMD after Williams, Kevrekidis & Rowley 2015; textbook, patent-clean per sec
0b FTO rule) and asks: does the residual drop, and do persistent modes appear
that the linear spectrum missed?

METRIC (build-time discovery, s340). We use the sec-5a reduced-DMD residual
(rel_resid = ||X'-TX||_F/||X'||_F, rank-truncated -> proven shuffle-sensitive)
but on the LIFTED, per-feature STANDARDISED snapshots, so no block dominates the
Frobenius norm and a genuinely Koopman-closed lift drives the residual toward 0.
The comparison is poly-vs-RANDOM-LIFT (matched dim) and poly-real-vs-SHUFFLE.

TWO TRAPS the freeze beats:
  * phi-ladder scar (lambda yardstick): ANY lift adds dims and can lower
    residual. A drop counts ONLY if it beats a matched-dim RANDOM-LIFT null and
    is corroborated by shuffled-layer.
  * register trap (lambda measure / lambda separate): residual-norm grows across
    depth; a lifted |lambda|~1 mode can be the DC/NORM-growth direction
    (degree-2 ||h||^2 makes it trivial) -> mundane, NOT the decision. A
    persistent mode must live OFF the square/energy block to count as decision.

FROZEN verdict tree (operator-geometry-la-toolkit.md sec 5c):
  G0 INSTRUMENT   planted worlds recovered + det-repeat (trivially 0.0, same H)
                  -> else VOID
  G1 RESIDUAL-DROP (make-or-break): rel_poly beats matched-dim random-lift null
                  by floor DELTA>=0.05, p<0.05, corroborated by shuffled-layer
                  (gap>0, p<0.05) -> else DIMENSION-ARTIFACT
  G2 PERSISTENCE  persist_frac_poly exceeds the random-lift null (95th pct)
                  -> else STILL-CONTRACTING
  G3 DECISION-LANDING persistent modes' energy NOT concentrated on the square/
                  norm block beyond a random-unit-vector null -> PERSISTENT-IS-
                  DECISION; else PERSISTENT-IS-NORM

A-priori masses: STILL-CONTRACTING 30 / DIMENSION-ARTIFACT 25 /
PERSISTENT-IS-NORM 20 / PERSISTENT-IS-DECISION 15 / VOID 10.

Lift: polynomial degree-2 on a P_LIFT=24 PCA frame -> 24 linear + 24 square +
276 cross = 324 observables (well-posed vs ~12000 pairs; deterministic; degree-2
Taylor of softmax.SiLU). NO constant observable (a bias feature is a trivial
|lambda|=1 mode by construction - excluded). Features centred + per-feature
standardised (as sec 5a centres) so the trivial DC does not manufacture
persistence and no block dominates the residual norm.

`--validate` drives 4 planted worlds (STILL-CONTRACTING / DIMENSION-ARTIFACT /
PERSISTENT-IS-DECISION / PERSISTENT-IS-NORM) - all Koopman-closed nonlinear
systems (driver/driven quadratic coupling) - through the REAL analyse() + gate
path (s331: planted plumbing must be probe plumbing). No model is loaded.

License: MIT.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from combinator_relationship_map import git_sha, log

from verbum.operator_dmd import economy_svd

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS (sec 5c, s340)
# ---------------------------------------------------------------------------
P_LIFT = 24                 # PCA frame the poly-2 lift is built on
LIFT_RANK = 240             # DMD truncation rank in the lifted space (gates);
#                             calibrated on planted worlds: the 324-dim lift needs
#                             high rank to capture the operator (rank 80 truncates
#                             the conserved modes; rank 240 recovers them, rel->0
#                             for Koopman-closed systems). Still shuffle-sensitive.
RANK_SWEEP = (80, 160, 240)  # descriptive only
N_NULL = 200                # matched-dim random-lift draws (G1 + G2 null)
N_PERM_SHUF = 100           # shuffled-layer-order permutations (G1 corroboration)
N_RAND_VEC = 4000           # random unit vectors for the G3 square-block null
ALPHA = 0.05
G1_DELTA_FLOOR = 0.05       # rel_resid must beat the random-lift null by this
PERSIST_ABS = 0.95          # |lambda| >= this counts as persistent (== sec 5a)
SEED = 0

VERDICTS = (
    "PERSISTENT-IS-DECISION", "PERSISTENT-IS-NORM", "STILL-CONTRACTING",
    "DIMENSION-ARTIFACT", "VOID",
)


def _json_native(o: Any):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"not JSON-native: {type(o)}")


# ---------------------------------------------------------------------------
# Lifts (each returns per-feature STANDARDISED observables)
# ---------------------------------------------------------------------------
def _pca_frame(H: np.ndarray, p: int) -> tuple[np.ndarray, np.ndarray]:
    """Top-p right singular vectors of the centred snapshot matrix.

    Returns (components (d, p), mean (d,)). Deterministic.
    """
    snaps = H.reshape(-1, H.shape[-1])
    mean = snaps.mean(axis=0)
    _, _, Vt = np.linalg.svd(snaps - mean, full_matrices=False)
    return Vt[:p].T, mean


def _standardise(F: np.ndarray) -> np.ndarray:
    """Per-feature z-score over all snapshots (mean 0, std 1)."""
    flat = F.reshape(-1, F.shape[-1])
    mu = flat.mean(axis=0)
    sd = flat.std(axis=0) + 1e-8
    return (F - mu) / sd


def poly2_lift(Z: np.ndarray) -> tuple[np.ndarray, dict[str, tuple[int, int]]]:
    """Degree-2 polynomial lift of a (n, lp1, P) PCA-projected trajectory.

    Features = [linear P | square P | cross P*(P-1)/2]. NO constant feature
    (would be a trivial |lambda|=1 mode). Output per-feature standardised.
    Returns (Psi, block_index).
    """
    _, _, p = Z.shape
    flat = Z.reshape(-1, p)
    std = flat.std(axis=0) + 1e-8
    Zs = Z / std
    lin = Zs
    sq = Zs * Zs
    iu = np.triu_indices(p, k=1)
    cross = Zs[..., iu[0]] * Zs[..., iu[1]]
    Psi = np.concatenate([lin, sq, cross], axis=-1)
    d = Psi.shape[-1]
    blocks = {"lin": (0, p), "sq": (p, 2 * p), "cross": (2 * p, d)}
    return _standardise(Psi), blocks


def random_lift(Z: np.ndarray, d_out: int, rng: np.random.Generator) -> np.ndarray:
    """Matched-dim random nonlinear feature map (random Fourier features).

    Psi_rand = cos(Zs @ W + b), W ~ N(0, 1/P), b ~ U[0, 2pi). A legitimate
    random nonlinear lift of the SAME output dimension d_out -> controls the
    "capacity alone lowers residual / manufactures persistence" confound.
    Output per-feature standardised.
    """
    _, _, p = Z.shape
    flat = Z.reshape(-1, p)
    std = flat.std(axis=0) + 1e-8
    Zs = Z / std
    W = rng.standard_normal((p, d_out)) / np.sqrt(p)
    b = rng.uniform(0.0, 2.0 * np.pi, size=d_out)
    return _standardise(np.cos(Zs @ W + b))


# ---------------------------------------------------------------------------
# Reduced-DMD on a lifted trajectory (sec-5a residual, shuffle-sensitive)
# ---------------------------------------------------------------------------
def _pairs(Psi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Centre features, return snapshot pairs (X, Xp), each (D, n*L)."""
    lp1 = Psi.shape[1]
    mean = Psi.reshape(-1, Psi.shape[-1]).mean(axis=0)
    C = Psi - mean
    x = C[:, : lp1 - 1, :].reshape(-1, C.shape[-1]).T
    xp = C[:, 1:, :].reshape(-1, C.shape[-1]).T
    return x, xp


def _dmd(
    Psi: np.ndarray, Z: np.ndarray, rank: int, want_modes: bool = True
) -> tuple[float, float, np.ndarray, np.ndarray]:
    """EDMD state-prediction: (rel_state, persist_frac, |eig|, modes Phi).

    A degree-2 dictionary is never Koopman-closed for nonlinear state dynamics
    (driven-coord squares are degree-4), so a full-lifted-vector residual is the
    wrong target. We measure the next-STATE prediction residual through a rank-r
    EDMD operator: predict Psi(l+1) = A_proj Psi(l), read the state back via a
    rank-r linear readout R (state ~ R Psi), residual vs the true next state.
    Rank truncation keeps it shuffle-sensitive; the spectrum (persistence) is the
    eig of the reduced operator A_tilde.
    """
    X, Xp = _pairs(Psi)               # (D, npairs)
    Sx, Sxp = _pairs(Z)               # (k, npairs) state pairs (target)
    U, s, Vt = economy_svd(X)
    r = int(min(rank, np.count_nonzero(s > s.max() * 1e-10))) if s.size else 0
    if r == 0:
        return 1.0, 0.0, np.zeros(0), np.zeros((Psi.shape[-1], 0), complex)
    Ur, sr, Vr = U[:, :r], s[:r], Vt[:r]
    A_tilde = (Ur.conj().T @ Xp @ Vr.conj().T) / sr[np.newaxis, :]  # (r, r)
    proj = Ur.conj().T @ X                          # (r, npairs) == sr*Vr
    next_feat = Ur @ (A_tilde @ proj)               # predicted Psi(l+1)
    # rank-r readout state <- features: R = Sx X^+ ; pred next state = R next_feat
    R = (Sx @ Vr.conj().T / sr[np.newaxis, :]) @ Ur.conj().T  # (k, D)
    pred_state = (R @ next_feat).real
    denom = float(np.linalg.norm(Sxp))
    rel_state = float(np.linalg.norm(Sxp - pred_state) / denom) if denom > 0 else 0.0
    w, V = np.linalg.eig(A_tilde)
    abs_eig = np.abs(w)
    persist = float(np.mean(abs_eig >= PERSIST_ABS)) if abs_eig.size else 0.0
    phi = Ur @ V if want_modes else np.zeros((Psi.shape[-1], 0), complex)
    return rel_state, persist, abs_eig, phi


def _shuffle_rel(
    Psi: np.ndarray, Z: np.ndarray, rank: int, n_perm: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """rel_state under n_perm shuffled-layer-order permutations of the lift."""
    lp1 = Psi.shape[1]
    out = np.empty(n_perm)
    for i in range(n_perm):
        pi = rng.permutation(lp1)
        out[i] = _dmd(Psi[:, pi, :], Z[:, pi, :], rank, want_modes=False)[0]
    return out


def _square_energy_frac(phi: np.ndarray, sq_slice: tuple[int, int]) -> np.ndarray:
    """Per-mode fraction of |phi|^2 energy on the square/norm block."""
    a, b = sq_slice
    e = np.abs(phi) ** 2
    tot = e.sum(axis=0)
    tot[tot == 0] = 1.0
    return e[a:b, :].sum(axis=0) / tot


# ---------------------------------------------------------------------------
# Shared analysis + gate path (real AND planted call this - s331)
# ---------------------------------------------------------------------------
def analyse(H: np.ndarray, rng: np.random.Generator) -> dict:
    """Full Koopman-lift DMD analysis + frozen gates on a trajectory tensor.

    H: (n, lp1, d) real last-token residual trajectories. Returns the gates
    dict incl. the per-class verdict (VOID is an instrument meta-verdict decided
    by the caller / --validate).
    """
    comps, mean = _pca_frame(H, P_LIFT)
    Z = (H - mean) @ comps  # (n, lp1, P_LIFT)
    Psi, blocks = poly2_lift(Z)
    d_out = Psi.shape[-1]

    # --- poly lift: primary statistics + rank sweep -------------------------
    rel_poly, persist_poly, abs_eig, phi = _dmd(Psi, Z, LIFT_RANK)
    sweep = {r: _dmd(Psi, Z, r, want_modes=False)[0] for r in RANK_SWEEP}
    top_abs = sorted(abs_eig.tolist(), reverse=True)[:5]

    # descriptive linear baseline (P_LIFT linear features only, same frame)
    rel_linear, persist_linear, _, _ = _dmd(
        _standardise(Z), Z, min(LIFT_RANK, P_LIFT))

    # --- matched-dim random-lift null (G1 residual + G2 persistence) --------
    rand_rel = np.empty(N_NULL)
    rand_persist = np.empty(N_NULL)
    for i in range(N_NULL):
        Pr = random_lift(Z, d_out, np.random.default_rng(1000 + i))
        rr, rp, _, _ = _dmd(Pr, Z, LIFT_RANK, want_modes=False)
        rand_rel[i] = rr
        rand_persist[i] = rp

    delta_rand = float(np.median(rand_rel) - rel_poly)
    p_rand = float(np.mean(rand_rel <= rel_poly))
    beats_random = bool(delta_rand >= G1_DELTA_FLOOR and p_rand < ALPHA)

    # --- shuffled-layer-order corroboration (G1) ----------------------------
    rel_shuf = _shuffle_rel(Psi, Z, LIFT_RANK, N_PERM_SHUF, rng)
    gap_shuf = float(np.median(rel_shuf) - rel_poly)
    p_shuf = float(np.mean(rel_shuf <= rel_poly))
    shuf_ok = bool(gap_shuf > 0.0 and p_shuf < ALPHA)

    g1_pass = beats_random and shuf_ok

    # --- G2 persistence vs random-lift null ---------------------------------
    persist_null95 = float(np.quantile(rand_persist, 0.95))
    g2_pass = bool(persist_poly > persist_null95 and persist_poly > 0.0)

    # --- G3 decision-landing: is EVERY persistent mode norm/square-dominated? -
    # A conserved LINEAR mode co-conserves its square (degenerate |lambda|=1
    # subspace), so the median mixes; the register question is whether a NON-norm
    # persistent mode EXISTS -> gate on the MIN square-fraction (build-time, s340).
    persist_mask = abs_eig >= PERSIST_ABS
    sqfrac_persist = _square_energy_frac(phi[:, persist_mask], blocks["sq"])
    min_sqfrac = float(np.min(sqfrac_persist)) if sqfrac_persist.size else 0.0
    med_sqfrac = float(np.median(sqfrac_persist)) if sqfrac_persist.size else 0.0
    rv = np.random.default_rng(SEED + 7)
    R = rv.standard_normal((d_out, N_RAND_VEC)) + 1j * rv.standard_normal(
        (d_out, N_RAND_VEC))
    sqfrac_null95 = float(np.quantile(_square_energy_frac(R, blocks["sq"]), 0.95))
    g3_norm = bool(min_sqfrac > sqfrac_null95)

    # --- verdict (per-class; VOID decided by caller) ------------------------
    if not g1_pass:
        verdict = "DIMENSION-ARTIFACT"
    elif not g2_pass:
        verdict = "STILL-CONTRACTING"
    elif g3_norm:
        verdict = "PERSISTENT-IS-NORM"
    else:
        verdict = "PERSISTENT-IS-DECISION"

    return {
        "n_prompts": int(H.shape[0]),
        "lp1": int(H.shape[1]),
        "d_out": int(d_out),
        "rel_resid_poly": float(rel_poly),
        "rel_resid_linear": float(rel_linear),
        "rel_resid_sweep": {int(k): float(v) for k, v in sweep.items()},
        "persist_frac_poly": float(persist_poly),
        "persist_frac_linear": float(persist_linear),
        "top_abs_eig": top_abs,
        "g1": {
            "delta_vs_random": delta_rand,
            "p_random": p_rand,
            "beats_random": beats_random,
            "rand_rel_median": float(np.median(rand_rel)),
            "gap_shuffle": gap_shuf,
            "p_shuffle": p_shuf,
            "shuffle_ok": shuf_ok,
            "pass": g1_pass,
        },
        "g2": {
            "persist_poly": float(persist_poly),
            "persist_null95": persist_null95,
            "pass": g2_pass,
        },
        "g3": {
            "min_square_frac": min_sqfrac,
            "median_square_frac": med_sqfrac,
            "square_null95": sqfrac_null95,
            "n_persistent": int(persist_mask.sum()),
            "norm_dominated": g3_norm,
        },
        "verdict": verdict,
    }


# ---------------------------------------------------------------------------
# Planted worlds - Koopman-closed nonlinear systems (run the full path, s331)
# ---------------------------------------------------------------------------
def _closed_world(
    lam: np.ndarray, quad_persist: str, rng: np.random.Generator,
    n: int, lp1: int, d: int, drivers: int = 3, clip: float = 6.0,
) -> np.ndarray:
    """Driver/driven quadratic system, Koopman-closed under degree-2.

    Coords 0..drivers-1 are LINEAR drivers (h'_j = lam_j h_j). Coords
    drivers..d-1 are driven: h'_i = lam_i h_i + sum_{j<=k in drivers} c h_j h_k.
    Driver quadratics evolve linearly (lam_j lam_k) -> [h, driver-quadratics]
    is closed under the poly-2 dictionary, so poly-DMD residual -> ~0 while
    linear DMD misses the coupling. `quad_persist` selects a persistence plant:
      'none'     - all |lam|<0.95 (STILL-CONTRACTING)
      'rotation' - a 2D norm-preserving rotation on coords d-2,d-1 (persistent
                   COMPLEX LINEAR modes; PERSISTENT-IS-DECISION)
      'norm'     - driver 0 conserves |h_0| with random sign (persistent SQUARE;
                   PERSISTENT-IS-NORM)
    """
    C = 0.35 * rng.standard_normal((d, drivers, drivers))
    C[:drivers] = 0.0  # drivers stay purely linear (closure)
    C[-1] = 0.0        # coord d-1 reserved as a non-source driven coord
    C[-2] = 0.0        # coord d-2 reserved (rotation partner)
    theta = 0.6
    ct, st = np.cos(theta), np.sin(theta)
    h = np.empty((n, lp1, d))
    h[:, 0] = 0.5 * rng.standard_normal((n, d))
    mag0 = np.abs(rng.standard_normal(n)) + 0.5
    if quad_persist == "norm":
        h[:, 0, 0] = mag0
    for ell in range(lp1 - 1):
        cur = h[:, ell]
        nxt = cur * lam[np.newaxis, :]
        # quadratic driver coupling into driven coords
        drv = cur[:, :drivers]
        quad = np.einsum("nj,nk->njk", drv, drv)  # (n, drivers, drivers)
        nxt += np.einsum("ijk,njk->ni", C, quad)
        nxt += 0.01 * rng.standard_normal((n, d))
        if quad_persist == "rotation":
            a, b = cur[:, -2], cur[:, -1]
            nxt[:, -2] = ct * a - st * b
            nxt[:, -1] = st * a + ct * b
        elif quad_persist == "norm":
            nxt[:, 0] = rng.choice([-1.0, 1.0], size=n) * mag0
        h[:, ell + 1] = np.clip(nxt, -clip, clip)
    return h


def planted_worlds(lp1: int = 41, n: int = 150, d: int = 20) -> dict:
    """Synthetic Koopman-closed trajectories for --validate."""
    worlds: dict[str, tuple[np.ndarray, str]] = {}

    # (1) STILL-CONTRACTING: closed, all contracting -> poly linearises, nothing
    #     persists.
    r = np.random.default_rng(101)
    lam = r.uniform(0.55, 0.88, size=d) * r.choice([-1.0, 1.0], size=d)
    worlds["STILL-CONTRACTING"] = (
        _closed_world(lam, "none", r, n, lp1, d), "STILL-CONTRACTING")

    # (2) DIMENSION-ARTIFACT: iid random snapshots - NO temporal operator. Poly
    #     and RFF both fail equally (no structure to capture), and shuffle ~ real
    #     -> G1 fails on BOTH sub-conditions -> DIMENSION-ARTIFACT.
    r = np.random.default_rng(202)
    worlds["DIMENSION-ARTIFACT"] = (
        r.standard_normal((n, lp1, d)), "DIMENSION-ARTIFACT")

    # (3) PERSISTENT-IS-DECISION: closed contracting bulk + a 2D ROTATION block
    #     (|lambda|=1, theta=0.6) on coords d-2,d-1 -> clean COMPLEX persistent
    #     modes on the LINEAR block, distinct from the real norm-invariant, so
    #     min-square-fraction ~ 0 -> a non-norm persistent mode exists.
    r = np.random.default_rng(303)
    lam = r.uniform(0.55, 0.85, size=d) * r.choice([-1.0, 1.0], size=d)
    H = _closed_world(lam, "rotation", r, n, lp1, d)
    worlds["PERSISTENT-IS-DECISION"] = (H, "PERSISTENT-IS-DECISION")

    # (4) PERSISTENT-IS-NORM: driver 0 conserves |h_0| with a random sign each
    #     layer -> h_0^2 (square feature) is persistent while the LINEAR h_0 mode
    #     contracts -> persistent mode lives on the SQUARE/norm block.
    r = np.random.default_rng(404)
    lam = r.uniform(0.55, 0.85, size=d) * r.choice([-1.0, 1.0], size=d)
    worlds["PERSISTENT-IS-NORM"] = (
        _closed_world(lam, "norm", r, n, lp1, d), "PERSISTENT-IS-NORM")
    return worlds


def run_validate() -> int:
    log("[koop] --validate: driving planted worlds through the real gate path")
    worlds = planted_worlds()
    ok = True
    for name, (H, expected) in worlds.items():
        res = analyse(H, np.random.default_rng(SEED))
        got = res["verdict"]
        passed = got == expected
        ok = ok and passed
        g2n = res["g2"]["persist_null95"]
        g3n = res["g3"]["square_null95"]
        log(
            f"[koop]   {name:22s} -> {got:22s} (want {expected:22s}) "
            f"rel={res['rel_resid_poly']:.3f}(lin {res['rel_resid_linear']:.2f}) "
            f"dR={res['g1']['delta_vs_random']:+.3f} "
            f"shuf={res['g1']['gap_shuffle']:+.3f} "
            f"persist={res['persist_frac_poly']:.3f}(>{g2n:.3f}) "
            f"min_sqf={res['g3']['min_square_frac']:.2f}(>{g3n:.2f}) "
            f"{'OK' if passed else 'FAIL'}"
        )
    log(f"[koop] validate {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# Main (re-analysis of saved H; no model load)
# ---------------------------------------------------------------------------
def _pole_landing(H: np.ndarray, labels: list[str] | None) -> dict | None:
    """Advisory (descriptive, NOT a gate): where the persistent modes' linear
    block points among combinator centroids. None if labels unavailable."""
    if not labels:
        return None
    comps, mean = _pca_frame(H, P_LIFT)
    Z = (H - mean) @ comps
    Psi, blocks = poly2_lift(Z)
    _, _, abs_eig, phi = _dmd(Psi, Z, LIFT_RANK)
    persist = phi[:, abs_eig >= PERSIST_ABS]
    if persist.shape[1] == 0:
        return None
    a, b = blocks["lin"]
    lin_modes = np.abs(persist[a:b, :])
    last = Z[:, -1, :]
    cents: dict[str, np.ndarray] = {}
    for comb in sorted({c for c in labels if c}):
        idx = [i for i, c in enumerate(labels) if c == comb]
        c = last[idx].mean(axis=0)
        nrm = np.linalg.norm(c)
        cents[comb] = c / nrm if nrm > 0 else c
    out = {}
    for k in range(lin_modes.shape[1]):
        m = lin_modes[:, k]
        mn = np.linalg.norm(m)
        m = m / mn if mn > 0 else m
        out[f"mode_{k}"] = {c: float(abs(cents[c] @ m)) for c in cents}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--h-path",
        default="results/p_dmd_transport_s338/run_14b/trajectories.npz",
    )
    ap.add_argument(
        "--labels-path",
        default="results/p_dmd_transport_s338/run_14b/results.jsonl",
    )
    ap.add_argument("--out", default="results/p_dmd_koopman_lift_s340/run_14b")
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return run_validate()

    hp = Path(args.h_path)
    log(f"[koop] loading H from {hp}")
    H = np.load(hp)["H"].astype(np.float64)
    log(f"[koop] H shape {H.shape}")

    labels = None
    lp = Path(args.labels_path)
    if lp.exists():
        labels = [json.loads(ln)["combinator"]
                  for ln in lp.read_text().splitlines() if ln.strip()]
        if len(labels) != H.shape[0]:
            log(f"[koop] label count {len(labels)} != n {H.shape[0]}; dropping")
            labels = None

    res = analyse(H, np.random.default_rng(SEED))
    advisory = _pole_landing(H, labels)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    meta = {
        "probe": "P-DMD-KOOPMAN-LIFT",
        "frozen": "s340 pre-data freeze (Michael GO): "
                  "operator-geometry-la-toolkit.md sec 5c",
        "pre_data_instantiations": {
            "P_LIFT": P_LIFT, "LIFT_RANK": LIFT_RANK,
            "RANK_SWEEP": list(RANK_SWEEP), "N_NULL": N_NULL,
            "N_PERM_SHUF": N_PERM_SHUF, "N_RAND_VEC": N_RAND_VEC,
            "ALPHA": ALPHA, "G1_DELTA_FLOOR": G1_DELTA_FLOOR,
            "PERSIST_ABS": PERSIST_ABS, "SEED": SEED,
            "apriori_masses": {
                "STILL-CONTRACTING": 30, "DIMENSION-ARTIFACT": 25,
                "PERSISTENT-IS-NORM": 20, "PERSISTENT-IS-DECISION": 15,
                "VOID": 10},
        },
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "source_H": str(hp),
        "reanalysis_of": "P-DMD-TRANSPORT s338 (no new inference)",
        "det_value_dev": 0.0,   # same H bytes -> deterministic by construction
        "det_ok": True,
        "git_sha": git_sha(),
        "global_verdict": res["verdict"],
        "gates": res,
        "advisory_pole_landing": advisory,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=_json_native))

    log(f"[koop] === VERDICT: {res['verdict']} ===")
    g = res
    g1, g2, g3 = g["g1"], g["g2"], g["g3"]
    log(f"[koop] rel_poly={g['rel_resid_poly']:.3f} "
        f"(linear {g['rel_resid_linear']:.3f}) "
        f"| G1 dR={g1['delta_vs_random']:+.3f} p={g1['p_random']:.3f} "
        f"shuf_gap={g1['gap_shuffle']:+.3f} pass={g1['pass']}")
    log(f"[koop] G2 persist={g['persist_frac_poly']:.3f} "
        f"(>{g2['persist_null95']:.3f}) pass={g2['pass']} "
        f"| G3 sqfrac={g3['median_square_frac']:.3f} "
        f"(>{g3['square_null95']:.3f}) norm={g3['norm_dominated']} "
        f"n_persist={g3['n_persistent']}")
    log(f"[koop] wrote {out}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
