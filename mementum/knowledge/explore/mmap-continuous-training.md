---
title: "mmap Continuous Training — No Checkpoints Needed"
status: active
category: architecture
tags: [mmap, training, delta-plate, checkpoint, continuous, statechart]
related:
  - vsm-statechart-tensor.md
  - delta-plate-lifecycle.md
  - ../v14-architecture.md
  - ../training-protocols.md
depends-on:
  - vsm-statechart-tensor.md
  - delta-plate-lifecycle.md
created: session 162
---

# mmap Continuous Training — No Checkpoints Needed

> Session 162. If the mmap'd plate file IS the model state, and every
> TD flip writes directly to the mmap'd file, then there are no
> checkpoints — the files on disk ARE always the current state.
> The OS page cache handles persistence. Process crash → restart
> from the mmap'd files. No serialize. No deserialize. No save.

## The Insight

Current training:

```
train step → accumulate in memory → every 500 steps: serialize → write → disk
crash between checkpoints → lose up to 499 steps of work
resume → load → deserialize → reconstruct → continue
```

mmap training:

```
train step → TD flip writes to mmap'd delta file → OS pages dirty → OS flushes
crash at any point → restart → mmap the same files → continue
zero work lost (within OS flush granularity, typically seconds)
```

The checkpoint IS the file. The file IS the checkpoint. They are the
same object. "Saving a checkpoint" becomes "the OS flushing dirty
pages" which it does automatically.

## File Layout

```
training/
├── base.plate        # mmap readonly  — frozen teacher etch (uint32 packed)
├── delta.plate       # mmap r+        — TD writes flips here (uint32 packed)
├── gamma.f32         # mmap r+        — per-channel scales (float32)
├── adam_m.f32        # mmap r+        — Adam first moment (float32)
├── adam_v.f32        # mmap r+        — Adam second moment (float32)
├── state.json        # written every log_interval — tiny metadata
└── folds/            # git-tracked fold history
    ├── fold_001.json # metadata for each fold event
    ├── fold_002.json
    └── ...
```

### File Sizes (v14 2-stack architecture)

| File | Elements | Dtype | Size |
|------|----------|-------|------|
| base.plate | 593M / 16 = 37M | uint32 | ~141 MB |
| delta.plate | 593M / 16 = 37M | uint32 | ~141 MB |
| gamma.f32 | ~2M channels | float32 | ~8 MB |
| adam_m.f32 | ~2M channels | float32 | ~8 MB |
| adam_v.f32 | ~2M channels | float32 | ~8 MB |
| state.json | N/A | JSON | ~2 KB |
| **Total** | | | **~306 MB** |

Compare: current checkpoint saves model.npz (~27 MB packed delta) +
optimizer.npz (~27 MB) + state.json every 500 steps. That's ~54 MB
of I/O every 500 steps. mmap does zero explicit I/O — the OS handles
dirty page flush in the background.

## The Training Cycle as Statechart

```
[plate-training-vsm]

  idle
    → load-training : mmap all files
  ↓
  loaded
    → training-step : (self-transition, repeats)
      action: forward pass → backward → Adam update gamma → TD flip delta
      all writes go to mmap'd files (delta.plate, gamma.f32, adam_*.f32)
    → fold-check : (periodic, check delta plateau)
      guard: delta_changed_frac < fold_threshold
  ↓
  folding
    action: sign(base × delta) → write new base.plate → reset delta to +1
    → folded : back to loaded, new cycle
  ↓
  [any state]
    → crash : OS flushes dirty pages
    → restart : mmap same files → loaded (no resume logic needed)
```

## How Each Component Maps to mmap

### Base Plate (readonly)

```python
# Load once, never modified during training
base = np.memmap("training/base.plate", dtype=np.uint32, mode='r',
                 shape=(n_packed_elements,))

# Convert to MLX for forward pass (zero-copy on read)
base_mx = mx.array(base)
```

### Delta Plate (read-write)

```python
# mmap in read-write mode — TD writes directly here
delta = np.memmap("training/delta.plate", dtype=np.uint32, mode='r+',
                  shape=(n_packed_elements,))

# After TD determines which positions to flip:
def td_flip(delta_mmap, flip_indices, new_values):
    \"\"\"TD flip writes directly to mmap'd file.\"\"\"
    # Unpack affected positions
    for idx in flip_indices:
        word_idx = idx // 16
        bit_offset = (idx % 16) * 2
        # Modify the packed uint32 in-place
        mask = ~(0b11 << bit_offset)
        delta_mmap[word_idx] = (delta_mmap[word_idx] & mask) | (new_values << bit_offset)
    # OS handles persistence — dirty pages flushed automatically
    # Optional: delta_mmap.flush() for explicit sync points
```

### Gamma (read-write)

```python
# Per-channel scales trained by Adam
gamma = np.memmap("training/gamma.f32", dtype=np.float32, mode='r+',
                  shape=(n_channels,))

# After Adam step:
gamma[:] = new_gamma_values  # writes directly to file
# No explicit save needed
```

### Adam Moments (read-write)

