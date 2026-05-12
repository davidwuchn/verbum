#!/usr/bin/env python3
"""Probe: Do KIBC combinators exist as separable circuits in Qwen3-32B?

v11 architecture is premised on {K, I, B, C} being the natural basis
of attention-mediated composition. Earlier probes (sessions 001, 062,
077) found evidence at both 4B and 32B scales. This probe tests the
premise directly: do different attention heads specialize for different
combinators?

Method:
  For each combinator, design sentence pairs that isolate its function:
    - K (select): "The cat, not the dog, ran" vs neutral
    - I (identity): "He said hello and she said hello" vs neutral
    - B (compose): nested clauses vs flat clauses
    - C (flip): passive vs active voice (same meaning, args reordered)

  Hook all layers, capture hidden states and attention patterns.
  Measure per-head selectivity for each combinator condition.
  Identify heads that are DIFFERENTIALLY selective for one combinator.

  Additionally: capture hidden state trajectories to test whether
  the residual stream encodes combinator-like operations at the
  per-token level.

Usage:
    uv run python scripts/explore/probe_combinators.py
    uv run python scripts/explore/probe_combinators.py --model hf   # use HF cached model
    uv run python scripts/explore/probe_combinators.py --quick       # fewer probes, faster

Output: results/combinator-probe/

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import seaborn as sns
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


# ══════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════

DEFAULT_GGUF = "/Users/mwhitford/localai/models/Qwen3-32B-Q8_0.gguf"
HF_MODEL = "Qwen/Qwen3-32B"
OUTPUT_DIR = Path("results/combinator-probe")

# 32B architecture: 64 layers, 64 heads, 8 KV heads (GQA 8:1)
# head_dim = 5120/64 = 80


# ══════════════════════════════════════════════════════════════════
# Probe sentences — designed to isolate each combinator
# ══════════════════════════════════════════════════════════════════

# Each combinator has ACTIVE probes (where it's needed) and
# MATCHED CONTROL probes (similar surface form, combinator not needed).
# Selectivity = attention difference between active and control.

PROBES = {
    # ── K (select): pick one, discard alternative ──────────────
    # Active: requires selecting one referent over another
    # Control: no selection needed (single referent)
    "K": {
        "description": "Selection — choose one referent, discard alternative",
        "active": [
            "The cat, not the dog, chased the mouse across the yard.",
            "Either the president or the minister signed the treaty last week.",
            "John, rather than his brother, won the competition in the end.",
            "The red ball, not the blue one, rolled under the table slowly.",
            "Some students but not all students passed the difficult exam.",
            "The old house, unlike the new building, survived the earthquake.",
        ],
        "control": [
            "The cat chased the mouse across the yard very quickly.",
            "The president signed the treaty at the ceremony last week.",
            "John won the competition in the end with great effort.",
            "The red ball rolled under the table slowly after the push.",
            "All students passed the difficult exam with high scores.",
            "The old house survived the earthquake without any damage.",
        ],
    },

    # ── I (identity): pass through unchanged ──────────────────
    # Active: repetition, copying, anaphora resolution (same entity)
    # Control: varied content (no copying needed)
    "I": {
        "description": "Identity — forward information unchanged, copy, repeat",
        "active": [
            'He said "hello" and then she also said "hello" to everyone.',
            "The result was five. The answer is five. Five is correct.",
            "She ran quickly. She ran so quickly that nobody could catch her.",
            "The temperature is rising. The temperature keeps rising every day.",
            "First he ate the apple. Then he ate another apple after that.",
            "The plan was simple. It was simple and it worked perfectly well.",
        ],
        "control": [
            'He said "hello" and then she said "goodbye" to everyone.',
            "The result was five. The method is correct. Nothing was wrong.",
            "She ran quickly. The others walked slowly behind the group.",
            "The temperature is rising. The wind keeps shifting every day.",
            "First he ate the apple. Then he drank some water after that.",
            "The plan was simple. It was elegant and it surprised everyone.",
        ],
    },

    # ── B (compose): chain two operations ─────────────────────
    # Active: nested clauses, embedded computation, function chaining
    # Control: flat clauses (same words, no nesting)
    "B": {
        "description": "Composition — nested operations, relative clauses, chaining",
        "active": [
            "The man who the dog that the cat chased bit ran away quickly.",
            "The student who read the book that the professor recommended passed.",
            "If every teacher who knows a student that failed helps them, all improve.",
            "The company that hired the lawyer who won the case prospered greatly.",
            "She believed that he thought that the answer was obviously wrong.",
            "The key that opened the door that led to the garden was lost.",
        ],
        "control": [
            "The man ran away quickly after the incident in the park.",
            "The student passed the course with excellent marks this year.",
            "If every teacher helps struggling students then all will improve.",
            "The company prospered greatly after its successful year overall.",
            "She believed the answer was obviously wrong from the start.",
            "The key was lost somewhere in the garden behind the house.",
        ],
    },

    # ── C (flip): reorder arguments ───────────────────────────
    # Active: passive voice (args swapped vs canonical active)
    # Control: active voice (canonical argument order)
    "C": {
        "description": "Flip — argument reordering, passive voice, topicalization",
        "active": [
            "The mouse was chased by the cat through the garden quickly.",
            "The treaty was signed by the president at the formal ceremony.",
            "The book was read by every student in the advanced class.",
            "The window was broken by the ball during the afternoon game.",
            "The letter was written by Mary to her friend in another city.",
            "The cake was baked by the chef for the celebration last night.",
        ],
        "control": [
            "The cat chased the mouse through the garden very quickly.",
            "The president signed the treaty at the formal ceremony today.",
            "Every student read the book in the advanced class this term.",
            "The ball broke the window during the afternoon game outside.",
            "Mary wrote the letter to her friend in another city yesterday.",
            "The chef baked the cake for the celebration last night here.",
        ],
    },
}

# Null baseline: generic sentences with no strong combinator demand
NULL_PROBES = [
    "The sun rose over the mountains in the early morning light.",
    "Water flows downhill following the path of least resistance.",
    "The library was quiet and the shelves were full of books.",
    "Birds flew south for the winter as the leaves began to fall.",
    "The clock on the wall showed that it was nearly midnight.",
    "Clouds gathered in the sky promising rain by the afternoon.",
]


# ══════════════════════════════════════════════════════════════════
# Model loading (follows v10 probe pattern)
# ══════════════════════════════════════════════════════════════════


def load_model_gguf(gguf_path: str, device: str = "mps"):
    """Load Qwen3-32B from GGUF (Q8_0)."""
    gguf_dir = str(Path(gguf_path).parent)
    gguf_file = Path(gguf_path).name

    print(f"Loading model from {gguf_path}...", file=sys.stderr)
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        gguf_dir, gguf_file=gguf_file,
        dtype=torch.float16, device_map=device,
        trust_remote_code=True,
        attn_implementation="eager",  # required for output_attentions=True
    )
    model.eval()
    model.config.output_attentions = True

    t1 = time.time()
    print(f"Loaded GGUF in {t1-t0:.1f}s: {model.config.num_hidden_layers} layers, "
          f"d={model.config.hidden_size}", file=sys.stderr)
    return model, tokenizer


def load_model_hf(device: str = "mps"):
    """Load Qwen3-32B from HuggingFace cache."""
    print(f"Loading {HF_MODEL} from HF cache...", file=sys.stderr)
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        HF_MODEL,
        dtype=torch.float16, device_map=device,
        trust_remote_code=True,
        attn_implementation="eager",  # required for output_attentions=True
    )
    model.eval()
    model.config.output_attentions = True

    t1 = time.time()
    print(f"Loaded HF in {t1-t0:.1f}s: {model.config.num_hidden_layers} layers, "
          f"d={model.config.hidden_size}", file=sys.stderr)
    return model, tokenizer


# ══════════════════════════════════════════════════════════════════
# Hidden state capture
# ══════════════════════════════════════════════════════════════════


def capture_hidden_states(
    model, tokenizer, text: str,
    layers: list[int] | None = None,
) -> dict:
    """Run a forward pass with hooks to capture hidden states at specified layers.

    Returns:
        {
            "token_ids": list[int],
            "token_strs": list[str],
            "hidden_states": {layer_idx: np.ndarray (seq_len, d_model)},
            "n_tokens": int,
        }
    """
    config = model.config
    n_layers = config.num_hidden_layers
    if layers is None:
        # Sample: early, typing zone, mid, late
        layers = [0, 1, 4, 8, 16, 24, 28, 31, 32, 40, 48, 56, 60, 63]
        layers = [l for l in layers if l < n_layers]

    captured = {}
    hooks = []

    def make_hook(layer_idx):
        def hook_fn(module, input, output):
            # output is (hidden_states, ...) for decoder layers
            if isinstance(output, tuple):
                h = output[0]
            else:
                h = output
            captured[layer_idx] = h[0].detach().cpu().float().numpy()
        return hook_fn

    # Hook into decoder layers
    for li in layers:
        layer_module = model.model.layers[li]
        hooks.append(layer_module.register_forward_hook(make_hook(li)))

    # Tokenize and run
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    token_ids = inputs["input_ids"][0].tolist()
    token_strs = [tokenizer.decode([tid]) for tid in token_ids]

    with torch.no_grad():
        model(**inputs)

    # Clean up hooks
    for h in hooks:
        h.remove()

    return {
        "token_ids": token_ids,
        "token_strs": token_strs,
        "hidden_states": captured,
        "n_tokens": len(token_ids),
    }


def capture_attention(
    model, tokenizer, text: str,
) -> dict:
    """Run forward pass with output_attentions=True.

    Returns:
        {
            "token_ids": list[int],
            "token_strs": list[str],
            "attentions": np.ndarray (n_layers, n_heads, seq_len, seq_len),
            "n_tokens": int,
        }

    Note: For 32B with 64 layers × 64 heads, attention matrices are large.
    We capture and immediately convert to float16 numpy to manage memory.
    """
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    token_ids = inputs["input_ids"][0].tolist()
    token_strs = [tokenizer.decode([tid]) for tid in token_ids]

    with torch.no_grad():
        outputs = model(**inputs, output_attentions=True)

    # outputs.attentions: tuple of (1, n_heads, seq_len, seq_len) per layer
    attn_list = []
    for layer_attn in outputs.attentions:
        attn_list.append(layer_attn[0].cpu().half().numpy())

    attentions = np.stack(attn_list, axis=0)  # (n_layers, n_heads, seq, seq)

    return {
        "token_ids": token_ids,
        "token_strs": token_strs,
        "attentions": attentions,
        "n_tokens": len(token_ids),
    }


# ══════════════════════════════════════════════════════════════════
# Analysis: per-head selectivity for each combinator
# ══════════════════════════════════════════════════════════════════


def head_selectivity(
    active_attn: np.ndarray,
    control_attn: np.ndarray,
) -> np.ndarray:
    """Compute per-head selectivity between active and control conditions.

    Both inputs: (n_layers, n_heads, seq_len, seq_len)
    Returns: (n_layers, n_heads) — mean L2 distance per head.
    """
    min_seq = min(active_attn.shape[2], control_attn.shape[2])
    a = active_attn[:, :, :min_seq, :min_seq].astype(np.float32)
    c = control_attn[:, :, :min_seq, :min_seq].astype(np.float32)
    diff = a - c
    return np.sqrt(np.mean(diff ** 2, axis=(-2, -1)))


def compute_combinator_selectivity(
    model, tokenizer, probes: dict, null_probes: list[str],
    quick: bool = False,
) -> dict:
    """For each combinator, compute per-head selectivity.

    Returns:
        {
            "K": {"vs_control": (n_layers, n_heads), "vs_null": ...},
            "I": ...,
            "B": ...,
            "C": ...,
        }
    """
    n_layers = model.config.num_hidden_layers
    n_heads = model.config.num_attention_heads

    results = {}

    # Capture null baseline
    print("  Capturing null baseline attention...", file=sys.stderr)
    null_attns = []
    for text in (null_probes[:2] if quick else null_probes):
        cap = capture_attention(model, tokenizer, text)
        null_attns.append(cap)
        torch.mps.empty_cache() if torch.backends.mps.is_available() else None

    for comb_name, comb_data in probes.items():
        active_texts = comb_data["active"][:3] if quick else comb_data["active"]
        control_texts = comb_data["control"][:3] if quick else comb_data["control"]
        n_pairs = min(len(active_texts), len(control_texts))

        print(f"  Probing {comb_name} ({comb_data['description']})...",
              file=sys.stderr)

        # Active vs matched control
        vs_control = np.zeros((n_layers, n_heads))
        for i in range(n_pairs):
            print(f"    pair {i+1}/{n_pairs}...", file=sys.stderr)
            active_cap = capture_attention(model, tokenizer, active_texts[i])
            control_cap = capture_attention(model, tokenizer, control_texts[i])
            sel = head_selectivity(active_cap["attentions"],
                                   control_cap["attentions"])
            vs_control += sel
            torch.mps.empty_cache() if torch.backends.mps.is_available() else None
        vs_control /= n_pairs

        # Active vs null baseline
        vs_null = np.zeros((n_layers, n_heads))
        n_null_pairs = min(n_pairs, len(null_attns))
        for i in range(n_null_pairs):
            active_cap = capture_attention(model, tokenizer, active_texts[i])
            sel = head_selectivity(active_cap["attentions"],
                                   null_attns[i]["attentions"])
            vs_null += sel
            torch.mps.empty_cache() if torch.backends.mps.is_available() else None
        vs_null /= max(n_null_pairs, 1)

        # Control vs null (to see if control itself is selective)
        vs_null_control = np.zeros((n_layers, n_heads))
        for i in range(n_null_pairs):
            control_cap = capture_attention(model, tokenizer, control_texts[i])
            sel = head_selectivity(control_cap["attentions"],
                                   null_attns[i]["attentions"])
            vs_null_control += sel
            torch.mps.empty_cache() if torch.backends.mps.is_available() else None
        vs_null_control /= max(n_null_pairs, 1)

        results[comb_name] = {
            "vs_control": vs_control,
            "vs_null": vs_null,
            "vs_null_control": vs_null_control,
            "description": comb_data["description"],
        }

    return results


# ══════════════════════════════════════════════════════════════════
# Analysis: hidden state trajectory per combinator
# ══════════════════════════════════════════════════════════════════


def compute_hidden_state_analysis(
    model, tokenizer, probes: dict, quick: bool = False,
) -> dict:
    """Capture hidden states and measure per-layer representation changes.

    For each combinator's active probes, track:
    - Per-layer norm of hidden states
    - Cosine similarity between consecutive layers (transformation rate)
    - Mean representation at each layer (for cross-combinator comparison)
    """
    layers = [0, 4, 8, 16, 24, 28, 31, 32, 40, 48, 56, 60, 63]
    n_layers_captured = len(layers)

    results = {}
    for comb_name, comb_data in probes.items():
        texts = comb_data["active"][:2] if quick else comb_data["active"][:4]
        print(f"  Hidden states for {comb_name}...", file=sys.stderr)

        all_norms = []
        all_cosines = []

        for text in texts:
            cap = capture_hidden_states(model, tokenizer, text, layers=layers)
            hs = cap["hidden_states"]

            # Per-layer mean norm across tokens
            norms = {}
            for li in sorted(hs.keys()):
                norms[li] = float(np.mean(np.linalg.norm(hs[li], axis=-1)))

            # Cosine between consecutive captured layers
            cosines = {}
            sorted_layers = sorted(hs.keys())
            for j in range(len(sorted_layers) - 1):
                l1, l2 = sorted_layers[j], sorted_layers[j+1]
                # Mean-pool over tokens
                h1 = hs[l1].mean(axis=0)
                h2 = hs[l2].mean(axis=0)
                cos = float(np.dot(h1, h2) / (np.linalg.norm(h1) * np.linalg.norm(h2) + 1e-8))
                cosines[f"L{l1}→L{l2}"] = cos

            all_norms.append(norms)
            all_cosines.append(cosines)
            torch.mps.empty_cache() if torch.backends.mps.is_available() else None

        # Average across probes
        avg_norms = {}
        for li in sorted(all_norms[0].keys()):
            avg_norms[li] = float(np.mean([n[li] for n in all_norms]))

        avg_cosines = {}
        for key in all_cosines[0].keys():
            avg_cosines[key] = float(np.mean([c[key] for c in all_cosines]))

        results[comb_name] = {
            "avg_norms": avg_norms,
            "avg_cosines": avg_cosines,
            "description": comb_data["description"],
        }

    return results


# ══════════════════════════════════════════════════════════════════
# Analysis: differential selectivity (which heads prefer which combinator)
# ══════════════════════════════════════════════════════════════════


def compute_differential_selectivity(selectivity: dict) -> dict:
    """For each head, determine which combinator it's most selective for.

    Uses vs_control (active vs matched control) as the primary signal,
    since this isolates the combinator function from surface-level
    sentence differences.

    Returns:
        {
            "dominant_combinator": (n_layers, n_heads) — index of most selective combinator,
            "selectivity_matrix": (4, n_layers, n_heads) — K, I, B, C selectivity,
            "differential": (n_layers, n_heads) — max - second_max (specialization strength),
            "top_heads_per_combinator": {K: [(layer, head, score), ...], ...},
        }
    """
    comb_names = ["K", "I", "B", "C"]
    n_layers, n_heads = selectivity["K"]["vs_control"].shape

    # Stack into (4, n_layers, n_heads)
    sel_matrix = np.stack(
        [selectivity[c]["vs_control"] for c in comb_names], axis=0
    )

    # Per-head: which combinator has highest selectivity?
    dominant = np.argmax(sel_matrix, axis=0)  # (n_layers, n_heads)

    # Differential: max - second_max
    sorted_sel = np.sort(sel_matrix, axis=0)  # ascending
    differential = sorted_sel[-1] - sorted_sel[-2]  # (n_layers, n_heads)

    # Top heads per combinator
    top_heads = {}
    for ci, cname in enumerate(comb_names):
        scores = sel_matrix[ci]
        flat = scores.flatten()
        top_idx = np.argsort(flat)[-20:][::-1]  # top 20
        heads = []
        for idx in top_idx:
            layer = idx // n_heads
            head = idx % n_heads
            score = float(flat[idx])
            diff = float(differential[layer, head])
            is_dominant = int(dominant[layer, head]) == ci
            heads.append({
                "layer": int(layer), "head": int(head),
                "score": score, "differential": diff,
                "is_dominant": is_dominant,
            })
        top_heads[cname] = heads

    return {
        "dominant_combinator": dominant,
        "selectivity_matrix": sel_matrix,
        "differential": differential,
        "top_heads_per_combinator": top_heads,
    }


# ══════════════════════════════════════════════════════════════════
# Visualization
# ══════════════════════════════════════════════════════════════════


def plot_selectivity_heatmaps(selectivity: dict, output_dir: Path):
    """Per-combinator selectivity heatmaps (layer × head)."""
    comb_names = ["K", "I", "B", "C"]
    comb_labels = {
        "K": "K (select)", "I": "I (identity)",
        "B": "B (compose)", "C": "C (flip)",
    }

    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle("Per-Head Combinator Selectivity (active vs matched control)\n"
                 "Qwen3-32B — 64 layers × 64 heads",
                 fontsize=14, fontweight="bold")

    vmax = max(selectivity[c]["vs_control"].max() for c in comb_names) * 0.8

    for idx, cname in enumerate(comb_names):
        ax = axes[idx // 2][idx % 2]
        data = selectivity[cname]["vs_control"]
        im = ax.imshow(data, aspect="auto", cmap="hot",
                       interpolation="nearest", vmin=0, vmax=vmax)
        ax.set_title(f"{comb_labels[cname]}", fontsize=12, fontweight="bold")
        ax.set_xlabel("Head")
        ax.set_ylabel("Layer")
        plt.colorbar(im, ax=ax, label="L2 selectivity")

    plt.tight_layout()
    fig.savefig(output_dir / "selectivity_heatmaps.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: selectivity_heatmaps.png", file=sys.stderr)


def plot_differential_map(diff_results: dict, output_dir: Path):
    """Map showing which combinator dominates each head."""
    dominant = diff_results["dominant_combinator"]
    differential = diff_results["differential"]
    comb_names = ["K", "I", "B", "C"]
    comb_colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]  # R, B, G, O

    n_layers, n_heads = dominant.shape

    # Create RGB image
    img = np.zeros((n_layers, n_heads, 3))
    for ci, color_hex in enumerate(comb_colors):
        r, g, b = int(color_hex[1:3], 16)/255, int(color_hex[3:5], 16)/255, int(color_hex[5:7], 16)/255
        mask = dominant == ci
        # Intensity proportional to differential strength
        intensity = np.clip(differential / (differential.max() + 1e-8), 0.2, 1.0)
        img[mask, 0] = r * intensity[mask]
        img[mask, 1] = g * intensity[mask]
        img[mask, 2] = b * intensity[mask]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 10),
                                    gridspec_kw={"width_ratios": [3, 1]})

    fig.suptitle("Combinator Head Assignment — Qwen3-32B\n"
                 "Color = dominant combinator, brightness = specialization strength",
                 fontsize=14, fontweight="bold")

    ax1.imshow(img, aspect="auto", interpolation="nearest")
    ax1.set_xlabel("Head")
    ax1.set_ylabel("Layer")
    ax1.set_title("Per-head dominant combinator")

    # Legend
    for ci, cname in enumerate(comb_names):
        count = int(np.sum(dominant == ci))
        pct = count / dominant.size * 100
        ax1.plot([], [], 's', color=comb_colors[ci], markersize=10,
                 label=f"{cname}: {count} heads ({pct:.1f}%)")
    ax1.legend(loc="upper right", fontsize=10)

    # Per-layer combinator distribution
    layer_dist = np.zeros((n_layers, 4))
    for ci in range(4):
        layer_dist[:, ci] = np.sum(dominant == ci, axis=1)

    bottom = np.zeros(n_layers)
    for ci in range(4):
        ax2.barh(range(n_layers), layer_dist[:, ci], left=bottom,
                 color=comb_colors[ci], label=comb_names[ci])
        bottom += layer_dist[:, ci]
    ax2.set_xlabel("Heads per combinator")
    ax2.set_ylabel("Layer")
    ax2.set_title("Per-layer distribution")
    ax2.invert_yaxis()
    ax2.legend()

    plt.tight_layout()
    fig.savefig(output_dir / "differential_map.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: differential_map.png", file=sys.stderr)


def plot_combinator_layer_profiles(selectivity: dict, output_dir: Path):
    """Per-combinator mean selectivity by layer."""
    comb_names = ["K", "I", "B", "C"]
    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.suptitle("Combinator Selectivity by Layer — Qwen3-32B\n"
                 "Mean per-head selectivity (active vs matched control)",
                 fontsize=12, fontweight="bold")

    for ci, cname in enumerate(comb_names):
        data = selectivity[cname]["vs_control"]
        mean_by_layer = data.mean(axis=1)
        ax.plot(mean_by_layer, color=colors[ci], linewidth=2,
                label=f"{cname} — max layer: L{np.argmax(mean_by_layer)}")
        ax.fill_between(range(len(mean_by_layer)), mean_by_layer,
                        alpha=0.15, color=colors[ci])

    ax.set_xlabel("Layer")
    ax.set_ylabel("Mean selectivity (L2 distance)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_dir / "layer_profiles.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: layer_profiles.png", file=sys.stderr)


def plot_cross_combinator_correlation(selectivity: dict, output_dir: Path):
    """Correlation matrix: do different combinators use the same heads?"""
    comb_names = ["K", "I", "B", "C"]

    # Flatten selectivity to 1D per combinator
    flat = {}
    for cname in comb_names:
        flat[cname] = selectivity[cname]["vs_control"].flatten()

    # Correlation matrix
    corr = np.zeros((4, 4))
    for i, ci in enumerate(comb_names):
        for j, cj in enumerate(comb_names):
            corr[i, j] = float(np.corrcoef(flat[ci], flat[cj])[0, 1])

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(4))
    ax.set_yticks(range(4))
    ax.set_xticklabels(comb_names, fontsize=12)
    ax.set_yticklabels(comb_names, fontsize=12)

    for i in range(4):
        for j in range(4):
            ax.text(j, i, f"{corr[i,j]:.3f}", ha="center", va="center",
                    fontsize=11, fontweight="bold",
                    color="white" if abs(corr[i,j]) > 0.5 else "black")

    ax.set_title("Cross-Combinator Head Selectivity Correlation\n"
                 "High = same heads respond to both, Low = different heads",
                 fontsize=12, fontweight="bold")
    plt.colorbar(im, label="Pearson r")

    plt.tight_layout()
    fig.savefig(output_dir / "cross_combinator_correlation.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: cross_combinator_correlation.png", file=sys.stderr)


# ══════════════════════════════════════════════════════════════════
# Session-001 circuit mapping
# ══════════════════════════════════════════════════════════════════


def map_known_circuit(selectivity: dict) -> dict:
    """Map the 3-head circuit from session 001 (4B) to 32B combinator roles.

    Session 001 found on 4B:
      L1:H0  = Gate recognizer
      L24:H0 = Universal compositor (typed_apply)
      L24:H2 = Recursion head

    32B has 64 layers vs 4B's 36 layers. Proportional mapping:
      L1/36  → L1.8/64  → ~L2
      L24/36 → L42.7/64 → ~L43

    Check selectivity at these proportional positions.
    """
    # Proportional positions in 64-layer model
    mapped = {
        "L1:H0_gate_recognizer": {"4b": (1, 0), "32b_approx": (2, 0)},
        "L24:H0_compositor": {"4b": (24, 0), "32b_approx": (43, 0)},
        "L24:H2_recursion": {"4b": (24, 2), "32b_approx": (43, 2)},
    }

    comb_names = ["K", "I", "B", "C"]
    for name, positions in mapped.items():
        l32, h32 = positions["32b_approx"]
        n_layers = selectivity["K"]["vs_control"].shape[0]
        if l32 >= n_layers:
            continue
        sel_at_head = {}
        for cname in comb_names:
            sel_at_head[cname] = float(selectivity[cname]["vs_control"][l32, h32])
        mapped[name]["selectivity_32b"] = sel_at_head
        mapped[name]["dominant"] = comb_names[np.argmax([sel_at_head[c] for c in comb_names])]

    return mapped


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(
        description="KIBC combinator probe — Qwen3-32B")
    parser.add_argument("--model", choices=["gguf", "hf"], default="gguf",
                        help="Model source: gguf (Q8_0) or hf (cached fp16)")
    parser.add_argument("--gguf", default=DEFAULT_GGUF,
                        help="Path to GGUF file")
    parser.add_argument("--device", default="mps",
                        help="Device (mps, cuda, cpu)")
    parser.add_argument("--quick", action="store_true",
                        help="Fewer probes for faster results")
    parser.add_argument("--skip-hidden", action="store_true",
                        help="Skip hidden state analysis (attention only)")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Load model
    if args.model == "hf":
        model, tokenizer = load_model_hf(args.device)
    else:
        model, tokenizer = load_model_gguf(args.gguf, args.device)

    n_layers = model.config.num_hidden_layers
    n_heads = model.config.num_attention_heads
    print(f"  Model: {n_layers} layers, {n_heads} heads", file=sys.stderr)

    # ── Attention-based combinator selectivity ────────────
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  Phase 1: Attention selectivity per combinator", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    t0 = time.time()
    selectivity = compute_combinator_selectivity(
        model, tokenizer, PROBES, NULL_PROBES, quick=args.quick)
    t_attn = time.time() - t0
    print(f"  Attention analysis: {t_attn:.1f}s", file=sys.stderr)

    # ── Differential analysis ─────────────────────────────
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  Phase 2: Differential selectivity analysis", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    diff_results = compute_differential_selectivity(selectivity)

    # Print summary
    comb_names = ["K", "I", "B", "C"]
    print(f"\n  Combinator selectivity summary (vs matched control):")
    print(f"  {'Comb':>5} {'Mean':>8} {'Max':>8} {'MaxLayer':>9} {'MaxHead':>8}")
    print(f"  {'─'*5} {'─'*8} {'─'*8} {'─'*9} {'─'*8}")
    for cname in comb_names:
        data = selectivity[cname]["vs_control"]
        max_idx = np.unravel_index(np.argmax(data), data.shape)
        print(f"  {cname:>5} {data.mean():>8.5f} {data.max():>8.5f} "
              f"L{max_idx[0]:>3}      H{max_idx[1]:>3}")

    # Dominant combinator distribution
    dominant = diff_results["dominant_combinator"]
    print(f"\n  Head assignment (dominant combinator per head):")
    for ci, cname in enumerate(comb_names):
        count = int(np.sum(dominant == ci))
        pct = count / dominant.size * 100
        print(f"    {cname}: {count:>5} heads ({pct:>5.1f}%)")

    # Top heads per combinator
    for cname in comb_names:
        heads = diff_results["top_heads_per_combinator"][cname]
        dominant_heads = [h for h in heads if h["is_dominant"]][:5]
        if dominant_heads:
            print(f"\n  Top {cname}-specialized heads:")
            for h in dominant_heads:
                print(f"    L{h['layer']:>2}:H{h['head']:>2}  "
                      f"score={h['score']:.5f}  diff={h['differential']:.5f}")

    # Cross-combinator correlation
    flat = {c: selectivity[c]["vs_control"].flatten() for c in comb_names}
    print(f"\n  Cross-combinator correlation (same heads = high):")
    print(f"  {'':>5}", end="")
    for c in comb_names:
        print(f" {c:>7}", end="")
    print()
    for ci in comb_names:
        print(f"  {ci:>5}", end="")
        for cj in comb_names:
            r = float(np.corrcoef(flat[ci], flat[cj])[0, 1])
            print(f" {r:>7.3f}", end="")
        print()

    # Map session-001 circuit
    circuit_map = map_known_circuit(selectivity)
    print(f"\n  Session 001 circuit → combinator mapping (4B→32B proportional):")
    for name, data in circuit_map.items():
        if "selectivity_32b" in data:
            l, h = data["32b_approx"]
            sel = data["selectivity_32b"]
            dom = data["dominant"]
            print(f"    {name}: L{l}:H{h} → {dom} "
                  f"(K={sel['K']:.4f} I={sel['I']:.4f} "
                  f"B={sel['B']:.4f} C={sel['C']:.4f})")

    # ── Hidden state analysis (optional) ──────────────────
    hidden_results = None
    if not args.skip_hidden:
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"  Phase 3: Hidden state trajectory", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)

        t0 = time.time()
        hidden_results = compute_hidden_state_analysis(
            model, tokenizer, PROBES, quick=args.quick)
        t_hidden = time.time() - t0
        print(f"  Hidden state analysis: {t_hidden:.1f}s", file=sys.stderr)

        # Print hidden state summary
        print(f"\n  Hidden state norms by combinator (selected layers):")
        layers_show = [0, 16, 28, 32, 48, 63]
        print(f"  {'Comb':>5}", end="")
        for l in layers_show:
            print(f" {'L'+str(l):>8}", end="")
        print()
        for cname in comb_names:
            norms = hidden_results[cname]["avg_norms"]
            print(f"  {cname:>5}", end="")
            for l in layers_show:
                if l in norms:
                    print(f" {norms[l]:>8.1f}", end="")
                else:
                    print(f" {'—':>8}", end="")
            print()

    # ── Visualizations ────────────────────────────────────
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  Phase 4: Visualizations", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    plot_selectivity_heatmaps(selectivity, args.output_dir)
    plot_differential_map(diff_results, args.output_dir)
    plot_combinator_layer_profiles(selectivity, args.output_dir)
    plot_cross_combinator_correlation(selectivity, args.output_dir)

    # ── Save JSON results ─────────────────────────────────
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model": HF_MODEL,
        "n_layers": n_layers,
        "n_heads": n_heads,
        "quick_mode": args.quick,
        "combinator_selectivity": {},
        "head_assignment": {
            c: int(np.sum(dominant == ci))
            for ci, c in enumerate(comb_names)
        },
        "cross_correlation": {
            f"{ci}_{cj}": float(np.corrcoef(flat[ci], flat[cj])[0, 1])
            for ci in comb_names for cj in comb_names
        },
        "circuit_mapping": {
            name: {
                "4b_position": data["4b"],
                "32b_approx": data["32b_approx"],
                "selectivity": data.get("selectivity_32b"),
                "dominant": data.get("dominant"),
            }
            for name, data in circuit_map.items()
        },
    }

    # Per-combinator summary stats
    for cname in comb_names:
        data = selectivity[cname]["vs_control"]
        output["combinator_selectivity"][cname] = {
            "mean": float(data.mean()),
            "max": float(data.max()),
            "std": float(data.std()),
            "max_layer": int(np.unravel_index(np.argmax(data), data.shape)[0]),
            "max_head": int(np.unravel_index(np.argmax(data), data.shape)[1]),
            "top_5_heads": diff_results["top_heads_per_combinator"][cname][:5],
        }

    if hidden_results:
        output["hidden_state_norms"] = {
            cname: hidden_results[cname]["avg_norms"]
            for cname in comb_names
        }
        output["hidden_state_cosines"] = {
            cname: hidden_results[cname]["avg_cosines"]
            for cname in comb_names
        }

    # Save selectivity matrices as npz
    np.savez_compressed(
        str(args.output_dir / "selectivity_matrices.npz"),
        **{f"{c}_vs_control": selectivity[c]["vs_control"] for c in comb_names},
        **{f"{c}_vs_null": selectivity[c]["vs_null"] for c in comb_names},
        dominant=dominant,
        differential=diff_results["differential"],
    )

    json_path = args.output_dir / "combinator_probe_results.json"
    json_path.write_text(json.dumps(output, indent=2, default=str))

    print(f"\n  💾 Results: {json_path}", file=sys.stderr)
    print(f"  💾 Matrices: {args.output_dir / 'selectivity_matrices.npz'}",
          file=sys.stderr)
    print(f"  🖼  Plots: {args.output_dir}/*.png", file=sys.stderr)

    total_time = t_attn + (t_hidden if not args.skip_hidden else 0)
    print(f"\n  Total analysis time: {total_time:.1f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
