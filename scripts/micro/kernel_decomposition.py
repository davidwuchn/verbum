"""
Kernel Decomposition — Can the full forward pass be computed from crystal constants?

Hypothesis: The inference pattern (alternating compose→select overlay) emerges
from the INTERACTION between:
  (A) Attention's soft reduction: softmax(QK^T/√d) · V
  (B) FFN's ternary grating: sign(eigenvector) routing

If both are computable from crystal eigendecomposition + distance prior,
then the entire model collapses to a kernel function:

    kernel(tokens) = Σ_layers lens(crystal, distance_prior, tokens)

This script runs three phases:
  Phase 1 — Decompose attention into crystal eigenbasis
  Phase 2 — Separate distance prior from content contribution
  Phase 3 — Kernel reconstruction vs actual forward pass

Usage:
    cd verbum
    uv run python scripts/micro/kernel_decomposition.py [checkpoint_path]
    # Default: checkpoints/micro/final

License: MIT
"""

from __future__ import annotations

import json
import sys
import math
from pathlib import Path

import numpy as np
import mlx.core as mx
import mlx.nn as nn

sys.path.insert(0, str(Path(__file__).parent))
from micro_model import (
    MicroModel, MicroConfig,
    PCAQ_ZONE_B_TARGETS, _precompute_parity_eigenbasis,
    COMBINATOR_NAMES, ANTI_COMBINATOR_NAMES,
    N_COMBINATORS, N_TOTAL_COMBINATORS,
)
from deep_trace import (
    get_crystal_basis, to_crystal_coords,
    extract_full_overlays, PC_NAMES,
)
from train_micro import (
    load_compile_examples,
    tokenize_examples,
)

# ══════════════════════════════════════════════════════════════════════
# Utilities
# ══════════════════════════════════════════════════════════════════════

def load_model(checkpoint_path: str) -> tuple[MicroModel, 'AutoTokenizer']:
    """Load trained micro model and tokenizer."""
    from transformers import AutoTokenizer

    cfg = MicroConfig()
    model = MicroModel(cfg)

    ckpt = Path(checkpoint_path)
    weights = mx.load(str(ckpt / "model.npz"))
    model.load_weights(list(weights.items()))
    mx.eval(model.parameters())

    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B", trust_remote_code=True)

    return model, tokenizer


def prepare_inputs(tokenizer, cfg: MicroConfig, n_examples: int = 32) -> tuple[mx.array, mx.array]:
    """Load and tokenize evaluation examples."""
    examples = load_compile_examples(cfg.eval_file)[:n_examples]
    sequences = tokenize_examples(examples, tokenizer, cfg.max_seq_len, cfg.eod_id)

    # Pad to same length
    max_len = max(len(s) for s in sequences)
    max_len = min(max_len, cfg.max_seq_len)

    input_batch = []
    target_batch = []
    for seq in sequences:
        ids = [int(x) for x in seq[:max_len]]
        pad_len = max_len - len(ids)
        padded = ids + [cfg.eod_id] * pad_len
        input_batch.append(padded[:-1])
        target_batch.append(padded[1:])

    return mx.array(input_batch), mx.array(target_batch)


# ══════════════════════════════════════════════════════════════════════
# Phase 1: Decompose attention into crystal eigenbasis
# ══════════════════════════════════════════════════════════════════════

