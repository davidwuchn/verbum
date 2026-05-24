"""
Universality + Rotation Probe — Is the mechanism universal?

Two analyses:
  A. UNIVERSALITY: Run the deep trace on many examples across all
     categories. Compare residual amplification, overlay patterns,
     attention routing. Are the patterns the same regardless of input?

  B. ROTATION EXTRACTION: Decompose the off-diagonal cross-couplings
     of the overlay matrices into rotation angles. Extract the
     specific rotation the FFN grating applies between crystal PCs.

Usage:
    cd verbum
    uv run python scripts/micro/universality_probe.py checkpoints/micro/final

License: MIT
"""

from __future__ import annotations

import json
import sys
import math
from pathlib import Path
from collections import defaultdict

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
    trace_residual_trajectory, extract_full_overlays,
    PC_NAMES,
)


# ══════════════════════════════════════════════════════════════════════
# Test examples by category
# ══════════════════════════════════════════════════════════════════════

TEST_EXAMPLES = [
    # Simple intransitive
    {"input": "The cat sits.", "output": "λx. sits(cat)", "category": "simple"},
    {"input": "The dog runs.", "output": "λx. runs(dog)", "category": "simple"},
    {"input": "Alice smiles.", "output": "λx. smiles(alice)", "category": "simple"},

    # Transitive
    {"input": "The cat chases the dog.", "output": "λx. chases(cat, dog)", "category": "transitive"},
    {"input": "Bob follows Alice.", "output": "λx. follows(bob, alice)", "category": "transitive"},

    # Quantified
    {"input": "Every dog runs.", "output": "∀x. (dog(x) → runs(x))", "category": "quantified"},
    {"input": "Some cat sits.", "output": "∃x. (cat(x) ∧ sits(x))", "category": "quantified"},

    # Conjunction
    {"input": "The cat sits and runs.", "output": "λx. sits(cat) ∧ runs(cat)", "category": "conjunction"},

    # Negation
    {"input": "The cat does not sit.", "output": "λx. ¬sits(cat)", "category": "negation"},

    # Conditional
    {"input": "If the cat sits, the dog runs.", "output": "λx. (sits(cat) → runs(dog))", "category": "conditional"},

    # Prepositional
    {"input": "The cat sits in the house.", "output": "λx. sits(cat, house)", "category": "prepositional"},

    # Copular
    {"input": "The cat is happy.", "output": "λx. happy(cat)", "category": "copular"},
]


# ══════════════════════════════════════════════════════════════════════
# A. UNIVERSALITY ANALYSIS
# ══════════════════════════════════════════════════════════════════════


