#!/usr/bin/env python3
"""
Cut Then Fill — Does GD recover loss after geometric topology cutting?

The hypothesis: shape the topology to match crystal geometry (accept loss hit),
then let GD fill the gaps (gamma calibration). Like a gemcutter: cut the facets
first, then polish. The kerf is not damage — GD is putty.

Protocol:
  1. Start with trained float32 micro model (CE ~0.38, converged)
  2. Create ternary attention variants with different cutting depths:
     A. No cut (float32 baseline)
     B. Sign-only (±1, no zeros — current approach)
     C. Light cut (10% M-noise zeros)
     D. Medium cut (30% M-noise zeros)
     E. Deep cut (50% M-noise zeros)
     F. Deep cut + facet flips (50% zeros + 20 M-space-scored flips per layer)
  3. For each variant:
     a. Measure initial loss (right after cutting — the kerf)
     b. Freeze topology, train gamma + other params with Adam for 200 steps
     c. Measure final loss (after GD fills gaps)
     d. Measure M-space quality before and after GD
  4. Answer: does GD recover? Does the gem stay sharp after filling?

License: MIT
"""

from __future__ import annotations

import copy
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim

sys.path.insert(0, str(Path(__file__).parent))
from micro_model import MicroModel, MicroConfig


# ══════════════════════════════════════════════════════════════════════
# Data
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


class SimpleDataLoader:
    def __init__(self, sequences, batch_size, seq_len, eod_id=151643, seed=42):
        self.batch_size = batch_size
        self.seq_len = seq_len
        self.rng = np.random.RandomState(seed)
        all_tokens = []
        indices = self.rng.permutation(len(sequences))
        for idx in indices:
            all_tokens.append(sequences[idx])
        self.stream = np.concatenate(all_tokens)
        self.position = 0

    def next_batch(self):
        B, T = self.batch_size, self.seq_len
        needed = B * (T + 1)
        if self.position + needed > len(self.stream):
            self.position = 0
        buf = self.stream[self.position:self.position + needed]
        self.position += needed
        buf = buf.reshape(B, T + 1)
        return mx.array(buf[:, :T]), mx.array(buf[:, 1:T + 1])


def make_eval_batch(sequences, max_seq_len=256):
    stream = np.concatenate(sequences)
    T = min(max_seq_len, len(stream) - 1)
    return mx.array(stream[:T].reshape(1, T)), mx.array(stream[1:T + 1].reshape(1, T))


# ══════════════════════════════════════════════════════════════════════
# M-space analysis
# ══════════════════════════════════════════════════════════════════════

def measure_mspace(model, cfg):
    """Measure M-space quality for all attention layers."""
    results = {}
    for layer_idx in range(cfg.n_layers):
        W_q = np.array(model.blocks[layer_idx].attn.q_proj.weight)
        W_k = np.array(model.blocks[layer_idx].attn.k_proj.weight)
        M = W_q.T @ W_k
        U, s, Vt = np.linalg.svd(M, full_matrices=False)
        total = (s ** 2).sum()
        cum = np.cumsum(s ** 2) / total
        rank90 = int(np.searchsorted(cum, 0.90) + 1)
        top1 = float(cum[0] * 100)
        top5 = float(cum[4] * 100) if len(cum) > 4 else 100.0
        ratio = float(s[0] / s[1]) if len(s) > 1 and s[1] > 0 else float('inf')
        results[layer_idx] = {
            "rank90": rank90,
            "top1_pct": top1,
            "top5_pct": top5,
            "sigma_ratio": ratio,
            "sigma_0": float(s[0]),
        }
    return results


def eval_loss(model, eval_input, eval_target):
    """Measure eval loss."""
    _, loss = model(eval_input, eval_target)
    mx.eval(loss)
    return float(loss.item())


# ══════════════════════════════════════════════════════════════════════
# Cutting tools
# ══════════════════════════════════════════════════════════════════════

def compute_noise_scores(W, M_float_U, M_float_Vt, K):
    """Score each position by M-space noise contribution.

    For W_q position (h,i): its contribution to M goes through all SVD modes.
    Noise = energy in modes beyond K (the ghost facets).
    """
    d_out, d_in = W.shape
    # For each position (h,i), the contribution to mode k is:
    #   U[i,k] * (W_other_row[h,:] @ V[:,k])
    # But we're scoring W_q positions using M's SVD, not W_k's.
    # Simpler: score by |w[h,i]| / row_mean — positions with small
    # relative magnitude contribute mainly noise.
    # This is the magnitude-based proxy that correlated well with M-noise.

    # Actually, let's use the proper M-space noise formula:
    # noise_score[h,i] = Σ_{k>K} U[i,k]^2  (how much dim i participates in noise modes)
    # This is independent of h — it only depends on which input dim (i) we're talking about.
    noise_per_dim = np.sum(M_float_U[:, K:] ** 2, axis=1)  # (d_in,)

    # Broadcast to all rows
    scores = np.broadcast_to(noise_per_dim[np.newaxis, :], (d_out, d_in)).copy()
    return scores


