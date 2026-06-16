#!/usr/bin/env python3
# register: topological/routing
"""Kernel-reference PROSE bridge — feasibility (s233, v5 lead 2b).

s233 lead 2 found BARE symbolic CL programs route only the S-gauge on Qwen3-14B
(target_recall 1/7; reducibility not tracked) -> the gate-routing register reads PROSE
SEMANTICS, not symbolic CL syntax. Before investing in a CL->decompiled-prose renderer,
de-risk the bridge: does PROSE route its combinator AT ALL (held-out, non-circular)?

Design (the precursor, λ measure):
  • split crystal_probes per-combinator into CALIB (most) + held-out TEST (last k).
  • calibrate the s231 classifier ONLY on CALIB (centroid_probes=calib) -> the TEST
    prose is UNSEEN by the centroids (non-circular).
  • read each TEST prose probe's LAST-token per-layer routing (the centroid locus where
    a probe's combinator semantics resolves), compute route_fracs.
  • RECALL: the probe's labeled combinator is routed (z>thresh) at some crystal layer.
    SPECIFICITY: that labeled combinator is the TOP-routed CRYSTAL op for the probe.

Contrast vs the bare-symbolic baseline (target_recall 1/7, all-S gauge): if held-out
prose RECALLS its combinator and is SPECIFIC, the register is prose-semantic and the
kernel-as-reference bridge is viable via decompiled prose (next: CL -> trace ->
render prose). If prose ALSO collapses to gauge, the substrate is calibration-fragile.

Usage:
    uv run python scripts/experiments/kernel_reference_prose.py --smoke
    uv run python scripts/experiments/kernel_reference_prose.py --model Qwen/Qwen3-14B

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))
sys.path.insert(0, str(_ROOT / "scripts" / "instruments"))

from opcode_monitor_v2 import (  # noqa: E402
    Z_SWEEP,
    _git_sha,
    _json_safe,
    _transformers_version,
    calibrate_v2,
    forward_all_positions,
    load_model_and_tokenizer,
)
from relational_opcode import CRYSTAL  # noqa: E402

from verbum.probes.library import crystal_probes  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "kernel-reference-audit"
# the single-combinator crystal labels we test recall on (exclude WHNF = terminal/stop)
TEST_COMBINATORS = ["K", "I", "B", "C", "S", "D", "W", "Y"]


def split_probes(heldout_per: int) -> tuple[list, list]:
    """Per-combinator: last `heldout_per` -> TEST, the rest -> CALIB."""
    by_comb: dict[str, list] = defaultdict(list)
    for p in crystal_probes():
        if p.combinator in CRYSTAL:
            by_comb[p.combinator].append(p)
    calib, test = [], []
    for comb, ps in by_comb.items():
        k = min(heldout_per, max(0, len(ps) - 1))
        test_ps = ps[len(ps) - k:] if k else []
        calib_ps = ps[: len(ps) - k]
        # only test the single-combinator labels we audit recall on
        if comb in TEST_COMBINATORS:
            test.extend(test_ps)
        calib.extend(calib_ps)
    return calib, test


def read_last_token(rcc, store, layers) -> dict[int, tuple[str, float]]:
    """Classify the LAST token; reduce each layer to its argmax (op, z)."""
    n = store[layers[0]].shape[0]
    gate_tok = {li: store[li][n - 1] for li in layers}
    tok_ops = rcc.classify(gate_tok)
    red: dict[int, tuple[str, float]] = {}
    for li, zmap in tok_ops.per_layer.items():
        op = max(zmap, key=zmap.get)
        red[li] = (op, float(zmap[op]))
    return red


def route_fracs(read: dict[int, tuple[str, float]], crystal_layers, zthresh):
    cset = set(crystal_layers)
    counts: Counter = Counter()
    n_cells = 0
    for li, (op, z) in read.items():
        if li not in cset:
            continue
        n_cells += 1
        if z > zthresh:
            counts[op] += 1
    return ({op: counts[op] / n_cells for op in counts} if n_cells else {}), n_cells


def main() -> None:
    parser = argparse.ArgumentParser(description="Kernel-reference prose bridge")
    parser.add_argument("--model", default="Qwen/Qwen3-14B")
    parser.add_argument("--heldout-per", type=int, default=10)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    model_name = args.model
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        n_perm, ppc, null_cap, heldout = 80, 5, 200, 3
        print("[prose] SMOKE MODE")
    else:
        n_perm, ppc, null_cap, heldout = 300, None, None, args.heldout_per

    calib, test = split_probes(heldout)
    print(f"[prose] calib={len(calib)} test={len(test)} (heldout_per={heldout})")

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    layers = list(range(n_layers))

    rcc, cal = calibrate_v2(model, tok, torch_mod, layers, n_perm, ppc, null_cap,
                            null_mode="crosstask", centroid_probes=calib)
    crystal_layers = rcc.crystal_layers
    print(f"[prose] crystal layers: {len(crystal_layers)}/{n_layers}")

    # read held-out prose
    per_probe = []
    for p in test:
        store, _ = forward_all_positions(p.prompt, model, tok, torch_mod, layers)
        read = read_last_token(rcc, store, layers)
        rec = {"combinator": p.combinator, "prompt": p.prompt[:60], "by_z": {}}
        for z in Z_SWEEP:
            fr, _n = route_fracs(read, crystal_layers, z)
            crystal_fr = {op: fr.get(op, 0.0) for op in CRYSTAL}
            top = (max(crystal_fr, key=crystal_fr.get)
                   if any(crystal_fr.values()) else None)
            rec["by_z"][f"z={z}"] = {
                "label_frac": round(fr.get(p.combinator, 0.0), 4),
                "top_crystal_op": top,
                "recall_hit": bool(fr.get(p.combinator, 0.0) > 0),
                "specific_hit": bool(
                    top == p.combinator and fr.get(p.combinator, 0) > 0),
            }
        per_probe.append(rec)

    # aggregate per z + per combinator
    verdict: dict = {}
    for z in Z_SWEEP:
        key = f"z={z}"
        recall = [r["by_z"][key]["recall_hit"] for r in per_probe]
        spec = [r["by_z"][key]["specific_hit"] for r in per_probe]
        per_comb: dict[str, dict] = {}
        for c in TEST_COMBINATORS:
            rows = [r for r in per_probe if r["combinator"] == c]
            if not rows:
                continue
            per_comb[c] = {
                "n": len(rows),
                "recall": round(
                    float(np.mean([r["by_z"][key]["recall_hit"] for r in rows])), 3),
                "specificity": round(
                    np.mean([r["by_z"][key]["specific_hit"] for r in rows]), 3),
                "mean_label_frac": round(
                    float(np.mean([r["by_z"][key]["label_frac"] for r in rows])), 4),
            }
        verdict[key] = {
            "n_test": len(per_probe),
            "recall_rate": round(float(np.mean(recall)), 3) if recall else 0.0,
            "specificity_rate": round(float(np.mean(spec)), 3) if spec else 0.0,
            "per_combinator": per_comb,
            # vs bare-symbolic baseline (s233 lead 2): target_recall 1/7, all-S gauge
            "bridge_viable": bool(np.mean(recall) > 0.5 and np.mean(spec) > 0.25),
        }

    print("\n" + "═" * 72)
    print("KERNEL-REFERENCE PROSE BRIDGE — held-out recall/specificity")
    print("═" * 72)
    for z in Z_SWEEP:
        d = verdict[f"z={z}"]
        print(f"\n[z={z}]  n_test={d['n_test']}  recall={d['recall_rate']} "
              f"specificity={d['specificity_rate']}  VIABLE={d['bridge_viable']}")
        for c, cd in d["per_combinator"].items():
            print(f"    {c}: recall={cd['recall']} spec={cd['specificity']} "
                  f"label_frac={cd['mean_label_frac']} (n={cd['n']})")
    print("═" * 72 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    out = {"calibration_summary": cal, "per_probe": per_probe, "verdict": verdict,
           "crystal_layers": crystal_layers}
    (RESULTS_DIR / f"prose_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(out), indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "n_layers": n_layers, "n_perm": n_perm, "heldout_per": heldout,
        "n_calib": len(calib), "n_test": len(test), "z_sweep": Z_SWEEP,
        "reference": "held-out crystal-prose combinator labels (non-circular split)",
    }
    (RESULTS_DIR / f"prose_meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[prose] wrote {RESULTS_DIR}/prose_verdict_{slug}.json")


if __name__ == "__main__":
    main()