def phase1_attention_in_crystal_basis(
    model: MicroModel,
    input_ids: mx.array,
    crystal_emb: np.ndarray,
    eigvecs: np.ndarray,
) -> dict:
    """Project attention weights and Q/K/V into crystal eigenbasis.

    Measures:
      - Q rotation per layer/head in crystal coordinates
      - K selectivity per layer/head in crystal coordinates
      - V contribution per layer/head in crystal coordinates
      - Attention weight patterns decomposed into eigenplane components
      - How much of attention aligns with the crystal eigenplanes vs residual
    """
    print("\n" + "=" * 70)
    print("  PHASE 1: Attention in Crystal Eigenbasis")
    print("=" * 70)

    cfg = model.cfg
    norms = np.linalg.norm(crystal_emb, axis=1, keepdims=True) + 1e-8
    crystal_norm = crystal_emb / norms

    # Run forward with trace capture
    model.set_capture(True)
    logits, _ = model(input_ids)
    mx.eval(logits)
    traces = model.get_traces()
    model.set_capture(False)

    results = {"layers": []}

    for layer_trace in traces:
        layer_idx = layer_trace["layer"]
        attn = layer_trace["attn"]

        # Get attention data
        q = np.array(attn["q"])     # (B, H, L, d_head)
        k = np.array(attn["k"])
        v = np.array(attn["v"])
        attn_weights = np.array(attn["attn_weights"])  # (B, H, L, L)

        B, H, L, d_head = q.shape

        # ── Q/K/V projection matrices in crystal eigenbasis ──
        block = model.blocks[layer_idx]
        q_w = np.array(block.attn.q_proj.weight)  # (d_model, d_model)
        k_w = np.array(block.attn.k_proj.weight)
        v_w = np.array(block.attn.v_proj.weight)
        o_w = np.array(block.attn.o_proj.weight)

        # Q in crystal eigenbasis: project through crystal embeddings
        q_crystal = crystal_norm @ q_w.T @ crystal_norm.T   # (16, 16)
        q_eigen = eigvecs.T @ q_crystal @ eigvecs            # (16, 16)

        # OV circuit: what does attention WRITE in crystal space?
        ov_circuit = crystal_norm @ (o_w @ v_w).T @ crystal_norm.T
        ov_eigen = eigvecs.T @ ov_circuit @ eigvecs

        # ── Attention weight analysis per head ──
        head_results = []
        for h in range(H):
            # Average attention pattern across batch and query positions
            avg_attn = attn_weights[:, h, :, :].mean(axis=0)  # (L, L)

            # Distance distribution: how much weight goes to each distance?
            distance_profile = np.zeros(L)
            for dist in range(L):
                # Collect attention weight at this distance across all positions
                weights_at_dist = []
                for pos in range(dist, L):
                    weights_at_dist.append(avg_attn[pos, pos - dist])
                if weights_at_dist:
                    distance_profile[dist] = np.mean(weights_at_dist)

            # Self-attention ratio (distance 0)
            self_attn_ratio = distance_profile[0] if L > 0 else 0.0

            # Attention entropy (how spread out is the attention?)
            # Higher entropy = more uniform, lower = more peaked
            attn_flat = avg_attn.flatten()
            attn_flat = attn_flat[attn_flat > 1e-10]  # remove zeros
            entropy = -np.sum(attn_flat * np.log(attn_flat + 1e-10))

            # Project attended values into crystal space
            # For each batch element: attn_weights @ V → attended_V
            v_head = v[:, h, :, :]  # (B, L, d_head)
            attn_v = attn_weights[:, h, :, :] @ v_head  # (B, L, d_head)

            head_results.append({
                "head": h,
                "distance_profile": distance_profile[:16].tolist(),  # first 16 positions
                "self_attn_ratio": float(self_attn_ratio),
                "entropy": float(entropy),
            })

        # ── Q rotation eigenplane alignment ──
        # Decompose Q rotation into eigenplane components
        q8 = q_eigen[:8, :8]  # top 8 PCs
        # Antisymmetric part = rotation generators
        q_antisym = (q8 - q8.T) / 2
        # How much rotation between PC0 (comp) and PC1 (sel)?
        comp_sel_rotation = float(q_antisym[0, 1])
        # Total rotation magnitude
        rotation_magnitude = float(np.sqrt(np.sum(q_antisym ** 2)))

        layer_result = {
            "layer": layer_idx,
            "q_rotation_eigen": q8.tolist(),
            "ov_circuit_eigen": ov_eigen[:8, :8].tolist(),
            "comp_sel_rotation": comp_sel_rotation,
            "rotation_magnitude": rotation_magnitude,
            "heads": head_results,
        }

        results["layers"].append(layer_result)

        # Print summary
        print(f"\n  Layer {layer_idx}:")
        print(f"    Q rotation (comp↔sel): {comp_sel_rotation:.4f}  "
              f"(total magnitude: {rotation_magnitude:.4f})")
        print(f"    OV diagonal (top 4 PCs): "
              f"[{', '.join(f'{ov_eigen[i,i]:.3f}' for i in range(4))}]")
        for hr in head_results:
            print(f"    Head {hr['head']}: self_attn={hr['self_attn_ratio']:.3f}  "
                  f"entropy={hr['entropy']:.2f}  "
                  f"dist_profile=[{', '.join(f'{d:.3f}' for d in hr['distance_profile'][:6])}]")

    return results


# ══════════════════════════════════════════════════════════════════════
# Phase 2: Separate distance prior from content
# ══════════════════════════════════════════════════════════════════════

