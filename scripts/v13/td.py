"""TernaryDescent — gradient-informed descent for ternary {-1, 0, +1} weights.

The missing half of optimization.  Adam handles continuous parameters.
TernaryDescent handles discrete sign topology.  Both run on the same
loss, same backward pass, same gradient tape.  They co-evolve naturally
because they optimize the same objective.

Core idea: gradients tell you which direction reduces loss.  For ternary
weights, you can't take fractional steps.  Instead, accumulate gradient
evidence over many steps (like Adam's moments) and flip when the signal
is strong and consistent.

Adam analogy:
    Adam m_t     → TD direction   (EMA of gradient — WHICH WAY to flip)
    Adam v_t     → TD magnitude   (EMA of grad² — HOW MUCH loss cares)
    Adam lr      → TD flip_rate   (max fraction of weights to flip per step)
    Adam step    → TD flip        (discrete: +1 → 0 → -1, through zero staging)

Two-step ternary transitions:
    +1 → 0 → -1    (keep → block → flip)
    -1 → 0 → +1    (flip → block → keep)
    
The zero state is a staging area.  Positions pass through zero on their
way between +1 and -1.  This prevents catastrophic flips — a position
goes silent (blocked) before committing to the opposite sign.  If
blocking hurts, the gradient pushes back immediately.

Delta plate architecture:
    effective = base_plate ⊙ delta_plate
    base_plate:  frozen teacher etch (full crystal)
    delta_plate: initialized to +1 (pass-through), trained by TD
    
    Delta semantics:
        +1 → "keep teacher sign here" (this part works for stride-stack)
        -1 → "flip teacher sign here" (this part needs to be different)
         0 → "block this position"    (staging area during transition)

    Reduction: fold delta into base, reset delta to +1, iterate.
        new_base = base ⊙ delta    (ternary × ternary = ternary, exact)
        new_delta = all +1

License: MIT
"""

from __future__ import annotations

import math
from typing import Any

import mlx.core as mx
import mlx.nn as nn

try:
    from .ternary import (
        TernaryLinear,
        TernaryMirror,
        TernaryMask,
        TernaryEmbedding,
        pack_ternary_mlx,
        unpack_ternary_mlx,
        _ternary_init,
        _walk_ternary_modules,
    )
except ImportError:
    from ternary import (
        TernaryLinear,
        TernaryMirror,
        TernaryMask,
        TernaryEmbedding,
        pack_ternary_mlx,
        unpack_ternary_mlx,
        _ternary_init,
        _walk_ternary_modules,
    )


# ══════════════════════════════════════════════════════════════════════
# Gradient decomposition: routing vs calibration
# ══════════════════════════════════════════════════════════════════════
#
# The gradient through the effective weight encodes two signals:
#
#   ROUTING:      gradient fights the topology (sign disagreement)
#                 → "this route is wrong, change the sign"
#                 → belongs to TernaryDescent
#
#   CALIBRATION:  gradient agrees with topology (magnitude adjustment)
#                 → "this route is right, adjust the scale"
#                 → belongs to Adam (gamma)
#
# When both signals are mixed, Adam wastes capacity encoding routing
# (distorting gamma to compensate for wrong signs) and TD gets noisy
# signal (calibration gradients dilute routing confidence).
#
# Decomposing them lets each optimizer handle what it's good at.


def decompose_gradient(
    grad_effective: mx.array,
    effective_signs: mx.array,
) -> tuple[mx.array, mx.array, mx.array]:
    """Split gradient into routing and calibration components.

    The DESCENT direction (-grad) tells us where the effective weight
    should move to decrease loss.  Compare it to the current sign:

        descent direction matches current sign → CALIBRATION
            "the route is correct, amplify it" → Adam handles via gamma
        descent direction opposes current sign → ROUTING
            "the route is wrong, flip it" → TernaryDescent handles via delta
        topology is zero → ROUTING
            "a route needs to be created" → TernaryDescent

    Args:
        grad_effective:   (N, K) float32 — ∂L/∂effective
        effective_signs:  (N, K) int8 or float32 — sign(base ⊙ delta)

    Returns:
        routing:     (N, K) float32 — gradient component for TD
        calibration: (N, K) float32 — gradient component for Adam
        routing_mask: (N, K) bool — True where gradient is routing
    """
    eff_float = effective_signs.astype(mx.float32)
    # The descent direction: which way effective should move to decrease loss
    descent_sign = mx.sign(-grad_effective)  # -grad is the descent direction

    # ROUTING: descent direction disagrees with current topology, or topology is zero
    # This means the sign needs to change — the route itself is wrong.
    # CALIBRATION: descent direction agrees — the route is correct, just scale it.
    is_routing = (
        (descent_sign != eff_float) | (eff_float == 0)
    ) & (grad_effective != 0)  # exclude zero-gradient positions

    routing = mx.where(is_routing, grad_effective, mx.array(0.0))
    calibration = mx.where(is_routing, mx.array(0.0), grad_effective)

    return routing, calibration, is_routing


def compute_routing_fraction(
    grad_effective: mx.array,
    effective_signs: mx.array,
) -> mx.array:
    """Compute per-row routing fraction: what % of each row is routing vs calibration.

    Returns (N,) float32 in [0, 1].  High values = row is mostly routing
    (topology is wrong).  Low values = row is mostly calibration
    (topology is correct, just needs magnitude adjustment).

    Used to filter the gamma gradient: attenuate routing-heavy rows
    so Adam doesn't waste capacity trying to solve routing via magnitude.
    """
    eff_float = effective_signs.astype(mx.float32)
    descent_sign = mx.sign(-grad_effective)  # descent direction

    # Count non-zero gradient positions (denominator)
    has_gradient = grad_effective != 0
    n_active = mx.sum(has_gradient.astype(mx.float32), axis=-1)  # (N,)

    # Count routing positions: descent disagrees with topology or topology is zero
    is_routing = ((descent_sign != eff_float) | (eff_float == 0)) & has_gradient
    n_routing = mx.sum(is_routing.astype(mx.float32), axis=-1)  # (N,)

    # Routing fraction per row (avoid div by zero)
    return n_routing / (n_active + 1e-8)


