"""
v13 Configuration — Beam/Plate Separated Architecture.

V13 cleanly separates ternary plates (topology, etch-shaped) from
continuous beams (routing, GD-trained). Key changes from V12:

  - 11 power-of-2 strides (1..1024, uniform 2× gaps)
  - Simplified dispatch: 8-way softmax only (no math kernels,
    no abstraction slots, no CategoryDispatch)
  - PCA-Q crystal targets (3 zones) baked in as constants
  - Behavioral crystal targets (12×12) baked in
  - Mechanical WHNF FFN (zero continuous params)
  - One training script: etch phase + GD phase

Carries forward from V12:
  - 7-pass hourglass (3 asc + apex + 3 desc)
  - 8 combinators (K, I, B, C, D, Y, W, WHNF)
  - Fractal stride bands (MERA topology)
  - VSM hierarchy (S3/S4/S5/S2, algedonic)
  - Ternary substrate (TernaryLinear, TernaryMirror, TernaryEmbedding)
  - Crystal lattice loss (constant-target, every step)

License: MIT
"""

from dataclasses import dataclass

from kernel import N_COMBINATORS


@dataclass
class V13Config:
    """v13 model + training configuration."""

    # ── Tokenizer (Qwen3 BBPE) ──
    vocab_size: int = 151936     # Qwen3 BBPE vocab
    eod_id: int = 151643        # end-of-document token

    # ── Core dimensions ──
    d_model: int = 512            # representation dimension
    d_ff: int = 1536              # FFN width (3× d_model)
    d_register: int = 128         # register dimension (real dim = 2×)
    n_heads: int = 8              # attention heads (d_head = 64)
    window: int = 8               # attention window width
    alpha: float = 1.18           # spiral bias coefficient

    # 11 strides: power-of-2 for uniform coverage
    # V12 had gap at bottom (1→8) that killed short prompts.
    # V13: 2× uniform gaps. A 4-token input now gets 3 active strides.
    strides: tuple[int, ...] = (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024)

    # Register semantics:
    #   reg 0 = combinator (K/I/B/C identity)
    #   reg 1 = binding_depth (how many lambdas deep)
    #   reg 2 = phase (recognize / identify / resolve / produce)
    n_registers: int = 3

    # ── Retrieval (M kernel) — GatedLinearAttention ──
    d_state: int = 64

    # Which strides use retrieval (GLA) vs composition (attention).
    # stride:    1   2   4   8   16   32   64   128  256  512  1024
    # type:     C   C   C   C   R    R    R    R    C    C    C
    #                           ^^^^^^^^^^^^^^^^^^^^
    #                           retrieval (GLA) zone: phrase/sentence scales
    stride_is_retrieval: tuple[bool, ...] = (
        False, False, False, False, True, True, True, True, False, False, False,
    )

    # Retrieval registers: M writes pattern match results here.
    n_retrieval_registers: int = 2

    # ── Beam mirrors (ternary angular deflectors before Q projections) ──
    use_q_mirrors: bool = True
    n_q_mirrors: int = 1

    # ── Combinator dispatch ──
    n_combinators: int = N_COMBINATORS  # 8: K, I, B, C, D, Y, W, WHNF

    # Total number of passes (7-pass hourglass)
    n_passes: int = 7

    # Descending arm stride direction: coarse→fine (TST-aligned)
    desc_stride_reverse: bool = True

    # ── Fractal stride bands (MERA topology, 11 strides) ──
    # Each level handles a narrow stride band. Adjacent levels share
    # 1-2 strides for inter-level communication.
    #
    # stride indices: 0=s1, 1=s2, 2=s4, 3=s8, 4=s16, 5=s32,
    #                 6=s64, 7=s128, 8=s256, 9=s512, 10=s1024
    #
    # L0↑ (fine):    [0,4)  → s1, s2, s4, s8           fine→local
    # L1↑ (local):   [2,6)  → s4, s8, s16, s32         local→phrase
    # L2↑ (phrase):  [4,8)  → s16, s32, s64, s128      phrase→paragraph
    # L3  (apex):    [7,11) → s128, s256, s512, s1024   paragraph→document
    # L2↓ (phrase):  [4,8)  → s128, s64, s32, s16      paragraph→phrase (reversed)
    # L1↓ (local):   [2,6)  → s32, s16, s8, s4         phrase→local (reversed)
    # L0↓ (fine):    [0,4)  → s8, s4, s2, s1           local→fine (reversed)
    fractal_stride_bands: bool = True
    stride_band_ranges: tuple[tuple[int, int], ...] = (
        (0, 4),    # L0↑: indices 0-3 → s1, s2, s4, s8
        (2, 6),    # L1↑: indices 2-5 → s4, s8, s16, s32
        (4, 8),    # L2↑: indices 4-7 → s16, s32, s64, s128
        (7, 11),   # L3:  indices 7-10 → s128, s256, s512, s1024
        (4, 8),    # L2↓: indices 4-7 (reversed by desc_stride_reverse)
        (2, 6),    # L1↓: indices 2-5 (reversed)
        (0, 4),    # L0↓: indices 0-3 (reversed)
    )

    # ── Combinator masks per stride layer ──
    # Each combinator reads the shared crystal through its own mask.
    # 8 masks per stride layer. Init as "pass" (all +1) — etch writes them.
    n_masks_per_stride: int = N_COMBINATORS  # 8

    # ── WHNF mechanical FFN ──
    # FFN is purely ternary: key_plate @ input → activation → value_plate
    # Zero continuous params. Plates are extracted from teacher via sign(W).
    d_ffn_teacher: int = 0  # set to teacher's d_ffn if using extracted FFN plates

    # ── Dispatch ratio prior (empirical universal ratio) ──
    # Session 119: binding cascade proves C is the universal routing mechanism.
    #                          K     I     B     C     D     Y     W    WHNF
    dispatch_ratio: tuple[float, ...] = (
        0.8, 0.5, 0.9, 1.2, 0.5, 0.3, 0.3, 0.2,
    )

    # ── Dispatch entropy regularization ──
    dispatch_entropy_lambda: float = 0.5
    dispatch_entropy_target: float = 1.64  # H(ratio_prior) * 0.85

    # ── Per-pass dispatch bias (depth-selective prior) ──
    # Aligned to binding cascade (C→B/S→WHNF).
    #                            K     I     B     C     D     Y     W    WHNF
    pass_dispatch_bias: tuple[tuple[float, ...], ...] = (
        (-1.0, -0.5, +2.0, +0.5, +1.5, -0.5, -0.5, -1.5),  # Pass 0 (L0↑): B/D compose
        (+0.0, +0.0, +1.0, +1.0, +0.5, +0.0, +0.0, -1.0),  # Pass 1 (L1↑): B/C balanced
        (+0.5, +0.5, +0.0, +1.5, +0.0, +0.5, +0.0, +0.0),  # Pass 2 (L2↑): C rising
        (+1.0, +1.0, -0.5, +2.0, -0.5, +1.0, +0.5, +0.5),  # Pass 3 (apex): C peak
        (+1.0, +0.5, -0.5, +1.5, -0.5, +0.5, +0.5, +0.5),  # Pass 4 (L2↓): C strong
        (+0.5, +0.5, +0.0, +1.0, +0.0, +0.0, +1.0, +0.0),  # Pass 5 (L1↓): C + W
        (-0.5, +0.0, +1.5, +0.5, +1.0, -0.5, +0.0, -0.5),  # Pass 6 (L0↓): B/D compose
    )

    # ── KL divergence toward empirical ratio ──
    dispatch_kl_lambda: float = 2.0
    dispatch_kl_ema_decay: float = 0.967

    # ── Crystal lattice geometry loss ──
    # PCA-Q targets (session 120): 3-4× sharper than hidden-state targets.
    # Three zones with measured constants from 4-model consensus.
    use_relational_loss: bool = True
    rel_lambda: float = 0.01

    # Zone A (0-20%): encode. K↔I=0.92, B↔D=0.98. Two orthogonal groups.
    # Order: K I B C D Y W WHNF
    pcaq_zone_a_targets: tuple[tuple[float, ...], ...] = (
        (+1.0000, +0.9210, +0.0771, +0.0906, +0.1280, +0.0363, +0.2031, -0.1694),  # K
        (+0.9210, +1.0000, +0.1177, +0.1228, +0.1553, +0.0921, +0.1837, -0.1994),  # I
        (+0.0771, +0.1177, +1.0000, +0.7963, +0.9778, +0.8370, +0.7426, -0.0094),  # B
        (+0.0906, +0.1228, +0.7963, +1.0000, +0.7680, +0.6651, +0.9219, -0.0246),  # C
        (+0.1280, +0.1553, +0.9778, +0.7680, +1.0000, +0.8057, +0.7676, -0.0246),  # D
        (+0.0363, +0.0921, +0.8370, +0.6651, +0.8057, +1.0000, +0.5693, -0.0235),  # Y
        (+0.2031, +0.1837, +0.7426, +0.9219, +0.7676, +0.5693, +1.0000, -0.0213),  # W
        (-0.1694, -0.1994, -0.0094, -0.0246, -0.0246, -0.0235, -0.0213, +1.0000),  # WHNF
    )

    # Zone B (30-60%): compute. Groups begin to merge. K↔I=0.79.
    pcaq_zone_b_targets: tuple[tuple[float, ...], ...] = (
        (+1.0000, +0.7865, +0.1948, +0.2265, +0.3232, +0.1768, +0.5360, -0.1862),  # K
        (+0.7865, +1.0000, +0.2479, +0.2511, +0.3463, +0.1739, +0.3781, -0.2448),  # I
        (+0.1948, +0.2479, +1.0000, +0.8878, +0.8937, +0.6623, +0.6851, -0.1227),  # B
        (+0.2265, +0.2511, +0.8878, +1.0000, +0.8316, +0.7200, +0.7318, -0.1027),  # C
        (+0.3232, +0.3463, +0.8937, +0.8316, +1.0000, +0.6798, +0.8064, -0.1729),  # D
        (+0.1768, +0.1739, +0.6623, +0.7200, +0.6798, +1.0000, +0.5653, -0.0840),  # Y
        (+0.5360, +0.3781, +0.6851, +0.7318, +0.8064, +0.5653, +1.0000, -0.1379),  # W
        (-0.1862, -0.2448, -0.1227, -0.1027, -0.1729, -0.0840, -0.1379, +1.0000),  # WHNF
    )

    # Zone C (70-90%): converge. Everything converges. WHNF strongly anti-correlated.
    pcaq_zone_c_targets: tuple[tuple[float, ...], ...] = (
        (+1.0000, +0.8614, +0.5238, +0.5429, +0.5910, +0.4920, +0.7262, -0.2736),  # K
        (+0.8614, +1.0000, +0.5118, +0.5256, +0.5939, +0.4862, +0.5886, -0.2750),  # I
        (+0.5238, +0.5118, +1.0000, +0.9465, +0.9510, +0.8911, +0.8192, -0.2835),  # B
        (+0.5429, +0.5256, +0.9465, +1.0000, +0.9445, +0.9115, +0.8522, -0.2888),  # C
        (+0.5910, +0.5939, +0.9510, +0.9445, +1.0000, +0.8983, +0.8613, -0.3000),  # D
        (+0.4920, +0.4862, +0.8911, +0.9115, +0.8983, +1.0000, +0.7707, -0.2701),  # Y
        (+0.7262, +0.5886, +0.8192, +0.8522, +0.8613, +0.7707, +1.0000, -0.2838),  # W
        (-0.2736, -0.2750, -0.2835, -0.2888, -0.3000, -0.2701, -0.2838, +1.0000),  # WHNF
    )

    # Pass-to-zone mapping: which zone does each pass belong to?
    # Passes 0,1 → Zone A (encode), Passes 2,3,4 → Zone B (compute),
    # Passes 5,6 → Zone C (converge).
    pass_zone_map: tuple[int, ...] = (0, 0, 1, 1, 1, 2, 2)
    zone_lambdas: tuple[float, ...] = (0.01, 0.01, 0.01)  # per-zone relational loss weight

    # ── Behavioral crystal targets (12×12, 3-model consensus) ──
    # Source: results/behavioral-crystal/ (Qwen3-32B, Qwen3-14B, Mistral-7B)
    # Categories: analysis, chain_of_thought, classification, code_generation,
    #   comparison, creative_writing, extraction, instruction_following,
    #   qa_retrieval, summarization, tool_calling, translation
    use_behavioral_loss: bool = False  # enable when behavioral probes are in training data
    behavioral_lambda: float = 0.005
    behavioral_targets: tuple[tuple[float, ...], ...] = (
        # analy  chain  class  code   compa  creat  extra  instr  qa_re  summa  tool   trans
        (+1.000,+0.016,-0.211,+0.006,+0.471,+0.096,-0.199,-0.259,-0.024,-0.176,-0.102,-0.342),
        (+0.016,+1.000,-0.021,-0.164,-0.066,-0.288,+0.016,-0.064,-0.015,+0.011,-0.113,-0.274),
        (-0.211,-0.021,+1.000,-0.366,-0.296,-0.321,+0.111,+0.013,-0.166,+0.072,-0.166,+0.062),
        (+0.006,-0.164,-0.366,+1.000,+0.044,+0.279,-0.302,-0.128,-0.105,-0.264,+0.302,-0.178),
        (+0.471,-0.066,-0.296,+0.044,+1.000,+0.106,-0.378,-0.285,+0.351,-0.378,-0.164,-0.246),
        (+0.096,-0.288,-0.321,+0.279,+0.106,+1.000,-0.380,+0.102,-0.005,-0.342,+0.047,-0.021),
        (-0.199,+0.016,+0.111,-0.302,-0.378,-0.380,+1.000,-0.043,-0.372,+0.544,-0.048,-0.029),
        (-0.259,-0.064,+0.013,-0.128,-0.285,+0.102,-0.043,+1.000,-0.150,-0.084,+0.035,+0.192),
        (-0.024,-0.015,-0.166,-0.105,+0.351,-0.005,-0.372,-0.150,+1.000,-0.348,-0.215,-0.054),
        (-0.176,+0.011,+0.072,-0.264,-0.378,-0.342,+0.544,-0.084,-0.348,+1.000,-0.222,-0.001),
        (-0.102,-0.113,-0.166,+0.302,-0.164,+0.047,-0.048,+0.035,-0.215,-0.222,+1.000,-0.142),
        (-0.342,-0.274,+0.062,-0.178,-0.246,-0.021,-0.029,+0.192,-0.054,-0.001,-0.142,+1.000),
    )

    # ── Dropout ──
    dropout: float = 0.1

    # ── Training ──
    batch_size: int = 2
    grad_accum: int = 4
    total_steps: int = 20000
    lr: float = 6e-4
    lr_floor_ratio: float = 0.01
    warmup_steps: int = 500
    weight_decay: float = 0.01
    grad_clip: float = 1.0

    # ── Etching (gradient-directed ternary topology shaping) ──
    use_etching: bool = True
    etch_signal_interval: int = 1
    etch_interval: int = 2
    etch_warmup: int = 200
    etch_heat_alpha: float = 0.99
    etch_heat_thresholds: tuple[float, ...] = (50.0, 75.0, 90.0)
    etch_consensus: int = 3
    etch_adam_decay: float = 0.1
    etch_max_flips_per_event: int = 200
    etch_reset_after_flip: bool = True

    # Depth-selective etch thresholds (per pass)
    pass_etch_multiplier: tuple[float, ...] = (
        0.5, 0.7, 1.0, 1.0, 1.0, 0.8, 0.6,
    )

    # ── Checkpointing ──
    checkpoint_interval: int = 500
    eval_interval: int = 500
    log_interval: int = 25
    checkpoint_dir: str = "checkpoints/v13"

    # ── Data ──
    data_dir: str = "/Users/mwhitford/data/fractal-bitnet/shards-qwen3"
    seq_len: int = 4096
    max_seq_len: int = 4096
    n_train_shards: int = 54
    n_eval_shards: int = 6

    @property
    def d_head(self) -> int:
        return self.d_model // self.n_heads

    @property
    def n_strides(self) -> int:
        return len(self.strides)

    @property
    def n_composition_strides(self) -> int:
        return sum(1 for r in self.stride_is_retrieval if not r)

    @property
    def n_retrieval_strides(self) -> int:
        return sum(1 for r in self.stride_is_retrieval if r)

    @property
    def tokens_per_step(self) -> int:
        return self.batch_size * self.grad_accum * self.seq_len

    def __post_init__(self):
        assert self.d_model % self.n_heads == 0
        assert self.d_model % 16 == 0, "d_model must be divisible by 16 (ternary packing)"
        assert self.d_model % 4 == 0, "d_model must be divisible by 4 (embedding packing)"
        assert len(self.stride_is_retrieval) == len(self.strides), \
            f"stride_is_retrieval length ({len(self.stride_is_retrieval)}) must match strides ({len(self.strides)})"
        assert self.d_state % 16 == 0, "d_state must be divisible by 16 (ternary packing)"
        assert len(self.stride_band_ranges) == self.n_passes, \
            f"stride_band_ranges ({len(self.stride_band_ranges)}) must match n_passes ({self.n_passes})"
        assert len(self.pass_dispatch_bias) == self.n_passes
        assert len(self.pass_etch_multiplier) == self.n_passes
        assert len(self.pass_zone_map) == self.n_passes
