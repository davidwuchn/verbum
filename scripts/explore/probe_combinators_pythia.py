#!/usr/bin/env python3
"""Probe: Do KIBC combinators exist in Pythia-160M?

Session 004 found three Montague primitives in Pythia-160M:
  1. Type assignment  → Embeddings + L0 (lexical, 84%)
  2. Structural parse → L3 (critical, +0.43 shift)
  3. Typed application → L8-L11 (high selectivity, resists patching)

Session 080 found three combinator circuits in Qwen3-32B:
  1. Routing    → K ≈ C ≈ W ≈ abstract (early, L0-L6)
  2. Composition → B ≈ S (early-to-mid, L3-L17)
  3. Identity   → I (distributed)

This probe tests whether the "Montague primitives" are actually
combinator circuits seen from a different angle. If K peaks at L0-L2
and B peaks at L3-L11, the Montague decomposition was describing
KIBC all along.

Model: EleutherAI/pythia-160m-deduped
  12 layers, 12 heads/layer, 768 hidden_size, GPTNeoX
  Total: 144 heads (vs 4096 in 32B)

Same probe sentences as the 32B experiment — natural language,
no chat template needed (Pythia is a base model).

Usage:
    uv run python scripts/explore/probe_combinators_pythia.py
    uv run python scripts/explore/probe_combinators_pythia.py --quick

Output: results/combinator-probe-pythia/

License: MIT
"""

from __future__ import annotations

import argparse
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
from transformers import AutoModelForCausalLM, AutoTokenizer


# ══════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════

MODEL_NAME = "EleutherAI/pythia-160m-deduped"
OUTPUT_DIR = Path("results/combinator-probe-pythia")

# Pythia-160M architecture: 12 layers, 12 heads, head_dim=64
N_LAYERS = 12
N_HEADS = 12

# Session 004 Montague zones (for overlay comparison)
MONTAGUE_ZONES = {
    "type_assignment": {"layers": [0], "color": "#9b59b6", "label": "Type (L0)"},
    "structural_parse": {"layers": [3], "color": "#e67e22", "label": "Parse (L3)"},
    "typed_application": {"layers": [8, 9, 10, 11], "color": "#1abc9c", "label": "Apply (L8-L11)"},
}


# ══════════════════════════════════════════════════════════════════
# Probe sentences — identical to 32B probe (natural language)
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


# ══════════════════════════════════════════════════════════════════
# Model loading — Pythia-160M (GPTNeoX, HuggingFace native)
# ══════════════════════════════════════════════════════════════════


def load_model(device: str = "mps") -> tuple:
    """Load Pythia-160M from HuggingFace cache."""
    print(f"Loading {MODEL_NAME}...", file=sys.stderr)
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float32,  # 160M is small, use full precision
        device_map=device,
        attn_implementation="eager",  # required for output_attentions=True
    )
    model.eval()
    model.config.output_attentions = True

    t1 = time.time()
    print(f"Loaded in {t1-t0:.1f}s: {model.config.num_hidden_layers} layers, "
          f"{model.config.num_attention_heads} heads, "
          f"d={model.config.hidden_size}", file=sys.stderr)
    return model, tokenizer


# ══════════════════════════════════════════════════════════════════
# Attention capture
# ══════════════════════════════════════════════════════════════════


def capture_attention(model, tokenizer, text: str) -> dict:
    """Run forward pass with output_attentions=True.

    Returns:
        {
            "token_ids": list[int],
            "token_strs": list[str],
            "attentions": np.ndarray (n_layers, n_heads, seq_len, seq_len),
            "n_tokens": int,
        }
    """
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    token_ids = inputs["input_ids"][0].tolist()
    token_strs = [tokenizer.decode([tid]) for tid in token_ids]

    with torch.no_grad():
        outputs = model(**inputs, output_attentions=True)

    # outputs.attentions: tuple of (1, n_heads, seq_len, seq_len) per layer
    attn_list = []
    for layer_attn in outputs.attentions:
        attn_list.append(layer_attn[0].cpu().float().numpy())

    attentions = np.stack(attn_list, axis=0)  # (n_layers, n_heads, seq, seq)

    return {
        "token_ids": token_ids,
        "token_strs": token_strs,
        "attentions": attentions,
        "n_tokens": len(token_ids),
    }


