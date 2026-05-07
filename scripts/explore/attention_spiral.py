#!/usr/bin/env python3
"""Attention spiral exploration — Qwen3-4B.

Hypothesis: standard transformer attention, when plotted, reveals a
logarithmic spiral pattern with expansion factor ~1.18 around a
fixed point at ~40 tokens distance.

This script:
  1. Loads Qwen3-4B with output_attentions=True
  2. Runs diverse prompts through the model
  3. Extracts attention weights from all 36 layers × 32 heads
  4. Produces several visualizations to reveal spiral structure
  5. Estimates spiral parameters (expansion factor, fixed point)

Usage:
    uv run python scripts/explore/attention_spiral.py
    uv run python scripts/explore/attention_spiral.py --quick     # 1 prompt, fast
    uv run python scripts/explore/attention_spiral.py --device mps # force device

Output: outputs/attention_spiral/

License: MIT
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import seaborn as sns
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ══════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════

MODEL_NAME = "Qwen/Qwen3-4B"
OUTPUT_DIR = Path("outputs/attention_spiral")

# Diverse prompts — different content types, lengths, structures
PROMPTS = [
    # Natural language — narrative
    "The old lighthouse keeper watched the storm approach from the west. "
    "Dark clouds gathered over the harbor as fishing boats hurried back to shore. "
    "He had seen a thousand storms, but something about this one felt different. "
    "The barometric pressure had dropped faster than he'd ever recorded, and the "
    "wind shifted from southwest to due north in less than an hour.",

    # Natural language — expository
    "Photosynthesis is the process by which plants convert sunlight into chemical "
    "energy. During the light-dependent reactions, chlorophyll absorbs photons and "
    "uses their energy to split water molecules, releasing oxygen as a byproduct. "
    "The electrons freed from water are passed along an electron transport chain, "
    "generating ATP and NADPH that power the Calvin cycle.",

    # Code-like / structured
    "def fibonacci(n):\n    if n <= 1:\n        return n\n    a, b = 0, 1\n"
    "    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b\n\n"
    "result = fibonacci(10)\nprint(f'The 10th Fibonacci number is {result}')\n"
    "# Output: The 10th Fibonacci number is 55",

    # Dialogue / conversational
    "\"Have you ever been to Tokyo?\" she asked, stirring her coffee. "
    "\"Once, about ten years ago,\" he replied. \"The cherry blossoms were in bloom. "
    "Every park was filled with families having picnics under the trees.\" "
    "\"I've always wanted to see that,\" she said quietly. \"My grandmother grew up "
    "near Ueno Park. She used to tell me stories about the festivals.\"",

    # Mathematical / formal
    "Consider the function f(x) = x^3 - 3x + 1. To find its critical points, "
    "we compute f'(x) = 3x^2 - 3 = 0, giving x = ±1. At x = -1, f(-1) = 3, "
    "which is a local maximum. At x = 1, f(1) = -1, which is a local minimum. "
    "The inflection point occurs where f''(x) = 6x = 0, i.e., at x = 0.",

    # Lambda / compositional (verbum-relevant)
    "λx. λy. apply(compose(f, g), pair(x, y)) → λz. f(g(z)) "
    "where compose ≡ λf. λg. λx. f(g(x)) and pair ≡ λa. λb. λs. s(a)(b) "
    "the Church encoding reduces: pair(true)(false)(λx.λy.x) → true "
    "because (λs. s(true)(false))(λx.λy.x) → (λx.λy.x)(true)(false) → true",

    # Long narrative — gives distance >100 tokens to observe
    "The history of mathematics is a story of abstraction. The ancient Babylonians "
    "developed arithmetic for commerce and astronomy. The Greeks introduced proof "
    "and axiomatic reasoning — Euclid's Elements remained the gold standard for "
    "over two thousand years. In the Renaissance, algebra emerged from practical "
    "problems of inheritance and trade. Newton and Leibniz independently invented "
    "calculus to describe motion and change. The nineteenth century brought a "
    "revolution in rigor: Cauchy formalized limits, Weierstrass eliminated "
    "infinitesimals, and Dedekind constructed the real numbers from rationals. "
    "Set theory, born from Cantor's investigations of infinity, provided a "
    "foundation — but also paradoxes. Russell's paradox shook the foundations, "
    "leading to Zermelo-Fraenkel axioms and the formalist program of Hilbert. "
    "Gödel's incompleteness theorems showed that any sufficiently powerful "
    "consistent system must contain true statements it cannot prove. Turing "
    "formalized computation, showing what functions are computable and discovering "
    "the halting problem. Church independently developed the lambda calculus, "
    "providing an equivalent model of computation based on function abstraction "
    "and application. The lambda calculus turned out to be far more than a "
    "theoretical curiosity — it became the foundation of functional programming "
    "languages and influenced the design of type systems, proof assistants, and "
    "the very large language models we use today.",
]


# ══════════════════════════════════════════════════════════════════
# Model loading
# ══════════════════════════════════════════════════════════════════


def load_model(device: str = "auto"):
    """Load Qwen3-4B with attention output enabled."""
    print(f"Loading {MODEL_NAME}...")
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME, trust_remote_code=True
    )

    # Determine device
    if device == "auto":
        if torch.backends.mps.is_available():
            device = "mps"
        elif torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"

    print(f"  Device: {device}")

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        torch_dtype=torch.float16 if device != "cpu" else torch.float32,
        attn_implementation="eager",  # need full attention matrices
    )
    model = model.to(device)
    model.eval()

    elapsed = time.time() - t0
    print(f"  Loaded in {elapsed:.1f}s")
    print(f"  Layers: {model.config.num_hidden_layers}")
    print(f"  Heads: {model.config.num_attention_heads}")
    print(f"  KV heads: {model.config.num_key_value_heads}")

    return model, tokenizer, device


# ══════════════════════════════════════════════════════════════════
# Attention extraction
# ══════════════════════════════════════════════════════════════════


def extract_attention(model, tokenizer, text: str, device: str) -> dict:
    """Run a prompt and extract attention weights from all layers.

    Returns dict with:
      tokens: list of token strings
      attention: list of (n_heads, seq_len, seq_len) arrays per layer
      seq_len: int
    """
    inputs = tokenizer(text, return_tensors="pt").to(device)
    seq_len = inputs["input_ids"].shape[1]

    with torch.no_grad():
        outputs = model(**inputs, output_attentions=True)

    # outputs.attentions is a tuple of (batch, n_heads, seq_len, seq_len)
    attention = []
    for layer_attn in outputs.attentions:
        # Remove batch dim, move to CPU, convert to float32 numpy
        attn_np = layer_attn[0].float().cpu().numpy()  # (n_heads, L, L)
        attention.append(attn_np)

    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])

    return {
        "tokens": tokens,
        "attention": attention,  # list of (H, L, L) arrays
        "seq_len": seq_len,
        "n_layers": len(attention),
        "n_heads": attention[0].shape[0],
    }


# ══════════════════════════════════════════════════════════════════
# Analysis functions
# ══════════════════════════════════════════════════════════════════


def compute_distance_profile(attention_data: dict) -> np.ndarray:
    """Compute attention mass as a function of distance, per layer.

    For each layer, average across heads and query positions:
      profile[layer, d] = mean attention weight at distance d

    Distance d = query_pos - key_pos (causal, so d >= 0).

    Returns: (n_layers, max_distance) array
    """
    n_layers = attention_data["n_layers"]
    seq_len = attention_data["seq_len"]

    # Max distance is seq_len - 1
    profiles = np.zeros((n_layers, seq_len))

    for layer_idx, attn in enumerate(attention_data["attention"]):
        # attn shape: (H, L, L)
        # Average across heads
        attn_mean = attn.mean(axis=0)  # (L, L)

        # For each query position q, attention to key position k
        # distance = q - k (causal: k <= q)
        for d in range(seq_len):
            # Collect attention weights at distance d
            # query positions q from d to seq_len-1, key position q-d
            weights = []
            for q in range(d, seq_len):
                weights.append(attn_mean[q, q - d])
            if weights:
                profiles[layer_idx, d] = np.mean(weights)

    return profiles


def compute_per_head_centroid(attention_data: dict) -> np.ndarray:
    """Compute the attention centroid (mean attended distance) per head per layer.

    centroid[layer, head] = Σ_d (d × attention_weight_at_d) / Σ attention

    Returns: (n_layers, n_heads) array
    """
    n_layers = attention_data["n_layers"]
    n_heads = attention_data["n_heads"]
    seq_len = attention_data["seq_len"]

    centroids = np.zeros((n_layers, n_heads))

    for layer_idx, attn in enumerate(attention_data["attention"]):
        for head_idx in range(n_heads):
            head_attn = attn[head_idx]  # (L, L)
            total_weighted_dist = 0.0
            total_weight = 0.0

            for q in range(seq_len):
                for k in range(q + 1):  # causal: k <= q
                    d = q - k
                    w = head_attn[q, k]
                    total_weighted_dist += d * w
                    total_weight += w

            if total_weight > 0:
                centroids[layer_idx, head_idx] = total_weighted_dist / total_weight

    return centroids


def compute_layer_centroid(attention_data: dict) -> np.ndarray:
    """Mean attention distance per layer (averaged across heads and positions).

    Returns: (n_layers,) array
    """
    centroids = compute_per_head_centroid(attention_data)
    return centroids.mean(axis=1)


def compute_cumulative_receptive_field(attention_data: dict) -> np.ndarray:
    """For each layer, compute the distance at which 50% of attention mass
    has been accumulated (median attention distance).

    Returns: (n_layers,) array
    """
    profiles = compute_distance_profile(attention_data)
    n_layers = profiles.shape[0]
    medians = np.zeros(n_layers)

    for layer_idx in range(n_layers):
        prof = profiles[layer_idx]
        cumsum = np.cumsum(prof)
        if cumsum[-1] > 0:
            cumsum_norm = cumsum / cumsum[-1]
            # Find first distance where cumulative >= 0.5
            median_idx = np.searchsorted(cumsum_norm, 0.5)
            medians[layer_idx] = median_idx

    return medians


def estimate_spiral_params(layer_centroids: np.ndarray) -> dict:
    """Estimate spiral parameters from per-layer centroids.

    If attention expands as a spiral: centroid(layer) ≈ r₀ × expansion^layer
    In log space: log(centroid) ≈ log(r₀) + layer × log(expansion)

    Also estimate fixed point as the centroid value that appears most stable.

    Returns dict with expansion_factor, fixed_point, r_squared, raw data.
    """
    n_layers = len(layer_centroids)
    layers = np.arange(n_layers)

    # Filter out zeros/tiny values for log fitting
    valid = layer_centroids > 0.5
    if valid.sum() < 3:
        return {"expansion_factor": None, "fixed_point": None,
                "r_squared": 0, "layer_centroids": layer_centroids}

    log_centroids = np.log(layer_centroids[valid])
    valid_layers = layers[valid]

    # Linear fit in log space
    coeffs = np.polyfit(valid_layers, log_centroids, 1)
    slope, intercept = coeffs
    expansion = np.exp(slope)
    r0 = np.exp(intercept)

    # R² goodness of fit
    predicted = slope * valid_layers + intercept
    ss_res = np.sum((log_centroids - predicted) ** 2)
    ss_tot = np.sum((log_centroids - np.mean(log_centroids)) ** 2)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

    # Fixed point: where does the expansion stabilize?
    # Look at the derivative of centroids — where it's closest to zero
    diffs = np.diff(layer_centroids)
    # Smooth
    if len(diffs) >= 5:
        kernel = np.ones(5) / 5
        smoothed_diffs = np.convolve(diffs, kernel, mode='valid')
        fixed_point_layer = np.argmin(np.abs(smoothed_diffs)) + 2  # offset for convolution
        fixed_point_dist = layer_centroids[fixed_point_layer]
    else:
        fixed_point_layer = len(layer_centroids) // 2
        fixed_point_dist = layer_centroids[fixed_point_layer]

    # Also compute per-layer expansion ratios
    ratios = []
    for i in range(1, n_layers):
        if layer_centroids[i - 1] > 0.5:
            ratios.append(layer_centroids[i] / layer_centroids[i - 1])
    mean_ratio = np.mean(ratios) if ratios else None

    return {
        "expansion_factor_fit": float(expansion),
        "expansion_factor_mean_ratio": float(mean_ratio) if mean_ratio else None,
        "r0": float(r0),
        "r_squared": float(r_squared),
        "fixed_point_layer": int(fixed_point_layer),
        "fixed_point_distance": float(fixed_point_dist),
        "per_layer_ratios": [float(r) for r in ratios],
        "layer_centroids": layer_centroids.tolist(),
    }


# ══════════════════════════════════════════════════════════════════
# Visualization
# ══════════════════════════════════════════════════════════════════


def plot_distance_heatmap(profiles: np.ndarray, title: str, path: Path,
                          max_dist: int = 128):
    """Heatmap: layer (y) × distance (x), showing attention mass distribution."""
    fig, ax = plt.subplots(figsize=(14, 8))

    # Clip to max_dist for visibility
    data = profiles[:, :max_dist]

    # Log scale for visibility (attention drops fast with distance)
    data_log = np.log10(data + 1e-10)

    im = ax.imshow(data_log, aspect="auto", origin="lower",
                   cmap="magma", interpolation="nearest")
    ax.set_xlabel("Distance (tokens)")
    ax.set_ylabel("Layer")
    ax.set_title(title)

    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("log₁₀(attention weight)")

    # Mark distance=40 with vertical line
    ax.axvline(x=40, color="cyan", linestyle="--", alpha=0.7, label="d=40")
    ax.legend(loc="upper right")

    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_centroid_evolution(centroids_per_prompt: list[np.ndarray],
                           prompt_labels: list[str], path: Path):
    """Line plot: attention centroid distance vs layer, per prompt."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Left: linear scale
    ax = axes[0]
    for centroids, label in zip(centroids_per_prompt, prompt_labels):
        ax.plot(centroids, label=label, alpha=0.8, linewidth=1.5)
    ax.axhline(y=40, color="red", linestyle="--", alpha=0.5, label="d=40 (hypothesized fixed point)")
    ax.set_xlabel("Layer")
    ax.set_ylabel("Mean attention distance (tokens)")
    ax.set_title("Attention centroid vs layer (linear)")
    ax.legend(fontsize=7, loc="upper left")
    ax.grid(True, alpha=0.3)

    # Right: log scale
    ax = axes[1]
    for centroids, label in zip(centroids_per_prompt, prompt_labels):
        ax.plot(centroids, label=label, alpha=0.8, linewidth=1.5)
    ax.axhline(y=40, color="red", linestyle="--", alpha=0.5, label="d=40")
    ax.set_xlabel("Layer")
    ax.set_ylabel("Mean attention distance (tokens) — log scale")
    ax.set_title("Attention centroid vs layer (log)")
    ax.set_yscale("log")
    ax.legend(fontsize=7, loc="upper left")
    ax.grid(True, alpha=0.3)

    fig.suptitle("Attention distance expansion across layers", fontsize=14)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_expansion_ratios(all_params: list[dict], prompt_labels: list[str],
                          path: Path):
    """Plot per-layer expansion ratios, looking for convergence to ~1.18."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Left: per-layer ratios
    ax = axes[0]
    for params, label in zip(all_params, prompt_labels):
        ratios = params["per_layer_ratios"]
        ax.plot(range(1, len(ratios) + 1), ratios, label=label, alpha=0.7)

    ax.axhline(y=1.18, color="red", linestyle="--", linewidth=2,
               alpha=0.8, label="1.18 (hypothesized)")
    ax.axhline(y=1.0, color="gray", linestyle=":", alpha=0.5, label="1.0 (no expansion)")
    ax.set_xlabel("Layer")
    ax.set_ylabel("Centroid ratio (layer n / layer n-1)")
    ax.set_title("Per-layer expansion ratio")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0.5, 2.0)

    # Right: running mean of ratios
    ax = axes[1]
    for params, label in zip(all_params, prompt_labels):
        ratios = np.array(params["per_layer_ratios"])
        if len(ratios) >= 5:
            kernel = np.ones(5) / 5
            smoothed = np.convolve(ratios, kernel, mode="valid")
            ax.plot(range(3, 3 + len(smoothed)), smoothed, label=label, alpha=0.8)

    ax.axhline(y=1.18, color="red", linestyle="--", linewidth=2,
               alpha=0.8, label="1.18 (hypothesized)")
    ax.axhline(y=1.0, color="gray", linestyle=":", alpha=0.5)
    ax.set_xlabel("Layer")
    ax.set_ylabel("Smoothed expansion ratio (5-layer window)")
    ax.set_title("Smoothed expansion ratio")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0.8, 1.5)

    fig.suptitle("Expansion factor analysis — looking for ~1.18", fontsize=14)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_polar_spiral(attention_data: dict, title: str, path: Path):
    """Polar plot of attention patterns — looking for spiral structure.

    Maps (layer, distance) → (θ, r):
      θ = layer × (2π / n_layers)   — one full revolution across all layers
      r = attention centroid distance at that layer

    If there's a spiral, points will trace a smooth expanding curve.
    """
    centroids = compute_layer_centroid(attention_data)
    n_layers = len(centroids)

    # Map layers to angles — try different rotations
    fig, axes = plt.subplots(1, 3, figsize=(18, 6),
                             subplot_kw={"projection": "polar"})

    for ax_idx, (n_revolutions, label) in enumerate([
        (1, "1 revolution"),
        (2, "2 revolutions"),
        (0.5, "½ revolution"),
    ]):
        ax = axes[ax_idx]
        theta = np.linspace(0, 2 * np.pi * n_revolutions, n_layers)

        # Color by layer depth
        colors = plt.cm.viridis(np.linspace(0, 1, n_layers))

        ax.scatter(theta, centroids, c=colors, s=30, zorder=5)
        ax.plot(theta, centroids, alpha=0.4, linewidth=1, color="gray")

        # Mark the 40-token circle
        theta_circle = np.linspace(0, 2 * np.pi, 100)
        ax.plot(theta_circle, [40] * 100, "r--", alpha=0.3, linewidth=1)

        ax.set_title(f"{label}\n{title}", fontsize=9, pad=15)
        ax.set_rmax(max(centroids) * 1.2 + 5)

    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_head_centroid_heatmap(attention_data: dict, title: str, path: Path):
    """Heatmap of per-head attention centroid: layer × head.

    Reveals which heads attend locally vs. globally, and whether
    there's structured progression.
    """
    centroids = compute_per_head_centroid(attention_data)  # (layers, heads)

    fig, ax = plt.subplots(figsize=(14, 8))
    im = ax.imshow(centroids, aspect="auto", origin="lower",
                   cmap="inferno", interpolation="nearest")
    ax.set_xlabel("Head")
    ax.set_ylabel("Layer")
    ax.set_title(f"Per-head attention centroid distance\n{title}")

    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Mean attention distance (tokens)")

    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_distance_profile_curves(profiles_per_prompt: list[np.ndarray],
                                 prompt_labels: list[str], path: Path,
                                 layers_to_show: list[int] | None = None):
    """Log-log plot of attention vs distance for selected layers.

    If attention follows a power law with distance, this will be linear.
    If it follows a log-spiral, we'll see characteristic curvature.
    """
    n_layers = profiles_per_prompt[0].shape[0]
    if layers_to_show is None:
        # Show layers 0, 6, 12, 18, 24, 30, 35
        layers_to_show = [0, 6, 12, 18, 24, 30, min(35, n_layers - 1)]

    fig, axes = plt.subplots(2, len(layers_to_show), figsize=(4 * len(layers_to_show), 8))

    for col, layer_idx in enumerate(layers_to_show):
        # Top row: linear
        ax = axes[0, col]
        for profiles, label in zip(profiles_per_prompt, prompt_labels):
            prof = profiles[layer_idx, 1:80]  # skip d=0 (self-attention)
            ax.plot(range(1, len(prof) + 1), prof, alpha=0.6, linewidth=1)
        ax.set_title(f"Layer {layer_idx}", fontsize=9)
        ax.set_xlabel("Distance")
        if col == 0:
            ax.set_ylabel("Attention weight")
        ax.grid(True, alpha=0.3)

        # Bottom row: log-log
        ax = axes[1, col]
        for profiles, label in zip(profiles_per_prompt, prompt_labels):
            prof = profiles[layer_idx, 1:80]
            distances = np.arange(1, len(prof) + 1)
            valid = prof > 1e-8
            if valid.any():
                ax.loglog(distances[valid], prof[valid], alpha=0.6, linewidth=1)
        ax.set_xlabel("Distance (log)")
        if col == 0:
            ax.set_ylabel("Attention weight (log)")
        ax.grid(True, alpha=0.3)

    fig.suptitle("Attention decay curves by layer (top: linear, bottom: log-log)",
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_aggregate_spiral(all_centroids: list[np.ndarray],
                          all_medians: list[np.ndarray],
                          prompt_labels: list[str], path: Path):
    """Aggregate view: mean centroid and median across all prompts,
    with confidence bands. The core spiral test."""
    centroids_stack = np.stack(all_centroids)  # (n_prompts, n_layers)
    medians_stack = np.stack(all_medians)

    mean_c = centroids_stack.mean(axis=0)
    std_c = centroids_stack.std(axis=0)
    mean_m = medians_stack.mean(axis=0)
    std_m = medians_stack.std(axis=0)

    layers = np.arange(len(mean_c))

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Left: centroid
    ax = axes[0]
    ax.plot(layers, mean_c, "b-", linewidth=2, label="Mean centroid")
    ax.fill_between(layers, mean_c - std_c, mean_c + std_c,
                    alpha=0.2, color="blue")
    ax.axhline(y=40, color="red", linestyle="--", alpha=0.7, label="d=40")

    # Overlay theoretical spiral: r = r0 * 1.18^layer
    r0_fit = mean_c[0] if mean_c[0] > 0.1 else 1.0
    theoretical = r0_fit * (1.18 ** layers)
    ax.plot(layers, theoretical, "r:", linewidth=1.5, alpha=0.6,
            label=f"r₀×1.18^L (r₀={r0_fit:.1f})")

    ax.set_xlabel("Layer")
    ax.set_ylabel("Mean attention distance")
    ax.set_title("Aggregate centroid (mean ± std across prompts)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Right: median
    ax = axes[1]
    ax.plot(layers, mean_m, "g-", linewidth=2, label="Mean median distance")
    ax.fill_between(layers, mean_m - std_m, mean_m + std_m,
                    alpha=0.2, color="green")
    ax.axhline(y=40, color="red", linestyle="--", alpha=0.7, label="d=40")
    ax.set_xlabel("Layer")
    ax.set_ylabel("Median attention distance")
    ax.set_title("Aggregate median distance (mean ± std across prompts)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.suptitle("Cross-prompt attention distance pattern", fontsize=14)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(description="Attention spiral exploration")
    parser.add_argument("--quick", action="store_true",
                        help="Use only 1 prompt for fast iteration")
    parser.add_argument("--device", default="auto",
                        help="Device: auto, cpu, mps, cuda")
    parser.add_argument("--max-dist-plot", type=int, default=128,
                        help="Max distance to show in heatmaps")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load model
    model, tokenizer, device = load_model(args.device)

    # Select prompts
    prompts = PROMPTS[:1] if args.quick else PROMPTS
    prompt_labels = [
        "narrative", "expository", "code", "dialogue", "math", "lambda",
        "long_narrative",
    ][:len(prompts)]

    # ── Extract attention from all prompts ────────────────────
    all_data = []
    all_profiles = []
    all_centroids = []
    all_medians = []
    all_params = []

    for i, (prompt, label) in enumerate(zip(prompts, prompt_labels)):
        print(f"\n{'─'*60}")
        print(f"Prompt {i+1}/{len(prompts)}: {label}")
        print(f"  Text: {prompt[:80]}...")
        print(f"  Extracting attention...")

        t0 = time.time()
        data = extract_attention(model, tokenizer, prompt, device)
        elapsed = time.time() - t0
        print(f"  Extracted in {elapsed:.1f}s  (seq_len={data['seq_len']})")

        # Compute profiles
        print(f"  Computing distance profiles...")
        profiles = compute_distance_profile(data)
        all_profiles.append(profiles)

        # Compute centroids
        print(f"  Computing centroids...")
        centroids = compute_layer_centroid(data)
        all_centroids.append(centroids)

        # Compute medians
        medians = compute_cumulative_receptive_field(data)
        all_medians.append(medians)

        # Estimate spiral params
        params = estimate_spiral_params(centroids)
        all_params.append(params)

        print(f"  Spiral estimate:")
        print(f"    expansion (fit):   {params['expansion_factor_fit']:.4f}" if params['expansion_factor_fit'] else "    expansion: N/A")
        print(f"    expansion (ratio): {params['expansion_factor_mean_ratio']:.4f}" if params['expansion_factor_mean_ratio'] else "    expansion: N/A")
        print(f"    R²:                {params['r_squared']:.4f}")
        print(f"    fixed point layer: {params['fixed_point_layer']}")
        print(f"    fixed point dist:  {params['fixed_point_distance']:.1f}")

        # Per-prompt plots
        plot_distance_heatmap(
            profiles, f"Attention distance profile — {label}",
            OUTPUT_DIR / f"heatmap_{label}.png",
            max_dist=args.max_dist_plot,
        )
        plot_polar_spiral(
            data, label,
            OUTPUT_DIR / f"polar_{label}.png",
        )
        plot_head_centroid_heatmap(
            data, label,
            OUTPUT_DIR / f"heads_{label}.png",
        )

        all_data.append(data)

    # ── Cross-prompt analysis ─────────────────────────────────
    print(f"\n{'═'*60}")
    print("Cross-prompt analysis")
    print(f"{'═'*60}")

    plot_centroid_evolution(
        all_centroids, prompt_labels,
        OUTPUT_DIR / "centroid_evolution.png",
    )

    plot_expansion_ratios(
        all_params, prompt_labels,
        OUTPUT_DIR / "expansion_ratios.png",
    )

    plot_distance_profile_curves(
        all_profiles, prompt_labels,
        OUTPUT_DIR / "distance_curves.png",
    )

    plot_aggregate_spiral(
        all_centroids, all_medians, prompt_labels,
        OUTPUT_DIR / "aggregate_spiral.png",
    )

    # ── Summary ───────────────────────────────────────────────
    print(f"\n{'═'*60}")
    print("SPIRAL PARAMETER SUMMARY")
    print(f"{'═'*60}")

    print(f"\n  {'prompt':15s} {'exp(fit)':>10} {'exp(ratio)':>12} {'R²':>8} {'FP layer':>10} {'FP dist':>10}")
    print(f"  {'─'*15} {'─'*10} {'─'*12} {'─'*8} {'─'*10} {'─'*10}")

    for label, params in zip(prompt_labels, all_params):
        ef = params['expansion_factor_fit']
        er = params['expansion_factor_mean_ratio']
        r2 = params['r_squared']
        fpl = params['fixed_point_layer']
        fpd = params['fixed_point_distance']
        print(f"  {label:15s} {ef:>10.4f} {er:>12.4f} {r2:>8.4f} {fpl:>10d} {fpd:>10.1f}")

    # Aggregate
    all_ef = [p['expansion_factor_fit'] for p in all_params if p['expansion_factor_fit']]
    all_er = [p['expansion_factor_mean_ratio'] for p in all_params if p['expansion_factor_mean_ratio']]
    all_fpd = [p['fixed_point_distance'] for p in all_params]

    if all_ef:
        print(f"\n  Aggregate:")
        print(f"    Mean expansion (fit):   {np.mean(all_ef):.4f} ± {np.std(all_ef):.4f}")
        print(f"    Mean expansion (ratio): {np.mean(all_er):.4f} ± {np.std(all_er):.4f}")
        print(f"    Mean fixed point dist:  {np.mean(all_fpd):.1f} ± {np.std(all_fpd):.1f}")
        print()
        print(f"    Hypothesis: expansion ≈ 1.18, fixed point ≈ 40")
        mean_exp = np.mean(all_ef)
        mean_fpd_val = np.mean(all_fpd)
        print(f"    Expansion deviation from 1.18: {abs(mean_exp - 1.18):.4f}")
        print(f"    Fixed point deviation from 40: {abs(mean_fpd_val - 40):.1f}")

    # Save numerical results
    results = {
        "model": MODEL_NAME,
        "n_prompts": len(prompts),
        "per_prompt": [
            {"label": label, **params}
            for label, params in zip(prompt_labels, all_params)
        ],
        "aggregate": {
            "mean_expansion_fit": float(np.mean(all_ef)) if all_ef else None,
            "std_expansion_fit": float(np.std(all_ef)) if all_ef else None,
            "mean_expansion_ratio": float(np.mean(all_er)) if all_er else None,
            "mean_fixed_point_distance": float(np.mean(all_fpd)),
            "std_fixed_point_distance": float(np.std(all_fpd)),
        },
    }
    results_path = OUTPUT_DIR / "spiral_params.json"
    results_path.write_text(json.dumps(results, indent=2))
    print(f"\n  Results saved: {results_path}")
    print(f"  Plots saved: {OUTPUT_DIR}/")
    print(f"\n{'═'*60}")


if __name__ == "__main__":
    main()
