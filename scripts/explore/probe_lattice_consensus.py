#!/usr/bin/env python3
"""
probe_lattice_consensus.py — Cross-model vote on the universal lattice.

Loads multiple teacher models sequentially. For each:
  1. Extracts FFN gate_proj weights at relative depths
  2. Projects into crystal eigenbasis (16 universal PCs)
  3. Computes per-neuron PC assignment + sign pattern
  4. Extracts attention M-space mode structure

Then votes across models: positions where ALL agree → irreducible lattice.

Models: Qwen3-0.6B, Qwen3-4B, Qwen3-8B, Qwen3-14B
(Qwen3.6-27B and Qwen3-32B are too large for sequential loading;
can be added if memory permits)

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)

import numpy as np


# ══════════════════════════════════════════════════════════════════════
# Crystal eigenbasis (universal — from micro_model.py Zone B targets)
# ══════════════════════════════════════════════════════════════════════

PCAQ_ZONE_B_TARGETS = np.array([
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
], dtype=np.float32)

COMBINATOR_NAMES = ["K", "I", "B", "C", "D", "Y", "W", "WHNF",
                    "āK", "āI", "āB", "āC", "āD", "āY", "āW", "āWHNF"]


def crystal_eigenbasis():
    """Compute universal crystal eigenbasis from Zone B targets."""
    eigvals, eigvecs = np.linalg.eigh(PCAQ_ZONE_B_TARGETS)
    idx = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]
    return eigvals, eigvecs


# ══════════════════════════════════════════════════════════════════════
# Model extraction
# ══════════════════════════════════════════════════════════════════════

MODELS = [
    ("Qwen3-0.6B", "Qwen/Qwen3-0.6B"),
    ("Qwen3-4B", "Qwen/Qwen3-4B"),
    ("Qwen3-8B", "Qwen/Qwen3-8B"),
    ("Qwen3-14B", "Qwen/Qwen3-14B"),
]

# Relative depths to sample (0.0 = first layer, 1.0 = last layer)
DEPTH_GRID = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


def extract_model_signatures(model_name: str, model_id: str, eigvecs: np.ndarray) -> dict:
    """Load a model, extract gate_proj crystal projections + M-space, unload.

    For each sampled layer:
      - FFN gate_proj: project each row into crystal eigenbasis → sign pattern
      - Attention: compute M = W_q^T @ W_k → SVD → mode structure

    Returns dict with projections and M-space info per relative depth.
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoConfig

    print(f"\n  Loading {model_name} ({model_id})...", flush=True)
    t0 = time.time()

    config = AutoConfig.from_pretrained(model_id, trust_remote_code=True)
    n_layers = config.num_hidden_layers
    d_model = config.hidden_size
    d_ff = config.intermediate_size

    # Load with minimal memory — we only need specific weight tensors
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float32,
        device_map="cpu",
        trust_remote_code=True,
    )

    print(f"  Loaded in {time.time()-t0:.0f}s: {n_layers} layers, d={d_model}, d_ff={d_ff}", flush=True)

    result = {
        "model_name": model_name,
        "model_id": model_id,
        "n_layers": n_layers,
        "d_model": d_model,
        "d_ff": d_ff,
        "depths": {},
    }

    n_pcs = eigvecs.shape[1]  # 16

    for rel_depth in DEPTH_GRID:
        layer_idx = min(int(rel_depth * (n_layers - 1)), n_layers - 1)
        layer = model.model.layers[layer_idx]

        # ── FFN gate_proj projection into crystal eigenbasis ──
        gate_w = layer.mlp.gate_proj.weight.detach().numpy()  # (d_ff, d_model)

        # Project each row into crystal eigenbasis
        # The eigenvectors are 16×16 (combinator space). We need to project
        # d_model-dimensional gate rows into this space.
        # Strategy: use the first min(16, d_model) dimensions as the
        # crystal subspace, project gate rows onto eigenvectors.
        #
        # More principled: the crystal operates in d_model space via the
        # embedding. We project gate rows onto the direction defined by
        # each eigenvector component pattern.
        #
        # Simplest: take the sign pattern of each eigenvector as a
        # d_model-agnostic fingerprint. For each gate row, compute
        # correlation with each eigenvector's sign pattern (tiled/truncated).

        # Build crystal projection matrix: (n_pcs, d_model)
        # Each PC defines a direction via its eigenvector components.
        # For cross-model comparison, we tile the 16-dim eigenvector
        # across d_model groups of 16.
        n_groups = d_model // n_pcs
        remainder = d_model % n_pcs

        # Build projection basis: tile eigenvectors across d_model
        proj_basis = np.zeros((n_pcs, d_model), dtype=np.float32)
        for pc in range(n_pcs):
            ev = eigvecs[:, pc]  # (16,) — one eigenvector
            # Tile across groups
            for g in range(n_groups):
                proj_basis[pc, g*n_pcs:(g+1)*n_pcs] = ev
            if remainder > 0:
                proj_basis[pc, n_groups*n_pcs:] = ev[:remainder]
            # Normalize
            norm = np.linalg.norm(proj_basis[pc])
            if norm > 0:
                proj_basis[pc] /= norm

        # Project gate rows: (d_ff, d_model) @ (d_model, n_pcs) → (d_ff, n_pcs)
        gate_proj_crystal = gate_w @ proj_basis.T  # (d_ff, n_pcs)

        # Dominant PC per neuron
        dominant_pc = np.argmax(np.abs(gate_proj_crystal), axis=1)  # (d_ff,)

        # Sign pattern: sign of projection onto each PC
        sign_pattern = np.sign(gate_proj_crystal)  # (d_ff, n_pcs)

        # PC allocation: how many neurons serve each PC
        pc_counts = np.bincount(dominant_pc, minlength=n_pcs)

        # ── Attention M-space (via K's rank structure) ──
        try:
            k_w = layer.self_attn.k_proj.weight.detach().numpy()  # (k_out, d_model)
            # Use K^T @ K — always well-defined regardless of GQA config
            M = k_w.T @ k_w  # (d_model, d_model)
            _, s, _ = np.linalg.svd(M, full_matrices=False)
            total = (s ** 2).sum()
            if total > 0:
                cum = np.cumsum(s ** 2) / total
                rank90 = int(np.searchsorted(cum, 0.90) + 1)
                top1_pct = float(cum[0] * 100)
            else:
                rank90 = len(s)
                top1_pct = 0.0
        except Exception as e:
            print(f"      M-space error at L{layer_idx}: {e}", flush=True)
            rank90 = -1
            top1_pct = 0.0

        result["depths"][rel_depth] = {
            "layer_idx": layer_idx,
            "gate_sign_pattern": sign_pattern,       # (d_ff, n_pcs) — the per-neuron signs
            "gate_dominant_pc": dominant_pc,          # (d_ff,) — which PC each neuron serves
            "gate_pc_counts": pc_counts,              # (n_pcs,) — allocation
            "mspace_rank90": rank90,
            "mspace_top1_pct": top1_pct,
        }

        print(f"    depth={rel_depth:.1f} (L{layer_idx}): "
              f"pc_alloc=[{','.join(str(c) for c in pc_counts[:8])}] "
              f"M:r90={rank90},t1={top1_pct:.1f}%",
              flush=True)

    # Free
    del model
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return result


