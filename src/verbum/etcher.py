"""Etcher — Activation-space distillation tool for ternary models.

A reusable VSM for transferring computation from a teacher model into
a ternary student's sign topology. Works in ACTIVATION space, not
weight space (session 129 proved weight signs are random across SVD
projections — the crystal lives in activations).

The etcher is structured as a VSM:
  S5: Crystal gate — reject flips that break relational geometry
  S4: TeacherProjection — learned dimensional bridge (d_teacher→d_student)
  S3: Schedule — etch rounds, confidence annealing, beam GD steps
  S2: Depth mapping — which teacher depths correspond to which student passes
  S1: The etch loop — accumulate MSE grads, vote on sign flips, train beams

Usage:
    from verbum.etcher import Etcher, TeacherFeatures, EtchConfig

    teacher = TeacherFeatures("checkpoints/teacher-features-14b")
    config = EtchConfig(
        d_teacher=5120, d_student=512,
        depth_mapping={8: 0, 16: 1, 24: 2, 32: 3, 40: 4},
        n_rounds=5, probes_per_round=100,
    )

    etcher = Etcher(student_model, teacher, config, pass_fn=my_pass_fn)
    results = etcher.run()

The pass_fn callback makes this model-agnostic:
    def my_pass_fn(model, x, pass_idx) -> mx.array:
        '''Run input x through student pass, return output.'''
        ...

License: MIT
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np


# ══════════════════════════════════════════════════════════════════════
# S4: Teacher projection (dimensional bridge)
# ══════════════════════════════════════════════════════════════════════


class TeacherProjection(nn.Module):
    """Learned projection from teacher hidden space to student space.

    Linear(d_teacher → d_student) + RMSNorm. No bias.
    The projection is trained alongside beam params during etch so the
    student learns which dimensions of the teacher's representation
    matter most.

    From holographic_distill_v12.py (session 124, proven pattern).
    """

    def __init__(self, d_teacher: int, d_student: int):
        super().__init__()
        self.proj = nn.Linear(d_teacher, d_student, bias=False)
        self.norm = nn.RMSNorm(d_student)
        # Xavier init
        scale = math.sqrt(2.0 / (d_teacher + d_student))
        self.proj.weight = mx.random.normal(
            shape=(d_student, d_teacher)) * scale

    def __call__(self, x: mx.array) -> mx.array:
        return self.norm(self.proj(x))


# ══════════════════════════════════════════════════════════════════════
# Teacher feature loader
# ══════════════════════════════════════════════════════════════════════


class TeacherFeatures:
    """Lazily loads teacher hidden states from NPZ files.

    Expected directory structure (from extract_teacher.py):
        manifest.json
        layer_008_inputs.npz   layer_008_outputs.npz
        layer_016_inputs.npz   layer_016_outputs.npz
        ...

    Each NPZ has keys inp_0..inp_N / out_0..out_N, one per probe.
    """

    def __init__(self, feature_dir: str | Path):
        import json
        self.feature_dir = Path(feature_dir)
        with open(self.feature_dir / "manifest.json") as f:
            self.manifest = json.load(f)

        self.n_probes: int = self.manifest["total_probes"]
        self.d_teacher: int = self.manifest["d_model"]
        self.depth_indices: list[int] = self.manifest["depth_indices"]
        self._cache: dict[str, np.lib.npyio.NpzFile] = {}

    def _load(self, key: str) -> np.lib.npyio.NpzFile:
        if key not in self._cache:
            self._cache[key] = np.load(str(self.feature_dir / key))
        return self._cache[key]

    def get_output(self, depth_idx: int, probe_idx: int) -> np.ndarray:
        """Teacher output hidden state. Returns (seq_len, d_teacher)."""
        layer = self.depth_indices[depth_idx]
        return self._load(f"layer_{layer:03d}_outputs.npz")[f"out_{probe_idx}"]

    def get_input(self, depth_idx: int, probe_idx: int) -> np.ndarray:
        """Teacher input hidden state. Returns (seq_len, d_teacher)."""
        layer = self.depth_indices[depth_idx]
        return self._load(f"layer_{layer:03d}_inputs.npz")[f"inp_{probe_idx}"]

    def close(self):
        for npz in self._cache.values():
            npz.close()
        self._cache.clear()


# ══════════════════════════════════════════════════════════════════════
# S3: Configuration (schedule)
# ══════════════════════════════════════════════════════════════════════


@dataclass
class EtchConfig:
    """Etch schedule and hyperparameters."""

    # Dimensions
    d_teacher: int = 5120
    d_student: int = 512

    # Depth mapping: teacher_depth_index → student_pass_index
    # Keys are indices into teacher.depth_indices, values are pass indices.
    depth_mapping: dict[int, int] = field(default_factory=dict)

    # Etch schedule
    n_rounds: int = 5
    probes_per_round: int = 100
    beam_steps_per_round: int = 200

    # Confidence annealing (cosine)
    confidence_start: float = 0.4
    confidence_end: float = 0.7

    # Learning rate for beam + projection
    beam_lr: float = 3e-4

    # Crystal gate (S5)
    crystal_targets: Optional[np.ndarray] = None  # 4×4 or 8×8 cosine matrix
    crystal_floor: float = 0.3

    seed: int = 42


# ══════════════════════════════════════════════════════════════════════
# Direction accumulator (from scripts/v12/ternary.py, simplified)
# ══════════════════════════════════════════════════════════════════════


class DirectionAccumulator:
    """Accumulates sign(gradient) votes for a single ternary plate."""

    def __init__(self, out_features: int, in_features: int):
        self.votes = np.zeros((out_features, in_features), dtype=np.float64)
        self.n_samples = 0

    def accumulate(self, grad: np.ndarray):
        # Guard: gradient shape must match accumulator.
        # Some modules return packed-shape grads (no custom VJP),
        # others return unpacked-shape grads (custom VJP).
        # Skip mismatched — they'll be handled by beam GD.
        if grad.shape != self.votes.shape:
            return
        self.votes += np.sign(grad)
        self.n_samples += 1

    def reset(self):
        self.votes[:] = 0
        self.n_samples = 0

    @property
    def confidence(self) -> np.ndarray:
        if self.n_samples == 0:
            return np.zeros_like(self.votes)
        return np.abs(self.votes) / self.n_samples


def _walk_ternary(model: nn.Module, prefix: str = "") -> list[tuple[str, nn.Module]]:
    """Find all modules with ternary_weight attribute."""
    results = []
    for name, child in model.named_modules():
        if hasattr(child, "ternary_weight"):
            results.append((name, child))
    return results


def strip_ternary_grads(grads):
    """Remove ternary_weight gradients from a grad tree.

    During beam GD, we only train continuous params (gamma, norms).
    Ternary_weight grads have mismatched shapes (unpacked VJP vs
    packed storage) and would break the optimizer. Removing the key
    entirely prevents the optimizer from creating state for it.
    """
    if isinstance(grads, dict):
        out = {}
        for k, v in grads.items():
            if k == "ternary_weight":
                continue  # drop entirely
            out[k] = strip_ternary_grads(v)
        return out
    elif isinstance(grads, list):
        return [strip_ternary_grads(v) for v in grads]
    return grads


def init_accumulators(model: nn.Module) -> dict[str, DirectionAccumulator]:
    """Create a DirectionAccumulator for each ternary module.

    Sized to the LOGICAL (unpacked) shape. The VJP computes gradients
    in the unpacked space (out_features × in_features) even when the
    weight is stored packed as uint8.
    """
    accums = {}
    for path, mod in _walk_ternary(model):
        # Use out_features/in_features if available (v6 TernaryLinear)
        if hasattr(mod, "out_features") and hasattr(mod, "in_features"):
            accums[path] = DirectionAccumulator(mod.out_features, mod.in_features)
        else:
            # Fallback: infer from ternary_weight shape
            tw = mod.ternary_weight
            rows = tw.shape[0]
            cols = tw.shape[1] * 4 if tw.dtype == mx.uint8 else tw.shape[1]
            accums[path] = DirectionAccumulator(rows, cols)
    return accums


def accumulate_grads(model: nn.Module, grads: dict, accumulators: dict[str, DirectionAccumulator]):
    """Route gradient signs to the corresponding accumulators."""
    for path, accum in accumulators.items():
        # Navigate grad tree by path
        parts = path.split(".")
        g = grads
        for part in parts:
            if isinstance(g, dict):
                g = g.get(part)
            elif isinstance(g, list):
                try:
                    g = g[int(part)]
                except (ValueError, IndexError):
                    g = None
            else:
                g = None
            if g is None:
                break

        if g is not None:
            # Look for ternary_weight gradient
            if isinstance(g, dict) and "ternary_weight" in g:
                gw = g["ternary_weight"]
                mx.eval(gw)
                accum.accumulate(np.array(gw))


def direct_etch(
    model: nn.Module,
    accumulators: dict[str, DirectionAccumulator],
    confidence_threshold: float = 0.5,
) -> dict:
    """Flip ternary signs where accumulator confidence exceeds threshold.

    Returns stats dict.
    """
    total_flipped = 0
    total_candidates = 0

    for path, accum in accumulators.items():
        conf = accum.confidence
        mask = conf >= confidence_threshold
        if not mask.any():
            continue

        desired = np.sign(accum.votes)

        # Navigate to the module
        parts = path.split(".")
        obj = model
        for part in parts:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            elif isinstance(obj, (list, tuple)):
                obj = obj[int(part)]
            else:
                obj = None
                break

        if obj is None or not hasattr(obj, "ternary_weight"):
            continue

        tw_raw = np.array(obj.ternary_weight)
        is_packed = (tw_raw.dtype == np.uint8)

        # Unpack to logical shape for sign comparison
        if is_packed:
            K = tw_raw.shape[1] * 4
            # Manual unpack (same as v6 ternary.py)
            w0 = ((tw_raw >> 6) & 0x3).astype(np.int16) - 1
            w1 = ((tw_raw >> 4) & 0x3).astype(np.int16) - 1
            w2 = ((tw_raw >> 2) & 0x3).astype(np.int16) - 1
            w3 = (tw_raw & 0x3).astype(np.int16) - 1
            current = np.stack([w0, w1, w2, w3], axis=-1).reshape(
                tw_raw.shape[0], K).astype(np.float64)
        else:
            current = tw_raw.astype(np.float64)

        nonzero = current != 0
        etchable = mask & nonzero
        n_candidates = int(etchable.sum())
        total_candidates += n_candidates

        if n_candidates > 0:
            new_signs = current.copy()
            new_signs[etchable] = desired[etchable]
            n_flipped = int((new_signs != current).sum())
            total_flipped += n_flipped

            if is_packed:
                # Repack: int8 → uint8
                w_int = (new_signs.astype(np.int16) + 1).astype(np.uint8)
                packed = (
                    (w_int[:, 0::4] << 6) |
                    (w_int[:, 1::4] << 4) |
                    (w_int[:, 2::4] << 2) |
                    w_int[:, 3::4]
                ).astype(np.uint8)
                obj.ternary_weight = mx.array(packed)
            else:
                obj.ternary_weight = mx.array(new_signs.astype(np.int8))
            mx.eval(obj.ternary_weight)

    return {"total_flipped": total_flipped, "total_candidates": total_candidates}


# ══════════════════════════════════════════════════════════════════════
# S1: The Etcher (the main loop)
# ══════════════════════════════════════════════════════════════════════


PassFn = Callable[[nn.Module, mx.array, int], mx.array]
"""Callback: (model, x_input, pass_idx) → x_output.

