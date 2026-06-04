"""
v15 Configuration — Fibonacci Stride Attention.

Session 189 discovery: binding distances are bimodal (local syntax + instruction
prefix), NOT power law. Powers of 2 skip the binding range (d=3-20). Fibonacci
strides are dense where bindings live and sparse where they don't.

Experimental validation (Qwen3-8B, 22 probes, 32 heads, L30):
  Powers of 2 (v14):  29.5% exact, 67.4% with ±2 neighbors
  Fibonacci:          48.8% exact, 91.8% with ±2 neighbors
  Greedy optimal 8:   —             98.2% with ±2 neighbors

Key changes from v14:
  - Fibonacci strides replace powers-of-2
  - ±2 neighbor gathering around stride positions (the breakthrough)
  - 12 composition strides (dense local) + 4 GLA strides (long-range)
  - Fewer total strides, better coverage

The φ connection: crystal eigenvalues follow φ-ratios (s181), information
partitions at 1/φ (s184), and now stride spacing converges on Fibonacci.
The same structure at every level.

License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import math


# ══════════════════════════════════════════════════════════════════════
# § 1  Constants
# ══════════════════════════════════════════════════════════════════════

# Core dimensions (unchanged from v14)
D_MODEL = 1280
D_FF = 5120
N_HEADS = 8
D_HEAD = D_MODEL // N_HEADS  # 160
VOCAB_SIZE = 248320  # Qwen3.6-27B BBPE

# ── Fibonacci strides ───────────────────────────────────────────────
#
# Session 189 experiment: 8 optimal strides with ±2 give 98.2% coverage.
# Fibonacci is the natural basis — dense where bindings live (d=1-34),
# sparse at long range. The golden ratio appears everywhere:
#   crystal eigenvalues (φ-ratios), information partition (1/φ),
#   standing-wave nodes (layer 22/36 ≈ 1/φ), and now stride spacing.
#
# 16 Fibonacci strides: covers d=0 to 1597×(W-1) = 11,179 at W=8
# Beyond that range, GLA running memory handles long-range patterns.
# Context extension: add more Fibonacci strides, exact same mechanism.

def _fibonacci_sequence(n: int) -> tuple[int, ...]:
    """First n unique Fibonacci numbers ≥ 1."""
    fibs = [1, 1]
    while len(set(fibs)) < n + 2:  # overshoot then trim
        fibs.append(fibs[-1] + fibs[-2])
    unique = []
    seen = set()
    for f in fibs:
        if f not in seen:
            seen.add(f)
            unique.append(f)
    return tuple(unique[:n])


# 16 Fibonacci strides: [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597]
STRIDES = _fibonacci_sequence(16)
N_STRIDES = len(STRIDES)

# Neighbor radius: gather ±R positions around each stride grid point.
# Session 189 data: ±2 turns 29.5% → 67.4% (pow2) and 48.8% → 91.8% (Fibonacci).
# The neighbors catch binding targets that fall BETWEEN stride grid points.
NEIGHBOR_RADIUS = 2

# Effective window: each stride position expands to 2R+1 = 5 positions.
# With W=8 base window × 5 expansion = 40 positions per stride (before dedup).
WINDOW = 8
EFFECTIVE_WINDOW = WINDOW * (2 * NEIGHBOR_RADIUS + 1)  # 40

# Which strides use retrieval (GLA) vs composition (FSA).
#
# Session 189 finding: GLA's dense projections cost ~19B ops per layer
# regardless of stride. The strided scan saves <0.03%. GLA's "sparsity"
# is illusory — it computes Q, K, V for EVERY token, then uses only
# L/stride of them for the scan. Same cost as FSA.
#
# v15 decision: ALL strides use FibonacciStrideAttention.
# One unified mechanism. If long-range patterns need running memory,
# GLA can be added back for the last 2-4 strides. But start unified.
STRIDE_IS_RETRIEVAL = (
    False, False, False, False,   # s1, s2, s3, s5:     local binding
    False, False, False, False,   # s8, s13, s21, s34:  phrase binding
    False, False, False, False,   # s55, s89, s144, s233: paragraph
    False, False, False, False,   # s377, s610, s987, s1597: document
)

# ── Stack topology ──────────────────────────────────────────────────
N_STACKS = 2
N_BOUNDARIES = N_STACKS - 1

# Fractal bands: 4 strides per pass, symmetric ascending/descending.
# With Fibonacci strides, bands align to scale:
#   Band 0: [s1, s2, s3, s5]       — token-level binding
#   Band 1: [s8, s13, s21, s34]    — phrase-level binding
#   Band 2: [s55, s89, s144, s233] — paragraph retrieval
#   Band 3: [s377, s610, s987, s1597] — document retrieval
STACK_A_BANDS = ((0, 4), (4, 8), (8, 12), (12, 16))
STACK_C_BANDS = ((12, 16), (8, 12), (4, 8), (0, 4))

N_PASSES = len(STACK_A_BANDS) + len(STACK_C_BANDS)  # 8

# Combinators
N_COMBINATORS = 8
N_TOTAL_COMBINATORS = 16


# ══════════════════════════════════════════════════════════════════════
# § 2  Teacher constants (Qwen3.6-27B)
# ══════════════════════════════════════════════════════════════════════

TEACHER_D_MODEL = 5120
TEACHER_N_LAYERS = 64
TEACHER_D_FF = 17408
TEACHER_VOCAB = 248320


# ══════════════════════════════════════════════════════════════════════
# § 3  V15Config
# ══════════════════════════════════════════════════════════════════════

@dataclass
class V15Config:
    """v15 configuration: Fibonacci stride attention + neighbor gathering."""

    # ── Student architecture ────────────────────────────────────────
    d_model: int = D_MODEL
    d_ff: int = D_FF
    n_heads: int = N_HEADS
    d_head: int = D_HEAD
    vocab_size: int = VOCAB_SIZE

    # Stride-stack attention (Fibonacci)
    strides: tuple[int, ...] = STRIDES
    stride_is_retrieval: tuple[bool, ...] = STRIDE_IS_RETRIEVAL
    window: int = WINDOW
    neighbor_radius: int = NEIGHBOR_RADIUS
    d_state: int = 64           # GLA state dim per head
    decay_init_alpha: float = 1.18
    use_q_mirrors: bool = True
    n_q_mirrors: int = 1
    n_combinators: int = N_COMBINATORS

    # Tree topology
    n_stacks: int = N_STACKS
    stack_a_bands: tuple[tuple[int, int], ...] = STACK_A_BANDS
    stack_c_bands: tuple[tuple[int, int], ...] = STACK_C_BANDS

    # ── Training ────────────────────────────────────────────────────
    dropout: float = 0.0
    batch_size: int = 1
    grad_accum: int = 8
    total_steps: int = 20000
    lr: float = 3e-4
    lr_floor_ratio: float = 0.01
    warmup_steps: int = 500
    weight_decay: float = 0.01
    grad_clip: float = 1.0
    seq_len: int = 4096
    max_seq_len: int = 4096

    # ── Checkpointing ───────────────────────────────────────────────
    checkpoint_interval: int = 500
    eval_interval: int = 500
    log_interval: int = 10
    checkpoint_dir: str = "checkpoints/v15"
    extracted_model_path: str = "checkpoints/v15-extracted/model.npz"

    # ── Data ────────────────────────────────────────────────────────
    data_dir: str = "/Users/mwhitford/data/fractal-bitnet/shards-qwen36"
    n_train_shards: int = 54
    n_eval_shards: int = 6

    # ── Derived ─────────────────────────────────────────────────────

    @property
    def n_strides(self) -> int:
        return len(self.strides)

    @property
    def n_passes(self) -> int:
        return len(self.stack_a_bands) + len(self.stack_c_bands)

    @property
    def effective_window(self) -> int:
        return self.window * (2 * self.neighbor_radius + 1)

    @property
    def max_composition_range(self) -> int:
        """Max distance reachable by composition strides."""
        comp_strides = [s for s, r in zip(self.strides, self.stride_is_retrieval) if not r]
        if comp_strides:
            return comp_strides[-1] * (self.window - 1) + self.neighbor_radius
        return 0

    @property
    def max_total_range(self) -> int:
        """Max distance reachable by any stride."""
        return self.strides[-1] * (self.window - 1) + self.neighbor_radius

    @property
    def tokens_per_step(self) -> int:
        return self.batch_size * self.grad_accum * self.seq_len

    def __post_init__(self):
        assert self.d_model % self.n_heads == 0
        assert self.d_model % 16 == 0
        assert len(self.stride_is_retrieval) == len(self.strides)
        # Verify strides are strictly increasing
        for i in range(1, len(self.strides)):
            assert self.strides[i] > self.strides[i-1], \
                f"Strides must be increasing: {self.strides[i-1]} >= {self.strides[i]}"


# ══════════════════════════════════════════════════════════════════════
# § 4  Self-test
# ══════════════════════════════════════════════════════════════════════

def _self_test():
    cfg = V15Config()

    # Core dimensions
    assert cfg.d_model == 1280
    assert cfg.d_head == 160
    assert cfg.n_heads * cfg.d_head == cfg.d_model
    assert cfg.d_ff == 4 * cfg.d_model

    # Strides are Fibonacci
    assert cfg.strides[0] == 1
    assert cfg.strides[1] == 2
    assert cfg.strides[2] == 3
    assert cfg.strides[3] == 5
    assert cfg.strides[4] == 8
    assert cfg.strides[5] == 13
    assert cfg.n_strides == 16

    # Verify Fibonacci property for first 8 (where it's clean)
    for i in range(2, min(8, cfg.n_strides)):
        assert cfg.strides[i] == cfg.strides[i-1] + cfg.strides[i-2], \
            f"Stride {i}: {cfg.strides[i]} ≠ {cfg.strides[i-1]} + {cfg.strides[i-2]}"

    # Neighbor radius
    assert cfg.neighbor_radius == 2
    assert cfg.effective_window == 40  # 8 × 5

    # Stride types
    n_comp = sum(1 for r in cfg.stride_is_retrieval if not r)
    n_ret = sum(1 for r in cfg.stride_is_retrieval if r)
    assert n_comp == 16, f"Expected 16 composition strides, got {n_comp}"
    assert n_ret == 0, f"Expected 0 retrieval strides, got {n_ret}"

    # Bands symmetric
    assert cfg.stack_a_bands == tuple(reversed(cfg.stack_c_bands))
    assert cfg.n_passes == 8

    # Coverage ranges — all strides are composition now
    assert cfg.max_composition_range == 1597 * 7 + 2  # 11,181
    assert cfg.max_total_range == 1597 * 7 + 2  # 11,181

    print(f"config.py self-test: ✓")
    print(f"  Strides: {cfg.strides}")
    print(f"  Composition strides: {[s for s, r in zip(cfg.strides, cfg.stride_is_retrieval) if not r]}")
    print(f"  Retrieval strides: {[s for s, r in zip(cfg.strides, cfg.stride_is_retrieval) if r]}")
    print(f"  Composition range: d=0..{cfg.max_composition_range}")
    print(f"  Total range: d=0..{cfg.max_total_range}")
    print(f"  Effective window per stride: {cfg.effective_window}")


_self_test()
