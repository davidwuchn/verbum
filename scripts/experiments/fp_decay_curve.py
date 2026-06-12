#!/usr/bin/env python3
# register: functional
"""Δx-decay curve — does the trained v15 outer recurrence actually CONTRACT past
pass 2, and in how many passes would it reach a fixed point?

WHY (s221, Michael): training runs K=2, so we have only ever OBSERVED Δx_2 (the
residual at the 2nd pass). We have NEVER watched Δx_3, Δx_4, … — so we do not
actually know whether the operator keeps contracting (→ fp~0 in a few passes) or
plateaus/limit-cycles past pass 2 (trained to look contractive at pass 2 only).
This loads the trained operator READ-ONLY and runs the recurrence to K=max on
REAL long sequences (so the long Fibonacci strides activate — the s215 seq-256
trap: short probes leave strides 610/987/1597 as no-ops), capturing the per-pass
relative residual `_last_outer_deltas`. Output:
  - mean Δx_k per pass k=2..K, the contraction ratio L_k = Δx_{k+1}/Δx_k,
  - geometric-mean L and the implied passes-to-ε (when does Δx<ε ≡ WHNF),
  - a verdict: CONTRACTIVE (L<1, decays) / PLATEAU (L≈1) / DIVERGENT (L>1),
  - and a suggested deadband target Δx* (just above the convergence floor) for a
    soft/inverse fp loss (Michael: nudge GD, don't enforce fp=0).
READ-ONLY: loads a saved checkpoint; does NOT perturb the running main:1 training.

Usage (GPU/MLX, kept light to avoid contending with main:1):
  uv run python scripts/experiments/fp_decay_curve.py \\
      --checkpoint checkpoints/v15-td-outer-k2-fp5-5k/step_001000/model.npz \\
      --seq-len 2048 --n-batches 6 --max-k 6

License: MIT
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "scripts" / "v15"))
sys.path.insert(0, str(_PROJECT_ROOT / "src"))

import mlx.core as mx  # noqa: E402
from config import V15Config  # noqa: E402
from data import ShardedDataLoader  # noqa: E402
from td_delta import reduce_all_deltas  # noqa: E402
from train_td import create_model_with_deltas  # noqa: E402

OUT_DIR = _PROJECT_ROOT / "results" / "fp-decay"


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--checkpoint", type=str,
                    default="checkpoints/v15-td-outer-k2-fp5-5k/step_001000/model.npz",
                    help="TRAINED v15 model.npz (READ-ONLY)")
    ap.add_argument("--extracted-model-path", type=str,
                    default="checkpoints/v15-extracted/model.npz/model.npz")
    ap.add_argument("--seq-len", type=int, default=2048,
                    help="real-data sequence length (activate long strides)")
    ap.add_argument("--n-batches", type=int, default=6)
    ap.add_argument("--batch-size", type=int, default=1)
    ap.add_argument("--max-k", type=int, default=6, help="outer passes to run")
    ap.add_argument("--epsilon", type=float, default=0.05,
                    help="WHNF threshold for passes-to-ε estimate")
    ap.add_argument("--seed", type=int, default=7,
                    help="loader seed (≠ training's 42 → different chunks)")
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    cfg = V15Config()
    if Path(args.extracted_model_path).exists():
        cfg.extracted_model_path = args.extracted_model_path

    log(f"building v15 operator (max_k={args.max_k}) ...")
    model, _ = create_model_with_deltas(cfg, convert_ffn=True)
    if args.checkpoint and Path(args.checkpoint).exists():
        log(f"  loading TRAINED checkpoint (read-only): {args.checkpoint}")
        model.load_weights(args.checkpoint, strict=False)
        mx.eval(model.parameters())
        n_reduced = reduce_all_deltas(model)
        log(f"  folded {n_reduced} trained delta plates into base")
        mx.eval(model.parameters())
    else:
        raise SystemExit(f"checkpoint not found: {args.checkpoint}")
    model._n_outer_passes = args.max_k
    model._fixed_point_lambda = 0.0

    loader = ShardedDataLoader(
        data_dir=cfg.data_dir, batch_size=args.batch_size, seq_len=args.seq_len,
        shard_start=0, shard_end=cfg.n_train_shards, seed=args.seed)

    # ── run K=max forwards, collect the per-pass residual curve ──
    curves = []   # each = [Δx_2, Δx_3, ..., Δx_K]  (max_k-1 entries)
    for b in range(args.n_batches):
        ids_np, tgts_np = next(loader)
        ids = mx.array(np.asarray(ids_np, np.int64))
        tgts = mx.array(np.asarray(tgts_np, np.int64))
        model._prev_alg_c = None
        _ = model(ids, tgts)
        deltas = model._last_outer_deltas  # list of mx scalars
        mx.eval(deltas)
        curve = [float(np.asarray(d)) for d in deltas]
        curves.append(curve)
        log(f"  batch {b + 1}/{args.n_batches}: Δx = "
            f"[{', '.join(f'{x:.4f}' for x in curve)}]")

    curves = np.array(curves)  # (n_batches, max_k-1)
    mean_dx = curves.mean(axis=0)
    std_dx = curves.std(axis=0)
    # pass index k for entry i (i=0 → Δx between pass1&2 → label k=2)
    ks = list(range(2, args.max_k + 1))

    # contraction ratios L_k = Δx_{k+1}/Δx_k
    ratios = [float(mean_dx[i + 1] / (mean_dx[i] + 1e-12))
              for i in range(len(mean_dx) - 1)]
    L = (float(np.exp(np.mean(np.log(np.clip(ratios, 1e-6, None)))))
         if ratios else float("nan"))

    last_dx = float(mean_dx[-1])
    if L < 1.0 and last_dx > args.epsilon:
        passes_to_eps = float(np.log(args.epsilon / last_dx) / np.log(L))
    elif last_dx <= args.epsilon:
        passes_to_eps = 0.0
    else:
        passes_to_eps = float("inf")

    if all(r < 0.98 for r in ratios):
        verdict = "CONTRACTIVE"
    elif any(r > 1.02 for r in ratios):
        verdict = "DIVERGENT-or-LIMIT-CYCLE"
    else:
        verdict = "PLATEAU"

    # suggested deadband target: the convergence floor (last Δx) with headroom
    suggested_target = round(last_dx * 1.2, 3)

    log("")
    log("  ════ Δx-DECAY CURVE — does the recurrence contract past pass 2? ════")
    log(f"  {'pass k':>7} {'Δx_k':>8} {'±std':>7} {'L_k=Δx_{k+1}/Δx_k':>18}")
    for i, k in enumerate(ks):
        r = f"{ratios[i]:.3f}" if i < len(ratios) else "   —"
        log(f"  {k:>7} {mean_dx[i]:>8.4f} {std_dx[i]:>7.4f} {r:>18}")
    log("")
    log(f"  geometric-mean contraction L = {L:.3f}  →  verdict: {verdict}")
    log(f"  passes to Δx<{args.epsilon} (from K={args.max_k}): {passes_to_eps:.1f}")
    log(f"  suggested deadband target Δx* ≈ {suggested_target} "
        f"(just above the convergence floor)")

    out = {
        "register": "functional",
        "git_sha": git_sha(),
        "question": ("does the trained v15 outer recurrence contract past pass 2 "
                     "(K=2 training only ever observed Δx_2)?"),
        "checkpoint": args.checkpoint,
        "seq_len": args.seq_len, "n_batches": args.n_batches,
        "batch_size": args.batch_size, "max_k": args.max_k, "epsilon": args.epsilon,
        "pass_index": ks,
        "mean_delta_x": [round(float(x), 5) for x in mean_dx],
        "std_delta_x": [round(float(x), 5) for x in std_dx],
        "contraction_ratios": [round(r, 4) for r in ratios],
        "geomean_L": round(L, 4),
        "passes_to_epsilon": passes_to_eps,
        "verdict": verdict,
        "suggested_deadband_target": suggested_target,
        "note": ("READ-ONLY on the checkpoint; real long sequences activate the "
                 "long strides. L<1 ⇒ contractive; the K=2 fp-loss only ever "
                 "trained Δx_2 so passes 3+ are the genuine test."),
        "elapsed_s": round(time.time() - t0, 1),
    }
    out_path = OUT_DIR / f"decay_curve_seq{args.seq_len}.json"
    out_path.write_text(json.dumps(out, indent=2))
    log(f"\n  wrote {out_path}  ({out['elapsed_s']}s)")


if __name__ == "__main__":
    main()
