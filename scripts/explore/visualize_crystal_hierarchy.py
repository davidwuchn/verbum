#!/usr/bin/env python3
"""
Visualize the recursive holographic crystal hierarchy.

Four levels of emergence, each arising from the intersection of the level above:

    Level 0 (top):    Training examples — individual "photographs"
    Level 1 (mid):    Domain holograms — piles of photographs intersect
    Level 2 (lower):  Model crystals — piles of holograms intersect
    Level 3 (bottom): Universal lattice — piles of crystals intersect → KIBC

The 4th dimension is encoded via color (crystal quality / alignment strength)
and size (selectivity / clustering ratio), while XYZ positions encode the
spatial hierarchy and depth structure.

Data-driven from actual Verbum experiments:
  - crystal_comparison_results.json  (5 models × 4 depths × 4 domains)
  - lambda_kernel_results.json       (20 operations, clustering ratios)
  - tomography_results.json          (cross-model RSA at 5 layers)
  - combinator_probe_results.json    (KIBC selectivity profiles)
"""

import json
import math
import numpy as np
from pathlib import Path

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

RESULTS = Path(__file__).resolve().parents[2] / "results"

with open(RESULTS / "crystal-comparison" / "crystal_comparison_results.json") as f:
    crystal = json.load(f)

with open(RESULTS / "holographic-extraction" / "lambda_kernel_results.json") as f:
    kernel = json.load(f)

with open(RESULTS / "holographic-extraction" / "tomography_results.json") as f:
    tomo = json.load(f)

with open(RESULTS / "combinator-probe" / "combinator_probe_results.json") as f:
    comb = json.load(f)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODELS = ["qwen3-14b", "olmo-2-13b", "mistral-7b", "pythia-1.4b", "pythia-160m"]
DOMAINS = ["tool_call", "code", "factual", "reasoning"]
DEPTHS = ["shallow", "mid_shallow", "mid_deep", "deep"]
COMBINATORS = ["K", "I", "B", "C"]
DEPTH_Z = {"shallow": 0.0, "mid_shallow": 1.0, "mid_deep": 2.0, "deep": 3.0}

# Vertical Y positions for the four levels (bottom to top)
Y_UNIVERSAL = 0.0   # Level 3: universal lattice (bottom — the irreducible kernel)
Y_CRYSTALS  = 4.0   # Level 2: per-model crystals
Y_HOLOGRAMS = 8.0   # Level 1: domain holograms
Y_PHOTOS    = 12.0  # Level 0: training examples (top)

# Domain colors (consistent throughout)
DOMAIN_COLORS = {
    "tool_call":  "rgba(46, 134, 193, {a})",   # blue
    "code":       "rgba(39, 174, 96, {a})",     # green
    "factual":    "rgba(231, 76, 60, {a})",     # red
    "reasoning":  "rgba(155, 89, 182, {a})",    # purple
}

# Model colors for crystal level
MODEL_COLORS = {
    "qwen3-14b":   "rgba(52, 152, 219, {a})",   # strong blue
    "olmo-2-13b":  "rgba(46, 204, 113, {a})",    # emerald
    "mistral-7b":  "rgba(241, 196, 15, {a})",    # gold
    "pythia-1.4b": "rgba(230, 126, 34, {a})",    # orange
    "pythia-160m": "rgba(149, 165, 166, {a})",   # grey (degenerate)
}

COMBINATOR_COLORS = {
    "K": "rgba(231, 76, 60, {a})",    # red — select/discard
    "I": "rgba(52, 152, 219, {a})",   # blue — identity/binding
    "B": "rgba(46, 204, 113, {a})",   # green — compose
    "C": "rgba(155, 89, 182, {a})",   # purple — flip
}


# ---------------------------------------------------------------------------
# Extract numeric data
# ---------------------------------------------------------------------------

def get_crystal_quality(model, depth, domain):
    """Get crystal quality metrics for a specific model/depth/domain."""
    return crystal["crystal_quality"][model][depth][domain]


def get_cross_model_cos(pair):
    """Get mean cross-model cosine for a pair."""
    return crystal["cross_model_alignment"][pair]["mean_cos"]


def get_cross_model_depth(pair, depth):
    """Get per-depth cross-model cosine."""
    return crystal["cross_model_alignment"][pair]["depths"][depth]["cos_after"]


