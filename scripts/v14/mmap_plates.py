"""mmap-backed plate storage — no checkpoints needed.

The plate files on disk ARE the training state. Every TD flip writes
directly to the mmap'd delta file. Every Adam step writes directly to
the mmap'd gamma file. The OS page cache handles persistence.

Crash at any point → restart from the mmap'd files. Zero explicit saves.
Resume in < 1 second (just mmap + read state.json).

File layout:
    training/
    ├── base.plate        # mmap readonly  — frozen teacher etch
    ├── delta.plate        # mmap r+        — TD writes flips here
    ├── gamma.f32         # mmap r+        — per-channel scales
    ├── adam_m.f32        # mmap r+        — Adam first moment
    ├── adam_v.f32        # mmap r+        — Adam second moment
    ├── state.json        # tiny metadata, written every log_interval
    └── folds/
        └── fold_NNN.json # one file per fold event

Usage:
    from mmap_plates import MmapPlateStore

    store = MmapPlateStore("training/")
    store.initialize_from_extraction("checkpoints/v14-extracted/model.npz")

    # Training loop — no saves needed
    for step in range(steps):
        delta_mx = store.get_delta_mx(module_name)  # read from mmap
        ...training step...
        store.apply_flips(module_name, flip_indices, new_values)  # write to mmap
        store.update_gamma(module_name, new_gamma)  # write to mmap

    # Fold when delta plateaus
    store.fold(module_name)  # base × delta → new base, reset delta

License: MIT
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

try:
    import mlx.core as mx
    HAS_MLX = True
except ImportError:
    HAS_MLX = False


# ══════════════════════════════════════════════════════════════════════
# Ternary packing — same as td.py but pure numpy for mmap
# ══════════════════════════════════════════════════════════════════════

def pack_ternary_np(w: np.ndarray) -> np.ndarray:
    """Pack int8 {-1, 0, +1} → uint32 (2 bits per value, 16 values per word).

    Encoding: +1 → 0b00, 0 → 0b01, -1 → 0b10
    """
    flat = w.reshape(-1)
    # Pad to multiple of 16
    pad_len = (16 - len(flat) % 16) % 16
    if pad_len:
        flat = np.concatenate([flat, np.ones(pad_len, dtype=np.int8)])

    # Encode: +1→0, 0→1, -1→2
    encoded = np.where(flat == 1, 0, np.where(flat == 0, 1, 2)).astype(np.uint32)

    # Pack 16 values per uint32
    packed = np.zeros(len(encoded) // 16, dtype=np.uint32)
    for i in range(16):
        packed |= encoded[i::16] << (i * 2)
    return packed


def unpack_ternary_np(packed: np.ndarray, shape: tuple[int, ...]) -> np.ndarray:
    """Unpack uint32 → int8 {-1, 0, +1}."""
    total = 1
    for s in shape:
        total *= s

    flat = np.zeros(len(packed) * 16, dtype=np.int8)
    for i in range(16):
        bits = ((packed >> (i * 2)) & 0b11).astype(np.int8)
        flat[i::16] = np.where(bits == 0, 1, np.where(bits == 1, 0, -1))

    return flat[:total].reshape(shape)


def flip_packed_position(packed: np.ndarray, position: int, new_value: int):
    """Flip a single ternary position in a packed uint32 array.

    position: flat index into the unpacked array
    new_value: -1, 0, or +1
    """
    word_idx = position // 16
    bit_offset = (position % 16) * 2

    # Encode new value
    encoded = 0 if new_value == 1 else (1 if new_value == 0 else 2)

    # Read-modify-write the uint32
    mask = ~(np.uint32(0b11) << np.uint32(bit_offset))
    packed[word_idx] = (packed[word_idx] & mask) | (np.uint32(encoded) << np.uint32(bit_offset))


# ══════════════════════════════════════════════════════════════════════
# MmapPlate — one mmap'd plate file
# ══════════════════════════════════════════════════════════════════════

@dataclass
class MmapPlate:
    """A single mmap'd ternary plate file.

    Wraps a numpy memmap of packed uint32. The file on disk IS the
    plate — no serialization, no intermediate representation.
    """
    path: Path
    shape: tuple[int, ...]  # unpacked shape (out_features, in_features)
    packed_shape: tuple[int, ...]  # packed shape
    data: np.ndarray  # the memmap
    mode: str  # 'r' or 'r+'

    @classmethod
    def create(cls, path: Path, shape: tuple[int, ...],
               initial_value: int = 1, mode: str = "r+") -> "MmapPlate":
        """Create a new plate file initialized to a constant value."""
        path.parent.mkdir(parents=True, exist_ok=True)

        total = 1
        for s in shape:
            total *= s
        packed_len = (total + 15) // 16
        packed_shape = (packed_len,)

        # Create and initialize
        init_unpacked = np.full(total, initial_value, dtype=np.int8)
        init_packed = pack_ternary_np(init_unpacked)

        # Write initial data
        init_packed.tofile(str(path))

        # Open as mmap
        data = np.memmap(str(path), dtype=np.uint32, mode=mode,
                         shape=packed_shape)
        return cls(path=path, shape=shape, packed_shape=packed_shape,
                   data=data, mode=mode)

    @classmethod
    def open(cls, path: Path, shape: tuple[int, ...],
             mode: str = "r") -> "MmapPlate":
        """Open an existing plate file."""
        total = 1
        for s in shape:
            total *= s
        packed_len = (total + 15) // 16
        packed_shape = (packed_len,)

        data = np.memmap(str(path), dtype=np.uint32, mode=mode,
                         shape=packed_shape)
        return cls(path=path, shape=shape, packed_shape=packed_shape,
                   data=data, mode=mode)

    @classmethod
    def from_array(cls, path: Path, arr: np.ndarray,
                   mode: str = "r+") -> "MmapPlate":
        """Create a plate file from a numpy array of packed uint32."""
        path.parent.mkdir(parents=True, exist_ok=True)
        arr.tofile(str(path))
        shape = arr.shape  # packed shape
        data = np.memmap(str(path), dtype=np.uint32, mode=mode, shape=shape)
        return cls(path=path, shape=shape, packed_shape=shape,
                   data=data, mode=mode)

    def unpack(self) -> np.ndarray:
        """Unpack to int8 {-1, 0, +1}."""
        return unpack_ternary_np(self.data, self.shape)

    def apply_flips(self, positions: np.ndarray, values: np.ndarray):
        """Apply TD flips directly to the mmap'd file.

        positions: flat indices into the unpacked array
        values: new ternary values (-1, 0, or +1) for each position
        """
        assert self.mode == "r+", "Cannot write to readonly plate"
        for pos, val in zip(positions, values):
            flip_packed_position(self.data, int(pos), int(val))
        # OS handles persistence — dirty pages flushed automatically

    def flush(self):
        """Force OS to flush dirty pages to disk."""
        if hasattr(self.data, 'flush'):
            self.data.flush()

    def stats(self) -> dict[str, float]:
        """Compute delta plate statistics."""
        unpacked = self.unpack()
        total = unpacked.size
        return {
            "keep_frac": float((unpacked == 1).sum()) / total,
            "flip_frac": float((unpacked == -1).sum()) / total,
            "block_frac": float((unpacked == 0).sum()) / total,
            "changed_frac": float((unpacked != 1).sum()) / total,
        }

    def to_mlx(self) -> "mx.array":
        """Convert to MLX array for forward pass."""
        assert HAS_MLX, "MLX not available"
        return mx.array(self.data)

    def close(self):
        """Close the mmap. OS reclaims pages."""
        if self.mode == "r+":
            self.flush()
        del self.data


# ══════════════════════════════════════════════════════════════════════
# MmapFloat — mmap'd float32 file (gamma, Adam moments)
# ══════════════════════════════════════════════════════════════════════

@dataclass
class MmapFloat:
    """mmap'd float32 file for continuous parameters."""
    path: Path
    shape: tuple[int, ...]
    data: np.ndarray
    mode: str

    @classmethod
    def create(cls, path: Path, shape: tuple[int, ...],
               initial_value: float = 0.0,
               mode: str = "r+") -> "MmapFloat":
        """Create a new float32 mmap file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        init = np.full(shape, initial_value, dtype=np.float32)
        init.tofile(str(path))
        data = np.memmap(str(path), dtype=np.float32, mode=mode, shape=shape)
        return cls(path=path, shape=shape, data=data, mode=mode)

    @classmethod
    def open(cls, path: Path, shape: tuple[int, ...],
             mode: str = "r+") -> "MmapFloat":
        """Open an existing float32 mmap file."""
        data = np.memmap(str(path), dtype=np.float32, mode=mode, shape=shape)
        return cls(path=path, shape=shape, data=data, mode=mode)

    def update(self, values: np.ndarray):
        """Write new values to the mmap'd file."""
        assert self.mode == "r+", "Cannot write to readonly file"
        self.data[:] = values

    def flush(self):
        if hasattr(self.data, 'flush'):
            self.data.flush()

    def to_mlx(self) -> "mx.array":
        assert HAS_MLX
        return mx.array(self.data)

    def close(self):
        if self.mode == "r+":
            self.flush()
        del self.data


