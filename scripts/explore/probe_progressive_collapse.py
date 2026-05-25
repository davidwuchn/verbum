#!/usr/bin/env python3
"""
Progressive Dimensionality Collapse — Qwen3.6-27B Teacher Probe.

Hypothesis: Each layer's attention soft-reduction is a beta reduction
(projection). The residual stream's effective dimensionality should
show the lens pattern: expand (aperture→fan) then collapse (→converge).

At micro scale (4 layers, d=128): we saw 2D→8D→2D in crystal space.
But the micro model is B-dominated (undifferentiated state machine).

The teacher (64 layers, d=5120, hundreds of billions of tokens) should
show the COMPLETE arc: the full combinator differentiation, the phase
transition where K/I/C separate from initial B domination, and the
converge back to low-D for output.

Measures at each of 64 layer boundaries:
  1. SVD effective rank (model space) — 80%, 90%, 95% thresholds
  2. Participation ratio (continuous rank measure)
  3. Top singular value concentration (σ₁/σ_total)
  4. Per-PC energy in crystal eigenbasis (if crystal embeddings available)
  5. Attention entropy per layer (how peaked is the soft reduction?)

Usage:
    cd verbum
    uv run python scripts/explore/probe_progressive_collapse.py

Requires: ~54 GB RAM (bf16 model), torch, transformers
License: MIT
"""

from __future__ import annotations

import sys
import time
import json
from pathlib import Path

import numpy as np
import torch

# ══════════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════════

MODEL_NAME = sys.argv[1] if len(sys.argv) > 1 else "Qwen/Qwen3.6-27B"
DEVICE = "mps"  # Apple Silicon
DTYPE = torch.bfloat16

# Probe texts — diverse structures to average over
PROBE_TEXTS = [
    "The cat sits on the mat while the dog runs through the garden chasing butterflies in the warm afternoon sun.",
    "Every student reads a book about mathematics before the final exam, hoping to understand the key concepts well enough to pass.",
    "If the weather is good tomorrow, we will go to the park and have a picnic with the whole family, bringing sandwiches and lemonade.",
    "The function applies the argument to produce a result, which is then passed to the next stage of computation in the evaluation pipeline.",
    "Lambda calculus is a formal system in mathematical logic for expressing computation based on function abstraction and application using variable binding and substitution.",
    "John, who Mary likes, runs quickly through the dense forest while the sun sets behind the distant mountains, casting long shadows across the valley below.",
    "The president announced that the committee would review the proposal before the deadline expires next month, and that all stakeholders should submit their feedback in writing.",
    "According to Church's theorem, there exists no general effective decision procedure for statements of first-order arithmetic, which has profound implications for the foundations of mathematics and computer science.",
]

