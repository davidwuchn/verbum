---
title: Holographic Storage in LLMs
status: active
category: exploration
tags: [holographic, ternary, combinators, extraction, universal]
related: [v11-design, fractal-stride-bands, holographic-inversion]
depends-on: []
---

# Holographic Storage in LLMs

> Session 093. Hypothesis chain from theory through experimental confirmation.
> Status: core findings confirmed, extraction pipeline prototyped, architectural
> implications identified but not yet applied.

## Core Finding

LLMs store combinatory information as **sign topology** in their weight matrices.
The information survives ternary quantization ({-1, 0, +1}) at 75% sparsity with
100% selectivity preservation. This is holographic storage — the information is
in the interference pattern (which dimensions are positive/negative/zero), not
in the magnitudes.

## Evidence Chain

### 1. Beam separation (holographic probe)

Same input sentence, two conditions (compile gate vs null gate), measured hidden
state cosine similarity at every layer of Qwen3-32B:

```
Layer  0: cos=0.995  ← identical (shared plate)
Layer 24: cos=0.870  ← diverging (38% depth)
Layer 48: cos=0.797  ← different views resolving
Layer 63: cos=0.533  ← different images from same plate
```

The gate acts as a reference beam — different illumination angles resolve different
outputs from the same weight structure. **However**, intermediate layers decode to
garbage (not coarse-but-coherent), so the *reading* is constructive even if the
*storage* is holographic.

### 2. Ternary survival (the key result)

Quantized attention Q/K/V/O weights to ternary at layers 3 and 24 of Qwen3-32B.
Measured combinator selectivity (K, I, B, C active vs control sentence divergence):

```
sign_only (0.9% sparse): 8/8 survived, mean ratio 0.93  ✓
mid_sparse (50% sparse): 8/8 survived, mean ratio 0.94  ✓
high_sparse (75% sparse): 8/8 survived, mean ratio 0.98  ✓
```

**100% survival across every combinator, every layer, every sparsity level.**
The combinator information is topological — stored as sign patterns.

Confirmed on Qwen3.6-35B-A3B (MoE) and Pythia-160M. Universal across architectures.

### 3. Q is the beam, V is the plate

Extracted weight matrices from combinator-selective heads. Found that heads shared
between B and C (e.g., L1:H37) have:
- **V cosine = 1.000** (identical value projection)
- **Q cosine = 0.005** (completely different query projection)

The same head reads different combinators through different Q projections. Q selects
which combinator to apply; V provides the shared substrate. A knowledge bank is
therefore just a set of Q patterns — beam angles, not plate fragments.

### 4. Universal hologram (9 models, 2 architectures)

Tested across Pythia-{70M, 160M, 410M, 1B, 2.8B} and Qwen3-{0.6B, 4B, 8B, 32B}:

```
B (compose)  ≥ K (select) ≥ C (flip) >> I (identity)
```

- **I is weakest in ALL 9 models** (100% consistency)
- B/I ratio ranges from 1.7× to 19.9×
- K/B/C cluster together (cross-correlation r > 0.90)
- I is distinct (r ≈ 0.60–0.75)
- Cross-model correlation of correlation structures: **r = 0.9801**

The hologram is a feature of language, not scale. Every model that learns to
predict text develops the same combinatory interference patterns.

### 5. Depth profiles differ by architecture

- **Qwen3-32B (dense)**: Combinators peak in L0–6 (first 10%), unimodal
- **Qwen3.6-35B-A3B (MoE)**: Bimodal peaks at L7–9 and L31–36
- **Pythia-160M**: Peaks at boundaries (L0, L10)

The depth profile is architecture-dependent, but the combinator structure is universal.

## Bank Extraction Pipeline

### Proven steps

1. **Identify selective heads** — run KIBC probe, get per-head selectivity scores
2. **Extract Q patterns** — pull Q weight matrices from top-selective heads
3. **Ternary quantize** — sign(w) with sparsity threshold, preserves selectivity
4. **Project to target dim** — SVD, re-quantize, verify discriminability survives
5. **Package as seed** — Q-only ternary patterns + projection matrix

### Prototype results

