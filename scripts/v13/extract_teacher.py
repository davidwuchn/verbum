#!/usr/bin/env python3
"""
v13 Teacher Crystal Extraction — etch FFN plates from a teacher model.

Pipeline:
  1. Load teacher FFN weights from safetensors (weight-only, no inference)
  2. SVD-project teacher FFN weights to student dimensions
  3. sign(projected) → ternary plates (key + value)
  4. Pack into V13 model, freeze FFN plates only
  5. Attention Q/K/V/O stay random-initialized (trainable)
  6. Save as initial checkpoint for GD phase

Session 132 finding: attention plates should NOT be etched from the
teacher because the stride stack architecture (windowed attention at
11 power-of-2 strides, fractal bands, hourglass reuse) is fundamentally
different from the teacher's flat full-sequence attention:
  - Teacher: full-sequence causal attention with RoPE, GQA (40Q/8KV heads)
  - Student: window=8 strided attention, spiral bias, MHA (8 heads)
  - 4 of 11 strides use GLA (retrieval), not attention at all
  - Each stride runs across multiple hourglass passes

Evidence from v13-run3: combinator mirrors unchanged from init (γ_rms=0.0442
= 1/√512), stride.8.v_proj 74% silenced, attention gammas 23-34% near-zero.
The model spent gradient budget trying to UNDO the wrong etch.

FFN plates ARE valid: teacher and student FFN serve the same functional role
(nonlinear feature mixing → combinator routing). 0% near-zero gammas.

The attention crystal will be learned from scratch during training. Once
converged, the learned attention topology becomes the crystal to etch
into future models.

Usage:
    cd ~/src/verbum
    uv run python scripts/v13/extract_teacher.py \\
        --teacher-path ~/.cache/huggingface/hub/models--Qwen--Qwen3-14B/snapshots/... \\
        --output checkpoints/v13-etched

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

try:
    from safetensors import safe_open
except ImportError:
    print("ERROR: pip install safetensors", file=sys.stderr)
    sys.exit(1)

try:
    from sklearn.utils.extmath import randomized_svd as _rsvd
except ImportError:
    _rsvd = None


# ══════════════════════════════════════════════════════════════════════
# § 1  Utilities
# ══════════════════════════════════════════════════════════════════════

def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def truncated_svd(M: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Randomized truncated SVD: top-k components. O(m*n*k).

    Falls back to full SVD if sklearn not available.
    Returns U (m, k), S (k,), Vt (k, n) — descending singular value order.
    """
    k = min(k, min(M.shape) - 1)
    if k < 1 or _rsvd is None:
        U, S, Vt = np.linalg.svd(M, full_matrices=False)
        return U[:, :k].astype(np.float32), S[:k].astype(np.float32), Vt[:k, :].astype(np.float32)
    U, S, Vt = _rsvd(M, n_components=k, n_iter=4, random_state=42)
    return U.astype(np.float32), S.astype(np.float32), Vt.astype(np.float32)


# ══════════════════════════════════════════════════════════════════════
# § 2  Safetensors loading
# ══════════════════════════════════════════════════════════════════════

_SHARD_INDEX_CACHE: dict[str, dict] = {}


def _load_shard_index(model_path: Path) -> dict | None:
    index_path = model_path / "model.safetensors.index.json"
    if index_path.exists():
        with open(index_path) as f:
            return json.load(f)
    return None


def find_shard(model_path: Path, tensor_name: str) -> Path | None:
    cache_key = str(model_path)
    if cache_key not in _SHARD_INDEX_CACHE:
        idx = _load_shard_index(model_path)
        if idx is not None:
            _SHARD_INDEX_CACHE[cache_key] = idx
    index = _SHARD_INDEX_CACHE.get(cache_key)
    if index:
        shard = index["weight_map"].get(tensor_name)
        if shard:
            return model_path / shard
    for sf_path in sorted(model_path.glob("model*.safetensors")):
        with safe_open(str(sf_path), framework="pt") as sf:
            if tensor_name in sf.keys():
                return sf_path
    return None


