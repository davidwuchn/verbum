#!/usr/bin/env python3
# register: topological/routing
"""Opcode v5 lead 1 — LOCUS-AGNOSTIC C-routing re-analysis (s233, no GPU).

The s232 scale verdict found the fixed depth>=0.6 C-late detector is the WRONG
cross-model instrument: it found 14B (composition routes C-LATE, L27-32) but MISLOCATES
8B/32B because the composition->C routing LOCUS SHIFTS with scale (32B is C-EARLY,
L5,10,11, depth ~0.1; the readable-zone detector reads 0 there even though a
lambda-specific C-early signal exists).

This RE-ANALYZES the committed gateneutral verdicts (8B/14B/32B) — the per-layer
dominant-op TRAJECTORIES are already stored, so NO GPU re-run is needed. It applies the
locus-agnostic detector (counts C-dominant crystal layers ANYWHERE + per-model locus +
specificity vs the matched gated guards) and asks: with the right instrument, does
composition route C SPECIFICALLY (above the gated controls) on 8B/32B — the models the
fixed-zone detector missed?

Single source of truth: the detector functions are imported from opcode_monitor_v2
(detect_c_profile, locus_agnostic_specificity) — the same code future model runs use.

Usage:
    uv run python scripts/experiments/opcode_v5_locus_agnostic.py

License: MIT
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))

from opcode_monitor_v2 import (  # noqa: E402
    Z_SWEEP,
    detect_c_profile,
    locus_agnostic_specificity,
)

RESULTS_DIR = _ROOT / "results" / "opcode-monitor-v2"
GATED_GUARDS = ("gate_neutral", "gate_retrieval", "gate_arithmetic")
MODELS = [
    ("8B", "verdict_qwen3-8b_gateneutral.json"),
    ("14B", "verdict_qwen3-14b_gateneutral.json"),
    ("32B", "verdict_qwen3-32b_gateneutral.json"),
]


def _depth_label(d: float | None) -> str:
    if d is None:
        return "—"
    if d < 1 / 3:
        return f"{d:.2f}(EARLY)"
    if d < 2 / 3:
        return f"{d:.2f}(MID)"
    return f"{d:.2f}(LATE)"


def reanalyze_model(tag: str, path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    monitor = data["monitor"]
    conds = monitor["conditions"]
    n_layers = data["calibration_summary"]["n_layers"]
    out: dict = {"model": tag, "n_layers": n_layers, "by_z": {}}
    for z in Z_SWEEP:
        key = f"z={z}"
        lam_traj = conds["lambda"]["by_z"][key]["trajectory"]
        guard_trajs = {c: conds[c]["by_z"][key]["trajectory"] for c in GATED_GUARDS}
        la = locus_agnostic_specificity(lam_traj, guard_trajs, n_layers)
        # what the OLD fixed-zone detector said (already in the committed verdict)
        old = data["verdict"][key]
        out["by_z"][key] = {
            "locus_agnostic": la,
            "old_fixed_zone_composition_specific": old["composition_specific"],
            "old_lambda_C_late_frac": old["lambda_C_late_frac"],
            "old_lambda_C_late_layers": old["lambda_C_late_layers"],
            # guard locus profiles (for the table)
            "guard_profiles": {
                c: detect_c_profile(guard_trajs[c], n_layers) for c in GATED_GUARDS
            },
        }
    return out


def main() -> None:
    results = []
    for tag, fname in MODELS:
        p = RESULTS_DIR / fname
        if not p.exists():
            print(f"[v5] MISSING {p} — skipping {tag}")
            continue
        results.append(reanalyze_model(tag, p))

    print("\n" + "═" * 78)
    print("OPCODE v5 lead 1 — LOCUS-AGNOSTIC C-ROUTING (re-analysis, gateneutral null)")
    print("═" * 78)
    for z in Z_SWEEP:
        key = f"z={z}"
        print(f"\n[{key}]")
        print(f"  {'model':5} {'Cfrac':>6} {'nC':>3} {'locus(depth)':>14} "
              f"{'maxGuard':>8} {'excl':>16} {'AGNOSTIC':>9} {'OLDzone':>8}")
        for r in results:
            d = r["by_z"][key]
            la = d["locus_agnostic"]
            lp = la["lambda_C_profile"]
            print(f"  {r['model']:5} "
                  f"{lp['C_frac_all']:6.3f} {lp['n_C']:3d} "
                  f"{_depth_label(lp['C_mean_depth']):>14} "
                  f"{la['max_guard_C_frac_all']:8.3f} "
                  f"{str(la['C_exclusive_layers'])[:16]:>16} "
                  f"{('SPEC' if la['composition_specific_agnostic'] else '·'):>9} "
                  f"{('SPEC' if d['old_fixed_zone_composition_specific'] else '·'):>8}")

    # cross-model verdict: how many models now read composition-specific vs old
    summary = {"by_z": {}}
    for z in Z_SWEEP:
        key = f"z={z}"
        agn_frac = sum(
            r["by_z"][key]["locus_agnostic"]["composition_specific_agnostic"]
            for r in results)
        agn_excl = sum(
            r["by_z"][key]["locus_agnostic"]["exclusive_specific"]
            for r in results)
        old_zone = sum(
            r["by_z"][key]["old_fixed_zone_composition_specific"]
            for r in results)
        summary["by_z"][key] = {
            "n_models": len(results),
            "agnostic_frac_specific": agn_frac,
            "agnostic_exclusive_specific": agn_excl,
            "old_fixed_zone_specific": old_zone,
            "per_model_locus": {
                r["model"]: _depth_label(
                    r["by_z"][key]["locus_agnostic"]["lambda_C_profile"]["C_mean_depth"]
                )
                for r in results
            },
        }

    print("\n" + "─" * 78)
    print(f"CROSS-MODEL VERDICT (composition-specific count, /{len(results)} models):")
    for z in Z_SWEEP:
        s = summary["by_z"][f"z={z}"]
        print(f"  z={z}: agnostic-frac {s['agnostic_frac_specific']} | "
              f"agnostic-exclusive {s['agnostic_exclusive_specific']} | "
              f"OLD fixed-zone {s['old_fixed_zone_specific']}   "
              f"locus={s['per_model_locus']}")
    print("─" * 78 + "\n")

    out = {"per_model": results, "cross_model": summary,
           "instrument": "locus_agnostic_specificity (v5 lead 1)",
           "null_mode": "gateneutral"}
    dst = RESULTS_DIR / "v5_locus_agnostic.json"
    dst.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[v5] wrote {dst}")


if __name__ == "__main__":
    main()
