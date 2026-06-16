#!/usr/bin/env python3
# register: topological/routing
"""Kernel-reference PROSE bridge v3 — the B LOCUS test (s234, v5 lead 2d prong 1b).

s234 prong 1 (v2) found the B/D/W gap GENUINE under the bottleneck-free raw-z contrast,
but at the LAST-TOKEN locus only. s127 (ffn-two-functional-groups) says {K,I}=selectors
->FFN, {B,C}=composers->ATTENTION. We read the FFN GATE -> K,I,C discriminable, B not.
TWO competing explanations for B's absence:
  (i)  TOKEN-LOCUS: B's composition resolves at a NON-last token; last-token misses it.
  (ii) REGISTER:    B lives in attention/value (s206), invisible to the FFN gate at
       ANY token -> escalate to a value-register read (prong 1b-ii).

This script falsifies (i) cheaply: forward_all_positions ALREADY returns [T, d] for
every token, so reading ALL positions costs the SAME forwards. Per probe per op:
  tokscore(c, t) = mean over crystal layers of raw z_c at token t (NO argmax).
  last_z(c) = tokscore at the last token (= the v2 baseline).
  max_z(c)  = max over tokens of tokscore  (does B fire ANYWHERE in the sentence?).
  mean_z(c) = mean over tokens of tokscore.
Contrast on-prose vs off-prose with a Welch t for last_z / max_z / mean_z. Plus a
relative-position PROFILE (binned t/(T-1)) to localize WHERE each op peaks.

VERDICT LOGIC (λ measure, two-sided):
  • B RECOVERS under max_z/mean_z (sig on>off) -> the gap was TOKEN-LOCUS; B fires
    mid-sentence. Report the peak relative position.
  • B STAYS flat at ALL positions -> falsifies token-locus; B absent from the FFN gate
    entirely -> the REGISTER explanation holds -> build value/attention read (1b-ii).

Usage:
    uv run python scripts/experiments/kernel_reference_prose_v3.py --smoke
    uv run python scripts/experiments/kernel_reference_prose_v3.py --model Qwen/Qwen3-8B

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))
sys.path.insert(0, str(_ROOT / "scripts" / "instruments"))

from kernel_reference_prose_v2 import (  # noqa: E402
    TEST_COMBINATORS,
    split_probes,
    welch_t,
)
from opcode_monitor_v2 import (  # noqa: E402
    _git_sha,
    _json_safe,
    _transformers_version,
    calibrate_v2,
    forward_all_positions,
    load_model_and_tokenizer,
)
from relational_opcode import CRYSTAL  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "kernel-reference-audit"
N_POS_BINS = 10  # relative-position profile resolution


def read_all_tokens(rcc, store, layers, crystal_layers) -> dict:
    """Per token: layer-averaged raw z per op over crystal layers (NO argmax).

    Returns {op: {"last": float, "max": float, "mean": float, "peak_rel": float,
                  "by_bin": [N_POS_BINS]}}.
    """
    cset = set(crystal_layers)
    n = store[layers[0]].shape[0]
    # tokscore[op] = list over tokens of mean-over-crystal-layers z_c
    tokscore: dict[str, list[float]] = {op: [] for op in CRYSTAL}
    for t in range(n):
        gate_tok = {li: store[li][t] for li in layers}
        per_layer = rcc.classify(gate_tok).per_layer
        for op in CRYSTAL:
            zs = [float(per_layer[li][op]) for li in per_layer if li in cset]
            tokscore[op].append(float(np.mean(zs)) if zs else 0.0)
    out: dict = {}
    for op in CRYSTAL:
        arr = np.asarray(tokscore[op], float)
        peak_t = int(np.argmax(arr))
        rel = peak_t / (n - 1) if n > 1 else 0.0
        # binned profile by relative position
        bins = [[] for _ in range(N_POS_BINS)]
        for t in range(n):
            r = t / (n - 1) if n > 1 else 0.0
            b = min(N_POS_BINS - 1, int(r * N_POS_BINS))
            bins[b].append(arr[t])
        by_bin = [round(float(np.mean(b)), 3) if b else None for b in bins]
        out[op] = {"last": round(float(arr[-1]), 4), "max": round(float(arr.max()), 4),
                   "mean": round(float(arr.mean()), 4), "peak_rel": round(rel, 3),
                   "by_bin": by_bin}
    return out


def contrast(per_probe: list, field: str) -> dict[str, dict]:
    """Welch t of field (last/max/mean) on-prose vs off-prose, per op."""
    res: dict[str, dict] = {}
    for c in CRYSTAL:
        on = [r["ops"][c][field] for r in per_probe if r["combinator"] == c]
        off = [r["ops"][c][field] for r in per_probe if r["combinator"] != c]
        if not on:
            continue
        res[c] = welch_t(on, off)
    return res


def main() -> None:
    parser = argparse.ArgumentParser(description="Kernel-ref prose bridge v3 (locus)")
    parser.add_argument("--model", default="Qwen/Qwen3-14B")
    parser.add_argument("--heldout-per", type=int, default=20)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    model_name = args.model
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        n_perm, ppc, null_cap, heldout = 80, 5, 200, 5
        print("[prose-v3] SMOKE MODE")
    else:
        n_perm, ppc, null_cap, heldout = 300, None, None, args.heldout_per

    calib, test = split_probes(heldout)
    print(f"[prose-v3] calib={len(calib)} test={len(test)} (heldout_per={heldout})")

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    layers = list(range(n_layers))

    rcc, cal = calibrate_v2(model, tok, torch_mod, layers, n_perm, ppc, null_cap,
                            null_mode="crosstask", centroid_probes=calib)
    crystal_layers = rcc.crystal_layers
    print(f"[prose-v3] crystal layers: {len(crystal_layers)}/{n_layers}")

    per_probe = []
    for p in test:
        store, _ = forward_all_positions(p.prompt, model, tok, torch_mod, layers)
        ops = read_all_tokens(rcc, store, layers, crystal_layers)
        per_probe.append({"combinator": p.combinator, "prompt": p.prompt[:60],
                          "ops": ops})

    discr_last = contrast(per_probe, "last")
    discr_max = contrast(per_probe, "max")
    discr_mean = contrast(per_probe, "mean")

    # relative-position profile per op: on-prose vs off-prose binned mean
    profile: dict[str, dict] = {}
    for c in CRYSTAL:
        on_rows = [r for r in per_probe if r["combinator"] == c]
        off_rows = [r for r in per_probe if r["combinator"] != c]
        if not on_rows:
            continue

        def binmean(rows, op):
            cols = [[] for _ in range(N_POS_BINS)]
            for r in rows:
                for b, v in enumerate(r["ops"][op]["by_bin"]):
                    if v is not None:
                        cols[b].append(v)
            return [round(float(np.mean(c2)), 3) if c2 else None for c2 in cols]

        on_peak = [r["ops"][c]["peak_rel"] for r in on_rows]
        profile[c] = {"on_by_bin": binmean(on_rows, c),
                      "off_by_bin": binmean(off_rows, c),
                      "on_peak_rel_mean": round(float(np.mean(on_peak)), 3),
                      "on_peak_rel_median": round(float(np.median(on_peak)), 3)}

    def recovered(d):
        return {c: bool(d.get(c, {}).get("significant")
                        and d.get(c, {}).get("discr_z", 0) > 0)
                for c in ("B", "D", "W")}

    verdict = {
        "n_test": len(per_probe), "heldout_per": heldout,
        "discr_last": discr_last, "discr_max": discr_max, "discr_mean": discr_mean,
        "bdw_recovered": {"last": recovered(discr_last), "max": recovered(discr_max),
                          "mean": recovered(discr_mean)},
        "peak_rel": {c: profile[c]["on_peak_rel_median"]
                     for c in profile if c in TEST_COMBINATORS},
    }

    print("\n" + "═" * 80)
    print("KERNEL-REFERENCE PROSE BRIDGE v3 — per-token B LOCUS test")
    print("═" * 80)
    print(f"  n_test={verdict['n_test']}  heldout_per={heldout}  "
          f"crystal_layers={len(crystal_layers)}")
    hdr = (f"\n  {'op':<4}"
           f"{'last_d':>8}{'t':>7} | {'max_d':>8}{'t':>7} | {'mean_d':>8}{'t':>7} | "
           f"{'peakRel':>8}")
    print(hdr)
    for c in CRYSTAL:
        dl, dm, dme = discr_last.get(c), discr_max.get(c), discr_mean.get(c)
        if dl is None:
            continue
        pr = profile.get(c, {}).get("on_peak_rel_median", "-")

        def fmt(d):
            s = "✓" if d["significant"] and d["discr_z"] > 0 else " "
            return f"{d['discr_z']:>8}{(d['t'] or 0):>6}{s}"
        print(f"  {c:<4}{fmt(dl)} | {fmt(dm)} | {fmt(dme)} | {pr:>8}")
    print(f"\n  ★ B/D/W recovered:  last={verdict['bdw_recovered']['last']}")
    print(f"                      max ={verdict['bdw_recovered']['max']}")
    print(f"                      mean={verdict['bdw_recovered']['mean']}")
    print("═" * 80 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    out = {"calibration_summary": cal, "verdict": verdict, "profile": profile,
           "per_probe": per_probe, "crystal_layers": crystal_layers}
    (RESULTS_DIR / f"prose_v3_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(out), indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "n_layers": n_layers, "n_perm": n_perm, "heldout_per": heldout,
        "n_calib": len(calib), "n_test": len(test),
        "metric": "per-token raw-z (last/max/mean) Welch contrast + position profile",
        "reference": "held-out crystal-prose combinator labels (non-circular split)",
    }
    (RESULTS_DIR / f"prose_v3_meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[prose-v3] wrote {RESULTS_DIR}/prose_v3_verdict_{slug}.json")


if __name__ == "__main__":
    main()