def analyze_universality(
    model: MicroModel,
    tokenizer,
    crystal_emb: np.ndarray,
    eigvecs: np.ndarray,
) -> dict:
    """Run trajectory analysis on all test examples.

    For each example, extract:
      - Final residual PC magnitudes (the output basin)
      - Per-layer amplification ratio for PC0 and PC1
      - Attention routing pattern at key positions
    """
    cfg = model.cfg
    results = []

    for ex in TEST_EXAMPLES:
        text = f"{ex['input']}\n{ex['output']}"
        tokens = tokenizer.encode(text, add_special_tokens=False)
        tokens.append(cfg.eod_id)

        if len(tokens) > cfg.max_seq_len + 1:
            tokens = tokens[:cfg.max_seq_len + 1]

        input_ids = mx.array([tokens[:-1]])
        targets = mx.array([tokens[1:]])
        L = input_ids.shape[1]

        # Find boundary between English and lambda
        token_strs = [tokenizer.decode([t]) for t in tokens[:-1]]
        nl_pos = None
        for pi, ts in enumerate(token_strs):
            if '\n' in ts:
                nl_pos = pi
                break

        # Trajectory
        traj = trace_residual_trajectory(
            model, input_ids, targets, crystal_emb, eigvecs)

        # Extract key metrics
        embed_crystal = traj["trajectory"][0]["crystal"]  # (L, 16)
        final_crystal = traj["trajectory"][-1]["crystal"]  # (L, 16)

        # Per-position amplification: final / embed
        # Use the lambda output positions (after newline)
        if nl_pos is not None and nl_pos + 1 < L:
            lambda_positions = list(range(nl_pos, L))
        else:
            lambda_positions = list(range(L))

        # Mean PC magnitudes at lambda positions
        embed_mean = np.mean(np.abs(embed_crystal[lambda_positions, :8]), axis=0)
        final_mean = np.mean(np.abs(final_crystal[lambda_positions, :8]), axis=0)
        amplification = final_mean / (embed_mean + 1e-8)

        # Per-layer PC0 and PC1 values at the last lambda position
        last_lambda_pos = min(lambda_positions[-1], L - 1)
        layer_pc0 = []
        layer_pc1 = []
        for entry in traj["trajectory"]:
            if entry["crystal"].shape[0] > last_lambda_pos:
                layer_pc0.append(entry["crystal"][last_lambda_pos, 0])
                layer_pc1.append(entry["crystal"][last_lambda_pos, 1])

        # Gradient
        def loss_fn(m, inp, tgt):
            _, loss = m(inp, tgt)
            return loss
        grad_fn = nn.value_and_grad(model, loss_fn)
        loss_val, grads = grad_fn(model, input_ids, targets)
        mx.eval(loss_val, grads)

        flat_grads = dict(nn.utils.tree_flatten(grads))
        norms = np.linalg.norm(crystal_emb, axis=1, keepdims=True) + 1e-8
        crystal_norm = crystal_emb / norms

        # Per-layer dominant gradient PC
        grad_dominant_pcs = []
        for layer_idx in range(cfg.n_layers):
            gate_key = f"blocks.{layer_idx}.ffn.gate_proj.weight"
            if gate_key in flat_grads:
                gate_grad = np.array(flat_grads[gate_key])
                gate_crystal = gate_grad @ crystal_norm.T
                gate_eigen = gate_crystal @ eigvecs
                pc_mags = np.linalg.norm(gate_eigen, axis=0)[:8]
                grad_dominant_pcs.append(int(np.argmax(pc_mags)))
            else:
                grad_dominant_pcs.append(-1)

        results.append({
            "input": ex["input"],
            "output": ex["output"],
            "category": ex["category"],
            "amplification": amplification.tolist(),
            "final_pc0": float(final_mean[0]),
            "final_pc1": float(final_mean[1]),
            "layer_pc0": layer_pc0,
            "layer_pc1": layer_pc1,
            "grad_dominant_pcs": grad_dominant_pcs,
            "loss": float(loss_val.item()),
        })

    return {"examples": results}


# ══════════════════════════════════════════════════════════════════════
# B. ROTATION EXTRACTION
# ══════════════════════════════════════════════════════════════════════


def extract_rotations(overlays: list[dict]) -> list[dict]:
    """Decompose overlay matrices into rotation + scaling.

    For each layer's overlay matrix O:
      1. SVD decomposition: O = U @ S @ V^T
         - U, V are rotation matrices
         - S is scaling (singular values)
      2. Polar decomposition: O = R @ P
         - R is the nearest rotation matrix
         - P is the positive-semidefinite stretch
      3. Extract rotation angles from R (Givens decomposition)
      4. The antisymmetric part A = (O - O^T)/2 encodes infinitesimal
         rotation — A[i,j] ≈ rotation angle from PC_i toward PC_j

    The key question: are the rotation angles consistent across layers?
    Do they form a pattern (e.g., always rotate from comp→sel→term→comp)?
    """
    results = []
    for ov in overlays:
        layer = ov["layer"]
        O = ov["overlay"]  # (8, 8)

        # SVD
        U, S, Vt = np.linalg.svd(O)
        V = Vt.T

        # Polar decomposition: O = R @ P where R = U @ V^T, P = V @ S @ V^T
        R = U @ Vt
        P = V @ np.diag(S) @ Vt

        # Check if R is a proper rotation (det = +1)
        det_R = np.linalg.det(R)

        # Antisymmetric part = infinitesimal rotation generator
        A = (O - O.T) / 2

        # Extract pairwise rotation angles from antisymmetric part
        # A[i,j] ≈ θ_{ij} for small rotations
        # For the key PC pairs:
        rotation_angles = {}
        pc_labels = PC_NAMES[:8]
        for i in range(min(6, O.shape[0])):
            for j in range(i+1, min(6, O.shape[1])):
                angle_rad = A[i, j]
                angle_deg = math.degrees(angle_rad)
                if abs(angle_rad) > 0.02:  # significant rotation
                    rotation_angles[f"{pc_labels[i]}→{pc_labels[j]}"] = {
                        "rad": float(angle_rad),
                        "deg": float(angle_deg),
                    }

        # Symmetric part = stretching
        Sym = (O + O.T) / 2
        stretch_eigvals, stretch_eigvecs = np.linalg.eigh(Sym)
        stretch_eigvals = stretch_eigvals[::-1]  # descending

        # Effective rotation composition with skip connection
        # Full layer transform: I + O
        full = np.eye(O.shape[0]) + O
        full_U, full_S, full_Vt = np.linalg.svd(full)
        full_R = full_U @ full_Vt
        full_det = np.linalg.det(full_R)

        # Extract angle of rotation from I+O
        # For a rotation matrix R, tr(R) = 1 + 2cos(θ) in 3D
        # In nD: tr(R) = Σ cos(θ_i) where θ_i are rotation angles
        # in each 2D subspace
        full_trace = np.trace(full_R)
        # Average rotation angle
        n = full_R.shape[0]
        avg_cos = full_trace / n
        avg_angle = math.degrees(math.acos(max(-1, min(1, avg_cos))))

        results.append({
            "layer": layer,
            "singular_values": S.tolist(),
            "det_R": float(det_R),
            "rotation_angles": rotation_angles,
            "stretch_eigenvalues": stretch_eigvals.tolist(),
            "full_singular_values": full_S.tolist(),
            "full_det": float(full_det),
            "full_avg_rotation_deg": float(avg_angle),
            "antisymmetric": A,
            "R": R,
        })

    return results