def apply_cut(model, float_model, zero_frac, use_mspace_noise=True, n_facet_flips=0):
    """Apply ternary cut to attention Q/K weights.

    Takes the float32 model's Q/K weights, sign-quantizes them,
    optionally zeros positions by M-noise, optionally applies
    M-space-scored flips.

    Returns the per-row gamma for proper scaling.
    """
    cfg = model.cfg

    for layer_idx in range(cfg.n_layers):
        block = model.blocks[layer_idx]
        float_block = float_model.blocks[layer_idx]

        for proj_name in ["q_proj", "k_proj"]:
            proj = getattr(block.attn, proj_name)
            float_proj = getattr(float_block.attn, proj_name)
            W_float = np.array(float_proj.weight)  # (d_out, d_in)

            # Per-row gamma (magnitude scale)
            gamma = np.abs(W_float).mean(axis=1, keepdims=True)  # (d_out, 1)

            # Sign quantize
            W_ternary = np.sign(W_float).astype(np.float32)
            W_ternary[W_ternary == 0] = 1.0  # force tied signs to +1

            # Apply zeros if requested
            if zero_frac > 0:
                if use_mspace_noise:
                    # M-space noise scoring for zero placement
                    W_q_f = np.array(float_block.attn.q_proj.weight)
                    W_k_f = np.array(float_block.attn.k_proj.weight)
                    M_float = W_q_f.T @ W_k_f
                    U, s, Vt = np.linalg.svd(M_float, full_matrices=False)
                    total = (s ** 2).sum()
                    cum = np.cumsum(s ** 2) / total
                    K = int(np.searchsorted(cum, 0.90) + 1)

                    # Noise score per position: how much does this dim
                    # participate in noise modes of M?
                    noise_per_dim = np.sum(U[:, K:] ** 2, axis=1)  # (d_in,)
                    # Also factor in the position's relative magnitude
                    rel_mag = np.abs(W_float) / (gamma + 1e-8)  # (d_out, d_in)
                    # Combined: high noise AND low magnitude → zero
                    combined = noise_per_dim[np.newaxis, :] / (rel_mag + 0.1)
                else:
                    # Magnitude threshold
                    combined = 1.0 / (np.abs(W_float) / (gamma + 1e-8) + 0.01)

                # Zero the top zero_frac fraction
                flat = combined.flatten()
                n_zero = int(zero_frac * len(flat))
                if n_zero > 0:
                    threshold = np.partition(flat, -n_zero)[-n_zero]
                    mask = combined >= threshold
                    W_ternary[mask] = 0.0

            # Apply facet-aligned flips if requested
            if n_facet_flips > 0 and proj_name == "q_proj":
                W_q_f = np.array(float_block.attn.q_proj.weight)
                W_k_f = np.array(float_block.attn.k_proj.weight)
                M_float_full = W_q_f.T @ W_k_f
                M_float_norm = M_float_full / (np.linalg.norm(M_float_full, 'fro') + 1e-12)

                # Current ternary kernel
                W_k_t = np.sign(W_k_f).astype(np.float32)
                W_k_t[W_k_t == 0] = 1.0
                M_current = W_ternary.T @ W_k_t
                M_current_norm = M_current / (np.linalg.norm(M_current, 'fro') + 1e-12)
                R = M_float_norm - M_current_norm

                # M-space scores for Q flips
                inner = (R @ W_k_t.T).T  # (d_out, d_in)
                scores = -4.0 * W_ternary * inner

                # Apply top-N flips (only where W_ternary != 0)
                nonzero_mask = W_ternary != 0
                scores_masked = np.where(nonzero_mask, scores, -np.inf)
                flat_scores = scores_masked.flatten()
                top_indices = np.argsort(-flat_scores)[:n_facet_flips]
                for idx in top_indices:
                    h, i = divmod(idx, W_ternary.shape[1])
                    if W_ternary[h, i] != 0:
                        W_ternary[h, i] = -W_ternary[h, i]

            # Set the effective weight: ternary * gamma
            W_effective = W_ternary * gamma
            proj.weight = mx.array(W_effective)

    mx.eval(model.parameters())


# ══════════════════════════════════════════════════════════════════════
# GD fill (train gamma + norms + FFN + embeddings, frozen topology)
# ══════════════════════════════════════════════════════════════════════

