"""Probe backbone threshold — find the 20% that IS 80% of the crystal.

Protocol:
  1. Generate lambda corpus (K, I, B, C, M)
  2. For each operation: accumulate gradient direction over many batches
  3. Compute per-position backbone score:
     - Positions with HIGH confidence across ALL operations = structural backbone
     - Positions with high confidence for ONE op only = operation-specific
     - Positions with low confidence = noise (model doesn't care)
  4. Progressive installation: install top N% of backbone, train beam, measure snap
  5. Find the inflection point (knee) where adding more stops helping
  6. Output: the backbone threshold and the backbone positions

The backbone score for position (i,j) is:
    backbone[i,j] = min(confidence_K[i,j], confidence_I[i,j], ..., confidence_M[i,j])
    
    High backbone = this position has strong, consistent gradient signal
    regardless of which operation is being recorded. It's structural.

Usage:
    uv run python scripts/v12/probe_backbone_threshold.py
    uv run python scripts/v12/probe_backbone_threshold.py --batches-per-op 100

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
import mlx.optimizers as optim
import numpy as np
from mlx.utils import tree_flatten, tree_map

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from config import V12Config
from model import V12Model, create_model, count_parameters
from ternary import (
    freeze_ternary_weights,
    zero_ternary_grads,
    restore_ternary,
    _walk_ternary_modules,
    TernaryLinear,
    DirectionAccumulator,
    init_direction_accumulators,
    accumulate_direction,
    direct_etch,
    reset_accumulators,
    pack_ternary_mlx,
    unpack_ternary_mlx,
    _unpack_signal_plane_np,
    _pack_signal_plane_np,
)
from holographic_train import build_lambda_corpus, corpus_batch, ce_loss


def compute_backbone_scores(
    model: V12Model,
    corpus: dict[str, list[list[int]]],
    cfg: V12Config,
    batches_per_op: int = 50,
    seed: int = 42,
) -> dict[str, dict]:
    """Accumulate gradient direction for each operation, compute backbone scores.

    Returns per-module dict with:
        - direction_per_op: dict[op] → (N, K) accumulated direction
        - confidence_per_op: dict[op] → (N, K) confidence [0, 1]
        - backbone_score: (N, K) = min confidence across all ops
        - target_sign_per_op: dict[op] → (N, K) int8 target signs
    """
    print("\n  Computing backbone scores...", file=sys.stderr, flush=True)

    loss_and_grad = nn.value_and_grad(model, ce_loss)
    rng = np.random.RandomState(seed)

    # Accumulate direction for each operation separately
    op_accumulators: dict[str, dict[str, DirectionAccumulator]] = {}

    for op in ["K", "I", "B", "C", "M"]:
        accums = init_direction_accumulators(model)
        
        op_losses = []
        for batch_idx in range(batches_per_op):
            input_ids, targets = corpus_batch(
                corpus, op, batch_size=cfg.batch_size, rng=rng,
                seq_len=cfg.seq_len,
            )
            loss_val, grads = loss_and_grad(model, input_ids, targets)
            mx.eval(loss_val, grads)
            op_losses.append(float(loss_val.item()))
            accumulate_direction(model, grads, accums)

        avg_loss = np.mean(op_losses)
        print(f"    {op}: {batches_per_op} batches, loss={avg_loss:.3f}",
              file=sys.stderr, flush=True)
        op_accumulators[op] = accums

    # Compute per-module backbone scores
    print("\n  Computing per-position backbone scores...", file=sys.stderr, flush=True)

    module_scores = {}
    for path, mod in _walk_ternary_modules(model):
        if not isinstance(mod, TernaryLinear) or "q_proj" in path:
            continue
        if path not in op_accumulators["K"]:
            continue

        N = mod.out_features
        K = mod.in_features

        # Get confidence and target signs per operation
        confidence_per_op = {}
        target_per_op = {}
        direction_per_op = {}

        for op in ["K", "I", "B", "C", "M"]:
            acc = op_accumulators[op][path]
            confidence_per_op[op] = acc.get_confidence()      # (N, K) [0, 1]
            target_per_op[op] = acc.get_target_signs()        # (N, K) int8
            direction_per_op[op] = acc.direction.copy()       # (N, K) raw

        # Backbone score = min confidence across all ops
        # High = this position has strong signal regardless of operation = structural
        all_confs = np.stack([confidence_per_op[op] for op in ["K", "I", "B", "C", "M"]])
        backbone_score = np.min(all_confs, axis=0)  # (N, K)

        # Also compute: positions where all ops AGREE on direction
        # These are the true lattice points (structure wants them the same way
        # regardless of which operation is being recorded)
        all_targets = np.stack([target_per_op[op] for op in ["K", "I", "B", "C", "M"]])
        # Agreement: same sign across all 5 ops (and non-zero)
        unanimous_pos = np.all(all_targets == all_targets[0:1], axis=0) & (all_targets[0] != 0)
        unanimous_sign = np.where(unanimous_pos, all_targets[0], np.int8(0))

        # Combined score: backbone × unanimity
        # Only positions where ALL ops agree AND all have high confidence
        combined_score = backbone_score * unanimous_pos.astype(np.float32)

        # Operation-specific score = max confidence for ONE op minus mean of others
        # High = this position is important for a specific operation
        mean_conf = np.mean(all_confs, axis=0)
        max_conf = np.max(all_confs, axis=0)
        specificity_score = max_conf - mean_conf  # (N, K)

        module_scores[path] = {
            "backbone_score": backbone_score,
            "combined_score": combined_score,
            "unanimous_sign": unanimous_sign,
            "specificity_score": specificity_score,
            "confidence_per_op": confidence_per_op,
            "target_per_op": target_per_op,
            "n_unanimous": int(unanimous_pos.sum()),
            "total_positions": N * K,
        }

    # Summary stats
    total_positions = sum(s["total_positions"] for s in module_scores.values())
    total_unanimous = sum(s["n_unanimous"] for s in module_scores.values())
    print(f"\n  Total etchable positions: {total_positions:,}", file=sys.stderr, flush=True)
    print(f"  Unanimous positions (all 5 ops agree): {total_unanimous:,} "
          f"({total_unanimous/total_positions*100:.1f}%)", file=sys.stderr, flush=True)

    return module_scores


def progressive_installation(
    cfg: V12Config,
    corpus: dict[str, list[list[int]]],
    module_scores: dict[str, dict],
    thresholds: list[float],
    beam_steps: int = 200,
    beam_lr: float = 3e-4,
    seed: int = 42,
) -> list[dict]:
    """Install increasing fractions of backbone, measure crystal snap.

    For each threshold in thresholds (percentage of top positions to install):
      1. Create fresh model
      2. Install top N% of backbone positions (by combined_score)
      3. Train beam for beam_steps
      4. Measure final loss

    Returns list of dicts with threshold, n_installed, final_loss, etc.
    """
    print(f"\n  Progressive installation sweep: {thresholds}",
          file=sys.stderr, flush=True)

    # Pre-compute global backbone ranking
    # Gather all (score, path, i, j, sign) tuples
    all_positions = []
    for path, scores in module_scores.items():
        combined = scores["combined_score"]
        unanimous = scores["unanimous_sign"]
        N, K = combined.shape
        # Only include positions with unanimous agreement
        mask = unanimous != 0
        indices = np.argwhere(mask)
        for idx in indices:
            i, j = idx
            all_positions.append((
                float(combined[i, j]),  # score for ranking
                path, int(i), int(j),
                int(unanimous[i, j]),    # the sign to install
            ))

    # Sort by score (descending)
    all_positions.sort(key=lambda x: -x[0])
    total_backbone = len(all_positions)
    total_etchable = sum(s["total_positions"] for s in module_scores.values())

    print(f"    Backbone candidates (unanimous): {total_backbone:,} "
          f"({total_backbone/total_etchable*100:.1f}% of plate)",
          file=sys.stderr, flush=True)
    print(f"    Top scores: {all_positions[0][0]:.4f}, {all_positions[100][0]:.4f}, "
          f"{all_positions[min(1000, len(all_positions)-1)][0]:.4f}",
          file=sys.stderr, flush=True)

    results = []
    rng = np.random.RandomState(seed)
    loss_and_grad = None  # will create per model

    for threshold_pct in thresholds:
        # How many positions to install
        n_install = int(total_etchable * threshold_pct / 100)
        n_install = min(n_install, total_backbone)

        # Create fresh model
        model = create_model(cfg)
        mx.eval(model.parameters())

        # Install top-N positions
        positions_to_install = all_positions[:n_install]

        # Group by module path for efficient writing
        by_module: dict[str, list[tuple[int, int, int]]] = {}
        for score, path, i, j, sign in positions_to_install:
            by_module.setdefault(path, []).append((i, j, sign))

        # Write signs
        n_actually_flipped = 0
        for path, mod in _walk_ternary_modules(model):
            if path not in by_module:
                continue
            if not isinstance(mod, TernaryLinear):
                continue

            current_signs = _unpack_signal_plane_np(
                np.array(mod.weight), mod.in_features
            )

            for i, j, target_sign in by_module[path]:
                if current_signs[i, j] != target_sign:
                    current_signs[i, j] = target_sign
                    n_actually_flipped += 1

            mod.weight = mx.array(_pack_signal_plane_np(current_signs))
            mx.eval(mod.weight)

        freeze_ternary_weights(model)
        restore_ternary(model)

        # Train beam
        optimizer = optim.Adam(learning_rate=beam_lr)
        mx.eval(optimizer.state)
        loss_fn = nn.value_and_grad(model, ce_loss)

        beam_losses = []
        for step in range(beam_steps):
            op = rng.choice(["K", "I", "B", "C", "M"])
            input_ids, targets = corpus_batch(
                corpus, op, batch_size=cfg.batch_size, rng=rng,
                seq_len=cfg.seq_len,
            )
            loss_val, grads = loss_fn(model, input_ids, targets)
            mx.eval(loss_val, grads)
            grads = zero_ternary_grads(model, grads)
            optimizer.update(model, grads)
            mx.eval(model.parameters(), optimizer.state)
            restore_ternary(model)
            beam_losses.append(float(loss_val.item()))

        # Measure final quality
        final_loss = np.mean(beam_losses[-50:]) if len(beam_losses) >= 50 else np.mean(beam_losses)
        min_loss = min(beam_losses)
        loss_at_100 = np.mean(beam_losses[90:100]) if len(beam_losses) >= 100 else final_loss

        result = {
            "threshold_pct": threshold_pct,
            "n_installed": n_install,
            "n_flipped": n_actually_flipped,
            "pct_of_plate": n_install / total_etchable * 100,
            "final_loss": final_loss,
            "min_loss": min_loss,
            "loss_at_100": loss_at_100,
            "loss_trajectory": beam_losses[::10],  # every 10th step
        }
        results.append(result)

        print(f"    {threshold_pct:5.1f}% | installed={n_install:>8,} | "
              f"flipped={n_actually_flipped:>8,} | "
              f"loss@100={loss_at_100:.3f} | final={final_loss:.3f} | min={min_loss:.3f}",
              file=sys.stderr, flush=True)

        # Free model memory
        del model, optimizer
        mx.metal.clear_cache() if hasattr(mx, 'metal') else None

    return results


def find_knee(results: list[dict]) -> dict:
    """Find the inflection point (knee) in the threshold→loss curve.

    Uses the maximum curvature method: where the second derivative
    of the loss curve is most negative = sharpest bend.
    """
    if len(results) < 3:
        return {"knee_pct": results[0]["threshold_pct"], "method": "insufficient_data"}

    x = np.array([r["threshold_pct"] for r in results])
    y = np.array([r["final_loss"] for r in results])

    # Normalize to [0,1] for curvature calculation
    x_norm = (x - x.min()) / (x.max() - x.min() + 1e-8)
    y_norm = (y - y.min()) / (y.max() - y.min() + 1e-8)

    # Second derivative (finite differences)
    if len(x_norm) >= 3:
        d2y = np.gradient(np.gradient(y_norm, x_norm), x_norm)
        # Knee = maximum negative curvature (sharpest downward bend)
        knee_idx = np.argmin(d2y)
        knee_pct = float(x[knee_idx])
    else:
        knee_idx = 0
        knee_pct = float(x[0])

    return {
        "knee_pct": knee_pct,
        "knee_loss": float(y[knee_idx]),
        "knee_improvement": float((y[0] - y[knee_idx]) / (y[0] - y[-1] + 1e-8) * 100),
        "method": "max_curvature",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Find the backbone threshold — the 20% that IS 80% of the crystal"
    )
    parser.add_argument("--batches-per-op", type=int, default=50,
                        help="Batches per operation for direction accumulation")
    parser.add_argument("--beam-steps", type=int, default=300,
                        help="Beam training steps per threshold test")
    parser.add_argument("--beam-lr", type=float, default=3e-4,
                        help="Beam training learning rate")
    parser.add_argument("--n-examples", type=int, default=3000,
                        help="Lambda examples per operation")
    parser.add_argument("--output-dir", default="results/backbone-threshold",
                        help="Directory for results")

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Config
    cfg = V12Config()
    cfg.seq_len = 2048
    cfg.batch_size = 2

    print("=" * 72, file=sys.stderr)
    print("  Backbone Threshold Probe", file=sys.stderr)
    print("  Finding the 20% that IS 80% of the crystal", file=sys.stderr)
    print("=" * 72, file=sys.stderr)

    # ── Step 1: Create model and corpus ───────────────────────
    print("\nCreating model...", file=sys.stderr, flush=True)
    model = create_model(cfg)
    mx.eval(model.parameters())

    print("Building lambda corpus...", file=sys.stderr, flush=True)
    corpus = build_lambda_corpus(
        n_per_op=args.n_examples,
        seq_len=cfg.seq_len,
        seed=42,
    )

    # ── Step 2: Compute backbone scores ───────────────────────
    module_scores = compute_backbone_scores(
        model, corpus, cfg,
        batches_per_op=args.batches_per_op,
    )

    # Save backbone analysis
    backbone_summary = {}
    for path, scores in module_scores.items():
        bs = scores["backbone_score"]
        cs = scores["combined_score"]
        backbone_summary[path] = {
            "total_positions": scores["total_positions"],
            "n_unanimous": scores["n_unanimous"],
            "backbone_score_mean": float(bs.mean()),
            "backbone_score_p90": float(np.percentile(bs, 90)),
            "combined_score_mean": float(cs.mean()),
            "combined_score_p90": float(np.percentile(cs, 90)),
        }

    with open(output_dir / "backbone_analysis.json", "w") as f:
        json.dump(backbone_summary, f, indent=2)

    # Free the model used for scoring (we'll create fresh ones for each threshold)
    del model

    # ── Step 3: Progressive installation sweep ────────────────
    thresholds = [1.0, 2.0, 5.0, 8.0, 10.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0]

    results = progressive_installation(
        cfg, corpus, module_scores,
        thresholds=thresholds,
        beam_steps=args.beam_steps,
        beam_lr=args.beam_lr,
    )

    # ── Step 4: Find the knee ─────────────────────────��───────
    knee = find_knee(results)

    # Also include a baseline (0% installed = random model)
    # This is effectively the first data point with n_installed=0
    # We can infer it from the highest loss in the sweep

    print(f"\n{'='*72}", file=sys.stderr)
    print(f"  RESULTS", file=sys.stderr)
    print(f"{'='*72}", file=sys.stderr)
    print(f"\n  Threshold sweep:", file=sys.stderr)
    print(f"  {'%':>6s} | {'installed':>10s} | {'loss@100':>8s} | {'final':>8s} | {'min':>8s}",
          file=sys.stderr)
    print(f"  {'-'*6}-+-{'-'*10}-+-{'-'*8}-+-{'-'*8}-+-{'-'*8}", file=sys.stderr)
    for r in results:
        print(f"  {r['threshold_pct']:5.1f}% | {r['n_installed']:>10,} | "
              f"{r['loss_at_100']:8.3f} | {r['final_loss']:8.3f} | {r['min_loss']:8.3f}",
              file=sys.stderr)

    print(f"\n  Knee (inflection point): {knee['knee_pct']:.1f}%", file=sys.stderr)
    if 'knee_improvement' in knee:
        print(f"  At knee, {knee['knee_improvement']:.0f}% of total improvement achieved",
              file=sys.stderr)
    print(f"{'='*72}\n", file=sys.stderr)

    # Save full results
    final_results = {
        "thresholds": thresholds,
        "results": results,
        "knee": knee,
        "config": {
            "batches_per_op": args.batches_per_op,
            "beam_steps": args.beam_steps,
            "beam_lr": args.beam_lr,
            "n_examples": args.n_examples,
            "seq_len": cfg.seq_len,
            "batch_size": cfg.batch_size,
        },
        "backbone_summary": backbone_summary,
    }

    with open(output_dir / "results.json", "w") as f:
        json.dump(final_results, f, indent=2)

    print(f"  💾 Results saved to {output_dir / 'results.json'}", file=sys.stderr)
    print(f"  💾 Backbone analysis: {output_dir / 'backbone_analysis.json'}", file=sys.stderr)


if __name__ == "__main__":
    main()