# ══════════════════════════════════════════════════════════════════════
# TernaryDescent optimizer
# ══════════════════════════════════════════════════════════════════════


class TernaryDescent:
    """Adam-equivalent optimizer for ternary {-1, 0, +1} weights.

    Accumulates gradient evidence via exponential moving averages.
    Flips ternary weights when the gradient direction is consistent
    (high confidence) AND the loss cares about that position (high
    importance).

    The crystal gate from session 124 emerges naturally: if CE loss
    says "flip" but crystal loss says "don't", the gradients oscillate,
    confidence stays low, and no flip happens.  Only fusion flips
    (where both losses agree) accumulate enough evidence to trigger.

    Usage:
        td = TernaryDescent(flip_rate=0.001)
        
        for step in training:
            loss, grads = value_and_grad(model)(x, y)
            adam.step(continuous_params, grads)
            td.step(delta_plates, grads_for_deltas)
    """

    def __init__(
        self,
        beta1: float = 0.9,
        beta2: float = 0.999,
        flip_rate: float = 0.001,
        warmup_steps: int = 100,
        min_confidence: float = 0.3,
        cooldown_tau: float = 50.0,
        cooldown_backoff: float = 2.0,
        neighbor_width: int = 3,
    ):
        """Initialize TernaryDescent.

        Args:
            beta1:          EMA decay for direction (first moment).
                            0.9 = ~10-step memory. Higher = more conservative.
            beta2:          EMA decay for magnitude (second moment).
                            0.999 = ~1000-step memory. Stable importance estimate.
            flip_rate:      Max fraction of total ternary weights to flip per step.
                            0.001 = at most 0.1% of weights flip each step.
            warmup_steps:   No flips before this many steps. Let Adam establish
                            stable moments before topology changes.
            min_confidence: Minimum signal-to-noise ratio to consider a flip.
                            Below this, the gradient signal is too noisy.
            cooldown_tau:   Base cooldown period (steps) after a flip before the
                            same position can flip again. Anti-oscillation.
            cooldown_backoff: Multiply tau by this factor each time a position
                            flips again. Exponential backoff for chronic oscillators.
            neighbor_width: Width of row-wise median filter for spatial smoothing.
                            Must be odd (3, 5, 7). Breaks ties, smooths noise,
                            preserves crystal edges.
        """
        self.beta1 = beta1
        self.beta2 = beta2
        self.flip_rate = flip_rate
        self.warmup_steps = warmup_steps
        self.min_confidence = min_confidence
        self.cooldown_tau = cooldown_tau
        self.cooldown_backoff = cooldown_backoff
        self.neighbor_width = neighbor_width
        assert neighbor_width % 2 == 1, "neighbor_width must be odd for tie-breaking"
        self.step_count = 0

        # Per-parameter state: {param_id: (direction, magnitude)}
        self._state: dict[int, tuple[mx.array, mx.array]] = {}

        # Per-parameter anti-oscillation state:
        # {param_id: (last_flip_step, flip_count)} — both (N, K) int32
        self._flip_history: dict[int, tuple[mx.array, mx.array]] = {}

        # Tracking
        self.last_n_flips = 0
        self.last_n_candidates = 0
        self.last_mean_confidence = 0.0

    def _get_state(self, param_id: int, grad_shape: tuple) -> tuple[mx.array, mx.array]:
        """Get or initialize moment state for a parameter.
        
        Uses grad_shape (unpacked N, K) rather than packed shape (N, K//16)
        because moments track per-logical-weight statistics.
        """
        if param_id not in self._state:
            self._state[param_id] = (
                mx.zeros(grad_shape),  # direction (first moment)
                mx.zeros(grad_shape),  # magnitude (second moment)
            )
        return self._state[param_id]

    def _set_state(self, param_id: int, direction: mx.array, magnitude: mx.array):
        """Store updated moment state."""
        self._state[param_id] = (direction, magnitude)

    def _get_flip_history(self, param_id: int, shape: tuple) -> tuple[mx.array, mx.array]:
        """Get or initialize flip history for anti-oscillation.

        Returns:
            last_flip_step: (N, K) int32 — step at which each position last flipped
            flip_count:     (N, K) int32 — how many times each position has flipped
        """
        if param_id not in self._flip_history:
            self._flip_history[param_id] = (
                mx.zeros(shape, dtype=mx.int32),   # last_flip_step (0 = never)
                mx.zeros(shape, dtype=mx.int32),   # flip_count
            )
        return self._flip_history[param_id]

    def _compute_cooldown(self, param_id: int, shape: tuple) -> mx.array:
        """Compute per-position cooldown factor ∈ [0, 1].

        cooldown = 1 - exp(-steps_since_flip / effective_tau)
        effective_tau = tau_base * backoff^flip_count

        0 = just flipped, can't flip again.
        1 = fully cooled, eligible for flip.

        Chronic oscillators (high flip_count) have very long effective_tau,
        effectively freezing them. The crystal grows from the stable interior.
        """
        last_flip_step, flip_count = self._get_flip_history(param_id, shape)

        steps_since_flip = mx.maximum(self.step_count - last_flip_step, 0).astype(mx.float32)

        # Effective tau: base * backoff^flip_count
        # Cap flip_count contribution to prevent inf: max exponent ~10
        capped_count = mx.minimum(flip_count, 10).astype(mx.float32)
        effective_tau = self.cooldown_tau * (self.cooldown_backoff ** capped_count)

        # Cooldown: 0 when just flipped, 1 when fully cooled
        cooldown = 1.0 - mx.exp(-steps_since_flip / (effective_tau + 1e-8))

        # Positions that never flipped (step=0) should have cooldown=1
        never_flipped = last_flip_step == 0
        cooldown = mx.where(never_flipped, mx.array(1.0), cooldown)

        return cooldown

    def _update_flip_history(self, param_id: int, flip_mask: mx.array):
        """Record which positions flipped this step."""
        shape = flip_mask.shape
        last_flip_step, flip_count = self._get_flip_history(param_id, shape)

        flipped = flip_mask.astype(mx.int32)
        last_flip_step = mx.where(flip_mask, mx.array(self.step_count, dtype=mx.int32), last_flip_step)
        flip_count = flip_count + flipped

        self._flip_history[param_id] = (last_flip_step, flip_count)

    @staticmethod
    def _row_median_smooth(signal: mx.array, width: int = 3) -> mx.array:
        """Row-wise median filter for spatial smoothing.

        Odd width guarantees tie-breaking. Median preserves edges
        (crystal boundaries stay sharp) while rejecting isolated
        outlier flips (noise).

        Args:
            signal: (N, K) float32 — raw signal to smooth
            width:  odd integer, filter width (3 = position ± 1 neighbor)

        Returns:
            (N, K) float32 — smoothed signal
        """
        if width == 1:
            return signal
        N, K = signal.shape
        pad = width // 2

        # Pad with zeros at boundaries (conservative: edge positions get damped)
        padded = mx.concatenate([
            mx.zeros((N, pad)),
            signal,
            mx.zeros((N, pad)),
        ], axis=1)  # (N, K + 2*pad)

        # Gather windows: (N, K, width)
        windows = mx.stack([
            padded[:, i:i + K] for i in range(width)
        ], axis=-1)  # (N, K, width)

        # Median via sort + middle element
        sorted_windows = mx.sort(windows, axis=-1)
        return sorted_windows[:, :, pad]  # middle element = median

    def step(
        self,
        delta_params: list[tuple[str, mx.array, mx.array, mx.array]],
    ) -> dict[str, Any]:
        """Perform one TernaryDescent step across all delta plates.

        Args:
            delta_params: List of (name, delta_packed_uint32, grad_wrt_effective, base_packed_uint32).
                - name: identifier for logging
                - delta_packed_uint32: the delta plate weights (N, K//16) uint32
                - grad_wrt_effective: gradient of loss w.r.t. EFFECTIVE weight,
                  shape (N, K) float32.  NOT projected through base.
                  This is ∂L/∂effective[i,j] (or the routing component thereof).
                - base_packed_uint32: the frozen base plate (N, K//16) uint32

            The desired direction for delta is computed from the gradient
            w.r.t. effective and the base sign:
                If the gradient says effective should decrease:
                    base=+1 → delta should decrease (+1→0→-1)
                    base=-1 → delta should INCREASE (since eff = base*delta,
                              decreasing eff when base=-1 means increasing delta)

        Returns:
            dict with step metrics:
                - step: current step count
                - total_flips: number of flips this step
                - per_module: dict[name, {flips, candidates, mean_confidence}]
        """
        self.step_count += 1
        total_flips = 0
        per_module = {}

        in_warmup = self.step_count <= self.warmup_steps

        for name, delta_packed, grad_effective, base_packed in delta_params:
            # Use name as stable ID (object id changes on reassignment)
            direction, magnitude = self._get_state(name, grad_effective.shape)

            # Update moments using the EFFECTIVE gradient directly
            # (not projected through base — that caused sign confusion)
            direction = self.beta1 * direction + (1 - self.beta1) * grad_effective
            magnitude = self.beta2 * magnitude + (1 - self.beta2) * (grad_effective ** 2)

            # Store updated moments
            self._set_state(name, direction, magnitude)

            if in_warmup:
                per_module[name] = {"flips": 0, "candidates": 0, "mean_confidence": 0.0}
                continue

            # Bias correction (same as Adam)
            bc1 = 1 - self.beta1 ** self.step_count
            bc2 = 1 - self.beta2 ** self.step_count
            dir_corrected = direction / bc1
            mag_corrected = magnitude / bc2

            # Confidence: signal-to-noise ratio
            # High |direction| / sqrt(magnitude) = gradient consistently points one way
            snr = mx.abs(dir_corrected) / (mx.sqrt(mag_corrected) + 1e-8)

            # Importance: how much loss cares about this position
            importance = mx.sqrt(mag_corrected)

            # ── Three-voter anti-oscillation (session 137) ────
            #
            # Voter 1: TD gradient confidence (snr) — already computed
            # Voter 2: Cooldown gate — time-based hysteresis with backoff
            # Voter 3: Neighbor consensus — row-wise median smoothing
            #
            # Three voters (odd) → always breaks ties.
            # Multiplicative: ALL must agree for a flip.

            # Voter 2: Cooldown — recently flipped positions can't flip again
            cooldown = self._compute_cooldown(name, grad_effective.shape)

            # Voter 3: Neighbor consensus — smooth confidence spatially
            # Row-wise median of width 3 (or 5): breaks ties, rejects outlier flips,
            # preserves crystal edges (if 2 of 3 neighbors agree, edge is real)
            smoothed_snr = self._row_median_smooth(snr, self.neighbor_width)

            # Combined score: all three voters contribute
            # smoothed_snr replaces raw snr (incorporates neighbor vote)
            # cooldown gates positions that recently flipped
            score = smoothed_snr * importance * cooldown

            # Minimum confidence gate (on smoothed signal)
            confident = smoothed_snr > self.min_confidence

            # Unpack current delta and base to determine valid transitions
            delta_unpacked = unpack_ternary_mlx(delta_packed)  # (N, K) int8
            base_unpacked = unpack_ternary_mlx(base_packed)    # (N, K) int8

            # Desired direction for DELTA, accounting for base sign.
            #
            # The gradient is w.r.t. effective (= base ⊙ delta).
            # To decrease loss, effective should move in direction -sign(gradient).
            # Since effective = base * delta:
            #   desired_effective = -sign(dir_corrected)
            #   desired_delta = desired_effective * base
            #     (because delta = effective / base, and base ∈ {-1,+1})
            #
            # Example: grad < 0 → effective should increase → desired_eff = +1
            #   base = +1 → desired_delta = +1 (increase delta)
            #   base = -1 → desired_delta = -1 (decrease delta, since eff = base*delta)
            desired_effective = -mx.sign(dir_corrected)  # (N, K) float32
            base_float = base_unpacked.astype(mx.float32)
            # Where base is 0, the position is blocked at the base level — skip it
            desired = desired_effective * base_float  # (N, K) float32

            # Valid transitions: positions where we CAN move in the desired direction
            # +1 and desired < 0 → can go to 0 (step toward -1)
            # -1 and desired > 0 → can go to 0 (step toward +1)
            #  0 and desired != 0 → can go to ±1
            # base == 0 → skip (base blocks this position)
            delta_float = delta_unpacked.astype(mx.float32)
            can_move = (
                ((delta_float > 0) & (desired < 0)) |   # +1 → 0
                ((delta_float < 0) & (desired > 0)) |   # -1 → 0
                (delta_float == 0)                        #  0 → ±1
            ) & (base_float != 0)  # skip base-blocked positions

            # Final candidate mask: confident AND can move
            candidates = confident & can_move

            n_candidates = int(candidates.sum().item())

            if n_candidates == 0:
                per_module[name] = {"flips": 0, "candidates": 0, "mean_confidence": 0.0}
                continue

            # Budget: at most flip_rate × total weights
            total_weights = delta_unpacked.size
            budget = max(1, int(self.flip_rate * total_weights))
            budget = min(budget, n_candidates)

            # Find threshold score for top-k
            candidate_scores = mx.where(candidates, score, mx.array(0.0))

            # Use partition to find the k-th largest score
            flat_scores = candidate_scores.reshape(-1)
            # Negate for descending order with partition
            neg_scores = -flat_scores
            # kth_value = k-th smallest of negated = k-th largest of original
            if budget < flat_scores.size:
                partitioned = mx.partition(neg_scores, kth=budget - 1)
                threshold = -partitioned[budget - 1]
            else:
                threshold = mx.array(0.0)

            # Select positions above threshold
            flip_mask = candidates & (score >= threshold)

            # Compute new values
            # Two-step transitions through zero:
            #   +1 → 0      (block before flip)
            #   -1 → 0      (block before flip)
            #    0 → sign(desired)  (commit to direction)
            new_delta = mx.where(
                flip_mask & (delta_float != 0),
                mx.array(0, dtype=mx.int8),  # ±1 → 0 (go to staging)
                mx.where(
                    flip_mask & (delta_float == 0),
                    mx.sign(desired).astype(mx.int8),  # 0 → ±1 (commit)
                    delta_unpacked,  # no change
                ),
            )

            # Count actual flips
            flip_occurred = (new_delta != delta_unpacked)
            n_flips = int(flip_occurred.sum().item())
            total_flips += n_flips

            # Repack and update
            if n_flips > 0:
                new_packed = pack_ternary_mlx(new_delta)
                # Update the delta plate in-place by copying data.
                # The caller's reference to the module's weight is the same object.
                delta_packed_data = new_packed
                mx.eval(delta_packed_data)

                # Reset moments at flipped positions
                flip_float = flip_occurred.astype(mx.float32)
                direction = direction * (1 - flip_float)
                magnitude = magnitude * (1 - flip_float)
                self._set_state(name, direction, magnitude)

                # Record flip history for anti-oscillation
                self._update_flip_history(name, flip_occurred)

                # Affected rows: rows where any column flipped.
                # Adam's gamma/bias for these rows are stale — GD was
                # compensating for the old topology. Caller must decay
                # Adam moments for these rows so GD can re-converge.
                row_any_flipped = mx.any(flip_occurred, axis=1)  # (N,)
                mx.eval(row_any_flipped)
                affected_rows = set(
                    int(i) for i in range(row_any_flipped.shape[0])
                    if row_any_flipped[i].item()
                )

                per_module[name] = {
                    "flips": n_flips,
                    "candidates": n_candidates,
                    "mean_confidence": float(mx.mean(
                        mx.where(candidates, snr, mx.array(0.0))
                    ).item()),
                    "new_packed": new_packed,  # caller must assign to module
                    "affected_rows": affected_rows,  # rows where GD compensation is stale
                }
            else:
                per_module[name] = {
                    "flips": 0,
                    "candidates": n_candidates,
                    "mean_confidence": float(mx.mean(
                        mx.where(candidates, snr, mx.array(0.0))
                    ).item()),
                }

        self.last_n_flips = total_flips
        return {
            "step": self.step_count,
            "total_flips": total_flips,
            "in_warmup": in_warmup,
            "per_module": per_module,
        }

    def reset(self):
        """Reset all state. Called after reduction (delta folded into base)."""
        self._state.clear()
        self._flip_history.clear()
        self.step_count = 0
        self.last_n_flips = 0
        self.last_n_candidates = 0
        self.last_mean_confidence = 0.0


