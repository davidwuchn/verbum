#!/usr/bin/env python3
"""v15 Trace-Guided Etching — Pure topology correction.

No Adam. No NTP. Just: trace loss → TD flips → fold → compare.

The teacher's opcode trace is the functional specification. The student's
plates already have the right signs (100% accurate from extraction). The
magnitude gap creates a COMPUTATION gap. TD corrects the topology so the
student's residual stream projects onto the same combinator directions
as the teacher's.

After etching:
  - Fold delta into base (lossless)
  - Compare old vs new topology: per-stride flip counts, zone density,
    which plates changed most
  - The corrected checkpoint IS the etched topology — load it and train

Usage:
    uv run python scripts/v15/etch.py \\
        --checkpoint checkpoints/v15-extracted \\
        --max-steps 200 \\
        --td-flip-rate 0.002 \\
        --output-dir checkpoints/v15-etched

    # With trained weights overlay:
    uv run python scripts/v15/etch.py \\
        --checkpoint checkpoints/v15-extracted \\
        --train-checkpoint checkpoints/v15-dolma/step_0002000 \\
        --max-steps 200 \\
        --output-dir checkpoints/v15-etched

Session 177. License: MIT.
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
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from config import V15Config, Zone, ZONE_NAMES
from model import TensorStatechart, TernaryPlate
from load_checkpoint import load_statechart
from td import TernaryDescent, apply_td_flips, fold_and_reset


# ══════════════════════════════════════════════════════════════════════
# Logging
# ══════════════════════════════════════════════════════════════════════

def log(msg: str) -> None:
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Diverse input corpus for trace evaluation
# ══════════════════════════════════════════════════════════════════════

ETCH_INPUTS = [
    # Prose — diverse sentence structures
    "The cat sat on the mat and looked out the window at the birds.",
    "Every student who passed the final exam received a certificate.",
    "She believed that he thought that the answer was obviously wrong.",
    "The key that opened the door that led to the garden was lost.",
    "The gradient of the loss with respect to the weights is computed via backpropagation.",
    "If every teacher who knows a student that failed helps them all improve.",
    "Birds flew south for the winter as the leaves began to fall.",
    "The company that hired the lawyer who won the case prospered greatly.",
    "Clouds gathered in the sky promising rain by the afternoon today.",
    "In a quiet village nestled between rolling hills the old baker opened his shop.",
    # Factual — knowledge retrieval
    "The capital of France is",
    "The largest planet in our solar system is",
    "Water boils at a temperature of",
    "Shakespeare was born in the year",
    "The chemical symbol for gold is",
    # Compositional — nested structures
    "The student who read the book that the professor recommended passed.",
    "No politician who endorsed the candidate that lost the election won.",
    "A program that calls a function that calls another function must manage the stack.",
    "Every dog that chased a cat that scratched a mouse was punished.",
    "She told him that she thought that he believed that they would win.",
    # Lambda / formal
    "K x y = x",
    "B f g x = f (g x)",
    "Apply the identity function to any argument and get that argument back.",
    "The fixed point combinator Y satisfies Y f = f (Y f) for all f.",
    # Code
    "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
]


def tokenize_inputs(
    inputs: list[str],
    max_len: int = 64,
) -> mx.array:
    """Tokenize inputs for trace evaluation."""
    from transformers import AutoTokenizer

    for name in ["Qwen/Qwen3-0.6B", "Qwen/Qwen3-4B"]:
        try:
            tok = AutoTokenizer.from_pretrained(name, trust_remote_code=True)
            log(f"Tokenizer: {name}")
            break
        except Exception:
            continue
    else:
        raise RuntimeError("No Qwen tokenizer available")

    all_ids = []
    for text in inputs:
        ids = tok.encode(text, add_special_tokens=False)[:max_len]
        all_ids.append(ids)

    # Pad
    pad_len = max(len(ids) for ids in all_ids)
    padded = np.zeros((len(all_ids), pad_len), dtype=np.int32)
    for i, ids in enumerate(all_ids):
        padded[i, :len(ids)] = ids

    return mx.array(padded)


# ══════════════════════════════════════════════════════════════════════
# Crystal trace loss (same as train.py, standalone copy)
# ══════════════════════════════════════════════════════════════════════

def crystal_trace_loss(
    residuals: list,
    crystal_basis: mx.array,
) -> mx.array:
    """1 - mean(crystal_coherence) across strides.

    Coherence = fraction of residual energy in crystal subspace.
    Can exceed 1.0 when basis vectors aren't orthogonal (overlapping
    projections). Clamped to [0, 1] for stable loss range.
    """
    n_strides = min(len(residuals), crystal_basis.shape[0])
    if n_strides == 0:
        return mx.array(0.0)

    coherences = []
    for s in range(n_strides):
        r = residuals[s]
        basis_s = crystal_basis[s]
        proj = r @ basis_s.T
        crystal_energy = mx.mean(proj * proj)
        total_energy = mx.mean(r * r) + 1e-10
        coh = mx.minimum(crystal_energy / total_energy, mx.array(1.0))
        coherences.append(coh)

    return 1.0 - mx.mean(mx.stack(coherences))


# ══════════════════════════════════════════════════════════════════════
# Snapshot: capture plate state before etching
# ══════════════════════════════════════════════════════════════════════

def snapshot_plates(model: TensorStatechart) -> dict[str, np.ndarray]:
    """Capture sign topology of all plates as numpy arrays."""
    snap = {}
    for si, stride in enumerate(model.strides):
        for pname in ("gate_plate", "up_plate", "down_plate"):
            plate: TernaryPlate = getattr(stride.ffn, pname)
            key1 = f"s{si:02d}.{pname}.plate1"
            snap[key1] = np.array(mx.sign(plate.plate1))
            if plate.plate2 is not None:
                key2 = f"s{si:02d}.{pname}.plate2"
                snap[key2] = np.array(mx.sign(plate.plate2))
    return snap


def compare_topologies(
    before: dict[str, np.ndarray],
    after: dict[str, np.ndarray],
    model: TensorStatechart,
) -> dict:
    """Compare before/after plate topologies. Return structured diff."""
    total_flipped = 0
    total_positions = 0
    per_stride = {}
    per_zone: dict[str, dict] = {}

    for si, stride in enumerate(model.strides):
        zone_name = stride.zone.name
        stride_flipped = 0
        stride_total = 0

        for pname in ("gate_plate", "up_plate", "down_plate"):
            for suffix in ("plate1", "plate2"):
                key = f"s{si:02d}.{pname}.{suffix}"
                if key not in before or key not in after:
                    continue
                b = before[key]
                a = after[key]
                changed = np.sum(b != a)
                stride_flipped += int(changed)
                stride_total += b.size

        per_stride[si] = {
            "zone": zone_name,
            "flipped": stride_flipped,
            "total": stride_total,
            "frac": stride_flipped / max(stride_total, 1),
        }

        if zone_name not in per_zone:
            per_zone[zone_name] = {"flipped": 0, "total": 0}
        per_zone[zone_name]["flipped"] += stride_flipped
        per_zone[zone_name]["total"] += stride_total

        total_flipped += stride_flipped
        total_positions += stride_total

    for z in per_zone.values():
        z["frac"] = z["flipped"] / max(z["total"], 1)

    return {
        "total_flipped": total_flipped,
        "total_positions": total_positions,
        "total_frac": total_flipped / max(total_positions, 1),
        "per_stride": per_stride,
        "per_zone": per_zone,
    }


# ══════════════════════════════════════════════════════════════════════
# Trace-guided TD gradient computation
# ══════════════════════════════════════════════════════════════════════

def compute_trace_grads(
    model: TensorStatechart,
    input_ids: mx.array,
    crystal_basis: mx.array,
) -> dict[str, mx.array]:
    """Compute ∂(trace_loss)/∂(delta) for each delta plate.

    Strategy: for each delta plate, create a function that maps
    delta values → trace loss, and take its gradient. The gradient
    tells TD which positions to flip to improve crystal coherence.
    """
    delta_params = model.collect_delta_params()
    if not delta_params:
        return {}

    grad_dict: dict[str, mx.array] = {}

    for name, plate, which in delta_params:
        base_attr = "plate1" if which == "delta1" else "plate2"
        base_val = getattr(plate, base_attr)

        # We need to compute gradient of trace_loss w.r.t. delta.
        # The effective weight = base * delta. The trace loss depends on
        # the forward pass which uses effective weights.
        #
        # Strategy: compute the full model trace loss as a function of
        # this one delta, take gradient. This is expensive per-delta,
        # so we batch all deltas via a single forward pass and use
        # a simpler approximation: the trace loss gradient w.r.t. the
        # effective weight, projected back through the base.
        #
        # grad_delta[i,j] = grad_effective[i,j] * base[i,j]
        # (chain rule: d(base*delta)/d(delta) = base)
        #
        # We compute grad_effective via a single forward pass.
        pass

    # More efficient: single forward pass, get residuals, compute
    # trace loss gradient w.r.t. each stride's FFN output, then
    # project back to each plate's effective weight.
    #
    # But for correctness-first, we use the direct approach:
    # Forward pass → trace loss → backward through all parameters.
    # The delta plates participate in the forward via _effective().
    #
    # To get gradients through the deltas, we need to NOT use
    # stop_gradient. So we temporarily modify the forward path.

    # Approach: compute trace loss with deltas participating in
    # the computation graph (not stopped). We do this by computing
    # effective = base * delta as a differentiable operation, then
    # using it in the matmul.

    # Build a wrapper function that treats all deltas as inputs.
    all_deltas = {}
    delta_info = []  # (name, plate, which, base_attr)
    for name, plate, which in delta_params:
        base_attr = "plate1" if which == "delta1" else "plate2"
        all_deltas[name] = getattr(plate, which)
        delta_info.append((name, plate, which, base_attr))

    def trace_loss_fn(deltas_dict):
        """Compute trace loss with gradients flowing through deltas."""
        # Temporarily set effective weights (base * delta, differentiable)
        saved = {}
        for dname, plate, which, base_attr in delta_info:
            delta_val = deltas_dict[dname]
            base_val = getattr(plate, base_attr)
            # Replace the plate with effective = base * delta
            saved[(dname, base_attr)] = getattr(plate, base_attr)
            saved[(dname, which)] = getattr(plate, which)
            setattr(plate, base_attr, base_val * delta_val)
            # Disable delta so _effective() doesn't double-apply
            setattr(plate, which, None)

        result = model(input_ids, return_residuals=True)

        # Restore
        for dname, plate, which, base_attr in delta_info:
            setattr(plate, base_attr, saved[(dname, base_attr)])
            setattr(plate, which, saved[(dname, which)])

        if "residuals" not in result:
            return mx.array(0.0)
        return crystal_trace_loss(result["residuals"], crystal_basis)

    # Take gradient w.r.t. the deltas dict
    grad_fn = mx.grad(trace_loss_fn)
    grads = grad_fn(all_deltas)
    mx.eval(grads)

    return grads


# ══════════════════════════════════════════════════════════════════════
# Main etching loop
# ══════════════════════════════════════════════════════════════════════

def etch(args: argparse.Namespace) -> None:
    """Pure topology correction via trace-guided TD."""

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Load model ──────────────────────────────────────────────────
    log(f"Loading statechart from {args.checkpoint} ...")
    model = load_statechart(args.checkpoint, freeze_plates=True)
    config = model.config

    # Overlay trained weights if provided
    if args.train_checkpoint:
        weights_path = Path(args.train_checkpoint) / "weights.npz"
        if weights_path.exists():
            saved = mx.load(str(weights_path))
            model.load_weights(list(saved.items()), strict=False)
            log(f"Overlaid trained weights from {weights_path}")
        else:
            log(f"WARNING: no weights.npz at {weights_path}")

    # ── Crystal basis ────────────────────────────────────────────────
    basis_path = Path(args.checkpoint) / "crystal_basis_d_model.npz"
    if not basis_path.exists():
        log(f"ERROR: No crystal basis at {basis_path}")
        log(f"  Trace-guided etching requires crystal_basis_d_model.npz")
        sys.exit(1)

    basis_data = np.load(basis_path)
    crystal_basis_np = basis_data["per_stride_basis"]
    combinator_names = list(basis_data["combinator_names"])
    crystal_basis = mx.array(crystal_basis_np)
    log(f"Crystal basis: {crystal_basis_np.shape} ({', '.join(combinator_names[:4])}...)")

    # ── Snapshot BEFORE etching ──────────────────────────────────────
    log("Snapshotting topology BEFORE etching...")
    before = snapshot_plates(model)
    log(f"  Captured {len(before)} plate arrays")

    # ── Measure initial trace loss ──────────────────────────────────
    log("Tokenizing evaluation inputs...")
    input_ids = tokenize_inputs(ETCH_INPUTS, max_len=args.max_seq_len)
    log(f"  Input shape: {input_ids.shape}")

    log("Measuring initial trace loss...")
    result = model(input_ids, return_residuals=True)
    initial_loss = float(crystal_trace_loss(result["residuals"], crystal_basis).item())
    log(f"  Initial trace loss: {initial_loss:.6f}")

    # Per-stride coherence
    log("  Per-stride crystal coherence:")
    for si in range(min(len(result["residuals"]), crystal_basis.shape[0])):
        r = result["residuals"][si]
        basis_s = crystal_basis[si]
        proj = r @ basis_s.T
        ce = float(mx.mean(proj * proj).item())
        te = float(mx.mean(r * r).item()) + 1e-10
        coh = ce / te
        zone = model.strides[si].zone.name
        log(f"    stride {si:02d} ({zone:8s}): coherence={coh:.4f}")
    del result

    # ── Enable delta plates ──────────────────────────────────────────
    n_delta = model.enable_delta_plates()
    log(f"Delta plates enabled: {n_delta} modules")

    # ── TernaryDescent ───────────────────────────────────────────────
    td = TernaryDescent(
        flip_rate=args.td_flip_rate,
        warmup_steps=args.td_warmup,
        flip_interval=args.td_flip_interval,
        min_confidence=args.td_min_confidence,
    )
    log(f"TD: rate={args.td_flip_rate}, warmup={args.td_warmup}, "
        f"interval={args.td_flip_interval}, min_conf={args.td_min_confidence}")

    # ── Etching loop ─────────────────────────────────────────────────
    log(f"\n{'='*60}")
    log(f"  ETCHING: {args.max_steps} steps of trace-guided TD")
    log(f"{'='*60}\n")

    t0 = time.time()
    cumulative_flips = 0

    for step in range(1, args.max_steps + 1):
        # Compute trace loss gradient w.r.t. all delta plates
        trace_grads = compute_trace_grads(model, input_ids, crystal_basis)

        # Build TD params
        td_params = []
        for name, plate, which in model.collect_delta_params():
            delta_val = getattr(plate, which)
            base_attr = "plate1" if which == "delta1" else "plate2"
            base_val = getattr(plate, base_attr)
            grad = trace_grads.get(name)
            if grad is None or grad.shape != delta_val.shape:
                continue
            # no_block=True: direct +1 ↔ -1 flips, no zero staging.
            # Structural zeros are in the base plate. Active positions stay active.
            td_params.append((name, delta_val, grad, base_val, True))

        if not td_params:
            log(f"  Step {step}: no delta params with gradients — stopping")
            break

        # TD step
        td_result = td.step(td_params, training_step=step)
        n_flips = td_result.get("total_flips", 0)

        # Apply flips
        if n_flips > 0:
            apply_td_flips(model, td_result)
            mx.eval(model.parameters())

        cumulative_flips += n_flips

        # Log
        if step % args.log_every == 0 or n_flips > 0:
            # Measure current trace loss
            result = model(input_ids, return_residuals=True)
            current_loss = float(crystal_trace_loss(result["residuals"], crystal_basis).item())
            del result

            elapsed = time.time() - t0
            log(f"  step {step:>5d} | trace_loss={current_loss:.6f} | "
                f"flips={n_flips:>6d} | cumulative={cumulative_flips:>8d} | "
                f"warmup={td_result['in_warmup']} | "
                f"flip_step={td_result['is_flip_step']} | {elapsed:.1f}s")

            if td_result.get("is_flip_step") and n_flips > 0:
                # Per-module breakdown
                active_modules = sorted(
                    [(name, info["flips"]) for name, info in td_result["per_module"].items()
                     if info.get("flips", 0) > 0],
                    key=lambda x: -x[1],
                )[:5]
                if active_modules:
                    top_str = ", ".join(f"{n}:{f}" for n, f in active_modules)
                    log(f"         top flippers: {top_str}")

    elapsed_total = time.time() - t0
    log(f"\nEtching complete: {cumulative_flips:,} total flips in {elapsed_total:.1f}s")

    # ── Measure FINAL trace loss ─────────────────────────────────────
    result = model(input_ids, return_residuals=True)
    final_loss = float(crystal_trace_loss(result["residuals"], crystal_basis).item())
    log(f"\nTrace loss: {initial_loss:.6f} → {final_loss:.6f} (Δ={initial_loss - final_loss:+.6f})")

    log("  Per-stride crystal coherence AFTER:")
    for si in range(min(len(result["residuals"]), crystal_basis.shape[0])):
        r = result["residuals"][si]
        basis_s = crystal_basis[si]
        proj = r @ basis_s.T
        ce = float(mx.mean(proj * proj).item())
        te = float(mx.mean(r * r).item()) + 1e-10
        coh = ce / te
        zone = model.strides[si].zone.name
        log(f"    stride {si:02d} ({zone:8s}): coherence={coh:.4f}")
    del result

    # ── Fold delta into base ─────────────────────────────────────────
    log("\nFolding delta plates into base (lossless)...")
    model.fold_delta_plates()
    mx.eval(model.parameters())

    # Verify fold is lossless
    result = model(input_ids, return_residuals=True)
    post_fold_loss = float(crystal_trace_loss(result["residuals"], crystal_basis).item())
    log(f"  Post-fold trace loss: {post_fold_loss:.6f} (should ≈ {final_loss:.6f})")
    fold_delta = abs(post_fold_loss - final_loss)
    if fold_delta < 1e-4:
        log(f"  ✅ Fold is lossless (delta={fold_delta:.8f})")
    else:
        log(f"  ⚠  Fold has drift: {fold_delta:.6f}")
    del result

    # ── Snapshot AFTER and compare ───────────────────────────────────
    log("\nSnapshotting topology AFTER etching...")
    after = snapshot_plates(model)

    diff = compare_topologies(before, after, model)

    log(f"\n{'='*60}")
    log(f"  TOPOLOGY DIFF")
    log(f"{'='*60}")
    log(f"  Total sign changes: {diff['total_flipped']:,} / {diff['total_positions']:,} "
        f"({diff['total_frac']*100:.4f}%)")

    log(f"\n  Per zone:")
    for zname, zdata in diff["per_zone"].items():
        bar_len = min(40, int(zdata["frac"] * 4000))
        bar = "█" * bar_len + "░" * (40 - bar_len)
        log(f"    {zname:8s}: {zdata['flipped']:>8,} / {zdata['total']:>10,} "
            f"({zdata['frac']*100:.4f}%)  {bar}")

    log(f"\n  Per stride:")
    for si, sdata in sorted(diff["per_stride"].items()):
        if sdata["flipped"] == 0:
            continue
        bar_len = min(30, int(sdata["frac"] * 3000))
        bar = "█" * bar_len
        log(f"    stride {si:02d} ({sdata['zone']:8s}): {sdata['flipped']:>7,} "
            f"({sdata['frac']*100:.4f}%)  {bar}")

    # ── Save etched checkpoint ───────────────────────────────────────
    log(f"\nSaving etched checkpoint to {output_dir}...")

    # Copy extraction structure
    import shutil
    src = Path(args.checkpoint)
    for item in ["config.json", "v_proj.npy", "embedding.npz", "crystal_basis_d_model.npz"]:
        src_path = src / item
        if src_path.exists():
            shutil.copy2(src_path, output_dir / item)

    # Copy attention dir
    attn_src = src / "attention"
    attn_dst = output_dir / "attention"
    if attn_src.exists():
        if attn_dst.exists():
            shutil.rmtree(attn_dst)
        shutil.copytree(attn_src, attn_dst)

    # Save etched strides (new plates)
    strides_dir = output_dir / "strides"
    strides_dir.mkdir(parents=True, exist_ok=True)

    for si, stride in enumerate(model.strides):
        spec = config.stride_specs()[si]
        arrays = {}

        for matrix_name in ("gate", "up", "down"):
            plate: TernaryPlate = getattr(stride.ffn, f"{matrix_name}_plate")
            arrays[f"{matrix_name}_plate1"] = np.array(plate.plate1).astype(np.int8)
            arrays[f"{matrix_name}_gamma1"] = np.array(plate.gamma1)
            if plate.plate2 is not None:
                arrays[f"{matrix_name}_plate2"] = np.array(plate.plate2).astype(np.int8)
                arrays[f"{matrix_name}_gamma2"] = np.array(plate.gamma2)

        np.savez(strides_dir / f"stride_{si:02d}.npz", **arrays)

    # Save state
    state = {
        "source": str(args.checkpoint),
        "train_checkpoint": args.train_checkpoint,
        "etch_steps": args.max_steps,
        "td_flip_rate": args.td_flip_rate,
        "td_warmup": args.td_warmup,
        "td_flip_interval": args.td_flip_interval,
        "initial_trace_loss": initial_loss,
        "final_trace_loss": final_loss,
        "post_fold_trace_loss": post_fold_loss,
        "total_sign_changes": diff["total_flipped"],
        "per_zone": {z: {"flipped": d["flipped"], "frac": d["frac"]}
                     for z, d in diff["per_zone"].items()},
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    with open(output_dir / "etch_state.json", "w") as f:
        json.dump(state, f, indent=2)

    # Save topology diff as npz for analysis
    diff_arrays = {}
    for key in before:
        if key in after:
            diff_arrays[key] = (before[key] != after[key]).astype(np.uint8)
    np.savez_compressed(output_dir / "topology_diff.npz", **diff_arrays)

    log(f"\n✅ Etched checkpoint saved to {output_dir}")
    log(f"   Load with: load_statechart('{output_dir}')")


# ══════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="v15 Trace-Guided Etching — pure topology correction",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    p.add_argument("--checkpoint", default="checkpoints/v15-extracted",
                   help="Path to extracted v15 checkpoint (base plates)")
    p.add_argument("--train-checkpoint", default=None,
                   help="Optional trained weights to overlay (e.g. step_0002000)")
    p.add_argument("--output-dir", default="checkpoints/v15-etched",
                   help="Output directory for etched checkpoint")

    # TD hyperparameters
    p.add_argument("--max-steps", type=int, default=200,
                   help="Number of TD etching steps")
    p.add_argument("--td-flip-rate", type=float, default=0.002,
                   help="TD flip rate (fraction of weights per flip step)")
    p.add_argument("--td-warmup", type=int, default=10,
                   help="TD warmup steps (accumulate before flipping)")
    p.add_argument("--td-flip-interval", type=int, default=5,
                   help="Steps between TD flip commits")
    p.add_argument("--td-min-confidence", type=float, default=0.3,
                   help="Minimum SNR for a flip candidate")

    # Input control
    p.add_argument("--max-seq-len", type=int, default=64,
                   help="Max sequence length for trace inputs")

    # Logging
    p.add_argument("--log-every", type=int, default=5,
                   help="Log metrics every N steps")

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    log("v15 Trace-Guided Etching — Pure Topology Correction")
    log(f"Args: {vars(args)}")

    etch(args)


if __name__ == "__main__":
    main()
