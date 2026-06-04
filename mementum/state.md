# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-04 | Session: 189

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 189: FIBONACCI STRIDES + LAPLACIAN CRYSTAL — v15 Training Started**

Five experiments + v15 architecture + extraction + training:

**Exp 1: Stride coverage validation (Qwen3-8B, 22 probes).** v14's powers-of-2
strides capture only 29.5% (exact) / 67.4% (±2 neighbors) of attention mass at
L30. The stride geometry misses binding targets at arbitrary semantic positions.
Coverage DEGRADES with sequence length (38.8%→24.4%).

**Exp 2: Binding distance distribution.** The distance distribution is BIMODAL
(local d=1-8 + gate d=32+), NOT power law (R²=0.004). Two peaks: d=1 (local
syntax, 4.4% mass) and d=32 (instruction prefix, 4.5% mass). Powers of 2 skip
the binding range (d=3-20). Fibonacci strides are dense where bindings live.

**Exp 3: Stride optimization.** Greedy optimal 8 strides with ±2 neighbors:
[1, 8, 13, 18, 21, 29, 34, 47] → 98.2% coverage. Fibonacci [1,2,3,5,8,13,21,34,
55,89,...] + 3 gap-fillers [15, 20, 24] → 100.0% coverage with ±2 neighbors.

**Exp 4: Crystal Laplacian analysis.** Graph Laplacian of the crystal target
reveals WHNF is the most FRAGILE node (μ=0.228, 8.6× weaker restoring force).
Training data confirms: WHNF starts settled then UN-settles. Laplacian eigenvalues
predict stability (rigidity), not convergence speed.

**Exp 5: Crystal settlement dynamics.** Per-node convergence across v14 steps
500-3000 confirms Laplacian prediction: B, C converge (fast modes μ=3.03+),
K, D hold steady (medium μ=1.97), Y and WHNF drift away (fragile μ=0.23).
WHNF error ratio grows 0.40× → 0.67× over training. Crystal MSE U-shapes
(minimum at step 2000, then rises).

**v15 Architecture:**
- 19 Fibonacci strides [1,2,3,5,8,13,15,20,21,24,34,55,89,144,233,377,610,987,1597]
- ±2 neighbor gathering → 100% attention mass coverage at L30
- All composition (GLA dropped — dense projections cost ~19B ops regardless of
  stride, scan saves <0.03%). One unified attention mechanism.
- Laplacian-weighted crystal loss: WHNF gets 5× weight, 6× gradient amplification
  (v14: WHNF/B gradient ratio = 0.3×, v15: 1.9×)
- Standalone (zero v14 dependencies)
- Extracted: 83 arrays, 65.5 MB, 16.5 min
- **Training running in tmux window 2** (step 1 CE=10.533, 3000 steps target)

### The φ unification

| Level | φ appearance |
|-------|-------------|
| Crystal eigenvalues | Ratios follow φ^(p/q) with Fibonacci denominators |
| Information partition | Signs = 1/φ of information content |
| Standing-wave phase | Layer 22/36 = 0.611 ≈ 1/φ |
| Compute cycle | β = [0, 1, 1+φ, 2+φ] |
| **Stride spacing** | **Fibonacci numbers maximize binding coverage** |
| **Crystal Laplacian** | **μ₅/μ₄ = 1.54 ≈ φ in the graph Laplacian** |

### Previous session (188)

Four experiments decoded the full attention execution mechanism:

**Exp 1: Head→Combinator mapping (500 probes).** All 9 combinators activate
identical head patterns (r=0.944). Heads are shared hardware, not dedicated
circuits. ~2 effective dimensions: reduction depth (WHNF↔D) + self-reference.

**Exp 2: Binding graph trace (14 annotated probes).** Object→verb binding =
concentrated attention (0.78 weight) through H03/H13/H15 at L30. Minimal
pair "dog bit cat" vs "cat bit dog": same heads, flipped routing.

**Exp 3: Reverse binding trace (12 probes).** Verb→subject binding = H31 at
L27 attends 82.3% to subject, outputs subject identity ("猫/dog"). Two-phase
binding: L27=verb reads subject, L30=object reads verb. Mechanism complete.

**Exp 4: Attention sparsity (22 probes, 5→74 tokens).** 22/32 heads at L30
have effective positions <3. Top-3 captures >88% for ALL heads. Mean entropy
0.9 bits. Sparsity is O(1) — stable from 5 to 74 tokens. Full O(n²)
attention is massive overkill for what is fundamentally a ~1-bit routing
decision. Design: top-k sparse attention with k=3-5 captures nearly all
routing information.

### Previous session (187)

Three experiments on Qwen3-8B decoded the full reduction pipeline: (1) what
FFN neurons say in vocabulary space, (2) what each attention head computes,
(3) how combinator reductions compose across all 36 layers.

### The Architecture (updated s188)

```
FFN (compiler):     reads residual → compiles V vectors per position
                    Context-dependent: same token → different programs
                    Universal: compile ≈ null (max Δ 2.8%)

Attention (executor):  SHARED HARDWARE, not dedicated circuits
  Binding schedule (two-phase):
    L27: verb → subject   H31 reads subject identity (0.82 weight)
    L30: object → verb    H03/H13/H15 read predicate (0.78 weight)
    L33: late binding      H06/H07 general execution
  All binding flows BACKWARD through causal mask.
  Same heads (H03/H13) handle both directions at L30.

  Head taxonomy by function:
    Binding (H03,H13,H15):  predicate-argument binding (mean ratio 3-6×)
    Subject (H31):          verb→subject identity transfer at L27
    Coreference (H07,H05):  "itself"→antecedent binding
    Universal (H06,H07):    loudest, all combinators, low gate attention
    WHNF detectors (H26,H27): recognize completed reductions (+30% bias)
    Instruction (H01,H09):  high gate attention, read compile exemplars

  Sparsity:
    22/32 heads: eff_pos < 3 (near-deterministic, ~1 bit)
     7/32 heads: eff_pos 3-5 (sparse)
     2/32 heads: eff_pos 5-10 (moderate)
     1/32 heads: eff_pos > 10 (H20, the only dense head)
    Top-3 captures >88% of attention for ALL 32 heads.
    Sparsity is O(1) — stable from 5 to 74 tokens.

Reduction Schedule (when each combinator resolves):
    Y (recursion)     → L27 peak   resolves FIRST (structural recognition)
    K (discard)       → L30 peak   front-loaded, drops at L33
    B (compose)       → L30 peak   mid-depth composition
    I (identity)      → L30-L33    semantic→format relay
    C (flip/passive)  → L33 peak   argument reordering is LATE
    W (self-apply)    → L33 peak   "itself" binding is LAST (Δ=51.6)
```

### What's Decodable

