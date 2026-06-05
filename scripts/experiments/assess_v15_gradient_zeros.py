"""Assess gradient-near-zero topology in v15-td step 1500.

Session 171/190 insight: the gradient-zero map IS the holographic fringe
pattern. Where GD has converged (gradient ≈ 0), the weights are at their
fixed points — either nodes (zeros) or antinodes (saturated ±1).

For the v15-td student, the interesting landscape has three layers:
  1. GAMMA gradients: continuous per-row scales on each projection.
     Where gamma-gradient ≈ 0, that row's scale is settled.
  2. TD gradient signal: the decomposed routing gradient tells TD
     which delta positions want to flip. Where it's near-zero, the
     delta plate has converged (teacher sign is correct for this topology).
  3. Effective weight zeros: base ⊙ delta positions that are 0
     (either teacher zero or delta-blocked). These are structural.

Comparisons to teacher:
  - Teacher attention had full context. Student has Fibonacci windows.
  - Teacher Q/K/V/O optimized by GD (float). Student has ternary base
    + delta signs + float gammas.
  - WHERE does the student's gradient settle differently from teacher?
    That tells us where the stride topology has different fixed points.

License: MIT
"""

import sys
import json
import math
from pathlib import Path
from collections import defaultdict

import numpy as np
import mlx.core as mx
import mlx.nn as nn
from mlx.utils import tree_flatten, tree_unflatten

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "v15"))

from config import V15Config, STRIDES
from v15model import V15Model
from ternary import (
    freeze_ternary_weights,
    restore_ternary,
    unpack_ternary_mlx,
    zero_ternary_grads,
)
from td_delta import (
    convert_to_delta,
    collect_delta_params,
    freeze_delta_architecture,
    DeltaTernaryLinear,
    decompose_gradient,
    compute_routing_fraction,
)
from data import ShardedDataLoader


def log(msg):
    print(msg, flush=True)


# ══════════════════════════════════════════════════════════════
# § 1  Load checkpoint (reuse from attention assessment)
# ══════════════════════════════════════════════════════════════

def load_checkpoint(checkpoint_dir: str, cfg: V15Config) -> V15Model:
    """Load v15-td checkpoint into V15Model with delta plates."""
    ckpt = Path(checkpoint_dir)

    model = V15Model(cfg)
    freeze_ternary_weights(model)

    # Load extracted base plates
    extracted_path = Path(cfg.extracted_model_path)
    if extracted_path.exists():
        saved = dict(mx.load(str(extracted_path)))
        flat_params = dict(tree_flatten(model.parameters()))
        n_loaded = 0

        proj_map = {"q": "q_proj", "k": "k_proj", "v": "v_proj", "o": "out_proj"}
        for layer_idx in range(cfg.n_strides):
            for ext_proj, model_proj in proj_map.items():
                model_key = f"shared_stride_stack.layers.{layer_idx}.{model_proj}.weight"
                if model_key not in flat_params:
                    continue
                ext_key = f"shared_stride_stack.layers.{layer_idx}.{ext_proj}"
                if ext_key not in saved:
                    continue
                arr = saved[ext_key]
                target_shape = flat_params[model_key].shape
                if arr.shape == target_shape:
                    flat_params[model_key] = mx.array(arr)
                    n_loaded += 1
                elif arr.shape[0] >= target_shape[0] and arr.shape[1] >= target_shape[1]:
                    flat_params[model_key] = mx.array(arr[:target_shape[0], :target_shape[1]])
                    n_loaded += 1

        ffn_map = {
            "stack_a.ffn.gate": "ffn_gate_plate_a.weight",
            "stack_a.ffn.up":   "ffn_key_plate_a.weight",
            "stack_a.ffn.down": "ffn_value_plate_a.weight",
            "stack_c.ffn.gate": "ffn_gate_plate_c.weight",
            "stack_c.ffn.up":   "ffn_key_plate_c.weight",
            "stack_c.ffn.down": "ffn_value_plate_c.weight",
        }
        for ext_key, model_key in ffn_map.items():
            if ext_key in saved and model_key in flat_params:
                if saved[ext_key].shape == flat_params[model_key].shape:
                    flat_params[model_key] = mx.array(saved[ext_key])
                    n_loaded += 1

        if "embed_tokens" in saved:
            emb_key = "embed.ternary_weight"
            if emb_key in flat_params:
                ext_emb = saved["embed_tokens"]
                if ext_emb.shape == flat_params[emb_key].shape:
                    flat_params[emb_key] = mx.array(ext_emb)
                    n_loaded += 1

        model.update(tree_unflatten(list(flat_params.items())))
        mx.eval(model.parameters())
        restore_ternary(model)
        freeze_ternary_weights(model)
        log(f"  Base plates loaded: {n_loaded} arrays")

    # Convert to delta architecture
    converted = convert_to_delta(
        model,
        include_prefixes=("shared_stride_stack",),
    )
    freeze_delta_architecture(model)
    freeze_ternary_weights(model)
    log(f"  Delta architecture: {len(converted)} modules")

    # Load checkpoint weights
    model_path = ckpt / "model.npz"
    if model_path.exists():
        saved_model = dict(mx.load(str(model_path)))
        flat_params = dict(tree_flatten(model.parameters()))
        n_loaded = 0
        for key, val in saved_model.items():
            if key in flat_params and val.shape == flat_params[key].shape:
                flat_params[key] = val
                n_loaded += 1
        model.update(tree_unflatten(list(flat_params.items())))
        mx.eval(model.parameters())
        log(f"  Checkpoint weights loaded: {n_loaded}")

    # Load delta plates
    delta_path = ckpt / "delta_plates.npz"
    if delta_path.exists():
        delta_data = dict(mx.load(str(delta_path)))
        delta_modules = collect_delta_params(model)
        n_delta_loaded = 0
        for path, dtl in delta_modules:
            delta_key = path.replace(".", "_") + "_delta_packed"
            if delta_key in delta_data:
                dtl.delta_weight = delta_data[delta_key]
                mx.eval(dtl.delta_weight)
                n_delta_loaded += 1
        log(f"  Delta plates loaded: {n_delta_loaded}")

    return model


