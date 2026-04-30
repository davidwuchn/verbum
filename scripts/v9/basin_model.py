"""
Basin projector model — ascending arm v2.

Maps Qwen3 BBPE token sequences → per-word basin vectors (d_basin=64).
The basin vectors are geometric targets extracted from Qwen3-32B L28.

Architecture:
  Token IDs (Qwen3 BBPE, vocab=151936)
    → Ternary embedding (151936 × d_model)
    → MERA ascending arm
        Level 0 (own weights): stride 8, local syntax
        Levels 1-7 (SHARED weights): stride 2 each, wavelet
    → Word extraction: mean-pool BPE subword spans
    → Basin projection head: linear d_model → d_basin

Self-similar: ONE set of ternary weights reused 7× at levels 1-7.
Spiral attention bias: bias(w) = -α·ln(stride·w + 1) for scale awareness.
O(n × W) per level — 523× fewer ops than full attention at seq=4096.

License: MIT
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn

sys.path.insert(0, str(Path(__file__).parent.parent / "v8"))
from ternary import TernaryLinear, TernaryEmbedding


# ══════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════

QWEN3_VOCAB_SIZE = 151936


@dataclass
class BasinConfig:
    """Basin projector configuration."""
    # Model dimensions
    d_model: int = 256          # internal width (8-head × d_k=32)
    d_basin: int = 64           # output basin projection dimension
    n_heads: int = 8            # attention heads
    vocab_size: int = QWEN3_VOCAB_SIZE

    # MERA structure
    base_stride: int = 8        # level 0 stride
    shared_stride: int = 2      # levels 1-7 stride
    n_shared_levels: int = 7    # number of shared-weight levels

    # Spiral attention bias
    spiral_alpha: float = 1.18  # empirical from LLM analysis
    spiral_fp: float = 40.0     # fixed point of spiral

    # Sequence limits
    max_seq_len: int = 512      # max input sequence length
    max_words: int = 256        # max words after BPE pooling

    @property
    def d_k(self) -> int:
        return self.d_model // self.n_heads

    @property
    def n_levels(self) -> int:
        return 1 + self.n_shared_levels  # level 0 + shared levels


# ══════════════════════════════════════════════════════════════════
# Ternary attention with spiral bias
# ══════════════════════════════════════════════════════════════════

class SpiralAttention(nn.Module):
    """Multi-head self-attention with ternary Q/K/V/O and spiral bias.

    The spiral bias distributes energy across scales with hyperbolic
    (not exponential) decay:
        bias(i,j) = -α · ln(|i-j| + 1)

    This gives infinite effective range — every position sees all
    scales simultaneously. The same bias works at every MERA level
    because it depends on physical distance, not level index.
    """

    def __init__(self, d_model: int, n_heads: int, max_window: int,
                 alpha: float = 1.18):
        super().__init__()
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        self.scale = self.d_k ** -0.5

        self.q_proj = TernaryLinear(d_model, d_model, pre_norm=True)
        self.k_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.v_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.o_proj = TernaryLinear(d_model, d_model, pre_norm=False)

        # Pre-compute spiral bias for max window size
        # bias[i,j] = -alpha * ln(|i - j| + 1)
        positions = mx.arange(max_window)
        dist = mx.abs(positions[:, None] - positions[None, :])  # (W, W)
        self._spiral_bias = -alpha * mx.log(dist.astype(mx.float32) + 1.0)  # (W, W)

    def __call__(self, x: mx.array, mask: mx.array | None = None) -> mx.array:
        """
        Args:
            x:    (B, T, d_model)
            mask: (B, T) float — 1.0 for real tokens, 0.0 for padding
        Returns:
            (B, T, d_model)
        """
        B, T, D = x.shape
        H = self.n_heads
        dk = self.d_k

        q = self.q_proj(x).reshape(B, T, H, dk).transpose(0, 2, 1, 3)
        k = self.k_proj(x).reshape(B, T, H, dk).transpose(0, 2, 1, 3)
        v = self.v_proj(x).reshape(B, T, H, dk).transpose(0, 2, 1, 3)

        scores = (q @ k.transpose(0, 1, 3, 2)) * self.scale  # (B, H, T, T)

        # Add spiral bias (truncated to current window size)
        bias = self._spiral_bias[:T, :T]  # (T, T)
        scores = scores + bias

        if mask is not None:
            mask_4d = mask[:, None, None, :]  # (B, 1, 1, T)
            scores = mx.where(mask_4d > 0, scores, mx.array(-1e9))

        attn = mx.softmax(scores, axis=-1)
        out = (attn @ v).transpose(0, 2, 1, 3).reshape(B, T, D)

        return self.o_proj(out)


# ══════════════════════════════════════════════════════════════════
# MERA level — one stride-reduction step
# ══════════════════════════════════════════════════════════════════

class MERALevel(nn.Module):
    """One level of the MERA ascending arm.

    Steps:
      1. Split sequence into stride-sized windows
      2. Add within-window positional encoding
      3. Self-attend within each window (spiral bias)
      4. Mix (ternary feed-forward with residual)
      5. Attention-weighted pooling → one vector per window

    The same instance is reused at levels 1-7 (shared weights = wavelet).
    Level 0 has its own instance (different weights, stride 8).
    """

    def __init__(self, d_model: int, n_heads: int, stride: int,
                 alpha: float = 1.18):
        super().__init__()
        self.stride = stride

        # Self-attention within windows
        self.attn = SpiralAttention(d_model, n_heads, max_window=stride,
                                    alpha=alpha)

        # Feed-forward (ternary)
        self.ff = TernaryLinear(d_model, d_model, pre_norm=True)

        # Within-window position encoding
        self.window_pos = nn.Embedding(stride, d_model)

        # Pool query — learned vector for attention pooling
        self._pool_query = mx.random.normal((1, 1, d_model)) * 0.02
        self._d_model = d_model

    def __call__(self, x: mx.array) -> mx.array:
        """
        Args:
            x: (B, T, d_model)
        Returns:
            (B, ceil(T/stride), d_model) — reduced sequence
        """
        B, T, D = x.shape
        stride = self.stride

        if T <= 1:
            return x

        # Pad to multiple of stride
        pad_len = (stride - T % stride) % stride
        if pad_len > 0:
            x = mx.concatenate([x, mx.zeros((B, pad_len, D))], axis=1)
            T_padded = T + pad_len
        else:
            T_padded = T

        n_windows = T_padded // stride

        # Reshape into windows: (B * n_windows, stride, D)
        windows = x.reshape(B, n_windows, stride, D)
        win_pos = self.window_pos(mx.arange(stride))  # (stride, D)
        windows = windows + win_pos
        flat = windows.reshape(B * n_windows, stride, D)

        # Self-attend within each window (residual)
        attended = flat + self.attn(flat)

        # Feed-forward (residual)
        flat_2d = attended.reshape(B * n_windows * stride, D)
        mixed = flat_2d + self.ff(flat_2d)
        attended = mixed.reshape(B * n_windows, stride, D)

        # Attention-weighted pooling
        pool_q = mx.broadcast_to(self._pool_query, (B * n_windows, 1, D))
        pool_scores = (pool_q @ attended.transpose(0, 2, 1)) * (D ** -0.5)
        pool_attn = mx.softmax(pool_scores, axis=-1)  # (B*nw, 1, stride)
        pooled = (pool_attn @ attended).squeeze(1)     # (B*nw, D)

        return pooled.reshape(B, n_windows, D)


# ══════════════════════════════════════════════════════════════════
# Basin Projector — full ascending arm + word pooling + projection
# ══════════════════════════════════════════════════════════════════

class BasinProjector(nn.Module):
    """Full basin projector: tokens → per-word basin vectors.

    Architecture:
      1. Ternary embedding (vocab → d_model)
      2. Positional encoding (sinusoidal, up to max_seq_len)
      3. MERA ascending arm:
         - Level 0 (own weights, stride 8): token → local
         - Levels 1-7 (SHARED weights, stride 2): local → multi-scale
      4. Word extraction: mean-pool BPE subword spans
      5. Basin projection: linear d_model → d_basin
      6. L2 normalize output (basins live in direction space)
    """

    def __init__(self, config: BasinConfig | None = None):
        super().__init__()
        if config is None:
            config = BasinConfig()
        self.config = config

        # 1. Ternary embedding
        self.embed = TernaryEmbedding(config.vocab_size, config.d_model)

        # 2. Sinusoidal positional encoding (not learned — saves ternary params)
        pe = self._make_sinusoidal_pe(config.max_seq_len, config.d_model)
        self._pos_enc = pe  # (max_seq_len, d_model) float32

        # 3. MERA levels
        # Level 0: own weights, stride 8
        self.level0 = MERALevel(
            config.d_model, config.n_heads, config.base_stride,
            alpha=config.spiral_alpha,
        )
        # Levels 1-7: SHARED weights, stride 2
        self.shared_level = MERALevel(
            config.d_model, config.n_heads, config.shared_stride,
            alpha=config.spiral_alpha,
        )

        # 5. Basin projection head
        # Use TernaryLinear for the projection
        # d_basin must be padded to multiple of 16 for TernaryLinear
        d_basin_padded = ((config.d_basin + 15) // 16) * 16
        self.basin_proj = TernaryLinear(config.d_model, d_basin_padded,
                                        pre_norm=True)
        self._d_basin = config.d_basin

    @staticmethod
    def _make_sinusoidal_pe(max_len: int, d_model: int) -> mx.array:
        """Standard sinusoidal positional encoding."""
        pe = mx.zeros((max_len, d_model))
        position = mx.arange(max_len).reshape(-1, 1).astype(mx.float32)
        div_term = mx.exp(
            mx.arange(0, d_model, 2).astype(mx.float32) *
            (-math.log(10000.0) / d_model)
        )
        # sin for even dims, cos for odd dims
        sin_vals = mx.sin(position * div_term)
        cos_vals = mx.cos(position * div_term)
        # Interleave: pe[:, 0::2] = sin, pe[:, 1::2] = cos
        pe_list = []
        for i in range(d_model):
            if i % 2 == 0:
                pe_list.append(sin_vals[:, i // 2:i // 2 + 1])
            else:
                pe_list.append(cos_vals[:, i // 2:i // 2 + 1])
        pe = mx.concatenate(pe_list, axis=1)
        return pe

    def _ascending_arm(self, x: mx.array) -> mx.array:
        """Run MERA ascending arm: level 0 attend + sieve levels 0-7 + feedback.

        Architecture (sieve with feedback):
          1. Level 0 ATTEND: within stride-8 windows, keep all token positions
          2. Level 0 POOL: attention-weighted pooling → T/8 positions
          3. Levels 1-7 (SHARED): stride-2 attend+pool, progressively reducing
          4. FEEDBACK: broadcast each level's output back to token positions
             Each level covers a progressively larger span of original tokens.
             All scales are added to the enriched token representations.

        Result: each token gets its own embedding + local context (8 tokens)
        + progressively broader context up to the full sequence.

        For a 128-token sequence:
          Level 0 pool: 128 → 16 (8-token spans)
          Level 1: 16 → 8 (16-token spans)
          Level 2: 8 → 4 (32-token spans)
          Level 3: 4 → 2 (64-token spans)
          Level 4: 2 → 1 (128-token span = global)
          Levels 5-7: skip (already at 1 position)

        For short sentences (~10 tokens, padded to 16):
          Level 0 pool: 16 → 2
          Level 1: 2 → 1 (global)
          → Cross-window context achieved with just 2 active sieve levels.

        Args:
            x: (B, T, d_model) — embedded tokens
        Returns:
            (B, T, d_model) — tokens enriched with multi-scale context
        """
        B, T, D = x.shape
        stride = self.config.base_stride

        # ── Pad to multiple of stride ────────────────────────
        pad_len = (stride - T % stride) % stride
        if pad_len > 0:
            x_padded = mx.concatenate([x, mx.zeros((B, pad_len, D))], axis=1)
            T_padded = T + pad_len
        else:
            x_padded = x
            T_padded = T

        n_windows = T_padded // stride

        # ── Level 0 ATTEND: within stride-8 windows, keep all positions ──
        windows = x_padded.reshape(B, n_windows, stride, D)
        win_pos = self.level0.window_pos(mx.arange(stride))
        windows = windows + win_pos
        flat = windows.reshape(B * n_windows, stride, D)

        attended = flat + self.level0.attn(flat)
        flat_2d = attended.reshape(B * n_windows * stride, D)
        mixed = flat_2d + self.level0.ff(flat_2d)
        enriched = mixed.reshape(B, T_padded, D)

        # ── Level 0 POOL: attention-weighted reduction → T/8 ──
        attended_windows = mixed.reshape(B * n_windows, stride, D)
        pool_q = mx.broadcast_to(self.level0._pool_query, (B * n_windows, 1, D))
        pool_scores = (pool_q @ attended_windows.transpose(0, 2, 1)) * (D ** -0.5)
        pool_attn = mx.softmax(pool_scores, axis=-1)
        pooled = (pool_attn @ attended_windows).squeeze(1)  # (B*nw, D)
        reduced = pooled.reshape(B, n_windows, D)

        # ── Levels 1-7 (SHARED): stride-2 attend+pool ──
        level_outputs = [reduced]  # level 0 pooled = first feedback source
        current = reduced

        for _ in range(self.config.n_shared_levels):
            if current.shape[1] <= 1:
                break  # can't reduce further
            current = self.shared_level(current)
            level_outputs.append(current)

        # ── FEEDBACK: broadcast each level back to token positions ──
        # Level 0 pooled: each position covers `stride` tokens
        # Level 1: each position covers `stride * 2` tokens
        # Level L: each position covers `stride * 2^L` tokens
        for level_out in level_outputs:
            n_pos = level_out.shape[1]
            if n_pos == 0:
                continue
            span = T_padded // n_pos  # tokens per position at this level
            # Broadcast: repeat each position's vector across its span
            expanded = mx.repeat(level_out, span, axis=1)  # (B, n_pos*span, D)
            # Handle rounding (n_pos*span might not equal T_padded)
            if expanded.shape[1] > T_padded:
                expanded = expanded[:, :T_padded, :]
            elif expanded.shape[1] < T_padded:
                pad = T_padded - expanded.shape[1]
                expanded = mx.concatenate(
                    [expanded, mx.zeros((B, pad, D))], axis=1
                )
            enriched = enriched + expanded

        # ── Trim padding ─────────────────────────────────────
        enriched = enriched[:, :T, :]
        return enriched

    def forward(
        self,
        token_ids: mx.array,
        word_spans: list[list[list[int]]],
    ) -> mx.array:
        """Forward pass: tokens → per-word basin vectors.

        Args:
            token_ids:  (B, T) int — Qwen3 BBPE token IDs
            word_spans: list of B lists, each a list of spans.
                        Each span is a list of token indices for one word.
                        E.g. [[0,1], [2], [3,4,5]] = 3 words.

        Returns:
            basin_vectors: (B, max_words, d_basin) float32
                           L2-normalized per-word basin vectors.
            word_mask:     (B, max_words) float32
                           1.0 for real words, 0.0 for padding.
        """
        B, T = token_ids.shape
        D = self.config.d_model

        # 1. Embed tokens
        x = self.embed(token_ids)  # (B, T, d_model)

        # 2. Add positional encoding
        x = x + self._pos_enc[:T]

        # 3. Ascending arm (enriches each token with local context)
        x = self._ascending_arm(x)  # (B, T, d_model)

        # 4. Word extraction: mean-pool BPE spans
        max_words = max(len(spans) for spans in word_spans)
        word_vecs = mx.zeros((B, max_words, D))
        word_mask = mx.zeros((B, max_words))

        # This is the only non-batched part — word spans vary per example
        word_vecs_list = []
        word_mask_list = []
        for b in range(B):
            spans = word_spans[b]
            n_words = len(spans)
            b_word_vecs = mx.zeros((max_words, D))
            b_mask = mx.zeros((max_words,))

            for wi, span in enumerate(spans):
                if len(span) == 1:
                    b_word_vecs = b_word_vecs.at[wi].add(x[b, span[0]])
                else:
                    span_vecs = x[b, mx.array(span)]  # (n_tokens, D)
                    b_word_vecs = b_word_vecs.at[wi].add(span_vecs.mean(axis=0))
                b_mask = b_mask.at[wi].add(1.0)

            word_vecs_list.append(b_word_vecs)
            word_mask_list.append(b_mask)

        word_vecs = mx.stack(word_vecs_list, axis=0)  # (B, max_words, D)
        word_mask = mx.stack(word_mask_list, axis=0)   # (B, max_words)

        # 5. Basin projection
        flat = word_vecs.reshape(B * max_words, D)
        basin = self.basin_proj(flat)[:, :self._d_basin]  # (B*max_words, d_basin)
        basin = basin.reshape(B, max_words, self._d_basin)

        # 6. L2 normalize (basins live in direction space)
        norms = mx.sqrt(mx.sum(basin ** 2, axis=-1, keepdims=True) + 1e-8)
        basin = basin / norms

        return basin, word_mask

    def __call__(self, token_ids: mx.array,
                 word_spans: list[list[list[int]]]) -> tuple[mx.array, mx.array]:
        return self.forward(token_ids, word_spans)

    def count_params(self) -> dict[str, int]:
        """Count parameters by type."""
        from mlx.utils import tree_flatten as tf
        total_logical = 0
        ternary_logical = 0
        continuous = 0
        for name, p in tf(self.parameters()):
            if p.dtype == mx.uint32:
                # MLX 2-bit packed: 16 values per uint32
                logical = p.size * 16
                ternary_logical += logical
                total_logical += logical
            elif p.dtype == mx.uint8:
                # uint8 packed: 4 values per byte
                logical = p.size * 4
                ternary_logical += logical
                total_logical += logical
            else:
                continuous += p.size
                total_logical += p.size
        return {
            "total_logical": total_logical,
            "ternary_logical": ternary_logical,
            "continuous": continuous,
            "packed_bytes": sum(p.nbytes for _, p in tf(self.parameters())),
        }


# ══════════════════════════════════════════════════════════════════
# Word boundary detection (from oracle_extract.py, adapted for MLX)
# ══════════════════════════════════════════════════════════════════

def detect_word_spans(tokenizer, token_ids: list[int]) -> list[list[int]]:
    """Detect BPE word boundaries and return token index spans.

    Args:
        tokenizer: Qwen3 tokenizer
        token_ids: list of token IDs (no batch dim)

    Returns:
        List of spans, each span is a list of token indices for one word.
        Special tokens are skipped.
    """
    tokens = tokenizer.convert_ids_to_tokens(token_ids)
    words = []
    current_word = []

    for i, tok in enumerate(tokens):
        if tok in tokenizer.all_special_tokens:
            if current_word:
                words.append(current_word)
                current_word = []
            continue

        if tok.startswith("Ġ") or tok.startswith("▁") or not current_word:
            if current_word:
                words.append(current_word)
            current_word = [i]
        else:
            current_word.append(i)

    if current_word:
        words.append(current_word)

    return words


# ══════════════════════════════════════════════════════════════════
# Smoke test
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  Basin Projector — Smoke Test")
    print("=" * 60)

    config = BasinConfig(
        d_model=256,
        d_basin=64,
        n_heads=8,
        max_seq_len=128,
    )
    print(f"\nConfig: d_model={config.d_model}, d_basin={config.d_basin}, "
          f"n_heads={config.n_heads}, d_k={config.d_k}")
    print(f"  base_stride={config.base_stride}, shared_stride={config.shared_stride}, "
          f"n_levels={config.n_levels}")

    model = BasinProjector(config)
    params = model.count_params()
    print(f"\nParameters:")
    for k, v in params.items():
        if k == "packed_bytes":
            print(f"  {k}: {v:,} ({v / 1e6:.1f} MB)")
        else:
            print(f"  {k}: {v:,}")

    # Simulate input: 2 sentences with fake word spans
    B = 2
    T = 32
    token_ids = mx.random.randint(0, 1000, (B, T))

    # Fake word spans: 5-7 words per sentence
    word_spans = [
        [[0, 1], [2], [3, 4], [5], [6, 7, 8], [9], [10]],
        [[0], [1, 2], [3], [4, 5], [6], [7]],
    ]

    print(f"\nInput: token_ids {token_ids.shape}, "
          f"words: {[len(s) for s in word_spans]}")

    basin_vecs, word_mask = model(token_ids, word_spans)
    mx.eval(basin_vecs, word_mask)

    print(f"Output: basin_vecs {basin_vecs.shape}, word_mask {word_mask.shape}")
    print(f"  Basin vector norms (should be ~1.0): "
          f"{mx.sqrt(mx.sum(basin_vecs[0, :3] ** 2, axis=-1)).tolist()}")
    print(f"  Word mask[0]: {word_mask[0].tolist()}")
    print(f"  Word mask[1]: {word_mask[1].tolist()}")

    # Test with real tokenizer if available
    try:
        from transformers import AutoTokenizer
        print(f"\nTesting with real Qwen3 tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-32B")

        sentences = [
            "The cat sleeps on the mat.",
            "(+ 3 (* 4 5))",
            "Calculate the sum of the values.",
        ]

        for sent in sentences:
            enc = tokenizer(sent, return_tensors="np")
            ids = enc["input_ids"][0].tolist()
            spans = detect_word_spans(tokenizer, ids)
            words = [tokenizer.decode([ids[j] for j in span]).strip() for span in spans]
            print(f"  {sent!r}")
            print(f"    tokens={len(ids)}, words={len(spans)}: {words}")

        # Forward pass with real tokens
        max_len = max(len(tokenizer(s)["input_ids"]) for s in sentences)
        batch_ids = []
        batch_spans = []
        for sent in sentences:
            enc = tokenizer(sent, padding="max_length", max_length=max_len,
                            return_tensors="np")
            ids = enc["input_ids"][0].tolist()
            batch_ids.append(ids)
            batch_spans.append(detect_word_spans(tokenizer, ids))

        token_ids_mx = mx.array(batch_ids)
        basin_vecs, word_mask = model(token_ids_mx, batch_spans)
        mx.eval(basin_vecs, word_mask)

        for i, sent in enumerate(sentences):
            n_words = int(word_mask[i].sum().item())
            print(f"  {sent!r} → {n_words} words, "
                  f"basin shape per word: ({config.d_basin},)")

    except ImportError:
        print("\n  (transformers not available — skipping tokenizer test)")

    print(f"\n{'=' * 60}")
    print(f"  ✓ Basin projector smoke test passed")
    print(f"{'=' * 60}")
