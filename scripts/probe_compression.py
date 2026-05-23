#!/usr/bin/env python3
"""Probe per-layer compression ratios in flat-attention models.

Hypothesis: if phi (1/φ ≈ 0.618) is the universal language compression
ratio, flat-attention models should show it per-layer — not just
stride-stack models.

Measures per-layer:
  1. Effective rank ratio: rank(layer_out) / d_model
     (how many dimensions carry information after each layer)
  2. Layer-to-layer cosine similarity: cos(h_{l}, h_{l-1})
     (how much does each layer change the representation)
  3. Entropy compression: H(layer_out) / H(layer_in)
     (information-theoretic compression per layer)
  4. Singular value concentration: σ₁/Σσ
     (how concentrated is the information in top components)

For each metric, compare to 1/φ ≈ 0.618.

Usage:
    uv run python scripts/probe_compression.py --model pythia-160m
    uv run python scripts/probe_compression.py --model qwen3-0.6b
    uv run python scripts/probe_compression.py --model pythia-1.4b
    uv run python scripts/probe_compression.py --model all
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

PHI = (1 + np.sqrt(5)) / 2
INV_PHI = 1 / PHI  # 0.6180339887...

# ══════════════════════════════════════════════════════════════════════
# Model registry
# ══════════════════════════════════════════════════════════════════════

MODELS = {
    "pythia-160m": "EleutherAI/pythia-160m-deduped",
    "pythia-410m": "EleutherAI/pythia-410m-deduped",
    "pythia-1.4b": "EleutherAI/pythia-1.4b-deduped",
    "qwen3-0.6b": "Qwen/Qwen3-0.6B",
    "smollm3-3b": "HuggingFaceTB/SmolLM3-3B",
}

# ══════════════════════════════════════════════════════════════════════
# Sample texts (same strata as V6 probe for comparability)
# ══════════════════════════════════════════════════════════════════════

SAMPLES = [
    # Prose
    "The cat sat on the mat and looked out the window at the birds flying south for the winter.",
    "In a quiet village nestled between rolling hills, the old baker opened his shop at dawn.",
    "Every student who passed the final exam received a certificate of achievement from the dean.",
    # Compositional
    "The man who the dog that the cat chased bit ran away quickly.",
    "If every student reads a book then some teacher who knows the author is happy.",
    # Technical
    "The gradient of the loss with respect to the weights is computed via backpropagation.",
    "Attention scores are computed as the softmax of the scaled dot product of queries and keys.",
    # Math
    "For all x in R, x squared is greater than or equal to zero, with equality if and only if x equals zero.",
    "The probability of A given B equals the probability of B given A times P of A divided by P of B.",
]


# ══════════════════════════════════════════════════════════════════════
# Compression metrics
# ══════════════════════════════════════════════════════════════════════

def effective_rank(H: np.ndarray) -> float:
    """Effective rank via Shannon entropy of normalized singular values.
    
    Roy & Vetterli (2007): exp(H(σ/Σσ)) where H is Shannon entropy.
    Returns ratio to d_model (0-1 range).
    """
    # H shape: (seq_len, d_model)
    s = np.linalg.svd(H.astype(np.float32), compute_uv=False)
    s = s[s > 1e-10]  # remove near-zero
    p = s / s.sum()
    entropy = -np.sum(p * np.log(p))
    erank = np.exp(entropy)
    return float(erank / H.shape[1])  # normalize by d_model


def sv_concentration(H: np.ndarray) -> float:
    """Top singular value / sum of all singular values.
    
    High = information concentrated in one direction.
    Low = information spread across dimensions.
    """
    s = np.linalg.svd(H.astype(np.float32), compute_uv=False)
    return float(s[0] / (s.sum() + 1e-10))


def layer_cosine_sim(H_prev: np.ndarray, H_curr: np.ndarray) -> float:
    """Mean cosine similarity between consecutive layer outputs.
    
    Measures how much each layer changes the representation.
    High = small change (layer refines). Low = big change (layer transforms).
    """
    # Normalize per-token
    H_prev_norm = H_prev / (np.linalg.norm(H_prev, axis=-1, keepdims=True) + 1e-10)
    H_curr_norm = H_curr / (np.linalg.norm(H_curr, axis=-1, keepdims=True) + 1e-10)
    # Per-token cosine similarity, then mean
    cos_sim = np.sum(H_prev_norm * H_curr_norm, axis=-1)
    return float(np.mean(cos_sim))


def representation_entropy(H: np.ndarray) -> float:
    """Entropy of the representation via SVD.
    
    Higher = more information spread across dimensions.
    Lower = more compressed/structured.
    """
    s = np.linalg.svd(H.astype(np.float32), compute_uv=False)
    s = s[s > 1e-10]
    p = s / s.sum()
    return float(-np.sum(p * np.log2(p)))


def compression_ratio(H_prev: np.ndarray, H_curr: np.ndarray) -> float:
    """Ratio of effective rank: rank(curr) / rank(prev).
    
    < 1 = compression (layer reduced effective dimensionality)
    > 1 = expansion (layer increased effective dimensionality)
    ≈ 0.618 = phi compression (the hypothesis)
    """
    r_prev = effective_rank(H_prev)
    r_curr = effective_rank(H_curr)
    if r_prev < 1e-10:
        return 1.0
    return r_curr / r_prev


# ══════════════════════════════════════════════════════════════════════
# Probe runner
# ══════════════════════════════════════════════════════════════════════

def probe_model(model_key: str) -> dict:
    """Run compression probes on a model."""
    model_name = MODELS[model_key]
    print(f"\n{'='*60}")
    print(f"Probing: {model_key} ({model_name})")
    print(f"{'='*60}")
    
    print("Loading model...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, 
        trust_remote_code=True,
        torch_dtype=torch.float32,
        device_map="cpu",
    )
    model.eval()
    
    n_layers = model.config.num_hidden_layers
    d_model = model.config.hidden_size
    print(f"  Layers: {n_layers}, d_model: {d_model}")
    
    # Collect per-layer hidden states across all samples
    all_hidden_states = []  # list of (n_layers+1, seq_len, d_model)
    
    for i, text in enumerate(SAMPLES):
        inputs = tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs, output_hidden_states=True)
        
        # hidden_states: tuple of (1, seq_len, d_model) per layer (including embedding)
        hs = [h[0].numpy() for h in outputs.hidden_states]
        all_hidden_states.append(hs)
        print(f"  Sample {i}: {len(inputs.input_ids[0])} tokens")
    
    # Concatenate all samples along sequence dimension for each layer
    n_total_layers = len(all_hidden_states[0])  # n_layers + 1 (embedding)
    concat_hs = []
    for layer_idx in range(n_total_layers):
        layer_tokens = np.concatenate(
            [hs[layer_idx] for hs in all_hidden_states], axis=0
        )
        concat_hs.append(layer_tokens)
    
    print(f"  Total tokens: {concat_hs[0].shape[0]}")
    print(f"  Layers (including embedding): {n_total_layers}")
    
    # ── Compute metrics per layer ─────────────────────────────
    results = {
        "model": model_key,
        "model_name": model_name,
        "n_layers": n_layers,
        "d_model": d_model,
        "inv_phi": INV_PHI,
        "layers": [],
    }
    
    print(f"\n  {'Layer':>6} {'EffRank':>8} {'Compress':>9} {'CosSim':>8} {'SVConc':>8} {'Entropy':>8} {'φ-dev':>7}")
    print(f"  {'-'*6} {'-'*8} {'-'*9} {'-'*8} {'-'*8} {'-'*8} {'-'*7}")
    
    for l in range(n_total_layers):
        H = concat_hs[l]
        
        layer_data = {
            "layer": l,
            "effective_rank": effective_rank(H),
            "sv_concentration": sv_concentration(H),
            "entropy": representation_entropy(H),
        }
        
        if l > 0:
            H_prev = concat_hs[l - 1]
            cr = compression_ratio(H_prev, H)
            cs = layer_cosine_sim(H_prev, H)
            layer_data["compression_ratio"] = cr
            layer_data["cosine_sim_prev"] = cs
            layer_data["phi_dev_compression"] = abs(cr - INV_PHI)
            
            phi_dev = layer_data["phi_dev_compression"]
            phi_marker = " ← φ!" if phi_dev < 0.05 else (" ~ φ" if phi_dev < 0.10 else "")
            
            print(f"  {l:>6} {layer_data['effective_rank']:>8.4f} {cr:>9.4f} "
                  f"{cs:>8.4f} {layer_data['sv_concentration']:>8.4f} "
                  f"{layer_data['entropy']:>8.2f} {phi_dev:>7.4f}{phi_marker}")
        else:
            print(f"  {'emb':>6} {layer_data['effective_rank']:>8.4f} {'---':>9} "
                  f"{'---':>8} {layer_data['sv_concentration']:>8.4f} "
                  f"{layer_data['entropy']:>8.2f}    ---")
        
        results["layers"].append(layer_data)
    
    # ── Summary statistics ────────────────────────────────────
    compress_ratios = [l["compression_ratio"] for l in results["layers"] if "compression_ratio" in l]
    phi_devs = [l["phi_dev_compression"] for l in results["layers"] if "phi_dev_compression" in l]
    
    results["summary"] = {
        "mean_compression": float(np.mean(compress_ratios)),
        "std_compression": float(np.std(compress_ratios)),
        "median_compression": float(np.median(compress_ratios)),
        "mean_phi_dev": float(np.mean(phi_devs)),
        "min_phi_dev": float(np.min(phi_devs)),
        "layers_within_0.05_of_phi": sum(1 for d in phi_devs if d < 0.05),
        "layers_within_0.10_of_phi": sum(1 for d in phi_devs if d < 0.10),
        "best_phi_layer": int(np.argmin(phi_devs)) + 1,  # +1 for embedding offset
    }
    
    s = results["summary"]
    print(f"\n  Summary:")
    print(f"    Mean compression ratio:  {s['mean_compression']:.4f}  (φ = {INV_PHI:.4f})")
    print(f"    Median compression:      {s['median_compression']:.4f}")
    print(f"    Std:                     {s['std_compression']:.4f}")
    print(f"    Mean φ-deviation:        {s['mean_phi_dev']:.4f}")
    print(f"    Best φ layer:            {s['best_phi_layer']} (dev={s['min_phi_dev']:.4f})")
    print(f"    Layers within 0.05 of φ: {s['layers_within_0.05_of_phi']}/{n_layers}")
    print(f"    Layers within 0.10 of φ: {s['layers_within_0.10_of_phi']}/{n_layers}")
    
    # Cleanup
    del model
    del tokenizer
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    
    return results


# ══════════════════════════════════════════════════════════════════════
# Cross-model comparison
# ══════════════════════════════════════════════════════════════════════

def compare_models(all_results: list[dict]):
    """Print cross-model comparison table."""
    print(f"\n{'='*70}")
    print(f"CROSS-MODEL COMPRESSION COMPARISON")
    print(f"{'='*70}")
    print(f"1/φ = {INV_PHI:.6f}")
    print()
    
    print(f"{'Model':>15} {'Layers':>6} {'Mean':>8} {'Median':>8} "
          f"{'φ-dev':>7} {'Best':>5} {'<0.05':>6} {'<0.10':>6}")
    print(f"{'-'*15} {'-'*6} {'-'*8} {'-'*8} {'-'*7} {'-'*5} {'-'*6} {'-'*6}")
    
    for r in all_results:
        s = r["summary"]
        print(f"{r['model']:>15} {r['n_layers']:>6} "
              f"{s['mean_compression']:>8.4f} {s['median_compression']:>8.4f} "
              f"{s['mean_phi_dev']:>7.4f} L{s['best_phi_layer']:>3} "
              f"{s['layers_within_0.05_of_phi']:>5}/{r['n_layers']} "
              f"{s['layers_within_0.10_of_phi']:>5}/{r['n_layers']}")
    
    # Check for consensus
    print(f"\n  Consensus check (mean compression across models):")
    means = [r["summary"]["mean_compression"] for r in all_results]
    print(f"    Range: {min(means):.4f} — {max(means):.4f}")
    print(f"    Mean:  {np.mean(means):.4f}")
    print(f"    Std:   {np.std(means):.4f}")
    print(f"    φ = {INV_PHI:.4f}")
    
    if abs(np.mean(means) - INV_PHI) < 0.10:
        print(f"    ⚡ SIGNAL: cross-model mean is within 0.10 of φ!")
    if abs(np.mean(means) - INV_PHI) < 0.05:
        print(f"    ⚡⚡ STRONG SIGNAL: cross-model mean is within 0.05 of φ!")


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Probe per-layer compression in flat-attention models")
    parser.add_argument("--model", type=str, default="all",
                        choices=list(MODELS.keys()) + ["all", "small"],
                        help="Which model(s) to probe")
    parser.add_argument("--output", type=str, default=None,
                        help="Save results to JSON file")
    args = parser.parse_args()
    
    if args.model == "all":
        model_keys = list(MODELS.keys())
    elif args.model == "small":
        model_keys = ["pythia-160m", "pythia-410m", "qwen3-0.6b"]
    else:
        model_keys = [args.model]
    
    all_results = []
    for mk in model_keys:
        try:
            r = probe_model(mk)
            all_results.append(r)
        except Exception as e:
            print(f"\n  ERROR probing {mk}: {e}")
            import traceback
            traceback.print_exc()
    
    if len(all_results) > 1:
        compare_models(all_results)
    
    if args.output:
        # Convert numpy types for JSON serialization
        def convert(obj):
            if isinstance(obj, (np.floating, np.integer)):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj
        
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(all_results, f, indent=2, default=convert)
        print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
