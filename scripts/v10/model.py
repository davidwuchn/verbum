"""
v10 Model — Strided compressor + tree of VSMs.

Architecture:

  tokens (4096) → [Strided Compressor W=8] → compressed (4096, d)
                                                    ↓
                            [Tree of VSMs — shared weights at every node]
                            each node = VSM receiving:
                              S5: compressed context at operator position (identity)
                              S4: children's values + types (intelligence)
                              S3: type check (control)
                              S1: kernel dispatch → exact computation (operations)
                              S2: output value + type → parent (coordination)
                                                    ↓
                                                 result

Compressor: strided windowed attention.
  Level 0: stride 1, W=8  — word level (±8 tokens)
  Level 1: stride 8, W=8  — phrase level (±64 tokens)
  Level 2: stride 64, W=8 — clause level (±512 tokens)
  Shared weights, iterated 2×. Proven setup from CompressorLM.

Tree of VSMs: each node is a shared-weight module.
  Input:  [context_d, child_val_1, child_type_1, child_val_2, child_type_2]
  Output: op_logits (22 ops), value, type
  Same weights at every tree position and depth — self-similar.
  Proven architecture from v9 (vsm_tree_v3-v5): 100% accuracy, 8K weights.

License: MIT
"""

from __future__ import annotations

import math

import mlx.core as mx
import mlx.nn as nn

from config import V10Config
from ternary import TernaryLinear, TernaryEmbedding


# ══════════════════════════════════════════════════════════════════
# Building blocks
# ══════════════════════════════════════════════════════════════════


class RMSNorm(nn.Module):
    def __init__(self, d: int, eps: float = 1e-6):
        super().__init__()
        self.weight = mx.ones((d,))
        self.eps = eps

    def __call__(self, x: mx.array) -> mx.array:
        rms = mx.rsqrt(mx.mean(x * x, axis=-1, keepdims=True) + self.eps)
        return x * rms * self.weight


class StridedWindowAttention(nn.Module):
    """Windowed self-attention with configurable stride.

    Each position attends only to W positions at the given stride.
    Position i attends to positions {i - (W//2)*stride, ..., i + (W//2-1)*stride}
    filtered to valid indices.

    This creates the multi-scale structure:
      stride=1, W=8:  word-level  (±4 tokens)
      stride=8, W=8:  phrase-level (±32 tokens = ±4 phrases)
      stride=64, W=8: clause-level (±256 tokens = ±4 clauses)

    Hyperbolic distance bias: bias(i,j) = -α·ln(|i-j|/stride + 1)
    """

    def __init__(self, d_model: int, n_heads: int, window: int = 8,
                 spiral_alpha: float = 1.18):
        super().__init__()
        assert d_model % n_heads == 0
        self.n_heads = n_heads
        self.d_head = d_model // n_heads
        self.scale = self.d_head ** -0.5
        self.window = window

        self.q_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.k_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.v_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.o_proj = TernaryLinear(d_model, d_model, pre_norm=False)

        self.spiral_alpha = mx.array([spiral_alpha])

    def __call__(self, x: mx.array, stride: int = 1) -> mx.array:
        B, L, D = x.shape
        W = self.window

        # For strided attention: subsample positions at stride intervals,
        # apply windowed attention, then scatter back.
        # Positions at this stride: 0, stride, 2*stride, ...
        n_positions = (L + stride - 1) // stride

        if stride == 1:
            # Full-resolution: use standard windowed attention
            return self._windowed_attention(x, W)
        else:
            # Subsample at stride, attend within window, scatter back.
            # indices shape: (n_pos,)  — the strided token positions in [0, L)
            indices = mx.arange(0, min(n_positions * stride, L), stride)
            n_pos = int(indices.shape[0])

            # Gather: (B, n_pos, D)
            x_strided = x[:, indices, :]

            # Windowed attention on the strided positions → (B, n_pos, D)
            out_strided = self._windowed_attention(x_strided, W)

            # Scatter back via differentiable one-hot projection.
            # scatter_matrix: (n_pos, L)  — one-hot rows at strided positions
            # out = out_strided @ scatter_matrix  →  (B, n_pos, D) × (n_pos, L) not right.
            # Correct: scatter (B, n_pos, D) → (B, L, D) using transpose multiply.
            #   scatter_matrix[i, j] = 1 if j == indices[i], else 0.   shape (n_pos, L)
            #   out_strided (B, n_pos, D) transposed to (B, D, n_pos)
            #   result (B, D, L) = (B, D, n_pos) @ (n_pos, L), then transpose → (B, L, D)
            # This keeps the operation fully inside the MLX autodiff graph.
            scatter_mat = mx.zeros((n_pos, L))
            for ii in range(n_pos):
                scatter_mat = scatter_mat.at[ii, int(indices[ii].item())].add(1.0)
            # (B, D, n_pos) @ (n_pos, L) → (B, D, L) → (B, L, D)
            out = (out_strided.transpose(0, 2, 1) @ scatter_mat).transpose(0, 2, 1)

            return out

    def _windowed_attention(self, x: mx.array, W: int) -> mx.array:
        """Standard windowed self-attention with spiral bias."""
        B, L, D = x.shape
        H = self.n_heads
        d_h = self.d_head

        q = self.q_proj(x).reshape(B, L, H, d_h).transpose(0, 2, 1, 3)
        k = self.k_proj(x).reshape(B, L, H, d_h).transpose(0, 2, 1, 3)
        v = self.v_proj(x).reshape(B, L, H, d_h).transpose(0, 2, 1, 3)

        # Full attention scores (for short sequences this is fine;
        # for seq=4096 we'd want true windowed, but MLX doesn't have
        # native sparse attention — we mask instead)
        scores = (q @ k.transpose(0, 1, 3, 2)) * self.scale  # (B, H, L, L)

        # Window mask: only attend within W positions
        positions = mx.arange(L)
        dist = mx.abs(positions.reshape(1, 1, L, 1) - positions.reshape(1, 1, 1, L))
        window_mask = mx.where(dist < W, 0.0, -1e9)  # (1, 1, L, L)
        scores = scores + window_mask

        # Spiral bias within window
        safe_dist = mx.maximum(dist.astype(mx.float32), 1e-6)
        bias = -self.spiral_alpha * mx.log(safe_dist + 1.0)
        bias = mx.where(dist < W, bias, 0.0)
        scores = scores + bias

        attn = mx.softmax(scores, axis=-1)
        out = (attn @ v).transpose(0, 2, 1, 3).reshape(B, L, D)
        return self.o_proj(out)


