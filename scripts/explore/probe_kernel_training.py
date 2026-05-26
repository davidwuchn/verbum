#!/usr/bin/env python3
"""
Probe: Can we train through the composed plate?

Tests whether the linearized composed transform (embed→pre-head)
captures enough of the model's computation for training gradients.

Protocol:
  1. Load v14 student model from checkpoint
  2. Run forward on eval data, capture residuals at embed and pre-head
  3. Fit least-squares composed plate T: x_out ≈ T @ x_embed
  4. Compare: logits via T vs full model logits
  5. Compare: gradient direction through T vs through full model
  6. Measure composed plate rank (SVD)

If the gradient through the composed plate points in a similar
direction to the full model gradient, we can train topology (TD)
through the composed plate at ~300× speedup.

Usage:
    cd verbum
    uv run python scripts/explore/probe_kernel_training.py

License: MIT
"""

from __future__ import annotations

import sys
import time
import math
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "v14"))

from config import V14Config
from data import ShardedDataLoader
from model import V14Model
from ternary import restore_ternary, freeze_ternary_weights
from td import convert_to_delta, collect_delta_params, freeze_delta_architecture


CHECKPOINT = Path("checkpoints/v14-kd/step_001000")
N_FIT_BATCHES = 20     # batches to fit the composed plate
N_TEST_BATCHES = 10    # batches to test on (held out from fit)
N_GRAD_BATCHES = 5     # batches for gradient comparison


def load_model():
    """Load v14 model from checkpoint."""
    cfg = V14Config()
    model = V14Model(cfg)

    # Load base plates
    base_path = Path(cfg.extracted_model_path).resolve()
    model.load_weights(str(base_path), strict=False)
    mx.eval(model.parameters())
    restore_ternary(model)
    freeze_ternary_weights(model)

    # Convert to delta and load checkpoint
    convert_to_delta(model, include_prefixes=("shared_stride_stack",))
    freeze_delta_architecture(model)
    freeze_ternary_weights(model)

    if CHECKPOINT.exists():
        model.load_weights(str(CHECKPOINT / "model.npz"), strict=False)
        mx.eval(model.parameters())
        restore_ternary(model)
        freeze_ternary_weights(model)

    return model, cfg


def capture_residuals(model, loader, n_batches):
    """Run forward pass, capture embed output and pre-head output.

    Returns:
        x_embeds: (total_tokens, d_model) — post-embed residuals
        x_outs:   (total_tokens, d_model) — pre-head residuals
        tokens:   (total_tokens,) — token IDs for loss computation
        targets:  (total_tokens,) — target token IDs
    """
    all_embeds = []
    all_outs = []
    all_tokens = []
    all_targets = []

    for i in range(n_batches):
        ids_np, tgts_np = next(loader)
        ids = mx.array(ids_np)
        tgts = mx.array(tgts_np)

        # Run forward, capture embed and pre-head
        B, L = ids.shape
        positions = mx.arange(L)
        x_embed = model.embed_norm(model.embed(ids) + model.pos_embed(positions))

        # Full forward to get x_out (the _last_hidden state)
        logits, loss = model(ids, tgts)
        mx.eval(logits, loss)
        x_out = model._last_hidden  # set during forward
        mx.eval(x_out)

        # Flatten batch dimension
        all_embeds.append(x_embed.reshape(-1, x_embed.shape[-1]))
        all_outs.append(x_out.reshape(-1, x_out.shape[-1]))
        all_tokens.append(ids.reshape(-1))
        all_targets.append(tgts.reshape(-1))

        if (i + 1) % 5 == 0:
            print(f"    Captured {i+1}/{n_batches} batches", flush=True)

    x_embeds = mx.concatenate(all_embeds, axis=0)
    x_outs = mx.concatenate(all_outs, axis=0)
    tokens = mx.concatenate(all_tokens, axis=0)
    targets = mx.concatenate(all_targets, axis=0)
    mx.eval(x_embeds, x_outs, tokens, targets)
    return x_embeds, x_outs, tokens, targets


