"""
v13 — Reference Beam Training Script (knowledge distillation via teacher logits)

Session 143: The teacher is the reference beam. In holography, you cannot
record without a reference beam — the object beam alone gives intensity
(hard target: which token is right) but loses phase (teacher's distribution
over all tokens — the dark knowledge about similarity structure).

Architecture:
  - Teacher:     Qwen3-32B loaded via mlx-lm, eval mode, no gradients
  - Student:     V13Model with base plates frozen + fresh delta plates
  - Base plates:  full teacher crystal etch, FROZEN (same as train_td)
  - Delta plates: initialized +1 (pass-through), trained by Adam
  - Reference beam: teacher logits on each training batch

Training loop:
  1. Feed Dolma batch to teacher → reference logits (full vocab distribution)
  2. Feed same batch to student → student logits
  3. Loss = α * CE(student, hard_target) + (1-α) * KD(student, teacher, T) + crystal + parity
  4. Backprop through student only, Adam updates beams
  5. TD activates when crystal latches (same Schmitt trigger as train_td)

The KD loss:
  KL(softmax(student/T) || softmax(teacher/T)) * T²
  T = temperature. Higher T → softer distributions → more dark knowledge.
  T² scaling ensures gradient magnitudes match between CE and KD terms
  (Hinton et al. 2015).

The reference beam provides the PHASE information that the ternary etch
can't carry. The teacher's distribution implicitly encodes type structure
(tokens of the same combinator type get similar probabilities), so the
reference beam REINFORCES the crystal — it's aligned with the geometry losses.

Pipeline:
  1. extract_teacher.py → frozen plates (base)
  2. train_rb.py --resume <etched-checkpoint> → reference beam training
  3. Compare delta plates with train_td's delta plates

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from collections import deque
from pathlib import Path

os.environ["PYTHONUNBUFFERED"] = "1"

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np
from mlx.utils import tree_flatten, tree_map, tree_unflatten

sys.path.insert(0, str(Path(__file__).parent))

from config import V13Config
from data import ShardedDataLoader, MixedDataLoader
from model import V13Model, crystal_lattice_loss
from ternary import (
    TernaryLinear,
    freeze_ternary_weights,
    zero_ternary_grads,
    restore_ternary,
    count_ternary_weights,
    unpack_ternary_mlx,
    surgical_adam_decay_for_etch,
)
from td import (
    TernaryDescent,
    DeltaTernaryLinear,
    convert_to_delta,
    collect_delta_params,
    reduce_all_deltas,
    freeze_delta_architecture,
    decompose_gradient,
    compute_routing_fraction,
)


# ══════════════════════════════════════════════════════════════════════════════
# § 1  Reference Beam Loss
# ══════════════════════════════════════════════════════════════════════════════


def reference_beam_loss(
    student_logits: mx.array,
    teacher_logits: mx.array,
    targets: mx.array,
    temperature: float = 2.0,
    alpha: float = 0.5,
) -> tuple[mx.array, mx.array, mx.array]:
    """Combined hard-target CE + soft-target KD loss.

    The teacher's softened distribution IS the reference beam.
    The KL divergence IS the interference pattern.
    Temperature T IS beam coherence.

    Args:
        student_logits: (B, L, V) raw logits from student
        teacher_logits: (B, L, V) raw logits from teacher (detached)
        targets: (B, L) hard target token IDs
        temperature: softening temperature (higher = more dark knowledge)
        alpha: weight for hard CE (1-alpha for KD). 0.5 = equal weight.

    Returns:
        combined_loss: α * CE + (1-α) * KD
        ce_loss: hard-target cross-entropy (for logging)
        kd_loss: soft-target KL divergence (for logging)
    """
    B, L, V = student_logits.shape

    # Hard-target CE
    ce_loss = nn.losses.cross_entropy(
        student_logits.reshape(-1, V),
        targets.reshape(-1),
    ).mean()

    # Soft-target KD: KL(student_soft || teacher_soft) * T²
    # teacher_logits are already detached (computed under mx.no_grad)
    student_log_probs = mx.softmax(student_logits / temperature, axis=-1)
    student_log_probs = mx.log(student_log_probs + 1e-10)
    teacher_probs = mx.softmax(teacher_logits / temperature, axis=-1)

    # KL divergence: sum_v teacher_v * (log(teacher_v) - log(student_v))
    # = sum_v teacher_v * log(teacher_v / student_v)
    kl = teacher_probs * (mx.log(teacher_probs + 1e-10) - student_log_probs)
    kd_loss = mx.mean(mx.sum(kl, axis=-1))  # mean over (B*L), sum over V

    # T² scaling: ensures gradient magnitudes match between CE and KD
    kd_loss = kd_loss * (temperature ** 2)

    # Combined: object beam + reference beam
    combined = alpha * ce_loss + (1.0 - alpha) * kd_loss

    return combined, ce_loss, kd_loss


# ══════════════════════════════════════════════════════════════════════════════
# § 2  Loss with crystal + parity + reference beam
# ══════════════════════════════════════════════════════════════════════════════


def loss_fn_rb(
    model: V13Model,
    input_ids: mx.array,
    targets: mx.array,
    teacher_top_k_indices: mx.array,
    teacher_top_k_logits: mx.array,
    temperature: float = 2.0,
    alpha: float = 0.5,
) -> mx.array:
    """Full loss: reference beam (top-k KD) + crystal + parity + geometry.

    Uses SPARSE top-k KD: instead of softmax + KL over full 151936-dim
    vocab, we compute KL only over the teacher's top-k tokens. This is
    O(B*L*k) instead of O(B*L*V) in both forward and backward — ~2000×
    cheaper for k=64, V=151936.

    The teacher's top-k captures 99%+ of probability mass and all the
    "dark knowledge" (relative ranking of plausible completions).

    Args:
        teacher_top_k_indices: (B, L, k) int32 — teacher's top-k token IDs
        teacher_top_k_logits: (B, L, k) float — teacher's scaled logits for those tokens

    Returns:
        total_loss: for backprop (internal_loss + alpha * KD)
    """
    # Run student forward with targets — get full internal loss
    # (CE * crystal_factor * holo_factor + crystal_additive + geometry + parity)
    student_logits, internal_loss = model(input_ids, targets)

    # ── Top-k KD loss ─────────────────────────────────────────
    # Teacher: softmax over top-k logits (already scaled by 1/T)
    teacher_probs_k = mx.softmax(teacher_top_k_logits, axis=-1)  # (B, L, k)

    # Student: gather logits for the same top-k tokens, scale by 1/T
    # student_logits is (B, L, V) — gather at teacher's top-k indices
    student_logits_scaled = student_logits / temperature  # (B, L, V)
    student_top_k = mx.take_along_axis(student_logits_scaled, teacher_top_k_indices, axis=-1)  # (B, L, k)

    # Student log-softmax over just the top-k slice
    # This is an approximation: we normalize over k tokens, not V.
    # The approximation is tight when k captures most of the mass.
    student_log_probs_k = student_top_k - mx.logsumexp(student_top_k, axis=-1, keepdims=True)  # (B, L, k)

    # KL(teacher_k || student_k) = sum_i teacher_i * (log(teacher_i) - log(student_i))
    kl = teacher_probs_k * (mx.log(teacher_probs_k + 1e-10) - student_log_probs_k)
    kd_loss = mx.mean(mx.sum(kl, axis=-1)) * (temperature ** 2)

    # Combined: internal loss + reference beam
    total_loss = internal_loss + alpha * kd_loss

    # Cache for logging
    model._last_kd_loss = mx.stop_gradient(kd_loss)

    return total_loss


# ══════════════════════════════════════════════════════════════════════════════
# § 3  Utilities (shared with train_td.py)
# ══════════════════════════════════════════════════════════════════════════════


def cosine_lr(step, warmup_steps, total_steps, lr_max, lr_floor_ratio=0.01):
    if step < warmup_steps:
        return lr_max * step / max(warmup_steps, 1)
    progress = (step - warmup_steps) / max(total_steps - warmup_steps, 1)
    floor = lr_max * lr_floor_ratio
    return floor + (lr_max - floor) * 0.5 * (1.0 + math.cos(math.pi * progress))


def _sanitize(obj):
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize(v) for v in obj]
    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else obj
    if hasattr(obj, "item"):
        v = obj.item()
        return None if isinstance(v, float) and (math.isnan(v) or math.isinf(v)) else v
    return obj


def _append_jsonl(path, record):
    with open(path, "a") as f:
        f.write(json.dumps(_sanitize(record)) + "\n")


# ══════════════════════════════════════════════════════════════════════════════
# § 4  Model setup (same delta architecture as train_td)
# ══════════════════════════════════════════════════════════════════════════════

def create_model_with_deltas(
    cfg: V13Config,
    convert_attention: bool = True,
    convert_ffn: bool = False,
) -> tuple[V13Model, list[tuple[str, DeltaTernaryLinear]]]:
    """Create V13Model, convert to delta plates. Same as train_td."""
    model = V13Model(cfg)
    freeze_ternary_weights(model)

    include = []
    exclude = []
    if convert_attention:
        include.append("stride_stack")
    if convert_ffn:
        include.append("ffn_key_plate")
        include.append("ffn_value_plate")
    if not convert_attention:
        exclude.append("stride_stack")
    if not convert_ffn:
        exclude.append("ffn_key_plate")
        exclude.append("ffn_value_plate")

    converted = convert_to_delta(
        model,
        include_prefixes=tuple(include) if include else None,
        exclude_prefixes=tuple(exclude) if exclude else None,
    )
    freeze_delta_architecture(model)
    freeze_ternary_weights(model)

    return model, converted


# Shared-weight gradient normalization (same as train_td)
_UNIVERSAL_SHARED = ("ffn_key_plate", "ffn_value_plate")
_N_ALL_PASSES = 8


def normalize_shared_grads(grads):
    all_scale = 1.0 / _N_ALL_PASSES

    def _walk(tree, keys):
        if isinstance(tree, dict):
            out = {}
            for k, v in tree.items():
                new_keys = keys + [k]
                root = new_keys[0] if new_keys else ""
                if root in _UNIVERSAL_SHARED:
                    out[k] = tree_map(lambda g: g * all_scale, v)
                else:
                    out[k] = _walk(v, new_keys)
            return out
        elif isinstance(tree, list):
            return [_walk(v, keys + [str(i)]) for i, v in enumerate(tree)]
        return tree

    return _walk(grads, [])


# ══════════════════════════════════════════════════════════════════════════════
# § 5  Teacher loading
# ══════════════════════════════════════════════════════════════════════════════


def load_teacher(teacher_model: str = "Qwen/Qwen3-32B") -> nn.Module:
    """Load teacher model via mlx-lm. Returns MLX nn.Module in eval mode.

    The teacher lives in the same unified memory as the student.
    No quantization — full fp16 for a clean reference beam.
    With 480GB unified memory, Qwen3-32B at fp16 (~64GB) is trivial.
    """
    import mlx_lm

    print(f"🔬 Loading teacher: {teacher_model} ...", file=sys.stderr)
    t0 = time.time()
    teacher, _tokenizer = mlx_lm.load(teacher_model)
    teacher.eval()
    # Freeze all teacher parameters
    teacher.freeze()
    dt = time.time() - t0
    print(f"✅ Teacher loaded in {dt:.1f}s", file=sys.stderr)

    return teacher


def teacher_forward(
    teacher: nn.Module,
    input_ids: mx.array,
    temperature: float = 2.0,
    top_k: int = 64,
) -> tuple[mx.array, mx.array]:
    """Run teacher forward pass, return top-k token indices and softened logits.

    Returns SPARSE representation: (top_k_indices, top_k_logits).
    Full-vocab softmax + KL over 151936 dims is catastrophically expensive
    in the backward pass. Top-k captures 99%+ of the teacher's probability
    mass and all the "dark knowledge" (relative ranking of plausible tokens).

    The logits (not probs) are returned so that the student loss function
    can compute the KL efficiently over just the top-k slice.

    Args:
        teacher: loaded mlx-lm model
        input_ids: (B, L) token IDs
        temperature: softening temperature
        top_k: number of top tokens to keep (default: 64)

    Returns:
        top_k_indices: (B, L, top_k) int32 — which tokens
        top_k_logits: (B, L, top_k) float — teacher's logits for those tokens
    """
    # Teacher forward (no gradients needed)
    logits = teacher(input_ids)
    mx.eval(logits)

    # Extract top-k: the reference beam is sparse
    # Softened logits (divide by T before top-k to get correct ranking)
    scaled_logits = logits / temperature

    # Top-k selection
    top_k_indices = mx.argpartition(scaled_logits, kth=scaled_logits.shape[-1] - top_k, axis=-1)[..., -top_k:]
    # Gather the logits for top-k tokens
    # argpartition doesn't sort, so we need to sort within top-k
    top_k_logits_unsorted = mx.take_along_axis(scaled_logits, top_k_indices, axis=-1)
    # Sort descending within top-k for stable computation
    sort_idx = mx.argsort(top_k_logits_unsorted, axis=-1)
    sort_idx = sort_idx[..., ::-1]  # descending
    top_k_indices = mx.take_along_axis(top_k_indices, sort_idx, axis=-1)
    top_k_logits_sorted = mx.take_along_axis(top_k_logits_unsorted, sort_idx, axis=-1)

    mx.eval(top_k_indices, top_k_logits_sorted)
    top_k_indices = mx.stop_gradient(top_k_indices)
    top_k_logits_sorted = mx.stop_gradient(top_k_logits_sorted)

    return top_k_indices, top_k_logits_sorted


# ══════════════════════════════════════════════════════════════════════════════
# § 6  Training loop — Reference Beam + Delta Plates
# ══════════════════════════════════════════════════════════════════════════════


def train_rb(
    cfg: V13Config,
    args: argparse.Namespace,
    model: V13Model,
    teacher: nn.Module,
    delta_modules: list[tuple[str, DeltaTernaryLinear]],
    start_step: int,
    train_loader,
    checkpoint_dir: Path,
) -> None:
    """Training loop: Adam (beams) + Reference Beam (teacher logits).

    Same delta plate architecture as train_td. The key difference:
    loss includes KL divergence against teacher's softened distribution.

    TD (TernaryDescent) can optionally run alongside, gated by crystal
    loss same as train_td. Disabled by default for clean comparison.
    """
    total_steps = args.steps if args.steps else cfg.total_steps
    temperature = args.temperature
    alpha = args.alpha
    top_k = args.top_k

    print(f"\n{'='*72}", file=sys.stderr)
    print(f"  Reference Beam Training", file=sys.stderr)
    print(f"  Teacher: {args.teacher_model}", file=sys.stderr)
    print(f"  Temperature T={temperature}  Alpha α={alpha}  Top-k={top_k}", file=sys.stderr)
    print(f"  Loss = CE*crystal + α * KD(top-{top_k}, T) + parity", file=sys.stderr)
    print(f"  steps {start_step+1}–{total_steps}", file=sys.stderr)
    if args.use_td:
        print(f"  TD: ENABLED (flip_rate={args.td_flip_rate}  "
              f"gate={args.td_crystal_gate})", file=sys.stderr)
    else:
        print(f"  TD: DISABLED (reference beam only)", file=sys.stderr)
    print(f"  Delta modules: {len(delta_modules)}", file=sys.stderr)
    for path, dtl in delta_modules:
        print(f"    {path}: ({dtl.out_features}, {dtl.in_features})", file=sys.stderr)
    print(f"{'='*72}", file=sys.stderr, flush=True)

    # ── Optimizers ─────────────────────────────────────────────
    adam = optim.AdamW(
        learning_rate=cfg.lr,
        weight_decay=cfg.weight_decay,
        betas=[0.9, 0.999],
    )

    # Optional TD (disabled by default for clean comparison)
    td = None
    td_active = False
    if args.use_td:
        td = TernaryDescent(
            flip_rate=args.td_flip_rate,
            warmup_steps=args.td_warmup,
            min_confidence=args.td_min_confidence,
            beta1=args.td_beta1,
            beta2=args.td_beta2,
        )

    def _student_loss(model, ids, tgts, tk_indices, tk_logits):
        return loss_fn_rb(
            model, ids, tgts, tk_indices, tk_logits,
            temperature=temperature, alpha=alpha,
        )

    loss_and_grad = nn.value_and_grad(model, _student_loss)

    # ── State ─────────────────────────────────────────────────
    train_losses = []
    loss_window = deque(maxlen=50)
    total_td_flips = 0
    t_start = time.time()

    # ── Warm-up forward pass (initialises Adam state) ─────────
    ids_np, tgts_np = next(train_loader)
    ids_mx = mx.array(ids_np)
    tgts_mx = mx.array(tgts_np)

    # Teacher forward: returns top-k indices + logits (stop_gradient'd)
    tk_indices, tk_logits = teacher_forward(teacher, ids_mx, temperature=temperature, top_k=top_k)

    lv, grads = loss_and_grad(model, ids_mx, tgts_mx, tk_indices, tk_logits)
    mx.eval(lv, grads)
    grads = zero_ternary_grads(model, grads)
    adam.update(model, grads)
    mx.eval(model.parameters(), adam.state)
    restore_ternary(model)

    # ── Restore optimizer/state from checkpoint if resuming ───
    if start_step > 0:
        opt_path = checkpoint_dir / f"step_{start_step:06d}" / "optimizer.npz"
        if not opt_path.exists() and args.resume:
            resume_opt = Path(args.resume).resolve() / "optimizer.npz"
            if resume_opt.exists():
                opt_path = resume_opt
        if opt_path.exists():
            saved_opt = dict(mx.load(str(opt_path)))
            current_flat = dict(tree_flatten(adam.state))
            n_restored = 0
            for k, v in saved_opt.items():
                if k in current_flat and current_flat[k].shape == v.shape:
                    current_flat[k] = v
                    n_restored += 1
            adam.state = tree_unflatten(list(current_flat.items()))
            mx.eval(adam.state)
            print(f"📂 Restored optimizer state ({n_restored} arrays)", file=sys.stderr)
            # Re-load model weights to undo warm-up step
            model_path = checkpoint_dir / f"step_{start_step:06d}" / "model.npz"
            if not model_path.exists() and args.resume:
                model_path = Path(args.resume).resolve() / "model.npz"
            if model_path.exists():
                model.load_weights(str(model_path), strict=False)
                mx.eval(model.parameters())
                restore_ternary(model)

        state_path = checkpoint_dir / f"step_{start_step:06d}" / "state.json"
        if not state_path.exists() and args.resume:
            state_path = Path(args.resume).resolve() / "state.json"
        if state_path.exists():
            state = json.loads(state_path.read_text())
            ema_val = state.get("crystal_ema")
            if ema_val is not None:
                model._crystal_ema = mx.array(float(ema_val))
            s5_state = state.get("s5_identity_state")
            if s5_state is not None:
                model.s5_identity.identity_state = mx.array(s5_state)
        model._training_step = start_step

    # ══════════════════════════════════════════════════════════
    # Main loop
    # ══════════════════════════════════════════════════════════

    nan_consecutive = 0

    for step in range(start_step + 1, total_steps + 1):
        t0 = time.time()

        lr = cosine_lr(step, cfg.warmup_steps, total_steps, cfg.lr, cfg.lr_floor_ratio)
        adam.learning_rate = lr
        model._training_step = step

        if cfg.use_holographic_loss:
            model._holo_lambda_effective = cfg.holo_lambda

        # ── Gradient accumulation ─────────────────────────────
        accum_loss = 0.0
        accum_ce = 0.0
        accum_kd = 0.0
        accum_grads = None

        for _micro in range(cfg.grad_accum):
            ids_np, tgts_np = next(train_loader)
            ids = mx.array(ids_np)
            tgts = mx.array(tgts_np)

            # ── Reference beam: teacher forward ───────────────
            # Returns top-k indices + logits (stop_gradient'd, eval'd)
            t_teacher = time.time()
            tk_indices, tk_logits = teacher_forward(teacher, ids, temperature=temperature, top_k=top_k)
            dt_teacher = time.time() - t_teacher

            # ── Student forward + backward ────────────────────
            lv, grads = loss_and_grad(model, ids, tgts, tk_indices, tk_logits)
            mx.eval(lv, grads)

            accum_loss += float(lv.item())

            # Grab cached CE and KD from model (set during forward/loss)
            ce_cached = getattr(model, "_last_ce", None)
            kd_cached = getattr(model, "_last_kd_loss", None)
            if ce_cached is not None:
                mx.eval(ce_cached)
                accum_ce += float(ce_cached.item())
            if kd_cached is not None:
                mx.eval(kd_cached)
                accum_kd += float(kd_cached.item())

            if accum_grads is None:
                accum_grads = grads
            else:
                accum_grads = tree_map(lambda a, b: a + b, accum_grads, grads)

        step_loss = accum_loss / cfg.grad_accum
        step_ce = accum_ce / cfg.grad_accum
        step_kd = accum_kd / cfg.grad_accum
        accum_grads = tree_map(lambda g: g / cfg.grad_accum, accum_grads)

        # ── NaN skip guard ────────────────────────────────────
        if math.isnan(step_loss) or math.isinf(step_loss):
            nan_consecutive += 1
            print(f"⚠️  NaN/Inf loss at step {step} (consecutive: {nan_consecutive})")
            if nan_consecutive >= 3:
                ckpt_dirs = sorted([d for d in os.listdir(str(checkpoint_dir))
                                    if d.startswith("step_")])
                if ckpt_dirs:
                    last_ckpt = checkpoint_dir / ckpt_dirs[-1]
                    print(f"🔄 3 consecutive NaN — rolling back to {last_ckpt}")
                    model.load_weights(str(last_ckpt / "model.npz"))
                    mx.eval(model.parameters())
                    restore_ternary(model)
                nan_consecutive = 0
            continue

        nan_consecutive = 0
        train_losses.append(step_loss)
        loss_window.append(step_loss)

        # ── Shared-weight normalization + zero ternary grads ──
        accum_grads = normalize_shared_grads(accum_grads)
        accum_grads = zero_ternary_grads(model, accum_grads)

        # ── Gradient clipping ─────────────────────────────────
        flat_grads = [g for _, g in tree_flatten(accum_grads) if isinstance(g, mx.array)]
        grad_sq = sum(float(mx.sum(g * g).item()) for g in flat_grads) if flat_grads else 0.0
        grad_norm = math.sqrt(max(grad_sq, 0.0))

        if cfg.grad_clip > 0 and grad_norm > cfg.grad_clip:
            s = cfg.grad_clip / (grad_norm + 1e-8)
            accum_grads = tree_map(lambda g: g * s, accum_grads)

        # ── Adam step ─────────────────────────────────────────
        adam.update(model, accum_grads)
        mx.eval(model.parameters(), adam.state)
        restore_ternary(model)

        # ── Optional TD step (crystal-gated) ──────────────────
        td_result = {"total_flips": 0, "in_warmup": True, "per_module": {}}
        n_adam_decayed = 0
        if td is not None:
            from train_td import compute_decomposed_gradients, filter_gamma_grads

            crystal_val_for_gate = getattr(model, "_last_crystal_loss", None)
            if crystal_val_for_gate is not None:
                mx.eval(crystal_val_for_gate)
                crystal_val_for_gate = float(crystal_val_for_gate.item())

            if crystal_val_for_gate is not None:
                if crystal_val_for_gate < args.td_crystal_gate:
                    td_active = True
                elif crystal_val_for_gate > args.td_crystal_ceiling:
                    td_active = False

            if td_active:
                td_inputs, gamma_filters = compute_decomposed_gradients(model, accum_grads)
                td_result = td.step(td_inputs)

                for name, info in td_result["per_module"].items():
                    if "new_packed" in info:
                        for path, dtl in delta_modules:
                            if path == name:
                                dtl.delta_weight = info["new_packed"]
                                mx.eval(dtl.delta_weight)
                                break
                        if "affected_rows" in info and info["affected_rows"]:
                            surgical_adam_decay_for_etch(
                                adam, model, {name: info["affected_rows"]}, decay=0.1)

            total_td_flips += td_result["total_flips"]

        dt = time.time() - t0

        # ── Logging ───────────────────────────────────────────
        if step % cfg.log_interval == 0 or step == start_step + 1:
            avg50 = sum(loss_window) / max(len(loss_window), 1)
            elapsed = time.time() - t_start
            tps = cfg.tokens_per_step / max(dt, 1e-6)

            crystal_val = getattr(model, "_last_crystal_loss", None)
            if crystal_val is not None:
                mx.eval(crystal_val)
                crystal_val = float(crystal_val.item())

            # Delta plate stats
            total_changed = 0.0
            for path, dtl in delta_modules:
                ds = dtl.delta_stats()
                total_changed += ds["changed_frac"]
            avg_changed = total_changed / max(len(delta_modules), 1)

            crystal_str = f" crystal={crystal_val:.4f}" if crystal_val is not None else ""

            parity_str = ""
            parity_val = getattr(model, "_last_parity_loss", None)
            if parity_val is not None:
                mx.eval(parity_val)
                parity_str = f" parity={float(parity_val.item()):.4f}"

            td_str = ""
            if td is not None:
                gate_icon = "🔓" if td_active else "🔒"
                td_str = f" {gate_icon} td={td_result['total_flips']} Δ={avg_changed:.3f}"

            print(
                f"step {step:>6d}"
                f" | loss={step_loss:.4f} (avg50: {avg50:.4f})"
                f" | CE={step_ce:.3f} KD={step_kd:.3f}"
                f"{crystal_str}{parity_str}"
                f" | lr {lr:.2e}"
                f" | gnorm {grad_norm:.2f}"
                f" | {tps:.0f} tok/s"
                f"{td_str}"
                f" | {elapsed:.0f}s",
                file=sys.stderr, flush=True,
            )

            # JSONL log
            record = {
                "step": step,
                "timestamp": time.time(),
                "loss": step_loss,
                "loss_avg50": avg50,
                "ce": step_ce,
                "kd_loss": step_kd,
                "temperature": temperature,
                "alpha": alpha,
                "lr": lr,
                "grad_norm": grad_norm,
                "tok_per_sec": tps,
                "elapsed": elapsed,
                "delta_avg_changed": avg_changed,
            }
            if crystal_val is not None:
                record["crystal_loss"] = crystal_val
            parity_val = getattr(model, "_last_parity_loss", None)
            if parity_val is not None:
                mx.eval(parity_val)
                record["parity_loss"] = float(parity_val.item())
            parity_errs = getattr(model, "_last_parity_errors", None)
            if parity_errs is not None:
                mx.eval(parity_errs)
                parity_levels = getattr(model, "_parity_levels", [3, 4, 5, 6, 8])
                for k, err in zip(parity_levels, parity_errs.tolist()):
                    record[f"parity_err_{k}d"] = err
            cross_zone_val = getattr(model, "_last_cross_zone_loss", None)
            if cross_zone_val is not None:
                mx.eval(cross_zone_val)
                record["cross_zone_loss"] = float(cross_zone_val.item())
            lens_rot = getattr(model, "_last_lens_rotation", None)
            if lens_rot is not None:
                mx.eval(lens_rot)
                for i, r in enumerate(lens_rot.tolist()):
                    record[f"lens_rot_zone{i}"] = r
            if td is not None:
                record["td_flips"] = td_result["total_flips"]
                record["td_total_flips"] = total_td_flips
                record["td_active"] = td_active

            _append_jsonl(checkpoint_dir / "train_rb_log.jsonl", record)

        # ── Evaluation ────────────────────────────────────────
        if step % cfg.eval_interval == 0:
            eval_result = _evaluate(model, teacher, cfg, temperature, alpha, top_k)
            print(
                f"📊 Eval @ {step}:"
                f" loss={eval_result['loss']:.3f}"
                f" CE={eval_result['ce']:.3f}"
                f" KD={eval_result['kd']:.3f}"
                f" ppl={eval_result['ppl']:.0f}",
                file=sys.stderr, flush=True,
            )
            crystal = eval_result.get("crystal", {})
            if crystal:
                print(
                    f"     crystal: WHNF_anti={crystal.get('whnf_anti_correlation', 0):.3f}"
                    f"  comp_cluster={crystal.get('composition_cluster_mean', 0):.3f}"
                    f"  cross={crystal.get('cross_crystal_mean', 0):.3f}",
                    file=sys.stderr, flush=True,
                )
            _append_jsonl(checkpoint_dir / "rb_metrics_log.jsonl", {
                "step": step, "timestamp": time.time(), **eval_result,
            })

        # ── Checkpoint ────────────────────────────────────────
        if step % cfg.checkpoint_interval == 0:
            _save_checkpoint(model, adam, step, cfg, checkpoint_dir,
                             train_losses, total_td_flips, temperature, alpha)

    # ── Final ─────────────────────────────────────────────────
    elapsed = time.time() - t_start
    final_eval = _evaluate(model, teacher, cfg, temperature, alpha, top_k)
    print(
        f"\n{'='*72}\n"
        f"Reference Beam training complete: {total_steps - start_step} steps in {elapsed:.0f}s\n"
        f"Final: loss={final_eval['loss']:.3f}  CE={final_eval['ce']:.3f}  "
        f"KD={final_eval['kd']:.3f}  ppl={final_eval['ppl']:.0f}",
        file=sys.stderr,
    )
    _save_checkpoint(model, adam, total_steps, cfg, checkpoint_dir,
                     train_losses, total_td_flips, temperature, alpha)


# ══════════════════════════════════════════════════════════════════════════════
# § 7  Evaluation and checkpointing
# ══════════════════════════════════════════════════════════════════════════════


def _evaluate(model, teacher, cfg, temperature, alpha, top_k=64):
    eval_loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=cfg.batch_size,
        seq_len=cfg.seq_len,
        shard_start=cfg.n_train_shards,
        shard_end=cfg.n_train_shards + cfg.n_eval_shards,
        seed=9999,
    )
    total_loss = 0.0
    total_ce = 0.0
    total_kd = 0.0
    n_batches = 0
    tokens_seen = 0

    while tokens_seen < 50_000:
        ids_np, tgts_np = next(eval_loader)
        ids = mx.array(ids_np)
        tgts = mx.array(tgts_np)

        # Teacher reference beam (top-k, eval'd)
        tk_indices, tk_logits = teacher_forward(teacher, ids, temperature=temperature, top_k=top_k)

        # Student forward with targets (triggers crystal/parity/geometry)
        student_logits, _ = model(ids, tgts)
        mx.eval(student_logits)

        # Hard CE (for PPL, comparable with train_td)
        ce_only = nn.losses.cross_entropy(
            student_logits.reshape(-1, cfg.vocab_size),
            tgts.reshape(-1),
        ).mean()

        # KD loss over top-k (reference beam quality)
        teacher_probs_k = mx.softmax(tk_logits, axis=-1)
        student_scaled = student_logits / temperature
        student_top_k = mx.take_along_axis(student_scaled, tk_indices, axis=-1)
        student_log_probs_k = student_top_k - mx.logsumexp(student_top_k, axis=-1, keepdims=True)
        kl = teacher_probs_k * (mx.log(teacher_probs_k + 1e-10) - student_log_probs_k)
        kd_val = mx.mean(mx.sum(kl, axis=-1)) * (temperature ** 2)

        mx.eval(ce_only, kd_val)
        total_loss += float(ce_only.item())
        total_ce += float(ce_only.item())
        total_kd += float(kd_val.item())
        n_batches += 1
        tokens_seen += ids_np.size

    avg_loss = total_loss / max(n_batches, 1)
    result = {
        "loss": avg_loss,
        "ce": total_ce / max(n_batches, 1),
        "kd": total_kd / max(n_batches, 1),
        "ppl": math.exp(min(avg_loss, 20.0)),
    }

    crystal = model.crystal_diagnostics()
    result["crystal"] = crystal

    parity_val = getattr(model, "_last_parity_loss", None)
    if parity_val is not None:
        mx.eval(parity_val)
        result["parity_loss"] = float(parity_val.item())

    return result


def _save_checkpoint(model, adam, step, cfg, checkpoint_dir,
                     train_losses, total_td_flips, temperature, alpha):
    step_dir = checkpoint_dir / f"step_{step:06d}"
    step_dir.mkdir(parents=True, exist_ok=True)

    flat_weights = dict(tree_flatten(model.parameters()))
    mx.savez(str(step_dir / "model.npz"), **flat_weights)

    if adam.state:
        flat_opt = dict(tree_flatten(adam.state))
        mx.savez(str(step_dir / "optimizer.npz"), **flat_opt)

    # Delta plate snapshots
    delta_snapshots = {}
    for path, mod in model.named_modules():
        if isinstance(mod, DeltaTernaryLinear):
            delta_key = path.replace(".", "_")
            delta_unpacked = unpack_ternary_mlx(mod.delta_weight)
            mx.eval(delta_unpacked)
            delta_snapshots[f"{delta_key}_delta"] = delta_unpacked
            delta_snapshots[f"{delta_key}_stats"] = mx.array([
                float((delta_unpacked == 1).sum().item()),
                float((delta_unpacked == -1).sum().item()),
                float((delta_unpacked == 0).sum().item()),
                float(delta_unpacked.size),
            ])
    if delta_snapshots:
        mx.savez(str(step_dir / "delta_plates.npz"), **delta_snapshots)

    crystal_ema = getattr(model, "_crystal_ema", None)
    if crystal_ema is not None:
        mx.eval(crystal_ema)

    s5_identity = getattr(model.s5_identity, "identity_state", None)
    if s5_identity is not None:
        mx.eval(s5_identity)

    state = {
        "step": step,
        "train_losses_last50": train_losses[-50:],
        "total_td_flips": total_td_flips,
        "temperature": temperature,
        "alpha": alpha,
        "crystal_ema": float(crystal_ema.item()) if crystal_ema is not None else None,
        "s5_identity_state": s5_identity.tolist() if s5_identity is not None else None,
    }

    delta_stats = {}
    for path, mod in model.named_modules():
        if isinstance(mod, DeltaTernaryLinear):
            delta_stats[path] = mod.delta_stats()
    if delta_stats:
        state["delta_stats"] = delta_stats

    (step_dir / "state.json").write_text(json.dumps(_sanitize(state), indent=2))
    print(f"💾 Checkpoint: {step_dir}", file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════════════
# § 8  CLI
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="v13 — Reference Beam trainer (teacher logits + delta plates)"
    )
    parser.add_argument("--checkpoint-dir", default="checkpoints/v13-rb")
    parser.add_argument("--resume", type=str, default=None,
                        help="Etched checkpoint or training checkpoint to resume")
    parser.add_argument("--steps", type=int, default=None)

    # Teacher / reference beam params
    parser.add_argument("--teacher-model", type=str, default="Qwen/Qwen3-32B",
                        help="HuggingFace model ID for teacher (default: Qwen/Qwen3-32B)")
    parser.add_argument("--temperature", type=float, default=2.0,
                        help="KD temperature. Higher = softer distributions = more dark knowledge. "
                             "Default: 2.0 (Hinton's recommended starting point)")
    parser.add_argument("--alpha", type=float, default=0.5,
                        help="Weight for hard CE. KD weight = 1-alpha. "
                             "0.5 = equal weight (default). 0.0 = pure KD. 1.0 = pure CE.")
    parser.add_argument("--top-k", type=int, default=64,
                        help="Number of top teacher tokens for KD (default: 64). "
                             "Captures 99%%+ of probability mass. Higher = more signal, slower.")

    # Optional TernaryDescent (disabled by default for clean comparison)
    parser.add_argument("--use-td", action="store_true", default=False,
                        help="Enable TernaryDescent alongside reference beam (default: off)")
    parser.add_argument("--td-flip-rate", type=float, default=0.001)
    parser.add_argument("--td-warmup", type=int, default=25)
    parser.add_argument("--td-crystal-gate", type=float, default=0.03)
    parser.add_argument("--td-crystal-ceiling", type=float, default=0.07)
    parser.add_argument("--td-min-confidence", type=float, default=0.3)
    parser.add_argument("--td-beta1", type=float, default=0.9)
    parser.add_argument("--td-beta2", type=float, default=0.999)

    # What to convert
    parser.add_argument("--convert-ffn", action="store_true",
                        help="Also convert FFN plates to delta (default: attention only)")

    # Config overrides
    parser.add_argument("--lr", type=float, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--seq-len", type=int, default=None)
    parser.add_argument("--data-dir", type=str, default=None)
    parser.add_argument("--crystal-direct-lambda", type=float, default=None)
    parser.add_argument("--crystal-direct-lambda-start", type=float, default=None)
    parser.add_argument("--crystal-warmup-steps", type=int, default=None)

    args = parser.parse_args()
    cfg = V13Config()

    if args.lr is not None:
        cfg.lr = args.lr
    if args.batch_size is not None:
        cfg.batch_size = args.batch_size
    if args.seq_len is not None:
        cfg.seq_len = args.seq_len
        cfg.max_seq_len = args.seq_len
    if args.data_dir is not None:
        cfg.data_dir = args.data_dir
    if args.crystal_direct_lambda is not None:
        cfg.crystal_direct_lambda = args.crystal_direct_lambda
    if args.crystal_direct_lambda_start is not None:
        cfg.crystal_direct_lambda_start = args.crystal_direct_lambda_start
    if args.crystal_warmup_steps is not None:
        cfg.crystal_warmup_steps = args.crystal_warmup_steps
    cfg.__post_init__()

    checkpoint_dir = Path(args.checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # ── Banner ────────────────────────────────────────────────
    print("=" * 72, file=sys.stderr)
    print("  v13 — Reference Beam Training", file=sys.stderr)
    print("  Teacher (reference beam) + Student (delta plates)", file=sys.stderr)
    print(f"  Teacher: {args.teacher_model}", file=sys.stderr)
    print(f"  T={args.temperature}  α={args.alpha}", file=sys.stderr)
    print("=" * 72, file=sys.stderr)

    # ── Load teacher ──────────────────────────────────────────
    teacher = load_teacher(args.teacher_model)

    # ── Load student (same pipeline as train_td) ──────────────
    # Pattern: create → freeze → load weights → convert to delta → reload
    # This matches train_td.py's proven sequence exactly.
    model = V13Model(cfg)
    freeze_ternary_weights(model)

    start_step = 0
    if args.resume:
        resume_path = Path(args.resume).resolve()
        if resume_path.exists():
            weights = dict(mx.load(str(resume_path / "model.npz")))
            reinit_prefixes = ("s4.", "s5_identity.")
            model_params = dict(tree_flatten(model.parameters()))
            filtered = []
            n_skipped = 0
            for k, v in weights.items():
                if any(k.startswith(p) for p in reinit_prefixes):
                    if k in model_params and model_params[k].shape == v.shape:
                        filtered.append((k, v))
                    else:
                        n_skipped += 1
                else:
                    filtered.append((k, v))
            model.load_weights(filtered, strict=False)
            mx.eval(model.parameters())
            restore_ternary(model)
            print(f"📂 Loaded weights from {resume_path}"
                  f" ({len(filtered)} loaded, {n_skipped} skipped)",
                  file=sys.stderr)

            # Check for training checkpoint (has step in path)
            state_path = resume_path / "state.json"
            if state_path.exists():
                state = json.loads(state_path.read_text())
                start_step = state.get("step", 0)
                print(f"📂 Resuming from step {start_step}", file=sys.stderr)
        else:
            print(f"⚠  Resume path not found: {resume_path}", file=sys.stderr)

    # ── Convert to delta plates (in-place on loaded model) ────
    # Determine which modules to convert
    # Must match full paths: stack_a.stride_stack, stack_b.stride_stack, etc.
    include = ["stack_a.stride_stack", "stack_b.stride_stack", "stack_c.stride_stack"]
    exclude = []
    if args.convert_ffn:
        include.extend(["ffn_key_plate", "ffn_value_plate"])
    else:
        exclude.extend(["ffn_key_plate", "ffn_value_plate"])

    delta_modules = convert_to_delta(
        model,
        include_prefixes=tuple(include) if include else None,
        exclude_prefixes=tuple(exclude) if exclude else None,
    )
    freeze_delta_architecture(model)
    freeze_ternary_weights(model)

    print(f"🔧 Converted {len(delta_modules)} modules to delta plates",
          file=sys.stderr)
    for path, dtl in delta_modules:
        print(f"    {path}: ({dtl.out_features}, {dtl.in_features})", file=sys.stderr)

    # Re-load weights into delta architecture (keys now include base_weight/delta_weight)
    if args.resume:
        resume_path = Path(args.resume).resolve()
        if resume_path.exists():
            weights = dict(mx.load(str(resume_path / "model.npz")))
            model.load_weights(list(weights.items()), strict=False)
            mx.eval(model.parameters())
            restore_ternary(model)

    # ── Data loader ───────────────────────────────────────────
    prose_loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=cfg.batch_size,
        seq_len=cfg.seq_len,
        shard_start=0,
        shard_end=cfg.n_train_shards,
    )

    structured_path = Path(cfg.structured_shard)
    if structured_path.exists():
        train_loader = MixedDataLoader(
            prose_loader=prose_loader,
            structured_path=structured_path,
            mix_ratio=cfg.mix_ratio,
            seq_len=cfg.seq_len,
            batch_size=cfg.batch_size,
        )
    else:
        train_loader = prose_loader

    # ── Train ─────────────────────────────────────────────────
    train_rb(
        cfg=cfg,
        args=args,
        model=model,
        teacher=teacher,
        delta_modules=delta_modules,
        start_step=start_step,
        train_loader=train_loader,
        checkpoint_dir=checkpoint_dir,
    )
