"""
Deep Trace — Full mechanism extraction from the micro model.

Traces the complete computation in crystal coordinates:
  1. Residual trajectory: track the hidden state in crystal eigenbasis
     through every layer boundary — watch it move between basins
  2. Full overlay matrices: not just diagonal, the cross-PC couplings
     that encode rotation angles between basins
  3. Attention routing: which tokens attend to which, per position,
     decoded to show the semantic routing structure
  4. Per-token transformation: for each position, what does each layer
     contribute in crystal space?
  5. Effective model rotation: compose all layers to see the complete
     transformation the model applies (input crystal state → output)
  6. Gradient anatomy: decompose the gradient to see which specific
     weights are being etched, and what beta-reduction they encode

Usage:
    cd verbum
    uv run python scripts/micro/deep_trace.py checkpoints/micro/step_001000

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
    N_COMBINATORS, N_TOTAL_COMBINATORS,
)


# ══════════════════════════════════════════════════════════════════════
# Crystal tools
# ══════════════════════════════════════════════════════════════════════

PC_NAMES = ["comp(B)", "sel(K)", "term(WHNF)", "rout(C)",
            "fine(D)", "rec(Y)", "dup(W)", "anti"]


def get_crystal_basis(model: MicroModel) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Get crystal embeddings, eigenvectors, eigenvalues."""
    crystal_emb = np.array(model.get_all_crystal_embeddings())  # (16, d_model)
    data = _precompute_parity_eigenbasis(PCAQ_ZONE_B_TARGETS)
    eigvecs = data["eigvecs"]  # (16, 16)
    eigvals = data["eigvals"]  # (16,)
    return crystal_emb, eigvecs, eigvals


def to_crystal_coords(
    hidden: np.ndarray,
    crystal_emb: np.ndarray,
    eigvecs: np.ndarray,
) -> np.ndarray:
    """Project hidden states into crystal eigenbasis.

    hidden: (..., d_model)
    Returns: (..., 16) in eigenbasis coordinates
    """
    norms = np.linalg.norm(crystal_emb, axis=1, keepdims=True) + 1e-8
    crystal_norm = crystal_emb / norms
    # Project to combinator space then rotate to eigenbasis
    proj = hidden @ crystal_norm.T  # (..., 16)
    return proj @ eigvecs  # (..., 16) in eigenbasis


# ══════════════════════════════════════════════════════════════════════
# 1. Residual trajectory in crystal space
# ══════════════════════════════════════════════════════════════════════


def trace_residual_trajectory(
    model: MicroModel,
    input_ids: mx.array,
    targets: mx.array,
    crystal_emb: np.ndarray,
    eigvecs: np.ndarray,
) -> dict:
    """Track the residual stream through every layer in crystal coords.

    Records the hidden state at:
      - Post-embedding (before any blocks)
      - Post-attention (after attention + residual, before FFN)
      - Post-FFN (after FFN + residual = layer output)
    for every layer, at every token position.
    """
    B, L = input_ids.shape
    cfg = model.cfg

    # Manual forward pass to capture intermediate states
    positions = mx.arange(L)
    x = model.embed(input_ids) + model.pos_embed(positions)
    mx.eval(x)

    mask = model._get_causal_mask(L)

    trajectory = []
    # Post-embedding
    x_np = np.array(x)
    emb_crystal = to_crystal_coords(x_np[0], crystal_emb, eigvecs)  # (L, 16)
    trajectory.append({"stage": "embed", "crystal": emb_crystal})

    for i, block in enumerate(model.blocks):
        # Attention
        normed = block.attn_norm(x)
        attn_out = block.attn(normed, mask=mask)
        x_post_attn = x + attn_out
        mx.eval(x_post_attn)

        x_np = np.array(x_post_attn)
        attn_crystal = to_crystal_coords(x_np[0], crystal_emb, eigvecs)
        trajectory.append({
            "stage": f"L{i}_post_attn",
            "crystal": attn_crystal,
            "attn_contribution": to_crystal_coords(
                np.array(attn_out)[0], crystal_emb, eigvecs),
        })

        # FFN
        normed = block.ffn_norm(x_post_attn)
        ffn_out = block.ffn(normed)
        x = x_post_attn + ffn_out
        mx.eval(x)

        x_np = np.array(x)
        ffn_crystal = to_crystal_coords(x_np[0], crystal_emb, eigvecs)
        trajectory.append({
            "stage": f"L{i}_post_ffn",
            "crystal": ffn_crystal,
            "ffn_contribution": to_crystal_coords(
                np.array(ffn_out)[0], crystal_emb, eigvecs),
        })

    return {"trajectory": trajectory}


