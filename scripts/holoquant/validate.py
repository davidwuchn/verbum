#!/usr/bin/env python3
"""HoloQuant validation — perplexity before/after ternarization.

The critical experiment: does replacing 93.6% of weights with ternary
values preserve model quality?

Steps:
  1. Load model (transformers)
  2. Measure baseline perplexity on test text
  3. Apply HoloQuant: ternarize holographic weights, keep precision weights
  4. Measure HoloQuant perplexity
  5. Report: perplexity delta, per-component breakdown, memory savings

Usage:
    # Quick validation on Pythia-160M (fast, validates methodology)
    uv run python scripts/holoquant/validate.py --model pythia

    # Full validation on Qwen3.6-35B-A3B
    uv run python scripts/holoquant/validate.py --model qwen36

    # Custom threshold for ternary-safe classification
    uv run python scripts/holoquant/validate.py --model pythia --threshold 0.90

License: MIT
"""

from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

# Add parent for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "explore"))

from core import ternarize, HoloLinear


MODELS = {
    "pythia": {
        "hf_name": "EleutherAI/pythia-160m-deduped",
        "description": "Pythia-160M — fast validation target",
    },
    "pythia-1b": {
        "hf_name": "EleutherAI/pythia-1b-deduped",
        "description": "Pythia-1B — mid-scale validation",
    },
    "qwen36": {
        "hf_name": "Qwen/Qwen3.6-35B-A3B",
        "description": "Qwen3.6-35B-A3B — primary HoloQuant target",
    },
}

# Gaussian baselines for corrected holographic score
GAUSSIAN_TC = float(np.sqrt(2 / np.pi))  # 0.7979
GAUSSIAN_CV = float(np.sqrt(np.pi / 2 - 1))  # 0.7555


def compute_corrected_score(W: torch.Tensor) -> float:
    """Compute corrected holographic score for a weight matrix."""
    W_flat = W.detach().float().reshape(-1)
    abs_W = W_flat.abs()

    # Ternary cosine
    dot = abs_W.sum().item()
    norm_W = W_flat.norm().item()
    n_nonzero = (W_flat != 0).sum().item()
    norm_sign = math.sqrt(n_nonzero + 1e-12)
    tc = dot / (norm_W * norm_sign + 1e-12)

    # Magnitude CV
    mag_mean = abs_W.mean().item()
    mag_std = abs_W.std().item()
    cv = mag_std / max(mag_mean, 1e-12)

    return 0.5 * (tc / GAUSSIAN_TC) + 0.5 * (GAUSSIAN_CV / max(cv, 0.01))


@torch.no_grad()
def measure_perplexity(model, tokenizer, texts: list[str],
                       max_length: int = 512, device: str = "cpu") -> float:
    """Measure perplexity on a list of texts."""
    total_loss = 0.0
    total_tokens = 0

    for text in texts:
        inputs = tokenizer(text, return_tensors="pt", truncation=True,
                          max_length=max_length).to(device)
        input_ids = inputs["input_ids"]

        if input_ids.shape[1] < 2:
            continue

        outputs = model(**inputs, labels=input_ids)
        loss = outputs.loss.item()
        n_tokens = input_ids.shape[1] - 1  # loss is over shifted tokens

        total_loss += loss * n_tokens
        total_tokens += n_tokens

    if total_tokens == 0:
        return float("inf")

    avg_loss = total_loss / total_tokens
    return math.exp(avg_loss)


