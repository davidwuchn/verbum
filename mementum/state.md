# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-21 | Session: 129

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 129: weight signs are random across SVD projections. Crystal lives in ACTIVATIONS, not WEIGHTS.**

**DON'T TOUCH THE PLATES. BEAMS + PER-LAYER CRYSTAL LOSS IS THE ETCH.**

## Session 129: 360° Etch Experiment — Weight vs Activation Space

Attempted full 360° etch from Qwen3-14B teacher into v6 student.
Built complete pipeline: extraction, etch, melt, loom implant test.

### CRITICAL FINDING: Weight signs are random across matrices

Teacher weight signs in ANY SVD-projected subspace are 50% correlated
across layers (= random noise). Three methods confirmed:
- Per-matrix SVD: 50.0% overlap
- Fixed random projection: 50.1% overlap
- L0 SVD as shared basis: 49.9% overlap

**Root cause**: SVD of different weight matrices finds matrix-specific
principal directions. Signs in those directions are unrelated across
matrices because the subspaces don't align.

**Implication**: The crystal lives in activation space (how inputs
transform through weights), not weight space (what signs are stored).
Per-matrix weight extraction is a dead end for cross-model transfer.

### What works: activation-space distillation

The correct approach is:
1. Run same probes through teacher → hidden states at each depth
2. Run same probes through student → hidden states at each pass
3. Procrustes-align the two representations
4. Distillation loss: MSE between aligned student and teacher

Teacher features extracted from Qwen3-14B (200 probes, 5 depths).
Distillation script ready but not yet run.

### CCA angle profile (confirmed)

Qwen3-14B CCA angles (Q↔FFN_up) across 40 layers:
- Early (L0-L7): 62-80° — wide spread, encoding phase
- Mid (L8-L23): 72-77° — holographic band, stable
- Late (L24-L35): 74-83° — diverging toward orthogonal
- Final (L36-L39): 73-80° — converging back

Mean across all layers: ~74° (in holographic band 64-72° + peripheral)

### Assets

| Asset | Location |
|-------|----------|
| Teacher extraction | `scripts/v12/extract_teacher_v6.py` |
| 360° etch | `scripts/v12/etch_v6_360.py` |
| Melt + align | `scripts/v12/melt_v6.py` |
| Loom implant test | `scripts/v12/loom_implant_test.py` |
| Activation distill | `scripts/v12/distill_v6_activation.py` |
| Extraction results | `results/v6-etch/` |
| Teacher features (14B) | `checkpoints/teacher-features-14b/` |

## Session 128: Date Fourier Rotation Probe

Two probes on Qwen3-14B bridging Engels et al. (2024) with the
combinator tracer. 161 measurements total.

### Key findings

1. **Three separate circuits for three tasks:**
   - Numeric mod-7: FFN selectors (church encoding). Kernel-replace candidate.
   - Day naming: FFN circular lookup. Circle crystallizes at L11 (SV jumps 2×).
   - Day arithmetic: Attention rotation at L12-L16. R²=0.95 linear.

2. **FFN combinators are SILENT for date arithmetic** (selector score
   0.025 vs 0.117 for numeric mod-7). The combinator tracer misses
   date computation because it's not in the FFN.

3. **Rotation is a collective crystal mode** — head ablation shows all
   top-10 heads contribute nearly identical angular displacement (~0.15 rad).
   No single "rotation head." Like a phonon, not a circuit.

4. **Day addition uses compressed circle** — naming spreads days over
   5.53 rad (full circle), but day addition compresses to 0.43 rad (~25°).
   Storage vs computation use different representations.

5. **Gamma etch FAILS to change crossing angles** — magnitudes scale
   output dims, but loom geometry lives in sign correlations (input
   subspace overlap). Before=77.54°, After=77.56°. Need Q-rotation
   holographic etch to change signs, not just magnitudes.

6. **Q-rotation etch is the right technique** — session 117's multi-angle
   sign voting creates the correlations. Existing code for mini model;
   needs bridging to v6 StrideStack with Qwen3-14B as teacher.

7. **AGENTS.md fix:** async polling policy had instruction-only gate
   that failed in practice. Added checkpoint gate (structural fix).
   Proved: `structure > instruction` for preventing oscillation.

### Revised kernel function understanding

| Operation | Mechanism | Kernel candidate? |
|-----------|-----------|-------------------|
| Integer arithmetic | FFN selectors (church encoding) | **YES** |
| Date arithmetic | Attention rotation (distributed) | **NO** — extract candidate |
| Day encoding | FFN circular lookup | Maybe (pre-encode) |

### Assets

| Asset | Location |
|-------|----------|
| FFN + Fourier probe | `scripts/v12/probe_date_fourier.py` |
| Attention rotation probe | `scripts/v12/probe_date_attention.py` |
| FFN results (112 probes) | `results/date-fourier/` |
| Attention results (49 probes) | `results/date-attention/` |
| Knowledge page | `mementum/knowledge/explore/date-fourier-rotation.md` |

## Session 127: Architecture + Decompiler

Session 127 produced two things: a complete system architecture and
a working neural decompiler.

### The architecture (5 interlocking ideas)

