#!/usr/bin/env python3
"""P-DUST-1c — halt-DISTANCE resolves the anti-block absorption geometry (s285).

P-DUST-1b left one question open (its own writeup named the successor):
    "the WHNF row may rank by HALT DISTANCE (mean steps-to-WHNF) rather than
     next-step halt probability -- KIBC cannot disambiguate; D/W/S placement
     would. A P-DUST-1c statistic candidate requiring its own freeze."

The s285 expanded-gram sweep supplied what 1b lacked: per-op halt states
whnf:X (not just the generic WHNF pole), style-corrected (fire_formal span
projected out; commit 6b521fb). 1c tests whether the FRESH walk statistic
`halt_distance` orders the per-op absorption geometry, head-to-head vs the
`halt_prob` statistic 1b showed fails on the healthy walk.

FREEZE DISCIPLINE (lambda yardstick): the GEOMETRY side (style_corrected.json)
is committed and cannot be blinded -- SAME footing as P-DUST-1/1b. What is
frozen BEFORE any walk-vs-geometry number is computed:
  - ENSEMBLE: reuse the 1b arm-B (Y-excluded) healthy walk verbatim
    (default_rng(1), sizes 3-9, N=100k, leaves K,I,B,C,S,D,W,atom).
  - STATISTICS: halt_distance_X (mean steps from an X-fire to the terminating
    WHNF), halt_prob_X (=1b h), presence_PMI (1b-comparable), co_absorption_PMI
    (final-window W=3 before WHNF, terminating traces only).
  - MAPPING + GATES + SIGN below.
  - MODELS: all 10 EXCLUDING qwen3-0-6b (peeked pre-freeze = tainted;
    instrument-check tier only).

Gates (Michael-approved design, s285):
  G1 (PRIMARY)  spearman( cos(X, whnf:X) , -halt_distance_X ) > 0 over 7 ops
                exact label-perm null (5040); pooled median + sign >= 8/10.
  G2 (DISCRIM.) rho_distance > rho_prob head-to-head (Delta rho > 0), per model
                + pooled -- resolves the 1b distance-vs-prob open question.
  G3 (CO-ABSORB) spearman( whnf:X x whnf:Y off-diag , PMI off-diag ) over 21
                pairs; BOTH presence-PMI (a, primary/1b-comparable) AND
                co-absorption-PMI (b, final-window); perm null; sign >= 8/10.
  G4 (POLE)     spearman( pole->whnf:X , -halt_distance_X ) > 0; perm; >=8/10.
  VERDICT: DUST-HALT-DISTANCE-SUPPORTED  <=>  G1 AND G3a AND G4.
           G2 reports resolution; G3b robustness.

sign map: cos(X,whnf:X) is NEGATIVE (X and its halt are anti-podal). Higher cos
(less negative) = closer to own halt = shorter halt_distance -> map to
-halt_distance (monotone). Confirmed s285.

Usage:
    uv run python scripts/explore/dust_1c.py --validate   # synthetic pipeline
    uv run python scripts/explore/dust_1c.py              # REAL (post-freeze)

No model load. Deterministic. License: MIT.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from itertools import combinations, permutations
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[2]
_XG = _ROOT / "results" / "expanded-gram"
sys.path.insert(0, str(_ROOT / "opcodes"))

import dust_walk as DW  # noqa: E402

OPS7 = ["K", "I", "B", "C", "S", "D", "W"]      # anti-block ops (no Y/WHNF)
EXCLUDE = {"qwen3-0-6b"}                          # tainted: peeked pre-freeze
FINAL_WINDOW = 3
PAIRS = list(combinations(range(7), 2))          # 21 off-diagonal pairs


# ── walk side (frozen statistics) ─────────────────────────────────────────────
def regenerate_arm_b(n_terms: int) -> list[list[str]]:
    """Reproduce the 1b arm-B ensemble VERBATIM (deterministic)."""
    arm = DW.ARMS["y-excluded"]
    labels, probs = DW.leaf_probs(arm)
    sys.setrecursionlimit(200_000)
    rng = np.random.default_rng(arm["seed"])       # seed = 1
    lo, hi = DW.SIZES
    traces = []
    for i in range(n_terms):
        n = int(rng.integers(lo, hi + 1))
        traces.append(DW.trace(DW.gen_term(n, rng, labels, probs)))
        if (i + 1) % 20_000 == 0:
            print(f"[1c]   walk {i + 1}/{n_terms}", file=sys.stderr)
    return traces


def compute_1c_stats(traces: list[list[str]]) -> dict:
    """halt_distance, halt_prob, presence_PMI, co_absorption_PMI over OPS7."""
    idx = {o: i for i, o in enumerate(OPS7)}
    dist_sum = np.zeros(7)
    dist_cnt = np.zeros(7)
    hp_num = np.zeros(7)
    hp_den = np.zeros(7)
    # presence over ALL traces (1b-comparable)
    pres = np.zeros(7)
    pres_co = np.zeros((7, 7))
    n_all = len(traces)
    # co-absorption: final-window over TERMINATING traces
    win_pres = np.zeros(7)
    win_co = np.zeros((7, 7))
    n_term = 0

    for ev in traces:
        terminating = ev and ev[-1] == "WHNF"
        fired = [e for e in ev if e != "WHNF"]
        # presence (all traces)
        s = {o for o in fired if o in idx}
        for o in s:
            pres[idx[o]] += 1
        for a, b in combinations(sorted(s), 2):
            pres_co[idx[a], idx[b]] += 1
            pres_co[idx[b], idx[a]] += 1
        # halt-prob (next event is WHNF | op) over all fired positions
        for i, e in enumerate(ev):
            if e in idx:
                hp_den[idx[e]] += 1
                if i + 1 < len(ev) and ev[i + 1] == "WHNF":
                    hp_num[idx[e]] += 1
        if not terminating:
            continue
        n_term += 1
        whnf_pos = len(ev) - 1
        # halt-distance: steps from each X-fire to the terminating WHNF
        for i, e in enumerate(ev[:-1]):
            if e in idx:
                dist_sum[idx[e]] += (whnf_pos - i)
                dist_cnt[idx[e]] += 1
        # co-absorption: ops in the final window before WHNF
        window = fired[-FINAL_WINDOW:]
        ws = {o for o in window if o in idx}
        for o in ws:
            win_pres[idx[o]] += 1
        for a, b in combinations(sorted(ws), 2):
            win_co[idx[a], idx[b]] += 1
            win_co[idx[b], idx[a]] += 1

    halt_distance = np.where(dist_cnt > 0, dist_sum / np.maximum(dist_cnt, 1),
                             np.nan)
    halt_prob = np.where(hp_den > 0, hp_num / np.maximum(hp_den, 1), 0.0)
    presence_pmi = _pmi(pres_co, pres, n_all)
    coabsorption_pmi = _pmi(win_co, win_pres, max(n_term, 1))
    return {
        "n_traces": n_all, "n_terminating": n_term,
        "ops": OPS7,
        "halt_distance": [round(float(v), 4) for v in halt_distance],
        "halt_prob": [round(float(v), 4) for v in halt_prob],
        "presence_pmi": presence_pmi.tolist(),
        "coabsorption_pmi": coabsorption_pmi.tolist(),
    }


def _pmi(co: np.ndarray, pres: np.ndarray, n: int) -> np.ndarray:
    pmi = np.zeros((7, 7))
    for i in range(7):
        for j in range(7):
            if i != j:
                pmi[i, j] = np.log(((co[i, j] + 1) / n)
                                   / (((pres[i] + 1) / n) * ((pres[j] + 1) / n)))
    return pmi


# ── geometry side (committed, style-corrected) ───────────────────────────────
def load_geometry() -> dict[str, dict]:
    out = {}
    for p in sorted(_XG.glob("*/style_corrected.json")):
        slug = p.parent.name
        if slug in EXCLUDE:
            continue
        d = json.loads(p.read_text())
        order = d["ops"]                    # OPS7 order (K..W)
        ix = [order.index(o) for o in OPS7]
        cor = d["corrected"]
        out[slug] = {
            "abs": np.array(cor["per_op_absorption_cos"])[ix],
            "pole": np.array(cor["pole_to_whnfX_cos"])[ix],
            "whnf_block": np.array(cor["whnf_block"])[np.ix_(ix, ix)],
        }
    return out


# ── stats machinery ──────────────────────────────────────────────────────────
def _rank(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x))
    r[order] = np.arange(len(x))
    # average ties
    _, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
    sums = np.zeros(len(cnt))
    np.add.at(sums, inv, r)
    return (sums / cnt)[inv]


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    if np.all(a == a[0]) or np.all(b == b[0]):
        return 0.0
    ra, rb = _rank(a), _rank(b)
    return float(np.corrcoef(ra, rb)[0, 1])


def perm_p_vec(geom: np.ndarray, walk: np.ndarray, obs: float) -> float:
    """Exact 7! permutation of opcode labels on the WALK side, one-sided >=."""
    hits = total = 0
    for p in permutations(range(7)):
        r = spearman(geom, walk[list(p)])
        total += 1
        if r >= obs - 1e-12:
            hits += 1
    return hits / total


def _off(m: np.ndarray) -> np.ndarray:
    return np.array([m[i, j] for i, j in PAIRS])


def perm_p_block(geom_blk: np.ndarray, walk_blk: np.ndarray,
                 obs: float) -> float:
    """Exact 7! opcode-label permutation on the walk block, one-sided >=."""
    g = _off(geom_blk)
    hits = total = 0
    for p in permutations(range(7)):
        pw = walk_blk[np.ix_(p, p)]
        r = spearman(g, _off(pw))
        total += 1
        if r >= obs - 1e-12:
            hits += 1
    return hits / total


# ── gates ─────────────────────────────────────────────────────────────────────
def run_gates(stats: dict, geom: dict[str, dict]) -> dict:
    hd = np.array(stats["halt_distance"])
    hp = np.array(stats["halt_prob"])
    ppmi = np.array(stats["presence_pmi"])
    cpmi = np.array(stats["coabsorption_pmi"])
    neg_hd = -hd

    per = {}
    for slug, g in geom.items():
        g1 = spearman(g["abs"], neg_hd)
        g1p = perm_p_vec(g["abs"], neg_hd, g1)
        g4 = spearman(g["pole"], neg_hd)
        g4p = perm_p_vec(g["pole"], neg_hd, g4)
        rho_dist = spearman(g["abs"], neg_hd)
        rho_prob = spearman(g["abs"], hp)
        g3a = spearman(_off(g["whnf_block"]), _off(ppmi))
        g3ap = perm_p_block(g["whnf_block"], ppmi, g3a)
        g3b = spearman(_off(g["whnf_block"]), _off(cpmi))
        g3bp = perm_p_block(g["whnf_block"], cpmi, g3b)
        per[slug] = {
            "G1_abs_vs_neg_halt_distance": round(g1, 4), "G1_perm_p": round(g1p, 4),
            "G2_rho_distance": round(rho_dist, 4), "G2_rho_prob": round(rho_prob, 4),
            "G2_delta": round(rho_dist - rho_prob, 4),
            "G3a_block_vs_presence_pmi": round(g3a, 4),
            "G3a_perm_p": round(g3ap, 4),
            "G3b_block_vs_coabsorption_pmi": round(g3b, 4),
            "G3b_perm_p": round(g3bp, 4),
            "G4_pole_vs_neg_halt_distance": round(g4, 4),
            "G4_perm_p": round(g4p, 4),
        }

    n = len(per)
    need = max(1, int(np.ceil(0.8 * n)))

    def col(k):
        return np.array([per[m][k] for m in per])

    def gate(rkey, pkey=None):
        r = col(rkey)
        pos = int((r > 0).sum())
        sig = int((col(pkey) < 0.05).sum()) if pkey else None
        return {"median_r": round(float(np.median(r)), 4),
                "sign_positive": f"{pos}/{n}",
                "perm_p_lt_05": (f"{sig}/{n}" if sig is not None else None),
                "passes": pos >= need}

    g1 = gate("G1_abs_vs_neg_halt_distance", "G1_perm_p")
    g4 = gate("G4_pole_vs_neg_halt_distance", "G4_perm_p")
    g3a = gate("G3a_block_vs_presence_pmi", "G3a_perm_p")
    g3b = gate("G3b_block_vs_coabsorption_pmi", "G3b_perm_p")
    delta = col("G2_delta")
    g2 = {"median_delta": round(float(np.median(delta)), 4),
          "n_distance_wins": f"{int((delta > 0).sum())}/{n}",
          "median_rho_distance": round(float(np.median(col('G2_rho_distance'))), 4),
          "median_rho_prob": round(float(np.median(col('G2_rho_prob'))), 4),
          "resolved_distance_over_prob": int((delta > 0).sum()) >= need}

    verdict = {
        "n_models": n, "excluded": sorted(EXCLUDE),
        "G1_per_op_absorption": g1,
        "G2_distance_vs_prob": g2,
        "G3a_coabsorption_presence_pmi": g3a,
        "G3b_coabsorption_final_window_pmi": g3b,
        "G4_whnf_pole": g4,
        "DUST_HALT_DISTANCE_SUPPORTED": bool(g1["passes"] and g3a["passes"]
                                             and g4["passes"]),
    }
    return {"verdict": verdict, "per_model": per}


# ── validation (synthetic; NO real geometry, NO walk) ────────────────────────
def validate() -> int:
    print("[1c] VALIDATE (synthetic planted + null; no real data)")
    rng = np.random.default_rng(0)
    # planted: cos(X,whnf:X) monotone-decreasing in a planted halt_distance
    hd = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0])
    stats = {"halt_distance": hd.tolist(),
             "halt_prob": (1.0 / hd).tolist(),
             "presence_pmi": None, "coabsorption_pmi": None}
    # build a block whose off-diag tracks a planted pmi
    pmi = rng.standard_normal((7, 7))
    pmi = (pmi + pmi.T) / 2
    np.fill_diagonal(pmi, 0.0)
    stats["presence_pmi"] = pmi.tolist()
    stats["coabsorption_pmi"] = pmi.tolist()
    geom = {}
    for s, sign in [("planted", 1.0), ("null", 0.0)]:
        abs_cos = -(hd / hd.max()) * sign + rng.standard_normal(7) * (1 - sign) * 0.5
        block = pmi * sign + rng.standard_normal((7, 7)) * (1 - sign)
        block = (block + block.T) / 2
        geom[s] = {"abs": abs_cos, "pole": abs_cos.copy(), "whnf_block": block}
    out = run_gates(stats, geom)
    pm = out["per_model"]
    ok = (pm["planted"]["G1_abs_vs_neg_halt_distance"] > 0.9
          and pm["planted"]["G1_perm_p"] < 0.05
          and pm["planted"]["G3a_block_vs_presence_pmi"] > 0.9
          and abs(pm["null"]["G1_abs_vs_neg_halt_distance"]) < 0.9
          and pm["null"]["G1_perm_p"] > 0.05)
    print(f"  planted G1 r={pm['planted']['G1_abs_vs_neg_halt_distance']:+.3f} "
          f"p={pm['planted']['G1_perm_p']:.3f} | G3a "
          f"r={pm['planted']['G3a_block_vs_presence_pmi']:+.3f}")
    print(f"  null    G1 r={pm['null']['G1_abs_vs_neg_halt_distance']:+.3f} "
          f"p={pm['null']['G1_perm_p']:.3f}")
    print(f"  G2 planted delta={pm['planted']['G2_delta']:+.3f} "
          f"(dist {pm['planted']['G2_rho_distance']:+.3f} vs "
          f"prob {pm['planted']['G2_rho_prob']:+.3f})")
    print("  VALIDATE", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> None:
    ap = argparse.ArgumentParser(description="P-DUST-1c halt-distance verdict")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--n-terms", type=int, default=DW.N_TERMS)
    ap.add_argument("--output", default=str(
        _ROOT / "results" / "dust-walk" / "dust_1c_verdict.json"))
    args = ap.parse_args()

    if args.validate:
        sys.exit(validate())

    print(f"[1c] regenerating arm-B walk (N={args.n_terms}, seed=1)",
          file=sys.stderr)
    traces = regenerate_arm_b(args.n_terms)
    stats = compute_1c_stats(traces)
    print(f"[1c] n_terminating={stats['n_terminating']}/{stats['n_traces']}",
          file=sys.stderr)
    print(f"[1c] halt_distance="
          f"{dict(zip(OPS7, stats['halt_distance'], strict=True))}",
          file=sys.stderr)
    print(f"[1c] halt_prob    ="
          f"{dict(zip(OPS7, stats['halt_prob'], strict=True))}",
          file=sys.stderr)
    geom = load_geometry()
    print(f"[1c] geometry models={list(geom)} (excl {sorted(EXCLUDE)})",
          file=sys.stderr)
    out = run_gates(stats, geom)
    payload = {"experiment": "P-DUST-1c",
               "timestamp_utc": datetime.now(UTC).isoformat(),
               "git_sha": DW._git_sha() if hasattr(DW, "_git_sha") else None,
               "ensemble": f"arm-B y-excluded (default_rng(1), N={args.n_terms})",
               "final_window": FINAL_WINDOW,
               "walk_stats": stats, **out}
    Path(args.output).write_text(json.dumps(payload, indent=1))
    v = out["verdict"]
    print(json.dumps(v, indent=1))
    print(f"[1c] wrote {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
