"""
v12 Configuration — KIBC + M (retrieval) dual-layer architecture.

V12 adds the M (match/retrieval) kernel as a *layer type*, not a 5th
combinator in the KIBC dispatch softmax. The insight from session 095:
Qwen3.6-35B-A3B accidentally separates composition (full attention at
every 4th layer) from retrieval (GatedDeltaNet between). The induction
circuit (J=0.176 with everything else) lives exclusively in the linear
attention layers — it's mechanistically independent.

V12 makes this separation intentional:
  - Composition layers: StrideStack (windowed attention) — KIBC lives here
  - Retrieval layers: GatedLinearAttention — M lives here
  - HybridStrideStack: interleaves both, configurable per stride

Design principle — SEPARATION ENABLES HOLOGRAPHY (session 096):
  Cross-architecture analysis (Pythia, Qwen3, SmolLM3, 7 models) proved:
    - MLP/FFN: universally holographic (score 0.97, CV 0.025)
    - Attention output: universally holographic (score 0.94, CV 0.020)
    - Separate Q/K/V: holographic (score 0.92, Qwen3/SmolLM3)
    - Fused QKV: magnitude-dependent (score 0.60, Pythia)
  Multiplexing functions into shared weights forces magnitudes to act
  as "lenses" steering beams between subspaces. Separation lets each
  weight encode one function as pure sign topology.
  → V12: every projection is separate. Every weight has one job.

Architecture:
  Ascending arm: HybridStrideStack (interleaved composition + retrieval)
  Descending arm: KIBC combinator dispatch + retrieval register access
  7 passes: L0↑ → L1↑ → L2↑ → L3_apex → L2↓ → L1↓ → L0↓
  Output: tied embedding projection → next-token prediction

Carries forward from v11:
  - KIBC combinator basis (4-way softmax, not 5)
  - VSM hierarchy (S1-S5, algedonic, CycleContinue)
  - Holographic loss (progressive intermediate decoding)
  - Abstraction slots (S4→S5 proposals)
  - Fractal stride bands (MERA topology)

License: MIT
"""

from dataclasses import dataclass, field

from kernel import N_COMBINATORS