def analyze_cross_layer_rotation_coherence(rotations: list[dict]) -> dict:
    """Check if rotations across layers form a coherent pattern.

    Questions:
      - Do the same PC pairs rotate in the same direction across layers?
      - Do rotation angles increase/decrease monotonically?
      - Is there a "rotation cycle" (comp→sel→term→comp)?
    """
    # Collect all rotation angles across layers
    all_pairs = set()
    for rot in rotations:
        all_pairs.update(rot["rotation_angles"].keys())

    pair_trajectories = {}
    for pair in sorted(all_pairs):
        trajectory = []
        for rot in rotations:
            if pair in rot["rotation_angles"]:
                trajectory.append(rot["rotation_angles"][pair]["deg"])
            else:
                trajectory.append(0.0)
        pair_trajectories[pair] = trajectory

    # Check for sign alternation (anti-phase pattern)
    alternating_pairs = []
    consistent_pairs = []
    for pair, traj in pair_trajectories.items():
        signs = [1 if v > 0 else -1 for v in traj if abs(v) > 0.5]
        if len(signs) >= 2:
            sign_changes = sum(1 for i in range(len(signs)-1)
                              if signs[i] != signs[i+1])
            if sign_changes == len(signs) - 1:
                alternating_pairs.append(pair)
            elif sign_changes == 0:
                consistent_pairs.append(pair)

    # Compose rotations: R_total = R_3 @ R_2 @ R_1 @ R_0
    R_composed = np.eye(rotations[0]["R"].shape[0])
    for rot in rotations:
        R_composed = rot["R"] @ R_composed

    # Extract composed rotation angles
    A_composed = (R_composed - R_composed.T) / 2
    composed_angles = {}
    pc_labels = PC_NAMES[:min(6, A_composed.shape[0])]
    for i in range(len(pc_labels)):
        for j in range(i+1, len(pc_labels)):
            angle = math.degrees(A_composed[i, j])
            if abs(angle) > 0.5:
                composed_angles[f"{pc_labels[i]}→{pc_labels[j]}"] = angle

    return {
        "pair_trajectories": pair_trajectories,
        "alternating_pairs": alternating_pairs,
        "consistent_pairs": consistent_pairs,
        "composed_rotation_angles": composed_angles,
        "R_composed": R_composed,
    }


# ══════════════════════════════════════════════════════════════════════
# C. ATTENTION PATTERN UNIVERSALITY
# ══════════════════════════════════════════════════════════════════════