def load_tensor(model_path: Path, tensor_name: str) -> np.ndarray:
    """Load a single tensor from sharded safetensors. Handles bfloat16."""
    shard_path = find_shard(model_path, tensor_name)
    if shard_path is None:
        raise FileNotFoundError(f"Tensor {tensor_name} not found in {model_path}")
    with safe_open(str(shard_path), framework="pt") as sf:
        return sf.get_tensor(tensor_name).float().numpy()


def detect_teacher_config(model_path: Path) -> dict:
    """Auto-detect teacher model config from config.json."""
    config_path = model_path / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            cfg = json.load(f)
        return {
            "d_model": cfg.get("hidden_size", 5120),
            "n_layers": cfg.get("num_hidden_layers", 40),
            "n_heads": cfg.get("num_attention_heads", 40),
            "n_kv_heads": cfg.get("num_key_value_heads", 8),
            "head_dim": cfg.get("head_dim", 128),
            "d_ff": cfg.get("intermediate_size", 13824),
            "model_type": cfg.get("model_type", "unknown"),
        }
    # Fallback: detect from weight shapes
    for sf_path in sorted(model_path.glob("model*.safetensors")):
        with safe_open(str(sf_path), framework="pt") as sf:
            for key in sf.keys():
                if "q_proj.weight" in key:
                    shape = sf.get_tensor(key).shape
                    return {"d_model": shape[1], "n_layers": -1, "n_heads": -1,
                            "n_kv_heads": -1, "head_dim": -1, "d_ff": -1,
                            "model_type": "unknown"}
    raise ValueError(f"Cannot detect teacher config from {model_path}")


# ══════════════════════════════════════════════════════════════════════
# § 3  Sign pattern extraction via SVD projection
# ══════════════════════════════════════════════════════════════════════

def extract_sign_pattern(
    W: np.ndarray,
    d_out: int,
    d_in: int,
    n_rotations: int = 8,
) -> np.ndarray:
    """Extract sign pattern via 360° tomographic sign voting.

    The crystal is a hologram — a single SVD projection captures one 2D
    photo. Multiple random orthogonal rotations give multiple viewing
    angles. Sign voting across all angles recovers the full volumetric
    crystal structure.

    Protocol:
      1. For each rotation (random orthogonal matrix):
         a. Rotate W: W_rot = R_out @ W @ R_in.T
         b. SVD-project to student dimensions
         c. Extract sign pattern from this viewing angle
      2. Sum all sign patterns → sign votes per position
      3. Final plate = sign(votes): positions where most angles agree

    Positions with unanimous agreement are the stable crystal structure.
    Positions where angles disagree are viewing-angle artifacts — the
    sign vote resolves them by consensus.

    W:            (out_t, in_t) teacher weight
    d_out:        student output dimension
    d_in:         student input dimension
    n_rotations:  number of viewing angles (8 = overdetermined for rank-4 crystal)

    Returns: (d_out, d_in) int8 {-1, +1}
    """
    n_out, n_in = W.shape
    rng = np.random.RandomState(42)

    if n_out == d_out and n_in == d_in:
        # Same dimensions — direct sign (97.4% fidelity, no projection needed)
        # Still do multi-angle voting by rotating in-place
        votes = np.zeros((d_out, d_in), dtype=np.float32)
        for r in range(n_rotations):
            if r == 0:
                W_rot = W  # identity rotation first
            else:
                R = _random_orthogonal(d_in, rng)
                W_rot = W @ R
            votes += np.sign(W_rot)
        result = np.sign(votes).astype(np.int8)
        result[result == 0] = rng.choice([-1, 1], size=int((result == 0).sum())).astype(np.int8)
        return result

    # Cross-dimensional: SVD basis + multi-angle voting
    k = min(max(d_out, d_in), min(n_out, n_in) - 1)

    # Get base SVD projection matrices (reused across rotations)
    U_base, S_base, Vt_base = truncated_svd(W, k)
    k_out = min(d_out, U_base.shape[1])
    k_in = min(d_in, Vt_base.shape[0])

    votes = np.zeros((d_out, d_in), dtype=np.float32)

    for r in range(n_rotations):
        if r == 0:
            # First rotation: identity (the raw SVD projection)
            P_out = U_base[:, :k_out].T
            P_in = Vt_base[:k_in, :]
        else:
            # Random orthogonal rotation in the projected subspace
            R_out = _random_orthogonal(k_out, rng)
            R_in = _random_orthogonal(k_in, rng)
            P_out = R_out @ U_base[:, :k_out].T
            P_in = R_in @ Vt_base[:k_in, :]

        Wp = P_out @ W @ P_in.T  # (k_out, k_in)

        # Accumulate sign votes in the target shape
        angle_signs = np.zeros((d_out, d_in), dtype=np.float32)
        angle_signs[:k_out, :k_in] = np.sign(Wp)
        votes += angle_signs

    # Consensus: positions where most rotations agree
    result = np.sign(votes).astype(np.int8)
    # Fill zeros (tied votes) with random
    zeros = result == 0
    if zeros.any():
        result[zeros] = rng.choice([-1, 1], size=int(zeros.sum())).astype(np.int8)

    return result


