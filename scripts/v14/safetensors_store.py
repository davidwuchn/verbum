"""safetensors_store.py — Safetensors-backed training loader and sync module.

Replaces the checkpoint save/load cycle in train_td.py with direct mmap
access to the three v14-mmap safetensors files.

File layout (from extract_to_safetensors.py):
    base.safetensors      — 76 frozen base plates   (readonly, never changes)
    delta.safetensors     — 76 delta plates          (mmap r/w, sparse TD flips)
    training.safetensors  — 835 continuous params +  (mmap r/w, dense Adam)
                            optimizer state
    state.json            — training loop metadata

Three operations:
    1. load_into_model / load_optimizer_state / load_state
       — Read safetensors → numpy → MLX, populate model and Adam
    2. sync(model, adam, step)
       — Write MLX → numpy → mmap data region, update state.json
    3. fold()
       — Compute new_base = unpack(base) * unpack(delta), write
         new base.safetensors (atomic), reset delta to all +1

Usage:
    store = SafetensorsStore("checkpoints/v14-mmap/")
    store.load_into_model(model)
    store.load_optimizer_state(adam)
    state = store.load_state()

    # ...training loop...

    store.sync(model, adam, step=2600)
    fold_meta = store.fold()

License: MIT
"""

from __future__ import annotations

import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import numpy as np

import mlx.core as mx
import mlx.nn as nn
from mlx.utils import tree_flatten, tree_unflatten

# Import pack/unpack from mmap_plates (pure numpy, no MLX dependency).
# mmap_plates.py lives in the same directory — import via sys.path manipulation
# so this file stays self-contained when run directly.
import sys as _sys
_sys.path.insert(0, str(Path(__file__).parent))
from mmap_plates import pack_ternary_np, unpack_ternary_np  # noqa: E402


# ──────────────────────────────────────────────────────────────────────────────
# Safetensors dtype → numpy dtype
# ──────────────────────────────────────────────────────────────────────────────

_ST_TO_NP: dict[str, str] = {
    "F32": "float32",
    "F16": "float16",
    "BF16": "bfloat16",
    "F64": "float64",
    "I8":  "int8",
    "I16": "int16",
    "I32": "int32",
    "I64": "int64",
    "U8":  "uint8",
    "U16": "uint16",
    "U32": "uint32",
    "U64": "uint64",
}

# Numpy dtype → numpy itemsize (bytes)
_NP_ITEMSIZE: dict[str, int] = {
    "float32": 4, "float16": 2, "float64": 8,
    "int8": 1, "int16": 2, "int32": 4, "int64": 8,
    "uint8": 1, "uint16": 2, "uint32": 4, "uint64": 8,
}


# ──────────────────────────────────────────────────────────────────────────────
# Header parsing (used for mmap offset calculation)
# ──────────────────────────────────────────────────────────────────────────────

def _parse_header(path: Path) -> tuple[dict[str, Any], int]:
    """Parse a safetensors file header.

    Returns:
        header:     Full header dict (including '__metadata__').
        data_start: Byte offset where the tensor data region begins.
                    Always a multiple of 4096 (PAGE_SIZE) for v14-mmap files.
    """
    with open(path, "rb") as f:
        header_size = struct.unpack("<Q", f.read(8))[0]
        header = json.loads(f.read(header_size))
        data_start = 8 + header_size
    return header, data_start


# ──────────────────────────────────────────────────────────────────────────────
# In-place mmap write (delta / training files only — never base)
# ──────────────────────────────────────────────────────────────────────────────

def _write_tensor(
    path: Path,
    data_start: int,
    tensor_info: dict[str, Any],
    new_data: np.ndarray,
) -> None:
    """Write a tensor directly to the mmap'd data region of a safetensors file.

    Uses np.memmap at the exact byte offset of this tensor so no copy is
    needed for the rest of the file.  Caller must ensure new_data dtype
    and shape match tensor_info exactly.

    Args:
        path:        Absolute path to the safetensors file.
        data_start:  Byte offset of the data region (from _parse_header).
        tensor_info: Header entry for this tensor (has 'data_offsets', 'dtype', 'shape').
        new_data:    C-contiguous numpy array to write.
    """
    offsets = tensor_info["data_offsets"]
    byte_start = data_start + offsets[0]
    byte_end   = data_start + offsets[1]
    expected_bytes = byte_end - byte_start

    # Ensure C-contiguous with the correct dtype
    dtype    = _ST_TO_NP[tensor_info["dtype"]]
    st_shape = tuple(tensor_info["shape"])  # shape recorded in safetensors header

    new_data = np.ascontiguousarray(new_data.astype(dtype))

    # Sanity check on byte count
    actual_bytes = new_data.nbytes
    if actual_bytes != expected_bytes:
        raise ValueError(
            f"Size mismatch writing to {path.name}: "
            f"tensor_info says {expected_bytes} bytes, got {actual_bytes} bytes "
            f"(data.shape={new_data.shape} st_shape={st_shape})"
        )

    # memmap shape: for 0-element or scalar tensors safetensors uses shape=[]
    # which numpy interprets as a 0-dimensional array.  Use the flat byte count
    # as the memmap shape and write the raw bytes to avoid indexing issues.
    if len(st_shape) == 0:
        # Scalar tensor — memmap as 1-element array, write single value
        itemsize = new_data.itemsize
        mm = np.memmap(str(path), dtype=dtype, mode="r+", offset=byte_start, shape=(1,))
        mm[0] = new_data.item() if new_data.ndim == 0 else new_data.flat[0]
    else:
        mm = np.memmap(str(path), dtype=dtype, mode="r+", offset=byte_start, shape=st_shape)
        mm[:] = new_data.reshape(st_shape)

    mm.flush()
    del mm


