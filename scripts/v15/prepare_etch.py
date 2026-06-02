"""
prepare_etch.py — Checkpoint preparation for v15 etch.

Loads step_0005000 from checkpoints/v15-hpe-dolma/step_0005000/ and the
base plates from checkpoints/v15-zeroed/strides/, then:

  1. Folds negative gammas: flip plate row + delta row + negate gamma.
  2. Zeros dead gamma rows: zero plate row + delta row (|gamma| < dead_threshold).

Saves a self-contained prepared checkpoint to
checkpoints/v15-hpe-dolma/step_0005000_prepared/ containing:

  strides/stride_XX.npz   — effective plates (base*delta, folded, zeroed) + corrected gammas
  weights.npz             — trained weights with corrected gammas (attn/norm unchanged)
  delta_plates.npz        — identity deltas (all ones) for the prepared plates
  meta.json               — copied verbatim
  td_meta.json            — copied verbatim

Usage:
  uv run python scripts/v15/prepare_etch.py
  uv run python scripts/v15/prepare_etch.py --ckpt-dir checkpoints/v15-hpe-dolma/step_0005000 \\
      --base-dir checkpoints/v15-zeroed/strides --out-dir checkpoints/v15-hpe-dolma/step_0005000_prepared
"""

import argparse
import json
import shutil
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Plate / gamma descriptors
# ---------------------------------------------------------------------------
PLATE_NAMES = ("gate", "up", "down")

# Which strides have gamma1 only vs gamma1+gamma2.
# Determined from weights.npz at runtime, not hard-coded — but we need the
# stride count first.  Populated in load_stride_gamma_counts().
_STRIDE_GAMMA_COUNTS: dict[int, int] = {}


def load_stride_gamma_counts(weights: dict[str, np.ndarray], n_strides: int) -> None:
    """Populate _STRIDE_GAMMA_COUNTS from the trained weights keys."""
    for s in range(n_strides):
        # All plate names have the same gamma count per stride; gate is canonical.
        if f"strides.{s}.ffn.gate_plate.gamma2" in weights:
            _STRIDE_GAMMA_COUNTS[s] = 2
        else:
            _STRIDE_GAMMA_COUNTS[s] = 1


# ---------------------------------------------------------------------------
# Data-loading helpers
# ---------------------------------------------------------------------------

def load_npz(path: Path) -> dict[str, np.ndarray]:
    """Load an npz file and return a plain mutable dict."""
    raw = np.load(path)
    return {k: raw[k].copy() for k in raw.files}


def load_weights(ckpt_dir: Path) -> dict[str, np.ndarray]:
    return load_npz(ckpt_dir / "weights.npz")


def load_deltas(ckpt_dir: Path) -> dict[str, np.ndarray]:
    return load_npz(ckpt_dir / "delta_plates.npz")


def load_base_stride(base_dir: Path, stride_idx: int) -> dict[str, np.ndarray]:
    path = base_dir / f"stride_{stride_idx:02d}.npz"
    return load_npz(path)


# ---------------------------------------------------------------------------
# Key-name helpers
# ---------------------------------------------------------------------------

def weights_gamma_key(stride: int, plate: str, g: int) -> str:
    return f"strides.{stride}.ffn.{plate}_plate.gamma{g}"


def delta_key(stride: int, plate: str, g: int) -> str:
    return f"strides.{stride}.ffn.{plate}_plate.delta{g}"


def stride_plate_key(plate: str, g: int) -> str:
    return f"{plate}_plate{g}"


def stride_gamma_key(plate: str, g: int) -> str:
    return f"{plate}_gamma{g}"


# ---------------------------------------------------------------------------
# Core preparation logic for a single (stride, plate, gamma) triple
# ---------------------------------------------------------------------------