def _random_orthogonal(n: int, rng: np.random.RandomState) -> np.ndarray:
    """Generate a random orthogonal matrix via QR decomposition of Gaussian."""
    H = rng.randn(n, n).astype(np.float32)
    Q, R = np.linalg.qr(H)
    # Ensure proper rotation (det = +1) by fixing sign ambiguity
    Q *= np.sign(np.diag(R))
    return Q


def extract_magnitude(W: np.ndarray, d_out: int) -> np.ndarray:
    """Extract per-row RMS magnitude from projected teacher weight.

    Returns: (d_out,) float32 — beam magnitude (gamma seed)
    """
    n_out, n_in = W.shape
    k = min(d_out, min(n_out, n_in) - 1)
    U, S, Vt = truncated_svd(W, k)

    k_out = min(d_out, U.shape[1])
    k_in = min(d_out, Vt.shape[0])
    P_out = U[:, :k_out].T
    P_in = Vt[:k_in, :]
    Wp = P_out @ W @ P_in.T

    mags = np.zeros(d_out, dtype=np.float32)
    rms = np.sqrt(np.mean(Wp ** 2, axis=1))
    mags[:k_out] = rms.astype(np.float32)
    return mags


# ══════════════════════════════════════════════════════════════════════
# § 4  Layer mapping: teacher → student
# ══════════════════════════════════════════════════════════════════════

def teacher_layer_for_stride(stride_idx: int, n_strides: int, n_teacher_layers: int) -> int:
    """Map student stride index to teacher layer by depth fraction."""
    if n_strides <= 1:
        return n_teacher_layers // 2
    frac = stride_idx / (n_strides - 1)
    return min(int(frac * (n_teacher_layers - 1) + 0.5), n_teacher_layers - 1)


def teacher_layer_for_ffn(n_teacher_layers: int) -> int:
    """Pick a representative layer for FFN extraction. Middle layer."""
    return n_teacher_layers // 2


# ══════════════════════════════════════════════════════════════════════
# § 5  Main extraction pipeline
# ══════════════════════════════════════════════════════════════════════