# Crystal eigenbasis from Zone B targets (same as micro model)
# We'll use this to project teacher residuals into crystal space
PCAQ_ZONE_B_TARGETS = np.array([
    [+1.0000, +0.7865, +0.1948, +0.2265, +0.3232, +0.1768, +0.5360, -0.1862, -0.1900, -0.1494, -0.0370, -0.0430, -0.0614, -0.0336, -0.1018, +0.0354],
    [+0.7865, +1.0000, +0.2479, +0.2511, +0.3463, +0.1739, +0.3781, -0.2448, -0.1494, -0.1900, -0.0471, -0.0477, -0.0658, -0.0330, -0.0718, +0.0465],
    [+0.1948, +0.2479, +1.0000, +0.8878, +0.8937, +0.6623, +0.6851, -0.1227, -0.0370, -0.0471, -0.1900, -0.1687, -0.1698, -0.1258, -0.1302, +0.0233],
    [+0.2265, +0.2511, +0.8878, +1.0000, +0.8316, +0.7200, +0.7318, -0.1027, -0.0430, -0.0477, -0.1687, -0.1900, -0.1580, -0.1368, -0.1390, +0.0195],
    [+0.3232, +0.3463, +0.8937, +0.8316, +1.0000, +0.6798, +0.8064, -0.1729, -0.0614, -0.0658, -0.1698, -0.1580, -0.1900, -0.1292, -0.1532, +0.0329],
    [+0.1768, +0.1739, +0.6623, +0.7200, +0.6798, +1.0000, +0.5653, -0.0840, -0.0336, -0.0330, -0.1258, -0.1368, -0.1292, -0.1900, -0.1074, +0.0160],
    [+0.5360, +0.3781, +0.6851, +0.7318, +0.8064, +0.5653, +1.0000, -0.1379, -0.1018, -0.0718, -0.1302, -0.1390, -0.1532, -0.1074, -0.1900, +0.0262],
    [-0.1862, -0.2448, -0.1227, -0.1027, -0.1729, -0.0840, -0.1379, +1.0000, +0.0354, +0.0465, +0.0233, +0.0195, +0.0329, +0.0160, +0.0262, -0.1900],
    [-0.1900, -0.1494, -0.0370, -0.0430, -0.0614, -0.0336, -0.1018, +0.0354, +1.0000, +0.7865, +0.1948, +0.2265, +0.3232, +0.1768, +0.5360, -0.1862],
    [-0.1494, -0.1900, -0.0471, -0.0477, -0.0658, -0.0330, -0.0718, +0.0465, +0.7865, +1.0000, +0.2479, +0.2511, +0.3463, +0.1739, +0.3781, -0.2448],
    [-0.0370, -0.0471, -0.1900, -0.1687, -0.1698, -0.1258, -0.1302, +0.0233, +0.1948, +0.2479, +1.0000, +0.8878, +0.8937, +0.6623, +0.6851, -0.1227],
    [-0.0430, -0.0477, -0.1687, -0.1900, -0.1580, -0.1368, -0.1390, +0.0195, +0.2265, +0.2511, +0.8878, +1.0000, +0.8316, +0.7200, +0.7318, -0.1027],
    [-0.0614, -0.0658, -0.1698, -0.1580, -0.1900, -0.1292, -0.1532, +0.0329, +0.3232, +0.3463, +0.8937, +0.8316, +1.0000, +0.6798, +0.8064, -0.1729],
    [-0.0336, -0.0330, -0.1258, -0.1368, -0.1292, -0.1900, -0.1074, +0.0160, +0.1768, +0.1739, +0.6623, +0.7200, +0.6798, +1.0000, +0.5653, -0.0840],
    [-0.1018, -0.0718, -0.1302, -0.1390, -0.1532, -0.1074, -0.1900, +0.0262, +0.5360, +0.3781, +0.6851, +0.7318, +0.8064, +0.5653, +1.0000, -0.1379],
    [+0.0354, +0.0465, +0.0233, +0.0195, +0.0329, +0.0160, +0.0262, -0.1900, -0.1862, -0.2448, -0.1227, -0.1027, -0.1729, -0.0840, -0.1379, +1.0000],
], dtype=np.float32)


def get_crystal_eigenbasis():
    """Eigendecompose crystal target for projection."""
    eigvals, eigvecs = np.linalg.eigh(PCAQ_ZONE_B_TARGETS)
    idx = np.argsort(eigvals)[::-1]
    return eigvals[idx], eigvecs[:, idx]


# ══════════════════════════════════════════════════════════════════════
# Model loading
# ══════════════════════════════════════════════════════════════════════

def load_model():
    """Load Qwen3.6-27B."""
    from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig

    print(f"\n  Loading {MODEL_NAME}...", flush=True)
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    config = AutoConfig.from_pretrained(MODEL_NAME, trust_remote_code=True)

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=DTYPE,
        device_map=DEVICE,
        trust_remote_code=True,
        attn_implementation="eager",
    )
    model.eval()

    dt = time.time() - t0
    # Get text config for hybrid models
    text_cfg = getattr(config, 'text_config', config)
    n_layers = getattr(text_cfg, 'num_hidden_layers', 64)
    d_model = getattr(text_cfg, 'hidden_size', 5120)
    layer_types = getattr(text_cfg, 'layer_types', [])

    print(f"  Loaded in {dt:.1f}s", flush=True)
    print(f"  Layers: {n_layers}  d_model: {d_model}", flush=True)
    if layer_types:
        n_linear = sum(1 for t in layer_types if t == 'linear_attention')
        n_full = sum(1 for t in layer_types if t == 'full_attention')
        print(f"  Layer types: {n_linear} linear + {n_full} full attention", flush=True)

    return model, tokenizer, text_cfg