def prepare_gamma(
    gamma: np.ndarray,          # (rows,) float32 — MODIFIED IN PLACE
    plate: np.ndarray,          # (rows, cols) float32 — MODIFIED IN PLACE (effective plate)
    delta: np.ndarray | None,   # (rows, cols) float32 | None — MODIFIED IN PLACE
    dead_threshold: float,
) -> tuple[int, int]:
    """
    Apply fold-negative and zero-dead transforms.

    Returns (n_folded, n_zeroed).

    The *effective* plate passed in is already base_plate * delta (float32).
    After this function the effective plate embeds both corrections, and
    delta (if provided) is left consistent (all ±1) so that the output
    stride files are self-contained with identity deltas.
    """
    # -- 1. Fold negative gammas ----------------------------------------
    neg_mask = gamma < 0.0
    n_folded = int(neg_mask.sum())
    if n_folded:
        # Flip the effective plate rows and the delta rows.
        plate[neg_mask, :] *= -1.0
        if delta is not None:
            delta[neg_mask, :] *= -1.0
        gamma[neg_mask] *= -1.0

    # -- 2. Zero dead gamma rows ----------------------------------------
    # Evaluate on the (now positive) gammas.
    dead_mask = np.abs(gamma) < dead_threshold
    n_zeroed = int(dead_mask.sum())
    if n_zeroed:
        plate[dead_mask, :] = 0.0
        if delta is not None:
            delta[dead_mask, :] = 0.0
        # gamma is left as-is (already near zero) so the checkpoint reader
        # can also see the dead rows clearly.  Optionally zero it too:
        gamma[dead_mask] = 0.0

    return n_folded, n_zeroed


# ---------------------------------------------------------------------------
# Statistics helpers
# ---------------------------------------------------------------------------

def nonzero_count(arr: np.ndarray) -> int:
    return int(np.count_nonzero(arr))


# ---------------------------------------------------------------------------
# Main preparation routine
# ---------------------------------------------------------------------------

