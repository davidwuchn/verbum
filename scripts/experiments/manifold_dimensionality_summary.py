#!/usr/bin/env python3
# register: spectral/semantic
"""Cross-model verdict for the 5D crystal lattice manifold test.

Consumes results/manifold-dimensionality/<model>.{json,npz} produced by
manifold_dimensionality_null.py and answers two questions HONESTLY:

  Q1 (dimensionality): what effective dimension is really there (1D/2D/3D/...),
     and do the 9 combinator centroids concentrate BELOW the shuffled-label
     null? Report participation ratio + variance-top-k across models. "5D" is
     refuted if centroid PR sits at the null; supported only where PR << null.

  Q2 (universality / "property of language"): do per-model RDMs agree ACROSS
     models, and does the agreement survive the controls?
       - raw            : Spearman of upper-triangle RDMs, every model pair.
       - shuffled-probe : permute probe identity in one RDM -> null agreement
                          (the s202 consensus-r=0.99 triviality control).
       - common-mode    : subtract the mean RDM across models, re-correlate
                          (the s202 fidelity fix; deflated 0.99 -> 0.20 before).
     Split same-family vs cross-family. Compare the SEMANTIC (prob) RDM vs the
     GEOMETRIC (hidden) RDM: if prob agreement (CMR, cross-family) > hidden,
     the universal structure lives in the probabilities, supporting the user's
     hypothesis that models learn a property of language.

Usage:
  uv run python scripts/experiments/manifold_dimensionality_summary.py
License: MIT
"""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "manifold-dimensionality"


def family(model: str) -> str:
    m = model.lower()
    for key in ("pythia", "qwen", "mistral", "smollm", "olmo", "phi"):
        if key in m:
            return key
    return model.split("_")[0].lower()


def upper(D: np.ndarray) -> np.ndarray:
    iu = np.triu_indices_from(D, k=1)
    return D[iu]


def load_all():
    models = {}
    for jf in sorted(RESULTS_DIR.glob("*.json")):
        if jf.stem in ("summary",):
            continue
        meta = json.loads(jf.read_text())
        npz = RESULTS_DIR / f"{jf.stem}.npz"
        if not npz.exists():
            continue
        z = np.load(npz, allow_pickle=True)
        models[meta["model"]] = {
            "meta": meta,
            "rdm_prob": z["rdm_prob"].astype(np.float64),
            "rdm_hidden": z["rdm_hidden"].astype(np.float64),
            "labels": list(z["labels"]),
        }
    return models


def rank_matrix(D: np.ndarray) -> np.ndarray:
    """Symmetric matrix whose upper triangle holds ranks of D's distances.

    Lets node-permutation nulls reindex precomputed ranks instead of re-ranking
    each draw (spearman = pearson on ranks; a node relabel just reorders pairs)."""
    iu = np.triu_indices_from(D, k=1)
    r = rankdata(D[iu])
    R = np.zeros_like(D)
    R[iu] = r
    R[(iu[1], iu[0])] = r
    return R


def agreement_from_ranks(Ra: np.ndarray, rb: np.ndarray) -> float:
    ra = upper(Ra)
    return float(np.corrcoef(ra, rb)[0, 1])


def shuffled_null(Ra: np.ndarray, rb: np.ndarray, n: int, seed: int):
    rng = np.random.default_rng(seed)
    nrow = Ra.shape[0]
    vals = np.empty(n)
    for i in range(n):
        perm = rng.permutation(nrow)
        vals[i] = float(np.corrcoef(upper(Ra[np.ix_(perm, perm)]), rb)[0, 1])
    return float(vals.mean()), float(vals.std()), vals


def common_mode_removed(rdms: list[np.ndarray]) -> list[np.ndarray]:
    """Subtract the across-model mean RDM (rank space) from each."""
    # rank-transform each upper-triangle, rebuild, then subtract mean
    stacks = np.stack([upper(D) for D in rdms])           # [M x P]
    ranks = np.argsort(np.argsort(stacks, axis=1), axis=1).astype(np.float64)
    ranks /= ranks.shape[1]
    mean = ranks.mean(axis=0, keepdims=True)
    return [ranks[i] - mean[0] for i in range(ranks.shape[0])]


