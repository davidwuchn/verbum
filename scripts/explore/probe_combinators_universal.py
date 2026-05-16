#!/usr/bin/env python3
"""Universal KIBC combinator selectivity probe — multi-model support.

Probes whether the holographic combinator structure (KIBC) exists in a
given model. Designed for convergence verification: run on multiple
models of similar size, compare selectivity profiles to establish
universality.

The probe measures attention pattern differences between active (combinator-
triggering) and control (matched neutral) sentences for each of K, I, B, C.
Per-head selectivity profiles reveal whether the model has dedicated
circuitry for each combinator operation.

Expected results for models with the universal hologram:
  - K/B/C form a cluster (cross-correlation > 0.85)
  - I is distinct (correlation with K/B/C in range 0.60-0.75)
  - Distribution: K ≈ B > C >> I (approximately 30:15:28:27 per session 093)

Supported models:
  - allenai/OLMo-2-1124-13B (Apache-2.0, 40L, 40H, d=5120)
  - EleutherAI/pythia-160m-deduped (Apache-2.0, 12L, 12H, d=768)
  - mistralai/Mistral-7B-v0.3 (Apache-2.0, 32L, 32H, d=4096)
  - Qwen/Qwen3-14B (Apache-2.0, 40L, 40H, d=5120)
  - meta-llama/Llama-3.1-8B (Llama license, 32L, 32H, d=4096)
  - Any HuggingFace CausalLM with output_attentions support

Usage:
    # OLMo-2-13B (primary canary)
    uv run python scripts/explore/probe_combinators_universal.py --model allenai/OLMo-2-1124-13B

    # Quick mode (fewer probes, faster)
    uv run python scripts/explore/probe_combinators_universal.py --model allenai/OLMo-2-1124-13B --quick

    # Specific device
    uv run python scripts/explore/probe_combinators_universal.py --model allenai/OLMo-2-1124-13B --device mps

    # Layer subset for large models (memory constrained)
    uv run python scripts/explore/probe_combinators_universal.py --model allenai/OLMo-2-1124-13B --layer-stride 2

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig


# ══════════════════════════════════════════════════════════════════
# Probe sentences — identical across all models
# ══════════════════════════════════════════════════════════════════

PROBES = {
    # ── K (select): pick one, discard alternative ──────────────
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

NULL_PROBES = [
    "The sun rose over the mountains in the early morning light.",
    "Water flows downhill following the path of least resistance.",
    "The library was quiet and the shelves were full of books.",
    "Birds flew south for the winter as the leaves began to fall.",
    "The clock on the wall showed that it was nearly midnight.",
    "Clouds gathered in the sky promising rain by the afternoon.",
]

# Prior results for comparison
PRIOR_RESULTS = {
    "pythia-160m": {
        "model": "EleutherAI/pythia-160m-deduped",
        "n_layers": 12, "n_heads": 12,
        "head_pcts": {"K": 30.6, "I": 13.8, "B": 28.1, "C": 27.5},
        "family": "pythia", "params": "160M",
    },
    "qwen3-32b": {
        "model": "Qwen/Qwen3-32B",
        "n_layers": 64, "n_heads": 64,
        "head_pcts": {"K": 31.3, "I": 14.7, "B": 31.3, "C": 22.6},
        "family": "qwen", "params": "32B",
    },
}


# ══════════════════════════════════════════════════════════════════
# Model loading — architecture-agnostic
# ══════════════════════════════════════════════════════════════════


def load_model(model_name: str, device: str = "mps", dtype: str = "auto") -> tuple:
    """Load any HuggingFace CausalLM with attention output support.

    For large models (>7B), uses float16/bfloat16 automatically.
    For small models (<1B), uses float32.
    """
    print(f"Loading {model_name}...", file=sys.stderr)
    t0 = time.time()

    config = AutoConfig.from_pretrained(model_name)
    n_params_approx = getattr(config, 'num_parameters', None)

    # Determine dtype
    if dtype == "auto":
        # Large models: use bfloat16 for memory efficiency
        n_layers = config.num_hidden_layers
        d_model = config.hidden_size
        approx_params = n_layers * d_model * d_model * 12  # rough estimate
        if approx_params > 1e9:
            torch_dtype = torch.bfloat16
        else:
            torch_dtype = torch.float32
    elif dtype == "fp16":
        torch_dtype = torch.float16
    elif dtype == "bf16":
        torch_dtype = torch.bfloat16
    else:
        torch_dtype = torch.float32

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch_dtype,
        device_map=device,
        attn_implementation="eager",  # required for output_attentions
    )
    model.eval()

    t1 = time.time()
    n_layers = config.num_hidden_layers
    n_heads = config.num_attention_heads
    d_model = config.hidden_size

    print(f"Loaded in {t1-t0:.1f}s: {n_layers} layers, {n_heads} heads, "
          f"d={d_model}, dtype={torch_dtype}", file=sys.stderr)

    return model, tokenizer, config


# ══════════════════════════════════════════════════════════════════
# Attention capture — architecture-agnostic
# ══════════════════════════════════════════════════════════════════


def capture_attention(
    model, tokenizer, text: str,
    layer_indices: list[int] | None = None,
) -> dict:
    """Run forward pass with output_attentions=True.

    Args:
        model: HuggingFace CausalLM
        tokenizer: corresponding tokenizer
        text: input text
        layer_indices: if set, only return these layers (memory optimization)

    Returns:
        {
            "token_ids": list[int],
            "attentions": np.ndarray (n_layers, n_heads, seq_len, seq_len),
            "n_tokens": int,
        }
    """
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    token_ids = inputs["input_ids"][0].tolist()

    with torch.no_grad():
        outputs = model(**inputs, output_attentions=True)

    # outputs.attentions: tuple of (1, n_heads, seq_len, seq_len) per layer
    if layer_indices is not None:
        attn_list = [outputs.attentions[i][0].cpu().float().numpy()
                     for i in layer_indices]
    else:
        attn_list = [layer_attn[0].cpu().float().numpy()
                     for layer_attn in outputs.attentions]

    attentions = np.stack(attn_list, axis=0)  # (n_layers, n_heads, seq, seq)

    return {
        "token_ids": token_ids,
        "attentions": attentions,
        "n_tokens": len(token_ids),
    }


# ══════════════════════════════════════════════════════════════════
# Selectivity computation
# ══════════════════════════════════════════════════════════════════


def head_selectivity(
    active_attn: np.ndarray,
    control_attn: np.ndarray,
) -> np.ndarray:
    """Per-head L2 selectivity between active and control conditions.

    Both inputs: (n_layers, n_heads, seq_len, seq_len)
    Returns: (n_layers, n_heads)
    """
    min_seq = min(active_attn.shape[2], control_attn.shape[2])
    a = active_attn[:, :, :min_seq, :min_seq].astype(np.float32)
    c = control_attn[:, :, :min_seq, :min_seq].astype(np.float32)
    diff = a - c
    return np.sqrt(np.mean(diff ** 2, axis=(-2, -1)))


def compute_combinator_selectivity(
    model, tokenizer, config,
    probes: dict, null_probes: list[str],
    quick: bool = False,
    layer_stride: int = 1,
) -> dict:
    """For each combinator, compute per-head selectivity.

    Args:
        layer_stride: sample every N-th layer (for memory on large models)
    """
    n_layers = config.num_hidden_layers
    n_heads = config.num_attention_heads

    # Determine which layers to probe
    if layer_stride > 1:
        layer_indices = list(range(0, n_layers, layer_stride))
        # Always include last layer
        if (n_layers - 1) not in layer_indices:
            layer_indices.append(n_layers - 1)
        print(f"  Layer stride={layer_stride}: probing {len(layer_indices)}/{n_layers} layers",
              file=sys.stderr)
    else:
        layer_indices = None  # all layers

    effective_n_layers = len(layer_indices) if layer_indices else n_layers
    results = {}

    # Null baseline
    print("  Capturing null baseline...", file=sys.stderr)
    null_attns = []
    for text in (null_probes[:2] if quick else null_probes):
        cap = capture_attention(model, tokenizer, text, layer_indices)
        null_attns.append(cap)

    for comb_name, comb_data in probes.items():
        active_texts = comb_data["active"][:3] if quick else comb_data["active"]
        control_texts = comb_data["control"][:3] if quick else comb_data["control"]
        n_pairs = min(len(active_texts), len(control_texts))

        print(f"  Probing {comb_name} ({comb_data['description']})...",
              file=sys.stderr)

        # Active vs matched control
        vs_control = np.zeros((effective_n_layers, n_heads))
        for i in range(n_pairs):
            print(f"    pair {i+1}/{n_pairs}...", file=sys.stderr)
            active_cap = capture_attention(model, tokenizer, active_texts[i], layer_indices)
            control_cap = capture_attention(model, tokenizer, control_texts[i], layer_indices)
            sel = head_selectivity(active_cap["attentions"],
                                   control_cap["attentions"])
            vs_control += sel
            # Free memory for large models
            del active_cap, control_cap
        vs_control /= n_pairs

        # Active vs null
        vs_null = np.zeros((effective_n_layers, n_heads))
        n_null_pairs = min(n_pairs, len(null_attns))
        for i in range(n_null_pairs):
            active_cap = capture_attention(model, tokenizer, active_texts[i], layer_indices)
            sel = head_selectivity(active_cap["attentions"],
                                   null_attns[i]["attentions"])
            vs_null += sel
            del active_cap
        vs_null /= max(n_null_pairs, 1)

        # Control vs null (baseline noise floor)
        vs_null_control = np.zeros((effective_n_layers, n_heads))
        for i in range(n_null_pairs):
            control_cap = capture_attention(model, tokenizer, control_texts[i], layer_indices)
            sel = head_selectivity(control_cap["attentions"],
                                   null_attns[i]["attentions"])
            vs_null_control += sel
            del control_cap
        vs_null_control /= max(n_null_pairs, 1)

        results[comb_name] = {
            "vs_control": vs_control,
            "vs_null": vs_null,
            "vs_null_control": vs_null_control,
            "description": comb_data["description"],
        }

        # Force GC between combinators for large models
        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
        elif torch.cuda.is_available():
            torch.cuda.empty_cache()

    return results, layer_indices


# ══════════════════════════════════════════════════════════════════
# Analysis: differential selectivity
# ══════════════════════════════════════════════════════════════════


def compute_differential_selectivity(selectivity: dict) -> dict:
    """Per head: which combinator dominates, and by how much?"""
    comb_names = ["K", "I", "B", "C"]
    n_layers, n_heads = selectivity["K"]["vs_control"].shape

    sel_matrix = np.stack(
        [selectivity[c]["vs_control"] for c in comb_names], axis=0
    )

    dominant = np.argmax(sel_matrix, axis=0)
    sorted_sel = np.sort(sel_matrix, axis=0)
    differential = sorted_sel[-1] - sorted_sel[-2]

    # Top heads per combinator
    top_heads = {}
    for ci, cname in enumerate(comb_names):
        scores = sel_matrix[ci]
        flat = scores.flatten()
        top_idx = np.argsort(flat)[-20:][::-1]
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


def plot_selectivity_heatmaps(
    selectivity: dict, n_layers: int, n_heads: int,
    model_label: str, output_dir: Path, layer_indices: list[int] | None,
):
    """Per-combinator selectivity heatmaps."""
    comb_names = ["K", "I", "B", "C"]
    comb_labels = {
        "K": "K (select)", "I": "I (identity)",
        "B": "B (compose)", "C": "C (flip)",
    }

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f"Per-Head Combinator Selectivity (active vs matched control)\n"
                 f"{model_label} — {n_layers} layers × {n_heads} heads",
                 fontsize=14, fontweight="bold")

    vmax = max(selectivity[c]["vs_control"].max() for c in comb_names) * 0.8

    for idx, cname in enumerate(comb_names):
        ax = axes[idx // 2][idx % 2]
        data = selectivity[cname]["vs_control"]
        im = ax.imshow(data, aspect="auto", cmap="hot",
                       interpolation="nearest", vmin=0, vmax=vmax)
        ax.set_title(f"{comb_labels[cname]}", fontsize=12, fontweight="bold")
        ax.set_xlabel("Head")
        ax.set_ylabel("Layer" + (" (strided)" if layer_indices else ""))

        if layer_indices and len(layer_indices) <= 25:
            ax.set_yticks(range(len(layer_indices)))
            ax.set_yticklabels([f"L{l}" for l in layer_indices], fontsize=7)

        plt.colorbar(im, ax=ax, label="L2 selectivity")

    plt.tight_layout()
    fig.savefig(output_dir / "selectivity_heatmaps.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: selectivity_heatmaps.png", file=sys.stderr)


def plot_layer_profiles(
    selectivity: dict, model_label: str, output_dir: Path,
    layer_indices: list[int] | None,
):
    """Layer profiles — mean selectivity per layer per combinator."""
    comb_names = ["K", "I", "B", "C"]
    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]

    fig, ax = plt.subplots(figsize=(14, 7))
    fig.suptitle(f"Combinator Selectivity by Layer — {model_label}",
                 fontsize=13, fontweight="bold")

    x_labels = [f"L{l}" for l in layer_indices] if layer_indices else None
    x_range = range(selectivity["K"]["vs_control"].shape[0])

    for ci, cname in enumerate(comb_names):
        data = selectivity[cname]["vs_control"]
        mean_by_layer = data.mean(axis=1)
        max_layer_idx = int(np.argmax(mean_by_layer))
        actual_layer = layer_indices[max_layer_idx] if layer_indices else max_layer_idx
        ax.plot(x_range, mean_by_layer, color=colors[ci], linewidth=2.5,
                label=f"{cname} — peak L{actual_layer}", marker='o', markersize=4)
        ax.fill_between(x_range, mean_by_layer, alpha=0.1, color=colors[ci])

    ax.set_xlabel("Layer", fontsize=12)
    ax.set_ylabel("Mean selectivity (L2 distance)", fontsize=12)
    if x_labels and len(x_labels) <= 40:
        ax.set_xticks(list(x_range))
        ax.set_xticklabels(x_labels, fontsize=7, rotation=45)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_dir / "layer_profiles.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: layer_profiles.png", file=sys.stderr)


def plot_differential_map(
    diff_results: dict, n_layers: int, n_heads: int,
    model_label: str, output_dir: Path, layer_indices: list[int] | None,
):
    """Which combinator dominates each head."""
    dominant = diff_results["dominant_combinator"]
    differential = diff_results["differential"]
    comb_names = ["K", "I", "B", "C"]
    comb_colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]

    eff_layers, eff_heads = dominant.shape

    img = np.zeros((eff_layers, eff_heads, 3))
    for ci, color_hex in enumerate(comb_colors):
        r = int(color_hex[1:3], 16) / 255
        g = int(color_hex[3:5], 16) / 255
        b = int(color_hex[5:7], 16) / 255
        mask = dominant == ci
        intensity = np.clip(differential / (differential.max() + 1e-8), 0.2, 1.0)
        img[mask, 0] = r * intensity[mask]
        img[mask, 1] = g * intensity[mask]
        img[mask, 2] = b * intensity[mask]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 10),
                                    gridspec_kw={"width_ratios": [2.5, 1]})

    fig.suptitle(f"Combinator Head Assignment — {model_label}\n"
                 f"Color = dominant combinator, brightness = specialization",
                 fontsize=13, fontweight="bold")

    ax1.imshow(img, aspect="auto", interpolation="nearest")
    ax1.set_xlabel("Head")
    ax1.set_ylabel("Layer" + (" (strided)" if layer_indices else ""))

    if layer_indices and len(layer_indices) <= 25:
        ax1.set_yticks(range(len(layer_indices)))
        ax1.set_yticklabels([f"L{l}" for l in layer_indices], fontsize=7)

    # Legend
    handles = []
    for ci, cname in enumerate(comb_names):
        count = int(np.sum(dominant == ci))
        pct = count / dominant.size * 100
        handles.append(mpatches.Patch(
            color=comb_colors[ci],
            label=f"{cname}: {count} heads ({pct:.1f}%)"))
    ax1.legend(handles=handles, loc="upper right", fontsize=10)

    # Per-layer stacked bar
    layer_dist = np.zeros((eff_layers, 4))
    for ci in range(4):
        layer_dist[:, ci] = np.sum(dominant == ci, axis=1)

    bottom = np.zeros(eff_layers)
    for ci in range(4):
        ax2.barh(range(eff_layers), layer_dist[:, ci], left=bottom,
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


def plot_cross_correlation(selectivity: dict, model_label: str, output_dir: Path):
    """Cross-combinator correlation matrix."""
    comb_names = ["K", "I", "B", "C"]

    flat = {c: selectivity[c]["vs_control"].flatten() for c in comb_names}
    corr = np.zeros((4, 4))
    for i, ci in enumerate(comb_names):
        for j, cj in enumerate(comb_names):
            corr[i, j] = float(np.corrcoef(flat[ci], flat[cj])[0, 1])

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(4))
    ax.set_yticks(range(4))
    ax.set_xticklabels(comb_names, fontsize=14)
    ax.set_yticklabels(comb_names, fontsize=14)

    for i in range(4):
        for j in range(4):
            ax.text(j, i, f"{corr[i,j]:.3f}", ha="center", va="center",
                    fontsize=13, fontweight="bold",
                    color="white" if abs(corr[i, j]) > 0.5 else "black")

    ax.set_title(f"Cross-Combinator Correlation — {model_label}\n"
                 f"High = same heads, Low = different circuits",
                 fontsize=12, fontweight="bold")
    plt.colorbar(im, label="Pearson r")

    plt.tight_layout()
    fig.savefig(output_dir / "cross_combinator_correlation.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: cross_combinator_correlation.png", file=sys.stderr)


def plot_convergence_comparison(
    current_pcts: dict, model_label: str, output_dir: Path,
):
    """Compare current model against all prior results."""
    comb_names = ["K", "I", "B", "C"]
    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]

    # Gather all models
    all_models = {}
    for name, data in PRIOR_RESULTS.items():
        all_models[name] = data["head_pcts"]
    all_models["current"] = current_pcts

    n_models = len(all_models)
    fig, axes = plt.subplots(1, n_models, figsize=(5 * n_models, 6))
    if n_models == 1:
        axes = [axes]

    fig.suptitle(f"Combinator Distribution Convergence\n"
                 f"Universal ratio prediction: K≈30% I≈15% B≈28% C≈27%",
                 fontsize=13, fontweight="bold")

    x = np.arange(4)
    width = 0.5

    for idx, (name, pcts) in enumerate(all_models.items()):
        ax = axes[idx]
        vals = [pcts[c] for c in comb_names]
        bars = ax.bar(x, vals, width, color=colors)
        ax.set_xticks(x)
        ax.set_xticklabels(comb_names, fontsize=14)
        ax.set_ylabel("% of heads", fontsize=11)
        ax.set_ylim(0, 50)

        label = model_label if name == "current" else name
        info = PRIOR_RESULTS.get(name, {})
        params = info.get("params", "")
        ax.set_title(f"{label}\n({params})" if params else label, fontsize=11)

        for i, pct in enumerate(vals):
            ax.text(i, pct + 1, f"{pct:.1f}%", ha="center", fontsize=10,
                    fontweight="bold")

    plt.tight_layout()
    fig.savefig(output_dir / "convergence_comparison.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: convergence_comparison.png", file=sys.stderr)


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(
        description="Universal KIBC combinator selectivity probe")
    parser.add_argument("--model", required=True,
                        help="HuggingFace model name or path")
    parser.add_argument("--device", default="mps",
                        help="Device (mps, cuda, cpu)")
    parser.add_argument("--dtype", default="auto",
                        choices=["auto", "fp16", "bf16", "fp32"],
                        help="Model dtype")
    parser.add_argument("--quick", action="store_true",
                        help="Fewer probes for faster results")
    parser.add_argument("--layer-stride", type=int, default=1,
                        help="Sample every N-th layer (memory optimization)")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="Output directory (default: results/combinator-probe-{model_slug}/)")
    args = parser.parse_args()

    # Derive output dir from model name
    model_slug = args.model.split("/")[-1].lower().replace("-", "_")
    if args.output_dir is None:
        args.output_dir = Path(f"results/combinator-probe-{model_slug}")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    model_label = args.model.split("/")[-1]

    # Load model
    model, tokenizer, config = load_model(args.model, args.device, args.dtype)
    n_layers = config.num_hidden_layers
    n_heads = config.num_attention_heads

    # ── Phase 1: Attention-based selectivity ──────────────
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  Phase 1: Attention selectivity per combinator", file=sys.stderr)
    print(f"  Model: {args.model}", file=sys.stderr)
    print(f"  Architecture: {n_layers}L × {n_heads}H = {n_layers * n_heads} heads",
          file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    t0 = time.time()
    selectivity, layer_indices = compute_combinator_selectivity(
        model, tokenizer, config,
        PROBES, NULL_PROBES,
        quick=args.quick,
        layer_stride=args.layer_stride,
    )
    t_attn = time.time() - t0
    print(f"  Attention analysis: {t_attn:.1f}s", file=sys.stderr)

    # ── Phase 2: Differential analysis ────────────────────
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  Phase 2: Differential selectivity analysis", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    diff_results = compute_differential_selectivity(selectivity)
    comb_names = ["K", "I", "B", "C"]

    # Summary
    print(f"\n  Combinator selectivity summary (vs matched control):")
    print(f"  {'Comb':>5} {'Mean':>8} {'Max':>8} {'MaxLayer':>9} {'MaxHead':>8}")
    print(f"  {'─'*5} {'─'*8} {'─'*8} {'─'*9} {'─'*8}")
    for cname in comb_names:
        data = selectivity[cname]["vs_control"]
        max_idx = np.unravel_index(np.argmax(data), data.shape)
        actual_layer = layer_indices[max_idx[0]] if layer_indices else max_idx[0]
        print(f"  {cname:>5} {data.mean():>8.5f} {data.max():>8.5f} "
              f"L{actual_layer:>3}      H{max_idx[1]:>3}")

    # Head assignment
    dominant = diff_results["dominant_combinator"]
    print(f"\n  Head assignment (dominant combinator per head):")
    current_pcts = {}
    for ci, cname in enumerate(comb_names):
        count = int(np.sum(dominant == ci))
        pct = count / dominant.size * 100
        current_pcts[cname] = pct
        print(f"    {cname}: {count:>3} heads ({pct:>5.1f}%)")

    # Cross-correlation — THE KEY UNIVERSALITY TEST
    flat = {c: selectivity[c]["vs_control"].flatten() for c in comb_names}
    print(f"\n  Cross-combinator correlation (universality test):")
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

    # Universality assessment
    print(f"\n  ═══ UNIVERSALITY ASSESSMENT ═══")
    kbc_corrs = []
    i_vs_kbc = []
    for ci in ["K", "B", "C"]:
        for cj in ["K", "B", "C"]:
            if ci != cj:
                r = float(np.corrcoef(flat[ci], flat[cj])[0, 1])
                kbc_corrs.append(r)
        r_i = float(np.corrcoef(flat["I"], flat[ci])[0, 1])
        i_vs_kbc.append(r_i)

    mean_kbc = np.mean(kbc_corrs)
    mean_i_vs_kbc = np.mean(i_vs_kbc)

    print(f"  K/B/C cluster mean correlation: {mean_kbc:.3f} "
          f"{'✓' if mean_kbc > 0.85 else '⚠' if mean_kbc > 0.70 else '✗'} "
          f"(expect >0.85)")
    print(f"  I vs K/B/C mean correlation:    {mean_i_vs_kbc:.3f} "
          f"{'✓' if mean_i_vs_kbc < 0.80 else '⚠'} "
          f"(expect <0.80 = I is distinct; <0.30 = strongly distinct)")

    # Comparison with priors
    print(f"\n  Comparison with prior models:")
    print(f"  {'Model':>20} {'K':>6} {'I':>6} {'B':>6} {'C':>6}")
    print(f"  {'─'*20} {'─'*6} {'─'*6} {'─'*6} {'─'*6}")
    for name, data in PRIOR_RESULTS.items():
        pcts = data["head_pcts"]
        print(f"  {name:>20} {pcts['K']:>5.1f}% {pcts['I']:>5.1f}% "
              f"{pcts['B']:>5.1f}% {pcts['C']:>5.1f}%")
    print(f"  {model_label:>20} {current_pcts['K']:>5.1f}% {current_pcts['I']:>5.1f}% "
          f"{current_pcts['B']:>5.1f}% {current_pcts['C']:>5.1f}%")

    # Cosine similarity of distribution to prior models
    current_vec = np.array([current_pcts[c] for c in comb_names])
    for name, data in PRIOR_RESULTS.items():
        prior_vec = np.array([data["head_pcts"][c] for c in comb_names])
        cos = float(np.dot(current_vec, prior_vec) /
                    (np.linalg.norm(current_vec) * np.linalg.norm(prior_vec) + 1e-8))
        print(f"  Distribution cos({model_label}, {name}): {cos:.4f}")

    # ── Phase 3: Visualizations ───────────────────────────
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  Phase 3: Visualizations", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    plot_selectivity_heatmaps(
        selectivity, n_layers, n_heads, model_label, args.output_dir, layer_indices)
    plot_layer_profiles(selectivity, model_label, args.output_dir, layer_indices)
    plot_differential_map(
        diff_results, n_layers, n_heads, model_label, args.output_dir, layer_indices)
    plot_cross_correlation(selectivity, model_label, args.output_dir)
    plot_convergence_comparison(current_pcts, model_label, args.output_dir)

    # ── Save JSON results ─────────────────────────────────
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model": args.model,
        "model_label": model_label,
        "n_layers": n_layers,
        "n_heads": n_heads,
        "total_heads": n_layers * n_heads,
        "layer_stride": args.layer_stride,
        "layers_probed": layer_indices if layer_indices else list(range(n_layers)),
        "quick_mode": args.quick,
        "dtype": str(model.dtype),
        "hypothesis": "Universal holographic combinator structure (KIBC)",
        "combinator_selectivity": {},
        "head_assignment": {
            c: int(np.sum(dominant == ci))
            for ci, c in enumerate(comb_names)
        },
        "head_assignment_pct": current_pcts,
        "cross_correlation": {
            f"{ci}_{cj}": float(np.corrcoef(flat[ci], flat[cj])[0, 1])
            for ci in comb_names for cj in comb_names
        },
        "universality_assessment": {
            "kbc_cluster_mean_corr": float(mean_kbc),
            "i_vs_kbc_mean_corr": float(mean_i_vs_kbc),
            "kbc_cluster_pass": bool(mean_kbc > 0.85),
            "i_distinct_pass": bool(mean_i_vs_kbc < 0.80),  # I must be distinct from K/B/C
            "i_distinct_strong": bool(mean_i_vs_kbc < 0.30),  # Stronger separation (13B+ models)
            "universal_hologram_confirmed": bool(mean_kbc > 0.85 and mean_i_vs_kbc < 0.80),
        },
        "distribution_similarity": {
            name: float(np.dot(current_vec,
                              np.array([data["head_pcts"][c] for c in comb_names])) /
                       (np.linalg.norm(current_vec) *
                        np.linalg.norm(np.array([data["head_pcts"][c] for c in comb_names])) + 1e-8))
            for name, data in PRIOR_RESULTS.items()
        },
        "comparison_priors": PRIOR_RESULTS,
    }

    # Per-combinator summary
    for cname in comb_names:
        data = selectivity[cname]["vs_control"]
        max_idx = np.unravel_index(np.argmax(data), data.shape)
        actual_layer = layer_indices[max_idx[0]] if layer_indices else max_idx[0]
        output["combinator_selectivity"][cname] = {
            "mean": float(data.mean()),
            "max": float(data.max()),
            "std": float(data.std()),
            "max_layer": int(actual_layer),
            "max_head": int(max_idx[1]),
            "mean_by_layer": [float(data[l].mean()) for l in range(data.shape[0])],
            "top_5_heads": diff_results["top_heads_per_combinator"][cname][:5],
        }

    # Save matrices
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
    print(f"\n  Total analysis time: {t_attn:.1f}s", file=sys.stderr)

    # Final verdict
    if output["universality_assessment"]["universal_hologram_confirmed"]:
        distinct_str = " (strongly)" if output["universality_assessment"]["i_distinct_strong"] else ""
        print(f"\n  ✅ UNIVERSAL HOLOGRAM CONFIRMED in {model_label}", file=sys.stderr)
        print(f"     K/B/C cluster: {mean_kbc:.3f} | I distinct{distinct_str}: {mean_i_vs_kbc:.3f}",
              file=sys.stderr)
    else:
        print(f"\n  ⚠️  Universality test inconclusive for {model_label}", file=sys.stderr)
        if not output["universality_assessment"]["kbc_cluster_pass"]:
            print(f"     K/B/C cluster correlation too low: {mean_kbc:.3f}", file=sys.stderr)
        if not output["universality_assessment"]["i_distinct_pass"]:
            print(f"     I not distinct enough: {mean_i_vs_kbc:.3f} (need <0.80)", file=sys.stderr)


if __name__ == "__main__":
    main()