# ══════════════════════════════════════════════════════════════════════
# Cross-model consensus
# ══════════════════════════════════════════════════════════════════════

def compute_consensus(model_results: list[dict], eigvecs: np.ndarray) -> dict:
    """Compute cross-model agreement on the lattice.

    For each (relative_depth, PC), compare the sign patterns across models.
    Agreement = fraction of models that assign the same sign to the same
    PC component.
    """
    n_models = len(model_results)
    n_pcs = eigvecs.shape[1]

    consensus = {}

    for rel_depth in DEPTH_GRID:
        # Collect PC allocation patterns
        pc_allocations = []
        for mr in model_results:
            if rel_depth in mr["depths"]:
                counts = mr["depths"][rel_depth]["gate_pc_counts"]
                # Normalize to fractions
                total = counts.sum()
                pc_allocations.append(counts / total if total > 0 else counts)

        pc_allocations = np.array(pc_allocations)  # (n_models, n_pcs)

        # PC allocation agreement: cosine similarity between allocation vectors
        if len(pc_allocations) >= 2:
            alloc_cos = []
            for i in range(n_models):
                for j in range(i+1, n_models):
                    a, b = pc_allocations[i], pc_allocations[j]
                    na, nb = np.linalg.norm(a), np.linalg.norm(b)
                    if na > 0 and nb > 0:
                        alloc_cos.append(float(np.dot(a, b) / (na * nb)))
            mean_alloc_cos = float(np.mean(alloc_cos)) if alloc_cos else 0.0
        else:
            mean_alloc_cos = 1.0

        # Sign agreement per PC: for neurons serving the same PC,
        # do they agree on the sign of their projection onto that PC?
        # This is the core lattice question.
        per_pc_agreement = []
        for pc in range(min(8, n_pcs)):  # Focus on positive PCs (K,I,B,C,D,Y,W,WHNF)
            # For each model, get the signs of neurons serving this PC
            signs_per_model = []
            for mr in model_results:
                d = mr["depths"].get(rel_depth)
                if d is None:
                    continue
                mask = d["gate_dominant_pc"] == pc
                if mask.sum() == 0:
                    continue
                # Sign of this PC's projection for neurons assigned to it
                pc_signs = d["gate_sign_pattern"][mask, pc]
                # What fraction are +1 vs -1?
                frac_pos = float((pc_signs > 0).mean())
                signs_per_model.append(frac_pos)

            if len(signs_per_model) >= 2:
                # Agreement: do models agree on the dominant sign?
                # If all models have >50% positive, they agree on +1
                # If all models have <50%, they agree on -1
                all_pos = all(s > 0.5 for s in signs_per_model)
                all_neg = all(s < 0.5 for s in signs_per_model)
                agreement = 1.0 if (all_pos or all_neg) else 0.0
                dominant = "+1" if all_pos else ("-1" if all_neg else "mixed")
                mean_frac = float(np.mean(signs_per_model))
                per_pc_agreement.append({
                    "pc": pc,
                    "pc_name": COMBINATOR_NAMES[pc],
                    "agreement": agreement,
                    "dominant": dominant,
                    "frac_positive": signs_per_model,
                    "mean_frac_positive": mean_frac,
                })

        # M-space agreement
        mspace_r90s = []
        mspace_t1s = []
        for mr in model_results:
            d = mr["depths"].get(rel_depth)
            if d is not None:
                mspace_r90s.append(d["mspace_rank90"])
                mspace_t1s.append(d["mspace_top1_pct"])

        consensus[rel_depth] = {
            "alloc_cosine": mean_alloc_cos,
            "pc_agreement": per_pc_agreement,
            "mspace_rank90s": mspace_r90s,
            "mspace_top1s": mspace_t1s,
        }

    return consensus


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def serialize(obj):
    """Convert numpy types for JSON serialization."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, dict):
        return {str(k): serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize(v) for v in obj]
    return obj


def save_model_result(out_dir: Path, model_result: dict):
    """Save one model's extracted data incrementally."""
    name = model_result["model_name"]
    save = {
        "model_name": name,
        "model_id": model_result["model_id"],
        "n_layers": model_result["n_layers"],
        "d_model": model_result["d_model"],
        "d_ff": model_result["d_ff"],
        "depths": {},
    }
    for rd, d in model_result["depths"].items():
        save["depths"][str(rd)] = {
            "layer_idx": d["layer_idx"],
            "gate_pc_counts": serialize(d["gate_pc_counts"]),
            "mspace_rank90": d["mspace_rank90"],
            "mspace_top1_pct": d["mspace_top1_pct"],
            # Sign pattern is large — save summary stats instead
            "gate_sign_pos_frac_per_pc": serialize(
                (d["gate_sign_pattern"] > 0).mean(axis=0)),
            "gate_dominant_pc_hist": serialize(
                np.bincount(d["gate_dominant_pc"], minlength=16)),
        }
    path = out_dir / f"model_{name.replace('.', '_').replace('-', '_')}.json"
    with open(path, "w") as f:
        json.dump(save, f, indent=2)
    print(f"    Saved → {path}", flush=True)

    # Also save the full sign patterns as npz (needed for consensus)
    npz_path = out_dir / f"signs_{name.replace('.', '_').replace('-', '_')}.npz"
    arrays = {}
    for rd, d in model_result["depths"].items():
        key = f"depth_{rd:.1f}"
        arrays[f"{key}_sign_pattern"] = d["gate_sign_pattern"]
        arrays[f"{key}_dominant_pc"] = d["gate_dominant_pc"]
    np.savez_compressed(str(npz_path), **arrays)
    print(f"    Saved → {npz_path}", flush=True)


