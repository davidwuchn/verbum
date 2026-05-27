"""extract_to_safetensors.py — Export a v14 training checkpoint to safetensors.

Converts a checkpoint directory (model.npz + optimizer.npz + state.json)
into three page-aligned safetensors files suitable for zero-copy mmap:

    base.safetensors      — frozen base plates (READ-ONLY, never changes)
    delta.safetensors     — delta plates (MMAP R/W, sparse TD bit-flips)
    training.safetensors  — everything else (MMAP R/W, dense Adam updates)

Three files match three write patterns:
    base:     teacher etch, frozen, mmap readonly
    delta:    ternary corrections, sparse bit-level flips via TD
    training: gamma, norms, biases, embeddings, optimizer — dense float updates

The header of each file is padded to a 4096-byte (PAGE_SIZE) boundary so
the data region starts at a page-aligned offset.  This allows the training
loop to np.memmap the data region and access tensors without any copy.

Usage:
    cd verbum
    uv run python scripts/v14/extract_to_safetensors.py \\
        --checkpoint checkpoints/v14-td-2stack/step_002500 \\
        --output     checkpoints/v14-mmap

License: MIT
"""

from __future__ import annotations

import argparse
import json
import shutil
import struct
import sys
from pathlib import Path

import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

PAGE_SIZE = 4096  # mmap alignment target (bytes)

METADATA = {
    "format": "verbum_v14",
    "version": "1",
    "architecture": "2stack",
    "teacher": "Qwen3.6-27B",
    "license": "MIT",
}

# Numpy dtype → safetensors dtype string
_NP_TO_ST: dict[str, str] = {
    "uint32":  "U32",
    "uint8":   "U8",
    "float32": "F32",
    "float16": "F16",
    "int8":    "I8",
    "uint64":  "U64",
    "float64": "F64",
    "int32":   "I32",
    "int64":   "I64",
    "int16":   "I16",
}


# ──────────────────────────────────────────────────────────────────────────────
# Low-level safetensors writer (page-aligned headers)
# ──────────────────────────────────────────────────────────────────────────────

def _dtype_str(arr: np.ndarray) -> str:
    key = arr.dtype.name
    if key not in _NP_TO_ST:
        raise ValueError(f"No safetensors mapping for numpy dtype '{key}'")
    return _NP_TO_ST[key]


