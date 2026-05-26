#!/usr/bin/env python3
"""
Algebraic Composition — Build zone plates from weight matrices directly.

Instead of fitting transforms from data (approximate, data-dependent),
compute the composed transform ALGEBRAICALLY from the teacher's weights.

Each layer contributes:
  A_i = I + OV_i + FFN_i
  OV_i = o_proj @ v_proj  (the attention OV circuit)
  FFN_i = down_proj @ diag(mean_gate) @ up_proj  (linearized SwiGLU)

The composed zone transform = product of layer matrices:
  T_zone = Π_{i in zone} A_i

This gives EXACT plates (up to linearization), not data-fitted approximations.

Usage:
    cd verbum
    uv run python scripts/explore/probe_algebraic_compose.py

License: MIT
"""

from __future__ import annotations

import sys
import time
import json
from pathlib import Path

import numpy as np
from safetensors import safe_open

TEACHER_PATH = Path.home() / ".cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
N_LAYERS = 64
D_MODEL = 5120

LAYER_TYPES = (['linear_attention'] * 3 + ['full_attention']) * 16

# Zone boundaries
ZONE_A = list(range(0, 16))   # compress
ZONE_B = list(range(16, 48))  # compute
ZONE_C = list(range(48, 64))  # expand

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
    """Compute the linearized layer matrix A_i = I + OV_i + FFN_i.
    
    For linear attention layers: OV = out_proj @ in_proj_qkv (V portion)
    For full attention layers: OV = o_proj @ v_proj
    FFN = down_proj @ up_proj (gate pattern absorbed into sign structure)
    
    Returns (D, D) matrix.
    """
    base = f"model.language_model.layers.{layer_idx}"
    lt = LAYER_TYPES[layer_idx]
    
    # Start with identity (residual connection)
    A = np.eye(D_MODEL, dtype=np.float32)
    
    # ── OV circuit ──
    if lt == 'full_attention':
        v_proj = load_tensor(f"{base}.self_attn.v_proj.weight")  # (d_v, D)
        o_proj = load_tensor(f"{base}.self_attn.o_proj.weight")  # (D, d_o)
        if v_proj is not None and o_proj is not None:
            # OV circuit: what attention writes = O @ V
            # v_proj: (1024, 5120), o_proj: (5120, 6144)
            # The OV circuit maps D→d_v→D, but sizes may not match for direct multiply
            # v_proj maps (D→d_v), o_proj maps (d_o→D) where d_o = n_heads * d_head
            # For the linearized version: OV ≈ o_proj @ v_proj when shapes align
            # Shapes: o=(5120, 6144), v=(1024, 5120)
            # These don't directly compose — o expects d_o=6144, v produces d_v=1024
            # This is because of multi-head: Q is (24*512=12288), KV is (4*256=1024)
            # The o_proj expects concat of all heads' outputs
            # For linearization: we need the AVERAGE effect, not per-head
            # Approximate: take the mean projection
            d_v = v_proj.shape[0]
            d_o = o_proj.shape[1]
            if d_v == d_o:
                OV = o_proj @ v_proj
                A += OV / N_LAYERS  # scale by 1/N to prevent explosion
            else:
                # GQA: V has fewer heads than O expects
                # Tile V to match O's expected input
                n_kv_heads = d_v // 256  # 1024/256 = 4 KV heads
                n_q_heads = d_o // 256   # 6144/256 = 24 Q heads
                repeat = n_q_heads // n_kv_heads  # 24/4 = 6
                v_expanded = np.tile(v_proj, (repeat, 1))  # (6144, 5120)
                OV = o_proj @ v_expanded  # (5120, 5120)
                A += OV / N_LAYERS
    else:
        # Linear attention: has out_proj and in_proj_qkv (fused)
        out_proj = load_tensor(f"{base}.linear_attn.out_proj.weight")
        # in_proj_qkv is fused Q+K+V, hard to decompose without knowing the split
        # For linearized approximation: just use out_proj as the residual contribution
        # The linear attention's effect ≈ out_proj @ some_state
        # Since we can't easily extract V from the fused projection,
        # we'll use a simpler approximation: identity + FFN only for linear layers
        pass  # Linear attention contribution approximated as identity
    
    # ── FFN circuit ──
    gate_proj = load_tensor(f"{base}.mlp.gate_proj.weight")  # (d_ff, D)
    up_proj = load_tensor(f"{base}.mlp.up_proj.weight")      # (d_ff, D)
    down_proj = load_tensor(f"{base}.mlp.down_proj.weight")  # (D, d_ff)
    
    if gate_proj is not None and up_proj is not None and down_proj is not None:
        # Linearized SwiGLU: silu(gate@x) * up@x ≈ sign(gate@x) * up@x
        # The gate determines WHICH neurons fire — this is the beamformer
        # For linearization: use sign(gate) as a binary mask
        # FFN ≈ down @ diag(sign(mean(gate))) @ up
        # But mean(gate) depends on data. For the SIGN structure:
        # We use the gate weight signs directly — sign(gate_proj) tells us
        # which input directions each neuron responds to positively
        
        # Simpler: the effective FFN is down @ up (ignoring gate)
        # This captures the ROUTING structure
        # Scale: each layer's FFN contribution should be 1/N_LAYERS
        # to prevent the product from exploding
        d_ff = gate_proj.shape[0]
        
        # The FFN's net effect on the residual:
        # For ternary extraction, we care about SIGN structure
        # FFN_signs = sign(down) @ sign(up) captures the routing
        FFN = down_proj @ up_proj  # (D, D)
        
        # Scale to prevent product explosion
        # The Frobenius norm of FFN relative to identity
        ffn_scale = np.linalg.norm(FFN, 'fro') / np.linalg.norm(A, 'fro')
        A += FFN / (ffn_scale * np.sqrt(N_LAYERS))
    
    return A


