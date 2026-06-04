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
v15 Extraction Pipeline — Qwen3.6-27B → 1B Ternary Student.

Key differences from v14 extraction
────────────────────────────────────
v14 had 16 stride layers: 10 composition (SSA) + 6 retrieval (GLA).
  • Composition strides used SSA (full_attn): Q/K/V/O from self_attn.
  • Retrieval strides used GLA (linear_attn): Q/K/V/O split from in_proj_qkv.
  • Two code paths: extract_ssa_plates() for SSA, extract_gla_plates() for GLA.

v15 has 19 stride layers: ALL composition (FibonacciStrideAttention).
  • ALL strides use the same Q/K/V/O projection dimensions: d_model→d_model.
  • Only ONE code path needed — extract_ssa_plates() for every stride.
  • No GLA extraction — simplifies the mapping considerably.

Stride-to-teacher-layer mapping (19 strides → 64 teacher layers)
──────────────────────────────────────────────────────────────────
v14: stride_idx * 4  (16 strides × step 4 = layers 0,4,8,...,60)
v15: distribute 19 strides across 64 layers as evenly as possible.
     stride_i → floor(i * 64 / 19) = layers 0,3,6,10,13,17,20,23,27,30,
                                               33,37,40,43,47,50,54,57,60

For teacher layers that land on a GLA layer (pos % 4 != 3):
  → pull from that layer's self_attn (the nearby full-attention layer)
  → Qwen3.6-27B pattern: [L,L,L,F]×16. Full-attn at positions 3,7,11,...,63.
  → If the target layer is a GLA layer, advance to the next full-attn layer.

This gives clean extraction: ALL v15 strides get full-attention plates from
teacher. The student never sees GLA topology — only SSA-derived sign crystals.

Output: checkpoints/v15-extracted/model.npz

Architecture mapping
────────────────────
Teacher (Qwen3.6-27B):  64 layers, d=5120, pattern [L,L,L,F]×16
Student (v15 1B):        19 stride layers, d=1280, ALL composition

