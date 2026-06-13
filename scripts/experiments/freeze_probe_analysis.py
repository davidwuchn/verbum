#!/usr/bin/env python3
"""Frozen-topology probe analysis (session 222, register: functional).

Tests Michael's hypothesis: GD will never *not* want superpositions. With the
ternary sign topology FROZEN, does GD re-express the superposition demand in the
continuous magnitude domain (gamma) at exactly the positions that oscillated
under TernaryDescent?

Pipeline
--------
1. Build per-output-row "oscillation score" from a TD flip map
   (positions with flip_count >= MULTI summed over the input axis).
   Oscillator rows = top decile; settled rows = zero-flip rows.
2. Snapshot gamma (per-output-row scale, Adam-trained) at oscillator vs
   settled rows from a BEFORE checkpoint (step_001000).
3. If an AFTER checkpoint is given (the frozen-topology probe end), compare:
   did gamma at oscillator rows drive to node/antinode (bimodality), grow in
   |magnitude|, or flip sign — i.e. superposition re-expressed in magnitude?

Verdict reads (falsifiable)
---------------------------
- contractivity: read separately from the training log (Δx, CE).
- gamma-bimodality: oscillator rows should show larger |Δgamma|, more sign
  flips, and a more bimodal |gamma| distribution than settled rows IF GD is
  rebuilding superposition in the soft topology.

Usage
-----
  # baseline snapshot (before the probe runs)
  freeze_probe_analysis.py --flip-map FLIP.npz --before BEFORE/model.npz
  # full comparison (after the probe ends)
  freeze_probe_analysis.py --flip-map FLIP.npz \
      --before BEFORE/model.npz --after AFTER/model.npz
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

MULTI = 2  # flip_count >= MULTI counts as an oscillating position
TOP_FRAC = 0.10  # oscillator rows = top decile by oscillation score


def _unpack_count_keys(flip_map: dict) -> dict[str, np.ndarray]:
    """Return {module_path: flip_count (out,in)} for every */flip_count key."""
    out = {}
    for k in flip_map.files:
        if k.endswith("/flip_count"):
            mod = k[: -len("/flip_count")]
            out[mod] = np.asarray(flip_map[k])
    return out


def _gamma_key(module_path: str) -> str:
    """flip-map module path -> model.npz gamma key."""
    return f"{module_path}.gamma"


def bimodality(x: np.ndarray) -> float:
    """Sarle's bimodality coefficient: (skew^2 + 1) / kurtosis.

    > 0.555 (uniform) suggests bimodal/multimodal; higher = more split.
    Operates on |gamma| to detect a node/antinode (two-cluster) split.
    """
    x = np.asarray(x, dtype=np.float64)
    n = x.size
    if n < 4:
        return float("nan")
    m = x.mean()
    s = x.std()
    if s == 0:
        return float("nan")
    z = (x - m) / s
    skew = (z**3).mean()
    kurt = (z**4).mean()  # non-excess
    g1 = skew
    g2 = kurt - 3.0
    denom = g2 + 3.0 * ((n - 1) ** 2) / ((n - 2) * (n - 3))
    if denom == 0:
        return float("nan")
    return float((g1**2 + 1.0) / denom)


def row_stats(g: np.ndarray) -> dict:
    a = np.abs(g)
    return {
        "n": int(g.size),
        "gamma_mean": float(g.mean()),
        "gamma_std": float(g.std()),
        "absmean": float(a.mean()),
        "absmax": float(a.max()),
        "frac_negative": float((g < 0).mean()),
        "frac_near_zero": float((a < 1e-4).mean()),
        "bimodality_abs": bimodality(a),
    }


def analyze(flip_map_path: str, before_path: str, after_path: str | None) -> dict:
    fm = np.load(flip_map_path)
    counts = _unpack_count_keys(fm)
    before = np.load(before_path)
    after = np.load(after_path) if after_path else None

    per_module = {}
    agg = {"osc": [], "settled": []}
    agg_after = {"osc": [], "settled": []}
    dgamma = {"osc": [], "settled": []}
    signflip = {"osc": [], "settled": []}

    for mod, fc in sorted(counts.items()):
        gk = _gamma_key(mod)
        if gk not in before.files:
            continue
        g_before = np.asarray(before[gk]).reshape(-1)
        n_out = g_before.shape[0]
        if fc.shape[0] != n_out:
            # flip_count out-axis must match gamma rows
            continue

        # per-row oscillation score = # multi-flip positions in the row
        osc_score = (fc >= MULTI).sum(axis=1).astype(np.int64)
        ever = (fc >= 1).sum(axis=1).astype(np.int64)

        n_top = max(1, round(TOP_FRAC * n_out))
        order = np.argsort(-osc_score)
        osc_rows = order[:n_top]
        osc_rows = osc_rows[osc_score[osc_rows] > 0]  # require real oscillation
        settled_rows = np.where(ever == 0)[0]

        entry = {
            "n_out": int(n_out),
            "n_osc_rows": int(osc_rows.size),
            "n_settled_rows": int(settled_rows.size),
            "max_osc_score": int(osc_score.max()),
            "before_osc": row_stats(g_before[osc_rows]) if osc_rows.size else None,
            "before_settled": (
                row_stats(g_before[settled_rows]) if settled_rows.size else None
            ),
        }
        if osc_rows.size:
            agg["osc"].append(g_before[osc_rows])
        if settled_rows.size:
            agg["settled"].append(g_before[settled_rows])

        if after is not None and gk in after.files:
            g_after = np.asarray(after[gk]).reshape(-1)
            if g_after.shape[0] == n_out:
                entry["after_osc"] = (
                    row_stats(g_after[osc_rows]) if osc_rows.size else None
                )
                entry["after_settled"] = (
                    row_stats(g_after[settled_rows]) if settled_rows.size else None
                )
                if osc_rows.size:
                    d = g_after[osc_rows] - g_before[osc_rows]
                    dgamma["osc"].append(np.abs(d))
                    signflip["osc"].append(
                        np.sign(g_after[osc_rows]) != np.sign(g_before[osc_rows])
                    )
                    agg_after["osc"].append(g_after[osc_rows])
                if settled_rows.size:
                    d = g_after[settled_rows] - g_before[settled_rows]
                    dgamma["settled"].append(np.abs(d))
                    signflip["settled"].append(
                        np.sign(g_after[settled_rows])
                        != np.sign(g_before[settled_rows])
                    )
                    agg_after["settled"].append(g_after[settled_rows])

        per_module[mod] = entry

    def _cat(d, key):
        return np.concatenate(d[key]) if d[key] else np.array([])

    summary = {
        "config": {"MULTI": MULTI, "TOP_FRAC": TOP_FRAC},
        "n_modules": len(per_module),
        "before": {
            "osc": row_stats(_cat(agg, "osc")) if agg["osc"] else None,
            "settled": row_stats(_cat(agg, "settled")) if agg["settled"] else None,
        },
    }
    if after is not None:
        o_d, s_d = _cat(dgamma, "osc"), _cat(dgamma, "settled")
        o_sf, s_sf = _cat(signflip, "osc"), _cat(signflip, "settled")
        summary["after"] = {
            "osc": row_stats(_cat(agg_after, "osc")) if agg_after["osc"] else None,
            "settled": (
                row_stats(_cat(agg_after, "settled"))
                if agg_after["settled"]
                else None
            ),
        }
        summary["delta"] = {
            "osc_abs_dgamma_mean": float(o_d.mean()) if o_d.size else None,
            "settled_abs_dgamma_mean": float(s_d.mean()) if s_d.size else None,
            "osc_signflip_frac": float(o_sf.mean()) if o_sf.size else None,
            "settled_signflip_frac": float(s_sf.mean()) if s_sf.size else None,
            "osc_over_settled_dgamma_ratio": (
                float(o_d.mean() / s_d.mean())
                if (o_d.size and s_d.size and s_d.mean() > 0)
                else None
            ),
        }
    return {"summary": summary, "per_module": per_module}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flip-map", required=True)
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", default=None)
    ap.add_argument(
        "--out", default="results/freeze-probe/gamma_analysis.json"
    )
    args = ap.parse_args()

    res = analyze(args.flip_map, args.before, args.after)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2))

    s = res["summary"]
    print(f"modules analyzed: {s['n_modules']}")
    b = s["before"]
    if b["osc"] and b["settled"]:
        print("\nBEFORE (step_001000) gamma at rows:")
        print(
            f"  oscillator: |g|mean={b['osc']['absmean']:.5f} "
            f"|g|max={b['osc']['absmax']:.5f} "
            f"neg={b['osc']['frac_negative']:.3f} "
            f"bimod={b['osc']['bimodality_abs']:.3f} n={b['osc']['n']}"
        )
        print(
            f"  settled:    |g|mean={b['settled']['absmean']:.5f} "
            f"|g|max={b['settled']['absmax']:.5f} "
            f"neg={b['settled']['frac_negative']:.3f} "
            f"bimod={b['settled']['bimodality_abs']:.3f} n={b['settled']['n']}"
        )
    if "delta" in s:
        d = s["delta"]
        print("\nAFTER vs BEFORE (frozen-topology probe):")
        print(f"  |Δγ| oscillator: {d['osc_abs_dgamma_mean']}")
        print(f"  |Δγ| settled:    {d['settled_abs_dgamma_mean']}")
        print(f"  |Δγ| ratio (osc/settled): {d['osc_over_settled_dgamma_ratio']}")
        print(f"  sign-flip frac oscillator: {d['osc_signflip_frac']}")
        print(f"  sign-flip frac settled:    {d['settled_signflip_frac']}")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
