"""Crystal Self-Similarity Experiment — Is the lattice fractal?

Pure numpy analysis. No GPU needed. Can run alongside training.

Tests whether the crystal structure is self-similar across layers:
1. Project combinator embeddings through each layer's plates
2. Compute 8×8 lattice geometry at each layer
3. SVD to find intrinsic dimensionality at each depth
4. Check for power-law scaling (fractal signature)
5. Measure cross-layer geometric correlation

If self-similar:
  - Same 8×8 topology at every layer (same rank ordering of distances)
  - Singular value spectrum follows power law
  - Cross-layer scaling ratio is constant (= self-similarity ratio)
  - Deeper layers = higher resolution of the same pattern

License: MIT
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

import mlx.core as mx
import mlx.nn as nn

sys.path.insert(0, str(Path(__file__).parent))

from mini_holo_d_sweep_v2 import (
    VOCAB_SIZE, TOKENS, TOK2ID,
    HoloModel, TernaryCausalAttention,
)


# ── Combinator tokens ────────────────────────────────────────────

COMBINATORS = ["K", "I", "B", "C"]
# Extended set if the model has them
COMBINATORS_EXT = ["K", "I", "B", "C"]
for t in ["W", "Y", "D", "S"]:
    if t in TOK2ID:
        COMBINATORS_EXT.append(t)


def get_combinator_embeddings(model: HoloModel) -> np.ndarray:
    """Extract combinator embeddings from the model's embedding table.

    Returns (n_combinators, d_model) array.
    """
    embed_weight = np.array(model.embed.weight)  # (vocab, d_model)
    ids = [TOK2ID[c] for c in COMBINATORS_EXT]
    return embed_weight[ids]  # (n_comb, d_model)


# ── Plate extraction ─────────────────────────────────────────────

def get_layer_plates(model: HoloModel, layer_idx: int) -> dict[str, np.ndarray]:
    """Extract plate weight matrices (ternary signs) for a layer.

    Returns dict with keys: K, V, O, FFN, each (out, in) ternary array.
    """
    layer = model.layers[layer_idx]
    return {
        "K": np.sign(np.array(layer.attn.k_plate.weight)),
        "V": np.sign(np.array(layer.attn.v_plate.weight)),
        "O": np.sign(np.array(layer.attn.o_plate.weight)),
        "FFN": np.sign(np.array(layer.ffn_plate.weight)),
    }


def get_layer_scales(model: HoloModel, layer_idx: int) -> dict[str, np.ndarray]:
    """Extract beam scales for a layer."""
    layer = model.layers[layer_idx]
    return {
        "K": np.array(layer.attn.k_scale),
        "V": np.array(layer.attn.v_scale),
        "O": np.array(layer.attn.o_scale),
        "FFN": np.array(layer.ffn_scale),
    }


def get_layer_norms(model: HoloModel, layer_idx: int) -> dict:
    """Extract layer norm parameters."""
    layer = model.layers[layer_idx]
    return {
        "attn_weight": np.array(layer.attn_norm.weight),
        "attn_bias": np.array(layer.attn_norm.bias),
        "ffn_weight": np.array(layer.ffn_norm.weight),
        "ffn_bias": np.array(layer.ffn_norm.bias),
    }


# ── Cosine geometry ──────────────────────────────────────────────

def cosine_matrix(vecs: np.ndarray) -> np.ndarray:
    """Compute pairwise cosine similarity matrix.

    vecs: (n, d) array
    Returns: (n, n) cosine similarity matrix
    """
    norms = np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-10
    normed = vecs / norms
    return normed @ normed.T


def upper_triangle(matrix: np.ndarray) -> np.ndarray:
    """Extract upper triangle (above diagonal) as flat vector."""
    n = matrix.shape[0]
    idx = np.triu_indices(n, k=1)
    return matrix[idx]


# ── Layer-wise crystal geometry ──────────────────────────────────

def project_through_plate(embeddings: np.ndarray, plate: np.ndarray) -> np.ndarray:
    """Project embeddings through a ternary plate.

    embeddings: (n_comb, d_model)
    plate: (d_model, d_model) — ternary weight matrix
    Returns: (n_comb, d_model) — projected embeddings

    nn.Linear: output = x @ W.T, so we do embeddings @ plate.T
    """
    return embeddings @ plate.T


def compute_layer_geometry(
    embeddings: np.ndarray,
    plates: dict[str, np.ndarray],
    scales: dict[str, np.ndarray] | None = None,
) -> dict:
    """Compute combinator geometry after projecting through a layer's plates.

    For each plate type (V, O, FFN — skip K since it's 98.6% noise):
      1. Project combinator embeddings through the plate
      2. Optionally apply beam scales
      3. Compute pairwise cosine similarity matrix
      4. SVD of the projected embeddings

    Returns geometry analysis per plate type.
    """
    results = {}
    for ptype in ["V", "O", "FFN", "K"]:
        plate = plates[ptype]
        projected = project_through_plate(embeddings, plate)

        if scales is not None and ptype in scales:
            projected = projected * scales[ptype][None, :]

        cos_mat = cosine_matrix(projected)
        cos_upper = upper_triangle(cos_mat)

        # SVD of projected embeddings
        U, S, Vt = np.linalg.svd(projected, full_matrices=False)
        # Normalized singular values (sum to 1)
        S_norm = S / (S.sum() + 1e-10)
        # Effective rank (participation ratio)
        eff_rank = (S.sum() ** 2) / ((S ** 2).sum() + 1e-10)

        results[ptype] = {
            "cos_matrix": cos_mat,
            "cos_upper": cos_upper,
            "singular_values": S,
            "singular_values_norm": S_norm,
            "effective_rank": float(eff_rank),
            "projected": projected,
        }

    return results


# ── Self-similarity metrics ──────────────────────────────────────

def compare_geometries(geom_a: dict, geom_b: dict) -> dict:
    """Compare two layer geometries for self-similarity.

    Metrics:
      - Cosine correlation: Pearson r between upper triangle vectors
        (do they have the same rank ordering of combinator distances?)
      - Singular value ratio: ratio of corresponding singular values
        (is one layer a scaled version of the other?)
      - Subspace alignment: principal angles between SVD subspaces
        (do they span the same directions?)
    """
    results = {}
    for ptype in ["V", "O", "FFN", "K"]:
        if ptype not in geom_a or ptype not in geom_b:
            continue

        a = geom_a[ptype]
        b = geom_b[ptype]

        # 1. Cosine geometry correlation
        cos_a = a["cos_upper"]
        cos_b = b["cos_upper"]
        # Pearson correlation of pairwise cosines
        r = np.corrcoef(cos_a, cos_b)[0, 1]

        # 2. Singular value ratio
        s_a = a["singular_values"]
        s_b = b["singular_values"]
        n = min(len(s_a), len(s_b))
        # Ratio of corresponding singular values
        sv_ratios = s_b[:n] / (s_a[:n] + 1e-10)
        # If self-similar, ratios should be constant
        sv_ratio_mean = float(sv_ratios.mean())
        sv_ratio_std = float(sv_ratios.std())
        sv_ratio_cv = sv_ratio_std / (abs(sv_ratio_mean) + 1e-10)

        # 3. Subspace alignment (principal angles)
        # Use top-k singular vectors
        k = min(4, n)
        U_a = a["projected"]  # (n_comb, d)
        U_b = b["projected"]  # (n_comb, d)
        # SVD of the cross-correlation
        _, S_cross, _ = np.linalg.svd(
            (U_a / (np.linalg.norm(U_a, axis=0, keepdims=True) + 1e-10)).T @
            (U_b / (np.linalg.norm(U_b, axis=0, keepdims=True) + 1e-10))
        )
        # Principal angles = arccos(singular values of cross-corr)
        # High values = aligned subspaces
        alignment = float(S_cross[:k].mean())

        results[ptype] = {
            "cos_geometry_corr": float(r),
            "sv_ratio_mean": sv_ratio_mean,
            "sv_ratio_cv": sv_ratio_cv,  # 0 = perfectly self-similar
            "subspace_alignment": alignment,
        }

    return results


def check_power_law(singular_values: np.ndarray) -> dict:
    """Check if singular values follow a power law (self-similar signature).

    In log-log space, a power law appears as a straight line:
      log(S_k) = -α * log(k) + c

    Returns slope α and R² fit quality.
    """
    S = singular_values[singular_values > 1e-10]
    n = len(S)
    if n < 3:
        return {"alpha": 0.0, "r_squared": 0.0, "n_values": n}

    log_k = np.log(np.arange(1, n + 1))
    log_s = np.log(S)

    # Linear regression in log-log space
    A = np.vstack([log_k, np.ones(n)]).T
    result = np.linalg.lstsq(A, log_s, rcond=None)
    slope, intercept = result[0]

    # R² (goodness of fit)
    predicted = slope * log_k + intercept
    ss_res = ((log_s - predicted) ** 2).sum()
    ss_tot = ((log_s - log_s.mean()) ** 2).sum()
    r_squared = 1 - ss_res / (ss_tot + 1e-10)

    return {
        "alpha": float(-slope),  # positive = decaying power law
        "r_squared": float(r_squared),
        "n_values": n,
    }


# ── Cumulative projection (simulate ascending arm) ───────────────

def simulate_ascending_arm(
    model: HoloModel,
    embeddings: np.ndarray,
) -> list[dict]:
    """Simulate the ascending arm by progressively projecting through layers.

    Layer 0: embed → layernorm → V_plate → output
    Layer 1: (layer 0 output) → layernorm → V_plate → output
    etc.

    This traces how the crystal transforms combinator representations
    as they ascend through the model.
    """
    n_layers = len(model.layers)
    current = embeddings.copy()  # (n_comb, d_model)
    layer_states = []

    for i in range(n_layers):
        norms = get_layer_norms(model, i)
        plates = get_layer_plates(model, i)
        scales = get_layer_scales(model, i)

        # Apply layer norm (simplified: just scale and shift)
        # LayerNorm: (x - mean) / std * weight + bias
        mean = current.mean(axis=1, keepdims=True)
        std = current.std(axis=1, keepdims=True) + 1e-5
        normed = (current - mean) / std
        normed = normed * norms["attn_weight"][None, :] + norms["attn_bias"][None, :]

        # Project through V plate (the main crystal compute path)
        v_proj = project_through_plate(normed, plates["V"])
        if scales:
            v_proj = v_proj * scales["V"][None, :]

        # Also project through FFN
        ffn_normed = (current - mean) / std  # re-normalize for FFN path
        ffn_normed = ffn_normed * norms["ffn_weight"][None, :] + norms["ffn_bias"][None, :]
        ffn_proj = project_through_plate(ffn_normed, plates["FFN"])
        if scales:
            ffn_proj = ffn_proj * scales["FFN"][None, :]

        # Residual connection (simplified — just add V projection)
        residual = current + v_proj + ffn_proj

        # Geometry at this layer's output
        cos_mat = cosine_matrix(residual)
        cos_upper = upper_triangle(cos_mat)
        _, S, _ = np.linalg.svd(residual, full_matrices=False)

        layer_states.append({
            "layer": i,
            "residual": residual,
            "cos_matrix": cos_mat,
            "cos_upper": cos_upper,
            "singular_values": S,
            "effective_rank": float((S.sum() ** 2) / ((S ** 2).sum() + 1e-10)),
        })

        current = residual

    return layer_states


# ── Main ─────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("  CRYSTAL SELF-SIMILARITY EXPERIMENT")
    print("  Is the lattice fractal?")
    print("=" * 70)

    D_MODEL = 96
    N_LAYERS = 3

    model = HoloModel(d_model=D_MODEL, n_layers=N_LAYERS)
    mx.eval(model.parameters())

    print(f"\n  Model: d={D_MODEL}, layers={N_LAYERS}")
    print(f"  Combinators: {COMBINATORS_EXT}")
    print(f"  Combinator IDs: {[TOK2ID[c] for c in COMBINATORS_EXT]}")

    # ================================================================
    # 1. Raw embedding geometry (the seed)
    # ================================================================
    print(f"\n{'=' * 70}")
    print("  1. SEED — Raw Combinator Embedding Geometry")
    print(f"{'=' * 70}")

    embeds = get_combinator_embeddings(model)  # (n_comb, d_model)
    print(f"\n  Embedding shape: {embeds.shape}")

    seed_cos = cosine_matrix(embeds)
    n_comb = len(COMBINATORS_EXT)

    print(f"\n  8×8 Cosine Similarity (raw embeddings):")
    print(f"  {'':>6s}", end="")
    for c in COMBINATORS_EXT:
        print(f"  {c:>5s}", end="")
    print()
    for i, ci in enumerate(COMBINATORS_EXT):
        print(f"  {ci:>5s}", end="")
        for j in range(n_comb):
            v = seed_cos[i, j]
            print(f"  {v:>5.2f}", end="")
        print()

    # SVD of seed
    _, S_seed, _ = np.linalg.svd(embeds, full_matrices=False)
    print(f"\n  Seed singular values: {S_seed[:6].round(3)}")
    print(f"  Seed effective rank: {(S_seed.sum()**2) / ((S_seed**2).sum()):.2f}")
    pl = check_power_law(S_seed)
    print(f"  Power law: α={pl['alpha']:.3f}, R²={pl['r_squared']:.3f}")

    # ================================================================
    # 2. Per-layer plate geometry (crystal at each depth)
    # ================================================================
    print(f"\n{'=' * 70}")
    print("  2. CRYSTAL — Per-Layer Plate Geometry")
    print(f"{'=' * 70}")

    layer_geoms = []
    for i in range(N_LAYERS):
        plates = get_layer_plates(model, i)
        scales = get_layer_scales(model, i)
        geom = compute_layer_geometry(embeds, plates, scales)
        layer_geoms.append(geom)

        print(f"\n  --- Layer {i} ---")
        for ptype in ["V", "O", "FFN", "K"]:
            g = geom[ptype]
            pl = check_power_law(g["singular_values"])
            print(f"    {ptype:>3s}: eff_rank={g['effective_rank']:.2f}  "
                  f"SV=[{', '.join(f'{s:.3f}' for s in g['singular_values'][:5])}]  "
                  f"α={pl['alpha']:.2f} R²={pl['r_squared']:.2f}")

    # ================================================================
    # 3. Cross-layer comparison (self-similarity test)
    # ================================================================
    print(f"\n{'=' * 70}")
    print("  3. SELF-SIMILARITY — Cross-Layer Comparison")
    print(f"{'=' * 70}")

    for i in range(N_LAYERS):
        for j in range(i + 1, N_LAYERS):
            comp = compare_geometries(layer_geoms[i], layer_geoms[j])
            print(f"\n  Layer {i} → Layer {j}:")
            for ptype in ["V", "O", "FFN", "K"]:
                c = comp[ptype]
                print(f"    {ptype:>3s}: cos_corr={c['cos_geometry_corr']:+.3f}  "
                      f"sv_ratio={c['sv_ratio_mean']:.3f}±{c['sv_ratio_cv']:.3f}  "
                      f"align={c['subspace_alignment']:.3f}")

    # Print the actual cosine matrices for V plates to eyeball topology
    print(f"\n  --- V-plate cosine matrices (the crystal lattice at each depth) ---")
    for i in range(N_LAYERS):
        print(f"\n  Layer {i} V-plate lattice:")
        cos_mat = layer_geoms[i]["V"]["cos_matrix"]
        print(f"  {'':>6s}", end="")
        for c in COMBINATORS_EXT:
            print(f"  {c:>5s}", end="")
        print()
        for ci_idx, ci in enumerate(COMBINATORS_EXT):
            print(f"  {ci:>5s}", end="")
            for cj_idx in range(n_comb):
                v = cos_mat[ci_idx, cj_idx]
                print(f"  {v:>5.2f}", end="")
            print()

    # ================================================================
    # 4. Ascending arm simulation (cumulative crystal effect)
    # ================================================================
    print(f"\n{'=' * 70}")
    print("  4. ASCENDING ARM — Cumulative Crystal Projection")
    print(f"{'=' * 70}")

    arm_states = simulate_ascending_arm(model, embeds)

    print(f"\n  Residual stream geometry after each layer:")
    for state in arm_states:
        i = state["layer"]
        cos_upper = state["cos_upper"]
        seed_upper = upper_triangle(seed_cos)
        # Correlation with seed geometry
        r_seed = float(np.corrcoef(cos_upper, seed_upper)[0, 1])

        # Correlation with previous layer
        if i > 0:
            prev_upper = arm_states[i-1]["cos_upper"]
            r_prev = float(np.corrcoef(cos_upper, prev_upper)[0, 1])
        else:
            r_prev = 1.0

        pl = check_power_law(state["singular_values"])
        print(f"  Layer {i}: eff_rank={state['effective_rank']:.2f}  "
              f"seed_corr={r_seed:+.3f}  prev_corr={r_prev:+.3f}  "
              f"α={pl['alpha']:.2f} R²={pl['r_squared']:.2f}")

    # Print ascending arm cosine matrices
    print(f"\n  --- Ascending arm lattice (residual stream after each layer) ---")
    for state in arm_states:
        i = state["layer"]
        print(f"\n  After layer {i}:")
        cos_mat = state["cos_matrix"]
        print(f"  {'':>6s}", end="")
        for c in COMBINATORS_EXT:
            print(f"  {c:>5s}", end="")
        print()
        for ci_idx, ci in enumerate(COMBINATORS_EXT):
            print(f"  {ci:>5s}", end="")
            for cj_idx in range(n_comb):
                v = cos_mat[ci_idx, cj_idx]
                print(f"  {v:>5.2f}", end="")
            print()

    # ================================================================
    # 5. Cross-layer singular value scaling
    # ================================================================
    print(f"\n{'=' * 70}")
    print("  5. SCALING — Singular Value Ratios Across Layers")
    print(f"{'=' * 70}")

    print(f"\n  If self-similar, SV ratios between layers should be constant.")
    print(f"  A constant ratio = the self-similarity scaling factor.\n")

    for ptype in ["V", "O", "FFN"]:
        print(f"  {ptype} plate singular value ratios:")
        svs = [layer_geoms[i][ptype]["singular_values"] for i in range(N_LAYERS)]
        for i in range(N_LAYERS - 1):
            n = min(len(svs[i]), len(svs[i+1]))
            ratios = svs[i+1][:n] / (svs[i][:n] + 1e-10)
            print(f"    L{i}→L{i+1}: [{', '.join(f'{r:.3f}' for r in ratios[:6])}]  "
                  f"mean={ratios.mean():.3f} cv={ratios.std()/(abs(ratios.mean())+1e-10):.3f}")

    # Check if the ratio is close to φ
    phi = (1 + np.sqrt(5)) / 2  # 1.618...
    inv_phi = 1 / phi            # 0.618...
    print(f"\n  φ = {phi:.4f}, 1/φ = {inv_phi:.4f}")
    print(f"  If scaling ratio ≈ φ or 1/φ, the crystal's self-similarity")
    print(f"  is governed by the golden ratio (same attractor as stridestack).")

    # ================================================================
    # Save results
    # ================================================================
    out_path = Path("results/crystal-selfsim")
    out_path.mkdir(parents=True, exist_ok=True)

    # Serialize (strip numpy arrays for JSON)
    save_data = {
        "seed_cosine": seed_cos.tolist(),
        "seed_singular_values": S_seed.tolist(),
        "layer_geometries": [],
        "ascending_arm": [],
    }

    for i in range(N_LAYERS):
        layer_data = {}
        for ptype in ["V", "O", "FFN", "K"]:
            g = layer_geoms[i][ptype]
            layer_data[ptype] = {
                "cos_matrix": g["cos_matrix"].tolist(),
                "singular_values": g["singular_values"].tolist(),
                "effective_rank": g["effective_rank"],
                "power_law": check_power_law(g["singular_values"]),
            }
        save_data["layer_geometries"].append(layer_data)

    for state in arm_states:
        save_data["ascending_arm"].append({
            "layer": state["layer"],
            "cos_matrix": state["cos_matrix"].tolist(),
            "singular_values": state["singular_values"].tolist(),
            "effective_rank": state["effective_rank"],
        })

    # Cross-layer comparisons
    save_data["cross_layer"] = {}
    for i in range(N_LAYERS):
        for j in range(i + 1, N_LAYERS):
            comp = compare_geometries(layer_geoms[i], layer_geoms[j])
            save_data["cross_layer"][f"L{i}_L{j}"] = comp

    with open(out_path / "results.json", "w") as f:
        json.dump(save_data, f, indent=2)

    print(f"\n  Results saved to {out_path}/")
    print(f"\n{'=' * 70}")
    print("  DONE")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
