"""
Train the basin projector — ascending arm that maps tokens to basin vectors.

Target: per-word basin vectors matching Qwen3-32B L28 activations (d_basin=64).
Loss: cosine similarity between predicted and PCA-projected L2-normed targets.

Training regime:
  - Adam on continuous params (gamma, norms)
  - Evolutionary mutation + tournament on ternary topology
  - Gradient-informed importance sampling (reuses v8 BIOS infra)

Data: oracle shards in results/oracle-data/ (160 shards, 442K words).
Each shard: {word_vectors(N,5120), sentence_texts, word_texts, sentence_offsets, strata, groups}

Usage:
    cd ~/src/verbum
    uv run python scripts/v9/train_basin.py
    uv run python scripts/v9/train_basin.py --resume checkpoints/basin/step_001000

License: MIT
"""

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

os.environ["PYTHONUNBUFFERED"] = "1"

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np
from mlx.utils import tree_flatten, tree_map

# ── project imports ──────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "v8"))

from basin_model import BasinProjector, BasinConfig, detect_word_spans
from ternary import (
    TernaryLinear,
    zero_ternary_grads,
    restore_ternary,
    count_ternary_weights,
    save_topology,
    load_topology,
    mutate_topology,
    bios_mutation_budget,
    _walk_ternary_modules,
)

# ═════════════════════════════════════════════════════════════════
# Configuration
# ═════════════════════════════════════════════════════════════════

SHARD_DIR = Path(__file__).parent.parent.parent / "results" / "oracle-data"
CHECKPOINT_DIR = Path(__file__).parent.parent.parent / "checkpoints" / "basin"
N_SHARDS = 160
EVAL_SHARDS = 8  # last 8 shards (4%) held out for eval

MUTANT_STRATEGIES = {
    "conservative": 0.25,
    "standard": 1.0,
    "aggressive": 2.0,
    "explorer": 4.0,
}


# ═════════════════════════════════════════════════════════════════
# PCA projector — transforms 5120-dim L28 → 64-dim basin targets
# ═════════════════════════════════════════════════════════════════

class PCAProjector:
    """Projects L2-normed 5120-dim vectors to d_basin via PCA."""

    def __init__(self, path: Path | str):
        d = np.load(path)
        self.components = d["components"]  # (d_basin, 5120) float32
        self.mean = d["mean"]              # (5120,) float32
        self.d_basin = int(d["d_basin"])

    def project(self, vecs: np.ndarray) -> np.ndarray:
        """Project raw word vectors to basin space.

        Args:
            vecs: (N, 5120) float16/32 — raw L28 activations
        Returns:
            (N, d_basin) float32 — L2-normed basin vectors
        """
        # L2-normalize (basin geometry is in direction, not magnitude)
        vecs = vecs.astype(np.float32)
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-8)
        normed = vecs / norms

        # Center + project
        centered = normed - self.mean
        projected = centered @ self.components.T  # (N, d_basin)

        # L2-normalize the basin vectors too
        p_norms = np.linalg.norm(projected, axis=1, keepdims=True)
        p_norms = np.maximum(p_norms, 1e-8)
        return projected / p_norms


# ═════════════════════════════════════════════════════════════════
# Oracle data loader — shard-based, sentence-level batching
# ═════════════════════════════════════════════════════════════════

