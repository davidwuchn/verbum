#!/usr/bin/env python3
"""Probe: Head-level hologram analysis — resolving angle multiplexing.

Session 095 found that all 6 holograms share the same bimodal depth profile
(L7 peak → L11 dip → L31 peak) because they ride the same architectural wave.
Layer-level orthogonality test failed: all cross-hologram correlations > 0.72.

This script resolves the question at HEAD granularity:
  - Are holograms angle-multiplexed (same heads, different Q patterns)?
  - Or independent circuits (different heads entirely)?
  - Does binding use the same heads as I-combinator?

Three analysis modes:

  1. HEAD-LEVEL SELECTIVITY: Hook inside attention to capture per-head
     output (before o_proj mixing). Compute per-head divergence between
     active/control for each hologram. Result: hologram × head matrix.

  2. BINDING ↔ I OVERLAP: Compare heads that show I-combinator selectivity
     against heads that show binding selectivity AND heads that fail ternary
     for binding. If binding IS the I-circuit, these should overlap.

  3. LATE MoE GATE TERNARY: Complete discourse beam-selector test at L31-L39
     (where discourse selectivity peaks), not just L0-L4.

Output: results/hologram-heads/

Usage:
    # Full analysis (all modes):
    uv run python scripts/explore/probe_hologram_heads.py

    # Specific analysis:
    uv run python scripts/explore/probe_hologram_heads.py --analysis heads
    uv run python scripts/explore/probe_hologram_heads.py --analysis binding_i
    uv run python scripts/explore/probe_hologram_heads.py --analysis moe_late

    # Quick mode:
    uv run python scripts/explore/probe_hologram_heads.py --quick

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

# ══════════════════════════════════════════════════════════════════
# Import infrastructure from atlas script
# ══════════════════════════════════════════════════════════════════

# We import probe definitions and model loading from the atlas script.
# The atlas script lives in the same directory.
sys.path.insert(0, str(Path(__file__).parent))
from probe_hologram_atlas import (
    MODELS,
    COMBINATOR_PROBES,
    HOLOGRAM_PROBES,
    load_model,
    get_model_info,
    get_decoder_layers,
    get_layer_attn_type,
    get_attn_module,
    get_attn_proj_names,
    ternary_quantize_layer,
    restore_layer,
    measure_selectivity,
    aggregate_selectivity,
)


# ══════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════

OUTPUT_DIR = Path("results/hologram-heads")

ALL_ANALYSES = ["heads", "binding_i", "moe_late"]


# ══════════════════════════════════════════════════════════════════
# Per-head hidden state capture
# ══════════════════════════════════════════════════════════════════

def get_per_head_outputs(
    model, tokenizer, text: str, layers: list[int], info: dict,
) -> dict:
    """Capture per-head attention outputs BEFORE o_proj mixing.

    For full-attention layers (Qwen/LLaMA): hooks v_proj output, then
    uses the attention weights to compute per-head attended values.

    Strategy: we hook the FULL LAYER to get residual stream, then also
    hook v_proj and capture attention weights via output_attentions.

    However, output_attentions may not work with all architectures.
    Simpler approach: hook the o_proj INPUT — this is the concatenated
    per-head outputs [batch, seq, n_heads * head_dim] before the final
    linear projection. We reshape to [batch, seq, n_heads, head_dim].

    For GatedDeltaNet layers: the per-head decomposition is different
    (recurrent, not attention). We hook out_proj input similarly.

    Returns: {layer_idx: tensor[seq, n_heads, head_dim]}
    """
    decoder_layers = get_decoder_layers(model)
    n_heads = info["n_heads"]
    head_dim = info["head_dim"]
    n_kv_heads = info["n_kv_heads"]

    captured = {}
    hooks = []

    def make_hook(layer_idx):
        def hook_fn(module, input, output):
            # input to o_proj is the concatenated per-head output
            # Shape: [batch, seq, n_heads * head_dim]
            if isinstance(input, tuple):
                h = input[0]
            else:
                h = input
            # Reshape to [seq, n_heads, head_dim]
            seq_len = h.shape[1]
            h = h[0].detach().cpu().float()  # [seq, n_heads*head_dim]
            h = h.view(seq_len, n_heads, head_dim)  # [seq, n_heads, head_dim]
            captured[layer_idx] = h
        return hook_fn

    for li in layers:
        layer = decoder_layers[li]
        attn = get_attn_module(layer)
        attn_type = get_layer_attn_type(layer)

        # Find o_proj / out_proj / dense — the output projection
        if hasattr(attn, "o_proj"):
            proj = attn.o_proj          # Qwen full attention
        elif hasattr(attn, "out_proj"):
            proj = attn.out_proj        # Qwen3.6 GatedDeltaNet
        elif hasattr(attn, "dense"):
            proj = attn.dense           # Pythia
        else:
            print(f"  ⚠ Cannot find output projection for L{li} ({attn_type}), skipping",
                  file=sys.stderr)
            continue

        hooks.append(proj.register_forward_hook(make_hook(li)))

    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        model(**inputs)

    for h in hooks:
        h.remove()

    return captured


def measure_head_selectivity(
    model, tokenizer, probes: dict,
    layers: list[int], info: dict,
    quick: bool = False,
) -> dict:
    """Measure per-head selectivity for each condition in a probe set.

    For each condition, computes cosine divergence between active and
    control at EACH HEAD in EACH LAYER (not just layer aggregate).

    Returns: {condition_name: {
        "layer_head_selectivity": {layer: [head0_sel, head1_sel, ...]},
        "output_kl": float,
    }}
    """
    n_heads = info["n_heads"]
    results = {}

    for cond_name, cond_data in probes.items():
        active_texts = cond_data["active"]
        control_texts = cond_data["control"]

        if quick:
            active_texts = active_texts[:2]
            control_texts = control_texts[:2]

        n_pairs = min(len(active_texts), len(control_texts))
        # head_sel[layer][head] = list of divergence values across pairs
        head_sel = {li: {hi: [] for hi in range(n_heads)} for li in layers}
        output_kls = []

        for i in range(n_pairs):
            a = get_per_head_outputs(model, tokenizer, active_texts[i], layers, info)
            c = get_per_head_outputs(model, tokenizer, control_texts[i], layers, info)

            # Also get output logits for KL
            a_logits = _get_logits(model, tokenizer, active_texts[i])
            c_logits = _get_logits(model, tokenizer, control_texts[i])

            p = F.softmax(a_logits, dim=-1)
            q = F.softmax(c_logits, dim=-1)
            kl = F.kl_div(q.log(), p, reduction="sum").item()
            output_kls.append(kl)

            for li in layers:
                if li not in a or li not in c:
                    continue
                # a[li] shape: [seq, n_heads, head_dim]
                # Mean-pool over sequence dim → [n_heads, head_dim]
                h_a = a[li].mean(dim=0)  # [n_heads, head_dim]
                h_c = c[li].mean(dim=0)  # [n_heads, head_dim]

                for hi in range(n_heads):
                    cos = F.cosine_similarity(
                        h_a[hi].unsqueeze(0), h_c[hi].unsqueeze(0)
                    ).item()
                    head_sel[li][hi].append(1.0 - cos)

            if torch.backends.mps.is_available():
                torch.mps.empty_cache()

        # Average across pairs
        results[cond_name] = {
            "description": cond_data["description"],
            "n_pairs": n_pairs,
            "layer_head_selectivity": {
                li: [float(np.mean(head_sel[li][hi])) if head_sel[li][hi] else 0.0
                     for hi in range(n_heads)]
                for li in layers
            },
            "output_kl": float(np.mean(output_kls)),
        }

    return results


def _get_logits(model, tokenizer, text: str) -> torch.Tensor:
    """Get output logits for a text."""
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.logits[0, -1].detach().cpu().float()


def aggregate_head_selectivity(
    per_condition: dict, layers: list[int], n_heads: int,
) -> dict:
    """Aggregate per-head selectivity across conditions.

    Returns: {
        "layer_head_selectivity": {layer: [head0_mean, head1_mean, ...]},
        "output_kl": float,
        "head_vector": list[float],  # flattened [layers × heads] for orthogonality
    }
    """
    all_head_sel = {li: {hi: [] for hi in range(n_heads)} for li in layers}
    all_kls = []

    for cond_name, cond in per_condition.items():
        for li in layers:
            heads = cond["layer_head_selectivity"][li]
            for hi in range(n_heads):
                all_head_sel[li][hi].append(heads[hi])
        all_kls.append(cond["output_kl"])

    layer_head = {
        li: [float(np.mean(all_head_sel[li][hi])) for hi in range(n_heads)]
        for li in layers
    }

    # Flatten to a single vector: [L0H0, L0H1, ..., L0Hn, L1H0, ..., LmHn]
    head_vector = []
    for li in sorted(layers):
        head_vector.extend(layer_head[li])

    return {
        "layer_head_selectivity": layer_head,
        "output_kl": float(np.mean(all_kls)),
        "head_vector": head_vector,
    }


# ══════════════════════════════════════════════════════════════════
# Cross-hologram orthogonality at head level
# ══════════════════════════════════════════════════════════════════

def compute_head_orthogonality(
    head_profiles: dict[str, list[float]],
) -> dict:
    """Compare head-level selectivity vectors across holograms.

    Each hologram has a flattened vector of [layers × heads] selectivity values.
    If two holograms use different heads, their vectors will be orthogonal.
    If they share heads (angle-multiplexed), high cosine similarity.

    This is the corrected test — head-level resolution instead of layer-level.
    """
    hologram_names = sorted(head_profiles.keys())
    n = len(hologram_names)

    vectors = {name: np.array(head_profiles[name]) for name in hologram_names}

    # Correlation matrix
    corr_matrix = np.zeros((n, n))
    for i, ni in enumerate(hologram_names):
        for j, nj in enumerate(hologram_names):
            vi, vj = vectors[ni], vectors[nj]
            if np.std(vi) < 1e-10 or np.std(vj) < 1e-10:
                corr_matrix[i, j] = 0.0
            else:
                corr_matrix[i, j] = float(np.corrcoef(vi, vj)[0, 1])

    # Cosine similarity matrix
    cos_matrix = np.zeros((n, n))
    for i, ni in enumerate(hologram_names):
        for j, nj in enumerate(hologram_names):
            norm_i = np.linalg.norm(vectors[ni])
            norm_j = np.linalg.norm(vectors[nj])
            if norm_i < 1e-10 or norm_j < 1e-10:
                cos_matrix[i, j] = 0.0
            else:
                cos_matrix[i, j] = float(np.dot(vectors[ni], vectors[nj])
                                         / (norm_i * norm_j))

    # Top-K head overlap analysis: for each hologram, find top-K heads
    # and measure Jaccard similarity between hologram pairs
    K = 20  # top 20 heads
    top_heads = {}
    for name in hologram_names:
        v = vectors[name]
        top_indices = np.argsort(v)[-K:]
        top_heads[name] = set(top_indices.tolist())

    jaccard_matrix = np.zeros((n, n))
    for i, ni in enumerate(hologram_names):
        for j, nj in enumerate(hologram_names):
            inter = len(top_heads[ni] & top_heads[nj])
            union = len(top_heads[ni] | top_heads[nj])
            jaccard_matrix[i, j] = inter / max(union, 1)

    return {
        "names": hologram_names,
        "correlation_matrix": corr_matrix.tolist(),
        "cosine_matrix": cos_matrix.tolist(),
        "jaccard_top20_matrix": jaccard_matrix.tolist(),
        "top20_heads": {name: sorted(heads) for name, heads in top_heads.items()},
        "vector_dims": len(vectors[hologram_names[0]]),
    }


# ══════════════════════════════════════════════════════════════════
# Analysis 2: Binding ↔ I combinator overlap
# ══════════════════════════════════════════════════════════════════

def analyze_binding_i_overlap(
    binding_head_sel: dict,  # from measure_head_selectivity on BINDING_PROBES
    combinator_head_sel: dict,  # from measure_head_selectivity on COMBINATOR_PROBES
    layers: list[int],
    info: dict,
) -> dict:
    """Test whether binding-selective heads overlap with I-combinator heads.

    Session 093 finding: I combinator is the outlier (r≈0.70 vs K/B/C r>0.90).
    Session 095 finding: binding has 5/18 ternary failures, all magnitude-dependent.
    Hypothesis: binding IS the I-circuit; I's distinctness = magnitude dependence.

    Method:
    1. Identify top-K heads for binding (across both conditions)
    2. Identify top-K heads for each combinator (K, I, B, C)
    3. Compare: Jaccard(binding_top, I_top) vs Jaccard(binding_top, K_top) etc.
    4. If binding ≈ I, Jaccard(binding, I) >> Jaccard(binding, K/B/C)
    """
    n_heads = info["n_heads"]
    K = 20  # top K heads

    # Aggregate binding across conditions
    binding_agg = aggregate_head_selectivity(binding_head_sel, layers, n_heads)
    binding_vec = np.array(binding_agg["head_vector"])

    # Per-combinator head vectors
    combinator_vecs = {}
    for comb_name, cond_data in combinator_head_sel.items():
        # Single condition → use directly
        vec = []
        for li in sorted(layers):
            vec.extend(cond_data["layer_head_selectivity"][li])
        combinator_vecs[comb_name] = np.array(vec)

    # Top-K heads for each
    binding_top = set(np.argsort(binding_vec)[-K:].tolist())

    combinator_tops = {}
    for name, vec in combinator_vecs.items():
        combinator_tops[name] = set(np.argsort(vec)[-K:].tolist())

    # Jaccard overlaps
    jaccard = {}
    for name, tops in combinator_tops.items():
        inter = len(binding_top & tops)
        union = len(binding_top | tops)
        jaccard[name] = inter / max(union, 1)

    # Cosine similarities
    cosines = {}
    for name, vec in combinator_vecs.items():
        norm_b = np.linalg.norm(binding_vec)
        norm_c = np.linalg.norm(vec)
        if norm_b < 1e-10 or norm_c < 1e-10:
            cosines[name] = 0.0
        else:
            cosines[name] = float(np.dot(binding_vec, vec) / (norm_b * norm_c))

    # Correlations
    correlations = {}
    for name, vec in combinator_vecs.items():
        if np.std(binding_vec) < 1e-10 or np.std(vec) < 1e-10:
            correlations[name] = 0.0
        else:
            correlations[name] = float(np.corrcoef(binding_vec, vec)[0, 1])

    # Per-layer top head breakdown (which layers contribute most to overlap?)
    per_layer_overlap = {}
    for li in layers:
        start = sorted(layers).index(li) * n_heads
        end = start + n_heads
        b_layer_top = set(np.argsort(binding_vec[start:end])[-5:].tolist())
        for cname, cvec in combinator_vecs.items():
            c_layer_top = set(np.argsort(cvec[start:end])[-5:].tolist())
            key = f"L{li}_{cname}"
            inter = len(b_layer_top & c_layer_top)
            per_layer_overlap[key] = inter / max(len(b_layer_top | c_layer_top), 1)

    return {
        "jaccard_binding_vs_combinator": jaccard,
        "cosine_binding_vs_combinator": cosines,
        "correlation_binding_vs_combinator": correlations,
        "binding_top20": sorted(binding_top),
        "combinator_top20": {n: sorted(t) for n, t in combinator_tops.items()},
        "per_layer_top5_overlap": per_layer_overlap,
        "prediction": "binding≈I iff Jaccard(binding,I) >> Jaccard(binding,K/B/C)",
    }


# ══════════════════════════════════════════════════════════════════
# Analysis 3: Late MoE gate ternary survival
# ══════════════════════════════════════════════════════════════════

def analyze_moe_gates_late(model, info: dict) -> dict:
    """Complete MoE gate ternary survival test for late layers (L31-L39).

    Atlas only tested L0-L4. Discourse selectivity peaks at L31-L35.
    The late-layer gates have smaller Frobenius norms but high effective rank.
    This tests whether discourse beam-selection survives quantization where
    it matters most.
    """
    decoder_layers = get_decoder_layers(model)
    n_layers = info["n_layers"]

    # Test late layers: last 10 layers + original L0-L4 for comparison
    test_layers = list(range(max(0, n_layers - 10), n_layers))
    # Also include some middle layers for the period-12 structure
    if n_layers > 20:
        test_layers = sorted(set(test_layers + list(range(n_layers // 2 - 2, n_layers // 2 + 3))))

    gate_results = {}

    for li in test_layers:
        layer = decoder_layers[li]
        if not hasattr(layer, "mlp") or not hasattr(layer.mlp, "gate"):
            continue
        gate = layer.mlp.gate
        if not hasattr(gate, "weight"):
            continue

        w = gate.weight.data.cpu().float()  # [num_experts, d_model]

        # Original gate stats
        frob = float(w.norm().item())
        svd_vals = torch.linalg.svdvals(w)
        cumsum = torch.cumsum(svd_vals / svd_vals.sum(), dim=0)
        eff_rank_90 = int((cumsum < 0.90).sum().item()) + 1
        eff_rank_99 = int((cumsum < 0.99).sum().item()) + 1

        # Sign balance
        n_pos = int((w > 0).sum().item())
        n_neg = int((w < 0).sum().item())
        balance = n_pos / max(n_neg, 1)

        # Ternary survival: sign-only
        w_ternary = torch.sign(w)
        cos_sign = F.cosine_similarity(
            w.flatten().unsqueeze(0),
            w_ternary.flatten().unsqueeze(0)
        ).item()

        # Ternary survival: 50% sparse
        abs_w = w.abs()
        flat = abs_w.flatten()
        threshold_50 = torch.quantile(flat, 0.50).item()
        w_tern_50 = torch.zeros_like(w)
        w_tern_50[w > threshold_50] = 1.0
        w_tern_50[w < -threshold_50] = -1.0
        cos_50 = F.cosine_similarity(
            w.flatten().unsqueeze(0),
            w_tern_50.flatten().unsqueeze(0)
        ).item()

        # Ternary survival: 75% sparse
        threshold_75 = torch.quantile(flat, 0.75).item()
        w_tern_75 = torch.zeros_like(w)
        w_tern_75[w > threshold_75] = 1.0
        w_tern_75[w < -threshold_75] = -1.0
        cos_75 = F.cosine_similarity(
            w.flatten().unsqueeze(0),
            w_tern_75.flatten().unsqueeze(0)
        ).item()

        gate_results[li] = {
            "frobenius_norm": frob,
            "effective_rank_90": eff_rank_90,
            "effective_rank_99": eff_rank_99,
            "balance": balance,
            "ternary_survival": {
                "sign_only": {"cos": cos_sign, "survived": cos_sign > 0.5},
                "mid_sparse_50": {"cos": cos_50, "survived": cos_50 > 0.5},
                "high_sparse_75": {"cos": cos_75, "survived": cos_75 > 0.5},
            },
        }

    return {
        "test_layers": test_layers,
        "gate_stats": gate_results,
    }


# ══════════════════════════════════════════════════════════════════
# Per-head ternary survival (for binding fragility analysis)
# ══════════════════════════════════════════════════════════════════

def measure_head_ternary_survival(
    model, tokenizer, probes: dict,
    target_layers: list[int],
    measure_layers: list[int],
    info: dict,
    quick: bool = False,
) -> dict:
    """Measure which SPECIFIC HEADS lose selectivity under ternary quantization.

    Instead of layer-level survival, this runs the full head-level selectivity
    measurement before and after quantization to identify exactly which heads
    are magnitude-dependent.

    Returns per-head survival ratios for each target layer quantized.
    """
    n_heads = info["n_heads"]

    # Baseline: per-head selectivity
    print("    Measuring baseline head selectivity...", file=sys.stderr)
    baseline = measure_head_selectivity(
        model, tokenizer, probes, measure_layers, info, quick)
    baseline_agg = aggregate_head_selectivity(baseline, measure_layers, n_heads)

    results = {"baseline": baseline_agg, "experiments": {}}

    for target_layer in target_layers:
        print(f"    Quantizing L{target_layer} (sign-only)...", file=sys.stderr)

        # Quantize to sign-only (the most discriminating test)
        originals, quant_stats = ternary_quantize_layer(model, target_layer, 0.0)

        # Measure per-head selectivity under quantization
        quantized = measure_head_selectivity(
            model, tokenizer, probes, measure_layers, info, quick)
        quantized_agg = aggregate_head_selectivity(quantized, measure_layers, n_heads)

        # Per-head survival ratios
        head_survival = {}
        for li in measure_layers:
            baseline_heads = baseline_agg["layer_head_selectivity"][li]
            quantized_heads = quantized_agg["layer_head_selectivity"][li]
            head_survival[li] = [
                quantized_heads[hi] / max(baseline_heads[hi], 1e-8)
                for hi in range(n_heads)
            ]

        results["experiments"][target_layer] = {
            "quant_stats": quant_stats,
            "head_survival": head_survival,
            "aggregate_quantized": quantized_agg,
        }

        # Restore
        restore_layer(model, target_layer, originals)

    return results


# ══════════════════════════════════════════════════════════════════
# Output formatting
# ══════════════════════════════════════════════════════════════════

def print_head_selectivity_summary(
    hologram_name: str,
    head_sel: dict,
    layers: list[int],
    n_heads: int,
    top_k: int = 10,
):
    """Print top-K most selective heads for a hologram."""
    agg = aggregate_head_selectivity(head_sel, layers, n_heads)

    # Find top-K heads globally
    all_heads = []
    for li in sorted(layers):
        heads = agg["layer_head_selectivity"][li]
        for hi, val in enumerate(heads):
            all_heads.append((val, li, hi))

    all_heads.sort(reverse=True)

    print(f"\n  ┌─ {hologram_name.upper()} Top-{top_k} Heads ──────────────────────┐")
    print(f"  │ {'rank':>4} {'layer':>6} {'head':>6} {'selectivity':>12}")
    for rank, (val, li, hi) in enumerate(all_heads[:top_k]):
        attn_type = ""
        print(f"  │ {rank+1:>4} L{li:>4} H{hi:>4} {val:>12.6f}")
    print(f"  └{'─'*46}┘")

    # Layer summary: mean selectivity per layer
    print(f"  │ {'layer':>6} {'mean_sel':>10} {'max_sel':>10} {'max_head':>10}")
    for li in sorted(layers):
        heads = agg["layer_head_selectivity"][li]
        mean_val = float(np.mean(heads))
        max_idx = int(np.argmax(heads))
        max_val = heads[max_idx]
        print(f"  │ L{li:>4} {mean_val:>10.6f} {max_val:>10.6f} H{max_idx:>8}")
    print()


def print_orthogonality_summary(ortho: dict):
    """Print cross-hologram head-level orthogonality."""
    names = ortho["names"]
    n = len(names)

    print(f"\n  ┌─ Head-Level Orthogonality ({ortho['vector_dims']}-dim vectors) ─────┐")

    # Correlation matrix
    print(f"\n  Pearson correlation:")
    print(f"  {'':>12}", end="")
    for name in names:
        print(f" {name[:10]:>10}", end="")
    print()
    for i, ni in enumerate(names):
        print(f"  {ni[:12]:>12}", end="")
        for j in range(n):
            print(f" {ortho['correlation_matrix'][i][j]:>10.3f}", end="")
        print()

    # Cosine matrix
    print(f"\n  Cosine similarity:")
    print(f"  {'':>12}", end="")
    for name in names:
        print(f" {name[:10]:>10}", end="")
    print()
    for i, ni in enumerate(names):
        print(f"  {ni[:12]:>12}", end="")
        for j in range(n):
            print(f" {ortho['cosine_matrix'][i][j]:>10.3f}", end="")
        print()

    # Jaccard top-20 matrix
    print(f"\n  Jaccard similarity (top-20 heads):")
    print(f"  {'':>12}", end="")
    for name in names:
        print(f" {name[:10]:>10}", end="")
    print()
    for i, ni in enumerate(names):
        print(f"  {ni[:12]:>12}", end="")
        for j in range(n):
            print(f" {ortho['jaccard_top20_matrix'][i][j]:>10.3f}", end="")
        print()

    print(f"  └{'─'*72}┘")


def print_binding_i_summary(result: dict):
    """Print binding ↔ I combinator analysis."""
    print(f"\n  ┌─ Binding ↔ Combinator Overlap ──────────────────────┐")
    print(f"  │ Prediction: Jaccard(binding,I) >> Jaccard(binding,K/B/C)")
    print(f"  │")
    print(f"  │ {'metric':>20} {'K':>10} {'I':>10} {'B':>10} {'C':>10}")

    jaccard = result["jaccard_binding_vs_combinator"]
    cosine = result["cosine_binding_vs_combinator"]
    corr = result["correlation_binding_vs_combinator"]

    # Handle both 2-key (K,B only) and 4-key combinator sets
    keys = sorted(jaccard.keys())

    print(f"  │ {'Jaccard(top-20)':>20}", end="")
    for k in keys:
        print(f" {jaccard[k]:>10.3f}", end="")
    print()
    print(f"  │ {'Cosine':>20}", end="")
    for k in keys:
        print(f" {cosine[k]:>10.3f}", end="")
    print()
    print(f"  │ {'Correlation':>20}", end="")
    for k in keys:
        print(f" {corr[k]:>10.3f}", end="")
    print()

    # Verdict
    if "I" in jaccard and "K" in jaccard:
        i_val = jaccard["I"]
        others = [jaccard[k] for k in keys if k != "I"]
        if others and i_val > max(others) * 1.3:
            verdict = "CONFIRMED: binding heads overlap with I more than K/B/C"
        elif others and i_val > max(others):
            verdict = "WEAK: binding-I overlap slightly higher than others"
        else:
            verdict = "NOT CONFIRMED: binding does not preferentially overlap with I"
    else:
        # Only K and B available from COMBINATOR_PROBES
        verdict = "PARTIAL: only K and B combinators available (need I/C probes)"

    print(f"  │")
    print(f"  │ Verdict: {verdict}")
    print(f"  └{'─'*60}┘")


def print_moe_late_summary(result: dict):
    """Print late MoE gate ternary survival."""
    print(f"\n  ┌─ MoE Gate Ternary Survival (late layers) ─────────────┐")
    print(f"  │ {'layer':>6} {'frob':>8} {'eff90':>6} {'eff99':>6} "
          f"{'sign':>8} {'50%':>8} {'75%':>8}")

    for li in sorted(result["gate_stats"].keys(), key=int):
        gs = result["gate_stats"][li]
        ts = gs["ternary_survival"]
        sign_ok = "✓" if ts["sign_only"]["survived"] else "✗"
        mid_ok = "✓" if ts["mid_sparse_50"]["survived"] else "✗"
        high_ok = "✓" if ts["high_sparse_75"]["survived"] else "✗"

        print(f"  │ L{li:>4} {gs['frobenius_norm']:>8.2f} {gs['effective_rank_90']:>6} "
              f"{gs['effective_rank_99']:>6} "
              f"{ts['sign_only']['cos']:>6.3f}{sign_ok:>2} "
              f"{ts['mid_sparse_50']['cos']:>6.3f}{mid_ok:>2} "
              f"{ts['high_sparse_75']['cos']:>6.3f}{high_ok:>2}")

    print(f"  └{'─'*68}┘")


# ══════════════════════════════════════════════════════════════════
# Persistence
# ══════════════════════════════════════════════════════════════════

def _json_convert(obj):
    """JSON serializer for numpy types."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Not JSON serializable: {type(obj)}")