def get_test_texts() -> list[str]:
    """Standard test texts for perplexity measurement."""
    return [
        "The transformer architecture revolutionized natural language processing by introducing self-attention mechanisms that allow models to weigh the importance of different parts of the input when producing each part of the output. Unlike recurrent neural networks, transformers can process all positions in parallel, leading to significant speedups during training.",
        "In quantum mechanics, the wave function describes the quantum state of a particle or system of particles. The Schrödinger equation governs how the wave function evolves over time. When a measurement is made, the wave function collapses to an eigenstate of the observable being measured.",
        "The Viable System Model, developed by Stafford Beer in 1972, describes the organizational structure needed for any viable system. It consists of five interacting subsystems: operations, coordination, control, intelligence, and identity. Each subsystem has a specific role in maintaining the viability of the organization.",
        "Lambda calculus is a formal system for expressing computation based on function abstraction and application using variable binding and substitution. It was introduced by Alonzo Church in the 1930s as part of his research into the foundations of mathematics. It has since become the basis for functional programming languages.",
        "The holographic principle suggests that the description of a volume of space can be thought of as encoded on a lower-dimensional boundary to the region. This principle was first proposed by Gerard 't Hooft and later given a precise string-theory interpretation by Leonard Susskind.",
        "Machine learning models learn representations of data through gradient descent optimization. The loss function measures how well the model's predictions match the true labels. Backpropagation efficiently computes the gradient of the loss with respect to each parameter, enabling the model to improve iteratively.",
        "Combinatory logic is a notation to eliminate the need for quantified variables in mathematical logic. It was introduced by Moses Schönfinkel and Haskell Curry. The key combinators are S, K, and I, which together can express any computable function.",
        "The attention mechanism in neural networks allows the model to focus on relevant parts of the input sequence when generating each output token. Multi-head attention splits the representation into multiple subspaces, allowing the model to attend to information from different representation subspaces at different positions.",
    ]


