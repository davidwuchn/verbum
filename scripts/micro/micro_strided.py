"""Strided-attention micro — surgical swap, float microscope left pristine.

Does Fibonacci-strided attention work? (s262). v15 bet its attention on
Fibonacci strides, but the bet was never isolated: v15 changed strides +
ternary + TD + VSM controllers + a 6-term loss simultaneously, and the only
functional assessment (s191) found attention collapsed to pure relay — with
blame plausibly on ternary/TD, not the stride geometry. This module isolates
the geometry: float32 micro, everything identical, attention SUPPORT is the
only changed variable.

Implementation: masked attention, not gathered attention. Each head gets a
single stride s; its allowed key set is the v15 grid {q - s*w + r | w in
0..W-1, r in -R..+R} intersected with causality. This tests the INFORMATION
ACCESS claim (can composition form within strided support?), not the FLOP
claim (masked attention still computes full scores). At the microscope scale
that is the right register: s191 showed the failure mode is functional
(relay collapse), not computational.

Arms (per-layer, per-head stride assignment):
  dense    — unmodified micro (control; swap is a no-op)
  local    — all heads stride 1 (locality null: is local support enough
             on this short corpus? strides must beat this to earn coverage)
  fib      — interleaved Fibonacci ladder: every layer sees local+long
             [1,3,8,21] / [2,5,13,34] alternating
  fibband  — v15-faithful ascending/descending bands: [1,2,3,5] /
             [8,13,21,34] / [8,13,21,34] / [1,2,3,5] — long-range access
             exists ONLY in the middle layers (sole-provider geometry)

Helpers:
  stridify_attention_(model, arm)  → swap MultiHeadAttention in place
  attention_diagnostics(model, batch) → relay cos(out, V_self) + entropy
                                        per layer/head (the s191 instrument)

micro_model.py is NOT edited (the microscope stays pristine).

License: MIT.
"""

from __future__ import annotations

import math

import mlx.core as mx
import numpy as np
from micro_model import MicroConfig, MicroModel, MultiHeadAttention

# ══════════════════════════════════════════════════════════════════════
# Stride geometry (s189: W=8 window, ±2 neighbor radius)
# ══════════════════════════════════════════════════════════════════════

WINDOW = 8
RADIUS = 2

# Per-arm stride assignment: {layer: [stride per head]}
ARM_STRIDES: dict[str, dict[int, list[int]]] = {
    "local": {li: [1, 1, 1, 1] for li in range(4)},
    "fib": {
        0: [1, 3, 8, 21],
        1: [2, 5, 13, 34],
        2: [1, 3, 8, 21],
        3: [2, 5, 13, 34],
    },
    "fibband": {
        0: [1, 2, 3, 5],
        1: [8, 13, 21, 34],
        2: [8, 13, 21, 34],
        3: [1, 2, 3, 5],
    },
}
ARMS = ("dense", "local", "fib", "fibband")


def allowed_distances(
    stride: int, window: int = WINDOW, radius: int = RADIUS
) -> set[int]:
    """The v15 grid: {s*w + r | w in 0..W-1, r in -R..+R}, non-negative."""
    out: set[int] = set()
    for w in range(window):
        for r in range(-radius, radius + 1):
            d = stride * w + r
            if d >= 0:
                out.add(d)
    return out


def build_stride_mask(
    strides: list[int],
    seq_len: int,
    window: int = WINDOW,
    radius: int = RADIUS,
) -> mx.array:
    """(H, L, L) additive mask: 0 where key allowed, -inf elsewhere.

    Causality is included (allowed distances are >= 0). d=0 is always
    allowed (w=0, r=0) so no softmax row is empty.
    """
    length = seq_len
    dist = np.arange(length)[:, None] - np.arange(length)[None, :]  # q - k
    masks = []
    for s in strides:
        dset = np.array(sorted(allowed_distances(s, window, radius)))
        ok = np.isin(dist, dset) & (dist >= 0)
        masks.append(np.where(ok, 0.0, float("-inf")).astype(np.float32))
    return mx.array(np.stack(masks))  # (H, L, L)


