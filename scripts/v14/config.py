"""
v14 Configuration — Stride-Stack Tree of VSMs, d=1280.

The student is a stride-stack holographic lens architecture:
  - 11 power-of-2 strides (1..1024): O(L×W) attention, ternary, CPU-runnable
  - 3 stacks (A=encode, B=compress, C=reconstruct) in a VSM tree
  - Base plates extracted from Qwen3.6-27B (Apache 2.0)
  - Delta plates (no-block on attention) discover stride-stack corrections
  - After training: fold delta into base → final topology

Key dimensions:
  d_model = 1280 (expanded from v13's 512 to hold more teacher knowledge)
  d_ff = 5120 (4× d_model)
  n_heads = 8 (d_head = 160)
  strides = (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024)

License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


# ══════════════════════════════════════════════════════════════════════
# § 1  Constants
# ══════════════════════════════════════════════════════════════════════

# Core dimensions
D_MODEL = 1280
D_FF = 5120
N_HEADS = 8
D_HEAD = D_MODEL // N_HEADS  # 160
VOCAB_SIZE = 248320  # Qwen3.6-27B BBPE (matches teacher)

# Strides: 16 power-of-2 holographic lenses (2⁰ through 2¹⁵)
# 16 eyes instead of flat attention's 1. Each specializes for a frequency
# band. Self-similar compressor spreads to all strides via wavelet.
# O(L×W) per stride, not O(N²). Max context: s32768 × W(8) = 262K tokens.
STRIDES = tuple(2**i for i in range(16))  # s1..s32768
N_STRIDES = len(STRIDES)  # 16

# Which strides use retrieval (GLA) vs composition (SSA)
# s1-s8:       composition (fine token-level patterns)
# s16-s512:    retrieval (phrase→paragraph pattern matching)
# s1024-s32768: composition (document-level structure)
STRIDE_IS_RETRIEVAL = (
    False, False, False, False,   # s1, s2, s4, s8
    True, True, True, True,       # s16, s32, s64, s128
    True, True,                   # s256, s512
    False, False, False, False, False, False,  # s1024..s32768
)

# Tree of VSMs
N_STACKS = 3
N_BOUNDARIES = N_STACKS - 1

# Combinators (KIBC-DYWH)
N_COMBINATORS = 8
N_TOTAL_COMBINATORS = 16  # + anti-crystal


# ══════════════════════════════════════════════════════════════════════
# § 2  Stack topology — fractal stride bands (MERA)
# ══════════════════════════════════════════════════════════════════════

# Two balanced frequency bands (ascending) + full sweep (descending).
# 4 strides per pass, 2-stride overlap between passes.
# 2-stride overlap at A↔B boundary (s128, s256).
#
# Stack A: ascending fine band (3 passes, s1→s256)
#   Pass 0: [0,4) → s1, s2, s4, s8
#   Pass 1: [2,6) → s4, s8, s16, s32
#   Pass 2: [4,9) → s16, s32, s64, s128, s256  (5 strides — reaches boundary)
#
# Stack B: ascending coarse band (3 passes, s128→s32768)
#   Overlaps Stack A at s128, s256 (register boundary)
#   Pass 3: [7,11)  → s128, s256, s512, s1024
#   Pass 4: [9,13)  → s512, s1024, s2048, s4096
#   Pass 5: [11,16) → s2048, s4096, s8192, s16384, s32768  (5 strides — reaches top)
#
# Stack C: descending, ALL 16 strides (5 passes, coarse→fine)
#   Pass 6:  [12,16) → s32768, s16384, s8192, s4096
#   Pass 7:  [9,13)  → s4096, s2048, s1024, s512
#   Pass 8:  [5,9)   → s512, s256, s128, s64, s32  — wait, that's 4
#   ...
#
# Actually let's keep it clean: 4 strides per pass, 2-stride overlap.
# Stack A: 9 strides (indices 0-8), 4 passes:
#   [0,4), [2,6), [4,8), [6,9)
# Stack B: 9 strides (indices 7-15), 4 passes:
#   [7,11), [9,13), [11,15), [13,16)
# Stack C: all 16 (indices 0-15), 5 passes:
#   [12,16), [8,12), [4,8), [2,6), [0,4)
#
# Stack A: ascending fine band, 4 passes (s1→s256)
#   Pass 0: [0,4)  → s1, s2, s4, s8
#   Pass 1: [2,6)  → s4, s8, s16, s32
#   Pass 2: [4,8)  → s16, s32, s64, s128
#   Pass 3: [6,9)  → s64, s128, s256          (3 strides — boundary)
#
# Stack B: ascending coarse band, 4 passes (s128→s32768)
#   Overlaps A at s128, s256 (indices 7, 8)
#   Pass 4: [7,11)  → s128, s256, s512, s1024
#   Pass 5: [9,13)  → s512, s1024, s2048, s4096
#   Pass 6: [11,15) → s2048, s4096, s8192, s16384
#   Pass 7: [13,16) → s8192, s16384, s32768    (3 strides — top)
#
# Stack C: descending, ALL 16 strides (5 passes, coarse→fine)
#   Pass 8:  [12,16) → s32768, s16384, s8192, s4096
#   Pass 9:  [8,12)  → s4096, s2048, s1024, s512
#   Pass 10: [5,9)   → s256, s128, s64, s32
#   Pass 11: [2,6)   → s32, s16, s8, s4
#   Pass 12: [0,4)   → s8, s4, s2, s1

STACK_A_BANDS = ((0, 4), (2, 6), (4, 8), (6, 9))
# Reduced from 4→2 passes (session 151 kernel insight: Stack B computes
# in already-compressed space PR=5.2, two wider passes cover same range).
STACK_B_BANDS = ((7, 13), (11, 16))
STACK_C_BANDS = ((12, 16), (8, 12), (5, 9), (2, 6), (0, 4))

N_PASSES = len(STACK_A_BANDS) + len(STACK_B_BANDS) + len(STACK_C_BANDS)  # 13


# ══════════════════════════════════════════════════════════════════════
# § 3  Teacher constants (Qwen3.6-27B — extraction source)
# ══════════════════════════════════════════════════════════════════════

TEACHER_D_MODEL = 5120
TEACHER_N_LAYERS = 64
TEACHER_D_FF = 17408
TEACHER_VOCAB = 248320


# ══════════════════════════════════════════════════════════════════════
# § 4  V14Config
# ══════════════════════════════════════════════════════════════════════

@dataclass
class V14Config:
    """Full v14 configuration: student + training + extraction metadata."""

    # ── Student architecture ────────────────────────────────────────
    d_model: int = D_MODEL
    d_ff: int = D_FF
    n_heads: int = N_HEADS
    d_head: int = D_HEAD
    vocab_size: int = VOCAB_SIZE

    # Stride-stack attention
    strides: tuple[int, ...] = STRIDES
    stride_is_retrieval: tuple[bool, ...] = STRIDE_IS_RETRIEVAL
    window: int = 8
    d_state: int = 64           # GLA state dim per head
    decay_init_alpha: float = 1.18
    use_q_mirrors: bool = True
    n_q_mirrors: int = 1
    n_combinators: int = N_COMBINATORS

    # Tree topology
    n_stacks: int = N_STACKS
    stack_a_bands: tuple[tuple[int, int], ...] = STACK_A_BANDS
    stack_b_bands: tuple[tuple[int, int], ...] = STACK_B_BANDS
    stack_c_bands: tuple[tuple[int, int], ...] = STACK_C_BANDS

    # Algedonic
    alg_dim: int = 32
    alg_modulation_range: float = 2.0

    # ── VSM control ─────────────────────────────────────────────────
    d_identity: int = 128       # S5 identity state (v13 was 64, scaled with d_model)
    identity_clip: float = 2.0
    n_regulation_surfaces: int = 4
    s5_gru_bias_init: float = 2.0
    s4_n_proposals: int = 4
    s4_hidden_dim: int = 128    # scaled from v13's 64
    s2_p_gain_init: float = 0.5
    s2_d_gain_init: float = 0.3
    fire_alarm_bias_init: float = -2.0

    # ── Crystal lattice ─────────────────────────────────────────────
    use_relational_loss: bool = True
    rel_lambda: float = 5.0
    crystal_direct_lambda: float = 3.0
    crystal_direct_lambda_start: float = 10.0
    crystal_warmup_steps: int = 1000
    use_parity_loss: bool = True
    parity_lambda: float = 1.0
    parity_zone_lambdas: tuple[float, ...] = (0.0, 1.0, 0.0)

    # ── Spectral φ ──────────────────────────────────────────────────
    use_spectral_loss: bool = True
    spectral_lambda: float = 1.0
    spectral_target_ratio: float = 0.6299
    spectral_target_std: float = 0.019

    # ── Training ────────────────────────────────────────────────────
    dropout: float = 0.0       # no dropout for v14
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
    checkpoint_dir: str = "checkpoints/v14"
    extracted_model_path: str = "checkpoints/v14-extracted/model.npz"

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
        return (len(self.stack_a_bands)
                + len(self.stack_b_bands)
                + len(self.stack_c_bands))

    @property
    def tokens_per_step(self) -> int:
        return self.batch_size * self.grad_accum * self.seq_len

    def __post_init__(self):
        assert self.d_model % self.n_heads == 0
        assert self.d_model % 16 == 0
        assert len(self.stride_is_retrieval) == len(self.strides)


# ══════════════════════════════════════════════════════════════════════
# § 5  Self-test
# ══════════════════════════════════════════════════════════════════════

def _self_test():
    cfg = V14Config()
    assert cfg.d_model == 1280
    assert cfg.d_head == 160
    assert cfg.n_strides == 16
    assert cfg.n_passes == 11  # reduced from 13: Stack B 4→2 passes
    assert cfg.n_heads * cfg.d_head == cfg.d_model
    assert cfg.d_ff == 4 * cfg.d_model
    assert sum(1 for r in cfg.stride_is_retrieval if r) == 6   # 6 retrieval strides
    assert sum(1 for r in cfg.stride_is_retrieval if not r) == 10  # 10 composition strides
    assert len(cfg.stride_is_retrieval) == cfg.n_strides
    print("config.py self-test: ✓")


_self_test()
