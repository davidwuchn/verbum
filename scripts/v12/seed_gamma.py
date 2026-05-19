#!/usr/bin/env python3
"""Gamma Seeding — Analytical beam initialization from teacher features.

The problem: after etching, gamma (per-row scale on TernaryLinear) is
uniform (~0.05). GD must discover from scratch which rows matter. This
causes the B-dominant shortcut: the steepest gradient direction routes
everything through B composition, starving K/I/C/D.

The fix: compute optimal gamma analytically from teacher features BEFORE
GD starts. For each TernaryLinear, measure how its plate responds to
teacher inputs, then set gamma so the module's output has the right
scale and direction to match the teacher's computation.

Two strategies:
  1. Variance calibration — normalize each row's contribution so no single
     row dominates. gamma_i = target_std / std(W[i,:] @ x)
  2. Matched filter — set gamma to maximize correlation with teacher output.
     gamma_i = cov(W[i,:] @ x, y_i) / var(W[i,:] @ x)

Strategy 1 is universal (works for every TernaryLinear).
Strategy 2 only works where we have per-module targets (pass I/O).

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/seed_gamma.py \\
        --weights checkpoints/v12-distill-run1/etch_round_005/weights.npz \\
        --projection checkpoints/v12-distill-run1/etch_round_005/projection.npz \\
        --output checkpoints/v12-distill-run1/gamma_seeded/weights.npz

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import numpy as np
from mlx.utils import tree_flatten

sys.path.insert(0, str(Path(__file__).parent))

from config import V12Config
from model import V12Model, create_model, count_parameters
from ternary import (
    freeze_ternary_weights,
    restore_ternary,
    unpack_ternary_mlx,
    TernaryLinear,
)


# ══════════════════════════════════════════════════════════════════════
# Teacher features + projection (reuse from holographic_distill_v12)
# ══════════════════════════════════════════════════════════════════════

TEACHER_DEPTHS = [8, 16, 24, 32, 40, 48, 56, 64]


def load_teacher_features(feature_dir: str, depth_idx: int, n_probes: int = 500):
    """Load teacher input/output arrays for a depth, return as numpy."""
    feature_dir = Path(feature_dir)
    layer = TEACHER_DEPTHS[depth_idx]
    inp_npz = np.load(str(feature_dir / f"layer_{layer:03d}_inputs.npz"))
    out_npz = np.load(str(feature_dir / f"layer_{layer:03d}_outputs.npz"))

    inputs = []
    outputs = []
    for i in range(n_probes):
        k_in = f"inp_{i}"
        k_out = f"out_{i}"
        if k_in in inp_npz and k_out in out_npz:
            inputs.append(inp_npz[k_in])     # (T_i, 5120)
            outputs.append(out_npz[k_out])    # (T_i, 5120)
    return inputs, outputs


class TeacherProjection(nn.Module):
    """Mirrors the projection from holographic_distill_v12.py."""
    def __init__(self, d_teacher: int = 5120, d_student: int = 512):
        import math
        super().__init__()
        self.proj = nn.Linear(d_teacher, d_student, bias=False)
        self.norm = nn.RMSNorm(d_student)
        scale = math.sqrt(2.0 / (d_teacher + d_student))
        self.proj.weight = mx.random.normal(shape=(d_student, d_teacher)) * scale

    def __call__(self, x: mx.array) -> mx.array:
        return self.norm(self.proj(x))


# ══════════════════════════════════════════════════════════════════════
# Gamma seeding strategies
# ══════════════════════════════════════════════════════════════════════

def collect_module_input_stats(
    model: V12Model,
    projection: TeacherProjection,
    teacher_inputs: list[np.ndarray],
    n_probes: int = 100,
) -> dict[str, np.ndarray]:
    """Forward projected teacher inputs through the model and collect
    the cached _x_mean at each TernaryLinear.

    Returns dict[module_path] → stacked input means (n_probes, in_features).
    """
    stats = {}
    cfg = model.cfg

    for pi in range(min(n_probes, len(teacher_inputs))):
        t_in = mx.array(teacher_inputs[pi])   # (T, 5120)
        proj_in = projection(t_in)             # (T, d_model)
        tokens_dummy = mx.zeros((1, proj_in.shape[0]), dtype=mx.int32)

        # We can't easily inject proj_in as the embedding output
        # in a full forward pass. Instead, just run a normal forward
        # with dummy tokens — this populates _x_mean on all TernaryLinear
        # modules with the actual input statistics for this sequence.
        #
        # The values will be from the dummy forward, not from teacher
        # features. But we don't need teacher-matched stats — we just
        # need the plate response statistics for WHATEVER input the
        # model currently produces.
        try:
            model.forward(tokens_dummy, targets=None)
        except Exception:
            # Some dummy tokens may cause issues with short seqs
            # Pad to minimum viable length
            min_len = max(cfg.strides) + cfg.window + 2
            if tokens_dummy.shape[1] < min_len:
                pad = mx.zeros((1, min_len - tokens_dummy.shape[1]), dtype=mx.int32)
                tokens_dummy = mx.concatenate([tokens_dummy, pad], axis=1)
                model.forward(tokens_dummy, targets=None)

        mx.eval(model.parameters())

        # Collect _x_mean from each TernaryLinear
        for name, mod in model.named_modules():
            if isinstance(mod, TernaryLinear) and hasattr(mod, '_x_mean'):
                xm = np.array(mod._x_mean)  # (in_features,)
                if name not in stats:
                    stats[name] = []
                stats[name].append(xm)

        if (pi + 1) % 25 == 0:
            mx.clear_cache()

    # Stack into arrays
    return {name: np.stack(vals) for name, vals in stats.items()}


def seed_gamma_variance(
    model: V12Model,
    target_output_std: float = 1.0,
) -> dict[str, dict]:
    """Strategy 1: Variance calibration.

    For each TernaryLinear, compute the raw plate response variance per row,
    then set gamma so output std = target_output_std.

    gamma_i = target_std / (std(W[i,:] @ x) + eps)

    Uses the cached _x_mean from recent forward passes. If not available,
    computes from random inputs.
    """
    log = {}

    for name, mod in model.named_modules():
        if not isinstance(mod, TernaryLinear):
            continue

        W = np.array(unpack_ternary_mlx(mod.weight)).astype(np.float64)
        out_features, in_features = W.shape
        old_gamma = np.array(mod.gamma)

        # Compute per-row response statistics using random inputs
        # (since we want the plate's intrinsic scale, not data-dependent)
        rng = np.random.RandomState(42)
        n_samples = 500
        X = rng.randn(n_samples, in_features).astype(np.float64)
        # RMSNorm-like normalization (approximate)
        X = X / (np.sqrt(np.mean(X**2, axis=-1, keepdims=True)) + 1e-8)

        # Raw plate response: (out_features, n_samples)
        R = W @ X.T

        # Per-row std
        row_std = np.std(R, axis=1)  # (out_features,)
        row_std = np.maximum(row_std, 1e-8)

        # New gamma: calibrate to target output std, preserving overall scale
        new_gamma = target_output_std / row_std
        scale_ratio = np.mean(np.abs(old_gamma)) / (np.mean(np.abs(new_gamma)) + 1e-8)
        new_gamma = new_gamma * scale_ratio

        # Clamp: no gamma should be more than 3× the median
        median_gamma = np.median(np.abs(new_gamma))
        new_gamma = np.clip(new_gamma, -3.0 * median_gamma, 3.0 * median_gamma)

        mod.gamma = mx.array(new_gamma.astype(np.float32))
        mx.eval(mod.gamma)

        cv_old = np.std(old_gamma) / (np.mean(np.abs(old_gamma)) + 1e-8)
        cv_new = np.std(new_gamma.astype(np.float32)) / (np.mean(np.abs(new_gamma)) + 1e-8)

        log[name] = {
            "old_gamma_mean": float(np.mean(old_gamma)),
            "new_gamma_mean": float(np.mean(new_gamma)),
            "old_cv": float(cv_old),
            "new_cv": float(cv_new),
            "row_std_range": [float(np.min(row_std)), float(np.max(row_std))],
        }

    return log


def seed_gamma_matched_filter(
    model: V12Model,
    projection: TeacherProjection,
    teacher_dir: str,
    n_probes: int = 200,
) -> dict[str, dict]:
    """Strategy 2: Matched filter on per-pass I/O.

    For each pass (depth), forward projected teacher INPUT through the
    V12 pass, compare to projected teacher OUTPUT. Solve for gamma at
    each TernaryLinear via least-squares that minimizes pass output MSE.

    Since the pass is nonlinear, we approximate: for each TernaryLinear,
    compute the correlation between its per-row output and the overall
    pass output error. Rows that reduce error get higher gamma.
    """
    log = {}

    for depth_idx in range(7):  # 7 passes
        inputs, outputs = load_teacher_features(teacher_dir, depth_idx, n_probes)

        # Concatenate all probes' tokens into one big matrix
        all_in = np.concatenate(inputs, axis=0)    # (N_total, 5120)
        all_out = np.concatenate(outputs, axis=0)   # (N_total, 5120)

        # Project to student space
        t_in = mx.array(all_in[:2000])   # Limit to 2000 tokens for memory
        t_out = mx.array(all_out[:2000])
        proj_in = np.array(projection(t_in))     # (N, 512)
        proj_out = np.array(projection(t_out))    # (N, 512)

        # Forward through the pass
        x_in = mx.array(proj_in[None, :, :])  # (1, N, 512)
        pass_idx = depth_idx
        is_desc = pass_idx >= 4

        # Build readable banks
        n_banks = {0: 3, 1: 4, 2: 5, 3: 5, 4: 6, 5: 5, 6: 5}[pass_idx]
        readable = [model._init_bank0()]
        for _ in range(n_banks - 1):
            readable.append(model._fresh_bank())
        bank = model._fresh_bank()
        ret_regs = model._init_retrieval_registers()

        x_out_mx, *_ = model._run_level_pass(
            x_in, pass_idx, is_desc, readable, bank, ret_regs=ret_regs)
        mx.eval(x_out_mx)

        student_out = np.array(x_out_mx.squeeze(0))  # (N, 512)
        pass_error = proj_out - student_out            # (N, 512) — what we're missing

        # For each TernaryLinear that was exercised in this pass,
        # correlate its per-row output with the pass error
        for name, mod in model.named_modules():
            if not isinstance(mod, TernaryLinear):
                continue
            if not hasattr(mod, '_x_mean'):
                continue

            W = np.array(unpack_ternary_mlx(mod.weight)).astype(np.float64)
            out_features, in_features = W.shape

            # The input this module saw (cached from the forward pass)
            x_mean = np.array(mod._x_mean).astype(np.float64)  # (in_features,)

            # Raw plate response for the mean input
            raw = W @ x_mean  # (out_features,)

            # Correlation with the mean pass error direction
            error_mean = np.mean(pass_error, axis=0).astype(np.float64)  # (512,)

            # Only works if out_features == 512 (matches error dim)
            if out_features == error_mean.shape[0]:
                # Per-row: how much does this row's plate response
                # correlate with the error in that output dimension?
                # Higher correlation = this row should be amplified
                corr = raw * error_mean  # element-wise (out_features,)

                # Use correlation magnitude as importance weight
                importance = np.abs(corr)
                importance = importance / (np.mean(importance) + 1e-8)

                # Modulate gamma by importance (gentle: 80% old, 20% importance)
                # Clamp importance to [0.2, 3.0] to prevent extreme values
                importance = np.clip(importance, 0.2, 3.0)
                old_gamma = np.array(mod.gamma).astype(np.float64)
                new_gamma = old_gamma * (0.8 + 0.2 * importance)

                mod.gamma = mx.array(new_gamma.astype(np.float32))
                mx.eval(mod.gamma)

                if name not in log:
                    log[name] = {
                        "depth": depth_idx,
                        "importance_range": [float(np.min(importance)), float(np.max(importance))],
                        "gamma_change_pct": float(np.mean(np.abs(new_gamma - old_gamma) / (np.abs(old_gamma) + 1e-8)) * 100),
                    }

        mx.clear_cache()

    return log


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser(description="Gamma seeding from teacher features")
    p.add_argument("--weights", type=str,
                   default="checkpoints/v12-distill-run1/etch_round_005/weights.npz")
    p.add_argument("--projection", type=str,
                   default="checkpoints/v12-distill-run1/etch_round_005/projection.npz")
    p.add_argument("--teacher-features", type=str,
                   default="checkpoints/teacher-features")
    p.add_argument("--output", type=str,
                   default="checkpoints/v12-distill-run1/gamma_seeded/weights.npz")
    p.add_argument("--n-probes", type=int, default=200)
    p.add_argument("--strategy", choices=["variance", "matched", "both"], default="both",
                   help="Seeding strategy: variance calibration, matched filter, or both")
    return p.parse_args()


def main():
    args = parse_args()

    print(f"\n{'='*60}")
    print(f"  Gamma Seeding — Analytical Beam Initialization")
    print(f"  Strategy: {args.strategy}")
    print(f"{'='*60}\n")

    # Create model + load etched weights
    cfg = V12Config()
    model = create_model(cfg)
    weights = mx.load(args.weights)
    model.load_weights(list(weights.items()), strict=False)
    freeze_ternary_weights(model)
    restore_ternary(model)

    params = count_parameters(model)
    print(f"Model loaded: {params['total']:,} params, {params['trainable']:,} trainable")

    # Load projection
    projection = TeacherProjection(d_teacher=5120, d_student=cfg.d_model)
    if Path(args.projection).exists():
        proj_weights = mx.load(args.projection)
        projection.load_weights(list(proj_weights.items()), strict=False)
        print(f"Projection loaded from {args.projection}")
    else:
        print(f"⚠️ No projection found at {args.projection}, using random init")
    mx.eval(projection.parameters())

    # Pre-seeding gamma stats
    print(f"\n--- Pre-seeding gamma statistics ---")
    gamma_stats_before = {}
    for name, mod in model.named_modules():
        if isinstance(mod, TernaryLinear):
            g = np.array(mod.gamma)
            gamma_stats_before[name] = {
                "mean": float(np.mean(g)),
                "std": float(np.std(g)),
                "cv": float(np.std(g) / (np.mean(np.abs(g)) + 1e-8)),
            }
    # Summary
    cvs = [v["cv"] for v in gamma_stats_before.values()]
    print(f"  Modules: {len(cvs)}")
    print(f"  Mean CV (coefficient of variation): {np.mean(cvs):.4f}")
    print(f"  All gammas nearly uniform (CV < 0.05): {sum(1 for c in cvs if c < 0.05)}/{len(cvs)}")

    # Strategy 1: Variance calibration
    if args.strategy in ("variance", "both"):
        print(f"\n--- Strategy 1: Variance Calibration ---")
        t0 = time.time()
        var_log = seed_gamma_variance(model, target_output_std=1.0)
        print(f"  Done in {time.time() - t0:.1f}s")
        print(f"  Modules calibrated: {len(var_log)}")
        # Show a few
        for name in list(var_log.keys())[:5]:
            v = var_log[name]
            print(f"  {name}: CV {v['old_cv']:.4f} → {v['new_cv']:.4f}")

    # Strategy 2: Matched filter
    if args.strategy in ("matched", "both"):
        print(f"\n--- Strategy 2: Matched Filter ---")
        t0 = time.time()
        mf_log = seed_gamma_matched_filter(
            model, projection, args.teacher_features, args.n_probes)
        print(f"  Done in {time.time() - t0:.1f}s")
        print(f"  Modules with matched filter: {len(mf_log)}")
        for name in list(mf_log.keys())[:5]:
            v = mf_log[name]
            print(f"  {name}: importance [{v['importance_range'][0]:.3f}, "
                  f"{v['importance_range'][1]:.3f}], "
                  f"gamma change {v['gamma_change_pct']:.1f}%")

    # Post-seeding gamma stats
    print(f"\n--- Post-seeding gamma statistics ---")
    gamma_stats_after = {}
    for name, mod in model.named_modules():
        if isinstance(mod, TernaryLinear):
            g = np.array(mod.gamma)
            gamma_stats_after[name] = {
                "mean": float(np.mean(g)),
                "std": float(np.std(g)),
                "cv": float(np.std(g) / (np.mean(np.abs(g)) + 1e-8)),
            }
    cvs_after = [v["cv"] for v in gamma_stats_after.values()]
    print(f"  Mean CV: {np.mean(cvs):.4f} → {np.mean(cvs_after):.4f}")
    print(f"  Uniform gammas (CV < 0.05): {sum(1 for c in cvs if c < 0.05)}/{len(cvs)}"
          f" → {sum(1 for c in cvs_after if c < 0.05)}/{len(cvs_after)}")

    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    flat = dict(tree_flatten(model.parameters()))
    mx.savez(str(output_path), **flat)
    print(f"\n  Saved gamma-seeded weights to {output_path}")

    # Save log
    log_path = output_path.parent / "seed_log.json"
    all_log = {
        "strategy": args.strategy,
        "n_probes": args.n_probes,
        "gamma_before": {k: v for k, v in list(gamma_stats_before.items())[:10]},
        "gamma_after": {k: v for k, v in list(gamma_stats_after.items())[:10]},
        "mean_cv_before": float(np.mean(cvs)),
        "mean_cv_after": float(np.mean(cvs_after)),
    }
    with open(log_path, "w") as f:
        json.dump(all_log, f, indent=2)
    print(f"  Saved log to {log_path}")

    print(f"\n{'='*60}")
    print(f"  Gamma seeding complete!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