# ══════════════════════════════════════════════════════════════════════
# 2. Full overlay matrices with cross-coupling analysis
# ══════════════════════════════════════════════════════════════════════


def extract_full_overlays(
    model: MicroModel,
    crystal_emb: np.ndarray,
    eigvecs: np.ndarray,
) -> list[dict]:
    """Extract the complete FFN overlay matrix for each layer.

    The overlay matrix O[i,j] tells you: when the input has energy
    in crystal PC_i, how much energy appears in PC_j at the output.

    Diagonal = same-PC transmission (amplify or suppress)
    Off-diagonal = cross-PC coupling (rotation between basins)

    Also extracts the attention Q/K/V projection matrices in crystal
    coordinates to see how attention steers the residual.
    """
    norms = np.linalg.norm(crystal_emb, axis=1, keepdims=True) + 1e-8
    crystal_norm = crystal_emb / norms

    results = []
    for i, block in enumerate(model.blocks):
        ffn = block.ffn

        # FFN overlay
        gate_w = np.array(ffn.gate_proj.weight)   # (d_ff, d_model)
        key_w = np.array(ffn.key_proj.weight)      # (d_ff, d_model)
        value_w = np.array(ffn.value_proj.weight)  # (d_model, d_ff)

        # Input-side crystal projection
        gate_crystal = gate_w @ crystal_norm.T      # (d_ff, 16)
        gate_eigen = gate_crystal @ eigvecs          # (d_ff, 16)
        key_crystal = key_w @ crystal_norm.T
        key_eigen = key_crystal @ eigvecs

        # Output-side crystal projection
        value_crystal = crystal_norm @ value_w       # (16, d_ff)
        value_eigen = eigvecs.T @ value_crystal      # (16, d_ff)

        # Full overlay: gate_eigen.T @ value_eigen.T = (16, 16)
        overlay = gate_eigen.T @ value_eigen.T

        # SwiGLU overlay: key_eigen contributes via element-wise gate
        # Effective overlay ≈ (gate ⊙ key)^T @ value
        # For the linear approximation, the cross-term matters
        key_overlay = key_eigen.T @ value_eigen.T

        # Decompose overlay into symmetric + antisymmetric
        sym = (overlay + overlay.T) / 2
        antisym = (overlay - overlay.T) / 2

        # Attention Q projection in crystal space
        q_w = np.array(block.attn.q_proj.weight)  # (d_model, d_model)
        k_w = np.array(block.attn.k_proj.weight)
        v_w = np.array(block.attn.v_proj.weight)
        o_w = np.array(block.attn.o_proj.weight)

        # Q in crystal coordinates: how does Q rotate crystal PCs?
        q_crystal = crystal_norm @ q_w.T @ crystal_norm.T  # (16, 16)
        q_eigen = eigvecs.T @ q_crystal @ eigvecs  # (16, 16) in eigenbasis

        # OV circuit in crystal coordinates: what does attention write?
        ov_crystal = crystal_norm @ (o_w @ v_w).T @ crystal_norm.T
        ov_eigen = eigvecs.T @ ov_crystal @ eigvecs

        results.append({
            "layer": i,
            "overlay": overlay[:8, :8],        # top 8x8 for readability
            "key_overlay": key_overlay[:8, :8],
            "symmetric": sym[:8, :8],
            "antisymmetric": antisym[:8, :8],
            "q_rotation": q_eigen[:8, :8],
            "ov_circuit": ov_eigen[:8, :8],
            "overlay_full": overlay,
        })

    return results


# ══════════════════════════════════════════════════════════════════════
# 3. Attention routing per token
# ══════════════════════════════════════════════════════════════════════


def trace_attention_routing(
    model: MicroModel,
    input_ids: mx.array,
    tokenizer,
) -> list[dict]:
    """Trace attention patterns to see semantic routing.

    For each layer, each head, shows which tokens attend to which,
    with the actual token text for readability.
    """
    B, L = input_ids.shape
    model.set_capture(True)
    logits, _ = model(input_ids)
    mx.eval(logits)
    traces = model.get_traces()
    model.set_capture(False)

    tokens = [tokenizer.decode([input_ids[0, i].item()]) for i in range(L)]

    results = []
    for layer_trace in traces:
        layer_idx = layer_trace["layer"]
        attn_weights = np.array(layer_trace["attn"]["attn_weights"])  # (B, H, L, L)

        head_routes = []
        for h in range(model.cfg.n_heads):
            # For each query position, find top-2 attended keys
            attn_h = attn_weights[0, h]  # (L, L)
            routes = []
            for q_pos in range(L):
                top2 = np.argsort(attn_h[q_pos])[-2:][::-1]
                routes.append({
                    "query": tokens[q_pos],
                    "attends_to": [
                        (tokens[k_pos], float(attn_h[q_pos, k_pos]))
                        for k_pos in top2
                    ],
                })
            head_routes.append({"head": h, "routes": routes})

        results.append({"layer": layer_idx, "heads": head_routes})

    return results


