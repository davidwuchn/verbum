#!/usr/bin/env python3
"""
train_etch_v3.py — Holographic Etch with Crystal Backbone.

Zeros are the lattice backbone — structural, not emergent.
They come from the crystal eigendecomposition / M-space SVD
of the teacher, not from training oscillation.

Flow:
  1. Load teacher → extract signs + compute M-space zero mask
  2. Initialize: zeros etched permanently (backbone), ±1 signs fluid
  3. Train: etch mechanism confirms/adjusts ±1 positions only
  4. Zeros never un-etch — they ARE the structure

Variants:
  A. Float32 baseline (diverse data)
  B. Crystal backbone 20% zeros + etch (teacher signs, diverse data)
  C. Crystal backbone 30% zeros + etch
  D. Crystal backbone 30% zeros, NO etch (frozen signs — session 166 comparison)

License: MIT
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)

import numpy as np
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim

sys.path.insert(0, str(Path(__file__).parent))
from micro_model import MicroModel, MicroConfig
from train_etch import EtchConfig, EtchState, measure_mspace
from train_etch_v2 import ShardDataLoader


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
    return mx.array(stream[:T].reshape(1, T)), mx.array(stream[1:T + 1].reshape(1, T))


# ══════════════════════════════════════════════════════════════════════
# Crystal backbone: M-space zero mask from teacher
# ══════════════════════════════════════════════════════════════════════

def compute_crystal_backbone(teacher_model, cfg, zero_frac: float) -> dict:
    """Compute M-space zero masks from teacher's attention weights.

    These zeros are the lattice backbone — structural positions where
    the crystal has no energy. They define the gaps between facets.

    Returns dict of (layer, proj_name) → {signs, gamma, mask}
    """
    mx.eval(teacher_model.parameters())
    topology = {}

    for li in range(cfg.n_layers):
        block = teacher_model.blocks[li]
        W_q = np.array(block.attn.q_proj.weight)
        W_k = np.array(block.attn.k_proj.weight)

        # M-space SVD
        M = W_q.T @ W_k
        U, s, Vt = np.linalg.svd(M, full_matrices=False)
        total = (s ** 2).sum()
        cum = np.cumsum(s ** 2) / total
        K = int(np.searchsorted(cum, 0.90) + 1)

        # Noise per input dim
        noise_per_dim = np.sum(U[:, K:] ** 2, axis=1)  # (d_in,)

        for pname, W in [("q_proj", W_q), ("k_proj", W_k)]:
            signs = np.sign(W).astype(np.float32)
            signs[signs == 0] = 1.0
            gamma = np.abs(W).mean(axis=1, keepdims=True)

            # M-noise score: high noise AND low relative magnitude → zero
            rel_mag = np.abs(W) / (gamma + 1e-8)
            combined = noise_per_dim[np.newaxis, :] / (rel_mag + 0.1)

            # Zero the top zero_frac positions by combined score
            flat = combined.flatten()
            n_zero = int(zero_frac * len(flat))
            mask = np.ones_like(combined, dtype=np.float32)
            if n_zero > 0:
                threshold = np.partition(flat, -n_zero)[-n_zero]
                mask[combined >= threshold] = 0.0

            topology[(li, pname)] = {
                "signs": signs,
                "gamma": gamma,
                "mask": mask,
                "K": K,
            }

    return topology


# ══════════════════════════════════════════════════════════════════════
# Training: etch with crystal backbone
# ══════════════════════════════════════════════════════════════════════

def train_with_backbone_etch(
    model, cfg, train_loader, eval_input, eval_target,
    etch_cfg: EtchConfig,
    topology: dict,
    total_steps: int = 5000,
    lr: float = 3e-4,
    warmup: int = 100,
    log_interval: int = 500,
):
    """Train with crystal backbone zeros (permanent) + etch for ±1 positions."""

    mx.eval(model.parameters())
    etch_states = {}
    gammas = {}

    n_backbone_zeros = 0
    n_total = 0

    for li in range(cfg.n_layers):
        for pname in ["q_proj", "k_proj"]:
            key = (li, pname)
            topo = topology[key]
            W = np.array(getattr(model.blocks[li].attn, pname).weight)
            state = EtchState(W.shape, etch_cfg)

            # Initialize signs from teacher
            state.initialize_signs_from(topo["signs"])

            # Etch backbone zeros permanently
            zero_positions = topo["mask"] == 0.0
            state.etch_mask[zero_positions] = True
            state.etch_value[zero_positions] = 0.0
            state.etch_step[zero_positions] = 0  # etched at init

            n_backbone_zeros += int(zero_positions.sum())
            n_total += int(np.prod(W.shape))

            etch_states[key] = state
            gammas[key] = mx.array(topo["gamma"].copy())

    backbone_pct = n_backbone_zeros / n_total * 100
    print(f"    Backbone: {n_backbone_zeros:,}/{n_total:,} zeros ({backbone_pct:.1f}%)")

    # ── Optimizer ──
    lr_schedule = optim.cosine_decay(lr, total_steps, lr * 0.01)
    warmup_schedule = optim.linear_schedule(1e-7, lr, warmup)
    def lr_fn(step):
        return warmup_schedule(step) if step < warmup else lr_schedule(step)

    optimizer = optim.AdamW(learning_rate=lr_fn, weight_decay=0.01)

    def apply_etch_weights():
        for li in range(cfg.n_layers):
            for pname in ["q_proj", "k_proj"]:
                key = (li, pname)
                state = etch_states[key]
                gamma = np.array(gammas[key])
                W_eff = state.get_effective_weight(gamma)
                getattr(model.blocks[li].attn, pname).weight = mx.array(W_eff)

    def loss_fn(model, x, t):
        _, loss = model(x, t)
        return loss

    loss_and_grad = nn.value_and_grad(model, loss_fn)

    curve = []
    etch_history = []
    t_start = time.time()

    apply_etch_weights()
    mx.eval(model.parameters())

    for step in range(1, total_steps + 1):
        model._training_step = step
        inp, tgt = train_loader.next_batch()

        loss_val, grads = loss_and_grad(model, inp, tgt)
        grads, gnorm = optim.clip_grad_norm(grads, 1.0)

        # Extract Q/K gradients, zero them for optimizer
        qk_grads = {}
        for li in range(cfg.n_layers):
            for pname in ["q_proj", "k_proj"]:
                key = (li, pname)
                grad_w = grads["blocks"][li]["attn"][pname]["weight"]
                qk_grads[key] = np.array(grad_w)
                grads["blocks"][li]["attn"][pname]["weight"] = mx.zeros_like(grad_w)

        optimizer.update(model, grads)
        mx.eval(model.parameters(), optimizer.state, loss_val, gnorm)

        # Gamma update
        gamma_lr_val = lr_fn(step)
        gamma_lr = float(gamma_lr_val.item() if isinstance(gamma_lr_val, mx.array) else gamma_lr_val)
        for key, grad in qk_grads.items():
            state = etch_states[key]
            gamma_np = np.array(gammas[key])
            gamma_grad = (state.get_effective_weight(np.ones_like(gamma_np)) * grad).mean(axis=1, keepdims=True)
            gamma_np -= gamma_lr * gamma_grad
            gamma_np = np.maximum(gamma_np, 1e-6)
            gammas[key] = mx.array(gamma_np)

        # TD updates (fluid ±1 positions only — backbone zeros are frozen)
        for key, grad in qk_grads.items():
            state = etch_states[key]
            state.update_td(grad, step)
            state.check_flips(step)
            state.update_opposition(grad)
            if step % 50 == 0:
                state.decay_flip_window(step)

        # Etch gate (for ±1 positions, NOT backbone zeros)
        etch_stats_this_step = None
        if step % etch_cfg.etch_interval == 0 and step >= etch_cfg.etch_warmup:
            total_stats = {"etched_plus": 0, "etched_minus": 0, "etched_zero": 0, "unetched": 0}
            for key in etch_states:
                s = etch_states[key].run_etch_gate(step)
                for k in total_stats:
                    total_stats[k] += s[k]
            etch_stats_this_step = total_stats

        apply_etch_weights()
        mx.eval(model.parameters())

        # Logging
        train_loss = float(loss_val.item())
        if step % log_interval == 0 or step == 1:
            _, eval_loss = model(eval_input, eval_target)
            mx.eval(eval_loss)
            eval_loss_val = float(eval_loss.item())
            elapsed = time.time() - t_start

            total_pos = 0
            total_etched = 0
            total_backbone = 0
            total_etched_sign = 0
            total_fluid = 0
            total_flips = 0
            for key, state in etch_states.items():
                s = state.summary()
                total_pos += s["total"]
                total_etched += s["etched"]
                total_backbone += s["etched_zero"]
                total_etched_sign += s["etched_nonzero"]
                total_fluid += s["fluid"]
                total_flips += int(state.flip_count.sum())

            sign_etch_pct = total_etched_sign / (total_pos - total_backbone) * 100 if (total_pos - total_backbone) > 0 else 0
            total_etch_pct = total_etched / total_pos * 100

            print(
                f"  step {step:>5}: train={train_loss:.4f} eval={eval_loss_val:.4f} "
                f"gnorm={float(gnorm.item()):.2f} | "
                f"total_etch={total_etch_pct:.1f}% sign_etch={sign_etch_pct:.1f}% "
                f"backbone={total_backbone} flips={total_flips} | "
                f"{elapsed:.0f}s",
                flush=True,
            )
            if etch_stats_this_step:
                es = etch_stats_this_step
                print(
                    f"         etch: +1={es['etched_plus']} -1={es['etched_minus']} "
                    f"0={es['etched_zero']} un={es['unetched']}",
                    flush=True,
                )

            curve.append({
                "step": step,
                "train_loss": train_loss,
                "eval_loss": eval_loss_val,
                "total_etch_pct": total_etch_pct,
                "sign_etch_pct": sign_etch_pct,
                "backbone_zeros": total_backbone,
                "total_flips": total_flips,
            })
            etch_history.append({
                "step": step,
                "total_etch_pct": total_etch_pct,
                "sign_etch_pct": sign_etch_pct,
            })

        if step % etch_cfg.mspace_interval == 0:
            ms = measure_mspace(model, cfg)
            print(f"         M-space:", end="", flush=True)
            for li in range(cfg.n_layers):
                m = ms[li]
                print(f" L{li}:r90={m['rank90']},t1={m['top1_pct']:.1f}%", end="")
            print(flush=True)

    # Per-layer summary
    print("\n  Per-layer summary:")
    for li in range(cfg.n_layers):
        for pname in ["q_proj", "k_proj"]:
            key = (li, pname)
            s = etch_states[key].summary()
            print(
                f"    L{li}.{pname}: total_etch={s['etched_pct']:.1f}% "
                f"(±1={s['etched_nonzero']}, 0={s['etched_zero']}) "
                f"fluid={s['fluid_pct']:.1f}%"
            )

    return curve, etch_history


# ══════════════════════════════════════════════════════════════════════
# Training: frozen topology (no etch — session 166 comparison)
# ══════════════════════════════════════════════════════════════════════

def train_frozen_topology(
    model, cfg, train_loader, eval_input, eval_target,
    topology: dict,
    total_steps: int = 5000,
    lr: float = 3e-4,
    warmup: int = 100,
    log_interval: int = 500,
):
    """Frozen ternary topology (signs + zeros) × learned gamma. No etch."""

    mx.eval(model.parameters())
    n_zeros = 0
    n_total = 0

    # Apply frozen topology
    for li in range(cfg.n_layers):
        block = model.blocks[li]
        for pname in ["q_proj", "k_proj"]:
            key = (li, pname)
            topo = topology[key]
            W_eff = topo["signs"] * topo["mask"] * topo["gamma"]
            getattr(block.attn, pname).weight = mx.array(W_eff)
            getattr(block.attn, pname).freeze(keys=["weight"])
            n_zeros += int((topo["mask"] == 0).sum())
            n_total += int(np.prod(topo["mask"].shape))

    mx.eval(model.parameters())
    print(f"    Frozen: {n_zeros:,}/{n_total:,} zeros ({n_zeros/n_total*100:.1f}%)")

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
            _, eval_loss = model(eval_input, eval_target)
            mx.eval(eval_loss)
            elapsed = time.time() - t_start
            print(
                f"  step {step:>5}: train={float(loss_val.item()):.4f} "
                f"eval={float(eval_loss.item()):.4f} "
                f"gnorm={float(gnorm.item()):.2f} | {elapsed:.0f}s",
                flush=True,
            )
            curve.append({
                "step": step,
                "train_loss": float(loss_val.item()),
                "eval_loss": float(eval_loss.item()),
            })

    return curve


# ══════════════════════════════════════════════════════════════════════
# Float32 baseline
# ══════════════════════════════════════════════════════════════════════

def train_float32(model, cfg, train_loader, eval_input, eval_target,
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
            _, eval_loss = model(eval_input, eval_target)
            mx.eval(eval_loss)
            elapsed = time.time() - t_start
            print(
                f"  step {step:>5}: train={float(loss_val.item()):.4f} "
                f"eval={float(eval_loss.item()):.4f} "
                f"gnorm={float(gnorm.item()):.2f} | {elapsed:.0f}s",
                flush=True,
            )
            curve.append({
                "step": step,
                "train_loss": float(loss_val.item()),
                "eval_loss": float(eval_loss.item()),
            })

    return curve


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    t0 = time.time()
    print("=" * 70)
    print("HOLOGRAPHIC ETCH v3 — CRYSTAL BACKBONE")
    print("Zeros are structure, not emergent. They come from the crystal.")
    print("=" * 70)
    print()

    cfg = MicroConfig()
    TOTAL_STEPS = 5000
    SHARD_PATH = "data/structured_shard_v2.npy"

    # ── Eval data ──
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    eval_examples = load_compile_examples(cfg.eval_file)
    eval_seqs = tokenize_examples(eval_examples, tokenizer, cfg.max_seq_len, cfg.eod_id)
    eval_input, eval_target = make_eval_batch(eval_seqs, cfg.max_seq_len)
    print(f"Eval: {len(eval_examples)} compile examples")

    # ── Teacher + crystal backbone ──
    ckpt_path = Path("checkpoints/micro/final/model.npz")
    teacher = MicroModel(cfg)
    teacher.load_weights(list(mx.load(str(ckpt_path)).items()))
    mx.eval(teacher.parameters())
    print(f"Teacher: {ckpt_path}")

    topo_20 = compute_crystal_backbone(teacher, cfg, zero_frac=0.20)
    topo_30 = compute_crystal_backbone(teacher, cfg, zero_frac=0.30)

    ms_teacher = measure_mspace(teacher, cfg)
    print("Teacher M-space:")
    for li in range(cfg.n_layers):
        m = ms_teacher[li]
        print(f"  L{li}: rank90={m['rank90']}, top1={m['top1_pct']:.1f}%, K={topo_30[(li,'q_proj')]['K']} signal modes")
    del teacher
    print()

    # ── Etch config ──
    etch_cfg = EtchConfig(
        ema_alpha=0.05,
        tau_coherent=0.4,
        tau_zero=0.15,
        tau_cold=0.1,
        tau_hot=0.15,
        flip_threshold=0.25,
        mag_threshold=0.001,
        etch_interval=100,
        etch_warmup=300,
        flip_window=200,
        mspace_interval=1000,
        tau_unetch=0.8,
        opposition_alpha=0.01,
    )

    all_results = {"total_steps": TOTAL_STEPS, "variants": []}

    # ═══════════════════════════════════════════════════════════════
    # A. Float32 baseline
    # ═══════════════════════════════════════════════════════════════
    print("═" * 70)
    print("  A. Float32 baseline (diverse data)")
    print("═" * 70)
    model_a = MicroModel(cfg)
    mx.eval(model_a.parameters())
    loader = ShardDataLoader(SHARD_PATH, cfg.batch_size, cfg.max_seq_len, seed=42)
    curve_a = train_float32(model_a, cfg, loader, eval_input, eval_target, TOTAL_STEPS)
    ms_a = measure_mspace(model_a, cfg)
    _, final_a = model_a(eval_input, eval_target); mx.eval(final_a)
    loss_a = float(final_a.item())
    print(f"\n  Final: loss={loss_a:.4f} L2:r90={ms_a[2]['rank90']},t1={ms_a[2]['top1_pct']:.1f}%\n")
    all_results["variants"].append({"name": "A. Float32", "loss": loss_a,
        "mspace": {str(k): v for k, v in ms_a.items()}, "curve": curve_a})

    # ═══════════════════════════════════════════════════════════════
    # B. Crystal backbone 20% + etch
    # ═══════════════════════════════════════════════════════════════
    print("═" * 70)
    print("  B. Crystal backbone 20% zeros + etch")
    print("═" * 70)
    model_b = MicroModel(cfg)
    mx.eval(model_b.parameters())
    loader = ShardDataLoader(SHARD_PATH, cfg.batch_size, cfg.max_seq_len, seed=42)
    curve_b, hist_b = train_with_backbone_etch(
        model_b, cfg, loader, eval_input, eval_target, etch_cfg, topo_20, TOTAL_STEPS)
    ms_b = measure_mspace(model_b, cfg)
    _, final_b = model_b(eval_input, eval_target); mx.eval(final_b)
    loss_b = float(final_b.item())
    print(f"\n  Final: loss={loss_b:.4f} L2:r90={ms_b[2]['rank90']},t1={ms_b[2]['top1_pct']:.1f}%\n")
    all_results["variants"].append({"name": "B. Backbone 20% + etch", "loss": loss_b,
        "mspace": {str(k): v for k, v in ms_b.items()}, "curve": curve_b, "etch": hist_b})

    # ═══════════════════════════════════════════════════════════════
    # C. Crystal backbone 30% + etch
    # ═══════════════════════════════════════════════════════════════
    print("═" * 70)
    print("  C. Crystal backbone 30% zeros + etch")
    print("═" * 70)
    model_c = MicroModel(cfg)
    mx.eval(model_c.parameters())
    loader = ShardDataLoader(SHARD_PATH, cfg.batch_size, cfg.max_seq_len, seed=42)
    curve_c, hist_c = train_with_backbone_etch(
        model_c, cfg, loader, eval_input, eval_target, etch_cfg, topo_30, TOTAL_STEPS)
    ms_c = measure_mspace(model_c, cfg)
    _, final_c = model_c(eval_input, eval_target); mx.eval(final_c)
    loss_c = float(final_c.item())
    print(f"\n  Final: loss={loss_c:.4f} L2:r90={ms_c[2]['rank90']},t1={ms_c[2]['top1_pct']:.1f}%\n")
    all_results["variants"].append({"name": "C. Backbone 30% + etch", "loss": loss_c,
        "mspace": {str(k): v for k, v in ms_c.items()}, "curve": curve_c, "etch": hist_c})

    # ═══════════════════════════════════════════════════════════════
    # D. Frozen topology 30% (no etch — session 166 comparison)
    # ═══════════════════════════════════════════════════════════════
    print("═" * 70)
    print("  D. Frozen topology 30% zeros (no etch)")
    print("═" * 70)
    model_d = MicroModel(cfg)
    mx.eval(model_d.parameters())
    loader = ShardDataLoader(SHARD_PATH, cfg.batch_size, cfg.max_seq_len, seed=42)
    curve_d = train_frozen_topology(model_d, cfg, loader, eval_input, eval_target, topo_30, TOTAL_STEPS)
    ms_d = measure_mspace(model_d, cfg)
    _, final_d = model_d(eval_input, eval_target); mx.eval(final_d)
    loss_d = float(final_d.item())
    print(f"\n  Final: loss={loss_d:.4f} L2:r90={ms_d[2]['rank90']},t1={ms_d[2]['top1_pct']:.1f}%\n")
    all_results["variants"].append({"name": "D. Frozen 30% (no etch)", "loss": loss_d,
        "mspace": {str(k): v for k, v in ms_d.items()}, "curve": curve_d})

    # ═══════════════════════════════════════════════════════════════
    # Summary
    # ═══════════════════════════════════════════════════════════════
    elapsed = time.time() - t0
    print("=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print()
    print(f"  {'Variant':<45} {'Loss':>8}  {'L2:r90':>6}  {'L2:t1%':>7}")
    print("  " + "─" * 70)
    for r in all_results["variants"]:
        ms = r.get("mspace", {})
        r90 = ms.get("2", {}).get("rank90", "?")
        t1 = ms.get("2", {}).get("top1_pct", 0)
        print(f"  {r['name']:<45} {r['loss']:>8.4f}  {r90:>6}  {t1:>6.1f}%")
    print(f"\n  Teacher reference:                               "
          f"{ms_teacher[2]['rank90']:>6}  {ms_teacher[2]['top1_pct']:>6.1f}%")
    print(f"\n  Total elapsed: {elapsed:.0f}s ({elapsed/60:.1f}m)")

    out_dir = Path("results/holographic-etch-micro")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "summary_v3.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"  Saved to {out_dir}/summary_v3.json")


if __name__ == "__main__":
    main()
