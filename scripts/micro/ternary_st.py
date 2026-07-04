"""Dual-mode ternary linear for the micro bench — TD vs ST on one substrate.

Two from-scratch ternary-training paradigms behind ONE interface, so Arm 0
(reproduce the flip-flop) and Arm 1 (does CAT-Q relaxation hide it?) run off
the same module (λ one_way / λ compose — no fork):

  mode="td"  — verbum TernaryDescent style. Hard ternary in the forward pass,
               straight-through identity backward to a LATENT float32 shadow
               weight trained by Adam. The sign flips when the shadow crosses
               ±Δ. This is the paradigm that oscillated: two input contexts
               pull the shadow across Δ in opposite directions and the sign
               never commits (holographic overloading — s257).

  mode="st"  — CAT-Q Softened Ternarization. A differentiable transition
               f(w) = ½(tanh(s·(w−Δ)) + tanh(s·(w+Δ))) with sharpness s
               annealed over training (soft → hard). Early: real gradients
               everywhere (the shadow can sit fractional, temporarily
               RESTORING the holographic capacity a float weight has). Late:
               set_hard() switches to a straight-through hard step whose
               backward uses the soft surrogate. The prediction under test:
               ST converges by HIDING the overload in the fractional phase,
               then forces a lossy projection at hardening.

Both carry the two registers as first-class LEARNED parameters (CAT-Q learns
α and Δ separately; verbum measured sign=routing / magnitude=value):

  α  (log_alpha, per output channel) — the MAGNITUDE / value register.
  Δ  (delta_ratio·α, per output channel) — the THRESHOLD / routing register:
     which shadow weights become ±1 vs collapse to 0.

The per-weight sign-demand instrument (flip counting + hard-sign snapshots)
lives here; the CATEGORY-conditioned accumulation lives in the training
script (unbraided — λ simplify).

License: MIT.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import mlx.core as mx
import mlx.nn as nn

# ══════════════════════════════════════════════════════════════════════
# Ternary primitives
# ══════════════════════════════════════════════════════════════════════


def hard_ternary(w: mx.array, delta: mx.array) -> mx.array:
    """Hard ternarization Q(w; Δ) → {-1, 0, +1} (CAT-Q Eq. 2).

    w:     (..., ) float shadow weights
    delta: broadcastable threshold > 0
    """
    pos = (w > delta).astype(w.dtype)
    neg = (w < -delta).astype(w.dtype)
    return pos - neg


def soft_ternary(w: mx.array, delta: mx.array, sharpness: float) -> mx.array:
    """Differentiable soft ternarization (CAT-Q ST transition f(·)).

    f(w) = ½·(tanh(s·(w−Δ)) + tanh(s·(w+Δ)))

    As s→∞:  w>Δ → +1,  |w|≤Δ → 0,  w<−Δ → −1  (recovers hard_ternary).
    For finite s it is smooth with the largest gradient in the transition
    band around ±Δ — which pushes shadow weights OUT of the dead zone toward
    the {−α, 0, +α} basins.
    """
    s = sharpness
    return 0.5 * (mx.tanh(s * (w - delta)) + mx.tanh(s * (w + delta)))


# ══════════════════════════════════════════════════════════════════════
# Config
# ══════════════════════════════════════════════════════════════════════


@dataclass
class TernaryConfig:
    """Per-layer ternary settings (defaults chosen for the micro bench)."""

    mode: str = "st"            # "td" | "st"
    sharpness_start: float = 2.0   # ST: soft at the start
    sharpness_end: float = 40.0    # ST: near-hard by the anneal end
    anneal_frac: float = 0.6       # ST: fraction of training spent annealing (γ)
    delta_ratio_init: float = 0.5  # Δ₀ = 0.5·α  (BitNet absmean default)
    learn_delta: bool = True       # ST learns Δ; TD keeps it structural


# ══════════════════════════════════════════════════════════════════════
# Dual-mode ternary linear
# ══════════════════════════════════════════════════════════════════════


class TernaryShadowLinear(nn.Module):
    """Ternary linear with a latent float shadow weight. Drop-in for nn.Linear.

    Forward computes  y = x @ (α · T)ᵀ  with no bias, where T is the ternary
    topology derived from the shadow weight and α is the per-channel scale.

    Registers (both learned):
        weight       (out, in)  float32  — the latent shadow (routing lives in
                                           its SIGN relative to ±Δ)
        log_alpha    (out,)      float32  — log magnitude scale α (value register)
        delta_ratio  (out,)      float32  — Δ = delta_ratio · α (routing threshold)

    Staging (ST only):
        set_sharpness(s)  — raise s over training (soft → hard)
        set_hard(True)    — second stage: straight-through hard step
    """

    def __init__(
        self,
        in_features: int,
        out_features: int,
        cfg: TernaryConfig | None = None,
    ):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.cfg = cfg or TernaryConfig()
        self.mode = self.cfg.mode

        # Latent float shadow — Kaiming normal (same init as v15 _ternary_init).
        std = math.sqrt(2.0 / in_features)
        self.weight = mx.random.normal((out_features, in_features)) * std

        # α (value register): init to per-channel absmean, learned in log space
        # so it stays positive under Adam.
        absmean = mx.abs(self.weight).mean(axis=-1)  # (out,)
        self.log_alpha = mx.log(absmean + 1e-6)

        # Δ (routing register): Δ = delta_ratio · α. Learnable in ST, frozen in TD.
        self.delta_ratio = mx.full((out_features,), self.cfg.delta_ratio_init)
        if not (self.cfg.learn_delta and self.mode == "st"):
            self.freeze(keys=["delta_ratio"])

        # Runtime ST state (not parameters — plain attributes).
        self._sharpness = self.cfg.sharpness_start
        self._hard = False

        # Instrument state (stop-gradient snapshots, not parameters).
        self._prev_signs: mx.array | None = None
        self._flip_count = mx.zeros((out_features, in_features), dtype=mx.int32)
        self._steps_seen = 0

    # ── ST staging ────────────────────────────────────────────────────

    def set_sharpness(self, s: float) -> None:
        self._sharpness = float(s)

    def set_hard(self, hard: bool) -> None:
        self._hard = bool(hard)

    def anneal(self, step: int, total_steps: int) -> None:
        """ST curriculum: raise sharpness over `anneal_frac`, then go hard.

        No-op for TD (which is always hard).
        """
        if self.mode != "st":
            return
        c = self.cfg
        gamma = max(1e-6, c.anneal_frac)
        t = step / max(1, total_steps)
        if t <= gamma:
            frac = t / gamma
            s = c.sharpness_start + (c.sharpness_end - c.sharpness_start) * frac
            self.set_sharpness(s)
            self.set_hard(False)
        else:
            self.set_sharpness(c.sharpness_end)
            self.set_hard(True)

    # ── Effective ternary weight ──────────────────────────────────────

    def _alpha_delta(self) -> tuple[mx.array, mx.array]:
        alpha = mx.exp(self.log_alpha).reshape(-1, 1)          # (out, 1)
        delta = self.delta_ratio.reshape(-1, 1) * alpha         # (out, 1)
        return alpha, delta

    def effective_weight(self) -> mx.array:
        """α · T  with the gradient path appropriate to the mode."""
        alpha, delta = self._alpha_delta()
        w = self.weight

        if self.mode == "td":
            # Straight-through identity: forward hard, backward d/dw = 1.
            t_hard = hard_ternary(w, delta)
            t = mx.stop_gradient(t_hard - w) + w
            return alpha * t

        # ST mode.
        t_soft = soft_ternary(w, delta, self._sharpness)
        if self._hard:
            # Second stage: forward hard, backward through the soft surrogate.
            t_hard = hard_ternary(w, delta)
            t = mx.stop_gradient(t_hard - t_soft) + t_soft
        else:
            t = t_soft
        return alpha * t

    def __call__(self, x: mx.array) -> mx.array:
        w_eff = self.effective_weight()          # (out, in)
        return x @ w_eff.T

    # ── Instrument ────────────────────────────────────────────────────

    def hard_signs(self) -> mx.array:
        """Current committed ternary topology {-1,0,+1} (stop-gradient)."""
        _, delta = self._alpha_delta()
        return mx.stop_gradient(hard_ternary(self.weight, delta))

    def observe_flips(self) -> dict[str, float]:
        """Update flip counters vs the previous snapshot; return live stats.

        Call once per training step AFTER the optimizer update. Detects the
        oscillation: positions whose committed sign changed since last step.
        """
        signs = self.hard_signs().astype(mx.int32)
        mx.eval(signs)
        stats: dict[str, float] = {}
        if self._prev_signs is not None:
            flipped = (signs != self._prev_signs).astype(mx.int32)
            self._flip_count = self._flip_count + flipped
            n = signs.size
            stats["flipped_this_step"] = float(flipped.sum().item()) / n
        self._prev_signs = signs
        self._steps_seen += 1

        total = signs.size
        stats["frac_zero"] = float((signs == 0).sum().item()) / total
        stats["frac_pos"] = float((signs == 1).sum().item()) / total
        stats["frac_neg"] = float((signs == -1).sum().item()) / total
        return stats

    def flip_summary(self) -> dict[str, float]:
        """Aggregate oscillation over the run (call at the end)."""
        fc = self._flip_count
        mx.eval(fc)
        total = fc.size
        steps = max(1, self._steps_seen - 1)
        # A weight that "oscillates" flips repeatedly, not just once (a single
        # flip = a legitimate one-time commit; many flips = irreconcilable).
        oscillating = (fc >= 3).astype(mx.int32)
        return {
            "mean_flips_per_weight": float(fc.sum().item()) / total,
            "frac_oscillating": float(oscillating.sum().item()) / total,
            "max_flips": float(fc.max().item()),
            "flip_rate": float(fc.sum().item()) / (total * steps),
        }

    def ternary_stats(self) -> dict[str, float]:
        signs = self.hard_signs()
        alpha = mx.exp(self.log_alpha)
        mx.eval(signs, alpha)
        total = signs.size
        return {
            "sparsity": float((signs == 0).sum().item()) / total,
            "pos_frac": float((signs == 1).sum().item()) / total,
            "neg_frac": float((signs == -1).sum().item()) / total,
            "alpha_mean": float(alpha.mean().item()),
            "delta_ratio_mean": float(self.delta_ratio.mean().item()),
        }


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("ternary_st.py self-test")
    print("=" * 60)

    mx.random.seed(0)
    B, IN, OUT = 4, 32, 16
    x = mx.random.normal((B, IN))

    # ── Ternary primitives ──
    w = mx.array([-0.8, -0.1, 0.05, 0.3, 0.9])
    d = mx.array(0.2)
    ht = hard_ternary(w, d)
    assert ht.tolist() == [-1.0, 0.0, 0.0, 1.0, 1.0], ht.tolist()
    st_sharp = soft_ternary(w, d, 100.0)
    # near-hard at high sharpness
    assert mx.allclose(st_sharp, ht, atol=1e-2), (st_sharp.tolist(), ht.tolist())
    print("primitives: hard + soft(s=100)≈hard ✓")

    # ── TD mode: forward shape + gradient reaches shadow & alpha ──
    td = TernaryShadowLinear(IN, OUT, TernaryConfig(mode="td"))
    mx.eval(td.parameters())

    def td_loss(m, x):
        return (m(x) ** 2).mean()

    lv, grads = nn.value_and_grad(td, td_loss)(td, x)
    mx.eval(lv, grads)
    gw = grads["weight"]
    ga = grads["log_alpha"]
    mx.eval(gw, ga)
    assert gw.shape == (OUT, IN)
    gwn = float(mx.sqrt((gw * gw).sum()).item())
    gan = float(mx.sqrt((ga * ga).sum()).item())
    assert gwn > 0.0, "TD: no gradient to shadow weight (STE broken)"
    assert gan > 0.0, "TD: no gradient to alpha"
    print(f"TD: forward {td(x).shape}, grad→shadow {gwn:.4f}, grad→alpha {gan:.4f} ✓")

    # ── ST mode: gradient reaches shadow, alpha, AND delta (soft phase) ──
    st = TernaryShadowLinear(IN, OUT, TernaryConfig(mode="st"))
    st.set_hard(False)
    st.set_sharpness(3.0)
    mx.eval(st.parameters())

    def st_loss(m, x):
        return (m(x) ** 2).mean()

    lv2, grads2 = nn.value_and_grad(st, st_loss)(st, x)
    mx.eval(lv2, grads2)
    gd = grads2["delta_ratio"]
    mx.eval(gd)
    gdn = float(mx.sqrt((gd * gd).sum()).item())
    assert gdn > 0.0, "ST(soft): no gradient to delta_ratio"
    print(f"ST(soft): grad→delta_ratio {gdn:.4f} ✓ (learnable threshold)")

    # ── ST hard-stage STE still passes gradient to shadow ──
    st.set_hard(True)
    st.set_sharpness(40.0)
    lv3, grads3 = nn.value_and_grad(st, st_loss)(st, x)
    mx.eval(lv3, grads3)
    gw3 = grads3["weight"]
    mx.eval(gw3)
    assert float(mx.sqrt((gw3 * gw3).sum()).item()) > 0.0, "ST(hard): STE broken"
    print("ST(hard): straight-through gradient to shadow ✓")

    # ── Anneal schedule sanity ──
    st2 = TernaryShadowLinear(IN, OUT, TernaryConfig(mode="st",
                                                     sharpness_start=2.0,
                                                     sharpness_end=40.0,
                                                     anneal_frac=0.6))
    st2.anneal(0, 100)
    assert abs(st2._sharpness - 2.0) < 1e-6 and not st2._hard
    st2.anneal(30, 100)  # halfway through the 0.6 anneal window
    assert 2.0 < st2._sharpness < 40.0 and not st2._hard
    st2.anneal(80, 100)  # past γ → hard
    assert st2._hard and abs(st2._sharpness - 40.0) < 1e-6
    print("anneal: soft→hard staging ✓")

    # ── Instrument: flips register when the shadow crosses ±Δ ──
    tl = TernaryShadowLinear(IN, OUT, TernaryConfig(mode="td"))
    tl.observe_flips()  # snapshot 1
    # Force some shadow weights across the threshold.
    tl.weight = tl.weight + 5.0
    s1 = tl.observe_flips()
    assert s1["flipped_this_step"] > 0.0, "instrument: flips not detected"
    summ = tl.flip_summary()
    print(f"instrument: flipped {s1['flipped_this_step']:.2f}, "
          f"summary keys {sorted(summ)} ✓")

    print("\nternary_st.py: all tests passed ✓")
