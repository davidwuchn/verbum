#!/usr/bin/env python3
"""Eigenvector self-similarity across transformer layers.

THE QUESTION: If the FFN topology is holographic (self-similar across layers),
are the eigenvectors (rotation matrices) also self-similar? If yes, then the
"unknown rotation" between eigenspace and weight space is shared structure,
and we can potentially reconstruct magnitudes from topology + crystal equation
+ shared basis.

WHAT WE MEASURE:
  1. Singular value spectra — confirm crystal equation holds per layer
  2. Subspace overlap — do top-k left/right singular vectors span the same space?
  3. Pairwise vector alignment — can we match individual singular vectors across layers?
  4. Reconstruction test — use layer j's eigenvectors + layer i's eigenvalues to
     reconstruct layer i's weights. If this works, the rotation is deducible.

Usage:
  uv run python scripts/experiments/eigenvector_selfsimilarity.py --model Qwen/Qwen3-8B
  uv run python scripts/experiments/eigenvector_selfsimilarity.py --model Qwen/Qwen3-8B --layers 0,5,10,17,25,35
  uv run python scripts/experiments/eigenvector_selfsimilarity.py --model Qwen/Qwen3-8B --top-k 256 --weight-type gate_proj

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import os
import sys
import time
from pathlib import Path

os.environ.setdefault('PYTHONUNBUFFERED', '1')

import numpy as np
import torch


def log(msg: str = "") -> None:
    print(msg, flush=True)


# ═══════════════════════════════════════════════════════════════════════
# SVD computation with memory management
# ═══════════════════════════════════════════════════════════════════════

def compute_svd(W: torch.Tensor, top_k: int = 256) -> dict:
    """Compute truncated SVD of a weight matrix.

    Returns dict with:
      U: (m, k) left singular vectors
      S: (k,) singular values
      Vt: (k, n) right singular vectors (transposed)
    where k = min(top_k, min(m, n))
    """
    # Move to float32 for numerical stability
    W_f32 = W.float().cpu()
    m, n = W_f32.shape
    k = min(top_k, min(m, n))

    # Use full SVD and truncate (more stable than randomized for our purposes)
    # For very large matrices, we could use torch.svd_lowrank, but full SVD
    # gives us exact results for comparison
    t0 = time.time()

    # For large matrices, use lowrank approximation
    if min(m, n) > 2 * top_k:
        U, S, Vt = torch.svd_lowrank(W_f32, q=k, niter=5)
        # svd_lowrank returns V not Vt
        Vt = Vt.T  # but actually it returns V, so transpose
        # Actually torch.svd_lowrank returns (U, S, V) where W ≈ U @ diag(S) @ V^T
        # V is (n, k), so Vt = V.T is (k, n)
        # Wait, let me re-check. torch.svd_lowrank returns U (m,k), S (k,), V (n,k)
        # So W ≈ U @ diag(S) @ V.T
        # We want Vt = V.T which is (k, n)
        Vt = Vt  # Already transposed above
    else:
        U_full, S_full, Vt_full = torch.linalg.svd(W_f32, full_matrices=False)
        U = U_full[:, :k]
        S = S_full[:k]
        Vt = Vt_full[:k, :]

    elapsed = time.time() - t0
    log(f"    SVD: {m}×{n} → top-{k}, {elapsed:.1f}s")

    return {'U': U, 'S': S, 'Vt': Vt, 'shape': (m, n)}


def subspace_overlap(U1: torch.Tensor, U2: torch.Tensor) -> float:
    """Compute subspace overlap between two sets of orthonormal vectors.

    overlap = ||U1^T @ U2||_F^2 / k
    Range: [0, 1] where 1 = identical subspaces.
    """
    # U1: (m, k1), U2: (m, k2)
    G = U1.T @ U2  # (k1, k2)
    # Frobenius norm squared, normalized
    k = min(U1.shape[1], U2.shape[1])
    return (G ** 2).sum().item() / k


def best_match_cosines(U1: torch.Tensor, U2: torch.Tensor) -> torch.Tensor:
    """For each vector in U1, find the best-matching vector in U2.

    Returns tensor of max absolute cosine similarities.
    Sign ambiguity in SVD means we use |cos|.
    """
    # G[i,j] = |u1_i · u2_j|
    G = (U1.T @ U2).abs()  # (k1, k2)
    # For each vector in U1, max match in U2
    max_cos, _ = G.max(dim=1)  # (k1,)
    return max_cos


def procrustes_residual(U1: torch.Tensor, U2: torch.Tensor) -> float:
    """Orthogonal Procrustes: find R that minimizes ||U1 - U2 @ R||_F.

    Returns the normalized residual ||U1 - U2 @ R||_F / ||U1||_F.
    Small residual = U1 and U2 differ by a simple rotation.
    """
    # Solve: R* = argmin ||U1 - U2 @ R|| = V @ U^T from SVD of U2^T @ U1
    M = U2.T @ U1  # (k, k)
    U, S, Vt = torch.linalg.svd(M)
    R = U @ Vt
    aligned = U2 @ R
    residual = torch.norm(U1 - aligned).item()
    baseline = torch.norm(U1).item()
    return residual / baseline if baseline > 0 else float('inf')


def reconstruction_test(svd_source: dict, svd_target: dict, W_target: torch.Tensor) -> dict:
    """Test: can we reconstruct W_target using source's eigenvectors + target's eigenvalues?

    Reconstruction: W_recon = U_source @ diag(S_target) @ Vt_source
    Compare with W_target via cosine similarity and relative error.
    """
    U_src = svd_source['U']
    Vt_src = svd_source['Vt']
    S_tgt = svd_target['S']

    k = min(U_src.shape[1], Vt_src.shape[0], len(S_tgt))
    U_src = U_src[:, :k]
    Vt_src = Vt_src[:k, :]
    S_tgt = S_tgt[:k]

    # Reconstruct
    W_recon = U_src @ torch.diag(S_tgt) @ Vt_src

    # Flatten for comparison
    w_flat = W_target.float().cpu().flatten()
    r_flat = W_recon.flatten()

    # Cosine similarity
    cos = torch.dot(w_flat, r_flat) / (torch.norm(w_flat) * torch.norm(r_flat) + 1e-10)

    # Relative Frobenius error
    rel_err = torch.norm(w_flat - r_flat).item() / (torch.norm(w_flat).item() + 1e-10)

    # Also compare with the "correct" reconstruction using target's own eigenvectors
    U_tgt = svd_target['U'][:, :k]
    Vt_tgt = svd_target['Vt'][:k, :]
    W_self_recon = U_tgt @ torch.diag(S_tgt) @ Vt_tgt
    self_cos = torch.dot(w_flat, W_self_recon.flatten()) / (torch.norm(w_flat) * torch.norm(W_self_recon.flatten()) + 1e-10)
    self_err = torch.norm(w_flat - W_self_recon.flatten()).item() / (torch.norm(w_flat).item() + 1e-10)

    return {
        'cross_cos': cos.item(),
        'cross_rel_err': rel_err,
        'self_cos': self_cos.item(),
        'self_rel_err': self_err,
    }


def singular_value_similarity(S1: torch.Tensor, S2: torch.Tensor) -> dict:
    """Compare singular value spectra between two layers.

    Normalized spectra (divide by sum) for shape comparison.
    """
    S1_norm = S1 / S1.sum()
    S2_norm = S2 / S2.sum()
    k = min(len(S1_norm), len(S2_norm))

    cos = torch.dot(S1_norm[:k], S2_norm[:k]) / (torch.norm(S1_norm[:k]) * torch.norm(S2_norm[:k]) + 1e-10)
    ratio = S1[:k] / (S2[:k] + 1e-10)

    return {
        'spectrum_cos': cos.item(),
        'scale_ratio_mean': ratio.mean().item(),
        'scale_ratio_std': ratio.std().item(),
    }


# ═══════════════════════════════════════════════════════════════════════
# Main experiment
# ═══════════════════════════════════════════════════════════════════════

def run_experiment(model_id: str, layer_indices: list[int], weight_types: list[str],
                   top_k: int = 256, device: str = "cpu"):
    """Run the full eigenvector self-similarity experiment."""

    log("=" * 72)
    log("EIGENVECTOR SELF-SIMILARITY EXPERIMENT")
    log("=" * 72)
    log(f"Model: {model_id}")
    log(f"Layers: {layer_indices}")
    log(f"Weight types: {weight_types}")
    log(f"Top-k singular vectors: {top_k}")
    log()

    # ── Load model weights ──────────────────────────────────────────
    log("Loading model weights...")
    from transformers import AutoModelForCausalLM, AutoConfig

    config = AutoConfig.from_pretrained(model_id)
    num_layers = config.num_hidden_layers
    log(f"  Model has {num_layers} layers")
    log(f"  Hidden size: {config.hidden_size}")
    log(f"  Intermediate size: {config.intermediate_size}")

    # Validate layer indices
    for idx in layer_indices:
        assert 0 <= idx < num_layers, f"Layer {idx} out of range [0, {num_layers})"

    # Load model in float16 to save memory
    log("  Loading model (float16)...")
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="cpu",  # Keep on CPU for SVD
        low_cpu_mem_usage=True,
    )
    log(f"  Loaded in {time.time() - t0:.1f}s")

    # ── Extract and SVD each layer's weights ────────────────────────
    svd_data = {}  # (layer_idx, weight_type) → svd dict
    raw_weights = {}  # (layer_idx, weight_type) → weight tensor

    for wtype in weight_types:
        log(f"\n{'─' * 60}")
        log(f"Weight type: {wtype}")
        log(f"{'─' * 60}")

        for layer_idx in layer_indices:
            log(f"\n  Layer {layer_idx}:")

            # Get the weight matrix
            layer = model.model.layers[layer_idx]
            if wtype in ('gate_proj', 'up_proj', 'down_proj'):
                W = getattr(layer.mlp, wtype).weight.data
            elif wtype in ('q_proj', 'k_proj', 'v_proj', 'o_proj'):
                W = getattr(layer.self_attn, wtype).weight.data
            else:
                raise ValueError(f"Unknown weight type: {wtype}")

            log(f"    Shape: {W.shape}")
            raw_weights[(layer_idx, wtype)] = W.clone()

            # Compute SVD
            svd = compute_svd(W, top_k=top_k)
            svd_data[(layer_idx, wtype)] = svd

            # Quick stats on singular values
            S = svd['S']
            log(f"    S range: [{S[-1].item():.4f}, {S[0].item():.4f}]")
            log(f"    S[0]/S[-1] condition: {S[0].item() / (S[-1].item() + 1e-10):.1f}")
            energy_top10 = (S[:10] ** 2).sum() / (S ** 2).sum()
            energy_top50 = (S[:50] ** 2).sum() / (S ** 2).sum()
            log(f"    Energy in top-10: {energy_top10.item():.4f}")
            log(f"    Energy in top-50: {energy_top50.item():.4f}")

    # ── Free model to save memory ───────────────────────────────────
    del model
    gc.collect()

    # ── Experiment 1: Singular value spectrum similarity ────────────
    log(f"\n{'=' * 72}")
    log("EXPERIMENT 1: SINGULAR VALUE SPECTRUM SIMILARITY")
    log(f"{'=' * 72}")
    log("Do the eigenvalue spectra have the same SHAPE across layers?")
    log("(Normalized spectra — comparing shape, not scale)")

    for wtype in weight_types:
        log(f"\n  {wtype}:")
        layers_for_type = [l for l in layer_indices if (l, wtype) in svd_data]
        for i, l1 in enumerate(layers_for_type):
            for l2 in layers_for_type[i+1:]:
                sim = singular_value_similarity(
                    svd_data[(l1, wtype)]['S'],
                    svd_data[(l2, wtype)]['S']
                )
                log(f"    L{l1:2d} vs L{l2:2d}: spectrum_cos={sim['spectrum_cos']:.6f}  "
                    f"scale_ratio={sim['scale_ratio_mean']:.3f}±{sim['scale_ratio_std']:.3f}")

    # ── Experiment 2: Subspace overlap ──────────────────────────────
    log(f"\n{'=' * 72}")
    log("EXPERIMENT 2: SUBSPACE OVERLAP (top-k left & right singular vectors)")
    log(f"{'=' * 72}")
    log("Overlap=1.0 means identical subspaces. Random ≈ k/min(m,n).")

    for wtype in weight_types:
        log(f"\n  {wtype} — LEFT singular vectors (U):")
        layers_for_type = [l for l in layer_indices if (l, wtype) in svd_data]

        # Compute expected random overlap for reference
        shape = svd_data[(layers_for_type[0], wtype)]['shape']
        k = svd_data[(layers_for_type[0], wtype)]['U'].shape[1]
        random_overlap = k / min(shape[0], shape[1])
        log(f"    Random baseline: {random_overlap:.6f}")

        for i, l1 in enumerate(layers_for_type):
            for l2 in layers_for_type[i+1:]:
                U1 = svd_data[(l1, wtype)]['U']
                U2 = svd_data[(l2, wtype)]['U']
                overlap = subspace_overlap(U1, U2)
                log(f"    L{l1:2d} vs L{l2:2d}: overlap={overlap:.6f}")

        log(f"\n  {wtype} — RIGHT singular vectors (Vt):")
        for i, l1 in enumerate(layers_for_type):
            for l2 in layers_for_type[i+1:]:
                Vt1 = svd_data[(l1, wtype)]['Vt']
                Vt2 = svd_data[(l2, wtype)]['Vt']
                # Vt rows are the right singular vectors
                overlap = subspace_overlap(Vt1.T, Vt2.T)
                log(f"    L{l1:2d} vs L{l2:2d}: overlap={overlap:.6f}")

    # ── Experiment 3: Best-match cosines ────────────────────────────
    log(f"\n{'=' * 72}")
    log("EXPERIMENT 3: BEST-MATCH COSINE SIMILARITIES")
    log(f"{'=' * 72}")
    log("For each singular vector in layer i, find its best match in layer j.")
    log("High mean |cos| = individual vectors transfer across layers.")

    for wtype in weight_types:
        log(f"\n  {wtype} — LEFT singular vectors (U):")
        layers_for_type = [l for l in layer_indices if (l, wtype) in svd_data]

        for i, l1 in enumerate(layers_for_type):
            for l2 in layers_for_type[i+1:]:
                U1 = svd_data[(l1, wtype)]['U']
                U2 = svd_data[(l2, wtype)]['U']
                cos = best_match_cosines(U1, U2)
                log(f"    L{l1:2d} vs L{l2:2d}: mean|cos|={cos.mean().item():.4f}  "
                    f"median={cos.median().item():.4f}  "
                    f"top10_mean={cos[:10].mean().item():.4f}  "
                    f"bot10_mean={cos[-10:].mean().item():.4f}")

    # ── Experiment 4: Procrustes alignment ──────────────────────────
    log(f"\n{'=' * 72}")
    log("EXPERIMENT 4: PROCRUSTES ALIGNMENT RESIDUAL")
    log(f"{'=' * 72}")
    log("If U1 ≈ U2 @ R for some rotation R, residual → 0.")
    log("Small residual = layers differ by a simple rotation.")

    for wtype in weight_types:
        log(f"\n  {wtype} — LEFT singular vectors (U):")
        layers_for_type = [l for l in layer_indices if (l, wtype) in svd_data]

        for i, l1 in enumerate(layers_for_type):
            for l2 in layers_for_type[i+1:]:
                U1 = svd_data[(l1, wtype)]['U']
                U2 = svd_data[(l2, wtype)]['U']
                res = procrustes_residual(U1, U2)
                log(f"    L{l1:2d} vs L{l2:2d}: residual={res:.6f}")

    # ── Experiment 5: Cross-layer reconstruction ────────────────────
    log(f"\n{'=' * 72}")
    log("EXPERIMENT 5: CROSS-LAYER RECONSTRUCTION")
    log(f"{'=' * 72}")
    log("Reconstruct layer i's weights using layer j's eigenvectors + layer i's eigenvalues.")
    log("If cross_cos ≈ self_cos, the eigenvectors are shared.")

    for wtype in weight_types:
        log(f"\n  {wtype}:")
        layers_for_type = [l for l in layer_indices if (l, wtype) in svd_data]

        for i, l1 in enumerate(layers_for_type):
            for l2 in layers_for_type[i+1:]:
                W_target = raw_weights[(l1, wtype)]
                result = reconstruction_test(
                    svd_source=svd_data[(l2, wtype)],
                    svd_target=svd_data[(l1, wtype)],
                    W_target=W_target
                )
                log(f"    Reconstruct L{l1:2d} from L{l2:2d}'s basis: "
                    f"cross_cos={result['cross_cos']:.6f}  "
                    f"self_cos={result['self_cos']:.6f}  "
                    f"cross_err={result['cross_rel_err']:.4f}  "
                    f"self_err={result['self_rel_err']:.4f}")

    # ── Experiment 6: Sign reconstruction ───────────────────────────
    log(f"\n{'=' * 72}")
    log("EXPERIMENT 6: SIGN-ONLY RECONSTRUCTION (THE KEY TEST)")
    log(f"{'=' * 72}")
    log("Given sign(W_target) + S_crystal (eigenvalues from crystal eq) +")
    log("U,V from another layer → can we recover W_target's magnitudes?")
    log()
    log("Test: W_recon = U_source @ diag(S_target) @ Vt_source")
    log("Then: W_signed = sign(W_target) * |W_recon|")
    log("This uses the target's topology + source's rotation + target's spectrum.")

    for wtype in weight_types:
        log(f"\n  {wtype}:")
        layers_for_type = [l for l in layer_indices if (l, wtype) in svd_data]

        for i, l1 in enumerate(layers_for_type):
            W_target = raw_weights[(l1, wtype)].float().cpu()
            signs_target = torch.sign(W_target)

            for l2 in layers_for_type:
                if l1 == l2:
                    continue

                U_src = svd_data[(l2, wtype)]['U']
                Vt_src = svd_data[(l2, wtype)]['Vt']
                S_tgt = svd_data[(l1, wtype)]['S']

                k = min(U_src.shape[1], Vt_src.shape[0], len(S_tgt))
                W_recon = U_src[:, :k] @ torch.diag(S_tgt[:k]) @ Vt_src[:k, :]

                # Apply the target's signs to the reconstruction's magnitudes
                W_signed = signs_target * W_recon.abs()

                w_flat = W_target.flatten()
                r_flat = W_signed.flatten()
                cos = torch.dot(w_flat, r_flat) / (torch.norm(w_flat) * torch.norm(r_flat) + 1e-10)
                rel_err = torch.norm(w_flat - r_flat) / (torch.norm(w_flat) + 1e-10)

                log(f"    L{l1:2d} signs + L{l2:2d} rotation: "
                    f"cos={cos.item():.6f}  rel_err={rel_err.item():.4f}")

    log(f"\n{'=' * 72}")
    log("DONE")
    log(f"{'=' * 72}")


def main():
    parser = argparse.ArgumentParser(description="Eigenvector self-similarity experiment")
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-8B")
    parser.add_argument("--layers", type=str, default="0,1,5,10,17,25,35",
                        help="Comma-separated layer indices to compare")
    parser.add_argument("--weight-type", type=str, default="gate_proj,down_proj",
                        help="Comma-separated weight types to analyze")
    parser.add_argument("--top-k", type=int, default=256,
                        help="Number of top singular vectors to compare")
    args = parser.parse_args()

    layer_indices = [int(x) for x in args.layers.split(",")]
    weight_types = [x.strip() for x in args.weight_type.split(",")]

    run_experiment(
        model_id=args.model,
        layer_indices=layer_indices,
        weight_types=weight_types,
        top_k=args.top_k,
    )


if __name__ == "__main__":
    main()
