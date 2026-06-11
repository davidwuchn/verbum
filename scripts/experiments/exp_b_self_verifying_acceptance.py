#!/usr/bin/env python3
# register: functional
"""Experiment B (core) — is the continuation a SELF-VERIFYING acceptance test?

THE DISTRIBUTED-TRAINING CLAIM (explore/consensus-delta-folding.md, s217):
  A working VSM continuation (the outer recurrence in v15model.py: shared sweep
  iterated, x_c fed back → β-reduction toward a fixed point / WHNF) should let
  distributed training ACCEPT or REJECT a donated delta WITHOUT trusted held-out
  labels — because the fixed point IS the target. A good delta should preserve /
  accelerate convergence (lower Δx-at-convergence); a bad delta should push the
  operator off its fixed point (raise Δx-at-convergence). If so:

      accept(delta)  ⟺  Δx-at-convergence does NOT rise

  is a label-free, Byzantine-robust acceptance rule (removes the audit-#7
  population-Goodhart risk: no shared calibration cache to overfit).

THE TEST (this script, gradient-free):
  Build the frozen continuation operator (V15Model + extracted base, n_outer=K).
  Perturb the ROUTING register (FFN gate delta plate) by flipping B random
  positions (a quality SPECTRUM via flip-count B = 1,2,4,...). For each candidate
  measure BOTH:
    ΔCE          = model._last_ce − CE0          (the TRUE quality label)
    Δ(Δx_conv)   = Δx_at_convergence − Δx0        (the SELF-VERIFYING signal)
  Then correlate. The hypothesis is corr(ΔCE, Δ(Δx_conv)) > 0: degrading the
  operator (raising CE) also raises the fixed-point residual. If yes, the
  continuation residual is a valid label-free acceptance signal.

  Δx_at_convergence = model._last_outer_deltas[-1] = ‖x_c^K − x_c^{K-1}‖/‖·‖
  (the last outer-recurrence relative step — 0 ⇒ exact fixed point / WHNF).

CAVEAT (register): on the FROZEN extracted base the operator is not yet trained
for contractivity (s214: naive K stays Δx~1.2). This is therefore a LOWER BOUND;
the clean test reruns on main:1's λ_fp-trained contractive checkpoint once it
lands. We report the baseline convergence curve so the regime is explicit.

Usage:
  uv run python scripts/experiments/exp_b_self_verifying_acceptance.py \
      --n-outer 6 --seqs 4 --seq-len 512 --reps 8

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
_V15 = _PROJECT_ROOT / "scripts" / "v15"
sys.path.insert(0, str(_V15))

import mlx.core as mx  # noqa: E402
from config import V15Config  # noqa: E402
from train_td import create_model_with_deltas  # noqa: E402
from td_delta import (  # noqa: E402
    collect_delta_params,
    unpack_ternary_mlx,
    pack_ternary_mlx,
    reduce_all_deltas,
)

RESULTS_DIR = _PROJECT_ROOT / "results" / "exp-b-self-verifying"
SHARD = Path.home() / "data" / "fractal-bitnet" / "shards-qwen36" / "shard_00000.npy"


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def load_token_batch(seqs: int, seq_len: int, vocab: int, seed: int = 0):
    """A (seqs, seq_len+1) token window from the data shard → (tokens, targets)."""
    arr = np.load(str(SHARD), mmap_mode="r")
    rng = np.random.default_rng(seed)
    need = seq_len + 1
    starts = rng.integers(0, len(arr) - need, size=seqs)
    rows = np.stack([np.asarray(arr[s:s + need], dtype=np.int64) for s in starts])
    rows = np.clip(rows, 0, vocab - 1)
    tokens = mx.array(rows[:, :-1])
    targets = mx.array(rows[:, 1:])
    return tokens, targets


def forward_metrics(model, tokens, targets):
    """One forward at the configured n_outer → (CE, Δx_at_convergence, curve)."""
    model._prev_alg_c = None  # clean state, no cross-call algedonic drift
    _, _ = model(tokens, targets)
    mx.eval(model._last_ce)
    ce = float(model._last_ce.item())
    curve = [float(d.item()) for d in model._last_outer_deltas]
    dx_conv = curve[-1] if curve else float("nan")
    return ce, dx_conv, curve


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-outer", type=int, default=6)
    ap.add_argument("--seqs", type=int, default=4)
    ap.add_argument("--seq-len", type=int, default=512)
    ap.add_argument("--reps", type=int, default=8,
                    help="random position-sets per flip-count")
    ap.add_argument("--flip-fracs", type=str,
                    default="0.0003,0.001,0.003,0.01,0.03,0.1,0.3",
                    help="flip these FRACTIONS of the plate's positions (the quality spectrum)")
    ap.add_argument("--module-filter", type=str, default="ffn_gate",
                    help="substring to pick the target routing module(s)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--extracted-model-path", type=str,
                    default="checkpoints/v15-extracted/model.npz/model.npz",
                    help="frozen base (nested model.npz, as main:1 uses)")
    ap.add_argument("--checkpoint", type=str, default="",
                    help="optional TRAINED model.npz (non-chance CE) to load over the base")
    args = ap.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    flip_fracs = [float(x) for x in args.flip_fracs.split(",")]

    cfg = V15Config()
    if Path(args.extracted_model_path).exists():
        cfg.extracted_model_path = args.extracted_model_path
    log(f"building continuation operator (n_outer={args.n_outer}) ...")
    model, _converted = create_model_with_deltas(cfg, convert_ffn=True)
    if args.checkpoint and Path(args.checkpoint).exists():
        log(f"  loading TRAINED checkpoint: {args.checkpoint}")
        model.load_weights(args.checkpoint, strict=False)
        mx.eval(model.parameters())
        # fold trained delta routing into the base so deltas restart at +1;
        # perturbations are then correctly RELATIVE to the trained operator.
        n_reduced = reduce_all_deltas(model)
        log(f"  folded {n_reduced} trained delta plates into base (deltas → +1)")
        mx.eval(model.parameters())
    model._n_outer_passes = args.n_outer
    model._fixed_point_lambda = 0.0  # eval only
    mx.eval(model.parameters())

    # pick the target routing module (FFN gate delta plate = routing register)
    deltas = collect_delta_params(model)
    targets_mods = [(n, m) for (n, m) in deltas if args.module_filter in n]
    if not targets_mods:
        targets_mods = deltas[:1]
    tgt_name, tgt_mod = targets_mods[0]
    base_unpacked = unpack_ternary_mlx(tgt_mod.base_weight)
    N, K = base_unpacked.shape
    n_positions = N * K
    ones_packed = pack_ternary_mlx(mx.ones((N, K), dtype=mx.int8))
    log(f"target routing module: {tgt_name}  shape=({N},{K})  positions={n_positions:,}")

    tokens, targets = load_token_batch(args.seqs, args.seq_len, cfg.vocab_size, args.seed)
    log(f"batch: tokens {tokens.shape}  targets {targets.shape}")

    # ── baseline ──
    ce0, dx0, curve0 = forward_metrics(model, tokens, targets)
    log(f"baseline  CE={ce0:.4f}  Δx_conv={dx0:.4f}  curve={['%.3f'%c for c in curve0]}")

    def apply_flip(flat_idx: np.ndarray):
        delta = np.ones((N, K), dtype=np.int8)
        delta.reshape(-1)[flat_idx] = -1  # flip effective sign at these positions
        tgt_mod.delta_weight = pack_ternary_mlx(mx.array(delta))
        mx.eval(tgt_mod.delta_weight)

    def reset_flip():
        tgt_mod.delta_weight = ones_packed
        mx.eval(tgt_mod.delta_weight)

    rng = np.random.default_rng(args.seed + 1)
    records = []
    for frac in flip_fracs:
        B = max(1, int(frac * n_positions))
        for r in range(args.reps):
            idx = rng.choice(n_positions, size=min(B, n_positions), replace=False)
            apply_flip(idx)
            ce, dx, _ = forward_metrics(model, tokens, targets)
            reset_flip()
            records.append({
                "flip_frac": float(frac), "flip_count": int(B), "rep": int(r),
                "dCE": ce - ce0, "dDx": dx - dx0,
                "CE": ce, "Dx_conv": dx,
            })
        sub = [x for x in records if x["flip_frac"] == frac]
        log(f"  frac={frac:<7} (B={B:>7})  mean ΔCE={np.mean([x['dCE'] for x in sub]):+.4f}  "
            f"mean Δ(Δx_conv)={np.mean([x['dDx'] for x in sub]):+.5f}")

    # ── analysis ──
    dCE = np.array([x["dCE"] for x in records])
    dDx = np.array([x["dDx"] for x in records])
    finite = np.isfinite(dCE) & np.isfinite(dDx)
    dCE, dDx = dCE[finite], dDx[finite]

    def pearson(a, b):
        if a.std() < 1e-12 or b.std() < 1e-12:
            return 0.0
        return float(np.corrcoef(a, b)[0, 1])

    def spearman(a, b):
        ra = np.argsort(np.argsort(a))
        rb = np.argsort(np.argsort(b))
        return pearson(ra.astype(float), rb.astype(float))

    pear = pearson(dCE, dDx)
    spear = spearman(dCE, dDx)

    # acceptance ROC: does "Δ(Δx_conv) > 0" predict "ΔCE > 0" (a degrading delta)?
    pred_bad = dDx > 0
    true_bad = dCE > 0
    tp = int(np.sum(pred_bad & true_bad))
    tn = int(np.sum(~pred_bad & ~true_bad))
    fp = int(np.sum(pred_bad & ~true_bad))
    fn = int(np.sum(~pred_bad & true_bad))
    acc = (tp + tn) / max(len(dCE), 1)
    # also: of accepted (Δx not raised) deltas, what fraction actually improved/held CE?
    accepted = ~pred_bad
    accept_good_rate = (float(np.mean(~true_bad[accepted])) if accepted.any() else float("nan"))

    verdict = ("SELF-VERIFYING SIGNAL PRESENT" if spear > 0.3 and pear > 0.3
               else "WEAK/ABSENT (needs contractive-trained base)" if spear > 0.1
               else "NO SIGNAL on this base")

    out = {
        "register": "functional",
        "model": "v15 extracted base (frozen)",
        "n_outer": args.n_outer, "target_module": tgt_name,
        "module_shape": [int(N), int(K)], "n_positions": int(n_positions),
        "batch": {"seqs": args.seqs, "seq_len": args.seq_len},
        "baseline": {"CE": ce0, "Dx_conv": dx0, "curve": curve0},
        "n_candidates": int(len(records)), "flip_fracs": flip_fracs,
        "pearson_dCE_dDx": pear, "spearman_dCE_dDx": spear,
        "acceptance_roc": {"tp": tp, "tn": tn, "fp": fp, "fn": fn,
                           "accuracy": acc, "accept_good_rate": accept_good_rate},
        "verdict": verdict,
        "per_flipfrac": {
            str(frac): {
                "mean_dCE": float(np.mean([x["dCE"] for x in records if x["flip_frac"] == frac])),
                "mean_dDx": float(np.mean([x["dDx"] for x in records if x["flip_frac"] == frac])),
            } for frac in flip_fracs},
        "records": records,
        "elapsed_s": round(time.time() - t0, 1),
    }
    (RESULTS_DIR / "result.json").write_text(json.dumps(out, indent=2))

    log("")
    log("  ════════ SELF-VERIFYING ACCEPTANCE — VERDICT ════════")
    log(f"  baseline convergence curve: {['%.3f' % c for c in curve0]}  (→0 = WHNF)")
    log(f"  candidates: {len(records)}  (flip-count spectrum × {args.reps} reps)")
    log(f"  corr(ΔCE, Δ(Δx_conv))   Pearson={pear:+.3f}  Spearman={spear:+.3f}")
    log(f"  acceptance rule 'reject if Δx_conv rises': accuracy={acc:.3f} "
        f"(predict degrade), accepted-and-good={accept_good_rate:.3f}")
    log(f"  ▶ {verdict}")
    log(f"  wrote result.json  ({out['elapsed_s']}s)")


if __name__ == "__main__":
    main()