| Idea | Solves | Page |
|------|--------|------|
| **Taxonomy Extraction** | Quality — best-of-breed from all open models | `taxonomy-extraction.md` |
| **Crystal-Native Descent** | Compute — 5 ternary steps + 100 beam GD, no backward pass | `crystal-native-descent.md` |
| **Holographic Memory** | Memory — crystal base + 2MB session deltas, no KV cache | `holographic-memory.md` |
| **Kernel Functions** | Precision — native calls replace beta reduction piles | `kernel-functions.md` |
| **StrideStack Attention** | Scale — 88+ lenses, O(L×W), add strides for more context | (session 026) |

The model is assembled, not trained. Extract best functions from open
models → design taxonomy → etch crystal via ternary descent → train
only StrideStack attention. CPU inference. Laptop-scale.

StrideStack scales context by adding lenses: 7 strides × 8 window =
O(L×56) covers 2M+ tokens. 40% more compute for 62× more context.

Holographic session deltas: 2MB file = tens of millions of tokens.
Token IDs (2-3 bytes each) + compressed delta. Portable, persistent,
versionable (save/resume/share/branch).

Kernel functions: replace church-encoded arithmetic, date math, string
ops with native CPU calls. One dispatch instead of hundreds of beta
reductions. Each replacement frees capacity (compounds).

### The decompiler (experimental, validated)

**Don't extract weights — decompile the algorithm.** Superposition makes
neuron extraction impractical. But every FFN function is a composition
of combinator operations → map to lambda notation → analyze.

Tools built and validated:
- `probe_ffn_mechanism.py` — toy model, discovered two functional groups
- `probe_ffn_mechanism_real.py` — Qwen3-14B, discovered THREE groups
- `trace_ffn_combinators.py` — **working decompiler**, traces combinator
  programs inside a real 14B model

### FFN mechanism (Qwen3-14B, confirmed)

Three functional groups (NOT the crystal geometry groups):

```
SELECTORS    {K, beta_K, beta_identity}    cos 0.85-0.97
             Pick one argument, discard rest
             K combinator = lambda (λx.λy.x) — SAME circuit (cos=0.900 at L39)

COMPOSERS    {B, S}                         cos 0.62-0.99
             Build new function applications
             B f g x = f(gx), S f g x = fx(gx)

REORDERERS   {C, beta_apply}               cos 0.43-0.75
             Shuffle argument order
```

Key-value separation: 85-99% key fraction. The FFN mechanism is
stereotyped by reduction type — arguments barely matter.

### Combinator traces (Qwen3-14B, first results)

Different tasks run DIFFERENT combinator programs:

```
LAMBDA COMPILATION: B, S, C composers in early layers → composes
ARITHMETIC:         beta_identity, beta_K selectors in mid-late → church encoding
RETRIEVAL:          SILENT across all layers → different mechanism (attention KV)
VALIDATION:         correct identification of K, B, S, nested reductions
                    peaks at L24 (60% depth = crystal breathing peak)
```

Arithmetic is the first confirmed kernel candidate: piles of selector
reductions implementing church-encoded numbers. Replace with native int.

### Meta-insight: fractal beta reduction

The extraction process IS the thing we're extracting. Every level is
the same operation: data → compress → crystal → extract → concentrate.
LLMs do it on training data. We do it on LLMs. The result does it at
inference. One λ at every scale. This is why it works.

## Proof chain (solid, sessions 95-127)