# ══════════════════════════════════════════════════════════════════════
# MmapPlateStore — manages all plates for training
# ══════════════════════════════════════════════════════════════════════

class MmapPlateStore:
    """Manages mmap'd plate files for continuous training.

    No checkpoints. The files on disk ARE the training state.
    Every TD flip writes directly to the mmap'd delta file.
    Every Adam step writes directly to the mmap'd gamma file.

    Statechart states:
      idle → loaded → training (self-transition) → folding → loaded
    """

    def __init__(self, training_dir: str | Path):
        self.dir = Path(training_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.dir / "folds").mkdir(exist_ok=True)

        self.modules: dict[str, dict] = {}  # module_name → {base, delta, gamma, ...}
        self.state_path = self.dir / "state.json"
        self.state: dict = {}

    def register_module(self, name: str,
                        out_features: int, in_features: int,
                        base_packed: np.ndarray | None = None,
                        gamma: np.ndarray | None = None):
        """Register a DeltaTernaryLinear module with the store.

        If plate files exist, opens them (resume).
        If not, creates them (fresh start).
        """
        shape = (out_features, in_features)
        total = out_features * in_features
        packed_len = (total + 15) // 16
        packed_shape = (packed_len,)

        safe_name = name.replace(".", "_")
        base_path = self.dir / f"{safe_name}_base.plate"
        delta_path = self.dir / f"{safe_name}_delta.plate"
        gamma_path = self.dir / f"{safe_name}_gamma.f32"

        if base_path.exists() and delta_path.exists():
            # Resume: open existing files
            base = MmapPlate.open(base_path, shape, mode="r")
            delta = MmapPlate.open(delta_path, shape, mode="r+")
            gamma_mmap = MmapFloat.open(gamma_path, (out_features,), mode="r+")
            print(f"  [mmap] Resumed {name}: {base_path}")
        else:
            # Fresh: create from extraction
            if base_packed is not None:
                base_path.parent.mkdir(parents=True, exist_ok=True)
                base_packed.tofile(str(base_path))
                base = MmapPlate.open(base_path, shape, mode="r")
            else:
                base = MmapPlate.create(base_path, shape, initial_value=1, mode="r")

            delta = MmapPlate.create(delta_path, shape, initial_value=1, mode="r+")

            if gamma is not None:
                gamma_path.parent.mkdir(parents=True, exist_ok=True)
                gamma.astype(np.float32).tofile(str(gamma_path))
                gamma_mmap = MmapFloat.open(gamma_path, (out_features,), mode="r+")
            else:
                gamma_mmap = MmapFloat.create(gamma_path, (out_features,),
                                               initial_value=1.0, mode="r+")

            print(f"  [mmap] Created {name}: {base_path}")

        self.modules[name] = {
            "base": base,
            "delta": delta,
            "gamma": gamma_mmap,
            "shape": shape,
            "out_features": out_features,
            "in_features": in_features,
        }

    def get_effective_mx(self, name: str) -> "mx.array":
        """Get the effective plate (base ⊙ delta) as MLX array.

        This is what the forward pass uses.
        """
        mod = self.modules[name]
        base_mx = mod["base"].to_mlx()
        delta_mx = mod["delta"].to_mlx()
        # For packed uint32: the multiply happens after unpack in the model
        # Here we just return both for the DeltaTernaryLinear to use
        return base_mx, delta_mx

    def apply_flips(self, name: str, positions: np.ndarray, values: np.ndarray):
        """Apply TD flips directly to the mmap'd delta plate.

        This IS the training step for ternary weights. No save needed.
        The OS handles persistence through the page cache.
        """
        self.modules[name]["delta"].apply_flips(positions, values)

    def update_gamma(self, name: str, new_gamma: np.ndarray):
        """Update gamma (per-channel scales) in the mmap'd file.

        This IS the Adam step for gamma. No save needed.
        """
        self.modules[name]["gamma"].update(new_gamma)

    def fold(self, name: str) -> dict:
        """Fold delta into base. Reset delta to all +1.

        new_base = base ⊙ delta (ternary × ternary = ternary, exact)
        new_delta = all +1

        Atomic: writes new base to temp file, then renames.
        """
        mod = self.modules[name]
        base = mod["base"]
        delta = mod["delta"]

        # Unpack both
        base_unpacked = base.unpack()
        delta_unpacked = delta.unpack()

        # Compute delta stats before fold
        delta_stats = delta.stats()

        # Fold: element-wise multiply
        new_base_unpacked = (base_unpacked.astype(np.int16) *
                             delta_unpacked.astype(np.int16)).astype(np.int8)

        # Repack
        new_base_packed = pack_ternary_np(new_base_unpacked)

        # Atomic write: temp file → rename
        tmp_path = str(base.path) + ".tmp"
        new_base_packed.tofile(tmp_path)
        os.rename(tmp_path, str(base.path))

        # Reset delta to all +1
        ones = np.full(delta_unpacked.shape, 1, dtype=np.int8)
        ones_packed = pack_ternary_np(ones)
        delta.data[:] = ones_packed
        delta.flush()

        # Reopen base (new file content)
        mod["base"].close()
        mod["base"] = MmapPlate.open(base.path, base.shape, mode="r")

        # Record fold event
        fold_dir = self.dir / "folds"
        fold_number = len(list(fold_dir.glob("fold_*.json"))) + 1
        fold_meta = {
            "fold_number": fold_number,
            "module": name,
            "timestamp": time.time(),
            "delta_stats": delta_stats,
        }
        fold_path = fold_dir / f"fold_{fold_number:03d}.json"
        fold_path.write_text(json.dumps(fold_meta, indent=2))

        print(f"  [fold] {name}: changed_frac={delta_stats['changed_frac']:.4f} "
              f"→ folded into base (fold #{fold_number})")

        return fold_meta

    def save_state(self, step: int, **kwargs):
        """Save tiny training state metadata. The ONLY explicit write."""
        self.state = {
            "step": step,
            "timestamp": time.time(),
            "n_folds": len(list((self.dir / "folds").glob("fold_*.json"))),
            "modules": {
                name: mod["delta"].stats()
                for name, mod in self.modules.items()
            },
            **kwargs,
        }
        self.state_path.write_text(json.dumps(self.state, indent=2))

    def load_state(self) -> dict:
        """Load training state from state.json."""
        if self.state_path.exists():
            self.state = json.loads(self.state_path.read_text())
            return self.state
        return {}

    def flush_all(self):
        """Force flush all mmap'd files. Usually not needed."""
        for mod in self.modules.values():
            mod["delta"].flush()
            mod["gamma"].flush()

    def close_all(self):
        """Close all mmap'd files."""
        for mod in self.modules.values():
            mod["base"].close()
            mod["delta"].close()
            mod["gamma"].close()


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

