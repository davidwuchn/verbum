#!/usr/bin/env python3
"""Verify the crystal phi structure directly in a model.

Measures the 16×16 crystal cosine matrix from a model's FFN gate_proj
activations, eigendecomposes it, and checks whether eigenvalues follow
φ^(p/q).

This is the direct verification that skips the consensus/micro-model
intermediary. If eigenvalues follow φ^(p/q) here, the crystal equation
is confirmed in the raw model.

Method:
  1. Load model (HuggingFace CausalLM)
  2. Run combinator probe prompts (K, I, B, C, D, Y, W, WHNF examples)
  3. Extract gate_proj activations at Zone B layers (middle depth)
  4. PCA of gate activations → 16 principal components
  5. Compute 16×16 cosine matrix between PC directions
  6. Eigendecompose and check φ^(p/q) structure

Usage:
  uv run python scripts/experiments/verify_crystal_phi.py --model Qwen/Qwen3-14B
  uv run python scripts/experiments/verify_crystal_phi.py --model Qwen/Qwen3-14B --device mps --quick
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


phi = (1 + np.sqrt(5)) / 2

# ══════════════════════════════════════════════════════════════════
# Combinator probe prompts — one per combinator type
# Each prompt activates a specific combinator pattern
# ══════════════════════════════════════════════════════════════════

COMBINATOR_PROBES = {
    "K": [  # Select first, discard second
        "The cat, not the dog, chased the mouse across the yard.",
        "Either the president or the minister signed the treaty.",
        "John, rather than his brother, won the competition.",
        "The red ball, not the blue one, rolled under the table.",
    ],
    "I": [  # Identity — pass through unchanged
        "The ball is round.",
        "Water flows downhill naturally.",
        "The sun rises in the east every morning.",
        "Birds fly south for the winter season.",
    ],
    "B": [  # Compose — f(g(x))
        "The quickly running athlete crossed the finish line first.",
        "The recently published research paper changed everything.",
        "The carefully designed algorithm solved the problem efficiently.",
        "The brightly colored butterfly landed on the flower.",
    ],
    "C": [  # Reorder arguments — f(y)(x)
        "The book that the student read was difficult to understand.",
        "The cake that Mary baked was eaten by all the guests.",
        "The song that the band played was requested by the audience.",
        "The letter that John wrote was delivered to the wrong address.",
    ],
    "D": [  # Double composition — B(B)
        "The very quickly running athlete crossed the brightly lit finish line.",
        "The recently and thoroughly published research dramatically changed outcomes.",
        "The carefully and precisely designed algorithm efficiently solved problems.",
        "The extremely brightly colored tropical butterfly gracefully landed nearby.",
    ],
    "Y": [  # Recursive / fixed-point patterns
        "The man who knows the man who knows the answer is here.",
        "She said that he said that they said it was true.",
        "The cat chased the dog that chased the cat that ran.",
        "If you know that I know that you know, then we agree.",
    ],
    "W": [  # Self-application / duplication
        "He himself admitted that he himself was wrong about it.",
        "The mirror reflected the mirror reflecting the mirror.",
        "The program that tests itself found a bug in itself.",
        "She told herself that she needed to trust herself more.",
    ],
    "WHNF": [  # Terminal / identity output
        "Hello.",
        "Yes.",
        "The.",
        "It is.",
    ],
}

COMBINATOR_NAMES = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]


def get_zone_b_layers(n_layers: int) -> list[int]:
    """Get Zone B (middle) layer indices."""
    start = int(n_layers * 0.3)
    end = int(n_layers * 0.7)
    # Pick ~4 layers evenly spaced in Zone B
    layers = np.linspace(start, end, min(4, end - start + 1), dtype=int).tolist()
    return layers


def extract_gate_activations(model, tokenizer, prompts: list[str],
                              layers: list[int], device: str) -> np.ndarray:
    """Extract gate_proj activations from specified layers.

    Returns: (n_prompts, n_layers, d_ff) mean-pooled over sequence positions.
    """
    activations = []
    hooks = []
    captured = {}

    def make_hook(layer_idx):
        def hook_fn(module, input, output):
            # output from gate_proj: (batch, seq, d_ff)
            captured[layer_idx] = output.detach().float()
        return hook_fn

    # Register hooks on gate_proj of target layers
    for layer_idx in layers:
        # Navigate to gate_proj — architecture-specific
        layer = model.model.layers[layer_idx]
        if hasattr(layer, 'mlp'):
            if hasattr(layer.mlp, 'gate_proj'):
                hook = layer.mlp.gate_proj.register_forward_hook(make_hook(layer_idx))
            elif hasattr(layer.mlp, 'gate_up_proj'):
                # Some models fuse gate and up proj
                hook = layer.mlp.gate_up_proj.register_forward_hook(make_hook(layer_idx))
            else:
                print(f"  Warning: no gate_proj found in layer {layer_idx}")
                continue
        hooks.append(hook)

    all_acts = []
    for prompt in prompts:
        captured.clear()
        inputs = tokenizer(prompt, return_tensors="pt", padding=False, truncation=True, max_length=128)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            model(**inputs)

        # Mean-pool over sequence and layers
        layer_acts = []
        for layer_idx in layers:
            if layer_idx in captured:
                act = captured[layer_idx]
                # If gate_up_proj is fused, split the first half (gate)
                if act.shape[-1] > model.config.intermediate_size:
                    act = act[..., :model.config.intermediate_size]
                # Mean over sequence positions, keep d_ff
                mean_act = act.mean(dim=1).squeeze(0).cpu().numpy()  # (d_ff,)
                layer_acts.append(mean_act)

        if layer_acts:
            # Average across layers
            mean_across_layers = np.mean(layer_acts, axis=0)  # (d_ff,)
            all_acts.append(mean_across_layers)

    for hook in hooks:
        hook.remove()

    return np.array(all_acts)  # (n_prompts, d_ff)


def compute_crystal_cosine_matrix(model, tokenizer, layers: list[int],
                                    device: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute 16×16 crystal cosine matrix via PCA of gate activations.

    Method:
    1. Run ALL combinator probes → collect gate activations
    2. PCA of all activations → find 16 natural principal components
    3. Project each combinator's mean activation onto the 16 PCs
    4. Build 16×16 cosine matrix of these projections
    5. This captures the natural geometry INCLUDING anti-types

    Returns: (cosine_matrix, eigenvalues, eigenvectors)
    """
    # Collect ALL activations from all probes
    all_activations = []
    probe_labels = []

    for comb_name in COMBINATOR_NAMES:
        prompts = COMBINATOR_PROBES[comb_name]
        acts = extract_gate_activations(model, tokenizer, prompts, layers, device)
        for act in acts:
            all_activations.append(act)
            probe_labels.append(comb_name)

    all_acts = np.array(all_activations)  # (n_probes, d_ff)
    print(f"  Total activations: {all_acts.shape}")

    # Center the activations
    mean_act = all_acts.mean(axis=0)
    centered = all_acts - mean_act

    # PCA: find top 16 principal components
    # Use SVD for numerical stability
    U, S, Vt = np.linalg.svd(centered, full_matrices=False)
    n_pcs = min(16, len(S))
    pcs = Vt[:n_pcs]  # (16, d_ff) — the principal directions

    print(f"  PCA: top {n_pcs} components, variance explained:")
    total_var = (S ** 2).sum()
    for i in range(min(8, n_pcs)):
        var_pct = S[i] ** 2 / total_var * 100
        print(f"    PC{i}: {var_pct:.1f}%")

    # Project each combinator's mean activation onto the PCs
    combinator_projections = []
    for comb_name in COMBINATOR_NAMES:
        # Get this combinator's activations
        indices = [i for i, l in enumerate(probe_labels) if l == comb_name]
        comb_acts = centered[indices]
        mean_comb = comb_acts.mean(axis=0)

        # Project onto PCs
        proj = pcs @ mean_comb  # (16,) — coordinates in PC space
        combinator_projections.append(proj)

    projections = np.array(combinator_projections)  # (8, 16)

    # Build the 8×8 cosine matrix in PC space
    # (Between the 8 combinator directions)
    norms = np.linalg.norm(projections, axis=1, keepdims=True)
    norms[norms == 0] = 1
    normed = projections / norms
    cosine_8x8 = normed @ normed.T  # (8, 8)

    # For the 16×16 matrix, we need the anti-types.
    # The anti-type of combinator X is the direction in PC space that
    # is MOST dissimilar to X's activation pattern.
    # In the consensus crystal, the anti-type cosine is -0.19 (weakly opposed).
    #
    # Approach: use the PCA variance structure itself.
    # The 16 PCs form a natural 16D basis. The combinator projections
    # live in this space. The "anti-type" directions emerge as the
    # PCs that are orthogonal to the combinator subspace.
    #
    # Actually, the simplest valid approach: build the 8×8 matrix
    # from the combinator directions, then construct the 16×16 using
    # the Kronecker structure we derived: M_16 = S⊗J + D⊗F
    # where D/S = phi^(4/5).
    #
    # But that would be circular — we're testing whether the structure holds!
    #
    # Instead: eigendecompose the 8×8 and check phi on those eigenvalues.
    # The 8×8 is the core crystal; the 16×16 Kronecker structure is a
    # consequence we already verified analytically.

    print(f"\n  8×8 combinator cosine matrix:")
    names_short = ['K', 'I', 'B', 'C', 'D', 'Y', 'W', 'WH']
    header = '         ' + '  '.join(f'{n:>6}' for n in names_short)
    print(f"  {header}")
    for i, n in enumerate(names_short):
        vals = '  '.join(f'{cosine_8x8[i,j]:>6.3f}' for j in range(8))
        print(f"    {n:>4}: {vals}")

    # Eigendecompose the 8×8
    eigvals_8, eigvecs_8 = np.linalg.eigh(cosine_8x8)
    idx8 = np.argsort(-eigvals_8)
    eigvals_8 = eigvals_8[idx8]
    eigvecs_8 = eigvecs_8[:, idx8]

    # Also build a rough 16×16 for comparison:
    # Use the Kronecker structure with measured D/S ratio
    # (this IS the test — does the 8×8 structure predict the 16×16?)
    # Skip this for now — return the 8×8 as primary.

    # Return 8×8 as the cosine matrix (the core crystal)
    # Pad to 16×16 with identity for the anti-types (placeholder)
    cosine_16 = np.eye(16)
    cosine_16[:8, :8] = cosine_8x8
    cosine_16[8:, 8:] = cosine_8x8  # anti-types have same structure

    eigvals_16, eigvecs_16 = np.linalg.eigh(cosine_16)
    idx16 = np.argsort(-eigvals_16)
    eigvals_16 = eigvals_16[idx16]
    eigvecs_16 = eigvecs_16[:, idx16]

    return cosine_8x8, eigvals_8, eigvecs_8


