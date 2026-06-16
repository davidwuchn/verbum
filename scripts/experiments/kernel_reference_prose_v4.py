#!/usr/bin/env python3
# register: value/attention (o_proj) — vs FFN gate
"""Kernel-ref PROSE bridge v4 — the VALUE-REGISTER read (s234 v5 lead 2d prong 1b-ii).

Prongs 1 + 1b found the B/D/W gap GENUINE and a REGISTER property of the FFN gate, NOT a
token-locus artifact (B flat at ALL positions; max-over-tokens t=0.68 n.s.). s127
(ffn-two-functional-groups): {K,I}=selectors->FFN, {B,C}=composers->ATTENTION. We read
the FFN GATE -> {C,I,K} present, B absent. THE DECISIVE TEST: read the crystal in the
ATTENTION/value register (s206 OV/logit-lens) — does B appear where the gate cannot?

Reuses the WHOLE machinery via the new `hook='attn'` slot in opcode_monitor_v2
(self_attn.o_proj output = attention's residual write). Same calibration (per-layer
crystal centroids, sign-CMR, crosstask null), same per-token raw-z contrast + position
profile as v3 — only the REGISTER changes. Direct comparison to v2/v3 (FFN gate).

VERDICT LOGIC (λ measure, two-sided):
  • B RECOVERS in attention (sig on>off where the FFN gate was flat) -> CONFIRMS s127:
    B is a composer that lives in attention; the C-yes/B-no gate split is a REGISTER
    split, not "B isn't computed."
  • B STAYS flat in attention too -> B not localized in either single register at the
    last/any token (escalate: per-head OV, composite trace-order, or B is diffuse).

Usage:
    uv run python scripts/experiments/kernel_reference_prose_v4.py --smoke
    uv run python scripts/experiments/kernel_reference_prose_v4.py --register gate

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
)
from kernel_reference_prose_v3 import (  # noqa: E402
    N_POS_BINS,
    contrast,
    read_all_tokens,
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


def build_profile(per_probe: list) -> dict[str, dict]:
    """Relative-position profile per op: on/off-prose binned mean + peak_rel."""
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
    return profile


def main() -> None:
    parser = argparse.ArgumentParser(description="Kernel-ref prose v4 (register)")
    parser.add_argument("--model", default="Qwen/Qwen3-14B")
    parser.add_argument("--register", default="attn", choices=["attn", "gate"])
    parser.add_argument("--heldout-per", type=int, default=20)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    register = args.register
    model_name = args.model
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        n_perm, ppc, null_cap, heldout = 80, 5, 200, 5
        print(f"[prose-v4] SMOKE MODE  register={register}")
    else:
        n_perm, ppc, null_cap, heldout = 300, None, None, args.heldout_per

    calib, test = split_probes(heldout)
    print(f"[prose-v4] register={register} calib={len(calib)} test={len(test)} "
          f"(heldout_per={heldout})")

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    layers = list(range(n_layers))

    rcc, cal = calibrate_v2(model, tok, torch_mod, layers, n_perm, ppc, null_cap,
                            null_mode="crosstask", centroid_probes=calib, hook=register)
    crystal_layers = rcc.crystal_layers
    print(f"[prose-v4] crystal layers: {len(crystal_layers)}/{n_layers}")

    per_probe = []
    for p in test:
        store, _ = forward_all_positions(p.prompt, model, tok, torch_mod, layers,
                                         hook=register)
        ops = read_all_tokens(rcc, store, layers, crystal_layers)
        per_probe.append({"combinator": p.combinator, "prompt": p.prompt[:60],
                          "ops": ops})

    discr_last = contrast(per_probe, "last")
    discr_max = contrast(per_probe, "max")
    discr_mean = contrast(per_probe, "mean")
    profile = build_profile(per_probe)

    def recovered(d):
        return {c: bool(d.get(c, {}).get("significant")
                        and d.get(c, {}).get("discr_z", 0) > 0)
                for c in ("B", "C", "D", "W")}

    verdict = {
        "register": register, "n_test": len(per_probe), "heldout_per": heldout,
        "discr_last": discr_last, "discr_max": discr_max, "discr_mean": discr_mean,
        "recovered": {"last": recovered(discr_last), "max": recovered(discr_max),
                      "mean": recovered(discr_mean)},
        "peak_rel": {c: profile[c]["on_peak_rel_median"]
                     for c in profile if c in TEST_COMBINATORS},
        "b_appears_in_attn": bool(
            register == "attn"
            and (discr_max.get("B", {}).get("significant")
                 and discr_max.get("B", {}).get("discr_z", 0) > 0)),
    }

    print("\n" + "═" * 80)
    print(f"KERNEL-REFERENCE PROSE BRIDGE v4 — register={register.upper()} "
          f"(o_proj=attn vs gate_proj=FFN)")
    print("═" * 80)
    print(f"  n_test={verdict['n_test']}  heldout_per={heldout}  "
          f"crystal_layers={len(crystal_layers)}")
    print(f"\n  {'op':<4}"
          f"{'last_d':>8}{'t':>7} | {'max_d':>8}{'t':>7} | {'mean_d':>8}{'t':>7} | "
          f"{'peakRel':>8}")
    for c in CRYSTAL:
        dl, dm, dme = discr_last.get(c), discr_max.get(c), discr_mean.get(c)
        if dl is None:
            continue
        pr = profile.get(c, {}).get("on_peak_rel_median", "-")

        def fmt(d):
            s = "✓" if d["significant"] and d["discr_z"] > 0 else " "
            return f"{d['discr_z']:>8}{(d['t'] or 0):>6}{s}"
        print(f"  {c:<4}{fmt(dl)} | {fmt(dm)} | {fmt(dme)} | {pr:>8}")
    print(f"\n  ★ recovered (sig on>off):  last={verdict['recovered']['last']}")
    print(f"                             max ={verdict['recovered']['max']}")
    print(f"                             mean={verdict['recovered']['mean']}")
    print(f"  ★ B appears in ATTENTION register: {verdict['b_appears_in_attn']}")
    print("═" * 80 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    out = {"calibration_summary": cal, "verdict": verdict, "profile": profile,
           "per_probe": per_probe, "crystal_layers": crystal_layers}
    (RESULTS_DIR / f"prose_v4_{register}_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(out), indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "register": register, "smoke": args.smoke,
        "git_sha": _git_sha(), "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "n_layers": n_layers, "n_perm": n_perm, "heldout_per": heldout,
        "n_calib": len(calib), "n_test": len(test),
        "metric": "per-token raw-z (last/max/mean) Welch contrast, ATTN/value register",
        "reference": "held-out crystal-prose combinator labels (non-circular split)",
    }
    (RESULTS_DIR / f"prose_v4_{register}_meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[prose-v4] wrote {RESULTS_DIR}/prose_v4_{register}_verdict_{slug}.json")


if __name__ == "__main__":
    main()
