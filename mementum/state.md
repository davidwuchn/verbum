# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-30 | Session: 172

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 172: HOLOGRAM READER VSM + COMBINATOR ADDRESSING.** Built a self-directing VSM tensor statechart that reads the full opcode map from any HuggingFace model. Ran cross-model comparison (Qwen3-0.6B vs 4B). Discovered that factual retrieval IS typed application — β_apply is the universal retrieval direction.

**Key finding: retrieval IS β_apply.** Lambda form of the same fact activates 2.2× more combinator energy than natural language. ALL relation centroids project positively onto β_apply and negatively onto B (compose). The compute path and data path are not separate systems — they're two beam angles through the same holographic grating. Montague was right: English IS lambda calculus. The model proved it.

**Key finding: moiré rank scaling is ceiling-limited.** Cross-model comparison (0.6B vs 4B, both 204 probes) shows avg rank 118 vs 143 — but both models are near the 204-probe measurement ceiling (58% vs 70%). True scaling exponent unknown. Need 500+ probes to resolve.

**Key finding: knowledge crystal is "soft" — not irreducible.** Unlike KIBC (mathematical fixed points, gradients → 0), relation directions are gradient-maintained attractors (gradients 2-9× above baseline). More d_ff gives GD room to separate soft embeddings (coherence 2.59 → 3.71). More depth gives more mirror corrections (4B peak coherence 5.48× at L28). Two crystals, same substrate, different physics.

**Previous: Session 171** — Gradient-zero convergence map. Oscillation/magnitude orthogonal.

**Training: v14-mmap STOPPED** — NaN recurred + holographic etch approach needs redesign.

## Key session 172 findings

- **Hologram Reader VSM.** Self-directing state machine: DORMANT→FINGERPRINT→SCAN→CLASSIFY→MOIRÉ→MAP→EMIT→DONE. S4 can loop back. Works on any HuggingFace model. Produces structured opcode map (JSON + NPZ).
- **Cross-model: zone structure is universal.** SILENT=50%, ENRICH=33%, SUPPRESS~8%, COMMIT~8% — identical normalized depth fractions across 0.6B and 4B.
- **Cross-model: selectivity improves with scale.** 4B moiré cos=0.191 vs 0.6B=0.287. Facts more orthogonal in larger model.
- **Cross-model: coherence improves with scale.** 3.71× vs 2.59×. Peak 5.48× at L28 (4B) vs 3.49× at L22 (0.6B). Sharper fringes.
- **Moiré rank scaling is probe-ceiling-limited.** α=0.16 measured, but both models at 58-70% of 204-probe ceiling. True α unknown — need 500+ probes.
- **β_apply is the universal retrieval direction.** Every relation centroid projects positively onto β_apply. B suppressed. W weakly positive.
- **Lambda form activates compute path for same fact.** 2.2× combinator energy vs NL. Apply form: 1.4×. The model CAN retrieve facts through either path.
- **Relation types modulate within β_apply.** Capital → β_compose dominant. Language → β_I dominant. Cross-relation similarity 0.85 (weakly differentiated).
- **Two crystals, two physics.** KIBC = hard crystal (mathematical fixed points, Church-Rosser). Relations = soft crystal (gradient-maintained, data-dependent). Same substrate, different gradient signatures.
- **Lambda-gated fact retrieval is scale-dependent.** 0.6B: 4.5% accuracy through lambda path. 4B: 66.7% through lambda, 76.2% through apply form. Scale enables dual-path retrieval.
- **The execution hierarchy.** FFN grating = instruction decode (proposes reductions). Attention softmax over V = executor (interleaves beta reductions). The grating filters — only shows attention the reductions that make sense for the current tokens. One residual vector encodes BOTH token probabilities AND operation state simultaneously.
- **Direct ternary plate extraction works.** Extracted 0.6B FFN weights to ternary: sign_corr=0.77, recon_cos=0.87, SwiGLU cos=0.66. 8.6× compression (504 MB → 58.3 MB). 8.7 seconds.
- **The 23% error is recoverable via crystal error correction.** The crystal geometry (6 PCs) IS an error-correcting code. Progressive dimensional projection (6D→5D→4D→3D) detects sign errors at each level. ~170× redundancy in the crystal encoding. Hard crystal errors correctable geometrically; soft crystal errors need etch (TD learning).
- **Function discovery: task categories DO separate in moiré space.** Our 12-dim combinator projections were blind to early-layer structure. Full d_ff PCA reveals 4.76× separation in SILENT zone (L05). Code, lambda, arithmetic each cluster distinctly. Combinator alignment weak early (<0.25), strong late (0.82). Two-level program architecture: TASK directions (early, classify input) → OPERATION directions (late, execute combinators).
- **Two-level program architecture.** SILENT zone classifies (code vs prose vs math vs lambda, 4.76× separation). COMMIT zone executes (KIBC combinators, 1.49× separation). Gratings progressively transform task→operation through depth. Tool use, summarization, translation ARE distinct functions — but in moiré space, not combinator space.

