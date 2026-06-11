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
    TernaryLinear,
    DeltaTernaryLinear,
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

    tokens, targets = load_token_batch(args.seqs, args.seq_len, cfg.vocab_size, args.seed)
    log(f"batch: tokens {tokens.shape}  targets {targets.shape}")

    # ── baseline ──
    ce0, dx0, curve0 = forward_metrics(model, tokens, targets)
    log(f"baseline  CE={ce0:.4f}  Δx_conv={dx0:.4f}  curve={['%.3f'%c for c in curve0]}")

    # ── pick a target routing module that is ACTUALLY IN THE FORWARD PATH ──
    # INSTRUMENT GUARD (s218): convert_ffn ORPHANS the top-level ffn_*_plate_*
    # DeltaTernaryLinear copies — `convert_to_delta` setattr's the model attribute
    # but stack_{a,c} keep their original references, so the LIVE FFN plates are
    # stack_{a,c}.ffn_gate_plate (TernaryLinear). The prior run perturbed an orphan
    # ⇒ CE bit-identical across 1.97M flips ⇒ VOID. We now (1) enumerate candidate
    # ternary modules matching the filter, (2) KEEP only those whose signs actually
    # move CE, (3) ABORT if none. Perturbation = sign-flip of NONZERO ternary
    # positions (= the routing register; zeros stay zero).
    def _is_delta(m):
        return isinstance(m, DeltaTernaryLinear)

    def _orig_signs(m):
        return np.asarray(unpack_ternary_mlx(m.delta_weight if _is_delta(m) else m.weight))

    def _set_signs(m, arr_np):
        packed = pack_ternary_mlx(mx.array(arr_np.astype(np.int8)))
        if _is_delta(m):
            m.delta_weight = packed
        else:
            m.weight = packed
        mx.eval(packed)

    candidates = [(n, m) for (n, m) in model.named_modules()
                  if isinstance(m, (TernaryLinear, DeltaTernaryLinear))
                  and args.module_filter in n]
    if not candidates:
        raise SystemExit(f"no ternary module matches --module-filter={args.module_filter!r}")

    tgt_name = tgt_mod = base_signs = None
    for name, mod in candidates:
        signs = _orig_signs(mod)
        N_, K_ = signs.shape
        nz = np.flatnonzero(signs.reshape(-1) != 0)
        if nz.size == 0:
            continue
        gr = np.random.default_rng(args.seed).choice(nz, size=max(1, nz.size // 2), replace=False)
        probe = signs.copy().reshape(-1)
        probe[gr] *= -1
        _set_signs(mod, probe.reshape(N_, K_))
        ce_probe, _, _ = forward_metrics(model, tokens, targets)
        _set_signs(mod, signs)  # restore exactly
        moved = abs(ce_probe - ce0)
        log(f"  guard: {name:34} ({N_},{K_}) nz={nz.size:>9,}  flip-½nz ΔCE={ce_probe-ce0:+.4f}"
            f"  {'LIVE ✓' if moved > 1e-4 else 'DEAD ✗'}")
        if moved > 1e-4 and tgt_mod is None:
            tgt_name, tgt_mod, base_signs = name, mod, signs

    if tgt_mod is None:
        raise SystemExit("INSTRUMENT GUARD FAILED: no live routing module for "
                         f"--module-filter={args.module_filter!r} — perturbations do not reach "
                         "the forward. ABORT (the result would be VOID, cf. s217 phase-2 bug).")

    N, K = base_signs.shape
    nz_idx = np.flatnonzero(base_signs.reshape(-1) != 0)  # routing positions (nonzero signs)
    n_positions = int(nz_idx.size)
    log(f"▶ LIVE target routing module: {tgt_name}  shape=({N},{K})  "
        f"routing(nonzero)-positions={n_positions:,}")

    def apply_flip(flat_idx: np.ndarray):
        signs = base_signs.copy().reshape(-1)
        signs[flat_idx] *= -1  # flip sign of selected nonzero routing positions
        _set_signs(tgt_mod, signs.reshape(N, K))

    def reset_flip():
        _set_signs(tgt_mod, base_signs)

    rng = np.random.default_rng(args.seed + 1)
    records = []
    for frac in flip_fracs:
        B = max(1, int(frac * n_positions))
        for r in range(args.reps):
            sel = rng.choice(n_positions, size=min(B, n_positions), replace=False)
            idx = nz_idx[sel]  # map to absolute flat indices among routing positions
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
               else "WEAK (partial signal)" if spear > 0.1
               else "NO SIGNAL on this base")

    out = {
        "register": "functional",
        "model": (f"v15 trained base ({args.checkpoint})" if args.checkpoint
                  else "v15 extracted base (frozen)"),
        "perturbation": "sign-flip of nonzero routing positions (live FFN gate plate)",
        "live_guard": "passed",
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
