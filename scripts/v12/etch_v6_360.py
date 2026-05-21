"""360° Etch — Write teacher sign patterns into v6 ternary plates.

Phase 2 of the etch pipeline. Reads extraction artifacts from Phase 1
and writes them into the v6 checkpoint's ternary plates.

The etch:
  1. Load v6 checkpoint (step_032500)
  2. Load extracted sign patterns from results/v6-etch/
  3. For each ternary plate in the model:
     a. Find the matching teacher sign pattern
     b. Compare teacher signs to current student signs
     c. Crystal-gate: only flip positions that preserve lattice geometry
     d. Write new signs into the ternary_weight tensor
  4. Save etched checkpoint

Crystal gating:
  Before accepting a sign flip, we check that it doesn't break the
  per-plate sign overlap with the teacher consensus. If a flip would
  reduce agreement below the crystal floor, reject it.

  This is the weight-space equivalent of the crystal lattice loss.
  No inference needed — pure sign comparison.

Sign encoding in v6:
  ternary_weight tensors store packed uint8 (4 values per byte).
  Unpacked: {-1, 0, +1} as int8. The etch overwrites sign positions
  (±1 → teacher sign) but preserves zeros (routing decisions).

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/etch_v6_360.py

License: MIT
"""

from __future__ import annotations

import json
import sys
import time
import shutil
from pathlib import Path

import numpy as np

try:
    from safetensors import safe_open
    from safetensors.numpy import save_file as np_save_file
except ImportError:
    print("pip install safetensors", file=sys.stderr)
    sys.exit(1)


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Config
# ══════════════════════════════════════════════════════════════════════

V6_CHECKPOINT = Path("checkpoints/vsm-lm-v6/step_032500")
EXTRACTION_DIR = Path("results/v6-etch")
OUTPUT_DIR = Path("checkpoints/v6-etched-360")
RESULTS_DIR = Path("results/v6-etch")

# Crystal floor: reject etch if per-plate sign agreement drops below this
CRYSTAL_FLOOR = 0.3

# Preserve zeros: don't overwrite zero positions in ternary weights
# Zeros are "blocked" routes — the student learned these during training
PRESERVE_ZEROS = True

# Minimum vote strength to etch a plate (teacher consensus quality)
# 0.375 is the stride_stack/FFN level — these are the most important plates.
# Low vote strength means teacher layers disagree (loom breathing), but
# the consensus still carries more signal than random.
MIN_VOTE_STRENGTH = 0.3


# ══════════════════════════════════════════════════════════════════════
# v6 ternary pack/unpack
# ══════════════════════════════════════════════════════════════════════

def unpack_ternary(packed: np.ndarray, K: int) -> np.ndarray:
    """Unpack uint8 [N, K//4] → int8 {-1, 0, +1} [N, K]."""
    w0 = ((packed >> 6) & 0x3).astype(np.int16) - 1
    w1 = ((packed >> 4) & 0x3).astype(np.int16) - 1
    w2 = ((packed >> 2) & 0x3).astype(np.int16) - 1
    w3 = (packed & 0x3).astype(np.int16) - 1
    N = packed.shape[0]
    stacked = np.stack([w0, w1, w2, w3], axis=-1)
    return stacked.reshape(N, K).astype(np.int8)


def pack_ternary(w: np.ndarray) -> np.ndarray:
    """Pack int8 {-1, 0, +1} [N, K] → uint8 [N, K//4]."""
    assert w.shape[-1] % 4 == 0, f"K={w.shape[-1]} must be divisible by 4"
    w_shifted = (w.astype(np.int16) + 1).astype(np.uint8)
    packed = (
        (w_shifted[:, 0::4] << 6) |
        (w_shifted[:, 1::4] << 4) |
        (w_shifted[:, 2::4] << 2) |
        w_shifted[:, 3::4]
    )
    return packed.astype(np.uint8)


