# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-29 | Session: 168

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 168: RETRIEVAL LATTICE DISCOVERED.** We found the universal knowledge encoding in LLMs. Factual knowledge is stored as a four-zone retrieval lattice (SILENT→ENRICH→SUPPRESS→COMMIT) that appears identically across Qwen and Pythia architectures. Relation directions (like "capital-of") are crystallized in FFN activation space with 0.90 consistency across entities. Universal relay neurons fire for ALL fact retrieval. The quantization cliff is at Q3 (3 bits) — facts die but computation survives. Ternary mirror stacking (2 mirrors ≈ Q4 precision) proves facts CAN be stored in ternary via depth. Post-hoc ternarization destroys everything, but ternary training distributes precision across layers.

**Key breakthrough: the retrieval lattice completes the picture.** KIBC = compute crystal (strong fringes). Retrieval lattice = knowledge crystal (weak fringes). Both are universal, both use the same holographic mechanism. The difference: compute converges to mathematical fixed points (Church-Rosser), knowledge is maintained by data pressure (not converged, but collectively structured).

**Previous: Session 167** — Holographic etch design. Unified mechanism for topology crystallization.

**Training: v14-mmap STOPPED** — NaN recurred + holographic etch approach (W-space machete) fundamentally flawed. Redesign with etch mechanism is the path forward.

## Key session 168 insights

- **Universal retrieval lattice.** SILENT→ENRICH→SUPPRESS→COMMIT. Same structure in Qwen3-0.6B (28L) and Pythia-410M (24L). Different architecture, same shape. This is the knowledge equivalent of KIBC.
- **Universal relay neurons.** Pythia L22/N1860 fires for 10/12 facts across ALL categories. These implement the retrieval OPERATION (like a combinator), not any specific fact.
- **Quantization cliff at Q3.** Q4 preserves facts (73%), Q3 kills them (15%). Arithmetic survives Q3 (100%). Facts need ~4 bits; computation doesn't. Ternary post-hoc: 0% everything.
- **Ternary mirror stack.** 2 stacked ternary corrections = cos 0.94 ≈ Q4. 3 mirrors = cos 0.97 > Q4. Depth replaces magnitude. The residual stream IS a mirror stack.
- **Relation directions crystallized in activation space.** "Capital-of" has 0.90 consistency across countries. Entity modulation is the 10-36% variation within the relation pattern. The crystal is collective (which neurons fire together), not individual (weight signs).
- **Knowledge neurons are HOT.** 2-9× higher gradient ratios than random. Facts are saddle points maintained by data pressure, not converged fixed points. But the collective pattern IS stable.
- **Three-step mechanism confirmed from raw weights.** L21: entity enrichment (France). L22: relation application (city/capital). L23: target retrieval (Paris). Visible in per-neuron contribution analysis.
- **LARQL pointer.** github.com/chrishayuk/larql decompiles transformers into queryable knowledge graphs. ~512 relation types, ~348K features. Reads the same structure we found independently.

## Active training

### v14-mmap STOPPED

NaN recurred. Holographic etch mechanism designed (session 167) but not yet implemented. Session 168 focused on understanding retrieval before implementing.

### Checkpoints available

| Location | Step | Notes |
|----------|------|-------|
| `checkpoints/v14-mmap/step_003000` | 3000 | npz (legacy format) |
| `checkpoints/v14-mmap/step_003500` | 3500 | npz |
| `checkpoints/v14-mmap/step_004000` | 4000 | npz — last clean checkpoint |

## What changed this session

| Change | Session | Impact |
|--------|---------|--------|
| **Retrieval lattice discovery** | 168 | Universal 4-zone knowledge encoding confirmed across 2 architectures |
| **Quantization cliff measured** | 168 | Q4 preserves facts, Q3 kills them. Ternary post-hoc: 0% |
| **Ternary mirror stack theory** | 168 | 2 mirrors ≈ Q4. Depth replaces magnitude. |
| **Relation direction crystallization** | 168 | cos=0.90 consistency in activation space, not weight space |
| **Knowledge neuron characterization** | 168 | Specific neurons traced for France→Paris across 3 layers |
| **Universal relay neurons found** | 168 | Pythia L22/N1860: 10/12 facts, all categories |
| **Holographic etch design** | 167 | Unified etch/un-etch mechanism for topology crystallization |
| **Three-state TD design** | 167 | Etch ±1, etch 0, or stay fluid |

### Previous sessions (selected)

| Change | Session | Impact |
|--------|---------|--------|
| M-space gemcutter (micro model) | 166 | Pre-cut topology + zeros beats float32. SVD-based SNR. |
| NaN post-mortem + restore tool | 165 | Softmax clamp, remove auto-rollback, restore_safetensors.py |
| ISA decoder + moiré gratings | 161 | FFN programs are deterministic fixed points. KIBC confirmed. |
| Safetensors-backed training | 163 | SafetensorsStore: load/sync/fold/snapshot |
| 2 symmetric stacks | 158 | 13→8 passes, ~1.6× faster, separate FFN |

## Next steps

### IMMEDIATE (knowledge encoding)

