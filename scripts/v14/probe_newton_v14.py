#!/usr/bin/env python3
"""
Probe: Is Newton's method / second-order optimization viable at scale?

Tests whether the gradient of the v14-td model (d=1280, 2500 steps of
ternary descent) aligns with the composed plate's SVD subspace.

The micro model (d=128) showed NO alignment (cos@k=27 = 0.06). If v14
shows high alignment (cos@k=27 > 0.5), Newton becomes viable at scale.

Protocol:
  1. Load v14-td checkpoint (step_002500)
  2. Capture embed → pre-head residuals on eval data
  3. Fit composed plate T via lstsq (X_out ≈ X_in @ T^T)
  4. SVD of T → rank, PR, singular values
  5. Compute gradient ∂L/∂T (plate residual gradient)
  6. Measure gradient alignment with T's SVD subspace at k=1,2,5,10,27,50,100,200
  7. Compute Hessian condition number (X_in^T @ X_in)
  8. Simulate one Newton step on the plate and measure MSE reduction

Key question: cos@k=27 — above 0.5 means Newton is viable.

Usage:
    cd verbum
    uv run python scripts/v14/probe_newton_v14.py

License: MIT
"""

from __future__ import annotations

import sys
import time
import math
from pathlib import Path

# Force CPU to avoid contention with training run on GPU
import mlx.core as mx
mx.set_default_device(mx.cpu)

import mlx.nn as nn
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from config import V14Config
from data import ShardedDataLoader
from model import V14Model
from ternary import restore_ternary, freeze_ternary_weights
from td import convert_to_delta, freeze_delta_architecture


# ══════════════════════════════════════════════════════════════════════
# § 0  Config
# ══════════════════════════════════════════════════════════════════════

CHECKPOINT = Path("checkpoints/v14-td/step_002500")
N_FIT_BATCHES = 16      # batches to fit the composed plate (≥ d for rank)
N_GRAD_BATCHES = 8      # batches for gradient / Newton analysis

# SVD subspace ranks to probe gradient alignment at
K_VALUES = [1, 2, 5, 10, 27, 50, 100, 200]


# ══════════════════════════════════════════════════════════════════════
# § 1  Model loading
# ══════════════════════════════════════════════════════════════════════

def load_model():
    """Load v14-td model from checkpoint (same pattern as probe_kernel_training.py)."""
    cfg = V14Config()
    model = V14Model(cfg)

    # Load base plates (extracted from Qwen3.6-27B)
    base_path = Path(cfg.extracted_model_path).resolve()
    print(f"   Loading base plates from {base_path}...", flush=True)
    model.load_weights(str(base_path), strict=False)
    mx.eval(model.parameters())
    restore_ternary(model)
    freeze_ternary_weights(model)

    # Convert to delta architecture
    convert_to_delta(model, include_prefixes=("shared_stride_stack",))
    freeze_delta_architecture(model)
    freeze_ternary_weights(model)

    # Load checkpoint (delta weights after 2500 steps of ternary descent)
    ckpt_model = CHECKPOINT / "model.npz"
    print(f"   Loading checkpoint from {ckpt_model}...", flush=True)
    if not ckpt_model.exists():
        raise FileNotFoundError(f"Checkpoint not found: {ckpt_model}")

    model.load_weights(str(ckpt_model), strict=False)
    mx.eval(model.parameters())
    restore_ternary(model)
    freeze_ternary_weights(model)

    return model, cfg


# ══════════════════════════════════════════════════════════════════════
# § 2  Residual capture
# ══════════════════════════════════════════════════════════════════════

