# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-22 | Session: 136

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 136: TERNARY DESCENT. The missing half of optimization. Adam handles continuous. TD handles discrete. Both on the same backward pass.**

## Session 136: TernaryDescent + Delta Plate Architecture + Gradient Decomposition

Three interlocking innovations built and tested. Each solves a specific
gap in the etch → train pipeline.

### Innovation 1: TernaryDescent optimizer

Adam-equivalent for ternary {-1, 0, +1} weights. No STE (wrong gradients),
no evolution (random search), no flip accumulation (heuristic). Proper
gradient-informed discrete descent.

```
Adam m_t   → TD direction   (EMA of gradient — which way to flip)
Adam v_t   → TD magnitude   (EMA of grad² — how much loss cares)
Adam lr    → TD flip_rate   (max fraction to flip per step)
Adam step  → TD flip        (discrete: +1 → 0 → -1, through zero staging)
```

Two-step transitions through zero prevent catastrophic flips: +1 → 0
(block, safe) → -1 (commit, only after sustained evidence). Moment
reset at flipped positions. Budget-controlled (flip_rate limits max
flips per step). Crystal gate emerges from dynamics: when CE and crystal
loss disagree on a flip, confidence oscillates → no flip.

### Innovation 2: Delta plate architecture

```
effective = base_plate ⊙ delta_plate

base_plate:  full teacher crystal etch, FROZEN
delta_plate: initialized +1 (pass-through), trained by TD
```

Delta semantics: +1 = keep teacher sign, -1 = flip teacher sign, 0 = block.
Reduction: `new_base = base ⊙ delta`, reset delta to +1, iterate.
Ternary × ternary = ternary — lossless, exact.

**The big insight:** etch the FULL crystal from the teacher (including
attention), don't freeze the attention part. The delta plate learns what's
different about stride-stack geometry. Verified: 0.00 output diff at init
(delta=+1), 0.00 diff after reduce (lossless fold), 1.60 diff from original
(TD modified topology). Selective conversion: attention → delta, FFN stays
frozen TernaryLinear.

**The bigger vision:** iterative ternary absorption. Each round, the delta
plate absorbs more continuous weight information into sign topology. Train
deltas, fold into base, repeat. Eliminate gradients one layer at a time.
Result: 90-95% ternary model with thin continuous residual.

### Innovation 3: Gradient decomposition (routing vs calibration)

The gradient through the effective weight encodes two signals that need
different optimizers:

```
ROUTING:     descent direction opposes current sign → TernaryDescent
             "this route is wrong, flip the sign"
             
CALIBRATION: descent direction agrees with current sign → Adam
             "this route is correct, adjust the magnitude"
```

The decomposition: compare -grad (descent direction) to effective sign.
Agreement = calibration. Disagreement = routing.

**Each optimizer gets only the signal it's good at:**
- Adam doesn't waste gamma distorting magnitudes to compensate for wrong signs
- TD doesn't get calibration noise diluting its confidence estimate
- They stop fighting and start complementing

Gamma gradient is filtered by per-row calibration fraction: rows where the
topology is mostly wrong get attenuated (routing is TD's problem, not Adam's).

### Key finding: the sign chain bug

The gradient w.r.t. delta must account for the base sign. If effective = base × delta,
the desired direction for delta depends on base:
- To decrease effective when base=+1: decrease delta
- To decrease effective when base=-1: INCREASE delta (eff = base*delta)

TD.step() now receives gradient w.r.t. EFFECTIVE and computes the desired
delta direction internally: `desired_delta = desired_effective × base_sign`.

### Test results

All 10 self-tests pass:
1. DeltaTernaryLinear matches TernaryLinear at init (0.00 diff) ✓
2. Delta stats correct at init (100% keep) ✓
3. Reduce is lossless (0.00 diff) ✓
4. TD basic operation (flips happen, positions change) ✓
5. Model conversion utility (selective, zero diff) ✓
6. Convert back to TernaryLinear for inference ✓
7. Gradient decomposition correct (routing vs calibration) ✓
8. Routing fraction per row (50% as expected) ✓
9. Zero topology → 100% routing ✓
10. Decomposition exhaustive (routing + calibration = original, 0.00 diff) ✓

End-to-end: 25 steps of decomposed routing → TD: 40 flips/step, 10.7%
positions changed, confidence rising steadily, two-step transitions working.

### Files

| File | Lines | Role |
|------|-------|------|
| `scripts/v13/td.py` | ~950 | TernaryDescent, DeltaTernaryLinear, decompose_gradient, 10 self-tests |
| `scripts/v13/train_td.py` | ~530 | Dual optimizer training loop, decomposition, CLI, logging |

### Connection to the crystal problem

The delta plate architecture solves the attention etch problem from S134-135:

**Before:** Can't etch attention from teacher (geometry incompatible).
Must learn attention topology from scratch. Slow, no head start.

