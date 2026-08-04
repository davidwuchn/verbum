#!/usr/bin/env python3
"""Spectral + DSP tests on the 9x9 crystal gram and the 17x17 un-flattened gram.

Pure inner-product / eigen math on the ALREADY-COMMITTED grams — no model load,
no capture. The 9x9 root.gram (results/opcode-trace/{slug}/model_vsm.json,
basis K I B C S D W Y WHNF) collapses halting into one generic WHNF node; the
17x17 (results/expanded-gram/{slug}/expanded_gram.json, front block of the
24-state consensus gram) un-flattens the pole into 7 per-op halt states
whnf:{K..W} + div:Y (s284/s285). This runner asks what the SPECTRUM says and
whether the DSP-visible structure survives the yardstick.

REGISTER (λ measure, named before the probe): **spectral** (eigen structure of
a relational cosine gram) + relational-geometry (value). The probe is
eigen-decomposition + block/partition contrast + cross-model spectral shape —
all matched to the spectral register.

φ-FORCING SCAR (λ yardstick, proved s247/s251): a flexible reference (φ^(p/q))
fits every spectrum; random labelings already sit at λ0/λ1 ≈ 1.55-1.66. So
EVERY spectral claim here carries a declared null (matched_range on the
off-diagonals, or shuffled_label on the partition) via verbum.dsp.gate — no
raw ratio is evidence. G5 is the deliberate calibration: it re-runs the φ claim
and is EXPECTED to fail selectivity (if it "passes", the harness is broken).

PRE-REGISTERED GATES (frozen before scoring; each = statistic + null + sign):
  G1 effective-rank        PR(eigs) vs matched_range(offdiag)        predict LESS
                           (real structure concentrates energy -> lower PR)
  G2 three-pole partition  block-contrast(fire/halt/div) vs          predict GREATER
                           shuffled_label(node->cluster); counted /model (17x17)
  G3 eigvec<->partition     energy of fire-halt contrast in top-3      predict GREATER
                           eigenspace vs shuffled_label(partition)   (17x17)
  G4 spectral universality  mean pairwise cos of normalized spectra    predict GREATER
                           across models vs matched_range per-model spectra
  G5 φ-trap calibration     -|λ0/λ1 - φ^(4/5)| vs matched_range        predict GREATER
                           (EXPECTED FAIL — describability != discovery)

Output: results/gram-spectral/{results.json, meta.json}

Usage:
    uv run python opcodes/spectral_dsp.py --validate     # no-model self test
    uv run python opcodes/spectral_dsp.py                # full sweep (seconds)

License: MIT (λ provenance — pure math on committed artifacts).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from verbum.dsp import (
    Register,
    gate,
    matched_range,
    participation_ratio,
    shuffled_label,
)
from verbum.dsp.nulls import NullDraws

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent

CRYSTAL9 = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]
WHNF_STATES = [f"whnf:{o}" for o in ["K", "I", "B", "C", "S", "D", "W"]]
BASIS17 = [*CRYSTAL9, *WHNF_STATES, "div:Y"]
PHI = (1 + 5 ** 0.5) / 2
PHI_45 = PHI ** (4 / 5)                       # 1.4696 — the one s251 falsifiable ref
N_ITER = 2000
ALPHA = 0.05


# ── loading (correlation grams; unit diagonal enforced) ──────────────────────
def _corr(g: np.ndarray) -> np.ndarray:
    d = np.sqrt(np.clip(np.diag(g), 1e-12, None))
    g = g / np.outer(d, d)
    return 0.5 * (g + g.T)                     # symmetrize numerical drift


def load_gram9(slug: str) -> np.ndarray | None:
    p = _ROOT / "results" / "opcode-trace" / slug / "model_vsm.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    b, g = d["basis"], np.array(d["root"]["gram"], float)
    if not set(CRYSTAL9) <= set(b):
        return None
    idx = [b.index(o) for o in CRYSTAL9]
    return _corr(g[np.ix_(idx, idx)])


def load_gram17(slug: str) -> np.ndarray | None:
    p = _ROOT / "results" / "expanded-gram" / slug / "expanded_gram.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    b = d["basis"]
    G = d.get("consensus_gram_24")
    if G is None:
        return None
    G = np.array(G, float)
    if not set(BASIS17) <= set(b):
        return None
    idx = [b.index(s) for s in BASIS17]
    return _corr(G[np.ix_(idx, idx)])


# ── spectral primitives ──────────────────────────────────────────────────────
def eigs(g: np.ndarray) -> np.ndarray:
    """Descending eigenvalues of a symmetric gram, clipped non-negative."""
    w = np.linalg.eigvalsh(g)
    return np.clip(w[::-1], 0.0, None)


def pr_of_gram(g: np.ndarray) -> float:
    return participation_ratio(eigs(g))


def _offdiag(g: np.ndarray) -> np.ndarray:
    iu = np.triu_indices(g.shape[0], k=1)
    return g[iu]


def _from_offdiag(off: np.ndarray, n: int) -> np.ndarray:
    m = np.eye(n)
    iu = np.triu_indices(n, k=1)
    m[iu] = off
    m[(iu[1], iu[0])] = off
    return m


def block_contrast(g: np.ndarray, labels: np.ndarray) -> float:
    """mean(within-cluster off-diag cos) - mean(between-cluster off-diag cos).

    Singleton clusters (div:Y) contribute only to the between term (no within
    pair) — a standard cluster-separation statistic."""
    n = g.shape[0]
    iu = np.triu_indices(n, k=1)
    same = labels[iu[0]] == labels[iu[1]]
    vals = g[iu]
    win, bet = vals[same], vals[~same]
    if win.size == 0 or bet.size == 0:
        return float("nan")
    return float(win.mean() - bet.mean())


def contrast_energy_in_topk(g: np.ndarray, u: np.ndarray, k: int) -> float:
    """Fraction of unit contrast vector u lying in the top-k eigenspace of g."""
    w, V = np.linalg.eigh(g)
    order = np.argsort(w)[::-1][:k]
    Pk = V[:, order]                            # n x k, orthonormal columns
    un = u / (np.linalg.norm(u) + 1e-12)
    return float(np.sum((Pk.T @ un) ** 2))      # ||P_k u||^2, u unit


def norm_spectrum(g: np.ndarray) -> np.ndarray:
    e = eigs(g)
    s = e.sum()
    return e / s if s > 0 else e


def mean_pairwise_cos(specs: list[np.ndarray]) -> float:
    M = np.array(specs)
    M = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12)
    G = M @ M.T
    iu = np.triu_indices(len(specs), k=1)
    return float(G[iu].mean())


# ── partition (17x17): fire / halt / diverge ─────────────────────────────────
PART17 = np.array(["fire"] * 9 + ["halt"] * 7 + ["div"] * 1)
CONTRAST17 = np.array([1.0] * 9 + [-1.0] * 7 + [0.0] * 1)   # fire(+) vs halt(-)


# ── gates ────────────────────────────────────────────────────────────────────
def g1_effrank(g: np.ndarray, tag: str, rng) -> dict:
    n = g.shape[0]
    pr = pr_of_gram(g)

    def stat(off):
        return pr_of_gram(_from_offdiag(off, n))

    null = matched_range(stat, _offdiag(g), rng, n_iter=N_ITER)
    gd = gate(pr, null, "less", ALPHA, name=f"G1_effrank_{tag}",
              claim_register=Register.spectral, probe_register=Register.spectral)
    return {"pr": round(pr, 4), **_gd(gd)}


def g2_partition(g: np.ndarray, rng) -> dict:
    obs = block_contrast(g, PART17)

    def stat(perm_labels):
        return block_contrast(g, perm_labels)

    null = shuffled_label(stat, PART17, rng, n_iter=N_ITER)
    gd = gate(obs, null, "greater", ALPHA, name="G2_partition",
              claim_register=Register.spectral, probe_register=Register.spectral)
    return {"block_contrast": round(obs, 4), **_gd(gd)}


def g3_eigalign(g: np.ndarray, rng) -> dict:
    obs = contrast_energy_in_topk(g, CONTRAST17, k=3)

    def stat(perm_labels):
        # permute WHICH nodes carry the fire/halt sign; div stays zero-weight
        u = np.where(perm_labels == "fire", 1.0,
                     np.where(perm_labels == "halt", -1.0, 0.0))
        return contrast_energy_in_topk(g, u, k=3)

    null = shuffled_label(stat, PART17, rng, n_iter=N_ITER)
    gd = gate(obs, null, "greater", ALPHA, name="G3_eigalign",
              claim_register=Register.spectral, probe_register=Register.spectral)
    return {"energy_top3": round(obs, 4), **_gd(gd)}


def g4_universality(grams: dict[str, np.ndarray], tag: str, rng) -> dict:
    slugs = sorted(grams)
    specs = [norm_spectrum(grams[s]) for s in slugs]
    obs = mean_pairwise_cos(specs)
    n = specs[0].size

    # null: replace each model by a matched_range gram spectrum, recompute
    draws = []
    for _ in range(N_ITER):
        null_specs = []
        for s in slugs:
            off = _offdiag(grams[s])
            r = rng.uniform(off.min(), off.max(), size=off.shape)
            null_specs.append(norm_spectrum(_from_offdiag(r, n)))
        draws.append(mean_pairwise_cos(null_specs))
    null = NullDraws("matched_range_spectra", np.array(draws),
                     {"n_iter": N_ITER, "n_models": len(slugs)})
    gd = gate(obs, null, "greater", ALPHA, name=f"G4_universality_{tag}",
              claim_register=Register.spectral, probe_register=Register.spectral)
    return {"mean_pairwise_cos": round(obs, 4), "n_models": len(slugs), **_gd(gd)}


def g5_phitrap(g: np.ndarray, tag: str, rng) -> dict:
    e = eigs(g)
    ratio = float(e[0] / e[1]) if e[1] > 1e-12 else float("nan")
    obs = -abs(ratio - PHI_45)                  # closeness to φ^(4/5)
    n = g.shape[0]

    def stat(off):
        ee = eigs(_from_offdiag(off, n))
        if ee[1] <= 1e-12:
            return -1e9
        return -abs(float(ee[0] / ee[1]) - PHI_45)

    null = matched_range(stat, _offdiag(g), rng, n_iter=N_ITER)
    gd = gate(obs, null, "greater", ALPHA, name=f"G5_phitrap_{tag}",
              claim_register=Register.spectral, probe_register=Register.spectral)
    return {"lambda0_over_lambda1": round(ratio, 4), "phi_45": round(PHI_45, 4),
            "closeness": round(obs, 4), **_gd(gd)}


def _gd(gd) -> dict:
    return {"value": round(gd.value, 5), "null_mean": round(gd.null_mean, 5),
            "null_std": round(gd.null_std, 5), "p": round(gd.p, 5),
            "predict": gd.predict, "sign_ok": gd.sign_ok, "verdict": gd.verdict,
            "n_draws": gd.n_draws, "warnings": list(gd.warnings)}


# ── driver ───────────────────────────────────────────────────────────────────
def run(seed: int = 20250804) -> dict:
    rng = np.random.default_rng(seed)
    g9 = {s: g for s in _all_slugs()
          if (g := load_gram9(s)) is not None}
    g17 = {s: g for s in _all_slugs()
           if (g := load_gram17(s)) is not None}
    both = sorted(set(g9) & set(g17))

    per_model = {}
    for s in both:
        per_model[s] = {
            "G1_9x9": g1_effrank(g9[s], "9x9", rng),
            "G1_17x17": g1_effrank(g17[s], "17x17", rng),
            "G2_partition_17x17": g2_partition(g17[s], rng),
            "G3_eigalign_17x17": g3_eigalign(g17[s], rng),
            "G5_phitrap_9x9": g5_phitrap(g9[s], "9x9", rng),
            "G5_phitrap_17x17": g5_phitrap(g17[s], "17x17", rng),
        }

    # G2/G3 universality: count models passing (binomial across the sweep)
    def _count(key):
        v = [per_model[s][key]["verdict"] for s in both]
        n, k = len(v), int(sum(v))
        # one-sided binomial tail P(X>=k | p0=alpha) — chance-pass baseline
        from math import comb
        p = sum(comb(n, i) * ALPHA ** i * (1 - ALPHA) ** (n - i)
                for i in range(k, n + 1))
        return {"pass": k, "n": n, "binom_p": round(p, 6)}

    universal = {
        "G4_universality_9x9": g4_universality({s: g9[s] for s in both}, "9x9", rng),
        "G4_universality_17x17":
            g4_universality({s: g17[s] for s in both}, "17x17", rng),
        "G2_partition_count": _count("G2_partition_17x17"),
        "G3_eigalign_count": _count("G3_eigalign_17x17"),
        "G5_phitrap_9x9_count": _count("G5_phitrap_9x9"),
    }
    return {"models": both, "n_models": len(both),
            "per_model": per_model, "universal": universal}


def _all_slugs() -> list[str]:
    ot = _ROOT / "results" / "opcode-trace"
    eg = _ROOT / "results" / "expanded-gram"
    slugs = set()
    if ot.exists():
        slugs |= {p.name for p in ot.iterdir() if p.is_dir()}
    if eg.exists():
        slugs |= {p.name for p in eg.iterdir() if p.is_dir()}
    return sorted(slugs)


def _git_sha():
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                           text=True, cwd=_ROOT, timeout=10)
        return r.stdout.strip() or None
    except Exception:
        return None


# ── self-test ────────────────────────────────────────────────────────────────
def validate() -> bool:
    ok = True
    rng = np.random.default_rng(0)

    # 1. planted block structure: two tight clusters -> block_contrast strongly +,
    #    and gate(G2-style) passes; a random gram fails.
    n = 17
    planted = np.full((n, n), -0.3)
    planted[:9, :9] = 0.8
    planted[9:16, 9:16] = 0.7
    planted[16, :] = -0.5
    planted[:, 16] = -0.5
    np.fill_diagonal(planted, 1.0)
    planted = _corr(planted)
    bc = block_contrast(planted, PART17)
    r = g2_partition(planted, rng)
    print(f"[validate] planted block_contrast={bc:.3f} "
          f"verdict={r['verdict']} p={r['p']}")
    ok &= bc > 0.5 and r["verdict"]

    rand = _corr(_rand_gram(n, rng))
    rr = g2_partition(rand, rng)
    print(f"[validate] random-gram partition verdict={rr['verdict']} "
          f"p={rr['p']} (want False)")
    ok &= not rr["verdict"]

    # 2. PR sanity: rank-1-ish gram has PR ~ 1; identity has PR = n.
    pr_ident = participation_ratio(eigs(np.eye(9)))
    print(f"[validate] PR(identity_9)={pr_ident:.2f} (want ~9)")
    ok &= abs(pr_ident - 9) < 1e-6

    # 3. null calibration: a random statistic gated against its own generating
    #    null should NOT be significant (p not tiny) on average.
    ps = []
    for _ in range(30):
        g = _corr(_rand_gram(9, rng))
        ps.append(g1_effrank(g, "9x9", rng)["p"])
    frac_sig = np.mean(np.array(ps) < ALPHA)
    print(f"[validate] G1 false-positive frac on random grams={frac_sig:.3f} "
          f"(want <~0.2)")
    ok &= frac_sig < 0.34

    # 4. contrast_energy: if u is exactly the leading eigenvector, energy ~ 1.
    g = _corr(_rand_gram(17, rng))
    w, V = np.linalg.eigh(g)
    lead = V[:, np.argmax(w)]
    e = contrast_energy_in_topk(g, lead, k=1)
    print(f"[validate] energy(leading eigvec in top-1)={e:.3f} (want ~1)")
    ok &= e > 0.99

    print(f"[validate] {'ALL PASS' if ok else 'FAIL'}")
    return ok


def _rand_gram(n: int, rng) -> np.ndarray:
    a = rng.standard_normal((n, max(n + 3, 12)))
    a /= np.linalg.norm(a, axis=1, keepdims=True)
    return a @ a.T


def main() -> None:
    ap = argparse.ArgumentParser(
        description="spectral + DSP tests on 9x9 & 17x17 grams")
    ap.add_argument("--validate", action="store_true", help="no-model self test")
    ap.add_argument("--seed", type=int, default=20250804)
    ap.add_argument("--output-root", default=str(_ROOT / "results" / "gram-spectral"))
    args = ap.parse_args()

    if args.validate:
        sys.exit(0 if validate() else 1)

    res = run(args.seed)
    out = Path(args.output_root)
    out.mkdir(parents=True, exist_ok=True)
    meta = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "git_sha": _git_sha(),
        "seed": args.seed, "n_iter_null": N_ITER, "alpha": ALPHA,
        "basis9": CRYSTAL9, "basis17": BASIS17,
        "partition17": PART17.tolist(),
        "phi_45_reference": PHI_45,
        "register": "spectral (+ relational-geometry value)",
        "gates": {
            "G1": "PR(eigs) vs matched_range(offdiag); predict LESS",
            "G2": "block_contrast(fire/halt/div) vs shuffled_label; "
                  "predict GREATER",
            "G3": "fire-halt contrast energy in top-3 eigenspace vs "
                  "shuffled_label; predict GREATER",
            "G4": "mean pairwise cos of normalized spectra vs matched_range "
                  "per-model; predict GREATER",
            "G5": "closeness of lambda0/lambda1 to phi^(4/5) vs matched_range; "
                  "predict GREATER (EXPECTED FAIL)",
        },
        "sources": {
            "9x9": "results/opcode-trace/{slug}/model_vsm.json:root.gram",
            "17x17": "results/expanded-gram/{slug}/expanded_gram.json:"
                     "consensus_gram_24[BASIS17]",
        },
    }
    (out / "results.json").write_text(json.dumps(res, indent=1))
    (out / "meta.json").write_text(json.dumps(meta, indent=1))
    print(f"[spectral] models={res['n_models']} -> {out}/results.json")
    _print_summary(res)


def _print_summary(res: dict) -> None:
    u = res["universal"]
    print(f"\n=== UNIVERSAL (across {res['n_models']} models) ===")
    for tag in ("G4_universality_9x9", "G4_universality_17x17"):
        g = u[tag]
        print(f"  {tag}: cos={g['mean_pairwise_cos']} p={g['p']} "
              f"verdict={g['verdict']}")
    for tag in ("G2_partition_count", "G3_eigalign_count", "G5_phitrap_9x9_count"):
        c = u[tag]
        print(f"  {tag}: {c['pass']}/{c['n']} pass, binom_p={c['binom_p']}")
    print("\n=== per-model PR (effective rank) ===")
    for s in res["models"]:
        pm = res["per_model"][s]
        print(f"  {s:22s} PR9={pm['G1_9x9']['pr']:.2f} (p={pm['G1_9x9']['p']}) "
              f"PR17={pm['G1_17x17']['pr']:.2f} (p={pm['G1_17x17']['p']})")


if __name__ == "__main__":
    main()