# ══════════════════════════════════════════════════════════════════════
# 4. Composed transformation
# ══════════════════════════════════════════════════════════════════════


def compose_model_transformation(overlays: list[dict]) -> dict:
    """Compose all layer overlays to see the total model transformation.

    If layers alternate between composition and selection modes,
    the composed transformation should show the net effect:
    what does the full model do to the crystal state?
    """
    n = overlays[0]["overlay_full"].shape[0]
    composed = np.eye(n)

    intermediates = [composed.copy()]
    for ov in overlays:
        # Each layer: residual + overlay (skip connection + FFN)
        # Effective transformation: I + overlay (linearized)
        layer_transform = np.eye(n) + ov["overlay_full"]
        composed = layer_transform @ composed
        intermediates.append(composed[:8, :8].copy())

    # Eigendecompose the composed transformation
    comp_eigvals, comp_eigvecs = np.linalg.eigh(composed[:8, :8])
    idx = np.argsort(np.abs(comp_eigvals))[::-1]
    comp_eigvals = comp_eigvals[idx]

    return {
        "composed": composed[:8, :8],
        "composed_diag": np.diag(composed[:8, :8]).tolist(),
        "composed_eigvals": comp_eigvals.tolist(),
        "intermediates": intermediates,
    }


# ══════════════════════════════════════════════════════════════════════
# 5. Gradient anatomy — which weights encode which reductions
# ══════════════════════════════════════════════════════════════════════


def gradient_anatomy(
    model: MicroModel,
    input_ids: mx.array,
    targets: mx.array,
    crystal_emb: np.ndarray,
    eigvecs: np.ndarray,
) -> dict:
    """Detailed gradient decomposition.

    For each parameter, decompose the gradient into crystal PCs
    and identify which beta-reduction it's encoding.
    """
    def loss_fn(m, inp, tgt):
        _, loss = m(inp, tgt)
        return loss

    grad_fn = nn.value_and_grad(model, loss_fn)
    loss_val, grads = grad_fn(model, input_ids, targets)
    mx.eval(loss_val, grads)

    flat_grads = dict(nn.utils.tree_flatten(grads))

    norms = np.linalg.norm(crystal_emb, axis=1, keepdims=True) + 1e-8
    crystal_norm = crystal_emb / norms

    # For each layer, compute the gradient's overlay change
    # i.e., what overlay matrix change does this gradient step encode?
    layer_deltas = []
    for layer_idx in range(model.cfg.n_layers):
        prefix = f"blocks.{layer_idx}"

        # Gate gradient → overlay change
        gate_key = f"{prefix}.ffn.gate_proj.weight"
        value_key = f"{prefix}.ffn.value_proj.weight"

        if gate_key in flat_grads and value_key in flat_grads:
            gate_grad = np.array(flat_grads[gate_key])    # (d_ff, d_model)
            value_w = np.array(model.blocks[layer_idx].ffn.value_proj.weight)

            # The gradient for gate_w changes the overlay by:
            # δ_overlay = (crystal_norm @ δ_gate_w.T)^T @ (crystal_norm @ value_w)^T
            # Simplified: project the gradient itself into crystal overlay space
            gate_grad_crystal = gate_grad @ crystal_norm.T  # (d_ff, 16)
            gate_grad_eigen = gate_grad_crystal @ eigvecs    # (d_ff, 16)

            value_crystal = crystal_norm @ value_w           # (16, d_ff)
            value_eigen = eigvecs.T @ value_crystal          # (16, d_ff)

            delta_overlay = gate_grad_eigen.T @ value_eigen.T  # (16, 16)
        else:
            delta_overlay = np.zeros((16, 16))

        # Q gradient → rotation change
        q_key = f"{prefix}.attn.q_proj.weight"
        if q_key in flat_grads:
            q_grad = np.array(flat_grads[q_key])
            q_grad_crystal = crystal_norm @ q_grad.T @ crystal_norm.T
            q_grad_eigen = eigvecs.T @ q_grad_crystal @ eigvecs
        else:
            q_grad_eigen = np.zeros((16, 16))

        layer_deltas.append({
            "layer": layer_idx,
            "delta_overlay": delta_overlay[:8, :8],
            "delta_overlay_diag": np.diag(delta_overlay[:8, :8]).tolist(),
            "delta_q_rotation": q_grad_eigen[:8, :8],
            "delta_q_diag": np.diag(q_grad_eigen[:8, :8]).tolist(),
        })

    return {"layer_deltas": layer_deltas, "loss": float(loss_val.item())}