def save_results(all_results: dict, output_dir: Path, label: str = ""):
    """Save results to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Main results file
    main_path = output_dir / "hologram_heads_results.json"
    main_path.write_text(
        json.dumps(all_results, indent=2, default=_json_convert)
    )
    print(f"  💾 Results: {main_path}", file=sys.stderr)

    # Per-analysis snapshot
    if label:
        snap_path = output_dir / f"analysis_{label}.json"
        data = all_results.get(label, {})
        if data:
            snap_path.write_text(
                json.dumps(data, indent=2, default=_json_convert)
            )
            print(f"  💾 Snapshot: {snap_path}", file=sys.stderr)

    # Save head vectors as npz for downstream analysis
    head_vecs = {}
    profiles = all_results.get("head_profiles", {})
    for hname, profile in profiles.items():
        if "head_vector" in profile:
            head_vecs[hname] = np.array(profile["head_vector"])
    if head_vecs:
        npz_path = output_dir / "head_selectivity_vectors.npz"
        np.savez_compressed(str(npz_path), **head_vecs)
        print(f"  💾 Head vectors: {npz_path}", file=sys.stderr)


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Head-level hologram probe — resolving angle multiplexing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Analysis modes:
  heads      Per-head selectivity for all holograms + cross-hologram orthogonality
  binding_i  Binding ↔ I combinator overlap analysis
  moe_late   MoE gate ternary survival at late layers (L31-L39)

Examples:
  uv run python scripts/explore/probe_hologram_heads.py
  uv run python scripts/explore/probe_hologram_heads.py --analysis heads --quick
  uv run python scripts/explore/probe_hologram_heads.py --analysis binding_i,moe_late
""",
    )
    parser.add_argument("--analysis", type=str, default="all",
                        help="Comma-separated analysis modes (default: all)")
    parser.add_argument("--model", type=str, choices=list(MODELS.keys()),
                        default="qwen36", help="Model to probe")
    parser.add_argument("--device", type=str, default="mps")
    parser.add_argument("--quick", action="store_true",
                        help="Fewer probe pairs, faster")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    # Parse analysis modes
    if args.analysis == "all":
        selected = ALL_ANALYSES[:]
    else:
        selected = [a.strip() for a in args.analysis.split(",")]
        for a in selected:
            if a not in ALL_ANALYSES:
                print(f"Unknown analysis: {a}. Choose from: {ALL_ANALYSES}",
                      file=sys.stderr)
                sys.exit(1)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    print(f"{'═'*72}")
    print(f"  Hologram Head-Level Probe")
    print(f"  Model: {args.model}")
    print(f"  Analyses: {selected}")
    print(f"  Output: {args.output_dir}/")
    print(f"{'═'*72}")

    # Load model
    model, tokenizer = load_model(args.model, args.device)
    info = get_model_info(model)
    n_layers = info["n_layers"]
    n_heads = info["n_heads"]

    # Select measurement layers — focus on full-attention layers for head analysis
    if info.get("full_attention_layers"):
        # Hybrid model: measure at full-attention layers (where heads are cleanly separable)
        measure_layers = sorted(info["full_attention_layers"])
        # Also include a couple of GatedDeltaNet layers for comparison
        linear_layers = info.get("linear_attention_layers", [])
        if linear_layers:
            measure_layers = sorted(set(
                measure_layers + [linear_layers[0], linear_layers[-1]]
            ))
    elif n_layers <= 16:
        measure_layers = list(range(n_layers))
    elif n_layers <= 32:
        measure_layers = [0, 2, 4, 8, 12, 16, 20, 24, n_layers - 1]
    else:
        measure_layers = [0, 4, 8, 16, 24, 32, 40, 48, 56, n_layers - 1]

    if args.quick:
        # In quick mode, reduce to ~half the layers
        measure_layers = measure_layers[::2]
        if measure_layers[-1] != n_layers - 1:
            measure_layers.append(n_layers - 1)

    print(f"\n  Architecture: {n_layers}L × {n_heads}H, d={info['d_model']}")
    print(f"  Head dim: {info['head_dim']}")
    print(f"  Measure layers ({len(measure_layers)}): {measure_layers}")

    all_results = {
        "model": args.model,
        "model_info": {k: v for k, v in info.items() if k != "layer_types"},
        "measure_layers": measure_layers,
        "quick": args.quick,
        "analyses": selected,
    }

    # ── Analysis 1: Head-level selectivity + orthogonality ────────
    if "heads" in selected:
        print(f"\n{'─'*72}")
        print(f"  Analysis 1: Head-Level Selectivity")
        print(f"{'─'*72}")

        head_profiles = {}  # hologram_name → head_vector (flattened)

        # Combinator baseline
        print(f"\n  Probing: COMBINATOR (baseline)")
        comb_head_sel = measure_head_selectivity(
            model, tokenizer, COMBINATOR_PROBES, measure_layers, info, args.quick)
        comb_agg = aggregate_head_selectivity(comb_head_sel, measure_layers, n_heads)
        head_profiles["combinator"] = comb_agg["head_vector"]
        print_head_selectivity_summary("combinator", comb_head_sel, measure_layers, n_heads)

        all_results["head_selectivity_combinator"] = {
            "per_condition": comb_head_sel,
            "aggregate": comb_agg,
        }

        # Each hologram
        for hname, probes in HOLOGRAM_PROBES.items():
            print(f"\n  Probing: {hname.upper()}")
            head_sel = measure_head_selectivity(
                model, tokenizer, probes, measure_layers, info, args.quick)
            agg = aggregate_head_selectivity(head_sel, measure_layers, n_heads)
            head_profiles[hname] = agg["head_vector"]
            print_head_selectivity_summary(hname, head_sel, measure_layers, n_heads)

            all_results[f"head_selectivity_{hname}"] = {
                "per_condition": head_sel,
                "aggregate": agg,
            }

        # Cross-hologram orthogonality at head level
        if len(head_profiles) >= 2:
            print(f"\n{'─'*72}")
            print(f"  Head-Level Cross-Hologram Orthogonality")
            print(f"{'─'*72}")

            ortho = compute_head_orthogonality(head_profiles)
            print_orthogonality_summary(ortho)
            all_results["head_orthogonality"] = ortho

        all_results["head_profiles"] = {
            name: {"head_vector": vec} for name, vec in head_profiles.items()
        }

        save_results(all_results, args.output_dir, "heads")

    # ── Analysis 2: Binding ↔ I overlap ──────────────────────────
    if "binding_i" in selected:
        print(f"\n{'─'*72}")
        print(f"  Analysis 2: Binding ↔ I Combinator Overlap")
        print(f"{'─'*72}")

        # Need binding + combinator head selectivity
        # Reuse from analysis 1 if already computed, else compute fresh
        if f"head_selectivity_binding" in all_results:
            binding_sel = all_results["head_selectivity_binding"]["per_condition"]
        else:
            print(f"\n  Probing: BINDING")
            binding_sel = measure_head_selectivity(
                model, tokenizer, HOLOGRAM_PROBES["binding"],
                measure_layers, info, args.quick)

        if "head_selectivity_combinator" in all_results:
            comb_sel = all_results["head_selectivity_combinator"]["per_condition"]
        else:
            print(f"\n  Probing: COMBINATOR")
            comb_sel = measure_head_selectivity(
                model, tokenizer, COMBINATOR_PROBES,
                measure_layers, info, args.quick)

        overlap = analyze_binding_i_overlap(
            binding_sel, comb_sel, measure_layers, info)
        print_binding_i_summary(overlap)

        # Also run per-head ternary survival on binding probes at the
        # layers that failed in atlas (L3, L7 for Qwen3.6)
        ternary_target_layers = []
        if info.get("full_attention_layers"):
            # Test the first few full-attention layers (where binding fails)
            fa = info["full_attention_layers"]
            ternary_target_layers = fa[:3]  # L3, L7, L11
        else:
            ternary_target_layers = [0, n_layers // 4, n_layers // 2]

        if ternary_target_layers:
            print(f"\n  Per-head ternary survival for binding at {ternary_target_layers}")
            head_ternary = measure_head_ternary_survival(
                model, tokenizer, HOLOGRAM_PROBES["binding"],
                ternary_target_layers, measure_layers, info, args.quick)
            overlap["head_ternary_survival"] = head_ternary

        all_results["binding_i_overlap"] = overlap
        save_results(all_results, args.output_dir, "binding_i")

    # ── Analysis 3: Late MoE gate ternary ─────────────────────────
    if "moe_late" in selected:
        print(f"\n{'─'*72}")
        print(f"  Analysis 3: Late MoE Gate Ternary Survival")
        print(f"{'─'*72}")

        if info.get("is_moe"):
            moe_late = analyze_moe_gates_late(model, info)
            print_moe_late_summary(moe_late)
            all_results["moe_gate_late"] = moe_late
            save_results(all_results, args.output_dir, "moe_late")
        else:
            print(f"  ⚠ Not an MoE model — skipping gate analysis")

    # ── Final save ────────────────────────────────────────────────
    save_results(all_results, args.output_dir)

    print(f"\n{'═'*72}")
    print(f"  Done. Results: {args.output_dir}/")
    print(f"{'═'*72}")


if __name__ == "__main__":
    main()