def capture_residuals(model, loader, n_batches):
    """Capture embed-output and pre-head residuals.

    Returns:
        X_in  (N_tok, d)  post-embed residuals
        X_out (N_tok, d)  pre-head residuals
    """
    all_in, all_out = [], []

    for i in range(n_batches):
        ids_np, tgts_np = next(loader)
        ids  = mx.array(ids_np)
        tgts = mx.array(tgts_np)
        B, L = ids.shape
        positions = mx.arange(L)

        # Embed output: x_embed (post-embed, post-embed-norm)
        x_embed = model.embed_norm(
            model.embed(ids) + model.pos_embed(positions)
        )
        mx.eval(x_embed)

        # Full forward to populate model._last_hidden
        logits, loss = model(ids, tgts)
        mx.eval(logits, loss)
        x_out = model._last_hidden
        mx.eval(x_out)

        all_in.append( np.array(x_embed.reshape(-1, x_embed.shape[-1]), dtype=np.float32))
        all_out.append(np.array(x_out.reshape(-1, x_out.shape[-1]),   dtype=np.float32))

        if (i + 1) % 4 == 0:
            print(f"    batch {i+1}/{n_batches}", flush=True)

    X_in  = np.concatenate(all_in,  axis=0)
    X_out = np.concatenate(all_out, axis=0)
    return X_in, X_out


# ══════════════════════════════════════════════════════════════════════
# § 3  Fit composed plate
# ══════════════════════════════════════════════════════════════════════

def fit_composed_plate(X_in: np.ndarray, X_out: np.ndarray):
    """Fit T: X_out ≈ X_in @ T^T via ordinary least-squares.

    Solves: T^T = argmin ||X_in @ T^T - X_out||_F
            T^T = (X_in^T X_in)^{-1} X_in^T X_out    [normal equations]
    Uses numpy lstsq for numerical stability.

    Returns:
        T    (d, d)  composed plate (T: x_in → x_out)
        XtX  (d, d)  Gram matrix for Hessian analysis
        rank         lstsq numerical rank
    """
    # lstsq solves min||X_in @ A - X_out||, so A = T^T
    T_T, residuals, rank, sv_in = np.linalg.lstsq(X_in, X_out, rcond=None)
    T = T_T.T     # (d_out=d, d_in=d)

    # Gram matrix for Hessian condition number
    XtX = X_in.T @ X_in   # (d, d)  — used for Newton step

    print(f"    lstsq rank: {rank}")
    if len(residuals) > 0:
        print(f"    residual norm: {np.sqrt(residuals.sum()):.4f}")

    return T, XtX, rank


# ══════════════════════════════════════════════════════════════════════
# § 4  Plate spectrum analysis
# ══════════════════════════════════════════════════════════════════════

def analyze_plate_spectrum(T: np.ndarray):
    """SVD of T. Return U, S, Vt and rank/PR metrics."""
    U, S, Vt = np.linalg.svd(T, full_matrices=False)   # T = U @ diag(S) @ Vt

    total_energy = np.sum(S ** 2)
    cumulative   = np.cumsum(S ** 2) / total_energy

    rank90 = int(np.searchsorted(cumulative, 0.90)) + 1
    rank95 = int(np.searchsorted(cumulative, 0.95)) + 1
    rank99 = int(np.searchsorted(cumulative, 0.99)) + 1

    # Participation ratio: effective rank of S
    pr = (np.sum(S) ** 2) / np.sum(S ** 2)

    # σ₁ dominance
    sigma1_frac = S[0] / np.sum(S)

    print(f"\n  Composed plate (T) SVD spectrum:")
    print(f"    Shape:  {T.shape}")
    print(f"    rank90={rank90}, rank95={rank95}, rank99={rank99}, PR={pr:.1f}")
    print(f"    σ₁={sigma1_frac*100:.1f}%  (fraction of spectral weight)")
    print(f"    Top-10 singular values: {S[:10].round(4)}")

    return U, S, Vt, rank90, pr


# ══════════════════════════════════════════════════════════════════════
# § 5  Gradient of T (plate residual gradient)
# ══════════════════════════════════════════════════════════════════════

