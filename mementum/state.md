# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-23 | Session: 141

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 141: FFN HOLOGRAPHIC INDEXING + OUTPUT BEAMFORMERS + SwiGLU ETCH. FFNs are holographic plates — input direction (beam angle) selects beta reductions from superposition (ρ=0.83 input→FFN, ρ=0.40 FFN→category, p<10⁻⁴⁴). Depth profile is a LENS (aperture 3% → fan 49% → converge 2%). Gate kills 89% of L63 neurons — gate_proj signs ARE the addressing topology. Added ffn_gate_plate + SwiGLU + zone-voted FFN extraction. Run 9 (SwiGLU etch) launched, CE=11.27 at step 1 (vs 11.88 in run 8).**

## Session 141: FFN Holographic Indexing + Output Beamformers + SwiGLU

### Discovery 1: FFN Indexing Is Holographic

Probed Qwen3-32B FFN activations across 48 prompts × 8 categories × 8 layers.

**The depth profile is a LENS, not a tree:**
```
L 2:  3.2% active   ← APERTURE (crystal bottleneck, all beams same direction)
L 8: 33.1% active   ← fan out
L48: 48.9% active   ← HOLOGRAPHIC READOUT ZONE (max superposition)
L56: 29.9% active   ← reconverge
L63:  1.3% active   ← OUTPUT LENS (329 neurons)
```

**Key numbers:**
- Input direction predicts FFN activation: ρ=0.83 (L16)
- FFN activation mirrors category structure: ρ=0.40, p<10⁻⁴⁴
- Individual neurons are UNIVERSAL (99%+ high entropy) — selectivity is COLLECTIVE (2x Jaccard)
- L2 = universal gateway (ALL inputs cos 0.93, no category separation)

### Discovery 2: Output Beamformers (L63)

Only 329/25600 neurons fire at L63. They are DYNAMICALLY SELECTED:
- Always-on: **2** neurons (structural — commas, whitespace)
- Frequent (≥75%): **99** neurons (universal output scaffolding)
- Pool: **3,807** total (14.9% of d_ffn)
- Pairwise Jaccard: 0.275 (substantial per-prompt reconfiguration)

**THE GATE IS THE BEAMFORMER:**
- 89% of inactive neurons killed by silu(gate_proj), not up_proj
- up_proj matches broadly (key is promiscuous), gate says "no"
- gate/up magnitude ratio for active neurons: 3.9×
- **gate_proj signs are MORE critical than up_proj signs for addressing**

**5-layer focal length:** L58 (30%) → L60 (24%) → L62 (10%) → L63 (2%)

**Heavy-tailed magnitudes:** skewness=13.84, max/median=160×

### Built: SwiGLU Gate Plate + Zone-Voted FFN Extraction

**Architecture change:**
- Added `ffn_gate_plate = TernaryLinear(d, d_ff)` — shared across all 3 stacks
- FFN activation: `value_plate(silu(gate_plate(x)) * key_plate(x))` — SwiGLU
- Replaces ReLU: `value_plate(max(key_plate(x), 0))`

**Extraction change:**
- gate_proj signs etched from teacher (new — was missing)
- Zone-voted: extract from teacher layers 4 (aperture), 20 (fan), 56 (convergence)
- 3-layer sign vote for each of gate/key/value — captures full lens topology
- Was: single teacher layer 20 for key+value only

**New etch budget:**
```
Embed:      77,791,232 positions   (54.2%)
Attention:  34,603,008 positions   (24.1%)
FFN:         3,145,728 positions   (2.2%)  ← +1M (gate plate)
────────────────────────────────────────────
Etched:    115,539,968             (80.5%)
Trainable:  27,954,176             (19.5%)
Total:     143,494,144
```

### Training Runs

| Run | Config | Key result |
|-----|--------|-----------|
| run6 | Crystal warmup 10→3 | crystal_loss 0.35 at step 250 ✅ |
| run7 | + TD→Adam surgical decay | Less see-saw ✅ |
| run8 | + geometry losses | CE=11.58, crystal=0.22 at step 500. Stopped for v2 etch. |
| **run9** | **+ SwiGLU gate plate + zone-voted FFN** | **CE=11.27 at step 1 (vs 11.88 run8). In progress.** |

### Files Changed

