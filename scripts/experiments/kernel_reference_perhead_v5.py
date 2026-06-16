#!/usr/bin/env python3
# register: per-head OV (o_proj input, split by head)
"""Kernel-ref per-HEAD OV scan — the B head-dilution test (s234 v5 lead 2d 1b-iii).

Prong 1b-ii found B flat in the head-SUMMED attention output (o_proj OUTPUT, max t=0.49
n.s.). But o_proj output SUMS all heads — a single B-composer head (s127 {B,C}=
composers->attention) could be averaged away. This scans the FINER register: hook o_proj
INPUT (concatenated per-head attention output [T, H*head_dim]), split into per-(layer,
head) cells [T, head_dim], calibrate the crystal per cell, and ask: does B discriminate
in ANY single head where the head-summed read was flat?

Method: treat each (layer, head) cell as a "layer" for RelationalCrystalClassifier
(sign-CMR, crosstask null). Read held-out prose last-token per cell; raw-z Welch
contrast discr_z(c, cell) = mean z_c on c-prose minus on other-prose. With ~1600 cells,
a Bonferroni-ish threshold (t>4.0 ~ p<0.05 family-wise over 1600 cells) marks "sig".

VERDICT LOGIC (λ measure, two-sided):
  • B has significant cells (t>4) where head-summed was flat -> HEAD-DILUTION confirmed;
    report the B-composer head(s). B IS localized, just diluted by summing.
  • B has ~0 significant cells while {C,I,K,Y} have many -> B genuinely NOT localized in
    any head either -> the no-single-token-signature hypothesis (B = ORDER, prong 2).

Usage:
    uv run python scripts/experiments/kernel_reference_perhead_v5.py --smoke
    uv run python scripts/experiments/kernel_reference_perhead_v5.py --register

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

from kernel_reference_prose_v2 import split_probes, welch_t  # noqa: E402
from opcode_monitor_v2 import (  # noqa: E402
    BASELINE_NULL_SENTENCES,
    _git_sha,
    _json_safe,
    _transformers_version,
    load_model_and_tokenizer,
)
from relational_opcode import CRYSTAL, RelationalCrystalClassifier  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "kernel-reference-audit"
TEST_COMBINATORS = ["K", "I", "B", "C", "S", "D", "W", "Y"]
MC_T = 4.0  # Bonferroni-ish t threshold (~p<0.05 family-wise over ~1600 cells)


def _make_input_hook(store: dict[int, np.ndarray], li: int):
    """Capture o_proj INPUT = concatenated per-head attention output [T, H*hd]."""

    def _hook(_m, inp, _out):
        x = inp[0]  # [B, T, H*head_dim]
        store[li] = x[0, :, :].detach().float().cpu().numpy().astype(np.float64)

    return _hook


def forward_attn_heads(prompt, model, tok, torch_mod, layers):
    """Forward once; return ({li: o_proj_input [T, H*head_dim]}, n_tokens)."""
    store: dict[int, np.ndarray] = {}
    handles = [model.model.layers[li].self_attn.o_proj.register_forward_hook(
        _make_input_hook(store, li)) for li in layers]
    try:
        inputs = tok(prompt, return_tensors="pt")
        dev = next(model.parameters()).device
        inputs = {k: v.to(dev) for k, v in inputs.items()}
        with torch_mod.no_grad():
            model(**inputs)
    finally:
        for h in handles:
            h.remove()
    return store, int(inputs["input_ids"].shape[1])


def split_heads(store, layers, num_heads, head_dim):
    """{li: [T, H*hd]} → {cell_id: [T, hd]}, cell_id = li*1000 + h."""
    out: dict[int, np.ndarray] = {}
    for li in layers:
        arr = store[li]
        for h in range(num_heads):
            out[li * 1000 + h] = arr[:, h * head_dim:(h + 1) * head_dim]
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Kernel-ref per-head OV scan (B)")
    parser.add_argument("--model", default="Qwen/Qwen3-14B")
    parser.add_argument("--heldout-per", type=int, default=20)
    parser.add_argument("--ppc", type=int, default=20, help="calib probes/combinator")
    parser.add_argument("--n-perm", type=int, default=30)
    parser.add_argument("--null-cap", type=int, default=300)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    model_name = args.model
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        heldout, ppc, n_perm, null_cap = 5, 5, 20, 150
        print("[perhead] SMOKE MODE")
    else:
        heldout, ppc, n_perm, null_cap = (args.heldout_per, args.ppc, args.n_perm,
                                          args.null_cap)

    calib, test = split_probes(heldout)
    # cap calib per combinator (memory/time: ~1600 cells)
    kept, counts = [], Counter()
    for p in calib:
        if counts[p.combinator] < ppc:
            kept.append(p)
            counts[p.combinator] += 1
    calib = kept
    print(f"[perhead] calib={len(calib)} test={len(test)} ppc={ppc}")

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    cfg = model.config
    n_layers = cfg.num_hidden_layers
    num_heads = cfg.num_attention_heads
    head_dim = getattr(cfg, "head_dim", cfg.hidden_size // num_heads)
    layers = list(range(n_layers))
    cells = [li * 1000 + h for li in layers for h in range(num_heads)]
    print(f"[perhead] layers={n_layers} heads={num_heads} head_dim={head_dim} "
          f"cells={len(cells)}")

    # ── calibration: per-cell last-token centroids + crosstask null ──────────────
    gate_by_cell: dict[int, list] = {c: [] for c in cells}
    labels: list[str] = []
    for i, p in enumerate(calib):
        if i % 40 == 0:
            print(f"[perhead]   calib forward {i}/{len(calib)} ...")
        store, _ = forward_attn_heads(p.prompt, model, tok, torch_mod, layers)
        sh = split_heads(store, layers, num_heads, head_dim)
        for c in cells:
            gate_by_cell[c].append(sh[c][-1])  # last token
        labels.append(p.combinator)
    gate_np = {c: np.stack(gate_by_cell[c], axis=0) for c in cells}
    labels_np = np.array(labels)

    null_by_cell: dict[int, list] = {c: [] for c in cells}
    print(f"[perhead] building crosstask null ({len(BASELINE_NULL_SENTENCES)} prompts)")
    for s in BASELINE_NULL_SENTENCES:
        store, _ = forward_attn_heads(s, model, tok, torch_mod, layers)
        sh = split_heads(store, layers, num_heads, head_dim)
        for c in cells:
            null_by_cell[c].append(sh[c])
    null_np = {c: np.concatenate(null_by_cell[c], axis=0)[:null_cap] for c in cells}

    rcc = RelationalCrystalClassifier(cells, n_perm=n_perm, z_thresh=2.0,
                                      sil_z_thresh=2.0, consensus_gram="auto")
    rcc.calibrate(gate_np, labels_np, null_gate_by_layer=null_np)
    n_crystal = len(rcc.crystal_layers)
    print(f"[perhead] crystal-bearing cells: {n_crystal}/{len(cells)}")

    # ── read held-out prose: last-token per cell → z tensor [n_test, n_cells, 9] ──
    op_idx = {op: i for i, op in enumerate(CRYSTAL)}
    cell_idx = {c: i for i, c in enumerate(cells)}
    reads = np.zeros((len(test), len(cells), len(CRYSTAL)), dtype=np.float64)
    test_labels = []
    for i, p in enumerate(test):
        if i % 40 == 0:
            print(f"[perhead]   test forward {i}/{len(test)} ...")
        store, _ = forward_attn_heads(p.prompt, model, tok, torch_mod, layers)
        sh = split_heads(store, layers, num_heads, head_dim)
        gate_tok = {c: sh[c][-1] for c in cells}
        per_cell = rcc.classify(gate_tok).per_layer  # {cell: {op: z}}
        for c in cells:
            zmap = per_cell.get(c, {})
            for op in CRYSTAL:
                reads[i, cell_idx[c], op_idx[op]] = zmap.get(op, 0.0)
        test_labels.append(p.combinator)
    test_labels = np.array(test_labels)

    # ── per-(cell, combinator) Welch contrast; per-op roll-up ────────────────────
    def cell_lh(cell_id):
        return cell_id // 1000, cell_id % 1000

    verdict: dict = {}
    for op in TEST_COMBINATORS:
        oi = op_idx[op]
        on_mask = test_labels == op
        off_mask = ~on_mask
        best = {"t": -1e9, "cell": None, "discr_z": 0.0}
        n_sig = 0
        per_cell_t = []
        for c in cells:
            ci = cell_idx[c]
            w = welch_t(list(reads[on_mask, ci, oi]), list(reads[off_mask, ci, oi]))
            t = w["t"] if w["t"] is not None else 0.0
            per_cell_t.append((c, t, w["discr_z"]))
            if t > MC_T and w["discr_z"] > 0:
                n_sig += 1
            if t > best["t"]:
                li, h = cell_lh(c)
                best = {"t": round(t, 3), "cell": [li, h],
                        "discr_z": w["discr_z"]}
        top = sorted(per_cell_t, key=lambda x: x[1], reverse=True)[:8]
        verdict[op] = {
            "max_t": best["t"], "best_cell_LH": best["cell"],
            "best_discr_z": best["discr_z"],
            "n_cells_sig_t4": n_sig,
            "top_cells": [{"LH": list(cell_lh(c)), "t": round(t, 2),
                           "discr_z": round(d, 3)} for c, t, d in top],
        }

    b = verdict["B"]
    b_localized = bool(b["max_t"] > MC_T and b["n_cells_sig_t4"] > 0)
    summary = {
        "b_localized_in_some_head": b_localized,
        "B": {"max_t": b["max_t"], "best_cell_LH": b["best_cell_LH"],
              "n_cells_sig_t4": b["n_cells_sig_t4"]},
        "controls": {op: {"max_t": verdict[op]["max_t"],
                          "n_cells_sig_t4": verdict[op]["n_cells_sig_t4"]}
                     for op in TEST_COMBINATORS},
    }

    print("\n" + "═" * 78)
    print("KERNEL-REFERENCE PER-HEAD OV SCAN — B head-dilution test")
    print("═" * 78)
    print(f"  n_test={len(test)}  cells={len(cells)}  crystal_cells={n_crystal}  "
          f"MC_t>{MC_T}")
    print(f"\n  {'op':<4}{'max_t':>8}{'n_sig':>9}  {'best(L,H)':>12}{'discr_z':>9}")
    for op in TEST_COMBINATORS:
        v = verdict[op]
        print(f"  {op:<4}{v['max_t']:>8}{v['n_cells_sig_t4']:>12}  "
              f"{v['best_cell_LH']!s:>12}{v['best_discr_z']:>9}")
    print(f"\n  ★ B localized in a head (t>{MC_T}): {b_localized}")
    print(f"  ★ B best: cell {b['best_cell_LH']} max_t={b['max_t']} "
          f"n_sig={b['n_cells_sig_t4']}")
    print("═" * 78 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    out = {"summary": summary, "verdict": verdict,
           "crystal_cells": n_crystal, "n_cells": len(cells),
           "config": {"n_layers": n_layers, "num_heads": num_heads,
                      "head_dim": head_dim}}
    (RESULTS_DIR / f"perhead_v5_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(out), indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "n_layers": n_layers, "num_heads": num_heads, "head_dim": head_dim,
        "n_perm": n_perm, "ppc": ppc, "heldout_per": heldout, "null_cap": null_cap,
        "n_calib": len(calib), "n_test": len(test), "mc_t": MC_T,
        "register": "per-head OV (o_proj input split by head)",
    }
    (RESULTS_DIR / f"perhead_v5_meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[perhead] wrote {RESULTS_DIR}/perhead_v5_verdict_{slug}.json")


if __name__ == "__main__":
    main()
