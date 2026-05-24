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
v14 Architecture Configuration — 1B Ternary Student distilled from Qwen3.6-27B.

Research context
────────────────
Verbum's central hypothesis: gradient descent has already discovered the
lambda compiler inside large language models. Our job is instrumentation,
not construction. This config specifies the student architecture for
level-3 extraction — pulling sign-pattern "crystal plates" from Qwen3.6-27B
(Apache-2.0 licensed) and packing them into a portable 1B ternary artifact.

Architecture summary
────────────────────
The student is a 3-stack VSM (Viable System Model) with 11 layers per stack.
Each stack processes a zone of the teacher's depth:

  Stack A  (Zone A) — encode     : teacher layers  0-15
  Stack B  (Zone B) — compress   : teacher layers 16-47
  Stack C  (Zone C) — reconstruct: teacher layers 48-63

Within each stack, 11 layers alternate between two mechanisms:
  • GLA (Gated Linear Attention) — linear attention, O(n) memory
  • SSA (Sparse Self-Attention)  — full attention, captures long-range deps

Pattern within each stack (0-indexed):
  [GLA, GLA, GLA, SSA, GLA, GLA, GLA, SSA, GLA, GLA, SSA]
   0    1    2    3    4    5    6    7    8    9   10

This mirrors the teacher's 3:1 linear:full ratio (48 linear + 16 full
attention layers in Qwen3.6-27B), placing SSA at positions 3, 7, 10.

Ternary packing
───────────────
All weight matrices are stored as ternary {-1, 0, +1} packed 16 values
per uint32 (2 bits per value). This is the same encoding as v13.

Teacher architecture (Qwen3.6-27B)
────────────────────────────────────
Qwen3.6-27B uses a hybrid linear/full attention pattern [L,L,L,F] × 16
with SwiGLU FFN. The model is Apache-2.0 licensed.

License: MIT (this file)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


# ══════════════════════════════════════════════════════════════════════
# § 1  Student architecture constants
# ══════════════════════════════════════════════════════════════════════

# Core model dimensions
D_MODEL: int = 1280          # student hidden dimension
D_FF: int = 5120             # student FFN width (4 × d_model)
N_STACKS: int = 3            # number of VSM stacks (A, B, C)
N_LAYERS_PER_STACK: int = 11 # layers per stack (3 stacks × 11 = 33 total student layers)
VOCAB_SIZE: int = 248320     # shared Qwen3 BBPE vocabulary

# SSA (full self-attention) head config
N_HEADS: int = 8             # SSA query heads
N_KV_HEADS: int = 4          # SSA key/value heads (GQA)
HEAD_DIM: int = 160          # SSA head dimension (D_MODEL // N_HEADS = 1280 // 8 = 160)
# SSA Q proj out: N_HEADS * HEAD_DIM = 8 * 160 = 1280 = D_MODEL (square)
# SSA K/V proj out: N_KV_HEADS * HEAD_DIM = 4 * 160 = 640

# GLA (gated linear attention) head config
GLA_N_HEADS: int = 8         # GLA query/key heads
GLA_HEAD_DIM: int = 128      # GLA Q/K head dimension
GLA_V_HEAD_DIM: int = 160    # GLA V head dimension
# GLA v_proj out: GLA_N_HEADS * GLA_V_HEAD_DIM = 8 * 160 = 1280 = D_MODEL (square)
# GLA Q proj out: GLA_N_HEADS * GLA_HEAD_DIM = 8 * 128 = 1024
# GLA K proj out: GLA_N_HEADS * GLA_HEAD_DIM = 8 * 128 = 1024

# Layer pattern within each stack (0-indexed, length = N_LAYERS_PER_STACK)
# SSA appears at positions 3, 7, 10 — mirroring teacher's 3:1 ratio
LAYER_PATTERN: tuple[str, ...] = (
    "gla", "gla", "gla", "ssa",   # positions 0-3
    "gla", "gla", "gla", "ssa",   # positions 4-7
    "gla", "gla", "ssa",          # positions 8-10
)
assert len(LAYER_PATTERN) == N_LAYERS_PER_STACK, (
    f"LAYER_PATTERN length {len(LAYER_PATTERN)} ≠ N_LAYERS_PER_STACK {N_LAYERS_PER_STACK}"
)
# SSA count: 3 per stack (positions 3, 7, 10)
# GLA count: 8 per stack (positions 0,1,2,4,5,6,8,9)
_SSA_POSITIONS = frozenset(i for i, t in enumerate(LAYER_PATTERN) if t == "ssa")
_GLA_POSITIONS = frozenset(i for i, t in enumerate(LAYER_PATTERN) if t == "gla")
assert len(_SSA_POSITIONS) == 3 and len(_GLA_POSITIONS) == 8