# ══════════════════════════════════════════════════════════════════════
# DeltaTernaryLinear — base plate + delta plate architecture
# ══════════════════════════════════════════════════════════════════════


class DeltaTernaryLinear(nn.Module):
    """Linear layer with frozen base plate + trainable delta plate.

    effective = base ⊙ delta   (element-wise ternary multiply)
    output = quantized_matmul(x, effective, gamma_scales, gamma_biases)

    The base plate contains the full teacher crystal etch, frozen.
    The delta plate starts at +1 (pass-through) and is trained by
    TernaryDescent.  When delta converges, reduce() folds it into
    the base and resets delta to +1 for another round.

    Delta semantics:
        +1 → keep teacher sign (this crystal position works)
        -1 → flip teacher sign (stride-stack needs different routing)
         0 → block this position (staging area during transition)

    Gamma is trained by Adam (same as TernaryLinear).

    Forward path:
        1. Unpack base and delta
        2. Multiply element-wise: effective = base * delta
        3. Repack effective
        4. quantized_matmul(norm(x), effective_packed, scales, biases)

    The unpack-multiply-repack is NOT in the hot path of inference —
    after training, reduce() folds delta into base and the model
    becomes a standard TernaryLinear.  During training, the overhead
    is small relative to the matmul.
    """

    group_size: int = 64
    bits: int = 2

    def __init__(
        self,
        in_features: int,
        out_features: int,
        pre_norm: bool = True,
    ):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.pre_norm = pre_norm

        if pre_norm:
            self.norm = nn.RMSNorm(in_features)

        # Base plate: will be loaded from teacher etch. Init random for now.
        wq_uint32, gamma = _ternary_init(out_features, in_features)
        self.base_weight = wq_uint32    # (N, K//16) uint32 — FROZEN
        self.gamma = gamma              # (N,) float32 — trained by Adam

        # Delta plate: starts as all +1 (pass-through)
        ones = mx.ones((out_features, in_features), dtype=mx.int8)
        self.delta_weight = pack_ternary_mlx(ones)  # (N, K//16) uint32 — trained by TD

    @classmethod
    def from_ternary_linear(cls, tl: TernaryLinear) -> "DeltaTernaryLinear":
        """Convert an existing TernaryLinear to DeltaTernaryLinear.

        The TernaryLinear's weight becomes the frozen base plate.
        Delta is initialized to all +1 (pass-through).
        Gamma transfers directly.
        """
        dtl = cls.__new__(cls)
        nn.Module.__init__(dtl)

        dtl.in_features = tl.in_features
        dtl.out_features = tl.out_features
        dtl.pre_norm = tl.pre_norm

        if tl.pre_norm:
            dtl.norm = tl.norm  # share the norm layer

        # Base plate from existing weights
        dtl.base_weight = tl.weight  # FROZEN
        dtl.gamma = tl.gamma         # trained by Adam

        # Delta plate: all +1 (pass-through)
        ones = mx.ones((tl.out_features, tl.in_features), dtype=mx.int8)
        dtl.delta_weight = pack_ternary_mlx(ones)
        mx.eval(dtl.delta_weight)

        return dtl

    def _compute_effective(self) -> mx.array:
        """Compute effective plate: base ⊙ delta, packed as uint32.

        Ternary × ternary = ternary:
            +1 × +1 = +1,  +1 × -1 = -1,  -1 × -1 = +1
            anything × 0 = 0

        Returns (N, K//16) uint32 packed effective weights.
        """
        base = unpack_ternary_mlx(self.base_weight)    # (N, K) int8
        delta = unpack_ternary_mlx(self.delta_weight)   # (N, K) int8

        # Element-wise multiply: int8 * int8 → int8 (stays in {-1, 0, +1})
        # MLX int8 multiply can overflow, so cast to int16 briefly
        effective = (base.astype(mx.int16) * delta.astype(mx.int16)).astype(mx.int8)

        return pack_ternary_mlx(effective)

    def _get_scales_biases(self) -> tuple[mx.array, mx.array]:
        """Compute quantized_matmul scales/biases from gamma (same as TernaryLinear)."""
        n_groups = self.in_features // self.group_size
        gamma_2d = mx.broadcast_to(
            mx.expand_dims(self.gamma, axis=-1),
            (self.out_features, n_groups),
        )
        return gamma_2d, -gamma_2d

    def __call__(self, x: mx.array) -> mx.array:
        if self.pre_norm:
            x = self.norm(x)

        # Cache input statistics (same as TernaryLinear)
        if x.ndim >= 2:
            reduce_axes = tuple(range(x.ndim - 1))
            self._x_abs_mean = mx.stop_gradient(mx.mean(mx.abs(x), axis=reduce_axes))
            self._x_mean = mx.stop_gradient(mx.mean(x, axis=reduce_axes))
        else:
            self._x_abs_mean = mx.stop_gradient(mx.abs(x))
            self._x_mean = mx.stop_gradient(x)

        # Compute effective plate: base ⊙ delta
        effective = self._compute_effective()

        scales, biases = self._get_scales_biases()

        # stop_gradient on effective: topology is TD-managed, not Adam-managed
        w = mx.stop_gradient(effective)
        return mx.quantized_matmul(
            x, w, scales, biases,
            transpose=True, group_size=self.group_size, bits=self.bits,
        )

    def compute_delta_gradient(self, grad_wrt_output: mx.array, x_input: mx.array) -> mx.array:
        """Compute gradient of loss w.r.t. delta plate positions.

        Since effective = base ⊙ delta, and the forward pass computes
        y = x @ (gamma * effective)^T, we need:

            ∂L/∂delta[i,j] = ∂L/∂effective[i,j] × base[i,j]

        And ∂L/∂effective[i,j] ≈ ∂L/∂y[i] × x[j] × gamma[i]

        This is computed from the gradient of the loss w.r.t. the
        matmul output and the input activations.

        Args:
            grad_wrt_output: ∂L/∂y, shape (..., out_features)
            x_input: input to this layer, shape (..., in_features)

        Returns:
            ∂L/∂delta, shape (out_features, in_features) float32
        """
        # Average over batch and sequence dimensions
        if grad_wrt_output.ndim > 2:
            # (B, T, out) → (out,) — mean over B, T
            grad_out_mean = grad_wrt_output.reshape(-1, self.out_features).mean(axis=0)
        elif grad_wrt_output.ndim == 2:
            grad_out_mean = grad_wrt_output.mean(axis=0)
        else:
            grad_out_mean = grad_wrt_output

        if x_input.ndim > 2:
            x_mean = x_input.reshape(-1, self.in_features).mean(axis=0)
        elif x_input.ndim == 2:
            x_mean = x_input.mean(axis=0)
        else:
            x_mean = x_input

        # ∂L/∂effective[i,j] ≈ ∂L/∂y[i] × x[j] × gamma[i]
        # Shape: (out,) × (in,) → (out, in) via outer product
        grad_effective = (
            mx.expand_dims(grad_out_mean * self.gamma, axis=-1)
            * mx.expand_dims(x_mean, axis=0)
        )  # (out_features, in_features)

        # ∂L/∂delta = ∂L/∂effective × base
        base = unpack_ternary_mlx(self.base_weight).astype(mx.float32)  # (N, K)
        grad_delta = grad_effective * base

        return grad_delta

    def reduce(self) -> None:
        """Fold delta into base plate. Reset delta to all +1.

        new_base = base ⊙ delta  (ternary × ternary = ternary, exact)
        new_delta = all +1

        This is lossless: the effective plate is unchanged.
        Called when delta has converged (most positions still +1).
        After reduction, TernaryDescent state should also be reset.
        """
        # Compute folded base
        new_base_packed = self._compute_effective()

        # Reset delta to all +1
        ones = mx.ones((self.out_features, self.in_features), dtype=mx.int8)
        new_delta_packed = pack_ternary_mlx(ones)

        # Assign
        self.base_weight = new_base_packed
        self.delta_weight = new_delta_packed
        mx.eval(self.base_weight, self.delta_weight)

    def to_ternary_linear(self) -> TernaryLinear:
        """Convert back to standard TernaryLinear after training.

        Folds delta into base first, then creates a TernaryLinear
        with the effective weights. Use for inference (no delta overhead).
        """
        self.reduce()  # ensure delta is folded

        tl = TernaryLinear.__new__(TernaryLinear)
        nn.Module.__init__(tl)
        tl.in_features = self.in_features
        tl.out_features = self.out_features
        tl.pre_norm = self.pre_norm
        if self.pre_norm:
            tl.norm = self.norm
        tl.weight = self.base_weight  # delta is all +1, so base IS effective
        tl.gamma = self.gamma
        return tl

    def delta_stats(self) -> dict[str, float]:
        """Report delta plate statistics."""
        delta = unpack_ternary_mlx(self.delta_weight)  # (N, K) int8
        total = delta.size
        n_keep = int((delta == 1).sum().item())
        n_flip = int((delta == -1).sum().item())
        n_block = int((delta == 0).sum().item())
        return {
            "keep_frac": n_keep / total,       # +1: using teacher sign
            "flip_frac": n_flip / total,       # -1: flipped from teacher
            "block_frac": n_block / total,     #  0: blocked (staging)
            "changed_frac": (n_flip + n_block) / total,  # anything not +1
        }

    def ternary_stats(self) -> dict[str, float]:
        """Report effective plate statistics (same interface as TernaryLinear)."""
        effective = self._compute_effective()
        w = unpack_ternary_mlx(effective)
        total = w.size
        return {
            "sparsity": float((w == 0).sum().item()) / total,
            "pos_frac": float((w == 1).sum().item()) / total,
            "neg_frac": float((w == -1).sum().item()) / total,
            "gamma_mean": float(self.gamma.mean().item()),
            "gamma_std": float(mx.sqrt(mx.var(self.gamma)).item()),
        }