def compute_plate_gradient(model, loader, n_batches):
    """Compute ∂L/∂T by differentiating the plate loss w.r.t. T.

    We fit T once from the *fit* batches, then compute gradients on
    the *grad* batches so they are held-out.

    Strategy: compute grad_T on each batch individually (T is small
    enough to keep in memory as an mx.array leaf), then average.

    Returns:
        grad_T_mean  (d, d) numpy  — averaged gradient of T
    """
    # Build T from fit data (we need a fresh capture here for grad batches)
    all_grad_T = []

    # We'll use a simple linear model: loss(T) = CE(output_norm(X_in @ T^T) → lm_head)
    # where X_in is fresh embed data for each batch.

    for i in range(n_batches):
        ids_np, tgts_np = next(loader)
        ids  = mx.array(ids_np)
        tgts = mx.array(tgts_np)
        B, L = ids.shape
        positions = mx.arange(L)

        # Embed output (frozen)
        x_embed = model.embed_norm(
            model.embed(ids) + model.pos_embed(positions)
        )
        mx.eval(x_embed)

        # We need a current T estimate from this batch's own data
        # For gradient measurement, use model._last_hidden captured fresh
        logits_full, loss_full = model(ids, tgts)
        mx.eval(logits_full, loss_full)
        x_out_full = model._last_hidden
        mx.eval(x_out_full)

        # Fit T from this batch (small local approximation)
        x_in_np  = np.array(x_embed.reshape(-1, x_embed.shape[-1]), dtype=np.float64)
        x_out_np = np.array(x_out_full.reshape(-1, x_out_full.shape[-1]), dtype=np.float64)
        T_T_local, _, _, _ = np.linalg.lstsq(x_in_np, x_out_np, rcond=None)
        T_local = T_T_local.T.astype(np.float32)

        # Now differentiate: d/dT [CE( output_norm(X_in @ T^T) → lm_head )]
        T_mx = mx.array(T_local)
        x_embed_flat = x_embed.reshape(-1, x_embed.shape[-1])
        tgts_flat    = tgts.reshape(-1)

        def plate_loss(T_param):
            x_comp        = x_embed_flat @ T_param.T
            x_comp_normed = model.output_norm(x_comp)
            logits_comp   = model.embed.output_proj(x_comp_normed)
            logits_r      = logits_comp.reshape(-1, logits_comp.shape[-1])
            return mx.mean(nn.losses.cross_entropy(logits_r, tgts_flat))

        _, grad_T = mx.value_and_grad(plate_loss)(T_mx)
        mx.eval(grad_T)
        all_grad_T.append(np.array(grad_T, dtype=np.float32))

        if (i + 1) % 4 == 0:
            print(f"    gradient batch {i+1}/{n_batches}", flush=True)

    grad_T_mean = np.mean(np.stack(all_grad_T, axis=0), axis=0)  # (d, d)
    return grad_T_mean


# ══════════════════════════════════════════════════════════════════════
# § 6  Gradient alignment with SVD subspace
# ══════════════════════════════════════════════════════════════════════

def gradient_alignment(grad_T: np.ndarray, U: np.ndarray, Vt: np.ndarray, k_values):
    """Measure cos(∂L/∂T, P_k(∂L/∂T)) for rank-k projections.

    Two natural projections of the gradient onto T's SVD subspace:

    Left projection  (output space):  P_k^L @ grad_T   = U_k @ U_k^T @ grad_T
    Right projection (input space):   grad_T @ P_k^R   = grad_T @ Vt_k^T @ Vt_k

    We measure the cosine similarity between the full gradient and its
    rank-k projection — how much gradient energy lives in the top-k
    singular directions.

    If cos@k=27 > 0.5 → Newton on the rank-27 plate is viable.
    """
    g_flat = grad_T.flatten()
    g_norm = np.linalg.norm(g_flat)

    results = {}
    print(f"\n  Gradient alignment with T's SVD subspace:")
    print(f"    ||∂L/∂T|| = {g_norm:.6f}")
    print(f"    grad_T shape: {grad_T.shape}")

    # ── Left projection (output-space: U basis) ──
    print(f"\n    {'k':>6}  {'cos_left':>10}  {'cos_right':>11}  {'cos_both':>10}")
    print(f"    {'-'*6}  {'-'*10}  {'-'*11}  {'-'*10}")

    for k in k_values:
        if k > U.shape[1]:
            continue
        U_k  = U[:, :k]      # (d, k)
        Vt_k = Vt[:k, :]    # (k, d)

        # Left: project gradient rows into output subspace
        g_left  = U_k @ (U_k.T @ grad_T)          # (d, d)

        # Right: project gradient cols into input subspace
        g_right = (grad_T @ Vt_k.T) @ Vt_k        # (d, d)

        # Both: project rows AND cols (double projection)
        g_both  = U_k @ (U_k.T @ grad_T @ Vt_k.T) @ Vt_k  # (d, d)

        cos_l = float(np.dot(g_flat, g_left.flatten())  / (g_norm * np.linalg.norm(g_left)  + 1e-12))
        cos_r = float(np.dot(g_flat, g_right.flatten()) / (g_norm * np.linalg.norm(g_right) + 1e-12))
        cos_b = float(np.dot(g_flat, g_both.flatten())  / (g_norm * np.linalg.norm(g_both)  + 1e-12))

        results[k] = {"cos_left": cos_l, "cos_right": cos_r, "cos_both": cos_b}
        marker = "  ← KEY" if k == 27 else ""
        print(f"    {k:>6}  {cos_l:>10.4f}  {cos_r:>11.4f}  {cos_b:>10.4f}{marker}")

    return results