# ══════════════════════════════════════════════════════════════════════
# Display
# ══════════════════════════════════════════════════════════════════════


def print_matrix(mat: np.ndarray, labels: list[str], title: str, width: int = 7):
    """Pretty-print a small matrix with labels."""
    n = min(len(labels), mat.shape[0], mat.shape[1])
    print(f"\n  {title}")
    header = " " * 10 + "".join(f"{labels[j]:>{width}}" for j in range(n))
    print(f"  {header}")
    for i in range(n):
        row = f"  {labels[i]:>8} |"
        for j in range(n):
            v = mat[i, j]
            if abs(v) > 0.1:
                row += f"\033[1m{v:>{width}.3f}\033[0m"
            else:
                row += f"{v:>{width}.3f}"
        print(row)


def print_matrix_plain(mat: np.ndarray, labels: list[str], title: str, width: int = 7):
    """Pretty-print without ANSI codes."""
    n = min(len(labels), mat.shape[0], mat.shape[1])
    print(f"\n  {title}")
    header = " " * 10 + "".join(f"{labels[j]:>{width}}" for j in range(n))
    print(f"  {header}")
    for i in range(n):
        row = f"  {labels[i]:>8} |"
        for j in range(n):
            v = mat[i, j]
            marker = "*" if abs(v) > 0.1 else " "
            row += f"{v:>{width-1}.3f}{marker}"
        print(row)


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════