def phase2_distance_vs_content(
    model: MicroModel,
    input_ids: mx.array,
    alpha: float = 1.18,
) -> dict:
    """Decompose attention weights into distance prior + content residual.

    For each layer/head:
      1. Compute the power-law distance prior: w(d) = 1/(d+1)^α
      2. Fit the prior to observed attention (find best α and scale)
      3. Compute residual: observed - fitted_prior
      4. Measure: what fraction of attention variance is distance vs content?
      5. Analyze: is the content residual low-rank?
    """
    print("\n" + "=" * 70)
    print("  PHASE 2: Distance Prior vs Content")
    print("=" * 70)

    cfg = model.cfg

    # Run forward with capture
    model.set_capture(True)
    logits, _ = model(input_ids)
    mx.eval(logits)
    traces = model.get_traces()
    model.set_capture(False)

    results = {"layers": [], "summary": {}}

    all_distance_fracs = []
    all_content_ranks = []

    for layer_trace in traces:
        layer_idx = layer_trace["layer"]
        attn_weights = np.array(layer_trace["attn"]["attn_weights"])  # (B, H, L, L)
        B, H, L, _ = attn_weights.shape

        layer_results = {"layer": layer_idx, "heads": []}

        for h in range(H):
            # Average attention across batch
            avg_attn = attn_weights[:, h, :, :].mean(axis=0)  # (L, L)

            # ── Build distance prior matrix ──
            # For causal attention: prior[i, j] = 1/(i-j+1)^α for j <= i, 0 otherwise
            distance_prior = np.zeros((L, L))
            for i in range(L):
                for j in range(i + 1):
                    distance_prior[i, j] = 1.0 / ((i - j + 1) ** alpha)

            # Normalize each row to sum to 1 (like softmax)
            row_sums = distance_prior.sum(axis=1, keepdims=True)
            row_sums = np.maximum(row_sums, 1e-10)
            distance_prior_norm = distance_prior / row_sums

            # ── Fit: find best scale between prior and observed ──
            # Use causal mask (lower triangle only)
            mask = np.tril(np.ones((L, L), dtype=bool))
            obs_vals = avg_attn[mask]
            prior_vals = distance_prior_norm[mask]

            # Variance explained by distance prior
            # R² = 1 - Var(residual) / Var(observed)
            residual = obs_vals - prior_vals
            var_obs = np.var(obs_vals)
            var_residual = np.var(residual)
            r_squared = 1.0 - var_residual / (var_obs + 1e-10)

            # Correlation
            corr = np.corrcoef(obs_vals, prior_vals)[0, 1] if var_obs > 1e-10 else 0.0

            distance_frac = max(0, r_squared)
            content_frac = 1.0 - distance_frac
            all_distance_fracs.append(distance_frac)

            # ── Content residual rank analysis ──
            content_matrix = avg_attn - distance_prior_norm
            # Apply causal mask
            content_matrix = content_matrix * np.tril(np.ones((L, L)))

            # SVD of content residual
            U, S, Vt = np.linalg.svd(content_matrix, full_matrices=False)
            total_energy = np.sum(S ** 2)
            cumulative = np.cumsum(S ** 2) / (total_energy + 1e-10)

            # Effective rank: how many singular values capture 90% of energy?
            rank_90 = int(np.searchsorted(cumulative, 0.90)) + 1
            rank_95 = int(np.searchsorted(cumulative, 0.95)) + 1
            rank_99 = int(np.searchsorted(cumulative, 0.99)) + 1
            all_content_ranks.append(rank_90)

            # Top singular value dominance
            sv_ratio = float(S[0] / S[1]) if len(S) > 1 and S[1] > 1e-10 else float('inf')

            head_result = {
                "head": h,
                "r_squared": float(r_squared),
                "correlation": float(corr),
                "distance_frac": float(distance_frac),
                "content_frac": float(content_frac),
                "content_rank_90": rank_90,
                "content_rank_95": rank_95,
                "content_rank_99": rank_99,
                "sv_ratio_1_2": float(sv_ratio),
                "top_5_sv": S[:5].tolist(),
            }
            layer_results["heads"].append(head_result)

            print(f"\n  Layer {layer_idx}, Head {h}:")
            print(f"    Distance prior R²: {r_squared:.4f}  (corr: {corr:.4f})")
            print(f"    Distance: {distance_frac:.1%}  Content: {content_frac:.1%}")
            print(f"    Content rank (90%): {rank_90}  (95%): {rank_95}  (99%): {rank_99}")
            print(f"    σ₁/σ₂ = {sv_ratio:.1f}")
            print(f"    Top 5 σ: [{', '.join(f'{s:.4f}' for s in S[:5])}]")

        # ── Fit per-layer α ──
        # Find optimal α for this layer by scanning
        best_alpha = alpha
        best_r2 = -1
        for test_alpha in np.arange(0.2, 3.0, 0.05):
            dp = np.zeros((L, L))
            for i in range(L):
                for j in range(i + 1):
                    dp[i, j] = 1.0 / ((i - j + 1) ** test_alpha)
            rs = dp.sum(axis=1, keepdims=True)
            dp_n = dp / np.maximum(rs, 1e-10)

            # Average across heads
            avg_all_heads = attn_weights[:, :, :, :].mean(axis=(0, 1))
            o = avg_all_heads[mask]
            p = dp_n[mask]
            r = o - p
            r2 = 1.0 - np.var(r) / (np.var(o) + 1e-10)
            if r2 > best_r2:
                best_r2 = r2
                best_alpha = test_alpha

        layer_results["fitted_alpha"] = float(best_alpha)
        layer_results["fitted_r2"] = float(best_r2)
        results["layers"].append(layer_results)
        print(f"\n  Layer {layer_idx} best α: {best_alpha:.2f} (R²={best_r2:.4f})")

    # Summary
    mean_dist = np.mean(all_distance_fracs)
    mean_rank = np.mean(all_content_ranks)
    results["summary"] = {
        "mean_distance_fraction": float(mean_dist),
        "mean_content_fraction": float(1 - mean_dist),
        "mean_content_rank_90": float(mean_rank),
        "alpha_used": alpha,
    }

    print(f"\n{'─' * 60}")
    print(f"  SUMMARY:")
    print(f"    Mean distance fraction: {mean_dist:.1%}")
    print(f"    Mean content fraction:  {1-mean_dist:.1%}")
    print(f"    Mean content rank (90%): {mean_rank:.1f}")
    print(f"{'─' * 60}")

    return results


# ══════════════════════════════════════════════════════════════════════
# Phase 3: Kernel reconstruction vs actual forward pass
# ══════════════════════════════════════════════════════════════════════

