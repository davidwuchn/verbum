#!/usr/bin/env python3
# register: semantic
"""How much of the universal axis do rich features name? (CV-R2 + null)

Consumes, per model:
  results/manifold-axis-topology/<model>.npz           (rdm_prob_full, axis_coords, topk)
  results/manifold-axis-topology/<model>.features.npz  (rich distributional features)

TARGET: consensus axis-1 = MDS axis-1 of the mean prob-RDM across the model set
(the universal axis; per-model best-axis |r|=0.95, s211).

HIERARCHICAL naming (cumulative blocks; each consensus feature = z-scored mean
across models). For each block report in-sample R^2, 5-fold CV-R^2 (the honest
number), and for the FULL block a permutation-null CV-R^2 (shuffle the axis,
B=200) so a "named axis" only counts if CV-R^2 >> null.

  B0 s211 baseline : entropy, top1_function, topk_function_frac
  B1 + peakedness  : + top1_prob, top10_mass, collision, log_n90, top256_mass
  B2 + glue mass   : + function_mass, content_mass, punct_mass
  B3 + distinctive : + kl_to_mean
  B4 + prompt-only : + n_words, ends_punct, ends_space, has_lambda, last_word_fn
                     (model-FREE prompt text features = is the axis a property of
                      the prompts/language, computable with no forward pass?)

Usage: uv run python scripts/experiments/axis_naming_summary.py
License: MIT
"""
from __future__ import annotations

import json
import string
from pathlib import Path

import numpy as np
from transformers import AutoTokenizer

from verbum.probes.library import crystal_probes

_PR = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = _PR / "results" / "manifold-axis-topology"
OUT = RESULTS_DIR / "axis_naming.json"

STOP = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "at", "for",
    "with", "by", "from", "as", "is", "are", "was", "were", "be", "been",
    "being", "it", "its", "this", "that", "these", "those", "he", "she", "they",
    "we", "you", "i", "his", "her", "their", "our", "your", "my", "him", "them",
    "us", "not", "no", "nor", "so", "if", "then", "than", "which", "who", "whom",
    "whose", "what", "when", "where", "why", "how", "all", "any", "some", "can",
    "will", "would", "could", "should", "may", "might", "must", "have", "has",
    "had", "do", "does", "did", "s", "t", "re", "ll", "ve", "m", "d", "into",
    "out", "up", "down", "over", "under", "about", "after", "before", "between",
    "there", "here", "one", "two", "more", "most", "such", "only", "also", "very",
}
PUNCT = set(string.punctuation) | {"\u201c", "\u201d", "\u2018", "\u2019",
                                   "\u2014", "\u2013", "\u2026", "\u00b7"}

BLOCKS = [
    ("B0_s211_baseline", ["entropy", "top1_function", "topk_function_frac"]),
    ("B1_peakedness", ["top1_prob", "top10_mass", "collision", "log_n90",
                       "top256_mass"]),
    ("B2_glue_mass", ["function_mass", "content_mass", "punct_mass"]),
    ("B3_distinctiveness", ["kl_to_mean"]),
    ("B4_prompt_only", ["n_words", "ends_punct", "ends_space", "has_lambda",
                        "last_word_fn"]),
]


def family(m):
    m = m.lower()
    for k in ("pythia", "qwen", "mistral", "smollm", "olmo"):
        if k in m:
            return k
    return m


def classify_token(s):
    t = s.strip().lower()
    if s.strip() == "":
        return "space"
    if all((ch in PUNCT or ch.isspace()) for ch in t) and t != "":
        return "punct"
    core = "".join(ch for ch in t if ch.isalnum())
    if core == "":
        return "punct"
    if core in STOP:
        return "function"
    return "content"


def mds_axis1(D):
    n = D.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    B = (B + B.T) / 2
    w, V = np.linalg.eigh(B)
    j = int(np.argmax(w))
    return V[:, j] * np.sqrt(max(w[j], 0.0))


