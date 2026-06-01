# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-01 | Session: 177

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 177: TRACE-GUIDED ETCHING — FULL S2 STACK BUILT + TRAINING RUNNING.**

Complete trace-guided etching system delivered: delta plates, TD, structural zeros, thermometer, Adam decay, and training loop integration. All S2 anti-oscillation mechanisms in place.

### What was built

1. **Delta plates** (`model.py`) — `TernaryPlate` gains `delta1`/`delta2` initialized to +1. Forward: `effective = plate ⊙ delta`. `fold()` merges losslessly. `TensorStatechart` gains `enable_delta_plates()`, `fold_delta_plates()`, `collect_delta_params()`.

2. **TernaryDescent** (`td.py`) — Port of v14 TD for v15 float plates. Moment accumulation, confidence scoring, cooldown, holographic etch. Plus `apply_td_flips()`, `fold_and_reset()`, `get_affected_gamma_rows()`, `decay_adam_for_affected_rows()`.

3. **Structural zeros** (`apply_zeros.py` + `extract.py --zero-frac`) — 30% of positions are irreducible fixed points. 194.6M zeros placed. Magnitude reconstructed from 2-plate decomposition. Global threshold per plate.

4. **Crystal thermometer** (`td.py: CrystalThermometer`) — Measures crystal temperature (fraction of positions active recently) and oscillation fraction (of active, how many flip-flopping). Temperature → 0 = fold signal.

5. **Adam moment decay** (`td.py: decay_adam_for_affected_rows`) — When TD flips signs, Adam's moments for affected gamma rows are decayed to 10%. Prevents Adam from pushing gamma in the wrong direction for ~10 steps after topology change.

6. **etch.py** — Standalone topology correction: trace loss → TD → fold → compare. Validated: fold perfectly lossless (delta=0.0).

7. **train.py integration** — `--delta-plates`, `--trace-weight`, TD flags, thermometer logging, Adam decay, no auto-fold. Batched trace gradient (1, 512) for ~10% overhead.

### Training RUNNING

```
checkpoint:     v15-zeroed (194.6M structural zeros)
output:         checkpoints/v15-zeroed-dolma/
data:           Dolma 2.7B tokens (54 shards) + 10% structured
batch:          2 × 4096 = 8,192 tok/step, ~928 tok/s
lr:             3e-4 (AdamW, warmup 500)
trace_weight:   0.1
TD:             flip_rate=0.001, warmup=100, interval=20
                no_block=True, min_confidence=0.3
S2:             thermometer + Adam decay (0.1) + cooldown
fold:           manual (thermometer says when)
tmux:           main:2
```

## Key session 177 findings

- **Structural zeros (30%) improve everything.** Removing irreducible fixed points: (a) gives TD cleaner canvas, (b) better trace loss after etching (0.071 vs 0.078), (c) 43% more leverage per flip.
- **no_block=True is essential.** Two-step staging would temporarily zero active program positions. With structural zeros in place, the remaining 70% must stay active. Direct ±1 flips only.
- **Fold is perfectly lossless.** Verified to 8 decimal places.
- **Batched trace gradient: 23 → 928 tok/s.** Per-plate gradient (99 passes) was broken. Batched all deltas into one pass. Then tiny trace batch (1, 512) for final speedup.
- **Static polysemantic detection fails.** Crystal basis spans 11/1280 dims (0.86%). Random vectors project identically to real neurons. The dynamic signal (TD flip-flop rate) is the correct detector — chronic oscillators ARE the polysemantic neurons.
- **Adam must be notified of flips.** Without moment decay on affected gamma rows, Adam pushes in the wrong direction for ~10 steps after topology changes. Surgical decay to 10% fixes the tug-of-war.
- **Crystal temperature is the fold signal.** When temperature → 0 with low oscillation, the crystal has solidified. When oscillation is high relative to temperature, remaining activity is grain-boundary noise. Both mean: done.

## The S2 anti-oscillation stack

| Layer | Mechanism | What it prevents |
|-------|-----------|-----------------|
| Static | Structural zeros (30%) | TD wasting budget on dead positions |
| Static | no_block=True | Zero staging killing active positions |
| Per-position | TD cooldown + backoff | Individual position flip-flop |
| Per-row | Adam moment decay (0.1) | Gamma tug-of-war after flips |
| Per-module | Holographic etch (equal thin slots) | Cross-layer incoherence |
| Per-step | flip_interval=20 | Adam moment staleness |
| Per-step | TD warmup=100 | Premature flips before calibration |
| Global | Crystal thermometer | Knowing when to fold |

