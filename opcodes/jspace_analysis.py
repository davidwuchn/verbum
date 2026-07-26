#!/usr/bin/env python3
# register: J-space workspace geometry (sidecar; never feeds the classifier)
"""Cross-model read of the jspace projector artifacts (s270 pre-regs + T1).

Inputs: results/opcode-trace/*/jspace_projector.json (s270c sweep).

P1  fraction(Y,WHNF,S) > fraction(K,I,B) — per-artifact shuffled-label gate is
    already computed by projector.py; here we aggregate: per-depth sign test
    (binomial, one-sided) + gate count across models.

P3  9-vector (per-op workspace fractions) stability across models — mean
    pairwise Pearson corr of the 9-vectors at each depth, gated by a
    shuffled-label null (each model's 9 labels permuted independently).

T1  CASCADE=REDUCTION — effective rank of the J-space consensus basis
    descends with depth. PRE-REGISTERED measure (fixed before data, no
    tunable cutoff): effective rank ≡ participation ratio
    PR = (Σλ)² / Σλ²  over λ = strength²  (threshold-free; λ yardstick).
    Gate: one-sided sign test across models on PR(d=0.25) > PR(d=0.75).

P2  verbalization is a judgment read: the top-strength directions' plus/minus
    tokens for the largest model are dumped for eyeball (WHNF-adjacent watch).

Output: results/opcode-trace/jspace_analysis.json + stdout tables.

Usage: uv run python opcodes/jspace_analysis.py [--verbalize-model qwen3-6-27b]

License: MIT.
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations, pairwise
from math import comb
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
RESULTS_DIR = _ROOT / "results" / "opcode-trace"

CONTENT = ("Y", "WHNF", "S")
OPERATOR = ("K", "I", "B")
OPS = ("K", "I", "B", "C", "S", "D", "W", "Y", "WHNF")


def sign_test_p(k: int, n: int) -> float:
    """One-sided binomial P(X >= k | n, 0.5)."""
    return sum(comb(n, i) for i in range(k, n + 1)) / 2.0**n


def participation_ratio(strengths: list[float]) -> float:
    lam = np.asarray(strengths, dtype=np.float64) ** 2
    s = lam.sum()
    return float(s * s / (lam * lam).sum()) if s > 0 else float("nan")


def load_artifacts() -> dict[str, dict]:
    out = {}
    for p in sorted(RESULTS_DIR.glob("*/jspace_projector.json")):
        out[p.parent.name] = json.loads(p.read_text(encoding="utf-8"))
    return out


def p1_table(arts: dict[str, dict]) -> dict:
    all_depths: list[str] = []
    rows = {}
    for slug, art in arts.items():
        rows[slug] = {}
        # NOTE: models with fewer unique quartile layers than depths (tiny
        # models where quartiles dedup, e.g. pythia-14m) align positionally;
        # missing depths are simply absent and excluded from that depth's
        # aggregate (n varies per depth).
        for dl, dep in zip(art["depth_layers"], art["depths"], strict=False):
            g = art["layers"][str(dl)]["p1_gap"]
            rows[slug][str(dep)] = {
                "observed": g["observed"], "z": g["z"], "p": g["p"],
                "gated": bool(g["gated"]),
            }
            if str(dep) not in all_depths:
                all_depths.append(str(dep))
    agg = {}
    for dep in all_depths:
        have = [r[dep] for r in rows.values() if dep in r]
        pos = sum(1 for c in have if c["observed"] > 0)
        gated = sum(1 for c in have if c["gated"])
        n = len(have)
        agg[dep] = {
            "n": n, "positive": pos, "gated": gated,
            "sign_p": sign_test_p(pos, n),
        }
    return {"per_model": rows, "aggregate": agg}


def p3_stability(arts: dict[str, dict], n_perm: int = 10000, seed: int = 272) -> dict:
    rng = np.random.default_rng(seed)
    out = {}
    depths = next(iter(arts.values()))["depths"]
    for di, dep in enumerate(depths):
        vecs = []
        for art in arts.values():
            if di >= len(art["depth_layers"]):
                continue  # deduped quartiles (tiny models)
            dl = art["depth_layers"][di]
            fr = art["layers"][str(dl)]["fractions"]
            vecs.append(np.array([fr[o] for o in OPS], dtype=np.float64))
        vecs = np.stack(vecs)

        def mean_pair(v):
            cs = [
                np.corrcoef(a, b)[0, 1]
                for a, b in combinations(v, 2)
            ]
            return float(np.mean(cs))

        obs = mean_pair(vecs)
        null = np.empty(n_perm)
        for i in range(n_perm):
            null[i] = mean_pair(
                np.stack([v[rng.permutation(len(OPS))] for v in vecs])
            )
        z = (obs - null.mean()) / null.std()
        p = float((np.sum(null >= obs) + 1) / (n_perm + 1))
        out[str(dep)] = {
            "mean_pairwise_corr": obs, "null_mean": float(null.mean()),
            "null_sd": float(null.std()), "z": float(z), "p": p,
            "gated": bool(p < 0.05),
        }
    return out


def t1_rank(arts: dict[str, dict]) -> dict:
    per_model = {}
    descend = 0
    monotone = 0
    for slug, art in arts.items():
        prs = []
        for dl in art["depth_layers"]:
            prs.append(participation_ratio(art["layers"][str(dl)]["strengths"]))
        per_model[slug] = {
            "depths": art["depths"], "pr": [round(p, 3) for p in prs],
            "descends_25_to_75": bool(prs[0] > prs[-1]),
            "monotone_desc": bool(all(a > b for a, b in pairwise(prs))),
        }
        descend += prs[0] > prs[-1]
        monotone += all(a > b for a, b in pairwise(prs))
    n = len(per_model)
    return {
        "measure": "participation ratio of strength^2 (pre-registered, "
                   "threshold-free)",
        "per_model": per_model,
        "aggregate": {
            "n": n, "descend_25_to_75": descend,
            "sign_p_descend": sign_test_p(descend, n),
            "monotone_desc": monotone,
            "sign_p_monotone_all_orderings": None,  # 1/6 chance per model
        },
    }


def dump_verbalize(art: dict, slug: str, top: int = 5) -> None:
    print(f"\nP2 VERBALIZE — {slug} (top {top} dirs per depth; eyeball read)")
    for dl, dep in zip(art["depth_layers"], art["depths"], strict=False):
        print(f"  depth {dep} (L{dl}):")
        for v in art["layers"][str(dl)]["verbalize"][:top]:
            plus = " ".join(t.strip() for t in v["plus"][:6])
            minus = " ".join(t.strip() for t in v["minus"][:6])
            print(f"    dir{v['dir']:>2} s={v['strength']:.1f}  +[{plus}]")
            print(f"           -[{minus}]")


def main() -> None:
    ap = argparse.ArgumentParser(description="Cross-model jspace analysis")
    ap.add_argument("--verbalize-model", default="qwen3-6-27b")
    ap.add_argument("--n-perm", type=int, default=10000)
    args = ap.parse_args()

    arts = load_artifacts()
    print(f"[jspace-analysis] {len(arts)} artifacts: {', '.join(arts)}")

    p1 = p1_table(arts)
    print("\nP1 fraction(Y,WHNF,S) > fraction(K,I,B) — per depth:")
    for dep, a in p1["aggregate"].items():
        print(f"  depth {dep}: {a['positive']}/{a['n']} positive "
              f"(sign-test p={a['sign_p']:.2e}) | {a['gated']}/{a['n']} gated")
    print("  per-model gates:")
    for slug, r in p1["per_model"].items():
        cells = " ".join(
            f"{dep}:{'G' if c['gated'] else ('+' if c['observed'] > 0 else '-')}"
            for dep, c in r.items()
        )
        print(f"    {slug:<24} {cells}")

    p3 = p3_stability(arts, n_perm=args.n_perm)
    print("\nP3 9-vector stability across models (shuffled-label null):")
    for dep, s in p3.items():
        print(f"  depth {dep}: mean pairwise corr={s['mean_pairwise_corr']:+.3f} "
              f"(null {s['null_mean']:+.3f}±{s['null_sd']:.3f}) "
              f"z={s['z']:.2f} p={s['p']:.4f} gated={s['gated']}")

    t1 = t1_rank(arts)
    print("\nT1 CASCADE=REDUCTION — effective rank (PR) vs depth:")
    for slug, r in t1["per_model"].items():
        arrow = " > ".join(f"{p:.1f}" for p in r["pr"])
        tag = "MONO" if r["monotone_desc"] else (
            "desc" if r["descends_25_to_75"] else "FLAT/ASC")
        print(f"  {slug:<24} PR {arrow}  [{tag}]")
    a = t1["aggregate"]
    print(f"  descend .25→.75: {a['descend_25_to_75']}/{a['n']} "
          f"(sign-test p={a['sign_p_descend']:.2e}) | "
          f"strictly monotone: {a['monotone_desc']}/{a['n']}")

    if args.verbalize_model in arts:
        dump_verbalize(arts[args.verbalize_model], args.verbalize_model)

    out = RESULTS_DIR / "jspace_analysis.json"
    out.write_text(json.dumps(
        {"p1": p1, "p3": p3, "t1": t1, "n_models": len(arts),
         "models": list(arts)}, indent=2), encoding="utf-8")
    print(f"\n[jspace-analysis] wrote {out}")


if __name__ == "__main__":
    main()