def get_layers(model):
    """Get transformer layers from any HF model."""
    # Qwen3.5 multimodal: model.model.language_model.model.layers
    if hasattr(model, 'model') and hasattr(model.model, 'language_model'):
        lm = model.model.language_model
        if hasattr(lm, 'model') and hasattr(lm.model, 'layers'):
            return lm.model.layers
    # Standard HF (Qwen, Mistral, Llama): model.model.layers
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        return model.model.layers
    # GPT-NeoX (Pythia): model.gpt_neox.layers
    if hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        return model.gpt_neox.layers
    # OLMo: model.model.transformer.blocks
    if hasattr(model, 'model') and hasattr(model.model, 'transformer'):
        if hasattr(model.model.transformer, 'blocks'):
            return model.model.transformer.blocks
    raise ValueError(f"Cannot find layers in {type(model).__name__}")


def get_embed(model):
    """Get embedding module from any HF model."""
    # Qwen3.5 multimodal
    if hasattr(model, 'model') and hasattr(model.model, 'language_model'):
        lm = model.model.language_model
        if hasattr(lm, 'model') and hasattr(lm.model, 'embed_tokens'):
            return lm.model.embed_tokens
    # Standard HF (Qwen, Mistral, Llama)
    if hasattr(model, 'model') and hasattr(model.model, 'embed_tokens'):
        return model.model.embed_tokens
    # GPT-NeoX (Pythia)
    if hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'embed_in'):
        return model.gpt_neox.embed_in
    return None


# ══════════════════════════════════════════════════════════════════════
# Residual capture
# ══════════════════════════════════════════════════════════════════════

def capture_all_residuals(
    model, tokenizer, text: str, n_layers: int
) -> tuple[dict[int, np.ndarray], list[int]]:
    """Capture residual stream at every layer boundary.

    Returns dict mapping layer_idx → (seq_len, d_model) numpy array.
    layer_idx = -1 is embedding output.
    """
    layers = get_layers(model)
    residuals: dict[int, np.ndarray] = {}
    hooks = []

    # Embedding hook
    embed = get_embed(model)
    if embed is not None:
        def embed_hook(module, args, output):
            h = output[0] if isinstance(output, tuple) else output
            residuals[-1] = h[0].detach().cpu().float().numpy()
        hooks.append(embed.register_forward_hook(embed_hook))

    # Layer hooks
    for idx in range(n_layers):
        def make_hook(layer_idx):
            def hook_fn(module, args, output):
                h = output[0] if isinstance(output, tuple) else output
                residuals[layer_idx] = h[0].detach().cpu().float().numpy()
            return hook_fn
        hooks.append(layers[idx].register_forward_hook(make_hook(idx)))

    try:
        inputs = tokenizer(text, return_tensors="pt")
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        token_ids = inputs["input_ids"][0].tolist()

        with torch.no_grad():
            model(**inputs, output_attentions=False)
    finally:
        for h in hooks:
            h.remove()

    return residuals, token_ids


# ══════════════════════════════════════════════════════════════════════
# Analysis
# ══════════════════════════════════════════════════════════════════════