# Compute domain-averaged crystal quality per model
def domain_avg_crystal(model):
    """Average mosaicity across all depths and domains for a model."""
    vals = []
    for d in DEPTHS:
        for dom in DOMAINS:
            vals.append(get_crystal_quality(model, d, dom)["mosaicity"])
    return np.mean(vals)


# RSA per layer
rsa_by_layer = {r["layer"]: r["rsa_pearson"] for r in tomo["rsa"]["layers"]}

# Axis clustering (operations)
op_clustering = {ax["axis"]: ax["ratio"] for ax in kernel["axis_clustering"]}

# Combinator selectivity means
comb_selectivity = {c: comb["combinator_selectivity"][c]["mean"] for c in COMBINATORS}


# ---------------------------------------------------------------------------
# Build the visualization with plotly
# ---------------------------------------------------------------------------

import plotly.graph_objects as go

fig = go.Figure()


# ===== LEVEL 0: Training examples (photographs) — top =====
# Abstract representation: scattered small points representing raw training data
# These are the raw "photographs" before any intersection
np.random.seed(42)
n_photos = 200
photo_x = np.random.normal(0, 3.5, n_photos)
photo_z = np.random.normal(0, 3.5, n_photos)
photo_y = np.full(n_photos, Y_PHOTOS) + np.random.normal(0, 0.3, n_photos)

# Color by which domain they'll eventually contribute to
photo_domains = np.random.choice(DOMAINS, n_photos)
photo_colors = []
for d in photo_domains:
    photo_colors.append(DOMAIN_COLORS[d].format(a=0.3))

fig.add_trace(go.Scatter3d(
    x=photo_x, y=photo_y, z=photo_z,
    mode='markers',
    marker=dict(size=2, color=photo_colors),
    name='Training examples (photographs)',
    hovertext=[f"Training example\nDomain tendency: {d}" for d in photo_domains],
    legendgroup='photos',
))


# ===== LEVEL 1: Domain holograms — piles of photographs intersect =====
# 4 domains × 4 depths = 16 hologram clusters
# Size = selectivity (how strongly the domain separates)
# Color = domain color
# Alpha = 1 - mosaicity (higher quality = more opaque)

# Use the BEST model (Qwen) to represent the "ideal" hologram per domain
# since holograms are the domain-level structure that emerges
hologram_traces_x = []
hologram_traces_y = []
hologram_traces_z = []
hologram_colors = []
hologram_sizes = []
hologram_texts = []

# Arrange domains in a 2×2 grid
domain_positions = {
    "tool_call":  (-2.5, -2.5),
    "code":       ( 2.5, -2.5),
    "factual":    (-2.5,  2.5),
    "reasoning":  ( 2.5,  2.5),
}

for dom in DOMAINS:
    dx, dz = domain_positions[dom]
    for di, depth in enumerate(DEPTHS):
        # Average across universal-tier models for this domain/depth
        mosaicities = []
        selectivities = []
        coherences = []
        for m in ["qwen3-14b", "olmo-2-13b", "mistral-7b", "pythia-1.4b"]:
            q = get_crystal_quality(m, depth, dom)
            mosaicities.append(q["mosaicity"])
            selectivities.append(q["selectivity_mean"])
            coherences.append(q["coherence_mean_angle"])

        avg_mos = np.mean(mosaicities)
        avg_sel = np.mean(selectivities)
        avg_coh = np.mean(coherences)

        # Position: spread along depth axis
        x = dx + (di - 1.5) * 0.8
        z = dz
        y = Y_HOLOGRAMS + di * 0.3 - 0.45

        alpha = max(0.2, 1.0 - avg_mos)
        size = max(4, avg_sel / 10)

        hologram_traces_x.append(x)
        hologram_traces_y.append(y)
        hologram_traces_z.append(z)
        hologram_colors.append(DOMAIN_COLORS[dom].format(a=alpha))
        hologram_sizes.append(size)
        hologram_texts.append(
            f"Domain: {dom}<br>Depth: {depth}<br>"
            f"Mosaicity: {avg_mos:.3f}<br>"
            f"Selectivity: {avg_sel:.1f}<br>"
            f"Coherence: {avg_coh:.1f}°"
        )