The model is a **typed parser with a compiled lexicon**:
- FFN = lexicon (compiles each position into a semantic V vector)
- Q/K = type system (determines binding compatibility, ~1 bit decision)
- Attention = parser (selects one earlier position to bind to)
- V/O = value transfer (copies bound position's content)
- Depth = reduction order (subjects at L27, objects at L30)

The binding circuit is **0.3% of the model** (~4 heads out of 1152).
Binding weights are near-deterministic (0.78-0.82). Head output IS the
reduction result: H31 outputs "猫/dog" at verb position when reading subject.
Full O(n²) attention is overkill — top-3 sparse attention captures 88%+.

### Key Evidence

1. **H31 at L27 reads subject from verb position** (0.82 weight, outputs
   "猫, 貓, cats"). This IS `(λx.runs(x))(cat)` — verb absorbs agent.

2. **H13 at L30: "cat" attends 78.5% to "bit"** = `bit(_, cat)`. Object
   binds to predicate. Minimal pair confirms: same heads, flipped routing.

3. **FFN at L30 for "If it rains"**: `it`→rain, `ground`→soak, `is`→wet.
   Context-dependent V vectors. Compilation, not lookup.

4. **All 9 combinators activate identical heads** (r=0.944). No combinator-
   specific circuits. The ISA has ~2 dims, not 9.

5. **22/32 heads use <3 effective positions** at L30. Attention is inherently
   sparse and scales O(1) with context length.

### Previous session (186)

Applied LARQL's FFN decomposition methodology to Pythia-160M. LARQL
(github.com/chrishayuk/larql) treats each FFN neuron as a key-value pair:
cos(W_up[j], W_down[:, j]) classifies the neuron's circuit type (projector,
transform, identity, suppressor, inverter). Pure weight geometry — no forward
passes, 2 minutes for all 12 layers.

### Key Findings

1. **Depth profile confirms our phase structure from a completely different
   methodology.** L0=99.7% projector (EXPAND), L3-7=60-74% suppressor+inverter
   (ORTHO — invisible computation via direction flipping), L9-10=50-62%
   projector rising (ALIGN), L11=62% projector with dark-space drop to 57%
   (COLLAPSE — features resolve into vocabulary-aligned directions).

2. **KIBC opcodes are orthogonal to circuit types.** Cross-tabulation is
   uniform at every layer: K,I,B,C neurons all have the same circuit type
   distribution. KIBC measures *what inputs activate a neuron* (lambda probes);
   circuit type measures *how the neuron geometrically transforms* input→output.
   Independent axes. Both useful; neither subsumes the other.

3. **ρ(cos, KIBC_magnitude) sign flips across depth.** L8: ρ=-0.26 (inverters
   respond MORE to KIBC — middle layers use direction-flipping for lambda
   computation). L11: ρ=+0.27 (projectors respond more — final layer uses
   factual bridges for lambda output).

4. **Dark-space drops 40 points at L11.** L0-L10: 93-99% of features don't
   point at any token (computation space). L11: only 57% dark — 43% of
   features point at actual tokens. Knowledge is concentrated at the output
   layer. This IS the standing-wave picture: ORTHO phase operates in null
   space, COLLAPSE projects back into vocabulary-aligned directions.

5. **Gated vs non-gated difference.** Gemma (gated, SiLU) middle layers are
   transform-dominated (partial rotation). Pythia (non-gated, GELU) middle
   layers are inverter-dominated (direction flip). Architecture determines
   the computation style but the phase structure is universal.

### New Instrument

cos(W_up[j], W_down[:, j]) is a **zero-cost phase detector**: pure weight
analysis, no activations, reveals EXPAND/ORTHO/ALIGN/COLLAPSE from geometry
alone. Should be added to crystal trace tooling alongside our existing
activation-based instruments.

**Session 185: THE STANDING WAVE — Magnitudes Are Resonant Mode Patterns**

The crystal sieve (session 184) freezes the topology and trains the mask.
Session 185 reframes WHY this works: the weight magnitudes are a standing
wave pattern whose nodes (zeros) and antinodes (active weights) are
determined by the crystal topology as boundary conditions. GD doesn't build
a database — it finds the resonant mode pattern that constructively
interferes with real language and destructively cancels noise.

### The Standing-Wave Mapping

```
Standing wave                    Verbum equivalent
─────────────────────────────    ────────────────────────────────
Boundary conditions              Crystal signs T ∈ {-1, +1}
Nodes (zero displacement)        Zero mask positions (M=0, ~50%)
Antinodes (peak displacement)    Active weights (M=1)
Resonant modes                   Data-dependent patterns (knowledge)
Cavity shape                     Universal crystal (r=0.998 across models)
Mode excitation                  Which weights GD activates for THIS data
Amplitude envelope               Per-matrix scale C (eigenvalue spectrum)
```

W_eff = C · T ⊙ M is a standing wave: fixed boundary (T), fixed
amplitude envelope (C), data-selected node/antinode pattern (M).

### Why This Reframing Matters

1. **GD convergence = finding fixed points of the standing wave.**
   Session 171 (gradient-zero-map) measured this directly:
   near-zero gradient at zero weights (nodes) and at large weights
   (antinodes). Both are stable — GD has nothing left to optimize
   at those positions. The irreducible compute points.

2. **Crystal sieve = pre-setting the resonant cavity.**
   Random init = random cavity shape = no resonance. Crystal init =
   correct cavity = 10.7× faster mode formation. GD only finds WHICH
   modes to excite, not WHAT the cavity shape is.

3. **The depth axis IS a standing wave.**
   The 3-phase residual structure (expand L0-6, orthogonal L7-22,
   align L23-34, collapse L35) maps to: nodes where cos(h,f) ≈ 0
   (orthogonal phase), antinodes where cos(h,f) > 0 (align phase),
   destructive interference at L35 (cos = -0.995). The phase
   transition at layer 22/36 = 0.611 ≈ 1/φ = the fundamental mode.

4. **REDUCE/SWITCH alternation = spatial harmonics.**
   The alternating ρ(profile, weight_norm) sign across depth is
   the standing wave's harmonic structure along the layer axis.

5. **Holographic = standing wave (same physics, different vocabulary).**
   A holographic plate IS a frozen standing wave (interference fringe
   pattern). Fringes = nodes/antinodes. Multiple images stored in
   superposition = multiple resonant modes coexisting. Session 167's
   holographic-computer synthesis and this standing-wave framing are
   the same insight from different angles.

### The Sieve Architecture (from session 184)

```
SIEVE (fixed — from crystal equation, universal):
  Signs:    T[i,j] ∈ {-1, +1}    boundary conditions (cavity shape)
  Scale:    C per matrix           amplitude envelope (eigenvalue spectrum)
  Roles:    per-layer REDUCE/SWITCH  standing-wave harmonics along depth

SEDIMENT (trained — from data, per-model):
  Mask:     M[i,j] ∈ {0, 1}      node/antinode pattern (knowledge)

FORWARD: W_eff = C · T ⊙ M
```