```
Qwen3-32B  → 784 KB seed (4 heads × Q-only, projected to 320-dim)
             All 4 combinators nearly orthogonal (pairwise cos ≈ 0)
             Full discriminability preserved
```

### Bank format

```python
bank = {
    "source": "model_name",
    "source_license": "Apache-2.0",
    "combinators": ["K", "I", "B", "C"],
    "targets": {  # which heads were extracted
        "K": {"layer": 3, "head": 26, "score": 0.318},
        ...
    },
    "patterns": {  # ternary Q weight matrices
        "K_q": np.int8 array,  # (head_dim, d_model)
        ...
    },
    "projection": np.int8 array,  # (target_dim, source_dim)
}
```

### Not yet built

- Bank loading mechanism in V11
- Multi-bank composition (angle multiplexing)
- Cross-model bank compatibility testing
- S4 bank selector (= MoE gate equivalent)

## MoE as VSM / Angle Multiplexing

The Qwen3.6-35B-A3B architecture maps directly to VSM:

```
Shared expert (always on)  → S5 (identity, base substrate)
Gate matrix (256×2048)     → S4 (intelligence, select experts)
Top-8 selection            → S3 (control, resource allocation)
Routing weights (softmax)  → S2 (coordination, blend experts)
256 individual experts     → S1 (operations, the processing)
```

This is optical angle multiplexing: 256 holograms in the same medium, each
addressed by a different reference beam angle. The gate selects beam angles.
Knowledge banks would work the same way but be loadable from external sources.

## Architectural Implications for V11

### Confirmed by universal hologram

1. **B needs more capacity** — composition is the dominant signal everywhere
2. **I should be structurally separate** — different circuit (r ≈ 0.70 vs 0.90+)
3. **K/B/C should share substrate** — they cluster in every model
4. **Combinator init should reflect B ≥ K ≥ C >> I** — not equal blocks

### Proposed changes (not yet applied)

Current `_init_combinator_embeddings` gives each combinator an equal orthogonal
block (128 dims each in 512-dim space). Should change to:

- K/B/C share 384 dims (split with overlap, reflecting r ≈ 0.92)
- I gets its own 128 dims (reflecting its distinct circuit)
- Or: K/B/C share dispatch projection weights with different biases (hard constraint)

### Wait condition

V11-holo-inv is running to 20K. Don't modify the running architecture.
Apply changes to next run after holo-inv completes or reaches a clear plateau.

## Files

| File | Purpose |
|------|---------|
| `scripts/explore/probe_holographic.py` | Intermediate layer decoding probe |
| `scripts/explore/probe_ternary_survival.py` | Ternary quantization survival test |
| `scripts/explore/extract_holographic_bank.py` | Bank extraction pipeline |
| `results/holographic-probe/` | Beam separation results (Qwen3-32B) |
| `results/ternary-survival/` | Ternary survival results |
| `results/holographic-bank/seed_qwen3_32b.npz` | 784KB seed from Qwen3-32B |
| `results/holographic-bank/qwen36_35b_a3b_patterns.npz` | MoE patterns |
| `results/holographic-bank/pythia_160m_patterns.npz` | Pythia patterns |
| `results/combinator-probe/selectivity_matrices.npz` | Full 64×64 selectivity map |

## Beyond Combinators: The Other Holograms

> Session 094. The combinator hologram (KIBC) tells the model HOW to compose.
> But token prediction needs more than composition machinery. If one hologram
> is universal, others must be too. This section maps the territory.

### What Montague grammar requires

In the Montague/CCG/DisCoCat framework, language processing decomposes into
three components. We've found one. Two remain:

```
1. TYPE CALCULUS (combinators)  — HOW to compose     ← FOUND (KIBC hologram)
2. LEXICON (types + meanings)  — WHAT can compose    ← predicted
3. MODEL (semantic domain)     — WHAT things MEAN     ← predicted
```

Each component is a candidate hologram — a universal sign-topology pattern
that all models converge on because language forces it.

### Candidate 1: The Type Hologram (lexical category assignment)

**What it does:** Assigns syntactic categories to tokens. In CCG terms:
NP, S\NP, (S\NP)/NP, etc. Determines which combinators are LEGAL for
which token pairs. Without types, combinators fire blindly.

