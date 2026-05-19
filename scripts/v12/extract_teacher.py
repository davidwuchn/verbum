#!/usr/bin/env python3
"""Extract teacher hidden states from Qwen3-32B for holographic distillation.

Forwards diverse probes through the teacher model and saves hidden states
at multiple depth points. These become the "beam angle photographs" that
get etched into V12's ternary plates.

The teacher has 64 layers. We sample hidden states at 8 depth points
(every 8 layers) to create a depth profile. V12's 7 passes map to
these depth points during distillation.

Output: checkpoints/teacher-features/
  - features_{depth}.npz  — hidden states at each depth point
  - manifest.json          — metadata (model, probes, depths)

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/extract_teacher.py

    # Custom probe count:
    uv run python scripts/v12/extract_teacher.py --n-probes 500

    # Dry run (just check model loads):
    uv run python scripts/v12/extract_teacher.py --dry-run

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

# ══════════════════════════════════════════════════════════════════════
# Probe generation — diverse inputs for multiple beam angles
# ══════════════════════════════════════════════════════════════════════

def load_diverse_probes(max_probes: int = 500) -> list[str]:
    """Load diverse probe texts from multiple sources.

    Sources (in priority order):
      1. lattice/diverse_corpus.json (807 probes across 8 domains)
      2. data/compile-train.jsonl (NL → lambda pairs)
      3. Generated lambda expressions from lambda_gen
    """
    probes = []

    # 1. Diverse corpus (already curated for multi-domain coverage)
    corpus_path = Path("lattice/diverse_corpus.json")
    if corpus_path.exists():
        with open(corpus_path) as f:
            corpus = json.load(f)
        if isinstance(corpus, list):
            for item in corpus:
                if isinstance(item, dict):
                    # Try common keys: text, prompt, input
                    text = item.get("text") or item.get("prompt") or item.get("input")
                    if text:
                        probes.append(text)
                elif isinstance(item, str):
                    probes.append(item)
        elif isinstance(corpus, dict) and "probes" in corpus:
            for item in corpus["probes"]:
                if isinstance(item, dict):
                    text = item.get("text") or item.get("prompt") or item.get("input")
                    if text:
                        probes.append(text)
                elif isinstance(item, str):
                    probes.append(item)
        print(f"  Diverse corpus: {len(probes)} probes", file=sys.stderr)

    # 2. Compile examples
    compile_path = Path("data/compile-train.jsonl")
    if compile_path.exists() and len(probes) < max_probes:
        with open(compile_path) as f:
            for line in f:
                if line.strip():
                    d = json.loads(line)
                    probes.append(f"{d['input']} → {d['output']}")
        print(f"  + compile examples: {len(probes)} total", file=sys.stderr)

    # 3. Lambda gen (if still need more)
    if len(probes) < max_probes:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        from verbum.lambda_gen import LambdaGenerator, Op
        gen = LambdaGenerator(seed=777)
        for op in Op:
            examples = gen.generate(op, n=50)
            for ex in examples:
                probes.append(f"[{ex.op.value}] {ex.expr}")
        print(f"  + lambda gen: {len(probes)} total", file=sys.stderr)

    # Deduplicate and limit
    seen = set()
    unique = []
    for p in probes:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    probes = unique[:max_probes]
    print(f"  Final: {len(probes)} unique probes", file=sys.stderr)
    return probes


# ══════════════════════════════════════════════════════════════════════
# Teacher extraction
# ══════════════════════════════════════════════════════════════════════

def extract_features(
    model_name: str = "Qwen/Qwen3-32B",
    probes: list[str] | None = None,
    n_probes: int = 500,
    max_seq_len: int = 128,
    output_dir: str = "checkpoints/teacher-features",
    batch_size: int = 4,
    n_depth_points: int = 8,
    dry_run: bool = False,
):
    """Extract hidden states from teacher model at multiple depths.

    For each probe:
      - Tokenize and forward through teacher
      - Record hidden state at n_depth_points evenly-spaced layers
      - Save as numpy arrays

    The hidden states capture the teacher's computation at each depth.
    V12's distillation etch will use these as targets.
    """
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Load probes
    if probes is None:
        probes = load_diverse_probes(max_probes=n_probes)

    # Load tokenizer
    print(f"\nLoading tokenizer for {model_name}...", file=sys.stderr)
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Tokenize all probes
    print(f"Tokenizing {len(probes)} probes...", file=sys.stderr)
    encodings = tokenizer(
        probes,
        padding=True,
        truncation=True,
        max_length=max_seq_len,
        return_tensors="pt",
    )
    input_ids = encodings["input_ids"]
    attention_mask = encodings["attention_mask"]
    print(f"  Token shape: {input_ids.shape}", file=sys.stderr)

    if dry_run:
        print("\nDry run — skipping model load.", file=sys.stderr)
        manifest = {
            "model": model_name,
            "n_probes": len(probes),
            "max_seq_len": max_seq_len,
            "token_shape": list(input_ids.shape),
            "dry_run": True,
        }
        with open(output_path / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
        return

    # Load model
    print(f"\nLoading {model_name}...", file=sys.stderr)
    t0 = time.time()
    # On Apple Silicon, use MPS for inference but load to CPU first
    # then move, to avoid placeholder storage issues with device_map="auto"
    device = "cpu"
    if torch.backends.mps.is_available():
        # MPS available but large models can hit placeholder issues
        # with device_map="auto". Load on CPU, it's fast enough with
        # 512GB unified memory.
        device = "cpu"
        print(f"  Using CPU (MPS available but safer for large models)",
              file=sys.stderr)
    elif torch.cuda.is_available():
        device = "cuda"

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        device_map={"": device},
        output_hidden_states=True,
    )
    model.eval()
    dt = time.time() - t0
    print(f"  Loaded in {dt:.1f}s", file=sys.stderr)

    # Determine depth points
    n_layers = model.config.num_hidden_layers
    # Evenly space depth points including first and last layer
    depth_indices = np.linspace(0, n_layers, n_depth_points + 1,
                                dtype=int)[1:]  # skip layer 0 (embedding)
    depth_indices = sorted(set(depth_indices.tolist()))
    print(f"  {n_layers} layers, depth points: {depth_indices}", file=sys.stderr)

    # Extract features in batches
    print(f"\nExtracting features ({batch_size} per batch)...", file=sys.stderr)

    # Storage: dict[depth_idx] -> list of hidden state arrays
    all_features = {d: [] for d in depth_indices}
    all_input_features = {d: [] for d in depth_indices}  # input to each layer

    n_batches = (len(probes) + batch_size - 1) // batch_size
    t0 = time.time()

    with torch.no_grad():
        for batch_idx in range(n_batches):
            start = batch_idx * batch_size
            end = min(start + batch_size, len(probes))

            batch_ids = input_ids[start:end].to(device)
            batch_mask = attention_mask[start:end].to(device)

            # Forward with hidden states
            outputs = model(
                input_ids=batch_ids,
                attention_mask=batch_mask,
                output_hidden_states=True,
            )

            # outputs.hidden_states is a tuple of (n_layers + 1) tensors
            # hidden_states[0] = embedding output
            # hidden_states[i] = output of layer i (1-indexed)
            hidden_states = outputs.hidden_states

            for depth_idx in depth_indices:
                # Input to layer = output of previous layer
                layer_input = hidden_states[depth_idx - 1]  # input
                layer_output = hidden_states[depth_idx]      # output

                # Convert to numpy, keep only non-padding positions
                for b in range(batch_ids.shape[0]):
                    mask = batch_mask[b].bool()
                    inp = layer_input[b][mask].float().cpu().numpy()
                    out = layer_output[b][mask].float().cpu().numpy()
                    all_input_features[depth_idx].append(inp)
                    all_features[depth_idx].append(out)

            if (batch_idx + 1) % 10 == 0 or batch_idx == n_batches - 1:
                elapsed = time.time() - t0
                rate = (batch_idx + 1) / elapsed
                eta = (n_batches - batch_idx - 1) / rate
                print(f"  Batch {batch_idx+1}/{n_batches} "
                      f"({elapsed:.1f}s, ETA {eta:.1f}s)", file=sys.stderr)

            # Clear GPU cache periodically
            if (batch_idx + 1) % 20 == 0:
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

    # Save features
    print(f"\nSaving features to {output_path}/...", file=sys.stderr)
    for depth_idx in depth_indices:
        # Stack all probes' features for this depth
        # Variable length sequences → save as list of arrays
        inputs = all_input_features[depth_idx]
        outputs = all_features[depth_idx]

        # Save as npz with numbered keys
        input_dict = {f"inp_{i}": arr for i, arr in enumerate(inputs)}
        output_dict = {f"out_{i}": arr for i, arr in enumerate(outputs)}

        np.savez_compressed(
            output_path / f"layer_{depth_idx:03d}_inputs.npz",
            **input_dict,
        )
        np.savez_compressed(
            output_path / f"layer_{depth_idx:03d}_outputs.npz",
            **output_dict,
        )
        total_tokens = sum(arr.shape[0] for arr in outputs)
        print(f"  Layer {depth_idx:3d}: {len(outputs)} probes, "
              f"{total_tokens:,} tokens, d={outputs[0].shape[-1]}", file=sys.stderr)

    # Save manifest
    manifest = {
        "model": model_name,
        "n_probes": len(probes),
        "n_layers": n_layers,
        "d_model": int(outputs[0].shape[-1]),
        "depth_indices": depth_indices,
        "max_seq_len": max_seq_len,
        "batch_size": batch_size,
        "probe_texts": probes[:10],  # save first 10 for reference
        "total_probes": len(probes),
    }
    with open(output_path / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    total_time = time.time() - t0
    total_size = sum(
        f.stat().st_size for f in output_path.glob("*.npz")
    ) / 1024 / 1024
    print(f"\n  Total: {total_size:.1f} MB, {total_time:.1f}s", file=sys.stderr)
    print(f"  Manifest: {output_path}/manifest.json", file=sys.stderr)


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Extract teacher features for holographic distillation")
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-32B",
                        help="Teacher model name")
    parser.add_argument("--n-probes", type=int, default=500,
                        help="Number of probes to extract")
    parser.add_argument("--max-seq-len", type=int, default=128,
                        help="Maximum sequence length for probes")
    parser.add_argument("--batch-size", type=int, default=4,
                        help="Batch size for extraction")
    parser.add_argument("--output", type=str,
                        default="checkpoints/teacher-features",
                        help="Output directory")
    parser.add_argument("--n-depths", type=int, default=8,
                        help="Number of depth sampling points")
    parser.add_argument("--dry-run", action="store_true",
                        help="Just check probes and tokenization, skip model")
    args = parser.parse_args()

    print("=" * 60, file=sys.stderr)
    print("  Teacher Feature Extraction", file=sys.stderr)
    print(f"  Model: {args.model}", file=sys.stderr)
    print(f"  Probes: {args.n_probes}", file=sys.stderr)
    print(f"  Depths: {args.n_depths}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    extract_features(
        model_name=args.model,
        n_probes=args.n_probes,
        max_seq_len=args.max_seq_len,
        output_dir=args.output,
        batch_size=args.batch_size,
        n_depth_points=args.n_depths,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