# ══════════════════════════════════════════════════════════════
# § 2  Gradient computation
# ══════════════════════════════════════════════════════════════

def compute_gradients(model: V15Model, data_loader, cfg: V15Config, n_batches: int = 4):
    """Run forward+backward on a few batches and accumulate gradient statistics.

    Returns accumulated gradient dict (not averaged — we want magnitude patterns).
    """
    loss_fn = lambda m, ids, tgts: m(ids, tgts)[1]
    loss_and_grad = nn.value_and_grad(model, loss_fn)

    accum_grads = None
    accum_grad_sq = None
    losses = []

    for i in range(n_batches):
        ids_np, tgts_np = next(data_loader)
        ids = mx.array(ids_np)
        tgts = mx.array(tgts_np)

        lv, grads = loss_and_grad(model, ids, tgts)
        mx.eval(lv, grads)

        # Zero ternary grads (they're not meaningful for packed uint32)
        grads = zero_ternary_grads(model, grads)

        losses.append(float(lv.item()))

        flat_g = dict(tree_flatten(grads))

        if accum_grads is None:
            accum_grads = {k: v.astype(mx.float32) for k, v in flat_g.items()
                          if isinstance(v, mx.array) and v.dtype in (mx.float32, mx.float16)}
            accum_grad_sq = {k: (v.astype(mx.float32) ** 2) for k, v in accum_grads.items()}
        else:
            for k, v in flat_g.items():
                if k in accum_grads and isinstance(v, mx.array):
                    vf = v.astype(mx.float32)
                    accum_grads[k] = accum_grads[k] + vf
                    accum_grad_sq[k] = accum_grad_sq[k] + vf ** 2

    # Compute mean and RMS
    mean_grads = {k: v / n_batches for k, v in accum_grads.items()}
    rms_grads = {}
    for k in accum_grad_sq:
        rms_grads[k] = mx.sqrt(accum_grad_sq[k] / n_batches)

    log(f"  Gradient computed over {n_batches} batches, mean loss = {np.mean(losses):.4f}")
    return mean_grads, rms_grads


# ══════════════════════════════════════════════════════════════
# § 3  Gamma gradient analysis
# ══════════════════════════════════════════════════════════════

