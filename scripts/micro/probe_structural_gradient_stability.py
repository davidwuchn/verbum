"""
Probe Structural Gradient Stability — Can we precompute the structural gradient?

THE QUESTION: The composed grating is rank-1 and determined by ternary
weights (which only change at TD flips every 20 steps). If the gradient
component in the crystal eigenplane (the "structural gradient") stays
constant across training steps, we can precompute it once and reuse it
for 20 steps — getting the structural training signal for free.

Measurements:
  1. Compute full gradients on multiple different batches
  2. Project each gradient into crystal eigenplane (structural) and
     orthogonal complement (content)
  3. Measure cosine similarity of structural gradients across batches
     → if high (>0.9), the structural gradient is stable
  4. Measure cosine similarity of content gradients across batches
     → should be lower (content varies with input)
  5. Measure the fraction of gradient energy in structural vs content
  6. Compare: full gradient training vs content-only vs structural-only
     → which component matters more for loss reduction?

Uses the micro model where we can run many fast experiments.

Usage:
    cd verbum
    uv run python scripts/micro/probe_structural_gradient_stability.py [checkpoint_dir]

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


def get_crystal_eigenbasis() -> tuple[np.ndarray, np.ndarray]:
    data = _precompute_parity_eigenbasis(PCAQ_ZONE_B_TARGETS)
    return data["eigvecs"], data["eigvals"]


def load_examples(path: str, n: int = 100) -> list[dict]:
    examples = []
    with open(path) as f:
        for line in f:
            examples.append(json.loads(line))
            if len(examples) >= n:
                break
    return examples


def compute_gradient(model, input_ids, targets):
    """Compute gradient of all parameters."""
    def loss_fn(m, inp, tgt):
        _, loss = m(inp, tgt)
        return loss

    grad_fn = nn.value_and_grad(model, loss_fn)
    loss_val, grads = grad_fn(model, input_ids, targets)
    mx.eval(loss_val, grads)
    return float(loss_val.item()), grads


def flatten_attention_grads(grads, n_layers) -> np.ndarray:
    """Extract and flatten just the attention parameter gradients."""
    flat = dict(nn.utils.tree_flatten(grads))
    vectors = []
    for layer in range(n_layers):
        for proj in ["q_proj", "k_proj", "v_proj", "o_proj"]:
            key = f"blocks.{layer}.attn.{proj}.weight"
            if key in flat:
                vectors.append(np.array(flat[key]).flatten())
    return np.concatenate(vectors)


def project_gradient_structural_content(
    grad_vector: np.ndarray,
    structural_basis: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Split gradient into structural (in-plane) and content (out-of-plane).

    structural_basis: (k, n) — k basis vectors of the structural subspace
    grad_vector: (n,) — the gradient
    Returns: (structural_component, content_component)
    """
    # Project onto structural basis
    # structural = sum_i (grad · basis_i) * basis_i
    coeffs = structural_basis @ grad_vector  # (k,)
    structural = structural_basis.T @ coeffs  # (n,)
    content = grad_vector - structural
    return structural, content