```python
# Adam first and second moments
adam_m = np.memmap("training/adam_m.f32", dtype=np.float32, mode='r+',
                   shape=(n_continuous_params,))
adam_v = np.memmap("training/adam_v.f32", dtype=np.float32, mode='r+',
                   shape=(n_continuous_params,))

# After each Adam step:
adam_m[:] = beta1 * adam_m + (1 - beta1) * grad
adam_v[:] = beta2 * adam_v + (1 - beta2) * grad**2
# Writes go directly to mmap'd files
```

### State Metadata (tiny, explicit write)

```python
# Tiny JSON file — written every log_interval (100 steps)
# This is the ONLY explicit file write in the entire training loop
state = {
    "step": current_step,
    "td_step_count": td.step_count,
    "crystal_ema": crystal_ema_value,
    "delta_changed_frac": delta_changed_frac,
    "n_reductions": n_reductions,
    "data_loader": loader.save_state(),
    "timestamp": time.time(),
}
Path("training/state.json").write_text(json.dumps(state, indent=2))
```

## Fold as Statechart Transition

Fold is the key event. In the current system, fold is:
1. Unpack base and delta
2. Multiply: new_base = base ⊙ delta
3. Repack
4. Reset delta to all +1
5. Save checkpoint

In mmap, fold becomes:
1. mmap base (readonly) and delta (readonly for fold)
2. Compute: new_base = sign(base × delta)
3. Write new_base to NEW file (atomic rename)
4. Reset delta file to all +1 (or create new file)
5. Update base mmap to point to new file
6. Record fold metadata in folds/fold_NNN.json

```python
def fold_mmap(base_path, delta_path, fold_dir):
    \"\"\"Fold delta into base via mmap. Atomic via rename.\"\"\"
    base = np.memmap(base_path, dtype=np.uint32, mode='r', shape=shape)
    delta = np.memmap(delta_path, dtype=np.uint32, mode='r', shape=shape)

    # Compute new base (unpack, multiply, repack)
    base_unpacked = unpack_ternary(base)
    delta_unpacked = unpack_ternary(delta)
    new_base_unpacked = base_unpacked * delta_unpacked  # ternary × ternary
    new_base_packed = pack_ternary(new_base_unpacked)

    # Write new base to temp file, then atomic rename
    tmp_path = base_path + ".tmp"
    new_base_packed.tofile(tmp_path)
    os.rename(tmp_path, base_path)  # atomic on same filesystem

    # Reset delta to all +1
    delta_rw = np.memmap(delta_path, dtype=np.uint32, mode='r+', shape=shape)
    ones_packed = pack_ternary(np.ones(unpacked_shape, dtype=np.int8))
    delta_rw[:] = ones_packed
    delta_rw.flush()

    # Record fold event
    fold_meta = {
        "fold_number": len(list(fold_dir.glob("fold_*.json"))) + 1,
        "timestamp": time.time(),
        "delta_stats": compute_delta_stats(delta_unpacked),
    }
    fold_path = fold_dir / f"fold_{fold_meta['fold_number']:03d}.json"
    fold_path.write_text(json.dumps(fold_meta, indent=2))

    return fold_meta
```

## Crash Recovery

Traditional checkpoint recovery:
```
1. Find latest checkpoint directory
2. Load model.npz (deserialize)
3. Load optimizer.npz (deserialize)
4. Load delta_plates.npz (deserialize)
5. Load state.json
6. Reconstruct model state
7. Resume training
```

mmap recovery:
```
1. Read state.json (2 KB)
2. mmap all files (instant — OS maps pages, no deserialization)
3. Resume training from state.json step number
```

Time comparison:
- Traditional resume: ~10-30 seconds (deserialize + reconstruct)
- mmap resume: < 1 second (just mmap + read JSON)

Data loss comparison:
- Traditional: up to 499 steps (between checkpoints)
- mmap: up to ~5 seconds (OS dirty page flush interval)

## The MLX ↔ mmap Bridge