def analyze_gamma_gradients(mean_grads: dict, rms_grads: dict):
    """Analyze where gamma (per-row scale) gradients are near zero.

    Gamma near-zero gradient = GD has found the optimal scale for
    that row of the projection. The pattern of settled vs active
    rows reveals which projections are still being calibrated.
    """
    results = {}

    for key in sorted(mean_grads.keys()):
        if ".gamma" not in key:
            continue

        mean_g = np.array(mean_grads[key])
        rms_g = np.array(rms_grads[key])
        mx.eval(mean_grads[key], rms_grads[key])

        abs_mean = np.abs(mean_g)
        n_total = len(abs_mean)

        # Define "near-zero" thresholds relative to the overall RMS
        overall_rms = float(np.sqrt(np.mean(rms_g ** 2)))
        if overall_rms < 1e-10:
            continue

        # Fraction of rows with |mean_grad| < threshold
        thresholds = [0.01, 0.05, 0.1, 0.2]
        near_zero_fracs = {}
        for t in thresholds:
            thresh = t * overall_rms
            frac = float(np.sum(abs_mean < thresh) / n_total)
            near_zero_fracs[f"<{t:.0%}rms"] = frac

        # Directional bias: fraction of positive vs negative gradients
        pos_frac = float(np.sum(mean_g > 0) / n_total)

        results[key] = {
            "n_rows": n_total,
            "mean_abs_grad": float(np.mean(abs_mean)),
            "rms_grad": overall_rms,
            "max_abs_grad": float(np.max(abs_mean)),
            "near_zero_fracs": near_zero_fracs,
            "pos_direction_frac": pos_frac,
            "settled_frac_10pct": near_zero_fracs.get("<10%rms", 0.0),
        }

    return results


# ══════════════════════════════════════════════════════════════
# § 4  TD gradient signal analysis (routing gradient on delta plates)
# ══════════════════════════════════════════════════════════════

def analyze_td_gradient_signal(model: V15Model, mean_grads: dict, rms_grads: dict):
    """Analyze the gradient signal that TD uses to decide flips.

    For each DeltaTernaryLinear, the "routing gradient" tells TD which
    positions want to flip sign. Where routing gradient ≈ 0, the delta
    plate has converged — the current sign (teacher or flipped) is correct.

    We proxy this with the gamma gradient × column importance, decomposed
    into routing and calibration components.
    """
    delta_modules = collect_delta_params(model)
    results = {}

    for path, dtl in delta_modules:
        # Get gamma gradient
        gamma_key = path + ".gamma"
        if gamma_key not in mean_grads:
            continue

        gamma_grad = mean_grads[gamma_key]
        mx.eval(gamma_grad)

        # Get effective signs
        base = unpack_ternary_mlx(dtl.base_weight)
        delta = unpack_ternary_mlx(dtl.delta_weight)
        effective = (base.astype(mx.int16) * delta.astype(mx.int16)).astype(mx.int8)

        # Column importance (cached from forward pass, or approximate)
        if hasattr(dtl, '_x_abs_mean'):
            col_imp = dtl._x_abs_mean
        else:
            col_imp = mx.ones((dtl.in_features,))

        # Gradient field: (out_features, in_features)
        grad_field = mx.expand_dims(gamma_grad, axis=-1) * mx.expand_dims(col_imp, axis=0)
        mx.eval(grad_field, effective)

        # Decompose into routing and calibration
        routing, calibration, routing_mask = decompose_gradient(grad_field, effective)
        mx.eval(routing, calibration)

        routing_np = np.array(routing)
        calibration_np = np.array(calibration)
        effective_np = np.array(effective)

        # Where routing gradient is near-zero → delta has converged
        routing_abs = np.abs(routing_np)
        routing_rms = float(np.sqrt(np.mean(routing_abs ** 2)))

        if routing_rms < 1e-12:
            continue

        # Gradient-zero map for the routing component
        near_zero_01 = float(np.sum(routing_abs < 0.01 * routing_rms) / routing_abs.size)
        near_zero_05 = float(np.sum(routing_abs < 0.05 * routing_rms) / routing_abs.size)
        near_zero_10 = float(np.sum(routing_abs < 0.10 * routing_rms) / routing_abs.size)
        near_zero_20 = float(np.sum(routing_abs < 0.20 * routing_rms) / routing_abs.size)

        # Where the effective weight is zero
        zero_frac = float(np.sum(effective_np == 0) / effective_np.size)

        # Routing fraction (how much gradient is topology vs calibration)
        routing_frac = compute_routing_fraction(grad_field, effective)
        mx.eval(routing_frac)
        rf_np = np.array(routing_frac).flatten()
        routing_frac_val = float(np.mean(rf_np))

        # Where are the largest routing gradients? (most unsettled positions)
        top_pct = np.percentile(routing_abs[routing_abs > 0], [50, 90, 99])

        # Spatial pattern: per-row RMS of routing gradient
        row_rms = np.sqrt(np.mean(routing_np ** 2, axis=1))
        row_rms_sorted = np.sort(row_rms)[::-1]

        # How many rows have nearly zero routing gradient?
        rows_settled = float(np.sum(row_rms < 0.1 * routing_rms) / len(row_rms))
        rows_active = float(np.sum(row_rms > routing_rms) / len(row_rms))

        # Split results by whether delta is +1 (keep) or -1 (flipped)
        delta_np = np.array(delta)
        keep_mask = delta_np == 1
        flip_mask = delta_np == -1

        routing_at_keeps = routing_abs[keep_mask] if keep_mask.any() else np.array([0.0])
        routing_at_flips = routing_abs[flip_mask] if flip_mask.any() else np.array([0.0])

        # Parse layer/proj from path
        parts = path.split(".")
        layer_idx = int(parts[2])
        proj = parts[3]  # q_proj, k_proj, v_proj, out_proj

        results[path] = {
            "layer_idx": layer_idx,
            "proj": proj,
            "stride": STRIDES[layer_idx] if layer_idx < len(STRIDES) else -1,
            "routing_rms": routing_rms,
            "routing_frac": routing_frac_val,
            "zero_frac": zero_frac,
            "gradient_zero_fracs": {
                "1%": near_zero_01,
                "5%": near_zero_05,
                "10%": near_zero_10,
                "20%": near_zero_20,
            },
            "routing_percentiles": {
                "p50": float(top_pct[0]),
                "p90": float(top_pct[1]),
                "p99": float(top_pct[2]),
            },
            "rows_settled_frac": rows_settled,
            "rows_active_frac": rows_active,
            "routing_at_keeps_rms": float(np.sqrt(np.mean(routing_at_keeps ** 2))),
            "routing_at_flips_rms": float(np.sqrt(np.mean(routing_at_flips ** 2))),
        }

    return results