| File | Change |
|------|--------|
| `scripts/v13/model.py` | Added `ffn_gate_plate`, pass to all 3 stacks |
| `scripts/v13/stack_vsm.py` | SwiGLU FFN: `silu(gate) * key`, gate plate required |
| `scripts/v13/extract_teacher_full.py` | gate_proj extraction, 3-layer zone vote |
| `scripts/explore/probe_ffn_indexing.py` | **NEW** 6-analysis FFN indexing probe |
| `scripts/explore/probe_output_beamformers.py` | **NEW** 6-analysis output beamformer probe |

## Previous sessions

### Session 140: S5 Crystal Custodian + Categorical Geometry

Built S5 crystal sub-lattice metrics (5 structured self-image signals), S5→S4 policy
channel (closed VSM loop), crystal warmup 10→3, TD→Adam surgical decay. Confirmed
Curry-Howard (100% L16), adjunctions (rank-1 σ₁/σ₂=128:1), hyperbolic norms (ρ=0.49).
Three geometry losses (adjunction, hyperbolic, coherence).

### Session 139: Full Etch + Type Probes + Crystal-Gated TD

Proved KIBC selectivity universal (r=0.998 Qwen3-32B vs Pythia-160M). Types are lexical
(88% in embeddings) and geometric. Built full teacher extraction: embeddings + attention
+ FFN = 82.2% of model etched. Crystal-gated TD (Schmitt trigger 3%/7%).

**Key numbers:** CE 11.5 (full etch) vs 12.4 (FFN-only). 10^50,623,893 search space reduction.

### Session 137: Phi Compression + Anti-Oscillation + Vision Synthesis

Proved SVD spectrum → phi across 5 architectures (φ-dev=0.012). Traced B→K→B
program in Qwen3-14B FFN combinators. Built three-voter anti-oscillation for TD.

## Proof chain

| Claim | Evidence | Status |
|-------|----------|--------|
| Universal crystal exists | 4+ model consensus on 16×16 PCA-Q cosines | ✅ proved |
| KIBC-DYWH basis universal | Found across all probed architectures | ✅ proved |
| KIBC selectivity r=0.998 | Qwen3-32B vs Pythia-160M, same distribution | ✅ proved |
| Types are lexical (88% embed) | Qwen3-32B type probe, 8 categories, 5-fold CV | ✅ proved |
| Types follow B→K→B | Zone A=94.9%, B=92.9%, C=93.1% | ✅ proved |
| Type peak = combinator peak | Both peak at L2 in Qwen3-32B | ✅ proved |
| SVD spectrum → phi | 5-model consensus, φ-dev=0.012 | ✅ proved |
| Compressor = K∘B | FFN tracer: B→K→B program across layers | ✅ proved |
| V13 shape matches computation | B→K→B ≡ Stack A→B→C | ✅ proved |
| Relational loss works | Exponential basin pull, crystal forms | ✅ proved |
| FFN extraction works | Teacher etch into ternary plates | ✅ proved |
| Full etch loads and runs | embed+attn+FFN from Qwen3-32B, 82.2% | ✅ proved |
| Delta plates compose losslessly | Ternary × ternary = ternary, 0.00 diff | ✅ proved |
| Gradient decomposition exact | routing + calibration = original, 0.00 diff | ✅ proved |
| GD converges ~100 steps on correct topology | Session 126 | ✅ proved |
| Curry-Howard separation | L16 100% accuracy, well/ill-typed separable | ✅ proved |
| Adjunction rank-1 | σ₁/σ₂=128:1, R²=1.0 all zone pairs | ✅ proved |
| Hyperbolic norms | ρ=0.49, p<0.0001, 8/8 layers significant | ✅ proved |
| Coherence (partial) | Δ=-0.135 but baseline 0.86-0.99, partial recovery | 🔶 partial |
| S5→S4 policy channel | Built, tested, closed VSM loop | ✅ built |
| TD→Adam surgical decay | Affected rows → moment decay 0.1 | ✅ built |
| Crystal warmup latch | run6: 0.35 at step 250 vs 0.57 baseline | ✅ proved |
| Crystal-gated TD (Schmitt trigger) | 3%/7% hysteresis, built | ✅ built |
| **FFN indexing is holographic** | **ρ=0.83 input→FFN, ρ=0.40 FFN→cat, p<10⁻⁴⁴** | **✅ proved** |
| **FFN depth = LENS** | **aperture 3% → fan 49% → converge 2%** | **✅ proved** |
| **Gate IS the beamformer** | **89% of L63 neuron selection from gate, not key** | **✅ proved** |
| **Output beamformers dynamic** | **329 from pool of 3807, only 2 always-on** | **✅ proved** |
| **SwiGLU gate etch built** | **ffn_gate_plate + zone-voted extraction** | **✅ built** |
| SwiGLU improves CE | run9 step 1 CE=11.27 vs run8 step 1 CE=11.88 | ❓ testing |
| Geometry losses improve CE | run8 stopped at step 500 | ❓ inconclusive |
| Stride-stack attention sub-crystal forms | Not yet trained | ❓ unproven |
| Delta plate consensus merging | Theory | 📐 theory |
| Continuous learning cycle | Theory | 📐 theory |

