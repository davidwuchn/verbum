#!/usr/bin/env python3
# MIT License
# Copyright (c) 2025 Verbum Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

"""
v14 Extraction Pipeline — Qwen3.6-27B → 1B Ternary Student.

Research context
────────────────
Verbum's central claim: the lambda compiler already exists inside large
language models as a discrete circuit, discovered by gradient descent.
Our role is instrumentation, not construction. This script is the level-3
extraction step: we pull sign-pattern "crystal plates" from a 27B teacher
and pack them into a portable 1B ternary artifact (the student).

What this script does
─────────────────────
1.  Global projection basis — SVD of the teacher's embedding matrix
    (248320, 5120) → top-1280 right singular vectors → V_proj (5120, 1280).
    This is the shared column basis for projecting all teacher weights into
    student-dimensional space.

2.  Embeddings — E_teacher (248320, 5120) @ V_proj → (248320, 1280)
    → sign() → ternary int8.

3.  Attention plates — for each (stack, layer):
    a. Determine the source teacher layer via the zone mapping (config.py).
    b. Determine layer type: GLA (linear_attn) or SSA (full_attn).
    c. Extract Q/K/V/O projections via 360° tomographic sign voting
       (multiple random orthogonal rotations, sign-vote for consensus).

4.  FFN plates — zone-voted from 3 representative teacher layers per zone.
    sign(sum_of_signs_across_3_layers) → shared plate per zone.

5.  Pack all ternary arrays as uint32 (16 values per word, 2 bits each).

6.  Save:
    • model.npz  — all packed weight arrays keyed by module path
    • state.json — extraction metadata (shapes, zone map, date, hashes)

Architecture mapping
────────────────────
Teacher (Qwen3.6-27B):  64 layers, d=5120, pattern [L,L,L,F]×16
Student (v14 1B):        3 stacks × 11 layers, d=1280, pattern [GLA×3,SSA]×2+[GLA×2,SSA]

Zone mapping:
  Stack A (encode)      ← teacher layers  0-15  (Zone A)
  Stack B (compress)    ← teacher layers 16-47  (Zone B)
  Stack C (reconstruct) ← teacher layers 48-63  (Zone C)

Key implementation notes
────────────────────────
• NumPy only — no torch, no mlx. Runs on CPU, no GPU required.
• safetensors for weight loading (sharded index supported).
• sklearn.utils.extmath.randomized_svd for fast truncated SVD when available.
• The global V_proj from embedding SVD is reused for all attention weights,
  providing a consistent semantic subspace mapping across all layers.

Teacher tensor name patterns (Qwen3.6-27B):
  Embeddings:     model.language_model.embed_tokens.weight
  Linear attn:    model.language_model.layers.{i}.linear_attn.{name}.weight
  Full attn:      model.language_model.layers.{i}.self_attn.{name}.weight
  FFN:            model.language_model.layers.{i}.mlp.{name}.weight

License: MIT (this file); teacher model: Apache-2.0 (Qwen3.6-27B)
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

try:
    from safetensors import safe_open
except ImportError:
    print(
        "ERROR: safetensors not installed. Run: pip install safetensors",
        file=sys.stderr,
    )
    sys.exit(1)

try:
    from sklearn.utils.extmath import randomized_svd as _rsvd

    _HAS_SKLEARN = True
except ImportError:
    _rsvd = None
    _HAS_SKLEARN = False

# Import v14 config — resolve path relative to this file so the script works
# regardless of working directory.
sys.path.insert(0, str(Path(__file__).parent))
from config import V14Config


# ══════════════════════════════════════════════════════════════════════
# § 0  Local teacher/student mapping constants
# ══════════════════════════════════════════════════════════════════════

# Teacher: Qwen3.6-27B
TEACHER_D_MODEL = 5120
TEACHER_N_LAYERS = 64
TEACHER_D_FF = 17408
TEACHER_VOCAB = 248320
TEACHER_PREFIX = "model.language_model"

# GLA in_proj_qkv row splits (Qwen3.6-27B linear_attn)
TEACHER_GLA_Q_ROWS = 2048   # 16 heads × 128 dim
TEACHER_GLA_K_ROWS = 2048   # 16 heads × 128 dim
TEACHER_GLA_V_ROWS = 6144   # 48 heads × 128 dim

# Stride-stack attention mapping
# Qwen3.6-27B: 64 layers, pattern [L,L,L,F]×16 (48 linear + 16 full attention)
# Student: 16 stride layers (one per stride, s1..s32768)
N_STUDENT_STRIDE_LAYERS = 16


def teacher_layer_type(layer_idx: int) -> str:
    """Determine if teacher layer is linear_attn or full_attn.

    Qwen3.6-27B pattern: [L, L, L, F] × 16.
    """
    return "full_attn" if (layer_idx % 4 == 3) else "linear_attn"


def teacher_layer_for_stride(stride_idx: int) -> int:
    """Map student stride index (0-15) to teacher layer for attention extraction.

    Spreads 16 strides across 64 teacher layers (every 4th layer).
    """
    return stride_idx * 4


# FFN zone mapping — 2-stack design
# Stack A (ascending, encode→compress): early-to-mid teacher layers
# Stack C (descending, decompress→decode): mid-to-late teacher layers
FFN_LAYERS_A: tuple[int, ...] = (4, 20, 32)   # aperture → fan → mid
FFN_LAYERS_C: tuple[int, ...] = (32, 48, 56)  # mid → converge → decode


# ══════════════════════════════════════════════════════════════════════
# § 1  Logging
# ══════════════════════════════════════════════════════════════════════


def log(msg: str) -> None:
    """Print progress message to stderr with flush."""
    print(msg, file=sys.stderr, flush=True)


def log_shape(label: str, arr: np.ndarray) -> None:
    """Log an array's shape and dtype compactly."""
    log(f"    {label}: {arr.shape}  dtype={arr.dtype}")