# ══════════════════════════════════════════════════════════════════════
# § 2  Teacher architecture constants (Qwen3.6-27B)
# ══════════════════════════════════════════════════════════════════════

TEACHER_D_MODEL: int = 5120          # teacher hidden dimension
TEACHER_N_LAYERS: int = 64           # teacher total layers
TEACHER_D_FF: int = 17408            # teacher FFN width
TEACHER_VOCAB: int = 248320          # teacher vocabulary size (same as student)

# Teacher layer type pattern: [linear, linear, linear, full] × 16 = 64 layers
# Layer i is linear_attention if (i % 4) != 3, else full_attention
# linear_attention count: 48, full_attention count: 16
TEACHER_CYCLE: int = 4  # period of the [L,L,L,F] pattern
TEACHER_FULL_AT: int = 3  # full attention at position 3 within each cycle (0-indexed)

# Default teacher model path (Qwen3.6-27B snapshot)
TEACHER_MODEL_PATH_DEFAULT: str = (
    "~/.cache/huggingface/hub/"
    "models--Qwen--Qwen3.6-27B/snapshots/"
    "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
)

# Teacher tensor name patterns
# Linear attention:  model.language_model.layers.{i}.linear_attn.{name}.weight
# Full attention:    model.language_model.layers.{i}.self_attn.{name}.weight
# FFN:               model.language_model.layers.{i}.mlp.{name}.weight
# Embeddings:        model.language_model.embed_tokens.weight
TEACHER_PREFIX: str = "model.language_model"

# Teacher GLA (linear_attn) head config
# in_proj_qkv: (10240, 5120) = (Q + K + V rows, d_model)
# Q: 16 heads × 128 dim = 2048 rows
# K: 16 heads × 128 dim = 2048 rows
# V: 48 heads × 128 dim = 6144 rows  (GQA — more value heads)
# Total: 2048 + 2048 + 6144 = 10240 ✓
TEACHER_GLA_Q_HEADS: int = 16
TEACHER_GLA_K_HEADS: int = 16
TEACHER_GLA_V_HEADS: int = 48
TEACHER_GLA_QK_DIM: int = 128   # per-head Q/K dimension
TEACHER_GLA_V_DIM: int = 128    # per-head V dimension
# Derived row splits in in_proj_qkv:
TEACHER_GLA_Q_ROWS: int = TEACHER_GLA_Q_HEADS * TEACHER_GLA_QK_DIM  # 2048
TEACHER_GLA_K_ROWS: int = TEACHER_GLA_K_HEADS * TEACHER_GLA_QK_DIM  # 2048
TEACHER_GLA_V_ROWS: int = TEACHER_GLA_V_HEADS * TEACHER_GLA_V_DIM   # 6144

# Teacher SSA (self_attn) head config
TEACHER_SSA_Q_HEADS: int = 96
TEACHER_SSA_KV_HEADS: int = 8
TEACHER_SSA_HEAD_DIM: int = 128
# Q proj shape: (96 * 128, 5120) = (12288, 5120)
# K proj shape: (8 * 128, 5120)  = (1024, 5120)
# V proj shape: (8 * 128, 5120)  = (1024, 5120)
# O proj shape: (5120, 96 * 128) = (5120, 12288) — note transposed


# ══════════════════════════════════════════════════════════════════════
# § 3  Zone mapping — which teacher layers feed each student stack
# ══════════════════════════════════════════════════════════════════════

# Zone definitions: (start_layer_inclusive, end_layer_exclusive)
# Total teacher layers: 64 → split into three zones
ZONE_A_START: int = 0
ZONE_A_END: int = 16   # blocks 0-3 (teacher layers 0-15, 16 layers)

ZONE_B_START: int = 16
ZONE_B_END: int = 48   # blocks 4-11 (teacher layers 16-47, 32 layers)

ZONE_C_START: int = 48
ZONE_C_END: int = 64   # blocks 12-15 (teacher layers 48-63, 16 layers)

