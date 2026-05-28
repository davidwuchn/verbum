#!/usr/bin/env python3
"""
Train From Scratch With Pre-Cut Topology — The Real Test.

Does a geometrically-correct topology train better than random?
Does GD fill the gaps when the gem is pre-cut?

Variants (each trained from scratch for 5000 steps):
  A. Float32 baseline (no frozen topology — full GD)
  B. Frozen sign topology from trained model (±1, no zeros)
  C. Frozen sign topology + 30% M-noise zeros (the gem-cut)
  D. Random ternary topology (±1, no zeros — the null hypothesis)
  E. Random ternary + 30% random zeros

For B-E: Q and K attention weights are FROZEN ternary topology × learned gamma.
Everything else trains normally (norms, FFN, V, O, embeddings).
Gamma is per-row, initialized from |trained_W|.mean(axis=1) for B,C
and from Kaiming init for D,E.

License: MIT
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path
from functools import partial

# Force unbuffered stdout (critical when piped through tee)
sys.stdout.reconfigure(line_buffering=True)

import numpy as np
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim

sys.path.insert(0, str(Path(__file__).parent))
from micro_model import MicroModel, MicroConfig


# ══════════════════════════════════════════════════════════════════════
# Data (copied from train_micro.py for self-contained script)
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


class DataLoader:
    def __init__(self, sequences, batch_size, seq_len, eod_id=151643, seed=42):
        self.sequences = sequences
        self.batch_size = batch_size
        self.seq_len = seq_len
        self.eod_id = eod_id
        self.rng = np.random.RandomState(seed)
        self._rebuild()

    def _rebuild(self):
        indices = self.rng.permutation(len(self.sequences))
        all_tokens = [self.sequences[idx] for idx in indices]
        self.stream = np.concatenate(all_tokens)
        self.position = 0

    def next_batch(self):
        B, T = self.batch_size, self.seq_len
        needed = B * (T + 1)
        if self.position + needed > len(self.stream):
            self._rebuild()
        buf = self.stream[self.position:self.position + needed]
        self.position += needed
        buf = buf.reshape(B, T + 1)
        return mx.array(buf[:, :T]), mx.array(buf[:, 1:T + 1])


def make_eval_batch(sequences, max_seq_len=256):
    stream = np.concatenate(sequences)
    T = min(max_seq_len, len(stream) - 1)
    return mx.array(stream[:T].reshape(1, T)), mx.array(stream[1:T + 1].reshape(1, T))


# ══════════════════════════════════════════════════════════════════════
# M-space measurement
# ══════════════════════════════════════════════════════════════════════

def measure_mspace(model, cfg):
    mx.eval(model.parameters())  # ensure all weights are materialized
    results = {}
    for li in range(cfg.n_layers):
        W_q = np.array(model.blocks[li].attn.q_proj.weight)
        W_k = np.array(model.blocks[li].attn.k_proj.weight)
        M = W_q.T @ W_k
        U, s, Vt = np.linalg.svd(M, full_matrices=False)
        total = (s ** 2).sum()
        cum = np.cumsum(s ** 2) / total
        rank90 = int(np.searchsorted(cum, 0.90) + 1)
        top1 = float(cum[0] * 100)
        ratio = float(s[0] / s[1]) if len(s) > 1 and s[1] > 0 else float('inf')
        results[li] = {"rank90": rank90, "top1_pct": top1, "sigma_ratio": ratio}
    return results


# ══════════════════════════════════════════════════════════════════════
# Topology cutting
# ══════════════════════════════════════════════════════════════════════

def extract_trained_topology(trained_model, cfg):
    """Extract sign topology and gamma from trained model."""
    mx.eval(trained_model.parameters())
    topology = {}
    for li in range(cfg.n_layers):
        block = trained_model.blocks[li]
        for pname in ["q_proj", "k_proj"]:
            W = np.array(getattr(block.attn, pname).weight)
            gamma = np.abs(W).mean(axis=1, keepdims=True)  # (d_out, 1)
            signs = np.sign(W).astype(np.float32)
            signs[signs == 0] = 1.0
            topology[(li, pname)] = {"signs": signs, "gamma": gamma, "W_float": W}
    return topology


def compute_mnoise_mask(topology, cfg, zero_frac):
    """Compute M-noise zero masks for all Q/K projections."""
    masks = {}
    for li in range(cfg.n_layers):
        W_q_f = topology[(li, "q_proj")]["W_float"]
        W_k_f = topology[(li, "k_proj")]["W_float"]
        M_float = W_q_f.T @ W_k_f
        U, s, Vt = np.linalg.svd(M_float, full_matrices=False)
        total = (s ** 2).sum()
        cum = np.cumsum(s ** 2) / total
        K = int(np.searchsorted(cum, 0.90) + 1)

        # Noise per input dim: how much does this dim participate in noise modes?
        noise_per_dim = np.sum(U[:, K:] ** 2, axis=1)  # (d_in,)

        for pname in ["q_proj", "k_proj"]:
            W = topology[(li, pname)]["W_float"]
            gamma = topology[(li, pname)]["gamma"]
            rel_mag = np.abs(W) / (gamma + 1e-8)
            # Combined: high noise AND low magnitude → zero
            combined = noise_per_dim[np.newaxis, :] / (rel_mag + 0.1)
            flat = combined.flatten()
            n_zero = int(zero_frac * len(flat))
            mask = np.ones_like(combined, dtype=np.float32)
            if n_zero > 0:
                threshold = np.partition(flat, -n_zero)[-n_zero]
                mask[combined >= threshold] = 0.0
            masks[(li, pname)] = mask
    return masks


def apply_topology(model, cfg, topology, masks=None):
    """Apply frozen ternary topology to Q/K weights.

    Sets weight = signs * mask * gamma (if mask provided)
    or weight = signs * gamma (no mask).
    Then freezes Q/K weights.
    """
    for li in range(cfg.n_layers):
        block = model.blocks[li]
        for pname in ["q_proj", "k_proj"]:
            proj = getattr(block.attn, pname)
            signs = topology[(li, pname)]["signs"]
            gamma = topology[(li, pname)]["gamma"]

            if masks and (li, pname) in masks:
                mask = masks[(li, pname)]
                W_effective = signs * mask * gamma
            else:
                W_effective = signs * gamma

            proj.weight = mx.array(W_effective)
            proj.freeze(keys=["weight"])

    mx.eval(model.parameters())


def apply_random_topology(model, cfg, zero_frac=0.0, seed=123):
    """Apply random ternary topology to Q/K weights."""
    rng = np.random.RandomState(seed)
    for li in range(cfg.n_layers):
        block = model.blocks[li]
        for pname in ["q_proj", "k_proj"]:
            proj = getattr(block.attn, pname)
            W = np.array(proj.weight)
            d_out, d_in = W.shape

            # Random ternary signs
            signs = rng.choice([-1.0, 1.0], size=(d_out, d_in)).astype(np.float32)

            # Kaiming-derived gamma
            gamma = np.full((d_out, 1), math.sqrt(2.0 / d_in), dtype=np.float32)

            # Random zeros if requested
            if zero_frac > 0:
                mask = rng.random((d_out, d_in)) > zero_frac
                signs = signs * mask.astype(np.float32)

            W_effective = signs * gamma
            proj.weight = mx.array(W_effective)
            proj.freeze(keys=["weight"])

    mx.eval(model.parameters())


# ══════════════════════════════════════════════════════════════════════
# Training loop
# ══════════════════════════════════════════════════════════════════════

def train_variant(
    model, cfg, train_loader, eval_input, eval_target,
    total_steps=5000, lr=3e-4, warmup=100, log_interval=500,
):
    """Train model, return loss curve and checkpoints."""

    lr_schedule = optim.cosine_decay(lr, total_steps, lr * 0.01)
    warmup_schedule = optim.linear_schedule(1e-7, lr, warmup)

    def lr_fn(step):
        if step < warmup:
            return warmup_schedule(step)
        return lr_schedule(step)

    optimizer = optim.AdamW(learning_rate=lr_fn, weight_decay=0.01)

    def loss_fn(model, x, t):
        _, loss = model(x, t)
        return loss

    loss_and_grad = nn.value_and_grad(model, loss_fn)

    curve = []
    mspace_snapshots = []
    t_start = time.time()

    for step in range(1, total_steps + 1):
        model._training_step = step
        inp, tgt = train_loader.next_batch()
        loss_val, grads = loss_and_grad(model, inp, tgt)
        grads, gnorm = optim.clip_grad_norm(grads, 1.0)
        optimizer.update(model, grads)
        mx.eval(model.parameters(), optimizer.state, loss_val, gnorm)

        train_loss = float(loss_val.item())

        if step % log_interval == 0 or step == 1:
            # Eval loss
            _, eval_loss = model(eval_input, eval_target)
            mx.eval(eval_loss)
            eval_loss_val = float(eval_loss.item())

            elapsed = time.time() - t_start
            print(f"    step {step:>5}: train={train_loss:.4f}, eval={eval_loss_val:.4f}, "
                  f"gnorm={float(gnorm.item()):.2f}, {elapsed:.0f}s", flush=True)

            curve.append({
                "step": step,
                "train_loss": train_loss,
                "eval_loss": eval_loss_val,
            })

            if step % 1000 == 0 or step == total_steps:
                ms = measure_mspace(model, cfg)
                mspace_snapshots.append({
                    "step": step,
                    "mspace": {str(k): v for k, v in ms.items()},
                })

    return curve, mspace_snapshots


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    t0 = time.time()
    print("=" * 70)
    print("TRAIN FROM SCRATCH WITH PRE-CUT TOPOLOGY")
    print("=" * 70)
    print()

    cfg = MicroConfig()
    TOTAL_STEPS = 5000

    # ── Load trained model for topology extraction ──
    ckpt_path = Path("checkpoints/micro/final/model.npz")
    if not ckpt_path.exists():
        ckpt_path = Path("checkpoints/micro/step_005000/model.npz")

    trained_model = MicroModel(cfg)
    trained_weights = mx.load(str(ckpt_path))
    trained_model.load_weights(list(trained_weights.items()))
    mx.eval(trained_model.parameters())
    print(f"Loaded trained model from {ckpt_path}")

    # Extract topology
    topology = extract_trained_topology(trained_model, cfg)
    masks_30 = compute_mnoise_mask(topology, cfg, zero_frac=0.30)
    print("Extracted topology and computed 30% M-noise zero masks")

    # ── Data ──
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    train_examples = load_compile_examples(cfg.train_file)
    eval_examples = load_compile_examples(cfg.eval_file)
    train_seqs = tokenize_examples(train_examples, tokenizer, cfg.max_seq_len, cfg.eod_id)
    eval_seqs = tokenize_examples(eval_examples, tokenizer, cfg.max_seq_len, cfg.eod_id)
    eval_input, eval_target = make_eval_batch(eval_seqs, cfg.max_seq_len)
    print(f"Data: {len(train_examples)} train, {len(eval_examples)} eval")
    print()

    # ── Define variants ──
    variants = [
        {"name": "A. Float32 (full GD)", "type": "float32"},
        {"name": "B. Trained sign (±1)", "type": "trained_sign", "zeros": 0.0},
        {"name": "C. Trained sign + 30% M-zeros", "type": "trained_sign", "zeros": 0.30},
        {"name": "D. Random sign (±1)", "type": "random", "zeros": 0.0},
        {"name": "E. Random sign + 30% zeros", "type": "random", "zeros": 0.30},
    ]

    all_results = {
        "total_steps": TOTAL_STEPS,
        "variants": [],
    }

    for var in variants:
        print(f"{'═'*70}")
        print(f"  {var['name']}")
        print(f"{'═'*70}")

        # Fresh model for each variant
        model = MicroModel(cfg)
        mx.eval(model.parameters())

        # Apply topology
        if var["type"] == "trained_sign":
            if var["zeros"] > 0:
                apply_topology(model, cfg, topology, masks=masks_30)
            else:
                apply_topology(model, cfg, topology)
            # Count frozen params
            # Count trainable params
            from mlx.utils import tree_flatten
            n_trainable = sum(v.size for _, v in tree_flatten(model.trainable_parameters()))
            print(f"  Topology: trained sign, {var['zeros']*100:.0f}% zeros")
            print(f"  Trainable params: {n_trainable:,}")
        elif var["type"] == "random":
            apply_random_topology(model, cfg, zero_frac=var.get("zeros", 0.0))
            from mlx.utils import tree_flatten
            n_trainable = sum(v.size for _, v in tree_flatten(model.trainable_parameters()))
            print(f"  Topology: random ternary, {var.get('zeros', 0)*100:.0f}% zeros")
            print(f"  Trainable params: {n_trainable:,}")
        else:
            from mlx.utils import tree_flatten
            n_trainable = sum(v.size for _, v in tree_flatten(model.trainable_parameters()))
            print(f"  Topology: float32 (all trainable)")
            print(f"  Trainable params: {n_trainable:,}")

        # Initial M-space
        init_mspace = measure_mspace(model, cfg)
        print(f"  Initial M-space:", flush=True)
        for li in [0, 2]:
            ms = init_mspace[li]
            print(f"    Layer {li}: rank90={ms['rank90']}, top1={ms['top1_pct']:.1f}%, σ0/σ1={ms['sigma_ratio']:.2f}", flush=True)

        # Initial eval loss
        _, init_loss = model(eval_input, eval_target)
        mx.eval(init_loss)
        init_loss_val = float(init_loss.item())
        print(f"  Initial eval loss: {init_loss_val:.4f}", flush=True)
        print(flush=True)

        # Train
        train_loader = DataLoader(train_seqs, cfg.batch_size, cfg.max_seq_len, cfg.eod_id, seed=42)
        curve, mspace_snaps = train_variant(
            model, cfg, train_loader, eval_input, eval_target,
            total_steps=TOTAL_STEPS, log_interval=500)

        # Final measurements
        final_mspace = measure_mspace(model, cfg)
        _, final_loss = model(eval_input, eval_target)
        mx.eval(final_loss)
        final_loss_val = float(final_loss.item())

        print(f"\n  Final eval loss: {final_loss_val:.4f}")
        print(f"  Final M-space:")
        for li in [0, 2]:
            ms = final_mspace[li]
            print(f"    Layer {li}: rank90={ms['rank90']}, top1={ms['top1_pct']:.1f}%, σ0/σ1={ms['sigma_ratio']:.2f}")
        print()

        all_results["variants"].append({
            "name": var["name"],
            "type": var["type"],
            "zeros": var.get("zeros", 0.0),
            "init_loss": init_loss_val,
            "final_loss": final_loss_val,
            "init_mspace": {str(k): v for k, v in init_mspace.items()},
            "final_mspace": {str(k): v for k, v in final_mspace.items()},
            "curve": curve,
            "mspace_snapshots": mspace_snaps,
            "n_trainable": n_trainable,
        })

    # ══════════════════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════════════════
    elapsed = time.time() - t0
    print("=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print()
    print(f"{'Variant':>35} │ {'Init loss':>10} │ {'Final loss':>10} │ {'L2 rank90':>10} │ {'L2 top1%':>9}")
    print("─" * 85)
    for r in all_results["variants"]:
        name = r["name"][:35]
        il = r["init_loss"]
        fl = r["final_loss"]
        r90 = r["final_mspace"]["2"]["rank90"]
        t1 = r["final_mspace"]["2"]["top1_pct"]
        print(f"{name:>35} │ {il:>10.4f} │ {fl:>10.4f} │ {r90:>10} │ {t1:>8.1f}%")

    print()
    print(f"Total elapsed: {elapsed:.0f}s ({elapsed/60:.1f}m)")

    # Save
    out_dir = Path("results/cut-then-fill-scratch")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "summary.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"Saved to results/cut-then-fill-scratch/summary.json")


if __name__ == "__main__":
    main()