def main():
    t0 = time.time()
    print("=" * 70)
    print("CROSS-MODEL LATTICE CONSENSUS PROBE")
    print("Finding the universal irreducible lattice across models")
    print("=" * 70)
    print()

    out_dir = Path("results/lattice-consensus")
    out_dir.mkdir(parents=True, exist_ok=True)

    eigvals, eigvecs = crystal_eigenbasis()
    print(f"Crystal eigenbasis: {len(eigvals)} PCs")
    print(f"Top eigenvalues: {eigvals[:8].tolist()}")
    print(f"Eigenvalue ratios: {[f'{eigvals[i]/eigvals[0]:.3f}' for i in range(8)]}")
    print()

    # Predicted neuron allocation ∝ eigenvalue
    total_ev = eigvals[eigvals > 0].sum()
    predicted_frac = eigvals[:8] / total_ev
    print(f"Predicted PC allocation fractions (from eigenvalues):")
    for i in range(8):
        print(f"  PC{i} ({COMBINATOR_NAMES[i]}): {predicted_frac[i]:.3f}")
    print()

    # Save eigenbasis for reference
    with open(out_dir / "eigenbasis.json", "w") as f:
        json.dump({"eigvals": eigvals.tolist(),
                    "predicted_fracs": predicted_frac.tolist(),
                    "combinator_names": COMBINATOR_NAMES}, f, indent=2)

    # ── Extract from each model (save incrementally) ──
    model_results = []
    for model_name, model_id in MODELS:
        print(f"\n{'─'*70}", flush=True)
        try:
            result = extract_model_signatures(model_name, model_id, eigvecs)
            save_model_result(out_dir, result)
            model_results.append(result)
            print(f"  ✓ {model_name} complete ({len(model_results)} models done)", flush=True)
        except Exception as e:
            print(f"  ✗ ERROR on {model_name}: {e}", flush=True)
            import traceback
            traceback.print_exc()
            # Continue to next model — don't lose progress
            continue

    print(f"\n{'='*70}", flush=True)
    print(f"Extraction complete: {len(model_results)}/{len(MODELS)} models", flush=True)

    if len(model_results) < 2:
        print("Need at least 2 models for consensus. Exiting.")
        return

    # ── Compute consensus ──
    print("\n" + "=" * 70)
    print("CROSS-MODEL CONSENSUS")
    print("=" * 70)

    consensus = compute_consensus(model_results, eigvecs)

    for rel_depth in DEPTH_GRID:
        c = consensus[rel_depth]
        print(f"\n  Depth {rel_depth:.1f}:")
        print(f"    PC allocation cosine: {c['alloc_cosine']:.3f}")
        print(f"    M-space rank90: {c['mspace_rank90s']}")

        # PC sign agreement
        n_unanimous = sum(1 for p in c['pc_agreement'] if p['agreement'] == 1.0)
        n_total = len(c['pc_agreement'])
        print(f"    PC sign agreement: {n_unanimous}/{n_total} unanimous")
        for p in c['pc_agreement']:
            marker = "✓" if p['agreement'] == 1.0 else "✗"
            print(f"      {marker} PC{p['pc']} ({p['pc_name']:>4}): "
                  f"dominant={p['dominant']:>5} "
                  f"frac_pos={[f'{f:.2f}' for f in p['frac_positive']]}")

    # ── Save consensus ──
    with open(out_dir / "consensus.json", "w") as f:
        json.dump({
            "models": [{"name": mr["model_name"], "id": mr["model_id"],
                         "n_layers": mr["n_layers"], "d_model": mr["d_model"],
                         "d_ff": mr["d_ff"]} for mr in model_results],
            "consensus": serialize(consensus),
        }, f, indent=2)
    print(f"\n  Saved consensus → {out_dir}/consensus.json", flush=True)

    # ── Summary ──
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total_unanimous = 0
    total_pcs_compared = 0
    for rel_depth in DEPTH_GRID:
        c = consensus[rel_depth]
        for p in c['pc_agreement']:
            total_pcs_compared += 1
            if p['agreement'] == 1.0:
                total_unanimous += 1

    print(f"\n  Models compared: {len(model_results)}")
    print(f"    {', '.join(mr['model_name'] for mr in model_results)}")
    if total_pcs_compared > 0:
        print(f"\n  Unanimous agreement: {total_unanimous}/{total_pcs_compared} "
              f"({total_unanimous/total_pcs_compared*100:.1f}%)")

    print(f"\n  PC allocation cosine by depth:")
    for rel_depth in DEPTH_GRID:
        c = consensus[rel_depth]
        print(f"    {rel_depth:.1f}: {c['alloc_cosine']:.3f}")

    elapsed = time.time() - t0
    print(f"\n  Total elapsed: {elapsed:.0f}s ({elapsed/60:.1f}m)")
    print(f"  All results in {out_dir}/", flush=True)


if __name__ == "__main__":
    main()