ZONE_LENGTHS: dict[str, int] = {
    "stack_a": ZONE_A_END - ZONE_A_START,  # 16
    "stack_b": ZONE_B_END - ZONE_B_START,  # 32
    "stack_c": ZONE_C_END - ZONE_C_START,  # 16
}

ZONE_STARTS: dict[str, int] = {
    "stack_a": ZONE_A_START,
    "stack_b": ZONE_B_START,
    "stack_c": ZONE_C_START,
}

# FFN zone-voted extraction: 3 representative teacher layers per zone.
# Early, mid, and late within each zone to capture the full lens topology.
ZONE_A_FFN_LAYERS: tuple[int, ...] = (2, 8, 14)    # early, mid, late in [0-15]
ZONE_B_FFN_LAYERS: tuple[int, ...] = (20, 32, 44)  # early, mid, late in [16-47]
ZONE_C_FFN_LAYERS: tuple[int, ...] = (50, 56, 62)  # early, mid, late in [48-63]

ZONE_FFN_LAYERS: dict[str, tuple[int, ...]] = {
    "stack_a": ZONE_A_FFN_LAYERS,
    "stack_b": ZONE_B_FFN_LAYERS,
    "stack_c": ZONE_C_FFN_LAYERS,
}


# ══════════════════════════════════════════════════════════════════════
# § 4  Dataclass — V14Config
# ══════════════════════════════════════════════════════════════════════

@dataclass
class V14Config:
    """Full v14 student + teacher extraction configuration.

    All architectural choices are recorded here so that a checkpoint can
    be reproduced from this config alone.  The config is intentionally
    flat — all values are concrete primitives, not nested structures.
    """

    # ── Student dimensions ──────────────────────────────────────────
    d_model: int = D_MODEL
    d_ff: int = D_FF
    n_stacks: int = N_STACKS
    n_layers_per_stack: int = N_LAYERS_PER_STACK
    vocab_size: int = VOCAB_SIZE

    # ── SSA (full self-attention) heads ─────────────────────────────
    n_heads: int = N_HEADS
    n_kv_heads: int = N_KV_HEADS
    head_dim: int = HEAD_DIM

    # ── GLA (gated linear attention) heads ──────────────────────────
    gla_n_heads: int = GLA_N_HEADS
    gla_head_dim: int = GLA_HEAD_DIM
    gla_v_head_dim: int = GLA_V_HEAD_DIM

    # ── Teacher (Qwen3.6-27B) ───────────────────────────────────────
    teacher_d_model: int = TEACHER_D_MODEL
    teacher_n_layers: int = TEACHER_N_LAYERS
    teacher_d_ff: int = TEACHER_D_FF
    teacher_vocab: int = TEACHER_VOCAB
    teacher_model_path: str = TEACHER_MODEL_PATH_DEFAULT
    teacher_prefix: str = TEACHER_PREFIX

    # ── Zone mapping ────────────────────────────────────────────────
    zone_a_start: int = ZONE_A_START
    zone_a_end: int = ZONE_A_END
    zone_b_start: int = ZONE_B_START
    zone_b_end: int = ZONE_B_END
    zone_c_start: int = ZONE_C_START
    zone_c_end: int = ZONE_C_END

    # FFN zone-voted layers (tuple fields preserved as tuples)
    zone_a_ffn_layers: tuple[int, ...] = field(default_factory=lambda: ZONE_A_FFN_LAYERS)
    zone_b_ffn_layers: tuple[int, ...] = field(default_factory=lambda: ZONE_B_FFN_LAYERS)
    zone_c_ffn_layers: tuple[int, ...] = field(default_factory=lambda: ZONE_C_FFN_LAYERS)

    # ── Derived properties ──────────────────────────────────────────

    @property
    def n_total_student_layers(self) -> int:
        """Total student layers across all stacks."""
        return self.n_stacks * self.n_layers_per_stack  # 33

    @property
    def ssa_q_proj_out(self) -> int:
        """SSA Q projection output dim (= d_model for square weight)."""
        return self.n_heads * self.head_dim  # 8 * 160 = 1280

    @property
    def ssa_kv_proj_out(self) -> int:
        """SSA K/V projection output dim (GQA)."""
        return self.n_kv_heads * self.head_dim  # 4 * 160 = 640

    @property
    def gla_q_proj_out(self) -> int:
        """GLA Q projection output dim."""
        return self.gla_n_heads * self.gla_head_dim  # 8 * 128 = 1024

    @property
    def gla_v_proj_out(self) -> int:
        """GLA V projection output dim (= d_model)."""
        return self.gla_n_heads * self.gla_v_head_dim  # 8 * 160 = 1280

    @property
    def teacher_model_path_expanded(self) -> Path:
        """Teacher path with ~ expanded."""
        return Path(self.teacher_model_path).expanduser()

    def __post_init__(self) -> None:
        # Sanity-check derived dimensions
        assert self.d_model % self.n_heads == 0, (
            f"d_model ({self.d_model}) must be divisible by n_heads ({self.n_heads})"
        )
        assert self.d_model % 16 == 0, (
            f"d_model ({self.d_model}) must be divisible by 16 for ternary packing"
        )
        assert self.gla_v_proj_out == self.d_model, (
            f"GLA v_proj_out ({self.gla_v_proj_out}) must equal d_model ({self.d_model})"
        )
        assert self.ssa_q_proj_out == self.d_model, (
            f"SSA q_proj_out ({self.ssa_q_proj_out}) must equal d_model ({self.d_model})"
        )
        assert self.zone_a_end == self.zone_b_start, "Zone A/B must be contiguous"
        assert self.zone_b_end == self.zone_c_start, "Zone B/C must be contiguous"
        assert self.zone_c_end == self.teacher_n_layers, (
            f"Zone C must cover all teacher layers (ends at {self.zone_c_end}, "
            f"teacher has {self.teacher_n_layers})"
        )