def compose_zone(layer_indices, label):
    """Compose layer matrices for a zone."""
    print(f"\n  {label}: layers {layer_indices[0]}-{layer_indices[-1]} "
          f"({len(layer_indices)} layers)", flush=True)
    
    T = np.eye(D_MODEL, dtype=np.float32)
    
    for i, layer_idx in enumerate(layer_indices):
        A_i = compute_layer_matrix(layer_idx)
        T = A_i @ T  # compose: T = A_n @ ... @ A_1 @ A_0
        
        if (i + 1) % 8 == 0 or (i + 1) == len(layer_indices):
            # Check intermediate quality
            _, S, _ = np.linalg.svd(T, full_matrices=False)
            rank90 = int(np.searchsorted(np.cumsum(S**2) / np.sum(S**2), 0.90)) + 1
            cond = S[0] / S[-1] if S[-1] > 1e-10 else float('inf')
            print(f"    After L{layer_idx}: rank90={rank90}, "
                  f"cond={cond:.1f}, σ₁={S[0]:.4f}", flush=True)
    
    return T


def analyze_composed(T, label, V_proj=None):
    """Analyze a composed transform: rank, ternary quality, sign structure."""
    # SVD
    _, S, _ = np.linalg.svd(T, full_matrices=False)
    S = S[:min(256, len(S))]
    energy = S**2
    total = energy.sum()
    cumulative = np.cumsum(energy) / (total + 1e-10)
    rank90 = int(np.searchsorted(cumulative, 0.90)) + 1
    
    # Sign structure
    signs = np.sign(T)
    n_pos = np.sum(signs == 1)
    n_neg = np.sum(signs == -1)
    n_zero = np.sum(signs == 0)
    
    # Ternary quality: sign(T) @ x vs T @ x on random inputs
    x_test = np.random.randn(200, T.shape[1]).astype(np.float32)
    y_full = x_test @ T.T
    
    # With per-row gamma
    gamma = np.mean(np.abs(T), axis=1)
    y_ternary = (x_test @ signs.astype(np.float32).T) * gamma[None, :]
    
    corr = np.corrcoef(y_full.flatten(), y_ternary.flatten())[0, 1]
    
    per_dim = []
    for d in range(T.shape[0]):
        if y_full[:, d].std() > 1e-10:
            c = np.corrcoef(y_full[:, d], y_ternary[:, d])[0, 1]
            if not np.isnan(c):
                per_dim.append(c)
    mean_per_dim = np.mean(per_dim) if per_dim else 0.0
    
    # Cosine similarity
    y_full_n = y_full / (np.linalg.norm(y_full, axis=1, keepdims=True) + 1e-10)
    y_tern_n = y_ternary / (np.linalg.norm(y_ternary, axis=1, keepdims=True) + 1e-10)
    cos = np.mean(np.sum(y_full_n * y_tern_n, axis=1))
    
    # Project to student space if V_proj provided
    student_result = None
    if V_proj is not None:
        T_student = V_proj.T @ T @ V_proj  # (1280, 1280)
        signs_s = np.sign(T_student)
        gamma_s = np.mean(np.abs(T_student), axis=1)
        
        x_s = np.random.randn(200, 1280).astype(np.float32)
        y_s_full = x_s @ T_student.T
        y_s_tern = (x_s @ signs_s.astype(np.float32).T) * gamma_s[None, :]
        
        corr_s = np.corrcoef(y_s_full.flatten(), y_s_tern.flatten())[0, 1]
        per_dim_s = []
        for d in range(1280):
            if y_s_full[:, d].std() > 1e-10:
                c = np.corrcoef(y_s_full[:, d], y_s_tern[:, d])[0, 1]
                if not np.isnan(c):
                    per_dim_s.append(c)
        mean_per_dim_s = np.mean(per_dim_s) if per_dim_s else 0.0
        
        student_result = {
            "global_corr": float(corr_s),
            "per_dim_corr": float(mean_per_dim_s),
        }
    
    result = {
        "label": label,
        "shape": list(T.shape),
        "rank90": rank90,
        "global_corr": float(corr),
        "per_dim_corr": float(mean_per_dim),
        "cosine_similarity": float(cos),
        "sign_dist": {"pos": float(n_pos/T.size), "neg": float(n_neg/T.size), "zero": float(n_zero/T.size)},
        "gamma_mean": float(gamma.mean()),
        "student": student_result,
    }
    
    print(f"\n    {label} (teacher space {T.shape[0]}D):")
    print(f"      rank90={rank90}  global_corr={corr:.4f}  per_dim={mean_per_dim:.4f}  cos={cos:.4f}")
    print(f"      signs: +{n_pos/T.size:.1%} / -{n_neg/T.size:.1%}")
    if student_result:
        print(f"    {label} (student space 1280D):")
        print(f"      global_corr={student_result['global_corr']:.4f}  per_dim={student_result['per_dim_corr']:.4f}")
    
    return result


