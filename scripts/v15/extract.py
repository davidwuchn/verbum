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
v15 Extraction Pipeline — Qwen3.6-27B → Crystal-Native Tensor Statechart.

Research context
────────────────
Verbum's central claim: the lambda compiler already exists inside large
language models as a discrete circuit, discovered by gradient descent.
This script is the level-3 extraction step for the v15 architecture:
the crystal-native tensor statechart. Each stride is an autonomous VSM
(Beer 1972); the checkpoint IS the statechart.

What this script does
─────────────────────
1.  Global projection basis — SVD of the teacher's embedding matrix
    (vocab, 5120) → top-1280 right singular vectors → V_proj (5120, 1280).
    Shared column basis for projecting all teacher weights into student space.

2.  Embeddings — E_teacher @ V_proj → (vocab, 1280) → sign() → ternary int8.
    Packed as uint8 (4 values/byte) matching TernaryEmbedding format.

3.  FFN stride plates (NEW in v15 — per-stride, not per-zone):
    For each of the 19 strides, vote across the teacher layers mapped to
    that stride (from V15Config.stride_specs()). Two strides types:
      • 1-plate (CLASSIFY):  plate1 = sign(W_projected)
      • 2-plate (COMPUTE, LINK, EMIT): plate1 + plate2 magnitude mirror

4.  Attention plates (NEW in v15 — FULL attention strides only):
    COMPUTE (strides 5-12) and LINK (strides 13-15) use full self-attention.
    For each such stride, vote Q/K/V/O sign patterns across mapped teacher
    layers. LINEAR strides (CLASSIFY, EMIT) skip attention extraction —
    those will be trained from scratch.

5.  Save all arrays to a structured checkpoint directory.

Architecture mapping (v15)
──────────────────────────
Teacher (Qwen3.6-27B):   64 layers, d=5120, d_ff=17408, [L,L,L,F]×16
Student (v15 statechart): 19 strides, d=1280, d_ff=5120

Stride zones (ablation-verified, session 174):
  CLASSIFY (strides  0- 4): 1-plate, linear attn ← teacher L0-31
  COMPUTE  (strides  5-12): 2-plate, full attn   ← teacher L32-53
  LINK     (strides 13-15): 2-plate, full attn   ← teacher L54-58
  EMIT     (strides 16-18): 2-plate, linear attn ← teacher L59-63

Key differences from v14
─────────────────────────
• Per-stride plates, not zone-voted. V14 extracted one FFN plate per zone
  (voted across 3 representative layers). V15 extracts one plate PER STRIDE,
  voted across the teacher layers mapped to that stride.
• 2-plate format for all non-CLASSIFY strides. plate1 captures the sign
  topology (program structure); plate2 captures the magnitude mirror
  (residual after plate1 reconstruction), recovering dynamic range lost
  in a single ternary quantisation.
• Structured output directory (strides/ + attention/) instead of model.npz.
• 19 strides (5 CLASSIFY + 8 COMPUTE + 3 LINK + 3 EMIT) instead of 16.
• Attention only for FULL attention strides (COMPUTE + LINK).

What is reused from v14 (without modification)
───────────────────────────────────────────────
• find_shard / load_tensor    — safetensors shard loading
• truncated_svd               — fast truncated SVD via sklearn fallback
• extract_sign_pattern        — 360° tomographic sign voting
• pack_ternary_np             — uint32 packing (16 values/word)
• pack_ternary_uint8_np       — uint8 packing (4 values/byte, embeddings)
• compute_global_projection   — embedding SVD → V_proj basis
• extract_embeddings          — E @ V_proj → sign → int8
• extract_ssa_plates          — full-attention Q/K/V/O extraction
• extract_gla_plates          — linear-attention Q/K/V/O extraction

What is NEW in v15
──────────────────
• extract_2plate_from_votes   — 2-plate decomposition from accumulated votes
• extract_stride_ffn_plates   — per-stride FFN extraction with vote aggregation
• extract_stride_attn_plates  — per-stride attention (FULL strides only)
• run_extraction              — completely rewritten pipeline
• verify_checkpoint           — checks new directory layout
• _build_parser / main        — updated CLI

Teacher tensor name patterns (Qwen3.6-27B):
  Embeddings:   model.language_model.embed_tokens.weight
  Linear attn:  model.language_model.layers.{i}.linear_attn.{name}.weight
  Full attn:    model.language_model.layers.{i}.self_attn.{name}.weight
  FFN:          model.language_model.layers.{i}.mlp.{name}.weight

Usage:
  uv run python scripts/v15/extract.py \\
      --model-path ~/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/HASH/

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
        "ERROR: safetensors not installed. Run: uv add safetensors",
        file=sys.stderr,
    )
    sys.exit(1)

try:
    from sklearn.utils.extmath import randomized_svd as _rsvd

    _HAS_SKLEARN = True
except ImportError:
    _rsvd = None
    _HAS_SKLEARN = False

# Import v15 config — resolved relative to this file so the script works
# regardless of working directory.
sys.path.insert(0, str(Path(__file__).parent))
from config import AttnType, V15Config, Zone


# ══════════════════════════════════════════════════════════════════════
# § 0  Teacher constants
# ══════════════════════════════════════════════════════════════════════

# Teacher: Qwen3.6-27B
TEACHER_D_MODEL = 5120
TEACHER_N_LAYERS = 64
TEACHER_D_FF = 17408
TEACHER_VOCAB = 151936  # Qwen3.6 tokeniser (different from 248320 in v14)
TEACHER_PREFIX = "model.language_model"

# GLA in_proj_qkv row splits (Qwen3.6-27B linear_attn hybrid)
# Reused from v14 — teacher architecture unchanged.
TEACHER_GLA_Q_ROWS = 2048   # 16 heads × 128 dim
TEACHER_GLA_K_ROWS = 2048   # 16 heads × 128 dim
TEACHER_GLA_V_ROWS = 6144   # 48 heads × 128 dim (GQA: more V heads)


def teacher_layer_type(layer_idx: int) -> str:
    """Determine if a teacher layer uses linear_attn or full_attn.

    Qwen3.6-27B pattern: [L, L, L, F] × 16  (layers 3, 7, 11, … are full).

    Reused from v14 — teacher architecture unchanged.
    """
    return "full_attn" if (layer_idx % 4 == 3) else "linear_attn"


# ══════════════════════════════════════════════════════════════════════
# § 1  Logging
# ══════════════════════════════════════════════════════════════════════


def log(msg: str) -> None:
    """Print a progress message to stderr with immediate flush."""
    print(msg, file=sys.stderr, flush=True)


def log_shape(label: str, arr: np.ndarray) -> None:
    """Log an array's shape and dtype compactly."""
    log(f"    {label}: {arr.shape}  dtype={arr.dtype}")


# ══════════════════════════════════════════════════════════════════════
# § 2  Safetensors loading  (reused from v14/extract_qwen36.py)
# ══════════════════════════════════════════════════════════════════════

# Module-level shard-index cache — large JSON, loaded once per model path.
_SHARD_INDEX_CACHE: dict[str, dict[str, Any]] = {}