# ══════════════════════════════════════════════════════════════════════
# § 5  Helper functions
# ══════════════════════════════════════════════════════════════════════

def student_layer_type(layer_idx: int) -> Literal["gla", "ssa"]:
    """Return "gla" or "ssa" for student layer index within a stack (0-based).

    The pattern repeats identically across all three stacks:
      Positions 0,1,2 → gla
      Position 3      → ssa
      Positions 4,5,6 → gla
      Position 7      → ssa
      Positions 8,9   → gla
      Position 10     → ssa

    Args:
        layer_idx: Layer index within a single stack, 0 ≤ layer_idx < N_LAYERS_PER_STACK.

    Returns:
        "gla" or "ssa".

    Raises:
        ValueError: If layer_idx is out of bounds.
    """
    if not (0 <= layer_idx < N_LAYERS_PER_STACK):
        raise ValueError(
            f"layer_idx {layer_idx} out of bounds for N_LAYERS_PER_STACK={N_LAYERS_PER_STACK}"
        )
    return LAYER_PATTERN[layer_idx]


def teacher_layer_for_student(stack: str, layer: int) -> int:
    """Map a student (stack, layer) pair to its source teacher layer index.

    The mapping is a uniform linear interpolation across the zone assigned
    to each stack:

        teacher_layer = zone_start + round(layer * zone_length / n_layers_per_stack)

    This places student layer 0 at the zone start and student layer
    (N_LAYERS_PER_STACK - 1) near (but not at) the zone end, distributing
    attention sources evenly across each zone.

    Args:
        stack: One of "stack_a", "stack_b", "stack_c".
        layer: Student layer index within the stack, 0 ≤ layer < N_LAYERS_PER_STACK.

    Returns:
        Teacher layer index (0-based).

    Raises:
        ValueError: If stack or layer are invalid.

    Examples:
        >>> teacher_layer_for_student("stack_a", 0)
        0                 # zone A start
        >>> teacher_layer_for_student("stack_a", 5)
        7                 # midpoint of zone A
        >>> teacher_layer_for_student("stack_b", 0)
        16                # zone B start
        >>> teacher_layer_for_student("stack_c", 10)
        62                # near zone C end
    """
    if stack not in ZONE_STARTS:
        raise ValueError(
            f"Unknown stack {stack!r}. Must be one of {sorted(ZONE_STARTS.keys())}"
        )
    if not (0 <= layer < N_LAYERS_PER_STACK):
        raise ValueError(
            f"layer {layer} out of bounds for N_LAYERS_PER_STACK={N_LAYERS_PER_STACK}"
        )
    zone_start = ZONE_STARTS[stack]
    zone_length = ZONE_LENGTHS[stack]
    teacher_idx = zone_start + round(layer * zone_length / N_LAYERS_PER_STACK)
    # Clamp to zone bounds (defensive — rounding should not exceed zone_end - 1)
    zone_end = zone_start + zone_length - 1
    return min(teacher_idx, zone_end)


