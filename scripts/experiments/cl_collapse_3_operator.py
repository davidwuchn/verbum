#!/usr/bin/env python3
# register: operator/orbit (eigen-decay + frequency structure of the shared reducer)
"""P-CL-COLLAPSE-3-operator - extensional equality in the ORBIT, not the point.

FROZEN spec (s339, Michael GO) + s339 BUILD-TIME AMENDMENT (Michael-approved,
pre-data): operator-geometry-la-toolkit.md sec 5b. Downstream of the s338
STATIONARY-REDUCER verdict (sec 5a): the within-pass residual trajectory is one
stationary CONTRACTING operator unrolled across depth.

THE REFRAME (s338): meaning-as-equality is a property of the ORBIT/attractor, not
the point. The static pairwise Gram G=X^T X is a 2nd-order INTENSIONAL shadow -
it found NO extensional routing (s321 clean-null, s323 prose-null).

THE BUILD-TIME AMENDMENT (s339, validated on planted worlds). The original frozen
make-or-break ("co-extensional converge in the slow-mode ATTRACTOR cosine, slow
beats raw") is UNREACHABLE for a normal contracting operator: whatever survives to
the attractor IS the top-|lambda| band, so orthogonal slow-projection(late) ==
raw(late) - they cannot dissociate (operator==point at the contracting attractor;
the dissociation exists only via NON-NORMALITY). ROBUST REPLACEMENT: read the
DECAY RATE of the pairwise DIFFERENCE h_A - h_B (differencing removes the common
high-variance part). Decompose the difference in the operator's eigenmodes, weight
by |lambda|. Co-extensional pairs differ only by SPELLING -> their difference rides
FASTER-decaying modes (|lambda| small -> contracts -> converges); co-intensional
differences carry FUNCTION -> SLOWER-decaying modes (|lambda| near top -> persists).
This needs the operator SPECTRUM (impossible for the point-Gram) and is robust
(orthogonal-ish projection + eigenvalue weighting, no pinv, no capture fragility).

TWO ADDED ADVISORIES (Michael, s339):
  (2) NON-NORMALITY - departure-from-normality of T (Henrici) + eigvec conditioning;
      if non-normal, a bounded ridge-modal convergence read. Contextualizes whether
      operator can dissociate from point at all.
  FREQUENCY SWEEP - lambda = |lambda| e^{i theta}; theta = rotation-rate per layer =
      the depth-clock (transitions-per-beta-step; s322 sign-oscillation; s301
      time-Bragg). Per-band within/across DIFFERENCE energy over theta in [0,pi]
      (DC=0 stable ... pi=sign-flip-per-layer), shuffled-NF null. Advisory scan -
      earns its own frozen make-or-break next round if structure appears (yardstick).

FROZEN verdict tree (amended):
  G0 INSTRUMENT (void)   operator-exists (sec 5a shuffled-layer null gap>0 p<.05,
                         reused verbatim) + det-repeat 0.0 + >=2 NF families with
                         >=2 clean spellings -> else VOID
  G2 DECAY-CONVERGENCE   (make-or-break) D_decay = mean(across-NF diff mean|lambda|)
                         - mean(within-NF diff mean|lambda|) > 0, beats shuffled-NF
                         null p<0.05 (co-ext differences decay faster = converge)
                         -> CONVERGENCE ; else NO-ORBITAL-CONVERGENCE
  Advisory: raw-point cosine convergence (also-pointwise vs operator-only
  characterization) ; non-normality + ridge-modal read ; frequency sweep ;
  convergence-slope ; per-family.

Verdicts + a-priori (favored = NO-CONVERGE per the three-register law s317/s335/s336;
amended: the old ORBITAL 20 + RAW-ALSO 15 merge into CONVERGENCE 35 - they differ
only by non-normality, which makes them mathematically identical at the attractor):
  NO-ORBITAL-CONVERGENCE 50 (modal) / CONVERGENCE 35 (reopens compositionality S5
  cell in the operator register) / VOID 15.

Register: last-token d_model residual trajectory (sec 5a). Corpus: kernel-certified
CLEAN collapse spellings (NF-symbol ABSENT - the genuine dissociation, s321) for
families I/W/B. Method: reuse sec 5a capture + operator_dmd (PCA P=128, global
pooled DMD rank 40).

`--validate` drives 3 verdict-planted worlds (CONVERGE / NO-CONVERGE / VOID) through
the REAL analyse+gate path (s331) + a non-normal sanity plant (departure metric).

License: MIT.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
sys.path.insert(0, str(_SCRIPT_DIR.parents[1] / "src"))

import dmd_transport as dt  # noqa: E402  (trusted sec 5a instrument, reused verbatim)
from combinator_relationship_map import git_sha, log  # noqa: E402

from verbum.lambda_ast import normal_form, parse, pretty  # noqa: E402
from verbum.operator_dmd import pca_basis, reduced_dmd  # noqa: E402

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS (s339, amended)
# ---------------------------------------------------------------------------
P_PCA = 128            # common PCA frame dim (sec 5a)
PRIMARY_RANK = 40      # DMD truncation rank (sec 5a)
LATE_LAYERS = 3        # attractor = mean of the last LATE_LAYERS hidden states
N_PER = 40             # atom instantiations per clean spelling
N_NULL = 5000          # shuffled-NF-label permutations
ALPHA = 0.05
FLOOR_D_DECAY = 0.01   # min meaningful decay-rate gap (|lambda| units); excludes
                       # negligible chance arrangements (yardstick: p<.05 AND
                       # effect-size). Planted CONVERGE ~0.030, planted null ~0.0004.
FREQ_BANDS = 6         # theta bins over [0, pi] (advisory frequency sweep)
NONNORMAL_DEP_MIN = 0.10   # Henrici departure flag (advisory)
MODAL_COND_MAX = 1.0e6     # eigvec conditioning ceiling for the ridge-modal read
MODAL_RIDGE = 1.0e-3       # ridge for the bounded modal read
DET_TOL = 0.0          # deterministic-repeat max abs hidden diff (bf16 greedy)
DET_CHECK_N = 8
SEED = 0

VERDICTS = ("CONVERGENCE", "NO-ORBITAL-CONVERGENCE", "VOID")

# ---------------------------------------------------------------------------
# CLEAN co-extensional families (NF-symbol ABSENT, kernel-certified at build)
# I:8 (28 within-pairs, well-powered) / W:2 (1 pair) / B:1 (0 pairs, enriches the
# across-NF distribution + the shuffled-NF null). The thin B/W families are a
# mathematical bound on clean CL spellings (verified s339).
# ---------------------------------------------------------------------------
FAMILIES: dict[str, dict] = {
    "I": {
        "arity": 1,
        "anchor": "I {0}",
        "spellings": [
            "S K K {0}", "S K S {0}", "W K {0}", "C K K {0}",
            "S K (K K) {0}", "C K S {0}", "C K (K K) {0}", "S K (S K) {0}",
        ],
    },
    "W": {
        "arity": 2,
        "anchor": "W {0} {1}",
        "spellings": ["S S (K I) {0} {1}", "C S I {0} {1}"],
    },
    "B": {
        "arity": 3,
        "anchor": "B {0} {1} {2}",
        "spellings": ["S (K S) K {0} {1} {2}"],
    },
}
ATOMS = list("abcdefghmnpqrtuvxz")
_COMB_SET = set("SKIBCWDYM")


def _reduce(text: str) -> str:
    return pretty(normal_form(parse(text)))


def _atom_tuples(n_slots: int, n: int, seed: int) -> list[tuple[str, ...]]:
    rng = np.random.default_rng(seed)
    seen: set[tuple[str, ...]] = set()
    out: list[tuple[str, ...]] = []
    tries = 0
    while len(out) < n and tries < n * 100:
        tries += 1
        pick = tuple(rng.choice(ATOMS, size=n_slots, replace=False))
        if pick not in seen:
            seen.add(pick)
            out.append(pick)
    return out


def build_corpus(n_per: int, seed: int) -> list[dict]:
    """Kernel-certified clean spellings. Each: reduce(spelling) == reduce(anchor),
    NF-symbol absent from the spelling. group = spelling id; nf = family."""
    probes: list[dict] = []
    sd = seed
    for nf, fam in FAMILIES.items():
        ar = fam["arity"]
        anchor = fam["anchor"]
        for si, tmpl in enumerate(fam["spellings"]):
            n_slots = tmpl.count("{")
            assert n_slots == ar, f"{tmpl}: {n_slots} slots != arity {ar}"
            toks = tmpl.replace("(", " ").replace(")", " ").split()
            combs = {t for t in toks if t in _COMB_SET}
            assert nf not in combs, f"NF-symbol {nf} present in clean spelling {tmpl}"
            group = f"{nf}:{si}"
            for atoms in _atom_tuples(ar, n_per, sd):
                sd += 1
                text = tmpl.format(*atoms)
                got = _reduce(text)
                want = _reduce(anchor.format(*atoms))
                assert got == want, f"NOT extensional: {text}->{got} != {nf}->{want}"
                probes.append({"id": f"{group}:{'-'.join(atoms)}", "nf": nf,
                               "group": group, "text": text, "arity": ar})
    return probes


# ---------------------------------------------------------------------------
# DMD modes: real oblique frame + per-mode |lambda|, theta, non-normality metrics
# ---------------------------------------------------------------------------
def _dmd_modes(dmd: dict) -> dict:
    """From the reduced DMD dict, build the real mode frame Bn (P, m) with per-
    column |lambda| and theta=|angle|, plus non-normality diagnostics.

    Modes Phi = Ur @ eigvecs(A_tilde) live in P-space. Complex conjugate pairs ->
    two real columns [Re, Im] sharing (|lambda|, theta). Columns are unit-normed
    (an OBLIQUE frame - exact orthogonality holds only for a normal operator; the
    make-or-break is a within-vs-across relative under a shuffled-NF null, so any
    shared obliqueness bias cancels)."""
    A = dmd["A_tilde"]
    Ur = dmd["Ur"]
    if A.shape[0] == 0:
        z = np.zeros((Ur.shape[0], 0))
        return {"Bn": z, "lam": np.zeros(0), "theta": np.zeros(0),
                "departure": 0.0, "eigvec_cond": np.inf, "V": np.zeros((0, 0)),
                "Phi": z.astype(complex), "eigvals": np.zeros(0, complex)}
    w, V = np.linalg.eig(A)
    Phi = Ur @ V  # (P, r) complex
    cols, lam, theta = [], [], []
    for k in range(len(w)):
        cols.append(Phi[:, k].real)
        lam.append(abs(w[k]))
        theta.append(abs(np.angle(w[k])))
        if np.linalg.norm(Phi[:, k].imag) > 1e-9:
            cols.append(Phi[:, k].imag)
            lam.append(abs(w[k]))
            theta.append(abs(np.angle(w[k])))
    B = np.stack(cols, axis=1)
    Bn = B / np.where(np.linalg.norm(B, axis=0) == 0, 1.0, np.linalg.norm(B, axis=0))
    # Henrici departure from normality of the reduced operator: normalised
    dep = float(np.sqrt(max(0.0, np.linalg.norm(A, "fro") ** 2
                            - float(np.sum(np.abs(w) ** 2)))))
    fro = float(np.linalg.norm(A, "fro"))
    dep_n = dep / fro if fro > 0 else 0.0
    try:
        cond = float(np.linalg.cond(V))
    except np.linalg.LinAlgError:
        cond = np.inf
    return {"Bn": Bn, "lam": np.array(lam), "theta": np.array(theta),
            "departure": dep_n, "eigvec_cond": cond, "V": V, "Phi": Phi,
            "eigvals": w}


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------
def _group_centroids(A: np.ndarray, groups: np.ndarray, order: list[str]) -> np.ndarray:
    return np.stack([A[groups == g].mean(axis=0) for g in order])


def _diff_decay_matrix(C: np.ndarray, Bn: np.ndarray, lam: np.ndarray) -> np.ndarray:
    """Per-pair energy-weighted mean |lambda| of the difference C_i - C_j (the
    effective decay rate of the direction separating the two groups). LOW = the
    difference rides fast-decaying modes -> the pair converges."""
    n = C.shape[0]
    M = np.full((n, n), np.nan)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            dd = C[i] - C[j]
            e = (Bn.T @ dd) ** 2
            se = float(e.sum())
            M[i, j] = float((e * lam).sum() / se) if se > 1e-12 else np.nan
    return M


def _cosdist_matrix(C: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(C, axis=1)
    norm = np.where(norm == 0.0, 1.0, norm)
    U = C / norm[:, None]
    return 1.0 - np.clip(U @ U.T, -1.0, 1.0)


def _within_across(M: np.ndarray, labels: np.ndarray) -> tuple[float, float]:
    n = M.shape[0]
    iu, ju = np.triu_indices(n, k=1)
    same = labels[iu] == labels[ju]
    d = M[iu, ju]
    fin = np.isfinite(d)
    within = float(d[fin & same].mean()) if np.any(fin & same) else float("nan")
    across = float(d[fin & ~same].mean()) if np.any(fin & ~same) else float("nan")
    return within, across


def _null(M: np.ndarray, labels: np.ndarray, n_null: int, rng: np.random.Generator,
          stat, floor: float = 0.0) -> dict:
    """Shuffled-NF-label null. `stat(within, across) -> observed` (>0 favours the
    convergence hypothesis). Preserves class sizes. pass requires the observed
    effect to clear `floor` AND beat the null (p<ALPHA) - yardstick effect-size."""
    within, across = _within_across(M, labels)
    obs = stat(within, across)
    null = np.empty(n_null)
    lab = labels.copy()
    for i in range(n_null):
        rng.shuffle(lab)
        w, a = _within_across(M, lab)
        null[i] = stat(w, a)
    p = float((np.sum(null >= obs) + 1) / (n_null + 1))
    return {"within": within, "across": across, "obs": float(obs),
            "null_mean": float(np.mean(null)), "null_std": float(np.std(null)),
            "p_value": p, "floor": floor,
            "pass": bool(obs > floor and p < ALPHA)}


def _freq_sweep(C: np.ndarray, Bn: np.ndarray, theta: np.ndarray,
                groups: np.ndarray, grp_nf: np.ndarray, order: list[str],
                rng: np.random.Generator) -> dict:
    """Advisory: per-frequency-band within/across DIFFERENCE energy fraction, with
    a shuffled-NF null. theta in [0, pi]: DC(0)=stable ... pi=sign-flip-per-layer
    (s322 oscillation). D_band = within - across energy-fraction (co-ext difference
    concentrates in that band relative to co-int)."""
    edges = np.linspace(0.0, np.pi, FREQ_BANDS + 1)
    bands = []
    n = len(order)
    # per-pair band-energy fractions
    iu, ju = np.triu_indices(n, k=1)
    same = grp_nf[iu] == grp_nf[ju]
    for b in range(FREQ_BANDS):
        mask = (theta >= edges[b]) & (theta < edges[b + 1] if b < FREQ_BANDS - 1
                                      else theta <= edges[b + 1])
        frac = np.full((n, n), np.nan)
        for i in range(n):
            for j in range(i + 1, n):
                dd = C[i] - C[j]
                e = (Bn.T @ dd) ** 2
                se = float(e.sum())
                f = float(e[mask].sum() / se) if se > 1e-12 else np.nan
                frac[i, j] = frac[j, i] = f
        w, a = _within_across(frac, grp_nf)
        # null on within-across
        d = frac[iu, ju]
        obs = w - a
        null = np.empty(2000)
        lab = grp_nf.copy()
        for k in range(2000):
            rng.shuffle(lab)
            sm = lab[iu] == lab[ju]
            fin = np.isfinite(d)
            ww = float(d[fin & sm].mean()) if np.any(fin & sm) else np.nan
            aa = float(d[fin & ~sm].mean()) if np.any(fin & ~sm) else np.nan
            null[k] = ww - aa
        p = float((np.sum(null >= obs) + 1) / 2001)
        bands.append({"band": [float(edges[b]), float(edges[b + 1])],
                      "n_modes": int(mask.sum()), "within_frac": w,
                      "across_frac": a, "D": float(obs), "p_value": p})
    del same
    return {"edges": edges.tolist(), "bands": bands}


def _modal_convergence(dmd_m: dict, Z: np.ndarray, groups: np.ndarray,
                       grp_nf: np.ndarray, order: list[str],
                       rng: np.random.Generator) -> dict:
    """Advisory non-normality read: if the operator is non-normal (departure > thr)
    and eigenvectors are not too ill-conditioned, read convergence in the ridge-
    regularised MODAL coordinates (Phi^+ z) - the read the point-Gram cannot do and
    the only place operator-vs-point can dissociate. Bounded (ridge); caveated."""
    dep = dmd_m["departure"]
    cond = dmd_m["eigvec_cond"]
    Phi = dmd_m["Phi"]
    lam = np.abs(dmd_m["eigvals"])
    out = {"departure": dep, "eigvec_cond": cond,
           "non_normal": bool(dep > NONNORMAL_DEP_MIN)}
    if Phi.shape[1] == 0 or cond > MODAL_COND_MAX or not out["non_normal"]:
        out.update({"skipped": True, "reason":
                    "normal-or-ill-conditioned (operator==point regime)"})
        return out
    # ridge pseudo-inverse modal amplitudes of the late-band centroids
    zbar = Z[:, -LATE_LAYERS:, :].mean(axis=1)
    zbar = zbar - zbar.mean(axis=0, keepdims=True)
    G = Phi.conj().T @ Phi + MODAL_RIDGE * np.eye(Phi.shape[1])
    b = (np.linalg.solve(G, Phi.conj().T @ zbar.T)).T  # (n, r) complex modal amp
    # slow-modal cosine convergence (top tertile by |lambda|)
    order_l = np.argsort(lam)[::-1]
    ns = max(1, round(len(lam) / 3))
    slow = order_l[:ns]
    feat = np.concatenate([b[:, slow].real, b[:, slow].imag], axis=1)
    C = _group_centroids(feat, groups, order)
    res = _null(_cosdist_matrix(C), grp_nf, 2000, rng,
                lambda w, a: a - w)
    out.update({"skipped": False, "modal_slow": res})
    return out


def _convergence_slope(Z: np.ndarray, Bn: np.ndarray, lam: np.ndarray,
                       groups: np.ndarray, grp_nf: np.ndarray,
                       order: list[str]) -> dict:
    """Advisory: within-NF difference decay-rate by depth; late-half slope."""
    lp1 = Z.shape[1]
    per_layer = []
    for ell in range(lp1):
        z = Z[:, ell, :] - Z[:, ell, :].mean(axis=0, keepdims=True)
        C = _group_centroids(z, groups, order)
        M = _diff_decay_matrix(C, Bn, lam)
        w, _ = _within_across(M, grp_nf)
        per_layer.append(w)
    y = np.array(per_layer)
    xs = np.arange(lp1)
    half = lp1 // 2
    sl = float(np.polyfit(xs[half:], y[half:], 1)[0]) if lp1 - half >= 2 else 0.0
    return {"within_decayrate_by_depth": y.tolist(), "late_half_slope": sl}


# ---------------------------------------------------------------------------
# Shared analysis + gate path (real AND planted call this - s331)
# ---------------------------------------------------------------------------
def analyse(H: np.ndarray, nf: np.ndarray, groups: np.ndarray,
            rng: np.random.Generator, det_ok: bool = True) -> dict:
    n, lp1, d = H.shape
    L = lp1 - 1

    # --- G0a operator-exists: reuse the trusted sec 5a instrument VERBATIM ----
    dt_gates = dt.analyse(H, np.random.default_rng(SEED))
    op_exists = bool(dt_gates["g2"]["pass"])

    # --- G0b family structure -------------------------------------------------
    fam_groups: dict[str, set] = {}
    for f, g in zip(nf.tolist(), groups.tolist(), strict=False):
        fam_groups.setdefault(f, set()).add(g)
    fams_ge2 = [f for f, gs in fam_groups.items() if len(gs) >= 2]
    family_ok = len(fams_ge2) >= 2
    g0_pass = op_exists and family_ok and det_ok

    # --- PCA + global DMD (our modes) ----------------------------------------
    snaps = H.reshape(n * lp1, -1)
    comps, mean, var_explained = pca_basis(snaps, P_PCA, seed=SEED)
    Z = (H - mean) @ comps
    P = Z.shape[2]
    X = Z[:, :L, :].reshape(n * L, P).T
    Xp = Z[:, 1:, :].reshape(n * L, P).T
    dmd = reduced_dmd(X, Xp, PRIMARY_RANK)
    dmd_m = _dmd_modes(dmd)
    Bn, lam, theta = dmd_m["Bn"], dmd_m["lam"], dmd_m["theta"]

    order = sorted(set(groups.tolist()))
    grp_nf = np.array([nf[groups == g][0] for g in order])

    # --- attractor centroids (PCA frame + raw) -------------------------------
    zbar = Z[:, -LATE_LAYERS:, :].mean(axis=1)
    zbar = zbar - zbar.mean(axis=0, keepdims=True)
    hbar = H[:, -LATE_LAYERS:, :].mean(axis=1)
    hbar = hbar - hbar.mean(axis=0, keepdims=True)
    Cz = _group_centroids(zbar, groups, order)
    Ch = _group_centroids(hbar, groups, order)

    # --- G2 DECAY-CONVERGENCE (make-or-break): across|lambda| - within|lambda| >0
    M_decay = _diff_decay_matrix(Cz, Bn, lam)
    decay = _null(M_decay, grp_nf, N_NULL, np.random.default_rng(SEED + 1),
                  lambda w, a: a - w, floor=FLOOR_D_DECAY)

    # --- advisory: raw-point cosine convergence (also-pointwise vs operator-only)
    raw = _null(_cosdist_matrix(Ch), grp_nf, N_NULL, np.random.default_rng(SEED + 3),
                lambda w, a: a - w)

    # --- advisories: non-normality/modal, frequency sweep, slope, per-family --
    modal = _modal_convergence(dmd_m, Z, groups, grp_nf, order,
                               np.random.default_rng(SEED + 4))
    freq = _freq_sweep(Cz, Bn, theta, groups, grp_nf, order,
                       np.random.default_rng(SEED + 5))
    slope = _convergence_slope(Z, Bn, lam, groups, grp_nf, order)

    per_family = {}
    for f in fam_groups:
        gs = [g for g in order if grp_nf[order.index(g)] == f]
        if len(gs) >= 2:
            idx = [order.index(g) for g in gs]
            sub = M_decay[np.ix_(idx, idx)]
            iu, ju = np.triu_indices(len(idx), k=1)
            vals = sub[iu, ju]
            per_family[f] = {"n_spellings": len(gs),
                             "within_decayrate": float(np.nanmean(vals))}
        else:
            per_family[f] = {"n_spellings": len(gs), "within_decayrate": None}

    # --- verdict tree --------------------------------------------------------
    if not g0_pass:
        verdict = "VOID"
    elif decay["pass"]:
        verdict = "CONVERGENCE"
    else:
        verdict = "NO-ORBITAL-CONVERGENCE"
    pointwise = "also-pointwise" if raw["p_value"] < ALPHA else "operator-only"

    return {
        "n_probes": n, "L": L, "d": d, "P": P, "var_explained": var_explained,
        "g0": {"op_exists": op_exists, "family_ok": family_ok, "det_ok": det_ok,
               "pass": g0_pass, "op_exists_gap": dt_gates["g2"]["gap"],
               "op_exists_p": dt_gates["g2"]["p"], "fams_ge2": fams_ge2},
        "rel_resid": dmd["rel_resid"],
        "spectrum": {"n_real_modes": len(lam),
                     "mean_abs_lam": float(np.mean(lam)) if lam.size else 0.0,
                     "top_abs_lam": sorted(lam.tolist(), reverse=True)[:5],
                     "departure_from_normality": dmd_m["departure"],
                     "eigvec_cond": dmd_m["eigvec_cond"]},
        "g2_decay": decay,
        "adv_raw_point": raw,
        "adv_nonnormal_modal": modal,
        "adv_freq_sweep": freq,
        "adv_slope": slope,
        "per_family": per_family,
        "pointwise_characterization": pointwise,
        "n_groups": len(order), "groups": order, "group_nf": grp_nf.tolist(),
        "verdict": verdict,
    }


# ---------------------------------------------------------------------------
# Planted worlds (synthetic; run the FULL analyse path - s331)
# ---------------------------------------------------------------------------
def _op(rng, d, slow_band, mid_band, fast_band, ns, nf, nonnormal=False):
    lam = rng.uniform(*mid_band, size=d)
    lam[:ns] = rng.uniform(*slow_band, size=ns)
    lam[-nf:] = rng.uniform(*fast_band, size=nf)
    lam = lam * rng.choice([-1.0, 1.0], size=d)
    if nonnormal:
        M = rng.standard_normal((d, d)) + 0.6 * np.eye(d)
        return M, M @ np.diag(lam) @ np.linalg.inv(M)
    Q, _ = np.linalg.qr(rng.standard_normal((d, d)))
    return Q, Q @ np.diag(lam) @ Q.T


def _planted(kind: str, lp1: int = 41, d: int = 120, n_mid: int = 40,
             n_per: int = 20, n_spell: int = 4, nonnormal: bool = False) -> tuple:
    """Trajectory tensor + labels engineered to hit `kind`. Co-extensional pairs
    differ only by SPELLING; where the spelling lives (fast vs slow modes) decides
    whether the difference decays (CONVERGE) or persists (NO-CONVERGE)."""
    rng = np.random.default_rng({"CONVERGE": 11, "NO-CONVERGE": 22,
                                 "VOID": 44, "NONNORMAL": 55}[kind])
    ns = nf = (d - n_mid) // 2
    Q, T = _op(rng, d, (0.985, 0.995), (0.965, 0.975), (0.55, 0.70), ns, nf,
               nonnormal=nonnormal)
    slow_ax, fast_ax = Q[:, :ns], Q[:, -nf:]
    mid_ax = Q[:, ns:d - nf]

    if kind == "VOID":  # single NF family -> family_ok False
        H = rng.standard_normal((n_per * n_spell, lp1, d))
        return (H, np.array(["I"] * H.shape[0]),
                np.repeat([f"I:{s}" for s in range(n_spell)], n_per))

    cls = {c: rng.standard_normal(ns) for c in range(3)}
    H, NF, GR = [], [], []
    for ci, cn in enumerate(["I", "W", "B"]):
        for si in range(n_spell):
            sp_fast = rng.standard_normal(nf)
            sp_slow = rng.standard_normal(ns)
            sm = rng.standard_normal(n_mid)
            for _ in range(n_per):
                if kind in ("CONVERGE", "NONNORMAL"):
                    # co-ext share SLOW function; differ only in FAST spelling
                    b_s = cls[ci]
                    b_f = sp_fast * 3.0 + rng.standard_normal(nf) * 0.2
                    b_m = sm * 0.5
                else:  # NO-CONVERGE: per-SPELLING function in SLOW, NO class
                    # sharing -> co-ext and co-int differences BOTH ride slow modes
                    b_s = sp_slow * 2.0
                    b_f = sp_fast * 0.5
                    b_m = sm * 0.5
                x0 = slow_ax @ b_s + mid_ax @ b_m + fast_ax @ b_f
                tr = np.empty((lp1, d))
                tr[0] = x0
                for e in range(lp1 - 1):
                    tr[e + 1] = T @ tr[e] + 0.01 * rng.standard_normal(d)
                H.append(tr)
                NF.append(cn)
                GR.append(f"{cn}:{si}")
    return np.stack(H), np.array(NF), np.array(GR)


def run_validate() -> int:
    log("[cl3] --validate: driving planted worlds through the real gate path")
    expect = {"CONVERGE": "CONVERGENCE", "NO-CONVERGE": "NO-ORBITAL-CONVERGENCE",
              "VOID": "VOID"}
    ok = True
    for kind, want in expect.items():
        H, nf, groups = _planted(kind)
        res = analyse(H, nf, groups, np.random.default_rng(SEED), det_ok=True)
        got = res["verdict"]
        passed = got == want
        ok = ok and passed
        dcy = res["g2_decay"]
        log(f"[cl3]   {kind:12s} -> {got:24s} (want {want:24s}) "
            f"Ddecay={dcy['obs']:+.4f}(w|λ|={dcy['within']:.3f} "
            f"a|λ|={dcy['across']:.3f} p={dcy['p_value']:.3f}) "
            f"raw_p={res['adv_raw_point']['p_value']:.3f} "
            f"{'OK' if passed else 'FAIL'}")
    # non-normality sanity: normal vs non-normal planted operator departure metric
    Hn, nfn, gn = _planted("CONVERGE")
    Hx, nfx, gx = _planted("NONNORMAL", nonnormal=True)
    rn = analyse(Hn, nfn, gn, np.random.default_rng(SEED))
    rx = analyse(Hx, nfx, gx, np.random.default_rng(SEED))
    dep_n = rn["spectrum"]["departure_from_normality"]
    dep_x = rx["spectrum"]["departure_from_normality"]
    dep_ok = dep_x > dep_n
    log(f"[cl3]   non-normality sanity: departure normal={dep_n:.3f} "
        f"nonnormal={dep_x:.3f} (nonnormal>normal:{dep_ok}) "
        f"modal_skipped_normal={rn['adv_nonnormal_modal'].get('skipped')} "
        f"{'OK' if dep_ok else 'FAIL'}")
    ok = ok and dep_ok
    log(f"[cl3] validate {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
def _json_native(o: Any):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"not JSON-native: {type(o)}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-14B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--n-per", type=int, default=N_PER)
    ap.add_argument("--out", default="results/p_cl_collapse_3_operator_s339/run")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return run_validate()

    corpus = build_corpus(args.n_per, SEED)
    log(f"[cl3] corpus: {len(corpus)} probes over "
        f"{len({c['group'] for c in corpus})} clean spellings, "
        f"{len({c['nf'] for c in corpus})} families")

    be = dt.RealBackend(args.model_id, args.device, args.dtype)
    trajs = []
    for i, item in enumerate(corpus):
        trajs.append(be.trajectory(item["text"]))
        if (i + 1) % 50 == 0:
            log(f"[cl3] captured {i + 1}/{len(corpus)}")
    H = np.stack(trajs)
    log(f"[cl3] H shape {H.shape}")

    rep = np.stack([be.trajectory(corpus[i]["text"])
                    for i in range(min(DET_CHECK_N, len(corpus)))])
    value_dev = float(np.max(np.abs(rep - H[: rep.shape[0]])))
    det_ok = value_dev <= DET_TOL
    log(f"[cl3] det-repeat value_dev={value_dev} ok={det_ok}")

    if args.device == "mps":
        try:
            torch = be.torch
            del be.model
            torch.mps.empty_cache()
        except Exception:
            pass

    nf = np.array([c["nf"] for c in corpus])
    groups = np.array([c["group"] for c in corpus])
    res = analyse(H, nf, groups, np.random.default_rng(SEED), det_ok=det_ok)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    corpus_hash = hashlib.sha256(
        json.dumps([c["text"] for c in corpus], sort_keys=True).encode()
    ).hexdigest()[:16]
    meta = {
        "probe": "P-CL-COLLAPSE-3-operator",
        "frozen": "s339 pre-data freeze (Michael GO) + s339 build-time amendment "
                  "(Michael-approved): operator-geometry-la-toolkit.md sec 5b; "
                  "make-or-break = decay-rate of pairwise differences",
        "pre_data_instantiations": {
            "P_PCA": P_PCA, "PRIMARY_RANK": PRIMARY_RANK, "LATE_LAYERS": LATE_LAYERS,
            "N_PER": args.n_per, "N_NULL": N_NULL, "ALPHA": ALPHA,
            "FREQ_BANDS": FREQ_BANDS, "NONNORMAL_DEP_MIN": NONNORMAL_DEP_MIN,
            "SEED": SEED,
            "families": {k: {"arity": v["arity"],
                             "n_clean_spellings": len(v["spellings"])}
                         for k, v in FAMILIES.items()},
            "apriori_masses": {"NO-ORBITAL-CONVERGENCE": 50, "CONVERGENCE": 35,
                               "VOID": 15},
        },
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "model_id": args.model_id, "device": args.device, "dtype": args.dtype,
        "smoke": args.smoke, "n_probes": len(corpus),
        "corpus_hash": corpus_hash, "git_sha": git_sha(),
        "det_value_dev": value_dev, "det_ok": det_ok,
        "global_verdict": res["verdict"], "gates": res,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=_json_native))
    with (out / "results.jsonl").open("w") as fh:
        for c in corpus:
            fh.write(json.dumps({"id": c["id"], "nf": c["nf"], "group": c["group"],
                                 "text_len": len(c["text"])},
                                default=_json_native) + "\n")
    np.savez_compressed(out / "trajectories.npz", H=H.astype(np.float16))

    dcy = res["g2_decay"]
    pc = res["pointwise_characterization"]
    log(f"[cl3] === VERDICT: {res['verdict']} ({pc}) ===")
    log(f"[cl3] G0 op={res['g0']['op_exists']} fam={res['g0']['family_ok']} "
        f"det={det_ok} | G2 D_decay={dcy['obs']:+.4f} (w|λ|={dcy['within']:.3f} "
        f"a|λ|={dcy['across']:.3f} p={dcy['p_value']:.3f}) | "
        f"raw_p={res['adv_raw_point']['p_value']:.3f} | "
        f"departure={res['spectrum']['departure_from_normality']:.3f}")
    log(f"[cl3] wrote {out}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