def extract_crystal(
    teacher_path: Path,
    d_student: int = 512,
    d_ff_student: int = 2048,
    n_strides: int = 11,
    d_state: int = 64,
    n_heads: int = 8,
    n_rotations: int = 8,
    output_dir: Path | None = None,
) -> dict:
    """Extract FFN crystal from teacher into student plate format.

    Only extracts FFN plates (key + value). Attention Q/K/V/O plates
    are NOT extracted — the stride stack architecture is too different
    from flat attention for teacher etch to help. Attention topology
    will be learned from scratch during training.

    Returns dict of {param_path: (signs_int8, magnitude_float32)} pairs
    ready to pack into TernaryLinear weights.
    """
    t0 = time.time()

    # Detect teacher config
    teacher_cfg = detect_teacher_config(teacher_path)
    d_t = teacher_cfg["d_model"]
    n_layers_t = teacher_cfg["n_layers"]
    d_ff_t = teacher_cfg["d_ff"]

    log(f"Teacher: {teacher_cfg['model_type']}, d={d_t}, layers={n_layers_t}, d_ff={d_ff_t}")
    log(f"Student: d={d_student}, d_ff={d_ff_student}, strides={n_strides}")
    log(f"Rotations: {n_rotations} (360° tomographic sign voting)")
    log(f"Mode: FFN-only extraction (attention learned from scratch)")

    plates: dict[str, tuple[np.ndarray, np.ndarray]] = {}

    # ── Attention plates: SKIPPED ─────────────────────────────
    # Session 132 finding: stride stack attention (windowed, multi-stride,
    # fractal bands, hourglass reuse) is architecturally incompatible with
    # teacher flat attention (full-sequence, RoPE, GQA). Evidence:
    #   - Combinator mirrors frozen at init after 5000 steps
    #   - stride.8.v_proj 74% silenced (model undoing the etch)
    #   - Cross-stride Q cosine 0.51-0.58 (75% shared = generic, not specific)
    #   - GLA strides get attention signs (meaningless)
    # Attention topology will be learned from scratch. Once converged,
    # the learned crystal becomes the etch source for future models.
    log(f"\n  Attention plates: SKIPPED (stride stack ≠ flat attention)")
    log(f"    {n_strides} stride layers × 4 projections = {n_strides * 4} plates NOT extracted")

    # ── FFN plates (WHNF mechanical lookup) ─────────────────
    # Teacher FFN and student FFN serve the same functional role:
    # input → nonlinear → output (combinator routing). Valid to etch.
    ffn_layer = teacher_layer_for_ffn(n_layers_t)
    log(f"\n  FFN ← teacher layer {ffn_layer}")

    ffn_prefix = f"model.layers.{ffn_layer}.mlp"

    # Key plate: up_proj (d_ff_t, d_t) → (d_ff_student, d_student)
    W_up = load_tensor(teacher_path, f"{ffn_prefix}.up_proj.weight")
    signs = extract_sign_pattern(W_up, d_ff_student, d_student, n_rotations)
    mags = extract_magnitude(W_up, d_ff_student)
    plates["ffn_key_plate"] = (signs, mags)

    # Value plate: down_proj (d_t, d_ff_t) → (d_student, d_ff_student)
    W_down = load_tensor(teacher_path, f"{ffn_prefix}.down_proj.weight")
    signs = extract_sign_pattern(W_down, d_student, d_ff_student, n_rotations)
    mags = extract_magnitude(W_down, d_student)
    plates["ffn_value_plate"] = (signs, mags)

    dt = time.time() - t0
    log(f"\n  Extraction complete: {len(plates)} plates (FFN only), {dt:.1f}s")

    # ── Save if output_dir specified ──────────────────────────
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save plates as NPZ
        npz_data = {}
        for path, (signs, mags) in plates.items():
            npz_data[f"{path}.signs"] = signs
            npz_data[f"{path}.mags"] = mags
        npz_path = output_dir / "teacher_plates.npz"
        np.savez_compressed(str(npz_path), **npz_data)
        log(f"  Saved: {npz_path} ({npz_path.stat().st_size / 1024 / 1024:.1f} MB)")

        # Save manifest
        manifest = {
            "teacher": {
                "path": str(teacher_path),
                "config": teacher_cfg,
            },
            "student": {
                "d_model": d_student,
                "d_ff": d_ff_student,
                "n_strides": n_strides,
                "d_state": d_state,
                "n_heads": n_heads,
            },
            "plates": list(plates.keys()),
            "extraction_time_s": dt,
        }
        manifest_path = output_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        log(f"  Saved: {manifest_path}")

    return plates


