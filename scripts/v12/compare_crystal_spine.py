"""Cross-model crystal-spine comparison.

Read-only post-processor over ``lattice/crystal_spine/*.json``. Builds a
comparison table of the variance bottleneck across every model measured and
flags whether a given model (e.g. gemma-4-31b) is sharper / cleaner than the
rest of the sweep ("too precise") or in-band.

λ measure discipline: a sharper bottleneck is a routing/spectral claim. We
report the raw quantities (bottleneck depth, top-3 variance, spine dominant-dim
fraction, n90) and a z-score of each model vs the cohort — we do NOT assert
"discovered" from a clean fit alone (describability != discovery).

Usage:
    uv run python scripts/v12/compare_crystal_spine.py
    uv run python scripts/v12/compare_crystal_spine.py --highlight gemma-4-31b
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def _layer(model_result: dict, li: int) -> dict:
    layers = model_result["layers"]
    return layers[str(li)] if str(li) in layers else layers[li]


def load_models(spine_dir: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    combined = spine_dir / "all_results.json"
    if combined.exists():
        out.update(json.load(open(combined)))
    # Per-model files take precedence (freshest single-model runs).
    for p in sorted(spine_dir.glob("*.json")):
        if p.name in {"all_results.json", "probes.json"}:
            continue
        d = json.load(open(p))
        if isinstance(d, dict) and "bottleneck_layer" in d:
            out[d.get("model", p.stem)] = d
    return out


def row(model_key: str, r: dict) -> dict:
    bl = r["bottleneck_layer"]
    bld = _layer(r, bl)
    return {
        "model": model_key,
        "n_layers": r["n_layers"],
        "d_model": r["d_model"],
        "bl": bl,
        "depth": r["bottleneck_depth"],
        "top3": bld["top3_var_pct"],
        "pc1": bld["pc1_var_pct"],
        "spine_dim": bld["pc1_dominant_dim"],
        "spine_frac": bld["pc1_dominant_frac"],
        "n90": bld["pc1_dims_for_90pct"],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Compare crystal spine across models")
    ap.add_argument("--dir", default="lattice/crystal_spine")
    ap.add_argument("--highlight", default="gemma-4-31b",
                    help="Model to z-score against the rest of the cohort")
    args = ap.parse_args()

    models = load_models(Path(args.dir))
    if not models:
        print("No model results found.")
        return

    rows = [row(k, v) for k, v in models.items()]
    rows.sort(key=lambda x: x["depth"])

    print(f"\n{'='*108}")
    print("  CRYSTAL-SPINE CROSS-MODEL COMPARISON")
    print(f"{'='*108}")
    hdr = (f"  {'model':<14} | {'L':>3} | {'d_model':>7} | {'bl':>3} | "
           f"{'depth':>5} | {'top3%':>6} | {'pc1%':>6} | {'spineDim':>8} | "
           f"{'spineFrac':>9} | {'n90':>4}")
    print(hdr)
    print(f"  {'-'*104}")
    for x in rows:
        mark = "  ◀" if x["model"] == args.highlight else ""
        print(f"  {x['model']:<14} | {x['n_layers']:3d} | {x['d_model']:7d} | "
              f"{x['bl']:3d} | {x['depth']*100:4.0f}% | {x['top3']:5.1f}% | "
              f"{x['pc1']:5.1f}% | {x['spine_dim']:8d} | {x['spine_frac']*100:8.1f}% | "
              f"{x['n90']:4d}{mark}")

    # z-score the highlighted model vs the rest of the cohort on each metric.
    hi = next((x for x in rows if x["model"] == args.highlight), None)
    if hi is None:
        print(f"\n  (highlight '{args.highlight}' not present yet)")
        return
    rest = [x for x in rows if x["model"] != args.highlight]
    if len(rest) < 2:
        print("\n  (need >=2 other models to z-score)")
        return

    print(f"\n  {args.highlight} vs cohort (z = (model - mean_rest) / std_rest):")
    for metric, label in [("depth", "bottleneck depth"),
                          ("top3", "top-3 variance %"),
                          ("spine_frac", "spine dominant frac"),
                          ("n90", "n90 (PC1 spread)")]:
        vals = np.array([x[metric] for x in rest], dtype=float)
        mu, sd = vals.mean(), vals.std()
        z = (hi[metric] - mu) / sd if sd > 0 else float("nan")
        print(f"    {label:<22}: {hi[metric]:8.3f}  "
              f"cohort {mu:7.3f}+-{sd:6.3f}  z={z:+.2f}")
    print("\n  NOTE (lambda measure): high top-3 / spine-frac z = a sharper")
    print("  bottleneck, NOT proof of discovered structure. A low-rank collapse on a")
    print("  diverse prose probe set is a property many decoders share; the honest")
    print("  test of 'too precise' is a matched-range / shuffled-probe null, not the")
    print("  raw sharpness alone.")


if __name__ == "__main__":
    main()