MLX arrays can be created from numpy arrays (including mmap'd ones):

```python
# Verified: numpy mmap → MLX works
base_np = np.memmap("base.plate", dtype=np.uint32, mode='r', shape=(N,))
base_mx = mx.array(base_np)  # creates MLX array from numpy
```

For the training loop, the bridge pattern is:

```python
# 1. Read phase: mmap → MLX (for forward/backward)
delta_np = np.memmap("delta.plate", dtype=np.uint32, mode='r+', shape=(N,))
delta_mx = mx.array(delta_np)  # snapshot for this step

# 2. Compute phase: forward + backward in MLX (GPU/ANE)
loss, grads = loss_and_grad_fn(model, batch)

# 3. Write phase: TD flips → numpy mmap (CPU, sparse)
flip_indices, new_values = td.compute_flips(grads)
apply_flips_to_mmap(delta_np, flip_indices, new_values)

# 4. Next step: create fresh mx.array from updated mmap
delta_mx = mx.array(delta_np)  # re-read with flips applied
```

The cost of the numpy↔MLX bridge is small because:
- TD flips are sparse (~0.1% of positions per step)
- The flip operation is on CPU anyway (bit manipulation)
- The mx.array() call from numpy is a copy, not a conversion

## What Changes vs Current System

| Current | mmap | Impact |
|---------|------|--------|
| `_save_checkpoint()` every 500 steps | No explicit saves | -1.5s every 500 steps |
| `_resume_from_checkpoint()` | Just mmap the files | Resume: 30s → <1s |
| model.npz (serialize all params) | base.plate + delta.plate (already there) | Zero serialize cost |
| optimizer.npz (serialize moments) | adam_m.f32 + adam_v.f32 (already there) | Zero serialize cost |
| delta_plates.npz (separate delta file) | delta.plate (the live training file) | Same file, no copy |
| Lose up to 499 steps on crash | Lose ~5 seconds on crash | Crash resilience |
| Checkpoint dirs accumulate on disk | Single set of files + fold history | Disk: N×54MB → 306MB |

## What We KEEP

1. **state.json** — still written explicitly (tiny, ~2 KB)
2. **train_td_log.jsonl** — training log (append-only, unchanged)
3. **Fold events** — still explicit (statechart transition)
4. **Eval runs** — still explicit (run eval script on current plates)

## What We REMOVE

1. **_save_checkpoint()** — the entire function
2. **_resume_from_checkpoint()** — replaced by mmap + state.json
3. **Checkpoint directories** — no more step_000500/, step_001000/
4. **Serialize/deserialize** — mx.savez/mx.load → mmap

## Safetensors Export — Zero-Cost Release Format

Safetensors IS mmap. The format is: 8-byte header size + JSON header +
raw contiguous tensor bytes. The data region is page-aligned for
zero-copy mmap access. Our mmap plate files are safetensors without
the header.

**Conversion cost: ~1 KB of JSON header. That's it.**

### Three Release Formats From the Same Files

| Format | Size | Audience | How |
|--------|------|----------|-----|
| int8 safetensors (unpacked) | ~723 MB | Universal — any framework, HF Hub | Unpack uint32 → int8, add header |
| uint32 safetensors (packed) | ~187 MB | Our ecosystem — needs custom unpack | Add header to packed plates |
| Raw mmap plates | ~187 MB | Training/dev — fastest, our runtime | Already what we have |

### The Pipeline

```
Training:     base.plate + delta.plate     ← mmap r/w, packed uint32
                   ↓ fold
              base.plate (updated)          ← mmap r, packed uint32
                   ↓ export (prepend 1KB JSON header)
Release:      model.safetensors             ← standard HF format
                   ↓ import (by others)
Inference:    safetensors mmap              ← OS pages in on demand
```

No conversion cost between training and release. The raw bytes are
identical. Safetensors mmap uses the same OS mechanism we use during
training.

### Domain Plates as Separate Safetensors

```
base.safetensors       187 MB   ← the universal model
medical.safetensors      ~1 MB   ← 2.6% positions flipped
legal.safetensors        ~2 MB   ← domain corrections
session.safetensors    ~0.1 MB   ← session-specific context
```

Users download base + domain plate. Composition = `sign(base × domain)`.
Pure integer multiply. No GPU. Runs on CPU.

### Metadata

Safetensors `__metadata__` carries provenance:

```json
{"format": "verbum_ternary_plates",
 "architecture": "v14-2stack",
 "teacher": "Qwen3.6-27B",
 "teacher_license": "Apache-2.0",
 "license": "MIT",
 "crystal_type": "KIBC_universal",
 "composition": "sign_multiply",
 "compression_ratio": "375x"}
```

### Verified

Session 162: wrote our demo plates to safetensors, read them back,
byte-identical. Header overhead at production scale: 0.00014%.

## Open Questions

1. **MLX mmap directly?** MLX has mx.load() which may use mmap internally.
   If MLX can consume mmap'd arrays in its computation graph without
   copying, the bridge cost drops to zero. Need to test.

2. **Packed uint32 bit-level mmap writes?** TD flips individual ternary
   positions, which are 2 bits inside a uint32. Modifying individual bits
   in a mmap'd file requires read-modify-write of the containing uint32.
   This is fine for sparse flips but needs care for concurrent access.

3. **Adam moments for ternary params?** Currently TD doesn't use Adam.
   But gamma (per-channel scale) uses Adam. The gamma mmap is small
   (~8 MB) so the write cost is negligible.

4. **Multiple delta plates per module?** Each DeltaTernaryLinear has its
   own delta. With separate files per module, fold can be per-module
   (fold the most converged module first). This is more granular than
   the current reduce_all_deltas().

5. **Git integration?** Each fold could be a git commit of the base.plate
   file. History is preserved. But 141 MB binary files in git is heavy.
   Alternative: store fold metadata in git, plates in LFS or external.

6. **Packed vs unpacked for HF Hub?** int8 unpacked (723 MB) is universal
   but 4× larger. uint32 packed (187 MB) is smaller but needs custom
   loader. Could publish both: packed for our ecosystem, unpacked for
   everyone else.