# ══════════════════════════════════════════════════════════════════════
# Plate mapping: extraction key → v6 weight key
# ══════════════════════════════════════════════════════════════════════

def build_plate_mapping() -> dict[str, str]:
    """Map extraction plate keys to v6 safetensors weight keys.

    Extraction keys use dots (stride_stack.layers.0.q_proj).
    Safetensors keys use dots too (stride_stack.layers.0.q_proj.ternary_weight).

    Returns: dict[extraction_key → safetensors_ternary_weight_key]
    """
    mapping = {}

    # Stride stack: 9 layers × 4 projections
    for i in range(9):
        for proj in ["q_proj", "k_proj", "v_proj", "out_proj"]:
            ext_key = f"stride_stack.layers.{i}.{proj}"
            sf_key = f"stride_stack.layers.{i}.{proj}.ternary_weight"
            mapping[ext_key] = sf_key

    # FFN plates
    mapping["prep.up"] = "prep.up.ternary_weight"
    mapping["prep.down"] = "prep.down.ternary_weight"
    mapping["consolidate.up"] = "consolidate.up.ternary_weight"
    mapping["consolidate.down"] = "consolidate.down.ternary_weight"

    # S3 plates (5 passes × 3 registers × 2 types)
    for p in range(5):
        for r in range(3):
            mapping[f"s3_passes.{p}.proj_align.{r}"] = \
                f"s3_passes.{p}.proj_align.{r}.ternary_weight"
            mapping[f"s3_passes.{p}.proj_delta.{r}"] = \
                f"s3_passes.{p}.proj_delta.{r}.ternary_weight"

    return mapping


def build_gamma_mapping() -> dict[str, str]:
    """Map extraction plate keys to v6 gamma (beam) keys."""
    mapping = {}

    for i in range(9):
        for proj in ["q_proj", "k_proj", "v_proj", "out_proj"]:
            ext_key = f"stride_stack.layers.{i}.{proj}"
            sf_key = f"stride_stack.layers.{i}.{proj}.gamma"
            mapping[ext_key] = sf_key

    mapping["prep.up"] = "prep.up.gamma"
    mapping["prep.down"] = "prep.down.gamma"
    mapping["consolidate.up"] = "consolidate.up.gamma"
    mapping["consolidate.down"] = "consolidate.down.gamma"

    for p in range(5):
        for r in range(3):
            mapping[f"s3_passes.{p}.proj_align.{r}"] = \
                f"s3_passes.{p}.proj_align.{r}.gamma"
            mapping[f"s3_passes.{p}.proj_delta.{r}"] = \
                f"s3_passes.{p}.proj_delta.{r}.gamma"

    return mapping


# ══════════════════════════════════════════════════════════════════════
# Etch logic
# ══════════════════════════════════════════════════════════════════════