# ══════════════════════════════════════════════════════════════
# § 5  Teacher vs student zero topology comparison
# ══════════════════════════════════════════════════════════════

def compare_zero_topology(model: V15Model, cfg: V15Config):
    """Compare where zeros are in effective weights vs teacher base.

    Teacher base: the original extracted signs (base plate)
    Student effective: base ⊙ delta (after TD training)

    Where delta = -1: sign flipped from teacher
    Where delta = +1: kept teacher sign

    The zero structure comes from the teacher's extraction.
    TD doesn't add zeros (no-block enforcement), but it can flip
    non-zero positions. The PATTERN of flips relative to the zero
    structure tells us about the student's gradient-zero topology.
    """
    delta_modules = collect_delta_params(model)
    results = {}

    for path, dtl in delta_modules:
        base = np.array(unpack_ternary_mlx(dtl.base_weight))
        delta = np.array(unpack_ternary_mlx(dtl.delta_weight))
        effective = (base.astype(np.int16) * delta.astype(np.int16)).astype(np.int8)

        # Teacher zeros (structural)
        teacher_zeros = (base == 0)
        teacher_nonzero = ~teacher_zeros

        # Where did TD flip?
        flipped = (delta == -1) & teacher_nonzero
        kept = (delta == 1) & teacher_nonzero

        n_total = base.size
        n_teacher_zero = int(teacher_zeros.sum())
        n_flipped = int(flipped.sum())
        n_kept = int(kept.sum())

        # Spatial pattern of flips: are they clustered or uniform?
        # Per-row flip density
        row_flip_density = flipped.sum(axis=1) / np.maximum(teacher_nonzero.sum(axis=1), 1)
        row_flip_cv = float(np.std(row_flip_density) / (np.mean(row_flip_density) + 1e-12))

        # Per-column flip density
        col_flip_density = flipped.sum(axis=0) / np.maximum(teacher_nonzero.sum(axis=0), 1)
        col_flip_cv = float(np.std(col_flip_density) / (np.mean(col_flip_density) + 1e-12))

        # Sign pattern of flips: are flips preferentially on +1 or -1 teacher positions?
        teacher_pos = base == 1
        teacher_neg = base == -1
        flips_on_pos = int((flipped & teacher_pos).sum())
        flips_on_neg = int((flipped & teacher_neg).sum())

        parts = path.split(".")
        layer_idx = int(parts[2])
        proj = parts[3]

        results[path] = {
            "layer_idx": layer_idx,
            "proj": proj,
            "stride": STRIDES[layer_idx] if layer_idx < len(STRIDES) else -1,
            "teacher_zero_frac": n_teacher_zero / n_total,
            "flip_frac": n_flipped / max(n_total - n_teacher_zero, 1),
            "flip_row_cv": row_flip_cv,
            "flip_col_cv": col_flip_cv,
            "flips_on_pos_teacher": flips_on_pos,
            "flips_on_neg_teacher": flips_on_neg,
            "pos_neg_flip_ratio": flips_on_pos / max(flips_on_neg, 1),
            "n_teacher_pos": int(teacher_pos.sum()),
            "n_teacher_neg": int(teacher_neg.sum()),
        }

    return results


