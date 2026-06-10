#!/usr/bin/env python3
# register: spectral/semantic
"""Cross-model verdict: the common axis + the topology fraction.

Consumes results/manifold-axis-topology/<model>.{json,npz}.

PART A — IS THERE ONE UNIVERSAL AXIS, AND WHAT DOES IT ENCODE?
  - Build the CONSENSUS prob RDM (mean across models; same probe order) and its
    MDS axis-1 = the candidate universal axis.
  - For each model, take whichever of its 3 MDS axes best matches consensus
    axis-1 (sign-aligned |corr|). High & consistent => one universal axis.
  - Characterize consensus axis-1: combinator eta^2, compositional-depth corr
    (W<I<K<C<B<WHNF<Y<D), next-token entropy corr, prompt-length corr.

PART B — HOW MUCH OF THE MANIFOLD IS TOPOLOGY (sign/routing) vs VALUE (magnitude)?
  - Aggregate per-model: separation fraction carried by sign(h) alone, and
    RDM-reconstruction agreement of sign-only / magnitude-only vs full hidden;
    semantic support(top-64 routing) vs full value RDM. Report scale trend.

Usage: uv run python scripts/experiments/manifold_axis_topology_summary.py
License: MIT
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

_PR = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = _PR / "results" / "manifold-axis-topology"
DEPTH = {"W": 0.90, "I": 1.00, "K": 1.02, "C": 1.05, "B": 1.05,
         "WHNF": 1.09, "Y": 1.14, "D": 1.19}

# rough param size for scale ordering
SIZE = {"pythia-160m": 0.16, "pythia-410m": 0.41, "Qwen3-0.6B": 0.6,
        "SmolLM3-3B": 3, "Qwen3-4B": 4, "Mistral-7B": 7,
        "OLMo-2-1124-13B": 13, "Qwen3-14B": 14}


def family(m):
    m = m.lower()
    for k in ("pythia", "qwen", "mistral", "smollm", "olmo"):
        if k in m:
            return k
    return m


def size_of(m):
    for k, v in SIZE.items():
        if k.lower() in m.lower():
            return v
    return 0


def mds_coords(D, k=3):
    n = D.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    B = (B + B.T) / 2
    w, V = np.linalg.eigh(B)
    idx = np.argsort(w)[::-1][:k]
    return V[:, idx] * np.sqrt(np.clip(w[idx], 0, None))


def best_axis_match(coords, ref):
    """max |corr| of any of coords' columns with ref (sign-aligned)."""
    best = 0.0
    for j in range(coords.shape[1]):
        c = coords[:, j]
        if np.std(c) < 1e-12:
            continue
        r = np.corrcoef(c, ref)[0, 1]
        if abs(r) > abs(best):
            best = r
    return best


