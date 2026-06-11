# register: functional
"""Compare TernaryDescent acceptance rules: gradient-proxy vs exact-ΔL.

Reads the train_td_log.jsonl from two matched v15 runs (identical seeded init,
differing ONLY in --td-acceptance) and reports the session-213 findings as they
manifest in real TD training:

  1. Loss trajectory + final avg50/CE (does exact help the task loss?).
  2. Flip budget parity (both should fill ~the same etch budget).
  3. Curvature-veto rate (exact only): how many proxy flips the curvature term
     rejects (the overshooting flips the proxy would make).
  4. FlipMap oscillation fraction (the TD analogue of session-213 finding #2:
     "the proxy is non-monotone / flip-flops"). Lower osc ⇒ more monotone etch.

Usage:
  uv run python scripts/experiments/compare_td_acceptance.py \
      --proxy checkpoints/v15-td-ab-proxy \
      --exact checkpoints/v15-td-ab-exact \
      --out   results/ternary-exact-td-ab

License: MIT.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean


def load_log(run_dir: Path) -> list[dict]:
    path = run_dir / "train_td_log.jsonl"
    if not path.exists():
        raise FileNotFoundError(path)
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def osc_fracs(row: dict) -> list[float]:
    return [v for k, v in row.items() if k.startswith("fm.") and k.endswith(".osc")]


def settled_fracs(row: dict) -> list[float]:
    # not always logged; settled lives in FlipMap.summary but only osc/hot/nozzle
    return []


def last_with_fm(rows: list[dict]) -> dict | None:
    for row in reversed(rows):
        if any(k.startswith("fm.") and k.endswith(".osc") for k in row):
            return row
    return None


def summarize(name: str, rows: list[dict]) -> dict:
    losses = [(r["step"], r["loss"]) for r in rows if "loss" in r]
    ce = [r["ce"] for r in rows if "ce" in r]
    flips = [r.get("td_flips", 0) for r in rows]
    changed = [r.get("delta_avg_changed", 0.0) for r in rows]
    veto = [(r["step"], r.get("exact_veto_frac")) for r in rows
            if r.get("exact_veto_frac") is not None]
    lin = [r["exact_lin_mean"] for r in rows if "exact_lin_mean" in r]
    curv = [r["exact_curv_mean"] for r in rows if "exact_curv_mean" in r]
    fm = last_with_fm(rows)
    osc = osc_fracs(fm) if fm else []

    final = rows[-1] if rows else {}
    summ = {
        "name": name,
        "n_logged": len(rows),
        "final_step": final.get("step"),
        "final_loss": final.get("loss"),
        "final_avg50": final.get("loss_avg50"),
        "final_ce": final.get("ce"),
        "total_td_flips": final.get("td_total_flips"),
        "mean_delta_changed": round(mean(changed), 5) if changed else None,
        "mean_osc_frac": round(mean(osc), 4) if osc else None,
        "fm_step": fm.get("step") if fm else None,
        "veto_traj": veto,
        "mean_veto_frac": round(mean([v for _, v in veto]), 3) if veto else None,
        "mean_lin": (sum(lin) / len(lin)) if lin else None,
        "mean_curv": (sum(curv) / len(curv)) if curv else None,
        "loss_curve": losses,
    }
    return summ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proxy", required=True)
    ap.add_argument("--exact", required=True)
    ap.add_argument("--out", default="results/ternary-exact-td-ab")
    args = ap.parse_args()

    proxy = summarize("proxy", load_log(Path(args.proxy)))
    exact = summarize("exact", load_log(Path(args.exact)))

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "comparison.json", "w") as f:
        json.dump({"proxy": proxy, "exact": exact}, f, indent=2)

    def fmt(v, nd=4):
        return f"{v:.{nd}f}" if isinstance(v, (int, float)) else str(v)

    print("=" * 72)
    print("TD ACCEPTANCE A/B — gradient-proxy vs exact-ΔL (session 213)")
    print("=" * 72)
    print(f"{'metric':<26}{'proxy':>20}{'exact':>20}")
    print("-" * 72)
    rows = [
        ("final step", "final_step", 0),
        ("final loss", "final_loss", 3),
        ("final avg50 loss", "final_avg50", 3),
        ("final CE", "final_ce", 4),
        ("total TD flips", "total_td_flips", 0),
        ("mean Δ changed frac", "mean_delta_changed", 5),
        ("mean osc frac (FlipMap)", "mean_osc_frac", 4),
        ("mean veto frac", "mean_veto_frac", 3),
        ("mean |linear|", "mean_lin", 6),
        ("mean curv·Δe²", "mean_curv", 6),
    ]
    for label, key, nd in rows:
        print(f"{label:<26}{fmt(proxy.get(key), nd):>20}{fmt(exact.get(key), nd):>20}")
    print("-" * 72)

    # Headline reads
    if proxy.get("final_avg50") and exact.get("final_avg50"):
        d = exact["final_avg50"] - proxy["final_avg50"]
        verdict = "exact LOWER ✓" if d < 0 else "exact higher"
        print(f"\nΔ final avg50 (exact − proxy) = {d:+.3f}  → {verdict}")
    if proxy.get("mean_osc_frac") is not None and exact.get("mean_osc_frac") is not None:
        do = exact["mean_osc_frac"] - proxy["mean_osc_frac"]
        v = "exact FEWER oscillators ✓" if do < 0 else "exact more oscillators"
        print(f"Δ osc frac (exact − proxy)   = {do:+.4f}  → {v}")
    if exact.get("mean_veto_frac") is not None:
        print(f"curvature vetoed ~{exact['mean_veto_frac']*100:.0f}% of proxy's "
              f"would-be flips (λ=1)")
    print(f"\nwrote {out_dir/'comparison.json'}")


if __name__ == "__main__":
    main()
