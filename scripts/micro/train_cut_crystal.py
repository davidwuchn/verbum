#!/usr/bin/env python3
"""
Train From Scratch — Crystal Subspace Zeros Variant.

Adds two new variants to compare against the 5 from train_cut_topology.py:
  F. Trained sign + 30% crystal-null zeros (structural denoising)
  G. Trained sign + crystal columns + M-noise positions (combined)

Reuses the same training setup (5000 steps, same data, same hyperparams)
so results are directly comparable.

Existing results (from train_cut_topology.py):
  A. Float32 (full GD):            loss 6.7412, L2 rank90=6
  B. Trained sign (±1):            loss 6.8625, L2 rank90=32
  C. Trained sign + 30% M-zeros:   loss 6.6972, L2 rank90=25
  D. Random sign (±1):             loss 6.6814, L2 rank90=48
  E. Random sign + 30% zeros:      loss 6.7721, L2 rank90=48

License: MIT
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)

import numpy as np
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
from mlx.utils import tree_flatten

sys.path.insert(0, str(Path(__file__).parent))
from micro_model import MicroModel, MicroConfig


# ══════════════════════════════════════════════════════════════════════
# Data (same as train_cut_topology.py)
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
        self.rng = np.random.RandomState(seed)
        self._rebuild()

    def _rebuild(self):
        indices = self.rng.permutation(len(self.sequences))
        self.stream = np.concatenate([self.sequences[i] for i in indices])
        self.position = 0

    def next_batch(self):
        B, T = self.batch_size, self.seq_len
        needed = B * (T + 1)
        if self.position + needed > len(self.stream):
            self._rebuild()
        buf = self.stream[self.position:self.position + needed].reshape(B, T + 1)
        self.position += needed
        return mx.array(buf[:, :T]), mx.array(buf[:, 1:T + 1])

def make_eval_batch(sequences, max_seq_len=256):
    stream = np.concatenate(sequences)
    T = min(max_seq_len, len(stream) - 1)
    return mx.array(stream[:T].reshape(1, T)), mx.array(stream[1:T+1].reshape(1, T))


# ══════════════════════════════════════════════════════════════════════
# M-space measurement
# ══════════════════════════════════════════════════════════════════════

def measure_mspace(model, cfg):
    mx.eval(model.parameters())
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

def eval_loss(model, eval_input, eval_target):
    _, loss = model(eval_input, eval_target)
    mx.eval(loss)
    return float(loss.item())


# ══════════════════════════════════════════════════════════════════════
# Crystal + M-noise zero placement
# ══════════════════════════════════════════════════════════════════════

def compute_crystal_null_dims(model, zero_frac):
    """Identify d_model dimensions in the crystal null space.

    Returns: sorted array of dim indices to zero (lowest crystal energy first).
    """
    mx.eval(model.parameters())
    C = np.array(model.get_all_crystal_embeddings())  # (16, d_model)
    U, s, Vt = np.linalg.svd(C, full_matrices=False)

    # Per-dimension crystal energy (unweighted)
    crystal_energy = np.sum(Vt ** 2, axis=0)  # (d_model,)
    d_model = len(crystal_energy)
    n_zero = max(1, int(zero_frac * d_model))
    zero_dims = np.argsort(crystal_energy)[:n_zero]
    return zero_dims, crystal_energy


def apply_crystal_null_topology(model, cfg, trained_model, zero_frac=0.30):
    """Apply trained sign topology with crystal-null-space zeros.

    Zeros entire COLUMNS (input dimensions) that are in the crystal null space.
    Same columns zeroed for every row and every Q/K matrix.
    """
    mx.eval(trained_model.parameters())
    zero_dims, crystal_energy = compute_crystal_null_dims(trained_model, zero_frac)

    for li in range(cfg.n_layers):
        block = model.blocks[li]
        trained_block = trained_model.blocks[li]

        for pname in ["q_proj", "k_proj"]:
            W_float = np.array(getattr(trained_block.attn, pname).weight)
            gamma = np.abs(W_float).mean(axis=1, keepdims=True)

            W_ternary = np.sign(W_float).astype(np.float32)
            W_ternary[W_ternary == 0] = 1.0
            W_ternary[:, zero_dims] = 0.0  # zero entire columns

            proj = getattr(block.attn, pname)
            proj.weight = mx.array(W_ternary * gamma)
            proj.freeze(keys=["weight"])

    mx.eval(model.parameters())
    return zero_dims


def apply_combined_topology(model, cfg, trained_model,
                            crystal_frac=0.15, mnoise_frac=0.15):
    """Apply trained sign topology with combined crystal + M-noise zeros.

    Phase 1: Zero crystal-null columns (structural — 15% of dims)
    Phase 2: Within remaining positions, zero by M-noise (surgical — 15% more)
    Total: ~30% zeros, but placed with both structural AND per-position guidance.
    """
    mx.eval(trained_model.parameters())
    zero_dims, crystal_energy = compute_crystal_null_dims(trained_model, crystal_frac)

    for li in range(cfg.n_layers):
        block = model.blocks[li]
        trained_block = trained_model.blocks[li]

        W_q_float = np.array(trained_block.attn.q_proj.weight)
        W_k_float = np.array(trained_block.attn.k_proj.weight)

        # Compute M-space SVD for M-noise scoring
        M_float = W_q_float.T @ W_k_float
        U_m, s_m, Vt_m = np.linalg.svd(M_float, full_matrices=False)
        total_m = (s_m ** 2).sum()
        cum_m = np.cumsum(s_m ** 2) / total_m
        K = int(np.searchsorted(cum_m, 0.90) + 1)
        noise_per_dim = np.sum(U_m[:, K:] ** 2, axis=1)

        for pname in ["q_proj", "k_proj"]:
            W_float = np.array(getattr(trained_block.attn, pname).weight)
            gamma = np.abs(W_float).mean(axis=1, keepdims=True)

            W_ternary = np.sign(W_float).astype(np.float32)
            W_ternary[W_ternary == 0] = 1.0

            # Phase 1: crystal-null columns
            W_ternary[:, zero_dims] = 0.0

            # Phase 2: M-noise zeros in remaining positions
            rel_mag = np.abs(W_float) / (gamma + 1e-8)
            combined = noise_per_dim[np.newaxis, :] / (rel_mag + 0.1)
            # Mask out already-zeroed positions
            combined[:, zero_dims] = -np.inf
            # Zero the noisiest remaining positions
            non_zero_mask = W_ternary != 0
            remaining = combined[non_zero_mask]
            n_remaining = len(remaining)
            n_mnoise_zero = int(mnoise_frac * W_ternary.size)
            if n_mnoise_zero > 0 and n_remaining > n_mnoise_zero:
                threshold = np.partition(remaining, -n_mnoise_zero)[-n_mnoise_zero]
                mnoise_mask = (combined >= threshold) & non_zero_mask
                W_ternary[mnoise_mask] = 0.0

            proj = getattr(block.attn, pname)
            proj.weight = mx.array(W_ternary * gamma)
            proj.freeze(keys=["weight"])

    mx.eval(model.parameters())


# ══════════════════════════════════════════════════════════════════════
# Training loop (identical to train_cut_topology.py)
# ══════════════════════════════════════════════════════════════════════

def train_variant(model, cfg, train_loader, eval_input, eval_target,
                  total_steps=5000, lr=3e-4, warmup=100, log_interval=500):
    lr_schedule = optim.cosine_decay(lr, total_steps, lr * 0.01)
    warmup_schedule = optim.linear_schedule(1e-7, lr, warmup)

    def lr_fn(step):
        return warmup_schedule(step) if step < warmup else lr_schedule(step)

    optimizer = optim.AdamW(learning_rate=lr_fn, weight_decay=0.01)

    def loss_fn(model, x, t):
        _, loss = model(x, t)
        return loss

    loss_and_grad = nn.value_and_grad(model, loss_fn)
    curve = []
    t_start = time.time()

    for step in range(1, total_steps + 1):
        model._training_step = step
        inp, tgt = train_loader.next_batch()
        loss_val, grads = loss_and_grad(model, inp, tgt)
        grads, gnorm = optim.clip_grad_norm(grads, 1.0)
        optimizer.update(model, grads)
        mx.eval(model.parameters(), optimizer.state, loss_val, gnorm)

        if step % log_interval == 0 or step == 1:
            _, eval_loss_t = model(eval_input, eval_target)
            mx.eval(eval_loss_t)
            elapsed = time.time() - t_start
            tl = float(loss_val.item())
            el = float(eval_loss_t.item())
            print(f"    step {step:>5}: train={tl:.4f}, eval={el:.4f}, "
                  f"gnorm={float(gnorm.item()):.2f}, {elapsed:.0f}s", flush=True)
            curve.append({"step": step, "train_loss": tl, "eval_loss": el})

    return curve


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    t0 = time.time()
    print("=" * 70, flush=True)
    print("CRYSTAL ZEROS — New Variants for Comparison", flush=True)
    print("=" * 70, flush=True)
    print(flush=True)

    cfg = MicroConfig()

    # Load trained model
    ckpt_path = Path("checkpoints/micro/final/model.npz")
    trained_weights = mx.load(str(ckpt_path))
    trained_model = MicroModel(cfg)
    trained_model.load_weights(list(trained_weights.items()))
    mx.eval(trained_model.parameters())
    print(f"Loaded trained model from {ckpt_path}", flush=True)

    # Data
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    train_examples = load_compile_examples(cfg.train_file)
    eval_examples = load_compile_examples(cfg.eval_file)
    train_seqs = tokenize_examples(train_examples, tokenizer, cfg.max_seq_len, cfg.eod_id)
    eval_seqs = tokenize_examples(eval_examples, tokenizer, cfg.max_seq_len, cfg.eod_id)
    eval_input, eval_target = make_eval_batch(eval_seqs, cfg.max_seq_len)

    baseline_loss = eval_loss(trained_model, eval_input, eval_target)
    print(f"Baseline (trained float32) eval loss: {baseline_loss:.4f}", flush=True)

    # Crystal subspace info
    zero_dims, ce = compute_crystal_null_dims(trained_model, 0.30)
    print(f"Crystal null dims (30%): {len(zero_dims)}/{cfg.d_model} dims zeroed", flush=True)
    print(flush=True)

    # ── Existing results for comparison ──
    print("Existing results (from train_cut_topology.py):", flush=True)
    print("  A. Float32:              loss 6.7412, L2 rank90=6", flush=True)
    print("  B. Trained sign (±1):    loss 6.8625, L2 rank90=32", flush=True)
    print("  C. Sign + 30% M-zeros:   loss 6.6972, L2 rank90=25", flush=True)
    print("  D. Random sign (±1):     loss 6.6814, L2 rank90=48", flush=True)
    print("  E. Random + 30% zeros:   loss 6.7721, L2 rank90=48", flush=True)
    print(flush=True)

    results = {"variants": []}

    # ── Variant F: Crystal null zeros ──
    print(f"{'═'*70}", flush=True)
    print("  F. Trained sign + 30% crystal-null zeros", flush=True)
    print(f"{'═'*70}", flush=True)

    model_f = MicroModel(cfg)
    mx.eval(model_f.parameters())
    zdims = apply_crystal_null_topology(model_f, cfg, trained_model, zero_frac=0.30)

    init_mspace_f = measure_mspace(model_f, cfg)
    init_loss_f = eval_loss(model_f, eval_input, eval_target)
    actual_zero_frac = sum(
        (np.array(model_f.blocks[li].attn.q_proj.weight) == 0).mean()
        for li in range(cfg.n_layers)
    ) / cfg.n_layers
    print(f"  Actual zero fraction: {actual_zero_frac:.1%}", flush=True)
    print(f"  Initial M-space:", flush=True)
    for li in [0, 2]:
        ms = init_mspace_f[li]
        print(f"    Layer {li}: rank90={ms['rank90']}, top1={ms['top1_pct']:.1f}%", flush=True)
    print(f"  Initial eval loss: {init_loss_f:.4f}", flush=True)
    print(flush=True)

    train_loader = DataLoader(train_seqs, cfg.batch_size, cfg.max_seq_len, cfg.eod_id, seed=42)
    curve_f = train_variant(model_f, cfg, train_loader, eval_input, eval_target)
    final_mspace_f = measure_mspace(model_f, cfg)
    final_loss_f = eval_loss(model_f, eval_input, eval_target)
    print(f"\n  Final: loss={final_loss_f:.4f}, L2 rank90={final_mspace_f[2]['rank90']}, "
          f"top1={final_mspace_f[2]['top1_pct']:.1f}%", flush=True)

    results["variants"].append({
        "name": "F. Trained sign + 30% crystal-null zeros",
        "final_loss": final_loss_f,
        "final_mspace": {str(k): v for k, v in final_mspace_f.items()},
        "curve": curve_f,
    })

    # ── Variant G: Combined crystal + M-noise ──
    print(f"\n{'═'*70}", flush=True)
    print("  G. Trained sign + 15% crystal + 15% M-noise zeros", flush=True)
    print(f"{'═'*70}", flush=True)

    model_g = MicroModel(cfg)
    mx.eval(model_g.parameters())
    apply_combined_topology(model_g, cfg, trained_model,
                            crystal_frac=0.15, mnoise_frac=0.15)

    init_mspace_g = measure_mspace(model_g, cfg)
    init_loss_g = eval_loss(model_g, eval_input, eval_target)
    actual_zero_frac_g = sum(
        (np.array(model_g.blocks[li].attn.q_proj.weight) == 0).mean()
        for li in range(cfg.n_layers)
    ) / cfg.n_layers
    print(f"  Actual zero fraction: {actual_zero_frac_g:.1%}", flush=True)
    print(f"  Initial M-space:", flush=True)
    for li in [0, 2]:
        ms = init_mspace_g[li]
        print(f"    Layer {li}: rank90={ms['rank90']}, top1={ms['top1_pct']:.1f}%", flush=True)
    print(f"  Initial eval loss: {init_loss_g:.4f}", flush=True)
    print(flush=True)

    train_loader = DataLoader(train_seqs, cfg.batch_size, cfg.max_seq_len, cfg.eod_id, seed=42)
    curve_g = train_variant(model_g, cfg, train_loader, eval_input, eval_target)
    final_mspace_g = measure_mspace(model_g, cfg)
    final_loss_g = eval_loss(model_g, eval_input, eval_target)
    print(f"\n  Final: loss={final_loss_g:.4f}, L2 rank90={final_mspace_g[2]['rank90']}, "
          f"top1={final_mspace_g[2]['top1_pct']:.1f}%", flush=True)

    results["variants"].append({
        "name": "G. Trained sign + 15% crystal + 15% M-noise zeros",
        "final_loss": final_loss_g,
        "final_mspace": {str(k): v for k, v in final_mspace_g.items()},
        "curve": curve_g,
    })

    # ── Combined Summary ──
    elapsed = time.time() - t0
    print(f"\n{'═'*70}", flush=True)
    print("ALL VARIANTS COMPARISON", flush=True)
    print(f"{'═'*70}", flush=True)
    print(flush=True)

    all_variants = [
        ("A. Float32 (full GD)",            6.7412,  6, 80.5),
        ("B. Trained sign (±1)",            6.8625, 32, 45.5),
        ("C. Sign + 30% M-zeros",           6.6972, 25, 56.1),
        ("D. Random sign (±1)",             6.6814, 48,  4.8),
        ("E. Random + 30% zeros",           6.7721, 48,  5.6),
        ("F. Sign + 30% crystal-null",      final_loss_f,
         final_mspace_f[2]["rank90"], final_mspace_f[2]["top1_pct"]),
        ("G. Sign + 15% crystal + 15% M",  final_loss_g,
         final_mspace_g[2]["rank90"], final_mspace_g[2]["top1_pct"]),
    ]

    print(f"{'Variant':>35} │ {'Loss':>8} │ {'vs Float':>8} │ {'L2 r90':>6} │ {'L2 top1':>7}", flush=True)
    print("─" * 75, flush=True)
    for name, loss, r90, t1 in all_variants:
        delta = loss - 6.7412
        marker = " ★" if loss == min(v[1] for v in all_variants) else ""
        print(f"{name:>35} │ {loss:>8.4f} │ {delta:>+8.4f} │ {r90:>6} │ {t1:>6.1f}%{marker}", flush=True)

    print(f"\nElapsed: {elapsed:.0f}s ({elapsed/60:.1f}m)", flush=True)

    out_dir = Path("results/crystal-zeros-train")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "summary.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved to results/crystal-zeros-train/summary.json", flush=True)


if __name__ == "__main__":
    main()
