#!/usr/bin/env python3
"""
Crystal Lattice Zeros — Are zeros the null space of the universal crystal?

Hypothesis: the positions that should be zero in attention Q/K weights are
the dimensions of d_model that are orthogonal to the crystal subspace.
If the crystal is universal across models, the zero mask is computable
analytically from the crystal eigendecomposition alone — no teacher needed.

Protocol:
  1. Load trained micro model (has crystal embeddings + trained attention)
  2. Compute crystal subspace from the 16 crystal embeddings (8 pos + 8 anti)
  3. For each d_model dimension, measure its participation in the crystal subspace
  4. Zero dimensions by crystal participation (lowest → zero first)
  5. Compare to M-noise zeros, magnitude zeros, random zeros
  6. Also test: project Q/K rows ONTO crystal subspace (hard projection)

License: MIT
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)

import numpy as np
import mlx.core as mx
import mlx.nn as nn

sys.path.insert(0, str(Path(__file__).parent))
from micro_model import MicroModel, MicroConfig


# ══════════════════════════════════════════════════════════════════════
# Data helpers
# ══════════════════════════════════════════════════════════════════════

def load_compile_examples(path):
    examples = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(json.loads(line))
    return examples

def tokenize_examples(examples, tokenizer, max_len=256, eod_id=151643):
    sequences = []
    for ex in examples:
        text = f"{ex['input']}\n{ex['output']}"
        token_ids = tokenizer.encode(text, add_special_tokens=False)
        token_ids.append(eod_id)
        if len(token_ids) > max_len:
            token_ids = token_ids[:max_len]
        sequences.append(np.array(token_ids, dtype=np.int32))
    return sequences

def make_eval_batch(sequences, max_seq_len=256):
    stream = np.concatenate(sequences)
    T = min(max_seq_len, len(stream) - 1)
    return mx.array(stream[:T].reshape(1, T)), mx.array(stream[1:T+1].reshape(1, T))


# ══════════════════════════════════════════════════════════════════════
# Crystal subspace analysis
# ══════════════════════════════════════════════════════════════════════

def compute_crystal_subspace(model):
    """Extract the crystal subspace from trained crystal embeddings.

    Returns:
        V_crystal: (d_model, rank) — basis vectors of crystal subspace
        crystal_energy: (d_model,) — per-dimension participation in crystal subspace
        eigvals: singular values of the crystal embedding matrix
    """
    mx.eval(model.parameters())
    C = np.array(model.get_all_crystal_embeddings())  # (16, d_model)

    # SVD of crystal embeddings
    U, s, Vt = np.linalg.svd(C, full_matrices=False)
    # V columns are the crystal subspace basis in d_model space
    # Vt has shape (min(16, d_model), d_model) = (16, 128)
    # V_crystal = Vt.T = (128, 16) — each column is a basis vector

    # Per-dimension participation: how much does dim i contribute to the crystal subspace?
    # crystal_energy[i] = Σ_k (Vt[k, i])² × s[k]²  (weighted by eigenvalue importance)
    # Or unweighted: crystal_energy[i] = Σ_k (Vt[k, i])²
    # Unweighted = fraction of crystal subspace that lives in dim i
    crystal_energy_unweighted = np.sum(Vt ** 2, axis=0)  # (d_model,)

    # Weighted by singular values (emphasizes dominant crystal axes)
    crystal_energy_weighted = np.sum((Vt * s[:, np.newaxis]) ** 2, axis=0)  # (d_model,)
    crystal_energy_weighted /= crystal_energy_weighted.sum()  # normalize

    # Effective rank of crystal subspace
    total_var = (s ** 2).sum()
    cum_var = np.cumsum(s ** 2) / total_var
    effective_rank = int(np.searchsorted(cum_var, 0.99) + 1)

    return {
        "Vt": Vt,
        "singular_values": s,
        "energy_unweighted": crystal_energy_unweighted,
        "energy_weighted": crystal_energy_weighted,
        "effective_rank": effective_rank,
        "cumulative_variance": cum_var.tolist(),
    }


def measure_mspace(W_q, W_k):
    """Measure M-space quality metrics."""
    M = W_q.T @ W_k
    U, s, Vt = np.linalg.svd(M, full_matrices=False)
    total = (s ** 2).sum()
    if total < 1e-12:
        return {"rank90": 128, "top1_pct": 0, "sigma_ratio": 1.0}
    cum = np.cumsum(s ** 2) / total
    rank90 = int(np.searchsorted(cum, 0.90) + 1)
    top1 = float(cum[0] * 100)
    ratio = float(s[0] / s[1]) if len(s) > 1 and s[1] > 0 else float('inf')
    return {"rank90": rank90, "top1_pct": top1, "sigma_ratio": ratio}


def eval_loss(model, eval_input, eval_target):
    _, loss = model(eval_input, eval_target)
    mx.eval(loss)
    return float(loss.item())


# ══════════════════════════════════════════════════════════════════════
# Zero strategies
# ══════════════════════════════════════════════════════════════════════

def apply_crystal_zeros(W_float, crystal_energy, zero_frac):
    """Zero positions where the INPUT DIMENSION has low crystal participation.

    crystal_energy[i] = how much dimension i participates in crystal subspace.
    Low energy → this dimension is in the crystal null space → zero it.
    """
    d_out, d_in = W_float.shape
    gamma = np.abs(W_float).mean(axis=1, keepdims=True)
    W_ternary = np.sign(W_float).astype(np.float32)
    W_ternary[W_ternary == 0] = 1.0

    if zero_frac > 0:
        # Zero dimensions with lowest crystal energy
        n_zero_dims = max(1, int(zero_frac * d_in))
        sorted_dims = np.argsort(crystal_energy)
        zero_dims = sorted_dims[:n_zero_dims]
        W_ternary[:, zero_dims] = 0.0

    actual_frac = (W_ternary == 0).mean()
    return W_ternary, gamma, actual_frac


def apply_crystal_weighted_zeros(W_float, crystal_energy_weighted, zero_frac):
    """Same but using eigenvalue-weighted crystal energy."""
    return apply_crystal_zeros(W_float, crystal_energy_weighted, zero_frac)


def apply_mnoise_zeros(W_float, M_float_U, K, zero_frac):
    """M-noise zeros (from experiment 2): zero by noise mode participation."""
    d_out, d_in = W_float.shape
    gamma = np.abs(W_float).mean(axis=1, keepdims=True)
    W_ternary = np.sign(W_float).astype(np.float32)
    W_ternary[W_ternary == 0] = 1.0

    if zero_frac > 0:
        noise_per_dim = np.sum(M_float_U[:, K:] ** 2, axis=1)
        rel_mag = np.abs(W_float) / (gamma + 1e-8)
        combined = noise_per_dim[np.newaxis, :] / (rel_mag + 0.1)
        flat = combined.flatten()
        n_zero = int(zero_frac * len(flat))
        if n_zero > 0:
            threshold = np.partition(flat, -n_zero)[-n_zero]
            W_ternary[combined >= threshold] = 0.0

    actual_frac = (W_ternary == 0).mean()
    return W_ternary, gamma, actual_frac


def apply_magnitude_zeros(W_float, zero_frac):
    """Magnitude threshold zeros."""
    d_out, d_in = W_float.shape
    gamma = np.abs(W_float).mean(axis=1, keepdims=True)
    W_ternary = np.sign(W_float).astype(np.float32)
    W_ternary[W_ternary == 0] = 1.0

    if zero_frac > 0:
        rel_mag = np.abs(W_float) / (gamma + 1e-8)
        flat = rel_mag.flatten()
        n_zero = int(zero_frac * len(flat))
        if n_zero > 0:
            threshold = np.partition(flat, n_zero)[n_zero]
            W_ternary[rel_mag <= threshold] = 0.0

    actual_frac = (W_ternary == 0).mean()
    return W_ternary, gamma, actual_frac


def apply_random_zeros(W_float, zero_frac, rng):
    """Random zeros (baseline)."""
    d_out, d_in = W_float.shape
    gamma = np.abs(W_float).mean(axis=1, keepdims=True)
    W_ternary = np.sign(W_float).astype(np.float32)
    W_ternary[W_ternary == 0] = 1.0

    if zero_frac > 0:
        mask = rng.random((d_out, d_in)) < zero_frac
        W_ternary[mask] = 0.0

    actual_frac = (W_ternary == 0).mean()
    return W_ternary, gamma, actual_frac


# ══════════════════════════════════════════════════════════════════════
# Main experiment
# ══════════════════════════════════════════════════════════════════════

def main():
    t0 = time.time()
    print("=" * 70)
    print("CRYSTAL LATTICE ZEROS — Is the null space universal?")
    print("=" * 70)
    print()

    cfg = MicroConfig()
    model = MicroModel(cfg)
    ckpt_path = Path("checkpoints/micro/final/model.npz")
    weights = mx.load(str(ckpt_path))
    model.load_weights(list(weights.items()))
    mx.eval(model.parameters())
    print(f"Loaded model from {ckpt_path}", flush=True)

    # Data for eval loss
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    eval_examples = load_compile_examples(cfg.eval_file)
    eval_seqs = tokenize_examples(eval_examples, tokenizer, cfg.max_seq_len, cfg.eod_id)
    eval_input, eval_target = make_eval_batch(eval_seqs, cfg.max_seq_len)

    baseline_loss = eval_loss(model, eval_input, eval_target)
    print(f"Baseline eval loss: {baseline_loss:.4f}", flush=True)

    # ── Crystal subspace analysis ──
    print("\n── Crystal Subspace ──", flush=True)
    crystal = compute_crystal_subspace(model)
    s = crystal["singular_values"]
    print(f"  Crystal embedding singular values: {', '.join(f'{v:.3f}' for v in s[:10])}", flush=True)
    print(f"  Effective rank (99% variance): {crystal['effective_rank']}", flush=True)
    print(f"  Top 5 cumulative variance: {', '.join(f'{v:.1%}' for v in crystal['cumulative_variance'][:5])}", flush=True)

    # How concentrated is crystal energy across dimensions?
    ce = crystal["energy_unweighted"]
    cew = crystal["energy_weighted"]
    print(f"\n  Crystal energy per d_model dimension:", flush=True)
    print(f"    Unweighted: min={ce.min():.4f}, max={ce.max():.4f}, "
          f"mean={ce.mean():.4f}, std={ce.std():.4f}", flush=True)
    print(f"    Weighted:   min={cew.min():.6f}, max={cew.max():.6f}, "
          f"mean={cew.mean():.6f}", flush=True)

    # How many dimensions carry most of the crystal?
    sorted_ce = np.sort(ce)[::-1]
    cum_ce = np.cumsum(sorted_ce) / sorted_ce.sum()
    dims_50 = int(np.searchsorted(cum_ce, 0.50) + 1)
    dims_90 = int(np.searchsorted(cum_ce, 0.90) + 1)
    dims_99 = int(np.searchsorted(cum_ce, 0.99) + 1)
    print(f"\n  Crystal concentration: 50% in {dims_50} dims, "
          f"90% in {dims_90} dims, 99% in {dims_99} dims (of {cfg.d_model})", flush=True)
    print(f"  → {cfg.d_model - dims_90} dims carry <10% of crystal = candidate zeros", flush=True)

    # ── Compare zero strategies across layers ──
    rng = np.random.RandomState(42)
    zero_fracs = [0.0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60]

    strategies = [
        "crystal_unweighted",
        "crystal_weighted",
        "mnoise",
        "magnitude",
        "random",
    ]

    results = {
        "crystal_subspace": {
            "effective_rank": crystal["effective_rank"],
            "singular_values": crystal["singular_values"].tolist(),
            "dims_50pct": dims_50,
            "dims_90pct": dims_90,
            "dims_99pct": dims_99,
        },
        "baseline_loss": baseline_loss,
        "layers": {},
    }

    for layer_idx in range(cfg.n_layers):
        print(f"\n{'═'*70}", flush=True)
        print(f"  LAYER {layer_idx}", flush=True)
        print(f"{'═'*70}", flush=True)

        block = model.blocks[layer_idx]
        W_q = np.array(block.attn.q_proj.weight)
        W_k = np.array(block.attn.k_proj.weight)

        # Float32 M-space reference
        ms_float = measure_mspace(W_q, W_k)
        print(f"  Float32 M: rank90={ms_float['rank90']}, top1={ms_float['top1_pct']:.1f}%", flush=True)

        # M-noise needs M's SVD
        M_float = W_q.T @ W_k
        U_m, s_m, Vt_m = np.linalg.svd(M_float, full_matrices=False)
        total_m = (s_m ** 2).sum()
        cum_m = np.cumsum(s_m ** 2) / total_m
        K = int(np.searchsorted(cum_m, 0.90) + 1)

        layer_results = {"float_mspace": ms_float, "float_K": K, "sweeps": {}}

        print(f"\n  {'zero%':>5} │ {'crystal_uw':>11} {'crystal_w':>11} {'mnoise':>11} {'magnitude':>11} {'random':>11}", flush=True)
        print(f"  {'':>5} │ {'rank90/top1':>11} {'rank90/top1':>11} {'rank90/top1':>11} {'rank90/top1':>11} {'rank90/top1':>11}", flush=True)
        print(f"  {'─'*5}─┼{'─'*60}", flush=True)

        for zf in zero_fracs:
            sweep_entry = {}

            for strat in strategies:
                if strat == "crystal_unweighted":
                    Wq_t, gq, fq = apply_crystal_zeros(W_q, ce, zf)
                    Wk_t, gk, fk = apply_crystal_zeros(W_k, ce, zf)
                elif strat == "crystal_weighted":
                    Wq_t, gq, fq = apply_crystal_weighted_zeros(W_q, cew, zf)
                    Wk_t, gk, fk = apply_crystal_weighted_zeros(W_k, cew, zf)
                elif strat == "mnoise":
                    Wq_t, gq, fq = apply_mnoise_zeros(W_q, U_m, K, zf)
                    Wk_t, gk, fk = apply_mnoise_zeros(W_k, U_m, K, zf)
                elif strat == "magnitude":
                    Wq_t, gq, fq = apply_magnitude_zeros(W_q, zf)
                    Wk_t, gk, fk = apply_magnitude_zeros(W_k, zf)
                elif strat == "random":
                    Wq_t, gq, fq = apply_random_zeros(W_q, zf, rng)
                    Wk_t, gk, fk = apply_random_zeros(W_k, zf, rng)

                ms = measure_mspace(Wq_t, Wk_t)

                # Measure eval loss: replace Q/K with ternary*gamma, measure, restore
                orig_q = np.array(block.attn.q_proj.weight)
                orig_k = np.array(block.attn.k_proj.weight)
                block.attn.q_proj.weight = mx.array(Wq_t * gq)
                block.attn.k_proj.weight = mx.array(Wk_t * gk)
                mx.eval(model.parameters())
                loss = eval_loss(model, eval_input, eval_target)
                block.attn.q_proj.weight = mx.array(orig_q)
                block.attn.k_proj.weight = mx.array(orig_k)
                mx.eval(model.parameters())

                sweep_entry[strat] = {
                    "rank90": ms["rank90"],
                    "top1_pct": ms["top1_pct"],
                    "sigma_ratio": ms["sigma_ratio"],
                    "eval_loss": loss,
                    "delta_loss": loss - baseline_loss,
                    "actual_zero_frac_q": float(fq),
                }

            # Print row
            vals = []
            for strat in strategies:
                e = sweep_entry[strat]
                vals.append(f"{e['rank90']:>3}/{e['top1_pct']:>5.1f}%")
            print(f"  {zf*100:>4.0f}% │ {' '.join(vals)}", flush=True)

            layer_results["sweeps"][f"{zf:.2f}"] = sweep_entry

        # Print loss comparison at 30%
        print(f"\n  Loss at 30% zeros (ΔLoss vs baseline):", flush=True)
        entry_30 = layer_results["sweeps"]["0.30"]
        for strat in strategies:
            e = entry_30[strat]
            print(f"    {strat:>20}: {e['delta_loss']:>+.4f}  (rank90={e['rank90']}, top1={e['top1_pct']:.1f}%)", flush=True)

        results["layers"][str(layer_idx)] = layer_results

    # ── Summary ──
    elapsed = time.time() - t0
    print(f"\n{'═'*70}", flush=True)
    print("SUMMARY", flush=True)
    print(f"{'═'*70}", flush=True)
    print(f"\nCrystal subspace: rank {crystal['effective_rank']}, "
          f"90% in {dims_90}/{cfg.d_model} dims", flush=True)
    print(f"→ {cfg.d_model - dims_90} dims ({(cfg.d_model-dims_90)/cfg.d_model:.0%}) "
          f"are crystal null space", flush=True)

    print(f"\nBest strategy at 30% zeros (Layer 2 — the gem):", flush=True)
    L2_30 = results["layers"]["2"]["sweeps"]["0.30"]
    ranked = sorted(strategies, key=lambda s: L2_30[s]["rank90"])
    for strat in ranked:
        e = L2_30[strat]
        print(f"  {strat:>20}: rank90={e['rank90']:>3}, top1={e['top1_pct']:>5.1f}%, "
              f"ΔLoss={e['delta_loss']:>+.4f}", flush=True)

    print(f"\nElapsed: {elapsed:.1f}s", flush=True)

    out_dir = Path("results/crystal-zeros")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "summary.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved to results/crystal-zeros/summary.json", flush=True)


if __name__ == "__main__":
    main()
