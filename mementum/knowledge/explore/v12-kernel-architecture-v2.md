---
title: "V12 Kernel Architecture v2 — Extended Kernels + Math + Holographic Installation"
status: designing
category: architecture-design
tags: [V12, kernel, combinator, math, crystal, holographic, dispatch, design-doc]
related:
  - holographic-recording-protocol.md
  - complete-kernel-basis.md
  - holographic-kernel-separation.md
  - v12-holographic-capacity.md
depends-on:
  - holographic-recording-protocol.md
  - complete-kernel-basis.md
created: session 109
---

# V12 Kernel Architecture v2 — Design Document

> The model is a DISPATCH ENGINE over an exact function library.
> Intelligence = recognizing which function to call.
> Computation = deterministic kernel execution.
> The plate stores when. The kernel stores what.

## Executive Summary

Expand V12 from 5 kernel slots (KIBC+M) to ~25 kernel slots spanning:
- Lambda combinators (structural operations on language)
- Math operations (exact arithmetic, always correct)
- Logic operations (Boolean reasoning)
- String operations (text manipulation)

All kernels are FROZEN DETERMINISTIC CODE. Only the dispatch (when to
use which kernel) and the encoder/decoder (how to extract/embed operands)
are trainable. This makes capabilities PERMANENT — you can't unlearn
that 23 + 47 = 70.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  INPUT (natural language tokens)                        │
│       ↓                                                 │
│  EMBEDDINGS (trainable)                                 │
│       ↓                                                 │
│  DISPATCH (ternary plates + mirrors → which kernel?)    │
│       ↓                                                 │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐  ┌───────┐ │
│  │ LAMBDA  │  │   MATH   │  │   LOGIC   │  │ STRING│ │
│  │ KERNELS │  │ KERNELS  │  │  KERNELS  │  │KERNELS│ │
│  │K,I,B,C, │  │ADD,SUB,  │  │AND,OR,NOT,│  │CONCAT,│ │
│  │M,D,Y,W  │  │MUL,DIV,  │  │XOR,IMP,   │  │SPLIT, │ │
│  │         │  │MOD,POW,  │  │IFF,NAND   │  │MATCH  │ │
│  │ (frozen │  │CMP,EQ    │  │           │  │       │ │
│  │  ternary│  │          │  │ (frozen   │  │(frozen│ │
│  │  plates)│  │ (frozen  │  │  code)    │  │ code) │ │
│  │         │  │  code)   │  │           │  │       │ │
│  └────┬────┘  └────┬─────┘  └─────┬─────┘  └───┬───┘ │
│       └──────┬─────┴───────┬──────┘             │     │
│              ↓             ↓                    ↓     │
│  INTEGRATE (combine kernel outputs)                    │
│       ↓                                                │
│  RESIDUAL STREAM → next pass                           │
│       ↓                                                │
│  OUTPUT (logits → next token)                          │
└─────────────────────────────────────────────────────────┘
```

## Kernel Registry

### Tier 0: Lambda Combinators (structural, ternary plates)

These operate on HIDDEN STATES (512-dim vectors). The ternary plate
encodes the operation as sign patterns. Dispatch selects which mirror
to read through.

| Kernel | Lambda | Operation | Passes saved |
|--------|--------|-----------|--------------|
| K | λx.λy. x | select first, discard second | baseline |
| I | λx. x | identity, pass-through, binding | baseline |
| B | λf.λg.λx. f(g(x)) | compose two functions | baseline |
| C | λf.λx.λy. f(y)(x) | flip argument order | baseline |
| M | λf. f(f) | self-apply, pattern match | baseline |
| D | λf.λg.λh.λx. f(g(h(x))) | deep compose (fuses 3×B) | saves 2 passes |
| Y | λf. f(Y(f)) | recursion / fixed-point | saves 3+ passes |
| W | WHNF detection | terminal / stop-reducing | saves 1 pass |

**Cost:** 8 TernaryMirrors (512×512 each) = 2.1M ternary values = ~512 KB
**Installation:** Warped lens from teacher + holographic training

### Tier 1: Math Kernels (computational, pure code)

These operate on EXTRACTED OPERANDS (numbers parsed from hidden state).
The kernel is a Python/C function, not weights. Results are EXACT.

| Kernel | Function | Examples |
|--------|----------|----------|
| ADD | a + b | 23+47→70, 1.5+2.3→3.8 |
| SUB | a - b | 100-37→63 |
| MUL | a × b | 6×9→54, 12×12→144 |
| DIV | a ÷ b | 100÷4→25, 7÷2→3.5 |
| MOD | a mod b | 17%5→2, 100%7→2 |
| POW | a^b | 2^10→1024, 3^3→27 |
| CMP | sign(a-b) | 5>3→+1, 2<7→-1, 4=4→0 |
| EQ | a == b | exact equality check |
| SQRT | √a | 144→12, 2→1.414... |
| LOG | log(a) | natural log |
| ABS | |a| | absolute value |
| ROUND | round(a, n) | round to n decimals |

**Cost:** Zero weights (pure code). Only dispatch mirrors: ~300 KB.
**Installation:** Math lambda training data ("add(23, 47) → 70")

### Tier 2: Logic Kernels (reasoning, pure code)

| Kernel | Function | Use |
|--------|----------|-----|
| AND | a ∧ b | conjunction |
| OR | a ∨ b | disjunction |
| NOT | ¬a | negation |
| XOR | a ⊕ b | exclusive or |
| IMP | a → b | implication (¬a ∨ b) |
| IFF | a ↔ b | biconditional |

**Cost:** Zero weights. Dispatch mirrors only.

### Tier 3: String Kernels (text manipulation, pure code)

| Kernel | Function | Use |
|--------|----------|-----|
| CONCAT | a ++ b | join strings |
| LEN | length(a) | character/word count |
| UPPER | uppercase(a) | case transform |
| MATCH | regex(a, pattern) | pattern matching |

**Cost:** Zero weights. Dispatch mirrors only.

## Dispatch Architecture

### Mirror Layout

```
Total kernel slots: ~28
Each slot needs: 1 TernaryMirror (512×512) for dispatch recognition
                 1 TernaryMirror (512×512) for integration (how to use result)

