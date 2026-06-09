#!/usr/bin/env python3
"""Audit #8 — rank-1 adjunction (sigma1/sigma2 = 128:1 cross-zone): real map
structure, or marginal/estimator artifact?

The claim (s140, Qwen3-32B; `direct-delta-adjunction.md`,
`explore/categorical-geometry-probes.md`):

    "SVD of cross-zone map L2->L56: sigma1/sigma2 = 128:1 (rank-1 dominated);
     R^2 = 1.000 for ALL zone pairs. The Jacobian of encode->decode has
     constant rank 1 -> the computation lives on a 1D curve in d-space."

The original instrument (`probe_categorical_geometry.py`, probe 2):
  (i)  M = (E^T D)/N on UNCENTERED residual vectors -> SVD -> sigma1/sigma2
  (ii) np.linalg.lstsq(E, D) mean per-dim R^2, with N tokens << d dims

Two suspected STRUCTURAL artifacts, visible from the instrument itself:

  A. R^2 = 1.000 is an underdetermination tautology. lstsq with N < d has
     more unknowns than equations -> exact interpolation -> R^2 = 1.000 for
     ANY data, including pure noise. (control: random Gaussian zones)

  B. sigma1/sigma2 is the carrier mean, not the map. The residual stream has
     a dominant shared mean direction (s185: within-zone lambda1/lambda2 ~
     4000-8800x). The uncentered cross-correlation of two clouds with large
     means is generically rank-1 dominated REGARDLESS of any token-level
     mapping. (controls: row-shuffled pairing, matched-Gaussian, centering)

Tests
-----
  PART A  Reproduce the original instrument at s140-like small N on Qwen3-8B
          zones (also answers `direct-delta-adjunction.md` open question #2).
  PART B  R^2 tautology proof: lstsq R^2 on iid random + matched-marginal
          random data at N < d (8 seeds). If 1.000 -> the R^2 leg is void.
  PART C  sigma1/sigma2 nulls (same instrument, same N):
            - row-shuffled pairing (destroys the map, keeps marginals)
            - matched Gaussian (per-zone mean+cov, independent draws)
            - centered real data (cross-covariance instead of cross-corr)
          If nulls reproduce the ratio and centering collapses it, the
          "128:1" is the carrier, not adjunction structure.
  PART D  Honest map estimate at N > d (dolma prose, train/test split):
          centered ridge fit E->D, SVD of fitted W, held-out R^2 of rank-k
          truncations (k = 1,2,4,...). The honest "is the map rank-1?" curve,
          vs a shuffled-pairing fit (estimator-leak control).

Verdict
-------
  REAL      : real sigma1/sigma2 >> shuffled/matched nulls AND survives
              centering; held-out rank-1 captures ~all predictable variance.
  ARTIFACT  : nulls reproduce the ratio (carrier mean) and/or random data
              gives R^2=1.000 (tautology); held-out curve needs rank >> 1.

Usage:
  uv run python scripts/experiments/adjunction_rank_null.py \
      --model Qwen/Qwen3-8B --device mps
  uv run python scripts/experiments/adjunction_rank_null.py --smoke

License: MIT
"""

# register: spectral  (singular-value structure of the estimated cross-zone
#   linear map — the same quantity the claim is about, measured with the
#   original estimator AND an honest held-out estimator, against marginal-
#   preserving nulls. See AGENTS.md lambda measure; audit-registry step 0.)

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent

DOLMA_DIR = Path("/Users/mwhitford/data/fractal-bitnet/dolma-raw")

# Zone layers. s140 (Qwen3-32B, 64 layers) used ENCODE=L2, COMPRESS=L32,
# DECODE=L56, FINAL=L63. On 64-layer models we use those literal zones;
# otherwise scale proportionally.
ZONES_REF = {"encode": 2, "compress": 32, "decode": 56, "final": 63}


def zones_for(n_layers: int) -> dict:
    if n_layers == 64:
        return dict(ZONES_REF)
    return {z: max(1, int(L / 64 * n_layers)) for z, L in ZONES_REF.items()}

