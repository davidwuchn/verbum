---
title: "Safetensors-Backed Continuous Training"
status: active
category: architecture
tags: [safetensors, training, mmap, sync, snapshot, crash-recovery, distributed]
related:
  - mmap-continuous-training.md
  - vsm-statechart-tensor.md
  - delta-plate-lifecycle.md
  - ../v14-architecture.md
  - ../training-protocols.md
depends-on:
  - mmap-continuous-training.md
  - ../v14-architecture.md
created: session 163
---

# Safetensors-Backed Continuous Training

> Session 163. The training loop stores all state in three safetensors
> files. Sync writes to the mmap'd data region every 20 steps. APFS
> snapshots protect against crash-during-sync. Legacy npz checkpoints
> every 500 steps preserve the timeseries. Same files for training
> AND release — zero conversion cost.

## Architecture

### Three Files, Three Write Patterns

| File | Contents | Size | Mode | Write pattern |
|------|----------|------|------|--------------|
| `base.safetensors` | 76 frozen base plates | 31.6 MB | readonly | Never changes |
| `delta.safetensors` | 76 delta plates | 31.6 MB | mmap r/w | Sparse bit flips (TD) |
| `training.safetensors` | 835 continuous params + optimizer | 105.5 MB | mmap r/w | Dense float updates (Adam) |
| `state.json` | Step, losses, TD state | ~42 KB | atomic write | Every sync |

987 tensors total. Headers page-aligned (4096 bytes) for zero-copy mmap.

### SafetensorsStore (`scripts/v14/safetensors_store.py`)

Three operations:

**load** — `safe_open(framework="numpy")` → numpy → `mx.array` → model
- Reads base + delta + training safetensors
- Populates model parameters, gamma, norms, biases, embeddings
- Loads optimizer state (keys prefixed `optimizer.`)

**sync** — `mx.array` → numpy → `np.memmap` write → flush
- Opens each tensor's byte range via `np.memmap(path, offset=..., mode='r+')`
- Writes current MLX array value to the mmap region
- state.json via atomic write (tempfile + `os.replace`)
- Never touches base.safetensors (frozen)

**fold** — `sign(base × delta)` → atomic rename → reset delta
- Unpack both plates, multiply, repack
- Write new base to temp file, `os.replace` (atomic)
- Reset all delta positions to +1 via mmap in-place
- Record fold metadata

### Sync Benchmark

| Component | Time | Size | Tensors |
|-----------|------|------|---------|
| delta.safetensors | 346 ms | 31.6 MB | 76 |
| training.safetensors | 4,160 ms | 105.5 MB | 835 |
| **Total** | **4,506 ms** | **137.1 MB** | **911** |

Bottleneck: 835 individual `np.memmap` open/close calls for training.safetensors.
Potential optimization: batch into single mmap of full data region.

### Sync Interval Trade-offs

| Interval | Overhead | Max crash loss |
|----------|----------|---------------|
| Every step | 25.5% | ~0s |
| Every 5 steps | 5.1% | ~90s |
| Every 10 steps | 2.5% | ~3 min |
| **Every 20 steps** | **1.3%** | **~6 min** ← chosen |
| Every 50 steps | 0.5% | ~15 min |
| Every 500 steps | 0.05% | ~2.5 hours |

## Three Defense Layers

| Layer | Interval | Max loss | Purpose |
|-------|----------|----------|---------|
| Safetensors sync | 20 steps (~6 min) | 6 min | Continuous persistence, fast resume |
| APFS snapshots | 200 steps (~1 hr) | 1 hour | Crash-during-sync recovery |
| Legacy npz checkpoints | 500 steps (~2.5 hr) | N/A | Timeseries analysis, last resort |

### Crash Protection

**Problem:** Sync writes 835+ tensors sequentially. Crash mid-sync = half-written file = corrupt.

**Solution:** Lock file + periodic snapshots.

1. Before sync: touch `syncing.lock`
2. Write all tensors to mmap regions
3. After sync: remove `syncing.lock`
4. On startup: if lock exists → auto-restore from latest snapshot

**Snapshots:** Every 10 syncs (200 steps), `cp -c` (APFS clone) all writable files.
- macOS APFS: 12 ms, zero disk cost (copy-on-write)
- Linux: `shutil.copy2` fallback, 22 ms for 169 MB
- Keep 3 most recent, prune oldest

## Safetensors = Training Format = Release Format

**Safetensors IS mmap.** The format is: 8-byte header size + JSON header +
raw contiguous tensor bytes, page-aligned for zero-copy mmap access.

Our training files are already valid safetensors. No conversion needed
for release. The lifecycle:

```
training (mmap write) → fold → release (same files, drop optimizer keys)
```

### Three Release Formats From the Same Files

| Format | Size | Audience |
|--------|------|----------|
| int8 safetensors (unpacked) | ~723 MB | Universal, any framework, HF Hub |
| uint32 safetensors (packed) | ~187 MB | Our ecosystem, needs custom unpack |
| Raw safetensors (as-is) | ~169 MB | Training/dev, fastest |

### Domain Plates as Separate Safetensors

```
base.safetensors       ~187 MB   ← universal model
medical.safetensors      ~1 MB   ← domain corrections
session.safetensors    ~0.1 MB   ← session context
```

Composition: `sign(base × domain)`. Pure integer multiply. CPU only.

### Metadata

```json
{"format": "verbum_v14", "architecture": "2stack",
 "teacher": "Qwen3.6-27B", "license": "MIT",
 "crystal_type": "KIBC_universal", "compression_ratio": "375x"}
```

## Distributed Training Vision

Multiple servers train independently from the same base:

1. Copy `base.safetensors` + `delta.safetensors` + `training.safetensors` to each server
2. Each server trains on different data (same architecture)
3. Each server's delta evolves independently
4. When deltas plateau: collect all `delta.safetensors` files
5. **Byzantine fold:** positions where ALL servers agree on flip → fold into base
6. Distribute new `base.safetensors`, reset all deltas, continue

Each server produces a portable artifact (safetensors files).
Fold consensus = the distributed equivalent of `reduce_all_deltas()`.

## CLI Usage

```bash
# Extract existing checkpoint to safetensors
uv run python scripts/v14/extract_to_safetensors.py \
  --checkpoint checkpoints/v14-td-2stack/step_002500 \
  --output checkpoints/v14-mmap

# Train with safetensors backend
uv run python scripts/v14/train_td.py \
  --safetensors-dir checkpoints/v14-mmap \
  --checkpoint-dir checkpoints/v14-mmap \
  --steps 20000 --convert-ffn

# Resume after crash: same command (loads from synced files)
```

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/v14/extract_to_safetensors.py` | npz checkpoint → 3 safetensors files |
| `scripts/v14/safetensors_store.py` | SafetensorsStore: load/sync/fold/snapshot |
| `scripts/v14/train_td.py` | Training loop with `--safetensors-dir` |
| `scripts/v14/mmap_plates.py` | Standalone mmap plate tests (precursor) |