class FeedForward(nn.Module):
    """SwiGLU FFN with ternary weights."""

    def __init__(self, d_model: int, d_ff: int):
        super().__init__()
        self.gate_proj = TernaryLinear(d_model, d_ff, pre_norm=False)
        self.up_proj = TernaryLinear(d_model, d_ff, pre_norm=False)
        self.down_proj = TernaryLinear(d_ff, d_model, pre_norm=False)

    def __call__(self, x: mx.array) -> mx.array:
        return self.down_proj(nn.silu(self.gate_proj(x)) * self.up_proj(x))


class CompressorBlock(nn.Module):
    """Single transformer block: strided windowed attention + FFN."""

    def __init__(self, d_model: int, n_heads: int, d_ff: int, window: int,
                 spiral_alpha: float):
        super().__init__()
        self.attn_norm = RMSNorm(d_model)
        self.attn = StridedWindowAttention(d_model, n_heads, window, spiral_alpha)
        self.ffn_norm = RMSNorm(d_model)
        self.ffn = FeedForward(d_model, d_ff)

    def __call__(self, x: mx.array, stride: int = 1) -> mx.array:
        x = x + self.attn(self.attn_norm(x), stride=stride)
        x = x + self.ffn(self.ffn_norm(x))
        return x


class CompressorLevel(nn.Module):
    """Stack of CompressorBlocks at one scale level."""

    def __init__(self, n_layers: int, d_model: int, n_heads: int,
                 d_ff: int, window: int, spiral_alpha: float):
        super().__init__()
        self.layers = [
            CompressorBlock(d_model, n_heads, d_ff, window, spiral_alpha)
            for _ in range(n_layers)
        ]
        self.norm = RMSNorm(d_model)

    def __call__(self, x: mx.array, stride: int = 1) -> mx.array:
        for layer in self.layers:
            x = layer(x, stride=stride)
        return self.norm(x)


