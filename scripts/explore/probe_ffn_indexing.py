#!/usr/bin/env python3
"""FFN Beta-Reduction Indexing Probe — How do inputs address the FFN?

Hypothesis: FFN weights are piles of beta reductions. The input activation
(residual stream entering the FFN) acts as a TYPED INDEX — a beamformer
angle that selects which beta reductions fire. Different input categories
activate sparse, distinct neuron subsets. The gradient direction IS the
beam angle.

TernaryDescent optimizes the routing topology (which beamformer angles exist).
GD optimizes only the beta reductions that are selected. TD = address book.
GD = page contents.

Six analyses on Qwen3-32B:

  1. SPARSITY — FFN activations per input. If FFNs are indexed beta
     reductions, activations should be sparse (few reductions fire per input).

  2. CATEGORY SELECTIVITY — Cluster inputs by semantic category. Same-category
     inputs should activate overlapping neuron subsets (typed indexing).

  3. GRADIENT-AS-BEAMFORMER — Compute input-to-FFN Jacobian structure. If the
     gradient IS the beam angle, gradient directions should cluster by category.

  4. ROW-LEVEL ADDRESSING — For each FFN row (neuron), which input categories
     activate it most? Is there a clean type→neuron mapping?

  5. DEPTH NARROWING — Does the addressing narrow (trunk→leaf) across layers?
     Early layers should use broad neuron subsets (trunk), late layers narrow
     subsets (leaves).

  6. COMBINATOR CORRELATION — How does the FFN addressing relate to the KIBC
     combinator system? Do combinator-typed inputs produce distinct FFN indices?

Architecture: Qwen3-32B — 64 layers, 64 heads, GQA(8 KV), d=5120, bf16.

Usage:
    uv run python scripts/explore/probe_ffn_indexing.py
    uv run python scripts/explore/probe_ffn_indexing.py --quick
    uv run python scripts/explore/probe_ffn_indexing.py --device cuda

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import torch
from scipy import stats as scipy_stats
from scipy.spatial.distance import pdist, squareform

MODEL = "Qwen/Qwen3-32B"
RESULTS_DIR = Path("results/ffn-indexing-qwen3-32b")

# Probe layers — sample across depth to test trunk→leaf narrowing
PROBE_LAYERS = [0, 2, 8, 16, 32, 48, 56, 63]

# ══════════════════════════════════════════════════════════════════════
# Categorized prompts — diverse categories for typed-indexing analysis
# ══════════════════════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════════════════════
# Utility
# ══════════════════════════════════════════════════════════════════════

def banner(msg: str) -> None:
    print(f"\n{'=' * 72}\n  {msg}\n{'=' * 72}\n", file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Model loading
# ══════════════════════════════════════════════════════════════════════

def load_model(model_name: str, device: str = "mps"):
    """Load Qwen3-32B in bf16 with eager attention (for hook compatibility)."""
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
    n_layers = config.num_hidden_layers
    d_model = config.hidden_size

    print(f"  Loaded in {dt:.1f}s", file=sys.stderr)
    print(f"  Layers: {n_layers}  d_model: {d_model}", file=sys.stderr, flush=True)
    return model, tokenizer, config


def get_transformer_layers(model):
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    raise ValueError(f"Cannot find transformer layers in {type(model).__name__}")


# ══════════════════════════════════════════════════════════════════════
# FFN activation capture — hook up_proj and gate×up (post-activation)
# ══════════════════════════════════════════════════════════════════════

def capture_ffn_activations(
    model,
    tokenizer,
    text: str,
    layer_indices: list[int],
    device: str = "mps",
) -> dict:
    """Capture FFN internals for a single prompt.

    Returns dict with per-layer:
      - 'residual_in': residual stream entering the FFN (post-attention, post-norm)
      - 'up_proj': raw up_proj output (before gating)
      - 'gate_up': silu(gate) * up (post-SwiGLU activation)
      - 'ffn_delta': FFN output (residual contribution)
      - 'last_token_logits': logits at last position
    """
    layers = get_transformer_layers(model)
    results = {}
    hooks = []

    for li in layer_indices:
        layer = layers[li]
        results[li] = {}

        # Hook 1: input to FFN (residual after attention + layernorm)
        # In Qwen3: layer.post_attention_layernorm feeds into layer.mlp
        def make_ffn_input_hook(layer_idx):
            def hook_fn(module, args, output):
                # post_attention_layernorm output = FFN input
                results[layer_idx]['residual_in'] = output.detach().float().cpu()
            return hook_fn
        hooks.append(layer.post_attention_layernorm.register_forward_hook(
            make_ffn_input_hook(li)
        ))

        # Hook 2: up_proj output (raw key matching before gating)
        def make_up_hook(layer_idx):
            def hook_fn(module, args, output):
                results[layer_idx]['up_proj'] = output.detach().float().cpu()
            return hook_fn
        hooks.append(layer.mlp.up_proj.register_forward_hook(
            make_up_hook(li)
        ))

        # Hook 3: gate_proj output (gating signal before silu)
        def make_gate_hook(layer_idx):
            def hook_fn(module, args, output):
                results[layer_idx]['gate_proj'] = output.detach().float().cpu()
            return hook_fn
        hooks.append(layer.mlp.gate_proj.register_forward_hook(
            make_gate_hook(li)
        ))

        # Hook 4: MLP output (FFN delta / residual contribution)
        def make_mlp_hook(layer_idx):
            def hook_fn(module, args, output):
                results[layer_idx]['ffn_delta'] = output.detach().float().cpu()
            return hook_fn
        hooks.append(layer.mlp.register_forward_hook(
            make_mlp_hook(li)
        ))

    # Forward pass
    inputs = tokenizer(text, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs)

    # Remove hooks
    for h in hooks:
        h.remove()

    # Compute gate×up (SwiGLU activation)
    for li in layer_indices:
        if 'gate_proj' in results[li] and 'up_proj' in results[li]:
            gate = results[li].pop('gate_proj')
            up = results[li]['up_proj']
            results[li]['gate_up'] = (torch.nn.functional.silu(gate) * up).numpy()
            results[li]['up_proj'] = up.numpy()
            results[li]['residual_in'] = results[li]['residual_in'].numpy()
            results[li]['ffn_delta'] = results[li]['ffn_delta'].numpy()

    return results


# ══════════════════════════════════════════════════════════════════════
# Analysis 1: SPARSITY — How sparse are FFN activations per input?
# ══════════════════════════════════════════════════════════════════════

def analyze_sparsity(all_activations: dict, layer_indices: list[int]) -> dict:
    """Measure activation sparsity (fraction of near-zero neurons) per layer.

    If FFNs are indexed beta reductions, most neurons should be inactive
    for any given input (high sparsity = selective indexing).
    """
    banner("Analysis 1: FFN Activation Sparsity")
    results = {}

    for li in layer_indices:
        sparsities = []
        active_counts = []
        total_neurons = None

        for cat, prompts in CATEGORIZED_PROMPTS.items():
            for pi, prompt in enumerate(prompts):
                key = f"{cat}_{pi}"
                if key not in all_activations or li not in all_activations[key]:
                    continue

                gate_up = all_activations[key][li]['gate_up']
                # Last token position
                acts = gate_up[0, -1, :]  # [d_ffn]
                total_neurons = acts.shape[0]

                # Sparsity: fraction of neurons with |activation| < threshold
                threshold = 0.01 * np.abs(acts).max()  # 1% of max
                n_inactive = np.sum(np.abs(acts) < threshold)
                sparsity = n_inactive / total_neurons
                n_active = total_neurons - n_inactive

                sparsities.append(sparsity)
                active_counts.append(int(n_active))

        results[f"L{li}"] = {
            "mean_sparsity": float(np.mean(sparsities)),
            "std_sparsity": float(np.std(sparsities)),
            "mean_active_neurons": float(np.mean(active_counts)),
            "std_active_neurons": float(np.std(active_counts)),
            "total_neurons": int(total_neurons) if total_neurons else 0,
            "pct_active": float(np.mean(active_counts) / total_neurons * 100) if total_neurons else 0,
        }
        print(f"  L{li:2d}: sparsity={results[f'L{li}']['mean_sparsity']:.3f} "
              f"active={results[f'L{li}']['mean_active_neurons']:.0f}/{total_neurons} "
              f"({results[f'L{li}']['pct_active']:.1f}%)",
              file=sys.stderr, flush=True)

    return results


# ══════════════════════════════════════════════════════════════════════
# Analysis 2: CATEGORY SELECTIVITY — Do same-category inputs activate
#             overlapping neuron subsets?
# ══════════════════════════════════════════════════════════════════════

def analyze_category_selectivity(all_activations: dict, layer_indices: list[int]) -> dict:
    """Measure within-category vs between-category neuron overlap.

    For each category, find the top-K active neurons (union across prompts).
    Measure Jaccard similarity within-category vs between-category.
    High within / low between = typed indexing confirmed.
    """
    banner("Analysis 2: Category Selectivity (Typed Indexing)")
    results = {}

    for li in layer_indices:
        # Build per-prompt activation masks (top-K active neurons)
        category_masks = {}
        for cat, prompts in CATEGORIZED_PROMPTS.items():
            masks = []
            for pi, prompt in enumerate(prompts):
                key = f"{cat}_{pi}"
                if key not in all_activations or li not in all_activations[key]:
                    continue

                gate_up = all_activations[key][li]['gate_up']
                acts = np.abs(gate_up[0, -1, :])  # [d_ffn]

                # Top-K active neurons (top 5% by magnitude)
                k = max(1, int(0.05 * len(acts)))
                top_k_idx = set(np.argsort(acts)[-k:].tolist())
                masks.append(top_k_idx)

            if masks:
                category_masks[cat] = masks

        if not category_masks:
            continue

        # Within-category Jaccard
        within_jaccards = []
        for cat, masks in category_masks.items():
            for i in range(len(masks)):
                for j in range(i + 1, len(masks)):
                    inter = len(masks[i] & masks[j])
                    union = len(masks[i] | masks[j])
                    if union > 0:
                        within_jaccards.append(inter / union)

        # Between-category Jaccard
        between_jaccards = []
        cats = list(category_masks.keys())
        for ci in range(len(cats)):
            for cj in range(ci + 1, len(cats)):
                for mi in category_masks[cats[ci]]:
                    for mj in category_masks[cats[cj]]:
                        inter = len(mi & mj)
                        union = len(mi | mj)
                        if union > 0:
                            between_jaccards.append(inter / union)

        within_mean = float(np.mean(within_jaccards)) if within_jaccards else 0
        between_mean = float(np.mean(between_jaccards)) if between_jaccards else 0
        selectivity_ratio = within_mean / between_mean if between_mean > 0 else float('inf')

        results[f"L{li}"] = {
            "within_category_jaccard": within_mean,
            "between_category_jaccard": between_mean,
            "selectivity_ratio": selectivity_ratio,
            "n_categories": len(category_masks),
        }
        print(f"  L{li:2d}: within={within_mean:.4f} between={between_mean:.4f} "
              f"ratio={selectivity_ratio:.2f}x",
              file=sys.stderr, flush=True)

    return results


# ══════════════════════════════════════════════════════════════════════
# Analysis 3: INPUT DIRECTION CLUSTERING — Do FFN inputs (residual
#             stream) cluster by category? The input IS the beam angle.
# ══════════════════════════════════════════════════════════════════════

def analyze_input_clustering(all_activations: dict, layer_indices: list[int]) -> dict:
    """Measure whether FFN input directions cluster by category.

    If the residual stream (FFN input) IS the beamformer angle, then
    same-category inputs should have similar directions (high cosine
    within, low cosine between).
    """
    banner("Analysis 3: FFN Input Direction Clustering (Beam Angles)")
    results = {}

    for li in layer_indices:
        # Collect per-category FFN input vectors (last token)
        category_vectors = {}
        for cat, prompts in CATEGORIZED_PROMPTS.items():
            vecs = []
            for pi, prompt in enumerate(prompts):
                key = f"{cat}_{pi}"
                if key not in all_activations or li not in all_activations[key]:
                    continue

                res_in = all_activations[key][li]['residual_in']
                vec = res_in[0, -1, :]  # [d_model]
                # Normalize to unit vector (direction only)
                norm = np.linalg.norm(vec)
                if norm > 0:
                    vecs.append(vec / norm)

            if vecs:
                category_vectors[cat] = np.array(vecs)

        if len(category_vectors) < 2:
            continue

        # Within-category cosine similarity
        within_cosines = []
        for cat, vecs in category_vectors.items():
            if len(vecs) < 2:
                continue
            cos_mat = vecs @ vecs.T
            for i in range(len(vecs)):
                for j in range(i + 1, len(vecs)):
                    within_cosines.append(cos_mat[i, j])

        # Between-category cosine similarity
        between_cosines = []
        cats = list(category_vectors.keys())
        for ci in range(len(cats)):
            for cj in range(ci + 1, len(cats)):
                cos_mat = category_vectors[cats[ci]] @ category_vectors[cats[cj]].T
                between_cosines.extend(cos_mat.flatten().tolist())

        within_mean = float(np.mean(within_cosines)) if within_cosines else 0
        between_mean = float(np.mean(between_cosines)) if between_cosines else 0
        separation = within_mean - between_mean

        results[f"L{li}"] = {
            "within_category_cosine": within_mean,
            "between_category_cosine": between_mean,
            "separation": separation,
        }
        print(f"  L{li:2d}: within_cos={within_mean:.4f} between_cos={between_mean:.4f} "
              f"Δ={separation:+.4f}",
              file=sys.stderr, flush=True)

    return results


# ══════════════════════════════════════════════════════════════════════
# Analysis 4: ROW-LEVEL ADDRESSING — Which categories activate which
#             FFN neurons most? Is there a clean type→neuron map?
# ══════════════════════════════════════════════════════════════════════

def analyze_row_addressing(all_activations: dict, layer_indices: list[int]) -> dict:
    """For each FFN neuron, measure which categories activate it most.

    If FFNs are typed beta reductions, each neuron (row) should be
    predominantly activated by one or few categories — not uniformly.
    Measure the entropy of the category distribution per neuron.
    Low entropy = highly typed. High entropy = universal (trunk).
    """
    banner("Analysis 4: Row-Level Category Addressing")
    results = {}

    categories = list(CATEGORIZED_PROMPTS.keys())

    for li in layer_indices:
        # Build neuron × category activation matrix
        cat_activations = {cat: [] for cat in categories}
        d_ffn = None

        for cat, prompts in CATEGORIZED_PROMPTS.items():
            for pi, prompt in enumerate(prompts):
                key = f"{cat}_{pi}"
                if key not in all_activations or li not in all_activations[key]:
                    continue

                gate_up = all_activations[key][li]['gate_up']
                acts = np.abs(gate_up[0, -1, :])  # [d_ffn]
                d_ffn = len(acts)
                cat_activations[cat].append(acts)

        if d_ffn is None:
            continue

        # Mean activation per category per neuron: [n_cats, d_ffn]
        cat_means = []
        for cat in categories:
            if cat_activations[cat]:
                cat_means.append(np.mean(cat_activations[cat], axis=0))
            else:
                cat_means.append(np.zeros(d_ffn))
        cat_means = np.array(cat_means)  # [n_cats, d_ffn]

        # Normalize to probability distribution per neuron (across categories)
        cat_sums = cat_means.sum(axis=0, keepdims=True)  # [1, d_ffn]
        cat_sums = np.maximum(cat_sums, 1e-10)
        cat_probs = cat_means / cat_sums  # [n_cats, d_ffn]

        # Entropy per neuron (across categories)
        # Low entropy = highly selective (typed). High entropy = universal (trunk).
        entropies = -np.sum(cat_probs * np.log2(np.maximum(cat_probs, 1e-10)), axis=0)
        max_entropy = np.log2(len(categories))

        # Dominant category per neuron
        dominant_cat_idx = np.argmax(cat_means, axis=0)
        dominant_cat_counts = {}
        for cat_idx in range(len(categories)):
            count = int(np.sum(dominant_cat_idx == cat_idx))
            dominant_cat_counts[categories[cat_idx]] = count

        # Stratify by entropy: how many neurons are selective vs universal
        low_entropy = np.sum(entropies < max_entropy * 0.3)
        mid_entropy = np.sum((entropies >= max_entropy * 0.3) & (entropies < max_entropy * 0.7))
        high_entropy = np.sum(entropies >= max_entropy * 0.7)

        results[f"L{li}"] = {
            "mean_entropy": float(np.mean(entropies)),
            "median_entropy": float(np.median(entropies)),
            "max_possible_entropy": float(max_entropy),
            "normalized_entropy": float(np.mean(entropies) / max_entropy),
            "pct_selective": float(low_entropy / d_ffn * 100),
            "pct_mixed": float(mid_entropy / d_ffn * 100),
            "pct_universal": float(high_entropy / d_ffn * 100),
            "dominant_category_counts": dominant_cat_counts,
            "d_ffn": int(d_ffn),
        }
        print(f"  L{li:2d}: entropy={results[f'L{li}']['normalized_entropy']:.3f} "
              f"selective={results[f'L{li}']['pct_selective']:.1f}% "
              f"universal={results[f'L{li}']['pct_universal']:.1f}%",
              file=sys.stderr, flush=True)

    return results


# ══════════════════════════════════════════════════════════════════════
# Analysis 5: DEPTH NARROWING — Does addressing narrow across layers?
# ══════════════════════════════════════════════════════════════════════

def analyze_depth_narrowing(all_activations: dict, layer_indices: list[int]) -> dict:
    """Test whether FFN addressing narrows with depth (trunk→leaf).

    Early layers should activate broad neuron subsets (universal trunk ops).
    Late layers should activate narrow subsets (specific leaf ops).
    Measure: effective dimensionality of activation patterns per layer.
    """
    banner("Analysis 5: Depth Narrowing (Trunk → Leaf)")
    results = {}

    for li in layer_indices:
        all_acts = []
        for cat, prompts in CATEGORIZED_PROMPTS.items():
            for pi, prompt in enumerate(prompts):
                key = f"{cat}_{pi}"
                if key not in all_activations or li not in all_activations[key]:
                    continue

                gate_up = all_activations[key][li]['gate_up']
                acts = gate_up[0, -1, :]  # [d_ffn]
                all_acts.append(acts)

        if not all_acts:
            continue

        all_acts = np.array(all_acts)  # [n_prompts, d_ffn]

        # Effective dimensionality: participation ratio of SVD spectrum
        # PR = (Σσ_i)² / Σσ_i² — higher = more dimensions active = broader addressing
        # Use a sample of neurons to keep SVD tractable
        n_neurons = all_acts.shape[1]
        if n_neurons > 4096:
            # Sample 4096 neurons
            idx = np.random.RandomState(42).choice(n_neurons, 4096, replace=False)
            acts_sample = all_acts[:, idx]
        else:
            acts_sample = all_acts

        # Center
        acts_sample = acts_sample - acts_sample.mean(axis=0, keepdims=True)

        try:
            U, S, Vt = np.linalg.svd(acts_sample, full_matrices=False)
            S2 = S ** 2
            participation_ratio = (S2.sum() ** 2) / (S2 ** 2).sum()
            top1_variance = float(S2[0] / S2.sum())
            top10_variance = float(S2[:10].sum() / S2.sum())
        except np.linalg.LinAlgError:
            participation_ratio = 0
            top1_variance = 0
            top10_variance = 0

        # Also measure mean activation magnitude (trunk = higher?)
        mean_magnitude = float(np.mean(np.abs(all_acts)))

        # Activation overlap across prompts (higher = broader addressing)
        # Compute pairwise Jaccard on top-5% active neuron sets
        k = max(1, int(0.05 * n_neurons))
        top_k_sets = []
        for acts in all_acts:
            top_k_idx = set(np.argsort(np.abs(acts))[-k:].tolist())
            top_k_sets.append(top_k_idx)

        overlaps = []
        for i in range(min(len(top_k_sets), 30)):  # cap pairwise comparisons
            for j in range(i + 1, min(len(top_k_sets), 30)):
                inter = len(top_k_sets[i] & top_k_sets[j])
                union = len(top_k_sets[i] | top_k_sets[j])
                if union > 0:
                    overlaps.append(inter / union)

        results[f"L{li}"] = {
            "participation_ratio": float(participation_ratio),
            "top1_variance_explained": top1_variance,
            "top10_variance_explained": top10_variance,
            "mean_activation_magnitude": mean_magnitude,
            "mean_cross_prompt_overlap": float(np.mean(overlaps)) if overlaps else 0,
        }
        print(f"  L{li:2d}: PR={participation_ratio:.1f} "
              f"top1_var={top1_variance:.3f} "
              f"overlap={results[f'L{li}']['mean_cross_prompt_overlap']:.4f} "
              f"mag={mean_magnitude:.3f}",
              file=sys.stderr, flush=True)

    return results


# ══════════════════════════════════════════════════════════════════════
# Analysis 6: ACTIVATION RDM vs CATEGORY STRUCTURE — Does the FFN
#             activation pattern reflect the category structure?
# ══════════════════════════════════════════════════════════════════════

def analyze_category_rdm(all_activations: dict, layer_indices: list[int]) -> dict:
    """Compare FFN activation RDMs against category structure.

    Build a representational dissimilarity matrix (RDM) from FFN activations.
    Build a categorical RDM (same category = 0, different = 1).
    Correlate them. High correlation = FFN preserves category structure.
    This is the beamformer test: if the beam angle IS the category,
    then the FFN activation pattern should mirror the category structure.
    """
    banner("Analysis 6: FFN Activation RDM vs Category Structure")
    results = {}

    # Build category labels
    prompt_labels = []
    for cat, prompts in CATEGORIZED_PROMPTS.items():
        for pi in range(len(prompts)):
            prompt_labels.append(cat)

    for li in layer_indices:
        # Collect activation vectors (last token gate×up)
        act_vectors = []
        valid_labels = []
        for cat, prompts in CATEGORIZED_PROMPTS.items():
            for pi, prompt in enumerate(prompts):
                key = f"{cat}_{pi}"
                if key not in all_activations or li not in all_activations[key]:
                    continue
                gate_up = all_activations[key][li]['gate_up']
                act_vectors.append(gate_up[0, -1, :])
                valid_labels.append(cat)

        if len(act_vectors) < 4:
            continue

        act_matrix = np.array(act_vectors)  # [n_prompts, d_ffn]

        # FFN activation RDM (cosine distance)
        norms = np.linalg.norm(act_matrix, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-10)
        act_normed = act_matrix / norms
        cos_sim = act_normed @ act_normed.T
        ffn_rdm = 1 - cos_sim  # cosine distance

        # Category RDM (0 if same category, 1 if different)
        n = len(valid_labels)
        cat_rdm = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                cat_rdm[i, j] = 0 if valid_labels[i] == valid_labels[j] else 1

        # Also do an FFN input (residual) RDM for comparison
        res_vectors = []
        for cat, prompts in CATEGORIZED_PROMPTS.items():
            for pi, prompt in enumerate(prompts):
                key = f"{cat}_{pi}"
                if key not in all_activations or li not in all_activations[key]:
                    continue
                res_in = all_activations[key][li]['residual_in']
                res_vectors.append(res_in[0, -1, :])

        res_matrix = np.array(res_vectors)
        norms_r = np.linalg.norm(res_matrix, axis=1, keepdims=True)
        norms_r = np.maximum(norms_r, 1e-10)
        res_normed = res_matrix / norms_r
        input_rdm = 1 - (res_normed @ res_normed.T)

        # Correlate RDMs (upper triangle only, excluding diagonal)
        triu_idx = np.triu_indices(n, k=1)
        ffn_flat = ffn_rdm[triu_idx]
        cat_flat = cat_rdm[triu_idx]
        input_flat = input_rdm[triu_idx]

        # Spearman correlation: FFN activation RDM vs category RDM
        r_ffn_cat, p_ffn_cat = scipy_stats.spearmanr(ffn_flat, cat_flat)
        # Spearman correlation: FFN input RDM vs category RDM
        r_input_cat, p_input_cat = scipy_stats.spearmanr(input_flat, cat_flat)
        # Spearman correlation: FFN input vs FFN activation (how much does FFN transform?)
        r_input_ffn, p_input_ffn = scipy_stats.spearmanr(input_flat, ffn_flat)

        results[f"L{li}"] = {
            "ffn_vs_category_rho": float(r_ffn_cat),
            "ffn_vs_category_p": float(p_ffn_cat),
            "input_vs_category_rho": float(r_input_cat),
            "input_vs_category_p": float(p_input_cat),
            "input_vs_ffn_rho": float(r_input_ffn),
            "input_vs_ffn_p": float(p_input_ffn),
        }
        print(f"  L{li:2d}: FFN↔cat ρ={r_ffn_cat:+.3f} (p={p_ffn_cat:.1e})  "
              f"input↔cat ρ={r_input_cat:+.3f}  input↔FFN ρ={r_input_ffn:+.3f}",
              file=sys.stderr, flush=True)

    return results


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="FFN Beta-Reduction Indexing Probe")
    parser.add_argument("--device", default="mps", help="Device (mps/cuda/cpu)")
    parser.add_argument("--quick", action="store_true", help="Use fewer layers (faster)")
    parser.add_argument("--model", default=MODEL, help="Model name")
    args = parser.parse_args()

    probe_layers = [0, 16, 32, 63] if args.quick else PROBE_LAYERS
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load model
    model, tokenizer, config = load_model(args.model, args.device)

    # ─────────────────────────────────────────────────────────────
    # Phase 1: Capture all FFN activations
    # ─────────────────────────────────────────────────────────────
    banner("Phase 1: Capturing FFN activations for all prompts")
    all_activations = {}
    total_prompts = sum(len(v) for v in CATEGORIZED_PROMPTS.values())
    done = 0

    for cat, prompts in CATEGORIZED_PROMPTS.items():
        for pi, prompt in enumerate(prompts):
            key = f"{cat}_{pi}"
            t0 = time.time()
            all_activations[key] = capture_ffn_activations(
                model, tokenizer, prompt, probe_layers, args.device
            )
            done += 1
            dt = time.time() - t0
            if done % 8 == 0 or done == total_prompts:
                print(f"  [{done}/{total_prompts}] {dt:.1f}s  {prompt[:40]}...",
                      file=sys.stderr, flush=True)

    # ─────────────────────────────────────────────────────────────
    # Phase 2: Run all analyses
    # ─────────────────────────────────────────────────────────────
    results = {
        "metadata": {
            "model": args.model,
            "timestamp": datetime.now(UTC).isoformat(),
            "probe_layers": probe_layers,
            "n_categories": len(CATEGORIZED_PROMPTS),
            "n_prompts_per_category": {k: len(v) for k, v in CATEGORIZED_PROMPTS.items()},
            "total_prompts": total_prompts,
        },
        "sparsity": analyze_sparsity(all_activations, probe_layers),
        "category_selectivity": analyze_category_selectivity(all_activations, probe_layers),
        "input_clustering": analyze_input_clustering(all_activations, probe_layers),
        "row_addressing": analyze_row_addressing(all_activations, probe_layers),
        "depth_narrowing": analyze_depth_narrowing(all_activations, probe_layers),
        "category_rdm": analyze_category_rdm(all_activations, probe_layers),
    }

    # ─────────────────────────────────────────────────────────────
    # Phase 3: Summary
    # ─────────────────────────────────────────────────────────────
    banner("SUMMARY")

    print("\n--- Sparsity Profile ---", file=sys.stderr)
    for li in probe_layers:
        s = results["sparsity"].get(f"L{li}", {})
        print(f"  L{li:2d}: {s.get('pct_active', 0):.1f}% active "
              f"({s.get('mean_active_neurons', 0):.0f}/{s.get('total_neurons', 0)})",
              file=sys.stderr)

    print("\n--- Category Selectivity ---", file=sys.stderr)
    for li in probe_layers:
        s = results["category_selectivity"].get(f"L{li}", {})
        print(f"  L{li:2d}: within/between={s.get('selectivity_ratio', 0):.2f}x",
              file=sys.stderr)

    print("\n--- Input Clustering (Beam Angles) ---", file=sys.stderr)
    for li in probe_layers:
        s = results["input_clustering"].get(f"L{li}", {})
        print(f"  L{li:2d}: within_cos={s.get('within_category_cosine', 0):.4f} "
              f"between_cos={s.get('between_category_cosine', 0):.4f} "
              f"Δ={s.get('separation', 0):+.4f}",
              file=sys.stderr)

    print("\n--- Depth Narrowing ---", file=sys.stderr)
    for li in probe_layers:
        s = results["depth_narrowing"].get(f"L{li}", {})
        print(f"  L{li:2d}: PR={s.get('participation_ratio', 0):.1f} "
              f"top1_var={s.get('top1_variance_explained', 0):.3f}",
              file=sys.stderr)

    print("\n--- Category RDM ---", file=sys.stderr)
    for li in probe_layers:
        s = results["category_rdm"].get(f"L{li}", {})
        print(f"  L{li:2d}: FFN↔cat ρ={s.get('ffn_vs_category_rho', 0):+.3f}  "
              f"input↔cat ρ={s.get('input_vs_category_rho', 0):+.3f}",
              file=sys.stderr)

    # Save
    out_path = RESULTS_DIR / "summary.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
