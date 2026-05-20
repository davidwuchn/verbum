"""Convert & Test — ternary model conversion proof of concept.

Three conversion modes, each more sophisticated:
  Phase 1: Raw ternary — sign(W) for all linear weights
  Phase 2: SVD ternary — low-rank SVD, ternary quantize the basis
  Phase 3: Holographic — unified plate per layer (future)

Tests generation quality after conversion by:
  1. Computing logit cosine similarity vs original
  2. Generating text samples
  3. Measuring total plate size on disk

Usage:
    uv run python scripts/v12/convert_and_test.py --model pythia-2.8b --mode raw
    uv run python scripts/v12/convert_and_test.py --model pythia-2.8b --mode svd --rank 64
    uv run python scripts/v12/convert_and_test.py --model qwen3-14b --mode svd --rank 128

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np

MODELS = {
    "pythia-2.8b":  "EleutherAI/pythia-2.8b-deduped",
    "mistral-7b":   "mistralai/Mistral-7B-v0.3",
    "qwen3-14b":    "Qwen/Qwen3-14B",
}

TEST_PROMPTS = [
    "The capital of France is",
    "def fibonacci(n):\n    ",
    "In quantum mechanics, the wave function",
    "Once upon a time in a land far away,",
    "The meaning of life is",
    "λx.λy.x is the combinator known as",
    "To compile a Haskell program, you need to",
    "The Pythagorean theorem states that",
]


def get_linear_modules(model):
    """Find all linear layers in the model, organized by transformer layer."""
    import torch.nn as nn

    layers_info = []

    # Detect architecture
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        transformer_layers = model.model.layers
        arch = 'standard'
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        transformer_layers = model.gpt_neox.layers
        arch = 'gptneox'
    else:
        raise ValueError("Unknown architecture")

    for li, layer in enumerate(transformer_layers):
        layer_modules = {}
        for name, mod in layer.named_modules():
            if isinstance(mod, nn.Linear):
                layer_modules[name] = mod
        layers_info.append((li, layer_modules))

    return layers_info, arch


def convert_raw_ternary(model, verbose: bool = True):
    """Phase 1: Replace all linear weights with sign(W)."""
    import torch

    layers_info, arch = get_linear_modules(model)
    total_params = 0
    total_nonzero = 0

    for li, modules in layers_info:
        for name, mod in modules.items():
            W = mod.weight.data
            W_ternary = torch.sign(W)
            mod.weight.data = W_ternary.to(W.dtype)
            n = W.numel()
            nz = (W_ternary != 0).sum().item()
            total_params += n
            total_nonzero += nz

        if verbose and (li + 1) % 10 == 0:
            print(f"    Layer {li+1} done", file=sys.stderr, flush=True)

    # Ternary size: 2 bits per param (stores -1, 0, +1)
    ternary_bytes = (total_params * 2) // 8
    zero_frac = 1.0 - total_nonzero / max(total_params, 1)

    return {
        "mode": "raw_ternary",
        "total_params": total_params,
        "ternary_bytes": ternary_bytes,
        "ternary_mb": ternary_bytes / (1024 * 1024),
        "zero_fraction": zero_frac,
    }


def convert_svd_ternary(model, rank: int = 64, verbose: bool = True):
    """Phase 2: SVD low-rank ternary — keep top-k singular vectors, ternary quantize."""
    import torch

    layers_info, arch = get_linear_modules(model)
    total_original_params = 0
    total_plate_params = 0
    total_beam_params = 0

    for li, modules in layers_info:
        for name, mod in modules.items():
            W = mod.weight.data.float()  # (out_dim, in_dim)
            out_dim, in_dim = W.shape
            k = min(rank, out_dim, in_dim)

            # SVD
            U, S, Vt = torch.linalg.svd(W, full_matrices=False)

            # Plate: ternary quantize the basis directions (Vt rows = input space)
            Vt_k = Vt[:k]                          # (k, in_dim) — the crystal directions
            plate = torch.sign(Vt_k)                # ternary plate

            # Beam: keep U and S as continuous (small — these are the readout)
            U_k = U[:, :k]                          # (out_dim, k)
            S_k = S[:k]                             # (k,)

            # Reconstruct: W_approx = U_k @ diag(S_k) @ plate
            W_approx = U_k @ torch.diag(S_k) @ plate
            mod.weight.data = W_approx.to(mod.weight.dtype)

            total_original_params += out_dim * in_dim
            total_plate_params += k * in_dim        # ternary
            total_beam_params += out_dim * k + k    # continuous (U_k + S_k)

        if verbose and (li + 1) % 10 == 0:
            print(f"    Layer {li+1} done", file=sys.stderr, flush=True)

    plate_bytes = (total_plate_params * 2) // 8       # 2 bits per ternary
    beam_bytes = total_beam_params * 2                 # 16 bits (bf16) per continuous
    total_bytes = plate_bytes + beam_bytes

    return {
        "mode": "svd_ternary",
        "rank": rank,
        "total_original_params": total_original_params,
        "plate_params": total_plate_params,
        "beam_params": total_beam_params,
        "plate_bytes": plate_bytes,
        "plate_mb": plate_bytes / (1024 * 1024),
        "beam_bytes": beam_bytes,
        "beam_mb": beam_bytes / (1024 * 1024),
        "total_mb": total_bytes / (1024 * 1024),
        "compression_vs_bf16": (total_original_params * 2) / max(total_bytes, 1),
    }


def compute_logit_similarity(
    model_orig, model_conv, tokenizer, prompts: list[str], device: str,
) -> dict:
    """Compare logits between original and converted model."""
    import torch

    cosines = []
    top1_matches = []
    top5_overlaps = []

    for prompt in prompts:
        input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)

        with torch.no_grad():
            logits_orig = model_orig(input_ids).logits[:, -1, :].float().cpu()
            logits_conv = model_conv(input_ids).logits[:, -1, :].float().cpu()

        # Cosine similarity
        cos = torch.nn.functional.cosine_similarity(
            logits_orig.flatten().unsqueeze(0),
            logits_conv.flatten().unsqueeze(0),
        ).item()
        cosines.append(cos)

        # Top-1 match
        top1_orig = logits_orig.argmax(dim=-1).item()
        top1_conv = logits_conv.argmax(dim=-1).item()
        top1_matches.append(top1_orig == top1_conv)

        # Top-5 overlap
        top5_orig = set(logits_orig.topk(5, dim=-1).indices[0].tolist())
        top5_conv = set(logits_conv.topk(5, dim=-1).indices[0].tolist())
        top5_overlaps.append(len(top5_orig & top5_conv) / 5.0)

    return {
        "mean_cosine": float(np.mean(cosines)),
        "min_cosine": float(np.min(cosines)),
        "cosines": cosines,
        "top1_match_rate": float(np.mean(top1_matches)),
        "mean_top5_overlap": float(np.mean(top5_overlaps)),
    }


def generate_samples(model, tokenizer, prompts: list[str], device: str,
                     max_new_tokens: int = 50) -> list[dict]:
    """Generate text samples from the model."""
    import torch

    samples = []
    for prompt in prompts:
        input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            output = model.generate(
                input_ids,
                max_new_tokens=max_new_tokens,
                do_sample=False,  # greedy for reproducibility
                temperature=1.0,
            )
        generated = tokenizer.decode(output[0], skip_special_tokens=True)
        samples.append({
            "prompt": prompt,
            "generation": generated,
        })
    return samples


def main():
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import copy

    parser = argparse.ArgumentParser(description="Convert & Test")
    parser.add_argument("--model", default="pythia-2.8b", choices=list(MODELS.keys()))
    parser.add_argument("--mode", default="svd", choices=["raw", "svd"])
    parser.add_argument("--rank", type=int, default=64, help="SVD rank for mode=svd")
    parser.add_argument("--device", default="mps")
    parser.add_argument("--max-tokens", type=int, default=50)
    parser.add_argument("--output-dir", default="results/conversion-test")
    parser.add_argument("--skip-comparison", action="store_true",
                        help="Skip logit comparison (saves memory — no need for two models)")

    args = parser.parse_args()
    model_name = MODELS[args.model]

    print("=" * 90, file=sys.stderr, flush=True)
    print(f"  Convert & Test — {args.model} → {args.mode} ternary", file=sys.stderr, flush=True)
    if args.mode == "svd":
        print(f"  SVD rank: {args.rank}", file=sys.stderr, flush=True)
    print("=" * 90, file=sys.stderr, flush=True)

    t_start = time.time()

    # Load tokenizer
    print(f"\n  Loading tokenizer...", file=sys.stderr, flush=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    if not args.skip_comparison:
        # ── Load original model for comparison ──
        print(f"  Loading original model for comparison...", file=sys.stderr, flush=True)
        model_orig = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=torch.bfloat16, device_map=args.device, trust_remote_code=True,
        )
        model_orig.eval()

        print(f"\n  ─── Original Model Generation ───", file=sys.stderr, flush=True)
        orig_samples = generate_samples(model_orig, tokenizer, TEST_PROMPTS[:4], args.device, args.max_tokens)
        for s in orig_samples:
            text = s['generation'][:120].replace('\n', '\\n')
            print(f"    {text}", file=sys.stderr, flush=True)

        # Free original model
        del model_orig
        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()

    # ── Load model for conversion ──
    print(f"\n  Loading model for conversion...", file=sys.stderr, flush=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map=args.device, trust_remote_code=True,
    )
    model.eval()

    # Original model size
    orig_params = sum(p.numel() for p in model.parameters())
    orig_bytes = sum(p.numel() * p.element_size() for p in model.parameters())
    print(f"  Original: {orig_params/1e6:.1f}M params, {orig_bytes/1024/1024:.0f} MB",
          file=sys.stderr, flush=True)

    # ── Convert ──
    print(f"\n  Converting ({args.mode})...", file=sys.stderr, flush=True)
    t_conv = time.time()

    if args.mode == "raw":
        conv_info = convert_raw_ternary(model)
    elif args.mode == "svd":
        conv_info = convert_svd_ternary(model, rank=args.rank)

    conv_time = time.time() - t_conv
    print(f"  Conversion done in {conv_time:.1f}s", file=sys.stderr, flush=True)

    # Print conversion info
    print(f"\n  ─── Conversion Results ───", file=sys.stderr, flush=True)
    for k, v in conv_info.items():
        if isinstance(v, float):
            print(f"    {k}: {v:.4f}", file=sys.stderr, flush=True)
        else:
            print(f"    {k}: {v}", file=sys.stderr, flush=True)

    # ── Generate from converted model ──
    print(f"\n  ─── Converted Model Generation ───", file=sys.stderr, flush=True)
    conv_samples = generate_samples(model, tokenizer, TEST_PROMPTS, args.device, args.max_tokens)
    for s in conv_samples:
        text = s['generation'][:120].replace('\n', '\\n')
        print(f"    {text}", file=sys.stderr, flush=True)

    # ── Logit comparison (if we have both models) ──
    logit_info = None
    if not args.skip_comparison:
        print(f"\n  Loading original again for logit comparison...", file=sys.stderr, flush=True)
        model_orig = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=torch.bfloat16, device_map=args.device, trust_remote_code=True,
        )
        model_orig.eval()

        print(f"  Computing logit similarity...", file=sys.stderr, flush=True)
        logit_info = compute_logit_similarity(model_orig, model, tokenizer, TEST_PROMPTS, args.device)
        print(f"\n  ─── Logit Comparison ───", file=sys.stderr, flush=True)
        print(f"    Mean cosine similarity: {logit_info['mean_cosine']:.4f}", file=sys.stderr, flush=True)
        print(f"    Min cosine similarity:  {logit_info['min_cosine']:.4f}", file=sys.stderr, flush=True)
        print(f"    Top-1 match rate:       {logit_info['top1_match_rate']:.1%}", file=sys.stderr, flush=True)
        print(f"    Mean top-5 overlap:     {logit_info['mean_top5_overlap']:.1%}", file=sys.stderr, flush=True)

        del model_orig

    # ── Save results ──
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "model": args.model,
        "model_name": model_name,
        "mode": args.mode,
        "rank": args.rank if args.mode == "svd" else None,
        "original_params": orig_params,
        "original_mb": orig_bytes / (1024 * 1024),
        "conversion_info": conv_info,
        "conversion_time_s": conv_time,
        "generated_samples": conv_samples,
        "logit_comparison": logit_info,
    }

    json_path = output_dir / f"convert_{args.model}_{args.mode}_k{args.rank}.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  💾 {json_path}", file=sys.stderr, flush=True)

    elapsed = time.time() - t_start
    print(f"\n{'='*90}", file=sys.stderr, flush=True)
    print(f"  SUMMARY: {args.model} → {args.mode} (rank={args.rank})", file=sys.stderr, flush=True)
    if args.mode == "svd":
        print(f"    Plate: {conv_info['plate_mb']:.1f} MB (ternary)", file=sys.stderr, flush=True)
        print(f"    Beam:  {conv_info['beam_mb']:.1f} MB (continuous)", file=sys.stderr, flush=True)
        print(f"    Total: {conv_info['total_mb']:.1f} MB ({conv_info['compression_vs_bf16']:.1f}× vs bf16)",
              file=sys.stderr, flush=True)
    elif args.mode == "raw":
        print(f"    Ternary: {conv_info['ternary_mb']:.1f} MB", file=sys.stderr, flush=True)
    if logit_info:
        print(f"    Logit cosine: {logit_info['mean_cosine']:.4f}", file=sys.stderr, flush=True)
    print(f"  Total time: {elapsed:.0f}s ({elapsed/60:.1f}min)", file=sys.stderr, flush=True)
    print(f"{'='*90}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
