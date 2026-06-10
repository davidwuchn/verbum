#!/usr/bin/env python3
# register: spectral/semantic
"""5D crystal lattice — is there real dimensional structure, and what dimension?

THE CLAIM (explore/5d-crystal-lattice.md, crystal-universality.md §"5D Lattice",
NOT in audit-registry — untested):
  "All measured crystals (per-depth, per-model, per-domain, per-combinator) are
   facets of ONE ~5-dimensional lattice. The combinators are the vertices.
   Different models discover the same lattice because it is a property of
   language (Montague / lambda calculus), not of any specific model."

REGISTER: spectral + semantic. The claim is about (a) the effective
DIMENSIONALITY of a representational manifold and (b) the cross-model AGREEMENT
of that manifold. Two register hazards, per audit-meta-pattern.md:
  - "5D" is a CRISP COUNT on a graded spectrum (the "9 FFN modes" failure mode):
    an integer chosen by where you threshold variance / pick an MDS elbow. The
    honest instrument reports a CONTINUOUS effective dimensionality
    (participation ratio) + the eigenspectrum shape, and lets the data say
    1D/2D/3D — never an elbow.
  - "all piles agree at 0.9" is the RDM-CORRELATION TRIVIALITY (the s202
    consensus-r=0.99 failure): RDMs of near-isotropic high-dim clouds correlate
    by default. The matched controls are a label-permutation null + common-mode
    removal across models.

USER STEER (this session): "semantic structure in the probabilities is what we
suspect." So the PRIMARY instrument is the model's NEXT-TOKEN PROBABILITY
distribution (output/meaning space), with last-layer hidden state as the
geometric comparison.

OBJECT: the 535 combinator-labeled crystal probes (verbum.probes.library,
9 operations K I B C D W Y S WHNF, >=50 each). For each probe, at the LAST
token of the raw prompt (NO chat template — we want the LM's continuation):
  - prob vector  = softmax(next-token logits)          -> SEMANTIC representation
  - hidden vector = last-layer hidden state             -> GEOMETRIC representation

REPRESENTATIONAL DISSIMILARITY MATRICES (N x N, vocab/width-agnostic so
cross-model comparable):
  - prob-RDM   : Hellinger distance  H(p,q) = ||sqrt(p) - sqrt(q)|| / sqrt(2)
                 (a proper bounded metric on distributions; = Euclidean on
                  sqrt-probs, so one cdist)
  - hidden-RDM : cosine distance  1 - cos(h_i, h_j)

ANALYSES (per model, per RDM):
  A. Effective dimensionality (CONTINUOUS, with null).
     Classical MDS: B = -1/2 J D^2 J (double-centered squared-distance Gram).
     Keep positive eigenvalues l_k. Report:
       - pr        = (sum l)^2 / sum l^2     (participation ratio = eff. dim)
       - var top-1,2,3,5                      (cumulative variance fractions)
       - spectrum  = top-12 normalized eigenvalues (the shape; reveals 1D/2D/3D)
     Computed for (i) the FULL 535-probe cloud and (ii) the 9 COMBINATOR
     CENTROIDS (<=8D by construction; THIS is the "vertex lattice").
     NULL: shuffled-label centroids (random 9-way grouping of the same probes),
     n_perm draws -> null PR distribution. Real structure => real PR << null PR.
  B. Combinator separation (the s202 SURVIVOR test).
     gap = mean(inter-combinator dist) - mean(intra-combinator dist). Label
     permutation null (n_perm) -> p-value. Confirms the operations are real
     groupings, not imposed.

OUTPUT: results/manifold-dimensionality/<model>.npz (the two RDMs + labels)
        results/manifold-dimensionality/<model>.json (metrics + provenance).
Cross-model agreement (raw / common-mode-removed / shuffled-probe null,
same-family vs cross-family, prob vs hidden) is done by the companion
manifold_dimensionality_summary.py over the saved RDMs.

Usage:
  uv run python scripts/experiments/manifold_dimensionality_null.py \
      --model Qwen/Qwen3-0.6B --device mps --dtype bfloat16
  uv run python scripts/experiments/manifold_dimensionality_null.py \
      --model EleutherAI/pythia-160m --device mps --limit 90   # smoke

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
RESULTS_DIR = _PROJECT_ROOT / "results" / "manifold-dimensionality"


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT
        ).decode().strip()
    except Exception:
        return "unknown"


# ----------------------------------------------------------------------------
# Representation capture
# ----------------------------------------------------------------------------
@torch.no_grad()
def collect_representations(model, tokenizer, device, prompts, max_length: int):
    """Return (probs [N x V] float32, hiddens [N x d] float32).

    For each prompt: forward the RAW text (no chat template), take the LAST
    token's next-token softmax and the last-layer hidden state.
    """
    n = len(prompts)
    probs = None
    hiddens = None
    for i, text in enumerate(prompts):
        enc = tokenizer(text, return_tensors="pt", truncation=True,
                        max_length=max_length)
        enc = {k: v.to(device) for k, v in enc.items()}
        out = model(**enc, output_hidden_states=True)
        logits = out.logits[0, -1].float()                 # [V]
        p = torch.softmax(logits, dim=-1).cpu().numpy().astype(np.float32)
        h = out.hidden_states[-1][0, -1].float().cpu().numpy().astype(np.float32)
        if probs is None:
            probs = np.empty((n, p.shape[0]), dtype=np.float32)
            hiddens = np.empty((n, h.shape[0]), dtype=np.float32)
        probs[i] = p
        hiddens[i] = h
        del out, logits
        if (i + 1) % 50 == 0:
            log(f"    {i + 1}/{n} probes")
    return probs, hiddens


# ----------------------------------------------------------------------------
# RDMs
# ----------------------------------------------------------------------------
def hellinger_rdm(probs: np.ndarray) -> np.ndarray:
    """Hellinger distance matrix on probability rows. = Euclidean on sqrt(p)/sqrt2."""
    sq = np.sqrt(np.clip(probs, 0, None)).astype(np.float64)
    # ||a-b||^2 = |a|^2 + |b|^2 - 2 a.b ; rows of sqrt(p) have |a|^2 = sum p = 1
    g = sq @ sq.T
    nrm = np.einsum("ij,ij->i", sq, sq)
    d2 = nrm[:, None] + nrm[None, :] - 2.0 * g
    d2 = np.clip(d2, 0, None)
    d = np.sqrt(d2) / np.sqrt(2.0)
    np.fill_diagonal(d, 0.0)
    return d


def cosine_rdm(hiddens: np.ndarray) -> np.ndarray:
    X = hiddens.astype(np.float64)
    nrm = np.linalg.norm(X, axis=1, keepdims=True) + 1e-30
    Xn = X / nrm
    cos = np.clip(Xn @ Xn.T, -1.0, 1.0)
    d = 1.0 - cos
    np.fill_diagonal(d, 0.0)
    return d


# ----------------------------------------------------------------------------
# Effective dimensionality (classical MDS spectrum + participation ratio)
# ----------------------------------------------------------------------------
def mds_eigenspectrum(D: np.ndarray) -> np.ndarray:
    """Positive eigenvalues (descending) of the double-centered Gram of D^2."""
    n = D.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    B = (B + B.T) / 2.0
    w = np.linalg.eigvalsh(B)
    w = np.sort(w)[::-1]
    w = w[w > 1e-12]
    return w


def participation_ratio(w: np.ndarray) -> float:
    if len(w) == 0:
        return 0.0
    return float((w.sum() ** 2) / (np.sum(w ** 2) + 1e-30))


def spectrum_summary(D: np.ndarray, top: int = 12) -> dict:
    w = mds_eigenspectrum(D)
    pr = participation_ratio(w)
    tot = w.sum() + 1e-30
    frac = (w / tot)
    cum = np.cumsum(frac)
    def at(k):
        return float(cum[k - 1]) if len(cum) >= k else float(cum[-1]) if len(cum) else 0.0
    return {
        "pr": pr,
        "n_pos_eig": int(len(w)),
        "var_top1": at(1), "var_top2": at(2), "var_top3": at(3), "var_top5": at(5),
        "spectrum": [float(x) for x in frac[:top]],
    }


def centroids(reps: np.ndarray, labels: list[str]) -> tuple[np.ndarray, list[str]]:
    uniq = sorted(set(labels))
    C = np.stack([reps[[i for i, l in enumerate(labels) if l == u]].mean(0)
                  for u in uniq])
    return C, uniq


def centroid_pr_from_rdm(D: np.ndarray, labels: list[str]) -> dict:
    """PR of the combinator-centroid configuration, derived from the probe RDM.

    Centroid squared-distance in the MDS-embedding equals the mean of the
    pairwise D^2 between groups minus within-group terms; simplest faithful
    route: embed probes via classical MDS, average per label, recompute PR.
    """
    n = D.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    B = (B + B.T) / 2.0
    w, V = np.linalg.eigh(B)
    idx = np.argsort(w)[::-1]
    w = w[idx]; V = V[:, idx]
    pos = w > 1e-12
    Y = V[:, pos] * np.sqrt(w[pos])           # MDS coords [n x r]
    C, uniq = centroids(Y, labels)            # [g x r]
    # PR of centroid cloud = participation ratio of its covariance eigenvalues
    Cc = C - C.mean(0, keepdims=True)
    cov = Cc @ Cc.T / max(len(uniq) - 1, 1)
    ev = np.linalg.eigvalsh(cov)
    ev = np.sort(ev)[::-1]; ev = ev[ev > 1e-12]
    return {"pr": participation_ratio(ev), "n_groups": len(uniq),
            "spectrum": [float(x) for x in (ev / (ev.sum() + 1e-30))[:8]]}


# ----------------------------------------------------------------------------
# Combinator separation + null
# ----------------------------------------------------------------------------
def separation_gap(D: np.ndarray, labels: np.ndarray) -> float:
    iu = np.triu_indices_from(D, k=1)
    same = labels[iu[0]] == labels[iu[1]]
    dv = D[iu]
    intra = dv[same].mean()
    inter = dv[~same].mean()
    return float(inter - intra)


def separation_permnull(D: np.ndarray, labels: list[str], n_perm: int, seed: int):
    lab = np.array(labels)
    obs = separation_gap(D, lab)
    rng = np.random.default_rng(seed)
    null = np.empty(n_perm)
    for b in range(n_perm):
        null[b] = separation_gap(D, rng.permutation(lab))
    p = float((np.sum(null >= obs) + 1) / (n_perm + 1))
    return {"gap": obs, "null_mean": float(null.mean()),
            "null_std": float(null.std()), "p_value": p}


def centroid_pr_null(D: np.ndarray, labels: list[str], n_perm: int, seed: int):
    """Null PR of centroid cloud under random regrouping (same group sizes)."""
    lab = np.array(labels)
    rng = np.random.default_rng(seed + 1)
    obs = centroid_pr_from_rdm(D, labels)["pr"]
    null = np.empty(n_perm)
    for b in range(n_perm):
        null[b] = centroid_pr_from_rdm(D, list(rng.permutation(lab)))["pr"]
    # real structure => observed PR LOWER than null (centroids concentrate)
    p_low = float((np.sum(null <= obs) + 1) / (n_perm + 1))
    return {"centroid_pr": obs, "null_mean": float(null.mean()),
            "null_std": float(null.std()), "p_value_concentrated": p_low}


# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="float32",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--max-length", type=int, default=64)
    ap.add_argument("--limit", type=int, default=0,
                    help="cap probes (smoke test); 0 = all 535")
    ap.add_argument("--n-perm", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    safe = args.model.replace("/", "_")
    t0 = time.time()

    probes = crystal_probes()
    if args.limit and args.limit < len(probes):
        # keep balanced across combinators when subsampling
        rng = np.random.default_rng(args.seed)
        by = {}
        for p in probes:
            by.setdefault(p.combinator, []).append(p)
        per = max(2, args.limit // len(by))
        sub = []
        for k in sorted(by):
            idx = rng.permutation(len(by[k]))[:per]
            sub.extend(by[k][i] for i in idx)
        probes = sub
    prompts = [p.prompt for p in probes]
    labels = [p.combinator for p in probes]
    log(f"[{args.model}] {len(prompts)} probes, {len(set(labels))} combinators")

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[args.dtype]
    log(f"  loading model ({args.dtype}) ...")
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)
    model.to(args.device).eval()

    log("  forward passes ...")
    probs, hiddens = collect_representations(model, tok, args.device, prompts,
                                             args.max_length)
    vocab = int(probs.shape[1]); width = int(hiddens.shape[1])
    del model
    gc.collect()
    if args.device == "mps":
        torch.mps.empty_cache()

    log("  building RDMs ...")
    rdm_prob = hellinger_rdm(probs)
    rdm_hidden = cosine_rdm(hiddens)

    out = {
        "model": args.model, "device": args.device, "dtype": args.dtype,
        "n_probes": len(prompts), "n_combinators": len(set(labels)),
        "vocab": vocab, "hidden_width": width,
        "max_length": args.max_length, "n_perm": args.n_perm, "seed": args.seed,
        "git_sha": git_sha(), "elapsed_s": None,
        "results": {},
    }

    for name, D in (("prob", rdm_prob), ("hidden", rdm_hidden)):
        log(f"  analyzing {name}-RDM ...")
        block = {
            "full_cloud": spectrum_summary(D),
            "centroids": centroid_pr_from_rdm(D, labels),
            "centroid_null": centroid_pr_null(D, labels, args.n_perm, args.seed),
            "separation": separation_permnull(D, labels, args.n_perm, args.seed),
        }
        out["results"][name] = block
        c = block["full_cloud"]; cen = block["centroids"]
        cn = block["centroid_null"]; sep = block["separation"]
        log(f"    {name}: full PR={c['pr']:.2f} (var top3={c['var_top3']:.2f}) | "
            f"centroid PR={cen['pr']:.2f} vs null {cn['null_mean']:.2f}"
            f"+-{cn['null_std']:.2f} (p_conc={cn['p_value_concentrated']:.4f}) | "
            f"sep gap={sep['gap']:.4f} p={sep['p_value']:.4f}")

    out["elapsed_s"] = round(time.time() - t0, 1)

    np.savez_compressed(RESULTS_DIR / f"{safe}.npz",
                        rdm_prob=rdm_prob.astype(np.float32),
                        rdm_hidden=rdm_hidden.astype(np.float32),
                        labels=np.array(labels))
    (RESULTS_DIR / f"{safe}.json").write_text(json.dumps(out, indent=2))
    log(f"  wrote {safe}.json + .npz  ({out['elapsed_s']}s)")


if __name__ == "__main__":
    main()