def fit_composed_plate(x_in, x_out):
    """Fit T such that x_out ≈ T @ x_in via least-squares.

    T = x_out^T @ x_in @ (x_in^T @ x_in)^{-1}
    Or equivalently: T = (x_in^T x_in)^{-1} x_in^T x_out  (for T: x_out = x_in @ T^T)

    We solve: x_out = x_in @ T^T  →  T^T = (x_in^T x_in)^{-1} x_in^T x_out
    """
    # Use numpy for the lstsq solve (more numerically stable)
    x_in_np = np.array(x_in, dtype=np.float32)
    x_out_np = np.array(x_out, dtype=np.float32)

    # x_out = x_in @ T^T  →  solve for T^T
    # lstsq: find T^T that minimizes ||x_in @ T^T - x_out||
    T_T, residuals, rank, sv = np.linalg.lstsq(x_in_np, x_out_np, rcond=None)
    T = T_T.T  # (d_out, d_in)

    print(f"    lstsq rank: {rank}")
    print(f"    residual norm: {np.sqrt(residuals.sum()) if len(residuals) > 0 else 'N/A'}")

    return T, sv


def analyze_plate(T, sv):
    """Analyze the composed plate: rank, spectrum, phi."""
    d = T.shape[0]

    # SVD of T
    U, S, Vt = np.linalg.svd(T)

    # Rank metrics
    total_energy = np.sum(S ** 2)
    cumulative = np.cumsum(S ** 2) / total_energy

    rank90 = np.searchsorted(cumulative, 0.90) + 1
    rank95 = np.searchsorted(cumulative, 0.95) + 1
    rank99 = np.searchsorted(cumulative, 0.99) + 1

    # Participation ratio
    pr = (np.sum(S) ** 2) / np.sum(S ** 2)

    # σ₁ dominance
    sigma1_frac = S[0] / np.sum(S)

    print(f"\n  Composed plate spectrum:")
    print(f"    Shape: {T.shape}")
    print(f"    rank90={rank90}, rank95={rank95}, rank99={rank99}")
    print(f"    PR={pr:.1f}, σ₁={sigma1_frac*100:.1f}%")
    print(f"    Top 10 singular values: {S[:10].round(3)}")

    return S, rank90


