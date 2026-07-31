#!/usr/bin/env python3
"""Anti-block vs Zone-B M16 anti-crystal cross-check (s285, cold-start step c).

The style-corrected WHNF anti-block (step b, style_corrected.json) is a FRESH
2026 measurement: 11 models, expanded 24-state basis, sign-CMR gate, per-op
halt states whnf:X, formal-style projected out. The Zone-B `M16` (hardcoded in
scripts/experiments/crystal_tree.py:52) is an OLD 4-model, 8-node (no S)
consensus cosine matrix with an explicit anti-crystal structure:
    M16 = S(x)J + D(x)F   (Kronecker; S=4/5)
    - crystal block  M16[0:8,0:8]  ~ +   (the KIBC..WHNF crystal)
    - anti block     M16[8:16,8:16] ~ +   (a phi-reflection of the crystal)
    - cross block    M16[0:8,8:16]  ~ -   (type <-> anti-type anti-correlation)
    - eigenvalues pair with ratio phi^(4/5)

This script treats the Kronecker/phi-reflection anti-crystal as a MEASURED
PREDICTION and asks whether the fresh style-corrected anti-block reproduces it,
on the 6 opcodes common to both bases: {K,I,B,C,D,W} (M16 has no S; our whnf
block has no Y/WHNF halt state).

Tests (each permutation-null-gated over the 6 opcode labels, 720 exact perms):
  C1  anti-block cross-arc match :
        corr( our whnf-block off-diag , M16 anti-block off-diag )   > 0
  C2  Kronecker phi-reflection   :
        does our anti-block MIRROR our crystal block, as M16's does?
        corr( our whnf-block , our crystal block ) vs the same in M16
  C3  cross-block anti-correlation :
        our crystal x whnf cross-block sign vs M16 crystal x anti (both < 0)
  (descriptive, lambda-yardstick-flagged) phi^(4/5) eigenvalue pairing of the
  6x6 anti-block, reported with a shuffled-label null -- NOT gated (s251: only
  Qwen3-14B ever beat the phi^(4/5) shuffled-label null; a flexible-basis fit).

Verdict per model + pooled. Reports verbatim; no forced fit.
Output: results/expanded-gram/antiblock_m16_crosscheck.json
No model load. License: MIT.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from itertools import permutations
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[2]
_XG = _ROOT / "results" / "expanded-gram"
_CTREE = _ROOT / "scripts" / "experiments" / "crystal_tree.py"

# opcodes common to M16 (NAMES_8 = K I B C D Y W WHNF, no S) and our whnf
# block (OPS = K I B C S D W, no Y/WHNF):
COMMON = ["K", "I", "B", "C", "D", "W"]
OURS_OPS = ["K", "I", "B", "C", "S", "D", "W"]     # style_corrected block order
PHI = (1 + np.sqrt(5)) / 2


def load_m16() -> tuple[np.ndarray, list[str]]:
    """Extract M16 + NAMES_16 from crystal_tree.py without importing scipy."""
    src = _CTREE.read_text()
    ns: dict = {"np": np}
    for name in ("NAMES_8", "NAMES_16"):
        m = re.search(rf"^{name}\s*=\s*(.+)$", src, re.M)
        exec(f"{name} = {m.group(1)}", ns)
    m = re.search(r"M16\s*=\s*np\.array\((\[.*?\]),\s*dtype=np\.float64\)",
                  src, re.S)
    exec(f"M16 = np.array({m.group(1)}, dtype=np.float64)", ns)
    return ns["M16"], ns["NAMES_16"]


def _off(m: np.ndarray) -> np.ndarray:
    n = m.shape[0]
    return m[np.triu_indices(n, k=1)]


def _perm_p(a_full: np.ndarray, b_full: np.ndarray, obs: float,
            two_sided: bool = False) -> float:
    """Exact permutation p: relabel opcodes on side `a`, recompute off-diag
    correlation, fraction of |perm| >= |obs| (or one-sided perm >= obs)."""
    n = a_full.shape[0]
    hits, total = 0, 0
    for p in permutations(range(n)):
        pa = a_full[np.ix_(p, p)]
        r = np.corrcoef(_off(pa), _off(b_full))[0, 1]
        total += 1
        if two_sided:
            if abs(r) >= abs(obs) - 1e-12:
                hits += 1
        elif r >= obs - 1e-12:
            hits += 1
    return hits / total


def _corr_off(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.corrcoef(_off(a), _off(b))[0, 1])


def phi_eig_pairing(anti6: np.ndarray) -> dict:
    """Descriptive phi^(4/5) eigenvalue-pairing of the 6x6 anti-block, with a
    shuffled-label null (lambda yardstick: reported, NOT gated)."""
    ev = np.sort(np.linalg.eigvalsh(anti6))[::-1]
    ev = ev[ev > 1e-6]
    ratios = [float(ev[k] / ev[k + 1]) for k in range(len(ev) - 1)]
    phi45 = PHI ** (4 / 5)
    obs_err = float(np.mean([abs(r - phi45) / phi45 for r in ratios])) \
        if ratios else float("nan")
    rng = np.random.default_rng(0)
    null = []
    n = anti6.shape[0]
    for _ in range(2000):
        p = rng.permutation(n)
        m = anti6[np.ix_(p, p)]
        e = np.sort(np.linalg.eigvalsh(m))[::-1]
        e = e[e > 1e-6]
        rr = [e[k] / e[k + 1] for k in range(len(e) - 1)]
        null.append(np.mean([abs(r - phi45) / phi45 for r in rr]) if rr
                    else np.nan)
    null = np.array([x for x in null if not np.isnan(x)])
    p_beats = float(np.mean(null <= obs_err)) if len(null) else float("nan")
    return {"phi_45": round(phi45, 4),
            "eig_ratios": [round(r, 4) for r in ratios],
            "mean_rel_err_vs_phi45": round(obs_err, 4),
            "shuffled_null_mean_err": round(float(null.mean()), 4)
            if len(null) else None,
            "p_beats_shuffled_null": round(p_beats, 4)}


def main() -> None:
    M16, N16 = load_m16()
    ai = {name: i for i, name in enumerate(N16)}
    anti_idx = [ai["ā" + o] for o in COMMON]     # anti-type rows
    cry_idx = [ai[o] for o in COMMON]            # crystal rows
    m16_anti = M16[np.ix_(anti_idx, anti_idx)]
    m16_cry = M16[np.ix_(cry_idx, cry_idx)]
    m16_cross = M16[np.ix_(cry_idx, anti_idx)]
    # M16's own anti<->crystal reflection correlation (the reference target)
    m16_refl = _corr_off(m16_anti, m16_cry)

    ours_i = [OURS_OPS.index(o) for o in COMMON]

    slugs = sorted(p.parent.name for p in _XG.glob("*/style_corrected.json"))
    per_model = {}
    for slug in slugs:
        d = json.loads((_XG / slug / "style_corrected.json").read_text())
        cor = d["corrected"]
        whnf = np.array(cor["whnf_block"])[np.ix_(ours_i, ours_i)]
        cry = np.array(cor["crystal_block"])[np.ix_(ours_i, ours_i)]
        cross = np.array(cor["cross_block"])[np.ix_(ours_i, ours_i)]

        # C1: anti-block cross-arc match
        c1 = _corr_off(whnf, m16_anti)
        c1_p = _perm_p(whnf, m16_anti, c1)
        # C2: our own reflection (anti mirrors crystal) + match to M16's
        c2 = _corr_off(whnf, cry)
        c2_p = _perm_p(whnf, cry, c2)
        # C3: cross-block anti-correlation
        c3_mean = float(cross.mean())
        c3_diag = float(np.mean(np.diag(cross)))
        # descriptive phi pairing
        phi = phi_eig_pairing(whnf)

        per_model[slug] = {
            "C1_antiblock_match_r": round(c1, 4), "C1_perm_p": round(c1_p, 4),
            "C2_our_reflection_r": round(c2, 4), "C2_perm_p": round(c2_p, 4),
            "C3_cross_mean": round(c3_mean, 4),
            "C3_cross_diag_mean": round(c3_diag, 4),
            "phi_pairing": phi,
        }

    # pooled
    c1s = np.array([m["C1_antiblock_match_r"] for m in per_model.values()])
    c2s = np.array([m["C2_our_reflection_r"] for m in per_model.values()])
    c3s = np.array([m["C3_cross_mean"] for m in per_model.values()])
    n = len(per_model)
    c1_pos = int((c1s > 0).sum())
    c2_pos = int((c2s > 0).sum())
    c3_neg = int((c3s < 0).sum())
    c1_sig = int(sum(m["C1_perm_p"] < 0.05 for m in per_model.values()))
    c2_sig = int(sum(m["C2_perm_p"] < 0.05 for m in per_model.values()))

    verdict = {
        "n_models": n, "common_ops": COMMON,
        "m16_reference": {
            "anti_block_offdiag_mean": round(float(_off(m16_anti).mean()), 4),
            "crystal_block_offdiag_mean": round(float(_off(m16_cry).mean()), 4),
            "cross_block_mean": round(float(m16_cross.mean()), 4),
            "anti_mirrors_crystal_r": round(m16_refl, 4),
        },
        "C1_antiblock_match": {
            "median_r": round(float(np.median(c1s)), 4),
            "sign_positive": f"{c1_pos}/{n}",
            "perm_p_lt_05": f"{c1_sig}/{n}",
        },
        "C2_kronecker_reflection": {
            "median_r": round(float(np.median(c2s)), 4),
            "sign_positive": f"{c2_pos}/{n}",
            "perm_p_lt_05": f"{c2_sig}/{n}",
            "m16_own_reflection_r": round(m16_refl, 4),
        },
        "C3_cross_anticorrelation": {
            "median_cross_mean": round(float(np.median(c3s)), 4),
            "sign_negative": f"{c3_neg}/{n}",
            "m16_cross_mean": round(float(m16_cross.mean()), 4),
        },
    }
    verdict["VERDICT"] = {
        "C1_supported": c1_pos >= max(1, round(0.8 * n)) and c1_sig >= 1,
        "C2_supported": c2_pos >= max(1, round(0.8 * n)),
        "C3_supported": c3_neg >= max(1, round(0.8 * n)),
        "note": ("C1=fresh anti-block reproduces M16 anti-crystal ordering; "
                 "C2=Kronecker reflection (anti mirrors crystal) present in "
                 "fresh data; C3=type<->anti anti-correlation. phi^(4/5) "
                 "pairing reported descriptively (lambda yardstick, not gated)."),
    }

    out = {"timestamp_utc": datetime.now(UTC).isoformat(),
           "source_m16": str(_CTREE.relative_to(_ROOT)) + ":52 (Zone-B 4-model)",
           "source_ours": "results/expanded-gram/*/style_corrected.json (s285)",
           "verdict": verdict, "per_model": per_model}
    (_XG / "antiblock_m16_crosscheck.json").write_text(json.dumps(out, indent=1))

    # console report
    ref = verdict["m16_reference"]
    print(f"M16 ref: anti_off {ref['anti_block_offdiag_mean']:+.3f} "
          f"cry_off {ref['crystal_block_offdiag_mean']:+.3f} "
          f"cross {ref['cross_block_mean']:+.3f} anti~cry r {m16_refl:+.3f}")
    print(f"{'model':<20} {'C1_r':>7} {'C1_p':>6} {'C2_r':>7} {'C2_p':>6} "
          f"{'C3mean':>7} {'phi_p':>6}")
    for slug, m in per_model.items():
        print(f"{slug:<20} {m['C1_antiblock_match_r']:>7.3f} "
              f"{m['C1_perm_p']:>6.3f} {m['C2_our_reflection_r']:>7.3f} "
              f"{m['C2_perm_p']:>6.3f} {m['C3_cross_mean']:>7.3f} "
              f"{m['phi_pairing']['p_beats_shuffled_null']:>6.3f}")
    v = verdict["VERDICT"]
    c1, c2, c3 = (verdict["C1_antiblock_match"],
                  verdict["C2_kronecker_reflection"],
                  verdict["C3_cross_anticorrelation"])
    print(f"\nC1 anti-block match : median r {c1['median_r']:+.3f} | "
          f"+{c1['sign_positive']} | p<.05 {c1['perm_p_lt_05']} "
          f"=> supported={v['C1_supported']}")
    print(f"C2 kron reflection  : median r {c2['median_r']:+.3f} | "
          f"+{c2['sign_positive']} | p<.05 {c2['perm_p_lt_05']} "
          f"(M16 own {m16_refl:+.3f}) => supported={v['C2_supported']}")
    print(f"C3 cross anti-corr  : median {c3['median_cross_mean']:+.3f} | "
          f"neg {c3['sign_negative']} (M16 {m16_cross.mean():+.3f}) "
          f"=> supported={v['C3_supported']}")
    print(f"\nwrote {_XG / 'antiblock_m16_crosscheck.json'}")


if __name__ == "__main__":
    main()
