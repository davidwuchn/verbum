#!/usr/bin/env python3
"""§P-AMP-TRAJECTORY — accumulation-vs-uniform-growth re-read of strata.npz.

Pre-reg: mementum/knowledge/explore/types-are-a-modulation-scheme.md
§P-AMP-TRAJECTORY (FROZEN s325, Michael GO — frozen BEFORE any trajectory
statistic was computed; SD1/SD2 read signs + final magnitudes only).

Claim (Michael, s325, on the INVERTED verdict): the lattice concentrates by
ACCUMULATION — amplitude ∝ ∫consistent-signal over the whole run; contested
cancels to net≈0. Rival 1: UNIFORM norm growth (generic optimizer physics —
"weights keep growing" is trivially true, so the claim must be DIFFERENTIAL).
Rival 2: EROSION (residual self-erasure flavor: late writes route away from
committed coords).

Statistic (pinned): fixed shared window b11→b19 (steps 1k→143k, post-freeze
for the whole early-frozen population by construction); per-coord
g = log(|W_b19|+ε) − log(|W_b11|+ε); early-frozen (freeze≤b10) vs churners
(≥1 flip after b15) matched within pooled |W_b11| deciles; AT1 Δ = weighted
mean over qualifying deciles (≥500 each pop) of (mean g_early − mean g_churn);
within-decile label-permutation null ×10k. Medians reported, not gated.
Weight decay biases AGAINST accumulation ⇒ conservative.

Verdicts + a-priori (NOT tuned; modal on the null):
ACCUMULATION-CONCENTRATION 30 / UNIFORM-GROWTH 40 / EROSION 20 / VOID 10.

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
MIN_PER_DECILE = 500           # decile qualifies iff >=500 of EACH population
MIN_QUAL_DECILES = 3
N_PERM = 10_000
ALPHA = 0.05
APRIORI = {"ACCUMULATION-CONCENTRATION": 30, "UNIFORM-GROWTH": 40,
           "EROSION": 20, "VOID": 10}


def _pooled_deciles(x: np.ndarray) -> np.ndarray:
    """Decile labels 1..10 over the pooled vector x (rank-based)."""
    order = np.argsort(x, kind="stable")
    r = np.empty(len(x), float)
    r[order] = np.arange(len(x), dtype=float)
    return np.minimum((r / len(x) * 10).astype(int) + 1, 10)


def gate_at0(obs: dict, pop: np.ndarray, quals: list[int]) -> dict:
    valid = obs["valid"]
    n = max(int(valid.sum()), 1)
    n_early = int((pop == 1).sum())
    n_churn = int((pop == 2).sum())
    ok = (float(valid.mean()) > 0.99 and n_early / n >= 0.01
          and n_churn / n >= 0.01 and len(quals) >= MIN_QUAL_DECILES)
    return {"gate": "AT0", "pass": bool(ok), "n_early": n_early,
            "n_churn": n_churn, "n_qualifying_deciles": len(quals),
            "qualifying_deciles": quals}


def gate_at1(g: np.ndarray, pop: np.ndarray, dec: np.ndarray,
             quals: list[int], rng: np.random.Generator,
             n_perm: int = N_PERM) -> dict:
    if not quals:
        return {"gate": "AT1", "delta": 0.0, "p_pos": 1.0, "p_neg": 1.0,
                "sign": "ns", "per_decile": {}}
    per, wts, med = {}, [], {}
    pools = []
    for d in quals:
        m = dec == d
        ge, gc = g[m & (pop == 1)], g[m & (pop == 2)]
        per[str(d)] = float(ge.mean() - gc.mean())
        med[str(d)] = float(np.median(ge) - np.median(gc))
        wts.append(len(ge) + len(gc))
        pools.append((np.concatenate([ge, gc]), len(ge)))
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
    return {"gate": "AT1", "delta": delta, "p_pos": p_pos, "p_neg": p_neg,
            "sign": sign, "per_decile_mean": per, "per_decile_median": med}


def gate_at2(obs: dict, mags: np.ndarray, pop: np.ndarray) -> dict:
    """Advisory: fraction of final amplitude present at sign-freeze."""
    sel = np.where(pop == 1)[0]
    if len(sel) == 0:
        return {"gate": "AT2", "advisory": True, "n": 0}
    fb = obs["freeze_bin"][sel].astype(int)
    r = mags[fb, sel] / (mags[N_BINS - 1, sel] + EPS)
    q = np.percentile(r, [25, 50, 75])
    return {"gate": "AT2", "advisory": True, "n": len(sel),
            "R_q25": float(q[0]), "R_median": float(q[1]),
            "R_q75": float(q[2]), "frac_R_below_half": float((r < 0.5).mean())}


def verdict(at0: dict, at1: dict) -> str:
    if not at0["pass"]:
        return "VOID"
    if at1["sign"] == "positive":
        return "ACCUMULATION-CONCENTRATION"
    if at1["sign"] == "negative":
        return "EROSION"
    return "UNIFORM-GROWTH"


def run_gates(signs: np.ndarray, mags: np.ndarray, rng: np.random.Generator,
              n_perm: int = N_PERM):
    obs = observables(signs)
    valid = obs["valid"]
    fb = obs["freeze_bin"]
    pop = np.zeros(signs.shape[1], np.int8)      # 0 other, 1 early, 2 churn
    pop[valid & (fb <= COMMONS_MAX_BIN)] = 1
    pop[valid & (fb >= CHURN_MIN_BIN)] = 2
    g = (np.log(mags[WINDOW_END] + EPS) - np.log(mags[WINDOW_START] + EPS))
    both = pop > 0
    dec = np.zeros(signs.shape[1], np.int8)
    dec[both] = _pooled_deciles(mags[WINDOW_START][both])
    quals = [d for d in range(1, 11)
             if (both & (dec == d) & (pop == 1)).sum() >= MIN_PER_DECILE
             and (both & (dec == d) & (pop == 2)).sum() >= MIN_PER_DECILE]
    at0 = gate_at0(obs, pop, quals)
    at1 = gate_at1(g, pop, dec, quals, rng, n_perm=n_perm)
    at2 = gate_at2(obs, mags, pop)
    return [at0, at1, at2], verdict(at0, at1)


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted worlds
# ══════════════════════════════════════════════════════════════════════════
def _mk_world(kind: str, rng: np.random.Generator, n: int = 20_000):
    sf = rng.choice([-1, 1], n).astype(np.int8)
    signs = np.repeat(sf[None, :], N_BINS, axis=0).astype(np.int8)
    half = n // 2
    early = np.arange(half)
    churn = np.arange(half, n)
    # early: frozen from b1 (b0 random)
    signs[0, early] = rng.choice([-1, 1], half).astype(np.int8)
    # churn: alternate every bin from b1 through b18 => flips after b15
    for b in range(1, N_BINS - 1):
        signs[b, churn] = signs[b - 1, churn] * -1
    # magnitudes: same |W_b11| distribution for BOTH pops (deciles overlap)
    m11 = np.exp(rng.normal(0.0, 1.0, n)).astype(np.float32)
    g = np.zeros(n, np.float32)
    if kind == "ACCUM":
        g[early], g[churn] = 1.0, 0.0
    elif kind == "UNIFORM":
        g[:] = 0.5
    elif kind == "EROSION":
        g[early], g[churn] = 0.0, 1.0
    elif kind == "VOID":
        signs[:, churn] = np.repeat(sf[None, churn], N_BINS, axis=0)  # no churners
        g[:] = 0.5
    mags = np.zeros((N_BINS, n), np.float32)
    t = np.arange(N_BINS, dtype=np.float32)[:, None]
    frac = np.clip((t - WINDOW_START) / (WINDOW_END - WINDOW_START), 0, 1)
    mags[:] = m11[None, :] * np.exp(frac * g[None, :])
    mags[:WINDOW_START] = 0.5 * m11[None, :]
    return signs, mags


def validate() -> bool:
    expected = {"ACCUM": "ACCUMULATION-CONCENTRATION",
                "UNIFORM": "UNIFORM-GROWTH", "EROSION": "EROSION",
                "VOID": "VOID"}
    ok_all = True
    for kind, want in expected.items():
        rng = np.random.default_rng(77)
        signs, mags = _mk_world(kind, rng)
        gates, v = run_gates(signs, mags, rng, n_perm=2000)
        ok = v == want
        ok_all &= ok
        at1 = gates[1]
        print(f"  world={kind:<8} verdict={v:<26} want={want:<26} "
              f"delta={at1['delta']:+.3f} {'PASS' if ok else 'FAIL'}")
    print(f"--validate: {'ALL PASS' if ok_all else 'FAIL'}")
    return ok_all


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strata", type=Path,
                    default=Path("results/stratigraphy-dating/pythia-160m/strata.npz"))
    ap.add_argument("--out", type=Path,
                    default=Path("results/stratigraphy-dating/pythia-160m/amp_trajectory.jsonl"))
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return 0 if validate() else 1

    rng = np.random.default_rng(325)
    z = np.load(args.strata)
    signs, mags = z["signs"], z["mags"]
    t0 = time.time()
    gates, v = run_gates(signs, mags, rng)
    rec = {"probe": "§P-AMP-TRAJECTORY (FROZEN s325)",
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