def test_composed_accuracy(model, T_np, loader, n_batches, cfg):
    """Compare full model logits vs composed plate logits."""
    T_mx = mx.array(T_np.astype(np.float32))

    logit_corrs = []
    ce_fulls = []
    ce_composeds = []
    top1_agrees = []
    per_dim_corrs = []

    for i in range(n_batches):
        ids_np, tgts_np = next(loader)
        ids = mx.array(ids_np)
        tgts = mx.array(tgts_np)
        B, L = ids.shape

        # Full model forward
        logits_full, loss_full = model(ids, tgts)
        x_out_full = model._last_hidden
        mx.eval(logits_full, loss_full, x_out_full)

        # Composed plate forward
        positions = mx.arange(L)
        x_embed = model.embed_norm(model.embed(ids) + model.pos_embed(positions))
        mx.eval(x_embed)

        # x_composed = x_embed @ T^T
        x_composed = x_embed @ T_mx.T
        x_composed_normed = model.output_norm(x_composed)
        logits_composed = model.embed.output_proj(x_composed_normed)
        mx.eval(logits_composed)

        # CE loss for composed
        logits_flat = logits_composed.reshape(-1, logits_composed.shape[-1])
        tgts_flat = tgts.reshape(-1)
        ce_composed = mx.mean(nn.losses.cross_entropy(logits_flat, tgts_flat))
        mx.eval(ce_composed)

        ce_fulls.append(float(loss_full.item()) if loss_full is not None else float('nan'))
        ce_composeds.append(float(ce_composed.item()))

        # Per-position logit correlation (flatten to 2D)
        lf = np.array(logits_full.reshape(-1, logits_full.shape[-1]))
        lc = np.array(logits_composed.reshape(-1, logits_composed.shape[-1]))

        # Overall correlation (sample 1000 positions to keep fast)
        n_pos = min(1000, lf.shape[0])
        idx = np.random.choice(lf.shape[0], n_pos, replace=False)
        lf_sample = lf[idx]
        lc_sample = lc[idx]

        # Per-position cosine similarity
        norms_f = np.linalg.norm(lf_sample, axis=1, keepdims=True) + 1e-10
        norms_c = np.linalg.norm(lc_sample, axis=1, keepdims=True) + 1e-10
        cos_sim = np.sum((lf_sample / norms_f) * (lc_sample / norms_c), axis=1)
        logit_corrs.append(np.mean(cos_sim))

        # Per-dim correlation on hidden states
        hf = np.array(x_out_full.reshape(-1, x_out_full.shape[-1]))
        hc = np.array(x_composed.reshape(-1, x_composed.shape[-1]))
        # Sample dims
        n_sample = min(500, hf.shape[0])
        idx_h = np.random.choice(hf.shape[0], n_sample, replace=False)
        dim_corrs = []
        for d in range(0, hf.shape[1], 40):  # sample every 40th dim
            r = np.corrcoef(hf[idx_h, d], hc[idx_h, d])[0, 1]
            if not np.isnan(r):
                dim_corrs.append(r)
        per_dim_corrs.append(np.mean(dim_corrs))

        # Top-1 agreement
        top1_full = np.argmax(lf, axis=1)
        top1_comp = np.argmax(lc, axis=1)
        top1_agrees.append(np.mean(top1_full == top1_comp))

    print(f"\n  Composed plate vs full model ({n_batches} batches):")
    print(f"    Logit cosine sim:   {np.mean(logit_corrs):.4f} ± {np.std(logit_corrs):.4f}")
    print(f"    Hidden per-dim corr: {np.mean(per_dim_corrs):.4f} ± {np.std(per_dim_corrs):.4f}")
    print(f"    Top-1 agreement:    {np.mean(top1_agrees)*100:.1f}%")
    print(f"    CE full model:      {np.mean(ce_fulls):.4f}")
    print(f"    CE composed:        {np.mean(ce_composeds):.4f}")
    print(f"    CE difference:      {np.mean(ce_composeds) - np.mean(ce_fulls):+.4f}")

    return {
        "logit_cos_sim": float(np.mean(logit_corrs)),
        "per_dim_corr": float(np.mean(per_dim_corrs)),
        "top1_agreement": float(np.mean(top1_agrees)),
        "ce_full": float(np.mean(ce_fulls)),
        "ce_composed": float(np.mean(ce_composeds)),
    }