fig.add_trace(go.Scatter3d(
    x=hologram_traces_x, y=hologram_traces_y, z=hologram_traces_z,
    mode='markers',
    marker=dict(
        size=hologram_sizes,
        color=hologram_colors,
        symbol='diamond',
        line=dict(width=1, color='rgba(255,255,255,0.5)')
    ),
    name='Domain holograms (photograph piles)',
    hovertext=hologram_texts,
    legendgroup='holograms',
))

# Domain labels
for dom in DOMAINS:
    dx, dz = domain_positions[dom]
    fig.add_trace(go.Scatter3d(
        x=[dx], y=[Y_HOLOGRAMS + 1.2], z=[dz],
        mode='text',
        text=[dom.replace("_", " ").title()],
        textfont=dict(size=11, color=DOMAIN_COLORS[dom].format(a=0.9)),
        showlegend=False,
    ))


# ===== Convergence funnels: photos → holograms =====
# Draw translucent cone shapes showing intersection
for dom in DOMAINS:
    dx, dz = domain_positions[dom]
    # Lines from scattered photo region down to hologram cluster
    n_funnel = 12
    for i in range(n_funnel):
        angle = 2 * math.pi * i / n_funnel
        px = dx + 3.0 * math.cos(angle)
        pz = dz + 3.0 * math.sin(angle)
        fig.add_trace(go.Scatter3d(
            x=[px, dx], y=[Y_PHOTOS - 0.5, Y_HOLOGRAMS + 0.5], z=[pz, dz],
            mode='lines',
            line=dict(width=1, color=DOMAIN_COLORS[dom].format(a=0.08)),
            showlegend=False,
            hoverinfo='skip',
        ))


# ===== LEVEL 2: Model crystals — piles of holograms intersect =====
# 5 models, each with their own crystal quality
# Arranged in a circle, with depth encoded vertically

model_angles = {m: 2 * math.pi * i / 5 for i, m in enumerate(MODELS)}
crystal_radius = 2.5

for model in MODELS:
    angle = model_angles[model]
    mx = crystal_radius * math.cos(angle)
    mz = crystal_radius * math.sin(angle)

    # One point per depth, showing the crystal at that depth
    xs, ys, zs = [], [], []
    colors, sizes, texts = [], [], []

    for di, depth in enumerate(DEPTHS):
        # Average across domains for this model/depth
        mos_vals = []
        sel_vals = []
        coh_vals = []
        for dom in DOMAINS:
            q = get_crystal_quality(model, depth, dom)
            mos_vals.append(q["mosaicity"])
            sel_vals.append(q["selectivity_mean"])
            coh_vals.append(q["coherence_mean_angle"])

        avg_mos = np.mean(mos_vals)
        avg_sel = np.mean(sel_vals)
        avg_coh = np.mean(coh_vals)

        x = mx
        z = mz
        y = Y_CRYSTALS + di * 0.5 - 0.75

        alpha = max(0.3, 1.0 - avg_mos)
        size = max(5, avg_sel / 8)

        # Degenerate Pythia-160m gets different treatment
        if model == "pythia-160m":
            alpha *= 0.5

        xs.append(x)
        ys.append(y)
        zs.append(z)
        colors.append(MODEL_COLORS[model].format(a=alpha))
        sizes.append(size)
        texts.append(
            f"Model: {model}<br>Depth: {depth}<br>"
            f"Mosaicity: {avg_mos:.3f}<br>"
            f"Selectivity: {avg_sel:.1f}<br>"
            f"Coherence: {avg_coh:.1f}°"
        )

    fig.add_trace(go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode='markers+lines',
        marker=dict(size=sizes, color=colors, symbol='circle',
                    line=dict(width=1, color='rgba(255,255,255,0.4)')),
        line=dict(width=2, color=MODEL_COLORS[model].format(a=0.5)),
        name=f'Crystal: {model}',
        hovertext=texts,
        legendgroup='crystals',
    ))


# ===== Convergence lines: holograms → crystals =====
# Each model's crystal is formed from the intersection of all domain holograms
for model in MODELS:
    angle = model_angles[model]
    mx = crystal_radius * math.cos(angle)
    mz = crystal_radius * math.sin(angle)

    for dom in DOMAINS:
        dx, dz = domain_positions[dom]
        fig.add_trace(go.Scatter3d(
            x=[dx, mx], y=[Y_HOLOGRAMS - 0.5, Y_CRYSTALS + 0.8], z=[dz, mz],
            mode='lines',
            line=dict(width=1, color=MODEL_COLORS[model].format(a=0.06)),
            showlegend=False,
            hoverinfo='skip',
        ))


