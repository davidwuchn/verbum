"""
v14 Student Progressive Collapse + Stride Attention Distance Prior.

Two questions:
  1. Does the v14 student inherit the 2D computation core from the teacher?
  2. Does the distance prior (α=1.18) dominate stride attention at W=8?

Usage:
  uv run python scripts/v14/probe_collapse.py --checkpoint checkpoints/v14-td/step_001500_folded

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import mlx.core as mx
import mlx.nn as nn

sys.path.insert(0, str(Path(__file__).parent))

from config import V14Config
from data import ShardedDataLoader
from model import V14Model
from ternary import restore_ternary, freeze_ternary_weights
from td import convert_to_delta, collect_delta_params, freeze_delta_architecture


# ══════════════════════════════════════════════════════════════════════
# Dimensionality analysis
# ══════════════════════════════════════════════════════════════════════

def measure_dimensionality(x_np: np.ndarray, label: str) -> dict:
    """Measure effective dimensionality of a (B, L, D) tensor."""
    flat = x_np.reshape(-1, x_np.shape[-1])  # (B*L, D)

    # Skip position 0 (potential attention sink)
    if flat.shape[0] > 3:
        flat = flat[1:]

    centered = flat - flat.mean(axis=0)
    n, d = centered.shape

    # Truncated SVD (top 256)
    k = min(256, n, d)
    try:
        _, S, _ = np.linalg.svd(centered, full_matrices=False)
        S = S[:k]
    except np.linalg.LinAlgError:
        S = np.ones(k)

    energy = S ** 2
    total = energy.sum()
    fracs = energy / (total + 1e-10)
    cumulative = np.cumsum(fracs)

    rank_80 = int(np.searchsorted(cumulative, 0.80)) + 1
    rank_90 = int(np.searchsorted(cumulative, 0.90)) + 1
    rank_95 = int(np.searchsorted(cumulative, 0.95)) + 1

    # Participation ratio
    pr = (fracs.sum() ** 2) / (np.sum(fracs ** 2) + 1e-10)

    # Top SV fractions
    sv1 = float(fracs[0])
    sv12 = float(fracs[:2].sum())
    sv5 = float(fracs[:5].sum())

    # Norm stats
    norms = np.linalg.norm(flat, axis=1)

    result = {
        "stage": label,
        "rank_80": rank_80,
        "rank_90": rank_90,
        "rank_95": rank_95,
        "participation_ratio": float(pr),
        "sv1_frac": sv1,
        "sv12_frac": sv12,
        "sv5_frac": sv5,
        "mean_norm": float(norms.mean()),
        "norm_cv": float(norms.std() / (norms.mean() + 1e-10)),
    }
    return result


# ══════════════════════════════════════════════════════════════════════
# Model loading (from eval_ppl.py)
# ══════════════════════════════════════════════════════════════════════

def load_model(ckpt_path: Path, cfg: V14Config) -> V14Model:
    """Load v14 model from checkpoint."""
    model = V14Model(cfg)

    # Base plates
    base_path = Path(cfg.extracted_model_path).resolve()
    if base_path.exists():
        model.load_weights(str(base_path), strict=False)
        mx.eval(model.parameters())
        restore_ternary(model)
        freeze_ternary_weights(model)
        print(f"  Base plates: {base_path}")

    # Delta architecture
    convert_to_delta(model, include_prefixes=("shared_stride_stack",))
    freeze_delta_architecture(model)

    # Checkpoint weights
    model_path = ckpt_path / "model.npz"
    if model_path.exists():
        model.load_weights(str(model_path), strict=False)
        mx.eval(model.parameters())
        restore_ternary(model)
        freeze_ternary_weights(model)
        print(f"  Checkpoint: {model_path}")

    # Delta plates
    delta_path = ckpt_path / "delta_plates.npz"
    if delta_path.exists():
        from ternary import pack_ternary_mlx
        delta_data = dict(np.load(str(delta_path), allow_pickle=False))
        delta_modules = collect_delta_params(model)
        n_loaded = 0
        for path, dtl in delta_modules:
            delta_key = path.replace(".", "_")
            packed_key = f"{delta_key}_delta_packed"
            old_key = f"{delta_key}_delta"
            if packed_key in delta_data:
                dtl.delta_weight = mx.array(delta_data[packed_key])
                mx.eval(dtl.delta_weight)
                n_loaded += 1
            elif old_key in delta_data:
                delta_int8 = mx.array(delta_data[old_key].astype(np.int8))
                dtl.delta_weight = pack_ternary_mlx(delta_int8)
                mx.eval(dtl.delta_weight)
                n_loaded += 1
        print(f"  Delta plates: {n_loaded}/{len(delta_modules)}")

    # State
    state_path = ckpt_path / "state.json"
    if state_path.exists():
        state = json.loads(state_path.read_text())
        s5 = state.get("s5_identity_state")
        if s5 is not None:
            model.s5_identity.identity_state = mx.array(s5)
        ema = state.get("crystal_ema")
        if ema is not None:
            model._crystal_ema = mx.array(float(ema))

    return model


# ══════════════════════════════════════════════════════════════════════
# Patched forward to capture intermediates
# ══════════════════════════════════════════════════════════════════════

def forward_with_capture(model: V14Model, tokens: mx.array) -> dict:
    """Run forward pass, capturing residual stream at stack boundaries."""
    B, L = tokens.shape
    cfg = model.cfg

    # Embed
    positions = mx.arange(L)
    x = model.embed_norm(model.embed(tokens) + model.pos_embed(positions))
    mx.eval(x)
    x_embed = np.array(x)

    # Stack A
    x_a_out, _, _, _ = model.stack_a(x)
    mx.eval(x_a_out)
    x_a_np = np.array(x_a_out)

    # Stack B
    x_b_out, _, _, _ = model.stack_b(x_a_out)
    mx.eval(x_b_out)
    x_b_np = np.array(x_b_out)

    # Stack C
    x_c_out, _, _, _ = model.stack_c(x_b_out)
    mx.eval(x_c_out)
    x_c_np = np.array(x_c_out)

    # Output norm
    x_out = model.output_norm(x_c_out)
    mx.eval(x_out)
    x_out_np = np.array(x_out)

    return {
        "embed": x_embed,
        "stack_a": x_a_np,
        "stack_b": x_b_np,
        "stack_c": x_c_np,
        "output": x_out_np,
    }


# ══════════════════════════════════════════════════════════════════════
# Distance prior analysis for stride attention
# ══════════════════════════════════════════════════════════════════════

def analyze_distance_prior(cfg: V14Config, alpha: float = 1.18) -> dict:
    """Compute the precomputed attention profiles and their properties."""
    results = {"strides": []}

    for s_idx, stride in enumerate(cfg.strides):
        W = cfg.window

        # Distance prior for this stride
        weights = np.array([1.0 / ((stride * w + 1) ** alpha) for w in range(W)])

        # Normalize (softmax-like)
        weights_norm = weights / weights.sum()

        # Entropy of the distribution
        entropy = -np.sum(weights_norm * np.log(weights_norm + 1e-10))
        max_entropy = np.log(W)
        entropy_ratio = entropy / max_entropy

        # Effective positions (how many positions have meaningful weight?)
        eff_pos = np.exp(entropy)

        # Self-attention fraction (position 0)
        self_frac = float(weights_norm[0])

        results["strides"].append({
            "stride": stride,
            "stride_idx": s_idx,
            "weights": weights_norm.tolist(),
            "entropy": float(entropy),
            "entropy_ratio": float(entropy_ratio),
            "effective_positions": float(eff_pos),
            "self_attention_frac": self_frac,
        })

    return results


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--n-batches", type=int, default=5)
    args = parser.parse_args()

    ckpt_path = Path(args.checkpoint).resolve()
    cfg = V14Config()

    print(f"\n{'='*70}")
    print(f"  v14 Progressive Collapse + Distance Prior Probe")
    print(f"  Checkpoint: {ckpt_path}")
    print(f"{'='*70}\n")

    # ── Load model ──
    model = load_model(ckpt_path, cfg)

    # ── Load data ──
    eval_loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=1,
        seq_len=cfg.seq_len,
        shard_start=54,
        shard_end=60,
    )

    # ══════════════════════════════════════════════════════════
    # Part 1: Progressive collapse at stack boundaries
    # ══════════════════════════════════════════════════════════

    print(f"\n{'='*70}")
    print(f"  PART 1: Progressive Collapse at Stack Boundaries")
    print(f"{'='*70}")

    all_measurements = []

    for batch_idx in range(args.n_batches):
        batch = eval_loader.next_batch()
        if batch is None:
            break

        input_ids_np, _ = batch
        input_ids = mx.array(input_ids_np)

        print(f"\n  Batch {batch_idx+1}/{args.n_batches} (seq_len={input_ids.shape[1]})")

        captures = forward_with_capture(model, input_ids)

        measurements = {}
        for stage_name, x_np in captures.items():
            m = measure_dimensionality(x_np, stage_name)
            measurements[stage_name] = m
            print(f"    {stage_name:<10} rank90={m['rank_90']:<4} "
                  f"PR={m['participation_ratio']:<6.1f} "
                  f"σ₁={m['sv1_frac']:.1%}  σ1-2={m['sv12_frac']:.1%}  "
                  f"‖h‖={m['mean_norm']:.1f}  CV={m['norm_cv']:.3f}")

        all_measurements.append(measurements)

    # Average
    print(f"\n{'─'*70}")
    print(f"  AVERAGED over {len(all_measurements)} batches:")
    print(f"{'─'*70}")

    stages = ["embed", "stack_a", "stack_b", "stack_c", "output"]
    averaged = {}
    for stage in stages:
        keys = ["rank_80", "rank_90", "rank_95", "participation_ratio",
                "sv1_frac", "sv12_frac", "sv5_frac", "mean_norm", "norm_cv"]
        avg = {}
        for k in keys:
            vals = [m[stage][k] for m in all_measurements]
            avg[k] = float(np.mean(vals))
        averaged[stage] = avg

        print(f"  {stage:<10} rank90={avg['rank_90']:<6.1f} "
              f"PR={avg['participation_ratio']:<6.1f} "
              f"σ₁={avg['sv1_frac']:.1%}  σ1-2={avg['sv12_frac']:.1%}  "
              f"‖h‖={avg['mean_norm']:.1f}")

    # Collapse trajectory
    prs = [averaged[s]["participation_ratio"] for s in stages]
    ranks = [averaged[s]["rank_90"] for s in stages]
    sv1s = [averaged[s]["sv1_frac"] for s in stages]

    print(f"\n  Trajectory:")
    print(f"    PR:      {' → '.join(f'{p:.1f}' for p in prs)}")
    print(f"    Rank90:  {' → '.join(f'{r:.0f}' for r in ranks)}")
    print(f"    σ₁:      {' → '.join(f'{s:.1%}' for s in sv1s)}")

    compress_ratio = prs[0] / (min(prs) + 1e-10)
    print(f"\n    Compression ratio: {compress_ratio:.1f}× (embed PR / min PR)")

    if prs[1] < prs[0] and prs[2] < prs[0]:
        print(f"    ★ Stack A+B COMPRESS (PR decreases)")
    if prs[3] > prs[2]:
        print(f"    ★ Stack C EXPANDS (PR increases)")

    # ══════════════════════════════════════════════════════════
    # Part 2: Distance Prior at W=8
    # ══════════════════════════════════════════════════════════

    print(f"\n\n{'='*70}")
    print(f"  PART 2: Distance Prior for Stride Attention (α=1.18, W=8)")
    print(f"{'='*70}")

    dp = analyze_distance_prior(cfg, alpha=1.18)

    print(f"\n  {'Stride':<8} {'Self%':<8} {'EffPos':<8} {'Entropy':<10} {'Profile (normalized)'}")
    print(f"  {'─'*80}")

    for s in dp["strides"]:
        profile = " ".join(f"{w:.3f}" for w in s["weights"][:8])
        print(f"  s{s['stride']:<7} {s['self_attention_frac']:.1%}   "
              f"{s['effective_positions']:.1f}     "
              f"{s['entropy_ratio']:.2f}       [{profile}]")

    # Summary
    low_strides = [s for s in dp["strides"] if s["stride"] <= 8]
    mid_strides = [s for s in dp["strides"] if 16 <= s["stride"] <= 512]
    high_strides = [s for s in dp["strides"] if s["stride"] >= 1024]

    avg_eff_low = np.mean([s["effective_positions"] for s in low_strides])
    avg_eff_mid = np.mean([s["effective_positions"] for s in mid_strides])
    avg_eff_high = np.mean([s["effective_positions"] for s in high_strides])

    print(f"\n  Summary:")
    print(f"    Low strides (s1-s8):       {avg_eff_low:.1f} effective positions (content can modulate)")
    print(f"    Mid strides (s16-s512):    {avg_eff_mid:.1f} effective positions (prior dominates)")
    print(f"    High strides (s1024+):     {avg_eff_high:.1f} effective positions (almost self-only)")

    pct_prior_dominated = sum(1 for s in dp["strides"] if s["effective_positions"] < 3) / len(dp["strides"])
    print(f"\n    Strides where prior dominates (<3 eff positions): {pct_prior_dominated:.0%}")

    # ── Save results ──
    out_dir = Path("results/v14-collapse-probe")
    out_dir.mkdir(parents=True, exist_ok=True)

    def clean(obj):
        if isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: clean(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [clean(v) for v in obj]
        return obj

    output = {
        "checkpoint": str(ckpt_path),
        "n_batches": len(all_measurements),
        "averaged_collapse": clean(averaged),
        "distance_prior": clean(dp),
        "trajectory": {
            "stages": stages,
            "pr": prs,
            "rank90": ranks,
            "sv1": sv1s,
        },
    }

    with open(out_dir / "results.json", "w") as f:
        json.dump(clean(output), f, indent=2)

    print(f"\n  Results saved to {out_dir}/results.json")
    print()


if __name__ == "__main__":
    main()
