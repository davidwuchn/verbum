"""Permutation null for the ORIGINAL crystal-φ pipeline.

Wraps verify_crystal_phi.py's exact measurement (gate_proj activations,
Zone B layers, sequence-mean-pooled, PCA→per-combinator cosine matrix,
φ^(p/q) eigenvalue fit, correlation to the hardcoded CONSENSUS_8x8) and
asks the decisive question:

    Does the TRUE combinator labeling produce its φ-structure and its
    consensus agreement BETTER than random regroupings of the SAME prose?

Three null tests, all on the same extracted activations (PCA basis is
label-independent, so permutation only re-averages per label — fast):

  A. φ^(p/q) fit error      — if random labels fit φ as well, the φ claim
                              is unfalsifiable (dense p/q grid fits anything).
  B. CONSENSUS_8x8 corr     — if random labels correlate with the consensus
                              as well as the true labels, cross-model
                              "agreement" is an artifact of the fixed target.
  C. cluster separation     — within-vs-between cosine; does the grouping
                              carve coherent clusters at all.

Verdict per metric: p = fraction of 2000 random labelings at least as
extreme as the true labeling.

Usage:
    uv run python scripts/experiments/crystal_phi_permnull.py \
        --models Qwen/Qwen3-8B EleutherAI/pythia-410m-deduped Qwen/Qwen3-0.6B \
        --n-perm 2000

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

# Reuse the ORIGINAL pipeline's exact components
from verify_crystal_phi import (  # noqa: E402
    CONSENSUS_8x8,
    CRYSTAL_COMBINATORS,
    PHI,
    _CONSENSUS_ORDER,
    extract_gate_activations,
    get_zone_b_layers,
    select_probes,
)

RESULTS_DIR = _PROJECT_ROOT / "results" / "crystal-phi-permnull"


def log(m):
    print(m, file=sys.stderr, flush=True)


# ──────────────────────────────────────────────────────────────────────
# Metrics — identical math to verify_crystal_phi, reduced to scalars
# ──────────────────────────────────────────────────────────────────────

def _normed_projection(centered, pcs, labels, combinators):
    vecs = []
    for c in combinators:
        idx = [i for i, l in enumerate(labels) if l == c]
        v = pcs @ centered[idx].mean(0) if idx else np.zeros(pcs.shape[0])
        vecs.append(v)
    V = np.array(vecs)
    n = np.linalg.norm(V, axis=1, keepdims=True)
    n[n == 0] = 1
    return V / n


def crystal_cosine(centered, pcs, labels, combinators):
    Vn = _normed_projection(centered, pcs, labels, combinators)
    return Vn @ Vn.T


def phi_fit_error(eigvals):
    """Mean relative error of best φ^(p/q) fit per eigenvalue (orig grid)."""
    C = eigvals[0]
    if C <= 0:
        return float("nan")
    errs = []
    for ev in eigvals:
        if ev <= 0.001:
            continue
        best = float("inf")
        for d in range(1, 13):
            for nn in range(-8 * d, 1):
                pred = C * PHI ** (nn / d)
                best = min(best, abs(pred - ev) / ev)
        errs.append(best)
    return float(np.mean(errs)) if errs else float("nan")


PHI_4_5 = PHI ** (4 / 5)  # 1.4696 — the pre-registered primary ratio target


def lambda01(eigvals):
    """Primary eigenvalue ratio λ0/λ1 (the φ^(4/5) prediction)."""
    e = np.sort(np.abs(eigvals))[::-1]
    if len(e) < 2 or e[1] < 1e-9:
        return float("nan")
    return float(e[0] / e[1])


def eig_ratio_corr(eigvals, combinators):
    """Correlation of sorted normalized eigenvalue ratios to CONSENSUS_8x8.

    This is the 'eigenvalue_ratio_correlation' the original reported as ~0.99.
    Sorted normalized spectra of PSD matrices are near-monotone, so this is
    expected to be trivially high even for random labels — the null tests that.
    """
    ci = [k for k, c in enumerate(_CONSENSUS_ORDER) if c in combinators]
    if len(ci) < 4:
        return float("nan")
    cons = CONSENSUS_8x8[np.ix_(ci, ci)]
    ev_c = np.sort(np.linalg.eigvalsh(cons))[::-1]
    ev_m = np.sort(np.abs(eigvals))[::-1][:len(ev_c)]
    if ev_c[0] <= 0 or ev_m[0] <= 0:
        return float("nan")
    return float(np.corrcoef(ev_m / ev_m[0], ev_c / ev_c[0])[0, 1])


def consensus_corr(cosine, combinators):
    """Correlation of measured submatrix to hardcoded CONSENSUS_8x8."""
    ci, mi, names = [], [], []
    for k, cname in enumerate(_CONSENSUS_ORDER):
        if cname in combinators:
            ci.append(k)
            mi.append(combinators.index(cname))
            names.append(cname)
    if len(names) < 4:
        return float("nan")
    meas = cosine[np.ix_(mi, mi)]
    cons = CONSENSUS_8x8[np.ix_(ci, ci)]
    iu = np.triu_indices_from(meas, k=1)
    return float(np.corrcoef(meas[iu], cons[iu])[0, 1])


def separation(centered, pcs, labels, combinators):
    P = centered @ pcs.T
    P = P / np.maximum(np.linalg.norm(P, axis=1, keepdims=True), 1e-9)
    C = P @ P.T
    lab = np.array(labels)
    idx = np.where(np.isin(lab, combinators))[0]
    same, diff = [], []
    for a, i in enumerate(idx):
        for j in idx[a + 1:]:
            (same if lab[i] == lab[j] else diff).append(C[i, j])
    return float(np.mean(same) - np.mean(diff))


def pval_low(t, null):
    null = np.array(null)
    return float((np.sum(null <= t) + 1) / (len(null) + 1))


def pval_high(t, null):
    null = np.array(null)
    return float((np.sum(null >= t) + 1) / (len(null) + 1))


# ──────────────────────────────────────────────────────────────────────
# Per-model
# ──────────────────────────────────────────────────────────────────────

def run_model(model_id, n_perm, device, n_layers_sample, n_per, seed):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    combinators = list(CRYSTAL_COMBINATORS)
    probe_dict = select_probes(combinators, n_per)

    log(f"  Loading {model_id} ...")
    tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_id, dtype=torch.float16,
        device_map=device if device != "mps" else None,
        trust_remote_code=True)
    if device == "mps":
        model = model.to(device)
    model.eval()
    nL = model.config.num_hidden_layers
    layers = get_zone_b_layers(nL, n_layers_sample)
    log(f"  {nL} layers, Zone B = {layers}")

    # ── extract gate activations once (labeled), exactly as original ──
    acts, labels = [], []
    for c in combinators:
        prompts = probe_dict.get(c, [])
        if not prompts:
            continue
        a = extract_gate_activations(model, tok, prompts, layers, device)
        acts.append(a)
        labels.extend([c] * len(a))
    acts = np.concatenate(acts, 0)
    del model, tok
    if device == "mps" and torch.backends.mps.is_available():
        torch.mps.empty_cache()

    centered = acts - acts.mean(0)
    # PCA once (label-independent) — n_pcs = 2*n_combs, as original
    _, _, Vt = np.linalg.svd(centered, full_matrices=False)
    n_pcs = min(2 * len(combinators), Vt.shape[0])
    pcs = Vt[:n_pcs]

    # ── TRUE metrics ──
    cos_true = crystal_cosine(centered, pcs, labels, combinators)
    eig_true = np.sort(np.linalg.eigvalsh(cos_true))[::-1]
    phi_true = phi_fit_error(eig_true)
    cons_true = consensus_corr(cos_true, combinators)
    sep_true = separation(centered, pcs, labels, combinators)
    lam01_true = lambda01(eig_true)
    eigratio_true = eig_ratio_corr(eig_true, combinators)
    dist45_true = abs(lam01_true - PHI_4_5)
    log(f"  TRUE: phi_fit={phi_true:.4f}  consensus_r={cons_true:+.4f}  sep={sep_true:+.4f}")
    log(f"        λ0/λ1={lam01_true:.4f} (φ^(4/5)={PHI_4_5:.4f}, dist={dist45_true:.4f})  "
        f"eig_ratio_corr={eigratio_true:+.4f}")

    # ── permutation null ──
    rng = np.random.default_rng(seed)
    lab = np.array(labels, dtype=object)
    phi_null, cons_null, sep_null = [], [], []
    lam01_null, dist45_null, eigratio_null = [], [], []
    t0 = time.time()
    for k in range(n_perm):
        perm = lab.copy()
        rng.shuffle(perm)
        pl = perm.tolist()
        cm = crystal_cosine(centered, pcs, pl, combinators)
        ev = np.sort(np.linalg.eigvalsh(cm))[::-1]
        phi_null.append(phi_fit_error(ev))
        cons_null.append(consensus_corr(cm, combinators))
        sep_null.append(separation(centered, pcs, pl, combinators))
        l01 = lambda01(ev)
        lam01_null.append(l01)
        dist45_null.append(abs(l01 - PHI_4_5))
        eigratio_null.append(eig_ratio_corr(ev, combinators))
        if (k + 1) % 500 == 0:
            log(f"    perm {k+1}/{n_perm} ({(time.time()-t0):.0f}s)")

    res = {
        "model": model_id,
        "n_perm": n_perm,
        "zone_b_layers": layers,
        "n_probes": int(acts.shape[0]),
        "n_pcs": int(n_pcs),
        "true": {"phi_fit": phi_true, "consensus_r": cons_true, "separation": sep_true,
                 "lambda01": lam01_true, "dist_phi45": dist45_true,
                 "eig_ratio_corr": eigratio_true, "eigenvalues": eig_true.tolist()},
        "phi_4_5_target": PHI_4_5,
        "null_phi_fit": {"mean": float(np.mean(phi_null)), "std": float(np.std(phi_null)),
                         "min": float(np.min(phi_null))},
        "null_consensus_r": {"mean": float(np.mean(cons_null)), "std": float(np.std(cons_null)),
                             "max": float(np.max(cons_null))},
        "null_separation": {"mean": float(np.mean(sep_null)), "std": float(np.std(sep_null))},
        "null_lambda01": {"mean": float(np.nanmean(lam01_null)), "std": float(np.nanstd(lam01_null)),
                          "median": float(np.nanmedian(lam01_null))},
        "null_eig_ratio_corr": {"mean": float(np.nanmean(eigratio_null)),
                                "std": float(np.nanstd(eigratio_null)),
                                "max": float(np.nanmax(eigratio_null))},
        # φ-fit LOW is "good" (fits φ); consensus & separation HIGH is "good"
        "p_phi_fit": pval_low(phi_true, phi_null),
        "p_consensus_r": pval_high(cons_true, cons_null),
        "p_separation": pval_high(sep_true, sep_null),
        # FALSIFIABLE φ tests: is true λ0/λ1 specially CLOSE to φ^(4/5)?
        "p_dist_phi45": pval_low(dist45_true, [d for d in dist45_null if not np.isnan(d)]),
        # is eigenvalue-ratio-corr an outlier, or trivially high for all labels?
        "p_eig_ratio_corr": pval_high(eigratio_true, [e for e in eigratio_null if not np.isnan(e)]),
    }
    log(f"  NULL phi_fit={res['null_phi_fit']['mean']:.4f}±{res['null_phi_fit']['std']:.4f} "
        f"(min {res['null_phi_fit']['min']:.4f})  →  p_phi={res['p_phi_fit']:.4f}")
    log(f"  NULL consensus_r={res['null_consensus_r']['mean']:+.4f}±{res['null_consensus_r']['std']:.4f} "
        f"(max {res['null_consensus_r']['max']:+.4f})  →  p_cons={res['p_consensus_r']:.4f}")
    log(f"  NULL separation={res['null_separation']['mean']:+.4f}±{res['null_separation']['std']:.4f} "
        f"→  p_sep={res['p_separation']:.4f}")
    log(f"  NULL λ0/λ1={res['null_lambda01']['mean']:.3f}±{res['null_lambda01']['std']:.3f} "
        f"(median {res['null_lambda01']['median']:.3f})  →  p(dist→φ^4/5)={res['p_dist_phi45']:.4f}")
    log(f"  NULL eig_ratio_corr={res['null_eig_ratio_corr']['mean']:+.4f}±{res['null_eig_ratio_corr']['std']:.4f} "
        f"(max {res['null_eig_ratio_corr']['max']:+.4f})  →  p_eigratio={res['p_eig_ratio_corr']:.4f}")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=["Qwen/Qwen3-0.6B"])
    ap.add_argument("--device", default="mps")
    ap.add_argument("--n-perm", type=int, default=2000)
    ap.add_argument("--n-layers", type=int, default=4)
    ap.add_argument("--n-per-combinator", type=int, default=None)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    for mid in args.models:
        log("═" * 64)
        log(f"  CRYSTAL-φ PERMUTATION NULL — {mid}")
        log("═" * 64)
        res = run_model(mid, args.n_perm, args.device, args.n_layers,
                        args.n_per_combinator, args.seed)
        slug = mid.replace("/", "_")
        with open(RESULTS_DIR / f"{slug}.json", "w") as f:
            json.dump(res, f, indent=2)
        log(f"  saved → {RESULTS_DIR / f'{slug}.json'}")
    log("\nDONE.")


if __name__ == "__main__":
    main()
