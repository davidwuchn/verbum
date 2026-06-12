#!/usr/bin/env python3
# register: topological/routing
"""Combinator crystallization trajectory — does the RECURSION family form only
as the operator becomes contractive (Δx→0 ≡ β-reduction to WHNF)?

THE QUESTION (s221, Michael's thread).
  We have only ever MEASURED finished models. This traces the combinator
  function shape FORMING during training. Each combinator's β-reduction is a
  substitution = a move/copy/delete of arguments across positions, and attention
  is the ONLY cross-position operation → the substructural class of a combinator
  predicts its attention cost:
    selection  {K,I,C}  affine/linear, 0 copies   → ONE attention pass
    composition{B,D,S}  B,D linear; S duplicates   → one pass (+1 fan-out)
    recursion  {Y,W,WHNF}  W dup, Y unbounded       → NEEDS the OUTER RECURRENCE
  PREDICTION: selection/composition (the "skeleton") bind EARLY and stay flat;
  the recursion family strengthens ONLY as Δx→0. If the recursion z_bind tracks
  (-Δx) while the skeleton z_bind does not, recursion-family combinators provably
  require β-reduction-iteration training; selection/composition do not.

WHAT IT DOES (CPU/numpy, no model load — cheap, run anytime).
  1. Globs per-checkpoint v15 maps (results/combinator-relationship-map/
     v15_<target>_step_*.json + v15_<target>_base.json), each carrying a
     `family_binding_best` block (produced by combinator_relationship_map_v15.py).
  2. Parses each checkpoint's training step; joins the contractivity state at
     that step (mean Δx = outer_deltas, fp_loss, ce over a window) from the live
     training log checkpoints/<run>/train_td_log.jsonl.
  3. Emits a trajectory {step, Δx, fp, ce, silhouette_z, selection_z,
     composition_z, recursion_z, skeleton_z} + a verdict:
       Spearman corr(recursion_z, -Δx)  vs  corr(skeleton_z, -Δx).
     recursion tracks contractivity AND skeleton does not  ⇒ PREDICTION SUPPORTED.

Usage:
  uv run python scripts/experiments/combinator_crystallization.py --target attn_q
  # custom run/glob:
  uv run python scripts/experiments/combinator_crystallization.py \\
      --target attn_q --train-log checkpoints/v15-td-outer-k2-fp5-5k/train_td_log.jsonl

License: MIT
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
MAP_DIR = _PROJECT_ROOT / "results" / "combinator-relationship-map"
OUT_DIR = _PROJECT_ROOT / "results" / "combinator-crystallization"


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


def _spearman(a, b):
    """Spearman rank correlation (no scipy). Returns nan if <3 points."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    n = len(a)
    if n < 3:
        return float("nan")
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean()
    rb -= rb.mean()
    denom = np.sqrt((ra * ra).sum() * (rb * rb).sum()) + 1e-30
    return float((ra * rb).sum() / denom)


def step_of(meta_json: dict, path: Path) -> int:
    """Training step for a v15 map json. base/'' → 0; else parse step_NNNNNN."""
    ckpt = meta_json.get("checkpoint") or ""
    m = re.search(r"step_0*([0-9]+)", ckpt) or re.search(r"step_0*([0-9]+)", path.name)
    return int(m.group(1)) if m else 0


