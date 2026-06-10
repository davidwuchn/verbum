#!/usr/bin/env python3
# register: geometric
"""Subsample CIs on the topology share + the within-Qwen3 scale trend.

AUDIT FOLLOW-UP (session 212, open lead #3 of manifold-axis-and-topology.md):
  "Does the sign/topology share keep climbing past 14B toward 1.0?"

manifold_axis_topology.py measures, per model, how much of the combinator
SEPARATION is carried by sign(h) alone:
    sep_frac_sign = sep_sign / (sep_sign + sep_mag)
    agree_sign_full = corr(upper(RDM_sign), upper(RDM_full))
s211 reported a mixed-family trend 0.33 -> 0.79 (pythia-160m -> Qwen3-14B) and
called it "sharpening with scale". BUT within the clean Qwen3 family it is
already NON-MONOTONE: 0.6B=0.742 -> 4B=0.667 -> 14B=0.793. A single 32B bump
would be over-read without a measurement-noise control.

THIS SCRIPT adds the missing control: a SUBSAMPLE confidence interval on each
quantity, computed offline from the saved RDMs (rdm_hidden_sign / _mag / _full
+ labels in each <model>.npz) -- so it covers ALL existing models with no
model re-run. We use m-out-of-n subsampling WITHOUT replacement (frac=0.8),
NOT a with-replacement bootstrap: resampling probes with replacement injects
duplicate probes -> zero-distance same-label pairs -> deflates the within-class
mean -> spuriously inflates the separation gap. Subsampling distinct probes
keeps every pair a genuine probe-pair.

Verdict logic:
  - per-model CI on sep_frac_sign and agree_sign_full
  - within-Qwen3 series (0.6B,4B,8B,14B,32B): linear slope vs log10(size) +
    Spearman, and whether the 32B CI lies ABOVE the 14B CI (climb), OVERLAPS
    it (plateau), or below (reversal).

Usage: uv run python scripts/experiments/manifold_topology_ci.py
License: MIT
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

_PR = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = _PR / "results" / "manifold-axis-topology"

SIZE = {"pythia-160m": 0.16, "pythia-410m": 0.41, "Qwen3-0.6B": 0.6,
        "SmolLM3-3B": 3, "Qwen3-4B": 4, "Qwen3-8B": 8, "Mistral-7B": 7,
        "OLMo-2-1124-13B": 13, "Qwen3-14B": 14, "Qwen3-32B": 32}

B = 2000
FRAC = 0.8
SEED = 0


def family(m: str) -> str:
    m = m.lower()
    for k in ("pythia", "qwen", "mistral", "smollm", "olmo"):
        if k in m:
            return k
    return m


def size_of(m: str) -> float:
    for k, v in SIZE.items():
        if k.lower() in m.lower():
            return v
    return 0.0


def upper(D):
    iu = np.triu_indices_from(D, k=1)
    return D[iu]


def gap(D, lab):
    """mean(between-class dist) - mean(within-class dist) on off-diagonal pairs."""
    iu = np.triu_indices_from(D, k=1)
    dv = D[iu]
    same = lab[iu[0]] == lab[iu[1]]
    return dv[~same].mean() - dv[same].mean()


def subsample_ci(rdm_sign, rdm_mag, rdm_full, labels, b=B, frac=FRAC, seed=SEED):
    """Subsample distinct probes (m=frac*n, no replacement); recompute
    sep_frac_sign and agree_sign_full each draw. Returns dict of point + CI."""
    n = len(labels)
    m = max(8, int(round(frac * n)))
    rng = np.random.default_rng(seed)
    fr = np.empty(b)
    ag = np.empty(b)
    for t in range(b):
        idx = rng.choice(n, size=m, replace=False)
        idx.sort()
        lab = labels[idx]
        ss = rdm_sign[np.ix_(idx, idx)]
        mm = rdm_mag[np.ix_(idx, idx)]
        ff = rdm_full[np.ix_(idx, idx)]
        gs = gap(ss, lab)
        gm = gap(mm, lab)
        fr[t] = gs / (gs + gm + 1e-30)
        ag[t] = np.corrcoef(upper(ss), upper(ff))[0, 1]
    # point estimate on the full set
    gs0 = gap(rdm_sign, labels)
    gm0 = gap(rdm_mag, labels)
    frac0 = gs0 / (gs0 + gm0 + 1e-30)
    agree0 = float(np.corrcoef(upper(rdm_sign), upper(rdm_full))[0, 1])
    return {
        "sep_frac_sign": float(frac0),
        "sep_frac_sign_ci": [float(np.percentile(fr, 2.5)),
                             float(np.percentile(fr, 97.5))],
        "sep_frac_sign_sd": float(fr.std()),
        "agree_sign_full": agree0,
        "agree_sign_full_ci": [float(np.percentile(ag, 2.5)),
                               float(np.percentile(ag, 97.5))],
        "agree_sign_full_sd": float(ag.std()),
    }


def main():
    models = {}
    for jf in sorted(RESULTS_DIR.glob("*.json")):
        if jf.stem == "summary":
            continue
        npz = RESULTS_DIR / f"{jf.stem}.npz"
        if not npz.exists():
            continue
        meta = json.loads(jf.read_text())
        z = np.load(npz, allow_pickle=True)
        models[meta["model"]] = {
            "labels": np.array([str(x) for x in z["labels"]]),
            "rdm_sign": z["rdm_hidden_sign"].astype(np.float64),
            "rdm_mag": z["rdm_hidden_mag"].astype(np.float64),
            "rdm_full": z["rdm_hidden_full"].astype(np.float64),
        }
    if not models:
        print("no models found")
        return

    rows = []
    print(f"subsample CIs (m={FRAC:.0%} of probes, B={B}, no replacement)\n")
    print(f"{'model':26s} {'B':>5s} {'sgnFrac':>7s} {'ci95':>15s} "
          f"{'agrSgn':>7s} {'ci95':>15s}")
    for name in sorted(models, key=size_of):
        d = models[name]
        ci = subsample_ci(d["rdm_sign"], d["rdm_mag"], d["rdm_full"], d["labels"])
        ci["model"] = name
        ci["size"] = size_of(name)
        ci["family"] = family(name)
        rows.append(ci)
        fc, fci = ci["sep_frac_sign"], ci["sep_frac_sign_ci"]
        ac, aci = ci["agree_sign_full"], ci["agree_sign_full_ci"]
        print(f"{name[:26]:26s} {size_of(name):>5} {fc:7.3f} "
              f"[{fci[0]:.3f},{fci[1]:.3f}] {ac:7.3f} [{aci[0]:.3f},{aci[1]:.3f}]")

    # ---- within-Qwen3 scale trend ----
    qwen = sorted([r for r in rows if r["family"] == "qwen"], key=lambda r: r["size"])
    trend = {}
    if len(qwen) >= 3:
        x = np.log10(np.array([r["size"] for r in qwen]))
        for key in ("sep_frac_sign", "agree_sign_full"):
            y = np.array([r[key] for r in qwen])
            slope = np.polyfit(x, y, 1)[0]
            # Spearman via rank correlation
            xr = np.argsort(np.argsort(x))
            yr = np.argsort(np.argsort(y))
            rho = float(np.corrcoef(xr, yr)[0, 1])
            trend[key] = {"slope_per_decade": float(slope), "spearman": rho,
                          "series": [(r["size"], r[key]) for r in qwen]}
        # 32B vs 14B CI overlap on sep_frac_sign
        big = {r["size"]: r for r in qwen}
        if 32 in big and 14 in big:
            lo32, hi32 = big[32]["sep_frac_sign_ci"]
            lo14, hi14 = big[14]["sep_frac_sign_ci"]
            if lo32 > hi14:
                verdict = "CLIMB (32B CI above 14B CI)"
            elif hi32 < lo14:
                verdict = "REVERSAL (32B CI below 14B CI)"
            else:
                verdict = "PLATEAU/NOISE (32B CI overlaps 14B CI)"
            trend["verdict_32_vs_14"] = verdict

        print("\n===== within-Qwen3 scale trend (clean family series) =====")
        for key in ("sep_frac_sign", "agree_sign_full"):
            t = trend[key]
            ser = " -> ".join(f"{s:g}B:{v:.3f}" for s, v in t["series"])
            print(f"  {key:16s}: {ser}")
            print(f"  {'':16s}  slope/decade={t['slope_per_decade']:+.4f} "
                  f"spearman={t['spearman']:+.2f}")
        if "verdict_32_vs_14" in trend:
            print(f"\n  VERDICT (sep_frac_sign 32B vs 14B): {trend['verdict_32_vs_14']}")
    else:
        print("\n(need >=3 Qwen3 points for a trend; have "
              f"{len(qwen)})")

    out = {"params": {"B": B, "frac": FRAC, "seed": SEED}, "rows": rows,
           "qwen_trend": trend}
    (RESULTS_DIR / "ci.json").write_text(json.dumps(out, indent=2))
    print(f"\nwrote {RESULTS_DIR / 'ci.json'}")


if __name__ == "__main__":
    main()