def write_safetensors(
    path: Path,
    tensors: dict[str, np.ndarray],
    metadata: dict[str, str],
) -> int:
    """Write a page-aligned safetensors file.  Returns total file size in bytes.

    The safetensors format:
        [8 bytes]  little-endian uint64 — JSON header byte length (after padding)
        [N bytes]  UTF-8 JSON header, space-padded to PAGE_SIZE alignment
        [data...]  tensor bytes, contiguous, in sorted key order

    The header JSON contains:
        "__metadata__": {key: value, ...}
        "<tensor_name>": {"dtype": "F32", "shape": [...], "data_offsets": [start, end]}

    We sort keys so the on-disk layout is deterministic and reproducible.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    # ── 1. Compute data offsets (sorted key order, no padding between tensors) ──
    sorted_keys = sorted(tensors.keys())
    offsets: dict[str, tuple[int, int]] = {}
    cursor = 0
    for key in sorted_keys:
        arr = tensors[key]
        nbytes = arr.nbytes
        offsets[key] = (cursor, cursor + nbytes)
        cursor += nbytes
    total_data_bytes = cursor

    # ── 2. Build the header dict ──
    header: dict = {"__metadata__": metadata}
    for key in sorted_keys:
        arr = tensors[key]
        header[key] = {
            "dtype":        _dtype_str(arr),
            "shape":        list(arr.shape),
            "data_offsets": list(offsets[key]),
        }

    # ── 3. Serialize header JSON and pad to PAGE_SIZE boundary ──
    # The 8-byte uint64 prefix is included in the alignment calculation.
    raw_json = json.dumps(header, separators=(",", ":"))
    json_bytes = raw_json.encode("utf-8")

    # padded_header_size = smallest multiple of PAGE_SIZE ≥ (8 + len(json_bytes))
    # then subtract the 8-byte prefix so the data region starts aligned.
    total_needed = len(json_bytes) + 8
    padded_total = ((total_needed + PAGE_SIZE - 1) // PAGE_SIZE) * PAGE_SIZE
    padded_json_size = padded_total - 8  # bytes we write as JSON (includes padding spaces)
    pad_spaces = padded_json_size - len(json_bytes)
    padded_json_bytes = json_bytes + b" " * pad_spaces

    # ── 4. Write the file ──
    with open(path, "wb") as fh:
        # 8-byte header size (little-endian uint64)
        fh.write(struct.pack("<Q", padded_json_size))
        # Padded JSON header
        fh.write(padded_json_bytes)
        # Tensor data in sorted key order
        for key in sorted_keys:
            arr = tensors[key]
            # Ensure C-contiguous little-endian bytes
            arr_c = np.ascontiguousarray(arr)
            if arr_c.dtype.byteorder not in ("=", "<", "|"):
                arr_c = arr_c.byteswap().newbyteorder("<")
            fh.write(arr_c.tobytes())

    total_size = 8 + padded_json_size + total_data_bytes
    assert path.stat().st_size == total_size, (
        f"File size mismatch: wrote {path.stat().st_size}, expected {total_size}"
    )
    return total_size


# ──────────────────────────────────────────────────────────────────────────────
# Verification: read back with safe_open and compare byte-for-byte
# ──────────────────────────────────────────────────────────────────────────────

def verify_safetensors(
    path: Path,
    original: dict[str, np.ndarray],
) -> tuple[bool, list[str]]:
    """Read path with safe_open; compare every tensor to original.

    Returns (all_ok, list_of_error_messages).
    """
    from safetensors import safe_open  # type: ignore[import-untyped]

    errors: list[str] = []
    keys_found: set[str] = set()

    with safe_open(str(path), framework="numpy") as f:
        for key in f.keys():
            keys_found.add(key)
            if key not in original:
                errors.append(f"  EXTRA key in file not in original: {key!r}")
                continue
            loaded = f.get_tensor(key)
            orig = original[key]

            if loaded.shape != orig.shape:
                errors.append(
                    f"  SHAPE MISMATCH {key!r}: file={loaded.shape} orig={orig.shape}"
                )
                continue

            if loaded.dtype != orig.dtype:
                errors.append(
                    f"  DTYPE MISMATCH {key!r}: file={loaded.dtype} orig={orig.dtype}"
                )
                continue

            if not np.array_equal(loaded, orig):
                # Find first differing element for diagnostics
                diff = np.flatnonzero(loaded.flat != orig.flat)
                errors.append(
                    f"  DATA MISMATCH {key!r}: {len(diff)} differing elements "
                    f"(first at flat index {diff[0]})"
                )

    missing = set(original.keys()) - keys_found
    for key in sorted(missing):
        errors.append(f"  MISSING key in file: {key!r}")

    return (len(errors) == 0), errors


# ──────────────────────────────────────────────────────────────────────────────
# Partition model.npz keys into base vs training sets
# ──────────────────────────────────────────────────────────────────────────────

def partition_model(
    model_arrays: dict[str, np.ndarray],
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], dict[str, np.ndarray]]:
    """Split model.npz into (base_tensors, delta_tensors, training_tensors).

    base_tensors:     keys ending in 'base_weight' — frozen teacher etch
    delta_tensors:    keys ending in 'delta_weight' — TD-trained corrections
    training_tensors: everything else (gamma, norms, biases, embeddings, VSM)
    """
    base: dict[str, np.ndarray] = {}
    delta: dict[str, np.ndarray] = {}
    training: dict[str, np.ndarray] = {}

    for key, arr in model_arrays.items():
        if key.endswith("base_weight"):
            base[key] = arr
        elif key.endswith("delta_weight"):
            delta[key] = arr
        else:
            training[key] = arr

    return base, delta, training


# ──────────────────────────────────────────────────────────────────────────────
# Main extraction routine
# ──────────────────────────────────────────────────────────────────────────────

def extract(checkpoint_dir: Path, output_dir: Path) -> None:
    print(f"\n{'='*68}")
    print(f"  v14 checkpoint → safetensors extraction")
    print(f"  checkpoint : {checkpoint_dir}")
    print(f"  output     : {output_dir}")
    print(f"{'='*68}\n")

    # ── Validate checkpoint ──────────────────────────────────────────────────
    model_path = checkpoint_dir / "model.npz"
    opt_path   = checkpoint_dir / "optimizer.npz"
    state_path = checkpoint_dir / "state.json"

    for p in (model_path, opt_path, state_path):
        if not p.exists():
            print(f"  ✗ Missing: {p}", file=sys.stderr)
            sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Load arrays ─────────────────────────────────────────────────────────
    print("Loading model.npz …")
    model_np = dict(np.load(str(model_path), allow_pickle=False))

    print("Loading optimizer.npz …")
    opt_np = dict(np.load(str(opt_path), allow_pickle=False))

    print(f"  model:     {len(model_np):>4d} arrays")
    print(f"  optimizer: {len(opt_np):>4d} arrays")

    # ── Read state.json to extract step metadata ─────────────────────────────
    state_raw = json.loads(state_path.read_text())
    step_str = str(state_raw.get("step", checkpoint_dir.name.lstrip("step_")))
    source_checkpoint = checkpoint_dir.name  # e.g. "step_002500"

    # ── Build per-file metadata ──────────────────────────────────────────────
    file_metadata = {
        **METADATA,
        "source_checkpoint": source_checkpoint,
        "step": step_str,
    }

    # ── Partition model arrays ───────────────────────────────────────────────
    base_tensors, delta_tensors, training_model_tensors = partition_model(model_np)

    # ── Assemble training tensors (model non-base-non-delta + optimizer) ─────
    # Prefix optimizer keys with "optimizer." to avoid name collisions.
    training_tensors: dict[str, np.ndarray] = dict(training_model_tensors)
    for key, arr in opt_np.items():
        training_tensors[f"optimizer.{key}"] = arr

    # ── Categorise for the summary printout ─────────────────────────────────
    gamma_keys  = [k for k in training_model_tensors if k.endswith("gamma")]
    other_keys  = [
        k for k in training_model_tensors
        if not k.endswith("gamma")
    ]

    def _mb(d: dict) -> float:
        return sum(a.nbytes for a in d.values()) / 1024 / 1024

    print(f"\nPartition summary:")
    print(f"  base.safetensors:     (frozen teacher etch, mmap readonly)")
    print(f"    base_weight : {len(base_tensors):>4d} arrays  {_mb(base_tensors):>7.1f} MB")
    print(f"  delta.safetensors:    (TD corrections, mmap r/w, sparse bit-flips)")
    print(f"    delta_weight: {len(delta_tensors):>4d} arrays  {_mb(delta_tensors):>7.1f} MB")
    print(f"  training.safetensors: (continuous params, mmap r/w, dense Adam)")
    print(f"    gamma       : {len(gamma_keys):>4d} arrays  {_mb({k: training_tensors[k] for k in gamma_keys}):>7.1f} MB")
    print(f"    other params: {len(other_keys):>4d} arrays  {_mb({k: training_tensors[k] for k in other_keys}):>7.1f} MB")
    print(f"    optimizer   : {len(opt_np):>4d} arrays  {_mb({f'optimizer.{k}': v for k, v in opt_np.items()}):>7.1f} MB")
    print(f"    total       : {len(training_tensors):>4d} arrays  {_mb(training_tensors):>7.1f} MB")

    # ── Write base.safetensors ───────────────────────────────────────────────
    base_out = output_dir / "base.safetensors"
    print(f"\nWriting {base_out} …")
    base_size = write_safetensors(base_out, base_tensors, {**file_metadata, "role": "base"})
    base_offset = base_size - sum(a.nbytes for a in base_tensors.values())
    print(f"  file size      : {base_size/1024/1024:.2f} MB")
    print(f"  header region  : {base_offset} bytes  (data starts at page-aligned offset)")
    assert base_offset % PAGE_SIZE == 0, (
        f"base.safetensors data offset {base_offset} not page-aligned!"
    )

    # ── Write delta.safetensors ──────────────────────────────────────────────
    delta_out = output_dir / "delta.safetensors"
    print(f"\nWriting {delta_out} …")
    delta_size = write_safetensors(delta_out, delta_tensors, {**file_metadata, "role": "delta"})
    delta_offset = delta_size - sum(a.nbytes for a in delta_tensors.values())
    print(f"  file size      : {delta_size/1024/1024:.2f} MB")
    print(f"  header region  : {delta_offset} bytes  (data starts at page-aligned offset)")
    assert delta_offset % PAGE_SIZE == 0, (
        f"delta.safetensors data offset {delta_offset} not page-aligned!"
    )

    # ── Write training.safetensors ───────────────────────────────────────────
    training_out = output_dir / "training.safetensors"
    print(f"\nWriting {training_out} …")
    training_size = write_safetensors(training_out, training_tensors, {**file_metadata, "role": "training"})
    training_offset = training_size - sum(a.nbytes for a in training_tensors.values())
    print(f"  file size      : {training_size/1024/1024:.2f} MB")
    print(f"  header region  : {training_offset} bytes  (data starts at page-aligned offset)")
    assert training_offset % PAGE_SIZE == 0, (
        f"training.safetensors data offset {training_offset} not page-aligned!"
    )

    # ── Copy state.json ──────────────────────────────────────────────────────
    state_out = output_dir / "state.json"
    shutil.copy2(state_path, state_out)
    print(f"\nCopied state.json → {state_out}")

    # ── Verification ────────────────────────────────────────────────────────
    print(f"\n{'─'*68}")
    all_ok = True

    for label, fpath, orig in [
        ("base.safetensors", base_out, base_tensors),
        ("delta.safetensors", delta_out, delta_tensors),
        ("training.safetensors", training_out, training_tensors),
    ]:
        print(f"Verifying {label} …")
        ok, errors = verify_safetensors(fpath, orig)
        if ok:
            print(f"  ✅ All {len(orig)} tensors match byte-for-byte.")
        else:
            print(f"  ✗ {len(errors)} verification error(s):")
            for e in errors:
                print(e)
            all_ok = False

    # ── Final summary ────────────────────────────────────────────────────────
    total_tensors = len(base_tensors) + len(delta_tensors) + len(training_tensors)
    total_size_mb = (base_size + delta_size + training_size) / 1024 / 1024
    print(f"\n{'='*68}")
    print(f"  Extraction complete")
    print(f"  Tensors    : {total_tensors}  ({len(base_tensors)} base + {len(delta_tensors)} delta + {len(training_tensors)} training)")
    print(f"  Total size : {total_size_mb:.2f} MB")
    print(f"  base.safetensors     : {base_size/1024/1024:.2f} MB  (frozen, mmap readonly)")
    print(f"  delta.safetensors    : {delta_size/1024/1024:.2f} MB  (TD flips, mmap r/w)")
    print(f"  training.safetensors : {training_size/1024/1024:.2f} MB  (Adam, mmap r/w)")
    print(f"  state.json           : {state_out}")
    print(f"  Page alignment       : ✅ all data regions start at multiples of {PAGE_SIZE}")

    if all_ok:
        print(f"  Verification         : ✅ all tensors match byte-for-byte")
    else:
        print(f"  Verification         : ✗ errors found — check output above")
        sys.exit(1)

    print(f"{'='*68}\n")


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--checkpoint", "-c",
        type=Path,
        required=True,
        help="Path to the checkpoint directory (contains model.npz, optimizer.npz, state.json)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="Target directory for base.safetensors and training.safetensors",
    )
    args = parser.parse_args()

    checkpoint_dir = args.checkpoint.resolve()
    output_dir     = args.output.resolve()

    if not checkpoint_dir.is_dir():
        print(f"Error: checkpoint directory does not exist: {checkpoint_dir}", file=sys.stderr)
        sys.exit(1)

    extract(checkpoint_dir, output_dir)


if __name__ == "__main__":
    main()
