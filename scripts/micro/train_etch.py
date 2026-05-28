#!/usr/bin/env python3
"""
train_etch.py — Holographic Etch on Micro Model.

Trains the micro model with interference-driven topology crystallization:
  - Three-state TD: etch ±1, etch 0, or stay fluid
  - Etch gate: direction EMA coherence + FlipMap temperature → convergence
  - Opposition monitor: gradient opposition at etched positions → un-etch
  - M-space SNR: periodic geometric confirmation (attention only)

The topology develops through interference. Positions reach normal form
and are etched permanently. Oscillation IS the signal for zero.

Variants:
  A. Float32 baseline (no etch, full GD) — control
  B. Etch mechanism (attention Q/K only, rest GD) — the experiment
  C. Pre-cut topology from session 166 (30% M-zeros) — comparison

License: MIT
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path
from dataclasses import dataclass, field

sys.stdout.reconfigure(line_buffering=True)

import numpy as np
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim

sys.path.insert(0, str(Path(__file__).parent))
from micro_model import MicroModel, MicroConfig


# ══════════════════════════════════════════════════════════════════════
# Etch State
# ══════════════════════════════════════════════════════════════════════

@dataclass
class EtchConfig:
    """Thresholds for the etch mechanism."""
    # Direction EMA
    ema_alpha: float = 0.01          # EMA decay for direction/magnitude

    # Etch gate thresholds
    tau_coherent: float = 0.7        # |direction_ema| > this → candidate for ±1 etch
    tau_zero: float = 0.2            # |direction_ema| < this → candidate for 0 etch
    tau_cold: float = 0.05           # flip_rate < this → cold (hasn't flipped recently)
    tau_hot: float = 0.3             # flip_rate > this → hot (oscillating)

    # Opposition (un-etch)
    tau_unetch: float = 0.8          # opposition_ema > this → un-etch
    opposition_alpha: float = 0.01   # EMA decay for opposition tracking

    # TD flip
    flip_threshold: float = 0.5      # |direction_ema| > this AND magnitude > mag_threshold → flip
    mag_threshold: float = 0.01      # minimum gradient magnitude to consider flip

    # Scheduling
    etch_interval: int = 100         # run etch gate every N steps
    etch_warmup: int = 500           # don't etch before this step (let interference develop)
    flip_window: int = 200           # window for measuring flip rate

    # M-space (periodic)
    mspace_interval: int = 500       # SVD check frequency


class EtchState:
    """Per-parameter etch tracking state.

    Tracks for each position:
      - etch_mask: True = etched (frozen), False = fluid
      - etch_value: the etched ternary value (+1, -1, or 0)
      - direction_ema: running average of gradient sign
      - magnitude_ema: running average of gradient magnitude
      - flip_history: ring buffer of step numbers when flips occurred
      - opposition_ema: for etched positions, tracks gradient opposition
    """

    def __init__(self, shape: tuple, cfg: EtchConfig):
        self.cfg = cfg
        self.shape = shape
        n = int(np.prod(shape))

        # Core state
        self.etch_mask = np.zeros(shape, dtype=bool)        # False = fluid
        self.etch_value = np.zeros(shape, dtype=np.float32)  # etched ternary value
        self.etch_step = np.zeros(shape, dtype=np.int32)     # when etched

        # TD tracking (for fluid positions)
        self.direction_ema = np.zeros(shape, dtype=np.float32)
        self.magnitude_ema = np.zeros(shape, dtype=np.float32)
        self.current_sign = np.ones(shape, dtype=np.float32)  # current ternary sign

        # Flip tracking
        self.flip_count = np.zeros(shape, dtype=np.int32)    # flips in current window
        self.last_flip_step = np.zeros(shape, dtype=np.int32)

        # Opposition tracking (for etched positions)
        self.opposition_ema = np.zeros(shape, dtype=np.float32)

    def initialize_signs(self, W_float: np.ndarray):
        """Initialize current signs from a float weight matrix."""
        self.current_sign = np.sign(W_float).astype(np.float32)
        self.current_sign[self.current_sign == 0] = 1.0

    def initialize_signs_from(self, signs: np.ndarray):
        """Initialize current signs from a pre-computed sign array."""
        self.current_sign = signs.copy().astype(np.float32)

    def update_td(self, gradient: np.ndarray, step: int):
        """Update direction/magnitude EMA for fluid positions."""
        alpha = self.cfg.ema_alpha
        fluid = ~self.etch_mask

        # Gradient sign and magnitude
        grad_sign = np.sign(gradient)
        grad_mag = np.abs(gradient)

        # Update EMA only for fluid positions
        self.direction_ema[fluid] = (
            (1 - alpha) * self.direction_ema[fluid] +
            alpha * grad_sign[fluid]
        )
        self.magnitude_ema[fluid] = (
            (1 - alpha) * self.magnitude_ema[fluid] +
            alpha * grad_mag[fluid]
        )

    def check_flips(self, step: int) -> np.ndarray:
        """Check which fluid positions should flip. Returns flip mask."""
        fluid = ~self.etch_mask
        coherence = np.abs(self.direction_ema)
        mag = self.magnitude_ema

        # Flip if: fluid AND direction EMA disagrees with current sign
        # AND coherence is above threshold AND magnitude is significant
        ema_sign = np.sign(self.direction_ema)
        should_flip = (
            fluid &
            (ema_sign != 0) &
            (ema_sign != self.current_sign) &
            (coherence > self.cfg.flip_threshold) &
            (mag > self.cfg.mag_threshold)
        )

        # Apply flips
        if should_flip.any():
            self.current_sign[should_flip] = ema_sign[should_flip]
            self.flip_count[should_flip] += 1
            self.last_flip_step[should_flip] = step

        return should_flip

    def decay_flip_window(self, step: int):
        """Reset flip counts for positions whose window has expired."""
        expired = (step - self.last_flip_step) > self.cfg.flip_window
        # Don't fully reset — halve the count for gradual decay
        self.flip_count[expired & (self.flip_count > 0)] //= 2

    def update_opposition(self, gradient: np.ndarray):
        """Update opposition EMA for etched ±1 positions."""
        alpha = self.cfg.opposition_alpha
        etched_nonzero = self.etch_mask & (self.etch_value != 0)

        if not etched_nonzero.any():
            return

        grad_sign = np.sign(gradient)
        opposes = (grad_sign != self.etch_value) & (grad_sign != 0)

        self.opposition_ema[etched_nonzero] = (
            (1 - alpha) * self.opposition_ema[etched_nonzero] +
            alpha * opposes[etched_nonzero].astype(np.float32)
        )

    def run_etch_gate(self, step: int) -> dict:
        """Run the etch gate. Returns stats about what was etched/un-etched."""
        cfg = self.cfg
        stats = {"etched_plus": 0, "etched_minus": 0, "etched_zero": 0, "unetched": 0}

        if step < cfg.etch_warmup:
            return stats

        fluid = ~self.etch_mask
        coherence = np.abs(self.direction_ema)

        # Flip rate: flips per window
        flip_rate = self.flip_count.astype(np.float32) / max(cfg.flip_window, 1)

        # ── Etch ±1: high coherence + cold ──
        etch_nonzero = (
            fluid &
            (coherence > cfg.tau_coherent) &
            (flip_rate < cfg.tau_cold)
        )
        if etch_nonzero.any():
            signs = self.current_sign[etch_nonzero]
            self.etch_mask[etch_nonzero] = True
            self.etch_value[etch_nonzero] = signs
            self.etch_step[etch_nonzero] = step
            stats["etched_plus"] = int((signs > 0).sum())
            stats["etched_minus"] = int((signs < 0).sum())

        # ── Etch 0: low coherence + hot (oscillating) ──
        etch_zero = (
            fluid &
            (coherence < cfg.tau_zero) &
            (flip_rate > cfg.tau_hot)
        )
        if etch_zero.any():
            self.etch_mask[etch_zero] = True
            self.etch_value[etch_zero] = 0.0
            self.etch_step[etch_zero] = step
            stats["etched_zero"] = int(etch_zero.sum())

        # ── Un-etch: opposition too high ──
        etched_nonzero = self.etch_mask & (self.etch_value != 0)
        unetch = etched_nonzero & (self.opposition_ema > cfg.tau_unetch)
        if unetch.any():
            self.etch_mask[unetch] = False
            # Restore current_sign from etch_value for TD to work with
            self.current_sign[unetch] = self.etch_value[unetch]
            self.etch_value[unetch] = 0.0
            self.etch_step[unetch] = 0
            self.opposition_ema[unetch] = 0.0
            self.flip_count[unetch] = 0
            self.direction_ema[unetch] = 0.0
            self.magnitude_ema[unetch] = 0.0
            stats["unetched"] = int(unetch.sum())

        return stats

    def get_effective_weight(self, gamma: np.ndarray) -> np.ndarray:
        """Compute effective ternary weight: etched values + fluid signs, scaled by gamma."""
        # Etched positions use etch_value, fluid use current_sign
        effective_sign = np.where(self.etch_mask, self.etch_value, self.current_sign)
        return effective_sign * gamma

    def summary(self) -> dict:
        """Summary statistics."""
        total = int(np.prod(self.shape))
        n_etched = int(self.etch_mask.sum())
        n_etched_zero = int((self.etch_mask & (self.etch_value == 0)).sum())
        n_etched_nonzero = n_etched - n_etched_zero
        n_fluid = total - n_etched
        return {
            "total": total,
            "etched": n_etched,
            "etched_pct": n_etched / total * 100,
            "etched_nonzero": n_etched_nonzero,
            "etched_zero": n_etched_zero,
            "zero_pct": n_etched_zero / total * 100,
            "fluid": n_fluid,
            "fluid_pct": n_fluid / total * 100,
            "mean_coherence_fluid": float(np.abs(self.direction_ema[~self.etch_mask]).mean())
                if n_fluid > 0 else 0.0,
            "mean_opposition_etched": float(self.opposition_ema[self.etch_mask & (self.etch_value != 0)].mean())
                if n_etched_nonzero > 0 else 0.0,
        }


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
    mx.eval(model.parameters())
    results = {}
    for li in range(cfg.n_layers):
        W_q = np.array(model.blocks[li].attn.q_proj.weight)
        W_k = np.array(model.blocks[li].attn.k_proj.weight)
        M = W_q.T @ W_k
        U, s, Vt = np.linalg.svd(M, full_matrices=False)
        total = (s ** 2).sum()
        if total < 1e-12:
            results[li] = {"rank90": len(s), "top1_pct": 0.0, "sigma_ratio": 1.0}
            continue
        cum = np.cumsum(s ** 2) / total
        rank90 = int(np.searchsorted(cum, 0.90) + 1)
        top1 = float(cum[0] * 100)
        ratio = float(s[0] / s[1]) if len(s) > 1 and s[1] > 0 else float('inf')
        results[li] = {"rank90": rank90, "top1_pct": top1, "sigma_ratio": ratio}
    return results


# ══════════════════════════════════════════════════════════════════════
# Etch Training Loop
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
    """Train with holographic etch mechanism on attention Q/K weights.

    If teacher_topology is provided, Q/K signs and gammas are initialized
    from the teacher (the universal lattice). Otherwise, from the model's
    own random initialization (not recommended).
    """

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
                # Initialize from teacher's sign topology
                state.initialize_signs_from(teacher_topology[key]["signs"])
                print(f"  {key}: initialized from teacher signs")
            else:
                state.initialize_signs(W)

            etch_states[key] = state

    # Per-row gamma (learned magnitude scale)
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

    # ── Optimizer (for all parameters — we zero Q/K grads manually) ──
    lr_schedule = optim.cosine_decay(lr, total_steps, lr * 0.01)
    warmup_schedule = optim.linear_schedule(1e-7, lr, warmup)

    def lr_fn(step):
        if step < warmup:
            return warmup_schedule(step)
        return lr_schedule(step)

    optimizer = optim.AdamW(learning_rate=lr_fn, weight_decay=0.01)

    # NOTE: we do NOT freeze Q/K — we need their gradients for TD.
    # Instead, we zero their grads before optimizer.update() so the
    # optimizer doesn't change them, then apply_etch_weights() sets
    # them from etch state each step.

    # ── Training functions ──
    def apply_etch_weights():
        """Set Q/K weights from etch state + gamma."""
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

    # Apply initial weights
    apply_etch_weights()
    mx.eval(model.parameters())

    for step in range(1, total_steps + 1):
        model._training_step = step
        inp, tgt = train_loader.next_batch()

        # Forward + backward
        loss_val, grads = loss_and_grad(model, inp, tgt)
        grads, gnorm = optim.clip_grad_norm(grads, 1.0)

        # ── Extract Q/K gradients, then zero them so optimizer ignores Q/K ──
        qk_grads = {}
        for li in range(cfg.n_layers):
            for pname in ["q_proj", "k_proj"]:
                key = (li, pname)
                grad_w = grads["blocks"][li]["attn"][pname]["weight"]
                qk_grads[key] = np.array(grad_w)
                # Zero the gradient so optimizer.update() won't change Q/K
                grads["blocks"][li]["attn"][pname]["weight"] = mx.zeros_like(grad_w)

        # ── Update non-Q/K parameters with optimizer (Q/K grads are zeroed) ──
        optimizer.update(model, grads)
        mx.eval(model.parameters(), optimizer.state, loss_val, gnorm)

        # ── Update gamma via gradient (manual SGD with momentum-like EMA) ──
        gamma_lr = float(lr_fn(step).item() if isinstance(lr_fn(step), mx.array) else lr_fn(step))
        for key, grad in qk_grads.items():
            li, pname = key
            state = etch_states[key]
            gamma_np = np.array(gammas[key])

            # Gamma gradient: d_loss/d_gamma ≈ sign * d_loss/d_W averaged per row
            gamma_grad = (state.get_effective_weight(np.ones_like(gamma_np)) * grad).mean(axis=1, keepdims=True)
            gamma_np -= gamma_lr * gamma_grad
            gamma_np = np.maximum(gamma_np, 1e-6)  # keep positive
            gammas[key] = mx.array(gamma_np)

        # ── TD updates for fluid positions ──
        for key, grad in qk_grads.items():
            state = etch_states[key]
            state.update_td(grad, step)
            state.check_flips(step)
            state.update_opposition(grad)

            # Decay flip window periodically
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

        # ── Apply updated etch weights to model ──
        apply_etch_weights()
        mx.eval(model.parameters())

        # ── Logging ──
        train_loss = float(loss_val.item())

        if step % log_interval == 0 or step == 1:
            _, eval_loss = model(eval_input, eval_target)
            mx.eval(eval_loss)
            eval_loss_val = float(eval_loss.item())
            elapsed = time.time() - t_start

            # Aggregate etch stats
            total_positions = 0
            total_etched = 0
            total_etched_zero = 0
            total_fluid = 0
            mean_coherence = 0.0
            n_coherence = 0
            for key, state in etch_states.items():
                s = state.summary()
                total_positions += s["total"]
                total_etched += s["etched"]
                total_etched_zero += s["etched_zero"]
                total_fluid += s["fluid"]
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
                f"coh={avg_coherence:.3f} | "
                f"{elapsed:.0f}s",
                flush=True,
            )

            if etch_stats_this_step:
                es = etch_stats_this_step
                print(
                    f"         etch gate: +1={es['etched_plus']} -1={es['etched_minus']} "
                    f"0={es['etched_zero']} un-etch={es['unetched']}",
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
            })

            # Etch history snapshot
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
                f"fluid={s['fluid_pct']:.1f}%"
            )

    return curve, etch_history


# ══════════════════════════════════════════════════════════════════════
# Float32 baseline (for comparison)
# ══════════════════════════════════════════════════════════════════════

def train_float32(
    model, cfg, train_loader, eval_input, eval_target,
    total_steps=5000, lr=3e-4, warmup=100, log_interval=100,
):
    """Standard float32 training — no etch, full GD."""
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
    print("HOLOGRAPHIC ETCH — MICRO MODEL")
    print("=" * 70)
    print()

    cfg = MicroConfig()
    TOTAL_STEPS = 5000

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

    all_results = {"total_steps": TOTAL_STEPS, "variants": []}

    # ── Load trained model as teacher (for sign topology) ──
    ckpt_path = Path("checkpoints/micro/final/model.npz")
    if not ckpt_path.exists():
        ckpt_path = Path("checkpoints/micro/step_005000/model.npz")
    teacher = MicroModel(cfg)
    teacher_weights = mx.load(str(ckpt_path))
    teacher.load_weights(list(teacher_weights.items()))
    mx.eval(teacher.parameters())
    print(f"Teacher loaded from {ckpt_path}")

    # Extract teacher topology (signs + gamma for Q/K)
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
    print()
    del teacher  # free memory

    # ═══════════════════════════════════════════════════════════════
    # Variant A: Float32 baseline (train from scratch)
    # ═══════════════════════════════════════════════════════════════
    print("═" * 70)
    print("  A. Float32 baseline (full GD)")
    print("═" * 70)

    model_a = MicroModel(cfg)
    mx.eval(model_a.parameters())
    train_loader = DataLoader(train_seqs, cfg.batch_size, cfg.max_seq_len, cfg.eod_id, seed=42)
    curve_a = train_float32(model_a, cfg, train_loader, eval_input, eval_target,
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
        "name": "A. Float32 (full GD)",
        "final_loss": float(final_a.item()),
        "mspace": {str(k): v for k, v in ms_a.items()},
        "curve": curve_a,
    })

    # ═══════════════════════════════════════════════════════════════
    # Variant B: Holographic Etch (teacher topology → etch discovers zeros)
    # ═══════════════════════════════════════════════════════════════
    print("═" * 70)
    print("  B. Holographic Etch (teacher signs → etch finds zeros)")
    print("═" * 70)

    etch_cfg = EtchConfig()
    model_b = MicroModel(cfg)
    mx.eval(model_b.parameters())
    train_loader = DataLoader(train_seqs, cfg.batch_size, cfg.max_seq_len, cfg.eod_id, seed=42)
    curve_b, etch_history = train_with_etch(
        model_b, cfg, train_loader, eval_input, eval_target,
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
        "name": "B. Holographic Etch (teacher signs → etch)",
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
        print(f"  {name:<45} loss={fl:.4f}  L2:rank90={r90},top1={t1:.1f}%")

    # Teacher reference
    print(f"\n  Teacher reference:")
    for li in [0, 2]:
        m = ms_teacher[li]
        print(f"    L{li}: rank90={m['rank90']}, top1={m['top1_pct']:.1f}%")

    if etch_history:
        last = etch_history[-1]
        print(f"\n  Etch progression (B): etch={last['etch_pct']:.1f}% zero={last['zero_pct']:.1f}% fluid={last['fluid_pct']:.1f}%")

    print(f"\n  Total elapsed: {elapsed:.0f}s ({elapsed/60:.1f}m)")

    # Save
    out_dir = Path("results/holographic-etch-micro")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "summary.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"  Saved to {out_dir}/summary.json")


if __name__ == "__main__":
    main()