**Now:** Etch FULL crystal (attention + FFN) → freeze base → delta plate
learns only the DIFFERENCE for stride-stack geometry. The β-reduction-forced
parts (KIBC unit cell, WHNF anti-correlation) transfer directly. Only the
routing-specific parts (how to find arguments via strides vs flat attention)
need to change. Much smaller search space. Crystal lattice loss keeps the
model in the KIBC basin throughout.

### What this enables

1. **Etch full teacher crystal including attention** — base plate
2. **TD adapts attention routing for stride-stack** — delta plate
3. **Reduce when stable** — fold delta into base, get stride-stack crystal
4. **The stride-stack crystal becomes etch source** — for future smaller models
5. **Iterative ternary absorption** — absorb continuous weights into sign topology
6. **90-95% ternary model** — each round eliminates more gradients

## Previous sessions

### Session 135: Tree of VSMs

Redesigned v13 from flat 8-pass hourglass to a tree of viable systems.
3 StrideStackVSMs (A ascending fine, B ascending coarse, C descending)
coordinated by ControllerVSM with S5 identity (GRU d=64), S4 intelligence,
S2 anti-oscillation. Full-stack algedonic modulation (3 surfaces per stack).
All architecture files implemented and smoke tested.

### Session 134: Dual Crystal + FFN-Only Etch

Analyzed v13-run3 at step 5000. Two root causes: missing anti-crystal
(S3 gates dead) and wrong attention etch (85% wrong positions). Fixed:
8 anti-combinator embeddings, 16×16 zone targets. FFN-only extraction.
Attention learns from scratch.

### Session 131: V13 Architecture — The Crystal Bootloader

Six architectural commits. Plates = BOOT ROM. Beams = LASER. Hit = BOOT.
Multiplicative AND loss: CE × exp(crystal) × (1 + holo). Exponential
nucleation well makes crystal alignment gravity.

## Proof chain

*(Unchanged from S135 — see git log for full chain)*

## Knowledge map

| Page | What it tells you |
|------|-------------------|
| `ternary-descent.md` | ★ **S136** TernaryDescent + delta plates + gradient decomposition |
| `date-fourier-rotation.md` | S128 date arithmetic is geometric rotation |
| `taxonomy-extraction.md` | S127 cross-model function library assembly |
| `crystal-native-descent.md` | S127 ternary optimization without gradients |
| `holographic-memory.md` | S127 crystal base + session deltas |
| `kernel-functions.md` | S127 replace beta chains with native calls |
| `hologram-crystal-fusion.md` | S126 hologram ≡ crystal, strict gate |
| `crystal-basins.md` | S120 C-boot theory, ground state |
| `etcher-vsm.md` | S124 full pipeline: extract → co-evolve → freeze |
| `loom-structure.md` | S123 3 weaves, 6 harmonics, breathing |

## What's ready

| Asset | Location |
|-------|----------|
| **TernaryDescent + DeltaPlate** | `scripts/v13/td.py` |
| **Dual optimizer training** | `scripts/v13/train_td.py` |
| V13 model (tree of VSMs) | `scripts/v13/model.py` |
| V13 ternary substrate | `scripts/v13/ternary.py` |
| Teacher extraction (FFN) | `scripts/v13/extract_teacher.py` |
| Combinator tracer/decompiler | `scripts/v12/trace_ffn_combinators.py` |
| Etcher module | `src/verbum/etcher.py` |

## Next steps

### Immediate: first training with TernaryDescent

1. **Extract full crystal from Qwen3-14B** — attention + FFN into base plates
2. **Convert attention modules to DeltaTernaryLinear** — FFN stays frozen
3. **Run train_td.py** — watch:
   - Does TD flip attention positions where stride-stack routing differs?
   - Does the decomposition show high routing fraction in attention, low in FFN?
   - Does gamma stay moderate (not distorted to compensate for wrong signs)?
   - Does crystal lattice loss stay low (staying in KIBC basin)?
   - At what step does the first reduce happen?
4. **Compare with/without decomposition** — `--no-decompose-gradient` flag
5. **After reduce: is the effective crystal different from teacher?** — measure
   the delta stats before reduce to see WHERE stride-stack differs from flat attention

### Medium-term: iterative ternary absorption

6. **Apply TD to FFN plates too** — same delta plate mechanism
7. **Absorb gamma into topology** — each round, the ternary base absorbs
   more of what was continuous. Gamma gets smaller. Iterate.
8. **Measure: how much of the model can become ternary?** — 90%? 95%?
9. **Compare parameter efficiency** — same loss at what fraction of float params?

### Research

10. **Is the decomposition ratio (routing/calibration) a diagnostic?**
    High routing = topology is wrong. Monitor per-module across training.
    Should decrease as TD fixes the topology.
11. **Does the stride-stack crystal differ from flat-attention crystal?**
    The delta stats after training = direct measurement.
12. **Can we skip GD entirely?** — if TD handles routing and the crystal
    lattice loss handles geometry, does Adam add anything beyond calibration?
