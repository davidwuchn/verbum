#!/usr/bin/env python3
# register: semantic
"""Name the universal axis of the combinator manifold.

manifold_axis_topology.py found ONE strongly universal axis (consensus MDS
axis-1 of the next-token-probability RDM; per-model best-axis match |r|=0.95
across 5 families, 0.16B->14B). But it is NOT the combinator operations
(eta^2=0.05), NOT compositional depth (r=-0.01), NOT prompt length (r=-0.02);
its best single correlate was next-token entropy (r=-0.29, modest).

HYPOTHESIS (register: semantic): the universal axis is a GENERIC PREDICTABILITY
/ CONTINUATION-TYPE gradient — does the prompt resolve toward a peaked, generic
continuation (function word / punctuation / high-frequency token) or a diffuse /
content-specific one? Test by regressing axis-1 on:
  - entropy            : H(next-token)               (diffuseness)
  - top1_function      : is argmax token a function word / punct / whitespace?
  - topk_function_frac : fraction of top-64 that are function/punct/space tokens
  - prompt_len         : token count                 (confound)
  - combinator (eta^2) : operation identity          (control)
Univariate corr + a multivariate R^2; if {entropy, function-continuation} carry
most of the axis, the axis is NAMED: generic predictability, not lambda structure.

OFFLINE: reads results/manifold-axis-topology/<model>.npz (axis_coords, entropy,
topk indices, prompt_len, labels) + each model's AutoTokenizer (no weights).

Usage: uv run python scripts/experiments/axis_probe.py
License: MIT
"""
from __future__ import annotations

import json
import string
from pathlib import Path

import numpy as np
from transformers import AutoTokenizer

_PR = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = _PR / "results" / "manifold-axis-topology"
OUT = RESULTS_DIR / "axis_probe.json"

# English function words (closed-class): the part of a continuation that is
# grammatical glue rather than content.
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
PUNCT = set(string.punctuation) | {"“", "”", "‘", "’", "—", "–", "…", "·"}


def family(m):
    m = m.lower()
    for k in ("pythia", "qwen", "mistral", "smollm", "olmo"):
        if k in m:
            return k
    return m


def classify_token(s: str) -> str:
    """function | content | punct | space — from the decoded token string."""
    raw = s
    t = s.strip().lower()
    if raw.strip() == "":
        return "space"
    if all((ch in PUNCT or ch.isspace()) for ch in t) and t != "":
        return "punct"
    # strip a leading subword marker space; keep alnum core
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


def multi_r2(y, X):
    """OLS R^2 of y ~ [1, X] (X columns z-scored)."""
    y = np.asarray(y, float)
    Xz = []
    for col in X:
        c = np.asarray(col, float)
        c = (c - c.mean()) / (c.std() + 1e-12)
        Xz.append(c)
    A = np.column_stack([np.ones_like(y)] + Xz)
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ beta
    ss_res = ((y - pred) ** 2).sum()
    ss_tot = ((y - y.mean()) ** 2).sum() + 1e-30
    return float(1 - ss_res / ss_tot), beta[1:].tolist()


def eta2(coord, lab):
    lab = np.asarray(lab)
    grand = coord.mean()
    ss_tot = ((coord - grand) ** 2).sum() + 1e-30
    ss_b = sum(len(coord[lab == u]) * (coord[lab == u].mean() - grand) ** 2
               for u in set(lab))
    return float(ss_b / ss_tot)


def features_for_model(model, z, tok):
    labels = list(z["labels"])
    topk = z["topk"]                       # [N x 64] token ids
    ent = z["entropy"].astype(np.float64)
    plen = z["prompt_len"].astype(np.float64)
    n, k = topk.shape
    # decode unique ids once
    uniq = np.unique(topk)
    cls = {int(i): classify_token(tok.decode([int(i)])) for i in uniq}
    top1_function = np.zeros(n)
    topk_function_frac = np.zeros(n)
    for i in range(n):
        cats = [cls[int(t)] for t in topk[i]]
        top1_function[i] = 1.0 if cats[0] in ("function", "punct", "space") else 0.0
        topk_function_frac[i] = np.mean([c in ("function", "punct", "space")
                                         for c in cats])
    return {"labels": labels, "entropy": ent, "prompt_len": plen,
            "top1_function": top1_function,
            "topk_function_frac": topk_function_frac}