# ══════════════════════════════════════════════════════════════════
# Hidden state capture (for layer-by-layer trajectory)
# ══════════════════════════════════════════════════════════════════


def capture_hidden_states(model, tokenizer, text: str) -> dict:
    """Capture hidden states at every layer.

    Returns:
        {
            "token_ids": list[int],
            "hidden_states": {layer_idx: np.ndarray (seq_len, d_model)},
        }
    """
    captured = {}
    hooks = []

    def make_hook(layer_idx):
        def hook_fn(module, input, output):
            if isinstance(output, tuple):
                h = output[0]
            else:
                h = output
            captured[layer_idx] = h[0].detach().cpu().float().numpy()
        return hook_fn

    # GPTNeoX layer path: model.gpt_neox.layers
    for li in range(model.config.num_hidden_layers):
        layer_module = model.gpt_neox.layers[li]
        hooks.append(layer_module.register_forward_hook(make_hook(li)))

    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    token_ids = inputs["input_ids"][0].tolist()

    with torch.no_grad():
        model(**inputs)

    for h in hooks:
        h.remove()

    return {
        "token_ids": token_ids,
        "hidden_states": captured,
    }


# ══════════════════════════════════════════════════════════════════
# Analysis: per-head selectivity
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
    model, tokenizer, probes: dict, null_probes: list[str],
    quick: bool = False,
) -> dict:
    """For each combinator, compute per-head selectivity."""
    n_layers = model.config.num_hidden_layers
    n_heads = model.config.num_attention_heads

    results = {}

    # Null baseline
    print("  Capturing null baseline...", file=sys.stderr)
    null_attns = []
    for text in (null_probes[:2] if quick else null_probes):
        cap = capture_attention(model, tokenizer, text)
        null_attns.append(cap)

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
        vs_control /= n_pairs

        # Active vs null
        vs_null = np.zeros((n_layers, n_heads))
        n_null_pairs = min(n_pairs, len(null_attns))
        for i in range(n_null_pairs):
            active_cap = capture_attention(model, tokenizer, active_texts[i])
            sel = head_selectivity(active_cap["attentions"],
                                   null_attns[i]["attentions"])
            vs_null += sel
        vs_null /= max(n_null_pairs, 1)

        # Control vs null
        vs_null_control = np.zeros((n_layers, n_heads))
        for i in range(n_null_pairs):
            control_cap = capture_attention(model, tokenizer, control_texts[i])
            sel = head_selectivity(control_cap["attentions"],
                                   null_attns[i]["attentions"])
            vs_null_control += sel
        vs_null_control /= max(n_null_pairs, 1)

        results[comb_name] = {
            "vs_control": vs_control,
            "vs_null": vs_null,
            "vs_null_control": vs_null_control,
            "description": comb_data["description"],
        }

    return results


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
# Analysis: hidden state comparison (combinator vs Montague zones)
# ══════════════════════════════════════════════════════════════════


