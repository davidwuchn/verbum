#!/usr/bin/env python3
# register: topological/routing
"""Is the tool-calling routing consensus TOOL-SPECIFIC, or generic structured-syntax?

The decisive control. tool_crystal_consensus_summary.py showed cross-family
route_sign_cmr agreement persists WITHIN tool domains (schema_binding 0.59,
selection 0.54). But if models ALSO agree that strongly within the lambda /
code / prose CONTROL groups, then the "tool-calling normal form" is really the
generic property-of-language universality (crystal-universality.md), not a
tool-specific routing structure.

This loads the saved route_sign_cmr RDMs and, for every probe GROUP (tool-side
domains + control subdomains), computes cross-family within-group agreement vs a
within-group shuffled-probe null. Verdict: do the TOOL groups agree MORE than
the CONTROL groups (tool-specific), or the same (generic structured-syntax)?

Usage:
  uv run python scripts/experiments/tool_crystal_control_baseline.py \
      [--route-layer-frac 0.6] [--n-perm 2000]
License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "tool-crystal-consensus"


def log(m: str = "") -> None:
    print(m, file=sys.stderr, flush=True)


def upper(D):
    return D[np.triu_indices_from(D, k=1)]


def family(s):
    for f in ["qwen3", "qwen2", "mistral", "smollm", "olmo", "pythia", "phi"]:
        if f in s.lower():
            return f
    return s.split("_")[0]


def group_of(subdomain: str) -> str:
    """Map a probe to a group. Tool side -> domain; controls -> subdomain."""
    if subdomain.startswith("control/"):
        return subdomain.split("/", 1)[1]          # lambda_calculus, code, prose, pure_math
    return subdomain.split("/", 1)[0]              # schema_binding, selection, format, recognition


def within_agree(rdms_by_model, idx, perm_rng=None):
    """Mean cross-family pairwise RDM agreement on the sub-block `idx`.
    If perm_rng given, permute one side's probe order (within-group null)."""
    fams = {m: family(m) for m in rdms_by_model}
    vals = []
    for a, b in combinations(rdms_by_model, 2):
        if fams[a] == fams[b]:
            continue
        Da = rdms_by_model[a][np.ix_(idx, idx)]
        Db = rdms_by_model[b][np.ix_(idx, idx)]
        if perm_rng is not None:
            p = perm_rng.permutation(len(idx))
            Db = Db[np.ix_(p, p)]
        x, y = upper(Da), upper(Db)
        if x.std() < 1e-12 or y.std() < 1e-12:
            continue
        vals.append(np.corrcoef(x, y)[0, 1])
    return float(np.mean(vals)) if vals else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--route-layer-frac", type=float, default=0.6)
    ap.add_argument("--n-perm", type=int, default=2000)
    ap.add_argument("--min-n", type=int, default=6)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    npzs = sorted(RESULTS_DIR.glob("*.npz"))
    rdms, sub0 = {}, None
    for p in npzs:
        safe = p.stem
        js = json.loads((RESULTS_DIR / f"{safe}.json").read_text())
        data = np.load(p, allow_pickle=True)
        n_layers = js["n_layers"]
        want = js["want_layers"]
        li = min(want, key=lambda x: abs(x - round(args.route_layer_frac * (n_layers - 1))))
        rdms[safe] = data[f"route_sign_cmr_L{li:02d}"]
        if sub0 is None:
            sub0 = data["subdomain"]
    if len(rdms) < 2:
        log("need >=2 model npz")
        sys.exit(1)

    groups = np.array([group_of(s) for s in sub0])
    TOOL = {"schema_binding", "selection", "format", "recognition"}
    CTRL = {"lambda_calculus", "code", "prose", "pure_math"}

    rng = np.random.default_rng(args.seed)
    rows = []
    for g in sorted(set(groups.tolist())):
        idx = np.where(groups == g)[0]
        if len(idx) < args.min_n:
            continue
        obs = within_agree(rdms, idx)
        null = np.array([within_agree(rdms, idx, perm_rng=rng) for _ in range(args.n_perm)])
        nmean, nstd = float(np.nanmean(null)), float(np.nanstd(null)) + 1e-30
        side = "TOOL" if g in TOOL else ("CTRL" if g in CTRL else "?")
        rows.append({"group": g, "side": side, "n": len(idx),
                     "agree": obs, "null_mean": nmean, "null_std": float(np.nanstd(null)),
                     "z": float((obs - nmean) / nstd),
                     "excess": float(obs - nmean)})

    tool_ex = [r["excess"] for r in rows if r["side"] == "TOOL"]
    ctrl_ex = [r["excess"] for r in rows if r["side"] == "CTRL"]
    out = {"route_layer_frac": args.route_layer_frac, "n_perm": args.n_perm,
           "models": list(rdms), "rows": rows,
           "tool_mean_excess": float(np.nanmean(tool_ex)) if tool_ex else float("nan"),
           "ctrl_mean_excess": float(np.nanmean(ctrl_ex)) if ctrl_ex else float("nan")}
    (RESULTS_DIR / "control_baseline.json").write_text(json.dumps(out, indent=2))

    log("")
    log("  === TOOL-SPECIFIC vs GENERIC structured-syntax (route_sign_cmr) ===")
    log(f"  {'group':16s} {'side':5s} {'n':>4s} {'agree':>7s} {'null':>7s} {'excess':>8s} {'z':>7s}")
    for r in sorted(rows, key=lambda r: (r["side"], -r["excess"])):
        log(f"  {r['group']:16s} {r['side']:5s} {r['n']:>4d} {r['agree']:>7.3f} "
            f"{r['null_mean']:>7.3f} {r['excess']:>+8.3f} {r['z']:>7.1f}")
    log("")
    log(f"  TOOL groups mean excess = {out['tool_mean_excess']:+.3f}")
    log(f"  CTRL groups mean excess = {out['ctrl_mean_excess']:+.3f}")
    log("  TOOL >> CTRL  => tool-calling has its OWN routing normal form.")
    log("  TOOL ~= CTRL  => the consensus is the GENERIC structured-language crystal")
    log("                  (tool-calling rides it; still on-thesis, different claim).")
    log("  wrote control_baseline.json")


if __name__ == "__main__":
    main()