def main():
    files = [f for f in sorted(RESULTS_DIR.glob("*.json"))
             if f.stem not in ("summary", "axis_probe")]
    models = {}
    for jf in files:
        meta = json.loads(jf.read_text())
        npz = RESULTS_DIR / f"{jf.stem}.npz"
        if not npz.exists():
            continue
        models[meta["model"]] = np.load(npz, allow_pickle=True)
    if not models:
        print("no per-model npz found")
        return
    names = list(models.keys())
    print(f"loaded {len(names)} models: {', '.join(family(n) for n in names)}")

    # consensus axis-1 from mean prob RDM
    consensus = np.mean([models[n]["rdm_prob_full"].astype(np.float64)
                         for n in names], axis=0)
    cax1 = mds_axis1(consensus)

    # per-model features; build consensus (z-scored, averaged) features
    feats = {n: features_for_model(n, models[n], AutoTokenizer.from_pretrained(n))
             for n in names}
    labels = feats[names[0]]["labels"]

    def consensus_feature(key):
        vals = []
        for n in names:
            v = feats[n][key].astype(np.float64)
            vals.append((v - v.mean()) / (v.std() + 1e-12))
        return np.mean(vals, axis=0)

    cf = {k: consensus_feature(k) for k in
          ("entropy", "top1_function", "topk_function_frac", "prompt_len")}

    print("\n===== CONSENSUS AXIS-1 — what explains it? =====")
    rows = {}
    for k, v in cf.items():
        r = corr(cax1, v)
        rows[k] = r
        print(f"  corr(axis1, {k:18s}) = {r:+.3f}")
    print(f"  eta^2(combinator identity)      = {eta2(cax1, labels):.3f}  (control)")
    r2_pred, beta = multi_r2(cax1, [cf["entropy"], cf["top1_function"],
                                    cf["topk_function_frac"]])
    print(f"  multivariate R^2 [entropy + top1_function + topk_function_frac] "
          f"= {r2_pred:.3f}")
    r2_full, _ = multi_r2(cax1, [cf["entropy"], cf["top1_function"],
                                 cf["topk_function_frac"], cf["prompt_len"]])
    print(f"  + prompt_len -> R^2 = {r2_full:.3f}")

    print("\n===== PER-MODEL (each model's own axis-1 vs its own features) =====")
    print(f"{'model':24s} {'ent':>6s} {'t1fn':>6s} {'kfn':>6s} {'R2':>6s} {'eta2':>6s}")
    per = {}
    for n in names:
        ax = models[n]["axis_coords"][:, 0].astype(np.float64)
        f = feats[n]
        r2, _ = multi_r2(ax, [f["entropy"], f["top1_function"],
                              f["topk_function_frac"]])
        per[n] = {"entropy": corr(ax, f["entropy"]),
                  "top1_function": corr(ax, f["top1_function"]),
                  "topk_function_frac": corr(ax, f["topk_function_frac"]),
                  "r2": r2, "eta2_combinator": eta2(ax, f["labels"])}
        print(f"{n[:24]:24s} {per[n]['entropy']:+6.2f} {per[n]['top1_function']:+6.2f} "
              f"{per[n]['topk_function_frac']:+6.2f} {r2:6.2f} "
              f"{per[n]['eta2_combinator']:6.2f}")

    out = {"n_models": len(names), "families": sorted({family(n) for n in names}),
           "consensus": {"corr": rows, "eta2_combinator": eta2(cax1, labels),
                         "r2_pred": r2_pred, "r2_with_len": r2_full,
                         "beta_pred": beta},
           "per_model": {family(n): per[n] for n in names}}
    OUT.write_text(json.dumps(out, indent=2))
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
