#!/usr/bin/env python3
"""Holographic landscape probe — per-weight-matrix ternary fidelity.

Maps every weight matrix in a model to determine its "holographic fraction":
how much of its information lives in the sign topology vs magnitudes.

A weight matrix where ternary quantization causes zero loss is one where
ALL information is topological — it's fully holographic. The magnitude
is noise that gradient descent left there, carrying no signal.

Metrics per weight matrix:
  1. ternary_cosine: cos(W, sign(W)) — how much direction is captured by signs
     ≈ 1.0 → fully holographic, signs ARE the signal
     < 0.8 → magnitude-dependent, needs more than 1.58 bits

  2. sign_balance: ratio of positive to negative entries
     ≈ 1.0 → balanced holographic plate (like the combinator holograms)
     >> 1 or << 1 → biased, may indicate structural role

  3. magnitude_cv: coefficient of variation of |W| (std/mean)
     Low → magnitudes are uniform (ternary-safe, magnitudes add nothing)
     High → magnitudes vary significantly (information in magnitudes)

  4. effective_rank_ratio: effective rank / min(rows, cols)
     High → distributed (holographic), low → concentrated (not holographic)

  5. sparsity: fraction of weights near zero (|w| < threshold)

Validation mode: for selected matrices, substitute ternary weights and
measure output divergence on a small eval set.

Usage:
    # Fast scan — per-matrix holographic scores (no inference)
    uv run python scripts/explore/probe_holographic_landscape.py \\
        --model qwen36 --output results/holographic-landscape/

    # With validation — substitute ternary weights, measure perplexity
    uv run python scripts/explore/probe_holographic_landscape.py \\
        --model qwen36 --validate --n-val-batches 5

Target: Qwen3.6-35B-A3B as primary model to emulate in V12 sieve.

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

import mlx.core as mx
import numpy as np


# ══════════════════════════════════════════════════════════════════════
# Per-matrix holographic metrics
# ══════════════════════════════════════════════════════════════════════


@dataclass
class HolographicMetrics:
    """Holographic fidelity metrics for a single weight matrix."""
    name: str               # full parameter path
    shape: tuple[int, ...]  # weight shape
    n_params: int           # total elements
    ternary_cosine: float   # cos(W, sign(W)) — holographic fidelity
    sign_balance: float     # n_positive / n_negative
    magnitude_cv: float     # std(|W|) / mean(|W|) — magnitude uniformity
    magnitude_mean: float   # mean(|W|) — scale
    effective_rank_ratio: float  # effective rank / min(rows, cols)
    sparsity_01: float      # fraction |w| < 0.01 * mean(|W|)
    # Derived
    holographic_score: float  # combined score: how ternary-safe is this matrix?

    @property
    def is_holographic(self) -> bool:
        """Heuristic: fully holographic if score > 0.9."""
        return self.holographic_score > 0.9

    @property
    def category(self) -> str:
        s = self.holographic_score
        if s > 0.95:
            return "fully_holographic"
        elif s > 0.85:
            return "mostly_holographic"
        elif s > 0.70:
            return "partially_holographic"
        else:
            return "magnitude_dependent"


def compute_holographic_metrics(name: str, W: mx.array) -> HolographicMetrics:
    """Compute holographic fidelity metrics for a weight matrix.

    All computation is on the weight matrix itself — no inference needed.
    """
    # Flatten to 1D for scalar metrics, keep 2D for rank
    W_flat = W.reshape(-1).astype(mx.float32)
    n = W_flat.shape[0]

    # ── Ternary cosine: cos(W, sign(W)) ──────────────────────
    # How much of W's direction is captured by signs alone?
    W_sign = mx.sign(W_flat)
    # cos = (W · sign(W)) / (||W|| × ||sign(W)||)
    # Note: W · sign(W) = sum(|W|), and ||sign(W)|| = sqrt(n_nonzero)
    abs_W = mx.abs(W_flat)
    dot = mx.sum(abs_W)  # = W · sign(W)
    norm_W = mx.sqrt(mx.sum(W_flat * W_flat) + 1e-12)
    n_nonzero = mx.sum(W_sign != 0)
    norm_sign = mx.sqrt(n_nonzero.astype(mx.float32) + 1e-12)
    ternary_cosine = float((dot / (norm_W * norm_sign + 1e-12)).item())

    # ── Sign balance ──────────────────────────────────────────
    n_pos = float(mx.sum(W_flat > 0).item())
    n_neg = float(mx.sum(W_flat < 0).item())
    sign_balance = n_pos / max(n_neg, 1)

    # ── Magnitude statistics ──────────────────────────────────
    mag_mean = float(mx.mean(abs_W).item())
    mag_std = float(mx.sqrt(mx.mean((abs_W - mag_mean) ** 2) + 1e-12).item())
    magnitude_cv = mag_std / max(mag_mean, 1e-12)

    # ── Sparsity ──────────────────────────────────────────────
    threshold = 0.01 * max(mag_mean, 1e-8)
    sparsity_01 = float(mx.mean((abs_W < threshold).astype(mx.float32)).item())

    # ── Effective rank (via singular value proxy) ─────────────
    # Full SVD is expensive for large matrices. Use a proxy:
    # For 2D matrices: sample random projections and estimate.
    # For simplicity, use row-norm variance as a proxy for rank.
    if W.ndim >= 2:
        W_2d = W.reshape(-1, W.shape[-1]) if W.ndim > 2 else W
        rows, cols = W_2d.shape
        min_dim = min(rows, cols)

        # Row norms
        row_norms = mx.sqrt(mx.sum(W_2d * W_2d, axis=-1) + 1e-12)
        row_norm_mean = float(mx.mean(row_norms).item())
        row_norm_std = float(mx.sqrt(mx.mean(
            (row_norms - row_norm_mean) ** 2) + 1e-12).item())

        # Low CV of row norms → distributed (high effective rank)
        # High CV → concentrated (low effective rank)
        row_cv = row_norm_std / max(row_norm_mean, 1e-12)
        # Map CV to rank ratio: CV=0 → ratio=1.0, CV=1 → ratio=0.5
        effective_rank_ratio = 1.0 / (1.0 + row_cv)
    else:
        effective_rank_ratio = 1.0  # 1D params are trivially "full rank"

    # ── Combined holographic score ────────────────────────────
    # Weighted combination:
    #   ternary_cosine: primary signal (0.5 weight)
    #   1 - magnitude_cv: magnitude uniformity (0.2 weight)
    #   sign_balance_score: near 1.0 is good (0.1 weight)
    #   effective_rank_ratio: distributed is holographic (0.1 weight)
    #   1 - sparsity: not too sparse (0.1 weight)
    balance_score = min(sign_balance, 1.0 / max(sign_balance, 1e-8))
    mag_uniformity = max(0, 1.0 - magnitude_cv)

    holographic_score = (
        0.50 * ternary_cosine +
        0.20 * mag_uniformity +
        0.10 * balance_score +
        0.10 * effective_rank_ratio +
        0.10 * (1.0 - sparsity_01)
    )

    return HolographicMetrics(
        name=name,
        shape=tuple(W.shape),
        n_params=n,
        ternary_cosine=ternary_cosine,
        sign_balance=sign_balance,
        magnitude_cv=magnitude_cv,
        magnitude_mean=mag_mean,
        effective_rank_ratio=effective_rank_ratio,
        sparsity_01=sparsity_01,
        holographic_score=holographic_score,
    )


# ══════════════════════════════════════════════════════════════════════
# Model loading
# ══════════════════════════════════════════════════════════════════════


def load_model_weights(model_name: str) -> dict[str, mx.array]:
    """Load model weights as a flat dict of name → tensor.

    Supports:
      qwen36: Qwen3.6-35B-A3B (mlx-community quantized or HF)
      qwen32b: Qwen3-32B
      pythia160m: Pythia-160M
    """
    if model_name == "qwen36":
        # Try mlx-community first (pre-sharded for MLX)
        try:
            from mlx_lm.utils import load_model
            model_path = "mlx-community/Qwen3-35B-A3B-4bit"
            print(f"Loading {model_path}...")
            model, tokenizer = load_model(model_path)
            # Extract all parameters as flat dict
            weights = {}
            for name, param in model.named_parameters():
                weights[name] = param
            return weights
        except Exception:
            pass

        # Fallback: load from safetensors directly
        try:
            from mlx.utils import tree_flatten
            import glob
            model_path = Path.home() / ".cache" / "huggingface" / "hub"
            # Find Qwen3.6 model files
            patterns = [
                str(model_path / "models--Qwen--Qwen3-30B-A3B" / "**" / "*.safetensors"),
                str(model_path / "models--Qwen--Qwen3-35B-A3B" / "**" / "*.safetensors"),
            ]
            for pattern in patterns:
                files = glob.glob(pattern, recursive=True)
                if files:
                    print(f"Loading from safetensors: {len(files)} files")
                    weights = {}
                    for f in sorted(files):
                        w = mx.load(f)
                        weights.update(w)
                    return weights
        except Exception:
            pass

        # Try mlx_lm load
        try:
            import mlx_lm
            model_path = "Qwen/Qwen3-30B-A3B"
            print(f"Loading {model_path} via mlx_lm...")
            model, tokenizer = mlx_lm.load(model_path)
            weights = dict(tree_flatten(model.parameters()))
            return weights
        except Exception as e:
            print(f"Failed to load qwen36: {e}")
            raise

    elif model_name == "qwen32b":
        import mlx_lm
        model, tokenizer = mlx_lm.load("mlx-community/Qwen3-32B-4bit")
        from mlx.utils import tree_flatten
        return dict(tree_flatten(model.parameters()))

    elif model_name == "pythia160m":
        import mlx_lm
        model, tokenizer = mlx_lm.load("EleutherAI/pythia-160m")
        from mlx.utils import tree_flatten
        return dict(tree_flatten(model.parameters()))

    else:
        raise ValueError(f"Unknown model: {model_name}")


# ══════════════════════════════════════════════════════════════════════
# Landscape analysis
# ══════════════════════════════════════════════════════════════════════


def analyze_landscape(
    weights: dict[str, mx.array],
    min_params: int = 1024,
) -> list[HolographicMetrics]:
    """Compute holographic metrics for all weight matrices.

    Args:
        weights: flat dict of parameter name → tensor
        min_params: skip matrices smaller than this (biases, norms, etc.)

    Returns: list of HolographicMetrics, sorted by holographic_score descending.
    """
    results = []
    total_params = 0
    skipped = 0

    for name, W in sorted(weights.items()):
        n = W.size
        total_params += n

        # Skip tiny params (biases, norms, scalars)
        if n < min_params:
            skipped += 1
            continue

        # Skip quantization scales/biases (not the actual weights)
        if any(skip in name for skip in ['scales', 'biases', '_norm', 'norm.']):
            skipped += 1
            continue

        metrics = compute_holographic_metrics(name, W)
        mx.eval(W)  # free memory
        results.append(metrics)

    results.sort(key=lambda m: m.holographic_score, reverse=True)

    print(f"\nAnalyzed {len(results)} weight matrices "
          f"({total_params:,} total params, skipped {skipped} small/meta)")

    return results


def print_landscape_summary(results: list[HolographicMetrics]) -> None:
    """Print summary of the holographic landscape."""
    if not results:
        print("No results to summarize.")
        return

    total_params = sum(m.n_params for m in results)

    # Category breakdown
    categories = defaultdict(lambda: {"count": 0, "params": 0})
    for m in results:
        cat = m.category
        categories[cat]["count"] += 1
        categories[cat]["params"] += m.n_params

    print("\n" + "=" * 80)
    print("HOLOGRAPHIC LANDSCAPE SUMMARY")
    print("=" * 80)

    print(f"\nTotal weight matrices: {len(results)}")
    print(f"Total parameters: {total_params:,}")

    print(f"\n{'Category':<25} {'Count':>6} {'Params':>14} {'% Params':>10}")
    print("─" * 60)
    for cat in ["fully_holographic", "mostly_holographic",
                "partially_holographic", "magnitude_dependent"]:
        info = categories[cat]
        pct = 100.0 * info["params"] / total_params if total_params > 0 else 0
        print(f"{cat:<25} {info['count']:>6} {info['params']:>14,} {pct:>9.1f}%")

    # Ternary-safe total
    ternary_safe_params = sum(
        m.n_params for m in results if m.holographic_score > 0.85)
    pct_safe = 100.0 * ternary_safe_params / total_params if total_params > 0 else 0
    print(f"\nTernary-safe (score > 0.85): {ternary_safe_params:,} / "
          f"{total_params:,} = {pct_safe:.1f}%")

    # Top-10 most holographic
    print(f"\n{'─' * 80}")
    print("TOP 10 MOST HOLOGRAPHIC (best ternary candidates)")
    print(f"{'─' * 80}")
    print(f"{'Name':<50} {'Score':>6} {'TernCos':>8} {'MagCV':>6} {'Params':>10}")
    for m in results[:10]:
        short_name = m.name[-48:] if len(m.name) > 48 else m.name
        print(f"{short_name:<50} {m.holographic_score:>6.3f} "
              f"{m.ternary_cosine:>8.4f} {m.magnitude_cv:>6.3f} {m.n_params:>10,}")

    # Bottom-10 most magnitude-dependent
    print(f"\n{'─' * 80}")
    print("BOTTOM 10 MOST MAGNITUDE-DEPENDENT (need precision)")
    print(f"{'─' * 80}")
    print(f"{'Name':<50} {'Score':>6} {'TernCos':>8} {'MagCV':>6} {'Params':>10}")
    for m in results[-10:]:
        short_name = m.name[-48:] if len(m.name) > 48 else m.name
        print(f"{short_name:<50} {m.holographic_score:>6.3f} "
              f"{m.ternary_cosine:>8.4f} {m.magnitude_cv:>6.3f} {m.n_params:>10,}")

    # By layer type
    print(f"\n{'─' * 80}")
    print("BY COMPONENT TYPE (mean holographic score)")
    print(f"{'─' * 80}")
    type_scores = defaultdict(list)
    for m in results:
        # Extract component type from name
        parts = m.name.split(".")
        if "q_proj" in m.name or "k_proj" in m.name or "v_proj" in m.name or "o_proj" in m.name:
            ctype = "attention_qkvo"
        elif "gate" in m.name.lower() and "proj" not in m.name.lower():
            ctype = "moe_gate"
        elif "expert" in m.name.lower() or "mlp" in m.name.lower():
            ctype = "mlp/expert"
        elif "embed" in m.name.lower():
            ctype = "embedding"
        elif "in_proj" in m.name or "linear_attn" in m.name:
            ctype = "linear_attention"
        else:
            ctype = "other"
        type_scores[ctype].append(m.holographic_score)

    print(f"{'Component':<25} {'N':>5} {'Mean Score':>11} {'Min':>7} {'Max':>7}")
    for ctype, scores in sorted(type_scores.items(), key=lambda x: -np.mean(x[1])):
        arr = np.array(scores)
        print(f"{ctype:<25} {len(arr):>5} {arr.mean():>11.4f} "
              f"{arr.min():>7.4f} {arr.max():>7.4f}")


def save_results(
    results: list[HolographicMetrics],
    output_dir: Path,
    model_name: str,
) -> None:
    """Save results to JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Full results
    out = {
        "model": model_name,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n_matrices": len(results),
        "total_params": sum(m.n_params for m in results),
        "matrices": [asdict(m) for m in results],
    }

    # Summary stats
    total = sum(m.n_params for m in results)
    out["summary"] = {
        "fully_holographic_pct": 100.0 * sum(
            m.n_params for m in results if m.category == "fully_holographic"
        ) / max(total, 1),
        "ternary_safe_pct": 100.0 * sum(
            m.n_params for m in results if m.holographic_score > 0.85
        ) / max(total, 1),
        "mean_holographic_score": float(np.mean(
            [m.holographic_score for m in results])),
        "mean_ternary_cosine": float(np.mean(
            [m.ternary_cosine for m in results])),
    }

    outpath = output_dir / f"holographic_landscape_{model_name}.json"
    with open(outpath, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nResults saved to {outpath}")


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(
        description="Map the holographic landscape of an LLM — "
                    "per-weight-matrix ternary fidelity analysis.")
    parser.add_argument(
        "--model", default="qwen36",
        choices=["qwen36", "qwen32b", "pythia160m"],
        help="Model to analyze (default: qwen36)")
    parser.add_argument(
        "--output", default="results/holographic-landscape/",
        help="Output directory for results")
    parser.add_argument(
        "--min-params", type=int, default=1024,
        help="Skip weight matrices smaller than this (default: 1024)")
    parser.add_argument(
        "--validate", action="store_true",
        help="Run inference-based validation on boundary matrices")
    parser.add_argument(
        "--n-val-batches", type=int, default=5,
        help="Number of eval batches for validation (default: 5)")
    args = parser.parse_args()

    print(f"Holographic Landscape Probe")
    print(f"  Model: {args.model}")
    print(f"  Output: {args.output}")
    print(f"  Min params: {args.min_params}")

    # Load model weights
    t0 = time.time()
    weights = load_model_weights(args.model)
    print(f"  Loaded in {time.time() - t0:.1f}s")

    # Analyze
    t1 = time.time()
    results = analyze_landscape(weights, min_params=args.min_params)
    print(f"  Analyzed in {time.time() - t1:.1f}s")

    # Print summary
    print_landscape_summary(results)

    # Save
    save_results(results, Path(args.output), args.model)

    if args.validate:
        print("\n[Validation mode not yet implemented — "
              "requires model inference pipeline]")


if __name__ == "__main__":
    main()