# ══════════════════════════════════════════════════════════════════════
# § 2  Safetensors loading  (reused from v13/extract_teacher_full.py)
# ══════════════════════════════════════════════════════════════════════

# Module-level cache for the shard index (large JSON, load once per path).
_SHARD_INDEX_CACHE: dict[str, dict[str, Any]] = {}


def _load_shard_index(model_path: Path) -> dict[str, Any] | None:
    """Load model.safetensors.index.json if it exists, else None."""
    index_path = model_path / "model.safetensors.index.json"
    if index_path.exists():
        with open(index_path) as f:
            return json.load(f)
    return None


def find_shard(model_path: Path, tensor_name: str) -> Path | None:
    """Return the safetensors shard path that owns *tensor_name*.

    Strategy:
    1. Check the cached shard index (model.safetensors.index.json).
    2. Fall back to scanning all *.safetensors files in the directory.

    Returns None if the tensor is not found anywhere.
    """
    cache_key = str(model_path)
    if cache_key not in _SHARD_INDEX_CACHE:
        idx = _load_shard_index(model_path)
        if idx is not None:
            _SHARD_INDEX_CACHE[cache_key] = idx
    index = _SHARD_INDEX_CACHE.get(cache_key)
    if index:
        shard_filename = index.get("weight_map", {}).get(tensor_name)
        if shard_filename:
            return model_path / shard_filename
    # Fallback: linear scan (slow, but handles non-indexed models)
    for sf_path in sorted(model_path.glob("model*.safetensors")):
        with safe_open(str(sf_path), framework="pt") as sf:
            if tensor_name in sf.keys():
                return sf_path
    return None


def load_tensor(model_path: Path, tensor_name: str) -> np.ndarray:
    """Load a single named tensor from sharded safetensors as float32.

    Raises:
        FileNotFoundError: If tensor_name is not found in any shard.
    """
    shard_path = find_shard(model_path, tensor_name)
    if shard_path is None:
        raise FileNotFoundError(
            f"Tensor {tensor_name!r} not found in {model_path}"
        )
    with safe_open(str(shard_path), framework="pt") as sf:
        # .float() upcasts bf16/fp16 to fp32 before .numpy()
        return sf.get_tensor(tensor_name).float().numpy()


# ══════════════════════════════════════════════════════════════════════
# § 3  Truncated SVD — fast on CPU via sklearn when available
# ══════════════════════════════════════════════════════════════════════