def safe_corr(a, b, m=None):
    if m is not None:
        a, b = a[m], b[m]
    if np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def main():
    models = {}
    for jf in sorted(RESULTS_DIR.glob("*.json")):
        if jf.stem == "summary":
            continue
        meta = json.loads(jf.read_text())
        npz = RESULTS_DIR / f"{jf.stem}.npz"
        if not npz.exists():
            continue
        z = np.load(npz, allow_pickle=True)
        models[meta["model"]] = {"meta": meta, "z": z}
    if len(models) < 2:
        print(f"need >=2 models; found {len(models)}")
        return
    names = list(models.keys())
    print(f"loaded {len(names)} models: {', '.join(family(n) for n in names)}")

    labels = list(models[names[0]]["z"]["labels"])
    lab = np.array(labels)
    depth = np.array([DEPTH.get(x, np.nan) for x in labels])
    dmask = ~np.isnan(depth)

    # ---- PART A: consensus axis ----
    consensus = np.mean([models[n]["z"]["rdm_prob_full"].astype(np.float64)
                         for n in names], axis=0)
    ccoords = mds_coords(consensus, 3)
    cax1 = ccoords[:, 0]
    # entropy averaged across models (z-scored per model first)
    ents = []
    for n in names:
        e = models[n]["z"]["entropy"].astype(np.float64)
        ents.append((e - e.mean()) / (e.std() + 1e-30))
    ent_mean = np.mean(ents, axis=0)
    plen = models[names[0]]["z"]["prompt_len"].astype(np.float64)

    print("\n===== PART A: THE COMMON AXIS =====")
    print("consensus axis-1 encodes:")
    print(f"  eta^2(combinator identity) = {_eta(cax1, lab):.3f}")
    print(f"  corr(compositional depth)  = {safe_corr(cax1, depth, dmask):+.3f}")
    print(f"  corr(next-token entropy)   = {safe_corr(cax1, ent_mean):+.3f}")
    print(f"  corr(prompt length)        = {safe_corr(cax1, plen):+.3f}")
    print("per-model best-axis match to consensus axis-1 (one universal axis?):")
    matches = []
    for n in names:
        m = best_axis_match(models[n]["z"]["axis_coords"].astype(np.float64), cax1)
        matches.append(abs(m))
        print(f"  {family(n):8s} {size_of(n):>5}B  |r|={abs(m):.3f}")
    print(f"  --- mean |match| = {np.mean(matches):.3f} "
          f"(high+consistent => the axis is universal)")

    # ---- PART B: topology fraction ----
    print("\n===== PART B: TOPOLOGY (sign/routing) vs VALUE (magnitude) =====")
    print(f"{'model':24s} {'B':>5s} {'sgnFrac':>7s} {'agrSgn':>7s} {'agrMag':>7s} "
          f"{'supFrac':>7s} {'sepFull':>8s} {'sepSign':>8s}")
    rows = []
    for n in sorted(names, key=size_of):
        t = models[n]["meta"]["topology"]
        supfrac = t["prob_sep_support"] / (t["prob_sep_support"] + t["prob_sep_full"] + 1e-30)
        print(f"{n[:24]:24s} {size_of(n):>5} {t['sep_frac_sign']:7.2f} "
              f"{t['agree_sign_full']:7.3f} {t['agree_mag_full']:7.3f} "
              f"{supfrac:7.2f} {t['sep_full']:8.4f} {t['sep_sign']:8.4f}")
        rows.append({"model": n, "size": size_of(n), **t, "support_frac": supfrac})

    sign_fracs = [r["sep_frac_sign"] for r in rows]
    agr_sign = [r["agree_sign_full"] for r in rows]
    print(f"\n  mean separation fraction in SIGN (topology) = {np.mean(sign_fracs):.2f}")
    print(f"  mean RDM agreement sign-only vs full         = {np.mean(agr_sign):.3f}")
    print("  => fraction of the combinator structure that is purely topological")

    out = {
        "n_models": len(names), "families": sorted({family(n) for n in names}),
        "axis": {
            "eta2_combinator": _eta(cax1, lab),
            "corr_depth": safe_corr(cax1, depth, dmask),
            "corr_entropy": safe_corr(cax1, ent_mean),
            "corr_promptlen": safe_corr(cax1, plen),
            "mean_universal_match": float(np.mean(matches)),
            "per_model_match": {family(n): float(abs(best_axis_match(
                models[n]["z"]["axis_coords"].astype(np.float64), cax1)))
                for n in names},
        },
        "topology": rows,
        "topology_summary": {
            "mean_sign_separation_fraction": float(np.mean(sign_fracs)),
            "mean_agree_sign_full": float(np.mean(agr_sign)),
        },
    }
    (RESULTS_DIR / "summary.json").write_text(json.dumps(out, indent=2))
    print(f"\nwrote {RESULTS_DIR / 'summary.json'}")


def _eta(coord, lab):
    grand = coord.mean()
    ss_tot = ((coord - grand) ** 2).sum() + 1e-30
    ss_b = sum(len(coord[lab == u]) * (coord[lab == u].mean() - grand) ** 2
               for u in set(lab))
    return float(ss_b / ss_tot)


if __name__ == "__main__":
    main()