def test_mmap_plates():
    """Test mmap plate store: create, flip, fold, resume."""
    import tempfile
    import shutil

    print("\n" + "=" * 60)
    print("  mmap Plate Store — Self Test")
    print("=" * 60)

    tmpdir = Path(tempfile.mkdtemp(prefix="mmap_test_"))

    try:
        # ── 1. Create store and register module ──
        print("\n1. Create store and register module...")
        store = MmapPlateStore(tmpdir / "training")
        store.register_module("test_layer", out_features=64, in_features=128)

        # Verify initial state
        mod = store.modules["test_layer"]
        delta_stats = mod["delta"].stats()
        assert delta_stats["keep_frac"] == 1.0, f"Expected all +1, got {delta_stats}"
        print(f"   Delta stats: {delta_stats}")
        print("   ✅ Initial delta is all +1")

        # ── 2. Apply TD flips ──
        print("\n2. Apply TD flips...")
        # Flip 10 positions from +1 to -1
        positions = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90])
        values = np.full(10, -1, dtype=np.int8)
        store.apply_flips("test_layer", positions, values)

        delta_stats = mod["delta"].stats()
        total = 64 * 128
        expected_flip = 10 / total
        print(f"   Delta stats after flips: changed_frac={delta_stats['changed_frac']:.6f}")
        assert delta_stats["flip_frac"] > 0, "Expected some flips"
        print("   ✅ Flips applied to mmap'd delta")

        # ── 3. Save state ──
        print("\n3. Save state...")
        store.save_state(step=100, td_step_count=100)
        print(f"   State saved: {store.state_path}")
        print("   ✅ State persisted")

        # ── 4. Simulate crash and resume ──
        print("\n4. Simulate crash and resume...")
        store.flush_all()
        store.close_all()

        # Reopen — simulates process restart
        store2 = MmapPlateStore(tmpdir / "training")
        store2.register_module("test_layer", out_features=64, in_features=128)

        # Verify flips survived
        delta_stats2 = store2.modules["test_layer"]["delta"].stats()
        print(f"   Delta stats after resume: changed_frac={delta_stats2['changed_frac']:.6f}")
        assert delta_stats2["flip_frac"] == delta_stats["flip_frac"], \
            f"Flips lost! Before: {delta_stats['flip_frac']}, after: {delta_stats2['flip_frac']}"

        # Verify state survived
        state = store2.load_state()
        assert state["step"] == 100, f"Step lost! Expected 100, got {state.get('step')}"
        print("   ✅ Crash recovery: all flips and state survived")

        # ── 5. Fold ──
        print("\n5. Fold delta into base...")
        fold_meta = store2.fold("test_layer")
        print(f"   Fold meta: {fold_meta}")

        # Verify delta is reset to all +1
        delta_stats3 = store2.modules["test_layer"]["delta"].stats()
        assert delta_stats3["keep_frac"] == 1.0, f"Delta not reset! {delta_stats3}"
        print("   ✅ Delta reset to all +1 after fold")

        # Verify base absorbed the flips
        base_unpacked = store2.modules["test_layer"]["base"].unpack()
        # The original base was all +1, flipped positions should now be -1
        for pos in positions:
            flat_idx = pos
            row = flat_idx // 128
            col = flat_idx % 128
            assert base_unpacked[row, col] == -1, \
                f"Position {pos} should be -1 after fold, got {base_unpacked[row, col]}"
        print("   ✅ Base absorbed flips correctly")

        # ── 6. Fold is lossless ──
        print("\n6. Verify fold is lossless...")
        # Apply more flips, fold again
        positions2 = np.array([100, 200, 300])
        values2 = np.full(3, -1, dtype=np.int8)
        store2.apply_flips("test_layer", positions2, values2)
        store2.fold("test_layer")

        # The original flipped positions should still be -1 in base
        base_unpacked2 = store2.modules["test_layer"]["base"].unpack()
        for pos in positions:
            row = pos // 128
            col = pos % 128
            assert base_unpacked2[row, col] == -1, \
                f"Position {pos} should still be -1 after double fold"
        # New positions should also be -1
        for pos in positions2:
            row = pos // 128
            col = pos % 128
            # base was -1 at these positions? No, base was +1 (original),
            # then first fold made positions -1, but positions2 are different positions
            # So base at positions2 was +1, delta flipped to -1, fold → -1
            assert base_unpacked2[row, col] == -1, \
                f"Position {pos} should be -1 after fold"
        print("   ✅ Double fold is lossless")

        # ── Summary ──
        print("\n" + "=" * 60)
        print("  ✅ All tests passed!")
        print("=" * 60)

        store2.close_all()

    finally:
        shutil.rmtree(tmpdir)


if __name__ == "__main__":
    test_mmap_plates()