def compute_hidden_state_analysis(
    model, tokenizer, probes: dict, quick: bool = False,
) -> dict:
    """Per-layer hidden state norms and transformation rates per combinator."""
    results = {}
    comb_names = ["K", "I", "B", "C"]

    for comb_name in comb_names:
        comb_data = probes[comb_name]
        texts = comb_data["active"][:2] if quick else comb_data["active"][:4]
        print(f"  Hidden states for {comb_name}...", file=sys.stderr)

        all_norms = []
        all_cosines = []

        for text in texts:
            cap = capture_hidden_states(model, tokenizer, text)
            hs = cap["hidden_states"]

            norms = {}
            for li in sorted(hs.keys()):
                norms[li] = float(np.mean(np.linalg.norm(hs[li], axis=-1)))

            cosines = {}
            sorted_layers = sorted(hs.keys())
            for j in range(len(sorted_layers) - 1):
                l1, l2 = sorted_layers[j], sorted_layers[j+1]
                h1 = hs[l1].mean(axis=0)
                h2 = hs[l2].mean(axis=0)
                cos = float(np.dot(h1, h2) / (np.linalg.norm(h1) * np.linalg.norm(h2) + 1e-8))
                cosines[f"L{l1}→L{l2}"] = cos

            all_norms.append(norms)
            all_cosines.append(cosines)

        avg_norms = {}
        for li in sorted(all_norms[0].keys()):
            avg_norms[str(li)] = float(np.mean([n[li] for n in all_norms]))

        avg_cosines = {}
        for key in all_cosines[0].keys():
            avg_cosines[key] = float(np.mean([c[key] for c in all_cosines]))

        results[comb_name] = {
            "avg_norms": avg_norms,
            "avg_cosines": avg_cosines,
        }

    return results


# ══════════════════════════════════════════════════════════════════
# Visualization — with Montague zone overlay
# ══════════════════════════════════════════════════════════════════


def plot_selectivity_heatmaps(selectivity: dict, output_dir: Path):
    """Per-combinator selectivity heatmaps (12 layers × 12 heads)."""
    comb_names = ["K", "I", "B", "C"]
    comb_labels = {
        "K": "K (select)", "I": "I (identity)",
        "B": "B (compose)", "C": "C (flip)",
    }

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle("Per-Head Combinator Selectivity (active vs matched control)\n"
                 "Pythia-160M — 12 layers × 12 heads",
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
        ax.set_xticks(range(N_HEADS))
        ax.set_yticks(range(N_LAYERS))
        plt.colorbar(im, ax=ax, label="L2 selectivity")

        # Montague zone markers on y-axis
        for zone_name, zone in MONTAGUE_ZONES.items():
            for ly in zone["layers"]:
                ax.axhline(y=ly, color=zone["color"], linewidth=1.5,
                          linestyle="--", alpha=0.7)

    plt.tight_layout()
    fig.savefig(output_dir / "selectivity_heatmaps.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: selectivity_heatmaps.png", file=sys.stderr)


def plot_differential_map(diff_results: dict, output_dir: Path):
    """Which combinator dominates each head — with Montague zone overlay."""
    dominant = diff_results["dominant_combinator"]
    differential = diff_results["differential"]
    comb_names = ["K", "I", "B", "C"]
    comb_colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]

    n_layers, n_heads = dominant.shape

    img = np.zeros((n_layers, n_heads, 3))
    for ci, color_hex in enumerate(comb_colors):
        r = int(color_hex[1:3], 16) / 255
        g = int(color_hex[3:5], 16) / 255
        b = int(color_hex[5:7], 16) / 255
        mask = dominant == ci
        intensity = np.clip(differential / (differential.max() + 1e-8), 0.2, 1.0)
        img[mask, 0] = r * intensity[mask]
        img[mask, 1] = g * intensity[mask]
        img[mask, 2] = b * intensity[mask]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8),
                                    gridspec_kw={"width_ratios": [2, 1]})

    fig.suptitle("Combinator Head Assignment — Pythia-160M\n"
                 "Color = dominant combinator, brightness = specialization\n"
                 "Dashed lines = session-004 Montague zones",
                 fontsize=13, fontweight="bold")

    ax1.imshow(img, aspect="auto", interpolation="nearest")
    ax1.set_xlabel("Head")
    ax1.set_ylabel("Layer")
    ax1.set_xticks(range(N_HEADS))
    ax1.set_yticks(range(N_LAYERS))

    # Montague zone overlay
    for zone_name, zone in MONTAGUE_ZONES.items():
        for ly in zone["layers"]:
            ax1.axhline(y=ly, color=zone["color"], linewidth=2,
                       linestyle="--", alpha=0.8)

    # Legend: combinators + Montague zones
    handles = []
    for ci, cname in enumerate(comb_names):
        count = int(np.sum(dominant == ci))
        pct = count / dominant.size * 100
        handles.append(mpatches.Patch(
            color=comb_colors[ci],
            label=f"{cname}: {count} heads ({pct:.1f}%)"))
    for zone_name, zone in MONTAGUE_ZONES.items():
        handles.append(plt.Line2D([0], [0], color=zone["color"],
                                   linewidth=2, linestyle="--",
                                   label=zone["label"]))
    ax1.legend(handles=handles, loc="upper right", fontsize=9)

    # Per-layer stacked bar
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
    ax2.set_yticks(range(N_LAYERS))
    ax2.set_title("Per-layer distribution")
    ax2.invert_yaxis()
    ax2.legend()

    # Montague zone bars on per-layer chart
    for zone_name, zone in MONTAGUE_ZONES.items():
        for ly in zone["layers"]:
            ax2.axhline(y=ly, color=zone["color"], linewidth=2,
                       linestyle="--", alpha=0.8)

    plt.tight_layout()
    fig.savefig(output_dir / "differential_map.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: differential_map.png", file=sys.stderr)