def prepare(
    ckpt_dir: Path,
    base_dir: Path,
    out_dir: Path,
    dead_threshold: float,
    verbose: bool,
) -> None:
    print(f"\n{'='*70}")
    print("prepare_etch — v15 checkpoint preparation")
    print(f"{'='*70}")
    print(f"  checkpoint : {ckpt_dir}")
    print(f"  base plates: {base_dir}")
    print(f"  output     : {out_dir}")
    print(f"  dead_thresh: {dead_threshold}")
    print()

    # -- Load source data --------------------------------------------------
    print("Loading weights.npz …", flush=True)
    weights = load_weights(ckpt_dir)

    print("Loading delta_plates.npz …", flush=True)
    deltas = load_deltas(ckpt_dir)

    # Read n_strides from meta.json (fall back to counting stride files).
    meta_path = ckpt_dir / "meta.json"
    with open(meta_path) as f:
        meta = json.load(f)
    n_strides: int = meta["n_strides"]

    load_stride_gamma_counts(weights, n_strides)

    # -- Prepare output directory ------------------------------------------
    out_dir.mkdir(parents=True, exist_ok=True)
    strides_out = out_dir / "strides"
    strides_out.mkdir(exist_ok=True)

    # We'll accumulate the corrected weights and deltas into fresh dicts.
    new_weights: dict[str, np.ndarray] = {k: v.copy() for k, v in weights.items()}
    new_deltas: dict[str, np.ndarray] = {}

    # -- Per-stride processing ---------------------------------------------
    total_folded = 0
    total_zeroed = 0
    total_nz_before = 0
    total_nz_after = 0

    print(f"Processing {n_strides} strides …\n")

    for s in range(n_strides):
        n_gammas = _STRIDE_GAMMA_COUNTS[s]
        base_stride = load_base_stride(base_dir, s)

        stride_folded = 0
        stride_zeroed = 0
        stride_nz_before = 0
        stride_nz_after = 0

        # Collect what we'll save into the output stride file.
        out_stride: dict[str, np.ndarray] = {}

        for plate_name in PLATE_NAMES:
            for g in range(1, n_gammas + 1):
                # --- Retrieve components -----------------------------------
                gamma_wkey = weights_gamma_key(s, plate_name, g)
                gamma: np.ndarray = new_weights[gamma_wkey].copy()  # (rows,) float32

                base_plate: np.ndarray = base_stride[stride_plate_key(plate_name, g)].astype(np.float32)

                dkey = delta_key(s, plate_name, g)
                delta: np.ndarray | None = deltas.get(dkey)
                if delta is not None:
                    delta = delta.copy()

                # --- Effective plate (base * delta) -------------------------
                if delta is not None:
                    eff_plate = base_plate * delta
                else:
                    eff_plate = base_plate.copy()

                nz_before = nonzero_count(eff_plate)
                stride_nz_before += nz_before

                # --- Apply corrections -------------------------------------
                # We pass eff_plate and a fresh identity delta so that
                # prepare_gamma operates on the effective values.  After the
                # call, eff_plate is the corrected effective plate.
                identity_delta = np.ones_like(eff_plate) if delta is not None else None

                n_folded, n_zeroed = prepare_gamma(
                    gamma, eff_plate, identity_delta, dead_threshold
                )

                nz_after = nonzero_count(eff_plate)
                stride_nz_after += nz_after
                stride_folded += n_folded
                stride_zeroed += n_zeroed

                if verbose:
                    print(
                        f"  s{s:02d} {plate_name} γ{g}: "
                        f"folded={n_folded:4d}  zeroed={n_zeroed:4d}  "
                        f"nz {nz_before:,} → {nz_after:,}"
                    )

                # --- Store corrected values --------------------------------
                # weights.npz: overwrite gamma with corrected value
                new_weights[gamma_wkey] = gamma

                # delta_plates.npz: store identity delta (plate IS effective)
                if identity_delta is not None:
                    new_deltas[dkey] = identity_delta

                # stride file: store effective plate + corrected gamma
                out_stride[stride_plate_key(plate_name, g)] = eff_plate
                out_stride[stride_gamma_key(plate_name, g)] = gamma

                # Preserve zeros_mask from base (only exists once per plate,
                # not per gamma — recompute from effective plate for plate1).
                if g == 1:
                    zeros_mask_key = f"{plate_name}_zeros_mask"
                    # Recompute from eff_plate (may have gained zeros from zeroing).
                    out_stride[zeros_mask_key] = (eff_plate == 0.0).astype(np.uint8)

        # Save stride file
        stride_out_path = strides_out / f"stride_{s:02d}.npz"
        np.savez_compressed(stride_out_path, **out_stride)

        total_folded += stride_folded
        total_zeroed += stride_zeroed
        total_nz_before += stride_nz_before
        total_nz_after += stride_nz_after

        pct_nz_change = (
            100.0 * (stride_nz_after - stride_nz_before) / max(stride_nz_before, 1)
        )
        print(
            f"  stride {s:02d}  [gammas={n_gammas}]  "
            f"folded={stride_folded:5d}  zeroed={stride_zeroed:4d}  "
            f"nz {stride_nz_before:,} → {stride_nz_after:,}  "
            f"({pct_nz_change:+.2f}%)"
        )

    # -- Save weights.npz --------------------------------------------------
    print("\nSaving weights.npz …", flush=True)
    np.savez_compressed(out_dir / "weights.npz", **new_weights)

    # -- Save delta_plates.npz (identity deltas) ---------------------------
    print("Saving delta_plates.npz …", flush=True)
    np.savez_compressed(out_dir / "delta_plates.npz", **new_deltas)

    # -- Copy meta files ---------------------------------------------------
    for fname in ("meta.json", "td_meta.json"):
        src = ckpt_dir / fname
        if src.exists():
            shutil.copy2(src, out_dir / fname)
            print(f"Copied {fname}")
        else:
            print(f"  (skipped {fname} — not found)")

    # -- Summary -----------------------------------------------------------
    total_pct = 100.0 * (total_nz_after - total_nz_before) / max(total_nz_before, 1)
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"  Gammas folded (neg → pos) : {total_folded:,}")
    print(f"  Rows zeroed (dead gammas) : {total_zeroed:,}")
    print(f"  Non-zero positions before : {total_nz_before:,}")
    print(f"  Non-zero positions after  : {total_nz_after:,}")
    print(f"  Change                    : {total_nz_after - total_nz_before:+,}  ({total_pct:+.4f}%)")
    print(f"\nPrepared checkpoint written to:\n  {out_dir}\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a v15 checkpoint: fold negative gammas, zero dead rows.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--ckpt-dir",
        type=Path,
        default=Path("checkpoints/v15-hpe-dolma/step_0005000"),
        help="Path to the source checkpoint directory (contains weights.npz, delta_plates.npz, meta.json).",
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path("checkpoints/v15-zeroed/strides"),
        help="Path to the base stride directory (stride_XX.npz files).",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("checkpoints/v15-hpe-dolma/step_0005000_prepared"),
        help="Output directory for the prepared checkpoint.",
    )
    parser.add_argument(
        "--dead-threshold",
        type=float,
        default=0.001,
        help="Gammas with |gamma| < this value are treated as dead and their rows zeroed.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-(stride, plate, gamma) statistics.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    prepare(
        ckpt_dir=args.ckpt_dir,
        base_dir=args.base_dir,
        out_dir=args.out_dir,
        dead_threshold=args.dead_threshold,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