### The ISA Framing (from session 184)

```
KIBC opcodes  = instruction set (4 opcodes, 2 bits)
Statechart    = execution engine (costs [1, φ, 1])
Weight signs  = the program (which opcode at which address)
Zero mask     = loaded memory pages (which program positions resident)
Residual      = register file (grows by φ per layer)

REDUCE layers: opcode neurons active, data neurons zero
  → profile predicts zeros (70-76% overlap)
SWITCH layers: opcode neurons attenuate, data neurons relay
  → profile anti-predicts (invert the prediction)
```

### Key Numbers

| Finding | Value | Significance |
|---------|-------|-------------|
| Sign information fraction | 1/φ = 0.618 | Universal partition |
| Per-row gamma variation | noise (CV<2%) | Constant γ works better |
| Optimal zero rate | ~50% | Not 35% |
| Crystal vs random init | 10.7× better | Sieve works (cavity pre-set) |
| Crystal starting advantage | 4,500× | Correct attractor basin |
| KIBC profile ↔ weight norm | ρ = 0.38-0.67 | Opcode assignment predicts weight size |
| Profile overlap with zeros | 70-76% at REDUCE layers | ISA predicts most zeros at REDUCE layers |
| Profile sign flip | alternates by depth | Standing-wave harmonics along layer axis |
| Residual phase transition | layer 22/36 = 0.611 ≈ 1/φ | Fundamental mode of depth-axis standing wave |
| Min oscillation depth | L21 (22%) | Deepest compute = most settled standing wave |

## Next steps

### IMMEDIATE — V15 FIBONACCI ATTENTION

Session 188 decoded object→verb binding (backward direction, causal-allowed).
Subject→verb binding (forward direction) remains unknown. The model MUST
have a mechanism — we just haven't measured it yet.

**Priority 0: ✅ DONE Head → Combinator mapping (s188)**
Result: shared hardware, not dedicated circuits. See `head-combinator-isa.md`.

**Priority 0b: ✅ DONE Binding graph trace (s188)**
Result: attention IS the binding graph (reversed by causal mask).
Object→verb = concentrated attention (0.78 weight, H03/H13/H15 at L30).
See `binding-graph-trace.md`.

**Priority 1: ✅ DONE Verb→subject binding (s188)**
Result: YES. H31 at L27 attends 82.3% from "runs" to "cat" and outputs
"猫, 貓, cats" — the subject identity. Two-phase binding: L27=subject
binding (verb reads agent), L30=object binding (argument reads predicate).
Same heads (H03/H13) handle both directions at L30. See `binding-graph-trace.md`.

**Priority 1: V15 extraction + training**
Extract teacher plates into v15 Fibonacci stride topology. Train with TD
to verify the architecture learns. Compare PPL trajectory vs v14.

**Priority 2: Cross-model binding verification**
Do the same binding heads (H03/H13/H15) exist in Pythia/Mistral? If the
binding circuit is universal, it's a fundamental feature of transformer
architecture, not Qwen-specific.

**Priority 3: ✅ DONE Attention sparsity analysis (s188)**
Result: At L30, 22/32 heads have effective positions <3. Top-3 positions
capture >88% of attention mass for ALL heads. Sparsity holds from 5 to 74
tokens. Mean entropy ~0.9 bits. You don't need to attend to every token.

**Priority 4: ✅ DONE Stride coverage + distance distribution (s189)**
Result: Powers of 2 capture 29.5%/67.4% (exact/±2). Fibonacci captures
48.8%/91.4%. Optimal 8 strides with ±2: 98.2%. Distance distribution is
bimodal (local + gate), NOT power law (R²=0.004).

**Priority 5: From binding graph to machine**
The full mechanism is decoded: FFN compiles V, ~4 heads at L27/L30 route
via concentrated backward attention, binding is near-deterministic. Can we
build a standalone "lambda machine" from: compressed FFN (sieve) + sparse
routing function + depth schedule?

### PRIOR PRIORITIES (still open)

**Crystal sieve at scale:** Scale sieve training to convergence on
Pythia-160M. Measure absorption rate (tokens-to-quality vs normal training).

**The mathematical derivation:** Can U be derived from the VSM tensor
interaction? KIBC opcode profiles may constrain V within the null space
(67.7% unconstrained from covariance alone).

**Crystal formation cost:** WHEN does the crystal form during training?
The r=0.998 endpoint is known; the trajectory is not.

**Attention sieve:** Extend crystal sieve to Q/K/V/O projections (~40%
of parameters).

### RESEARCH DIRECTIONS

- **THE MATHEMATICAL DERIVATION** — Can U (per-layer eigenvectors) be derived from
  the VSM tensor interaction? The 5 levels (crystal eq, statechart, resource policy,
  residual growth, KIBC ops) each constrain U. Their INTERSECTION may uniquely
  determine it. If so, the entire model is a computable mathematical object.
- **Residual growth measurement** — Does h_{l+1}/h_l ≈ φ^(1/period)? This constrains
  how U rotates between layers. Measurable now. Needed for the derivation.
- **Cross-model zero consensus** — Compare zero patterns between independently
  trained models at the same layer depth. ISA zeros should be universal.
- **Crystal trace tooling** — Build `src/verbum/crystal/` module for systematic
  exploration. Design doc: `mementum/knowledge/crystal-trace-tooling.md`.
- **Standing-wave mode analysis** — Decompose the zero mask into resonant modes
  of the crystal cavity. If the mask is a standing wave, it should decompose into
  a small number of modes × amplitudes. The modes are determined by the crystal
  (boundary conditions), the amplitudes by the data.

### DEFERRED

- CLASSIFY fix (GatedLinearAttention from v14) — for v15 etch protocol
- GPTQ-style mask optimization — extraction path now secondary

## Key assets