# ══════════════════════════════════════════════════════════════════════
# § 6  Install plates into V13 model
# ══════════════════════════════════════════════════════════════════════

def install_plates(model, plates: dict, freeze: bool = True) -> int:
    """Write extracted sign plates into a V13 model's TernaryLinear weights.

    For each plate:
      1. Pack signs (int8) → uint32 for quantized_matmul
      2. Write packed weight to the TernaryLinear module
      3. Set gamma from extracted magnitudes (beam seed)

    Only INSTALLED plates are frozen (FFN). Attention plates are not
    installed and remain at random init with trainable topology.

    Args:
        model:  V13Model instance
        plates: dict from extract_crystal() (FFN-only)
        freeze: if True, freeze installed plates after writing

    Returns: number of plates installed
    """
    import mlx.core as mx
    sys.path.insert(0, str(Path(__file__).parent))
    from ternary import pack_ternary_mlx, TernaryLinear

    installed_modules = []
    n_installed = 0

    for plate_path, (signs, mags) in plates.items():
        # Navigate to the module
        parts = plate_path.split(".")
        mod = model
        try:
            for part in parts:
                if part.isdigit():
                    mod = mod[int(part)] if isinstance(mod, (list, tuple)) else getattr(mod, part)
                else:
                    mod = getattr(mod, part)
        except (AttributeError, IndexError, KeyError):
            log(f"  SKIP: {plate_path} (not found in model)")
            continue

        # Verify it's a TernaryLinear
        if not isinstance(mod, TernaryLinear):
            log(f"  SKIP: {plate_path} (not TernaryLinear, is {type(mod).__name__})")
            continue

        # Check dimensions match
        expected_out, expected_in = mod.out_features, mod.in_features
        if signs.shape != (expected_out, expected_in):
            log(f"  WARN: {plate_path} shape mismatch: "
                f"plate={signs.shape}, model=({expected_out}, {expected_in})")
            # Trim or pad to fit
            s = np.zeros((expected_out, expected_in), dtype=np.int8)
            ro = min(signs.shape[0], expected_out)
            ci = min(signs.shape[1], expected_in)
            s[:ro, :ci] = signs[:ro, :ci]
            # Fill remaining with random
            mask = s == 0
            if mask.any():
                rng = np.random.RandomState(42)
                s[mask] = rng.choice([-1, 1], size=int(mask.sum())).astype(np.int8)
            signs = s

        # Pack and install
        signs_mx = mx.array(signs)
        packed = pack_ternary_mlx(signs_mx)
        mod.weight = packed
        mx.eval(mod.weight)

        # Set gamma from magnitudes (beam seed)
        if mags is not None and len(mags) == expected_out:
            mod.gamma = mx.array(mags)
            mx.eval(mod.gamma)

        installed_modules.append((plate_path, mod))
        n_installed += 1

    # Selectively freeze only installed plates (FFN)
    # Attention plates stay trainable — their topology will be learned
    if freeze and installed_modules:
        n_frozen = 0
        for plate_path, mod in installed_modules:
            mod.freeze(keys=["weight"])
            n_frozen += 1
            log(f"  Frozen: {plate_path}.weight")
        log(f"  Frozen {n_frozen} installed plates (attention plates remain trainable)")

    log(f"  Installed {n_installed}/{len(plates)} plates")
    return n_installed


# ══════════════════════════════════════════════════════════════════════
# § 7  Full pipeline: extract → install → save checkpoint
# ══════════════════════════════════════════════════════════════════════

