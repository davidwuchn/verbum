#!/usr/bin/env python3
"""Probe TD flip topology — do flips form patterns matching the crystal?

Loads delta plates from a checkpoint and analyzes WHERE flips landed:
1. Per-module flip density (which layers, which projections)
2. Row/column flip density profiles within each flipped module
3. Crystal eigenbasis projection (do flips cluster along specific PCs?)
4. Row-flip correlation with crystal combinator structure
5. Spatial autocorrelation (are flips clustered or scattered?)

The hypothesis: GD creates "dunes" of gradient pressure. TD flips the
peaks. If the dunes have crystal structure, the flip topology should
correlate with crystal eigenvectors — flips should cluster at basin
boundaries (where routing is ambiguous) and be sparse at basin centers
(where routing is unambiguous).

Usage:
    uv run python scripts/v14/probe_td_topology.py \\
        --checkpoint checkpoints/v14-td/step_002000

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

# ══════════════════════════════════════════════════════════════════════
# § 1  Unpack ternary (numpy version, no MLX needed)
# ══════════════════════════════════════════════════════════════════════

def unpack_ternary_np(packed_uint32: np.ndarray) -> np.ndarray:
    """Unpack uint32 [N, K//16] → int8 {-1, 0, +1} [N, K].
    
    Same encoding as pack_ternary_mlx: 16 values per uint32,
    each 2-bit field encodes {0→-1, 1→0, 2→+1}.
    """
    N, K16 = packed_uint32.shape
    K = K16 * 16
    
    # Extract each 2-bit field
    shifts = np.arange(16, dtype=np.uint32) * 2  # [0, 2, 4, ..., 30]
    # packed: (N, K16) → (N, K16, 1), shifts: (16,) → broadcasts
    expanded = packed_uint32[:, :, np.newaxis]  # (N, K16, 1)
    fields = (expanded >> shifts) & 3  # (N, K16, 16)
    
    # Decode: field - 1 → {-1, 0, +1}
    decoded = fields.astype(np.int8) - 1  # (N, K16, 16)
    
    return decoded.reshape(N, K)


# ══════════════════════════════════════════════════════════════════════
# § 2  Crystal eigenbasis (from crystal.py zone targets)
# ══════════════════════════════════════════════════════════════════════

# Order: K I B C D Y W WHNF āK āI āB āC āD āY āW āWHNF
COMBINATOR_NAMES = [
    "K", "I", "B", "C", "D", "Y", "W", "WHNF",
    "āK", "āI", "āB", "āC", "āD", "āY", "āW", "āWHNF",
]

# Zone B target cosine matrix (the compute zone — the crystal proper)
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


def crystal_eigenbasis():
    """Eigendecompose Zone B target → eigenvectors and eigenvalues.
    
    Returns eigenvectors sorted by descending eigenvalue (PC0 = composition).
    """
    eigenvalues, eigenvectors = np.linalg.eigh(ZONE_B_TARGET)
    # eigh returns ascending; flip to descending
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]  # columns are eigenvectors
    return eigenvalues, eigenvectors


# ══════════════════════════════════════════════════════════════════════
# § 3  Analysis functions
# ══════════════════════════════════════════════════════════════════════

def analyze_flip_density(delta: np.ndarray, name: str) -> dict:
    """Analyze spatial distribution of flips in a delta plate.
    
    delta: (N, K) int8, values in {-1, 0, +1}
      +1 = keep teacher sign
      -1 = flipped
       0 = blocked (staging)
    """
    N, K = delta.shape
    flip_mask = (delta == -1)  # boolean (N, K)
    total_flips = flip_mask.sum()
    flip_frac = total_flips / delta.size
    
    if total_flips == 0:
        return {"name": name, "total_flips": 0, "flip_frac": 0.0}
    
    # ── Row density: flip fraction per output row ──
    row_flips = flip_mask.sum(axis=1)  # (N,)
    row_density = row_flips / K  # fraction of each row that's flipped
    
    # ── Column density: flip fraction per input column ──
    col_flips = flip_mask.sum(axis=0)  # (K,)
    col_density = col_flips / N  # fraction of each column that's flipped
    
    # ── Row density statistics ──
    row_stats = {
        "mean": float(row_density.mean()),
        "std": float(row_density.std()),
        "min": float(row_density.min()),
        "max": float(row_density.max()),
        "cv": float(row_density.std() / (row_density.mean() + 1e-10)),
        # Top-10 and bottom-10 rows by flip density
        "top10_rows": np.argsort(row_density)[-10:][::-1].tolist(),
        "top10_density": row_density[np.argsort(row_density)[-10:][::-1]].tolist(),
        "bot10_rows": np.argsort(row_density)[:10].tolist(),
        "bot10_density": row_density[np.argsort(row_density)[:10]].tolist(),
    }
    
    # ── Column density statistics ──
    col_stats = {
        "mean": float(col_density.mean()),
        "std": float(col_density.std()),
        "cv": float(col_density.std() / (col_density.mean() + 1e-10)),
    }
    
    # ── Spatial autocorrelation (are flips clustered?) ──
    # Measure: mean flip density in 8-neighborhood vs random expectation
    # Use row-based blocks for efficiency
    block_size = max(1, N // 32)  # ~32 blocks along rows
    n_blocks_r = N // block_size
    n_blocks_c = K // block_size
    if n_blocks_r > 1 and n_blocks_c > 1:
        block_density = np.zeros((n_blocks_r, n_blocks_c))
        for i in range(n_blocks_r):
            for j in range(n_blocks_c):
                block = flip_mask[
                    i*block_size:(i+1)*block_size,
                    j*block_size:(j+1)*block_size
                ]
                block_density[i, j] = block.mean()
        
        # Autocorrelation: correlation of each block with its right neighbor
        if n_blocks_c > 1:
            auto_h = np.corrcoef(
                block_density[:, :-1].ravel(),
                block_density[:, 1:].ravel()
            )[0, 1]
        else:
            auto_h = 0.0
        if n_blocks_r > 1:
            auto_v = np.corrcoef(
                block_density[:-1, :].ravel(),
                block_density[1:, :].ravel()
            )[0, 1]
        else:
            auto_v = 0.0
        spatial = {
            "block_size": block_size,
            "auto_horizontal": float(auto_h) if not np.isnan(auto_h) else 0.0,
            "auto_vertical": float(auto_v) if not np.isnan(auto_v) else 0.0,
            "block_density_cv": float(block_density.std() / (block_density.mean() + 1e-10)),
        }
    else:
        spatial = {"block_size": 0, "auto_horizontal": 0.0, "auto_vertical": 0.0}
    
    # ── Row density distribution (histogram) ──
    hist_counts, hist_edges = np.histogram(row_density, bins=20)
    
    return {
        "name": name,
        "shape": [N, K],
        "total_flips": int(total_flips),
        "flip_frac": float(flip_frac),
        "row_stats": row_stats,
        "col_stats": col_stats,
        "spatial": spatial,
        "row_density": row_density,  # keep for crystal projection
        "col_density": col_density,
        "hist_counts": hist_counts.tolist(),
        "hist_edges": hist_edges.tolist(),
    }


def project_onto_crystal(row_density: np.ndarray, N: int, eigenvalues: np.ndarray,
                          eigenvectors: np.ndarray, name: str) -> dict:
    """Project row flip density onto crystal eigenbasis.
    
    The weight matrix is (N, K) where N = output features.
    In attention, output features map to d_model = 1280.
    The crystal is 16-dimensional (16 combinator types).
    
    We can't directly project 1280-dim rows onto 16-dim crystal.
    Instead, we analyze whether the row density DISTRIBUTION has
    structure that correlates with crystal eigenvalues.
    
    Approach: partition rows into groups based on their density,
    then check if the group structure matches crystal PC structure.
    """
    # Divide rows into 16 equal groups (matching combinator count)
    n_groups = min(16, N)
    group_size = N // n_groups
    
    group_means = []
    for g in range(n_groups):
        start = g * group_size
        end = start + group_size if g < n_groups - 1 else N
        group_means.append(float(row_density[start:end].mean()))
    group_means = np.array(group_means)
    
    # Normalize to zero-mean unit-variance
    gm_centered = group_means - group_means.mean()
    gm_norm = np.linalg.norm(gm_centered)
    if gm_norm < 1e-10:
        return {"name": name, "projections": [], "explained": []}
    gm_unit = gm_centered / gm_norm
    
    # Project onto crystal eigenvectors
    projections = []
    for pc_idx in range(min(8, eigenvectors.shape[1])):
        ev = eigenvectors[:n_groups, pc_idx]
        ev_centered = ev - ev.mean()
        ev_norm = np.linalg.norm(ev_centered)
        if ev_norm < 1e-10:
            projections.append(0.0)
            continue
        ev_unit = ev_centered / ev_norm
        proj = float(np.dot(gm_unit, ev_unit))
        projections.append(proj)
    
    # How much variance is explained by top crystal PCs
    total_var = float(np.var(group_means))
    explained = []
    for pc_idx in range(min(8, len(projections))):
        explained.append(projections[pc_idx] ** 2)
    
    return {
        "name": name,
        "group_means": group_means.tolist(),
        "projections": projections,  # correlation with each crystal PC
        "explained": explained,  # fraction of variance per PC
        "total_var": total_var,
    }


def analyze_head_structure(delta: np.ndarray, name: str, n_heads: int) -> dict:
    """Analyze flip density per attention head within a projection.
    
    For out_proj (1280, 1280): each head has d_head = 1280 // n_heads rows.
    For q_proj/k_proj in layers 4-9: (512, 1280) with n_kv or n_q heads.
    """
    N, K = delta.shape
    flip_mask = (delta == -1)
    
    if n_heads <= 0 or N % n_heads != 0:
        # Can't cleanly split — skip
        return {"name": name, "n_heads": n_heads, "per_head": []}
    
    d_head = N // n_heads
    per_head = []
    for h in range(n_heads):
        head_flips = flip_mask[h * d_head : (h + 1) * d_head, :]
        per_head.append({
            "head": h,
            "flip_frac": float(head_flips.mean()),
            "flip_count": int(head_flips.sum()),
        })
    
    # Sort by flip fraction
    per_head.sort(key=lambda x: x["flip_frac"], reverse=True)
    
    fracs = [h["flip_frac"] for h in per_head]
    return {
        "name": name,
        "n_heads": n_heads,
        "per_head": per_head,
        "head_flip_cv": float(np.std(fracs) / (np.mean(fracs) + 1e-10)),
        "head_flip_range": float(max(fracs) - min(fracs)),
    }


# ══════════════════════════════════════════════════════════════════════
# § 4  Main
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Probe TD flip topology")
    parser.add_argument("--checkpoint", type=str, required=True,
                        help="Path to checkpoint directory")
    parser.add_argument("--save", type=str, default=None,
                        help="Save results JSON to this path")
    args = parser.parse_args()
    
    ckpt_dir = Path(args.checkpoint)
    delta_path = ckpt_dir / "delta_plates.npz"
    
    if not delta_path.exists():
        print(f"ERROR: {delta_path} not found", file=sys.stderr)
        sys.exit(1)
    
    print(f"Loading delta plates from {delta_path}", file=sys.stderr)
    data = np.load(str(delta_path), allow_pickle=True)
    
    # Get crystal eigenbasis
    eigenvalues, eigenvectors = crystal_eigenbasis()
    print(f"\nCrystal eigenvalues (Zone B, top 8):", file=sys.stderr)
    for i, ev in enumerate(eigenvalues[:8]):
        print(f"  PC{i}: λ={ev:.4f}  ({COMBINATOR_NAMES[i] if i < 8 else '?'})",
              file=sys.stderr)
    print(f"  λ₀/λ₁ = {eigenvalues[0]/eigenvalues[1]:.4f}", file=sys.stderr)
    
    # ── Identify modules with flips ──
    packed_keys = sorted([k for k in data.keys() if k.endswith("_delta_packed")])
    stats_keys = sorted([k for k in data.keys() if k.endswith("_stats")])
    
    # ── Overview: which modules have flips? ──
    print("\n" + "=" * 75, file=sys.stderr)
    print("§1  MODULE-LEVEL FLIP DENSITY", file=sys.stderr)
    print("=" * 75, file=sys.stderr)
    
    flipped_modules = []
    for pk in packed_keys:
        module_name = pk.replace("_delta_packed", "")
        stats_key = module_name + "_stats"
        
        packed = data[pk]
        delta = unpack_ternary_np(packed)
        
        n_flip = int((delta == -1).sum())
        n_total = delta.size
        flip_pct = n_flip / n_total * 100
        
        if n_flip > 0:
            flipped_modules.append((module_name, delta, n_flip, flip_pct))
            marker = "█" * int(flip_pct) + "░" * (35 - int(flip_pct))
            print(f"  {module_name:50s}  {flip_pct:6.2f}%  {marker}  ({n_flip:>8,}/{n_total:>10,})",
                  file=sys.stderr)
    
    if not flipped_modules:
        print("\n  No flips found in any module!", file=sys.stderr)
        sys.exit(0)
    
    print(f"\n  Total flipped modules: {len(flipped_modules)}", file=sys.stderr)
    total_flips = sum(nf for _, _, nf, _ in flipped_modules)
    total_positions = sum(d.size for _, d, _, _ in flipped_modules)
    print(f"  Total flips: {total_flips:,} / {total_positions:,} "
          f"({total_flips/total_positions*100:.3f}%)", file=sys.stderr)
    
    # ── Detailed analysis for each flipped module ──
    print("\n" + "=" * 75, file=sys.stderr)
    print("§2  ROW/COLUMN DENSITY PROFILES", file=sys.stderr)
    print("=" * 75, file=sys.stderr)
    
    all_analyses = []
    for module_name, delta, n_flip, flip_pct in flipped_modules:
        analysis = analyze_flip_density(delta, module_name)
        all_analyses.append(analysis)
        
        rs = analysis["row_stats"]
        cs = analysis["col_stats"]
        sp = analysis["spatial"]
        
        print(f"\n  {module_name} ({delta.shape[0]}×{delta.shape[1]}, "
              f"{flip_pct:.2f}% flipped)", file=sys.stderr)
        print(f"    Row density:  mean={rs['mean']:.4f}  std={rs['std']:.4f}  "
              f"CV={rs['cv']:.3f}  range=[{rs['min']:.4f}, {rs['max']:.4f}]",
              file=sys.stderr)
        print(f"    Col density:  mean={cs['mean']:.4f}  std={cs['std']:.4f}  "
              f"CV={cs['cv']:.3f}", file=sys.stderr)
        print(f"    Spatial auto: horiz={sp['auto_horizontal']:.3f}  "
              f"vert={sp['auto_vertical']:.3f}  "
              f"block_CV={sp.get('block_density_cv', 0):.3f}", file=sys.stderr)
        
        # Show top and bottom rows
        print(f"    Top-5 rows:  {rs['top10_rows'][:5]}  "
              f"density={[f'{d:.4f}' for d in rs['top10_density'][:5]]}",
              file=sys.stderr)
        print(f"    Bot-5 rows:  {rs['bot10_rows'][:5]}  "
              f"density={[f'{d:.4f}' for d in rs['bot10_density'][:5]]}",
              file=sys.stderr)
        
        # Row density histogram (text sparkline)
        hc = analysis["hist_counts"]
        max_hc = max(hc) if hc else 1
        bars = "".join("▁▂▃▄▅▆▇█"[min(7, int(c / max_hc * 7.99))] if c > 0 else " "
                      for c in hc)
        print(f"    Row density distribution: [{bars}]", file=sys.stderr)
    
    # ── Head-level analysis for out_proj modules ──
    print("\n" + "=" * 75, file=sys.stderr)
    print("§3  PER-HEAD FLIP DENSITY (out_proj only)", file=sys.stderr)
    print("=" * 75, file=sys.stderr)
    
    # v14 model: d_model=1280, out_proj is (1280, 1280)
    # Layers 0-3: n_heads = 1280 // head_dim. Need to figure out head_dim.
    # For now assume 10 heads (d_head=128) which is common for d=1280
    # Actually let's infer from the shape
    head_analyses = []
    for module_name, delta, n_flip, flip_pct in flipped_modules:
        if "out_proj" not in module_name:
            continue
        
        N, K = delta.shape
        # out_proj: (d_model, d_model) = (1280, 1280)
        # Try common head dims
        for d_head in [128, 64, 160, 256]:
            if N % d_head == 0:
                n_heads = N // d_head
                break
        else:
            n_heads = 10  # fallback
        
        ha = analyze_head_structure(delta, module_name, n_heads)
        head_analyses.append(ha)
        
        print(f"\n  {module_name} ({n_heads} heads, d_head={N // n_heads})",
              file=sys.stderr)
        print(f"    Head flip CV: {ha['head_flip_cv']:.3f}  "
              f"range: {ha['head_flip_range']:.4f}", file=sys.stderr)
        
        # Show all heads sorted by flip fraction
        for h in ha["per_head"]:
            bar_len = int(h["flip_frac"] * 200)
            bar = "█" * bar_len
            print(f"      H{h['head']:2d}: {h['flip_frac']:.4f}  {bar}  "
                  f"({h['flip_count']:,})", file=sys.stderr)
    
    # ── Crystal projection ──
    print("\n" + "=" * 75, file=sys.stderr)
    print("§4  CRYSTAL EIGENBASIS PROJECTION", file=sys.stderr)
    print("=" * 75, file=sys.stderr)
    
    crystal_results = []
    for analysis in all_analyses:
        if analysis["total_flips"] == 0:
            continue
        
        rd = analysis["row_density"]
        N = analysis["shape"][0]
        
        cp = project_onto_crystal(rd, N, eigenvalues, eigenvectors, analysis["name"])
        crystal_results.append(cp)
        
        print(f"\n  {analysis['name']}:", file=sys.stderr)
        print(f"    Group means: {[f'{g:.4f}' for g in cp['group_means']]}", file=sys.stderr)
        print(f"    Crystal PC projections (correlation with eigenvector):", file=sys.stderr)
        for i, (proj, expl) in enumerate(zip(cp["projections"], cp["explained"])):
            bar = "+" * int(abs(proj) * 20) if proj >= 0 else "-" * int(abs(proj) * 20)
            print(f"      PC{i} ({COMBINATOR_NAMES[i]:4s}): {proj:+.4f}  "
                  f"R²={expl:.4f}  {bar}", file=sys.stderr)
    
    # ── Cross-layer patterns ──
    print("\n" + "=" * 75, file=sys.stderr)
    print("§5  CROSS-LAYER PATTERNS", file=sys.stderr)
    print("=" * 75, file=sys.stderr)
    
    # Compare row density profiles across layers
    out_proj_densities = {}
    for analysis in all_analyses:
        if "out_proj" in analysis["name"]:
            layer_num = None
            parts = analysis["name"].split("_")
            for i, p in enumerate(parts):
                if p == "layers" and i + 1 < len(parts):
                    try:
                        layer_num = int(parts[i + 1])
                    except ValueError:
                        pass
            if layer_num is not None:
                out_proj_densities[layer_num] = analysis["row_density"]
    
    if len(out_proj_densities) >= 2:
        layers = sorted(out_proj_densities.keys())
        print(f"\n  Cross-layer row density correlation (out_proj):", file=sys.stderr)
        for i, l1 in enumerate(layers):
            for l2 in layers[i+1:]:
                d1 = out_proj_densities[l1]
                d2 = out_proj_densities[l2]
                if len(d1) == len(d2):
                    corr = np.corrcoef(d1, d2)[0, 1]
                    print(f"    L{l1} ↔ L{l2}: r={corr:.4f}", file=sys.stderr)
    
    # ── Row density sorted profiles for visual inspection ──
    print("\n" + "=" * 75, file=sys.stderr)
    print("§6  SORTED ROW DENSITY PROFILES (are there plateaus/steps?)", file=sys.stderr)
    print("=" * 75, file=sys.stderr)
    
    for analysis in all_analyses:
        if "out_proj" not in analysis["name"]:
            continue
        rd = analysis["row_density"]
        sorted_rd = np.sort(rd)[::-1]  # descending
        
        # Show as percentile bins
        percentiles = [0, 5, 10, 25, 50, 75, 90, 95, 100]
        values = np.percentile(rd, percentiles)
        
        print(f"\n  {analysis['name']}:", file=sys.stderr)
        print(f"    Percentiles: ", end="", file=sys.stderr)
        for p, v in zip(percentiles, values):
            print(f"P{p}={v:.4f} ", end="", file=sys.stderr)
        print(file=sys.stderr)
        
        # Sparkline of sorted density (64 chars)
        n_bins = 64
        bin_size = max(1, len(sorted_rd) // n_bins)
        spark = []
        for b in range(n_bins):
            chunk = sorted_rd[b * bin_size : (b + 1) * bin_size]
            if len(chunk) > 0:
                v = chunk.mean()
                # Scale: 0 to max
                idx = min(7, int(v / (sorted_rd[0] + 1e-10) * 7.99))
                spark.append("▁▂▃▄▅▆▇█"[idx])
        print(f"    Sorted: [{''.join(spark)}]", file=sys.stderr)
        
        # Detect steps/plateaus: where does density drop sharply?
        diffs = np.diff(sorted_rd)
        big_drops = np.where(np.abs(diffs) > 2 * np.std(diffs))[0]
        if len(big_drops) > 0:
            print(f"    Sharp transitions at ranks: {big_drops[:10].tolist()} "
                  f"(of {len(sorted_rd)})", file=sys.stderr)
    
    # ── Summary ──
    print("\n" + "=" * 75, file=sys.stderr)
    print("§7  SUMMARY", file=sys.stderr)
    print("=" * 75, file=sys.stderr)
    
    print(f"\n  Flips are in: out_proj layers 4-9 (exclusively)", file=sys.stderr)
    
    # Check: is row density CV > column density CV? (rows more structured than cols?)
    for a in all_analyses:
        if "out_proj" in a["name"] and a["total_flips"] > 0:
            row_cv = a["row_stats"]["cv"]
            col_cv = a["col_stats"]["cv"]
            winner = "ROWS" if row_cv > col_cv else "COLS"
            print(f"  {a['name']:50s}  row_CV={row_cv:.3f}  col_CV={col_cv:.3f}  "
                  f"→ {winner} more structured", file=sys.stderr)
    
    # Crystal alignment summary
    if crystal_results:
        print(f"\n  Crystal alignment (max |projection| per module):", file=sys.stderr)
        for cr in crystal_results:
            if cr["projections"]:
                max_pc = np.argmax(np.abs(cr["projections"]))
                max_proj = cr["projections"][max_pc]
                print(f"  {cr['name']:50s}  max=PC{max_pc} "
                      f"({COMBINATOR_NAMES[max_pc]:4s}) "
                      f"r={max_proj:+.4f}", file=sys.stderr)
    
    # ── Save results ──
    if args.save:
        save_data = {
            "checkpoint": str(ckpt_dir),
            "crystal_eigenvalues": eigenvalues[:8].tolist(),
            "modules": [],
        }
        for a in all_analyses:
            module_data = {
                "name": a["name"],
                "shape": a["shape"],
                "total_flips": a["total_flips"],
                "flip_frac": a["flip_frac"],
                "row_stats": a["row_stats"],
                "col_stats": a["col_stats"],
                "spatial": a["spatial"],
            }
            save_data["modules"].append(module_data)
        save_data["crystal_projections"] = [
            {k: v for k, v in cr.items()}
            for cr in crystal_results
        ]
        save_data["head_analyses"] = [
            {k: v for k, v in ha.items()}
            for ha in head_analyses
        ]
        
        save_path = Path(args.save)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w") as f:
            json.dump(save_data, f, indent=2, default=str)
        print(f"\n  Results saved to {save_path}", file=sys.stderr)
    
    print("\n  Done.", file=sys.stderr)


if __name__ == "__main__":
    main()
