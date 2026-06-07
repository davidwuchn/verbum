#!/usr/bin/env python3
"""
Verify Bridge Nodes — W and Y have dual tree membership
========================================================

The crystal decomposes into 3 trees + bridge nodes (session 197):
  Tree 0 (54.5%): compute/halt — all computation vs WHNF
  Tree 1 (20.1%): selection/composition — K,I vs B,C,D,Y
  Tree 2 (11.4%): termination detection — K,I,W,WHNF vs B,C,D,Y

W and Y are BRIDGE NODES that change sides across trees.
This script verifies empirically that W and Y probes activate
BOTH selection-side and composition-side neurons in the gate_proj.

Method:
  1. Load model, run probes (W, Y, K, I, B, C, D, WHNF, null control)
  2. Capture gate_proj activations at Zone B layers
  3. PCA the activations → project onto the crystal eigenvectors
  4. Measure each probe type's projection onto each tree axis
  5. Show W and Y project onto BOTH trees 1 & 2, while
     K,I and B,C,D project onto only one side

If the bridge hypothesis is correct:
  - K,I probes → strongly positive on Tree 1 (selection side)
  - B,C,D probes → strongly negative on Tree 1 (composition side)
  - W probes → INTERMEDIATE on Tree 1 (bridge)
  - Y probes → composition side on Tree 1, FLIPS on Tree 3 (bridge)
  - WHNF probes → positive on Tree 0, negative on Tree 1

Usage:
    uv run python scripts/experiments/verify_bridge_nodes.py \\
        --model Qwen/Qwen3-0.6B [--n-probes 10]
"""

import argparse
import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch

# ═══════════════════════════════════════════════════════════════
# Crystal basis (from EQUATIONS.md / crystal_tree.py)
# ═══════════════════════════════════════════════════════════════

PHI = (1 + np.sqrt(5)) / 2

# 8x8 empirical crystal cosine matrix
# Order: K, I, B, C, D, Y, W, WHNF
M8 = np.array([
    [+1.0000, +0.7865, +0.1948, +0.2265, +0.3232, +0.1768, +0.5360, -0.1862],
    [+0.7865, +1.0000, +0.2479, +0.2511, +0.3463, +0.1739, +0.3781, -0.2448],
    [+0.1948, +0.2479, +1.0000, +0.8878, +0.8937, +0.6623, +0.6851, -0.1227],
    [+0.2265, +0.2511, +0.8878, +1.0000, +0.8316, +0.7200, +0.7318, -0.1027],
    [+0.3232, +0.3463, +0.8937, +0.8316, +1.0000, +0.6798, +0.8064, -0.1729],
    [+0.1768, +0.1739, +0.6623, +0.7200, +0.6798, +1.0000, +0.5653, -0.0840],
    [+0.5360, +0.3781, +0.6851, +0.7318, +0.8064, +0.5653, +1.0000, -0.1379],
    [-0.1862, -0.2448, -0.1227, -0.1027, -0.1729, -0.0840, -0.1379, +1.0000],
], dtype=np.float64)

CRYSTAL_NAMES = ['K', 'I', 'B', 'C', 'D', 'Y', 'W', 'WHNF']

# Pre-compute crystal eigenvectors (the tree axes)
_eigvals, _eigvecs = np.linalg.eigh(M8)
_idx = np.argsort(_eigvals)[::-1]
CRYSTAL_EIGVALS = _eigvals[_idx]
CRYSTAL_EIGVECS = _eigvecs[:, _idx]  # columns = tree axes

TREE_NAMES = [
    "T0:compute/halt",
    "T1:select/compose",
    "T2:termination",
    "T3:Y-routing",
    "T4:W-bridge",
    "T5:C-D-detail",
    "T6:K-I-detail",
    "T7:B-D-detail",
]


# ═══════════════════════════════════════════════════════════════
# Model loading
# ═══════════════════════════════════════════════════════════════

