"""Test 1 (s281): is D "I, repeatedly"? — decompose D onto span{I, WHNF} from the crystal Gram.

D x y = x(x(y)) = double / iterated application (probes/library.py). Hypothesis (Michael s281):
D is not an independent value-axis primitive but IDENTITY riding the reduction-DEPTH axis, i.e.
D ≈ α·I + β·WHNF — "apply I repeatedly" = identity plus a step-count/halt-distance marker.

Pure inner-product math on the committed 9×9 crystal Gram (root.gram in each model_vsm.json);
NO model load. "Repeatedly" = robustness across every model that has a Gram (cross-model = C2 axis).

Statistics (unit-diagonal cosine Gram G, labels via basis order):
  cos(D,I), cos(D,WHNF), cos(I,WHNF)                          — raw geometry
  explained_frac(D | {I,WHNF}) + coeffs α (on I), β (on WHNF) — least-squares projection
  partial cos(D,I | WHNF)                                     — D vs I on the NON-halt (value) axis
NULLS (λ yardstick): the same for EVERY combinator X∈{K,B,C,S,D,W,Y}; D "is I repeatedly" only if
its explained_frac AND partial-cos-with-I|WHNF stand OUT above the other active reducers (which
are also WHNF-anti-correlated). A high explained_frac shared by all reducers ≠ D-specific.

License: MIT (`λ provenance`).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

ROOT = Path("results/opcode-trace")
OUT = Path("results/crystal-d-is-i")


def load_grams():
    """{model_name: (basis_list, gram np.ndarray)} for every model_vsm.json with a 9-combinator gram."""
    out = {}
    for p in sorted(ROOT.glob("*/model_vsm.json")):
        try:
            d = json.loads(p.read_text())
            basis = d["basis"]
            g = np.array(d["root"]["gram"], float)
        except Exception:
            continue
        if g.shape != (len(basis), len(basis)) or "D" not in basis:
            continue
        # defensively renormalize to a correlation matrix (unit diagonal)
        dg = np.sqrt(np.clip(np.diag(g), 1e-12, None))
        g = g / np.outer(dg, dg)
        out[d["root"].get("name", p.parent.name)] = (basis, g)
    return out


def project_onto(G, t, basis_idx):
    """least-squares project vector t onto span{basis_idx} using only the Gram.
    returns (coeffs, explained_frac)."""
    B = np.array(basis_idx)
    M = G[np.ix_(B, B)]
    b = G[t, B]
    coeffs = np.linalg.solve(M, b)
    explained = float(coeffs @ b)          # ||proj||² since ||t||²=1
    return coeffs, explained / float(G[t, t])


def partial_cos(G, a, b, c):
    """partial correlation of a,b controlling for c (unit-diagonal G)."""
    rab, rac, rbc = G[a, b], G[a, c], G[b, c]
    denom = math.sqrt(max(1e-12, (1 - rac**2) * (1 - rbc**2)))
    return (rab - rac * rbc) / denom


def main() -> None:
    grams = load_grams()
    if not grams:
        print("no grams found under", ROOT)
        return
    print(f"[D=I?] {len(grams)} models with a 9-combinator crystal Gram\n")

    reducers = ["K", "B", "C", "S", "D", "W", "Y"]   # non-{I,WHNF} combinators = the null cohort
    per_model = {}
    agg = {"cos_D_I": [], "cos_D_WHNF": [], "cos_I_WHNF": [],
           "expl_D": [], "alpha_D": [], "beta_D": [], "partial_D_I": [],
           "D_rank_expl": [], "D_rank_partial": [], "n_reducers": []}

    hdr = f"{'model':<26} {'cosDI':>6} {'cosDW':>6} {'expl%':>6} {'αI':>6} {'βW':>6} {'pc(D,I|W)':>9} {'rk_ex':>5} {'rk_pc':>5}"
    print(hdr)
    print("-" * len(hdr))
    for name, (basis, G) in grams.items():
        idx = {c: basis.index(c) for c in basis}
        if not all(c in idx for c in ("I", "WHNF", "D")):
            continue
        iI, iW, iD = idx["I"], idx["WHNF"], idx["D"]
        coeffs, expl = project_onto(G, iD, [iI, iW])
        aD, bD = float(coeffs[0]), float(coeffs[1])
        pcD = partial_cos(G, iD, iI, iW)

        # null cohort: explained_frac + partial-cos-with-I|WHNF for every reducer present
        cohort = [c for c in reducers if c in idx]
        expl_all = {c: project_onto(G, idx[c], [iI, iW])[1] for c in cohort}
        pc_all = {c: partial_cos(G, idx[c], iI, iW) for c in cohort}
        # rank of D (1 = highest) among the cohort
        rank_ex = 1 + sum(1 for c in cohort if expl_all[c] > expl_all["D"])
        rank_pc = 1 + sum(1 for c in cohort if pc_all[c] > pc_all["D"])

        per_model[name] = {
            "cos_D_I": round(G[iD, iI], 4), "cos_D_WHNF": round(G[iD, iW], 4),
            "cos_I_WHNF": round(G[iI, iW], 4),
            "explained_frac_D": round(expl, 4), "alpha_I": round(aD, 4), "beta_WHNF": round(bD, 4),
            "partial_cos_D_I_given_WHNF": round(pcD, 4),
            "D_rank_explained": rank_ex, "D_rank_partial": rank_pc, "n_reducers": len(cohort),
            "explained_all": {c: round(v, 4) for c, v in expl_all.items()},
            "partial_all": {c: round(v, 4) for c, v in pc_all.items()},
        }
        for k, v in [("cos_D_I", G[iD, iI]), ("cos_D_WHNF", G[iD, iW]), ("cos_I_WHNF", G[iI, iW]),
                     ("expl_D", expl), ("alpha_D", aD), ("beta_D", bD), ("partial_D_I", pcD),
                     ("D_rank_expl", rank_ex), ("D_rank_partial", rank_pc), ("n_reducers", len(cohort))]:
            agg[k].append(v)
        short = name.split("/")[-1][:26]
        print(f"{short:<26} {G[iD,iI]:>6.3f} {G[iD,iW]:>6.3f} {expl*100:>6.1f} {aD:>6.3f} "
              f"{bD:>6.3f} {pcD:>9.3f} {rank_ex:>5} {rank_pc:>5}")

    def ms(x):
        a = np.array(x, float)
        return float(a.mean()), float(a.std())

    print("\n=== aggregate across models (mean ± sd) ===")
    for k in ["cos_D_I", "cos_D_WHNF", "cos_I_WHNF", "expl_D", "alpha_D", "beta_D", "partial_D_I"]:
        m, s = ms(agg[k])
        print(f"  {k:<14} {m:+.3f} ± {s:.3f}")
    rex = np.array(agg["D_rank_expl"]); rpc = np.array(agg["D_rank_partial"])
    print(f"  D rank by explained_frac : mean {rex.mean():.2f} (1=highest of "
          f"{int(np.mean(agg['n_reducers']))} reducers); top-1 in {int((rex==1).sum())}/{len(rex)} models")
    print(f"  D rank by partial(D,I|W) : mean {rpc.mean():.2f}; "
          f"top-1 in {int((rpc==1).sum())}/{len(rpc)} models")

    # verdict heuristic (pre-stated): "D is I repeatedly" ⟺ explained high AND α>0 (I-component)
    # AND D stands out from the reducer cohort on BOTH ranks (specific, not shared).
    m_expl = ms(agg["expl_D"])[0]; m_alpha = ms(agg["alpha_D"])[0]; m_pc = ms(agg["partial_D_I"])[0]
    stands_out = (rex.mean() <= 2.0 and rpc.mean() <= 2.0)
    verdict = (m_expl > 0.66 and m_alpha > 0.15 and m_pc > 0.3 and stands_out)
    print(f"\n[VERDICT heuristic] D≈I⊕WHNF (identity+depth, D-SPECIFIC) = {verdict}")
    print(f"  (explained {m_expl:.2f}>0.66, αI {m_alpha:+.2f}>0.15, partial {m_pc:+.2f}>0.3, "
          f"stands-out {stands_out}) — βW sign {'neg=away-from-halt(active)' if ms(agg['beta_D'])[0]<0 else 'pos'}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "d_is_i.json").write_text(json.dumps({
        "test": "D ≈ I ⊕ WHNF (is D identity, repeatedly?)",
        "basis_order_note": "cosine crystal Gram (root.gram), unit diagonal",
        "n_models": len(per_model),
        "aggregate": {k: {"mean": round(ms(agg[k])[0], 4), "sd": round(ms(agg[k])[1], 4)}
                      for k in ["cos_D_I", "cos_D_WHNF", "cos_I_WHNF", "expl_D",
                                "alpha_D", "beta_D", "partial_D_I"]},
        "D_rank_explained_mean": round(float(rex.mean()), 3),
        "D_rank_partial_mean": round(float(rpc.mean()), 3),
        "verdict_D_is_I_repeatedly_Dspecific": bool(verdict),
        "per_model": per_model,
    }, indent=2))
    print(f"\n[D=I?] wrote {OUT}/d_is_i.json")


if __name__ == "__main__":
    main()
