#!/usr/bin/env python3
"""Combined 3D visualization: RoPE frequency structure × attention spiral.

Renders three interlocking helices:
  1. OBSERVED attention spiral — centroid distance as radius, wound by layer
  2. ROPE-PREDICTED spiral — what RoPE energy alone would predict (flat)
  3. ROPE FREQUENCY BAND — Q energy centroid mapped to wavelength scale

Plus per-layer spectral ribbons showing the RoPE dim-pair energy distribution
radiating from the helix at key layers.

Loads pre-computed data from:
  - outputs/attention_spiral/spiral_params.json   (observed centroids)
  - outputs/rope_energy/rope_energy_params.json   (RoPE energy analysis)

Usage:
    uv run python scripts/explore/rope_spiral_combined.py

Output: outputs/rope_spiral/

License: MIT
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import matplotlib.cm as cm
import numpy as np

OUTPUT_DIR = Path("outputs/rope_spiral")

# RoPE constants for Qwen3-4B
HEAD_DIM = 128
ROPE_THETA = 1_000_000
N_PAIRS = HEAD_DIM // 2
FREQS = 1.0 / (ROPE_THETA ** (2 * np.arange(N_PAIRS) / HEAD_DIM))
WAVELENGTHS = 2 * np.pi / FREQS


def load_data():
    """Load observed attention spiral and RoPE energy data."""
    with open("outputs/attention_spiral/spiral_params.json") as f:
        spiral_data = json.load(f)
    with open("outputs/rope_energy/rope_energy_params.json") as f:
        rope_data = json.load(f)

    # Also load the full RoPE energy distributions (need to re-run or
    # use the JSON summary). For now, we use the centroid data.
    return spiral_data, rope_data


def map_centroid_to_wavelength(centroid_idx: float) -> float:
    """Map a Q energy centroid (dim-pair index) to the corresponding
    RoPE wavelength in tokens."""
    return np.interp(centroid_idx, np.arange(N_PAIRS), WAVELENGTHS)


# ══════════════════════════════════════════════════════════════════
# Dual helix: observed spiral + RoPE prediction
# ══════════════════════════════════════════════════════════════════


def plot_dual_helix(
    observed_centroids: np.ndarray,
    predicted_centroids: np.ndarray,
    q_centroids: np.ndarray,
    label: str,
    lpr: float,
    path: Path,
):
    """Dual 3D helix: observed vs RoPE-predicted attention spiral.

    Maps:
      z = layer
      r = attention centroid distance (tokens)
      θ = 2π × layer / layers_per_revolution
      color = Q energy centroid (which RoPE band dominates)
    """
    n_layers = len(observed_centroids)
    layers = np.arange(n_layers)
    theta = 2 * np.pi * layers / lpr

    fig = plt.figure(figsize=(22, 16))

    views = [
        (25, -50, "Perspective"),
        (90, 0, "Top-down (spiral view)"),
        (0, 0, "Side (expansion visible)"),
        (0, -90, "Front"),
    ]

    for vi, (elev, azim, view_label) in enumerate(views):
        ax = fig.add_subplot(2, 2, vi + 1, projection="3d")

        # ── Observed spiral (solid, colored by RoPE energy centroid) ──
        r_obs = observed_centroids
        x_obs = r_obs * np.cos(theta)
        y_obs = r_obs * np.sin(theta)
        z_obs = layers.astype(float)

        # Color by Q energy centroid (higher = lower freq = warmer)
        q_norm = (q_centroids - q_centroids.min()) / (q_centroids.max() - q_centroids.min() + 1e-8)
        colors_q = cm.RdYlBu_r(q_norm)

        # Plot as colored segments
        for i in range(n_layers - 1):
            ax.plot(
                [x_obs[i], x_obs[i + 1]],
                [y_obs[i], y_obs[i + 1]],
                [z_obs[i], z_obs[i + 1]],
                color=colors_q[i], linewidth=2.5, alpha=0.9,
            )
        ax.scatter(
            x_obs, y_obs, z_obs,
            c=q_norm, cmap="RdYlBu_r", s=35, zorder=5,
            depthshade=True, edgecolors="black", linewidths=0.3,
        )

        # ── RoPE-predicted spiral (dashed gray — nearly a cylinder) ──
        r_pred = predicted_centroids
        x_pred = r_pred * np.cos(theta)
        y_pred = r_pred * np.sin(theta)
        z_pred = layers.astype(float)

        ax.plot(
            x_pred, y_pred, z_pred,
            color="gray", linewidth=1.5, linestyle="--", alpha=0.5,
            label="RoPE-only prediction",
        )

        # ── Reference circles at fixed distances ──
        theta_circle = np.linspace(0, 2 * np.pi, 100)
        for r_ref, clr, lbl in [
            (20, "green", "d=20"),
            (40, "red", "d=40"),
            (60, "purple", "d=60"),
        ]:
            for z_val in [0, n_layers - 1]:
                ax.plot(
                    r_ref * np.cos(theta_circle),
                    r_ref * np.sin(theta_circle),
                    z_val,
                    color=clr, alpha=0.12, linewidth=0.5,
                )
            # Only label once
            if vi == 0:
                ax.plot([], [], [], color=clr, alpha=0.3, linewidth=1, label=lbl)

        # ── Central axis ──
        ax.plot([0, 0], [0, 0], [0, n_layers - 1],
                color="black", linewidth=0.5, alpha=0.2)

        # ── Mark revolution boundaries ──
        for rev in range(int(n_layers / lpr) + 1):
            li = int(rev * lpr)
            if li < n_layers:
                ax.scatter(
                    [x_obs[li]], [y_obs[li]], [z_obs[li]],
                    color="red", s=60, marker="*", zorder=10, alpha=0.7,
                )

        ax.set_xlabel("x = r·cos(θ)", fontsize=8)
        ax.set_ylabel("y = r·sin(θ)", fontsize=8)
        ax.set_zlabel("Layer", fontsize=8)
        ax.view_init(elev=elev, azim=azim)
        ax.set_title(f"{view_label}", fontsize=10)

        if vi == 0:
            ax.legend(fontsize=7, loc="upper left")

    fig.suptitle(
        f"Attention Spiral vs RoPE Prediction — {label}\n"
        f"Solid = observed (colored by RoPE frequency band), "
        f"Dashed = RoPE-only prediction, LPR={lpr:.1f}",
        fontsize=13,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════
# Spectral helix: RoPE frequency bands at each layer
# ══════════════════════════════════════════════════════════════════


def plot_spectral_helix(
    observed_centroids: np.ndarray,
    q_centroids: np.ndarray,
    k_centroids: np.ndarray,
    label: str,
    path: Path,
):
    """3D helix colored by dual RoPE energy: Q and K frequency bands.

    The helix winds once per 18 layers (the dominant FFT period from
    the attention spiral analysis). At each point, the marker size
    encodes the magnitude of the energy centroid difference (Q vs K).

    Side panels show the Q and K centroid traces.
    """
    n_layers = len(observed_centroids)
    layers = np.arange(n_layers)

    # Use 18-layer period (the dominant FFT signal)
    lpr = 18.0
    theta = 2 * np.pi * layers / lpr

    fig = plt.figure(figsize=(20, 14))

    # ── Main 3D: observed spiral, colored by Q centroid ──
    ax3d = fig.add_subplot(2, 2, 1, projection="3d")

    r = observed_centroids
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    z = layers.astype(float)

    # Map Q centroid to RoPE wavelength for color
    q_wavelengths = np.array([map_centroid_to_wavelength(c) for c in q_centroids])
    q_log_wl = np.log10(q_wavelengths)
    q_norm = (q_log_wl - q_log_wl.min()) / (q_log_wl.max() - q_log_wl.min() + 1e-8)

    # Size by Q-K divergence (how differently Q and K use the spectrum)
    qk_diff = np.abs(q_centroids - k_centroids)
    sizes = 20 + 80 * (qk_diff / qk_diff.max())

    sc = ax3d.scatter(
        x, y, z,
        c=q_log_wl, cmap="Spectral_r", s=sizes,
        zorder=5, depthshade=True,
        edgecolors="black", linewidths=0.3,
    )

    # Connect with lines colored by Q centroid
    for i in range(n_layers - 1):
        ax3d.plot(
            [x[i], x[i + 1]], [y[i], y[i + 1]], [z[i], z[i + 1]],
            color=cm.Spectral_r(q_norm[i]), linewidth=2, alpha=0.8,
        )

    ax3d.set_xlabel("x", fontsize=8)
    ax3d.set_ylabel("y", fontsize=8)
    ax3d.set_zlabel("Layer", fontsize=8)
    ax3d.set_title("Attention spiral colored by RoPE frequency band\n(size = Q-K divergence)", fontsize=10)
    ax3d.view_init(elev=25, azim=-50)

    cbar = fig.colorbar(sc, ax=ax3d, shrink=0.6, pad=0.1)
    cbar.set_label("log₁₀(effective RoPE wavelength)")

    # ── Top-right: Q and K centroid vs layer ──
    ax = fig.add_subplot(2, 2, 2)
    ax.plot(layers, q_centroids, "b-", linewidth=2, label="Q energy centroid", alpha=0.8)
    ax.plot(layers, k_centroids, "r-", linewidth=2, label="K energy centroid", alpha=0.8)
    ax.fill_between(layers, q_centroids, k_centroids, alpha=0.15, color="purple")

    # Mark the characteristic RoPE boundaries
    for dim_idx, clr, lbl in [(10, "green", "dim 10 (λ=54)"), (20, "orange", "dim 20 (λ=471)"), (32, "red", "dim 32 (λ=6.3k)")]:
        ax.axhline(y=dim_idx, color=clr, linestyle=":", alpha=0.4, label=lbl)

    ax.set_xlabel("Layer")
    ax.set_ylabel("Energy centroid (dim pair index)\n← high freq    low freq →")
    ax.set_title("Q vs K RoPE energy centroid")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # ── Bottom-left: observed centroid with RoPE wavelength right axis ──
    ax = fig.add_subplot(2, 2, 3)
    ax.plot(layers, observed_centroids, "k-", linewidth=2, label="Observed attention centroid")

    # Overlay the RoPE-mapped wavelength
    ax2 = ax.twinx()
    ax2.plot(layers, q_wavelengths, "b--", linewidth=1.5, alpha=0.6, label="Q→RoPE wavelength")
    ax2.set_ylabel("Effective RoPE wavelength (tokens)", color="blue", fontsize=9)
    ax2.set_yscale("log")
    ax2.tick_params(axis="y", labelcolor="blue")

    ax.set_xlabel("Layer")
    ax.set_ylabel("Attention centroid (tokens)")
    ax.set_title(f"Observed spiral vs RoPE frequency — {label}")
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(True, alpha=0.3)

    # ── Bottom-right: expansion ratio comparison ──
    ax = fig.add_subplot(2, 2, 4)
    obs_ratios = observed_centroids[1:] / observed_centroids[:-1]
    ax.plot(range(1, len(obs_ratios) + 1), obs_ratios, "k-", linewidth=1.5,
            alpha=0.7, label="Observed expansion ratio")

    # Q centroid shift rate mapped to expansion
    q_shift = np.diff(q_centroids)
    # Map dim-pair shift to wavelength ratio: shift by 1 dim → wavelength × 1.2409
    implied_expansion = 1.2409 ** (q_shift / N_PAIRS)  # normalized
    ax.plot(range(1, len(implied_expansion) + 1), implied_expansion, "b--",
            linewidth=1, alpha=0.5, label="RoPE-implied expansion")

    ax.axhline(y=1.018, color="green", linestyle=":", alpha=0.5, label="1.018 (observed mean)")
    ax.axhline(y=1.0, color="gray", linestyle=":", alpha=0.3)
    ax.set_xlabel("Layer")
    ax.set_ylabel("Expansion ratio")
    ax.set_title("Per-layer expansion: observed vs RoPE-implied")
    ax.set_ylim(0.7, 2.0)
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    fig.suptitle(
        f"RoPE × Attention Spiral — {label}\n"
        f"RoPE provides the frequency substrate; learned Q·K alignment creates the spiral",
        fontsize=13,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════
# Aggregate: all prompts wound together
# ══════════════════════════════════════════════════════════════════


def plot_aggregate_dual(
    spiral_data: dict,
    rope_data: dict,
    path: Path,
):
    """Aggregate 3D: all prompts overlaid, observed vs RoPE-predicted.

    Uses mean LPR from the 3D analysis.
    """
    # Load 3D params for LPR
    try:
        with open("outputs/attention_spiral/spiral_3d_params.json") as f:
            s3d = json.load(f)
        mean_lpr = s3d["mean_best_lpr"]
    except FileNotFoundError:
        mean_lpr = 3.5

    n_layers = spiral_data["per_prompt"][0]["fixed_point_layer"] + 16  # ~36
    n_layers = len(spiral_data["per_prompt"][0]["layer_centroids"])
    layers = np.arange(n_layers)
    theta = 2 * np.pi * layers / mean_lpr

    fig = plt.figure(figsize=(20, 10))

    # ── Left: perspective view ──
    ax = fig.add_subplot(1, 2, 1, projection="3d")

    prompt_colors = cm.tab10(np.linspace(0, 0.7, len(spiral_data["per_prompt"])))

    for pi, (sp, rp) in enumerate(zip(
        spiral_data["per_prompt"],
        rope_data["per_prompt"],
    )):
        obs = np.array(sp["layer_centroids"])
        pred = np.array(rp["predicted_attn_centroids"])
        label = sp["label"]

        # Observed
        x_obs = obs * np.cos(theta)
        y_obs = obs * np.sin(theta)
        ax.plot(x_obs, y_obs, layers, color=prompt_colors[pi],
                linewidth=1.5, alpha=0.7, label=f"{label} (observed)")
        ax.scatter(x_obs, y_obs, layers, color=prompt_colors[pi],
                   s=8, alpha=0.5, depthshade=True)

        # Predicted (only first prompt to avoid clutter)
        if pi == 0:
            x_pred = pred * np.cos(theta)
            y_pred = pred * np.sin(theta)
            ax.plot(x_pred, y_pred, layers, color="gray",
                    linewidth=2, linestyle="--", alpha=0.6,
                    label="RoPE-only prediction")

    # Reference circles
    theta_c = np.linspace(0, 2 * np.pi, 100)
    for r, clr in [(20, "green"), (40, "red"), (60, "purple")]:
        ax.plot(r * np.cos(theta_c), r * np.sin(theta_c), 0,
                color=clr, alpha=0.1, linewidth=0.5)
        ax.plot(r * np.cos(theta_c), r * np.sin(theta_c), n_layers - 1,
                color=clr, alpha=0.1, linewidth=0.5)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("Layer")
    ax.view_init(elev=20, azim=-55)
    ax.legend(fontsize=6, loc="upper left")
    ax.set_title(f"All prompts — perspective\nLPR={mean_lpr:.1f}", fontsize=10)

    # ── Right: top-down (spiral structure visible) ──
    ax = fig.add_subplot(1, 2, 2, projection="3d")

    for pi, (sp, rp) in enumerate(zip(
        spiral_data["per_prompt"],
        rope_data["per_prompt"],
    )):
        obs = np.array(sp["layer_centroids"])
        q_c = np.array(rp["q_centroids"])

        x_obs = obs * np.cos(theta)
        y_obs = obs * np.sin(theta)

        # Color by Q centroid
        q_norm = (q_c - 25) / (48 - 25)
        q_norm = np.clip(q_norm, 0, 1)
        colors = cm.RdYlBu_r(q_norm)

        for i in range(n_layers - 1):
            ax.plot(
                [x_obs[i], x_obs[i + 1]],
                [y_obs[i], y_obs[i + 1]],
                [layers[i], layers[i + 1]],
                color=colors[i], linewidth=1.5, alpha=0.6,
            )

    for r, clr in [(20, "green"), (40, "red"), (60, "purple")]:
        ax.plot(r * np.cos(theta_c), r * np.sin(theta_c), 18,
                color=clr, alpha=0.15, linewidth=0.5)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("Layer")
    ax.view_init(elev=90, azim=0)
    ax.set_title("Top-down — colored by RoPE frequency band\n(blue = high freq/local, red = low freq/global)", fontsize=10)

    fig.suptitle(
        "Observed Attention Spirals vs RoPE-Only Prediction\n"
        "Solid colored = observed (color = Q RoPE band), Gray dashed = RoPE alone (flat)",
        fontsize=13,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════
# The gap visualization: what creates the spiral if not RoPE alone?
# ══════════════════════════════════════════════════════════════════


def plot_gap_analysis(
    spiral_data: dict,
    rope_data: dict,
    path: Path,
):
    """Visualize the gap between RoPE-predicted and observed spirals.

    Shows: at each layer, observed radius minus predicted radius.
    This 'gap' is what the learned Q·K alignment contributes.
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Use mean across prompts
    all_obs = np.stack([np.array(sp["layer_centroids"]) for sp in spiral_data["per_prompt"]])
    all_pred = np.stack([np.array(rp["predicted_attn_centroids"]) for rp in rope_data["per_prompt"]])
    all_qc = np.stack([np.array(rp["q_centroids"]) for rp in rope_data["per_prompt"]])

    mean_obs = all_obs.mean(axis=0)
    std_obs = all_obs.std(axis=0)
    mean_pred = all_pred.mean(axis=0)
    mean_qc = all_qc.mean(axis=0)

    n_layers = len(mean_obs)
    layers = np.arange(n_layers)

    # ── Top-left: observed vs predicted ──
    ax = axes[0, 0]
    ax.plot(layers, mean_obs, "k-", linewidth=2, label="Observed attention centroid")
    ax.fill_between(layers, mean_obs - std_obs, mean_obs + std_obs, alpha=0.15, color="black")
    ax.plot(layers, mean_pred, "b--", linewidth=2, label="RoPE-only prediction")
    ax.set_xlabel("Layer")
    ax.set_ylabel("Attention centroid (tokens)")
    ax.set_title("Observed vs RoPE-predicted attention distance")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # ── Top-right: the gap (learned contribution) ──
    ax = axes[0, 1]
    gap = mean_obs - mean_pred
    gap_colors = cm.RdBu_r((gap - gap.min()) / (gap.max() - gap.min() + 1e-8))
    ax.bar(layers, gap, color=gap_colors, alpha=0.8, edgecolor="gray", linewidth=0.3)
    ax.axhline(y=0, color="black", linewidth=0.5)
    ax.set_xlabel("Layer")
    ax.set_ylabel("Observed − Predicted (tokens)")
    ax.set_title("The 'learned gap': what training adds beyond RoPE")
    ax.grid(True, alpha=0.3)

    # ── Bottom-left: 3D gap helix ──
    ax = fig.add_subplot(2, 2, 3, projection="3d")
    lpr = 9.4  # LPR that gives ~1.18 expansion
    theta = 2 * np.pi * layers / lpr

    # Observed helix
    x_obs = mean_obs * np.cos(theta)
    y_obs = mean_obs * np.sin(theta)
    z = layers.astype(float)

    # Predicted helix
    x_pred = mean_pred * np.cos(theta)
    y_pred = mean_pred * np.sin(theta)

    # Color the observed helix by the gap
    gap_norm = (gap - gap.min()) / (gap.max() - gap.min() + 1e-8)
    for i in range(n_layers - 1):
        ax.plot(
            [x_obs[i], x_obs[i + 1]],
            [y_obs[i], y_obs[i + 1]],
            [z[i], z[i + 1]],
            color=cm.RdBu_r(gap_norm[i]), linewidth=2.5, alpha=0.9,
        )
    ax.plot(x_pred, y_pred, z, color="gray", linewidth=1.5,
            linestyle="--", alpha=0.5, label="RoPE-only")

    # Draw radial lines showing the gap at key layers
    for li in range(0, n_layers, 4):
        ax.plot(
            [x_pred[li], x_obs[li]],
            [y_pred[li], y_obs[li]],
            [z[li], z[li]],
            color="green" if gap[li] > 0 else "red",
            linewidth=1, alpha=0.6,
        )

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("Layer")
    ax.view_init(elev=25, azim=-50)
    ax.set_title(f"3D gap: radial lines = learned contribution\nLPR={lpr:.1f}", fontsize=10)

    # ── Bottom-right: Q centroid vs gap correlation ──
    ax = axes[1, 1]
    ax.scatter(mean_qc, gap, c=layers, cmap="viridis", s=40, edgecolors="black", linewidths=0.3)
    ax.set_xlabel("Q energy centroid (dim pair index)")
    ax.set_ylabel("Learned gap (obs − pred, tokens)")
    ax.set_title("Does RoPE frequency band predict the gap?")
    ax.grid(True, alpha=0.3)

    # Correlation
    r = np.corrcoef(mean_qc, gap)[0, 1]
    ax.text(0.05, 0.95, f"r = {r:.3f}", transform=ax.transAxes,
            fontsize=12, va="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    cbar = fig.colorbar(
        cm.ScalarMappable(cmap="viridis", norm=plt.Normalize(0, n_layers - 1)),
        ax=ax, shrink=0.8,
    )
    cbar.set_label("Layer")

    fig.suptitle(
        "Anatomy of the Attention Spiral\n"
        "RoPE provides flat substrate → learned Q·K alignment creates expansion",
        fontsize=14,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════
# Unwound view: the spiral as a flat ribbon with RoPE spectrum
# ══════════════════════════════════════════════════════════════════


def plot_unwound_ribbon(
    spiral_data: dict,
    rope_data: dict,
    path: Path,
):
    """Unwound ribbon: layer on x, attention distance on y, with
    RoPE frequency annotation as a background heatmap.

    This is the 'flattened' version of the 3D helix — easier to read.
    """
    fig, axes = plt.subplots(3, 1, figsize=(18, 14), height_ratios=[2, 1, 1])

    n_layers = len(spiral_data["per_prompt"][0]["layer_centroids"])
    layers = np.arange(n_layers)

    # ── Top: observed centroids with RoPE wavelength scale ──
    ax = axes[0]

    for sp, rp in zip(spiral_data["per_prompt"], rope_data["per_prompt"]):
        obs = np.array(sp["layer_centroids"])
        q_c = np.array(rp["q_centroids"])
        label = sp["label"]

        # Color segments by Q centroid
        q_norm = (q_c - 25) / (48 - 25)
        q_norm = np.clip(q_norm, 0, 1)
        colors = cm.RdYlBu_r(q_norm)

        for i in range(n_layers - 1):
            ax.plot(
                [layers[i], layers[i + 1]],
                [obs[i], obs[i + 1]],
                color=colors[i], linewidth=2, alpha=0.7,
            )

    # RoPE prediction (mean)
    mean_pred = np.stack([np.array(rp["predicted_attn_centroids"])
                          for rp in rope_data["per_prompt"]]).mean(axis=0)
    ax.plot(layers, mean_pred, "k--", linewidth=2.5, alpha=0.8,
            label="RoPE-only prediction (flat)")

    # Wavelength scale on right
    ax2 = ax.twinx()
    mean_qc = np.stack([np.array(rp["q_centroids"])
                        for rp in rope_data["per_prompt"]]).mean(axis=0)
    q_wl = np.array([map_centroid_to_wavelength(c) for c in mean_qc])
    ax2.plot(layers, q_wl, "b:", linewidth=1, alpha=0.4)
    ax2.set_ylabel("Q→RoPE wavelength (tokens)", color="blue", fontsize=9)
    ax2.set_yscale("log")
    ax2.tick_params(axis="y", labelcolor="blue")

    ax.set_ylabel("Attention centroid (tokens)")
    ax.set_title(
        "Unwound attention spiral — colored by RoPE frequency band\n"
        "(blue = high freq / local, red = low freq / global)",
        fontsize=12,
    )
    ax.legend(fontsize=9, loc="upper left")
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-0.5, n_layers - 0.5)

    # ── Middle: Q and K centroid traces ──
    ax = axes[1]
    for rp in rope_data["per_prompt"]:
        q_c = np.array(rp["q_centroids"])
        k_c = np.array(rp["k_centroids"])
        ax.plot(layers, q_c, "b-", alpha=0.3, linewidth=0.8)
        ax.plot(layers, k_c, "r-", alpha=0.3, linewidth=0.8)

    # Mean
    mean_q = np.stack([np.array(rp["q_centroids"]) for rp in rope_data["per_prompt"]]).mean(axis=0)
    mean_k = np.stack([np.array(rp["k_centroids"]) for rp in rope_data["per_prompt"]]).mean(axis=0)
    ax.plot(layers, mean_q, "b-", linewidth=2.5, label="Q centroid (mean)")
    ax.plot(layers, mean_k, "r-", linewidth=2.5, label="K centroid (mean)")
    ax.fill_between(layers, mean_q, mean_k, alpha=0.1, color="purple")

    ax.set_ylabel("Energy centroid\n(dim pair index)")
    ax.set_title("RoPE energy distribution: Q vs K across layers", fontsize=11)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-0.5, n_layers - 0.5)

    # ── Bottom: per-layer expansion ratio ──
    ax = axes[2]
    for sp in spiral_data["per_prompt"]:
        obs = np.array(sp["layer_centroids"])
        ratios = obs[1:] / obs[:-1]
        ax.plot(range(1, len(ratios) + 1), ratios, alpha=0.3, linewidth=0.8, color="gray")

    mean_obs = np.stack([np.array(sp["layer_centroids"])
                         for sp in spiral_data["per_prompt"]]).mean(axis=0)
    mean_ratios = mean_obs[1:] / mean_obs[:-1]
    # Smooth
    kernel = np.ones(3) / 3
    smoothed = np.convolve(mean_ratios, kernel, mode="valid")
    ax.plot(range(2, 2 + len(smoothed)), smoothed, "k-", linewidth=2.5,
            label="Observed (smoothed)")
    ax.axhline(y=1.018, color="green", linestyle=":", linewidth=1.5,
               alpha=0.7, label="1.018 (mean expansion)")
    ax.axhline(y=1.0, color="gray", linestyle=":", alpha=0.3)

    ax.set_xlabel("Layer")
    ax.set_ylabel("Expansion ratio\n(L_n / L_{n-1})")
    ax.set_title("Per-layer attention expansion — the spiral unwound", fontsize=11)
    ax.set_ylim(0.7, 2.0)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-0.5, n_layers - 0.5)

    fig.suptitle(
        "The Attention Spiral Unwound\n"
        "RoPE frequency ladder provides the substrate; learned alignment creates the expansion",
        fontsize=14,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading data...")
    spiral_data, rope_data = load_data()

    n_prompts = min(len(spiral_data["per_prompt"]), len(rope_data["per_prompt"]))

    # Load 3D params for LPR
    try:
        with open("outputs/attention_spiral/spiral_3d_params.json") as f:
            s3d = json.load(f)
        mean_lpr = s3d["mean_best_lpr"]
    except FileNotFoundError:
        mean_lpr = 3.5

    print(f"  {n_prompts} prompts, mean LPR={mean_lpr:.1f}")
    print()

    # ── Per-prompt dual helix ──────────────────────────────────
    for i in range(n_prompts):
        sp = spiral_data["per_prompt"][i]
        rp = rope_data["per_prompt"][i]
        label = sp["label"]

        obs = np.array(sp["layer_centroids"])
        pred = np.array(rp["predicted_attn_centroids"])
        qc = np.array(rp["q_centroids"])
        kc = np.array(rp["k_centroids"])

        print(f"── {label} ──")
        plot_dual_helix(obs, pred, qc, label, mean_lpr,
                        OUTPUT_DIR / f"dual_helix_{label}.png")
        plot_spectral_helix(obs, qc, kc, label,
                            OUTPUT_DIR / f"spectral_{label}.png")

    # ── Aggregate views ───────────────────────────────────────
    print(f"\n── Aggregate ──")
    plot_aggregate_dual(spiral_data, rope_data,
                        OUTPUT_DIR / "aggregate_dual.png")
    plot_gap_analysis(spiral_data, rope_data,
                      OUTPUT_DIR / "gap_analysis.png")
    plot_unwound_ribbon(spiral_data, rope_data,
                        OUTPUT_DIR / "unwound_ribbon.png")

    print(f"\n{'═'*60}")
    print(f"All outputs saved to: {OUTPUT_DIR}/")
    print(f"{'═'*60}")


if __name__ == "__main__":
    main()
