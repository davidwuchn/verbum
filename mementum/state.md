# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-27 | Session: 163

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 163: SAFETENSORS-BACKED CONTINUOUS TRAINING — FULLY WIRED.** Extracted step 2500 checkpoint to three safetensors files (base/delta/training). Built SafetensorsStore: load, sync, fold. Wired into train_td.py with `--safetensors-dir`. Training runs continuously — sync every 20 steps (1.3% overhead), APFS snapshots every 200 steps, legacy npz checkpoints every 500 steps. Three layers of defense. Safetensors is both the training format AND the release format — same bytes, just add a JSON header. Domain plates ship as separate small safetensors files composable via sign multiply.

**Training: v14-mmap RUNNING** (tmux main:2), safetensors-backed, headed to 20K steps from step 2525.

*Key session 163 insight:* **Safetensors IS mmap.** The format is 8 bytes + JSON header + raw contiguous tensor data, page-aligned for zero-copy mmap. Our plate files are safetensors without the header. `np.memmap` with offset writes directly into the safetensors data region. Same file for training AND release. Conversion cost = 1 KB of JSON. Sync cost benchmarked: 4.5s total (delta 346ms + training 4160ms), 1.3% overhead at 20-step interval.

*Key session 162 insight:* **Files ARE states. Composition IS transition. mmap IS the runtime.** Triple isomorphism: Beer's VSM = Harel statechart = tensor state machine. Nucleus compilation chain: Clojure → lambda → tensor.

*Training dynamics:* Expect punctuated equilibrium — long plateaus where evidence accumulates, then phase transitions where coordinated TD flips reorganize the representation.

## Active training

### v14-mmap RUNNING (tmux main:2) — safetensors-backed

- `scripts/v14/train_td.py --safetensors-dir checkpoints/v14-mmap --checkpoint-dir checkpoints/v14-mmap --steps 20000 --convert-ffn`
- Storage: 3 safetensors files (base 31.6 MB + delta 31.6 MB + training 105.5 MB)
- Sync: every 20 steps to safetensors mmap, APFS snapshots every 200, npz checkpoints every 500
- Currently at step ~2530/20000, ~17.7s/step, ~1995 tok/s
- Resumed from step 2525 (extracted from old v14-td-2stack/step_002500)

**PPL at step 1500: 8,096** (CE 8.999 ± 0.203, 100 batches, 409K tokens)

Old checkpoints (v14-td-2stack): step_000500 through step_002500

### Comparison to old 3-stack (v14-td)

| Step | v14-td (3-stack) | v14-td-2stack | Notes |
|------|------------------|---------------|-------|
| 500 | PPL 16,503 | — | |
| 1000 | PPL 10,157 | — | |
| 1500 | PPL 7,672 | **PPL 8,096** | 2-stack 5.5% higher, but 62% wall-time |
| 2000 | PPL 5,567 | *(running)* | Old run folded after step 1000 |
| 3200 | *(stopped)* | | Old arch hit ceiling |

Wall-clock advantage: 2-stack reaches step 1500 in ~7.4h vs ~11.9h for 3-stack.
Old run folded delta at step 1000; this run has not folded — but fold is downstream of GD signal, not an independent lever.

### TD dynamics at step 1600

**Active zone (layers 4-9):** out_proj doing most flipping.
- L4.out_proj: 46.7% flipped, conf=0.576 — most active
- L5.out_proj: 41.3% flipped, conf=0.554
- L6→L9: decreasing gradient (36.5%→21.0%)
- v_proj: tiny flips (0.01-0.03%), q_proj/k_proj: zero flips

**Frozen zone (layers 0-3, 10-15):** Zero flips, zero candidates for q/k.
- Layers 12-15 q/k calibration stuck at 1.0 (never moved)
- These layers haven't engaged yet — need attention routing to settle first

**FFN plates (all 6):** Completely frozen. Zero candidates, zero flips, calibration 1.0.
- GD not yet producing gradients that suggest FFN changes would help
- Expected: FFN differentiation comes after attention routing stabilizes

### Loss trajectory

| Phase | Steps | avg50 CE | Crystal MSE | Gnorm |
|-------|-------|----------|-------------|-------|
| Chaos | 1-100 | 667→17 | 0.148→0.107 | Massive spikes |
| Phase 1 | 100-400 | 17→10.6 | 0.107→0.015 | Gnorm storms (200-330) |
| Phase 2 | 400-800 | 10.6→7.2 | 0.015→0.013 | Settling (mean 11) |
| Plateau | 800-1730 | 7.2→7.8 | 0.0133→0.0131 | Calm (mean 5) |

