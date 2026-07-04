"""Ternary-FFN micro — surgical swap, float microscope left pristine.

micro_model.py is explicitly "the microscope, not the target" (float32
throughout). To test from-scratch ternary WITHOUT contaminating it, this
module swaps ONLY the SwiGLUFFN linears (gate/key/value) for
TernaryShadowLinear, in place, after construction. Crystal embeddings,
attention, embeddings, and the output path stay float — so the ONLY
changed variable is the FFN ternarization paradigm (td | st).

This is the Arm 0 / Arm 1 bench:
  - td: reproduce the flip-flop (holographic overloading → sign oscillation)
  - st: does CAT-Q soft→hard relaxation converge by HIDING the overload?

Helpers here drive the whole ternary population from the training loop:
  ternarize_ffn_(model, mode, cfg)  → list[(path, TernaryShadowLinear)]
  anneal_all(mods, step, total)     → ST sharpness curriculum
  observe_all(mods)                 → per-step flip snapshot (aggregate)
  flip_summary_all(mods)            → end-of-run oscillation report
  ternary_stats_all(mods)           → sparsity / register health

License: MIT.
"""

from __future__ import annotations

import mlx.core as mx
from micro_model import MicroConfig, MicroModel, SwiGLUFFN
from ternary_st import TernaryConfig, TernaryShadowLinear

# ══════════════════════════════════════════════════════════════════════
# Surgical FFN ternarization
# ══════════════════════════════════════════════════════════════════════


def _ternary_like(linear, cfg: TernaryConfig) -> TernaryShadowLinear:
    """Build a TernaryShadowLinear matching an nn.Linear's (in, out)."""
    # nn.Linear stores weight as (out_features, in_features).
    out_features, in_features = linear.weight.shape
    return TernaryShadowLinear(in_features, out_features, cfg)


def ternarize_ffn_(
    model: MicroModel,
    mode: str = "st",
    cfg: TernaryConfig | None = None,
) -> list[tuple[str, TernaryShadowLinear]]:
    """Replace every SwiGLUFFN's gate/key/value proj with ternary linears.

    In place. Returns [(path, module)] for annealing + instrumentation.
    Attention and crystal stay float — the FFN is the ONLY changed variable.
    """
    base = cfg or TernaryConfig()
    tcfg = TernaryConfig(
        mode=mode,
        sharpness_start=base.sharpness_start,
        sharpness_end=base.sharpness_end,
        anneal_frac=base.anneal_frac,
        delta_ratio_init=base.delta_ratio_init,
        learn_delta=base.learn_delta,
    )

    swapped: list[tuple[str, TernaryShadowLinear]] = []
    for li, block in enumerate(model.blocks):
        ffn = block.ffn
        assert isinstance(ffn, SwiGLUFFN), f"block {li} ffn is {type(ffn)}"
        for name in ("gate_proj", "key_proj", "value_proj"):
            old = getattr(ffn, name)
            new = _ternary_like(old, tcfg)
            setattr(ffn, name, new)
            swapped.append((f"blocks.{li}.ffn.{name}", new))
    mx.eval(model.parameters())
    return swapped


def build_ternary_micro(
    cfg: MicroConfig,
    mode: str = "st",
    tcfg: TernaryConfig | None = None,
) -> tuple[MicroModel, list[tuple[str, TernaryShadowLinear]]]:
    """Construct a micro model and ternarize its FFN. mode='none' = float."""
    model = MicroModel(cfg)
    mx.eval(model.parameters())
    if mode == "none":
        return model, []
    mods = ternarize_ffn_(model, mode=mode, cfg=tcfg)
    return model, mods


# ══════════════════════════════════════════════════════════════════════
# Population drivers (called from the training loop)
# ══════════════════════════════════════════════════════════════════════


def anneal_all(
    mods: list[tuple[str, TernaryShadowLinear]],
    step: int,
    total_steps: int,
) -> None:
    for _, m in mods:
        m.anneal(step, total_steps)


def observe_all(mods: list[tuple[str, TernaryShadowLinear]]) -> dict[str, float]:
    """Aggregate per-step flip snapshot across all ternary FFN linears."""
    if not mods:
        return {}
    keys = ("flipped_this_step", "frac_zero", "frac_pos", "frac_neg")
    acc = dict.fromkeys(keys, 0.0)
    n = 0
    for _, m in mods:
        s = m.observe_flips()
        for k in keys:
            acc[k] += s.get(k, 0.0)
        n += 1
    return {k: v / n for k, v in acc.items()}


def flip_summary_all(
    mods: list[tuple[str, TernaryShadowLinear]],
) -> dict[str, dict[str, float]]:
    """Per-layer oscillation report at end of run."""
    return {path: m.flip_summary() for path, m in mods}


def ternary_stats_all(
    mods: list[tuple[str, TernaryShadowLinear]],
) -> dict[str, dict[str, float]]:
    return {path: m.ternary_stats() for path, m in mods}


# ══════════════════════════════════════════════════════════════════════
# Smoke test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import mlx.nn as nn

    print("=" * 60)
    print("micro_ternary.py smoke test")
    print("=" * 60)

    mx.random.seed(0)
    cfg = MicroConfig(d_model=64, d_ff=128, n_heads=4, n_layers=2,
                      max_seq_len=64, use_parity_loss=False, crystal_lambda=0.0)

    tokens = mx.random.randint(0, 1000, (2, 32))
    targets = mx.random.randint(0, 1000, (2, 32))

    # ── Float baseline: build_ternary_micro('none') must be untouched micro ──
    fmodel, fmods = build_ternary_micro(cfg, mode="none")
    assert fmods == []
    _, floss = fmodel(tokens, targets)
    mx.eval(floss)
    assert isinstance(floss.item(), float) and floss.item() == floss.item()
    print(f"float baseline: loss {floss.item():.4f}, 0 ternary mods ✓")

    for mode in ("td", "st"):
        model, mods = build_ternary_micro(cfg, mode=mode)
        assert len(mods) == cfg.n_layers * 3, len(mods)

        # forward + backward produce finite loss and gradients
        def loss_fn(m, tok, tgt):
            _, loss = m(tok, tgt)
            return loss

        lv, grads = nn.value_and_grad(model, loss_fn)(model, tokens, targets)
        mx.eval(lv, grads)
        assert lv.item() == lv.item(), f"{mode}: NaN loss"

        # ternary FFN linears received gradient on the shadow weight
        gw = grads["blocks"][0]["ffn"]["gate_proj"]["weight"]
        mx.eval(gw)
        gwn = float(mx.sqrt((gw * gw).sum()).item())
        assert gwn > 0.0, f"{mode}: no gradient to FFN shadow weight"

        # anneal + instrument populate
        anneal_all(mods, step=1, total_steps=100)
        snap = observe_all(mods)
        stats = ternary_stats_all(mods)
        s0 = next(iter(stats.values()))
        print(f"{mode}: loss {lv.item():.4f}, {len(mods)} mods, "
              f"grad→shadow {gwn:.4f}, sparsity {s0['sparsity']:.2f}, "
              f"snap_keys {sorted(snap)} ✓")

    print("\nmicro_ternary.py: smoke test passed ✓")
