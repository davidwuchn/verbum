#!/usr/bin/env python3
# register: topological/routing (FFN gate native order)
"""Program Native Order — infer the model's own FFN opcode depth schedule.

The path tracer showed that Qwen3-14B does not preferentially follow the kernel's
certified `fired_sequence` order under same-multiset controls. This experiment stops
asking whether the model follows OUR bracket-abstraction order and instead asks what
order the model actually exposes in the FFN gate routing register.

For each probe and each op in {B,C,S}, read matched-null relational z(op) over content
positions and crystal-bearing layers, then summarize:
  • peak layer: layer with max mean z(op) over content tokens;
  • centroid layer: z-positive weighted average depth for the op;
  • pairwise order relations S<B, B<C, S<C by peak and centroid;
  • category/c_count aggregates and C-load vs object-count.

Usage:
    uv run python scripts/experiments/program_native_order.py --smoke
    uv run python scripts/experiments/program_native_order.py \
      --model Qwen/Qwen3-14B --probe-set data/firing-probes.const.jsonl

License: MIT. AGENTS.md S5 λ provenance.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))
sys.path.insert(0, str(_ROOT / "scripts" / "instruments"))

from ffn_program_decode import (  # noqa: E402
    FIRING_SET,
    build_firing_corpus,
    classify_positions,
    zone_layers,
)
from opcode_monitor_v2 import (  # noqa: E402
    COMPILE_GATE,
    _git_sha,
    _json_safe,
    _transformers_version,
    calibrate_v2,
    forward_all_positions,
    gate_prefix_len,
    load_model_and_tokenizer,
)

RESULTS_DIR = _ROOT / "results" / "program-native-order"
PAIRS = [("S", "B"), ("B", "C"), ("S", "C")]


def op_layer_profile(
    reads: list[dict[int, dict[str, float]]], layers: list[int], op: str
) -> dict[int, float]:
    prof = {}
    for li in layers:
        vals = [r[li][op] for r in reads if li in r]
        prof[li] = float(np.mean(vals)) if vals else float("nan")
    return prof


def summarize_op(prof: dict[int, float], n_layers: int) -> dict:
    vals = [(li, z) for li, z in prof.items() if not np.isnan(z)]
    if not vals:
        return {"peak_layer": None, "peak_depth": None, "peak_z": None,
                "centroid_layer": None, "centroid_depth": None,
                "mean_z": None, "positive_mass": 0.0}
    peak_layer, peak_z = max(vals, key=lambda x: x[1])
    zs = np.array([z for _, z in vals], dtype=float)
    lis = np.array([li for li, _ in vals], dtype=float)
    pos = np.maximum(zs, 0.0)
    mass = float(pos.sum())
    if mass > 1e-12:
        cen = float((lis * pos).sum() / mass)
    else:
        cen = None
    denom = max(n_layers - 1, 1)
    return {
        "peak_layer": int(peak_layer),
        "peak_depth": round(float(peak_layer / denom), 4),
        "peak_z": round(float(peak_z), 4),
        "centroid_layer": round(cen, 4) if cen is not None else None,
        "centroid_depth": round(float(cen / denom), 4) if cen is not None else None,
        "mean_z": round(float(np.mean(zs)), 4),
        "positive_mass": round(mass, 4),
    }


def compare_order(op_summ: dict[str, dict], key: str) -> dict[str, bool | None]:
    out = {}
    for a, b in PAIRS:
        av = op_summ[a].get(key)
        bv = op_summ[b].get(key)
        out[f"{a}_before_{b}"] = None if av is None or bv is None else bool(av < bv)
    return out


def _safe_slug(model_name: str, probe_set: str | None) -> str:
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    if probe_set:
        stem = Path(probe_set).stem
        slug += "_" + (stem.split(".")[-1] if "." in stem else stem)
    return slug


def _mean(xs: list[float | int | None]) -> float | None:
    vals = [float(x) for x in xs if x is not None]
    return round(float(np.mean(vals)), 4) if vals else None


def _frac(xs: list[bool | None]) -> float | None:
    vals = [x for x in xs if x is not None]
    return round(float(np.mean(vals)), 4) if vals else None


def summarize_group(rows: list[dict]) -> dict:
    out: dict = {"n": len(rows)}
    out["truth_distribution"] = dict(Counter(r["dominant_fired"] for r in rows))
    for op in FIRING_SET:
        out[f"{op}_peak_layer_mean"] = _mean(
            [r["ops_zone"][op]["peak_layer"] for r in rows])
        out[f"{op}_centroid_layer_mean"] = _mean(
            [r["ops_zone"][op]["centroid_layer"] for r in rows])
        out[f"{op}_peak_z_mean"] = _mean([r["ops_zone"][op]["peak_z"] for r in rows])
        out[f"{op}_positive_mass_mean"] = _mean(
            [r["ops_zone"][op]["positive_mass"] for r in rows])
    for a, b in PAIRS:
        out[f"peak_P_{a}_before_{b}"] = _frac(
            [r["order_peak"].get(f"{a}_before_{b}") for r in rows])
        out[f"centroid_P_{a}_before_{b}"] = _frac(
            [r["order_centroid"].get(f"{a}_before_{b}") for r in rows])
    return out


def spearman(x: list[float], y: list[float]) -> tuple[float | None, float | None]:
    if len(x) < 3 or len(set(x)) < 2 or len(set(y)) < 2:
        return None, None
    from scipy import stats

    r, p = stats.spearmanr(x, y)
    return round(float(r), 4), round(float(p), 4)


def run(
    model_name: str,
    probe_set: str,
    max_items: int | None,
    null_mode: str,
    zone_lo: float,
    zone_hi: float,
    n_perm_calib: int,
    ppc: int | None,
    null_cap: int | None,
) -> tuple[dict, list[dict], dict]:
    print("═" * 78)
    print("PROGRAM NATIVE ORDER — infer FFN gate opcode schedule")
    print("═" * 78)
    firing, nonfiring = build_firing_corpus([Path(probe_set)])
    if max_items is not None:
        firing = firing[:max_items]
    print(
        f"[corpus] source={probe_set} firing={len(firing)} "
        f"nonfiring={len(nonfiring)}"
    )

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    layers = list(range(n_layers))
    print(f"[model] {model_name} layers={n_layers}")

    print(f"\n[calib] FFN gate register null_mode={null_mode} ...")
    rcc, calib = calibrate_v2(
        model, tok, torch_mod, layers, n_perm_calib, ppc, null_cap,
        null_mode=null_mode, hook="gate")
    crystal_layers = rcc.crystal_layers
    zlayers = zone_layers(crystal_layers, n_layers, zone_lo, zone_hi)
    print(f"[calib] crystal_layers={len(crystal_layers)}/{n_layers} zone={zlayers}")

    gate_n = gate_prefix_len(tok)
    per_item: list[dict] = []
    print(f"\n[decode] {len(firing)} items ...")
    for i, item in enumerate(firing):
        if i % 20 == 0:
            print(f"[decode]   item {i}/{len(firing)} ...")
        prompt = COMPILE_GATE + item["input"]
        store, n_tok = forward_all_positions(prompt, model, tok, torch_mod, layers,
                                             hook="gate")
        positions = list(range(min(gate_n, n_tok - 1), n_tok))
        reads = classify_positions(rcc, store, layers, positions)

        ops_zone = {}
        ops_all = {}
        for op in FIRING_SET:
            ops_zone[op] = summarize_op(op_layer_profile(reads, zlayers, op), n_layers)
            ops_all[op] = summarize_op(
                op_layer_profile(reads, crystal_layers, op), n_layers)
        per_item.append({
            "input": item["input"],
            "category": item["category"],
            "dominant_fired": item["dominant_fired"],
            "fired_sequence": item["fired_sequence"],
            "fired_multiset": item["fired_multiset"],
            "reduction_len": item["reduction_len"],
            "b_count": item.get("b_count"),
            "s_count": item.get("s_count"),
            "c_count": item.get("c_count"),
            "n_content_tokens": len(positions),
            "zone_layers": zlayers,
            "ops_zone": ops_zone,
            "ops_all_crystal": ops_all,
            "order_peak": compare_order(ops_zone, "peak_layer"),
            "order_centroid": compare_order(ops_zone, "centroid_layer"),
            "order_peak_all_crystal": compare_order(ops_all, "peak_layer"),
            "order_centroid_all_crystal": compare_order(ops_all, "centroid_layer"),
        })

    by_category = {}
    for cat in sorted({r["category"] for r in per_item}):
        rows = [r for r in per_item if r["category"] == cat]
        by_category[cat] = summarize_group(rows)
    by_c_count = {}
    c_counts = sorted({r["c_count"] for r in per_item if r.get("c_count") is not None})
    for cc in c_counts:
        rows = [r for r in per_item if r.get("c_count") == cc]
        by_c_count[str(cc)] = summarize_group(rows)

    c_count = [float(r["c_count"]) for r in per_item]
    c_mass = [float(r["ops_zone"]["C"]["positive_mass"]) for r in per_item]
    c_peak_z = [float(r["ops_zone"]["C"]["peak_z"]) for r in per_item]
    c_centroid = [float(r["ops_zone"]["C"]["centroid_layer"]) for r in per_item]
    mass_r, mass_p = spearman(c_count, c_mass)
    peak_r, peak_p = spearman(c_count, c_peak_z)
    cen_r, cen_p = spearman(c_count, c_centroid)

    verdict = {
        "model": model_name,
        "n_layers": n_layers,
        "probe_set": probe_set,
        "n_items": len(per_item),
        "null_mode": null_mode,
        "zone_depth": [zone_lo, zone_hi],
        "zone_layers": zlayers,
        "crystal_layers": crystal_layers,
        "truth_distribution": dict(Counter(r["dominant_fired"] for r in per_item)),
        "native_order": summarize_group(per_item),
        "by_category": by_category,
        "by_c_count": by_c_count,
        "c_count_correlations": {
            "spearman_C_positive_mass_vs_c_count": mass_r,
            "p_mass": mass_p,
            "spearman_C_peak_z_vs_c_count": peak_r,
            "p_peak_z": peak_p,
            "spearman_C_centroid_layer_vs_c_count": cen_r,
            "p_centroid_layer": cen_p,
        },
        "calib": calib,
    }
    meta = {
        "model": model_name,
        "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "params": {
            "probe_set": probe_set,
            "max_items": max_items,
            "null_mode": null_mode,
            "zone_lo": zone_lo,
            "zone_hi": zone_hi,
            "n_perm_calib": n_perm_calib,
            "ppc": ppc,
            "null_cap": null_cap,
        },
        "method": "Infer native FFN gate opcode order via peak/centroid layer of "
                  "matched-null relational z(op) profiles over content tokens.",
    }
    return verdict, per_item, meta


def write_outputs(verdict: dict, per_item: list[dict], meta: dict) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = _safe_slug(verdict["model"], verdict.get("probe_set"))
    (RESULTS_DIR / f"verdict_{slug}.json").write_text(
        json.dumps(_json_safe(verdict), indent=2), encoding="utf-8")
    (RESULTS_DIR / f"per_item_{slug}.json").write_text(
        json.dumps(_json_safe(per_item), indent=2), encoding="utf-8")
    (RESULTS_DIR / f"meta_{slug}.json").write_text(
        json.dumps(_json_safe(meta), indent=2), encoding="utf-8")
    print(f"[write] {RESULTS_DIR / f'verdict_{slug}.json'} (+ per_item, meta)")


def report(verdict: dict) -> None:
    n = verdict["native_order"]
    print("\n" + "═" * 78)
    print("PROGRAM NATIVE ORDER — VERDICT")
    print("═" * 78)
    print(f"items={verdict['n_items']} truth={verdict['truth_distribution']}")
    print(f"crystal_layers={len(verdict['crystal_layers'])}/{verdict['n_layers']} "
          f"zone={verdict['zone_layers']}")
    print("\nNative order probabilities (zone):")
    for a, b in PAIRS:
        print(
            f"  peak P({a}<{b})={n[f'peak_P_{a}_before_{b}']}  "
            f"centroid P({a}<{b})={n[f'centroid_P_{a}_before_{b}']}"
        )
    print("\nMean peak/centroid layers by op:")
    for op in FIRING_SET:
        print(
            f"  {op}: peak={n[f'{op}_peak_layer_mean']} "
            f"centroid={n[f'{op}_centroid_layer_mean']} "
            f"mass={n[f'{op}_positive_mass_mean']}"
        )
    print("\nC-count correlations:")
    print(json.dumps(verdict["c_count_correlations"], indent=2))
    print("\nBy category:")
    for cat, d in verdict["by_category"].items():
        print(
            f"  {cat}: n={d['n']} C_mass={d['C_positive_mass_mean']} "
            f"P(B<C)={d['peak_P_B_before_C']} "
            f"P(S<C)={d['peak_P_S_before_C']}"
        )
    print("═" * 78 + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description="Infer native FFN opcode order")
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--probe-set", default="data/firing-probes.const.jsonl")
    ap.add_argument("--max-items", type=int, default=None)
    ap.add_argument("--null-mode", default="gateneutral",
                    choices=["gateneutral", "crosstask"])
    ap.add_argument("--zone-lo", type=float, default=0.70)
    ap.add_argument("--zone-hi", type=float, default=0.86)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    model = args.model
    max_items = args.max_items
    if args.smoke:
        if model == "Qwen/Qwen3-14B":
            model = "Qwen/Qwen3-0.6B"
        n_perm_calib, ppc, null_cap = 80, 3, 200
        max_items = max_items or 6
        print("[smoke] Qwen3-0.6B small calibration")
    else:
        n_perm_calib, ppc, null_cap = 300, None, None

    verdict, per_item, meta = run(
        model, args.probe_set, max_items, args.null_mode, args.zone_lo, args.zone_hi,
        n_perm_calib, ppc, null_cap)
    report(verdict)
    write_outputs(verdict, per_item, meta)


if __name__ == "__main__":
    main()