def analyze_attention_universality(
    model: MicroModel,
    tokenizer,
) -> dict:
    """Check if attention patterns are universal across examples.

    For each example, at the boundary position (newline), which
    English tokens does each head attend to? Does Layer 3 always
    attend to the verb? Does it always bind the subject?
    """
    cfg = model.cfg
    results = []

    for ex in TEST_EXAMPLES:
        text = f"{ex['input']}\n{ex['output']}"
        tokens = tokenizer.encode(text, add_special_tokens=False)
        tokens.append(cfg.eod_id)
        if len(tokens) > cfg.max_seq_len + 1:
            tokens = tokens[:cfg.max_seq_len + 1]

        input_ids = mx.array([tokens[:-1]])
        L = input_ids.shape[1]
        token_strs = [tokenizer.decode([t]) for t in tokens[:-1]]

        # Find newline boundary
        nl_pos = None
        for pi, ts in enumerate(token_strs):
            if '\n' in ts:
                nl_pos = pi
                break

        model.set_capture(True)
        logits, _ = model(input_ids)
        mx.eval(logits)
        traces = model.get_traces()
        model.set_capture(False)

        # For each layer, at the first lambda position, what does each head attend to?
        if nl_pos is not None:
            lambda_start = nl_pos + 1 if nl_pos + 1 < L else nl_pos
        else:
            lambda_start = 0

        layer_attention = []
        for layer_trace in traces:
            attn_weights = np.array(layer_trace["attn"]["attn_weights"])
            head_patterns = []
            for h in range(cfg.n_heads):
                attn_h = attn_weights[0, h]  # (L, L)
                # At lambda_start, what English tokens get attended?
                if lambda_start < attn_h.shape[0]:
                    attn_row = attn_h[lambda_start, :lambda_start+1]
                    top_idx = np.argsort(attn_row)[-3:][::-1]
                    top_tokens = [(token_strs[k].strip(), float(attn_row[k]))
                                 for k in top_idx]
                else:
                    top_tokens = []
                head_patterns.append(top_tokens)
            layer_attention.append(head_patterns)

        results.append({
            "input": ex["input"],
            "category": ex["category"],
            "layer_attention": layer_attention,
        })

    return {"examples": results}


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════