def build_structural_basis(
    model: MicroModel,
    crystal_emb: np.ndarray,
    eigvecs: np.ndarray,
    n_structural_pcs: int = 2,
) -> np.ndarray:
    """Build the structural basis for attention gradient projection.

    The structural subspace is defined by the crystal eigenplane (comp↔sel).
    For attention weights, this is the subspace where the gradient pushes
    Q/K/V projections toward/away from crystal basin directions.

    We build basis vectors in the flattened attention-gradient space that
    correspond to the top-k crystal PCs.
    """
    norms = np.linalg.norm(crystal_emb, axis=1, keepdims=True) + 1e-8
    crystal_norm = crystal_emb / norms

    # Crystal directions in model space: top PCs projected through embeddings
    crystal_dirs = eigvecs[:, :n_structural_pcs].T @ crystal_norm  # (k, d_model)
    # Normalize
    for i in range(n_structural_pcs):
        crystal_dirs[i] /= np.linalg.norm(crystal_dirs[i]) + 1e-8

    # For each attention weight matrix (d_model × d_model), the structural
    # directions are outer products of crystal_dirs with themselves
    # But that makes a huge basis. Simpler: project each weight's gradient
    # row-by-row into crystal space.

    # Actually, the simplest approach: for each attention weight's flattened
    # gradient, the "structural" part is the component along crystal directions.
    # We can do this per-weight-matrix.

    # Build block-diagonal basis: for each weight matrix, the crystal
    # directions act on the input dimension.
    d = model.cfg.d_model
    n_layers = model.cfg.n_layers
    n_projections = 4  # q, k, v, o per layer
    total_params = n_layers * n_projections * d * d

    basis_vectors = []
    for layer in range(n_layers):
        for proj_idx in range(n_projections):
            offset = (layer * n_projections + proj_idx) * d * d
            for pc in range(n_structural_pcs):
                # This basis vector is: for this weight matrix, the crystal
                # direction on the input axis, broadcast across output dims
                bv = np.zeros(total_params)
                crystal_dir = crystal_dirs[pc]  # (d_model,)
                # The structural direction is: each row of the weight matrix
                # should have a component along crystal_dir
                # Simplified: just use crystal_dir tiled across rows
                for row in range(d):
                    bv[offset + row * d: offset + (row + 1) * d] = crystal_dir
                norm = np.linalg.norm(bv)
                if norm > 1e-8:
                    basis_vectors.append(bv / norm)

    # Orthogonalize via Gram-Schmidt
    orthogonal = []
    for bv in basis_vectors:
        for ob in orthogonal:
            bv = bv - np.dot(bv, ob) * ob
        norm = np.linalg.norm(bv)
        if norm > 1e-6:
            orthogonal.append(bv / norm)

    return np.array(orthogonal)  # (k_eff, total_params)


