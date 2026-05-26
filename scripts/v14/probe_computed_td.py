#!/usr/bin/env python3
"""Probe: Can crystal eigendecomposition PREDICT TD flips?

The hypothesis: TD flips are not random corrections. They follow the
crystal eigenstructure. If so, we can COMPUTE the flip pattern from
the eigendecomposition instead of LEARNING it through gradient accumulation.

Method:
  1. Load base plate (teacher etch) and delta plate (TD's discovered flips)
  2. Load the student's learned combinator embeddings (the crystal)
  3. For each flipped out_proj layer:
     a. Project each column of base plate onto crystal eigenvectors
     b. Compute "misalignment score" — how much each position's sign
        disagrees with the dominant eigenvector for that layer
     c. Test: do high-misalignment positions predict actual TD flips?
  4. Report precision, recall, AUC
  5. Also test: can we predict flip DIRECTION from eigenvector sign?

If this works, TD becomes a computed operation: eigendecompose → predict
flips → apply. No gradient accumulation needed. The phonograph groove
is cut from the sheet music.

Usage:
    uv run python scripts/v14/probe_computed_td.py \
        --checkpoint checkpoints/v14-td/step_002000

License: MIT
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np


# ══════════════════════════════════════════════════════════════════════
# § 1  Unpack ternary (numpy version)
# ══════════════════════════════════════════════════════════════════════

def unpack_ternary_np(packed_uint32: np.ndarray) -> np.ndarray:
    """Unpack uint32 [N, K//16] → int8 {-1, 0, +1} [N, K]."""
    N, K16 = packed_uint32.shape
    K = K16 * 16
    shifts = np.arange(16, dtype=np.uint32) * 2
    expanded = packed_uint32[:, :, np.newaxis]
    fields = (expanded >> shifts) & 3
    decoded = fields.astype(np.int8) - 1
    return decoded.reshape(N, K)


# ══════════════════════════════════════════════════════════════════════
# § 2  Crystal eigenbasis from student's learned embeddings
# ══════════════════════════════════════════════════════════════════════

COMBINATOR_NAMES = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]


def crystal_from_embeddings(combinator_emb: np.ndarray) -> tuple:
    """Extract crystal eigenbasis from learned combinator embeddings.
    
    Args:
        combinator_emb: (8, d_model) combinator embeddings
    
    Returns:
        eigenvalues: (8,) descending
        eigenvectors: (8, 8) columns are eigenvectors
        emb_normed: (8, d_model) unit-normed embeddings
        cos_matrix: (8, 8) cosine similarity matrix
    """
    norms = np.linalg.norm(combinator_emb, axis=1, keepdims=True)
    emb_normed = combinator_emb / (norms + 1e-10)
    cos_matrix = emb_normed @ emb_normed.T
    
    eigenvalues, eigenvectors = np.linalg.eigh(cos_matrix)
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    
    return eigenvalues, eigenvectors, emb_normed, cos_matrix


# ══════════════════════════════════════════════════════════════════════
# § 3  Misalignment scoring
# ══════════════════════════════════════════════════════════════════════

