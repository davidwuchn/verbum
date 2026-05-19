"""Mini Holographic Microscope — Oracle Crystal Write.

Tests the seed crystal hypothesis: can we write the correct plate
topology in one shot, freeze, and let GD on continuous params recover
the model's performance?

Protocol:
  1. Train a GD model to convergence → the "oracle"
  2. Extract sign(W) from oracle attention K/V/O + FFN → the "crystal"
  3. Write crystal into HoloModel plates → one-shot crystal write
  4. Freeze plates, GD on continuous params only

Conditions:
  - GD baseline (no ternary, the ceiling)
  - Oracle crystal + freeze + GD (perfect crystal from converged model)
  - Noisy crystal at 10%, 20%, 50% flip rate (how much noise tolerable?)
  - Random plates + freeze + GD (beam-only baseline)
  - Iterative etch (round 5) + freeze + GD (prior experiment's best)

The noisy crystal test is critical: the Procrustes-translated crystal
from a teacher model won't be exact. We need to know the tolerance.

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

from mini_holo_d_sweep_v2 import (
    VOCAB_SIZE, PAD_ID, EQ_ID, TOK2ID, ID2TOK,
    TernaryLinear,
    CausalSelfAttention, GDLayer, GDModel,
    TernaryCausalAttention, HoloBeamLayer, HoloModel,
    count_holo_params, _get_plates,
    holo_plate_fingerprint, holo_plate_diff,
    masked_ce_loss, eval_model, eval_by_depth,
    generate_batch, generate_example,
    etch_plates, train_beams, _zero_plate_grads,
)


# ══════════════════════════════════════════════════════════════════════
# Oracle extraction — get the crystal from a trained GD model
# ══════════════════════════════════════════════════════════════════════

def extract_crystal(gd_model: GDModel) -> list[dict[str, np.ndarray]]:
    """Extract sign topology from a trained GD model's attention layers.

    For each GD layer, extract sign(W) for K, V, O projections and FFN.
    These become the ternary plate values for the HoloModel.

    Returns list of dicts, one per layer:
      {"k": sign(W_k), "v": sign(W_v), "o": sign(W_o), "ffn": sign(W_ffn)}
    """
    crystal = []
    for layer in gd_model.layers:
        layer_signs = {
            "k": np.sign(np.array(layer.attn.k_proj.weight)),
            "v": np.sign(np.array(layer.attn.v_proj.weight)),
            "o": np.sign(np.array(layer.attn.o_proj.weight)),
            "ffn": np.sign(np.array(layer.ffn.weight)),
        }
        # Replace zeros with random ±1 (ternary plates shouldn't have zeros
        # from continuous weights — sign(0) = 0 is degenerate)
        for key in layer_signs:
            zeros = layer_signs[key] == 0
            if zeros.any():
                rng = np.random.RandomState(42)
                layer_signs[key][zeros] = rng.choice([-1.0, 1.0],
                                                      size=int(zeros.sum()))
        crystal.append(layer_signs)
    return crystal


def add_noise_to_crystal(
    crystal: list[dict[str, np.ndarray]],
    flip_fraction: float,
    rng: np.random.RandomState,
) -> list[dict[str, np.ndarray]]:
    """Randomly flip a fraction of signs in the crystal."""
    noisy = []
    for layer_signs in crystal:
        noisy_layer = {}
        for key, signs in layer_signs.items():
            mask = rng.random(signs.shape) < flip_fraction
            flipped = signs.copy()
            flipped[mask] *= -1
            noisy_layer[key] = flipped
        noisy.append(noisy_layer)
    return noisy


def write_crystal_to_model(
    model: HoloModel,
    crystal: list[dict[str, np.ndarray]],
):
    """Write crystal signs into HoloModel's ternary plates."""
    for i, layer in enumerate(model.layers):
        layer.attn.k_plate.weight = mx.array(crystal[i]["k"].astype(np.float32))
        layer.attn.v_plate.weight = mx.array(crystal[i]["v"].astype(np.float32))
        layer.attn.o_plate.weight = mx.array(crystal[i]["o"].astype(np.float32))
        layer.ffn_plate.weight = mx.array(crystal[i]["ffn"].astype(np.float32))
    mx.eval(model.parameters())