def gd_fill(model, train_loader, n_steps, lr=1e-3):
    """Train the model with Adam, keeping Q/K topology frozen.

    We freeze the attention Q/K weights and train everything else
    (norms, FFN, embeddings, V, O projections).
    Actually, to be precise about "filling": we want to let the model
    adapt everything EXCEPT the Q/K sign topology. Since we set
    Q/K weights as float32 (ternary * gamma), Adam will adjust them
    as continuous params. To truly freeze topology, we'd need the
    DeltaTernaryLinear setup. Instead, we freeze Q/K entirely and
    let everything else adapt.
    """
    # Freeze Q and K proj weights
    for layer_idx in range(model.cfg.n_layers):
        block = model.blocks[layer_idx]
        block.attn.q_proj.freeze(keys=["weight"])
        block.attn.k_proj.freeze(keys=["weight"])

    optimizer = optim.Adam(learning_rate=lr)

    def loss_fn(model, x, t):
        _, loss = model(x, t)
        return loss

    loss_and_grad = nn.value_and_grad(model, loss_fn)

    losses = []
    for step in range(n_steps):
        inp, tgt = train_loader.next_batch()
        loss_val, grads = loss_and_grad(model, inp, tgt)
        grads, _ = optim.clip_grad_norm(grads, 1.0)
        optimizer.update(model, grads)
        mx.eval(model.parameters(), optimizer.state, loss_val)
        losses.append(float(loss_val.item()))

    # Unfreeze for future use
    for layer_idx in range(model.cfg.n_layers):
        block = model.blocks[layer_idx]
        block.attn.q_proj.unfreeze()
        block.attn.k_proj.unfreeze()

    return losses


# ══════════════════════════════════════════════════════════════════════
# Main experiment
# ══════════════════════════════════════════════════════════════════════

