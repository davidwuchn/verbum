#!/usr/bin/env python3
"""
Probe: How does extraction quality scale with student dimension?

We know:
  - Full model composed transform is rank90=27 in teacher space (5120D)
  - At d_student=1280: per-dim correlation ≈ 0.76
  - At d_student=5120 (teacher): per-dim correlation ≈ 0.97

This probe sweeps d_student and measures ternary extraction quality.

Two-phase approach:
  Phase 1: Compose the full-model transform from weights, save it.
  Phase 2: Load the saved transform, sweep d_student values.

Usage:
    # Phase 1 (slow — ~15 min):
    uv run python scripts/explore/probe_extraction_dimension.py --compose

    # Phase 2 (fast — ~2 min):
    uv run python scripts/explore/probe_extraction_dimension.py --sweep

    # Both:
    uv run python scripts/explore/probe_extraction_dimension.py

License: MIT
"""

from __future__ import annotations

import sys
import time
import json
import argparse
from pathlib import Path

import numpy as np
from safetensors import safe_open

TEACHER_PATH = Path.home() / ".cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
N_LAYERS = 64
D_MODEL = 5120

LAYER_TYPES = (['linear_attention'] * 3 + ['full_attention']) * 16

CACHE_PATH = Path("results/extraction-dimension-sweep/T_full.npy")

_SHARD_INDEX = None

def get_index():
    global _SHARD_INDEX
    if _SHARD_INDEX is None:
        _SHARD_INDEX = json.load(open(TEACHER_PATH / "model.safetensors.index.json"))
    return _SHARD_INDEX


def load_tensor(name):
    idx = get_index()
    fname = idx["weight_map"].get(name)
    if fname is None:
        return None
    with safe_open(str(TEACHER_PATH / fname), framework="pt") as sf:
        return sf.get_tensor(name).float().numpy()


def compute_layer_matrix(layer_idx):
    """Compute linearized layer: A_i = I + OV_i + FFN_i."""
    base = f"model.language_model.layers.{layer_idx}"
    lt = LAYER_TYPES[layer_idx]
    
    A = np.eye(D_MODEL, dtype=np.float32)
    
    if lt == 'full_attention':
        v_proj = load_tensor(f"{base}.self_attn.v_proj.weight")
        o_proj = load_tensor(f"{base}.self_attn.o_proj.weight")
        if v_proj is not None and o_proj is not None:
            d_v = v_proj.shape[0]
            d_o = o_proj.shape[1]
            if d_v == d_o:
                OV = o_proj @ v_proj
                A += OV / N_LAYERS
            else:
                n_kv_heads = d_v // 256
                n_q_heads = d_o // 256
                repeat = n_q_heads // n_kv_heads
                v_expanded = np.tile(v_proj, (repeat, 1))
                OV = o_proj @ v_expanded
                A += OV / N_LAYERS
    
    gate_proj = load_tensor(f"{base}.mlp.gate_proj.weight")
    up_proj = load_tensor(f"{base}.mlp.up_proj.weight")
    down_proj = load_tensor(f"{base}.mlp.down_proj.weight")
    
    if gate_proj is not None and up_proj is not None and down_proj is not None:
        FFN = down_proj @ up_proj
        ffn_scale = np.linalg.norm(FFN, 'fro') / np.linalg.norm(A, 'fro')
        A += FFN / (ffn_scale * np.sqrt(N_LAYERS))
    
    return A


def compose_full_model():
    """Compose T = A_63 @ ... @ A_0 and save to disk."""
    print(f"\n  Phase 1: Composing {N_LAYERS} layers...", flush=True)
    t0 = time.time()
    
    T = np.eye(D_MODEL, dtype=np.float32)
    
    for i in range(N_LAYERS):
        A_i = compute_layer_matrix(i)
        T = A_i @ T
        
        if (i + 1) % 8 == 0:
            _, S, _ = np.linalg.svd(T, full_matrices=False)
            rank90 = int(np.searchsorted(np.cumsum(S**2) / np.sum(S**2), 0.90)) + 1
            print(f"    L{i:2d}: rank90={rank90:3d}, σ₁={S[0]:.4f}, ||T||={np.linalg.norm(T, 'fro'):.2f}  "
                  f"[{time.time()-t0:.0f}s]", flush=True)
    
    # Save
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    np.save(str(CACHE_PATH), T)
    print(f"\n  Saved T_full ({T.shape}) to {CACHE_PATH}")
    print(f"  Composition took {time.time()-t0:.0f}s")
    
    return T