# s140-flavor well-typed sentences (small-N regime)
SMALL_SENTENCES = [
    "The cat chased the mouse across the garden.",
    "A teacher explained the lesson to the students.",
    "The river flows quietly through the old valley.",
    "She placed the heavy book on the wooden table.",
    "The pilot landed the plane during the storm.",
    "A farmer planted seeds in the fertile soil.",
    "The children played games near the tall fence.",
    "He repaired the broken clock with small tools.",
    "The singer performed a song for the audience.",
    "A doctor examined the patient in the clinic.",
    "The dog buried a bone behind the green shed.",
    "The committee approved the plan after debate.",
    "Workers built a bridge over the narrow stream.",
    "The artist painted a portrait of the queen.",
    "A soldier guarded the gate through the night.",
]

ZONE_PAIRS = [("encode", "compress"), ("compress", "decode"),
              ("encode", "decode")]


def log(msg=""):
    print(msg, flush=True)


# ──────────────────────────────────────────────────────────────────────
# Activation capture
# ──────────────────────────────────────────────────────────────────────

@torch.no_grad()
def capture_zone_residuals(model, tokenizer, texts, zone_layers, device,
                           max_len=512, max_tokens=None, skip_first=1):
    """Run texts, return {zone_name: (N, d) float32 array} aligned per token."""
    buf = {z: [] for z in zone_layers}
    n_collected = 0
    for ti, text in enumerate(texts):
        enc = tokenizer(text, return_tensors="pt", truncation=True,
                        max_length=max_len)
        ids = enc["input_ids"].to(device)
        if ids.shape[1] <= skip_first + 1:
            continue
        out = model(input_ids=ids, output_hidden_states=True)
        hs = out.hidden_states  # tuple, len n_layers+1; [0]=embeddings
        for z, L in zone_layers.items():
            v = hs[L][0, skip_first:, :].float().cpu().numpy()
            buf[z].append(v)
        n_collected += ids.shape[1] - skip_first
        del out, hs
        if max_tokens is not None and n_collected >= max_tokens:
            break
    res = {z: np.concatenate(buf[z], axis=0) for z in zone_layers}
    if max_tokens is not None:
        res = {z: a[:max_tokens] for z, a in res.items()}
    return res


def load_dolma_texts(n_docs, min_chars=2000, seed=0):
    """Sample documents from the local dolma parquet shards."""
    import pyarrow.parquet as pq
    files = sorted(DOLMA_DIR.glob("*.parquet"))
    if not files:
        raise FileNotFoundError(f"no parquet under {DOLMA_DIR}")
    rng = np.random.default_rng(seed)
    tbl = pq.read_table(files[0], columns=["text"])
    texts = [t for t in tbl.column("text").to_pylist()
             if t and len(t) >= min_chars]
    idx = rng.permutation(len(texts))[:n_docs]
    return [texts[i] for i in idx]


# ──────────────────────────────────────────────────────────────────────
# The two instruments
# ──────────────────────────────────────────────────────────────────────

def cross_corr_spectrum(A, B, center=False, k=64):
    """SVD spectrum of the s140 estimator M = A^T B / N (optionally centered)."""
    if center:
        A = A - A.mean(axis=0, keepdims=True)
        B = B - B.mean(axis=0, keepdims=True)
    n = A.shape[0]
    M = (A.T @ B) / n
    s = np.linalg.svd(M, compute_uv=False)
    s = s[:k]
    total = float(np.sum(s ** 2)) + 1e-30
    return {
        "sigma1_over_sigma2": float(s[0] / (s[1] + 1e-30)),
        "top1_var": float(s[0] ** 2 / total),
        "top5_var": float(np.sum(s[:5] ** 2) / total),
        "singular_top10": [float(v) for v in s[:10]],
    }


def lstsq_mean_r2(A, B):
    """The s140 R^2 instrument verbatim: lstsq fit, in-sample mean per-dim R^2."""
    W, _, _, _ = np.linalg.lstsq(A, B, rcond=None)
    P = A @ W
    ss_res = np.sum((B - P) ** 2, axis=0)
    ss_tot = np.sum((B - B.mean(axis=0)) ** 2, axis=0)
    return float(np.mean(1.0 - ss_res / (ss_tot + 1e-12)))


def matched_gaussian(X, rng):
    """Gaussian sample with X's mean and covariance (independent of any map)."""
    n, d = X.shape
    mu = X.mean(axis=0)
    Xc = X - mu
    # sample via SVD of the centered data (exact covariance factor, cheap)
    U, s, Vt = np.linalg.svd(Xc, full_matrices=False)
    Z = rng.standard_normal((n, len(s)))
    return mu + (Z * (s / np.sqrt(max(n - 1, 1)))) @ Vt


