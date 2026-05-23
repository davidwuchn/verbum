#!/usr/bin/env python3
"""Output Beamformer Probe — What are the 329 neurons that fire at L63?

The FFN indexing probe (session 141) found that the final layer (L63)
of Qwen3-32B has only 329 active neurons out of 25,600 (1.3%). These
are the OUTPUT BEAMFORMERS — the final lens that focuses the holographic
beam onto the token cloud for prediction.

This probe investigates:

  1. IDENTITY — Which neuron indices fire? Are they STABLE across prompts
     (permanent beamformers) or DYNAMIC (prompt-selected)?

  2. GATE vs UP — Is the sparsity from silu(gate_proj) killing neurons
     (gate-driven) or from up_proj key-match being near-zero (key-driven)?
     Gate-driven = addressing is in the gate weights.
     Key-driven = addressing is in the key-match weights.

  3. DOWN_PROJ → TOKEN CLOUD — Each active neuron's down_proj column is
     its contribution to the residual stream. Map to the embedding space:
     which vocabulary regions does each output beamformer point at?

  4. CATEGORY PROFILE — Per-neuron activation across 8 semantic categories.
     Do specific output beamformers specialize for specific categories?

  5. MULTI-LAYER CHECK — Are other layers also ultra-sparse? Check L0,
     L62 (penultimate), L60, L58 to see where ultra-sparsity begins.

  6. ACTIVATION MAGNITUDE SPECTRUM — Within the 329, what's the magnitude
     distribution? Are there a few dominant neurons and a long tail?

Architecture: Qwen3-32B — 64 layers, d_model=5120, d_ffn=25600.

Usage:
    uv run python scripts/explore/probe_output_beamformers.py
    uv run python scripts/explore/probe_output_beamformers.py --device cuda

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import torch

MODEL = "Qwen/Qwen3-32B"
RESULTS_DIR = Path("results/output-beamformers-qwen3-32b")

# Same categories as the indexing probe
CATEGORIZED_PROMPTS = {
    "factual_geography": [
        "The capital of France is",
        "The capital of Japan is",
        "The capital of Germany is",
        "The largest ocean is the",
        "The longest river in Africa is the",
        "Mount Everest is located in",
    ],
    "factual_science": [
        "Water boils at a temperature of",
        "The speed of light is approximately",
        "DNA stands for deoxyribonucleic",
        "The chemical formula for water is",
        "Photosynthesis converts sunlight into",
        "The atomic number of carbon is",
    ],
    "arithmetic": [
        "2 + 3 =",
        "7 * 8 =",
        "100 / 4 =",
        "15 - 9 =",
        "The square root of 144 is",
        "3 to the power of 4 is",
    ],
    "code": [
        "def fibonacci(n):",
        "for i in range(10):",
        "import numpy as np",
        "class Node:",
        "if __name__ == '__main__':",
        "return sorted(items, key=lambda x:",
    ],
    "reasoning": [
        "If all cats are mammals, and all mammals breathe, then all cats",
        "The train leaves at 3pm and arrives at 5pm, so the journey takes",
        "If A is taller than B, and B is taller than C, then A is",
        "Given that it is raining, the ground is",
        "Since every prime greater than 2 is odd, the number 17 is",
        "If the hypothesis is true, then we would expect to observe",
    ],
    "instruction": [
        "Please write a summary of the following text:",
        "Translate the following sentence into French:",
        "List the main advantages of renewable energy:",
        "Explain the concept of machine learning in simple terms:",
        "Compare and contrast the following two approaches:",
        "Describe step by step how to solve this problem:",
    ],
    "lambda_compile": [
        "The dog chases the cat",
        "Every student read some book",
        "Alice believes Bob saw Carol",
        "The teacher who wrote the book left",
        "No politician that every voter trusts exists",
        "Most students that attended the lecture passed",
    ],
    "narrative": [
        "Once upon a time, in a land far away,",
        "She opened the door and stepped into the",
        "The detective examined the evidence carefully before",
        "As the sun set over the mountains,",
        "He had always known that this day would",
        "The letter arrived on a Tuesday morning,",
    ],
}


def banner(msg: str) -> None:
    print(f"\n{'=' * 72}\n  {msg}\n{'=' * 72}\n", file=sys.stderr, flush=True)


def load_model(model_name: str, device: str = "mps"):
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

    banner(f"Loading {model_name}")
    t0 = time.time()

    config = AutoConfig.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map=device,
        attn_implementation="eager",
    )
    model.eval()

    dt = time.time() - t0
    print(f"  Loaded in {dt:.1f}s", file=sys.stderr)
    print(
        f"  Layers: {config.num_hidden_layers}  d_model: {config.hidden_size}  "
        f"d_ffn: {config.intermediate_size}",
        file=sys.stderr,
        flush=True,
    )
    return model, tokenizer, config


def get_transformer_layers(model):
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    raise ValueError(f"Cannot find transformer layers in {type(model).__name__}")


# ══════════════════════════════════════════════════════════════════════
# Capture detailed FFN internals for specific layers
# ══════════════════════════════════════════════════════════════════════

def capture_ffn_detailed(
    model,
    tokenizer,
    text: str,
    layer_indices: list[int],
    device: str = "mps",
) -> dict:
    """Capture gate_proj, up_proj, and mlp output separately for decomposition."""
    layers = get_transformer_layers(model)
    results = {}
    hooks = []

    for li in layer_indices:
        layer = layers[li]
        results[li] = {}

        def make_hook(layer_idx, name):
            def hook_fn(module, args, output):
                results[layer_idx][name] = output.detach().float().cpu().numpy()
            return hook_fn

        hooks.append(layer.mlp.gate_proj.register_forward_hook(make_hook(li, 'gate_raw')))
        hooks.append(layer.mlp.up_proj.register_forward_hook(make_hook(li, 'up_raw')))
        hooks.append(layer.mlp.register_forward_hook(make_hook(li, 'ffn_delta')))
        hooks.append(layer.post_attention_layernorm.register_forward_hook(
            make_hook(li, 'residual_in')
        ))

    inputs = tokenizer(text, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs)

    for h in hooks:
        h.remove()

    # Compute derived quantities
    for li in layer_indices:
        r = results[li]
        gate_raw = r['gate_raw']  # [1, seq_len, d_ffn]
        up_raw = r['up_raw']      # [1, seq_len, d_ffn]
        gate_activated = 1.0 / (1.0 + np.exp(-gate_raw.astype(np.float64))) * gate_raw  # silu
        r['gate_up'] = gate_activated * up_raw  # post-SwiGLU

    return results


# ══════════════════════════════════════════════════════════════════════
# Analysis 1: IDENTITY — Which neurons fire, and are they stable?
# ══════════════════════════════════════════════════════════════════════

def analyze_identity(all_captures: dict, final_layer: int, threshold_frac: float = 0.01) -> dict:
    """Identify which neurons fire at the final layer across all prompts.

    For each prompt, find active neurons (|gate_up| > threshold_frac * max).
    Measure: how many are shared across ALL prompts vs prompt-specific?
    """
    banner("Analysis 1: Output Beamformer Identity")

    # Collect active neuron sets per prompt
    active_sets = {}
    active_magnitudes = {}

    for key, captures in all_captures.items():
        gate_up = captures[final_layer]['gate_up']
        acts = gate_up[0, -1, :]  # last token [d_ffn]
        thresh = threshold_frac * np.abs(acts).max()
        active = set(np.where(np.abs(acts) > thresh)[0].tolist())
        active_sets[key] = active
        active_magnitudes[key] = {int(i): float(acts[i]) for i in active}

    # Core set (active in ALL prompts)
    all_keys = list(active_sets.keys())
    core = active_sets[all_keys[0]].copy()
    for key in all_keys[1:]:
        core &= active_sets[key]

    # Union set (active in ANY prompt)
    union = set()
    for key in all_keys:
        union |= active_sets[key]

    # Frequency: how many prompts each neuron appears in
    neuron_freq = Counter()
    for key in all_keys:
        for n in active_sets[key]:
            neuron_freq[n] += 1

    n_prompts = len(all_keys)

    # Stability tiers
    always_on = {n for n, c in neuron_freq.items() if c == n_prompts}
    frequent = {n for n, c in neuron_freq.items() if c >= n_prompts * 0.75}
    occasional = {n for n, c in neuron_freq.items() if c >= n_prompts * 0.25 and c < n_prompts * 0.75}
    rare = {n for n, c in neuron_freq.items() if c < n_prompts * 0.25}

    # Per-prompt active count statistics
    counts = [len(s) for s in active_sets.values()]

    results = {
        "n_prompts": n_prompts,
        "mean_active_per_prompt": float(np.mean(counts)),
        "std_active_per_prompt": float(np.std(counts)),
        "min_active": int(min(counts)),
        "max_active": int(max(counts)),
        "core_size": len(core),
        "union_size": len(union),
        "always_on": len(always_on),
        "frequent_75pct": len(frequent),
        "occasional_25_75pct": len(occasional),
        "rare_lt25pct": len(rare),
        "core_neuron_indices": sorted(core)[:50],  # first 50 for reference
        "stability_ratio": len(always_on) / len(union) if union else 0,
        "jaccard_all_pairs_mean": 0.0,
    }

    # Pairwise Jaccard to measure consistency
    jaccards = []
    keys_list = list(active_sets.keys())
    for i in range(min(len(keys_list), 48)):
        for j in range(i + 1, min(len(keys_list), 48)):
            si, sj = active_sets[keys_list[i]], active_sets[keys_list[j]]
            inter = len(si & sj)
            union_ij = len(si | sj)
            if union_ij > 0:
                jaccards.append(inter / union_ij)
    results["jaccard_all_pairs_mean"] = float(np.mean(jaccards)) if jaccards else 0

    print(f"  Active per prompt: {results['mean_active_per_prompt']:.0f} ± {results['std_active_per_prompt']:.0f}",
          file=sys.stderr)
    print(f"  Core (in ALL prompts): {results['core_size']}", file=sys.stderr)
    print(f"  Union (in ANY prompt): {results['union_size']}", file=sys.stderr)
    print(f"  Always-on: {results['always_on']}  Frequent: {results['frequent_75pct']}  "
          f"Occasional: {results['occasional_25_75pct']}  Rare: {results['rare_lt25pct']}",
          file=sys.stderr)
    print(f"  Stability ratio (always/union): {results['stability_ratio']:.3f}", file=sys.stderr)
    print(f"  Pairwise Jaccard: {results['jaccard_all_pairs_mean']:.4f}", file=sys.stderr, flush=True)

    return results, neuron_freq, active_sets


# ══════════════════════════════════════════════════════════════════════
# Analysis 2: GATE vs UP — Where does the sparsity come from?
# ══════════════════════════════════════════════════════════════════════

def analyze_gate_vs_up(all_captures: dict, final_layer: int) -> dict:
    """Decompose: is sparsity from silu(gate) killing neurons or up_proj being near-zero?

    For each neuron at the last token:
      - |up_raw|: the key-match magnitude (before gating)
      - |silu(gate)|: the gate activation magnitude
      - |gate_up|: the product (what actually fires)

    If gate kills it: up_raw is large but silu(gate) ≈ 0
    If key kills it: up_raw ≈ 0 regardless of gate
    """
    banner("Analysis 2: Gate vs UP Decomposition")

    # Aggregate over all prompts
    all_gate_magnitudes = []
    all_up_magnitudes = []
    all_product_magnitudes = []

    for key, captures in all_captures.items():
        gate_raw = captures[final_layer]['gate_raw'][0, -1, :]  # [d_ffn]
        up_raw = captures[final_layer]['up_raw'][0, -1, :]
        gate_up = captures[final_layer]['gate_up'][0, -1, :]

        silu_gate = 1.0 / (1.0 + np.exp(-gate_raw.astype(np.float64))) * gate_raw
        all_gate_magnitudes.append(np.abs(silu_gate))
        all_up_magnitudes.append(np.abs(up_raw))
        all_product_magnitudes.append(np.abs(gate_up))

    # Mean across prompts: [d_ffn]
    mean_gate = np.mean(all_gate_magnitudes, axis=0)
    mean_up = np.mean(all_up_magnitudes, axis=0)
    mean_product = np.mean(all_product_magnitudes, axis=0)

    d_ffn = len(mean_gate)

    # Classify each neuron by what kills it
    product_thresh = 0.01 * mean_product.max()
    active_mask = mean_product > product_thresh
    n_active = int(np.sum(active_mask))
    n_inactive = d_ffn - n_active

    # For inactive neurons: is gate or up the bottleneck?
    inactive_idx = np.where(~active_mask)[0]
    gate_small = mean_gate[inactive_idx] < 0.01 * mean_gate.max()
    up_small = mean_up[inactive_idx] < 0.01 * mean_up.max()
    both_small = gate_small & up_small
    gate_only = gate_small & ~up_small  # gate kills it, up is fine
    up_only = ~gate_small & up_small    # up kills it, gate is fine
    neither = ~gate_small & ~up_small   # both moderate but product is small (cancellation)

    results = {
        "d_ffn": d_ffn,
        "n_active": n_active,
        "n_inactive": n_inactive,
        "inactive_breakdown": {
            "gate_kills": int(np.sum(gate_only)),
            "up_kills": int(np.sum(up_only)),
            "both_kill": int(np.sum(both_small)),
            "neither_dominant": int(np.sum(neither)),
        },
        "pct_gate_kills": float(np.sum(gate_only) / max(n_inactive, 1) * 100),
        "pct_up_kills": float(np.sum(up_only) / max(n_inactive, 1) * 100),
        "pct_both_kill": float(np.sum(both_small) / max(n_inactive, 1) * 100),
        "pct_neither": float(np.sum(neither) / max(n_inactive, 1) * 100),
        # For active neurons: what's the gate/up balance?
        "active_mean_gate": float(mean_gate[active_mask].mean()),
        "active_mean_up": float(mean_up[active_mask].mean()),
        "active_gate_up_ratio": float(mean_gate[active_mask].mean() / max(mean_up[active_mask].mean(), 1e-10)),
        # Overall magnitude profiles
        "gate_magnitude_percentiles": {
            "p10": float(np.percentile(mean_gate, 10)),
            "p50": float(np.percentile(mean_gate, 50)),
            "p90": float(np.percentile(mean_gate, 90)),
            "p99": float(np.percentile(mean_gate, 99)),
            "max": float(mean_gate.max()),
        },
        "up_magnitude_percentiles": {
            "p10": float(np.percentile(mean_up, 10)),
            "p50": float(np.percentile(mean_up, 50)),
            "p90": float(np.percentile(mean_up, 90)),
            "p99": float(np.percentile(mean_up, 99)),
            "max": float(mean_up.max()),
        },
    }

    print(f"  Active: {n_active}  Inactive: {n_inactive}", file=sys.stderr)
    print(f"  Inactive breakdown:", file=sys.stderr)
    print(f"    Gate kills (gate≈0, up≠0): {results['inactive_breakdown']['gate_kills']} "
          f"({results['pct_gate_kills']:.1f}%)", file=sys.stderr)
    print(f"    UP kills (up≈0, gate≠0):   {results['inactive_breakdown']['up_kills']} "
          f"({results['pct_up_kills']:.1f}%)", file=sys.stderr)
    print(f"    Both kill:                  {results['inactive_breakdown']['both_kill']} "
          f"({results['pct_both_kill']:.1f}%)", file=sys.stderr)
    print(f"    Neither dominant:           {results['inactive_breakdown']['neither_dominant']} "
          f"({results['pct_neither']:.1f}%)", file=sys.stderr)
    print(f"  Active neurons: gate/up ratio = {results['active_gate_up_ratio']:.3f}", file=sys.stderr, flush=True)

    return results


# ══════════════════════════════════════════════════════════════════════
# Analysis 3: DOWN_PROJ → TOKEN CLOUD — Where do beamformers point?
# ══════════════════════════════════════════════════════════════════════

def analyze_token_cloud_mapping(
    model, tokenizer, neuron_freq: Counter, final_layer: int, top_n: int = 50
) -> dict:
    """Map the most frequent output beamformer neurons to vocabulary regions.

    Each neuron's down_proj column is its contribution direction. Project
    onto the embedding space to find which tokens it points toward.
    """
    banner("Analysis 3: Down_proj → Token Cloud Mapping")

    layers = get_transformer_layers(model)
    layer = layers[final_layer]

    # Get down_proj weights: [d_model, d_ffn] — each COLUMN is one neuron's output direction
    down_proj_weight = layer.mlp.down_proj.weight.detach().float().cpu()  # [d_model, d_ffn]

    # Get embedding matrix for token cloud
    if hasattr(model, "model") and hasattr(model.model, "embed_tokens"):
        embed_weight = model.model.embed_tokens.weight.detach().float().cpu()  # [vocab, d_model]
    else:
        raise ValueError("Cannot find embedding weights")

    # Normalize embeddings for cosine similarity
    embed_norms = embed_weight.norm(dim=1, keepdim=True).clamp(min=1e-10)
    embed_normed = embed_weight / embed_norms

    # Top-N most frequent neurons
    top_neurons = [n for n, _ in neuron_freq.most_common(top_n)]

    results = {"n_neurons_analyzed": len(top_neurons), "neurons": {}}

    for neuron_idx in top_neurons:
        # This neuron's output direction: column of down_proj
        direction = down_proj_weight[:, neuron_idx]  # [d_model]
        dir_norm = direction.norm().clamp(min=1e-10)
        dir_normed = direction / dir_norm

        # Cosine similarity to all tokens
        cos_sims = (embed_normed @ dir_normed).numpy()  # [vocab]

        # Top-10 most aligned tokens
        top_k = 10
        top_indices = np.argsort(cos_sims)[-top_k:][::-1]
        bottom_indices = np.argsort(cos_sims)[:top_k]

        top_tokens = []
        for idx in top_indices:
            token_str = tokenizer.decode([int(idx)])
            top_tokens.append({
                "token_id": int(idx),
                "token": token_str,
                "cosine": float(cos_sims[idx]),
            })

        bottom_tokens = []
        for idx in bottom_indices:
            token_str = tokenizer.decode([int(idx)])
            bottom_tokens.append({
                "token_id": int(idx),
                "token": token_str,
                "cosine": float(cos_sims[idx]),
            })

        results["neurons"][str(neuron_idx)] = {
            "frequency": int(neuron_freq[neuron_idx]),
            "direction_norm": float(dir_norm),
            "top_aligned_tokens": top_tokens,
            "bottom_aligned_tokens": bottom_tokens,
            "cos_sim_mean": float(cos_sims.mean()),
            "cos_sim_std": float(cos_sims.std()),
            "cos_sim_max": float(cos_sims.max()),
            "cos_sim_min": float(cos_sims.min()),
        }

    # Summary: are the output beamformers pointing at diverse or concentrated regions?
    all_top_token_ids = set()
    for ndata in results["neurons"].values():
        for t in ndata["top_aligned_tokens"][:3]:
            all_top_token_ids.add(t["token_id"])

    results["summary"] = {
        "unique_top3_tokens_across_neurons": len(all_top_token_ids),
        "concentration_ratio": float(len(all_top_token_ids) / (3 * len(top_neurons))),
    }

    # Print top-5 neurons with their top tokens
    for i, neuron_idx in enumerate(top_neurons[:10]):
        ndata = results["neurons"][str(neuron_idx)]
        tokens = [t["token"] for t in ndata["top_aligned_tokens"][:5]]
        freq = ndata["frequency"]
        n_total = sum(1 for _ in neuron_freq.values())  # total unique neurons seen
        print(f"  Neuron {neuron_idx:5d} (freq={freq:2d}): "
              f"{' | '.join(repr(t) for t in tokens)}",
              file=sys.stderr)

    print(f"\n  Unique top-3 tokens: {results['summary']['unique_top3_tokens_across_neurons']} "
          f"across {len(top_neurons)} neurons "
          f"(concentration={results['summary']['concentration_ratio']:.3f})",
          file=sys.stderr, flush=True)

    return results


# ══════════════════════════════════════════════════════════════════════
# Analysis 4: CATEGORY PROFILE — Per-neuron category specialization
# ══════════════════════════════════════════════════════════════════════

def analyze_category_profile(
    all_captures: dict, neuron_freq: Counter, final_layer: int, top_n: int = 100
) -> dict:
    """For each frequent output beamformer neuron, measure per-category activation."""
    banner("Analysis 4: Per-Neuron Category Profile")

    categories = list(CATEGORIZED_PROMPTS.keys())
    top_neurons = [n for n, _ in neuron_freq.most_common(top_n)]

    # Build neuron × category activation matrix
    cat_activations = {n: {cat: [] for cat in categories} for n in top_neurons}

    for key, captures in all_captures.items():
        cat = key.rsplit("_", 1)[0]
        # Reconstruct category name (handle multi-word categories)
        for c in categories:
            prefix = c + "_"
            if key.startswith(prefix):
                cat = c
                break

        gate_up = captures[final_layer]['gate_up'][0, -1, :]

        for n in top_neurons:
            cat_activations[n][cat].append(float(gate_up[n]))

    # Compute per-neuron statistics
    results = {"n_neurons": len(top_neurons), "neurons": {}}

    specialist_count = 0
    generalist_count = 0

    for n in top_neurons:
        cat_means = {}
        for cat in categories:
            vals = cat_activations[n][cat]
            cat_means[cat] = float(np.mean(np.abs(vals))) if vals else 0

        # Entropy of category distribution
        total = sum(cat_means.values())
        if total > 0:
            probs = [v / total for v in cat_means.values()]
            entropy = -sum(p * np.log2(max(p, 1e-10)) for p in probs)
        else:
            entropy = 0

        max_entropy = np.log2(len(categories))
        norm_entropy = entropy / max_entropy if max_entropy > 0 else 0

        # Dominant category
        dominant = max(cat_means, key=cat_means.get)
        dominance_ratio = cat_means[dominant] / max(total / len(categories), 1e-10)

        is_specialist = norm_entropy < 0.7
        if is_specialist:
            specialist_count += 1
        else:
            generalist_count += 1

        results["neurons"][str(n)] = {
            "frequency": int(neuron_freq[n]),
            "category_mean_activation": cat_means,
            "normalized_entropy": float(norm_entropy),
            "dominant_category": dominant,
            "dominance_ratio": float(dominance_ratio),
            "is_specialist": bool(is_specialist),
        }

    results["summary"] = {
        "specialists": specialist_count,
        "generalists": generalist_count,
        "pct_specialist": float(specialist_count / max(len(top_neurons), 1) * 100),
    }

    # Print top-10 most specialized
    by_entropy = sorted(results["neurons"].items(), key=lambda x: x[1]["normalized_entropy"])
    print(f"\n  Most specialized neurons (low entropy):", file=sys.stderr)
    for nid, ndata in by_entropy[:10]:
        print(f"    Neuron {nid:>5s}: entropy={ndata['normalized_entropy']:.3f}  "
              f"dominant={ndata['dominant_category']}  "
              f"ratio={ndata['dominance_ratio']:.2f}x",
              file=sys.stderr)

    print(f"\n  Specialists: {specialist_count}/{len(top_neurons)} "
          f"({results['summary']['pct_specialist']:.1f}%)",
          file=sys.stderr, flush=True)

    return results


# ══════════════════════════════════════════════════════════════════════
# Analysis 5: MULTI-LAYER — Where does ultra-sparsity begin?
# ══════════════════════════════════════════════════════════════════════

def analyze_sparsity_gradient(
    model, tokenizer, all_captures: dict, device: str, config
) -> dict:
    """Check sparsity at layers near the end to find where ultra-sparsity begins."""
    banner("Analysis 5: Sparsity Gradient (Where Ultra-Sparsity Begins)")

    check_layers = [58, 60, 61, 62, 63]
    n_layers = config.num_hidden_layers
    check_layers = [l for l in check_layers if l < n_layers]

    # We already have L63 from main captures. Need to capture others.
    # Use a subset of prompts for speed
    sample_prompts = [
        "The capital of France is",
        "def fibonacci(n):",
        "If all cats are mammals, then all cats",
        "Once upon a time, in a land far away,",
        "2 + 3 =",
        "Translate the following sentence into French:",
    ]

    layers = get_transformer_layers(model)
    results = {}

    for li in check_layers:
        active_counts = []
        for prompt in sample_prompts:
            hooks = []
            capture = {}

            def make_hook(name):
                def hook_fn(module, args, output):
                    capture[name] = output.detach().float().cpu().numpy()
                return hook_fn

            hooks.append(layers[li].mlp.gate_proj.register_forward_hook(make_hook('gate')))
            hooks.append(layers[li].mlp.up_proj.register_forward_hook(make_hook('up')))

            inputs = tokenizer(prompt, return_tensors="pt").to(device)
            with torch.no_grad():
                model(**inputs)

            for h in hooks:
                h.remove()

            gate = capture['gate'][0, -1, :]
            up = capture['up'][0, -1, :]
            silu_gate = 1.0 / (1.0 + np.exp(-gate.astype(np.float64))) * gate
            gate_up = silu_gate * up

            d_ffn = len(gate_up)
            thresh = 0.01 * np.abs(gate_up).max()
            n_active = int(np.sum(np.abs(gate_up) > thresh))
            active_counts.append(n_active)

        mean_active = float(np.mean(active_counts))
        results[f"L{li}"] = {
            "mean_active": mean_active,
            "pct_active": float(mean_active / d_ffn * 100),
            "d_ffn": d_ffn,
        }
        print(f"  L{li}: {mean_active:.0f}/{d_ffn} active ({mean_active/d_ffn*100:.1f}%)",
              file=sys.stderr, flush=True)

    return results


# ══════════════════════════════════════════════════════════════════════
# Analysis 6: MAGNITUDE SPECTRUM — Within the active neurons
# ══════════════════════════════════════════════════════════════════════

def analyze_magnitude_spectrum(all_captures: dict, final_layer: int) -> dict:
    """Within the active neurons, what's the magnitude distribution?"""
    banner("Analysis 6: Active Neuron Magnitude Spectrum")

    all_magnitudes = []
    for key, captures in all_captures.items():
        gate_up = captures[final_layer]['gate_up'][0, -1, :]
        thresh = 0.01 * np.abs(gate_up).max()
        active_mask = np.abs(gate_up) > thresh
        active_mags = np.abs(gate_up[active_mask])
        all_magnitudes.extend(active_mags.tolist())

    mags = np.array(all_magnitudes)

    results = {
        "n_observations": len(mags),
        "mean": float(mags.mean()),
        "median": float(np.median(mags)),
        "std": float(mags.std()),
        "percentiles": {
            "p10": float(np.percentile(mags, 10)),
            "p25": float(np.percentile(mags, 25)),
            "p50": float(np.percentile(mags, 50)),
            "p75": float(np.percentile(mags, 75)),
            "p90": float(np.percentile(mags, 90)),
            "p95": float(np.percentile(mags, 95)),
            "p99": float(np.percentile(mags, 99)),
            "max": float(mags.max()),
        },
        "skewness": float(np.mean(((mags - mags.mean()) / max(mags.std(), 1e-10)) ** 3)),
        "top1_pct_of_total": float(mags.max() / mags.sum() * 100) if mags.sum() > 0 else 0,
    }

    print(f"  {len(mags)} active-neuron observations across all prompts", file=sys.stderr)
    print(f"  Mean: {results['mean']:.4f}  Median: {results['median']:.4f}", file=sys.stderr)
    print(f"  Skewness: {results['skewness']:.2f}", file=sys.stderr)
    print(f"  p10={results['percentiles']['p10']:.4f}  "
          f"p50={results['percentiles']['p50']:.4f}  "
          f"p90={results['percentiles']['p90']:.4f}  "
          f"p99={results['percentiles']['p99']:.4f}  "
          f"max={results['percentiles']['max']:.4f}",
          file=sys.stderr, flush=True)

    return results


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Output Beamformer Probe")
    parser.add_argument("--device", default="mps", help="Device (mps/cuda/cpu)")
    parser.add_argument("--model", default=MODEL, help="Model name")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    final_layer = 63  # Qwen3-32B has 64 layers (0-63)

    # Load model
    model, tokenizer, config = load_model(args.model, args.device)
    final_layer = config.num_hidden_layers - 1

    # ─────────────────────────────────────────────────────────────
    # Phase 1: Capture FFN details for all prompts at final layer
    # ─────────────────────────────────────────────────────────────
    banner("Phase 1: Capturing FFN details at final layer")
    global all_captures
    all_captures = {}
    total = sum(len(v) for v in CATEGORIZED_PROMPTS.values())
    done = 0

    for cat, prompts in CATEGORIZED_PROMPTS.items():
        for pi, prompt in enumerate(prompts):
            key = f"{cat}_{pi}"
            t0 = time.time()
            all_captures[key] = capture_ffn_detailed(
                model, tokenizer, prompt, [final_layer], args.device
            )
            done += 1
            dt = time.time() - t0
            if done % 8 == 0 or done == total:
                print(f"  [{done}/{total}] {dt:.1f}s  {prompt[:40]}...",
                      file=sys.stderr, flush=True)

    # ─────────────────────────────────────────────────────────────
    # Phase 2: Run all analyses
    # ─────────────────────────────────────────────────────────────

    identity_results, neuron_freq, active_sets = analyze_identity(
        all_captures, final_layer
    )
    gate_up_results = analyze_gate_vs_up(all_captures, final_layer)
    token_cloud_results = analyze_token_cloud_mapping(
        model, tokenizer, neuron_freq, final_layer
    )
    category_results = analyze_category_profile(
        all_captures, neuron_freq, final_layer
    )
    sparsity_gradient = analyze_sparsity_gradient(
        model, tokenizer, all_captures, args.device, config
    )
    magnitude_results = analyze_magnitude_spectrum(all_captures, final_layer)

    # ─────────────────────────────────────────────────────────────
    # Phase 3: Save
    # ─────────────────────────────────────────────────────────────
    results = {
        "metadata": {
            "model": args.model,
            "timestamp": datetime.now(UTC).isoformat(),
            "final_layer": final_layer,
            "d_ffn": config.intermediate_size,
            "d_model": config.hidden_size,
            "n_prompts": total,
            "n_categories": len(CATEGORIZED_PROMPTS),
        },
        "identity": identity_results,
        "gate_vs_up": gate_up_results,
        "token_cloud_mapping": token_cloud_results,
        "category_profile": category_results,
        "sparsity_gradient": sparsity_gradient,
        "magnitude_spectrum": magnitude_results,
    }

    out_path = RESULTS_DIR / "summary.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    banner("COMPLETE")
    print(f"Results saved to {out_path}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
