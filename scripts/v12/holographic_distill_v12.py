"""Holographic Distillation V12 — Teacher-guided plate etching + extended GD.

Two-phase training:
  Phase 1 — ETCH: Use pre-extracted Qwen3-32B teacher features to etch
    ternary plates. For each etch round, forward teacher hidden states
    through V12 passes, compute MSE(projected_teacher, student_hidden),
    accumulate gradients into direction accumulators, then flip confident
    positions via direct_etch.

  Phase 2 — GD: Freeze all ternary plates, then extended gradient descent
    on continuous params (Q proj gammas, norms, S3/S4/S5, embeddings)
    using CE loss on structured_shard_v2 + Dolma.

Teacher depth → V12 pass mapping:
  Teacher L8  → Pass 0 (L0↑)    Teacher L40 → Pass 4 (L2↓)
  Teacher L16 → Pass 1 (L1↑)    Teacher L48 → Pass 5 (L1↓)
  Teacher L24 → Pass 2 (L2↑)    Teacher L56 → Pass 6 (L0↓)
  Teacher L32 → Pass 3 (apex)   Teacher L64 → output (pre-lm_head)

Dimension bridging: Learned projection 5120 → 512 (teacher → student).
The projection is trained alongside beam params during etch, then frozen
during Phase 2 (it has no role in normal LM inference).

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/holographic_distill_v12.py

    # Smoke test:
    uv run python scripts/v12/holographic_distill_v12.py \\
        --n-etch-rounds 1 --etch-probes-per-round 10 --beam-steps-per-round 5 \\
        --gd-steps 10 --checkpoint-dir checkpoints/v12-distill-smoke

    # Full run:
    uv run python scripts/v12/holographic_distill_v12.py \\
        --n-etch-rounds 5 --etch-probes-per-round 500 --beam-steps-per-round 200 \\
        --gd-steps 20000 --checkpoint-dir checkpoints/v12-distill-run1 \\
        2>&1 | tee checkpoints/v12-distill-run1/run.log

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np
from mlx.utils import tree_flatten, tree_map

sys.path.insert(0, str(Path(__file__).parent))

from config import V12Config
from model import V12Model, create_model, count_parameters
from data import ShardedDataLoader, MixedDataLoader
from ternary import (
    freeze_ternary_weights,
    zero_ternary_grads,
    restore_ternary,
    TernaryLinear,
    init_direction_accumulators,
    accumulate_direction,
    direct_etch,
    reset_accumulators,
)


# ══════════════════════════════════════════════════════════════════════
# Teacher feature loading
# ══════════════════════════════════════════════════════════════════════

# Teacher depth indices → V12 pass indices
# Teacher has 8 depth points: layers [8, 16, 24, 32, 40, 48, 56, 64]
# V12 has 7 passes + output. Map:
#   depth[0..6] → pass[0..6]  (layer-wise hidden state matching)
#   depth[7]    → output       (pre-lm_head hidden state)
TEACHER_DEPTHS = [8, 16, 24, 32, 40, 48, 56, 64]
N_PASS_DEPTHS = 7   # passes 0-6
N_OUTPUT_DEPTH = 1   # depth[7] → output


class TeacherFeatures:
    """Lazily loads teacher hidden states from NPZ files.

    Each depth has (input, output) NPZ files. For distillation we use
    the OUTPUT hidden states: we want the student's pass to produce
    representations that match what the teacher computed at that depth.
    """

    def __init__(self, feature_dir: str | Path):
        self.feature_dir = Path(feature_dir)
        manifest_path = self.feature_dir / "manifest.json"
        assert manifest_path.exists(), f"No manifest at {manifest_path}"

        with open(manifest_path) as f:
            self.manifest = json.load(f)

        self.n_probes = self.manifest["total_probes"]
        self.d_teacher = self.manifest["d_model"]      # 5120
        self.depth_indices = self.manifest["depth_indices"]  # [8,16,...,64]
        assert self.depth_indices == TEACHER_DEPTHS, (
            f"Expected depths {TEACHER_DEPTHS}, got {self.depth_indices}")

        # Cache loaded NPZ files (lazy)
        self._cache: dict[str, np.lib.npyio.NpzFile] = {}

    def _load_npz(self, key: str) -> np.lib.npyio.NpzFile:
        if key not in self._cache:
            path = self.feature_dir / key
            assert path.exists(), f"Missing: {path}"
            self._cache[key] = np.load(str(path))
        return self._cache[key]

    def get_output(self, depth_idx: int, probe_idx: int) -> np.ndarray:
        """Get teacher output hidden state at depth for probe.

        Returns: (seq_len_i, d_teacher) float32 — variable-length.
        """
        layer = self.depth_indices[depth_idx]
        npz = self._load_npz(f"layer_{layer:03d}_outputs.npz")
        return npz[f"out_{probe_idx}"]

    def get_input(self, depth_idx: int, probe_idx: int) -> np.ndarray:
        """Get teacher input hidden state at depth for probe.

        Returns: (seq_len_i, d_teacher) float32 — variable-length.
        """
        layer = self.depth_indices[depth_idx]
        npz = self._load_npz(f"layer_{layer:03d}_inputs.npz")
        return npz[f"inp_{probe_idx}"]

    def get_probe_seqlen(self, probe_idx: int) -> int:
        """Token count for this probe (all depths have same length)."""
        return self.get_output(0, probe_idx).shape[0]

    def close(self):
        for npz in self._cache.values():
            npz.close()
        self._cache.clear()


# ══════════════════════════════════════════════════════════════════════
# Dimension projection: teacher (5120) → student (512)
# ══════════════════════════════════════════════════════════════════════

class TeacherProjection(nn.Module):
    """Projects teacher hidden states into student dimension space.

    One shared projection across all depths. The projection is trained
    during etch rounds (alongside beam params) so the student learns
    which dimensions of the teacher's representation matter most.

    Architecture: Linear(5120→512) with layer norm on output.
    No bias — the norm handles centering.
    """

    def __init__(self, d_teacher: int = 5120, d_student: int = 512):
        super().__init__()
        self.proj = nn.Linear(d_teacher, d_student, bias=False)
        self.norm = nn.RMSNorm(d_student)
        # Xavier init for stable gradient flow
        scale = math.sqrt(2.0 / (d_teacher + d_student))
        self.proj.weight = mx.random.normal(
            shape=(d_student, d_teacher)) * scale

    def __call__(self, x: mx.array) -> mx.array:
        """Project teacher hiddens: (*, d_teacher) → (*, d_student)."""
        return self.norm(self.proj(x))



# NOTE: forward_instrumented and distillation_loss were removed.
# The etch phase uses per-pass distillation (feeding projected teacher
# features through individual passes) rather than full-model forward.
# This is simpler, more memory-efficient, and matches mini_holo_distill.


# ══════════════════════════════════════════════════════════════════════
# Focusing schedule (reused from holographic_train.py)
# ══════════════════════════════════════════════════════════════════════

def focusing_schedule(
    round_idx: int,
    total_rounds: int,
    start_val: float,
    end_val: float,
) -> float:
    """Cosine annealing: slow start → fast middle → slow finish."""
    if total_rounds <= 1:
        return end_val
    progress = round_idx / (total_rounds - 1)
    cosine_factor = 0.5 * (1 + math.cos(math.pi * progress))
    return end_val + (start_val - end_val) * cosine_factor


# ══════════════════════════════════════════════════════════════════════
# Phase 1: Teacher-guided etch
# ══════════════════════════════════════════════════════════════════════

def run_etch_phase(
    model: V12Model,
    projection: TeacherProjection,
    teacher: TeacherFeatures,
    args: argparse.Namespace,
) -> list[dict]:
    """Etch ternary plates using teacher distillation loss.

    Per round:
      1. Reset accumulators
      2. For each probe: compute distillation loss, accumulate gradients
      3. Direct etch (flip confident positions)
      4. Train beam params + projection for beam_steps_per_round steps

    Returns: list of per-round log dicts.
    """
    n_rounds = args.n_etch_rounds
    probes_per_round = min(args.etch_probes_per_round, teacher.n_probes)
    beam_steps = args.beam_steps_per_round

    # Etch config
    conf_start = args.etch_confidence_start
    conf_end = args.etch_confidence_end
    max_flips_start = args.etch_max_flips_start
    max_flips_end = args.etch_max_flips_end

    log = []
    rng = np.random.RandomState(args.seed)

    # Beam optimizer: trains projection + continuous model params
    # Use separate param groups for projection vs model
    beam_lr = args.beam_lr
    beam_optimizer = optim.Adam(learning_rate=beam_lr)

    print(f"\n{'='*60}")
    print(f"  Phase 1: Teacher-Guided Etch")
    print(f"  Rounds: {n_rounds}")
    print(f"  Probes/round: {probes_per_round}")
    print(f"  Beam steps/round: {beam_steps}")
    print(f"  Confidence: {conf_start:.2f} → {conf_end:.2f}")
    print(f"  Max flips: {max_flips_start} → {max_flips_end}")
    print(f"{'='*60}\n")

    for round_idx in range(n_rounds):
        t_round = time.time()

        # Focusing schedule
        round_confidence = focusing_schedule(
            round_idx, n_rounds, conf_start, conf_end)
        round_max_flips = int(focusing_schedule(
            round_idx, n_rounds, max_flips_start, max_flips_end))

        # ── Accumulation phase ────────────────────────────────
        accumulators = init_direction_accumulators(model)
        reset_accumulators(accumulators)

        # Shuffle probe order each round
        probe_order = rng.permutation(teacher.n_probes)[:probes_per_round]

        total_distill_loss = 0.0
        n_loss_samples = 0

        for pi, probe_idx in enumerate(probe_order):
            # Load teacher outputs for all 8 depths (keep as numpy for closures)
            teacher_outputs_np = []
            for depth_idx in range(8):
                out = teacher.get_output(depth_idx, int(probe_idx))
                teacher_outputs_np.append(out)

            seq_len = teacher_outputs_np[0].shape[0]
            # We need token ids to run through the student model.
            # The teacher features were extracted from specific probes,
            # but we don't have the token ids here. Instead, we can use
            # the teacher INPUT at depth 0 (embedding output) as a proxy.
            # However, the V12 model needs actual token IDs for its embedding.
            #
            # Solution: Use dummy tokens and replace the embedding output.
            # OR: Store probe token IDs in manifest.
            #
            # Actually, the teacher features include layer 8 INPUT which is
            # the output of layers 0-7. We can't directly use this as V12 input.
            #
            # The correct approach: we don't need to match the EXACT same
            # tokens. The distillation loss matches REPRESENTATIONS, not tokens.
            # We feed dummy tokens through V12 to generate student hiddens,
            # then compare to teacher hiddens at corresponding depths.
            #
            # But wait — for the etch signal to be meaningful, the student
            # needs to process something that generates a meaningful hidden
            # state. Using dummy tokens would give garbage activations.
            #
            # Better approach: Instead of running the full V12 forward and
            # comparing per-pass outputs, we can do LAYER-WISE distillation:
            # feed the teacher input at each depth through the corresponding
            # V12 pass/component and match its output to the teacher output.
            # This is what mini_holo_distill does.
            #
            # However, V12's passes don't work in isolation — they depend on
            # banks, registers, etc. from previous passes.
            #
            # Simplest viable approach: Use the teacher's input at the FIRST
            # depth (L8) as a representation target for the V12 embedding,
            # then run the full forward and match pass outputs.
            #
            # Actually the cleanest approach: the GBNF/NPZ manifest should
            # have stored probe token IDs. Let's check if we can reconstruct
            # them from the probe texts in the manifest.

            # For now: use the distillation loss on the FINAL hidden state
            # only (hiddens[7] vs teacher L64 output), using probe text
            # tokens. This is the most tractable approach.
            #
            # UPDATE: We'll tokenize the probe texts on the fly, since the
            # manifest stores the first 10 texts and total_probes=500.
            # We need to regenerate/load them.
            #
            # PRACTICAL DECISION: Store tokenized probe IDs during etch.
            # For now, we match representation geometry using a different
            # approach — we compute a per-pass "representation alignment"
            # loss using a differentiable proxy.

            # === REVISED CLEAN APPROACH ===
            # Feed teacher hidden states DIRECTLY through a per-depth loss.
            # The student model's ternary plates need gradients w.r.t. their
            # impact on representation space. We can compute:
            #
            # For each depth d:
            #   loss_d = MSE(projection(teacher_output_d), target_d)
            #
            # Where target_d is what we WANT the student to produce at pass d.
            # This simplifies to: the etch signal says "these plate signs
            # should produce outputs closer to the teacher's representations."
            #
            # The trick from mini_holo_distill: feed teacher INPUT through
            # the student layer, compare OUTPUT to teacher OUTPUT. This works
            # because each layer/pass is a local function.
            #
            # For V12: each pass is complex (dispatch → stride → integrate),
            # but we can still feed projected teacher input as x and compare
            # the output. The pass WILL use the model's internal state
            # (banks, etc.) which won't be meaningful, but the gradient
            # signal through the ternary plates is still valid — it says
            # "given this input pattern, which plate signs produce the
            # closest output to the teacher's computation?"

            # Per-depth distillation: feed projected teacher input through
            # each V12 pass independently.
            for depth_idx in range(min(8, N_PASS_DEPTHS + N_OUTPUT_DEPTH)):
                teacher_in_np = teacher.get_input(depth_idx, int(probe_idx))
                teacher_out_np = teacher_outputs_np[depth_idx]

                # Capture depth_idx in closure
                _depth = depth_idx

                def _distill_step(model, _d=_depth):
                    t_in = mx.array(teacher_in_np)     # (T, 5120)
                    t_out = mx.array(teacher_out_np)   # (T, 5120)

                    proj_in = projection(t_in)         # (T, 512)
                    proj_out = projection(t_out)        # (T, 512)

                    x_in = proj_in[None, :, :]         # (1, T, 512)

                    if _d < N_PASS_DEPTHS:
                        pass_idx = _d
                        is_desc = pass_idx >= 4

                        # Build readable banks with correct count per pass
                        # Pass 0: [bank_0, prev_b1d, prev_kernel] → 3
                        # Pass 1: [bank_0, b1_asc, prev_b2d, prev_kernel] → 4
                        # Pass 2: [bank_0, b1_asc, b2_asc, prev_b3d, prev_kernel] → 5
                        # Pass 3: [bank_0, b1_asc, b2_asc, b3_asc, prev_kernel] → 5
                        # Pass 4: [bank_0, b1_asc, b2_asc, b3_asc, b4_apex, asc_gate] → 6
                        # Pass 5: [bank_0, b1_asc, b3_desc, b4_apex, asc_gate] → 5
                        # Pass 6: [bank_0, b1_asc, b2_desc, b4_apex, asc_gate] → 5
                        n_banks = {0: 3, 1: 4, 2: 5, 3: 5,
                                   4: 6, 5: 5, 6: 5}[pass_idx]
                        readable = [model._init_bank0()]
                        for _ in range(n_banks - 1):
                            readable.append(model._fresh_bank())

                        bank = model._fresh_bank()
                        ret_regs = model._init_retrieval_registers()

                        x_out, *_ = model._run_level_pass(
                            x_in, pass_idx, is_desc,
                            readable, bank,
                            ret_regs=ret_regs)
                        student_out = x_out.squeeze(0)
                    else:
                        student_out = model.output_norm(x_in).squeeze(0)

                    diff = student_out - proj_out
                    return (diff * diff).mean()

                loss_fn = nn.value_and_grad(model, _distill_step)
                loss_val, grads = loss_fn(model)
                mx.eval(loss_val, grads)

                accumulate_direction(model, grads, accumulators)

                total_distill_loss += loss_val.item()
                n_loss_samples += 1

                del loss_val, grads

            if (pi + 1) % 50 == 0 or pi == len(probe_order) - 1:
                avg_loss = total_distill_loss / max(n_loss_samples, 1)
                print(f"  Round {round_idx+1}/{n_rounds} — "
                      f"probe {pi+1}/{len(probe_order)} — "
                      f"avg distill loss: {avg_loss:.6f}")

            # Clear cache periodically
            if (pi + 1) % 25 == 0:
                mx.clear_cache()

        # ── Etch phase ────────────────────────────────────────
        etch_result = direct_etch(
            model, accumulators,
            confidence_threshold=round_confidence,
            max_flips=round_max_flips if round_max_flips > 0 else None,
        )
        freeze_ternary_weights(model)
        restore_ternary(model)

        total_flips = etch_result.get("total_flipped", 0)
        total_candidates = etch_result.get("total_candidates", 0)

        mx.clear_cache()

        # ── Beam training phase (projection + continuous params) ──
        # Retrain beam params after etch to adapt to new plate topology
        if beam_steps > 0:
            beam_loss_sum = 0.0
            beam_loss_n = 0

            # Separate optimizers for model and projection
            proj_optimizer = optim.Adam(learning_rate=beam_lr)

            for step in range(beam_steps):
                # Random probe and depth
                p_idx = int(rng.randint(0, teacher.n_probes))
                d_idx = int(rng.randint(0, 8))

                t_in_np = teacher.get_input(d_idx, p_idx)
                t_out_np = teacher.get_output(d_idx, p_idx)

                _d = d_idx  # capture for closure

                def _beam_loss_model(model, _dd=_d):
                    t_in = mx.array(t_in_np)
                    t_out = mx.array(t_out_np)
                    proj_in = projection(t_in)
                    proj_out = projection(t_out)
                    x_in = proj_in[None, :, :]

                    if _dd < N_PASS_DEPTHS:
                        pass_idx = _dd
                        is_desc = pass_idx >= 4
                        n_banks = {0: 3, 1: 4, 2: 5, 3: 5,
                                   4: 6, 5: 5, 6: 5}[pass_idx]
                        readable = [model._init_bank0()]
                        for _ in range(n_banks - 1):
                            readable.append(model._fresh_bank())
                        bank = model._fresh_bank()
                        ret_regs = model._init_retrieval_registers()
                        x_out, *_ = model._run_level_pass(
                            x_in, pass_idx, is_desc,
                            readable, bank, ret_regs=ret_regs)
                        student_out = x_out.squeeze(0)
                    else:
                        student_out = model.output_norm(x_in).squeeze(0)

                    diff = student_out - proj_out
                    return (diff * diff).mean()

                # Model gradients
                loss_fn = nn.value_and_grad(model, _beam_loss_model)
                loss_val, model_grads = loss_fn(model)
                mx.eval(loss_val, model_grads)

                # Zero ternary grads — only train beam params
                model_grads = zero_ternary_grads(model, model_grads)
                beam_optimizer.update(model, model_grads)
                mx.eval(model.parameters(), beam_optimizer.state)
                restore_ternary(model)

                # Projection gradients (separate backward pass)
                def _beam_loss_proj(proj, _dd=_d):
                    t_in = mx.array(t_in_np)
                    t_out = mx.array(t_out_np)
                    proj_in = proj(t_in)
                    proj_out = proj(t_out)
                    x_in = proj_in[None, :, :]

                    if _dd < N_PASS_DEPTHS:
                        pass_idx = _dd
                        is_desc = pass_idx >= 4
                        n_banks = {0: 3, 1: 4, 2: 5, 3: 5,
                                   4: 6, 5: 5, 6: 5}[pass_idx]
                        readable = [model._init_bank0()]
                        for _ in range(n_banks - 1):
                            readable.append(model._fresh_bank())
                        bank = model._fresh_bank()
                        ret_regs = model._init_retrieval_registers()
                        x_out, *_ = model._run_level_pass(
                            x_in, pass_idx, is_desc,
                            readable, bank, ret_regs=ret_regs)
                        student_out = x_out.squeeze(0)
                    else:
                        student_out = model.output_norm(x_in).squeeze(0)

                    diff = student_out - proj_out
                    return (diff * diff).mean()

                proj_loss_fn = nn.value_and_grad(projection, _beam_loss_proj)
                _, proj_grads = proj_loss_fn(projection)
                mx.eval(proj_grads)

                proj_optimizer.update(projection, proj_grads)
                mx.eval(projection.parameters(), proj_optimizer.state)

                beam_loss_sum += loss_val.item()
                beam_loss_n += 1

                del loss_val, model_grads, proj_grads

                if (step + 1) % 50 == 0:
                    mx.clear_cache()

            avg_beam_loss = beam_loss_sum / max(beam_loss_n, 1)
        else:
            avg_beam_loss = 0.0

        mx.clear_cache()

        # ── Log ───────────────────────────────────────────────
        avg_distill = total_distill_loss / max(n_loss_samples, 1)
        elapsed = time.time() - t_round

        round_log = {
            "round": round_idx + 1,
            "distill_loss": avg_distill,
            "beam_loss": avg_beam_loss,
            "flips": total_flips,
            "candidates": total_candidates,
            "confidence_threshold": round_confidence,
            "max_flips": round_max_flips,
            "elapsed_s": elapsed,
        }
        log.append(round_log)

        print(f"\n  Round {round_idx+1}/{n_rounds} complete:")
        print(f"    Distill loss: {avg_distill:.6f}")
        print(f"    Beam loss:    {avg_beam_loss:.6f}")
        print(f"    Flips:        {total_flips:,} / {total_candidates:,} candidates")
        print(f"    Confidence:   {round_confidence:.3f}")
        print(f"    Time:         {elapsed:.1f}s\n")

        # Save etch checkpoint
        if args.checkpoint_dir:
            ckpt_dir = Path(args.checkpoint_dir) / f"etch_round_{round_idx+1:03d}"
            ckpt_dir.mkdir(parents=True, exist_ok=True)
            flat = dict(tree_flatten(model.parameters()))
            mx.savez(str(ckpt_dir / "weights.npz"), **flat)
            proj_flat = dict(tree_flatten(projection.parameters()))
            mx.savez(str(ckpt_dir / "projection.npz"), **proj_flat)
            with open(ckpt_dir / "state.json", "w") as f:
                json.dump(round_log, f, indent=2)

    return log


# ══════════════════════════════════════════════════════════════════════
# Phase 2: Extended GD (frozen plates, CE loss)
# ══════════════════════════════════════════════════════════════════════

def cosine_lr_schedule(
    step: int,
    total_steps: int,
    lr_max: float,
    lr_min: float,
    warmup_steps: int,
) -> float:
    """Cosine LR with linear warmup."""
    if step < warmup_steps:
        return lr_max * step / max(warmup_steps, 1)
    progress = (step - warmup_steps) / max(total_steps - warmup_steps, 1)
    return lr_min + 0.5 * (lr_max - lr_min) * (1 + math.cos(math.pi * progress))


def run_gd_phase(
    model: V12Model,
    args: argparse.Namespace,
) -> list[dict]:
    """Extended GD on frozen plates using CE loss.

    Trains continuous params on structured_shard_v2 + Dolma.
    """
    total_steps = args.gd_steps
    if total_steps <= 0:
        print("Skipping GD phase (--gd-steps 0)")
        return []

    # Verify plates are frozen
    n_frozen = freeze_ternary_weights(model)
    restore_ternary(model)
    print(f"\n{'='*60}")
    print(f"  Phase 2: Extended GD (frozen plates)")
    print(f"  Steps: {total_steps}")
    print(f"  Frozen modules: {n_frozen}")
    print(f"  LR: {args.gd_lr} → {args.gd_lr_min}")
    print(f"  Warmup: {args.gd_warmup} steps")
    print(f"  Batch size: {args.batch_size}")
    print(f"  Seq len: {args.seq_len}")
    print(f"  Mix ratio (structured): {args.mix_ratio}")
    print(f"{'='*60}\n")

    # Data loaders
    prose_loader = ShardedDataLoader(
        data_dir=args.data_dir,
        batch_size=args.batch_size,
        seq_len=args.seq_len,
        shard_start=0,
        shard_end=args.n_train_shards,
        seed=args.seed,
    )

    if args.structured_path and Path(args.structured_path).exists():
        data_loader = MixedDataLoader(
            prose_loader=prose_loader,
            structured_path=args.structured_path,
            mix_ratio=args.mix_ratio,
            seq_len=args.seq_len,
            batch_size=args.batch_size,
            seed=args.seed,
        )
        print(f"  Using MixedDataLoader (structured + prose)")
    else:
        data_loader = prose_loader
        print(f"  Using prose-only ShardedDataLoader")

    # Eval loader (separate shards)
    eval_loader = ShardedDataLoader(
        data_dir=args.data_dir,
        batch_size=args.batch_size,
        seq_len=args.seq_len,
        shard_start=args.n_train_shards,
        shard_end=args.n_train_shards + args.n_eval_shards,
        seed=args.seed + 1,
    )

    # Optimizer
    optimizer = optim.AdamW(
        learning_rate=args.gd_lr,
        weight_decay=args.weight_decay,
    )

    # Loss function
    def ce_loss(model, input_ids, targets):
        logits, loss = model(input_ids, targets=targets)
        return loss

    loss_and_grad = nn.value_and_grad(model, ce_loss)

    log = []
    best_eval_loss = float("inf")
    loss_ema = None

    t0 = time.time()

    for step in range(total_steps):
        # LR schedule
        lr = cosine_lr_schedule(
            step, total_steps,
            args.gd_lr, args.gd_lr_min, args.gd_warmup)
        optimizer.learning_rate = mx.array(lr)

        # Forward + backward
        input_ids_np, targets_np = data_loader.next_batch()
        input_ids = mx.array(input_ids_np)
        targets = mx.array(targets_np)

        loss_val, grads = loss_and_grad(model, input_ids, targets)
        mx.eval(loss_val, grads)

        # Zero ternary grads (plates are frozen)
        grads = zero_ternary_grads(model, grads)

        # Gradient clipping
        grad_sq = [mx.sum(g * g) for _, g in tree_flatten(grads)]
        mx.eval(*grad_sq)
        grad_norm = sum(float(g) for g in grad_sq) ** 0.5
        if args.grad_clip > 0 and grad_norm > args.grad_clip:
            s = args.grad_clip / (grad_norm + 1e-8)
            grads = tree_map(lambda g: g * s, grads)

        optimizer.update(model, grads)
        mx.eval(model.parameters(), optimizer.state)
        restore_ternary(model)

        loss_item = loss_val.item()
        loss_ema = loss_item if loss_ema is None else 0.99 * loss_ema + 0.01 * loss_item

        del loss_val, grads, input_ids, targets

        # Logging
        if (step + 1) % args.log_every == 0:
            elapsed = time.time() - t0
            tok_per_sec = (step + 1) * args.batch_size * args.seq_len / elapsed
            print(f"  Step {step+1:6d}/{total_steps} | "
                  f"loss {loss_ema:.4f} | lr {lr:.2e} | "
                  f"gnorm {grad_norm:.2f} | "
                  f"{tok_per_sec:.0f} tok/s | "
                  f"{elapsed:.0f}s")

        # Eval
        if (step + 1) % args.eval_every == 0:
            eval_loss = _run_eval(model, eval_loader, args.eval_batches)
            is_best = eval_loss < best_eval_loss
            if is_best:
                best_eval_loss = eval_loss
            print(f"  ── Eval step {step+1}: loss {eval_loss:.4f}"
                  f"{' ★ best' if is_best else ''}")

            step_log = {
                "step": step + 1,
                "train_loss_ema": loss_ema,
                "eval_loss": eval_loss,
                "lr": lr,
                "grad_norm": grad_norm,
                "elapsed_s": time.time() - t0,
            }
            log.append(step_log)

            # Checkpoint
            if is_best and args.checkpoint_dir:
                ckpt_dir = Path(args.checkpoint_dir) / "best"
                ckpt_dir.mkdir(parents=True, exist_ok=True)
                flat = dict(tree_flatten(model.parameters()))
                mx.savez(str(ckpt_dir / "weights.npz"), **flat)
                with open(ckpt_dir / "state.json", "w") as f:
                    json.dump(step_log, f, indent=2)
                print(f"  ── Saved best checkpoint (eval {eval_loss:.4f})")

        # Periodic checkpoint
        if (step + 1) % args.checkpoint_every == 0 and args.checkpoint_dir:
            ckpt_dir = Path(args.checkpoint_dir) / f"step_{step+1:06d}"
            ckpt_dir.mkdir(parents=True, exist_ok=True)
            flat = dict(tree_flatten(model.parameters()))
            mx.savez(str(ckpt_dir / "weights.npz"), **flat)
            loader_state = data_loader.save_state() if hasattr(data_loader, 'save_state') else {}
            with open(ckpt_dir / "state.json", "w") as f:
                json.dump({
                    "step": step + 1,
                    "train_loss_ema": loss_ema,
                    "lr": lr,
                    "loader_state": loader_state,
                }, f, indent=2)

        # Clear cache periodically
        if (step + 1) % 50 == 0:
            mx.clear_cache()

    # Final checkpoint
    if args.checkpoint_dir:
        ckpt_dir = Path(args.checkpoint_dir) / "final"
        ckpt_dir.mkdir(parents=True, exist_ok=True)
        flat = dict(tree_flatten(model.parameters()))
        mx.savez(str(ckpt_dir / "weights.npz"), **flat)
        loader_state = data_loader.save_state() if hasattr(data_loader, 'save_state') else {}
        with open(ckpt_dir / "state.json", "w") as f:
            json.dump({
                "step": total_steps,
                "train_loss_ema": loss_ema,
                "best_eval_loss": best_eval_loss,
                "loader_state": loader_state,
            }, f, indent=2)
        print(f"\n  Final checkpoint saved to {ckpt_dir}")

    return log


def _run_eval(
    model: V12Model,
    eval_loader: ShardedDataLoader,
    n_batches: int = 10,
) -> float:
    """Run eval and return mean CE loss."""
    total_loss = 0.0
    for _ in range(n_batches):
        input_ids_np, targets_np = eval_loader.next_batch()
        input_ids = mx.array(input_ids_np)
        targets = mx.array(targets_np)

        logits, loss = model(input_ids, targets=targets)
        mx.eval(loss)
        total_loss += loss.item()

        del logits, loss, input_ids, targets

    mx.clear_cache()
    return total_loss / n_batches


# ══════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Holographic Distillation V12 — teacher-guided etch + extended GD")

    # Paths
    p.add_argument("--teacher-features", type=str,
                   default="checkpoints/teacher-features",
                   help="Directory with teacher NPZ features + manifest.json")
    p.add_argument("--checkpoint-dir", type=str,
                   default="checkpoints/v12-distill",
                   help="Output checkpoint directory")
    p.add_argument("--load-weights", type=str, default=None,
                   help="Load model weights from .npz (for resuming)")

    # Phase 1: Etch
    p.add_argument("--n-etch-rounds", type=int, default=5,
                   help="Number of etch rounds")
    p.add_argument("--etch-probes-per-round", type=int, default=500,
                   help="Probes to use per etch round")
    p.add_argument("--beam-steps-per-round", type=int, default=200,
                   help="Beam GD steps per etch round")
    p.add_argument("--beam-lr", type=float, default=1e-4,
                   help="Beam/projection learning rate during etch")
    p.add_argument("--etch-confidence-start", type=float, default=0.5,
                   help="Etch confidence threshold (start)")
    p.add_argument("--etch-confidence-end", type=float, default=0.9,
                   help="Etch confidence threshold (end)")
    p.add_argument("--etch-max-flips-start", type=int, default=0,
                   help="Max flips per etch (start, 0=unlimited)")
    p.add_argument("--etch-max-flips-end", type=int, default=100,
                   help="Max flips per etch (end)")

    # Phase 2: Extended GD
    p.add_argument("--gd-steps", type=int, default=20000,
                   help="Total GD steps after freeze")
    p.add_argument("--gd-lr", type=float, default=6e-4,
                   help="Peak learning rate for GD")
    p.add_argument("--gd-lr-min", type=float, default=6e-6,
                   help="Minimum learning rate for GD")
    p.add_argument("--gd-warmup", type=int, default=500,
                   help="Warmup steps for GD")
    p.add_argument("--weight-decay", type=float, default=0.01,
                   help="Weight decay for AdamW")
    p.add_argument("--grad-clip", type=float, default=1.0,
                   help="Gradient norm clipping")

    # Data
    p.add_argument("--data-dir", type=str,
                   default="/Users/mwhitford/data/fractal-bitnet/shards-qwen3",
                   help="Dolma shard directory")
    p.add_argument("--structured-path", type=str,
                   default="data/structured_shard_v2.npy",
                   help="Path to structured shard")
    p.add_argument("--mix-ratio", type=float, default=0.1,
                   help="Structured data mix ratio")
    p.add_argument("--batch-size", type=int, default=2,
                   help="Batch size for GD")
    p.add_argument("--seq-len", type=int, default=2048,
                   help="Sequence length for GD")
    p.add_argument("--n-train-shards", type=int, default=54)
    p.add_argument("--n-eval-shards", type=int, default=6)

    # Logging
    p.add_argument("--log-every", type=int, default=10,
                   help="Log every N steps")
    p.add_argument("--eval-every", type=int, default=500,
                   help="Eval every N steps")
    p.add_argument("--eval-batches", type=int, default=10,
                   help="Eval batches per eval")
    p.add_argument("--checkpoint-every", type=int, default=2000,
                   help="Checkpoint every N GD steps")

    # General
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--skip-etch", action="store_true",
                   help="Skip etch phase (load weights and go to GD)")
    p.add_argument("--skip-gd", action="store_true",
                   help="Skip GD phase (etch only)")

    return p.parse_args()


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    args = parse_args()

    # Create output directory
    ckpt_dir = Path(args.checkpoint_dir)
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    # Save args
    with open(ckpt_dir / "args.json", "w") as f:
        json.dump(vars(args), f, indent=2)

    print(f"\n{'='*60}")
    print(f"  Holographic Distillation V12")
    print(f"  Checkpoint dir: {ckpt_dir}")
    print(f"{'='*60}")

    # ── Create model ──────────────────────────────────────────
    cfg = V12Config()
    cfg.seq_len = args.seq_len
    cfg.batch_size = args.batch_size

    print(f"\nCreating V12 model...")
    model = create_model(cfg)

    if args.load_weights:
        print(f"  Loading weights from {args.load_weights}")
        weights = mx.load(args.load_weights)
        model.load_weights(list(weights.items()), strict=False)

    freeze_ternary_weights(model)
    restore_ternary(model)

    params = count_parameters(model)
    print(f"  Parameters: {params['total']:,} total, {params['trainable']:,} trainable")

    # ── Phase 1: Etch ─────────────────────────────────────────
    if not args.skip_etch:
        # Load teacher features
        print(f"\nLoading teacher features from {args.teacher_features}...")
        teacher = TeacherFeatures(args.teacher_features)
        print(f"  Probes: {teacher.n_probes}, d_teacher: {teacher.d_teacher}")
        print(f"  Depths: {teacher.depth_indices}")

        # Create projection
        projection = TeacherProjection(
            d_teacher=teacher.d_teacher,
            d_student=cfg.d_model,
        )
        mx.eval(projection.parameters())

        # Run etch
        etch_log = run_etch_phase(model, projection, teacher, args)

        # Save etch summary
        with open(ckpt_dir / "etch_log.json", "w") as f:
            json.dump(etch_log, f, indent=2)

        teacher.close()
        print(f"\nEtch phase complete. {len(etch_log)} rounds.")
    else:
        print("\nSkipping etch phase (--skip-etch)")

    # Ensure plates are frozen for GD
    freeze_ternary_weights(model)
    restore_ternary(model)

    # ── Phase 2: Extended GD ──────────────────────────────────
    if not args.skip_gd:
        gd_log = run_gd_phase(model, args)

        # Save GD summary
        with open(ckpt_dir / "gd_log.json", "w") as f:
            json.dump(gd_log, f, indent=2)

        print(f"\nGD phase complete. {len(gd_log)} eval points logged.")
    else:
        print("\nSkipping GD phase (--skip-gd)")

    print(f"\n{'='*60}")
    print(f"  Training complete!")
    print(f"  Checkpoints in: {ckpt_dir}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
