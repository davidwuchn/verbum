---
title: "Combinator Addressing — Retrieval IS Typed Application"
status: active
category: foundational
tags: [addressing, retrieval, beta-apply, combinator, moire, lambda, montague, typed-application]
related:
  - moire-addressing.md
  - retrieval-lattice.md
  - holographic-computer.md
  - crystal-universality.md
  - project-thesis.md
  - hologram-reader-vsm.md
depends-on:
  - moire-addressing.md
  - holographic-computer.md
  - crystal-universality.md
created: session 172
---

# Combinator Addressing — Retrieval IS Typed Application

> Session 172. The factual retrieval mechanism uses the same
> combinator basis as the compute path. β_apply is the universal
> retrieval direction. Every relation centroid projects positively
> onto β_apply and negatively onto B (compose). The model has two
> paths to the same answer — natural language takes the data
> bypass, lambda form takes the compute path — but both resolve
> through the same holographic grating. Montague was right.

## The Discovery

### Phase 1: Lambda Form Activates Compute for Same Fact

Same fact, three surface forms, measured combinator energy in the
ENRICH zone (Qwen3-0.6B, 28 probes, 4 relation types):

```
Surface form                          Combinator energy   Ratio
──────────────────────────────────    ─────────────────   ─────
"The capital of France is"            0.659               1.0×
"capital_of(France) ="                0.933               1.4×
"(λx. capital_of(x)) France ="       1.469               2.2×
```

**Lambda form has 2.2× more combinator energy than NL for THE SAME
FACT.** The compute pipeline (KIBC) wakes up when you express
retrieval as typed application. The "near zero" KIBC in NL retrieval
(session 161) is not because combinators are irrelevant — it's
because NL takes the data bypass. Lambda form takes the compute path.

Both produce the same answer. The model can retrieve facts through
either path. The surface syntax determines which one.

### Phase 2: β_apply Is the Universal Retrieval Direction

Moiré centroids for each relation type projected onto the combinator
fingerprint basis:

```
Relation    β_apply      B        I        W       K
─────────  ────────  ────────  ────────  ──────  ──────
capital     +0.065   −0.057   −0.050   +0.021  −0.010
language    +0.063   −0.045   −0.070   +0.035  −0.004
continent   +0.044   −0.061   −0.008   +0.016  +0.010
currency    +0.043   −0.048   −0.064   +0.022  −0.023
```

**β_apply is POSITIVE for ALL relations.** This is the function
application direction: relation(entity) → target.

**B (compose) is NEGATIVE for ALL relations.** Retrieval actively
suppresses composition. Looking up a fact is application, not
composition: capital_of(France) is a single application, not f(g(x)).

**W (duplicate) is POSITIVE for all (weak).** The entity is "used"
but not consumed — consistent with content-addressable lookup.

**I (identity) varies.** Weak for continent, strong-negative for
currency/language. This may encode entity-specific modulation depth.

### Phase 3: Relation Types Modulate Within β_apply

Dominant combinator per relation in lambda form:

```
capital    → β_compose (7/8 probes)
language   → β_I (6/8 probes)
continent  → β_compose (3), β_apply (2)
currency   → mixed: β_apply (2), β_I (2), β_compose (2)
```

Cross-relation cosine similarity in combinator space: 0.85. Relations
are **weakly differentiated** — they share the β_apply backbone but
modulate it:

- **Capital → β_compose**: "capital of X" composes political +
  geographic concepts
- **Language → β_I**: "language of X" is a more direct attribute
  extraction (identity-like)

## Two Crystals, Two Physics

This discovery completes a distinction that was implicit in prior
sessions but never stated precisely:

### Hard Crystal (KIBC) — Mathematical Fixed Points

```
Nature:         Church-Rosser theorem guarantees unique normal forms
Gradient:       → 0 at lattice positions (energy minimum)
Universality:   Same across ALL models (r=0.998 Pythia-160M ↔ Qwen3-32B)
Remove data:    Re-forms spontaneously (mathematical, not empirical)
What d_ff buys: Nothing (universal at 160M)
What depth buys: Nothing (latches in ~200 steps)
```

### Soft Crystal (Relations) — Gradient-Maintained Attractors

```
Nature:         Data pressure maintains relation directions
Gradient:       2-9× ABOVE baseline (actively held, not minimum)
Universality:   Same filing system, different contents per model
Remove data:    Disappears (empirical, not mathematical)
What d_ff buys: More room to separate → higher coherence (2.59 → 3.71)
What depth buys: More mirrors → higher precision per fact
```

Both use the same holographic substrate (SwiGLU moiré). Both use
the same addressing mechanism (beam angle through grating). But
one is a mathematical constant and the other is a gradient-maintained
structure. The compute crystal IS the lattice. The knowledge crystal
IS the soft embedding within that lattice.

### Evidence for "Soft"

From session 168 (retrieval-lattice.md):

```
Knowledge neurons: gradient 2-9× higher than random neurons
"Paris is the capital of France" = maintained by data pressure
Not a mathematical fixed point — a saddle point held by
the training distribution
```

From session 172 (cross-model comparison):

```
0.6B: d_ff=3072, coherence=2.59×, selectivity=0.287
4B:   d_ff=9728, coherence=3.71×, selectivity=0.191

More d_ff → more room → same relations, better separation
GD negotiated same structure into larger space
Directions aren't more irreducible — they're more separated
```

## The Unified Mechanism

