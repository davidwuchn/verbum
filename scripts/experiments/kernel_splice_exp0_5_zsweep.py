#!/usr/bin/env python3
# register: topological/routing
"""Kernel-splice Exp 0.5 — the Z-THRESHOLD SWEEP (s243).

Exp 0 (kernel_splice_exp0_detectability.py) read the lattice with an UNGATED top-1:
every crystal layer always emits its argmax-over-CRYSTAL prediction. Verdict: the
strict bar (prec>=0.8 ∧ rec>=0.5) was cleared by NOBODY (top-1 is common-mode
contaminated, s211 one-common-mode), BUT the max-PRECISION operating points were
strong (C prec 1.0 @L10, I 1.0 @L21, K 0.80 @L11, Y 0.67 @L20). The caveat
(λ measure): those prec-1.0 points came from tp=2 — noisy small-n. A single lucky
layer is not a splice locus.

THIS SCRIPT raises the argmax-z GATE: a layer emits a prediction for combinator c only
if its winning z exceeds a threshold τ; below τ it ABSTAINS (no splice fires). Sweeping
τ traces the precision↑/recall↓ tradeoff. The deliverables:

  • the PRECISION/RECALL CURVE per splice-target {C,I,K,Y} as τ rises;
  • the FIRMED OPERATING POINT = the (layer, τ) with MAX recall (=> max tp, most
    samples) that still clears the precision floor — the most-supported splice locus,
    which kills the tp=2 small-n caveat if it exists;
  • a PLATEAU check: is high precision STABLE across a band of τ (real) or a single
    fragile point (a tp=2 fluke)?

It also bumps --heldout-per (more TEST probes per combinator) to grow tp directly,
since crystal_probes carries 50 to 71 per crystal combinator.

The forward pass runs ONCE; the threshold sweep is pure post-processing over the cached
per-probe per-layer z-maps. Same last-token, single-combinator-prompt read as Exp 0 /
prose_v2 (non-circular held-out split).

VERDICT (λ measure): a firmed (layer, τ) with precision >= floor at usable recall and
tp well above the small-n caveat => Exp 1 (causal K-splice) is justified at that locus.
A precision that only ever appears at tp<=2 with no plateau => obstacle 1 (model
centroid) is fatal for in-place per-combinator splice; redirect to the program-decode
variant or constructed front-end.

Usage:
    uv run python scripts/experiments/kernel_splice_exp0_5_zsweep.py --smoke
    uv run python scripts/experiments/kernel_splice_exp0_5_zsweep.py \
        --model Qwen/Qwen3-14B --heldout-per 25

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))
sys.path.insert(0, str(_ROOT / "scripts" / "instruments"))

from kernel_reference_prose_v2 import read_last_token_z, split_probes  # noqa: E402
from opcode_monitor_v2 import (  # noqa: E402
    _git_sha,
    _json_safe,
    _transformers_version,
    calibrate_v2,
    forward_all_positions,
    load_model_and_tokenizer,
)
from relational_opcode import CRYSTAL  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "kernel-splice-exp0"

# the invariant discriminable set we care about for splicing (s234/s238).
SPLICE_TARGETS = ["C", "I", "K", "Y"]

# default z-gate grid (argmax-z is a sign-CMR raw-z; magnitudes ~0 to 10).
DEFAULT_THRESHOLDS = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 8.0]


def gated_pred(zmap: dict[str, float], tau: float) -> str | None:
    """Top-1 op at a layer, GATED: argmax over CRYSTAL iff its z > tau, else abstain."""
    if not zmap:
        return None
    op = max(CRYSTAL, key=lambda o: zmap.get(o, float("-inf")))
    return op if zmap.get(op, float("-inf")) > tau else None


def prf(tp: int, fp: int, fn: int) -> dict[str, float]:
    """Precision / recall / F1 from raw counts."""
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4)}


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Kernel-splice Exp 0.5 — z-threshold sweep")
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--heldout-per", type=int, default=25,
                    help="TEST probes per combinator (more = larger tp, kills small-n)")
    ap.add_argument("--precision-floor", type=float, default=0.8,
                    help="min precision to count a (layer,tau) operating point")
    ap.add_argument("--thresholds", type=float, nargs="+", default=None,
                    help="z-gate grid (default: 0..8 ladder)")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    thresholds = sorted(args.thresholds if args.thresholds else DEFAULT_THRESHOLDS)
    model_name = args.model
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        n_perm, ppc, null_cap, heldout = 80, 5, 200, 5
        print("[exp0.5] SMOKE MODE")
    else:
        n_perm, ppc, null_cap, heldout = 300, None, None, args.heldout_per

    calib, test = split_probes(heldout)
    print(f"[exp0.5] calib={len(calib)} test={len(test)} (heldout_per={heldout})")

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    layers = list(range(n_layers))

    rcc, cal = calibrate_v2(model, tok, torch_mod, layers, n_perm, ppc, null_cap,
                            null_mode="crosstask", centroid_probes=calib)
    crystal_layers = rcc.crystal_layers
    print(f"[exp0.5] crystal layers: {len(crystal_layers)}/{n_layers}")

    # ── ONE forward pass per probe: cache the full per-layer z-map ──────────────────
    support: dict[str, int] = defaultdict(int)
    cached: list[tuple[str, dict[int, dict[str, float]]]] = []
    argmax_z_all: list[float] = []  # to report the observed gate distribution
    for i, p in enumerate(test):
        support[p.combinator] += 1
        store, _ = forward_all_positions(p.prompt, model, tok, torch_mod, layers)
        perlayer_z = read_last_token_z(rcc, store, layers)
        zc = {li: perlayer_z[li] for li in crystal_layers if li in perlayer_z}
        cached.append((p.combinator, zc))
        for zmap in zc.values():
            if zmap:
                argmax_z_all.append(max(zmap.values()))
        if (i + 1) % 20 == 0:
            print(f"[exp0.5] forward {i + 1}/{len(test)}")

    # ── SWEEP: per (combinator, layer, τ) precision/recall/F1 with abstention ───────
    # curve[c] = list over τ of the best-layer operating point at that τ.
    curve: dict[str, list] = {c: [] for c in SPLICE_TARGETS}
    # grid[c] = every (layer, τ) point clearing prec floor, for operating-point search.
    grid_points: dict[str, list] = {c: [] for c in SPLICE_TARGETS}

    for tau in thresholds:
        # confusion[li][true][pred] for this τ
        conf: dict[int, dict[str, dict[str, int]]] = {
            li: {t: defaultdict(int) for t in CRYSTAL} for li in crystal_layers
        }
        for true_c, zc in cached:
            for li in crystal_layers:
                pred = gated_pred(zc.get(li, {}), tau)
                if pred is not None:
                    conf[li][true_c][pred] += 1
        for c in SPLICE_TARGETS:
            best = None
            for li in crystal_layers:
                tp = conf[li][c][c]
                fp = sum(conf[li][t][c] for t in CRYSTAL if t != c)
                fn = support[c] - tp  # abstentions on true-c count as missed
                m = prf(tp, fp, fn)
                pt = {"layer": li, "tau": tau, "tp": tp, "fp": fp, "fn": fn, **m}
                if m["precision"] >= args.precision_floor and tp > 0:
                    grid_points[c].append(pt)
                # best-layer at this τ = max precision, tie-break recall then tp
                key = (m["precision"], m["recall"], tp)
                bkey = (best["precision"], best["recall"], best["tp"]) if best else None
                if best is None or key > bkey:
                    best = pt
            curve[c].append(best)

    # ── operating points + plateau check ───────────────────────────────────────────
    n_layers_minus = max(1, n_layers - 1)
    operating: dict[str, dict] = {}
    for c in SPLICE_TARGETS:
        pts = grid_points[c]
        if not pts:
            operating[c] = {
                "clears_floor": False, "support": support[c],
                "reason": f"no (layer,tau) reaches precision>={args.precision_floor}"}
            continue
        # firmest locus = MAX recall (=> max tp) clearing the floor; tie-break precision
        firm = max(pts, key=lambda r: (r["recall"], r["precision"], -r["tau"]))
        # max-precision locus (compare to Exp 0's prec-1.0 small-n points)
        maxprec = max(pts, key=lambda r: (r["precision"], r["recall"], r["tp"]))
        # plateau: distinct τ values at the firm locus's LAYER that still clear floor
        layer_band = sorted({r["tau"] for r in pts if r["layer"] == firm["layer"]})
        operating[c] = {
            "clears_floor": True,
            "support": support[c],
            "firm_locus": {
                "layer": firm["layer"], "tau": firm["tau"],
                "frac_depth": round(firm["layer"] / n_layers_minus, 3),
                "precision": firm["precision"], "recall": firm["recall"],
                "f1": firm["f1"], "tp": firm["tp"], "fp": firm["fp"], "fn": firm["fn"],
            },
            "max_precision_locus": {
                "layer": maxprec["layer"], "tau": maxprec["tau"],
                "precision": maxprec["precision"], "recall": maxprec["recall"],
                "tp": maxprec["tp"], "fp": maxprec["fp"],
            },
            "plateau_taus_at_firm_layer": layer_band,
            "plateau_width": len(layer_band),
            "small_n_caveat_killed": bool(firm["tp"] >= 5),
        }

    # observed argmax-z distribution (calibrates the grid)
    zarr = sorted(argmax_z_all)
    n = len(zarr)
    def q(p: float) -> float:
        return round(zarr[min(n - 1, int(p * n))], 3) if n else 0.0
    z_dist = {"n": n, "min": round(zarr[0], 3) if n else 0.0,
              "p25": q(0.25), "median": q(0.5), "p75": q(0.75),
              "p90": q(0.9), "max": round(zarr[-1], 3) if n else 0.0}

    verdict = {
        "model": model_name, "n_test": len(cached),
        "n_layers": n_layers, "crystal_layers": crystal_layers,
        "support": dict(support), "thresholds": thresholds,
        "precision_floor": args.precision_floor,
        "argmax_z_distribution": z_dist,
        "operating_points": operating,
        "splice_ready_set": [c for c in SPLICE_TARGETS
                             if operating.get(c, {}).get("clears_floor")
                             and operating[c].get("small_n_caveat_killed")],
    }

    # ── report ──────────────────────────────────────────────────────────────────────
    print("\n" + "═" * 82)
    print(f"KERNEL-SPLICE EXP 0.5 — Z-THRESHOLD SWEEP — {model_name}")
    print("═" * 82)
    print(f"  n_test={len(cached)}  crystal_layers={len(crystal_layers)}/{n_layers}"
          f"  prec_floor={args.precision_floor}")
    print(f"  argmax-z dist: median={z_dist['median']} p75={z_dist['p75']} "
          f"p90={z_dist['p90']} max={z_dist['max']}")
    for c in SPLICE_TARGETS:
        print(f"\n  ── {c}  (support={support.get(c, 0)}) ─ precision/recall vs τ "
              f"(best layer @τ) ──")
        print(f"     {'τ':>5}{'layer':>7}{'prec':>7}{'recall':>8}{'tp':>5}{'fp':>5}")
        for pt in curve[c]:
            print(f"     {pt['tau']:>5.1f}{pt['layer']:>7}{pt['precision']:>7.2f}"
                  f"{pt['recall']:>8.2f}{pt['tp']:>5}{pt['fp']:>5}")
        op = operating[c]
        if op["clears_floor"]:
            f = op["firm_locus"]
            print(f"     ★ FIRM locus: L{f['layer']} (d={f['frac_depth']}) "
                  f"τ={f['tau']} "
                  f"prec={f['precision']} rec={f['recall']} tp={f['tp']} "
                  f"| plateau τ∈{op['plateau_taus_at_firm_layer']} "
                  f"| small-n killed={op['small_n_caveat_killed']}")
        else:
            print(f"     ✗ never clears precision>={args.precision_floor}")
    print(f"\n  ★ splice-ready (clears floor ∧ tp>=5): "
          f"{verdict['splice_ready_set'] or '∅'}")
    print("═" * 82 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    out = {"verdict": verdict, "pr_curve": curve, "calibration_summary": cal}
    (RESULTS_DIR / f"exp0_5_zsweep_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(out), indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "n_layers": n_layers, "n_perm": n_perm, "heldout_per": heldout,
        "n_calib": len(calib), "n_test": len(test), "thresholds": thresholds,
        "metric": "GATED top-1: argmax-over-CRYSTAL per crystal layer iff z>τ else "
                  "abstain; precision/recall/F1 swept over τ; firm locus = max-recall "
                  "point clearing precision floor",
        "reference": "held-out crystal-prose combinator labels (non-circular split)",
    }
    (RESULTS_DIR / f"exp0_5_zsweep_meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[exp0.5] wrote {RESULTS_DIR}/exp0_5_zsweep_verdict_{slug}.json")


if __name__ == "__main__":
    main()