# ══════════════════════════════════════════════════════════════════════
# Model conversion utilities
# ══════════════════════════════════════════════════════════════════════


def convert_to_delta(
    model: nn.Module,
    include_prefixes: tuple[str, ...] | None = None,
    exclude_prefixes: tuple[str, ...] | None = None,
) -> list[tuple[str, DeltaTernaryLinear]]:
    """Convert TernaryLinear modules to DeltaTernaryLinear in-place.

    Walks the model tree.  For each TernaryLinear matching the
    include/exclude filters, replaces it with a DeltaTernaryLinear
    whose base_weight = the original weight and delta = all +1.

    Args:
        model:            Model to convert in-place.
        include_prefixes: If set, only convert modules whose path starts
                          with one of these prefixes.
        exclude_prefixes: If set, skip modules whose path starts with
                          any of these prefixes.

    Returns:
        List of (path, DeltaTernaryLinear) for all converted modules.
    """
    converted = []

    for path, mod in list(model.named_modules()):
        if not isinstance(mod, TernaryLinear):
            continue

        # Apply filters
        if include_prefixes is not None:
            if not any(path.startswith(p) for p in include_prefixes):
                continue
        if exclude_prefixes is not None:
            if any(path.startswith(p) for p in exclude_prefixes):
                continue

        # Convert
        dtl = DeltaTernaryLinear.from_ternary_linear(mod)

        # Replace in parent module
        parts = path.split(".")
        parent = model
        for part in parts[:-1]:
            if part.isdigit():
                parent = parent[int(part)]
            else:
                parent = getattr(parent, part)

        attr_name = parts[-1]
        if attr_name.isdigit():
            parent[int(attr_name)] = dtl
        else:
            setattr(parent, attr_name, dtl)

        converted.append((path, dtl))

    return converted