# ══════════════════════════════════════════════════════════════════
# SelfSimilarCompressor — strided, W=8, shared weights
# ══════════════════════════════════════════════════════════════════


class SelfSimilarCompressor(nn.Module):
    """Multi-scale self-similar compressor with strided windowed attention.

    Proven setup: seq=4096, W=8, strides=(1, 8, 64), 2 iterations.

    The SAME CompressorLevel is applied at each stride (self-similar).
    All tensors stay at full sequence length — no pooling.
    Prediction errors between scales enrich the residual stream.
    """

    def __init__(self, cfg: V10Config):
        super().__init__()
        self.cfg = cfg

        self.embed = TernaryEmbedding(cfg.vocab_size, cfg.d_model)

        # Single shared level — self-similar across all strides
        self.shared_level = CompressorLevel(
            n_layers=cfg.n_layers_per_level,
            d_model=cfg.d_model,
            n_heads=cfg.n_heads,
            d_ff=cfg.d_ff,
            window=cfg.window,
            spiral_alpha=cfg.spiral_alpha_init,
        )

        # Prediction heads between levels
        self.predict_heads = [
            TernaryLinear(cfg.d_model, cfg.d_model, pre_norm=True)
            for _ in range(cfg.n_levels - 1)
        ]

        self.output_norm = RMSNorm(cfg.d_model)

    def __call__(self, tokens: mx.array) -> mx.array:
        """tokens (B, L) → compressed representations (B, L, d_model)."""
        h = self.embed(tokens)

        for _iteration in range(self.cfg.n_iterations):
            # Process at each stride (fine → coarse)
            scale_outputs = []
            for stride in self.cfg.strides:
                h_level = self.shared_level(h, stride=stride)
                scale_outputs.append(h_level)

            # Prediction error accumulation
            for i in range(len(scale_outputs) - 1):
                predicted = self.predict_heads[i](scale_outputs[i])
                error = scale_outputs[i + 1] - predicted
                h = h + error

            h = h + scale_outputs[0]

        return self.output_norm(h)


# ══════════════════════════════════════════════════════════════════
# VSMNode — shared-weight node for tree of VSMs
# ══════════════════════════════════════════════════════════════════