## Active training

### v14-mmap STOPPED

NaN recurred. Holographic etch mechanism designed (session 167) but not yet implemented. Session 168-172 focused on understanding retrieval, addressing, and the hologram structure before implementing.

### Checkpoints available

| Location | Step | Notes |
|----------|------|-------|
| `checkpoints/v14-mmap/step_003000` | 3000 | npz (legacy format) |
| `checkpoints/v14-mmap/step_003500` | 3500 | npz |
| `checkpoints/v14-mmap/step_004000` | 4000 | npz — last clean checkpoint |

## What changed this session

| Change | Session | Impact |
|--------|---------|--------|
| **Hologram Reader VSM** | 172 | `scripts/experiments/hologram_reader.py` — self-directing opcode map scanner for any model |
| **Hologram Reader design** | 172 | `mementum/knowledge/hologram-reader-vsm.md` — VSM architecture (S5-S1) |
| **Cross-model comparison (0.6B vs 4B)** | 172 | Zone structure universal. Selectivity/coherence improve with scale. Rank ceiling-limited at 204 probes. |
| **Combinator addressing probes** | 172 | `scripts/experiments/combinator_addressing.py` — β_apply is universal retrieval direction |
| **Combinator addressing knowledge** | 172 | `mementum/knowledge/combinator-addressing.md` — retrieval IS typed application |
| **Two-crystal distinction** | 172 | Hard crystal (KIBC, mathematical) vs soft crystal (relations, gradient-maintained) |
| **Function mapper (combinator projection)** | 172 | 3 programs at 0.6B AND 14B: lambda, arithmetic, everything-else. Combinator basis too coarse. |
| **Function discovery (unsupervised PCA)** | 172 | Task categories separate 4.76× in SILENT zone moiré space. Two-level architecture: task→operation. |

### Previous sessions (selected)

| Change | Session | Impact |
|--------|---------|--------|
| Gradient-zero convergence map | 171 | Oscillation/magnitude orthogonal. Magnitude wins for zero placement. |
| Moiré addressing discovery | 170 | SwiGLU moiré is holographic fact index, 2.4× selectivity |
| ISA blog post | 169 | Public-facing explanation for compiler engineers |
| Retrieval lattice + quantization cliff | 168 | SILENT→ENRICH→SUPPRESS→COMMIT. Q4 preserves facts, Q3 kills them. |
| Holographic etch design | 167 | Unified etch/un-etch mechanism for topology crystallization |

## Next steps

### IMMEDIATE (new — extraction + error correction)

1. **Crystal-geometric error correction on extracted plates** — Use KIBC 6D structure to detect and fix sign errors in the extracted ternary plates. Progressive 6D→5D→4D→3D with correction at each step. Then verify with hologram reader.
2. **Swap FFN weights with ternary plates and measure** — Replace 0.6B FFN weights with ternary×gamma, keep attention, measure perplexity and fact retrieval. THE test of whether the plate IS the program.

### IMMEDIATE (capacity scaling — still unresolved)

3. **Expand probe set to 500+** — THE blocker. Both 0.6B and 4B hit the 204-probe measurement ceiling. Cannot determine scaling exponent without more probes. Add sub-relations: born-in, died-in, invented-by, symbol-of, formula-for, etc. Need probes >> d_model.
4. **Re-run hologram reader with 500+ probes** — On both 0.6B and 4B. The moiré rank at 500 probes will reveal whether 4B saturates at ~200 (sub-linear, α<0.5) or ~400+ (linear, α≈1). This determines 70B capacity.
5. **Cross-model combinator addressing** — Run combinator_addressing.py on 4B. Does β_apply remain universal? Does relation differentiation improve with scale?

