#!/usr/bin/env python3
"""Test: does the residual stream follow the Fibonacci recurrence?

If h_{l+1} = h_l + f(h_l) is at the φ fixed point:
  ||f(h_l)|| / ||h_l|| ≈ 1/φ
  ||h_{l+1}|| / ||h_l|| ≈ φ

This constrains the per-layer rotation U because U must produce
a contribution f(h) that has the right magnitude AND direction
relative to the residual stream.

MEASUREMENTS:
  1. ||h_l|| per layer — the residual stream norm trajectory
  2. ||h_{l+1}|| / ||h_l|| — growth ratio per layer (looking for φ)
  3. ||f_l(h_l)|| / ||h_l|| — contribution ratio (looking for 1/φ)
  4. cos(h_l, f_l(h_l)) — angle between residual and contribution
  5. cos(h_l, h_{l+1}) — how much direction changes per layer
  6. Periodicity in growth ratios — does it follow [1, φ, 1] cycle?

Usage:
  uv run python scripts/experiments/residual_fibonacci.py --model Qwen/Qwen3-8B

License: MIT
"""

from __future__ import annotations

import argparse
import math
import os
import time

os.environ.setdefault('PYTHONUNBUFFERED', '1')

import numpy as np
import torch

PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1 / PHI


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


def run_experiment(model_id: str, n_calib: int = 20, seq_len: int = 256):
    log("=" * 72)
    log("RESIDUAL STREAM FIBONACCI TEST")
    log("=" * 72)
    log(f"Model: {model_id}")
    log(f"φ = {PHI:.6f}, 1/φ = {INV_PHI:.6f}")
    log()

    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float32, device_map="cpu",
        low_cpu_mem_usage=True)
    model.eval()

    n_layers = model.config.num_hidden_layers
    log(f"Loaded: {n_layers} layers")

    # Calibration data
    try:
        from datasets import load_dataset
        dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="train")
        texts = [t for t in dataset["text"] if len(t.strip()) > 100]
    except Exception:
        texts = ["The theory of computation studies abstract machines and the problems they can solve. " * 20] * 50

    calib_ids = []
    for text in texts:
        ids = tokenizer.encode(text, add_special_tokens=False, truncation=True,
                               max_length=seq_len)
        if len(ids) >= 32:
            calib_ids.append(torch.tensor(ids[:seq_len]))
        if len(calib_ids) >= n_calib:
            break
    log(f"Calibration: {len(calib_ids)} sequences\n")

    # Accumulators
    # Per layer: residual norm, contribution norm, angles
    residual_norms = np.zeros((n_calib, n_layers + 1))  # +1 for embedding output
    contribution_norms = np.zeros((n_calib, n_layers))
    cos_residual_contribution = np.zeros((n_calib, n_layers))
    cos_residual_next = np.zeros((n_calib, n_layers))

    log("Recording residual stream...")
    t0 = time.time()

    with torch.no_grad():
        for batch_idx, ids in enumerate(calib_ids):
            # Get hidden states at every layer
            outputs = model(ids.unsqueeze(0), output_hidden_states=True)
            hidden_states = outputs.hidden_states  # tuple of (1, seq, hidden)

            for l in range(n_layers + 1):
                h = hidden_states[l].squeeze(0)  # (seq, hidden)
                # Mean norm across sequence positions
                residual_norms[batch_idx, l] = h.norm(dim=1).mean().item()

            for l in range(n_layers):
                h_l = hidden_states[l].squeeze(0)      # (seq, hidden)
                h_next = hidden_states[l + 1].squeeze(0)  # (seq, hidden)
                f_l = h_next - h_l  # layer contribution

                # Norms
                h_norm = h_l.norm(dim=1)  # (seq,)
                f_norm = f_l.norm(dim=1)

                contribution_norms[batch_idx, l] = f_norm.mean().item()

                # Cosine between residual and contribution
                cos_hf = (h_l * f_l).sum(dim=1) / (h_norm * f_norm + 1e-10)
                cos_residual_contribution[batch_idx, l] = cos_hf.mean().item()

                # Cosine between h_l and h_{l+1}
                h_next_norm = h_next.norm(dim=1)
                cos_hn = (h_l * h_next).sum(dim=1) / (h_norm * h_next_norm + 1e-10)
                cos_residual_next[batch_idx, l] = cos_hn.mean().item()

            if (batch_idx + 1) % 5 == 0:
                log(f"  batch {batch_idx + 1}/{len(calib_ids)}")

    elapsed = time.time() - t0
    log(f"  Done in {elapsed:.1f}s\n")

    # Average across batches
    mean_norms = residual_norms.mean(axis=0)
    mean_contrib = contribution_norms.mean(axis=0)
    mean_cos_hf = cos_residual_contribution.mean(axis=0)
    mean_cos_hn = cos_residual_next.mean(axis=0)

    # Growth ratios
    growth_ratios = mean_norms[1:] / (mean_norms[:-1] + 1e-10)
    contrib_ratios = mean_contrib / (mean_norms[:-1] + 1e-10)

    # ── Results ─────────────────────────────────────────────────
    log("=" * 72)
    log("RESIDUAL STREAM TRAJECTORY")
    log("=" * 72)
    log(f"\n  {'Layer':>5s} {'||h||':>10s} {'||f||':>10s} {'||h+1||/||h||':>14s} "
        f"{'||f||/||h||':>12s} {'cos(h,f)':>10s} {'cos(h,h+1)':>12s}")
    log(f"  {'─'*5} {'─'*10} {'─'*10} {'─'*14} {'─'*12} {'─'*10} {'─'*12}")

    for l in range(n_layers):
        marker = ""
        if abs(growth_ratios[l] - PHI) < 0.05:
            marker = " ← φ?"
        elif abs(growth_ratios[l] - 1.0) < 0.05:
            marker = " ← 1"
        elif abs(contrib_ratios[l] - INV_PHI) < 0.05:
            marker = " ← 1/φ?"

        log(f"  {l:5d} {mean_norms[l]:10.4f} {mean_contrib[l]:10.4f} "
            f"{growth_ratios[l]:14.6f} {contrib_ratios[l]:12.6f} "
            f"{mean_cos_hf[l]:10.4f} {mean_cos_hn[l]:12.4f}{marker}")

    # Final layer output
    log(f"  {'out':>5s} {mean_norms[n_layers]:10.4f}")

    # ── Summary statistics ──────────────────────────────────────
    log(f"\n{'=' * 72}")
    log("SUMMARY")
    log(f"{'=' * 72}")

    # Skip first few layers (embedding effects)
    stable_start = 4
    stable_growth = growth_ratios[stable_start:]
    stable_contrib = contrib_ratios[stable_start:]

    log(f"\n  Growth ratio ||h_{{l+1}}|| / ||h_l|| (layers {stable_start}-{n_layers-1}):")
    log(f"    Mean:   {stable_growth.mean():.6f}  (φ = {PHI:.6f})")
    log(f"    Std:    {stable_growth.std():.6f}")
    log(f"    Min:    {stable_growth.min():.6f}")
    log(f"    Max:    {stable_growth.max():.6f}")
    log(f"    Dev from φ: {abs(stable_growth.mean() - PHI):.6f}")
    log(f"    Dev from 1: {abs(stable_growth.mean() - 1.0):.6f}")

    log(f"\n  Contribution ratio ||f_l|| / ||h_l|| (layers {stable_start}-{n_layers-1}):")
    log(f"    Mean:   {stable_contrib.mean():.6f}  (1/φ = {INV_PHI:.6f})")
    log(f"    Std:    {stable_contrib.std():.6f}")
    log(f"    Dev from 1/φ: {abs(stable_contrib.mean() - INV_PHI):.6f}")
    log(f"    Dev from 1:   {abs(stable_contrib.mean() - 1.0):.6f}")

    log(f"\n  Direction change cos(h_l, h_{{l+1}}) (layers {stable_start}-{n_layers-1}):")
    mean_dir = mean_cos_hn[stable_start:].mean()
    log(f"    Mean:   {mean_dir:.6f}")
    log(f"    Dev from 1/φ: {abs(mean_dir - INV_PHI):.6f}")

    # ── Periodicity test ────────────────────────────────────────
    log(f"\n{'=' * 72}")
    log("PERIODICITY IN GROWTH RATIOS")
    log(f"{'=' * 72}")

    # Autocorrelation of growth ratios
    gr = stable_growth - stable_growth.mean()
    autocorr = np.correlate(gr, gr, mode='full')
    autocorr = autocorr[len(gr)-1:] / (autocorr[len(gr)-1] + 1e-10)

    log(f"\n  Autocorrelation of growth ratios:")
    for lag in range(min(15, len(autocorr))):
        bar = '█' * int(abs(autocorr[lag]) * 40)
        log(f"    lag {lag:2d}: {autocorr[lag]:8.4f}  {bar}")

    # Check specific periods
    for period in [2, 3, 4, 5, 6, 8]:
        if period < len(stable_growth):
            # Reshape into periods and compute within-period variance
            n_complete = len(stable_growth) // period * period
            reshaped = stable_growth[:n_complete].reshape(-1, period)
            within_var = reshaped.var(axis=0).mean()
            between_var = reshaped.mean(axis=1).var()
            f_ratio = between_var / (within_var + 1e-10)
            log(f"    Period {period}: within_var={within_var:.6f} between_var={between_var:.6f} F={f_ratio:.4f}")

    log(f"\n{'=' * 72}")
    log("DONE")
    log(f"{'=' * 72}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-8B")
    parser.add_argument("--n-calib", type=int, default=20)
    args = parser.parse_args()

    run_experiment(args.model, args.n_calib)


if __name__ == "__main__":
    main()
