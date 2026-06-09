#!/usr/bin/env python3
# register: spectral
"""Aggregate svd_phi_null.py per-model JSONs into the audit #6 verdict table.

Reads results/svd-phi-null/*.json and prints, for the RAW object (matches the
session-137 definition: SVD of H, no centering), per model:
  head_ratio (model)  vs  MP-null  vs  shuffled-null   [the 0.6299 number + nulls]
  geometric-win layers / total                          [is it constant/geometric?]
  geom_r2 vs power_r2                                    [shape: φ needs geometric]
  layers within ±0.05 of 1/φ (model vs MP)              [φ-specific or null too?]
"""
import json
import math
from pathlib import Path

PHI_INV = 1 / ((1 + math.sqrt(5)) / 2)
RES = Path(__file__).resolve().parent.parent.parent / "results" / "svd-phi-null"

ORDER = [
    "EleutherAI_pythia-160m-deduped",
    "EleutherAI_pythia-410m-deduped",
    "Qwen_Qwen3-0.6B",
    "HuggingFaceTB_SmolLM3-3B",
    "mistralai_Mistral-7B-v0.3",
]


def g(d, *ks, default=None):
    for k in ks:
        d = d.get(k) if isinstance(d, dict) else None
        if d is None:
            return default
    return d


def main():
    files = {p.stem: p for p in RES.glob("*.json")}
    print(f"1/φ target = {PHI_INV:.4f}\n")
    hdr = (f"{'model':28s} {'obj':4s} | {'model':>7s} {'MP':>7s} {'shuf':>7s} "
           f"| {'geomWin':>9s} {'gR2':>5s} {'pR2':>5s} | {'φ±.05 m/MP':>11s}")
    print(hdr)
    print("-" * len(hdr))
    rows = []
    for name in ORDER + [k for k in files if k not in ORDER]:
        if name not in files:
            continue
        d = json.load(open(files[name]))
        for obj in ("raw", "centered"):
            o = g(d, "object_results", obj)
            if not o:
                continue
            m, mp, sh = o["model"], o["mp"], o["shuffled"]
            nL = m["n_layers"]
            line = (f"{name[:28]:28s} {obj:4s} | "
                    f"{m['core_mean_over_layers']:7.4f} {mp['core_mean_over_layers']:7.4f} "
                    f"{sh['core_mean_over_layers']:7.4f} | "
                    f"{m['geometric_win_layers']:3d}/{nL:<3d}    "
                    f"{m['geom_r2_mean']:.2f}  {m['power_r2_mean']:.2f} | "
                    f"{m['layers_within_0.05_of_phi']:3d}/{nL:<3d} "
                    f"{mp['layers_within_0.05_of_phi']:2d}/{nL:<3d}")
            print(line)
            if obj == "raw":
                rows.append((name, m, mp, sh, nL))
    # consensus on the raw head ratio (the 0.6299 reproduction)
    print()
    vals = [r[1]["core_mean_over_layers"] for r in rows]
    mpvals = [r[2]["core_mean_over_layers"] for r in rows]
    if vals:
        import statistics as st
        print(f"RAW head-ratio grand mean (model): {st.mean(vals):.4f} "
              f"± {st.pstdev(vals):.4f}   (page: 0.6299 ± 0.019)")
        print(f"RAW head-ratio grand mean (MP null): {st.mean(mpvals):.4f} "
              f"± {st.pstdev(mpvals):.4f}")
        tot_geom = sum(r[1]["geometric_win_layers"] for r in rows)
        tot_L = sum(r[4] for r in rows)
        print(f"Geometric-wins (model, raw): {tot_geom}/{tot_L} layers "
              f"→ power-law wins {tot_L - tot_geom}/{tot_L}")
        tot_phi_m = sum(r[1]["layers_within_0.05_of_phi"] for r in rows)
        tot_phi_mp = sum(r[2]["layers_within_0.05_of_phi"] for r in rows)
        print(f"Layers within ±0.05 of 1/φ: model {tot_phi_m}/{tot_L}  "
              f"MP {tot_phi_mp}/{tot_L}")


if __name__ == "__main__":
    main()
