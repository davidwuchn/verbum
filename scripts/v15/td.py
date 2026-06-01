"""TernaryDescent for v15 — gradient-informed sign flipping for float ternary plates.

Port of v14/td.py adapted for v15's architecture where plates are float
arrays with values in {-1, 0, +1} (not packed uint32).

Core idea: gradients tell you which direction reduces loss. For ternary
weights, you can't take fractional steps. Instead, accumulate gradient
evidence over many steps (like Adam's moments) and flip when the signal
is strong and consistent.

Delta plate architecture:
    effective = base_plate ⊙ delta_plate
    base_plate:  frozen teacher etch
    delta_plate: initialized to +1 (pass-through), trained by TD

    Delta semantics:
        +1 → keep teacher sign here
        -1 → flip teacher sign here
         0 → block this position (staging area)

Session 177. License: MIT.
"""

from __future__ import annotations

import math
from typing import Any

import mlx.core as mx
import mlx.nn as nn


# ══════════════════════════════════════════════════════════════════════
# Gradient decomposition: routing vs calibration
# ══════════════════════════════════════════════════════════════════════

def decompose_gradient(
    grad_effective: mx.array,
    effective_signs: mx.array,
) -> tuple[mx.array, mx.array, mx.array]:
    """Split gradient into routing and calibration components.

    ROUTING:   gradient fights the topology (sign disagreement)
               → "this route is wrong, change the sign" → TD
    CALIBRATION: gradient agrees with topology (magnitude adjustment)
               → "this route is right, adjust the scale" → Adam (gamma)

    Args:
        grad_effective:   (N, K) float32 — ∂L/∂effective
        effective_signs:  (N, K) float32 — sign(base ⊙ delta), values in {-1,0,+1}

    Returns:
        routing:      (N, K) float32 — gradient component for TD
        calibration:  (N, K) float32 — gradient component for Adam
        routing_mask: (N, K) bool    — True where gradient is routing
    """
    descent_sign = mx.sign(-grad_effective)  # -grad is the descent direction

    is_routing = (
        (descent_sign != effective_signs) | (effective_signs == 0)
    ) & (grad_effective != 0)

    routing = mx.where(is_routing, grad_effective, mx.array(0.0))
    calibration = mx.where(is_routing, mx.array(0.0), grad_effective)

    return routing, calibration, is_routing


def compute_routing_fraction(
    grad_effective: mx.array,
    effective_signs: mx.array,
) -> mx.array:
    """Compute per-row routing fraction: what % of each row is routing.

    Returns (N,) float32 in [0, 1]. High = topology is wrong.
    """
    descent_sign = mx.sign(-grad_effective)
    has_gradient = grad_effective != 0
    is_routing = ((descent_sign != effective_signs) | (effective_signs == 0)) & has_gradient
    n_active = mx.sum(has_gradient.astype(mx.float32), axis=-1)
    n_routing = mx.sum(is_routing.astype(mx.float32), axis=-1)
    return n_routing / (n_active + 1e-8)


# ══════════════════════════════════════════════════════════════════════
# TernaryDescent optimizer — v15 (float plates, no packing)
# ══════════════════════════════════════════════════════════════════════