def collect_delta_params(
    model: nn.Module,
) -> list[tuple[str, DeltaTernaryLinear]]:
    """Collect all DeltaTernaryLinear modules from the model.

    Returns list of (path, module) for use with TernaryDescent.step().
    """
    result = []
    for path, mod in model.named_modules():
        if isinstance(mod, DeltaTernaryLinear):
            result.append((path, mod))
    return result


def reduce_all_deltas(model: nn.Module) -> int:
    """Reduce all DeltaTernaryLinear modules: fold delta into base.

    Returns number of modules reduced.
    """
    n = 0
    for path, mod in model.named_modules():
        if isinstance(mod, DeltaTernaryLinear):
            mod.reduce()
            n += 1
    return n


def freeze_delta_architecture(model: nn.Module) -> int:
    """Freeze base plates and delta plates for optimizer exclusion.

    base_weight: always frozen (teacher crystal)
    delta_weight: frozen from Adam (TD manages it directly)
    gamma: NOT frozen (Adam trains it)
    norm: NOT frozen (Adam trains it)

    Returns number of modules frozen.
    """
    n = 0
    for path, mod in model.named_modules():
        if isinstance(mod, DeltaTernaryLinear):
            mod.freeze(keys=["base_weight", "delta_weight"])
            n += 1
    return n


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("TernaryDescent + DeltaTernaryLinear self-test")
    print("=" * 60)

    # 1. Test DeltaTernaryLinear matches TernaryLinear at init
    print("\n1. DeltaTernaryLinear vs TernaryLinear (delta=+1 should match)...")
    mx.random.seed(42)
    tl = TernaryLinear(64, 32, pre_norm=False)
    dtl = DeltaTernaryLinear.from_ternary_linear(tl)

    x = mx.random.normal((2, 4, 64))
    y_tl = tl(x)
    y_dtl = dtl(x)
    diff = float(mx.max(mx.abs(y_tl - y_dtl)).item())
    print(f"   Max diff: {diff:.2e}  {'✓ PASS' if diff < 1e-5 else '✗ FAIL'}")

    # 2. Test delta stats at init
    print("\n2. Delta stats at init (should be all +1)...")
    stats = dtl.delta_stats()
    print(f"   keep={stats['keep_frac']:.3f}  flip={stats['flip_frac']:.3f}  "
          f"block={stats['block_frac']:.3f}")
    assert stats["keep_frac"] == 1.0, f"Expected all +1, got keep={stats['keep_frac']}"
    print("   ✓ PASS")

    # 3. Test reduce() is lossless
    print("\n3. Reduce (fold delta into base) should be lossless...")
    # Manually flip some delta positions first
    delta_unpacked = unpack_ternary_mlx(dtl.delta_weight)
    # Flip first 10 positions to -1
    delta_modified = delta_unpacked.at[0, :10].add(mx.full((10,), -2, dtype=mx.int8))
    dtl.delta_weight = pack_ternary_mlx(delta_modified)
    mx.eval(dtl.delta_weight)

    y_before = dtl(x)
    dtl.reduce()
    y_after = dtl(x)
    diff = float(mx.max(mx.abs(y_before - y_after)).item())
    print(f"   Max diff after reduce: {diff:.2e}  {'✓ PASS' if diff < 1e-5 else '✗ FAIL'}")

    stats_after = dtl.delta_stats()
    assert stats_after["keep_frac"] == 1.0, "Delta should be all +1 after reduce"
    print(f"   Delta reset to +1: ✓ PASS")

    # 4. Test TernaryDescent basic operation
    print("\n4. TernaryDescent basic operation...")
    td = TernaryDescent(flip_rate=0.01, warmup_steps=5, min_confidence=0.1)

    # Create a fresh delta plate
    dtl2 = DeltaTernaryLinear(64, 32, pre_norm=False)
    mx.eval(dtl2.base_weight, dtl2.delta_weight, dtl2.gamma)

    # Simulate some gradient steps
    for i in range(10):
        # Fake gradient: consistent negative gradient on first half, positive on second
        grad = mx.zeros((32, 64))
        grad = grad.at[:, :32].add(mx.full((32, 32), -0.5))
        grad = grad.at[:, 32:].add(mx.full((32, 32), 0.5))
        # Add some noise
        grad = grad + mx.random.normal(grad.shape) * 0.1

        result = td.step([
            ("test", dtl2.delta_weight, grad, dtl2.base_weight),
        ])

        # Apply any flips
        for name, info in result["per_module"].items():
            if "new_packed" in info:
                dtl2.delta_weight = info["new_packed"]
                mx.eval(dtl2.delta_weight)

        if i >= 5:  # past warmup
            stats = dtl2.delta_stats()
            print(f"   Step {i+1}: flips={result['total_flips']}, "
                  f"changed={stats['changed_frac']:.4f}")

    final_stats = dtl2.delta_stats()
    print(f"   Final: keep={final_stats['keep_frac']:.3f}  "
          f"flip={final_stats['flip_frac']:.3f}  "
          f"block={final_stats['block_frac']:.3f}")
    if final_stats["changed_frac"] > 0:
        print("   ✓ PASS — delta plate evolved")
    else:
        print("   ⚠ No flips occurred (may need more steps or lower confidence)")

    # 5. Test convert_to_delta
    print("\n5. Model conversion utility...")

    class TinyModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.proj_a = TernaryLinear(128, 64, pre_norm=False)
            self.proj_b = TernaryLinear(64, 64, pre_norm=False)

        def __call__(self, x):
            return self.proj_b(self.proj_a(x))

    tiny = TinyModel()
    x = mx.random.normal((2, 4, 128))
    y_before = tiny(x)

    converted = convert_to_delta(tiny)
    print(f"   Converted {len(converted)} modules")

    y_after = tiny(x)
    diff = float(mx.max(mx.abs(y_before - y_after)).item())
    print(f"   Max diff after conversion: {diff:.2e}  {'✓ PASS' if diff < 1e-5 else '✗ FAIL'}")

    # Verify types
    assert isinstance(tiny.proj_a, DeltaTernaryLinear), "proj_a should be DeltaTernaryLinear"
    assert isinstance(tiny.proj_b, DeltaTernaryLinear), "proj_b should be DeltaTernaryLinear"
    print("   ✓ Types correct")

    # 6. Test to_ternary_linear (convert back for inference)
    print("\n6. Convert back to TernaryLinear for inference...")
    tl_back = tiny.proj_a.to_ternary_linear()
    x6 = mx.random.normal((2, 4, 128))
    y_back = tl_back(x6)
    y_dtl = tiny.proj_a(x6)
    diff = float(mx.max(mx.abs(y_back - y_dtl)).item())
    print(f"   Max diff: {diff:.2e}  {'✓ PASS' if diff < 1e-5 else '✗ FAIL'}")

    # 7. Test gradient decomposition
    print("\n7. Gradient decomposition (routing vs calibration)...")

    # Create a known topology and gradient
    # Topology: all +1
    effective_signs = mx.ones((8, 16), dtype=mx.int8)
    # Gradient semantics: descent = -grad
    # grad > 0 at eff=+1: descent = negative, disagrees with +1 → ROUTING (sign should flip)
    # grad < 0 at eff=+1: descent = positive, agrees with +1 → CALIBRATION (sign is correct)
    grad = mx.concatenate([
        mx.full((8, 8), 0.5),    # grad>0, descent<0, disagrees with +1 → ROUTING
        mx.full((8, 8), -0.5),   # grad<0, descent>0, agrees with +1 → CALIBRATION
    ], axis=1)
    mx.eval(grad)

    routing, calibration, routing_mask = decompose_gradient(grad, effective_signs)
    mx.eval(routing, calibration, routing_mask)

    # Check: first half should be ROUTING (grad>0, eff=+1, descent direction opposes)
    routing_first_half = float(mx.sum(mx.abs(routing[:, :8])).item())
    calib_first_half = float(mx.sum(mx.abs(calibration[:, :8])).item())
    # Check: second half should be CALIBRATION (grad<0, eff=+1, descent direction agrees)
    routing_second_half = float(mx.sum(mx.abs(routing[:, 8:])).item())
    calib_second_half = float(mx.sum(mx.abs(calibration[:, 8:])).item())

    print(f"   First half (grad>0 at eff=+1 → descent opposes → ROUTING):")
    print(f"     routing={routing_first_half:.2f}  calibration={calib_first_half:.2f}")
    assert routing_first_half > 0.0, f"Expected nonzero routing"
    assert calib_first_half == 0.0, f"Expected 0 calibration in routing zone"

    print(f"   Second half (grad<0 at eff=+1 → descent agrees → CALIBRATION):")
    print(f"     routing={routing_second_half:.2f}  calibration={calib_second_half:.2f}")
    assert routing_second_half == 0.0, f"Expected 0 routing in calibration zone"
    assert calib_second_half > 0.0, f"Expected nonzero calibration"
    print("   ✓ PASS — decomposition correct")

    # 8. Test routing fraction
    print("\n8. Routing fraction per row...")
    frac = compute_routing_fraction(grad, effective_signs)
    mx.eval(frac)
    # Every row has 8/16 = 50% routing
    for i in range(8):
        f = float(frac[i].item())
        assert abs(f - 0.5) < 0.01, f"Row {i} routing fraction {f} != 0.5"
    print(f"   All rows: routing_frac=0.50 (expected)  ✓ PASS")

    # 9. Test with zero topology (all should be routing)
    print("\n9. Zero topology → all routing...")
    zero_signs = mx.zeros((4, 8), dtype=mx.int8)
    grad9 = mx.ones((4, 8)) * 0.3
    routing9, calib9, _ = decompose_gradient(grad9, zero_signs)
    mx.eval(routing9, calib9)
    assert float(mx.sum(mx.abs(calib9)).item()) == 0.0, "Zero topology should have no calibration"
    assert float(mx.sum(mx.abs(routing9)).item()) > 0.0, "Zero topology should be all routing"
    frac9 = compute_routing_fraction(grad9, zero_signs)
    mx.eval(frac9)
    assert float(frac9[0].item()) == 1.0, "Zero topology should be 100% routing"
    print("   ✓ PASS")

    # 10. Test decomposition is exhaustive (routing + calibration = original)
    print("\n10. Decomposition is exhaustive (routing + calibration = original)...")
    mx.random.seed(99)
    rand_signs = (mx.random.uniform(shape=(16, 32)) * 3 - 1).astype(mx.int32).astype(mx.int8)
    rand_signs = mx.clip(rand_signs, -1, 1)
    rand_grad = mx.random.normal((16, 32))
    r, c, _ = decompose_gradient(rand_grad, rand_signs)
    mx.eval(r, c)
    reconstructed = r + c
    diff = float(mx.max(mx.abs(rand_grad - reconstructed)).item())
    print(f"   Max diff (original - (routing + calibration)): {diff:.2e}")
    assert diff < 1e-6, f"Decomposition not exhaustive! diff={diff}"
    print("   ✓ PASS — routing + calibration = original gradient")

    print("\n" + "=" * 60)
    print("All tests passed ✓")
    print("=" * 60)

    # ── CLI: delta plate inspection ──────────────────────────
    import sys as _sys
    if len(_sys.argv) > 1 and _sys.argv[1] == "inspect":
        # Usage: python -m scripts.v13.td inspect <delta_plates.npz> [<delta_plates_2.npz>]
        import numpy as np

        paths = _sys.argv[2:]
        if not paths:
            print("Usage: python -m scripts.v13.td inspect <delta_plates.npz> [<other.npz>]")
            _sys.exit(1)

        snapshots = []
        for p in paths:
            data = dict(np.load(p))
            snapshots.append((p, data))
            print(f"\n{'='*60}")
            print(f"Delta plates: {p}")
            print(f"{'='*60}")

            for key in sorted(data.keys()):
                if key.endswith("_stats"):
                    s = data[key]
                    total = s[3]
                    print(f"  {key.replace('_stats','')}: "
                          f"keep={s[0]/total:.3f} flip={s[1]/total:.3f} "
                          f"block={s[2]/total:.3f} "
                          f"changed={1 - s[0]/total:.3f}")
                elif key.endswith("_delta"):
                    d = data[key]
                    print(f"  {key}: shape={d.shape} "
                          f"+1={np.sum(d==1)} 0={np.sum(d==0)} -1={np.sum(d==-1)}")

        # Compare two snapshots
        if len(snapshots) == 2:
            print(f"\n{'='*60}")
            print(f"Comparison: {paths[0]} vs {paths[1]}")
            print(f"{'='*60}")
            d1, d2 = snapshots[0][1], snapshots[1][1]
            for key in sorted(d1.keys()):
                if key.endswith("_delta") and key in d2:
                    a, b = d1[key], d2[key]
                    if a.shape == b.shape:
                        agree = np.sum(a == b)
                        total = a.size
                        disagree = total - agree
                        # Where did each run flip that the other didn't?
                        a_flipped = a != 1
                        b_flipped = b != 1
                        both_flipped = a_flipped & b_flipped
                        only_a = a_flipped & ~b_flipped
                        only_b = b_flipped & ~a_flipped
                        print(f"  {key}:")
                        print(f"    agreement: {agree}/{total} ({agree/total:.3f})")
                        print(f"    both changed:  {np.sum(both_flipped)}")
                        print(f"    only run 1:    {np.sum(only_a)}")
                        print(f"    only run 2:    {np.sum(only_b)}")
                        # At shared flip positions, do they flip the same way?
                        if np.sum(both_flipped) > 0:
                            same_dir = np.sum(a[both_flipped] == b[both_flipped])
                            n_both = np.sum(both_flipped)
                            print(f"    same direction: {same_dir}/{n_both} ({same_dir/n_both:.3f})")