def carrier_stats(X):
    """Diagnostic: how dominant is the mean (carrier) vs centered variance?"""
    mu = X.mean(axis=0)
    Xc = X - mu
    sc = np.linalg.svd(Xc, compute_uv=False)
    su = np.linalg.svd(X, compute_uv=False)
    return {
        "mean_norm": float(np.linalg.norm(mu)),
        "centered_sigma1": float(sc[0]),
        "uncentered_sigma1_over_sigma2": float(su[0] / (su[1] + 1e-30)),
        "mean_energy_share": float(
            X.shape[0] * np.linalg.norm(mu) ** 2
            / (np.linalg.norm(X) ** 2 + 1e-30)),
    }


# ──────────────────────────────────────────────────────────────────────
# Part D — honest held-out rank-k map
# ──────────────────────────────────────────────────────────────────────

def ridge_fit(A, B, lam):
    """Centered ridge: returns (W, mu_A, mu_B) with B ~ mu_B + (A-mu_A) W."""
    mu_a, mu_b = A.mean(axis=0), B.mean(axis=0)
    Ac, Bc = A - mu_a, B - mu_b
    d = A.shape[1]
    G = Ac.T @ Ac + lam * np.eye(d)
    W = np.linalg.solve(G, Ac.T @ Bc)
    return W, mu_a, mu_b


def heldout_r2(A_te, B_te, W, mu_a, mu_b):
    P = mu_b + (A_te - mu_a) @ W
    ss_res = float(np.sum((B_te - P) ** 2))
    ss_tot = float(np.sum((B_te - B_te.mean(axis=0)) ** 2))
    return 1.0 - ss_res / (ss_tot + 1e-12)


def rank_k_curve(A_tr, B_tr, A_te, B_te, lam, ks):
    """Held-out R^2 of rank-k truncations of the ridge map."""
    W, mu_a, mu_b = ridge_fit(A_tr, B_tr, lam)
    U, s, Vt = np.linalg.svd(W, full_matrices=False)
    curve = {}
    for k in ks:
        Wk = (U[:, :k] * s[:k]) @ Vt[:k, :]
        curve[int(k)] = heldout_r2(A_te, B_te, Wk, mu_a, mu_b)
    curve["full"] = heldout_r2(A_te, B_te, W, mu_a, mu_b)
    spec = {
        "sigma1_over_sigma2": float(s[0] / (s[1] + 1e-30)),
        "top1_var": float(s[0] ** 2 / (np.sum(s ** 2) + 1e-30)),
        "participation_ratio": float(
            (np.sum(s ** 2) ** 2) / (np.sum(s ** 4) + 1e-30)),
        "singular_top10": [float(v) for v in s[:10]],
    }
    return curve, spec