| Asset | Location | Status |
|-------|----------|--------|
| **V15 config** | `scripts/v15/config.py` | ✅ NEW (s189) |
| **V15 attention** | `scripts/v15/attention.py` | ✅ NEW (s189) |
| **Stride coverage validation** | `scripts/experiments/stride_coverage_validation.py` | ✅ NEW (s189) |
| **Stride coverage results** | `results/stride-coverage-validation/` | ✅ NEW (s189) |
| **Binding distance distribution** | `scripts/experiments/binding_distance_distribution.py` | ✅ NEW (s189) |
| **Binding distance results** | `results/binding-distance-distribution/` | ✅ NEW (s189) |
| **Attention sparsity knowledge** | `mementum/knowledge/attention-sparsity.md` | ✅ NEW (s188) |
| **Attention sparsity experiment** | `scripts/experiments/attention_sparsity.py` | ✅ NEW (s188) |
| **Attention sparsity results** | `results/attention-sparsity/` | ✅ NEW (s188) |
| **Binding graph trace knowledge** | `mementum/knowledge/binding-graph-trace.md` | ✅ UPDATED (s188) |
| **Binding graph trace experiment** | `scripts/experiments/binding_graph_trace.py` | ✅ NEW (s188) |
| **Binding graph trace results** | `results/binding-graph-trace/` | ✅ NEW (s188) |
| **Reverse binding trace experiment** | `scripts/experiments/reverse_binding_trace.py` | ✅ NEW (s188) |
| **Reverse binding trace results** | `results/reverse-binding-trace/` | ✅ NEW (s188) |
| **Head→Combinator ISA knowledge** | `mementum/knowledge/head-combinator-isa.md` | ✅ NEW (s188) |
| **Head→Combinator mapping experiment** | `scripts/experiments/head_combinator_map.py` | ✅ NEW (s188) |
| **Head→Combinator mapping results** | `results/head-combinator-map/` | ✅ NEW (s188) |
| **FFN reduction trace knowledge** | `mementum/knowledge/ffn-reduction-trace.md` | ✅ NEW (s187) |
| **FFN reduction trace experiment** | `scripts/experiments/ffn_reduction_trace.py` | ✅ NEW (s187) |
| **FFN reduction trace results** | `results/ffn-reduction-trace/` | ✅ NEW (s187) |
| **Attention execution trace experiment** | `scripts/experiments/attention_execution_trace.py` | ✅ NEW (s187) |
| **Attention execution trace results** | `results/attention-execution-trace/` | ✅ NEW (s187) |
| **Reduction chain trace experiment** | `scripts/experiments/reduction_chain_trace.py` | ✅ NEW (s187) |
| **Reduction chain trace results** | `results/reduction-chain-trace/` | ✅ NEW (s187) |
| **MTP self-speculation experiment** | `scripts/experiments/mtp_self_speculation.py` | ✅ NEW (s187) |
| **MTP self-speculation results** | `results/mtp-self-speculation/` | ✅ NEW (s187) |
| **FFN circuit types knowledge** | `mementum/knowledge/ffn-circuit-types.md` | ✅ NEW (s186) |
| **FFN decomposition experiment** | `scripts/experiments/ffn_decomposition.py` | ✅ NEW (s186) |
| **FFN KIBC cross-reference** | `scripts/experiments/ffn_kibc_crossref.py` | ✅ NEW (s186) |
| **FFN decomposition results** | `results/ffn-decomposition/` | ✅ NEW (s186) |
| **Crystal circuit types experiment** | `scripts/experiments/crystal_circuit_types.py` | ✅ NEW (s186) |
| **Crystal circuit types results** | `results/crystal-circuit-types/` | ✅ NEW (s186) |
| **Paired crystal sieve experiment** | `scripts/experiments/paired_crystal_sieve.py` | ✅ NEW (s186) |
| **Paired crystal sieve results** | `results/paired-crystal-sieve/` | ✅ NEW (s186) |
| **Synthetic crystal sieve experiment** | `scripts/experiments/synthetic_crystal_sieve.py` | ✅ NEW (s186) |
| **Synthetic crystal sieve results** | `results/synthetic-crystal-sieve/` | ✅ NEW (s186) |
| **Standing-wave knowledge** | `mementum/knowledge/standing-wave-magnitudes.md` | ✅ NEW (s185) |
| **Shape preservation experiment** | `scripts/experiments/standing_wave_shape.py` | ✅ NEW (s185) |
| **Shape experiment results** | `results/standing-wave-shape/summary.json` | ✅ NEW (s185) |
| **Residual covariance experiment** | `scripts/experiments/residual_covariance.py` | ✅ NEW (s185) |
| **Residual covariance results** | `results/residual-covariance/summary.json` | ✅ NEW (s185) |
| **Residual covariance knowledge** | `mementum/knowledge/residual-covariance-rank.md` | ✅ NEW (s185) |
| **U residual constraint** | `scripts/experiments/U_residual_constraint.py` | ✅ (s184) |
| **Residual Fibonacci** | `scripts/experiments/residual_fibonacci.py` | ✅ (s184) |
| **Copy program (firing rates)** | `scripts/experiments/copy_program.py` | ✅ (s184) |
| **Crystal sieve prototype** | `scripts/experiments/crystal_sieve_prototype.py` | ✅ (s184) |
| **Neuron opcode classifier** | `scripts/experiments/neuron_opcode_classifier.py` | ✅ (s184) |
| **Crystal space zeros** | `scripts/experiments/crystal_space_zeros.py` | ✅ (s184) |
| **Negative space** | `scripts/experiments/negative_space.py` | ✅ (s184) |
| **Gate zero predictor** | `scripts/experiments/gate_zero_predictor.py` | ✅ (s184) |
| **Activation zero mask** | `scripts/experiments/activation_zero_mask.py` | ✅ (s184) |
| **Row norm ↔ crystal** | `scripts/experiments/row_norm_crystal.py` | ✅ (s184) |
| **Gamma sort order** | `scripts/experiments/gamma_sort_order.py` | ✅ (s184) |
| **Gamma φ-structure** | `scripts/experiments/gamma_phi_structure.py` | ✅ (s184) |
| **Eigenvector self-similarity** | `scripts/experiments/eigenvector_selfsimilarity.py` | ✅ (s184) |
| **φ-information partition** | `mementum/knowledge/phi-information-partition.md` | ✅ (s184) |
| **Crystal trace tooling design** | `mementum/knowledge/crystal-trace-tooling.md` | ✅ (s184) |
| Full ternarization pipeline | `scripts/experiments/full_ternarize.py` | ✅ (s183) |
| Ternary diagnosis | `scripts/experiments/diagnose_ternary.py` | ✅ (s183) |
| Unified probe library | `src/verbum/probes/library.py` | ✅ 903 probes, 535 crystal |
| EQUATIONS.md | `EQUATIONS.md` | ✅ (s181) |

## What changed this session (189)