def compute_misalignment(base_plate: np.ndarray, 
                          emb_normed: np.ndarray,
                          eigenvalues: np.ndarray,
                          eigenvectors: np.ndarray) -> np.ndarray:
    """Compute per-position misalignment score.
    
    For each position (i,j) in the base plate:
    - Row i maps to an output dimension in d_model=1280
    - Col j maps to an input dimension in d_model=1280
    - The combinator embeddings live in d_model=1280
    - We project the row/col combination onto crystal space
    
    Approach: compute the "crystal projection" of each row.
    Each row of out_proj is a readout direction in d_model space.
    Project each row onto each combinator embedding.
    The projection tells us which combinator that row "serves."
    
    Misalignment = for the dominant PC of this layer, how much does
    each position disagree with the eigenvector prediction?
    
    Returns: (N, K) float array of misalignment scores (higher = more misaligned)
    """
    N, K = base_plate.shape
    
    # Project each ROW of base_plate onto combinator embeddings
    # base_plate: (N, K) ternary {-1, 0, +1}
    # emb_normed: (8, K) where K = d_model = 1280
    # row_projections: (N, 8) — how much each row aligns with each combinator
    base_float = base_plate.astype(np.float32)
    row_projections = base_float @ emb_normed.T  # (N, 8)
    
    # Normalize row projections
    row_norms = np.linalg.norm(row_projections, axis=1, keepdims=True)
    row_proj_normed = row_projections / (row_norms + 1e-10)  # (N, 8)
    
    # For each PC, compute how well each row aligns with that PC's eigenvector
    # eigenvectors: (8, 8), columns are PCs
    # row_alignment[i, pc] = how well row i aligns with PC pc
    row_alignment = row_proj_normed @ eigenvectors  # (N, 8)
    
    # Similarly for columns — project each COLUMN onto combinator embeddings
    col_projections = base_float.T @ emb_normed.T  # (K, 8)
    col_norms = np.linalg.norm(col_projections, axis=1, keepdims=True)
    col_proj_normed = col_projections / (col_norms + 1e-10)
    col_alignment = col_proj_normed @ eigenvectors  # (K, 8)
    
    # Misalignment for each PC: positions where both row AND column
    # are at the boundary between PCs (neither strongly aligned)
    # Use absolute alignment — low absolute value = boundary = high misalignment
    misalignment_per_pc = {}
    for pc in range(min(8, eigenvectors.shape[1])):
        row_align_pc = np.abs(row_alignment[:, pc])  # (N,)
        col_align_pc = np.abs(col_alignment[:, pc])  # (K,)
        # Outer product: positions where BOTH row and col are weakly aligned
        # = boundary positions = flip candidates
        # Invert: low alignment = high misalignment
        row_misalign = 1.0 - row_align_pc  # (N,)
        col_misalign = 1.0 - col_align_pc  # (K,)
        misalignment_per_pc[pc] = np.outer(row_misalign, col_misalign)
    
    return row_alignment, col_alignment, misalignment_per_pc


def predict_flips_from_eigenvectors(base_plate: np.ndarray,
                                     emb_normed: np.ndarray,
                                     eigenvectors: np.ndarray,
                                     eigenvalues: np.ndarray) -> dict:
    """Predict which positions should flip based on crystal eigenvectors.
    
    Simple approach: for each position, compute the "crystal-preferred sign"
    by projecting the row onto the dominant eigenvector direction in 
    combinator space. If the base plate sign disagrees, predict a flip.
    
    Returns prediction quality metrics.
    """
    N, K = base_plate.shape
    base_float = base_plate.astype(np.float32)
    
    # Project rows onto combinator space
    row_projections = base_float @ emb_normed.T  # (N, 8)
    
    # For each PC, the eigenvector defines a "direction" in combinator space.
    # The sign of each row's projection onto that direction suggests whether
    # the row should be positive or negative relative to that combinator.
    predictions = {}
    for pc in range(min(6, eigenvectors.shape[1])):
        # Row's projection onto this PC
        pc_scores = row_projections @ eigenvectors[:, pc]  # (N,)
        
        # Predicted sign per row: sign of the PC score
        # This predicts whether each row should be "with" or "against" this PC
        row_predicted_sign = np.sign(pc_scores)  # (N,)
        
        # Similarly for columns
        col_projections = base_float.T @ emb_normed.T  # (K, 8)
        col_pc_scores = col_projections @ eigenvectors[:, pc]  # (K,)
        col_predicted_sign = np.sign(col_pc_scores)  # (K,)
        
        # Combined prediction: positions where the base sign disagrees with
        # what the eigenvector predicts
        # For each position (i,j): if row_sign and col_sign predict a flip...
        # Simpler: just use row-level prediction (since row_CV < col_CV but
        # flips are more structured along columns)
        predictions[pc] = {
            "row_scores": pc_scores,
            "row_predicted_sign": row_predicted_sign,
            "col_scores": col_pc_scores,
            "col_predicted_sign": col_predicted_sign,
        }
    
    return predictions


