# Session 162 — VSM ↔ Statechart ↔ Tensor Triple Isomorphism

## What happened

Explored two connected ideas: (1) Can VSMs be expressed as statecharts? (2) Can we build a VSM with mmap'd files as the delta plate? Both turned out to be the same idea from different angles, and we built a working dual-runtime proof.

### The Triple Isomorphism

Mapped Beer's VSM (1972), Harel's Statecharts (1987), and the tensor state machine discovered in the teacher (session 142) as three representations of the same structure:

| VSM | Statechart | Tensor |
|-----|-----------|--------|
| S5 identity | Top-level invariant | Crystal lattice |
| S4 intelligence | Orthogonal monitoring | Environment scanning |
| S3 control | Compound state | Plate controller |
| S2 coordination | Guards | Thresholds and protocols |
| S1 operations | Leaf states | Operational plates |
| Algedonic alert | Direct event | Crystal loss spike |
| Recursion | Hierarchical nesting | Nested statechart |

### What was built

1. **Shared EDN definition** (`specs/plate-loader.edn`): Single source of truth for the plate-loader VSM. Statechart with parallel regions mapping to VSM layers, guards, actions, and data model.

2. **Fulcro statechart** (`src/statechart/plate_loader.cljc`): The VSM as a Fulcro/Harel statechart in Clojure. Parallel regions for crystal (S5), plates (S3), inference (S1), and intelligence (S4). Guards reference the data model. Actions are mmap/compose/fold operations.

3. **Tensor statechart engine** (`scripts/explore/tensor_statechart.py`): The same VSM as int8 state vectors + ternary transition matrices. Real mmap'd plate files composed via sign multiplication. Verified working with demo plates.

### Key findings

- **Parallel regions work** — plates, inference, and intelligence regions transition independently, matching Harel's semantics
- **Guards correctly block** — fold-delta blocked until delta_changed_frac < threshold, then passes
- **Algedonic alert works** — inference → halted bypasses normal flow (S1 → S5 direct)
- **mmap composition verified** — sign(crystal × base × medical × session) = ternary ✓
- **Fold is lossless** — ternary × ternary = ternary, infinite folds without accumulation error
- **The compilation chain exists** — Clojure (96% lambda) → lambda → tensor is mechanical

### Nucleus connection

The nucleus repo (`~/src/nucleus`) contains exactly the compilation chain needed:
- `COMPILER.md` outputs EDN statecharts (the shared format)
- `LAMBDA-COMPILER.md` produces lambda notation
- `ALLIUM.md` produces behavioral specs with transitions and guards
- `VSM.md` structures prompts as Beer's five layers
- All four are different views of the same structure

### The central insight

**Files ARE states. Composition IS transition. mmap IS the runtime.**

A ternary plate loaded via mmap is simultaneously a state in the statechart AND a tensor in the computation. The statechart doesn't *control* the model — it *IS* the model's control structure, made explicit and executable.

## Artifacts

| File | Description |
|------|-------------|
| `specs/plate-loader.edn` | Shared statechart definition |
| `src/statechart/plate_loader.cljc` | Fulcro statechart (Clojure) |
| `scripts/explore/tensor_statechart.py` | Tensor statechart engine (Python) |
| `checkpoints/plates/*.bin` | Demo plate files |
| `mementum/knowledge/explore/vsm-statechart-tensor.md` | Knowledge synthesis |

### mmap Continuous Training — No Checkpoints Needed

The statechart + mmap insight led directly to checkpoint-free training:

| Old (checkpoint) | New (mmap) |
|---|---|
| Serialize every 500 steps | TD flips write directly to mmap'd file |
| Crash → lose up to 499 steps | Crash → lose ~5 seconds (OS flush) |
| Resume: load + deserialize (30s) | Resume: mmap + read JSON (<1s) |
| N × 54 MB checkpoint dirs | Single set of files (306 MB) |
| `_save_checkpoint()` (100 lines) | **Deleted** — files ARE the state |

Built `MmapPlateStore` (`scripts/v14/mmap_plates.py`) with:
- `MmapPlate`: packed ternary uint32 with in-place bit-level flips
- `MmapFloat`: float32 mmap for gamma and Adam moments
- Fold: atomic rename of base plate, delta reset to +1
- All tests passing: create, flip, crash recovery, fold, lossless double fold

**The central equation:** `file = state = checkpoint = tensor = plate`

### Safetensors Export — Zero-Cost Release

Safetensors IS mmap with a JSON header. Our mmap plate files are safetensors without the header. Conversion = prepend ~1 KB JSON. Verified: wrote demo plates to `.safetensors`, read back byte-identical.

Three release formats from the same files:
- **int8 safetensors (unpacked):** ~723 MB — universal, any framework, HF Hub
- **uint32 safetensors (packed):** ~187 MB — our ecosystem, needs custom unpack
- **Raw mmap plates:** ~187 MB — training/dev, fastest, our runtime only

Domain plates become separate small safetensors files:
- `base.safetensors` (187 MB) + `medical.safetensors` (~1 MB) + `session.safetensors` (~0.1 MB)
- Users download base + domain. Composition = `sign(base × domain)`. CPU only. No GPU.

The full lifecycle: `mmap training → fold → prepend header → safetensors release → mmap inference`. Same bytes end to end. Zero conversion cost.

## Connection to prior work

- Session 142: Discovered the holographic state machine (crystal basins = states, Q rotation = transition)
- Session 153: Envisioned "TIER 3: DOMAIN PLATES (mmap on demand)" and ecosystem vision
- Session 157: Delta plate lifecycle (extract → train → fold → repeat)
- Session 161: ISA decoder showed different tasks run different programs

This session closes the circle: the state machine discovered empirically in session 142 can now be expressed as a Fulcro statechart AND run as a tensor engine. Same structure, three representations, two working runtimes.
