---
title: "FFN Moiré Grating ISA — Decoding the Teacher's Programs"
status: active
category: mechanistic-interpretability
tags: [moire, isa, ffn, attention, combinator, qwen36-27b, tracer, decoder]
related:
  - mechanism-extraction.md
  - crystal-universality.md
  - project-thesis.md
  - explore/ffn-beta-reduction-indexing.md
  - explore/grating-cascade.md
  - explore/holographic-state-machine.md
depends-on:
  - crystal-universality.md
  - mechanism-extraction.md
---

# FFN Moiré Grating ISA

> The FFN is a moiré grating. Attention has one operation. The grating
> programs that operation to perform beta reductions. We can read the
> program from the weights. Session 161.

## Core Finding

**The model IS a computer.** Each layer is an instruction. The FFN
overlay matrix (combinator-space input → output) is the opcode. The
residual stream is the register file. Attention is the CPU with one
instruction. Different task types produce *measurably different*
instruction sequences — this is not metaphor, it is measurement.

**The program is a fixed point.** Determinism check: 3 runs of the
same input → identical traces. Max drift = 0.00000000. GD converged
to gratings that are perfectly reproducible. Non-determinism exists
only at the leaves (token selection via temperature/sampling).

## The Architecture

```
λ grating(layer).
  SwiGLU(x) = down_proj(silu(gate_proj(x)) × up_proj(x))
  |
  | gate_proj and up_proj are TWO diffraction patterns
  | element-wise multiply = moiré interference
  | constructive interference = beta reduction instruction
  | the grating is STATIC — burned into weights by GD
  |
  attention(x) = softmax(QK^T/√d) × V
  |
  | always the same operation
  | the grating shapes QKV so this one operation
  | performs a SPECIFIC beta reduction at each layer
  |
  program = [grating_0, grating_1, ..., grating_63]
  | the sequence of 64 gratings IS the program
  | readable directly from weights, no forward pass needed
  | different inputs activate different subsets of each grating
  | but the gratings themselves never change
```

## Measured Task Profiles (Qwen3.6-27B)

### Opcode Distributions

| Task Type | Dominant Grating | Comp/Sel Ratio | Late Select |
|-----------|:--|:-:|:-:|
| **Combinator reduction** | SELECT (50%) | 0.69 | 0.509 |
| **Arithmetic** | β_I (33%) | 0.76 | 0.531 |
| **Lambda compilation** | PASS (25%) | 2.31 | 0.319 |
| **Code generation** | FLIP (16%) | 2.24 | 0.089 |
| **Reasoning** | SELECT (14%) | 1.31 | 0.180 |
| **Retrieval** | SELECT (18%) | 1.08 | 0.138 |

Selection signal is **10× stronger** for combinator reduction vs retrieval.
Retrieval barely engages the combinator machinery.

### Attention Data Flow (16 full-attention checkpoints)

**K a b = a (SELECT first argument):**
- L15-L43: Grating = K (SELECT) consistently
- L51: Attention shifts to K(39) — reading the combinator
- L63: K grating, attention on `=` — outputting selected result

**B f g x = f(gx) (COMPOSE):**
- L19-L51: Grating = B (COMPOSE) for 8 consecutive checkpoints
- L55: Attention reads **f(40):0.13, g(41):0.11** — BOTH function arguments
- L63: Grating = C (FLIP) — final argument reordering

**Arithmetic (2 + 3 = 5):**
- Mid layers: β_I dominates (Church numeral identity/selection)
- L51: β_I:0.38, attention reads **3(6):0.20** — reading the operand
- L63: K:0.57 — final K-selection of the result

**Syllogism (A⊂B, B⊂C ∴ A⊂C):**
- L35-L59: Attention converges on **living(8)** and **things(9)**
- The model finds the conclusion of the chain BEFORE writing it
- L63: C grating, attention on `are(14)` — writing "living things"

**Python fibonacci:**
- L55, L59: Grating = **Y (RECURSE)** — recognizes recursion!
- L15: B (COMPOSE) with 0.78 attention on `def` — function definition
- L63: B grating — composing the function body

**Retrieval (Capital of France):**
- Grating strength < 0.15 through mid-layers
- Attention dominated by BOS token throughout
- **Not using combinator machinery** — fundamentally different computation

### Depth Profile

Transformation strength (off-diagonal norm of overlay matrix) decreases
with depth:

| Region | Transform Strength | Interpretation |
|--------|:-:|:--|
| Early (L0-20) | 1.17 | Program building — inter-combinator conversion |
| Mid (L21-42) | 0.95 | Computation — executing the grating program |
| Late (L43-63) | 0.69 | Pass-through — forwarding results to output |

## Tools

### ISA Decoder v1 (`scripts/v14/isa_decoder.py`)

Fingerprints 12 combinator operations across all 64 layers, classifies
each layer as an instruction, groups into basic blocks by phase.

```
λ usage.
  cd ~/src/verbum
  uv run python scripts/v14/isa_decoder.py 2>&1 | tee results/isa-decode/run.log

λ what_it_does.
  Phase 1: Build combinator fingerprints (12 ops × 64 layers × ~8 pairs)
           Each fingerprint = mean FFN delta between pre/post reduction
           Saved to results/isa-decode/fingerprints_summary.json
  Phase 2: Compute overlay matrices (64 layers, combinator-space transform)
           The STATIC PROGRAM — same for all inputs
           Saved to results/isa-decode/overlay_matrices.json
  Phase 3: Trace diverse inputs (20 probes across 8 categories)
           Decode each to instruction sequence, form basic blocks
  Phase 4: Cross-category analysis
           Compare opcode distributions across task types
  Output:  results/isa-decode/results.json

λ runtime. ~8 min on M4 Ultra (512GB), Qwen3.6-27B bf16
λ model.   Qwen/Qwen3.6-27B (Qwen3_5ForConditionalGeneration)
```