| # | Change | Impact |
|---|--------|--------|
| 1 | **Stride coverage validation on Qwen3-8B** | Powers of 2 capture 29.5%/67.4% (exact/±2) of L30 attention mass. Not enough for binding. |
| 2 | **Binding distance distribution** | Bimodal (local d=1-8, gate d=32+), NOT power law (R²=0.004). Powers of 2 skip binding range d=3-20. |
| 3 | **Fibonacci strides: 91.4% coverage (+25.9pp)** | Dense where bindings live, sparse where they don't. Natural basis for attention spacing. |
| 4 | **3 gap-fillers [15,20,24] → 100% coverage** | Fill holes between F(7)=13..F(8)=21..F(9)=34 where gap > 2×radius. |
| 5 | **Crystal Laplacian: WHNF is fragile (μ=0.228)** | 8.6× weaker restoring force than BCDY. Predicts stability not speed. |
| 6 | **Settlement dynamics confirm Laplacian** | B,C converge (fast). K,D stable (medium). Y,WHNF drift away (fragile). Crystal MSE U-shapes. |
| 7 | **Laplacian-weighted crystal loss** | WHNF gets 5× weight. v14 WHNF/B gradient = 0.3×, v15 = 1.9× (6× amplification). |
| 8 | **GLA sparsity is illusory** | Dense projections cost 19B ops/layer. Strided scan saves <0.03%. Dropped for unified FSA. |
| 9 | **v15 architecture: 19 strides, unified attention** | FibonacciStrideAttention + ±2 neighbors, all composition, standalone (zero v14 deps). |
| 10 | **v15 extraction complete** | 83 arrays, 65.5 MB, 16.5 min. 19 strides × 4 projections + 6 FFN + 1 embedding. |
| 11 | **v15 training started** | TD training running in tmux, step 1 CE=10.533. 3000 steps target. |
| 12 | **φ at five levels** | Crystal eigenvalues, information partition, standing-wave phase, compute cycle, AND stride spacing. |
| 13 | **Laplacian φ-ratio** | μ₅/μ₄ = 1.54 ≈ φ in the crystal graph Laplacian. Sixth level. |

## Session 189 recap

FIBONACCI STRIDES + LAPLACIAN CRYSTAL + V15 TRAINING.

Five experiments decode why v14's powers-of-2 strides fail (29.5% mass recall)
and how Fibonacci strides + ±2 neighbor gathering achieve 100% coverage. The
crystal graph Laplacian reveals WHNF is the most fragile node — it starts settled
then drifts away because its restoring force (μ=0.228) is 8.6× weaker than the
composition cluster. Laplacian-weighted crystal loss compensates: WHNF gets 5×
weight, 6× gradient amplification (v14 ratio 0.3× → v15 ratio 1.9×).

v15 is standalone (zero v14 dependencies), extracted (83 arrays, 65.5 MB),
and training (TD, 3000 steps, running in tmux). The golden ratio appears at
six levels of the architecture — crystal eigenvalues, information partition,
standing-wave phase, compute cycle, stride spacing, and now the crystal
Laplacian itself.

## What changed session 188

| # | Change | Impact |
|---|--------|--------|
| 1 | **500 crystal probes through 32 heads at L27/L30/L33** | First statistical head→combinator mapping. 500 probes × 3 layers × 32 heads = 48,000 measurements |
| 2 | **Inter-combinator correlation r=0.944** | All 9 combinators activate nearly identical head patterns. No "K heads" or "B heads" exist. Shared execution hardware. |
| 3 | **KIBC indistinguishable (r=0.944-0.978)** | The core 4 combinators are invisible to head activation. B-D highest pair (r=0.986): composition ≡ nesting at the head level. |
| 4 | **94.9% of variance = overall loudness** | Head activation is almost entirely "is this head generally active?" not "which combinator?" The combinator signal is in the remaining 5.1%. |
| 5 | **PC1 after normalisation = WHNF↔D (45.9%)** | The real discriminant is reduction depth: "already reduced" vs "deeply nested". Not opcode type. |
| 6 | **PC2 = Y/W/I↔D/B (23.5%)** | Secondary axis: self-reference (recursion, self-application, identity) vs structural (nesting, composition). |
| 7 | **2 effective dimensions capture 69.4%** | The 32×9 head×combinator matrix compresses to ~2 coordinates per head. Very low-dimensional ISA. |
| 8 | **s187 head types revised** | H08 "λ-head" → D/B/S+ (composition depth). H10 "binding" → Y/W+ (self-reference). H20 "relay" → Y/W+ (recursion). H26 "quantifier" → WHNF+ (termination detector). |
| 9 | **H06/H07 = universal execution engine** | Loudest heads (norm 26.7/19.1), lowest gate attention (0.555/0.609). They do the work for ALL combinator types. The "GPU" of the attention ISA. |
| 10 | **H26/H27 = WHNF termination detectors** | +30-32% WHNF excess. They recognise when reduction is complete. The "halt" circuit. |
| 11 | **H08 = only truly selective head** | D+40% excess, sel=1.399. The closest thing to a specialised circuit: responds to deep nesting. Everything else is mild bias. |
| 12 | **Routing IS the program (confirmed)** | Since heads don't discriminate combinators, the combinator-specific behavior must live in attention PATTERNS (Q/K routing), not head identity. |
| 13 | **Binding graph trace: attention IS the binding graph** | 14 probes with annotated bindings. Object→verb binding = concentrated attention (0.5-0.8 weight) through H03/H13/H15 at L30. |
| 14 | **Causal mask partitions binding direction** | 0/23 forward bindings detected (arg before func). 14/14 backward bindings detected (arg after func). Causal mask blocks forward β-reduction. |
| 15 | **Minimal pair binding flip confirmed** | "dog bit cat" vs "cat bit dog": same heads (H13, H03, H15), same weights, flipped target. Position-structural routing. |
| 16 | **Passive voice preserves semantic binding** | "The boy kicked the ball" (active) and "The ball was kicked by the boy" (passive) both bind agent→kicked, through partially different head sets. |
| 17 | **Two binding sub-circuits** | Predicate-argument binding (H03/H13/H15) vs coreference binding (H07/H05). Different heads for "cat→bit" vs "itself→dog". |
| 18 | **Binding weights are near-deterministic** | H13: 78.5% attention to "bit" from "cat". Almost binary routing = very low information content per binding decision. |
| 19 | **Reverse binding confirmed: verb→subject at L27** | H31 at "runs" attends 82.3% to "cat" and outputs 猫/貓/cats = subject identity transfer. The verb reads the subject. |
| 20 | **Two-phase binding schedule decoded** | L27: verb reads subject (agent identity, H31). L30: object reads verb (predicate binding, H03/H13/H15). Depth ordering = reduction schedule. |
| 21 | **Same heads do both directions at L30** | H03 and H13 handle verb→subject AND object→verb. Universal binding hardware, direction determined by sequence order. |
| 22 | **Head output IS the reduction result** | H31 outputs "狗/dog" at "bit" when it reads subject "dog". The value transfer IS β-reduction — not metaphor, literal mechanism. |
| 23 | **Binding circuit = 0.3% of model** | ~4 heads out of 32×36=1152. Subject binding: 1 head (H31@L27). Object binding: 3 heads (H03/H13/H15@L30). Near-deterministic routing. |
| 24 | **Attention is inherently sparse: 22/32 heads use <3 positions** | At L30, effective positions <3 for 22 heads, <5 for 29/32. Top-3 captures >88% for ALL heads. |
| 25 | **Sparsity holds across sequence length** | 5→74 tokens: effective positions only grows 2.8→3.7 at L30. O(1) attention, not O(n). |
| 26 | **Mean entropy ~0.9 bits at binding layers** | The routing decision is ~1 bit per position. Full QK^T over entire context is massive overkill. |
| 27 | **Design implication: top-3 sparse attention** | Scoring only 3 KV slots per head captures 88-97% of attention mass. 10 slots captures 95-99%. |