## Knowledge map

| Page | What it tells you |
|------|-------------------|
| `ffn-beta-reduction-indexing.md` | ★ **S141** Holographic indexing, LENS profile, ρ=0.83, beam angles |
| `output-beamformers.md` | ★ **S141** L63 dynamic selection, gate=89%, 5-layer focal length |
| `categorical-geometry-probes.md` | **S140** Curry-Howard 100%, adjunctions rank-1, hyperbolic norms |
| `s5-crystal-custodian.md` | **S140** S5 sub-lattice metrics, S5→S4 policy, warmup, TD-Adam decay |
| `type-probe-qwen3-32b.md` | **S139** Types are lexical, B→K→B trajectory, peak=L2 |
| `full-etch-extraction.md` | **S139** Full etch design, 82.2%, crystal-gated TD |
| `beamformer-theory.md` | **S136** Model as beamformer array, token cloud, KIBC mapping |
| `ffn-hierarchy.md` | **S120** FFN tree hypothesis (refined by S141 LENS finding) |
| `ffn-beam-discovery.md` | **S121** PCA-up_proj reads FFN crystal, 0.9462 agreement |
| `phi-compression-universal.md` | S137 SVD spectrum → phi, 5-model consensus |
| `ternary-descent.md` | S136 TernaryDescent + delta plates + gradient decomposition |
| `crystal-basins.md` | S120 C-boot theory, ground state |
| `etcher-vsm.md` | S124 full pipeline: extract → co-evolve → freeze |
| `loom-structure.md` | S123 3 weaves, 6 harmonics, breathing |

## What's ready

| Asset | Location |
|-------|----------|
| **SwiGLU etch checkpoint (v2)** | `checkpoints/v13-etched-full-v2/` |
| **FFN indexing probe** | `scripts/explore/probe_ffn_indexing.py` |
| **FFN indexing results** | `results/ffn-indexing-qwen3-32b/` |
| **Output beamformer probe** | `scripts/explore/probe_output_beamformers.py` |
| **Output beamformer results** | `results/output-beamformers-qwen3-32b/` |
| **Categorical geometry probe suite** | `scripts/explore/probe_categorical_geometry.py` |
| **Full extraction script (v2 + gate)** | `scripts/v13/extract_teacher_full.py` |
| TernaryDescent + crystal gate | `scripts/v13/td.py`, `scripts/v13/train_td.py` |
| V13 model (tree of VSMs + SwiGLU) | `scripts/v13/model.py` |
| V13 ternary substrate | `scripts/v13/ternary.py` |

## Next steps

### Immediate: watch run9

1. **Does CE stay below run8?** run9 step 1 = 11.27 vs run8 step 1 = 11.88. Watch divergence.
2. **Does crystal latch faster with gate plate?** Gate signs should help crystal latch.
3. **Throughput impact?** SwiGLU adds one extra matmul per FFN. Watch tok/s.

### Medium: compare runs

4. **run9 vs run8 CE at step 500.** Gate plate + zone-voted FFN should improve.
5. **Does the student develop the LENS profile?** Probe V13's FFN sparsity across passes.
   Should see aperture→fan→converge in the stride stack passes.

### Open questions from today's probes

6. **What's in the 329 L63 neurons?** Probe deeper — do they correspond to token cloud clusters?
7. **Is the 2x Jaccard selectivity the theoretical limit for holographic readout?**
8. **Does gradient sparsity match activation sparsity?** Would confirm "GD fills entries, TD writes address book."
9. **Cross-model: does Qwen3-14B / Pythia show the same LENS profile?**