def compare_gradients(model, T_np, loader, n_batches, cfg):
    """Compare gradient direction: full model vs composed plate.

    The key question: does ∂L/∂T_composed point in the same direction
    as the full model's gradient projected into the same space?

    We compare:
    - ∂L/∂x_embed from full model vs from composed plate
      (this is the gradient the embedding layer sees)
    - ∂L/∂T (the composed plate gradient itself)
    """
    T_mx = mx.array(T_np.astype(np.float32))

    embed_grad_cosines = []
    embed_grad_magnitudes = []

    for i in range(n_batches):
        ids_np, tgts_np = next(loader)
        ids = mx.array(ids_np)
        tgts = mx.array(tgts_np)
        B, L = ids.shape

        # ── Full model gradient w.r.t. x_embed ──
        positions = mx.arange(L)

        def full_forward(x_embed):
            """Forward through full model from x_embed to loss."""
            # We need to inject x_embed into the model's forward path
            # This is tricky because model.forward() starts from tokens
            # Instead, we'll capture the gradient at the embed level
            # by computing loss and getting grad w.r.t. a parameter
            pass

        # Simpler approach: compare gradient w.r.t. the OUTPUT NORM weights
        # This is a parameter that appears in both computation paths

        # Full model: loss w.r.t. output_norm weight
        def loss_full_fn(model, ids, tgts):
            logits, _ = model(ids, tgts)
            x_out = model._last_hidden
            logits_r = logits.reshape(-1, logits.shape[-1])
            tgts_r = tgts.reshape(-1)
            return mx.mean(nn.losses.cross_entropy(logits_r, tgts_r))

        loss_full, grads_full = nn.value_and_grad(model, loss_full_fn)(model, ids, tgts)
        mx.eval(loss_full, grads_full)

        # Get gradient of output_norm.weight from full model
        grad_norm_full = None
        from mlx.utils import tree_flatten
        for name, param in tree_flatten(grads_full):
            if "output_norm.weight" in name:
                grad_norm_full = param
                break

        # Composed plate: same loss but through T
        x_embed = model.embed_norm(model.embed(ids) + model.pos_embed(positions))
        mx.eval(x_embed)

        def loss_composed_fn(T_param):
            x_comp = x_embed @ T_param.T
            x_comp_normed = model.output_norm(x_comp)
            logits_comp = model.embed.output_proj(x_comp_normed)
            logits_r = logits_comp.reshape(-1, logits_comp.shape[-1])
            tgts_r = tgts.reshape(-1)
            return mx.mean(nn.losses.cross_entropy(logits_r, tgts_r))

        loss_comp, grad_T = mx.value_and_grad(loss_composed_fn)(T_mx)
        mx.eval(loss_comp, grad_T)

        # Compare: gradient of T itself (this is what we'd use for training)
        # Flatten gradient and compute cosine similarity with... what?
        # We need to compare gradient DIRECTIONS, not magnitudes.
        #
        # The fairest comparison: both paths produce ∂L/∂x_embed.
        # Full model: ∂L/∂x_embed (through 238 matmuls)
        # Composed:   ∂L/∂x_embed = T^T @ ∂L/∂x_out (through 1 matmul)
        #
        # But getting ∂L/∂x_embed from the full model requires
        # making x_embed a leaf variable in the graph.

        # Alternative comparison: use output_norm gradient as a proxy.
        # Both paths end with output_norm → embed.output_proj → CE.
        # The gradient of output_norm.weight tells us how the pre-head
        # representation should change — same final layers, different paths to get there.

        if grad_norm_full is not None:
            # Get composed path gradient of output_norm
            # Need to redo with output_norm as the gradient target
            def loss_composed_with_norm(norm_weight):
                x_comp = x_embed @ T_mx.T
                # Manual RMSNorm with the given weight
                rms = mx.sqrt(mx.mean(x_comp * x_comp, axis=-1, keepdims=True) + 1e-6)
                x_comp_normed = (x_comp / rms) * norm_weight
                logits_comp = model.embed.output_proj(x_comp_normed)
                logits_r = logits_comp.reshape(-1, logits_comp.shape[-1])
                tgts_r = tgts.reshape(-1)
                return mx.mean(nn.losses.cross_entropy(logits_r, tgts_r))

            norm_w = model.output_norm.weight
            _, grad_norm_comp = mx.value_and_grad(loss_composed_with_norm)(norm_w)
            mx.eval(grad_norm_comp)

            # Cosine similarity between the two norm gradients
            gf = grad_norm_full.reshape(-1)
            gc = grad_norm_comp.reshape(-1)
            cos = float(mx.sum(gf * gc).item()) / (
                float(mx.sqrt(mx.sum(gf * gf)).item()) *
                float(mx.sqrt(mx.sum(gc * gc)).item()) + 1e-10
            )
            embed_grad_cosines.append(cos)

            # Magnitude ratio
            mag_f = float(mx.sqrt(mx.sum(gf * gf)).item())
            mag_c = float(mx.sqrt(mx.sum(gc * gc)).item())
            embed_grad_magnitudes.append(mag_c / (mag_f + 1e-10))

        if (i + 1) % 2 == 0:
            print(f"    Gradient batch {i+1}/{n_batches}: "
                  f"cos={embed_grad_cosines[-1]:.4f}, "
                  f"mag_ratio={embed_grad_magnitudes[-1]:.4f}")

    # Also report gradient of T itself
    grad_T_np = np.array(grad_T)
    grad_T_norm = np.linalg.norm(grad_T_np)
    grad_T_rank = np.linalg.matrix_rank(grad_T_np, tol=grad_T_norm * 0.01)

    print(f"\n  Gradient comparison ({n_batches} batches):")
    print(f"    output_norm grad cosine:  {np.mean(embed_grad_cosines):.4f} ± {np.std(embed_grad_cosines):.4f}")
    print(f"    output_norm mag ratio:    {np.mean(embed_grad_magnitudes):.4f}")
    print(f"    ∂L/∂T norm:              {grad_T_norm:.6f}")
    print(f"    ∂L/∂T effective rank:    {grad_T_rank}")

    return {
        "grad_cosine": float(np.mean(embed_grad_cosines)),
        "grad_mag_ratio": float(np.mean(embed_grad_magnitudes)),
        "grad_T_norm": float(grad_T_norm),
        "grad_T_rank": int(grad_T_rank),
    }