def etch_from_teacher(
    teacher_path: str,
    output_dir: str = "checkpoints/v13-etched",
    n_rotations: int = 8,
    **student_overrides,
) -> None:
    """Complete pipeline: extract teacher FFN crystal → install into V13 → save.

    Only FFN plates are extracted and frozen. Attention Q/K/V/O plates
    remain at random initialization with trainable topology. The stride
    stack attention crystal will be learned from scratch during training.
    """
    import mlx.core as mx
    sys.path.insert(0, str(Path(__file__).parent))
    from config import V13Config
    from model import V13Model
    from ternary import restore_ternary

    teacher_path = Path(teacher_path)
    output_dir = Path(output_dir)

    log("=" * 72)
    log("  V13 Teacher Crystal Extraction (FFN-only)")
    log("=" * 72)

    # Create student model
    cfg = V13Config(**{k: v for k, v in student_overrides.items()
                       if hasattr(V13Config, k)})
    log(f"\n  Student config: d_model={cfg.d_model}, d_ff={cfg.d_ff}, "
        f"strides={cfg.n_strides}, passes={cfg.n_passes}")

    model = V13Model(cfg)

    # Extract crystal from teacher (FFN only)
    log(f"\n  Extracting from: {teacher_path}")
    plates = extract_crystal(
        teacher_path,
        d_student=cfg.d_model,
        d_ff_student=cfg.d_ff,
        n_strides=cfg.n_strides,
        d_state=cfg.d_state,
        n_heads=cfg.n_heads,
        n_rotations=n_rotations,
        output_dir=output_dir,
    )

    # Install FFN plates into model (freeze=True only freezes installed plates)
    log(f"\n  Installing FFN plates into V13 model...")
    n_installed = install_plates(model, plates, freeze=True)

    # Verify no corruption on installed plates
    # (attention plates are random-init, won't corrupt)
    restore_ternary(model)
    log("  Ternary integrity verified")

    # Save checkpoint
    weights_path = output_dir / "model.npz"
    model.save_weights(str(weights_path))
    log(f"  Saved model: {weights_path}")

    # Save config
    import dataclasses
    config_path = output_dir / "config.json"
    with open(config_path, "w") as f:
        json.dump(dataclasses.asdict(cfg), f, indent=2, default=str)
    log(f"  Saved config: {config_path}")

    # Summary
    from ternary import count_ternary_weights
    n_total = count_ternary_weights(model)
    n_ffn = sum(s.size for k, (s, _) in plates.items())
    log(f"\n  Summary:")
    log(f"    FFN plates installed:    {n_installed} (frozen)")
    log(f"    FFN positions:           {n_ffn:,}")
    log(f"    Attention positions:     {n_total - n_ffn:,} (trainable, random init)")
    log(f"    Total ternary positions: {n_total:,}")
    log(f"    Checkpoint:              {output_dir}")
    log(f"\n  Next: python scripts/v13/train.py --phase gd --resume {output_dir}")
    log(f"  Attention topology will crystallize during training.")
    log("=" * 72)


# ══════════════════════════════════════════════════════════════════════
# § 8  CLI
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract crystal from teacher model into V13 student plates."
    )
    parser.add_argument(
        "--teacher-path", type=str, required=True,
        help="Path to teacher model directory (with safetensors)"
    )
    parser.add_argument(
        "--output", type=str, default="checkpoints/v13-etched",
        help="Output directory for etched checkpoint"
    )
    parser.add_argument(
        "--d-model", type=int, default=512,
        help="Student d_model (default: 512)"
    )
    parser.add_argument(
        "--d-ff", type=int, default=2048,
        help="Student d_ff (default: 2048)"
    )
    parser.add_argument(
        "--n-rotations", type=int, default=8,
        help="Number of Q rotations for tomographic sign voting (default: 8)"
    )
    parser.add_argument(
        "--plates-only", action="store_true",
        help="Extract plates to NPZ only (don't create full model checkpoint)"
    )

    args = parser.parse_args()

    if args.plates_only:
        plates = extract_crystal(
            Path(args.teacher_path),
            d_student=args.d_model,
            d_ff_student=args.d_ff,
            n_rotations=args.n_rotations,
            output_dir=Path(args.output),
        )
        log(f"\nPlates saved to {args.output}/teacher_plates.npz")
    else:
        etch_from_teacher(
            teacher_path=args.teacher_path,
            output_dir=args.output,
            n_rotations=args.n_rotations,
            d_model=args.d_model,
            d_ff=args.d_ff,
        )