def teacher_layer_type(teacher_layer: int) -> Literal["linear_attn", "full_attn"]:
    """Return the attention type of a teacher layer.

    Qwen3.6-27B uses pattern [L,L,L,F] × 16:
      linear_attn: (layer % 4) in {0, 1, 2}
      full_attn:   (layer % 4) == 3

    Args:
        teacher_layer: Teacher layer index (0-based, 0 ≤ teacher_layer < 64).

    Returns:
        "linear_attn" or "full_attn".
    """
    if teacher_layer % TEACHER_CYCLE == TEACHER_FULL_AT:
        return "full_attn"
    return "linear_attn"


def zone_for_stack(stack: str) -> tuple[int, int]:
    """Return (start, end_exclusive) teacher layer range for a stack.

    Args:
        stack: One of "stack_a", "stack_b", "stack_c".

    Returns:
        (zone_start, zone_end) tuple where zone_end is exclusive.
    """
    if stack not in ZONE_STARTS:
        raise ValueError(
            f"Unknown stack {stack!r}. Must be one of {sorted(ZONE_STARTS.keys())}"
        )
    start = ZONE_STARTS[stack]
    end = start + ZONE_LENGTHS[stack]
    return (start, end)


def ffn_layers_for_stack(stack: str) -> tuple[int, ...]:
    """Return the 3 representative teacher layer indices for FFN zone-voting.

    Args:
        stack: One of "stack_a", "stack_b", "stack_c".

    Returns:
        Tuple of 3 teacher layer indices (early, mid, late within zone).
    """
    if stack not in ZONE_FFN_LAYERS:
        raise ValueError(
            f"Unknown stack {stack!r}. Must be one of {sorted(ZONE_FFN_LAYERS.keys())}"
        )
    return ZONE_FFN_LAYERS[stack]


# ══════════════════════════════════════════════════════════════════════
# § 6  Module-level self-test (runs when imported)
# ══════════════════════════════════════════════════════════════════════

def _self_test() -> None:
    """Verify all derived quantities are consistent at import time."""
    cfg = V14Config()

    # Check total student layers
    assert cfg.n_total_student_layers == 33

    # Check SSA/GLA projection dimensions
    assert cfg.ssa_q_proj_out == 1280
    assert cfg.ssa_kv_proj_out == 640
    assert cfg.gla_q_proj_out == 1024
    assert cfg.gla_v_proj_out == 1280  # must equal d_model

    # Check teacher GLA row splits
    assert TEACHER_GLA_Q_ROWS == 2048
    assert TEACHER_GLA_K_ROWS == 2048
    assert TEACHER_GLA_V_ROWS == 6144
    assert TEACHER_GLA_Q_ROWS + TEACHER_GLA_K_ROWS + TEACHER_GLA_V_ROWS == 10240

    # Check zone coverage
    assert ZONE_A_START == 0
    assert ZONE_C_END == TEACHER_N_LAYERS == 64
    assert ZONE_A_END == ZONE_B_START
    assert ZONE_B_END == ZONE_C_START

    # Check layer type pattern counts
    assert sum(1 for t in LAYER_PATTERN if t == "gla") == 8
    assert sum(1 for t in LAYER_PATTERN if t == "ssa") == 3

    # Check helper functions
    assert student_layer_type(0) == "gla"
    assert student_layer_type(3) == "ssa"
    assert student_layer_type(7) == "ssa"
    assert student_layer_type(10) == "ssa"

    # Check teacher_layer_for_student boundaries
    assert teacher_layer_for_student("stack_a", 0) == 0    # zone A start
    assert teacher_layer_for_student("stack_b", 0) == 16   # zone B start
    assert teacher_layer_for_student("stack_c", 0) == 48   # zone C start

    # Check teacher_layer_type follows [L,L,L,F] pattern
    assert teacher_layer_type(0) == "linear_attn"
    assert teacher_layer_type(3) == "full_attn"
    assert teacher_layer_type(7) == "full_attn"
    assert teacher_layer_type(63) == "full_attn"
    assert teacher_layer_type(62) == "linear_attn"

    # Check FFN zone layers are within bounds
    for stack, layers in ZONE_FFN_LAYERS.items():
        start, end = zone_for_stack(stack)
        for l in layers:
            assert start <= l < end, (
                f"FFN layer {l} for {stack} out of zone [{start}, {end})"
            )


_self_test()