# ===== Cross-model alignment arcs =====
# Lines between model pairs, colored by alignment strength
universal_models = ["qwen3-14b", "olmo-2-13b", "mistral-7b", "pythia-1.4b"]
for i, m1 in enumerate(universal_models):
    for m2 in universal_models[i+1:]:
        pair = f"{m1}_vs_{m2}"
        if pair not in crystal["cross_model_alignment"]:
            pair = f"{m2}_vs_{m1}"
        if pair in crystal["cross_model_alignment"]:
            cos = get_cross_model_cos(pair)

            a1 = model_angles[m1]
            a2 = model_angles[m2]
            x1, z1 = crystal_radius * math.cos(a1), crystal_radius * math.sin(a1)
            x2, z2 = crystal_radius * math.cos(a2), crystal_radius * math.sin(a2)

            # Arc through midpoint slightly above
            mid_x = (x1 + x2) / 2
            mid_z = (z1 + z2) / 2
            mid_y = Y_CRYSTALS + 0.2

            # Color = alignment strength (green = strong, red = weak)
            alpha = cos * 0.6
            if cos > 0.8:
                arc_color = f"rgba(46, 204, 113, {alpha})"  # green
            elif cos > 0.6:
                arc_color = f"rgba(241, 196, 15, {alpha})"  # yellow
            else:
                arc_color = f"rgba(231, 76, 60, {alpha})"   # red

            fig.add_trace(go.Scatter3d(
                x=[x1, mid_x, x2],
                y=[Y_CRYSTALS, mid_y, Y_CRYSTALS],
                z=[z1, mid_z, z2],
                mode='lines',
                line=dict(width=max(1, cos * 4), color=arc_color),
                showlegend=False,
                hovertext=f"{pair}<br>Cosine: {cos:.4f}",
                hoverinfo='text',
            ))


# ===== LEVEL 3: Universal lattice — KIBC at the bottom =====
# The irreducible kernel: K, I, B, C combinators
# Arranged as a tetrahedron at the center bottom

# Tetrahedron vertices for KIBC
tet_scale = 1.2
tet_positions = {
    "K": (tet_scale * math.cos(0),
          Y_UNIVERSAL,
          tet_scale * math.sin(0)),
    "I": (tet_scale * math.cos(2*math.pi/3),
          Y_UNIVERSAL + 0.4,
          tet_scale * math.sin(2*math.pi/3)),
    "B": (tet_scale * math.cos(4*math.pi/3),
          Y_UNIVERSAL,
          tet_scale * math.sin(4*math.pi/3)),
    "C": (0, Y_UNIVERSAL - 0.5, 0),  # center bottom
}

# Size from selectivity, color from combinator identity
for c_name in COMBINATORS:
    px, py, pz = tet_positions[c_name]
    sel = comb_selectivity[c_name]
    size = max(8, sel * 120)  # Scale up for visibility

    fig.add_trace(go.Scatter3d(
        x=[px], y=[py], z=[pz],
        mode='markers+text',
        marker=dict(
            size=size,
            color=COMBINATOR_COLORS[c_name].format(a=0.9),
            symbol='diamond',
            line=dict(width=2, color='white'),
        ),
        text=[c_name],
        textfont=dict(size=14, color='white'),
        textposition='middle center',
        name=f'Combinator {c_name} (sel={sel:.4f})',
        legendgroup='universal',
        hovertext=(
            f"Combinator: {c_name}<br>"
            f"Mean selectivity: {sel:.4f}<br>"
            f"{'K=select/discard' if c_name=='K' else 'I=identity/bind' if c_name=='I' else 'B=compose' if c_name=='B' else 'C=flip'}"
        ),
    ))

# Tetrahedron edges (the lattice bonds)
tet_edges = [("K","I"), ("K","B"), ("K","C"), ("I","B"), ("I","C"), ("B","C")]
for c1, c2 in tet_edges:
    x1, y1, z1 = tet_positions[c1]
    x2, y2, z2 = tet_positions[c2]
    fig.add_trace(go.Scatter3d(
        x=[x1, x2], y=[y1, y2], z=[z1, z2],
        mode='lines',
        line=dict(width=3, color='rgba(255, 255, 255, 0.6)'),
        showlegend=False,
        hoverinfo='skip',
    ))


