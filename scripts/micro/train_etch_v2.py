#!/usr/bin/env python3
"""
train_etch_v2.py — Holographic Etch on Micro Model (diverse data).

Same etch mechanism as v1 but trained on the structured shard —
diverse mixed data (arithmetic, lambda, list ops, combinators).
1.2M tokens vs 509 examples. The model is capacity-constrained.
Genuine interference: different task types competing for positions.

Teacher signs from the lambda-trained micro model.
EMA accelerated (α=0.05 vs 0.01) based on v1 findings.

License: MIT
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path
from dataclasses import dataclass

sys.stdout.reconfigure(line_buffering=True)

import numpy as np
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim

sys.path.insert(0, str(Path(__file__).parent))
from micro_model import MicroModel, MicroConfig
from train_etch import (
    EtchConfig, EtchState, measure_mspace,
    make_eval_batch, load_compile_examples, tokenize_examples,
)


# ══════════════════════════════════════════════════════════════════════
# Shard DataLoader
# ══════════════════════════════════════════════════════════════════════

class ShardDataLoader:
    """DataLoader from a pre-tokenized numpy shard (1D int32 array).

    Shuffles at epoch boundary by splitting into chunks and permuting.
    """

    def __init__(self, shard_path: str, batch_size: int, seq_len: int, seed: int = 42):
        self.data = np.load(shard_path).astype(np.int32)
        self.batch_size = batch_size
        self.seq_len = seq_len
        self.rng = np.random.RandomState(seed)
        self.position = 0
        print(f"  Shard: {len(self.data):,} tokens from {shard_path}")

    def next_batch(self):
        B, T = self.batch_size, self.seq_len
        needed = B * (T + 1)
        if self.position + needed > len(self.data):
            # Shuffle: cut into ~1000-token chunks, permute
            chunk_size = 1024
            n_chunks = len(self.data) // chunk_size
            chunks = self.data[:n_chunks * chunk_size].reshape(n_chunks, chunk_size)
            perm = self.rng.permutation(n_chunks)
            self.data[:n_chunks * chunk_size] = chunks[perm].reshape(-1)
            self.position = 0

        buf = self.data[self.position:self.position + needed]
        self.position += needed
        buf = buf.reshape(B, T + 1)
        return mx.array(buf[:, :T]), mx.array(buf[:, 1:T + 1])


# ══════════════════════════════════════════════════════════════════════
# Training with etch (adapted from train_etch.py)
# ══════════════════════════════════════════════════════════════════════

def train_with_etch(
    model, cfg, train_loader, eval_input, eval_target,
    etch_cfg: EtchConfig,
    total_steps: int = 5000,
    lr: float = 3e-4,
    warmup: int = 100,
    log_interval: int = 100,
    teacher_topology: dict | None = None,
):
    """Train with holographic etch mechanism on attention Q/K weights."""

    # ── Initialize etch state for Q/K projections ──
    etch_states = {}
    mx.eval(model.parameters())

    for li in range(cfg.n_layers):
        block = model.blocks[li]
        for pname in ["q_proj", "k_proj"]:
            proj = getattr(block.attn, pname)
            W = np.array(proj.weight)
            key = (li, pname)
            state = EtchState(W.shape, etch_cfg)

            if teacher_topology and key in teacher_topology:
                state.initialize_signs_from(teacher_topology[key]["signs"])
                print(f"    {key}: teacher signs")
            else:
                state.initialize_signs(W)

            etch_states[key] = state

    # Per-row gamma
    gammas = {}
    for li in range(cfg.n_layers):
        for pname in ["q_proj", "k_proj"]:
            key = (li, pname)
            if teacher_topology and key in teacher_topology:
                gamma = teacher_topology[key]["gamma"].copy()
            else:
                W = np.array(getattr(model.blocks[li].attn, pname).weight)
                gamma = np.abs(W).mean(axis=1, keepdims=True)
            gammas[key] = mx.array(gamma)

    # ── Optimizer ──
    lr_schedule = optim.cosine_decay(lr, total_steps, lr * 0.01)
    warmup_schedule = optim.linear_schedule(1e-7, lr, warmup)

    def lr_fn(step):
        if step < warmup:
            return warmup_schedule(step)
        return lr_schedule(step)

    optimizer = optim.AdamW(learning_rate=lr_fn, weight_decay=0.01)

    # ── Training functions ──
    def apply_etch_weights():
        for li in range(cfg.n_layers):
            block = model.blocks[li]
            for pname in ["q_proj", "k_proj"]:
                key = (li, pname)
                state = etch_states[key]
                gamma = np.array(gammas[key])
                W_effective = state.get_effective_weight(gamma)
                getattr(block.attn, pname).weight = mx.array(W_effective)

    def loss_fn(model, x, t):
        _, loss = model(x, t)
        return loss

    loss_and_grad = nn.value_and_grad(model, loss_fn)

    # ── Tracking ──
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

        # ── Extract Q/K gradients, then zero them ──
        qk_grads = {}
        for li in range(cfg.n_layers):
            for pname in ["q_proj", "k_proj"]:
                key = (li, pname)
                grad_w = grads["blocks"][li]["attn"][pname]["weight"]
                qk_grads[key] = np.array(grad_w)
                grads["blocks"][li]["attn"][pname]["weight"] = mx.zeros_like(grad_w)

        optimizer.update(model, grads)
        mx.eval(model.parameters(), optimizer.state, loss_val, gnorm)

        # ── Gamma update ──
        gamma_lr_val = lr_fn(step)
        gamma_lr = float(gamma_lr_val.item() if isinstance(gamma_lr_val, mx.array) else gamma_lr_val)
        for key, grad in qk_grads.items():
            state = etch_states[key]
            gamma_np = np.array(gammas[key])
            gamma_grad = (state.get_effective_weight(np.ones_like(gamma_np)) * grad).mean(axis=1, keepdims=True)
            gamma_np -= gamma_lr * gamma_grad
            gamma_np = np.maximum(gamma_np, 1e-6)
            gammas[key] = mx.array(gamma_np)

        # ── TD updates ──
        for key, grad in qk_grads.items():
            state = etch_states[key]
            state.update_td(grad, step)
            state.check_flips(step)
            state.update_opposition(grad)

            if step % 50 == 0:
                state.decay_flip_window(step)

        # ── Etch gate ──
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

        # ── Logging ──
        train_loss = float(loss_val.item())

        if step % log_interval == 0 or step == 1:
            _, eval_loss = model(eval_input, eval_target)
            mx.eval(eval_loss)
            eval_loss_val = float(eval_loss.item())
            elapsed = time.time() - t_start

            total_positions = 0
            total_etched = 0
            total_etched_zero = 0
            total_fluid = 0
            mean_coherence = 0.0
            n_coherence = 0
            total_flips = 0
            for key, state in etch_states.items():
                s = state.summary()
                total_positions += s["total"]
                total_etched += s["etched"]
                total_etched_zero += s["etched_zero"]
                total_fluid += s["fluid"]
                total_flips += int(state.flip_count.sum())
                if s["fluid"] > 0:
                    mean_coherence += s["mean_coherence_fluid"] * s["fluid"]
                    n_coherence += s["fluid"]

            etch_pct = total_etched / total_positions * 100
            zero_pct = total_etched_zero / total_positions * 100
            fluid_pct = total_fluid / total_positions * 100
            avg_coherence = mean_coherence / n_coherence if n_coherence > 0 else 0.0

            print(
                f"  step {step:>5}: train={train_loss:.4f} eval={eval_loss_val:.4f} "
                f"gnorm={float(gnorm.item()):.2f} | "
                f"etch={etch_pct:.1f}% zero={zero_pct:.1f}% fluid={fluid_pct:.1f}% "
                f"coh={avg_coherence:.3f} flips={total_flips} | "
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
                "etch_pct": etch_pct,
                "zero_pct": zero_pct,
                "fluid_pct": fluid_pct,
                "coherence": avg_coherence,
                "total_flips": total_flips,
            })

            etch_history.append({
                "step": step,
                "etch_pct": etch_pct,
                "zero_pct": zero_pct,
                "fluid_pct": fluid_pct,
            })

        # ── M-space check ──
        if step % etch_cfg.mspace_interval == 0:
            ms = measure_mspace(model, cfg)
            print(f"         M-space:", end="", flush=True)
            for li in range(cfg.n_layers):
                m = ms[li]
                print(f" L{li}:r90={m['rank90']},t1={m['top1_pct']:.1f}%", end="")
            print(flush=True)

    # ── Per-layer final summary ──
    print("\n  Per-layer etch summary:")
    for li in range(cfg.n_layers):
        for pname in ["q_proj", "k_proj"]:
            key = (li, pname)
            s = etch_states[key].summary()
            print(
                f"    L{li}.{pname}: etched={s['etched_pct']:.1f}% "
                f"(±1={s['etched_nonzero']}, 0={s['etched_zero']}) "
                f"fluid={s['fluid_pct']:.1f}% "
                f"coh={s['mean_coherence_fluid']:.3f}"
            )

    return curve, etch_history


# ══════════════════════════════════════════════════════════════════════
# Float32 baseline
# ══════════════════════════════════════════════════════════════════════

def train_float32(
    model, cfg, train_loader, eval_input, eval_target,
    total_steps=5000, lr=3e-4, warmup=100, log_interval=100,
):
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
    print("HOLOGRAPHIC ETCH v2 — DIVERSE DATA (structured shard)")
    print("=" * 70)
    print()

    cfg = MicroConfig()
    TOTAL_STEPS = 5000
    SHARD_PATH = "data/structured_shard_v2.npy"

    # ── Eval data (lambda compile — measures compile ability specifically) ──
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    eval_examples = load_compile_examples(cfg.eval_file)
    eval_seqs = tokenize_examples(eval_examples, tokenizer, cfg.max_seq_len, cfg.eod_id)
    eval_input, eval_target = make_eval_batch(eval_seqs, cfg.max_seq_len)
    print(f"Eval: {len(eval_examples)} compile examples")

    # ── Teacher ──
    ckpt_path = Path("checkpoints/micro/final/model.npz")
    teacher = MicroModel(cfg)
    teacher_weights = mx.load(str(ckpt_path))
    teacher.load_weights(list(teacher_weights.items()))
    mx.eval(teacher.parameters())
    print(f"Teacher: {ckpt_path}")

    teacher_topology = {}
    for li in range(cfg.n_layers):
        block = teacher.blocks[li]
        for pname in ["q_proj", "k_proj"]:
            W = np.array(getattr(block.attn, pname).weight)
            signs = np.sign(W).astype(np.float32)
            signs[signs == 0] = 1.0
            gamma = np.abs(W).mean(axis=1, keepdims=True)
            teacher_topology[(li, pname)] = {"signs": signs, "gamma": gamma}

    ms_teacher = measure_mspace(teacher, cfg)
    print("Teacher M-space:")
    for li in range(cfg.n_layers):
        m = ms_teacher[li]
        print(f"  L{li}: rank90={m['rank90']}, top1={m['top1_pct']:.1f}%")
    del teacher
    print()

    # ── Etch config (accelerated from v1 findings) ──
    etch_cfg = EtchConfig(
        ema_alpha=0.05,            # 5× faster than v1 (was 0.01)
        tau_coherent=0.4,          # lower bar for ±1 etch (was 0.7)
        tau_zero=0.15,             # lower bar for zero detection (was 0.2)
        tau_cold=0.1,              # relaxed cold threshold (was 0.05)
        tau_hot=0.15,              # relaxed hot threshold (was 0.3)
        flip_threshold=0.25,       # lower bar for flips (was 0.5)
        mag_threshold=0.001,       # lower magnitude bar (was 0.01)
        etch_interval=100,
        etch_warmup=300,           # shorter warmup (was 500)
        flip_window=200,
        mspace_interval=500,
        tau_unetch=0.8,
        opposition_alpha=0.01,
    )
    print(f"Etch config: α={etch_cfg.ema_alpha} τ_c={etch_cfg.tau_coherent} "
          f"τ_z={etch_cfg.tau_zero} τ_cold={etch_cfg.tau_cold} τ_hot={etch_cfg.tau_hot} "
          f"τ_flip={etch_cfg.flip_threshold}")
    print()

    all_results = {"total_steps": TOTAL_STEPS, "shard": SHARD_PATH, "variants": []}

    # ═══════════════════════════════════════════════════════════════
    # Variant A: Float32 baseline on diverse data
    # ═══════════════════════════════════════════════════════════════
    print("═" * 70)
    print("  A. Float32 baseline (diverse data)")
    print("═" * 70)

    model_a = MicroModel(cfg)
    mx.eval(model_a.parameters())
    loader_a = ShardDataLoader(SHARD_PATH, cfg.batch_size, cfg.max_seq_len, seed=42)
    curve_a = train_float32(model_a, cfg, loader_a, eval_input, eval_target,
                            total_steps=TOTAL_STEPS, log_interval=500)
    ms_a = measure_mspace(model_a, cfg)
    _, final_a = model_a(eval_input, eval_target)
    mx.eval(final_a)
    print(f"\n  Final eval loss: {float(final_a.item()):.4f}")
    for li in [0, 2]:
        m = ms_a[li]
        print(f"  L{li}: rank90={m['rank90']}, top1={m['top1_pct']:.1f}%")
    print()

    all_results["variants"].append({
        "name": "A. Float32 (diverse data)",
        "final_loss": float(final_a.item()),
        "mspace": {str(k): v for k, v in ms_a.items()},
        "curve": curve_a,
    })

    # ═══════════════════════════════════════════════════════════════
    # Variant B: Holographic Etch on diverse data
    # ═══════════════════════════════════════════════════════════════
    print("═" * 70)
    print("  B. Holographic Etch (teacher signs + diverse data)")
    print("═" * 70)

    model_b = MicroModel(cfg)
    mx.eval(model_b.parameters())
    loader_b = ShardDataLoader(SHARD_PATH, cfg.batch_size, cfg.max_seq_len, seed=42)
    curve_b, etch_history = train_with_etch(
        model_b, cfg, loader_b, eval_input, eval_target,
        etch_cfg=etch_cfg, total_steps=TOTAL_STEPS, log_interval=500,
        teacher_topology=teacher_topology,
    )
    ms_b = measure_mspace(model_b, cfg)
    _, final_b = model_b(eval_input, eval_target)
    mx.eval(final_b)
    print(f"\n  Final eval loss: {float(final_b.item()):.4f}")
    for li in [0, 2]:
        m = ms_b[li]
        print(f"  L{li}: rank90={m['rank90']}, top1={m['top1_pct']:.1f}%")
    print()

    all_results["variants"].append({
        "name": "B. Holographic Etch (teacher signs + diverse data)",
        "final_loss": float(final_b.item()),
        "mspace": {str(k): v for k, v in ms_b.items()},
        "curve": curve_b,
        "etch_history": etch_history,
    })

    # ═══════════════════════════════════════════════════════════════
    # Summary
    # ═══════════════════════════════════════════════════════════════
    elapsed = time.time() - t0
    print("=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print()
    for r in all_results["variants"]:
        name = r["name"]
        fl = r["final_loss"]
        ms = r.get("mspace", {})
        r90 = ms.get("2", {}).get("rank90", "?")
        t1 = ms.get("2", {}).get("top1_pct", 0)
        print(f"  {name:<50} loss={fl:.4f}  L2:rank90={r90},top1={t1:.1f}%")

    print(f"\n  Teacher: L2:rank90={ms_teacher[2]['rank90']},top1={ms_teacher[2]['top1_pct']:.1f}%")

    if etch_history:
        last = etch_history[-1]
        print(f"  Etch final (B): etch={last['etch_pct']:.1f}% zero={last['zero_pct']:.1f}% fluid={last['fluid_pct']:.1f}%")

    print(f"\n  Total elapsed: {elapsed:.0f}s ({elapsed/60:.1f}m)")

    out_dir = Path("results/holographic-etch-micro")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "summary_v2.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"  Saved to {out_dir}/summary_v2.json")


if __name__ == "__main__":
    main()