# ══════════════════════════════════════════════════════════════
# § 6  Non-attention continuous parameter gradient landscape
# ══════════════════════════════════════════════════════════════

def analyze_continuous_gradients(mean_grads: dict, rms_grads: dict):
    """Broad survey of gradient magnitudes across all continuous parameters.

    Groups by component type: norms, biases, embeddings, S5, S4, crystal, etc.
    """
    categories = defaultdict(list)

    for key in sorted(mean_grads.keys()):
        mg = mean_grads[key]
        rg = rms_grads[key]
        mx.eval(mg, rg)
        mg_np = np.array(mg)
        rg_np = np.array(rg)

        abs_mean = float(np.mean(np.abs(mg_np)))
        rms = float(np.sqrt(np.mean(rg_np ** 2)))
        max_abs = float(np.max(np.abs(mg_np)))

        # Near-zero fraction
        if rms > 1e-12:
            near_zero = float(np.sum(np.abs(mg_np) < 0.1 * rms) / mg_np.size)
        else:
            near_zero = 1.0

        # Categorize
        if "gamma" in key and "shared_stride_stack" in key:
            cat = "attention_gamma"
        elif "gamma" in key and "ffn" in key:
            cat = "ffn_gamma"
        elif "norm" in key:
            cat = "norm_params"
        elif "bias" in key:
            cat = "biases"
        elif "embed" in key:
            cat = "embedding"
        elif "combinator" in key:
            cat = "crystal"
        elif "s5" in key or "s4" in key or "s2" in key:
            cat = "vsm_controller"
        elif "reweight" in key or "fire_alarm" in key:
            cat = "meta_control"
        elif "alg" in key:
            cat = "algedonic"
        else:
            cat = "other"

        categories[cat].append({
            "key": key,
            "shape": list(mg_np.shape),
            "n_params": mg_np.size,
            "abs_mean_grad": abs_mean,
            "rms_grad": rms,
            "max_abs_grad": max_abs,
            "near_zero_10pct": near_zero,
        })

    return dict(categories)


