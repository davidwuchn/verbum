#!/usr/bin/env python3
# register: topological/routing (FFN gate) + value (attention o_proj)
"""Reading preference — objects as EXISTENTIALS or CONSTANTS? (s248 reason #3)

THE QUESTION (s248 reason #3). ffn_program_decode found only WEAK B-tracking on prose
labelled with the existential reading (`a dog` = ∃y.dog(y)∧…, B-heavy). A free post-hoc
on the balanced run showed the gate register decodes MORE C and LESS B when an object is
present — the OPPOSITE of the existential prediction and exactly the CONSTANT-object
prediction. So the weak B-signal may be a LABELING MISMATCH: we labelled B, the model
computes the object as a constant entity argument → C. This script tests it cleanly.

THE DISCRIMINATOR (object-count ladder, data/reading-probes.jsonl):
    0 obj (intransitive)  exist=const            (C:0, B:1)
    1 obj (transitive)    const S,B,C / exist B:3 (const C:1 | exist B:3)
    2 obj (ditransitive)  const S,B,C,C / exist B:5 (const C:2 | exist B:5)
  • CONSTANT reading   → C scales with #objects {0,1,2}, B flat.
  • EXISTENTIAL reading → B scales with #objects {1,3,5}, C flat at 0.

So decode the gate (opcode) register, take MEAN z per combinator over the zone (length-
controlled), and ask which SCALES with the object count:
    Spearman(z(C), n_objects)  > 0  ⇒ CONSTANT reading   (model: object = entity arg)
    Spearman(z(B), n_objects)  > 0  ⇒ EXISTENTIAL reading (model: object = ∃ quantifier)
The SLOPE controls for the C common-mode (a uniform baseline cancels); two-sided.

METHOD: reuses the validated spine (calibrate_v2 gate+attn registers with matched-prefix
null; one dual-hook forward per item; the RelationalCrystalClassifier decode).

Usage:
    uv run python scripts/experiments/ffn_reading_preference.py --smoke
    uv run python scripts/experiments/ffn_reading_preference.py --model Qwen/Qwen3-8B

License: MIT. AGENTS.md S5 λ provenance (this project's instruments).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from scipy import stats

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "instruments"))
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))

from ffn_program_decode import (  # noqa: E402
    classify_positions,
    forward_dual,
    op_layer_profile,
    zone_layers,
)
from opcode_monitor_v2 import (  # noqa: E402
    COMPILE_GATE,
    _git_sha,
    _json_safe,
    _transformers_version,
    calibrate_v2,
    gate_prefix_len,
    load_model_and_tokenizer,
)

RESULTS_DIR = _ROOT / "results" / "ffn-reading-preference"
PROBES = _ROOT / "data" / "reading-probes.jsonl"


def meanz(reads, zone, op):
    """Mean decoded z(op) over (content tokens × zone layers), ignoring NaN."""
    prof = op_layer_profile(reads, zone, op)
    vals = [v for v in prof.values() if not np.isnan(v)]
    return float(np.mean(vals)) if vals else float("nan")


def _spear(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    m = ~(np.isnan(x) | np.isnan(y))
    if m.sum() < 5 or np.std(x[m]) == 0 or np.std(y[m]) == 0:
        return float("nan"), float("nan")
    r, p = stats.spearmanr(x[m], y[m])
    return round(float(r), 4), round(float(p), 4)


def run(model_name, n_perm_calib, ppc, null_cap, zone_lo, zone_hi, max_items):
    print("═" * 78)
    print("READING PREFERENCE — existential (B) vs constant (C) objects (s248)")
    print("═" * 78)
    rows = [json.loads(line) for line in open(PROBES, encoding="utf-8")]
    if max_items is not None:
        # keep a balance across object counts under the cap
        by = {}
        for r in rows:
            by.setdefault(r["n_objects"], []).append(r)
        rows = [r for n in sorted(by) for r in by[n][: max(1, max_items // len(by))]]
    print(f"[probes] {len(rows)} items  by_n_objects="
          f"{dict(Counter(r['n_objects'] for r in rows))}")

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    layers = list(range(n_layers))
    print(f"[model] {model_name}  layers={n_layers}")

    print("\n[calib] FFN gate register ...")
    rcc_ffn, calib_ffn = calibrate_v2(
        model, tok, torch_mod, layers, n_perm_calib, ppc, null_cap,
        null_mode="gateneutral", hook="gate")
    print("[calib] attention o_proj register ...")
    rcc_attn, calib_attn = calibrate_v2(
        model, tok, torch_mod, layers, n_perm_calib, ppc, null_cap,
        null_mode="gateneutral", hook="attn")
    zl_ffn = zone_layers(rcc_ffn.crystal_layers, n_layers, zone_lo, zone_hi)
    zl_attn = zone_layers(rcc_attn.crystal_layers, n_layers, zone_lo, zone_hi)
    print(f"[calib] FFN  zone={zl_ffn}")
    print(f"[calib] attn zone={zl_attn}")

    gate_n = gate_prefix_len(tok)
    per_item = []
    print(f"\n[decode] {len(rows)} items ...")
    for i, item in enumerate(rows):
        if i % 25 == 0:
            print(f"[decode]   {i}/{len(rows)} ...")
        sg, sa, n = forward_dual(COMPILE_GATE + item["input"], model, tok, torch_mod,
                                 layers)
        pos = list(range(min(gate_n, n - 1), n))
        rf = classify_positions(rcc_ffn, sg, layers, pos)
        ra = classify_positions(rcc_attn, sa, layers, pos)
        per_item.append({
            "input": item["input"], "n_objects": item["n_objects"],
            "category": item["category"],
            "ffn_zB": round(meanz(rf, zl_ffn, "B"), 4),
            "ffn_zC": round(meanz(rf, zl_ffn, "C"), 4),
            "ffn_zS": round(meanz(rf, zl_ffn, "S"), 4),
            "attn_zB": round(meanz(ra, zl_attn, "B"), 4),
            "attn_zC": round(meanz(ra, zl_attn, "C"), 4),
            "attn_zS": round(meanz(ra, zl_attn, "S"), 4),
        })

    # proportions (length / common-mode controlled): of the positive decoded mass over
    # {B,S,C}, what fraction is C vs B? The post-hoc discriminator (raw z inflates with
    # complexity; proportion cancels the uniform common-mode → the real shift).
    for p in per_item:
        for reg in ("ffn", "attn"):
            pos = {k: max(p[f"{reg}_z{k}"], 0.0) for k in ("B", "S", "C")}
            tot = sum(pos.values())
            p[f"{reg}_Cprop"] = round(pos["C"] / tot, 4) if tot > 0 else float("nan")
            p[f"{reg}_Bprop"] = round(pos["B"] / tot, 4) if tot > 0 else float("nan")

    nobj = [p["n_objects"] for p in per_item]
    verdict = {
        "model": model_name, "n_layers": n_layers, "n_items": len(per_item),
        "zone_depth": [zone_lo, zone_hi], "ffn_zone": zl_ffn, "attn_zone": zl_attn,
        "by_n_objects": dict(Counter(nobj)),
    }
    for reg in ("ffn", "attn"):
        zC = [p[f"{reg}_zC"] for p in per_item]
        zB = [p[f"{reg}_zB"] for p in per_item]
        Cp = [p[f"{reg}_Cprop"] for p in per_item]
        Bp = [p[f"{reg}_Bprop"] for p in per_item]
        contrast = [c - b for c, b in zip(Cp, Bp, strict=True)]  # C-share − B-share
        rc, pc = _spear(nobj, zC)
        rb, pb = _spear(nobj, zB)
        rcp, pcp = _spear(nobj, Cp)
        rbp, pbp = _spear(nobj, Bp)
        rct, pct = _spear(nobj, contrast)  # PRIMARY discriminator (length-controlled)
        ladder = {}
        for n in sorted(set(nobj)):
            sel = [j for j, x in enumerate(nobj) if x == n]
            ladder[str(n)] = {
                "zC": round(float(np.nanmean([zC[j] for j in sel])), 3),
                "zB": round(float(np.nanmean([zB[j] for j in sel])), 3),
                "Cprop": round(float(np.nanmean([Cp[j] for j in sel])), 3),
                "Bprop": round(float(np.nanmean([Bp[j] for j in sel])), 3),
            }
        # PRIMARY (length-controlled): does the C-share rise (constant) or fall
        # (existential) with object count? sign of the C−B-share slope decides.
        supports = ("constant" if (rct > 0 and not np.isnan(rct)) else
                    "existential" if (rct < 0 and not np.isnan(rct)) else "neither")
        verdict[reg] = {
            "PRIMARY_spearman_Cshare_minus_Bshare_vs_nobjects": rct,
            "PRIMARY_p": pct, "PRIMARY_supports": supports,
            "spearman_Cprop_vs_nobjects": rcp, "Cprop_p": pcp,
            "spearman_Bprop_vs_nobjects": rbp, "Bprop_p": pbp,
            "spearman_zC_raw_vs_nobjects": rc, "zC_raw_p": pc,
            "spearman_zB_raw_vs_nobjects": rb, "zB_raw_p": pb,
            "ladder_mean_by_nobjects": ladder,
        }
    verdict["calib_ffn"] = calib_ffn
    verdict["calib_attn"] = calib_attn

    _report(verdict)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    (RESULTS_DIR / f"verdict_{slug}.json").write_text(
        json.dumps(_json_safe(verdict), indent=2), encoding="utf-8")
    (RESULTS_DIR / f"per_item_{slug}.json").write_text(
        json.dumps(_json_safe(per_item), indent=2, ensure_ascii=False),
        encoding="utf-8")
    (RESULTS_DIR / f"meta_{slug}.json").write_text(json.dumps({
        "model": model_name, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "probes": str(PROBES.relative_to(_ROOT)),
        "params": {"n_perm_calib": n_perm_calib, "ppc": ppc, "null_cap": null_cap,
                   "zone_lo": zone_lo, "zone_hi": zone_hi, "max_items": max_items},
    }, indent=2), encoding="utf-8")
    print(f"\n[write] {RESULTS_DIR}/verdict_{slug}.json (+ per_item, meta)")
    return verdict


def _report(v):
    print("\n" + "═" * 78)
    print(f"VERDICT — {v['n_items']} items  by_n_objects={v['by_n_objects']}")
    print("═" * 78)
    print("As object count rises {0,1,2}: does the C-SHARE rise (CONSTANT reading) or "
          "the B-SHARE (EXISTENTIAL)?")
    for reg in ("ffn", "attn"):
        d = v[reg]
        print(f"\n[{reg} register]  zone-mean by n_objects (Cprop/Bprop = "
              "length-controlled shares):")
        for n, m in d["ladder_mean_by_nobjects"].items():
            print(f"    {n} obj: Cprop={m['Cprop']:.3f} Bprop={m['Bprop']:.3f}  "
                  f"(raw z(C)={m['zC']:+.2f} z(B)={m['zB']:+.2f})")
        print(f"  ★ PRIMARY Spearman (Cshare−Bshare) vs n_obj = "
              f"{d['PRIMARY_spearman_Cshare_minus_Bshare_vs_nobjects']} "
              f"(p={d['PRIMARY_p']})")
        print(f"    Cprop slope={d['spearman_Cprop_vs_nobjects']} "
              f"(p={d['Cprop_p']})  Bprop slope={d['spearman_Bprop_vs_nobjects']} "
              f"(p={d['Bprop_p']})")
        print(f"  ⇒ supports the {d['PRIMARY_supports'].upper()} reading")
    print("═" * 78)


def main():
    ap = argparse.ArgumentParser(description="Reading preference experiment")
    ap.add_argument("--model", default="Qwen/Qwen3-8B")
    ap.add_argument("--zone-lo", type=float, default=0.70)
    ap.add_argument("--zone-hi", type=float, default=0.86)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    model_name = args.model
    if args.smoke:
        if model_name == "Qwen/Qwen3-8B":
            model_name = "Qwen/Qwen3-0.6B"
        n_perm_calib, ppc, null_cap, max_items = 80, 4, 200, 18
        print("[smoke] mode")
    else:
        n_perm_calib, ppc, null_cap, max_items = 300, None, None, None
    run(model_name, n_perm_calib, ppc, null_cap, args.zone_lo, args.zone_hi, max_items)


if __name__ == "__main__":
    main()
