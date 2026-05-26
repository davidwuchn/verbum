"""
Probe Composed Direction — What does the grating cascade point toward?

THE QUESTION: The compound grating (4 FFN overlays composed) collapses
to PR=1.4 — nearly rank-1. What IS that dominant direction? Does it
predict the output? Is it universal or per-input? How does it rotate
through the cascade?

Measurements:
  1. Extract the dominant direction of the composed grating
  2. Decompose it in crystal eigenbasis — which combinators?
  3. Track how the dominant direction rotates after each layer
  4. Compare the total rotation to arccos(λ₁/λ₀) = 47.1°
  5. Per-example: correlate the dominant direction with actual
     residual stream at output — does it predict the output?
  6. Per-category: does the direction change by input type?
  7. The intermediate directions (after L0, L1, L2) — rotation path

Usage:
    cd verbum
    uv run python scripts/micro/probe_composed_direction.py [checkpoint_dir]

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
# Crystal tools
# ══════════════════════════════════════════════════════════════════════

def get_crystal_eigenbasis() -> tuple[np.ndarray, np.ndarray]:
    data = _precompute_parity_eigenbasis(PCAQ_ZONE_B_TARGETS)
    return data["eigvecs"], data["eigvals"]


def project_to_crystal(tensor: np.ndarray, crystal_emb: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(crystal_emb, axis=1, keepdims=True) + 1e-8
    crystal_norm = crystal_emb / norms
    return tensor @ crystal_norm.T


def project_to_eigenbasis(tensor: np.ndarray, crystal_emb: np.ndarray,
                          eigvecs: np.ndarray) -> np.ndarray:
    crystal_proj = project_to_crystal(tensor, crystal_emb)
    return crystal_proj @ eigvecs


# ══════════════════════════════════════════════════════════════════════
# Compound grating extraction
# ══════════════════════════════════════════════════════════════════════

def extract_overlay_matrices(model: MicroModel, crystal_emb: np.ndarray,
                              eigvecs: np.ndarray) -> list[np.ndarray]:
    """Extract the 16×16 FFN overlay matrix per layer in crystal eigenbasis."""
    norms = np.linalg.norm(crystal_emb, axis=1, keepdims=True) + 1e-8
    crystal_norm = crystal_emb / norms

    overlays = []
    for block in model.blocks:
        ffn = block.ffn
        gate_w = np.array(ffn.gate_proj.weight)   # (d_ff, d_model)
        value_w = np.array(ffn.value_proj.weight)  # (d_model, d_ff)

        gate_crystal = gate_w @ crystal_norm.T     # (d_ff, 16)
        gate_eigen = gate_crystal @ eigvecs        # (d_ff, 16)
        value_crystal = crystal_norm @ value_w     # (16, d_ff)
        value_eigen = eigvecs.T @ value_crystal    # (16, d_ff)

        overlay = gate_eigen.T @ value_eigen.T     # (16, 16)
        overlays.append(overlay)

    return overlays


def compose_overlays(overlays: list[np.ndarray]) -> list[np.ndarray]:
    """Compose overlay matrices progressively, returning intermediate compositions.

    Returns [identity, after_L0, after_L0L1, after_L0L1L2, after_L0L1L2L3].
    Each normalized by Frobenius norm to track structure not magnitude.
    """
    chain = [np.eye(16)]  # identity = before any grating
    composed = np.eye(16)
    for ov in overlays:
        ov_normed = ov / (np.linalg.norm(ov, 'fro') + 1e-8)
        composed = ov_normed @ composed
        chain.append(composed.copy())
    return chain


def extract_dominant_direction(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """SVD of matrix → dominant left singular vector, right singular vector, singular values."""
    u, s, vh = np.linalg.svd(matrix)
    return u[:, 0], vh[0, :], s


def angle_between(v1: np.ndarray, v2: np.ndarray) -> float:
    """Angle in degrees between two vectors."""
    cos = np.clip(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-12), -1, 1)
    return float(np.degrees(np.arccos(np.abs(cos))))


# ══════════════════════════════════════════════════════════════════════
# Data loading
# ══════════════════════════════════════════════════════════════════════

def load_examples(path: str, n: int = 50) -> list[dict]:
    examples = []
    with open(path) as f:
        for line in f:
            examples.append(json.loads(line))
            if len(examples) >= n:
                break
    return examples


def tokenize_example(example: dict, tokenizer) -> tuple[mx.array, mx.array]:
    text = example["input"] + "\n" + example["output"]
    tokens = tokenizer.encode(text)
    if len(tokens) > 128:
        tokens = tokens[:128]
    input_ids = mx.array([tokens[:-1]])
    targets = mx.array([tokens[1:]])
    return input_ids, targets


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    checkpoint_dir = sys.argv[1] if len(sys.argv) > 1 else "checkpoints/micro/final"
    checkpoint_path = Path(checkpoint_dir)
    if not checkpoint_path.exists():
        checkpoint_path = Path(__file__).parent.parent.parent / checkpoint_dir
    assert checkpoint_path.exists(), f"Checkpoint not found: {checkpoint_path}"

    results_dir = Path(__file__).parent.parent.parent / "results" / "composed-direction"
    results_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("Composed Direction Probe — What does the grating cascade point toward?")
    print("=" * 70)

    # ── Load model ──
    print(f"\nLoading model from {checkpoint_path}...")
    cfg = MicroConfig()
    model = MicroModel(cfg)
    weights = mx.load(str(checkpoint_path / "model.npz"))
    model.load_weights(list(weights.items()))
    mx.eval(model.parameters())
    print("  Model loaded ✓")

    # ── Crystal ──
    crystal_emb = np.array(model.get_all_crystal_embeddings())
    eigvecs, eigvals = get_crystal_eigenbasis()
    print(f"  Crystal eigenvalues: {eigvals[:4]}")

    # Theoretical rotation angle from mechanism-extraction
    theory_angle = float(np.degrees(np.arccos(eigvals[1] / eigvals[0])))
    print(f"  Theoretical rotation arccos(λ₁/λ₀) = {theory_angle:.1f}°")

    # ── Extract and compose overlay matrices ──
    overlays = extract_overlay_matrices(model, crystal_emb, eigvecs)
    composed_chain = compose_overlays(overlays)

    print("\n" + "=" * 70)
    print("1. DOMINANT DIRECTION AT EACH CASCADE STAGE")
    print("=" * 70)

    # Track the dominant direction through the cascade
    dominant_left_dirs = []   # output direction (what the cascade produces)
    dominant_right_dirs = []  # input direction (what the cascade selects from)
    all_svs = []

    PC_NAMES = COMBINATOR_NAMES + [f"ā{n}" for n in COMBINATOR_NAMES]

    for i, comp in enumerate(composed_chain):
        left_dir, right_dir, svs = extract_dominant_direction(comp)
        dominant_left_dirs.append(left_dir)
        dominant_right_dirs.append(right_dir)
        all_svs.append(svs)

        stage = "identity" if i == 0 else f"after L{i-1}"
        pr = (svs.sum() ** 2) / (np.sum(svs ** 2) + 1e-12)

        # Decompose dominant output direction in crystal eigenbasis
        # The eigenbasis IS the coordinate system, so left_dir components
        # directly correspond to PCs
        print(f"\n  {stage} (PR={pr:.2f}, SV₁={svs[0]:.4f}, SV₂={svs[1]:.4f}):")

        # Top contributors to the dominant OUTPUT direction
        abs_left = np.abs(left_dir)
        top_out = np.argsort(abs_left)[::-1][:4]
        print(f"    Output direction (where it points):")
        for idx in top_out:
            name = PC_NAMES[idx]
            print(f"      {name:>6}: {left_dir[idx]:+.4f} ({abs_left[idx]/abs_left.sum()*100:.1f}%)")

        # Top contributors to the dominant INPUT direction
        abs_right = np.abs(right_dir)
        top_in = np.argsort(abs_right)[::-1][:4]
        print(f"    Input direction (what it selects from):")
        for idx in top_in:
            name = PC_NAMES[idx]
            print(f"      {name:>6}: {right_dir[idx]:+.4f} ({abs_right[idx]/abs_right.sum()*100:.1f}%)")

    # ── Rotation through the cascade ──
    print("\n" + "=" * 70)
    print("2. ROTATION OF DOMINANT DIRECTION THROUGH CASCADE")
    print("=" * 70)

    total_rotation = 0.0
    for i in range(1, len(dominant_left_dirs)):
        angle = angle_between(dominant_left_dirs[i-1], dominant_left_dirs[i])
        total_rotation += angle
        stage_from = "identity" if i-1 == 0 else f"L{i-2}"
        stage_to = f"L{i-1}"
        print(f"  {stage_from:>8} → {stage_to}: {angle:.1f}°")

    print(f"\n  Total rotation:     {total_rotation:.1f}°")
    print(f"  Theoretical target: {theory_angle:.1f}° [arccos(λ₁/λ₀)]")
    print(f"  Error:              {abs(total_rotation - theory_angle):.1f}°")

    # Also measure in the comp↔sel (PC0↔PC1) plane specifically
    print(f"\n  Comp↔Sel plane analysis:")
    for i, left in enumerate(dominant_left_dirs):
        stage = "identity" if i == 0 else f"after L{i-1}"
        pc0 = left[0]  # composition
        pc1 = left[1]  # selection
        angle_in_plane = float(np.degrees(np.arctan2(pc1, pc0)))
        frac_in_plane = (pc0**2 + pc1**2) / (np.sum(left**2) + 1e-12)
        print(f"    {stage:>12}: PC0={pc0:+.4f} PC1={pc1:+.4f} "
              f"angle={angle_in_plane:+.1f}° "
              f"({frac_in_plane*100:.1f}% energy in plane)")

    # ── Now: per-example analysis ──
    print("\n" + "=" * 70)
    print("3. PER-EXAMPLE: DOES THE DOMINANT DIRECTION PREDICT OUTPUT?")
    print("=" * 70)

    # Load tokenizer and data
    try:
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B", trust_remote_code=True)
    except Exception:
        tokenizer = None

    data_path = Path(__file__).parent.parent.parent / "data" / "compile-eval.jsonl"
    if not data_path.exists():
        data_path = Path(__file__).parent.parent.parent / "data" / "compile-test.jsonl"
    examples = load_examples(str(data_path), n=30)
    print(f"  Loaded {len(examples)} examples")

    # The final composed grating's dominant direction
    final_left, final_right, final_svs = extract_dominant_direction(composed_chain[-1])

    # Per-example: project the output residual onto the dominant direction
    category_results = {}
    example_results = []

    for ex_idx, example in enumerate(examples):
        if tokenizer is not None:
            input_ids, targets = tokenize_example(example, tokenizer)
        else:
            text = example["input"] + "\n" + example["output"]
            tokens = [ord(c) % 1000 for c in text]
            input_ids = mx.array([tokens[:-1]])
            targets = mx.array([tokens[1:]])

        # Forward with traces
        model.set_capture(True)
        logits, loss = model(input_ids, targets)
        mx.eval(logits, loss)
        traces = model.get_traces()
        for t in traces:
            for section in ["block", "attn", "ffn"]:
                for k, v in t[section].items():
                    if isinstance(v, mx.array):
                        mx.eval(v)
        model.set_capture(False)

        # Get final residual (after L3, before output norm)
        final_residual = np.array(traces[-1]["block"]["residual_post_ffn"])[0]  # (L, d_model)

        # Project residual into crystal eigenbasis
        residual_eigen = project_to_eigenbasis(final_residual, crystal_emb, eigvecs)  # (L, 16)

        # Mean residual direction (averaged over positions)
        mean_residual_eigen = np.mean(residual_eigen, axis=0)  # (16,)
        mean_residual_norm = mean_residual_eigen / (np.linalg.norm(mean_residual_eigen) + 1e-12)

        # Projection of residual onto the composed grating's dominant output direction
        projection = float(np.dot(mean_residual_norm, final_left))

        # Also: per-position projection (how aligned is each position?)
        pos_projections = []
        for pos in range(residual_eigen.shape[0]):
            pos_norm = residual_eigen[pos] / (np.linalg.norm(residual_eigen[pos]) + 1e-12)
            pos_projections.append(float(np.dot(pos_norm, final_left)))

        # Also: which layer's composed direction best predicts the final residual?
        layer_alignment = []
        for layer_idx in range(len(composed_chain)):
            left_dir = dominant_left_dirs[layer_idx]
            cos = float(np.dot(mean_residual_norm, left_dir))
            layer_alignment.append(cos)

        # Track per-layer residual evolution
        per_layer_residual_proj = []
        for layer_idx, trace in enumerate(traces):
            layer_res = np.array(trace["block"]["residual_post_ffn"])[0]  # (L, d_model)
            layer_res_eigen = project_to_eigenbasis(layer_res, crystal_emb, eigvecs)
            mean_res = np.mean(layer_res_eigen, axis=0)
            mean_res_norm = mean_res / (np.linalg.norm(mean_res) + 1e-12)
            # Project onto the CORRESPONDING composed direction
            if layer_idx + 1 < len(composed_chain):
                corresponding_dir = dominant_left_dirs[layer_idx + 1]
                proj = float(np.dot(mean_res_norm, corresponding_dir))
            else:
                proj = float(np.dot(mean_res_norm, final_left))
            per_layer_residual_proj.append(proj)

        cat = example.get("category", "unknown")
        er = {
            "index": ex_idx,
            "category": cat,
            "input": example["input"][:60],
            "loss": float(loss.item()),
            "projection_onto_dominant": projection,
            "mean_pos_projection": float(np.mean(pos_projections)),
            "std_pos_projection": float(np.std(pos_projections)),
            "layer_alignment": layer_alignment,
            "per_layer_residual_proj": per_layer_residual_proj,
        }
        example_results.append(er)

        if cat not in category_results:
            category_results[cat] = []
        category_results[cat].append(er)

    # Print per-example summary
    print(f"\n  {'#':>3} {'Category':>18} {'Input':>35} | {'Proj':>6} {'PosStd':>6} | L_align")
    print("  " + "-" * 105)
    for er in example_results[:20]:
        la = er["layer_alignment"]
        la_str = " ".join(f"{v:+.3f}" for v in la)
        print(f"  {er['index']:>3} {er['category']:>18} {er['input']:>35} | "
              f"{er['projection_onto_dominant']:+.3f} {er['std_pos_projection']:.3f} | {la_str}")

    # ── Category analysis ──
    print("\n" + "=" * 70)
    print("4. PER-CATEGORY: IS THE DOMINANT DIRECTION UNIVERSAL?")
    print("=" * 70)

    print(f"\n  {'Category':>18} | {'N':>3} | {'Mean Proj':>9} {'Std':>6} | "
          f"{'Mean Loss':>9} | {'Per-layer residual proj':>30}")
    print("  " + "-" * 95)
    for cat, results in sorted(category_results.items()):
        projs = [r["projection_onto_dominant"] for r in results]
        losses = [r["loss"] for r in results]
        # Per-layer mean
        n_layers = len(results[0]["per_layer_residual_proj"])
        per_layer = [np.mean([r["per_layer_residual_proj"][l] for r in results]) for l in range(n_layers)]
        pl_str = " ".join(f"{v:+.3f}" for v in per_layer)
        print(f"  {cat:>18} | {len(results):>3} | {np.mean(projs):+9.4f} {np.std(projs):6.4f} | "
              f"{np.mean(losses):9.4f} | {pl_str}")

    # Overall statistics
    all_projs = [r["projection_onto_dominant"] for r in example_results]
    print(f"\n  Overall: mean_proj = {np.mean(all_projs):+.4f} ± {np.std(all_projs):.4f}")
    print(f"  Projection range: [{np.min(all_projs):+.4f}, {np.max(all_projs):+.4f}]")

    # ── Correlate projection with loss ──
    all_losses = [r["loss"] for r in example_results]
    proj_loss_corr = float(np.corrcoef(all_projs, all_losses)[0, 1])
    print(f"  Correlation(projection, loss): r = {proj_loss_corr:.4f}")

    # ── The dominant direction decomposition ──
    print("\n" + "=" * 70)
    print("5. THE DOMINANT DIRECTION — FULL DECOMPOSITION")
    print("=" * 70)

    print("\n  Final composed grating SVD:")
    print(f"    Singular values: {final_svs[:6]}")
    print(f"    SV ratios: SV₁/SV₂ = {final_svs[0]/final_svs[1]:.1f}, "
          f"SV₁/SV₃ = {final_svs[0]/final_svs[2]:.1f}")
    pr = (final_svs.sum()**2) / (np.sum(final_svs**2) + 1e-12)
    print(f"    Participation ratio: {pr:.2f}")

    print(f"\n  OUTPUT direction (left SV₁) — full 16-component:")
    for i, val in enumerate(final_left):
        name = PC_NAMES[i]
        bar = "█" * int(abs(val) * 50)
        sign = "+" if val > 0 else "-"
        print(f"    {name:>6}: {val:+.4f} {sign}{bar}")

    print(f"\n  INPUT direction (right SV₁) — full 16-component:")
    for i, val in enumerate(final_right):
        name = PC_NAMES[i]
        bar = "█" * int(abs(val) * 50)
        sign = "+" if val > 0 else "-"
        print(f"    {name:>6}: {val:+.4f} {sign}{bar}")

    # ── Comp/Sel plane ──
    out_comp = final_left[0]
    out_sel = final_left[1]
    in_comp = final_right[0]
    in_sel = final_right[1]
    out_angle = float(np.degrees(np.arctan2(out_sel, out_comp)))
    in_angle = float(np.degrees(np.arctan2(in_sel, in_comp)))
    out_frac = (out_comp**2 + out_sel**2) / (np.sum(final_left**2) + 1e-12)
    in_frac = (in_comp**2 + in_sel**2) / (np.sum(final_right**2) + 1e-12)

    print(f"\n  Comp↔Sel plane:")
    print(f"    Output: angle={out_angle:+.1f}° ({out_frac*100:.1f}% of energy in plane)")
    print(f"    Input:  angle={in_angle:+.1f}° ({in_frac*100:.1f}% of energy in plane)")
    print(f"    Rotation output-input: {abs(out_angle - in_angle):.1f}°")

    # ── Layer-by-layer: where does each grating rotate the direction? ──
    print("\n" + "=" * 70)
    print("6. PER-GRATING ROTATION DECOMPOSITION")
    print("=" * 70)

    # For each individual overlay, compute its effect on the dominant direction
    # Apply each overlay to the INPUT dominant direction of the NEXT composed stage
    for i, ov in enumerate(overlays):
        ov_normed = ov / (np.linalg.norm(ov, 'fro') + 1e-8)
        # This overlay's action in the comp↔sel plane
        # Extract the 2×2 submatrix for PC0 (comp) and PC1 (sel)
        sub = ov_normed[:2, :2]
        # Rotation component (antisymmetric part)
        antisym = (sub - sub.T) / 2
        rotation_strength = antisym[0, 1]  # positive = comp→sel rotation
        # Scaling component (symmetric part)
        sym = (sub + sub.T) / 2
        comp_scale = sym[0, 0]
        sel_scale = sym[1, 1]
        cross_scale = sym[0, 1]

        # Full overlay: what fraction of energy is in comp↔sel plane?
        sub_energy = np.sum(sub**2)
        full_energy = np.sum(ov_normed**2)
        plane_frac = sub_energy / (full_energy + 1e-12)

        # The overlay's alternation sign
        diag = np.diag(ov_normed)

        print(f"\n  Layer {i} overlay:")
        print(f"    Diag[comp,sel] = [{diag[0]:+.4f}, {diag[1]:+.4f}] "
              f"(alternation: {'comp−/sel+' if diag[0]<0 else 'comp+/sel−'})")
        print(f"    2×2 comp↔sel submatrix:")
        print(f"      [{sub[0,0]:+.4f}  {sub[0,1]:+.4f}]")
        print(f"      [{sub[1,0]:+.4f}  {sub[1,1]:+.4f}]")
        print(f"    Rotation strength (antisym[0,1]): {rotation_strength:+.4f}")
        print(f"    Comp scale: {comp_scale:+.4f}, Sel scale: {sel_scale:+.4f}")
        print(f"    Cross-coupling: {cross_scale:+.4f}")
        print(f"    Plane energy fraction: {plane_frac:.1%}")

    # ── Save results ──
    summary = {
        "theory_angle": theory_angle,
        "measured_total_rotation": total_rotation,
        "rotation_error": abs(total_rotation - theory_angle),
        "final_pr": float(pr),
        "final_sv_ratio_12": float(final_svs[0] / final_svs[1]),
        "final_output_direction": final_left.tolist(),
        "final_input_direction": final_right.tolist(),
        "final_svs": final_svs[:8].tolist(),
        "comp_sel_output_angle": out_angle,
        "comp_sel_input_angle": in_angle,
        "comp_sel_output_energy_frac": float(out_frac),
        "comp_sel_input_energy_frac": float(in_frac),
        "proj_loss_correlation": proj_loss_corr,
        "per_category": {
            cat: {
                "n": len(results),
                "mean_proj": float(np.mean([r["projection_onto_dominant"] for r in results])),
                "std_proj": float(np.std([r["projection_onto_dominant"] for r in results])),
                "mean_loss": float(np.mean([r["loss"] for r in results])),
            }
            for cat, results in category_results.items()
        },
        "cascade_rotation": [
            {
                "stage": f"L{i-1}" if i > 0 else "identity",
                "pr": float((all_svs[i].sum()**2) / (np.sum(all_svs[i]**2) + 1e-12)),
                "dominant_output_dir_top4": [
                    {"pc": PC_NAMES[j], "value": float(dominant_left_dirs[i][j])}
                    for j in np.argsort(np.abs(dominant_left_dirs[i]))[::-1][:4]
                ],
            }
            for i in range(len(composed_chain))
        ],
    }

    out_path = results_dir / "summary.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
