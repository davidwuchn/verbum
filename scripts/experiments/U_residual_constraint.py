#!/usr/bin/env python3
"""Quick test: does the residual stream direction constrain U?

If U_l is determined by h_l, then:
  Phase 2 (orthogonal): U_l columns should be ⊥ to h_l direction
  Phase 3 (aligned):    U_l columns should partially align with h_l

Measure: projection of SVD left singular vectors onto residual stream direction.

Usage:
  uv run python scripts/experiments/U_residual_constraint.py --model Qwen/Qwen3-8B

License: MIT
"""

from __future__ import annotations

import math
import os
import time

os.environ.setdefault('PYTHONUNBUFFERED', '1')

import numpy as np
import torch

PHI = (1 + math.sqrt(5)) / 2


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


def run_experiment(model_id: str, n_calib: int = 10):
    log("=" * 72)
    log("U ↔ RESIDUAL STREAM CONSTRAINT TEST")
    log("=" * 72)

    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float32, device_map="cpu",
        low_cpu_mem_usage=True)
    model.eval()

    n_layers = model.config.num_hidden_layers
    hidden_size = model.config.hidden_size
    log(f"Loaded: {n_layers} layers, hidden={hidden_size}")

    # Get residual stream directions from calibration
    try:
        from datasets import load_dataset
        dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="train")
        texts = [t for t in dataset["text"] if len(t.strip()) > 100]
    except Exception:
        texts = ["Language models compute by applying functions to representations. " * 30] * 50

    calib_ids = []
    for text in texts:
        ids = tokenizer.encode(text, add_special_tokens=False, truncation=True, max_length=256)
        if len(ids) >= 32:
            calib_ids.append(torch.tensor(ids[:256]))
        if len(calib_ids) >= n_calib:
            break

    log(f"Calibration: {len(calib_ids)} sequences\n")

    # Record mean residual direction per layer
    log("Recording residual stream directions...")
    h_directions = [torch.zeros(hidden_size) for _ in range(n_layers + 1)]
    h_count = 0

    with torch.no_grad():
        for ids in calib_ids:
            outputs = model(ids.unsqueeze(0), output_hidden_states=True)
            for l in range(n_layers + 1):
                h = outputs.hidden_states[l].squeeze(0)  # (seq, hidden)
                h_mean_dir = h.mean(dim=0)  # mean across sequence positions
                h_directions[l] += h_mean_dir
            h_count += 1

    for l in range(n_layers + 1):
        h_directions[l] /= h_count
        h_directions[l] = h_directions[l] / (h_directions[l].norm() + 1e-10)

    log("Done.\n")

    # For each layer: SVD of gate_proj, project U onto h_l
    log("=" * 72)
    log("U ALIGNMENT WITH RESIDUAL STREAM")
    log("=" * 72)
    log(f"\n  {'Layer':>5s} {'phase':>8s} {'top1_|cos|':>12s} {'top10_mean':>12s} "
        f"{'top50_mean':>12s} {'all_mean':>12s} {'f_contrib_cos':>14s}")
    log(f"  {'─'*5} {'─'*8} {'─'*12} {'─'*12} {'─'*12} {'─'*12} {'─'*14}")

    all_top10 = []
    all_phases = []

    for l in range(n_layers):
        W = model.model.layers[l].mlp.gate_proj.weight.data.float().cpu()
        h_dir = h_directions[l]  # (hidden,) — normalized residual direction AT this layer

        # SVD of gate_proj
        k = min(128, min(W.shape))
        U, S, V = torch.svd_lowrank(W, q=k, niter=3)
        # U: (intermediate, k) — left singular vectors
        # V: (hidden, k) — right singular vectors

        # Project RIGHT singular vectors onto residual direction
        # V columns are in hidden_size space, same as h_dir
        # cos(v_k, h_dir) tells us if this singular direction reads from the residual
        cos_V_h = (V.T @ h_dir).abs()  # (k,) — |cos| for each singular vector

        # Also check contribution direction
        # f_l = h_{l+1} - h_l direction
        if l < n_layers:
            f_dir = h_directions[l + 1] - h_directions[l]
            f_dir = f_dir / (f_dir.norm() + 1e-10)
            cos_f_h = (h_dir @ f_dir).item()  # contribution alignment with residual
        else:
            cos_f_h = 0

        # Phase classification
        if l <= 6:
            phase = "EXPAND"
        elif l <= 22:
            phase = "ORTHO"
        elif l <= 34:
            phase = "ALIGN"
        else:
            phase = "COLLAPSE"

        top1 = cos_V_h[0].item()
        top10 = cos_V_h[:10].mean().item()
        top50 = cos_V_h[:50].mean().item()
        all_mean = cos_V_h.mean().item()

        all_top10.append(top10)
        all_phases.append(phase)

        marker = ""
        if phase == "ORTHO" and top10 < 0.05:
            marker = " ← ⊥"
        elif phase == "ALIGN" and top10 > 0.10:
            marker = " ← ∥"

        log(f"  {l:5d} {phase:>8s} {top1:12.4f} {top10:12.4f} "
            f"{top50:12.4f} {all_mean:12.4f} {cos_f_h:14.4f}{marker}")

    # Summary by phase
    log(f"\n{'=' * 72}")
    log("SUMMARY BY PHASE")
    log(f"{'=' * 72}")

    for phase_name in ["EXPAND", "ORTHO", "ALIGN", "COLLAPSE"]:
        vals = [all_top10[i] for i in range(len(all_top10)) if all_phases[i] == phase_name]
        if vals:
            log(f"  {phase_name:10s}: mean top10 |cos(V, h)| = {np.mean(vals):.4f} ± {np.std(vals):.4f}  "
                f"(n={len(vals)} layers)")

    # The key question: does the alignment CHANGE with phase?
    ortho_vals = [all_top10[i] for i in range(len(all_top10)) if all_phases[i] == "ORTHO"]
    align_vals = [all_top10[i] for i in range(len(all_top10)) if all_phases[i] == "ALIGN"]

    if ortho_vals and align_vals:
        from scipy.stats import mannwhitneyu
        stat, pval = mannwhitneyu(ortho_vals, align_vals, alternative='two-sided')
        log(f"\n  Mann-Whitney U test (ORTHO vs ALIGN): p={pval:.4e}")
        log(f"  ORTHO mean: {np.mean(ortho_vals):.4f}")
        log(f"  ALIGN mean: {np.mean(align_vals):.4f}")

        if np.mean(align_vals) > np.mean(ortho_vals):
            log(f"  ✅ ALIGN phase has higher V-h alignment than ORTHO phase")
        else:
            log(f"  ❌ No phase difference in V-h alignment")

    log(f"\n{'=' * 72}")
    log("DONE")
    log(f"{'=' * 72}")

    del model


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-8B")
    parser.add_argument("--n-calib", type=int, default=10)
    args = parser.parse_args()
    run_experiment(args.model, args.n_calib)


if __name__ == "__main__":
    main()