def main(checkpoint_dir: str | None = None):
    print("=" * 70)
    print("DEEP TRACE — Full Mechanism Extraction")
    print("=" * 70)

    cfg = MicroConfig()
    model = MicroModel(cfg)
    mx.eval(model.parameters())

    if checkpoint_dir:
        ckpt_path = Path(checkpoint_dir) / "model.npz"
        if ckpt_path.exists():
            print(f"\nLoading: {ckpt_path}")
            weights = mx.load(str(ckpt_path))
            model.load_weights(list(weights.items()))
            mx.eval(model.parameters())
            print("  Loaded ✓")

    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")

    crystal_emb, eigvecs, eigvals = get_crystal_basis(model)

    # ── Test examples ──
    examples = [
        ("The cat sits.", "λx. sits(cat)"),
        ("Every dog runs.", "∀x. (dog(x) → runs(x))"),
        ("Alice gave Bob a book.", "λx. gave(alice, bob, book)"),
    ]

    labels = PC_NAMES

    for eng, lam in examples:
        text = f"{eng}\n{lam}"
        tokens = tokenizer.encode(text, add_special_tokens=False)
        tokens.append(cfg.eod_id)
        token_strs = [tokenizer.decode([t]) for t in tokens]

        input_ids = mx.array([tokens[:-1]])
        targets = mx.array([tokens[1:]])
        L = input_ids.shape[1]

        print(f"\n{'═' * 70}")
        print(f"EXAMPLE: {eng} → {lam}")
        print(f"TOKENS:  {' | '.join(token_strs[:min(20, len(token_strs))])}")
        print(f"{'═' * 70}")

        # ═══════════════════════════════════════════════════
        # 1. RESIDUAL TRAJECTORY
        # ═══════════════════════════════════════════════════
        print(f"\n{'─' * 70}")
        print("1. RESIDUAL TRAJECTORY IN CRYSTAL SPACE")
        print(f"{'─' * 70}")

        traj = trace_residual_trajectory(
            model, input_ids, targets, crystal_emb, eigvecs)

        # Show trajectory for a few key positions
        # Find the newline position (boundary between English and lambda)
        nl_pos = None
        for pi, ts in enumerate(token_strs[:-1]):
            if '\n' in ts:
                nl_pos = pi
                break

        key_positions = [0, nl_pos, nl_pos + 1 if nl_pos else 1, L - 2]
        key_positions = [p for p in key_positions if p is not None and p < L]
        key_positions = sorted(set(key_positions))

        for pos in key_positions:
            tok = token_strs[pos] if pos < len(token_strs) - 1 else "?"
            print(f"\n  Position {pos} ('{tok.strip()}'):")
            print(f"  {'Stage':<16} | " +
                  " ".join(f"{'PC'+str(i):>7}" for i in range(8)))
            print(f"  {'─'*16} | " + " ".join("─" * 7 for _ in range(8)))

            for entry in traj["trajectory"]:
                stage = entry["stage"]
                crystal = entry["crystal"]
                vals = crystal[pos, :8]
                print(f"  {stage:<16} | " +
                      " ".join(f"{v:7.3f}" for v in vals))

        # ═══════════════════════════════════════════════════
        # 2. FULL OVERLAY MATRICES
        # ═══════════════════════════════════════════════════
        print(f"\n{'─' * 70}")
        print("2. FFN OVERLAY MATRICES (Diffraction Gratings)")
        print(f"{'─' * 70}")

        overlays = extract_full_overlays(model, crystal_emb, eigvecs)
        for ov in overlays:
            layer = ov["layer"]
            print_matrix_plain(
                ov["overlay"], labels,
                f"Layer {layer} — FFN Overlay (gate path)")
            print_matrix_plain(
                ov["q_rotation"], labels,
                f"Layer {layer} — Q Rotation in Crystal Space")
            print_matrix_plain(
                ov["ov_circuit"], labels,
                f"Layer {layer} — OV Circuit (what attention writes)")

        # ═══════════════════════════════════════════════════
        # 3. ATTENTION ROUTING
        # ═══════════════════════════════════════════════════
        print(f"\n{'─' * 70}")
        print("3. ATTENTION ROUTING (who attends to whom)")
        print(f"{'─' * 70}")

        routing = trace_attention_routing(model, input_ids, tokenizer)
        for lr in routing:
            layer = lr["layer"]
            print(f"\n  Layer {layer}:")
            # Show just head 0 for brevity, all positions
            head0 = lr["heads"][0]
            for r in head0["routes"][:min(15, L)]:
                q_tok = r["query"].strip()
                att = r["attends_to"]
                att_str = ", ".join(
                    f"'{k.strip()}':{w:.2f}" for k, w in att)
                print(f"    '{q_tok:>12}' → {att_str}")

        # ═══════════════════════════════════════════════════
        # 4. COMPOSED TRANSFORMATION
        # ═══════════════════════════════════════════════════
        print(f"\n{'─' * 70}")
        print("4. COMPOSED MODEL TRANSFORMATION")
        print(f"{'─' * 70}")

        comp = compose_model_transformation(overlays)
        print_matrix_plain(
            comp["composed"], labels,
            "Total model transformation (all layers composed)")
        print(f"\n  Composed eigenvalues: "
              + " ".join(f"{v:.3f}" for v in comp["composed_eigvals"]))
        print(f"  Composed diagonal: "
              + " ".join(f"{v:.3f}" for v in comp["composed_diag"]))

        # Show intermediate compositions
        print(f"\n  Progressive composition (diagonal only):")
        print(f"  {'After':<12} | " +
              " ".join(f"{'PC'+str(i):>7}" for i in range(8)))
        for step, inter in enumerate(comp["intermediates"]):
            diag = np.diag(inter)[:8]
            stage = f"Layer {step-1}" if step > 0 else "Identity"
            print(f"  {stage:<12} | " +
                  " ".join(f"{v:7.3f}" for v in diag))

        # ═══════════════════════════════════════════════════
        # 5. GRADIENT ANATOMY
        # ═══════════════════════════════════════════════════
        print(f"\n{'─' * 70}")
        print("5. GRADIENT ANATOMY — What beta-reductions is GD selecting?")
        print(f"{'─' * 70}")

        grad_anat = gradient_anatomy(
            model, input_ids, targets, crystal_emb, eigvecs)

        for ld in grad_anat["layer_deltas"]:
            layer = ld["layer"]
            print(f"\n  Layer {layer}:")
            print(f"    δ_overlay diagonal (what the gradient wants to change):")
            diag = ld["delta_overlay_diag"]
            for i, (d, l) in enumerate(zip(diag, labels)):
                direction = "↑amplify" if d > 0 else "↓suppress"
                bar = "█" * min(30, int(abs(d) * 50))
                print(f"      PC{i}({l:>9}): {d:+8.4f} {direction:>10} {bar}")

            print(f"    δ_Q diagonal (how the gradient wants to change Q rotation):")
            q_diag = ld["delta_q_diag"]
            for i, (d, l) in enumerate(zip(q_diag, labels)):
                direction = "↑amplify" if d > 0 else "↓suppress"
                bar = "█" * min(30, int(abs(d) * 500))
                print(f"      PC{i}({l:>9}): {d:+8.5f} {direction:>10} {bar}")

        # Only trace one example in full detail
        break

    print(f"\n{'═' * 70}")
    print("DEEP TRACE COMPLETE")
    print(f"{'═' * 70}")


if __name__ == "__main__":
    ckpt = sys.argv[1] if len(sys.argv) > 1 else None
    main(ckpt)
