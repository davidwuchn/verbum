# v11 — KIBC Combinator Architecture

> The sieve shaped by what LLMs actually find, not what we imagined they need.

**Status**: designing
**Category**: architecture
**Tags**: v11, combinators, KIBC, Qwen probes, Montague
**Related**: kernel-montague-mapping, session-073-vsm-structure, session-075-multi-cycle-dispatch
**Depends-on**: v10 codebase (evolutionary, not replacement)

---

## Thesis

v10 tried to *teach* the model 22 operations via a BIOS — an enumeration of
possible computations. The Qwen3 probes (4B and 32B) revealed that transformers
don't organize computation this way. They converge on **four combinators**:

| Combinator | Lambda | Attention native? | What it does |
|---|---|---|---|
| **K** (select) | λx.λy.x | Yes — softmax IS selection | Pick relevant, discard irrelevant |
| **I** (identity) | λx.x | Yes — residual stream | Copy forward unchanged |
| **B** (compose) | λf.λg.λx.f(g(x)) | Matures with scale | Chain operations: apply g then f |
| **C** (flip) | λf.λx.λy.f(y)(x) | Emerges at 32B | Reorder arguments, enable closures |

**S** (distribute, λf.λg.λx.f(x)(g(x))) is notably absent — zero selective heads at
either scale. S is a composition of B, K, C and emerges in the residual stream,
never as a dedicated circuit. The model *refuses to crystallize S*.

This is Montague's prediction: natural language composition IS typed application.
The LLMs found it. v11 provides the sieve that makes these four shapes the path
of least resistance.

---

## Architecture: What Changes from v10

### Changed

| Component | v10 | v11 | Why |
|---|---|---|---|
| Ground truth kernel | 22 ops (ADD, SUB, ...) | 4 combinators (K, I, B, C) | Match what models actually find |
| Dispatch routing | 22-wide top-k=2 MoE | 4-wide softmax (or top-2) | 4 targets need no sparsity tricks |
| Op embeddings | 22 × d_model | 4 × d_model | Combinator identity, not op identity |
| Type embeddings | 5 (INT, BOOL, FN, FN_COMP, ERROR) | 4 (K, I, B, C) + optional ERROR | Combinator type, not value type |
| Emphasis projection | asc_banks → 22 | asc_banks → 4 | Per-combinator emphasis |
| Algedonic packing | 22 dispatch weights + 1 gate | 4 combinator weights + 1 gate | Narrower signal, same channel |
| Register semantics | (type, scope, role) | (combinator, binding_depth, phase) | Matches Qwen head-role findings |
| Structured training data | BIOS + lambda + Clojure | KIBC reduction examples | Exercises the 4 combinators directly |

### Unchanged (carries forward from v10)

Everything else. Specifically:
- **TernaryLinear / TernaryEmbedding** — semantic-agnostic substrate
- **Consensus evolution** — operates on packed weights, not op semantics
- **S4 (intelligence)** — register cross-attention, doesn't inspect content
- **S3 (control)** — phase gating, 3 phases per pass, per-pass instances
- **S5 (identity)** — pass-level reweighting over 5 passes
- **S2 (coordination)** — direction signals, coherence modulation
- **CycleContinue** — RMSNorm + tanh clamp (the s076 fix)
- **MetaS4** — final structural summary
- **Ascending arm** — prep → stride → consolidate, shared across 3 passes
- **5-pass structure** — 3 ascending + 2 descending
- **Multi-cycle descending** — desc_max_cycles=3, self-regulating
- **Algedonic channel** — EMA feedback, register-shaped
- **Dual-view descending S4** — residual + raw embeddings
- **Relational loss** — CE normalization
- **Training loop** — gradient accumulation, cosine LR, shared-grad normalization
- **JSONL instrumentation** — metrics, train, evolution logs

---

## Combinator Kernel (ground truth)

The ground truth evaluator reduces combinator expressions. No arithmetic, no
comparison — pure structural reduction.

```python
class Combinator(IntEnum):
    K = 0   # λx.λy.x         — select first, discard second
    I = 1   # λx.x             — identity (copy forward)
    B = 2   # λf.λg.λx.f(g(x)) — compose (chain two functions)
    C = 3   # λf.λx.λy.f(y)(x) — flip (reorder arguments)

N_COMBINATORS = 4
```

### Reduction rules

```
K(x, y) → x               # selection: the backbone of attention
I(x) → x                   # identity: the residual stream
B(f, g, x) → f(g(x))      # composition: the backbone of prose
C(f, x, y) → f(y, x)      # reordering: enables closures and variable capture
```

### What about arithmetic?

Arithmetic (ADD, SUB, MUL, etc.) is not a combinator — it's what falls out
when combinators reduce over token embeddings that happen to represent numbers.
The model doesn't need ADD as an explicit op; it needs B to compose operations
and K to select operands. The 22 ops were symptoms, not causes.