class VSMNode(nn.Module):
    """A single VSM node — shared weights, used at every tree position.

    Each node in the expression tree is a viable system:
      S5 (identity):      compressed context embedding (who am I?)
      S4 (intelligence):  children's values + types (what are my inputs?)
      S3 (control):       type checking (are inputs compatible?)
      S1 (operations):    kernel dispatch (what do I compute?)
      S2 (coordination):  output value + type to parent

    Input features:
      - context: d_model floats (from compressor at operator position)
      - child 1 value: 1 float (or 0 if leaf/unary)
      - child 1 type:  n_types one-hot (or zeros)
      - child 2 value: 1 float (or 0 if leaf/binary with 1 child)
      - child 2 type:  n_types one-hot (or zeros)
      Total input: d_model + 2*(1 + n_types) = d_model + 12 (for 5 types)

    Output:
      - op_logits: n_ops floats (operation classification)
    """

    def __init__(self, d_model: int, n_ops: int, n_types: int = 5,
                 hidden: int = 128, max_children: int = 3):
        super().__init__()
        self.d_model = d_model
        self.n_ops = n_ops
        self.n_types = n_types
        self.max_children = max_children

        # Input: context + per-child (value + type one-hot)
        child_features = max_children * (1 + n_types)  # 3 * 6 = 18
        input_dim = d_model + child_features

        # Pad input_dim to multiple of 16 for ternary packing
        self.input_dim = ((input_dim + 15) // 16) * 16
        self.pad_size = self.input_dim - (d_model + child_features)

        # Two-layer network: input → hidden → op_logits
        self.norm = RMSNorm(self.input_dim)
        self.fc1 = nn.Linear(self.input_dim, hidden)
        self.fc2 = nn.Linear(hidden, n_ops)

    def __call__(
        self,
        context: mx.array,       # (*, d_model) — compressed rep at op position
        child_values: mx.array,   # (*, max_children) — children's computed values
        child_types: mx.array,    # (*, max_children) — children's type indices (int)
    ) -> mx.array:
        """Forward: context + children info → op_logits (*, n_ops)."""
        # One-hot encode child types
        child_type_oh = mx.zeros((*child_types.shape, self.n_types))
        # Manual one-hot since mx doesn't have a direct one_hot
        for i in range(self.max_children):
            for t in range(self.n_types):
                mask = (child_types[..., i] == t)
                child_type_oh = child_type_oh.at[..., i, t].add(
                    mask.astype(mx.float32)
                )

        # Flatten child features: [val1, type1_oh, val2, type2_oh, ...]
        child_feats = []
        for i in range(self.max_children):
            child_feats.append(child_values[..., i:i+1])  # (*, 1)
            child_feats.append(child_type_oh[..., i, :])   # (*, n_types)
        child_feat = mx.concatenate(child_feats, axis=-1)  # (*, max_children*(1+n_types))

        # Concatenate with context
        x = mx.concatenate([context, child_feat], axis=-1)

        # Pad to multiple of 16
        if self.pad_size > 0:
            pad = mx.zeros((*x.shape[:-1], self.pad_size))
            x = mx.concatenate([x, pad], axis=-1)

        # Forward through shared network
        x = self.norm(x)
        x = nn.gelu(self.fc1(x))
        return self.fc2(x)  # (*, n_ops)


# ══════════════════════════════════════════════════════════════════
# V10Model — strided compressor + tree of VSMs
# ══════════════════════════════════════════════════════════════════


class V10Model(nn.Module):
    """v10: Strided compressor + tree of shared-weight VSM nodes.

    Forward:
      1. tokens → compressor → compressed representations (B, L, d)
      2. For each tree: bottom-up traversal through VSMNode
         - Leaves: pass through value, type=INT
         - Internal nodes: VSMNode(context, children_values, children_types) → op_logits
      3. Op logits → argmax → kernel dispatch → exact result

    The tree traversal is done per-example (trees have different shapes).
    The VSMNode weights are shared across ALL nodes and ALL examples.
    """

    def __init__(self, cfg: V10Config):
        super().__init__()
        self.cfg = cfg
        self.compressor = SelfSimilarCompressor(cfg)
        self.vsm_node = VSMNode(
            d_model=cfg.d_model,
            n_ops=cfg.n_ops,
            n_types=5,
            hidden=cfg.dispatcher_hidden,
            max_children=3,  # max arity (ternary for 'if')
        )

    def compress(self, tokens: mx.array) -> mx.array:
        """tokens (B, L) → compressed representations (B, L, d_model)."""
        return self.compressor(tokens)

    def dispatch_node(
        self,
        context: mx.array,       # (d_model,) — compressed rep at this node's position
        child_values: mx.array,   # (max_children,) — children's values
        child_types: mx.array,    # (max_children,) — children's type indices
    ) -> mx.array:
        """Single node dispatch: context + children → op_logits (n_ops,)."""
        # Add batch dims for the VSMNode
        ctx = context.reshape(1, -1)
        cv = child_values.reshape(1, -1)
        ct = child_types.reshape(1, -1)
        logits = self.vsm_node(ctx, cv, ct)
        return logits[0]  # (n_ops,)

    def forward_tree(
        self,
        h: mx.array,              # (L, d_model) — compressed reps for one example
        tree_nodes: list,          # list of node dicts from data pipeline
        node_positions: list[int], # token position for each node
    ) -> tuple[list[mx.array], list[int], list[int]]:
        """Evaluate one tree bottom-up through shared VSMNode.

        Returns:
            op_logits_list: list of (n_ops,) logits for each internal node
            predicted_ops: list of int — argmax op for each internal node
            node_indices: which nodes are internal (have op_logits)
        """
        from kernel import kernel_eval, N_TYPES

        n_nodes = len(tree_nodes)
        # Storage for computed values and types
        values = [0] * n_nodes
        types = [0] * n_nodes  # 0 = INT
        op_logits_list = []
        node_indices = []

        # Process in order (data.py stores nodes in DFS pre-order;
        # we need bottom-up, so reverse)
        # Actually, we need topological order: children before parents.
        # For DFS pre-order, children come after parent.
        # Process in REVERSE to get children before parents.
        for i in range(n_nodes - 1, -1, -1):
            node = tree_nodes[i]

            if node.is_leaf:
                # Leaves: pass through value
                values[i] = node.value if node.value is not None else 0
                types[i] = 0  # INT for numbers
                if isinstance(node.value, bool):
                    types[i] = 1  # BOOL
                    values[i] = int(node.value)
                continue

            # Internal node: get children's values and types
            children = node.children if hasattr(node, 'children') else []
            child_vals = mx.zeros((3,))
            child_typs = mx.zeros((3,), dtype=mx.int32)

            for ci, child_idx in enumerate(children[:3]):
                child_vals = child_vals.at[ci].add(float(values[child_idx]))
                child_typs = child_typs.at[ci].add(types[child_idx])

            # Get compressed context at this node's token position
            pos = node_positions[i]
            context = h[pos]  # (d_model,)

            # VSMNode forward
            logits = self.dispatch_node(context, child_vals, child_typs)
            op_logits_list.append(logits)
            node_indices.append(i)

            # Predicted op for computing the result
            pred_op = int(mx.argmax(logits).item())

            # Execute kernel with predicted op
            child_val_list = [values[ci] for ci in children]
            child_aux_list = [0] * len(children)  # aux for FN types
            child_type_list = [types[ci] for ci in children]

            try:
                result_val, result_aux, result_type = kernel_eval(
                    pred_op, child_val_list, child_aux_list, child_type_list
                )
                values[i] = result_val
                types[i] = result_type
            except Exception:
                values[i] = 0
                types[i] = 4  # ERROR

        # Reverse to match tree order (root first)
        op_logits_list.reverse()
        node_indices.reverse()

        predicted_ops = [int(mx.argmax(l).item()) for l in op_logits_list]
        return op_logits_list, predicted_ops, node_indices

    def forward_batch_trees(
        self,
        h: mx.array,              # (B, L, d_model)
        batch_trees: list,         # list of (tree_nodes, node_positions) per example
    ) -> tuple[list[list[mx.array]], list[list[int]]]:
        """Process all trees in a batch.

        Returns:
            all_logits: list of list of (n_ops,) per example per node
            all_pred_ops: list of list of int per example
        """
        B = h.shape[0]
        all_logits = []
        all_pred_ops = []

        for b in range(B):
            tree_nodes, node_positions = batch_trees[b]
            logits, pred_ops, _ = self.forward_tree(
                h[b], tree_nodes, node_positions
            )
            all_logits.append(logits)
            all_pred_ops.append(pred_ops)

        return all_logits, all_pred_ops


# ══════════════════════════════════════════════════════════════════
# Factory
# ══════════════════════════════════════════════════════════════════


def create_model(cfg: V10Config) -> V10Model:
    """Create and initialize a V10Model."""
    model = V10Model(cfg)
    mx.eval(model.parameters())
    return model


def count_parameters(model: nn.Module) -> dict[str, int]:
    """Count parameters by component."""
    from mlx.utils import tree_flatten

    counts = {"total": 0, "trainable": 0}
    all_params = tree_flatten(model.parameters())
    trainable = tree_flatten(model.trainable_parameters())

    counts["total"] = sum(p.size for _, p in all_params)
    counts["trainable"] = sum(p.size for _, p in trainable)

    for name in ("compressor", "vsm_node"):
        component = getattr(model, name, None)
        if component is not None:
            params = tree_flatten(component.parameters())
            counts[name] = sum(p.size for _, p in params)

    return counts


# ══════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    cfg = V10Config(d_model=64, d_ff=192, n_heads=4,
                    dispatcher_hidden=32, vocab_size=256, max_seq_len=32)
    model = create_model(cfg)

    # Test compressor
    tokens = mx.array([[1, 5, 27, 28, 4, 0, 0, 0]])  # (1, 8) — "(+ 0 1)" padded
    h = model.compress(tokens)
    print(f"Compressed: {h.shape}")  # (1, 8, 64)

    # Test single VSMNode
    context = h[0, 1]  # context at operator position
    child_vals = mx.array([0.0, 1.0, 0.0])
    child_types = mx.array([0, 0, 0], dtype=mx.int32)
    logits = model.dispatch_node(context, child_vals, child_types)
    print(f"Node logits: {logits.shape}")  # (22,)
    print(f"Predicted op: {int(mx.argmax(logits).item())}")

    params = count_parameters(model)
    print(f"Parameters: {params}")
    print("model.py self-test: all ok ✓")
