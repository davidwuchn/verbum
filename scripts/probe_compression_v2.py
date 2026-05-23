#!/usr/bin/env python3
"""Probe v2: Look for the universal compressor in flat-attention models.

V1 used effective rank ratio — not the right lens. The compressor
might manifest as:

1. Per-layer RESIDUAL ratio: how much of the input survives vs how much
   the layer adds. ||residual|| / ||input|| — the layer's compression
   of the SIGNAL, not the rank.

2. Information gain per layer: KL(output || input) — how much each
   layer changes the distribution.

3. Cumulative compression: track how the signal compresses from
   embedding to final layer. Look for self-similar scaling.

4. Per-head attention entropy: how concentrated is each head's
   attention? Concentrated = compressed. Diffuse = raw.

5. FFN gate sparsity: what fraction of FFN neurons fire per layer?
   This IS compression — the FFN is selecting which features matter.

The key insight: in stride-stack, we measured compression ACROSS STRIDES
(different scales). In flat models, the analog might be compression
ACROSS LAYERS (different depths) or ACROSS HEADS (different functions).

Usage:
    uv run python scripts/probe_compression_v2.py --model pythia-160m
"""

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

PHI = (1 + np.sqrt(5)) / 2
INV_PHI = 1 / PHI  # 0.6180339887...

MODELS = {
    "pythia-160m": "EleutherAI/pythia-160m-deduped",
    "pythia-410m": "EleutherAI/pythia-410m-deduped",
    "pythia-1.4b": "EleutherAI/pythia-1.4b-deduped",
    "qwen3-0.6b": "Qwen/Qwen3-0.6B",
    "qwen3-4b": "Qwen/Qwen3-4B",
    "smollm3-3b": "HuggingFaceTB/SmolLM3-3B",
    "mistral-7b": "mistralai/Mistral-7B-v0.3",
}

SAMPLES = [
    "The cat sat on the mat and looked out the window at the birds flying south for the winter.",
    "In a quiet village nestled between rolling hills, the old baker opened his shop at dawn.",
    "Every student who passed the final exam received a certificate of achievement from the dean.",
    "The man who the dog that the cat chased bit ran away quickly.",
    "If every student reads a book then some teacher who knows the author is happy.",
    "The gradient of the loss with respect to the weights is computed via backpropagation.",
    "Attention scores are computed as the softmax of the scaled dot product of queries and keys.",
    "For all x in R, x squared is greater than or equal to zero, with equality if and only if x equals zero.",
    "The probability of A given B equals the probability of B given A times P of A divided by P of B.",
]


