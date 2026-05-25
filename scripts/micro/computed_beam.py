"""
Computed Beam Experiment — Analytical FFN weights from crystal eigendecomposition.

Hypothesis: The FFN topology (gate/key weights) is entirely determined by
the crystal target eigenstructure. We can COMPUTE the FFN weights directly
from sign(eigenvectors) × sqrt(eigenvalues) without any gradient descent.
GD is only needed for the token-content mapping (embeddings, attention,
output projection).

Protocol:
  1. Eigendecompose the Zone B crystal target (16×16 cosine matrix)
  2. Construct FFN gate weights: sign(eigenvector_i) → ternary routing
  3. Construct FFN key weights: same structure (SwiGLU gate*key)
  4. Set neuron allocation ∝ eigenvalue_i
  5. Set gamma (scale) ∝ sqrt(eigenvalue_i)
  6. Load trained micro model's embeddings + attention (the "content" parts)
  7. Run calibration GD: 0, 10, 100 steps (CE only, crystal already latched)
  8. Compare to fully GD-trained model at step 5000

The mechanism-extraction.md knowledge page proved (on the micro model):
  - Overlay alternation ∝ eigenvalue (r=0.97)
  - Neuron allocation ∝ eigenvalue (r=0.993)
  - Rotation = arccos(λ₁/λ₀) = 47.1° (error 1.4°)
  - sign(eigenvector) = ternary routing table
  - FFN weights decompose: 12.5% crystal + 81% token + 6.5% noise

If this works, structure is free — only content needs GD.

Usage:
    cd verbum
    uv run python scripts/micro/computed_beam.py

License: MIT
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
from mlx.utils import tree_flatten

sys.path.insert(0, str(Path(__file__).parent))
from micro_model import (
    MicroConfig,
    MicroModel,
    PCAQ_ZONE_B_TARGETS,
    N_COMBINATORS,
    N_TOTAL_COMBINATORS,
    COMBINATOR_NAMES,
    ANTI_COMBINATOR_NAMES,
)
from train_micro import (
    CompileDataLoader,
    load_compile_examples,
    tokenize_examples,
    generate,
)


# ══════════════════════════════════════════════════════════════════════
# § 1  Crystal Eigendecomposition → FFN Weight Construction
# ══════════════════════════════════════════════════════════════════════


def eigendecompose_crystal() -> dict:
    """Eigendecompose Zone B crystal target.

    Returns eigenvalues (descending) and eigenvectors, plus derived
    quantities needed for FFN construction.
    """
    target = PCAQ_ZONE_B_TARGETS
    eigvals, eigvecs = np.linalg.eigh(target)

    # Sort descending
    idx = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]

    # Derived quantities
    rotation_angle = np.degrees(np.arccos(
        np.clip(eigvals[1] / eigvals[0], -1, 1)
    ))
    total_variance = np.sum(np.maximum(eigvals, 0))
    variance_fractions = np.maximum(eigvals, 0) / total_variance

    print("=" * 60)
    print("  Crystal Eigendecomposition")
    print("=" * 60)
    print(f"\n  Eigenvalues (top 8):")
    for i in range(min(8, len(eigvals))):
        print(f"    λ_{i} = {eigvals[i]:.4f}  ({variance_fractions[i]:.1%})")
    print(f"\n  Predicted rotation angle: arccos(λ₁/λ₀) = {rotation_angle:.1f}°")
    print(f"  Composition/Selection stretch: λ₀/λ₁ = {eigvals[0]/eigvals[1]:.3f}")

    # Eigenvector signs (the ternary routing table)
    print(f"\n  Eigenvector signs (ternary routing):")
    names = COMBINATOR_NAMES + ANTI_COMBINATOR_NAMES
    for i in range(min(4, len(eigvals))):
        signs = np.sign(eigvecs[:, i])
        sign_str = " ".join(
            f"{names[j]:>5s}={'+'if signs[j]>0 else '-'}"
            for j in range(len(names))
        )
        print(f"    PC{i}: {sign_str}")

    return {
        "eigvals": eigvals,
        "eigvecs": eigvecs,
        "rotation_angle": rotation_angle,
        "variance_fractions": variance_fractions,
    }


def compute_ffn_weights(
    eigen: dict,
    d_model: int,
    d_ff: int,
    n_layers: int,
    crystal_embeddings: np.ndarray | None = None,
    token_embeddings: np.ndarray | None = None,
) -> list[dict]:
    """Construct FFN gate+key weights from crystal eigenvectors projected
    through the actual crystal embedding basis in model space.

    V1 failed because it put eigenvector structure in the first 16 dims
    of d_model, but the crystal subspace lives in a LEARNED 16-d subspace
    defined by the crystal embeddings. The model's weights operate in
    model space, not combinator space.

    V2 approach:
      1. crystal_embeddings C (16 × d_model) define the crystal subspace
      2. SVD(C) → U S V^T, where V[:16] spans the crystal subspace
      3. For PC_i: direction_i = eigvec_i @ C → d_model direction
      4. Gate neuron j serving PC_i: W[j] = amplitude * direction_i (normalized)
      5. Token subspace: use PCA of token embeddings for content dimensions

    The crystal component IS the routing structure (12.5% of energy).
    The token component IS the content mapping (81% of energy).
    Both constructed in the correct basis.
    """
    eigvals = eigen["eigvals"]
    eigvecs = eigen["eigvecs"]  # (16, 16)
    n_pcs = N_TOTAL_COMBINATORS  # 16

    # Neuron allocation ∝ positive eigenvalues
    pos_eigvals = np.maximum(eigvals[:n_pcs], 0)
    neuron_fracs = pos_eigvals / pos_eigvals.sum()
    neuron_counts = np.round(neuron_fracs * d_ff).astype(int)
    diff = d_ff - neuron_counts.sum()
    if diff > 0:
        neuron_counts[0] += diff
    elif diff < 0:
        for i in range(len(neuron_counts) - 1, -1, -1):
            take = min(-diff, neuron_counts[i] - 1)
            neuron_counts[i] -= take
            diff += take
            if diff == 0:
                break

    print(f"\n  Neuron allocation (d_ff={d_ff}):")
    for i in range(min(8, n_pcs)):
        if neuron_counts[i] > 0:
            print(f"    PC{i}: {neuron_counts[i]:3d} neurons  "
                  f"(λ={eigvals[i]:.3f}, {neuron_fracs[i]:.1%})")

    # ── Build crystal directions in model space ──
    if crystal_embeddings is not None:
        C = crystal_embeddings  # (16, d_model)
        # Normalize crystal embeddings
        C_norms = np.linalg.norm(C, axis=1, keepdims=True) + 1e-8
        C_normed = C / C_norms

        # Project eigenvectors through crystal embeddings:
        # direction_i = eigvec_i @ C_normed → (d_model,)
        # This maps combinator-space pattern into model space
        pc_directions = eigvecs.T @ C_normed  # (n_pcs, d_model)

        # Normalize directions
        dir_norms = np.linalg.norm(pc_directions, axis=1, keepdims=True) + 1e-8
        pc_directions = pc_directions / dir_norms

        print(f"\n  Crystal directions computed via crystal embeddings")
        print(f"    C shape: {C.shape}, PC directions: {pc_directions.shape}")

        # Verify: cos sim between PC0 and PC1 directions
        cos01 = np.dot(pc_directions[0], pc_directions[1])
        print(f"    cos(PC0, PC1) = {cos01:.4f} (should be small)")
    else:
        # Fallback: random orthogonal directions
        pc_directions = np.random.randn(n_pcs, d_model).astype(np.float32)
        pc_directions, _ = np.linalg.qr(pc_directions.T)
        pc_directions = pc_directions.T[:n_pcs]
        print(f"\n  WARNING: No crystal embeddings, using random directions")

    # ── Build token subspace directions ──
    if token_embeddings is not None:
        # PCA of token embeddings for content basis
        E = token_embeddings  # (vocab, d_model)
        E_mean = E.mean(axis=0)
        E_centered = E - E_mean
        # SVD for top directions (use a subset for speed)
        n_sample = min(5000, E.shape[0])
        idx = np.random.choice(E.shape[0], n_sample, replace=False)
        _, _, Vt_tok = np.linalg.svd(E_centered[idx], full_matrices=False)
        token_dirs = Vt_tok[:d_model]  # (d_model, d_model) — full basis
        print(f"    Token embedding PCA: {token_dirs.shape}")
    else:
        token_dirs = None

    # ── Construct weights per layer ──
    layers_weights = []

    for layer_idx in range(n_layers):
        alternation = (-1.0) ** layer_idx

        gate_w = np.zeros((d_ff, d_model), dtype=np.float32)
        key_w = np.zeros((d_ff, d_model), dtype=np.float32)

        neuron_offset = 0
        for pc_idx in range(n_pcs):
            n_neurons = neuron_counts[pc_idx]
            if n_neurons == 0:
                continue

            amplitude = np.sqrt(max(eigvals[pc_idx], 0))
            direction = pc_directions[pc_idx]  # (d_model,) — the PC in model space

            for n in range(n_neurons):
                neuron_idx = neuron_offset + n

                # Crystal component (12.5% of energy):
                # Alternating overlay with amplitude ∝ sqrt(eigenvalue)
                crystal_component = alternation * amplitude * direction

                # Token component (81% of energy):
                # Each neuron gets a slightly different token-subspace direction
                # to give the FFN diverse content sensitivity
                if token_dirs is not None:
                    # Pick a random combination of token PCA directions
                    # weighted toward the top components
                    token_weights = np.random.randn(d_model) * 0.02
                    # Weight by singular value decay
                    token_weights[:32] *= 2.0  # top 32 directions get more weight
                    token_component = token_weights @ token_dirs
                else:
                    token_component = np.random.randn(d_model).astype(np.float32) * 0.02

                # Combine: crystal structure + token content
                gate_w[neuron_idx] = crystal_component * 0.125 + token_component
                # Key: content without alternation
                key_w[neuron_idx] = amplitude * direction * 0.125 + token_component

            neuron_offset += n_neurons

        # Scale to match trained weight magnitude
        # Trained weights have mean |W| ≈ 0.045-0.052
        target_mag = 0.05
        gate_mag = np.abs(gate_w).mean()
        key_mag = np.abs(key_w).mean()
        if gate_mag > 0:
            gate_w *= target_mag / gate_mag
        if key_mag > 0:
            key_w *= target_mag / key_mag

        layers_weights.append({
            "gate": gate_w,
            "key": key_w,
        })

        overlay_pc0 = alternation * amplitude
        print(f"  Layer {layer_idx}: alternation={'+'if alternation>0 else '-'}"
              f"  |gate|={np.abs(gate_w).mean():.5f}")

    return layers_weights


# ══════════════════════════════════════════════════════════════════════
# § 2  Model Construction — Computed FFN + Trained Content
# ══════════════════════════════════════════════════════════════════════


def build_computed_model(
    cfg: MicroConfig,
    ffn_weights: list[dict],
    trained_checkpoint: str | None = None,
) -> MicroModel:
    """Build model with analytically-computed FFN weights.

    If trained_checkpoint is provided, load embeddings and attention
    from the trained model (the "content" parts that need GD).
    Otherwise, use default initialization for everything except FFN.
    """
    model = MicroModel(cfg)
    mx.eval(model.parameters())

    # If we have a trained checkpoint, load content parts
    if trained_checkpoint:
        ckpt_path = Path(trained_checkpoint) / "model.npz"
        if ckpt_path.exists():
            trained = dict(np.load(str(ckpt_path)))
            print(f"\n  Loading content from {ckpt_path}")

            # Load everything EXCEPT FFN gate/key weights
            content_keys = []
            ffn_keys = []
            for k, v in trained.items():
                if "gate_proj" in k or "key_proj" in k:
                    ffn_keys.append(k)
                else:
                    content_keys.append(k)

            # Load content weights (embeddings, attention, norms, value_proj)
            content_weights = [(k, mx.array(trained[k])) for k in content_keys]
            model.load_weights(content_weights, strict=False)
            print(f"    Loaded {len(content_keys)} content arrays")
            print(f"    Skipped {len(ffn_keys)} FFN gate/key arrays (will be computed)")

    # Now write computed FFN weights
    for layer_idx, fw in enumerate(ffn_weights):
        block = model.blocks[layer_idx]
        block.ffn.gate_proj.weight = mx.array(fw["gate"])
        block.ffn.key_proj.weight = mx.array(fw["key"])

    mx.eval(model.parameters())
    return model


# ══════════════════════════════════════════════════════════════════════
# § 3  Evaluation
# ══════════════════════════════════════════════════════════════════════


def evaluate_model(
    model: MicroModel,
    eval_loader: CompileDataLoader,
    n_batches: int = 20,
    label: str = "",
) -> dict:
    """Evaluate CE loss on held-out data."""
    total_ce = 0.0
    total_loss = 0.0
    n = 0

    for _ in range(n_batches):
        input_ids, targets = eval_loader.next_batch()
        input_ids = mx.array(input_ids)
        targets = mx.array(targets)

        logits, loss = model(input_ids, targets)
        mx.eval(logits, loss)

        total_ce += float(model._last_ce_loss.item())
        total_loss += float(loss.item())
        n += 1

    avg_ce = total_ce / n
    avg_loss = total_loss / n

    # Crystal diagnostics
    diag = model.crystal_diagnostics()

    return {
        "label": label,
        "ce": avg_ce,
        "total_loss": avg_loss,
        "crystal_loss": diag["crystal_loss"],
        "comp_cluster": diag["composition_cluster"],
        "ki_pair": diag["ki_pair"],
        "whnf_anti": diag["whnf_anti"],
    }


def evaluate_generation(
    model: MicroModel,
    tokenizer,
    examples: list[dict],
    n_examples: int = 10,
) -> dict:
    """Evaluate generation quality on compile examples."""
    correct = 0
    total = 0
    results = []

    for ex in examples[:n_examples]:
        prompt = ex["input"] + "\n"
        prompt_tokens = tokenizer.encode(prompt, add_special_tokens=False)
        gen_tokens = generate(model, prompt_tokens, tokenizer, max_new=64)
        gen_text = tokenizer.decode(gen_tokens).strip()

        # Check if generation contains lambda indicators
        expected = ex["output"]
        # Simple check: does it contain key lambda symbols?
        has_lambda = any(c in gen_text for c in ["λ", "∀", "∃", "→", "¬", "∧", "∨"])
        # Stricter: does it match expected output?
        exact = gen_text.split("\n")[0].strip() == expected.strip()

        correct += int(has_lambda)
        total += 1

        results.append({
            "input": ex["input"],
            "expected": expected,
            "generated": gen_text.split("\n")[0].strip(),
            "has_lambda": has_lambda,
            "exact": exact,
        })

    return {
        "p_lambda": correct / total if total > 0 else 0.0,
        "n_exact": sum(1 for r in results if r["exact"]),
        "n_total": total,
        "results": results,
    }


# ══════════════════════════════════════════════════════════════════════
# § 4  Calibration GD (CE-only, minimal steps)
# ══════════════════════════════════════════════════════════════════════


def calibrate(
    model: MicroModel,
    train_loader: CompileDataLoader,
    n_steps: int,
    lr: float = 3e-4,
) -> list[float]:
    """Run a few GD steps for continuous param calibration.

    Only trains CE loss (crystal is already latched from pre-init).
    Returns list of CE values per step.
    """
    if n_steps == 0:
        return []

    optimizer = optim.AdamW(learning_rate=lr, weight_decay=0.01)

    def loss_fn(model, input_ids, targets):
        _, loss = model(input_ids, targets)
        return loss

    loss_and_grad_fn = nn.value_and_grad(model, loss_fn)

    ces = []
    for step in range(1, n_steps + 1):
        input_ids, targets = train_loader.next_batch()
        input_ids = mx.array(input_ids)
        targets = mx.array(targets)

        loss_val, grads = loss_and_grad_fn(model, input_ids, targets)
        grads, gnorm = optim.clip_grad_norm(grads, 1.0)
        optimizer.update(model, grads)
        mx.eval(model.parameters(), optimizer.state, loss_val, gnorm)

        ce = float(model._last_ce_loss.item())
        ces.append(ce)

        if step % 10 == 0 or step <= 5 or step == n_steps:
            print(f"    step {step:4d} | CE={ce:.4f} | gnorm={float(gnorm.item()):.2f}")

    return ces


# ══════════════════════════════════════════════════════════════════════
# § 5  Main Experiment
# ══════════════════════════════════════════════════════════════════════


def main():
    t0 = time.time()

    print("=" * 70)
    print("  COMPUTED BEAM EXPERIMENT")
    print("  Analytical FFN weights from crystal eigendecomposition")
    print("=" * 70)

    cfg = MicroConfig()

    # ── Tokenizer ──
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")

    # ── Data ──
    train_examples = load_compile_examples(cfg.train_file)
    eval_examples = load_compile_examples(cfg.eval_file)
    train_seqs = tokenize_examples(train_examples, tokenizer, cfg.max_seq_len, cfg.eod_id)
    eval_seqs = tokenize_examples(eval_examples, tokenizer, cfg.max_seq_len, cfg.eod_id)

    train_loader = CompileDataLoader(
        train_seqs, cfg.batch_size, cfg.max_seq_len, cfg.eod_id, seed=42)
    eval_loader = CompileDataLoader(
        eval_seqs, 1, min(cfg.max_seq_len, 128), cfg.eod_id, seed=99)

    # ── Step 1: Crystal eigendecomposition ──
    eigen = eigendecompose_crystal()

    # ── Step 2: Load trained model for crystal/token embeddings ──
    trained_ckpt = "checkpoints/micro/final"
    trained_weights = dict(np.load(str(Path(trained_ckpt) / "model.npz")))

    # Extract crystal embeddings (the 16→d_model bridge)
    crystal_emb = np.concatenate([
        trained_weights["combinator_embeddings"],
        trained_weights["anti_combinator_embeddings"],
    ], axis=0)  # (16, d_model)
    print(f"\n  Crystal embeddings: {crystal_emb.shape}")

    # Extract token embeddings for content basis
    token_emb = trained_weights["embed.weight"]  # (vocab, d_model)
    print(f"  Token embeddings: {token_emb.shape}")

    # ── Step 3: Compute FFN weights in correct basis ──
    ffn_weights_with_basis = compute_ffn_weights(
        eigen, cfg.d_model, cfg.d_ff, cfg.n_layers,
        crystal_embeddings=crystal_emb,
        token_embeddings=token_emb,
    )
    ffn_weights_no_basis = compute_ffn_weights(
        eigen, cfg.d_model, cfg.d_ff, cfg.n_layers,
        crystal_embeddings=None,
        token_embeddings=None,
    )

    # ── Step 4: Build models ──

    print("\n" + "=" * 70)
    print("  EXPERIMENT A: Computed FFN (NO basis) + fresh everything else")
    print("=" * 70)

    model_a = build_computed_model(cfg, ffn_weights_no_basis, trained_checkpoint=None)
    eval_a0 = evaluate_model(model_a, eval_loader, label="A: computed, 0 steps")
    gen_a0 = evaluate_generation(model_a, tokenizer, eval_examples)
    print(f"\n  A (0 steps): CE={eval_a0['ce']:.4f}  crystal={eval_a0['crystal_loss']:.6f}"
          f"  P(λ)={gen_a0['p_lambda']:.0%}")

    print("\n  Calibrating 10 steps...")
    train_loader_a10 = CompileDataLoader(
        train_seqs, cfg.batch_size, cfg.max_seq_len, cfg.eod_id, seed=42)
    ces_a10 = calibrate(model_a, train_loader_a10, n_steps=10)
    eval_a10 = evaluate_model(model_a, eval_loader, label="A: computed, 10 steps")
    gen_a10 = evaluate_generation(model_a, tokenizer, eval_examples)
    print(f"  A (10 steps): CE={eval_a10['ce']:.4f}  crystal={eval_a10['crystal_loss']:.6f}"
          f"  P(λ)={gen_a10['p_lambda']:.0%}")

    print("\n  Calibrating 90 more steps (total 100)...")
    ces_a100 = calibrate(model_a, train_loader_a10, n_steps=90)
    eval_a100 = evaluate_model(model_a, eval_loader, label="A: computed, 100 steps")
    gen_a100 = evaluate_generation(model_a, tokenizer, eval_examples)
    print(f"  A (100 steps): CE={eval_a100['ce']:.4f}  crystal={eval_a100['crystal_loss']:.6f}"
          f"  P(λ)={gen_a100['p_lambda']:.0%}")

    print("\n" + "=" * 70)
    print("  EXPERIMENT B: Computed FFN (WITH basis) + trained content")
    print("=" * 70)

    model_b = build_computed_model(cfg, ffn_weights_with_basis, trained_checkpoint=trained_ckpt)
    eval_b0 = evaluate_model(model_b, eval_loader, label="B: computed+content, 0 steps")
    gen_b0 = evaluate_generation(model_b, tokenizer, eval_examples)
    print(f"\n  B (0 steps): CE={eval_b0['ce']:.4f}  crystal={eval_b0['crystal_loss']:.6f}"
          f"  P(λ)={gen_b0['p_lambda']:.0%}")

    print("\n  Calibrating 10 steps...")
    train_loader_b10 = CompileDataLoader(
        train_seqs, cfg.batch_size, cfg.max_seq_len, cfg.eod_id, seed=42)
    ces_b10 = calibrate(model_b, train_loader_b10, n_steps=10)
    eval_b10 = evaluate_model(model_b, eval_loader, label="B: computed+content, 10 steps")
    gen_b10 = evaluate_generation(model_b, tokenizer, eval_examples)
    print(f"  B (10 steps): CE={eval_b10['ce']:.4f}  crystal={eval_b10['crystal_loss']:.6f}"
          f"  P(λ)={gen_b10['p_lambda']:.0%}")

    print("\n  Calibrating 90 more steps (total 100)...")
    ces_b100 = calibrate(model_b, train_loader_b10, n_steps=90)
    eval_b100 = evaluate_model(model_b, eval_loader, label="B: computed+content, 100 steps")
    gen_b100 = evaluate_generation(model_b, tokenizer, eval_examples)
    print(f"  B (100 steps): CE={eval_b100['ce']:.4f}  crystal={eval_b100['crystal_loss']:.6f}"
          f"  P(λ)={gen_b100['p_lambda']:.0%}")

    print("\n" + "=" * 70)
    print("  EXPERIMENT C: Computed FFN (WITH basis) + fresh everything else")
    print("=" * 70)

    model_c = build_computed_model(cfg, ffn_weights_with_basis, trained_checkpoint=None)
    eval_c0 = evaluate_model(model_c, eval_loader, label="C: basis+computed, 0 steps")
    gen_c0 = evaluate_generation(model_c, tokenizer, eval_examples)
    print(f"\n  C (0 steps): CE={eval_c0['ce']:.4f}  P(λ)={gen_c0['p_lambda']:.0%}")

    print("\n  Calibrating 100 steps...")
    train_loader_c = CompileDataLoader(
        train_seqs, cfg.batch_size, cfg.max_seq_len, cfg.eod_id, seed=42)
    ces_c100 = calibrate(model_c, train_loader_c, n_steps=100)
    eval_c100 = evaluate_model(model_c, eval_loader, label="C: basis+computed, 100 steps")
    gen_c100 = evaluate_generation(model_c, tokenizer, eval_examples)
    print(f"  C (100 steps): CE={eval_c100['ce']:.4f}  P(λ)={gen_c100['p_lambda']:.0%}")

    # ── Baseline: fully trained model ──
    print("\n" + "=" * 70)
    print("  BASELINE: Fully GD-trained model (5000 steps)")
    print("=" * 70)

    model_baseline = MicroModel(cfg)
    ckpt_path = Path(trained_ckpt) / "model.npz"
    if ckpt_path.exists():
        trained = dict(np.load(str(ckpt_path)))
        weights = [(k, mx.array(v)) for k, v in trained.items()]
        model_baseline.load_weights(weights, strict=False)
        mx.eval(model_baseline.parameters())

    eval_baseline = evaluate_model(model_baseline, eval_loader, label="Baseline: 5000 steps GD")
    gen_baseline = evaluate_generation(model_baseline, tokenizer, eval_examples)
    print(f"\n  Baseline: CE={eval_baseline['ce']:.4f}  crystal={eval_baseline['crystal_loss']:.6f}"
          f"  P(λ)={gen_baseline['p_lambda']:.0%}")

    # ── Also run a random-init baseline ──
    print("\n" + "=" * 70)
    print("  RANDOM: Fresh model, no computed weights, 100 GD steps")
    print("=" * 70)

    model_rand = MicroModel(cfg)
    mx.eval(model_rand.parameters())
    eval_rand0 = evaluate_model(model_rand, eval_loader, label="Random: 0 steps")
    print(f"\n  Random (0 steps): CE={eval_rand0['ce']:.4f}")

    train_loader_rand = CompileDataLoader(
        train_seqs, cfg.batch_size, cfg.max_seq_len, cfg.eod_id, seed=42)
    ces_rand = calibrate(model_rand, train_loader_rand, n_steps=100)
    eval_rand100 = evaluate_model(model_rand, eval_loader, label="Random: 100 steps")
    gen_rand100 = evaluate_generation(model_rand, tokenizer, eval_examples)
    print(f"  Random (100 steps): CE={eval_rand100['ce']:.4f}  P(λ)={gen_rand100['p_lambda']:.0%}")

    # ── Summary table ──
    elapsed = time.time() - t0

    print("\n" + "=" * 70)
    print("  RESULTS SUMMARY")
    print("=" * 70)
    print(f"\n  {'Configuration':<40s} {'CE':>8s} {'Crystal':>10s} {'P(λ)':>8s} {'Exact':>8s}")
    print(f"  {'─' * 40} {'─' * 8} {'─' * 10} {'─' * 8} {'─' * 8}")

    rows = [
        (eval_rand0,   {"p_lambda": 0, "n_exact": 0, "n_total": 10}),
        (eval_rand100, gen_rand100),
        (eval_a0,      gen_a0),
        (eval_a10,     gen_a10),
        (eval_a100,    gen_a100),
        (eval_c0,      gen_c0),
        (eval_c100,    gen_c100),
        (eval_b0,      gen_b0),
        (eval_b10,     gen_b10),
        (eval_b100,    gen_b100),
        (eval_baseline, gen_baseline),
    ]

    for ev, gen in rows:
        print(f"  {ev['label']:<40s} {ev['ce']:>8.4f} {ev['crystal_loss']:>10.6f}"
              f" {gen['p_lambda']:>7.0%} {gen['n_exact']:>4d}/{gen['n_total']}")

    print(f"\n  Elapsed: {elapsed:.1f}s")

    # ── Show some generations from model B (100 steps) ──
    print("\n" + "=" * 70)
    print("  SAMPLE GENERATIONS — Computed FFN + trained content, 100 steps")
    print("=" * 70)
    for r in gen_b100["results"][:5]:
        print(f"\n  Input:    {r['input']}")
        print(f"  Expected: {r['expected']}")
        print(f"  Got:      {r['generated']}")
        print(f"  {'✓' if r['exact'] else '✗'} {'exact' if r['exact'] else 'has_λ' if r['has_lambda'] else 'MISS'}")

    # ── Save results ──
    results = {
        "experiment": "computed_beam",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_s": elapsed,
        "eigenvalues": [float(x) for x in eigen["eigvals"]],
        "rotation_angle_predicted": float(eigen["rotation_angle"]),
        "evaluations": {ev["label"]: {
            "ce": ev["ce"],
            "crystal_loss": ev["crystal_loss"],
            "comp_cluster": ev["comp_cluster"],
        } for ev, _ in rows},
        "generations": {ev["label"]: {
            "p_lambda": gen["p_lambda"],
            "n_exact": gen["n_exact"],
        } for ev, gen in rows},
    }

    results_path = Path("results/computed-beam")
    results_path.mkdir(parents=True, exist_ok=True)
    with open(results_path / "results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to {results_path / 'results.json'}")


if __name__ == "__main__":
    main()