def _load_shard_index(model_path: Path) -> dict[str, Any] | None:
    """Load model.safetensors.index.json if present, else return None."""
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

    Reused from v14 (unchanged).
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
    # Fallback: linear scan (slower, handles non-indexed models).
    for sf_path in sorted(model_path.glob("model*.safetensors")):
        with safe_open(str(sf_path), framework="pt") as sf:
            if tensor_name in sf.keys():
                return sf_path
    return None


def load_tensor(model_path: Path, tensor_name: str) -> np.ndarray:
    """Load a single named tensor from sharded safetensors as float32.

    Raises:
        FileNotFoundError: If tensor_name is not found in any shard.

    Reused from v14 (unchanged).
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
# § 3  Truncated SVD  (reused from v14/extract_qwen36.py)
# ══════════════════════════════════════════════════════════════════════


def truncated_svd(
    M: np.ndarray, k: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute top-k truncated SVD of M (m × n).

    Returns U (m, k), S (k,), Vt (k, n) in descending singular-value order.
    Uses sklearn randomized_svd (O(m·n·k)) when available; falls back to
    numpy full SVD otherwise.

    Reused from v14 (unchanged).
    """
    k = min(k, min(M.shape) - 1)
    if k < 1:
        k = 1
    if _HAS_SKLEARN and _rsvd is not None:
        U, S, Vt = _rsvd(M, n_components=k, n_iter=4, random_state=42)
    else:
        U, S, Vt = np.linalg.svd(M, full_matrices=False)
        U, S, Vt = U[:, :k], S[:k], Vt[:k, :]
    return (
        U.astype(np.float32),
        S.astype(np.float32),
        Vt.astype(np.float32),
    )


# ══════════════════════════════════════════════════════════════════════
# § 4  360° tomographic sign voting  (reused from v14/extract_qwen36.py)
# ══════════════════════════════════════════════════════════════════════


def _random_orthogonal(n: int, rng: np.random.RandomState) -> np.ndarray:
    """Generate a random orthogonal matrix via QR decomposition.

    Returns (n, n) float32 orthogonal matrix with det = ±1 (Haar measure).

    Reused from v14 (unchanged).
    """
    H = rng.randn(n, n).astype(np.float32)
    Q, R = np.linalg.qr(H)
    Q *= np.sign(np.diag(R))
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
         b. Project W into student dims: Wp = P_out @ W @ P_in.T
         c. Accumulate sign votes: votes += sign(Wp)
      3. Final result: sign(votes), shape (d_out, d_in).
      4. Fill zeros (tied votes) with random ±1.

    Same-dimension case (no projection needed):
      In-place rotation: W_rot = W @ R_in, accumulate sign votes.

    Reused from v14 (unchanged).

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
            P_out = U_base[:, :k_out].T          # (k_out, n_out)
            P_in = Vt_base[:k_in, :]             # (k_in, n_in)
        else:
            R_out = _random_orthogonal(k_out, rng)
            R_in  = _random_orthogonal(k_in, rng)
            P_out = R_out @ U_base[:, :k_out].T  # (k_out, n_out)
            P_in  = R_in  @ Vt_base[:k_in, :]   # (k_in, n_in)

        Wp = P_out @ W @ P_in.T                  # (k_out, k_in)

        angle_signs = np.zeros((d_out, d_in), dtype=np.float32)
        angle_signs[:k_out, :k_in] = np.sign(Wp)
        votes += angle_signs

    result = np.sign(votes).astype(np.int8)
    zeros = result == 0
    if zeros.any():
        result[zeros] = rng.choice([-1, 1], size=int(zeros.sum())).astype(np.int8)
    return result


# ══════════════════════════════════════════════════════════════════════
# § 5  Ternary packing  (reused from v14/extract_qwen36.py)
# ══════════════════════════════════════════════════════════════════════


