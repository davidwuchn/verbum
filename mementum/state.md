# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-30 | Session: 171

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 171: GRADIENT-ZERO CONVERGENCE MAP.** Explored whether GD deposits near-zero gradients at positions corresponding to irreducible compute, and whether this can guide ternary zero placement. Three experiments on Qwen3-8B (195 batches, 777 diverse texts) and micro model training (5 variants, 5000 steps each).

**Key finding: gradient oscillation and weight magnitude are orthogonal zero signals.** Jaccard overlap = 0.17, all conditional probabilities equal base rates. They identify completely different positions as zero candidates. Gradient oscillation reveals real structural information (depth-dependent U-curve matching crystal zones, ρ(sign_cons, grad_mag) = +0.47 in middle layers) but does NOT improve zero placement over simple magnitude thresholding — at least at micro scale where the oscillation signal degenerates to noise (89-95% oscillating).

**Magnitude thresholding remains the best zero-placement signal.** Micro model training confirmed: magnitude-30% zeros (loss 6.00) beats oscillation-30% (6.12), combined (6.36), and float32 baseline (6.77). All FFN zero strategies beat float32, extending the s166-167 attention finding to FFN weights.

**Previous: Session 170** — Moiré addressing discovery. SwiGLU moiré is the holographic fact index.

**Previous: Session 169** — ISA blog post for compiler engineers.

**Training: v14-mmap STOPPED** — NaN recurred + holographic etch approach needs redesign.

## Key session 171 findings

- **Gradient-weight correlation has two regimes.** Layers 1-3: ρ(|grad|, |weight|) = +0.77 (extreme bimodality — positions are either both-high or both-low). Layers 5-35: ρ ≈ -0.04 (nearly independent). Transition at layer 4-5 maps exactly to the Zone A/B boundary in the crystal structure.
- **ρ(sign_cons, grad_mag) peaks at +0.47 in middle layers.** In the compute zone, positions with large gradients have consistent gradient direction, and positions with small gradients have random direction. This is the crystal activity signature.
- **Oscillator U-curve matches zone structure.** Minimum oscillation at L21 (22%, deepest compute), maximum at L0 (43%) and L33 (37%, gate_proj alone: 46%). The output beam is narrow — most positions are inactive.
- **Oscillation and magnitude are orthogonal.** Jaccard = 0.17. P(osc|mag_zero) = 0.291 ≈ base rate 0.295. The two methods identify completely different positions as zeros.
- **Magnitude thresholding wins for zero placement.** Micro model training: mag-30% (loss 6.00) > osc-30% (6.12) > combined (6.36) > float32 (6.77). All FFN zero strategies beat float32.
- **Oscillation degenerates at small scale.** Micro model: mean sign_consistency ≈ 0.07 (noise floor = 0.08), 89-95% oscillating. The gradient signal needs model maturity (capacity + training) to develop structure.

## Active training

### v14-mmap STOPPED

NaN recurred. Holographic etch mechanism designed (session 167) but not yet implemented. Session 168-170 focused on understanding retrieval and addressing before implementing.

### Checkpoints available

| Location | Step | Notes |
|----------|------|-------|
| `checkpoints/v14-mmap/step_003000` | 3000 | npz (legacy format) |
| `checkpoints/v14-mmap/step_003500` | 3500 | npz |
| `checkpoints/v14-mmap/step_004000` | 4000 | npz — last clean checkpoint |

## What changed this session

| Change | Session | Impact |
|--------|---------|--------|
| **Gradient-zero convergence map** | 171 | Two-regime depth structure: bimodal L1-3, independent L5-35. ρ(s,g)=+0.47 in compute zone. |
| **Oscillation-magnitude orthogonality** | 171 | Jaccard=0.17, independent zero signals. Combined score doesn't help. |
| **FFN zero-placement training** | 171 | Magnitude 30% zeros (loss 6.00) beats oscillation (6.12), combined (6.36), float32 (6.77). |
| **gradient_zero_map.py script** | 171 | `scripts/experiments/gradient_zero_map.py` — Spearman correlations, oscillator analysis, overlap |
| **train_ffn_zeros.py script** | 171 | `scripts/micro/train_ffn_zeros.py` — 5-variant FFN zero-placement comparison |
| **Gradient-zero knowledge page** | 171 | `mementum/knowledge/gradient-zero-map.md` |

