#!/usr/bin/env python3
"""Test: is the depth computation a rotation spiral?

If β-reduction is rotational:
  IN (L0→L19):   analysis — rotate from token space to semantic space
  BOTTOM (L19):  pure semantic — β-reduction happens here
  OUT (L19→L35): synthesis — rotate back from semantic to token space

Predictions:
  1. The IN and OUT trajectories should be SYMMETRIC around L19
  2. Residual vectors should ROTATE through layers (consistent angular velocity)
  3. The cosine between symmetric layers (L_in, L_out) should be high
     where L_in + L_out ≈ 2 * L_bottom
  4. Mode entropy should mirror: IN descent ↔ OUT ascent
  5. Ternary PPL should mirror: both sides of L19 should be symmetric

Method:
  1. Capture residual at every layer for diverse inputs
  2. Measure angle between consecutive layers (rotation rate)
  3. Measure angle between symmetric layer pairs
  4. Compare IN and OUT trajectories via procrustes alignment
  5. Correlate with ternary PPL profile and mode entropy

Usage:
  uv run python scripts/experiments/rotation_spiral.py --model Qwen/Qwen3-8B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


EVAL_TEXTS = [
    "The theory of general relativity describes gravity as the curvature of spacetime caused by mass and energy.",
    "In a large mixing bowl, combine the flour, sugar, and baking powder. Make a well in the center.",
    "She walked through the ancient forest, her footsteps muffled by centuries of fallen leaves.",
    "The function takes two arguments and returns their composition as a new callable object.",
    "During the Cambrian explosion, roughly 541 million years ago, most major animal phyla appeared.",
    "The patient was admitted with acute respiratory distress. Initial blood work showed elevated levels.",
    "To solve this equation, first isolate the variable on one side by subtracting three from both sides.",
    "Democracy originated in ancient Greece, specifically in the city-state of Athens.",
    "DNA carries genetic information in a double helix structure discovered by Watson and Crick.",
    "The Industrial Revolution began in Britain in the late 18th century and transformed manufacturing.",
    "Quantum mechanics describes the behavior of particles at the atomic and subatomic scale.",
    "Mozart composed his first symphony at the age of eight, showing extraordinary musical talent.",
    "The Amazon rainforest produces approximately twenty percent of the world's atmospheric oxygen.",
    "Climate change is caused primarily by the burning of fossil fuels and deforestation.",
    "Abraham Lincoln delivered the Gettysburg Address in 1863 during the American Civil War.",
    "The Pacific Ocean is the largest and deepest ocean on Earth, covering more than 30 percent.",
]


def get_layers(model):
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        return model.model.layers
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        return model.gpt_neox.layers
    raise RuntimeError(f"Cannot find layers in {type(model).__name__}")


def get_all_residuals(model, tokenizer, text, device):
    """Capture residual at every layer boundary."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    layers = get_layers(model)
    captured = {}
    handles = []

    for i, layer in enumerate(layers):
        def make_hook(idx):
            def hook_fn(module, input, output):
                h = output[0] if isinstance(output, tuple) else output
                captured[idx] = h.detach().float().cpu()
            return hook_fn
        handles.append(layer.register_forward_hook(make_hook(i)))

    # Embedding
    embed_module = None
    if hasattr(model, 'model') and hasattr(model.model, 'embed_tokens'):
        embed_module = model.model.embed_tokens
    if embed_module:
        def embed_hook(module, input, output):
            captured['embed'] = output.detach().float().cpu()
        handles.append(embed_module.register_forward_hook(embed_hook))

    with torch.no_grad():
        model(**inputs)
    for h in handles:
        h.remove()

    result = []
    if 'embed' in captured:
        result.append(captured['embed'][0].numpy())
    for i in range(len(layers)):
        if i in captured:
            result.append(captured[i][0].numpy())
    return result


def cosine_sim(a, b):
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a < 1e-10 or norm_b < 1e-10:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def angular_velocity(residuals):
    """Angle between consecutive layer residuals (radians)."""
    angles = []
    for i in range(len(residuals) - 1):
        cos = cosine_sim(residuals[i].mean(axis=0), residuals[i+1].mean(axis=0))
        cos = np.clip(cos, -1, 1)
        angle = np.arccos(cos)
        angles.append(float(angle))
    return angles


