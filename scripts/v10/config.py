"""
v10 Configuration — self-contained.

Architecture informed by probe findings:
  - Compression IS typing (probe 1: no special type layer)
  - Binding info in compressed representations (probe 3: gap +0.15)
  - Self-similar compressor produces both signals at 16M params
  - Identity as substrate (invariant words pass through unchanged)
  - VSM tree kernel proven for 22 ops at 100% accuracy

Pipeline:
  tokens → [Compressor] → compressed_reps → [Tree Parser] → tree
         → [Dispatcher] → op_assignments → [Kernel] → result

License: MIT
"""

from dataclasses import dataclass, field


@dataclass
class V10Config:
    """v10 model + training configuration."""

    # ── Tokenizer ──
    # Simple S-expression tokenizer: each symbol is a token
    # Vocab: (, ), operators, numbers 0-99, special tokens
    # No BPE needed — S-expr tokens are unambiguous
    vocab_size: int = 256  # covers all S-expr tokens with room to spare

    # ── Compressor ──
    d_model: int = 256          # representation dimension
    d_ff: int = 768             # FFN expansion (3× d_model)
    n_heads: int = 8            # attention heads (d_head = 32)
    n_layers_per_level: int = 2 # transformer blocks per level
    window: int = 8             # attention window width
    n_iterations: int = 2       # iterative refinement passes

    # Strides: each level's attention stride
    # Level 0: stride 1 (word), Level 1: stride 8 (phrase), Level 2: stride 64 (clause)
    strides: tuple[int, ...] = (1, 8, 64)

    # Spiral attention bias
    spiral_alpha_init: float = 1.18
    use_spiral: bool = True

    # ── Dispatcher ──
    n_ops: int = 22             # kernel operations (from v9 VSM tree)
    dispatcher_hidden: int = 128 # hidden dim for op classification head

    # ── Kernel ──
    max_value: int = 1000       # max integer value in S-expressions
    max_depth: int = 4          # max nesting depth for training data

    # ── Training ──
    batch_size: int = 32
    total_steps: int = 20000
    lr: float = 3e-4
    lr_floor_ratio: float = 0.01   # cosine LR floor
    warmup_steps: int = 500
    weight_decay: float = 0.01
    grad_clip: float = 1.0

    # ── Evolution ──
    gen_interval: int = 25      # steps between tournament generations
    base_pct: float = 0.005     # base mutation rate
    sign_flip_rate: float = 0.2
    guided_fraction: float = 0.7

    # ── Checkpointing ──
    checkpoint_interval: int = 1000
    eval_interval: int = 500
    log_interval: int = 10
    checkpoint_dir: str = "checkpoints/v10"

    # ── Data ──
    n_eval: int = 500           # evaluation examples
    seq_len: int = 4096         # compressor sequence length (proven setup)
    max_seq_len: int = 4096     # token sequence length (pack multiple S-exprs to fill)

    @property
    def d_head(self) -> int:
        return self.d_model // self.n_heads

    @property
    def n_levels(self) -> int:
        return len(self.strides)

    def __post_init__(self):
        assert self.d_model % self.n_heads == 0
        assert self.d_model % 16 == 0, "d_model must be divisible by 16 (ternary packing)"
        assert self.d_model % 4 == 0, "d_model must be divisible by 4 (embedding packing)"