def main():
    checkpoint_dir = sys.argv[1] if len(sys.argv) > 1 else "checkpoints/micro/final"
    checkpoint_path = Path(checkpoint_dir)
    if not checkpoint_path.exists():
        checkpoint_path = Path(__file__).parent.parent.parent / checkpoint_dir
    assert checkpoint_path.exists(), f"Not found: {checkpoint_path}"

    results_dir = Path(__file__).parent.parent.parent / "results" / "structural-gradient"
    results_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("Structural Gradient Stability Probe")
    print("=" * 70)

    # ── Load model ──
    cfg = MicroConfig()
    model = MicroModel(cfg)
    weights = mx.load(str(checkpoint_path / "model.npz"))
    model.load_weights(list(weights.items()))
    mx.eval(model.parameters())

    crystal_emb = np.array(model.get_all_crystal_embeddings())
    eigvecs, eigvals = get_crystal_eigenbasis()

    # ── Build structural basis ──
    print("\nBuilding structural basis...")
    structural_basis = build_structural_basis(model, crystal_emb, eigvecs, n_structural_pcs=2)
    print(f"  Structural basis: {structural_basis.shape[0]} orthogonal vectors "
          f"in {structural_basis.shape[1]}-dimensional gradient space")

    # ── Load data ──
    try:
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B", trust_remote_code=True)
    except Exception:
        tokenizer = None

    data_path = Path(__file__).parent.parent.parent / "data" / "compile-eval.jsonl"
    if not data_path.exists():
        data_path = Path(__file__).parent.parent.parent / "data" / "compile-test.jsonl"
    examples = load_examples(str(data_path), n=20)

    # ── Compute gradients on different batches ──
    print(f"\nComputing gradients on {len(examples)} different inputs...")

    all_structural = []
    all_content = []
    all_full = []
    all_losses = []

    for ex_idx, example in enumerate(examples):
        if tokenizer:
            text = example["input"] + "\n" + example["output"]
            tokens = tokenizer.encode(text)
            if len(tokens) > 128:
                tokens = tokens[:128]
            input_ids = mx.array([tokens[:-1]])
            targets = mx.array([tokens[1:]])
        else:
            text = example["input"] + "\n" + example["output"]
            tokens = [ord(c) % 1000 for c in text]
            input_ids = mx.array([tokens[:-1]])
            targets = mx.array([tokens[1:]])

        loss, grads = compute_gradient(model, input_ids, targets)
        all_losses.append(loss)

        # Flatten attention gradients
        flat_grad = flatten_attention_grads(grads, cfg.n_layers)

        # Pad or truncate to match structural basis dimension
        target_dim = structural_basis.shape[1]
        if len(flat_grad) < target_dim:
            flat_grad = np.pad(flat_grad, (0, target_dim - len(flat_grad)))
        elif len(flat_grad) > target_dim:
            flat_grad = flat_grad[:target_dim]

        # Split into structural and content
        structural, content = project_gradient_structural_content(
            flat_grad, structural_basis)

        all_full.append(flat_grad)
        all_structural.append(structural)
        all_content.append(content)

        if ex_idx == 0:
            s_energy = np.sum(structural ** 2)
            c_energy = np.sum(content ** 2)
            total = s_energy + c_energy
            print(f"  Example 0: loss={loss:.4f}, "
                  f"structural={s_energy/total:.1%}, content={c_energy/total:.1%}")

    # ── Compute pairwise cosine similarities ──
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    def pairwise_cosine(vectors):
        """Mean pairwise cosine similarity."""
        n = len(vectors)
        cosines = []
        for i in range(n):
            for j in range(i + 1, n):
                ni = np.linalg.norm(vectors[i])
                nj = np.linalg.norm(vectors[j])
                if ni > 1e-8 and nj > 1e-8:
                    cosines.append(float(np.dot(vectors[i], vectors[j]) / (ni * nj)))
        return cosines

    full_cosines = pairwise_cosine(all_full)
    struct_cosines = pairwise_cosine(all_structural)
    content_cosines = pairwise_cosine(all_content)

    print(f"\n1. GRADIENT STABILITY (pairwise cosine across {len(examples)} batches)")
    print(f"   Full gradient:        cos = {np.mean(full_cosines):+.4f} ± {np.std(full_cosines):.4f}")
    print(f"   Structural component: cos = {np.mean(struct_cosines):+.4f} ± {np.std(struct_cosines):.4f}")
    print(f"   Content component:    cos = {np.mean(content_cosines):+.4f} ± {np.std(content_cosines):.4f}")

    if np.mean(struct_cosines) > np.mean(content_cosines):
        print(f"   ✓ Structural gradient is MORE stable than content ({np.mean(struct_cosines):.4f} > {np.mean(content_cosines):.4f})")
    else:
        print(f"   ✗ Structural gradient is LESS stable than content")

    # ── Energy decomposition ──
    struct_energies = [np.sum(s**2) for s in all_structural]
    content_energies = [np.sum(c**2) for c in all_content]
    total_energies = [se + ce for se, ce in zip(struct_energies, content_energies)]
    struct_fracs = [se / (te + 1e-12) for se, te in zip(struct_energies, total_energies)]
    content_fracs = [ce / (te + 1e-12) for ce, te in zip(content_energies, total_energies)]

    print(f"\n2. ENERGY DECOMPOSITION")
    print(f"   Structural fraction: {np.mean(struct_fracs):.1%} ± {np.std(struct_fracs):.1%}")
    print(f"   Content fraction:    {np.mean(content_fracs):.1%} ± {np.std(content_fracs):.1%}")

    # ── Direction stability: does the structural gradient point the SAME WAY? ──
    # Compute the mean structural gradient (the "template")
    mean_structural = np.mean(all_structural, axis=0)
    mean_structural_norm = mean_structural / (np.linalg.norm(mean_structural) + 1e-12)

    # How well does each example's structural gradient align with the template?
    template_cosines = []
    for s in all_structural:
        n = np.linalg.norm(s)
        if n > 1e-8:
            template_cosines.append(float(np.dot(s / n, mean_structural_norm)))
        else:
            template_cosines.append(0.0)

    print(f"\n3. TEMPLATE ALIGNMENT (each batch vs mean structural)")
    print(f"   cos(batch_structural, template): {np.mean(template_cosines):+.4f} ± {np.std(template_cosines):.4f}")
    if np.mean(template_cosines) > 0.9:
        print(f"   ✓ STABLE — structural gradient is nearly identical across batches")
        print(f"   → Can precompute once, reuse for ~20 steps")
    elif np.mean(template_cosines) > 0.7:
        print(f"   ~ MODERATELY STABLE — some variation but mostly consistent")
        print(f"   → Precomputed gradient would capture 70%+ of structural signal")
    else:
        print(f"   ✗ UNSTABLE — structural gradient varies by batch")
        print(f"   → Cannot precompute; need per-batch structural gradient")

    # ── What does the structural gradient LOOK like? ──
    print(f"\n4. STRUCTURAL GRADIENT DIRECTION")
    # Project mean structural gradient back through the basis to see crystal PC coefficients
    struct_coeffs = structural_basis @ mean_structural
    print(f"   Crystal PC coefficients of mean structural gradient:")
    pc_per_layer = 2  # n_structural_pcs
    for layer in range(cfg.n_layers):
        for proj_idx, proj_name in enumerate(["Q", "K", "V", "O"]):
            base = (layer * 4 + proj_idx) * pc_per_layer
            if base + pc_per_layer <= len(struct_coeffs):
                c = struct_coeffs[base:base + pc_per_layer]
                print(f"     L{layer}.{proj_name}: PC0(comp)={c[0]:+.4f} PC1(sel)={c[1]:+.4f}")

    # ── Content gradient: how much does it vary? ──
    mean_content = np.mean(all_content, axis=0)
    mean_content_norm = mean_content / (np.linalg.norm(mean_content) + 1e-12)
    content_template_cosines = []
    for c in all_content:
        n = np.linalg.norm(c)
        if n > 1e-8:
            content_template_cosines.append(float(np.dot(c / n, mean_content_norm)))
        else:
            content_template_cosines.append(0.0)

    print(f"\n5. CONTENT GRADIENT STABILITY (for comparison)")
    print(f"   cos(batch_content, template): {np.mean(content_template_cosines):+.4f} ± {np.std(content_template_cosines):.4f}")

    # ── Summary ──
    print(f"\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    s_stable = np.mean(struct_cosines)
    c_stable = np.mean(content_cosines)
    s_frac = np.mean(struct_fracs)
    print(f"  Structural stability:  {s_stable:+.4f} (pairwise cos)")
    print(f"  Content stability:     {c_stable:+.4f} (pairwise cos)")
    print(f"  Structural energy:     {s_frac:.1%}")
    print(f"  Separation ratio:      {s_stable / (c_stable + 1e-8):.2f}× "
          f"({'structural MORE stable' if s_stable > c_stable else 'content MORE stable'})")

    # ── Save ──
    summary = {
        "n_examples": len(examples),
        "structural_basis_dim": int(structural_basis.shape[0]),
        "full_gradient_cosine": {"mean": float(np.mean(full_cosines)), "std": float(np.std(full_cosines))},
        "structural_cosine": {"mean": float(np.mean(struct_cosines)), "std": float(np.std(struct_cosines))},
        "content_cosine": {"mean": float(np.mean(content_cosines)), "std": float(np.std(content_cosines))},
        "structural_energy_frac": {"mean": float(np.mean(struct_fracs)), "std": float(np.std(struct_fracs))},
        "template_alignment": {"mean": float(np.mean(template_cosines)), "std": float(np.std(template_cosines))},
        "content_template_alignment": {"mean": float(np.mean(content_template_cosines)), "std": float(np.std(content_template_cosines))},
    }

    out_path = results_dir / "summary.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
