# Session 141 — FFN Holographic Indexing + Output Beamformers + SwiGLU

> 2026-05-23 | The session that found the smoking gun for FFN addressing.

## Arc

Started exploring "how does the input index into the FFN?" Hypothesis: FFNs
are piles of beta reductions, gradients act as beamformer angles. Built two
probes, discovered the holographic lens profile and that the gate IS the
addressing mechanism. Evolved V13 architecture with SwiGLU + gate plate etch.
Launched run 9.

## Discoveries

### 1. FFN Indexing Is Holographic (probe_ffn_indexing.py)

48 prompts × 8 categories × 8 layers on Qwen3-32B.

**Depth profile is a LENS:**
- L2: 3.2% active (aperture — ALL beams same direction, cos=0.93)
- L8-L48: 33-49% active (fan — holographic readout, max superposition)
- L63: 1.3% active (converge — 329 neurons, prediction focus)

**Key numbers:**
- Input→FFN correlation: ρ=0.83 (L16) — beam angle predicts activation
- FFN→category correlation: ρ=0.40, p<10⁻⁴⁴ — preserves category structure
- Individual neurons: 99%+ universal (high entropy)
- Category selectivity: 2x Jaccard (collective, not individual)

**Refuted:** trunk→leaf tree hierarchy. Reality: aperture→fan→converge lens.
**Confirmed:** beam angle indexes the FFN. Typed input directions.

### 2. Output Beamformers (probe_output_beamformers.py)

**L63 neurons are dynamically selected:**
- Always-on: 2 (commas, whitespace — structural scaffolding)
- Frequent ≥75%: 99 (universal output ops)
- Pool: 3,807 / 25,600 (14.9%)
- Pairwise Jaccard: 0.275

**Gate IS the beamformer — THE smoking gun:**
- 89% of inactive neurons killed by silu(gate_proj)
- up_proj matches broadly (key is promiscuous)
- Gate/up magnitude ratio for active: 3.9×
- gate_proj signs = addressing topology

**5-layer focal length:** L58 (30%) → L60 (24%) → L62 (10%) → L63 (2%)
**Heavy-tailed:** skewness=13.84, max=160× median

### 3. Architectural Evolution

- Added `ffn_gate_plate = TernaryLinear(d, d_ff)` to V13Model
- SwiGLU: `value_plate(silu(gate_plate(x)) * key_plate(x))`
- Zone-voted FFN extraction: teacher layers 4, 20, 56 → sign vote
- +1M ternary positions (142.4M → 143.5M)
- Etched 80.5% of model (was 82.2% by count but without gate)

### 4. Run 9 Launched

CE=11.27 at step 1 (run 8 was 11.88). Gate plate etch helping immediately.

## Mechanistic Understanding Gained

```
FFN = holographic plate (beta reductions in superposition)
Input = beam angle (typed by category)
Gate = aperture selector (89% of neuron selection)
Key = content match (promiscuous, broadly active)
Output = resolved interference pattern (selected beta reduction)

TD flips = address rewrites (change which patterns the plate stores)
GD updates = amplitude calibration (tune contrast of stored patterns)
Crystal = aperture alignment (L2 bottleneck, must latch first)
```

The depth profile through the model is a LENS:
```
L0-L2:   APERTURE    3-8%    crystal gateway
L8-L48:  FAN         33-49%  holographic readout
L56-L63: CONVERGE    1-30%   prediction focus (5-layer focal length)
```

## Files Created/Modified

| File | Type | What |
|------|------|------|
| `scripts/explore/probe_ffn_indexing.py` | NEW | 6-analysis FFN indexing probe |
| `scripts/explore/probe_output_beamformers.py` | NEW | 6-analysis output beamformer probe |
| `results/ffn-indexing-qwen3-32b/` | NEW | FFN indexing results |
| `results/output-beamformers-qwen3-32b/` | NEW | Output beamformer results |
| `mementum/knowledge/explore/ffn-beta-reduction-indexing.md` | NEW | Holographic indexing finding |
| `mementum/knowledge/explore/output-beamformers.md` | NEW | Output beamformer finding |
| `scripts/v13/model.py` | MOD | Added ffn_gate_plate, pass to 3 stacks |
| `scripts/v13/stack_vsm.py` | MOD | SwiGLU FFN activation |
| `scripts/v13/extract_teacher_full.py` | MOD | gate_proj + zone-voted extraction |
| `checkpoints/v13-etched-full-v2/` | NEW | SwiGLU etch checkpoint |

## Commits

1. `💡 FFN indexing is holographic — beam angle selects beta reductions from superposition`
2. `💡 output beamformers — gate IS the holographic aperture selector`
3. `🎯 add ffn_gate_plate + SwiGLU + zone-voted FFN extraction`
4. `🌀 state.md` updates

## Open Questions for Next Session

1. Does run 9 CE curve stay below run 8?
2. Does the V13 student develop the LENS profile across its passes?
3. Gradient sparsity = activation sparsity? (GD fills entries, TD writes address book)
4. Cross-model LENS profile (Qwen3-14B, Pythia)?
5. What's in the 2 always-on L63 neurons specifically?
6. Is 2x Jaccard the theoretical limit for holographic readout selectivity?
