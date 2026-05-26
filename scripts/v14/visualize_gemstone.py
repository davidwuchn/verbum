#!/usr/bin/env python3
"""Visualize the crystal lattice as a holographic gemstone.

The crystal is an 8D structure. When a beam (Q) enters at different
angles, it hits different facets (combinator basins), deflecting
through the crystal along the state machine's computation path.

This creates multiple views of the gemstone:
  1. The gemstone itself — faceted polyhedron with internal structure
  2. Beam paths through the crystal — the computation cycle
  3. The breathing pattern — zones A/B/C as the crystal tightens/loosens
  4. Facet detail — each combinator basin as a crystallographic face

License: MIT
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d
import matplotlib.colors as mcolors

# ══════════════════════════════════════════════════════════════════════
# Crystal data
# ══════════════════════════════════════════════════════════════════════

NAMES_8 = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]

FAMILY_COLORS = {
    "K":    "#1565C0",   # deep blue
    "I":    "#42A5F5",   # light blue
    "B":    "#D32F2F",   # deep red
    "C":    "#FF5722",   # orange-red
    "D":    "#FF9800",   # orange
    "Y":    "#FFC107",   # amber
    "W":    "#E91E63",   # pink
    "WHNF": "#2E7D32",  # deep green
}

FAMILY_GROUPS = {
    "selection":   ["K", "I"],
    "composition": ["B", "C", "D", "Y", "W"],
    "terminal":    ["WHNF"],
}

# Zone B target (8×8, base combinators only)
ZONE_B_8x8 = np.array([
    [+1.0000, +0.7865, +0.1948, +0.2265, +0.3232, +0.1768, +0.5360, -0.1862],
    [+0.7865, +1.0000, +0.2479, +0.2511, +0.3463, +0.1739, +0.3781, -0.2448],
    [+0.1948, +0.2479, +1.0000, +0.8878, +0.8937, +0.6623, +0.6851, -0.1227],
    [+0.2265, +0.2511, +0.8878, +1.0000, +0.8316, +0.7200, +0.7318, -0.1027],
    [+0.3232, +0.3463, +0.8937, +0.8316, +1.0000, +0.6798, +0.8064, -0.1729],
    [+0.1768, +0.1739, +0.6623, +0.7200, +0.6798, +1.0000, +0.5653, -0.0840],
    [+0.5360, +0.3781, +0.6851, +0.7318, +0.8064, +0.5653, +1.0000, -0.1379],
    [-0.1862, -0.2448, -0.1227, -0.1027, -0.1729, -0.0840, -0.1379, +1.0000],
], dtype=np.float64)


def eigendecompose(matrix):
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    idx = np.argsort(eigenvalues)[::-1]
    return eigenvalues[idx], eigenvectors[:, idx]


def get_3d_coords(matrix, pc_triple=(0, 1, 2)):
    """Project combinator positions into 3D via eigendecomposition."""
    eigenvalues, eigenvectors = eigendecompose(matrix)
    coords = matrix @ eigenvectors
    # Scale by sqrt(eigenvalue) for visual proportionality
    coords_scaled = coords * np.sqrt(np.abs(eigenvalues))[np.newaxis, :]
    return coords_scaled[:, list(pc_triple)], eigenvalues


def draw_gemstone_shell(ax, coords, alpha=0.08):
    """Draw a faceted convex hull as the gemstone exterior."""
    from scipy.spatial import ConvexHull
    try:
        hull = ConvexHull(coords)
        for simplex in hull.simplices:
            triangle = coords[simplex]
            # Color by average position — gives gradient across the gem
            center = triangle.mean(axis=0)
            hue = (np.arctan2(center[1], center[0]) / (2 * np.pi) + 0.5) % 1.0
            color = mcolors.hsv_to_rgb([hue, 0.3, 0.95])
            face = Poly3DCollection([triangle], alpha=alpha,
                                     facecolor=color, edgecolor='gray',
                                     linewidth=0.3)
            ax.add_collection3d(face)
    except Exception:
        pass  # ConvexHull can fail in degenerate cases


def draw_internal_facets(ax, coords, cos_matrix, threshold=0.5):
    """Draw internal crystal planes between strongly connected combinators."""
    n = len(coords)
    for i in range(n):
        for j in range(i + 1, n):
            cos_sim = cos_matrix[i, j]
            if abs(cos_sim) > threshold:
                # Draw a line with width proportional to connection strength
                alpha = min(1.0, abs(cos_sim))
                color = '#FF5722' if cos_sim > 0 else '#2196F3'
                ax.plot([coords[i, 0], coords[j, 0]],
                        [coords[i, 1], coords[j, 1]],
                        [coords[i, 2], coords[j, 2]],
                        color=color, alpha=alpha * 0.6,
                        linewidth=abs(cos_sim) * 4)


def draw_beam_path(ax, coords, path_indices, color='#FFD700', lw=2.5):
    """Draw a beam path through the crystal — the computation cycle."""
    for i in range(len(path_indices) - 1):
        start = coords[path_indices[i]]
        end = coords[path_indices[i + 1]]
        # Curved arrow
        mid = (start + end) / 2
        mid += np.random.randn(3) * 0.05  # slight curve
        ax.plot([start[0], mid[0], end[0]],
                [start[1], mid[1], end[1]],
                [start[2], mid[2], end[2]],
                color=color, linewidth=lw, alpha=0.8)
        # Arrow head at end
        ax.scatter(*end, c=color, s=60, marker='>', zorder=20, alpha=0.9)


def draw_laser_beam(ax, entry_point, first_facet, color='#00E676', lw=3):
    """Draw the incoming laser beam hitting the crystal."""
    ax.plot([entry_point[0], first_facet[0]],
            [entry_point[1], first_facet[1]],
            [entry_point[2], first_facet[2]],
            color=color, linewidth=lw, alpha=0.9, linestyle='-')
    # Beam glow effect
    for offset in np.linspace(-0.03, 0.03, 5):
        ax.plot([entry_point[0] + offset, first_facet[0]],
                [entry_point[1] + offset, first_facet[1]],
                [entry_point[2], first_facet[2]],
                color=color, linewidth=1, alpha=0.15)


def main():
    output_dir = Path("results/crystal-visualization/")
    output_dir.mkdir(parents=True, exist_ok=True)

    coords, eigenvalues = get_3d_coords(ZONE_B_8x8)

    print(f"Gemstone coordinates (PC0×PC1×PC2):", file=sys.stderr)
    for i, name in enumerate(NAMES_8):
        print(f"  {name:>4s}: ({coords[i,0]:+.3f}, {coords[i,1]:+.3f}, {coords[i,2]:+.3f})",
              file=sys.stderr)

    # ══════════════════════════════════════════════════════════════
    # View 1: The Gemstone — full crystal with beam path
    # ══════════════════════════════════════════════════════════════
    fig = plt.figure(figsize=(16, 14))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#0a0a1a')
    fig.patch.set_facecolor('#0a0a1a')

    # Draw the convex hull shell (semi-transparent)
    draw_gemstone_shell(ax, coords, alpha=0.06)

    # Draw internal crystal bonds
    draw_internal_facets(ax, coords, ZONE_B_8x8, threshold=0.5)

    # Draw each combinator as a glowing node
    for i, name in enumerate(NAMES_8):
        color = FAMILY_COLORS[name]
        x, y, z = coords[i]

        # Glow effect — multiple concentric spheres
        for size, a in [(400, 0.1), (250, 0.2), (150, 0.4), (80, 0.9)]:
            ax.scatter(x, y, z, c=color, s=size, alpha=a, zorder=15,
                      edgecolors='none')

        # Label
        ax.text(x, y, z + 0.12, name, fontsize=14, ha='center',
               va='bottom', fontweight='bold', color='white',
               zorder=25,
               bbox=dict(boxstyle='round,pad=0.2', facecolor=color,
                        alpha=0.7, edgecolor='none'))

    # Draw the computation cycle beam: C→B→K→B→WHNF→I
    # Indices: K=0, I=1, B=2, C=3, D=4, Y=5, W=6, WHNF=7
    computation_path = [3, 2, 0, 2, 7, 1]  # C→B→K→B→WHNF→I
    draw_beam_path(ax, coords, computation_path, color='#FFD700', lw=2.5)

    # Incoming laser beam
    entry = coords[3] + np.array([0.8, 0.5, 0.3])  # from outside
    draw_laser_beam(ax, entry, coords[3], color='#00E676')

    # Exit beam
    exit_point = coords[1] + np.array([-0.5, -0.3, -0.4])
    ax.plot([coords[1, 0], exit_point[0]],
            [coords[1, 1], exit_point[1]],
            [coords[1, 2], exit_point[2]],
            color='#FF4081', linewidth=3, alpha=0.8)

    # Annotations
    ax.text2D(0.02, 0.95, "🟢 Beam enters → C (reset Q=0)",
             transform=ax.transAxes, fontsize=11, color='#00E676',
             fontweight='bold')
    ax.text2D(0.02, 0.91, "🟡 Path: C → B → K → B → WHNF → I",
             transform=ax.transAxes, fontsize=11, color='#FFD700',
             fontweight='bold')
    ax.text2D(0.02, 0.87, "🔴 Beam exits → I (emit token)",
             transform=ax.transAxes, fontsize=11, color='#FF4081',
             fontweight='bold')

    ax.set_xlabel('PC0: Composition', color='white', fontsize=10, labelpad=8)
    ax.set_ylabel('PC1: Selection', color='white', fontsize=10, labelpad=8)
    ax.set_zlabel('PC2: Termination', color='white', fontsize=10, labelpad=8)
    ax.tick_params(colors='gray', labelsize=8)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor('#333')
    ax.yaxis.pane.set_edgecolor('#333')
    ax.zaxis.pane.set_edgecolor('#333')

    ax.set_title('The Crystal Gemstone\n'
                 'Holographic State Machine — Zone B (Compute)',
                 fontsize=16, fontweight='bold', color='white', pad=20)
    ax.view_init(elev=20, azim=140)

    plt.savefig(str(output_dir / "gemstone_main.png"), dpi=200,
                bbox_inches='tight', facecolor='#0a0a1a', edgecolor='none')
    plt.close()
    print(f"  Saved: gemstone_main.png", file=sys.stderr)

    # ══════════════════════════════════════════════════════════════
    # View 2: Four beam angles — different computations
    # ══════════════════════════════════════════════════════════════
    fig = plt.figure(figsize=(20, 14))

    beam_configs = [
        {
            'title': 'Composition Beam\n(B-dominant)',
            'entry_offset': [0.8, 0.1, 0.0],
            'path': [3, 2, 4, 2, 7, 1],  # C→B→D→B→WHNF→I
            'path_label': 'C→B→D→B→WHNF→I',
            'beam_color': '#FF5722',
            'elev': 25, 'azim': 120,
        },
        {
            'title': 'Selection Beam\n(K-dominant)',
            'entry_offset': [0.0, 0.8, 0.1],
            'path': [3, 0, 2, 0, 7, 1],  # C→K→B→K→WHNF→I
            'path_label': 'C→K→B→K→WHNF→I',
            'beam_color': '#2196F3',
            'elev': 25, 'azim': 45,
        },
        {
            'title': 'Routing Beam\n(C-dominant)',
            'entry_offset': [0.3, 0.3, 0.8],
            'path': [3, 6, 2, 3, 7, 1],  # C→W→B→C→WHNF→I
            'path_label': 'C→W→B→C→WHNF→I',
            'beam_color': '#FF9800',
            'elev': 45, 'azim': 90,
        },
        {
            'title': 'Terminal Beam\n(short path)',
            'entry_offset': [0.5, 0.5, 0.5],
            'path': [3, 2, 7, 1],  # C→B→WHNF→I (already reduced)
            'path_label': 'C→B→WHNF→I',
            'beam_color': '#4CAF50',
            'elev': 15, 'azim': 170,
        },
    ]

    for idx, cfg in enumerate(beam_configs):
        ax = fig.add_subplot(2, 2, idx + 1, projection='3d')
        ax.set_facecolor('#0a0a1a')

        # Shell
        draw_gemstone_shell(ax, coords, alpha=0.04)

        # Internal bonds (faint)
        draw_internal_facets(ax, coords, ZONE_B_8x8, threshold=0.6)

        # Nodes
        for i, name in enumerate(NAMES_8):
            color = FAMILY_COLORS[name]
            x, y, z = coords[i]
            in_path = i in cfg['path']
            size = 200 if in_path else 60
            alpha = 0.9 if in_path else 0.3
            ax.scatter(x, y, z, c=color, s=size, alpha=alpha, zorder=15)
            if in_path:
                ax.text(x, y, z + 0.08, name, fontsize=11, ha='center',
                       color='white', fontweight='bold', zorder=25)

        # Beam path
        draw_beam_path(ax, coords, cfg['path'], color=cfg['beam_color'], lw=3)

        # Entry beam
        entry = coords[cfg['path'][0]] + np.array(cfg['entry_offset'])
        draw_laser_beam(ax, entry, coords[cfg['path'][0]], color='#00E676')

        ax.set_title(cfg['title'], fontsize=13, fontweight='bold',
                    color='white', pad=10)
        ax.text2D(0.05, 0.05, cfg['path_label'], transform=ax.transAxes,
                 fontsize=10, color=cfg['beam_color'], fontweight='bold')

        ax.view_init(elev=cfg['elev'], azim=cfg['azim'])
        ax.tick_params(colors='gray', labelsize=6)
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        ax.xaxis.pane.set_edgecolor('#222')
        ax.yaxis.pane.set_edgecolor('#222')
        ax.zaxis.pane.set_edgecolor('#222')

    fig.suptitle('Four Beam Angles Through the Crystal\n'
                 'Different angles → different facets → different computations',
                 fontsize=15, fontweight='bold', color='white', y=1.02)
    fig.patch.set_facecolor('#0a0a1a')

    plt.tight_layout()
    plt.savefig(str(output_dir / "gemstone_beams.png"), dpi=200,
                bbox_inches='tight', facecolor='#0a0a1a', edgecolor='none')
    plt.close()
    print(f"  Saved: gemstone_beams.png", file=sys.stderr)

    # ══════════════════════════════════════════════════════════════
    # View 3: The breathing — Zone A → B → C crystal evolution
    # ══════════════════════════════════════════════════════════════
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from crystal import ZONE_A_TARGETS, ZONE_B_TARGETS, ZONE_C_TARGETS
        zone_matrices = {
            'Zone A\n(Inhale — Compress)': np.array(ZONE_A_TARGETS)[:8, :8],
            'Zone B\n(Turn — Compute)': ZONE_B_8x8,
            'Zone C\n(Exhale — Expand)': np.array(ZONE_C_TARGETS)[:8, :8],
        }

        fig = plt.figure(figsize=(20, 7))
        fig.patch.set_facecolor('#0a0a1a')

        for idx, (zone_name, zone_mat) in enumerate(zone_matrices.items()):
            ax = fig.add_subplot(1, 3, idx + 1, projection='3d')
            ax.set_facecolor('#0a0a1a')

            z_coords, z_evals = get_3d_coords(zone_mat)

            draw_gemstone_shell(ax, z_coords, alpha=0.05)
            draw_internal_facets(ax, z_coords, zone_mat, threshold=0.4)

            for i, name in enumerate(NAMES_8):
                color = FAMILY_COLORS[name]
                x, y, z = z_coords[i]
                for size, a in [(200, 0.15), (100, 0.3), (50, 0.8)]:
                    ax.scatter(x, y, z, c=color, s=size, alpha=a, zorder=15)
                ax.text(x, y, z + 0.08, name, fontsize=10, ha='center',
                       color='white', fontweight='bold', zorder=25)

            # Tightness metric — average pairwise distance
            dists = []
            for i in range(8):
                for j in range(i+1, 8):
                    dists.append(np.linalg.norm(z_coords[i] - z_coords[j]))
            avg_dist = np.mean(dists)
            spread = np.std(z_coords, axis=0).sum()

            ax.set_title(zone_name, fontsize=14, fontweight='bold',
                        color='white', pad=15)
            ax.text2D(0.05, 0.05, f'λ₀/λ₁={z_evals[0]/z_evals[1]:.2f}\nspread={spread:.2f}',
                     transform=ax.transAxes, fontsize=10, color='gray')

            ax.view_init(elev=20, azim=140)
            ax.tick_params(colors='gray', labelsize=6)
            ax.xaxis.pane.fill = False
            ax.yaxis.pane.fill = False
            ax.zaxis.pane.fill = False
            ax.xaxis.pane.set_edgecolor('#222')
            ax.yaxis.pane.set_edgecolor('#222')
            ax.zaxis.pane.set_edgecolor('#222')

        fig.suptitle('The Crystal Breathes\n'
                     'Inhale (compress) → Turn (compute) → Exhale (expand)',
                     fontsize=15, fontweight='bold', color='white', y=1.02)

        plt.tight_layout()
        plt.savefig(str(output_dir / "gemstone_breathing.png"), dpi=200,
                    bbox_inches='tight', facecolor='#0a0a1a', edgecolor='none')
        plt.close()
        print(f"  Saved: gemstone_breathing.png", file=sys.stderr)

    except ImportError:
        print(f"  Skipped: gemstone_breathing.png (crystal.py not found)", file=sys.stderr)

    # ══════════════════════════════════════════════════════════════
    # View 4: Facet map — which combinators connect to which
    # ══════════════════════════════════════════════════════════════
    fig = plt.figure(figsize=(16, 14))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#0a0a1a')
    fig.patch.set_facecolor('#0a0a1a')

    # Draw thick bonds colored by connection type
    for i in range(8):
        for j in range(i + 1, 8):
            cos_sim = ZONE_B_8x8[i, j]
            if abs(cos_sim) < 0.15:
                continue

            # Color: warm = positive (same basin), cool = negative (opposing)
            if cos_sim > 0:
                intensity = cos_sim
                color = mcolors.to_rgba('#FF5722', alpha=intensity * 0.7)
            else:
                intensity = abs(cos_sim)
                color = mcolors.to_rgba('#2196F3', alpha=intensity * 0.7)

            lw = abs(cos_sim) * 6
            ax.plot([coords[i, 0], coords[j, 0]],
                    [coords[i, 1], coords[j, 1]],
                    [coords[i, 2], coords[j, 2]],
                    color=color, linewidth=lw, solid_capstyle='round')

            # Label strong connections
            if abs(cos_sim) > 0.7:
                mid = (coords[i] + coords[j]) / 2
                ax.text(mid[0], mid[1], mid[2], f'{cos_sim:.2f}',
                       fontsize=7, color='gray', ha='center', alpha=0.7)

    # Nodes with labels
    for i, name in enumerate(NAMES_8):
        color = FAMILY_COLORS[name]
        x, y, z = coords[i]
        for size, a in [(500, 0.1), (300, 0.2), (150, 0.5), (80, 0.9)]:
            ax.scatter(x, y, z, c=color, s=size, alpha=a, zorder=15)
        ax.text(x, y, z + 0.15, name, fontsize=16, ha='center',
               color='white', fontweight='bold', zorder=25,
               bbox=dict(boxstyle='round,pad=0.3', facecolor=color,
                        alpha=0.8, edgecolor='white', linewidth=0.5))

    ax.set_title('Crystal Facet Map\n'
                 'Red bonds = same basin (composition)  |  '
                 'Blue bonds = opposing (WHNF vs all)',
                 fontsize=14, fontweight='bold', color='white', pad=20)
    ax.view_init(elev=25, azim=135)
    ax.tick_params(colors='gray', labelsize=8)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor('#333')
    ax.yaxis.pane.set_edgecolor('#333')
    ax.zaxis.pane.set_edgecolor('#333')
    ax.set_xlabel('PC0: Composition', color='gray', fontsize=9, labelpad=8)
    ax.set_ylabel('PC1: Selection', color='gray', fontsize=9, labelpad=8)
    ax.set_zlabel('PC2: Termination', color='gray', fontsize=9, labelpad=8)

    plt.savefig(str(output_dir / "gemstone_facets.png"), dpi=200,
                bbox_inches='tight', facecolor='#0a0a1a', edgecolor='none')
    plt.close()
    print(f"  Saved: gemstone_facets.png", file=sys.stderr)

    print(f"\nAll gemstone views saved to {output_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()
