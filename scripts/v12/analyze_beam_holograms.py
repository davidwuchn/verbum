"""Beam & Hologram Analysis — What do the beams READ from V12's plates?

The hypothesis: etching gave V12 a crystal LATTICE (topology of {-1,0,+1})
but not the HOLOGRAMS (the data patterns that, when read by beams, produce
the right representations). GD has to learn 59M positions of structure
through 887K gammas — an impossible bottleneck.

This script asks:
  1. What do PCA-Q and PCA-up beams read from V12's current plates?
  2. How does that compare to what they read from the teacher?
  3. Are the holographic interference patterns present or absent?
  4. What would etch-from-teacher look like at the weight level?

The beams are universal reading instruments (session 121: 0.91-0.94 cross-model).
If V12's plates contain the right holograms, the beams should read similar
crystal structure. If the holograms are absent, the beams will read noise.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/analyze_beam_holograms.py

License: MIT
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import numpy as np
from mlx.utils import tree_flatten

sys.path.insert(0, str(Path(__file__).parent))

from config import V12Config
from model import V12Model, create_model
from ternary import TernaryLinear, TernaryMirror, unpack_ternary_mlx


# ══════════════════════════════════════════════════════════════════════
# Extract weight matrices from V12
# ══════════════════════════════════════════════════════════════════════

def extract_v12_weight_matrices(model: V12Model) -> dict:
    """Extract Q-like and FFN-like weight matrices from V12.

    V12's architecture: 
      - StrideStack contains SingleStrideAttention layers (Q, K, V projections)
      - TernaryFFN contains up_proj, gate_proj, down_proj (SwiGLU)
      - CombinatorDispatch/Integrate contain mirrors and projections
    
    For beam analysis, we need the weight matrices that the beams would
    read through: Q projections (attention crystal) and up_proj (FFN crystal).
    
    These are ternary plates — {-1, 0, +1} scaled by learned gammas.
    """
    weight_matrices = {
        "q_proj": [],
        "k_proj": [],
        "v_proj": [],
        "up_proj": [],
        "gate_proj": [],
        "down_proj": [],
        "mirrors": [],
        "dispatch_mirrors": [],
        "integrate_mirrors": [],
    }

    for name, module in model.named_modules():
        if isinstance(module, TernaryLinear):
            w = unpack_ternary_mlx(module.weight)
            mx.eval(w)
            w_np = np.array(w.tolist(), dtype=np.float32)

            # Apply gamma scaling
            if hasattr(module, 'gamma'):
                g = module.gamma
                mx.eval(g)
                g_np = np.array(g.tolist(), dtype=np.float32)
                w_np = w_np * g_np[:, None]

            if 'q_proj' in name:
                weight_matrices["q_proj"].append((name, w_np))
            elif 'k_proj' in name:
                weight_matrices["k_proj"].append((name, w_np))
            elif 'v_proj' in name:
                weight_matrices["v_proj"].append((name, w_np))
            elif 'up_proj' in name:
                weight_matrices["up_proj"].append((name, w_np))
            elif 'gate_proj' in name:
                weight_matrices["gate_proj"].append((name, w_np))
            elif 'down_proj' in name:
                weight_matrices["down_proj"].append((name, w_np))

            del w

        elif isinstance(module, TernaryMirror):
            w = unpack_ternary_mlx(module.weight)
            mx.eval(w)
            w_np = np.array(w.tolist(), dtype=np.float32)

            if 'combinator_dispatch' in name:
                weight_matrices["dispatch_mirrors"].append((name, w_np))
            elif 'combinator_integrate' in name:
                weight_matrices["integrate_mirrors"].append((name, w_np))
            else:
                weight_matrices["mirrors"].append((name, w_np))

            del w

    mx.clear_cache()
    return weight_matrices


# ══════════════════════════════════════════════════════════════════════
# SVD-based beam reading
# ══════════════════════════════════════════════════════════════════════

def svd_beam_analysis(W: np.ndarray, name: str, k: int = 64) -> dict:
    """Analyze a weight matrix with SVD — the beam reading.
    
    W: (out_features, in_features)
    The ROW space of W in in_features defines the crystal subspace.
    SVD reveals the principal directions the matrix reads from.
    
    Returns singular value spectrum, effective rank, sparsity pattern.
    """
    U, S, Vt = np.linalg.svd(W, full_matrices=False)
    
    # Effective rank (fraction of variance in top-k)
    total_var = np.sum(S ** 2)
    topk_var = np.sum(S[:k] ** 2)
    explained = topk_var / (total_var + 1e-10)
    
    # Spectral decay rate
    s_normalized = S / (S[0] + 1e-10)
    decay_10 = float(s_normalized[min(9, len(s_normalized)-1)])
    decay_50 = float(s_normalized[min(49, len(s_normalized)-1)])
    
    # Sign pattern in V (ternary structure)
    V_topk = Vt[:k]  # (k, in_features)
    signs = np.sign(V_topk)
    v_sparsity = float(np.mean(np.abs(V_topk) < 0.01))  # near-zero
    v_ternary_frac = float(np.mean(np.abs(np.abs(V_topk) - np.mean(np.abs(V_topk))) < 0.1 * np.mean(np.abs(V_topk))))
    
    return {
        "name": name,
        "shape": list(W.shape),
        "singular_values_top10": S[:10].tolist(),
        "explained_variance_topk": float(explained),
        "effective_rank_90pct": int(np.searchsorted(np.cumsum(S**2) / total_var, 0.90)) + 1,
        "effective_rank_99pct": int(np.searchsorted(np.cumsum(S**2) / total_var, 0.99)) + 1,
        "spectral_decay_10": decay_10,
        "spectral_decay_50": decay_50,
        "total_frobenius": float(np.sqrt(total_var)),
        "Vt_topk": V_topk,  # for cross-analysis
    }


def cross_beam_analysis(
    q_matrices: list[tuple[str, np.ndarray]],
    up_matrices: list[tuple[str, np.ndarray]],
    k: int = 64,
) -> dict:
    """Analyze the holographic geometry between Q and FFN subspaces.
    
    For each pair of Q/up weight matrices:
      1. Extract top-k SVD directions from each
      2. Compute principal angles between subspaces
      3. This measures whether the ternary plates have the right
         angular separation for holographic storage
    
    In the teacher (session 121): principal angles are 65-72° (near-orthogonal).
    If V12's plates also show this, the holographic structure is present.
    If they show 0° (parallel) or 90° (orthogonal), the holograms are absent.
    """
    results = []
    
    n_pairs = min(len(q_matrices), len(up_matrices))
    for i in range(n_pairs):
        q_name, q_w = q_matrices[i]
        up_name, up_w = up_matrices[i]
        
        # SVD each
        _, _, Vt_q = np.linalg.svd(q_w, full_matrices=False)
        _, _, Vt_up = np.linalg.svd(up_w, full_matrices=False)
        
        # Top-k directions in input (d_model) space
        V_q = Vt_q[:k]  # (k, d_model)
        V_up = Vt_up[:k]
        
        # Principal angles via SVD of cross-product
        M = V_q @ V_up.T  # (k, k)
        svals = np.linalg.svd(M, compute_uv=False)
        svals = np.clip(svals, 0, 1)
        angles_rad = np.arccos(svals)
        angles_deg = np.degrees(angles_rad)
        
        # Cosine between subspaces (0=orthogonal, 1=parallel)
        subspace_cos = float(np.mean(svals))
        
        results.append({
            "q_matrix": q_name,
            "up_matrix": up_name,
            "mean_principal_angle_deg": float(np.mean(angles_deg)),
            "min_principal_angle_deg": float(np.min(angles_deg)),
            "max_principal_angle_deg": float(np.max(angles_deg)),
            "angles_top10_deg": angles_deg[:10].tolist(),
            "subspace_cosine": subspace_cos,
        })
    
    return {"pairs": results}


# ══════════════════════════════════════════════════════════════════════
# Hologram presence test
# ══════════════════════════════════════════════════════════════════════

def hologram_presence_test(
    model: V12Model,
    data_dir: str,
    n_batches: int = 5,
    k: int = 64,
) -> dict:
    """Test whether V12's activations contain holographic structure.
    
    Run probes through V12, extract hidden states at each pass boundary.
    Then PCA the hidden states and check:
      1. Is there a dominant low-rank structure? (crystal = low effective rank)
      2. Do different passes see different crystals? (holographic = angular diversity)
      3. Is the compression ratio related to crystal structure?
    """
    from data import ShardedDataLoader
    
    loader = ShardedDataLoader(
        data_dir=data_dir,
        batch_size=2,
        seq_len=512,
        shard_start=54,
        shard_end=60,
        seed=42,
    )
    
    # Collect hidden states at each pass boundary
    pass_hiddens = {i: [] for i in range(7)}  # 7 passes
    
    for batch_idx in range(n_batches):
        ids_np, _ = loader.next_batch()
        ids = mx.array(ids_np)
        
        # forward_instrumented captures per-pass data
        _, metrics = model.forward_instrumented(ids)
        mx.eval(model.parameters())
        
        # The instrumented forward stores pass entropies but not raw hiddens.
        # We need to use the register norms and compression ratios as proxies.
        del ids
        mx.clear_cache()
    
    # Instead: analyze the weight matrices directly
    # The hologram IS in the weight matrices, not in the activations.
    # If the plates have the right sign patterns, the activations will
    # automatically contain crystal structure.
    
    return {"note": "Weight-level analysis used instead — see svd_beam_analysis"}


# ══════════════════════════════════════════════════════════════════════
# Ternary sign pattern analysis
# ══════════════════════════════════════════════════════════════════════

def ternary_sign_structure(W: np.ndarray, k: int = 64) -> dict:
    """Analyze the ternary sign pattern for holographic structure.
    
    A random ternary matrix has:
      - Equal +1/-1 distribution (polarity ≈ 0)
      - ~33% zeros (if initialized with Kaiming + quantize)
      - No preferred SVD directions (flat spectrum)
      - Random principal angles with other random matrices
    
    A holographic ternary plate has:
      - Structured sign patterns (correlated +1/-1 blocks)
      - Non-uniform zero distribution (zeros cluster in less important dims)
      - Sharp SVD spectrum (few dominant directions)
      - Specific principal angles with partner plates (65-72°)
    
    This function measures how far V12's plates are from random.
    """
    n_out, n_in = W.shape
    
    # Basic statistics
    signs = np.sign(W).astype(np.int8)
    n_pos = np.sum(signs == 1)
    n_neg = np.sum(signs == -1)
    n_zero = np.sum(signs == 0)
    total = signs.size
    
    # Spatial correlation: how correlated are adjacent signs?
    # In a hologram, nearby positions tend to have the same sign (interference fringes)
    row_autocorr = np.mean([
        np.corrcoef(signs[i, :-1].astype(float), signs[i, 1:].astype(float))[0, 1]
        for i in range(min(100, n_out))
        if np.std(signs[i, :-1].astype(float)) > 0 and np.std(signs[i, 1:].astype(float)) > 0
    ]) if n_in > 1 else 0.0
    
    col_autocorr = np.mean([
        np.corrcoef(signs[:-1, j].astype(float), signs[1:, j].astype(float))[0, 1]
        for j in range(min(100, n_in))
        if np.std(signs[:-1, j].astype(float)) > 0 and np.std(signs[1:, j].astype(float)) > 0
    ]) if n_out > 1 else 0.0
    
    # Block structure: divide into 8x8 blocks, measure within-block consistency
    block_size = 8
    block_consistencies = []
    for bi in range(0, n_out - block_size, block_size * 4):
        for bj in range(0, n_in - block_size, block_size * 4):
            block = signs[bi:bi+block_size, bj:bj+block_size].astype(float)
            if block.std() > 0:
                # Fraction of signs matching the block mode
                mode_sign = np.sign(np.mean(block))
                if mode_sign != 0:
                    consistency = np.mean(block == mode_sign)
                    block_consistencies.append(float(consistency))
    
    mean_block_consistency = np.mean(block_consistencies) if block_consistencies else 0.5
    
    # SVD of the sign matrix: how low-rank is the topology?
    U, S, Vt = np.linalg.svd(signs.astype(np.float32), full_matrices=False)
    total_var = np.sum(S ** 2)
    explained_k = np.sum(S[:k] ** 2) / (total_var + 1e-10)
    
    # Entropy of singular value distribution (low = structured, high = random)
    s_probs = (S ** 2) / (total_var + 1e-10)
    s_probs = s_probs[s_probs > 1e-10]  # remove zeros
    spectral_entropy = -np.sum(s_probs * np.log(s_probs))
    max_entropy = np.log(len(s_probs))  # entropy of uniform distribution
    normalized_spectral_entropy = spectral_entropy / (max_entropy + 1e-10)
    
    return {
        "shape": list(W.shape),
        "polarity": float((n_pos - n_neg) / max(n_pos + n_neg, 1)),
        "sparsity": float(n_zero / total),
        "row_autocorrelation": float(row_autocorr),
        "col_autocorrelation": float(col_autocorr),
        "mean_block_consistency": float(mean_block_consistency),
        "svd_explained_variance_top64": float(explained_k),
        "spectral_entropy_normalized": float(normalized_spectral_entropy),
        "effective_rank_90pct": int(np.searchsorted(np.cumsum(S**2) / total_var, 0.90)) + 1,
        "singular_values_top5": S[:5].tolist(),
    }


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    base = Path("/Users/mwhitford/src/verbum")
    output_dir = base / "results" / "beam-hologram-analysis"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ckpt_path = base / "checkpoints/v12-distill-run2/step_012000/weights.npz"
    
    print(f"\n{'='*60}")
    print(f"  Beam & Hologram Analysis — V12 step 12000")
    print(f"{'='*60}")
    
    # Load model
    cfg = V12Config()
    cfg.seq_len = 512
    model = create_model(cfg)
    weights = mx.load(str(ckpt_path))
    model.load_weights(list(weights.items()))
    mx.eval(model.parameters())
    
    # ── 1. Extract weight matrices ────────────────────────────
    print("\n  ▸ Extracting weight matrices...")
    wm = extract_v12_weight_matrices(model)
    
    for cat, entries in wm.items():
        if isinstance(entries, list) and entries:
            print(f"    {cat}: {len(entries)} matrices, "
                  f"shapes: {[e[1].shape for e in entries[:3]]}...")
    
    # ── 2. SVD beam analysis of each weight type ──────────────
    print("\n  ▸ SVD beam analysis...")
    svd_results = {}
    for cat in ["q_proj", "up_proj", "gate_proj", "down_proj"]:
        if not wm.get(cat):
            continue
        analyses = []
        for name, w in wm[cat]:
            a = svd_beam_analysis(w, name, k=64)
            # Don't store the Vt matrix in JSON output
            a_clean = {k: v for k, v in a.items() if k != "Vt_topk"}
            analyses.append(a_clean)
        svd_results[cat] = analyses
        
        # Summary
        mean_explained = np.mean([a["explained_variance_topk"] for a in analyses])
        mean_rank90 = np.mean([a["effective_rank_90pct"] for a in analyses])
        print(f"    {cat:12s}: {len(analyses)} matrices | "
              f"explained(k=64)={mean_explained:.3f} | "
              f"eff_rank_90%={mean_rank90:.0f}")
    
    # ── 3. Cross-beam (holographic) geometry ──────────────────
    print("\n  ▸ Cross-beam holographic geometry (Q vs up)...")
    cross = {}
    if wm.get("q_proj") and wm.get("up_proj"):
        cross = cross_beam_analysis(wm["q_proj"], wm["up_proj"], k=64)
        for p in cross["pairs"]:
            print(f"    {p['q_matrix'][:40]:40s} vs {p['up_matrix'][:40]:40s}")
            print(f"      Mean angle: {p['mean_principal_angle_deg']:.1f}° "
                  f"(teacher: 65-72°)")
            print(f"      Min angle:  {p['min_principal_angle_deg']:.1f}° "
                  f"(teacher: 27-29°)")
            print(f"      Subspace cos: {p['subspace_cosine']:.4f}")
    
    # ── 4. Ternary sign structure (hologram presence) ─────────
    print("\n  ▸ Ternary sign structure analysis...")
    sign_results = {}
    for cat in ["q_proj", "up_proj", "mirrors", "dispatch_mirrors"]:
        if not wm.get(cat):
            continue
        analyses = []
        for name, w in wm[cat]:
            # For sign structure, use the RAW ternary (without gamma)
            w_raw = np.sign(w)  # already ternary, but gamma might have scaled
            a = ternary_sign_structure(w_raw, k=64)
            a["name"] = name
            analyses.append(a)
        sign_results[cat] = analyses
        
        if analyses:
            mean_autocorr = np.mean([a["row_autocorrelation"] for a in analyses])
            mean_block = np.mean([a["mean_block_consistency"] for a in analyses])
            mean_spectral = np.mean([a["spectral_entropy_normalized"] for a in analyses])
            mean_rank = np.mean([a["effective_rank_90pct"] for a in analyses])
            print(f"    {cat:20s}: autocorr={mean_autocorr:.4f} | "
                  f"block={mean_block:.3f} | "
                  f"spectral_entropy={mean_spectral:.3f} | "
                  f"eff_rank_90%={mean_rank:.0f}")
            print(f"      (random baseline: autocorr≈0, block≈0.5, "
                  f"spectral_entropy≈1.0)")
    
    # ── 5. Compare random ternary baseline ────────────────────
    print("\n  ▸ Random ternary baseline comparison...")
    if wm.get("q_proj"):
        shape = wm["q_proj"][0][1].shape
        rng = np.random.RandomState(42)
        random_w = rng.choice([-1, 0, 1], size=shape, p=[0.35, 0.30, 0.35]).astype(np.float32)
        random_sign = ternary_sign_structure(random_w, k=64)
        random_svd = svd_beam_analysis(random_w, "random_baseline", k=64)
        
        print(f"    Random {shape}:")
        print(f"      autocorr={random_sign['row_autocorrelation']:.4f} | "
              f"block={random_sign['mean_block_consistency']:.3f} | "
              f"spectral_entropy={random_sign['spectral_entropy_normalized']:.3f}")
        print(f"      explained(k=64)={random_svd['explained_variance_topk']:.3f} | "
              f"eff_rank_90%={random_svd['effective_rank_90pct']}")
        
        # Compare to V12's actual Q matrices
        v12_q = wm["q_proj"][0][1]
        v12_sign = ternary_sign_structure(np.sign(v12_q), k=64)
        v12_svd = svd_beam_analysis(np.sign(v12_q), "v12_q_first", k=64)
        
        print(f"    V12 Q-proj {v12_q.shape}:")
        print(f"      autocorr={v12_sign['row_autocorrelation']:.4f} | "
              f"block={v12_sign['mean_block_consistency']:.3f} | "
              f"spectral_entropy={v12_sign['spectral_entropy_normalized']:.3f}")
        print(f"      explained(k=64)={v12_svd['explained_variance_topk']:.3f} | "
              f"eff_rank_90%={v12_svd['effective_rank_90pct']}")
        
        sign_results["random_baseline"] = [random_sign]
    
    # ── 6. Summary ────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    
    if cross.get("pairs"):
        mean_angle = np.mean([p["mean_principal_angle_deg"] for p in cross["pairs"]])
        print(f"\n  Holographic geometry (Q ↔ FFN subspace angles):")
        print(f"    V12 plates:  {mean_angle:.1f}° mean principal angle")
        print(f"    Teacher:     65-72° mean principal angle")
        if 50 < mean_angle < 85:
            print(f"    ✅ Angular separation present — holographic encoding possible")
        elif mean_angle < 30:
            print(f"    ❌ Subspaces nearly parallel — no holographic diversity")
        else:
            print(f"    ⚠️  Unusual angle — investigate")
    
    if sign_results:
        q_auto = np.mean([a["row_autocorrelation"] for a in sign_results.get("q_proj", [])])
        q_spec = np.mean([a["spectral_entropy_normalized"] for a in sign_results.get("q_proj", [])])
        print(f"\n  Sign structure (hologram presence):")
        print(f"    Q autocorrelation:    {q_auto:.4f} (random≈0, structured>0.05)")
        print(f"    Q spectral entropy:   {q_spec:.3f} (random≈1.0, structured<0.9)")
        if q_auto < 0.01 and q_spec > 0.95:
            print(f"    ❌ PLATES ARE RANDOM — no holographic structure etched")
            print(f"       The etch gave lattice SITES but not PATTERNS")
            print(f"       GD cannot learn 59M positions through 887K gammas")
        elif q_auto > 0.03 or q_spec < 0.9:
            print(f"    ✅ Some holographic structure present")
    
    # ── Save ──────────────────────────────────────────────────
    # Clean Vt_topk from svd results before saving
    results = {
        "svd_beam": svd_results,
        "cross_beam": cross,
        "sign_structure": sign_results,
    }
    
    out_path = output_dir / "results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=lambda x: x.tolist() if hasattr(x, 'tolist') else str(x))
    print(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