def pack_ternary_np(w_int8: np.ndarray) -> np.ndarray:
    """Pack int8 {-1, 0, +1} array [N, K] → uint32 [N, K // 16].

    Encoding: {-1 → 0b00, 0 → 0b01, +1 → 0b10}
    16 values packed per uint32 word (value i in bits [2i : 2i+2]).

    K must be divisible by 16.

    Reused from v14 (unchanged).
    """
    assert w_int8.ndim == 2, f"Expected 2D array, got shape {w_int8.shape}"
    assert w_int8.shape[1] % 16 == 0, (
        f"K ({w_int8.shape[1]}) must be divisible by 16 for uint32 packing"
    )
    N, K = w_int8.shape
    mapped = (w_int8.astype(np.int32) + 1).astype(np.uint32)
    packed = np.zeros((N, K // 16), dtype=np.uint32)
    for i in range(16):
        packed |= mapped[:, i::16] << (i * 2)
    return packed


def pack_ternary_uint8_np(w_int8: np.ndarray) -> np.ndarray:
    """Pack int8 {-1, 0, +1} array [N, K] → uint8 [N, K // 4].

    Encoding: {-1 → 0b00, 0 → 0b01, +1 → 0b10}
    4 values per byte in bit positions {7:6, 5:4, 3:2, 1:0}.
    K must be divisible by 4.

    Used for TernaryEmbedding format. Reused from v14 (unchanged).
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
# § 6  Global projection basis  (reused from v14/extract_qwen36.py)
# ══════════════════════════════════════════════════════════════════════


def compute_global_projection(
    model_path: Path,
    d_model: int,
    teacher_d_model: int,
) -> np.ndarray:
    """Compute shared column projection basis from teacher embeddings.

    Loads E (vocab, teacher_d_model), computes truncated SVD to rank d_model,
    and returns V_proj (teacher_d_model, d_model) — the top-d_model right
    singular vectors. This shared column basis is used for all subsequent
    projections of teacher weights into student-dimensional space.

    Reused from v14 (signature simplified: cfg removed, not needed for v15).

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
# § 7  Embedding plate extraction  (reused from v14/extract_qwen36.py)
# ══════════════════════════════════════════════════════════════════════


def extract_embeddings(
    model_path: Path,
    V_proj: np.ndarray,
    d_model: int,
    vocab_size: int,
) -> np.ndarray:
    """Extract ternary embedding plate from teacher.

    E_teacher (vocab, teacher_d_model) @ V_proj (teacher_d_model, d_model)
        → E_proj (vocab, d_model) → sign() → int8 {-1, +1}.

    Projected in 32 chunks to avoid peak-memory explosion at fp32.

    Reused from v14 (signature adapted: cfg → d_model, vocab_size).

    Returns:
        int8 array (vocab_size, d_model) with values in {-1, +1}.
    """
    t0 = time.time()
    embed_name = f"{TEACHER_PREFIX}.embed_tokens.weight"
    log(f"  Loading embeddings for sign extraction ...")
    E = load_tensor(model_path, embed_name)  # (vocab, teacher_d_model)
    log(f"  Projecting: {E.shape} @ {V_proj.shape} ...")

    vocab = E.shape[0]
    chunk = max(1, vocab // 32)
    E_proj = np.zeros((vocab, d_model), dtype=np.float32)
    for start in range(0, vocab, chunk):
        end = min(start + chunk, vocab)
        E_proj[start:end] = E[start:end] @ V_proj
    del E
    log(f"  E_proj range: [{E_proj.min():.4f}, {E_proj.max():.4f}]")

    signs = np.sign(E_proj).astype(np.int8)
    del E_proj
    zeros = signs == 0
    if zeros.any():
        rng = np.random.RandomState(7)
        signs[zeros] = rng.choice([-1, 1], size=int(zeros.sum())).astype(np.int8)

    log(f"  Embedding signs: {signs.shape}  ({time.time() - t0:.1f}s)")
    return signs


# ══════════════════════════════════════════════════════════════════════
# § 8  Full-attention plate extraction  (reused from v14/extract_qwen36.py)
# ══════════════════════════════════════════════════════════════════════


def extract_ssa_plates(
    model_path: Path,
    teacher_layer: int,
    d_model: int,
    n_rotations: int,
) -> dict[str, np.ndarray]:
    """Extract Q/K/V/O sign plates from a teacher full-attention (SSA) layer.

    Teacher SSA shapes (Qwen3.6-27B):
      q_proj.weight: (12288, 5120) = (96 heads × 128, d_model)
      k_proj.weight: (1024,  5120) = (8  heads × 128, d_model)
      v_proj.weight: (1024,  5120) = (8  heads × 128, d_model)
      o_proj.weight: (5120, 12288) = (d_model, 96 heads × 128)

    Student target: (d_model, d_model) for all four projections.

    Reused from v14 (signature adapted: cfg → d_model).

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
        log(f"      SSA L{teacher_layer} {proj_name}: {W.shape}")
        plates[key] = extract_sign_pattern(
            W, d_out=d_model, d_in=d_model, n_rotations=n_rotations
        )
        del W
    return plates


# ══════════════════════════════════════════════════════════════════════
# § 9  Linear-attention plate extraction  (reused from v14/extract_qwen36.py)
# ══════════════════════════════════════════════════════════════════════


def extract_gla_plates(
    model_path: Path,
    teacher_layer: int,
    d_model: int,
    n_rotations: int,
) -> dict[str, np.ndarray]:
    """Extract Q/K/V/O sign plates from a teacher linear-attention (GLA) layer.

    Teacher GLA shapes (Qwen3.6-27B):
      linear_attn.in_proj_qkv.weight: (10240, 5120) — Q+K+V concatenated
        Q: rows [0    : 2048]  = 16 heads × 128
        K: rows [2048 : 4096]  = 16 heads × 128
        V: rows [4096 : 10240] = 48 heads × 128
      linear_attn.out_proj.weight:    (5120, 6144)  — (d_model, 48×128)

    Student target: (d_model, d_model) for all four projections.

    Reused from v14 (signature adapted: cfg → d_model).

    Returns:
        Dict with keys "q", "k", "v", "o" → int8 (d_model, d_model).
    """
    prefix = f"{TEACHER_PREFIX}.layers.{teacher_layer}.linear_attn"
    plates: dict[str, np.ndarray] = {}

    # ── in_proj_qkv: split into Q, K, V ────────────────────────────────
    qkv_name = f"{prefix}.in_proj_qkv.weight"
    W_qkv = load_tensor(model_path, qkv_name)  # (10240, 5120)
    log(f"      GLA L{teacher_layer} in_proj_qkv: {W_qkv.shape}")
    assert W_qkv.shape[0] == TEACHER_GLA_Q_ROWS + TEACHER_GLA_K_ROWS + TEACHER_GLA_V_ROWS, (
        f"Unexpected in_proj_qkv rows: {W_qkv.shape[0]}"
    )
    q_end = TEACHER_GLA_Q_ROWS
    k_end = TEACHER_GLA_Q_ROWS + TEACHER_GLA_K_ROWS

    for slice_, key, label in [
        (W_qkv[:q_end, :],    "q", "Q"),
        (W_qkv[q_end:k_end, :], "k", "K"),
        (W_qkv[k_end:, :],    "v", "V"),
    ]:
        log(f"      GLA L{teacher_layer} {label}: {slice_.shape}")
        plates[key] = extract_sign_pattern(
            slice_, d_out=d_model, d_in=d_model, n_rotations=n_rotations
        )
    del W_qkv

    # ── out_proj: (5120, 6144) → student (d_model, d_model) ───────────
    out_name = f"{prefix}.out_proj.weight"
    W_out = load_tensor(model_path, out_name)
    log(f"      GLA L{teacher_layer} out_proj: {W_out.shape}")
    plates["o"] = extract_sign_pattern(
        W_out, d_out=d_model, d_in=d_model, n_rotations=n_rotations
    )
    del W_out

    return plates


# ══════════════════════════════════════════════════════════════════════
# § 10  2-plate decomposition  (NEW in v15)
# ══════════════════════════════════════════════════════════════════════


def extract_2plate_from_votes(
    votes: np.ndarray,
    magnitude_sum: np.ndarray,
    n_teacher_layers: int,
    seed: int = 0,
    zero_frac: float = 0.30,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Derive 2-plate decomposition from accumulated vote and magnitude arrays.

    This is the core v15 novelty. Rather than reducing teacher information to
    a single ternary plate, we extract two plates that together recover more
    dynamic range:

      plate1 captures the sign topology (program structure) — the dominant
      directional consensus across teacher layers.

      plate2 captures the magnitude mirror — the residual left after the
      plate1 reconstruction, representing fine-grained magnitude variation
      that a single ternary plate discards.

    The 2-plate approximation of W_avg is:
        W_avg ≈ plate1 * gamma1[:, None] + plate2 * gamma2[:, None]

    Structural zeros (session 177):
      Positions where teacher layers agreed on near-zero magnitude are
      irreducible fixed points — GD deposited near-zero weights because
      there's nothing left to reduce. These become structural zeros in
      both plates (plate1=0, plate2=0). The bottom `zero_frac` of
      positions by average magnitude PER ROW are zeroed. Gammas are
      recomputed over non-zero positions only.

      These zeros are distinct from the gate's runtime kill (89% per token).
      Static zeros = "this position NEVER computes" (structural).
      Gate kill = "this position doesn't compute for THIS token" (dynamic).
      Combined: ~3% of neurons active per position per token.

    Algorithm:
      1. W_avg = magnitude_sum / n_teacher_layers * sign(votes)
      2. Per-row magnitude threshold: bottom zero_frac → structural zero
      3. gamma1 = per-row RMS of W_avg (non-zero positions only)
      4. plate1 = sign(votes), zeros where magnitude below threshold
      5. residual = W_avg - plate1 * gamma1[:, None]
      6. gamma2 = per-row RMS of residual (non-zero positions only)
      7. plate2 = sign(residual), zeros where plate1 is zero

    NEW in v15 — no equivalent in v14.

    Args:
        votes:            float32 (d_out, d_in) — accumulated sign votes.
        magnitude_sum:    float32 (d_out, d_in) — accumulated |W| per element.
        n_teacher_layers: Number of teacher layers that contributed to votes.
        seed:             Random seed for zero-tie breaking.
        zero_frac:        Fraction of positions to zero per row (default 0.30).
                          Set to 0.0 to disable zero placement.

    Returns:
        plate1: int8  (d_out, d_in)   — sign topology (with structural zeros)
        plate2: int8  (d_out, d_in)   — magnitude mirror (zeros match plate1)
        gamma1: float32 (d_out,)      — per-row RMS scale for plate1
        gamma2: float32 (d_out,)      — per-row RMS scale for plate2
    """
    rng = np.random.RandomState(seed)
    n = max(1, n_teacher_layers)

    # ── Average magnitude per position (teacher consensus) ──────────────
    avg_magnitude = magnitude_sum / n                      # (d_out, d_in)

    # ── Structural zero mask: bottom zero_frac per row ──────────────────
    # Positions where teacher layers agreed on near-zero magnitude =
    # irreducible fixed points. Nothing computes here.
    if zero_frac > 0.0:
        d_out, d_in = avg_magnitude.shape
        # Per-row threshold: zero the bottom zero_frac positions by magnitude.
        # np.partition puts the k smallest values in positions 0..k-1.
        # Threshold at position k with strict < gives exactly k zeros per row.
        k = max(1, int(d_in * zero_frac))
        k = min(k, d_in - 1)  # leave at least 1 non-zero per row
        thresholds = np.partition(avg_magnitude, k, axis=1)[:, k]  # (d_out,)
        zero_mask = avg_magnitude < thresholds[:, None]  # (d_out, d_in)
    else:
        zero_mask = np.zeros_like(avg_magnitude, dtype=bool)

    # ── Plate 1: sign topology from majority vote ───────────────────────
    plate1 = np.sign(votes).astype(np.int8)
    # Resolve vote ties (zero votes) with random ±1
    vote_ties = plate1 == 0
    if vote_ties.any():
        plate1[vote_ties] = rng.choice(
            [-1, 1], size=int(vote_ties.sum())
        ).astype(np.int8)
    # Apply structural zeros
    plate1[zero_mask] = 0

    # ── W_avg and gamma1 (over non-zero positions only) ─────────────────
    W_avg = plate1.astype(np.float32) * avg_magnitude      # (d_out, d_in)
    # Per-row RMS over non-zero positions
    nonzero_count = np.sum(~zero_mask, axis=1, keepdims=True).astype(np.float32)
    nonzero_count = np.maximum(nonzero_count, 1.0)  # avoid div-by-zero
    gamma1 = np.sqrt(
        np.sum(W_avg ** 2 * (~zero_mask), axis=1) / nonzero_count.ravel()
    ).astype(np.float32)

    # ── Plate 2: magnitude mirror — residual after plate1 ──────────────
    reconstructed1 = plate1.astype(np.float32) * gamma1[:, None]
    residual = W_avg - reconstructed1

    gamma2 = np.sqrt(
        np.sum(residual ** 2 * (~zero_mask), axis=1) / nonzero_count.ravel()
    ).astype(np.float32)

    plate2 = np.sign(residual).astype(np.int8)
    # Resolve ties in residual sign
    res_ties = (plate2 == 0) & (~zero_mask)
    if res_ties.any():
        plate2[res_ties] = rng.choice(
            [-1, 1], size=int(res_ties.sum())
        ).astype(np.int8)
    # Plate2 zeros match plate1 zeros (structural absence)
    plate2[zero_mask] = 0

    return plate1, plate2, gamma1, gamma2


def extract_1plate_from_votes(
    votes: np.ndarray,
    magnitude_sum: np.ndarray,
    n_teacher_layers: int,
    seed: int = 0,
    zero_frac: float = 0.30,
) -> tuple[np.ndarray, np.ndarray]:
    """Derive 1-plate decomposition from accumulated votes.

    Simplified extraction for CLASSIFY strides that only need plate1.
    Same structural zero placement as 2-plate (bottom zero_frac per row).

    Algorithm:
      1. plate1 = sign(votes) with zero-tie breaking.
      2. Apply structural zeros: bottom zero_frac by magnitude per row.
      3. gamma1 = per-row RMS of the average signed weight (non-zero only).

    NEW in v15 — v14's zone voting produced only plates, not gammas.

    Args:
        votes:            float32 (d_out, d_in) — accumulated sign votes.
        magnitude_sum:    float32 (d_out, d_in) — accumulated |W| per element.
        n_teacher_layers: Number of teacher layers that contributed.
        seed:             Random seed for zero-tie breaking.
        zero_frac:        Fraction of positions to zero per row (default 0.30).

    Returns:
        plate1: int8    (d_out, d_in) — with structural zeros
        gamma1: float32 (d_out,)
    """
    rng = np.random.RandomState(seed)
    n = max(1, n_teacher_layers)

    avg_magnitude = magnitude_sum / n

    # ── Structural zero mask ────────────────────────────────────────────
    if zero_frac > 0.0:
        d_out, d_in = avg_magnitude.shape
        k = max(1, int(d_in * zero_frac))
        k = min(k, d_in - 1)
        thresholds = np.partition(avg_magnitude, k, axis=1)[:, k]
        zero_mask = avg_magnitude < thresholds[:, None]
    else:
        zero_mask = np.zeros_like(avg_magnitude, dtype=bool)

    plate1 = np.sign(votes).astype(np.int8)
    vote_ties = plate1 == 0
    if vote_ties.any():
        plate1[vote_ties] = rng.choice(
            [-1, 1], size=int(vote_ties.sum())
        ).astype(np.int8)
    plate1[zero_mask] = 0

    W_avg = plate1.astype(np.float32) * avg_magnitude
    nonzero_count = np.maximum(np.sum(~zero_mask, axis=1).astype(np.float32), 1.0)
    gamma1 = np.sqrt(
        np.sum(W_avg ** 2 * (~zero_mask), axis=1) / nonzero_count
    ).astype(np.float32)

    return plate1, gamma1


# ══════════════════════════════════════════════════════════════════════
# § 11  Per-stride FFN extraction  (NEW in v15)
# ══════════════════════════════════════════════════════════════════════


def extract_stride_ffn_plates(
    model_path: Path,
    stride_index: int,
    teacher_layers: tuple[int, ...],
    n_plates: int,
    cfg: V15Config,
    n_rotations: int,
    V_proj: np.ndarray,
    zero_frac: float = 0.30,
) -> dict[str, np.ndarray]:
    """Extract FFN plates for one v15 stride, voting across teacher layers.

    For each teacher layer mapped to this stride:
      1. Load gate_proj, up_proj, down_proj.
      2. Project into student dimensions via extract_sign_pattern.
      3. Accumulate sign votes and absolute magnitude sums.

    Then derive plates from accumulated votes:
      n_plates == 1 → plate1 + gamma1              (CLASSIFY strides)
      n_plates == 2 → plate1 + plate2 + gamma1 + gamma2  (COMPUTE/LINK/EMIT)

    Teacher FFN shapes (Qwen3.6-27B, SwiGLU):
      gate_proj.weight: (17408, 5120) → student (d_ff, d_model) = (5120, 1280)
      up_proj.weight:   (17408, 5120) → student (d_ff, d_model) = (5120, 1280)
      down_proj.weight: (5120, 17408) → student (d_model, d_ff) = (1280, 5120)

    Note: V_proj is accepted for API consistency but FFN weight projection
    uses the tomographic sign voting directly — column basis is embedded
    in the SVD rotations, not applied explicitly.

    NEW in v15 (v14 used a zone-level vote over 3 fixed representative layers).

    Args:
        model_path:     Path to teacher model directory.
        stride_index:   Student stride index (0-18) for logging.
        teacher_layers: Teacher layer indices to vote across.
        n_plates:       1 for CLASSIFY, 2 for all other zones.
        cfg:            V15Config instance.
        n_rotations:    Tomographic viewing angles.
        V_proj:         Global projection basis (unused here, kept for symmetry).

    Returns:
        Dict with arrays keyed by "gate_plate1", "gate_gamma1",
        "gate_plate2" (if n_plates==2), "gate_gamma2" (if n_plates==2),
        and similarly for "up_*" and "down_*".
    """
    d_ff = cfg.d_ff
    d_model = cfg.d_model
    n = len(teacher_layers)

    log(f"  stride {stride_index:02d} FFN: {n_plates}-plate, "
        f"teacher layers {teacher_layers}")

    # Accumulate votes and magnitude sums for each FFN matrix type.
    # gate and up: (d_ff, d_model); down: (d_model, d_ff)
    accum = {
        "gate": {
            "votes": np.zeros((d_ff, d_model), dtype=np.float32),
            "mag":   np.zeros((d_ff, d_model), dtype=np.float32),
            "d_out": d_ff, "d_in": d_model,
        },
        "up": {
            "votes": np.zeros((d_ff, d_model), dtype=np.float32),
            "mag":   np.zeros((d_ff, d_model), dtype=np.float32),
            "d_out": d_ff, "d_in": d_model,
        },
        "down": {
            "votes": np.zeros((d_model, d_ff), dtype=np.float32),
            "mag":   np.zeros((d_model, d_ff), dtype=np.float32),
            "d_out": d_model, "d_in": d_ff,
        },
    }

    for teacher_layer in teacher_layers:
        layer_prefix = f"{TEACHER_PREFIX}.layers.{teacher_layer}.mlp"
        t_layer = time.time()

        for name, proj_suffix in [
            ("gate", "gate_proj"),
            ("up",   "up_proj"),
            ("down", "down_proj"),
        ]:
            tensor_name = f"{layer_prefix}.{proj_suffix}.weight"
            W = load_tensor(model_path, tensor_name)
            log(f"    L{teacher_layer} {proj_suffix}: {W.shape}")

            a = accum[name]
            signs_raw = extract_sign_pattern(
                W,
                d_out=a["d_out"],
                d_in=a["d_in"],
                n_rotations=n_rotations,
            ).astype(np.float32)

            a["votes"] += signs_raw

            # Accumulate absolute magnitude via projection onto sign basis.
            # We compute a per-element magnitude estimate: project W to
            # student dims, take absolute value, accumulate.
            # (Reuses the sign pattern infrastructure; magnitude is the
            #  absolute value of the projected weights before sign().)
            #
            # For large matrices the sign pattern function already projects
            # W. We need the pre-sign float values too — re-project directly.
            d_out, d_in = a["d_out"], a["d_in"]
            n_out, n_in = W.shape
            if n_out == d_out and n_in == d_in:
                a["mag"] += np.abs(W)
            else:
                # Use top-1 SVD projection to get a representative magnitude.
                k = min(max(d_out, d_in), min(n_out, n_in) - 1)
                U_b, _S, Vt_b = truncated_svd(W, k)
                k_out = min(d_out, U_b.shape[1])
                k_in = min(d_in, Vt_b.shape[0])
                W_proj = np.zeros((d_out, d_in), dtype=np.float32)
                W_proj[:k_out, :k_in] = (
                    U_b[:, :k_out].T @ W @ Vt_b[:k_in, :].T
                )
                a["mag"] += np.abs(W_proj)
                del U_b, Vt_b, W_proj
            del W, signs_raw

        log(f"    L{teacher_layer} done in {time.time() - t_layer:.1f}s")

    # ── Derive plates from accumulated votes ──────────────────────────────
    results: dict[str, np.ndarray] = {}
    zeros_masks: dict[str, np.ndarray] = {}

    for name, a in accum.items():
        seed_base = {"gate": 100, "up": 200, "down": 300}[name]

        if n_plates == 2:
            p1, p2, g1, g2 = extract_2plate_from_votes(
                a["votes"], a["mag"], n, seed=seed_base,
                zero_frac=zero_frac,
            )
            results[f"{name}_plate1"] = p1
            results[f"{name}_plate2"] = p2
            results[f"{name}_gamma1"] = g1
            results[f"{name}_gamma2"] = g2
        else:
            p1, g1 = extract_1plate_from_votes(
                a["votes"], a["mag"], n, seed=seed_base,
                zero_frac=zero_frac,
            )
            results[f"{name}_plate1"] = p1
            results[f"{name}_gamma1"] = g1

        # Record structural zero fraction + vote-tie mask
        structural_zeros = (results[f"{name}_plate1"] == 0).mean()
        vote_ties = (a["votes"] == 0).mean()
        zeros_masks[f"{name}_zeros_mask"] = (results[f"{name}_plate1"] == 0).astype(np.uint8)

        # Save average magnitude for future analysis / re-zeroing
        results[f"{name}_avg_magnitude"] = (a["mag"] / max(1, n)).astype(np.float32)

        log(f"    {name}: structural zeros = {structural_zeros:.4f} "
            f"(vote-tie fraction = {vote_ties:.4f})")

    results.update(zeros_masks)
    return results


# ══════════════════════════════════════════════════════════════════════
# § 12  Per-stride attention extraction  (NEW in v15)
# ══════════════════════════════════════════════════════════════════════


def extract_stride_attn_plates(
    model_path: Path,
    stride_index: int,
    teacher_layers: tuple[int, ...],
    cfg: V15Config,
    n_rotations: int,
) -> dict[str, np.ndarray]:
    """Extract attention Q/K/V/O plates for one FULL-attention stride.

    Called only for COMPUTE (strides 5-12) and LINK (strides 13-15) strides.
    LINEAR strides (CLASSIFY, EMIT) skip attention extraction — those
    attention weights will be trained from scratch.

    For each teacher layer mapped to this stride:
      1. Determine if teacher layer is GLA (linear_attn) or SSA (full_attn).
      2. Extract Q/K/V/O sign plates via the appropriate extraction function.
      3. Accumulate sign votes across all mapped teacher layers.
    4. Final plate = sign(majority vote), zeros → random ±1.

    Teacher layer type follows the [L,L,L,F]×16 pattern; we extract attention
    from whatever type of layer is mapped, projecting to student dimensions
    either way (sign topology is architecture-independent, r=0.998).

    NOTE: Unlike FFN extraction, attention plates are NOT gamma-scaled (no
    2-plate format for attention in v15). Attention is the router; the
    crystal basis is the program. Attention weights will be fine-tuned.

    NEW in v15 (v14 also extracted attention but used a fixed stride↔layer
    mapping rather than the config-driven per-stride teacher_layers).

    Args:
        model_path:     Path to teacher model directory.
        stride_index:   Student stride index for logging.
        teacher_layers: Teacher layer indices to vote across.
        cfg:            V15Config instance.
        n_rotations:    Tomographic viewing angles.

    Returns:
        Dict with keys "q", "k", "v", "o" → int8 (d_model, d_model).
    """
    d_model = cfg.d_model
    n = len(teacher_layers)
    log(f"  stride {stride_index:02d} ATTN: voting across {n} teacher layers {teacher_layers}")

    votes: dict[str, np.ndarray] = {
        proj: np.zeros((d_model, d_model), dtype=np.float32)
        for proj in ("q", "k", "v", "o")
    }

    for teacher_layer in teacher_layers:
        t_layer_type = teacher_layer_type(teacher_layer)
        log(f"    L{teacher_layer} ({t_layer_type})")

        if t_layer_type == "full_attn":
            plates = extract_ssa_plates(
                model_path, teacher_layer, d_model, n_rotations
            )
        else:
            plates = extract_gla_plates(
                model_path, teacher_layer, d_model, n_rotations
            )

        for proj in ("q", "k", "v", "o"):
            votes[proj] += plates[proj].astype(np.float32)

    # Resolve votes → final plates
    rng = np.random.RandomState(stride_index * 13 + 7)
    final: dict[str, np.ndarray] = {}
    for proj, v in votes.items():
        plate = np.sign(v).astype(np.int8)
        zeros = plate == 0
        if zeros.any():
            plate[zeros] = rng.choice(
                [-1, 1], size=int(zeros.sum())
            ).astype(np.int8)
        final[proj] = plate

    return final


# ══════════════════════════════════════════════════════════════════════
# § 13  Checkpoint verification  (NEW in v15)
# ══════════════════════════════════════════════════════════════════════


def verify_checkpoint(output_dir: Path, cfg: V15Config) -> bool:
    """Verify the v15 checkpoint directory structure and key shapes.

    Checks:
      • config.json exists and d_model matches.
      • v_proj.npy has shape (teacher_d_model, d_model).
      • embedding.npz has "embedding" key with shape (vocab, d_model // 4).
      • strides/stride_XX.npz files exist for all 19 strides.
      • Each stride NPZ has correctly shaped plate1 / gamma1 arrays.
      • attention/stride_XX.npz files exist for all FULL-attention strides.

    Args:
        output_dir: Root checkpoint directory.
        cfg:        V15Config used during extraction.

    Returns:
        True if all checks pass, False otherwise.
    """
    log(f"\n── Verification ──────────────────────────────────────────────────")
    errors: list[str] = []

    def check(condition: bool, msg: str) -> None:
        if not condition:
            log(f"  [✗] {msg}")
            errors.append(msg)
        else:
            log(f"  [✓] {msg}")

    # config.json
    cfg_path = output_dir / "config.json"
    check(cfg_path.exists(), "config.json exists")
    if cfg_path.exists():
        with open(cfg_path) as f:
            saved_cfg = json.load(f)
        check(
            saved_cfg.get("d_model") == cfg.d_model,
            f"config.json d_model == {cfg.d_model}"
        )

    # v_proj.npy: (teacher_d_model, d_model)
    vproj_path = output_dir / "v_proj.npy"
    check(vproj_path.exists(), "v_proj.npy exists")
    if vproj_path.exists():
        vp = np.load(str(vproj_path))
        check(
            vp.shape == (TEACHER_D_MODEL, cfg.d_model),
            f"v_proj.npy shape == ({TEACHER_D_MODEL}, {cfg.d_model}), got {vp.shape}"
        )

    # embedding.npz
    emb_path = output_dir / "embedding.npz"
    check(emb_path.exists(), "embedding.npz exists")
    if emb_path.exists():
        emb = np.load(str(emb_path))
        check(
            "embedding" in emb.files,
            "embedding.npz has 'embedding' key"
        )
        if "embedding" in emb.files:
            expected_emb_shape = (cfg.vocab_size, cfg.d_model // 4)
            check(
                emb["embedding"].shape == expected_emb_shape,
                f"embedding shape == {expected_emb_shape}, "
                f"got {emb['embedding'].shape}"
            )

    # Stride NPZs
    strides_dir = output_dir / "strides"
    attn_dir = output_dir / "attention"
    specs = cfg.stride_specs()

    for spec in specs:
        s = spec.index
        npz_path = strides_dir / f"stride_{s:02d}.npz"
        check(npz_path.exists(), f"strides/stride_{s:02d}.npz exists")

        if npz_path.exists():
            data = np.load(str(npz_path))
            for prefix in ("gate", "up", "down"):
                d_out = cfg.d_ff if prefix != "down" else cfg.d_model
                d_in  = cfg.d_model if prefix != "down" else cfg.d_ff

                p1_key = f"{prefix}_plate1"
                g1_key = f"{prefix}_gamma1"
                check(
                    p1_key in data.files and data[p1_key].shape == (d_out, d_in),
                    f"stride_{s:02d} {p1_key}: ({d_out}, {d_in})"
                )
                check(
                    g1_key in data.files and data[g1_key].shape == (d_out,),
                    f"stride_{s:02d} {g1_key}: ({d_out},)"
                )
                if spec.n_plates == 2:
                    p2_key = f"{prefix}_plate2"
                    g2_key = f"{prefix}_gamma2"
                    check(
                        p2_key in data.files and data[p2_key].shape == (d_out, d_in),
                        f"stride_{s:02d} {p2_key}: ({d_out}, {d_in})"
                    )
                    check(
                        g2_key in data.files and data[g2_key].shape == (d_out,),
                        f"stride_{s:02d} {g2_key}: ({d_out},)"
                    )
            data.close()

    # Attention NPZs — only for FULL attention strides
    full_strides = [
        spec for spec in specs if spec.attn_type == AttnType.FULL
    ]
    for spec in full_strides:
        s = spec.index
        attn_path = attn_dir / f"stride_{s:02d}.npz"
        check(attn_path.exists(), f"attention/stride_{s:02d}.npz exists")

        if attn_path.exists():
            data = np.load(str(attn_path))
            for proj in ("q", "k", "v", "o"):
                expected = (cfg.d_model, cfg.d_model)
                check(
                    proj in data.files and data[proj].shape == expected,
                    f"attention/stride_{s:02d} {proj}: {expected}"
                )
            data.close()

    if errors:
        log(f"\n  VERIFICATION FAILED — {len(errors)} issue(s):")
        for e in errors:
            log(f"    • {e}")
        return False

    log(f"\n  All checks passed ✓")
    return True


# ══════════════════════════════════════════════════════════════════════
# § 14  Main extraction pipeline  (NEW in v15)
# ══════════════════════════════════════════════════════════════════════


def run_extraction(
    model_path: Path,
    output_dir: Path,
    n_rotations: int = 8,
    skip_embeddings: bool = False,
    skip_ffn: bool = False,
    skip_attention: bool = False,
    cfg: V15Config | None = None,
    zero_frac: float = 0.30,
) -> None:
    """Full v15 extraction pipeline: Qwen3.6-27B → crystal-native statechart.

    Stages:
      1. Global V_proj from embedding SVD → saved as v_proj.npy.
      2. Embedding signs → packed uint8 → saved as embedding.npz.
      3. For each of 19 strides: FFN plates (1- or 2-plate) → strides/stride_XX.npz.
      4. For each FULL-attention stride: attention Q/K/V/O → attention/stride_XX.npz.
      5. Save config.json and state.json.
      6. Verify checkpoint.

    Memory discipline: one teacher layer at a time. 27B weights are large;
    we load, project, accumulate, then delete before moving to the next layer.

    NEW in v15 — completely rewritten from v14's run_extraction.

    Args:
        model_path:       Path to teacher model directory.
        output_dir:       Root output directory for the checkpoint.
        n_rotations:      Tomographic viewing angles (default: 8).
        skip_embeddings:  Skip embedding extraction (resume-friendly).
        skip_ffn:         Skip FFN stride extraction.
        skip_attention:   Skip attention plate extraction.
        cfg:              V15Config (uses defaults if None).
    """
    t_total = time.time()
    if cfg is None:
        cfg = V15Config()

    # ── Create output directory tree ──────────────────────────────────────
    strides_dir = output_dir / "strides"
    attn_dir    = output_dir / "attention"
    for d in (output_dir, strides_dir, attn_dir):
        d.mkdir(parents=True, exist_ok=True)

    specs = cfg.stride_specs()

    log("=" * 72)
    log("  V15 Extraction — Qwen3.6-27B → Crystal-Native Tensor Statechart")
    log("=" * 72)
    log(f"  Teacher path:    {model_path}")
    log(f"  Output dir:      {output_dir}")
    log(f"  d_model:         {cfg.d_model}")
    log(f"  d_ff:            {cfg.d_ff}")
    log(f"  n_strides:       {cfg.n_strides}  (5 CLASSIFY + 8 COMPUTE + 3 LINK + 3 EMIT)")
    log(f"  n_rotations:     {n_rotations}")
    log(f"  sklearn SVD:     {_HAS_SKLEARN}")
    log(f"  skip_embeddings: {skip_embeddings}")
    log(f"  skip_ffn:        {skip_ffn}")
    log(f"  skip_attention:  {skip_attention}")
    log("")

    # Print stride table for orientation
    log("  Stride map:")
    for spec in specs:
        from config import ZONE_NAMES
        z = ZONE_NAMES[spec.zone]
        a = spec.attn_type.name
        log(f"    stride {spec.index:02d}  {z:<9}  {a:<7}  "
            f"{spec.n_plates}-plate  "
            f"teacher layers {spec.teacher_layers}")
    log("")

    # ── Stage 1: Global projection basis ─────────────────────────────────
    log("── Stage 1: Global projection basis (embedding SVD) ────────────")
    V_proj = compute_global_projection(
        model_path, cfg.d_model, TEACHER_D_MODEL
    )  # (teacher_d_model, d_model)

    vproj_path = output_dir / "v_proj.npy"
    np.save(str(vproj_path), V_proj)
    log(f"  Saved v_proj.npy: {vproj_path.stat().st_size / 1024:.1f} KB")

    # ── Stage 2: Embedding plate ──────────────────────────────────────────
    if not skip_embeddings:
        log("\n── Stage 2: Embedding plate ────────────────────────────────────")
        t_emb = time.time()
        emb_signs = extract_embeddings(
            model_path, V_proj, cfg.d_model, cfg.vocab_size
        )  # (vocab, d_model) int8
        emb_packed = pack_ternary_uint8_np(emb_signs)
        # (vocab, d_model // 4) uint8 — TernaryEmbedding format
        np.savez_compressed(
            str(output_dir / "embedding.npz"), embedding=emb_packed
        )
        log(f"  Saved embedding.npz: "
            f"{(output_dir / 'embedding.npz').stat().st_size / 1024 / 1024:.1f} MB  "
            f"({time.time() - t_emb:.1f}s)")
        del emb_signs, emb_packed
    else:
        log("\n── Stage 2: Embedding plate [SKIPPED] ──────────────────────────")

    # ── Stage 3: FFN stride plates ────────────────────────────────────────
    if not skip_ffn:
        log("\n── Stage 3: FFN stride plates (per-stride, 1- or 2-plate) ─────")
        t_ffn_total = time.time()

        for spec in specs:
            s = spec.index
            from config import ZONE_NAMES
            z = ZONE_NAMES[spec.zone]
            t_stride = time.time()

            log(f"\n  [stride {s:02d} / {z}]  "
                f"n_plates={spec.n_plates}  "
                f"teacher={spec.teacher_layers}")

            stride_data = extract_stride_ffn_plates(
                model_path=model_path,
                stride_index=s,
                teacher_layers=spec.teacher_layers,
                n_plates=spec.n_plates,
                cfg=cfg,
                n_rotations=n_rotations,
                V_proj=V_proj,
                zero_frac=zero_frac,
            )

            stride_path = strides_dir / f"stride_{s:02d}.npz"
            np.savez_compressed(str(stride_path), **stride_data)
            sz = stride_path.stat().st_size / 1024 / 1024
            elapsed = time.time() - t_stride
            log(f"  → stride_{s:02d}.npz  {sz:.1f} MB  ({elapsed:.1f}s)")

        log(f"\n  FFN total: {time.time() - t_ffn_total:.1f}s")
    else:
        log("\n── Stage 3: FFN stride plates [SKIPPED] ────────────────────────")

    # ── Stage 4: Attention plates (FULL attention strides only) ──────────
    if not skip_attention:
        log("\n── Stage 4: Attention plates (COMPUTE + LINK strides) ──────────")
        t_attn_total = time.time()

        full_strides = [s for s in specs if s.attn_type == AttnType.FULL]
        log(f"  FULL attention strides: "
            f"{[s.index for s in full_strides]}")

        for spec in full_strides:
            s = spec.index
            from config import ZONE_NAMES
            z = ZONE_NAMES[spec.zone]
            t_stride = time.time()

            log(f"\n  [stride {s:02d} / {z}]  teacher={spec.teacher_layers}")

            attn_data = extract_stride_attn_plates(
                model_path=model_path,
                stride_index=s,
                teacher_layers=spec.teacher_layers,
                cfg=cfg,
                n_rotations=n_rotations,
            )

            attn_path = attn_dir / f"stride_{s:02d}.npz"
            np.savez_compressed(str(attn_path), **attn_data)
            sz = attn_path.stat().st_size / 1024 / 1024
            elapsed = time.time() - t_stride
            log(f"  → attention/stride_{s:02d}.npz  {sz:.1f} MB  ({elapsed:.1f}s)")

        log(f"\n  Attention total: {time.time() - t_attn_total:.1f}s")
    else:
        log("\n── Stage 4: Attention plates [SKIPPED] ─────────────────────────")

    # ── Stage 5: Save config.json and state.json ──────────────────────────
    log("\n── Stage 5: Saving metadata ────────────────────────────────────")

    # config.json — architecture config for downstream model construction
    config_dict = {
        "version": "v15",
        "d_model": cfg.d_model,
        "d_ff": cfg.d_ff,
        "n_heads": cfg.n_heads,
        "n_kv_heads": cfg.n_kv_heads,
        "d_head": cfg.d_head,
        "vocab_size": cfg.vocab_size,
        "n_strides": cfg.n_strides,
        "n_combinators": cfg.n_combinators,
        "max_seq_len": cfg.max_seq_len,
        "teacher_name": cfg.teacher_name,
        "teacher_n_layers": cfg.teacher_n_layers,
        "teacher_d_model": cfg.teacher_d_model,
        "teacher_d_ff": cfg.teacher_d_ff,
        "zones": {
            "CLASSIFY": {"strides": list(range(0, 5)),  "n_plates": 1, "attn": "LINEAR"},
            "COMPUTE":  {"strides": list(range(5, 13)), "n_plates": 2, "attn": "FULL"},
            "LINK":     {"strides": list(range(13, 16)), "n_plates": 2, "attn": "FULL"},
            "EMIT":     {"strides": list(range(16, 19)), "n_plates": 2, "attn": "LINEAR"},
        },
    }
    cfg_path = output_dir / "config.json"
    with open(cfg_path, "w") as f:
        json.dump(config_dict, f, indent=2)
    log(f"  Saved config.json: {cfg_path}")

    # state.json — extraction metadata / provenance
    state = {
        "version": "v15",
        "extraction_date": datetime.datetime.utcnow().isoformat() + "Z",
        "teacher": {
            "path": str(model_path),
            "name": cfg.teacher_name,
            "d_model": TEACHER_D_MODEL,
            "n_layers": TEACHER_N_LAYERS,
            "d_ff": TEACHER_D_FF,
            "vocab_size": TEACHER_VOCAB,
            "layer_pattern": "[L,L,L,F] × 16 (48 linear + 16 full attention)",
        },
        "student": {
            "d_model": cfg.d_model,
            "d_ff": cfg.d_ff,
            "n_strides": cfg.n_strides,
            "n_heads": cfg.n_heads,
            "n_kv_heads": cfg.n_kv_heads,
            "d_head": cfg.d_head,
            "vocab_size": cfg.vocab_size,
        },
        "stride_specs": [
            {
                "index": spec.index,
                "zone": spec.zone.name,
                "attn_type": spec.attn_type.name,
                "n_plates": spec.n_plates,
                "teacher_layers": list(spec.teacher_layers),
            }
            for spec in specs
        ],
        "extraction_flags": {
            "n_rotations": n_rotations,
            "skip_embeddings": skip_embeddings,
            "skip_ffn": skip_ffn,
            "skip_attention": skip_attention,
            "sklearn_svd": _HAS_SKLEARN,
        },
        "output_layout": {
            "v_proj.npy":    f"({TEACHER_D_MODEL}, {cfg.d_model}) float32",
            "embedding.npz": f"embedding: ({cfg.vocab_size}, {cfg.d_model // 4}) uint8",
            "strides/":      "stride_00.npz ... stride_18.npz  (gate/up/down plates + gammas)",
            "attention/":    "stride_05.npz ... stride_15.npz  (Q/K/V/O sign plates, FULL only)",
        },
        "2plate_note": (
            "plate1 = sign topology (program structure). "
            "plate2 = magnitude mirror of residual. "
            "Reconstruction: W ≈ plate1 * gamma1 + plate2 * gamma2."
        ),
        "elapsed_s": round(time.time() - t_total, 1),
    }
    state_path = output_dir / "state.json"
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)
    log(f"  Saved state.json:  {state_path}")

    # ── Stage 6: Verify ───────────────────────────────────────────────────
    ok = verify_checkpoint(output_dir, cfg)

    # ── Summary ───────────────────────────────────────────────────────────
    elapsed = time.time() - t_total
    log(f"\n{'=' * 72}")
    log(f"  V15 EXTRACTION {'COMPLETE ✓' if ok else 'COMPLETE (with warnings ✗)'}")
    log(f"{'─' * 72}")
    log(f"  Checkpoint dir:  {output_dir}")
    log(f"  Total elapsed:   {elapsed:.1f}s  ({elapsed / 60:.1f} min)")
    log(f"{'=' * 72}")
    if not ok:
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════════
# § 15  CLI entry point  (NEW in v15)
# ══════════════════════════════════════════════════════════════════════


def _build_parser() -> argparse.ArgumentParser:
    _default_model_path = (
        "~/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/latest"
    )
    parser = argparse.ArgumentParser(
        prog="extract",
        description=(
            "v15 extraction pipeline: pull crystal-native tensor statechart plates "
            "from Qwen3.6-27B (Apache-2.0) into a portable 19-stride checkpoint. "
            "Produces per-stride 1- or 2-plate FFN plates and attention plates "
            "for FULL-attention strides (COMPUTE + LINK)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full extraction (all stages):
  uv run python scripts/v15/extract.py \\
      --model-path ~/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/HASH/

  # Custom output directory:
  uv run python scripts/v15/extract.py \\
      --model-path /data/Qwen3.6-27B \\
      --output-dir checkpoints/v15-run2

  # Skip embeddings (already extracted):
  uv run python scripts/v15/extract.py \\
      --model-path /data/Qwen3.6-27B \\
      --skip-embeddings

  # Quick smoke test — FFN only, 2 rotations (fast, lower quality):
  uv run python scripts/v15/extract.py \\
      --model-path /data/Qwen3.6-27B \\
      --skip-embeddings --skip-attention --n-rotations 2

  # Attention only (resume after FFN):
  uv run python scripts/v15/extract.py \\
      --model-path /data/Qwen3.6-27B \\
      --skip-embeddings --skip-ffn
""",
    )
    parser.add_argument(
        "--model-path",
        type=str,
        default=str(Path(_default_model_path).expanduser()),
        help=(
            "Path to teacher model directory containing safetensors shards. "
            f"Default: {_default_model_path}"
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="checkpoints/v15-extracted",
        help="Output directory for the extracted checkpoint. Default: checkpoints/v15-extracted",
    )
    parser.add_argument(
        "--n-rotations",
        type=int,
        default=8,
        help=(
            "Number of orthogonal rotations for tomographic sign voting. "
            "Higher = more stable sign consensus, more compute. Default: 8"
        ),
    )
    parser.add_argument(
        "--skip-embeddings",
        action="store_true",
        help="Skip embedding plate extraction (useful for resuming).",
    )
    parser.add_argument(
        "--skip-ffn",
        action="store_true",
        help="Skip FFN stride plate extraction.",
    )
    parser.add_argument(
        "--skip-attention",
        action="store_true",
        help="Skip attention Q/K/V/O plate extraction.",
    )
    parser.add_argument(
        "--zero-frac",
        type=float,
        default=0.30,
        help=(
            "Fraction of positions per row to zero (bottom by magnitude). "
            "These are irreducible fixed points where GD deposited near-zero "
            "weights across teacher layers. Default: 0.30 (30%%). "
            "Set to 0.0 to disable zero placement."
        ),
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    model_path = Path(args.model_path).expanduser()
    output_dir = Path(args.output_dir)

    if not model_path.exists():
        log(f"ERROR: Model path does not exist: {model_path}")
        log(
            "Hint: Download with:\n"
            "  huggingface-cli download Qwen/Qwen3.6-27B --local-dir <path>\n"
            "  uv add huggingface-hub && huggingface-cli download Qwen/Qwen3.6-27B"
        )
        sys.exit(1)

    cfg = V15Config()

    log(f"v15 extraction — {cfg.n_strides} strides, "
        f"{cfg.d_model}d student from {cfg.teacher_name}")

    run_extraction(
        model_path=model_path,
        output_dir=output_dir,
        n_rotations=args.n_rotations,
        skip_embeddings=args.skip_embeddings,
        skip_ffn=args.skip_ffn,
        skip_attention=args.skip_attention,
        cfg=cfg,
        zero_frac=args.zero_frac,
    )


if __name__ == "__main__":
    main()
