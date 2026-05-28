#!/usr/bin/env python3
"""
M-space vs Gradient-Heat Scoring — Micro Model Experiment.

The core question: does scoring topology flips by their effect on the
attention kernel M = W_q^T @ W_k (M-space) produce different and better
candidates than scoring by gradient magnitude (heat)?

Protocol:
  1. Load trained float32 micro model (converged, CE ~0.38)
  2. Sign-quantize Q and K to ternary {-1, +1} (no zeros)
  3. For each attention layer:
     a. M_target  = W_q_float^T @ W_k_float   (the ideal gem)
     b. M_current = W_q_ternary^T @ W_k_ternary (the rough stone)
     c. M-space score: how much does each flip move M toward M_target?
     d. Gradient score: routing component of ∂L/∂W (TD's signal)
  4. Rank-correlate the two scores (Spearman)
  5. Verify: flip top candidates from each, measure actual loss delta
  6. Report which scoring better predicts real improvement

Key formula (derived analytically):
  For flip at W_q[h, i]:
    ΔM = -2 * W_q[h,i] * e_i ⊗ W_k[h,:]   (rank-1 update)
    M-score = -4 * W_q[h,i] * dot(R[i,:], W_k[h,:])
    where R = M_target_norm - M_current_norm  (residual in M-space)

  For flip at W_k[h, j]:
    ΔM = -2 * W_k[h,j] * W_q[:,h] ⊗ e_j     (rank-1 update)
    M-score = -4 * W_k[h,j] * dot(R[:,j], W_q[h,:])
    where W_q[h,:] is used via W_q^T[:,h]

License: MIT
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import mlx.core as mx
import mlx.nn as nn

sys.path.insert(0, str(Path(__file__).parent))
from micro_model import MicroModel, MicroConfig


# ══════════════════════════════════════════════════════════════════════
# Data loading (reuse from train_micro)
# ══════════════════════════════════════════════════════════════════════

def load_compile_examples(path: str) -> list[dict]:
    examples = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(json.loads(line))
    return examples


def tokenize_examples(examples, tokenizer, max_len=256, eod_id=151643):
    sequences = []
    for ex in examples:
        text = f"{ex['input']}\n{ex['output']}"
        token_ids = tokenizer.encode(text, add_special_tokens=False)
        token_ids.append(eod_id)
        if len(token_ids) > max_len:
            token_ids = token_ids[:max_len]
        sequences.append(np.array(token_ids, dtype=np.int32))
    return sequences


def make_eval_batch(sequences, max_seq_len=256, eod_id=151643):
    """Pack all eval sequences into one batch for consistent loss measurement."""
    all_tokens = []
    for s in sequences:
        all_tokens.append(s)
    stream = np.concatenate(all_tokens)
    # Use as much as fits in one sequence
    T = min(max_seq_len, len(stream) - 1)
    input_ids = stream[:T].reshape(1, T)
    targets = stream[1:T+1].reshape(1, T)
    return mx.array(input_ids), mx.array(targets)


# ══════════════════════════════════════════════════════════════════════
# M-space analysis
# ══════════════════════════════════════════════════════════════════════

def normalize_frobenius(M: np.ndarray) -> np.ndarray:
    """Normalize matrix to unit Frobenius norm."""
    norm = np.linalg.norm(M, 'fro')
    if norm < 1e-12:
        return M
    return M / norm


def compute_mspace_scores_q(
    W_q_t: np.ndarray,     # (d_out, d_in) ternary ±1
    W_k_t: np.ndarray,     # (d_out, d_in) ternary ±1
    R: np.ndarray,          # (d_in, d_in) residual M_target_norm - M_current_norm
) -> np.ndarray:
    """Compute M-space improvement score for every possible Q flip.

    score_q[h, i] = -4 * W_q_t[h,i] * dot(R[i,:], W_k_t[h,:])

    Positive score → flipping this position moves M closer to target.

    Returns: (d_out, d_in) float64 scores
    """
    # R @ W_k_t[h,:] gives (d_in,) vector where element i = dot(R[i,:], W_k_t[h,:])
    # For all h at once: R @ W_k_t.T gives (d_in, d_out), transpose to (d_out, d_in)
    #   element [h, i] = dot(R[i,:], W_k_t[h,:])
    inner = (R @ W_k_t.T).T   # (d_out, d_in)
    scores = -4.0 * W_q_t * inner
    return scores


def compute_mspace_scores_k(
    W_q_t: np.ndarray,     # (d_out, d_in) ternary ±1
    W_k_t: np.ndarray,     # (d_out, d_in) ternary ±1
    R: np.ndarray,          # (d_in, d_in) residual
) -> np.ndarray:
    """Compute M-space improvement score for every possible K flip.

    score_k[h, j] = -4 * W_k_t[h,j] * dot(R[:,j], W_q_t[h,:])
                   = -4 * W_k_t[h,j] * dot(R.T[j,:], W_q_t[h,:])

    Returns: (d_out, d_in) float64 scores
    """
    # R.T @ W_q_t.T gives (d_in, d_out), transpose to (d_out, d_in)
    #   element [h, j] = dot(R.T[j,:], W_q_t[h,:]) = dot(R[:,j], W_q_t[h,:])
    inner = (R.T @ W_q_t.T).T  # (d_out, d_in)
    scores = -4.0 * W_k_t * inner
    return scores


def compute_gradient_scores(
    model: MicroModel,
    input_ids: mx.array,
    targets: mx.array,
) -> dict[int, dict[str, np.ndarray]]:
    """Compute gradient-heat (routing) scores for all Q/K positions.

    Returns: {layer_idx: {"grad_q": (d_out, d_in), "grad_k": (d_out, d_in)}}

    The routing score at position [h,i] is:
      -grad[h,i] * sign(W[h,i])
    Positive → gradient wants to flip this position (routing signal).
    """
    def loss_fn(model, x, t):
        _, loss = model(x, t)
        return loss

    loss_val, grads = nn.value_and_grad(model, loss_fn)(model, input_ids, targets)
    mx.eval(loss_val, grads)

    result = {}
    for layer_idx in range(model.cfg.n_layers):
        # Navigate the grad tree to find q_proj and k_proj weight gradients
        block_grads = grads["blocks"][layer_idx]
        grad_q = np.array(block_grads["attn"]["q_proj"]["weight"])
        grad_k = np.array(block_grads["attn"]["k_proj"]["weight"])

        W_q = np.array(model.blocks[layer_idx].attn.q_proj.weight)
        W_k = np.array(model.blocks[layer_idx].attn.k_proj.weight)

        # Routing score: positive when gradient wants to flip the sign
        # descent direction = -grad, routing when descent opposes current sign
        sign_q = np.sign(W_q)
        sign_k = np.sign(W_k)
        sign_q[sign_q == 0] = 1
        sign_k[sign_k == 0] = 1

        # score = -grad * sign(W) → positive when descent direction opposes sign
        routing_q = -grad_q * sign_q
        routing_k = -grad_k * sign_k

        result[layer_idx] = {
            "grad_q": routing_q,
            "grad_k": routing_k,
        }

    return result, float(loss_val.item())


def measure_flip_loss_delta(
    model: MicroModel,
    layer_idx: int,
    matrix: str,          # "q" or "k"
    positions: list[tuple[int, int]],
    input_ids: mx.array,
    targets: mx.array,
    baseline_loss: float,
) -> np.ndarray:
    """Measure actual loss delta for each flip (one at a time).

    Flips position, measures loss, restores. Returns array of loss deltas.
    Negative delta = loss improved (flip helped).
    """
    block = model.blocks[layer_idx]
    attn = block.attn
    proj = attn.q_proj if matrix == "q" else attn.k_proj

    # Get current weight
    W = np.array(proj.weight)  # (d_out, d_in)
    deltas = np.zeros(len(positions))

    for idx, (h, i) in enumerate(positions):
        # Flip one position
        W_new = W.copy()
        W_new[h, i] = -W_new[h, i]

        # Set weight, forward pass, measure loss
        proj.weight = mx.array(W_new)
        mx.eval(proj.weight)
        _, loss = model(input_ids, targets)
        mx.eval(loss)
        deltas[idx] = float(loss.item()) - baseline_loss

        # Restore
        proj.weight = mx.array(W)
        mx.eval(proj.weight)

    return deltas


# ══════════════════════════════════════════════════════════════════════
# SVD mode analysis
# ══════════════════════════════════════════════════════════════════════

def analyze_kernel_structure(
    M_float: np.ndarray,
    M_ternary: np.ndarray,
    label: str,
) -> dict:
    """Analyze and compare M-space structure."""
    U_f, s_f, Vt_f = np.linalg.svd(M_float, full_matrices=False)
    U_t, s_t, Vt_t = np.linalg.svd(M_ternary, full_matrices=False)

    total_f = (s_f**2).sum()
    total_t = (s_t**2).sum()
    cum_f = np.cumsum(s_f**2) / total_f
    cum_t = np.cumsum(s_t**2) / total_t

    # Mode alignment for top modes
    n_modes = min(10, len(s_f), len(s_t))
    mode_align = []
    for k in range(n_modes):
        cos = abs(np.dot(U_f[:, k], U_t[:, k]))
        mode_align.append(float(cos))

    return {
        "label": label,
        "float_rank90": int(np.searchsorted(cum_f, 0.90) + 1),
        "ternary_rank90": int(np.searchsorted(cum_t, 0.90) + 1),
        "float_top1_pct": float(cum_f[0] * 100),
        "ternary_top1_pct": float(cum_t[0] * 100),
        "float_top5_pct": float(cum_f[4] * 100) if len(cum_f) > 4 else 100.0,
        "ternary_top5_pct": float(cum_t[4] * 100) if len(cum_t) > 4 else 100.0,
        "mode_alignment": mode_align,
        "sigma_ratio_0_1_float": float(s_f[0] / s_f[1]) if s_f[1] > 0 else float('inf'),
        "sigma_ratio_0_1_ternary": float(s_t[0] / s_t[1]) if s_t[1] > 0 else float('inf'),
    }


# ══════════════════════════════════════════════════════════════════════
# Main experiment
# ══════════════════════════════════════════════════════════════════════

def run_experiment():
    t0 = time.time()
    print("=" * 70)
    print("M-SPACE vs GRADIENT-HEAT SCORING — Micro Model Experiment")
    print("=" * 70)
    print()

    cfg = MicroConfig()
    model = MicroModel(cfg)

    # Load trained weights
    ckpt_path = Path("checkpoints/micro/final/model.npz")
    if not ckpt_path.exists():
        ckpt_path = Path("checkpoints/micro/step_005000/model.npz")
    print(f"Loading model from {ckpt_path}")
    weights = mx.load(str(ckpt_path))
    model.load_weights(list(weights.items()))
    mx.eval(model.parameters())
    print(f"  {cfg.n_layers} layers, {cfg.n_heads} heads, d_model={cfg.d_model}, d_head={cfg.d_head}")

    # Load eval data for loss measurement
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    train_examples = load_compile_examples(cfg.train_file)
    eval_examples = load_compile_examples(cfg.eval_file)
    train_seqs = tokenize_examples(train_examples, tokenizer, cfg.max_seq_len, cfg.eod_id)
    eval_seqs = tokenize_examples(eval_examples, tokenizer, cfg.max_seq_len, cfg.eod_id)

    # Use a FIXED eval batch for consistent loss measurement
    eval_input, eval_target = make_eval_batch(eval_seqs, cfg.max_seq_len, cfg.eod_id)

    # Use a larger training batch for gradient estimation (average over more data)
    train_input_ids_list = []
    train_targets_list = []
    rng = np.random.RandomState(42)
    all_train = np.concatenate(train_seqs)
    for b in range(8):  # 8 sequences
        start = rng.randint(0, len(all_train) - cfg.max_seq_len - 1)
        chunk = all_train[start:start + cfg.max_seq_len + 1]
        train_input_ids_list.append(chunk[:cfg.max_seq_len])
        train_targets_list.append(chunk[1:cfg.max_seq_len + 1])
    grad_input = mx.array(np.stack(train_input_ids_list))
    grad_target = mx.array(np.stack(train_targets_list))

    # Baseline loss
    _, baseline_loss_val = model(eval_input, eval_target)
    mx.eval(baseline_loss_val)
    baseline_loss = float(baseline_loss_val.item())
    print(f"  Baseline eval loss: {baseline_loss:.4f}")
    print()

    # ── Gradient scores (one backward pass on training data) ──
    print("Computing gradient-heat scores (one backward pass)...")
    grad_scores, train_loss = compute_gradient_scores(model, grad_input, grad_target)
    print(f"  Train loss: {train_loss:.4f}")
    print()

    # ── Per-layer analysis ──
    results = {"layers": {}, "baseline_loss": baseline_loss}
    N_VERIFY = 50  # number of top candidates to actually flip-test

    for layer_idx in range(cfg.n_layers):
        print(f"{'='*70}")
        print(f"LAYER {layer_idx}")
        print(f"{'='*70}")

        block = model.blocks[layer_idx]
        attn = block.attn
        W_q = np.array(attn.q_proj.weight)  # (128, 128) float32
        W_k = np.array(attn.k_proj.weight)  # (128, 128) float32

        # ── Sign-quantize ──
        W_q_t = np.sign(W_q).astype(np.float64)
        W_k_t = np.sign(W_k).astype(np.float64)
        W_q_t[W_q_t == 0] = 1.0
        W_k_t[W_k_t == 0] = 1.0

        # ── Compute M matrices ──
        M_float = W_q.T @ W_k           # (128, 128) — the target gem
        M_ternary = W_q_t.T @ W_k_t     # (128, 128) — the rough stone

        # Normalize to unit Frobenius norm for scale-invariant comparison
        M_float_n = normalize_frobenius(M_float.astype(np.float64))
        M_ternary_n = normalize_frobenius(M_ternary.astype(np.float64))
        R = M_float_n - M_ternary_n  # residual in normalized M-space

        # ── M-space structure analysis ──
        structure = analyze_kernel_structure(M_float, M_ternary, f"layer_{layer_idx}")
        print(f"\n  M-space structure:")
        print(f"    Float32:  rank90={structure['float_rank90']}, "
              f"top-1={structure['float_top1_pct']:.1f}%, "
              f"σ0/σ1={structure['sigma_ratio_0_1_float']:.2f}")
        print(f"    Ternary:  rank90={structure['ternary_rank90']}, "
              f"top-1={structure['ternary_top1_pct']:.1f}%, "
              f"σ0/σ1={structure['sigma_ratio_0_1_ternary']:.2f}")
        print(f"    Mode 0 alignment: {structure['mode_alignment'][0]:.4f}")

        # ── M-space scores ──
        m_scores_q = compute_mspace_scores_q(W_q_t, W_k_t, R)
        m_scores_k = compute_mspace_scores_k(W_q_t, W_k_t, R)

        # ── Gradient scores ──
        g_scores_q = grad_scores[layer_idx]["grad_q"]
        g_scores_k = grad_scores[layer_idx]["grad_k"]

        # ── Rank correlation (Spearman) ──
        from scipy import stats

        # Flatten and compare Q scores
        m_flat_q = m_scores_q.flatten()
        g_flat_q = g_scores_q.flatten()
        rho_q, pval_q = stats.spearmanr(m_flat_q, g_flat_q)

        # K scores
        m_flat_k = m_scores_k.flatten()
        g_flat_k = g_scores_k.flatten()
        rho_k, pval_k = stats.spearmanr(m_flat_k, g_flat_k)

        print(f"\n  Score correlation (Spearman ρ):")
        print(f"    Q: ρ = {rho_q:+.4f}  (p = {pval_q:.2e})")
        print(f"    K: ρ = {rho_k:+.4f}  (p = {pval_k:.2e})")

        # ── Score distribution ──
        print(f"\n  Score distributions:")
        print(f"    M-space Q: mean={m_flat_q.mean():.6f}, std={m_flat_q.std():.6f}, "
              f"max={m_flat_q.max():.6f}")
        print(f"    Gradient Q: mean={g_flat_q.mean():.6f}, std={g_flat_q.std():.6f}, "
              f"max={g_flat_q.max():.6f}")

        # ── Top candidates: where do they agree/disagree? ──
        top_m_q_idx = np.argsort(-m_flat_q)[:N_VERIFY]
        top_g_q_idx = np.argsort(-g_flat_q)[:N_VERIFY]
        overlap_q = len(set(top_m_q_idx) & set(top_g_q_idx))

        top_m_k_idx = np.argsort(-m_flat_k)[:N_VERIFY]
        top_g_k_idx = np.argsort(-g_flat_k)[:N_VERIFY]
        overlap_k = len(set(top_m_k_idx) & set(top_g_k_idx))

        print(f"\n  Top-{N_VERIFY} overlap:")
        print(f"    Q: {overlap_q}/{N_VERIFY} positions in common ({overlap_q/N_VERIFY*100:.0f}%)")
        print(f"    K: {overlap_k}/{N_VERIFY} positions in common ({overlap_k/N_VERIFY*100:.0f}%)")

        # ── Ground truth: actually flip top candidates and measure loss ──
        print(f"\n  Measuring actual loss deltas for top-{N_VERIFY} from each scorer...")

        d_out, d_in = W_q.shape

        # M-space top candidates for Q
        m_top_positions_q = [(idx // d_in, idx % d_in) for idx in top_m_q_idx]
        m_deltas_q = measure_flip_loss_delta(
            model, layer_idx, "q", m_top_positions_q,
            eval_input, eval_target, baseline_loss)

        # Gradient top candidates for Q
        g_top_positions_q = [(idx // d_in, idx % d_in) for idx in top_g_q_idx]
        g_deltas_q = measure_flip_loss_delta(
            model, layer_idx, "q", g_top_positions_q,
            eval_input, eval_target, baseline_loss)

        # M-space top candidates for K
        m_top_positions_k = [(idx // d_in, idx % d_in) for idx in top_m_k_idx]
        m_deltas_k = measure_flip_loss_delta(
            model, layer_idx, "k", m_top_positions_k,
            eval_input, eval_target, baseline_loss)

        # Gradient top candidates for K
        g_top_positions_k = [(idx // d_in, idx % d_in) for idx in top_g_k_idx]
        g_deltas_k = measure_flip_loss_delta(
            model, layer_idx, "k", g_top_positions_k,
            eval_input, eval_target, baseline_loss)

        # ── Results ──
        m_helpful_q = (m_deltas_q < 0).sum()
        g_helpful_q = (g_deltas_q < 0).sum()
        m_helpful_k = (m_deltas_k < 0).sum()
        g_helpful_k = (g_deltas_k < 0).sum()

        m_mean_delta_q = m_deltas_q.mean()
        g_mean_delta_q = g_deltas_q.mean()
        m_mean_delta_k = m_deltas_k.mean()
        g_mean_delta_k = g_deltas_k.mean()

        m_best_q = m_deltas_q.min()
        g_best_q = g_deltas_q.min()
        m_best_k = m_deltas_k.min()
        g_best_k = g_deltas_k.min()

        print(f"\n  RESULTS — Q flips (top-{N_VERIFY} from each scorer):")
        print(f"    {'':>12} {'M-space':>12} {'Gradient':>12}")
        print(f"    {'helpful':>12} {m_helpful_q:>12}/{N_VERIFY} {g_helpful_q:>12}/{N_VERIFY}")
        print(f"    {'mean Δloss':>12} {m_mean_delta_q:>+12.6f} {g_mean_delta_q:>+12.6f}")
        print(f"    {'best Δloss':>12} {m_best_q:>+12.6f} {g_best_q:>+12.6f}")

        print(f"\n  RESULTS — K flips (top-{N_VERIFY} from each scorer):")
        print(f"    {'':>12} {'M-space':>12} {'Gradient':>12}")
        print(f"    {'helpful':>12} {m_helpful_k:>12}/{N_VERIFY} {g_helpful_k:>12}/{N_VERIFY}")
        print(f"    {'mean Δloss':>12} {m_mean_delta_k:>+12.6f} {g_mean_delta_k:>+12.6f}")
        print(f"    {'best Δloss':>12} {m_best_k:>+12.6f} {g_best_k:>+12.6f}")

        # ── Correlation of scores with actual loss deltas ──
        # For the positions we tested, how well does each score predict loss delta?
        # Combine M-space top and gradient top for a broader sample
        all_positions_q = list(set(m_top_positions_q + g_top_positions_q))
        all_m_scores = np.array([m_scores_q[h, i] for h, i in all_positions_q])
        all_g_scores = np.array([g_scores_q[h, i] for h, i in all_positions_q])

        # Measure loss deltas for the combined set (skip already-measured ones)
        already_measured_q = {}
        for idx, pos in enumerate(m_top_positions_q):
            already_measured_q[pos] = m_deltas_q[idx]
        for idx, pos in enumerate(g_top_positions_q):
            already_measured_q[pos] = g_deltas_q[idx]

        # For positions not yet measured
        need_measure = [p for p in all_positions_q if p not in already_measured_q]
        if need_measure:
            extra_deltas = measure_flip_loss_delta(
                model, layer_idx, "q", need_measure,
                eval_input, eval_target, baseline_loss)
            for idx, pos in enumerate(need_measure):
                already_measured_q[pos] = extra_deltas[idx]

        all_deltas_q = np.array([already_measured_q[p] for p in all_positions_q])

        # Correlation of score with actual delta (negative = better score should predict negative delta)
        # A good scorer has NEGATIVE correlation with loss delta (high score → loss decreases)
        pred_corr_m, _ = stats.spearmanr(-all_m_scores, all_deltas_q)
        pred_corr_g, _ = stats.spearmanr(-all_g_scores, all_deltas_q)

        print(f"\n  Predictive power (ρ of score vs actual Δloss, {len(all_positions_q)} positions):")
        print(f"    M-space:  ρ = {pred_corr_m:+.4f}  (positive = score predicts improvement)")
        print(f"    Gradient: ρ = {pred_corr_g:+.4f}")

        # ── Store results ──
        results["layers"][str(layer_idx)] = {
            "structure": structure,
            "correlation_q": {"rho": float(rho_q), "pval": float(pval_q)},
            "correlation_k": {"rho": float(rho_k), "pval": float(pval_k)},
            "overlap_q": overlap_q,
            "overlap_k": overlap_k,
            "q_flips": {
                "mspace": {
                    "n_helpful": int(m_helpful_q),
                    "mean_delta": float(m_mean_delta_q),
                    "best_delta": float(m_best_q),
                },
                "gradient": {
                    "n_helpful": int(g_helpful_q),
                    "mean_delta": float(g_mean_delta_q),
                    "best_delta": float(g_best_q),
                },
            },
            "k_flips": {
                "mspace": {
                    "n_helpful": int(m_helpful_k),
                    "mean_delta": float(m_mean_delta_k),
                    "best_delta": float(m_best_k),
                },
                "gradient": {
                    "n_helpful": int(g_helpful_k),
                    "mean_delta": float(g_mean_delta_k),
                    "best_delta": float(g_best_k),
                },
            },
            "predictive_power_q": {
                "mspace_rho": float(pred_corr_m),
                "gradient_rho": float(pred_corr_g),
                "n_positions": len(all_positions_q),
            },
        }

        print()

    # ── Summary ──
    elapsed = time.time() - t0
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"{'Layer':>6} │ {'ρ(M,G)_Q':>10} │ {'Overlap Q':>10} │ "
          f"{'M helpful':>10} │ {'G helpful':>10} │ {'M pred ρ':>10} │ {'G pred ρ':>10}")
    print("─" * 80)
    for layer_idx in range(cfg.n_layers):
        lr = results["layers"][str(layer_idx)]
        rho_q = lr["correlation_q"]["rho"]
        ov_q = lr["overlap_q"]
        mh = lr["q_flips"]["mspace"]["n_helpful"]
        gh = lr["q_flips"]["gradient"]["n_helpful"]
        mp = lr["predictive_power_q"]["mspace_rho"]
        gp = lr["predictive_power_q"]["gradient_rho"]
        print(f"  {layer_idx:>4} │ {rho_q:>+10.4f} │ {ov_q:>7}/{N_VERIFY:>2} │ "
              f"{mh:>7}/{N_VERIFY:>2} │ {gh:>7}/{N_VERIFY:>2} │ {mp:>+10.4f} │ {gp:>+10.4f}")

    print()
    print(f"Elapsed: {elapsed:.1f}s")

    # ── Save ──
    out_dir = Path("results/mspace-probe")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "summary.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {out_path}")


if __name__ == "__main__":
    run_experiment()
