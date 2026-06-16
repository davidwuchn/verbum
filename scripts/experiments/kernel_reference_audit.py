#!/usr/bin/env python3
# register: topological/routing
"""Kernel-reference opcode audit (s233, v5 lead 2 / the (b) thread).

Opcode reads do NOT transfer across model scale (s232/s233 lead 1: 8B≠14B≠32B, and the
gated-guard contrast is itself model-dependent). So stop comparing models to each
other — anchor each model's trajectory against a FIXED, model-invariant reference: the
kernel's CERTIFIED reduction trace of a symbolic combinator program (`lambda_ast`).

Feed a symbolic program (e.g. "B f g h"), read its per-token/per-layer opcode routing
(the s231 validated RelationalCrystalClassifier, calibrated on crystal prose probes with
a cross-task null), and measure AGREEMENT with what the kernel certifies the program
does.

Conditions (kernel_reference probe set):
  • SATURATED  — target fires (kernel-certified). e.g. "B f g h" -> fires B.
  • INERT      — same target UNDER-APPLIED -> normal form, no fire. e.g. "B f g".
  • COMPOSITE  — multi-fire, certified ORDER. e.g. "B K I x y" -> B,K,I.

The SATURATED⊗INERT contrast is the load-bearing test (λ measure): does the model's
opcode routing track certified REDUCIBILITY (a live redex) or mere SYMBOL PRESENCE?
  - route_frac(prog, c) = fraction of (crystal-layer x content-token) cells whose
    argmax routed opcode is c at z>thresh.
  - target recall:   route_frac(SAT_X, X) elevated.
  - reducibility:    d = route_frac(SAT_X, X) - route_frac(INERT_X, X) > 0  (the key).
  - specificity:     route_frac(SAT_X, X) beats route_frac(SAT_X, other crystals).
  - trace recall:    composites route their certified-fired combinators.

CAVEAT (recorded, λ measure): the classifier is calibrated on PROSE crystal probes; bare
symbolic CL terms are out-of-distribution. If symbolic programs route only the gauge ops
(Y/S/W) regardless of the certified target, the finding is that the routing register is
prose-semantic, not symbolic-CL — itself a result, and the signal to pivot the reference
to compiled prose. Two-sided either way.

Usage:
    uv run python scripts/experiments/kernel_reference_audit.py --smoke
    uv run python scripts/experiments/kernel_reference_audit.py --model Qwen/Qwen3-14B

License: MIT
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

from opcode_monitor_v2 import (  # noqa: E402
    Z_SWEEP,
    _git_sha,
    _json_safe,
    _transformers_version,
    calibrate_v2,
    forward_all_positions,
    load_model_and_tokenizer,
    read_prompt_tokens,
)
from relational_opcode import CRYSTAL  # noqa: E402

from verbum.probes.kernel_reference import all_probes  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "kernel-reference-audit"


# ═══════════════════════════════════════════════════════════════════════════════
# Read one program -> per-(crystal-layer, token) routed opcode, then route_frac(c)
# ═══════════════════════════════════════════════════════════════════════════════
def route_fracs(
    reads: list[dict[int, tuple[str, float]]], crystal_layers: list[int],
    zthresh: float,
) -> tuple[dict[str, float], int]:
    """reads: per-token {layer: (op, z)}. Returns ({op: frac_of_cells}, n_cells)
    over CRYSTAL layers x tokens where z>zthresh (argmax op carries the cell)."""
    cset = set(crystal_layers)
    counts: Counter = Counter()
    n_cells = 0
    for tok_read in reads:
        for li, (op, z) in tok_read.items():
            if li not in cset:
                continue
            n_cells += 1
            if z > zthresh:
                counts[op] += 1
    fracs = {op: counts[op] / n_cells for op in counts} if n_cells else {}
    return fracs, n_cells


def analyze(
    rcc, model, tok, torch_mod, layers: list[int],
) -> dict:
    crystal_layers = rcc.crystal_layers
    probes = all_probes()
    # per-probe routing fracs at each z
    per_probe: dict[str, dict] = {}
    for p in probes:
        store, n = forward_all_positions(p.program_text, model, tok, torch_mod, layers)
        positions = list(range(1, n)) if n > 1 else [0]  # skip BOS
        reads = read_prompt_tokens(rcc, store, layers, positions)
        rec = {"id": p.id, "program": p.program_text, "target": p.target_combinator,
               "saturated": p.saturated, "composite": p.composite,
               "certified_fired": p.certified_fired_seq, "by_z": {}}
        for z in Z_SWEEP:
            fr, ncells = route_fracs(reads, crystal_layers, z)
            rec["by_z"][f"z={z}"] = {"route_fracs": fr, "n_cells": ncells}
        per_probe[p.id] = rec
    return {"crystal_layers": crystal_layers, "per_probe": per_probe}


# ═══════════════════════════════════════════════════════════════════════════════
# Verdict: saturated-vs-inert reducibility, target recall, specificity, trace recall
# ═══════════════════════════════════════════════════════════════════════════════
def build_verdict(analysis: dict) -> dict:
    pp = analysis["per_probe"]
    sat = {p["target"]: p for p in pp.values() if p["saturated"] and not p["composite"]}
    inert = {p["target"]: p for p in pp.values() if not p["saturated"]}
    composites = [p for p in pp.values() if p["composite"]]
    crystal_targets = [c for c in sat if c in CRYSTAL]

    v: dict = {}
    for z in Z_SWEEP:
        key = f"z={z}"

        def rf(rec, c, _key=key):
            return rec["by_z"][_key]["route_fracs"].get(c, 0.0)

        # (1) reducibility contrast: route_frac(SAT_X, X) - route_frac(INERT_X, X)
        deltas = {}
        sat_target, inert_target = {}, {}
        for c in crystal_targets:
            s = rf(sat[c], c)
            i = rf(inert[c], c) if c in inert else 0.0
            deltas[c] = round(s - i, 4)
            sat_target[c] = round(s, 4)
            inert_target[c] = round(i, 4)
        pos = [c for c, d in deltas.items() if d > 0]
        mean_delta = float(np.mean(list(deltas.values()))) if deltas else 0.0

        # (2) target recall: SAT_X routes X at all (frac>0)
        recall_hits = [c for c in crystal_targets if sat_target[c] > 0]

        # (3) specificity: in SAT_X, is X the top-routed CRYSTAL op (vs other crystals)?
        spec_hits = []
        for c in crystal_targets:
            fr = sat[c]["by_z"][key]["route_fracs"]
            crystal_fr = {op: fr.get(op, 0.0) for op in CRYSTAL}
            top = (max(crystal_fr, key=crystal_fr.get)
                   if any(crystal_fr.values()) else None)
            if top == c and crystal_fr[c] > 0:
                spec_hits.append(c)

        # (4) composite trace recall: fraction of certified-fired routed (frac>0)
        comp_recalls = []
        for p in composites:
            fr = p["by_z"][key]["route_fracs"]
            fired = set(p["certified_fired"]) & set(CRYSTAL)
            if fired:
                hit = sum(1 for c in fired if fr.get(c, 0.0) > 0)
                comp_recalls.append(hit / len(fired))
        comp_recall = float(np.mean(comp_recalls)) if comp_recalls else 0.0

        # gauge check: what dominates SAT programs overall (diagnostic for OOD)
        all_sat_fr: Counter = Counter()
        for c in crystal_targets:
            for op, f in sat[c]["by_z"][key]["route_fracs"].items():
                all_sat_fr[op] += f
        top_overall = all_sat_fr.most_common(3)

        v[key] = {
            "reducibility_mean_delta": round(mean_delta, 4),
            "reducibility_positive": f"{len(pos)}/{len(crystal_targets)}",
            "reducibility_deltas": deltas,
            "sat_target_frac": sat_target,
            "inert_target_frac": inert_target,
            "target_recall": f"{len(recall_hits)}/{len(crystal_targets)}",
            "specificity_hits": f"{len(spec_hits)}/{len(crystal_targets)}",
            "specific_targets": spec_hits,
            "composite_trace_recall": round(comp_recall, 4),
            "top_routed_overall_sat": [(op, round(f, 3)) for op, f in top_overall],
            # decisive: reducibility tracked AND specific (not just gauge)
            "reducibility_tracked": bool(
                mean_delta > 0 and len(pos) > len(crystal_targets) / 2),
            "routing_is_specific": bool(
                len(spec_hits) >= max(1, len(crystal_targets) // 3)),
        }
    return v


def _print_summary(analysis: dict, verdict: dict) -> None:
    print("\n" + "═" * 74)
    print("KERNEL-REFERENCE OPCODE AUDIT — SUMMARY")
    print("═" * 74)
    print(f"Crystal layers: {len(analysis['crystal_layers'])}")
    for z in Z_SWEEP:
        d = verdict[f"z={z}"]
        print(f"\n[z={z}]")
        print(f"  REDUCIBILITY (SAT-INERT): mean d={d['reducibility_mean_delta']} "
              f"pos={d['reducibility_positive']} tracked={d['reducibility_tracked']}")
        print(f"    deltas={d['reducibility_deltas']}")
        print(f"    sat_target ={d['sat_target_frac']}")
        print(f"    inert_target={d['inert_target_frac']}")
        print(f"  target_recall={d['target_recall']}  "
              f"SPECIFICITY={d['specificity_hits']} ({d['specific_targets']})  "
              f"specific={d['routing_is_specific']}")
        print(f"  composite trace recall={d['composite_trace_recall']}")
        print(f"  top routed overall (SAT)={d['top_routed_overall_sat']}")
    print("═" * 74 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Kernel-reference opcode audit")
    parser.add_argument("--model", default="Qwen/Qwen3-14B")
    parser.add_argument("--null-mode", default="crosstask",
                        choices=["crosstask", "gateneutral"],
                        help="crosstask=bare natural-text null (symbolic programs are "
                             "bare, so crosstask is the matched reference)")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    model_name = args.model
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        n_perm, ppc, null_cap = 80, 3, 200
        print("[kref] SMOKE MODE")
    else:
        n_perm, ppc, null_cap = 300, None, None

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    layers = list(range(n_layers))
    print(f"[kref] Layers: {n_layers}")

    rcc, calib = calibrate_v2(model, tok, torch_mod, layers, n_perm, ppc, null_cap,
                              null_mode=args.null_mode)
    print(f"[kref] Crystal-bearing layers: {len(calib['crystal_layers'])}/{n_layers}")

    print("\n[kref] Reading kernel-reference programs ...")
    analysis = analyze(rcc, model, tok, torch_mod, layers)
    verdict = build_verdict(analysis)
    _print_summary(analysis, verdict)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    out = {"calibration_summary": calib, "analysis": analysis, "verdict": verdict}
    (RESULTS_DIR / f"verdict_{slug}_{args.null_mode}.json").write_text(
        json.dumps(_json_safe(out), indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "n_layers": n_layers, "n_perm": n_perm, "probes_per_combinator": ppc,
        "z_sweep": Z_SWEEP, "null_mode": args.null_mode,
        "n_crystal_layers": len(calib["crystal_layers"]),
        "reference": "lambda_ast certified fired_sequence (model-invariant)",
    }
    (RESULTS_DIR / f"meta_{slug}_{args.null_mode}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[kref] wrote {RESULTS_DIR}/verdict_{slug}_{args.null_mode}.json")


if __name__ == "__main__":
    main()