# ══════════════════════════════════════════════════════════════
# § 7  Main
# ══════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default="checkpoints/v15-td/step_001500")
    parser.add_argument("--extracted", default="checkpoints/v15-extracted/model.npz/model.npz")
    parser.add_argument("--data-dir", default="/Users/mwhitford/data/fractal-bitnet/shards-qwen36")
    parser.add_argument("--n-batches", type=int, default=4)
    parser.add_argument("--seq-len", type=int, default=512)
    args = parser.parse_args()

    cfg = V15Config(extracted_model_path=args.extracted)

    log("=" * 72)
    log("v15-td Gradient-Zero Topology Assessment")
    log("=" * 72)

    # ── Load ──────────────────────────────────────────────────
    log(f"\n§ 1  Loading checkpoint: {args.checkpoint}")
    model = load_checkpoint(args.checkpoint, cfg)

    # ── Compute gradients ─────────────────────────────────────
    log(f"\n§ 2  Computing gradients ({args.n_batches} batches, seq_len={args.seq_len})")
    data_loader = ShardedDataLoader(
        args.data_dir, seq_len=args.seq_len, batch_size=1,
        shard_start=54, shard_end=60, seed=789,
    )
    mean_grads, rms_grads = compute_gradients(model, data_loader, cfg, n_batches=args.n_batches)

    # ── Gamma gradient analysis ───────────────────────────────
    log(f"\n§ 3  Gamma (per-row scale) gradient landscape")
    gamma_results = analyze_gamma_gradients(mean_grads, rms_grads)

    # Group by projection type across layers
    proj_summary = defaultdict(list)
    for key, r in gamma_results.items():
        # Extract projection type from key
        for proj_name in ["q_proj", "k_proj", "v_proj", "out_proj",
                          "ffn_gate", "ffn_key", "ffn_value"]:
            if proj_name in key:
                proj_summary[proj_name].append(r)
                break
        else:
            proj_summary["other"].append(r)

    log(f"  {'Projection':>12s} | {'N':>5s} {'RMS':>8s} {'MaxAbs':>8s} | {'<1%rms':>7s} {'<5%rms':>7s} {'<10%rms':>7s} {'<20%rms':>7s} | {'Settled%':>8s}")
    for proj_name in ["q_proj", "k_proj", "v_proj", "out_proj", "other"]:
        if proj_name not in proj_summary:
            continue
        entries = proj_summary[proj_name]
        avg_rms = np.mean([e["rms_grad"] for e in entries])
        avg_max = np.mean([e["max_abs_grad"] for e in entries])
        avg_nz_01 = np.mean([e["near_zero_fracs"].get("<1%rms", 0) for e in entries])
        avg_nz_05 = np.mean([e["near_zero_fracs"].get("<5%rms", 0) for e in entries])
        avg_nz_10 = np.mean([e["near_zero_fracs"].get("<10%rms", 0) for e in entries])
        avg_nz_20 = np.mean([e["near_zero_fracs"].get("<20%rms", 0) for e in entries])
        avg_settled = np.mean([e["settled_frac_10pct"] for e in entries])
        n_layers = len(entries)
        log(f"  {proj_name:>12s} | {n_layers:5d} {avg_rms:8.2e} {avg_max:8.2e} | {avg_nz_01:6.1%} {avg_nz_05:6.1%} {avg_nz_10:6.1%} {avg_nz_20:6.1%} | {avg_settled:7.1%}")

    # ── TD gradient signal analysis ───────────────────────────
    log(f"\n§ 4  TD routing gradient landscape (delta plate convergence)")
    td_results = analyze_td_gradient_signal(model, mean_grads, rms_grads)

    # Per-projection type summary
    td_proj_summary = defaultdict(list)
    for path, r in td_results.items():
        td_proj_summary[r["proj"]].append(r)

    log(f"\n  {'Proj':>8s} | {'RoutRMS':>8s} {'RoutFrac':>8s} | {'GZ 1%':>6s} {'GZ 5%':>6s} {'GZ 10%':>6s} {'GZ 20%':>6s} | {'RowSettled':>10s} {'RowActive':>9s}")
    for proj_name in ["q_proj", "k_proj", "v_proj", "out_proj"]:
        entries = td_proj_summary.get(proj_name, [])
        if not entries:
            continue
        avg_rms = np.mean([e["routing_rms"] for e in entries])
        avg_rf = np.mean([e["routing_frac"] for e in entries])
        avg_gz1 = np.mean([e["gradient_zero_fracs"]["1%"] for e in entries])
        avg_gz5 = np.mean([e["gradient_zero_fracs"]["5%"] for e in entries])
        avg_gz10 = np.mean([e["gradient_zero_fracs"]["10%"] for e in entries])
        avg_gz20 = np.mean([e["gradient_zero_fracs"]["20%"] for e in entries])
        avg_settled = np.mean([e["rows_settled_frac"] for e in entries])
        avg_active = np.mean([e["rows_active_frac"] for e in entries])
        log(f"  {proj_name:>8s} | {avg_rms:8.2e} {avg_rf:8.3f} | {avg_gz1:5.1%} {avg_gz5:5.1%} {avg_gz10:5.1%} {avg_gz20:5.1%} | {avg_settled:9.1%} {avg_active:8.1%}")

    # Per-layer detail
    log(f"\n  Per-layer routing gradient (mean over Q/K/V/O):")
    log(f"  {'Layer':>5s} {'Stride':>6s} | {'RoutRMS':>8s} | {'GZ10%':>6s} {'GZ20%':>6s} | {'Settled':>7s} {'Active':>6s} | {'Keep-RMS':>8s} {'Flip-RMS':>8s} {'Ratio':>6s}")
    for layer_idx in range(cfg.n_strides):
        layer_entries = [r for r in td_results.values() if r["layer_idx"] == layer_idx]
        if not layer_entries:
            continue
        stride = STRIDES[layer_idx] if layer_idx < len(STRIDES) else -1
        avg_rms = np.mean([e["routing_rms"] for e in layer_entries])
        avg_gz10 = np.mean([e["gradient_zero_fracs"]["10%"] for e in layer_entries])
        avg_gz20 = np.mean([e["gradient_zero_fracs"]["20%"] for e in layer_entries])
        avg_settled = np.mean([e["rows_settled_frac"] for e in layer_entries])
        avg_active = np.mean([e["rows_active_frac"] for e in layer_entries])
        avg_keep_rms = np.mean([e["routing_at_keeps_rms"] for e in layer_entries])
        avg_flip_rms = np.mean([e["routing_at_flips_rms"] for e in layer_entries])
        ratio = avg_flip_rms / max(avg_keep_rms, 1e-12)
        log(f"  {layer_idx:5d} {stride:6d} | {avg_rms:8.2e} | {avg_gz10:5.1%} {avg_gz20:5.1%} | {avg_settled:6.1%} {avg_active:5.1%} | {avg_keep_rms:8.2e} {avg_flip_rms:8.2e} {ratio:6.2f}")

    # ── Zero topology comparison ──────────────────────────────
    log(f"\n§ 5  Teacher vs student zero topology")
    zero_results = compare_zero_topology(model, cfg)

    # Summary by projection
    zero_proj_summary = defaultdict(list)
    for path, r in zero_results.items():
        zero_proj_summary[r["proj"]].append(r)

    log(f"\n  {'Proj':>8s} | {'TeachZero%':>10s} | {'FlipFrac':>8s} | {'RowCV':>6s} {'ColCV':>6s} | {'FlipPos':>7s} {'FlipNeg':>7s} {'P/N Ratio':>9s}")
    for proj_name in ["q_proj", "k_proj", "v_proj", "out_proj"]:
        entries = zero_proj_summary.get(proj_name, [])
        if not entries:
            continue
        avg_tz = np.mean([e["teacher_zero_frac"] for e in entries])
        avg_ff = np.mean([e["flip_frac"] for e in entries])
        avg_rcv = np.mean([e["flip_row_cv"] for e in entries])
        avg_ccv = np.mean([e["flip_col_cv"] for e in entries])
        total_fp = sum(e["flips_on_pos_teacher"] for e in entries)
        total_fn = sum(e["flips_on_neg_teacher"] for e in entries)
        ratio = total_fp / max(total_fn, 1)
        log(f"  {proj_name:>8s} | {avg_tz:9.1%} | {avg_ff:7.2%} | {avg_rcv:6.2f} {avg_ccv:6.2f} | {total_fp:7d} {total_fn:7d} {ratio:9.3f}")

    # Per-layer flip pattern
    log(f"\n  Per-layer flip topology:")
    log(f"  {'Layer':>5s} {'Stride':>6s} | {'TeachZero%':>10s} {'FlipFrac':>8s} | {'RowCV':>6s} {'ColCV':>6s} | {'P/N':>5s}")
    for layer_idx in range(cfg.n_strides):
        layer_entries = [r for r in zero_results.values() if r["layer_idx"] == layer_idx]
        if not layer_entries:
            continue
        stride = STRIDES[layer_idx] if layer_idx < len(STRIDES) else -1
        avg_tz = np.mean([e["teacher_zero_frac"] for e in layer_entries])
        avg_ff = np.mean([e["flip_frac"] for e in layer_entries])
        avg_rcv = np.mean([e["flip_row_cv"] for e in layer_entries])
        avg_ccv = np.mean([e["flip_col_cv"] for e in layer_entries])
        total_fp = sum(e["flips_on_pos_teacher"] for e in layer_entries)
        total_fn = sum(e["flips_on_neg_teacher"] for e in layer_entries)
        ratio = total_fp / max(total_fn, 1)
        log(f"  {layer_idx:5d} {stride:6d} | {avg_tz:9.1%} {avg_ff:7.2%} | {avg_rcv:6.2f} {avg_ccv:6.2f} | {ratio:5.3f}")

    # ── Continuous parameter gradient survey ──────────────────
    log(f"\n§ 6  Continuous parameter gradient landscape")
    cont_results = analyze_continuous_gradients(mean_grads, rms_grads)

    log(f"\n  {'Category':>18s} | {'#Params':>10s} {'#Tensors':>8s} | {'MeanAbsG':>9s} {'RMS_G':>9s} | {'GZ@10%':>7s}")
    for cat in ["attention_gamma", "ffn_gamma", "norm_params", "biases",
                "crystal", "vsm_controller", "meta_control", "algedonic",
                "embedding", "other"]:
        if cat not in cont_results:
            continue
        entries = cont_results[cat]
        total_params = sum(e["n_params"] for e in entries)
        avg_abs = np.mean([e["abs_mean_grad"] for e in entries])
        avg_rms = np.mean([e["rms_grad"] for e in entries])
        avg_gz = np.mean([e["near_zero_10pct"] for e in entries])
        log(f"  {cat:>18s} | {total_params:10,d} {len(entries):8d} | {avg_abs:9.2e} {avg_rms:9.2e} | {avg_gz:6.1%}")

    # ── Overall assessment ────────────────────────────────────
    log(f"\n§ 7  Assessment: gradient-zero topology vs teacher")

    # Key questions:
    # 1. Are attention gammas settled? (gradient near zero → GD converged)
    # 2. Is the TD routing signal settled? (near-zero → delta plates converged)
    # 3. Are flips symmetric in +/- signs? (balanced → structural, biased → systematic)
    # 4. Where is gradient still active? (these are the frontier)

    findings = []
    concerns = []

    # Q1: Gamma convergence
    attn_gamma_entries = [e for entries in proj_summary.values()
                         for e in entries if any(p in e.get("key", "") for p in ["q_proj", "k_proj", "v_proj", "out_proj"])]
    if attn_gamma_entries:
        # Use the actual gamma results we already have
        q_entries = proj_summary.get("q_proj", [])
        k_entries = proj_summary.get("k_proj", [])
        v_entries = proj_summary.get("v_proj", [])
        o_entries = proj_summary.get("out_proj", [])
        all_attn = q_entries + k_entries + v_entries + o_entries
        if all_attn:
            avg_settled = np.mean([e["settled_frac_10pct"] for e in all_attn])
            if avg_settled > 0.5:
                findings.append(f"Attention gammas are {avg_settled:.0%} settled — GD is converging on row scales")
            elif avg_settled > 0.2:
                findings.append(f"Attention gammas are {avg_settled:.0%} settled — still calibrating but progressing")
            else:
                concerns.append(f"Attention gammas are only {avg_settled:.0%} settled — GD is still searching")

    # Q2: TD routing convergence
    if td_results:
        all_gz10 = [r["gradient_zero_fracs"]["10%"] for r in td_results.values()]
        avg_gz10 = np.mean(all_gz10)
        if avg_gz10 > 0.5:
            findings.append(f"TD routing gradients are {avg_gz10:.0%} near-zero — delta plates are converging")
        elif avg_gz10 > 0.2:
            findings.append(f"TD routing gradients are {avg_gz10:.0%} near-zero — still evolving but structured")
        else:
            concerns.append(f"TD routing gradients are only {avg_gz10:.0%} near-zero — delta plates still searching")

    # Q3: Flip symmetry
    if zero_results:
        total_fp = sum(r["flips_on_pos_teacher"] for r in zero_results.values())
        total_fn = sum(r["flips_on_neg_teacher"] for r in zero_results.values())
        pn_ratio = total_fp / max(total_fn, 1)
        if 0.8 < pn_ratio < 1.2:
            findings.append(f"Flip P/N ratio = {pn_ratio:.3f} — symmetric, flips are structural not biased")
        else:
            direction = "positive" if pn_ratio > 1 else "negative"
            concerns.append(f"Flip P/N ratio = {pn_ratio:.3f} — TD preferentially flips {direction} teacher signs")

    # Q4: Keep vs flip routing gradient
    if td_results:
        all_keep_rms = [r["routing_at_keeps_rms"] for r in td_results.values()]
        all_flip_rms = [r["routing_at_flips_rms"] for r in td_results.values()]
        avg_keep = np.mean(all_keep_rms)
        avg_flip = np.mean(all_flip_rms)
        ratio = avg_flip / max(avg_keep, 1e-12)
        if ratio > 1.5:
            concerns.append(f"Flipped positions have {ratio:.1f}× higher routing gradient than keeps — flips may be unstable")
        elif ratio > 1.1:
            findings.append(f"Flipped positions have {ratio:.1f}× higher routing gradient — flips are slightly less settled than keeps (expected)")
        else:
            findings.append(f"Flipped positions have similar routing gradient to keeps (ratio={ratio:.2f}) — both are converging")

    log(f"\n  ✅ Findings:")
    for f in findings:
        log(f"    + {f}")
    if concerns:
        log(f"\n  ⚠️  Concerns:")
        for c in concerns:
            log(f"    - {c}")
    else:
        log(f"\n  No concerns identified.")

    log(f"\n{'='*72}")
    log("Gradient-zero topology assessment complete.")


if __name__ == "__main__":
    main()
