"""Profile a single training step to find the bottleneck.

Usage:
  uv run python scripts/v14/profile_step.py [--batch-size 1] [--batch-size 2]

Measures: data loading, forward pass, backward pass, TD step, Adam step.
Tests batch_size=1 and batch_size=2 to see where time differs.

License: MIT
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from config import V14Config
from data import ShardedDataLoader
from model import V14Model
from ternary import (
    freeze_ternary_weights,
    restore_ternary,
    zero_ternary_grads,
    unpack_ternary_mlx,
)
from td import (
    TernaryDescent,
    convert_to_delta,
    collect_delta_params,
    freeze_delta_architecture,
    decompose_gradient,
    DeltaTernaryLinear,
)


def time_section(name, fn):
    """Time a function, returning (result, elapsed_ms)."""
    mx.eval()  # drain any pending work
    t0 = time.perf_counter()
    result = fn()
    mx.eval()  # force completion
    elapsed = (time.perf_counter() - t0) * 1000
    return result, elapsed


def profile_one_step(cfg, model, delta_modules, td, loader, grad_accum):
    """Profile a single training step broken into phases."""
    loss_and_grad = nn.value_and_grad(model, lambda m, x, t: m(x, t)[1])

    timings = {}

    # Phase 1: Data loading (all microbatches)
    batches = []
    t0 = time.perf_counter()
    for _ in range(grad_accum):
        batch = loader.next_batch()
        if batch is None:
            raise RuntimeError("Ran out of data")
        batches.append(batch)
    timings["data_load_ms"] = (time.perf_counter() - t0) * 1000

    # Phase 2: Forward + backward (with grad accumulation)
    accum_grads = None
    total_loss = 0.0

    mx.eval()
    t_fb_start = time.perf_counter()

    for micro_idx, (ids_np, tgts_np) in enumerate(batches):
        ids = mx.array(ids_np)
        tgts = mx.array(tgts_np)

        lv, grads = loss_and_grad(model, ids, tgts)
        mx.eval(lv, grads)
        total_loss += float(lv.item())

        if accum_grads is None:
            accum_grads = grads
        else:
            from mlx.utils import tree_map
            accum_grads = tree_map(lambda a, b: a + b, accum_grads, grads)

    timings["fwd_bwd_ms"] = (time.perf_counter() - t_fb_start) * 1000
    timings["fwd_bwd_per_micro_ms"] = timings["fwd_bwd_ms"] / grad_accum

    from mlx.utils import tree_map, tree_flatten
    accum_grads = tree_map(lambda g: g / grad_accum, accum_grads)

    # Phase 3: Grad processing (zero ternary, clip, decompose)
    mx.eval()
    t_grad = time.perf_counter()
    accum_grads = zero_ternary_grads(model, accum_grads)

    flat_grads = [g for _, g in tree_flatten(accum_grads) if isinstance(g, mx.array)]
    grad_sq = sum(float(mx.sum(g * g).item()) for g in flat_grads)
    import math
    grad_norm = math.sqrt(max(grad_sq, 0.0))
    if grad_norm > 1.0:
        s = 1.0 / (grad_norm + 1e-8)
        accum_grads = tree_map(lambda g: g * s, accum_grads)
    mx.eval()
    timings["grad_process_ms"] = (time.perf_counter() - t_grad) * 1000

    # Phase 4: TD step (moment accumulation — not a flip step usually)
    mx.eval()
    t_td = time.perf_counter()

    # Build TD inputs (simplified — just accumulate moments)
    td_inputs = []
    for path, dtl in delta_modules:
        # Create a fake gradient for TD (from the accumulated grads)
        grad_shape = (dtl.out_features, dtl.in_features)
        fake_grad = mx.zeros(grad_shape)  # placeholder
        no_block = path.startswith("shared_stride_stack")
        td_inputs.append((path, dtl.delta_weight, fake_grad, dtl.base_weight, no_block))

    td_result = td.step(td_inputs)
    mx.eval()
    timings["td_step_ms"] = (time.perf_counter() - t_td) * 1000

    # Phase 5: Adam step
    import mlx.optimizers as optim
    adam = optim.AdamW(learning_rate=3e-4, weight_decay=0.01)
    # Warm up adam
    adam.update(model, accum_grads)
    mx.eval(model.parameters(), adam.state)
    restore_ternary(model)

    mx.eval()
    t_adam = time.perf_counter()
    adam.update(model, accum_grads)
    mx.eval(model.parameters(), adam.state)
    restore_ternary(model)
    timings["adam_step_ms"] = (time.perf_counter() - t_adam) * 1000

    # Phase 6: _compute_effective overhead (delta matmul)
    mx.eval()
    t_eff = time.perf_counter()
    for _, dtl in delta_modules:
        eff = dtl._compute_effective()
        mx.eval(eff)
    timings["compute_effective_all_ms"] = (time.perf_counter() - t_eff) * 1000

    timings["total_loss"] = total_loss / grad_accum
    timings["grad_norm"] = grad_norm
    timings["tokens_per_step"] = cfg.batch_size * grad_accum * cfg.seq_len

    return timings


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=None,
                        help="Override batch size (test 1 vs 2)")
    parser.add_argument("--grad-accum", type=int, default=None,
                        help="Override grad accumulation steps")
    parser.add_argument("--n-warmup", type=int, default=1,
                        help="Warmup steps before timing")
    parser.add_argument("--n-measure", type=int, default=3,
                        help="Steps to average")
    args = parser.parse_args()

    # Test configurations
    configs = []
    if args.batch_size is not None:
        configs.append((args.batch_size, args.grad_accum or (8 // args.batch_size)))
    else:
        configs = [(1, 8), (2, 4)]  # same effective batch

    for batch_size, grad_accum in configs:
        print(f"\n{'='*70}")
        print(f"  PROFILING: batch_size={batch_size}  grad_accum={grad_accum}"
              f"  effective_batch={batch_size * grad_accum}")
        print(f"  tokens_per_step={batch_size * grad_accum * 4096:,}")
        print(f"{'='*70}\n")

        cfg = V14Config()
        cfg.batch_size = batch_size
        cfg.grad_accum = grad_accum

        # Build model
        print("Building model...", flush=True)
        model = V14Model(cfg)

        # Load base plates
        base_path = Path(cfg.extracted_model_path).resolve()
        if base_path.exists():
            model.load_weights(str(base_path), strict=False)
            mx.eval(model.parameters())
            from ternary import restore_ternary as rt
            rt(model)
            freeze_ternary_weights(model)
            print(f"  Base plates loaded")

        # Convert to delta
        convert_to_delta(model, include_prefixes=("shared_stride_stack",))
        freeze_delta_architecture(model)
        freeze_ternary_weights(model)
        delta_modules = collect_delta_params(model)
        print(f"  Delta modules: {len(delta_modules)}")

        # Load checkpoint weights
        ckpt = Path("checkpoints/v14-td/step_001500/model.npz")
        if ckpt.exists():
            model.load_weights(str(ckpt), strict=False)
            mx.eval(model.parameters())
            restore_ternary(model)
            freeze_ternary_weights(model)
            print(f"  Checkpoint loaded")

        # Data loader
        loader = ShardedDataLoader(
            data_dir=cfg.data_dir,
            batch_size=batch_size,
            seq_len=cfg.seq_len,
            shard_start=0,
            shard_end=cfg.n_train_shards,
            seed=42,
        )

        td = TernaryDescent(
            flip_rate=0.001, warmup_steps=25,
            min_confidence=0.3, flip_interval=10,
        )

        # Warmup
        print(f"\n  Warming up ({args.n_warmup} steps)...", flush=True)
        for _ in range(args.n_warmup):
            timings = profile_one_step(cfg, model, delta_modules, td, loader, grad_accum)
        print(f"  Warmup done (loss={timings['total_loss']:.3f})")

        # Measure
        print(f"\n  Measuring ({args.n_measure} steps)...\n", flush=True)
        all_timings = []
        for i in range(args.n_measure):
            timings = profile_one_step(cfg, model, delta_modules, td, loader, grad_accum)
            all_timings.append(timings)
            tok_per_sec = timings['tokens_per_step'] / (
                (timings['data_load_ms'] + timings['fwd_bwd_ms'] +
                 timings['grad_process_ms'] + timings['td_step_ms'] +
                 timings['adam_step_ms']) / 1000
            )
            print(f"  Step {i+1}: total_wall={sum(v for k,v in timings.items() if k.endswith('_ms')):.0f}ms"
                  f"  fwd+bwd={timings['fwd_bwd_ms']:.0f}ms"
                  f"  data={timings['data_load_ms']:.0f}ms"
                  f"  adam={timings['adam_step_ms']:.0f}ms"
                  f"  td={timings['td_step_ms']:.0f}ms"
                  f"  ~{tok_per_sec:.0f} tok/s", flush=True)

        # Average
        print(f"\n  {'AVERAGES':=^50}")
        avg = {}
        for key in all_timings[0]:
            if key.endswith("_ms"):
                avg[key] = sum(t[key] for t in all_timings) / len(all_timings)

        total_step_ms = sum(avg.values())
        for key in sorted(avg.keys(), key=lambda k: -avg[k]):
            pct = avg[key] / total_step_ms * 100
            print(f"    {key:<30s}  {avg[key]:>8.1f} ms  ({pct:>5.1f}%)")
        print(f"    {'TOTAL':<30s}  {total_step_ms:>8.1f} ms")

        tokens = batch_size * grad_accum * cfg.seq_len
        print(f"\n    tokens/step: {tokens:,}")
        print(f"    tok/s: {tokens / (total_step_ms / 1000):.0f}")
        print(f"    ms/microbatch (fwd+bwd): {avg['fwd_bwd_per_micro_ms']:.1f} ms")
        print(f"    compute_effective (all 70): {avg['compute_effective_all_ms']:.1f} ms")


if __name__ == "__main__":
    main()
