#!/usr/bin/env python3
# register: spectral
"""Audit #6 — SVD φ-ratio 0.6299: real structure, or "what spectra look like"?

THE CLAIM (crystal-universality.md §"SVD phi-ratio: 0.6299 ± 0.019",
audit-registry.md #6, load: med — a φ-universality pillar):
  "The SVD spectrum of hidden-state representations follows a GEOMETRIC
   sequence with consecutive ratio ≈ 1/φ (0.618), across 5 architecturally
   distinct families."

REGISTER: spectral. A claim about singular-value spectra. The matched null
for a spectral claim is a random matrix (Marchenko–Pastur) of the SAME shape,
plus a shuffled-entries control — not eyeballing that five numbers cluster
near 0.63.

THE CONFOUND we must rule out (registry #6): "heavy-tailed / power-law spectra
generically have near-constant consecutive ratios; 0.618 may be what power-law
spectra look like." SHARPER STATEMENT (and a finding in itself): a power-law
spectrum s_k ∝ k^(-α) does NOT have a constant consecutive ratio — its ratio
s_{k+1}/s_k = (1+1/k)^(-α) DRIFTS toward 1 in the bulk. A genuinely *constant*
ratio near 0.618 requires a GEOMETRIC (exponential) spectrum s_k ∝ r^k. So the
real discriminators are three, not one:
  (a) Is the model's core consecutive-ratio distinct from a same-shape random
      (MP) matrix and from shuffled entries? (effect size + seed variance)
  (b) Is the core ratio actually CONSTANT (geometric wins over power-law),
      i.e. is the "geometric self-similar" premise that makes φ meaningful true?
  (c) Is the constant 0.618 SPECIFIC — or does the random/shuffled null ALSO
      land near 0.618 (then it is unfalsifiable, failure mode #1)?

OBJECT: per-layer hidden-state representations. For each layer we stack all
eval-text token activations into M=[n_tokens × d_model] and take its singular
values. Computed BOTH centered (PCA / covariance spectrum, removes the trivial
common mode) and raw (the common mode dominates s0). We report both so the
common-mode choice is transparent — it is exactly the kind of knob that
manufactures or hides structure (audit-meta-pattern §fidelity).

NULLS (n_seeds each):
  - mp        : standard-normal Gaussian of the same [n_tokens × d] shape
                (Marchenko–Pastur reference)
  - shuffled  : the real M with all entries permuted (destroys cross-feature
                correlation; preserves the exact value distribution)

METRICS (per layer, per object, per variant):
  - core_mean : mean consecutive ratio s_{k+1}/s_k over a core window
                [n_skip, noise_floor), reported for n_skip ∈ {0,1,2,5}
  - geom_r2   : R² of log s_k vs k         (geometric: constant ratio)
  - power_r2  : R² of log s_k vs log(k+1)   (power-law: drifting ratio)
  - winner    : geometric | powerlaw
  - phi_dist  : |core_mean − 1/φ|
  - geom_r    : the fitted geometric ratio (= exp(slope)); compare to 1/φ

VERDICT inputs (aggregated across layers, written to JSON):
  model vs mp vs shuffled core_mean; geometric-win fraction for each;
  whether mp/shuffled also sit near 1/φ.

Usage:
  uv run python scripts/experiments/svd_phi_null.py --model EleutherAI/pythia-160m-deduped --device mps
  uv run python scripts/experiments/svd_phi_null.py --model mistralai/Mistral-7B-v0.3 --device mps --dtype bfloat16

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "svd-phi-null"

PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1.0 / PHI  # 0.6180339887...

# Longer texts → more tokens → a deeper spectrum (core ranks up to ~128).
EVAL_TEXTS = [
    "The theory of general relativity describes gravity as the curvature of spacetime "
    "caused by mass and energy, and it predicts the bending of light around massive bodies, "
    "the slowing of clocks in strong gravitational fields, and the existence of black holes.",
    "In a large mixing bowl, combine the flour, sugar, and baking powder, then add the eggs "
    "and milk and whisk until the batter is smooth; pour into a greased pan and bake at a "
    "moderate temperature until a toothpick inserted in the center comes out clean.",
    "The committee voted unanimously to approve the new environmental regulations for "
    "manufacturing plants, citing rising pollution levels, public health concerns, and the "
    "long-term economic benefits of cleaner air and water for the surrounding communities.",
    "She walked through the ancient forest, her footsteps muffled by centuries of fallen "
    "leaves, and as the canopy thinned she could see shafts of pale light falling between "
    "the trunks, illuminating drifting motes of dust and the slow circling of distant birds.",
    "The function takes two arguments and returns their composition as a new callable object, "
    "so that applying the result is equivalent to applying the inner function first and then "
    "the outer function to whatever value the inner function happens to produce in the end.",
    "During the Cambrian explosion, roughly five hundred forty-one million years ago, most "
    "major animal phyla appeared in the fossil record over a relatively short geological "
    "interval, a burst of morphological innovation that still puzzles evolutionary biologists.",
    "Photosynthesis converts carbon dioxide and water into glucose and oxygen using sunlight "
    "as the energy source, capturing photons in chlorophyll, splitting water molecules, and "
    "fixing carbon through a cycle of enzyme-catalyzed reactions in the chloroplast stroma.",
    "Machine learning algorithms can be broadly categorized as supervised, unsupervised, or "
    "reinforcement based, and within each family there are dozens of model architectures, "
    "each with characteristic assumptions about the structure of the data and the loss surface.",
    "def compose(f, g):\n    return lambda x: f(g(x))\n\ndef pipeline(*fns):\n    acc = fns[0]\n"
    "    for fn in fns[1:]:\n        acc = compose(fn, acc)\n    return acc\n\nresult = pipeline(square, increment, negate)(5)",
    "Quantum mechanics describes the probabilistic behavior of particles at the atomic and "
    "subatomic scale, where observables do not have definite values until measured and where "
    "entanglement links the outcomes of distant measurements in ways classical intuition denies.",
    "DNA carries genetic information encoded in sequences of four nucleotide bases arranged "
    "along a double helix, and during replication the strands separate so that each serves as "
    "a template for the synthesis of a complementary strand, preserving the code across cells.",
    "The Renaissance began in Italy in the fourteenth century and gradually spread across all "
    "of Europe, reviving classical learning, transforming painting and architecture, and laying "
    "intellectual foundations that would eventually give rise to the scientific revolution.",
]


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT
        ).decode().strip()
    except Exception:
        return "unknown"


@torch.no_grad()
def collect_layer_reprs(model, tokenizer, device, max_length: int):
    """Return list over layers of [n_tokens × d] activation matrices (np.float32).

    Stacks every (non-pad) token's hidden state across all eval texts, per layer.
    Uses hidden_states[1:] (skip the embedding layer-0 input) so index i is the
    output of transformer block i.
    """
    per_layer = None
    for text in EVAL_TEXTS:
        enc = tokenizer(text, return_tensors="pt", truncation=True, max_length=max_length)
        enc = {k: v.to(device) for k, v in enc.items()}
        out = model(**enc, output_hidden_states=True)
        hs = out.hidden_states  # tuple len n_layers+1, each [1, seq, d]
        if per_layer is None:
            per_layer = [[] for _ in range(len(hs) - 1)]
        for li in range(1, len(hs)):
            per_layer[li - 1].append(hs[li][0].float().cpu().numpy())
        del out, hs
    mats = [np.concatenate(chunks, axis=0) for chunks in per_layer]  # [N × d]
    return mats


def singular_values(M: np.ndarray, center: bool) -> np.ndarray:
    X = M.astype(np.float64)
    if center:
        X = X - X.mean(axis=0, keepdims=True)
    # economy SVD; we only need singular values
    s = np.linalg.svd(X, compute_uv=False)
    return s


def core_window(s: np.ndarray, n_skip: int, floor: float = 1e-3, cap: int = 128):
    """Indices [lo, hi) of the core spectrum: skip the top n_skip dominant
    modes, cut at the noise floor (s_k < floor·s_0) and at a rank cap."""
    s0 = s[0] if s[0] > 0 else 1.0
    above = np.where(s > floor * s0)[0]
    hi = int(above[-1]) + 1 if len(above) else len(s)
    hi = min(hi, n_skip + cap, len(s))
    lo = min(n_skip, max(hi - 2, 0))
    return lo, hi


def consecutive_ratio_mean(s: np.ndarray, lo: int, hi: int):
    seg = s[lo:hi]
    if len(seg) < 3:
        return None, None, 0
    r = seg[1:] / (seg[:-1] + 1e-30)
    return float(np.mean(r)), float(np.std(r)), int(len(r))


def fit_geom_vs_power(s: np.ndarray, lo: int, hi: int):
    """Geometric: log s_k = a + b·k (constant ratio e^b). Power-law:
    log s_k = a + c·log(k+1). Return R² of each + fitted geometric ratio."""
    seg = s[lo:hi]
    if len(seg) < 4 or np.any(seg <= 0):
        seg = seg[seg > 0]
        if len(seg) < 4:
            return {"geom_r2": None, "power_r2": None, "geom_r": None,
                    "winner": None, "n": int(len(seg))}
    y = np.log(seg.astype(np.float64))
    k = np.arange(len(seg))
    # geometric
    Ag = np.vstack([k, np.ones_like(k)]).T
    bg, *_ = np.linalg.lstsq(Ag, y, rcond=None)
    pg = Ag @ bg
    ss_tot = ((y - y.mean()) ** 2).sum() + 1e-30
    geom_r2 = float(1 - ((y - pg) ** 2).sum() / ss_tot)
    geom_r = float(np.exp(bg[0]))  # consecutive ratio of the geometric fit
    # power-law
    lk = np.log(k + 1.0)
    Ap = np.vstack([lk, np.ones_like(lk)]).T
    bp, *_ = np.linalg.lstsq(Ap, y, rcond=None)
    pp = Ap @ bp
    power_r2 = float(1 - ((y - pp) ** 2).sum() / ss_tot)
    return {
        "geom_r2": geom_r2, "power_r2": power_r2, "geom_r": geom_r,
        "winner": "geometric" if geom_r2 >= power_r2 else "powerlaw",
        "n": int(len(seg)),
    }


def head_ratio(s: np.ndarray, top_n: int = 5) -> float | None:
    """Session-137 definition EXACTLY: mean of consecutive ratios over the
    TOP `top_n` singular values, i.e. mean(s1/s0, s2/s1, ..., s_{n-1}/s_{n-2}).
    This is the number that produced the 0.6299 table — a 4-ratio average at
    the steep spectral head, NOT the bulk."""
    if len(s) < top_n:
        top_n = len(s)
    if top_n < 2:
        return None
    seg = s[:top_n]
    r = seg[1:] / (seg[:-1] + 1e-30)
    return float(np.mean(r))


def analyze_spectrum(s: np.ndarray, n_skips=(0, 1, 2, 5)) -> dict:
    out = {"n_sv": int(len(s)), "core_mean_by_skip": {}}
    # ── PRIMARY: the session-137 head ratio (mean of top-5 consecutive) ──
    hr = head_ratio(s, top_n=5)
    out["core_mean"] = hr  # 'core_mean' keeps the downstream aggregation key
    out["phi_dist"] = (abs(hr - INV_PHI) if hr is not None else None)
    out["head_ratio_top5"] = hr
    out["head_ratio_top8"] = head_ratio(s, top_n=8)
    out["head_ratio_top3"] = head_ratio(s, top_n=3)
    # geometric-vs-powerlaw SHAPE on the top of the spectrum (top ~20)
    hi_shape = min(20, len(s))
    out.update(fit_geom_vs_power(s, 0, hi_shape))
    out["core_std"] = None
    out["core_n"] = 4
    # ── SECONDARY: bulk window, for contrast (skip top, average the body) ──
    lo, hi = core_window(s, n_skip=2)
    bmean, bstd, bn = consecutive_ratio_mean(s, lo, hi)
    out["bulk_mean"], out["bulk_std"], out["bulk_n"] = bmean, bstd, bn
    out["bulk_lo"], out["bulk_hi"] = lo, hi
    for ns in n_skips:
        lo2, hi2 = core_window(s, n_skip=ns)
        m2, _, _ = consecutive_ratio_mean(s, lo2, hi2)
        out["core_mean_by_skip"][str(ns)] = m2
    return out


def variant_spectrum(M: np.ndarray, variant: str, center: bool, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    if variant == "model":
        return singular_values(M, center)
    if variant == "mp":
        G = rng.standard_normal(size=M.shape)
        return singular_values(G, center)
    if variant == "shuffled":
        flat = M.flatten().copy()
        rng.shuffle(flat)
        return singular_values(flat.reshape(M.shape), center)
    raise ValueError(variant)


def aggregate(layer_records, key_path):
    """Mean over layers of a nested numeric field; skips None."""
    vals = []
    for rec in layer_records:
        v = rec
        for k in key_path:
            v = v.get(k) if isinstance(v, dict) else None
            if v is None:
                break
        if isinstance(v, (int, float)):
            vals.append(v)
    return (float(np.mean(vals)), float(np.std(vals)), len(vals)) if vals else (None, None, 0)


def run(model_id: str, device: str, dtype: str, n_seeds: int, max_length: int):
    t0 = time.time()
    log(f"[load] {model_id} dtype={dtype} device={device}")
    torch_dtype = {"float32": torch.float32, "float16": torch.float16,
                   "bfloat16": torch.bfloat16}[dtype]
    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch_dtype)
    model.to(device).eval()

    log("[collect] forward passes, stacking per-layer token reprs ...")
    mats = collect_layer_reprs(model, tok, device, max_length)
    n_layers = len(mats)
    ntok, d = mats[0].shape
    log(f"[collect] {n_layers} layers, repr matrix {ntok}×{d}")
    del model
    gc.collect()
    if device == "mps":
        torch.mps.empty_cache()

    objects = {"centered": True, "raw": False}
    variants = ["model", "mp", "shuffled"]
    result = {
        "object_results": {},
        "n_layers": n_layers, "n_tokens": int(ntok), "d_model": int(d),
    }

    for obj_name, center in objects.items():
        log(f"[svd] object={obj_name} (center={center})")
        per_variant_layers = {v: [] for v in variants}
        for M in mats:
            for v in variants:
                if v == "model":
                    s = variant_spectrum(M, v, center, seed=0)
                    rec = analyze_spectrum(s)
                    per_variant_layers[v].append(rec)
                else:
                    # average the analysis over seeds
                    seed_recs = [analyze_spectrum(variant_spectrum(M, v, center, seed=si))
                                 for si in range(n_seeds)]
                    # store the per-seed core_mean / winner; aggregate later
                    agg = {
                        "core_mean": float(np.mean([r["core_mean"] for r in seed_recs
                                                    if r["core_mean"] is not None])),
                        "core_mean_seed_std": float(np.std([r["core_mean"] for r in seed_recs
                                                            if r["core_mean"] is not None])),
                        "geom_r2": float(np.mean([r["geom_r2"] for r in seed_recs
                                                  if r["geom_r2"] is not None])),
                        "power_r2": float(np.mean([r["power_r2"] for r in seed_recs
                                                   if r["power_r2"] is not None])),
                        "geom_r": float(np.mean([r["geom_r"] for r in seed_recs
                                                 if r["geom_r"] is not None])),
                        "winner": max(set(r["winner"] for r in seed_recs),
                                      key=[r["winner"] for r in seed_recs].count),
                    }
                    agg["phi_dist"] = abs(agg["core_mean"] - INV_PHI)
                    per_variant_layers[v].append(agg)
        # aggregate across layers
        obj_summary = {}
        for v in variants:
            recs = per_variant_layers[v]
            cm_mean, cm_std, _ = aggregate(recs, ["core_mean"])
            gr2_mean, _, _ = aggregate(recs, ["geom_r2"])
            pr2_mean, _, _ = aggregate(recs, ["power_r2"])
            geomr_mean, _, _ = aggregate(recs, ["geom_r"])
            n_geom_win = sum(1 for r in recs if r.get("winner") == "geometric")
            n_phi = sum(1 for r in recs if r.get("core_mean") is not None
                        and abs(r["core_mean"] - INV_PHI) <= 0.05)
            obj_summary[v] = {
                "core_mean_over_layers": cm_mean,
                "core_mean_std_over_layers": cm_std,
                "geom_r2_mean": gr2_mean,
                "power_r2_mean": pr2_mean,
                "geom_fit_ratio_mean": geomr_mean,
                "geometric_win_layers": n_geom_win,
                "layers_within_0.05_of_phi": n_phi,
                "n_layers": len(recs),
            }
            log(f"  {v:9s} core_mean={cm_mean:.4f}±{cm_std:.4f} "
                f"geom_r2={gr2_mean:.3f} power_r2={pr2_mean:.3f} "
                f"geom_win={n_geom_win}/{len(recs)} phi±.05={n_phi}/{len(recs)}")
        obj_summary["_per_layer"] = {v: per_variant_layers[v] for v in variants}
        result["object_results"][obj_name] = obj_summary

    result["meta"] = {
        "model": model_id,
        "phi_inv_target": INV_PHI,
        "n_seeds": n_seeds,
        "max_length": max_length,
        "dtype": dtype,
        "git_sha": git_sha(),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elapsed_s": round(time.time() - t0, 1),
        "register": "spectral",
        "claim": "consecutive SVD ratio ~ 1/phi geometric, across architectures (audit #6)",
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    safe = model_id.replace("/", "_")
    out_path = RESULTS_DIR / f"{safe}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    log(f"[done] {out_path}  ({result['meta']['elapsed_s']}s)")

    # one-line verdict to stdout
    cen = result["object_results"]["centered"]
    print(json.dumps({
        "model": model_id,
        "centered_model_core_mean": cen["model"]["core_mean_over_layers"],
        "centered_mp_core_mean": cen["mp"]["core_mean_over_layers"],
        "centered_shuffled_core_mean": cen["shuffled"]["core_mean_over_layers"],
        "model_geom_win": f"{cen['model']['geometric_win_layers']}/{cen['model']['n_layers']}",
        "model_layers_near_phi": f"{cen['model']['layers_within_0.05_of_phi']}/{cen['model']['n_layers']}",
        "mp_layers_near_phi": f"{cen['mp']['layers_within_0.05_of_phi']}/{cen['mp']['n_layers']}",
    }, indent=2))
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="float32",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--n-seeds", type=int, default=5)
    ap.add_argument("--max-length", type=int, default=128)
    args = ap.parse_args()
    run(args.model, args.device, args.dtype, args.n_seeds, args.max_length)


if __name__ == "__main__":
    main()
