#!/usr/bin/env python3
"""Does the same ±1 structure carry computation in EVERY model?

Runs the sign-topology measurement across all weight matrices and
reports the per-layer depth profile. The claim: independently trained
models — different architectures, different data, different scales —
converge to the same sign-dominance ratio.

Run on two or more models. Compare the numbers.

Usage:
    pip install torch transformers numpy
    python 02_universal_profile.py                                  # Pythia-160M
    python 02_universal_profile.py --model Qwen/Qwen3-0.6B         # Qwen
    python 02_universal_profile.py --model mistralai/Mistral-7B-v0.3
"""
import argparse
import sys
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM


def measure_sign_fidelity(W, n_samples=20):
    """cos(sign(W) @ x, W @ x) averaged over random inputs."""
    sign_W = torch.sign(W)
    scores = []
    for _ in range(n_samples):
        x = torch.randn(W.shape[1], device=W.device)
        scores.append(F.cosine_similarity(sign_W @ x, W @ x, dim=0).item())
    return sum(scores) / len(scores)


def classify_layer(name):
    """Classify a parameter as attention or FFN."""
    low = name.lower()
    if any(k in low for k in ["q_proj", "k_proj", "v_proj", "o_proj",
                               "query_key_value", "attention.dense",
                               "self_attn"]):
        return "attention"
    if any(k in low for k in ["mlp", "dense_h_to_4h", "dense_4h_to_h",
                               "gate_proj", "up_proj", "down_proj", "ffn"]):
        return "ffn"
    return "other"


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="EleutherAI/pythia-160m-deduped")
    p.add_argument("--device", default="cpu")
    p.add_argument("--samples", type=int, default=20)
    args = p.parse_args()

    print(f"Loading {args.model} ...", file=sys.stderr)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=torch.float32, device_map=args.device)
    model.eval()

    attn_scores, ffn_scores, other_scores = [], [], []

    for name, param in model.named_parameters():
        if param.ndim != 2 or min(param.shape) < 64:
            continue
        W = param.data.float()
        cs = measure_sign_fidelity(W, args.samples)
        kind = classify_layer(name)
        if kind == "attention":
            attn_scores.append(cs)
        elif kind == "ffn":
            ffn_scores.append(cs)
        else:
            other_scores.append(cs)

    all_scores = attn_scores + ffn_scores + other_scores
    attn_mean = np.mean(attn_scores) if attn_scores else 0
    ffn_mean = np.mean(ffn_scores) if ffn_scores else 0
    all_mean = np.mean(all_scores)
    all_std = np.std(all_scores)

    print(f"\n{'='*52}")
    print(f"  Model: {args.model}")
    print(f"  Total weight matrices: {len(all_scores)}")
    print(f"{'='*52}")
    print(f"  Component      Matrices   Mean cos(sign)")
    print(f"  ─────────────  ────────   ──────────────")
    if attn_scores:
        print(f"  Attention      {len(attn_scores):>5}      {attn_mean:.4f}")
    if ffn_scores:
        print(f"  FFN            {len(ffn_scores):>5}      {ffn_mean:.4f}")
    if other_scores:
        print(f"  Other          {len(other_scores):>5}      {np.mean(other_scores):.4f}")
    print(f"  ─────────────  ────────   ──────────────")
    print(f"  ALL            {len(all_scores):>5}      {all_mean:.4f} ± {all_std:.4f}")
    print(f"{'='*52}")
    print(f"\n  Signs carry {all_mean*100:.1f}% of computation.")
    print(f"  FFN matrices:       {ffn_mean*100:.1f}%")
    print(f"  Attention matrices: {attn_mean*100:.1f}%")
    print(f"\n  Run on another model. Compare the numbers.\n")


if __name__ == "__main__":
    main()