def analyze_residuals(
    residuals: dict[int, np.ndarray],
    n_layers: int,
    d_model: int,
) -> list[dict]:
    """Compute dimensionality metrics at each layer."""

    crystal_eigvals, crystal_eigvecs = get_crystal_eigenbasis()

    results = []

    layer_indices = sorted(residuals.keys())

    for layer_idx in layer_indices:
        h = residuals[layer_idx]  # (seq_len, d_model)

        # Skip position 0 (attention sink — dominates SVD with extreme norm)
        if h.shape[0] > 3:
            h = h[1:]

        seq_len = h.shape[0]

        # ── SVD of residual stream ──
        centered = h - h.mean(axis=0)
        # Truncated SVD for speed (top 256 singular values)
        k = min(256, seq_len, d_model)
        try:
            U, S, Vt = np.linalg.svd(centered, full_matrices=False)
            S = S[:k]
        except np.linalg.LinAlgError:
            S = np.ones(k)

        energy = S ** 2
        total_energy = energy.sum()
        cumulative = np.cumsum(energy) / (total_energy + 1e-10)

        rank_80 = int(np.searchsorted(cumulative, 0.80)) + 1
        rank_90 = int(np.searchsorted(cumulative, 0.90)) + 1
        rank_95 = int(np.searchsorted(cumulative, 0.95)) + 1

        # Participation ratio
        fracs = energy / (total_energy + 1e-10)
        pr = (fracs.sum() ** 2) / (np.sum(fracs ** 2) + 1e-10)

        # Top SV concentration
        sv1_frac = float(energy[0] / (total_energy + 1e-10))
        sv12_frac = float(energy[:2].sum() / (total_energy + 1e-10))
        sv5_frac = float(energy[:5].sum() / (total_energy + 1e-10))

        # ── Norm statistics ──
        norms = np.linalg.norm(h, axis=1)
        mean_norm = float(norms.mean())
        std_norm = float(norms.std())

        result = {
            "layer": layer_idx,
            "seq_len": seq_len,
            "rank_80": rank_80,
            "rank_90": rank_90,
            "rank_95": rank_95,
            "participation_ratio": float(pr),
            "sv1_fraction": sv1_frac,
            "sv12_fraction": sv12_frac,
            "sv5_fraction": sv5_frac,
            "top_5_sv": S[:5].tolist(),
            "mean_norm": mean_norm,
            "norm_cv": float(std_norm / (mean_norm + 1e-10)),
        }

        results.append(result)

    return results


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    model, tokenizer, text_cfg = load_model()

    n_layers = getattr(text_cfg, 'num_hidden_layers', 64)
    d_model = getattr(text_cfg, 'hidden_size', 5120)
    layer_types = getattr(text_cfg, 'layer_types', [])

    print(f"\n  Running progressive collapse probe on {n_layers} layers...")

    # ── Collect residuals across multiple texts ──
    all_results = []

    for i, text in enumerate(PROBE_TEXTS):
        print(f"\n  Probe {i+1}/{len(PROBE_TEXTS)}: \"{text[:60]}...\"", flush=True)
        t0 = time.time()

        residuals, token_ids = capture_all_residuals(model, tokenizer, text, n_layers)
        results = analyze_residuals(residuals, n_layers, d_model)
        all_results.append(results)

        dt = time.time() - t0
        print(f"    {len(token_ids)} tokens, {dt:.1f}s", flush=True)

        # Free residuals immediately
        del residuals
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()

    # ── Average across probes ──
    n_probes = len(all_results)
    n_stages = len(all_results[0])

    averaged = []
    for stage_idx in range(n_stages):
        avg = {
            "layer": all_results[0][stage_idx]["layer"],
        }
        numeric_keys = ["rank_80", "rank_90", "rank_95", "participation_ratio",
                        "sv1_fraction", "sv12_fraction", "sv5_fraction",
                        "mean_norm", "norm_cv"]
        for key in numeric_keys:
            vals = [all_results[p][stage_idx][key] for p in range(n_probes)]
            avg[key] = float(np.mean(vals))
            avg[f"{key}_std"] = float(np.std(vals))

        averaged.append(avg)

    # ── Print results ──
    print(f"\n{'=' * 100}")
    print(f"  Progressive Dimensionality Collapse — {MODEL_NAME}")
    print(f"  Averaged over {n_probes} probe texts")
    print(f"{'=' * 100}")

    print(f"\n{'─' * 100}")
    print(f"  {'Layer':<8} {'Type':<8} {'Rank80':<8} {'Rank90':<8} {'Rank95':<8} "
          f"{'PR':<8} {'σ₁%':<8} {'σ1-2%':<8} {'σ1-5%':<8} {'‖h‖':<8} {'CV':<8}")
    print(f"{'─' * 100}")

    for r in averaged:
        layer = r["layer"]
        if layer == -1:
            ltype = "embed"
        elif layer < len(layer_types):
            ltype = "lin" if layer_types[layer] == "linear_attention" else "FULL"
        else:
            ltype = "?"

        print(f"  {layer:<8} {ltype:<8} "
              f"{r['rank_80']:<8.1f} {r['rank_90']:<8.1f} {r['rank_95']:<8.1f} "
              f"{r['participation_ratio']:<8.1f} "
              f"{r['sv1_fraction']:<8.1%} {r['sv12_fraction']:<8.1%} "
              f"{r['sv5_fraction']:<8.1%} "
              f"{r['mean_norm']:<8.1f} {r['norm_cv']:<8.3f}")

    # ── Trajectory summary ──
    ranks90 = [r["rank_90"] for r in averaged]
    prs = [r["participation_ratio"] for r in averaged]
    norms = [r["mean_norm"] for r in averaged]

    embed_rank = ranks90[0]
    min_rank = min(ranks90)
    min_rank_layer = averaged[np.argmin(ranks90)]["layer"]
    max_rank = max(ranks90[1:])  # skip embed
    max_rank_layer = averaged[1 + np.argmax(ranks90[1:])]["layer"]
    final_rank = ranks90[-1]

    print(f"\n{'─' * 100}")
    print(f"  TRAJECTORY SUMMARY:")
    print(f"{'─' * 100}")
    print(f"  Rank90: embed={embed_rank:.0f} → max={max_rank:.0f} (L{max_rank_layer}) → "
          f"min={min_rank:.0f} (L{min_rank_layer}) → final={final_rank:.0f}")
    print(f"  PR:     embed={prs[0]:.1f} → max={max(prs):.1f} → "
          f"min={min(prs):.1f} → final={prs[-1]:.1f}")
    print(f"  Norm:   embed={norms[0]:.1f} → max={max(norms):.1f} → final={norms[-1]:.1f}")

    # ── Zone analysis (teacher zones) ──
    # Zone A: layers 0-15 (encode)
    # Zone B: layers 16-47 (compute)
    # Zone C: layers 48-63 (converge)
    zone_a = [r for r in averaged if 0 <= r["layer"] <= 15]
    zone_b = [r for r in averaged if 16 <= r["layer"] <= 47]
    zone_c = [r for r in averaged if 48 <= r["layer"] <= 63]

    if zone_a and zone_b and zone_c:
        mean_rank_a = np.mean([r["rank_90"] for r in zone_a])
        mean_rank_b = np.mean([r["rank_90"] for r in zone_b])
        mean_rank_c = np.mean([r["rank_90"] for r in zone_c])
        mean_pr_a = np.mean([r["participation_ratio"] for r in zone_a])
        mean_pr_b = np.mean([r["participation_ratio"] for r in zone_b])
        mean_pr_c = np.mean([r["participation_ratio"] for r in zone_c])

        print(f"\n  Zone averages:")
        print(f"    Zone A (encode,  L0-15):  rank90={mean_rank_a:.1f}  PR={mean_pr_a:.1f}")
        print(f"    Zone B (compute, L16-47): rank90={mean_rank_b:.1f}  PR={mean_pr_b:.1f}")
        print(f"    Zone C (converge,L48-63): rank90={mean_rank_c:.1f}  PR={mean_pr_c:.1f}")

        if mean_rank_b > mean_rank_a and mean_rank_b > mean_rank_c:
            print(f"\n  ★ LENS PATTERN CONFIRMED: Zone B expands (rank {mean_rank_b:.0f}), "
                  f"Zones A ({mean_rank_a:.0f}) and C ({mean_rank_c:.0f}) compress.")
        elif mean_rank_a > mean_rank_b > mean_rank_c:
            print(f"\n  → MONOTONIC COLLAPSE: rank decreases through depth.")
        else:
            print(f"\n  → NON-STANDARD PATTERN: investigate further.")

    # ── Save results ──
    model_slug = MODEL_NAME.replace("/", "_")
    out_dir = Path(f"results/progressive-collapse-{model_slug}")
    out_dir.mkdir(parents=True, exist_ok=True)

    output = {
        "model": MODEL_NAME,
        "n_probes": n_probes,
        "n_layers": n_layers,
        "d_model": d_model,
        "layer_types": layer_types,
        "averaged": averaged,
        "per_probe": [[{k: v for k, v in r.items() if not isinstance(v, np.ndarray)}
                       for r in probe] for probe in all_results],
    }

    def clean(obj):
        if isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: clean(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [clean(v) for v in obj]
        return obj

    with open(out_dir / "results.json", "w") as f:
        json.dump(clean(output), f, indent=2)

    print(f"\n  Results saved to {out_dir}/results.json")
    print()


if __name__ == "__main__":
    main()
