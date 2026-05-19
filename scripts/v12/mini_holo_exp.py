"""Mini Holographic Microscope — Experiment 0: Fundamental Decomposition.

Four runs isolating plate vs beam contribution:
  0. GD baseline (regular Linear, no ternary) — the ceiling
  1. Beam-only (plates frozen random) — can beams read a random plate?
  2. Plate-only (etch, beams frozen) — can plates encode without beams?
  3. Alternating (etch then beam) — current protocol

Same task: combinator reduction (K, I, B, C).
Same model size: d=48, 3 layers.

License: MIT
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim

from mini_holo import (
    VOCAB_SIZE, PAD_ID, BOS_ID, EOS_ID, EQ_ID,
    TernaryLinear, BeamLayer, MiniHoloModel,
    generate_batch, evaluate, measure_geometry,
    tokenize, count_plate_params, plate_fingerprint, plate_diff,
    masked_ce_loss,
)


# ══════════════════════════════════════════════════════════════════════
# GD Baseline model (regular Linear, no ternary constraint)
# ══════════════════════════════════════════════════════════════════════

class GDLayer(nn.Module):
    """Regular linear layer + norm + residual. No ternary constraint."""

    def __init__(self, d_model: int):
        super().__init__()
        self.linear = nn.Linear(d_model, d_model)
        self.norm = nn.LayerNorm(d_model)

    def __call__(self, x: mx.array) -> mx.array:
        return x + self.linear(self.norm(x))


class GDModel(nn.Module):
    """Same architecture as MiniHoloModel but with regular Linear layers."""

    def __init__(self, d_model: int = 48, n_layers: int = 3):
        super().__init__()
        self.d_model = d_model
        self.embed = nn.Embedding(VOCAB_SIZE, d_model)
        self.layers = [GDLayer(d_model) for _ in range(n_layers)]
        self.output_norm = nn.LayerNorm(d_model)
        self.output_proj = nn.Linear(d_model, VOCAB_SIZE)

    def __call__(self, input_ids: mx.array) -> mx.array:
        x = self.embed(input_ids)
        for layer in self.layers:
            x = layer(x)
        return self.output_proj(self.output_norm(x))


def gd_loss(model, input_ids, targets, mask):
    logits = model(input_ids)
    B, T, V = logits.shape
    ce = nn.losses.cross_entropy(
        logits.reshape(-1, V), targets.reshape(-1),
    ).reshape(B, T)
    return (ce * mask).sum() / (mask.sum() + 1e-8)


def gd_evaluate(model, rng, n_batches=50, batch_size=64):
    total_correct = 0
    total_tokens = 0
    total_loss = 0.0
    for _ in range(n_batches):
        input_ids, targets, mask = generate_batch(batch_size, rng)
        logits = model(input_ids)
        mx.eval(logits)
        B, T, V = logits.shape
        ce = nn.losses.cross_entropy(
            logits.reshape(-1, V), targets.reshape(-1),
        ).reshape(B, T)
        loss = (ce * mask).sum() / (mask.sum() + 1e-8)
        mx.eval(loss)
        total_loss += float(loss.item())
        preds = mx.argmax(logits, axis=-1)
        correct = (preds == targets).astype(mx.float32) * mask
        mx.eval(correct)
        total_correct += float(correct.sum().item())
        total_tokens += float(mask.sum().item())
    return {
        "loss": total_loss / n_batches,
        "accuracy": total_correct / max(total_tokens, 1),
    }


# ══════════════════════════════════════════════════════════════════════
# Experiment runners
# ══════════════════════════════════════════════════════════════════════

def run_exp0_gd_baseline(n_steps=2000, batch_size=32, lr=0.003):
    """Experiment 0: Full GD on regular Linear layers. The ceiling."""
    print("\n" + "=" * 60)
    print("  EXP 0: GD Baseline (no ternary constraint)")
    print("=" * 60)

    model = GDModel(d_model=48, n_layers=3)
    mx.eval(model.parameters())

    from mlx.utils import tree_flatten
    n_params = sum(p.size for _, p in tree_flatten(model.parameters()))
    print(f"  Parameters: {n_params:,} (all continuous)")

    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(model, gd_loss)
    rng = np.random.RandomState(42)

    log = []
    for step in range(n_steps):
        input_ids, targets, mask = generate_batch(batch_size, rng)
        loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        model.update(optimizer.apply_gradients(grads, model))
        mx.eval(model.parameters())
        del loss_val, grads, input_ids, targets, mask
        if (step + 1) % 50 == 0:
            mx.clear_cache()

        if (step + 1) % 200 == 0 or step == 0:
            ev = gd_evaluate(model, np.random.RandomState(999))
            log.append({"step": step + 1, **ev})
            print(f"  Step {step+1:5d} | loss={ev['loss']:.4f} "
                  f"acc={ev['accuracy']:.1%}")

    return log


def run_exp1_beam_only(n_rounds=20, beam_steps=500, batch_size=32, lr=0.003):
    """Experiment 1: Plates frozen random, train only beams + embeds."""
    print("\n" + "=" * 60)
    print("  EXP 1: Beam-Only (plates frozen random)")
    print("=" * 60)

    model = MiniHoloModel(d_model=48, n_layers=3)
    mx.eval(model.parameters())

    # Freeze plates permanently
    for layer in model.layers:
        layer.plate.freeze()

    params = count_plate_params(model)
    print(f"  Plates: {params['plate_positions']:,} (FROZEN)")
    print(f"  Beams:  {params['beam_params']:,} (trainable)")
    print(f"  Embeds: {params['embed_params']:,} (trainable)")

    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
    rng = np.random.RandomState(42)

    log = []
    total_steps = 0
    for round_idx in range(n_rounds):
        losses = []
        for step in range(beam_steps):
            input_ids, targets, mask = generate_batch(batch_size, rng)
            loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
            mx.eval(loss_val, grads)
            losses.append(float(loss_val.item()))
            model.update(optimizer.apply_gradients(grads, model))
            mx.eval(model.parameters())
            del loss_val, grads, input_ids, targets, mask
            total_steps += 1
            if total_steps % 50 == 0:
                mx.clear_cache()

        ev = evaluate(model, np.random.RandomState(999))
        log.append({"round": round_idx + 1, "steps": total_steps, **ev})
        print(f"  Round {round_idx+1:3d} | steps={total_steps:5d} | "
              f"loss={ev['loss']:.4f} acc={ev['accuracy']:.1%} | "
              f"train_loss={np.mean(losses[-50:]):.4f}")

    return log


def run_exp2_plate_only(n_rounds=20, etch_batches=200, batch_size=32):
    """Experiment 2: Etch plates, beams frozen at init."""
    print("\n" + "=" * 60)
    print("  EXP 2: Plate-Only (beams frozen, etch plates)")
    print("=" * 60)

    model = MiniHoloModel(d_model=48, n_layers=3)
    mx.eval(model.parameters())

    params = count_plate_params(model)
    print(f"  Plates: {params['plate_positions']:,} (etchable)")
    print(f"  Beams:  {params['beam_params']:,} (FROZEN)")
    print(f"  Embeds: {params['embed_params']:,} (FROZEN)")

    rng = np.random.RandomState(42)

    log = []
    for round_idx in range(n_rounds):
        before = plate_fingerprint(model)

        # Accumulate directions
        accumulators = {}
        for i, layer in enumerate(model.layers):
            shape = (layer.plate.out_features, layer.plate.in_features)
            accumulators[i] = np.zeros(shape, dtype=np.float64)

        loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
        losses = []

        for _ in range(etch_batches):
            input_ids, targets, mask = generate_batch(batch_size, rng)
            loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
            mx.eval(loss_val, grads)
            losses.append(float(loss_val.item()))
            for i, layer in enumerate(model.layers):
                g = grads["layers"][i]["plate"]["weight"]
                mx.eval(g)
                accumulators[i] += np.sign(np.array(g))
            del loss_val, grads
            if (_ + 1) % 50 == 0:
                mx.clear_cache()

        # Etch: flip confident positions
        total_flipped = 0
        for i, layer in enumerate(model.layers):
            acc = accumulators[i]
            confidence = np.abs(acc) / etch_batches
            target_sign = np.sign(acc)
            current = layer.plate.signs
            should_flip = (confidence > 0.6) & (target_sign != 0) & (target_sign != current)
            new_signs = np.where(should_flip, target_sign, current).astype(np.float32)
            layer.plate.weight = mx.array(new_signs)
            mx.eval(layer.plate.weight)
            total_flipped += int(should_flip.sum())

        after = plate_fingerprint(model)
        diff = plate_diff(before, after)
        ev = evaluate(model, np.random.RandomState(999))
        log.append({"round": round_idx + 1, "flips": total_flipped,
                     "flip_frac": diff["fraction"], **ev})
        print(f"  Round {round_idx+1:3d} | flips={total_flipped:5d} "
              f"({diff['fraction']:.1%}) | loss={ev['loss']:.4f} "
              f"acc={ev['accuracy']:.1%}")
        mx.clear_cache()

    return log


def run_exp3_alternating(n_rounds=20, etch_batches=200, beam_steps=500,
                         batch_size=32, lr=0.003):
    """Experiment 3: Etch plates then train beams, alternating."""
    print("\n" + "=" * 60)
    print("  EXP 3: Alternating (etch plates → train beams)")
    print("=" * 60)

    model = MiniHoloModel(d_model=48, n_layers=3)
    mx.eval(model.parameters())

    params = count_plate_params(model)
    print(f"  Plates: {params['plate_positions']:,} (etchable)")
    print(f"  Beams:  {params['beam_params']:,} (trainable)")
    print(f"  Embeds: {params['embed_params']:,} (trainable)")

    rng = np.random.RandomState(42)

    log = []
    for round_idx in range(n_rounds):
        before = plate_fingerprint(model)

        # Phase 1: Etch
        accumulators = {}
        for i, layer in enumerate(model.layers):
            shape = (layer.plate.out_features, layer.plate.in_features)
            accumulators[i] = np.zeros(shape, dtype=np.float64)

        loss_and_grad_etch = nn.value_and_grad(model, masked_ce_loss)
        etch_losses = []
        for _ in range(etch_batches):
            input_ids, targets, mask = generate_batch(batch_size, rng)
            loss_val, grads = loss_and_grad_etch(model, input_ids, targets, mask)
            mx.eval(loss_val, grads)
            etch_losses.append(float(loss_val.item()))
            for i, layer in enumerate(model.layers):
                g = grads["layers"][i]["plate"]["weight"]
                mx.eval(g)
                accumulators[i] += np.sign(np.array(g))
            del loss_val, grads
            if (_ + 1) % 50 == 0:
                mx.clear_cache()

        # Flip
        total_flipped = 0
        for i, layer in enumerate(model.layers):
            acc = accumulators[i]
            confidence = np.abs(acc) / etch_batches
            target_sign = np.sign(acc)
            current = layer.plate.signs
            should_flip = (confidence > 0.6) & (target_sign != 0) & (target_sign != current)
            new_signs = np.where(should_flip, target_sign, current).astype(np.float32)
            layer.plate.weight = mx.array(new_signs)
            mx.eval(layer.plate.weight)
            total_flipped += int(should_flip.sum())

        after = plate_fingerprint(model)
        diff = plate_diff(before, after)

        # Phase 2: Beam training
        optimizer = optim.Adam(learning_rate=lr)
        loss_and_grad_beam = nn.value_and_grad(model, masked_ce_loss)
        beam_losses = []
        for step in range(beam_steps):
            input_ids, targets, mask = generate_batch(batch_size, rng)
            loss_val, grads = loss_and_grad_beam(model, input_ids, targets, mask)
            mx.eval(loss_val, grads)
            beam_losses.append(float(loss_val.item()))
            # Zero plate grads
            for i in range(len(model.layers)):
                if "plate" in grads["layers"][i]:
                    grads["layers"][i]["plate"]["weight"] = mx.zeros_like(
                        grads["layers"][i]["plate"]["weight"])
            model.update(optimizer.apply_gradients(grads, model))
            mx.eval(model.parameters())
            del loss_val, grads
            if (step + 1) % 50 == 0:
                mx.clear_cache()

        ev = evaluate(model, np.random.RandomState(999))
        log.append({
            "round": round_idx + 1,
            "flips": total_flipped,
            "flip_frac": diff["fraction"],
            "beam_start": float(np.mean(beam_losses[:10])),
            "beam_end": float(np.mean(beam_losses[-10:])),
            **ev,
        })
        print(f"  Round {round_idx+1:3d} | flips={total_flipped:5d} "
              f"({diff['fraction']:.1%}) | beam {np.mean(beam_losses[:10]):.3f}"
              f"→{np.mean(beam_losses[-10:]):.3f} | "
              f"loss={ev['loss']:.4f} acc={ev['accuracy']:.1%}")

    return log


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    output_dir = Path("checkpoints/mini-holo-exp0")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  EXPERIMENT 0: Fundamental Decomposition")
    print("  Isolating plate vs beam contribution")
    print("  Task: combinator reduction (K, I, B, C)")
    print("  Model: d=48, 3 layers, ~9K params")
    print("=" * 60)

    results = {}

    t0 = time.time()
    results["exp0_gd"] = run_exp0_gd_baseline(n_steps=2000)
    t1 = time.time()
    results["exp1_beam"] = run_exp1_beam_only(n_rounds=20, beam_steps=500)
    t2 = time.time()
    results["exp2_plate"] = run_exp2_plate_only(n_rounds=20, etch_batches=200)
    t3 = time.time()
    results["exp3_alt"] = run_exp3_alternating(n_rounds=20, etch_batches=200, beam_steps=500)
    t4 = time.time()

    # ── Summary ───────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)

    def best(log, key="accuracy"):
        return max(log, key=lambda x: x[key])

    for name, log in results.items():
        b = best(log)
        step_key = "step" if "step" in b else "round"
        print(f"  {name:20s}: best acc={b['accuracy']:.1%} "
              f"loss={b['loss']:.4f} @ {step_key}={b[step_key]}")

    print(f"\n  Timing:")
    print(f"    GD baseline:  {t1-t0:.1f}s")
    print(f"    Beam-only:    {t2-t1:.1f}s")
    print(f"    Plate-only:   {t3-t2:.1f}s")
    print(f"    Alternating:  {t4-t3:.1f}s")

    # Save
    with open(output_dir / "results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to {output_dir}/results.json")


if __name__ == "__main__":
    main()