def plot_layer_profiles_with_montague(selectivity: dict, output_dir: Path):
    """Layer profiles with Montague zone bands — the key comparison chart."""
    comb_names = ["K", "I", "B", "C"]
    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]

    fig, ax = plt.subplots(figsize=(14, 7))
    fig.suptitle("Combinator Selectivity by Layer — Pythia-160M\n"
                 "Overlaid with session-004 Montague zones",
                 fontsize=13, fontweight="bold")

    # Montague zone background bands
    zone_alpha = 0.12
    ax.axvspan(-0.5, 0.5, alpha=zone_alpha, color=MONTAGUE_ZONES["type_assignment"]["color"],
               label="Montague: Type (L0)")
    ax.axvspan(2.5, 3.5, alpha=zone_alpha, color=MONTAGUE_ZONES["structural_parse"]["color"],
               label="Montague: Parse (L3)")
    ax.axvspan(7.5, 11.5, alpha=zone_alpha, color=MONTAGUE_ZONES["typed_application"]["color"],
               label="Montague: Apply (L8-L11)")

    # Combinator profiles
    for ci, cname in enumerate(comb_names):
        data = selectivity[cname]["vs_control"]
        mean_by_layer = data.mean(axis=1)
        max_layer = int(np.argmax(mean_by_layer))
        ax.plot(mean_by_layer, color=colors[ci], linewidth=2.5,
                label=f"{cname} — peak L{max_layer}", marker='o', markersize=6)
        ax.fill_between(range(len(mean_by_layer)), mean_by_layer,
                        alpha=0.1, color=colors[ci])

    ax.set_xlabel("Layer", fontsize=12)
    ax.set_ylabel("Mean selectivity (L2 distance)", fontsize=12)
    ax.set_xticks(range(N_LAYERS))
    ax.set_xticklabels([f"L{i}" for i in range(N_LAYERS)])
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_dir / "layer_profiles_montague_overlay.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: layer_profiles_montague_overlay.png", file=sys.stderr)


def plot_cross_correlation(selectivity: dict, output_dir: Path):
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

    ax.set_title("Cross-Combinator Correlation — Pythia-160M\n"
                 "High = same heads, Low = different circuits",
                 fontsize=12, fontweight="bold")
    plt.colorbar(im, label="Pearson r")

    plt.tight_layout()
    fig.savefig(output_dir / "cross_combinator_correlation.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: cross_combinator_correlation.png", file=sys.stderr)


