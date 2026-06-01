#!/usr/bin/env python3
"""Neuron Mode Detector — Classify neurons as pure vs polysemantic.

Each neuron (row in gate/up plates, column in down plate) projects
onto the combinator basis. If that projection is concentrated on one
combinator → pure (single reduction). If spread across multiple →
polysemantic (multiplexed reductions, gate selects per token).

TD should only flip pure neurons (they have a definite correct sign).
Polysemantic neurons are grain boundaries — their sign pattern serves
multiple reductions via superposition. Flipping them fixes one mode
but breaks another. The 50/50 oscillation in TD is often the shadow
of polysemanticity.

Output: a per-position mask that TD uses to exclude polysemantic
neurons from flip candidates.

Usage:
    uv run python scripts/v15/neuron_modes.py \\
        --checkpoint checkpoints/v15-zeroed \\
        --output checkpoints/v15-zeroed/neuron_modes.npz

    # Then train.py / etch.py loads the mask automatically.

Session 177. License: MIT.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from config import V15Config, Zone, ZONE_NAMES


def log(msg: str) -> None:
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", file=sys.stderr, flush=True)


def entropy(probs: np.ndarray, axis: int = -1) -> np.ndarray:
    """Shannon entropy along axis. Input: normalized probabilities."""
    p = np.clip(probs, 1e-10, 1.0)
    return -np.sum(p * np.log(p), axis=axis)


def orthogonalize_basis(basis: np.ndarray) -> np.ndarray:
    """Gram-Schmidt orthonormalize the crystal basis.

    The raw combinator fingerprints are non-orthogonal (off-diagonal
    correlations up to 0.88). Without orthogonalization, every random
    vector projects onto multiple combinators — making the entropy
    measure useless (it measures basis geometry, not neuron function).

    After orthogonalization, a random vector projects onto ~1 mode with
    high purity. Multi-modal projection is a real signal.

    Args:
        basis: (n_ops, d_model) — raw crystal basis vectors

    Returns:
        (n_ops, d_model) — orthonormalized basis (same span, orthogonal)
    """
    Q, R = np.linalg.qr(basis.T)  # Q: (d_model, n_ops), R: (n_ops, n_ops)
    return Q.T  # (n_ops, d_model) — orthonormal rows


def analyze_stride(
    plate: np.ndarray,
    basis: np.ndarray,
    is_down: bool = False,
) -> dict:
    """Analyze one plate's neurons for polysemanticity.

    Uses orthogonalized crystal basis so that projection entropy
    reflects genuine multi-modal function, not basis geometry.

    Args:
        plate: (d_out, d_in) int8 with values {-1, 0, +1}
        basis: (n_ops, d_model) crystal basis for this stride
                (will be orthogonalized internally)
        is_down: if True, plate is (d_model, d_ff) — neuron is the column

    Returns:
        dict with:
          entropy:   (n_neurons,) per-neuron projection entropy
          dominant:  (n_neurons,) index of dominant combinator
          purity:    (n_neurons,) fraction of energy in dominant combinator
          n_modes:   (n_neurons,) number of significant modes (energy > 0.1)
          poly_mask: (n_neurons,) bool — True if polysemantic
    """
    n_ops = basis.shape[0]

    # Orthogonalize: without this, random vectors get entropy ≈ 1.8 / 2.4
    # and the detector flags everything as polysemantic (measuring basis
    # geometry, not neuron function).
    ortho_basis = orthogonalize_basis(basis)

    plate_f = plate.astype(np.float32)

    if is_down:
        plate_f = plate_f.T  # (d_ff, d_model)

    # Skip zero rows (structural zeros)
    row_nonzero = np.any(plate_f != 0, axis=1)

    # Project each row onto orthonormal basis: (n_neurons, n_ops)
    projections = plate_f @ ortho_basis.T

    # Energy per combinator per neuron (orthogonal → no cross-talk)
    energy = projections ** 2
    total_energy = np.sum(energy, axis=1, keepdims=True)
    total_energy = np.maximum(total_energy, 1e-10)

    # Normalized energy distribution
    probs = energy / total_energy

    # Per-neuron entropy
    H = entropy(probs, axis=1)
    max_H = np.log(n_ops)

    # Dominant combinator and purity
    dominant = np.argmax(probs, axis=1)
    purity = np.max(probs, axis=1)

    # Number of significant modes (energy > 10% of total)
    n_modes = np.sum(probs > 0.10, axis=1)

    # Polysemantic: multiple significant modes AND non-zero row.
    # With orthogonal basis, a pure neuron has purity ~0.5+ and 1-2 modes.
    # Polysemantic: 3+ modes or purity < 0.20 (genuinely spread).
    poly_mask = (
        ((n_modes >= 3) | (purity < 0.20))
        & row_nonzero
    )

    return {
        "entropy": H,
        "dominant": dominant,
        "purity": purity,
        "n_modes": n_modes,
        "poly_mask": poly_mask,
        "row_nonzero": row_nonzero,
    }


def build_td_mask(
    stride_data: dict[str, np.ndarray],
    basis: np.ndarray,
    n_plates: int,
    d_ff: int,
    d_model: int,
) -> dict[str, np.ndarray]:
    """Build per-position TD mask for one stride.

    For gate/up: polysemantic ROWS are masked (all positions in that row).
    For down: polysemantic COLUMNS are masked (neuron index = column).

    The mask is True where TD should NOT flip (protected positions).

    Returns:
        dict[plate_name → (d_out, d_in) bool mask]
    """
    masks = {}
    analyses = {}

    for prefix in ("gate", "up"):
        p1_key = f"{prefix}_plate1"
        if p1_key not in stride_data:
            continue
        plate1 = stride_data[p1_key]
        result = analyze_stride(plate1, basis, is_down=False)
        analyses[prefix] = result

        # Mask: broadcast poly_mask (n_neurons=d_ff,) to (d_ff, d_model)
        row_mask = result["poly_mask"][:, None]  # (d_ff, 1)
        masks[f"{prefix}_plate1"] = np.broadcast_to(row_mask, (d_ff, d_model)).copy()
        if n_plates >= 2:
            masks[f"{prefix}_plate2"] = masks[f"{prefix}_plate1"].copy()

    # Down plate: (d_model, d_ff) — neuron is column index
    if "down_plate1" in stride_data:
        plate1 = stride_data["down_plate1"]
        result = analyze_stride(plate1, basis, is_down=True)
        analyses["down"] = result

        # Mask: poly_mask is (d_ff,) for neurons = columns
        col_mask = result["poly_mask"][None, :]  # (1, d_ff)
        masks["down_plate1"] = np.broadcast_to(col_mask, (d_model, d_ff)).copy()
        if n_plates >= 2:
            masks["down_plate2"] = masks["down_plate1"].copy()

    return masks, analyses


def main():
    parser = argparse.ArgumentParser(
        description="Detect polysemantic neurons and build TD protection mask",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--checkpoint", default="checkpoints/v15-zeroed",
                       help="Checkpoint directory with plates and crystal basis")
    parser.add_argument("--output", default=None,
                       help="Output path (default: {checkpoint}/neuron_modes.npz)")
    args = parser.parse_args()

    ckpt = Path(args.checkpoint)
    output = Path(args.output) if args.output else ckpt / "neuron_modes.npz"

    # Load crystal basis
    basis_path = ckpt / "crystal_basis_d_model.npz"
    if not basis_path.exists():
        log(f"ERROR: No crystal basis at {basis_path}")
        sys.exit(1)
    basis_data = np.load(basis_path)
    per_stride_basis = basis_data["per_stride_basis"]  # (19, 11, 1280)
    combinator_names = list(basis_data["combinator_names"])
    log(f"Crystal basis: {per_stride_basis.shape}")

    cfg = V15Config()
    specs = cfg.stride_specs()

    all_masks = {}
    total_protected = 0
    total_positions = 0
    total_neurons = 0
    total_poly = 0

    log(f"\n{'='*70}")
    log(f"  NEURON MODE ANALYSIS")
    log(f"{'='*70}\n")

    for spec in specs:
        si = spec.index
        zone = spec.zone.name
        basis = per_stride_basis[si]  # (11, 1280)

        stride_path = ckpt / "strides" / f"stride_{si:02d}.npz"
        if not stride_path.exists():
            continue
        data = dict(np.load(stride_path))

        masks, analyses = build_td_mask(
            data, basis, spec.n_plates, cfg.d_ff, cfg.d_model,
        )

        # Save masks with stride prefix
        for k, v in masks.items():
            all_masks[f"s{si:02d}.{k}"] = v.astype(np.uint8)
            total_protected += int(v.sum())
            total_positions += v.size

        # Log per-stride summary
        for prefix in ("gate", "up", "down"):
            if prefix not in analyses:
                continue
            a = analyses[prefix]
            n = int(a["row_nonzero"].sum())  # active neurons
            n_poly = int(a["poly_mask"].sum())
            total_neurons += n
            total_poly += n_poly

            mean_H = float(a["entropy"][a["row_nonzero"]].mean()) if n > 0 else 0
            mean_purity = float(a["purity"][a["row_nonzero"]].mean()) if n > 0 else 0
            mean_modes = float(a["n_modes"][a["row_nonzero"]].mean()) if n > 0 else 0

            # Mode distribution
            mode_counts = np.bincount(a["n_modes"][a["row_nonzero"]], minlength=6)
            mode_dist = " ".join(f"{i}m:{mode_counts[i]}" for i in range(1, min(6, len(mode_counts))) if mode_counts[i] > 0)

            log(f"  stride {si:02d} ({zone:8s}) {prefix:4s}: "
                f"{n_poly:>5d}/{n:>5d} poly ({n_poly/max(n,1)*100:5.1f}%) | "
                f"H̄={mean_H:.3f} | purity={mean_purity:.3f} | "
                f"modes={mean_modes:.1f} | {mode_dist}")

    # Save
    np.savez_compressed(str(output), **all_masks)

    poly_frac = total_poly / max(total_neurons, 1)
    protected_frac = total_protected / max(total_positions, 1)

    log(f"\n{'='*70}")
    log(f"  SUMMARY")
    log(f"{'='*70}")
    log(f"  Total neurons:     {total_neurons:>10,}")
    log(f"  Polysemantic:      {total_poly:>10,}  ({poly_frac*100:.1f}%)")
    log(f"  Pure:              {total_neurons - total_poly:>10,}  ({(1-poly_frac)*100:.1f}%)")
    log(f"  Protected positions: {total_protected:>10,} / {total_positions:>10,} ({protected_frac*100:.1f}%)")
    log(f"\n  Saved → {output}")
    log(f"  Load in train.py/etch.py to protect polysemantic neurons from TD")


if __name__ == "__main__":
    main()