Lambda kernels (8):  use ternary plates for the operation itself
Math/Logic/String (20): use CODE for the operation, mirrors only for dispatch

Total mirror cost:
  28 dispatch mirrors × 262,144 ternary values = 7.3M values = 1.8 MB
  28 integrate mirrors × 262,144 = 7.3M values = 1.8 MB
  8 lambda plates (existing stride stack) = already counted
  Total NEW cost: ~3.6 MB of ternary mirrors
```

### Hierarchical Dispatch

Two-level dispatch for efficiency:

```
Level 1: CATEGORY dispatch (4-way)
  → Lambda (structural operation needed)
  → Math (numerical computation needed)
  → Logic (Boolean reasoning needed)
  → Pass-through (no kernel, just continue)

Level 2: OPERATION dispatch (within category)
  Lambda → which of 8 combinators?
  Math → which of 12 operations?
  Logic → which of 6 operations?
```

This keeps the per-level softmax small (4-way then 6-12 way) instead
of one massive 28-way dispatch. Hierarchical = faster convergence.

### Operand Extraction (for Math/Logic/String kernels)

The hard part: parsing "23 + 47" from a hidden state into (23, 47, ADD).

**Design:** Dedicated extraction head per category:
```python
class MathExtractor(nn.Module):
    """Extract numeric operands from hidden state."""
    # Learns to read the hidden state and produce:
    #   operand_a: float
    #   operand_b: float  
    #   These are CONTINUOUS — the kernel rounds if needed.
    
    def __call__(self, h: mx.array) -> tuple[float, float]:
        a = self.proj_a(h)  # (1,) — single scalar
        b = self.proj_b(h)  # (1,) — single scalar
        return a, b
