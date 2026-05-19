"""Experiment 1: Squeeze the beams — find the plate/beam crossover.

At what beam capacity do plates become load-bearing?
Same task (combinator reduction), same plates (6.9K ternary),
varying beam capacity from full (576 params) to zero.

For each config: beam-only + alternating.
When beam-only drops below alternating → plates carry information.

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
    TernaryLinear, MiniHoloModel,
    generate_batch, evaluate, tokenize,
    masked_ce_loss, plate_fingerprint, plate_diff,
)


# ══════════════════════════════════════════════════════════════════════
# Beam layer variants with different capacity
# ══════════════════════════════════════════════════════════════════════

class BeamLayerFull(nn.Module):
    """Full beam: per-feature scale + bias (current, 2*d params)."""
    def __init__(self, d_model):
        super().__init__()
        self.plate = TernaryLinear(d_model, d_model)
        self.norm = nn.LayerNorm(d_model)
        self.beam_scale = mx.ones((d_model,))
        self.beam_bias = mx.zeros((d_model,))

    def __call__(self, x):
        return x + self.plate(self.norm(x)) * self.beam_scale + self.beam_bias


class BeamLayerScaleOnly(nn.Module):
    """Reduced beam: per-feature scale only (d params)."""
    def __init__(self, d_model):
        super().__init__()
        self.plate = TernaryLinear(d_model, d_model)
        self.norm = nn.LayerNorm(d_model)
        self.beam_scale = mx.ones((d_model,))

    def __call__(self, x):
        return x + self.plate(self.norm(x)) * self.beam_scale


class BeamLayerScalar(nn.Module):
    """Minimal beam: one scalar gain per layer (1 param)."""
    def __init__(self, d_model):
        super().__init__()
        self.plate = TernaryLinear(d_model, d_model)
        self.norm = nn.LayerNorm(d_model)
        self.beam_gain = mx.array([1.0])

    def __call__(self, x):
        return x + self.plate(self.norm(x)) * self.beam_gain


class BeamLayerNone(nn.Module):
    """No beam: raw plate output only."""
    def __init__(self, d_model):
        super().__init__()
        self.plate = TernaryLinear(d_model, d_model)
        self.norm = nn.LayerNorm(d_model)

    def __call__(self, x):
        return x + self.plate(self.norm(x))


# ══════════════════════════════════════════════════════════════════════
# Model factory
# ══════════════════════════════════════════════════════════════════════

BEAM_CONFIGS = {
    "full":       (BeamLayerFull,      "per-feature scale+bias"),
    "scale_only": (BeamLayerScaleOnly, "per-feature scale only"),
    "scalar":     (BeamLayerScalar,    "one scalar per layer"),
    "none":       (BeamLayerNone,      "no beam params"),
}


class ConfigurableModel(nn.Module):
    def __init__(self, d_model=48, n_layers=3, beam_type="full"):
        super().__init__()
        self.d_model = d_model
        LayerClass = BEAM_CONFIGS[beam_type][0]
        self.embed = nn.Embedding(VOCAB_SIZE, d_model)
        self.layers = [LayerClass(d_model) for _ in range(n_layers)]
        self.output_norm = nn.LayerNorm(d_model)
        self.output_proj = nn.Linear(d_model, VOCAB_SIZE)

    def __call__(self, input_ids):
        x = self.embed(input_ids)
        for layer in self.layers:
            x = layer(x)
        return self.output_proj(self.output_norm(x))


def count_params(model):
    from mlx.utils import tree_flatten
    plate = 0
    beam = 0
    embed = 0
    for name, p in tree_flatten(model.parameters()):
        if "plate" in name:
            plate += p.size
        elif "embed" in name or "output" in name:
            embed += p.size
        else:
            beam += p.size
    return {"plate": plate, "beam": beam, "embed": embed,
            "total": plate + beam + embed}


# ══════════════════════════════════════════════════════════════════════
# Training routines
# ══════════════════════════════════════════════════════════════════════

def model_loss(model, input_ids, targets, mask):
    logits = model(input_ids)
    B, T, V = logits.shape
    ce = nn.losses.cross_entropy(
        logits.reshape(-1, V), targets.reshape(-1),
    ).reshape(B, T)
    return (ce * mask).sum() / (mask.sum() + 1e-8)


def run_beam_only(beam_type, n_steps=2000, batch_size=32, lr=0.003):
    """Train only continuous params. Plates frozen random."""
    model = ConfigurableModel(beam_type=beam_type)
    mx.eval(model.parameters())

    # Freeze plates
    for layer in model.layers:
        layer.plate.freeze()

    params = count_params(model)
    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(model, model_loss)
    rng = np.random.RandomState(42)

    best_acc = 0.0
    best_loss = 99.0
    for step in range(n_steps):
        input_ids, targets, mask = generate_batch(batch_size, rng)
        loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        model.update(optimizer.apply_gradients(grads, model))
        mx.eval(model.parameters())
        del loss_val, grads, input_ids, targets, mask
        if (step + 1) % 50 == 0:
            mx.clear_cache()

        if (step + 1) % 500 == 0 or step == 0:
            ev = evaluate(model, np.random.RandomState(999))
            if ev["accuracy"] > best_acc:
                best_acc = ev["accuracy"]
                best_loss = ev["loss"]

    ev = evaluate(model, np.random.RandomState(999))
    if ev["accuracy"] > best_acc:
        best_acc = ev["accuracy"]
        best_loss = ev["loss"]

    return {"beam_type": beam_type, "mode": "beam_only",
            "best_acc": best_acc, "best_loss": best_loss, **params}


def run_alternating(beam_type, n_rounds=10, etch_batches=200,
                    beam_steps=200, batch_size=32, lr=0.003):
    """Etch plates then train beams, alternating."""
    model = ConfigurableModel(beam_type=beam_type)
    mx.eval(model.parameters())
    params = count_params(model)
    rng = np.random.RandomState(42)

    best_acc = 0.0
    best_loss = 99.0

    for round_idx in range(n_rounds):
        # Phase 1: Etch plates
        accumulators = {}
        for i, layer in enumerate(model.layers):
            shape = (layer.plate.out_features, layer.plate.in_features)
            accumulators[i] = np.zeros(shape, dtype=np.float64)

        loss_and_grad = nn.value_and_grad(model, model_loss)
        for b in range(etch_batches):
            input_ids, targets, mask = generate_batch(batch_size, rng)
            loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
            mx.eval(loss_val, grads)
            for i, layer in enumerate(model.layers):
                g = grads["layers"][i]["plate"]["weight"]
                mx.eval(g)
                accumulators[i] += np.sign(np.array(g))
            del loss_val, grads, input_ids, targets, mask
            if (b + 1) % 50 == 0:
                mx.clear_cache()

        total_flipped = 0
        for i, layer in enumerate(model.layers):
            acc = accumulators[i]
            confidence = np.abs(acc) / etch_batches
            target_sign = np.sign(acc)
            current = layer.plate.signs
            should_flip = ((confidence > 0.6) & (target_sign != 0) &
                           (target_sign != current))
            new_signs = np.where(should_flip, target_sign, current)
            layer.plate.weight = mx.array(new_signs.astype(np.float32))
            mx.eval(layer.plate.weight)
            total_flipped += int(should_flip.sum())

        # Phase 2: Train beams
        optimizer = optim.Adam(learning_rate=lr)
        loss_and_grad_beam = nn.value_and_grad(model, model_loss)
        for step in range(beam_steps):
            input_ids, targets, mask = generate_batch(batch_size, rng)
            loss_val, grads = loss_and_grad_beam(model, input_ids, targets, mask)
            mx.eval(loss_val, grads)
            # Zero plate grads
            for i in range(len(model.layers)):
                if "plate" in grads["layers"][i]:
                    grads["layers"][i]["plate"]["weight"] = mx.zeros_like(
                        grads["layers"][i]["plate"]["weight"])
            model.update(optimizer.apply_gradients(grads, model))
            mx.eval(model.parameters())
            del loss_val, grads, input_ids, targets, mask
            if (step + 1) % 50 == 0:
                mx.clear_cache()

        ev = evaluate(model, np.random.RandomState(999))
        if ev["accuracy"] > best_acc:
            best_acc = ev["accuracy"]
            best_loss = ev["loss"]

    return {"beam_type": beam_type, "mode": "alternating",
            "best_acc": best_acc, "best_loss": best_loss,
            "final_flips": total_flipped, **params}


def run_plate_only(beam_type, n_rounds=10, etch_batches=200, batch_size=32):
    """Etch plates only, no beam training."""
    model = ConfigurableModel(beam_type=beam_type)
    mx.eval(model.parameters())
    params = count_params(model)
    rng = np.random.RandomState(42)

    best_acc = 0.0
    best_loss = 99.0

    for round_idx in range(n_rounds):
        accumulators = {}
        for i, layer in enumerate(model.layers):
            shape = (layer.plate.out_features, layer.plate.in_features)
            accumulators[i] = np.zeros(shape, dtype=np.float64)

        loss_and_grad = nn.value_and_grad(model, model_loss)
        for b in range(etch_batches):
            input_ids, targets, mask = generate_batch(batch_size, rng)
            loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
            mx.eval(loss_val, grads)
            for i, layer in enumerate(model.layers):
                g = grads["layers"][i]["plate"]["weight"]
                mx.eval(g)
                accumulators[i] += np.sign(np.array(g))
            del loss_val, grads, input_ids, targets, mask
            if (b + 1) % 50 == 0:
                mx.clear_cache()

        for i, layer in enumerate(model.layers):
            acc = accumulators[i]
            confidence = np.abs(acc) / etch_batches
            target_sign = np.sign(acc)
            current = layer.plate.signs
            should_flip = ((confidence > 0.6) & (target_sign != 0) &
                           (target_sign != current))
            new_signs = np.where(should_flip, target_sign, current)
            layer.plate.weight = mx.array(new_signs.astype(np.float32))
            mx.eval(layer.plate.weight)

        ev = evaluate(model, np.random.RandomState(999))
        if ev["accuracy"] > best_acc:
            best_acc = ev["accuracy"]
            best_loss = ev["loss"]
        mx.clear_cache()

    return {"beam_type": beam_type, "mode": "plate_only",
            "best_acc": best_acc, "best_loss": best_loss, **params}


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    output_dir = Path("checkpoints/mini-holo-exp1")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("  EXPERIMENT 1: Squeeze the Beams")
    print("  Finding the plate/beam crossover point")
    print("=" * 70)

    results = []

    for beam_type in ["full", "scale_only", "scalar", "none"]:
        label = BEAM_CONFIGS[beam_type][1]
        print(f"\n{'─' * 70}")
        print(f"  Config: {beam_type} ({label})")
        print(f"{'─' * 70}")

        # Count params for display
        test_model = ConfigurableModel(beam_type=beam_type)
        mx.eval(test_model.parameters())
        params = count_params(test_model)
        print(f"  Plates: {params['plate']:,}  Beam: {params['beam']:,}  "
              f"Embed: {params['embed']:,}")
        del test_model

        # Beam-only
        print(f"  Running beam-only...", end="", flush=True)
        t0 = time.time()
        r1 = run_beam_only(beam_type)
        print(f" acc={r1['best_acc']:.1%} loss={r1['best_loss']:.4f} "
              f"({time.time()-t0:.1f}s)")
        results.append(r1)

        # Plate-only
        print(f"  Running plate-only...", end="", flush=True)
        t0 = time.time()
        r2 = run_plate_only(beam_type)
        print(f" acc={r2['best_acc']:.1%} loss={r2['best_loss']:.4f} "
              f"({time.time()-t0:.1f}s)")
        results.append(r2)

        # Alternating
        print(f"  Running alternating...", end="", flush=True)
        t0 = time.time()
        r3 = run_alternating(beam_type)
        print(f" acc={r3['best_acc']:.1%} loss={r3['best_loss']:.4f} "
              f"({time.time()-t0:.1f}s)")
        results.append(r3)

    # ── Summary ───────────────────────────────────────────────
    print(f"\n{'=' * 70}")
    print("  SUMMARY: Beam capacity vs accuracy")
    print(f"{'=' * 70}")
    print(f"  {'Config':<15} {'Beam#':>6} {'Beam-only':>10} "
          f"{'Plate-only':>11} {'Alternating':>12}")
    print(f"  {'─'*15} {'─'*6} {'─'*10} {'─'*11} {'─'*12}")

    for beam_type in ["full", "scale_only", "scalar", "none"]:
        beam_r = [r for r in results
                  if r["beam_type"] == beam_type and r["mode"] == "beam_only"]
        plate_r = [r for r in results
                   if r["beam_type"] == beam_type and r["mode"] == "plate_only"]
        alt_r = [r for r in results
                 if r["beam_type"] == beam_type and r["mode"] == "alternating"]

        beam_acc = beam_r[0]["best_acc"] if beam_r else 0
        plate_acc = plate_r[0]["best_acc"] if plate_r else 0
        alt_acc = alt_r[0]["best_acc"] if alt_r else 0
        n_beam = beam_r[0]["beam"] if beam_r else 0

        # Mark crossover
        marker = " ← CROSSOVER" if alt_acc > beam_acc + 0.01 else ""
        print(f"  {beam_type:<15} {n_beam:>6} {beam_acc:>9.1%} "
              f"{plate_acc:>10.1%} {alt_acc:>11.1%}{marker}")

    # Save
    with open(output_dir / "results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Saved to {output_dir}/results.json")


if __name__ == "__main__":
    main()
