#!/usr/bin/env python3
"""Apply structural zeros to an existing v15 checkpoint.

Reads an already-extracted checkpoint, reconstructs per-position magnitude
from the 2-plate decomposition (plate1*gamma1 + plate2*gamma2), applies
a per-row magnitude threshold to zero the bottom 30%, recomputes gammas
over non-zero positions, and saves the zeroed checkpoint.

For 1-plate strides (CLASSIFY): uses avg_magnitude saved during extraction
if available, otherwise reconstructs magnitude as uniform plate1*gamma1
and zeros positions where the absolute contribution is smallest per row.

Why this exists:
  The original v15 extraction (session 176) produced plates with no
  structural zeros — every position is ±1. Session 177 identified that
  the bottom ~30% of positions by magnitude are irreducible fixed points
  where GD deposited near-zero weights across teacher layers. These
  should be structural zeros: "nothing computes here."

  Re-extraction from the 27B teacher is expensive. This script applies
  zeros post-hoc using the magnitude information already encoded in the
  2-plate decomposition (97% accurate per mirror findings).

Usage:
    uv run python scripts/v15/apply_zeros.py \\
        --input checkpoints/v15-extracted \\
        --output checkpoints/v15-zeroed \\
        --zero-frac 0.30

Session 177. License: MIT.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from config import V15Config, Zone, ZONE_NAMES


def log(msg: str) -> None:
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", file=sys.stderr, flush=True)


def apply_zeros_to_stride(
    data: dict[str, np.ndarray],
    n_plates: int,
    zero_frac: float,
    stride_idx: int,
) -> dict[str, np.ndarray]:
    """Apply structural zeros to one stride's plates.

    For 2-plate strides:
      1. Reconstruct magnitude: |plate1 * gamma1 + plate2 * gamma2| per position
      2. Per-row threshold: bottom zero_frac → zero in BOTH plates
      3. Recompute gammas over non-zero positions

    For 1-plate strides:
      1. Use avg_magnitude if saved during extraction, else plate1 * gamma1
      2. Same per-row threshold and gamma recomputation

    Returns new data dict with zeroed plates and updated gammas.
    """
    result = dict(data)  # shallow copy

    for prefix in ("gate", "up", "down"):
        p1_key = f"{prefix}_plate1"
        g1_key = f"{prefix}_gamma1"
        if p1_key not in data:
            continue

        plate1 = data[p1_key].astype(np.float32)
        gamma1 = data[g1_key].astype(np.float32)
        d_out, d_in = plate1.shape

        # Reconstruct per-position magnitude
        if n_plates >= 2:
            p2_key = f"{prefix}_plate2"
            g2_key = f"{prefix}_gamma2"
            plate2 = data[p2_key].astype(np.float32)
            gamma2 = data[g2_key].astype(np.float32)
            # Full 2-plate reconstruction: plate1*gamma1 + plate2*gamma2
            magnitude = np.abs(
                plate1 * gamma1[:, None] + plate2 * gamma2[:, None]
            )
        else:
            # 1-plate: check for saved avg_magnitude from extraction
            avg_mag_key = f"{prefix}_avg_magnitude"
            if avg_mag_key in data:
                magnitude = data[avg_mag_key].astype(np.float32)
            else:
                # Fallback: uniform magnitude per row (plate1 * gamma1)
                # For 1-plate, use gamma as the per-row signal.
                # Zero entire rows where gamma is in the bottom zero_frac.
                magnitude = np.abs(plate1) * gamma1[:, None]

        # Global threshold across the entire plate (not per-row).
        # The 2-plate reconstruction has only 2 magnitude levels per row
        # (|γ1+γ2| and |γ1-γ2|), so per-row threshold can't achieve 30%.
        # Global threshold catches rows where the "small" level is near zero
        # (γ1 ≈ γ2 → |γ1-γ2| ≈ 0 → those positions are at the noise floor).
        flat = magnitude.ravel()
        target_n = max(1, int(len(flat) * zero_frac))
        target_n = min(target_n, len(flat) - d_out)  # leave ≥1 non-zero per row
        threshold = np.partition(flat, target_n)[target_n]
        zero_mask = magnitude < threshold

        # Ensure at least 1 non-zero per row
        all_zero_rows = np.all(zero_mask, axis=1)
        if all_zero_rows.any():
            # For fully-zeroed rows, keep the max-magnitude position
            for row in np.where(all_zero_rows)[0]:
                best_col = np.argmax(magnitude[row])
                zero_mask[row, best_col] = False

        # Reconstruct signed weights for gamma recomputation
        if n_plates >= 2:
            W_recon = plate1 * gamma1[:, None] + plate2 * gamma2[:, None]
        else:
            W_recon = plate1 * gamma1[:, None]

        nonzero_mask = ~zero_mask
        nonzero_count = np.maximum(np.sum(nonzero_mask, axis=1).astype(np.float32), 1.0)

        # Apply zeros to plate1 and recompute gamma1
        new_plate1 = plate1.copy()
        new_plate1[zero_mask] = 0

        new_gamma1 = np.sqrt(
            np.sum(W_recon ** 2 * nonzero_mask, axis=1) / nonzero_count
        ).astype(np.float32)

        result[p1_key] = new_plate1.astype(np.int8)
        result[g1_key] = new_gamma1

        # Apply zeros to plate2 (same mask — structural absence)
        if n_plates >= 2:
            new_plate2 = plate2.copy()
            new_plate2[zero_mask] = 0

            # Gamma2 from residual at non-zero positions
            reconstructed1 = new_plate1 * new_gamma1[:, None]
            residual = (W_recon - reconstructed1) * nonzero_mask
            new_gamma2 = np.sqrt(
                np.sum(residual ** 2, axis=1) / nonzero_count
            ).astype(np.float32)

            result[p2_key] = new_plate2.astype(np.int8)
            result[g2_key] = new_gamma2

        # Update zeros mask
        result[f"{prefix}_zeros_mask"] = zero_mask.astype(np.uint8)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Apply structural zeros to existing v15 checkpoint",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--input", default="checkpoints/v15-extracted",
                       help="Input checkpoint directory")
    parser.add_argument("--output", default="checkpoints/v15-zeroed",
                       help="Output checkpoint directory")
    parser.add_argument("--zero-frac", type=float, default=0.30,
                       help="Fraction of positions per row to zero (by magnitude)")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)

    if not input_dir.exists():
        log(f"ERROR: Input checkpoint not found: {input_dir}")
        sys.exit(1)

    log(f"Applying structural zeros to {input_dir}")
    log(f"  zero_frac = {args.zero_frac}")
    log(f"  output → {output_dir}")

    # Load config
    cfg = V15Config()
    with open(input_dir / "config.json") as f:
        cfg_data = json.load(f)

    specs = cfg.stride_specs()

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Copy non-stride files
    for item in ["config.json", "v_proj.npy", "embedding.npz", "crystal_basis_d_model.npz",
                  "state.json"]:
        src = input_dir / item
        if src.exists():
            shutil.copy2(src, output_dir / item)

    # Copy attention dir (unchanged)
    attn_src = input_dir / "attention"
    attn_dst = output_dir / "attention"
    if attn_src.exists():
        if attn_dst.exists():
            shutil.rmtree(attn_dst)
        shutil.copytree(attn_src, attn_dst)

    # Process strides
    strides_out = output_dir / "strides"
    strides_out.mkdir(parents=True, exist_ok=True)

    total_zeros_before = 0
    total_zeros_after = 0
    total_positions = 0
    per_zone_zeros: dict[str, dict] = {}

    for spec in specs:
        si = spec.index
        zone_name = spec.zone.name
        stride_path = input_dir / "strides" / f"stride_{si:02d}.npz"

        if not stride_path.exists():
            log(f"  stride {si:02d}: MISSING, skipping")
            continue

        data = dict(np.load(stride_path))

        # Count zeros before
        zeros_before = sum(
            np.sum(data[k] == 0)
            for k in data if "plate" in k and "zeros" not in k
        )
        positions = sum(
            data[k].size
            for k in data if "plate" in k and "zeros" not in k
        )

        # Apply zeros
        new_data = apply_zeros_to_stride(data, spec.n_plates, args.zero_frac, si)

        # Count zeros after
        zeros_after = sum(
            np.sum(new_data[k] == 0)
            for k in new_data if "plate" in k and "zeros" not in k
        )

        # Save
        np.savez(strides_out / f"stride_{si:02d}.npz", **new_data)

        new_zeros = zeros_after - zeros_before
        zero_pct = zeros_after / max(positions, 1) * 100

        log(f"  stride {si:02d} ({zone_name:8s}): "
            f"+{new_zeros:>8,} zeros → {zeros_after:>8,} / {positions:>10,} ({zero_pct:.1f}%)")

        total_zeros_before += zeros_before
        total_zeros_after += zeros_after
        total_positions += positions

        if zone_name not in per_zone_zeros:
            per_zone_zeros[zone_name] = {"zeros": 0, "total": 0}
        per_zone_zeros[zone_name]["zeros"] += zeros_after
        per_zone_zeros[zone_name]["total"] += positions

    # Summary
    log(f"\n{'='*60}")
    log(f"  ZERO PLACEMENT SUMMARY")
    log(f"{'='*60}")
    log(f"  Total: {total_zeros_before:,} → {total_zeros_after:,} zeros "
        f"({total_zeros_after/max(total_positions,1)*100:.2f}% of {total_positions:,} positions)")

    log(f"\n  Per zone:")
    for zname, zdata in per_zone_zeros.items():
        frac = zdata["zeros"] / max(zdata["total"], 1)
        bar = "█" * int(frac * 100) + "░" * (30 - int(frac * 100))
        log(f"    {zname:8s}: {zdata['zeros']:>10,} / {zdata['total']:>10,} ({frac*100:.1f}%)  {bar}")

    # Save metadata
    meta = {
        "source": str(args.input),
        "zero_frac": args.zero_frac,
        "total_zeros": int(total_zeros_after),
        "total_positions": int(total_positions),
        "zero_rate": float(total_zeros_after / max(total_positions, 1)),
        "per_zone": {z: {"zeros": int(d["zeros"]), "total": int(d["total"]),
                         "frac": float(d["zeros"] / max(d["total"], 1))}
                     for z, d in per_zone_zeros.items()},
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    with open(output_dir / "zero_placement.json", "w") as f:
        json.dump(meta, f, indent=2)

    log(f"\n✅ Zeroed checkpoint saved to {output_dir}")
    log(f"   Load with: load_statechart('{output_dir}')")


if __name__ == "__main__":
    main()