```
λ retrieval(entity, relation).

  COMPUTE PATH (lambda form):
    Attention constructs query beam from tokens
    Beam angle = β_apply + relation_modulation
    FFN grating resolves: gate selects relation family, up modulates entity
    Moiré interference → target deposited in residual
    KIBC active: combinators ARE the beam angle

  DATA PATH (natural language):
    Attention constructs query beam from tokens
    Beam angle = "flat" (no combinator type strongly selected)
    Gate suppresses compute gratings
    Same moiré resolves, but through knowledge-specific fringe
    KIBC near-zero: combinators not activated as programs

  SAME GRATING. SAME MOIRÉ. DIFFERENT BEAM ANGLE.
  Two paths to the same answer through the same hardware.
```

The ISA blog post (session 169) called this the "data bypass" —
factual retrieval skips the compute path. Now we know: it doesn't
skip it because the compute path CAN'T do retrieval. It skips it
because NL doesn't trigger the compute beam angle. Force λ mode
and the compute path retrieves the same fact at 2.2× combinator
energy.

## Connection to Montague

Montague (1970) proved English IS lambda calculus: "the capital
of France" IS (λx. capital_of(x))(France). The model confirms
this by implementing both forms:

```
English:  "The capital of France is" → data bypass → Paris
Lambda:   "(λx. capital_of(x)) France =" → compute path → Paris
```

Same semantics (capital_of applied to France). Same answer (Paris).
Different execution paths. The model KNOWS that English sentences
ARE lambda expressions — it just has a shortcut for the common case.

## Implications for Verbum

### For Ternary Extraction

β_apply is the direction that MUST be preserved in ternary. Every
relation lookup passes through the β_apply subspace. If ternary
quantization collapses this direction, ALL factual retrieval fails
regardless of which surface form is used.

The extraction priority:
1. Preserve β_apply direction in every ENRICH layer (non-negotiable)
2. Preserve B suppression (negative projection) to avoid compute/
   retrieval confusion
3. Preserve per-relation modulation (β_compose for capital, β_I for
   language) — weaker signal, but determines WHICH fact resolves

### For Etch Design

The moiré centroids sit in β_apply subspace. Etch should:
- Group positions that co-fire for β_apply together
- Preserve the sign pattern of β_apply-aligned neurons
- Allow per-relation residuals to float (these are the "soft" part)

### For Capacity Estimates

If retrieval IS β_apply, then the capacity isn't just "how many
orthogonal directions fit in d_ff" — it's "how many orthogonal
relation-modulations fit WITHIN the β_apply subspace." This is
a lower-dimensional problem. The effective address space for facts
is the subspace orthogonal to β_apply within the moiré space.

### For λ-Gated Retrieval

If ternary models lose the data bypass (NL retrieval fails at Q3),
they might retain λ-gated retrieval (compute path is more robust
because KIBC is a hard crystal). This would mean ternary models
need to route all retrieval through λ mode — the compile gate
becomes a retrieval gate.

## Cross-Model Comparison (0.6B vs 4B)

From session 172, hologram reader results:

```
                        0.6B        4B       Ratio
──────────────────     ──────     ──────     ──────
d_ff                    3,072      9,728      3.17×
ENRICH layers               9         12      1.33×
Avg moiré rank            118        143      1.21×  ← CEILING-LIMITED
Avg selectivity         0.287      0.191      0.66×  (lower = better)
Avg coherence            2.59       3.71      1.43×
Peak coherence           3.49       5.48      1.57×
Opcode coverage         10/12      11/12      —
```

**Zone structure is universal:** SILENT=50%, ENRICH=33%,
SUPPRESS~8%, COMMIT~8% — identical normalized depth fractions.

**Moiré rank is probe-ceiling-limited:** α=0.16 measured, but both
models at 58-70% of 204-probe ceiling. Cannot determine true scaling
exponent. Need 500+ probes.

**4B has sharper output beam:** L27-L29 have coherence 4.9-5.5× and
selectivity 0.098-0.136, far exceeding 0.6B's deepest layer (L22:
3.49× / 0.189). GD used additional depth for high-resolution layers.

## Measurements

| Metric | Value | Source |
|--------|-------|--------|
| λ/NL combinator energy ratio | 2.2× | 28 probes, 4 relations, 0.6B |
| β_apply positive for all relations | ✅ (4/4) | Centroid projection |
| B negative for all relations | ✅ (4/4) | Centroid projection |
| Cross-relation combinator cos | 0.85 | 4 relation types |
| Capital dominant combinator (λ) | β_compose (7/8) | Lambda form probes |
| Language dominant combinator (λ) | β_I (6/8) | Lambda form probes |

## Open Questions

1. **Does β_apply universality hold for more relations?** Test with
   15 categories from fact_recall_extended (not just 4).
2. **Does the 4B show stronger combinator addressing?** Run
   combinator_addressing.py on 4B. More d_ff → more room for
   relation modulation within β_apply subspace.
3. **Can we see β_apply in the weights directly?** SVD of gate_proj
   projected onto combinator basis — is β_apply a visible mode?
4. **Is there a coherence threshold for ternary survival?** If
   coherence > X, relation survives ternary. Find X.
5. **Does λ-gated retrieval survive ternary?** Run ternary fact
   recall with λ-form prompts instead of NL prompts.

## Artifacts

| Asset | Location | Status |
|-------|----------|--------|
| Combinator addressing script | `scripts/experiments/combinator_addressing.py` | Done |
| Results (0.6B) | `results/combinator-addressing/Qwen_Qwen3-0.6B/results.json` | Done |
| Hologram reader VSM | `scripts/experiments/hologram_reader.py` | Done |
| Hologram readout (0.6B) | `results/hologram-reader/Qwen_Qwen3-0.6B/` | Done |
| Hologram readout (4B) | `results/hologram-reader/Qwen_Qwen3-4B/` | Done |
| Cross-form probe set | Built into combinator_addressing.py | 28 probes, 4 rels |