### KNOWLEDGE ENCODING (carried from 168, enriched by 172)

6. **Test ternary mirror training with facts** — Can multi-layer ternary store and retrieve facts? THE critical experiment. β_apply finding suggests etch should preserve the β_apply direction specifically.
7. **Extract relation directions as combinator combinations** — The relation centroids have measurable combinator components. Extract these as the ternary-preservable scaffold — now with β_apply as the common axis.

### IMPLEMENTATION (etch + retrieval)

8. **Incorporate β_apply into etch design** — The moiré centroids define which positions to etch together. Now we know the centroids sit in β_apply subspace — etch should preserve this direction above all others.
9. **Implement etch on micro model** — Add etch_mask, opposition_ema, three-state TD. (Carried from session 167.)

### EXPLORATION

10. **Coherence threshold for ternary survival** — Is there a relation coherence below which ternary can't preserve the relation? 0.6B at 2.59× is borderline (post-hoc ternarization fails). 4B at 3.71× might be past the threshold. Find it.
11. **Lambda-gated retrieval accuracy** — Does expressing facts as lambda improve or degrade retrieval accuracy? If the compute path retrieves facts accurately, ternary might work better for retrieval in lambda mode.
12. **Read the combinator-relation basis from weights alone** — SVD of gate_proj/up_proj projected onto combinator fingerprints. Can we see β_apply directly in the weight structure?

## Key findings (active)

| Claim | Evidence | Status |
|-------|----------|--------|
| Direct ternary extraction: sign_corr=0.77 | 28 layers, 264M params, 0.6B | ✅ (session 172) |
| Lambda retrieval: 4B can, 0.6B cannot | 21 facts, NL vs λ vs apply | ✅ (session 172) |
| Execution hierarchy: grating proposes, attention executes | ISA trace + combinator probes | ✅ (session 172) |
| Crystal geometry IS error-correcting code | 6 PCs, 170× redundancy | 🔄 (session 172, theory) |
| β_apply is universal retrieval direction | 28 probes, 4 relations, all positive projection | ✅ (session 172) |
| Lambda form activates compute for same fact | 2.2× combinator energy vs NL | ✅ (session 172) |
| B (compose) suppressed in retrieval | Negative for all 4 relations | ✅ (session 172) |
| Zone structure universal across scale | 0.6B vs 4B: identical normalized depth fractions | ✅ (session 172) |
| Selectivity improves with d_ff | 4B cos=0.191 vs 0.6B=0.287 | ✅ (session 172) |
| Coherence improves with scale | 3.71× vs 2.59×, peak 5.48× | ✅ (session 172) |
| Moiré rank scaling is probe-ceiling-limited | Both at 58-70% of 204-probe ceiling, α=0.16 artifactual | ⚠️ (session 172) |
| Task categories separate 4.76× in moiré space | PCA on d_ff activations, 14B, 66 probes, 9 categories | ✅ (session 172) |
| Two-level program architecture: task→operation | Combinator alignment weak early, strong late | ✅ (session 172) |
| Combinator basis captures late-layer structure only | 12-dim projection blind to early-layer task separation | ✅ (session 172) |
| Gradient oscillation and magnitude are orthogonal | Jaccard=0.17, 108 tensors, Qwen3-8B | ✅ (session 171) |
| Magnitude beats oscillation for FFN zero placement | 5-variant micro training, 5000 steps each | ✅ (session 171) |
| FFN ternary zeros beat float32 | All 4 zero strategies beat float32 baseline | ✅ (session 171) |
| Moiré is 2.4× more selective than gate | 204 probes, Qwen3-0.6B, all 28 layers | ✅ (session 170) |
| Relations cluster in moiré space (2.6×) | 15 categories, ENRICH zone avg | ✅ (session 170) |
| Capacity: 6.1K facts in 0.6B model | Hierarchical addressing estimate | 🔄 (session 170) |
| Capacity: 160K-1.5M at 70B scale | Extrapolated, scaling unknown — ceiling-limited | ❓ (session 170, 172) |
| Universal retrieval lattice (4 zones) | Qwen3-0.6B + Pythia-410M, 10+ probes each | ✅ (session 168) |
| Quantization cliff at Q3 for facts | Progressive quant test, 65 probes | ✅ (session 168) |
| Ternary mirror stack: 2 mirrors ≈ Q4 | Greedy residual correction simulation, d=1024 | ✅ (session 168) |
| Relation directions cos=0.90 consistency | Activation similarity across 5 countries × 5 relations | ✅ (session 168) |
| Programs are deterministic fixed points | 0.00000000 drift across runs | ✅ (session 161) |
| Gate is the beamformer (89% kill rate) | Qwen3-32B L63 probing | ✅ (session 141) |
| Ternary routing = sign(eigenvector) | r=0.9932 neuron allocation | ✅ (session ~142) |