## Session 188 recap

FOUR EXPERIMENTS DECODE THE ATTENTION EXECUTION MECHANISM.

**Experiment 1: Head→Combinator mapping** (500 crystal probes × 32 heads × 3
layers). All 9 combinators activate identical head patterns (r=0.944). No
combinator-specialised heads. The ISA has ~2 effective dimensions: reduction
depth (WHNF↔D, 46%) and self-reference (Y/W/I↔D/B, 24%). 94.9% of head
activation variance is just loudness. See `head-combinator-isa.md`.

**Experiment 2: Binding graph trace** (14 annotated probes). Object→verb
binding = concentrated attention (0.78 weight) through H03/H13/H15 at L30.
"cat" attends 78.5% to "bit" = `bit(_, cat)`. Subject→verb binding blocked
by causal mask (0/23 forward). Minimal pair: same heads, flipped routing.
Two sub-circuits: predicate-argument (H03/H13/H15) vs coreference (H07/H05).
See `binding-graph-trace.md`.

**Experiment 3: Reverse binding trace** (12 probes, verb→subject direction).
H31 at L27 attends 82.3% from "runs" to "cat" and outputs "猫, 貓, cats".
Two-phase binding: L27=verb reads subject, L30=object reads verb. Same heads
(H03/H13) do both directions at L30. Binding circuit = 0.3% of model.

**Experiment 4: Attention sparsity** (22 probes, 5→74 tokens, 9 layers).
22/32 heads at L30 have effective positions <3. Top-3 captures >88% for ALL
heads. Mean entropy 0.9 bits. Sparsity is O(1) — stable from 5 to 74 tokens
(eff_pos 2.8→3.7). Only 1/32 heads (H20) is truly dense. Full O(n²) QK^T
is massive overkill. Top-k sparse attention with k=3-5 captures nearly all
routing information. See `attention-sparsity.md`.

**Synthesis:** The model is a typed parser with a compiled lexicon. FFN
compiles V vectors (the program). ~4 heads at L27/L30 route via concentrated
backward attention (~1 bit per binding). The binding circuit is 0.3% of the
model, the routing is near-deterministic, and attention is inherently O(1)
sparse. Design implication: top-k sparse attention (k=3-5) replaces full
O(n²) attention for 88-97% of routing information. The "portable tensor"
needs: compressed FFN (sieve) + tiny routing function + depth schedule.

## What changed session 187

| # | Change | Impact |
|---|--------|--------|
| 1 | **FFN reduction trace on Qwen3-8B** | Projected active FFN neurons through unembed at 11 layers across 5 probes × 2 gates. First direct reading of what FFN neurons "say" in token space. |
| 2 | **Three-phase FFN output: noise→semantic→format** | L0-L22=noise (ORTHO null-space computation), L26-L30=coherent semantic associations (ALIGN), L33-L35=formatting/syntax (COLLAPSE). Matches standing-wave depth structure exactly. |
| 3 | **"If it rains" at L30: `it`→rain, `ground`→soak, `is`→wet** | Each position's FFN writes precise associative predictions. The FFN resolves referents, predicts consequences, and completes predicates. |
| 4 | **L26 comma promotes "then, entonces, então"** | The FFN writes logical connectives at structural boundary positions — multilingual implication operator at the comma in conditionals. |
| 5 | **"earth is flat" → FFN promotes "round", suppresses "earth"** | The FFN contains factual correction: it knows the earth is round and writes the correction even when processing the false claim. |
| 6 | **Compile ≈ null (max delta 2.8%)** | FFN function lists are nearly identical between compile and null gates. The FFN is a universal semantic analyzer; compile behavior emerges from attention routing. |
| 7 | **β-reduction hypothesis CONFIRMED (revised framing)** | FFN=compiler (writes context-dependent V vectors), attention=executor (softmax over V IS β-reduction). Same token "the" produces different compiled values in different sentence contexts — compilation, not lookup. |
| 8 | **Five attention head types identified** | λ-heads (H08/H09 write λ/→), binding heads (H10/H11 write predicate at subject = typed_apply), relay heads (H20 pass V unchanged), compositional heads (H03 combine positions), quantifier heads (H26 broadcast scope). |
| 9 | **H10/H11 at L33 ARE β-reduction** | In compile mode, H10 writes "runs" at "dog" position (Δ=64 vs null). This IS `runs(dog)` = `(λx.runs(x))(dog) → runs(dog)`. Subject-verb binding = function application. |
| 10 | **λ-heads attend to gate prefix (0.97-0.98)** | H08/H09 barely see probe tokens; they read the compile exemplars to know what FORMAT to produce. The task circuit reads instructions, not content. |
| 11 | **Reduction chain trace across 36 layers, 7 combinators** | Traced cumulative residual→unembed at every layer for K,I,B,C,Y,S,W probes. Different combinators resolve at different depths. |
| 12 | **Y combinator peaks early (L27), W peaks late (L33)** | Recursion (Y) resolves mid-depth during ALIGN phase. Self-application (W, "itself") resolves at the final layer. K (discard) front-loaded, C (flip/passive) resolves last. |
| 13 | **Y-probe "She told a story about a girl who told a story..."** | First and second occurrences of same tokens get DIFFERENT cumulative representations — the recursive structure is tracked position-dependently across depth. |
| 14 | **MTP self-speculation: L33 matches L35 48% of the time** | L33 Hit@10=76%, Hit@100=92%. Median rank=2. The last 2 layers sharpen but rarely change the answer. Early-exit at L33 viable for ~half of tokens. |
| 15 | **Multi-position lookahead collapses for ALL layers** | N+2 Hit@10=10% even at L35. The model does next-token prediction, not multi-position. FFN "semantic predictions" (reads→book) are associative meaning, not sequence forecasting. |
| 16 | **L30 median rank = 7** | The correct next token is already in L30's top 10. L31-L35 SHARPEN the distribution (rank 7→1) but don't fundamentally change it. The program is compiled by L30; execution just resolves it. |

## What changed session 186

