#!/usr/bin/env python3
# register: functional
"""Stride-fit of the agreed normal forms — does v15's FIXED stride topology
ADMIT the combinators the open-weight ecosystem agrees on (s219 harvest edges)?

WHY (s221, Michael): v15 attention is NOT full content-addressable attention.
`FibonacciStrideAttention` gathers a FIXED window {q - s·w + r | w<W, |r|≤R},
causal (future masked); the *which-positions* is ARITHMETIC, content only WEIGHTS
within the gathered window (attention.py: "no content-based indexing"). So a
β-reduction substitution at distance d is a Zeckendorf composition of stride-hops,
not a single move; and some combinators' substitution PATTERNS may not fit the
fixed-window prior at all. Before designing a curriculum to TEACH the agreed
normal forms, ask which are even expressible on this architecture.

PART A — distance reachability (COMPUTED, decisive).
  Per composition stride s, one layer's backward reach set is
    D_s = {s·w - r : w∈0..W-1, r∈-R..R} ∩ Z>=0.
  A single ascending sweep applies each composition stride once → reachable
  distances = subset-sum (one element of D_s per stride, 0∈D_s via w=0). DP over
  [0, composition_range]. This is a CONSERVATIVE LOWER BOUND: the real model runs
  8 passes  x  2 directions  x  K outer, which only expands reach. Report coverage %,
  gap runs (unreachable distances), max reach.

PART B — pattern expressibility (architectural classification, grounded by A).
  Each combinator needs a move primitive realized by content-weighted, causal,
  fixed-window stride gathers:
    pass     (I)       : w=0 self                              → FITS (native)
    compose  (B,D)     : chain stride windows = the stack IS B → FITS (native)
    fan-out  (S,W)     : one key read by many queries (free)   → FITS
    permute  (C)       : swap ⇒ a FORWARD move ⇒ needs the descending sweep
                                                                → FEASIBLE (via sweep)
    erase    (K)       : zero in-window neighbours (fight blend) → FEASIBLE (grain)
    iterate  (Y)       : unbounded ⇒ the OUTER RECURRENCE        → NEEDS-RECURRENCE
    halt     (WHNF)    : Δx<ε control signal, not a gather       → N/A (recurrence)
  Edge-fit (s219 harvest edges) = the weaker endpoint's verdict.

Usage (CPU, no model load, seconds):
  uv run python scripts/experiments/stride_fit_normal_forms.py
  uv run python scripts/experiments/stride_fit_normal_forms.py --max-d 11181

License: MIT
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "scripts" / "v15"))

OUT_DIR = _PROJECT_ROOT / "results" / "stride-fit"


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


# ── geometry from the live config (no model load) ─────────────────────────────
def load_geometry():
    from config import V15Config
    cfg = V15Config()
    comp = [s for s, ret in zip(cfg.strides, cfg.stride_is_retrieval, strict=True)
            if not ret]
    return {
        "strides": list(cfg.strides),
        "stride_is_retrieval": list(cfg.stride_is_retrieval),
        "composition_strides": comp,
        "window": int(cfg.window),
        "radius": int(cfg.neighbor_radius),
    }


def stride_reach(stride: int, window: int, radius: int) -> set[int]:
    """Backward (causal) distances one layer at this stride can gather."""
    return {stride * w - r
            for w in range(window)
            for r in range(-radius, radius + 1)
            if stride * w - r >= 0}


def single_sweep_reachable(comp_strides, window, radius, max_d) -> np.ndarray:
    """Subset-sum DP: each composition stride contributes one hop from its reach
    set (0 included via w=0). Boolean reachability over [0, max_d]."""
    reach = np.zeros(max_d + 1, dtype=bool)
    reach[0] = True
    for s in comp_strides:
        offs = sorted(d for d in stride_reach(s, window, radius) if 0 < d <= max_d)
        if not offs:
            continue
        nxt = reach.copy()
        for d in offs:
            nxt[d:] |= reach[: max_d + 1 - d]
        reach = nxt
    return reach


def gap_runs(reach: np.ndarray, lo: int, hi: int, top: int = 12):
    """Largest runs of consecutive UNreachable distances in [lo, hi]."""
    runs = []
    i = lo
    while i <= hi:
        if not reach[i]:
            j = i
            while j <= hi and not reach[j]:
                j += 1
            runs.append((i, j - 1, j - i))
            i = j
        else:
            i += 1
    runs.sort(key=lambda r: -r[2])
    return runs[:top]


# ── PART B: per-combinator pattern classification ─────────────────────────────
# verdict ∈ {NATIVE, FEASIBLE, NEEDS-RECURRENCE, NA}
COMBINATOR_FIT = {
    "I": ("pass", "backward", "NATIVE",
          "identity = w=0 self-gather; trivial"),
    "B": ("compose", "backward", "NATIVE",
          "f(g x) = chain stride windows; the stride stack IS composition"),
    "D": ("compose", "backward", "NATIVE",
          "deep-nest compose = more stride hops; same primitive as B"),
    "S": ("fan-out", "backward", "NATIVE",
          "x used twice ⇒ one key read by two queries; keys are shared freely"),
    "W": ("fan-out", "backward", "NATIVE",
          "f x x = self-app fan-out; same as S (one source, two reads)"),
    "C": ("permute", "forward+backward", "FEASIBLE",
          "flip f y x swaps arg order ⇒ a FORWARD move ⇒ needs the descending "
          "sweep (stack_c) to carry it; reachable but not single-pass causal"),
    "K": ("erase", "backward", "FEASIBLE",
          "λx.λy.x discards y ⇒ must zero in-window neighbours; fights the blend "
          "prior, needs sharp content weighting (against the grain)"),
    "Y": ("iterate", "n/a", "NEEDS-RECURRENCE",
          "fixpoint = unbounded reduction; no single stride pattern; the OUTER "
          "RECURRENCE (Δx→0 ≡ WHNF) is required"),
    "WHNF": ("halt", "n/a", "NA",
             "normal-form predicate = the Δx<ε stop signal of the recurrence, "
             "not a gather pattern"),
}

# s219 universal harvest edges (consensus-delta-folding §s219, frac 0.40)
HARVEST_EDGES = ["B-D", "B-C", "K-C", "S-D", "S-Y"]
_RANK = {"NATIVE": 3, "FEASIBLE": 2, "NEEDS-RECURRENCE": 1, "NA": 0}


def edge_fit(edge: str):
    a, b = edge.split("-")
    va = COMBINATOR_FIT[a][2]
    vb = COMBINATOR_FIT[b][2]
    weaker = va if _RANK[va] <= _RANK[vb] else vb
    teachable = _RANK[weaker] >= _RANK["FEASIBLE"]
    return {"edge": edge, "endpoints": {a: va, b: vb},
            "edge_verdict": weaker, "stride_teachable": teachable}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max-d", type=int, default=0,
                    help="distance ceiling (0 = use config composition range)")
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    geo = load_geometry()
    comp = geo["composition_strides"]
    W, R = geo["window"], geo["radius"]
    # config composition range = last_stride·(W-1)+R
    cfg_range = comp[-1] * (W - 1) + R
    max_d = args.max_d or cfg_range

    log(f"  strides (composition): {comp}")
    log(f"  window W={W}  radius R={R}  W_eff={W * (2 * R + 1)}  "
        f"composition_range={cfg_range}  max_d={max_d}")

    # ── PART A ──
    reach = single_sweep_reachable(comp, W, R, max_d)
    n_reach = int(reach[1:max_d + 1].sum())
    coverage = n_reach / max_d
    gaps = gap_runs(reach, 1, max_d)
    max_reach = int(np.max(np.nonzero(reach)))
    log("")
    log(f"  PART A — single-sweep reachable distances over [1,{max_d}]:")
    log(f"    coverage = {coverage * 100:.2f}%  ({n_reach}/{max_d})  "
        f"max_reach={max_reach}")
    log(f"    largest unreachable gap runs (start,end,len): {gaps[:6]}")

    # ── PART B ──
    log("")
    log("  PART B — per-combinator stride-fit:")
    combinators = {}
    for c, (prim, direction, verdict, why) in COMBINATOR_FIT.items():
        combinators[c] = {"primitive": prim, "direction": direction,
                          "verdict": verdict, "reason": why}
        log(f"    {c:>4}  {verdict:<16} {prim:<8} {why}")

    log("")
    log("  s219 HARVEST EDGES — stride-teachability:")
    edges = [edge_fit(e) for e in HARVEST_EDGES]
    for e in edges:
        mark = "✓" if e["stride_teachable"] else "✗"
        log(f"    {mark} {e['edge']:<5} {e['edge_verdict']:<16} "
            f"({', '.join(f'{k}={v}' for k, v in e['endpoints'].items())})")
    n_teach = sum(e["stride_teachable"] for e in edges)
    log(f"\n  ▶ {n_teach}/{len(edges)} agreed edges stride-teachable; "
        f"the rest need the outer recurrence.")

    out = {
        "register": "functional",
        "git_sha": git_sha(),
        "question": ("does v15's fixed stride topology admit the agreed "
                     "(s219) normal forms?"),
        "geometry": geo,
        "composition_range": cfg_range,
        "max_d": max_d,
        "part_a_reachability": {
            "coverage_fraction": round(coverage, 4),
            "n_reachable": n_reach,
            "max_reach": max_reach,
            "largest_gap_runs": [{"start": s, "end": e, "len": ln}
                                 for s, e, ln in gaps],
            "note": ("single ascending sweep, each composition stride once = "
                     "conservative LOWER bound; real model = 8 passes x 2 dirs x K"),
        },
        "part_b_combinator_fit": combinators,
        "harvest_edge_fit": edges,
        "n_edges_stride_teachable": n_teach,
        "verdict": (
            "composition skeleton {B,D} is NATIVE to the stride stack; fan-out "
            "{S,W} fits; permute {C} needs the bidirectional sweep; erase {K} is "
            "feasible against the blend prior; the ONLY agreed structure that "
            "escapes the stride prior is the recursion endpoint {Y} (S-Y), which "
            "requires the outer recurrence — consistent with map=B(CB)(CB)."),
    }
    (OUT_DIR / "normal_form_fit.json").write_text(json.dumps(out, indent=2))
    log(f"\n  wrote {OUT_DIR / 'normal_form_fit.json'}")


if __name__ == "__main__":
    main()