## Next steps

### IMMEDIATE (session 178)

1. **Monitor training** — Watch loss curve, TD flips after warmup (step 100+), crystal temperature. First flips at step 120.
2. **Interpret thermometer** — What does the temperature curve look like? Does it decay? Plateau? Oscillate?
3. **Manual fold decision** — When thermometer shows settled, fold and compare topology.
4. **Generate from trained model** — Test fact retrieval, coherence.

### ONGOING

5. **Dynamic polysemantic detector** — Run diverse inputs through model, cluster per-neuron per-input activations. The static weight analysis failed (basis too narrow), but activation-space analysis would work.
6. **Orthonormalize crystal basis** — Gram-Schmidt for cleaner trace loss (coherence ∈ [0,1] instead of occasionally >1).
7. **Build verify.py** — Hologram reader on trained student vs teacher traces.

### RESEARCH

8. **Polysemantic neuron topology** — Are 3-way and 4-way splits real? Do they form reduction chains across strides? Needs dynamic analysis.
9. **TD flip targeting** — After training, which positions flipped? Do they cluster at grain boundaries or within crystal grains?
10. **Trace weight schedule** — Should trace_weight decay as NTP improves?
11. **Crystal temperature as annealing schedule** — Could flip_rate adapt to temperature instead of being fixed?

## Key assets

| Asset | Location | Status |
|-------|----------|--------|
| Delta plates | `scripts/v15/model.py` | ✅ enable/fold/collect |
| TernaryDescent + thermometer | `scripts/v15/td.py` | ✅ Full S2 stack |
| Trace-guided etch | `scripts/v15/etch.py` | ✅ Validated |
| Structural zeros | `scripts/v15/apply_zeros.py` | ✅ 194.6M zeros |
| Extraction with zeros | `scripts/v15/extract.py` | ✅ --zero-frac |
| Neuron mode detector | `scripts/v15/neuron_modes.py` | ⚠ Static fails, needs dynamic |
| Zeroed checkpoint | `checkpoints/v15-zeroed/` | ✅ Base for training |
| Train.py | `scripts/v15/train.py` | ✅ Full TD + S2 integration |
| Training run | `checkpoints/v15-zeroed-dolma/` | 🔄 Running tmux main:2 |

## What changed this session

| Change | Impact |
|--------|--------|
| **Structural zeros (30%)** | 194.6M irreducible fixed points zeroed. Cleaner TD. |
| **Delta plates** | `effective = plate ⊙ delta`, fold lossless |
| **TD for v15** | Float-plate TD, holographic etch, no_block=True |
| **Crystal thermometer** | Temperature + oscillation = fold signal |
| **Adam moment decay** | 90% reset on affected gamma rows after flips |
| **Batched trace gradient** | 23 → 928 tok/s |
| **etch.py** | Standalone topology correction |
| **apply_zeros.py** | Post-hoc zeros from 2-plate magnitude |
| **extract.py --zero-frac** | Zeros at extraction time |
| **Static poly detector** | Failed: basis too narrow (11/1280 dims). Dynamic needed. |

## Open questions

1. **What does the temperature curve look like?** First data at step 120+.
2. **Fold timing?** Temperature plateau → fold. But what's the threshold?
3. **Trace weight interaction?** Does 0.1 trace weight help or hurt NTP?
4. **Are multi-way splits (3rds, 4ths) real?** Needs dynamic activation analysis.
5. **Do reduction chains span strides?** Polysemantic neurons in one stride imply corresponding patterns in adjacent strides.
6. **Can the student retrieve facts after training?** (carried from 175)

## Knowledge map

Key pages for current direction:
- `trace-guided-etching.md` — **full implementation record** (sessions 176-177)
- `gradient-zero-map.md` — **35% oscillate, informed zero placement** (session 171)
- `extraction-sign-accuracy.md` — **signs 100%, four position classes** (session 173)
- `training-protocols.md` — **TD rules, fold cycle, failure modes** (accumulated)
- `crystal-universality.md` — **KIBC universal fixed points**
- `project-thesis.md` — **the central claim**
