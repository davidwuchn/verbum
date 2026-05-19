"""Crystal Self-Similarity — V12 Trained Model (step 2000).

Traces the lattice geometry through the 9 stride stack layers
and the dispatch/integrate plates. Pure numpy — no GPU forward passes.

Tests:
1. Project 8 combinator embeddings through each stride layer's plates
2. Compute 8×8 cosine geometry at each stride depth
3. SVD for intrinsic dimensionality and power-law scaling
4. Cross-layer correlation (self-similarity test)
5. Cumulative projection through the stride stack (ascending arm)

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

from config import V12Config
from model import V12Model, create_model
from ternary import TernaryLinear, unpack_ternary_mlx
from kernel import COMBINATOR_NAMES, N_COMBINATORS


# ── Utilities ────────────────────────────────────────────────────

def cosine_matrix(vecs: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-10
    normed = vecs / norms
    return normed @ normed.T


def upper_triangle(matrix: np.ndarray) -> np.ndarray:
    n = matrix.shape[0]
    idx = np.triu_indices(n, k=1)
    return matrix[idx]


def check_power_law(sv: np.ndarray) -> dict:
    S = sv[sv > 1e-10]
    n = len(S)
    if n < 3:
        return {"alpha": 0.0, "r_squared": 0.0, "n_values": n}
    log_k = np.log(np.arange(1, n + 1))
    log_s = np.log(S)
    A = np.vstack([log_k, np.ones(n)]).T
    result = np.linalg.lstsq(A, log_s, rcond=None)
    slope, intercept = result[0]
    predicted = slope * log_k + intercept
    ss_res = ((log_s - predicted) ** 2).sum()
    ss_tot = ((log_s - log_s.mean()) ** 2).sum()
    r_squared = 1 - ss_res / (ss_tot + 1e-10)
    return {"alpha": float(-slope), "r_squared": float(r_squared), "n_values": n}


def extract_ternary_signs(mod: TernaryLinear) -> np.ndarray:
    """Extract the ternary weight matrix {-1, 0, +1} from bit-packed TernaryLinear."""
    # Weight is bit-packed uint32 (out, in//16). Unpack to int8 (out, in).
    unpacked = unpack_ternary_mlx(mod.weight)  # (out, in) int8
    return np.array(unpacked).astype(np.float32)


def extract_effective_weight(mod: TernaryLinear) -> np.ndarray:
    """Extract the full effective weight (signs × gamma)."""
    signs = extract_ternary_signs(mod)
    gamma = np.array(mod.gamma)  # (out,)
    return signs * gamma[:, None]


# ── Main ─────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("  CRYSTAL SELF-SIMILARITY — V12 TRAINED MODEL")
    print("=" * 70)

    cfg = V12Config()
    model = create_model(cfg)

    weights = mx.load("checkpoints/v12-distill-run2/step_002000/weights.npz")
    model.load_weights(list(weights.items()), strict=False)
    mx.eval(model.parameters())

    print(f"\n  Model: V12, d={cfg.d_model}, strides={len(cfg.strides)}")
    print(f"  Checkpoint: step 2000")
    print(f"  Combinators: {COMBINATOR_NAMES}")

    # ================================================================
    # 1. SEED — Trained Combinator Embedding Geometry
    # ================================================================
    print(f"\n{'=' * 70}")
    print("  1. SEED — Trained Combinator Embedding Geometry")
    print(f"{'=' * 70}")

    dispatch = model.combinator_dispatch
    emb = np.array(dispatch._normalize_embeddings())  # (8, 512)
    mx.clear_cache()

    seed_cos = cosine_matrix(emb)
    names = COMBINATOR_NAMES

    print(f"\n  8×8 Cosine Similarity (trained embeddings):")
    print(f"  {'':>6s}  " + "  ".join(f"{n:>5s}" for n in names))
    for i, ni in enumerate(names):
        row = "  ".join(f"{seed_cos[i,j]:>5.2f}" for j in range(N_COMBINATORS))
        print(f"  {ni:>5s}  {row}")

    _, S_seed, _ = np.linalg.svd(emb, full_matrices=False)
    pl = check_power_law(S_seed)
    print(f"\n  Seed SV: [{', '.join(f'{s:.3f}' for s in S_seed)}]")
    print(f"  Effective rank: {(S_seed.sum()**2) / ((S_seed**2).sum()):.2f}")
    print(f"  Power law: α={pl['alpha']:.3f}, R²={pl['r_squared']:.3f}")

    # ================================================================
    # 2. CRYSTAL — Per-Stride Plate Geometry
    # ================================================================
    print(f"\n{'=' * 70}")
    print("  2. CRYSTAL — Per-Stride Plate Geometry (V, O plates)")
    print(f"{'=' * 70}")

    n_strides = len(model.stride_stack.layers)
    stride_geoms = []

    for si in range(n_strides):
        layer = model.stride_stack.layers[si]
        plate_results = {}

        for ptype in ["v_proj", "out_proj", "k_proj"]:
            plate_mod = getattr(layer, ptype, None)
            if plate_mod is None or not isinstance(plate_mod, TernaryLinear):
                continue

            signs = extract_ternary_signs(plate_mod)  # (out, in)
            # Project combinator embeddings through the plate
            projected = emb @ signs.T  # (8, out)

            cos_mat = cosine_matrix(projected)
            cos_upper = upper_triangle(cos_mat)

            _, S, _ = np.linalg.svd(projected, full_matrices=False)
            eff_rank = float((S.sum() ** 2) / ((S ** 2).sum() + 1e-10))
            pl = check_power_law(S)

            plate_results[ptype] = {
                "cos_matrix": cos_mat,
                "cos_upper": cos_upper,
                "singular_values": S,
                "effective_rank": eff_rank,
                "power_law": pl,
                "projected": projected,
            }

        stride_geoms.append(plate_results)

        # Print summary for V plate
        if "v_proj" in plate_results:
            v = plate_results["v_proj"]
            print(f"  Stride {si} (s={cfg.strides[si]:>4d}): "
                  f"V eff_rank={v['effective_rank']:.2f}  "
                  f"SV=[{', '.join(f'{s:.2f}' for s in v['singular_values'][:5])}]  "
                  f"α={v['power_law']['alpha']:.2f} R²={v['power_law']['r_squared']:.2f}")

    # ================================================================
    # 3. SELF-SIMILARITY — Cross-Stride Comparison
    # ================================================================
    print(f"\n{'=' * 70}")
    print("  3. SELF-SIMILARITY — Cross-Stride V-plate Correlation")
    print(f"{'=' * 70}")

    # Correlation matrix between all strides (V plate geometry)
    n = n_strides
    corr_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if "v_proj" in stride_geoms[i] and "v_proj" in stride_geoms[j]:
                ci = stride_geoms[i]["v_proj"]["cos_upper"]
                cj = stride_geoms[j]["v_proj"]["cos_upper"]
                corr_matrix[i, j] = np.corrcoef(ci, cj)[0, 1]

    print(f"\n  V-plate geometry correlation across strides:")
    print(f"  {'':>3s}  " + "  ".join(f"S{i}" for i in range(n)))
    for i in range(n):
        row = "  ".join(f"{corr_matrix[i,j]:>4.2f}" for j in range(n))
        print(f"  S{i}  {row}")

    # Average correlation (off-diagonal) = overall self-similarity
    mask = ~np.eye(n, dtype=bool)
    avg_corr = corr_matrix[mask].mean()
    print(f"\n  Average off-diagonal correlation: {avg_corr:.3f}")
    print(f"  (1.0 = perfectly self-similar, 0.0 = no relationship)")

    # Same for O plate
    corr_matrix_o = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if "out_proj" in stride_geoms[i] and "out_proj" in stride_geoms[j]:
                ci = stride_geoms[i]["out_proj"]["cos_upper"]
                cj = stride_geoms[j]["out_proj"]["cos_upper"]
                corr_matrix_o[i, j] = np.corrcoef(ci, cj)[0, 1]

    print(f"\n  O-plate geometry correlation across strides:")
    print(f"  {'':>3s}  " + "  ".join(f"S{i}" for i in range(n)))
    for i in range(n):
        row = "  ".join(f"{corr_matrix_o[i,j]:>4.2f}" for j in range(n))
        print(f"  S{i}  {row}")
    avg_corr_o = corr_matrix_o[mask].mean()
    print(f"  Average off-diagonal: {avg_corr_o:.3f}")

    # ================================================================
    # 4. SCALING — Singular Value Ratios
    # ================================================================
    print(f"\n{'=' * 70}")
    print("  4. SCALING — V-plate Singular Value Ratios (adjacent strides)")
    print(f"{'=' * 70}")

    phi = (1 + np.sqrt(5)) / 2
    inv_phi = 1 / phi
    print(f"\n  φ = {phi:.4f}, 1/φ = {inv_phi:.4f}")

    for i in range(n_strides - 1):
        if "v_proj" in stride_geoms[i] and "v_proj" in stride_geoms[i+1]:
            sv_a = stride_geoms[i]["v_proj"]["singular_values"]
            sv_b = stride_geoms[i+1]["v_proj"]["singular_values"]
            k = min(len(sv_a), len(sv_b))
            ratios = sv_b[:k] / (sv_a[:k] + 1e-10)
            print(f"  S{i}→S{i+1}: ratio=[{', '.join(f'{r:.3f}' for r in ratios[:6])}]  "
                  f"mean={ratios.mean():.3f}  cv={ratios.std()/(abs(ratios.mean())+1e-10):.3f}")

    # ================================================================
    # 5. LATTICE AT EACH STRIDE (the crystal map)
    # ================================================================
    print(f"\n{'=' * 70}")
    print("  5. LATTICE — V-plate cosine matrices at select strides")
    print(f"{'=' * 70}")

    # Show stride 0 (finest), stride 4 (mid), stride 8 (coarsest)
    for si in [0, 4, 8]:
        if si < n_strides and "v_proj" in stride_geoms[si]:
            cos_mat = stride_geoms[si]["v_proj"]["cos_matrix"]
            print(f"\n  Stride {si} (s={cfg.strides[si]}) V-plate lattice:")
            print(f"  {'':>6s}  " + "  ".join(f"{n:>5s}" for n in names))
            for i, ni in enumerate(names):
                row = "  ".join(f"{cos_mat[i,j]:>5.2f}" for j in range(N_COMBINATORS))
                print(f"  {ni:>5s}  {row}")

    # Correlation of each stride's lattice with the seed
    print(f"\n  Stride lattice correlation with seed (embedding geometry):")
    for si in range(n_strides):
        if "v_proj" in stride_geoms[si]:
            cos_upper = stride_geoms[si]["v_proj"]["cos_upper"]
            seed_upper = upper_triangle(seed_cos)
            r = np.corrcoef(cos_upper, seed_upper)[0, 1]
            print(f"    S{si} (s={cfg.strides[si]:>4d}): seed_corr = {r:+.3f}")

    # ================================================================
    # 6. DISPATCH + INTEGRATE plates (the beam optics)
    # ================================================================
    print(f"\n{'=' * 70}")
    print("  6. DISPATCH/INTEGRATE — FFN plate geometry")
    print(f"{'=' * 70}")

    for comp_name, comp in [("dispatch", model.combinator_dispatch),
                             ("integrate", model.combinator_integrate)]:
        for proj_name in ["up", "down"]:
            proj = getattr(comp, proj_name, None)
            if proj is None or not isinstance(proj, TernaryLinear):
                continue
            signs = extract_ternary_signs(proj)
            # Only project if input dim matches embedding dim
            if signs.shape[1] != emb.shape[1]:
                print(f"  {comp_name}.{proj_name}: shape ({signs.shape[0]}, {signs.shape[1]}) — "
                      f"skipped (dim mismatch)")
                continue
            projected = emb @ signs.T
            cos_mat = cosine_matrix(projected)
            cos_upper = upper_triangle(cos_mat)
            seed_upper = upper_triangle(seed_cos)
            r = np.corrcoef(cos_upper, seed_upper)[0, 1]
            _, S, _ = np.linalg.svd(projected, full_matrices=False)
            eff_rank = (S.sum()**2) / ((S**2).sum() + 1e-10)
            print(f"  {comp_name}.{proj_name}: seed_corr={r:+.3f}  "
                  f"eff_rank={eff_rank:.2f}  "
                  f"SV=[{', '.join(f'{s:.1f}' for s in S[:5])}]")

    # ================================================================
    # Save
    # ================================================================
    out_path = Path("results/crystal-selfsim-v12")
    out_path.mkdir(parents=True, exist_ok=True)

    save_data = {
        "seed_cosine": seed_cos.tolist(),
        "seed_singular_values": S_seed.tolist(),
        "stride_v_corr_matrix": corr_matrix.tolist(),
        "stride_o_corr_matrix": corr_matrix_o.tolist(),
        "stride_geometries": [],
    }
    for si in range(n_strides):
        entry = {"stride": si, "stride_value": int(cfg.strides[si])}
        for ptype in ["v_proj", "out_proj", "k_proj"]:
            if ptype in stride_geoms[si]:
                g = stride_geoms[si][ptype]
                entry[ptype] = {
                    "cos_matrix": g["cos_matrix"].tolist(),
                    "singular_values": g["singular_values"].tolist(),
                    "effective_rank": g["effective_rank"],
                    "power_law": g["power_law"],
                }
        save_data["stride_geometries"].append(entry)

    with open(out_path / "results.json", "w") as f:
        json.dump(save_data, f, indent=2)

    print(f"\n  Results saved to {out_path}/")
    print(f"\n{'=' * 70}")
    print("  DONE")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