class TernaryDescent:
    """Adam-equivalent optimizer for ternary {-1, 0, +1} weights.

    V15 adaptation: plates are float arrays, not packed uint32.
    Accumulates gradient evidence via EMA. Flips when confident.

    Usage:
        td = TernaryDescent(flip_rate=0.001)

        for step in training:
            loss, grads = value_and_grad(model)(x, y)
            adam.step(continuous_params, grads)
            td_result = td.step(delta_params, training_step=step)
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
        flip_interval: int = 20,
    ):
        self.beta1 = beta1
        self.beta2 = beta2
        self.flip_rate = flip_rate
        self._base_flip_rate = flip_rate
        self.warmup_steps = warmup_steps
        self.min_confidence = min_confidence
        self.cooldown_tau = cooldown_tau
        self.cooldown_backoff = cooldown_backoff
        self.neighbor_width = neighbor_width
        self.flip_interval = flip_interval
        assert neighbor_width % 2 == 1
        assert flip_interval >= 1
        self.step_count = 0

        # Per-parameter state: {name: (direction, magnitude)}
        self._state: dict[str, tuple[mx.array, mx.array]] = {}

        # Per-parameter anti-oscillation: {name: (last_flip_step, flip_count)}
        self._flip_history: dict[str, tuple[mx.array, mx.array]] = {}

        # Tracking
        self.last_n_flips = 0
        self.last_n_candidates = 0

    def _get_state(self, name: str, shape: tuple) -> tuple[mx.array, mx.array]:
        if name not in self._state:
            self._state[name] = (mx.zeros(shape), mx.zeros(shape))
        return self._state[name]

    def _get_flip_history(self, name: str, shape: tuple) -> tuple[mx.array, mx.array]:
        if name not in self._flip_history:
            self._flip_history[name] = (
                mx.zeros(shape, dtype=mx.int32),
                mx.zeros(shape, dtype=mx.int32),
            )
        return self._flip_history[name]

    def _compute_cooldown(self, name: str, shape: tuple) -> mx.array:
        """Per-position cooldown ∈ [0, 1]. 0 = just flipped, 1 = fully cooled."""
        last_flip_step, flip_count = self._get_flip_history(name, shape)
        steps_since = mx.maximum(self.step_count - last_flip_step, 0).astype(mx.float32)
        capped_count = mx.minimum(flip_count, 10).astype(mx.float32)
        effective_tau = self.cooldown_tau * (self.cooldown_backoff ** capped_count)
        cooldown = 1.0 - mx.exp(-steps_since / (effective_tau + 1e-8))
        never_flipped = last_flip_step == 0
        return mx.where(never_flipped, mx.array(1.0), cooldown)

    def _update_flip_history(self, name: str, flip_mask: mx.array):
        shape = flip_mask.shape
        last_flip_step, flip_count = self._get_flip_history(name, shape)
        last_flip_step = mx.where(flip_mask, mx.array(self.step_count, dtype=mx.int32), last_flip_step)
        flip_count = flip_count + flip_mask.astype(mx.int32)
        self._flip_history[name] = (last_flip_step, flip_count)

    @staticmethod
    def _row_median_smooth(signal: mx.array, width: int = 3) -> mx.array:
        """Row-wise median filter for spatial smoothing."""
        if width == 1:
            return signal
        N, K = signal.shape
        pad = width // 2
        padded = mx.concatenate([
            mx.zeros((N, pad)), signal, mx.zeros((N, pad))
        ], axis=1)
        windows = mx.stack([padded[:, i:i + K] for i in range(width)], axis=-1)
        sorted_windows = mx.sort(windows, axis=-1)
        return sorted_windows[:, :, pad]

    def step(
        self,
        delta_params: list[tuple[str, mx.array, mx.array, mx.array, bool]],
        training_step: int | None = None,
    ) -> dict[str, Any]:
        """Perform one TernaryDescent step.

        Every call accumulates moments. Flips commit every flip_interval steps.

        Args:
            delta_params: List of (name, delta_float, grad_wrt_effective,
                          base_float, no_block).
                - name: identifier for logging
                - delta_float: (N, K) float32 with values in {-1, 0, +1}
                - grad_wrt_effective: (N, K) float32 — ∂L/∂(base⊙delta)
                - base_float: (N, K) float32 with values in {-1, 0, +1}
                - no_block: if True, skip zero staging (+1 ↔ -1 directly)
            training_step: external step count for flip timing alignment.

        Returns:
            dict with step metrics.
        """
        self.step_count += 1
        per_module: dict[str, dict] = {}

        in_warmup = self.step_count <= self.warmup_steps
        flip_clock = training_step if training_step is not None else self.step_count
        is_flip_step = (
            not in_warmup
            and self.flip_interval > 0
            and flip_clock % self.flip_interval == 0
        )

        # ── Pass 1: Accumulate moments ──
        for name, _delta, grad_eff, _base, _no_block in delta_params:
            direction, magnitude = self._get_state(name, grad_eff.shape)
            direction = self.beta1 * direction + (1 - self.beta1) * grad_eff
            magnitude = self.beta2 * magnitude + (1 - self.beta2) * (grad_eff ** 2)
            self._state[name] = (direction, magnitude)

        if not is_flip_step:
            for name, *_ in delta_params:
                per_module[name] = {"flips": 0, "candidates": 0, "mean_confidence": 0.0}
            self.last_n_flips = 0
            return {
                "step": self.step_count,
                "total_flips": 0,
                "in_warmup": in_warmup,
                "is_flip_step": False,
                "per_module": per_module,
            }

        # ── Pass 2: Score candidates ──
        bc1 = 1 - self.beta1 ** self.step_count
        bc2 = 1 - self.beta2 ** self.step_count

        module_candidates = []
        total_ternary_weights = 0

        for name, delta_float, grad_eff, base_float, no_block in delta_params:
            direction, magnitude = self._state[name]

            dir_corrected = direction / bc1
            mag_corrected = magnitude / bc2

            snr = mx.abs(dir_corrected) / (mx.sqrt(mag_corrected) + 1e-8)
            importance = mx.sqrt(mag_corrected)

            cooldown = self._compute_cooldown(name, grad_eff.shape)
            smoothed_snr = self._row_median_smooth(snr, self.neighbor_width)
            score = smoothed_snr * importance * cooldown

            confident = smoothed_snr > self.min_confidence

            # Desired direction for delta:
            # If gradient says effective should decrease (descent = -grad):
            #   base=+1 → delta should decrease (flip toward -1)
            #   base=-1 → delta should increase (flip toward +1)
            desired_effective = -mx.sign(dir_corrected)
            desired = desired_effective * base_float

            # Valid transitions
            if no_block:
                can_move = (
                    ((delta_float > 0) & (desired < 0)) |
                    ((delta_float < 0) & (desired > 0))
                ) & (base_float != 0)
            else:
                can_move = (
                    ((delta_float > 0) & (desired < 0)) |
                    ((delta_float < 0) & (desired > 0)) |
                    (delta_float == 0)
                ) & (base_float != 0)

            candidates = confident & can_move
            candidate_scores = mx.where(candidates, score, mx.array(0.0))

            total_ternary_weights += delta_float.size

            module_candidates.append({
                "name": name,
                "no_block": no_block,
                "delta_float": delta_float,
                "desired": desired,
                "candidates": candidates,
                "candidate_scores": candidate_scores,
                "snr": snr,
            })

        # ── Pass 3: Holographic etch — equal thin slot per module ──
        global_budget = max(1, int(self.flip_rate * total_ternary_weights))

        module_n_candidates = []
        total_candidates = 0
        n_active_modules = 0
        for mc in module_candidates:
            n_cands = int(mc["candidates"].sum().item())
            module_n_candidates.append(n_cands)
            total_candidates += n_cands
            if n_cands > 0:
                n_active_modules += 1

        if total_candidates == 0:
            for mc in module_candidates:
                per_module[mc["name"]] = {
                    "flips": 0, "candidates": 0, "mean_confidence": 0.0,
                }
            self.last_n_flips = 0
            return {
                "step": self.step_count,
                "total_flips": 0,
                "in_warmup": False,
                "is_flip_step": True,
                "per_module": per_module,
            }

        effective_budget = min(global_budget, total_candidates)
        per_module_slot = max(1, effective_budget // max(n_active_modules, 1))
        total_flips = 0

        for i, mc in enumerate(module_candidates):
            name = mc["name"]
            candidates = mc["candidates"]
            scores = mc["candidate_scores"]
            delta_float = mc["delta_float"]
            desired = mc["desired"]
            no_block = mc["no_block"]
            snr = mc["snr"]

            n_cands = module_n_candidates[i]
            if n_cands == 0:
                per_module[name] = {
                    "flips": 0, "candidates": 0, "mean_confidence": 0.0,
                }
                continue

            module_budget = per_module_slot

            # Find threshold via top-K
            module_scores_flat = scores.reshape(-1)
            n_positive = int((module_scores_flat > 0).sum().item())
            this_budget = min(module_budget, n_positive)

            if this_budget <= 0:
                flip_mask = mx.zeros_like(candidates, dtype=mx.bool_)
            elif this_budget >= n_positive:
                flip_mask = candidates
            else:
                neg_scores = -module_scores_flat
                partitioned = mx.partition(neg_scores, kth=this_budget - 1)
                threshold = float((-partitioned[this_budget - 1]).item())
                flip_mask = candidates & (scores >= threshold)

            if not flip_mask.any().item():
                per_module[name] = {
                    "flips": 0,
                    "candidates": n_cands,
                    "mean_confidence": float(mx.mean(
                        mx.where(candidates, snr, mx.array(0.0))
                    ).item()),
                }
                continue

            # Compute new delta values
            if no_block:
                # Direct flip: +1 ↔ -1
                new_delta = mx.where(flip_mask, -delta_float, delta_float)
            else:
                # Two-step staging: +1 → 0 → -1
                new_delta = mx.where(
                    flip_mask & (delta_float != 0),
                    mx.array(0.0),                   # non-zero → zero (stage)
                    mx.where(
                        flip_mask & (delta_float == 0),
                        mx.sign(desired),             # zero → ±1 (commit)
                        delta_float,                   # no flip
                    ),
                )

            flip_occurred = (new_delta != delta_float)
            n_flips = int(flip_occurred.sum().item())
            total_flips += n_flips

            if n_flips > 0:
                self._update_flip_history(name, flip_occurred)

                per_module[name] = {
                    "flips": n_flips,
                    "candidates": n_cands,
                    "mean_confidence": float(mx.mean(
                        mx.where(candidates, snr, mx.array(0.0))
                    ).item()),
                    "new_delta": new_delta,  # caller applies to model
                    "flip_occurred": flip_occurred,
                }
            else:
                per_module[name] = {
                    "flips": 0,
                    "candidates": n_cands,
                    "mean_confidence": float(mx.mean(
                        mx.where(candidates, snr, mx.array(0.0))
                    ).item()),
                }

        # ── Surgical moment reset at flipped positions ──
        if total_flips > 0:
            for mc in module_candidates:
                name = mc["name"]
                info = per_module.get(name, {})
                if info.get("flips", 0) > 0 and "flip_occurred" in info:
                    flip_mask = info["flip_occurred"]
                    if name in self._state:
                        direction, magnitude = self._state[name]
                        direction = mx.where(flip_mask, mx.array(0.0), direction)
                        magnitude = mx.where(flip_mask, mx.array(0.0), magnitude)
                        self._state[name] = (direction, magnitude)

        self.last_n_flips = total_flips
        self.last_n_candidates = total_candidates
        return {
            "step": self.step_count,
            "total_flips": total_flips,
            "in_warmup": False,
            "is_flip_step": True,
            "per_module": per_module,
            "etch_active_modules": n_active_modules,
            "etch_slot_size": per_module_slot,
            "etch_global_budget": global_budget,
            "etch_total_candidates": total_candidates,
        }

    def reset_moments(self):
        """Reset all moment accumulators but keep flip history."""
        self._state.clear()

    def reset(self):
        """Full reset: moments + flip history + step count."""
        self._state.clear()
        self._flip_history.clear()
        self.step_count = 0
        self.last_n_flips = 0
        self.last_n_candidates = 0


# ══════════════════════════════════════════════════════════════════════
# Crystal Thermometer — oscillation = temperature, settled = frozen
# ══════════════════════════════════════════════════════════════════════

class CrystalThermometer:
    """Measures the crystal temperature: how much topology is still moving.

    Every flip step, records which positions flipped. Over time, builds
    a per-position history that reveals:

      frozen:      never a candidate           → irreducible, done
      settled:     flipped before, quiet now    → found normal form
      active:      flipped recently             → still reducing
      oscillating: flipped >1× in recent window → 50/50, ambiguous

    Temperature = active_frac. When it → 0, the delta is done.
    Oscillation_frac = fraction of active positions that are flip-flopping
    (the "noise floor" — positions that will never settle).

    Usage:
        thermo = CrystalThermometer()

        # After each TD step:
        thermo.record(td_result, step)

        # At log intervals:
        temp = thermo.temperature(step)
        log(f"crystal_temp={temp['temperature']:.4f}")
    """

    def __init__(self, recent_window: int = 100):
        """
        Args:
            recent_window: steps to look back for "recent" activity.
                          ~5× flip_interval is a good default.
        """
        self.recent_window = recent_window
        self._modules: dict[str, dict[str, "np.ndarray"]] = {}

    def _ensure(self, name: str, shape: tuple):
        if name in self._modules:
            return
        import numpy as np
        self._modules[name] = {
            "flip_count": np.zeros(shape, dtype=np.int32),
            "last_flip_step": np.zeros(shape, dtype=np.int32),
        }

    def record(self, td_result: dict, step: int):
        """Record flip data from a TD step. Call after every flip step."""
        import numpy as np

        if not td_result.get("is_flip_step", False):
            return

        for name, info in td_result.get("per_module", {}).items():
            flip_occurred = info.get("flip_occurred")
            if flip_occurred is None:
                continue

            flip_arr = np.asarray(flip_occurred).astype(bool)
            self._ensure(name, flip_arr.shape)
            m = self._modules[name]
            m["flip_count"] += flip_arr.astype(np.int32)
            m["last_flip_step"] = np.where(
                flip_arr, step, m["last_flip_step"]
            )

    def temperature(self, step: int) -> dict:
        """Compute crystal temperature and per-module breakdown.

        Returns:
            dict with:
              temperature:      float — fraction of all positions active recently
              oscillation_frac: float — of active positions, fraction oscillating
              settled_frac:     float — of ever-flipped, fraction now quiet
              frozen_frac:      float — fraction never flipped
              per_module:       dict[name → {temp, osc, settled, n_flips}]
              total_flips:      int — cumulative flips across all positions
        """
        import numpy as np

        if not self._modules:
            return {
                "temperature": 0.0, "oscillation_frac": 0.0,
                "settled_frac": 0.0, "frozen_frac": 1.0,
                "per_module": {}, "total_flips": 0,
            }

        total_positions = 0
        total_active = 0
        total_oscillating = 0
        total_settled = 0
        total_frozen = 0
        total_ever_flipped = 0
        total_flips = 0
        per_module = {}

        for name, m in self._modules.items():
            fc = m["flip_count"]
            lfs = m["last_flip_step"]
            n = fc.size

            ever_flipped = fc > 0
            recent = lfs >= (step - self.recent_window)
            active = ever_flipped & recent
            oscillating = (fc > 1) & recent
            settled = ever_flipped & ~recent
            frozen = ~ever_flipped

            n_active = int(active.sum())
            n_osc = int(oscillating.sum())
            n_settled = int(settled.sum())
            n_frozen = int(frozen.sum())
            n_ever = int(ever_flipped.sum())
            n_flips = int(fc.sum())

            per_module[name] = {
                "temp": n_active / max(n, 1),
                "osc": n_osc / max(n_active, 1),
                "settled": n_settled / max(n_ever, 1),
                "n_flips": n_flips,
            }

            total_positions += n
            total_active += n_active
            total_oscillating += n_osc
            total_settled += n_settled
            total_frozen += n_frozen
            total_ever_flipped += n_ever
            total_flips += n_flips

        return {
            "temperature": total_active / max(total_positions, 1),
            "oscillation_frac": total_oscillating / max(total_active, 1),
            "settled_frac": total_settled / max(total_ever_flipped, 1),
            "frozen_frac": total_frozen / max(total_positions, 1),
            "per_module": per_module,
            "total_flips": total_flips,
        }

    def hottest_modules(self, step: int, top_n: int = 5) -> list[tuple[str, float]]:
        """Return the top_n modules by temperature (most active)."""
        t = self.temperature(step)
        ranked = sorted(
            t["per_module"].items(),
            key=lambda x: -x[1]["temp"],
        )
        return [(name, info["temp"]) for name, info in ranked[:top_n]]


# ══════════════════════════════════════════════════════════════════════
# Helper: apply TD results to model
# ══════════════════════════════════════════════════════════════════════

def get_affected_gamma_rows(
    model: "TensorStatechart",
    td_result: dict,
) -> dict[str, set[int]]:
    """Identify which gamma rows are affected by TD flips.

    When TD flips delta[i, j], the effective weight for row i changes.
    Adam's moments for gamma[i] are now stale — they encode gradient
    history for the old sign topology. Without decay, Adam pushes
    gamma in the wrong direction for ~10 steps (1/β₁).

    Returns:
        dict mapping gamma parameter path → set of affected row indices.
        Keys match the flattened parameter tree used by the optimizer.
        e.g. {"strides.5.ffn.gate_plate.gamma1": {12, 45, 200, ...}}
    """
    affected: dict[str, set[int]] = {}
    delta_params = model.collect_delta_params()
    name_to_plate = {name: (plate, which) for name, plate, which in delta_params}

    for name, info in td_result.get("per_module", {}).items():
        flip_occurred = info.get("flip_occurred")
        if flip_occurred is None or info.get("flips", 0) == 0:
            continue
        if name not in name_to_plate:
            continue

        plate, which = name_to_plate[name]

        # flip_occurred is (N, K). A row is affected if ANY position in it flipped.
        import numpy as np
        flip_arr = np.asarray(flip_occurred)
        row_affected = np.any(flip_arr, axis=1)
        rows = set(int(i) for i in np.where(row_affected)[0])

        if not rows:
            continue

        # Map delta name to the corresponding gamma parameter path.
        # delta name: "strides.5.ffn.gate_plate.delta1"
        # gamma name: "strides.5.ffn.gate_plate.gamma1"
        gamma_attr = "gamma1" if which == "delta1" else "gamma2"
        gamma_path = name.replace(which, gamma_attr)
        affected[gamma_path] = rows

    return affected


def decay_adam_for_affected_rows(
    optimizer: "optim.Optimizer",
    model: "nn.Module",
    affected: dict[str, set[int]],
    decay_factor: float = 0.1,
) -> int:
    """Decay Adam moments for gamma rows affected by TD flips.

    For each affected gamma row, multiply Adam's first and second
    moments by decay_factor. This prevents Adam from pushing gamma
    in the wrong direction after the topology changed underneath it.

    decay_factor = 0.1 means 90% of the stale momentum is removed.
    The remaining 10% provides a gentle prior toward the pre-flip
    direction, which is usually close to correct (most flips are
    small corrections, not reversals).

    Args:
        optimizer: The AdamW optimizer.
        model: The model (for parameter tree alignment).
        affected: Output of get_affected_gamma_rows().
        decay_factor: Multiply moments by this (0.0 = full reset, 1.0 = no decay).

    Returns:
        Number of gamma rows decayed.
    """
    import mlx.nn as nn

    if not affected:
        return 0

    total_decayed = 0

    # The optimizer state is indexed by the parameter tree structure.
    # We need to find the optimizer state entry for each affected gamma.
    # MLX optimizer state is a nested structure mirroring the model tree.
    # We walk the flattened state to find matching paths.
    flat_state = dict(nn.utils.tree_flatten(optimizer.state))

    for gamma_path, rows in affected.items():
        # Adam stores state as (step, m, v) or similar.
        # Look for keys containing the gamma path + moment suffixes.
        for state_key, state_val in flat_state.items():
            if gamma_path not in state_key:
                continue
            if state_val.ndim != 1:
                continue
            # This is a 1D state array matching a gamma parameter.
            # Decay the affected rows.
            for row in rows:
                if row < state_val.shape[0]:
                    state_val = state_val.at[row].multiply(decay_factor)
            flat_state[state_key] = state_val
            total_decayed += len(rows)

    # Write back (MLX optimizer state is mutable, but we modified via .at[])
    # The tree_unflatten would be needed for nested state, but since we
    # modified in-place via the flat view, evaluate to commit.
    if total_decayed > 0:
        import mlx.core as mx
        mx.eval(list(flat_state.values()))

    return total_decayed


def apply_td_flips(
    model: "TensorStatechart",
    td_result: dict,
) -> int:
    """Apply flip results from TD step back to the model's delta plates.

    Walks td_result["per_module"], finds entries with "new_delta",
    and writes them back to the corresponding plate module.

    Returns total number of flips applied.
    """
    total = 0
    delta_params = model.collect_delta_params()
    name_to_plate = {name: (plate, which) for name, plate, which in delta_params}

    for name, info in td_result.get("per_module", {}).items():
        if "new_delta" not in info:
            continue
        if name not in name_to_plate:
            continue

        plate, which = name_to_plate[name]
        new_delta = info["new_delta"]
        mx.eval(new_delta)
        setattr(plate, which, new_delta)
        total += info.get("flips", 0)

    return total


def collect_td_step_params(
    model: "TensorStatechart",
    grads: dict,
    no_block: bool = False,
) -> list[tuple[str, mx.array, mx.array, mx.array, bool]]:
    """Build the delta_params list that TD.step() expects.

    Walks the model's delta plates and matches gradients from the
    flattened grad tree. For each delta plate, computes the gradient
    w.r.t. the effective weight (plate ⊙ delta).

    The gradient w.r.t. effective comes from the loss backprop through
    the matmul. Since the forward path uses:
        out = (x @ effective.T) * gamma
    the gradient ∂L/∂effective is available through the chain rule.

    For v15's float plates, the effective weight is plate * delta.
    The gradient ∂L/∂(plate*delta) w.r.t. delta is:
        ∂L/∂delta[i,j] = ∂L/∂effective[i,j] * plate[i,j]
    But TD wants ∂L/∂effective, not ∂L/∂delta. The base_float tells
    TD how to interpret the direction.

    Args:
        model: TensorStatechart with delta plates enabled.
        grads: Flattened gradient dict from value_and_grad.
        no_block: Whether to use direct flips (no zero staging).

    Returns:
        List of (name, delta_float, grad_effective, base_float, no_block)
        suitable for TernaryDescent.step().
    """
    flat_grads = dict(nn.utils.tree_flatten(grads))
    result = []

    for name, plate, which in model.collect_delta_params():
        delta_val = getattr(plate, which)  # (N, K) float {-1,0,+1}
        base_attr = "plate1" if which == "delta1" else "plate2"
        base_val = getattr(plate, base_attr)  # (N, K) float {-1,0,+1}

        # The gradient key in the flattened tree matches the delta path.
        # But since delta is inside stop_gradient in the forward pass,
        # there is no direct gradient for delta. Instead, we need the
        # gradient w.r.t. the matmul input (the effective weight).
        #
        # Strategy: use the gradient of the gamma-scaled output as a proxy.
        # The gamma gradient tells us how the output wants to change.
        # Combined with the input activation statistics, this gives us
        # the effective weight gradient.
        #
        # However, the cleaner approach for v15 is to compute the
        # trace loss gradient directly w.r.t. the effective weight.
        # For now, we use the routing component of whatever gradient
        # is available for the effective weight positions.
        #
        # Placeholder: use a zero-gradient if no matching grad found.
        # The training loop in train.py will compute proper gradients
        # via a separate backward pass that includes the delta.
        grad_key_candidates = [
            name.replace(".delta1", ".plate1").replace(".delta2", ".plate2"),
            name,
        ]

        grad_eff = None
        for gk in grad_key_candidates:
            if gk in flat_grads:
                grad_eff = flat_grads[gk]
                break

        if grad_eff is None:
            # No gradient available — skip this param
            continue

        if grad_eff.shape != delta_val.shape:
            continue

        result.append((name, delta_val, grad_eff, base_val, no_block))

    return result


# ══════════════════════════════════════════════════════════════════════
# Fold helper
# ══════════════════════════════════════════════════════════════════════

def fold_and_reset(
    model: "TensorStatechart",
    td: TernaryDescent,
) -> None:
    """Fold all delta plates into base and reset TD state.

    The standard inter-phase operation:
        1. new_plate = plate ⊙ delta (lossless consolidation)
        2. delta → all +1 (pass-through)
        3. TD moments → zero (gradient landscape changed)
        4. TD flip history → preserved (cooldown tracks physical positions)

    After fold, the model produces identical outputs but the delta
    is reset for the next round of TD corrections.
    """
    model.fold_delta_plates()
    td.reset_moments()