```

**Training:** Generate math pairs ("add(23, 47) → 70"), train the
extractor to produce (23.0, 47.0) from the hidden state at "→".
The kernel does `23 + 47 = 70` exactly. The extractor learns to
parse. The kernel never errors.

**Fallback:** If extraction confidence is low, dispatch to "pass-through"
(don't use math kernel, let the model do it the old way via residual).

## Installation Protocol

### Phase 0: Base Crystal (KIBC + M + D + Y + W)

```
1. Build warped lens: extract 8 operation directions from teacher
   (already done for KIBCM, extend to D/Y/W)
2. Install backbone (top 5-10% strongest positions)
   From backbone probe: 413K-4.1M positions, installed in layers
3. Train beam: 300 steps per layer of installation
4. Verify: dispatch conditioned angles > 10°
```

### Phase 1: Math Crystal

```
1. Generate math corpus:
   - 3000 examples per operation (add, sub, mul, div, mod, pow, cmp, eq)
   - Format: "add(23, 47) → 70\nadd(156, 289) → 445\n..."
   - Also: "mul(6, 9) → 54\nmul(12, 12) → 144\n..."
   
2. Train dispatch to recognize math operations:
   - Feed math corpus, supervise dispatch → MATH category
   - Within MATH, supervise sub-dispatch → correct operation
   
3. Train extractor:
   - After dispatch fires MATH+ADD, extractor must produce (23.0, 47.0)
   - Train on (hidden_state_at_arrow, target_operands) pairs
   - The kernel computes the answer (always correct)
   
