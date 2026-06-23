#!/usr/bin/env python3
# register: topological/routing (FFN gate) + value (attention o_proj)
"""Scope forcing — CAN the model do existential-B when syntax forces it? (s248 cont.3)

THE CAUSAL TEST (s248 cont.2 follow-up). Reading-preference showed the model reads plain
indefinite objects as CONSTANTS (→ C), not existentials (→ B). Is that a representation
LIMIT, or just the DEFAULT reading? Force wide-scope ∃ in syntax; does z(B) rise?

PAIRED CONTRAST (data/scope-probes.jsonl — matched subj/verb/obj triples, 3 conditions):
    PLAIN  "Every cat fears a dog."               → applicative GT (S,B,C)
    CLEFT  "There is a dog that every cat fears."  → ∃ fronted GT (S,B,B,B, no C)
    RELCL  "Every cat fears a dog that runs."      → ∃ object GT  (S,B,B,B, no C)

For each triple, decode the gate (opcode) + attn registers, take MEAN z per combinator
over the L25-30 zone, and PAIR within triple:
    ΔB = z(B)_forced − z(B)_plain   (if model CAN do existential-B: ΔB > 0)
    ΔC = z(C)_forced − z(C)_plain   (prediction: ΔC < 0)
Wilcoxon signed-rank (paired, one-sided). Verdict:
    ΔB>0 ∧ ΔC<0  ⇒ model DOES existential-B when forced (discoverable, not default)
    ΔB≈0         ⇒ model is ALWAYS applicative (ignores the scope marking)

Usage:
    uv run python scripts/experiments/ffn_scope_forcing.py --smoke
    uv run python scripts/experiments/ffn_scope_forcing.py --model Qwen/Qwen3-8B

License: MIT. AGENTS.md S5 λ provenance (this project's instruments).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
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
    zone_layers,
)
from ffn_reading_preference import meanz  # noqa: E402
from opcode_monitor_v2 import (  # noqa: E402
    COMPILE_GATE,
    _git_sha,
    _json_safe,
    _transformers_version,
    calibrate_v2,
    gate_prefix_len,
    load_model_and_tokenizer,
)

RESULTS_DIR = _ROOT / "results" / "ffn-scope-forcing"
PROBES = _ROOT / "data" / "scope-probes.jsonl"


def _wilcoxon(deltas, alternative):
    d = np.array([x for x in deltas if not np.isnan(x)])
    nz = d[d != 0]
    if nz.size < 5:
        return {"n": int(d.size), "n_nonzero": int(nz.size), "median": None, "p": None}
    try:
        _w, p = stats.wilcoxon(nz, alternative=alternative)
    except ValueError:
        p = float("nan")
    return {"n": int(d.size), "n_nonzero": int(nz.size),
            "median": round(float(np.median(d)), 4),
            "mean": round(float(np.mean(d)), 4),
            "frac_predicted_sign": round(float(
                np.mean(d > 0) if alternative == "greater" else np.mean(d < 0)), 3),
            "p": (round(float(p), 5) if not np.isnan(p) else None)}


def run(model_name, n_perm_calib, ppc, null_cap, zone_lo, zone_hi, max_triples):
    print("═" * 78)
    print("SCOPE FORCING — does forcing ∃ wide-scope raise z(B)? (s248 cont.3)")
    print("═" * 78)
    rows = [json.loads(line) for line in open(PROBES, encoding="utf-8")]
    if max_triples is not None:
        keep = set(sorted({r["triple_id"] for r in rows})[:max_triples])
        rows = [r for r in rows if r["triple_id"] in keep]
    print(f"[probes] {len(rows)} rows  by_condition="
          f"{dict(Counter(r['condition'] for r in rows))}")

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
    print(f"[calib] FFN zone={zl_ffn}  attn zone={zl_attn}")

    gate_n = gate_prefix_len(tok)
    per_item = []
    print(f"\n[decode] {len(rows)} items ...")
    for i, item in enumerate(rows):
        if i % 30 == 0:
            print(f"[decode]   {i}/{len(rows)} ...")
        sg, sa, n = forward_dual(COMPILE_GATE + item["input"], model, tok, torch_mod,
                                 layers)
        pos = list(range(min(gate_n, n - 1), n))
        rf = classify_positions(rcc_ffn, sg, layers, pos)
        ra = classify_positions(rcc_attn, sa, layers, pos)
        rec = {"input": item["input"], "condition": item["condition"],
               "triple_id": item["triple_id"]}
        for reg, reads, zl in (("ffn", rf, zl_ffn), ("attn", ra, zl_attn)):
            zB, zS, zC = (meanz(reads, zl, "B"), meanz(reads, zl, "S"),
                          meanz(reads, zl, "C"))
            pos_sum = max(zB, 0) + max(zS, 0) + max(zC, 0)
            rec[f"{reg}_zB"] = round(zB, 4)
            rec[f"{reg}_zC"] = round(zC, 4)
            rec[f"{reg}_Bprop"] = round(max(zB, 0) / pos_sum, 4) if pos_sum > 0 else \
                float("nan")
            rec[f"{reg}_Cprop"] = round(max(zC, 0) / pos_sum, 4) if pos_sum > 0 else \
                float("nan")
        per_item.append(rec)

    # ── pair within triple ──────────────────────────────────────────────────────
    by_tid: dict[int, dict[str, dict]] = defaultdict(dict)
    for p in per_item:
        by_tid[p["triple_id"]][p["condition"]] = p
    complete = [d for d in by_tid.values()
                if {"plain", "cleft", "relcl"} <= set(d)]
    print(f"\n[pair] {len(complete)} complete triples")

    verdict = {"model": model_name, "n_layers": n_layers, "n_triples": len(complete),
               "zone_depth": [zone_lo, zone_hi], "ffn_zone": zl_ffn,
               "attn_zone": zl_attn}
    for reg in ("ffn", "attn"):
        # condition means (ladder)
        cond_means = {}
        for cond in ("plain", "cleft", "relcl"):
            vals = [d[cond] for d in complete]
            cond_means[cond] = {
                "zB": round(float(np.nanmean([v[f"{reg}_zB"] for v in vals])), 3),
                "zC": round(float(np.nanmean([v[f"{reg}_zC"] for v in vals])), 3),
                "Bprop": round(float(np.nanmean([v[f"{reg}_Bprop"] for v in vals])), 3),
                "Cprop": round(float(np.nanmean([v[f"{reg}_Cprop"] for v in vals])), 3),
            }
        block = {"condition_means": cond_means}
        for forced in ("cleft", "relcl"):
            dB = [d[forced][f"{reg}_zB"] - d["plain"][f"{reg}_zB"] for d in complete]
            dC = [d[forced][f"{reg}_zC"] - d["plain"][f"{reg}_zC"] for d in complete]
            dBp = [d[forced][f"{reg}_Bprop"] - d["plain"][f"{reg}_Bprop"]
                   for d in complete]
            block[f"{forced}_vs_plain"] = {
                "deltaB_raw": _wilcoxon(dB, "greater"),
                "deltaC_raw": _wilcoxon(dC, "less"),
                "deltaBprop": _wilcoxon(dBp, "greater"),
            }
        verdict[reg] = block
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
                   "zone_lo": zone_lo, "zone_hi": zone_hi, "max_triples": max_triples},
    }, indent=2), encoding="utf-8")
    print(f"\n[write] {RESULTS_DIR}/verdict_{slug}.json (+ per_item, meta)")
    return verdict


def _report(v):
    print("\n" + "═" * 78)
    print(f"VERDICT — {v['n_triples']} complete triples")
    print("═" * 78)
    print("Does forcing ∃ wide-scope RAISE z(B) (and lower z(C)) vs plain? "
          "(paired Wilcoxon)")
    for reg in ("ffn", "attn"):
        d = v[reg]
        cm = d["condition_means"]
        print(f"\n[{reg} register]  mean z by condition:")
        for cond in ("plain", "cleft", "relcl"):
            m = cm[cond]
            print(f"    {cond:6} z(B)={m['zB']:+.3f} z(C)={m['zC']:+.3f}  "
                  f"(Bprop={m['Bprop']:.3f} Cprop={m['Cprop']:.3f})")
        for forced in ("cleft", "relcl"):
            b = d[f"{forced}_vs_plain"]["deltaB_raw"]
            c = d[f"{forced}_vs_plain"]["deltaC_raw"]
            bp = d[f"{forced}_vs_plain"]["deltaBprop"]
            print(f"  {forced} vs plain: ΔB med={b['median']} "
                  f"(frac+={b.get('frac_predicted_sign')}, p={b['p']})  "
                  f"ΔC med={c['median']} (p={c['p']})  ΔBprop p={bp['p']}")
    print("═" * 78)


def main():
    ap = argparse.ArgumentParser(description="Scope-forcing experiment")
    ap.add_argument("--model", default="Qwen/Qwen3-8B")
    ap.add_argument("--zone-lo", type=float, default=0.70)
    ap.add_argument("--zone-hi", type=float, default=0.86)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    model_name = args.model
    if args.smoke:
        if model_name == "Qwen/Qwen3-8B":
            model_name = "Qwen/Qwen3-0.6B"
        n_perm_calib, ppc, null_cap, max_triples = 80, 4, 200, 8
        print("[smoke] mode")
    else:
        n_perm_calib, ppc, null_cap, max_triples = 300, None, None, None
    run(model_name, n_perm_calib, ppc, null_cap, args.zone_lo, args.zone_hi,
        max_triples)


if __name__ == "__main__":
    main()
