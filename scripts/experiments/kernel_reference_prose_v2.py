#!/usr/bin/env python3
# register: topological/routing
"""Kernel-reference PROSE bridge v2 — the B/D/W gap (s234, v5 lead 2d prong 1).

s233 lead 2c rescued composition SPECIFICITY (C, I discriminable) via a gauge-
subtracted contrast on the argmax-winner route_fracs. But the deep/duplicate composers
B/D/W STAYED flat (B DISCR -0.005, D -0.025, W 0.0; recall present for B at 0.3 but
on_prose ~= off_prose). HYPOTHESIS (the residual argmax bottleneck): route_fracs are
built from a PER-LAYER ARGMAX (`op = max(zmap)`) BEFORE the lead-2c contrast. B/D/W's
raw z is out-competed by the S/Y common-mode at EVERY layer -> route_frac ~= 0 -> the
on/off contrast has no power. This is the SAME "argmax manufactures false negatives when
one op has a big common-mode" theme (lead 2c, s225 AUC, lead-1 lambda-vs-control) pushed
ONE LEVEL DEEPER: lead 2c removed argmax at winner-SELECTION; route_frac still embeds
per-layer argmax.

THE FIX (this script): contrast on the RAW per-op z per layer, NO argmax.
  • discr_z(c) = layer-averaged raw z of op c on c-prose vs other-prose, Welch t-test.
  • per-layer PROFILE on_z/off_z/delta_z for each (combinator, crystal-layer): WHERE
    does C fire vs where SHOULD B fire? (localizes the gap).
  • keep the lead-2c argmax route_frac DISCR side-by-side -> direct before/after.
  • raise held-out N to 20 for power (counts allow: B=69 C=61 D=50 W=71 -> calib >=30).

VERDICT LOGIC (λ measure, two-sided):
  • B/D/W RECOVER under discr_z (significant on>off) -> the gap was an INSTRUMENT
    artifact (argmax bottleneck); composition routing is present, just sub-dominant.
  • B/D/W STAY flat under discr_z -> GENUINE: the deep/duplicate composers are not
    routed in this register at the last-token locus (escalate: per-token, composite
    trace-order).

Usage:
    uv run python scripts/experiments/kernel_reference_prose_v2.py --smoke
    uv run python scripts/experiments/kernel_reference_prose_v2.py --model Qwen/Qwen3-8B

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
    """Per-combinator: last `heldout_per` -> TEST, the rest -> CALIB (non-circular)."""
    by_comb: dict[str, list] = defaultdict(list)
    for p in crystal_probes():
        if p.combinator in CRYSTAL:
            by_comb[p.combinator].append(p)
    calib, test = [], []
    for comb, ps in by_comb.items():
        k = min(heldout_per, max(0, len(ps) - 1))
        test_ps = ps[len(ps) - k:] if k else []
        calib_ps = ps[: len(ps) - k]
        if comb in TEST_COMBINATORS:
            test.extend(test_ps)
        calib.extend(calib_ps)
    return calib, test


def read_last_token_z(rcc, store, layers) -> dict[int, dict[str, float]]:
    """Classify the LAST token; return the FULL per-layer per-op z-map (NO argmax)."""
    n = store[layers[0]].shape[0]
    gate_tok = {li: store[li][n - 1] for li in layers}
    tok_ops = rcc.classify(gate_tok)
    return tok_ops.per_layer  # {li: {op: z}}


def argmax_route_fracs(perlayer_z, crystal_layers, zthresh):
    """The lead-2c read: per-layer argmax, fraction of crystal layers won by each op."""
    cset = set(crystal_layers)
    counts: Counter = Counter()
    n_cells = 0
    for li, zmap in perlayer_z.items():
        if li not in cset:
            continue
        n_cells += 1
        op = max(zmap, key=zmap.get)
        if zmap[op] > zthresh:
            counts[op] += 1
    return ({op: counts[op] / n_cells for op in counts} if n_cells else {}), n_cells


def welch_t(on: list[float], off: list[float]) -> dict:
    """Welch's t (unequal variance) of mean(on) - mean(off)."""
    on_a, off_a = np.asarray(on, float), np.asarray(off, float)
    n1, n2 = len(on_a), len(off_a)
    m1, m2 = float(on_a.mean()), float(off_a.mean())
    if n1 < 2 or n2 < 2:
        return {"on_mean": round(m1, 4), "off_mean": round(m2, 4),
                "discr_z": round(m1 - m2, 4), "t": None, "significant": False,
                "n_on": n1, "n_off": n2}
    v1, v2 = float(on_a.var(ddof=1)), float(off_a.var(ddof=1))
    se = float(np.sqrt(v1 / n1 + v2 / n2))
    t = (m1 - m2) / se if se > 1e-12 else 0.0
    return {"on_mean": round(m1, 4), "off_mean": round(m2, 4),
            "discr_z": round(m1 - m2, 4), "t": round(t, 3),
            "significant": bool(abs(t) > 2.0), "n_on": n1, "n_off": n2}


