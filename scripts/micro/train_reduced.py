#!/usr/bin/env python3
"""
Train with β-reduced topology — one SVD, three outcomes.

Variant H: reduce_attention() applied to all layers, then train from scratch.
Compares to existing variants A-G.

Also sweeps zero_threshold to find the optimal reduction depth.

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
import mlx.optimizers as optim
from mlx.utils import tree_flatten

sys.path.insert(0, str(Path(__file__).parent))
from micro_model import MicroModel, MicroConfig
from reduce import reduce_attention, measure_mspace


# ══════════════════════════════════════════════════════════════════════
# Data (same as other train scripts)
# ══════════════════════════════════════════════════════════════════════

def load_compile_examples(path):
    examples = []
    with open(path) as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line.strip()))
    return examples

def tokenize_examples(examples, tokenizer, max_len=256, eod_id=151643):
    sequences = []
    for ex in examples:
        text = f"{ex['input']}\n{ex['output']}"
        ids = tokenizer.encode(text, add_special_tokens=False)
        ids.append(eod_id)
        sequences.append(np.array(ids[:max_len], dtype=np.int32))
    return sequences

class DataLoader:
    def __init__(self, sequences, batch_size, seq_len, eod_id=151643, seed=42):
        self.sequences = sequences
        self.batch_size = batch_size
        self.seq_len = seq_len
        self.rng = np.random.RandomState(seed)
        self._rebuild()

    def _rebuild(self):
        idx = self.rng.permutation(len(self.sequences))
        self.stream = np.concatenate([self.sequences[i] for i in idx])
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
# Apply reduction to model
# ══════════════════════════════════════════════════════════════════════

def apply_reduction(model, cfg, trained_model, zero_threshold=0.5, flip_threshold=0.0):
    """Apply reduce_attention to all layers, freeze Q/K."""
    mx.eval(trained_model.parameters())
    all_stats = {}

    for li in range(cfg.n_layers):
        W_q = np.array(trained_model.blocks[li].attn.q_proj.weight)
        W_k = np.array(trained_model.blocks[li].attn.k_proj.weight)

        result = reduce_attention(W_q, W_k,
                                  zero_threshold=zero_threshold,
                                  flip_threshold=flip_threshold)

        # Set effective weights = ternary × gamma
        block = model.blocks[li]
        block.attn.q_proj.weight = mx.array(result["W_q_ternary"] * result["gamma_q"])
        block.attn.k_proj.weight = mx.array(result["W_k_ternary"] * result["gamma_k"])
        block.attn.q_proj.freeze(keys=["weight"])
        block.attn.k_proj.freeze(keys=["weight"])

        all_stats[li] = result["stats"]

    mx.eval(model.parameters())
    return all_stats


# ══════════════════════════════════════════════════════════════════════
# Training
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
            _, el = model(eval_input, eval_target)
            mx.eval(el)
            elapsed = time.time() - t_start
            tl = float(loss_val.item())
            elv = float(el.item())
            gn = float(gnorm.item())
            print(f"    step {step:>5}: train={tl:.4f}, eval={elv:.4f}, "
                  f"gnorm={gn:.2f}, {elapsed:.0f}s", flush=True)
            curve.append({"step": step, "train_loss": tl, "eval_loss": elv})
    return curve


def mspace_all(model, cfg):
    mx.eval(model.parameters())
    r = {}
    for li in range(cfg.n_layers):
        W_q = np.array(model.blocks[li].attn.q_proj.weight)
        W_k = np.array(model.blocks[li].attn.k_proj.weight)
        r[li] = measure_mspace(W_q, W_k)
    return r


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    t0 = time.time()
    print("=" * 70, flush=True)
    print("β-REDUCED TOPOLOGY — One SVD, Three Outcomes", flush=True)
    print("=" * 70, flush=True)
    print(flush=True)

    cfg = MicroConfig()

    # Load trained model for topology extraction
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

    # Existing results
    print(flush=True)
    print("Existing results:", flush=True)
    print("  A. Float32:              loss 6.7412, L2 rank90=6", flush=True)
    print("  B. Sign-only (±1):       loss 6.8625, L2 rank90=32", flush=True)
    print("  C. M-noise 30% zeros:    loss 6.6972, L2 rank90=25  ★ best", flush=True)
    print(flush=True)

    # ── Sweep zero_threshold to find optimal reduction depth ──
    # Higher threshold = more aggressive zeroing, lower = more conservative
    thresholds = [0.3, 0.5, 0.7, 1.0, 1.5, 2.0]

    results = {"variants": []}

    for zt in thresholds:
        print(f"{'═'*70}", flush=True)
        print(f"  H. β-reduced (zero_thresh={zt})", flush=True)
        print(f"{'═'*70}", flush=True)

        model = MicroModel(cfg)
        mx.eval(model.parameters())

        stats = apply_reduction(model, cfg, trained_model,
                                zero_threshold=zt, flip_threshold=0.0)

        # Report reduction stats
        for li in [0, 2]:
            s = stats[li]
            q = s["q"]
            print(f"  Layer {li}: K={s['K']} modes | "
                  f"Q: {q['zero_frac']:.0%} zero, {q['flip_frac']:.0%} flip, "
                  f"snr={q['mean_snr']:.2f}", flush=True)

        init_ms = mspace_all(model, cfg)
        _, init_loss = model(eval_input, eval_target)
        mx.eval(init_loss)
        print(f"  Init: loss={float(init_loss.item()):.4f}, "
              f"L2 rank90={init_ms[2]['rank90']}, "
              f"top1={init_ms[2]['top1_pct']:.1f}%", flush=True)
        print(flush=True)

        # Train
        loader = DataLoader(train_seqs, cfg.batch_size, cfg.max_seq_len,
                            cfg.eod_id, seed=42)
        curve = train_variant(model, cfg, loader, eval_input, eval_target)

        final_ms = mspace_all(model, cfg)
        _, final_loss = model(eval_input, eval_target)
        mx.eval(final_loss)
        fl = float(final_loss.item())

        print(f"\n  Final: loss={fl:.4f}, L2 rank90={final_ms[2]['rank90']}, "
              f"top1={final_ms[2]['top1_pct']:.1f}%", flush=True)
        print(flush=True)

        results["variants"].append({
            "name": f"H. β-reduced (zt={zt})",
            "zero_threshold": zt,
            "final_loss": fl,
            "init_loss": float(init_loss.item()),
            "final_mspace": {str(k): v for k, v in final_ms.items()},
            "reduction_stats": {str(k): v for k, v in stats.items()},
            "curve": curve,
        })

    # ── Summary ──
    elapsed = time.time() - t0
    print(f"{'═'*70}", flush=True)
    print("ALL VARIANTS COMPARISON", flush=True)
    print(f"{'═'*70}", flush=True)
    print(flush=True)

    all_variants = [
        ("A. Float32",          6.7412,  6, 80.5, "—"),
        ("B. Sign-only",        6.8625, 32, 45.5, "—"),
        ("C. M-noise 30%",      6.6972, 25, 56.1, "—"),
    ]
    for r in results["variants"]:
        zt = r["zero_threshold"]
        zf = r["reduction_stats"]["2"]["q"]["zero_frac"]
        ff = r["reduction_stats"]["2"]["q"]["flip_frac"]
        all_variants.append((
            r["name"],
            r["final_loss"],
            r["final_mspace"]["2"]["rank90"],
            r["final_mspace"]["2"]["top1_pct"],
            f"{zf:.0%}z {ff:.0%}f",
        ))

    best_loss = min(v[1] for v in all_variants)
    print(f"{'Variant':>30} │ {'Loss':>8} │ {'L2 r90':>6} │ {'L2 top1':>7} │ {'Q reduction':>12}", flush=True)
    print("─" * 80, flush=True)
    for name, loss, r90, t1, red in all_variants:
        marker = " ★" if loss == best_loss else ""
        print(f"{name:>30} │ {loss:>8.4f} │ {r90:>6} │ {t1:>6.1f}% │ {red:>12}{marker}", flush=True)

    print(f"\nElapsed: {elapsed:.0f}s ({elapsed/60:.1f}m)", flush=True)

    out_dir = Path("results/reduced-train")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "summary.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved to results/reduced-train/summary.json", flush=True)


if __name__ == "__main__":
    main()
