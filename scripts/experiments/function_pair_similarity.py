#!/usr/bin/env python3
# register: topological/routing
"""Function-pair similarity — is `reduce` ≡ `fold`, and is `map` a fold?

THE QUESTION (session 225, Michael): map CAN be expressed as a fold
(map f = foldr (λx acc. f x : acc) []); fold is the universal catamorphism.
Does the model represent these relationships?

  PREDICTION 1 (synonym):    reduce ≈ fold        — same algebra, different word
                             ⇒ topology tracks FUNCTION not WORD.
  PREDICTION 2 (special-case): map ≉ fold          — same recursion scheme but a
                             DIFFERENT algebra/result-type. The separating axis is
                             WHNF (terminal/collapse): fold/reduce COLLAPSE to a
                             value (WHNF↑); map PRESERVES structure (WHNF↓).

THE INSTRUMENT (this script): reads the per-model fingerprints written by
function_topology_consensus.py (each function's cosine to the 9 combinators) and
computes the cross-FUNCTION similarity (cosine between fingerprint vectors),
aggregated across models. Reports each function's nearest function neighbour, the
reduce↔fold and map↔fold pairs, and the WHNF (collapse) loading per function.

Usage:
  uv run python scripts/experiments/function_pair_similarity.py

License: MIT
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "function-topology-consensus"


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


def unit(v):
    return v / (np.linalg.norm(v) + 1e-30)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="ffn_gate",
                    choices=["ffn_gate", "attn_q", "attn_out"])
    args = ap.parse_args()
    in_dir = RESULTS_DIR if args.target == "ffn_gate" else RESULTS_DIR / args.target
    files = sorted(f for f in in_dir.glob("*.json")
                   if f.stem not in ("consensus", "function_pairs"))
    if not files:
        log(f"no per-model jsons in {in_dir}")
        sys.exit(1)
    models = [json.loads(f.read_text()) for f in files]
    crystal = models[0]["crystal_order"]
    funcs = models[0]["functions"]
    log(f"function-pair similarity over {len(models)} models: "
        f"{[m['model'] for m in models]}")

    # per-model function-by-function cosine of fingerprint vectors, then average
    n = len(funcs)
    acc = np.zeros((len(models), n, n))
    whnf_idx = crystal.index("WHNF")
    whnf_load = {f: [] for f in funcs}
    for mi, m in enumerate(models):
        fp = {f: np.array([m["fingerprints"][f][c] for c in crystal]) for f in funcs}
        for f in funcs:
            whnf_load[f].append(float(fp[f][whnf_idx]))
        U = {f: unit(fp[f]) for f in funcs}
        for i, a in enumerate(funcs):
            for j, b in enumerate(funcs):
                acc[mi, i, j] = float(np.dot(U[a], U[b]))
    M = acc.mean(axis=0)
    Msd = acc.std(axis=0)

    # nearest function neighbour for each function (off-diagonal max)
    nearest = {}
    for i, a in enumerate(funcs):
        row = [(funcs[j], float(M[i, j])) for j in range(n) if j != i]
        row.sort(key=lambda x: -x[1])
        nearest[a] = row[:3]

    def pair(a, b):
        i, j = funcs.index(a), funcs.index(b)
        return round(float(M[i, j]), 4), round(float(Msd[i, j]), 4)

    out = {
        "models": [m["model"] for m in models], "n_models": len(models),
        "functions": funcs, "crystal_order": crystal,
        "function_cosine_mean": {a: {b: round(float(M[i, j]), 4)
                                     for j, b in enumerate(funcs)}
                                 for i, a in enumerate(funcs)},
        "nearest_function": nearest,
        "whnf_collapse_loading": {f: round(float(np.mean(whnf_load[f])), 4)
                                  for f in funcs},
        "git_sha": git_sha(),
    }
    # the two predictions
    preds = {}
    if "reduce" in funcs and "fold" in funcs:
        rc, rsd = pair("reduce", "fold")
        preds["reduce_vs_fold"] = {"cosine": rc, "std": rsd,
                                   "reduce_nearest": nearest["reduce"][0]}
    if "map" in funcs and "fold" in funcs:
        mc, msd = pair("map", "fold")
        preds["map_vs_fold"] = {"cosine": mc, "std": msd,
                                "map_nearest": nearest["map"][0]}
    out["predictions"] = preds
    (RESULTS_DIR / "function_pairs.json").write_text(json.dumps(out, indent=2))

    # ---- readable ----
    log("")
    log("  === FUNCTION-PAIR SIMILARITY (cosine of combinator fingerprints) ===")
    log(f"  {len(models)} models")
    log("")
    header = "          " + " ".join(f"{f[:6]:>6}" for f in funcs)
    log(header)
    for i, a in enumerate(funcs):
        row = " ".join(f"{M[i, j]:+.2f}".rjust(6) for j in range(n))
        log(f"  {a:>8} {row}")
    log("")
    log("  nearest function neighbour:")
    for f in funcs:
        ns = ", ".join(f"{x}({s:+.2f})" for x, s in nearest[f])
        log(f"    {f:>8} -> {ns}")
    log("")
    log("  WHNF (collapse / terminal) loading — high = collapses to a value:")
    for f in sorted(funcs, key=lambda f: -out["whnf_collapse_loading"][f]):
        log(f"    {f:>8} {out['whnf_collapse_loading'][f]:+.3f}")
    log("")
    if "reduce_vs_fold" in preds:
        p = preds["reduce_vs_fold"]
        nn = p["reduce_nearest"]
        log(f"  PRED 1 (reduce≈fold): cosine {p['cosine']:+.3f} (±{p['std']:.3f}); "
            f"reduce nearest = {nn[0]} ({nn[1]:+.2f})")
    if "map_vs_fold" in preds:
        p = preds["map_vs_fold"]
        nn = p["map_nearest"]
        log(f"  PRED 2 (map≉fold):   cosine {p['cosine']:+.3f} (±{p['std']:.3f}); "
            f"map nearest = {nn[0]} ({nn[1]:+.2f})")
    log("")
    log("  wrote function_pairs.json")


if __name__ == "__main__":
    main()
