#!/usr/bin/env python3
"""P-SCHEDULE-READ arm A - is the per-direction emphasis SCHEDULE (the candidate
'trains') UNIVERSAL across models, or model-specific? (frozen s343, Michael GO).

The direct successor to s342 P-JOINT-DIAG (operator-geometry-la-toolkit.md sec
5e). s342 delivered the STATION MAP: the 9x9 route-Gram identity frame is
layer-stationary AND cross-model universal - the common switch basis exists and
is fixed. It did NOT test the TRAINS: whether the per-direction eigenvalue-vs-
layer schedule (schedules.npz) carries model-specific / dynamic content, or is
- like the frame - just another universal intensional invariant.

This arm reads the SCHEDULE across models in ONE shared cross-model frame V*
(built here from the committed grams) and asks: is the depth-schedule UNIVERSAL
(the trains run identically on every model) or MODEL-SPECIFIC (learned dynamic
content that varies)?

HONESTY BOUND (frozen, lambda measure register-check). This tests universality
across MODELS, not co-extensionality. The inference is ONE-DIRECTIONAL:
  MODEL-SPECIFIC  => the schedule carries model-contingent (learned) content
                    => the actionable lead that sharpens arm C.
  UNIVERSAL       => consistent with BOTH intensional-architectural emphasis AND
                    a shared universal *computational* schedule; does NOT alone
                    prove intensional (the 5-register tape-residency prior +
                    Occam favor intensional, but that is a prior, not this
                    measurement). So arm A is a SCOUT: MODEL-SPECIFIC is the
                    informative outcome; UNIVERSAL adds one universal invariant
                    and leaves extension/intension to arm C.
Also: identity register (9x9) only, not the 17x17 fate poles; the schedule is
EMPHASIS, not a transport operator (that is P-DMD-TRANSPORT's object); last-token
CMR routing capture; the shared V* assumes the JD-MODEL universal frame
(established s342).

Data (committed, ZERO model load): results/combinator-relationship-map/*.npz -
per-layer `gram_route_cmr_L**` (11 matched fractional-depth layers x 10 models).
All 9x9 over the SAME crystal_order [K,I,B,C,S,D,W,Y,WHNF] -> cross-model
comparable by construction.

Method (FTO-clean, reuses verbum.joint_diag; NO CBLL code, sec 0b):
  1. Pool all 10 models' 11 route grams (110 x 9x9). GLOBAL DC-remove (one shared
     Q, 9->8) so every gram lives in one 8-dim complement = the 'one atlas'
     hypothesis made concrete and comparable.
  2. ONE shared cross-model frame V* = joint-diagonalize the pooled stack.
     Express each model's per-layer grams in V* -> schedule
     S[model, dir, layer] = diag(V*^T G'_{model,layer} V*).  Shape (M, 8, L).
     All schedules share the SAME basis by construction - no per-model sign/perm
     ambiguity (V* fixed once; diag is invariant to V* column sign flips).
  3. Universality statistic U = leading-eigenvalue fraction lambda1/M of the MxM
     Pearson correlation matrix of the flattened per-model schedule fingerprints
     s_m in R^{8L} (corroborated by mean off-diagonal correlation).

Nulls (pre-registered, lambda yardstick, N=300, floor delta>=0.05 AND p<0.05):
  SHUFFLED-LAYER (PRIMARY, shape-vs-level discriminator): per model, one random
     permutation of the layer axis (all directions) - keeps each direction's
     exact value-multiset and each layer's cross-direction co-activation,
     destroys the shared DEPTH-ORDERING. real >> shuffled  <=>  a shared TIMETABLE
     (beyond layer-order-invariant level agreement).
  MATCHED-RANGE (guards the s342 low-rank-inflation scar): per (model,direction)
     keep [min,max], redraw uniform iid across layers - destroys ordering AND the
     exact multiset, keeps range. real >> matched-range  <=>  agreement beyond
     shared per-direction ranges.

FROZEN verdict tree (a-priori mass):
  UNIVERSAL-SCHEDULE 45  : pass_shuf AND pass_mr (shared depth-timetable).
  PARTIALLY-SHARED   25  : pass_mr AND NOT pass_shuf (emergent intermediate; no
                           dedicated planted world, s342 MIXED precedent).
  MODEL-SPECIFIC     20  : NOT pass_mr (the actionable lead for arm C).
  VOID               10  : V* non-convergent on the pooled stack, or degenerate
                           (schedule variance ~0).

`--validate` drives 4 planted worlds (in ALL of which the FRAME V0 is shared -
s342 established the frame is universal; only the SCHEDULE varies) through the
REAL analyse path (s331: planted plumbing == data plumbing):
  UNIVERSAL      shared depth-structured template + noise  -> UNIVERSAL-SCHEDULE
  MODEL-SPECIFIC independent random schedules              -> MODEL-SPECIFIC
  LEVEL-ONLY     shared per-direction level, no timetable  -> MODEL-SPECIFIC
                 (the critical guard: the nulls must REFUSE to promote trivial
                  level-agreement to UNIVERSAL)
  DC-DEGENERATE  shared DC only, tiny independent remainder -> NOT UNIVERSAL
                 (guards low-rank inflation; accepts MODEL-SPECIFIC or VOID)

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

from verbum.joint_diag import dc_remove, joint_diagonalize, random_orthogonal

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS (s343 pre-data freeze, Michael GO)
# ---------------------------------------------------------------------------
CRYSTAL = ("K", "I", "B", "C", "S", "D", "W", "Y", "WHNF")
N_NULL = 300           # shuffled-layer draws (primary)
N_MR = 300             # matched-range draws (guard)
ALPHA = 0.05
FLOOR = 0.05           # effect-size floor on the U statistic
SEED = 0

APRIORI = {
    "UNIVERSAL-SCHEDULE": 45,
    "PARTIALLY-SHARED": 25,
    "MODEL-SPECIFIC": 20,
    "VOID": 10,
}

FAMILY = {
    "Qwen_Qwen3-0.6B": "qwen3", "Qwen_Qwen3-4B": "qwen3", "Qwen_Qwen3-8B": "qwen3",
    "Qwen_Qwen3-14B": "qwen3", "Qwen_Qwen3-32B": "qwen3",
    "allenai_OLMo-2-1124-13B": "olmo", "HuggingFaceTB_SmolLM3-3B": "smollm",
    "mistralai_Mistral-7B-v0.3": "mistral",
    "EleutherAI_pythia-410m": "pythia", "EleutherAI_pythia-2.8b-deduped": "pythia",
}


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


# ---------------------------------------------------------------------------
# Core: shared frame V*, per-model schedules, universality statistic
# ---------------------------------------------------------------------------
def _sym(m: np.ndarray) -> np.ndarray:
    return 0.5 * (m + np.swapaxes(m, -1, -2))


def shared_frame_schedules(
    route_by_model: dict[str, np.ndarray],
) -> tuple[np.ndarray, list[str], dict]:
    """Global DC-remove -> shared V* -> per-model schedule in V*.

    Returns (S (M, m_sub, L), names, info). S[m, dir, layer] = diag of the
    model's DC-removed layer gram in the shared frame V*.
    """
    names = sorted(route_by_model)
    n_layers = [route_by_model[m].shape[0] for m in names]
    lmin = min(n_layers)
    # pooled stack over models x layers (truncate to the common layer count)
    pooled = np.concatenate(
        [route_by_model[m][:lmin] for m in names], axis=0
    ).astype(np.float64)                                   # (M*lmin, 9, 9)
    gp_all, q = dc_remove(pooled)                          # (M*lmin, 8, 8), q (9,8)
    vstar, _, jd_info = joint_diagonalize(gp_all)          # (8,8) shared frame

    m_sub = gp_all.shape[1]
    sched = np.empty((len(names), m_sub, lmin))
    for mi, name in enumerate(names):
        g = route_by_model[name][:lmin].astype(np.float64)  # (L,9,9)
        gp = _sym(np.einsum("ij,kjl,lm->kim", q.T, g, q))   # (L,8,8) shared Q
        for li in range(lmin):
            sched[mi, :, li] = np.diag(vstar.T @ gp[li] @ vstar)
    return sched, names, {
        "jd": jd_info, "n_sub": int(m_sub), "n_layers": int(lmin),
        "V": vstar, "Q": q,
    }


def universality(smat: np.ndarray) -> tuple[float, float, bool]:
    """U = leading-eigenvalue fraction of the MxM Pearson correlation matrix of
    the flattened per-model schedule fingerprints. Returns (lead_frac, mean_off,
    degenerate). Each row is centered (per-model global level removed) so U reads
    SHAPE agreement across the (dir x layer) grid, not brightness.
    """
    m = smat.shape[0]
    x = smat.reshape(m, -1)
    xc = x - x.mean(axis=1, keepdims=True)
    norms = np.linalg.norm(xc, axis=1, keepdims=True)
    degenerate = bool(np.any(norms < 1e-12))
    xn = xc / np.where(norms < 1e-12, 1.0, norms)
    r = xn @ xn.T
    w = np.linalg.eigvalsh(r)
    lead = float(w[-1] / m)
    off = r[~np.eye(m, dtype=bool)]
    return lead, float(np.mean(off)), degenerate


def _shuf_null(smat: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    m, _, ell = smat.shape
    out = np.empty(n)
    for t in range(n):
        sp = np.empty_like(smat)
        for mi in range(m):
            sp[mi] = smat[mi][:, rng.permutation(ell)]
        out[t] = universality(sp)[0]
    return out


def _mr_null(smat: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    m, d, ell = smat.shape
    lo = smat.min(axis=2, keepdims=True)
    hi = smat.max(axis=2, keepdims=True)
    span = hi - lo
    out = np.empty(n)
    for t in range(n):
        sp = lo + span * rng.random((m, d, ell))
        out[t] = universality(sp)[0]
    return out


def analyse(route_by_model: dict[str, np.ndarray], rng: np.random.Generator) -> dict:
    """Frozen analysis: shared frame -> schedules -> U -> both nulls -> verdict.
    Identical path for real data and planted worlds (s331)."""
    smat, names, info = shared_frame_schedules(route_by_model)
    converged = bool(info["jd"]["converged"])
    lead, mean_off, degenerate = universality(smat)

    u_shuf = _shuf_null(smat, N_NULL, rng)
    u_mr = _mr_null(smat, N_MR, rng)

    med_shuf, med_mr = float(np.median(u_shuf)), float(np.median(u_mr))
    p_shuf = float(np.mean(u_shuf >= lead))
    p_mr = float(np.mean(u_mr >= lead))
    delta_shuf = float(lead - med_shuf)
    delta_mr = float(lead - med_mr)
    pass_shuf = bool(p_shuf < ALPHA and delta_shuf >= FLOOR)
    pass_mr = bool(p_mr < ALPHA and delta_mr >= FLOOR)

    if (not converged) or degenerate:
        verdict = "VOID"
    elif pass_mr and pass_shuf:
        verdict = "UNIVERSAL-SCHEDULE"
    elif pass_mr and not pass_shuf:
        verdict = "PARTIALLY-SHARED"
    else:
        verdict = "MODEL-SPECIFIC"

    return {
        "verdict": verdict,
        "U": lead,
        "mean_offdiag_corr": mean_off,
        "converged": converged,
        "degenerate": degenerate,
        "n_sub": info["n_sub"],
        "n_layers": info["n_layers"],
        "n_models": len(names),
        "shuf_null": {"median": med_shuf, "q95": float(np.quantile(u_shuf, 0.95)),
                      "p": p_shuf, "delta": delta_shuf, "pass": pass_shuf},
        "mr_null": {"median": med_mr, "q95": float(np.quantile(u_mr, 0.95)),
                    "p": p_mr, "delta": delta_mr, "pass": pass_mr},
        "schedule": smat,
        "names": names,
    }


# ---------------------------------------------------------------------------
# Planted worlds (shared FRAME V0 in all; only the SCHEDULE varies)
# ---------------------------------------------------------------------------
def _grams_from_schedule(
    lam: np.ndarray, v0: np.ndarray, dc_scale: float = 4.0,
) -> np.ndarray:
    """Build (L,9,9) grams = V0 diag([dc_scale, lam[l,1:]]) V0^T. Direction 0 is
    the shared DC mode (removed by the analyse path); lam[:,1:] is the schedule
    on the 8 non-DC directions.
    """
    ell, n = lam.shape
    g = np.empty((ell, n, n))
    for li in range(ell):
        d = lam[li].copy()
        d[0] = dc_scale
        g[li] = v0 @ np.diag(d) @ v0.T
    return _sym(g)


def planted_worlds(n: int = 9, ell: int = 11, m: int = 10):
    """Four synthetic 10-model gram sets + expected verdict. In ALL worlds the
    frame V0 is SHARED (s342: the frame is universal); only the SCHEDULE differs.
    """
    rng = np.random.default_rng(SEED)
    v0 = random_orthogonal(n, rng)
    layers = np.linspace(0.0, 1.0, ell)
    worlds: dict[str, tuple[dict[str, np.ndarray], object]] = {}

    # (1) UNIVERSAL: shared depth-structured template (distinct per-direction
    #     depth profile) + small per-model noise -> UNIVERSAL-SCHEDULE.
    templ = np.zeros((ell, n))
    for d in range(1, n):
        templ[:, d] = 2.0 * np.cos(np.pi * layers * d)     # distinct frequency
    rbm = {}
    for mi in range(m):
        lam = templ + 0.05 * rng.standard_normal((ell, n))
        rbm[f"model_{mi:02d}"] = _grams_from_schedule(lam, v0)
    worlds["UNIVERSAL"] = (rbm, "UNIVERSAL-SCHEDULE")

    # (2) MODEL-SPECIFIC: independent random schedules -> MODEL-SPECIFIC.
    rbm = {}
    for mi in range(m):
        lam = rng.standard_normal((ell, n)) * np.linspace(2.0, 0.5, n)
        rbm[f"model_{mi:02d}"] = _grams_from_schedule(lam, v0)
    worlds["MODEL-SPECIFIC"] = (rbm, "MODEL-SPECIFIC")

    # (3) LEVEL-ONLY guard: shared per-direction LEVEL (constant across layers),
    #     model-specific tiny layer wobble, NO shared timetable. The nulls must
    #     REFUSE to promote level-agreement to UNIVERSAL -> MODEL-SPECIFIC.
    level = rng.standard_normal(n) * np.linspace(2.0, 0.5, n)
    rbm = {}
    for mi in range(m):
        lam = np.tile(level, (ell, 1)) + 0.03 * rng.standard_normal((ell, n))
        rbm[f"model_{mi:02d}"] = _grams_from_schedule(lam, v0)
    worlds["LEVEL-ONLY"] = (rbm, "MODEL-SPECIFIC")

    # (4) DC-DEGENERATE: shared DC only, tiny INDEPENDENT remainder -> must NOT
    #     be UNIVERSAL (guards low-rank inflation). Accept MODEL-SPECIFIC or VOID.
    rbm = {}
    for mi in range(m):
        lam = 1e-3 * rng.standard_normal((ell, n))
        rbm[f"model_{mi:02d}"] = _grams_from_schedule(lam, v0)
    worlds["DC-DEGENERATE"] = (rbm, {"MODEL-SPECIFIC", "VOID"})
    return worlds


def run_validate() -> int:
    log("[sched] --validate: planted worlds through the real analyse path")
    ok = True
    for name, (rbm, expect) in planted_worlds().items():
        rng = np.random.default_rng(SEED)
        res = analyse(rbm, rng)
        want = expect if isinstance(expect, set) else {expect}
        passed = res["verdict"] in want
        ok = ok and passed
        exp_s = "|".join(sorted(want))
        log(f"[sched]   {name:14s} -> {res['verdict']:18s} (want {exp_s:24s}) "
            f"U={res['U']:.3f} shuf_med={res['shuf_null']['median']:.3f} "
            f"p_shuf={res['shuf_null']['p']:.3f} mr_med={res['mr_null']['median']:.3f} "
            f"p_mr={res['mr_null']['p']:.3f}  {'OK' if passed else 'FAIL'}")
    log(f"[sched] validate {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# Real backend
# ---------------------------------------------------------------------------
def load_route_grams(path: Path) -> np.ndarray:
    d = np.load(path)
    keys = sorted(k for k in d.files if k.startswith("gram_route_cmr_L"))
    return np.stack([d[k].astype(np.float64) for k in keys])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gram-dir", default="results/combinator-relationship-map")
    ap.add_argument("--out", default="results/p_schedule_read_s343/run")
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return run_validate()

    paths = sorted(
        p for p in glob.glob(f"{args.gram_dir}/*.npz")
        if "v15" not in Path(p).name
    )
    route_by_model = {}
    for p in paths:
        name = Path(p).stem
        route = load_route_grams(Path(p))
        route_by_model[name] = route
        log(f"[sched] {name}: {route.shape[0]} layers, gram {route.shape[1]}x"
            f"{route.shape[2]}")

    rng = np.random.default_rng(SEED)
    res = analyse(route_by_model, rng)
    smat = res.pop("schedule")
    names = res.pop("names")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    gram_hash = hashlib.sha256(
        json.dumps(sorted(route_by_model), sort_keys=True).encode()
    ).hexdigest()[:16]
    meta = {
        "probe": "P-SCHEDULE-READ-A",
        "frozen": "s343 pre-data freeze (Michael GO): schedule-universality on "
                  "committed CMR route grams; operator-geometry-la-toolkit.md "
                  "sec 5e successor",
        "pre_data": {
            "N_NULL": N_NULL, "N_MR": N_MR, "ALPHA": ALPHA, "FLOOR": FLOOR,
            "SEED": SEED, "apriori": APRIORI,
            "statistic": "U = lambda1/M of MxM Pearson corr of flattened "
                         "per-model schedules (8x11)",
            "nulls": {"shuffled_layer": "primary (shape-vs-level)",
                      "matched_range": "guard (low-rank inflation)"},
            "honesty_bound": "tests universality across MODELS not "
                             "co-extensionality; MODEL-SPECIFIC is the actionable "
                             "outcome; UNIVERSAL does not alone prove intensional",
        },
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "gram_dir": args.gram_dir, "n_models": len(names),
        "gram_hash": gram_hash, "git_sha": git_sha(),
        "families": {nm: FAMILY.get(nm, "other") for nm in names},
        "result": res,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=_json_native))
    np.savez_compressed(
        out / "schedules_shared_frame.npz",
        schedule=smat, names=np.array(names),
    )

    ap_mass = APRIORI.get(res["verdict"])
    log(f"[sched] === VERDICT: {res['verdict']} (a-priori {ap_mass}) ===")
    log(f"[sched] U={res['U']:.3f} mean_offdiag={res['mean_offdiag_corr']:.3f} "
        f"n_sub={res['n_sub']} n_layers={res['n_layers']} n_models={res['n_models']}")
    log(f"[sched] shuf-null: median={res['shuf_null']['median']:.3f} "
        f"p={res['shuf_null']['p']:.3f} delta={res['shuf_null']['delta']:+.3f} "
        f"pass={res['shuf_null']['pass']}")
    log(f"[sched] mr-null:   median={res['mr_null']['median']:.3f} "
        f"p={res['mr_null']['p']:.3f} delta={res['mr_null']['delta']:+.3f} "
        f"pass={res['mr_null']['pass']}")
    log(f"[sched] wrote {out}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
