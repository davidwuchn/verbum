# Session 163 — Safetensors-Backed Continuous Training

## What happened

Wired the safetensors mmap architecture from session 162 into the real training loop. The model now trains continuously with three safetensors files as the live storage backend. No checkpoint serialization in the hot path.

### Extraction

Extracted step 2500 checkpoint (model.npz + optimizer.npz) into three page-aligned safetensors files:

| File | Contents | Size | Mode |
|------|----------|------|------|
| base.safetensors | 76 frozen base plates | 31.6 MB | readonly |
| delta.safetensors | 76 delta plates | 31.6 MB | mmap r/w (TD flips) |
| training.safetensors | 835 continuous params + optimizer | 105.5 MB | mmap r/w (Adam) |

987 tensors total, all verified byte-for-byte against original npz.

### SafetensorsStore

Built `scripts/v14/safetensors_store.py` — three operations:

1. **load**: `safe_open` → numpy → `mx.array` → model parameters + optimizer state
2. **sync**: `mx.array` → numpy → `np.memmap` write to safetensors data region
3. **fold**: unpack(base) × unpack(delta) → new base (atomic rename) + reset delta

### Sync benchmark

| Component | Time | Size |
|-----------|------|------|
| delta.safetensors | 346 ms | 31.6 MB (76 tensors) |
| training.safetensors | 4,160 ms | 105.5 MB (835 tensors) |
| **Total** | **4,506 ms** | **137.1 MB** |

At 17.7s/step: every 20 steps = 1.3% overhead, 6 min max crash loss.

### Three defense layers

| Layer | Interval | Max loss | Purpose |
|-------|----------|----------|---------|
| Safetensors sync | 20 steps | 6 min | Fast resume, continuous persistence |
| APFS snapshots | 200 steps | ~1 hr | Crash-during-sync recovery (12ms clone) |
| Legacy npz checkpoints | 500 steps | N/A | Timeseries analysis, last resort |

### Crash protection

- `syncing.lock` created before sync, removed after
- On startup: lock exists → auto-restore from latest APFS snapshot
- Snapshots: `cp -c` (APFS clone, 12ms, zero disk cost), keep 3 most recent

### Key insight

**Safetensors IS mmap.** The format is designed for zero-copy mmap access. Our plate files are safetensors without the header. `np.memmap` with offset writes directly into the safetensors data region. Same file for training AND release. The training format IS the distribution format.

### Training launched

Running in tmux main:2, step ~2530 → 20000, safetensors-backed, all three defense layers active.

## Artifacts

| File | Description |
|------|-------------|
| `scripts/v14/safetensors_store.py` | SafetensorsStore: load/sync/fold/snapshot |
| `scripts/v14/extract_to_safetensors.py` | Checkpoint → 3 safetensors files |
| `scripts/v14/train_td.py` | Updated with --safetensors-dir |
| `checkpoints/v14-mmap/` | Live training state (3 safetensors + state.json) |

## Commits

| Hash | Symbol | Description |
|------|--------|-------------|
| `a1c5134` | 💡 | Extract checkpoint to 3-file safetensors layout |
| `a54cda0` | ✅ | Safetensors-backed training loop |
| `79aa4c3` | 🔄 | Sync every 10 steps (benchmarked) |
| `646e978` | 🔄 | Changed to every 20 steps |
| `5483d40` | 🎯 | Snapshot + crash protection |
| `dbbe5b2` | ✅ | Keep legacy checkpoints every 500 alongside safetensors |
