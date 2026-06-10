#!/usr/bin/env python3
# register: semantic
"""Name the remaining ~70% of the universal combinator axis (rich features).

OPEN LEAD (manifold-axis-and-topology.md §"Open Leads", s211 -> s212):
  The universal consensus axis-1 of the next-token-probability RDM (|r|=0.95
  across 5 families) is a GENERIC PREDICTABILITY / CONTINUATION-TYPE gradient,
  NOT the lambda operations (eta^2=0.05). s211 named only ~30% of it
  (multivariate R^2=0.296 on {entropy, top1_function, topk_function_frac}).
  The s211 npz saved only top-64 token INDICES + entropy -> mass-based features
  were impossible offline. This harness re-runs the forward pass and computes
  the RICH DISTRIBUTIONAL features needed to name the rest.

Per-probe features (register: semantic = properties of the next-token dist):
  entropy            Shannon H(p)                       (diffuseness; s211 had it)
  collision          Renyi-2 entropy -log sum p^2       (peakedness, tail-robust)
  top1_prob          max_i p_i                          (confidence)
  top{5,10,32,64,256}_mass   cumulative mass            (concentration shape)
  n90                # tokens to reach 0.9 mass         (effective support)
  function_mass      prob mass on function/punct/space  (grammatical-glue mass;
  content_mass       prob mass on content tokens         the prob-weighted version
  punct_mass         prob mass on punctuation            of s211's count fraction)
  captured512        mass inside the classified top-512 (coverage diagnostic)
  kl_to_mean         KL(p_i || mean_j p_j)              (distinctiveness from the
                                                         GENERIC average continuation)

Held in RAM: the full [N x V] prob matrix (needed for kl_to_mean + exact masses),
then only the small feature matrix is saved.

Usage:
  uv run python scripts/experiments/axis_naming.py --model Qwen/Qwen3-0.6B \
      --device mps --dtype bfloat16
License: MIT
"""
from __future__ import annotations

import argparse
import gc
import json
import string
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
CLASSIFY_TOPN = 512

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
PUNCT = set(string.punctuation) | {"\u201c", "\u201d", "\u2018", "\u2019",
                                   "\u2014", "\u2013", "\u2026", "\u00b7"}

FEATURE_NAMES = [
    "entropy", "collision", "top1_prob", "top5_mass", "top10_mass",
    "top32_mass", "top64_mass", "top256_mass", "n90", "function_mass",
    "content_mass", "punct_mass", "captured512", "kl_to_mean",
]


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJECT_ROOT).decode().strip()
    except Exception:
        return "unknown"


def classify_token(s: str) -> str:
    t = s.strip().lower()
    if s.strip() == "":
        return "space"
    if all((ch in PUNCT or ch.isspace()) for ch in t) and t != "":
        return "punct"
    core = "".join(ch for ch in t if ch.isalnum())
    if core == "":
        return "punct"
    if core in STOP:
        return "function"
    return "content"


@torch.no_grad()
def collect_probs(model, tokenizer, device, prompts, max_length):
    """Full [N x V] float32 next-token prob matrix + prompt_len[N]."""
    n = len(prompts)
    probs = None
    plen = np.empty(n, np.int32)
    for i, text in enumerate(prompts):
        enc = tokenizer(text, return_tensors="pt", truncation=True,
                        max_length=max_length)
        enc = {k: v.to(device) for k, v in enc.items()}
        out = model(**enc)
        logits = out.logits[0, -1].float()
        p = torch.softmax(logits, dim=-1).cpu().numpy().astype(np.float32)
        if probs is None:
            probs = np.empty((n, p.shape[0]), np.float32)
        probs[i] = p
        plen[i] = int(enc["input_ids"].shape[1])
        del out, logits
        if (i + 1) % 100 == 0:
            log(f"    {i + 1}/{n}")
    return probs, plen