class OracleDataLoader:
    """Loads oracle shards and yields (token_ids, word_spans, target_basins) batches.

    Each shard has 500 sentences with per-word 5120-dim L28 activations.
    This loader:
      1. Tokenizes sentences on-the-fly with Qwen3 tokenizer
      2. Detects BPE word boundaries
      3. Projects target vectors through PCA to d_basin=64
      4. Batches sentences (padding tokens and words to max in batch)
    """

    def __init__(
        self,
        shard_dir: Path,
        pca: PCAProjector,
        tokenizer,
        shard_indices: list[int],
        batch_size: int = 32,
        max_seq_len: int = 128,
        seed: int = 42,
    ):
        self.shard_dir = shard_dir
        self.pca = pca
        self.tokenizer = tokenizer
        self.shard_indices = list(shard_indices)
        self.batch_size = batch_size
        self.max_seq_len = max_seq_len
        self.rng = np.random.RandomState(seed)

        # Build index: [(shard_idx, sentence_idx), ...]
        self._build_index()
        self._pos = 0
        self._epoch = 0

        # Cache for current shard data
        self._cached_shard_idx = -1
        self._cached_shard = None

    def _build_index(self):
        """Build shuffled index of all sentences across all shards."""
        self._index = []
        for si in self.shard_indices:
            # 500 sentences per shard
            for sent_idx in range(500):
                self._index.append((si, sent_idx))
        self.rng.shuffle(self._index)

        # Pre-tokenization cache: (shard_idx, sent_idx) → (token_ids, word_spans)
        self._token_cache: dict[tuple[int, int], tuple[list[int], list[list[int]]]] = {}

    def _load_shard(self, shard_idx: int):
        """Load and cache a shard."""
        if shard_idx == self._cached_shard_idx:
            return self._cached_shard
        path = self.shard_dir / f"shard_{shard_idx:04d}.npz"
        d = np.load(path, allow_pickle=True)
        self._cached_shard_idx = shard_idx
        self._cached_shard = d
        return d

    def _get_sentence(self, shard_idx: int, sent_idx: int):
        """Get one sentence's data: text, word target vectors, stratum."""
        d = self._load_shard(shard_idx)
        offsets = d["sentence_offsets"]
        n_words_total = len(d["word_texts"])

        start = int(offsets[sent_idx])
        end = int(offsets[sent_idx + 1]) if sent_idx + 1 < len(offsets) else n_words_total

        text = str(d["sentence_texts"][sent_idx])
        word_vecs = d["word_vectors"][start:end]  # (n_words, 5120)
        stratum = str(d["strata"][sent_idx])

        return text, word_vecs, stratum

    def next_batch(self):
        """Get next batch of training data.

        Returns:
            token_ids:      mx.array (B, max_T) int32
            word_spans:     list[list[list[int]]] — per-batch word spans
            target_basins:  mx.array (B, max_words, d_basin) float32
            word_mask:      mx.array (B, max_words) float32
            strata:         list[str] — stratum labels per example
        """
        if self._pos + self.batch_size > len(self._index):
            self._epoch += 1
            self._pos = 0
            self.rng.shuffle(self._index)

        batch_entries = self._index[self._pos:self._pos + self.batch_size]
        self._pos += self.batch_size

        # Collect raw data
        batch_texts = []
        batch_word_vecs = []
        batch_strata = []

        for shard_idx, sent_idx in batch_entries:
            text, word_vecs, stratum = self._get_sentence(shard_idx, sent_idx)
            batch_texts.append(text)
            batch_word_vecs.append(word_vecs)
            batch_strata.append(stratum)

        # Tokenize all sentences (cached)
        batch_token_ids = []
        batch_word_spans = []

        for (shard_idx, sent_idx), text in zip(batch_entries, batch_texts):
            cache_key = (shard_idx, sent_idx)
            if cache_key in self._token_cache:
                ids, spans = self._token_cache[cache_key]
            else:
                enc = self.tokenizer(text, add_special_tokens=False)
                ids = enc["input_ids"][:self.max_seq_len]
                spans = detect_word_spans(self.tokenizer, ids)
                self._token_cache[cache_key] = (ids, spans)
            batch_token_ids.append(ids)
            batch_word_spans.append(spans)

        # Pad token IDs to max length in batch
        max_T = max(len(ids) for ids in batch_token_ids)
        padded_ids = np.zeros((len(batch_token_ids), max_T), dtype=np.int32)
        for i, ids in enumerate(batch_token_ids):
            padded_ids[i, :len(ids)] = ids

        # Project target vectors through PCA and pad
        max_words = max(len(spans) for spans in batch_word_spans)
        d_basin = self.pca.d_basin
        target_basins = np.zeros((len(batch_texts), max_words, d_basin), dtype=np.float32)
        word_mask = np.zeros((len(batch_texts), max_words), dtype=np.float32)

        for i, (word_vecs, spans) in enumerate(zip(batch_word_vecs, batch_word_spans)):
            # Align: oracle word count may differ from tokenizer word count
            # Use min of both to avoid index errors
            n_words = min(len(spans), len(word_vecs))
            if n_words > 0:
                basin_targets = self.pca.project(word_vecs[:n_words])
                target_basins[i, :n_words] = basin_targets
                word_mask[i, :n_words] = 1.0

        return (
            mx.array(padded_ids),
            batch_word_spans,
            mx.array(target_basins),
            mx.array(word_mask),
            batch_strata,
        )

    @property
    def epoch(self):
        return self._epoch

    @property
    def total_sentences(self):
        return len(self._index)

    def reset(self):
        self._pos = 0
        self.rng.shuffle(self._index)


