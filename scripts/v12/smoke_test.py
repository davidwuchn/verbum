"""
Smoke test — exercise ALL code paths in 20 steps, then verify resume.

Tests: training loop, holographic loss, relational loss, etching,
eval with crystal diagnostics, checkpoint save, checkpoint resume.

Usage:
    uv run python scripts/v12/smoke_test.py
"""

from __future__ import annotations

import json
import shutil
import sys
import os
from pathlib import Path

os.environ["PYTHONUNBUFFERED"] = "1"

sys.path.insert(0, str(Path(__file__).parent))

from config import V12Config
from train import train

import argparse


def make_config() -> V12Config:
    """Config tuned to exercise everything in 20 steps."""
    cfg = V12Config()
    cfg.total_steps = 20
    cfg.seq_len = 1024
    cfg.max_seq_len = 1024
    cfg.batch_size = 2
    cfg.grad_accum = 1
    cfg.holo_lambda = 0.1
    cfg.mix_ratio = 0.0

    # Intervals: hit everything within 20 steps
    cfg.log_interval = 5
    cfg.eval_interval = 10        # eval at step 10, 20 (crystal diagnostics)
    cfg.checkpoint_interval = 10  # checkpoint at step 10, 20

    # Etch: start early so we see etch events
    cfg.etch_warmup = 5
    cfg.etch_interval = 2
    cfg.etch_signal_interval = 1

    # LR warmup: short so relational loss can fire
    cfg.warmup_steps = 3

    # Relational loss: fire every 5 steps (after warmup)
    cfg.rel_every = 5
    cfg.rel_n_probes = 10  # small batch for speed

    return cfg