def sweep_dimensions(T_full):
    """Sweep d_student and measure ternary quality at each."""
    print(f"\n  Phase 2: Sweeping student dimensions...", flush=True)
    t0 = time.time()
    
    np.random.seed(42)
    
    # Full SVD of teacher transform
    print(f"  Computing SVD of T_full ({T_full.shape})...", flush=True)
    U_T, S_T, Vt_T = np.linalg.svd(T_full, full_matrices=False)
    
    total_energy = np.sum(S_T**2)
    cum_energy = np.cumsum(S_T**2) / total_energy
    
    print(f"\n  Singular value spectrum:")
    rank_thresholds = {}
    for threshold in [0.50, 0.70, 0.80, 0.85, 0.90, 0.95, 0.99, 0.999]:
        rank = int(np.searchsorted(cum_energy, threshold)) + 1
        rank_thresholds[f"rank{int(threshold*100)}"] = rank
        print(f"    rank{int(threshold*100):3d}: {rank:4d} dims capture {threshold*100:.1f}% of energy")
    
    print(f"\n  Top 50 singular values:")
    for i in range(0, 50, 5):
        vals = [f"{S_T[j]:.4f}" for j in range(i, min(i+5, len(S_T)))]
        print(f"    [{i:3d}-{min(i+4,len(S_T)-1):3d}]: {', '.join(vals)}")
    
    # Load embedding for SVD basis
    print(f"\n  Loading embedding for projection basis...", flush=True)
    from sklearn.utils.extmath import randomized_svd
    E = load_tensor("model.language_model.embed_tokens.weight")
    print(f"  Computing full embedding SVD...", flush=True)
    # We only need up to 5120 components
    _, S_emb, Vt_emb = randomized_svd(E, n_components=min(D_MODEL, E.shape[0]), random_state=42)
    V_full = Vt_emb.T  # (5120, min(5120, vocab))
    
    # Dimension sweep
    d_values = sorted(set([
        8, 16, 24, 27, 32, 48, 64, 96, 128,
        160, 192, 256, 320, 384, 448, 512,
        640, 768, 896, 1024, 1280,
        1536, 1792, 2048,
        2560, 3072, 3584, 4096,
        4608, 5120,
    ]))
    d_values = [d for d in d_values if d <= V_full.shape[1]]
    
    # Teacher-space ternary quality (the ceiling)
    signs_t = np.sign(T_full).astype(np.float32)
    gamma_t = np.mean(np.abs(T_full), axis=1)
    x_test = np.random.randn(500, D_MODEL).astype(np.float32)
    y_t_full = x_test @ T_full.T
    y_t_tern = (x_test @ signs_t.T) * gamma_t[None, :]
    t_per_dim_list = []
    for d in range(D_MODEL):
        if y_t_full[:, d].std() > 1e-10:
            c = np.corrcoef(y_t_full[:, d], y_t_tern[:, d])[0, 1]
            if not np.isnan(c):
                t_per_dim_list.append(c)
    teacher_per_dim = float(np.mean(t_per_dim_list))
    teacher_global = float(np.corrcoef(y_t_full.flatten(), y_t_tern.flatten())[0, 1])
    print(f"\n  Teacher space (d=5120): per_dim={teacher_per_dim:.4f}, global={teacher_global:.4f}")
    
    results = []
    
    for d in d_values:
        V_proj = V_full[:, :d]  # (5120, d)
        
        # Project
        T_s = V_proj.T @ T_full @ V_proj  # (d, d)
        
        # Ternary
        signs = np.sign(T_s).astype(np.float32)
        gamma = np.mean(np.abs(T_s), axis=1)
        
        # Test in student space
        n_test = 500
        x_s = np.random.randn(n_test, d).astype(np.float32)
        y_full = x_s @ T_s.T
        y_tern = (x_s @ signs.T) * gamma[None, :]
        
        # Global correlation
        global_corr = float(np.corrcoef(y_full.flatten(), y_tern.flatten())[0, 1])
        
        # Per-dim correlation
        per_dim = []
        for dim in range(d):
            if y_full[:, dim].std() > 1e-10:
                c = np.corrcoef(y_full[:, dim], y_tern[:, dim])[0, 1]
                if not np.isnan(c):
                    per_dim.append(c)
        mean_per_dim = float(np.mean(per_dim)) if per_dim else 0.0
        
        # Cosine similarity
        y_fn = y_full / (np.linalg.norm(y_full, axis=1, keepdims=True) + 1e-10)
        y_tn = y_tern / (np.linalg.norm(y_tern, axis=1, keepdims=True) + 1e-10)
        cos_sim = float(np.mean(np.sum(y_fn * y_tn, axis=1)))
        
        # E2E: teacher input → ternary student output vs teacher output projected
        x_t = np.random.randn(n_test, D_MODEL).astype(np.float32)
        y_t = x_t @ T_full.T
        y_t_proj = y_t @ V_proj  # project teacher output to student space
        x_s_from_t = x_t @ V_proj  # project teacher input to student space
        y_tern_e2e = (x_s_from_t @ signs.T) * gamma[None, :]
        
        e2e_per_dim = []
        for dim in range(d):
            if y_t_proj[:, dim].std() > 1e-10 and y_tern_e2e[:, dim].std() > 1e-10:
                c = np.corrcoef(y_t_proj[:, dim], y_tern_e2e[:, dim])[0, 1]
                if not np.isnan(c):
                    e2e_per_dim.append(c)
        mean_e2e = float(np.mean(e2e_per_dim)) if e2e_per_dim else 0.0
        
        # SV energy at this d
        sv_energy = float(cum_energy[min(d-1, len(cum_energy)-1)])
        
        # Rank of T_student
        _, S_s, _ = np.linalg.svd(T_s, full_matrices=False)
        cum_s = np.cumsum(S_s**2) / (np.sum(S_s**2) + 1e-10)
        rank90_s = int(np.searchsorted(cum_s, 0.90)) + 1
        
        result = {
            "d_student": d,
            "per_dim_corr": mean_per_dim,
            "global_corr": global_corr,
            "cosine_sim": cos_sim,
            "e2e_per_dim": mean_e2e,
            "sv_energy_top_d": sv_energy,
            "rank90_student": rank90_s,
            "ternary_positions": d * d,
            "plate_size_mb": (d * d) / (8 * 1024 * 1024),
        }
        results.append(result)
        
        print(f"    d={d:5d}: per_dim={mean_per_dim:.4f}  e2e={mean_e2e:.4f}  "
              f"sv={sv_energy:.4f}  rank90={rank90_s:3d}  "
              f"plate={d*d/1e6:.1f}M ({d*d/(8*1024*1024):.2f}MB)",
              flush=True)
    
    # Find crossings
    target_90 = next((r for r in results if r['per_dim_corr'] >= 0.90), None)
    target_95 = next((r for r in results if r['per_dim_corr'] >= 0.95), None)
    
    # Also check: what if we use T_teacher's OWN SVD as projection basis
    # instead of embedding SVD? This gives the OPTIMAL projection.
    print(f"\n  Bonus: Using T_teacher's OWN SVD basis (optimal projection)...", flush=True)
    optimal_results = []
    for d in [27, 48, 64, 128, 256, 512, 1024, 1280, 2048, 3072, 5120]:
        if d > D_MODEL:
            continue
        V_opt = Vt_T[:d, :].T  # (5120, d) — top-d right singular vectors of T
        
        T_opt = V_opt.T @ T_full @ V_opt
        signs_o = np.sign(T_opt).astype(np.float32)
        gamma_o = np.mean(np.abs(T_opt), axis=1)
        
        x_o = np.random.randn(500, d).astype(np.float32)
        y_o_full = x_o @ T_opt.T
        y_o_tern = (x_o @ signs_o.T) * gamma_o[None, :]
        
        pd = []
        for dim in range(d):
            if y_o_full[:, dim].std() > 1e-10:
                c = np.corrcoef(y_o_full[:, dim], y_o_tern[:, dim])[0, 1]
                if not np.isnan(c):
                    pd.append(c)
        mpd = float(np.mean(pd)) if pd else 0.0
        gc = float(np.corrcoef(y_o_full.flatten(), y_o_tern.flatten())[0, 1])
        
        optimal_results.append({
            "d": d,
            "per_dim_corr": mpd,
            "global_corr": gc,
            "sv_energy": float(cum_energy[min(d-1, len(cum_energy)-1)]),
        })
        
        print(f"    d={d:5d}: per_dim={mpd:.4f}  global={gc:.4f}  "
              f"sv_energy={cum_energy[min(d-1,len(cum_energy)-1)]:.4f}",
              flush=True)
    
    target_95_opt = next((r for r in optimal_results if r['per_dim_corr'] >= 0.95), None)
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"  RESULTS TABLE")
    print(f"{'='*80}")
    
    print(f"\n  {'d':>6s} | {'per_dim':>8s} | {'e2e':>8s} | {'global':>8s} | {'cos':>8s} | {'sv_energy':>10s} | {'positions':>12s} | {'MB':>8s}")
    print(f"  {'-'*6} | {'-'*8} | {'-'*8} | {'-'*8} | {'-'*8} | {'-'*10} | {'-'*12} | {'-'*8}")
    
    for r in results:
        flag = ""
        if target_90 and r['d_student'] == target_90['d_student'] and target_90 != target_95:
            flag = " ← 90%"
        if target_95 and r['d_student'] == target_95['d_student']:
            flag = " ← 95%"
        if r['d_student'] == 1280:
            flag = flag or " ← current"
        
        print(f"  {r['d_student']:>6d} | {r['per_dim_corr']:>8.4f} | {r['e2e_per_dim']:>8.4f} | "
              f"{r['global_corr']:>8.4f} | {r['cosine_sim']:>8.4f} | "
              f"{r['sv_energy_top_d']:>10.6f} | {r['ternary_positions']:>12,} | "
              f"{r['plate_size_mb']:>8.2f}{flag}")
    
    print(f"\n  Teacher (d=5120): per_dim={teacher_per_dim:.4f}")
    
    print(f"\n{'='*80}")
    print(f"  KEY FINDINGS")
    print(f"{'='*80}")
    
    if target_90:
        print(f"\n  90% per-dim crossing: d={target_90['d_student']}")
        print(f"    Positions: {target_90['ternary_positions']:,} ({target_90['plate_size_mb']:.2f} MB)")
    
    if target_95:
        print(f"\n  95% per-dim crossing: d={target_95['d_student']}")
        print(f"    Positions: {target_95['ternary_positions']:,} ({target_95['plate_size_mb']:.2f} MB)")
        current = next(r for r in results if r['d_student'] == 1280)
        print(f"    vs current (d=1280, {current['per_dim_corr']:.4f}):")
        print(f"    d increase: {target_95['d_student']/1280:.1f}×")
        print(f"    position increase: {target_95['ternary_positions']/current['ternary_positions']:.1f}×")
    else:
        print(f"\n  95% per-dim NOT reached!")
        print(f"  Teacher ceiling: {teacher_per_dim:.4f}")
        if teacher_per_dim < 0.95:
            print(f"  ⚠ The ceiling ({teacher_per_dim:.4f}) is BELOW 95%!")
            print(f"  Gap is in ternary approximation (sign+gamma), not dimension.")
    
    if target_95_opt:
        print(f"\n  With OPTIMAL projection basis (T's own SVD):")
        print(f"    95% per-dim at d={target_95_opt['d']}")
        print(f"    (vs embedding-SVD basis which may be suboptimal)")
    
    # Save
    out_dir = Path("results/extraction-dimension-sweep")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    output = {
        "teacher_per_dim": teacher_per_dim,
        "teacher_global": teacher_global,
        "singular_values_top100": S_T[:100].tolist(),
        "rank_thresholds": rank_thresholds,
        "embedding_basis_sweep": results,
        "optimal_basis_sweep": optimal_results,
        "target_90_emb": target_90,
        "target_95_emb": target_95,
        "target_95_opt": target_95_opt,
    }
    
    with open(out_dir / "results.json", "w") as f:
        json.dump(output, f, indent=2, default=lambda x: float(x) if isinstance(x, (np.floating, np.integer)) else x)
    
    print(f"\n  Saved to {out_dir}/results.json")
    print(f"  Phase 2 took {time.time()-t0:.0f}s")
    
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--compose", action="store_true", help="Phase 1 only: compose and save T_full")
    parser.add_argument("--sweep", action="store_true", help="Phase 2 only: load T_full and sweep dimensions")
    args = parser.parse_args()
    
    if not args.compose and not args.sweep:
        args.compose = True
        args.sweep = True
    
    T_full = None
    
    if args.compose:
        T_full = compose_full_model()
    
    if args.sweep:
        if T_full is None:
            if CACHE_PATH.exists():
                print(f"\n  Loading cached T_full from {CACHE_PATH}...", flush=True)
                T_full = np.load(str(CACHE_PATH))
                print(f"  Loaded: shape={T_full.shape}")
            else:
                print(f"\n  ERROR: {CACHE_PATH} not found. Run with --compose first.")
                sys.exit(1)
        
        sweep_dimensions(T_full)


if __name__ == "__main__":
    main()