def pairwise_block(models, key, label, n_null=200):
    names = list(models.keys())
    rdms = [models[n][key] for n in names]
    ranks = [rank_matrix(D) for D in rdms]
    upr = [upper(R) for R in ranks]
    print(f"\n===== {label} ({key}) =====")
    # raw agreement + null
    raw_same, raw_cross = [], []
    for a, b in combinations(range(len(names)), 2):
        r = agreement_from_ranks(ranks[a], upr[b])
        nm, ns, _ = shuffled_null(ranks[a], upr[b], n_null, seed=a * 100 + b)
        same = family(names[a]) == family(names[b])
        (raw_same if same else raw_cross).append(r)
        tag = "same" if same else "CROSS"
        print(f"  {tag:5s} {family(names[a]):7s} x {family(names[b]):7s}: "
              f"r={r:+.3f}  null={nm:+.3f}+-{ns:.3f}")
    # common-mode-removed agreement
    cmr = common_mode_removed(rdms)
    cmr_same, cmr_cross = [], []
    for a, b in combinations(range(len(names)), 2):
        r = float(np.corrcoef(cmr[a], cmr[b])[0, 1])
        same = family(names[a]) == family(names[b])
        (cmr_same if same else cmr_cross).append(r)

    def mean(x):
        return float(np.mean(x)) if x else float("nan")

    summary = {
        "raw_same_mean": mean(raw_same), "raw_cross_mean": mean(raw_cross),
        "cmr_same_mean": mean(cmr_same), "cmr_cross_mean": mean(cmr_cross),
        "n_same": len(raw_same), "n_cross": len(raw_cross),
    }
    print(f"  --- raw:  same={summary['raw_same_mean']:+.3f}  "
          f"CROSS={summary['raw_cross_mean']:+.3f}")
    print(f"  --- CMR:  same={summary['cmr_same_mean']:+.3f}  "
          f"CROSS={summary['cmr_cross_mean']:+.3f}  "
          f"(common-mode removed = the honest universality)")
    return summary


def dimensionality_table(models):
    print("\n===== EFFECTIVE DIMENSIONALITY (per model) =====")
    print(f"{'model':28s} {'RDM':6s} {'fullPR':>7s} {'v1':>5s} {'v2':>5s} "
          f"{'v3':>5s} {'cenPR':>6s} {'null':>6s} {'p_conc':>7s} {'sepP':>7s}")
    rows = []
    for name, d in models.items():
        for rdm in ("prob", "hidden"):
            r = d["meta"]["results"][rdm]
            fc, cen, cn, sep = (r["full_cloud"], r["centroids"],
                                r["centroid_null"], r["separation"])
            print(f"{name[:28]:28s} {rdm:6s} {fc['pr']:7.2f} "
                  f"{fc['var_top1']:5.2f} {fc['var_top2']:5.2f} {fc['var_top3']:5.2f} "
                  f"{cen['pr']:6.2f} {cn['null_mean']:6.2f} "
                  f"{cn['p_value_concentrated']:7.4f} {sep['p_value']:7.4f}")
            rows.append({"model": name, "rdm": rdm, "full_pr": fc["pr"],
                         "var_top1": fc["var_top1"], "var_top2": fc["var_top2"],
                         "var_top3": fc["var_top3"], "centroid_pr": cen["pr"],
                         "centroid_null_mean": cn["null_mean"],
                         "p_concentrated": cn["p_value_concentrated"],
                         "sep_p": sep["p_value"]})
    return rows


def main():
    models = load_all()
    if len(models) < 2:
        print(f"need >=2 models in {RESULTS_DIR}; found {len(models)}")
        return
    print(f"loaded {len(models)} models: {', '.join(family(m) for m in models)}")

    dim_rows = dimensionality_table(models)
    prob = pairwise_block(models, "rdm_prob", "SEMANTIC / probabilities")
    hidden = pairwise_block(models, "rdm_hidden", "GEOMETRIC / hidden state")

    print("\n===== VERDICT INPUTS =====")
    print("  Raw cross-family agreement is the universality measure (vs shuffled-")
    print("  probe null ~0.00); CMR-cross ~0 for BOTH means the SHARED structure is")
    print("  a single common mode (rank-~1), not a rich multi-D lattice.")
    print(f"  semantic  raw cross-family: {prob['raw_cross_mean']:+.3f}  "
          f"same-family CMR residual: {prob['cmr_same_mean']:+.3f}")
    print(f"  geometric raw cross-family: {hidden['raw_cross_mean']:+.3f}  "
          f"same-family CMR residual: {hidden['cmr_same_mean']:+.3f}")
    # the meaningful discriminator: raw cross-family + same-family residual
    sem_more = (prob["raw_cross_mean"] > hidden["raw_cross_mean"]
                and prob["cmr_same_mean"] > hidden["cmr_same_mean"])
    print(f"  => semantic {'MORE' if sem_more else 'NOT clearly more'} universal "
          f"than geometric (raw cross + same-family residual)")

    out = {
        "n_models": len(models),
        "families": sorted(set(family(m) for m in models)),
        "dimensionality": dim_rows,
        "agreement_prob": prob,
        "agreement_hidden": hidden,
        "semantic_more_universal": bool(sem_more),
        "note": ("raw cross-family agreement >> shuffled-probe null => universal "
                 "structure is REAL; CMR-cross ~0 for both RDMs => that shared "
                 "structure is a single common mode (rank-~1), NOT a 5D lattice."),
    }
    (RESULTS_DIR / "summary.json").write_text(json.dumps(out, indent=2))
    print(f"\nwrote {RESULTS_DIR / 'summary.json'}")


if __name__ == "__main__":
    main()