def load_model(model_name: str):
    """Load a HuggingFace model and tokenizer."""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"  Loading {model_name}...")
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()

    dt = time.time() - t0
    n_layers = model.config.num_hidden_layers
    d_model = model.config.hidden_size
    print(f"  Loaded in {dt:.1f}s — {n_layers}L × d={d_model}")

    return model, tokenizer, n_layers, d_model


def get_layers(model):
    """Get transformer layers from any arch."""
    for attr in ["model.layers", "transformer.h", "gpt_neox.layers"]:
        obj = model
        try:
            for part in attr.split("."):
                obj = getattr(obj, part)
            return list(obj)
        except AttributeError:
            continue
    raise RuntimeError("Cannot find layers")


def get_gate_proj(layer):
    """Get gate_proj module."""
    mlp = layer.mlp if hasattr(layer, "mlp") else layer
    if hasattr(mlp, "gate_proj"):
        return mlp.gate_proj
    if hasattr(mlp, "dense_h_to_4h"):
        return mlp.dense_h_to_4h
    raise RuntimeError(f"No gate_proj in {type(mlp)}")


# ═══════════════════════════════════════════════════════════════
# Probe definitions
# ═══════════════════════════════════════════════════════════════

def get_probes(n_per_type: int = 10) -> dict[str, list[str]]:
    """Get probes for each combinator type."""
    # Try loading from library
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        from verbum.probes.library import by_combinator
        probes = {}
        for comb in CRYSTAL_NAMES:
            ps = by_combinator(comb)
            probes[comb] = [p.prompt for p in ps[:n_per_type]]
        return probes
    except Exception:
        pass

    # Fallback: hand-crafted minimal probes
    return {
        'K': [
            "If it rains, take the umbrella; otherwise, take the",
            "Given A and B, the result is just",
            "The first of the two options is always the",
            "She chose the red one and ignored the",
            "Between coffee and tea, he always picks",
            "The function returns the first argument and discards the",
            "Of the left and right paths, we take the",
            "The winning team was the first to score a",
            "He kept the diamond and threw away the",
            "Select the primary option: A over B means",
        ],
        'I': [
            "The value passes through unchanged as",
            "The identity function returns its input which is",
            "She repeated exactly what he said word for",
            "The mirror shows exactly what stands before",
            "Copy the input directly to the output to get",
            "The transparent proxy forwards the request without",
            "Echo back the same message that was",
            "The relay passes the signal unchanged through the",
            "Return the argument as-is with no",
            "What goes in must come out exactly the",
        ],
        'B': [
            "First wash, then dry, then fold the",
            "Apply f to the result of g applied to",
            "The pipeline processes data through multiple stages of",
            "Compose the two transformations into a single",
            "The outer function wraps the inner function's",
            "Chain the operations: first filter, then map, then",
            "The composition of rotation and translation gives a",
            "After encoding, then encrypting, the message becomes",
            "Nested function calls: f(g(x)) where x is",
            "The combined effect of both transformations is",
        ],
        'C': [
            "Instead of f(x)(y), compute f(y)(x) which gives",
            "Flip the argument order so the second comes",
            "The passive voice reverses subject and object in the",
            "Swap the two parameters before calling the",
            "Rather than applying to A then B, apply to B then",
            "The inverse operation reverses the order of",
            "Reorder the arguments so the receiver becomes the",
            "Exchange the positions of the first and second",
            "The commutative law says we can swap",
            "Transpose the matrix to flip rows and",
        ],
        'D': [
            "Compose f with g, then compose the result with h to get",
            "The double composition applies three functions in",
            "Deeply nested: f(g(h(x))) processes x through three",
            "The pipeline has three stages of",
            "Triple function composition: first h, then g, then f applied to",
            "The deeply composed transformation chains three",
            "After three successive operations, the data becomes",
            "Each layer transforms the output of the previous",
            "The deeply nested call evaluates from inside",
            "Three composed functions form a single composite",
        ],
        'Y': [
            "A folder contains files and other folders which contain",
            "She told a story about a girl who told a story about",
            "The dream was about having a dream which was about having a dream",
            "He opened a box inside a box inside a box inside",
            "The mirror reflected the mirror which reflected the",
            "The function calls itself with a smaller input until it reaches",
            "Each level of recursion creates another level of",
            "The fractal pattern repeats at every scale of",
            "The recursive definition refers back to itself in the",
            "To compute factorial of n, multiply n by factorial of",
        ],
        'W': [
            "The dog bit itself on the",
            "She taught herself to play the",
            "The robot programmed itself to perform",
            "He convinced himself that everything would",
            "The system tested itself and found",
            "The compiler compiles itself to produce",
            "She found herself lost in the",
            "The program modifies itself during",
            "He argued with himself about the",
            "The AI trained itself on its own",
        ],
        'WHNF': [
            "The value 42 is fully evaluated as",
            "The constant function always returns the same",
            "No further reduction is needed for the",
            "The normal form of the expression is simply",
            "The computation has terminated with result",
            "The irreducible value cannot be simplified",
            "After all reductions, the final answer is",
            "The base case of the recursion returns",
            "The fully simplified expression equals",
            "The ground term has no variables left to",
        ],
    }