def phase3_kernel_reconstruction(
    model: MicroModel,
    input_ids: mx.array,
    crystal_emb: np.ndarray,
    eigvecs: np.ndarray,
    eigvals: np.ndarray,
    alpha: float = 1.18,
) -> dict:
    """Attempt to reconstruct the forward pass from crystal constants.

    The kernel hypothesis:
      1. Attention profile ≈ distance_prior (power law with α=1.18)
      2. FFN overlay = sign(eigenvector) routing (from eigendecomposition)
      3. The full forward pass = iterate(attention_reduce + ffn_grating)

    We reconstruct the residual stream at each layer boundary using:
      - Crystal-predicted attention (distance prior only, no content Q·K)
      - Crystal-predicted FFN overlay (eigendecomposition, no learned weights)
    And compare to the actual residual stream from the real forward pass.

    Then we add back components incrementally:
      - kernel_v0: distance prior only (no Q·K content)
      - kernel_v1: distance prior + actual Q·K (content-aware attention)
      - kernel_v2: v1 + actual FFN (full attention, analytical FFN)
      - ground_truth: actual forward pass
    """
    print("\n" + "=" * 70)
    print("  PHASE 3: Kernel Reconstruction")
    print("=" * 70)

    cfg = model.cfg
    B, L = input_ids.shape
    norms = np.linalg.norm(crystal_emb, axis=1, keepdims=True) + 1e-8
    crystal_norm = crystal_emb / norms

    # ── Ground truth: actual forward pass with captured residuals ──
    model.set_capture(True)
    logits_gt, _ = model(input_ids)
    mx.eval(logits_gt)
    traces = model.get_traces()
    model.set_capture(False)

    # Collect ground truth residual streams
    gt_residuals = []
    positions = mx.arange(L)
    x_gt = np.array(model.embed(input_ids) + model.pos_embed(positions))
    mx.eval(x_gt)
    x_gt = np.array(x_gt)  # (B, L, d_model)
    gt_residuals.append({"stage": "embed", "residual": x_gt.copy()})

    for layer_trace in traces:
        layer = layer_trace["layer"]
        block = layer_trace["block"]
        gt_residuals.append({
            "stage": f"L{layer}_post_attn",
            "residual": np.array(block["residual_post_attn"]),
        })
        gt_residuals.append({
            "stage": f"L{layer}_post_ffn",
            "residual": np.array(block["residual_post_ffn"]),
        })

    # ── Build distance prior ──
    distance_prior = np.zeros((L, L))
    for i in range(L):
        for j in range(i + 1):
            distance_prior[i, j] = 1.0 / ((i - j + 1) ** alpha)
    row_sums = distance_prior.sum(axis=1, keepdims=True)
    distance_prior_norm = distance_prior / np.maximum(row_sums, 1e-10)

    # ── Build analytical FFN overlays from eigendecomposition ──
    # The overlay at layer l: O_l[i,j] = (-1)^l * sqrt(λ_i * λ_j) * delta(i,j)
    # (diagonal approximation from mechanism extraction)
    analytical_overlays = []
    for layer_idx in range(cfg.n_layers):
        alternation = (-1.0) ** layer_idx
        overlay = np.zeros((16, 16))
        for pc in range(16):
            amplitude = np.sqrt(max(eigvals[pc], 0))
            overlay[pc, pc] = alternation * amplitude
        analytical_overlays.append(overlay)

    # ── Extract actual overlays for comparison ──
    actual_overlays = extract_full_overlays(model, crystal_emb, eigvecs)

    # ── Kernel v0: distance prior attention + analytical FFN ──
    print("\n  Reconstructing with kernel...")

    # Start from actual embeddings (these are learned, not crystal-derivable)
    x_kernel = x_gt.copy()  # (B, L, d_model)

    kernel_residuals_v0 = [{"stage": "embed", "residual": x_kernel.copy()}]

    for layer_idx in range(cfg.n_layers):
        block = model.blocks[layer_idx]

        # ── v0 attention: distance prior only ──
        # Normalize input
        x_normed = np.array(block.attn_norm(mx.array(x_kernel)))

        # Get actual V projection (the content we're reducing over)
        v_w = np.array(block.attn.v_proj.weight)   # (d_model, d_model)
        o_w = np.array(block.attn.o_proj.weight)   # (d_model, d_model)
        v_proj = x_normed @ v_w.T                   # (B, L, d_model)

        # Apply distance prior as attention weights
        # Shape: (L, L) applied to (B, L, d_model)
        attn_out_v0 = distance_prior_norm @ v_proj   # (B, L, d_model)
        attn_out_v0 = attn_out_v0 @ o_w.T            # project through o_proj

        x_post_attn = x_kernel + attn_out_v0
        kernel_residuals_v0.append({
            "stage": f"L{layer_idx}_post_attn",
            "residual": x_post_attn.copy(),
        })

        # ── v0 FFN: analytical overlay ──
        x_ffn_in = np.array(block.ffn_norm(mx.array(x_post_attn)))

        # Project input to crystal eigenbasis
        x_crystal = to_crystal_coords(x_ffn_in.reshape(-1, cfg.d_model),
                                       crystal_emb, eigvecs)  # (B*L, 16)

        # Apply analytical overlay
        overlay = analytical_overlays[layer_idx]
        x_transformed = x_crystal @ overlay.T  # (B*L, 16)

        # Project back to model space
        # crystal_coords → combinator_space → model_space
        x_combinator = x_transformed @ eigvecs.T  # (B*L, 16)
        x_model = x_combinator @ crystal_norm     # (B*L, d_model)
        x_model = x_model.reshape(B, L, cfg.d_model)

        # Scale to match FFN magnitude
        actual_ffn = np.array(traces[layer_idx]["block"]["ffn_contribution"])
        ffn_scale = np.linalg.norm(actual_ffn) / (np.linalg.norm(x_model) + 1e-10)
        x_model *= ffn_scale

        x_kernel = x_post_attn + x_model
        kernel_residuals_v0.append({
            "stage": f"L{layer_idx}_post_ffn",
            "residual": x_kernel.copy(),
        })

    # ── Kernel v1: actual attention + analytical FFN ──
    x_kernel_v1 = x_gt.copy()
    kernel_residuals_v1 = [{"stage": "embed", "residual": x_kernel_v1.copy()}]

    for layer_idx in range(cfg.n_layers):
        block = model.blocks[layer_idx]

        # Use ACTUAL attention (real Q·K + real softmax)
        actual_attn_contrib = np.array(traces[layer_idx]["block"]["attn_contribution"])
        x_post_attn = x_kernel_v1 + actual_attn_contrib
        kernel_residuals_v1.append({
            "stage": f"L{layer_idx}_post_attn",
            "residual": x_post_attn.copy(),
        })

        # Analytical FFN (same as v0)
        x_ffn_in = np.array(block.ffn_norm(mx.array(x_post_attn)))
        x_crystal = to_crystal_coords(x_ffn_in.reshape(-1, cfg.d_model),
                                       crystal_emb, eigvecs)
        overlay = analytical_overlays[layer_idx]
        x_transformed = x_crystal @ overlay.T
        x_combinator = x_transformed @ eigvecs.T
        x_model = x_combinator @ crystal_norm
        x_model = x_model.reshape(B, L, cfg.d_model)

        actual_ffn = np.array(traces[layer_idx]["block"]["ffn_contribution"])
        ffn_scale = np.linalg.norm(actual_ffn) / (np.linalg.norm(x_model) + 1e-10)
        x_model *= ffn_scale

        x_kernel_v1 = x_post_attn + x_model
        kernel_residuals_v1.append({
            "stage": f"L{layer_idx}_post_ffn",
            "residual": x_kernel_v1.copy(),
        })

    # ── Kernel v2: actual attention + actual FFN ──
    # This is just the ground truth, but built incrementally to confirm
    x_kernel_v2 = x_gt.copy()
    kernel_residuals_v2 = [{"stage": "embed", "residual": x_kernel_v2.copy()}]

    for layer_idx in range(cfg.n_layers):
        actual_attn = np.array(traces[layer_idx]["block"]["attn_contribution"])
        actual_ffn = np.array(traces[layer_idx]["block"]["ffn_contribution"])
        x_kernel_v2 = x_kernel_v2 + actual_attn
        kernel_residuals_v2.append({
            "stage": f"L{layer_idx}_post_attn",
            "residual": x_kernel_v2.copy(),
        })
        x_kernel_v2 = x_kernel_v2 + actual_ffn
        kernel_residuals_v2.append({
            "stage": f"L{layer_idx}_post_ffn",
            "residual": x_kernel_v2.copy(),
        })

    # ── Compare all versions ──
    print(f"\n{'─' * 70}")
    print(f"  {'Stage':<20} {'v0(dist+anal)':<18} {'v1(real+anal)':<18} {'v2(real+real)':<18}")
    print(f"  {'':20} {'cos / MSE':<18} {'cos / MSE':<18} {'cos / MSE':<18}")
    print(f"{'─' * 70}")

    comparisons = {"stages": []}

    for i, gt_r in enumerate(gt_residuals):
        stage = gt_r["stage"]
        gt_flat = gt_r["residual"].reshape(-1, cfg.d_model)

        metrics = {"stage": stage}
        for label, kernel_residuals in [("v0", kernel_residuals_v0),
                                         ("v1", kernel_residuals_v1),
                                         ("v2", kernel_residuals_v2)]:
            k_flat = kernel_residuals[i]["residual"].reshape(-1, cfg.d_model)

            # Cosine similarity (per-vector, averaged)
            gt_norms = np.linalg.norm(gt_flat, axis=1, keepdims=True) + 1e-10
            k_norms = np.linalg.norm(k_flat, axis=1, keepdims=True) + 1e-10
            cos_sim = np.mean(np.sum((gt_flat / gt_norms) * (k_flat / k_norms), axis=1))

            # Relative MSE
            mse = np.mean((gt_flat - k_flat) ** 2)
            gt_var = np.mean(gt_flat ** 2)
            rel_mse = mse / (gt_var + 1e-10)

            metrics[f"{label}_cos"] = float(cos_sim)
            metrics[f"{label}_rel_mse"] = float(rel_mse)

        comparisons["stages"].append(metrics)

        v0_cos = metrics["v0_cos"]
        v1_cos = metrics["v1_cos"]
        v2_cos = metrics["v2_cos"]
        v0_mse = metrics["v0_rel_mse"]
        v1_mse = metrics["v1_rel_mse"]
        v2_mse = metrics["v2_rel_mse"]

        print(f"  {stage:<20} {v0_cos:+.4f} / {v0_mse:.4f}  "
              f"{v1_cos:+.4f} / {v1_mse:.4f}  "
              f"{v2_cos:+.4f} / {v2_mse:.4f}")

    # ── Crystal-space comparison (more meaningful than model-space) ──
    print(f"\n{'─' * 70}")
    print(f"  Crystal-space comparison (top 8 PCs):")
    print(f"{'─' * 70}")
    print(f"  {'Stage':<20} {'v0 cos':<12} {'v1 cos':<12} {'v2 cos':<12}")

    crystal_comparisons = {"stages": []}

    for i, gt_r in enumerate(gt_residuals):
        stage = gt_r["stage"]
        gt_crystal = to_crystal_coords(
            gt_r["residual"].reshape(-1, cfg.d_model), crystal_emb, eigvecs)

        metrics = {"stage": stage}
        for label, kernel_residuals in [("v0", kernel_residuals_v0),
                                         ("v1", kernel_residuals_v1),
                                         ("v2", kernel_residuals_v2)]:
            k_crystal = to_crystal_coords(
                kernel_residuals[i]["residual"].reshape(-1, cfg.d_model),
                crystal_emb, eigvecs)

            # Use top 8 PCs only
            gt8 = gt_crystal[:, :8]
            k8 = k_crystal[:, :8]

            # Cosine similarity in crystal space
            gt_n = np.linalg.norm(gt8, axis=1, keepdims=True) + 1e-10
            k_n = np.linalg.norm(k8, axis=1, keepdims=True) + 1e-10
            cos_sim = np.mean(np.sum((gt8 / gt_n) * (k8 / k_n), axis=1))

            metrics[f"{label}_crystal_cos"] = float(cos_sim)

        crystal_comparisons["stages"].append(metrics)
        print(f"  {stage:<20} {metrics['v0_crystal_cos']:+.4f}      "
              f"{metrics['v1_crystal_cos']:+.4f}      "
              f"{metrics['v2_crystal_cos']:+.4f}")

    # ── FFN overlay comparison: analytical vs actual ──
    print(f"\n{'─' * 70}")
    print(f"  FFN Overlay: Analytical vs Actual (diagonal, top 8 PCs)")
    print(f"{'─' * 70}")

    overlay_comparison = {"layers": []}
    for layer_idx in range(cfg.n_layers):
        analytical = analytical_overlays[layer_idx]
        actual = actual_overlays[layer_idx]["overlay"]

        # Diagonal comparison
        anal_diag = np.diag(analytical[:8, :8])
        actual_diag = np.array([actual[i, i] for i in range(8)])

        # Correlation
        corr = np.corrcoef(anal_diag, actual_diag)[0, 1]

        # Off-diagonal energy fraction
        actual_full = actual_overlays[layer_idx]["overlay_full"]
        diag_energy = np.sum(np.diag(actual_full) ** 2)
        total_energy = np.sum(actual_full ** 2)
        diag_frac = diag_energy / (total_energy + 1e-10)

        overlay_comparison["layers"].append({
            "layer": layer_idx,
            "analytical_diag": anal_diag.tolist(),
            "actual_diag": actual_diag.tolist(),
            "diagonal_correlation": float(corr),
            "diagonal_energy_fraction": float(diag_frac),
        })

        print(f"  Layer {layer_idx}:")
        print(f"    Analytical: [{', '.join(f'{d:+.3f}' for d in anal_diag)}]")
        print(f"    Actual:     [{', '.join(f'{d:+.3f}' for d in actual_diag)}]")
        print(f"    Correlation: {corr:.4f}   Diag energy: {diag_frac:.1%}")

    return {
        "model_space": comparisons,
        "crystal_space": crystal_comparisons,
        "overlay_comparison": overlay_comparison,
    }


