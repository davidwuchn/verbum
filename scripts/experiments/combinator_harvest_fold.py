#!/usr/bin/env python3
# register: topological/routing
"""Combinator HARVEST FOLD — Phase 0 (CPU-only): the harvest PRESCRIPTION.

THE GOAL (consensus-delta-folding.md, s220 open-lead #1):
  Harvest the open-weight ecosystem's agreed combinator function shape into the
  v15 base plate. The pipeline (reverse-direction folding):
    measure per-model combinator Grams (routing register)  [DONE, s217-s220]
    cross-model CONSENSUS Gram + universal edges            [DONE, consensus.json]
    >>> PRESCRIPTION: which edges to reinforce, target Gram  [THIS SCRIPT, CPU]
    measure v15's OWN combinator Gram + centroids            [DEFERRED — GPU/MLX]
    Procrustes-align consensus -> v15 frame                  [DEFERRED — needs v15 Gram]
    WHNF-verify each fold direction (exp_b forward_metrics)   [DEFERRED — GPU/MLX]
    fold survivors + measure downstream PPL vs base           [DEFERRED — GPU/MLX]

WHY ONLY PHASE 0 HERE (the honest scope):
  The harvest as originally sketched ("Procrustes-align consensus centroids into
  v15 frame") is NOT runnable yet for two reasons the s220 mapping found:
   (1) DATA: the per-model 9-d_ff centroid VECTORS were computed but DISCARDED;
       only the relational 9x9 Gram persisted. (combinator_relationship_map.py is
       now patched to save centroids on future runs — but those runs are GPU.)
   (2) FRAME: v15 has NO combinator Gram/centroids yet, and the producing forward
       passes are GPU/MLX, which would CONTEND with the multi-day main:1 training
       (s219 GPU-contention stalled it). main:1 must stay UNTOUCHED.
  So this script lands the CPU-only PRESCRIPTION: from the cross-model consensus,
  the target combinator Gram restricted to the s220 HARVEST BAND (4B-14B, where the
  function shape is fully crystallized and saturated — see scale.json) and the
  ranked positive universal edges to reinforce. This is the spec the deferred GPU
  fold consumes. It manufactures NO numbers from forward passes — pure re-reduction
  of already-measured Grams.

THE HARVEST BAND (s220 finding):
  Skeleton binding rises 0.6B->4B then SATURATES; 32B regresses. So harvest from
  the 4B-14B dense band, not the frontier. Default band = Qwen3-4B/8B/14B.

Usage:
  uv run python scripts/experiments/combinator_harvest_fold.py
  uv run python scripts/experiments/combinator_harvest_fold.py --frac 0.30

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
MAP_DIR = _PROJECT_ROOT / "results" / "combinator-relationship-map"
CONS_DIR = _PROJECT_ROOT / "results" / "combinator-map-consensus"
OUT_DIR = _PROJECT_ROOT / "results" / "combinator-harvest-fold"

CRYSTAL = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]
# s220 harvest band: dense mid-scale where the shape is fully crystallized.
HARVEST_BAND = ["Qwen_Qwen3-4B", "Qwen_Qwen3-8B", "Qwen_Qwen3-14B"]


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=_PROJECT_ROOT,
            text=True).strip()
    except Exception:
        return "unknown"


def gram_at_frac(safe: str, frac: float) -> tuple[np.ndarray, float]:
    """Load a model's routing-CMR Gram at the layer nearest the target fraction."""
    j = json.loads((MAP_DIR / f"{safe}.json").read_text())
    nl = int(j["n_layers"])
    npz = np.load(MAP_DIR / f"{safe}.npz")
    grams = {
        int(k.split("L")[1]) / nl: np.asarray(npz[k], dtype=np.float64)
        for k in npz.keys() if k.startswith("gram_route_cmr_L")
    }
    f = min(grams, key=lambda x: abs(x - frac))
    return grams[f], f


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--frac", type=float, default=None,
                    help="depth fraction (default: consensus harvest_frac)")
    ap.add_argument("--band", nargs="+", default=HARVEST_BAND,
                    help="model files (without ext) forming the harvest band")
    args = ap.parse_args()

    cons = json.loads((CONS_DIR / "consensus.json").read_text())
    order = cons.get("crystal_order", CRYSTAL)
    idx = {c: i for i, c in enumerate(order)}
    models = cons["models"]
    frac = args.frac if args.frac is not None else float(cons["harvest_frac"])

    # band consensus Gram = mean of band models' Grams at the harvest fraction.
    band_grams, used_fracs = [], {}
    for safe in args.band:
        if not (MAP_DIR / f"{safe}.json").exists():
            print(f"  ! missing {safe}, skipping", file=sys.stderr)
            continue
        g, uf = gram_at_frac(safe, frac)
        band_grams.append(g)
        used_fracs[safe] = uf
    if not band_grams:
        print("no band models found", file=sys.stderr)
        sys.exit(1)
    band_gram = np.mean(band_grams, axis=0)

    # map consensus model names -> band membership for per-edge band consensus.
    band_pretty = {s.replace("Qwen_", "Qwen/").replace("_", "-") for s in args.band}
    band_model_idx = [i for i, m in enumerate(models)
                      if m.replace("/", "-") in {b.replace("/", "-")
                                                 for b in band_pretty}]

    # positive universal edges = the harvest targets (consensus > 0, universal).
    pos_edges = []
    for e in cons["universal_edges"]:
        if e["consensus"] <= 0 or not e.get("universal"):
            continue
        a, b = e["edge"].split("-")
        per = e.get("per_model", [])
        band_vals = [per[i] for i in band_model_idx if i < len(per)]
        band_cons = float(np.mean(band_vals)) if band_vals else float("nan")
        pos_edges.append({
            "edge": e["edge"],
            "a": a, "b": b,
            "consensus_all": round(float(e["consensus"]), 4),
            "consensus_band": round(band_cons, 4),
            "cross_model_std": round(float(e["cross_model_std"]), 4),
            "reliability_t": round(float(e["reliability_t"]), 3),
            "band_gram": round(float(band_gram[idx[a], idx[b]]), 4),
        })
    # rank by band consensus * reliability (strong AND agreed).
    pos_edges.sort(key=lambda x: -(x["consensus_band"] * x["reliability_t"]))

    print(f"\n  ══ HARVEST PRESCRIPTION (band={','.join(args.band)} frac~{frac}) ══")
    print(f"  {'edge':6} {'cons_all':>9} {'cons_band':>10} "
          f"{'rel_t':>7} {'band_gram':>10}")
    for e in pos_edges:
        print(f"  {e['edge']:6} {e['consensus_all']:+9.4f} "
              f"{e['consensus_band']:+10.4f} {e['reliability_t']:7.2f} "
              f"{e['band_gram']:+10.4f}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "prescription.json"
    out.write_text(json.dumps({
        "register": "topological/routing",
        "phase": "0 (CPU prescription; GPU fold deferred — main:1 untouched)",
        "git_sha": git_sha(),
        "source_consensus": "results/combinator-map-consensus/consensus.json",
        "harvest_band": args.band,
        "band_used_fracs": used_fracs,
        "target_frac": frac,
        "crystal_order": order,
        "band_consensus_gram": [[round(float(v), 4) for v in row]
                                for row in band_gram],
        "positive_universal_edges": pos_edges,
        "deferred_gpu_phases": [
            "measure v15 combinator Gram+centroids (combinator_relationship_map "
            "adapted for MLX/ternary; hook ffn_gate_plate_a/c)",
            "Procrustes-align consensus -> v15 frame (needs v15 Gram)",
            "WHNF-verify each fold direction via exp_b forward_metrics "
            "(accept iff dx_conv does not rise)",
            "fold survivors via DeltaTernaryLinear.reduce; measure PPL vs base",
        ],
        "deferral_reason": "all producing steps are GPU/MLX forward passes that "
                           "would contend with the multi-day main:1 training "
                           "(s219 GPU-contention stalled it); main:1 stays UNTOUCHED",
    }, indent=2))
    print(f"\n  wrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