# ===== Convergence lines: crystals → universal =====
# All model crystals converge to the universal KIBC lattice
for model in MODELS:
    angle = model_angles[model]
    mx = crystal_radius * math.cos(angle)
    mz = crystal_radius * math.sin(angle)

    # Connect to the center of the KIBC tetrahedron
    center_x = np.mean([tet_positions[c][0] for c in COMBINATORS])
    center_z = np.mean([tet_positions[c][2] for c in COMBINATORS])

    # Alpha based on model quality (universal-tier vs degenerate)
    alpha = 0.15 if model != "pythia-160m" else 0.05

    fig.add_trace(go.Scatter3d(
        x=[mx, center_x], y=[Y_CRYSTALS - 0.5, Y_UNIVERSAL + 0.8], z=[mz, center_z],
        mode='lines',
        line=dict(width=2, color=MODEL_COLORS[model].format(a=alpha)),
        showlegend=False,
        hoverinfo='skip',
    ))


# ===== Lambda kernel operations orbiting the lattice =====
# Show the 14 operations with their clustering ratios orbiting the KIBC core
ops_sorted = sorted(kernel["axis_clustering"], key=lambda x: x["ratio"], reverse=True)
n_ops = len(ops_sorted)

for i, op in enumerate(ops_sorted):
    angle = 2 * math.pi * i / n_ops
    r = 2.5  # orbit radius
    x = r * math.cos(angle)
    z = r * math.sin(angle)
    y = Y_UNIVERSAL - 0.2

    ratio = op["ratio"]
    name = op["axis"].replace("lambda_", "").replace("contrast_", "Δ")

    # Size and alpha from clustering ratio
    # ratio > 1.0 = distinct operation, < 1.0 = superposed
    if ratio > 1.0:
        color = f"rgba(46, 204, 113, {min(1.0, (ratio - 1.0) * 5 + 0.3)})"
        size = 3 + (ratio - 1.0) * 30
    else:
        color = f"rgba(149, 165, 166, {max(0.2, ratio * 0.4)})"
        size = 2

    fig.add_trace(go.Scatter3d(
        x=[x], y=[y], z=[z],
        mode='markers+text',
        marker=dict(size=size, color=color),
        text=[name],
        textfont=dict(size=8, color=color),
        textposition='top center',
        showlegend=False,
        hovertext=(
            f"Operation: {op['axis']}<br>"
            f"Clustering ratio: {ratio:.4f}<br>"
            f"Within-sim: {op['within']:.4f}<br>"
            f"Between-sim: {op['between']:.4f}"
        ),
    ))


# ===== RSA correlation indicator — the "spine" of universal agreement =====
# Vertical axis showing RSA strength at each depth
rsa_layers_sorted = sorted(rsa_by_layer.items())
rsa_x = [0.0] * len(rsa_layers_sorted)
rsa_z = [4.5] * len(rsa_layers_sorted)
rsa_y = [Y_CRYSTALS - 0.5 + i * 0.5 for i in range(len(rsa_layers_sorted))]
rsa_sizes = [r * 12 for _, r in rsa_layers_sorted]
rsa_colors = [f"rgba(241, 196, 15, {r})" for _, r in rsa_layers_sorted]
rsa_texts = [f"RSA L{layer}: r={r:.3f}" for layer, r in rsa_layers_sorted]

fig.add_trace(go.Scatter3d(
    x=rsa_x, y=rsa_y, z=rsa_z,
    mode='markers+lines',
    marker=dict(size=rsa_sizes, color=rsa_colors, symbol='square'),
    line=dict(width=2, color='rgba(241, 196, 15, 0.3)'),
    name='Cross-model RSA (universal agreement)',
    hovertext=rsa_texts,
    legendgroup='rsa',
))


# ===== Level labels =====
label_x = -6.0
label_z = 0.0
level_labels = [
    (Y_PHOTOS,    "Level 0: Training Examples\n(photographs)"),
    (Y_HOLOGRAMS, "Level 1: Domain Holograms\n(photograph piles intersect)"),
    (Y_CRYSTALS,  "Level 2: Model Crystals\n(hologram piles intersect)"),
    (Y_UNIVERSAL, "Level 3: Universal Lattice\n(crystal piles intersect → KIBC)"),
]

