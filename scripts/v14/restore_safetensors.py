"""Restore safetensors live files from an npz checkpoint.

Usage:
    uv run python scripts/v14/restore_safetensors.py \\
        --checkpoint checkpoints/v14-mmap/step_004000 \\
        --safetensors-dir checkpoints/v14-mmap

This rebuilds the safetensors working copy (delta.safetensors,
training.safetensors, state.json) from a frozen npz checkpoint so
training can resume in safetensors mode.

base.safetensors is NEVER touched — it was created during extraction
and must stay immutable.

The npz checkpoint is the source of truth. After restore, the
safetensors files are consistent with the checkpoint at the stored step.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
from mlx.utils import tree_flatten, tree_unflatten

sys.path.insert(0, str(Path(__file__).parent))

from config import V14Config
from safetensors_store import SafetensorsStore
from ternary import (
    freeze_ternary_weights,
    restore_ternary,
)
from td import (
    freeze_delta_architecture,
)
from train_td import create_model_with_deltas


def main():
    parser = argparse.ArgumentParser(
        description="Restore safetensors from npz checkpoint",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--checkpoint", required=True,
        help="Path to npz checkpoint directory (e.g. checkpoints/v14-mmap/step_004000)",
    )
    parser.add_argument(
        "--safetensors-dir", required=True,
        help="Path to safetensors directory to restore into",
    )
    parser.add_argument(
        "--convert-ffn", action="store_true",
        help="Include FFN delta modules (must match training config)",
    )
    parser.add_argument(
        "--extracted-model-path", type=str, default=None,
        help="Path to extracted base plates (default: from config)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Verify checkpoint without writing safetensors",
    )
    args = parser.parse_args()

    ckpt_dir = Path(args.checkpoint).resolve()
    st_dir = Path(args.safetensors_dir).resolve()

    # ── Validate checkpoint ───────────────────────────────────
    model_path = ckpt_dir / "model.npz"
    opt_path = ckpt_dir / "optimizer.npz"
    state_path = ckpt_dir / "state.json"

    if not model_path.exists():
        print(f"❌ model.npz not found in {ckpt_dir}", file=sys.stderr)
        sys.exit(1)
    if not opt_path.exists():
        print(f"❌ optimizer.npz not found in {ckpt_dir}", file=sys.stderr)
        sys.exit(1)
    if not state_path.exists():
        print(f"❌ state.json not found in {ckpt_dir}", file=sys.stderr)
        sys.exit(1)

    with open(state_path) as f:
        saved_state = json.load(f)
    step = saved_state.get("step", 0)

    print(f"{'='*72}", file=sys.stderr)
    print(f"  Restore safetensors from npz checkpoint", file=sys.stderr)
    print(f"  Checkpoint: {ckpt_dir} (step {step})", file=sys.stderr)
    print(f"  Target:     {st_dir}", file=sys.stderr)
    print(f"{'='*72}", file=sys.stderr)

    # ── Validate safetensors dir ──────────────────────────────
    base_st = st_dir / "base.safetensors"
    if not base_st.exists():
        print(f"❌ base.safetensors not found in {st_dir}", file=sys.stderr)
        print(f"   This is created during extraction and must exist.", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(f"\n✅ Dry run: checkpoint is valid. Would restore to {st_dir}.", file=sys.stderr)
        sys.exit(0)

    # ── Create model (same pipeline as train_td.py) ───────────
    cfg = V14Config()
    if args.extracted_model_path:
        cfg.extracted_model_path = args.extracted_model_path
    cfg.__post_init__()

    print(f"\n📦 Creating model...", file=sys.stderr)
    model, delta_modules = create_model_with_deltas(
        cfg,
        convert_ffn=args.convert_ffn,
        skip_base_load=False,  # Load base from extraction, not safetensors
    )

    # ── Load checkpoint weights ───────────────────────────────
    print(f"📂 Loading model weights from {model_path}...", file=sys.stderr)
    model.load_weights(str(model_path), strict=False)
    mx.eval(model.parameters())
    restore_ternary(model)
    freeze_ternary_weights(model)
    freeze_delta_architecture(model)

    # ── Set up Adam + load optimizer state ────────────────────
    print(f"📂 Loading optimizer state from {opt_path}...", file=sys.stderr)
    adam = optim.AdamW(
        learning_rate=cfg.lr,
        weight_decay=cfg.weight_decay,
        betas=[0.9, 0.999],
    )

    # Warm-up pass to initialize Adam state structure
    # (same as train_td.py — Adam needs one update to know the param shapes)
    dummy_ids = mx.zeros((1, 32), dtype=mx.int32)
    dummy_tgts = mx.zeros((1, 32), dtype=mx.int32)
    from train_td import loss_fn
    loss_and_grad = nn.value_and_grad(model, loss_fn)
    lv, grads = loss_and_grad(model, dummy_ids, dummy_tgts)
    mx.eval(lv, grads)
    from train_td import zero_ternary_grads
    grads = zero_ternary_grads(model, grads)
    adam.update(model, grads)
    mx.eval(model.parameters(), adam.state)
    restore_ternary(model)

    # Re-load model weights (undo the dummy gradient step)
    model.load_weights(str(model_path), strict=False)
    mx.eval(model.parameters())
    restore_ternary(model)

    # Load saved optimizer state
    saved_opt = dict(mx.load(str(opt_path)))
    current_flat = dict(tree_flatten(adam.state))
    n_restored = 0
    n_skipped = 0
    for k, v in saved_opt.items():
        if k in current_flat and current_flat[k].shape == v.shape:
            current_flat[k] = v
            n_restored += 1
        else:
            n_skipped += 1
    adam.state = tree_unflatten(list(current_flat.items()))
    mx.eval(adam.state)
    print(f"  Optimizer: {n_restored} arrays restored, {n_skipped} skipped", file=sys.stderr)

    # ── Sync to safetensors ───────────────────────────────────
    print(f"\n🔄 Opening SafetensorsStore: {st_dir}", file=sys.stderr)
    store = SafetensorsStore(str(st_dir))

    print(f"🔄 Syncing model + optimizer → safetensors...", file=sys.stderr)

    # Build extra_state from checkpoint's state.json
    extra_state = {}
    for key in ["n_reductions", "total_td_flips", "td_step_count", "td_active",
                "structured_warmup_done", "structured_warmup_steps",
                "target_mix_ratio", "train_losses_last50", "data_loader",
                "crystal_ema"]:
        if key in saved_state:
            extra_state[key] = saved_state[key]

    store.sync(model, adam, step, extra_state=extra_state)

    # Verify
    verify_state = store.load_state()
    verify_step = verify_state.get("step", -1)

    print(f"\n{'='*72}", file=sys.stderr)
    print(f"✅ Restore complete.", file=sys.stderr)
    print(f"   Safetensors now at step {verify_step}", file=sys.stderr)
    print(f"   delta.safetensors    → updated", file=sys.stderr)
    print(f"   training.safetensors → updated", file=sys.stderr)
    print(f"   state.json           → step {verify_step}", file=sys.stderr)
    print(f"   base.safetensors     → untouched (frozen)", file=sys.stderr)
    print(f"\n   Resume training with:", file=sys.stderr)
    print(f"   uv run python scripts/v14/train_td.py --safetensors-dir {st_dir} ...", file=sys.stderr)
    print(f"{'='*72}", file=sys.stderr)


if __name__ == "__main__":
    main()
