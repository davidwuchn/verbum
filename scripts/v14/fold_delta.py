"""Fold delta plates into base plates — lossless reduction.

Takes a checkpoint with DeltaTernaryLinear modules and:
1. Calls reduce() on each: new_base = base ⊙ delta, delta = all +1
2. Saves the folded model as a new checkpoint ready for restart

The effective weights are UNCHANGED — this is a lossless operation.
After folding, delta plates are all +1 (pass-through), meaning
TernaryDescent starts fresh with a new base that incorporates all
the routing corrections discovered so far.

Usage:
  uv run python scripts/v14/fold_delta.py \
    --source checkpoints/v14-td/step_001500 \
    --output checkpoints/v14-td/step_001500_folded

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import numpy as np
from mlx.utils import tree_flatten

sys.path.insert(0, str(Path(__file__).parent))

from config import V14Config
from model import V14Model
from ternary import (
    restore_ternary,
    freeze_ternary_weights,
    unpack_ternary_mlx,
    pack_ternary_mlx,
    count_ternary_weights,
)
from td import (
    DeltaTernaryLinear,
    convert_to_delta,
    collect_delta_params,
    freeze_delta_architecture,
)


def main():
    parser = argparse.ArgumentParser(description="Fold delta plates into base plates (lossless)")
    parser.add_argument(
        "--source", type=str, required=True,
        help="Source checkpoint directory (e.g. checkpoints/v14-td/step_001500)",
    )
    parser.add_argument(
        "--output", type=str, required=True,
        help="Output directory for folded checkpoint",
    )
    parser.add_argument(
        "--extracted-model-path", type=str, default=None,
        help="Override extracted model path (default: from config)",
    )
    args = parser.parse_args()

    source_path = Path(args.source).resolve()
    output_path = Path(args.output).resolve()
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"{'='*60}")
    print(f"  Delta Fold — Lossless Reduction")
    print(f"  Source:  {source_path}")
    print(f"  Output:  {output_path}")
    print(f"{'='*60}\n")

    # ── Config ────────────────────────────────────────────────
    cfg = V14Config()
    if args.extracted_model_path:
        cfg.extracted_model_path = args.extracted_model_path

    # ── Build model + load base plates ────────────────────────
    print("Building model...", flush=True)
    model = V14Model(cfg)

    base_path = Path(cfg.extracted_model_path).resolve()
    if base_path.exists():
        model.load_weights(str(base_path), strict=False)
        mx.eval(model.parameters())
        restore_ternary(model)
        freeze_ternary_weights(model)
        print(f"  Base plates loaded from {base_path}")

    # ── Convert to delta architecture ─────────────────────────
    convert_to_delta(model, include_prefixes=("shared_stride_stack",))
    freeze_delta_architecture(model)

    # ── Load checkpoint weights ───────────────────────────────
    model_path = source_path / "model.npz"
    if not model_path.exists():
        print(f"  ✗ No model.npz found at {model_path}")
        sys.exit(1)

    model.load_weights(str(model_path), strict=False)
    mx.eval(model.parameters())
    restore_ternary(model)
    freeze_ternary_weights(model)
    print(f"  Checkpoint weights loaded from {model_path}")

    # ── Load delta plates ─────────────────────────────────────
    delta_path = source_path / "delta_plates.npz"
    delta_modules = collect_delta_params(model)

    if delta_path.exists():
        delta_data = dict(np.load(str(delta_path), allow_pickle=False))
        n_loaded = 0
        for path, dtl in delta_modules:
            delta_key = path.replace(".", "_")
            # New format: packed uint32
            packed_key = f"{delta_key}_delta_packed"
            # Old format: unpacked int8
            old_key = f"{delta_key}_delta"
            if packed_key in delta_data:
                dtl.delta_weight = mx.array(delta_data[packed_key])
                mx.eval(dtl.delta_weight)
                n_loaded += 1
            elif old_key in delta_data:
                delta_int8 = mx.array(delta_data[old_key].astype(np.int8))
                dtl.delta_weight = pack_ternary_mlx(delta_int8)
                mx.eval(dtl.delta_weight)
                n_loaded += 1
        print(f"  Delta plates loaded: {n_loaded}/{len(delta_modules)}")
    else:
        print(f"  No delta_plates.npz — using delta from model.npz")

    # ── Pre-fold stats ────────────────────────────────────────
    print(f"\n{'─'*50}")
    print(f"  PRE-FOLD DELTA STATS")
    print(f"{'─'*50}")
    total_positions = 0
    total_flipped = 0
    for path, dtl in delta_modules:
        ds = dtl.delta_stats()
        n = dtl.out_features * dtl.in_features
        total_positions += n
        flipped = int(ds["flip_frac"] * n)
        total_flipped += flipped
        if ds["flip_frac"] > 0:
            print(f"  {path}: {ds['flip_frac']*100:.1f}% flipped ({flipped:,}/{n:,})")

    print(f"  TOTAL: {total_flipped:,}/{total_positions:,} flipped"
          f" ({total_flipped/total_positions*100:.2f}%)")

    # ── Sample effective weights before fold (for verification) ─
    # Pick the hottest module for verification
    verify_path = None
    verify_pre = None
    for path, dtl in delta_modules:
        ds = dtl.delta_stats()
        if ds["flip_frac"] > 0.4:  # layer 4 is ~43%
            verify_path = path
            verify_pre = dtl._compute_effective()
            mx.eval(verify_pre)
            break

    if verify_path is None and delta_modules:
        verify_path = delta_modules[0][0]
        verify_pre = delta_modules[0][1]._compute_effective()
        mx.eval(verify_pre)

    # ── FOLD: reduce all deltas ───────────────────────────────
    print(f"\n🔄 Folding delta into base...", flush=True)
    t0 = time.time()

    n_folded = 0
    for path, dtl in delta_modules:
        dtl.reduce()
        n_folded += 1

    mx.eval(model.parameters())
    elapsed = time.time() - t0
    print(f"  Folded {n_folded} modules in {elapsed:.1f}s")

    # ── Verify: effective weights unchanged ───────────────────
    if verify_path is not None:
        for path, dtl in delta_modules:
            if path == verify_path:
                verify_post = dtl._compute_effective()
                mx.eval(verify_post)
                # After fold, delta=+1, so effective = base ⊙ (+1) = base
                # which should equal the pre-fold effective
                pre_unpacked = unpack_ternary_mlx(verify_pre)
                post_unpacked = unpack_ternary_mlx(verify_post)
                diff = int((pre_unpacked != post_unpacked).sum().item())
                if diff == 0:
                    print(f"  ✓ Verified lossless: {verify_path} (0 differences)")
                else:
                    print(f"  ✗ MISMATCH: {verify_path} has {diff} differences!")
                    sys.exit(1)
                break

    # ── Post-fold stats ───────────────────────────────────────
    print(f"\n{'─'*50}")
    print(f"  POST-FOLD DELTA STATS")
    print(f"{'─'*50}")
    all_clean = True
    for path, dtl in delta_modules:
        ds = dtl.delta_stats()
        if ds["keep_frac"] != 1.0:
            print(f"  ✗ {path}: keep={ds['keep_frac']:.4f} (expected 1.0)")
            all_clean = False
    if all_clean:
        print(f"  ✓ All {n_folded} modules: delta = all +1 (clean reset)")

    # ── Save folded model ─────────────────────────────────────
    print(f"\n💾 Saving folded checkpoint to {output_path}...", flush=True)

    # Model weights (includes folded base_weight + reset delta_weight)
    flat_weights = dict(tree_flatten(model.parameters()))
    mx.savez(str(output_path / "model.npz"), **flat_weights)
    model_size = (output_path / "model.npz").stat().st_size
    print(f"  model.npz: {model_size / 1024 / 1024:.1f} MB")

    # Delta plates (all +1, packed, deduplicated)
    delta_snapshots = {}
    for path, dtl in delta_modules:
        delta_key = path.replace(".", "_")
        mx.eval(dtl.delta_weight)
        delta_snapshots[f"{delta_key}_delta_packed"] = dtl.delta_weight
        ds = dtl.delta_stats()
        total = dtl.out_features * dtl.in_features
        delta_snapshots[f"{delta_key}_stats"] = mx.array([
            ds["keep_frac"] * total,
            ds["flip_frac"] * total,
            ds["block_frac"] * total,
            float(total),
        ])
    mx.savez(str(output_path / "delta_plates.npz"), **delta_snapshots)
    delta_size = (output_path / "delta_plates.npz").stat().st_size
    print(f"  delta_plates.npz: {delta_size / 1024 / 1024:.1f} MB"
          f" (was 355.6 MB before fix)")

    # State: copy source state + add fold metadata
    source_state_path = source_path / "state.json"
    if source_state_path.exists():
        state = json.loads(source_state_path.read_text())
    else:
        state = {}

    state["fold_metadata"] = {
        "source_checkpoint": str(source_path),
        "source_step": state.get("step", "?"),
        "total_flipped_before_fold": total_flipped,
        "total_positions": total_positions,
        "flip_pct_before_fold": total_flipped / total_positions * 100,
        "fold_timestamp": time.time(),
        "n_modules_folded": n_folded,
    }
    # Reset TD counters for fresh start
    state["n_reductions"] = state.get("n_reductions", 0) + 1
    state["total_td_flips"] = 0  # reset — delta is clean
    state["td_step_count"] = 0

    (output_path / "state.json").write_text(json.dumps(state, indent=2, default=str))
    print(f"  state.json written")

    # Copy optimizer state (Adam moments are still valid for continuous params)
    opt_source = source_path / "optimizer.npz"
    if opt_source.exists():
        import shutil
        shutil.copy2(str(opt_source), str(output_path / "optimizer.npz"))
        print(f"  optimizer.npz copied from source")

    print(f"\n{'='*60}")
    print(f"  FOLD COMPLETE")
    print(f"  {total_flipped:,} flipped positions absorbed into base")
    print(f"  Delta plates reset to all +1")
    print(f"  Ready for restart with --convert-ffn")
    print(f"  Resume from: --resume {output_path}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