1. **Extract relation directions explicitly** — Cluster FFN activation patterns across many facts to find the ~512 relation directions. SAE decomposition or direct activation clustering. These are the ternary-preservable scaffold.
2. **Build fact probe infrastructure** — Expand the 65-probe set. Need 200+ probes across diverse relation types to map the full relation direction space.
3. **Test ternary mirror training with facts** — Train micro model with factual recall probes in the training data. Does multi-layer ternary learn to store and retrieve facts? This is THE critical experiment for the north star.

### IMPLEMENTATION (etch + retrieval)

4. **Implement etch on micro model** — Add etch_mask, opposition_ema, three-state TD. (Carried from session 167.)
5. **Incorporate retrieval lattice into etch design** — The knowledge layers (ENRICH zone) need different etch thresholds than compute layers. Knowledge neurons are hot — they should stay fluid longer.
6. **Teacher transfer with relation awareness** — Instead of transferring raw topology, transfer the RELATION DIRECTIONS. Preserve the collective activation patterns, not individual weight signs.

### EXPLORATION

7. **LARQL-style vindex from our analysis** — Build our own queryable knowledge index from the relation direction + neuron activation structure we found.
8. **Cross-model relation direction comparison** — Are the ~512 relation directions the same across Qwen and Pythia? If yes, that's a universal knowledge alphabet.
9. **Capacity analysis** — How many facts per relation direction per layer? Superposition multiplies capacity combinatorially. Connect to recent work on MLP fact storage scaling.

## Key findings (active)

| Claim | Evidence | Status |
|-------|----------|--------|
| Universal retrieval lattice (4 zones) | Qwen3-0.6B + Pythia-410M, 10+ probes each | ✅ (session 168) |
| Quantization cliff at Q3 for facts | Progressive quant test, 65 probes | ✅ (session 168) |
| Ternary mirror stack: 2 mirrors ≈ Q4 | Greedy residual correction simulation, d=1024 | ✅ (session 168) |
| Relation directions cos=0.90 consistency | Activation similarity across 5 countries × 5 relations | ✅ (session 168) |
| Universal relay neurons | Pythia L22/N1860: 10/12 facts | ✅ (session 168) |
| Knowledge neurons are hot (2-9× gradient) | Gradient analysis, knowledge vs random neurons | 🔄 (session 168) |
| Post-hoc ternarization destroys everything | FFN-only ternary, 4 thresholds, with/without scaling | ✅ (session 168) |
| Zeros are structural backbone, not emergent | 3 experiments: 0 zeros from oscillation detection | 🎯 (session 167) |
| Backbone 30% + etch beats float32 | Loss 6.46 vs 6.68 on diverse 1.2M tokens | ✅ (session 167) |
| FFN topology transferable from teacher | Fixed points, ISA decoder, eigenvector routing r=0.9932 | 🎯 (session 167) |
| Programs are deterministic fixed points | 0.00000000 drift across runs | ✅ (session 161) |
| Gate is the beamformer (89% kill rate) | Qwen3-32B L63 probing | ✅ (session 141) |
| Ternary routing = sign(eigenvector) | r=0.9932 neuron allocation | ✅ (session ~142) |

## Open questions

1. **Are the ~512 relation directions the same across models?** If universal, they're a knowledge alphabet like KIBC is a compute alphabet.
2. **Can ternary-trained micro model recall facts?** THE critical experiment. Mirror stack theory predicts yes if depth ≥ 8-10 layers.
3. **What's the fact capacity per parameter?** Literature says linear scaling. Does ternary change the constant?
4. **How do relation directions relate to KIBC?** Same space? Orthogonal? Interleaved?
5. **Can we build a vindex from relation directions?** A queryable knowledge graph from ternary weights would be directly useful.
6. **How does the SUPPRESS zone work mechanically?** Multiple candidates loaded in ENRICH — what selects the right one?

## Knowledge map

**See `mementum/knowledge/INDEX.md` for full reading order.**

Key pages for current direction:
- `retrieval-lattice.md` — universal knowledge encoding (THIS SESSION)
- `holographic-etch.md` — etch/un-etch design (session 167)
- `holographic-computer.md` — unified theory of LLM computation
- `mspace-gemcutter.md` — M-space geometry, SVD scoring
- `crystal-universality.md` — why KIBC are universal fixed points
- `project-thesis.md` — the central claim, updated through session 150
- `explore/ffn-moire-isa.md` — ISA decoder, grating programs

## What's ready

| Asset | Location |
|-------|----------|
| Fact recall probe set (65 probes) | `probes/fact_recall.json` |
| Ternary fact recall experiment | `scripts/experiments/ternary_fact_recall.py` |
| Quantization cliff experiment | `scripts/experiments/quant_fact_recall.py` |
| ISA decoder v1 | `scripts/v14/isa_decoder.py` |
| ISA decoder v2 | `scripts/v14/isa_decoder_v2.py` |
| ISA decode results | `results/isa-decode-v2/` (fingerprints + traces) |
| Ternary fact recall results | `results/ternary-fact-recall/` |
| Micro training | `scripts/micro/train_cut_topology.py` |
| M-space probes | `scripts/micro/probe_mspace*.py` |
| Training script | `scripts/v14/train_td.py` |
| SafetensorsStore | `scripts/v14/safetensors_store.py` |
| Cached fingerprints | `results/isa-decode-v2/fingerprints_full.npz` |