def evaluate_prediction(actual_flips: np.ndarray, 
                        predicted_scores: np.ndarray,
                        name: str) -> dict:
    """Evaluate how well a continuous score predicts binary flip/no-flip.
    
    actual_flips: (N, K) boolean
    predicted_scores: (N, K) float — higher = more likely to flip
    """
    flat_actual = actual_flips.ravel()
    flat_scores = predicted_scores.ravel()
    
    n_actual = flat_actual.sum()
    n_total = len(flat_actual)
    base_rate = n_actual / n_total
    
    if n_actual == 0 or n_actual == n_total:
        return {"name": name, "auc": 0.5, "n_actual": int(n_actual)}
    
    # Rank-based AUC approximation (fast, no sklearn needed)
    # Sort by predicted score descending
    sorted_idx = np.argsort(flat_scores)[::-1]
    sorted_actual = flat_actual[sorted_idx]
    
    # AUC = probability that a random positive is ranked above a random negative
    # Compute via rank sum
    ranks = np.arange(1, n_total + 1)
    positive_ranks = ranks[sorted_actual]
    auc = (positive_ranks.sum() - n_actual * (n_actual + 1) / 2) / (n_actual * (n_total - n_actual))
    auc = 1.0 - auc  # flip because we sorted descending
    
    # Precision/recall at various thresholds
    thresholds = [0.01, 0.05, 0.10, 0.20, 0.30, 0.50]
    pr_at_k = []
    for t in thresholds:
        k = int(n_total * t)
        if k == 0:
            continue
        top_k_actual = sorted_actual[:k].sum()
        precision = top_k_actual / k
        recall = top_k_actual / n_actual
        pr_at_k.append({
            "top_frac": t,
            "precision": float(precision),
            "recall": float(recall),
            "lift": float(precision / base_rate),
        })
    
    return {
        "name": name,
        "auc": float(auc),
        "n_actual": int(n_actual),
        "n_total": n_total,
        "base_rate": float(base_rate),
        "pr_at_k": pr_at_k,
    }