def probe_model(model_key: str) -> dict:
    model_name = MODELS[model_key]
    print(f"\n{'='*70}")
    print(f"Probing: {model_key} ({model_name})")
    print(f"{'='*70}")

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, trust_remote_code=True,
        torch_dtype=torch.float32, device_map="cpu",
    )
    model.eval()

    n_layers = model.config.num_hidden_layers
    d_model = model.config.hidden_size
    print(f"  Layers: {n_layers}, d_model: {d_model}")

    # Collect hidden states
    all_hs = []
    for text in SAMPLES:
        inputs = tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs, output_hidden_states=True)
        hs = [h[0].numpy() for h in outputs.hidden_states]
        all_hs.append(hs)

    n_total = len(all_hs[0])
    concat_hs = []
    for l in range(n_total):
        concat_hs.append(np.concatenate([hs[l] for hs in all_hs], axis=0))
    
    n_tokens = concat_hs[0].shape[0]
    print(f"  Tokens: {n_tokens}, Layers+emb: {n_total}")

    # ── Metric 1: Residual stream analysis ────────────────────
    # Each transformer layer: output = input + delta
    # delta = attention(input) + ffn(input)
    # Ratio: ||delta|| / ||input|| — how much each layer ADDS relative to what's there
    # Ratio: ||delta|| / ||output|| — what fraction of the output is NEW
    print(f"\n  === RESIDUAL STREAM ANALYSIS ===")
    print(f"  {'Layer':>6} {'δ/in':>8} {'δ/out':>8} {'cos(in,out)':>11} {'cum_cos':>8} {'norm_ratio':>10}")
    print(f"  {'-'*6} {'-'*8} {'-'*8} {'-'*11} {'-'*8} {'-'*10}")

    residual_ratios_in = []
    residual_ratios_out = []
    cos_in_out = []
    norm_ratios = []

    for l in range(1, n_total):
        inp = concat_hs[l - 1]
        out = concat_hs[l]
        delta = out - inp

        # Per-token norms, then mean
        inp_norm = np.linalg.norm(inp, axis=-1)
        out_norm = np.linalg.norm(out, axis=-1)
        delta_norm = np.linalg.norm(delta, axis=-1)

        r_in = float(np.mean(delta_norm / (inp_norm + 1e-10)))
        r_out = float(np.mean(delta_norm / (out_norm + 1e-10)))

        # Cosine similarity between input and output
        cos = float(np.mean(
            np.sum(inp * out, axis=-1) /
            (inp_norm * out_norm + 1e-10)
        ))

        # Cumulative: cos(embedding, layer_l)
        emb = concat_hs[0]
        emb_norm = np.linalg.norm(emb, axis=-1)
        cum_cos = float(np.mean(
            np.sum(emb * out, axis=-1) /
            (emb_norm * out_norm + 1e-10)
        ))

        # Norm growth: ||output|| / ||input||
        nr = float(np.mean(out_norm / (inp_norm + 1e-10)))

        residual_ratios_in.append(r_in)
        residual_ratios_out.append(r_out)
        cos_in_out.append(cos)
        norm_ratios.append(nr)

        phi_dev_r_out = abs(r_out - INV_PHI)
        phi_dev_nr = abs(nr - INV_PHI)
        marker = ""
        if phi_dev_r_out < 0.05:
            marker = " ← δ/out≈φ!"
        elif phi_dev_nr < 0.05:
            marker = " ← norm≈φ!"
        elif phi_dev_r_out < 0.10:
            marker = " ~ δ/out≈φ"

        print(f"  {l:>6} {r_in:>8.4f} {r_out:>8.4f} {cos:>11.4f} {cum_cos:>8.4f} {nr:>10.4f}{marker}")

    # ── Metric 2: SVD spectrum compression per layer ──────────
    # Track how the singular value spectrum changes layer by layer
    # The RATIO of consecutive singular values might show phi
    print(f"\n  === SVD SPECTRUM RATIOS (σ₂/σ₁, σ₃/σ₂, ...) ===")
    print(f"  {'Layer':>6} {'σ₂/σ₁':>8} {'σ₃/σ₂':>8} {'σ₄/σ₃':>8} {'σ₅/σ₄':>8} {'mean':>8} {'φ-dev':>7}")
    print(f"  {'-'*6} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*7}")

    sv_ratio_means = []
    for l in range(n_total):
        H = concat_hs[l].astype(np.float32)
        s = np.linalg.svd(H, compute_uv=False)
        s = s[s > 1e-10]
        if len(s) < 6:
            continue
        ratios = s[1:6] / s[0:5]
        mean_ratio = float(np.mean(ratios))
        sv_ratio_means.append(mean_ratio)
        phi_dev = abs(mean_ratio - INV_PHI)
        marker = " ← φ!" if phi_dev < 0.05 else (" ~ φ" if phi_dev < 0.10 else "")
        label = "emb" if l == 0 else str(l)
        print(f"  {label:>6} {ratios[0]:>8.4f} {ratios[1]:>8.4f} {ratios[2]:>8.4f} "
              f"{ratios[3]:>8.4f} {mean_ratio:>8.4f} {phi_dev:>7.4f}{marker}")

    # ── Metric 3: Per-layer information distance ──────────────
    # Normalize each layer's hidden states, compute the change in
    # the covariance structure (not just the vectors)
    print(f"\n  === COVARIANCE COMPRESSION ===")
    print(f"  Track how the representation covariance changes per layer")
    print(f"  {'Layer':>6} {'cov_rank':>9} {'rank_ratio':>10} {'φ-dev':>7}")
    print(f"  {'-'*6} {'-'*9} {'-'*10} {'-'*7}")

    prev_rank = None
    cov_rank_ratios = []
    for l in range(n_total):
        H = concat_hs[l].astype(np.float32)
        # Center
        H_centered = H - H.mean(axis=0, keepdims=True)
        # Covariance: (d, d)
        cov = (H_centered.T @ H_centered) / H_centered.shape[0]
        # Eigenvalues
        eigvals = np.linalg.eigvalsh(cov)
        eigvals = eigvals[eigvals > 1e-8]
        # Effective rank of covariance
        p = eigvals / eigvals.sum()
        ent = -np.sum(p * np.log(p))
        erank = np.exp(ent)

        label = "emb" if l == 0 else str(l)
        if prev_rank is not None:
            ratio = erank / prev_rank
            cov_rank_ratios.append(ratio)
            phi_dev = abs(ratio - INV_PHI)
            marker = " ← φ!" if phi_dev < 0.05 else (" ~ φ" if phi_dev < 0.10 else "")
            print(f"  {label:>6} {erank:>9.2f} {ratio:>10.4f} {phi_dev:>7.4f}{marker}")
        else:
            print(f"  {label:>6} {erank:>9.2f}        ---     ---")
        prev_rank = erank

    # ── Summary ───────────────────────────────────────────────
    print(f"\n  === SUMMARY ===")
    print(f"  1/φ = {INV_PHI:.6f}")
    
    print(f"\n  Residual δ/out ratios:")
    print(f"    Mean: {np.mean(residual_ratios_out):.4f}, Median: {np.median(residual_ratios_out):.4f}")
    print(f"    φ-dev of mean: {abs(np.mean(residual_ratios_out) - INV_PHI):.4f}")
    
    print(f"\n  SVD spectrum ratios (consecutive σ ratios):")
    print(f"    Mean: {np.mean(sv_ratio_means):.4f}, Median: {np.median(sv_ratio_means):.4f}")
    print(f"    φ-dev of mean: {abs(np.mean(sv_ratio_means) - INV_PHI):.4f}")
    
    if cov_rank_ratios:
        print(f"\n  Covariance rank ratios:")
        print(f"    Mean: {np.mean(cov_rank_ratios):.4f}, Median: {np.median(cov_rank_ratios):.4f}")
        print(f"    φ-dev of mean: {abs(np.mean(cov_rank_ratios) - INV_PHI):.4f}")

    # Which metric is closest to phi?
    metrics = {
        "residual_delta_out": np.mean(residual_ratios_out),
        "svd_spectrum_ratio": np.mean(sv_ratio_means),
        "cov_rank_ratio": np.mean(cov_rank_ratios) if cov_rank_ratios else None,
        "norm_growth": np.mean(norm_ratios),
    }
    
    print(f"\n  All metric means vs φ:")
    for name, val in sorted(metrics.items()):
        if val is not None:
            dev = abs(val - INV_PHI)
            marker = " ← CLOSE!" if dev < 0.05 else (" ~ near" if dev < 0.10 else "")
            print(f"    {name:>25}: {val:.4f}  (φ-dev={dev:.4f}){marker}")

    del model, tokenizer
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="small",
                        choices=list(MODELS.keys()) + ["all", "small"])
    args = parser.parse_args()

    if args.model == "all":
        keys = list(MODELS.keys())
    elif args.model == "small":
        keys = ["pythia-160m", "pythia-410m", "qwen3-0.6b"]
    else:
        keys = [args.model]

    all_metrics = {}
    for k in keys:
        try:
            all_metrics[k] = probe_model(k)
        except Exception as e:
            print(f"ERROR: {k}: {e}")
            import traceback
            traceback.print_exc()

    if len(all_metrics) > 1:
        print(f"\n{'='*70}")
        print(f"CROSS-MODEL COMPARISON")
        print(f"{'='*70}")
        print(f"1/φ = {INV_PHI:.6f}")
        print()
        for metric_name in ["residual_delta_out", "svd_spectrum_ratio", "cov_rank_ratio", "norm_growth"]:
            vals = [m[metric_name] for m in all_metrics.values() if m.get(metric_name) is not None]
            if vals:
                mean = np.mean(vals)
                std = np.std(vals)
                dev = abs(mean - INV_PHI)
                marker = " ⚡ SIGNAL!" if dev < 0.05 else (" ~ near" if dev < 0.10 else "")
                print(f"  {metric_name:>25}: mean={mean:.4f} ± {std:.4f}  φ-dev={dev:.4f}{marker}")
                for name, m in all_metrics.items():
                    v = m.get(metric_name)
                    if v is not None:
                        print(f"    {name:>15}: {v:.4f}")


if __name__ == "__main__":
    main()