# ═════════════════════════════════════════════════════════════════
# Loss function
# ═════════════════════════════════════════════════════════════════

def cosine_loss(pred: mx.array, target: mx.array, mask: mx.array) -> mx.array:
    """Cosine similarity loss between predicted and target basin vectors.

    Args:
        pred:   (B, W, D) float32 — model output (already L2-normed)
        target: (B, W, D) float32 — PCA-projected L28 targets (L2-normed)
        mask:   (B, W)    float32 — 1.0 for real words, 0.0 for padding
    Returns:
        scalar loss in [0, 2]: 1 - mean(cosine_similarity)
    """
    # Dot product per word (already L2-normed, so dot = cosine sim)
    sim = mx.sum(pred * target, axis=-1)  # (B, W)

    # Mask out padding
    masked_sim = sim * mask
    n_words = mx.sum(mask) + 1e-8

    return 1.0 - mx.sum(masked_sim) / n_words


# ═════════════════════════════════════════════════════════════════
# Learning rate schedule
# ═════════════════════════════════════════════════════════════════

def cosine_lr(step: int, warmup: int, total: int, lr_max: float,
              lr_min: float = 1e-6) -> float:
    """Cosine annealing with linear warmup."""
    if step <= warmup:
        return lr_max * step / max(1, warmup)
    progress = (step - warmup) / max(1, total - warmup)
    return lr_min + 0.5 * (lr_max - lr_min) * (1.0 + math.cos(math.pi * progress))


# ═════════════════════════════════════════════════════════════════
# Evaluation
# ═════════════════════════════════════════════════════════════════

def evaluate(model, eval_loader, n_batches: int = 8) -> dict:
    """Run evaluation, return per-stratum cosine similarity."""
    total_sim = 0.0
    total_words = 0
    stratum_sims = {}
    stratum_counts = {}

    for _ in range(n_batches):
        token_ids, word_spans, target_basins, word_mask, strata = eval_loader.next_batch()
        pred_basins, pred_mask = model(token_ids, word_spans)

        # Compute per-example cosine sim
        B = token_ids.shape[0]
        pred_np = np.array(pred_basins)
        target_np = np.array(target_basins)
        mask_np = np.array(word_mask)

        for b in range(B):
            n_words = int(mask_np[b].sum())
            if n_words == 0:
                continue
            p = pred_np[b, :n_words]
            t = target_np[b, :n_words]
            sim = np.sum(p * t, axis=-1).mean()

            total_sim += sim * n_words
            total_words += n_words

            s = strata[b]
            stratum_sims[s] = stratum_sims.get(s, 0.0) + sim * n_words
            stratum_counts[s] = stratum_counts.get(s, 0) + n_words

    metrics = {
        "cosine_sim": total_sim / max(1, total_words),
        "n_words": total_words,
    }
    for s in sorted(stratum_sims.keys()):
        metrics[f"sim_{s}"] = stratum_sims[s] / max(1, stratum_counts[s])

    return metrics


# ═════════════════════════════════════════════════════════════════
# Checkpoint save / load
# ═════════════════════════════════════════════════════════════════