# ══════════════════════════════════════════════════════════════════════
# § 7  Hessian condition number (X^T X)
# ══════════════════════════════════════════════════════════════════════

def hessian_condition(XtX: np.ndarray):
    """Estimate Hessian condition number from the Gram matrix X^T X.

    The Hessian of the MSE loss ||X_in @ T^T - X_out||^2 w.r.t. T is:
        H = X_in^T @ X_in  (same for every row of T)

    The condition number κ = σ_max / σ_min determines how many Newton
    steps are needed and how much preconditioning helps.

    κ < 100:   well-conditioned, Newton converges in <10 steps
    κ < 1000:  moderately ill, 2nd-order still helps vs GD
    κ > 1000:  ill-conditioned, Newton without damping will diverge
    """
    sv_H = np.linalg.svd(XtX, compute_uv=False)
    kappa = float(sv_H[0]) / float(sv_H[-1] + 1e-30)
    rank_H = np.sum(sv_H > sv_H[0] * 1e-6)

    print(f"\n  Hessian (X^T X) analysis:")
    print(f"    d={XtX.shape[0]}, rank={rank_H}")
    print(f"    σ_max={sv_H[0]:.4e}, σ_min={sv_H[-1]:.4e}")
    print(f"    Condition number κ = {kappa:.4e}")
    if kappa < 1e2:
        regime = "well-conditioned → Newton converges fast"
    elif kappa < 1e3:
        regime = "moderate ill-conditioning → Newton helps vs GD"
    elif kappa < 1e6:
        regime = "ill-conditioned → needs damping / regularization"
    else:
        regime = "severely ill-conditioned → Newton diverges without PCG"
    print(f"    Regime: {regime}")
    print(f"    Top-10 Hessian singular values: {sv_H[:10].round(4)}")

    return float(kappa), sv_H


# ══════════════════════════════════════════════════════════════════════
# § 8  Newton step simulation
# ══════════════════════════════════════════════════════════════════════

