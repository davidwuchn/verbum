#!/usr/bin/env python3
"""Factual Indexing Probe — HOW does Q (the beam) index into ternary plates?

Extends probe_factual_recall.py. After confirming that extracted plates carry
factual knowledge (session 104), this probe instruments the MECHANISM:

  Beta reduction: (λx.body)(arg) → body[x := arg]
  Attention:      softmax(Q · K^T / √d) · V
  Indexing:       Q direction determines WHICH stored pattern is retrieved

Four analyses:
  A) Q DIRECTION ANALYSIS — What do learned Q vectors look like for factual prompts?
     Do category-similar facts produce similar Q? (typed indexing = similar β-functions
     reading same hologram region)

  B) PER-LAYER INDEXING — Which layer does fact retrieval happen in?
     Ablate Q per-layer → measure recall drop → localize the indexing layer.

  C) ATTENTION PATTERN TRACING — Where does the beam point?
     Full attention distributions for factual prompts. Extracted vs random sharpness.
     Sharp attention = selective Bragg readout. Diffuse = failed indexing.

  D) CROSS-FACT Q SIMILARITY STRUCTURE — Is Q-space organized by type?
     Cluster Q vectors. If geography clusters separately from science, the model
     has learned typed indexing (different β-functions for different hologram regions).

The hypothesis: Q learns to construct a TYPED INDEX that addresses specific regions
of the ternary plate. Different fact categories live at different "angles" in the
plate, and Q rotates to the correct angle via progressive refinement through layers.

Usage:
    uv run python scripts/explore/probe_factual_indexing.py
    uv run python scripts/explore/probe_factual_indexing.py --train-steps 1000 --n-layers 6

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path
from collections import defaultdict

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoTokenizer

# Reuse architecture from extraction scripts
sys.path.insert(0, str(Path(__file__).parent))
from extract_and_train import (
    ExtractedModel, ExtractedLayer, ExtractedAttention, TernaryFrozen,
    SimpleDataLoader, extract_signs,
    D_MODEL, N_HEADS, N_KV_HEADS, HEAD_DIM, VOCAB_SIZE,
)

DATA_DIR = Path("/Users/mwhitford/data/fractal-bitnet/shards-qwen3")
OUTPUT_DIR = Path("results/holographic-extraction")


# ══════════════════════════════════════════════════════════════════
# Factual probes — organized by category for typed-indexing analysis
# ══════════════════════════════════════════════════════════════════

FACTUAL_PROBES = {
    "geography": [
        {"prompt": "The capital of France is", "answer": " Paris"},
        {"prompt": "The capital of Japan is", "answer": " Tokyo"},
        {"prompt": "The capital of Germany is", "answer": " Berlin"},
        {"prompt": "The capital of Italy is", "answer": " Rome"},
        {"prompt": "The capital of Spain is", "answer": " Madrid"},
        {"prompt": "The capital of Russia is", "answer": " Moscow"},
        {"prompt": "The capital of China is", "answer": " Beijing"},
        {"prompt": "The capital of Australia is", "answer": " Canberra"},
        {"prompt": "The largest ocean is the", "answer": " Pacific"},
        {"prompt": "The longest river in the world is the", "answer": " Nile"},
        {"prompt": "The highest mountain in the world is Mount", "answer": " Everest"},
        {"prompt": "The largest continent is", "answer": " Asia"},
    ],
    "science": [
        {"prompt": "Water freezes at zero degrees", "answer": " Celsius"},
        {"prompt": "The speed of light is approximately 300,000 kilometers per", "answer": " second"},
        {"prompt": "The chemical symbol for gold is", "answer": " Au"},
        {"prompt": "DNA stands for deoxyribonucleic", "answer": " acid"},
        {"prompt": "The closest star to Earth is the", "answer": " Sun"},
        {"prompt": "Gravity was described by Isaac", "answer": " Newton"},
        {"prompt": "The theory of relativity was developed by Albert", "answer": " Einstein"},
        {"prompt": "Photosynthesis converts sunlight into", "answer": " energy"},
        {"prompt": "The chemical formula for table salt is Na", "answer": "Cl"},
        {"prompt": "Electrons carry a negative electric", "answer": " charge"},
    ],
    "culture": [
        {"prompt": "Shakespeare wrote Romeo and", "answer": " Juliet"},
        {"prompt": "The Mona Lisa was painted by Leonardo da", "answer": " Vinci"},
        {"prompt": "The Great Wall is located in", "answer": " China"},
        {"prompt": "The Eiffel Tower is in", "answer": " Paris"},
        {"prompt": "The Colosseum is in", "answer": " Rome"},
        {"prompt": "Beethoven composed the Moonlight", "answer": " Son"},
        {"prompt": "The Sistine Chapel was painted by", "answer": " Michel"},
        {"prompt": "The Odyssey was written by", "answer": " Homer"},
    ],
    "math": [
        {"prompt": "Two plus two equals", "answer": " four"},
        {"prompt": "The square root of 144 is", "answer": " 12"},
        {"prompt": "Pi is approximately 3.14", "answer": "15"},
        {"prompt": "A triangle has three", "answer": " sides"},
        {"prompt": "A hexagon has six", "answer": " sides"},
        {"prompt": "The derivative of x squared is", "answer": " 2"},
        {"prompt": "Ten multiplied by ten equals", "answer": " one"},
        {"prompt": "A right angle measures exactly", "answer": " 90"},
    ],
    "common": [
        {"prompt": "The Earth orbits the", "answer": " Sun"},
        {"prompt": "There are 24 hours in a", "answer": " day"},
        {"prompt": "There are 365 days in a", "answer": " year"},
        {"prompt": "The human body has 206", "answer": " bones"},
        {"prompt": "Oxygen is essential for", "answer": " breathing"},
        {"prompt": "The color of the sky is typically", "answer": " blue"},
        {"prompt": "Ice is the solid form of", "answer": " water"},
        {"prompt": "The opposite of hot is", "answer": " cold"},
    ],
}


def flatten_probes() -> list[dict]:
    """Flatten category dict into list with category labels."""
    flat = []
    for category, probes in FACTUAL_PROBES.items():
        for probe in probes:
            flat.append({**probe, "category": category})
    return flat


# ══════════════════════════════════════════════════════════════════
# Hooked model — captures Q vectors and attention patterns per layer
# ══════════════════════════════════════════════════════════════════


class HookedExtractedAttention(nn.Module):
    """ExtractedAttention with hooks to capture Q and attention weights."""

    def __init__(self, base_attn: ExtractedAttention):
        super().__init__()
        self.base = base_attn
        self.n_heads = base_attn.n_heads
        self.n_kv_heads = base_attn.n_kv_heads
        self.head_dim = base_attn.head_dim
        self.n_kv_groups = base_attn.n_kv_groups

        # Storage for captured activations
        self.captured_q: torch.Tensor | None = None
        self.captured_attn_weights: torch.Tensor | None = None
        self.capture_enabled = False

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, L, _ = x.shape

        q = self.base.q_proj(x).view(B, L, self.n_heads, self.head_dim).transpose(1, 2)
        k = self.base.k_proj(x).view(B, L, self.n_kv_heads, self.head_dim).transpose(1, 2)
        v = self.base.v_proj(x).view(B, L, self.n_kv_heads, self.head_dim).transpose(1, 2)

        # GQA expand
        if self.n_kv_groups > 1:
            k = k.repeat_interleave(self.n_kv_groups, dim=1)
            v = v.repeat_interleave(self.n_kv_groups, dim=1)

        if self.capture_enabled:
            # Store Q vector at last position (the prediction position)
            self.captured_q = q[:, :, -1, :].detach().cpu()  # (B, n_heads, head_dim)

            # Compute attention weights manually for capture
            scale = self.head_dim ** -0.5
            attn_weights = torch.matmul(q, k.transpose(-2, -1)) * scale

            # Causal mask
            causal_mask = torch.triu(
                torch.ones(L, L, dtype=torch.bool, device=x.device), diagonal=1
            )
            attn_weights = attn_weights.masked_fill(causal_mask.unsqueeze(0).unsqueeze(0), float('-inf'))
            attn_weights = F.softmax(attn_weights, dim=-1)

            # Store attention from last position to all others
            self.captured_attn_weights = attn_weights[:, :, -1, :].detach().cpu()  # (B, n_heads, L)

            # Compute output
            attn_out = torch.matmul(attn_weights, v)
        else:
            # Use efficient SDPA (no capture)
            attn_out = F.scaled_dot_product_attention(q, k, v, is_causal=True)

        attn_out = attn_out.transpose(1, 2).contiguous().view(B, L, -1)
        return self.base.o_proj(attn_out)


class HookedExtractedModel(nn.Module):
    """Wraps ExtractedModel to capture Q and attention at every layer."""

    def __init__(self, base_model: ExtractedModel):
        super().__init__()
        self.embed = base_model.embed
        self.norm = base_model.norm
        self.lm_head = base_model.lm_head

        # Replace attention modules with hooked versions
        self.layers = nn.ModuleList()
        self.hooked_attns: list[HookedExtractedAttention] = []

        for layer in base_model.layers:
            hooked_attn = HookedExtractedAttention(layer.attn)
            self.hooked_attns.append(hooked_attn)

            # Create new layer with hooked attention
            new_layer = nn.Module()
            new_layer.input_norm = layer.input_norm
            new_layer.attn = hooked_attn
            new_layer.post_attn_norm = layer.post_attn_norm
            new_layer.ffn = layer.ffn
            # Manual forward
            self.layers.append(new_layer)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.embed(x)
        for layer in self.layers:
            h = h + layer.attn(layer.input_norm(h))
            h = h + layer.ffn(layer.post_attn_norm(h))
        h = self.norm(h)
        return self.lm_head(h)

    def set_capture(self, enabled: bool):
        for attn in self.hooked_attns:
            attn.capture_enabled = enabled

    def get_captured_q(self) -> list[torch.Tensor]:
        """Get Q vectors from all layers. Returns list of (B, n_heads, head_dim)."""
        return [attn.captured_q for attn in self.hooked_attns]

    def get_captured_attn(self) -> list[torch.Tensor]:
        """Get attention weights from all layers. Returns list of (B, n_heads, seq_len)."""
        return [attn.captured_attn_weights for attn in self.hooked_attns]


# ══════════════════════════════════════════════════════════════════
# Analysis A: Q Direction Analysis
# ══════════════════════════════════════════════════════════════════


def analyze_q_directions(
    model: HookedExtractedModel,
    probes: list[dict],
    tokenizer,
    device: str,
    label: str,
) -> dict:
    """Capture Q vectors for all factual prompts, analyze structure.

    Key questions:
    - Do same-category facts produce similar Q vectors? (typed indexing)
    - Which layers show strongest category clustering? (indexing layer)
    - What is the effective dimensionality of factual Q-space? (index capacity)
    """
    model.eval()
    model.set_capture(True)
    n_layers = len(model.hooked_attns)

    # Collect Q vectors per probe per layer
    # Shape: per_layer_qs[layer_idx] = list of (n_heads, head_dim) per probe
    per_layer_qs = [[] for _ in range(n_layers)]
    categories = []

    for probe in probes:
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)

        with torch.no_grad():
            _ = model(input_ids)

        captured = model.get_captured_q()
        for li, q in enumerate(captured):
            # q shape: (1, n_heads, head_dim) — flatten to (n_heads * head_dim,)
            per_layer_qs[li].append(q[0].reshape(-1).numpy())

        categories.append(probe["category"])

    model.set_capture(False)

    # ── Compute similarity structure per layer ──
    category_names = list(FACTUAL_PROBES.keys())
    n_probes = len(probes)
    results = {"label": label, "n_probes": n_probes, "n_layers": n_layers, "layers": []}

    for li in range(n_layers):
        qs = np.array(per_layer_qs[li])  # (n_probes, n_heads*head_dim)

        # Normalize for cosine similarity
        norms = np.linalg.norm(qs, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-8)
        qs_normed = qs / norms

        # Full cosine similarity matrix
        cos_sim = qs_normed @ qs_normed.T  # (n_probes, n_probes)

        # Within-category vs between-category similarity
        within_sims = []
        between_sims = []
        per_category_within = defaultdict(list)

        for i in range(n_probes):
            for j in range(i + 1, n_probes):
                sim = cos_sim[i, j]
                if categories[i] == categories[j]:
                    within_sims.append(sim)
                    per_category_within[categories[i]].append(sim)
                else:
                    between_sims.append(sim)

        # Effective dimensionality (participation ratio of singular values)
        _, S, _ = np.linalg.svd(qs_normed, full_matrices=False)
        S_sq = S ** 2
        S_sq_norm = S_sq / S_sq.sum()
        participation_ratio = 1.0 / (S_sq_norm ** 2).sum()

        # Variance explained by top-k components
        cumvar = np.cumsum(S_sq) / S_sq.sum()
        dim_90 = int(np.searchsorted(cumvar, 0.9)) + 1
        dim_95 = int(np.searchsorted(cumvar, 0.95)) + 1
        dim_99 = int(np.searchsorted(cumvar, 0.99)) + 1

        layer_result = {
            "layer_idx": li,
            "mean_within_sim": float(np.mean(within_sims)) if within_sims else 0,
            "mean_between_sim": float(np.mean(between_sims)) if between_sims else 0,
            "clustering_ratio": (float(np.mean(within_sims)) / float(np.mean(between_sims))
                                 if between_sims and np.mean(between_sims) > 0 else 0),
            "per_category_within": {
                cat: float(np.mean(sims)) for cat, sims in per_category_within.items()
            },
            "effective_dim": float(participation_ratio),
            "dim_90_pct": dim_90,
            "dim_95_pct": dim_95,
            "dim_99_pct": dim_99,
            "q_magnitude_mean": float(np.mean(norms)),
            "q_magnitude_std": float(np.std(norms)),
        }
        results["layers"].append(layer_result)

    return results


# ══════════════════════════════════════════════════════════════════
# Analysis B: Per-Layer Indexing Decomposition
# ══════════════════════════════════════════════════════════════════


def analyze_per_layer_indexing(
    model: HookedExtractedModel,
    probes: list[dict],
    tokenizer,
    device: str,
    label: str,
) -> dict:
    """Ablate Q per-layer to find where indexing happens.

    For each layer L:
      - Zero Q at layer L only → measure recall drop (how much does L contribute?)
      - Zero Q at all layers EXCEPT L → measure recall (can L alone index?)

    Recall measured as mean log-prob of correct answer token.
    """
    model.eval()
    model.set_capture(False)
    n_layers = len(model.layers)

    # First: baseline recall (no ablation)
    baseline_logprobs = _measure_recall(model, probes, tokenizer, device)
    baseline_mean = float(np.mean(baseline_logprobs))

    # Per-layer ablation: zero Q at layer L
    zero_one_results = []  # zero one layer at a time
    only_one_results = []  # keep only one layer's Q

    for target_layer in range(n_layers):
        # ── Zero Q at target layer ──
        # Save original Q weight
        q_weight = model.hooked_attns[target_layer].base.q_proj.weight.data.clone()
        model.hooked_attns[target_layer].base.q_proj.weight.data.zero_()

        logprobs = _measure_recall(model, probes, tokenizer, device)
        drop = baseline_mean - float(np.mean(logprobs))

        zero_one_results.append({
            "layer": target_layer,
            "mean_logprob": float(np.mean(logprobs)),
            "drop_from_baseline": drop,
            "relative_drop": drop / abs(baseline_mean) if baseline_mean != 0 else 0,
        })

        # Restore
        model.hooked_attns[target_layer].base.q_proj.weight.data = q_weight

        # ── Keep ONLY target layer Q, zero all others ──
        saved_weights = []
        for li in range(n_layers):
            saved_weights.append(model.hooked_attns[li].base.q_proj.weight.data.clone())
            if li != target_layer:
                model.hooked_attns[li].base.q_proj.weight.data.zero_()

        logprobs = _measure_recall(model, probes, tokenizer, device)
        only_one_results.append({
            "layer": target_layer,
            "mean_logprob": float(np.mean(logprobs)),
            "recall_fraction": float(np.mean(logprobs)) / baseline_mean if baseline_mean != 0 else 0,
        })

        # Restore all
        for li in range(n_layers):
            model.hooked_attns[li].base.q_proj.weight.data = saved_weights[li]

    return {
        "label": label,
        "baseline_mean_logprob": baseline_mean,
        "zero_one_layer": zero_one_results,
        "only_one_layer": only_one_results,
    }


def _measure_recall(model, probes, tokenizer, device) -> list[float]:
    """Measure log-prob of correct answer for all probes."""
    model.eval()
    logprobs = []

    for probe in probes:
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
        answer_ids = tokenizer.encode(probe["answer"], add_special_tokens=False)
        if not answer_ids:
            logprobs.append(float('-inf'))
            continue
        target_id = answer_ids[0]

        with torch.no_grad():
            logits = model(input_ids)
            log_probs = F.log_softmax(logits[0, -1, :], dim=-1)
            logprobs.append(log_probs[target_id].item())

    return logprobs


# ══════════════════════════════════════════════════════════════════
# Analysis C: Attention Pattern Tracing
# ══════════════════════════════════════════════════════════════════


def analyze_attention_patterns(
    model: HookedExtractedModel,
    probes: list[dict],
    tokenizer,
    device: str,
    label: str,
) -> dict:
    """Trace attention patterns for factual prompts.

    For each fact at each layer:
    - Attention entropy (sharp = selective Bragg readout, diffuse = failed index)
    - Position of max attention (where does the beam point?)
    - Whether attention peaks at semantically relevant tokens (entity name)
    """
    model.eval()
    model.set_capture(True)
    n_layers = len(model.hooked_attns)

    per_layer_entropy = [[] for _ in range(n_layers)]
    per_layer_max_attn = [[] for _ in range(n_layers)]
    per_layer_top5_attn_mass = [[] for _ in range(n_layers)]

    probe_details = []

    for probe in probes:
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
        seq_len = input_ids.shape[1]
        tokens = tokenizer.convert_ids_to_tokens(input_ids[0])

        with torch.no_grad():
            _ = model(input_ids)

        captured_attn = model.get_captured_attn()

        probe_layers = []
        for li, attn_w in enumerate(captured_attn):
            # attn_w: (1, n_heads, seq_len) — attention from last position
            attn_w = attn_w[0]  # (n_heads, seq_len)

            # Average across heads for summary
            mean_attn = attn_w.mean(dim=0).numpy()  # (seq_len,)

            # Entropy of mean attention
            # Clip for numerical stability
            mean_attn_clipped = np.clip(mean_attn, 1e-10, 1.0)
            entropy = -np.sum(mean_attn_clipped * np.log2(mean_attn_clipped))
            max_entropy = np.log2(seq_len) if seq_len > 1 else 1.0

            # Position of max attention
            max_pos = int(np.argmax(mean_attn))

            # Mass in top-5 positions
            top5_idx = np.argsort(mean_attn)[-5:]
            top5_mass = float(mean_attn[top5_idx].sum())

            per_layer_entropy[li].append(entropy)
            per_layer_max_attn[li].append(max_pos)
            per_layer_top5_attn_mass[li].append(top5_mass)

            probe_layers.append({
                "entropy": float(entropy),
                "entropy_ratio": float(entropy / max_entropy) if max_entropy > 0 else 0,
                "max_attn_pos": max_pos,
                "max_attn_token": tokens[max_pos] if max_pos < len(tokens) else "?",
                "top5_mass": top5_mass,
                "max_attn_value": float(mean_attn[max_pos]),
            })

        probe_details.append({
            "prompt": probe["prompt"],
            "category": probe["category"],
            "seq_len": seq_len,
            "layers": probe_layers,
        })

    model.set_capture(False)

    # Summary per layer
    layer_summary = []
    for li in range(n_layers):
        layer_summary.append({
            "layer": li,
            "mean_entropy": float(np.mean(per_layer_entropy[li])),
            "std_entropy": float(np.std(per_layer_entropy[li])),
            "mean_top5_mass": float(np.mean(per_layer_top5_attn_mass[li])),
            "std_top5_mass": float(np.std(per_layer_top5_attn_mass[li])),
        })

    return {
        "label": label,
        "layer_summary": layer_summary,
        "probe_details": probe_details,
    }


# ══════════════════════════════════════════════════════════════════
# Analysis D: Cross-Fact Q Similarity Structure
# ══════════════════════════════════════════════════════════════════


def analyze_q_clustering(
    model: HookedExtractedModel,
    probes: list[dict],
    tokenizer,
    device: str,
    label: str,
) -> dict:
    """Spectral analysis of Q-space structure across facts.

    Key question: does Q-space have TYPE structure?
    If yes → the model has learned categorical indexing (typed beta reduction).
    If no → flat addressing, each fact gets its own unique Q direction.
    """
    model.eval()
    model.set_capture(True)
    n_layers = len(model.hooked_attns)

    # Collect ALL Q vectors: one per (probe, layer)
    per_layer_qs = [[] for _ in range(n_layers)]
    categories = [p["category"] for p in probes]
    category_names = list(FACTUAL_PROBES.keys())

    for probe in probes:
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
        with torch.no_grad():
            _ = model(input_ids)
        captured = model.get_captured_q()
        for li, q in enumerate(captured):
            per_layer_qs[li].append(q[0].reshape(-1).numpy())

    model.set_capture(False)

    results = {"label": label, "layers": []}

    for li in range(n_layers):
        qs = np.array(per_layer_qs[li])  # (n_probes, q_dim)
        n = qs.shape[0]

        # Cosine similarity matrix
        norms = np.linalg.norm(qs, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-8)
        qs_normed = qs / norms
        cos_sim = qs_normed @ qs_normed.T

        # Category-level similarity: mean sim between all pairs within each category pair
        cat_sim_matrix = {}
        for ci, cat_i in enumerate(category_names):
            idx_i = [k for k, c in enumerate(categories) if c == cat_i]
            for cj, cat_j in enumerate(category_names):
                idx_j = [k for k, c in enumerate(categories) if c == cat_j]
                sims = []
                for ii in idx_i:
                    for jj in idx_j:
                        if ii != jj:
                            sims.append(cos_sim[ii, jj])
                cat_sim_matrix[f"{cat_i}_{cat_j}"] = float(np.mean(sims)) if sims else 0

        # Category separation score: within / between diagonal ratio
        within_scores = []
        between_scores = []
        for ci, cat_i in enumerate(category_names):
            within_scores.append(cat_sim_matrix[f"{cat_i}_{cat_i}"])
            for cj, cat_j in enumerate(category_names):
                if ci != cj:
                    between_scores.append(cat_sim_matrix[f"{cat_i}_{cat_j}"])

        separation = (float(np.mean(within_scores)) / float(np.mean(between_scores))
                      if between_scores and np.mean(between_scores) > 0 else 0)

        # Per-head analysis: which heads are most category-selective?
        # Reshape Q vectors back to (n_probes, n_heads, head_dim)
        qs_by_head = qs.reshape(n, N_HEADS, HEAD_DIM)

        # For each head, compute category separation
        head_separations = []
        for h in range(N_HEADS):
            head_qs = qs_by_head[:, h, :]  # (n_probes, head_dim)
            h_norms = np.linalg.norm(head_qs, axis=1, keepdims=True)
            h_norms = np.maximum(h_norms, 1e-8)
            h_normed = head_qs / h_norms
            h_cos = h_normed @ h_normed.T

            h_within = []
            h_between = []
            for i in range(n):
                for j in range(i + 1, n):
                    if categories[i] == categories[j]:
                        h_within.append(h_cos[i, j])
                    else:
                        h_between.append(h_cos[i, j])

            h_sep = (float(np.mean(h_within)) / float(np.mean(h_between))
                     if h_between and np.mean(h_between) > 0 else 0)
            head_separations.append(h_sep)

        # Top-5 most category-selective heads
        top_heads = sorted(range(N_HEADS), key=lambda h: head_separations[h], reverse=True)[:5]

        results["layers"].append({
            "layer": li,
            "category_sim_matrix": cat_sim_matrix,
            "mean_within_sim": float(np.mean(within_scores)),
            "mean_between_sim": float(np.mean(between_scores)),
            "separation_ratio": separation,
            "top_selective_heads": [
                {"head": h, "separation": head_separations[h]} for h in top_heads
            ],
            "mean_head_separation": float(np.mean(head_separations)),
            "max_head_separation": float(np.max(head_separations)),
        })

    return results


# ══════════════════════════════════════════════════════════════════
# Training (reused from probe_factual_recall.py)
# ══════════════════════════════════════════════════════════════════


def train_model_quick(
    model, train_loader, n_steps: int, lr: float, device: str, label: str,
) -> list[dict]:
    """Train model, return loss history."""
    model = model.to(device)
    trainable_params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable_params, lr=lr, weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=n_steps)

    history = []
    t0 = time.time()
    for step in range(1, n_steps + 1):
        model.train()
        input_ids, targets = train_loader.next_batch()
        input_ids = input_ids.to(device)
        targets = targets.to(device)

        logits = model(input_ids)
        loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(trainable_params, 1.0)
        optimizer.step()
        scheduler.step()

        if step % 100 == 0 or step == 1:
            elapsed = time.time() - t0
            tok_per_sec = step * 2 * 256 / elapsed
            history.append({"step": step, "loss": loss.item(), "tok_per_sec": tok_per_sec})
            print(f"  [{label}] step {step:>4} | loss {loss.item():.4f} | "
                  f"{tok_per_sec:.0f} tok/s", file=sys.stderr)

    return history


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(description="Factual indexing probe")
    parser.add_argument("--source", default="Qwen/Qwen3-14B")
    parser.add_argument("--train-steps", type=int, default=500)
    parser.add_argument("--n-layers", type=int, default=4)
    parser.add_argument("--layer-stride", type=int, default=10)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--skip-training", action="store_true",
                        help="Skip training (analyze untrained models)")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    layer_indices = list(range(0, 40, args.layer_stride))[:args.n_layers]
    probes = flatten_probes()

    tokenizer = AutoTokenizer.from_pretrained(args.source)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"\n{'═'*70}", file=sys.stderr)
    print(f"  FACTUAL INDEXING PROBE — How does Q index into ternary plates?", file=sys.stderr)
    print(f"{'═'*70}", file=sys.stderr)
    print(f"  Source:     {args.source}", file=sys.stderr)
    print(f"  Layers:     {layer_indices} (stride={args.layer_stride})", file=sys.stderr)
    print(f"  Train:      {args.train_steps} steps", file=sys.stderr)
    print(f"  Probes:     {len(probes)} facts in {len(FACTUAL_PROBES)} categories", file=sys.stderr)
    print(f"  Categories: {list(FACTUAL_PROBES.keys())}", file=sys.stderr)
    print(f"{'═'*70}\n", file=sys.stderr)

    # ══ Phase 1: Extract signs ═══════════════════════════════════
    print("Phase 1: Extracting signs from source model...", file=sys.stderr)
    t0 = time.time()
    extracted_signs = extract_signs(args.source, layer_indices, device=args.device)
    intermediate = extracted_signs[0]["gate"].shape[0]
    print(f"  Done in {time.time()-t0:.1f}s (intermediate={intermediate})\n", file=sys.stderr)

    # ══ Phase 2: Build models ════════════════════════════════════
    print("Phase 2: Building extracted + random models...", file=sys.stderr)

    model_extracted = ExtractedModel(
        n_layers=len(layer_indices),
        d_model=D_MODEL, n_heads=N_HEADS, n_kv_heads=N_KV_HEADS,
        head_dim=HEAD_DIM, intermediate=intermediate,
        vocab_size=VOCAB_SIZE, layer_signs=extracted_signs,
    )

    model_random = ExtractedModel(
        n_layers=len(layer_indices),
        d_model=D_MODEL, n_heads=N_HEADS, n_kv_heads=N_KV_HEADS,
        head_dim=HEAD_DIM, intermediate=intermediate,
        vocab_size=VOCAB_SIZE, layer_signs=None,
    )

    params = model_extracted.count_params()
    print(f"  {params['trainable']/1e6:.1f}M trainable, "
          f"{params['frozen_ternary']/1e6:.1f}M frozen ternary\n", file=sys.stderr)

    # ══ Phase 3: Train both ══════════════════════════════════════
    if not args.skip_training:
        print("Phase 3: Training models...", file=sys.stderr)

        train_loader_a = SimpleDataLoader(DATA_DIR, 2, 256, shard_start=0, shard_end=4, seed=42)
        hist_e = train_model_quick(model_extracted, train_loader_a, args.train_steps,
                                   args.lr, args.device, "EXTRACTED")

        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()

        train_loader_b = SimpleDataLoader(DATA_DIR, 2, 256, shard_start=0, shard_end=4, seed=42)
        hist_r = train_model_quick(model_random, train_loader_b, args.train_steps,
                                   args.lr, args.device, "RANDOM")
    else:
        print("Phase 3: SKIPPED (--skip-training)\n", file=sys.stderr)
        hist_e, hist_r = [], []

    # ══ Phase 4: Analysis ════════════════════════════════════════
    print(f"\n{'─'*70}", file=sys.stderr)
    print(f"  Phase 4: INDEXING ANALYSIS", file=sys.stderr)
    print(f"{'─'*70}\n", file=sys.stderr)

    # Wrap models with hooks
    model_extracted = model_extracted.to(args.device)
    model_random = model_random.to(args.device)
    hooked_extracted = HookedExtractedModel(model_extracted).to(args.device)
    hooked_random = HookedExtractedModel(model_random).to(args.device)

    # ── A: Q Direction Analysis ─────────────────────────────────
    print("  A) Q Direction Analysis...", file=sys.stderr)
    q_analysis_extracted = analyze_q_directions(hooked_extracted, probes, tokenizer, args.device, "extracted")
    q_analysis_random = analyze_q_directions(hooked_random, probes, tokenizer, args.device, "random")

    print(f"\n  Q Direction Results:", file=sys.stderr)
    print(f"  {'Layer':<8} {'Within(E)':>10} {'Between(E)':>11} {'Ratio(E)':>9} "
          f"{'Within(R)':>10} {'Between(R)':>11} {'Ratio(R)':>9} {'EffDim(E)':>10}", file=sys.stderr)
    print(f"  {'─'*8} {'─'*10} {'─'*11} {'─'*9} {'─'*10} {'─'*11} {'─'*9} {'─'*10}", file=sys.stderr)
    for le, lr_layer in zip(q_analysis_extracted["layers"], q_analysis_random["layers"]):
        print(f"  L{le['layer_idx']:<6} {le['mean_within_sim']:>10.4f} {le['mean_between_sim']:>11.4f} "
              f"{le['clustering_ratio']:>9.4f} "
              f"{lr_layer['mean_within_sim']:>10.4f} {lr_layer['mean_between_sim']:>11.4f} "
              f"{lr_layer['clustering_ratio']:>9.4f} "
              f"{le['effective_dim']:>10.1f}", file=sys.stderr)

    # ── B: Per-Layer Indexing ───────────────────────────────────
    print(f"\n  B) Per-Layer Indexing Decomposition...", file=sys.stderr)
    layer_index_extracted = analyze_per_layer_indexing(hooked_extracted, probes, tokenizer, args.device, "extracted")
    layer_index_random = analyze_per_layer_indexing(hooked_random, probes, tokenizer, args.device, "random")

    print(f"\n  Layer Indexing Results (EXTRACTED):", file=sys.stderr)
    print(f"  Baseline mean log-prob: {layer_index_extracted['baseline_mean_logprob']:.4f}", file=sys.stderr)
    print(f"  {'Layer':<8} {'Zero-Q Drop':>12} {'Rel Drop':>9} {'Only-Q Recall':>14} {'Recall%':>8}", file=sys.stderr)
    print(f"  {'─'*8} {'─'*12} {'─'*9} {'─'*14} {'─'*8}", file=sys.stderr)
    for z, o in zip(layer_index_extracted["zero_one_layer"], layer_index_extracted["only_one_layer"]):
        print(f"  L{z['layer']:<6} {z['drop_from_baseline']:>+12.4f} "
              f"{z['relative_drop']:>8.1%} {o['mean_logprob']:>14.4f} "
              f"{o['recall_fraction']:>7.1%}", file=sys.stderr)

    # ── C: Attention Patterns ───────────────────────────────────
    print(f"\n  C) Attention Pattern Tracing...", file=sys.stderr)
    attn_extracted = analyze_attention_patterns(hooked_extracted, probes, tokenizer, args.device, "extracted")
    attn_random = analyze_attention_patterns(hooked_random, probes, tokenizer, args.device, "random")

    print(f"\n  Attention Entropy (lower = sharper indexing):", file=sys.stderr)
    print(f"  {'Layer':<8} {'Entropy(E)':>11} {'Top5Mass(E)':>12} "
          f"{'Entropy(R)':>11} {'Top5Mass(R)':>12} {'Δ Entropy':>10}", file=sys.stderr)
    print(f"  {'─'*8} {'─'*11} {'─'*12} {'─'*11} {'─'*12} {'─'*10}", file=sys.stderr)
    for le, lr_l in zip(attn_extracted["layer_summary"], attn_random["layer_summary"]):
        delta_ent = le["mean_entropy"] - lr_l["mean_entropy"]
        print(f"  L{le['layer']:<6} {le['mean_entropy']:>11.3f} {le['mean_top5_mass']:>12.4f} "
              f"{lr_l['mean_entropy']:>11.3f} {lr_l['mean_top5_mass']:>12.4f} "
              f"{delta_ent:>+10.3f}", file=sys.stderr)

    # ── D: Q Clustering Structure ──────────────────────────────
    print(f"\n  D) Q Clustering Structure...", file=sys.stderr)
    cluster_extracted = analyze_q_clustering(hooked_extracted, probes, tokenizer, args.device, "extracted")
    cluster_random = analyze_q_clustering(hooked_random, probes, tokenizer, args.device, "random")

    print(f"\n  Category Separation (higher = more typed indexing):", file=sys.stderr)
    print(f"  {'Layer':<8} {'Sep(E)':>8} {'Within(E)':>10} {'Between(E)':>11} "
          f"{'Sep(R)':>8} {'MaxHead(E)':>11} {'MaxHead(R)':>11}", file=sys.stderr)
    print(f"  {'─'*8} {'─'*8} {'─'*10} {'─'*11} {'─'*8} {'─'*11} {'─'*11}", file=sys.stderr)
    for le, lr_l in zip(cluster_extracted["layers"], cluster_random["layers"]):
        print(f"  L{le['layer']:<6} {le['separation_ratio']:>8.4f} "
              f"{le['mean_within_sim']:>10.4f} {le['mean_between_sim']:>11.4f} "
              f"{lr_l['separation_ratio']:>8.4f} "
              f"{le['max_head_separation']:>11.4f} {lr_l['max_head_separation']:>11.4f}",
              file=sys.stderr)

    # ══ Summary ══════════════════════════════════════════════════
    print(f"\n{'═'*70}", file=sys.stderr)
    print(f"  SUMMARY — Indexing Mechanism Findings", file=sys.stderr)
    print(f"{'═'*70}", file=sys.stderr)

    # Find the most important indexing layer
    if layer_index_extracted["zero_one_layer"]:
        most_important = max(layer_index_extracted["zero_one_layer"],
                            key=lambda x: x["drop_from_baseline"])
        print(f"\n  Most important indexing layer (EXTRACTED): L{most_important['layer']} "
              f"(drop={most_important['drop_from_baseline']:+.4f})", file=sys.stderr)

    # Compare clustering extracted vs random
    if cluster_extracted["layers"]:
        max_sep_e = max(l["separation_ratio"] for l in cluster_extracted["layers"])
        max_sep_r = max(l["separation_ratio"] for l in cluster_random["layers"])
        print(f"  Max category separation: Extracted={max_sep_e:.4f}, Random={max_sep_r:.4f}", file=sys.stderr)
        if max_sep_e > max_sep_r:
            print(f"  ✅ Extracted plates induce TYPED indexing (categories cluster in Q-space)",
                  file=sys.stderr)
        else:
            print(f"  ⚠️  Random plates show similar or more clustering — investigate",
                  file=sys.stderr)

    # Compare attention sharpness
    if attn_extracted["layer_summary"] and attn_random["layer_summary"]:
        mean_ent_e = np.mean([l["mean_entropy"] for l in attn_extracted["layer_summary"]])
        mean_ent_r = np.mean([l["mean_entropy"] for l in attn_random["layer_summary"]])
        if mean_ent_e < mean_ent_r:
            print(f"  ✅ Extracted plates produce SHARPER attention (better Bragg selectivity)",
                  file=sys.stderr)
            print(f"     Mean entropy: Extracted={mean_ent_e:.3f}, Random={mean_ent_r:.3f}",
                  file=sys.stderr)
        else:
            print(f"  ⚠️  Random plates have similar/sharper attention — entropy is not the signal",
                  file=sys.stderr)

    # ══ Save results ═════════════════════════════════════════════
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "config": {
            "source_model": args.source,
            "layer_indices": layer_indices,
            "n_layers": len(layer_indices),
            "train_steps": args.train_steps,
            "n_probes": len(probes),
            "categories": list(FACTUAL_PROBES.keys()),
            "probes_per_category": {k: len(v) for k, v in FACTUAL_PROBES.items()},
        },
        "training_history": {
            "extracted": hist_e,
            "random": hist_r,
        },
        "analysis": {
            "q_directions": {
                "extracted": q_analysis_extracted,
                "random": q_analysis_random,
            },
            "per_layer_indexing": {
                "extracted": layer_index_extracted,
                "random": layer_index_random,
            },
            "attention_patterns": {
                "extracted": attn_extracted,
                "random": attn_random,
            },
            "q_clustering": {
                "extracted": cluster_extracted,
                "random": cluster_random,
            },
        },
    }

    json_path = args.output_dir / "factual_indexing_results.json"
    json_path.write_text(json.dumps(output, indent=2))
    print(f"\n  💾 Results: {json_path}", file=sys.stderr)
    print(f"{'═'*70}\n", file=sys.stderr)


if __name__ == "__main__":
    main()
