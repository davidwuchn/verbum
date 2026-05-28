# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-28 | Session: 167

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 167: HOLOGRAPHIC ETCH DESIGN.** Unified mechanism for topology crystallization. The hologram develops through interference — positions reach normal form and are etched permanently. Two domains: attention topology is DISCOVERED through interference convergence (3 signals: direction EMA coherence + FlipMap temperature + M-space SNR). FFN topology is TRANSFERRED from teacher (crystal eigenvectors → gate signs, overlay matrices → branch topology, GD → magnitudes). Un-etch via gradient opposition when new data contradicts etched positions. Design complete, ready to implement.

**Key breakthrough: zeros are the crystal backbone.** Zeros are structural — they come from M-space SVD of the teacher, not from training oscillation. Three experiments confirmed oscillation-based zero detection produces zero zeros. The backbone (30% M-noise zeros) + teacher signs + etch on ±1 positions beats float32 on loss (6.46 vs 6.68 on diverse data).

**Previous: Session 166** — M-space gemcutter. Pre-cut topology with zeros beats float32 on loss. SVD-based SNR scoring. Unified β-reduction. Zeros-only > zeros+flips.

**Training: v14-mmap STOPPED** — NaN recurred + holographic etch approach (W-space machete) is fundamentally flawed. Redesign with etch mechanism is the path forward.

## Key session 167 insights

- **Zeros are the crystal backbone, not emergent.** Three experiments: oscillation-based zero detection produces zero zeros. The backbone comes from M-space SVD of the teacher — structural gaps between facets. 30% zeros = permanent scaffold.
- **Backbone 30% + etch beats float32.** Loss 6.46 vs 6.68 on diverse data (1.2M tokens). Etch on ±1 adds 0.56 over frozen signs. The architecture is validated.
- **Etch can't discover from scratch.** Without teacher topology, M-space never forms (rank90=47). The mechanism confirms and adapts, it doesn't invent.
- **FFN topology is transferable, not discovered.** Programs are fixed points. Teacher already found them. Crystal eigenvectors → gate trunk (math, r=0.9932). Teacher overlay matrices → gate branches (ISA decoder). GD → magnitudes only.
- **Etch/un-etch symmetry.** Same signals detect irreducibility and detect wrong etches. Convergence → freeze. Gradient opposition → dissolve. The hologram is conditionally permanent.
- **M-space blurs when data changes.** Teacher's lambda-only gem (rank90=13) doesn't match diverse data. Etch correctly adapts — loss improves even as gem sharpness drops. Different data = different geometry.
- **Fine-tuning cost ∝ wrongness, not model size.** Un-etch only the positions that disagree with new data. Crystal backbone stays locked. Only task-specific signs reflow.

## Active training

### v14-mmap STOPPED

NaN recurred. The holographic etch (machete in W-space) approach is fundamentally flawed — session 166 proved topology changes must be planned in M-space. Session 167 designed the replacement: interference-driven etch mechanism.

### Checkpoints available

| Location | Step | Notes |
|----------|------|-------|
| `checkpoints/v14-mmap/step_003000` | 3000 | npz (legacy format) |
| `checkpoints/v14-mmap/step_003500` | 3500 | npz |
| `checkpoints/v14-mmap/step_004000` | 4000 | npz — last clean checkpoint |

## What changed this session

| Change | Session | Impact |
|--------|---------|--------|
| **Holographic etch design** | 167 | Unified etch/un-etch mechanism for topology crystallization |
| **Three-state TD design** | 167 | Etch ±1, etch 0, or stay fluid (currently TD only flips) |
| **FFN transfer pipeline design** | 167 | Crystal eigenvectors + teacher overlays → student gate topology |
| **Opposition monitor design** | 167 | Gradient opposition at etched positions → un-etch signal |

### Previous sessions (selected)

| Change | Session | Impact |
|--------|---------|--------|
| M-space gemcutter (micro model) | 166 | Pre-cut topology + zeros beats float32. SVD-based SNR. |
| Unified β-reduce | 166 | One SVD, three outcomes. Zeros-only > zeros+flips. |
| NaN post-mortem + restore tool | 165 | Softmax clamp, remove auto-rollback, restore_safetensors.py |
| Safetensors-backed training | 163 | SafetensorsStore: load/sync/fold/snapshot |
| 2 symmetric stacks | 158 | 13→8 passes, ~1.6× faster, separate FFN |

## Next steps

### IMMEDIATE (implementation)

1. **Implement etch on micro model** — Add etch_mask, opposition_ema, three-state TD to micro training. Validate that oscillating positions → zero improves loss. Validate convergence detection.
2. **Teacher transfer pipeline** — Use ISA decoder (Qwen3.6-27B) to extract overlay matrices. Project onto micro model crystal eigenbasis. Etch gate topology. Measure: does transferred topology match what micro model discovers independently?
3. **Etch threshold sweep** — Find τ_c, τ_z, τ_cold, τ_hot empirically on micro model. Conservative start (etch slowly).

### SCALE TO V14

