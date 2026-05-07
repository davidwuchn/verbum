#!/usr/bin/env python3
"""3D spiral analysis of attention patterns — Qwen3-4B.

Hypothesis: the attention distance expansion of ~1.05/layer becomes
~1.18 per revolution when layers are arranged as a 3D helix with
~3.4 layers per revolution. The fixed point at ~40 tokens is the
axis of the helix.

This script:
  1. Loads attention data from the previous run (or re-extracts)
  2. Fits the optimal layers-per-revolution for a 3D helix
  3. Searches for periodicity in per-head attention centroids
  4. Produces 3D visualizations from multiple angles
  5. Tests whether the expansion per revolution converges to ~1.18

Usage:
    uv run python scripts/explore/attention_spiral_3d.py
    uv run python scripts/explore/attention_spiral_3d.py --quick

License: MIT
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

OUTPUT_DIR = Path("outputs/attention_spiral")
MODEL_NAME = "Qwen/Qwen3-4B"

# Reuse prompts from the first script
PROMPTS = [
    # narrative
    "The old lighthouse keeper watched the storm approach from the west. "
    "Dark clouds gathered over the harbor as fishing boats hurried back to shore. "
    "He had seen a thousand storms, but something about this one felt different. "
    "The barometric pressure had dropped faster than he'd ever recorded, and the "
    "wind shifted from southwest to due north in less than an hour.",

    # expository
    "Photosynthesis is the process by which plants convert sunlight into chemical "
    "energy. During the light-dependent reactions, chlorophyll absorbs photons and "
    "uses their energy to split water molecules, releasing oxygen as a byproduct. "
    "The electrons freed from water are passed along an electron transport chain, "
    "generating ATP and NADPH that power the Calvin cycle.",

    # code
    "def fibonacci(n):\n    if n <= 1:\n        return n\n    a, b = 0, 1\n"
    "    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b\n\n"
    "result = fibonacci(10)\nprint(f'The 10th Fibonacci number is {result}')\n"
    "# Output: The 10th Fibonacci number is 55",

    # dialogue
    "\"Have you ever been to Tokyo?\" she asked, stirring her coffee. "
    "\"Once, about ten years ago,\" he replied. \"The cherry blossoms were in bloom. "
    "Every park was filled with families having picnics under the trees.\" "
    "\"I've always wanted to see that,\" she said quietly. \"My grandmother grew up "
    "near Ueno Park. She used to tell me stories about the festivals.\"",

    # math
    "Consider the function f(x) = x^3 - 3x + 1. To find its critical points, "
    "we compute f'(x) = 3x^2 - 3 = 0, giving x = ±1. At x = -1, f(-1) = 3, "
    "which is a local maximum. At x = 1, f(1) = -1, which is a local minimum. "
    "The inflection point occurs where f''(x) = 6x = 0, i.e., at x = 0.",

    # lambda
    "λx. λy. apply(compose(f, g), pair(x, y)) → λz. f(g(z)) "
    "where compose ≡ λf. λg. λx. f(g(x)) and pair ≡ λa. λb. λs. s(a)(b) "
    "the Church encoding reduces: pair(true)(false)(λx.λy.x) → true "
    "because (λs. s(true)(false))(λx.λy.x) → (λx.λy.x)(true)(false) → true",

    # long narrative
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

PROMPT_LABELS = [
    "narrative", "expository", "code", "dialogue", "math", "lambda",
    "long_narrative",
]


# ══════════════════════════════════════════════════════════════════
# Model / extraction (reused from attention_spiral.py)
# ══════════════════════════════════════════════════════════════════


def load_model(device: str = "auto"):
    print(f"Loading {MODEL_NAME}...")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)

    if device == "auto":
        if torch.backends.mps.is_available():
            device = "mps"
        elif torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"

    print(f"  Device: {device}")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, trust_remote_code=True,
        torch_dtype=torch.float16 if device != "cpu" else torch.float32,
        attn_implementation="eager",
    ).to(device)
    model.eval()
    print(f"  Loaded in {time.time() - t0:.1f}s")
    return model, tokenizer, device


def extract_attention(model, tokenizer, text: str, device: str) -> dict:
    inputs = tokenizer(text, return_tensors="pt").to(device)
    seq_len = inputs["input_ids"].shape[1]
    with torch.no_grad():
        outputs = model(**inputs, output_attentions=True)
    attention = [layer_attn[0].float().cpu().numpy()
                 for layer_attn in outputs.attentions]
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    return {
        "tokens": tokens,
        "attention": attention,
        "seq_len": seq_len,
        "n_layers": len(attention),
        "n_heads": attention[0].shape[0],
    }


def compute_per_head_centroid(attention_data: dict) -> np.ndarray:
    """(n_layers, n_heads) — mean attention distance per head."""
    n_layers = attention_data["n_layers"]
    n_heads = attention_data["n_heads"]
    seq_len = attention_data["seq_len"]
    centroids = np.zeros((n_layers, n_heads))

    for li, attn in enumerate(attention_data["attention"]):
        for hi in range(n_heads):
            ha = attn[hi]
            total_wd = 0.0
            total_w = 0.0
            for q in range(seq_len):
                for k in range(q + 1):
                    d = q - k
                    w = ha[q, k]
                    total_wd += d * w
                    total_w += w
            if total_w > 0:
                centroids[li, hi] = total_wd / total_w
    return centroids


def compute_layer_centroid(attention_data: dict) -> np.ndarray:
    return compute_per_head_centroid(attention_data).mean(axis=1)


# ══════════════════════════════════════════════════════════════════
# 3D helix fitting
# ══════════════════════════════════════════════════════════════════


def fit_helix(centroids: np.ndarray, layers_per_rev_range: np.ndarray
              ) -> dict:
    """Try different layers-per-revolution and find the best helix fit.

    For each candidate LPR:
      θ(layer) = 2π × layer / LPR
      r(layer) = centroid(layer)  (the attention distance = radius)
      z(layer) = layer            (depth)

    A perfect logarithmic spiral satisfies:
      r(θ) = r₀ × exp(b × θ)

    In log space: ln(r) = ln(r₀) + b × θ
    We fit this and measure R².

    The expansion per revolution is exp(b × 2π).

    Returns best fit params.
    """
    n_layers = len(centroids)
    layers = np.arange(n_layers)

    # Filter valid centroids
    valid = centroids > 0.5
    if valid.sum() < 5:
        return {"best_lpr": None, "error": "too few valid centroids"}

    log_c = np.log(centroids[valid])
    valid_layers = layers[valid]

    results = []

    for lpr in layers_per_rev_range:
        theta = 2 * np.pi * valid_layers / lpr
        # Fit: log(r) = a + b*theta
        A = np.vstack([theta, np.ones(len(theta))]).T
        (b, a), residuals, _, _ = np.linalg.lstsq(A, log_c, rcond=None)

        # Predicted
        predicted = a + b * theta
        ss_res = np.sum((log_c - predicted) ** 2)
        ss_tot = np.sum((log_c - np.mean(log_c)) ** 2)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

        expansion_per_rev = np.exp(b * 2 * np.pi)
        r0 = np.exp(a)

        results.append({
            "lpr": float(lpr),
            "b": float(b),
            "r0": float(r0),
            "expansion_per_rev": float(expansion_per_rev),
            "r_squared": float(r_squared),
        })

    # Best by R²
    best = max(results, key=lambda x: x["r_squared"])

    # Also find which LPR gives expansion closest to 1.18
    closest_118 = min(results,
                      key=lambda x: abs(x["expansion_per_rev"] - 1.18))

    return {
        "best_fit": best,
        "closest_to_118": closest_118,
        "all_fits": results,
        "centroids": centroids.tolist(),
    }


def find_periodicity(per_head_centroids: np.ndarray) -> dict:
    """Look for periodic structure in per-head centroids across layers.

    Uses FFT on the mean centroid signal to find dominant frequencies.
    Also checks autocorrelation for periodic patterns.
    """
    # Mean across heads
    mean_signal = per_head_centroids.mean(axis=1)
    n = len(mean_signal)

    # Detrend (remove linear growth to find oscillation)
    x = np.arange(n)
    coeffs = np.polyfit(x, mean_signal, 1)
    trend = np.polyval(coeffs, x)
    detrended = mean_signal - trend

    # FFT
    fft = np.fft.rfft(detrended)
    freqs = np.fft.rfftfreq(n)
    magnitudes = np.abs(fft)
    # Skip DC component
    magnitudes[0] = 0

    # Top 5 frequencies
    top_indices = np.argsort(magnitudes)[::-1][:5]
    top_freqs = freqs[top_indices]
    top_mags = magnitudes[top_indices]
    top_periods = [1.0 / f if f > 0 else np.inf for f in top_freqs]

    # Autocorrelation
    autocorr = np.correlate(detrended, detrended, mode='full')
    autocorr = autocorr[n - 1:]  # positive lags only
    autocorr = autocorr / autocorr[0]  # normalize

    # Find first peak after lag 0
    peaks = []
    for i in range(2, min(len(autocorr) - 1, n // 2)):
        if autocorr[i] > autocorr[i - 1] and autocorr[i] > autocorr[i + 1]:
            peaks.append((i, float(autocorr[i])))
    peaks.sort(key=lambda x: -x[1])

    # Also do per-head FFT — look for heads with strong periodicity
    head_periodicities = []
    for hi in range(per_head_centroids.shape[1]):
        signal = per_head_centroids[:, hi]
        s_detrend = signal - np.polyval(np.polyfit(x, signal, 1), x)
        s_fft = np.fft.rfft(s_detrend)
        s_mags = np.abs(s_fft)
        s_mags[0] = 0
        dominant_idx = np.argmax(s_mags)
        dominant_freq = freqs[dominant_idx]
        dominant_period = 1.0 / dominant_freq if dominant_freq > 0 else np.inf
        head_periodicities.append({
            "head": hi,
            "dominant_period": float(dominant_period),
            "dominant_magnitude": float(s_mags[dominant_idx]),
        })

    return {
        "top_frequencies": [(float(f), float(m), float(p))
                            for f, m, p in zip(top_freqs, top_mags, top_periods)],
        "autocorrelation_peaks": peaks[:5],
        "head_periodicities": head_periodicities,
        "detrended_signal": detrended.tolist(),
        "autocorrelation": autocorr[:n // 2].tolist(),
    }


# ══════════════════════════════════════════════════════════════════
# Visualization
# ══════════════════════════════════════════════════════════════════


def plot_3d_helix(centroids: np.ndarray, lpr: float, title: str,
                  path: Path, expansion: float = None):
    """3D helix: x = r×cos(θ), y = r×sin(θ), z = layer."""
    n = len(centroids)
    layers = np.arange(n)
    theta = 2 * np.pi * layers / lpr
    r = centroids

    x = r * np.cos(theta)
    y = r * np.sin(theta)
    z = layers

    fig = plt.figure(figsize=(18, 6))

    # Three viewing angles
    views = [
        (30, -60, "Perspective"),
        (90, 0, "Top-down (spiral view)"),
        (0, 0, "Side view (expansion)"),
    ]

    for vi, (elev, azim, view_label) in enumerate(views):
        ax = fig.add_subplot(1, 3, vi + 1, projection="3d")

        # Color by layer
        colors = plt.cm.viridis(np.linspace(0, 1, n))

        # Plot the helix path
        ax.plot(x, y, z, alpha=0.3, color="gray", linewidth=0.8)

        # Plot points colored by layer
        ax.scatter(x, y, z, c=colors, s=25, zorder=5, depthshade=True)

        # Mark revolution boundaries
        for rev in range(int(n / lpr) + 1):
            boundary_layer = rev * lpr
            if boundary_layer < n:
                li = int(boundary_layer)
                ax.scatter([x[li]], [y[li]], [z[li]],
                           color="red", s=80, marker="*", zorder=10)

        # Draw the fixed point axis (r=40 circle at various z)
        theta_circle = np.linspace(0, 2 * np.pi, 100)
        for z_val in [0, n // 3, 2 * n // 3, n - 1]:
            ax.plot(40 * np.cos(theta_circle), 40 * np.sin(theta_circle),
                    z_val, color="red", alpha=0.15, linewidth=0.5)

        ax.set_xlabel("x = r·cos(θ)")
        ax.set_ylabel("y = r·sin(θ)")
        ax.set_zlabel("Layer")
        ax.view_init(elev=elev, azim=azim)

        exp_str = f", exp/rev={expansion:.3f}" if expansion else ""
        ax.set_title(f"{view_label}\nLPR={lpr:.1f}{exp_str}", fontsize=9)

    fig.suptitle(title, fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_helix_search(fit_results: dict, title: str, path: Path):
    """Plot R² and expansion-per-revolution as function of layers-per-revolution."""
    fits = fit_results["all_fits"]
    lprs = [f["lpr"] for f in fits]
    r2s = [f["r_squared"] for f in fits]
    expansions = [f["expansion_per_rev"] for f in fits]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left: R² vs LPR
    ax = axes[0]
    ax.plot(lprs, r2s, "b-", linewidth=1.5)
    best = fit_results["best_fit"]
    ax.axvline(x=best["lpr"], color="blue", linestyle="--", alpha=0.5,
               label=f"Best R²={best['r_squared']:.4f} at LPR={best['lpr']:.1f}")
    ax.set_xlabel("Layers per revolution")
    ax.set_ylabel("R² (log-spiral fit)")
    ax.set_title("Helix fit quality vs layers per revolution")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Right: expansion per rev vs LPR
    ax = axes[1]
    ax.plot(lprs, expansions, "g-", linewidth=1.5)
    ax.axhline(y=1.18, color="red", linestyle="--", linewidth=2,
               alpha=0.7, label="1.18 (hypothesized)")
    ax.axhline(y=1.0, color="gray", linestyle=":", alpha=0.5)
    c118 = fit_results["closest_to_118"]
    ax.axvline(x=c118["lpr"], color="orange", linestyle="--", alpha=0.5,
               label=f"exp≈1.18 at LPR={c118['lpr']:.1f} (R²={c118['r_squared']:.4f})")
    ax.set_xlabel("Layers per revolution")
    ax.set_ylabel("Expansion per revolution")
    ax.set_title("Expansion factor vs layers per revolution")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    fig.suptitle(title, fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_periodicity(period_data: dict, title: str, path: Path):
    """Plot FFT and autocorrelation of detrended attention centroid signal."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Top-left: detrended signal
    ax = axes[0, 0]
    signal = period_data["detrended_signal"]
    ax.plot(signal, "b-", linewidth=1)
    ax.axhline(y=0, color="gray", linestyle=":", alpha=0.5)
    ax.set_xlabel("Layer")
    ax.set_ylabel("Detrended centroid")
    ax.set_title("Detrended attention centroid (trend removed)")
    ax.grid(True, alpha=0.3)

    # Top-right: autocorrelation
    ax = axes[0, 1]
    ac = period_data["autocorrelation"]
    ax.plot(ac, "g-", linewidth=1)
    ax.axhline(y=0, color="gray", linestyle=":", alpha=0.5)
    # Mark peaks
    for lag, val in period_data["autocorrelation_peaks"][:3]:
        ax.plot(lag, val, "ro", markersize=8)
        ax.annotate(f"lag={lag}", (lag, val), textcoords="offset points",
                    xytext=(5, 5), fontsize=8)
    ax.set_xlabel("Lag (layers)")
    ax.set_ylabel("Autocorrelation")
    ax.set_title("Autocorrelation of detrended centroid")
    ax.grid(True, alpha=0.3)

    # Bottom-left: FFT magnitudes
    ax = axes[1, 0]
    freqs_and_mags = period_data["top_frequencies"]
    all_freqs = [f for f, m, p in freqs_and_mags]
    all_mags = [m for f, m, p in freqs_and_mags]
    all_periods = [p for f, m, p in freqs_and_mags]
    ax.bar(range(len(all_mags)), all_mags, color="purple", alpha=0.7)
    ax.set_xticks(range(len(all_mags)))
    ax.set_xticklabels([f"f={f:.3f}\nT={p:.1f}L" for f, _, p in freqs_and_mags],
                       fontsize=7)
    ax.set_ylabel("FFT magnitude")
    ax.set_title("Top 5 frequency components")

    # Bottom-right: per-head dominant periods
    ax = axes[1, 1]
    head_periods = [hp["dominant_period"] for hp in period_data["head_periodicities"]]
    head_mags = [hp["dominant_magnitude"] for hp in period_data["head_periodicities"]]
    # Cap infinite periods
    head_periods_capped = [min(p, 40) for p in head_periods]
    scatter = ax.scatter(range(len(head_periods_capped)), head_periods_capped,
                         c=head_mags, cmap="hot", s=40)
    ax.axhline(y=3.4, color="red", linestyle="--", alpha=0.5,
               label="3.4 layers (1.18 target)")
    ax.set_xlabel("Head index")
    ax.set_ylabel("Dominant period (layers)")
    ax.set_title("Per-head dominant periodicity")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.colorbar(scatter, ax=ax, label="FFT magnitude", shrink=0.8)

    fig.suptitle(title, fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_aggregate_3d(all_centroids: list[np.ndarray],
                      prompt_labels: list[str],
                      best_lpr: float, path: Path):
    """Overlay all prompts on one 3D helix plot."""
    fig = plt.figure(figsize=(16, 12))

    views = [
        (30, -60, "Perspective"),
        (90, 0, "Top-down (spiral view)"),
        (0, -90, "Side (layer vs radius)"),
        (0, 0, "Side (orthogonal)"),
    ]

    for vi, (elev, azim, view_label) in enumerate(views):
        ax = fig.add_subplot(2, 2, vi + 1, projection="3d")

        colors_prompt = plt.cm.tab10(np.linspace(0, 1, len(all_centroids)))

        for pi, (centroids, label) in enumerate(zip(all_centroids, prompt_labels)):
            n = len(centroids)
            layers = np.arange(n)
            theta = 2 * np.pi * layers / best_lpr
            r = centroids
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            z = layers

            ax.plot(x, y, z, alpha=0.5, color=colors_prompt[pi],
                    linewidth=1, label=label)
            ax.scatter(x, y, z, color=colors_prompt[pi], s=8,
                       alpha=0.6, depthshade=True)

        # Draw r=40 reference circles
        theta_circle = np.linspace(0, 2 * np.pi, 100)
        for z_val in [0, 12, 24, 35]:
            ax.plot(40 * np.cos(theta_circle), 40 * np.sin(theta_circle),
                    z_val, color="red", alpha=0.1, linewidth=0.5)

        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("Layer")
        ax.view_init(elev=elev, azim=azim)
        ax.set_title(f"{view_label}\nLPR={best_lpr:.1f}", fontsize=9)

        if vi == 0:
            ax.legend(fontsize=6, loc="upper left")

    fig.suptitle(f"All prompts on 3D helix (LPR={best_lpr:.1f})", fontsize=13)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_revolution_expansion(all_centroids: list[np.ndarray],
                              prompt_labels: list[str],
                              best_lpr: float, path: Path):
    """For each revolution of the helix, compute the expansion factor.

    If the spiral hypothesis holds, each revolution should expand by ~1.18.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    ax = axes[0]
    for centroids, label in zip(all_centroids, prompt_labels):
        n = len(centroids)
        lpr_int = max(1, int(round(best_lpr)))

        # Compute mean centroid per revolution
        rev_means = []
        rev_starts = list(range(0, n, lpr_int))
        for start in rev_starts:
            end = min(start + lpr_int, n)
            rev_means.append(np.mean(centroids[start:end]))

        # Expansion ratios between successive revolutions
        ratios = []
        for i in range(1, len(rev_means)):
            if rev_means[i - 1] > 0.5:
                ratios.append(rev_means[i] / rev_means[i - 1])

        ax.plot(range(1, len(ratios) + 1), ratios, "o-", label=label,
                alpha=0.7, markersize=5)

    ax.axhline(y=1.18, color="red", linestyle="--", linewidth=2,
               alpha=0.7, label="1.18 target")
    ax.axhline(y=1.0, color="gray", linestyle=":", alpha=0.5)
    ax.set_xlabel(f"Revolution number (1 rev = {int(round(best_lpr))} layers)")
    ax.set_ylabel("Expansion per revolution")
    ax.set_title("Per-revolution expansion factor")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0.8, 1.6)

    # Right: scan across different LPR values, show expansion
    ax = axes[1]
    lpr_candidates = np.arange(2, 13, 0.5)
    for centroids, label in zip(all_centroids, prompt_labels):
        n = len(centroids)
        mean_expansions = []
        for lpr in lpr_candidates:
            lpr_int = max(1, int(round(lpr)))
            rev_means = []
            for start in range(0, n, lpr_int):
                end = min(start + lpr_int, n)
                rev_means.append(np.mean(centroids[start:end]))
            ratios = []
            for i in range(1, len(rev_means)):
                if rev_means[i - 1] > 0.5:
                    ratios.append(rev_means[i] / rev_means[i - 1])
            mean_expansions.append(np.mean(ratios) if ratios else 1.0)
        ax.plot(lpr_candidates, mean_expansions, alpha=0.6, linewidth=1)

    ax.axhline(y=1.18, color="red", linestyle="--", linewidth=2, alpha=0.7,
               label="1.18 target")
    ax.set_xlabel("Layers per revolution")
    ax.set_ylabel("Mean expansion per revolution")
    ax.set_title("How LPR affects measured expansion")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    fig.suptitle("Revolution-based expansion analysis", fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(description="3D attention spiral analysis")
    parser.add_argument("--quick", action="store_true",
                        help="Use 2 prompts for fast iteration")
    parser.add_argument("--device", default="auto")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    model, tokenizer, device = load_model(args.device)

    prompts = PROMPTS[:2] if args.quick else PROMPTS
    labels = PROMPT_LABELS[:len(prompts)]

    # ── Extract attention ─────────────────────────────────────
    all_centroids = []
    all_per_head = []
    all_fit_results = []
    all_period_data = []

    lpr_range = np.arange(1.5, 18.5, 0.25)

    for i, (prompt, label) in enumerate(zip(prompts, labels)):
        print(f"\n{'─'*60}")
        print(f"Prompt {i+1}/{len(prompts)}: {label}")
        print(f"  Text: {prompt[:80]}...")

        t0 = time.time()
        data = extract_attention(model, tokenizer, prompt, device)
        print(f"  Extracted in {time.time() - t0:.1f}s (seq_len={data['seq_len']})")

        # Centroids
        print(f"  Computing centroids...")
        per_head = compute_per_head_centroid(data)
        centroids = per_head.mean(axis=1)
        all_centroids.append(centroids)
        all_per_head.append(per_head)

        # Helix fit
        print(f"  Fitting helix across LPR range...")
        fit = fit_helix(centroids, lpr_range)
        all_fit_results.append(fit)

        best = fit["best_fit"]
        c118 = fit["closest_to_118"]
        print(f"  Best fit:  LPR={best['lpr']:.1f}, exp/rev={best['expansion_per_rev']:.4f}, R²={best['r_squared']:.4f}")
        print(f"  Near 1.18: LPR={c118['lpr']:.1f}, exp/rev={c118['expansion_per_rev']:.4f}, R²={c118['r_squared']:.4f}")

        # Periodicity analysis
        print(f"  Analyzing periodicity...")
        period_data = find_periodicity(per_head)
        all_period_data.append(period_data)

        top_ac = period_data["autocorrelation_peaks"][:3]
        if top_ac:
            print(f"  Top autocorrelation peaks: {[(lag, f'{val:.3f}') for lag, val in top_ac]}")

        # Per-prompt 3D plots
        plot_3d_helix(
            centroids, best["lpr"],
            f"3D helix — {label} (best fit LPR={best['lpr']:.1f})",
            OUTPUT_DIR / f"helix3d_{label}_bestfit.png",
            expansion=best["expansion_per_rev"],
        )
        plot_3d_helix(
            centroids, c118["lpr"],
            f"3D helix — {label} (LPR for exp≈1.18 = {c118['lpr']:.1f})",
            OUTPUT_DIR / f"helix3d_{label}_at118.png",
            expansion=c118["expansion_per_rev"],
        )
        plot_helix_search(
            fit, f"Helix fit search — {label}",
            OUTPUT_DIR / f"helix_search_{label}.png",
        )
        plot_periodicity(
            period_data, f"Periodicity — {label}",
            OUTPUT_DIR / f"periodicity_{label}.png",
        )

    # ── Cross-prompt aggregate ────────────────────────────────
    print(f"\n{'═'*60}")
    print("Cross-prompt aggregate analysis")
    print(f"{'═'*60}")

    # Find consensus best LPR
    all_best_lprs = [f["best_fit"]["lpr"] for f in all_fit_results]
    all_118_lprs = [f["closest_to_118"]["lpr"] for f in all_fit_results]
    mean_best_lpr = np.mean(all_best_lprs)
    mean_118_lpr = np.mean(all_118_lprs)

    print(f"\n  Best-fit LPR per prompt: {[f'{x:.1f}' for x in all_best_lprs]}")
    print(f"  Mean best-fit LPR: {mean_best_lpr:.2f}")
    print(f"  LPR-for-1.18 per prompt: {[f'{x:.1f}' for x in all_118_lprs]}")
    print(f"  Mean LPR-for-1.18: {mean_118_lpr:.2f}")

    # Aggregate 3D plot
    plot_aggregate_3d(
        all_centroids, labels, mean_best_lpr,
        OUTPUT_DIR / "helix3d_aggregate_bestfit.png",
    )
    plot_aggregate_3d(
        all_centroids, labels, mean_118_lpr,
        OUTPUT_DIR / "helix3d_aggregate_at118.png",
    )

    # Revolution expansion analysis
    plot_revolution_expansion(
        all_centroids, labels, mean_best_lpr,
        OUTPUT_DIR / "revolution_expansion_bestfit.png",
    )
    plot_revolution_expansion(
        all_centroids, labels, mean_118_lpr,
        OUTPUT_DIR / "revolution_expansion_at118.png",
    )

    # ── Summary ───────────────────────────────────────────────
    print(f"\n{'═'*60}")
    print("3D SPIRAL PARAMETER SUMMARY")
    print(f"{'═'*60}")

    print(f"\n  {'prompt':15s} {'best LPR':>10} {'exp/rev':>10} {'R²':>8} {'LPR@1.18':>10} {'R²@1.18':>8}")
    print(f"  {'─'*15} {'─'*10} {'─'*10} {'─'*8} {'─'*10} {'─'*8}")

    for label, fit in zip(labels, all_fit_results):
        b = fit["best_fit"]
        c = fit["closest_to_118"]
        print(f"  {label:15s} {b['lpr']:>10.1f} {b['expansion_per_rev']:>10.4f} {b['r_squared']:>8.4f} {c['lpr']:>10.1f} {c['r_squared']:>8.4f}")

    print(f"\n  Aggregate:")
    print(f"    Mean best-fit LPR:  {mean_best_lpr:.2f} ± {np.std(all_best_lprs):.2f}")
    print(f"    Mean LPR for 1.18:  {mean_118_lpr:.2f} ± {np.std(all_118_lprs):.2f}")

    # Periodicity summary
    print(f"\n  Periodicity (autocorrelation top peak):")
    for label, pd in zip(labels, all_period_data):
        peaks = pd["autocorrelation_peaks"]
        if peaks:
            lag, val = peaks[0]
            print(f"    {label:15s}  lag={lag:3d} layers, r={val:.3f}")
        else:
            print(f"    {label:15s}  no peaks found")

    # Save results
    results = {
        "model": MODEL_NAME,
        "n_prompts": len(prompts),
        "lpr_search_range": [float(lpr_range[0]), float(lpr_range[-1])],
        "mean_best_lpr": float(mean_best_lpr),
        "mean_118_lpr": float(mean_118_lpr),
        "per_prompt": [],
    }
    for label, fit, pd in zip(labels, all_fit_results, all_period_data):
        results["per_prompt"].append({
            "label": label,
            "best_fit": fit["best_fit"],
            "closest_to_118": fit["closest_to_118"],
            "top_autocorrelation_peaks": pd["autocorrelation_peaks"][:3],
            "top_fft_periods": [
                {"freq": f, "magnitude": m, "period_layers": p}
                for f, m, p in pd["top_frequencies"]
            ],
        })

    results_path = OUTPUT_DIR / "spiral_3d_params.json"
    results_path.write_text(json.dumps(results, indent=2))
    print(f"\n  Results saved: {results_path}")
    print(f"  Plots saved: {OUTPUT_DIR}/")
    print(f"\n{'═'*60}")


if __name__ == "__main__":
    main()
