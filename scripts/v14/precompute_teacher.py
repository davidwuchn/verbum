#!/usr/bin/env python3
"""
Pre-compute teacher logits for knowledge distillation.

Runs Qwen3.6-27B on training shards and saves sparse top-k logits
per token position. Output: one .npz per shard with:
  - indices: (n_batches, seq_len, top_k) int32 — top-k token IDs
  - logits:  (n_batches, seq_len, top_k) float16 — teacher logits (scaled by 1/T)

The student training loop loads these alongside tokens and computes
KL divergence against the teacher's distribution.

Usage:
    uv run python scripts/v14/precompute_teacher.py \
        --shard-start 0 --shard-end 54 \
        --out-dir data/teacher-logits

Memory: ~15 GB for bf16 model on MPS. Processes one shard at a time.
Speed: ~800 tok/s → 50M tokens/shard ÷ 800 ≈ 17 hours per shard.
       But we only need the first ~50K positions per shard (matching
       what training actually sees per shard visit). At seq_len=4096,
       that's ~12 batches per shard = ~50K tokens ≈ 1 minute per shard.

License: MIT
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import torch

TEACHER_NAME = "Qwen/Qwen3.6-27B"
DEVICE = "mps"
DTYPE = torch.bfloat16


def load_teacher():
    from transformers import AutoModelForCausalLM, AutoTokenizer
    print(f"\n  Loading {TEACHER_NAME}...", flush=True)
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(TEACHER_NAME, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        TEACHER_NAME, torch_dtype=DTYPE, device_map=DEVICE,
        trust_remote_code=True, attn_implementation="eager",
    )
    model.eval()
    print(f"  Loaded in {time.time()-t0:.1f}s", flush=True)
    return model, tokenizer


def process_shard(
    model,
    shard_path: Path,
    out_path: Path,
    seq_len: int = 4096,
    n_batches: int = 12,
    top_k: int = 64,
    temperature: float = 2.0,
):
    """Process one shard: run teacher, save sparse logits."""
    # Load shard
    data = np.load(str(shard_path), mmap_mode="r").astype(np.int64)

    needed_per_batch = seq_len + 1  # +1 for target shift
    total_needed = n_batches * needed_per_batch

    if len(data) < total_needed:
        print(f"  ⚠ Shard too small: {len(data):,} < {total_needed:,}")
        n_batches = len(data) // needed_per_batch
        if n_batches == 0:
            return

    all_indices = []
    all_logits = []
    all_positions = []  # track which position in the shard each batch starts at

    t0 = time.time()
    pos = 0

    for batch_idx in range(n_batches):
        # Extract sequence (B=1 for teacher — no batching to save memory)
        tokens = data[pos:pos + seq_len].astype(np.int64)
        pos += needed_per_batch

        # To torch
        input_ids = torch.tensor(tokens, dtype=torch.long, device=DEVICE).unsqueeze(0)

        with torch.no_grad():
            outputs = model(input_ids)
            logits = outputs.logits[0]  # (L, V)

            # Scale by 1/T for softened distribution
            scaled = logits / temperature

            # Top-k selection
            topk_vals, topk_idx = torch.topk(scaled, k=top_k, dim=-1, sorted=True)

            # To numpy (float16 for storage efficiency)
            all_indices.append(topk_idx.cpu().numpy().astype(np.int32))
            all_logits.append(topk_vals.cpu().to(torch.float16).numpy())
            all_positions.append(pos - needed_per_batch)

        if (batch_idx + 1) % 4 == 0:
            elapsed = time.time() - t0
            tok_per_s = (batch_idx + 1) * seq_len / elapsed
            print(f"    Batch {batch_idx+1}/{n_batches}: {tok_per_s:.0f} tok/s", flush=True)

    # Stack: (n_batches, seq_len, top_k)
    indices = np.stack(all_indices, axis=0)
    logits_arr = np.stack(all_logits, axis=0)
    positions = np.array(all_positions, dtype=np.int64)

    # Save
    np.savez_compressed(
        str(out_path),
        indices=indices,
        logits=logits_arr,
        positions=positions,
    )

    elapsed = time.time() - t0
    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"  Saved {out_path.name}: {indices.shape} indices + logits, "
          f"{size_mb:.1f} MB, {elapsed:.1f}s")


def main():
    parser = argparse.ArgumentParser(description="Pre-compute teacher logits")
    parser.add_argument("--shard-start", type=int, default=0)
    parser.add_argument("--shard-end", type=int, default=54)
    parser.add_argument("--data-dir", type=str,
                        default="/Users/mwhitford/data/fractal-bitnet/shards-qwen3")
    parser.add_argument("--out-dir", type=str, default="data/teacher-logits")
    parser.add_argument("--seq-len", type=int, default=4096)
    parser.add_argument("--n-batches", type=int, default=12,
                        help="Batches per shard (12 × 4096 = ~50K tokens)")
    parser.add_argument("--top-k", type=int, default=64)
    parser.add_argument("--temperature", type=float, default=2.0)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    data_dir = Path(args.data_dir)
    shards = sorted(data_dir.glob("shard_*.npy"))
    shards = shards[args.shard_start:args.shard_end]

    print(f"\n{'='*70}")
    print(f"  Pre-compute Teacher Logits")
    print(f"  Teacher: {TEACHER_NAME}")
    print(f"  Shards: {args.shard_start}–{args.shard_end} ({len(shards)} shards)")
    print(f"  seq_len={args.seq_len}  n_batches={args.n_batches}  top_k={args.top_k}")
    print(f"  Output: {out_dir}/")
    print(f"{'='*70}")

    model, _tokenizer = load_teacher()

    t0_total = time.time()
    for i, shard_path in enumerate(shards):
        shard_id = int(shard_path.stem.split("_")[1])
        out_path = out_dir / f"teacher_shard_{shard_id:05d}.npz"

        if out_path.exists():
            print(f"\n  [{i+1}/{len(shards)}] Shard {shard_id}: already exists, skipping")
            continue

        print(f"\n  [{i+1}/{len(shards)}] Shard {shard_id}: {shard_path.name}")
        process_shard(
            model, shard_path, out_path,
            seq_len=args.seq_len,
            n_batches=args.n_batches,
            top_k=args.top_k,
            temperature=args.temperature,
        )

    elapsed = time.time() - t0_total
    print(f"\n  Total: {elapsed:.0f}s ({elapsed/60:.1f} min)")
    print(f"  Output: {out_dir}/")


if __name__ == "__main__":
    main()