def main(checkpoint_dir: str | None = None):
    print("=" * 70)
    print("UNIVERSALITY + ROTATION PROBE")
    print("=" * 70)

    cfg = MicroConfig()
    model = MicroModel(cfg)
    mx.eval(model.parameters())

    if checkpoint_dir:
        ckpt_path = Path(checkpoint_dir) / "model.npz"
        if ckpt_path.exists():
            print(f"Loading: {ckpt_path}")
            weights = mx.load(str(ckpt_path))
            model.load_weights(list(weights.items()))
            mx.eval(model.parameters())
            print("  Loaded ✓")

    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    crystal_emb, eigvecs, eigvals = get_crystal_basis(model)

    # ═══════════════════════════════════════════════════════
    # A. UNIVERSALITY
    # ═══════════════════════════════════════════════════════
    print(f"\n{'═' * 70}")
    print("A. UNIVERSALITY — Same mechanism across all examples?")
    print(f"{'═' * 70}")

    uni = analyze_universality(model, tokenizer, crystal_emb, eigvecs)

    # Summary table
    print(f"\n  {'Example':<45} {'Cat':<12} {'Loss':>6} | "
          f"{'PC0 amp':>8} {'PC1 amp':>8} {'PC2 amp':>8} | "
          f"{'Grad dominant (per layer)':>24}")
    print(f"  {'─'*45} {'─'*12} {'─'*6} | {'─'*8} {'─'*8} {'─'*8} | {'─'*24}")

    for ex in uni["examples"]:
        amp = ex["amplification"]
        grad_pcs = ex["grad_dominant_pcs"]
        grad_str = " ".join(f"PC{p}" for p in grad_pcs)
        print(f"  {ex['input']:<45} {ex['category']:<12} {ex['loss']:6.3f} | "
              f"{amp[0]:8.1f} {amp[1]:8.1f} {amp[2]:8.1f} | "
              f"{grad_str}")

    # Amplification statistics
    all_amps = np.array([ex["amplification"] for ex in uni["examples"]])
    print(f"\n  Amplification statistics across all examples:")
    print(f"  {'PC':<12} {'Mean':>8} {'Std':>8} {'Min':>8} {'Max':>8} {'CV':>8}")
    print(f"  {'─'*12} {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*8}")
    for i in range(8):
        vals = all_amps[:, i]
        mean = np.mean(vals)
        std = np.std(vals)
        cv = std / (mean + 1e-8)
        print(f"  {PC_NAMES[i]:<12} {mean:8.2f} {std:8.2f} "
              f"{np.min(vals):8.2f} {np.max(vals):8.2f} {cv:8.3f}")

    # Layer-by-layer PC0 trajectory comparison
    print(f"\n  PC0 (composition) trajectory through layers:")
    print(f"  {'Example':<35} | " +
          " ".join(f"{'stg'+str(i):>7}" for i in range(9)))
    for ex in uni["examples"][:6]:
        pc0 = ex["layer_pc0"]
        label = ex["input"][:33]
        print(f"  {label:<35} | " +
              " ".join(f"{v:7.2f}" for v in pc0[:9]))

    # ═══════════════════════════════════════════════════════
    # B. ROTATION EXTRACTION
    # ═══════════════════════════════════════════════════════
    print(f"\n{'═' * 70}")
    print("B. ROTATION EXTRACTION — The grating's angular structure")
    print(f"{'═' * 70}")

    overlays = extract_full_overlays(model, crystal_emb, eigvecs)
    rotations = extract_rotations(overlays)

    for rot in rotations:
        layer = rot["layer"]
        print(f"\n  Layer {layer}:")
        print(f"    Singular values: {' '.join(f'{s:.4f}' for s in rot['singular_values'][:6])}")
        print(f"    det(R) = {rot['det_R']:.4f}")
        print(f"    Full transform: avg rotation = {rot['full_avg_rotation_deg']:.1f}°")

        if rot["rotation_angles"]:
            print(f"    Significant rotations (|θ| > 1°):")
            for pair, angle in sorted(rot["rotation_angles"].items(),
                                      key=lambda x: abs(x[1]["deg"]),
                                      reverse=True):
                deg = angle["deg"]
                direction = "⟲" if deg > 0 else "⟳"
                bar = "█" * min(40, int(abs(deg) * 3))
                print(f"      {pair:<28} {direction} {deg:+6.2f}° {bar}")

        # Show the full antisymmetric matrix (rotation generator)
        A = rot["antisymmetric"]
        print(f"\n    Rotation generator (antisymmetric part, degrees):")
        labels = PC_NAMES[:6]
        header = " " * 14 + "".join(f"{l:>10}" for l in labels)
        print(f"    {header}")
        for i in range(6):
            row = f"    {labels[i]:>12} |"
            for j in range(6):
                deg = math.degrees(A[i, j])
                if abs(deg) > 1.0:
                    row += f"  {deg:+6.1f}°*"
                else:
                    row += f"  {deg:+6.1f}° "
            print(row)

    # Cross-layer coherence
    print(f"\n{'─' * 70}")
    print("  CROSS-LAYER ROTATION COHERENCE")
    print(f"{'─' * 70}")

    coherence = analyze_cross_layer_rotation_coherence(rotations)

    print(f"\n  Rotation angle trajectories (degrees per layer):")
    print(f"  {'Pair':<30} | {'L0':>7} {'L1':>7} {'L2':>7} {'L3':>7} | Pattern")
    print(f"  {'─'*30} | {'─'*7} {'─'*7} {'─'*7} {'─'*7} | {'─'*12}")
    for pair, traj in sorted(coherence["pair_trajectories"].items(),
                             key=lambda x: max(abs(v) for v in x[1]),
                             reverse=True):
        pattern = ""
        if pair in coherence["alternating_pairs"]:
            pattern = "ALTERNATING"
        elif pair in coherence["consistent_pairs"]:
            pattern = "CONSISTENT"
        print(f"  {pair:<30} | " +
              " ".join(f"{d:+7.2f}" for d in traj) +
              f" | {pattern}")

    if coherence["alternating_pairs"]:
        print(f"\n  ⚡ ALTERNATING pairs: {', '.join(coherence['alternating_pairs'])}")
    if coherence["consistent_pairs"]:
        print(f"  → CONSISTENT pairs: {', '.join(coherence['consistent_pairs'])}")

    # Composed rotation
    print(f"\n  Composed rotation angles (all 4 layers):")
    if coherence["composed_rotation_angles"]:
        for pair, angle in sorted(coherence["composed_rotation_angles"].items(),
                                  key=lambda x: abs(x[1]), reverse=True):
            print(f"    {pair:<28} {angle:+6.2f}°")
    else:
        print(f"    (no significant rotations in composed transform)")

    # Composed rotation matrix (top 6x6)
    R_comp = coherence["R_composed"][:6, :6]
    print(f"\n  Composed rotation matrix R (top 6×6):")
    labels = PC_NAMES[:6]
    header = " " * 14 + "".join(f"{l:>10}" for l in labels)
    print(f"    {header}")
    for i in range(6):
        row = f"    {labels[i]:>12} |"
        for j in range(6):
            v = R_comp[i, j]
            marker = "*" if abs(v) > 0.15 else " "
            row += f"  {v:+6.3f}{marker}"
        print(row)

    # ═══════════════════════════════════════════════════════
    # C. ATTENTION UNIVERSALITY
    # ═══════════════════════════════════════════════════════
    print(f"\n{'═' * 70}")
    print("C. ATTENTION ROUTING UNIVERSALITY")
    print(f"{'═' * 70}")

    attn_uni = analyze_attention_universality(model, tokenizer)

    print(f"\n  At the lambda boundary (first λ token), what does each head attend to?")
    print(f"\n  Layer 3 (output layer) — Head 0:")
    for ex in attn_uni["examples"]:
        if ex["layer_attention"] and len(ex["layer_attention"]) > 3:
            head0 = ex["layer_attention"][3][0]  # layer 3, head 0
            attn_str = ", ".join(f"'{t}':{w:.2f}" for t, w in head0[:3])
            print(f"    {ex['input']:<40} → {attn_str}")

    # Check for pattern: does layer 3 head 0 always attend to the verb?
    print(f"\n  All heads at lambda boundary (Layer 3):")
    for ex in attn_uni["examples"][:6]:
        print(f"\n    {ex['input']}")
        if len(ex["layer_attention"]) > 3:
            for h_idx, head_pattern in enumerate(ex["layer_attention"][3]):
                attn_str = ", ".join(f"'{t}':{w:.2f}" for t, w in head_pattern[:3])
                print(f"      H{h_idx}: {attn_str}")

    # ═══════════════════════════════════════════════════════
    # D. SYNTHESIS
    # ═══════════════════════════════════════════════════════
    print(f"\n{'═' * 70}")
    print("D. SYNTHESIS — The Complete Mechanism")
    print(f"{'═' * 70}")

    # Check universality of overlay alternation
    overlay_diags = np.array([[ov["overlay"][i, i] for i in range(8)]
                              for ov in overlays])
    print(f"\n  FFN overlay diagonal across layers:")
    print(f"  {'PC':<12} | {'L0':>7} {'L1':>7} {'L2':>7} {'L3':>7} | Pattern")
    print(f"  {'─'*12} | {'─'*7} {'─'*7} {'─'*7} {'─'*7} | {'─'*12}")
    for pc in range(8):
        vals = overlay_diags[:, pc]
        signs = ['+' if v > 0.03 else '-' if v < -0.03 else '0' for v in vals]
        sign_str = "".join(signs)
        if sign_str in ["-+-+", "+-+-"]:
            pattern = "ALTERNATING ⚡"
        elif sign_str in ["----", "++++"]:
            pattern = "MONOTONE"
        elif sign_str in ["-++−", "+--+"]:
            pattern = "SYMMETRIC"
        else:
            pattern = sign_str
        print(f"  {PC_NAMES[pc]:<12} | " +
              " ".join(f"{v:+7.3f}" for v in vals) +
              f" | {pattern}")

    # Amplification universality
    amp_cv = np.std(all_amps, axis=0) / (np.mean(all_amps, axis=0) + 1e-8)
    print(f"\n  Amplification coefficient of variation (lower = more universal):")
    for i in range(8):
        bar = "█" * min(30, int(amp_cv[i] * 30))
        universal = "✓ UNIVERSAL" if amp_cv[i] < 0.5 else "✗ variable"
        print(f"    {PC_NAMES[i]:<12}: CV={amp_cv[i]:.3f} {universal} {bar}")

    print(f"\n{'═' * 70}")
    print("PROBE COMPLETE")
    print(f"{'═' * 70}")


if __name__ == "__main__":
    ckpt = sys.argv[1] if len(sys.argv) > 1 else None
    main(ckpt)