Run input hidden states through one student pass.
The etcher calls this for each depth during distillation.
"""


class Etcher:
    """Activation-space distillation etcher.

    Transfers teacher computation into student sign topology via:
    1. Project teacher hidden states → student dimension
    2. Feed projected input through student pass (via pass_fn callback)
    3. MSE vs projected teacher output → gradient → sign vote
    4. Flip confident signs → train beams → repeat

    Args:
        model: student model (any nn.Module with ternary_weight params)
        teacher: TeacherFeatures loader
        config: EtchConfig schedule
        pass_fn: callback (model, x, pass_idx) → x_out
    """

    def __init__(
        self,
        model: nn.Module,
        teacher: TeacherFeatures,
        config: EtchConfig,
        pass_fn: PassFn,
    ):
        self.model = model
        self.teacher = teacher
        self.config = config
        self.pass_fn = pass_fn

        # S4: projection
        self.projection = TeacherProjection(config.d_teacher, config.d_student)
        mx.eval(self.projection.parameters())

        # Direction accumulators
        self.accumulators = init_accumulators(model)

        self.rng = np.random.RandomState(config.seed)

    def _focusing_schedule(self, round_idx: int, start: float, end: float) -> float:
        n = self.config.n_rounds
        if n <= 1:
            return end
        progress = round_idx / (n - 1)
        return end + (start - end) * 0.5 * (1 + math.cos(math.pi * progress))

    def _distill_one_probe(self, depth_idx: int, probe_idx: int):
        """Compute distillation loss for one probe at one depth.

        Feed projected teacher input through student pass,
        MSE vs projected teacher output.
        """
        pass_idx = self.config.depth_mapping.get(depth_idx)
        if pass_idx is None:
            return None

        t_in_np = self.teacher.get_input(depth_idx, int(probe_idx))
        t_out_np = self.teacher.get_output(depth_idx, int(probe_idx))

        _pass_idx = pass_idx
        _pass_fn = self.pass_fn
        projection = self.projection

        def _loss(model):
            t_in = mx.array(t_in_np)
            t_out = mx.array(t_out_np)
            proj_in = projection(t_in)    # (T, d_student)
            proj_out = projection(t_out)
            x_in = proj_in[None, :, :]    # (1, T, d_student)
            x_out = _pass_fn(model, x_in, _pass_idx)  # (1, T, d_student)
            diff = x_out.squeeze(0) - proj_out
            return (diff * diff).mean()

        loss_fn = nn.value_and_grad(self.model, _loss)
        loss_val, grads = loss_fn(self.model)
        mx.eval(loss_val, grads)
        return loss_val, grads

    def run(self, log_fn=None) -> list[dict]:
        """Run the full etch pipeline. Returns per-round logs."""
        if log_fn is None:
            log_fn = lambda msg: print(msg, flush=True)

        cfg = self.config
        n_depths = len(cfg.depth_mapping)
        logs = []

        log_fn(f"Etcher: {cfg.n_rounds} rounds, "
               f"{cfg.probes_per_round} probes/round, "
               f"{n_depths} depths")

        for round_idx in range(cfg.n_rounds):
            t0 = time.time()
            confidence = self._focusing_schedule(
                round_idx, cfg.confidence_start, cfg.confidence_end)

            # Reset accumulators
            for acc in self.accumulators.values():
                acc.reset()

            # ── Accumulation: distill probes ──
            probe_order = self.rng.permutation(
                self.teacher.n_probes)[:cfg.probes_per_round]
            total_loss = 0.0
            n_samples = 0

            for pi, probe_idx in enumerate(probe_order):
                for depth_idx in range(len(self.teacher.depth_indices)):
                    result = self._distill_one_probe(depth_idx, int(probe_idx))
                    if result is None:
                        continue
                    loss_val, grads = result
                    accumulate_grads(self.model, grads, self.accumulators)
                    total_loss += loss_val.item()
                    n_samples += 1
                    del loss_val, grads

                if (pi + 1) % 25 == 0:
                    mx.clear_cache()
                    avg = total_loss / max(n_samples, 1)
                    log_fn(f"  R{round_idx+1} probe {pi+1}/{len(probe_order)}: "
                           f"avg_loss={avg:.6f}")

            # ── Etch: flip confident signs ──
            etch_result = direct_etch(
                self.model, self.accumulators,
                confidence_threshold=confidence,
            )
            mx.eval(self.model.parameters())

            # ── Beam GD: train continuous params + projection ──
            if cfg.beam_steps_per_round > 0:
                beam_opt = optim.Adam(learning_rate=cfg.beam_lr)
                proj_opt = optim.Adam(learning_rate=cfg.beam_lr)
                beam_loss_sum = 0.0

                for step in range(cfg.beam_steps_per_round):
                    p_idx = int(self.rng.randint(0, self.teacher.n_probes))
                    d_idx = int(self.rng.randint(0, len(self.teacher.depth_indices)))
                    pass_idx = cfg.depth_mapping.get(d_idx)
                    if pass_idx is None:
                        continue

                    t_in_np = self.teacher.get_input(d_idx, p_idx)
                    t_out_np = self.teacher.get_output(d_idx, p_idx)
                    _pi = pass_idx
                    _pfn = self.pass_fn
                    proj = self.projection

                    def _beam_loss(model, _p=_pi):
                        t_in = mx.array(t_in_np)
                        t_out = mx.array(t_out_np)
                        pi_ = proj(t_in)
                        po_ = proj(t_out)
                        x_out = _pfn(model, pi_[None], _p).squeeze(0)
                        diff = x_out - po_
                        return (diff * diff).mean()

                    bl_fn = nn.value_and_grad(self.model, _beam_loss)
                    bv, bg = bl_fn(self.model)
                    mx.eval(bv, bg)
                    bg = strip_ternary_grads(bg)
                    beam_opt.update(self.model, bg)
                    mx.eval(self.model.parameters())
                    beam_loss_sum += bv.item()

                    # Projection grads (separate)
                    def _proj_loss(proj, _p=_pi):
                        t_in = mx.array(t_in_np)
                        t_out = mx.array(t_out_np)
                        pi_ = proj(t_in)
                        po_ = proj(t_out)
                        x_out = _pfn(self.model, pi_[None], _p).squeeze(0)
                        diff = x_out - po_
                        return (diff * diff).mean()

                    pl_fn = nn.value_and_grad(self.projection, _proj_loss)
                    _, pg = pl_fn(self.projection)
                    mx.eval(pg)
                    proj_opt.update(self.projection, pg)
                    mx.eval(self.projection.parameters())

                    del bv, bg, pg
                    if (step + 1) % 50 == 0:
                        mx.clear_cache()

                avg_beam = beam_loss_sum / max(cfg.beam_steps_per_round, 1)
            else:
                avg_beam = 0.0

            # ── Log ──
            elapsed = time.time() - t0
            avg_distill = total_loss / max(n_samples, 1)
            entry = {
                "round": round_idx + 1,
                "distill_loss": avg_distill,
                "beam_loss": avg_beam,
                "flips": etch_result["total_flipped"],
                "candidates": etch_result["total_candidates"],
                "confidence": confidence,
                "elapsed_s": elapsed,
            }
            logs.append(entry)
            log_fn(f"  R{round_idx+1}: distill={avg_distill:.6f} beam={avg_beam:.6f} "
                   f"flips={etch_result['total_flipped']:,} ({elapsed:.1f}s)")

        return logs
