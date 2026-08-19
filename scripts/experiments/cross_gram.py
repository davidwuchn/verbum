#!/usr/bin/env python3
"""P-CROSS-GRAM - do labeled semantic directions coincide with W_down's
principal write-axes? (frozen s341, Michael GO; Option C - residual register).

The one probe that deliberately compares our LABELED anchors against the
principal directions of the residual-writer weight W_down. Motivated by the
operator-geometry toolkit sec 3 (the "W_down bridge") but run in Option C: the
d_model RESIDUAL register, where W_down's left singular vectors U already live -
avoiding the double register gap (sign + SiLU-gating) that voids the d_ff bridge
against the stored sign(gate-preact) centroids.

FTO (operator-geometry-la-toolkit.md sec 0b, Michael ruling s341): this takes a
textbook economy SVD (Golub & Van Loan; here the left singular vectors are the
eigenvectors of W W^T) of OUR OWN public model's OWN down_proj weight, in OUR OWN
function, projects OUR labeled anchors, and emits a COMPARISON - never a rotation
or realigned model. NO CBLL code is opened or vendored (grep-clean invariant).
CBLL cited once as description-level consilience only.

FROZEN verdict tree (operator-geometry-la-toolkit.md sec 3a):
  CG0 INSTRUMENT   SVD finite + spectrum decays; --validate recovers 4 worlds
                   -> else VOID
  CG1 CONCENTRATION band-median PR_X below the random-direction null (p<0.05):
                   centroids live concentrated in the writer subspace
                   -> else NO-COINCIDENCE
  CG2 SPECIFICITY  band-median inter-combinator alignment-profile correlation
                   vs random-9 null: > null q95 (p_high<0.05) -> GENERIC-WRITE-
                   STRUCTURE (shared axes); else -> LABEL-ALIGNED (distinct axes)
  CG3 OSCILLATOR   (advisory) fire (mean active reducers) vs halt (WHNF) opposite
                   sign on a shared high-energy U-axis -> +OSCILLATOR subtag

A-priori masses: GENERIC-WRITE-STRUCTURE 35 / LABEL-ALIGNED 30 (+OSCILLATOR) /
NO-COINCIDENCE 25 / VOID 10.

Register: d_model residual (last-token), labeled side REUSES the s338
H (300,41,5120) combinator-tagged trajectories (zero new inference); weight side
= left singular vectors of down_proj per layer.

`--validate` drives 4 planted worlds (LABEL-ALIGNED / GENERIC / NO-COINCIDENCE /
OSCILLATOR) through the REAL analyse path (s331: planted plumbing == probe
plumbing) - synthetic H + synthetic down_proj, same centroid extraction, same
SVD, same gates. No model is loaded.

License: MIT.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from combinator_relationship_map import git_sha, log

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS (sec 3a, s341)
# ---------------------------------------------------------------------------
COMBINATORS = ("K", "I", "B", "C", "S", "D", "W", "Y", "WHNF")
ACTIVE = ("K", "I", "B", "C", "S", "D", "W")   # "fire" pole proxy
HALT = "WHNF"                                    # "halt" pole proxy
DIVERGE = "Y"                                    # "diverge" pole proxy
R_PRIMARY = 128
R_SWEEP = (64, 128, 256)
N_RAND = 1000            # random-direction null (CG1)
N_RAND9 = 200            # random-9 null (CG2)
ALPHA = 0.05
BAND = (8, 32)          # verdict band: mid-stack layers [8,32) (a priori)
SEED = 0
OSC_PR_MAX = 2.0        # CG3: (fire-halt) must concentrate (PR<=this) on ~1 axis
OSC_MIN = 0.05          # CG3: min per-pole |projection| on the shared axis
OSC_BALANCE = 0.30      # CG3: min(|pf|,|ph|)/max(|pf|,|ph|) - a true bipolar pair
                        #      has BOTH poles strong (not one strong, one leaking)

VERDICTS = ("LABEL-ALIGNED", "GENERIC-WRITE-STRUCTURE", "NO-COINCIDENCE", "VOID")


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
# Textbook linear algebra (FTO-clean; left singular vectors via eig(W W^T))
# ---------------------------------------------------------------------------
def left_singular(W: np.ndarray, r: int) -> tuple[np.ndarray, np.ndarray]:
    """Top-r left singular vectors U_r (d_out, r) and singular values s_r.

    For W (d_out, d_in), the left singular vectors are the eigenvectors of
    G = W W^T and the singular values are sqrt of its eigenvalues (Golub &
    Van Loan, Matrix Computations). Exact; cheaper than a full economy SVD when
    d_out << d_in and only U is needed. Public-domain LA (NOT CBLL code).
    """
    G = W @ W.T                                  # (d_out, d_out) symmetric PSD
    evals, evecs = np.linalg.eigh(G)             # ascending
    order = np.argsort(evals)[::-1][:r]
    s = np.sqrt(np.clip(evals[order], 0.0, None))
    U = evecs[:, order]
    return U.astype(np.float64), s.astype(np.float64)


def _unit(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def centroids_from_H(
    H: np.ndarray, labels: list[str]
) -> dict[int, dict[str, np.ndarray]]:
    """Per-layer, mean-centered, unit-normalized combinator centroids.

    H: (n, L+1, d) last-token residual trajectories. Returns
    {layer_index -> {combinator -> unit vector (d,)}} for hidden[1..L]
    (paired downstream with W_down of block (layer_index-1)).
    """
    lp1 = H.shape[1]
    lab = np.asarray(labels)
    out: dict[int, dict[str, np.ndarray]] = {}
    for hs in range(1, lp1):                      # hidden state 1..L (skip embed)
        layer = hs - 1                            # block index that produced it
        X = H[:, hs, :].astype(np.float64)
        gmean = X.mean(axis=0)
        cents = {}
        for comb in COMBINATORS:
            m = lab == comb
            if not m.any():
                continue
            cents[comb] = _unit(X[m].mean(axis=0) - gmean)
        out[layer] = cents
    return out


# ---------------------------------------------------------------------------
# Core statistics on one (centroids, U_r) layer
# ---------------------------------------------------------------------------
def _profiles(cents: dict[str, np.ndarray], U: np.ndarray) -> dict[str, np.ndarray]:
    """Alignment profile a_k^X = (u_k . c_X)^2 for each combinator present."""
    return {c: (U.T @ v) ** 2 for c, v in cents.items()}


def _pr(a: np.ndarray) -> float:
    s1 = float(a.sum())
    s2 = float((a * a).sum())
    return (s1 * s1 / s2) if s2 > 0 else float(a.size)


def _mean_pairwise_corr(profs: list[np.ndarray]) -> float:
    if len(profs) < 2:
        return 0.0
    M = np.stack(profs)
    C = np.corrcoef(M)
    iu = np.triu_indices(len(profs), k=1)
    vals = C[iu]
    vals = vals[np.isfinite(vals)]
    return float(np.mean(vals)) if vals.size else 0.0


def _mean_pairwise_abscos(cents: list[np.ndarray]) -> float:
    if len(cents) < 2:
        return 0.0
    M = np.stack([_unit(c) for c in cents])
    C = np.abs(M @ M.T)
    iu = np.triu_indices(len(cents), k=1)
    return float(np.mean(C[iu]))


def analyse(
    cents_by_layer: dict[int, dict[str, np.ndarray]],
    U_by_layer: dict[int, np.ndarray],
    d_model: int,
    band: tuple[int, int],
    rng: np.random.Generator,
    r: int = R_PRIMARY,
) -> dict:
    """Full frozen-gate analysis. Shared by real + planted paths (s331)."""
    band_layers = [
        ell for ell in sorted(cents_by_layer)
        if band[0] <= ell < band[1] and ell in U_by_layer
    ]
    per_layer = {}
    pr_obs_band: list[float] = []
    corr_obs_band: list[float] = []
    abscos_obs_band: list[float] = []
    pr_null_pool: list[float] = []
    corr_null_pool: list[float] = []
    abscos_null_pool: list[float] = []
    f_obs_band: list[float] = []

    for ell in band_layers:
        cents = cents_by_layer[ell]
        U = U_by_layer[ell][:, :r]
        combs = [c for c in COMBINATORS if c in cents]
        profs = _profiles(cents, U)
        pr_x = np.array([_pr(profs[c]) for c in combs])
        f_x = np.array([float(profs[c].sum()) for c in combs])
        prof_list = [profs[c] for c in combs]
        cent_list = [cents[c] for c in combs]

        pr_med = float(np.median(pr_x))
        f_med = float(np.median(f_x))
        corr = _mean_pairwise_corr(prof_list)
        abscos = _mean_pairwise_abscos(cent_list)

        # random-direction null (CG1): PR of random unit dirs on the same U
        rand = rng.standard_normal((N_RAND, d_model))
        rand /= np.linalg.norm(rand, axis=1, keepdims=True)
        ar = (rand @ U) ** 2                       # (N_RAND, r)
        pr_rand = (ar.sum(1) ** 2) / (ar * ar).sum(1)

        # random-9 null (CG2): profile-corr + |cos| of n_comb random dirs
        n_comb = len(combs)
        corr_null = np.empty(N_RAND9)
        abscos_null = np.empty(N_RAND9)
        for j in range(N_RAND9):
            rr = rng.standard_normal((n_comb, d_model))
            rr /= np.linalg.norm(rr, axis=1, keepdims=True)
            rp = [(U.T @ rr[k]) ** 2 for k in range(n_comb)]
            corr_null[j] = _mean_pairwise_corr(rp)
            abscos_null[j] = _mean_pairwise_abscos([rr[k] for k in range(n_comb)])

        per_layer[ell] = {
            "pr_med": pr_med, "f_med": f_med, "corr": corr, "abscos": abscos,
            "pr_rand_q05": float(np.quantile(pr_rand, 0.05)),
            "corr_null_q95": float(np.quantile(corr_null, 0.95)),
            "top_axes": {c: int(np.argmax(profs[c])) for c in combs},
        }
        pr_obs_band.append(pr_med)
        f_obs_band.append(f_med)
        corr_obs_band.append(corr)
        abscos_obs_band.append(abscos)
        pr_null_pool.extend(pr_rand.tolist())
        corr_null_pool.extend(corr_null.tolist())
        abscos_null_pool.extend(abscos_null.tolist())

    pr_null_pool_a = np.array(pr_null_pool)
    corr_null_pool_a = np.array(corr_null_pool)
    abscos_null_pool_a = np.array(abscos_null_pool)

    pr_obs = float(np.median(pr_obs_band)) if pr_obs_band else float("nan")
    f_obs = float(np.median(f_obs_band)) if f_obs_band else float("nan")
    corr_obs = float(np.median(corr_obs_band)) if corr_obs_band else float("nan")
    abscos_obs = float(np.median(abscos_obs_band)) if abscos_obs_band else 0.0

    # CG1: PR below random-direction null (concentration)
    p_cg1 = float(np.mean(pr_null_pool_a <= pr_obs)) if pr_null_pool_a.size else 1.0
    cg1_pass = bool(p_cg1 < ALPHA)

    # CG2: profile-corr above random-9 null q95 -> GENERIC (shared axes)
    p_cg2_high = (
        float(np.mean(corr_null_pool_a >= corr_obs)) if corr_null_pool_a.size else 1.0
    )
    generic = bool(p_cg2_high < ALPHA)
    # |cos| corroboration: are centroids mutually distinguishable? (below null)
    p_abscos_low = (
        float(np.mean(abscos_null_pool_a <= abscos_obs))
        if abscos_null_pool_a.size else 1.0
    )

    # CG3 OSCILLATOR (advisory): fire vs halt opposite-sign on a shared top axis
    osc = _oscillator(cents_by_layer, U_by_layer, band_layers, r)

    # verdict
    if not cg1_pass:
        verdict = "NO-COINCIDENCE"
    elif generic:
        verdict = "GENERIC-WRITE-STRUCTURE"
    else:
        verdict = "LABEL-ALIGNED"

    return {
        "r": r,
        "band": list(band),
        "band_layers": band_layers,
        "pr_obs": pr_obs,
        "pr_null_median": (
            float(np.median(pr_null_pool_a)) if pr_null_pool_a.size else None
        ),
        "f_obs": f_obs,
        "corr_obs": corr_obs,
        "corr_null_q95_pooled": (
            float(np.quantile(corr_null_pool_a, 0.95))
            if corr_null_pool_a.size else None
        ),
        "abscos_obs": abscos_obs,
        "abscos_null_median": (
            float(np.median(abscos_null_pool_a)) if abscos_null_pool_a.size else None
        ),
        "cg1": {"p": p_cg1, "pass": cg1_pass},
        "cg2": {"p_high": p_cg2_high, "generic": generic, "p_abscos_low": p_abscos_low},
        "cg3": osc,
        "verdict": verdict,
        "verdict_tag": verdict + ("+OSCILLATOR" if osc["fires"] else ""),
        "per_layer": {int(k): v for k, v in per_layer.items()},
    }


def _oscillator(cents_by_layer, U_by_layer, band_layers, r) -> dict:
    """Advisory: are fire (mean active) and halt (WHNF) two ends of ONE axis?

    A true bipolar oscillator means fire ~ +a*u_k and halt ~ -b*u_k, so the
    DIFFERENCE d = fire - halt ~ (a+b)*u_k concentrates on a single U-axis
    (PR ~ 1). Using the difference cancels the per-layer global mean exactly,
    so this is immune to the mean-centering coupling that inflates a per-pole
    top-axis test. Fires iff d concentrates (PR <= OSC_PR_MAX) on an axis where
    fire and halt have opposite sign, across >=50% of band layers.
    """
    hits = 0
    total = 0
    best = {"axis": None, "fire": 0.0, "halt": 0.0, "layer": None, "pr": None}
    for ell in band_layers:
        cents = cents_by_layer[ell]
        if HALT not in cents or not all(a in cents for a in ACTIVE):
            continue
        U = U_by_layer[ell][:, :r]
        fire = _unit(np.mean([cents[a] for a in ACTIVE], axis=0))
        halt = cents[HALT]
        pd = U.T @ (fire - halt)
        pr_d = _pr(pd * pd)
        k = int(np.argmax(pd * pd))
        pf = float(U[:, k] @ fire)
        ph = float(U[:, k] @ halt)
        total += 1
        balance = min(abs(pf), abs(ph)) / max(abs(pf), abs(ph), 1e-12)
        if (pr_d <= OSC_PR_MAX and np.sign(pf) != np.sign(ph)
                and abs(pf) >= OSC_MIN and abs(ph) >= OSC_MIN
                and balance >= OSC_BALANCE):
            hits += 1
            if best["pr"] is None or pr_d < best["pr"]:
                best = {"axis": k, "fire": pf, "halt": ph, "layer": int(ell),
                        "pr": float(pr_d)}
    frac = (hits / total) if total else 0.0
    return {"fires": bool(frac >= 0.5), "hit_frac": frac, "n_layers": total,
            "best": best}


# ---------------------------------------------------------------------------
# Planted worlds (synthetic H + synthetic down_proj -> REAL analyse path)
# ---------------------------------------------------------------------------
def _planted_wdown(U_full: np.ndarray, s: np.ndarray, d_ff: int, rng) -> np.ndarray:
    """down_proj (d, d_ff) whose left singular vectors are U_full[:, :k]."""
    k = s.size
    Q, _ = np.linalg.qr(rng.standard_normal((d_ff, k)))
    return (U_full[:, :k] * s) @ Q.T


def planted_worlds(d=256, d_ff=512, L=10, n_per=24, r=64):
    """Four synthetic worlds; each returns (H, labels, Wd_by_layer, expect)."""
    worlds = {}
    n = n_per * len(COMBINATORS)
    labels = [c for c in COMBINATORS for _ in range(n_per)]
    k = r
    s = np.linspace(k, 1.0, k)                    # decaying spectrum

    def build(centre_fn, world_seed):
        rng = np.random.default_rng(world_seed)
        U_full, _ = np.linalg.qr(rng.standard_normal((d, d)))
        base = rng.standard_normal(d) * 2.0        # shared DC offset
        H = np.empty((n, L + 1, d))
        H[:, 0, :] = rng.standard_normal((n, d)) * 0.1
        Wd = {}
        for ell in range(L):
            Wd[ell] = _planted_wdown(U_full, s, d_ff, np.random.default_rng(
                world_seed * 100 + ell))
        for i, comb in enumerate(labels):
            direction = centre_fn(comb, U_full, rng)
            for hs in range(1, L + 1):
                H[i, hs, :] = (base + 3.0 * direction
                               + 0.4 * rng.standard_normal(d))
        return H, labels, Wd, U_full

    # (1) LABEL-ALIGNED: each combinator on a distinct top axis
    def aligned(comb, U, rng):
        return U[:, COMBINATORS.index(comb)]
    H, lab, Wd, _ = build(aligned, 101)
    worlds["LABEL-ALIGNED"] = (H, lab, Wd, "LABEL-ALIGNED")

    # (2) GENERIC: distinct centroids all living in a SHARED low-rank axis
    #     subset {U0,U1,U2} (survive mean-centering, but share the same axes)
    def generic(comb, U, rng):
        cr = np.random.default_rng(2020 + COMBINATORS.index(comb))
        coef = cr.standard_normal(3)
        return _unit(coef[0] * U[:, 0] + coef[1] * U[:, 1] + coef[2] * U[:, 2])
    H, lab, Wd, _ = build(generic, 202)
    worlds["GENERIC"] = (H, lab, Wd, "GENERIC-WRITE-STRUCTURE")

    # (3) NO-COINCIDENCE: random directions (spread across all axes)
    def nocoinc(comb, U, rng):
        return _unit(np.random.default_rng(
            303 + hash(comb) % 1000).standard_normal(U.shape[0]))
    H, lab, Wd, _ = build(nocoinc, 303)
    worlds["NO-COINCIDENCE"] = (H, lab, Wd, "NO-COINCIDENCE")

    # (4) OSCILLATOR: actives on +axis0, WHNF on -axis0 (bipolar), Y on axis1
    def osc(comb, U, rng):
        if comb == HALT:
            return -U[:, 0]
        if comb == DIVERGE:
            return U[:, 1]
        return U[:, 0]
    H, lab, Wd, _ = build(osc, 404)
    worlds["OSCILLATOR"] = (H, lab, Wd, "GENERIC-WRITE-STRUCTURE")  # +OSCILLATOR
    return worlds, r


def run_validate() -> int:
    log("[cross] --validate: planted worlds through the real analyse path")
    worlds, r = planted_worlds()
    ok = True
    for name, (H, labels, Wd, expect) in worlds.items():
        cents = centroids_from_H(H, labels)
        U_by = {ell: left_singular(Wd[ell], r)[0] for ell in Wd}
        d_model = H.shape[2]
        rng = np.random.default_rng(SEED)
        res = analyse(cents, U_by, d_model, (0, H.shape[1] - 1), rng, r=r)
        got = res["verdict"]
        passed = got == expect
        # CG3 is ADVISORY: --validate certifies the verdict TREE (CG0/CG1/CG2).
        # CG3's only planted requirement is "can detect a real oscillator" ->
        # must fire on the OSCILLATOR world. It also fires on LABEL-ALIGNED as a
        # KNOWN confound (the fire=mean-of-actives proxy develops a large
        # normalized leak onto the halt axis under mean-centering), so a firing
        # CG3 on real data is NOT strong consilience evidence - only the
        # quantitative bipolar strength (best.balance/pr) is read, cautiously.
        if name == "OSCILLATOR":
            passed = passed and res["cg3"]["fires"]
        extra = f" osc_frac={res['cg3']['hit_frac']:.2f}"
        flag = "OK" if passed else "FAIL"
        ok = ok and passed
        log(f"[cross]   {name:15s} -> {res['verdict_tag']:28s} (want {expect:22s}) "
            f"cg1_p={res['cg1']['p']:.3f} corr={res['corr_obs']:+.3f} "
            f"pr={res['pr_obs']:.1f}{extra}  {flag}")
    log(f"[cross] validate {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# Real backend
# ---------------------------------------------------------------------------
def load_H(run_dir: Path) -> tuple[np.ndarray, list[str]]:
    z = np.load(run_dir / "trajectories.npz")
    H = z["H"].astype(np.float32)
    labels = []
    with (run_dir / "results.jsonl").open() as fh:
        for line in fh:
            labels.append(json.loads(line)["combinator"])
    assert len(labels) == H.shape[0], (len(labels), H.shape)
    return H, labels


def snapshot_dir(model_id: str) -> Path:
    slug = "models--" + model_id.replace("/", "--")
    base = Path.home() / ".cache/huggingface/hub" / slug / "snapshots"
    snaps = sorted(glob.glob(str(base / "*")))
    if not snaps:
        raise FileNotFoundError(f"no snapshot for {model_id} under {base}")
    return Path(snaps[-1])


def down_proj_svds(model_id: str, n_layers: int, r: int) -> dict[int, np.ndarray]:
    """Left singular vectors U_r of down_proj per layer, read from safetensors."""
    from safetensors import safe_open

    snap = snapshot_dir(model_id)
    index = json.loads((snap / "model.safetensors.index.json").read_text())
    wmap = index["weight_map"]
    U_by = {}
    for ell in range(n_layers):
        key = f"model.layers.{ell}.mlp.down_proj.weight"
        shard = wmap[key]
        with safe_open(str(snap / shard), framework="pt") as f:
            W = f.get_tensor(key).float().numpy()   # (d_model, d_ff)
        U, s = left_singular(W, r)
        U_by[ell] = U
        if (ell + 1) % 10 == 0:
            log(f"[cross] SVD {ell + 1}/{n_layers} d={W.shape} s0={s[0]:.1f} "
                f"s_r={s[-1]:.2f}")
    return U_by


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-14B")
    ap.add_argument("--h-run", default="results/p_dmd_transport_s338/run_14b")
    ap.add_argument("--r", type=int, default=R_PRIMARY)
    ap.add_argument("--out", default="results/p_cross_gram_s341/run_14b")
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return run_validate()

    H, labels = load_H(Path(args.h_run))
    d_model = H.shape[2]
    n_layers = H.shape[1] - 1
    log(f"[cross] H {H.shape}; d_model={d_model} n_layers={n_layers}")

    cents = centroids_from_H(H, labels)
    U_by = down_proj_svds(args.model_id, n_layers, max(R_SWEEP))

    results_by_r = {}
    for r in R_SWEEP:
        U_r = {ell: U_by[ell][:, :r] for ell in U_by}
        rng = np.random.default_rng(SEED)
        results_by_r[r] = analyse(cents, U_r, d_model, BAND, rng, r=r)

    primary = results_by_r[args.r]
    verdict = primary["verdict_tag"]

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    corpus_hash = hashlib.sha256(
        json.dumps(labels, sort_keys=True).encode()).hexdigest()[:16]
    meta = {
        "probe": "P-CROSS-GRAM",
        "frozen": "s341 pre-data freeze (Michael GO): "
                  "operator-geometry-la-toolkit.md sec 3a (Option C)",
        "pre_data": {
            "R_PRIMARY": R_PRIMARY, "R_SWEEP": list(R_SWEEP), "N_RAND": N_RAND,
            "N_RAND9": N_RAND9, "ALPHA": ALPHA, "BAND": list(BAND), "SEED": SEED,
            "apriori_masses": {"GENERIC-WRITE-STRUCTURE": 35,
                               "LABEL-ALIGNED": 30, "NO-COINCIDENCE": 25,
                               "VOID": 10},
        },
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "model_id": args.model_id, "h_run": args.h_run,
        "h_corpus_hash": corpus_hash, "git_sha": git_sha(),
        "global_verdict": verdict,
        "primary_r": args.r,
        "results_by_r": {int(k): v for k, v in results_by_r.items()},
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=_json_native))

    log(f"[cross] === VERDICT: {verdict} ===")
    for r in R_SWEEP:
        rr = results_by_r[r]
        log(f"[cross] r={r:3d}: {rr['verdict_tag']:28s} "
            f"CG1 p={rr['cg1']['p']:.3f}({'Y' if rr['cg1']['pass'] else 'N'}) "
            f"CG2 corr={rr['corr_obs']:+.3f} vs q95={rr['corr_null_q95_pooled']:+.3f} "
            f"generic={rr['cg2']['generic']} | osc={rr['cg3']['fires']}")
    log(f"[cross] wrote {out}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