def contractivity_at(log_rows: list[dict], step: int, window: int) -> dict:
    """Mean Δx (outer_deltas), fp_loss, ce over [step-window, step]."""
    if not log_rows:
        return {"dx": None, "fp": None, "ce": None, "n": 0}
    lo = step - window
    sel = [r for r in log_rows if lo <= int(r.get("step", -1)) <= step]
    if not sel and step == 0:  # base: take the earliest rows as the pre-train state
        sel = log_rows[: max(1, window // 10)]
    if not sel:  # step beyond log → take the last window
        sel = [r for r in log_rows
               if int(r.get("step", -1)) >= step - window] or log_rows[-5:]

    def _scalar(v):
        # outer_deltas is logged as a list (per-iteration Δx, K-1 entries)
        if isinstance(v, (list, tuple)):
            return float(np.mean(v)) if v else None
        return float(v)

    def _mean(key):
        vals = [_scalar(r[key]) for r in sel if r.get(key) is not None]
        vals = [v for v in vals if v is not None]
        return float(np.mean(vals)) if vals else None

    return {"dx": _mean("outer_deltas"), "fp": _mean("fp_loss"),
            "ce": _mean("ce"), "n": len(sel)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", default="attn_q",
                    help="register tag matching v15_<target>_step_*.json")
    ap.add_argument("--map-glob", default="",
                    help="override glob for v15 map jsons")
    ap.add_argument("--train-log",
                    default="checkpoints/v15-td-outer-k2-fp5-5k/train_td_log.jsonl",
                    help="live training log to join Δx/fp/ce by step")
    ap.add_argument("--window", type=int, default=100,
                    help="steps before a checkpoint to average contractivity over")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    pattern = args.map_glob or str(MAP_DIR / f"v15_{args.target}_*.json")
    files = sorted(glob.glob(pattern))
    if not files:
        raise SystemExit(f"no v15 map jsons matched: {pattern}")

    log_path = _PROJECT_ROOT / args.train_log
    log_rows = []
    if log_path.exists():
        with log_path.open() as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        log_rows.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    else:
        log(f"  ⚠ train log not found: {log_path} (Δx/fp/ce will be null)")

    rows = []
    for f in files:
        p = Path(f)
        meta = json.loads(p.read_text())
        fb = meta.get("family_binding_best")
        if not fb:
            log(f"  skip (no family_binding_best, rerun the map): {p.name}")
            continue
        step = step_of(meta, p)
        con = contractivity_at(log_rows, step, args.window)
        rows.append({
            "file": p.name,
            "step": step,
            "best_key": meta.get("best_key"),
            "dx": con["dx"], "fp": con["fp"], "ce": con["ce"],
            "silhouette_z": round(float(meta["route_cmr_silhouette"]["z"]), 2),
            "selection_z": fb["selection_KIC"]["z_bind"],
            "composition_z": fb["composition_BDS"]["z_bind"],
            "recursion_z": fb["recursion_YWWHNF"]["z_bind"],
            "skeleton_z": fb["_summary"]["skeleton_z_bind"],
        })
    rows.sort(key=lambda r: r["step"])

    # ── verdict: do recursion/skeleton z_bind track contractivity (-Δx)? ──
    have_dx = [r for r in rows if r["dx"] is not None]
    verdict = {"n_checkpoints": len(rows), "n_with_dx": len(have_dx)}
    if len(have_dx) >= 3:
        neg_dx = [-r["dx"] for r in have_dx]
        rec = [r["recursion_z"] for r in have_dx]
        skel = [r["skeleton_z"] for r in have_dx]
        verdict.update({
            "spearman_recursion_vs_contractivity": round(_spearman(rec, neg_dx), 3),
            "spearman_skeleton_vs_contractivity": round(_spearman(skel, neg_dx), 3),
            "prediction": ("recursion z_bind RISES as Δx→0 (corr>0) AND skeleton "
                           "does NOT track contractivity (corr≈0/flat)"),
            "supported": bool(
                _spearman(rec, neg_dx) > _spearman(skel, neg_dx)
                and _spearman(rec, neg_dx) > 0),
        })
    else:
        verdict["note"] = ("need ≥3 checkpoints with Δx to test the trajectory; "
                           "rerun the v15 map as main:1 checkpoints land")

    out = {
        "register": "topological/routing",
        "git_sha": git_sha(),
        "question": ("does the recursion combinator family form only as the "
                     "operator becomes contractive (β-reduction to WHNF)?"),
        "target": args.target,
        "train_log": str(args.train_log),
        "window": args.window,
        "trajectory": rows,
        "verdict": verdict,
    }
    (OUT_DIR / f"trajectory_{args.target}.json").write_text(json.dumps(out, indent=2))

    # ── summary ──
    log("")
    log("  ════ COMBINATOR CRYSTALLIZATION — family binding vs contractivity ════")
    log(f"  {'step':>7} {'Δx':>7} {'fp':>6} {'sil_z':>6} "
        f"{'sel':>6} {'comp':>6} {'skel':>6} {'REC':>6}")
    for r in rows:
        dx = f"{r['dx']:.3f}" if r["dx"] is not None else "  -  "
        fp = f"{r['fp']:.3f}" if r["fp"] is not None else "  -  "
        log(f"  {r['step']:>7} {dx:>7} {fp:>6} {r['silhouette_z']:>+6.2f} "
            f"{r['selection_z']:>+6.2f} {r['composition_z']:>+6.2f} "
            f"{r['skeleton_z']:>+6.2f} {r['recursion_z']:>+6.2f}")
    if "supported" in verdict:
        log("")
        log(f"  recursion vs contractivity:  r = "
            f"{verdict['spearman_recursion_vs_contractivity']:+.3f}")
        log(f"  skeleton  vs contractivity:  r = "
            f"{verdict['spearman_skeleton_vs_contractivity']:+.3f}")
        log(f"  ▶ PREDICTION SUPPORTED: {verdict['supported']}")
    else:
        log(f"  {verdict.get('note', '')}")
    log(f"\n  wrote {OUT_DIR / f'trajectory_{args.target}.json'}")


if __name__ == "__main__":
    main()
