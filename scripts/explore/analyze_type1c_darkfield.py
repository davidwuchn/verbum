#!/usr/bin/env python3
"""P-TYPE-1c — dark-field dissociation VERDICT analysis (post-hoc script of record).

Pre-reg: mementum/knowledge/explore/types-are-the-well-formedness-of-reduction.md
(#p-type-1c, FROZEN s283b). The wrapper's built-in 1b storage verdict is NOT the
1c verdict; THIS script computes it from the run's per_nonce arrays.

FROZEN ANALYSIS (verbatim from the pre-reg):
  1. g_Q(E), g_M(E) fit from the RANDOM condition ONLY — monotone interpolation
     in log realized E/tok (np.interp, piecewise-linear in log E). rolenull is a
     TEST condition, never a curve anchor. Roles fall inside random's realized-E
     range by construction (~2x per planned dose); verified + flagged.
  2. Per-nonce residuals Delta_c = ret_c - g(E_c), POOLED over d3+d4 (the region
     where the s283b deviations appeared).
  3. Permutation null over slice<->channel condition labels (shuffled-pairing),
     p < 0.05. Rows = (cond, dose, nonce) residual pairs (DQ, DM); labels
     shuffled across the three role conditions, row pairing preserved.
  4. Sign discipline: only pre-registered directions count — bind DQ < 0,
     comp DM > 0; opposite-sign deviations = verbatim-reported miss.

VERDICT (FROZEN): DARK-FIELD DISSOCIATION SUPPORTED <=>
  (a) bind DQ more negative than BOTH comp DQ and rolenull DQ (perm p<0.05), AND
  (b) comp DM more positive than BOTH bind DM and rolenull DM (perm p<0.05), AND
  (c) rolenull within null on both channels (one-sample sign-flip, p>0.05).

ANALYSIS DECISIONS (made before computing residuals; documented per λ measure):
  - per-nonce retention ret_c,i = X_c,i / mean(X_baseline): nonce-level
    numerator over the AGGREGATE baseline mean. Per-nonce-paired division
    (X_c,i / X_base,i) is unstable (baseline per-nonce values cross zero,
    e.g. -0.258); the aggregate denominator is a constant scale, so per-nonce
    variance structure is preserved.
  - compound contrasts: T_a = DQ_bind - min(DQ_comp, DQ_rolenull) with
    p_a = frac(T_perm <= T_real)  ("more negative than BOTH");
    T_b = DM_comp - max(DM_bind, DM_rolenull) with p_b = frac(T_perm >= T_real).
  - (c) via one-sample sign-flip permutation on rolenull residuals per channel
    (two-sided); "within null" <=> p > 0.05 on both.

Usage:
    uv run python scripts/explore/analyze_type1c_darkfield.py \
        [--run results/type-zone-ablation/qwen3-32b-1c] [--n-perm 10000]

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent

ROLE_CONDS = ["bind", "comp", "rolenull"]
POOL_DOSES = ["d3", "d4"]          # frozen: pooled region
ALL_DOSES = ["d1", "d2", "d3", "d4"]


def load_run(run_dir: Path) -> dict:
    return json.loads((run_dir / "verdict.json").read_text())


def per_nonce_ret(v: dict, cond: str, dose: str, ch: str) -> np.ndarray:
    """ret_c,i = X_c,i / mean(X_baseline) — aggregate-denominator retention."""
    base = float(v["baseline"][f"{ch}_eff"]["mean"])
    x = np.array(v["conditions"][f"{cond}@{dose}"]["per_nonce"][ch], dtype=float)
    return x / base


def realized_e(v: dict, cond: str, dose: str) -> float:
    return float(v["retention"][f"{cond}@{dose}"]["E_per_tok"])


def fit_gain_law(v: dict, ch: str) -> tuple[np.ndarray, np.ndarray]:
    """(log_e, ret) anchor points from RANDOM only, sorted by E. Frozen: random
    is the ONLY anchor; interpolation is piecewise-linear in log realized E."""
    pts = []
    for dose in ALL_DOSES:
        e = realized_e(v, "random", dose)
        base = float(v["baseline"][f"{ch}_eff"]["mean"])
        x = np.array(v["conditions"][f"random@{dose}"]["per_nonce"][ch], dtype=float)
        pts.append((np.log(e), float(x.mean() / base)))
    pts.sort()
    return np.array([p[0] for p in pts]), np.array([p[1] for p in pts])


def g_of(log_e_anchors: np.ndarray, ret_anchors: np.ndarray, e: float) -> float:
    """Monotone (piecewise-linear, clamped) interpolation in log E."""
    return float(np.interp(np.log(e), log_e_anchors, ret_anchors))


def main() -> None:
    ap = argparse.ArgumentParser(description="P-TYPE-1c dark-field verdict analysis")
    ap.add_argument("--run", default="results/type-zone-ablation/qwen3-32b-1c")
    ap.add_argument("--n-perm", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    run_dir = (_ROOT / args.run) if not Path(args.run).is_absolute() else Path(args.run)
    v = load_run(run_dir)
    rng = np.random.default_rng(args.seed)

    # gain law from RANDOM only (frozen)
    law = {ch: fit_gain_law(v, ch) for ch in ("Q", "M")}
    rand_e_range = [min(np.exp(law["Q"][0])), max(np.exp(law["Q"][0]))]

    # range check: roles must sit inside random's realized-E span (else flagged)
    inside = {}
    for cond in ROLE_CONDS:
        for dose in ALL_DOSES:
            e = realized_e(v, cond, dose)
            inside[f"{cond}@{dose}"] = bool(
                rand_e_range[0] <= e <= rand_e_range[1])

    # per-nonce residuals, all doses (verbatim) + pooled d3+d4 (verdict region)
    residual_rows: dict[str, dict[str, np.ndarray]] = {}
    per_dose_table = {}
    for cond in ROLE_CONDS:
        pooled_q, pooled_m = [], []
        for dose in ALL_DOSES:
            e = realized_e(v, cond, dose)
            dq = per_nonce_ret(v, cond, dose, "Q") - g_of(*law["Q"], e)
            dm = per_nonce_ret(v, cond, dose, "M") - g_of(*law["M"], e)
            per_dose_table[f"{cond}@{dose}"] = {
                "E_per_tok": e, "inside_random_range": inside[f"{cond}@{dose}"],
                "gQ": round(g_of(*law["Q"], e), 4),
                "gM": round(g_of(*law["M"], e), 4),
                "dQ_mean": round(float(dq.mean()), 4),
                "dQ_se": round(float(dq.std(ddof=1) / np.sqrt(dq.size)), 4),
                "dM_mean": round(float(dm.mean()), 4),
                "dM_se": round(float(dm.std(ddof=1) / np.sqrt(dm.size)), 4),
            }
            if dose in POOL_DOSES:
                pooled_q.append(dq)
                pooled_m.append(dm)
        residual_rows[cond] = {"Q": np.concatenate(pooled_q),
                               "M": np.concatenate(pooled_m)}

    # real pooled means
    dq = {c: float(residual_rows[c]["Q"].mean()) for c in ROLE_CONDS}
    dm = {c: float(residual_rows[c]["M"].mean()) for c in ROLE_CONDS}

    # sign discipline (frozen): bind DQ<0, comp DM>0 must hold for p to count
    signs_ok = {"bind_dQ_neg": dq["bind"] < 0, "comp_dM_pos": dm["comp"] > 0}

    # permutation null over slice<->channel labels (shuffled-pairing).
    # rows = (cond,dose,nonce) with paired (DQ, DM); condition labels shuffled
    # across the pooled role rows, pairing preserved.
    rows_q = np.concatenate([residual_rows[c]["Q"] for c in ROLE_CONDS])
    rows_m = np.concatenate([residual_rows[c]["M"] for c in ROLE_CONDS])
    n_per = residual_rows["bind"]["Q"].size          # 60 per cond (30 x 2 doses)
    labels = np.repeat(np.arange(3), n_per)

    def contrasts(lab: np.ndarray) -> tuple[float, float]:
        mq = [rows_q[lab == i].mean() for i in range(3)]
        mm = [rows_m[lab == i].mean() for i in range(3)]
        t_a = mq[0] - min(mq[1], mq[2])              # bind vs best competitor (Q)
        t_b = mm[1] - max(mm[0], mm[2])              # comp vs best competitor (M)
        return t_a, t_b

    t_a_real, t_b_real = contrasts(labels)
    perm_a = np.empty(args.n_perm)
    perm_b = np.empty(args.n_perm)
    for i in range(args.n_perm):
        lab = rng.permutation(labels)
        perm_a[i], perm_b[i] = contrasts(lab)
    p_a = float(np.mean(perm_a <= t_a_real))         # more negative than both
    p_b = float(np.mean(perm_b >= t_b_real))         # more positive than both

    # (c) rolenull within null on both channels: one-sample sign-flip, two-sided
    def signflip_p(x: np.ndarray) -> float:
        real = abs(x.mean())
        flips = rng.choice([-1.0, 1.0], size=(args.n_perm, x.size))
        null = np.abs((flips * x[None, :]).mean(axis=1))
        return float(np.mean(null >= real))

    p_null_q = signflip_p(residual_rows["rolenull"]["Q"])
    p_null_m = signflip_p(residual_rows["rolenull"]["M"])
    rolenull_clean = bool(p_null_q > 0.05 and p_null_m > 0.05)

    gate_a = bool(signs_ok["bind_dQ_neg"] and p_a < 0.05)
    gate_b = bool(signs_ok["comp_dM_pos"] and p_b < 0.05)
    supported = bool(gate_a and gate_b and rolenull_clean)

    out = {
        "experiment": "P-TYPE-1c dark-field dissociation (verdict analysis)",
        "prereg": ("mementum/knowledge/explore/"
                   "types-are-the-well-formedness-of-reduction.md#p-type-1c"),
        "run_dir": str(run_dir.relative_to(_ROOT)),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "seed": args.seed, "n_perm": args.n_perm,
        "gate0": v["gate0"],
        "baseline": {ch: v["baseline"][f"{ch}_eff"] for ch in ("Q", "M")},
        "gain_law_anchors": {
            ch: {"E_per_tok": [round(float(np.exp(x)), 1) for x in law[ch][0]],
                 "ret": [round(float(r), 4) for r in law[ch][1]]}
            for ch in ("Q", "M")},
        "roles_inside_random_range": inside,
        "per_dose_residuals": per_dose_table,
        "pooled_d3d4": {
            "dQ": {c: round(dq[c], 4) for c in ROLE_CONDS},
            "dM": {c: round(dm[c], 4) for c in ROLE_CONDS},
            "n_rows_per_cond": int(n_per)},
        "sign_discipline": signs_ok,
        "permutation": {
            "T_a_bindQ_vs_best": round(t_a_real, 4), "p_a": p_a,
            "T_b_compM_vs_best": round(t_b_real, 4), "p_b": p_b},
        "rolenull_within_null": {
            "p_Q": p_null_q, "p_M": p_null_m, "clean": rolenull_clean},
        "verdict": {
            "gate_a_bind_suppresses_Q": gate_a,
            "gate_b_comp_preserves_M": gate_b,
            "gate_c_rolenull_clean": rolenull_clean,
            "darkfield_dissociation_supported": supported},
    }

    dst = run_dir / "darkfield_verdict.json"
    dst.write_text(json.dumps(out, indent=2))

    print(f"[1c] gain-law anchors (random): "
          f"Q ret={out['gain_law_anchors']['Q']['ret']} "
          f"M ret={out['gain_law_anchors']['M']['ret']} "
          f"@E={out['gain_law_anchors']['Q']['E_per_tok']}", file=sys.stderr)
    for cond in ROLE_CONDS:
        for dose in ALL_DOSES:
            r = per_dose_table[f"{cond}@{dose}"]
            print(f"[1c] {cond:9s}@{dose} E={r['E_per_tok']:7.1f} "
                  f"dQ={r['dQ_mean']:+.3f}±{r['dQ_se']:.3f} "
                  f"dM={r['dM_mean']:+.3f}±{r['dM_se']:.3f} "
                  f"{'':2s}in_range={r['inside_random_range']}", file=sys.stderr)
    print(f"[1c] POOLED d3+d4: dQ={out['pooled_d3d4']['dQ']} "
          f"dM={out['pooled_d3d4']['dM']}", file=sys.stderr)
    print(f"[1c] signs: {signs_ok} | T_a={t_a_real:+.4f} p_a={p_a:.4f} | "
          f"T_b={t_b_real:+.4f} p_b={p_b:.4f} | "
          f"rolenull p_Q={p_null_q:.3f} p_M={p_null_m:.3f}", file=sys.stderr)
    print(f"[1c] VERDICT: darkfield_dissociation_supported = {supported}",
          file=sys.stderr)
    print(f"[1c] wrote {dst}", file=sys.stderr)


if __name__ == "__main__":
    main()