def truncated_svd(
    M: np.ndarray, k: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute top-k truncated SVD of M (m × n).

    Returns U (m, k), S (k,), Vt (k, n) in descending singular-value order.
    Uses sklearn randomized_svd (O(m·n·k)) when available; falls back to
    numpy full SVD otherwise.

    Args:
        M: Input matrix, float32.
        k: Number of singular components to keep.

    Returns:
        (U, S, Vt) all cast to float32.
    """
    k = min(k, min(M.shape) - 1)
    if k < 1:
        k = 1
    if _HAS_SKLEARN and _rsvd is not None:
        U, S, Vt = _rsvd(M, n_components=k, n_iter=4, random_state=42)
    else:
        # Full SVD — correct but O(min(m,n)³) memory/time
        U, S, Vt = np.linalg.svd(M, full_matrices=False)
        U, S, Vt = U[:, :k], S[:k], Vt[:k, :]
    return (
        U.astype(np.float32),
        S.astype(np.float32),
        Vt.astype(np.float32),
    )


# ══════════════════════════════════════════════════════════════════════
# § 4  360° tomographic sign voting (reused from v13/extract_teacher_full.py)
# ══════════════════════════════════════════════════════════════════════


def _random_orthogonal(n: int, rng: np.random.RandomState) -> np.ndarray:
    """Generate a random orthogonal matrix via QR decomposition.

    Args:
        n: Dimension of the square orthogonal matrix.
        rng: Seeded random state for reproducibility.

    Returns:
        (n, n) float32 orthogonal matrix with det = ±1.
    """
    H = rng.randn(n, n).astype(np.float32)
    Q, R = np.linalg.qr(H)
    Q *= np.sign(np.diag(R))  # Ensure uniqueness (Haar measure)
    return Q


def extract_sign_pattern(
    W: np.ndarray,
    d_out: int,
    d_in: int,
    n_rotations: int = 8,
) -> np.ndarray:
    """Extract ternary sign pattern via 360° tomographic sign voting.

    A single SVD projection gives one 2D "photo" of the weight crystal.
    Multiple random orthogonal rotations provide additional viewing angles;
    sign-voting across all angles recovers the volumetric crystal structure.

    Protocol for cross-dimensional extraction (common case):
      1. Compute truncated SVD: W = U S Vt  (top-k components).
      2. For each rotation r:
         a. Apply random rotation to the top-k subspaces:
            P_out = R_out @ U[:, :k_out].T
            P_in  = R_in  @ Vt[:k_in, :]
         b. Project W into student dims: Wp = P_out @ W @ P_in.T  (k_out × k_in)
         c. Accumulate sign votes: votes += sign(Wp)
      3. Final result: sign(votes), shape (d_out, d_in).
      4. Fill zeros (tied votes) with random ±1.

    Same-dimension case (d_out == n_out, d_in == n_in):
      In-place rotation without SVD: W_rot = W @ R_in, accumulate sign votes.

    Args:
        W:           Teacher weight matrix (n_out, n_in), float32.
        d_out:       Student output dimension.
        d_in:        Student input dimension.
        n_rotations: Number of tomographic viewing angles (default: 8).

    Returns:
        int8 array of shape (d_out, d_in) with values in {-1, +1}.
    """
    n_out, n_in = W.shape
    rng = np.random.RandomState(42)

    if n_out == d_out and n_in == d_in:
        # Same dimensions — multi-angle in-place rotation
        votes = np.zeros((d_out, d_in), dtype=np.float32)
        for r in range(n_rotations):
            W_rot = W if r == 0 else W @ _random_orthogonal(d_in, rng)
            votes += np.sign(W_rot)
        result = np.sign(votes).astype(np.int8)
        mask = result == 0
        if mask.any():
            result[mask] = rng.choice([-1, 1], size=int(mask.sum())).astype(np.int8)
        return result

    # Cross-dimensional case: SVD basis + multi-angle voting
    k = min(max(d_out, d_in), min(n_out, n_in) - 1)
    U_base, _S, Vt_base = truncated_svd(W, k)
    k_out = min(d_out, U_base.shape[1])
    k_in = min(d_in, Vt_base.shape[0])

    votes = np.zeros((d_out, d_in), dtype=np.float32)

    for r in range(n_rotations):
        if r == 0:
            P_out = U_base[:, :k_out].T         # (k_out, n_out)
            P_in = Vt_base[:k_in, :]            # (k_in, n_in)
        else:
            R_out = _random_orthogonal(k_out, rng)
            R_in = _random_orthogonal(k_in, rng)
            P_out = R_out @ U_base[:, :k_out].T  # (k_out, n_out)
            P_in = R_in @ Vt_base[:k_in, :]     # (k_in, n_in)

        Wp = P_out @ W @ P_in.T                 # (k_out, k_in)

        angle_signs = np.zeros((d_out, d_in), dtype=np.float32)
        angle_signs[:k_out, :k_in] = np.sign(Wp)
        votes += angle_signs

    result = np.sign(votes).astype(np.int8)
    zeros = result == 0
    if zeros.any():
        result[zeros] = rng.choice([-1, 1], size=int(zeros.sum())).astype(np.int8)
    return result


# ══════════════════════════════════════════════════════════════════════
# § 5  Ternary packing — uint32 (16 values per word, 2 bits each)
# ══════════════════════════════════════════════════════════════════════


def pack_ternary_np(w_int8: np.ndarray) -> np.ndarray:
    """Pack int8 {-1, 0, +1} array [N, K] → uint32 [N, K // 16].

    Encoding:
      ternary value → 2-bit code
      -1 → 0b00 (0)
       0 → 0b01 (1)
      +1 → 0b10 (2)

    16 values are packed into one uint32, value i occupying bits [2i : 2i+2].
    This is the same encoding as v13's pack_ternary_mlx format.

    Args:
        w_int8: int8 array of shape (N, K) with values in {-1, 0, +1}.
                K must be divisible by 16.

    Returns:
        uint32 array of shape (N, K // 16).

    Raises:
        AssertionError: If K is not divisible by 16.
    """
    assert w_int8.ndim == 2, f"Expected 2D array, got shape {w_int8.shape}"
    assert w_int8.shape[1] % 16 == 0, (
        f"K ({w_int8.shape[1]}) must be divisible by 16 for uint32 packing"
    )
    N, K = w_int8.shape
    # Map {-1, 0, +1} → {0, 1, 2}
    mapped = (w_int8.astype(np.int32) + 1).astype(np.uint32)  # values in {0, 1, 2}
    packed = np.zeros((N, K // 16), dtype=np.uint32)
    for i in range(16):
        # Each group of 16 consecutive columns (strided by 16 starting at i)
        # is packed into bit positions [2i : 2i+2].
        packed |= mapped[:, i::16] << (i * 2)
    return packed


def pack_ternary_uint8_np(w_int8: np.ndarray) -> np.ndarray:
    """Pack int8 {-1, 0, +1} array [N, K] → uint8 [N, K // 4].

    Matches TernaryEmbedding's uint8 format (4 values per byte):
      Encoding: {-1 → 0b00, 0 → 0b01, +1 → 0b10}
      Bit positions: {7:6, 5:4, 3:2, 1:0} for columns {4k, 4k+1, 4k+2, 4k+3}

    K must be divisible by 4.
    """
    assert w_int8.ndim == 2, f"Expected 2D array, got shape {w_int8.shape}"
    assert w_int8.shape[1] % 4 == 0, (
        f"K ({w_int8.shape[1]}) must be divisible by 4 for uint8 packing"
    )
    w_shifted = (w_int8.astype(np.int16) + 1).astype(np.uint8)
    packed = (
        (w_shifted[:, 0::4] << 6) |
        (w_shifted[:, 1::4] << 4) |
        (w_shifted[:, 2::4] << 2) |
        w_shifted[:, 3::4]
    )
    return packed.astype(np.uint8)


# ══════════════════════════════════════════════════════════════════════
# § 6  Global projection basis — embedding SVD
# ══════════════════════════════════════════════════════════════════════


def compute_global_projection(
    model_path: Path,
    d_model: int,
    teacher_d_model: int,
    cfg: V14Config,
) -> np.ndarray:
    """Compute shared column projection basis from teacher embeddings.

    Loads the teacher embedding matrix E (vocab, teacher_d_model), computes
    its truncated SVD, and returns the top-d_model right singular vectors
    as V_proj (teacher_d_model, d_model).

    This V_proj is the shared semantic subspace: projecting any teacher
    weight matrix W (…, teacher_d_model) by (W @ V_proj) maps it into
    student-dimensional space while preserving the dominant geometric
    structure of the teacher's representation space.

    Args:
        model_path:       Path to teacher model directory.
        d_model:          Student hidden dimension (target SVD rank).
        teacher_d_model:  Teacher hidden dimension.
        cfg:              V14Config instance (for tensor name construction).

    Returns:
        V_proj: float32 array (teacher_d_model, d_model).
    """
    t0 = time.time()
    embed_name = f"{TEACHER_PREFIX}.embed_tokens.weight"
    log(f"  Loading embeddings: {embed_name}")
    E = load_tensor(model_path, embed_name)
    log(f"  Embedding shape: {E.shape}  dtype={E.dtype}")

    log(f"  Computing truncated SVD (top-{d_model} components) ...")
    _U, _S, Vt = truncated_svd(E, d_model)  # Vt: (d_model, teacher_d_model)
    V_proj = Vt.T  # (teacher_d_model, d_model)
    del E, _U, _S, Vt
    log(f"  V_proj shape: {V_proj.shape}  ({time.time() - t0:.1f}s)")
    return V_proj


# ══════════════════════════════════════════════════════════════════════
# § 7  Embedding plate extraction
# ══════════════════════════════════════════════════════════════════════


def extract_embeddings(
    model_path: Path,
    V_proj: np.ndarray,
    cfg: V14Config,
) -> np.ndarray:
    """Extract ternary embedding plate from teacher.

    E_teacher (vocab, teacher_d_model) @ V_proj (teacher_d_model, d_model)
        → E_proj (vocab, d_model) → sign() → int8 {-1, +1}.

    Args:
        model_path: Path to teacher model directory.
        V_proj:     Global projection basis (teacher_d_model, d_model).
        cfg:        V14Config instance.

    Returns:
        int8 array (vocab_size, d_model) with values in {-1, +1}.
    """
    t0 = time.time()
    embed_name = f"{TEACHER_PREFIX}.embed_tokens.weight"
    log(f"  Loading embeddings for sign extraction ...")
    E = load_tensor(model_path, embed_name)  # (vocab, teacher_d_model)
    log(f"  Projecting: {E.shape} @ {V_proj.shape} ...")

    # Project in chunks to avoid peak memory explosion
    # (248320 × 5120) × (5120 × 1280) = ~5.1 GB at fp32 — do in 32 chunks
    vocab = E.shape[0]
    chunk = max(1, vocab // 32)
    E_proj = np.zeros((vocab, cfg.d_model), dtype=np.float32)
    for start in range(0, vocab, chunk):
        end = min(start + chunk, vocab)
        E_proj[start:end] = E[start:end] @ V_proj

    del E
    log(f"  E_proj range: [{E_proj.min():.4f}, {E_proj.max():.4f}]")

    signs = np.sign(E_proj).astype(np.int8)
    del E_proj

    # Replace zeros (exact zero is rare but possible)
    zeros = signs == 0
    if zeros.any():
        rng = np.random.RandomState(7)
        signs[zeros] = rng.choice([-1, 1], size=int(zeros.sum())).astype(np.int8)

    log(f"  Embedding signs: {signs.shape}  ({time.time() - t0:.1f}s)")
    return signs


# ══════════════════════════════════════════════════════════════════════
# § 8  Attention plate extraction — SSA (full_attn) layers
# ══════════════════════════════════════════════════════════════════════


def extract_ssa_plates(
    model_path: Path,
    teacher_layer: int,
    cfg: V14Config,
    n_rotations: int,
) -> dict[str, np.ndarray]:
    """Extract Q/K/V/O plates from a teacher full-attention (SSA) layer.

    Teacher SSA shapes (Qwen3.6-27B):
      q_proj.weight:  (12288, 5120)  = (96 heads × 128 dim, d_model)
      k_proj.weight:  (1024, 5120)   = (8 heads × 128 dim, d_model)
      v_proj.weight:  (1024, 5120)   = (8 heads × 128 dim, d_model)
      o_proj.weight:  (5120, 12288)  = (d_model, 96 heads × 128 dim)

    Student target shapes (all square after projection):
      q_proj: (d_model, d_model) = (1280, 1280)
      k_proj: (d_model, d_model) = (1280, 1280)
      v_proj: (d_model, d_model) = (1280, 1280)
      o_proj: (d_model, d_model) = (1280, 1280)

    Args:
        model_path:    Path to teacher model directory.
        teacher_layer: Teacher layer index (0-based).
        cfg:           V14Config instance.
        n_rotations:   Tomographic viewing angles for sign voting.

    Returns:
        Dict with keys "q", "k", "v", "o" → int8 (d_model, d_model).
    """
    prefix = f"{TEACHER_PREFIX}.layers.{teacher_layer}.self_attn"
    plates: dict[str, np.ndarray] = {}

    for proj_name, key in [
        ("q_proj", "q"),
        ("k_proj", "k"),
        ("v_proj", "v"),
        ("o_proj", "o"),
    ]:
        tensor_name = f"{prefix}.{proj_name}.weight"
        W = load_tensor(model_path, tensor_name)
        log(f"    SSA layer {teacher_layer} {proj_name}: {W.shape}")
        plates[key] = extract_sign_pattern(
            W, d_out=cfg.d_model, d_in=cfg.d_model, n_rotations=n_rotations
        )
        del W

    return plates


# ══════════════════════════════════════════════════════════════════════
# § 9  Attention plate extraction — GLA (linear_attn) layers
# ══════════════════════════════════════════════════════════════════════


def extract_gla_plates(
    model_path: Path,
    teacher_layer: int,
    cfg: V14Config,
    n_rotations: int,
) -> dict[str, np.ndarray]:
    """Extract Q/K/V/O plates from a teacher linear-attention (GLA) layer.

    Teacher GLA shapes (Qwen3.6-27B):
      linear_attn.in_proj_qkv.weight: (10240, 5120)
        Rows split as:
          Q: rows [0      : 2048]   = 16 heads × 128 dim
          K: rows [2048   : 4096]   = 16 heads × 128 dim
          V: rows [4096   : 10240]  = 48 heads × 128 dim (GQA: more V heads)
      linear_attn.in_proj_z.weight:  (6144, 5120)
          (gate tensor — not extracted for student, logged for completeness)
      linear_attn.out_proj.weight:   (5120, 6144)
          Note: in_dim is 6144 = 48 V-heads × 128 dim; out_dim is d_model.

    Student target shapes:
      q: (d_model, d_model) = (1280, 1280)
      k: (d_model, d_model) = (1280, 1280)
      v: (d_model, d_model) = (1280, 1280)
      o: (d_model, d_model) = (1280, 1280)

    Args:
        model_path:    Path to teacher model directory.
        teacher_layer: Teacher layer index (0-based).
        cfg:           V14Config instance.
        n_rotations:   Tomographic viewing angles for sign voting.

    Returns:
        Dict with keys "q", "k", "v", "o" → int8 (d_model, d_model).
    """
    prefix = f"{TEACHER_PREFIX}.layers.{teacher_layer}.linear_attn"
    plates: dict[str, np.ndarray] = {}

    # ── in_proj_qkv: split into Q, K, V sub-matrices ──────────────
    qkv_name = f"{prefix}.in_proj_qkv.weight"
    W_qkv = load_tensor(model_path, qkv_name)  # (10240, 5120)
    log(f"    GLA layer {teacher_layer} in_proj_qkv: {W_qkv.shape}")
    assert W_qkv.shape[0] == TEACHER_GLA_Q_ROWS + TEACHER_GLA_K_ROWS + TEACHER_GLA_V_ROWS, (
        f"Expected in_proj_qkv rows = {TEACHER_GLA_Q_ROWS + TEACHER_GLA_K_ROWS + TEACHER_GLA_V_ROWS}, "
        f"got {W_qkv.shape[0]}"
    )

    q_end = TEACHER_GLA_Q_ROWS                           # 2048
    k_end = TEACHER_GLA_Q_ROWS + TEACHER_GLA_K_ROWS      # 4096

    W_q = W_qkv[:q_end, :]                 # (2048, 5120)
    W_k = W_qkv[q_end:k_end, :]            # (2048, 5120)
    W_v = W_qkv[k_end:, :]                 # (6144, 5120)
    del W_qkv

    log(f"    GLA Q sub-matrix: {W_q.shape}")
    plates["q"] = extract_sign_pattern(
        W_q, d_out=cfg.d_model, d_in=cfg.d_model, n_rotations=n_rotations
    )
    del W_q

    log(f"    GLA K sub-matrix: {W_k.shape}")
    plates["k"] = extract_sign_pattern(
        W_k, d_out=cfg.d_model, d_in=cfg.d_model, n_rotations=n_rotations
    )
    del W_k

    log(f"    GLA V sub-matrix: {W_v.shape}")
    plates["v"] = extract_sign_pattern(
        W_v, d_out=cfg.d_model, d_in=cfg.d_model, n_rotations=n_rotations
    )
    del W_v

    # ── out_proj: (5120, 6144) → student (d_model, d_model) ───────
    out_name = f"{prefix}.out_proj.weight"
    W_out = load_tensor(model_path, out_name)  # (5120, 6144)
    log(f"    GLA layer {teacher_layer} out_proj: {W_out.shape}")
    plates["o"] = extract_sign_pattern(
        W_out, d_out=cfg.d_model, d_in=cfg.d_model, n_rotations=n_rotations
    )
    del W_out

    return plates


# ══════════════════════════════════════════════════════════════════════
# § 10  FFN plate extraction — zone-voted across 3 teacher layers
# ══════════════════════════════════════════════════════════════════════


def extract_ffn_plates_for_zone(
    model_path: Path,
    teacher_layers: tuple[int, ...],
    cfg: V14Config,
    n_rotations: int,
    zone_name: str,
) -> dict[str, np.ndarray]:
    """Extract zone-voted FFN plates (gate, up, down) from 3 teacher layers.

    For each of the 3 representative teacher layers in the zone:
      1. Load gate_proj, up_proj, down_proj.
      2. Extract sign pattern: gate/up project to (d_ff, d_model);
         down projects to (d_model, d_ff).
      3. Accumulate votes: votes += extracted_signs.

    Final plate = sign(votes).  Majority wins; ties → random ±1.

    Teacher FFN shapes (Qwen3.6-27B, SwiGLU):
      mlp.gate_proj.weight: (17408, 5120) = (d_ff_teacher, d_model_teacher)
      mlp.up_proj.weight:   (17408, 5120) = (d_ff_teacher, d_model_teacher)
      mlp.down_proj.weight: (5120, 17408) = (d_model_teacher, d_ff_teacher)

    Student FFN shapes:
      gate: (d_ff, d_model) = (5120, 1280)
      up:   (d_ff, d_model) = (5120, 1280)
      down: (d_model, d_ff) = (1280, 5120)

    Args:
        model_path:    Path to teacher model directory.
        teacher_layers: 3 teacher layer indices for zone voting.
        cfg:           V14Config instance.
        n_rotations:   Tomographic viewing angles.
        zone_name:     Human-readable zone identifier for logging.

    Returns:
        Dict with keys "gate", "up", "down" → int8 arrays.
    """
    log(f"  FFN zone {zone_name}: voting across teacher layers {teacher_layers}")

    gate_votes = np.zeros((cfg.d_ff, cfg.d_model), dtype=np.float32)
    up_votes   = np.zeros((cfg.d_ff, cfg.d_model), dtype=np.float32)
    down_votes = np.zeros((cfg.d_model, cfg.d_ff), dtype=np.float32)

    for teacher_layer in teacher_layers:
        layer_prefix = f"{TEACHER_PREFIX}.layers.{teacher_layer}.mlp"

        W_gate = load_tensor(model_path, f"{layer_prefix}.gate_proj.weight")
        log(f"    layer {teacher_layer} gate_proj: {W_gate.shape}")
        gate_votes += extract_sign_pattern(
            W_gate, d_out=cfg.d_ff, d_in=cfg.d_model, n_rotations=n_rotations
        ).astype(np.float32)
        del W_gate

        W_up = load_tensor(model_path, f"{layer_prefix}.up_proj.weight")
        log(f"    layer {teacher_layer} up_proj:   {W_up.shape}")
        up_votes += extract_sign_pattern(
            W_up, d_out=cfg.d_ff, d_in=cfg.d_model, n_rotations=n_rotations
        ).astype(np.float32)
        del W_up

        W_down = load_tensor(model_path, f"{layer_prefix}.down_proj.weight")
        log(f"    layer {teacher_layer} down_proj: {W_down.shape}")
        down_votes += extract_sign_pattern(
            W_down, d_out=cfg.d_model, d_in=cfg.d_ff, n_rotations=n_rotations
        ).astype(np.float32)
        del W_down

    def _vote_to_signs(votes: np.ndarray, seed: int) -> np.ndarray:
        result = np.sign(votes).astype(np.int8)
        zeros = result == 0
        if zeros.any():
            rng = np.random.RandomState(seed)
            result[zeros] = rng.choice([-1, 1], size=int(zeros.sum())).astype(np.int8)
        return result

    return {
        "gate": _vote_to_signs(gate_votes, 100),
        "up":   _vote_to_signs(up_votes,   101),
        "down": _vote_to_signs(down_votes, 102),
    }


# ══════════════════════════════════════════════════════════════════════
# § 11  Verification — load saved NPZ and check all shapes
# ══════════════════════════════════════════════════════════════════════


def verify_checkpoint(output_dir: Path, cfg: V14Config) -> bool:
    """Load saved model.npz and verify expected shapes for all keys.

    Args:
        output_dir: Directory where model.npz was saved.
        cfg:        V14Config used during extraction.

    Returns:
        True if all shapes match expectations, False otherwise.
    """
    npz_path = output_dir / "model.npz"
    log(f"\n── Verification ─────────────────────────────────────────────")
    log(f"  Loading {npz_path} ...")

    try:
        data = np.load(str(npz_path))
    except Exception as e:
        log(f"  ERROR loading NPZ: {e}")
        return False

    keys = sorted(data.files)
    log(f"  Found {len(keys)} arrays")
    errors: list[str] = []

    # Expected dims after packing
    d = cfg.d_model          # 1280
    d16 = d // 16            # 80   (uint32 for TernaryLinear)
    d4 = d // 4              # 320  (uint8 for TernaryEmbedding)
    dff = cfg.d_ff           # 5120
    dff16 = dff // 16        # 320
    vocab = cfg.vocab_size   # 248320

    # Expected key prefixes for attention and FFN
    # Attention: shared_stride_stack.layers.{0-15}.{q,k,v,o}
    # FFN: stack_a.ffn.{gate,up,down} and stack_c.ffn.{gate,up,down}
    for key in keys:
        arr = data[key]
        # Embedding: (vocab, d // 4) uint8 — TernaryEmbedding format
        if key == "embed_tokens":
            expected = (vocab, d4)
        # Attention projections under shared_stride_stack: (d, d // 16)
        elif key.startswith("shared_stride_stack.") and (
            key.endswith(".q") or key.endswith(".k")
            or key.endswith(".v") or key.endswith(".o")
        ):
            expected = (d, d16)
        # FFN gate/up: (d_ff, d // 16)
        elif key.endswith(".gate") or key.endswith(".up"):
            expected = (dff, d16)
        # FFN down: (d, d_ff // 16)
        elif key.endswith(".down"):
            expected = (d, dff16)
        else:
            # Unknown key — just report shape
            log(f"  [?] {key}: {arr.shape}")
            continue

        if arr.shape == expected:
            log(f"  [✓] {key}: {arr.shape}")
        else:
            msg = f"  [✗] {key}: got {arr.shape}, expected {expected}"
            log(msg)
            errors.append(msg)

    data.close()

    if errors:
        log(f"\n  VERIFICATION FAILED — {len(errors)} shape mismatch(es):")
        for e in errors:
            log(f"    {e}")
        return False

    log(f"  All shapes verified ✓")
    return True


# ══════════════════════════════════════════════════════════════════════
# § 12  Main extraction pipeline
# ══════════════════════════════════════════════════════════════════════


def run_extraction(
    teacher_path: Path,
    output_dir: Path,
    n_rotations: int = 8,
    skip_embeddings: bool = False,
    skip_attention: bool = False,
    cfg: V14Config | None = None,
) -> None:
    """Full v14 extraction pipeline: teacher → ternary student checkpoint.

    Stages:
      1. Global V_proj from embedding SVD.
      2. Embedding signs (vocab × d_model) → pack → model.npz key "embed_tokens".
      3. For each stack and layer: attention Q/K/V/O → pack → keyed by path.
      4. For each stack: FFN gate/up/down (zone-voted) → pack → keyed by path.
      5. Save model.npz and state.json.
      6. Verify saved checkpoint.

    Args:
        teacher_path:    Path to teacher model directory (safetensors shards).
        output_dir:      Directory for output checkpoint files.
        n_rotations:     Tomographic viewing angles (default: 8).
        skip_embeddings: If True, skip embedding extraction.
        skip_attention:  If True, skip attention extraction.
        cfg:             V14Config (uses defaults if None).
    """
    t_total = time.time()

    if cfg is None:
        cfg = V14Config()

    output_dir.mkdir(parents=True, exist_ok=True)

    log("=" * 72)
    log("  V14 Extraction Pipeline — Qwen3.6-27B → 1B Ternary Student")
    log("=" * 72)
    log(f"  Teacher path:  {teacher_path}")
    log(f"  Output dir:    {output_dir}")
    log(f"  d_model:          {cfg.d_model}")
    log(f"  d_ff:             {cfg.d_ff}")
    log(f"  n_stacks:         {cfg.n_stacks}")
    log(f"  stride_layers:    {N_STUDENT_STRIDE_LAYERS}")
    log(f"  n_rotations:      {n_rotations}")
    log(f"  sklearn SVD:   {_HAS_SKLEARN}")
    log("")

    # Accumulate all packed arrays
    npz_data: dict[str, np.ndarray] = {}
    shapes_log: dict[str, list[int]] = {}  # for state.json

    # ── Stage 1: Global projection basis ─────────────────────────
    log("── Stage 1: Global projection basis (embedding SVD) ────────")
    V_proj = compute_global_projection(
        teacher_path, cfg.d_model, TEACHER_D_MODEL, cfg
    )  # (teacher_d_model, d_model)

    # ── Stage 2: Embedding plate ──────────────────────────────────
    if not skip_embeddings:
        log("\n── Stage 2: Embedding plate ────────────────────────────────")
        t_emb = time.time()
        emb_signs = extract_embeddings(teacher_path, V_proj, cfg)
        # emb_signs: (vocab, d_model) int8

        emb_packed = pack_ternary_uint8_np(emb_signs)
        # emb_packed: (vocab, d_model // 4) uint8 — matches TernaryEmbedding format
        key = "embed_tokens"
        npz_data[key] = emb_packed
        shapes_log[key] = list(emb_packed.shape)
        log(f"  Packed embedding: {emb_signs.shape} → {emb_packed.shape}  "
            f"({time.time() - t_emb:.1f}s)")
        del emb_signs, emb_packed

    # ── Stage 3: Attention plates — shared stride stack ───────────
    if not skip_attention:
        log("\n── Stage 3: Attention plates (shared_stride_stack) ────────")
        attn_count = 0

        for stride_idx in range(N_STUDENT_STRIDE_LAYERS):
            teacher_layer = teacher_layer_for_stride(stride_idx)
            t_layer_type = teacher_layer_type(teacher_layer)
            t_layer = time.time()

            log(f"  [stride {stride_idx:02d}] → teacher layer {teacher_layer} ({t_layer_type})")

            # Dispatch based on TEACHER layer type (determines which tensors
            # exist in the teacher safetensors). The student gets Q/K/V/O
            # plates regardless of its own stride type — sign topology is
            # architecture-independent (r=0.998).
            if t_layer_type == "full_attn":
                plates = extract_ssa_plates(
                    teacher_path, teacher_layer, cfg, n_rotations
                )
            else:  # linear_attn
                plates = extract_gla_plates(
                    teacher_path, teacher_layer, cfg, n_rotations
                )

            # Pack and store each projection under shared_stride_stack
            for proj_name, signs in plates.items():
                # signs: (d_model, d_model) int8
                packed = pack_ternary_np(signs)
                # packed: (d_model, d_model // 16) uint32
                key = f"shared_stride_stack.layers.{stride_idx}.{proj_name}"
                npz_data[key] = packed
                shapes_log[key] = list(packed.shape)
                attn_count += 1
                del signs, packed

            log(f"    Done in {time.time() - t_layer:.1f}s")

        log(f"\n  Attention total: {attn_count} packed arrays "
            f"({N_STUDENT_STRIDE_LAYERS} strides × 4 projections)")

    # ── Stage 4: FFN plates (zone-voted) — 2 stacks ──────────────
    log("\n── Stage 4: FFN plates (zone-voted, 2 stacks) ──────────────")
    ffn_config: dict[str, tuple[int, ...]] = {
        "stack_a": FFN_LAYERS_A,
        "stack_c": FFN_LAYERS_C,
    }
    for stack_name, ffn_layers in ffn_config.items():
        t_ffn = time.time()
        ffn_plates = extract_ffn_plates_for_zone(
            teacher_path, ffn_layers, cfg, n_rotations, zone_name=stack_name
        )
        for ffn_key, signs in ffn_plates.items():
            packed = pack_ternary_np(signs)
            key = f"{stack_name}.ffn.{ffn_key}"
            npz_data[key] = packed
            shapes_log[key] = list(packed.shape)
            del signs, packed
        log(f"  {stack_name} FFN done in {time.time() - t_ffn:.1f}s")

    # ── Stage 5: Save checkpoint ─────────────────────────────────
    log("\n── Stage 5: Saving checkpoint ──────────────────────────────")
    npz_path = output_dir / "model.npz"
    t_save = time.time()
    np.savez_compressed(str(npz_path), **npz_data)
    log(f"  Saved model.npz: {npz_path.stat().st_size / 1024 / 1024:.1f} MB  "
        f"({time.time() - t_save:.1f}s)")
    log(f"  Total arrays: {len(npz_data)}")

    # Build and save state.json
    state = {
        "version": "v14",
        "extraction_date": datetime.datetime.utcnow().isoformat() + "Z",
        "teacher": {
            "path": str(teacher_path),
            "d_model": TEACHER_D_MODEL,
            "n_layers": TEACHER_N_LAYERS,
            "d_ff": TEACHER_D_FF,
            "vocab_size": TEACHER_VOCAB,
            "layer_pattern": "[L,L,L,F] × 16 (48 linear + 16 full attention)",
        },
        "student": {
            "d_model": cfg.d_model,
            "d_ff": cfg.d_ff,
            "n_stacks": cfg.n_stacks,
            "n_stride_layers": N_STUDENT_STRIDE_LAYERS,
            "stride_pattern": "s1..s32768 (10 composition + 6 retrieval)",
            "vocab_size": cfg.vocab_size,
            "n_heads": cfg.n_heads,
            "d_head": cfg.d_head,
        },
        "zone_mapping": {
            "stack_a": {
                "description": "ascending (encode→compress)",
                "ffn_vote_layers": list(FFN_LAYERS_A),
            },
            "stack_c": {
                "description": "descending (decompress→decode)",
                "ffn_vote_layers": list(FFN_LAYERS_C),
            },
        },
        "extraction_flags": {
            "n_rotations": n_rotations,
            "skip_embeddings": skip_embeddings,
            "skip_attention": skip_attention,
            "sklearn_svd": _HAS_SKLEARN,
        },
        "packing": {
            "format": "uint32",
            "values_per_word": 16,
            "bits_per_value": 2,
            "encoding": "{-1: 0b00, 0: 0b01, +1: 0b10}",
        },
        "shapes": shapes_log,
        "elapsed_s": round(time.time() - t_total, 1),
    }

    state_path = output_dir / "state.json"
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)
    log(f"  Saved state.json: {state_path}")

    # ── Stage 6: Verification ─────────────────────────────────────
    ok = verify_checkpoint(output_dir, cfg)

    # ── Summary ───────────────────────────────────────────────────
    elapsed = time.time() - t_total
    log(f"\n{'=' * 72}")
    log(f"  V14 EXTRACTION {'COMPLETE ✓' if ok else 'COMPLETE (with warnings ✗)'}")
    log(f"{'─' * 72}")
    log(f"  Arrays saved:    {len(npz_data)}")
    log(f"  Checkpoint dir:  {output_dir}")
    log(f"  model.npz size:  {npz_path.stat().st_size / 1024 / 1024:.1f} MB")
    log(f"  Total elapsed:   {elapsed:.1f}s  ({elapsed / 60:.1f} min)")
    log(f"{'=' * 72}")
    if not ok:
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════════
# § 13  CLI entry point
# ══════════════════════════════════════════════════════════════════════


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="extract_qwen36",
        description=(
            "v14 extraction pipeline: pull ternary sign-pattern crystal plates "
            "from Qwen3.6-27B (Apache-2.0) into a portable 1B student checkpoint."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default run (all stages, 8 rotations):
  uv run python scripts/v14/extract_qwen36.py

  # Custom teacher path:
  uv run python scripts/v14/extract_qwen36.py \\
      --teacher-path ~/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/abc123

  # Skip embeddings (attention + FFN only):
  uv run python scripts/v14/extract_qwen36.py --skip-embeddings

  # Quick smoke test — FFN only, 2 rotations:
  uv run python scripts/v14/extract_qwen36.py \\
      --skip-embeddings --skip-attention --n-rotations 2
""",
    )
    _default_teacher_path = (
        "~/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/latest"
    )

    parser.add_argument(
        "--teacher-path",
        type=str,
        default=str(Path(_default_teacher_path).expanduser()),
        help=(
            "Path to teacher model directory containing safetensors shards. "
            f"Default: {_default_teacher_path}"
        ),
    )
    parser.add_argument(
        "--output",
        type=str,
        default="checkpoints/v14-extracted",
        help="Output directory for the extracted checkpoint. Default: checkpoints/v14-extracted",
    )
    parser.add_argument(
        "--skip-embeddings",
        action="store_true",
        help="Skip embedding plate extraction.",
    )
    parser.add_argument(
        "--skip-attention",
        action="store_true",
        help="Skip attention Q/K/V/O plate extraction.",
    )
    parser.add_argument(
        "--n-rotations",
        type=int,
        default=8,
        help=(
            "Number of orthogonal rotations for tomographic sign voting. "
            "Higher = more stable at cost of more compute. Default: 8"
        ),
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    teacher_path = Path(args.teacher_path).expanduser()
    output_dir = Path(args.output)

    if not teacher_path.exists():
        log(f"ERROR: Teacher path does not exist: {teacher_path}")
        log(
            "Hint: Download with:\n"
            "  huggingface-cli download Qwen/Qwen3.6-27B --local-dir <path>"
        )
        sys.exit(1)

    cfg = V14Config()

    run_extraction(
        teacher_path=teacher_path,
        output_dir=output_dir,
        n_rotations=args.n_rotations,
        skip_embeddings=args.skip_embeddings,
        skip_attention=args.skip_attention,
        cfg=cfg,
    )


if __name__ == "__main__":
    main()
