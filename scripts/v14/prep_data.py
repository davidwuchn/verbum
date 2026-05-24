#!/usr/bin/env python3
"""Tokenize Dolma parquet data with Qwen3.6-27B tokenizer for v14 training.

Reads raw Dolma parquet files, tokenizes each document with the
Qwen3.6-27B tokenizer (vocab 248,320), packs into 50M-token numpy
shards (int32).

Input:  ~/data/fractal-bitnet/dolma-raw/*.parquet
Output: ~/data/fractal-bitnet/shards-qwen36/shard_NNNNN.npy

Usage:
    cd ~/src/verbum
    uv run python scripts/v14/prep_data.py [--target-tokens 3_000_000_000]

License: MIT
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

# ═══════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════

RAW_DIR = Path(os.path.expanduser("~/data/fractal-bitnet/dolma-raw"))
OUT_DIR = Path(os.path.expanduser("~/data/fractal-bitnet/shards-qwen36"))

TOKENIZER_MODEL = "Qwen/Qwen3.6-27B"
SHARD_SIZE = 50_000_000   # tokens per shard
TARGET_TOKENS = 3_000_000_000  # 3B tokens
PARQUET_BATCH_SIZE = 1000


# ═══════════════════════════════════════════════════════════════════
# Tokenizer
# ═══════════════════════════════════════════════════════════════════

_tokenizer = None

def load_tokenizer():
    """Load Qwen3.6-27B tokenizer (only once)."""
    global _tokenizer
    if _tokenizer is None:
        from transformers import AutoTokenizer
        print(f"Loading tokenizer: {TOKENIZER_MODEL}")
        _tokenizer = AutoTokenizer.from_pretrained(
            TOKENIZER_MODEL, trust_remote_code=True)
        print(f"  vocab_size: {_tokenizer.vocab_size}")
        print(f"  eos_token_id: {_tokenizer.eos_token_id}")
    return _tokenizer


def encode_document(text: str) -> list[int]:
    """Tokenize a document and append EOD token."""
    tok = load_tokenizer()
    ids = tok.encode(text, add_special_tokens=False)
    # Append EOS as document separator
    ids.append(tok.eos_token_id)
    return ids


# ═══════════════════════════════════════════════════════════════════
# Shard writer
# ═══════════════════════════════════════════════════════════════════

class ShardWriter:
    """Accumulates token IDs and writes fixed-size .npy shards."""

    def __init__(self, out_dir: Path, shard_size: int, target_tokens: int):
        self.out_dir = out_dir
        self.shard_size = shard_size
        self.target_tokens = target_tokens

        self.buffer = np.zeros(shard_size, dtype=np.int32)
        self.buf_pos = 0
        self.shard_idx = 0
        self.total_tokens = 0
        self.total_docs = 0
        self.done = False

        out_dir.mkdir(parents=True, exist_ok=True)

    def add_document(self, token_ids: list[int]) -> bool:
        """Add tokenized document. Returns True if target reached."""
        if self.done:
            return True

        for tid in token_ids:
            self.buffer[self.buf_pos] = tid
            self.buf_pos += 1
            self.total_tokens += 1

            if self.buf_pos >= self.shard_size:
                self._flush()

            if self.total_tokens >= self.target_tokens:
                if self.buf_pos > 0:
                    self._flush()
                self.done = True
                return True

        self.total_docs += 1
        return False

    def _flush(self):
        path = self.out_dir / f"shard_{self.shard_idx:05d}.npy"
        np.save(path, self.buffer[:self.buf_pos])
        self.shard_idx += 1
        self.buffer = np.zeros(self.shard_size, dtype=np.int32)
        self.buf_pos = 0

    def finalize(self):
        if self.buf_pos > 0:
            self._flush()


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Tokenize Dolma with Qwen3.6-27B")
    parser.add_argument("--target-tokens", type=int, default=TARGET_TOKENS)
    parser.add_argument("--raw-dir", type=str, default=str(RAW_DIR))
    parser.add_argument("--out-dir", type=str, default=str(OUT_DIR))
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    out_dir = Path(args.out_dir)

    # Find parquet files
    parquet_files = sorted(raw_dir.glob("*.parquet"))
    if not parquet_files:
        print(f"ERROR: No .parquet files found in {raw_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"{'='*72}")
    print(f"  Dolma → Qwen3.6-27B tokenization")
    print(f"  Source: {raw_dir} ({len(parquet_files)} parquet files)")
    print(f"  Output: {out_dir}")
    print(f"  Target: {args.target_tokens:,} tokens")
    print(f"  Shard size: {SHARD_SIZE:,} tokens")
    print(f"  Expected shards: {args.target_tokens // SHARD_SIZE}")
    print(f"{'='*72}")

    # Load tokenizer (triggers download if needed)
    tok = load_tokenizer()
    vocab_size = tok.vocab_size
    eod_id = tok.eos_token_id

    writer = ShardWriter(out_dir, SHARD_SIZE, args.target_tokens)
    errors_skipped = 0
    t_start = time.time()

    try:
        import pyarrow.parquet as pq
    except ImportError:
        print("ERROR: pyarrow required. Install: uv pip install pyarrow", file=sys.stderr)
        sys.exit(1)

    for fi, pf in enumerate(parquet_files):
        if writer.done:
            break

        print(f"\n[{fi+1}/{len(parquet_files)}] {pf.name}...", flush=True)
        table = pq.read_table(pf, columns=["text"])

        for batch_start in range(0, len(table), PARQUET_BATCH_SIZE):
            if writer.done:
                break

            batch_end = min(batch_start + PARQUET_BATCH_SIZE, len(table))
            batch = table.slice(batch_start, batch_end - batch_start)
            texts = batch.column("text").to_pylist()

            for text in texts:
                if writer.done:
                    break

                if not text or len(text.strip()) < 10:
                    continue

                try:
                    ids = encode_document(text)
                    writer.add_document(ids)
                except Exception:
                    errors_skipped += 1
                    continue

            # Progress
            elapsed = time.time() - t_start
            tps = writer.total_tokens / max(elapsed, 1)
            pct = 100 * writer.total_tokens / args.target_tokens
            print(f"  {writer.total_tokens:,} tokens ({pct:.1f}%) | "
                  f"{writer.total_docs:,} docs | "
                  f"{writer.shard_idx} shards | "
                  f"{tps:,.0f} tok/s | "
                  f"{elapsed:.0f}s", end="\r", flush=True)

    writer.finalize()
    elapsed = time.time() - t_start

    # Write metadata
    meta = {
        "tokenizer": "Qwen3.6-BBPE",
        "tokenizer_model": TOKENIZER_MODEL,
        "vocab_size": vocab_size,
        "eod_id": eod_id,
        "source": str(raw_dir),
        "source_files": len(parquet_files),
        "shards_written": writer.shard_idx,
        "shard_size": SHARD_SIZE,
        "total_tokens": writer.total_tokens,
        "total_documents": writer.total_docs,
        "target_tokens": args.target_tokens,
        "errors_skipped": errors_skipped,
        "elapsed_seconds": round(elapsed, 1),
        "tokens_per_second": round(writer.total_tokens / max(elapsed, 1)),
        "timestamp": datetime.now(UTC).isoformat(),
        "dtype": "int32",
    }
    (out_dir / "prep_status.json").write_text(json.dumps(meta, indent=2))

    print(f"\n\n{'='*72}")
    print(f"  Done!")
    print(f"  {writer.total_tokens:,} tokens in {writer.shard_idx} shards")
    print(f"  {writer.total_docs:,} documents ({errors_skipped} errors skipped)")
    print(f"  {elapsed:.0f}s ({writer.total_tokens / max(elapsed, 1):,.0f} tok/s)")
    print(f"  Output: {out_dir}")
    print(f"{'='*72}")


if __name__ == "__main__":
    main()