def simulate_newton_step(
    X_in:  np.ndarray,
    X_out: np.ndarray,
    T:     np.ndarray,
    XtX:   np.ndarray,
    sv_H:  np.ndarray,
    grad_T: np.ndarray,
    damping_factor: float = 1e-3,
):
    """Simulate one Newton step on the composed plate and measure MSE reduction.

    The MSE loss is:
        L(T) = (1/N) ||X_in @ T^T - X_out||_F^2

    Gradient:
        ∂L/∂T = (2/N) (T @ X_in^T - X_out^T) @ X_in
              = (2/N) (X_in @ T^T - X_out)^T @ X_in   [reshaped]

    The Newton step solves:  H @ ΔT^T = -∂L/∂T^T  where H = X^T X.
    Equivalently for each row of T^T:
        ΔT^T[:, j] = -H^{-1} @ ∂L/∂T^T[:, j]

    With damping λ: H_λ = H + λ * σ_max * I  → (H_λ)^{-1} @ g

    We also try the closed-form Newton optimum for comparison:
        T* = X_out^T @ X_in @ (X_in^T @ X_in)^{-1}  [this IS lstsq!]
    So the "perfect Newton step" from the current T just jumps to T*.
    The question is: how much does one damped Newton step reduce MSE
    vs one gradient step of the same effective learning rate?
    """
    N = X_in.shape[0]

    # ── Current MSE ──
    X_hat     = X_in @ T.T   # (N, d)
    residual  = X_hat - X_out
    mse_init  = float(np.mean(residual ** 2))

    # ── Gradient of MSE w.r.t. T ──
    # ∂L/∂T = (2/N) (X_hat - X_out)^T @ X_in  → same as -grad but in MSE sense
    grad_T_mse = (2.0 / N) * (X_hat - X_out).T @ X_in   # (d, d): row = ∂L/∂T[row_of_T]

    grad_norm_mse = np.linalg.norm(grad_T_mse)

    # ── Damped Newton step: solve (XtX + λ σ_max I) ΔT^T = -∂L/∂T^T ──
    lambda_damp = damping_factor * float(sv_H[0])  # Levenberg-Marquardt damping
    H_damped    = XtX + lambda_damp * np.eye(XtX.shape[0])  # (d, d)

    # Solve for each column of T simultaneously via lstsq
    # grad_T_mse.T is (d, d) — columns = grad w.r.t. each row of T
    delta_T_T, _, _, _ = np.linalg.lstsq(H_damped, -grad_T_mse.T, rcond=None)
    delta_T = delta_T_T.T   # (d, d) — same shape as T

    T_newton = T + delta_T

    X_hat_newton = X_in @ T_newton.T
    mse_newton   = float(np.mean((X_hat_newton - X_out) ** 2))

    # ── Gradient descent step for comparison (lr = 1 / σ_max for stability) ──
    lr_gd = 2.0 / (float(sv_H[0]) + float(sv_H[-1]) + 1e-30)
    T_gd  = T - lr_gd * grad_T_mse
    mse_gd = float(np.mean((X_in @ T_gd.T - X_out) ** 2))

    # ── Perfect lstsq baseline (Newton converges in 1 step for MSE) ──
    T_T_star, _, _, _ = np.linalg.lstsq(X_in, X_out, rcond=None)
    T_star = T_T_star.T
    mse_star = float(np.mean((X_in @ T_star.T - X_out) ** 2))

    # ── How much gradient energy is in the SVD subspace vs Newton step ──
    step_norm_newton = np.linalg.norm(delta_T)
    step_norm_gd     = np.linalg.norm(-lr_gd * grad_T_mse)

    print(f"\n  Newton step simulation (MSE loss, damping={damping_factor:.0e}):")
    print(f"    MSE (current T):     {mse_init:.6f}")
    print(f"    MSE after Newton:    {mse_newton:.6f}   reduction={1-mse_newton/mse_init:.4f}  ({(1-mse_newton/mse_init)*100:.2f}%)")
    print(f"    MSE after GD step:   {mse_gd:.6f}   reduction={1-mse_gd/mse_init:.4f}  ({(1-mse_gd/mse_init)*100:.2f}%)")
    print(f"    MSE lstsq optimum:   {mse_star:.6f}   (lower bound)")
    print(f"    ||ΔT Newton||:       {step_norm_newton:.6f}")
    print(f"    ||ΔT GD||:           {step_norm_gd:.6f}")
    print(f"    ||∂L/∂T (MSE)||:     {grad_norm_mse:.6f}")
    newton_ratio = (mse_init - mse_newton) / (mse_init - mse_gd + 1e-30)
    print(f"    Newton / GD MSE reduction ratio: {newton_ratio:.2f}×")

    return {
        "mse_init":    mse_init,
        "mse_newton":  mse_newton,
        "mse_gd":      mse_gd,
        "mse_star":    mse_star,
        "mse_reduction_newton": float(1 - mse_newton / mse_init),
        "mse_reduction_gd":     float(1 - mse_gd     / mse_init),
        "newton_vs_gd_ratio":   float(newton_ratio),
    }