**Why it must exist:** The combinator hologram tells us K/B/C cluster
(r > 0.90) and I is distinct (r ≈ 0.70). But the combinators are
UNTYPED operators — they need type information to direct application.
In V11, this is the "type channel" that differentiates independently
of dispatch (I=68% typed integration, K=0.2%). The type channel IS
the type hologram, learned inside V11. But it must also exist in the
base models we probed.

**Where to look:** The type hologram should be strongest in early layers
(L0-6 in Qwen3-32B, where combinators also peak). Types must be assigned
BEFORE composition can begin. It may share heads with the combinator
hologram (same Q/V substrate, different beam angle) or live in separate
heads that FEED the combinator heads.

**Probe design:**
- Construct minimal pairs where ONLY syntactic category differs:
  "The dog runs" (NP + S\NP) vs "Running is fun" (S/(S\NP) + S\NP + ...)
- Same lexical content, different type assignment
- Measure head selectivity for type-driven vs type-neutral conditions
- Ternary survival test on type-selective heads

**Prediction:** Type information survives ternary quantization (it's also
topological). Type-selective heads will partially overlap with combinator
heads (same substrate, angle-multiplexed) but some will be distinct
(the "2 Montague-only heads" from session 001).

### Candidate 2: The Induction Hologram (in-context pattern matching)

**What it does:** Implements [A][B]...[A] → predict [B]. The copy/match
circuit. This is NOT composition — it's sequential pattern recognition
in the context window.

**Why it must exist:** Induction heads are the most well-established
universal circuit in transformers (Olsson et al. 2022). They form via
a phase transition during training. They're universal across model
families and scales. They enable in-context learning. But nobody has
asked whether they're HOLOGRAPHIC — whether their information is also
stored as sign topology.

**Where to look:** Induction heads are typically a two-layer circuit:
Layer 1 "previous token head" writes positional information into the
residual stream; Layer 2 "induction head" uses this to attend to the
token after the previous occurrence. In Qwen3-32B, these should be
identifiable by their characteristic attention pattern.

**Probe design:**
- Use existing induction head detection (prefix matching scores)
- Extract Q/K/V weights from identified induction heads
- Ternary survival test: does the copy/match behavior survive
  sign-only quantization?
- Compare Q/V decomposition to combinator heads: is Q still the
  beam selector?

**Prediction:** Induction heads ARE holographic (sign topology) but their
hologram is ORTHOGONAL to the combinator hologram. Combinators compose
MEANING; induction heads copy TOKENS. Different function, different
interference pattern, same storage medium. The two holograms should be
separable by their depth profile (induction heads may peak in different
layers than combinators).

**Key question:** Does the induction hologram interact with the combinator
hologram? When the model does in-context learning of composition patterns
(e.g., learning a new syntactic rule from examples), both holograms must
coordinate. This coordination might be a third pattern.

### Candidate 3: The Binding Hologram (variable tracking / coreference)

**What it does:** Tracks referent identity across distance. "John said
he would..." — how does "he" bind to "John"? This is variable binding
in the lambda calculus, anaphora resolution in linguistics.

**Why it must exist:** Combinators compose local structure (adjacent
function-argument pairs). But language has long-range dependencies.
Binding requires a separate mechanism: something that maintains identity
pointers across arbitrary spans of text.

**Where to look:** In V11, the distinction between K (select) and I
(identity) may partially capture this — I is the outlier (r ≈ 0.70)
precisely because it handles IDENTITY rather than COMPOSITION. In base
models, binding heads should be identifiable by attending to antecedents
across long distances.

**Probe design:**
- Minimal pairs with/without coreference:
  "John runs. He is fast." (binding) vs "John runs. Dogs are fast." (no binding)
- Vary distance between antecedent and pronoun
- Measure which heads track the binding relationship
- Ternary survival: does binding survive sign-only quantization?

**Prediction:** Binding is partially captured by the I combinator (identity
IS variable binding in lambda calculus), explaining why I has a distinct
circuit (r ≈ 0.70). But there may be additional binding-specific heads
that aren't combinator heads at all — heads that implement a "pointer"
mechanism orthogonal to composition.