def main() -> None:
    parser = argparse.ArgumentParser(description="Kernel-reference prose bridge v2")
    parser.add_argument("--model", default="Qwen/Qwen3-14B")
    parser.add_argument("--heldout-per", type=int, default=20)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    model_name = args.model
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        n_perm, ppc, null_cap, heldout = 80, 5, 200, 5
        print("[prose-v2] SMOKE MODE")
    else:
        n_perm, ppc, null_cap, heldout = 300, None, None, args.heldout_per

    calib, test = split_probes(heldout)
    print(f"[prose-v2] calib={len(calib)} test={len(test)} (heldout_per={heldout})")

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    layers = list(range(n_layers))

    rcc, cal = calibrate_v2(model, tok, torch_mod, layers, n_perm, ppc, null_cap,
                            null_mode="crosstask", centroid_probes=calib)
    crystal_layers = rcc.crystal_layers
    print(f"[prose-v2] crystal layers: {len(crystal_layers)}/{n_layers}")

    # read held-out prose: store the FULL per-layer z over crystal layers
    cset = set(crystal_layers)
    per_probe = []
    for p in test:
        store, _ = forward_all_positions(p.prompt, model, tok, torch_mod, layers)
        perlayer_z = read_last_token_z(rcc, store, layers)
        crystal_z = {li: {op: float(perlayer_z[li].get(op, 0.0)) for op in CRYSTAL}
                     for li in perlayer_z if li in cset}
        # layer-averaged raw z per op (the discr_z substrate, NO argmax)
        layer_avg = {op: float(np.mean([crystal_z[li][op] for li in crystal_z]))
                     for op in CRYSTAL} if crystal_z else {op: 0.0 for op in CRYSTAL}
        # argmax route_fracs per z (the lead-2c read, for direct comparison)
        argmax = {}
        for z in Z_SWEEP:
            fr, _ = argmax_route_fracs(perlayer_z, crystal_layers, z)
            argmax[f"z={z}"] = {op: round(fr.get(op, 0.0), 4) for op in CRYSTAL}
        per_probe.append({
            "combinator": p.combinator, "prompt": p.prompt[:60],
            "layer_avg_z": {op: round(v, 4) for op, v in layer_avg.items()},
            "argmax_route_fracs": argmax,
            "crystal_z": {str(li): {op: round(crystal_z[li][op], 3) for op in CRYSTAL}
                          for li in crystal_z},
        })

    # ── (1) discr_z(c): raw-z contrast, Welch t (NO argmax) ───────────────────────
    discr_z: dict[str, dict] = {}
    for c in CRYSTAL:
        on = [r["layer_avg_z"][c] for r in per_probe if r["combinator"] == c]
        off = [r["layer_avg_z"][c] for r in per_probe if r["combinator"] != c]
        if not on:
            continue
        discr_z[c] = welch_t(on, off)

    # ── (2) per-layer PROFILE: WHERE does each op discriminate? ────────────────────
    profile: dict[str, list] = {}
    peak: dict[str, dict] = {}
    for c in CRYSTAL:
        rows_on = [r for r in per_probe if r["combinator"] == c]
        rows_off = [r for r in per_probe if r["combinator"] != c]
        if not rows_on:
            continue
        prof = []
        for li in crystal_layers:
            sli = str(li)
            on_z = [r["crystal_z"][sli][c] for r in rows_on if sli in r["crystal_z"]]
            off_z = [r["crystal_z"][sli][c] for r in rows_off if sli in r["crystal_z"]]
            if not on_z:
                continue
            o, f = float(np.mean(on_z)), (float(np.mean(off_z)) if off_z else 0.0)
            prof.append({"layer": li, "on_z": round(o, 3), "off_z": round(f, 3),
                         "delta": round(o - f, 3)})
        profile[c] = prof
        if prof:
            pk = max(prof, key=lambda d: d["delta"])
            peak[c] = {"layer": pk["layer"], "delta": pk["delta"],
                       "on_z": pk["on_z"], "off_z": pk["off_z"]}

    # ── (3) argmax route_frac DISCR (lead-2c, side-by-side) ───────────────────────
    argmax_discr: dict[str, dict] = {}
    for z in Z_SWEEP:
        key = f"z={z}"
        ad: dict[str, dict] = {}
        for c in CRYSTAL:
            on = [r["argmax_route_fracs"][key][c]
                  for r in per_probe if r["combinator"] == c]
            off = [r["argmax_route_fracs"][key][c]
                   for r in per_probe if r["combinator"] != c]
            if not on:
                continue
            on_m, off_m = float(np.mean(on)), (float(np.mean(off)) if off else 0.0)
            ad[c] = {"on": round(on_m, 4), "off": round(off_m, 4),
                     "discr": round(on_m - off_m, 4),
                     "specific": bool(on_m - off_m > 0.05)}
        argmax_discr[key] = ad

    # ── verdict roll-up ───────────────────────────────────────────────────────────
    bdw_recovered = {c: bool(discr_z.get(c, {}).get("significant")
                             and discr_z.get(c, {}).get("discr_z", 0) > 0)
                     for c in ("B", "D", "W")}
    verdict = {
        "n_test": len(per_probe), "heldout_per": heldout,
        "discr_z": discr_z, "argmax_discr": argmax_discr,
        "peak_layer": peak,
        "bdw_recovered_under_discr_z": bdw_recovered,
        "n_discr_z_significant": sum(
            1 for c in CRYSTAL
            if discr_z.get(c, {}).get("significant")
            and discr_z.get(c, {}).get("discr_z", 0) > 0),
    }

    # ── report ────────────────────────────────────────────────────────────────────
    print("\n" + "═" * 78)
    print("KERNEL-REFERENCE PROSE BRIDGE v2 — raw-z contrast (NO argmax) vs argmax")
    print("═" * 78)
    print(f"  n_test={verdict['n_test']}  heldout_per={heldout}  "
          f"crystal_layers={len(crystal_layers)}")
    print(f"\n  {'op':<5}{'discr_z':>9}{'t':>8}{'sig':>5}  "
          f"{'(argmax z=2)':>13}{'peak_L':>8}{'peakΔ':>8}")
    a2 = argmax_discr.get("z=2.0", {})
    for c in CRYSTAL:
        dz = discr_z.get(c)
        if dz is None:
            continue
        ad = a2.get(c, {})
        pk = peak.get(c, {})
        sig = "✓" if dz["significant"] and dz["discr_z"] > 0 else "·"
        print(f"  {c:<5}{dz['discr_z']:>9}{(dz['t'] if dz['t'] is not None else 0):>8}"
              f"{sig:>5}  {ad.get('discr', 0):>13}"
              f"{pk.get('layer', '-'):>8}{pk.get('delta', '-'):>8}")
    print(f"\n  ★ B/D/W recovered under raw-z contrast: {bdw_recovered}")
    print(f"  ★ n_discr_z_significant (on>off, |t|>2): "
          f"{verdict['n_discr_z_significant']}")
    print("═" * 78 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    out = {"calibration_summary": cal, "verdict": verdict,
           "per_probe": per_probe, "profile": profile,
           "crystal_layers": crystal_layers}
    (RESULTS_DIR / f"prose_v2_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(out), indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "n_layers": n_layers, "n_perm": n_perm, "heldout_per": heldout,
        "n_calib": len(calib), "n_test": len(test), "z_sweep": Z_SWEEP,
        "metric": "raw-z layer-avg contrast (Welch t) + per-layer profile, NO argmax",
        "reference": "held-out crystal-prose combinator labels (non-circular split)",
    }
    (RESULTS_DIR / f"prose_v2_meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[prose-v2] wrote {RESULTS_DIR}/prose_v2_verdict_{slug}.json")


if __name__ == "__main__":
    main()