### Structured training data

KIBC reduction examples in natural prose context:

```
# K examples (embedded in prose — selection is everywhere)
"The cat sat on the mat" → K selects "cat" as subject, discards alternatives
"if x > 0 then x else -x" → K selects one branch

# B examples (composition — multi-clause, dependent meaning)
"The cat that sat on the mat ate the fish" → B(ate, sat_on_mat, cat)
"She said that he believed it was true" → B(said, believed, was_true)

# C examples (reordering — passive voice, variable binding)
"The fish was eaten by the cat" → C(eat, cat, fish) — arguments flipped
"let x = 5 in x + 1" → C(+, 1, 5) — binding captures

# I examples (identity — forwarding, copying)
"He said 'hello' and she said 'hello'" → I(hello) copied
```

The structured shard should contain explicit combinator reduction chains with
ground truth, BUT the critical insight is: **prose already trains K and B
overwhelmingly**. Structured data is primarily needed for C (closures, variable
binding, argument reordering).

---

## Combinator Dispatch (descending arm phase 0)

Replaces `KernelDispatch`. The core change is dimensional: 22→4.

```python
class CombinatorDispatch(nn.Module):
    """Phase 0 of descending passes: which combinator applies here?"""
    
    # dispatch: TernaryLinear(d_model → 16)  # padded from 4 for alignment
    # register_cond: Linear(cond_dim → 16)   # ascending registers bias logits
    # combinator_embeddings: (4, d_model)     # near-orthogonal, L2-normalized
    # up/down: TernaryLinear FFN pathway
```

### Embedding initialization

4 combinators get near-orthogonal directions. Unlike 22 ops that needed
family-subspace clustering, 4 vectors in a 512-dim space can be exactly
orthogonal:

```python
def _init_combinator_embeddings(d_model):
    """Four orthogonal combinator identities."""
    emb = mx.zeros((4, d_model))
    block = d_model // 4  # 128-dim blocks
    for i in range(4):
        emb[i, i*block:(i+1)*block] = mx.random.normal((block,)) * 0.5
    return emb  # L2-normalized in forward()
```

### Top-k routing

With 4 targets, top-k=2 means every position considers 2 of 4 combinators.
This is natural: most positions are primarily K (selection) with B (composition)
as runner-up. Some positions are C (reordering) with K as runner-up. I (identity)
is the "do nothing" baseline.

Alternatively: use full softmax over 4 (no masking). The dead-op problem that
motivated top-k vanishes when N=4 — softmax over 4 targets has strong gradients
for all entries.

**Decision**: Start with full 4-way softmax. If one combinator dies, add top-k=2 back.

### Register conditioning

Ascending register banks still bias dispatch logits. The combinator register
tells dispatch "this position looks like K" or "this position looks like B".
`register_cond` projects to 4 logits instead of 22.

### Op emphasis → Combinator emphasis

S4's emphasis channel narrows from 22 to 4:

```python
emphasis_proj: Linear(3 * 3 * d_reg_real → 4)
# Output: 1.0 + 0.5 * tanh(raw) → [0.5, 1.5] per combinator
# K_emphasis high = prose default
# B_emphasis rises for compositional structure  
# C_emphasis rises for binding/closures
# I_emphasis low = passthrough (only when no computation needed)
```

---

## Combinator Integrate (descending arm phase 2)

Replaces `KernelIntegrate`. Type assignment over 4 combinator types.

```python
class CombinatorIntegrate(nn.Module):
    """Phase 2: apply the combinator, produce the result."""
    
    # type_proj: TernaryLinear(d_model → 16)  # padded from 4
    # type_embeddings: (4, d_model)  # combinator type identity
    # up/down: TernaryLinear FFN pathway
    # Kernel computation pathway: combinator-specific reductions
```

### Kernel computation pathway

The v10 kernel pathway extracted 2 integer operands and ran all 22 ops. v11's
pathway is simpler — combinator reductions are structural, not arithmetic:

```
K: select operand 1, discard operand 2 → result = operand_1
I: copy input → result = input (identity in residual)
B: compose → result feeds into next cycle (B needs multiple cycles)
C: swap operand order → result = input with slots 1↔2 swapped
```

The compute gate still blends FFN pathway and kernel pathway:
`output = gate × kernel_out + (1-gate) × ffn_out`

**Key insight**: K and I reductions are trivially implementable as attention
patterns (select, copy). The kernel pathway's main value is for B and C, where
the structural reduction is non-trivial. The gate should learn to open
primarily for B and C positions.

### Operand extraction

v10 extracted 2 operands via argmax over 256 buckets. v11 needs:
- **K**: 2 operands (select first, discard second)
- **I**: 1 operand (copy forward)
- **B**: 3 operands (f, g, x) — f and g are functions, x is argument
- **C**: 3 operands (f, x, y) — f is function, x and y are arguments