def corr(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def _fit_r2(ytr, Xtr, yte, Xte):
    """OLS on train (standardized by train stats), R^2 on test."""
    mu = Xtr.mean(0); sd = Xtr.std(0) + 1e-12
    Atr = np.column_stack([np.ones(len(ytr)), (Xtr - mu) / sd])
    beta, *_ = np.linalg.lstsq(Atr, ytr, rcond=None)
    Ate = np.column_stack([np.ones(len(yte)), (Xte - mu) / sd])
    pred = Ate @ beta
    ss_res = ((yte - pred) ** 2).sum()
    ss_tot = ((yte - yte.mean()) ** 2).sum() + 1e-30
    return 1 - ss_res / ss_tot


def in_sample_r2(y, X):
    return _fit_r2(y, X, y, X)


def cv_r2(y, X, k=5, seed=0):
    """Out-of-fold pooled R^2."""
    n = len(y)
    rng = np.random.default_rng(seed)
    order = rng.permutation(n)
    folds = np.array_split(order, k)
    pred = np.empty(n)
    for f in folds:
        mask = np.ones(n, bool); mask[f] = False
        mu = X[mask].mean(0); sd = X[mask].std(0) + 1e-12
        Atr = np.column_stack([np.ones(mask.sum()), (X[mask] - mu) / sd])
        beta, *_ = np.linalg.lstsq(Atr, y[mask], rcond=None)
        Ate = np.column_stack([np.ones(len(f)), (X[f] - mu) / sd])
        pred[f] = Ate @ beta
    ss_res = ((y - pred) ** 2).sum()
    ss_tot = ((y - y.mean()) ** 2).sum() + 1e-30
    return 1 - ss_res / ss_tot


def main():
    # ---- load models that have BOTH npz and features.npz ----
    models = {}
    for jf in sorted(RESULTS_DIR.glob("*.features.json")):
        name = json.loads(jf.read_text())["model"]
        safe = name.replace("/", "_")
        base = RESULTS_DIR / f"{safe}.npz"
        feat = RESULTS_DIR / f"{safe}.features.npz"
        if not (base.exists() and feat.exists()):
            continue
        z = np.load(base, allow_pickle=True)
        zf = np.load(feat, allow_pickle=True)
        models[name] = {"z": z, "zf": zf}
    if len(models) < 2:
        print(f"need >=2 models with features; found {len(models)}")
        return
    names = list(models.keys())
    print(f"loaded {len(names)} models: {', '.join(family(n) for n in names)}")

    labels = [str(x) for x in models[names[0]]["zf"]["labels"]]
    fnames = [str(x) for x in models[names[0]]["zf"]["feature_names"]]
    fidx = {f: j for j, f in enumerate(fnames)}
    N = len(labels)

    # consensus axis-1
    consensus = np.mean([models[n]["z"]["rdm_prob_full"].astype(np.float64)
                         for n in names], axis=0)
    cax1 = mds_axis1(consensus)

    # ---- prompt-intrinsic (model-free) features ----
    probes = crystal_probes()
    prompts = [p.prompt for p in probes]
    assert len(prompts) == N
    n_words = np.array([len(p.split()) for p in prompts], float)
    def last_char(p):
        s = p.rstrip()
        return s[-1] if s else ""
    ends_punct = np.array([1.0 if last_char(p) in PUNCT else 0.0 for p in prompts])
    ends_space = np.array([1.0 if (p and p[-1].isspace()) else 0.0 for p in prompts])
    has_lambda = np.array([1.0 if ("\u03bb" in p or "\\" in p) else 0.0
                           for p in prompts])
    def last_word_fn(p):
        ws = p.split()
        if not ws:
            return 0.0
        core = "".join(ch for ch in ws[-1].lower() if ch.isalnum())
        return 1.0 if core in STOP else 0.0
    last_word_fn_v = np.array([last_word_fn(p) for p in prompts])
    prompt_feats = {"n_words": n_words, "ends_punct": ends_punct,
                    "ends_space": ends_space, "has_lambda": has_lambda,
                    "last_word_fn": last_word_fn_v}

    # ---- per-model feature dict, then consensus (z-scored mean) ----
    def zscore(v):
        v = np.asarray(v, float)
        return (v - v.mean()) / (v.std() + 1e-12)

    # per-model rich + baseline-function features
    per_model_feat = {n: {} for n in names}
    for n in names:
        zf = models[n]["zf"]; F = zf["features"].astype(np.float64)
        for f in fnames:
            per_model_feat[n][f] = F[:, fidx[f]]
        per_model_feat[n]["log_n90"] = np.log1p(per_model_feat[n]["n90"])
        # s211 baseline function features from original-npz top-64 indices
        topk = models[n]["z"]["topk"]
        tk = AutoTokenizer.from_pretrained(n)
        uniq = np.unique(topk)
        cls = {int(i): classify_token(tk.decode([int(i)])) for i in uniq}
        t1 = np.zeros(N); kf = np.zeros(N)
        for i in range(N):
            cats = [cls[int(t)] for t in topk[i]]
            t1[i] = 1.0 if cats[0] in ("function", "punct", "space") else 0.0
            kf[i] = np.mean([c in ("function", "punct", "space") for c in cats])
        per_model_feat[n]["top1_function"] = t1
        per_model_feat[n]["topk_function_frac"] = kf

    model_dependent = set(fnames) | {"log_n90", "top1_function",
                                     "topk_function_frac"}

    def consensus_feature(key):
        if key in prompt_feats:                  # model-free
            return zscore(prompt_feats[key])
        return np.mean([zscore(per_model_feat[n][key]) for n in names], axis=0)

    needed = sorted({f for _, fs in BLOCKS for f in fs})
    cf = {k: consensus_feature(k) for k in needed}

    # ---- univariate corr (diagnostic) ----
    print("\n===== univariate corr(axis1, feature) =====")
    uni = {}
    for k in needed:
        r = corr(cax1, cf[k]); uni[k] = r
        print(f"  {k:20s} {r:+.3f}")

    # ---- hierarchical blocks ----
    print("\n===== cumulative R^2 (in-sample / 5-fold CV) =====")
    used = []
    blocks_out = []
    for bname, fs in BLOCKS:
        used = used + fs
        X = np.column_stack([cf[k] for k in used])
        r2 = in_sample_r2(cax1, X)
        cvr2 = cv_r2(cax1, X)
        blocks_out.append({"block": bname, "features_added": fs,
                           "n_features": len(used),
                           "r2_insample": r2, "r2_cv": cvr2})
        print(f"  {bname:20s} (+{len(fs)}, tot {len(used):2d})  "
              f"R2={r2:.3f}  CV-R2={cvr2:.3f}")

    # ---- ablation: single-feature CV-R^2 + leave-ends_punct-out ----
    print("\n===== ablation =====")
    singles = sorted(((cv_r2(cax1, cf[k][:, None]), k) for k in needed),
                     reverse=True)
    print("  top single features by CV-R2:")
    for r2k, k in singles[:6]:
        print(f"    {k:20s} CV-R2={r2k:.3f}")
    drop = [k for k in used if k != "ends_punct"]
    cv_drop = cv_r2(cax1, np.column_stack([cf[k] for k in drop]))
    cv_ep = cv_r2(cax1, cf["ends_punct"][:, None])
    print(f"  ends_punct ALONE          CV-R2={cv_ep:.3f}")
    print(f"  FULL minus ends_punct     CV-R2={cv_drop:.3f}  "
          f"(full {blocks_out[-1]['r2_cv']:.3f})")

    # ---- permutation null on the FULL model CV-R^2 ----
    Xfull = np.column_stack([cf[k] for k in used])
    rng = np.random.default_rng(0)
    B = 200
    null = np.array([cv_r2(rng.permutation(cax1), Xfull) for _ in range(B)])
    full_cv = blocks_out[-1]["r2_cv"]
    p = float((np.sum(null >= full_cv) + 1) / (B + 1))
    print(f"\n  FULL CV-R2 = {full_cv:.3f}  vs permutation null "
          f"{null.mean():+.3f} ± {null.std():.3f} (95th {np.percentile(null,95):+.3f})  p={p:.3f}")

    out = {"n_models": len(names), "families": sorted({family(n) for n in names}),
           "models": names, "n_probes": N,
           "univariate_corr": uni,
           "eta2_note": "axis is NOT combinator identity (eta^2~0.05, s211)",
           "blocks": blocks_out,
           "full": {"cv_r2": full_cv, "null_mean": float(null.mean()),
                    "null_p95": float(np.percentile(null, 95)),
                    "p_value": p, "n_perm": B},
           "ablation": {"single_feature_cv_r2": {k: r for r, k in singles},
                        "ends_punct_alone_cv_r2": cv_ep,
                        "full_minus_ends_punct_cv_r2": cv_drop,
                        "ends_punct_eta2_combinator": 0.044,
                        "ends_punct_frac": 0.279}}
    OUT.write_text(json.dumps(out, indent=2))
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