def coverage(strides: list[int], max_d: int = 64) -> float:
    """Fraction of distances 0..max_d-1 reachable by the union of strides."""
    union: set[int] = set()
    for s in strides:
        union |= allowed_distances(s)
    return len([d for d in range(max_d) if d in union]) / max_d


# ══════════════════════════════════════════════════════════════════════
# Strided attention (drop-in; identical parameter tree)
# ══════════════════════════════════════════════════════════════════════


class StridedMultiHeadAttention(MultiHeadAttention):
    """MultiHeadAttention restricted to per-head strided support.

    Same parameters, same math — only the attention support changes.
    The stride mask REPLACES the causal mask (it is a subset of it).
    `_`-prefixed attrs are not MLX parameters: param tree matches the
    parent exactly, so seeded init is identical across arms.
    """

    def __init__(self, d_model: int, n_heads: int, head_strides: list[int]):
        super().__init__(d_model, n_heads)
        assert len(head_strides) == n_heads
        self._head_strides = list(head_strides)
        self._smask_cache: dict[int, mx.array] = {}

    def _stride_mask(self, seq_len: int) -> mx.array:
        m = self._smask_cache.get(seq_len)
        if m is None:
            m = build_stride_mask(self._head_strides, seq_len)
            self._smask_cache[seq_len] = m
        return m

    def __call__(self, x: mx.array, mask: mx.array | None = None) -> mx.array:
        length = x.shape[1]
        # (H, L, L) broadcasts over batch against (B, H, L, L) scores.
        return super().__call__(x, mask=self._stride_mask(length))


def stridify_attention_(
    model: MicroModel, arm: str
) -> list[tuple[str, StridedMultiHeadAttention]]:
    """Replace every block's attention with the arm's strided version.

    In place. `arm='dense'` is a no-op (returns []). Fresh modules are
    seeded by the surrounding mx.random state; because the parameter
    tree is identical, building each arm under the same seed yields
    identical initial weights (asserted in the smoke test).
    """
    if arm == "dense":
        return []
    assignment = ARM_STRIDES[arm]
    cfg = model.cfg
    swapped: list[tuple[str, StridedMultiHeadAttention]] = []
    for li, block in enumerate(model.blocks):
        new = StridedMultiHeadAttention(
            cfg.d_model, cfg.n_heads, assignment[li]
        )
        # Keep the seeded weights: transplant the originals.
        for name in ("q_proj", "k_proj", "v_proj", "o_proj"):
            getattr(new, name).weight = getattr(block.attn, name).weight
        block.attn = new
        swapped.append((f"blocks.{li}.attn", new))
    mx.eval(model.parameters())
    return swapped


def build_strided_micro(
    cfg: MicroConfig, arm: str
) -> tuple[MicroModel, list[tuple[str, StridedMultiHeadAttention]]]:
    """Construct a micro model and stridify its attention."""
    model = MicroModel(cfg)
    mx.eval(model.parameters())
    mods = stridify_attention_(model, arm)
    return model, mods


# ══════════════════════════════════════════════════════════════════════
# Diagnostics — the s191 instruments
# ══════════════════════════════════════════════════════════════════════