def pick_lambda(A_tr, B_tr, A_va, B_va, grid):
    best, best_r2 = None, -np.inf
    for lam in grid:
        W, mu_a, mu_b = ridge_fit(A_tr, B_tr, lam)
        r2 = heldout_r2(A_va, B_va, W, mu_a, mu_b)
        if r2 > best_r2:
            best, best_r2 = lam, r2
    return best, best_r2


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="mps")
    p.add_argument("--seeds", type=int, default=8)
    p.add_argument("--big-tokens", type=int, default=12288,
                   help="prose tokens for the honest fit (train+val+test)")
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args()

    if args.smoke:
        args.seeds = 2
        args.big_tokens = 2048

    t0 = time.time()
    log("=" * 72)
    log("AUDIT #8 — rank-1 adjunction vs marginal/estimator nulls")
    log("register: spectral")
    log(f"model={args.model} device={args.device} seeds={args.seeds} "
        f"big_tokens={args.big_tokens} smoke={args.smoke}")
    log("=" * 72)

    dtype = (torch.float16 if any(s in args.model for s in ["8B", "14B", "32B"])
             else torch.float32)
    log(f"loading {args.model} ({dtype}) ...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=dtype, device_map=args.device,
        attn_implementation="eager")
    model.eval()
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    n_layers = model.config.num_hidden_layers
    zones = zones_for(n_layers)
    log(f"n_layers={n_layers} zones={zones}")

    results = {
        "audit": 8, "register": "spectral",
        "model": args.model, "zones": zones,
        "seeds": args.seeds, "big_tokens": args.big_tokens,
        "smoke": args.smoke,
    }
    rng_master = np.random.default_rng(0)

    # ── PART A: small-N repro of the original instrument ─────────────
    log("\nPART A — original instrument, small N (s140 regime)")
    small = capture_zone_residuals(model, tokenizer, SMALL_SENTENCES,
                                   zones, args.device)
    n_small, d = small["encode"].shape
    log(f"  small-N tokens: {n_small}  d={d}  (N<d: {n_small < d})")
    A_part = {"n_tokens": n_small, "d": d, "pairs": {}, "carrier": {}}
    for z in zones:
        A_part["carrier"][z] = carrier_stats(small[z])
        cs = A_part["carrier"][z]
        log(f"  carrier[{z}]: mean_norm={cs['mean_norm']:.1f} "
            f"mean_energy={cs['mean_energy_share']:.3f} "
            f"unc_s1/s2={cs['uncentered_sigma1_over_sigma2']:.1f}")
    for za, zb in ZONE_PAIRS:
        E, D = small[za], small[zb]
        orig = cross_corr_spectrum(E, D, center=False)
        cent = cross_corr_spectrum(E, D, center=True)
        r2 = lstsq_mean_r2(E, D)
        A_part["pairs"][f"{za}->{zb}"] = {
            "uncentered": orig, "centered": cent, "lstsq_r2": r2}
        log(f"  {za}->{zb}: UNC s1/s2={orig['sigma1_over_sigma2']:.1f} "
            f"top1={orig['top1_var']:.3f} | CEN s1/s2="
            f"{cent['sigma1_over_sigma2']:.2f} top1={cent['top1_var']:.3f} "
            f"| lstsq R2={r2:.4f}")
    results["A_small_repro"] = A_part

    # ── PART B: R^2 tautology proof ──────────────────────────────────
    log("\nPART B — lstsq R^2 on data with NO map (N<d tautology proof)")
    B_part = {"iid_random": [], "matched_marginals": []}
    for s in range(args.seeds):
        rng = np.random.default_rng(1000 + s)
        Er = rng.standard_normal((n_small, d))
        Dr = rng.standard_normal((n_small, d))
        B_part["iid_random"].append(lstsq_mean_r2(Er, Dr))
        Em = matched_gaussian(small["encode"], rng)
        Dm = matched_gaussian(small["decode"], rng)
        B_part["matched_marginals"].append(lstsq_mean_r2(Em, Dm))
    for kname, vals in B_part.items():
        log(f"  {kname}: R2 = {np.mean(vals):.4f} +/- {np.std(vals):.4f}")
    results["B_r2_tautology"] = {
        k: {"mean": float(np.mean(v)), "std": float(np.std(v)),
            "values": [float(x) for x in v]}
        for k, v in B_part.items()}

    # ── PART C: sigma-ratio nulls at small N ─────────────────────────
    log("\nPART C — sigma1/sigma2 nulls (uncentered instrument, small N)")
    C_part = {}
    for za, zb in ZONE_PAIRS:
        E, D = small[za], small[zb]
        real = A_part["pairs"][f"{za}->{zb}"]["uncentered"][
            "sigma1_over_sigma2"]
        shuf, match = [], []
        for s in range(args.seeds):
            rng = np.random.default_rng(2000 + s)
            perm = rng.permutation(D.shape[0])
            shuf.append(cross_corr_spectrum(E, D[perm], center=False)
                        ["sigma1_over_sigma2"])
            Em = matched_gaussian(E, rng)
            Dm = matched_gaussian(D, rng)
            match.append(cross_corr_spectrum(Em, Dm, center=False)
                         ["sigma1_over_sigma2"])
        C_part[f"{za}->{zb}"] = {
            "real": real,
            "shuffled_pairing": {"mean": float(np.mean(shuf)),
                                 "std": float(np.std(shuf)),
                                 "values": [float(x) for x in shuf]},
            "matched_gaussian": {"mean": float(np.mean(match)),
                                 "std": float(np.std(match)),
                                 "values": [float(x) for x in match]},
            "centered_real": A_part["pairs"][f"{za}->{zb}"]["centered"][
                "sigma1_over_sigma2"],
        }
        log(f"  {za}->{zb}: real={real:.1f} | shuffled="
            f"{np.mean(shuf):.1f}+/-{np.std(shuf):.1f} | matched="
            f"{np.mean(match):.1f}+/-{np.std(match):.1f} | centered_real="
            f"{C_part[f'{za}->{zb}']['centered_real']:.2f}")
    results["C_sigma_nulls_smallN"] = C_part

    # ── PART D: honest held-out rank-k map at N>d ───────────────────
    log("\nPART D — honest map (dolma prose, centered ridge, held-out rank-k)")
    docs = load_dolma_texts(n_docs=256, seed=0)
    big = capture_zone_residuals(model, tokenizer, docs, zones, args.device,
                                 max_len=512, max_tokens=args.big_tokens)
    Nb = big["encode"].shape[0]
    log(f"  prose tokens: {Nb} (N>d: {Nb > d})")
    # also repeat the uncentered instrument + nulls at large N
    D_part = {"n_tokens": Nb, "pairs": {}}
    n_tr = int(Nb * 0.6)
    n_va = int(Nb * 0.15)
    idx = rng_master.permutation(Nb)
    tr, va, te = idx[:n_tr], idx[n_tr:n_tr + n_va], idx[n_tr + n_va:]
    ks = [1, 2, 4, 8, 16, 32, 64, 128] if not args.smoke else [1, 2, 8, 32]
    lam_grid = [1e0, 1e1, 1e2, 1e3, 1e4]
    for za, zb in ZONE_PAIRS:
        E, D = big[za], big[zb]
        unc = cross_corr_spectrum(E, D, center=False)
        cen = cross_corr_spectrum(E, D, center=True)
        # shuffled-pairing null at large N (uncentered instrument)
        rngs = np.random.default_rng(3000)
        shuf_ratio = []
        for s in range(args.seeds):
            perm = rngs.permutation(D.shape[0])
            shuf_ratio.append(cross_corr_spectrum(E, D[perm], center=False)
                              ["sigma1_over_sigma2"])
        lam, lam_r2 = pick_lambda(E[tr], D[tr], E[va], D[va], lam_grid)
        curve, spec = rank_k_curve(E[tr], D[tr], E[te], D[te], lam, ks)
        # estimator-leak control: fit to shuffled targets
        perm = np.random.default_rng(4000).permutation(len(tr))
        curve_null, _ = rank_k_curve(E[tr], D[tr][perm], E[te], D[te],
                                     lam, [1, max(ks)])
        D_part["pairs"][f"{za}->{zb}"] = {
            "uncentered_instrument": unc,
            "centered_instrument": cen,
            "shuffled_pairing_ratio": {
                "mean": float(np.mean(shuf_ratio)),
                "std": float(np.std(shuf_ratio))},
            "ridge_lambda": lam, "val_r2": lam_r2,
            "heldout_r2_by_rank": curve,
            "map_spectrum": spec,
            "shuffled_target_fit": curve_null,
        }
        r1 = curve[1]
        rf = curve["full"]
        log(f"  {za}->{zb}: UNC s1/s2={unc['sigma1_over_sigma2']:.1f} "
            f"(shuf {np.mean(shuf_ratio):.1f}) | map s1/s2="
            f"{spec['sigma1_over_sigma2']:.2f} PR="
            f"{spec['participation_ratio']:.1f}")
        log(f"      heldout R2: k=1 {r1:.4f}  full {rf:.4f}  "
            f"ratio {r1 / (rf + 1e-12):.3f} | leak-control full "
            f"{curve_null['full']:.4f}")
    results["D_honest_map"] = D_part

    # ── Save ─────────────────────────────────────────────────────────
    out_dir = _PROJECT_ROOT / "results" / "adjunction-rank-null"
    out_dir.mkdir(parents=True, exist_ok=True)
    tag = args.model.replace("/", "_") + (".smoke" if args.smoke else "")
    out_path = out_dir / f"{tag}.json"
    results["elapsed_s"] = time.time() - t0
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    log(f"\nsaved -> {out_path}  ({results['elapsed_s']:.0f}s)")


if __name__ == "__main__":
    main()
