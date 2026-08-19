#!/usr/bin/env python3
"""P-JOINT-DIAG - do the per-layer / per-model 9x9 route Grams share a COMMON
eigenframe (the invariant 'switch basis' the route map needs)? (frozen s342,
Michael GO).

The reframe's direct successor (state s342): the static Grams are 'station maps
- no trains' (gram-registers-and-the-route-map.md sec route-map); a shared
eigenframe is the coordinate system the trains (per-direction eigenvalue-vs-layer
schedule) would ride in. Complements s338 (residual TRANSPORT OPERATOR is
stationary) and s341 (the crystal is a d_ff ROUTING-register property) in a third
object: the routing-Gram eigenframe.

Data (committed, ZERO model load): results/combinator-relationship-map/*.npz -
per-layer `gram_route_cmr_L**` (11 fractional-depth layers x 10 models) + one
`gram_hidden_cmr` per model. All 9x9 over the SAME crystal_order
[K,I,B,C,S,D,W,Y,WHNF] -> cross-model comparable by construction.

Method (FTO-clean): Cardoso & Souloumiac (1996) orthogonal joint diagonalization
via the Jacobi-angle sweep, our own `verbum.joint_diag` (textbook LA, NO CBLL
code; operator-geometry-la-toolkit.md sec 0b). The shared DC ('everything-
correlates', top eigenvalue ~2.4-3.9) mode is projected out first (s341 mean-
centering discipline); the verdict is NULL-RELATIVE only (soft bulk eigenvectors,
gaps 0.02-0.08 -> individual eigenvectors ill-defined; absolute D is meaningless).

Statistic: D_joint = mean_k Sum_i (V^T G'_k V)_ii^2 / ||G'_k||_F^2 in [0,1] on the
DC-removed stack, under the jointly-optimised orthogonal V.

Nulls (pre-registered, lambda yardstick):
  PRIMARY  per-context random ORTHOGONAL rotation (preserves each spectrum,
           destroys frame alignment) - the textbook 'no common eigenframe' null.
  ADVISORY per-context opcode-label PERMUTATION (stays gram-class; node-align).
  Floor: D_real - median(D_null) >= 0.05 AND p < 0.05.

Two arms:
  JD-LAYER  (primary)   per model, JD the 11 layer route Grams -> is the routing
                        frame LAYER-STATIONARY?
  JD-MODEL  (secondary) across the 10 models at each matched fractional depth, JD
                        the route Grams -> UNIVERSAL-FRAME, or the informative
                        refinement SIGN-ONLY (s314: universality lives in the
                        sign PATTERN; a shared eigenframe is strictly stronger).

FROZEN verdict trees (a-priori mass):
  JD-LAYER : LAYER-STATIONARY-FRAME 50 / MIXED-FAMILY-SPLIT 22 /
             LAYER-DRIFTING-FRAME 20 / VOID 8
  JD-MODEL : UNIVERSAL-FRAME 40 / SIGN-ONLY 35 / VOID 25

`--validate` drives 4 planted worlds (COMMON-FRAME / NO-FRAME / DC-ONLY /
PARTIAL) through the REAL analyse path (s331: planted plumbing == probe plumbing).
The DC-ONLY world is the critical guard: shared DC + independent remainder must
verdict DRIFTING (else DC-removal is broken and would manufacture STATIONARY).

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

from verbum.joint_diag import (
    common_frame_fraction,
    dc_remove,
    diag_energy_fraction,
    joint_diagonalize,
    random_orthogonal,
)

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS (s342 pre-data freeze, Michael GO)
# ---------------------------------------------------------------------------
CRYSTAL = ("K", "I", "B", "C", "S", "D", "W", "Y", "WHNF")
N_NULL = 300            # rotation-null draws (primary)
N_PERM = 300            # permutation-null draws (advisory)
ALPHA = 0.05
FLOOR = 0.05            # effect-size floor: D_real - median(D_null)
SEED = 0
FRAC_STATIONARY = 0.70  # JD-LAYER: >= this fraction of models pass -> STATIONARY
FRAC_DRIFTING = 0.30    # JD-LAYER: <= this fraction pass -> DRIFTING (else MIXED)
IDX_MAJORITY = 0.50     # JD-MODEL: > this fraction of depth indices pass -> UNIV

APRIORI_LAYER = {
    "LAYER-STATIONARY-FRAME": 50,
    "MIXED-FAMILY-SPLIT": 22,
    "LAYER-DRIFTING-FRAME": 20,
    "VOID": 8,
}
APRIORI_MODEL = {"UNIVERSAL-FRAME": 40, "SIGN-ONLY": 35, "VOID": 25}

# family tags for the split read (s314 precedent; descriptive, not gated)
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
# Core statistic + nulls (shared real + planted path, s331)
# ---------------------------------------------------------------------------
def _rotation_null(gp: np.ndarray, n_draws: int, rng: np.random.Generator):
    """D under independent random rotations of the DC-removed stack gp (K,m,m)."""
    k, m, _ = gp.shape
    out = np.empty(n_draws)
    for t in range(n_draws):
        gr = np.empty_like(gp)
        for i in range(k):
            r = random_orthogonal(m, rng)
            gr[i] = r @ gp[i] @ r.T
        v, _, _ = joint_diagonalize(gr)
        out[t] = diag_energy_fraction(v, gr)
    return out


def _perm_null(grams: np.ndarray, n_draws: int, rng: np.random.Generator):
    """D under independent opcode-label permutations (rows+cols) then DC-remove."""
    k, n, _ = grams.shape
    out = np.empty(n_draws)
    for t in range(n_draws):
        gperm = np.empty_like(grams)
        for i in range(k):
            p = rng.permutation(n)
            gperm[i] = grams[i][np.ix_(p, p)]
        out[t], _ = common_frame_fraction(gperm)
    return out


def analyse_set(grams: np.ndarray, rng: np.random.Generator) -> dict:
    """Frozen per-set analysis: D_real, both nulls, local verdict.

    Local verdict (per set/model): STATIONARY iff the rotation-null gate passes
    (p_rot < ALPHA and D_real - median >= FLOOR) and JD converged; VOID iff JD
    did not converge on the real stack; else DRIFTING.
    """
    grams = np.asarray(grams, dtype=np.float64)
    d_real, info = common_frame_fraction(grams)
    converged = bool(info["jd"]["converged"])
    gp = info["Gp"]

    d_rot = _rotation_null(gp, N_NULL, rng)
    d_perm = _perm_null(grams, N_PERM, rng)

    med_rot = float(np.median(d_rot))
    med_perm = float(np.median(d_perm))
    p_rot = float(np.mean(d_rot >= d_real))
    p_perm = float(np.mean(d_perm >= d_real))
    delta_rot = float(d_real - med_rot)
    delta_perm = float(d_real - med_perm)

    pass_rot = bool(p_rot < ALPHA and delta_rot >= FLOOR and converged)
    pass_perm = bool(p_perm < ALPHA and delta_perm >= FLOOR and converged)

    if not converged:
        verdict = "VOID"
    elif pass_rot:
        verdict = "STATIONARY"
    else:
        verdict = "DRIFTING"

    return {
        "d_real": float(d_real),
        "n_sub": int(info["n_sub"]),
        "converged": converged,
        "jd_sweeps": int(info["jd"]["sweeps"]),
        "rot_null": {"median": med_rot, "q95": float(np.quantile(d_rot, 0.95)),
                     "p": p_rot, "delta": delta_rot, "pass": pass_rot},
        "perm_null": {"median": med_perm, "q95": float(np.quantile(d_perm, 0.95)),
                      "p": p_perm, "delta": delta_perm, "pass": pass_perm},
        "verdict": verdict,
    }


def frame_schedule(grams: np.ndarray) -> np.ndarray:
    """The bonus deliverable: per-direction diagonal value vs layer in the common
    frame (the 'switch schedule' - trains in Gram coordinates). Shape (m, K)."""
    gp, _ = dc_remove(grams)
    v, _, _ = joint_diagonalize(gp)
    return np.stack([np.diag(v.T @ gk @ v) for gk in gp], axis=1)  # (m, K)


# ---------------------------------------------------------------------------
# Planted worlds (synthetic gram sets -> REAL analyse path)
# ---------------------------------------------------------------------------
def _unit(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def _sym(m: np.ndarray) -> np.ndarray:
    return 0.5 * (m + m.T)


def planted_worlds(n: int = 9, k: int = 11):
    """Four synthetic gram sets; each a (K,n,n) stack + expected local verdict.

    DC = a shared all-positive high-energy mode (mimics the real route grams).
    """
    rng = np.random.default_rng(SEED)
    dc = _unit(np.abs(rng.standard_normal(n)) + 1.0)
    dc_mode = 4.0 * np.outer(dc, dc)
    worlds = {}

    # (1) COMMON-FRAME: shared DC + shared remainder frame -> STATIONARY
    v = random_orthogonal(n, rng)
    g = []
    for _ in range(k):
        lam = np.concatenate([[0.0], rng.standard_normal(n - 1)])
        g.append(_sym(dc_mode + v @ np.diag(lam) @ v.T))
    worlds["COMMON-FRAME"] = (np.stack(g), "STATIONARY")

    # (2) NO-FRAME: no shared DC, fully independent -> DRIFTING
    g = []
    for _ in range(k):
        r = random_orthogonal(n, rng)
        lam = rng.standard_normal(n) * np.linspace(3, 1, n)
        g.append(_sym(r @ np.diag(lam) @ r.T))
    worlds["NO-FRAME"] = (np.stack(g), "DRIFTING")

    # (3) DC-ONLY (critical guard): shared DC + INDEPENDENT remainder -> DRIFTING
    g = []
    for _ in range(k):
        r = random_orthogonal(n, rng)
        lam = np.concatenate([[0.0], rng.standard_normal(n - 1)])
        g.append(_sym(dc_mode + r @ np.diag(lam) @ r.T))
    worlds["DC-ONLY"] = (np.stack(g), "DRIFTING")

    # (4) PARTIAL: shared DC + shared frame on a 4-dim subspace only -> STATIONARY
    vp = random_orthogonal(n, rng)
    g = []
    for _ in range(k):
        r = random_orthogonal(n, rng)
        lam_shared = np.concatenate([[0.0], rng.standard_normal(3), np.zeros(n - 4)])
        lam_indep = np.concatenate([np.zeros(4), rng.standard_normal(n - 4)])
        shared = vp @ np.diag(lam_shared) @ vp.T
        indep = r @ np.diag(lam_indep) @ r.T
        g.append(_sym(dc_mode + shared + indep))
    worlds["PARTIAL"] = (np.stack(g), "STATIONARY")
    return worlds


def run_validate() -> int:
    log("[jd] --validate: planted worlds through the real analyse path")
    ok = True
    for name, (grams, expect) in planted_worlds().items():
        rng = np.random.default_rng(SEED)
        res = analyse_set(grams, rng)
        passed = res["verdict"] == expect
        ok = ok and passed
        log(f"[jd]   {name:13s} -> {res['verdict']:10s} (want {expect:10s}) "
            f"D={res['d_real']:.3f} rot_med={res['rot_null']['median']:.3f} "
            f"p_rot={res['rot_null']['p']:.3f} d={res['rot_null']['delta']:+.3f}  "
            f"{'OK' if passed else 'FAIL'}")
    log(f"[jd] validate {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# Real backend
# ---------------------------------------------------------------------------
def load_route_grams(path: Path) -> tuple[list[str], np.ndarray, np.ndarray]:
    """Return (layer_keys, route_grams (L,9,9), hidden_gram (9,9))."""
    d = np.load(path)
    keys = sorted(k for k in d.files if k.startswith("gram_route_cmr_L"))
    route = np.stack([d[k].astype(np.float64) for k in keys])
    hidden = d["gram_hidden_cmr"].astype(np.float64)
    return keys, route, hidden


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gram-dir", default="results/combinator-relationship-map")
    ap.add_argument("--out", default="results/p_joint_diag_s342/run")
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return run_validate()

    paths = sorted(
        p for p in glob.glob(f"{args.gram_dir}/*.npz")
        if "v15" not in Path(p).name
    )
    models = {}
    route_by_model: dict[str, np.ndarray] = {}
    layer_keys_by_model: dict[str, list[str]] = {}
    for p in paths:
        name = Path(p).stem
        keys, route, _ = load_route_grams(Path(p))
        route_by_model[name] = route
        layer_keys_by_model[name] = keys
        log(f"[jd] {name}: {route.shape[0]} layers, gram {route.shape[1]}x"
            f"{route.shape[2]}")

    # ---- JD-LAYER (primary): per model, JD its layer route grams -------------
    schedules = {}
    for name, route in route_by_model.items():
        rng = np.random.default_rng(SEED)
        res = analyse_set(route, rng)
        res["family"] = FAMILY.get(name, "other")
        res["n_layers"] = int(route.shape[0])
        models[name] = res
        if res["verdict"] == "STATIONARY":
            schedules[name] = frame_schedule(route)
        log(f"[jd] LAYER {name:32s} {res['verdict']:10s} D={res['d_real']:.3f} "
            f"rot p={res['rot_null']['p']:.3f} d={res['rot_null']['delta']:+.3f} | "
            f"perm p={res['perm_null']['p']:.3f}")

    n_models = len(models)
    n_pass = sum(m["verdict"] == "STATIONARY" for m in models.values())
    n_void = sum(m["verdict"] == "VOID" for m in models.values())
    frac_pass = n_pass / n_models if n_models else 0.0
    fam_pass = {}
    for m in models.values():
        fam_pass.setdefault(m["family"], []).append(m["verdict"] == "STATIONARY")
    fam_frac = {f: float(np.mean(v)) for f, v in fam_pass.items()}

    if n_void > n_models / 2:
        layer_verdict = "VOID"
    elif frac_pass >= FRAC_STATIONARY:
        layer_verdict = "LAYER-STATIONARY-FRAME"
    elif frac_pass <= FRAC_DRIFTING:
        layer_verdict = "LAYER-DRIFTING-FRAME"
    else:
        layer_verdict = "MIXED-FAMILY-SPLIT"

    # ---- JD-MODEL (secondary): across models at each matched fractional depth --
    n_idx = min(r.shape[0] for r in route_by_model.values())
    model_names = sorted(route_by_model)
    model_by_idx = {}
    for idx in range(n_idx):
        stack = np.stack([route_by_model[m][idx] for m in model_names])
        rng = np.random.default_rng(SEED)
        model_by_idx[idx] = analyse_set(stack, rng)
    idx_pass = [model_by_idx[i]["rot_null"]["pass"] for i in range(n_idx)]
    idx_void = sum(model_by_idx[i]["verdict"] == "VOID" for i in range(n_idx))
    frac_idx = float(np.mean(idx_pass)) if idx_pass else 0.0
    med_d_model = float(np.median([model_by_idx[i]["d_real"] for i in range(n_idx)]))

    if idx_void > n_idx / 2:
        model_verdict = "VOID"
    elif frac_idx > IDX_MAJORITY:
        model_verdict = "UNIVERSAL-FRAME"
    else:
        model_verdict = "SIGN-ONLY"

    # ---- write results -------------------------------------------------------
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    gram_hash = hashlib.sha256(
        json.dumps(sorted(route_by_model), sort_keys=True).encode()
    ).hexdigest()[:16]
    meta = {
        "probe": "P-JOINT-DIAG",
        "frozen": "s342 pre-data freeze (Michael GO): operator-geometry-la-"
                  "toolkit.md sec 4 #7 + gram-registers sec route-map",
        "pre_data": {
            "N_NULL": N_NULL, "N_PERM": N_PERM, "ALPHA": ALPHA, "FLOOR": FLOOR,
            "SEED": SEED, "FRAC_STATIONARY": FRAC_STATIONARY,
            "FRAC_DRIFTING": FRAC_DRIFTING, "IDX_MAJORITY": IDX_MAJORITY,
            "apriori_layer": APRIORI_LAYER, "apriori_model": APRIORI_MODEL,
        },
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "gram_dir": args.gram_dir, "n_models": n_models, "gram_hash": gram_hash,
        "git_sha": git_sha(),
        "jd_layer": {
            "verdict": layer_verdict, "n_pass": n_pass, "n_models": n_models,
            "n_void": n_void, "frac_pass": frac_pass, "family_frac": fam_frac,
            "per_model": models,
        },
        "jd_model": {
            "verdict": model_verdict, "n_idx": n_idx, "frac_idx_pass": frac_idx,
            "median_d": med_d_model, "model_names": model_names,
            "per_idx": {int(k): v for k, v in model_by_idx.items()},
        },
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=_json_native))
    if schedules:
        np.savez_compressed(
            out / "schedules.npz",
            **{k.replace("/", "_"): v for k, v in schedules.items()},
        )

    log(f"[jd] === JD-LAYER: {layer_verdict} (pass {n_pass}/{n_models}, "
        f"frac {frac_pass:.2f}) ===")
    for f, fr in sorted(fam_frac.items()):
        log(f"[jd]     family {f:10s} pass_frac={fr:.2f}")
    log(f"[jd] === JD-MODEL: {model_verdict} (idx pass {sum(idx_pass)}/{n_idx}, "
        f"median D={med_d_model:.3f}) ===")
    log(f"[jd] wrote {out}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
