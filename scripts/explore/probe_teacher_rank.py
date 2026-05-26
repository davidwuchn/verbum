#!/usr/bin/env python3
"""
Teacher Q/K Rank Structure Probe — Qwen3.6-27B.

Measures: for each layer's Q and K projections, how much energy is
captured by the top-k singular values? If top-8 captures >90%, we
can extract rank-8 Q/K plates instead of full-rank (80× smaller).

Also measures: how rank structure varies by zone (A/B/C) and by
layer type (linear_attn vs full_attn).

Usage:
    cd verbum
    uv run python scripts/explore/probe_teacher_rank.py

License: MIT
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from safetensors import safe_open


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


_SHARD_INDEX_CACHE: dict[str, dict] = {}

def load_tensor(model_path: Path, tensor_name: str) -> np.ndarray:
    """Load a single tensor from sharded safetensors as float32."""
    cache_key = str(model_path)
    if cache_key not in _SHARD_INDEX_CACHE:
        idx_path = model_path / "model.safetensors.index.json"
        if idx_path.exists():
            _SHARD_INDEX_CACHE[cache_key] = json.load(open(idx_path))
    index = _SHARD_INDEX_CACHE.get(cache_key)
    shard_path = None
    if index:
        fname = index.get("weight_map", {}).get(tensor_name)
        if fname:
            shard_path = model_path / fname
    if shard_path is None:
        for sf in sorted(model_path.glob("model*.safetensors")):
            with safe_open(str(sf), framework="pt") as f:
                if tensor_name in f.keys():
                    shard_path = sf
                    break
    if shard_path is None:
        raise FileNotFoundError(f"Tensor {tensor_name!r} not found in {model_path}")
    with safe_open(str(shard_path), framework="pt") as sf:
        return sf.get_tensor(tensor_name).float().numpy()

TEACHER_PATH = Path.home() / ".cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
N_LAYERS = 64
D_MODEL = 5120

# Layer types: [L,L,L,F] × 16
LAYER_TYPES = (['linear_attention'] * 3 + ['full_attention']) * 16

# Tensor name patterns
# Linear attention: fused in_proj_qkv, in_proj_a, in_proj_b, in_proj_z, out_proj
# Full attention:   separate q_proj, k_proj, v_proj, o_proj

def get_projections_for_layer(layer_idx: int) -> list[tuple[str, str]]:
    """Return list of (proj_label, tensor_name) for a layer.
    
    Linear attn has fused QKV + separate A/B/Z + out_proj.
    Full attn has separate Q/K/V/O.
    """
    lt = LAYER_TYPES[layer_idx]
    base = f"model.language_model.layers.{layer_idx}"
    
    if lt == 'linear_attention':
        return [
            ("in_proj_qkv", f"{base}.linear_attn.in_proj_qkv.weight"),
            ("in_proj_a",   f"{base}.linear_attn.in_proj_a.weight"),
            ("in_proj_b",   f"{base}.linear_attn.in_proj_b.weight"),
            ("in_proj_z",   f"{base}.linear_attn.in_proj_z.weight"),
            ("out_proj",    f"{base}.linear_attn.out_proj.weight"),
            ("gate_proj",   f"{base}.mlp.gate_proj.weight"),
            ("up_proj",     f"{base}.mlp.up_proj.weight"),
            ("down_proj",   f"{base}.mlp.down_proj.weight"),
        ]
    else:
        return [
            ("q_proj",    f"{base}.self_attn.q_proj.weight"),
            ("k_proj",    f"{base}.self_attn.k_proj.weight"),
            ("v_proj",    f"{base}.self_attn.v_proj.weight"),
            ("o_proj",    f"{base}.self_attn.o_proj.weight"),
            ("gate_proj", f"{base}.mlp.gate_proj.weight"),
            ("up_proj",   f"{base}.mlp.up_proj.weight"),
            ("down_proj", f"{base}.mlp.down_proj.weight"),
        ]


def analyze_rank(W: np.ndarray, name: str) -> dict:
    """SVD rank analysis of a weight matrix."""
    # Truncated SVD for speed (top 256)
    k = min(256, *W.shape)
    try:
        _, S, _ = np.linalg.svd(W, full_matrices=False)
        S = S[:k]
    except np.linalg.LinAlgError:
        return {"name": name, "error": "SVD failed"}

    energy = S ** 2
    total = energy.sum()
    cumulative = np.cumsum(energy) / (total + 1e-10)

    # Energy captured at various ranks
    ranks = [1, 2, 4, 8, 16, 32, 64, 128]
    energy_at_rank = {}
    for r in ranks:
        if r <= len(cumulative):
            energy_at_rank[f"top_{r}"] = float(cumulative[r - 1])

    # Effective rank at thresholds
    rank_80 = int(np.searchsorted(cumulative, 0.80)) + 1
    rank_90 = int(np.searchsorted(cumulative, 0.90)) + 1
    rank_95 = int(np.searchsorted(cumulative, 0.95)) + 1
    rank_99 = int(np.searchsorted(cumulative, 0.99)) + 1

    # Participation ratio
    fracs = energy / (total + 1e-10)
    pr = (fracs.sum() ** 2) / (np.sum(fracs ** 2) + 1e-10)

    # σ₁/σ₂ ratio
    sv_ratio = float(S[0] / S[1]) if len(S) > 1 and S[1] > 1e-10 else float('inf')

    return {
        "name": name,
        "shape": list(W.shape),
        "rank_80": rank_80,
        "rank_90": rank_90,
        "rank_95": rank_95,
        "rank_99": rank_99,
        "participation_ratio": float(pr),
        "sv_ratio_1_2": sv_ratio,
        "energy_at_rank": energy_at_rank,
        "top_5_sv": S[:5].tolist(),
    }


def main():
    print(f"\n{'='*80}")
    print(f"  Teacher Q/K Rank Structure — Qwen3.6-27B")
    print(f"  Path: {TEACHER_PATH}")
    print(f"{'='*80}")

    # Sample layers across all three zones
    # Zone A: L0-15, Zone B: L16-47, Zone C: L48-63
    sample_layers = [0, 2, 3, 7, 11, 15,  # Zone A (6 layers)
                     16, 20, 24, 31, 35, 39, 43, 47,  # Zone B (8 layers)
                     48, 51, 55, 59, 63]  # Zone C (5 layers)

    results = []
    t0 = time.time()

    for layer_idx in sample_layers:
        lt = LAYER_TYPES[layer_idx]
        zone = "A" if layer_idx < 16 else ("B" if layer_idx < 48 else "C")
        ltype = "lin" if lt == "linear_attention" else "FULL"

        print(f"\n  Layer {layer_idx} ({ltype}, Zone {zone}):", flush=True)

        projections = get_projections_for_layer(layer_idx)
        for proj_label, tname in projections:
            try:
                W = load_tensor(TEACHER_PATH, tname)
            except FileNotFoundError:
                print(f"    {proj_label}: NOT FOUND (skipping)")
                continue

            r = analyze_rank(W, f"L{layer_idx}.{proj_label}")
            r["layer"] = layer_idx
            r["zone"] = zone
            r["layer_type"] = ltype
            r["projection"] = proj_label

            e = r["energy_at_rank"]
            print(f"    {proj_label:<14} {str(r['shape']):<20} "
                  f"rank90={r['rank_90']:<4} PR={r['participation_ratio']:<6.1f} "
                  f"top8={e.get('top_8', 0):.1%} top16={e.get('top_16', 0):.1%} "
                  f"top32={e.get('top_32', 0):.1%}")

            results.append(r)

    dt = time.time() - t0
    print(f"\n  Completed in {dt:.1f}s")

    # ── Summary by zone and projection ──
    print(f"\n{'='*80}")
    print(f"  SUMMARY: Average rank90 and top-8 energy by zone × projection")
    print(f"{'='*80}")

    all_projs = sorted(set(r["projection"] for r in results))
    for zone in ["A", "B", "C"]:
        print(f"\n  Zone {zone}:")
        for proj in all_projs:
            zone_proj = [r for r in results if r["zone"] == zone and r["projection"] == proj]
            if not zone_proj:
                continue
            avg_rank90 = np.mean([r["rank_90"] for r in zone_proj])
            avg_top8 = np.mean([r["energy_at_rank"].get("top_8", 0) for r in zone_proj])
            avg_top16 = np.mean([r["energy_at_rank"].get("top_16", 0) for r in zone_proj])
            avg_top32 = np.mean([r["energy_at_rank"].get("top_32", 0) for r in zone_proj])
            avg_pr = np.mean([r["participation_ratio"] for r in zone_proj])
            print(f"    {proj:<14} rank90={avg_rank90:<6.1f} PR={avg_pr:<6.1f} "
                  f"top8={avg_top8:.1%}  top16={avg_top16:.1%}  top32={avg_top32:.1%}")

    # ── Key question: is rank-8 viable? ──
    print(f"\n{'='*80}")
    print(f"  KEY QUESTION: Is rank-8 Q/K extraction viable?")
    print(f"{'='*80}")

    q_results = [r for r in results if r["projection"] == "q_proj"]
    k_results = [r for r in results if r["projection"] == "k_proj"]

    if q_results:
        q_top8 = np.mean([r["energy_at_rank"].get("top_8", 0) for r in q_results])
        q_top16 = np.mean([r["energy_at_rank"].get("top_16", 0) for r in q_results])
        q_rank90 = np.mean([r["rank_90"] for r in q_results])
        print(f"\n  Q projections: avg top-8 energy = {q_top8:.1%}, top-16 = {q_top16:.1%}, rank90 = {q_rank90:.0f}")

    if k_results:
        k_top8 = np.mean([r["energy_at_rank"].get("top_8", 0) for r in k_results])
        k_top16 = np.mean([r["energy_at_rank"].get("top_16", 0) for r in k_results])
        k_rank90 = np.mean([r["rank_90"] for r in k_results])
        print(f"  K projections: avg top-8 energy = {k_top8:.1%}, top-16 = {k_top16:.1%}, rank90 = {k_rank90:.0f}")

    if q_results and k_results:
        combined_top8 = (q_top8 + k_top8) / 2
        if combined_top8 > 0.9:
            print(f"\n  ★ RANK-8 VIABLE: {combined_top8:.1%} energy captured → 80× smaller Q/K plates")
        elif combined_top8 > 0.7:
            print(f"\n  ◎ RANK-16 MAY WORK: top-8={combined_top8:.1%}, try rank-16")
        else:
            print(f"\n  ✗ FULL RANK NEEDED: top-8={combined_top8:.1%} — Q/K are high-rank")

    # Also check V and O for comparison
    v_results = [r for r in results if r["projection"] == "v_proj"]
    o_results = [r for r in results if r["projection"] == "o_proj"]
    if v_results:
        v_top8 = np.mean([r["energy_at_rank"].get("top_8", 0) for r in v_results])
        v_rank90 = np.mean([r["rank_90"] for r in v_results])
        print(f"\n  V projections: avg top-8 energy = {v_top8:.1%}, rank90 = {v_rank90:.0f}")
    if o_results:
        o_top8 = np.mean([r["energy_at_rank"].get("top_8", 0) for r in o_results])
        o_rank90 = np.mean([r["rank_90"] for r in o_results])
        print(f"  O projections: avg top-8 energy = {o_top8:.1%}, rank90 = {o_rank90:.0f}")

    # ── Save ──
    out_dir = Path("results/teacher-rank-probe")
    out_dir.mkdir(parents=True, exist_ok=True)

    def clean(obj):
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: clean(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [clean(v) for v in obj]
        return obj

    with open(out_dir / "results.json", "w") as f:
        json.dump(clean(results), f, indent=2)

    print(f"\n  Results saved to {out_dir}/results.json\n")


if __name__ == "__main__":
    main()
__ == "__main__":
    main()