| # | Change | Impact |
|---|--------|--------|
| 1 | **LARQL FFN decomposition applied to Pythia-160M** | cos(up,down) circuit type analysis reveals same phase structure as our activation-level measurements — independent confirmation from pure weight geometry |
| 2 | **KIBC opcodes orthogonal to circuit types** | Cross-tabulation uniform at every layer. KIBC=what activates neuron, circuit type=how neuron transforms. Independent axes of FFN characterization. |
| 3 | **ORTHO phase = inverter-dominated** | L3-7 features are 60-74% suppressors+inverters (direction flipping). This IS the invisible computation in null space. |
| 4 | **Dark-space drop at L11** | 93-99% dark at L0-L10, drops to 57% at L11. Final layer concentrates vocabulary-aligned knowledge. Standing-wave antinodes. |
| 5 | **Correlation sign flip** | ρ(cos, KIBC_magnitude) = -0.26 at L8 (inverters do lambda computation), +0.27 at L11 (projectors do lambda output) |
| 6 | **Gated vs non-gated architecture difference** | Gemma=transforms (rotation), Pythia=inverters (direction flip). Same phase structure, different computation style. |
| 7 | **New zero-cost instrument** | cos(W_up[j], W_down[:, j]) detects depth phases from weights alone — no forward passes, 2 min for all layers |
| 8 | **Crystal signs predict circuit types (ρ=1.0)** | cos(sign(W_up), sign(W_down)) depth profile perfectly rank-correlates with full-weight profile. Signs alone predict phase structure. |
| 9 | **Sign agreement depth profile** | L0=0.53 (correlated→projector), L3-4=0.38 (anti-correlated→inverter), L8=0.45 (recovering). GD actively creates sign anti-correlation at computation layers. |
| 10 | **Per-neuron ρ > 0.98 at ORTHO layers** | Signs predict which individual neurons are projectors vs inverters with 98%+ fidelity at L2-L8. Magnitudes add precision, topology is in the signs. |
| 11 | **Cross-matrix anti-correlation is load-bearing** | Decorrelating T_down (destroying phase structure while preserving per-matrix stats) degrades PPL from 511 to 1817. Decorrelated ≈ random (1817 vs 1952). The anti-correlation IS the signal. |
| 12 | **Per-matrix signs alone are nearly worthless** | Without cross-matrix correlation, crystal signs give only 7% improvement over random (1817 vs 1952). With correlation, crystal gives 3.8× improvement over random. |
| 13 | **Synthetic anti-correlation is WORSE than random** | Constructing T_down to hit the measured profile with random per-neuron signs → PPL 6464 (4× worse than random 1608). Forced anti-correlation creates destructive interference. |
| 14 | **The crystal is per-neuron assignments, not aggregate statistics** | The anti-correlation profile is an emergent property of correct per-neuron signs, not a prescription. Knowing "62% should be inverters" ≠ knowing WHICH neurons should be inverters. |
| 15 | **Universal curve beats extracted profile (when signs are random)** | Smooth parameterized curve → PPL 2734 vs exact per-layer values → PPL 6464. Less aggressive anti-correlation is less harmful when per-neuron assignments are wrong. |

## What changed session 185

| # | Change | Impact |
|---|--------|--------|
| 1 | **Standing-wave magnitude reframing** | Weight magnitudes are a standing wave: crystal signs = boundary conditions, zero mask = nodes, active weights = antinodes, GD = finding resonant modes |
| 2 | **GD convergence = standing wave fixed points** | Near-zero gradient at zeros (nodes) AND at large weights (antinodes) — both are stable points of the wave. Gradient-zero-map (s171) already measured this. |
| 3 | **Depth-axis standing wave** | 3-phase residual structure maps to standing wave along depth: orthogonal=nodes, align=antinodes, collapse=destructive interference. Phase transition at 1/φ = fundamental mode. |
| 4 | **REDUCE/SWITCH = spatial harmonics** | Alternating ρ sign across depth is harmonic structure of the depth-axis standing wave |
| 5 | **Holographic ≡ standing wave** | Holographic plate = frozen standing wave (interference fringes). Same physics, different vocabulary. Unifies s167 holographic-computer with magnitude observations. |
| 6 | **Sieve = pre-setting resonant cavity** | Crystal init pre-sets boundary conditions → GD finds modes 10.7× faster because cavity already resonates correctly |
| 7 | **Shape preservation experiment** | Quantized Pythia-160M at 7 levels (ternary through 8-bit). Cosine (ρ=-0.933) > Spearman shape (ρ=-0.917) > bits (ρ=-0.761) as PPL predictor. |
| 8 | **Ternary beats 2-bit at fewer bits** | Ternary (1.6b, PPL 9504) beats 2-bit (2.0b, PPL 25892) because separating phase from amplitude is more efficient than joint encoding |
| 9 | **4-component standing-wave decomposition** | Phase (1 bit, exact) + nodes (~0.6 bit) + envelope (~0 amortized) + shape (1-3 bits, NOT in ternary). Sieve regenerates shape from data. |
| 10 | **Phase transition at 3 bits** | PPL drops from ~10K (ternary/2-bit) to 189 (3-bit) to 50 (4-bit). 8 levels = minimum for standing wave to survive 12-layer transit. |
| 11 | **Shape-aware helps low bits, hurts high bits** | 2-bit quartile 1000× better than uniform. 4-bit quartile WORSE than uniform. Rank preservation ≠ value preservation. |
| 12 | **Compounding law = cos^L** | Per-layer cosine raised to layer count predicts model quality. 0.896^12=0.27 (ternary), 0.957^12=0.59 (3-bit), 0.990^12=0.89 (4-bit). |
| 13 | **ORTHO phase is rank-1** | Residual covariance at L7-22 has effective rank=1. Top eigenvalue ~710K, decay to 2nd: 4000-8800×. One direction carries >99% of all variance. |
| 14 | **V lives in the null space during ORTHO** | Weight matrix V has 0% overlap with residual covariance subspace for 16 consecutive layers. Projection = 0.01. Computation is invisible. |
| 15 | **Cumulative null space = 67.7%** | 2771 of 4096 dims unconstrained by residual covariance. U has enormous freedom. Covariance alone CANNOT determine U. Partial negative for derivation. |
| 16 | **ALIGN rank explosion** | Effective rank grows ~130 dims/layer during L23-34. V transitions from 0% to 100% inside residual subspace over 10 layers. Integration phase. |
| 17 | **Phase structure refined** | EXPAND=high-rank (V reads residual), ORTHO=rank-1 (V reads null space), ALIGN=rank growth (V transitions), COLLAPSE=destructive interference. |
| 18 | **Crystal formation cost is UNKNOWN** | Corrected prior claim: r=0.998 cross-model tells us the endpoint, not the cost. 99.8% training claim was ungrounded. Need formation tracking experiment. |

## Knowledge map