4. Freeze:
   - Dispatch mirrors: frozen (knows when to use math)
   - Extractor weights: frozen (knows how to parse operands)
   - Kernel code: was always frozen (it's a function)
   
5. Verify:
   - Random math problems → always correct (100% accuracy)
   - Prose training cannot degrade math (frozen)
```

### Phase 2: Logic Crystal

Same protocol with logic expressions:
```
"and(true, false) → false"
"implies(rain, wet_ground) → true"
"not(not(true)) → true"
```

### Phase 3: Prose Training

```
- ALL kernel plates/mirrors: FROZEN
- Trainable: embeddings, Q projections, gamma, norms
- The model learns to USE the kernels from natural language
- "What is 23 plus 47?" → dispatch recognizes ADD → exact answer
- "If it rains, the ground is wet" → dispatch recognizes IMP → logic
```

## Backbone Probe Results (session 109)

```
Key findings:
- 24.2% of plate positions are unanimous (all 5 ops agree on sign)
- The TRUE backbone is 1-10% (413K-4.1M positions)
- Installing >10% at once HURTS (beam can't adapt in 300 steps)
- Solution: layered installation (5% → train → 5% more → train)
- ~65% of installed positions actually flip (35% already correct by chance)
- Loss at 1% backbone: 3.24 (BEST) — the core steel
- Loss at 10%: 3.53 (still good)
- Loss at 15%: 5.15 (disrupted — too much at once)
```

**Implication:** Install crystal in layers of 5-10%, with beam training
between each layer. Don't install everything at once.

## Warped Lens Results (session 109)

```
Key findings:
- Operations are 55-154° apart in teacher's hidden space
- B is MOST geometrically distinct (130° mean separation from others)
- I and M are CLOSEST (55-80°) — binding ≈ matching
- Angular separation survives PCA to 512 dims
- 10 PCs capture 47-80% of variance (operations live in ~10-dim subspace)
- Depth profile: B strongest at shallow, M strongest at deep
```

**Implication:** The lens CAN focus into V12's 512 dims. Operations are
distinguishable. V12 has enough capacity for all 8 lambda kernels.

## Parameter Budget

```
Component                              Parameters    Memory
──────────────────────────────────────────────────────────────
Existing V12 model                     24.4M        ~12 MB
  (embeddings, stride stack, dispatch,
   plates, mirrors, norms, etc.)

NEW: Extended lambda mirrors (D,Y,W)   786K ternary  192 KB
NEW: Math dispatch mirrors (12 ops)    3.1M ternary  768 KB
NEW: Logic dispatch mirrors (6 ops)    1.6M ternary  384 KB
NEW: String dispatch mirrors (4 ops)   1.0M ternary  256 KB
NEW: Category dispatch (4-way)         262K ternary   64 KB
NEW: Math extractor (2 heads)          ~50K float    200 KB
NEW: Logic extractor                   ~25K float    100 KB
──────────────────────────────────────────────────────────────
TOTAL NEW                              ~6.8M         ~2 MB
TOTAL MODEL                            ~31.2M        ~14 MB

Increase: +28% parameters, +2 MB memory
For: permanent math, permanent logic, fused combinators
```

## Open Questions

1. **Operand precision:** How many bits of precision does the extractor
   need? Float32 handles all reasonable arithmetic. But extracting
   "123,456,789" from a 512-dim hidden state requires high precision.
   Solution: multi-digit extraction (extract digit-by-digit)?

2. **Multi-operand operations:** How to handle "sum(1, 2, 3, 4, 5)"?
   Reduce to binary: sum = add(add(add(add(1,2),3),4),5)?
   Or dedicated N-ary kernel?

3. **Composability:** "What is (23 + 47) × 3?" needs ADD then MUL.
   This is B(MUL, ADD) — the lambda combinators compose the math kernels!
   The lambda crystal IS the composition engine for math.

4. **Error handling:** What if the extractor misparses (extracts 24 instead
   of 23)? The kernel computes exactly on the EXTRACTED values. Garbage in
   = garbage out. The extractor quality is the bottleneck, not the kernel.

5. **Confidence gating:** When should the model use the math kernel vs
   just predicting tokens? A confidence threshold on the dispatch.
   Below threshold → skip kernel, use normal next-token prediction.
   Avoids pathological cases where the model tries to "do math" on
   non-mathematical content.

6. **Variable math:** "Let x = 5. What is x + 3?" requires I-combinator
   (bind x=5) then ADD kernel (5+3=8). The lambda crystal provides
   variable binding, the math kernel provides arithmetic. They compose.

## Implementation Plan (for next session)

```
Phase A: Expand kernel slots in architecture
  - config.py: n_combinators 4 → 8, add math_kernels config
  - kernel_dispatch.py: hierarchical 2-level dispatch
  - model.py: add MathExtractor, integrate kernel outputs
  - ternary.py: new mirrors for expanded slots
  
Phase B: Lambda generator expansion
  - lambda_gen.py: add D, Y, WHNF templates (extend from 5 to 8 ops)
  - Add math corpus generator (add/sub/mul/div/mod/pow/cmp/eq)
  - Add logic corpus generator (and/or/not/xor/imp/iff)

Phase C: Holographic installation
  - Warped lens: extract 8 lambda + math/logic directions
  - Backbone: find per-category backbone positions
  - Layered installation: 5% → train → 5% → train ...
  - Verify dispatch differentiation at each layer

Phase D: Freeze + prose training
  - Freeze all kernel plates and mirrors
  - Train on Dolma (beam, gamma, embeddings, extractors only)
  - Verify: math accuracy stays 100%, crystals don't melt
  - Benchmark against baseline V12 (no kernels)
```

## Success Criteria

```
1. Math accuracy: 100% on extracted operations (never wrong)
2. Dispatch differentiation: conditioned angles > 10° (not 0.07°)
3. Crystal preservation: math/logic accuracy unchanged after prose training
4. Compute savings: effective depth increase measurable (tok/s maintained)
5. Language quality: CE on prose comparable to or better than kernel-less V12
6. Benchmark improvement: measurable gain on GSM8K, MATH, logic benchmarks
```