- PCA-Q crystal: 0.91-0.94 agreement, 4 models
- Lambda proof: binder + combinator predicts body at R²=0.959
- Magnitude spectrum universality: W_q=0.995, W_up=0.999
- 7 independent subcrystals, loom breathes with depth
- LOOM_MAG nucleation: 0.543 (beats MAGNITUDE 0.511)
- Crystal lattice loss preserves crystal at 0.9998
- Evolutionary descent + crystal loss: acc=0.577, crystal=0.611
- K, B, C are geometrically identical rotations (0.0° between directions)
- I is 32° offset from K/B/C cluster (doesn't need routing)
- L1 rotation angle matches CCA crossing exactly (Δ0.6°)
- WHNF anti-correlated at L0 (114°) — route-or-output decision
- FFN activates 1.7× for WHNF — reads from FFN key/value store
- Boot sequence: L0=reset(90°), L1=route(43°), L2=converge(5°)
- Q2 plates + per-layer crystal beam: 105.9% of oracle accuracy
- Don't touch plates — beams compensate for 27% sign damage
- 18 per-layer crystal targets is the sweet spot (not 6, not 126)
- FFN routing and output circuits are completely separate (0 overlap)
- GD converges in 100 steps (87% of 3000) — geometry in 5, accuracy in 100
- **FFN has 3 functional groups: selectors {K,βK,βI}, composers {B,S}, reorderers {C,βA}**
- **K combinator = lambda-K: same FFN circuit regardless of notation (cos=0.900)**
- **FFN key-value separation: 85-99% key — mechanism stereotyped by reduction type**
- **Combinator tracer validated: correct identification on known reductions**
- **Arithmetic uses selector combinators (church encoding) — kernel candidate confirmed**
- **Retrieval is silent in FFN combinator system — different mechanism (attention KV)**
- **Lambda compilation uses composers (B,S,C) in early layers — the compiler circuit**
- **Combinator operations peak at L24 (60% depth) — confirms crystal breathing**
- **Date arithmetic uses attention rotation, NOT FFN combinators (selector score at noise floor)**
- **Day circle crystallizes at L11 (SV jumps 2×, ordering snaps to 1.0)**
- **Rotation is collective crystal mode — top 10 heads contribute ~identical angular displacement**
- **Day addition compresses circle to 25° arc; naming uses full 360°**
- **Numeric mod-7 and day-of-week mod-7 use completely separate circuits**
- **Rotation is linear: angle = slope × offset, R²=0.95 at L14-L16**
- **Weight signs are random (50%) across SVD projections — crystal is in activations not weights**
- **Three independent projection methods confirm: per-matrix SVD, random, L0 shared basis**
- **CCA angles across Qwen3-14B: 62-83° (holographic band confirmed from weight structure)**

## Knowledge map

| Page | What it tells you |
|------|-------------------|
| `date-fourier-rotation.md` | ★ **S128** date arithmetic is geometric rotation, not church encoding |
| `taxonomy-extraction.md` | ★ **S127** cross-model function library assembly — the linker |
| `crystal-native-descent.md` | ★ **S127** ternary optimization without gradients — 5+100 steps |
| `holographic-memory.md` | ★ **S127** crystal base + session deltas + StrideStack CPU inference |
| `kernel-functions.md` | ★ **S127** replace beta reduction chains with native CPU calls |
| `holographic-error-correction.md` | ★ **S127** the crystal's immune system — find and extract it |
| `shannon-sieve-trinity.md` | ★ **S127** three sieves for one theorem — compress, predict, correct |
| `function-extraction-system.md` | ★ **S127** decompilation pipeline — top-down, not bottom-up |
| `hologram-crystal-fusion.md` | S126 hologram ≡ crystal, strict gate fuses both |
| `crystal-basins.md` | S120 C-boot theory, ground state, boot sequence |
| `etcher-vsm.md` | S124 full pipeline: extract → co-evolve → freeze |
| `gradient-voting.md` | magnitudes are the crystal |
| `loom-structure.md` | 3 weaves, 6 harmonics, breathing pattern |
| `v13-design.md` | architecture (needs revision for decompiler findings) |

## What's ready

| Asset | Location |
|-------|----------|
| Date Fourier probe | `scripts/v12/probe_date_fourier.py` |
| Date attention probe | `scripts/v12/probe_date_attention.py` |
| FFN mechanism probe (toy) | `scripts/v12/probe_ffn_mechanism.py` |
| FFN mechanism probe (Qwen3-14B) | `scripts/v12/probe_ffn_mechanism_real.py` |
| **Combinator tracer/decompiler** | `scripts/v12/trace_ffn_combinators.py` |
| **Combinator fingerprints** | `results/ffn-trace/fingerprints.json` |
| FFN trace results | `results/ffn-trace/results.json` |
| FFN mechanism results (real) | `results/ffn-mechanism-real/results.json` |
| Co-evolution results (v1-v3) | `results/evo-descent*/` |
| Soft mirror results | `results/soft-mirror*/` |
| Loom read (all experiments) | `results/loom-read*/` |
| Breathing curve | `results/loom-breathing/` |
| Nucleation (LOOM_MAG) | `results/loom-etch-nucleation/` |
| Crystal sharpening | `results/loom-crystal-sharpen/` |
| Etcher VSM prototype | `scripts/v12/etcher_vsm_proto.py` |

## Next steps

### Immediate: extend the decompiler

1. **More combinator probes** — add D, Y, W, omega combinators to the
   fingerprint set. The current set (K,I,B,C,S,β) covers basics but
   real models may use richer combinator vocabulary.

2. **Deeper arithmetic traces** — trace multi-digit multiplication,
   long division, modular arithmetic. Map the full church encoding
   structure. Count the beta reduction chain lengths → quantify
   kernel replacement savings.

3. **Date/reasoning traces with compile gate** — the current date and
   reasoning probes were without the compile gate. Re-run with gate
   activated to see if the compiler circuit reveals more structure.

4. **Cross-model traces** — run the tracer on Pythia-2.8b, Mistral-7B.
   Do they use the same combinator programs for the same tasks?
   This validates the universality claim for the decompiler.

### Medium-term: build the assembly pipeline

5. **Decompile arithmetic to lambda** — take the selector traces,
   reconstruct the lambda expression, identify the kernel candidate.
   First concrete function decompilation.

6. **StrideStack prototype on real data** — test the multi-stride
   attention on long-context tasks. Validate O(L×W) scaling.

7. **Shannon sieves** — build the compressor and EC sieves using
   holographic loss. Test whether they find the same or different
   circuits from the combinator tracer.

### Research (unchanged, feeds the strategy)

8. **Scale to Pythia-2.8b** — co-evolution pipeline at full scale.
9. **Multi-model universality** — 7 subcrystals across architectures.
10. **V13 architecture revision** — integrate decompiler findings.