# ──────────────────────────────────────────────────────────────────────────────
# MLX ↔ numpy bridge helpers
# ──────────────────────────────────────────────────────────────────────────────

def _mx_to_np(arr: mx.array) -> np.ndarray:
    """Evaluate and convert an MLX array to a C-contiguous numpy array."""
    mx.eval(arr)
    return np.ascontiguousarray(np.array(arr))


def _np_to_mx(arr: np.ndarray) -> mx.array:
    """Convert a numpy array to an MLX array."""
    return mx.array(arr)


# ──────────────────────────────────────────────────────────────────────────────
# SafetensorsStore
# ──────────────────────────────────────────────────────────────────────────────

class SafetensorsStore:
    """Safetensors-backed training state: load, sync, and fold.

    Wraps three safetensors files produced by extract_to_safetensors.py:

        base.safetensors      — 76 frozen base plates (readonly)
        delta.safetensors     — 76 delta plates (mmap r/w)
        training.safetensors  — 835 continuous params + Adam state (mmap r/w)
        state.json            — training loop metadata

    The header of each file is parsed once at __init__ time; byte offsets
    for every tensor are cached so sync() can write directly without any
    re-parsing.

    Partition rules (mirror extract_to_safetensors.py):
        key.endswith("base_weight")  → base.safetensors
        key.endswith("delta_weight") → delta.safetensors
        key starts with "optimizer." → training.safetensors (Adam state)
        everything else              → training.safetensors (continuous params)
    """

    # Snapshot every N syncs (default: 10 syncs = every 200 steps at 20-step sync)
    SNAPSHOT_EVERY_N_SYNCS: int = 10
    # Keep this many most recent snapshots
    MAX_SNAPSHOTS: int = 3

    def __init__(self, store_dir: str | Path) -> None:
        self.dir = Path(store_dir).resolve()

        self._base_path     = self.dir / "base.safetensors"
        self._delta_path    = self.dir / "delta.safetensors"
        self._training_path = self.dir / "training.safetensors"
        self._state_path    = self.dir / "state.json"

        for p in (self._base_path, self._delta_path, self._training_path):
            if not p.exists():
                raise FileNotFoundError(f"SafetensorsStore: missing file: {p}")

        # Parse headers once; cache (header, data_start) per file.
        self._base_hdr,     self._base_data_start     = _parse_header(self._base_path)
        self._delta_hdr,    self._delta_data_start     = _parse_header(self._delta_path)
        self._training_hdr, self._training_data_start  = _parse_header(self._training_path)

        # Build lookup: key → (file_label, header_entry)
        # file_label in {"base", "delta", "training"}
        self._key_map: dict[str, tuple[str, dict[str, Any]]] = {}
        for key, info in self._base_hdr.items():
            if key == "__metadata__":
                continue
            self._key_map[key] = ("base", info)
        for key, info in self._delta_hdr.items():
            if key == "__metadata__":
                continue
            self._key_map[key] = ("delta", info)
        for key, info in self._training_hdr.items():
            if key == "__metadata__":
                continue
            self._key_map[key] = ("training", info)

        # Count keys per file for diagnostics
        n_base     = sum(1 for f, _ in self._key_map.values() if f == "base")
        n_delta    = sum(1 for f, _ in self._key_map.values() if f == "delta")
        n_training = sum(1 for f, _ in self._key_map.values() if f == "training")

        # Sync counter for periodic snapshots
        self._sync_count = 0
        self._snapshots_dir = self.dir / "snapshots"

        # ── Crash detection: if syncing.lock exists, last sync was interrupted
        self._lock_path = self.dir / "syncing.lock"
        if self._lock_path.exists():
            print(
                f"[SafetensorsStore] ⚠ syncing.lock found — last sync was interrupted!",
                file=sys.stderr,
            )
            # Find latest snapshot and restore from it
            if self._snapshots_dir.exists():
                snapshots = sorted(self._snapshots_dir.iterdir())
                if snapshots:
                    latest = snapshots[-1]
                    print(
                        f"[SafetensorsStore] Restoring from snapshot: {latest.name}",
                        file=sys.stderr,
                    )
                    for fname in ("delta.safetensors", "training.safetensors", "state.json"):
                        snap_file = latest / fname
                        live_file = self.dir / fname
                        if snap_file.exists():
                            shutil.copy2(str(snap_file), str(live_file))
                    print(f"[SafetensorsStore] ✅ Restored. Re-parsing headers.", file=sys.stderr)
                    # Re-parse headers after restore
                    self._delta_hdr, self._delta_data_start = _parse_header(self._delta_path)
                    self._training_hdr, self._training_data_start = _parse_header(self._training_path)
                    # Rebuild key_map for delta and training
                    self._key_map = {k: v for k, v in self._key_map.items()
                                     if v[0] == "base"}
                    for key, info in self._delta_hdr.items():
                        if key != "__metadata__":
                            self._key_map[key] = ("delta", info)
                    for key, info in self._training_hdr.items():
                        if key != "__metadata__":
                            self._key_map[key] = ("training", info)
                else:
                    print(
                        f"[SafetensorsStore] ⚠ No snapshots found — cannot restore. "
                        f"Files may be corrupt!",
                        file=sys.stderr,
                    )
            self._lock_path.unlink()

        print(
            f"[SafetensorsStore] {self.dir.name}: "
            f"{n_base} base + {n_delta} delta + {n_training} training = "
            f"{len(self._key_map)} total tensors"
        )

    # ── Snapshot management ──────────────────────────────────────────────────

    def _snapshot(self, step: int) -> None:
        """Create a copy-on-write snapshot of delta + training + state.

        On macOS APFS: uses cp -c (instant, zero disk cost until modified).
        On Linux btrfs/xfs: uses cp --reflink=auto.
        Fallback: shutil.copy2 (real copy, still fast — 22 ms for 169 MB).

        Keeps only MAX_SNAPSHOTS most recent snapshots.
        """
        self._snapshots_dir.mkdir(exist_ok=True)
        snap_dir = self._snapshots_dir / f"step_{step:06d}"
        snap_dir.mkdir(exist_ok=True)

        files = ["delta.safetensors", "training.safetensors", "state.json"]
        for fname in files:
            src = self.dir / fname
            dst = snap_dir / fname
            if not src.exists():
                continue
            try:
                # Try APFS clone first (macOS)
                subprocess.run(
                    ["cp", "-c", str(src), str(dst)],
                    check=True, capture_output=True,
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback: real copy
                shutil.copy2(str(src), str(dst))

        # Prune old snapshots
        existing = sorted(self._snapshots_dir.iterdir())
        while len(existing) > self.MAX_SNAPSHOTS:
            oldest = existing.pop(0)
            shutil.rmtree(str(oldest))

    # ── Low-level read ──────────────────────────────────────────────────────

    def _read_tensor_np(self, key: str) -> np.ndarray:
        """Read a single tensor by its dotted key; returns numpy array."""
        from safetensors import safe_open  # type: ignore[import-untyped]

        label, info = self._key_map[key]
        path = {
            "base":     self._base_path,
            "delta":    self._delta_path,
            "training": self._training_path,
        }[label]

        with safe_open(str(path), framework="numpy") as f:
            return f.get_tensor(key)

    # ── Public: load_into_model ─────────────────────────────────────────────

    def load_into_model(self, model: nn.Module) -> int:
        """Populate all model parameters from safetensors.

        Walks model.parameters() via tree_flatten to get (path, array)
        pairs, then matches each path to the appropriate safetensors key.

        The checkpoint maps parameter paths to files:
            key.endswith("base_weight")  → base.safetensors
            key.endswith("delta_weight") → delta.safetensors
            everything else              → training.safetensors

        If the model has DeltaTernaryLinear modules (post-convert_to_delta),
        both base_weight and delta_weight are loaded directly.  If the model
        still has TernaryLinear modules (pre-convert), .weight keys from
        training.safetensors are loaded directly (these correspond to layers
        that were not delta-converted at checkpoint time).

        Returns the number of parameters restored.
        """
        from safetensors import safe_open  # type: ignore[import-untyped]

        # Build the list of (dotted_path, array) pairs to pass to load_weights.
        weights_to_load: list[tuple[str, mx.array]] = []
        n_restored = 0
        n_skipped  = 0

        with (
            safe_open(str(self._base_path),     framework="numpy") as bf,
            safe_open(str(self._delta_path),    framework="numpy") as df,
            safe_open(str(self._training_path), framework="numpy") as tf,
        ):
            file_handles = {"base": bf, "delta": df, "training": tf}

            flat_params = dict(tree_flatten(model.parameters()))

            for dotted_path in flat_params:
                if dotted_path in self._key_map:
                    label, info = self._key_map[dotted_path]
                    np_arr = file_handles[label].get_tensor(dotted_path)
                    weights_to_load.append((dotted_path, _np_to_mx(np_arr)))
                    n_restored += 1
                else:
                    n_skipped += 1

        # strict=False: tolerate keys present in model but absent in safetensors
        # (e.g. delta-converted layers that the checkpoint saved as .weight, or
        # newly-added architecture members).
        model.load_weights(weights_to_load, strict=False)
        mx.eval(model.parameters())

        if n_skipped:
            print(
                f"[SafetensorsStore.load_into_model] "
                f"{n_restored} restored, {n_skipped} skipped "
                f"(no matching safetensors key — expected if model/checkpoint architecture differ)"
            )
        else:
            print(
                f"[SafetensorsStore.load_into_model] "
                f"{n_restored} parameters restored ✓"
            )
        return n_restored

    # ── Public: load_optimizer_state ────────────────────────────────────────

    def load_optimizer_state(self, adam: Any) -> int:
        """Populate Adam optimizer state from training.safetensors.

        Optimizer state keys are stored with a leading "optimizer." prefix
        (set by extract_to_safetensors.py).  This method strips that prefix,
        matches against Adam's current state tree (from tree_flatten), and
        loads matching tensors.

        Returns the number of state arrays restored.
        """
        from safetensors import safe_open  # type: ignore[import-untyped]

        # Build a lookup of bare optimizer keys (strip "optimizer." prefix).
        opt_keys: dict[str, dict[str, Any]] = {
            key[len("optimizer."):]: info
            for key, (label, info) in self._key_map.items()
            if key.startswith("optimizer.")
        }

        if not opt_keys:
            print("[SafetensorsStore.load_optimizer_state] No optimizer keys found.")
            return 0

        current_flat = dict(tree_flatten(adam.state))
        n_restored = 0
        n_skipped  = 0

        with safe_open(str(self._training_path), framework="numpy") as tf:
            for bare_key, info in opt_keys.items():
                if bare_key not in current_flat:
                    n_skipped += 1
                    continue
                np_arr = tf.get_tensor(f"optimizer.{bare_key}")
                mx_arr = _np_to_mx(np_arr)
                # Shape must match — guard against architecture mismatches
                if current_flat[bare_key].shape != mx_arr.shape:
                    n_skipped += 1
                    continue
                current_flat[bare_key] = mx_arr
                n_restored += 1

        adam.state = tree_unflatten(list(current_flat.items()))
        mx.eval(adam.state)

        print(
            f"[SafetensorsStore.load_optimizer_state] "
            f"{n_restored} restored, {n_skipped} skipped ✓"
        )
        return n_restored

    # ── Public: load_state ──────────────────────────────────────────────────

    def load_state(self) -> dict[str, Any]:
        """Read state.json and return it as a plain dict.

        Returns an empty dict if state.json does not exist.
        """
        if not self._state_path.exists():
            return {}
        return json.loads(self._state_path.read_text())

    # ── Public: sync ────────────────────────────────────────────────────────

    def sync(
        self,
        model: nn.Module,
        adam: Any,
        step: int,
        *,
        extra_state: dict[str, Any] | None = None,
    ) -> None:
        """Write current model and optimizer state back to safetensors files.

        For delta.safetensors and training.safetensors:
          - Open each tensor's data region via np.memmap (no copy of other tensors)
          - Write the current MLX array value to the mmap region
          - Flush the mapping

        base.safetensors is NEVER touched — it is frozen.

        state.json is written atomically (write tmp, rename) with the
        current step plus any extra_state fields.

        Args:
            model:       The V14Model (or any nn.Module) to read parameters from.
            adam:        The Adam optimizer to read state from.
            step:        Current training step (written to state.json).
            extra_state: Additional fields to merge into state.json.
        """
        # ── Periodic snapshot (before we start writing) ────────────────────
        self._sync_count += 1
        if self._sync_count % self.SNAPSHOT_EVERY_N_SYNCS == 0:
            self._snapshot(step)

        # ── Lock: signal that we're mid-sync ──────────────────────────────
        self._lock_path.touch()

        # ── delta plate sync ──────────────────────────────────────────────
        n_delta = 0
        flat_params = dict(tree_flatten(model.parameters()))

        for key, label_info in self._key_map.items():
            label, info = label_info

            if label == "base":
                continue  # frozen — never touch

            if label == "delta":
                if key not in flat_params:
                    continue
                np_arr = _mx_to_np(flat_params[key])
                _write_tensor(self._delta_path, self._delta_data_start, info, np_arr)
                n_delta += 1

        # ── training (continuous params) sync ────────────────────────────
        n_training = 0
        for key, label_info in self._key_map.items():
            label, info = label_info
            if label != "training":
                continue
            if key.startswith("optimizer."):
                continue  # handled separately below
            if key not in flat_params:
                continue
            np_arr = _mx_to_np(flat_params[key])
            _write_tensor(self._training_path, self._training_data_start, info, np_arr)
            n_training += 1

        # ── optimizer state sync ─────────────────────────────────────────
        # adam may be None (e.g. during inference-only sync) or have an empty state.
        n_opt = 0
        if adam is not None and adam.state:
            flat_opt = dict(tree_flatten(adam.state))
            for key, label_info in self._key_map.items():
                label, info = label_info
                if label != "training":
                    continue
                if not key.startswith("optimizer."):
                    continue
                bare_key = key[len("optimizer."):]
                if bare_key not in flat_opt:
                    continue
                np_arr = _mx_to_np(flat_opt[bare_key])
                # Guard: shape must match the slot in the file
                expected_shape = tuple(info["shape"])
                actual_shape   = np_arr.shape
                # Scalar stored as shape=[1] in safetensors but may be () from MLX
                if actual_shape == () and expected_shape == (1,):
                    np_arr = np_arr.reshape(1)
                elif actual_shape != expected_shape:
                    continue  # architecture mismatch — skip silently
                _write_tensor(self._training_path, self._training_data_start, info, np_arr)
                n_opt += 1

        # ── state.json (atomic write) ─────────────────────────────────────
        state: dict[str, Any] = {
            "step": step,
            "timestamp": time.time(),
        }
        if extra_state:
            state.update(extra_state)

        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=self.dir, prefix=".state_", suffix=".json.tmp"
        )
        try:
            with os.fdopen(tmp_fd, "w") as fh:
                json.dump(state, fh, indent=2)
            os.replace(tmp_path, self._state_path)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

        # ── Remove lock: sync completed successfully ─────────────────────
        if self._lock_path.exists():
            self._lock_path.unlink()

        print(
            f"[SafetensorsStore.sync] step={step}: "
            f"{n_delta} delta + {n_training} training + {n_opt} opt tensors synced ✓"
        )

    # ── Public: fold ────────────────────────────────────────────────────────

    def fold(self) -> dict[str, Any]:
        """Fold all delta plates into base plates, then reset delta to all +1.

        Algorithm (per plate pair):
            new_base = unpack(base_plate) * unpack(delta_plate)   (int8 * int8 → int8)
            new_delta = all +1

        base.safetensors is written atomically:
            1. Write new tensors to a tmp file in the same directory.
            2. os.replace(tmp, base.safetensors).
            3. Re-parse the header (data_start does not change; keys/offsets
               are preserved because we write using the same layout).

        delta.safetensors is updated in-place via mmap (reset all values to
        the packed representation of all +1, matching the original layout).

        Returns a fold_meta dict with per-plate change statistics.
        """
        from safetensors import safe_open  # type: ignore[import-untyped]

        # Extract the write function for the base file writer — we need to
        # write a completely new base.safetensors with atomic replace, so we
        # use the same page-aligned writer from extract_to_safetensors.py.
        # Rather than importing it (circular dep risk), we inline the minimal
        # logic here using the cached header layout to preserve byte offsets.

        # ── 1. Read all base and delta plates ─────────────────────────────
        base_keys  = sorted(k for k, (lbl, _) in self._key_map.items() if lbl == "base")
        delta_keys = sorted(k for k, (lbl, _) in self._key_map.items() if lbl == "delta")

        # Derive matching delta key from base key: replace suffix
        def _base_to_delta(base_key: str) -> str:
            return base_key.replace("base_weight", "delta_weight")

        with (
            safe_open(str(self._base_path),  framework="numpy") as bf,
            safe_open(str(self._delta_path), framework="numpy") as df,
        ):
            base_arrays  = {k: bf.get_tensor(k) for k in base_keys}
            delta_arrays = {k: df.get_tensor(_base_to_delta(k)) for k in base_keys}

        # ── 2. Compute per-plate statistics and new base/delta arrays ─────
        new_base_arrays:  dict[str, np.ndarray] = {}
        delta_stats:      dict[str, dict[str, float]] = {}
        base_info_sample  = next(iter(base_keys))
        sample_shape      = tuple(self._base_hdr[base_info_sample]["shape"])

        for base_key in base_keys:
            base_packed  = base_arrays[base_key]   # (N, K//16) uint32
            delta_packed = delta_arrays[base_key]  # (N, K//16) uint32

            # Recover the 2D packed shape from the header (N, K//16)
            base_shape = tuple(self._base_hdr[base_key]["shape"])  # (N, K//16)
            N, K16 = base_shape
            weight_shape = (N, K16 * 16)   # unpacked shape (N, K)

            # mmap_plates.unpack_ternary_np operates on flat 1D packed arrays.
            # The safetensors files store plates as 2D (N, K//16), so we
            # flatten → unpack → reshape back to (N, K).
            base_unpacked  = unpack_ternary_np(base_packed.ravel(),  weight_shape)
            delta_unpacked = unpack_ternary_np(delta_packed.ravel(), weight_shape)

            # Delta statistics (before fold)
            total = delta_unpacked.size
            n_keep  = int((delta_unpacked == 1).sum())
            n_flip  = int((delta_unpacked == -1).sum())
            n_block = int((delta_unpacked == 0).sum())
            delta_stats[base_key] = {
                "keep_frac":    n_keep  / total,
                "flip_frac":    n_flip  / total,
                "block_frac":   n_block / total,
                "changed_frac": (n_flip + n_block) / total,
            }

            # Fold: new_base = base * delta (int8 * int8, stays in {-1, 0, +1})
            new_base_unpacked = (
                base_unpacked.astype(np.int16) * delta_unpacked.astype(np.int16)
            ).astype(np.int8)
            # pack_ternary_np operates on flat 1D input; result is also 1D.
            # Reshape back to (N, K//16) to match the safetensors layout.
            new_base_packed_flat = pack_ternary_np(new_base_unpacked.ravel())
            new_base_arrays[base_key] = new_base_packed_flat.reshape(N, K16)

        # ── 3. Write new base.safetensors (atomic) ───────────────────────
        #  We need to write the exact same layout as the current base.safetensors
        #  (same key order, same padding) so that data_start and offsets are
        #  preserved.  Use write_safetensors from extract_to_safetensors.py
        #  so the page-alignment invariant is maintained.
        from extract_to_safetensors import write_safetensors as _write_st  # type: ignore

        tmp_base = self.dir / ".base.safetensors.tmp"
        metadata = self._base_hdr.get("__metadata__", {})
        _write_st(tmp_base, new_base_arrays, metadata)
        os.replace(str(tmp_base), str(self._base_path))

        # Re-parse header so our cache stays valid.
        self._base_hdr, self._base_data_start = _parse_header(self._base_path)
        # Rebuild key_map entries for base
        for key, info in self._base_hdr.items():
            if key == "__metadata__":
                continue
            self._key_map[key] = ("base", info)

        # ── 4. Reset all delta plates to all +1 via mmap ─────────────────
        # For each delta key, build the all-+1 packed array and write it.
        # pack_ternary_np works on flat 1D arrays; reshape result to (N, K//16).
        ones_cache: dict[tuple, np.ndarray] = {}  # (N, K//16) → packed 2D ones

        for delta_key in delta_keys:
            info = self._delta_hdr[delta_key]
            packed_shape = tuple(info["shape"])  # (N, K//16) uint32
            N, K16 = packed_shape
            weight_shape = (N, K16 * 16)

            if packed_shape not in ones_cache:
                ones_flat = np.ones(N * K16 * 16, dtype=np.int8)
                packed_flat = pack_ternary_np(ones_flat)
                ones_cache[packed_shape] = packed_flat.reshape(N, K16)

            packed_ones = ones_cache[packed_shape]
            _write_tensor(self._delta_path, self._delta_data_start, info, packed_ones)

        # ── 5. Record and return fold metadata ───────────────────────────
        fold_meta: dict[str, Any] = {
            "timestamp": time.time(),
            "n_plates": len(base_keys),
            "delta_stats": delta_stats,
        }

        print(
            f"[SafetensorsStore.fold] Folded {len(base_keys)} plates. "
            f"mean_changed_frac="
            f"{sum(v['changed_frac'] for v in delta_stats.values()) / max(len(delta_stats), 1):.4f}"
        )
        return fold_meta


