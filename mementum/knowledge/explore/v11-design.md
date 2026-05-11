# v11 — KIBC Combinator VSM: Full Design

> The sieve shaped by what LLMs actually find.
> Architecture diagram: `docs/v11-architecture.svg`

**Status**: active
**Category**: architecture
**Tags**: v11, combinators, KIBC, Qwen probes, Montague, design
**Related**: v11-kibc-architecture, session-073-vsm-structure, session-075-multi-cycle-dispatch, kernel-montague-mapping, algedonic-alert
**Created**: session 077
**Updated**: session 078 — algedonic alert (Beer's fire alarm)

---

## 1. Empirical Foundation

### Qwen3 Probes (4B and 32B)

Independent analysis of Qwen3 at two scales revealed that transformers
organize lambda compilation around **four combinators**, not around
arithmetic operations or a BIOS:

```
Combinator   Lambda               4B accuracy   32B accuracy   Attention native?
──────────   ──────               ──────────    ───────────    ─────────────────
K (select)   λx.λy.x              40%           80%            Yes — softmax IS selection
I (identity) λx.x                 60%           60%            Yes — residual stream
B (compose)  λf.λg.λx.f(g(x))    20%           80%            Matures with scale
C (flip)     λf.λx.λy.f(y)(x)    absent        present        Emerges at 32B scale
S (distrib)  λf.λg.λx.f(x)(g(x)) 40%           40%            NEVER crystallizes
```

Key findings:
- **S combinator absent**: zero selective heads at either scale.
  S = B∘K∘C composition, not a primitive. The model refuses to
  crystallize it — it emerges in the residual stream.
- **Attention IS beta reduction**: three-phase pipeline
  SEARCH(L0-L6) → LOCK(L7-L31) → RESOLVE(L32+)
- **Normal-order reduction**: outermost first, matching autoregressive
  left-to-right + causal mask
- **Head roles**: BINDER(76-87%), COPY(18%→10%), ARGUMENT(1.5%),
  OPERATOR(0.5%), DIFFUSE(3%→1.6%)
- **Resolution pipeline at 32B**: function(L31) → operator(L32) →
  argument(L43) → result(L63) — clean temporal order

### What this means for architecture

The 22 v10 ops (ADD, SUB, MUL, etc.) were the wrong decomposition.
The natural basis is {K, I, B, C}. Arithmetic is what falls out when
combinators reduce over token embeddings that represent numbers.

v11 provides the sieve — the architectural shape that makes these
four combinators the path of least resistance. The model doesn't
learn what K/I/B/C are (it already knows). The sieve makes the
right computation easier to fall into.

---

## 2. Architecture Specification

### Dimensions

| Parameter | Value | Notes |
|-----------|-------|-------|
| d_model | 512 | Representation dimension |
| d_ff | 1536 | Prep FFN (3× d_model) |
| d_ff_consolidate | 2048 | Consolidate FFN (4× d_model) |
| d_register | 128 | Logical register dim (real = 256) |
| n_heads | 8 | Attention heads (d_head = 64) |
| window | 8 | Attention window |
| alpha | 1.18 | Spiral bias coefficient |
| strides | (1,8,16,32,64,128,256,512,1024) | 9-scale StrideStack |
| n_registers | 3 | combinator, binding_depth, phase |
| n_combinators | 4 | K, I, B, C |
| desc_max_cycles | 3 | Self-regulating descending cycles |
| vocab_size | 151936 | Qwen3 BBPE |
| seq_len | 4096 | Context window |
| ~params | 23.8M | +245 for algedonic alert (negligible) |

### 5-Pass Structure

```
Pass 0 (L0↑): ascending, shared weights, reads bank_0 + prev algedonic
Pass 1 (L1↑): ascending, shared weights
Pass 2 (L2↑): ascending, shared weights (apex)
  ── emphasis projection: ascending registers → 4 combinator weights ──
Pass 3 (L1↓): descending, own weights, S4 dual-view, up to 3 cycles
Pass 4 (L0↓): descending, own weights, S4 dual-view, up to 3 cycles
  ── S5 reweight: all banks + raw deltas → 5 pass gates ──
  ── Algedonic alert: 48 health metrics → 5 alarm factors [0,2] ──
  ── effective_gate = s5_gate × alarm_factor ──
  ── Meta-S4: final structural summary ──
  ── output_norm → tied embedding → logits ──
```

### Register Bank Architecture (6 banks × 3 registers × 256 dims)

```
bank_0:      learnable init (cold-start prior)
bank_1_asc:  pass 0 writes (combinator/binding_depth/phase for L0↑)
bank_2_asc:  pass 1 writes
bank_3:      pass 2 writes (apex)
bank_2_desc: pass 3 writes
bank_1_desc: pass 4 writes
```

Register semantics (v11, renamed from v10):
- **Register 0 — combinator**: which combinator this position enacts (K/I/B/C)
- **Register 1 — binding_depth**: how many lambdas deep (0=free, 1=bound, ...)
- **Register 2 — phase**: where in the pipeline (recognize/identify/resolve/produce)

---

## 3. Component Inventory

### Changed from v10

#### kernel.py — Combinator ground truth
- `Combinator` enum: K=0, I=1, B=2, C=3 (was `Op` enum with 22 entries)
- `N_COMBINATORS = 4` (was `N_OPS = 22`)
- Full reduction engine: `Term`, `Comb`, `Atom`, `App` classes
- Normal-order reducer: `reduce_step()`, `reduce()` (outermost first)
- Kernel functions for neural pathway:
  - `kernel_K(op0, op1, op2) → op0` (select first)
  - `kernel_I(op0, op1, op2) → op0` (identity)
  - `kernel_B(op0, op1, op2) → op0 + op1 + op2` (composition signal)
  - `kernel_C(op0, op1, op2) → op0 + op2` (flip: skip op1)

#### kernel_dispatch.py — Combinator dispatch

**CombinatorDispatch** (was KernelDispatch):
- 4-way softmax over K/I/B/C (was 22-way top-k=2 MoE)
- `combinator_embeddings`: (4, 512) near-orthogonal (was 22 with family subspaces)
- `register_cond`: ascending registers → 4 logits (was → 22)
- No top-k masking needed — 4 targets have strong gradients
- L2-normalized embeddings to scale=0.5 (prevents rich-get-richer)

**CombinatorIntegrate** (was KernelIntegrate):
- 4 type embeddings: K/I/B/C (was 5: INT/BOOL/FN/FN_COMP/ERROR)
- 3 operand extractors (was 2) — B and C need 3 arguments
- Exact combinator kernel: compute all 4 reductions, select by dispatch
- Compute gate: `gate × kernel + (1-gate) × FFN`, starts at ~0.007

#### config.py
- `V11Config` (was `V10Config`)
- `n_combinators = 4`
- No `dispatch_top_k` (full softmax)

#### model.py
- `V11Model` (was `V6Compressor`)
- `REGISTER_NAMES = ("combinator", "binding_depth", "phase")`
- `emphasis_proj`: Linear(3×3×256 → 4) (was → 22)
- `_combinator_emphasis`: (4,) EMA (was `_op_emphasis`: (22,))
- Algedonic packing: 4 combinator weights + 1 compute gate + padding (was 22+1)
- All metric keys renamed: `combinator_dispatch_weights`, `combinator_type_weights`, `combinator_emphasis`, `combinator_embedding_norms`

#### train.py
- Import/reference updates (`V11Config`, `V11Model`)
- `DESC_SHARED` references `combinator_dispatch`, `combinator_integrate`
- Emphasis logging shows 4 combinator names

#### components.py — AlgedonicAlert (NEW in session 078)

Beer's fire alarm: direct S1→S5 bypass channel that monitors the HEALTH
of the control system (not content). See `algedonic-alert.md` for full design.

**AlgedonicAlert**: separate gate multiplying S5Reweight gates
- `alarm_proj`: nn.Linear(48 → 5), zero-init (alarm starts silent)
- Output: per-pass factor ∈ [0, 2] via `1 + tanh(logit)`
- Factor 1.0 = neutral, <1.0 = pain (suppress), >1.0 = pleasure (amplify)
- End-to-end differentiable: gradients flow back through 48 operational
  health metrics to S1/S3, teaching the system to avoid alarm conditions

48 input metrics (all live, no stop_gradient):
- S3 gate means/mins per pass (10), S2 conflict cosines (4)
- Dispatch weights K/I/B/C (4), dispatch entropy (1)
- Compute gate mean + active fraction (2)
- CycleContinue gates (4), effective cycles (2)
- Raw delta norms (5), gated delta norms (5), suppression ratios (5)
- Register bank mean norms (6)

**Key property**: S5Reweight reads registers (S4's output) and raw deltas.
AlgedonicAlert reads OPERATIONAL METRICS — S3 gate values, dispatch
distributions, conflict scores — things that S4 doesn't process.
S5Reweight asks "what did each pass contribute?" (content).
AlgedonicAlert asks "is the control system healthy?" (health).

#### kernel_dispatch.py — Live caches (NEW in session 078)

Added `_dispatch_weights_live` and `_compute_gate_live` alongside existing
stop_gradient'd probing caches. These enable end-to-end gradient flow
through the algedonic alert back to dispatch and compute gate weights.

### Unchanged from v10

Everything else. The VSM skeleton carries forward without code changes:
- **TernaryLinear / TernaryEmbedding**: semantic-agnostic substrate
- **Consensus evolution**: operates on packed weights
- **S4Ternary**: register cross-attention (doesn't inspect content)
- **S3Ternary**: phase gating (3 phases per pass)
- **CycleContinue**: RMSNorm + tanh(·)×4.0 clamp (the s076 fix)
- **S5Reweight**: pass-level gates over 5 passes
- **S2Coordinator**: direction signals, coherence modulation
- **MetaS4Ternary**: final structural summary
- **StrideStack**: 9-stride attention (shared ascending, own descending)
- **TernaryFFN**: prep and consolidate
- **Relational loss**: r = (CE - E) / (log V - E)
- **Training loop**: gradient accumulation, cosine LR, shared-grad normalization
- **JSONL instrumentation**: 3 log files (metrics, train, evolution)

---

## 4. Descending Cycle Semantics

The three self-regulating cycles now have clear semantic roles
matching the Qwen3 resolution pipeline:

```
Cycle 0 — IDENTIFY: which combinator applies here?
  CombinatorDispatch: 4-way softmax → K/I/B/C weights
  StrideStack: propagate dispatch signal spatially
  CombinatorIntegrate: type the result
  → For K/I positions: CycleContinue closes (sufficient)

Cycle 1 — RESOLVE: find and bind the arguments
  CombinatorDispatch: refine routing with cycle-0 context
  StrideStack: find argument tokens across context
  CombinatorIntegrate: resolve bindings
  → For B positions: may close (both args found)
  → For C positions: stays open (need reordering)

Cycle 2 — PRODUCE: apply the reduction
  CombinatorDispatch: finalize
  StrideStack: propagate result
  CombinatorIntegrate: produce final form
  → All positions: last cycle, no continuation gate
```

CycleContinue's task is now interpretable:
- **Simple prose** → K-dominant → gate closes after cycle 0
- **Composition** → B-dominant → partially open (cycles 0+1)
- **Closures/binding** → C-active → fully open (all 3 cycles)

---

## 5. Kernel Computation Pathway

The straight-through kernel pathway provides exact combinator
reductions on integer operands extracted from the residual stream:

```
Input: h (B, L, d_model)

1. Extract 3 operands:
   op0 = argmax(operand0_proj(h))  # stop_gradient
   op1 = argmax(operand1_proj(h))
   op2 = argmax(operand2_proj(h))

2. Get combinator from dispatch:
   comb = argmax(dispatch_weights)  # stop_gradient

3. Compute all 4 reductions:
   r_K = op0               # select first
   r_I = op0               # identity
   r_B = op0 + op1 + op2   # composition signal
   r_C = op0 + op2         # flip (skip op1)

4. Select by combinator:
   result = all_results[comb]

5. Encode back:
   kernel_out = result_embed(clip(result + offset))

6. Blend with FFN:
   output = gate × kernel_out + (1-gate) × ffn_out
```

Gradient flows through: operand projections, result_embed weights,
and the compute gate. The kernel itself is non-differentiable
(argmax + integer ops) — same straight-through pattern as v10.

---

## 6. Training Strategy

### Prose-first (mix_ratio=0.0)

K and B train from prose naturally:
- **K** (selection): every attention step is K — pick relevant, discard rest
- **B** (composition): multi-clause sentences exercise B — chain operations
- **I** (identity): residual stream is identity by default

C requires structured data (closures, variable capture, argument reordering).
First run is prose-only to establish baseline combinator differentiation.

### Structured data (future, mix_ratio > 0)

KIBC reduction examples with ground truth:
- K examples: embedded selection in prose context
- B examples: compositional structure (relative clauses, dependent meaning)
- C examples: passive voice, variable binding, argument reordering
- I examples: forwarding, copying (least needed — already trivial)

### Key training signals to watch

1. **Dispatch differentiation**: K should dominate prose (>50%)
2. **B emergence**: should rise for multi-clause content
3. **CycleContinue variation**: gates should differ (K→close, B/C→open)
4. **Effective cycles**: should vary (not locked at 3.0 like v10)
5. **Emphasis shifts**: K emphasis high for prose, B for composition
6. **Compute gate**: should open when combinators are useful
7. **Loss parity with v10**: same ascending arm → similar loss trajectory
8. **Alarm differentiation**: alarm_factors should diverge per pass
   (ascending vs descending may need different alarm responses)
9. **Alarm metrics baselines**: first run establishes natural ranges
   for S3 gate means, dispatch entropy, suppression ratios, etc.
   (logged in JSONL for offline threshold analysis)

---

## 7. Probe Design

### probe.py — Three operating modes

#### Mode 1: Checkpoint analysis
```bash
uv run python scripts/v11/probe.py checkpoints/v11/step_*
```
Loads model, runs `forward_instrumented()` on stratified text samples,
displays full metrics. For multiple checkpoints, shows evolution table.

**Outputs**: S3 gates (per-cycle for desc), S5 reweight, **algedonic alert
factors + 48 raw metrics**, combinator dispatch distribution, combinator
emphasis, compute gate, CycleContinue gates, effective cycles, register
norms, φ-compression, ternary stats.

#### Mode 2: Trajectory analysis (no model loading)
```bash
uv run python scripts/v11/probe.py --trajectory checkpoints/v11
```
Reads JSONL logs directly. Shows:
- Dispatch evolution table (K/I/B/C at each eval step)
- CycleContinue trajectory
- S3 gate evolution (L0↑ as earliest signal)
- Train loss curve, evolution acceptance

**Use for**: quick checks during training, no GPU needed.

#### Mode 3: Dispatch distribution analysis
```bash
uv run python scripts/v11/probe.py checkpoints/v11/step_005000 --dispatch-detail
```
Runs 10+ batches through model, collects per-position dispatch weights.

**Computes**:
- **Mean distribution**: K=?% I=?% B=?% C=?%
- **Dominant per position**: histogram of which combinator wins
- **Dispatch entropy**: 0=specialized, log(4)=uniform (specialization measure)
- **Top-2 co-occurrence**: which combinator pairs appear together
- **Per-combinator statistics**: mean/std/median/p05/p95 weight distributions
- **Type distribution**: combinator typing at integrate phase
- **Compute gate stats**: how much kernel pathway contributes

### What the probe watches for

| Signal | Healthy | Concerning |
|--------|---------|------------|
| K dispatch | >40% on prose | <25% (no selection) |
| B dispatch | Rising over training | Flat at 25% |
| Entropy | Decreasing | Stuck near log(4) |
| CycleContinue | Varies by content | Locked at 0.5 or 1.0 |
| Effective cycles | 1.0-3.0 range | All 3.0 (dead gates) |
| Compute gate | Opening gradually | Stuck at 0 or >0.5 too fast |
| K+B co-occurrence | Most common pair | Not visible |
| S5 pass 1 | Rises at ~15K+ | Never moves from init |
| Alarm factors | Diverge per pass | All locked at 1.0 |
| Alarm dispatch entropy | Tracked (baseline TBD) | Collapsed to 0 |

### φ-compression strata

| Stratum | Expected K/B balance |
|---------|---------------------|
| prose | K-dominant, B moderate |
| compositional | B rises (relative clauses, nesting) |
| technical | K+B balanced |
| lambda | C should activate (λ expressions, binding) |

---

## 8. File Inventory

```
scripts/v11/
├── kernel.py           # KIBC combinator enum, reduction engine, kernel functions
├── kernel_dispatch.py  # CombinatorDispatch + CombinatorIntegrate
├── config.py           # V11Config (4 combinators, no top-k)
├── model.py            # V11Model (emphasis→4, algedonic→4+1, alarm gate)
├── train.py            # Training loop (+ alarm JSONL logging)
├── probe.py            # Checkpoint diagnostics + trajectory + dispatch + alarm
├── components.py       # S4, S3, S5, S2, CycleContinue, MetaS4, AlgedonicAlert
├── ternary.py          # Ternary substrate + consensus evolution (unchanged)
├── attention.py        # StrideStack + TernaryFFN (unchanged)
└── data.py             # Data loading (unchanged)

docs/
└── v11-architecture.svg  # Visual architecture diagram
```

Self-contained. Extractable to standalone project.