Attention plate key format:
  shared_stride_stack.layers.{0-18}.{q, k, v, o}  → (d, d//16) uint32

FFN plates (zone-voted):
  stack_a.ffn.{gate, up, down}
  stack_c.ffn.{gate, up, down}

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

# ── Path setup ────────────────────────────────────────────────────────
_v15_dir = str(Path(__file__).parent)
if _v15_dir not in sys.path:
    sys.path.insert(0, _v15_dir)
from config import V15Config


# ══════════════════════════════════════════════════════════════════════
# § 0  Teacher constants
# ══════════════════════════════════════════════════════════════════════

TEACHER_D_MODEL = 5120
TEACHER_N_LAYERS = 64
TEACHER_D_FF = 17408
TEACHER_VOCAB = 248320
TEACHER_PREFIX = "model.language_model"

# Qwen3.6-27B full-attn shapes
TEACHER_SSA_Q_ROWS = 12288   # 96 heads × 128 dim
TEACHER_SSA_K_ROWS = 1024    # 8 heads × 128 dim
TEACHER_SSA_V_ROWS = 1024    # 8 heads × 128 dim

# v15: ALL 19 strides use FibonacciStrideAttention
N_STUDENT_STRIDE_LAYERS = 19


def teacher_layer_type(layer_idx: int) -> str:
    """Determine if teacher layer is linear_attn (GLA) or full_attn (SSA).

    Qwen3.6-27B pattern: [L, L, L, F] × 16.
    Full attention at indices where (layer_idx % 4 == 3).
    """
    return "full_attn" if (layer_idx % 4 == 3) else "linear_attn"


def nearest_full_attn_layer(layer_idx: int) -> int:
    """Return the nearest full-attention layer at or after layer_idx.

    Since Qwen3.6-27B has full_attn at positions 3,7,11,...,63, this
    rounds up to the next multiple of 4 that is ≡ 3 (mod 4).
    """
    if teacher_layer_type(layer_idx) == "full_attn":
        return layer_idx
    # Next full-attn position: the next number ≡ 3 (mod 4) >= layer_idx
    remainder = layer_idx % 4
    steps_to_next = (3 - remainder) % 4
    candidate = layer_idx + steps_to_next
    return min(candidate, TEACHER_N_LAYERS - 1)


def teacher_layer_for_stride(stride_idx: int, n_strides: int = N_STUDENT_STRIDE_LAYERS) -> int:
    """Map student stride index (0 to n_strides-1) to a teacher FULL-ATTN layer.

    Distributes n_strides evenly across 64 teacher layers.
    Then rounds up to the nearest full-attention layer so the extraction
    always pulls from SSA (self_attn) tensors — consistent with v15's
    all-composition architecture.

    stride_idx=0  → teacher layer  0  → full_attn: layer  3
    stride_idx=1  → teacher layer  3  → full_attn: layer  3
    stride_idx=2  → teacher layer  6  → full_attn: layer  7
    stride_idx=3  → teacher layer 10  → full_attn: layer 11
    ... (evenly spaced, always rounded up to nearest SSA layer)
    """
    # Evenly distribute across [0, 63]
    raw_layer = int(stride_idx * TEACHER_N_LAYERS / n_strides)
    raw_layer = min(raw_layer, TEACHER_N_LAYERS - 1)
    return nearest_full_attn_layer(raw_layer)


# Pre-compute and validate the mapping
_STRIDE_TO_TEACHER = [
    teacher_layer_for_stride(i) for i in range(N_STUDENT_STRIDE_LAYERS)
]

# FFN zone mapping — same as v14 (2-stack design unchanged)
FFN_LAYERS_A: tuple[int, ...] = (4, 20, 32)   # aperture → fan → mid
FFN_LAYERS_C: tuple[int, ...] = (32, 48, 56)  # mid → converge → decode


# ══════════════════════════════════════════════════════════════════════
# § 1  Logging
# ══════════════════════════════════════════════════════════════════════


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def log_shape(label: str, arr: np.ndarray) -> None:
    log(f"    {label}: {arr.shape}  dtype={arr.dtype}")


# ══════════════════════════════════════════════════════════════════════
# § 2  Safetensors loading (identical to v14)
# ══════════════════════════════════════════════════════════════════════

_SHARD_INDEX_CACHE: dict[str, dict[str, Any]] = {}


def _load_shard_index(model_path: Path) -> dict[str, Any] | None:
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
        shard_filename = index.get("weight_map", {}).get(tensor_name)
        if shard_filename:
            return model_path / shard_filename
    for sf_path in sorted(model_path.glob("model*.safetensors")):
        with safe_open(str(sf_path), framework="pt") as sf:
            if tensor_name in sf.keys():
                return sf_path
    return None


def load_tensor(model_path: Path, tensor_name: str) -> np.ndarray:
    shard_path = find_shard(model_path, tensor_name)
    if shard_path is None:
        raise FileNotFoundError(f"Tensor {tensor_name!r} not found in {model_path}")
    with safe_open(str(shard_path), framework="pt") as sf:
        return sf.get_tensor(tensor_name).float().numpy()


# ══════════════════════════════════════════════════════════════════════
# § 3  Truncated SVD (identical to v14)
# ══════════════════════════════════════════════════════════════════════


def truncated_svd(M: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    k = min(k, min(M.shape) - 1)
    if k < 1:
        k = 1
    if _HAS_SKLEARN and _rsvd is not None:
        U, S, Vt = _rsvd(M, n_components=k, n_iter=4, random_state=42)
    else:
        U, S, Vt = np.linalg.svd(M, full_matrices=False)
        U, S, Vt = U[:, :k], S[:k], Vt[:k, :]
    return U.astype(np.float32), S.astype(np.float32), Vt.astype(np.float32)


# ══════════════════════════════════════════════════════════════════════
# § 4  360° tomographic sign voting (identical to v14)
# ══════════════════════════════════════════════════════════════════════


def _random_orthogonal(n: int, rng: np.random.RandomState) -> np.ndarray:
    H = rng.randn(n, n).astype(np.float32)
    Q, R = np.linalg.qr(H)
    Q *= np.sign(np.diag(R))
    return Q


def extract_sign_pattern(
    W: np.ndarray, d_out: int, d_in: int, n_rotations: int = 8,
) -> np.ndarray:
    """Extract ternary sign pattern via 360° tomographic sign voting."""
    n_out, n_in = W.shape
    rng = np.random.RandomState(42)

    if n_out == d_out and n_in == d_in:
        votes = np.zeros((d_out, d_in), dtype=np.float32)
        for r in range(n_rotations):
            W_rot = W if r == 0 else W @ _random_orthogonal(d_in, rng)
            votes += np.sign(W_rot)
        result = np.sign(votes).astype(np.int8)
        mask = result == 0
        if mask.any():
            result[mask] = rng.choice([-1, 1], size=int(mask.sum())).astype(np.int8)
        return result

    k = min(max(d_out, d_in), min(n_out, n_in) - 1)
    U_base, _S, Vt_base = truncated_svd(W, k)
    k_out = min(d_out, U_base.shape[1])
    k_in = min(d_in, Vt_base.shape[0])

    votes = np.zeros((d_out, d_in), dtype=np.float32)
    for r in range(n_rotations):
        if r == 0:
            P_out = U_base[:, :k_out].T
            P_in = Vt_base[:k_in, :]
        else:
            R_out = _random_orthogonal(k_out, rng)
            R_in = _random_orthogonal(k_in, rng)
            P_out = R_out @ U_base[:, :k_out].T
            P_in = R_in @ Vt_base[:k_in, :]

        Wp = P_out @ W @ P_in.T
        angle_signs = np.zeros((d_out, d_in), dtype=np.float32)
        angle_signs[:k_out, :k_in] = np.sign(Wp)
        votes += angle_signs

    result = np.sign(votes).astype(np.int8)
    zeros = result == 0
    if zeros.any():
        result[zeros] = rng.choice([-1, 1], size=int(zeros.sum())).astype(np.int8)
    return result


# ══════════════════════════════════════════════════════════════════════
# § 5  Ternary packing (identical to v14)
# ══════════════════════════════════════════════════════════════════════


def pack_ternary_np(w_int8: np.ndarray) -> np.ndarray:
    """Pack int8 {-1, 0, +1} array [N, K] → uint32 [N, K // 16]."""
    assert w_int8.ndim == 2
    assert w_int8.shape[1] % 16 == 0, f"K ({w_int8.shape[1]}) must be divisible by 16"
    N, K = w_int8.shape
    mapped = (w_int8.astype(np.int32) + 1).astype(np.uint32)
    packed = np.zeros((N, K // 16), dtype=np.uint32)
    for i in range(16):
        packed |= mapped[:, i::16] << (i * 2)
    return packed


def pack_ternary_uint8_np(w_int8: np.ndarray) -> np.ndarray:
    """Pack int8 {-1, 0, +1} array [N, K] → uint8 [N, K // 4]."""
    assert w_int8.ndim == 2
    assert w_int8.shape[1] % 4 == 0
    w_shifted = (w_int8.astype(np.int16) + 1).astype(np.uint8)
    packed = (
        (w_shifted[:, 0::4] << 6) |
        (w_shifted[:, 1::4] << 4) |
        (w_shifted[:, 2::4] << 2) |
        w_shifted[:, 3::4]
    )
    return packed.astype(np.uint8)


# ══════════════════════════════════════════════════════════════════════
# § 6  Global projection basis (identical to v14)
# ══════════════════════════════════════════════════════════════════════


def compute_global_projection(
    model_path: Path, d_model: int, teacher_d_model: int, cfg: V15Config,
) -> np.ndarray:
    t0 = time.time()
    embed_name = f"{TEACHER_PREFIX}.embed_tokens.weight"
    log(f"  Loading embeddings: {embed_name}")
    E = load_tensor(model_path, embed_name)
    log(f"  Embedding shape: {E.shape}  dtype={E.dtype}")
    log(f"  Computing truncated SVD (top-{d_model} components) ...")
    _U, _S, Vt = truncated_svd(E, d_model)
    V_proj = Vt.T
    del E, _U, _S, Vt
    log(f"  V_proj shape: {V_proj.shape}  ({time.time() - t0:.1f}s)")
    return V_proj


# ══════════════════════════════════════════════════════════════════════
# § 7  Embedding plate extraction (identical to v14)
# ══════════════════════════════════════════════════════════════════════


def extract_embeddings(
    model_path: Path, V_proj: np.ndarray, cfg: V15Config,
) -> np.ndarray:
    t0 = time.time()
    embed_name = f"{TEACHER_PREFIX}.embed_tokens.weight"
    log(f"  Loading embeddings for sign extraction ...")
    E = load_tensor(model_path, embed_name)
    log(f"  Projecting: {E.shape} @ {V_proj.shape} ...")
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
    zeros = signs == 0
    if zeros.any():
        rng = np.random.RandomState(7)
        signs[zeros] = rng.choice([-1, 1], size=int(zeros.sum())).astype(np.int8)
    log(f"  Embedding signs: {signs.shape}  ({time.time() - t0:.1f}s)")
    return signs


# ══════════════════════════════════════════════════════════════════════
# § 8  Attention plate extraction — ALL strides use SSA (full_attn)
# ══════════════════════════════════════════════════════════════════════
#
# v15 simplification: all 19 student strides use FibonacciStrideAttention
# with Q/K/V/O all of shape (d_model, d_model). We always extract from
# teacher's self_attn (full attention layers).
#
# Teacher SSA shapes (Qwen3.6-27B):
#   q_proj.weight:  (12288, 5120)  = (96 heads × 128 dim, d_model)
#   k_proj.weight:  (1024, 5120)   = (8 heads × 128 dim, d_model)
#   v_proj.weight:  (1024, 5120)   = (8 heads × 128 dim, d_model)
#   o_proj.weight:  (5120, 12288)  = (d_model, 96 heads × 128 dim)
#
# Student target: (d_model, d_model) = (1280, 1280) for all Q/K/V/O


def extract_ssa_plates(
    model_path: Path,
    teacher_layer: int,
    cfg: V15Config,
    n_rotations: int,
) -> dict[str, np.ndarray]:
    """Extract Q/K/V/O plates from a teacher full-attention layer.

    Args:
        model_path:    Path to teacher model directory.
        teacher_layer: Teacher layer index (must be a full_attn layer).
        cfg:           V15Config instance.
        n_rotations:   Tomographic viewing angles for sign voting.

    Returns:
        Dict with keys "q", "k", "v", "o" → int8 (d_model, d_model).
    """
    assert teacher_layer_type(teacher_layer) == "full_attn", (
        f"Expected full_attn layer, got {teacher_layer} ({teacher_layer_type(teacher_layer)})"
    )
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
            W, d_out=cfg.d_model, d_in=cfg.d_model, n_rotations=n_rotations,
        )
        del W

    return plates


# ══════════════════════════════════════════════════════════════════════
# § 9  FFN plate extraction (identical to v14)
# ══════════════════════════════════════════════════════════════════════


def extract_ffn_plates_for_zone(
    model_path: Path,
    teacher_layers: tuple[int, ...],
    cfg: V15Config,
    n_rotations: int,
    zone_name: str,
) -> dict[str, np.ndarray]:
    """Extract zone-voted FFN plates (gate, up, down) from 3 teacher layers."""
    log(f"  FFN zone {zone_name}: voting across teacher layers {teacher_layers}")

    gate_votes = np.zeros((cfg.d_ff, cfg.d_model), dtype=np.float32)
    up_votes   = np.zeros((cfg.d_ff, cfg.d_model), dtype=np.float32)
    down_votes = np.zeros((cfg.d_model, cfg.d_ff), dtype=np.float32)

    for teacher_layer in teacher_layers:
        layer_prefix = f"{TEACHER_PREFIX}.layers.{teacher_layer}.mlp"

        W_gate = load_tensor(model_path, f"{layer_prefix}.gate_proj.weight")
        log(f"    layer {teacher_layer} gate_proj: {W_gate.shape}")
        gate_votes += extract_sign_pattern(
            W_gate, d_out=cfg.d_ff, d_in=cfg.d_model, n_rotations=n_rotations,
        ).astype(np.float32)
        del W_gate

        W_up = load_tensor(model_path, f"{layer_prefix}.up_proj.weight")
        log(f"    layer {teacher_layer} up_proj:   {W_up.shape}")
        up_votes += extract_sign_pattern(
            W_up, d_out=cfg.d_ff, d_in=cfg.d_model, n_rotations=n_rotations,
        ).astype(np.float32)
        del W_up

        W_down = load_tensor(model_path, f"{layer_prefix}.down_proj.weight")
        log(f"    layer {teacher_layer} down_proj: {W_down.shape}")
        down_votes += extract_sign_pattern(
            W_down, d_out=cfg.d_model, d_in=cfg.d_ff, n_rotations=n_rotations,
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
# § 10  Verification
# ══════════════════════════════════════════════════════════════════════


def verify_checkpoint(output_dir: Path, cfg: V15Config) -> bool:
    """Load saved model.npz and verify expected shapes for all keys."""
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

    d = cfg.d_model          # 1280
    d16 = d // 16            # 80  (uint32 TernaryLinear)
    d4 = d // 4              # 320 (uint8 TernaryEmbedding)
    dff = cfg.d_ff           # 5120
    dff16 = dff // 16        # 320
    vocab = cfg.vocab_size   # 248320

    for key in keys:
        arr = data[key]
        if key == "embed_tokens":
            expected = (vocab, d4)
        elif key.startswith("shared_stride_stack.") and any(
            key.endswith(f".{p}") for p in ("q", "k", "v", "o")
        ):
            # All v15 strides: (d, d//16) — uniform for all composition strides
            expected = (d, d16)
        elif key.endswith(".gate") or key.endswith(".up"):
            expected = (dff, d16)
        elif key.endswith(".down"):
            expected = (d, dff16)
        else:
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
# § 11  Main extraction pipeline
# ══════════════════════════════════════════════════════════════════════


def run_extraction(
    teacher_path: Path,
    output_dir: Path,
    n_rotations: int = 8,
    skip_embeddings: bool = False,
    skip_attention: bool = False,
    cfg: V15Config | None = None,
) -> None:
    """Full v15 extraction pipeline: teacher → ternary student checkpoint.

    Stages:
      1. Global V_proj from embedding SVD.
      2. Embedding signs (vocab × d_model) → pack → model.npz.
      3. For each of 19 strides: attention Q/K/V/O from full_attn → pack.
         (All 19 strides are composition — no GLA extraction needed.)
      4. FFN zone plates (zone-voted from 3 teacher layers per stack).
      5. Save model.npz and state.json.
      6. Verify saved checkpoint.
    """
    t_total = time.time()

    if cfg is None:
        cfg = V15Config()

    output_dir.mkdir(parents=True, exist_ok=True)

    log("=" * 72)
    log("  V15 Extraction Pipeline — Qwen3.6-27B → 1B Ternary Student")
    log("=" * 72)
    log(f"  Teacher path:  {teacher_path}")
    log(f"  Output dir:    {output_dir}")
    log(f"  d_model:          {cfg.d_model}")
    log(f"  d_ff:             {cfg.d_ff}")
    log(f"  n_strides:        {cfg.n_strides} (ALL composition, no GLA)")
    log(f"  n_rotations:      {n_rotations}")
    log(f"  sklearn SVD:   {_HAS_SKLEARN}")
    log("")

    # Print stride-to-teacher mapping
    log("  Stride → Teacher layer mapping:")
    for i, tl in enumerate(_STRIDE_TO_TEACHER):
        log(f"    stride {i:02d} (s={cfg.strides[i]:4d}) → teacher layer {tl:2d} (full_attn)")
    log("")

    npz_data: dict[str, np.ndarray] = {}
    shapes_log: dict[str, list[int]] = {}

    # ── Stage 1: Global projection basis ──────────────────────────
    log("── Stage 1: Global projection basis (embedding SVD) ────────")
    V_proj = compute_global_projection(teacher_path, cfg.d_model, TEACHER_D_MODEL, cfg)

    # ── Stage 2: Embedding plate ───────────────────────────────────
    if not skip_embeddings:
        log("\n── Stage 2: Embedding plate ────────────────────────────────")
        t_emb = time.time()
        emb_signs = extract_embeddings(teacher_path, V_proj, cfg)
        emb_packed = pack_ternary_uint8_np(emb_signs)
        key = "embed_tokens"
        npz_data[key] = emb_packed
        shapes_log[key] = list(emb_packed.shape)
        log(f"  Packed embedding: {emb_signs.shape} → {emb_packed.shape}  "
            f"({time.time() - t_emb:.1f}s)")
        del emb_signs, emb_packed

    # ── Stage 3: Attention plates — ALL strides use SSA ───────────
    if not skip_attention:
        log("\n── Stage 3: Attention plates (19 strides, ALL full_attn) ──")
        attn_count = 0

        for stride_idx in range(N_STUDENT_STRIDE_LAYERS):
            teacher_layer = _STRIDE_TO_TEACHER[stride_idx]
            student_stride = cfg.strides[stride_idx]
            t_layer = time.time()

            assert teacher_layer_type(teacher_layer) == "full_attn", (
                f"Stride {stride_idx} mapped to non-full-attn layer {teacher_layer}!"
            )

            log(f"  [stride {stride_idx:02d}, s={student_stride:4d}] → "
                f"teacher layer {teacher_layer} (full_attn)")

            plates = extract_ssa_plates(teacher_path, teacher_layer, cfg, n_rotations)

            for proj_name, signs in plates.items():
                # All v15 Q/K/V/O: (d_model, d_model) → packed (d_model, d_model//16)
                packed = pack_ternary_np(signs)
                key = f"shared_stride_stack.layers.{stride_idx}.{proj_name}"
                npz_data[key] = packed
                shapes_log[key] = list(packed.shape)
                attn_count += 1
                del signs, packed

            log(f"    Done in {time.time() - t_layer:.1f}s")

        log(f"\n  Attention total: {attn_count} packed arrays "
            f"({N_STUDENT_STRIDE_LAYERS} strides × 4 projections)")

    # ── Stage 4: FFN plates (zone-voted, 2 stacks) ────────────────
    log("\n── Stage 4: FFN plates (zone-voted, 2 stacks) ──────────────")
    ffn_config: dict[str, tuple[int, ...]] = {
        "stack_a": FFN_LAYERS_A,
        "stack_c": FFN_LAYERS_C,
    }
    for stack_name, ffn_layers in ffn_config.items():
        t_ffn = time.time()
        ffn_plates = extract_ffn_plates_for_zone(
            teacher_path, ffn_layers, cfg, n_rotations, zone_name=stack_name,
        )
        for ffn_key, signs in ffn_plates.items():
            packed = pack_ternary_np(signs)
            key = f"{stack_name}.ffn.{ffn_key}"
            npz_data[key] = packed
            shapes_log[key] = list(packed.shape)
            del signs, packed
        log(f"  {stack_name} FFN done in {time.time() - t_ffn:.1f}s")

    # ── Stage 5: Save checkpoint ──────────────────────────────────
    log("\n── Stage 5: Saving checkpoint ──────────────────────────────")
    npz_path = output_dir / "model.npz"
    t_save = time.time()
    np.savez_compressed(str(npz_path), **npz_data)
    log(f"  Saved model.npz: {npz_path.stat().st_size / 1024 / 1024:.1f} MB  "
        f"({time.time() - t_save:.1f}s)")
    log(f"  Total arrays: {len(npz_data)}")

    # stride-to-teacher mapping for state.json
    stride_map = {
        str(i): {
            "student_stride": cfg.strides[i],
            "student_type": "composition",
            "teacher_layer": _STRIDE_TO_TEACHER[i],
            "teacher_type": "full_attn",
        }
        for i in range(N_STUDENT_STRIDE_LAYERS)
    }

    state = {
        "version": "v15",
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
            "n_strides": cfg.n_strides,
            "strides": list(cfg.strides),
            "stride_pattern": "all composition (FibonacciStrideAttention, no GLA)",
            "vocab_size": cfg.vocab_size,
            "n_heads": cfg.n_heads,
            "d_head": cfg.d_head,
            "neighbor_radius": cfg.neighbor_radius,
        },
        "stride_mapping": stride_map,
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
            "all_composition": True,
            "no_gla_extraction": True,
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

    elapsed = time.time() - t_total
    log(f"\n{'=' * 72}")
    log(f"  V15 EXTRACTION {'COMPLETE ✓' if ok else 'COMPLETE (with warnings ✗)'}")
    log(f"{'─' * 72}")
    log(f"  Arrays saved:    {len(npz_data)}")
    log(f"  Checkpoint dir:  {output_dir}")
    log(f"  model.npz size:  {npz_path.stat().st_size / 1024 / 1024:.1f} MB")
    log(f"  Total elapsed:   {elapsed:.1f}s  ({elapsed / 60:.1f} min)")
    log(f"{'=' * 72}")
    if not ok:
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════════
# § 12  CLI entry point
# ══════════════════════════════════════════════════════════════════════


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="extract_qwen36",
        description=(
            "v15 extraction pipeline: pull ternary sign-pattern crystal plates "
            "from Qwen3.6-27B (Apache-2.0) into a portable 1B student checkpoint.\n\n"
            "v15 vs v14: all 19 strides are composition (FibonacciStrideAttention). "
            "No GLA extraction needed — one uniform code path for all strides."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default run (all stages, 8 rotations):
  uv run python scripts/v15/extract_qwen36.py

  # Custom teacher path:
  uv run python scripts/v15/extract_qwen36.py \\
      --teacher-path ~/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/abc123

  # Skip embeddings:
  uv run python scripts/v15/extract_qwen36.py --skip-embeddings

  # Quick smoke test — FFN only, 2 rotations:
  uv run python scripts/v15/extract_qwen36.py \\
      --skip-embeddings --skip-attention --n-rotations 2
""",
    )
    _default_teacher_path = (
        "~/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/latest"
    )
    parser.add_argument(
        "--teacher-path", type=str,
        default=str(Path(_default_teacher_path).expanduser()),
        help=f"Path to teacher model directory. Default: {_default_teacher_path}",
    )
    parser.add_argument(
        "--output", type=str, default="checkpoints/v15-extracted",
        help="Output directory. Default: checkpoints/v15-extracted",
    )
    parser.add_argument("--skip-embeddings", action="store_true")
    parser.add_argument("--skip-attention", action="store_true")
    parser.add_argument(
        "--n-rotations", type=int, default=8,
        help="Number of orthogonal rotations for sign voting (default: 8)",
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

    cfg = V15Config()
    run_extraction(
        teacher_path=teacher_path,
        output_dir=output_dir,
        n_rotations=args.n_rotations,
        skip_embeddings=args.skip_embeddings,
        skip_attention=args.skip_attention,
        cfg=cfg,
    )


# ══════════════════════════════════════════════════════════════════════
# Self-test (validates mapping logic without teacher weights)
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys as _sys

    # If run with --help or arguments, go to CLI
    if len(_sys.argv) > 1:
        main()
        _sys.exit(0)

    # Otherwise: self-test
    print("=" * 60)
    print("v15 extract_qwen36.py self-test (no teacher weights needed)")
    print("=" * 60)

    cfg = V15Config()

    print(f"\nStride mapping ({N_STUDENT_STRIDE_LAYERS} strides → teacher layers):")
    for i, tl in enumerate(_STRIDE_TO_TEACHER):
        ltype = teacher_layer_type(tl)
        print(f"  stride {i:02d} (s={cfg.strides[i]:4d}) → teacher layer {tl:2d} ({ltype})")

    # Verify all mappings land on full_attn
    for i, tl in enumerate(_STRIDE_TO_TEACHER):
        assert teacher_layer_type(tl) == "full_attn", (
            f"Stride {i} mapped to non-full-attn layer {tl} ({teacher_layer_type(tl)})"
        )
    print("\n  All strides map to full_attn layers ✓")

    # Verify distribution covers teacher layers reasonably
    unique_layers = sorted(set(_STRIDE_TO_TEACHER))
    print(f"  Unique teacher layers used: {unique_layers}")
    print(f"  Coverage: {len(unique_layers)} / 16 full-attn layers "
          f"({len(unique_layers)/16*100:.0f}%)")

    # Verify nearest_full_attn_layer
    for i in range(64):
        tl = nearest_full_attn_layer(i)
        assert teacher_layer_type(tl) == "full_attn", f"Layer {i} → {tl} not full_attn"
        assert tl >= i, f"Layer {i} → {tl} went backwards"
    print("  nearest_full_attn_layer: all correct ✓")

    # Test packing functions
    print("\nPacking functions...")
    rng = np.random.default_rng(42)
    d = cfg.d_model  # 1280

    # TernaryLinear packing: (d, d//16) uint32
    w = rng.choice([-1, 0, 1], size=(d, d)).astype(np.int8)
    p = pack_ternary_np(w)
    assert p.shape == (d, d // 16)
    assert p.dtype == np.uint32
    print(f"  pack_ternary_np: {w.shape} → {p.shape} {p.dtype} ✓")

    # TernaryEmbedding packing: (vocab, d//4) uint8
    w_emb = rng.choice([-1, 1], size=(100, d)).astype(np.int8)
    p_emb = pack_ternary_uint8_np(w_emb)
    assert p_emb.shape == (100, d // 4)
    assert p_emb.dtype == np.uint8
    print(f"  pack_ternary_uint8_np: {w_emb.shape} → {p_emb.shape} {p_emb.dtype} ✓")

    # Test extract_sign_pattern (CPU only)
    print("\nSign pattern extraction (small matrix)...")
    W_small = rng.standard_normal((256, 512)).astype(np.float32)
    signs = extract_sign_pattern(W_small, d_out=64, d_in=64, n_rotations=4)
    assert signs.shape == (64, 64)
    assert signs.dtype == np.int8
    assert set(signs.flat).issubset({-1, 1})
    print(f"  extract_sign_pattern: {W_small.shape} → {signs.shape} ✓")

    print("\n" + "=" * 60)
    print("v15 extract_qwen36.py: all tests passed ✓")
    print("Run 'python extract_qwen36.py --help' for extraction CLI.")