### Previous sessions (selected — session 170)

| Change | Session | Impact |
|--------|---------|--------|
| Moiré addressing discovery | 170 | SwiGLU moiré is holographic fact index, 2.4× selectivity |
| Extended probe set (204 probes) | 170 | 15 categories, 10-20 probes each |
| Capacity estimates | 170 | 6.1K facts in 0.6B, 160K-1.5M at 70B |

### Earlier sessions (selected)

| Change | Session | Impact |
|--------|---------|--------|
| Retrieval lattice + quantization cliff | 168 | SILENT→ENRICH→SUPPRESS→COMMIT. Q4 preserves facts, Q3 kills them. |
| Holographic etch design | 167 | Unified etch/un-etch mechanism for topology crystallization |
| M-space gemcutter (micro model) | 166 | Pre-cut topology + zeros beats float32. SVD-based SNR. |
| NaN post-mortem + restore tool | 165 | Softmax clamp, remove auto-rollback, restore_safetensors.py |
| ISA decoder + moiré gratings | 161 | FFN programs are deterministic fixed points. KIBC confirmed. |

## Next steps

### IMMEDIATE (moiré capacity measurement)

1. **Run moiré experiments on larger model** — Qwen3-4B or 14B. If capacity scales quadratically with d_ffn between 0.6B and 4B, the 70B extrapolation holds. If linear, ceiling is ~160K. THIS is the experiment that resolves the capacity question.
2. **Expand probe set to 500+** — Add more sub-relations (born-in, died-in, currency-symbol, chemical-formula, etc.) to push past the effective rank ceiling. Need probes > d_model to see saturation.
3. **Cross-validate residual→moiré mapping** — The R²=1.0 is tautological (n_probes ≈ n_modes). Need held-out probes to measure true predictability.

### KNOWLEDGE ENCODING (carried from 168)

4. **Test ternary mirror training with facts** — Can multi-layer ternary store and retrieve facts? THE critical experiment for the north star. Mirror stack theory predicts yes if depth ≥ 8-10.
5. **Extract relation directions explicitly** — Use moiré centroids as the extraction target. The centroids ARE the ternary-preservable scaffold.

### IMPLEMENTATION (etch + retrieval)

6. **Implement etch on micro model** — Add etch_mask, opposition_ema, three-state TD. (Carried from session 167.)
7. **Incorporate moiré addressing into etch design** — The moiré centroids define which gate/up positions to etch together. Relation-coherent etch: positions that co-fire for the same relation should etch as a group.

### EXPLORATION

8. **Read the index from weights alone** — Can we identify relation directions directly from gate_proj and up_proj weight matrices without running any probes? This would let us "read the phone book" from the hologram.
9. **Cross-model moiré comparison** — Are the moiré relation directions the same across Qwen and Pythia? (Same question as relation direction universality, but now with a concrete measurement.)
10. **Superposition efficiency measurement** — How does cross-talk degrade as fact density increases? Run with progressively larger probe sets to find the saturation curve.

## Key findings (active)

