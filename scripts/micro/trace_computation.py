"""
Trace Computation — Reverse-engineer the micro model's algorithm.

Loads a trained micro model and traces one forward + backward pass
to map how gradients relate to beta-reduction selections.

Three analyses:
  1. FORWARD TRACE: Q rotations, attention patterns, FFN overlay,
     residual stream decomposition at every layer
  2. BACKWARD TRACE: gradient projected into crystal eigenbasis,
     per-layer gradient decomposition by crystal PC
  3. FFN OVERLAY ANALYSIS: extract the "inference pattern" from FFN
     weights in crystal coordinates — what does the diffraction
     grating look like?

Usage:
    cd verbum
    uv run python scripts/micro/trace_computation.py [checkpoint_dir]

If no checkpoint, uses untrained model (for structure verification).

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
    COMBINATOR_NAMES, ANTI_COMBINATOR_NAMES,
    N_COMBINATORS,
)


# ══════════════════════════════════════════════════════════════════════
# Crystal eigenbasis tools
# ══════════════════════════════════════════════════════════════════════


def get_crystal_eigenbasis() -> tuple[np.ndarray, np.ndarray]:
    """Get the Zone B crystal eigenbasis (sorted by eigenvalue descending).

    Returns:
        eigvecs: (16, 16) — columns are eigenvectors
        eigvals: (16,) — eigenvalues sorted descending
    """
    data = _precompute_parity_eigenbasis(PCAQ_ZONE_B_TARGETS)
    return data["eigvecs"], data["eigvals"]


def project_to_crystal(
    tensor: np.ndarray,
    crystal_emb: np.ndarray,
) -> np.ndarray:
    """Project a (d_model,) or (..., d_model) tensor into crystal space.

    crystal_emb: (16, d_model) — the 16 combinator embeddings (normalized)
    Returns: (..., 16) — projection coefficients onto each combinator direction.
    """
    # Normalize crystal embeddings
    norms = np.linalg.norm(crystal_emb, axis=1, keepdims=True) + 1e-8
    crystal_norm = crystal_emb / norms
    # Project: tensor @ crystal_norm.T
    return tensor @ crystal_norm.T


def project_gradient_to_crystal_eigenbasis(
    grad: np.ndarray,
    crystal_emb: np.ndarray,
    eigvecs: np.ndarray,
) -> np.ndarray:
    """Project gradient first to crystal space, then to eigenbasis.

    Returns: (..., 16) in the eigendecomposed crystal coordinate system.
    PC0 = composition/selection axis, PC1 = selection polarity, etc.
    """
    crystal_proj = project_to_crystal(grad, crystal_emb)
    return crystal_proj @ eigvecs  # rotate into eigenbasis


# ══════════════════════════════════════════════════════════════════════
# Forward trace
# ══════════════════════════════════════════════════════════════════════


def trace_forward(
    model: MicroModel,
    input_ids: mx.array,
    targets: mx.array,
    tokenizer=None,
) -> dict:
    """Run forward pass with full trace capture.

    Returns dict with:
      - per-layer Q/K/V projections, attention weights, FFN activations
      - residual stream at every layer boundary
      - logits and loss
      - crystal embeddings state
    """
    model.set_capture(True)
    logits, loss = model(input_ids, targets)
    mx.eval(logits, loss)

    traces = model.get_traces()
    model.set_capture(False)

    # Evaluate all trace tensors
    for layer_trace in traces:
        for section in ["block", "attn", "ffn"]:
            for k, v in layer_trace[section].items():
                if isinstance(v, mx.array):
                    mx.eval(v)

    # Crystal state
    crystal_emb = model.get_all_crystal_embeddings()
    mx.eval(crystal_emb)

    result = {
        "logits": logits,
        "loss": float(loss.item()),
        "traces": traces,
        "crystal_emb": np.array(crystal_emb),
        "ce_loss": float(model._last_ce_loss.item()),
        "crystal_loss": float(model._last_crystal_loss.item()),
    }

    if tokenizer is not None:
        result["input_text"] = tokenizer.decode(input_ids[0].tolist())
        result["target_tokens"] = targets[0].tolist()

    return result


# ══════════════════════════════════════════════════════════════════════
# Backward trace
# ══════════════════════════════════════════════════════════════════════


def trace_backward(
    model: MicroModel,
    input_ids: mx.array,
    targets: mx.array,
) -> dict:
    """Run backward pass and capture all gradients.

    Returns dict with:
      - per-parameter gradients
      - gradients projected into crystal eigenbasis
      - per-layer gradient magnitude decomposition
    """

    def loss_fn(m, inp, tgt):
        _, loss = m(inp, tgt)
        return loss

    grad_fn = nn.value_and_grad(model, loss_fn)
    loss_val, grads = grad_fn(model, input_ids, targets)
    mx.eval(loss_val, grads)

    # Get crystal embeddings and eigenbasis
    crystal_emb = np.array(model.get_all_crystal_embeddings())
    eigvecs, eigvals = get_crystal_eigenbasis()

    # Flatten gradient tree and analyze each parameter
    flat_grads = dict(nn.utils.tree_flatten(grads))

    # Per-layer gradient analysis
    layer_analysis = []
    for layer_idx in range(model.cfg.n_layers):
        prefix = f"blocks.{layer_idx}"
        layer_grads = {
            k.replace(prefix + ".", ""): np.array(v)
            for k, v in flat_grads.items()
            if k.startswith(prefix)
        }

        # Total gradient magnitude per component
        component_norms = {}
        for k, v in layer_grads.items():
            component_norms[k] = float(np.linalg.norm(v))

        # Project attention Q gradients into crystal space
        q_crystal_proj = None
        q_key = "attn.q_proj.weight"
        if q_key in layer_grads:
            q_grad = layer_grads[q_key]  # (d_model, d_model)
            # Each row of Q grad is a gradient for one output dimension
            # Project into crystal space to see which combinator directions
            # get the most gradient signal
            q_crystal_proj = project_to_crystal(q_grad, crystal_emb)  # (d_model, 16)
            q_crystal_eigenbasis = q_crystal_proj @ eigvecs  # (d_model, 16)

            # Summarize: magnitude per crystal PC across all output dims
            pc_magnitudes = np.linalg.norm(q_crystal_eigenbasis, axis=0)  # (16,)
        else:
            pc_magnitudes = np.zeros(16)

        # Project FFN gate gradients into crystal space
        gate_crystal_proj = None
        gate_key = "ffn.gate_proj.weight"
        if gate_key in layer_grads:
            gate_grad = layer_grads[gate_key]  # (d_ff, d_model)
            gate_crystal_proj = project_to_crystal(gate_grad, crystal_emb)  # (d_ff, 16)
            gate_pc_magnitudes = np.linalg.norm(
                gate_crystal_proj @ eigvecs, axis=0)  # (16,)
        else:
            gate_pc_magnitudes = np.zeros(16)

        # Project FFN key gradients into crystal space
        key_crystal_proj = None
        key_key = "ffn.key_proj.weight"
        if key_key in layer_grads:
            key_grad = layer_grads[key_key]  # (d_ff, d_model)
            key_crystal_proj = project_to_crystal(key_grad, crystal_emb)  # (d_ff, 16)
            key_pc_magnitudes = np.linalg.norm(
                key_crystal_proj @ eigvecs, axis=0)  # (16,)
        else:
            key_pc_magnitudes = np.zeros(16)

        layer_analysis.append({
            "layer": layer_idx,
            "component_norms": component_norms,
            "q_pc_magnitudes": pc_magnitudes.tolist(),
            "gate_pc_magnitudes": gate_pc_magnitudes.tolist(),
            "key_pc_magnitudes": key_pc_magnitudes.tolist(),
        })

    # Crystal embedding gradients directly
    crystal_grad = None
    for k, v in flat_grads.items():
        if "combinator_embeddings" in k and "anti" not in k:
            crystal_grad = np.array(v)
            break

    anti_crystal_grad = None
    for k, v in flat_grads.items():
        if "anti_combinator_embeddings" in k:
            anti_crystal_grad = np.array(v)
            break

    return {
        "loss": float(loss_val.item()),
        "layer_analysis": layer_analysis,
        "crystal_grad": crystal_grad,
        "anti_crystal_grad": anti_crystal_grad,
        "eigvecs": eigvecs,
        "eigvals": eigvals,
    }


# ══════════════════════════════════════════════════════════════════════
# FFN overlay analysis
# ══════════════════════════════════════════════════════════════════════


def analyze_ffn_overlay(model: MicroModel) -> list[dict]:
    """Extract the FFN 'inference pattern' in crystal coordinates.

    The FFN doesn't store data — it stores the inference pattern that,
    when overlaid onto the crystal lattice, shows attention what
    rotations it needs for the next step.

    For each layer's FFN:
      1. Project gate_proj weights into crystal space → which combinator
         directions does each neuron respond to?
      2. Project key_proj weights into crystal space → what content does
         each neuron provide?
      3. Project value_proj weights into crystal space → what direction
         does each neuron write back?
      4. The overlay pattern = gate_crystal × value_crystal → what the
         FFN writes as a function of crystal input direction
    """
    crystal_emb = np.array(model.get_all_crystal_embeddings())
    eigvecs, eigvals = get_crystal_eigenbasis()

    # Normalize crystal embeddings
    norms = np.linalg.norm(crystal_emb, axis=1, keepdims=True) + 1e-8
    crystal_norm = crystal_emb / norms

    layer_overlays = []
    for layer_idx, block in enumerate(model.blocks):
        ffn = block.ffn

        # Gate weights: (d_ff, d_model) — "which neurons fire for which input direction"
        gate_w = np.array(ffn.gate_proj.weight)  # (d_ff, d_model)
        # Project input side into crystal space
        gate_crystal = gate_w @ crystal_norm.T  # (d_ff, 16)
        gate_eigen = gate_crystal @ eigvecs  # (d_ff, 16) in eigenbasis

        # Key weights: (d_ff, d_model) — "what content each neuron holds"
        key_w = np.array(ffn.key_proj.weight)
        key_crystal = key_w @ crystal_norm.T
        key_eigen = key_crystal @ eigvecs

        # Value weights: (d_model, d_ff) — "what each neuron writes back"
        value_w = np.array(ffn.value_proj.weight)  # (d_model, d_ff)
        # Project output side into crystal space
        value_crystal = crystal_norm @ value_w  # (16, d_ff)
        value_eigen = eigvecs.T @ value_crystal  # (16, d_ff) in eigenbasis

        # The OVERLAY MATRIX: how crystal-input maps to crystal-output through FFN
        # gate_eigen.T @ value_eigen.T → (16, 16) in eigenbasis
        # This is the "diffraction grating" in crystal coordinates
        # overlay[i, j] = how much PC_i input produces PC_j output
        overlay = gate_eigen.T @ value_eigen.T  # (16, 16)

        # Neuron selectivity: which neurons are most selective for specific PCs
        gate_selectivity = np.argmax(np.abs(gate_eigen), axis=1)  # (d_ff,)
        gate_max_pc = np.bincount(gate_selectivity, minlength=16)

        # Top neurons per PC (which neurons fire most strongly for each PC)
        top_neurons_per_pc = {}
        for pc in range(min(8, gate_eigen.shape[1])):
            scores = np.abs(gate_eigen[:, pc])
            top_idx = np.argsort(scores)[-5:][::-1]
            top_neurons_per_pc[f"PC{pc}"] = {
                "neuron_ids": top_idx.tolist(),
                "scores": scores[top_idx].tolist(),
            }

        layer_overlays.append({
            "layer": layer_idx,
            "overlay_matrix": overlay.tolist(),
            "overlay_diag": np.diag(overlay).tolist(),
            "overlay_off_diag_norm": float(np.linalg.norm(
                overlay - np.diag(np.diag(overlay)))),
            "gate_pc_distribution": gate_max_pc.tolist(),
            "top_neurons_per_pc": top_neurons_per_pc,
            "gate_sparsity": float(np.mean(np.abs(gate_eigen) < 0.01)),
        })

    return layer_overlays


# ══════════════════════════════════════════════════════════════════════
# Attention Q-rotation analysis
# ══════════════════════════════════════════════════════════════════════


def analyze_q_rotations(forward_trace: dict) -> list[dict]:
    """Analyze how Q projections rotate the residual into crystal basins.

    For each layer, each head:
      - What direction does Q project the residual into?
      - How does that direction relate to crystal PCs?
      - Does the attention pattern show basin selection?
    """
    crystal_emb = forward_trace["crystal_emb"]
    eigvecs, _ = get_crystal_eigenbasis()

    norms = np.linalg.norm(crystal_emb, axis=1, keepdims=True) + 1e-8
    crystal_norm = crystal_emb / norms

    results = []
    for layer_trace in forward_trace["traces"]:
        layer_idx = layer_trace["layer"]
        attn = layer_trace["attn"]

        q = np.array(attn["q"])  # (B, H, L, d_head)
        k = np.array(attn["k"])
        attn_weights = np.array(attn["attn_weights"])  # (B, H, L, L)

        B, H, L, D = q.shape

        head_analyses = []
        for h in range(H):
            # Q vectors for this head (first batch item)
            q_h = q[0, h]  # (L, d_head)
            k_h = k[0, h]  # (L, d_head)

            # Attention pattern entropy (how selective is this head?)
            attn_h = attn_weights[0, h]  # (L, L)
            # Per-query entropy
            eps = 1e-10
            entropy = -np.sum(attn_h * np.log(attn_h + eps), axis=-1)
            mean_entropy = float(np.mean(entropy))
            max_attn = float(np.mean(np.max(attn_h, axis=-1)))

            head_analyses.append({
                "head": h,
                "mean_entropy": mean_entropy,
                "mean_max_attn": max_attn,
                "q_norm_mean": float(np.mean(np.linalg.norm(q_h, axis=-1))),
                "k_norm_mean": float(np.mean(np.linalg.norm(k_h, axis=-1))),
            })

        results.append({
            "layer": layer_idx,
            "heads": head_analyses,
        })

    return results


# ══════════════════════════════════════════════════════════════════════
# Main analysis
# ══════════════════════════════════════════════════════════════════════


def run_analysis(checkpoint_dir: str | None = None):
    """Run full forward + backward trace analysis."""

    print("=" * 70)
    print("MICRO MODEL COMPUTATION TRACE")
    print("=" * 70)

    cfg = MicroConfig()
    model = MicroModel(cfg)
    mx.eval(model.parameters())

    # Load checkpoint if provided
    if checkpoint_dir is not None:
        ckpt_path = Path(checkpoint_dir) / "model.npz"
        if ckpt_path.exists():
            print(f"\nLoading checkpoint: {ckpt_path}")
            weights = mx.load(str(ckpt_path))
            # Unflatten and load
            model.load_weights(list(weights.items()))
            mx.eval(model.parameters())
            print("  Loaded ✓")
        else:
            print(f"\n⚠ Checkpoint not found: {ckpt_path}")
            print("  Using untrained model (structure verification mode)")
    else:
        print("\nNo checkpoint provided — using untrained model")

    # Tokenizer
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")

    # ── Pick a compile example ──
    example_text = "The cat sits.\nλx. sits(cat)"
    tokens = tokenizer.encode(example_text, add_special_tokens=False)
    tokens.append(cfg.eod_id)
    input_ids = mx.array([tokens[:-1]])
    targets = mx.array([tokens[1:]])

    print(f"\nExample: {example_text}")
    print(f"Tokens: {tokens}")
    print(f"Sequence length: {len(tokens)}")

    # ═══════════════════════════════════════════════════════
    # 1. FORWARD TRACE
    # ═══════════════════════════════════════════════════════
    print("\n" + "═" * 70)
    print("1. FORWARD TRACE")
    print("═" * 70)

    fwd = trace_forward(model, input_ids, targets, tokenizer)
    print(f"  Loss: {fwd['loss']:.4f} (CE: {fwd['ce_loss']:.4f}, Crystal: {fwd['crystal_loss']:.6f})")

    # Residual stream analysis
    print("\n  Residual stream (per-layer contributions):")
    for layer_trace in fwd["traces"]:
        layer = layer_trace["layer"]
        block = layer_trace["block"]
        if "attn_contribution" in block and "ffn_contribution" in block:
            attn_norm = float(np.linalg.norm(np.array(block["attn_contribution"])))
            ffn_norm = float(np.linalg.norm(np.array(block["ffn_contribution"])))
            ratio = ffn_norm / (attn_norm + 1e-8)
            print(f"    Layer {layer}: attn={attn_norm:.3f}, ffn={ffn_norm:.3f}, ffn/attn={ratio:.2f}")

    # FFN gate sparsity
    print("\n  FFN gate sparsity (fraction of near-zero neurons):")
    for layer_trace in fwd["traces"]:
        layer = layer_trace["layer"]
        ffn = layer_trace["ffn"]
        if "gate_sparsity" in ffn:
            print(f"    Layer {layer}: {float(np.array(ffn['gate_sparsity'])):.3f}")

    # ═══════════════════════════════════════════════════════
    # 2. Q-ROTATION ANALYSIS
    # ═══════════════════════════════════════════════════════
    print("\n" + "═" * 70)
    print("2. Q-ROTATION ANALYSIS")
    print("═" * 70)

    q_analysis = analyze_q_rotations(fwd)
    for layer_result in q_analysis:
        layer = layer_result["layer"]
        print(f"\n  Layer {layer}:")
        for head in layer_result["heads"]:
            h = head["head"]
            print(f"    Head {h}: entropy={head['mean_entropy']:.3f}, "
                  f"max_attn={head['mean_max_attn']:.3f}, "
                  f"q_norm={head['q_norm_mean']:.3f}")

    # ═══════════════════════════════════════════════════════
    # 3. BACKWARD TRACE
    # ═══════════════════════════════════════════════════════
    print("\n" + "═" * 70)
    print("3. BACKWARD TRACE — Gradient → Crystal Eigenbasis")
    print("═" * 70)

    bwd = trace_backward(model, input_ids, targets)
    print(f"  Loss: {bwd['loss']:.4f}")

    # Per-layer gradient in crystal eigenbasis
    print("\n  Q-projection gradient magnitude per crystal PC:")
    print(f"  {'Layer':>5} | {'PC0 comp':>8} {'PC1 sel':>8} {'PC2 term':>8} "
          f"{'PC3 rout':>8} {'PC4 fine':>8} {'PC5':>8}")
    print(f"  {'':>5} | {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*8}")
    for la in bwd["layer_analysis"]:
        pcs = la["q_pc_magnitudes"][:6]
        layer = la["layer"]
        print(f"  {layer:>5} | " + " ".join(f"{pc:8.4f}" for pc in pcs))

    print("\n  FFN gate gradient magnitude per crystal PC:")
    print(f"  {'Layer':>5} | {'PC0 comp':>8} {'PC1 sel':>8} {'PC2 term':>8} "
          f"{'PC3 rout':>8} {'PC4 fine':>8} {'PC5':>8}")
    print(f"  {'':>5} | {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*8}")
    for la in bwd["layer_analysis"]:
        pcs = la["gate_pc_magnitudes"][:6]
        layer = la["layer"]
        print(f"  {layer:>5} | " + " ".join(f"{pc:8.4f}" for pc in pcs))

    # Crystal embedding gradients
    if bwd["crystal_grad"] is not None:
        print("\n  Crystal embedding gradients (per combinator):")
        cg = bwd["crystal_grad"]  # (8, d_model)
        for i in range(N_COMBINATORS):
            name = COMBINATOR_NAMES[i]
            gnorm = float(np.linalg.norm(cg[i]))
            print(f"    {name:>4}: grad_norm={gnorm:.6f}")

    # ═══════════════════════════════════════════════════════
    # 4. FFN OVERLAY ANALYSIS
    # ═══════════════════════════════════════════════════════
    print("\n" + "═" * 70)
    print("4. FFN OVERLAY — The Inference Pattern (Diffraction Grating)")
    print("═" * 70)

    overlays = analyze_ffn_overlay(model)
    for ov in overlays:
        layer = ov["layer"]
        print(f"\n  Layer {layer}:")
        print(f"    Overlay diagonal (PC_in → PC_out, same-PC transmission):")
        diag = ov["overlay_diag"][:8]
        labels = ["comp", "sel", "term", "rout", "fine", "PC5", "PC6", "PC7"]
        for i, (d, l) in enumerate(zip(diag, labels)):
            bar = "█" * int(abs(d) * 2) if abs(d) > 0.1 else "·"
            sign = "+" if d > 0 else "-"
            print(f"      PC{i}({l:>4}): {sign}{abs(d):6.3f} {bar}")

        print(f"    Off-diagonal norm: {ov['overlay_off_diag_norm']:.4f}")
        print(f"    Gate PC distribution (neurons per PC): "
              f"{ov['gate_pc_distribution'][:8]}")

    # ═══════════════════════════════════════════════════════
    # 5. GRADIENT → β-REDUCTION MAPPING
    # ═══════════════════════════════════════════════════════
    print("\n" + "═" * 70)
    print("5. GRADIENT → β-REDUCTION MAPPING")
    print("═" * 70)

    print("\n  Hypothesis: gradient in crystal eigenbasis selects β-reductions")
    print("  PC0 (composition) → B combinator → chain operations")
    print("  PC1 (selection)   → K combinator → select/discard")
    print("  PC2 (termination) → WHNF → stop reducing")
    print("  PC3 (routing)     → C combinator → reorder args")

    print("\n  Per-layer dominant gradient direction:")
    for la in bwd["layer_analysis"]:
        layer = la["layer"]
        q_pcs = np.array(la["q_pc_magnitudes"][:8])
        gate_pcs = np.array(la["gate_pc_magnitudes"][:8])

        q_dom = int(np.argmax(q_pcs))
        gate_dom = int(np.argmax(gate_pcs))

        pc_names = ["comp(B)", "sel(K)", "term(WHNF)", "rout(C)",
                     "fine(D)", "rec(Y)", "dup(W)", "PC7"]

        print(f"    Layer {layer}: "
              f"Q→PC{q_dom}({pc_names[q_dom]}), "
              f"Gate→PC{gate_dom}({pc_names[gate_dom]})")
        print(f"      Q:    {' '.join(f'{v:5.3f}' for v in q_pcs)}")
        print(f"      Gate: {' '.join(f'{v:5.3f}' for v in gate_pcs)}")

    # ═══════════════════════════════════════════════════════
    # 6. LOGIT DECOMPOSITION
    # ═══════════════════════════════════════════════════════
    print("\n" + "═" * 70)
    print("6. LOGIT DECOMPOSITION — The Photograph")
    print("═" * 70)

    logits = np.array(fwd["logits"])  # (1, L, vocab)
    # Top-5 predictions at each position
    print(f"\n  Top predictions at each position:")
    seq_len = logits.shape[1]
    for pos in range(min(seq_len, 20)):
        pos_logits = logits[0, pos]
        top5_idx = np.argsort(pos_logits)[-5:][::-1]
        top5_tokens = [tokenizer.decode([int(idx)]) for idx in top5_idx]
        top5_probs = np.exp(pos_logits[top5_idx]) / np.sum(np.exp(pos_logits[top5_idx]))
        actual_token = tokenizer.decode([targets[0, pos].item()]) if pos < targets.shape[1] else "?"
        pred_str = ", ".join(f"'{t}':{p:.2f}" for t, p in zip(top5_tokens, top5_probs))
        print(f"    pos {pos:2d} (→'{actual_token}'): {pred_str}")

    print("\n" + "═" * 70)
    print("TRACE COMPLETE")
    print("═" * 70)


# ══════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    ckpt = sys.argv[1] if len(sys.argv) > 1 else None
    run_analysis(ckpt)