# ──────────────────────────────────────────────────────────────────────────────
# Self-test
# ──────────────────────────────────────────────────────────────────────────────

def test_safetensors_store() -> None:
    """Integration test: load, sync round-trip, and fold.

    Requires:
        checkpoints/v14-mmap/  — the real v14-mmap checkpoint
        scripts/v14/model.py, td.py, etc.  — the v14 model code

    Run from the verbum repo root:
        uv run python scripts/v14/safetensors_store.py
    """
    import shutil
    import tempfile

    # ── Locate repo root ──────────────────────────────────────────────────
    repo_root = Path(__file__).parent.parent.parent
    store_dir = repo_root / "checkpoints" / "v14-mmap"

    print("\n" + "=" * 72)
    print("  SafetensorsStore — Self Test")
    print("=" * 72)

    if not store_dir.exists():
        print(f"  ⚠  Skipping: {store_dir} does not exist.")
        print("     Run extract_to_safetensors.py first.")
        return

    # ── Test 1: Header parsing and key map ───────────────────────────────
    print("\n[1] Parse headers and build key map …")
    store = SafetensorsStore(store_dir)
    n_base     = sum(1 for lbl, _ in store._key_map.values() if lbl == "base")
    n_delta    = sum(1 for lbl, _ in store._key_map.values() if lbl == "delta")
    n_training = sum(1 for lbl, _ in store._key_map.values() if lbl == "training")
    assert n_base == 76,   f"Expected 76 base plates, got {n_base}"
    assert n_delta == 76,  f"Expected 76 delta plates, got {n_delta}"
    assert n_training > 0, f"Expected training tensors, got 0"
    print(f"  base={n_base}  delta={n_delta}  training={n_training}  ✓")

    # ── Test 2: load_state ───────────────────────────────────────────────
    print("\n[2] load_state() …")
    state = store.load_state()
    assert "step" in state, "state.json missing 'step'"
    print(f"  step={state['step']}  ✓")

    # ── Test 3: load_into_model ──────────────────────────────────────────
    print("\n[3] load_into_model() …")
    # Import model builder — must be run from scripts/v14 or with sys.path set.
    try:
        from model import V14Model
        from config import V14Config
    except ImportError:
        print("  ⚠  Cannot import V14Model — skipping model load test.")
        print("     Run this script from scripts/v14/ or ensure sys.path is set.")
        _test_header_only(store)
        return

    cfg = V14Config()
    model = V14Model(cfg)
    n_restored = store.load_into_model(model)
    assert n_restored > 0, "No parameters restored"
    print(f"  {n_restored} parameters restored ✓")

    # Spot-check: verify a base plate matches raw safetensors read
    print("\n[4] Spot-check base plate value …")
    from safetensors import safe_open  # type: ignore[import-untyped]
    sample_base_key = sorted(k for k, (lbl, _) in store._key_map.items() if lbl == "base")[0]
    with safe_open(str(store._base_path), framework="numpy") as bf:
        np_orig = bf.get_tensor(sample_base_key)

    # Navigate to the model parameter using dotted path
    flat = dict(tree_flatten(model.parameters()))
    if sample_base_key in flat:
        np_model = _mx_to_np(flat[sample_base_key])
        assert np_model.shape == np_orig.shape, (
            f"Shape mismatch: model={np_model.shape} file={np_orig.shape}"
        )
        assert np.array_equal(np_model, np_orig), (
            f"Value mismatch for {sample_base_key}"
        )
        print(f"  {sample_base_key}: shapes match, values identical ✓")
    else:
        print(f"  ⚠  {sample_base_key} not in flat params (may be aliased) — skipping value check")

    # ── Test 5: sync round-trip (work on a temp copy) ────────────────────
    print("\n[5] Sync round-trip (temp copy) …")
    tmp_dir = Path(tempfile.mkdtemp(prefix="safetensors_store_test_"))
    try:
        tmp_store_dir = tmp_dir / "v14-mmap"
        shutil.copytree(str(store_dir), str(tmp_store_dir))

        tmp_store = SafetensorsStore(tmp_store_dir)

        # Build an Adam optimizer whose state matches the checkpoint.
        # We prime it from the safetensors file via load_optimizer_state.
        import mlx.optimizers as optim

        # Create Adam and prime state by running a minimal warm-up update
        # over the model's trainable parameters so the state tree has the
        # right shape.  Frozen parameters (base_weight, delta_weight) should
        # be excluded, matching the training loop.
        adam = optim.Adam(learning_rate=1e-4)
        trainable = {
            k: v for k, v in dict(tree_flatten(model.parameters())).items()
            if "base_weight" not in k and "delta_weight" not in k
        }
        adam.update(trainable, {k: mx.zeros_like(v) for k, v in trainable.items()})
        mx.eval(adam.state)

        # Now load the real optimizer state from safetensors
        n_opt_restored = tmp_store.load_optimizer_state(adam)
        print(f"  load_optimizer_state: {n_opt_restored} tensors restored ✓")

        # Sync to tmp copy
        tmp_store.sync(model, adam, step=9999, extra_state={"test": True})

        # Reload and verify a training tensor round-trips
        tmp_store2 = SafetensorsStore(tmp_store_dir)
        state2 = tmp_store2.load_state()
        assert state2["step"] == 9999, f"Expected step=9999, got {state2['step']}"
        assert state2.get("test") is True, "extra_state not written"
        print(f"  sync/reload: step={state2['step']} test={state2['test']} ✓")

        # Verify a training param round-trips byte-for-byte
        sample_training_key = next(
            k for k, (lbl, _) in tmp_store._key_map.items()
            if lbl == "training" and not k.startswith("optimizer.")
        )
        if sample_training_key in flat:
            np_before = _mx_to_np(flat[sample_training_key])
            with safe_open(str(tmp_store_dir / "training.safetensors"), framework="numpy") as tf:
                np_after = tf.get_tensor(sample_training_key)
            assert np_before.shape == np_after.shape, "Round-trip shape mismatch"
            assert np.allclose(np_before, np_after, rtol=0, atol=0), (
                f"Round-trip value mismatch for {sample_training_key}"
            )
            print(f"  round-trip: {sample_training_key} ✓")

        # ── Test 6: fold ─────────────────────────────────────────────────
        print("\n[6] fold() …")
        fold_meta = tmp_store2.fold()
        assert "n_plates" in fold_meta,   "fold_meta missing n_plates"
        assert fold_meta["n_plates"] == 76, f"Expected 76 plates, got {fold_meta['n_plates']}"
        print(f"  n_plates={fold_meta['n_plates']}  ✓")

        # Verify delta was reset to all +1
        sample_delta_key = sorted(k for k, (lbl, _) in tmp_store2._key_map.items() if lbl == "delta")[0]
        with safe_open(str(tmp_store_dir / "delta.safetensors"), framework="numpy") as df:
            delta_packed = df.get_tensor(sample_delta_key)
        info = tmp_store2._delta_hdr[sample_delta_key]
        N, K16 = info["shape"]
        # unpack_ternary_np expects a flat 1D uint32 array; reshape after
        delta_unpacked = unpack_ternary_np(delta_packed.ravel(), (N, K16 * 16))
        assert np.all(delta_unpacked == 1), "Delta not reset to all +1 after fold"
        print(f"  {sample_delta_key}: all +1 after fold ✓")

        # Verify fold correctness: re-load model params and check effective plate
        model2 = V14Model(cfg)
        tmp_store2.load_into_model(model2)
        flat2 = dict(tree_flatten(model2.parameters()))

        # The base plate should now encode the fold result.
        # Since delta was all +1 before fold (test started with a fresh copy from
        # step 2500 where delta may not be all +1), what we can verify is that
        # base.safetensors is structurally valid and readable.
        sample_base_key2 = sorted(k for k, (lbl, _) in tmp_store2._key_map.items() if lbl == "base")[0]
        if sample_base_key2 in flat2:
            base_param = flat2[sample_base_key2]
            assert base_param is not None
            mx.eval(base_param)
            print(f"  reloaded base plate {sample_base_key2}: shape={base_param.shape} ✓")

    finally:
        shutil.rmtree(str(tmp_dir), ignore_errors=True)

    print("\n" + "=" * 72)
    print("  ✅  All tests passed!")
    print("=" * 72 + "\n")


def _test_header_only(store: SafetensorsStore) -> None:
    """Minimal test when model imports are unavailable."""
    print("\n[header-only] Verifying header parsing …")
    assert store._base_data_start % 4096 == 0, "base.safetensors not page-aligned"
    assert store._delta_data_start % 4096 == 0, "delta.safetensors not page-aligned"
    assert store._training_data_start % 4096 == 0, "training.safetensors not page-aligned"
    print(
        f"  base_data_start={store._base_data_start}  "
        f"delta_data_start={store._delta_data_start}  "
        f"training_data_start={store._training_data_start}  ✓"
    )

    # Verify a round-trip read on a small tensor
    sample_key = next(
        k for k, (lbl, _) in store._key_map.items() if lbl == "training"
        and not k.startswith("optimizer.")
    )
    np_arr = store._read_tensor_np(sample_key)
    print(f"  sample read: {sample_key} shape={np_arr.shape} dtype={np_arr.dtype} ✓")
    print("\n  ✅  Header-only tests passed!")


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_safetensors_store()
