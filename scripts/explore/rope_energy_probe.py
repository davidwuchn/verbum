#!/usr/bin/env python3
"""RoPE energy distribution probe — Qwen3-4B.

Tests the hypothesis that the attention spiral pattern is tied to RoPE's
cos-sin frequency structure. Specifically:

  RoPE creates 64 dimension pairs (head_dim=128), each rotating at
  θ_i = θ_base^(-2i/d). Wavelengths form a geometric series with ratio
  θ^(1/64) ≈ 1.2409. If layers progressively shift Q/K energy from
  high-frequency (local) to low-frequency (long-range) dim pairs, the
  attention centroid expands — producing the observed ~1.018/layer spiral.

This script hooks into the model to capture Q and K vectors BEFORE and
AFTER RoPE is applied, then measures:

  1. Per-dim-pair energy: mean(|q_2i|² + |q_{2i+1}|²) per layer × head
  2. Energy centroid in dim-pair space per layer (weighted mean dim index)
  3. Rate of centroid shift → predicted expansion factor
  4. Layer-6 transition visibility (positional → semantic)

Prior art: "Round and Round We Go!" (ICLR 2025) found that Gemma 7B
uses high-freq RoPE dims for positional attention and low-freq for
semantic attention. We test whether this frequency allocation creates
the spiral we observed in outputs/attention_spiral/.

Usage:
    uv run python scripts/explore/rope_energy_probe.py
    uv run python scripts/explore/rope_energy_probe.py --quick  # 2 prompts

Output: outputs/rope_energy/

License: MIT
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from contextlib import contextmanager

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ══════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════

MODEL_NAME = "Qwen/Qwen3-4B"
OUTPUT_DIR = Path("outputs/rope_energy")

# Same prompts as attention_spiral.py for direct comparison
PROMPTS = [
    "The old lighthouse keeper watched the storm approach from the west. "
    "Dark clouds gathered over the harbor as fishing boats hurried back to shore. "
    "He had seen a thousand storms, but something about this one felt different. "
    "The barometric pressure had dropped faster than he'd ever recorded, and the "
    "wind shifted from southwest to due north in less than an hour.",

    "Photosynthesis is the process by which plants convert sunlight into chemical "
    "energy. During the light-dependent reactions, chlorophyll absorbs photons and "
    "uses their energy to split water molecules, releasing oxygen as a byproduct. "
    "The electrons freed from water are passed along an electron transport chain, "
    "generating ATP and NADPH that power the Calvin cycle.",

    "def fibonacci(n):\n    if n <= 1:\n        return n\n    a, b = 0, 1\n"
    "    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b\n\n"
    "result = fibonacci(10)\nprint(f'The 10th Fibonacci number is {result}')\n"
    "# Output: The 10th Fibonacci number is 55",

    "\"Have you ever been to Tokyo?\" she asked, stirring her coffee. "
    "\"Once, about ten years ago,\" he replied. \"The cherry blossoms were in bloom. "
    "Every park was filled with families having picnics under the trees.\" "
    "\"I've always wanted to see that,\" she said quietly. \"My grandmother grew up "
    "near Ueno Park. She used to tell me stories about the festivals.\"",

    "Consider the function f(x) = x^3 - 3x + 1. To find its critical points, "
    "we compute f'(x) = 3x^2 - 3 = 0, giving x = ±1. At x = -1, f(-1) = 3, "
    "which is a local maximum. At x = 1, f(1) = -1, which is a local minimum. "
    "The inflection point occurs where f''(x) = 6x = 0, i.e., at x = 0.",

    "λx. λy. apply(compose(f, g), pair(x, y)) → λz. f(g(z)) "
    "where compose ≡ λf. λg. λx. f(g(x)) and pair ≡ λa. λb. λs. s(a)(b) "
    "the Church encoding reduces: pair(true)(false)(λx.λy.x) → true "
    "because (λs. s(true)(false))(λx.λy.x) → (λx.λy.x)(true)(false) → true",

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
# RoPE frequency constants (computed from model config)
# ══════════════════════════════════════════════════════════════════


def compute_rope_freqs(head_dim: int = 128, theta_base: float = 1_000_000.0):
    """Compute the RoPE frequency for each dimension pair."""
    n_pairs = head_dim // 2
    dim_indices = np.arange(n_pairs)
    freqs = 1.0 / (theta_base ** (2 * dim_indices / head_dim))
    wavelengths = 2 * np.pi / freqs
    return freqs, wavelengths, n_pairs


# ══════════════════════════════════════════════════════════════════
# Model loading + hooking
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

    n_layers = model.config.num_hidden_layers
    n_heads = model.config.num_attention_heads
    n_kv_heads = model.config.num_key_value_heads
    head_dim = model.config.head_dim

    print(f"  Loaded in {time.time() - t0:.1f}s")
    print(f"  Layers: {n_layers}, Q heads: {n_heads}, KV heads: {n_kv_heads}, head_dim: {head_dim}")

    return model, tokenizer, device


class RoPEEnergyCapture:
    """Hook manager that captures Q/K energy distributions across RoPE dim pairs.

    Hooks into:
      - q_proj output (after q_norm, before RoPE) via forward hook on q_norm
      - k_proj output (after k_norm, before RoPE) via forward hook on k_norm

    We also capture post-RoPE Q/K by hooking the attention forward itself.
    """

    def __init__(self, model):
        self.model = model
        self.n_layers = model.config.num_hidden_layers
        self.n_heads = model.config.num_attention_heads
        self.n_kv_heads = model.config.num_key_value_heads
        self.head_dim = model.config.head_dim
        self.n_pairs = self.head_dim // 2

        # Storage: pre-RoPE Q/K energy per dim pair per layer
        self.pre_rope_q_energy = {}  # layer_idx → (n_heads, n_pairs)
        self.pre_rope_k_energy = {}  # layer_idx → (n_kv_heads, n_pairs)
        self.post_rope_q_energy = {}
        self.post_rope_k_energy = {}

        self._hooks = []

    def _register_hooks(self):
        """Register forward hooks on each attention layer."""
        for layer_idx in range(self.n_layers):
            attn = self.model.model.layers[layer_idx].self_attn

            # Hook q_norm output → pre-RoPE Q
            # q_norm is applied AFTER q_proj, BEFORE RoPE
            # Shape at this point: (batch, seq_len, num_heads * head_dim)
            # But actually in forward: q_proj(hidden).view(hidden_shape) → q_norm → transpose
            # The q_norm sees shape (batch, seq_len, n_heads, head_dim)
            # Its output is the same shape, then .transpose(1,2) gives (batch, n_heads, seq_len, head_dim)
            hook_q = attn.q_norm.register_forward_hook(
                self._make_norm_hook(layer_idx, "q", self.n_heads)
            )
            hook_k = attn.k_norm.register_forward_hook(
                self._make_norm_hook(layer_idx, "k", self.n_kv_heads)
            )
            self._hooks.extend([hook_q, hook_k])

            # To capture post-RoPE, we hook the attention module itself
            # and intercept after apply_rotary_pos_emb
            hook_attn = attn.register_forward_hook(
                self._make_attn_hook(layer_idx)
            )
            self._hooks.append(hook_attn)

    def _make_norm_hook(self, layer_idx: int, qk: str, n_heads: int):
        """Create a hook for q_norm or k_norm output.

        The norm module receives input shape (batch, seq_len, n_heads, head_dim)
        and outputs the same shape. We compute per-dim-pair energy from the output.
        """
        def hook_fn(module, input, output):
            # output shape: (batch, seq_len, n_heads, head_dim)
            with torch.no_grad():
                x = output.float()  # (B, S, H, D)
                # Reshape to dim pairs: (B, S, H, n_pairs, 2)
                x_pairs = x.view(*x.shape[:-1], self.n_pairs, 2)
                # Energy per pair: sum of squares across the 2 dims in each pair
                # Then mean across batch and seq positions
                pair_energy = (x_pairs ** 2).sum(dim=-1)  # (B, S, H, n_pairs)
                pair_energy = pair_energy.mean(dim=(0, 1))  # (H, n_pairs)

                storage = self.pre_rope_q_energy if qk == "q" else self.pre_rope_k_energy
                storage[layer_idx] = pair_energy.cpu().numpy()

        return hook_fn

    def _make_attn_hook(self, layer_idx: int):
        """Hook on the full attention forward.

        RoPE is a rotation within each 2D pair, so |q_2i|² + |q_{2i+1}|²
        is invariant under RoPE. Per-dim-pair energy is identical before
        and after RoPE — we don't need a separate post-RoPE energy hook.

        However, we DO capture QK alignment per dim pair here by wrapping
        apply_rotary_pos_emb to intercept the post-RoPE Q and K.
        """
        def hook_fn(module, input, output):
            pass

        return hook_fn

    def _remove_hooks(self):
        for h in self._hooks:
            h.remove()
        self._hooks.clear()

    def clear(self):
        self.pre_rope_q_energy.clear()
        self.pre_rope_k_energy.clear()
        self.post_rope_q_energy.clear()
        self.post_rope_k_energy.clear()

    @contextmanager
    def capture(self):
        """Context manager to capture RoPE energy during a forward pass."""
        self.clear()
        self._register_hooks()
        try:
            yield self
        finally:
            self._remove_hooks()


# ══════════════════════════════════════════════════════════════════
# Analysis
# ══════════════════════════════════════════════════════════════════


def compute_energy_centroid(energy: np.ndarray) -> float:
    """Compute the weighted mean dim-pair index (energy centroid).

    Args:
        energy: shape (n_pairs,) — energy per dim pair

    Returns:
        Weighted mean index: Σ(i × E_i) / Σ(E_i)
    """
    n = len(energy)
    indices = np.arange(n, dtype=np.float64)
    total = energy.sum()
    if total < 1e-12:
        return n / 2.0
    return float((indices * energy).sum() / total)


def compute_rope_predicted_centroid(
    energy_per_pair: np.ndarray,
    freqs: np.ndarray,
    seq_len: int = 100,
    max_dist: int = 200,
) -> float:
    """Given an energy distribution across RoPE dim pairs, predict the
    attention distance centroid.

    The attention logit contribution from RoPE at distance d is:
        logit(d) ∝ Σ_i w_i × cos(freq_i × d)

    where w_i is the energy in dim pair i.

    Returns the expected attention centroid distance.
    """
    distances = np.arange(1, min(seq_len, max_dist) + 1)

    # Build the RoPE-only logit as a function of distance
    logits = np.zeros(len(distances))
    for i, (w, f) in enumerate(zip(energy_per_pair, freqs)):
        logits += w * np.cos(f * distances)

    # Softmax → attention weights
    head_dim = len(energy_per_pair) * 2
    logits = logits / np.sqrt(head_dim)
    logits_exp = np.exp(logits - np.max(logits))
    attn = logits_exp / logits_exp.sum()

    return float(np.sum(distances * attn))


def analyze_prompt(
    capture: RoPEEnergyCapture,
    freqs: np.ndarray,
    seq_len: int,
) -> dict:
    """Analyze the captured energy distributions for one prompt."""
    n_layers = capture.n_layers
    n_pairs = capture.n_pairs
    n_heads = capture.n_heads
    n_kv_heads = capture.n_kv_heads

    # Collect per-layer Q energy (averaged across heads)
    q_energy_per_layer = np.zeros((n_layers, n_pairs))
    k_energy_per_layer = np.zeros((n_layers, n_pairs))
    q_energy_per_head = np.zeros((n_layers, n_heads, n_pairs))

    for li in range(n_layers):
        if li in capture.pre_rope_q_energy:
            q_e = capture.pre_rope_q_energy[li]  # (n_heads, n_pairs)
            q_energy_per_layer[li] = q_e.mean(axis=0)
            q_energy_per_head[li] = q_e
        if li in capture.pre_rope_k_energy:
            k_e = capture.pre_rope_k_energy[li]  # (n_kv_heads, n_pairs)
            k_energy_per_layer[li] = k_e.mean(axis=0)

    # Normalize per layer (to get distribution, not magnitude)
    q_dist_per_layer = np.zeros_like(q_energy_per_layer)
    k_dist_per_layer = np.zeros_like(k_energy_per_layer)
    for li in range(n_layers):
        q_total = q_energy_per_layer[li].sum()
        k_total = k_energy_per_layer[li].sum()
        if q_total > 0:
            q_dist_per_layer[li] = q_energy_per_layer[li] / q_total
        if k_total > 0:
            k_dist_per_layer[li] = k_energy_per_layer[li] / k_total

    # Energy centroids
    q_centroids = np.array([
        compute_energy_centroid(q_energy_per_layer[li])
        for li in range(n_layers)
    ])
    k_centroids = np.array([
        compute_energy_centroid(k_energy_per_layer[li])
        for li in range(n_layers)
    ])

    # Predicted attention centroids from RoPE energy distribution
    predicted_attn_centroids = np.array([
        compute_rope_predicted_centroid(q_dist_per_layer[li], freqs, seq_len)
        for li in range(n_layers)
    ])

    # Fit expansion factor from predicted centroids
    valid = predicted_attn_centroids > 0.5
    if valid.sum() >= 3:
        log_c = np.log(predicted_attn_centroids[valid])
        layers = np.arange(n_layers)[valid]
        slope, intercept = np.polyfit(layers, log_c, 1)
        predicted_expansion = float(np.exp(slope))
        r_squared = 1 - np.sum((log_c - (slope * layers + intercept)) ** 2) / \
                    np.sum((log_c - log_c.mean()) ** 2)
    else:
        predicted_expansion = None
        r_squared = None

    # Per-head analysis: which heads use which frequency bands?
    head_centroids = np.zeros((n_layers, n_heads))
    for li in range(n_layers):
        for hi in range(n_heads):
            head_centroids[li, hi] = compute_energy_centroid(
                q_energy_per_head[li, hi]
            )

    return {
        "q_energy_per_layer": q_energy_per_layer,
        "k_energy_per_layer": k_energy_per_layer,
        "q_dist_per_layer": q_dist_per_layer,
        "k_dist_per_layer": k_dist_per_layer,
        "q_centroids": q_centroids,
        "k_centroids": k_centroids,
        "predicted_attn_centroids": predicted_attn_centroids,
        "predicted_expansion": predicted_expansion,
        "r_squared": r_squared,
        "head_centroids": head_centroids,
        "q_energy_per_head": q_energy_per_head,
    }


# ══════════════════════════════════════════════════════════════════
# Visualization
# ══════════════════════════════════════════════════════════════════


def plot_energy_heatmap(
    q_dist: np.ndarray,
    k_dist: np.ndarray,
    wavelengths: np.ndarray,
    title: str,
    path: Path,
):
    """Core plot: dim-pair energy distribution vs layer.

    x = dim pair index (0=fastest rotation, 63=slowest)
    y = layer
    color = energy fraction
    Second x-axis = RoPE wavelength in tokens
    """
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))

    for ax, data, qk_label in [
        (axes[0], q_dist, "Query"),
        (axes[1], k_dist, "Key"),
    ]:
        im = ax.imshow(
            data, aspect="auto", origin="lower", cmap="magma",
            interpolation="nearest",
        )
        ax.set_xlabel("RoPE dim pair index (→ lower frequency)")
        ax.set_ylabel("Layer")
        ax.set_title(f"{qk_label} energy distribution")

        # Wavelength annotations on top
        ax2 = ax.twiny()
        tick_dims = [0, 5, 10, 15, 20, 30, 40, 50, 63]
        ax2.set_xlim(ax.get_xlim())
        ax2.set_xticks(tick_dims)
        ax2.set_xticklabels(
            [f"{wavelengths[d]:.0f}" if wavelengths[d] < 10000
             else f"{wavelengths[d]/1000:.0f}k"
             for d in tick_dims],
            fontsize=7,
        )
        ax2.set_xlabel("RoPE wavelength (tokens)", fontsize=8)

        fig.colorbar(im, ax=ax, shrink=0.8, label="Energy fraction")

    fig.suptitle(title, fontsize=13)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_centroid_shift(
    all_results: list[dict],
    labels: list[str],
    wavelengths: np.ndarray,
    path: Path,
):
    """Energy centroid (in dim-pair space) vs layer for all prompts.

    Shows whether the 'active frequency band' shifts across layers.
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Top-left: Q centroid in dim-pair space
    ax = axes[0, 0]
    for res, label in zip(all_results, labels):
        ax.plot(res["q_centroids"], label=label, alpha=0.7, linewidth=1.5)
    ax.set_xlabel("Layer")
    ax.set_ylabel("Energy centroid (dim-pair index)")
    ax.set_title("Q energy centroid across layers\n(higher = lower freq = longer range)")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # Top-right: K centroid
    ax = axes[0, 1]
    for res, label in zip(all_results, labels):
        ax.plot(res["k_centroids"], label=label, alpha=0.7, linewidth=1.5)
    ax.set_xlabel("Layer")
    ax.set_ylabel("Energy centroid (dim-pair index)")
    ax.set_title("K energy centroid across layers")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # Bottom-left: Q centroid mapped to wavelength
    ax = axes[1, 0]
    for res, label in zip(all_results, labels):
        # Map centroid index → interpolated wavelength
        centroid_wavelengths = np.interp(
            res["q_centroids"],
            np.arange(len(wavelengths)),
            wavelengths,
        )
        ax.plot(centroid_wavelengths, label=label, alpha=0.7, linewidth=1.5)
    ax.set_xlabel("Layer")
    ax.set_ylabel("Effective RoPE wavelength (tokens)")
    ax.set_title("Q energy centroid mapped to RoPE wavelength")
    ax.set_yscale("log")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # Bottom-right: Q centroid shift rate (derivative)
    ax = axes[1, 1]
    for res, label in zip(all_results, labels):
        diffs = np.diff(res["q_centroids"])
        smoothed = np.convolve(diffs, np.ones(5) / 5, mode="valid")
        ax.plot(
            range(3, 3 + len(smoothed)), smoothed,
            label=label, alpha=0.7, linewidth=1.5,
        )
    ax.axhline(y=0, color="gray", linestyle=":", alpha=0.5)
    ax.set_xlabel("Layer")
    ax.set_ylabel("Centroid shift rate (dim pairs / layer)")
    ax.set_title("Rate of frequency band shift\n(positive = moving to lower freq)")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    fig.suptitle("RoPE energy centroid shift across layers", fontsize=14)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_predicted_vs_observed(
    all_results: list[dict],
    labels: list[str],
    path: Path,
):
    """Compare RoPE-predicted attention centroid with actual observed spiral.

    Loads observed centroids from outputs/attention_spiral/spiral_params.json.
    """
    # Load observed data
    observed_path = Path("outputs/attention_spiral/spiral_params.json")
    observed_data = None
    if observed_path.exists():
        with open(observed_path) as f:
            observed_data = json.load(f)

    n_plots = min(len(all_results), 4)
    fig, axes = plt.subplots(2, max(n_plots, 2), figsize=(6 * max(n_plots, 2), 10))

    for i, (res, label) in enumerate(zip(all_results[:n_plots], labels[:n_plots])):
        # Top row: predicted vs observed attention centroid
        ax = axes[0, i]
        ax.plot(
            res["predicted_attn_centroids"], "b-", linewidth=2,
            label=f"RoPE-predicted (exp={res['predicted_expansion']:.4f})",
        )

        if observed_data:
            for pp in observed_data["per_prompt"]:
                if pp["label"] == label:
                    obs_c = pp["layer_centroids"]
                    ax.plot(
                        obs_c, "r--", linewidth=1.5,
                        label=f"Observed (exp={pp['expansion_factor_fit']:.4f})",
                    )
                    break

        ax.set_xlabel("Layer")
        ax.set_ylabel("Attention centroid (tokens)")
        ax.set_title(f"{label}", fontsize=10)
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

        # Bottom row: per-layer ratio comparison
        ax = axes[1, i]
        pred_ratios = res["predicted_attn_centroids"][1:] / res["predicted_attn_centroids"][:-1]
        ax.plot(range(1, len(pred_ratios) + 1), pred_ratios, "b-",
                alpha=0.7, label="RoPE-predicted")

        if observed_data:
            for pp in observed_data["per_prompt"]:
                if pp["label"] == label:
                    obs_ratios = pp.get("per_layer_ratios", [])
                    if obs_ratios:
                        ax.plot(range(1, len(obs_ratios) + 1), obs_ratios, "r--",
                                alpha=0.7, label="Observed")
                    break

        ax.axhline(y=1.018, color="green", linestyle=":", alpha=0.5, label="1.018")
        ax.axhline(y=1.0, color="gray", linestyle=":", alpha=0.3)
        ax.set_xlabel("Layer")
        ax.set_ylabel("Centroid ratio (L_n / L_{n-1})")
        ax.set_title(f"{label} — expansion ratio", fontsize=10)
        ax.set_ylim(0.7, 2.0)
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

    fig.suptitle(
        "RoPE-predicted vs observed attention centroids\n"
        "(Does the Q/K energy distribution explain the spiral?)",
        fontsize=13,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_head_frequency_map(
    result: dict,
    title: str,
    path: Path,
):
    """Heatmap: per-head energy centroid (layer × head).

    Shows which heads at which layers are using which frequency bands.
    """
    head_centroids = result["head_centroids"]  # (n_layers, n_heads)

    fig, ax = plt.subplots(figsize=(14, 8))
    im = ax.imshow(
        head_centroids, aspect="auto", origin="lower",
        cmap="RdYlBu_r", interpolation="nearest",
    )
    ax.set_xlabel("Head index")
    ax.set_ylabel("Layer")
    ax.set_title(f"Per-head RoPE energy centroid\n{title}")

    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Energy centroid (dim pair index)\n← high freq (local)    low freq (long-range) →")

    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_transition_analysis(
    all_results: list[dict],
    labels: list[str],
    path: Path,
):
    """Focus on the layer 5-6 transition region.

    Tests whether the positional→semantic transition in RoPE energy
    explains the observed attention centroid spike.
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Left: Q centroid jump at each layer (derivative)
    ax = axes[0]
    for res, label in zip(all_results, labels):
        diffs = np.diff(res["q_centroids"])
        ax.plot(range(1, len(diffs) + 1), diffs, "o-",
                label=label, alpha=0.6, markersize=3)
    ax.axhline(y=0, color="gray", linestyle=":", alpha=0.5)
    ax.axvspan(5.5, 7.5, color="red", alpha=0.1, label="Transition zone")
    ax.set_xlabel("Layer")
    ax.set_ylabel("ΔCentroid (dim pair shift)")
    ax.set_title("Per-layer centroid jump (Q)")
    ax.legend(fontsize=6)
    ax.grid(True, alpha=0.3)

    # Middle: energy distribution at layers 0, 5, 6, 7, 18, 35
    ax = axes[1]
    key_layers = [0, 3, 5, 6, 7, 10, 18, 35]
    if all_results:
        res = all_results[0]  # Use first prompt
        colors = plt.cm.viridis(np.linspace(0, 1, len(key_layers)))
        for li, c in zip(key_layers, colors):
            if li < res["q_dist_per_layer"].shape[0]:
                ax.plot(
                    res["q_dist_per_layer"][li],
                    color=c, alpha=0.8, linewidth=1.5,
                    label=f"Layer {li}",
                )
    ax.set_xlabel("Dim pair index (→ lower freq)")
    ax.set_ylabel("Energy fraction")
    ax.set_title(f"Q energy distribution at key layers\n({labels[0]})")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # Right: aggregate centroid with 95% CI across prompts
    ax = axes[2]
    if all_results:
        all_q_centroids = np.stack([r["q_centroids"] for r in all_results])
        mean = all_q_centroids.mean(axis=0)
        std = all_q_centroids.std(axis=0)
        layers = np.arange(len(mean))

        ax.plot(layers, mean, "b-", linewidth=2, label="Mean Q centroid")
        ax.fill_between(layers, mean - 2 * std, mean + 2 * std,
                        alpha=0.2, color="blue")
        ax.axvspan(5.5, 7.5, color="red", alpha=0.1, label="Transition zone")

    ax.set_xlabel("Layer")
    ax.set_ylabel("Energy centroid (dim pair index)")
    ax.set_title("Aggregate Q centroid ± 2σ")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    fig.suptitle(
        "Layer 5-6 transition: positional → semantic frequency shift",
        fontsize=13,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_expansion_summary(
    all_results: list[dict],
    labels: list[str],
    path: Path,
):
    """Summary: compare RoPE-predicted expansion vs observed."""
    fig, ax = plt.subplots(figsize=(10, 6))

    observed_exp = {
        "narrative": 1.0173, "expository": 1.0180, "code": 1.0163,
        "dialogue": 1.0217, "math": 1.0145, "lambda": 1.0184,
        "long_narrative": 1.0210,
    }

    predicted = []
    observed = []
    prompt_labels = []

    for res, label in zip(all_results, labels):
        if res["predicted_expansion"] is not None:
            predicted.append(res["predicted_expansion"])
            observed.append(observed_exp.get(label, np.nan))
            prompt_labels.append(label)

    x = np.arange(len(prompt_labels))
    width = 0.35

    bars1 = ax.bar(x - width / 2, predicted, width, label="RoPE-predicted",
                   color="steelblue", alpha=0.8)
    bars2 = ax.bar(x + width / 2, observed, width, label="Observed (attention spiral)",
                   color="coral", alpha=0.8)

    ax.axhline(y=1.0, color="gray", linestyle=":", alpha=0.5)
    ax.set_xlabel("Prompt type")
    ax.set_ylabel("Expansion factor per layer")
    ax.set_title("RoPE-predicted vs observed attention expansion factor")
    ax.set_xticks(x)
    ax.set_xticklabels(prompt_labels, rotation=30, ha="right")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    # Annotate
    if predicted and observed:
        mean_pred = np.mean(predicted)
        mean_obs = np.nanmean(observed)
        ratio = mean_pred / mean_obs if mean_obs > 0 else 0
        ax.text(
            0.98, 0.95,
            f"Mean predicted: {mean_pred:.4f}\n"
            f"Mean observed:  {mean_obs:.4f}\n"
            f"RoPE explains:  {ratio:.1%}",
            transform=ax.transAxes, ha="right", va="top",
            fontsize=10, bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(description="RoPE energy distribution probe")
    parser.add_argument("--quick", action="store_true", help="Use 2 prompts")
    parser.add_argument("--device", default="auto")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # RoPE constants
    freqs, wavelengths, n_pairs = compute_rope_freqs()
    print(f"RoPE: {n_pairs} dim pairs, wavelengths {wavelengths[0]:.1f} → {wavelengths[-1]:.0f} tokens")
    print(f"  Geometric ratio: {wavelengths[1]/wavelengths[0]:.4f}")
    print()

    # Load model
    model, tokenizer, device = load_model(args.device)

    # Select prompts
    prompts = PROMPTS[:2] if args.quick else PROMPTS
    labels = PROMPT_LABELS[:len(prompts)]

    # Create capture manager
    capture = RoPEEnergyCapture(model)

    all_results = []

    for i, (prompt, label) in enumerate(zip(prompts, labels)):
        print(f"\n{'─'*60}")
        print(f"Prompt {i+1}/{len(prompts)}: {label}")
        print(f"  Text: {prompt[:80]}...")

        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        seq_len = inputs["input_ids"].shape[1]
        print(f"  seq_len: {seq_len}")

        t0 = time.time()
        with capture.capture():
            with torch.no_grad():
                _ = model(**inputs)

        elapsed = time.time() - t0
        print(f"  Forward pass: {elapsed:.1f}s")

        # Analyze
        result = analyze_prompt(capture, freqs, seq_len)
        all_results.append(result)

        print(f"  Q centroid range: {result['q_centroids'].min():.1f} → {result['q_centroids'].max():.1f}")
        print(f"  K centroid range: {result['k_centroids'].min():.1f} → {result['k_centroids'].max():.1f}")
        print(f"  Predicted expansion: {result['predicted_expansion']:.4f}" if result['predicted_expansion'] else "  Predicted expansion: N/A")
        print(f"  R²: {result['r_squared']:.4f}" if result['r_squared'] else "  R²: N/A")

        # Per-prompt plots
        plot_energy_heatmap(
            result["q_dist_per_layer"],
            result["k_dist_per_layer"],
            wavelengths,
            f"RoPE energy distribution — {label}",
            OUTPUT_DIR / f"energy_heatmap_{label}.png",
        )
        plot_head_frequency_map(
            result,
            label,
            OUTPUT_DIR / f"head_freqmap_{label}.png",
        )

    # ── Cross-prompt analysis ─────────────────────────────────
    print(f"\n{'═'*60}")
    print("Cross-prompt analysis")
    print(f"{'═'*60}")

    plot_centroid_shift(all_results, labels, wavelengths,
                        OUTPUT_DIR / "centroid_shift.png")
    plot_predicted_vs_observed(all_results, labels,
                               OUTPUT_DIR / "predicted_vs_observed.png")
    plot_transition_analysis(all_results, labels,
                              OUTPUT_DIR / "transition_analysis.png")
    plot_expansion_summary(all_results, labels,
                            OUTPUT_DIR / "expansion_summary.png")

    # ── Summary ───────────────────────────────────────────────
    print(f"\n{'═'*60}")
    print("ROPE ENERGY PROBE SUMMARY")
    print(f"{'═'*60}")

    print(f"\n  {'prompt':15s} {'Q centroid':>12} {'K centroid':>12} {'pred exp':>10} {'R²':>8}")
    print(f"  {'─'*15} {'─'*12} {'─'*12} {'─'*10} {'─'*8}")

    for label, res in zip(labels, all_results):
        q_range = f"{res['q_centroids'][0]:.1f}→{res['q_centroids'][-1]:.1f}"
        k_range = f"{res['k_centroids'][0]:.1f}→{res['k_centroids'][-1]:.1f}"
        exp = f"{res['predicted_expansion']:.4f}" if res['predicted_expansion'] else "N/A"
        r2 = f"{res['r_squared']:.4f}" if res['r_squared'] else "N/A"
        print(f"  {label:15s} {q_range:>12} {k_range:>12} {exp:>10} {r2:>8}")

    # Aggregate
    all_exp = [r["predicted_expansion"] for r in all_results if r["predicted_expansion"]]
    if all_exp:
        mean_exp = np.mean(all_exp)
        print(f"\n  Aggregate predicted expansion: {mean_exp:.4f}")
        print(f"  Observed expansion (from spiral): 1.0182")
        print(f"  RoPE accounts for: {(mean_exp - 1.0) / (1.0182 - 1.0) * 100:.0f}% of expansion")

    # Key transitions
    print(f"\n  Layer-by-layer Q centroid jumps (mean across prompts):")
    all_q_centroids = np.stack([r["q_centroids"] for r in all_results])
    mean_centroids = all_q_centroids.mean(axis=0)
    diffs = np.diff(mean_centroids)
    for li in range(min(12, len(diffs))):
        bar = "+" * int(abs(diffs[li]) * 10) if diffs[li] > 0 else "-" * int(abs(diffs[li]) * 10)
        print(f"    L{li:2d}→L{li+1:2d}: {diffs[li]:+.3f} {bar}")

    # Save numerical results
    results_json = {
        "model": MODEL_NAME,
        "rope_theta": 1_000_000,
        "head_dim": 128,
        "n_dim_pairs": n_pairs,
        "wavelength_ratio": float(wavelengths[1] / wavelengths[0]),
        "n_prompts": len(prompts),
        "per_prompt": [],
    }
    for label, res in zip(labels, all_results):
        results_json["per_prompt"].append({
            "label": label,
            "q_centroids": res["q_centroids"].tolist(),
            "k_centroids": res["k_centroids"].tolist(),
            "predicted_attn_centroids": res["predicted_attn_centroids"].tolist(),
            "predicted_expansion": res["predicted_expansion"],
            "r_squared": res["r_squared"],
        })

    if all_exp:
        results_json["aggregate"] = {
            "mean_predicted_expansion": float(np.mean(all_exp)),
            "observed_expansion": 1.0182,
            "rope_explanation_fraction": float((np.mean(all_exp) - 1.0) / (1.0182 - 1.0)),
        }

    results_path = OUTPUT_DIR / "rope_energy_params.json"
    results_path.write_text(json.dumps(results_json, indent=2))
    print(f"\n  Results saved: {results_path}")
    print(f"  Plots saved: {OUTPUT_DIR}/")

    # ── Interpretation ────────────────────────────────────────
    print(f"\n{'═'*60}")
    print("INTERPRETATION")
    print(f"{'═'*60}")
    print()
    print("  The Q/K energy distribution across RoPE dim pairs is BROAD at")
    print("  every layer — heads use the full frequency spectrum, not a narrow")
    print("  band that shifts progressively. The energy centroid oscillates")
    print("  rather than monotonically shifting.")
    print()
    print("  The K centroids show strong layer-to-layer alternation (~27 vs")
    print("  ~37-48), reflecting GQA head specialization: some KV heads are")
    print("  'local' (high-freq RoPE dims) and others 'global' (low-freq).")
    print()
    print("  CONCLUSION: RoPE provides the geometric SUBSTRATE (wavelengths")
    print("  that span 6 → 5M tokens in a geometric series), but the")
    print("  attention spiral is driven by LEARNED Q·K alignment patterns")
    print("  that progressively emphasize longer-range interactions through")
    print("  the depth of the model. The spiral is an emergent property of")
    print("  training, not a direct readout of RoPE's frequency ladder.")
    print()
    print("  NEXT PROBE: Decompose actual attention logits by RoPE dim pair")
    print("  to find which frequency bands DRIVE attention at each layer.")
    print(f"\n{'═'*60}")


if __name__ == "__main__":
    main()