# ══════════════════════════════════════════════════════════════════════
# § 4  Main
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Can crystal eigendecomposition predict TD flips?")
    parser.add_argument("--checkpoint", type=str, required=True)
    args = parser.parse_args()
    
    ckpt_dir = Path(args.checkpoint)
    model_path = ckpt_dir / "model.npz"
    delta_path = ckpt_dir / "delta_plates.npz"
    
    print(f"Loading model from {model_path}", file=sys.stderr)
    model = np.load(str(model_path), allow_pickle=True)
    
    print(f"Loading delta plates from {delta_path}", file=sys.stderr)
    deltas = np.load(str(delta_path), allow_pickle=True)
    
    # ── Get crystal eigenbasis from student's learned embeddings ──
    combinator_emb = model['combinator_embeddings']  # (8, 1280)
    eigenvalues, eigenvectors, emb_normed, cos_matrix = crystal_from_embeddings(combinator_emb)
    
    print(f"\n{'='*75}", file=sys.stderr)
    print(f"STUDENT CRYSTAL (learned combinator embeddings)", file=sys.stderr)
    print(f"{'='*75}", file=sys.stderr)
    print(f"  Eigenvalues: {eigenvalues[:6]}", file=sys.stderr)
    print(f"  λ₀/λ₁ = {eigenvalues[0]/eigenvalues[1]:.4f}", file=sys.stderr)
    
    for pc in range(min(6, eigenvectors.shape[1])):
        ev = eigenvectors[:, pc]
        signs = ''.join('+' if v > 0 else '-' for v in ev)
        dominant = COMBINATOR_NAMES[np.argmax(np.abs(ev))]
        print(f"  PC{pc}: [{signs}]  dominant={dominant}  λ={eigenvalues[pc]:.4f}",
              file=sys.stderr)
    
    # ── Analyze each flipped out_proj layer ──
    flipped_layers = [4, 5, 6, 7, 8, 9]
    
    print(f"\n{'='*75}", file=sys.stderr)
    print(f"FLIP PREDICTION ANALYSIS", file=sys.stderr)
    print(f"{'='*75}", file=sys.stderr)
    
    for layer in flipped_layers:
        # Load base plate and delta
        base_key = f"shared_stride_stack.layers.{layer}.out_proj.base_weight"
        delta_key = f"shared_stride_stack_layers_{layer}_out_proj_delta_packed"
        
        base_packed = model[base_key]
        base_plate = unpack_ternary_np(base_packed)  # (1280, 1280)
        
        delta_packed = deltas[delta_key]
        delta_plate = unpack_ternary_np(delta_packed)  # (1280, 1280)
        
        actual_flips = (delta_plate == -1)  # boolean
        n_flips = actual_flips.sum()
        flip_rate = n_flips / delta_plate.size
        
        print(f"\n  Layer {layer} out_proj (flips: {n_flips:,} = {flip_rate:.2%})",
              file=sys.stderr)
        
        # ── Method 1: Row projection onto crystal PCs ──
        row_alignment, col_alignment, misalignment_per_pc = compute_misalignment(
            base_plate, emb_normed, eigenvalues, eigenvectors
        )
        
        # ── Method 2: Eigenvector-based flip prediction ──
        predictions = predict_flips_from_eigenvectors(
            base_plate, emb_normed, eigenvectors, eigenvalues
        )
        
        # ── Evaluate each PC as a predictor ──
        print(f"  {'─'*65}", file=sys.stderr)
        print(f"  {'PC':>4s}  {'Comb':>5s}  {'AUC':>6s}  {'Lift@10%':>9s}  "
              f"{'Prec@10%':>9s}  {'Rec@10%':>8s}  {'Direction':>10s}",
              file=sys.stderr)
        print(f"  {'─'*65}", file=sys.stderr)
        
        best_auc = 0
        best_pc = -1
        
        for pc in range(min(6, eigenvectors.shape[1])):
            # Score: absolute misalignment with this PC
            # Rows far from 0 projection = strongly aligned = less likely to flip
            # Rows near 0 projection = boundary = more likely to flip
            row_scores = predictions[pc]["row_scores"]  # (N,)
            
            # Create (N, K) score matrix
            # Method A: row boundary score (1 - |row_alignment|)
            row_boundary = 1.0 - np.abs(row_alignment[:, pc])  # (N,)
            col_boundary = 1.0 - np.abs(col_alignment[:, pc])  # (K,)
            boundary_score = np.outer(row_boundary, col_boundary)  # (N, K)
            
            # Method B: disagreement score
            # If eigenvector says row should be positive and base is negative, predict flip
            row_sign = np.sign(row_alignment[:, pc])  # (N,)
            col_sign = np.sign(col_alignment[:, pc])  # (K,)
            # Position (i,j) disagrees if base_sign(i,j) ≠ predicted pattern
            # The predicted pattern from eigenvector is: row_sign * col_sign
            predicted_pattern = np.outer(row_sign, col_sign)  # (N, K) in {-1, 0, +1}
            disagreement = (base_plate.astype(np.float32) * predicted_pattern < 0).astype(np.float32)
            
            # Method C: combined — boundary + disagreement
            combined = boundary_score * 0.5 + disagreement * 0.5
            
            # Evaluate
            eval_boundary = evaluate_prediction(actual_flips, boundary_score,
                                                 f"L{layer}_PC{pc}_boundary")
            eval_disagree = evaluate_prediction(actual_flips, disagreement,
                                                 f"L{layer}_PC{pc}_disagree")
            eval_combined = evaluate_prediction(actual_flips, combined,
                                                 f"L{layer}_PC{pc}_combined")
            
            # Pick the best method for this PC
            best_method = max([eval_boundary, eval_disagree, eval_combined],
                              key=lambda x: x["auc"])
            method_name = best_method["name"].split("_")[-1]
            
            auc = best_method["auc"]
            lift_10 = next((p["lift"] for p in best_method.get("pr_at_k", [])
                           if p["top_frac"] == 0.10), 0)
            prec_10 = next((p["precision"] for p in best_method.get("pr_at_k", [])
                           if p["top_frac"] == 0.10), 0)
            rec_10 = next((p["recall"] for p in best_method.get("pr_at_k", [])
                          if p["top_frac"] == 0.10), 0)
            
            if auc > best_auc:
                best_auc = auc
                best_pc = pc
            
            marker = " ◄◄◄" if auc > 0.55 else ""
            print(f"  PC{pc:>1d}   {COMBINATOR_NAMES[pc]:>5s}  {auc:.4f}  "
                  f"{lift_10:>8.2f}×  {prec_10:>8.2%}  {rec_10:>7.2%}  "
                  f"{method_name:>10s}{marker}",
                  file=sys.stderr)
        
        print(f"  Best: PC{best_pc} ({COMBINATOR_NAMES[best_pc]}) AUC={best_auc:.4f}",
              file=sys.stderr)
        
        # ── Row-level analysis: does row flip density correlate with PC projection? ──
        row_flip_density = actual_flips.mean(axis=1)  # (N,)
        
        print(f"\n  Row flip density vs crystal PC projection (Pearson r):",
              file=sys.stderr)
        for pc in range(min(6, eigenvectors.shape[1])):
            r = np.corrcoef(row_flip_density, np.abs(row_alignment[:, pc]))[0, 1]
            r_signed = np.corrcoef(row_flip_density, row_alignment[:, pc])[0, 1]
            bar = "+" * int(abs(r) * 40) if not np.isnan(r) else "?"
            print(f"    PC{pc} ({COMBINATOR_NAMES[pc]:>4s}): |r|={abs(r):.4f}  "
                  f"r_signed={r_signed:+.4f}  {bar}", file=sys.stderr)
        
        # ── Column-level: does column flip density correlate with PC projection? ──
        col_flip_density = actual_flips.mean(axis=0)  # (K,)
        
        print(f"\n  Col flip density vs crystal PC projection (Pearson r):",
              file=sys.stderr)
        for pc in range(min(6, eigenvectors.shape[1])):
            r = np.corrcoef(col_flip_density, np.abs(col_alignment[:, pc]))[0, 1]
            r_signed = np.corrcoef(col_flip_density, col_alignment[:, pc])[0, 1]
            bar = "+" * int(abs(r) * 40) if not np.isnan(r) else "?"
            print(f"    PC{pc} ({COMBINATOR_NAMES[pc]:>4s}): |r|={abs(r):.4f}  "
                  f"r_signed={r_signed:+.4f}  {bar}", file=sys.stderr)
    
    # ── Summary ──
    print(f"\n{'='*75}", file=sys.stderr)
    print(f"SUMMARY", file=sys.stderr)
    print(f"{'='*75}", file=sys.stderr)
    print(f"\n  If AUC > 0.55: crystal eigenvector predicts flip locations", file=sys.stderr)
    print(f"  If Lift@10% > 1.5: top 10% predicted positions contain 1.5× more flips", file=sys.stderr)
    print(f"  If row/col r > 0.3: flip density strongly correlates with crystal projection", file=sys.stderr)
    print(f"\n  AUC=0.5 means no predictive power (random).", file=sys.stderr)
    print(f"  AUC=0.7+ means the crystal eigenstructure substantially predicts TD.", file=sys.stderr)
    print(f"  AUC=0.9+ means we can COMPUTE the flips from eigendecomposition.", file=sys.stderr)
    
    print(f"\n  Done.", file=sys.stderr)


if __name__ == "__main__":
    main()
