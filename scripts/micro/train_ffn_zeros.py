#!/usr/bin/env python3
"""FFN Zero-Placement Comparison — Does gradient oscillation beat magnitude?

Tests three zero-placement strategies for FFN weights:
  A. Float32 baseline (no frozen topology — full GD)
  B. FFN magnitude zeros: bottom 30% by |w| → zero, rest → sign(w) × gamma
  C. FFN oscillation zeros: bottom 30% by sign_consistency → zero
  D. FFN combined zeros: bottom 30% by |w| × sign_consistency → zero
  E. FFN both-agree zeros: positions where B AND C agree → zero (~9%)

For B-E: FFN gate/key/value weights are frozen ternary topology × learned gamma.
Attention and everything else trains normally.
Gamma is per-row, initialized from teacher |W|.mean(axis=1).

The gradient oscillation stats are computed on the trained teacher model
using diverse data (same approach as gradient_zero_map.py but on micro model).

License: MIT
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
from micro_model import MicroModel, MicroConfig


# ══════════════════════════════════════════════════════════════════════
# Data
# ══════════════════════════════════════════════════════════════════════

def load_ex(p):
    return [json.loads(l) for l in open(p) if l.strip()]

def tok(exs, tokenizer, cfg):
    seqs = []
    for ex in exs:
        ids = tokenizer.encode(f"{ex['input']}\n{ex['output']}", add_special_tokens=False)
        ids.append(cfg.eod_id)
        seqs.append(np.array(ids[:cfg.max_seq_len], dtype=np.int32))
    return seqs

class DataLoader:
    def __init__(self, seqs, bs, sl, seed=42):
        self.seqs, self.bs, self.sl = seqs, bs, sl
        self.rng = np.random.RandomState(seed)
        self._build()
    def _build(self):
        idx = self.rng.permutation(len(self.seqs))
        self.stream = np.concatenate([self.seqs[i] for i in idx])
        self.pos = 0
    def next_batch(self):
        n = self.bs * (self.sl + 1)
        if self.pos + n > len(self.stream): self._build()
        buf = self.stream[self.pos:self.pos+n].reshape(self.bs, self.sl+1)
        self.pos += n
        return mx.array(buf[:,:self.sl]), mx.array(buf[:,1:self.sl+1])


# ══════════════════════════════════════════════════════════════════════
# Gradient oscillation measurement (MLX-based, on the micro teacher)
# ══════════════════════════════════════════════════════════════════════

def compute_gradient_oscillation(model, cfg, train_seqs, n_batches=50):
    """Compute per-element gradient sign consistency for FFN weights.

    Runs n_batches forward+backward passes, accumulates sign(grad) per element.
    Returns dict mapping (layer, proj_name) → sign_consistency array.
    """
    print(f"  Computing gradient oscillation ({n_batches} batches)...", flush=True)

    loader = DataLoader(train_seqs, cfg.batch_size, cfg.max_seq_len, seed=123)

    # Identify FFN parameters
    ffn_params = {}
    for li in range(cfg.n_layers):
        for pname in ["gate_proj", "key_proj", "value_proj"]:
            key = f"blocks.{li}.ffn.{pname}.weight"
            ffn_params[(li, pname)] = key

    # Accumulators
    sign_sums = {}
    for (li, pname), key in ffn_params.items():
        w = model.blocks[li].ffn
        param = getattr(w, pname).weight
        sign_sums[(li, pname)] = np.zeros(param.shape, dtype=np.float32)

    def loss_fn(model, inp, tgt):
        _, loss = model(inp, tgt)
        return loss

    loss_and_grad = nn.value_and_grad(model, loss_fn)

    for b in range(n_batches):
        inp, tgt = loader.next_batch()
        lv, grads = loss_and_grad(model, inp, tgt)
        mx.eval(lv, grads)

        # Extract FFN gradients
        for (li, pname) in ffn_params:
            g = grads["blocks"][li]["ffn"][pname]["weight"]
            sign_sums[(li, pname)] += np.sign(np.array(g))

    # Compute sign consistency = |mean(sign)| = |sign_sum / n|
    result = {}
    noise_floor = np.sqrt(2 / (np.pi * n_batches))
    print(f"  Sign consistency noise floor (n={n_batches}): {noise_floor:.4f}", flush=True)

    for (li, pname), ss in sign_sums.items():
        sc = np.abs(ss / n_batches)
        result[(li, pname)] = sc
        osc_frac = (sc <= 2 * noise_floor).mean()
        print(f"    L{li} {pname:>10}: mean_sc={sc.mean():.4f}, "
              f"osc%={osc_frac*100:.1f}%", flush=True)

    return result, noise_floor


# ══════════════════════════════════════════════════════════════════════
# Zero mask computation
# ══════════════════════════════════════════════════════════════════════

def compute_zero_masks(model, cfg, sign_cons, zero_frac=0.30):
    """Compute three zero mask strategies for FFN weights.

    Returns dict of strategy_name → {(layer, proj_name) → mask_array}.
    mask = 1.0 where weight is kept, 0.0 where zeroed.
    """
    masks = {}

    for strategy in ["magnitude", "oscillation", "combined", "both_agree"]:
        masks[strategy] = {}

    for li in range(cfg.n_layers):
        for pname in ["gate_proj", "key_proj", "value_proj"]:
            W = np.array(getattr(model.blocks[li].ffn, pname).weight)
            sc = sign_cons[(li, pname)]
            w_mag = np.abs(W)

            n_total = W.size
            n_zero = int(zero_frac * n_total)

            # Strategy A: magnitude bottom-30%
            mag_flat = w_mag.ravel()
            mag_thresh = np.partition(mag_flat, n_zero)[n_zero]
            mag_mask = (w_mag > mag_thresh).astype(np.float32)

            # Strategy B: oscillation bottom-30% (lowest sign consistency)
            sc_flat = sc.ravel()
            sc_thresh = np.partition(sc_flat, n_zero)[n_zero]
            osc_mask = (sc > sc_thresh).astype(np.float32)

            # Strategy C: combined score |w| × (sign_cons + ε)
            combined = w_mag * (sc + 0.01)
            comb_flat = combined.ravel()
            comb_thresh = np.partition(comb_flat, n_zero)[n_zero]
            comb_mask = (combined > comb_thresh).astype(np.float32)

            # Strategy D: both agree (intersection of mag and osc zeros)
            # Only zero where BOTH methods say zero — conservative
            both_zero = (w_mag <= mag_thresh) & (sc <= sc_thresh)
            both_mask = (~both_zero).astype(np.float32)

            masks["magnitude"][(li, pname)] = mag_mask
            masks["oscillation"][(li, pname)] = osc_mask
            masks["combined"][(li, pname)] = comb_mask
            masks["both_agree"][(li, pname)] = both_mask

            actual_zeros = {
                "magnitude": (1 - mag_mask).sum(),
                "oscillation": (1 - osc_mask).sum(),
                "combined": (1 - comb_mask).sum(),
                "both_agree": (1 - both_mask).sum(),
            }
            print(f"  L{li} {pname:>10}: mag={int(actual_zeros['magnitude'])}, "
                  f"osc={int(actual_zeros['oscillation'])}, "
                  f"comb={int(actual_zeros['combined'])}, "
                  f"both={int(actual_zeros['both_agree'])} zeros "
                  f"(of {n_total})", flush=True)

    return masks


# ══════════════════════════════════════════════════════════════════════
# Apply FFN topology
# ══════════════════════════════════════════════════════════════════════

def apply_ffn_topology(model, teacher, cfg, mask_dict):
    """Apply frozen ternary topology to FFN weights.

    weight = sign(teacher_W) × mask × gamma
    gamma = per-row mean(|teacher_W|) where mask=1
    """
    for li in range(cfg.n_layers):
        for pname in ["gate_proj", "key_proj", "value_proj"]:
            W_teacher = np.array(getattr(teacher.blocks[li].ffn, pname).weight)
            mask = mask_dict[(li, pname)]
            signs = np.sign(W_teacher).astype(np.float32)
            signs[signs == 0] = 1.0

            # Per-row gamma: mean |W| over non-zeroed positions
            masked_abs = np.abs(W_teacher) * mask
            row_nnz = mask.sum(axis=1, keepdims=True).clip(min=1)
            gamma = masked_abs.sum(axis=1, keepdims=True) / row_nnz

            # Apply: sign × mask × gamma
            frozen_w = signs * mask * gamma

            proj = getattr(model.blocks[li].ffn, pname)
            proj.weight = mx.array(frozen_w)
            proj.freeze(keys=["weight"])

    mx.eval(model.parameters())


# ══════════════════════════════════════════════════════════════════════
# Training loop
# ══════════════════════════════════════════════════════════════════════

def train(model, cfg, train_seqs, ev_in, ev_tgt, steps=5000, label=""):
    lr_sched = optim.cosine_decay(3e-4, steps, 3e-6)
    warmup = optim.linear_schedule(1e-7, 3e-4, 100)
    def lr_fn(s): return warmup(s) if s < 100 else lr_sched(s)
    opt = optim.AdamW(learning_rate=lr_fn, weight_decay=0.01)

    def lfn(m, x, t):
        _, l = m(x, t)
        return l
    lag = nn.value_and_grad(model, lfn)
    loader = DataLoader(train_seqs, cfg.batch_size, cfg.max_seq_len, seed=42)

    t0 = time.time()
    for step in range(1, steps + 1):
        model._training_step = step
        inp, tgt = loader.next_batch()
        lv, g = lag(model, inp, tgt)
        g, gn = optim.clip_grad_norm(g, 1.0)
        opt.update(model, g)
        mx.eval(model.parameters(), opt.state, lv, gn)
        if step % 1000 == 0 or step == 1:
            _, el = model(ev_in, ev_tgt)
            mx.eval(el)
            print(f"    [{label}] step {step:>5}: train={float(lv.item()):.4f}, "
                  f"eval={float(el.item()):.4f}, {time.time()-t0:.0f}s", flush=True)

    _, fl = model(ev_in, ev_tgt)
    mx.eval(fl)
    return float(fl.item())


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    t0 = time.time()
    print("=" * 70, flush=True)
    print("FFN ZERO-PLACEMENT COMPARISON", flush=True)
    print("  Does gradient oscillation beat magnitude for zero placement?", flush=True)
    print("=" * 70, flush=True)

    cfg = MicroConfig()

    # Load trained teacher
    print("\nLoading teacher model...", flush=True)
    teacher = MicroModel(cfg)
    w = mx.load("checkpoints/micro/final/model.npz")
    teacher.load_weights(list(w.items()))
    mx.eval(teacher.parameters())

    # Tokenize data
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    train_seqs = tok(load_ex(cfg.train_file), tokenizer, cfg)
    eval_seqs = tok(load_ex(cfg.eval_file), tokenizer, cfg)
    stream = np.concatenate(eval_seqs)
    T = min(cfg.max_seq_len, len(stream) - 1)
    ev_in = mx.array(stream[:T].reshape(1, T))
    ev_tgt = mx.array(stream[1:T+1].reshape(1, T))

    # Compute gradient oscillation on teacher
    print("\n" + "─" * 70, flush=True)
    print("PHASE 1: Compute gradient sign consistency on teacher FFN", flush=True)
    print("─" * 70, flush=True)
    sign_cons, noise_floor = compute_gradient_oscillation(
        teacher, cfg, train_seqs, n_batches=100
    )

    # Compute zero masks
    print("\n" + "─" * 70, flush=True)
    print("PHASE 2: Compute zero masks (30% zeros for A-C, ~9% for D)", flush=True)
    print("─" * 70, flush=True)
    all_masks = compute_zero_masks(teacher, cfg, sign_cons, zero_frac=0.30)

    # Compute overlaps
    print("\n  Overlap analysis:", flush=True)
    total_params = 0
    total_both = 0
    for li in range(cfg.n_layers):
        for pname in ["gate_proj", "key_proj", "value_proj"]:
            mag_z = all_masks["magnitude"][(li, pname)] == 0
            osc_z = all_masks["oscillation"][(li, pname)] == 0
            both = (mag_z & osc_z).sum()
            total_both += both
            total_params += mag_z.size
    print(f"  Both-agree zeros: {total_both} / {total_params} "
          f"({total_both/total_params*100:.1f}%)", flush=True)

    # ── Variant A: Float32 baseline ──
    print("\n" + "═" * 70, flush=True)
    print("VARIANT A: Float32 baseline (no frozen topology)", flush=True)
    print("═" * 70, flush=True)
    model_a = MicroModel(cfg)
    mx.eval(model_a.parameters())
    loss_a = train(model_a, cfg, train_seqs, ev_in, ev_tgt, label="A-float32")
    print(f"  → A final loss: {loss_a:.4f}", flush=True)

    # ── Variant B: Magnitude zeros ──
    print("\n" + "═" * 70, flush=True)
    print("VARIANT B: FFN magnitude zeros (bottom 30% by |w|)", flush=True)
    print("═" * 70, flush=True)
    model_b = MicroModel(cfg)
    mx.eval(model_b.parameters())
    apply_ffn_topology(model_b, teacher, cfg, all_masks["magnitude"])
    loss_b = train(model_b, cfg, train_seqs, ev_in, ev_tgt, label="B-magnitude")
    print(f"  → B final loss: {loss_b:.4f}", flush=True)

    # ── Variant C: Oscillation zeros ──
    print("\n" + "═" * 70, flush=True)
    print("VARIANT C: FFN oscillation zeros (bottom 30% by sign_consistency)", flush=True)
    print("═" * 70, flush=True)
    model_c = MicroModel(cfg)
    mx.eval(model_c.parameters())
    apply_ffn_topology(model_c, teacher, cfg, all_masks["oscillation"])
    loss_c = train(model_c, cfg, train_seqs, ev_in, ev_tgt, label="C-oscillation")
    print(f"  → C final loss: {loss_c:.4f}", flush=True)

    # ── Variant D: Combined zeros ──
    print("\n" + "═" * 70, flush=True)
    print("VARIANT D: FFN combined zeros (bottom 30% by |w| × sign_cons)", flush=True)
    print("═" * 70, flush=True)
    model_d = MicroModel(cfg)
    mx.eval(model_d.parameters())
    apply_ffn_topology(model_d, teacher, cfg, all_masks["combined"])
    loss_d = train(model_d, cfg, train_seqs, ev_in, ev_tgt, label="D-combined")
    print(f"  → D final loss: {loss_d:.4f}", flush=True)

    # ── Variant E: Both-agree zeros ──
    print("\n" + "═" * 70, flush=True)
    print("VARIANT E: FFN both-agree zeros (only where mag AND osc agree)", flush=True)
    print("═" * 70, flush=True)
    model_e = MicroModel(cfg)
    mx.eval(model_e.parameters())
    apply_ffn_topology(model_e, teacher, cfg, all_masks["both_agree"])
    loss_e = train(model_e, cfg, train_seqs, ev_in, ev_tgt, label="E-both")
    print(f"  → E final loss: {loss_e:.4f}", flush=True)

    # ── Summary ──
    print("\n" + "═" * 70, flush=True)
    print("RESULTS", flush=True)
    print("═" * 70, flush=True)

    results = [
        ("A. Float32 (baseline)", loss_a, "0%", "none"),
        ("B. Magnitude 30%", loss_b, "30%", "|w|"),
        ("C. Oscillation 30%", loss_c, "30%", "sign_cons"),
        ("D. Combined 30%", loss_d, "30%", "|w|×sc"),
        ("E. Both-agree ~9%", loss_e, f"{total_both/total_params*100:.0f}%", "intersection"),
    ]
    best = min(r[1] for r in results)

    print(f"\n{'Variant':>25} | {'Loss':>8} | {'Zeros':>6} | {'Method':>12}", flush=True)
    print("-" * 62, flush=True)
    for name, loss, zeros, method in results:
        mark = " ★" if loss == best else ""
        print(f"{name:>25} | {loss:>8.4f} | {zeros:>6} | {method:>12}{mark}", flush=True)

    print(f"\nElapsed: {time.time()-t0:.0f}s", flush=True)

    # Save
    out_dir = Path("results/ffn-zero-placement")
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "variants": {name: {"loss": loss, "zeros": zeros, "method": method}
                     for name, loss, zeros, method in results},
        "noise_floor": noise_floor,
        "total_params": total_params,
        "both_agree_zeros": int(total_both),
    }
    with open(out_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved to {out_dir / 'summary.json'}", flush=True)


if __name__ == "__main__":
    main()