@dataclass
class V12Config:
    """v12 model + training configuration."""

    # ── Tokenizer (Qwen3 BBPE) ──
    vocab_size: int = 151936     # Qwen3 BBPE vocab
    eod_id: int = 151643        # end-of-document token

    # ── Core dimensions ──
    d_model: int = 512            # representation dimension
    d_ff: int = 1536              # prep FFN width (3× d_model)
    d_ff_consolidate: int = 2048  # consolidate FFN width (wider)
    d_register: int = 128         # register dimension (real dim = 2×)
    n_heads: int = 8              # attention heads (d_head = 64)
    window: int = 8               # attention window width
    alpha: float = 1.18           # spiral bias coefficient

    # 9 strides: the full scale hierarchy proven in v6
    strides: tuple[int, ...] = (1, 8, 16, 32, 64, 128, 256, 512, 1024)

    # Register semantics:
    #   reg 0 = combinator (K/I/B/C identity)
    #   reg 1 = binding_depth (how many lambdas deep)
    #   reg 2 = phase (recognize / identify / resolve / produce)
    n_registers: int = 3

    # ── Retrieval (M kernel) — GatedLinearAttention ──
    # d_state: dimension of the running memory matrix per head.
    # The GLA memory is (n_heads, d_head, d_state) — keys project
    # to d_state, values to d_head. Total memory = n_heads × d_head × d_state.
    # At d_state=64 with 8 heads and d_head=64: 8×64×64 = 32K params of state.
    d_state: int = 64

    # Which strides use retrieval (GLA) vs composition (attention).
    # Tuple of booleans, one per stride. True = retrieval layer.
    # Default: small strides (local patterns) use composition,
    # medium strides use retrieval (pattern matching across phrases),
    # large strides use composition (structural composition).
    #
    # Inspired by Qwen3.6 layout: GatedDeltaNet at 3/4 of layers,
    # full attention at every 4th. We're more conservative — 3 of 9
    # strides are retrieval, focusing on the phrase/sentence scales
    # where induction patterns live empirically.
    #
    # stride:    1     8    16    32    64   128   256   512  1024
    # type:     comp  comp  ret   ret   ret  comp  comp  comp comp
    stride_is_retrieval: tuple[bool, ...] = (
        False, False, True, True, True, False, False, False, False,
    )

    # Retrieval registers: M writes pattern match results here.
    # The descending arm reads them alongside existing registers.
    # n_retrieval_registers: how many retrieval slots M can write to.
    n_retrieval_registers: int = 2

    # ── Combinator dispatch ──
    n_combinators: int = N_COMBINATORS  # 4: K, I, B, C (M is NOT here)

    # Self-regulating descending cycles (unchanged from v11)
    desc_max_cycles: int = 3

    # Descending arm stride direction: coarse→fine (TST-aligned)
    desc_stride_reverse: bool = True

    # Fractal stride bands (MERA topology)
    # v12: 7 passes (3 asc + apex + 3 desc) — symmetric hourglass.
    # Each level handles a narrow stride band. Adjacent levels share
    # 1-2 strides for inter-level communication.
    #
    # stride indices: 0=s1, 1=s8, 2=s16, 3=s32, 4=s64, 5=s128, 6=s256, 7=s512, 8=s1024
    #
    # L0↑ (fine):     [0,1,2]     → s1,s8,s16           fine→coarse
    # L1↑ (medium):   [1,2,3,4]   → s8,s16,s32,s64      fine→coarse
    # L2↑ (coarse):   [3,4,5,6]   → s32,s64,s128,s256   fine→coarse
    # L3  (apex):     [5,6,7,8]   → s128,s256,s512,s1024 fine→coarse
    # L2↓ (coarse):   [3,4,5,6]   → s256,s128,s64,s32   coarse→fine
    # L1↓ (medium):   [1,2,3,4]   → s64,s32,s16,s8      coarse→fine
    # L0↓ (fine):     [0,1,2]     → s16,s8,s1           coarse→fine
    fractal_stride_bands: bool = True
    stride_band_ranges: tuple[tuple[int, int], ...] = (
        (0, 3),   # L0↑: indices 0-2 → s1,s8,s16
        (1, 5),   # L1↑: indices 1-4 → s8,s16,s32,s64
        (3, 7),   # L2↑: indices 3-6 → s32,s64,s128,s256
        (5, 9),   # L3:  indices 5-8 → s128,s256,s512,s1024
        (3, 7),   # L2↓: indices 3-6 → s32..s256 (reversed by desc_stride_reverse)
        (1, 5),   # L1↓: indices 1-4 → s8..s64 (reversed by desc_stride_reverse)
        (0, 3),   # L0↓: indices 0-2 → s1..s16 (reversed by desc_stride_reverse)
    )

    # ── Abstraction slots (S4→S5 composed abstractions) ──
    n_abstraction_slots: int = 16
    abstraction_diversity_lambda: float = 0.01
    abstraction_copy_lambda: float = 0.01
    abstraction_copy_threshold: float = 0.7
    abstraction_diversity_threshold: float = 0.5
    abstraction_dead_recycle_steps: int = 2000
    abstraction_proposal_threshold_init: float = 1.0

    # ── Holographic loss (progressive intermediate decoding) ──
    holo_lambda: float = 0.0
    holo_warmup_steps: int = 0
    holo_ramp_steps: int = 0

    # ── Dispatch entropy regularization (v12 variety fix) ──
    # Penalizes dispatch collapse: squared hinge on entropy below target.
    # Target = 85% of max entropy (ln(4) ≈ 1.386 → target ≈ 1.178).
    # Creates gradient flow from dispatch diversity back to ascending arm.
    dispatch_entropy_lambda: float = 0.01
    dispatch_entropy_target: float = 1.178   # ln(4) * 0.85

    # Dropout
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

    # ── Evolution ──
    gen_interval: int = 50
    base_pct: float = 0.0002
    sign_flip_rate: float = 0.2
    guided_fraction: float = 0.7
    mutation_adam_decay: float = 0.1
    s4_boost: float = 3.0
    evolution_min_delta: float = 0.01
    # Alarm-path noise floor: minimum health improvement to accept via alarm.
    # Alarm health ∈ [0, 2] (mean of per-pass factors). Without a floor,
    # health deltas of 0.0001 (measurement noise on a single eval batch)
    # get accepted, and the resulting sign flips cause routing ripple
    # effects that accumulate silently. 0.02 = 1% of the full range.
    evolution_alarm_min_delta: float = 0.02

    # ── Checkpointing ──
    checkpoint_interval: int = 1000
    eval_interval: int = 500
    log_interval: int = 25
    checkpoint_dir: str = "checkpoints/v12"

    # ── Data ──
    data_dir: str = "/Users/mwhitford/data/fractal-bitnet/shards-qwen3"
    structured_shard: str = "data/structured_shard.npy"
    mix_ratio: float = 0.0
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