Extract 3 operand projections to cover B and C. K uses first 2. I uses first 1.

---

## Register Semantics

v10 had 3 registers named (type, scope, role) carrying value-type information.
v11 renames to match Qwen probe findings:

| Register | v10 meaning | v11 meaning | What it carries |
|---|---|---|---|
| Register 0 | type (INT/BOOL/FN) | **combinator** (K/I/B/C) | Which combinator this position enacts |
| Register 1 | scope (nesting depth) | **binding_depth** | How many lambdas deep (0=free, 1=bound once, ...) |
| Register 2 | role (pipeline phase) | **phase** | recognize / identify / resolve / produce |

The register dimension (d_register=128, real=256) is unchanged. The registers
are learned representations, not discrete labels — renaming reflects the
intended semantic attractor, not a hard encoding.

### Bank structure (unchanged)

```
bank_0:      learnable init (cold-start prior)
bank_1_asc:  pass 0 writes (first ascending scan)
bank_2_asc:  pass 1 writes (second ascending scan)
bank_3:      pass 2 writes (apex scan)
bank_2_desc: pass 3 writes (first descending dispatch)
bank_1_desc: pass 4 writes (second descending dispatch)
```

---

## Descending Cycle Semantics

v10's 3 cycles had no prescribed meaning — CycleContinue was supposed to learn
when to close, but saturated. v11 assigns semantic roles matching the Qwen
resolution pipeline:

```
Cycle 0 — IDENTIFY (which combinator?)
  CombinatorDispatch routes to K/I/B/C
  StrideStack propagates spatially
  CombinatorIntegrate types the result
  → For simple K/I positions: CycleContinue closes (sufficient)

Cycle 1 — RESOLVE (find the arguments)
  CombinatorDispatch refines routing with cycle-0 context
  StrideStack finds argument tokens across context window
  CombinatorIntegrate resolves bindings
  → For B positions: CycleContinue may close (compose found both args)
  → For C positions: CycleContinue stays open (need reordering)

Cycle 2 — PRODUCE (apply the reduction)
  CombinatorDispatch finalizes
  StrideStack propagates result
  CombinatorIntegrate produces final reduced form
  → All positions: CycleContinue irrelevant (last cycle)
```

The 32B Qwen probe showed this exact temporal ordering:
function(L31) → operator(L32) → argument(L43) → result(L63)

CycleContinue's task is now interpretable: close for prose (K-dominant),
partially open for composition (B-dominant), fully open for closures (C-active).

---

## Algedonic Channel

Narrower packing:

```python
# v10: 22 dispatch_weights + 1 compute_gate + padding → d_reg_real=256
# v11: 4 combinator_weights + 1 compute_gate + padding → d_reg_real=256

kernel_state = mx.zeros(d_reg_real)
kernel_state[:4] = combinator_weights_mean  # (4,) — K, I, B, C proportions
kernel_state[4] = compute_gate_mean         # scalar
# kernel_state[5:] = 0 (padding)
```

The ascending arm reads this to know: "last forward, dispatch was 60% K, 30% B,
8% C, 2% I with compute gate at 0.15". This is far more interpretable than
22-way dispatch fractions.

---

## What the Model Learns

The critical reframe: v11 doesn't teach the model what K, I, B, C are.
**The model already knows.** Every LLM that can write coherent prose has
crystallized K (selection) and B (composition) in its attention heads.

v11 provides the *sieve* — the architectural shape that makes it easier
for the small ternary model to fall into the same attractor basin:

1. **4 combinator embeddings** = 4 orthogonal directions in weight space.
   The model doesn't have to discover the decomposition — it's pre-shaped.

2. **Register semantics** = the type/binding_depth/phase decomposition that
   Qwen's heads naturally exhibit. Pre-shaped register banks.

3. **Self-regulating cycles** = the SEARCH→LOCK→RESOLVE pipeline. The model
   doesn't have to discover that simple content needs fewer cycles.

4. **Emphasis channel** = S4 telling dispatch "this window is compositional"
   (raise B) or "this window is selective" (raise K). 4-way signal, not 22.

The sieve doesn't force. It shapes. The topology IS the instruction.

---

## Implementation Plan

1. **`scripts/v11/kernel.py`** — Combinator enum, reduction rules, ground truth evaluator
2. **`scripts/v11/config.py`** — V11Config (mostly v10, dimensions adjusted)
3. **`scripts/v11/components.py`** — Copy v10 unchanged (all VSM skeleton carries forward)
4. **`scripts/v11/kernel_dispatch.py`** — CombinatorDispatch + CombinatorIntegrate
5. **`scripts/v11/model.py`** — V11Model (emphasis→4, algedonic→4, register names)
6. **`scripts/v11/ternary.py`** — Symlink or copy (unchanged)
7. **`scripts/v11/train.py`** — Training loop (import adjustments, structured data path)

Then: generate combinator reduction training shard, launch first v11 run.