def apply_holoquant(
    model,
    threshold: float = 0.95,
    group_size: int = 64,
) -> dict:
    """Apply HoloQuant to a model — ternarize holographic weights in-place.

    Returns statistics about what was quantized.
    """
    stats = {
        "n_ternarized": 0,
        "n_kept": 0,
        "n_skipped": 0,
        "params_ternarized": 0,
        "params_kept": 0,
        "params_skipped": 0,
        "per_module": [],
    }

    for name, param in list(model.named_parameters()):
        n = param.numel()

        # Skip small params (biases, norms, etc.)
        if n < 1024:
            stats["n_skipped"] += 1
            stats["params_skipped"] += n
            continue

        # Skip non-weight params
        if any(s in name for s in ["layernorm", "layer_norm", "rmsnorm",
                                    "norm.weight", "norm.bias"]):
            stats["n_skipped"] += 1
            stats["params_skipped"] += n
            continue

        # Compute holographic score
        score = compute_corrected_score(param.data)

        if score > threshold:
            # Ternarize this weight
            ternary, scales = ternarize(param.data, group_size=group_size)

            # Reconstruct: ternary * scales (expanded)
            if param.data.ndim == 2:
                out_feat, in_feat = param.data.shape
                n_groups = scales.shape[-1]
                scales_exp = scales.unsqueeze(-1).expand(
                    -1, -1, group_size).reshape(out_feat, -1)[:, :in_feat]
                param.data = (ternary.float() * scales_exp.float()).to(param.dtype)
            else:
                # For non-2D, just use global scale
                scale = param.data.abs().mean()
                param.data = (torch.sign(param.data) * scale).to(param.dtype)

            stats["n_ternarized"] += 1
            stats["params_ternarized"] += n
            stats["per_module"].append({
                "name": name, "score": score, "params": n, "action": "ternary"
            })
        else:
            stats["n_kept"] += 1
            stats["params_kept"] += n
            stats["per_module"].append({
                "name": name, "score": score, "params": n, "action": "kept"
            })

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="HoloQuant validation — perplexity before/after ternarization")
    parser.add_argument("--model", default="pythia", choices=list(MODELS.keys()))
    parser.add_argument("--threshold", type=float, default=0.95,
                        help="Corrected holographic score threshold for ternarization")
    parser.add_argument("--device", default="cpu",
                        help="Device for inference (cpu, mps, cuda)")
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--group-size", type=int, default=64)
    args = parser.parse_args()

    cfg = MODELS[args.model]
    print(f"HoloQuant Validation")
    print(f"  Model: {cfg['hf_name']}")
    print(f"  Threshold: {args.threshold}")
    print(f"  Device: {args.device}")
    print()

    # Load model
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"Loading model...", end="", flush=True)
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(
        cfg["hf_name"], trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        cfg["hf_name"],
        torch_dtype=torch.float32,
        device_map=args.device,
        trust_remote_code=True,
    )
    model.eval()
    print(f" {time.time()-t0:.1f}s")

    # Count params
    total_params = sum(p.numel() for p in model.parameters())
    total_bytes = sum(p.numel() * p.element_size() for p in model.parameters())
    print(f"  Parameters: {total_params:,} ({total_bytes/1e9:.2f} GB)")

    # Get test texts
    texts = get_test_texts()
    print(f"  Test texts: {len(texts)} passages")

    # Baseline perplexity
    print(f"\n{'='*60}")
    print(f"BASELINE (original weights)")
    print(f"{'='*60}")
    t0 = time.time()
    baseline_ppl = measure_perplexity(
        model, tokenizer, texts, max_length=args.max_length, device=args.device)
    print(f"  Perplexity: {baseline_ppl:.2f} ({time.time()-t0:.1f}s)")

    # Apply HoloQuant
    print(f"\n{'='*60}")
    print(f"APPLYING HOLOQUANT (threshold={args.threshold})")
    print(f"{'='*60}")
    t0 = time.time()
    stats = apply_holoquant(model, threshold=args.threshold,
                            group_size=args.group_size)
    print(f"  Applied in {time.time()-t0:.1f}s")
    print(f"  Ternarized: {stats['n_ternarized']} matrices "
          f"({stats['params_ternarized']:,} params, "
          f"{100*stats['params_ternarized']/total_params:.1f}%)")
    print(f"  Kept:       {stats['n_kept']} matrices "
          f"({stats['params_kept']:,} params, "
          f"{100*stats['params_kept']/total_params:.1f}%)")
    print(f"  Skipped:    {stats['n_skipped']} matrices "
          f"({stats['params_skipped']:,} params)")

    # HoloQuant perplexity
    print(f"\n{'='*60}")
    print(f"HOLOQUANT (ternarized weights)")
    print(f"{'='*60}")
    t0 = time.time()
    holo_ppl = measure_perplexity(
        model, tokenizer, texts, max_length=args.max_length, device=args.device)
    print(f"  Perplexity: {holo_ppl:.2f} ({time.time()-t0:.1f}s)")

    # Results
    ppl_delta = holo_ppl - baseline_ppl
    ppl_pct = 100 * (holo_ppl - baseline_ppl) / baseline_ppl

    print(f"\n{'='*60}")
    print(f"RESULTS")
    print(f"{'='*60}")
    print(f"  Baseline perplexity:  {baseline_ppl:.2f}")
    print(f"  HoloQuant perplexity: {holo_ppl:.2f}")
    print(f"  Delta:                {ppl_delta:+.2f} ({ppl_pct:+.1f}%)")
    print()

    if abs(ppl_pct) < 1.0:
        print(f"  ✅ LOSSLESS — perplexity change < 1%")
    elif abs(ppl_pct) < 5.0:
        print(f"  ⚠️  NEAR-LOSSLESS — perplexity change < 5%")
    else:
        print(f"  ❌ LOSSY — perplexity change ≥ 5%")

    # Memory savings estimate
    ternary_params = stats["params_ternarized"]
    kept_params = stats["params_kept"]
    skipped_params = stats["params_skipped"]
    holo_bytes = (
        ternary_params * 1.6 / 8  # ternary at 1.6 bits
        + kept_params * 2          # kept at FP16
        + skipped_params * 2       # biases/norms at FP16
    )
    print(f"\n  Memory estimate:")
    print(f"    Original (FP16):  {total_params*2/1e9:.2f} GB")
    print(f"    HoloQuant:        {holo_bytes/1e9:.2f} GB")
    print(f"    Savings:          {total_params*2/holo_bytes:.1f}×")

    # Per-module details (top ternarized and top kept)
    ternarized_modules = [m for m in stats["per_module"] if m["action"] == "ternary"]
    kept_modules = [m for m in stats["per_module"] if m["action"] == "kept"]

    if ternarized_modules:
        print(f"\n  Top ternarized (by params):")
        for m in sorted(ternarized_modules, key=lambda x: -x["params"])[:5]:
            print(f"    {m['name']:<50} score={m['score']:.3f} params={m['params']:,}")

    if kept_modules:
        print(f"\n  Kept at precision (by score, ascending):")
        for m in sorted(kept_modules, key=lambda x: x["score"])[:5]:
            print(f"    {m['name']:<50} score={m['score']:.3f} params={m['params']:,}")


if __name__ == "__main__":
    main()