def compute_features(probs, plen, tokenizer):
    """probs [N x V] -> features [N x F] (order = FEATURE_NAMES)."""
    n, V = probs.shape
    P = probs.astype(np.float64)
    Pc = np.clip(P, 1e-30, None)

    entropy = -(P * np.log(Pc)).sum(1)
    collision = -np.log(np.clip((P ** 2).sum(1), 1e-30, None))
    top1 = P.max(1)

    log("    sorting for mass curve + n90 ...")
    S = -np.sort(-P, axis=1)                       # descending
    csum = np.cumsum(S, axis=1)
    def kmass(k):
        return S[:, :k].sum(1)
    top5, top10, top32 = kmass(5), kmass(10), kmass(32)
    top64, top256 = kmass(64), kmass(256)
    n90 = (csum < 0.9).sum(1) + 1                   # tokens to reach 0.9 mass

    log("    classifying top-512 token ids ...")
    topidx = np.argpartition(-P, CLASSIFY_TOPN, axis=1)[:, :CLASSIFY_TOPN]
    uniq = np.unique(topidx)
    cls = {int(t): classify_token(tokenizer.decode([int(t)])) for t in uniq}
    is_fn = np.array([cls[int(t)] in ("function", "space") for t in uniq])
    is_pn = np.array([cls[int(t)] == "punct" for t in uniq])
    is_ct = np.array([cls[int(t)] == "content" for t in uniq])
    id2pos = {int(t): j for j, t in enumerate(uniq)}
    function_mass = np.zeros(n); content_mass = np.zeros(n)
    punct_mass = np.zeros(n); captured = np.zeros(n)
    for i in range(n):
        ids = topidx[i]
        pp = P[i, ids]
        pos = np.array([id2pos[int(t)] for t in ids])
        function_mass[i] = pp[is_fn[pos]].sum()
        punct_mass[i] = pp[is_pn[pos]].sum()
        content_mass[i] = pp[is_ct[pos]].sum()
        captured[i] = pp.sum()

    log("    KL to mean (generic-continuation distinctiveness) ...")
    mean_p = P.mean(0)
    log_mean = np.log(np.clip(mean_p, 1e-30, None))
    kl = (P * (np.log(Pc) - log_mean[None, :])).sum(1)

    feats = np.column_stack([
        entropy, collision, top1, top5, top10, top32, top64, top256,
        n90.astype(np.float64), function_mass, content_mass, punct_mass,
        captured, kl,
    ])
    assert feats.shape[1] == len(FEATURE_NAMES)
    return feats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--max-length", type=int, default=64)
    args = ap.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    safe = args.model.replace("/", "_")
    t0 = time.time()

    probes = crystal_probes()
    prompts = [p.prompt for p in probes]
    labels = [p.combinator for p in probes]
    log(f"[{args.model}] {len(prompts)} probes")

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[args.dtype]
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)
    model.to(args.device).eval()
    log("  forward passes (full dist held in RAM) ...")
    probs, plen = collect_probs(model, tok, args.device, prompts, args.max_length)
    vocab = int(probs.shape[1])
    del model
    gc.collect()
    if args.device == "mps":
        torch.mps.empty_cache()

    log("  computing rich distributional features ...")
    feats = compute_features(probs, plen, tok)
    del probs
    gc.collect()

    out = {"model": args.model, "dtype": args.dtype, "n_probes": len(prompts),
           "vocab": vocab, "feature_names": FEATURE_NAMES, "git_sha": git_sha(),
           "elapsed_s": round(time.time() - t0, 1),
           "feature_means": {k: float(feats[:, j].mean())
                             for j, k in enumerate(FEATURE_NAMES)}}
    np.savez_compressed(RESULTS_DIR / f"{safe}.features.npz",
                        features=feats.astype(np.float32),
                        feature_names=np.array(FEATURE_NAMES),
                        labels=np.array(labels),
                        prompt_len=plen)
    (RESULTS_DIR / f"{safe}.features.json").write_text(json.dumps(out, indent=2))
    log(f"  wrote {safe}.features.npz + .json  ({out['elapsed_s']}s)")


if __name__ == "__main__":
    main()