def crystal_similarity(crystal_a, crystal_b) -> float:
    """Fraction of matching signs between two crystals."""
    total = 0
    matching = 0
    for la, lb in zip(crystal_a, crystal_b):
        for key in la:
            a = la[key].flatten()
            b = lb[key].flatten()
            total += len(a)
            matching += int((a == b).sum())
    return matching / total if total > 0 else 0


# ══════════════════════════════════════════════════════════════════════
# Experiment runners
# ══════════════════════════════════════════════════════════════════════

def train_gd_oracle(
    d_model: int = 48,
    n_layers: int = 3,
    n_steps: int = 10500,
    batch_size: int = 32,
    lr: float = 0.003,
    max_depth: int = 4,
) -> tuple[GDModel, list[dict]]:
    """Train a full GD model to convergence. This is the oracle."""
    model = GDModel(d_model=d_model, n_layers=n_layers)
    mx.eval(model.parameters())

    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
    rng = np.random.RandomState(42)

    log = []
    for step in range(n_steps):
        input_ids, targets, mask = generate_batch(
            batch_size, rng, max_depth=max_depth)
        loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        model.update(optimizer.apply_gradients(grads, model))
        mx.eval(model.parameters())
        del loss_val, grads, input_ids, targets, mask
        if (step + 1) % 50 == 0:
            mx.clear_cache()
        if (step + 1) % 1000 == 0:
            ev = eval_model(model, np.random.RandomState(999),
                            max_depth=max_depth)
            log.append({"step": step + 1, **ev})
            print(f"    Oracle step {step+1:5d}: "
                  f"acc={ev['accuracy']:.1%} loss={ev['loss']:.4f}")

    return model, log


def run_crystal_gd(
    crystal: list[dict[str, np.ndarray]],
    label: str,
    d_model: int = 48,
    n_layers: int = 3,
    n_steps: int = 10500,
    batch_size: int = 32,
    lr: float = 0.003,
    max_depth: int = 4,
) -> dict:
    """Write crystal into HoloModel, freeze, train beams only."""
    model = HoloModel(d_model=d_model, n_layers=n_layers)
    mx.eval(model.parameters())

    # Write crystal
    write_crystal_to_model(model, crystal)

    # Freeze plates
    for layer in model.layers:
        layer.attn.k_plate.freeze()
        layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze()
        layer.ffn_plate.freeze()

    # Train continuous params only
    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
    rng = np.random.RandomState(42)

    log = []
    for step in range(n_steps):
        input_ids, targets, mask = generate_batch(
            batch_size, rng, max_depth=max_depth)
        loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        model.update(optimizer.apply_gradients(grads, model))
        mx.eval(model.parameters())
        del loss_val, grads, input_ids, targets, mask
        if (step + 1) % 50 == 0:
            mx.clear_cache()
        if (step + 1) % 1000 == 0:
            ev = eval_model(model, np.random.RandomState(999),
                            max_depth=max_depth)
            log.append({"step": step + 1, **ev})

    final = eval_model(model, np.random.RandomState(999), max_depth=max_depth)
    log.append({"step": n_steps, **final})
    depth = eval_by_depth(model, np.random.RandomState(999),
                          max_depth=max_depth)

    return {
        "label": label,
        "best_acc": max(e["accuracy"] for e in log),
        "best_loss": min(e["loss"] for e in log),
        "final_acc": final["accuracy"],
        "final_depth": depth,
        "log": log,
    }


