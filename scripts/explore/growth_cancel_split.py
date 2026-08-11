#!/usr/bin/env python3
"""§P-GROWTH-CANCEL-SPLIT — separate the ✅ AT1 Δ into growth vs cancellation.

Pre-reg: mementum/knowledge/explore/types-are-a-modulation-scheme.md
§P-GROWTH-CANCEL-SPLIT (FROZEN s326, Michael GO — frozen before computing any
MID-population magnitude-trajectory statistic; only the fb histogram, a data
class fully read in s325 by SD1/SD2, was inspected for feasibility).

Claim under test: the ✅ §P-AMP-TRAJECTORY Δ = +0.975 (early-frozen vs churner,
matched) conflates early-frozen GROWTH above baseline with churner CANCELLATION
below baseline. Third population MID = valid ∧ fb∈[11,15] (sign committed steps
1k–16k) is the decile-matched same-substrate baseline.

Statistics (pinned): shared window b11→b19; g = log(|W_b19|+ε) − log(|W_b11|+ε);
one shared 3-population pooled-|W_b11| decile frame; Δ_growth = Σ w_k (mean
g_early,k − mean g_mid,k); Δ_cancel = Σ w_k (mean g_mid,k − mean g_churn,k);
each with its OWN within-decile pair-label permutation null ×10k; decile
qualifies per-comparison iff ≥500 of each population in that pair; ≥3
qualifying deciles per comparison. Consistency identity Δ_growth + Δ_cancel ≈
AT1 Δ reported, not gated.

GC3 advisory (never gates): repeat both with MID restricted to fb∈{11,12}
(minimal mid-window commitment rebound — MID commits DURING the window ⇒
conservative for GC1, ANTI-conservative for GC2, named at freeze) + per-fb
baseline breakdown of mean g.

Verdicts + a-priori (NOT tuned; co-modal on revision and deflation):
BOTH-LIVE 30 / CANCELLATION-DRIVEN 30 / GROWTH-DRIVEN 15 / UNSEPARATED 15 /
VOID 10.

License: MIT (lambda provenance).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from stratigraphy_dating import (  # noqa: E402
    CHURN_MIN_BIN,
    COMMONS_MAX_BIN,
    EPS,
    N_BINS,
    observables,
)

WINDOW_START = 11              # step 1000
WINDOW_END = 19                # step 143000
MID_ROBUST_MAX_FB = 12         # GC3 advisory: MID restricted to fb in {11,12}
MIN_PER_DECILE = 500
MIN_QUAL_DECILES = 3
N_PERM = 10_000
ALPHA = 0.05
APRIORI = {"BOTH-LIVE": 30, "CANCELLATION-DRIVEN": 30, "GROWTH-DRIVEN": 15,
           "UNSEPARATED": 15, "VOID": 10}

EARLY, CHURN, MID = 1, 2, 3


def _pooled_deciles(x: np.ndarray) -> np.ndarray:
    """Decile labels 1..10 over the pooled vector x (rank-based)."""
    order = np.argsort(x, kind="stable")
    r = np.empty(len(x), float)
    r[order] = np.arange(len(x), dtype=float)
    return np.minimum((r / len(x) * 10).astype(int) + 1, 10)


def _pair_delta(g: np.ndarray, pop: np.ndarray, dec: np.ndarray,
                a: int, b: int, rng: np.random.Generator,
                n_perm: int = N_PERM) -> dict:
    """Weighted within-decile Δ = mean g_a − mean g_b + pair-label perm null."""
    quals = [d for d in range(1, 11)
             if ((dec == d) & (pop == a)).sum() >= MIN_PER_DECILE
             and ((dec == d) & (pop == b)).sum() >= MIN_PER_DECILE]
    if len(quals) < MIN_QUAL_DECILES:
        return {"n_qualifying_deciles": len(quals), "delta": 0.0,
                "p_pos": 1.0, "p_neg": 1.0, "sign": "ns", "quals": quals}
    per, med, wts, pools = {}, {}, [], []
    for d in quals:
        m = dec == d
        ga, gb = g[m & (pop == a)], g[m & (pop == b)]
        per[str(d)] = float(ga.mean() - gb.mean())
        med[str(d)] = float(np.median(ga) - np.median(gb))
        wts.append(len(ga) + len(gb))
        pools.append((np.concatenate([ga, gb]), len(ga)))
    w = np.array(wts, float)
    w /= w.sum()
    delta = float(np.dot(w, [per[str(d)] for d in quals]))
    null = np.empty(n_perm)
    for i in range(n_perm):
        acc = 0.0
        for wk, (pool, k) in zip(w, pools, strict=True):
            p = pool[rng.permutation(len(pool))]
            acc += wk * (p[:k].mean() - p[k:].mean())
        null[i] = acc
    p_pos = float((null >= delta).mean())
    p_neg = float((null <= delta).mean())
    sign = "positive" if (delta > 0 and p_pos < ALPHA) else \
           "negative" if (delta < 0 and p_neg < ALPHA) else "ns"
    return {"n_qualifying_deciles": len(quals), "quals": quals,
            "delta": delta, "p_pos": p_pos, "p_neg": p_neg, "sign": sign,
            "per_decile_mean": per, "per_decile_median": med}


def gate_gc0(obs: dict, pop: np.ndarray, growth: dict, cancel: dict) -> dict:
    valid = obs["valid"]
    n = max(int(valid.sum()), 1)
    counts = {"early": int((pop == EARLY).sum()),
              "churn": int((pop == CHURN).sum()),
              "mid": int((pop == MID).sum())}
    ok = (float(valid.mean()) > 0.99
          and all(c / n >= 0.01 for c in counts.values())
          and growth["n_qualifying_deciles"] >= MIN_QUAL_DECILES
          and cancel["n_qualifying_deciles"] >= MIN_QUAL_DECILES)
    return {"gate": "GC0", "pass": bool(ok), **counts,
            "n_quals_growth": growth["n_qualifying_deciles"],
            "n_quals_cancel": cancel["n_qualifying_deciles"]}


def gate_gc3(g: np.ndarray, pop: np.ndarray, dec: np.ndarray, fb: np.ndarray,
             rng: np.random.Generator, n_perm: int = N_PERM) -> dict:
    """Advisory: MID restricted to fb in {11, MID_ROBUST_MAX_FB} + per-fb g."""
    pop_r = pop.copy()
    pop_r[(pop == MID) & (fb > MID_ROBUST_MAX_FB)] = 0
    growth_r = _pair_delta(g, pop_r, dec, EARLY, MID, rng, n_perm=n_perm)
    cancel_r = _pair_delta(g, pop_r, dec, MID, CHURN, rng, n_perm=n_perm)
    per_fb = {str(b): {"n": int(((pop == MID) & (fb == b)).sum()),
                       "mean_g": float(g[(pop == MID) & (fb == b)].mean())
                       if ((pop == MID) & (fb == b)).any() else None}
              for b in range(COMMONS_MAX_BIN + 1, CHURN_MIN_BIN)}
    return {"gate": "GC3", "advisory": True,
            "n_mid_restricted": int((pop_r == MID).sum()),
            "growth_restricted": {k: growth_r[k] for k in
                                  ("delta", "p_pos", "p_neg", "sign",
                                   "n_qualifying_deciles")},
            "cancel_restricted": {k: cancel_r[k] for k in
                                  ("delta", "p_pos", "p_neg", "sign",
                                   "n_qualifying_deciles")},
            "mid_per_fb_mean_g": per_fb}


def verdict(gc0: dict, gc1: dict, gc2: dict) -> str:
    if not gc0["pass"]:
        return "VOID"
    g_ok = gc1["sign"] == "positive"
    c_ok = gc2["sign"] == "positive"
    if g_ok and c_ok:
        return "BOTH-LIVE"
    if c_ok:
        return "CANCELLATION-DRIVEN"
    if g_ok:
        return "GROWTH-DRIVEN"
    return "UNSEPARATED"


def run_gates(signs: np.ndarray, mags: np.ndarray, rng: np.random.Generator,
              n_perm: int = N_PERM):
    obs = observables(signs)
    valid = obs["valid"]
    fb = obs["freeze_bin"]
    pop = np.zeros(signs.shape[1], np.int8)
    pop[valid & (fb <= COMMONS_MAX_BIN)] = EARLY
    pop[valid & (fb >= CHURN_MIN_BIN)] = CHURN
    pop[valid & (fb > COMMONS_MAX_BIN) & (fb < CHURN_MIN_BIN)] = MID
    g = (np.log(mags[WINDOW_END] + EPS) - np.log(mags[WINDOW_START] + EPS))
    dec = np.zeros(signs.shape[1], np.int8)
    all3 = pop > 0
    dec[all3] = _pooled_deciles(mags[WINDOW_START][all3])

    growth = _pair_delta(g, pop, dec, EARLY, MID, rng, n_perm=n_perm)
    cancel = _pair_delta(g, pop, dec, MID, CHURN, rng, n_perm=n_perm)
    at1_replica = _pair_delta(g, pop, dec, EARLY, CHURN, rng, n_perm=n_perm)

    gc0 = gate_gc0(obs, pop, growth, cancel)
    gc1 = {"gate": "GC1", **growth}
    gc2 = {"gate": "GC2", **cancel}
    gc3 = gate_gc3(g, pop, dec, fb, rng, n_perm=n_perm)
    consistency = {"gate": "CONSISTENCY", "advisory": True,
                   "delta_growth_plus_cancel":
                       float(growth["delta"] + cancel["delta"]),
                   "at1_replica_delta": at1_replica["delta"],
                   "at1_replica_sign": at1_replica["sign"]}
    return [gc0, gc1, gc2, gc3, consistency], verdict(gc0, gc1, gc2)


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted worlds
# ══════════════════════════════════════════════════════════════════════════
def _mk_world(kind: str, rng: np.random.Generator, n: int = 30_000):
    """Three planted populations: early (fb<=10), mid (fb 12/14), churn."""
    sf = rng.choice([-1, 1], n).astype(np.int8)
    signs = np.repeat(sf[None, :], N_BINS, axis=0).astype(np.int8)
    third = n // 3
    early = np.arange(third)
    mid = np.arange(third, 2 * third)
    churn = np.arange(2 * third, n)
    # early: frozen from b1 (b0 random)
    signs[0, early] = rng.choice([-1, 1], len(early)).astype(np.int8)
    # mid: alternate through b11 (first half -> fb=12) or b13 (-> fb=14)
    mid_a, mid_b = mid[: len(mid) // 2], mid[len(mid) // 2:]
    for b in range(1, 12):
        signs[b, mid_a] = signs[b - 1, mid_a] * -1
    for b in range(1, 14):
        signs[b, mid_b] = signs[b - 1, mid_b] * -1
    # churn: alternate through b18 => flips after b15
    for b in range(1, N_BINS - 1):
        signs[b, churn] = signs[b - 1, churn] * -1
    # planted growth per population over the window
    grow = np.zeros(n, np.float32)
    if kind == "BOTH":
        grow[early], grow[mid], grow[churn] = 1.0, 0.5, 0.0
    elif kind == "GROWTH":
        grow[early], grow[mid], grow[churn] = 1.0, 0.0, 0.0
    elif kind == "CANCEL":
        grow[early], grow[mid], grow[churn] = 0.5, 0.5, 0.0
    elif kind == "UNSEP":
        grow[:] = 0.5
    elif kind == "VOID":
        # no mid population: freeze mid from b1 like early
        signs[:, mid] = np.repeat(sf[None, mid], N_BINS, axis=0)
        signs[0, mid] = rng.choice([-1, 1], len(mid)).astype(np.int8)
        grow[:] = 0.5
    # same |W_b11| distribution for all pops (deciles overlap by construction)
    m11 = np.exp(rng.normal(0.0, 1.0, n)).astype(np.float32)
    mags = np.zeros((N_BINS, n), np.float32)
    t = np.arange(N_BINS, dtype=np.float32)[:, None]
    frac = np.clip((t - WINDOW_START) / (WINDOW_END - WINDOW_START), 0, 1)
    mags[:] = m11[None, :] * np.exp(frac * grow[None, :])
    mags[:WINDOW_START] = 0.5 * m11[None, :]
    return signs, mags


def validate() -> bool:
    expected = {"BOTH": "BOTH-LIVE", "GROWTH": "GROWTH-DRIVEN",
                "CANCEL": "CANCELLATION-DRIVEN", "UNSEP": "UNSEPARATED",
                "VOID": "VOID"}
    ok_all = True
    for kind, want in expected.items():
        rng = np.random.default_rng(77)
        signs, mags = _mk_world(kind, rng)
        gates, v = run_gates(signs, mags, rng, n_perm=2000)
        ok = v == want
        ok_all &= ok
        gc1, gc2 = gates[1], gates[2]
        print(f"  world={kind:<7} verdict={v:<20} want={want:<20} "
              f"dg={gc1['delta']:+.3f} dc={gc2['delta']:+.3f} "
              f"{'PASS' if ok else 'FAIL'}")
    print(f"--validate: {'ALL PASS' if ok_all else 'FAIL'}")
    return ok_all


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strata", type=Path,
                    default=Path("results/stratigraphy-dating/pythia-160m/strata.npz"))
    ap.add_argument("--out", type=Path,
                    default=Path("results/stratigraphy-dating/pythia-160m/growth_cancel_split.jsonl"))
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return 0 if validate() else 1

    rng = np.random.default_rng(326)
    z = np.load(args.strata)
    signs, mags = z["signs"], z["mags"]
    t0 = time.time()
    gates, v = run_gates(signs, mags, rng)
    rec = {"probe": "§P-GROWTH-CANCEL-SPLIT (FROZEN s326)",
           "strata": str(args.strata),
           "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "elapsed_s": round(time.time() - t0, 1)}
    with args.out.open("w") as f:
        f.write(json.dumps(rec) + "\n")
        for gd in gates:
            f.write(json.dumps(gd) + "\n")
        f.write(json.dumps({"verdict": v, "a_priori": APRIORI}) + "\n")
    for gd in gates:
        print(json.dumps(gd))
    print(f"VERDICT: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
