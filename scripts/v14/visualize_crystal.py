#!/usr/bin/env python3
"""Visualize the crystal lattice as multiple 3D cross-sections.

The crystal is ~6-8D. We create multiple 3D views by projecting
the 16 combinator types onto different triplets of principal components.

Each view reveals different structure:
  PC0×PC1×PC2: composition × selection × termination (the core)
  PC0×PC1×PC3: composition × selection × routing
  PC0×PC2×PC3: composition × termination × routing
  PC1×PC2×PC3: selection × termination × routing

Usage:
    uv run python scripts/v14/visualize_crystal.py \
        --output results/crystal-visualization/

License: MIT
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')  # non-interactive backend
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# ══════════════════════════════════════════════════════════════════════
# Crystal data
# ══════════════════════════════════════════════════════════════════════

COMBINATOR_NAMES = ["K", "I", "B", "C", "D", "Y", "W", "WHNF",
                    "āK", "āI", "āB", "āC", "āD", "āY", "āW", "āWHNF"]

# Combinator families for coloring
FAMILIES = {
    "selection":    ["K", "I", "āK", "āI"],
    "composition":  ["B", "C", "D", "Y", "W", "āB", "āC", "āD", "āY", "āW"],
    "terminal":     ["WHNF", "āWHNF"],
}

FAMILY_COLORS = {
    "selection":   "#2196F3",  # blue
    "composition": "#FF5722",  # red-orange
    "terminal":    "#4CAF50",  # green
}

PC_LABELS = {
    0: "PC0: Composition (λ=5.19)",
    1: "PC1: Selection (λ=3.53)",
    2: "PC2: Termination (λ=1.91)",
    3: "PC3: Routing (λ=1.30)",
    4: "PC4: Dispatch (λ=1.08)",
    5: "PC5: Fine (λ=0.74)",
    6: "PC6: Dup (λ=0.50)",
    7: "PC7: Micro (λ=0.43)",
}

# Zone B target cosine matrix (the crystal proper)
ZONE_B_TARGET = np.array([
    [+1.0000, +0.7865, +0.1948, +0.2265, +0.3232, +0.1768, +0.5360, -0.1862, -0.1900, -0.1494, -0.0370, -0.0430, -0.0614, -0.0336, -0.1018, +0.0354],
    [+0.7865, +1.0000, +0.2479, +0.2511, +0.3463, +0.1739, +0.3781, -0.2448, -0.1494, -0.1900, -0.0471, -0.0477, -0.0658, -0.0330, -0.0718, +0.0465],
    [+0.1948, +0.2479, +1.0000, +0.8878, +0.8937, +0.6623, +0.6851, -0.1227, -0.0370, -0.0471, -0.1900, -0.1687, -0.1698, -0.1258, -0.1302, +0.0233],
    [+0.2265, +0.2511, +0.8878, +1.0000, +0.8316, +0.7200, +0.7318, -0.1027, -0.0430, -0.0477, -0.1687, -0.1900, -0.1580, -0.1368, -0.1390, +0.0195],
    [+0.3232, +0.3463, +0.8937, +0.8316, +1.0000, +0.6798, +0.8064, -0.1729, -0.0614, -0.0658, -0.1698, -0.1580, -0.1900, -0.1292, -0.1532, +0.0329],
    [+0.1768, +0.1739, +0.6623, +0.7200, +0.6798, +1.0000, +0.5653, -0.0840, -0.0336, -0.0330, -0.1258, -0.1368, -0.1292, -0.1900, -0.1074, +0.0160],
    [+0.5360, +0.3781, +0.6851, +0.7318, +0.8064, +0.5653, +1.0000, -0.1379, -0.1018, -0.0718, -0.1302, -0.1390, -0.1532, -0.1074, -0.1900, +0.0262],
    [-0.1862, -0.2448, -0.1227, -0.1027, -0.1729, -0.0840, -0.1379, +1.0000, +0.0354, +0.0465, +0.0233, +0.0195, +0.0329, +0.0160, +0.0262, -0.1900],
    [-0.1900, -0.1494, -0.0370, -0.0430, -0.0614, -0.0336, -0.1018, +0.0354, +1.0000, +0.7865, +0.1948, +0.2265, +0.3232, +0.1768, +0.5360, -0.1862],
    [-0.1494, -0.1900, -0.0471, -0.0477, -0.0658, -0.0330, -0.0718, +0.0465, +0.7865, +1.0000, +0.2479, +0.2511, +0.3463, +0.1739, +0.3781, -0.2448],
    [-0.0370, -0.0471, -0.1900, -0.1687, -0.1698, -0.1258, -0.1302, +0.0233, +0.1948, +0.2479, +1.0000, +0.8878, +0.8937, +0.6623, +0.6851, -0.1227],
    [-0.0430, -0.0477, -0.1687, -0.1900, -0.1580, -0.1368, -0.1390, +0.0195, +0.2265, +0.2511, +0.8878, +1.0000, +0.8316, +0.7200, +0.7318, -0.1027],
    [-0.0614, -0.0658, -0.1698, -0.1580, -0.1900, -0.1292, -0.1532, +0.0329, +0.3232, +0.3463, +0.8937, +0.8316, +1.0000, +0.6798, +0.8064, -0.1729],
    [-0.0336, -0.0330, -0.1258, -0.1368, -0.1292, -0.1900, -0.1074, +0.0160, +0.1768, +0.1739, +0.6623, +0.7200, +0.6798, +1.0000, +0.5653, -0.0840],
    [-0.1018, -0.0718, -0.1302, -0.1390, -0.1532, -0.1074, -0.1900, +0.0262, +0.5360, +0.3781, +0.6851, +0.7318, +0.8064, +0.5653, +1.0000, -0.1379],
    [+0.0354, +0.0465, +0.0233, +0.0195, +0.0329, +0.0160, +0.0262, -0.1900, -0.1862, -0.2448, -0.1227, -0.1027, -0.1729, -0.0840, -0.1379, +1.0000],
], dtype=np.float64)


def get_family(name: str) -> str:
    for family, members in FAMILIES.items():
        if name in members:
            return family
    return "unknown"


def make_3d_plot(coords: np.ndarray, pc_x: int, pc_y: int, pc_z: int,
                 eigenvalues: np.ndarray, output_path: Path,
                 title_suffix: str = ""):
    """Create a 3D scatter plot of the crystal cross-section."""
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Plot each combinator
    for i, name in enumerate(COMBINATOR_NAMES):
        family = get_family(name)
        color = FAMILY_COLORS.get(family, "#999999")
        is_anti = name.startswith("ā")

        x, y, z = coords[i, pc_x], coords[i, pc_y], coords[i, pc_z]

        # Anti-types: hollow markers, smaller
        if is_anti:
            ax.scatter(x, y, z, c='white', edgecolors=color, s=120,
                      marker='o', linewidths=2, alpha=0.7, zorder=5)
            ax.text(x, y, z + 0.03, name, fontsize=7, ha='center',
                   va='bottom', color=color, alpha=0.6)
        else:
            ax.scatter(x, y, z, c=color, s=200, marker='o',
                      edgecolors='black', linewidths=0.5, alpha=0.9, zorder=10)
            ax.text(x, y, z + 0.04, name, fontsize=10, ha='center',
                   va='bottom', fontweight='bold', color='black')

    # Draw lines between related combinators
    # Selection cluster: K-I
    for pair in [(0, 1), (8, 9)]:  # K-I, āK-āI
        ax.plot([coords[pair[0], pc_x], coords[pair[1], pc_x]],
                [coords[pair[0], pc_y], coords[pair[1], pc_y]],
                [coords[pair[0], pc_z], coords[pair[1], pc_z]],
                color=FAMILY_COLORS["selection"], alpha=0.3, linewidth=1)

    # Composition cluster: B-C-D-Y-W
    comp_base = [2, 3, 4, 5, 6]  # B, C, D, Y, W
    comp_anti = [10, 11, 12, 13, 14]
    for cluster in [comp_base, comp_anti]:
        for i in range(len(cluster)):
            for j in range(i + 1, len(cluster)):
                ci, cj = cluster[i], cluster[j]
                cos_sim = ZONE_B_TARGET[ci, cj]
                if cos_sim > 0.7:  # only draw strong connections
                    ax.plot([coords[ci, pc_x], coords[cj, pc_x]],
                            [coords[ci, pc_y], coords[cj, pc_y]],
                            [coords[ci, pc_z], coords[cj, pc_z]],
                            color=FAMILY_COLORS["composition"],
                            alpha=cos_sim * 0.4, linewidth=cos_sim * 2)

    # Draw lines between type and anti-type (dashed)
    for i in range(8):
        ax.plot([coords[i, pc_x], coords[i + 8, pc_x]],
                [coords[i, pc_y], coords[i + 8, pc_y]],
                [coords[i, pc_z], coords[i + 8, pc_z]],
                color='gray', alpha=0.15, linewidth=0.5, linestyle='--')

    # Labels
    ax.set_xlabel(f'\n{PC_LABELS[pc_x]}', fontsize=10, labelpad=10)
    ax.set_ylabel(f'\n{PC_LABELS[pc_y]}', fontsize=10, labelpad=10)
    ax.set_zlabel(f'\n{PC_LABELS[pc_z]}', fontsize=10, labelpad=10)

    var_explained = (eigenvalues[pc_x] + eigenvalues[pc_y] + eigenvalues[pc_z]) / eigenvalues.sum() * 100
    ax.set_title(f'Crystal Lattice — PC{pc_x}×PC{pc_y}×PC{pc_z} '
                 f'({var_explained:.1f}% variance){title_suffix}',
                 fontsize=13, fontweight='bold', pad=20)

    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=FAMILY_COLORS["composition"],
               markersize=12, label='Composition (B,C,D,Y,W)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=FAMILY_COLORS["selection"],
               markersize=12, label='Selection (K,I)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=FAMILY_COLORS["terminal"],
               markersize=12, label='Terminal (WHNF)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='white',
               markeredgecolor='gray', markersize=10, label='Anti-types (ā)'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=9)

    ax.view_init(elev=25, azim=135)

    plt.tight_layout()
    plt.savefig(str(output_path), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"  Saved: {output_path}", file=sys.stderr)


def make_2d_overview(coords: np.ndarray, eigenvalues: np.ndarray, output_path: Path):
    """Create a 2×3 grid of 2D projections for quick overview."""
    pairs = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]

    fig, axes = plt.subplots(2, 3, figsize=(18, 11))

    for idx, (pc_x, pc_y) in enumerate(pairs):
        ax = axes[idx // 3][idx % 3]

        for i, name in enumerate(COMBINATOR_NAMES):
            family = get_family(name)
            color = FAMILY_COLORS.get(family, "#999999")
            is_anti = name.startswith("ā")

            x, y = coords[i, pc_x], coords[i, pc_y]

            if is_anti:
                ax.scatter(x, y, c='white', edgecolors=color, s=80,
                          marker='o', linewidths=1.5, alpha=0.6, zorder=5)
                ax.annotate(name, (x, y), fontsize=6, ha='center',
                           va='bottom', color=color, alpha=0.5,
                           xytext=(0, 4), textcoords='offset points')
            else:
                ax.scatter(x, y, c=color, s=150, marker='o',
                          edgecolors='black', linewidths=0.5, alpha=0.9, zorder=10)
                ax.annotate(name, (x, y), fontsize=9, ha='center',
                           va='bottom', fontweight='bold',
                           xytext=(0, 6), textcoords='offset points')

        # Draw composition cluster connections
        comp_indices = [2, 3, 4, 5, 6]
        for ci in range(len(comp_indices)):
            for cj in range(ci + 1, len(comp_indices)):
                ii, jj = comp_indices[ci], comp_indices[cj]
                cos_sim = ZONE_B_TARGET[ii, jj]
                if cos_sim > 0.7:
                    ax.plot([coords[ii, pc_x], coords[jj, pc_x]],
                            [coords[ii, pc_y], coords[jj, pc_y]],
                            color=FAMILY_COLORS["composition"],
                            alpha=cos_sim * 0.3, linewidth=cos_sim * 1.5)

        # K-I connection
        ax.plot([coords[0, pc_x], coords[1, pc_x]],
                [coords[0, pc_y], coords[1, pc_y]],
                color=FAMILY_COLORS["selection"], alpha=0.3, linewidth=1)

        var_pct = (eigenvalues[pc_x] + eigenvalues[pc_y]) / eigenvalues.sum() * 100
        ax.set_xlabel(PC_LABELS[pc_x].split(':')[0], fontsize=9)
        ax.set_ylabel(PC_LABELS[pc_y].split(':')[0], fontsize=9)
        ax.set_title(f'PC{pc_x}×PC{pc_y} ({var_pct:.0f}%)', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.2)
        ax.axhline(y=0, color='gray', linewidth=0.5, alpha=0.3)
        ax.axvline(x=0, color='gray', linewidth=0.5, alpha=0.3)

    fig.suptitle('Crystal Lattice — Zone B (Compute Zone)\n'
                 '16 combinator types projected onto principal component pairs',
                 fontsize=14, fontweight='bold', y=1.02)

    plt.tight_layout()
    plt.savefig(str(output_path), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"  Saved: {output_path}", file=sys.stderr)


def make_eigenvalue_plot(eigenvalues: np.ndarray, output_path: Path):
    """Visualize the eigenvalue spectrum."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Bar chart of eigenvalues
    colors = ['#FF5722', '#2196F3', '#4CAF50', '#FF9800',
              '#9C27B0', '#795548', '#607D8B', '#E91E63'] * 2
    pc_names = ['Comp', 'Sel', 'Term', 'Route', 'Disp', 'Fine', 'Dup', 'Micro',
                'āCo', 'āSe', 'āTe', 'āRo', 'āDi', 'āFi', 'āDu', 'āMi']

    # Show only top 8 for clarity
    n_show = min(8, len(eigenvalues))
    bars = ax1.bar(range(n_show), eigenvalues[:n_show], color=colors[:n_show])
    ax1.set_xticks(range(n_show))
    ax1.set_xticklabels([f'PC{i}\n{pc_names[i]}\nλ={ev:.2f}'
                         for i, ev in enumerate(eigenvalues[:n_show])], fontsize=8)
    ax1.set_ylabel('Eigenvalue', fontsize=11)
    ax1.set_title('Crystal Eigenvalue Spectrum', fontsize=13, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

    # Key ratios
    ax1.annotate(f'λ₀/λ₁ = {eigenvalues[0]/eigenvalues[1]:.3f}',
                xy=(0.5, eigenvalues[0] * 0.85), fontsize=10, ha='center',
                fontweight='bold', color='#333')

    # Cumulative variance (top 8)
    cum_var = np.cumsum(eigenvalues[:n_show]) / eigenvalues.sum() * 100
    ax2.plot(range(1, n_show + 1), cum_var, 'o-', color='#2196F3',
             linewidth=2, markersize=8)
    ax2.axhline(y=95, color='gray', linestyle='--', alpha=0.5)
    ax2.axhline(y=99, color='gray', linestyle='--', alpha=0.3)
    ax2.text(len(eigenvalues) - 0.5, 95.5, '95%', fontsize=9, color='gray')
    ax2.text(len(eigenvalues) - 0.5, 99.5, '99%', fontsize=9, color='gray')
    ax2.set_xlabel('Number of PCs', fontsize=11)
    ax2.set_ylabel('Cumulative Variance (%)', fontsize=11)
    ax2.set_title('Variance Explained', fontsize=13, fontweight='bold')
    ax2.set_xticks(range(1, n_show + 1))
    ax2.grid(alpha=0.3)
    ax2.set_ylim(50, 102)

    for i, cv in enumerate(cum_var):
        ax2.annotate(f'{cv:.0f}%', (i + 1, cv), textcoords="offset points",
                    xytext=(0, 10), ha='center', fontsize=8)

    plt.tight_layout()
    plt.savefig(str(output_path), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"  Saved: {output_path}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Visualize crystal lattice")
    parser.add_argument("--output", type=str, default="results/crystal-visualization/")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Eigendecompose Zone B target
    eigenvalues, eigenvectors = np.linalg.eigh(ZONE_B_TARGET)
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    print(f"Crystal eigenvalues:", file=sys.stderr)
    for i, ev in enumerate(eigenvalues):
        cum = eigenvalues[:i+1].sum() / eigenvalues.sum() * 100
        print(f"  PC{i}: λ={ev:.4f}  cum={cum:.1f}%", file=sys.stderr)
    print(f"  λ₀/λ₁ = {eigenvalues[0]/eigenvalues[1]:.4f}", file=sys.stderr)

    # Project 16 combinator types onto eigenbasis
    # Each combinator's coordinates = its row in the cosine matrix,
    # projected onto eigenvectors
    coords = ZONE_B_TARGET @ eigenvectors  # (16, 16) — each row is a combinator's position

    # Normalize by eigenvalue (scale by sqrt(λ) for visual clarity)
    coords_scaled = coords * np.sqrt(np.abs(eigenvalues))[np.newaxis, :]

    print(f"\nGenerating visualizations...", file=sys.stderr)

    # 1. Eigenvalue spectrum
    make_eigenvalue_plot(eigenvalues, output_dir / "eigenvalue_spectrum.png")

    # 2. 2D overview (6 panels)
    make_2d_overview(coords_scaled, eigenvalues, output_dir / "crystal_2d_overview.png")

    # 3. 3D cross-sections — the main views
    triplets = [
        (0, 1, 2, "The Core: Composition × Selection × Termination"),
        (0, 1, 3, "Routing: Composition × Selection × Routing"),
        (0, 2, 3, "Structure: Composition × Termination × Routing"),
        (1, 2, 3, "Operations: Selection × Termination × Routing"),
        (0, 1, 4, "Dispatch: Composition × Selection × Dispatch"),
        (2, 3, 4, "Fine Structure: Termination × Routing × Dispatch"),
    ]

    for pc_x, pc_y, pc_z, subtitle in triplets:
        filename = f"crystal_3d_pc{pc_x}{pc_y}{pc_z}.png"
        make_3d_plot(coords_scaled, pc_x, pc_y, pc_z, eigenvalues,
                     output_dir / filename, f"\n{subtitle}")

    # 4. Multiple viewing angles for the core (PC0×PC1×PC2)
    fig = plt.figure(figsize=(18, 5))
    for idx, (elev, azim, label) in enumerate([
        (25, 45, "Front"), (25, 135, "Side"), (90, 0, "Top"), (0, 0, "Edge")
    ]):
        ax = fig.add_subplot(1, 4, idx + 1, projection='3d')

        for i, name in enumerate(COMBINATOR_NAMES):
            family = get_family(name)
            color = FAMILY_COLORS.get(family, "#999999")
            is_anti = name.startswith("ā")
            x, y, z = coords_scaled[i, 0], coords_scaled[i, 1], coords_scaled[i, 2]

            if is_anti:
                ax.scatter(x, y, z, c='white', edgecolors=color, s=60,
                          marker='o', linewidths=1.5, alpha=0.6)
            else:
                ax.scatter(x, y, z, c=color, s=120, marker='o',
                          edgecolors='black', linewidths=0.5, alpha=0.9)
                ax.text(x, y, z + 0.02, name, fontsize=7, ha='center')

        ax.view_init(elev=elev, azim=azim)
        ax.set_title(f'{label}\n(elev={elev}°, azim={azim}°)', fontsize=10)
        ax.set_xlabel('PC0', fontsize=8)
        ax.set_ylabel('PC1', fontsize=8)
        ax.set_zlabel('PC2', fontsize=8)

    fig.suptitle('Crystal Core (PC0×PC1×PC2) — Four Viewing Angles',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(str(output_dir / "crystal_3d_angles.png"), dpi=150,
                bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {output_dir / 'crystal_3d_angles.png'}", file=sys.stderr)

    # 5. Zone comparison: A vs B vs C
    zones = {}
    try:
        from crystal import ZONE_A_TARGETS, ZONE_B_TARGETS, ZONE_C_TARGETS
    except ImportError:
        import sys as _sys
        _sys.path.insert(0, str(Path(__file__).parent))
        from crystal import ZONE_A_TARGETS, ZONE_B_TARGETS, ZONE_C_TARGETS
    zone_data = {
        'A (Encode)': np.array(ZONE_A_TARGETS),
        'B (Compute)': np.array(ZONE_B_TARGETS),
        'C (Converge)': np.array(ZONE_C_TARGETS),
    }

    fig = plt.figure(figsize=(18, 5))
    for idx, (zone_name, zone_target) in enumerate(zone_data.items()):
        z_vals, z_vecs = np.linalg.eigh(zone_target)
        z_idx = np.argsort(z_vals)[::-1]
        z_vals = z_vals[z_idx]
        z_vecs = z_vecs[:, z_idx]
        z_coords = zone_target @ z_vecs * np.sqrt(np.abs(z_vals))[np.newaxis, :]

        ax = fig.add_subplot(1, 3, idx + 1, projection='3d')
        for i, name in enumerate(COMBINATOR_NAMES):
            family = get_family(name)
            color = FAMILY_COLORS.get(family, "#999999")
            is_anti = name.startswith("ā")
            x, y, z = z_coords[i, 0], z_coords[i, 1], z_coords[i, 2]

            if is_anti:
                ax.scatter(x, y, z, c='white', edgecolors=color, s=50,
                          marker='o', linewidths=1.5, alpha=0.5)
            else:
                ax.scatter(x, y, z, c=color, s=100, marker='o',
                          edgecolors='black', linewidths=0.5, alpha=0.9)
                ax.text(x, y, z + 0.02, name, fontsize=7, ha='center')

        ax.view_init(elev=25, azim=135)
        ax.set_title(f'Zone {zone_name}\nλ₀/λ₁={z_vals[0]/z_vals[1]:.2f}',
                     fontsize=11, fontweight='bold')
        ax.set_xlabel('PC0', fontsize=8)
        ax.set_ylabel('PC1', fontsize=8)
        ax.set_zlabel('PC2', fontsize=8)

    fig.suptitle('Crystal Lattice Across Three Zones — The Breathing Pattern',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(str(output_dir / "crystal_zones_3d.png"), dpi=150,
                bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {output_dir / 'crystal_zones_3d.png'}", file=sys.stderr)

    print(f"\nAll visualizations saved to {output_dir}", file=sys.stderr)
    print(f"  eigenvalue_spectrum.png   — eigenvalue bar chart + cumulative", file=sys.stderr)
    print(f"  crystal_2d_overview.png   — 6-panel 2D projections", file=sys.stderr)
    print(f"  crystal_3d_pc012.png      — core: comp×sel×term", file=sys.stderr)
    print(f"  crystal_3d_pc013.png      — routing view", file=sys.stderr)
    print(f"  crystal_3d_pc023.png      — structure view", file=sys.stderr)
    print(f"  crystal_3d_pc123.png      — operations view", file=sys.stderr)
    print(f"  crystal_3d_pc014.png      — dispatch view", file=sys.stderr)
    print(f"  crystal_3d_pc234.png      — fine structure", file=sys.stderr)
    print(f"  crystal_3d_angles.png     — core from 4 angles", file=sys.stderr)
    print(f"  crystal_zones_3d.png      — A/B/C zones (breathing)", file=sys.stderr)


if __name__ == "__main__":
    main()