for y, text in level_labels:
    fig.add_trace(go.Scatter3d(
        x=[label_x], y=[y], z=[label_z],
        mode='text',
        text=[text],
        textfont=dict(size=10, color='rgba(200, 200, 200, 0.8)'),
        showlegend=False,
    ))


# ===== Downward arrows between levels (vertical flow indicators) =====
for y_top, y_bot in [(Y_PHOTOS, Y_HOLOGRAMS), (Y_HOLOGRAMS, Y_CRYSTALS), (Y_CRYSTALS, Y_UNIVERSAL)]:
    fig.add_trace(go.Scatter3d(
        x=[-5.5, -5.5], y=[y_top - 0.8, y_bot + 0.8], z=[0, 0],
        mode='lines',
        line=dict(width=3, color='rgba(200, 200, 200, 0.3)'),
        showlegend=False,
        hoverinfo='skip',
    ))
    # Arrow head
    fig.add_trace(go.Scatter3d(
        x=[-5.5], y=[y_bot + 0.8], z=[0],
        mode='markers',
        marker=dict(size=4, color='rgba(200, 200, 200, 0.5)', symbol='diamond'),
        showlegend=False,
        hoverinfo='skip',
    ))


# ===== Layout =====
fig.update_layout(
    title=dict(
        text=(
            "<b>The Recursive Holographic Hierarchy</b><br>"
            "<sub>Training examples → domain holograms → model crystals → universal KIBC lattice<br>"
            "Each level = intersection of the level above. Size = selectivity. Opacity = crystal quality (1-mosaicity).</sub>"
        ),
        font=dict(size=16, color='white'),
        x=0.5,
    ),
    scene=dict(
        xaxis=dict(
            title='', showgrid=False, showticklabels=False,
            zeroline=False, showline=False,
            backgroundcolor='rgba(0,0,0,0)',
        ),
        yaxis=dict(
            title='← Universal lattice ... Training data →',
            showgrid=False, showticklabels=False,
            zeroline=False, showline=False,
            backgroundcolor='rgba(0,0,0,0)',
        ),
        zaxis=dict(
            title='', showgrid=False, showticklabels=False,
            zeroline=False, showline=False,
            backgroundcolor='rgba(0,0,0,0)',
        ),
        bgcolor='rgb(10, 10, 20)',
        camera=dict(
            eye=dict(x=1.8, y=0.4, z=0.8),
            up=dict(x=0, y=1, z=0),
        ),
        aspectratio=dict(x=1.2, y=2.0, z=1.2),
    ),
    paper_bgcolor='rgb(10, 10, 20)',
    plot_bgcolor='rgb(10, 10, 20)',
    font=dict(color='white'),
    legend=dict(
        bgcolor='rgba(20, 20, 40, 0.8)',
        font=dict(size=10, color='white'),
        x=0.02, y=0.98,
    ),
    margin=dict(l=0, r=0, t=80, b=0),
    width=1400,
    height=900,
)

# ===== Save =====
output_dir = Path(__file__).resolve().parents[2] / "outputs" / "crystal_hierarchy"
output_dir.mkdir(parents=True, exist_ok=True)

html_path = output_dir / "crystal_hierarchy_4d.html"
fig.write_html(str(html_path), include_plotlyjs='cdn')
print(f"✅ Interactive visualization saved: {html_path}")

# Also save a static image if kaleido is available
try:
    png_path = output_dir / "crystal_hierarchy_4d.png"
    fig.write_image(str(png_path), width=1400, height=900, scale=2)
    print(f"✅ Static image saved: {png_path}")
except Exception as e:
    print(f"⚠️  Static image skipped (install kaleido for PNG): {e}")

print("\nData summary:")
print(f"  Models: {len(MODELS)}")
print(f"  Domains: {len(DOMAINS)}")
print(f"  Depths: {len(DEPTHS)}")
print(f"  Crystal quality points: {len(MODELS) * len(DEPTHS) * len(DOMAINS)}")
print(f"  Cross-model pairs: {len(crystal['cross_model_alignment'])}")
print(f"  Lambda kernel operations: {len(kernel['axis_clustering'])}")
print(f"  RSA layers: {len(rsa_by_layer)}")
print(f"  Mean cross-model cos (universal tier): {np.mean([get_cross_model_cos(p) for p in crystal['cross_model_alignment'] if 'pythia-160m' not in p]):.4f}")