# ══════════════════════════════════════════════════════════════════════
# § 9  Main
# ══════════════════════════════════════════════════════════════════════

def main():
    t_start = time.time()
    print("=" * 70)
    print("  Newton / Second-Order Optimization Viability Probe")
    print(f"  Checkpoint: {CHECKPOINT}")
    print(f"  d_model=1280, N_FIT={N_FIT_BATCHES}, N_GRAD={N_GRAD_BATCHES}")
    print("=" * 70)

    # ── 1. Load model ──────────────────────────────────────────────────
    print("\n1. Loading v14-td model...", flush=True)
    model, cfg = load_model()
    d = cfg.d_model
    print(f"   d_model={d}, d_ff={cfg.d_ff}, n_heads={cfg.n_heads}")

    # ── 2. Data loader (eval shards 54–59) ────────────────────────────
    loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=1,
        seq_len=cfg.seq_len,
        shard_start=cfg.n_train_shards,         # 54
        shard_end=cfg.n_train_shards + cfg.n_eval_shards,  # 60
        seed=1337,
    )

    # ── 3. Capture residuals (fit set) ────────────────────────────────
    print(f"\n2. Capturing residuals ({N_FIT_BATCHES} batches for plate fit)...",
          flush=True)
    X_in, X_out = capture_residuals(model, loader, N_FIT_BATCHES)
    N_tok = X_in.shape[0]
    print(f"   Captured {N_tok:,} tokens × d={d}")
    print(f"   X_in  shape: {X_in.shape},  dtype: {X_in.dtype}")
    print(f"   X_out shape: {X_out.shape}, dtype: {X_out.dtype}")

    # ── 4. Fit composed plate T ───────────────────────────────────────
    print(f"\n3. Fitting composed plate T (lstsq)...", flush=True)
    t0 = time.time()
    T, XtX, lstsq_rank = fit_composed_plate(X_in, X_out)
    print(f"   T shape: {T.shape}, fit time: {time.time()-t0:.1f}s")

    # ── 5. Plate SVD spectrum ─────────────────────────────────────────
    print(f"\n4. Analyzing plate SVD spectrum...", flush=True)
    U, S, Vt, rank90, pr = analyze_plate_spectrum(T)

    # ── 6. Hessian condition number ───────────────────────────────────
    print(f"\n5. Hessian condition number...", flush=True)
    kappa, sv_H = hessian_condition(XtX)

    # ── 7. Gradient of T (plate gradient, on held-out batches) ────────
    print(f"\n6. Computing ∂L/∂T on held-out batches ({N_GRAD_BATCHES})...",
          flush=True)
    grad_T = compute_plate_gradient(model, loader, N_GRAD_BATCHES)
    grad_norm = np.linalg.norm(grad_T)
    grad_rank = int(np.linalg.matrix_rank(grad_T, tol=grad_norm * 0.01))
    print(f"   ||∂L/∂T|| = {grad_norm:.6f}")
    print(f"   ∂L/∂T effective rank (1% tol): {grad_rank}")

    # ── 8. Gradient alignment with SVD subspace ───────────────────────
    print(f"\n7. Measuring gradient alignment with SVD subspace...")
    align = gradient_alignment(grad_T, U, Vt, K_VALUES)

    # ── 9. Newton step simulation ─────────────────────────────────────
    print(f"\n8. Simulating Newton step on the plate...")
    newton = simulate_newton_step(X_in, X_out, T, XtX, sv_H, grad_T)

    # ── 10. Summary ───────────────────────────────────────────────────
    elapsed = time.time() - t_start
    cos27 = align.get(27, {}).get("cos_left", float("nan"))
    cos27_right = align.get(27, {}).get("cos_right", float("nan"))
    cos27_both  = align.get(27, {}).get("cos_both",  float("nan"))

    print("\n" + "=" * 70)
    print("  SUMMARY — Newton Viability at Scale (v14-td, step_002500)")
    print("=" * 70)
    print(f"  Checkpoint:          {CHECKPOINT}")
    print(f"  d_model:             {d}")
    print(f"  N_fit_tokens:        {N_tok:,}")
    print()
    print(f"  ── Plate spectrum ──────────────────────────────")
    print(f"  lstsq rank:          {lstsq_rank}")
    print(f"  SVD rank90:          {rank90}")
    print(f"  PR (eff. rank):      {pr:.1f}")
    print(f"  σ₁/Σσ:               {S[0]/np.sum(S)*100:.1f}%")
    print()
    print(f"  ── Hessian ─────────────────────────────────────")
    print(f"  Condition number κ:  {kappa:.4e}")
    print()
    print(f"  ── Gradient ────────────────────────────────────")
    print(f"  ||∂L/∂T||:           {grad_norm:.6f}")
    print(f"  ∂L/∂T rank (1%):     {grad_rank}")
    print()
    print(f"  ── Gradient alignment (cos with rank-k subspace) ──")
    for k in K_VALUES:
        if k in align:
            a = align[k]
            marker = "  ← KEY" if k == 27 else ""
            print(f"  cos@k={k:<4}: left={a['cos_left']:.4f}  "
                  f"right={a['cos_right']:.4f}  "
                  f"both={a['cos_both']:.4f}{marker}")
    print()
    print(f"  ── Newton step ─────────────────────────────────")
    print(f"  MSE init:            {newton['mse_init']:.6f}")
    print(f"  MSE after Newton:    {newton['mse_newton']:.6f}  "
          f"({newton['mse_reduction_newton']*100:.2f}% reduction)")
    print(f"  MSE after GD:        {newton['mse_gd']:.6f}  "
          f"({newton['mse_reduction_gd']*100:.2f}% reduction)")
    print(f"  MSE lstsq optimum:   {newton['mse_star']:.6f}")
    print(f"  Newton / GD ratio:   {newton['newton_vs_gd_ratio']:.2f}×")
    print()

    # Verdict
    viable = cos27 > 0.5
    print("  ── Verdict ─────────────────────────────────────")
    print(f"  cos@k=27 (left):     {cos27:.4f}  (threshold = 0.50)")
    if viable:
        print("  ✅ NEWTON VIABLE: gradient aligns with rank-27 SVD subspace")
        print("     → Second-order optimization on the plate is warranted.")
        print("     → A rank-27 Newton step captures most gradient energy.")
        print("     → Expected speedup over GD: ~{:.1f}× per step.".format(
              newton['newton_vs_gd_ratio']))
    else:
        print("  ❌ NEWTON NOT VIABLE at rank-27")
        if cos27 > 0.2:
            print("     → Weak alignment — gradient energy spread over many directions.")
            print("     → Consider higher-rank approximation or different preconditioning.")
        else:
            print("     → Near-zero alignment — gradient is essentially isotropic.")
            print("     → The micro-model result (cos=0.06) reproduces at scale.")
            print("     → Newton requires full-rank Hessian inversion (expensive).")

    print(f"\n  Total wall time: {elapsed:.1f}s")
    print("=" * 70)

    # ── Save results ──────────────────────────────────────────────────
    import json
    out_dir = Path("results/newton-probe-v14")
    out_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        str(out_dir / "plate.npz"),
        T=T, U=U, S=S, Vt=Vt, grad_T=grad_T
    )
    results_json = {
        "checkpoint":          str(CHECKPOINT),
        "d_model":             d,
        "n_fit_tokens":        int(N_tok),
        "lstsq_rank":          int(lstsq_rank),
        "rank90":              int(rank90),
        "pr":                  float(pr),
        "kappa":               float(kappa),
        "grad_norm":           float(grad_norm),
        "grad_rank":           int(grad_rank),
        "alignment":           {str(k): v for k, v in align.items()},
        "newton":              newton,
        "viable":              bool(viable),
    }
    with open(str(out_dir / "results.json"), "w") as f:
        json.dump(results_json, f, indent=2)
    print(f"\n  Results saved → {out_dir}/")


if __name__ == "__main__":
    main()