def save_checkpoint(
    step: int, model, optimizer, state: dict,
    row_importance: dict, col_importance: dict, grad_direction: dict,
    checkpoint_dir: Path,
):
    """Save full checkpoint."""
    step_dir = checkpoint_dir / f"step_{step:06d}"
    step_dir.mkdir(parents=True, exist_ok=True)

    # Model weights
    flat = tree_flatten(model.parameters())
    mx.savez(str(step_dir / "model.npz"), **{k: v for k, v in flat})

    # Optimizer state
    opt_flat = tree_flatten(optimizer.state)
    mx.savez(str(step_dir / "optimizer.npz"), **{k: v for k, v in opt_flat})

    # Importance maps
    imp = {}
    for path, arr in row_importance.items():
        imp[f"row.{path}"] = arr
    for path, arr in col_importance.items():
        imp[f"col.{path}"] = arr
    for path, arr in grad_direction.items():
        imp[f"dir.{path}"] = arr
    if imp:
        np.savez_compressed(str(step_dir / "importance.npz"), **imp)

    # State JSON
    with open(step_dir / "state.json", "w") as f:
        json.dump(state, f, indent=2)

    print(f"  💾 Checkpoint saved: {step_dir}")


def load_checkpoint(
    checkpoint_dir: Path, model, optimizer,
) -> tuple[dict, dict, dict, dict]:
    """Load checkpoint, return (state, row_imp, col_imp, grad_dir)."""
    # Model
    weights = dict(mx.load(str(checkpoint_dir / "model.npz")))
    model.load_weights(list(weights.items()))

    # Optimizer (must have been dummy-inited first)
    opt_path = checkpoint_dir / "optimizer.npz"
    if opt_path.exists():
        from mlx.utils import tree_unflatten
        opt_state = dict(mx.load(str(opt_path)))
        optimizer.state = tree_unflatten(list(opt_state.items()))
        mx.eval(optimizer.state)

    # State
    with open(checkpoint_dir / "state.json") as f:
        state = json.load(f)

    # Importance maps
    row_imp, col_imp, grad_dir = {}, {}, {}
    imp_path = checkpoint_dir / "importance.npz"
    if imp_path.exists():
        imp = dict(np.load(str(imp_path)))
        for k, v in imp.items():
            if k.startswith("row."):
                row_imp[k[4:]] = v
            elif k.startswith("col."):
                col_imp[k[4:]] = v
            elif k.startswith("dir."):
                grad_dir[k[4:]] = v

    return state, row_imp, col_imp, grad_dir


# ═════════════════════════════════════════════════════════════════
# Gradient navigation helper
# ═════════════════════════════════════════════════════════════════

def navigate_grad(grads: dict, path: str, param: str):
    """Navigate a nested grad dict by dot-separated path + param name."""
    node = grads
    for part in path.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        elif isinstance(node, list):
            try:
                node = node[int(part)]
            except (ValueError, IndexError):
                return None
        else:
            return None
    if isinstance(node, dict) and param in node:
        return node[param]
    return None


# ═════════════════════════════════════════════════════════════════
# Adaptive mutation rate
# ═════════════════════════════════════════════════════════════════

_strategy_history: list[str | None] = []


def adapt_base_pct(base_pct: float, window: int = 20) -> float:
    """Adapt mutation rate based on which strategies win."""
    recent = _strategy_history[-window:]
    if len(recent) < 5:
        return base_pct

    wins = [s for s in recent if s is not None]
    if not wins:
        return base_pct

    explorer_rate = sum(1 for s in wins if s == "explorer") / len(wins)
    conservative_rate = sum(1 for s in wins if s == "conservative") / len(wins)

    min_pct, max_pct = 0.001, 0.02
    if explorer_rate > 0.5:
        return min(max_pct, base_pct * 1.5)
    if conservative_rate > 0.5:
        return max(min_pct, base_pct * 0.67)
    return base_pct