def run_experiment():
    t0 = time.time()
    print("=" * 70)
    print("CUT THEN FILL — Does GD Recover After Geometric Cutting?")
    print("=" * 70)
    print()

    cfg = MicroConfig()

    # Load baseline model
    ckpt_path = Path("checkpoints/micro/final/model.npz")
    if not ckpt_path.exists():
        ckpt_path = Path("checkpoints/micro/step_005000/model.npz")

    # Keep a pristine copy of the trained model
    float_model = MicroModel(cfg)
    weights = mx.load(str(ckpt_path))
    float_model.load_weights(list(weights.items()))
    mx.eval(float_model.parameters())
    print(f"Loaded float32 model from {ckpt_path}")

    # Data
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    train_examples = load_compile_examples(cfg.train_file)
    eval_examples = load_compile_examples(cfg.eval_file)
    train_seqs = tokenize_examples(train_examples, tokenizer, cfg.max_seq_len, cfg.eod_id)
    eval_seqs = tokenize_examples(eval_examples, tokenizer, cfg.max_seq_len, cfg.eod_id)

    eval_input, eval_target = make_eval_batch(eval_seqs, cfg.max_seq_len)

    # Baseline measurements
    baseline_loss = eval_loss(float_model, eval_input, eval_target)
    baseline_mspace = measure_mspace(float_model, cfg)
    print(f"Float32 baseline: eval loss = {baseline_loss:.4f}")
    for li, ms in baseline_mspace.items():
        print(f"  Layer {li}: rank90={ms['rank90']}, top1={ms['top1_pct']:.1f}%, σ0/σ1={ms['sigma_ratio']:.2f}")
    print()

    # ── Define cutting variants ──
    N_FILL_STEPS = 200
    FILL_LR = 3e-4

    variants = [
        {"name": "A. Float32 (no cut)", "zero_frac": 0.0, "use_mnoise": False, "n_flips": 0, "skip_cut": True},
        {"name": "B. Sign-only (±1)", "zero_frac": 0.0, "use_mnoise": False, "n_flips": 0, "skip_cut": False},
        {"name": "C. Light cut (10% zeros)", "zero_frac": 0.10, "use_mnoise": True, "n_flips": 0, "skip_cut": False},
        {"name": "D. Medium cut (30% zeros)", "zero_frac": 0.30, "use_mnoise": True, "n_flips": 0, "skip_cut": False},
        {"name": "E. Deep cut (50% zeros)", "zero_frac": 0.50, "use_mnoise": True, "n_flips": 0, "skip_cut": False},
        {"name": "F. Deep cut + 20 flips", "zero_frac": 0.50, "use_mnoise": True, "n_flips": 20, "skip_cut": False},
    ]

    results = {
        "baseline_loss": baseline_loss,
        "baseline_mspace": {str(k): v for k, v in baseline_mspace.items()},
        "n_fill_steps": N_FILL_STEPS,
        "fill_lr": FILL_LR,
        "variants": [],
    }

    for var in variants:
        print(f"{'─'*70}")
        print(f"  {var['name']}")
        print(f"{'─'*70}")

        # Fresh copy of the trained model for each variant
        model = MicroModel(cfg)
        model.load_weights(list(weights.items()))
        mx.eval(model.parameters())

        # ── CUT ──
        if not var["skip_cut"]:
            apply_cut(model, float_model, var["zero_frac"],
                      use_mspace_noise=var["use_mnoise"],
                      n_facet_flips=var["n_flips"])

        # Measure after cut
        cut_loss = eval_loss(model, eval_input, eval_target)
        cut_mspace = measure_mspace(model, cfg)
        kerf = cut_loss - baseline_loss

        print(f"  After cut:  loss = {cut_loss:.4f}  (kerf = {kerf:+.4f})")
        for li in [0, 2, 3]:
            ms = cut_mspace[li]
            print(f"    Layer {li}: rank90={ms['rank90']}, top1={ms['top1_pct']:.1f}%")

        # ── FILL (GD recovery) ──
        print(f"  Filling with {N_FILL_STEPS} steps of Adam (lr={FILL_LR})...")
        train_loader = SimpleDataLoader(
            train_seqs, cfg.batch_size, cfg.max_seq_len, cfg.eod_id, seed=42)

        fill_losses = gd_fill(model, train_loader, N_FILL_STEPS, lr=FILL_LR)

        # Measure after fill
        fill_loss = eval_loss(model, eval_input, eval_target)
        fill_mspace = measure_mspace(model, cfg)
        recovery = cut_loss - fill_loss  # positive = GD recovered
        residual = fill_loss - baseline_loss  # gap remaining vs float32

        print(f"  After fill: loss = {fill_loss:.4f}  (recovered {recovery:+.4f}, residual = {residual:+.4f})")
        for li in [0, 2, 3]:
            ms = fill_mspace[li]
            bms = baseline_mspace[li]
            print(f"    Layer {li}: rank90={ms['rank90']} (was {bms['rank90']}), "
                  f"top1={ms['top1_pct']:.1f}% (was {bms['top1_pct']:.1f}%)")

        # GD loss curve: sample points
        curve_points = []
        for i in [0, 4, 9, 19, 49, 99, 149, 199]:
            if i < len(fill_losses):
                curve_points.append({"step": i + 1, "train_loss": fill_losses[i]})

        result = {
            "name": var["name"],
            "zero_frac": var["zero_frac"],
            "n_flips": var["n_flips"],
            "cut_loss": cut_loss,
            "kerf": kerf,
            "fill_loss": fill_loss,
            "recovery": recovery,
            "residual": residual,
            "recovery_pct": recovery / max(kerf, 1e-8) * 100 if kerf > 0 else 0.0,
            "cut_mspace": {str(k): v for k, v in cut_mspace.items()},
            "fill_mspace": {str(k): v for k, v in fill_mspace.items()},
            "fill_curve": curve_points,
        }
        results["variants"].append(result)
        print()

    # ══════════════════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════════════════
    elapsed = time.time() - t0
    print("=" * 70)
    print("SUMMARY: CUT THEN FILL")
    print("=" * 70)
    print()
    print(f"Float32 baseline loss: {baseline_loss:.4f}")
    print()
    print(f"{'Variant':>30} │ {'Cut loss':>9} │ {'Kerf':>8} │ {'Fill loss':>9} │ {'Recovery':>9} │ {'Residual':>9} │ {'Recov%':>7}")
    print("─" * 100)

    for r in results["variants"]:
        name = r["name"][:30]
        cl = r["cut_loss"]
        k = r["kerf"]
        fl = r["fill_loss"]
        rec = r["recovery"]
        res = r["residual"]
        rpct = r["recovery_pct"]
        print(f"{name:>30} │ {cl:>9.4f} │ {k:>+8.4f} │ {fl:>9.4f} │ {rec:>+9.4f} │ {res:>+9.4f} │ {rpct:>6.1f}%")

    print()
    print("M-space quality after fill (layer 2 — the gem):")
    print(f"{'Variant':>30} │ {'rank90':>7} │ {'top1%':>7} │ {'σ0/σ1':>7}")
    print("─" * 60)
    for r in results["variants"]:
        ms = r["fill_mspace"]["2"]
        name = r["name"][:30]
        print(f"{name:>30} │ {ms['rank90']:>7} │ {ms['top1_pct']:>6.1f}% │ {ms['sigma_ratio']:>7.2f}")

    print()
    print(f"Elapsed: {elapsed:.1f}s")

    # Save
    out_dir = Path("results/cut-then-fill")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "summary.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {out_path}")


if __name__ == "__main__":
    run_experiment()
