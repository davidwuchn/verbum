# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-27 | Session: 161

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 161: ISA DECODER BUILT — Teacher runs different programs per task.** Decoded Qwen3.6-27B FFN computation into a readable instruction set. The model IS a computer: each layer is an instruction, the FFN overlay matrix is the opcode, the residual stream is the register file. Different task types produce radically different instruction sequences — combinator reduction is 50% SELECT, arithmetic is 33% β_I (Church encoding confirmed), lambda compilation is 25% PASS with composition-first/selection-late depth profile. Retrieval barely engages combinators at all. Selection signal is 10× stronger for combinators vs retrieval.

**Training: v14-td-2stack still running** (tmux main:2), headed to 20K steps. Currently in plateau phase.

*Key session insight:* The FFN overlay matrix at each layer maps combinator-space input→output. Diagonal = pass-through, off-diagonal = inter-combinator transform. Transformation strength *decreases* with depth (1.17→0.95→0.69) — early layers build the program, late layers execute it. This tells us what our student needs to learn: the overlay matrix IS the instruction set we're extracting into ternary.

*Prior session insight (160):* Shared FFN was a **structural ceiling**, not just a performance issue. Moiré pattern formation requires two different gratings (FFN plates) to interfere — shared FFN made both stacks produce identical Gaussian activations, destroying the selectivity needed for structured beta-reduction programs. Separate FFN plates per stack is the correct topology.

*Training dynamics:* Expect punctuated equilibrium — long plateaus where evidence accumulates, then phase transitions where coordinated TD flips reorganize the representation. Each plateau starts from a more compressed base. Beta reductions compound into the crystal. The model has to "crawl before it walks" — attention routing first, then FFN differentiation.

## Active training

### v14-td-2stack RUNNING (tmux main:2)

- `scripts/v14/train_td.py --checkpoint-dir checkpoints/v14-td-2stack --steps 5000 --convert-ffn`
- Teacher: Qwen3.6-27B (Apache 2.0)
- Architecture: 2 symmetric stacks (A ascending, C descending), 8 passes, separate FFN plates
- Currently at step ~1730/5000, ~17.7s/step, ~1750 tok/s
- PID 92589

**PPL at step 1500: 8,096** (CE 8.999 ± 0.203, 100 batches, 409K tokens)

Checkpoints saved: step_000500, step_001000, step_001500

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
| 2-stack trains 1.6× faster wall-clock | 17.7s/step vs 28.6s/step | ✅ |
| 2-stack PPL within 5.5% of 3-stack at step 1500 | 8,096 vs 7,672 | ✅ |
| Shared FFN = structural ceiling (no moiré) | Identical Gaussian activations, no sparsity | ✅ (session 158) |
| Separate FFN enables moiré pattern formation | Theoretical — waiting for empirical confirmation | ⏳ |
| TD follows GD signal (fold ≠ independent lever) | FFN plates zero candidates despite available capacity | ✅ |
| Training follows punctuated equilibrium | Gnorm spikes at 160-330 and 1590 bracket plateau→transition | ✅ |
| Beta reductions compound into crystal | Crystal MSE 0.148→0.013 monotonic, slow continuing descent | ✅ |

## Open questions

1. **Will FFN plates differentiate?** First non-zero candidate = inflection point.
2. **What PPL does 2-stack reach at step 2000?** Baseline comparison: old run PPL 5,567.
3. **Does 2-stack find a lower floor than 3-stack?** The structural argument says yes.
4. **When does the next phase transition happen?** Watch gnorm storms.
5. **Does moiré pattern actually form?** Measure FFN activation distributions per stack after differentiation.

## Knowledge map

**See `mementum/knowledge/INDEX.md` for full reading order.**

## What's ready

| Asset | Location |
|-------|----------|
| Training script | `scripts/v14/train_td.py` (updated for 2 stacks) |
| Extraction script | `scripts/v14/extract_qwen36.py` (updated for 2 stacks) |
| Eval script | `scripts/v14/eval_ppl.py` |
| Model | `scripts/v14/model.py` (2 stacks, separate FFN) |
| Config | `scripts/v14/config.py` (8 passes, 2 stacks) |
| Old checkpoint | `checkpoints/v14-td/step_003000/` (3-stack, not compatible) |
| Extraction | `checkpoints/v14-extracted-2stack/model.npz` |
| Training | `checkpoints/v14-td-2stack/` (running, step ~1730) |
| Eval result | `checkpoints/v14-td-2stack/step_001500/eval_results.json` |