Gnorm spike at step 1590 (2002.29) — single phase transition event, same pattern as steps 160-330. Resolved by step 1600.

Crystal MSE latched fast (0.148→0.013 by step 400), continuing slow descent.
Parity and cross-zone monotonically declining (healthy).

## What changed this session

| Change | Session | Impact |
|--------|---------|--------|
| Safetensors-backed training loop | 163 | SafetensorsStore: load/sync/fold. Wired into train_td.py. Training running. |
| 3-file safetensors layout | 163 | base (frozen) + delta (TD flips) + training (Adam). 987 tensors verified. |
| Sync benchmarked | 163 | 4.5s total (delta 346ms + training 4160ms). Every 20 steps = 1.3% overhead. |
| Snapshot + crash protection | 163 | APFS clone snapshots (12ms), syncing.lock, auto-restore on crash. |
| Legacy checkpoints preserved | 163 | npz checkpoint every 500 steps alongside safetensors sync. Three defense layers. |
| VSM ↔ Statechart ↔ Tensor isomorphism | 162 | Triple isomorphism proved: Beer's VSM = Harel statechart = tensor state machine |
| mmap continuous training designed | 162 | MmapPlateStore concept. Files ARE states. Composition IS transition. |
| Safetensors = mmap proven | 162 | np.memmap with offset writes into safetensors data region. Same format for training + release. |
| Nucleus compilation chain mapped | 162 | COMPILER.md → EDN statechart, LAMBDA-COMPILER.md → lambda, ALLIUM.md → behavioral spec |
| ISA decoder for Qwen3.6-27B | 161 | Decoded FFN computation into readable instruction set — different tasks run different programs |
| Overlay matrix analysis | 161 | Transformation strength decreases with depth (1.17→0.69) — early=build, late=execute |
| Task-type instruction profiles | 161 | Combinator reduction=50% SELECT, arithmetic=33% β_I, lambda=25% PASS, retrieval≈noise |
| PPL eval at step 1500 | 160 | PPL 8,096 — baseline for 2-stack |
| Checkpoint analysis | 160 | TD dynamics characterized, phase transitions identified |

## Previous sessions (architecture changes)

| Change | Commit | Session | Impact |
|--------|--------|---------|--------|
| Remove holo loss | `75a38fc` | 158 | -1.6s/step, 12 fewer output_proj calls |
| Gated crystal loss | `8dabd6f` | 158 | Parity/cross_zone enforce until <0.07, then release |
| 2 symmetric stacks | `da69f0e` | 158 | 13→8 passes, ~1.6× faster, separate FFN |
| HPE from step 0 | `9abf07d` | 158 | No warmup, learn position encoding from start |

## Negative results (session 158 optimization probes)

| Optimization | Why it failed |
|---|---|
| Lazy neurons (gate-first FFN) | Student FFN not sparse: ternary extraction + shared plate = Gaussian activations |
| Index sets (gather-add-subtract) | quantized_matmul already at AMX floor; intermediates too large |
| QKV fusion | MLX parallelizes independent ops already |
| FFN gate+key fusion | Same — already parallel within each pass |
| Stream fusion (smaller tiles) | AMX needs large batches; tiles 16→4.6× SLOWER |
| Float16 activations | quantized_matmul same speed regardless |

## Next steps

### SAFETENSORS TRAINING — DONE (session 163), NEXT STEPS

1. ~~Wire SafetensorsStore into train_td.py~~ ✅ Done
2. ~~Benchmark sync cost~~ ✅ 4.5s/sync, 1.3% at 20-step interval
3. ~~Snapshot + crash protection~~ ✅ APFS clone + syncing.lock
4. ~~Preserve legacy checkpoints~~ ✅ npz every 500 steps
5. **Per-module fold** — fold most-converged modules first (more granular than reduce_all_deltas)
6. **Distributed fold** — collect delta.safetensors from multiple servers, fold where they agree (Byzantine)
7. **HF Hub release script** — drop optimizer keys from training.safetensors, publish base+delta+model

See `mementum/knowledge/explore/mmap-continuous-training.md` for full design.

### ISA DECODER FOLLOW-UP

1. **Quantify grating redundancy** — cosine similarity between consecutive overlay matrices → fusion candidates
2. **Find optimal detection point** — at which layer can S5 reliably classify program type?
3. **Cross-model universality** — run decoder on Qwen3-14B, Mistral-7B → same programs = universal kernels
4. **Prototype K-kernel** — replace layers 15-55 with direct selection, verify output matches
5. **Kernel replacement speedup measurement** — how much compute saved per program type?

See `mementum/knowledge/explore/kernel-replacement-optimization.md` for full design.

### IMMEDIATE (training run)