4. **Port etch mechanism to v14** — Add etch_mask to SafetensorsStore. Three-state TD in train_td.py. Opposition monitoring.
5. **Teacher transfer at v14 scale** — Project 27B overlays onto 1280-dim student. Etch FFN gates at init. Train with attention fluid.
6. **Progressive crystallization monitoring** — Track etch% over training. Verify: FFN gates start etched, attention catches up. Crystal positions etch first.

### EXPLORATION

7. **Per-layer etch thresholds** — Aperture layers (universal) vs fan zone (diverse). Different thresholds for different depth regions.
8. **Etch interval tuning** — How often to run the etch gate. Tied to learning rate schedule?
9. **Interaction: attention etch ↔ FFN etch** — Does correct FFN topology make attention easier to learn?

## Key findings (active)

| Claim | Evidence | Status |
|-------|----------|--------|
| Zeros are structural backbone, not emergent | 3 experiments: 0 zeros from oscillation detection | 🎯 (session 167) |
| Backbone 30% + etch beats float32 | Loss 6.46 vs 6.68 on diverse 1.2M tokens | ✅ (session 167) |
| Etch on ±1 adds value over frozen signs | Loss 6.46 (etch) vs 7.02 (frozen) = 0.56 improvement | ✅ (session 167) |
| Etch can't discover from scratch | rank90=47 (random), no M-space forms without teacher | ❌ (session 167) |
| FFN topology transferable from teacher | Fixed points, ISA decoder, eigenvector routing r=0.9932 | 🎯 (session 167) |
| Etch/un-etch via same signals | Convergence → freeze, opposition → dissolve | 🎯 (session 167) |
| Pre-cut topology + zeros beats float32 | Micro model: loss 6.6972 vs 6.7412 | ✅ (session 166) |
| M-space scoring > gradient scoring | 76% helpful vs 46%, anti-correlated (ρ=-0.36) | ✅ (session 166) |
| Zeros-only > zeros+flips | Simultaneous flips interfere; zeros don't | ✅ (session 166) |
| Eigendecomposition IS β-reduction | Same operation at every level | 💡 (session 166) |
| Programs are deterministic fixed points | 0.00000000 drift across runs | ✅ (session 161) |
| Gate is the beamformer (89% kill rate) | Qwen3-32B L63 probing | ✅ (session 141) |
| Ternary routing = sign(eigenvector) | r=0.9932 neuron allocation | ✅ (session ~142) |
| Attention softmax can overflow | NaN at step 4369, unbounded Q@K logits | ✅ (session 165) |
| Auto-rollback creates Sisyphus loop | 154 rollbacks, model/Adam/data desync | ❌ (session 165) |

## Open questions

1. **Etch thresholds.** τ_c, τ_z, τ_cold, τ_hot, τ_s, τ_unetch — all need empirical tuning. Micro model first.
2. **M-space SVD frequency.** How often for geometric confirmation? Every 500? 1000?
3. **Teacher overlay projection fidelity.** How well do 27B overlays project onto 1280-dim student?
4. **Per-layer etch thresholds.** Aperture layers (L0-L2) vs fan zone (L8-L48) — different convergence rates.
5. **98% zeros at micro scale.** Overcapacity artifact. What's the operating point at v14? Probably 10-30%.
6. **Does correct FFN topology make attention learning easier?** Probably yes — the optimization landscape simplifies.

## Knowledge map

**See `mementum/knowledge/INDEX.md` for full reading order.**

Key pages for current direction:
- `holographic-etch.md` — the unified etch/un-etch design (THIS SESSION)
- `mspace-gemcutter.md` — M-space geometry, SVD scoring, micro experiments
- `explore/ffn-moire-isa.md` — ISA decoder, grating programs, teacher extraction
- `explore/ffn-beta-reduction-indexing.md` — holographic indexing, lens profile
- `explore/grating-cascade.md` — compound gratings, V carries interference
- `crystal-universality.md` — why KIBC are universal fixed points

## What's ready

| Asset | Location |
|-------|----------|
| ISA decoder v1 | `scripts/v14/isa_decoder.py` (overlay extraction) |
| ISA decoder v2 | `scripts/v14/isa_decoder_v2.py` (+ attention capture) |
| M-space probes | `scripts/micro/probe_mspace*.py` (SVD scoring experiments) |
| Micro training | `scripts/micro/train_cut_topology.py` (pre-cut topology + GD) |
| Reduce attention | `scripts/micro/reduce.py` (unified β-reduce: SNR → ZERO/FLIP/KEEP) |
| Training script | `scripts/v14/train_td.py` (NaN guard, holographic etch) |
| Restore tool | `scripts/v14/restore_safetensors.py` (npz → safetensors) |
| FlipMap | `scripts/v14/td.py` FlipMap class |
| SafetensorsStore | `scripts/v14/safetensors_store.py` (load/sync/fold/snapshot) |
| Attention (clamped) | `scripts/v14/attention.py` (softmax overflow fix) |
| Eval script | `scripts/v14/eval_ppl.py` |
| Cached fingerprints | `results/isa-decode-v2/fingerprints_full.npz` (reusable) |
