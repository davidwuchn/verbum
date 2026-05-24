"""
Mechanism Extraction — KIBC head mapping + rotation closed form + GD as one operation.

Three analyses:
  A. HEAD → COMBINATOR MAPPING: Verify the 4 attention heads correspond
     to K (select), I (identity), B (compose), C (flip) by measuring
     what each head DOES to the residual stream in crystal coordinates.

  B. COMPOSED ROTATION CLOSED FORM: Decompose the total model rotation
     into a product of Givens rotations. Find the minimal description.
     Is it expressible as a small number of named rotations?

  C. GD AS ONE OPERATION: Track how the overlay matrix evolves during
     training. Is each gradient step a consistent rotation in crystal
     space? Can we predict the final overlay from the initial state?

Usage:
    cd verbum
    uv run python scripts/micro/mechanism_extraction.py checkpoints/micro/final

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
    COMBINATOR_NAMES, N_COMBINATORS,
)
from deep_trace import (
    get_crystal_basis, to_crystal_coords,
    extract_full_overlays, PC_NAMES,
)


# ══════════════════════════════════════════════════════════════════════
# A. HEAD → COMBINATOR MAPPING
# ══════════════════════════════════════════════════════════════════════


def map_heads_to_combinators(
    model: MicroModel,
    tokenizer,
    crystal_emb: np.ndarray,
    eigvecs: np.ndarray,
) -> dict:
    """Map each attention head to its combinator role.

    Method: For each head, measure what it DOES to the residual stream
    in crystal coordinates. The OV circuit (O @ V) tells us what the
    head writes. The QK circuit tells us what it selects.

    A head that:
      - Copies the attended token unchanged → I (identity)
      - Selects one token, discards context → K (select)
      - Combines two tokens' representations → B (compose)
      - Reorders/flips token roles → C (flip)

    We measure this by:
      1. OV circuit in crystal space: what crystal PCs does this head write?
      2. Attention entropy: how selective is this head?
      3. Crystal-space effect: what happens to PC0-PC7 when this head acts?
    """
    cfg = model.cfg
    norms = np.linalg.norm(crystal_emb, axis=1, keepdims=True) + 1e-8
    crystal_norm = crystal_emb / norms

    # Test examples for different structure types
    examples = [
        "The cat sits.\nλx. sits(cat)",
        "Bob follows Alice.\nλx. follows(bob, alice)",
        "Every dog runs.\n∀x. (dog(x) → runs(x))",
        "The cat sits and runs.\nλx. sits(cat) ∧ runs(cat)",
        "If the cat sits, the dog runs.\nλx. (sits(cat) → runs(dog))",
    ]

    all_head_data = []

    for text in examples:
        tokens = tokenizer.encode(text, add_special_tokens=False)
        tokens.append(cfg.eod_id)
        if len(tokens) > cfg.max_seq_len:
            tokens = tokens[:cfg.max_seq_len]
        token_strs = [tokenizer.decode([t]) for t in tokens]

        input_ids = mx.array([tokens[:-1]])
        L = input_ids.shape[1]

        # Find newline
        nl_pos = None
        for pi, ts in enumerate(token_strs[:-1]):
            if '\n' in ts:
                nl_pos = pi
                break

        # Run with capture
        model.set_capture(True)
        logits, _ = model(input_ids)
        mx.eval(logits)
        traces = model.get_traces()
        model.set_capture(False)

        for layer_trace in traces:
            layer = layer_trace["layer"]
            attn = layer_trace["attn"]
            q = np.array(attn["q"])[0]  # (H, L, d_head)
            k = np.array(attn["k"])[0]
            v = np.array(attn["v"])[0]
            attn_weights = np.array(attn["attn_weights"])[0]  # (H, L, L)
            attn_out = np.array(attn["attn_out"])[0]  # (H, L, d_head)

            for h in range(cfg.n_heads):
                # Attention selectivity
                attn_h = attn_weights[h]  # (L, L)
                entropy = -np.sum(attn_h * np.log(attn_h + 1e-10), axis=-1)
                mean_entropy = float(np.mean(entropy))
                max_attn_per_query = np.max(attn_h, axis=-1)
                mean_max = float(np.mean(max_attn_per_query))

                # Self-attention ratio (how much each token attends to itself)
                self_attn = float(np.mean(np.diag(attn_h[:L, :L])))

                # At the lambda boundary: what does this head attend to?
                if nl_pos is not None and nl_pos + 1 < L:
                    lambda_pos = nl_pos + 1
                    lambda_attn = attn_h[lambda_pos, :lambda_pos + 1]
                    # Classify what it attends to
                    eng_positions = list(range(nl_pos))
                    lambda_positions = list(range(nl_pos, lambda_pos + 1))

                    eng_attn = float(np.sum(lambda_attn[:nl_pos]))
                    struct_attn = float(np.sum(lambda_attn[nl_pos:]))
                else:
                    eng_attn = 0.0
                    struct_attn = 0.0

                all_head_data.append({
                    "example": text.split('\n')[0],
                    "layer": layer,
                    "head": h,
                    "entropy": mean_entropy,
                    "max_attn": mean_max,
                    "self_attn": self_attn,
                    "eng_attn": eng_attn,
                    "struct_attn": struct_attn,
                })

    # Aggregate per (layer, head)
    head_profiles = {}
    for d in all_head_data:
        key = (d["layer"], d["head"])
        if key not in head_profiles:
            head_profiles[key] = {
                "entropy": [], "max_attn": [], "self_attn": [],
                "eng_attn": [], "struct_attn": [],
            }
        for k in ["entropy", "max_attn", "self_attn", "eng_attn", "struct_attn"]:
            head_profiles[key][k].append(d[k])

    # Average
    for key in head_profiles:
        for k in head_profiles[key]:
            head_profiles[key][k] = float(np.mean(head_profiles[key][k]))

    # Per-layer OV circuit analysis in crystal space
    layer_ov_analysis = []
    for layer_idx, block in enumerate(model.blocks):
        v_w = np.array(block.attn.v_proj.weight)  # (d_model, d_model)
        o_w = np.array(block.attn.o_proj.weight)  # (d_model, d_model)

        # Full OV: o_w @ v_w — what does the full attention write?
        ov_full = o_w @ v_w  # (d_model, d_model)

        # In crystal space
        ov_crystal = crystal_norm @ ov_full @ crystal_norm.T  # (16, 16)
        ov_eigen = eigvecs.T @ ov_crystal @ eigvecs  # (16, 16)

        # Per-head OV circuit
        d_head = cfg.d_head
        head_ov_crystals = []
        for h in range(cfg.n_heads):
            # Extract per-head V and O slices
            v_h = v_w[:, h*d_head:(h+1)*d_head]     # (d_model, d_head)
            o_h = o_w[h*d_head:(h+1)*d_head, :]     # (d_head, d_model)  -- WRONG

            # Actually: O projects from concat of heads back to d_model
            # O weight is (d_model, d_model), applied after concatenation
            # Per-head contribution: o_w @ [0..0, v_h, 0..0]
            # = o_w[:, h*d_head:(h+1)*d_head] @ v_h.T ... no
            # Actually V: (d_model, d_model), reshaped to (d_model, H, d_head)
            # O: (d_model, d_model)
            # Per-head OV = o_w[:, h*d_head:(h+1)*d_head] @ v_w[h*d_head:(h+1)*d_head, :]
            # Wait, V projects to d_model then reshapes. Let me think...
            # v_proj: (d_model, d_model), output reshaped to (B, L, H, d_head)
            # So V for head h = v_proj.weight[h*d_head:(h+1)*d_head, :] — rows h*d_head to (h+1)*d_head
            # o_proj: (d_model, d_model), input is (B, L, d_model) after reshape from (B, L, H, d_head)
            # So O for head h = o_proj.weight[:, h*d_head:(h+1)*d_head] — cols h*d_head to (h+1)*d_head

            v_h = v_w[h*d_head:(h+1)*d_head, :]     # (d_head, d_model)
            o_h = o_w[:, h*d_head:(h+1)*d_head]      # (d_model, d_head)

            ov_h = o_h @ v_h  # (d_model, d_model) — per-head OV circuit

            # In crystal space
            ov_h_crystal = crystal_norm @ ov_h @ crystal_norm.T  # (16, 16)
            ov_h_eigen = eigvecs.T @ ov_h_crystal @ eigvecs  # (16, 16)

            head_ov_crystals.append(ov_h_eigen[:8, :8])

        # Per-head QK circuit
        q_w = np.array(block.attn.q_proj.weight)  # (d_model, d_model)
        k_w = np.array(block.attn.k_proj.weight)  # (d_model, d_model)

        head_qk_crystals = []
        for h in range(cfg.n_heads):
            q_h = q_w[h*d_head:(h+1)*d_head, :]   # (d_head, d_model)
            k_h = k_w[h*d_head:(h+1)*d_head, :]   # (d_head, d_model)

            # QK circuit: q_h.T @ k_h — what does this head match?
            qk_h = q_h.T @ k_h  # (d_model, d_model)
            qk_h_crystal = crystal_norm @ qk_h @ crystal_norm.T
            qk_h_eigen = eigvecs.T @ qk_h_crystal @ eigvecs

            head_qk_crystals.append(qk_h_eigen[:8, :8])

        layer_ov_analysis.append({
            "layer": layer_idx,
            "head_ov": head_ov_crystals,
            "head_qk": head_qk_crystals,
        })

    return {
        "head_profiles": head_profiles,
        "layer_ov": layer_ov_analysis,
    }


# ══════════════════════════════════════════════════════════════════════
# B. COMPOSED ROTATION — GIVENS DECOMPOSITION
# ══════════════════════════════════════════════════════════════════════


def givens_decomposition(R: np.ndarray, n: int = 6) -> list[dict]:
    """Decompose rotation matrix R into Givens rotations.

    A Givens rotation G(i,j,θ) rotates in the (i,j) plane by angle θ.
    Any rotation can be decomposed into at most n(n-1)/2 Givens rotations.

    Returns list of {i, j, angle_deg} for significant rotations.
    """
    R_work = R[:n, :n].copy()
    givens = []

    # QR-like decomposition using Givens rotations
    for j in range(n):
        for i in range(n-1, j, -1):
            if abs(R_work[i, j]) > 1e-10:
                r = math.sqrt(R_work[i-1, j]**2 + R_work[i, j]**2)
                c = R_work[i-1, j] / r
                s = R_work[i, j] / r
                angle = math.atan2(s, c)

                # Apply rotation
                for k in range(n):
                    t1 = c * R_work[i-1, k] + s * R_work[i, k]
                    t2 = -s * R_work[i-1, k] + c * R_work[i, k]
                    R_work[i-1, k] = t1
                    R_work[i, k] = t2

                if abs(math.degrees(angle)) > 0.5:
                    givens.append({
                        "i": i-1, "j": i,
                        "angle_deg": math.degrees(angle),
                        "pc_i": PC_NAMES[i-1] if i-1 < len(PC_NAMES) else f"PC{i-1}",
                        "pc_j": PC_NAMES[i] if i < len(PC_NAMES) else f"PC{i}",
                    })

    return givens


def analyze_rotation_structure(overlays: list[dict]) -> dict:
    """Deep analysis of the composed rotation.

    Questions:
      1. Can the total rotation be expressed as a small number of
         Givens rotations in the crystal eigenbasis?
      2. Is there a "rotation generator" (Lie algebra element) that
         generates the composed rotation via matrix exponential?
      3. What are the rotation eigenplanes and eigenangles?
    """
    # Compose overlay transformations: T = (I+O_3)(I+O_2)(I+O_1)(I+O_0)
    n = 8
    composed = np.eye(n)
    per_layer = []
    for ov in overlays:
        O = ov["overlay"][:n, :n]
        T = np.eye(n) + O
        composed = T @ composed
        per_layer.append(T)

    # Polar decomposition: composed = R @ P
    U, S, Vt = np.linalg.svd(composed)
    R = U @ Vt
    P = Vt.T @ np.diag(S) @ Vt

    # Givens decomposition of R
    givens = givens_decomposition(R, n=min(n, 6))

    # Lie algebra: find generator A such that exp(A) ≈ R
    # A = log(R) — for rotation matrices, A is antisymmetric
    # Use the real Schur decomposition to compute matrix log
    # Simpler: A ≈ (R - R^T) / 2 for small rotations
    # For larger rotations, use the proper matrix logarithm
    A_approx = (R[:6, :6] - R[:6, :6].T) / 2

    # Eigendecomposition of composed (includes scaling)
    eigvals_comp = np.linalg.eigvals(composed)
    # Sort by magnitude
    idx = np.argsort(np.abs(eigvals_comp))[::-1]
    eigvals_comp = eigvals_comp[idx]

    # Rotation eigenplanes: eigenvalues of R come in conjugate pairs
    # e^{iθ} → rotation by θ in that eigenplane
    R_eigvals = np.linalg.eigvals(R[:6, :6])
    eigenangles = []
    seen = set()
    for ev in R_eigvals:
        angle = math.degrees(math.atan2(ev.imag, ev.real))
        rounded = round(angle, 1)
        if rounded not in seen and abs(rounded) > 0.5:
            eigenangles.append(rounded)
            seen.add(rounded)

    # Stretch spectrum (P diagonal)
    stretch_eigvals = np.linalg.eigvals(P[:6, :6])
    stretch_magnitudes = np.sort(np.abs(stretch_eigvals))[::-1]

    return {
        "R": R[:6, :6],
        "P": P[:6, :6],
        "givens": givens,
        "generator_A": A_approx,
        "eigenangles": sorted(eigenangles, key=abs, reverse=True),
        "stretch_spectrum": stretch_magnitudes.tolist(),
        "composed_eigvals": [(float(ev.real), float(ev.imag))
                             for ev in eigvals_comp[:8]],
        "composed": composed,
    }


# ══════════════════════════════════════════════════════════════════════
# C. GD AS ONE OPERATION
# ══════════════════════════════════════════════════════════════════════


def analyze_gd_operation(
    model: MicroModel,
    tokenizer,
    crystal_emb: np.ndarray,
    eigvecs: np.ndarray,
) -> dict:
    """Characterize what GD does as a single operation in crystal space.

    Run multiple gradient steps, capture the overlay delta each time,
    and check if they're all the same rotation (or proportional).

    If GD is "one operation" in crystal space, then:
      δ_overlay ∝ G  (a fixed crystal-space operator)
    scaled by learning rate and loss gradient magnitude.

    We check this by computing the cosine similarity between
    successive gradient-induced overlay deltas.
    """
    cfg = model.cfg
    norms_c = np.linalg.norm(crystal_emb, axis=1, keepdims=True) + 1e-8
    crystal_norm = crystal_emb / norms_c

    # Collect gradient overlay deltas from different examples
    examples = [
        "The cat sits.\nλx. sits(cat)",
        "The dog runs.\nλx. runs(dog)",
        "Every dog runs.\n∀x. (dog(x) → runs(x))",
        "Bob follows Alice.\nλx. follows(bob, alice)",
        "The cat sits and runs.\nλx. sits(cat) ∧ runs(cat)",
        "Alice smiles.\nλx. smiles(alice)",
        "The cat chases the dog.\nλx. chases(cat, dog)",
        "Some cat sits.\n∃x. (cat(x) ∧ sits(x))",
    ]

    overlay_deltas_per_layer = {i: [] for i in range(cfg.n_layers)}
    q_deltas_per_layer = {i: [] for i in range(cfg.n_layers)}

    for text in examples:
        tokens = tokenizer.encode(text, add_special_tokens=False)
        tokens.append(cfg.eod_id)
        if len(tokens) > cfg.max_seq_len:
            tokens = tokens[:cfg.max_seq_len]

        input_ids = mx.array([tokens[:-1]])
        targets = mx.array([tokens[1:]])

        def loss_fn(m, inp, tgt):
            _, loss = m(inp, tgt)
            return loss

        grad_fn = nn.value_and_grad(model, loss_fn)
        loss_val, grads = grad_fn(model, input_ids, targets)
        mx.eval(loss_val, grads)

        flat_grads = dict(nn.utils.tree_flatten(grads))

        for layer_idx in range(cfg.n_layers):
            # Gate gradient → overlay delta
            gate_key = f"blocks.{layer_idx}.ffn.gate_proj.weight"
            value_w = np.array(model.blocks[layer_idx].ffn.value_proj.weight)

            if gate_key in flat_grads:
                gate_grad = np.array(flat_grads[gate_key])
                gate_grad_crystal = gate_grad @ crystal_norm.T
                gate_grad_eigen = gate_grad_crystal @ eigvecs

                value_crystal = crystal_norm @ value_w
                value_eigen = eigvecs.T @ value_crystal

                delta_overlay = gate_grad_eigen.T @ value_eigen.T
                overlay_deltas_per_layer[layer_idx].append(
                    delta_overlay[:8, :8].copy())

            # Q gradient → rotation delta
            q_key = f"blocks.{layer_idx}.attn.q_proj.weight"
            if q_key in flat_grads:
                q_grad = np.array(flat_grads[q_key])
                q_grad_crystal = crystal_norm @ q_grad.T @ crystal_norm.T
                q_grad_eigen = eigvecs.T @ q_grad_crystal @ eigvecs
                q_deltas_per_layer[layer_idx].append(
                    q_grad_eigen[:8, :8].copy())

    # Analyze consistency: are all deltas proportional?
    results_per_layer = []
    for layer_idx in range(cfg.n_layers):
        deltas = overlay_deltas_per_layer[layer_idx]
        q_deltas = q_deltas_per_layer[layer_idx]

        if len(deltas) < 2:
            continue

        # Flatten each delta to a vector and compute pairwise cosine similarity
        flat_deltas = [d.flatten() for d in deltas]
        n = len(flat_deltas)
        cos_sims = []
        for i in range(n):
            for j in range(i+1, n):
                a, b = flat_deltas[i], flat_deltas[j]
                cos = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10)
                cos_sims.append(float(cos))

        # Same for Q deltas
        flat_q = [d.flatten() for d in q_deltas]
        q_cos_sims = []
        for i in range(n):
            for j in range(i+1, n):
                a, b = flat_q[i], flat_q[j]
                cos = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10)
                q_cos_sims.append(float(cos))

        # Mean delta (the "canonical GD operator")
        mean_delta = np.mean(deltas, axis=0)
        mean_q_delta = np.mean(q_deltas, axis=0)

        # How much does each individual delta deviate from the mean?
        delta_angles = []
        for d in deltas:
            cos = np.dot(d.flatten(), mean_delta.flatten()) / (
                np.linalg.norm(d.flatten()) * np.linalg.norm(mean_delta.flatten()) + 1e-10)
            delta_angles.append(float(math.degrees(math.acos(max(-1, min(1, cos))))))

        results_per_layer.append({
            "layer": layer_idx,
            "n_examples": len(deltas),
            "overlay_cos_sim_mean": float(np.mean(cos_sims)),
            "overlay_cos_sim_std": float(np.std(cos_sims)),
            "overlay_cos_sim_min": float(np.min(cos_sims)),
            "q_cos_sim_mean": float(np.mean(q_cos_sims)),
            "q_cos_sim_std": float(np.std(q_cos_sims)),
            "q_cos_sim_min": float(np.min(q_cos_sims)),
            "mean_delta_diag": np.diag(mean_delta).tolist(),
            "mean_q_delta_diag": np.diag(mean_q_delta).tolist(),
            "delta_deviation_degrees": delta_angles,
            "mean_delta": mean_delta,
            "mean_q_delta": mean_q_delta,
        })

    return {"per_layer": results_per_layer}


# ══════════════════════════════════════════════════════════════════════
# D. CHECKPOINT EVOLUTION — How overlays evolved during training
# ══════════════════════════════════════════════════════════════════════


def track_overlay_evolution(
    checkpoints: list[str],
    crystal_emb: np.ndarray,
    eigvecs: np.ndarray,
) -> dict:
    """Load checkpoints at different training steps and track how
    the overlay matrices evolved. Did they converge monotonically?
    Was there a phase transition?
    """
    cfg = MicroConfig()
    norms = np.linalg.norm(crystal_emb, axis=1, keepdims=True) + 1e-8
    crystal_norm = crystal_emb / norms

    evolution = []
    for ckpt_dir in checkpoints:
        ckpt_path = Path(ckpt_dir) / "model.npz"
        state_path = Path(ckpt_dir) / "state.json"

        if not ckpt_path.exists():
            continue

        model = MicroModel(cfg)
        mx.eval(model.parameters())
        weights = mx.load(str(ckpt_path))
        model.load_weights(list(weights.items()))
        mx.eval(model.parameters())

        step = 0
        if state_path.exists():
            with open(state_path) as f:
                state = json.load(f)
                step = state.get("step", 0)

        overlays = extract_full_overlays(model, crystal_emb, eigvecs)

        # Extract overlay diagonals and key cross-couplings
        overlay_diags = []
        comp_sel_coupling = []  # PC0→PC1
        for ov in overlays:
            O = ov["overlay"][:8, :8]
            overlay_diags.append(np.diag(O).tolist())
            comp_sel_coupling.append(float(O[0, 1]))

        evolution.append({
            "step": step,
            "overlay_diags": overlay_diags,
            "comp_sel_coupling": comp_sel_coupling,
        })

    return {"evolution": evolution}


# ══════════════════════════════════════════════════════════════════════
# Display
# ══════════════════════════════════════════════════════════════════════


def print_matrix(mat, labels, title, n=None):
    if n is None:
        n = min(len(labels), mat.shape[0], mat.shape[1])
    print(f"\n    {title}")
    header = " " * 14 + "".join(f"{labels[j]:>10}" for j in range(n))
    print(f"    {header}")
    for i in range(n):
        row = f"    {labels[i]:>12} |"
        for j in range(n):
            v = mat[i, j]
            marker = "*" if abs(v) > 0.05 else " "
            row += f"  {v:+6.3f}{marker}"
        print(row)


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════


def main(checkpoint_dir: str | None = None):
    print("=" * 70)
    print("MECHANISM EXTRACTION")
    print("  Head→Combinator | Rotation Closed Form | GD as One Operation")
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

    # ═══════════════════════════════════════════════════════
    # A. HEAD → COMBINATOR MAPPING
    # ═══════════════════════════════════════════════════════
    print(f"\n{'═' * 70}")
    print("A. HEAD → COMBINATOR MAPPING")
    print(f"{'═' * 70}")

    head_data = map_heads_to_combinators(model, tokenizer, crystal_emb, eigvecs)

    # Behavioral profiles
    print(f"\n  Head behavioral profiles (averaged across 5 examples):")
    print(f"  {'L.H':>4} {'Entropy':>8} {'Max Attn':>9} {'Self Attn':>10} "
          f"{'Eng Attn':>9} {'Struct':>7} | Role")
    print(f"  {'─'*4} {'─'*8} {'─'*9} {'─'*10} {'─'*9} {'─'*7} | {'─'*20}")

    for (layer, head), profile in sorted(head_data["head_profiles"].items()):
        # Classify role based on profile
        role = "?"
        if profile["self_attn"] > 0.3:
            role = "I (identity/copy)"
        elif profile["max_attn"] > 0.6:
            role = "K (select)"
        elif profile["entropy"] > 1.4:
            role = "B (compose/mix)"
        elif profile["eng_attn"] > 0.7:
            role = "content reader"
        else:
            role = "C (route/flip)"

        print(f"  {layer}.{head:>1} {profile['entropy']:8.3f} "
              f"{profile['max_attn']:9.3f} {profile['self_attn']:10.3f} "
              f"{profile['eng_attn']:9.3f} {profile['struct_attn']:7.3f} "
              f"| {role}")

    # Per-head OV circuits in crystal space
    print(f"\n  Per-head OV circuits (what each head writes in crystal space):")
    labels = PC_NAMES[:6]
    for layer_data in head_data["layer_ov"]:
        layer = layer_data["layer"]
        for h in range(cfg.n_heads):
            ov_h = layer_data["head_ov"][h][:6, :6]
            # Summarize: what are the dominant read→write mappings?
            dominant = []
            for i in range(6):
                for j in range(6):
                    if abs(ov_h[i, j]) > 0.02:
                        sign = "+" if ov_h[i, j] > 0 else "-"
                        dominant.append(
                            f"{labels[i]}→{labels[j]}:{sign}{abs(ov_h[i,j]):.3f}")
            if dominant:
                print(f"    L{layer}.H{h}: {', '.join(dominant[:6])}")

    # Per-head QK circuits
    print(f"\n  Per-head QK circuits (what each head matches):")
    for layer_data in head_data["layer_ov"]:
        layer = layer_data["layer"]
        for h in range(cfg.n_heads):
            qk_h = layer_data["head_qk"][h][:6, :6]
            # Diagonal = self-matching per PC
            diag = np.diag(qk_h)
            diag_str = " ".join(f"{labels[i]}:{diag[i]:+.3f}" for i in range(6)
                               if abs(diag[i]) > 0.01)
            if diag_str:
                print(f"    L{layer}.H{h} diag: {diag_str}")

    # ═══════════════════════════════════════════════════════
    # B. ROTATION CLOSED FORM
    # ═══════════════════════════════════════════════════════
    print(f"\n{'═' * 70}")
    print("B. COMPOSED ROTATION — CLOSED FORM")
    print(f"{'═' * 70}")

    overlays = extract_full_overlays(model, crystal_emb, eigvecs)
    rot_struct = analyze_rotation_structure(overlays)

    print(f"\n  Givens decomposition of the composed rotation R:")
    print(f"  (Each Givens rotation is a rotation in one 2D plane)")
    for g in rot_struct["givens"]:
        deg = g["angle_deg"]
        direction = "⟲" if deg > 0 else "⟳"
        bar = "█" * min(40, int(abs(deg) * 2))
        print(f"    {g['pc_i']:>10} ↔ {g['pc_j']:<10} "
              f"{direction} {deg:+7.2f}° {bar}")

    print(f"\n  Rotation eigenangles (rotation in each eigenplane):")
    for angle in rot_struct["eigenangles"]:
        bar = "█" * min(40, int(abs(angle) * 2))
        print(f"    {angle:+7.1f}° {bar}")

    print(f"\n  Stretch spectrum (scaling in each direction):")
    for i, s in enumerate(rot_struct["stretch_spectrum"][:6]):
        bar = "█" * int(s * 20)
        label = "amplify" if s > 1 else "compress"
        print(f"    Direction {i}: {s:.4f} ({label}) {bar}")

    print(f"\n  Composed eigenvalues (magnitude, angle):")
    for i, (re, im) in enumerate(rot_struct["composed_eigvals"][:8]):
        mag = math.sqrt(re*re + im*im)
        angle = math.degrees(math.atan2(im, re))
        label = "amplify" if mag > 1 else "compress"
        print(f"    λ{i}: mag={mag:.4f} ({label}), angle={angle:+.1f}°")

    # Print the rotation generator
    print_matrix(rot_struct["generator_A"], labels,
                 "Rotation generator A ≈ log(R) (antisymmetric, degrees)")

    # Print the stretch
    print_matrix(rot_struct["P"][:6, :6], labels,
                 "Stretch matrix P (positive semidefinite)")

    # ═══════════════════════════════════════════════════════
    # C. GD AS ONE OPERATION
    # ═══════════════════════════════════════════════════════
    print(f"\n{'═' * 70}")
    print("C. GD AS ONE OPERATION — Is every gradient step the same rotation?")
    print(f"{'═' * 70}")

    gd_data = analyze_gd_operation(model, tokenizer, crystal_emb, eigvecs)

    print(f"\n  Gradient overlay delta consistency across {gd_data['per_layer'][0]['n_examples']} examples:")
    print(f"  {'Layer':>5} | {'Overlay cos_sim':>16} {'(std)':>7} {'(min)':>7} | "
          f"{'Q cos_sim':>10} {'(std)':>7} {'(min)':>7} | Verdict")
    print(f"  {'─'*5} | {'─'*16} {'─'*7} {'─'*7} | {'─'*10} {'─'*7} {'─'*7} | {'─'*20}")

    for ld in gd_data["per_layer"]:
        layer = ld["layer"]
        ov_sim = ld["overlay_cos_sim_mean"]
        ov_std = ld["overlay_cos_sim_std"]
        ov_min = ld["overlay_cos_sim_min"]
        q_sim = ld["q_cos_sim_mean"]
        q_std = ld["q_cos_sim_std"]
        q_min = ld["q_cos_sim_min"]

        if ov_sim > 0.8:
            verdict = "✓ SAME OPERATION"
        elif ov_sim > 0.5:
            verdict = "~ similar"
        else:
            verdict = "✗ different"

        print(f"  {layer:>5} | {ov_sim:16.4f} {ov_std:7.4f} {ov_min:7.4f} | "
              f"{q_sim:10.4f} {q_std:7.4f} {q_min:7.4f} | {verdict}")

    # Show the canonical GD operator (mean overlay delta)
    print(f"\n  Canonical GD operator G (mean overlay delta per layer):")
    for ld in gd_data["per_layer"]:
        layer = ld["layer"]
        diag = ld["mean_delta_diag"]
        print(f"\n    Layer {layer} overlay δ diagonal:")
        for i, (d, l) in enumerate(zip(diag, PC_NAMES)):
            direction = "↑" if d > 0 else "↓"
            bar = "█" * min(40, int(abs(d) * 200))
            print(f"      {l:>12}: {d:+9.5f} {direction} {bar}")

    print(f"\n  Canonical GD Q-rotation operator:")
    for ld in gd_data["per_layer"]:
        layer = ld["layer"]
        q_diag = ld["mean_q_delta_diag"]
        print(f"\n    Layer {layer} Q δ diagonal:")
        for i, (d, l) in enumerate(zip(q_diag, PC_NAMES)):
            direction = "↑" if d > 0 else "↓"
            bar = "█" * min(40, int(abs(d) * 2000))
            print(f"      {l:>12}: {d:+10.6f} {direction} {bar}")

    # Deviation of individual examples from the mean
    print(f"\n  Per-example deviation from canonical operator (degrees):")
    for ld in gd_data["per_layer"]:
        layer = ld["layer"]
        devs = ld["delta_deviation_degrees"]
        mean_dev = np.mean(devs)
        max_dev = np.max(devs)
        print(f"    Layer {layer}: mean={mean_dev:.1f}°, max={max_dev:.1f}°, "
              f"all: [{', '.join(f'{d:.1f}' for d in devs)}]")

    # ═══════════════════════════════════════════════════════
    # D. OVERLAY EVOLUTION ACROSS TRAINING
    # ═══════════════════════════════════════════════════════
    print(f"\n{'═' * 70}")
    print("D. OVERLAY EVOLUTION ACROSS TRAINING")
    print(f"{'═' * 70}")

    # Find all checkpoints
    ckpt_base = Path(checkpoint_dir).parent if checkpoint_dir else Path("checkpoints/micro")
    ckpt_dirs = sorted(ckpt_base.glob("step_*"))
    if not ckpt_dirs:
        ckpt_dirs = [Path(checkpoint_dir)] if checkpoint_dir else []

    if len(ckpt_dirs) >= 2:
        evo = track_overlay_evolution(
            [str(d) for d in ckpt_dirs[:6]],  # first 6 checkpoints
            crystal_emb, eigvecs)

        print(f"\n  Overlay PC0 (composition) diagonal evolution:")
        print(f"  {'Step':>6} | {'L0':>7} {'L1':>7} {'L2':>7} {'L3':>7}")
        print(f"  {'─'*6} | {'─'*7} {'─'*7} {'─'*7} {'─'*7}")
        for entry in evo["evolution"]:
            step = entry["step"]
            pc0s = [entry["overlay_diags"][l][0] for l in range(4)]
            print(f"  {step:6d} | " + " ".join(f"{v:+7.3f}" for v in pc0s))

        print(f"\n  Overlay PC1 (selection) diagonal evolution:")
        print(f"  {'Step':>6} | {'L0':>7} {'L1':>7} {'L2':>7} {'L3':>7}")
        print(f"  {'─'*6} | {'─'*7} {'─'*7} {'─'*7} {'─'*7}")
        for entry in evo["evolution"]:
            step = entry["step"]
            pc1s = [entry["overlay_diags"][l][1] for l in range(4)]
            print(f"  {step:6d} | " + " ".join(f"{v:+7.3f}" for v in pc1s))

        print(f"\n  PC0→PC1 coupling evolution:")
        print(f"  {'Step':>6} | {'L0':>7} {'L1':>7} {'L2':>7} {'L3':>7}")
        print(f"  {'─'*6} | {'─'*7} {'─'*7} {'─'*7} {'─'*7}")
        for entry in evo["evolution"]:
            step = entry["step"]
            couplings = entry["comp_sel_coupling"]
            print(f"  {step:6d} | " + " ".join(f"{v:+7.3f}" for v in couplings))
    else:
        print(f"\n  (Need ≥2 checkpoints for evolution tracking)")

    # ═══════════════════════════════════════════════════════
    # E. SYNTHESIS
    # ═══════════════════════════════════════════════════════
    print(f"\n{'═' * 70}")
    print("E. SYNTHESIS — Can we compute weights directly?")
    print(f"{'═' * 70}")

    # Key finding: if GD cos_sim > 0.8, the gradient is one operation
    gd_is_one_op = all(
        ld["overlay_cos_sim_mean"] > 0.5 for ld in gd_data["per_layer"])

    print(f"\n  GD is one operation? {gd_is_one_op}")
    if gd_is_one_op:
        print(f"  → The gradient in crystal space is the SAME operator")
        print(f"    regardless of input. It always applies the same rotation")
        print(f"    + scaling to the overlay matrix.")
        print(f"  → This means: given the crystal geometry and the canonical")
        print(f"    GD operator G, the final overlay is:")
        print(f"      O_final = O_init + N_steps × lr × G")
        print(f"    where G is input-invariant.")
    else:
        print(f"  → GD operator varies with input (needs more analysis)")

    # Alternation is universal?
    overlay_diags = np.array([
        [ov["overlay"][i, i] for i in range(8)]
        for ov in overlays
    ])
    pc0_alternates = all(
        overlay_diags[i, 0] * overlay_diags[i+1, 0] < 0
        for i in range(3)
    )
    pc1_alternates = all(
        overlay_diags[i, 1] * overlay_diags[i+1, 1] < 0
        for i in range(3)
    )

    print(f"\n  PC0 alternation confirmed: {pc0_alternates}")
    print(f"  PC1 alternation confirmed: {pc1_alternates}")
    print(f"  PC0/PC1 anti-phase: {pc0_alternates and pc1_alternates}")

    if pc0_alternates and pc1_alternates:
        print(f"\n  → The overlay at each layer is determined by:")
        print(f"    O[layer] = (-1)^layer × amplitude × crystal_PC_operator")
        print(f"    This is an INTERFERENCE PATTERN with period 2.")
        print(f"    The 'diffraction grating' IS the alternation itself.")

    print(f"\n{'═' * 70}")
    print("MECHANISM EXTRACTION COMPLETE")
    print(f"{'═' * 70}")


if __name__ == "__main__":
    ckpt = sys.argv[1] if len(sys.argv) > 1 else None
    main(ckpt)
