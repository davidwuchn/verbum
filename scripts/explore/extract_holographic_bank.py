#!/usr/bin/env python3
"""Extract holographic bank from Qwen3-32B.

Pulls ternary weight patterns from combinator-selective heads,
characterizes their structure, and packages into a bank prototype.

Usage:
    uv run python scripts/explore/extract_holographic_bank.py
    uv run python scripts/explore/extract_holographic_bank.py --top-k 10
    uv run python scripts/explore/extract_holographic_bank.py --target-dim 512

License: MIT
"""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

DEFAULT_GGUF = "/Users/mwhitford/localai/models/Qwen3-32B-Q8_0.gguf"
HF_MODEL = "Qwen/Qwen3-32B"
OUTPUT_DIR = Path("results/holographic-bank")
SELECTIVITY_PATH = Path("results/combinator-probe/selectivity_matrices.npz")

COMBINATOR_NAMES = ["K", "I", "B", "C"]

# ══════════════════════════════════════════════════════════════════
# Step 1: Identify extraction targets from selectivity map
# ══════════════════════════════════════════════════════════════════

def identify_targets(sel_path: Path, top_k: int = 10, max_layer: int = 63) -> dict:
    """Find top-K selective heads per combinator."""
    data = np.load(sel_path)
    targets = {}
    for comb in COMBINATOR_NAMES:
        m = data[f"{comb}_vs_control"][:max_layer+1]  # (layers, heads)
        flat = m.flatten()
        top_idx = np.argsort(flat)[-top_k:][::-1]
        heads = []
        for idx in top_idx:
            layer = int(idx // m.shape[1])
            head = int(idx % m.shape[1])
            score = float(flat[idx])
            heads.append({"layer": layer, "head": head, "score": score})
        targets[comb] = heads
    return targets

# ══════════════════════════════════════════════════════════════════
# Step 2: Extract and ternary-quantize weight patterns
# ══════════════════════════════════════════════════════════════════

def extract_head_weights(model, layer_idx: int, head_idx: int) -> dict:
    """Extract Q/K/V/O weight slices for a specific head."""
    layer = model.model.layers[layer_idx]
    attn = layer.self_attn
    
    head_dim = model.config.hidden_size // model.config.num_attention_heads
    n_kv_heads = model.config.num_key_value_heads
    kv_head_dim = model.config.hidden_size // model.config.num_attention_heads
    heads_per_kv = model.config.num_attention_heads // n_kv_heads
    kv_idx = head_idx // heads_per_kv
    
    q_start = head_idx * head_dim
    q_end = q_start + head_dim
    kv_start = kv_idx * kv_head_dim
    kv_end = kv_start + kv_head_dim
    
    return {
        "q": attn.q_proj.weight.data[q_start:q_end].cpu().float().numpy(),
        "k": attn.k_proj.weight.data[kv_start:kv_end].cpu().float().numpy(),
        "v": attn.v_proj.weight.data[kv_start:kv_end].cpu().float().numpy(),
        "o": attn.o_proj.weight.data[:, q_start:q_end].cpu().float().numpy(),
    }

def ternary_quantize(w: np.ndarray, sparsity: float = 0.5) -> tuple[np.ndarray, float]:
    """Quantize to {-1, 0, +1} with given sparsity level."""
    abs_w = np.abs(w)
    if sparsity > 0:
        threshold = np.percentile(abs_w.flatten(), sparsity * 100)
    else:
        threshold = 0.0
    scale = float(abs_w[abs_w > threshold].mean()) if np.any(abs_w > threshold) else 1.0
    t = np.zeros_like(w, dtype=np.int8)
    t[w > threshold] = 1
    t[w < -threshold] = -1
    return t, scale

# ══════════════════════════════════════════════════════════════════
# Step 3: Characterize extracted patterns
# ══════════════════════════════════════════════════════════════════

def characterize_pattern(t: np.ndarray) -> dict:
    """Compute structure metrics for a ternary pattern."""
    total = t.size
    n_pos = int(np.sum(t == 1))
    n_neg = int(np.sum(t == -1))
    n_zero = int(np.sum(t == 0))
    return {
        "shape": list(t.shape),
        "sparsity": n_zero / total,
        "balance": n_pos / max(n_neg, 1),
        "density": (n_pos + n_neg) / total,
        "n_pos": n_pos, "n_neg": n_neg, "n_zero": n_zero,
    }

# ══════════════════════════════════════════════════════════════════
# Step 4: Project to target dimensionality
# ══════════════════════════════════════════════════════════════════

def project_patterns(patterns: dict, target_dim: int) -> tuple[dict, np.ndarray]:
    """SVD-project extracted patterns from source_dim to target_dim.
    
    Collects all Q weight rows across all combinators/heads,
    does SVD, keeps top target_dim directions, re-quantizes to ternary.
    Returns projected patterns and the projection matrix.
    """
    # Collect all Q rows (most informative for combinator structure)
    all_rows = []
    for comb in COMBINATOR_NAMES:
        for head_data in patterns.get(comb, []):
            all_rows.append(head_data["weights"]["q"])
    
    if not all_rows:
        return {}, np.array([])
    
    stacked = np.vstack(all_rows)  # (total_rows, source_dim)
    
    # SVD
    U, S, Vt = np.linalg.svd(stacked, full_matrices=False)
    
    # Keep top target_dim directions
    proj = Vt[:target_dim]  # (target_dim, source_dim)
    
    # Project and re-quantize all patterns
    projected = {}
    for comb in COMBINATOR_NAMES:
        projected[comb] = []
        for head_data in patterns.get(comb, []):
            proj_weights = {}
            for wn in ["q", "k", "v", "o"]:
                w = head_data["weights"][wn]  # (head_dim, source_dim) or (source_dim, head_dim)
                if wn == "o":
                    pw = (proj @ w).astype(np.float32)  # (target, head_dim)
                else:
                    pw = (w @ proj.T).astype(np.float32)  # (head_dim, target)
                t, scale = ternary_quantize(pw, sparsity=0.5)
                proj_weights[wn] = {"ternary": t, "scale": scale}
            projected[comb].append({
                "layer": head_data["layer"],
                "head": head_data["head"],
                "score": head_data["score"],
                "projected_weights": proj_weights,
            })
    
    # Ternary-quantize the projection matrix itself
    proj_ternary, proj_scale = ternary_quantize(proj, sparsity=0.3)
    
    return projected, proj_ternary, proj_scale, S[:target_dim]

# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Extract holographic bank")
    parser.add_argument("--model", choices=["gguf", "hf"], default="gguf")
    parser.add_argument("--top-k", type=int, default=5, help="Heads per combinator")
    parser.add_argument("--max-layer", type=int, default=63)
    parser.add_argument("--target-dim", type=int, default=512)
    parser.add_argument("--sparsity", type=float, default=0.5)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  Holographic Bank Extraction", file=sys.stderr)
    print(f"  top-k={args.top_k}, max_layer={args.max_layer}", file=sys.stderr)
    print(f"  target_dim={args.target_dim}, sparsity={args.sparsity}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    # Identify targets
    targets = identify_targets(SELECTIVITY_PATH, args.top_k, args.max_layer)
    unique_layers = set()
    for comb, heads in targets.items():
        print(f"\n  {comb} targets:", file=sys.stderr)
        for h in heads:
            print(f"    L{h['layer']}:H{h['head']} score={h['score']:.3f}", file=sys.stderr)
            unique_layers.add(h['layer'])
    print(f"\n  Unique layers needed: {sorted(unique_layers)}", file=sys.stderr)

    # Load model
    if args.model == "gguf":
        gguf_dir = str(Path(DEFAULT_GGUF).parent)
        gguf_file = Path(DEFAULT_GGUF).name
        print(f"  Loading {DEFAULT_GGUF}...", file=sys.stderr)
        tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
        model = AutoModelForCausalLM.from_pretrained(
            gguf_dir, gguf_file=gguf_file,
            dtype=torch.float16, device_map=args.device,
            trust_remote_code=True)
    else:
        tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
        model = AutoModelForCausalLM.from_pretrained(
            HF_MODEL, dtype=torch.float16, device_map=args.device,
            trust_remote_code=True)
    model.eval()
    
    d_model = model.config.hidden_size
    head_dim = d_model // model.config.num_attention_heads
    print(f"  d_model={d_model}, head_dim={head_dim}, n_kv_heads={model.config.num_key_value_heads}", file=sys.stderr)

    # Extract and quantize
    raw_patterns = {}
    total_params = 0
    
    for comb in COMBINATOR_NAMES:
        raw_patterns[comb] = []
        for h in targets[comb]:
            weights = extract_head_weights(model, h["layer"], h["head"])
            ternary_weights = {}
            chars = {}
            for wn, w in weights.items():
                t, scale = ternary_quantize(w, sparsity=args.sparsity)
                ternary_weights[wn] = t
                chars[wn] = characterize_pattern(t)
                total_params += t.size
            
            raw_patterns[comb].append({
                "layer": h["layer"], "head": h["head"],
                "score": h["score"],
                "weights": {wn: weights[wn] for wn in ["q", "k", "v", "o"]},
                "ternary": ternary_weights,
                "characteristics": chars,
            })
    
    # Print extraction summary
    print(f"\n  ┌─ Extraction Summary ─────────────────────────┐")
    print(f"  │ Total ternary params: {total_params:,}")
    print(f"  │ Storage at 2 bits/param: {total_params * 2 / 8 / 1024:.1f} KB")
    for comb in COMBINATOR_NAMES:
        print(f"  │ {comb}:", end="")
        for hp in raw_patterns[comb]:
            c = hp["characteristics"]["q"]
            print(f" L{hp['layer']}:H{hp['head']}(sp={c['sparsity']:.2f})", end="")
        print()
    print(f"  └──────────────────────────────────────────────┘")

    # Project to target dimensionality
    print(f"\n  Projecting {d_model}→{args.target_dim}...", file=sys.stderr)
    projected, proj_ternary, proj_scale, singular_values = project_patterns(
        raw_patterns, args.target_dim)
    
    # Characterize projection
    sv_ratio = float(singular_values[:args.target_dim].sum() / singular_values.sum()) if len(singular_values) > 0 else 0
    print(f"  SVD variance retained: {sv_ratio:.1%}")
    print(f"  Projection matrix: {proj_ternary.shape}, sparsity={np.mean(proj_ternary==0):.2f}")

    # Save bank
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as npz
    save_dict = {
        "projection_matrix": proj_ternary,
        "projection_scale": np.array([proj_scale]),
        "singular_values": singular_values,
    }
    for comb in COMBINATOR_NAMES:
        for i, hp in enumerate(raw_patterns[comb]):
            for wn in ["q", "k", "v", "o"]:
                save_dict[f"{comb}_{i}_{wn}"] = hp["ternary"][wn]
    
    bank_path = args.output_dir / "bank_qwen3_32b.npz"
    np.savez_compressed(str(bank_path), **save_dict)
    
    # Save metadata
    meta = {
        "source": "Qwen3-32B",
        "source_license": "Apache-2.0",
        "extraction_timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "source_dim": d_model,
        "target_dim": args.target_dim,
        "head_dim": head_dim,
        "sparsity": args.sparsity,
        "top_k": args.top_k,
        "total_ternary_params": total_params,
        "storage_bytes": total_params * 2 // 8,
        "sv_variance_retained": sv_ratio,
        "targets": {c: [{"layer": h["layer"], "head": h["head"], 
                         "score": h["score"]} for h in targets[c]] 
                   for c in COMBINATOR_NAMES},
        "characteristics": {c: [hp["characteristics"] for hp in raw_patterns[c]]
                           for c in COMBINATOR_NAMES},
    }
    meta_path = args.output_dir / "bank_meta.json"
    meta_path.write_text(json.dumps(meta, indent=2))
    
    bank_size = bank_path.stat().st_size
    print(f"\n  💾 Bank: {bank_path} ({bank_size/1024:.1f} KB)")
    print(f"  💾 Meta: {meta_path}")
    print(f"\n  Compression: 32B model → {bank_size/1024:.1f} KB bank")

if __name__ == "__main__":
    main()
