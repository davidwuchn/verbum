"""
Etch Strategy Probe — fast A/B/C experiments for etching parameters.

Runs multiple short training variants (300 steps each) with different
etch settings and compares:
  - Final CE (does etching help or hurt language modeling?)
  - Loss stability (does etching cause spikes?)
  - Etch activity (how many flips, what tempo?)
  - Dispatch balance (does etching help or fight the lattice?)

Uses reduced seq_len and grad_accum for speed (~2-3 min per variant).
Each variant gets a fresh model from the same random seed.

Usage:
    uv run python scripts/v12/probe_etch_strategy.py
    uv run python scripts/v12/probe_etch_strategy.py --steps 500 --suite timing
    uv run python scripts/v12/probe_etch_strategy.py --suite all

License: MIT
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
import sys
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

os.environ["PYTHONUNBUFFERED"] = "1"

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np
from mlx.utils import tree_flatten, tree_map

sys.path.insert(0, str(Path(__file__).parent))

from config import V12Config
from data import ShardedDataLoader
from model import V12Model, create_model, count_parameters
from ternary import (
    freeze_ternary_weights,
    zero_ternary_grads,
    restore_ternary,
    count_ternary_weights,
    init_etch_states,
    accumulate_etch_heat,
    update_signal_planes,
    etch_check,
    _walk_ternary_modules,
    TernaryLinear,
    surgical_adam_decay_for_etch,
)
from train import (
    E_IRREDUCIBLE, LOG_V,
    loss_fn, normalize_shared_grads, cosine_lr, holo_schedule,
    _compute_etch_threshold_multipliers,
    MODULE_PASS_MAP,
)


# ═══════════════════════���════════════════════════��═════════════════
# Experiment definitions
# ════════════════════════════════════════════════��═════════════════

@dataclass
class EtchVariant:
    """One etch experiment configuration."""
    name: str
    description: str
    # Override fields (None = use base config)
    etch_warmup: int | None = None
    etch_interval: int | None = None
    etch_signal_interval: int | None = None
    etch_heat_alpha: float | None = None
    etch_reset_after_flip: bool | None = None
    etch_max_flips_per_event: int | None = None
    etch_consensus: int | None = None
    pass_etch_multiplier: tuple | None = None
    use_etching: bool | None = None
    # Dispatch-gated etching (new)
    etch_kl_gate: float | None = None  # only etch when kl_loss < this value


# ── Core experiment: the 4 questions that matter ──────────────
CORE_SUITE = [
    EtchVariant(
        name="no_etch",
        description="Baseline: no etching at all",
        use_etching=False,
    ),
    EtchVariant(
        name="current",
        description="Current: interval=2, reset=True, 200 flips",
    ),
    EtchVariant(
        name="no_reset",
        description="No reset after flip: continuous signal accumulation",
        etch_reset_after_flip=False,
        etch_heat_alpha=0.95,
    ),
    EtchVariant(
        name="kl_gated",
        description="Only etch when kl_loss < 2.0 (dispatch is balanced)",
        etch_kl_gate=2.0,
    ),
]

SUITES = {
    "core": CORE_SUITE,
}


# ══════════════════════════════════════════════════════════════════
# Run one variant
# ════════════════════════════════════════════════════��═════════════

@dataclass
class RunResult:
    """Collected metrics from one experiment run."""
    name: str
    description: str
    final_ce: float
    mean_ce_last50: float
    min_ce: float
    total_flips: int
    n_etch_events: int
    mean_etch_tempo: float
    # Loss stability: max CE spike in 5-step window after an etch
    max_post_etch_spike: float
    # Dispatch at end
    dispatch_K: float
    dispatch_I: float
    dispatch_B: float
    dispatch_C: float
    kl_loss_final: float
    elapsed_sec: float
    steps_run: int


def run_variant(
    variant: EtchVariant,
    total_steps: int = 300,
    seed: int = 42,
) -> RunResult:
    """Run one etch strategy variant and collect metrics."""

    # ── Config ───────────────────���────────────────────────────
    cfg = V12Config()
    # Speed overrides for probe (fast iteration)
    cfg.seq_len = 1024
    cfg.max_seq_len = 1024
    cfg.batch_size = 2
    cfg.grad_accum = 1
    cfg.total_steps = total_steps
    cfg.holo_lambda = 0.1
    cfg.log_interval = 50
    cfg.eval_interval = 99999  # no eval during probe
    cfg.checkpoint_interval = 99999  # no checkpoint
    cfg.use_evolution = False
    cfg.use_relational_loss = False  # skip for speed

    # Apply variant overrides
    if variant.use_etching is not None:
        cfg.use_etching = variant.use_etching
    if variant.etch_warmup is not None:
        cfg.etch_warmup = variant.etch_warmup
    if variant.etch_interval is not None:
        cfg.etch_interval = variant.etch_interval
    if variant.etch_signal_interval is not None:
        cfg.etch_signal_interval = variant.etch_signal_interval
    if variant.etch_heat_alpha is not None:
        cfg.etch_heat_alpha = variant.etch_heat_alpha
    if variant.etch_reset_after_flip is not None:
        cfg.etch_reset_after_flip = variant.etch_reset_after_flip
    if variant.etch_max_flips_per_event is not None:
        cfg.etch_max_flips_per_event = variant.etch_max_flips_per_event
    if variant.etch_consensus is not None:
        cfg.etch_consensus = variant.etch_consensus
    if variant.pass_etch_multiplier is not None:
        cfg.pass_etch_multiplier = variant.pass_etch_multiplier

    # ── Model (deterministic init) ────────────────────────────
    mx.random.seed(seed)
    np.random.seed(seed)
    model = create_model(cfg)
    freeze_ternary_weights(model)
    total_ternary = count_ternary_weights(model)

    # ── Optimizer ───────────────────────────────────────��─────
    optimizer = optim.Adam(learning_rate=cfg.lr, betas=[0.9, 0.999])
    loss_and_grad = nn.value_and_grad(model, loss_fn)

    # ── Data (deterministic) ───────────────────────��──────────
    train_loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=cfg.batch_size,
        seq_len=cfg.seq_len,
        shard_start=0,
        shard_end=cfg.n_train_shards,
        seed=seed,
    )

    # ── Etch states ───────────────────────────────────────────
    etch_states = None
    if cfg.use_etching:
        etch_states = init_etch_states(model)

    # ── Warm up optimizer ─────────────────────────────────────
    ids_np, tgts_np = next(train_loader)
    ids = mx.array(ids_np)
    tgts = mx.array(tgts_np)
    lv, grads = loss_and_grad(model, ids, tgts)
    mx.eval(lv, grads)
    grads = normalize_shared_grads(grads)
    grads = zero_ternary_grads(model, grads)
    optimizer.update(model, grads)
    mx.eval(model.parameters(), optimizer.state)
    restore_ternary(model)

    # ── Training loop ─────────────────────���───────────────────
    t_start = time.time()
    ce_history = []
    total_flips = 0
    n_etch_events = 0
    etch_tempos = []
    post_etch_spikes = []
    last_kl_loss = 0.0

    for step in range(1, total_steps + 1):
        lr = cosine_lr(step, cfg.warmup_steps, cfg.total_steps,
                       cfg.lr, cfg.lr_floor_ratio)
        optimizer.learning_rate = lr

        holo_eff = holo_schedule(step, cfg)
        model._holo_lambda_effective = holo_eff

        # Forward + backward
        ids_np, tgts_np = next(train_loader)
        ids = mx.array(ids_np)
        tgts = mx.array(tgts_np)
        lv, grads = loss_and_grad(model, ids, tgts)
        mx.eval(lv, grads)

        step_loss = float(lv.item())
        total_loss = step_loss * (LOG_V - E_IRREDUCIBLE) + E_IRREDUCIBLE
        raw_ce = float(model._last_ce.item()) if hasattr(model, '_last_ce') else total_loss
        ce_history.append(raw_ce)

        # Track KL
        if hasattr(model, '_last_kl_loss'):
            mx.eval(model._last_kl_loss)
            last_kl_loss = float(model._last_kl_loss.item())

        # Etch heat accumulation
        if etch_states is not None:
            accumulate_etch_heat(model, grads, etch_states, alpha=cfg.etch_heat_alpha)

        # Normalize + zero ternary + clip + update
        grads = normalize_shared_grads(grads)
        grads = zero_ternary_grads(model, grads)
        # Gradient clipping
        grad_sq = [mx.sum(g * g) for _, g in tree_flatten(grads)]
        mx.eval(*grad_sq)
        grad_norm = sum(float(g) for g in grad_sq) ** 0.5
        if cfg.grad_clip > 0 and grad_norm > cfg.grad_clip:
            s = cfg.grad_clip / (grad_norm + 1e-8)
            grads = tree_map(lambda g: g * s, grads)

        optimizer.update(model, grads)
        mx.eval(model.parameters(), optimizer.state)
        restore_ternary(model)

        # ── Signal plane update ───────────────────────────────
        if (etch_states is not None
                and step >= cfg.etch_warmup
                and step % cfg.etch_signal_interval == 0):
            modules = list(_walk_ternary_modules(model))
            etch_thresh_mults = None
            if hasattr(cfg, 'pass_etch_multiplier') and cfg.pass_etch_multiplier:
                etch_thresh_mults = _compute_etch_threshold_multipliers(cfg, modules)
            update_signal_planes(
                etch_states, model,
                heat_thresholds=cfg.etch_heat_thresholds,
                etch_threshold_multipliers=etch_thresh_mults,
            )

        # ── Etch check ──────────────────────────────���─────────
        if (etch_states is not None
                and step >= cfg.etch_warmup
                and step % cfg.etch_interval == 0):

            # Dispatch-gated: skip if KL is too high
            if variant.etch_kl_gate is not None and last_kl_loss > variant.etch_kl_gate:
                continue  # skip this etch event

            etch_result = etch_check(
                etch_states, model,
                consensus_required=cfg.etch_consensus,
                max_flips=cfg.etch_max_flips_per_event,
            )
            n_flipped = etch_result["total_flipped"]
            total_flips += n_flipped

            if n_flipped > 0:
                n_etch_events += 1
                # Surgical Adam decay
                affected = etch_result.get("affected_rows", {})
                if cfg.etch_adam_decay < 1.0 and affected:
                    surgical_adam_decay_for_etch(
                        optimizer, model, affected, decay=cfg.etch_adam_decay)
                freeze_ternary_weights(model)
                restore_ternary(model)

                # Reset if configured
                if cfg.etch_reset_after_flip:
                    for es in etch_states.values():
                        if hasattr(es, 'reset_heat'):
                            es.reset_heat()

                # Track post-etch spike (CE change over next few steps)
                post_etch_spikes.append(step)

            # Track tempo
            tempo = etch_result.get("total_candidates", 0) / max(total_ternary, 1)
            etch_tempos.append(tempo)

    elapsed = time.time() - t_start

    # ── Compute metrics ─────────────────────��─────────────────
    final_ce = ce_history[-1] if ce_history else 99.0
    mean_ce_last50 = sum(ce_history[-50:]) / max(len(ce_history[-50:]), 1)
    min_ce = min(ce_history) if ce_history else 99.0
    mean_tempo = sum(etch_tempos) / max(len(etch_tempos), 1) if etch_tempos else 0.0

    # Post-etch spikes: max CE increase in 5 steps after each etch event
    max_spike = 0.0
    for etch_step in post_etch_spikes:
        idx = etch_step - 1  # 0-indexed
        if idx < len(ce_history) - 5:
            pre_ce = ce_history[idx]
            post_max = max(ce_history[idx+1:idx+6])
            spike = post_max - pre_ce
            max_spike = max(max_spike, spike)

    # Final dispatch
    dk = di = db = dc = 0.25
    if hasattr(model, 'combinator_dispatch') and hasattr(model.combinator_dispatch, '_dispatch_weights'):
        dw = model.combinator_dispatch._dispatch_weights
        if dw is not None:
            dw_mean = dw.mean(axis=(0, 1))
            mx.eval(dw_mean)
            dk = float(dw_mean[0].item())
            di = float(dw_mean[1].item())
            db = float(dw_mean[2].item())
            dc = float(dw_mean[3].item())

    return RunResult(
        name=variant.name,
        description=variant.description,
        final_ce=final_ce,
        mean_ce_last50=mean_ce_last50,
        min_ce=min_ce,
        total_flips=total_flips,
        n_etch_events=n_etch_events,
        mean_etch_tempo=mean_tempo,
        max_post_etch_spike=max_spike,
        dispatch_K=dk,
        dispatch_I=di,
        dispatch_B=db,
        dispatch_C=dc,
        kl_loss_final=last_kl_loss,
        elapsed_sec=elapsed,
        steps_run=total_steps,
    )


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════

def print_comparison(results: list[RunResult], suite_name: str):
    """Print a comparison table of results."""
    print(f"\n{'='*80}")
    print(f"  ETCH STRATEGY PROBE — Suite: {suite_name}")
    print(f"  {len(results)} variants × {results[0].steps_run} steps each")
    print(f"{'='*80}\n")

    # Header
    print(f"{'Name':<16} {'CE(final)':>9} {'CE(avg50)':>9} {'CE(min)':>8}"
          f" {'Flips':>6} {'Events':>6} {'Tempo':>7} {'Spike':>6}"
          f" {'K':>5} {'I':>5} {'B':>5} {'C':>5}"
          f" {'KL':>6} {'Time':>5}")
    print("─" * 120)

    # Sort by mean_ce_last50 (lower is better)
    ranked = sorted(results, key=lambda r: r.mean_ce_last50)

    for r in ranked:
        winner = " ★" if r == ranked[0] else ""
        print(f"{r.name:<16} {r.final_ce:>9.3f} {r.mean_ce_last50:>9.3f} {r.min_ce:>8.3f}"
              f" {r.total_flips:>6} {r.n_etch_events:>6} {r.mean_etch_tempo:>7.5f}"
              f" {r.max_post_etch_spike:>+6.2f}"
              f" {r.dispatch_K:>5.2f} {r.dispatch_I:>5.2f}"
              f" {r.dispatch_B:>5.2f} {r.dispatch_C:>5.2f}"
              f" {r.kl_loss_final:>6.1f} {r.elapsed_sec:>5.0f}s{winner}")

    print(f"\n{'─'*120}")
    print(f"  ★ = lowest mean CE (last 50 steps)")
    print(f"  Spike = max CE increase in 5 steps after an etch event")
    print(f"  Tempo = fraction of total ternary weights that are etch candidates")
    print()

    # Descriptions
    print("  Variants:")
    for r in ranked:
        marker = "★" if r == ranked[0] else " "
        print(f"  {marker} {r.name:<16} — {r.description}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Etch Strategy Probe — compare etch settings")
    parser.add_argument("--steps", type=int, default=300,
                        help="Steps per variant (default: 300, min ~250 to see etch)")
    parser.add_argument("--suite", type=str, default="core",
                        choices=list(SUITES.keys()) + ["all"],
                        help="Which experiment suite to run")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (same for all variants = fair comparison)")
    args = parser.parse_args()

    if args.suite == "all":
        suites_to_run = list(SUITES.keys())
    else:
        suites_to_run = [args.suite]

    output_path = Path("results/etch-strategy-probe")
    output_path.mkdir(parents=True, exist_ok=True)
    total_elapsed = 0.0

    for suite_idx, suite_name in enumerate(suites_to_run):
        variants = SUITES[suite_name]
        print(f"\n{'━'*80}", file=sys.stderr)
        print(f"  Running suite: {suite_name} ({len(variants)} variants × {args.steps} steps)"
              f"  [{suite_idx+1}/{len(suites_to_run)}]",
              file=sys.stderr)
        print(f"{'━'*80}", file=sys.stderr)

        results = []
        for i, variant in enumerate(variants):
            print(f"\n  [{i+1}/{len(variants)}] {variant.name}: {variant.description}",
                  file=sys.stderr)
            result = run_variant(variant, total_steps=args.steps, seed=args.seed)
            results.append(result)
            print(f"    → CE={result.mean_ce_last50:.3f}  flips={result.total_flips}"
                  f"  spike={result.max_post_etch_spike:+.2f}"
                  f"  time={result.elapsed_sec:.0f}s", file=sys.stderr)

        # Print comparison table immediately after suite completes
        print_comparison(results, suite_name)

        # Save results as JSON immediately after each suite
        suite_data = {
            "suite": suite_name,
            "steps": args.steps,
            "seed": args.seed,
            "timestamp": time.time(),
            "variants": [
                {
                    "name": r.name,
                    "description": r.description,
                    "final_ce": r.final_ce,
                    "mean_ce_last50": r.mean_ce_last50,
                    "min_ce": r.min_ce,
                    "total_flips": r.total_flips,
                    "n_etch_events": r.n_etch_events,
                    "mean_etch_tempo": r.mean_etch_tempo,
                    "max_post_etch_spike": r.max_post_etch_spike,
                    "dispatch_K": r.dispatch_K,
                    "dispatch_I": r.dispatch_I,
                    "dispatch_B": r.dispatch_B,
                    "dispatch_C": r.dispatch_C,
                    "kl_loss_final": r.kl_loss_final,
                    "elapsed_sec": r.elapsed_sec,
                    "steps_run": r.steps_run,
                }
                for r in sorted(results, key=lambda r: r.mean_ce_last50)
            ],
        }
        suite_path = output_path / f"{suite_name}.json"
        suite_path.write_text(json.dumps(suite_data, indent=2))
        print(f"  💾 Saved: {suite_path}", file=sys.stderr)

        total_elapsed += sum(r.elapsed_sec for r in results)

    print(f"\n  Done. Total time: {total_elapsed:.0f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