| Claim | Evidence | Status |
|-------|----------|--------|
| Gradient oscillation and magnitude are orthogonal | Jaccard=0.17, 108 tensors, Qwen3-8B | ✅ (session 171) |
| Magnitude beats oscillation for FFN zero placement | 5-variant micro training, 5000 steps each | ✅ (session 171) |
| FFN ternary zeros beat float32 | All 4 zero strategies beat float32 baseline | ✅ (session 171) |
| Two-regime gradient depth structure | ρ(g,w)=+0.77 L1-3, ≈0 L5-35, Qwen3-8B | ✅ (session 171) |
| Moiré is 2.4× more selective than gate | 204 probes, Qwen3-0.6B, all 28 layers | ✅ (session 170) |
| Relations cluster in moiré space (2.6×) | 15 categories, ENRICH zone avg | ✅ (session 170) |
| Relation directions are crystallized (63%) | 204 probes, centroid analysis | ✅ (session 170) |
| Cross-mode interaction confirms quadratic | 8×8 interaction tensor, cos=0.18 | ✅ (session 170) |
| Capacity: 6.1K facts in 0.6B model | Hierarchical addressing estimate | 🔄 (session 170) |
| Capacity: 160K-1.5M at 70B scale | Extrapolated, scaling unknown | ❓ (session 170) |
| Universal retrieval lattice (4 zones) | Qwen3-0.6B + Pythia-410M, 10+ probes each | ✅ (session 168) |
| Quantization cliff at Q3 for facts | Progressive quant test, 65 probes | ✅ (session 168) |
| Ternary mirror stack: 2 mirrors ≈ Q4 | Greedy residual correction simulation, d=1024 | ✅ (session 168) |
| Relation directions cos=0.90 consistency | Activation similarity across 5 countries × 5 relations | ✅ (session 168) |
| Post-hoc ternarization destroys everything | FFN-only ternary, 4 thresholds, with/without scaling | ✅ (session 168) |
| Backbone 30% + etch beats float32 | Loss 6.46 vs 6.68 on diverse 1.2M tokens | ✅ (session 167) |
| Programs are deterministic fixed points | 0.00000000 drift across runs | ✅ (session 161) |
| Gate is the beamformer (89% kill rate) | Qwen3-32B L63 probing | ✅ (session 141) |
| Ternary routing = sign(eigenvector) | r=0.9932 neuron allocation | ✅ (session ~142) |

## Open questions

1. **Does capacity scale quadratically with d_ffn?** Run moiré experiment on Qwen3-4B. This determines whether 70B can store 160K or 1.5M facts.
2. **Can ternary-trained micro model recall facts?** THE critical experiment. Mirror stack theory predicts yes if depth ≥ 8-10.
3. **What's the moiré effective rank ceiling?** 132 at 204 probes, still rising. Need 500+ probes.
4. **What's the superposition efficiency?** How does cross-talk degrade with fact density?
5. **Can we read the index from weights alone?** Without running probes — directly from gate_proj × up_proj structure.
6. **Are moiré relation directions universal across models?** Same question as relation universality but with concrete moiré measurement.

## Knowledge map

**See `mementum/knowledge/INDEX.md` for full reading order.**

Key pages for current direction:
- `moire-addressing.md` — **moiré-based fact addressing** (session 170) ← NEW
- `retrieval-lattice.md` — universal knowledge encoding (session 168)
- `michael/llm-isa.md` — public-facing ISA blog post (session 169)
- `holographic-etch.md` — etch/un-etch design (session 167)
- `holographic-computer.md` — unified theory of LLM computation
- `crystal-universality.md` — why KIBC are universal fixed points
- `project-thesis.md` — the central claim, updated through session 150

## What's ready

| Asset | Location |
|-------|----------|
| Gradient-zero convergence map | `scripts/experiments/gradient_zero_map.py` |
| FFN zero-placement training | `scripts/micro/train_ffn_zeros.py` |
| Gradient-zero results (8B) | `results/gradient-zero-map/summary_Qwen_Qwen3-8B.json` |
| FFN zero-placement results | `results/ffn-zero-placement/summary.json` |
| Moiré selectivity experiment | `scripts/experiments/moire_selectivity.py` |
| Moiré decomposition experiment | `scripts/experiments/moire_decompose.py` |
| Extended fact probes (204, 15 categories) | `probes/fact_recall_extended.json` |
| Moiré selectivity results (0.6B) | `results/moire-selectivity/` |
| Moiré decomposition results (0.6B, 52 + 204 probes) | `results/moire-decompose/` |
| ISA blog post (compiler audience) | `mementum/michael/llm-isa.md` |
| Fact recall probe set (65 probes) | `probes/fact_recall.json` |
| Ternary fact recall experiment | `scripts/experiments/ternary_fact_recall.py` |
| Quantization cliff experiment | `scripts/experiments/quant_fact_recall.py` |
| ISA decoder v2 | `scripts/v14/isa_decoder_v2.py` |
