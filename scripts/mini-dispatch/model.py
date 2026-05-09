"""
MiniDispatch — a routing lab bench.

Minimal architecture to study top-k dispatch routing in isolation.
No strides, no registers, no ternary, no evolution, no S3/S4/meta.
Pure float weights, standard Adam. One question: can a router learn
content-sensitive dispatch to different op pathways?

Architecture:
  tokens → embed + pos_embed → RMSNorm
  → [DispatchBlock × n_layers]:
      Router: Linear → top-k → softmax-over-k
      Per-op FFNs: n_ops separate (up, down) pairs
      Weighted sum of op outputs
      Residual connection
  → output_norm → tied embed → logits → cross-entropy

Baseline (no routing):
  Same architecture but one FFN per layer with matched total params.
  Proves whether routing helps vs just having more parameters.

Key design: each op has its OWN FFN, not a shared pathway modulated
by an embedding vector. If dispatch learns diversity, it's because
different ops compute genuinely different transformations.

License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass

import mlx.core as mx
import mlx.nn as nn


# ══════════════════════════════════════════════════════════════════
# Config
# ══════════════════════════════════════════════════════════════════


@dataclass
class MiniDispatchConfig:
    """Configuration for MiniDispatch experiments."""

    # Model
    vocab_size: int = 151936      # Qwen3 BBPE
    d_model: int = 128            # small — fast iteration
    n_ops: int = 4                # few ops — easy to see diversity
    d_ff: int = 384               # 3× d_model per-op FFN width
    n_layers: int = 2             # stack dispatch blocks for depth
    top_k: int = 2                # MoE routing top-k
    dropout: float = 0.0          # no dropout for clean signal

    # Training
    batch_size: int = 4
    seq_len: int = 512
    total_steps: int = 2000
    lr: float = 3e-4
    warmup_steps: int = 100
    weight_decay: float = 0.01
    grad_clip: float = 1.0

    # Data
    data_dir: str = "/Users/mwhitford/data/fractal-bitnet/shards-qwen3"
    n_train_shards: int = 54
    n_eval_shards: int = 6

    # Logging
    log_interval: int = 25
    checkpoint_interval: int = 500
    checkpoint_dir: str = "checkpoints/mini-dispatch"

    @property
    def max_seq_len(self) -> int:
        return self.seq_len


# ══════════════════════════════════════════════════════════════════
# Router — the thing we're studying
# ══════════════════════════════════════════════════════════════════


class TopKRouter(nn.Module):
    """Top-k router: projects hidden state to per-op scores.

    Returns dispatch weights: (B, L, n_ops) with only top-k nonzero
    per position. Also caches weights for probing.
    """

    def __init__(self, d_model: int, n_ops: int, top_k: int = 2):
        super().__init__()
        self.n_ops = n_ops
        self.top_k = min(top_k, n_ops)
        self.gate = nn.Linear(d_model, n_ops, bias=False)

    def __call__(self, x: mx.array) -> mx.array:
        """x: (B, L, d_model) → weights: (B, L, n_ops)"""
        logits = self.gate(x)                                   # (B, L, n_ops)

        # Top-k selection
        top_vals = mx.topk(logits, k=self.top_k, axis=-1)      # (B, L, k)
        threshold = mx.min(top_vals, axis=-1, keepdims=True)    # (B, L, 1)
        masked = mx.where(logits >= threshold, logits, mx.full(logits.shape, -1e9))
        weights = mx.softmax(masked, axis=-1)                   # (B, L, n_ops)

        # Cache for probing
        self._logits = mx.stop_gradient(logits)
        self._weights = mx.stop_gradient(weights)

        return weights


# ══════════════════════════════════════════════════════════════════
# DispatchBlock — router + per-op FFNs
# ══════════════════════════════════════════════════════════════════


class DispatchBlock(nn.Module):
    """One dispatch layer: route, compute per-op, weighted sum, residual.

    Each op is a separate (up, down) FFN pair. The router decides
    which ops to use at each position. Weighted sum of op outputs.

    This is a simplified MoE layer — no load balancing loss, no
    capacity factor, no auxiliary loss. We want to see what routing
    does naturally with only the LM loss as signal.
    """

    def __init__(self, d_model: int, d_ff: int, n_ops: int, top_k: int = 2,
                 dropout: float = 0.0):
        super().__init__()
        self.n_ops = n_ops
        self.norm = nn.RMSNorm(d_model)
        self.router = TopKRouter(d_model, n_ops, top_k)

        # Per-op FFNs — each op is genuinely different
        self.op_ups = [nn.Linear(d_model, d_ff, bias=False) for _ in range(n_ops)]
        self.op_downs = [nn.Linear(d_ff, d_model, bias=False) for _ in range(n_ops)]

        self.dropout = nn.Dropout(dropout)

    def __call__(self, x: mx.array) -> mx.array:
        """x: (B, L, d_model) → (B, L, d_model) with residual."""
        h = self.norm(x)
        weights = self.router(h)  # (B, L, n_ops)

        # Compute all ops (we could optimize with sparse dispatch,
        # but for a lab bench clarity > speed)
        op_outputs = []
        for i in range(self.n_ops):
            op_out = self.op_downs[i](nn.gelu(self.op_ups[i](h)))  # (B, L, d_model)
            op_outputs.append(op_out)

        # Stack: (n_ops, B, L, d_model) → weighted sum
        stacked = mx.stack(op_outputs, axis=0)                     # (n_ops, B, L, d_model)
        weights_4d = mx.transpose(weights, axes=(2, 0, 1))        # (n_ops, B, L)
        weights_4d = mx.expand_dims(weights_4d, axis=-1)          # (n_ops, B, L, 1)
        combined = mx.sum(stacked * weights_4d, axis=0)           # (B, L, d_model)

        return x + self.dropout(combined)


# ══════════════════════════════════════════════════════════════════
# MiniDispatchModel — the full LM
# ══════════════════════════════════════════════════════════════════


class MiniDispatchModel(nn.Module):
    """Minimal dispatch-routing language model.

    embed → [DispatchBlock × n_layers] → output_norm → tied embed → logits
    """

    def __init__(self, cfg: MiniDispatchConfig):
        super().__init__()
        self.cfg = cfg

        # Embedding (standard float, not ternary)
        self.embed = nn.Embedding(cfg.vocab_size, cfg.d_model)
        self.pos_embed = nn.Embedding(cfg.max_seq_len, cfg.d_model)
        self.embed_norm = nn.RMSNorm(cfg.d_model)

        # Dispatch blocks
        self.blocks = [
            DispatchBlock(cfg.d_model, cfg.d_ff, cfg.n_ops, cfg.top_k, cfg.dropout)
            for _ in range(cfg.n_layers)
        ]

        # Output
        self.output_norm = nn.RMSNorm(cfg.d_model)
        self.output_proj = nn.Linear(cfg.d_model, cfg.vocab_size, bias=False)

        # Tie output to input embedding
        self.output_proj.weight = self.embed.weight

    def __call__(self, tokens: mx.array, targets: mx.array | None = None):
        """tokens: (B, L) → logits: (B, L, V), optional loss."""
        B, L = tokens.shape

        # Embed
        positions = mx.arange(L)
        x = self.embed_norm(self.embed(tokens) + self.pos_embed(positions))

        # Dispatch blocks
        for block in self.blocks:
            x = block(x)

        # Output
        x = self.output_norm(x)
        logits = self.output_proj(x)

        loss = None
        if targets is not None:
            loss = nn.losses.cross_entropy(
                logits.reshape(-1, self.cfg.vocab_size),
                targets.reshape(-1),
            ).mean()

        return logits, loss

    def get_routing_stats(self) -> list[dict]:
        """Extract cached routing stats from all blocks."""
        stats = []
        for i, block in enumerate(self.blocks):
            router = block.router
            if hasattr(router, '_weights'):
                w = router._weights  # (B, L, n_ops)
                mx.eval(w)
                # Mean dispatch weight per op
                mean_weights = mx.mean(w, axis=(0, 1))  # (n_ops,)
                mx.eval(mean_weights)
                stats.append({
                    "layer": i,
                    "mean_weights": [float(mean_weights[j].item()) for j in range(w.shape[-1])],
                    "weights_tensor": w,  # keep for deeper analysis
                })
        return stats


# ══════════════════════════════════════════════════════════════════
# BaselineModel — single FFN, no routing (param-matched control)
# ══════════════════════════════════════════════════════════════════


class BaselineBlock(nn.Module):
    """Single-FFN block with matched parameter count.

    To match n_ops separate (d_model→d_ff, d_ff→d_model) pairs,
    we use one wider FFN: d_model → d_ff_wide → d_model
    where d_ff_wide = d_ff * n_ops (so total params ≈ same).

    Actually: n_ops FFNs each have 2 * d_model * d_ff params.
    One FFN with d_ff_wide = n_ops * d_ff has 2 * d_model * d_ff_wide.
    So d_ff_wide = n_ops * d_ff matches exactly.
    """

    def __init__(self, d_model: int, d_ff_wide: int, dropout: float = 0.0):
        super().__init__()
        self.norm = nn.RMSNorm(d_model)
        self.up = nn.Linear(d_model, d_ff_wide, bias=False)
        self.down = nn.Linear(d_ff_wide, d_model, bias=False)
        self.dropout = nn.Dropout(dropout)

    def __call__(self, x: mx.array) -> mx.array:
        h = self.norm(x)
        return x + self.dropout(self.down(nn.gelu(self.up(h))))


class BaselineModel(nn.Module):
    """Param-matched baseline: same total FFN capacity, no routing."""

    def __init__(self, cfg: MiniDispatchConfig):
        super().__init__()
        self.cfg = cfg

        self.embed = nn.Embedding(cfg.vocab_size, cfg.d_model)
        self.pos_embed = nn.Embedding(cfg.max_seq_len, cfg.d_model)
        self.embed_norm = nn.RMSNorm(cfg.d_model)

        # Match total FFN params: n_ops FFNs → one FFN of width n_ops * d_ff
        d_ff_wide = cfg.n_ops * cfg.d_ff
        self.blocks = [
            BaselineBlock(cfg.d_model, d_ff_wide, cfg.dropout)
            for _ in range(cfg.n_layers)
        ]

        self.output_norm = nn.RMSNorm(cfg.d_model)
        self.output_proj = nn.Linear(cfg.d_model, cfg.vocab_size, bias=False)
        self.output_proj.weight = self.embed.weight

    def __call__(self, tokens: mx.array, targets: mx.array | None = None):
        B, L = tokens.shape
        positions = mx.arange(L)
        x = self.embed_norm(self.embed(tokens) + self.pos_embed(positions))

        for block in self.blocks:
            x = block(x)

        x = self.output_norm(x)
        logits = self.output_proj(x)

        loss = None
        if targets is not None:
            loss = nn.losses.cross_entropy(
                logits.reshape(-1, self.cfg.vocab_size),
                targets.reshape(-1),
            ).mean()

        return logits, loss


# ══════════════════════════════════════════════════════════════════
# Utilities
# ══════════════════════════════════════════════════════════════════


def count_parameters(model: nn.Module) -> dict[str, int]:
    """Count total and per-component parameters."""
    from mlx.utils import tree_flatten

    all_p = tree_flatten(model.parameters())
    total = sum(p.size for _, p in all_p)

    # Group by top-level key
    groups = {}
    for name, p in all_p:
        top = name.split(".")[0]
        groups[top] = groups.get(top, 0) + p.size

    return {"total": total, "groups": groups}


def create_model(cfg: MiniDispatchConfig, model_type: str = "dispatch") -> nn.Module:
    """Factory: 'dispatch' or 'baseline'."""
    if model_type == "dispatch":
        model = MiniDispatchModel(cfg)
    elif model_type == "baseline":
        model = BaselineModel(cfg)
    else:
        raise ValueError(f"Unknown model_type: {model_type}")

    mx.eval(model.parameters())
    return model


# ══════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import numpy as np

    cfg = MiniDispatchConfig()
    print(f"Config: d_model={cfg.d_model}, n_ops={cfg.n_ops}, d_ff={cfg.d_ff}, "
          f"n_layers={cfg.n_layers}, top_k={cfg.top_k}")

    # Test dispatch model
    print("\n── MiniDispatchModel ──")
    dispatch_model = create_model(cfg, "dispatch")
    tokens = mx.array(np.random.randint(0, 1000, (2, 64)).astype(np.int32))
    targets = mx.array(np.random.randint(0, 1000, (2, 64)).astype(np.int32))

    logits, loss = dispatch_model(tokens, targets)
    mx.eval(logits, loss)
    print(f"  Logits: {logits.shape}")
    print(f"  Loss: {loss.item():.4f}")

    dp = count_parameters(dispatch_model)
    print(f"  Params: {dp['total']:,}")
    for k, v in dp["groups"].items():
        print(f"    {k}: {v:,}")

    # Check routing stats
    stats = dispatch_model.get_routing_stats()
    for s in stats:
        w = s["mean_weights"]
        print(f"  Layer {s['layer']} routing: {' '.join(f'{v:.3f}' for v in w)}")

    # Test baseline model
    print("\n── BaselineModel ──")
    baseline_model = create_model(cfg, "baseline")
    logits_b, loss_b = baseline_model(tokens, targets)
    mx.eval(logits_b, loss_b)
    print(f"  Logits: {logits_b.shape}")
    print(f"  Loss: {loss_b.item():.4f}")

    bp = count_parameters(baseline_model)
    print(f"  Params: {bp['total']:,}")
    for k, v in bp["groups"].items():
        print(f"    {k}: {v:,}")

    # Parameter comparison
    # Dispatch has router params extra; baseline has wider FFN
    # They won't match exactly (router is small overhead) but should be close
    d_ffn = sum(v for k, v in dp["groups"].items() if k == "blocks")
    b_ffn = sum(v for k, v in bp["groups"].items() if k == "blocks")
    print(f"\n  Block params — dispatch: {d_ffn:,}  baseline: {b_ffn:,}  "
          f"ratio: {d_ffn/b_ffn:.3f}")

    # Gradient flow test
    print("\n── Gradient flow ──")
    def test_loss(model, tok, tgt):
        _, loss = model(tok, tgt)
        return loss

    grad_fn = nn.value_and_grad(dispatch_model, test_loss)
    lv, grads = grad_fn(dispatch_model, tokens, targets)
    mx.eval(lv, grads)

    # Check router gradients exist
    for li in range(cfg.n_layers):
        gate_grad = grads["blocks"][li]["router"]["gate"]["weight"]
        mx.eval(gate_grad)
        gn = float(mx.sqrt(mx.sum(gate_grad * gate_grad)).item())
        print(f"  Layer {li} router grad norm: {gn:.6f}")

    # Check per-op FFN gradients
    for li in range(cfg.n_layers):
        for oi in range(cfg.n_ops):
            up_grad = grads["blocks"][li]["op_ups"][oi]["weight"]
            mx.eval(up_grad)
            gn = float(mx.sqrt(mx.sum(up_grad * up_grad)).item())
            print(f"  Layer {li} op {oi} up grad norm: {gn:.6f}")

    print("\nmodel.py self-test: all ok ✓")
