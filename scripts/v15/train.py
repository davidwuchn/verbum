"""v15 Phase 2 Training — Attention + Gamma Distillation.

Session 174+. Crystal-native Phase 2 protocol:
  - Plates are FROZEN (they ARE the program).
  - Attention (Q/K/V/O), gammas, RMSNorm weights, and embedding are trained.
  - Loss: cross-entropy on next-token prediction (auto-regressive LM).
  - Optional KL distillation against Qwen3.6-27B teacher logits (offline mode).
  - α diagnostic: per-stride, per-head power-law fit of attention vs distance.
  - Algedonic monitoring: every eval_every steps.

CLI:
    uv run python scripts/v15/train.py \\
        --checkpoint checkpoints/v15-extracted \\
        --data-path data/compile-train.jsonl \\
        --batch-size 4 \\
        --seq-len 512 \\
        --lr 1e-4 \\
        --max-steps 10000 \\
        --log-every 10 \\
        --eval-every 100 \\
        --save-every 1000 \\
        --output-dir checkpoints/v15-train

Architecture note: TernaryPlate.plate1/plate2 are already frozen via
mx.stop_gradient in load_statechart. The MLX freeze() mechanism is used
on TernaryPlate to exclude plate1/plate2 from trainable_parameters() as
well, so the optimizer never receives gradients for them.

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
from pathlib import Path
from typing import Iterator, Optional

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np

# Ensure scripts/v15 is on the path for local imports
sys.path.insert(0, str(Path(__file__).parent))

from config import V15Config, Zone, AttnType, ZONE_NAMES
from model import TensorStatechart, TernaryPlate, AlgedonicSignal, FullAttention, LinearAttention
from load_checkpoint import load_statechart
from td import (TernaryDescent, CrystalThermometer, apply_td_flips,
                collect_td_step_params, fold_and_reset,
                get_affected_gamma_rows, decay_adam_for_affected_rows)


# ══════════════════════════════════════════════════════════════════════
# Logging
# ══════════════════════════════════════════════════════════════════════

def log(msg: str, *, file=None) -> None:
    """Write a timestamped log line to stderr."""
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", file=file or sys.stderr, flush=True)


def log_metrics(step: int, metrics: dict[str, float]) -> None:
    """Emit a structured metrics line for easy grep."""
    pairs = " | ".join(f"{k}={v:.4g}" for k, v in metrics.items())
    log(f"step={step:>7d} | {pairs}")


# ══════════════════════════════════════════════════════════════════════
# Tokenizer
# ══════════════════════════════════════════════════════════════════════

class QwenTokenizer:
    """Thin wrapper around HuggingFace tokenizer for Qwen3.6-27B.

    Falls back to Qwen/Qwen3-0.6B if the 27B variant isn't cached;
    both share the same BBPE vocabulary.
    """

    def __init__(self, model_name: str = "Qwen/Qwen3.6-27B"):
        try:
            from transformers import AutoTokenizer
        except ImportError:
            raise ImportError(
                "transformers is required for tokenization. "
                "Install with: uv add transformers"
            )
        # Try the requested model, fall back to a smaller Qwen with same vocab.
        for name in [model_name, "Qwen/Qwen3-0.6B", "Qwen/Qwen3-4B"]:
            try:
                self._tok = AutoTokenizer.from_pretrained(
                    name, trust_remote_code=True
                )
                log(f"Tokenizer loaded from {name!r} (vocab={len(self._tok)})")
                break
            except Exception:
                continue
        else:
            raise RuntimeError(
                "Could not load any Qwen tokenizer. Check HF cache or network."
            )

        self.eos_id: int = self._tok.eos_token_id or 0
        self.pad_id: int = (
            self._tok.pad_token_id
            if self._tok.pad_token_id is not None
            else self.eos_id
        )
        self.vocab_size: int = len(self._tok)

    def encode(self, text: str, max_length: int | None = None) -> list[int]:
        kwargs = {"add_special_tokens": False}
        if max_length is not None:
            kwargs["truncation"] = True
            kwargs["max_length"] = max_length
        return self._tok.encode(text, **kwargs)


# ══════════════════════════════════════════════════════════════════════
# Data loading
# ══════════════════════════════════════════════════════════════════════

def _load_texts_jsonl(path: Path) -> list[str]:
    """Load texts from JSONL — tries 'text', 'input'+'output', 'input' keys."""
    texts: list[str] = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "text" in obj:
                texts.append(obj["text"])
            elif "input" in obj and "output" in obj:
                # Compilation pair: concatenate with separator
                texts.append(f"{obj['input']} → {obj['output']}")
            elif "input" in obj:
                texts.append(obj["input"])
    return texts


def _load_texts_dir(path: Path) -> list[str]:
    """Load texts from .txt files in a directory."""
    texts: list[str] = []
    for p in sorted(path.glob("**/*.txt")):
        texts.append(p.read_text(errors="replace"))
    return texts


def load_texts(data_path: Path) -> list[str]:
    """Load texts from a JSONL file or a directory of .txt files."""
    if data_path.is_dir():
        texts = _load_texts_dir(data_path)
        log(f"Loaded {len(texts)} texts from directory {data_path}")
    else:
        texts = _load_texts_jsonl(data_path)
        log(f"Loaded {len(texts)} texts from {data_path}")
    if not texts:
        raise ValueError(f"No texts found in {data_path}")
    return texts


def tokenize_texts(
    texts: list[str],
    tokenizer: QwenTokenizer,
    seq_len: int,
) -> np.ndarray:
    """Tokenize all texts and pack into fixed-length windows.

    Returns:
        (N, seq_len) int32 array of token IDs.
    """
    log(f"Tokenizing {len(texts)} texts...")
    all_ids: list[int] = []
    for text in texts:
        ids = tokenizer.encode(text)
        all_ids.extend(ids)
        all_ids.append(tokenizer.eos_id)

    total = len(all_ids)
    n_windows = total // seq_len
    if n_windows == 0:
        raise ValueError(
            f"Not enough tokens ({total}) for seq_len={seq_len}. "
            "Use shorter seq_len or more data."
        )
    # Trim to exact multiple
    ids_arr = np.array(all_ids[: n_windows * seq_len], dtype=np.int32).reshape(
        n_windows, seq_len
    )
    log(f"Tokenized: {total} tokens → {n_windows} windows of {seq_len}")
    return ids_arr


def make_dataloader(
    tokens: np.ndarray,
    batch_size: int,
    shuffle: bool = True,
) -> Iterator[mx.array]:
    """Infinite dataloader — yields (batch_size, seq_len) mx.array batches."""
    n = len(tokens)
    indices = np.arange(n)
    if shuffle:
        np.random.shuffle(indices)
    ptr = 0
    while True:
        if ptr + batch_size > n:
            if shuffle:
                np.random.shuffle(indices)
            ptr = 0
        batch_idx = indices[ptr : ptr + batch_size]
        ptr += batch_size
        yield mx.array(tokens[batch_idx])


# ══════════════════════════════════════════════════════════════════════
# Pre-tokenized npy shard dataloader (streaming, memory-efficient)
# ══════════════════════════════════════════════════════════════════════

def is_shard_dir(path: Path) -> bool:
    """Detect if a directory contains pre-tokenized npy shards."""
    if not path.is_dir():
        return False
    return any(path.glob("shard_*.npy"))


def make_shard_dataloader(
    shard_dir: Path,
    batch_size: int,
    seq_len: int,
    vocab_size: int,
    structured_path: Optional[Path] = None,
    structured_ratio: float = 0.10,
    n_train_shards: int = 54,
    shuffle: bool = True,
    seed: int = 42,
) -> Iterator[mx.array]:
    """Streaming dataloader over pre-tokenized npy shards.

    Memory-efficient: mmap one shard at a time, shuffle chunk positions
    within each shard, shuffle shard order between epochs.

    Optionally mixes in structured data (lambda/code) at a configurable
    ratio — same pattern as v14 MixedDataLoader.

    Adapted from v14/data.py ShardedDataLoader + MixedDataLoader.

    Args:
        shard_dir: Directory containing shard_*.npy files (flat int32).
        batch_size: Sequences per batch.
        seq_len: Tokens per sequence.
        vocab_size: Model vocab size (for clipping OOV tokens).
        structured_path: Optional .npy shard of structured data (lambda, code).
        structured_ratio: Probability of drawing a structured batch (default 10%).
        n_train_shards: Number of shards to use for training (rest = eval).
        shuffle: Whether to shuffle shard/chunk order.
        seed: RNG seed for reproducibility.

    Yields:
        mx.array of shape (batch_size, seq_len).
    """
    shard_files = sorted(shard_dir.glob("shard_*.npy"))
    if not shard_files:
        raise ValueError(f"No shard_*.npy files found in {shard_dir}")

    # Use first n_train_shards for training
    shard_files = shard_files[:n_train_shards]
    n_shards = len(shard_files)

    rng = np.random.RandomState(seed)

    # Peek at first shard for stats
    s0 = np.load(shard_files[0], mmap_mode="r")
    tokens_per_shard = s0.shape[0]
    chunk_size = batch_size * seq_len
    chunks_per_shard = tokens_per_shard // chunk_size
    total_tokens = tokens_per_shard * n_shards

    log(f"Shard dataloader: {n_shards} shards × {tokens_per_shard:,} tokens = {total_tokens:,} total")
    log(f"  {chunks_per_shard:,} batches/shard → {chunks_per_shard * n_shards:,} steps/epoch")

    # Optional structured data
    structured_data = None
    structured_pos = 0
    if structured_path is not None and structured_path.exists():
        structured_data = np.load(str(structured_path), mmap_mode="r")
        log(f"Structured data: {structured_path.name} ({structured_data.shape[0]:,} tokens, "
            f"ratio={structured_ratio:.0%})")
    elif structured_path is not None:
        log(f"WARNING: structured path {structured_path} not found — using prose only")

    def _next_structured() -> mx.array:
        """Draw a batch from the structured shard, wrapping if needed."""
        nonlocal structured_pos
        needed = batch_size * seq_len
        if structured_pos + needed > len(structured_data):
            structured_pos = 0  # wrap
        chunk = np.array(structured_data[structured_pos : structured_pos + needed])
        structured_pos += needed
        chunk = chunk.reshape(batch_size, seq_len).astype(np.int32)
        np.clip(chunk, 0, vocab_size - 1, out=chunk)
        return mx.array(chunk)

    shard_order = np.arange(n_shards)
    epoch = 0

    while True:
        if shuffle:
            rng.shuffle(shard_order)
        epoch_batches = 0

        for file_idx in shard_order:
            # mmap: OS pages in on demand
            shard = np.load(shard_files[file_idx], mmap_mode="r")
            n_tokens = shard.shape[0]
            n_chunks = n_tokens // chunk_size

            if n_chunks == 0:
                continue

            # Shuffle chunk positions within shard
            chunk_indices = np.arange(n_chunks)
            if shuffle:
                rng.shuffle(chunk_indices)

            for ci in chunk_indices:
                # Mixed data: with probability structured_ratio, draw structured
                if structured_data is not None and rng.random() < structured_ratio:
                    yield _next_structured()
                    epoch_batches += 1
                    continue

                start = int(ci) * chunk_size
                chunk = np.array(shard[start : start + chunk_size])
                chunk = chunk.reshape(batch_size, seq_len).astype(np.int32)
                np.clip(chunk, 0, vocab_size - 1, out=chunk)
                yield mx.array(chunk)
                epoch_batches += 1

        epoch += 1
        log(f"Epoch {epoch} complete ({epoch_batches:,} batches) — reshuffling shards")


# ══════════════════════════════════════════════════════════════════════
# KL distillation data (offline teacher logits)
# ══════════════════════════════════════════════════════════════════════

class TeacherLogits:
    """Cached teacher logits for offline KL distillation.

    Expects a directory produced by a separate precompute step:
        teacher_logits/{index:07d}.npz  → keys: 'logits' (seq, vocab)

    If the directory doesn't exist, falls back to next-token CE loss.
    """

    def __init__(self, logits_dir: Path | None):
        self.logits_dir = logits_dir
        self.available = logits_dir is not None and logits_dir.exists()
        if self.available:
            self._files = sorted(logits_dir.glob("*.npz"))
            log(f"Teacher logits: {len(self._files)} files in {logits_dir}")
        else:
            log("Teacher logits: not available — using next-token CE loss only")

    def get(self, batch_index: int) -> mx.array | None:
        """Load teacher logits for a given batch index (if available)."""
        if not self.available:
            return None
        idx = batch_index % len(self._files)
        data = np.load(self._files[idx])
        return mx.array(data["logits"].astype(np.float32))


# ══════════════════════════════════════════════════════════════════════
# Loss functions
# ══════════════════════════════════════════════════════════════════════

def cross_entropy_loss(logits: mx.array, input_ids: mx.array) -> mx.array:
    """Standard next-token prediction loss.

    Args:
        logits: (B, L, V) — student logits
        input_ids: (B, L) — token IDs

    Returns:
        Scalar mean CE loss.
    """
    B, L, V = logits.shape
    # Predict tokens 1..L from context 0..L-1
    pred = logits[:, :-1, :].reshape(-1, V)      # (B*(L-1), V)
    target = input_ids[:, 1:].reshape(-1)          # (B*(L-1),)
    loss = nn.losses.cross_entropy(pred, target, reduction="mean")
    return loss


def kl_distillation_loss(
    student_logits: mx.array,
    teacher_logits: mx.array,
    temperature: float = 2.0,
) -> mx.array:
    """KL divergence distillation loss.

    KL(teacher_soft || student_soft) where distributions are softened at
    temperature T. Teacher is treated as the fixed target.

    Args:
        student_logits: (B, L, V)
        teacher_logits: (B, L, V) — may be precomputed or online
        temperature: softening temperature (default 2.0)

    Returns:
        Scalar mean KL loss (scaled by T² per Hinton 2015).
    """
    T = temperature
    B, L, V = student_logits.shape

    # Trim to prediction window (L-1 tokens)
    s = student_logits[:, :-1, :].reshape(-1, V)
    t = teacher_logits[:, :-1, :].reshape(-1, V)

    # Soft probabilities
    s_log_soft = nn.log_softmax(s / T, axis=-1)
    t_soft = mx.softmax(t / T, axis=-1)

    # KL: sum over vocab, mean over batch/sequence
    # KL(t || s) = sum_v t_v * (log t_v - log s_v)
    # Using: KL = sum_v t_v * log_t_v - sum_v t_v * log_s_v
    # The cross-entropy form: -sum_v t_v * log_s_v
    kl = -mx.sum(t_soft * s_log_soft, axis=-1).mean()
    return kl * (T * T)


def crystal_trace_loss(
    residuals: list,
    crystal_basis: mx.array,
) -> mx.array:
    """Trace loss — maximize crystal coherence of per-stride residuals.

    Projects each stride's residual stream onto the crystal basis and
    measures how much computation aligns with known combinator directions.
    Higher crystal projection energy = student is executing recognizable
    opcodes. Low energy = student is doing something the crystal basis
    can't describe = wrong computation.

    The loss is: 1 - mean(normalized_projection_energy) across strides.
    At 0.0 the student perfectly reproduces crystal-aligned computation.
    At 1.0 the residuals are orthogonal to all combinator directions.

    Args:
        residuals: list of (B, L, d_model) per stride from return_residuals=True
        crystal_basis: (n_strides, n_combinators, d_model) basis vectors

    Returns:
        Scalar trace loss in [0, 1].
    """
    n_strides = min(len(residuals), crystal_basis.shape[0])
    if n_strides == 0:
        return mx.array(0.0)

    coherences = []
    for s in range(n_strides):
        r = residuals[s]           # (B, L, d_model)
        basis_s = crystal_basis[s] # (n_ops, d_model)

        # Project residual onto crystal directions: (B, L, n_ops)
        proj = r @ basis_s.T

        # Energy in crystal space: mean squared projection across batch and seq
        crystal_energy = mx.mean(proj * proj)

        # Total energy of residual
        total_energy = mx.mean(r * r) + 1e-10

        # Fraction of residual energy explained by crystal directions
        coherence = crystal_energy / total_energy
        coherences.append(coherence)

    # Mean coherence across strides → loss = 1 - coherence
    mean_coherence = mx.mean(mx.stack(coherences))
    return 1.0 - mean_coherence


def combined_loss(
    model: TensorStatechart,
    input_ids: mx.array,
    teacher_logits: mx.array | None = None,
    kl_weight: float = 0.5,
    temperature: float = 2.0,
    crystal_basis: mx.array | None = None,
    trace_weight: float = 0.0,
) -> mx.array:
    """Combined CE + optional KL + optional trace loss.

    Args:
        model: The student statechart.
        input_ids: (B, L) token IDs.
        teacher_logits: (B, L, V) if available, else None.
        kl_weight: Weight for KL loss (0 = pure CE, 1 = pure KL).
        temperature: Distillation temperature.
        crystal_basis: (n_strides, n_ops, d_model) for trace loss, or None.
        trace_weight: Weight for trace loss (0.0 = disabled).

    Returns:
        Scalar loss.
    """
    need_residuals = trace_weight > 0.0 and crystal_basis is not None
    result = model(input_ids, return_residuals=need_residuals)
    student_logits = result["logits"]

    ce = cross_entropy_loss(student_logits, input_ids)

    if teacher_logits is not None:
        kl = kl_distillation_loss(student_logits, teacher_logits, temperature)
        loss = (1.0 - kl_weight) * ce + kl_weight * kl
    else:
        loss = ce

    # Trace loss: match crystal opcode projections
    if need_residuals and "residuals" in result:
        tl = crystal_trace_loss(result["residuals"], crystal_basis)
        loss = (1.0 - trace_weight) * loss + trace_weight * tl

    return loss


# ══════════════════════════════════════════════════════════════════════
# α diagnostic — attention decay power law
# ══════════════════════════════════════════════════════════════════════

def _compute_attn_weights_for_stride(
    attn: FullAttention,
    x: mx.array,
    mask: mx.array | None,
) -> mx.array:
    """Compute attention weight matrix for a FullAttention module.

    Returns (B, H, L, L) softmax weights without running o_proj.
    Mirrors the full forward path including q_norm, k_norm, HPE rotation,
    and learnable decay bias so the α diagnostic sees real attention patterns.
    """
    B, L, D = x.shape
    d_head = attn.d_head
    scale = attn.scale

    # Project + per-head QK normalization
    q = attn.q_proj(x).reshape(B, L, attn.n_heads, d_head)
    k = attn.k_proj(x).reshape(B, L, attn.n_kv_heads, d_head)
    q = attn.q_norm(q)
    k = attn.k_norm(k)
    q = q.transpose(0, 2, 1, 3)  # (B, H, L, Dh)
    k = k.transpose(0, 2, 1, 3)

    # HPE rotation on K
    k = attn._apply_hpe_rotation(k, L)

    # GQA repeat
    if attn.n_kv_heads < attn.n_heads:
        repeats = attn.n_heads // attn.n_kv_heads
        k = mx.repeat(k, repeats, axis=1)

    scores = (q @ k.transpose(0, 1, 3, 2)) * scale

    # Learnable log-decay bias
    alpha = mx.exp(attn.log_alpha)
    log_dist = attn._get_log_distances(L)
    scores = scores - alpha * log_dist

    if mask is not None:
        scores = scores + mask
    return mx.softmax(scores, axis=-1)  # (B, H, L, L)


def _fit_power_law_alpha(
    w: np.ndarray,  # (B, H, L, L)
    n_heads: int,
) -> dict[int, float]:
    """Fit α (decay exponent) per head from an attention weight matrix.

    Power law model: E[attn(q, k)] ∝ distance(q, k)^{-α}
    Fit via log-log OLS on the mean weight at each relative distance.

    Returns:
        {head_idx: α}
    """
    B, H, L, _ = w.shape
    result: dict[int, float] = {}

    for h in range(H):
        w_h = w[:, h, :, :]   # (B, L, L)

        # Average attention weight at each relative distance d ∈ [0, L-1]
        # w_h[b, i, j] = attn weight from query i to key j (j <= i, causal)
        # distance = i - j
        dist_sum = np.zeros(L, dtype=np.float64)
        dist_count = np.zeros(L, dtype=np.int64)

        for d in range(L):
            # Collect w_h[:, i, i-d] for i = d..L-1
            diag = np.array([w_h[:, i, i - d] for i in range(d, L)]).ravel()
            if len(diag) > 0:
                dist_sum[d] = diag.sum()
                dist_count[d] = len(diag)

        dist_mean = np.where(dist_count > 0, dist_sum / dist_count, 0.0)

        # Fit on distances 1..L-1 (skip d=0 = self-attention)
        distances = np.arange(1, L, dtype=np.float64)
        attn_vals = dist_mean[1:L]

        valid = attn_vals > 1e-10
        if valid.sum() < 4:
            result[h] = float("nan")
            continue

        log_d = np.log(distances[valid] + 1.0)
        log_a = np.log(attn_vals[valid])

        # OLS: log_a = -α * log_d + c  →  slope = -α
        A = np.column_stack([log_d, np.ones_like(log_d)])
        try:
            coeffs, _, _, _ = np.linalg.lstsq(A, log_a, rcond=None)
            result[h] = float(-coeffs[0])
        except np.linalg.LinAlgError:
            result[h] = float("nan")

    return result


def measure_alpha(
    model: TensorStatechart,
    input_ids: mx.array,
) -> dict[str, float]:
    """Measure attention decay exponent α per stride, per head.

    For each FullAttention stride, computes the attention weight matrix for
    the given batch, then fits a power law: attn(d) ∝ d^{-α} where d is the
    relative distance between query and key positions.

    Strategy: run a per-stride mini forward pass up to each FullAttention
    stride to collect attention weights without modifying the model internals.
    Uses mx.stop_gradient to avoid accumulating a huge compute graph.

    Returns:
        {f"stride_{i:02d}_head_{h:02d}_alpha": α, ...}
        for every FullAttention stride × head.
        α > 0  → local attention (attends more to nearby tokens)
        α ≈ 0  → uniform attention
        α < 0  → anti-local (rare — attends to distant tokens more)
    """
    config = model.config
    B, L = input_ids.shape
    alphas: dict[str, float] = {}

    # Build causal mask once
    mask = model._get_causal_mask(L)

    # Forward pass collecting attention weights stride by stride
    # Use stop_gradient on x between strides — we don't need gradients here
    x = mx.stop_gradient(model.embed(input_ids))

    for stride in model.strides:
        # Only capture FullAttention strides
        if isinstance(stride.attn, FullAttention):
            # Compute attention weights BEFORE applying the stride
            h_normed = mx.stop_gradient(stride.attn_norm(x))
            w_tensor = _compute_attn_weights_for_stride(stride.attn, h_normed, mask)
            w_tensor = mx.stop_gradient(w_tensor)
            mx.eval(w_tensor)

            w_np = np.array(w_tensor)  # (B, H, L, L)
            head_alphas = _fit_power_law_alpha(w_np, config.n_heads)

            for h, alpha_val in head_alphas.items():
                alphas[f"stride_{stride.spec.index:02d}_head_{h:02d}_alpha"] = alpha_val

        # Advance the residual stream through this stride (stop grad between)
        x_new = stride(mx.stop_gradient(x), mask=mask)
        x = mx.stop_gradient(x_new)

    return alphas


# ══════════════════════════════════════════════════════════════════════
# Freeze protocol — only plates are frozen
# ══════════════════════════════════════════════════════════════════════

def freeze_plates(model: TensorStatechart) -> None:
    """Freeze all TernaryPlate plate1/plate2 matrices.

    The gammas (gamma1, gamma2) remain trainable.
    RMSNorm, attention projections, and embedding remain trainable.
    LM head is tied to embedding so it trains automatically.

    When delta plates are enabled, also freezes delta1/delta2 from Adam
    (they are managed by TernaryDescent, not gradient descent).

    Uses MLX Module.freeze(keys=...) so trainable_parameters() excludes
    the plate matrices and the optimizer never receives them.
    """
    frozen_params = 0
    for stride in model.strides:
        for matrix_name in ("gate", "up", "down"):
            plate_module = getattr(stride.ffn, f"{matrix_name}_plate")
            # Freeze plate1 and plate2 (if present)
            keys_to_freeze = ["plate1"]
            if plate_module.plate2 is not None:
                keys_to_freeze.append("plate2")
            # Also freeze delta plates if present (TD manages them, not Adam)
            if plate_module.delta1 is not None:
                keys_to_freeze.append("delta1")
            if plate_module.delta2 is not None:
                keys_to_freeze.append("delta2")
            plate_module.freeze(keys=keys_to_freeze)
            frozen_params += len(keys_to_freeze)

    log(f"Frozen {frozen_params} plate parameter arrays. Gammas remain trainable.")


def compute_trace_td_gradients(
    model: TensorStatechart,
    input_ids: mx.array,
    crystal_basis: mx.array,
) -> dict[str, mx.array]:
    """Compute trace loss gradient w.r.t. ALL delta plates in one pass.

    Single forward+backward through the model. Takes gradient of trace_loss
    w.r.t. a dict of all delta arrays simultaneously.

    The deltas normally live inside stop_gradient (so Adam doesn't touch them).
    Here we temporarily bypass that: substitute base*delta as the plate value
    with gradient flowing through delta, run forward, compute trace loss,
    take gradient w.r.t. all deltas at once.

    Args:
        model: TensorStatechart with delta plates enabled.
        input_ids: (B, L) token IDs for trace evaluation.
        crystal_basis: (n_strides, n_ops, d_model) basis.

    Returns:
        dict[delta_name → (N, K) gradient array] for each delta plate.
    """
    delta_params = model.collect_delta_params()
    if not delta_params:
        return {}

    # Gather all deltas into a single dict for batched gradient
    all_deltas: dict[str, mx.array] = {}
    delta_info: list[tuple[str, object, str, str]] = []  # (name, plate, which, base_attr)
    for name, plate, which in delta_params:
        base_attr = "plate1" if which == "delta1" else "plate2"
        all_deltas[name] = getattr(plate, which)
        delta_info.append((name, plate, which, base_attr))

    def trace_loss_fn(deltas_dict):
        """Compute trace loss with gradients flowing through all deltas."""
        # Temporarily substitute effective = base * delta (differentiable)
        saved = {}
        for dname, plate, which, base_attr in delta_info:
            delta_val = deltas_dict[dname]
            base_val = getattr(plate, base_attr)
            saved[(dname, base_attr)] = getattr(plate, base_attr)
            saved[(dname, which)] = getattr(plate, which)
            # Replace plate with effective (grad flows through delta)
            setattr(plate, base_attr, base_val * delta_val)
            # Disable delta so _effective() doesn't double-apply
            setattr(plate, which, None)

        result = model(input_ids, return_residuals=True)

        # Restore all plates
        for dname, plate, which, base_attr in delta_info:
            setattr(plate, base_attr, saved[(dname, base_attr)])
            setattr(plate, which, saved[(dname, which)])

        if "residuals" not in result:
            return mx.array(0.0)
        return crystal_trace_loss(result["residuals"], crystal_basis)

    # One forward+backward for ALL deltas
    grad_fn = mx.grad(trace_loss_fn)
    grads = grad_fn(all_deltas)
    mx.eval(grads)

    return grads


# NOTE: _trace_etch_step_REMOVED preserved as historical reference.
# Replaced by delta plate TD with trace routing (session 177).
# See mementum/knowledge/trace-guided-etching.md for the design.
def _trace_etch_step_REMOVED(
    model: TensorStatechart,
    crystal_basis: mx.array,
    input_ids: mx.array,
    max_flips_per_plate: int = 50,
    threshold: float = 0.01,
) -> dict:
    """Trace-guided etching: flip plate signs to improve crystal coherence.

    Temporarily unfreezes plates, computes trace loss gradient w.r.t.
    each plate1/plate2, identifies positions where flipping the sign
    would reduce trace loss (guided by gradient direction), flips the
    top candidates, and re-freezes.

    Unlike blind TD (which uses NTP loss), trace etching uses the
    crystal basis projection — an 11-dimensional signal that says
    "this position should point more toward B-compose" rather than
    "this position is wrong for predicting the next token."

    Args:
        model: The student statechart (plates will be modified in-place).
        crystal_basis: (n_strides, n_ops, d_model) basis for trace loss.
        input_ids: (B, L) input batch to evaluate trace loss on.
        max_flips_per_plate: maximum sign flips per plate per etch step.
        threshold: minimum gradient magnitude to consider a flip.

    Returns:
        dict with etch statistics: total_flips, per_stride_flips, loss_before, loss_after.
    """
    n_strides = min(len(model.strides), crystal_basis.shape[0])
    total_flips = 0
    per_stride = {}

    # Measure trace loss before
    result_before = model(input_ids, return_residuals=True)
    loss_before = float(crystal_trace_loss(result_before["residuals"], crystal_basis).item())

    for si in range(n_strides):
        stride = model.strides[si]
        stride_flips = 0

        for plate_name in ("gate_plate", "up_plate", "down_plate"):
            plate_mod = getattr(stride.ffn, plate_name)

            for which in ("plate1", "plate2"):
                plate_arr = getattr(plate_mod, which)
                if plate_arr is None:
                    continue

                # Compute gradient of trace loss w.r.t. this plate
                # We need a function that takes the plate as input
                def trace_fn(plate_val):
                    # Temporarily substitute the plate
                    old = getattr(plate_mod, which)
                    setattr(plate_mod, which, plate_val)
                    res = model(input_ids, return_residuals=True)
                    tl = crystal_trace_loss(res["residuals"], crystal_basis)
                    setattr(plate_mod, which, old)
                    return tl

                grad_fn = mx.grad(trace_fn)
                plate_grad = grad_fn(plate_arr)
                mx.eval(plate_grad)

                # The gradient tells us: to decrease trace loss, move plate in -grad direction.
                # For a ternary plate, "moving" means flipping signs.
                # A position with plate=+1 and grad > 0 means:
                #   flipping to -1 would move in -grad direction → reduces loss.
                # A position with plate=-1 and grad < 0 means:
                #   flipping to +1 would move in -grad direction → reduces loss.
                # Flip benefit = -plate * grad (positive = beneficial flip)

                plate_np = np.array(plate_arr)
                grad_np = np.array(plate_grad)

                flip_benefit = -plate_np * grad_np
                # Only consider non-zero positions (zero = structurally absent)
                flip_benefit[plate_np == 0] = -np.inf

                # Find top candidates
                flat_benefit = flip_benefit.flatten()
                top_k = min(max_flips_per_plate, int(np.sum(flat_benefit > threshold)))
                if top_k == 0:
                    continue

                top_indices = np.argpartition(flat_benefit, -top_k)[-top_k:]
                top_indices = top_indices[flat_benefit[top_indices] > threshold]

                if len(top_indices) == 0:
                    continue

                # Flip the signs
                new_plate = plate_np.copy()
                for idx in top_indices:
                    row, col = divmod(idx, plate_np.shape[1])
                    new_plate[row, col] *= -1

                # Apply
                setattr(plate_mod, which, mx.array(new_plate))
                stride_flips += len(top_indices)

            # Re-freeze this plate
            keys_to_freeze = ["plate1"]
            if plate_mod.plate2 is not None:
                keys_to_freeze.append("plate2")
            plate_mod.freeze(keys=keys_to_freeze)

        per_stride[si] = stride_flips
        total_flips += stride_flips

    # Measure trace loss after
    result_after = model(input_ids, return_residuals=True)
    loss_after = float(crystal_trace_loss(result_after["residuals"], crystal_basis).item())
    mx.eval(model.parameters())

    return {
        "total_flips": total_flips,
        "per_stride": per_stride,
        "loss_before": loss_before,
        "loss_after": loss_after,
        "delta": loss_before - loss_after,
    }


def count_trainable(model: TensorStatechart) -> int:
    """Count the number of unique trainable scalar values in the model.

    De-duplicates by array identity to handle tied weights (embed = lm_head).
    """
    total = 0
    seen: set[int] = set()
    flat = dict(nn.utils.tree_flatten(model.trainable_parameters()))
    for arr in flat.values():
        if id(arr) not in seen:
            seen.add(id(arr))
            total += arr.size
    return total


def report_trainable_summary(model: TensorStatechart) -> None:
    """Log a breakdown of trainable parameters by component type.

    Note: embed.weight and lm_head.weight are the same array (tied weights).
    Both paths appear in trainable_parameters() — the optimizer handles aliasing
    correctly, but the summary de-duplicates them by id() to avoid double-counting.
    """
    flat = dict(nn.utils.tree_flatten(model.trainable_parameters()))

    summary: dict[str, int] = {
        "attn_qkvo": 0,
        "gammas": 0,
        "rms_norms": 0,
        "embedding": 0,
        "other": 0,
    }

    seen_ids: set[int] = set()

    for key, arr in flat.items():
        arr_id = id(arr)
        if arr_id in seen_ids:
            continue  # skip tied duplicates
        seen_ids.add(arr_id)

        n = arr.size
        if any(p in key for p in ["q_proj", "k_proj", "v_proj", "o_proj"]):
            summary["attn_qkvo"] += n
        elif "gamma" in key and "norm" not in key:
            summary["gammas"] += n
        elif "norm" in key or "rms" in key.lower():
            summary["rms_norms"] += n
        elif "embed" in key or "lm_head" in key:
            # embed and lm_head are tied — count once under "embedding"
            summary["embedding"] += n
        else:
            summary["other"] += n

    total = sum(summary.values())
    log(f"Trainable parameters (unique): {total:,}  [embed+lm_head tied, counted once]")
    for name, count in summary.items():
        if count > 0:
            log(f"  {name:16s}: {count:>12,}  ({100*count/total:.1f}%)")


# ══════════════════════════════════════════════════════════════════════
# Checkpoint save / load
# ══════════════════════════════════════════════════════════════════════

def save_checkpoint(
    model: TensorStatechart,
    optimizer: optim.Optimizer,
    step: int,
    output_dir: Path,
    metrics: dict[str, float] | None = None,
) -> Path:
    """Save trainable weights + optimizer state to a step directory.

    Only trainable weights are saved. Plate matrices (frozen) are NOT
    re-saved here — the original extraction checkpoint is the source of
    truth for plates.

    Directory: {output_dir}/step_{step:07d}/
    Files:
        weights.npz      — trainable model parameters (safetensors would be
                           cleaner but .npz is simpler with mx.savez)
        optimizer.npz    — optimizer state
        meta.json        — step, loss, timestamp, config summary
    """
    ckpt_dir = output_dir / f"step_{step:07d}"
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    # Trainable weights only
    trainable = dict(nn.utils.tree_flatten(model.trainable_parameters()))
    mx.savez(str(ckpt_dir / "weights.npz"), **{
        k: mx.array(v) for k, v in trainable.items()
    })

    # Optimizer state
    opt_state = dict(nn.utils.tree_flatten(optimizer.state))
    if opt_state:
        mx.savez(str(ckpt_dir / "optimizer.npz"), **{
            k: mx.array(v) for k, v in opt_state.items()
        })

    # Metadata
    meta = {
        "step": step,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "d_model": model.config.d_model,
        "d_ff": model.config.d_ff,
        "n_strides": model.config.n_strides,
        "vocab_size": model.config.vocab_size,
        "trainable_params": count_trainable(model),
    }
    if metrics:
        meta["metrics"] = metrics

    with open(ckpt_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    log(f"Checkpoint saved → {ckpt_dir}")
    return ckpt_dir


def find_latest_checkpoint(output_dir: Path) -> Path | None:
    """Find the most recent step checkpoint directory."""
    if not output_dir.exists():
        return None
    dirs = sorted(
        [d for d in output_dir.iterdir() if d.is_dir() and d.name.startswith("step_")],
        key=lambda d: int(d.name.split("_")[1]),
    )
    return dirs[-1] if dirs else None


def _save_delta_state(
    model: TensorStatechart,
    td: TernaryDescent,
    ckpt_dir: Path,
) -> None:
    """Save delta plate values and TD moment state."""
    delta_arrays = {}
    for name, plate, which in model.collect_delta_params():
        delta_val = getattr(plate, which)
        if delta_val is not None:
            delta_arrays[name] = delta_val

    if delta_arrays:
        mx.savez(str(ckpt_dir / "delta_plates.npz"), **delta_arrays)
        log(f"  Saved {len(delta_arrays)} delta plate arrays")

    # Save TD moments
    td_state = {}
    for name, (direction, magnitude) in td._state.items():
        td_state[f"{name}.direction"] = direction
        td_state[f"{name}.magnitude"] = magnitude
    for name, (last_step, count) in td._flip_history.items():
        td_state[f"{name}.last_flip_step"] = last_step
        td_state[f"{name}.flip_count"] = count

    if td_state:
        mx.savez(str(ckpt_dir / "td_state.npz"), **td_state)
        log(f"  Saved TD state: {len(td_state)} arrays, step_count={td.step_count}")

    # Save TD metadata
    td_meta = {
        "step_count": td.step_count,
        "flip_rate": td.flip_rate,
        "warmup_steps": td.warmup_steps,
        "flip_interval": td.flip_interval,
        "min_confidence": td.min_confidence,
    }
    with open(ckpt_dir / "td_meta.json", "w") as f:
        json.dump(td_meta, f, indent=2)


def _load_delta_state(
    model: TensorStatechart,
    td: TernaryDescent,
    ckpt_dir: Path,
) -> None:
    """Load delta plate values and TD moment state from checkpoint."""
    # Load delta plates
    delta_path = ckpt_dir / "delta_plates.npz"
    if delta_path.exists():
        saved = mx.load(str(delta_path))
        name_to_plate = {name: (plate, which)
                         for name, plate, which in model.collect_delta_params()}
        loaded = 0
        for name, arr in saved.items():
            if name in name_to_plate:
                plate, which = name_to_plate[name]
                setattr(plate, which, arr)
                loaded += 1
        log(f"  Loaded {loaded} delta plate arrays from {delta_path}")

    # Load TD moments
    td_state_path = ckpt_dir / "td_state.npz"
    if td_state_path.exists():
        saved = dict(mx.load(str(td_state_path)))
        for key, arr in saved.items():
            parts = key.rsplit(".", 1)
            if len(parts) != 2:
                continue
            name, field = parts
            if field == "direction":
                _, mag = td._get_state(name, arr.shape)
                td._state[name] = (arr, mag)
            elif field == "magnitude":
                dir_, _ = td._get_state(name, arr.shape)
                td._state[name] = (dir_, arr)
            elif field == "last_flip_step":
                _, count = td._get_flip_history(name, arr.shape)
                td._flip_history[name] = (arr, count)
            elif field == "flip_count":
                last, _ = td._get_flip_history(name, arr.shape)
                td._flip_history[name] = (last, arr)
        log(f"  Loaded TD state from {td_state_path}")

    # Load TD metadata
    td_meta_path = ckpt_dir / "td_meta.json"
    if td_meta_path.exists():
        with open(td_meta_path) as f:
            meta = json.load(f)
        td.step_count = meta.get("step_count", 0)
        log(f"  Resumed TD at step_count={td.step_count}")


def load_checkpoint_weights(
    model: TensorStatechart,
    optimizer: optim.Optimizer,
    ckpt_dir: Path,
) -> int:
    """Resume from a training checkpoint. Returns the step number."""
    weights_path = ckpt_dir / "weights.npz"
    if weights_path.exists():
        # Load only the weights that exist in the checkpoint (strict=False)
        # because plates are not saved here
        saved = mx.load(str(weights_path))
        model.load_weights(list(saved.items()), strict=False)
        log(f"Resumed model weights from {weights_path}")

    opt_path = ckpt_dir / "optimizer.npz"
    if opt_path.exists():
        saved_opt = dict(mx.load(str(opt_path)))
        optimizer.state.update(saved_opt)
        log(f"Resumed optimizer state from {opt_path}")

    meta_path = ckpt_dir / "meta.json"
    step = 0
    if meta_path.exists():
        with open(meta_path) as f:
            meta = json.load(f)
        step = meta.get("step", 0)

    log(f"Resumed from step {step}")
    return step


# ══════════════════════════════════════════════════════════════════════
# Learning rate schedule — linear warmup + cosine decay
# ══════════════════════════════════════════════════════════════════════

def make_lr_schedule(
    peak_lr: float,
    warmup_steps: int,
    total_steps: int,
    min_lr_ratio: float = 0.1,
) -> object:
    """Linear warmup → cosine decay LR schedule."""
    min_lr = peak_lr * min_lr_ratio
    warmup = optim.linear_schedule(0.0, peak_lr, steps=warmup_steps)
    cosine = optim.cosine_decay(
        peak_lr,
        decay_steps=max(1, total_steps - warmup_steps),
        end=min_lr,
    )
    return optim.join_schedules([warmup, cosine], [warmup_steps])


# ══════════════════════════════════════════════════════════════════════
# Algedonic report
# ══════════════════════════════════════════════════════════════════════

def run_algedonic_check(
    model: TensorStatechart,
    input_ids: mx.array,
    step: int,
) -> None:
    """Run model with algedonic monitoring and log any non-OK signals."""
    result = model(input_ids, return_algedonic=True)
    signals = result.get("algedonic_signals", [])
    non_ok = [(i, z, s) for i, z, s in signals if s != AlgedonicSignal.OK]
    if non_ok:
        log(f"  ⚠ ALGEDONIC at step {step}:")
        for stride_idx, zone, sig in non_ok:
            log(f"    Stride {stride_idx:2d} ({zone.name:8s}): {sig.name}")
    else:
        ok_count = len(signals)
        log(f"  Algedonic: {ok_count}/{ok_count} strides OK ✓")


# ══════════════════════════════════════════════════════════════════════
# Per-zone loss breakdown
# ══════════════════════════════════════════════════════════════════════

def per_zone_grad_norm(
    grads: dict,
    model: TensorStatechart,
) -> dict[str, float]:
    """Compute gradient norm per zone for diagnostics.

    Returns {zone_name: grad_norm, ...}.
    """
    zone_norms: dict[str, float] = {}
    flat_grads = dict(nn.utils.tree_flatten(grads))

    for zone in Zone:
        # Identify strides in this zone
        specs = [s for s in model.strides if s.zone == zone]
        indices = {s.spec.index for s in specs}
        prefix_patterns = [f"strides.{i}." for i in indices]

        zone_sq = 0.0
        for key, g in flat_grads.items():
            if any(key.startswith(p) for p in prefix_patterns):
                if hasattr(g, "size"):
                    zone_sq += float(mx.sum(g * g).item())

        zone_norms[ZONE_NAMES[zone]] = math.sqrt(zone_sq)

    return zone_norms


# ══════════════════════════════════════════════════════════════════════
# Combinator phase profiler — track B→K→I phase cascade
# ══════════════════════════════════════════════════════════════════════

# Fixed diagnostic sentences: same every eval for consistent measurement.
# Split into PROSE (zero mathematical/logical symbols) and SYMBOLIC
# (lambda, math, =) to track whether they show different combinator profiles.
# Symbol contamination concern: session 175 identified that "=" in probes
# may trigger compute circuitry independently of lambda syntax.
PROSE_PROBES = [
    "The old man walked slowly through the crowded market.",
    "She remembered the day they first met at the library.",
    "Rain fell steadily on the tin roof all night long.",
    "The children played in the park until the sun went down.",
    "He opened the letter and read it twice before responding.",
    "The professor explained the concept to the confused students.",
    "The capital of France is Paris, a city known for its history.",
    "The teacher who the student admires reads every morning.",
    "Birds gathered on the wire above the quiet street.",
    "Once upon a time there was a small village near the mountains.",
]

SYMBOLIC_PROBES = [
    "λx. λy. x y",
    "∀x. (artist(x) → knows(x, baker))",
    "(λx. capital_of(x)) France =",
    "B f g x = f (g x)",
    "K a b = a",
    "2 + 3 = 5",
    "def fibonacci(n): return n if n < 2 else fibonacci(n-1) + fibonacci(n-2)",
    "If the dog runs → the cat sleeps.",
    "Every artist knows a baker. → ∀x. (artist(x) → knows(x, baker))",
    "I x = x",
]


def load_crystal_basis(checkpoint_dir: str | Path) -> np.ndarray | None:
    """Load per-stride trace basis from extracted checkpoint.

    Prefers expanded PCA basis (50-dim, 90%+ coverage) over KIBC (11-dim, ~5%).
    Falls back to KIBC crystal basis if expanded not available.

    Returns:
        (n_strides, n_components, d_model) array, or None if not found.
    """
    checkpoint_dir = Path(checkpoint_dir)

    # Prefer expanded PCA basis
    expanded_path = checkpoint_dir / "expanded_trace_basis.npz"
    if expanded_path.exists():
        data = np.load(expanded_path)
        basis = data["pca_components"]  # (n_strides, 50, d_model)
        ev = data["explained_variance"]
        mean_cumvar = float(np.mean([np.cumsum(ev[s])[-1] for s in range(basis.shape[0])]))
        log(f"Expanded PCA basis loaded: {basis.shape[0]} strides × {basis.shape[1]} PCs "
            f"(mean coverage: {mean_cumvar:.1%})")
        return basis

    # Fallback to KIBC crystal basis
    basis_path = checkpoint_dir / "crystal_basis_d_model.npz"
    if not basis_path.exists():
        log(f"Crystal basis not found at {basis_path} — profiler disabled")
        return None
    data = np.load(basis_path)
    basis = data["per_stride_basis"]  # (19, 11, 1280)
    names = list(data["combinator_names"])
    log(f"KIBC crystal basis loaded: {basis.shape[0]} strides × {basis.shape[1]} combinators "
        f"({', '.join(names[:4])}...) — consider building expanded basis for better coverage")
    return basis


def _profile_probe_set(
    model: "TensorStatechart",
    tokenizer: "QwenTokenizer",
    crystal_basis: np.ndarray,
    prompts: list[str],
    combinator_names: list[str],
) -> dict:
    """Run one set of probes and return per-stride combinator profile."""
    n_strides = crystal_basis.shape[0]
    n_ops = crystal_basis.shape[1]

    # Tokenize (truncate to reasonable length)
    all_ids = []
    for prompt in prompts:
        ids = tokenizer.encode(prompt)[:128]
        all_ids.append(ids)

    # Pad to same length for batching
    max_len = max(len(ids) for ids in all_ids)
    padded = np.zeros((len(all_ids), max_len), dtype=np.int32)
    for i, ids in enumerate(all_ids):
        padded[i, :len(ids)] = ids
    input_ids = mx.array(padded)

    # Forward with residual capture
    result = model(input_ids, return_residuals=True)
    residuals = result["residuals"]

    profile = {}
    for s in range(min(n_strides, len(residuals))):
        r = residuals[s]
        basis_s = mx.array(crystal_basis[s])
        proj = r @ basis_s.T
        energy = mx.mean(proj * proj, axis=(0, 1))
        mx.eval(energy)
        energy_np = np.array(energy)

        total_energy = energy_np.sum()
        fracs = energy_np / total_energy if total_energy > 0 else np.zeros(n_ops)

        stride_profile = {combinator_names[i]: float(fracs[i]) for i in range(n_ops)}
        stride_profile["_dominant"] = combinator_names[int(np.argmax(fracs))]
        stride_profile["_total_energy"] = float(total_energy)
        profile[s] = stride_profile

    return profile


def _zone_summary(
    profile: dict,
    model: "TensorStatechart",
    combinator_names: list[str],
) -> dict:
    """Compute zone-averaged combinator profiles from per-stride data."""
    zone_names = {}
    for s in profile:
        zone_names[s] = model.strides[s].zone.name

    zone_profiles = {}
    for zone in Zone:
        zone_strides = [s for s in profile if zone_names.get(s) == zone.name]
        if not zone_strides:
            continue
        avg = {}
        for op in combinator_names:
            avg[op] = float(np.mean([profile[s][op] for s in zone_strides]))
        zone_profiles[zone.name] = {"profile": avg, "dominant": max(avg, key=avg.get)}

    return zone_profiles


def run_combinator_profile(
    model: "TensorStatechart",
    tokenizer: "QwenTokenizer",
    crystal_basis: np.ndarray,
    step: int,
    output_dir: Path,
) -> dict:
    """Profile combinator activation per stride using diagnostic probes.

    Runs two probe sets (PROSE and SYMBOLIC) separately through the model,
    captures residual stream after each stride, projects onto per-stride
    crystal basis. Logs both profiles for phase transition tracking and
    symbol contamination monitoring.

    Returns dict with per-stride dominant combinator and activation profiles
    for both probe sets.
    """
    combinator_names = ["K", "I", "B", "C", "D", "Y", "W",
                        "beta_K", "beta_I", "beta_apply", "beta_compose"]

    # Run both probe sets
    prose_profile = _profile_probe_set(
        model, tokenizer, crystal_basis, PROSE_PROBES, combinator_names,
    )
    symbolic_profile = _profile_probe_set(
        model, tokenizer, crystal_basis, SYMBOLIC_PROBES, combinator_names,
    )

    prose_zones = _zone_summary(prose_profile, model, combinator_names)
    symbolic_zones = _zone_summary(symbolic_profile, model, combinator_names)

    # Log prose profile
    log("  Combinator profile (PROSE — no symbols):")
    for s in sorted(prose_profile):
        p = prose_profile[s]
        zone = model.strides[s].zone.name
        sorted_ops = sorted(combinator_names, key=lambda op: p[op], reverse=True)[:3]
        top3 = " ".join(f"{op}={p[op]:.2f}" for op in sorted_ops)
        log(f"    stride {s:02d} ({zone:8s}): {p['_dominant']:>12} | {top3}")

    log("  Prose zone dominants:")
    for zname, zp in prose_zones.items():
        log(f"    {zname:8s}: {zp['dominant']}")

    # Log symbolic profile
    log("  Combinator profile (SYMBOLIC — λ, =, →):")
    for s in sorted(symbolic_profile):
        p = symbolic_profile[s]
        zone = model.strides[s].zone.name
        sorted_ops = sorted(combinator_names, key=lambda op: p[op], reverse=True)[:3]
        top3 = " ".join(f"{op}={p[op]:.2f}" for op in sorted_ops)
        log(f"    stride {s:02d} ({zone:8s}): {p['_dominant']:>12} | {top3}")

    log("  Symbolic zone dominants:")
    for zname, zp in symbolic_zones.items():
        log(f"    {zname:8s}: {zp['dominant']}")

    # Log comparison
    log("  Prose vs Symbolic total energy ratio per zone:")
    for zname in prose_zones:
        p_total = sum(prose_zones[zname]["profile"].values())
        s_total = sum(symbolic_zones.get(zname, {"profile": {}})["profile"].values())
        ratio = s_total / p_total if p_total > 0 else 0
        log(f"    {zname:8s}: symbolic/prose = {ratio:.2f}x")

    # Save to JSON
    result_data = {
        "step": step,
        "prose": {"per_stride": prose_profile, "per_zone": prose_zones},
        "symbolic": {"per_stride": symbolic_profile, "per_zone": symbolic_zones},
        "combinator_names": combinator_names,
    }
    prof_path = output_dir / f"combinator_step_{step:07d}.json"
    with open(prof_path, "w") as f:
        json.dump(result_data, f, indent=2)

    return result_data


# ══════════════════════════════════════════════════════════════════════
# Main training loop
# ══════════════════════════════════════════════════════════════════════

def train(args: argparse.Namespace) -> None:
    """Phase 2 training entry point."""

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Load model ──────────────────────────────────────────────────
    log(f"Loading statechart from {args.checkpoint} ...")
    model = load_statechart(args.checkpoint, freeze_plates=True)
    config = model.config

    # ── Enable delta plates (if requested) ──────────────────────────
    td_optimizer = None
    if args.delta_plates:
        n_delta = model.enable_delta_plates()
        log(f"Delta plates ENABLED: {n_delta} plate modules with deltas")

    # Freeze plates via MLX mechanism (so trainable_parameters() excludes them)
    # This freezes base plates AND delta plates (deltas managed by TD, not Adam)
    freeze_plates(model)
    report_trainable_summary(model)

    # ── TernaryDescent (if delta plates enabled) ─────────────────────
    thermometer = None
    if args.delta_plates:
        td_optimizer = TernaryDescent(
            flip_rate=args.td_flip_rate,
            warmup_steps=args.td_warmup,
            flip_interval=args.td_flip_interval,
            min_confidence=args.td_min_confidence,
        )
        thermometer = CrystalThermometer(recent_window=args.td_flip_interval * 5)
        log(f"TernaryDescent: rate={args.td_flip_rate}, warmup={args.td_warmup}, "
            f"interval={args.td_flip_interval}, min_conf={args.td_min_confidence}")
        log(f"CrystalThermometer: recent_window={args.td_flip_interval * 5}")

    n_trainable = count_trainable(model)
    log(f"Total trainable: {n_trainable:,} parameters")
    log(f"Vocab size: {config.vocab_size}")

    # ── Tokenizer ───────────────────────────────────────────────────
    tokenizer = QwenTokenizer()
    # Sanity-check vocab alignment
    if tokenizer.vocab_size != config.vocab_size:
        log(
            f"WARNING: tokenizer vocab ({tokenizer.vocab_size}) ≠ "
            f"model vocab ({config.vocab_size}). "
            f"Tokens will be clipped to model vocab."
        )

    # ── Teacher logits (optional) ────────────────────────────────────
    teacher_logits_store = TeacherLogits(
        Path(args.teacher_logits_dir) if args.teacher_logits_dir else None
    )

    # ── Optimizer + LR schedule ──────────────────────────────────────
    warmup_steps = max(1, args.max_steps // 20)  # 5% warmup
    lr_schedule = make_lr_schedule(args.lr, warmup_steps, args.max_steps)

    optimizer = optim.AdamW(
        learning_rate=lr_schedule,
        betas=[0.9, 0.95],
        eps=1e-8,
        weight_decay=args.weight_decay,
    )

    log(f"Optimizer: AdamW  lr={args.lr}  wd={args.weight_decay}  warmup={warmup_steps}")

    # ── Crystal basis (for combinator profiling) ─────────────────────
    crystal_basis = load_crystal_basis(args.checkpoint)

    # ── Resume if checkpoint exists ──────────────────────────────────
    start_step = 0
    if not args.no_resume:
        latest = find_latest_checkpoint(output_dir)
        if latest is not None:
            start_step = load_checkpoint_weights(model, optimizer, latest)
        else:
            log("No existing checkpoint found — starting from scratch")

    # ── Data (after resume so start_step seeds the shuffle) ─────────
    data_path = Path(args.data_path)
    if is_shard_dir(data_path):
        # Pre-tokenized npy shards (Dolma, etc.) — stream without loading all into RAM
        log(f"Detected pre-tokenized npy shards in {data_path}")
        structured_path = Path(args.structured_path) if args.structured_path else None
        # Seed from start_step so each restart/resume sees different shard order.
        # Same start_step = reproducible. Different start_step = different data.
        data_seed = 42 + start_step
        log(f"Data seed: {data_seed} (base=42 + start_step={start_step})")
        dataloader = make_shard_dataloader(
            data_path,
            batch_size=args.batch_size,
            seq_len=args.seq_len,
            vocab_size=config.vocab_size,
            structured_path=structured_path,
            structured_ratio=args.structured_ratio,
            n_train_shards=args.n_train_shards,
            shuffle=True,
            seed=data_seed,
        )
    else:
        # Legacy: text data (JSONL / .txt directory) — tokenize and load into RAM
        texts = load_texts(data_path)
        tokens = tokenize_texts(texts, tokenizer, args.seq_len)
        # Clip token IDs to model vocab (handles tokenizer/model mismatch)
        tokens = np.clip(tokens, 0, config.vocab_size - 1).astype(np.int32)
        dataloader = make_dataloader(tokens, args.batch_size, shuffle=True)

    # ── Crystal basis for trace loss ────────────────────────────────
    trace_basis_mx = None
    if args.trace_weight > 0.0 and crystal_basis is not None:
        trace_basis_mx = mx.array(crystal_basis)
        log(f"Trace loss ENABLED: weight={args.trace_weight}, basis shape={crystal_basis.shape}")
    elif args.trace_weight > 0.0:
        log(f"⚠ Trace loss requested (weight={args.trace_weight}) but no crystal basis — disabled")
        args.trace_weight = 0.0

    # ── Build value_and_grad function ────────────────────────────────
    # MLX value_and_grad computes grads w.r.t. model.trainable_parameters()
    # Capture trace config in closure
    _trace_weight = args.trace_weight
    _trace_basis = trace_basis_mx

    def loss_fn(model: TensorStatechart, input_ids: mx.array, teacher_l: mx.array | None):
        return combined_loss(
            model,
            input_ids,
            teacher_logits=teacher_l,
            kl_weight=args.kl_weight,
            temperature=args.kl_temperature,
            crystal_basis=_trace_basis,
            trace_weight=_trace_weight,
        )

    loss_and_grad = nn.value_and_grad(model, loss_fn)

    # ── Training state ───────────────────────────────────────────────
    loss_history: list[float] = []
    t0 = time.time()

    log(f"Starting training at step {start_step} (max {args.max_steps})")
    log(f"Batch size: {args.batch_size}  Seq len: {args.seq_len}")
    log(f"Log every: {args.log_every}  Eval every: {args.eval_every}  Save every: {args.save_every}")

    # ── Main loop ────────────────────────────────────────────────────
    for step, batch in enumerate(dataloader, start=start_step):
        if step >= args.max_steps:
            break

        # Optionally attach teacher logits
        teacher_l = teacher_logits_store.get(step) if teacher_logits_store.available else None

        # Truncate batch to actual seq_len (already fixed by tokenize_texts)
        input_ids = batch  # (B, seq_len)

        # Forward + backward
        loss, grads = loss_and_grad(model, input_ids, teacher_l)

        # Gradient clipping
        clipped_grads, grad_norm = optim.clip_grad_norm(grads, max_norm=args.grad_clip)

        # Parameter update
        optimizer.update(model, clipped_grads)

        # MLX: commit computation graph
        mx.eval(model.parameters(), optimizer.state)

        # ── TernaryDescent step (if delta plates enabled) ────────────
        td_flips = 0
        td_candidates = 0
        if td_optimizer is not None and _trace_basis is not None:
            # Compute trace loss gradient w.r.t. delta plates.
            # Use a small slice of the batch (1 seq, 512 tokens) — trace
            # gradient just needs any forward pass to see crystal coherence,
            # not the full training batch. This keeps TD overhead ~10%.
            trace_input = input_ids[:1, :512]
            trace_grads = compute_trace_td_gradients(
                model, trace_input, _trace_basis,
            )

            # Build delta_params list for TD
            td_params = []
            for name, plate, which in model.collect_delta_params():
                delta_val = getattr(plate, which)
                base_attr = "plate1" if which == "delta1" else "plate2"
                base_val = getattr(plate, base_attr)
                grad_eff = trace_grads.get(name)
                if grad_eff is None or grad_eff.shape != delta_val.shape:
                    continue
                # no_block=True: direct +1 ↔ -1 flips only.
                # Structural zeros are already placed in the base plate.
                # The active 70% IS the program — never zero it via staging.
                td_params.append((name, delta_val, grad_eff, base_val, True))

            if td_params:
                td_result = td_optimizer.step(td_params, training_step=step)
                td_flips = td_result.get("total_flips", 0)
                td_candidates = td_result.get("etch_total_candidates", 0)

                # Record into thermometer
                if thermometer is not None:
                    thermometer.record(td_result, step)

                # Apply flips to model + notify Adam of stale rows
                if td_flips > 0:
                    apply_td_flips(model, td_result)
                    # Decay Adam moments for affected gamma rows.
                    # Without this, Adam pushes gamma in the wrong direction
                    # for ~10 steps after a topology change.
                    affected = get_affected_gamma_rows(model, td_result)
                    n_decayed = decay_adam_for_affected_rows(
                        optimizer, model, affected, decay_factor=0.1,
                    )
                    mx.eval(model.parameters())

        # ── Periodic fold (if requested) ─────────────────────────────
        if (
            td_optimizer is not None
            and args.fold_every > 0
            and step > 0
            and step % args.fold_every == 0
        ):
            log(f"  FOLD at step {step} — consolidating delta plates into base")
            fold_and_reset(model, td_optimizer)
            # Re-freeze after fold (delta arrays were replaced)
            freeze_plates(model)
            mx.eval(model.parameters())
            log(f"  Fold complete. Delta plates reset to +1.")

        loss_val = float(loss.item())
        loss_history.append(loss_val)

        # ── Logging ──────────────────────────────────────────────────
        if step % args.log_every == 0:
            elapsed = time.time() - t0
            steps_done = step - start_step + 1
            steps_per_sec = steps_done / max(elapsed, 1e-6)
            tokens_per_sec = steps_per_sec * args.batch_size * args.seq_len

            # Smooth loss (last log_every steps)
            smooth_loss = float(np.mean(loss_history[-args.log_every :]))
            perplexity = math.exp(min(smooth_loss, 20.0))  # cap to avoid overflow

            try:
                lr_val = float(optimizer.learning_rate.item())
            except AttributeError:
                lr_val = args.lr

            metrics = {
                "loss": smooth_loss,
                "ppl": perplexity,
                "lr": lr_val,
                "grad_norm": float(grad_norm.item()),
                "tok/s": tokens_per_sec,
            }
            if td_optimizer is not None:
                metrics["td_flips"] = td_flips
                metrics["td_cands"] = td_candidates
                if thermometer is not None and step > 0:
                    temp = thermometer.temperature(step)
                    metrics["crystal_T"] = round(temp["temperature"], 6)
                    metrics["osc_frac"] = round(temp["oscillation_frac"], 4)
            log_metrics(step, metrics)

            # Per-zone grad norms every 5*log_every steps
            if step % (5 * args.log_every) == 0 and step > 0:
                zone_norms = per_zone_grad_norm(grads, model)
                zone_str = " | ".join(f"{z}={n:.3g}" for z, n in zone_norms.items())
                log(f"  zone grad norms: {zone_str}")

        # ── Eval: algedonic + α diagnostics ──────────────────────────
        if step % args.eval_every == 0 and step > 0:
            log(f"── Eval at step {step} ──")

            # Algedonic check (informational only — does not halt training)
            try:
                run_algedonic_check(model, input_ids, step)
            except Exception as e:
                log(f"  Algedonic check failed: {e}")

            # α measurement (power-law attention decay)
            if args.measure_alpha:
                try:
                    alphas = measure_alpha(model, input_ids)
                    if alphas:
                        # Log per-stride summary: mean α across heads
                        stride_alphas: dict[int, list[float]] = {}
                        for key, val in alphas.items():
                            # key format: stride_NN_head_MM_alpha
                            parts = key.split("_")
                            sidx = int(parts[1])
                            if not math.isnan(val):
                                stride_alphas.setdefault(sidx, []).append(val)

                        log("  α (attention decay) per stride:")
                        for sidx in sorted(stride_alphas):
                            vals = stride_alphas[sidx]
                            mean_a = float(np.mean(vals))
                            std_a = float(np.std(vals))
                            stride_obj = model.strides[sidx]
                            log(
                                f"    stride {sidx:02d} ({stride_obj.zone.name:8s}): "
                                f"α={mean_a:.3f} ± {std_a:.3f}  "
                                f"(n_heads={len(vals)})"
                            )

                        # Log learned α (HPE decay bias) per stride
                        learned_alphas = {}
                        for stride in model.strides:
                            if isinstance(stride.attn, FullAttention):
                                si = stride.spec.index
                                la = float(mx.exp(stride.attn.log_alpha))
                                learned_alphas[f"stride_{si:02d}_learned_alpha"] = la
                        if learned_alphas:
                            log("  learned α (HPE decay bias) per stride:")
                            for si in sorted(stride_alphas):
                                key = f"stride_{si:02d}_learned_alpha"
                                if key in learned_alphas:
                                    stride_obj = model.strides[si]
                                    log(
                                        f"    stride {si:02d} ({stride_obj.zone.name:8s}): "
                                        f"learned_α={learned_alphas[key]:.4f}"
                                    )
                            alphas.update(learned_alphas)

                        # Save alphas to output dir
                        alpha_path = output_dir / f"alpha_step_{step:07d}.json"
                        with open(alpha_path, "w") as f:
                            json.dump({"step": step, "alphas": alphas}, f, indent=2)
                except Exception as e:
                    log(f"  α measurement failed: {e}")

            # Combinator phase profiler
            if crystal_basis is not None:
                try:
                    run_combinator_profile(
                        model, tokenizer, crystal_basis, step, output_dir,
                    )
                except Exception as e:
                    log(f"  Combinator profiler failed: {e}")

            # ── TD diagnostics (at eval steps) ──
            if td_optimizer is not None:
                log(f"  TD state: step={td_optimizer.step_count}, "
                    f"last_flips={td_optimizer.last_n_flips}, "
                    f"last_candidates={td_optimizer.last_n_candidates}")

                if thermometer is not None:
                    temp = thermometer.temperature(step)
                    log(f"  Crystal thermometer:")
                    log(f"    temperature    = {temp['temperature']:.6f}  "
                        f"(fraction of positions active recently)")
                    log(f"    oscillation    = {temp['oscillation_frac']:.4f}  "
                        f"(of active, fraction flip-flopping)")
                    log(f"    settled        = {temp['settled_frac']:.4f}  "
                        f"(of ever-flipped, fraction now quiet)")
                    log(f"    frozen         = {temp['frozen_frac']:.4f}  "
                        f"(never flipped)")
                    log(f"    total flips    = {temp['total_flips']:,}")

                    # Hottest modules
                    hot = thermometer.hottest_modules(step, top_n=5)
                    if hot and hot[0][1] > 0:
                        log(f"    hottest modules:")
                        for name, t in hot:
                            if t > 0:
                                log(f"      {name}: T={t:.6f}")

        # ── Checkpoint ───────────────────────────────────────────────
        if step % args.save_every == 0 and step > 0:
            metrics_snap = {
                "loss": float(np.mean(loss_history[-args.save_every :])),
                "step": step,
            }
            try:
                lr_val = float(optimizer.learning_rate.item())
                metrics_snap["lr"] = lr_val
            except AttributeError:
                pass
            if td_optimizer is not None:
                metrics_snap["td_flips"] = td_optimizer.last_n_flips
                metrics_snap["td_step_count"] = td_optimizer.step_count
            save_checkpoint(model, optimizer, step, output_dir, metrics_snap)
            # Save delta plate state if enabled
            if td_optimizer is not None:
                _save_delta_state(model, td_optimizer, output_dir / f"step_{step:07d}")

    # ── Final checkpoint ─────────────────────────────────────────────
    final_loss = float(np.mean(loss_history[-100:])) if loss_history else float("nan")
    log(f"Training complete at step {step}. Final loss: {final_loss:.4f}")
    save_checkpoint(
        model, optimizer, step, output_dir,
        {"loss": final_loss, "step": step, "final": True},
    )


# ══════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="v15 Phase 2 — Attention + gamma training against frozen plates",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # ── Paths ────────────────────────────────────────────────────────
    p.add_argument(
        "--checkpoint",
        default="checkpoints/v15-extracted",
        help="Path to the extracted Phase 1 statechart checkpoint",
    )
    p.add_argument(
        "--data-path",
        default="data/compile-train.jsonl",
        help=(
            "Path to training data: directory of pre-tokenized shard_*.npy files "
            "(preferred), JSONL with 'text'/'input'+'output' fields, "
            "or a directory of .txt files"
        ),
    )
    p.add_argument(
        "--output-dir",
        default="checkpoints/v15-train",
        help="Directory to write training checkpoints",
    )
    p.add_argument(
        "--structured-path",
        default=None,
        help=(
            "Path to structured data shard (.npy) for mixed training. "
            "Used when --data-path is a shard directory. "
            "10%% structured / 90%% prose by default (see --structured-ratio)."
        ),
    )
    p.add_argument(
        "--structured-ratio",
        type=float,
        default=0.10,
        help="Probability of drawing a structured batch (default: 0.10 = 10%%)",
    )
    p.add_argument(
        "--n-train-shards",
        type=int,
        default=54,
        help="Number of Dolma shards to use for training (rest reserved for eval)",
    )
    p.add_argument(
        "--teacher-logits-dir",
        default=None,
        help=(
            "Optional directory of precomputed teacher logits (.npz files) for "
            "KL distillation. If absent, uses CE loss only."
        ),
    )

    # ── Training hyperparameters ─────────────────────────────────────
    p.add_argument("--batch-size", type=int, default=4, help="Batch size")
    p.add_argument(
        "--seq-len",
        type=int,
        default=512,
        help="Sequence length (tokens per example)",
    )
    p.add_argument("--lr", type=float, default=1e-4, help="Peak learning rate")
    p.add_argument(
        "--weight-decay", type=float, default=0.01, help="AdamW weight decay"
    )
    p.add_argument(
        "--grad-clip", type=float, default=1.0, help="Gradient clipping max norm"
    )
    p.add_argument(
        "--max-steps", type=int, default=10_000, help="Total training steps"
    )

    # ── KL distillation ──────────────────────────────────────────────
    p.add_argument(
        "--kl-weight",
        type=float,
        default=0.5,
        help=(
            "Weight for KL distillation loss when teacher logits are present "
            "(0.0 = pure CE, 1.0 = pure KL)"
        ),
    )
    p.add_argument(
        "--kl-temperature",
        type=float,
        default=2.0,
        help="Softening temperature for KL distillation",
    )

    # ── Trace-guided etching ────────────────────────────────────────
    p.add_argument(
        "--trace-weight",
        type=float,
        default=0.0,
        help=(
            "Weight for crystal trace loss (0.0 = disabled, 0.1 = recommended start). "
            "Encourages student residuals to project onto crystal combinator basis. "
            "Requires crystal_basis_d_model.npz in checkpoint dir."
        ),
    )
    p.add_argument(
        "--etch-max-flips",
        type=int,
        default=50,
        help="(Legacy, unused.) See --delta-plates and --td-* flags instead.",
    )
    p.add_argument(
        "--delta-plates",
        action="store_true",
        help=(
            "Enable delta plates for TernaryDescent topology correction. "
            "Adds delta1/delta2 arrays to each TernaryPlate, trained by TD. "
            "Requires --trace-weight > 0 for gradient signal."
        ),
    )
    p.add_argument(
        "--td-flip-rate",
        type=float,
        default=0.001,
        help="TD flip rate: max fraction of ternary weights flipped per commit step.",
    )
    p.add_argument(
        "--td-warmup",
        type=int,
        default=100,
        help="TD warmup steps before first flip (accumulate gradient evidence).",
    )
    p.add_argument(
        "--td-flip-interval",
        type=int,
        default=20,
        help="Steps between TD flip commits (accumulate moments between flips).",
    )
    p.add_argument(
        "--td-min-confidence",
        type=float,
        default=0.3,
        help="TD minimum SNR to consider a flip candidate.",
    )
    p.add_argument(
        "--fold-every",
        type=int,
        default=0,
        help=(
            "Auto-fold delta plates every N steps (0 = never). "
            "Folds delta into base, resets delta to +1, resets TD moments."
        ),
    )

    # ── Logging & checkpointing ──────────────────────────────────────
    p.add_argument("--log-every", type=int, default=10, help="Log metrics every N steps")
    p.add_argument(
        "--eval-every",
        type=int,
        default=100,
        help="Run algedonic + α diagnostics every N steps",
    )
    p.add_argument(
        "--save-every", type=int, default=1000, help="Save checkpoint every N steps"
    )
    p.add_argument(
        "--no-resume",
        action="store_true",
        help="Do not resume from existing checkpoint — start fresh",
    )

    # ── Diagnostics ──────────────────────────────────────────────────
    p.add_argument(
        "--measure-alpha",
        action="store_true",
        default=True,
        help="Measure attention decay power law (α) at each eval step",
    )
    p.add_argument(
        "--no-measure-alpha",
        dest="measure_alpha",
        action="store_false",
        help="Disable α measurement",
    )

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    log("v15 Phase 2 Training — Crystal-Native Tensor Statechart")
    log(f"MLX version: {mx.__version__ if hasattr(mx, '__version__') else 'unknown'}")
    log(f"Args: {vars(args)}")

    train(args)


if __name__ == "__main__":
    main()
