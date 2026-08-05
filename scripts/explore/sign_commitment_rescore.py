#!/usr/bin/env python3
"""§SIGN-COMMITMENT-CURVE — offline magnitude-split re-score (NON-FROZEN).

Post-hoc descriptive analysis of the tracked trit history dumped by
`sign_commitment.py --dump-history`. Does NOT touch the frozen gates/verdict
(those stand, committed 26ad20b as SIGN-CHURN). This script asks the follow-up
Michael raised: SIGN-CHURN says the sign *pattern* never fully freezes — but the
wire WORKS (loss 5.03→0.25, mag_cos 0.901). So WHERE is the churn, and is it
loss-neutral?

Hypothesis (two populations):
  • CONFIDENT core (r=|Δ_T|/thr_j ≫ 1, magnitude clears the TWN threshold) →
    commits its sign early and freezes.
  • MARGINAL / UNDECIDED tail (r≈1, sits ON the per-column threshold) → its float
    delta jitters across the threshold forever → carries ~all the late churn.
  r<1 ⇒ the final trit is 0 (below threshold) — the natural TWN "0" population.

Tests:
  Q1  bin trits by r_final; per-band median commit-step, late-flip-rate, and
      SHARE of total late flips. Prediction: late flips concentrate at r≈1.
  Q2  loss-neutrality: pooled flip-rate vs per-step loss over the plateau
      (step ≥ 89, where loss is flat). Prediction: flips continue while loss
      is ~constant ⇒ the churn buys no loss.

Outputs: prints a table; writes rescore.json + rescore.png next to the npz.

License: MIT.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

# r_final bands: below / on / just-above / clear-of the TWN column threshold.
BANDS = [
    ("r<1  (final 0)", 0.0, 1.0),
    ("1≤r<1.3 marginal", 1.0, 1.3),
    ("1.3≤r<2", 1.3, 2.0),
    ("2≤r<4", 2.0, 4.0),
    ("r≥4  confident", 4.0, np.inf),
]
LATE_STEP = 89          # plateau onset (loss flat beyond here)


def commit_step(tau: np.ndarray, steps: np.ndarray) -> np.ndarray:
    """Per-trit last step where τ_t != τ_final (0 if already final at t=0)."""
    final = tau[:, -1:]
    differ = tau != final
    differ[:, -1] = False
    idx = np.where(differ.any(axis=1),
                   (differ * np.arange(tau.shape[1])[None, :]).argmax(axis=1),
                   0)
    return steps[idx]


def late_flip_mask(tau: np.ndarray, steps: np.ndarray) -> np.ndarray:
    """Per-trit: did it flip in any interval whose END step ≥ LATE_STEP?"""
    late = steps[1:] >= LATE_STEP                     # interval-end mask
    changes = tau[:, 1:] != tau[:, :-1]
    return (changes[:, late]).any(axis=1)


def band_flip_curve(tau: np.ndarray, steps: np.ndarray) -> np.ndarray:
    """flip-rate per consecutive-snap interval for a set of trits."""
    if tau.shape[0] == 0:
        return np.zeros(tau.shape[1] - 1)
    return (tau[:, 1:] != tau[:, :-1]).mean(axis=0)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--npz",
        default="results/sign-commitment/qwen3-4b-rescore/tracked_history.npz")
    args = ap.parse_args()

    npz = Path(args.npz)
    d = np.load(npz, allow_pickle=True)
    tau = d["tau"].astype(np.int8)                   # (n_trit, n_snap)
    r = d["r_final"].astype(np.float64)              # (n_trit,)
    steps = d["steps"].astype(int)                   # (n_snap,)
    loss = d["loss"].astype(np.float64)              # (seeds, n_snap)
    n_trit, n_snap = tau.shape
    loss_mean = loss.mean(axis=0)

    cstep = commit_step(tau, steps)
    late = late_flip_mask(tau, steps)
    T = float(steps[-1])
    # total flips in late intervals (for share denominator, exact)
    late_iv = steps[1:] >= LATE_STEP
    if not late_iv.any():                            # smoke: no plateau window
        late_iv = np.zeros_like(late_iv)
        late_iv[-1] = True
    late_flip_events = int((tau[:, 1:] != tau[:, :-1])[:, late_iv].sum())

    print(f"\n══ §SIGN-COMMITMENT re-score (NON-FROZEN) — {npz} ══")
    print(f"n_trit={n_trit:,}  n_snap={n_snap}  T={T:.0f}  "
          f"late-window step≥{LATE_STEP}")
    print(f"pooled: median commit-step={np.median(cstep):.0f} "
          f"(frac {np.median(cstep)/T:.3f})  "
          f"late-churn trits={late.mean():.3f}\n")

    # ── Q1: per r_final band ──
    hdr = (f"{'band':18s} {'n':>9s} {'%pool':>6s} {'medCommit':>9s} "
           f"{'%late-flip':>10s} {'shareLateFlips':>14s} {'flip_last':>9s}")
    print(hdr)
    print("-" * len(hdr))
    rows = []
    for name, lo, hi in BANDS:
        m = (r >= lo) & (r < hi)
        n = int(m.sum())
        if n == 0:
            continue
        lf_events = int((tau[m][:, 1:] != tau[m][:, :-1])[:, late_iv].sum())
        share = lf_events / max(late_flip_events, 1)
        curve = band_flip_curve(tau[m], steps)
        row = {
            "band": name, "n": n, "pct_pool": n / n_trit,
            "med_commit": float(np.median(commit_step(tau[m], steps))),
            "pct_late_flip": float(late_flip_mask(tau[m], steps).mean()),
            "share_late_flips": float(share),
            "flip_last": float(curve[-1]),
            "flip_curve": curve.tolist(),
        }
        rows.append(row)
        print(f"{name:18s} {n:9,d} {n/n_trit:6.3f} "
              f"{row['med_commit']:9.0f} {row['pct_late_flip']:10.3f} "
              f"{share:14.3f} {row['flip_last']:9.4f}")

    # ── Q2: loss-neutrality over the plateau ──
    li = int(np.argmin(np.abs(steps - LATE_STEP)))
    loss_plateau_delta = float(loss_mean[li] - loss_mean[-1])
    loss_total_drop = float(loss_mean[0] - loss_mean[-1])
    pooled_curve = band_flip_curve(tau, steps)
    late_flip_mean = float(pooled_curve[late_iv].mean())
    print(f"\n── Q2 loss-neutrality (plateau step≥{LATE_STEP}) ──")
    print(f"loss: {loss_mean[0]:.3f}→{loss_mean[-1]:.3f} "
          f"(total drop {loss_total_drop:.3f}); "
          f"plateau drop step{steps[li]}→{steps[-1]} = {loss_plateau_delta:.4f} "
          f"({100*loss_plateau_delta/loss_total_drop:.2f}% of total)")
    print(f"mean flip-rate over plateau intervals = {late_flip_mean:.4f} "
          f"(nonzero churn under ~flat loss)")

    # ── plot ──
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        mids = steps[1:]
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.5))
        for row in rows:
            a1.plot(mids, row["flip_curve"], marker="o", ms=3,
                    label=row["band"])
        a1.axvline(LATE_STEP, ls=":", c="gray")
        a1.set_xscale("symlog")
        a1.set_xlabel("training step")
        a1.set_ylabel("flip-rate / interval")
        a1.set_title("Q1 — sign-flip rate by r_final band")
        a1.legend(fontsize=7)
        a2b = a2.twinx()
        a2.plot(steps, loss_mean, "k-o", ms=3, label="loss")
        a2b.plot(mids, pooled_curve, "r-s", ms=3, label="pooled flip-rate")
        a2.axvline(LATE_STEP, ls=":", c="gray")
        a2.set_xscale("symlog")
        a2.set_xlabel("training step")
        a2.set_ylabel("loss")
        a2b.set_ylabel("flip-rate", color="r")
        a2.set_title("Q2 — loss vs churn (loss-neutral tail)")
        fig.tight_layout()
        png = npz.with_name("rescore.png")
        fig.savefig(png, dpi=110)
        print(f"\n[rescore] wrote {png}")
    except Exception as e:
        print(f"[rescore] plot skipped: {e}")

    summary = {
        "npz": str(npz), "n_trit": n_trit,
        "median_commit_step": float(np.median(cstep)),
        "late_churn_trit_frac": float(late.mean()),
        "loss_total_drop": loss_total_drop,
        "loss_plateau_drop": loss_plateau_delta,
        "plateau_flip_rate_mean": late_flip_mean,
        "bands": rows,
    }
    out = npz.with_name("rescore.json")
    out.write_text(json.dumps(summary, indent=2))
    print(f"[rescore] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
