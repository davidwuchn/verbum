#!/usr/bin/env python3
# register: spectral/semantic
"""The common axis + the topology of the combinator manifold.

FOLLOW-UP to manifold_dimensionality_null.py, which found: the universal
cross-family structure of the 9 combinator operations is REAL (separation
p=0.0005 everywhere) but ~RANK-1 (CMR collapses cross-family agreement
0.79 -> -0.19) and lives in the PROBABILITIES more than the activations.
Two questions remain:

  PART A — WHAT IS THE COMMON AXIS?  The shared structure is ~1-dimensional.
    What does that single dominant axis encode? Candidates (register: semantic):
      - combinator identity (categorical eta^2)
      - compositional depth = attention-entropy gradient (crystal-validity §4):
            W 0.90 < I 1.00 < K 1.02 < C 1.05 < B 1.05 < WHNF 1.09 < Y 1.14 < D 1.19
      - next-token entropy (how DECIDED the continuation is; fact/I = sharp)
      - prompt length (confound)
    And: is it the SAME axis across all families (sign-aligned axis-1 corr)?

  PART B — HOW MUCH OF THE MANIFOLD IS TOPOLOGY?  (register: geometric)
    topology-gradient-separation.md: GD lays structure as SIGN (routing/
    topology, the dominant share) vs MAGNITUDE (value/calibration). Decompose
    the last-layer hidden state h -> sign(h) | |h| | full, build a cosine RDM
    from each, and measure how much of the combinator structure (separation +
    full-RDM reconstruction) the SIGN carries alone. Past sessions put ~77%+ of
    computation in the topology; this measures it directly on this manifold.
    BONUS (semantic topology): support-RDM = Jaccard on the top-64 next tokens
    ("which tokens get mass" = routing) vs the full Hellinger value-RDM.

This script is PER-MODEL (one invocation each). It saves rich artifacts
(hidden, top-k, entropy, axis coords, RDMs) so the cross-model verdict
(manifold_axis_topology_summary.py) needs no re-run.

Usage:
  uv run python scripts/experiments/manifold_axis_topology.py \
      --model Qwen/Qwen3-0.6B --device mps --dtype bfloat16
License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from verbum.probes.library import crystal_probes

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
RESULTS_DIR = _PROJECT_ROOT / "results" / "manifold-axis-topology"
TOPK = 64

# compositional-depth scalar (crystal-validity-and-fidelity.md §4 attention entropy)
DEPTH = {"W": 0.90, "I": 1.00, "K": 1.02, "C": 1.05, "B": 1.05,
         "WHNF": 1.09, "Y": 1.14, "D": 1.19}  # S omitted (not in the gradient)


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


@torch.no_grad()
def collect(model, tokenizer, device, prompts, max_length):
    """Return hidden [N x d] f32, full probs [N x V] f32, entropy [N],
    topk_idx [N x TOPK], prompt_len [N]."""
    n = len(prompts)
    hidden = probs = None
    ent = np.empty(n, np.float32)
    topk = np.empty((n, TOPK), np.int32)
    plen = np.empty(n, np.int32)
    for i, text in enumerate(prompts):
        enc = tokenizer(text, return_tensors="pt", truncation=True, max_length=max_length)
        enc = {k: v.to(device) for k, v in enc.items()}
        out = model(**enc, output_hidden_states=True)
        logits = out.logits[0, -1].float()
        p = torch.softmax(logits, dim=-1)
        h = out.hidden_states[-1][0, -1].float().cpu().numpy().astype(np.float32)
        pn = p.cpu().numpy().astype(np.float32)
        if hidden is None:
            hidden = np.empty((n, h.shape[0]), np.float32)
            probs = np.empty((n, pn.shape[0]), np.float32)
        hidden[i] = h
        probs[i] = pn
        ent[i] = float(-(p * (p + 1e-30).log()).sum().cpu())
        topk[i] = torch.topk(p, TOPK).indices.cpu().numpy().astype(np.int32)
        plen[i] = int(enc["input_ids"].shape[1])
        del out, logits, p
        if (i + 1) % 50 == 0:
            log(f"    {i + 1}/{n}")
    return hidden, probs, ent, topk, plen


# ---- RDMs -------------------------------------------------------------------
def cosine_rdm(X):
    X = X.astype(np.float64)
    n = np.linalg.norm(X, axis=1, keepdims=True) + 1e-30
    cos = np.clip((X / n) @ (X / n).T, -1, 1)
    d = 1.0 - cos
    np.fill_diagonal(d, 0.0)
    return d


def hellinger_rdm(probs):
    sq = np.sqrt(np.clip(probs, 0, None)).astype(np.float64)
    nrm = np.einsum("ij,ij->i", sq, sq)
    d2 = np.clip(nrm[:, None] + nrm[None, :] - 2.0 * (sq @ sq.T), 0, None)
    d = np.sqrt(d2) / np.sqrt(2.0)
    np.fill_diagonal(d, 0.0)
    return d


def jaccard_rdm(topk):
    n = topk.shape[0]
    sets = [set(topk[i].tolist()) for i in range(n)]
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            inter = len(sets[i] & sets[j])
            union = len(sets[i] | sets[j])
            D[i, j] = D[j, i] = 1.0 - inter / max(union, 1)
    return D


# ---- analysis ---------------------------------------------------------------
def upper(D):
    iu = np.triu_indices_from(D, k=1)
    return D[iu]


def mds_coords(D, k=3):
    n = D.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    B = (B + B.T) / 2
    w, V = np.linalg.eigh(B)
    idx = np.argsort(w)[::-1][:k]
    w = np.clip(w[idx], 0, None)
    return V[:, idx] * np.sqrt(w)            # [n x k]


def separation(D, labels, n_perm, seed):
    lab = np.array(labels)
    iu = np.triu_indices_from(D, k=1)
    dv = D[iu]

    def gap(L):
        same = L[iu[0]] == L[iu[1]]
        return dv[~same].mean() - dv[same].mean()

    obs = gap(lab)
    rng = np.random.default_rng(seed)
    null = np.array([gap(rng.permutation(lab)) for _ in range(n_perm)])
    p = float((np.sum(null >= obs) + 1) / (n_perm + 1))
    return {"gap": float(obs), "null_mean": float(null.mean()), "p_value": p}


def agree(Da, Db):
    return float(np.corrcoef(upper(Da), upper(Db))[0, 1])


def eta_squared(coord, labels):
    """Fraction of axis variance explained by combinator identity."""
    lab = np.array(labels)
    grand = coord.mean()
    ss_tot = ((coord - grand) ** 2).sum() + 1e-30
    ss_between = sum(len(coord[lab == u]) * (coord[lab == u].mean() - grand) ** 2
                     for u in set(lab))
    return float(ss_between / ss_tot)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="float32",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--max-length", type=int, default=64)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--n-perm", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    safe = args.model.replace("/", "_")
    t0 = time.time()

    probes = crystal_probes()
    if args.limit and args.limit < len(probes):
        rng = np.random.default_rng(args.seed)
        by = {}
        for p in probes:
            by.setdefault(p.combinator, []).append(p)
        per = max(2, args.limit // len(by))
        probes = [by[k][i] for k in sorted(by)
                  for i in rng.permutation(len(by[k]))[:per]]
    prompts = [p.prompt for p in probes]
    labels = [p.combinator for p in probes]
    log(f"[{args.model}] {len(prompts)} probes")

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[args.dtype]
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)
    model.to(args.device).eval()
    log("  forward passes ...")
    hidden, probs, ent, topk, plen = collect(model, tok, args.device, prompts,
                                             args.max_length)
    vocab = int(probs.shape[1]); width = int(hidden.shape[1])
    del model
    gc.collect()
    if args.device == "mps":
        torch.mps.empty_cache()

    log("  building RDMs (prob full/support; hidden full/sign/mag) ...")
    rdm = {
        "prob_full": hellinger_rdm(probs),
        "prob_support": jaccard_rdm(topk),
        "hidden_full": cosine_rdm(hidden),
        "hidden_sign": cosine_rdm(np.sign(hidden)),
        "hidden_mag": cosine_rdm(np.abs(hidden)),
    }

    out = {"model": args.model, "dtype": args.dtype, "n_probes": len(prompts),
           "vocab": vocab, "hidden_width": width, "n_perm": args.n_perm,
           "git_sha": git_sha(), "results": {}}

    # separation per RDM
    for name, D in rdm.items():
        out["results"][name] = {"separation": separation(D, labels, args.n_perm, args.seed)}

    # PART A — the common axis (semantic, prob_full)
    coords = mds_coords(rdm["prob_full"], k=3)
    ax1 = coords[:, 0]
    depth_vec = np.array([DEPTH.get(l, np.nan) for l in labels])
    mask = ~np.isnan(depth_vec)
    def safe_corr(a, b, m=None):
        if m is not None:
            a, b = a[m], b[m]
        if np.std(a) < 1e-12 or np.std(b) < 1e-12:
            return float("nan")
        return float(np.corrcoef(a, b)[0, 1])
    out["axis"] = {
        "eta2_combinator": eta_squared(ax1, labels),
        "corr_depth": safe_corr(ax1, depth_vec, mask),
        "corr_entropy": safe_corr(ax1, ent.astype(np.float64)),
        "corr_promptlen": safe_corr(ax1, plen.astype(np.float64)),
        "var_top1": float((coords[:, 0] ** 2).sum() /
                          ((coords ** 2).sum() + 1e-30)),
    }

    # PART B — topology fraction (geometric, hidden)
    full = rdm["hidden_full"]
    sep_full = out["results"]["hidden_full"]["separation"]["gap"]
    sep_sign = out["results"]["hidden_sign"]["separation"]["gap"]
    sep_mag = out["results"]["hidden_mag"]["separation"]["gap"]
    out["topology"] = {
        "sep_full": sep_full, "sep_sign": sep_sign, "sep_mag": sep_mag,
        "sep_frac_sign": float(sep_sign / (sep_sign + sep_mag + 1e-30)),
        "agree_sign_full": agree(rdm["hidden_sign"], full),
        "agree_mag_full": agree(rdm["hidden_mag"], full),
        # semantic parallel: support(topology) vs full value RDM
        "prob_agree_support_full": agree(rdm["prob_support"], rdm["prob_full"]),
        "prob_sep_support": out["results"]["prob_support"]["separation"]["gap"],
        "prob_sep_full": out["results"]["prob_full"]["separation"]["gap"],
    }

    out["elapsed_s"] = round(time.time() - t0, 1)
    log(f"  AXIS: eta2(comb)={out['axis']['eta2_combinator']:.3f} "
        f"depth r={out['axis']['corr_depth']:.3f} ent r={out['axis']['corr_entropy']:.3f} "
        f"plen r={out['axis']['corr_promptlen']:.3f}")
    log(f"  TOPO: sep full={sep_full:.4f} sign={sep_sign:.4f} mag={sep_mag:.4f} "
        f"sign-frac={out['topology']['sep_frac_sign']:.2f} | "
        f"agree sign={out['topology']['agree_sign_full']:.3f} "
        f"mag={out['topology']['agree_mag_full']:.3f}")

    np.savez_compressed(
        RESULTS_DIR / f"{safe}.npz",
        hidden=hidden.astype(np.float16), topk=topk, entropy=ent,
        prompt_len=plen, labels=np.array(labels),
        axis_coords=coords.astype(np.float32),
        **{f"rdm_{k}": v.astype(np.float32) for k, v in rdm.items()})
    (RESULTS_DIR / f"{safe}.json").write_text(json.dumps(out, indent=2))
    log(f"  wrote {safe}.json + .npz  ({out['elapsed_s']}s)")


if __name__ == "__main__":
    main()