# ═══════════════════════════════════════════════════════════════
# Main experiment
# ═══════════════════════════════════════════════════════════════

def run_experiment(model_name: str, n_probes: int = 10):
    """Run the bridge node verification experiment."""
    print("╔" + "═" * 68 + "╗")
    print("║" + "  BRIDGE NODE VERIFICATION".center(68) + "║")
    print("║" + f"  {model_name}".center(68) + "║")
    print("╚" + "═" * 68 + "╝")

    model, tokenizer, n_layers, d_model = load_model(model_name)
    layers = get_layers(model)

    # Zone B layers (middle 50% of layers)
    zone_b_start = int(n_layers * 0.30)
    zone_b_end = int(n_layers * 0.65)
    zone_b_layers = list(range(zone_b_start, zone_b_end + 1))
    print(f"\n  Zone B layers: {zone_b_start}-{zone_b_end} ({len(zone_b_layers)} layers)")

    # Get probes
    probes = get_probes(n_probes)
    print(f"  Probes per type: {n_probes}")
    for comb, ps in probes.items():
        print(f"    {comb}: {len(ps)} probes")

    # Collect gate activations
    print(f"\n  ── Collecting gate_proj activations ──")

    # Per-combinator, per-layer gate activations
    # gate_acts[comb_type][layer_idx] = list of activation vectors
    gate_acts = defaultdict(lambda: defaultdict(list))

    device = next(model.parameters()).device
    total = sum(len(ps) for ps in probes.values())
    done = 0

    for comb_type, prompt_list in probes.items():
        for prompt in prompt_list:
            input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)

            captures = {}

            def make_hook(li):
                def hook(m, inp, out):
                    # Capture gate activation at last token position
                    captures[li] = out[0, -1, :].detach().cpu().float().numpy()
                return hook

            # Install hooks
            hooks = []
            for li in zone_b_layers:
                gate = get_gate_proj(layers[li])
                hooks.append(gate.register_forward_hook(make_hook(li)))

            # Forward pass
            with torch.no_grad():
                _ = model(input_ids=input_ids)

            # Remove hooks
            for h in hooks:
                h.remove()

            # Store activations
            for li, act in captures.items():
                gate_acts[comb_type][li].append(act)

            done += 1
            if done % 20 == 0:
                print(f"    {done}/{total} probes done...")

    print(f"    {done}/{total} probes done ✅")

    # ── Analysis: PCA across all activations ──
    print(f"\n  ── PCA at each Zone B layer ──")

    # For each layer, compute the mean activation per combinator type
    # Then project onto crystal tree axes
    results = {}

    for li in zone_b_layers:
        # Collect all activations at this layer
        all_acts = []
        all_labels = []
        for comb_type in CRYSTAL_NAMES:
            for act in gate_acts[comb_type][li]:
                all_acts.append(act)
                all_labels.append(comb_type)

        if not all_acts:
            continue

        X = np.array(all_acts)  # (n_probes_total, d_intermediate)

        # Compute mean per combinator type
        mean_acts = {}
        for comb_type in CRYSTAL_NAMES:
            acts = gate_acts[comb_type][li]
            if acts:
                mean_acts[comb_type] = np.mean(acts, axis=0)

        if len(mean_acts) < 4:
            continue

        # Build 8×d matrix of mean activations
        M = np.array([mean_acts[c] for c in CRYSTAL_NAMES if c in mean_acts])
        available = [c for c in CRYSTAL_NAMES if c in mean_acts]

        # Compute cosine similarity matrix between combinator means
        norms = np.linalg.norm(M, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-10)
        M_normed = M / norms
        cos_sim = M_normed @ M_normed.T

        # Eigendecompose the observed cosine matrix
        obs_eigvals, obs_eigvecs = np.linalg.eigh(cos_sim)
        idx = np.argsort(obs_eigvals)[::-1]
        obs_eigvals = obs_eigvals[idx]
        obs_eigvecs = obs_eigvecs[:, idx]

        # Compare to crystal eigenvector structure
        # Project each combinator's mean activation onto the observed PCs
        projections = obs_eigvecs.T  # (n_pcs, n_combinators) — each row is a PC

        results[li] = {
            'cos_sim': cos_sim,
            'eigvals': obs_eigvals,
            'eigvecs': obs_eigvecs,
            'available': available,
            'projections': projections,
        }

    # ── Report ──
    print(f"\n" + "═" * 70)
    print(f"  RESULTS: Per-layer combinator cosine structure")
    print(f"═" * 70)

    # Average cosine matrix across Zone B layers
    avg_cos = np.zeros((len(CRYSTAL_NAMES), len(CRYSTAL_NAMES)))
    n_layers_used = 0
    for li, res in results.items():
        if len(res['available']) == len(CRYSTAL_NAMES):
            avg_cos += res['cos_sim']
            n_layers_used += 1

    if n_layers_used > 0:
        avg_cos /= n_layers_used
        print(f"\n  Average cosine similarity across {n_layers_used} Zone B layers:")
        print("       " + "    ".join(f"{n:>6}" for n in CRYSTAL_NAMES))
        for i, n in enumerate(CRYSTAL_NAMES):
            row = "  ".join(f"{avg_cos[i,j]:>6.3f}" for j in range(8))
            print(f"  {n:>4}: {row}")

        # Eigendecompose the average
        avg_eigvals, avg_eigvecs = np.linalg.eigh(avg_cos)
        idx = np.argsort(avg_eigvals)[::-1]
        avg_eigvals = avg_eigvals[idx]
        avg_eigvecs = avg_eigvecs[:, idx]

        print(f"\n  Eigenvalues: {['%.4f' % v for v in avg_eigvals]}")

        # Compare eigenvector signs to crystal prediction
        print(f"\n  Eigenvector sign comparison (observed vs crystal):")
        print(f"  {'PC':>4}  {'λ_obs':>8}  {'λ_cryst':>8}  {'Obs signs':>40}  {'Crystal signs':>40}  {'Match':>6}")
        print(f"  {'─'*4}  {'─'*8}  {'─'*8}  {'─'*40}  {'─'*40}  {'─'*6}")

        for k in range(min(5, len(avg_eigvals))):
            obs_signs = ''.join('+' if avg_eigvecs[i,k] > 0 else '-' for i in range(8))
            cry_signs = ''.join('+' if CRYSTAL_EIGVECS[i,k] > 0 else '-' for i in range(8))

            obs_str = ' '.join(f"{CRYSTAL_NAMES[i]}{'+'if avg_eigvecs[i,k]>0 else '-'}"
                              for i in range(8))
            cry_str = ' '.join(f"{CRYSTAL_NAMES[i]}{'+'if CRYSTAL_EIGVECS[i,k]>0 else '-'}"
                              for i in range(8))

            # Sign match (allow flip)
            match_normal = sum(1 for i in range(8) if (avg_eigvecs[i,k] > 0) == (CRYSTAL_EIGVECS[i,k] > 0))
            match_flip = sum(1 for i in range(8) if (avg_eigvecs[i,k] > 0) != (CRYSTAL_EIGVECS[i,k] > 0))
            match = max(match_normal, match_flip)

            print(f"  PC{k}  {avg_eigvals[k]:>8.4f}  {CRYSTAL_EIGVALS[k]:>8.4f}  {obs_str:>40}  {cry_str:>40}  {match}/8")

        # ── THE KEY TEST: Bridge node verification ──
        print(f"\n" + "═" * 70)
        print(f"  BRIDGE NODE TEST")
        print(f"═" * 70)

        # Project each combinator onto the first 3 tree axes
        print(f"\n  Node positions in observed eigenspace (first 3 trees):")
        print(f"  {'Node':>4}  {'Tree 0':>8}  {'Tree 1':>8}  {'Tree 2':>8}  {'Side T1':>8}  {'Bridge?':>8}")
        print(f"  {'─'*4}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*8}")

        # Determine which side of Tree 1 each node is on
        # Positive = selection side, negative = composition side (or vice versa)
        for i, name in enumerate(CRYSTAL_NAMES):
            t0 = avg_eigvecs[i, 0]
            t1 = avg_eigvecs[i, 1]
            t2 = avg_eigvecs[i, 2]

            # Check if this node is a bridge by looking at its consistency
            # across trees 1 and 3 (if available)
            if len(avg_eigvals) > 3:
                t3 = avg_eigvecs[i, 3]
                # Bridge = changes sign between tree 1 and tree 3
                t1_side = '+' if t1 > 0 else '-'
                t3_side = '+' if t3 > 0 else '-'
                is_bridge = t1_side != t3_side
            else:
                is_bridge = False
                t3 = 0

            side = "SEL" if t1 > 0 else "COMP"
            bridge = "BRIDGE" if is_bridge else ""

            print(f"  {name:>4}  {t0:>+8.3f}  {t1:>+8.3f}  {t2:>+8.3f}  {side:>8}  {bridge:>8}")

        # Quantify: W's interpolation on Tree 1
        # KI mean vs BCD mean vs W position
        ki_mean = np.mean([avg_eigvecs[CRYSTAL_NAMES.index(c), 1] for c in ['K', 'I']])
        bcd_mean = np.mean([avg_eigvecs[CRYSTAL_NAMES.index(c), 1] for c in ['B', 'C', 'D']])
        w_val = avg_eigvecs[CRYSTAL_NAMES.index('W'), 1]
        y_val = avg_eigvecs[CRYSTAL_NAMES.index('Y'), 1]

        if abs(ki_mean - bcd_mean) > 1e-10:
            w_interp = (w_val - bcd_mean) / (ki_mean - bcd_mean)
            y_interp = (y_val - bcd_mean) / (ki_mean - bcd_mean)
        else:
            w_interp = 0.5
            y_interp = 0.5

        print(f"\n  Bridge interpolation on Tree 1 axis:")
        print(f"    KI centroid (selection):    {ki_mean:+.4f}")
        print(f"    BCD centroid (composition): {bcd_mean:+.4f}")
        print(f"    W position:                {w_val:+.4f}  ({w_interp:.1%} toward selection)")
        print(f"    Y position:                {y_val:+.4f}  ({y_interp:.1%} toward selection)")
        print(f"\n    Crystal prediction: W ≈ 30% toward selection")
        print(f"    Crystal prediction: Y ≈ 0% (composition side)")

        # Correlation with crystal cosine matrix
        mask = np.triu(np.ones_like(M8, dtype=bool), k=1)
        corr = np.corrcoef(avg_cos[mask], M8[mask])[0, 1]
        print(f"\n  Observed vs crystal cosine matrix correlation: r = {corr:.4f}")

        # Per-edge comparison: show edges where observed MATCHES crystal
        print(f"\n  Top matched edges (observed ≈ crystal):")
        edges = []
        for i in range(8):
            for j in range(i+1, 8):
                err = abs(avg_cos[i,j] - M8[i,j])
                edges.append((err, CRYSTAL_NAMES[i], CRYSTAL_NAMES[j], avg_cos[i,j], M8[i,j]))
        edges.sort()
        for err, a, b, obs, cry in edges[:10]:
            print(f"    {a}-{b}: observed={obs:+.3f}  crystal={cry:+.3f}  error={err:.3f}")

        print(f"\n  Worst matched edges:")
        for err, a, b, obs, cry in edges[-5:]:
            print(f"    {a}-{b}: observed={obs:+.3f}  crystal={cry:+.3f}  error={err:.3f}")

        # ── VERDICT ──
        print(f"\n" + "═" * 70)
        print(f"  VERDICT")
        print(f"═" * 70)

        # Check bridge criteria
        w_is_bridge = abs(w_interp - 0.5) < 0.35  # W should be between 15-85%
        y_is_composition = y_interp < 0.35  # Y should be on composition side
        ki_are_selection = ki_mean > 0  # K,I should be on selection side
        bcd_are_composition = bcd_mean < 0  # B,C,D should be on composition side

        print(f"\n  Bridge hypothesis tests:")
        print(f"    K,I are on selection side:     {'✅ PASS' if ki_are_selection else '❌ FAIL'} (mean={ki_mean:+.4f})")
        print(f"    B,C,D are on composition side: {'✅ PASS' if bcd_are_composition else '❌ FAIL'} (mean={bcd_mean:+.4f})")
        print(f"    W is BETWEEN (bridge):         {'✅ PASS' if w_is_bridge else '❌ FAIL'} (interp={w_interp:.1%})")
        print(f"    Y is on composition side:      {'✅ PASS' if y_is_composition else '❌ FAIL'} (interp={y_interp:.1%})")
        print(f"    Crystal matrix correlation:    {'✅ PASS' if corr > 0.7 else '⚠️ WEAK' if corr > 0.4 else '❌ FAIL'} (r={corr:.4f})")

        all_pass = ki_are_selection and bcd_are_composition and w_is_bridge
        print(f"\n  {'✅ BRIDGE HYPOTHESIS CONFIRMED' if all_pass else '⚠️ PARTIAL / ❌ REFUTED'}")

        # Save results
        out_dir = Path(__file__).parent.parent.parent / 'results' / 'bridge-verification'
        out_dir.mkdir(parents=True, exist_ok=True)
        slug = model_name.replace("/", "_")

        results_data = {
            'model': model_name,
            'n_layers': n_layers,
            'zone_b_layers': zone_b_layers,
            'n_probes_per_type': n_probes,
            'avg_cosine_matrix': avg_cos.tolist(),
            'eigvals': avg_eigvals.tolist(),
            'crystal_correlation': float(corr),
            'w_interpolation': float(w_interp),
            'y_interpolation': float(y_interp),
            'ki_mean_tree1': float(ki_mean),
            'bcd_mean_tree1': float(bcd_mean),
            'bridge_confirmed': bool(all_pass),
        }

        with open(out_dir / f'{slug}_results.json', 'w') as f:
            json.dump(results_data, f, indent=2)
        print(f"\n  Results saved to: {out_dir / slug}_results.json")

    else:
        print("  ❌ No valid layers — cannot analyze")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='Qwen/Qwen3-0.6B')
    parser.add_argument('--n-probes', type=int, default=10)
    args = parser.parse_args()

    run_experiment(args.model, args.n_probes)