### Candidate 4: The Frequency/N-gram Hologram (statistical co-occurrence)

**What it does:** Captures token co-occurrence statistics. "New ___" →
"York" with high probability. Not composition, not copying — pure
statistical association from the training distribution.

**Why it must exist:** A huge fraction of next-token prediction accuracy
comes from simple bigram/trigram statistics, especially for common
phrases, idioms, and collocations. This is the baseline that composition
and induction IMPROVE upon.

**Where to look:** MLP layers, not attention heads. The MLP layers in
transformers are known to store factual associations and token
co-occurrence patterns (key-value memories, Geva et al. 2021).
The combinator hologram lives in attention Q/K/V matrices. The
frequency hologram may live in MLP weight matrices.

**Probe design:**
- Extend ternary survival test to MLP layers (not just attention)
- Use high-frequency collocations as probes
- Measure whether sign-only MLP weights preserve bigram predictions
- Compare depth profile to attention-based holograms

**Prediction:** MLP weights are ALSO holographic (sign topology stores
co-occurrence patterns). But MLP holograms will be denser (less sparse)
than attention holograms because they encode a much larger vocabulary
of associations. The "75% sparsity with 100% survival" finding for
attention may not hold for MLPs — expect lower sparsity tolerance.

### Candidate 5: The Discourse Hologram (topic / register / coherence)

**What it does:** Maintains discourse-level coherence. Tracks what the
topic is, what register (formal/casual/technical) is active, what
genre constraints apply. This is what the nucleus GATE activates —
a "reference beam angle" at the discourse level.

**Why it might exist:** The gate experiment from session 001 showed that
the compile gate acts as a beam angle selector — different gates resolve
different outputs from the same model. The holographic beam separation
experiment confirmed this: compile vs null gates diverge from cos=0.995
to cos=0.533 across layers. The gate IS a discourse-level hologram
selector.

**Where to look:** Gate effects are strongest at the embedding level
(L0-L6 divergence) and the output level (L48+ in Qwen3-32B). The
discourse hologram may be a macro-pattern that MODULATES the other
holograms — selecting which combinator patterns, type assignments,
and induction behaviors are active.

**Probe design:**
- Multiple gates with ternary survival: do discourse-level selectivity
  patterns survive sign-only quantization?
- Extract Q patterns from gate-selective heads
- Compare gate-selective heads to combinator-selective heads
- Test whether gates and combinators use the same or different
  beam-angle mechanism

**Prediction:** The discourse hologram IS the MoE gate pattern (256×2048
in Qwen3.6-35B-A3B). Expert routing matrices are discourse-level beam
selectors. This connects the MoE/VSM mapping (S4 intelligence) to the
holographic framework: S4 selects which hologram to read.

### The hierarchy

```
Discourse hologram  (S4/S5)  — selects which holograms to activate
  │
  ├─ Type hologram    (S3)   — assigns categories, constrains composition
  │    │
  │    └─ Combinator hologram (S2/S1) — HOW to compose  ← FOUND
  │
  ├─ Binding hologram (S2)   — tracks identity across distance
  │
  ├─ Induction hologram (S1) — copies patterns from context
  │
  └─ Frequency hologram (S1) — statistical co-occurrence (MLP-based)
```