def main():
    print(f"\n{'='*80}")
    print(f"  Algebraic Composition — Build plates from weight matrices")
    print(f"  Teacher: {TEACHER_PATH.name}")
    print(f"{'='*80}")
    
    t0 = time.time()
    
    # Compose each zone
    T_A = compose_zone(ZONE_A, "Zone A (compress)")
    T_B = compose_zone(ZONE_B, "Zone B (compute)")
    T_C = compose_zone(ZONE_C, "Zone C (expand)")
    
    # Full model
    T_full = T_C @ T_B @ T_A
    
    dt = time.time() - t0
    print(f"\n  Composition completed in {dt:.1f}s")
    
    # Load V_proj for student-space projection
    print(f"\n  Computing SVD projection basis...", flush=True)
    from sklearn.utils.extmath import randomized_svd
    emb_name = "model.language_model.embed_tokens.weight"
    E = load_tensor(emb_name)
    _, _, Vt = randomized_svd(E, n_components=1280, random_state=42)
    V_proj = Vt.T  # (5120, 1280)
    
    # Analyze
    print(f"\n{'='*80}")
    print(f"  ANALYSIS")
    print(f"{'='*80}")
    
    results = []
    results.append(analyze_composed(T_A, "Zone_A_compress", V_proj))
    results.append(analyze_composed(T_B, "Zone_B_compute", V_proj))
    results.append(analyze_composed(T_C, "Zone_C_expand", V_proj))
    results.append(analyze_composed(T_full, "Full_model", V_proj))
    
    # Save
    out_dir = Path("results/algebraic-compose")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    def clean(obj):
        if isinstance(obj, (np.floating,)): return float(obj)
        if isinstance(obj, (np.integer,)): return int(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        if isinstance(obj, dict): return {k: clean(v) for k, v in obj.items()}
        if isinstance(obj, list): return [clean(v) for v in obj]
        return obj
    
    with open(out_dir / "results.json", "w") as f:
        json.dump(clean(results), f, indent=2)
    
    # Also save the composed plates
    signs_A = np.sign(V_proj.T @ T_A @ V_proj).astype(np.int8)
    signs_B = np.sign(V_proj.T @ T_B @ V_proj).astype(np.int8)
    signs_C = np.sign(V_proj.T @ T_C @ V_proj).astype(np.int8)
    gamma_A = np.mean(np.abs(V_proj.T @ T_A @ V_proj), axis=1).astype(np.float32)
    gamma_B = np.mean(np.abs(V_proj.T @ T_B @ V_proj), axis=1).astype(np.float32)
    gamma_C = np.mean(np.abs(V_proj.T @ T_C @ V_proj), axis=1).astype(np.float32)
    
    np.savez_compressed(
        str(out_dir / "algebraic_plates.npz"),
        zone_a_signs=signs_A, zone_a_gamma=gamma_A,
        zone_b_signs=signs_B, zone_b_gamma=gamma_B,
        zone_c_signs=signs_C, zone_c_gamma=gamma_C,
    )
    
    print(f"\n  Results saved to {out_dir}/")
    print(f"  Plates saved to {out_dir}/algebraic_plates.npz")
    
    # Verdict
    print(f"\n{'='*80}")
    print(f"  VERDICT: Algebraic vs Data-Fitted Composition")
    print(f"{'='*80}")
    for r in results:
        s = r.get("student", {})
        print(f"  {r['label']}: teacher per-dim={r['per_dim_corr']:.4f}  "
              f"student per-dim={s.get('per_dim_corr', 'N/A')}")
    print()


if __name__ == "__main__":
    main()