def run_etch_then_freeze_gd(
    d_model: int = 48,
    n_layers: int = 3,
    n_etch_rounds: int = 5,
    etch_batches: int = 200,
    beam_steps_per_round: int = 500,
    post_freeze_steps: int = 7000,
    batch_size: int = 32,
    lr: float = 0.003,
    max_depth: int = 4,
) -> dict:
    """Iterative etch for N rounds, freeze, then extended GD."""
    model = HoloModel(d_model=d_model, n_layers=n_layers)
    mx.eval(model.parameters())
    rng = np.random.RandomState(42)

    # Etch phase
    etch_log = []
    for r in range(n_etch_rounds):
        flips, flip_frac = etch_plates(model, rng, n_batches=etch_batches,
                                       batch_size=batch_size,
                                       max_depth=max_depth)
        losses = train_beams(model, rng, n_steps=beam_steps_per_round,
                             batch_size=batch_size, lr=lr,
                             max_depth=max_depth)
        ev = eval_model(model, np.random.RandomState(999),
                        max_depth=max_depth)
        etch_log.append({
            "round": r + 1, "flips": flips, "flip_frac": flip_frac, **ev,
        })
        mx.clear_cache()

    # Extract what the etch produced (for comparison)
    etched_crystal = holo_plate_fingerprint(model)

    # Freeze
    for layer in model.layers:
        layer.attn.k_plate.freeze()
        layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze()
        layer.ffn_plate.freeze()

    # GD phase
    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
    gd_log = []
    for step in range(post_freeze_steps):
        input_ids, targets, mask = generate_batch(
            batch_size, rng, max_depth=max_depth)
        loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        model.update(optimizer.apply_gradients(grads, model))
        mx.eval(model.parameters())
        del loss_val, grads, input_ids, targets, mask
        if (step + 1) % 50 == 0:
            mx.clear_cache()
        if (step + 1) % 1000 == 0:
            ev = eval_model(model, np.random.RandomState(999),
                            max_depth=max_depth)
            gd_log.append({"step": step + 1, **ev})

    final = eval_model(model, np.random.RandomState(999), max_depth=max_depth)
    depth = eval_by_depth(model, np.random.RandomState(999),
                          max_depth=max_depth)

    return {
        "label": f"etch_r{n_etch_rounds}+freeze+GD",
        "best_acc": max(
            max((e["accuracy"] for e in etch_log), default=0),
            max((e["accuracy"] for e in gd_log), default=0),
            final["accuracy"],
        ),
        "final_acc": final["accuracy"],
        "final_depth": depth,
        "etch_log": etch_log,
        "gd_log": gd_log,
        "etched_crystal": etched_crystal,
    }


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    output_dir = Path("checkpoints/mini-holo-crystal")
    output_dir.mkdir(parents=True, exist_ok=True)

    d_model = 48
    n_layers = 3
    max_depth = 4
    gd_steps = 10500
    batch_size = 32
    lr = 0.003

    noise_levels = [0.0, 0.05, 0.10, 0.20, 0.30, 0.50]

    print("=" * 70)
    print("  ORACLE CRYSTAL WRITE EXPERIMENT")
    print(f"  d={d_model}, layers={n_layers}, max_depth={max_depth}")
    print(f"  GD budget: {gd_steps} steps")
    print(f"  Noise levels: {noise_levels}")
    print("=" * 70)

    results = {}

    # ── 1. Train oracle ───────────────────────────────────────
    print(f"\n  [1] Training GD oracle ({gd_steps} steps)...")
    t0 = time.time()
    oracle_model, oracle_log = train_gd_oracle(
        d_model, n_layers, n_steps=gd_steps,
        batch_size=batch_size, lr=lr, max_depth=max_depth,
    )
    oracle_eval = eval_model(oracle_model, np.random.RandomState(999),
                             max_depth=max_depth)
    oracle_depth = eval_by_depth(oracle_model, np.random.RandomState(999),
                                 max_depth=max_depth)
    dt = time.time() - t0
    print(f"    Oracle final: acc={oracle_eval['accuracy']:.1%} "
          f"loss={oracle_eval['loss']:.4f} ({dt:.1f}s)")

    results["oracle"] = {
        "acc": oracle_eval["accuracy"],
        "loss": oracle_eval["loss"],
        "depth": oracle_depth,
        "log": oracle_log,
    }

    # ── 2. Extract crystal ────────────────────────────────────
    crystal = extract_crystal(oracle_model)
    print(f"\n  Crystal extracted from oracle.")

    # Count total plate positions
    total_signs = sum(
        s.size for layer_signs in crystal for s in layer_signs.values()
    )
    print(f"  Total plate positions: {total_signs:,}")

    # ── 3. Crystal + freeze + GD at various noise levels ──────
    n_conditions = len(noise_levels) + 2  # + random + etch
    for i, noise in enumerate(noise_levels):
        label = f"crystal_noise_{int(noise*100)}pct"
        if noise == 0:
            label = "oracle_crystal"
            noisy_crystal = crystal
        else:
            noisy_crystal = add_noise_to_crystal(
                crystal, noise, np.random.RandomState(int(noise * 1000) + 7))

        # Measure similarity to oracle
        sim = crystal_similarity(crystal, noisy_crystal)

        print(f"\n  [{i+2}/{n_conditions+1}] {label} "
              f"(similarity={sim:.1%})...", end="", flush=True)
        t0 = time.time()
        r = run_crystal_gd(noisy_crystal, label, d_model, n_layers,
                           n_steps=gd_steps, batch_size=batch_size,
                           lr=lr, max_depth=max_depth)
        dt = time.time() - t0
        r["noise_fraction"] = noise
        r["similarity_to_oracle"] = sim
        print(f" best={r['best_acc']:.1%} ({dt:.1f}s)")
        results[label] = r

    # ── 4. Random plates baseline ─────────────────────────────
    print(f"\n  [{len(noise_levels)+2}/{n_conditions+1}] "
          f"Random plates + freeze + GD...", end="", flush=True)
    t0 = time.time()
    random_crystal = add_noise_to_crystal(
        crystal, 0.50, np.random.RandomState(999))
    # Actually make truly random: regenerate
    random_crystal_true = []
    rng_rc = np.random.RandomState(42)
    for layer_signs in crystal:
        layer_random = {}
        for key, signs in layer_signs.items():
            layer_random[key] = rng_rc.choice(
                [-1.0, 1.0], size=signs.shape).astype(np.float32)
        random_crystal_true.append(layer_random)

    r_random = run_crystal_gd(random_crystal_true, "random_plates",
                              d_model, n_layers, n_steps=gd_steps,
                              batch_size=batch_size, lr=lr,
                              max_depth=max_depth)
    dt = time.time() - t0
    r_random["noise_fraction"] = 1.0
    r_random["similarity_to_oracle"] = crystal_similarity(
        crystal, random_crystal_true)
    print(f" best={r_random['best_acc']:.1%} ({dt:.1f}s)")
    results["random_plates"] = r_random

    # ── 5. Iterative etch (round 5) + freeze + GD ─────────────
    print(f"\n  [{len(noise_levels)+3}/{n_conditions+1}] "
          f"Iterative etch (r5) + freeze + GD...", end="", flush=True)
    t0 = time.time()
    r_etch = run_etch_then_freeze_gd(
        d_model, n_layers,
        n_etch_rounds=5, etch_batches=200, beam_steps_per_round=500,
        post_freeze_steps=gd_steps,  # give same GD budget
        batch_size=batch_size, lr=lr, max_depth=max_depth,
    )
    dt = time.time() - t0

    # Compare etch crystal to oracle crystal
    etched_signs = r_etch["etched_crystal"]
    # Convert to same format as crystal for comparison
    etched_formatted = []
    idx = 0
    for layer_signs in crystal:
        layer_etched = {}
        for key in ["k", "v", "o", "ffn"]:
            layer_etched[key] = etched_signs[idx].astype(np.float32)
            idx += 1
        etched_formatted.append(layer_etched)

    etch_similarity = crystal_similarity(crystal, etched_formatted)
    r_etch["similarity_to_oracle"] = etch_similarity
    print(f" best={r_etch['best_acc']:.1%} "
          f"(etch↔oracle sim={etch_similarity:.1%}) ({dt:.1f}s)")
    results["etch_r5"] = r_etch

    # ── Summary ───────────────────────────────────────────────
    print(f"\n{'═' * 70}")
    print(f"  SUMMARY — Oracle Crystal Write")
    print(f"{'═' * 70}")

    print(f"\n  Oracle GD ceiling: {results['oracle']['acc']:.1%}")
    print()
    print(f"  {'Condition':>25}  {'Noise':>6}  {'Sim':>6}  "
          f"{'Best':>7}  {'vs Oracle':>10}  {'vs Random':>10}")
    print(f"  {'─'*25}  {'─'*6}  {'─'*6}  {'─'*7}  {'─'*10}  {'─'*10}")

    oracle_acc = results["oracle"]["acc"]
    random_acc = results["random_plates"]["best_acc"]

    for key in (
        ["oracle_crystal"]
        + [f"crystal_noise_{int(n*100)}pct" for n in noise_levels if n > 0]
        + ["random_plates", "etch_r5"]
    ):
        r = results[key]
        noise = r.get("noise_fraction", "?")
        sim = r.get("similarity_to_oracle", "?")
        best = r["best_acc"]
        vs_oracle = best - oracle_acc
        vs_random = best - random_acc

        noise_str = f"{noise:.0%}" if isinstance(noise, float) else noise
        sim_str = f"{sim:.1%}" if isinstance(sim, float) else sim

        print(f"  {r['label']:>25}  {noise_str:>6}  {sim_str:>6}  "
              f"{best:>6.1%}  {vs_oracle:>+9.1%}  {vs_random:>+9.1%}")

    # Depth breakdown for key conditions
    print(f"\n  Depth breakdown (exact sequence match):")
    print(f"  {'Condition':>25}  {'d1':>6}  {'d2':>6}  {'d3':>6}  {'d4':>6}")
    print(f"  {'─'*25}  {'─'*6}  {'─'*6}  {'─'*6}  {'─'*6}")

    for label, data in [
        ("Oracle GD", {"final_depth": results["oracle"]["depth"]}),
        ("Oracle crystal", results["oracle_crystal"]),
        ("10% noise", results.get("crystal_noise_10pct", {})),
        ("20% noise", results.get("crystal_noise_20pct", {})),
        ("50% noise", results.get("crystal_noise_50pct", {})),
        ("Random plates", results["random_plates"]),
        ("Etch r5", results["etch_r5"]),
    ]:
        fd = data.get("final_depth", {})
        vals = []
        for d in range(1, max_depth + 1):
            acc = fd.get(d, fd.get(str(d), {}))
            if isinstance(acc, dict):
                acc = acc.get("accuracy", 0)
            vals.append(acc if isinstance(acc, (int, float)) else 0)
        print(f"  {label:>25}  " + "  ".join(f"{v:>5.1%}" for v in vals))

    # Noise tolerance curve
    print(f"\n  Noise tolerance curve:")
    print(f"  {'Noise':>8}  {'Accuracy':>10}  {'% of Oracle':>12}")
    for noise in noise_levels:
        if noise == 0:
            key = "oracle_crystal"
        else:
            key = f"crystal_noise_{int(noise*100)}pct"
        r = results[key]
        pct = r["best_acc"] / oracle_acc * 100 if oracle_acc > 0 else 0
        print(f"  {noise:>7.0%}  {r['best_acc']:>9.1%}  {pct:>11.1f}%")

    # Random and etch for comparison
    pct_r = random_acc / oracle_acc * 100 if oracle_acc > 0 else 0
    pct_e = results["etch_r5"]["best_acc"] / oracle_acc * 100 if oracle_acc > 0 else 0
    print(f"  {'random':>7}  {random_acc:>9.1%}  {pct_r:>11.1f}%")
    print(f"  {'etch r5':>7}  {results['etch_r5']['best_acc']:>9.1%}  "
          f"{pct_e:>11.1f}%")

    # Save
    # Strip large arrays for JSON
    save_results = {}
    for k, v in results.items():
        if isinstance(v, dict):
            save_v = {kk: vv for kk, vv in v.items()
                      if kk != "etched_crystal"}
            save_results[k] = save_v
        else:
            save_results[k] = v

    with open(output_dir / "results.json", "w") as f:
        json.dump(save_results, f, indent=2, default=str)
    print(f"\n  Saved to {output_dir}/results.json")


if __name__ == "__main__":
    main()