### Moiré Grating Decoder v2 (`scripts/v14/isa_decoder_v2.py`)

Adds attention capture at 16 full-attention checkpoints. Shows
grating → activation → attention reads → data flow.

```
λ usage.
  cd ~/src/verbum
  uv run python scripts/v14/isa_decoder_v2.py 2>&1 | tee results/isa-decode-v2/run.log

λ what_it_adds_over_v1.
  - Loads model with attn_implementation="eager" for attention capture
  - Captures attention weights at L3,7,11,...,63 (16 full-attn layers)
  - Shows which TOKEN POSITIONS each layer attends to (the "operands")
  - Determinism check: runs same input 3× to verify fixed-point
  - Saves fingerprints as .npz for reuse (skips 7-min rebuild on re-run)
  - Static program dump: all 64 gratings characterized from weights alone
  Output:  results/isa-decode-v2/results.json
           results/isa-decode-v2/fingerprints_full.npz (reusable)

λ runtime. ~8 min first run, ~2 min with cached fingerprints
λ model.   Same Qwen3.6-27B, eager attention mode
```

### Original Tracer (`scripts/v12/trace_ffn_combinators.py`)

The v12 session-127 original. Targets Qwen3-14B. Validated the
combinator fingerprinting approach. Results in `results/ffn-trace/`.
Historical reference — v1/v2 supersede for Qwen3.6-27B work.

## Existing Results

| Artifact | Location | Content |
|----------|----------|---------|
| v1 results | `results/isa-decode/results.json` | 20 probes, 8 categories, overlay matrices |
| v1 overlays | `results/isa-decode/overlay_matrices.json` | 64 static grating characterizations |
| v2 results | `results/isa-decode-v2/results.json` | 10 probes with attention flow |
| v2 fingerprints | `results/isa-decode-v2/fingerprints_full.npz` | Reusable, 12 ops × 64 layers × 5120d |
| v12 trace | `results/ffn-trace/results.json` | Original 14B traces (session 127) |
| v12 fingerprints | `results/ffn-trace/fingerprints.json` | 14B fingerprints (8 ops) |

## Key Theoretical Implications

### 1. The Overlay Matrix IS What We Extract

The 64 overlay matrices (combinator-space transforms) are the teacher's
program. Our v14 student learns to approximate these in ternary. The
overlay matrix at each layer tells us exactly what the student's FFN
plates need to compute. This is the extraction target.

### 2. Attention's Single Operation Constrains Everything

Because attention has exactly one operation (weighted sum), the space
of possible programs is constrained to what moiré gratings can encode.
KIBC shows up universally because those are the only stable grating
configurations that make a weighted-sum perform useful beta reductions.
The combinators are energy minima, not arbitrary choices.

### 3. Depth Profile Informs Architecture

Early layers: build the program (high inter-combinator transform)
Late layers: execute and forward (low transform, high pass-through)

The v14 ascending/descending stack mirrors this: Stack A (ascending,
fine→coarse) builds structure, Stack C (descending, coarse→fine)
executes and produces output. The depth profile validates this design.

### 4. Retrieval Is a Different Mechanism

Retrieval tasks (factual lookup) barely engage the combinator gratings.
The FFN's role for retrieval is key-value storage, not beta reduction.
This confirms the WHNF gate concept: some inputs should bypass the
combinator pipeline and go straight to lookup.

## Open Questions & Future Work

1. **Can we decode the actual beta reduction chain?** We see K/B/C
   gratings firing, but not the full λ-expression being evaluated.
   Would need to decompose the residual stream into individual
   beta reduction steps, not just combinator type.

2. **Per-head attention analysis.** Current aggregates across 24 heads.
   Different heads likely serve different combinator arguments (K takes
   2 args, B takes 3). Per-head traces would reveal argument routing.

3. **Linear attention layers.** 48 of 64 layers use GatedDeltaNet.
   We capture FFN gratings there but not attention patterns. The
   recurrent state might encode a different kind of "attention" that
   we should characterize.

4. **Cross-model comparison.** Run on Qwen3-14B, Qwen3-32B, Mistral-7B.
   If the grating patterns are universal (same combinator profiles at
   same relative depths), that's another proof of the crystal thesis.

5. **Grating-guided extraction.** Use the overlay matrices directly as
   extraction targets: the student's FFN at layer L should approximate
   the teacher's overlay matrix at the corresponding depth.

6. **Assembly-level optimization.** If we can read the program, we can
   optimize it. Redundant gratings (consecutive identity passes) could
   be collapsed. Parallel-reducible sequences could be fused.

## Connects To

- **mechanism-extraction.md** — micro-model version of the same finding
- **crystal-universality.md** — why KIBC are the fixed points
- **ffn-beta-reduction-indexing.md** — the holographic indexing mechanism
- **grating-cascade.md** — compound gratings, cross-PC coupling
- **project-thesis.md** — this IS the thesis: pretraining = beta reduction
- **tracer-works-different-programs** (memory) — original 14B confirmation
- **pretraining-is-beta-reduction** (memory) — the deepest insight
- **kibc-32b-probe-validation** (memory) — KIBC confirmed in 32B