def plot_32b_comparison(selectivity: dict, output_dir: Path):
    """Side-by-side comparison: Pythia-160M vs Qwen3-32B distributions."""
    comb_names = ["K", "I", "B", "C"]
    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]

    # Pythia data
    dominant = np.argmax(np.stack(
        [selectivity[c]["vs_control"] for c in comb_names], axis=0), axis=0)
    pythia_pcts = [float(np.sum(dominant == ci) / dominant.size * 100)
                   for ci in range(4)]

    # 32B data (from session 080)
    qwen_pcts = [31.3, 14.7, 31.3, 22.6]  # K, I, B, C

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Combinator Distribution: Pythia-160M vs Qwen3-32B\n"
                 "Percentage of heads dominated by each combinator",
                 fontsize=13, fontweight="bold")

    x = np.arange(4)
    width = 0.5

    ax1.bar(x, pythia_pcts, width, color=colors)
    ax1.set_xticks(x)
    ax1.set_xticklabels(comb_names, fontsize=14)
    ax1.set_ylabel("% of heads", fontsize=12)
    ax1.set_title(f"Pythia-160M (144 heads)", fontsize=12)
    ax1.set_ylim(0, 50)
    for i, pct in enumerate(pythia_pcts):
        ax1.text(i, pct + 1, f"{pct:.1f}%", ha="center", fontsize=11,
                 fontweight="bold")

    ax2.bar(x, qwen_pcts, width, color=colors)
    ax2.set_xticks(x)
    ax2.set_xticklabels(comb_names, fontsize=14)
    ax2.set_ylabel("% of heads", fontsize=12)
    ax2.set_title(f"Qwen3-32B (4096 heads)", fontsize=12)
    ax2.set_ylim(0, 50)
    for i, pct in enumerate(qwen_pcts):
        ax2.text(i, pct + 1, f"{pct:.1f}%", ha="center", fontsize=11,
                 fontweight="bold")

    plt.tight_layout()
    fig.savefig(output_dir / "pythia_vs_32b_distribution.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: pythia_vs_32b_distribution.png", file=sys.stderr)


# ══════════════════════════════════════════════════════════════════
# Montague zone analysis — the key question
# ══════════════════════════════════════════════════════════════════


def analyze_montague_vs_combinators(selectivity: dict) -> dict:
    """For each Montague zone, measure which combinator dominates.

    This answers: are the "three Montague primitives" actually
    combinator circuits viewed from a different angle?
    """
    comb_names = ["K", "I", "B", "C"]
    sel_matrix = np.stack(
        [selectivity[c]["vs_control"] for c in comb_names], axis=0
    )  # (4, 12, 12)

    analysis = {}
    for zone_name, zone in MONTAGUE_ZONES.items():
        layers = zone["layers"]
        # Mean selectivity per combinator in this zone
        zone_sel = {}
        for ci, cname in enumerate(comb_names):
            zone_sel[cname] = float(sel_matrix[ci, layers, :].mean())

        # Which combinator dominates heads in this zone?
        dominant_in_zone = np.argmax(sel_matrix[:, layers, :], axis=0)
        zone_dist = {}
        for ci, cname in enumerate(comb_names):
            count = int(np.sum(dominant_in_zone == ci))
            zone_dist[cname] = count

        analysis[zone_name] = {
            "layers": layers,
            "label": zone["label"],
            "mean_selectivity": zone_sel,
            "dominant_combinator": max(zone_sel, key=zone_sel.get),
            "head_distribution": zone_dist,
        }

    return analysis


# ══════════════════════════════════════════════════════════════════
# Session 004 circuit mapping (L0, L3 critical layers)
# ══════════════════════════════════════════════════════════════════