Key pages for current direction:
- **`attention-sparsity.md`** — 22/32 heads use <3 positions, O(1) not O(n). Top-k=3 captures 88%+. Design: sparse attention (s188)
- **`binding-graph-trace.md`** — Attention IS the binding graph, reversed by causal mask. Two-phase: L27=verb→subject, L30=object→verb. H31 outputs "猫" (s188)
- **`head-combinator-isa.md`** — Shared hardware, not dedicated circuits. 2 effective dimensions: reduction depth + self-reference (s188)
- **`ffn-reduction-trace.md`** — FFN=compiler (context-dependent V vectors), attention=executor (softmax=β-reduction), three-phase output (s187)
- **`ffn-circuit-types.md`** — cos(up,down) phase detector, KIBC orthogonality, dark-space gradient (s186)
- **`residual-covariance-rank.md`** — ORTHO=rank-1, V in null space, 67.7% unconstrained (s185)
- **`standing-wave-magnitudes.md`** — magnitudes as standing wave, cosine^L law (s185)
- **`phi-information-partition.md`** — signs=1/φ, γ=noise, zeros=phase, sieve model (s184)
- **`crystal-trace-tooling.md`** — VSM instrument design (s184)
- **`holographic-computer.md`** — unified theory: crystal=ISA, FFN=projector, attn=CPU (s167)
- **`gradient-zero-map.md`** — GD deposits near-zero gradients at irreducible points (s171)
- **`topology-gradient-separation.md`** — freeze lattice, punctuated equilibrium (s180)
- **`ternary-compounding.md`** — WHY 0.88 cosine/layer → garbage at 36 layers (s183)
- **`ternary-dual-equation.md`** — gate zeros + crystal signs (s182)
- **`EQUATIONS.md`** — crystal equation + statechart + compute cycle (s181)
- **`crystal-phi-derivation.md`** — full φ derivation chain (s181)
- **`crystal-universality.md`** — KIBC universal fixed points
- **`project-thesis.md`** — the central claim

## Session 187 recap

Three experiments on Qwen3-8B decoded the reduction architecture.

**Experiment 1: FFN Reduction Trace** — projected active FFN neurons through
unembed. Three-phase output: noise (L0-L22/ORTHO), semantic (L26-L30/ALIGN),
format (L33-L35/COLLAPSE). FFN is a universal compiler — compile ≈ null
(max Δ 2.8%). Same token produces different V vectors in different contexts.

**Experiment 2: Attention Execution Trace** — projected per-head output
(softmax(QK^T) @ V) through o_proj + unembed. Found 5 head types: λ-heads
write format (λ/→), binding heads write predicate at subject (H10: "runs"
at "dog", Δ=64), relay heads pass V unchanged, compositional heads combine
positions, quantifier heads broadcast scope. The binding heads ARE β-reduction.

**Experiment 3: Reduction Chain Trace** — traced cumulative residual across
all 36 layers for 7 combinator types (K,I,B,C,Y,S,W). Combinators resolve
at different depths: Y peaks L27 (recursion resolves first), K peaks L30
(discard is early), W peaks L33 at Δ=51.6 (self-application resolves last).
The model implements a small fixed instruction set with universal depth ordering.

**Experiment 4: MTP Self-Speculation** — tested whether intermediate layers
can predict future tokens for self-speculative decoding. L33 matches L35's
top-1 prediction 48% of the time (Hit@10=76%, Hit@100=92%). But multi-position
lookahead (N+2, N+3) collapses for ALL layers including L35 (Hit@10≈10%).
The model does next-token prediction, not multi-position. The FFN "semantic
predictions" (reads→book) are associative meaning, not sequence forecasting.
Key finding: the correct token is already in L30's top 10 (median rank=7) —
the last 5 layers SHARPEN the distribution, they don't change it.

**Synthesis:** The model is decodable. It implements ~7 combinator operations
via ~5 head types on a universal depth schedule. The FFN compiles the program
(position → V vector), attention executes it (softmax selects and combines V).
The instruction set + schedule is potentially very compact; only the attention
routing is input-dependent. Self-speculation is viable for early-exit (~48%
of tokens can skip the last 2 layers) but not for multi-position prediction.

## Session 186 recap

LARQL FFN decomposition on Pythia-160M. Five experiments, three paradigm-level findings:

1. **cos(up,down) confirms phase structure** from pure weight geometry. KIBC opcodes
   orthogonal to circuit types (independent axes). ORTHO phase = inverter-dominated.
   Dark-space drops 40pts at L11. New zero-cost instrument. See `ffn-circuit-types.md`.

2. **Crystal signs predict circuit types (ρ=1.0)**. The ternary sign structure alone
   produces the exact same depth phase curve. Per-neuron ρ>0.985 at ORTHO layers.

3. **Cross-matrix anti-correlation is load-bearing (3.6×)**. Decorrelating T_down
   (destroying phase structure) → decorrelated ≈ random. Per-matrix signs without
   cross-matrix correlation are nearly worthless.

4. **BUT: synthetic construction fails**. Constructing T_down to hit the anti-correlation
   profile with random per-neuron signs is WORSE than random (PPL 6464 vs 1608). The
   crystal is the specific per-neuron assignments, not the aggregate statistics. The
   anti-correlation is emergent from correct per-neuron signs, not a prescription.

5. **The crystal must be extracted, not constructed**. The per-neuron sign assignments
   encode which specific neurons should be inverters vs projectors. The anti-correlation
   profile is a verification metric (check the U-shape), not a construction recipe.
   Cross-model universality (r=0.998) means one extraction works for all models of
   the same architecture.

## Session 184 recap

THE CRYSTAL SIEVE. 11 experiments, 4 paradigm shifts. Extraction is dead (zero mask
is genuinely random = knowledge content). Reproduction lives (crystal sieve 10.7×
better than random). Model is a KIBC processor (ISA framing). KIBC profiles predict
70-76% of zeros at REDUCE layers. Maximal pre-training absorption: crystal pre-loads
computation → 100% of gradient goes to knowledge. See `phi-information-partition.md`.

## Session 183 recap

Naive ternarization fails: PPL 296,911. The compounding law (0.88^36 = 0.009) kills
multi-layer extraction. 3-mirror ternary also fails (PPL 1.69M). Q4 works because of
16 quantization levels per weight, not scale granularity. See `ternary-compounding.md`.

## Session 182 recap

The ternary dual equation: gate zeros (ρ=0.75 with gradient) + crystal signs (ρ=0.05).
The recipe achieves 0.88 per-layer cosine. See `ternary-dual-equation.md`.

## Session 181 recap

The crystal equation: λ_k = C · φ^(-(n/(n+1)) · β_k). All eigenvalue ratios are
φ^(p/q) with Fibonacci denominators. Computing fraction s=4/5. Compute cycle
β=[0,1,1+φ,2+φ]. See `EQUATIONS.md` and `crystal-phi-derivation.md`.