def norm_growth(residuals):
    """L2 norm of residual at each layer."""
    return [float(np.linalg.norm(r.mean(axis=0))) for r in residuals]


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    args = p.parse_args()

    print(f"\n{'='*70}")
    print(f"  ROTATION SPIRAL TEST")
    print(f"  Is depth computation a rotation? IN → BOTTOM → OUT?")
    print(f"{'='*70}")
    print(f"  Model: {args.model}")
    print(f"  Device: {args.device}")
    print()

    dtype = torch.float16 if any(s in args.model for s in ["8B", "14B", "32B"]) else torch.float32
    print(f"  Loading {args.model}...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    n_layers = model.config.num_hidden_layers
    print(f"  Layers: {n_layers}")

    # ── Collect residuals ─────────────────────────────────────────
    print(f"\n  Collecting residuals for {len(EVAL_TEXTS)} texts...")
    all_residuals = []
    for text in EVAL_TEXTS:
        residuals = get_all_residuals(model, tokenizer, text, args.device)
        all_residuals.append(residuals)
        print(f"    '{text[:50]}...' → {len(residuals)} layers")

    n_depth = len(all_residuals[0])  # embed + n_layers

    # ── Test 1: Angular velocity (rotation rate per layer) ────────
    print(f"\n{'='*70}")
    print(f"  Test 1: Angular velocity (consecutive layer angle)")
    print(f"{'='*70}")

    all_angles = []
    for residuals in all_residuals:
        angles = angular_velocity(residuals)
        all_angles.append(angles)

    mean_angles = np.mean(all_angles, axis=0)
    std_angles = np.std(all_angles, axis=0)

    print(f"\n  {'Transition':>12s}  {'Angle(rad)':>10s}  {'Angle(deg)':>10s}  Visual")
    for i in range(len(mean_angles)):
        label = f"emb→L0" if i == 0 else f"L{i-1}→L{i}"
        deg = np.degrees(mean_angles[i])
        bar = "█" * int(deg * 2)
        print(f"  {label:>12s}  {mean_angles[i]:>10.4f}  {deg:>10.2f}°  {bar}")

    # Rotation rate should be roughly constant if it's a uniform spiral
    # Check coefficient of variation
    cv = np.std(mean_angles[1:]) / np.mean(mean_angles[1:])  # skip embed→L0
    print(f"\n  Mean rotation rate (L0→L35): {np.mean(mean_angles[1:]):.4f} rad = {np.degrees(np.mean(mean_angles[1:])):.2f}°")
    print(f"  CV of rotation rate: {cv:.3f} (0 = perfectly uniform)")
    print(f"  Total rotation: {np.sum(mean_angles):.2f} rad = {np.degrees(np.sum(mean_angles)):.1f}°")

    # ── Test 2: Norm growth (spiral expansion) ────────────────────
    print(f"\n{'='*70}")
    print(f"  Test 2: Norm growth (spiral radius)")
    print(f"{'='*70}")

    all_norms = []
    for residuals in all_residuals:
        norms = norm_growth(residuals)
        all_norms.append(norms)

    mean_norms = np.mean(all_norms, axis=0)

    # Normalize to L0
    norm_ratio = mean_norms / (mean_norms[1] + 1e-10)  # relative to L0

    print(f"\n  {'Layer':>7s}  {'Norm':>10s}  {'Ratio':>7s}  Visual")
    for i in range(len(mean_norms)):
        label = "emb" if i == 0 else f"L{i-1}"
        bar = "█" * int(norm_ratio[i] * 10)
        print(f"  {label:>7s}  {mean_norms[i]:>10.2f}  {norm_ratio[i]:>7.3f}  {bar}")

    # Check if growth follows φ
    if len(mean_norms) > 2:
        growth_rates = [mean_norms[i+1]/mean_norms[i] for i in range(1, len(mean_norms)-1) if mean_norms[i] > 0]
        mean_growth = np.mean(growth_rates)
        phi = (1 + np.sqrt(5)) / 2
        print(f"\n  Mean per-layer growth rate: {mean_growth:.6f}")
        print(f"  φ^(1/n_layers) = {phi**(1/n_layers):.6f}")
        print(f"  Ratio to φ^(1/n): {mean_growth / phi**(1/n_layers):.4f}")

    # ── Test 3: Symmetric layer similarity ────────────────────────
    print(f"\n{'='*70}")
    print(f"  Test 3: IN↔OUT symmetry around the bottom")
    print(f"{'='*70}")

    # Find the "bottom" — we hypothesize L19 (0.53 * 36)
    # But let's also test multiple candidate bottoms
    for bottom_frac in [0.50, 0.53, 0.55, 0.58, 0.61]:
        bottom = int(n_layers * bottom_frac) + 1  # +1 for embed offset
        print(f"\n  Bottom at L{bottom-1} (frac={bottom_frac:.2f}):")

        sym_pairs = []
        for offset in range(1, min(bottom, n_depth - bottom)):
            l_in = bottom - offset
            l_out = bottom + offset
            if l_out >= n_depth:
                break

            pair_cos = []
            for residuals in all_residuals:
                cos = cosine_sim(
                    residuals[l_in].mean(axis=0),
                    residuals[l_out].mean(axis=0))
                pair_cos.append(cos)

            mean_cos = float(np.mean(pair_cos))
            label_in = "emb" if l_in == 0 else f"L{l_in-1}"
            label_out = f"L{l_out-1}"
            bar = "█" * int(mean_cos * 30)
            print(f"    {label_in:>5s} ↔ {label_out:>5s} (±{offset}):  cos={mean_cos:>6.3f}  {bar}")
            sym_pairs.append({"in": l_in, "out": l_out, "offset": offset, "cos": mean_cos})

        if sym_pairs:
            mean_sym = np.mean([s["cos"] for s in sym_pairs])
            print(f"    Mean symmetric cosine: {mean_sym:.3f}")

    # ── Test 4: Consecutive layer cosine (is it a smooth rotation?) ─
    print(f"\n{'='*70}")
    print(f"  Test 4: Layer-to-layer cosine (rotation smoothness)")
    print(f"{'='*70}")

    all_consec = []
    for residuals in all_residuals:
        consec = []
        for i in range(len(residuals) - 1):
            cos = cosine_sim(residuals[i].mean(axis=0), residuals[i+1].mean(axis=0))
            consec.append(cos)
        all_consec.append(consec)

    mean_consec = np.mean(all_consec, axis=0)
    print(f"\n  {'Pair':>10s}  {'cos':>7s}  Visual")
    for i in range(len(mean_consec)):
        label = f"emb→L0" if i == 0 else f"L{i-1}→L{i}"
        bar = "█" * int(mean_consec[i] * 30)
        print(f"  {label:>10s}  {mean_consec[i]:>7.3f}  {bar}")

    # ── Test 5: Full cosine matrix (all layers vs all layers) ─────
    print(f"\n{'='*70}")
    print(f"  Test 5: Full cosine matrix (identify the spiral structure)")
    print(f"{'='*70}")

    # Average cosine across all texts
    cos_matrix = np.zeros((n_depth, n_depth))
    for residuals in all_residuals:
        means = [r.mean(axis=0) for r in residuals]
        for i in range(n_depth):
            for j in range(n_depth):
                cos_matrix[i, j] += cosine_sim(means[i], means[j])
    cos_matrix /= len(all_residuals)

    # Print sampled rows
    sample_idx = list(range(0, n_depth, max(1, n_depth // 12)))
    print(f"\n  {'':>5s}", end="")
    for j in sample_idx:
        label = "emb" if j == 0 else f"L{j-1:>2d}"
        print(f"  {label:>5s}", end="")
    print()
    for i in sample_idx:
        label = "emb" if i == 0 else f"L{i-1:>2d}"
        print(f"  {label:>5s}", end="")
        for j in sample_idx:
            print(f"  {cos_matrix[i,j]:>5.2f}", end="")
        print()

    # ── Test 6: Symmetry correlation ──────────────────────────────
    print(f"\n{'='*70}")
    print(f"  Test 6: IN vs OUT trajectory correlation")
    print(f"{'='*70}")

    # For each candidate bottom, compute:
    # IN = [cos(L0,L1), cos(L1,L2), ..., cos(L_{b-1}, L_b)]
    # OUT = [cos(L_b, L_{b+1}), ..., cos(L_{n-2}, L_{n-1})]
    # Then compare: is IN reversed ≈ OUT?

    for bottom_frac in [0.50, 0.53, 0.55]:
        bottom = int(n_layers * bottom_frac) + 1
        in_angles = mean_angles[:bottom]
        out_angles = mean_angles[bottom:]
        in_reversed = in_angles[::-1]

        # Truncate to same length
        min_len = min(len(in_reversed), len(out_angles))
        in_r = np.array(in_reversed[:min_len])
        out_a = np.array(out_angles[:min_len])

        if min_len > 2:
            corr = float(np.corrcoef(in_r, out_a)[0, 1])
            print(f"  Bottom L{bottom-1} (frac={bottom_frac:.2f}):")
            print(f"    IN(reversed) vs OUT correlation: r = {corr:.3f}")
            print(f"    IN mean angle:  {np.mean(in_angles):.4f} rad ({np.degrees(np.mean(in_angles)):.2f}°)")
            print(f"    OUT mean angle: {np.mean(out_angles):.4f} rad ({np.degrees(np.mean(out_angles)):.2f}°)")

    # ── Test 7: Compare with ternary PPL profile ──────────────────
    print(f"\n{'='*70}")
    print(f"  Test 7: Ternary PPL symmetry around bottom")
    print(f"{'='*70}")

    # Load ternary PPL results if available
    ternary_path = Path("results/multilayer-ternary-replace/Qwen_Qwen3-8B.json")
    if ternary_path.exists():
        with open(ternary_path) as f:
            ternary_data = json.load(f)
        scan = sorted(ternary_data.get("full_scan", []), key=lambda x: x["layer"])
        if scan:
            ppl_ratios = {s["layer"]: s["ppl_ratio"] for s in scan}

            # Symmetry around L19
            bottom = 19
            print(f"\n  Ternary PPL symmetry around L{bottom}:")
            print(f"  {'IN':>5s}  {'PPL_in':>7s}  {'OUT':>5s}  {'PPL_out':>7s}  {'Δ':>7s}")
            for offset in range(1, 17):
                l_in = bottom - offset
                l_out = bottom + offset
                if l_in in ppl_ratios and l_out in ppl_ratios:
                    ppl_in = ppl_ratios[l_in]
                    ppl_out = ppl_ratios[l_out]
                    delta = ppl_out - ppl_in
                    print(f"  L{l_in:>2d}    {ppl_in:>6.3f}×  L{l_out:>2d}    {ppl_out:>6.3f}×  {delta:>+6.3f}")

            # Correlation of IN and OUT PPL profiles
            in_ppl = [ppl_ratios.get(bottom - i, None) for i in range(1, 17)]
            out_ppl = [ppl_ratios.get(bottom + i, None) for i in range(1, 17)]
            valid = [(a, b) for a, b in zip(in_ppl, out_ppl) if a is not None and b is not None]
            if len(valid) > 2:
                in_v, out_v = zip(*valid)
                corr = float(np.corrcoef(in_v, out_v)[0, 1])
                print(f"\n  IN vs OUT ternary PPL correlation: r = {corr:.3f}")

    # ── Save ──────────────────────────────────────────────────────
    out_dir = Path("results/rotation-spiral")
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = args.model.replace("/", "_")
    out_path = out_dir / f"{model_slug}.json"

    save_data = {
        "model": args.model,
        "n_layers": n_layers,
        "angular_velocity": {
            "mean": [float(x) for x in mean_angles],
            "std": [float(x) for x in std_angles],
            "cv": float(cv),
            "total_rotation_deg": float(np.degrees(np.sum(mean_angles))),
        },
        "norm_growth": {
            "mean_norms": [float(x) for x in mean_norms],
            "norm_ratios": [float(x) for x in norm_ratio],
        },
        "consecutive_cosine": [float(x) for x in mean_consec],
        "cosine_matrix": cos_matrix.tolist(),
    }
    with open(out_path, "w") as f:
        json.dump(save_data, f, indent=2)
    print(f"\n  Results saved to {out_path}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
