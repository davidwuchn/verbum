"""
v11 Configuration — KIBC combinator basis, Qwen3 tokenizer.

Architecture:
  Ascending arm: v6 proven 5-pass bidirectional VSM (9 strides, StrideStack)
  Descending arm: KIBC combinator dispatch (4 combinators, not 22 ops)
  Output: tied embedding projection → next-token prediction

The combinator basis comes from Qwen3 probes (4B and 32B, session 077):
  K (select):   native to attention softmax
  I (identity): native to residual stream
  B (compose):  matures with scale (20%→80% accuracy)
  C (flip):     emerges at scale (enables closures)

License: MIT
"""

from dataclasses import dataclass

from kernel import N_COMBINATORS


@dataclass
class V11Config:
    """v11 model + training configuration."""

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

    # ── Combinator dispatch ──
    n_combinators: int = N_COMBINATORS  # 4: K, I, B, C
    # No top-k needed with 4 targets — full softmax over all 4.
    # If a combinator dies, revisit and add top-k back.

    # Self-regulating descending cycles (unchanged from v10)
    desc_max_cycles: int = 3

    # Descending arm stride direction: coarse→fine (TST-aligned)
    # When True, descending arm processes s1024→...→s8→s1 (coarse→fine),
    # complementing the ascending arm's s1→s8→...→s1024 (fine→coarse).
    # Rationale: ascending compresses, descending expands. With holographic
    # loss providing per-pass signal, each arm gets the inductive bias
    # matching its function. See: Peng et al. "Token Superposition Training"
    # (2026) — coarse→fine works when coarse levels have direct loss.
    desc_stride_reverse: bool = True  # coarse→fine is the natural descending direction

    # Fractal stride bands: each pass activates only strides matching its
    # resolution level. Symmetric hourglass — ascending mirrors descending.
    # When enabled, each pass uses ~4-5 of the 9 strides instead of all 9.
    # This gives ~49% compute savings per forward pass and ensures each
    # pass focuses on its natural scale. Shared weights (S5 coherence) —
    # only the activation pattern changes, not the parameters.
    #
    # Band assignments (index into strides tuple):
    #   L0↑ (fine):    [0,1,2,3]   → s1,s8,s16,s32       fine→coarse
    #   L1↑ (medium):  [2,3,4,5,6] → s16,s32,s64,s128,s256  fine→coarse
    #   L2  (apex):    [4,5,6,7,8] → s64,s128,s256,s512,s1024  fine→coarse
    #   L1↓ (medium):  [2,3,4,5,6] → s256,s128,s64,s32,s16  coarse→fine
    #   L0↓ (fine):    [0,1,2,3]   → s32,s16,s8,s1       coarse→fine
    #
    # Adjacent passes share 2-3 strides for inter-level communication.
    # MERA tensor network topology: each level handles one scale band.
    fractal_stride_bands: bool = False  # default off, enable for fractal runs
    # Per-pass stride index ranges: (start_inclusive, end_exclusive) into strides tuple
    # 5 passes: L0↑, L1↑, L2, L1↓, L0↓
    stride_band_ranges: tuple[tuple[int, int], ...] = (
        (0, 4),   # L0↑: indices 0-3 → s1,s8,s16,s32
        (2, 7),   # L1↑: indices 2-6 → s16,s32,s64,s128,s256
        (4, 9),   # L2:  indices 4-8 → s64,s128,s256,s512,s1024
        (2, 7),   # L1↓: indices 2-6 → s16..s256 (reversed by desc_stride_reverse)
        (0, 4),   # L0↓: indices 0-3 → s1..s32 (reversed by desc_stride_reverse)
    )

    # ── Abstraction slots (S4→S5 composed abstractions) ──
    n_abstraction_slots: int = 16    # learnable embedding slots beyond KIBC
    abstraction_diversity_lambda: float = 0.01   # pairwise orthogonality pressure
    abstraction_copy_lambda: float = 0.01        # prevent copying KIBC embeddings
    abstraction_copy_threshold: float = 0.7      # cosine above this penalized
    abstraction_diversity_threshold: float = 0.5  # cosine above this penalized
    abstraction_dead_recycle_steps: int = 2000   # reinit dead slots after N steps
    abstraction_proposal_threshold_init: float = 1.0  # alarm×confidence threshold

    # ── Holographic loss (progressive intermediate decoding) ──
    holo_lambda: float = 0.0          # holographic loss weight (0.0 = disabled, preserves existing behavior)
    holo_warmup_steps: int = 0        # steps before holographic loss activates (0 = immediate)
    holo_ramp_steps: int = 0          # linear ramp from 0 → holo_lambda after warmup (0 = immediate)

    # Dropout
    dropout: float = 0.1

    # ── Training ──
    batch_size: int = 2
    grad_accum: int = 4           # effective batch = batch_size × grad_accum
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

    # ── Checkpointing ──
    checkpoint_interval: int = 1000
    eval_interval: int = 500
    log_interval: int = 25
    checkpoint_dir: str = "checkpoints/v11"

    # ── Data ──
    data_dir: str = "/Users/mwhitford/data/fractal-bitnet/shards-qwen3"
    structured_shard: str = "data/structured_shard.npy"
    mix_ratio: float = 0.0        # fraction of structured data (0.0 = prose only)
    seq_len: int = 4096           # context window
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
    def tokens_per_step(self) -> int:
        return self.batch_size * self.grad_accum * self.seq_len

    def __post_init__(self):
        assert self.d_model % self.n_heads == 0
        assert self.d_model % 16 == 0, "d_model must be divisible by 16 (ternary packing)"
        assert self.d_model % 4 == 0, "d_model must be divisible by 4 (embedding packing)"
