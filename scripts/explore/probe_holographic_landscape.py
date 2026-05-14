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

import numpy as np
import torch


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


def compute_holographic_metrics(name: str, W: np.ndarray) -> HolographicMetrics:
    """Compute holographic fidelity metrics for a weight matrix.

    All computation is on the weight matrix itself — no inference needed.
    Uses numpy for portability (works on CPU after extracting from GPU).
    """
    W_flat = W.reshape(-1).astype(np.float32)
    n = W_flat.shape[0]

    # ── Ternary cosine: cos(W, sign(W)) ──────────────────────
    # How much of W's direction is captured by signs alone?
    # cos = (W · sign(W)) / (||W|| × ||sign(W)||)
    # Note: W · sign(W) = sum(|W|), and ||sign(W)|| = sqrt(n_nonzero)
    abs_W = np.abs(W_flat)
    dot = np.sum(abs_W)  # = W · sign(W)
    norm_W = np.sqrt(np.sum(W_flat * W_flat) + 1e-12)
    n_nonzero = np.sum(W_flat != 0)
    norm_sign = np.sqrt(float(n_nonzero) + 1e-12)
    ternary_cosine = float(dot / (norm_W * norm_sign + 1e-12))

    # ── Sign balance ──────────────────────────────────────────
    n_pos = float(np.sum(W_flat > 0))
    n_neg = float(np.sum(W_flat < 0))
    sign_balance = n_pos / max(n_neg, 1)

    # ── Magnitude statistics ──────────────────────────────────
    mag_mean = float(np.mean(abs_W))
    mag_std = float(np.std(abs_W))
    magnitude_cv = mag_std / max(mag_mean, 1e-12)

    # ── Sparsity ──────────────────────────────────────────────
    threshold = 0.01 * max(mag_mean, 1e-8)
    sparsity_01 = float(np.mean(abs_W < threshold))

    # ── Effective rank (via row-norm CV proxy) ────────────────
    if W.ndim >= 2:
        W_2d = W.reshape(-1, W.shape[-1]) if W.ndim > 2 else W
        row_norms = np.sqrt(np.sum(W_2d * W_2d, axis=-1) + 1e-12)
        row_norm_mean = float(np.mean(row_norms))
        row_norm_std = float(np.std(row_norms))
        row_cv = row_norm_std / max(row_norm_mean, 1e-12)
        effective_rank_ratio = 1.0 / (1.0 + row_cv)
    else:
        effective_rank_ratio = 1.0

    # ── Combined holographic score ────────────────────────────
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


MODELS = {
    "qwen36": {
        "hf_name": "Qwen/Qwen3.6-35B-A3B",
        "source": "hf",
        "description": "Qwen3.6-35B-A3B MoE — 40L, 256 experts × 8 active, "
                       "hybrid attention. Primary target for V12 sieve.",
    },
    "qwen32b": {
        "hf_name": "Qwen/Qwen3-32B",
        "path": "/Users/mwhitford/localai/models/Qwen3-32B-Q8_0.gguf",
        "source": "gguf",
        "description": "Qwen3-32B dense — 64L, original combinator hologram target.",
    },
    "pythia": {
        "hf_name": "EleutherAI/pythia-160m-deduped",
        "source": "hf",
        "description": "Pythia-160M — 12L, fast cross-architecture validation.",
    },
}


def load_model_weights(model_name: str) -> dict[str, np.ndarray]:
    """Load model weights as a flat dict of name → numpy array.

    Uses transformers + PyTorch, same as existing explore probes.
    Weights are moved to CPU and converted to numpy for analysis.
    """
    from transformers import AutoModelForCausalLM

    cfg = MODELS[model_name]
    hf_name = cfg["hf_name"]
    source = cfg["source"]

    print(f"Loading {hf_name} ({source})...", file=sys.stderr)
    if "description" in cfg:
        print(f"  {cfg['description']}", file=sys.stderr)

    if source == "gguf" and "path" in cfg:
        gguf_path = Path(cfg["path"])
        model = AutoModelForCausalLM.from_pretrained(
            str(gguf_path.parent),
            gguf_file=gguf_path.name,
            torch_dtype=torch.float16,
            device_map="cpu",
            trust_remote_code=True,
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            hf_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
        )

    model.eval()

    # Extract all named parameters as numpy arrays
    weights = {}
    for name, param in model.named_parameters():
        weights[name] = param.detach().cpu().float().numpy()

    # Count
    total_params = sum(w.size for w in weights.values())
    print(f"  {len(weights)} parameter tensors, {total_params:,} total params",
          file=sys.stderr)

    # Free the model
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    if hasattr(torch, 'mps') and hasattr(torch.mps, 'empty_cache'):
        torch.mps.empty_cache()

    return weights


# ══════════════════════════════════════════════════════════════════════
# Landscape analysis
# ══════════════════════════════════════════════════════════════════════


def analyze_landscape(
    weights: dict[str, np.ndarray],
    min_params: int = 1024,
) -> list[HolographicMetrics]:
    """Compute holographic metrics for all weight matrices.

    Args:
        weights: flat dict of parameter name → numpy array
        min_params: skip matrices smaller than this (biases, norms, etc.)

    Returns: list of HolographicMetrics, sorted by holographic_score descending.
    """
    results = []
    total_params = 0
    skipped = 0
    n_total = len(weights)

    for idx, (name, W) in enumerate(sorted(weights.items())):
        n = W.size
        total_params += n

        # Skip tiny params (biases, norms, scalars)
        if n < min_params:
            skipped += 1
            continue

        # Skip normalization layers (weight is a scale, not holographic)
        if any(skip in name for skip in ['layernorm', 'layer_norm', 'rmsnorm',
                                          'norm.weight', 'norm.bias']):
            skipped += 1
            continue

        metrics = compute_holographic_metrics(name, W)
        results.append(metrics)

        # Progress
        if (idx + 1) % 50 == 0 or idx == n_total - 1:
            print(f"  [{idx+1}/{n_total}] {name}: score={metrics.holographic_score:.3f}",
                  file=sys.stderr)

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
        choices=list(MODELS.keys()),
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