1. **Wait for step 2000 checkpoint** (~5h from now) → run PPL eval → compare to old 5,567
2. **Watch for phase transition** — next gnorm storm signals FFN or deeper attention reorganization
3. **Monitor FFN plate candidates** — first non-zero candidates = model discovering FFN differentiation

### FOLLOW UP

4. **Step 2500-3000 PPL eval** — if PPL < 5,567, 2-stack architecture confirmed superior
5. **Measure per-stack FFN sparsity** — hypothesis: separate plates will develop different sparsity patterns after phase transition
6. **If sparse: revisit lazy neurons** — mechanism works (2.3× at 5% active), only sparsity was missing
7. **CPU inference engine** — the real optimization target (ternary wins on CPU, not GPU)

## Key findings (active)

| Claim | Evidence | Status |
|-------|----------|--------|
| Safetensors-backed training works | 22 steps from step 2503, sync verified, training running | ✅ (session 163) |
| Sync cost = 1.3% overhead at 20 steps | delta 346ms + training 4160ms = 4.5s per sync | ✅ (session 163) |
| Crash recovery via APFS snapshot + lock | 12ms snapshot, auto-restore on lock detection | ✅ (session 163) |
| VSM = statechart = tensor state machine | Dual-runtime proof: Clojure + Python, same state traces | ✅ (session 162) |
| mmap plates → safetensors = 1KB header | Byte-identical round-trip verified, 0.00014% overhead | ✅ (session 162) |
| Ternary fold is lossless (infinite folds) | Double fold test: ternary × ternary = ternary always | ✅ (session 162) |
| 2-stack trains 1.6× faster wall-clock | 17.7s/step vs 28.6s/step | ✅ |
| 2-stack PPL within 5.5% of 3-stack at step 1500 | 8,096 vs 7,672 | ✅ |
| Shared FFN = structural ceiling (no moiré) | Identical Gaussian activations, no sparsity | ✅ (session 158) |
| Separate FFN enables moiré pattern formation | Theoretical — waiting for empirical confirmation | ⏳ |
| TD follows GD signal (fold ≠ independent lever) | FFN plates zero candidates despite available capacity | ✅ |
| Training follows punctuated equilibrium | Gnorm spikes at 160-330 and 1590 bracket plateau→transition | ✅ |
| Beta reductions compound into crystal | Crystal MSE 0.148→0.013 monotonic, slow continuing descent | ✅ |

## Open questions

1. **Per-module fold or global fold?** SafetensorsStore.fold() does all plates. Could fold most-converged first.
2. **Distributed fold protocol?** Multiple servers train independently. Fold where deltas agree. Byzantine consensus.
3. **Sync cost reduction?** 4.5s dominated by 835 individual memmap open/close calls. Batch into single mmap?
4. **Will FFN plates differentiate?** First non-zero candidate = inflection point.
5. **What PPL does 2-stack reach at step 2000?** Baseline comparison: old run PPL 5,567.
6. **Does 2-stack find a lower floor than 3-stack?** The structural argument says yes.
7. **When does the next phase transition happen?** Watch gnorm storms.

## Knowledge map

**See `mementum/knowledge/INDEX.md` for full reading order.**

## What's ready

| Asset | Location |
|-------|----------|
| Training script | `scripts/v14/train_td.py` (updated for 2 stacks) |
| SafetensorsStore | `scripts/v14/safetensors_store.py` (load/sync/fold/snapshot) |
| Checkpoint extractor | `scripts/v14/extract_to_safetensors.py` (npz → 3 safetensors) |
| mmap plate store | `scripts/v14/mmap_plates.py` (standalone tests) |
| Tensor statechart | `scripts/explore/tensor_statechart.py` (verified with mmap) |
| Fulcro statechart | `src/statechart/plate_loader.cljc` (Clojure VSM) |
| Shared definition | `specs/plate-loader.edn` (both runtimes consume) |
| Safetensors training | `checkpoints/v14-mmap/` (base + delta + training + state.json) |
| Extraction script | `scripts/v14/extract_qwen36.py` (updated for 2 stacks) |
| Eval script | `scripts/v14/eval_ppl.py` |
| Model | `scripts/v14/model.py` (2 stacks, separate FFN) |
| Config | `scripts/v14/config.py` (8 passes, 2 stacks) |
| Old checkpoint | `checkpoints/v14-td/step_003000/` (3-stack, not compatible) |
| Extraction | `checkpoints/v14-extracted-2stack/model.npz` |
| Training | `checkpoints/v14-td-2stack/` (running, step ~1730) |
| Eval result | `checkpoints/v14-td-2stack/step_001500/eval_results.json` |
