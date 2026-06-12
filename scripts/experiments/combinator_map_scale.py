#!/usr/bin/env python3
# register: topological/routing
"""Combinator-map SCALE stratification — does the function shape sharpen with scale?

THE QUESTION (session 217, Michael; tested s220):
  s217 called "14B has capacity to FULLY form the systems; 0.6B only partially
  crystallizes." The combinator-map CONSENSUS (combinator_map_consensus.py) pools
  ALL models and finds the forced SKELETON (composition+selection) binds above a
  random-triple null while RECURSION does not. But the POOL cannot answer the
  SCALE question: does the skeleton/recursion gap WIDEN as models get bigger?

  This script stratifies the clean DENSE Qwen series (0.6B -> 4B -> 8B -> 14B ->
  32B) and regresses each family's INTRA-family routing-cosine binding against
  log(params). MoE models (30B-A3B, 235B) are excluded: their router+expert FFN
  is not comparable to dense gate_proj in this routing register.

THE INSTRUMENT (gradient-free, NO GPU — reads saved per-model Grams):
  inputs : results/combinator-relationship-map/Qwen_Qwen3-<size>.{json,npz}
  metric : per family, the mean off-diagonal routing-cosine among its members,
           read from each model's 9x9 combinator Gram at the harvest depth
           fraction (default 0.40, the consensus max-agreement fraction).
             composition = {B, D, S}
             selection   = {K, I, C}
             recursion   = {Y, W, WHNF}
             skeleton    = mean(composition, selection)
             gap         = skeleton - recursion
  fit    : Pearson r and slope-per-e-fold of each metric vs log(params).
  output : results/combinator-map-consensus/scale.json + stdout table.

Usage:
  uv run python scripts/experiments/combinator_map_scale.py
  uv run python scripts/experiments/combinator_map_scale.py --frac 0.30

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
IN_DIR = _PROJECT_ROOT / "results" / "combinator-relationship-map"
OUT_DIR = _PROJECT_ROOT / "results" / "combinator-map-consensus"

COMP = ["B", "D", "S"]
SEL = ["K", "I", "C"]
REC = ["Y", "W", "WHNF"]
CRYSTAL = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]

# clean dense Qwen3 scale series (params in billions). MoE excluded.
SERIES = [
    ("Qwen_Qwen3-0.6B", 0.6),
    ("Qwen_Qwen3-4B", 4.0),
    ("Qwen_Qwen3-8B", 8.0),
    ("Qwen_Qwen3-14B", 14.0),
    ("Qwen_Qwen3-32B", 32.0),
]


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=_PROJECT_ROOT,
            text=True).strip()
    except Exception:
        return "unknown"


def load_gram_at_frac(safe: str, frac: float):
    """Return (gram9x9, crystal_order, chosen_frac, n_layers)."""
    j = json.loads((IN_DIR / f"{safe}.json").read_text())
    nl = int(j["n_layers"])
    order = j.get("crystal_order", CRYSTAL)
    npz = np.load(IN_DIR / f"{safe}.npz")
    grams = {}
    for k in npz.keys():
        if k.startswith("gram_route_cmr_L"):
            li = int(k.split("L")[1])
            grams[li / nl] = np.asarray(npz[k], dtype=np.float64)
    f = min(grams, key=lambda x: abs(x - frac))
    return grams[f], order, f, nl


def intra_family(gram: np.ndarray, order: list[str], fam: list[str]) -> float:
    """Mean off-diagonal routing-cosine among family members (per-model order)."""
    idx = {c: i for i, c in enumerate(order)}
    vals = [
        gram[idx[a], idx[b]]
        for n, a in enumerate(fam)
        for b in fam[n + 1:]
    ]
    return float(np.mean(vals))


def fit(logp: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    r = float(np.corrcoef(logp, y)[0, 1])
    slope = float(np.polyfit(logp, y, 1)[0])
    return r, slope


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--frac", type=float, default=0.40,
                    help="depth fraction (default 0.40 = consensus harvest frac)")
    args = ap.parse_args()

    rows = []
    print(f"{'model':16} {'params':>6} {'comp':>7} {'sel':>7} "
          f"{'skel':>7} {'rec':>7} {'gap':>7} {'frac':>5}")
    for safe, p in SERIES:
        if not (IN_DIR / f"{safe}.json").exists():
            print(f"  ! missing {safe}, skipping", file=sys.stderr)
            continue
        gram, order, used_frac, nl = load_gram_at_frac(safe, args.frac)
        comp = intra_family(gram, order, COMP)
        sel = intra_family(gram, order, SEL)
        rec = intra_family(gram, order, REC)
        skel = (comp + sel) / 2.0
        gap = skel - rec
        rows.append({
            "model": safe.replace("Qwen_", ""), "params_b": p,
            "log_params": float(np.log(p)),
            "composition_BDS": comp, "selection_KIC": sel,
            "recursion_YWWHNF": rec, "skeleton": skel, "gap": gap,
            "used_frac": used_frac, "n_layers": nl,
        })
        print(f"{safe.replace('Qwen_',''):16} {p:6} {comp:+7.3f} {sel:+7.3f} "
              f"{skel:+7.3f} {rec:+7.3f} {gap:+7.3f} {used_frac:5.2f}")

    logp = np.array([r["log_params"] for r in rows])
    fits = {}
    print()
    for key, lab in [("skeleton", "skeleton"),
                     ("recursion_YWWHNF", "recursion"),
                     ("gap", "gap skel-rec")]:
        y = np.array([r[key] for r in rows])
        r, slope = fit(logp, y)
        fits[key] = {"r": r, "slope_per_efold": slope}
        print(f"{lab:14} vs log(params): r={r:+.3f} slope={slope:+.4f}/e-fold")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "scale.json"
    out.write_text(json.dumps({
        "register": "topological/routing",
        "question": "does the combinator function shape sharpen with scale?",
        "series": "dense Qwen3 0.6B->32B (MoE excluded)",
        "frac": args.frac,
        "git_sha": git_sha(),
        "per_model": rows,
        "fits_vs_log_params": fits,
    }, indent=2))
    print(f"\n  wrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
