"""
v13 Data Pipeline — Qwen3-tokenized Dolma shards for causal LM training.

Shards: /Users/mwhitford/data/fractal-bitnet/shards-qwen3/shard_NNNNN.npy
Format: flat int32 arrays, 50M tokens each, 60 shards, 3B total.
Tokenizer: Qwen3 BBPE (vocab 151936, EOD=151643).

License: MIT
"""

from __future__ import annotations

from pathlib import Path

import numpy as np


class ShardedDataLoader:
    """Streams (input_ids, targets) from pre-tokenized Dolma shards.

    Each call to next_batch() returns:
      input_ids: (batch_size, seq_len) int32
      targets:   (batch_size, seq_len) int32  (shifted by 1)

    Loads one shard at a time via mmap. Advances to the next shard
    when the current one is exhausted.
    """

    def __init__(
        self,
        data_dir: str | Path,
        batch_size: int,
        seq_len: int,
        shard_start: int = 0,
        shard_end: int = 54,
        seed: int = 42,
    ):
        self.data_dir = Path(data_dir)
        self.batch_size = batch_size
        self.seq_len = seq_len

        # Discover shards
        all_shards = sorted(self.data_dir.glob("shard_*.npy"))
        self.shards = all_shards[shard_start:shard_end]
        assert len(self.shards) > 0, (
            f"No shards found in {self.data_dir} "
            f"(range {shard_start}:{shard_end})"
        )

        self.rng = np.random.RandomState(seed)
        self.current_shard_idx = 0
        self.position = 0
        self.current_data: np.ndarray | None = None
        self._load_shard(0)

    def _load_shard(self, idx: int) -> None:
        self.current_shard_idx = idx % len(self.shards)
        self.current_data = np.load(
            self.shards[self.current_shard_idx], mmap_mode="r"
        ).astype(np.int64)
        self.position = 0

    def next_batch(self) -> tuple[np.ndarray, np.ndarray]:
        """Returns (input_ids, targets) each of shape (batch_size, seq_len)."""
        B, T = self.batch_size, self.seq_len
        needed = B * (T + 1)  # +1 for the target shift

        if self.current_data is None or self.position + needed > len(self.current_data):
            self._load_shard(self.current_shard_idx + 1)

        buf = self.current_data[self.position : self.position + needed]
        self.position += needed

        buf = buf.reshape(B, T + 1)
        input_ids = buf[:, :T].astype(np.int32)
        targets = buf[:, 1 : T + 1].astype(np.int32)

        return input_ids, targets

    def save_state(self) -> dict:
        """Save loader position for checkpoint resume."""
        return {
            "shard_idx": self.current_shard_idx,
            "position": self.position,
        }

    def load_state(self, state: dict) -> None:
        """Restore loader position from checkpoint."""
        shard_idx = state.get("shard_idx", 0)
        position = state.get("position", 0)
        self._load_shard(shard_idx)
        self.position = min(position, len(self.current_data) - 1)

    def __iter__(self):
        return self

    def __next__(self) -> tuple[np.ndarray, np.ndarray]:
        return self.next_batch()


class MixedDataLoader:
    """Mixes prose (Dolma shards) with structured data (BIOS/lambda shard).

    Per-batch random draw: with probability mix_ratio, draw from
    structured data; otherwise draw from prose. This gives the kernel
    dispatch structured targets (math, lambda, clojure) to latch onto
    while the bulk prose training drives overall LM quality.

    The structured shard is smaller and wraps around (repeats).
    """

    def __init__(
        self,
        prose_loader: ShardedDataLoader,
        structured_path: str | Path,
        mix_ratio: float = 0.1,
        seq_len: int = 4096,
        batch_size: int = 2,
        seed: int = 42,
    ):
        self.prose = prose_loader
        self.mix_ratio = mix_ratio
        self.seq_len = seq_len
        self.batch_size = batch_size
        self.rng = np.random.RandomState(seed)

        # Load structured shard
        structured_path = Path(structured_path)
        assert structured_path.exists(), f"Structured shard not found: {structured_path}"
        self.structured_data = np.load(str(structured_path), mmap_mode="r").astype(np.int64)
        self.structured_pos = 0

    def _next_structured(self) -> tuple[np.ndarray, np.ndarray]:
        """Draw a batch from the structured shard, wrapping if needed."""
        B, T = self.batch_size, self.seq_len
        needed = B * (T + 1)

        if self.structured_pos + needed > len(self.structured_data):
            self.structured_pos = 0  # wrap around

        buf = self.structured_data[self.structured_pos : self.structured_pos + needed]
        self.structured_pos += needed

        buf = np.array(buf).reshape(B, T + 1)
        input_ids = buf[:, :T].astype(np.int32)
        targets = buf[:, 1 : T + 1].astype(np.int32)
        return input_ids, targets

    def next_batch(self) -> tuple[np.ndarray, np.ndarray]:
        """Returns (input_ids, targets). Randomly picks prose or structured."""
        if self.rng.random() < self.mix_ratio:
            return self._next_structured()
        else:
            return self.prose.next_batch()

    def save_state(self) -> dict:
        """Save both loader positions for checkpoint resume."""
        return {
            **self.prose.save_state(),
            "structured_pos": self.structured_pos,
        }

    def load_state(self, state: dict) -> None:
        """Restore both loader positions from checkpoint."""
        self.prose.load_state(state)
        self.structured_pos = state.get("structured_pos", 0)

    def __iter__(self):
        return self

    def __next__(self) -> tuple[np.ndarray, np.ndarray]:
        return self.next_batch()


# ══════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    from config import V13Config
    cfg = V13Config()

    print(f"Data dir: {cfg.data_dir}")
    print(f"Seq len: {cfg.seq_len}, Batch size: {cfg.batch_size}")

    loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=cfg.batch_size,
        seq_len=cfg.seq_len,
        shard_start=0,
        shard_end=cfg.n_train_shards,
    )
    print(f"Shards: {len(loader.shards)}")

    input_ids, targets = next(loader)
    print(f"input_ids: {input_ids.shape}, dtype={input_ids.dtype}")
    print(f"targets:   {targets.shape}, dtype={targets.dtype}")
    print(f"First 10 tokens: {input_ids[0, :10]}")
    print(f"First 10 targets: {targets[0, :10]}")

    # Verify shift
    assert (input_ids[0, 1:10] == targets[0, :9]).all(), "Shift mismatch!"
    print("Shift verified ✓")

    # Decode a sample
    try:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
        text = tok.decode(input_ids[0, :100].tolist())
        print(f"\nSample text (first 100 tokens):\n{text[:300]}")
    except Exception as e:
        print(f"(tokenizer not available for decode: {e})")

    # Test multiple batches
    for i in range(5):
        ids, tgts = next(loader)
    print(f"\n5 batches read, position={loader.position:,}")

    print("\ndata.py self-test: all ok ✓")