def map_session004_circuit(selectivity: dict) -> dict:
    """Map session 004 findings to combinator assignments.

    Session 004 found:
      L0: critical (type assignment / embedding refinement)
      L3: critical (structural parse / composition order)
      L8-L11: high selectivity zone (typed application)

    No individual essential heads (distributed), but we can check
    which combinator is most selective at each critical layer.
    """
    comb_names = ["K", "I", "B", "C"]
    sel_matrix = np.stack(
        [selectivity[c]["vs_control"] for c in comb_names], axis=0
    )

    mapping = {}
    critical_layers = [0, 3, 8, 9, 10, 11]
    layer_roles = {
        0: "type_assignment",
        3: "structural_parse",
        8: "typed_application_start",
        9: "typed_application",
        10: "typed_application",
        11: "typed_application_end",
    }

    for ly in critical_layers:
        per_head = {}
        for head in range(N_HEADS):
            head_sel = {c: float(sel_matrix[ci, ly, head])
                       for ci, c in enumerate(comb_names)}
            per_head[f"H{head}"] = {
                "selectivity": head_sel,
                "dominant": max(head_sel, key=head_sel.get),
            }

        layer_mean = {c: float(sel_matrix[ci, ly, :].mean())
                     for ci, c in enumerate(comb_names)}
        dominant_layer = max(layer_mean, key=layer_mean.get)

        mapping[f"L{ly}"] = {
            "role": layer_roles[ly],
            "mean_selectivity": layer_mean,
            "dominant": dominant_layer,
            "per_head": per_head,
        }

    return mapping


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(
        description="KIBC combinator probe — Pythia-160M")
    parser.add_argument("--device", default="mps",
                        help="Device (mps, cuda, cpu)")
    parser.add_argument("--quick", action="store_true",
                        help="Fewer probes for faster results")
    parser.add_argument("--skip-hidden", action="store_true",
                        help="Skip hidden state analysis")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Load model
    model, tokenizer = load_model(args.device)

    # ── Phase 1: Attention-based selectivity ──────────────
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  Phase 1: Attention selectivity per combinator", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    t0 = time.time()
    selectivity = compute_combinator_selectivity(
        model, tokenizer, PROBES, NULL_PROBES, quick=args.quick)
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
        print(f"  {cname:>5} {data.mean():>8.5f} {data.max():>8.5f} "
              f"L{max_idx[0]:>3}      H{max_idx[1]:>3}")

    # Head assignment
    dominant = diff_results["dominant_combinator"]
    print(f"\n  Head assignment (dominant combinator per head):")
    for ci, cname in enumerate(comb_names):
        count = int(np.sum(dominant == ci))
        pct = count / dominant.size * 100
        print(f"    {cname}: {count:>3} heads ({pct:>5.1f}%)")

    # Top heads
    for cname in comb_names:
        heads = diff_results["top_heads_per_combinator"][cname]
        dominant_heads = [h for h in heads if h["is_dominant"]][:5]
        if dominant_heads:
            print(f"\n  Top {cname}-specialized heads:")
            for h in dominant_heads:
                print(f"    L{h['layer']:>2}:H{h['head']:>2}  "
                      f"score={h['score']:.5f}  diff={h['differential']:.5f}")

    # Cross-correlation
    flat = {c: selectivity[c]["vs_control"].flatten() for c in comb_names}
    print(f"\n  Cross-combinator correlation:")
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

    # ── Phase 3: Montague zone → combinator mapping ───────
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  Phase 3: Montague zone → combinator analysis", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    montague_analysis = analyze_montague_vs_combinators(selectivity)
    print(f"\n  Montague zone → combinator mapping:")
    for zone_name, zone_data in montague_analysis.items():
        print(f"\n    {zone_data['label']}:")
        print(f"      Dominant combinator: {zone_data['dominant_combinator']}")
        print(f"      Mean selectivity: ", end="")
        for c, v in zone_data["mean_selectivity"].items():
            print(f"{c}={v:.5f}  ", end="")
        print()
        print(f"      Head distribution: ", end="")
        for c, v in zone_data["head_distribution"].items():
            print(f"{c}={v}  ", end="")
        print()

    # Session 004 circuit mapping
    circuit_map = map_session004_circuit(selectivity)
    print(f"\n  Session 004 critical layers → combinator assignment:")
    for layer_key, layer_data in circuit_map.items():
        dom = layer_data["dominant"]
        role = layer_data["role"]
        sel = layer_data["mean_selectivity"]
        print(f"    {layer_key} ({role}): dominant={dom} "
              f"(K={sel['K']:.4f} I={sel['I']:.4f} "
              f"B={sel['B']:.4f} C={sel['C']:.4f})")

    # ── Phase 4: Hidden state analysis ────────────────────
    hidden_results = None
    if not args.skip_hidden:
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"  Phase 4: Hidden state trajectory", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)

        t0 = time.time()
        hidden_results = compute_hidden_state_analysis(
            model, tokenizer, PROBES, quick=args.quick)
        t_hidden = time.time() - t0
        print(f"  Hidden state analysis: {t_hidden:.1f}s", file=sys.stderr)

        print(f"\n  Hidden state norms by combinator:")
        print(f"  {'Comb':>5}", end="")
        for l in range(N_LAYERS):
            print(f" {'L'+str(l):>7}", end="")
        print()
        for cname in comb_names:
            norms = hidden_results[cname]["avg_norms"]
            print(f"  {cname:>5}", end="")
            for l in range(N_LAYERS):
                key = str(l)
                if key in norms:
                    print(f" {norms[key]:>7.1f}", end="")
                else:
                    print(f" {'—':>7}", end="")
            print()

        print(f"\n  Cosine similarity (layer-to-layer transformation rate):")
        for cname in comb_names:
            cosines = hidden_results[cname]["avg_cosines"]
            print(f"    {cname}: ", end="")
            for key, val in sorted(cosines.items()):
                print(f"{key}={val:.4f} ", end="")
            print()

    # ── Phase 5: Visualizations ───────────────────────────
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  Phase 5: Visualizations", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    plot_selectivity_heatmaps(selectivity, args.output_dir)
    plot_differential_map(diff_results, args.output_dir)
    plot_layer_profiles_with_montague(selectivity, args.output_dir)
    plot_cross_correlation(selectivity, args.output_dir)
    plot_32b_comparison(selectivity, args.output_dir)

    # ── Save JSON results ─────────────────────────────────
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model": MODEL_NAME,
        "n_layers": N_LAYERS,
        "n_heads": N_HEADS,
        "total_heads": N_LAYERS * N_HEADS,
        "quick_mode": args.quick,
        "hypothesis": "Session-004 Montague primitives are KIBC combinator circuits",
        "combinator_selectivity": {},
        "head_assignment": {
            c: int(np.sum(dominant == ci))
            for ci, c in enumerate(comb_names)
        },
        "head_assignment_pct": {
            c: float(np.sum(dominant == ci) / dominant.size * 100)
            for ci, c in enumerate(comb_names)
        },
        "cross_correlation": {
            f"{ci}_{cj}": float(np.corrcoef(flat[ci], flat[cj])[0, 1])
            for ci in comb_names for cj in comb_names
        },
        "montague_zone_analysis": {
            zone: {
                "layers": data["layers"],
                "label": data["label"],
                "dominant_combinator": data["dominant_combinator"],
                "mean_selectivity": data["mean_selectivity"],
                "head_distribution": data["head_distribution"],
            }
            for zone, data in montague_analysis.items()
        },
        "session004_circuit_mapping": {
            layer: {
                "role": data["role"],
                "dominant": data["dominant"],
                "mean_selectivity": data["mean_selectivity"],
            }
            for layer, data in circuit_map.items()
        },
        "comparison_32b": {
            "pythia_pcts": {c: float(np.sum(dominant == ci) / dominant.size * 100)
                          for ci, c in enumerate(comb_names)},
            "qwen_pcts": {"K": 31.3, "I": 14.7, "B": 31.3, "C": 22.6},
        },
    }

    # Per-combinator summary
    for cname in comb_names:
        data = selectivity[cname]["vs_control"]
        output["combinator_selectivity"][cname] = {
            "mean": float(data.mean()),
            "max": float(data.max()),
            "std": float(data.std()),
            "max_layer": int(np.unravel_index(np.argmax(data), data.shape)[0]),
            "max_head": int(np.unravel_index(np.argmax(data), data.shape)[1]),
            "mean_by_layer": [float(data[l].mean()) for l in range(N_LAYERS)],
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

    total_time = t_attn
    if hidden_results:
        total_time += t_hidden
    print(f"\n  Total analysis time: {total_time:.1f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
