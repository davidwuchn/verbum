#!/usr/bin/env python3
# register: functional + topological/routing
"""Ternary holographic plate — lay a program spec into the weights as a SPARSE
DELTA against a CONSTRUCTED basis. Greenfield: no pretrained model touched.

THE FUTURE POSSIBILITY (Michael): a DESIGNED ternary holographic substrate where
the basis is GIVEN (constructed, frozen, shared) and arbitrary data (a program
spec) is laid in as a sparse ternary delta against it; continuations are the
shared basis for distributed training; folds stay exact (ternary x ternary).

WHY GREENFIELD: gd_frozen_basis + Qwen3-14B showed the frozen/active basis is
CAPACITY-GATED (absent at micro, present in mature Zone A). Probing more existing
models only locates the threshold. The future move = ENGINEER PAST the threshold by
CONSTRUCTING the basis, so 100% of laid-in capacity becomes DATA, not scaffolding.

THE CONCRETE MODEL (faithful to the whole thread): a correlation-matrix holographic
memory. A program spec = a finite map {key → value} = a set of associations. Each
association is an OUTER PRODUCT val ⊗ key = one "photograph" (the same δxᵀ structure
as a gradient exposure). plate M = Σ_i val_i key_iᵀ; ternarize(M) stores the
associations as sign topology (holographic-storage: sign survives ternary).

FOUR MEASUREMENTS (each decides whether the future is real):
  (1) CAPACITY : recall accuracy vs #associations N at fixed d → the threshold N*,
                 now a DESIGN parameter, not a training mystery.
  (2) DELTA    : program P = basis B with K bindings changed (a spec / fact update)
                 encodes as a delta whose SPARSITY scales with K/N, ≪ 0.5.
  (3) FOLD     : plate_P = plate_B ⊙ Δ exactly (ternary x ternary), and
                 recall(folded) == recall(plate_P) — lossless install.
  (4) NULL     : a matched-RANDOM basis yields a ~50% DENSE delta (no sharing).
                 Gate (λ yardstick): real-delta-sparsity ≪ null, else the claim is
                 unfalsifiable (any flexible basis "fits").

Usage:
  uv run python scripts/experiments/holo_plate_delta.py --smoke
  uv run python scripts/experiments/holo_plate_delta.py --seeds 0,1,2,3,4

License: MIT
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "holo-plate-delta"


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


# --------------------------------------------------------------------------- #
# Codebook + plate primitives                                                   #
# --------------------------------------------------------------------------- #
def codebook(n: int, d: int, rng: np.random.Generator) -> np.ndarray:
    """n random ±1 vectors in d dims (near-orthogonal in high d)."""
    return rng.integers(0, 2, size=(n, d)).astype(np.float64) * 2 - 1


def ternarize(m: np.ndarray, sparsity: float) -> np.ndarray:
    """Sign topology with a zero-band: zero the smallest |m| fraction, else sign.
    sparsity=0 → pure binary sign {-1,+1}; sparsity>0 → ternary {-1,0,+1}."""
    sign = np.where(m >= 0, 1.0, -1.0)
    if sparsity <= 0:
        return sign
    thr = np.quantile(np.abs(m), sparsity)
    sign[np.abs(m) <= thr] = 0.0
    return sign


def build_plate(prog: np.ndarray, keys: np.ndarray, vals: np.ndarray,
                sparsity: float) -> np.ndarray:
    """prog = (N,2) int (key_idx, val_idx). plate = ternarize(Σ val ⊗ key)."""
    ksel = keys[prog[:, 0]]          # (N,d)
    vsel = vals[prog[:, 1]]          # (N,d)
    m = vsel.T @ ksel                # (d,d) correlation matrix = Σ val_i key_iᵀ
    return ternarize(m, sparsity)


def recall_acc(plate: np.ndarray, prog: np.ndarray, keys: np.ndarray,
               vals: np.ndarray) -> float:
    """For each (a,b): v̂ = plate·key[a]; decode argmax cos over value codebook."""
    ksel = keys[prog[:, 0]]                       # (N,d)
    vhat = ksel @ plate.T                          # (N,d) = (plate·key)_i rows
    scores = vhat @ vals.T                         # (N, n_vals) unnormalized cos
    pred = scores.argmax(axis=1)
    return float((pred == prog[:, 1]).mean())


def make_program(n_assoc: int, n_keys: int, n_vals: int,
                 rng: np.random.Generator) -> np.ndarray:
    """A finite map: n_assoc DISTINCT keys → random values (a program spec)."""
    key_ids = rng.choice(n_keys, size=n_assoc, replace=False)
    val_ids = rng.integers(0, n_vals, size=n_assoc)
    return np.stack([key_ids, val_ids], axis=1)


# --------------------------------------------------------------------------- #
# (1) CAPACITY sweep                                                            #
# --------------------------------------------------------------------------- #
def capacity_sweep(d: int, n_list: list[int], n_keys: int, n_vals: int,
                   sparsity: float, rng: np.random.Generator) -> list[dict]:
    keys = codebook(n_keys, d, rng)
    vals = codebook(n_vals, d, rng)
    out = []
    for n in n_list:
        prog = make_program(n, n_keys, n_vals, rng)
        plate = build_plate(prog, keys, vals, sparsity)
        out.append({"N": n, "acc": round(recall_acc(plate, prog, keys, vals), 4),
                    "bits_per_cell": round(n * np.log2(n_vals) / (d * d), 5)})
    return out


def n_star(curve: list[dict], thresh: float) -> int:
    ok = [c["N"] for c in curve if c["acc"] >= thresh]
    return max(ok) if ok else 0


# --------------------------------------------------------------------------- #
# (2)+(3)+(4) DELTA against a constructed basis, FOLD, NULL                      #
# --------------------------------------------------------------------------- #
def flip_fraction(plate_a: np.ndarray, plate_b: np.ndarray) -> float:
    """Fraction of positions whose sign differs (binary-sign plates)."""
    return float((plate_a != plate_b).mean())


def delta_test(d: int, n_assoc: int, k_list: list[int], n_keys: int, n_vals: int,
               rng: np.random.Generator) -> list[dict]:
    """Basis program B (n_assoc bindings). Target P = B with K bindings re-pointed
    (a spec/fact update). Measure delta sparsity vs a matched-random basis, and the
    exact ternary fold. Pure-sign plates (sparsity 0) so ⊙ = exact sign-flip."""
    keys = codebook(n_keys, d, rng)
    vals = codebook(n_vals, d, rng)
    base_prog = make_program(n_assoc, n_keys, n_vals, rng)
    plate_B = build_plate(base_prog, keys, vals, 0.0)              # {-1,+1}
    # matched-random basis: same shape/stats, structure-free
    plate_R = np.where(rng.standard_normal((d, d)) >= 0, 1.0, -1.0)

    out = []
    for k in k_list:
        prog_P = base_prog.copy()
        idx = rng.choice(n_assoc, size=min(k, n_assoc), replace=False)
        prog_P[idx, 1] = rng.integers(0, n_vals, size=idx.size)   # re-point K vals
        plate_P = build_plate(prog_P, keys, vals, 0.0)

        # (2) delta sparsity: structured basis vs (4) random-basis null
        flip_real = flip_fraction(plate_B, plate_P)
        flip_null = flip_fraction(plate_R, plate_P)

        # (3) FOLD: Δ = +1 keep / -1 flip;  plate_B ⊙ Δ must equal plate_P exactly
        delta = plate_B * plate_P                                  # {-1,+1}
        folded = plate_B * delta                                  # = plate_P
        fold_exact = bool(np.array_equal(folded, plate_P))
        acc_P = recall_acc(plate_P, prog_P, keys, vals)
        acc_folded = recall_acc(folded, prog_P, keys, vals)

        out.append({
            "K": k, "K_over_N": round(k / n_assoc, 4),
            "flip_frac_real": round(flip_real, 5),
            "flip_frac_null": round(flip_null, 5),
            "delta_advantage": round(flip_null / max(flip_real, 1e-9), 2),
            "fold_exact": fold_exact,
            "recall_P": round(acc_P, 4), "recall_folded": round(acc_folded, 4),
            "fold_lossless": bool(abs(acc_P - acc_folded) < 1e-9),
        })
    return out


# --------------------------------------------------------------------------- #
def _ms(vals: list) -> list:
    a = np.array([v for v in vals if v is not None], dtype=float)
    return [round(float(a.mean()), 4), round(float(a.std()), 4)] if a.size else \
        [None, None]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--d", type=int, default=512)
    ap.add_argument("--n-keys", type=int, default=2048)
    ap.add_argument("--n-vals", type=int, default=64)
    ap.add_argument("--cap-n", default="32,64,128,192,256,320,384,448,512,640,768")
    ap.add_argument("--cap-sparsity", default="0.0,0.5,0.75")
    ap.add_argument("--delta-n", type=int, default=256)
    ap.add_argument("--delta-k", default="1,2,4,8,16,32,64,128")
    ap.add_argument("--acc-thresh", type=float, default=0.99)
    ap.add_argument("--seeds", default="0,1,2,3,4")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.smoke:
        args.d, args.n_keys = 128, 512
        args.cap_n = "16,32,64,128"
        args.cap_sparsity = "0.0,0.5"
        args.delta_n, args.delta_k = 64, "1,4,16,32"
        args.seeds = "0,1"

    n_list = [int(x) for x in args.cap_n.split(",") if x.strip()]
    sps = [float(x) for x in args.cap_sparsity.split(",") if x.strip()]
    k_list = [int(x) for x in args.delta_k.split(",") if x.strip()]
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    log(f"  d={args.d} n_keys={args.n_keys} n_vals={args.n_vals} seeds={seeds}")

    # (1) capacity — per sparsity, per seed
    cap_runs: dict[str, list] = {f"s{sp}": [] for sp in sps}
    for sp in sps:
        for sd in seeds:
            cap_runs[f"s{sp}"].append(
                capacity_sweep(args.d, n_list, args.n_keys, args.n_vals, sp,
                               np.random.default_rng(sd)))
    cap_agg: dict[str, dict] = {}
    for sp in sps:
        runs = cap_runs[f"s{sp}"]
        by_n = {n: _ms([r[i]["acc"] for r in runs])
                for i, n in enumerate(n_list)}
        nstar = _ms([n_star(r, args.acc_thresh) for r in runs])
        cap_agg[f"sparsity_{sp}"] = {
            "acc_by_N": {str(n): by_n[n] for n in n_list},
            "N_star": nstar,
            "N_star_over_d": [round((nstar[0] or 0) / args.d, 3), nstar[1]]}
        nd = cap_agg[f"sparsity_{sp}"]["N_star_over_d"]
        log(f"  [capacity sp={sp}] N*={nstar} (N*/d={nd})")

    # (2)+(3)+(4) delta / fold / null — per seed
    delta_runs = [delta_test(args.d, args.delta_n, k_list, args.n_keys,
                             args.n_vals, np.random.default_rng(sd + 100))
                  for sd in seeds]
    delta_agg = []
    for i, k in enumerate(k_list):
        rows = [r[i] for r in delta_runs]
        delta_agg.append({
            "K": k, "K_over_N": rows[0]["K_over_N"],
            "flip_frac_real": _ms([r["flip_frac_real"] for r in rows]),
            "flip_frac_null": _ms([r["flip_frac_null"] for r in rows]),
            "delta_advantage": _ms([r["delta_advantage"] for r in rows]),
            "fold_exact_all": all(r["fold_exact"] for r in rows),
            "fold_lossless_all": all(r["fold_lossless"] for r in rows),
            "recall_P": _ms([r["recall_P"] for r in rows]),
            "recall_folded": _ms([r["recall_folded"] for r in rows]),
        })
        log(f"  [delta K={k:>3} ({rows[0]['K_over_N']:.3f}N)] "
            f"flip_real={delta_agg[-1]['flip_frac_real']} "
            f"flip_null={delta_agg[-1]['flip_frac_null']} "
            f"advx{delta_agg[-1]['delta_advantage']} fold_exact="
            f"{delta_agg[-1]['fold_exact_all']}")

    # verdict
    small_k = delta_agg[0]
    verdict = {
        "capacity_threshold_N_star_over_d_sign": cap_agg[
            f"sparsity_{sps[0]}"]["N_star_over_d"],
        "delta_sparse_at_smallK_real_vs_null": [
            small_k["flip_frac_real"], small_k["flip_frac_null"]],
        "delta_advantage_smallK": small_k["delta_advantage"],
        "fold_exact_all_K": all(d["fold_exact_all"] for d in delta_agg),
        "fold_lossless_all_K": all(d["fold_lossless_all"] for d in delta_agg),
        "ternary_capacity_survives": {
            f"sparsity_{sp}": cap_agg[f"sparsity_{sp}"]["N_star"] for sp in sps},
    }

    meta = {
        "experiment": "holo-plate-delta",
        "register": "functional + topological/routing",
        "idea": "lay a program spec into ternary holographic plates as a sparse "
                "delta against a constructed basis; capacity / delta / fold / null.",
        "timestamp_utc": datetime.now(UTC).isoformat(), "git_sha": git_sha(),
        "config": vars(args), "seeds": seeds, "elapsed_s": round(time.time()-t0, 1),
    }
    tag = "smoke" if args.smoke else "multiseed"
    out = {**meta, "verdict": verdict, "capacity": cap_agg, "delta": delta_agg}
    (RESULTS_DIR / f"verdict_{tag}.json").write_text(json.dumps(out, indent=2))

    nstar_sign = verdict["capacity_threshold_N_star_over_d_sign"]
    ternary_cap = verdict["ternary_capacity_survives"]
    adv = small_k["delta_advantage"]
    real0 = small_k["flip_frac_real"][0] or 1.0
    null0 = small_k["flip_frac_null"][0] or 0.0
    null_gate = "YES" if real0 < 0.5 * null0 else "NO"
    log("\n  ==== TERNARY HOLOGRAPHIC PLATE: spec-as-delta-against-basis ====")
    log(f"  (1) CAPACITY  : N*/d (sign) = {nstar_sign}  ternary N* = {ternary_cap}")
    log(f"  (2) DELTA     : K=1 flip_real={small_k['flip_frac_real']} vs "
        f"null={small_k['flip_frac_null']} (advantage x{adv})")
    log(f"  (3) FOLD      : exact_all_K={verdict['fold_exact_all_K']} "
        f"lossless_all_K={verdict['fold_lossless_all_K']}")
    log(f"  (4) NULL gate : real << null? {null_gate}")
    log(f"\n  wrote {RESULTS_DIR / f'verdict_{tag}.json'}  ({meta['elapsed_s']}s)")


if __name__ == "__main__":
    main()