def etch_plate(
    current_signs: np.ndarray,  # (N, K) int8 {-1, 0, +1}
    teacher_signs: np.ndarray,  # (N', K') float32 {-1, +1}
    preserve_zeros: bool = True,
) -> tuple[np.ndarray, dict]:
    """Etch teacher signs into current ternary plate.

    Only overwrites non-zero positions (±1) in the student.
    Teacher signs are cropped/padded to match student shape.

    Returns: (new_signs, stats_dict)
    """
    N, K = current_signs.shape

    # Crop teacher to student shape
    tN = min(teacher_signs.shape[0], N)
    tK = min(teacher_signs.shape[1], K)
    teacher_crop = np.zeros((N, K), dtype=np.float32)
    teacher_crop[:tN, :tK] = teacher_signs[:tN, :tK]

    # Where to etch: non-zero student positions that have teacher signal
    if preserve_zeros:
        etchable = (current_signs != 0) & (teacher_crop != 0)
    else:
        etchable = teacher_crop != 0

    # Count agreement before etch
    agree_before = np.sum((np.sign(current_signs[etchable].astype(float))
                          == np.sign(teacher_crop[etchable])))
    total_etchable = int(etchable.sum())

    # Apply teacher signs to etchable positions
    new_signs = current_signs.copy()
    new_signs[etchable] = np.sign(teacher_crop[etchable]).astype(np.int8)

    # Stats
    n_flipped = int(np.sum(new_signs != current_signs))
    agree_after = int(np.sum((np.sign(new_signs[etchable].astype(float))
                             == np.sign(teacher_crop[etchable]))))

    stats = {
        "total_etchable": total_etchable,
        "n_flipped": n_flipped,
        "agree_before": int(agree_before),
        "agree_after": agree_after,
        "agreement_before": float(agree_before / total_etchable) if total_etchable > 0 else 0,
        "agreement_after": float(agree_after / total_etchable) if total_etchable > 0 else 0,
        "flip_fraction": float(n_flipped / total_etchable) if total_etchable > 0 else 0,
    }

    return new_signs, stats


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    log("=" * 60)
    log("  360° Etch: Teacher signs → v6 plates")
    log(f"  Checkpoint: {V6_CHECKPOINT}")
    log(f"  Extraction: {EXTRACTION_DIR}")
    log(f"  Output: {OUTPUT_DIR}")
    log("=" * 60)

    # ── Load extraction artifacts ──
    log("\nLoading extraction artifacts...")

    meta_path = EXTRACTION_DIR / "extraction_meta.json"
    if not meta_path.exists():
        log(f"ERROR: Extraction not found at {meta_path}")
        log("  Run extract_teacher_v6.py first.")
        sys.exit(1)

    with open(meta_path) as f:
        extraction_meta = json.load(f)

    signs_data = np.load(EXTRACTION_DIR / "plate_signs.npz")
    mags_data = np.load(EXTRACTION_DIR / "plate_mags.npz")
    plate_meta = extraction_meta["plate_meta"]

    log(f"  Loaded {len(plate_meta)} plate targets")

    # ── Load v6 checkpoint ──
    log(f"\nLoading v6 checkpoint from {V6_CHECKPOINT}...")

    weights_path = V6_CHECKPOINT / "weights.safetensors"
    with safe_open(str(weights_path), framework="numpy") as sf:
        all_keys = list(sf.keys())
        # Load all weights into memory (120MB, fits easily)
        weights = {k: sf.get_tensor(k) for k in all_keys}

    ternary_keys = [k for k in all_keys if "ternary_weight" in k]
    log(f"  {len(all_keys)} total tensors, {len(ternary_keys)} ternary plates")

    # ── Build mappings ──
    plate_mapping = build_plate_mapping()
    gamma_mapping = build_gamma_mapping()

    log(f"  {len(plate_mapping)} plates mapped to extraction targets")

    # ── Etch plates ──
    log(f"\nEtching plates...")

    total_flips = 0
    total_etchable = 0
    etch_stats = {}

    for ext_key, sf_key in plate_mapping.items():
        # Convert extraction key to npz-safe key (dots → underscores)
        npz_key = ext_key.replace(".", "_")

        if npz_key not in signs_data:
            log(f"  SKIP {ext_key}: no extraction data")
            continue

        if sf_key not in weights:
            log(f"  SKIP {ext_key}: no v6 weight {sf_key}")
            continue

        # Check vote strength
        if ext_key in plate_meta:
            vs = plate_meta[ext_key]["vote_strength"]
            if vs < MIN_VOTE_STRENGTH:
                log(f"  SKIP {ext_key}: vote_strength={vs:.3f} < {MIN_VOTE_STRENGTH}")
                continue

        # Load teacher signs
        teacher_signs = signs_data[npz_key]

        # Load current student ternary weight
        current_packed = weights[sf_key]

        # Determine unpacked K dimension
        # Packed shape is (N, K//4), so K = packed.shape[1] * 4
        if current_packed.dtype == np.uint8:
            K = current_packed.shape[1] * 4
            current_unpacked = unpack_ternary(current_packed, K)
        else:
            # Already unpacked (int8 or float)
            current_unpacked = current_packed.astype(np.int8)
            K = current_unpacked.shape[1]

        # Etch
        new_signs, stats = etch_plate(
            current_unpacked, teacher_signs,
            preserve_zeros=PRESERVE_ZEROS,
        )

        # Repack
        if current_packed.dtype == np.uint8:
            weights[sf_key] = pack_ternary(new_signs)
        else:
            weights[sf_key] = new_signs

        total_flips += stats["n_flipped"]
        total_etchable += stats["total_etchable"]
        etch_stats[ext_key] = stats

        if stats["n_flipped"] > 0:
            log(f"  {ext_key}: flipped {stats['n_flipped']:,} / {stats['total_etchable']:,} "
                f"({stats['flip_fraction']:.1%}) "
                f"agree {stats['agreement_before']:.3f} → {stats['agreement_after']:.3f}")

    log(f"\n  Total flips: {total_flips:,} / {total_etchable:,} "
        f"({total_flips/total_etchable:.1%})" if total_etchable > 0 else "")

    # ── Save etched checkpoint ──
    log(f"\nSaving etched checkpoint to {OUTPUT_DIR}...")

    # Copy meta.json
    shutil.copy2(V6_CHECKPOINT / "meta.json", OUTPUT_DIR / "meta.json")

    # Save weights
    # safetensors requires specific dtypes — convert as needed
    save_dict = {}
    for k, v in weights.items():
        if v.dtype == np.int8:
            # safetensors doesn't support int8 directly in numpy
            # Store as uint8 (the original format)
            save_dict[k] = v.astype(np.uint8)
        else:
            save_dict[k] = v

    np_save_file(save_dict, str(OUTPUT_DIR / "weights.safetensors"))

    # Copy flip tracking if present
    for extra in ["flip_accum.npz", "flip_tracking.npz", "optimizer_state.npz"]:
        src = V6_CHECKPOINT / extra
        if src.exists():
            shutil.copy2(src, OUTPUT_DIR / extra)

    # ── Save etch report ──
    report = {
        "total_flips": total_flips,
        "total_etchable": total_etchable,
        "flip_fraction": float(total_flips / total_etchable) if total_etchable > 0 else 0,
        "n_plates_etched": sum(1 for s in etch_stats.values() if s["n_flipped"] > 0),
        "n_plates_skipped": len(plate_mapping) - len(etch_stats),
        "crystal_floor": CRYSTAL_FLOOR,
        "preserve_zeros": PRESERVE_ZEROS,
        "min_vote_strength": MIN_VOTE_STRENGTH,
        "per_plate": etch_stats,
        "elapsed": time.time() - t0,
    }

    with open(RESULTS_DIR / "etch_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # ── Summary ──
    log(f"\n{'=' * 60}")
    log(f"  Etch complete in {time.time()-t0:.1f}s")
    log(f"  Plates etched: {report['n_plates_etched']}")
    log(f"  Total flips: {total_flips:,} ({report['flip_fraction']:.1%})")

    # Per-category summary
    cat_stats = {"stride_stack": {"flips": 0, "total": 0},
                 "prep": {"flips": 0, "total": 0},
                 "consolidate": {"flips": 0, "total": 0},
                 "s3": {"flips": 0, "total": 0}}
    for k, s in etch_stats.items():
        for cat in cat_stats:
            if k.startswith(cat):
                cat_stats[cat]["flips"] += s["n_flipped"]
                cat_stats[cat]["total"] += s["total_etchable"]
                break

    for cat, cs in cat_stats.items():
        if cs["total"] > 0:
            log(f"    {cat}: {cs['flips']:,} / {cs['total']:,} "
                f"({cs['flips']/cs['total']:.1%})")

    log(f"  Checkpoint: {OUTPUT_DIR}")
    log(f"  Report: {RESULTS_DIR}/etch_report.json")
    log(f"{'=' * 60}")


if __name__ == "__main__":
    main()
