#!/usr/bin/env python3
"""Probe: Is attention β-reduction? Variable binding and pipeline depth.

Theory (session 081):
  Attention IS β-reduction: (λx.M)N → M[x:=N]
  - Query at position i = "I need the value for variable x"
  - Key at position j = "I am the argument N"
  - Value at position j = "substitute me in"
  - Output at position i = M[x:=N]

  If true, then:
  1. Binding depth → layer depth (deeper bindings resolve later)
  2. Pipelining: each layer resolves one reduction step
  3. Attention at binding positions shows substitution pattern

Prior evidence (session 080 extended probe):
  - Binding lives at L21-L39 in Qwen3-32B
  - KIBC (routing/composition) lives at L0-L15
  - This is consistent: identify combinators first, then bind variables

This probe tests three hypotheses:
  H1: DEPTH SCALING — sentences with N binding steps activate
      layer N+k more than layer k (pipeline pushes binding deeper)
  H2: SEQUENTIAL RESOLUTION — for nested bindings, inner bindings
      resolve at earlier layers than outer bindings (pipeline order)
  H3: ATTENTION = SUBSTITUTION — at the layer where binding resolves,
      the bound position attends strongly to its binder

Method:
  - Designed sentences with 1, 2, 3, 4 binding depths
  - Track attention from specific "bound" token positions to their
    "binder" positions across all 64 layers
  - Measure at which layer each binding "peaks" (strongest attention
    from bound → binder)
  - Compare peak layers across binding depths

Model: Qwen3-32B (GGUF Q8, 64 layers × 64 heads)

Usage:
    uv run python scripts/explore/probe_beta_reduction.py
    uv run python scripts/explore/probe_beta_reduction.py --quick

Output: results/beta-reduction-probe/

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

DEFAULT_GGUF = "/Users/mwhitford/localai/models/Qwen3-32B-Q8_0.gguf"
HF_MODEL = "Qwen/Qwen3-32B"
OUTPUT_DIR = Path("results/beta-reduction-probe")

# From session 080 extended probe: binding zone
BINDING_ZONE = (21, 39)   # layers where binding was found
KIBC_ZONE = (0, 15)       # layers where combinators live


# ══════════════════════════════════════════════════════════════════
# Probe sentences — designed for binding depth measurement
#
# Each probe has:
#   - text: the sentence
#   - bindings: list of (bound_word, binder_word, depth) tuples
#     depth = how many reductions must happen before this binding
#     depth 1 = direct binding, depth 2 = depends on depth 1, etc.
#   - description: what this tests
#
# The key insight: we track WHERE each bound token attends across
# layers. If attention = β-reduction, deeper bindings should peak
# at later layers.
# ══════════════════════════════════════════════════════════════════

BINDING_DEPTH_PROBES = [
    # ── Depth 1: single binding ──────────────────────────────
    {
        "text": "The cat sleeps and it purrs loudly every single night.",
        "bindings": [("it", "cat", 1)],
        "depth": 1,
        "description": "Simple pronoun binding: it → cat",
    },
    {
        "text": "John saw himself clearly in the old bathroom mirror.",
        "bindings": [("himself", "John", 1)],
        "depth": 1,
        "description": "Reflexive binding: himself → John",
    },
    {
        "text": "The bird that sang flew away over the tall green trees.",
        "bindings": [("sang", "bird", 1)],
        "depth": 1,
        "description": "Relative clause: subject of 'sang' → bird",
    },

    # ── Depth 2: two sequential bindings ─────────────────────
    {
        "text": "The cat that chased the dog bit it on the tail quickly.",
        "bindings": [
            ("chased", "cat", 1),     # who chased? → cat
            ("it", "dog", 2),          # bit what? → dog (requires resolving rel clause first)
        ],
        "depth": 2,
        "description": "Relative clause + pronoun: chased→cat, it→dog",
    },
    {
        "text": "John told Mary that he loved her very much that evening.",
        "bindings": [
            ("he", "John", 1),         # he → John
            ("her", "Mary", 2),        # her → Mary (requires knowing he=John first)
        ],
        "depth": 2,
        "description": "Two pronoun bindings in complement clause",
    },
    {
        "text": "The student who read the book that was long passed the exam.",
        "bindings": [
            ("long", "book", 1),       # what was long? → book
            ("read", "student", 2),    # who read? → student (outer relative)
        ],
        "depth": 2,
        "description": "Nested relative clauses: inner then outer",
    },

    # ── Depth 3: three sequential bindings ───────────────────
    {
        "text": "The man who the dog that the cat scratched bit ran away from the park.",
        "bindings": [
            ("scratched", "cat", 1),   # who scratched? → cat
            ("bit", "dog", 2),         # who bit? → dog (after resolving cat scratched)
            ("ran", "man", 3),         # who ran? → man (after resolving dog bit)
        ],
        "depth": 3,
        "description": "Triple-nested relative: cat scratched → dog bit → man ran",
    },
    {
        "text": "John said that Mary believed that Bill knew that she lied to him.",
        "bindings": [
            ("knew", "Bill", 1),       # Bill knew
            ("believed", "Mary", 2),   # Mary believed (that Bill knew)
            ("she", "Mary", 2),        # she → Mary
            ("him", "Bill", 3),        # him → Bill (requires resolving she=Mary first)
        ],
        "depth": 3,
        "description": "Triple-nested complement with pronouns",
    },

    # ── Depth 4: four sequential bindings ────────────────────
    {
        "text": "The cat that the dog that the bird that the fish scared startled chased fled from the garden.",
        "bindings": [
            ("scared", "fish", 1),      # fish scared
            ("startled", "bird", 2),    # bird startled (after fish scared)
            ("chased", "dog", 3),       # dog chased (after bird startled)
            ("fled", "cat", 4),         # cat fled (after dog chased)
        ],
        "depth": 4,
        "description": "Quadruple-nested relative clauses",
    },
]

# ── Pipeline probes: same semantic content, different binding structure ──
# These test whether the model pipelines reductions or does them in parallel
PIPELINE_PROBES = [
    # Flat (all bindings independent, could be parallel)
    {
        "text": "John ate the apple and Mary drank the water and Bill read the book.",
        "bindings": [
            ("ate", "John", 1),
            ("drank", "Mary", 1),
            ("read", "Bill", 1),
        ],
        "depth": 1,
        "label": "flat_3_independent",
        "description": "Three independent clauses — no pipeline needed",
    },
    # Sequential (each depends on previous)
    {
        "text": "John told Mary that she should tell Bill that he should leave now.",
        "bindings": [
            ("she", "Mary", 1),         # she → Mary
            ("tell", "Mary", 1),        # Mary should tell
            ("he", "Bill", 2),          # he → Bill (after resolving inner clause)
            ("leave", "Bill", 2),       # Bill should leave
        ],
        "depth": 2,
        "label": "sequential_2_chained",
        "description": "Chained complement clauses — pipeline required",
    },
    # Mixed (some parallel, some sequential)
    {
        "text": "The cat that chased the dog and the bird that saw the fish both ran away.",
        "bindings": [
            ("chased", "cat", 1),       # cat chased (independent)
            ("saw", "bird", 1),         # bird saw (independent)
            ("ran", "cat", 2),          # both ran → cat+bird (depends on resolving both)
        ],
        "depth": 2,
        "label": "mixed_parallel_then_merge",
        "description": "Two independent relatives, then merged subject",
    },
]

# ── Substitution probes: test if attention shows value substitution ──
# Minimal pairs where only the binding target changes
SUBSTITUTION_PROBES = [
    {
        "text_a": "The cat that the dog chased ran away quickly through the garden.",
        "text_b": "The bird that the dog chased ran away quickly through the garden.",
        "binding_word": "chased",
        "target_a": "cat",
        "target_b": "bird",
        "description": "Same structure, different binding target",
    },
    {
        "text_a": "John said that he was tired after the long difficult day.",
        "text_b": "Mary said that she was tired after the long difficult day.",
        "binding_word_a": "he",
        "binding_word_b": "she",
        "target_a": "John",
        "target_b": "Mary",
        "description": "Pronoun resolves to different antecedent",
    },
]


# ══════════════════════════════════════════════════════════════════
# Model loading (reuse from combinator probe)
# ══════════════════════════════════════════════════════════════════


def load_model(gguf_path: str, device: str = "mps"):
    """Load Qwen3-32B from GGUF."""
    gguf_dir = str(Path(gguf_path).parent)
    gguf_file = Path(gguf_path).name

    print(f"Loading model from {gguf_path}...", file=sys.stderr)
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        gguf_dir, gguf_file=gguf_file,
        dtype=torch.float16, device_map=device,
        trust_remote_code=True,
        attn_implementation="eager",
    )
    model.eval()
    model.config.output_attentions = True

    t1 = time.time()
    print(f"Loaded in {t1-t0:.1f}s: {model.config.num_hidden_layers} layers, "
          f"{model.config.num_attention_heads} heads, "
          f"d={model.config.hidden_size}", file=sys.stderr)
    return model, tokenizer


# ══════════════════════════════════════════════════════════════════
# Token position finder
# ══════════════════════════════════════════════════════════════════


def find_token_positions(token_strs: list[str], word: str) -> list[int]:
    """Find positions where a word appears in tokenized text.

    Handles subword tokenization: looks for tokens that contain the word
    (case-insensitive) or tokens that start/end the word.
    Returns all matching positions.
    """
    positions = []
    word_lower = word.lower()

    for i, tok in enumerate(token_strs):
        # Strip leading space/special chars that tokenizers add
        tok_clean = tok.strip().lower()
        # Remove common tokenizer prefixes
        for prefix in ["Ġ", "▁", " "]:
            if tok_clean.startswith(prefix.lower()):
                tok_clean = tok_clean[len(prefix):]

        if tok_clean == word_lower:
            positions.append(i)
        elif word_lower.startswith(tok_clean) and len(tok_clean) >= 2:
            positions.append(i)

    return positions


# ══════════════════════════════════════════════════════════════════
# Attention capture (per-position tracking)
# ══════════════════════════════════════════════════════════════════


def capture_attention(model, tokenizer, text: str) -> dict:
    """Capture full attention patterns.

    Returns:
        {
            "token_ids": list[int],
            "token_strs": list[str],
            "attentions": np.ndarray (n_layers, n_heads, seq_len, seq_len),
        }
    """
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    token_ids = inputs["input_ids"][0].tolist()
    token_strs = [tokenizer.decode([tid]) for tid in token_ids]

    with torch.no_grad():
        outputs = model(**inputs, output_attentions=True)

    attn_list = []
    for layer_attn in outputs.attentions:
        attn_list.append(layer_attn[0].cpu().half().numpy())

    attentions = np.stack(attn_list, axis=0)  # (n_layers, n_heads, seq, seq)

    return {
        "token_ids": token_ids,
        "token_strs": token_strs,
        "attentions": attentions,
    }


def binding_attention_profile(
    attentions: np.ndarray,
    bound_positions: list[int],
    binder_positions: list[int],
) -> np.ndarray:
    """Measure how strongly bound positions attend to binder positions.

    For each layer and head, compute the mean attention from
    bound_positions → binder_positions.

    Returns: (n_layers, n_heads) — attention strength per layer per head.
    """
    n_layers, n_heads = attentions.shape[:2]
    profile = np.zeros((n_layers, n_heads), dtype=np.float32)

    for bp in bound_positions:
        for br in binder_positions:
            if bp > br:  # causal: bound can attend to binder only if binder is earlier
                profile += attentions[:, :, bp, br].astype(np.float32)

    # Normalize by number of position pairs
    n_pairs = sum(1 for bp in bound_positions for br in binder_positions if bp > br)
    if n_pairs > 0:
        profile /= n_pairs

    return profile


# ══════════════════════════════════════════════════════════════════
# Analysis: binding depth → layer depth
# ══════════════════════════════════════════════════════════════════


def analyze_binding_depths(
    model, tokenizer, probes: list[dict],
) -> dict:
    """For each probe, measure at which layer each binding peaks.

    Returns per-binding: {peak_layer, peak_strength, layer_profile}
    """
    results = []

    for probe in probes:
        text = probe["text"]
        print(f"  Probing: {probe['description'][:60]}...", file=sys.stderr)

        cap = capture_attention(model, tokenizer, text)
        attn = cap["attentions"]
        token_strs = cap["token_strs"]

        print(f"    Tokens: {' '.join(repr(t) for t in token_strs[:30])}...",
              file=sys.stderr)

        binding_results = []
        for binding in probe["bindings"]:
            bound_word, binder_word, depth = binding

            bound_pos = find_token_positions(token_strs, bound_word)
            binder_pos = find_token_positions(token_strs, binder_word)

            if not bound_pos or not binder_pos:
                print(f"    ⚠ Could not find '{bound_word}'→'{binder_word}' "
                      f"in tokens", file=sys.stderr)
                binding_results.append({
                    "bound": bound_word, "binder": binder_word,
                    "depth": depth, "found": False,
                })
                continue

            # Use first occurrence of each
            profile = binding_attention_profile(
                attn, bound_pos[:1], binder_pos[:1])

            # Max across heads per layer
            layer_max = profile.max(axis=1)  # (n_layers,)
            # Mean across heads per layer
            layer_mean = profile.mean(axis=1)

            peak_layer = int(np.argmax(layer_max))
            peak_strength = float(layer_max[peak_layer])

            # Also compute centroid (weighted average layer)
            weights = layer_mean / (layer_mean.sum() + 1e-8)
            centroid = float(np.sum(np.arange(len(weights)) * weights))

            # Top 5 heads at peak layer
            peak_heads = np.argsort(profile[peak_layer])[-5:][::-1]
            top_heads = [
                {"head": int(h), "attention": float(profile[peak_layer, h])}
                for h in peak_heads
            ]

            binding_results.append({
                "bound": bound_word, "binder": binder_word,
                "depth": depth, "found": True,
                "bound_pos": bound_pos[:1],
                "binder_pos": binder_pos[:1],
                "peak_layer": peak_layer,
                "peak_strength": peak_strength,
                "centroid_layer": round(centroid, 2),
                "layer_profile_max": layer_max.tolist(),
                "layer_profile_mean": layer_mean.tolist(),
                "top_heads_at_peak": top_heads,
            })

            print(f"    {bound_word}→{binder_word} (depth {depth}): "
                  f"peak=L{peak_layer} strength={peak_strength:.4f} "
                  f"centroid=L{centroid:.1f}",
                  file=sys.stderr)

        torch.mps.empty_cache() if torch.backends.mps.is_available() else None

        results.append({
            "text": text,
            "description": probe["description"],
            "max_depth": probe["depth"],
            "bindings": binding_results,
        })

    return results


# ══════════════════════════════════════════════════════════════════
# Analysis: pipeline structure
# ══════════════════════════════════════════════════════════════════


def analyze_pipeline(
    model, tokenizer, probes: list[dict],
) -> dict:
    """Test whether bindings resolve sequentially (pipeline) or in parallel."""
    results = []

    for probe in probes:
        text = probe["text"]
        label = probe.get("label", "unknown")
        print(f"  Pipeline probe: {label}...", file=sys.stderr)

        cap = capture_attention(model, tokenizer, text)
        attn = cap["attentions"]
        token_strs = cap["token_strs"]

        binding_peaks = []
        for binding in probe["bindings"]:
            bound_word, binder_word, depth = binding
            bound_pos = find_token_positions(token_strs, bound_word)
            binder_pos = find_token_positions(token_strs, binder_word)

            if not bound_pos or not binder_pos:
                binding_peaks.append({
                    "bound": bound_word, "binder": binder_word,
                    "depth": depth, "found": False,
                })
                continue

            profile = binding_attention_profile(
                attn, bound_pos[:1], binder_pos[:1])
            layer_max = profile.max(axis=1)
            peak = int(np.argmax(layer_max))
            weights = layer_max / (layer_max.sum() + 1e-8)
            centroid = float(np.sum(np.arange(len(weights)) * weights))

            binding_peaks.append({
                "bound": bound_word, "binder": binder_word,
                "depth": depth, "found": True,
                "peak_layer": peak,
                "centroid_layer": round(centroid, 2),
                "peak_strength": float(layer_max[peak]),
            })

        torch.mps.empty_cache() if torch.backends.mps.is_available() else None

        # Analyze pipeline order
        found_bindings = [b for b in binding_peaks if b.get("found")]
        if found_bindings:
            by_depth = sorted(found_bindings, key=lambda b: b["depth"])
            peaks_by_depth = [(b["depth"], b["peak_layer"], b["centroid_layer"])
                             for b in by_depth]

            # Check if deeper bindings → later layers
            depths = [p[0] for p in peaks_by_depth]
            peaks = [p[1] for p in peaks_by_depth]
            centroids = [p[2] for p in peaks_by_depth]

            # Correlation between depth and peak layer
            if len(set(depths)) > 1:
                depth_peak_corr = float(np.corrcoef(depths, peaks)[0, 1]) if len(depths) > 2 else 0.0
                depth_centroid_corr = float(np.corrcoef(depths, centroids)[0, 1]) if len(depths) > 2 else 0.0
            else:
                depth_peak_corr = 0.0
                depth_centroid_corr = 0.0
        else:
            depth_peak_corr = 0.0
            depth_centroid_corr = 0.0

        results.append({
            "text": text,
            "label": label,
            "description": probe["description"],
            "max_depth": probe["depth"],
            "bindings": binding_peaks,
            "depth_peak_correlation": depth_peak_corr,
            "depth_centroid_correlation": depth_centroid_corr,
        })

    return results


# ══════════════════════════════════════════════════════════════════
# Analysis: substitution pattern
# ══════════════════════════════════════════════════════════════════


def analyze_substitution(
    model, tokenizer, probes: list[dict],
) -> dict:
    """Test whether attention shows substitution pattern.

    For minimal pairs where only the binding target changes,
    measure whether the attention at the bound position shifts
    from target_a to target_b.
    """
    results = []

    for probe in probes:
        print(f"  Substitution probe: {probe['description'][:50]}...",
              file=sys.stderr)

        cap_a = capture_attention(model, tokenizer, probe["text_a"])
        cap_b = capture_attention(model, tokenizer, probe["text_b"])

        bound_word_a = probe.get("binding_word_a", probe.get("binding_word"))
        bound_word_b = probe.get("binding_word_b", probe.get("binding_word"))

        bound_pos_a = find_token_positions(cap_a["token_strs"], bound_word_a)
        bound_pos_b = find_token_positions(cap_b["token_strs"], bound_word_b)

        target_pos_a = find_token_positions(cap_a["token_strs"], probe["target_a"])
        target_pos_b = find_token_positions(cap_b["token_strs"], probe["target_b"])

        if not all([bound_pos_a, bound_pos_b, target_pos_a, target_pos_b]):
            results.append({
                "description": probe["description"],
                "found": False,
            })
            continue

        # In text_a: how strongly does bound attend to target_a?
        profile_a = binding_attention_profile(
            cap_a["attentions"], bound_pos_a[:1], target_pos_a[:1])

        # In text_b: how strongly does bound attend to target_b?
        profile_b = binding_attention_profile(
            cap_b["attentions"], bound_pos_b[:1], target_pos_b[:1])

        layer_max_a = profile_a.max(axis=1)
        layer_max_b = profile_b.max(axis=1)

        # Cross-check: in text_a, does bound attend to where target_b would be?
        # (It shouldn't — wrong target)

        # Similarity of layer profiles (should be similar if same mechanism)
        profile_corr = float(np.corrcoef(layer_max_a, layer_max_b)[0, 1])

        results.append({
            "description": probe["description"],
            "found": True,
            "text_a_peak": int(np.argmax(layer_max_a)),
            "text_b_peak": int(np.argmax(layer_max_b)),
            "text_a_strength": float(layer_max_a.max()),
            "text_b_strength": float(layer_max_b.max()),
            "profile_correlation": profile_corr,
            "layer_profile_a": layer_max_a.tolist(),
            "layer_profile_b": layer_max_b.tolist(),
        })

        print(f"    A peak=L{int(np.argmax(layer_max_a))} "
              f"B peak=L{int(np.argmax(layer_max_b))} "
              f"profile_corr={profile_corr:.3f}",
              file=sys.stderr)

        torch.mps.empty_cache() if torch.backends.mps.is_available() else None

    return results


# ══════════════════════════════════════════════════════════════════
# Visualization
# ══════════════════════════════════════════════════════════════════


def plot_depth_vs_layer(binding_results: list[dict], output_dir: Path):
    """Scatter: binding depth vs peak layer / centroid layer."""
    depths = []
    peak_layers = []
    centroid_layers = []
    labels = []
    colors_depth = {1: "#3498db", 2: "#2ecc71", 3: "#f39c12", 4: "#e74c3c"}

    for probe_result in binding_results:
        for b in probe_result["bindings"]:
            if b.get("found"):
                d = b["depth"]
                depths.append(d)
                peak_layers.append(b["peak_layer"])
                centroid_layers.append(b["centroid_layer"])
                labels.append(f"{b['bound']}→{b['binder']}")

    if not depths:
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle("Binding Depth vs Layer — Qwen3-32B\n"
                 "Does deeper binding → later layer? (attention = β-reduction)",
                 fontsize=13, fontweight="bold")

    # Peak layer scatter
    for i, (d, p, c, lbl) in enumerate(zip(depths, peak_layers, centroid_layers, labels)):
        ax1.scatter(d, p, c=colors_depth.get(d, "#999"),
                    s=100, zorder=5, edgecolors="black", linewidth=0.5)
        ax1.annotate(lbl, (d, p), textcoords="offset points",
                     xytext=(5, 5), fontsize=7, alpha=0.8)

    ax1.set_xlabel("Binding depth", fontsize=12)
    ax1.set_ylabel("Peak attention layer", fontsize=12)
    ax1.set_title("Peak layer (max attention across heads)")

    # Binding zone overlay
    ax1.axhspan(BINDING_ZONE[0], BINDING_ZONE[1], alpha=0.1, color="#e74c3c",
                label=f"Session 080 binding zone (L{BINDING_ZONE[0]}-L{BINDING_ZONE[1]})")
    ax1.axhspan(KIBC_ZONE[0], KIBC_ZONE[1], alpha=0.1, color="#3498db",
                label=f"KIBC zone (L{KIBC_ZONE[0]}-L{KIBC_ZONE[1]})")
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # Centroid layer scatter
    for i, (d, p, c, lbl) in enumerate(zip(depths, peak_layers, centroid_layers, labels)):
        ax2.scatter(d, c, c=colors_depth.get(d, "#999"),
                    s=100, zorder=5, edgecolors="black", linewidth=0.5)
        ax2.annotate(lbl, (d, c), textcoords="offset points",
                     xytext=(5, 5), fontsize=7, alpha=0.8)

    ax2.set_xlabel("Binding depth", fontsize=12)
    ax2.set_ylabel("Centroid layer (weighted average)", fontsize=12)
    ax2.set_title("Centroid layer (attention-weighted mean)")
    ax2.axhspan(BINDING_ZONE[0], BINDING_ZONE[1], alpha=0.1, color="#e74c3c")
    ax2.axhspan(KIBC_ZONE[0], KIBC_ZONE[1], alpha=0.1, color="#3498db")
    ax2.grid(True, alpha=0.3)

    # Trend line if enough points
    if len(depths) >= 3:
        z = np.polyfit(depths, centroid_layers, 1)
        p = np.poly1d(z)
        x_fit = np.linspace(min(depths) - 0.2, max(depths) + 0.2, 50)
        ax2.plot(x_fit, p(x_fit), "--", color="#e74c3c", alpha=0.5,
                 label=f"trend: {z[0]:.1f} layers/depth")
        corr = np.corrcoef(depths, centroid_layers)[0, 1]
        ax2.set_title(f"Centroid layer (r={corr:.3f} with depth)")
        ax2.legend(fontsize=9)

    plt.tight_layout()
    fig.savefig(output_dir / "depth_vs_layer.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: depth_vs_layer.png", file=sys.stderr)


def plot_binding_layer_profiles(binding_results: list[dict], output_dir: Path):
    """Layer-by-layer attention profile for each binding, grouped by depth."""
    colors_depth = {1: "#3498db", 2: "#2ecc71", 3: "#f39c12", 4: "#e74c3c"}

    fig, axes = plt.subplots(2, 2, figsize=(18, 14))
    fig.suptitle("Binding Attention Profiles by Layer — Qwen3-32B\n"
                 "Max attention from bound→binder across all heads per layer",
                 fontsize=13, fontweight="bold")

    for depth in [1, 2, 3, 4]:
        ax = axes[(depth - 1) // 2][(depth - 1) % 2]

        found = False
        for probe_result in binding_results:
            for b in probe_result["bindings"]:
                if b.get("found") and b["depth"] == depth:
                    profile = b["layer_profile_max"]
                    label = f"{b['bound']}→{b['binder']}"
                    ax.plot(profile, alpha=0.7, linewidth=1.5, label=label)
                    found = True

        if found:
            # Binding zone overlay
            ax.axvspan(BINDING_ZONE[0], BINDING_ZONE[1], alpha=0.08,
                      color="#e74c3c")
            ax.axvspan(KIBC_ZONE[0], KIBC_ZONE[1], alpha=0.08,
                      color="#3498db")

        ax.set_title(f"Depth {depth}", fontsize=12, fontweight="bold",
                     color=colors_depth.get(depth, "#999"))
        ax.set_xlabel("Layer")
        ax.set_ylabel("Max attention (bound→binder)")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_dir / "binding_layer_profiles.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: binding_layer_profiles.png", file=sys.stderr)


def plot_pipeline_comparison(pipeline_results: list[dict], output_dir: Path):
    """Compare flat vs sequential vs mixed pipeline structures."""
    fig, axes = plt.subplots(1, len(pipeline_results), figsize=(6 * len(pipeline_results), 6))
    if len(pipeline_results) == 1:
        axes = [axes]

    fig.suptitle("Pipeline Structure — Qwen3-32B\n"
                 "Do bindings resolve in sequence (pipeline) or parallel?",
                 fontsize=13, fontweight="bold")

    colors_depth = {1: "#3498db", 2: "#2ecc71", 3: "#f39c12"}

    for idx, probe_result in enumerate(pipeline_results):
        ax = axes[idx]
        label = probe_result.get("label", f"probe_{idx}")

        for b in probe_result["bindings"]:
            if b.get("found"):
                depth = b["depth"]
                ax.barh(f"{b['bound']}→{b['binder']}\n(d={depth})",
                        b["peak_layer"],
                        color=colors_depth.get(depth, "#999"),
                        height=0.6, alpha=0.8)
                ax.plot(b["centroid_layer"],
                        f"{b['bound']}→{b['binder']}\n(d={depth})",
                        "k*", markersize=10)

        ax.set_xlabel("Layer")
        ax.set_title(f"{label}\ncorr(depth,peak)={probe_result.get('depth_peak_correlation', 0):.2f}",
                     fontsize=10)
        ax.axvspan(BINDING_ZONE[0], BINDING_ZONE[1], alpha=0.08, color="#e74c3c")
        ax.axvspan(KIBC_ZONE[0], KIBC_ZONE[1], alpha=0.08, color="#3498db")
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_dir / "pipeline_comparison.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: pipeline_comparison.png", file=sys.stderr)


def plot_substitution_profiles(subst_results: list[dict], output_dir: Path):
    """Layer profiles for substitution pairs — do they use the same mechanism?"""
    fig, axes = plt.subplots(1, len(subst_results), figsize=(8 * len(subst_results), 6))
    if len(subst_results) == 1:
        axes = [axes]

    fig.suptitle("Substitution Test — Qwen3-32B\n"
                 "Minimal pairs: same structure, different binding target.\n"
                 "If attention = β-reduction, same layer profile different values.",
                 fontsize=12, fontweight="bold")

    for idx, sr in enumerate(subst_results):
        ax = axes[idx]
        if not sr.get("found"):
            ax.text(0.5, 0.5, "Not found", transform=ax.transAxes, ha="center")
            continue

        ax.plot(sr["layer_profile_a"], "b-", linewidth=2, alpha=0.8,
                label=f"A (peak L{sr['text_a_peak']})")
        ax.plot(sr["layer_profile_b"], "r-", linewidth=2, alpha=0.8,
                label=f"B (peak L{sr['text_b_peak']})")
        ax.axvspan(BINDING_ZONE[0], BINDING_ZONE[1], alpha=0.08, color="#e74c3c")

        ax.set_xlabel("Layer")
        ax.set_ylabel("Max attention (bound→binder)")
        ax.set_title(f"{sr['description']}\nprofile_corr={sr['profile_correlation']:.3f}",
                     fontsize=10)
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_dir / "substitution_profiles.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: substitution_profiles.png", file=sys.stderr)


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(
        description="Beta reduction probe — Qwen3-32B")
    parser.add_argument("--gguf", default=DEFAULT_GGUF)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--quick", action="store_true",
                        help="Fewer probes")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    model, tokenizer = load_model(args.gguf, args.device)
    n_layers = model.config.num_hidden_layers
    n_heads = model.config.num_attention_heads

    # ── H1: Binding depth → layer depth ───────────────────
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  H1: Binding depth → layer depth", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    depth_probes = BINDING_DEPTH_PROBES
    if args.quick:
        depth_probes = [p for p in depth_probes if p["depth"] <= 2][:4]

    t0 = time.time()
    binding_results = analyze_binding_depths(model, tokenizer, depth_probes)
    t_bind = time.time() - t0
    print(f"\n  Binding analysis: {t_bind:.1f}s", file=sys.stderr)

    # Summary: depth vs peak layer
    print(f"\n  Binding depth → layer summary:")
    print(f"  {'Depth':>5} {'Bound':>12} {'Binder':>12} {'Peak':>6} {'Centroid':>9} {'Strength':>9}")
    print(f"  {'─'*5} {'─'*12} {'─'*12} {'─'*6} {'─'*9} {'─'*9}")

    all_depths = []
    all_peaks = []
    all_centroids = []
    for pr in binding_results:
        for b in pr["bindings"]:
            if b.get("found"):
                print(f"  {b['depth']:>5} {b['bound']:>12} {b['binder']:>12} "
                      f"L{b['peak_layer']:>4} L{b['centroid_layer']:>7.1f} "
                      f"{b['peak_strength']:>9.4f}")
                all_depths.append(b["depth"])
                all_peaks.append(b["peak_layer"])
                all_centroids.append(b["centroid_layer"])

    if len(all_depths) >= 3:
        depth_peak_r = float(np.corrcoef(all_depths, all_peaks)[0, 1])
        depth_centroid_r = float(np.corrcoef(all_depths, all_centroids)[0, 1])
        print(f"\n  Correlation (depth → peak layer):     r = {depth_peak_r:.3f}")
        print(f"  Correlation (depth → centroid layer):  r = {depth_centroid_r:.3f}")
        if depth_centroid_r > 0.5:
            print(f"  ✓ SUPPORTS H1: deeper binding → later layer")
        elif depth_centroid_r < -0.1:
            print(f"  ✗ CONTRADICTS H1: deeper binding → earlier layer (?)")
        else:
            print(f"  ? INCONCLUSIVE: weak correlation")

    # ── H2: Pipeline structure ────────────────────────────
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  H2: Pipeline structure", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    pipe_probes = PIPELINE_PROBES
    if args.quick:
        pipe_probes = pipe_probes[:2]

    t0 = time.time()
    pipeline_results = analyze_pipeline(model, tokenizer, pipe_probes)
    t_pipe = time.time() - t0
    print(f"\n  Pipeline analysis: {t_pipe:.1f}s", file=sys.stderr)

    print(f"\n  Pipeline results:")
    for pr in pipeline_results:
        print(f"\n    {pr['label']}: depth_peak_corr={pr['depth_peak_correlation']:.3f}")
        for b in pr["bindings"]:
            if b.get("found"):
                print(f"      {b['bound']:>10}→{b['binder']:<10} "
                      f"depth={b['depth']} peak=L{b['peak_layer']} "
                      f"centroid=L{b['centroid_layer']:.1f}")

    # ── H3: Substitution pattern ──────────────────────────
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  H3: Substitution pattern", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    t0 = time.time()
    subst_results = analyze_substitution(model, tokenizer, SUBSTITUTION_PROBES)
    t_subst = time.time() - t0
    print(f"\n  Substitution analysis: {t_subst:.1f}s", file=sys.stderr)

    print(f"\n  Substitution results:")
    for sr in subst_results:
        if sr.get("found"):
            print(f"    {sr['description']}")
            print(f"      A peak=L{sr['text_a_peak']}  B peak=L{sr['text_b_peak']}  "
                  f"profile_corr={sr['profile_correlation']:.3f}")
            if sr['profile_correlation'] > 0.8:
                print(f"      ✓ Same mechanism, different values (supports β-reduction)")
            elif sr['profile_correlation'] > 0.5:
                print(f"      ~ Partially similar mechanism")
            else:
                print(f"      ✗ Different mechanisms")

    # ── Visualizations ────────────────────────────────────
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  Visualizations", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    plot_depth_vs_layer(binding_results, args.output_dir)
    plot_binding_layer_profiles(binding_results, args.output_dir)
    plot_pipeline_comparison(pipeline_results, args.output_dir)
    plot_substitution_profiles(subst_results, args.output_dir)

    # ── Save results ──────────────────────────────────────
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model": HF_MODEL,
        "n_layers": n_layers,
        "n_heads": n_heads,
        "hypothesis": "Attention is β-reduction: binding depth → layer depth, pipeline resolution",
        "binding_depth_results": binding_results,
        "pipeline_results": pipeline_results,
        "substitution_results": subst_results,
        "summary": {
            "depth_peak_correlation": depth_peak_r if len(all_depths) >= 3 else None,
            "depth_centroid_correlation": depth_centroid_r if len(all_depths) >= 3 else None,
            "n_bindings_found": len(all_depths),
            "n_bindings_total": sum(len(pr["bindings"]) for pr in binding_results),
            "mean_peak_by_depth": {},
            "mean_centroid_by_depth": {},
        },
    }

    # Mean peak/centroid by depth
    for d in sorted(set(all_depths)):
        idx = [i for i, dd in enumerate(all_depths) if dd == d]
        output["summary"]["mean_peak_by_depth"][str(d)] = float(np.mean([all_peaks[i] for i in idx]))
        output["summary"]["mean_centroid_by_depth"][str(d)] = float(np.mean([all_centroids[i] for i in idx]))

    json_path = args.output_dir / "beta_reduction_results.json"
    json_path.write_text(json.dumps(output, indent=2, default=str))

    print(f"\n  💾 Results: {json_path}", file=sys.stderr)
    print(f"  🖼  Plots: {args.output_dir}/*.png", file=sys.stderr)

    total = t_bind + t_pipe + t_subst
    print(f"\n  Total analysis time: {total:.1f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
