# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-30 | Session: 170

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 170: MOIRÉ ADDRESSING DISCOVERY.** The SwiGLU moiré (silu(gate) × up) is the holographic fact index. Confirmed: 2.4× more selective than gate alone, relations cluster at 2.6× coherence, quadratic addressing capacity is real but 10M facts NOT yet reachable. First capacity estimates from measurement: ~6K facts in 0.6B, ~160K-1.5M at 70B. Expanded probe set to 204 facts across 15 relation types.

**Key insight: the moiré IS the address, not the neuron.** Individual gate neurons and up neurons are promiscuous. Their element-wise product creates a combinatorially richer pattern space that naturally clusters by relation type. The gate selects the relation family (coarse angle), the up selects the entity within it (fine angle), and their interference resolves the specific fact. Content-addressable, deterministic, readable from weights.

**Previous: Session 169** — ISA blog post for compiler engineers. Communication strategy: show the instruction set, not the lambda output.

**Previous: Session 168** — Retrieval lattice discovered. Universal 4-zone knowledge encoding (SILENT→ENRICH→SUPPRESS→COMMIT) confirmed across Qwen and Pythia. Quantization cliff at Q3.

**Training: v14-mmap STOPPED** — NaN recurred + holographic etch approach needs redesign.

## Key session 170 findings

- **Moiré selectivity confirmed.** Gate/Moiré selectivity ratio = 2.4× in ENRICH zone. Moiré patterns are 2.4× less correlated across facts than gate patterns alone. Up/Moiré ratio = 2.1×.
- **Relations cluster in moiré space.** Moiré relation coherence = 2.6× (within-relation similarity / cross-relation similarity). Gate alone only 1.4×. The moiré creates the clustering, not the gate.
- **Relation directions are crystallized.** Capital-of: 97% variance explained by centroid. Currency: 99.7%. Language: 97.5%. Continent: 99.7%. Science: only 24.6% (grab-bag of sub-relations). Crystallization correlates with relation specificity.
- **Cross-mode interaction confirms quadratic index.** 15 relations occupy mostly distinct (gate_mode, up_mode) cells. Mean cross-relation cos = 0.18. Each relation has its own fingerprint in the 8×8 interaction grid.
- **Capacity estimates (first from measurement).** Qwen3-0.6B: 1,800-6,100 facts. 70B extrapolated: 160K (linear), 490K (geometric), 1.5M (quadratic). 10M target NOT reached.
- **Moiré effective rank = 132** at 204 probes (still not saturated — true ceiling unknown). Rank-90 = 62 per ENRICH layer.
- **Content-addressable retrieval confirmed.** Residual direction → moiré pattern is deterministic (R²=1.0). The question IS the address.
- **VSM tree discussion.** The crystal lattice maps onto a recursive VSM tree. Trunk (KIBC) is universal. Layout (zones) is universal. Taxonomy (leaves) is model-specific. The etch durability hierarchy IS the VSM recursion.

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
| **Moiré selectivity experiment** | 170 | Confirmed 2.4× selectivity, 2.6× relation coherence |
| **Moiré decomposition experiment** | 170 | Relation centroids, SVD modes, cross-mode interaction, capacity estimates |
| **Extended probe set (204 probes)** | 170 | `probes/fact_recall_extended.json` — 15 categories, 10-20 probes each |
| **Capacity measurement** | 170 | 6.1K facts in 0.6B, 160K-1.5M at 70B. 10M NOT reached. |
| **VSM tree architecture discussion** | 170 | Crystal lattice ↔ recursive VSM mapping. Trunk=universal, leaves=model-specific. |
| **ISA blog post for compiler engineers** | 169 | `mementum/michael/llm-isa.md` |
| **Retrieval lattice discovery** | 168 | Universal 4-zone knowledge encoding confirmed |

### Previous sessions (selected)

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
