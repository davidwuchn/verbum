#!/usr/bin/env python3
"""
v13 Etch Verification — teacher reference beam + dimensional tomography.

The crystal is self-similar across dimensional projections. A 5D SVD
subspace contains the 4D, which contains the 3D. Signs that are stable
across 5D → 4D → 3D projections are high-confidence crystal positions.
Signs that flip between dimensions are etch artifacts — the dimensional
consensus corrects them.

The teacher at two reference layers (L0 = input encoding, L_mid ≈ apex)
provides two independent planes to triangulate the crystal. Agreement
between both reference layers AND across dimensional projections gives
the highest confidence etch.

Protocol per plate:
  1. Load teacher weight W at reference layer(s)
  2. SVD-project W to 5D, 4D, 3D subspaces (with 360° rotation voting)
  3. Check dimensional consistency:
     - 5D sign pattern → restrict to 4D → compare with 4D sign pattern
     - 4D sign pattern → restrict to 3D → compare with 3D sign pattern
  4. Positions stable across all projections = crystal (high confidence)
  5. Compare with student etch plates → identify etch errors
  6. Optionally error-correct: replace low-confidence student positions
     with dimensional consensus

Usage:
    cd ~/src/verbum
    uv run python scripts/v13/verify_etch.py \\
        --teacher-path <qwen3-14b-safetensors-dir> \\
        --etched-dir checkpoints/v13-etched \\
        [--correct --output checkpoints/v13-corrected]

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

# Reuse extraction utilities from extract_teacher
sys.path.insert(0, str(Path(__file__).parent))
from extract_teacher import (
    load_tensor,
    detect_teacher_config,
    truncated_svd,
    _random_orthogonal,
    log,
)


# ══════════════════════════════════════════════════════════════════════
# § 1  Dimensional sign extraction (5D → 4D → 3D hierarchy)
# ══════════════════════════════════════════════════════════════════════

def extract_signs_at_rank(
    W: np.ndarray,
    d_out: int,
    d_in: int,
    rank: int,
    n_rotations: int = 8,
    seed: int = 42,
) -> np.ndarray:
    """Extract sign pattern at a specific SVD rank (dimensionality).

    Like extract_sign_pattern but explicitly controls the projection
    rank. Lower rank = fewer principal components = coarser crystal view.

    The crystal at rank-k is the k-dimensional "shadow" of the full
    weight structure. The rank-5 shadow contains the rank-4 which
    contains the rank-3 — because the first 3 SVD components are the
    same whether you compute 3, 4, or 5 components.

    W:       (out_t, in_t) teacher weight
    d_out:   student output dimension
    d_in:    student input dimension
    rank:    SVD rank for this projection (3, 4, or 5)

    Returns: (d_out, d_in) int8 {-1, 0, +1}
             0 = outside the rank-k subspace (not projected)
    """
    n_out, n_in = W.shape
    rng = np.random.RandomState(seed)

    # Truncated SVD at the specified rank
    k = min(rank, min(n_out, n_in) - 1, max(d_out, d_in))
    U, S, Vt = truncated_svd(W, k)

    k_out = min(d_out, k)
    k_in = min(d_in, k)

    votes = np.zeros((d_out, d_in), dtype=np.float32)

    for r in range(n_rotations):
        if r == 0:
            P_out = U[:, :k_out].T
            P_in = Vt[:k_in, :]
        else:
            R_out = _random_orthogonal(k_out, rng)
            R_in = _random_orthogonal(k_in, rng)
            P_out = R_out @ U[:, :k_out].T
            P_in = R_in @ Vt[:k_in, :]

        Wp = P_out @ W @ P_in.T  # (k_out, k_in)

        angle_signs = np.zeros((d_out, d_in), dtype=np.float32)
        angle_signs[:k_out, :k_in] = np.sign(Wp)
        votes += angle_signs

    result = np.sign(votes).astype(np.int8)
    # Don't fill zeros — they indicate positions outside the subspace
    # or tied votes (genuinely ambiguous)
    return result


def extract_dimensional_hierarchy(
    W: np.ndarray,
    d_out: int,
    d_in: int,
    ranks: tuple[int, ...] = (5, 4, 3),
    n_rotations: int = 8,
) -> dict[int, np.ndarray]:
    """Extract sign patterns at multiple SVD ranks.

    Returns dict mapping rank → (d_out, d_in) sign pattern.
    Higher rank = more dimensions = finer crystal view.
    """
    return {
        rank: extract_signs_at_rank(W, d_out, d_in, rank, n_rotations)
        for rank in ranks
    }


# ══════════════════════════════════════════════════════════════════════
# § 2  Dimensional consistency check
# ══════════════════════════════════════════════════════════════════════

def check_dimensional_consistency(
    signs_by_rank: dict[int, np.ndarray],
) -> dict:
    """Check whether sign patterns are consistent across dimensions.

    The crystal at rank-k should be a sub-pattern of rank-(k+1).
    Where they agree = stable crystal. Where they disagree = artifact.

    Returns:
        agreement: dict[str, float]  — pairwise agreement fractions
        confidence: (d_out, d_in) float32  — per-position confidence [0, 1]
            1.0 = all ranks agree, 0.0 = all ranks disagree
        consensus: (d_out, d_in) int8  — sign(sum of votes across ranks)
    """
    ranks = sorted(signs_by_rank.keys(), reverse=True)  # highest first
    if not ranks:
        return {"agreement": {}, "confidence": None, "consensus": None}

    shape = signs_by_rank[ranks[0]].shape
    d_out, d_in = shape

    # Weighted vote: higher rank gets more weight (more information)
    weighted_votes = np.zeros(shape, dtype=np.float32)
    rank_weights = {r: float(r) for r in ranks}  # rank itself as weight

    for rank in ranks:
        s = signs_by_rank[rank].astype(np.float32)
        weighted_votes += s * rank_weights[rank]

    total_weight = sum(rank_weights.values())
    consensus = np.sign(weighted_votes).astype(np.int8)

    # Confidence: what fraction of total weight agrees with consensus
    agreement_weight = np.zeros(shape, dtype=np.float32)
    for rank in ranks:
        s = signs_by_rank[rank].astype(np.float32)
        # Where sign matches consensus, add that rank's weight
        matches = (np.sign(s) == np.sign(consensus)) & (s != 0) & (consensus != 0)
        agreement_weight += matches.astype(np.float32) * rank_weights[rank]

    # Positions where at least one rank has a non-zero sign
    has_signal = np.zeros(shape, dtype=np.float32)
    for rank in ranks:
        has_signal += (signs_by_rank[rank] != 0).astype(np.float32) * rank_weights[rank]

    safe_signal = np.maximum(has_signal, 1e-12)
    confidence = np.where(has_signal > 0, agreement_weight / safe_signal, 0.0)

    # Pairwise agreement between adjacent ranks
    pair_agreement = {}
    for i in range(len(ranks) - 1):
        r_high, r_low = ranks[i], ranks[i + 1]
        s_high = signs_by_rank[r_high]
        s_low = signs_by_rank[r_low]
        # Only compare positions where both have signal
        mask = (s_high != 0) & (s_low != 0)
        if mask.any():
            agree = np.mean((s_high[mask] == s_low[mask]).astype(np.float32))
            pair_agreement[f"{r_high}D→{r_low}D"] = float(agree)

    return {
        "agreement": pair_agreement,
        "confidence": confidence,
        "consensus": consensus,
    }


# ══════════════════════════════════════════════════════════════════════
# § 3  Multi-layer triangulation
# ══════════════════════════════════════════════════════════════════════

def triangulate_layers(
    layer_results: dict[int, dict],
) -> dict:
    """Combine dimensional consistency from multiple reference layers.

    Each reference layer gives an independent view of the crystal.
    Positions where BOTH layers agree across ALL dimensions are the
    highest-confidence crystal positions.

    layer_results: dict[teacher_layer → check_dimensional_consistency output]
    """
    layers = sorted(layer_results.keys())
    if not layers:
        return {"confidence": None, "consensus": None}

    shape = None
    for lr in layer_results.values():
        if lr["confidence"] is not None:
            shape = lr["confidence"].shape
            break
    if shape is None:
        return {"confidence": None, "consensus": None}

    # Weighted consensus across layers
    # L0 gets higher weight (input encoding is most constrained)
    layer_weights = {}
    for i, layer in enumerate(layers):
        # First layer (L0) gets weight 2, others get 1
        layer_weights[layer] = 2.0 if i == 0 else 1.0

    total_consensus = np.zeros(shape, dtype=np.float32)
    total_confidence = np.zeros(shape, dtype=np.float32)
    total_weight = sum(layer_weights.values())

    for layer in layers:
        w = layer_weights[layer]
        lr = layer_results[layer]
        if lr["consensus"] is not None:
            total_consensus += lr["consensus"].astype(np.float32) * w
        if lr["confidence"] is not None:
            total_confidence += lr["confidence"] * w

    consensus = np.sign(total_consensus).astype(np.int8)
    confidence = total_confidence / total_weight

    # Cross-layer agreement
    cross_agreement = {}
    for i in range(len(layers)):
        for j in range(i + 1, len(layers)):
            c_i = layer_results[layers[i]]["consensus"]
            c_j = layer_results[layers[j]]["consensus"]
            if c_i is not None and c_j is not None:
                mask = (c_i != 0) & (c_j != 0)
                if mask.any():
                    agree = np.mean((c_i[mask] == c_j[mask]).astype(np.float32))
                    cross_agreement[f"L{layers[i]}↔L{layers[j]}"] = float(agree)

    return {
        "consensus": consensus,
        "confidence": confidence,
        "cross_layer_agreement": cross_agreement,
    }


# ══════════════════════════════════════════════════════════════════════
# § 4  Student plate comparison + error correction
# ══════════════════════════════════════════════════════════════════════

def load_student_plates(etched_dir: Path) -> dict[str, np.ndarray]:
    """Load etched student sign plates from NPZ."""
    npz_path = etched_dir / "teacher_plates.npz"
    if not npz_path.exists():
        raise FileNotFoundError(f"No teacher_plates.npz in {etched_dir}")

    data = np.load(str(npz_path))
    plates = {}
    for key in data.files:
        if key.endswith(".signs"):
            plate_name = key[:-6]  # strip ".signs"
            plates[plate_name] = data[key]
    return plates


def compare_with_student(
    student_signs: np.ndarray,
    verification: dict,
    confidence_threshold: float = 0.7,
) -> dict:
    """Compare student etch against dimensional consensus.

    Returns:
        agreement:    fraction of positions where student matches consensus
        n_errors:     positions where student disagrees with high-confidence consensus
        error_mask:   (d_out, d_in) bool — True where correction needed
        corrected:    (d_out, d_in) int8 — student signs with errors corrected
    """
    consensus = verification["consensus"]
    confidence = verification["confidence"]

    if consensus is None or confidence is None:
        return {
            "agreement": 0.0,
            "n_errors": 0,
            "n_high_conf": 0,
            "error_mask": np.zeros_like(student_signs, dtype=bool),
            "corrected": student_signs.copy(),
        }

    # Positions where both student and consensus have signal
    mask = (student_signs != 0) & (consensus != 0)
    if not mask.any():
        return {
            "agreement": 0.0,
            "n_errors": 0,
            "n_high_conf": 0,
            "error_mask": np.zeros_like(student_signs, dtype=bool),
            "corrected": student_signs.copy(),
        }

    # Agreement
    agree = np.mean((student_signs[mask] == consensus[mask]).astype(np.float32))

    # High-confidence positions where student disagrees
    high_conf = confidence >= confidence_threshold
    disagree = student_signs != consensus
    error_mask = mask & high_conf & disagree

    n_errors = int(error_mask.sum())
    n_high_conf = int((mask & high_conf).sum())

    # Corrected plate: replace errors with consensus
    corrected = student_signs.copy()
    corrected[error_mask] = consensus[error_mask]

    return {
        "agreement": float(agree),
        "n_errors": n_errors,
        "n_high_conf": n_high_conf,
        "error_mask": error_mask,
        "corrected": corrected,
    }


# ══════════════════════════════════════════════════════════════════════
# § 5  Per-plate verification pipeline
# ══════════════════════════════════════════════════════════════════════

# Map student plate paths → teacher weight names
PLATE_TO_TEACHER = {
    "stride_stack.stack.layers.{si}.q_proj": "{prefix}.q_proj.weight",
    "stride_stack.stack.layers.{si}.k_proj": "{prefix}.k_proj.weight",
    "stride_stack.stack.layers.{si}.v_proj": "{prefix}.v_proj.weight",
    "stride_stack.stack.layers.{si}.out_proj": "{prefix}.o_proj.weight",
    "ffn_key_plate": "model.layers.{ffn_layer}.mlp.up_proj.weight",
    "ffn_value_plate": "model.layers.{ffn_layer}.mlp.down_proj.weight",
}


def verify_single_plate(
    plate_name: str,
    student_signs: np.ndarray,
    teacher_path: Path,
    reference_layers: list[int],
    n_rotations: int = 8,
    ranks: tuple[int, ...] = (5, 4, 3),
    confidence_threshold: float = 0.7,
) -> dict:
    """Verify a single student plate against teacher reference beams.

    For each reference layer:
      1. Load teacher weight at that layer
      2. Extract 5D, 4D, 3D sign patterns
      3. Check dimensional consistency
    Then triangulate across layers and compare with student.
    """
    d_out, d_in = student_signs.shape

    # Determine which teacher weight to load
    teacher_tensor_name = _resolve_teacher_tensor(plate_name, reference_layers[0])
    if teacher_tensor_name is None:
        return {"error": f"Cannot map {plate_name} to teacher tensor"}

    layer_results = {}

    for ref_layer in reference_layers:
        tensor_name = _resolve_teacher_tensor(plate_name, ref_layer)
        if tensor_name is None:
            continue

        try:
            W = load_tensor(teacher_path, tensor_name)
        except FileNotFoundError:
            log(f"    SKIP L{ref_layer}: {tensor_name} not found")
            continue

        # Extract at each rank
        signs_by_rank = extract_dimensional_hierarchy(
            W, d_out, d_in, ranks=ranks, n_rotations=n_rotations,
        )

        # Check consistency within this layer
        consistency = check_dimensional_consistency(signs_by_rank)
        layer_results[ref_layer] = consistency

    if not layer_results:
        return {"error": "No reference layers could be loaded"}

    # Triangulate across layers
    triangulated = triangulate_layers(layer_results)

    # Compare with student etch
    comparison = compare_with_student(
        student_signs, triangulated,
        confidence_threshold=confidence_threshold,
    )

    # Build per-layer dimensional agreement for the report
    per_layer_dim = {}
    for layer, consistency in layer_results.items():
        per_layer_dim[f"L{layer}"] = consistency["agreement"]

    return {
        "plate": plate_name,
        "shape": list(student_signs.shape),
        "ranks_checked": list(ranks),
        "reference_layers": list(layer_results.keys()),
        "per_layer_dimensional_agreement": per_layer_dim,
        "cross_layer": triangulated.get("cross_layer_agreement", {}),
        "student_agreement": comparison["agreement"],
        "n_errors": comparison["n_errors"],
        "n_high_confidence": comparison["n_high_conf"],
        "error_rate": (comparison["n_errors"] / max(comparison["n_high_conf"], 1)),
        "corrected": comparison["corrected"],
        "error_mask": comparison["error_mask"],
    }


def _resolve_teacher_tensor(plate_name: str, teacher_layer: int) -> str | None:
    """Map student plate name → teacher tensor name at a given layer."""
    prefix = f"model.layers.{teacher_layer}.self_attn"

    if plate_name.startswith("stride_stack.stack.layers."):
        # Extract stride index
        parts = plate_name.split(".")
        proj_name = parts[-1]  # q_proj, k_proj, v_proj, out_proj
        teacher_proj = proj_name if proj_name != "out_proj" else "o_proj"
        return f"{prefix}.{teacher_proj}.weight"

    elif plate_name == "ffn_key_plate":
        return f"model.layers.{teacher_layer}.mlp.up_proj.weight"

    elif plate_name == "ffn_value_plate":
        return f"model.layers.{teacher_layer}.mlp.down_proj.weight"

    return None


# ══════════════════════════════════════════════════════════════════════
# § 6  Main verification pipeline
# ══════════════════════════════════════════════════════════════════════

def verify_etch(
    teacher_path: Path,
    etched_dir: Path,
    reference_layers: list[int] | None = None,
    n_rotations: int = 8,
    ranks: tuple[int, ...] = (5, 4, 3),
    confidence_threshold: float = 0.7,
    correct: bool = False,
    output_dir: Path | None = None,
) -> dict:
    """Full verification pipeline: verify all student plates against teacher.

    Args:
        teacher_path:   Path to teacher model (safetensors directory)
        etched_dir:     Path to extract_teacher.py output (with teacher_plates.npz)
        reference_layers: Teacher layers to use as reference beams.
                          Default: [0, n_layers//2] (L0 + apex)
        n_rotations:    360° rotation count per rank
        ranks:          Dimensional projections to check (default: 5D, 4D, 3D)
        confidence_threshold: minimum confidence to flag an error (0-1)
        correct:        If True, produce corrected plates
        output_dir:     Where to save corrected plates (required if correct=True)

    Returns dict with per-plate verification results and global summary.
    """
    t0 = time.time()

    # Teacher config
    teacher_cfg = detect_teacher_config(teacher_path)
    n_layers_t = teacher_cfg["n_layers"]

    if reference_layers is None:
        reference_layers = [0, n_layers_t // 2]
    log(f"  Teacher: {teacher_cfg['model_type']}, "
        f"d={teacher_cfg['d_model']}, layers={n_layers_t}")
    log(f"  Reference layers: {reference_layers}")
    log(f"  Ranks: {list(ranks)} (dimensional tomography)")
    log(f"  Confidence threshold: {confidence_threshold}")

    # Load student plates
    student_plates = load_student_plates(etched_dir)
    log(f"  Student plates: {len(student_plates)}")

    # Map stride indices to teacher layers for proper stride→layer matching
    n_strides = 11  # V13 default
    stride_to_teacher = {
        si: _stride_to_teacher_layer(si, n_strides, n_layers_t)
        for si in range(n_strides)
    }

    # Verify each plate
    results = {}
    total_errors = 0
    total_high_conf = 0
    corrected_plates = {}

    for plate_name, student_signs in sorted(student_plates.items()):
        # Determine reference layers for this plate
        # For stride layers: use the stride's own depth layer + L0
        # For FFN plates: use mid layer + L0
        plate_ref_layers = _get_plate_reference_layers(
            plate_name, reference_layers, stride_to_teacher, n_layers_t,
        )

        log(f"\n  Verifying: {plate_name} {student_signs.shape}"
            f"  refs={plate_ref_layers}")

        result = verify_single_plate(
            plate_name,
            student_signs,
            teacher_path,
            plate_ref_layers,
            n_rotations=n_rotations,
            ranks=ranks,
            confidence_threshold=confidence_threshold,
        )

        if "error" in result:
            log(f"    ⚠  {result['error']}")
            results[plate_name] = result
            continue

        # Report
        agree_pct = result["student_agreement"] * 100
        n_err = result["n_errors"]
        n_hc = result["n_high_confidence"]
        err_rate = result["error_rate"] * 100

        icon = "✅" if err_rate < 1.0 else ("⚠ " if err_rate < 5.0 else "❌")
        log(f"    {icon} agree={agree_pct:.1f}%  errors={n_err:,}/{n_hc:,}"
            f"  err_rate={err_rate:.2f}%")

        # Dimensional agreement per layer
        for layer_key, dim_agree in result["per_layer_dimensional_agreement"].items():
            parts = "  ".join(f"{k}={v:.3f}" for k, v in dim_agree.items())
            log(f"       {layer_key}: {parts}")

        # Cross-layer agreement
        if result["cross_layer"]:
            parts = "  ".join(f"{k}={v:.3f}" for k, v in result["cross_layer"].items())
            log(f"       cross: {parts}")

        total_errors += n_err
        total_high_conf += n_hc

        # Strip non-serializable arrays from results for JSON
        results[plate_name] = {
            k: v for k, v in result.items()
            if k not in ("corrected", "error_mask")
        }

        if correct:
            corrected_plates[plate_name] = result["corrected"]

    dt = time.time() - t0

    # Global summary
    global_err_rate = total_errors / max(total_high_conf, 1)
    log(f"\n{'='*72}")
    log(f"  Verification complete: {dt:.1f}s")
    log(f"  Total high-confidence positions: {total_high_conf:,}")
    log(f"  Total errors found: {total_errors:,}")
    log(f"  Global error rate: {global_err_rate:.4%}")
    log(f"{'='*72}")

    # Save corrected plates if requested
    if correct and corrected_plates and output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

        # Load original NPZ to preserve magnitudes
        orig_data = dict(np.load(str(etched_dir / "teacher_plates.npz")))

        # Replace signs with corrected versions
        for plate_name, corrected_signs in corrected_plates.items():
            orig_data[f"{plate_name}.signs"] = corrected_signs

        out_path = output_dir / "teacher_plates.npz"
        np.savez_compressed(str(out_path), **orig_data)
        log(f"  Corrected plates saved: {out_path}")

        # Save verification report
        report = {
            "teacher_path": str(teacher_path),
            "etched_dir": str(etched_dir),
            "reference_layers": reference_layers,
            "ranks": list(ranks),
            "confidence_threshold": confidence_threshold,
            "n_rotations": n_rotations,
            "total_high_confidence": total_high_conf,
            "total_errors": total_errors,
            "global_error_rate": global_err_rate,
            "plates": results,
            "elapsed_s": dt,
        }
        report_path = output_dir / "verification_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        log(f"  Report saved: {report_path}")

    return {
        "total_high_confidence": total_high_conf,
        "total_errors": total_errors,
        "global_error_rate": global_err_rate,
        "plates": results,
    }


def _stride_to_teacher_layer(si: int, n_strides: int, n_layers_t: int) -> int:
    """Map stride index → teacher layer by depth fraction."""
    if n_strides <= 1:
        return n_layers_t // 2
    frac = si / (n_strides - 1)
    return min(int(frac * (n_layers_t - 1) + 0.5), n_layers_t - 1)


def _get_plate_reference_layers(
    plate_name: str,
    global_ref_layers: list[int],
    stride_to_teacher: dict[int, int],
    n_layers_t: int,
) -> list[int]:
    """Determine which teacher layers to use as reference beams for a plate.

    For stride plates: use the stride's own depth layer + L0 (always include
    the most constrained reference).
    For FFN plates: use mid layer + L0.
    Deduplicates and sorts.
    """
    ref_set = set(global_ref_layers)

    if plate_name.startswith("stride_stack.stack.layers."):
        parts = plate_name.split(".")
        try:
            si = int(parts[3])
            own_layer = stride_to_teacher.get(si, n_layers_t // 2)
            ref_set.add(own_layer)
        except (IndexError, ValueError):
            pass
    elif plate_name in ("ffn_key_plate", "ffn_value_plate"):
        ref_set.add(n_layers_t // 2)

    return sorted(ref_set)


# ══════════════════════════════════════════════════════════════════════
# § 7  CLI
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Verify etched student plates against teacher reference beams "
                    "using dimensional tomography (5D → 4D → 3D consistency)."
    )
    parser.add_argument(
        "--teacher-path", type=str, required=True,
        help="Path to teacher model directory (with safetensors)",
    )
    parser.add_argument(
        "--etched-dir", type=str, required=True,
        help="Path to extract_teacher.py output (with teacher_plates.npz)",
    )
    parser.add_argument(
        "--ref-layers", type=int, nargs="+", default=None,
        help="Teacher reference layers (default: L0 + L_mid). "
             "E.g. --ref-layers 0 20",
    )
    parser.add_argument(
        "--ranks", type=int, nargs="+", default=[5, 4, 3],
        help="SVD ranks for dimensional hierarchy (default: 5 4 3)",
    )
    parser.add_argument(
        "--n-rotations", type=int, default=8,
        help="Number of 360° rotations per rank (default: 8)",
    )
    parser.add_argument(
        "--confidence", type=float, default=0.7,
        help="Confidence threshold for error detection (default: 0.7)",
    )
    parser.add_argument(
        "--correct", action="store_true",
        help="Error-correct plates using dimensional consensus",
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Output directory for corrected plates (required if --correct)",
    )

    args = parser.parse_args()

    if args.correct and not args.output:
        parser.error("--output is required when using --correct")

    log("=" * 72)
    log("  V13 Etch Verification — Dimensional Tomography")
    log("  Crystal self-similarity: 5D ⊃ 4D ⊃ 3D")
    log("=" * 72)

    verify_etch(
        teacher_path=Path(args.teacher_path),
        etched_dir=Path(args.etched_dir),
        reference_layers=args.ref_layers,
        n_rotations=args.n_rotations,
        ranks=tuple(args.ranks),
        confidence_threshold=args.confidence,
        correct=args.correct,
        output_dir=Path(args.output) if args.output else None,
    )