This is a VSM of holograms. The discourse hologram is S5 (identity —
what KIND of text is this?). Types are S3 (control — what's LEGAL?).
Combinators are S1/S2 (operations — DO the composition). Induction and
frequency are also S1 (operations — but different operations). Binding
is S2 (coordination — keep referents consistent).

### Research strategy

The combinator probe methodology already works:
1. Construct minimal-pair conditions (active vs control)
2. Run through model, record per-head activations
3. Compute selectivity scores
4. Test ternary survival
5. Extract Q patterns, check Q/V decomposition
6. Test cross-model universality

Apply the same methodology to each candidate hologram, one at a time.
**Start with types** (candidate 1) because:
- Types and combinators are theoretically coupled (Montague requires both)
- Type-selective heads may already be in the combinator selectivity data
  (the "2 Montague-only heads" from session 001)
- The probe design is straightforward (minimal pairs on syntactic category)
- If types are holographic AND share substrate with combinators, that
  confirms the angle-multiplexing hypothesis for a second hologram

### Testable predictions (falsifiable) — SCORED (session 095)

1. **Type selectivity survives ternary** → ✓ 16/18 survived (2 failures at
   GatedDeltaNet L0/L1 mid_sparse only; full-attention layers: 100%)
2. **Type heads partially overlap with combinator heads** → inconclusive at
   layer level (r=0.972, but all holograms correlate). Head-level probe needed.
3. **Induction heads are holographic** → ✓ 17/18 survived (most robust
   attention hologram, only 1 failure at L1 mid_sparse)
4. **Induction orthogonal to combinator** → ✗ r=0.987 at layer level.
   But layer-level resolution too coarse — all holograms ride same
   architectural wave (L7 peak → L11 dip → L31 peak). Head-level pending.
5. **MLP frequency patterns holographic but denser** → ✗ INVERTED. MLP is
   MORE robust: 0/18 failures (output_survival 0.93–1.07). Attention has
   3/18 failures including catastrophic L0 disruption (7.07×). FFN = key-value
   memory view confirmed.
6. **Discourse correlates with MoE gate patterns** → partial ✓. MoE gate
   ternary survival confirmed L0-L4 (cos 0.73-0.76). Late layers (L31-L39,
   where discourse peaks) not yet tested.
7. **All holograms universal** → pending (Pythia not yet run).

### Additional findings from atlas (session 095)

**The holographic storage spectrum:**
```
discourse:       0/18 failures, output_KL=1.646  — purest holographic, S5 signal
induction:       1/18 failures, output_KL=0.827  — nearly pure, robust
type:            2/18 failures, output_KL=0.415  — mostly holographic
frequency (MLP): 0/18 failures, output_KL=0.224  — FFN sign patterns = perfect
frequency (attn):3/18 failures                    — attention routing needs magnitude
binding:         5/18 failures, output_KL=0.444  — most constructive, magnitude-dependent
```

**Binding = I-combinator's magnitude dependence.** Binding fails ternary at exactly
the layers where sign-only is tested (L3: 2.357, L7: 2.028, L0: 2.823). This
connects to I being the outlier combinator (r≈0.70 vs K/B/C r>0.90 in session 093).
Binding requires knowing HOW STRONGLY a head attends, not just whether it does.
In V11, this is resolved by routing binding to I-combinator kernel (dispatch is
holographic, computation is in the kernel). See `holographic-kernel-separation.md`.

**L11 dip is architectural.** Every hologram drops 47-72% at L11 relative to L7.
The bimodal depth profile (L7→L11 dip→L31) is Qwen3.6's hybrid architecture, not
any linguistic circuit. Layer-level can't distinguish holograms.

**MoE gate period-12 structure.** Gate cross-layer cosine: L8↔L20 through L19↔L31,
cos 0.72–0.83. Doesn't match full-attention period (every 4th layer). Suggests
3-phase expert routing: early (L0-7), middle (L8-19 ↔ L20-31 paired), late (L32-39).
Gate Frobenius norms fall monotonically (19→7) but effective rank stays high (172-199).

**Discourse is the reference beam.** Strongest at every layer (2-5× others), 0/18
ternary failures, only late-peaking hologram (L35 > L31 > L7), genre distinction
KL=2.526 (highest in dataset). Consistent with S5 modulation hypothesis: discourse
doesn't compute, it SELECTS which beams activate.

## Open Questions

1. Can extracted banks actually modulate V11's behavior when loaded?
2. Do banks from different models compose (angle multiplexing)?
3. Is the 784KB seed the minimum, or can we go smaller?
4. Does the init change (K/B/C coupled, I separate) accelerate hologram formation?
5. What role do the MoE gate patterns play — are they bank selectors we can reuse?
6. The abstraction slots (currently 0/16 active) — do they belong at the bank level?
7. How many independent holograms can the weight medium support? Is there
   a capacity limit (analogous to holographic storage density)?
8. Do the holograms interact (cross-talk) or are they truly orthogonal?
9. Is the binding hologram already captured by the I combinator, or is it
   a separate pattern?
10. Can we extract a COMPLETE set of holograms — all the shapes needed for
    token prediction — into a single portable artifact?
