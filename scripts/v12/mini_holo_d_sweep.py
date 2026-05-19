"""Mini Holographic Microscope — D-Sweep: Finding the Plate/Beam Crossover.

Runs the four-way decomposition (GD, beam-only, plate-only, alternating)
across d values [48, 96, 128, 192, 256] to find where plates become
load-bearing.

Additionally tests BEAM-FIRST alternating (train beams → etch plates)
vs the original ETCH-FIRST alternating (etch plates → train beams) at
each scale. This validates whether beam-first remains correct at the
crossover.

Measures per d:
  - Four-way accuracy (GD, beam-only, plate-only, alternating)
  - Beam-first vs etch-first comparison
  - Flip rate per round in alternating modes
  - Number of cycles to convergence
  - GD-minus-beam-only gap (the crossover signal)
  - Plate/beam parameter ratio

Task: combinator reduction (K, I, B, C) — same as mini_holo_exp.py.

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
    generate_batch, tokenize,
    count_plate_params, plate_fingerprint, plate_diff,
)


# ══════════════════════════════════════════════════════════════════════
# GD Baseline model (regular Linear, no ternary constraint)
# ══════════════════════════════════════════════════════════════════════

class GDLayer(nn.Module):
    """Regular linear layer + norm + residual."""
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


# ══════════════════════════════════════════════════════════════════════
# Loss & eval (shared)
# ══════════════════════════════════════════════════════════════════════

def masked_ce_loss(model, input_ids, targets, mask):
    logits = model(input_ids)
    B, T, V = logits.shape
    ce = nn.losses.cross_entropy(
        logits.reshape(-1, V), targets.reshape(-1),
    ).reshape(B, T)
    return (ce * mask).sum() / (mask.sum() + 1e-8)


def eval_model(model, rng, n_batches=50, batch_size=64):
    """Evaluate accuracy on combinator reduction task."""
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
# Etch helper — accumulate gradient directions then flip
# ══════════════════════════════════════════════════════════════════════

def etch_plates(model, rng, n_batches=200, batch_size=32):
    """Accumulate gradient signs, flip confident positions. Returns flip stats."""
    before = plate_fingerprint(model)

    accumulators = {}
    for i, layer in enumerate(model.layers):
        shape = (layer.plate.out_features, layer.plate.in_features)
        accumulators[i] = np.zeros(shape, dtype=np.float64)

    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)

    for b in range(n_batches):
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
        confidence = np.abs(acc) / n_batches
        target_sign = np.sign(acc)
        current = layer.plate.signs
        should_flip = (
            (confidence > 0.6) & (target_sign != 0) & (target_sign != current)
        )
        new_signs = np.where(should_flip, target_sign, current).astype(np.float32)
        layer.plate.weight = mx.array(new_signs)
        mx.eval(layer.plate.weight)
        total_flipped += int(should_flip.sum())

    after = plate_fingerprint(model)
    diff = plate_diff(before, after)
    return total_flipped, diff["fraction"]


def train_beams(model, rng, n_steps=500, batch_size=32, lr=0.003):
    """Train only continuous params (plates frozen via zeroed grads)."""
    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
    losses = []

    for step in range(n_steps):
        input_ids, targets, mask = generate_batch(batch_size, rng)
        loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        losses.append(float(loss_val.item()))
        # Zero plate grads
        for i in range(len(model.layers)):
            if "plate" in grads["layers"][i]:
                grads["layers"][i]["plate"]["weight"] = mx.zeros_like(
                    grads["layers"][i]["plate"]["weight"]
                )
        model.update(optimizer.apply_gradients(grads, model))
        mx.eval(model.parameters())
        del loss_val, grads, input_ids, targets, mask
        if (step + 1) % 50 == 0:
            mx.clear_cache()

    return losses


# ══════════════════════════════════════════════════════════════════════
# Experiment conditions
# ══════════════════════════════════════════════════════════════════════

def run_gd(d_model, n_layers=3, n_steps=2000, batch_size=32, lr=0.003):
    """Full GD baseline — no ternary constraint."""
    model = GDModel(d_model=d_model, n_layers=n_layers)
    mx.eval(model.parameters())

    from mlx.utils import tree_flatten
    n_params = sum(p.size for _, p in tree_flatten(model.parameters()))

    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
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

        if (step + 1) % 500 == 0:
            ev = eval_model(model, np.random.RandomState(999))
            log.append({"step": step + 1, **ev})

    final = eval_model(model, np.random.RandomState(999))
    log.append({"step": n_steps, **final})
    return {"best_acc": max(e["accuracy"] for e in log),
            "best_loss": min(e["loss"] for e in log),
            "n_params": n_params, "log": log}


def run_beam_only(d_model, n_layers=3, n_steps=2000, batch_size=32, lr=0.003):
    """Plates frozen random, train only beams + embeds."""
    model = MiniHoloModel(d_model=d_model, n_layers=n_layers)
    mx.eval(model.parameters())

    # Freeze plates
    for layer in model.layers:
        layer.plate.freeze()

    params = count_plate_params(model)

    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
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

        if (step + 1) % 500 == 0:
            ev = eval_model(model, np.random.RandomState(999))
            log.append({"step": step + 1, **ev})

    final = eval_model(model, np.random.RandomState(999))
    log.append({"step": n_steps, **final})
    return {"best_acc": max(e["accuracy"] for e in log),
            "best_loss": min(e["loss"] for e in log),
            "params": params, "log": log}


def run_plate_only(d_model, n_layers=3, n_rounds=15, etch_batches=200,
                   batch_size=32):
    """Etch plates only, beams frozen at init."""
    model = MiniHoloModel(d_model=d_model, n_layers=n_layers)
    mx.eval(model.parameters())
    params = count_plate_params(model)
    rng = np.random.RandomState(42)

    log = []
    for r in range(n_rounds):
        flips, flip_frac = etch_plates(model, rng, n_batches=etch_batches,
                                       batch_size=batch_size)
        ev = eval_model(model, np.random.RandomState(999))
        log.append({"round": r + 1, "flips": flips,
                     "flip_frac": flip_frac, **ev})
        mx.clear_cache()

    return {"best_acc": max(e["accuracy"] for e in log),
            "best_loss": min(e["loss"] for e in log),
            "params": params, "log": log}


def run_etch_first(d_model, n_layers=3, n_rounds=15, etch_batches=200,
                   beam_steps=500, batch_size=32, lr=0.003):
    """Original protocol: etch plates → train beams (alternating)."""
    model = MiniHoloModel(d_model=d_model, n_layers=n_layers)
    mx.eval(model.parameters())
    params = count_plate_params(model)
    rng = np.random.RandomState(42)

    log = []
    for r in range(n_rounds):
        # Phase 1: etch
        flips, flip_frac = etch_plates(model, rng, n_batches=etch_batches,
                                       batch_size=batch_size)
        # Phase 2: beam
        losses = train_beams(model, rng, n_steps=beam_steps,
                             batch_size=batch_size, lr=lr)
        ev = eval_model(model, np.random.RandomState(999))
        log.append({
            "round": r + 1, "flips": flips, "flip_frac": flip_frac,
            "beam_start": float(np.mean(losses[:10])),
            "beam_end": float(np.mean(losses[-10:])),
            **ev,
        })
        mx.clear_cache()

    return {"best_acc": max(e["accuracy"] for e in log),
            "best_loss": min(e["loss"] for e in log),
            "params": params, "log": log}


def run_beam_first(d_model, n_layers=3, n_rounds=15, etch_batches=200,
                   beam_steps=500, batch_size=32, lr=0.003):
    """New protocol: train beams → etch plates (beam-first alternating).

    Round 0: beam training only (no etch — establish initial reading).
    Round 1+: beam training → etch with coherent gradients.
    """
    model = MiniHoloModel(d_model=d_model, n_layers=n_layers)
    mx.eval(model.parameters())
    params = count_plate_params(model)
    rng = np.random.RandomState(42)

    log = []
    for r in range(n_rounds):
        # Phase 1: train beams FIRST
        losses = train_beams(model, rng, n_steps=beam_steps,
                             batch_size=batch_size, lr=lr)

        # Phase 2: etch plates (now guided by trained beams)
        flips, flip_frac = etch_plates(model, rng, n_batches=etch_batches,
                                       batch_size=batch_size)

        ev = eval_model(model, np.random.RandomState(999))
        log.append({
            "round": r + 1, "flips": flips, "flip_frac": flip_frac,
            "beam_start": float(np.mean(losses[:10])),
            "beam_end": float(np.mean(losses[-10:])),
            **ev,
        })
        mx.clear_cache()

    return {"best_acc": max(e["accuracy"] for e in log),
            "best_loss": min(e["loss"] for e in log),
            "params": params, "log": log}


# ══════════════════════════════════════════════════════════════════════
# D-sweep orchestrator
# ══════════════════════════════════════════════════════════════════════

def run_d_sweep(d_values, n_layers=3, n_rounds=15, etch_batches=200,
                beam_steps=500, gd_steps=2000, batch_size=32, lr=0.003):
    """Run all five conditions at each d value."""

    all_results = {}

    for d in d_values:
        print(f"\n{'═' * 70}")
        print(f"  d = {d}")
        print(f"{'═' * 70}")

        # Quick param count
        test_model = MiniHoloModel(d_model=d, n_layers=n_layers)
        mx.eval(test_model.parameters())
        params = count_plate_params(test_model)
        plate_beam_ratio = params["plate_positions"] / max(
            params["beam_params"] + params["embed_params"], 1
        )
        print(f"  Plates: {params['plate_positions']:,}  "
              f"Continuous: {params['beam_params'] + params['embed_params']:,}  "
              f"Ratio: {plate_beam_ratio:.1f}:1")
        del test_model
        mx.clear_cache()

        d_results = {
            "d_model": d,
            "n_layers": n_layers,
            "plate_positions": params["plate_positions"],
            "beam_params": params["beam_params"],
            "embed_params": params["embed_params"],
            "plate_beam_ratio": plate_beam_ratio,
        }

        # 1. GD baseline
        print(f"\n  [1/5] GD baseline...", end="", flush=True)
        t0 = time.time()
        gd = run_gd(d, n_layers, n_steps=gd_steps, batch_size=batch_size,
                     lr=lr)
        print(f" acc={gd['best_acc']:.1%} ({time.time()-t0:.1f}s)")
        d_results["gd"] = gd

        # 2. Beam-only
        print(f"  [2/5] Beam-only...", end="", flush=True)
        t0 = time.time()
        beam = run_beam_only(d, n_layers, n_steps=gd_steps,
                             batch_size=batch_size, lr=lr)
        print(f" acc={beam['best_acc']:.1%} ({time.time()-t0:.1f}s)")
        d_results["beam_only"] = beam

        # 3. Plate-only
        print(f"  [3/5] Plate-only...", end="", flush=True)
        t0 = time.time()
        plate = run_plate_only(d, n_layers, n_rounds=n_rounds,
                               etch_batches=etch_batches,
                               batch_size=batch_size)
        print(f" acc={plate['best_acc']:.1%} ({time.time()-t0:.1f}s)")
        d_results["plate_only"] = plate

        # 4. Etch-first alternating (original)
        print(f"  [4/5] Etch-first alternating...", end="", flush=True)
        t0 = time.time()
        etch_first = run_etch_first(d, n_layers, n_rounds=n_rounds,
                                    etch_batches=etch_batches,
                                    beam_steps=beam_steps,
                                    batch_size=batch_size, lr=lr)
        print(f" acc={etch_first['best_acc']:.1%} ({time.time()-t0:.1f}s)")
        d_results["etch_first"] = etch_first

        # 5. Beam-first alternating (new)
        print(f"  [5/5] Beam-first alternating...", end="", flush=True)
        t0 = time.time()
        beam_first = run_beam_first(d, n_layers, n_rounds=n_rounds,
                                    etch_batches=etch_batches,
                                    beam_steps=beam_steps,
                                    batch_size=batch_size, lr=lr)
        print(f" acc={beam_first['best_acc']:.1%} ({time.time()-t0:.1f}s)")
        d_results["beam_first"] = beam_first

        # Summary for this d
        gap = gd["best_acc"] - beam["best_acc"]
        bf_vs_ef = beam_first["best_acc"] - etch_first["best_acc"]
        print(f"\n  d={d} summary:")
        print(f"    GD:          {gd['best_acc']:.1%}")
        print(f"    Beam-only:   {beam['best_acc']:.1%}  "
              f"(gap: {gap:+.1%})")
        print(f"    Plate-only:  {plate['best_acc']:.1%}")
        print(f"    Etch-first:  {etch_first['best_acc']:.1%}")
        print(f"    Beam-first:  {beam_first['best_acc']:.1%}  "
              f"(vs etch-first: {bf_vs_ef:+.1%})")

        # Flip trajectory (from beam-first log)
        flip_fracs = [e["flip_frac"] for e in beam_first["log"]]
        print(f"    Flip trajectory (beam-first): "
              f"{' → '.join(f'{f:.0%}' for f in flip_fracs[:5])}"
              f"{'...' if len(flip_fracs) > 5 else ''}")

        d_results["summary"] = {
            "gd_acc": gd["best_acc"],
            "beam_only_acc": beam["best_acc"],
            "plate_only_acc": plate["best_acc"],
            "etch_first_acc": etch_first["best_acc"],
            "beam_first_acc": beam_first["best_acc"],
            "gap_gd_vs_beam": gap,
            "beam_first_vs_etch_first": bf_vs_ef,
            "flip_trajectory_beam_first": flip_fracs,
            "flip_trajectory_etch_first": [
                e["flip_frac"] for e in etch_first["log"]
            ],
        }

        all_results[str(d)] = d_results
        mx.clear_cache()

    return all_results


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    output_dir = Path("checkpoints/mini-holo-d-sweep")
    output_dir.mkdir(parents=True, exist_ok=True)

    d_values = [48, 96, 128, 192, 256]

    print("=" * 70)
    print("  D-SWEEP MICROSCOPE: Finding the Plate/Beam Crossover")
    print(f"  d values: {d_values}")
    print(f"  Task: combinator reduction (K, I, B, C)")
    print(f"  Conditions: GD, beam-only, plate-only, etch-first, beam-first")
    print("=" * 70)

    t_start = time.time()
    results = run_d_sweep(d_values)
    t_total = time.time() - t_start

    # ── Grand summary ─────────────────────────────────────────
    print(f"\n{'═' * 70}")
    print(f"  GRAND SUMMARY — D-Sweep Crossover Analysis")
    print(f"{'═' * 70}")
    print(f"  {'d':>5}  {'Ratio':>6}  {'GD':>7}  {'Beam':>7}  "
          f"{'Gap':>7}  {'Plate':>7}  {'EtchF':>7}  {'BeamF':>7}  "
          f"{'BF-EF':>7}")
    print(f"  {'─'*5}  {'─'*6}  {'─'*7}  {'─'*7}  {'─'*7}  "
          f"{'─'*7}  {'─'*7}  {'─'*7}  {'─'*7}")

    for d in d_values:
        s = results[str(d)]["summary"]
        r = results[str(d)]["plate_beam_ratio"]
        marker = ""
        if s["gap_gd_vs_beam"] > 0.02:
            marker = " ← CROSSOVER"
        print(f"  {d:>5}  {r:>5.1f}×  {s['gd_acc']:>6.1%}  "
              f"{s['beam_only_acc']:>6.1%}  {s['gap_gd_vs_beam']:>+6.1%}  "
              f"{s['plate_only_acc']:>6.1%}  {s['etch_first_acc']:>6.1%}  "
              f"{s['beam_first_acc']:>6.1%}  "
              f"{s['beam_first_vs_etch_first']:>+6.1%}{marker}")

    print(f"\n  Total time: {t_total:.0f}s ({t_total/60:.1f}m)")

    # Save
    # Strip log arrays for the summary file (they're large)
    summary_results = {}
    for d_key, d_data in results.items():
        summary_results[d_key] = {
            "d_model": d_data["d_model"],
            "plate_positions": d_data["plate_positions"],
            "beam_params": d_data["beam_params"],
            "embed_params": d_data["embed_params"],
            "plate_beam_ratio": d_data["plate_beam_ratio"],
            "summary": d_data["summary"],
        }

    with open(output_dir / "summary.json", "w") as f:
        json.dump(summary_results, f, indent=2)

    with open(output_dir / "full_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n  Summary: {output_dir}/summary.json")
    print(f"  Full:    {output_dir}/full_results.json")


if __name__ == "__main__":
    main()