def attention_diagnostics(
    model: MicroModel, tokens: mx.array
) -> list[dict]:
    """Per layer/head: relay cosine cos(attn_out, V_self) and entropy.

    relay ≈ 1.0 → the head passes its own value through (I combinator,
    the s191 collapse signature). entropy → eff_pos = exp(H) effective
    attended positions.
    """
    model.set_capture(True)
    model(tokens)
    out = []
    for li, block in enumerate(model.blocks):
        tr = block.attn.trace
        v = tr["v"]                    # (B, H, L, dh)
        attn_out = tr["attn_out"]      # (B, H, L, dh)
        w = tr["attn_weights"]         # (B, H, L, L)
        dot = mx.sum(v * attn_out, axis=-1)
        nv = mx.sqrt(mx.sum(v * v, axis=-1) + 1e-8)
        no = mx.sqrt(mx.sum(attn_out * attn_out, axis=-1) + 1e-8)
        relay = dot / (nv * no)                       # (B, H, L)
        relay_h = mx.mean(relay, axis=(0, 2))         # (H,)
        ent = -mx.sum(w * mx.log(w + 1e-10), axis=-1)  # (B, H, L)
        ent_h = mx.mean(ent, axis=(0, 2))             # (H,)
        mx.eval(relay_h, ent_h)
        out.append({
            "layer": li,
            "relay": [round(float(r), 4) for r in relay_h.tolist()],
            "entropy": [round(float(e), 4) for e in ent_h.tolist()],
            "eff_pos": [round(math.exp(float(e)), 2) for e in ent_h.tolist()],
        })
    model.set_capture(False)
    # Clear traces: mx.arrays stored in `trace` dicts (not _-prefixed)
    # would otherwise enter the MLX parameter tree and break the
    # optimizer's tree_map on the next update.
    for block in model.blocks:
        block.trace = {}
        block.attn.trace = {}
        block.ffn.trace = {}
    return out


# ══════════════════════════════════════════════════════════════════════
# Smoke test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import mlx.nn as nn

    print("=" * 60)
    print("micro_strided.py smoke test")
    print("=" * 60)

    cfg = MicroConfig(d_model=64, d_ff=128, n_heads=4, n_layers=4,
                      max_seq_len=64, use_parity_loss=False,
                      crystal_lambda=0.0)
    tokens = mx.random.randint(0, 1000, (2, 48))
    targets = mx.random.randint(0, 1000, (2, 48))

    # Coverage report
    for arm in ("local", "fib", "fibband"):
        for li, strides in ARM_STRIDES[arm].items():
            cov = coverage(strides)
            print(f"{arm:8s} L{li} strides={strides}  coverage(d<64)={cov:.2f}")

    # Mask sanity: subset of causal, self always allowed
    m = build_stride_mask([1, 3, 8, 21], 48)
    m_np = np.array(m)
    assert m_np.shape == (4, 48, 48)
    for h in range(4):
        assert np.all(np.isinf(m_np[h][np.triu_indices(48, k=1)])), "future leak"
        assert np.all(np.diag(m_np[h]) == 0.0), "self not allowed"
    print("mask: causal-subset + self-allowed ✓")

    # Identical init across arms under the same seed
    params = {}
    losses = {}
    for arm in ARMS:
        mx.random.seed(7)
        np.random.seed(7)  # crystal-embedding pad uses np.random
        model, mods = build_strided_micro(cfg, arm)
        flat = dict(nn.utils.tree_flatten(model.parameters()))
        params[arm] = {k: np.array(v) for k, v in flat.items()}
        n_params = sum(v.size for v in params[arm].values())

        def loss_fn(m, tok, tgt):
            _, loss = m(tok, tgt)
            return loss

        lv, grads = nn.value_and_grad(model, loss_fn)(model, tokens, targets)
        mx.eval(lv, grads)
        assert lv.item() == lv.item(), f"{arm}: NaN loss"
        losses[arm] = float(lv.item())
        diags = attention_diagnostics(model, tokens)
        assert len(diags) == cfg.n_layers
        print(f"{arm:8s} params={n_params:,}  loss={losses[arm]:.4f}  "
              f"L0 relay={diags[0]['relay']}  swapped={len(mods)}")

    ref_keys = set(params["dense"])
    for arm in ("local", "fib", "fibband"):
        assert set(params[arm]) == ref_keys, f"{arm}: param tree differs"
        for k in ref_keys:
            assert np.allclose(params[arm][k], params["dense"][k]), (
                f"{arm}: init differs at {k}"
            )
    print("param trees + seeded inits identical across arms ✓")

    # Strided arms must differ from dense in output (mask is active)
    assert losses["fib"] != losses["dense"], "fib mask had no effect"
    assert losses["fibband"] != losses["dense"], "fibband mask had no effect"
    print("stride masks change the computation ✓")

    print("\nmicro_strided.py: smoke test passed ✓")