def main():
    print("=" * 70)
    print("  Kernel Training Probe")
    print(f"  Checkpoint: {CHECKPOINT}")
    print("=" * 70)

    # ── Load model ──
    print("\n1. Loading model...", flush=True)
    model, cfg = load_model()
    print(f"   Model loaded. d_model={cfg.d_model}")

    # ── Data loader (eval shards) ──
    loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=1,
        seq_len=cfg.seq_len,
        shard_start=cfg.n_train_shards,  # eval shards
        shard_end=cfg.n_train_shards + cfg.n_eval_shards,
        seed=42,
    )

    # ── Phase 1: Capture residuals for fitting ──
    print(f"\n2. Capturing residuals ({N_FIT_BATCHES} batches for fit)...", flush=True)
    x_embeds, x_outs, tokens, targets = capture_residuals(
        model, loader, N_FIT_BATCHES
    )
    n_tokens = x_embeds.shape[0]
    print(f"   Captured {n_tokens:,} tokens, d={x_embeds.shape[1]}")

    # ── Phase 2: Fit composed plate ──
    print(f"\n3. Fitting composed plate...", flush=True)
    t0 = time.time()
    T, sv = fit_composed_plate(x_embeds, x_outs)
    print(f"   Fit in {time.time()-t0:.1f}s")

    # ── Phase 3: Analyze plate spectrum ──
    S, rank90 = analyze_plate(T, sv)

    # ── Phase 4: Test accuracy on held-out data ──
    print(f"\n4. Testing composed plate accuracy ({N_TEST_BATCHES} batches)...", flush=True)
    accuracy = test_composed_accuracy(model, T, loader, N_TEST_BATCHES, cfg)

    # ── Phase 5: Compare gradients ──
    print(f"\n5. Comparing gradient directions ({N_GRAD_BATCHES} batches)...", flush=True)
    grad_results = compare_gradients(model, T, loader, N_GRAD_BATCHES, cfg)

    # ── Summary ──
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  Composed plate rank90: {rank90}")
    print(f"  Logit cosine sim:      {accuracy['logit_cos_sim']:.4f}")
    print(f"  Hidden per-dim corr:   {accuracy['per_dim_corr']:.4f}")
    print(f"  Top-1 agreement:       {accuracy['top1_agreement']*100:.1f}%")
    print(f"  CE full:               {accuracy['ce_full']:.4f}")
    print(f"  CE composed:           {accuracy['ce_composed']:.4f}")
    print(f"  Gradient cosine:       {grad_results['grad_cosine']:.4f}")
    print(f"  ∂L/∂T rank:           {grad_results['grad_T_rank']}")
    print()

    viable = grad_results['grad_cosine'] > 0.5
    print(f"  VIABILITY: {'✅ VIABLE' if viable else '❌ NOT VIABLE'}")
    print(f"  Gradient cosine > 0.5 means composed plate gradient")
    print(f"  points in a similar enough direction for TD training.")
    if viable:
        print(f"  → Kernel training is worth pursuing!")
        print(f"  → Expected speedup: ~{238/3:.0f}× (238 matmuls → ~3 matmuls)")
    else:
        print(f"  → The linearized composed plate loses too much information.")
        print(f"  → Need nonlinear kernel or per-zone composition instead.")

    # Save results
    out_dir = Path("results/kernel-training-probe")
    out_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        str(out_dir / "composed_plate.npz"),
        T=T, S=S,
    )

    import json
    results = {**accuracy, **grad_results, "rank90": int(rank90)}
    with open(str(out_dir / "results.json"), "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to {out_dir}/")


if __name__ == "__main__":
    main()