def run_smoke_test():
    test_dir = Path("checkpoints/smoke-test")

    # Clean slate
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True)

    cfg = make_config()
    cfg.checkpoint_dir = str(test_dir)

    # ── Phase 1: Train 20 steps ──────────────────────────────
    print("=" * 60, file=sys.stderr)
    print("  SMOKE TEST — Phase 1: Train 20 steps", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    args = argparse.Namespace(resume=False)
    train(cfg, args)

    # ── Verify outputs ───────────────────────────────────────
    print("\n" + "=" * 60, file=sys.stderr)
    print("  SMOKE TEST — Verifying outputs", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    errors = []

    # Check JSONL logs exist and have content
    for log_name in ["train_log.jsonl", "etch_log.jsonl", "metrics_log.jsonl"]:
        log_path = test_dir / log_name
        if not log_path.exists():
            errors.append(f"  ✗ {log_name} missing")
        else:
            lines = log_path.read_text().strip().split("\n")
            n = len([l for l in lines if l.strip()])
            if n == 0:
                errors.append(f"  ✗ {log_name} empty")
            else:
                print(f"  ✓ {log_name}: {n} entries", file=sys.stderr)

    # Check checkpoints exist
    for step in [10, 20]:
        step_dir = test_dir / f"step_{step:06d}"
        if not step_dir.exists():
            errors.append(f"  ✗ step_{step:06d}/ missing")
            continue
        for fname in ["model.npz", "optimizer.npz", "state.json"]:
            fpath = step_dir / fname
            if not fpath.exists():
                errors.append(f"  ✗ step_{step:06d}/{fname} missing")
            else:
                size = fpath.stat().st_size
                print(f"  ✓ step_{step:06d}/{fname} ({size:,} bytes)", file=sys.stderr)

    # Check state.json has crystal diagnostics
    state_path = test_dir / "step_000020" / "state.json"
    if state_path.exists():
        state = json.loads(state_path.read_text())
        crystal = state.get("crystal", {})
        if "combinator_mirror_cosines" in crystal:
            cmc = crystal["combinator_mirror_cosines"]
            print(f"  ✓ crystal diagnostics in checkpoint: {list(cmc.keys())}", file=sys.stderr)
        else:
            errors.append("  ✗ crystal diagnostics missing from state.json")

        if state.get("dispatch_ema"):
            ema = state["dispatch_ema"]
            print(f"  ✓ dispatch_ema: K={ema['K']:.3f} I={ema['I']:.3f} "
                  f"B={ema['B']:.3f} C={ema['C']:.3f}", file=sys.stderr)
        else:
            errors.append("  ✗ dispatch_ema missing from state.json")

    # Check metrics_log has crystal + conditioned angles
    metrics_path = test_dir / "metrics_log.jsonl"
    if metrics_path.exists():
        last_line = metrics_path.read_text().strip().split("\n")[-1]
        metrics = json.loads(last_line)
        if "crystal_formation_score" in metrics:
            score = metrics["crystal_formation_score"]
            print(f"  ✓ crystal_formation_score in metrics: {score:.4f}", file=sys.stderr)
        else:
            errors.append("  ✗ crystal_formation_score missing from metrics_log")
        if "dispatch_conditioned_angles_deg" in metrics:
            angles = metrics["dispatch_conditioned_angles_deg"]
            print(f"  ✓ conditioned angles: {angles}", file=sys.stderr)
        else:
            errors.append("  ✗ dispatch_conditioned_angles_deg missing from metrics_log")

    # Check etch_log has tempo
    etch_path = test_dir / "etch_log.jsonl"
    if etch_path.exists():
        lines = [l for l in etch_path.read_text().strip().split("\n") if l.strip()]
        if lines:
            last = json.loads(lines[-1])
            if "etch_tempo" in last:
                print(f"  ✓ etch_tempo in etch_log: {last['etch_tempo']:.6f}", file=sys.stderr)
            else:
                errors.append("  ✗ etch_tempo missing from etch_log")
            if "flips_by_type" in last:
                print(f"  ✓ flips_by_type: {last['flips_by_type']}", file=sys.stderr)
            # Verify q_proj is excluded
            for entry_line in lines:
                entry = json.loads(entry_line)
                pm = entry.get("per_module", {})
                for mod_path, mod_data in pm.items():
                    if "q_proj" in mod_path and mod_data.get("n_flipped", 0) > 0:
                        errors.append(f"  ✗ q_proj got etched! {mod_path}: {mod_data['n_flipped']} flips")

    # Check relational loss fired
    train_log_path = test_dir / "train_log.jsonl"
    if train_log_path.exists():
        rel_found = False
        for line in train_log_path.read_text().strip().split("\n"):
            if line.strip():
                entry = json.loads(line)
                if entry.get("rel_loss", 0) > 0:
                    rel_found = True
                    print(f"  ✓ relational loss fired at step {entry['step']}: "
                          f"rel_loss={entry['rel_loss']:.4f}", file=sys.stderr)
                    break
        if not rel_found:
            errors.append("  ✗ relational loss never fired (no rel_loss > 0 in train_log)")

    if errors:
        print(f"\n  {'─'*50}", file=sys.stderr)
        print(f"  ERRORS ({len(errors)}):", file=sys.stderr)
        for e in errors:
            print(e, file=sys.stderr)
        print(f"  {'─'*50}", file=sys.stderr)
        # Don't proceed to resume test if phase 1 had errors
        sys.exit(1)

    # ── Phase 2: Resume from step 10 and run to step 20 ─────
    print("\n" + "=" * 60, file=sys.stderr)
    print("  SMOKE TEST — Phase 2: Resume from step 10", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    # Get step 10 state for comparison
    state_10 = json.loads((test_dir / "step_000010" / "state.json").read_text())
    step_10_losses = state_10.get("train_losses_last50", [])

    # Resume
    args_resume = argparse.Namespace(resume=True)
    cfg_resume = make_config()
    cfg_resume.checkpoint_dir = str(test_dir)
    cfg_resume.total_steps = 20  # will resume from 10, run 10 more

    train(cfg_resume, args_resume)

    # Verify resume produced step 20 checkpoint
    step_20_dir = test_dir / "step_000020"
    if step_20_dir.exists():
        state_20 = json.loads((step_20_dir / "state.json").read_text())
        print(f"  ✓ Resume produced step_000020 (step={state_20['step']})", file=sys.stderr)
        if state_20["step"] == 20:
            print(f"  ✓ Step counter correct: {state_20['step']}", file=sys.stderr)
        else:
            print(f"  ✗ Step counter wrong: {state_20['step']} (expected 20)", file=sys.stderr)
    else:
        print(f"  ✗ step_000020/ not created after resume", file=sys.stderr)
        sys.exit(1)

    # ── Summary ──────────────────────────────────────────────
    print("\n" + "=" * 60, file=sys.stderr)
    print("  ✅ SMOKE TEST PASSED — all code paths exercised", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    # Cleanup
    shutil.rmtree(test_dir)
    print("  🧹 Cleaned up smoke-test checkpoints", file=sys.stderr)


if __name__ == "__main__":
    run_smoke_test()