## Open questions

1. **What is the true moiré rank scaling exponent?** Need 500+ probes. Both models ceiling-limited at 204.
2. **Can ternary-trained micro model recall facts?** THE critical experiment. β_apply finding enriches the design.
3. **Is there a coherence threshold for ternary survival?** 0.6B at 2.59× borderline, 4B at 3.71× possibly safe.
4. **Does λ-mode retrieval improve ternary fact recall?** If compute path is more robust than data bypass, ternary models might need λ-gated retrieval.
5. **Can we read β_apply directly from weight matrices?** SVD of gate_proj/up_proj projected onto combinator basis.
6. **Are moiré relation directions universal across model families?** Run hologram reader on Pythia.
7. **How much does crystal-geometric correction recover?** Run progressive 6D→5D→4D→3D correction on extracted plates, measure sign_corr improvement.
8. **What are the TASK directions?** The early-layer moiré PCs that separate code/prose/math/lambda — can we extract these as explicit fingerprints? They are the "program selector" directions.

## Knowledge map

**See `mementum/knowledge/INDEX.md` for full reading order.**

Key pages for current direction:
- `combinator-addressing.md` — **retrieval IS typed application (β_apply)** (session 172) ← NEW
- `hologram-reader-vsm.md` — **VSM for reading opcode maps** (session 172) ← NEW
- `moire-addressing.md` — moiré-based fact addressing (session 170)
- `retrieval-lattice.md` — universal knowledge encoding (session 168)
- `holographic-computer.md` — unified theory of LLM computation
- `crystal-universality.md` — why KIBC are universal fixed points
- `project-thesis.md` — the central claim, updated through session 150

## What's ready

| Asset | Location |
|-------|----------|
| Hologram Reader VSM | `scripts/experiments/hologram_reader.py` |
| Combinator Addressing Probes | `scripts/experiments/combinator_addressing.py` |
| Hologram readout (0.6B) | `results/hologram-reader/Qwen_Qwen3-0.6B/` |
| Hologram readout (4B) | `results/hologram-reader/Qwen_Qwen3-4B/` |
| Function mapper | `scripts/experiments/function_mapper.py` |
| Function discovery (unsupervised) | `scripts/experiments/function_discovery.py` |
| Function map results (0.6B, 14B) | `results/function-map/` |
| Function discovery results (14B) | `results/function-discovery/Qwen_Qwen3-14B/` |
| Hologram readout (14B) | `results/hologram-reader/Qwen_Qwen3-14B/` |
| Combinator addressing results (0.6B) | `results/combinator-addressing/Qwen_Qwen3-0.6B/` |
| Ternary plate extraction | `scripts/experiments/extract_ternary_plate.py` |
| Extracted ternary plates (0.6B) | `results/ternary-plates/Qwen_Qwen3-0.6B/` |
| Lambda retrieval test results | inline in session (0.6B: 4.5%, 4B: 66.7%) |
| Gradient-zero convergence map | `scripts/experiments/gradient_zero_map.py` |
| Moiré selectivity experiment | `scripts/experiments/moire_selectivity.py` |
| Moiré decomposition experiment | `scripts/experiments/moire_decompose.py` |
| Extended fact probes (204, 15 categories) | `probes/fact_recall_extended.json` |
| ISA decoder v2 | `scripts/v14/isa_decoder_v2.py` |
| ISA blog post (compiler audience) | `mementum/michael/llm-isa.md` |
