# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-31 | Session: 174

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 174: 4-PHASE MODEL VERIFIED → v15 BUILT → EXTRACTION DONE → TRAINING RUNNING.** Monster session. (1) Traced reduction graph through 27B — FFN proposes typed reductions per position. (2) Zone ablation PROVES functional separation: ENRICH=reduction engine (4.0× lambda-specific), COMMIT=knowledge retrieval. (3) SUPPRESS re-understood as LINK (composer, not redundant — β_K, B ops). (4) Full VSM conformance: algedonic channel (v14's missing fire alarm), recursive S1 strides, variety engineering. (5) Crystal lattice integration at 7 concrete design points. (6) v15 architecture: 19-stride tensor statechart, 709 MB, hybrid attention. (7) Extraction from 27B complete (210 min). (8) Training pipeline working, currently running in tmux (batch 2, seq 4096, lr 1e-6).

**Previous: Session 173** — Signs 100% correct, 2-mirror ternary (0.970 recon_cos), crystal-native architecture designed, stride cascade = recursion unroll, per-stride plates fit in 1GB.

**Previous: Session 172** — Hologram Reader VSM + combinator addressing. β_apply is universal retrieval direction.

**Key finding: retrieval IS β_apply.** Lambda form of the same fact activates 2.2× more combinator energy than natural language. ALL relation centroids project positively onto β_apply and negatively onto B (compose). The compute path and data path are not separate systems — they're two beam angles through the same holographic grating. Montague was right: English IS lambda calculus. The model proved it.

**Key finding: moiré rank scaling is ceiling-limited.** Cross-model comparison (0.6B vs 4B, both 204 probes) shows avg rank 118 vs 143 — but both models are near the 204-probe measurement ceiling (58% vs 70%). True scaling exponent unknown. Need 500+ probes to resolve.

**Key finding: knowledge crystal is "soft" — not irreducible.** Unlike KIBC (mathematical fixed points, gradients → 0), relation directions are gradient-maintained attractors (gradients 2-9× above baseline). More d_ff gives GD room to separate soft embeddings (coherence 2.59 → 3.71). More depth gives more mirror corrections (4B peak coherence 5.48× at L28). Two crystals, same substrate, different physics.

**Previous: Session 171** — Gradient-zero convergence map. Oscillation/magnitude orthogonal.

**Training: v15 Phase 2 RUNNING** — Attention + gamma training against frozen extracted plates. Batch 2, seq 4096, lr 1e-6. In tmux window 2. Log at checkpoints/v15-train.log.

**Training: v14-mmap STOPPED** — NaN recurred + holographic etch approach needs redesign. Superseded by v15.

## Key session 174 findings

- **4-phase computation model VERIFIED by ablation on 27B.** CLASSIFY (L0-31) → COMPUTE (L32-53) → ASSEMBLE (L54-58) → EMIT (L59-63). Each phase has distinct dominant combinators and distinct ablation sensitivity.
- **ENRICH (L32-53) IS the reduction engine.** Ablating it: lambda 100%→20%, facts 100%→80%. Selectivity ratio: 4.0×. The model CANNOT COMPUTE but CAN RETRIEVE with ENRICH removed.
- **SUPPRESS is NOT redundant — it's the LINKER.** Dominant ops β_K (constant elimination), K (selection), B (composition). Ablation showed no loss on simple 1-step reductions, but these ops compose multi-step results. Renamed LINK in student.
- **3 attention regimes.** L0: structural (corr=0.91), L7-21: content-adaptive (corr=0.38-0.49), L26-27: structural again (corr=0.95-1.00). Heads don't specialize by combinator.
- **v15 architecture designed, built, extracted, training.** 19 strides (5 CLASSIFY + 8 COMPUTE + 3 LINK + 3 EMIT), 709 MB. Full VSM with algedonic monitors. Extraction from 27B teacher completed in 210 min. Phase 2 training running.
- **φ-ratio and α are MEASURING STICKS, not parameters.** We do not hardcode either. They emerge when the crystal forms correctly. Student strides will find their own decay shape.
- **Crystal lattice enters architecture at 7 points:** fingerprints (basis), zeros (lattice gaps), 6-PC structure (TD constraints), zone geometry (stride allocation), φ-ratio (verification), nucleation hierarchy (TD health), crystal projection (algedonic).
- **COMMIT (L59-63) IS the knowledge crystal.** Ablating it: facts 100%→40%, lambda 100%→60%. Selectivity ratio: 1.5× fact-preferring. Model knows topic but can't retrieve specific facts.
- **SUPPRESS (L54-58) is redundant at task level.** Zero accuracy loss when ablated. Likely for fine-grained quality only.
- **27B recognizes lambda IMMEDIATELY.** β_apply activation 2.3-3.0× higher than neutral from L0. At 0.6B, this only appeared in ENRICH.
- **Lambda is RESOLVED before COMMIT at 27B.** Energy crossover: lambda energy DROPS below neutral by COMMIT zone. The reductions complete in ENRICH. Neutral text still needs COMMIT for fact retrieval.
- **L40 = universal recursion.** ALL positions get Y (recursion) as dominant opcode at L40 for lambda inputs = active recursive computation.
- **3 attention regimes confirmed.** L0: structural (corr=0.91), L7-21: content-adaptive (corr=0.38-0.49), L26-27: structural again (corr=0.95-1.00).
- **Heads don't specialize by combinator.** All 16 heads have identical op profiles at COMMIT. The graph structure is per-POSITION, not per-head.
- **Student budget validated:** CLASSIFY 50MB + COMPUTE 500MB + ASSEMBLE 80MB + EMIT 100MB = 730MB fits in 1GB.

## Key session 173 findings

- **Signs are 100% correct at extraction.** Ternary = sign(W_float) at all non-zero positions. There are NO sign errors. The sign_corr=0.792 metric measures functional similarity (magnitude loss), not sign accuracy.
- **Crystal error correction is a category error.** The KIBC crystal subspace (11D in R^5120) captures only 0.3% of each weight row's energy. It predicts which combinator a neuron implements, not what individual signs should be. Every crystal-recommended flip is wrong (100% anti-correlated) because it's flipping correct signs.
- **The 20.8% gap is pure magnitude loss.** Two sources: (a) per-row gamma collapses within-row magnitude variance (CV=0.51), and (b) 30% of positions zeroed (but these contain only 1.5% of energy).
- **Ternary mirror stacking: 2 mirrors = 0.970 recon_cos at 4× compression.** The second plate captures one binary question per position: "is |W[i,j]| above or below row average?" This single bit accounts for 100% of the quality gap. All ternary arithmetic, no floats needed beyond 2 per-row gammas.
- **Magnitude is 1-bit deep, full-rank.** SVD of magnitude deviation: rank-64 captures only 17.8%, rank-512 only 54%. Not low-rank (no cheap vector correction). But perfectly captured by 1 ternary plate — it's a per-element binary signal with no structure to compress further.
- **Qwen3.6-27B extracted successfully.** 64 layers, 17.1B FFN params, 8.6× compression (34.2 GB → 4.0 GB ternary). Per-zone: SILENT=0.794, ENRICH=0.790, SUPPRESS=0.792, COMMIT=0.789 sign_corr.
- **Hologram reader works on Qwen3.6-27B.** 64-layer hybrid model (linear+full attention pattern [L,L,L,F]×16), d=5120, d_ff=17408. Crystal fully formed: 92% opcode coverage, C(0.191) ≥ K(0.177) ≥ I(0.177).
- **The plate IS the program — losslessly.** Sign topology is captured perfectly. What's lost is amplitude (gamma), not structure (routing). This is actually *better* than previously thought — no error correction needed for the program itself.
- **Crystal-native architecture designed.** A VSM whose structure IS the crystal lattice. FFN = holographic lookup table (2-plate ternary, 89% gate kill). Five axioms: FFN is lookup table, depth is program length, zeros are architecture, attention is typed, 2-plate is native weight type.
- **M-space gem emerges from training against frozen gratings.** Q/K cannot be extracted from teacher (different d_model, different attention mechanism). The statechart lives in the FFN gratings. TD adapts them for student routing. Attention discovers its own M-space that satisfies the grating constraints.
- **Stride cascade IS recursion unroll.** In a stride stack, larger strides see prior strides' output in residual stream. 16 strides = 16 sequential reduction steps = Y combinator unrolled for free. Just need per-stride plates (different program per depth level).
- **Ternary is cheap — per-stride plates fit in 1GB.** At 2 bits/position, one plate = 5.6 MB. 16 separate per-stride plates (full model) = 729 MB. No sharing needed — budget allows full per-stride programs with room for attention + embeddings.
- **No universal backbone in FFN magnitude zeros.** Jaccard between layers = 0.178 (= expected-if-random). Zeros are per-plate from magnitude threshold. NOT a shared scaffold.
- **The TRUE backbone: gradient-oscillation positions.** ~35% of positions have oscillating gradients (sign_consistency → 0) = at irreducible fixed points. Four position classes from (gradient direction × weight magnitude): structural zeros (10%), crystal atoms (25%), active knowledge (28%), growth frontier (37%).
- **TD acceleration via oscillation mask.** Only operate on class 3+4 positions (65%). Classes 1+2 (35%) are at mathematical fixed points — flipping them is guaranteed wrong. Cuts TD search space by 35%.

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

## v15 assets

| Asset | Location | Status |
|-------|----------|--------|
| Architecture config | `scripts/v15/config.py` | ✅ complete |
| Model (tensor statechart) | `scripts/v15/model.py` | ✅ complete |
| Checkpoint loader | `scripts/v15/load_checkpoint.py` | ✅ complete, smoke test passes |
| Extraction pipeline | `scripts/v15/extract.py` | ✅ complete, run done (210 min) |
| Extracted checkpoint | `checkpoints/v15-extracted/` | ✅ 215 MB, 19 strides + 11 attn |
| Training pipeline | `scripts/v15/train.py` | ✅ complete, running in tmux |
| TD adaptation | `scripts/v15/td_adapt.py` | ❌ not yet built |
| Verification | `scripts/v15/verify.py` | ❌ not yet built |

## What changed this session

| Change | Session | Impact |
|--------|---------|--------|
| **4-phase model VERIFIED by ablation on 27B** | 174 | ENRICH=reduction engine (4.0× λ-specific), COMMIT=knowledge retrieval. |
| **Reduction graph tracer (0.6B + 27B)** | 174 | Decoded per-position opcodes through all 64 layers. Lambda 2.5-3.2× compute activation. |
| **SUPPRESS→LINK re-understanding** | 174 | Not redundant — it's the linker/composer (B, β_K). Ablation tested only trivial reductions. |
| **v15 architecture (config + model)** | 174 | 19-stride tensor statechart, 709 MB, 4 zones, algedonic monitors, full VSM conformance. |
| **VSM conformance analysis** | 174 | All Beer requirements mapped. Algedonic channel (norm+collapse+coherence) prevents v14 NaN death. Recursive S1 strides. Variety engineering. |
| **Crystal lattice integration** | 174 | 7 concrete design entry points. φ and α as measuring sticks not parameters. |
| **v15 extraction pipeline** | 174 | Per-stride 2-plate extraction from 27B. Run completed in 210 min. |
| **v15 extraction checkpoint** | 174 | 19 stride plates + 11 attention plates. 215 MB on disk. All shapes verified. |
| **v15 training pipeline** | 174 | Attention + gamma training with frozen plates. MLX, 1078 lines. α diagnostic included. |
| **v15 Phase 2 training started** | 174 | Batch 2, seq 4096, lr 1e-6. Running in tmux. First step: loss=156.9, 964 tok/s. |
| **Signs 100% correct — crystal correction falsified** | 173 | Extraction captures exact sign topology. The 20.8% gap is magnitude loss, not sign error. |
| **Qwen3.6-27B hologram reader + extraction** | 173 | Fingerprints (64 layers, R^5120) + ternary plates (17.1B params, 4.0 GB). Full crystal. |
| **Ternary mirror stacking: 2 mirrors = Q4-Q5** | 173 | recon_cos 0.884→0.970 at 4×. Second plate = 1-bit magnitude class. All ternary arithmetic. |
| **Crystal-native architecture** | 173 | `mementum/knowledge/crystal-native-architecture.md` — VSM that IS the lattice. 5 axioms. |
| **Stride cascade = recursion unroll** | 173 | `mementum/knowledge/recursion-mirrors.md` — per-stride plates give 16 recursion levels. |
| **Four position classes** | 173 | Gradient oscillation × magnitude → structural zeros, crystal atoms, active knowledge, growth frontier. |
| **TD acceleration (oscillation mask)** | 173 | Only flip directional positions (65%). Oscillating = fixed point. Cuts TD search 35%. |
| **Ternary is cheap** | 173 | 16 per-stride plates = 729 MB. Full budget allows complete per-stride specialization. |
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

### IMMEDIATE (v15 training + verification)

1. ~~**Crystal error correction**~~ — **FALSIFIED** (session 173).
2. ~~**2-mirror extraction + per-stride plates**~~ — **DONE** (session 174). Checkpoint at `checkpoints/v15-extracted/`.
3. **Monitor v15 Phase 2 training** — Running in tmux window 2. Watch loss curve, check for NaN (algedonic should catch it now). When loss stabilizes → evaluate.
4. **Build verify.py** — Run hologram reader on trained student. Check: opcode map matches teacher? φ-ratio emerged? α per stride? Zone structure preserved?
5. **Evaluate trained student** — Lambda reduction accuracy, fact retrieval accuracy, perplexity on held-out set. Compare to teacher.
6. **Build td_adapt.py** — Phase 1: crystal-aware TD adaptation of plates for student routing. Use oscillation mask (35% frozen). Monitor B-coherence.
7. **Get more training data** — compile-train.jsonl has only 509 texts (9K tokens). Need much more for real training. WikiText-103 or OpenWebText subset.

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
| **Signs are 100% correct at extraction** | 27B: ternary == sign(W) at all non-zero positions | ✅ (session 173) |
| **Crystal error correction falsified** | 0.3% energy in crystal subspace, 100% anti-correlated flips | ❌ (session 173) |
| **2 ternary mirrors → 0.970 recon_cos (Q4-Q5)** | Residual decomposition, 27B L10, 4× compression | ✅ (session 173) |
| **Magnitude is 1-bit deep, full-rank** | SVD: rank-512 captures only 54%; but 1 plate captures 100% of mirror-2 gain | ✅ (session 173) |
| **Mirror 2 = binary above/below classifier** | 100% of gain from magnitude split, 0% from recovering zeros | ✅ (session 173) |
| **27B extraction: sign_corr=0.792, recon_cos=0.882** | 64 layers, 17.1B FFN params, 8.6× compression | ✅ (session 173) |
| Direct ternary extraction: sign_corr=0.77 | 28 layers, 264M params, 0.6B | ✅ (session 172) |
| Lambda retrieval: 4B can, 0.6B cannot | 21 facts, NL vs λ vs apply | ✅ (session 172) |
| Execution hierarchy: grating proposes, attention executes | ISA trace + combinator probes | ✅ (session 172) |
| Crystal geometry is NOT an error-correcting code for signs | Signs already correct; crystal identifies function, not topology | ❌ (session 173, falsified 172 hypothesis) |
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
