#!/usr/bin/env python3
# register: topological/routing
"""Kernel-splice Exp 0 — the DETECTABILITY MAP (s242).

The precursor to the kernel-splice program (knowledge/explore/kernel-splice-geometry-
detector.md): before we can DELIVER a combinator from the kernel at the geometrically-
detected locus, we must know WHERE and WHICH combinators the lattice classifier can
recover RELIABLY ENOUGH TO ACT ON. Discriminability (prose_v2: a Welch contrast,
on-prose > off-prose) is necessary but NOT sufficient for a splice: a splice acts on a
TOP-1 decision at a specific layer, so what matters is per-combinator **precision**
(when we read "K", is it really K? — a wrong splice corrupts) and **recall** (do we
catch the K firings?) at the best single layer.

THIS SCRIPT turns the prose_v2 read into a SPLICE-READINESS MAP:
  • reuse the prose_v2 / opcode_monitor_v2 calibration + last-token per-layer z read;
  • per crystal layer, predicted op = argmax over CRYSTAL of the classifier z;
  • score the top-1 prediction against the certified single-combinator label
    (crystal_probes .combinator — each probe engages exactly one combinator);
  • per (combinator, layer): precision / recall / F1 + a confusion matrix;
  • peak layer per combinator = max F1; splice-ready iff precision >= --precision-floor
    AND recall >= --recall-floor at the peak.

VERDICT (λ measure): which of the invariant discriminable set {C,I,K,Y} clear the
splice-readiness bar, at which per-model layer. High precision => Exp 1 (causal
K-splice) is justified at that locus; nothing clears the bar => obstacle 1 (model
centroid, s211 one-common-mode) is FATAL for in-place per-combinator splice, redirect to
the cut/program-decode variant (Exp 2) or the constructed front-end.

NOTE: this is the LAST-TOKEN, single-combinator-prompt read (same locus as prose_v2).
Position-resolved detection along a multi-step reduction (operator AND position vs
`lambda_ast.fired_sequence`) is Exp 2; Exp 0 first establishes per-op splice-readiness
at all, cheaply, on the labels we already trust.

Usage:
    uv run python scripts/experiments/kernel_splice_exp0_detectability.py --smoke
    uv run python scripts/experiments/kernel_splice_exp0_detectability.py \
        --model Qwen/Qwen3-14B --heldout-per 20

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

# the invariant discriminable set we care about for splicing (s234/s238); we still
# score the full CRYSTAL confusion so the common-mode contaminants (S/Y) are visible.
SPLICE_TARGETS = ["C", "I", "K", "Y"]


def predicted_op(zmap: dict[str, float]) -> str:
    """Top-1 op at a layer = argmax of the classifier z over CRYSTAL."""
    return max(CRYSTAL, key=lambda op: zmap.get(op, float("-inf")))


def prf(tp: int, fp: int, fn: int) -> dict[str, float]:
    """Precision / recall / F1 from raw counts."""
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4)}


def main() -> None:
    ap = argparse.ArgumentParser(description="Kernel-splice Exp 0 — detectability map")
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--heldout-per", type=int, default=20)
    ap.add_argument("--precision-floor", type=float, default=0.8,
                    help="min top-1 precision at peak layer to call splice-ready")
    ap.add_argument("--recall-floor", type=float, default=0.5,
                    help="min recall at peak layer to call a combinator splice-ready")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    model_name = args.model
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        n_perm, ppc, null_cap, heldout = 80, 5, 200, 5
        print("[exp0] SMOKE MODE")
    else:
        n_perm, ppc, null_cap, heldout = 300, None, None, args.heldout_per

    calib, test = split_probes(heldout)
    print(f"[exp0] calib={len(calib)} test={len(test)} (heldout_per={heldout})")

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    layers = list(range(n_layers))

    rcc, cal = calibrate_v2(model, tok, torch_mod, layers, n_perm, ppc, null_cap,
                            null_mode="crosstask", centroid_probes=calib)
    crystal_layers = rcc.crystal_layers
    print(f"[exp0] crystal layers: {len(crystal_layers)}/{n_layers}")

    # per layer: confusion[li][true][pred] = count
    confusion: dict[int, dict[str, dict[str, int]]] = {
        li: {t: defaultdict(int) for t in CRYSTAL} for li in crystal_layers
    }
    support: dict[str, int] = defaultdict(int)
    per_probe = []
    for p in test:
        support[p.combinator] += 1
        store, _ = forward_all_positions(p.prompt, model, tok, torch_mod, layers)
        perlayer_z = read_last_token_z(rcc, store, layers)
        preds = {}
        for li in crystal_layers:
            if li in perlayer_z:
                pred = predicted_op(perlayer_z[li])
                confusion[li][p.combinator][pred] += 1
                preds[li] = pred
        per_probe.append({"combinator": p.combinator, "prompt": p.prompt[:60],
                          "preds": {str(li): preds[li] for li in preds}})

    # per (combinator, layer): precision/recall/F1 from the confusion matrix
    per_comb_layer: dict[str, list] = {}
    peak: dict[str, dict] = {}
    for c in CRYSTAL:
        rows = []
        for li in crystal_layers:
            tp = confusion[li][c][c]
            fn = support[c] - tp
            fp = sum(confusion[li][t][c] for t in CRYSTAL if t != c)
            m = prf(tp, fp, fn)
            rows.append({"layer": li, "tp": tp, "fp": fp, "fn": fn, **m})
        per_comb_layer[c] = rows
        scored = [r for r in rows if support[c] > 0]
        if scored:
            pk = max(scored, key=lambda r: (r["f1"], r["recall"]))
            peak[c] = pk

    # splice-readiness verdict
    readiness: dict[str, dict] = {}
    for c in SPLICE_TARGETS:
        pk = peak.get(c)
        if not pk or support[c] == 0:
            readiness[c] = {"splice_ready": False, "reason": "no support/peak"}
            continue
        ready = (pk["precision"] >= args.precision_floor
                 and pk["recall"] >= args.recall_floor)
        readiness[c] = {
            "splice_ready": bool(ready), "peak_layer": pk["layer"],
            "precision": pk["precision"], "recall": pk["recall"], "f1": pk["f1"],
            "support": support[c],
            "frac_depth": round(pk["layer"] / max(1, n_layers - 1), 3),
        }

    verdict = {
        "model": model_name, "n_test": len(per_probe),
        "n_layers": n_layers, "crystal_layers": crystal_layers,
        "support": dict(support),
        "precision_floor": args.precision_floor, "recall_floor": args.recall_floor,
        "splice_readiness": readiness,
        "peak_per_combinator": peak,
        "splice_ready_set": [c for c in SPLICE_TARGETS
                             if readiness.get(c, {}).get("splice_ready")],
    }

    # ── report ────────────────────────────────────────────────────────────────────
    print("\n" + "═" * 78)
    print(f"KERNEL-SPLICE EXP 0 — DETECTABILITY MAP — {model_name}")
    print("═" * 78)
    print(f"  n_test={len(per_probe)}  crystal_layers={len(crystal_layers)}/{n_layers}"
          f"  floors: prec>={args.precision_floor} rec>={args.recall_floor}")
    print(f"\n  {'op':<4}{'support':>8}{'peakL':>7}{'depth':>7}"
          f"{'prec':>8}{'recall':>8}{'f1':>7}{'splice?':>9}")
    for c in SPLICE_TARGETS:
        r = readiness.get(c, {})
        if "peak_layer" not in r:
            print(f"  {c:<4}{support.get(c, 0):>8}{'-':>7}{'-':>7}"
                  f"{'-':>8}{'-':>8}{'-':>7}{'no':>9}")
            continue
        flag = "✓ READY" if r["splice_ready"] else "·"
        print(f"  {c:<4}{r['support']:>8}{r['peak_layer']:>7}{r['frac_depth']:>7}"
              f"{r['precision']:>8}{r['recall']:>8}{r['f1']:>7}{flag:>9}")
    print(f"\n  ★ splice-ready set: {verdict['splice_ready_set'] or '∅'}")
    print("═" * 78 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    out = {"verdict": verdict, "per_comb_layer": per_comb_layer,
           "per_probe": per_probe, "calibration_summary": cal}
    (RESULTS_DIR / f"exp0_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(out), indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "n_layers": n_layers, "n_perm": n_perm, "heldout_per": heldout,
        "n_calib": len(calib), "n_test": len(test),
        "metric": "top-1 argmax-over-CRYSTAL per crystal layer vs certified "
                  "single-combinator label; precision/recall/F1 + peak layer",
        "reference": "held-out crystal-prose combinator labels (non-circular split)",
    }
    (RESULTS_DIR / f"exp0_meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[exp0] wrote {RESULTS_DIR}/exp0_verdict_{slug}.json")


if __name__ == "__main__":
    main()