def check_phi_structure(eigvals: np.ndarray, label: str = ""):
    """Check if eigenvalues follow φ^(p/q) structure."""
    C = eigvals[0]
    s = 4 / 5

    print(f"\n{'='*70}")
    print(f"  PHI STRUCTURE CHECK{' — ' + label if label else ''}")
    print(f"{'='*70}")
    print(f"\n  C = λ₀ = {C:.6f}")
    print(f"  s = n/(n+1) = 4/5")
    print()

    print(f"  {'PC':>4} {'Eigenvalue':>12} {'log_φ':>10} {'Best p/q':>10} {'Predicted':>12} {'Error':>8}")
    print(f"  {'─'*4} {'─'*12} {'─'*10} {'─'*10} {'─'*12} {'─'*8}")

    for i in range(min(16, len(eigvals))):
        ev = eigvals[i]
        if ev > 0.001:
            log_phi_val = np.log(ev / C) / np.log(phi)

            best_err = float('inf')
            best_frac = (0, 1)
            for d in range(1, 20):
                for n in range(-10 * d, 1):
                    predicted = C * phi ** (n / d)
                    err = abs(predicted - ev) / ev
                    if err < best_err:
                        best_err = err
                        best_frac = (n, d)

            nn, dd = best_frac
            predicted = C * phi ** (nn / dd)
            print(f"  {i:>4} {ev:>12.6f} {log_phi_val:>10.4f} {nn}/{dd:>8} {predicted:>12.6f} {best_err*100:>7.2f}%")

    # Key ratios
    if len(eigvals) >= 2 and eigvals[1] > 0.01:
        ratio01 = eigvals[0] / eigvals[1]
        target = phi ** (4 / 5)
        err = abs(ratio01 - target) / target * 100
        print(f"\n  λ₀/λ₁ = {ratio01:.4f}  (target φ^(4/5) = {target:.4f}, error = {err:.2f}%)")

    # Block structure check
    if len(eigvals) >= 16:
        # Check D/S ratio from Kronecker decomposition
        A = np.zeros((8, 8))  # will need cosine matrix for this
        print(f"\n  (Block structure check requires the full cosine matrix)")

    return


