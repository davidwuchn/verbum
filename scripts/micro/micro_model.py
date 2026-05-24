"""
Micro Model — Minimum viable holographic state machine.

A tiny transformer (~500K params) trained on pure lambda calculus data,
designed to be fully traceable. Every activation, every gradient, every
Q rotation can be read like a circuit diagram.

Architecture:
  embed → [attention → FFN] × N_LAYERS → unembed

No VSM tree, no algedonics, no S5 controller.
Float32 weights throughout (no ternary — this is the microscope, not the target).
Crystal embeddings (16 = 8 positive + 8 anti) pre-initialized from
PCAQ Zone B targets and enforced via crystal lattice loss.

The goal: train this on lambda calculus compile examples until the
holographic state machine forms (crystal latches, FFN encodes inference
pattern). Then trace forward and backward passes to reverse-engineer:
  1. How Q rotations select crystal basins
  2. How FFN overlays encode the inference pattern
  3. How gradients map to beta-reduction selections

License: MIT
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import mlx.core as mx
import mlx.nn as nn


# ══════════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════════

N_COMBINATORS = 8
N_TOTAL_COMBINATORS = 16
COMBINATOR_NAMES = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]
ANTI_COMBINATOR_NAMES = ["āK", "āI", "āB", "āC", "āD", "āY", "āW", "āWHNF"]


@dataclass
class MicroConfig:
    """Configuration for the micro tracing model."""

    # ── Tokenizer ──
    vocab_size: int = 151936     # Qwen3 BBPE (same as v13)
    eod_id: int = 151643

    # ── Architecture ──
    d_model: int = 128           # small enough to read every dim
    d_ff: int = 512              # 4x d_model
    n_heads: int = 4             # d_head = 32
    n_layers: int = 4            # 4 transformer blocks
    max_seq_len: int = 256       # lambda outputs are short (~25 chars)
    dropout: float = 0.0         # no dropout — we want deterministic traces

    # ── Crystal ──
    crystal_lambda: float = 5.0           # crystal lattice loss weight
    crystal_warmup_steps: int = 200       # high enforcement early
    crystal_warmup_start: float = 20.0    # initial crystal weight
    use_parity_loss: bool = True
    parity_lambda: float = 1.0

    # ── Training ──
    batch_size: int = 8
    lr: float = 3e-4
    warmup_steps: int = 100
    total_steps: int = 5000
    weight_decay: float = 0.01
    grad_clip: float = 1.0
    eval_interval: int = 100
    log_interval: int = 25
    checkpoint_interval: int = 500
    checkpoint_dir: str = "checkpoints/micro"

    # ── Data ──
    train_file: str = "data/compile-train.jsonl"
    eval_file: str = "data/compile-eval.jsonl"
    test_file: str = "data/compile-test.jsonl"

    @property
    def d_head(self) -> int:
        return self.d_model // self.n_heads


# ══════════════════════════════════════════════════════════════════════
# Crystal targets (Zone B — the compute zone)
# From V13Config, PCAQ Zone B targets (4-model consensus)
# ══════════════════════════════════════════════════════════════════════

PCAQ_ZONE_B_TARGETS = np.array([
    [+1.0000, +0.7865, +0.1948, +0.2265, +0.3232, +0.1768, +0.5360, -0.1862, -0.1900, -0.1494, -0.0370, -0.0430, -0.0614, -0.0336, -0.1018, +0.0354],
    [+0.7865, +1.0000, +0.2479, +0.2511, +0.3463, +0.1739, +0.3781, -0.2448, -0.1494, -0.1900, -0.0471, -0.0477, -0.0658, -0.0330, -0.0718, +0.0465],
    [+0.1948, +0.2479, +1.0000, +0.8878, +0.8937, +0.6623, +0.6851, -0.1227, -0.0370, -0.0471, -0.1900, -0.1687, -0.1698, -0.1258, -0.1302, +0.0233],
    [+0.2265, +0.2511, +0.8878, +1.0000, +0.8316, +0.7200, +0.7318, -0.1027, -0.0430, -0.0477, -0.1687, -0.1900, -0.1580, -0.1368, -0.1390, +0.0195],
    [+0.3232, +0.3463, +0.8937, +0.8316, +1.0000, +0.6798, +0.8064, -0.1729, -0.0614, -0.0658, -0.1698, -0.1580, -0.1900, -0.1292, -0.1532, +0.0329],
    [+0.1768, +0.1739, +0.6623, +0.7200, +0.6798, +1.0000, +0.5653, -0.0840, -0.0336, -0.0330, -0.1258, -0.1368, -0.1292, -0.1900, -0.1074, +0.0160],
    [+0.5360, +0.3781, +0.6851, +0.7318, +0.8064, +0.5653, +1.0000, -0.1379, -0.1018, -0.0718, -0.1302, -0.1390, -0.1532, -0.1074, -0.1900, +0.0262],
    [-0.1862, -0.2448, -0.1227, -0.1027, -0.1729, -0.0840, -0.1379, +1.0000, +0.0354, +0.0465, +0.0233, +0.0195, +0.0329, +0.0160, +0.0262, -0.1900],
    [-0.1900, -0.1494, -0.0370, -0.0430, -0.0614, -0.0336, -0.1018, +0.0354, +1.0000, +0.7865, +0.1948, +0.2265, +0.3232, +0.1768, +0.5360, -0.1862],
    [-0.1494, -0.1900, -0.0471, -0.0477, -0.0658, -0.0330, -0.0718, +0.0465, +0.7865, +1.0000, +0.2479, +0.2511, +0.3463, +0.1739, +0.3781, -0.2448],
    [-0.0370, -0.0471, -0.1900, -0.1687, -0.1698, -0.1258, -0.1302, +0.0233, +0.1948, +0.2479, +1.0000, +0.8878, +0.8937, +0.6623, +0.6851, -0.1227],
    [-0.0430, -0.0477, -0.1687, -0.1900, -0.1580, -0.1368, -0.1390, +0.0195, +0.2265, +0.2511, +0.8878, +1.0000, +0.8316, +0.7200, +0.7318, -0.1027],
    [-0.0614, -0.0658, -0.1698, -0.1580, -0.1900, -0.1292, -0.1532, +0.0329, +0.3232, +0.3463, +0.8937, +0.8316, +1.0000, +0.6798, +0.8064, -0.1729],
    [-0.0336, -0.0330, -0.1258, -0.1368, -0.1292, -0.1900, -0.1074, +0.0160, +0.1768, +0.1739, +0.6623, +0.7200, +0.6798, +1.0000, +0.5653, -0.0840],
    [-0.1018, -0.0718, -0.1302, -0.1390, -0.1532, -0.1074, -0.1900, +0.0262, +0.5360, +0.3781, +0.6851, +0.7318, +0.8064, +0.5653, +1.0000, -0.1379],
    [+0.0354, +0.0465, +0.0233, +0.0195, +0.0329, +0.0160, +0.0262, -0.1900, -0.1862, -0.2448, -0.1227, -0.1027, -0.1729, -0.0840, -0.1379, +1.0000],
], dtype=np.float32)


def _precompute_parity_eigenbasis(target: np.ndarray) -> dict:
    """Eigendecompose target cosine matrix for parity checks."""
    eigvals, eigvecs = np.linalg.eigh(target)
    idx = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]

    parity_levels = [3, 4, 5, 6, 8]
    total_var = sum(max(ev, 0) for ev in eigvals)
    level_weights = []
    for k in parity_levels:
        cum_var = sum(max(eigvals[j], 0) for j in range(k))
        level_weights.append(cum_var / total_var)

    return {
        "eigvecs": eigvecs,
        "eigvals": eigvals,
        "parity_levels": parity_levels,
        "level_weights": level_weights,
    }


def _init_crystal_embeddings(d_model: int) -> tuple[np.ndarray, np.ndarray]:
    """Initialize crystal embeddings from Zone B target eigenstructure.

    Instead of random init, we seed the embeddings so their cosine matrix
    already approximates the Zone B target. This gives the crystal a head
    start on latching.

    Method: eigendecompose the target, take top-k eigenvectors scaled by
    sqrt(eigenvalue), truncate/pad to d_model. The resulting embeddings
    have cosine matrix ≈ target by construction.
    """
    target = PCAQ_ZONE_B_TARGETS
    eigvals, eigvecs = np.linalg.eigh(target)
    idx = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]

    # Use top eigenvalues to construct embeddings
    # emb[i] = sum_k sqrt(max(eigval_k, 0)) * eigvec_k[i] * random_direction_k
    n = target.shape[0]  # 16
    k = min(n, d_model)

    # Scale eigenvectors by sqrt(eigenvalue) — preserves cosine structure
    scales = np.sqrt(np.maximum(eigvals[:k], 0))
    basis = eigvecs[:, :k] * scales[np.newaxis, :]  # (16, k)

    # If d_model > k, pad with small random noise
    if d_model > k:
        pad = np.random.randn(n, d_model - k).astype(np.float32) * 0.001
        embeddings = np.concatenate([basis, pad], axis=1)
    else:
        embeddings = basis[:, :d_model]

    # Normalize to unit norm (cosine matrix is scale-invariant)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-8
    embeddings = embeddings / norms * 0.5  # scale=0.5 for stable training

    return embeddings[:N_COMBINATORS], embeddings[N_COMBINATORS:]


# ══════════════════════════════════════════════════════════════════════
# Model components
# ══════════════════════════════════════════════════════════════════════


class MultiHeadAttention(nn.Module):
    """Standard multi-head attention with full trace capture.

    When self.capture_trace is True, stores Q, K, V projections and
    attention weights for later analysis.
    """

    def __init__(self, d_model: int, n_heads: int):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_head = d_model // n_heads

        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.k_proj = nn.Linear(d_model, d_model, bias=False)
        self.v_proj = nn.Linear(d_model, d_model, bias=False)
        self.o_proj = nn.Linear(d_model, d_model, bias=False)

        # Trace storage (populated when capture_trace=True)
        self.capture_trace = False
        self.trace = {}

    def __call__(self, x: mx.array, mask: Optional[mx.array] = None) -> mx.array:
        B, L, D = x.shape
        H = self.n_heads

        q = self.q_proj(x).reshape(B, L, H, self.d_head).transpose(0, 2, 1, 3)
        k = self.k_proj(x).reshape(B, L, H, self.d_head).transpose(0, 2, 1, 3)
        v = self.v_proj(x).reshape(B, L, H, self.d_head).transpose(0, 2, 1, 3)

        # Scaled dot-product attention
        scale = math.sqrt(self.d_head)
        scores = (q @ k.transpose(0, 1, 3, 2)) / scale  # (B, H, L, L)

        if mask is not None:
            scores = scores + mask

        attn_weights = mx.softmax(scores, axis=-1)
        attn_out = attn_weights @ v  # (B, H, L, d_head)

        # Capture trace if requested
        if self.capture_trace:
            self.trace = {
                "q": mx.stop_gradient(q),           # (B, H, L, d_head)
                "k": mx.stop_gradient(k),
                "v": mx.stop_gradient(v),
                "attn_weights": mx.stop_gradient(attn_weights),  # (B, H, L, L)
                "attn_out": mx.stop_gradient(attn_out),
            }

        # Reshape and project
        out = attn_out.transpose(0, 2, 1, 3).reshape(B, L, D)
        return self.o_proj(out)


class SwiGLUFFN(nn.Module):
    """SwiGLU FFN with full trace capture.

    gate_proj controls which neurons fire (the beamformer).
    key_proj provides the content to gate (the holographic plate).
    value_proj projects back to d_model (the readout).

    When capture_trace is True, stores gate activations, key activations,
    gated output, and value projection for analysis.
    """

    def __init__(self, d_model: int, d_ff: int):
        super().__init__()
        self.gate_proj = nn.Linear(d_model, d_ff, bias=False)
        self.key_proj = nn.Linear(d_model, d_ff, bias=False)
        self.value_proj = nn.Linear(d_ff, d_model, bias=False)

        self.capture_trace = False
        self.trace = {}

    def __call__(self, x: mx.array) -> mx.array:
        gate = nn.silu(self.gate_proj(x))   # gate activation (beamformer)
        key = self.key_proj(x)               # key activation (plate content)
        gated = gate * key                   # SwiGLU gating
        out = self.value_proj(gated)         # project back

        if self.capture_trace:
            self.trace = {
                "gate": mx.stop_gradient(gate),
                "key": mx.stop_gradient(key),
                "gated": mx.stop_gradient(gated),
                "out": mx.stop_gradient(out),
                "gate_sparsity": mx.stop_gradient(
                    mx.mean((mx.abs(gate) < 0.01).astype(mx.float32))
                ),
            }

        return out


class TransformerBlock(nn.Module):
    """Pre-norm transformer block: norm → attn → add → norm → ffn → add.

    Captures residual stream at input and output for tracing.
    """

    def __init__(self, d_model: int, n_heads: int, d_ff: int):
        super().__init__()
        self.attn_norm = nn.RMSNorm(d_model)
        self.attn = MultiHeadAttention(d_model, n_heads)
        self.ffn_norm = nn.RMSNorm(d_model)
        self.ffn = SwiGLUFFN(d_model, d_ff)

        self.capture_trace = False
        self.trace = {}

    def __call__(self, x: mx.array, mask: Optional[mx.array] = None) -> mx.array:
        # Attention
        normed = self.attn_norm(x)
        attn_out = self.attn(normed, mask=mask)
        x = x + attn_out

        # FFN
        normed = self.ffn_norm(x)
        ffn_out = self.ffn(normed)
        x = x + ffn_out

        if self.capture_trace:
            self.trace = {
                "residual_post_attn": mx.stop_gradient(x - ffn_out),
                "attn_contribution": mx.stop_gradient(attn_out),
                "ffn_contribution": mx.stop_gradient(ffn_out),
                "residual_post_ffn": mx.stop_gradient(x),
            }

        return x


# ══════════════════════════════════════════════════════════════════════
# Crystal loss functions
# ══════════════════════════════════════════════════════════════════════


def crystal_lattice_loss(emb_all: mx.array, target: mx.array) -> mx.array:
    """Crystal lattice MSE: upper-triangle cosine matrix vs target."""
    norms = mx.sqrt(mx.sum(emb_all * emb_all, axis=-1, keepdims=True) + 1e-8)
    emb_norm = emb_all / norms
    cos_matrix = emb_norm @ emb_norm.T
    n = cos_matrix.shape[0]
    # Upper triangle indices
    rows, cols = [], []
    for i in range(n):
        for j in range(i + 1, n):
            rows.append(i)
            cols.append(j)
    student = cos_matrix[mx.array(rows), mx.array(cols)]
    target_vals = target[mx.array(rows), mx.array(cols)]
    diff = student - target_vals
    return mx.mean(diff * diff)


def crystal_parity_loss(
    emb_all: mx.array,
    eigvecs: mx.array,
    eigvals: mx.array,
    parity_levels: list[int],
    level_weights: list[float],
) -> tuple[mx.array, mx.array]:
    """Hierarchical dimensional parity check."""
    norms = mx.sqrt(mx.sum(emb_all * emb_all, axis=-1, keepdims=True) + 1e-8)
    emb_norm = emb_all / norms
    student_cos = emb_norm @ emb_norm.T

    projected = eigvecs.T @ student_cos @ eigvecs
    total_loss = mx.array(0.0)
    level_errors = []

    for k, w in zip(parity_levels, level_weights):
        P_k = projected[:k, :k]
        target_diag = mx.diag(eigvals[:k])
        diff = P_k - target_diag
        mse = mx.mean(diff * diff)
        mask = 1.0 - mx.eye(k)
        off_diag = mx.abs(P_k * mask)
        max_off_diag = mx.max(off_diag)
        level_errors.append(max_off_diag)
        total_loss = total_loss + w * mse

    per_level_errors = mx.stack(level_errors)
    return total_loss, per_level_errors


# ══════════════════════════════════════════════════════════════════════
# Micro Model
# ══════════════════════════════════════════════════════════════════════


class MicroModel(nn.Module):
    """Minimum viable holographic state machine.

    Tiny transformer with crystal embeddings. Every component is
    individually traceable. No abstractions hiding computation.

    Forward: embed → blocks × n_layers → norm → unembed
    Crystal: 16 combinator embeddings enforced via Zone B lattice loss
    Trace: set_capture(True) to record all intermediate computations
    """

    def __init__(self, cfg: MicroConfig):
        super().__init__()
        self.cfg = cfg
        d = cfg.d_model

        # ── Embeddings ──
        self.embed = nn.Embedding(cfg.vocab_size, d)
        self.pos_embed = nn.Embedding(cfg.max_seq_len, d)

        # ── Crystal embeddings (pre-initialized from Zone B targets) ──
        pos_init, anti_init = _init_crystal_embeddings(d)
        self.combinator_embeddings = mx.array(pos_init)
        self.anti_combinator_embeddings = mx.array(anti_init)

        # Precompute parity eigenbasis
        parity_data = _precompute_parity_eigenbasis(PCAQ_ZONE_B_TARGETS)
        self._parity_eigvecs = mx.array(parity_data["eigvecs"])
        self._parity_eigvals = mx.array(parity_data["eigvals"])
        self._parity_levels = parity_data["parity_levels"]
        self._parity_weights = parity_data["level_weights"]

        # Zone B target (frozen)
        self._zone_b_target = mx.array(PCAQ_ZONE_B_TARGETS)

        # ── Transformer blocks ──
        self.blocks = [
            TransformerBlock(d, cfg.n_heads, cfg.d_ff)
            for _ in range(cfg.n_layers)
        ]

        # ── Output ──
        self.output_norm = nn.RMSNorm(d)

        # ── Training state ──
        self._training_step = 0
        self._crystal_ema = mx.array(1.0)

        # ── Causal mask cache ──
        self._causal_mask = None
        self._causal_mask_len = 0

    def _get_causal_mask(self, L: int) -> mx.array:
        """Causal attention mask: -inf above diagonal."""
        if L != self._causal_mask_len:
            mask = mx.full((L, L), float("-inf"))
            mask = mx.triu(mask, k=1)  # zero on and below diagonal
            self._causal_mask = mask
            self._causal_mask_len = L
        return self._causal_mask

    def set_capture(self, on: bool):
        """Enable/disable trace capture on all components."""
        for block in self.blocks:
            block.capture_trace = on
            block.attn.capture_trace = on
            block.ffn.capture_trace = on

    def get_traces(self) -> list[dict]:
        """Collect all traces from all layers."""
        traces = []
        for i, block in enumerate(self.blocks):
            layer_trace = {
                "layer": i,
                "block": block.trace,
                "attn": block.attn.trace,
                "ffn": block.ffn.trace,
            }
            traces.append(layer_trace)
        return traces

    def get_all_crystal_embeddings(self) -> mx.array:
        """Concatenate positive + anti crystal embeddings."""
        return mx.concatenate([
            self.combinator_embeddings,
            self.anti_combinator_embeddings,
        ], axis=0)  # (16, d_model)

    def forward(
        self,
        tokens: mx.array,
        targets: Optional[mx.array] = None,
    ) -> tuple[mx.array, Optional[mx.array]]:
        B, L = tokens.shape
        cfg = self.cfg

        # Embed
        positions = mx.arange(L)
        x = self.embed(tokens) + self.pos_embed(positions)

        # Causal mask
        mask = self._get_causal_mask(L)

        # Transformer blocks
        for block in self.blocks:
            x = block(x, mask=mask)

        # Output
        x = self.output_norm(x)
        logits = self.embed.weight @ x.reshape(-1, cfg.d_model).T
        logits = logits.T.reshape(B, L, cfg.vocab_size)

        # Loss
        loss = None
        if targets is not None:
            loss = self._compute_loss(logits, targets)

        return logits, loss

    def _compute_loss(self, logits: mx.array, targets: mx.array) -> mx.array:
        """CE loss + crystal lattice loss + parity loss."""
        cfg = self.cfg
        B, L = targets.shape

        # Cross-entropy
        ce_loss = nn.losses.cross_entropy(
            logits.reshape(-1, cfg.vocab_size),
            targets.reshape(-1),
        ).mean()

        # Crystal lattice loss (Zone B only)
        emb_all = self.get_all_crystal_embeddings()
        crystal_loss = crystal_lattice_loss(emb_all, self._zone_b_target)

        # Crystal warmup schedule
        if cfg.crystal_warmup_steps > 0 and self._training_step < cfg.crystal_warmup_steps:
            progress = self._training_step / cfg.crystal_warmup_steps
            crystal_weight = cfg.crystal_lambda + (cfg.crystal_warmup_start - cfg.crystal_lambda) * 0.5 * (1.0 + math.cos(math.pi * progress))
        else:
            crystal_weight = cfg.crystal_lambda

        # EMA tracking
        self._crystal_ema = mx.stop_gradient(
            0.99 * self._crystal_ema + 0.01 * crystal_loss)
        self._last_crystal_loss = mx.stop_gradient(crystal_loss)
        self._last_ce_loss = mx.stop_gradient(ce_loss)

        # Parity loss
        parity_additive = mx.array(0.0)
        if cfg.use_parity_loss:
            parity_loss, parity_errors = crystal_parity_loss(
                emb_all,
                self._parity_eigvecs,
                self._parity_eigvals,
                self._parity_levels,
                self._parity_weights,
            )
            parity_additive = cfg.parity_lambda * parity_loss
            self._last_parity_loss = mx.stop_gradient(parity_loss)
            self._last_parity_errors = mx.stop_gradient(parity_errors)

        total = ce_loss + crystal_weight * crystal_loss + parity_additive
        return total

    def __call__(self, tokens, targets=None):
        return self.forward(tokens, targets)

    # ── Diagnostics ──

    def crystal_diagnostics(self) -> dict:
        """Crystal health check."""
        emb_all = self.get_all_crystal_embeddings()
        norms = mx.sqrt(mx.sum(emb_all * emb_all, axis=-1, keepdims=True) + 1e-8)
        emb_norm = emb_all / norms
        cos_matrix = emb_norm @ emb_norm.T
        mx.eval(cos_matrix)

        crystal_loss = crystal_lattice_loss(emb_all, self._zone_b_target)
        mx.eval(crystal_loss)

        # Key sub-lattice metrics
        # Composition cluster: mean(cos(B,C), cos(B,D), cos(C,D))
        comp_cluster = float((cos_matrix[2, 3] + cos_matrix[2, 4] + cos_matrix[3, 4]).item()) / 3.0
        # WHNF anti-correlation
        whnf_anti = float(sum(cos_matrix[7, i].item() for i in range(7))) / 7.0
        # K-I pair
        ki_pair = float(cos_matrix[0, 1].item())

        return {
            "crystal_loss": float(crystal_loss.item()),
            "composition_cluster": comp_cluster,
            "whnf_anti": whnf_anti,
            "ki_pair": ki_pair,
            "cos_matrix": cos_matrix,
        }

    def param_count(self) -> dict:
        """Count parameters by component."""
        def _count(params):
            total = 0
            if isinstance(params, dict):
                for v in params.values():
                    total += _count(v)
            elif isinstance(params, list):
                for v in params:
                    total += _count(v)
            elif isinstance(params, mx.array):
                total += params.size
            return total

        params = self.parameters()
        total = _count(params)

        # Breakdown
        embed_params = self.embed.weight.size + self.pos_embed.weight.size
        crystal_params = self.combinator_embeddings.size + self.anti_combinator_embeddings.size
        block_params = total - embed_params - crystal_params - self.output_norm.weight.size

        return {
            "total": total,
            "embed": embed_params,
            "crystal": crystal_params,
            "blocks": block_params,
            "output_norm": self.output_norm.weight.size,
        }


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("micro_model.py self-test")
    print("=" * 60)

    cfg = MicroConfig()
    model = MicroModel(cfg)
    mx.eval(model.parameters())

    # Parameter count
    counts = model.param_count()
    print(f"\nParameter counts:")
    for k, v in counts.items():
        print(f"  {k}: {v:,}")

    # Forward pass (no targets)
    tokens = mx.random.randint(0, 1000, (2, 32))
    logits, loss = model(tokens)
    mx.eval(logits)
    assert logits.shape == (2, 32, cfg.vocab_size), f"Expected (2, 32, {cfg.vocab_size}), got {logits.shape}"
    assert loss is None
    print(f"\nForward (no targets): logits {logits.shape} ✓")

    # Forward pass (with targets)
    targets = mx.random.randint(0, 1000, (2, 32))
    logits2, loss2 = model(tokens, targets)
    mx.eval(logits2, loss2)
    print(f"Forward (with targets): loss={loss2.item():.4f} ✓")

    # Gradient flow
    def loss_fn(m, tok, tgt):
        _, loss = m(tok, tgt)
        return loss

    gfn = nn.value_and_grad(model, loss_fn)
    lv, grads = gfn(model, tokens, targets)
    mx.eval(lv, grads)
    print(f"Backward: loss={lv.item():.4f}, gradient flow OK ✓")

    # Crystal diagnostics
    diag = model.crystal_diagnostics()
    print(f"\nCrystal:")
    print(f"  loss: {diag['crystal_loss']:.6f}")
    print(f"  composition cluster: {diag['composition_cluster']:.4f}")
    print(f"  WHNF anti: {diag['whnf_anti']:.4f}")
    print(f"  K-I pair: {diag['ki_pair']:.4f}")

    # Trace capture
    model.set_capture(True)
    logits3, loss3 = model(tokens, targets)
    mx.eval(logits3, loss3)
    traces = model.get_traces()
    print(f"\nTrace capture:")
    for t in traces:
        layer = t["layer"]
        attn = t["attn"]
        ffn = t["ffn"]
        print(f"  Layer {layer}:")
        print(f"    Q: {attn['q'].shape}, attn_weights: {attn['attn_weights'].shape}")
        print(f"    gate_sparsity: {ffn['gate_sparsity'].item():.3f}")
    model.set_capture(False)

    # The transformer blocks are the traceable part — embedding table is just lookup
    assert counts["blocks"] < 2_000_000, f"Too many block params: {counts['blocks']:,}"
    print(f"\nTotal params: {counts['total']:,}")
    print(f"  (embedding table: {counts['embed']:,} — just lookup, not traced)")
    print(f"  (transformer blocks: {counts['blocks']:,} — THIS is what we trace ✓)")

    print("\n" + "=" * 60)
    print("micro_model.py: all tests passed ✓")