# ══════════════════════════════════════════════════════════════════════
# Phase 4: Progressive dimensionality collapse
# ══════════════════════════════════════════════════════════════════════

def phase4_progressive_collapse(
    model: MicroModel,
    input_ids: mx.array,
    crystal_emb: np.ndarray,
    eigvecs: np.ndarray,
    eigvals: np.ndarray,
) -> dict:
    """Measure the effective dimensionality of the residual stream at
    each layer boundary.

    Hypothesis: Each layer is a beta reduction (projection). The
    effective dimensionality should decrease monotonically through
    depth, converging to 2D (the comp↔sel eigenplane).

    Measures at each stage:
      1. Effective rank in crystal eigenbasis (how many PCs carry energy?)
      2. PC0+PC1 fraction (how much energy is in the 2D target subspace?)
      3. SVD spectrum of the residual stream (effective rank in model space)
      4. Projection angle: how aligned is the residual with the primary eigenplane?
      5. Per-PC energy trajectory: watch each PC's contribution through depth
      6. Attention contribution rank: what rank does each attention step add?
      7. FFN contribution rank: what rank does each FFN step add?
    """
    print("\n" + "=" * 70)
    print("  PHASE 4: Progressive Dimensionality Collapse")
    print("=" * 70)

    cfg = model.cfg
    B, L = input_ids.shape
    norms = np.linalg.norm(crystal_emb, axis=1, keepdims=True) + 1e-8
    crystal_norm = crystal_emb / norms

    # Manual forward pass capturing every intermediate
    positions = mx.arange(L)
    x = model.embed(input_ids) + model.pos_embed(positions)
    mx.eval(x)
    mask = model._get_causal_mask(L)

    stages = []

    def measure_stage(name: str, x_np: np.ndarray, contribution_np: np.ndarray = None):
        """Measure dimensionality of residual stream at this point."""
        flat = x_np.reshape(-1, cfg.d_model)  # (B*L, d_model)

        # ── Crystal eigenbasis energy distribution ──
        crystal_coords = to_crystal_coords(flat, crystal_emb, eigvecs)  # (B*L, 16)
        # Energy per PC (variance across tokens)
        pc_energy = np.var(crystal_coords, axis=0)  # (16,)
        total_crystal_energy = pc_energy.sum()
        pc_fractions = pc_energy / (total_crystal_energy + 1e-10)

        # PC0+PC1 fraction (the 2D target)
        pc01_frac = float(pc_fractions[0] + pc_fractions[1])

        # Effective rank in crystal space (how many PCs carry 90% of energy?)
        sorted_fracs = np.sort(pc_fractions)[::-1]
        cumulative = np.cumsum(sorted_fracs)
        eff_rank_90 = int(np.searchsorted(cumulative, 0.90)) + 1
        eff_rank_80 = int(np.searchsorted(cumulative, 0.80)) + 1
        eff_rank_95 = int(np.searchsorted(cumulative, 0.95)) + 1

        # Participation ratio (continuous effective rank measure)
        # PR = (Σ pᵢ)² / Σ pᵢ² — equals N for uniform, 1 for single-PC
        pr = (pc_fractions.sum() ** 2) / (np.sum(pc_fractions ** 2) + 1e-10)

        # ── Model-space SVD (full d_model dimensionality) ──
        centered = flat - flat.mean(axis=0)
        _, S_model, _ = np.linalg.svd(centered, full_matrices=False)
        model_energy = S_model ** 2
        model_total = model_energy.sum()
        model_cumulative = np.cumsum(model_energy) / (model_total + 1e-10)
        model_rank_90 = int(np.searchsorted(model_cumulative, 0.90)) + 1
        model_rank_80 = int(np.searchsorted(model_cumulative, 0.80)) + 1

        # Model-space participation ratio
        model_fracs = model_energy / (model_total + 1e-10)
        model_pr = (model_fracs.sum() ** 2) / (np.sum(model_fracs ** 2) + 1e-10)

        # ── Alignment with primary eigenplane ──
        # How much of the residual's variance lies in the PC0-PC1 plane?
        pc0_energy = pc_energy[0]
        pc1_energy = pc_energy[1]
        eigenplane_alignment = (pc0_energy + pc1_energy) / (total_crystal_energy + 1e-10)

        # ── Contribution rank (if provided) ──
        contrib_rank = None
        contrib_pc01 = None
        if contribution_np is not None:
            c_flat = contribution_np.reshape(-1, cfg.d_model)
            c_crystal = to_crystal_coords(c_flat, crystal_emb, eigvecs)
            c_energy = np.var(c_crystal, axis=0)
            c_total = c_energy.sum()
            if c_total > 1e-10:
                c_fracs = c_energy / c_total
                c_sorted = np.sort(c_fracs)[::-1]
                c_cum = np.cumsum(c_sorted)
                contrib_rank = int(np.searchsorted(c_cum, 0.90)) + 1
                contrib_pc01 = float(c_fracs[0] + c_fracs[1])

        result = {
            "stage": name,
            "pc_energy_fractions": pc_fractions[:8].tolist(),
            "pc01_fraction": pc01_frac,
            "effective_rank_90": eff_rank_90,
            "effective_rank_80": eff_rank_80,
            "effective_rank_95": eff_rank_95,
            "participation_ratio": float(pr),
            "model_rank_90": model_rank_90,
            "model_rank_80": model_rank_80,
            "model_participation_ratio": float(model_pr),
            "eigenplane_alignment": float(eigenplane_alignment),
            "contribution_rank_90": contrib_rank,
            "contribution_pc01": contrib_pc01,
        }
        stages.append(result)
        return result

    # ── Embed ──
    x_np = np.array(x)
    r = measure_stage("embed", x_np)

    # ── Through each layer ──
    for i, block in enumerate(model.blocks):
        # Attention
        normed = block.attn_norm(x)
        attn_out = block.attn(normed, mask=mask)
        x_post_attn = x + attn_out
        mx.eval(x_post_attn, attn_out)

        attn_np = np.array(attn_out)
        x_np = np.array(x_post_attn)
        measure_stage(f"L{i}_post_attn", x_np, contribution_np=attn_np)

        # FFN
        normed = block.ffn_norm(x_post_attn)
        ffn_out = block.ffn(normed)
        x = x_post_attn + ffn_out
        mx.eval(x, ffn_out)

        ffn_np = np.array(ffn_out)
        x_np = np.array(x)
        measure_stage(f"L{i}_post_ffn", x_np, contribution_np=ffn_np)

    # ── Print results ──
    print(f"\n{'─' * 90}")
    print(f"  {'Stage':<16} {'CrysRank90':<12} {'PR(crys)':<10} {'PC0+1':<10} "
          f"{'ModelRank90':<12} {'PR(model)':<10} {'Contrib':<10}")
    print(f"{'─' * 90}")

    for s in stages:
        contrib_str = ""
        if s["contribution_rank_90"] is not None:
            contrib_str = f"r={s['contribution_rank_90']}, pc01={s['contribution_pc01']:.1%}"
        print(f"  {s['stage']:<16} {s['effective_rank_90']:<12} "
              f"{s['participation_ratio']:<10.2f} {s['pc01_fraction']:<10.1%} "
              f"{s['model_rank_90']:<12} {s['model_participation_ratio']:<10.2f} "
              f"{contrib_str}")

    # ── PC energy trajectory ──
    print(f"\n{'─' * 90}")
    print(f"  Per-PC energy fractions through depth:")
    print(f"{'─' * 90}")
    pc_names_short = ["comp", "sel", "term", "rout", "fine", "rec", "dup", "anti"]
    header = f"  {'Stage':<16} " + " ".join(f"{n:>7}" for n in pc_names_short)
    print(header)
    for s in stages:
        fracs = s["pc_energy_fractions"]
        vals = " ".join(f"{f:7.1%}" for f in fracs)
        print(f"  {s['stage']:<16} {vals}")

    # ── Monotonicity check ──
    print(f"\n{'─' * 90}")
    print(f"  Dimensionality trajectory:")
    print(f"{'─' * 90}")
    ranks = [s["effective_rank_90"] for s in stages]
    prs = [s["participation_ratio"] for s in stages]
    pc01s = [s["pc01_fraction"] for s in stages]

    rank_decreasing = all(ranks[i] >= ranks[i+1] for i in range(len(ranks)-1))
    pr_decreasing = all(prs[i] >= prs[i+1] for i in range(len(prs)-1))
    pc01_increasing = all(pc01s[i] <= pc01s[i+1] for i in range(len(pc01s)-1))

    print(f"  Crystal rank (90%):  {' → '.join(str(r) for r in ranks)}")
    print(f"    Monotonically decreasing? {'YES ✓' if rank_decreasing else 'NO ✗'}")
    print(f"  Participation ratio: {' → '.join(f'{p:.2f}' for p in prs)}")
    print(f"    Monotonically decreasing? {'YES ✓' if pr_decreasing else 'NO ✗'}")
    print(f"  PC0+PC1 fraction:   {' → '.join(f'{p:.1%}' for p in pc01s)}")
    print(f"    Monotonically increasing? {'YES ✓' if pc01_increasing else 'NO ✗'}")

    # ── Composed projection analysis ──
    # What is the total projection from embed → final?
    embed_crystal = to_crystal_coords(
        np.array(stages[0].get("_raw", np.zeros((1, cfg.d_model)))).reshape(-1, cfg.d_model),
        crystal_emb, eigvecs)

    first_pc01 = stages[0]["pc01_fraction"]
    last_pc01 = stages[-1]["pc01_fraction"]
    compression = last_pc01 / (first_pc01 + 1e-10)

    print(f"\n  Projection compression: {first_pc01:.1%} → {last_pc01:.1%} "
          f"({compression:.1f}× concentration into 2D eigenplane)")

    # ── Attention vs FFN: which projects more? ──
    print(f"\n{'─' * 90}")
    print(f"  Attention vs FFN projection contribution:")
    print(f"{'─' * 90}")
    for i in range(cfg.n_layers):
        attn_stage = stages[1 + i * 2]      # L{i}_post_attn
        ffn_stage = stages[2 + i * 2]       # L{i}_post_ffn
        prev_stage = stages[i * 2]           # previous stage

        prev_pc01 = prev_stage["pc01_fraction"]
        attn_pc01 = attn_stage["pc01_fraction"]
        ffn_pc01 = ffn_stage["pc01_fraction"]

        attn_delta = attn_pc01 - prev_pc01
        ffn_delta = ffn_pc01 - attn_pc01

        prev_pr = prev_stage["participation_ratio"]
        attn_pr = attn_stage["participation_ratio"]
        ffn_pr = ffn_stage["participation_ratio"]

        attn_pr_delta = attn_pr - prev_pr
        ffn_pr_delta = ffn_pr - attn_pr

        a_contrib = attn_stage.get("contribution_pc01")
        f_contrib = ffn_stage.get("contribution_pc01")
        a_rank = attn_stage.get("contribution_rank_90")
        f_rank = ffn_stage.get("contribution_rank_90")

        print(f"  Layer {i}:")
        print(f"    PC0+1: {prev_pc01:.1%} →(attn {attn_delta:+.1%})→ {attn_pc01:.1%} "
              f"→(ffn {ffn_delta:+.1%})→ {ffn_pc01:.1%}")
        print(f"    PR:    {prev_pr:.2f} →(attn {attn_pr_delta:+.2f})→ {attn_pr:.2f} "
              f"→(ffn {ffn_pr_delta:+.2f})→ {ffn_pr:.2f}")
        if a_contrib is not None:
            print(f"    Attn contribution: rank={a_rank}, pc01={a_contrib:.1%}")
        if f_contrib is not None:
            print(f"    FFN  contribution: rank={f_rank}, pc01={f_contrib:.1%}")

    return {"stages": stages}


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    checkpoint = sys.argv[1] if len(sys.argv) > 1 else "checkpoints/micro/final"
    print(f"\n  Loading model from {checkpoint}")

    model, tokenizer = load_model(checkpoint)
    cfg = model.cfg
    crystal_emb, eigvecs, eigvals = get_crystal_basis(model)

    print(f"  Model loaded: {cfg.n_layers} layers, d={cfg.d_model}, {cfg.n_heads} heads")
    print(f"  Crystal eigenvalues (top 8): [{', '.join(f'{e:.3f}' for e in eigvals[:8])}]")

    # Prepare inputs
    input_ids, targets = prepare_inputs(tokenizer, cfg, n_examples=16)
    print(f"  Input batch: {input_ids.shape}")

    # Phase 1: Attention in crystal eigenbasis
    p1 = phase1_attention_in_crystal_basis(model, input_ids, crystal_emb, eigvecs)

    # Phase 2: Distance prior vs content
    p2 = phase2_distance_vs_content(model, input_ids)

    # Phase 3: Kernel reconstruction
    p3 = phase3_kernel_reconstruction(model, input_ids, crystal_emb, eigvecs, eigvals)

    # Phase 4: Progressive dimensionality collapse
    p4 = phase4_progressive_collapse(model, input_ids, crystal_emb, eigvecs, eigvals)

    # Save results
    out_dir = Path("results/kernel-decomposition")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Convert numpy arrays in results for JSON serialization
    def clean(obj):
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: clean(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [clean(v) for v in obj]
        return obj

    results = {
        "phase1_attention_crystal": clean(p1),
        "phase2_distance_vs_content": clean(p2),
        "phase3_kernel_reconstruction": clean(p3),
        "phase4_progressive_collapse": clean(p4),
    }

    with open(out_dir / "results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n  Results saved to {out_dir}/results.json")

    # Phase 4 summary in verdict
    if p4.get("stages"):
        rank_trajectory = [s["effective_rank_90"] for s in p4["stages"]]
        pc01_trajectory = [s["pc01_fraction"] for s in p4["stages"]]

    # ── Final verdict ──
    print("\n" + "=" * 70)
    print("  VERDICT")
    print("=" * 70)

    dist_frac = p2["summary"]["mean_distance_fraction"]
    content_rank = p2["summary"]["mean_content_rank_90"]

    final_v0_cos = p3["crystal_space"]["stages"][-1]["v0_crystal_cos"]
    final_v1_cos = p3["crystal_space"]["stages"][-1]["v1_crystal_cos"]

    print(f"\n  Distance prior explains: {dist_frac:.1%} of attention variance")
    print(f"  Content residual rank (90%): {content_rank:.0f}")
    print(f"  Kernel v0 (distance+analytical) final crystal cos: {final_v0_cos:+.4f}")
    print(f"  Kernel v1 (real_attn+analytical) final crystal cos: {final_v1_cos:+.4f}")

    if dist_frac > 0.5:
        print(f"\n  → Distance prior is DOMINANT ({dist_frac:.0%})")
        print(f"    Attention is mostly a power-law distance weighting.")
    else:
        print(f"\n  → Content is DOMINANT ({1-dist_frac:.0%})")
        print(f"    Q·K content interaction matters more than distance.")

    if content_rank < 5:
        print(f"  → Content residual is LOW-RANK (rank {content_rank:.0f})")
        print(f"    The content contribution is structured and computable.")
    elif content_rank < 15:
        print(f"  → Content residual is MODERATE-RANK (rank {content_rank:.0f})")
        print(f"    Some structure, but not trivially computable.")
    else:
        print(f"  → Content residual is HIGH-RANK (rank {content_rank:.0f})")
        print(f"    Content interaction is complex — kernel needs Q·K.")

    if final_v1_cos > 0.9:
        print(f"\n  ★ KERNEL WORKS: Analytical FFN matches forward pass (cos={final_v1_cos:.3f})")
        print(f"    The grating IS computable. Focus on computing attention next.")
    elif final_v1_cos > 0.7:
        print(f"\n  ◎ KERNEL PARTIAL: Analytical FFN captures most of it (cos={final_v1_cos:.3f})")
        print(f"    The grating captures the dominant pattern. Residual needs work.")
    else:
        print(f"\n  ✗ KERNEL FAILS: Analytical FFN misses too much (cos={final_v1_cos:.3f})")
        print(f"    The FFN does more than the diagonal overlay predicts.")

    print()


if __name__ == "__main__":
    main()