# ═════════════════════════════════════════════════════════════════
# Main training loop
# ═════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Train basin projector")
    parser.add_argument("--resume", type=str, default=None,
                        help="Resume from checkpoint dir")
    parser.add_argument("--total-steps", type=int, default=20000)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--warmup", type=int, default=500)
    parser.add_argument("--gen-interval", type=int, default=25,
                        help="Steps between evolutionary tournaments")
    parser.add_argument("--eval-interval", type=int, default=100)
    parser.add_argument("--checkpoint-interval", type=int, default=1000)
    parser.add_argument("--grad-accum", type=int, default=1)
    parser.add_argument("--base-pct", type=float, default=0.005,
                        help="Base mutation rate for ternary topology")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    print("=" * 60)
    print("  Basin Projector Training")
    print("=" * 60)

    # ── Tokenizer ────────────────────────────────────────────
    print("\nLoading tokenizer...")
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-32B")
    print(f"  Vocab size: {tokenizer.vocab_size}")

    # ── PCA projector ────────────────────────────────────────
    pca_path = SHARD_DIR / "pca_projector.npz"
    print(f"Loading PCA projector: {pca_path}")
    pca = PCAProjector(pca_path)
    print(f"  d_basin={pca.d_basin}, components: {pca.components.shape}")

    # ── Data loaders ─────────────────────────────────────────
    train_shards = list(range(N_SHARDS - EVAL_SHARDS))
    eval_shards = list(range(N_SHARDS - EVAL_SHARDS, N_SHARDS))
    print(f"\nData: {len(train_shards)} train shards, {len(eval_shards)} eval shards")
    print(f"  ~{len(train_shards) * 500} train sentences, ~{len(eval_shards) * 500} eval sentences")

    train_loader = OracleDataLoader(
        SHARD_DIR, pca, tokenizer, train_shards,
        batch_size=args.batch_size, seed=args.seed,
    )
    eval_loader = OracleDataLoader(
        SHARD_DIR, pca, tokenizer, eval_shards,
        batch_size=args.batch_size, seed=args.seed + 1,
    )

    # ── Model ────────────────────────────────────────────────
    config = BasinConfig(
        d_model=256,
        d_basin=64,
        n_heads=8,
        max_seq_len=128,  # oracle sentences are short (median 6 words)
    )
    model = BasinProjector(config)
    params = model.count_params()
    print(f"\nModel: d_model={config.d_model}, d_basin={config.d_basin}, "
          f"n_heads={config.n_heads}, n_levels={config.n_levels}")
    print(f"  Total logical params: {params['total_logical']:,}")
    print(f"  Ternary logical: {params['ternary_logical']:,}")
    print(f"  Continuous: {params['continuous']:,}")
    print(f"  Packed size: {params['packed_bytes'] / 1e6:.1f} MB")

    total_ternary = count_ternary_weights(model)
    print(f"  Ternary weights (evolution): {total_ternary:,}")

    # ── Optimizer (Adam on continuous params only) ────────────
    optimizer = optim.AdamW(learning_rate=args.lr, weight_decay=0.01)

    # ── Resume or fresh start ────────────────────────────────
    start_step = 0
    base_pct = args.base_pct
    row_importance: dict[str, np.ndarray] = {}
    col_importance: dict[str, np.ndarray] = {}
    grad_direction: dict[str, np.ndarray] = {}

    if args.resume:
        print(f"\nResuming from {args.resume}")
        # Dummy forward+backward to init optimizer state structure
        dummy_ids, dummy_spans, dummy_targets, dummy_mask, _ = train_loader.next_batch()
        def _loss_fn(m, ids, spans, targets, mask):
            pred, pred_mask = m(ids, spans)
            return cosine_loss(pred, targets, mask)
        _lfg = nn.value_and_grad(model, _loss_fn)
        _lv, _g = _lfg(model, dummy_ids, dummy_spans, dummy_targets, dummy_mask)
        mx.eval(_lv, _g)
        _g = zero_ternary_grads(model, _g)
        optimizer.update(model, _g)
        mx.eval(model.parameters(), optimizer.state)
        restore_ternary(model)
        train_loader.reset()

        state, row_importance, col_importance, grad_direction = \
            load_checkpoint(Path(args.resume), model, optimizer)
        start_step = state.get("step", 0)
        base_pct = state.get("base_pct", args.base_pct)
        print(f"  Resumed at step {start_step}, base_pct={base_pct:.4f}")

    # ── Training state ───────────────────────────────────────
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.RandomState(args.seed)
    importance_alpha = 0.1
    train_losses = []
    total_accepted = 0
    total_gens = 0

    print(f"\n{'=' * 60}")
    print(f"  Training: {args.total_steps} steps, batch={args.batch_size}, "
          f"lr={args.lr}, gen_interval={args.gen_interval}")
    print(f"  Mutation: base_pct={base_pct:.4f}, {total_ternary:,} ternary weights")
    print(f"{'=' * 60}\n")

    # ── Loss function for value_and_grad ─────────────────────
    def loss_fn(model, token_ids, word_spans, target_basins, word_mask):
        pred_basins, pred_mask = model(token_ids, word_spans)
        return cosine_loss(pred_basins, target_basins, word_mask)

    loss_and_grad = nn.value_and_grad(model, loss_fn)
    t_start = time.time()

    for step in range(start_step + 1, args.total_steps + 1):
        t_step = time.time()

        # Learning rate schedule
        lr = cosine_lr(step, args.warmup, args.total_steps, args.lr)
        optimizer.learning_rate = lr

        # ── Forward + backward (with optional grad accumulation) ──
        accum_loss = 0.0
        accum_grads = None

        for _micro in range(args.grad_accum):
            token_ids, word_spans, target_basins, word_mask, strata = \
                train_loader.next_batch()

            loss_val, grads = loss_and_grad(
                model, token_ids, word_spans, target_basins, word_mask
            )
            mx.eval(loss_val, grads)
            accum_loss += loss_val.item()

            if accum_grads is None:
                accum_grads = grads
            else:
                accum_grads = tree_map(lambda a, b: a + b, accum_grads, grads)

        if args.grad_accum > 1:
            accum_grads = tree_map(lambda g: g / args.grad_accum, accum_grads)
        avg_loss = accum_loss / args.grad_accum

        # ── Extract importance maps BEFORE zeroing ternary grads ──
        for path, mod in _walk_ternary_modules(model):
            if not isinstance(mod, TernaryLinear):
                continue
            gamma_grad = navigate_grad(accum_grads, path, "gamma")
            if gamma_grad is not None:
                gg = np.array(mx.abs(gamma_grad))
                if path in row_importance:
                    row_importance[path] = importance_alpha * gg + \
                        (1 - importance_alpha) * row_importance[path]
                else:
                    row_importance[path] = gg

                gd = np.array(gamma_grad)
                if path in grad_direction:
                    grad_direction[path] = importance_alpha * gd + \
                        (1 - importance_alpha) * grad_direction[path]
                else:
                    grad_direction[path] = gd

            if hasattr(mod, "_x_abs_mean") and mod._x_abs_mean is not None:
                xm = np.array(mod._x_abs_mean)
                # Skip scalar _x_abs_mean (happens when input is 2D, not 3D)
                if xm.ndim == 0:
                    continue
                if path in col_importance:
                    col_importance[path] = importance_alpha * xm + \
                        (1 - importance_alpha) * col_importance[path]
                else:
                    col_importance[path] = xm

        # ── Zero ternary grads, clip, update ──
        accum_grads = zero_ternary_grads(model, accum_grads)

        # Grad clipping
        grad_norm = mx.sqrt(sum(
            mx.sum(g * g) for _, g in tree_flatten(accum_grads) if g.dtype == mx.float32
        ))
        mx.eval(grad_norm)
        max_norm = 1.0
        if grad_norm.item() > max_norm:
            scale = max_norm / (grad_norm.item() + 1e-8)
            accum_grads = tree_map(
                lambda g: g * scale if g.dtype == mx.float32 else g,
                accum_grads,
            )

        optimizer.update(model, accum_grads)
        mx.eval(model.parameters(), optimizer.state)
        restore_ternary(model)

        train_losses.append(avg_loss)

        # ── Evolutionary tournament ──────────────────────────
        if step % args.gen_interval == 0:
            total_gens += 1
            budget = bios_mutation_budget(
                step, args.total_steps, total_ternary, base_pct
            )

            # Evaluate champion (2 batches for tournament — fast noisy signal)
            champion_snap = save_topology(model)
            champion_eval = evaluate(model, eval_loader, n_batches=2)
            champion_sim = champion_eval["cosine_sim"]

            # Try all mutant strategies
            best_sim = champion_sim
            best_snap = None
            best_strategy = None

            for strategy, scale in MUTANT_STRATEGIES.items():
                load_topology(model, champion_snap)
                n_mut = max(1, int(budget * scale))
                mutate_topology(
                    model, n_mut, rng,
                    row_importance=row_importance if row_importance else None,
                    col_importance=col_importance if col_importance else None,
                    grad_direction=grad_direction if grad_direction else None,
                )
                mutant_eval = evaluate(model, eval_loader, n_batches=2)
                mutant_sim = mutant_eval["cosine_sim"]

                # Higher cosine sim = better (invert for "lower is better")
                if mutant_sim > best_sim:
                    best_sim = mutant_sim
                    best_snap = save_topology(model)
                    best_strategy = strategy

            # Accept or reject
            if best_snap is not None:
                load_topology(model, best_snap)
                total_accepted += 1
                _strategy_history.append(best_strategy)
            else:
                load_topology(model, champion_snap)
                _strategy_history.append(None)

            # Adapt mutation rate
            base_pct = adapt_base_pct(base_pct)

        # ── Logging ──────────────────────────────────────────
        if step % 10 == 0:
            elapsed = time.time() - t_start
            recent_loss = np.mean(train_losses[-50:]) if train_losses else avg_loss
            step_time = time.time() - t_step
            epoch = train_loader.epoch

            print(f"  step {step:5d} | loss {avg_loss:.4f} (avg50: {recent_loss:.4f}) | "
                  f"lr {lr:.2e} | epoch {epoch} | "
                  f"{step_time:.2f}s/step | {elapsed:.0f}s total")

        # ── Evaluation ───────────────────────────────────────
        if step % args.eval_interval == 0:
            eval_metrics = evaluate(model, eval_loader, n_batches=8)
            sim = eval_metrics["cosine_sim"]
            print(f"\n  📊 Eval @ step {step}: cosine_sim={sim:.4f}")
            for k, v in sorted(eval_metrics.items()):
                if k.startswith("sim_"):
                    print(f"     {k}: {v:.4f}")
            accept_rate = total_accepted / max(1, total_gens)
            print(f"     evo: {total_gens} gens, {total_accepted} accepted "
                  f"({accept_rate:.1%}), base_pct={base_pct:.4f}")
            print()

        # ── Checkpoint ───────────────────────────────────────
        if step % args.checkpoint_interval == 0:
            state = {
                "step": step,
                "epoch": train_loader.epoch,
                "base_pct": base_pct,
                "total_gens": total_gens,
                "total_accepted": total_accepted,
                "train_loss_recent": float(np.mean(train_losses[-100:])),
                "train_losses_last100": [float(x) for x in train_losses[-100:]],
            }
            save_checkpoint(
                step, model, optimizer, state,
                row_importance, col_importance, grad_direction,
                CHECKPOINT_DIR,
            )

    # ── Final checkpoint ─────────────────────────────────────
    final_metrics = evaluate(model, eval_loader, n_batches=16)
    print(f"\n{'=' * 60}")
    print(f"  Training complete: {args.total_steps} steps")
    print(f"  Final cosine_sim: {final_metrics['cosine_sim']:.4f}")
    for k, v in sorted(final_metrics.items()):
        if k.startswith("sim_"):
            print(f"    {k}: {v:.4f}")
    print(f"  Evo: {total_gens} gens, {total_accepted} accepted")
    print(f"{'=' * 60}")

    state = {
        "step": args.total_steps,
        "epoch": train_loader.epoch,
        "base_pct": base_pct,
        "total_gens": total_gens,
        "total_accepted": total_accepted,
        "train_loss_recent": float(np.mean(train_losses[-100:])),
        "final_metrics": {k: float(v) for k, v in final_metrics.items()},
    }
    save_checkpoint(
        args.total_steps, model, optimizer, state,
        row_importance, col_importance, grad_direction,
        CHECKPOINT_DIR,
    )


if __name__ == "__main__":
    main()
