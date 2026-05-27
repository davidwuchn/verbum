"""
Probe Newton Phase Transition — When does second-order become viable?

THE QUESTION: The model has two training phases:
  1. EXPANDING: rank-1 → rank-27, gradient orthogonal to subspace, Adam works
  2. REFINING: rank-27 stable, gradient aligned with subspace, Newton optimal

We have micro model checkpoints at every 500 steps (step_000500 through
step_005000). For each checkpoint, measure:
  1. The composed plate's effective rank (how expanded is the model?)
  2. Gradient alignment with the composed plate's SVD subspace
  3. At what step does alignment cross 0.5? (the phase transition)
  4. How much faster would Newton be at each stage?

Also: simulate a Newton step at each checkpoint and measure loss reduction
compared to one Adam step.

Usage:
    cd verbum
    uv run python scripts/micro/probe_newton_phase.py

License: MIT
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import mlx.core as mx
import mlx.nn as nn

sys.path.insert(0, str(Path(__file__).parent))
from micro_model import (
    MicroModel, MicroConfig,
    PCAQ_ZONE_B_TARGETS, _precompute_parity_eigenbasis,
    COMBINATOR_NAMES,
)


def get_crystal_eigenbasis():
    data = _precompute_parity_eigenbasis(PCAQ_ZONE_B_TARGETS)
    return data["eigvecs"], data["eigvals"]


def compute_composed_plate(model, examples, tokenizer):
    """Compute the composed plate T via least-squares: T = lstsq(X_in, X_out).

    X_in = post-embedding residuals, X_out = pre-output residuals.
    """
    model.set_capture(True)
    all_inputs = []
    all_outputs = []

    for example in examples:
        text = example["input"] + "\n" + example["output"]
        if tokenizer:
            tokens = tokenizer.encode(text)
        else:
            tokens = [ord(c) % 1000 for c in text]
        if len(tokens) > 128:
            tokens = tokens[:128]
        input_ids = mx.array([tokens[:-1]])
        targets = mx.array([tokens[1:]])

        logits, loss = model(input_ids, targets)
        mx.eval(logits, loss)
        traces = model.get_traces()
        for t in traces:
            for section in ["block", "attn", "ffn"]:
                for k, v in t[section].items():
                    if isinstance(v, mx.array):
                        mx.eval(v)

        # Input = first layer's input (post-embedding)
        # = residual_post_attn[0] - attn_contribution[0]
        first_block = traces[0]["block"]
        post_attn = np.array(first_block["residual_post_attn"])[0]  # (L, d)
        attn_contrib = np.array(first_block["attn_contribution"])[0]
        embed_residual = post_attn - attn_contrib  # (L, d)

        # Output = last layer's output (pre-output-norm)
        last_block = traces[-1]["block"]
        final_residual = np.array(last_block["residual_post_ffn"])[0]  # (L, d)

        all_inputs.append(embed_residual)
        all_outputs.append(final_residual)

    model.set_capture(False)

    X_in = np.concatenate(all_inputs, axis=0)   # (N, d)
    X_out = np.concatenate(all_outputs, axis=0)  # (N, d)

    # Composed plate: X_out ≈ X_in @ T
    T, residuals, rank, sv = np.linalg.lstsq(X_in, X_out, rcond=None)
    return T, X_in, X_out


def compute_gradient_flat(model, input_ids, targets):
    """Compute gradient, return as flat vector of all parameters."""
    def loss_fn(m, inp, tgt):
        _, loss = m(inp, tgt)
        return loss

    grad_fn = nn.value_and_grad(model, loss_fn)
    loss_val, grads = grad_fn(model, input_ids, targets)
    mx.eval(loss_val, grads)

    flat = dict(nn.utils.tree_flatten(grads))
    vectors = []
    for k in sorted(flat.keys()):
        vectors.append(np.array(flat[k]).flatten())
    return float(loss_val.item()), np.concatenate(vectors)


def main():
    checkpoint_base = Path(__file__).parent.parent.parent / "checkpoints" / "micro"
    results_dir = Path(__file__).parent.parent.parent / "results" / "newton-phase"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Available checkpoints
    steps = [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
    checkpoint_dirs = []
    for s in steps:
        p = checkpoint_base / f"step_{s:06d}"
        if p.exists():
            checkpoint_dirs.append((s, p))

    print("=" * 70)
    print("Newton Phase Transition Probe")
    print(f"Checkpoints: {[s for s, _ in checkpoint_dirs]}")
    print("=" * 70)

    # Load tokenizer
    try:
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B", trust_remote_code=True)
    except Exception:
        tokenizer = None

    # Load data
    data_path = Path(__file__).parent.parent.parent / "data" / "compile-eval.jsonl"
    if not data_path.exists():
        data_path = Path(__file__).parent.parent.parent / "data" / "compile-test.jsonl"
    examples = []
    with open(data_path) as f:
        for line in f:
            examples.append(json.loads(line))
            if len(examples) >= 10:
                break

    cfg = MicroConfig()
    crystal_eigvecs, crystal_eigvals = get_crystal_eigenbasis()

    all_results = []

    for step, ckpt_path in checkpoint_dirs:
        print(f"\n{'─'*50}")
        print(f"Step {step}")
        print(f"{'─'*50}")

        # Load model
        model = MicroModel(cfg)
        weights = mx.load(str(ckpt_path / "model.npz"))
        model.load_weights(list(weights.items()))
        mx.eval(model.parameters())

        # Crystal health
        diag = model.crystal_diagnostics()
        crystal_loss = diag["crystal_loss"]
        print(f"  Crystal loss: {crystal_loss:.6f}")

        # Compute composed plate
        T, X_in, X_out = compute_composed_plate(model, examples[:5], tokenizer)

        # SVD of composed plate
        U, S, Vh = np.linalg.svd(T, full_matrices=False)
        # Effective rank
        S_norm = S / (S.sum() + 1e-12)
        pr = float((S.sum()**2) / (np.sum(S**2) + 1e-12))
        rank90 = int(np.searchsorted(np.cumsum(S / S.sum()), 0.9)) + 1
        sigma1_frac = float(S[0] / S.sum())

        print(f"  Composed plate: PR={pr:.1f}, rank90={rank90}, σ₁={sigma1_frac:.3f}")
        print(f"  Top 5 SVs: {S[:5].tolist()}")

        # Compute gradient on a test example
        text = examples[0]["input"] + "\n" + examples[0]["output"]
        if tokenizer:
            tokens = tokenizer.encode(text)
        else:
            tokens = [ord(c) % 1000 for c in text]
        if len(tokens) > 128:
            tokens = tokens[:128]
        input_ids = mx.array([tokens[:-1]])
        targets = mx.array([tokens[1:]])

        loss, grad_flat = compute_gradient_flat(model, input_ids, targets)
        print(f"  Loss: {loss:.4f}, |grad|: {np.linalg.norm(grad_flat):.4f}")

        # Gradient alignment with composed plate's SVD subspace
        # The composed plate T has SVD: T = U @ diag(S) @ Vh
        # Gradient of loss w.r.t. T: ∂L/∂T
        # We need the gradient w.r.t. T specifically

        # Compute ∂L/∂T via finite differences on the composed plate
        # ∂L/∂T[i,j] ≈ (loss(T + εE_ij) - loss(T)) / ε
        # But this is expensive. Instead, use the analytical result:
        # ∂L/∂T = X_in^T @ (X_in @ T - X_out) / N  (for MSE loss on plate)
        # This is the composed plate gradient

        N = X_in.shape[0]
        residual = X_in @ T - X_out  # (N, d)
        grad_T = X_in.T @ residual / N  # (d, d) — gradient of plate error

        # Project gradient into T's SVD subspace
        grad_T_flat = grad_T.flatten()
        grad_norm = np.linalg.norm(grad_T_flat)

        # Subspace alignment at various k
        alignments = {}
        for k in [1, 2, 5, 10, 27, 50, 100]:
            if k > min(T.shape):
                continue
            # Project T's gradient into top-k subspace of T
            # T = U S Vh → top-k subspace is spanned by columns of U[:,:k] and Vh[:k,:]
            # For a d×d matrix gradient, project via:
            # G_proj = U[:,:k] @ U[:,:k].T @ G @ Vh[:k,:].T @ Vh[:k,:]
            G_proj = U[:, :k] @ (U[:, :k].T @ grad_T @ Vh[:k, :].T) @ Vh[:k, :]
            G_proj_flat = G_proj.flatten()
            cos = float(np.dot(grad_T_flat, G_proj_flat) /
                       (np.linalg.norm(grad_T_flat) * np.linalg.norm(G_proj_flat) + 1e-12))
            energy = float(np.sum(G_proj_flat**2) / (np.sum(grad_T_flat**2) + 1e-12))
            alignments[k] = {"cosine": cos, "energy_frac": energy}
            print(f"  Alignment k={k}: cos={cos:.4f}, energy={energy:.1%}")

        # Newton step simulation
        # For the composed plate: the Hessian is H = X_in^T @ X_in / N
        # Newton step: ΔT = H⁻¹ @ grad_T = (X_in^T X_in)⁻¹ @ X_in^T @ residual / N
        # = lstsq(X_in, residual)  (it's just another least-squares!)
        delta_T_newton, _, _, _ = np.linalg.lstsq(X_in, residual, rcond=None)

        # Predicted loss reduction from Newton step
        # New T = T - delta_T_newton
        T_new = T - delta_T_newton
        new_residual = X_in @ T_new - X_out
        old_mse = float(np.mean(residual**2))
        new_mse = float(np.mean(new_residual**2))
        newton_reduction = old_mse - new_mse

        # For comparison: one Adam-like step (gradient descent with lr)
        lr = 1e-3
        T_adam = T - lr * grad_T
        adam_residual = X_in @ T_adam - X_out
        adam_mse = float(np.mean(adam_residual**2))
        adam_reduction = old_mse - adam_mse

        newton_advantage = newton_reduction / (adam_reduction + 1e-12)

        print(f"  Plate MSE: {old_mse:.6f}")
        print(f"  Newton step: MSE → {new_mse:.6f} (Δ={newton_reduction:+.6f})")
        print(f"  Adam step:   MSE → {adam_mse:.6f} (Δ={adam_reduction:+.6f})")
        print(f"  Newton advantage: {newton_advantage:.1f}× better loss reduction")

        # Condition number of the Hessian
        H = X_in.T @ X_in / N
        H_eigvals = np.linalg.eigvalsh(H)[::-1]
        cond = float(H_eigvals[0] / (H_eigvals[-1] + 1e-12))
        effective_cond = float(H_eigvals[0] / (H_eigvals[min(26, len(H_eigvals)-1)] + 1e-12))

        print(f"  Hessian condition: {cond:.1f} (full), {effective_cond:.1f} (top-27)")

        all_results.append({
            "step": step,
            "crystal_loss": crystal_loss,
            "loss": loss,
            "composed_plate_pr": pr,
            "composed_plate_rank90": rank90,
            "sigma1_frac": sigma1_frac,
            "alignments": {str(k): v for k, v in alignments.items()},
            "plate_mse": old_mse,
            "newton_mse": new_mse,
            "adam_mse": adam_mse,
            "newton_advantage": newton_advantage,
            "hessian_condition": cond,
            "hessian_condition_top27": effective_cond,
        })

    # ══════════════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════════════

    print("\n" + "=" * 70)
    print("PHASE TRANSITION SUMMARY")
    print("=" * 70)

    print(f"\n{'Step':>6} | {'Loss':>8} | {'Plate PR':>8} | {'rank90':>6} | "
          f"{'cos@k=1':>8} {'cos@k=27':>8} | {'Newton×':>8} | {'Hess κ':>10}")
    print("-" * 90)
    for r in all_results:
        cos1 = r["alignments"].get("1", {}).get("cosine", 0)
        cos27 = r["alignments"].get("27", {}).get("cosine", 0)
        print(f"{r['step']:>6} | {r['loss']:>8.4f} | {r['composed_plate_pr']:>8.1f} | "
              f"{r['composed_plate_rank90']:>6} | "
              f"{cos1:>+8.4f} {cos27:>+8.4f} | "
              f"{r['newton_advantage']:>8.1f}× | "
              f"{r['hessian_condition_top27']:>10.1f}")

    # Identify phase transition
    for r in all_results:
        cos27 = r["alignments"].get("27", {}).get("cosine", 0)
        if cos27 > 0.5:
            print(f"\n  Phase transition at step {r['step']}: cos@k=27 = {cos27:.4f} > 0.5")
            print(f"  → Newton becomes viable here")
            break
    else:
        cosines = [r["alignments"].get("27", {}).get("cosine", 0) for r in all_results]
        print(f"\n  No phase transition observed. Max cos@k=27 = {max(cosines):.4f}")

    # Save
    out_path = results_dir / "summary.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