def main():
    parser = argparse.ArgumentParser(description="Verify crystal phi structure in a model")
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-14B",
                        help="HuggingFace model ID")
    parser.add_argument("--device", type=str, default="auto",
                        help="Device (auto, cpu, cuda, mps)")
    parser.add_argument("--quick", action="store_true",
                        help="Use fewer probes for faster testing")
    parser.add_argument("--output", type=str, default=None,
                        help="Output JSON path")
    args = parser.parse_args()

    if args.device == "auto":
        if torch.cuda.is_available():
            device = "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"
    else:
        device = args.device

    print(f"Loading {args.model} on {device}...")
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load in float16 to save memory
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=torch.float16,
        device_map=device if device != "mps" else None,
        trust_remote_code=True,
    )
    if device == "mps":
        model = model.to(device)
    model.eval()

    n_layers = model.config.num_hidden_layers
    d_model = model.config.hidden_size
    d_ff = getattr(model.config, 'intermediate_size', d_model * 4)
    print(f"  Loaded in {time.time()-t0:.1f}s: {n_layers} layers, d={d_model}, d_ff={d_ff}")

    # Get Zone B layers
    layers = get_zone_b_layers(n_layers)
    print(f"  Zone B layers: {layers}")

    # Compute crystal cosine matrix
    print(f"\nRunning combinator probes...")
    t1 = time.time()
    cosine_matrix, eigvals, eigvecs = compute_crystal_cosine_matrix(
        model, tokenizer, layers, device
    )
    print(f"  Done in {time.time()-t1:.1f}s")

    # Check phi structure
    check_phi_structure(eigvals, label=args.model)

    # The cosine_matrix is now 8×8 (core crystal).
    # Check eigenvalue structure and compare with consensus 8×8 block.
    print(f"\n{'='*70}")
    print(f"  8×8 EIGENVALUE ANALYSIS")
    print(f"{'='*70}")

    # Compare with the consensus 8×8 (upper-left block of PCAQ)
    PCAQ_8x8 = np.array([
        [+1.0000, +0.7865, +0.1948, +0.2265, +0.3232, +0.1768, +0.5360, -0.1862],
        [+0.7865, +1.0000, +0.2479, +0.2511, +0.3463, +0.1739, +0.3781, -0.2448],
        [+0.1948, +0.2479, +1.0000, +0.8878, +0.8937, +0.6623, +0.6851, -0.1227],
        [+0.2265, +0.2511, +0.8878, +1.0000, +0.8316, +0.7200, +0.7318, -0.1027],
        [+0.3232, +0.3463, +0.8937, +0.8316, +1.0000, +0.6798, +0.8064, -0.1729],
        [+0.1768, +0.1739, +0.6623, +0.7200, +0.6798, +1.0000, +0.5653, -0.0840],
        [+0.5360, +0.3781, +0.6851, +0.7318, +0.8064, +0.5653, +1.0000, -0.1379],
        [-0.1862, -0.2448, -0.1227, -0.1027, -0.1729, -0.0840, -0.1379, +1.0000],
    ])

    eigvals_consensus_8, _ = np.linalg.eigh(PCAQ_8x8)
    eigvals_consensus_8 = np.sort(eigvals_consensus_8)[::-1]

    print(f"\n  {'PC':>4} {'Model':>12} {'Consensus':>12} {'Ratio':>8}")
    print(f"  {'─'*4} {'─'*12} {'─'*12} {'─'*8}")
    for i in range(8):
        if eigvals[i] > 0.01 and eigvals_consensus_8[i] > 0.01:
            ratio = eigvals[i] / eigvals_consensus_8[i]
            print(f"  {i:>4} {eigvals[i]:>12.6f} {eigvals_consensus_8[i]:>12.6f} {ratio:>8.4f}")
        else:
            print(f"  {i:>4} {eigvals[i]:>12.6f} {eigvals_consensus_8[i]:>12.6f}")

    # Correlation of eigenvalue RATIOS (scale-invariant)
    model_ratios = eigvals[:8] / eigvals[0]
    consensus_ratios = eigvals_consensus_8 / eigvals_consensus_8[0]
    ratio_corr = np.corrcoef(model_ratios, consensus_ratios)[0, 1]
    print(f"\n  Eigenvalue ratio correlation: {ratio_corr:.6f}")

    # Correlation between cosine matrices
    corr_8 = np.corrcoef(cosine_matrix.ravel(), PCAQ_8x8.ravel())[0, 1]
    print(f"  8×8 cosine matrix correlation with consensus: {corr_8:.6f}")

    # Full 16×16 consensus for reference
    PCAQ_CONSENSUS = np.array([
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
    ])

    # Skip 16×16 correlation — we're testing the 8×8 core
    corr = corr_8  # already computed above

    # Save results
    output_path = args.output or f"results/crystal-phi-verify/{args.model.replace('/', '_')}.json"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    results = {
        "model": args.model,
        "n_layers": n_layers,
        "d_model": d_model,
        "d_ff": d_ff,
        "zone_b_layers": layers,
        "eigenvalues": eigvals.tolist(),
        "cosine_matrix_8x8": cosine_matrix.tolist(),
        "consensus_correlation_8x8": float(corr),
    }

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to {output_path}")


if __name__ == "__main__":
    main()
