---
title: Session 062 Probes — The Four Findings That Shaped v10
status: active
category: experiment-results
tags: [probes, typing, binding, composition, compressor, Qwen3-32B]
related: [basin-projector-results, compressor-architecture, identity-as-substrate]
depends-on: []
---

# Session 062 Probes

> Four probes on Qwen3-32B and the CompressorLM that established the
> design constraints for v10. Each probe answered a specific question
> about how the 32B performs compositional semantics.

## Probe 1: Type Transition Shape (L27→L28)

**Question:** Is the typing zone a discrete event at a single layer?

**Method:** Track per-token representation changes across all 64 layers
for "Every student is happy" — one context-invariant word ("Every"),
one context-dependent ("is").

**Findings:**
- All layer transitions have identical rank (~35), magnitude (~0.17),
  cosine similarity (~0.977) — no special layer
- Context-invariant words ("Every") pass through ALL 64 layers with
  0.1% change — the identity function
- Context-dependent words ("is") transform continuously at every layer
  (15-33% change per layer)

**Conclusion: Compression IS typing.** No special type layer needed.
The continuous transformation of context-dependent tokens across all
layers is the typing process. A compressor that captures this
transformation has already performed typing.

**Data:** `results/type-transition/transition_analysis.json`
**Script:** `scripts/v10/probe_type_transition.py`

## Probe 2: Parse Structure / Composition Timeline

**Question:** Does the 32B build trees? In what order does it compose?

**Method:** Logit lens on nested S-expressions, math expressions, and
prose. Track when correct outputs become decodable.

**Findings:**
- Prose resolves EARLIEST (L57-58)
- S-expressions barely resolve even at the final layer
- Math expressions resolve late
- No tree-ordered composition — everything resolves all-at-once in the
  last 5 layers
- The 32B uses superposed β-reductions across many layers, not
  sequential tree evaluation

**Conclusion: The 32B doesn't build trees. We build them instead.**
Don't try to extract a tree-building circuit — it doesn't exist. The
model uses massive parallelism across layers. A small model can't
replicate this, so we provide explicit tree structure and let the model
handle individual node computations.

**Data:** `results/parse-structure/composition_timeline.json`
**Script:** `scripts/v10/probe_parse_structure.py`

## Probe 3: Binding Structure in Residual Stream

**Question:** Can binding relationships be read from the residual stream?

**Method:** Measure cosine similarity between bound pairs (functor→argument)
vs unbound pairs at each layer for "Every student is happy."

**Findings:**
- Bound pairs have 3-4× higher cosine sim than unbound at L28
- Binding gap peaks at exactly L28 (+0.150), the typing zone
- All binding types are positive:
  - conj→noun: +0.49
  - copula→pred: +0.31
  - det→noun: +0.11
- Signal collapses to ~0 by L40 (consumed by downstream computation)

**Conclusion: Types and bindings are the same signal.** The typing zone
geometry encodes binding relationships. A parser can use cosine proximity
between compressed representations to determine what binds to what.

**Data:** `results/binding-structure/binding_analysis.json`
**Script:** `scripts/v10/probe_binding_structure.py`

## Probe 4: CompressorLM Already Has Binding + Typing

**Question:** Does the existing 16M CompressorLM preserve the 32B's
binding and typing signals?

**Method:** Run the same binding/typing analysis on CompressorLM
(iterative, W=8, strides 1/8/64) outputs.

**Findings:**
- Binding gap: +0.12 to +0.14 (80-91% of 32B's +0.15)
- "Every" within-sim: 1.000 (identical to 32B — perfect identity)
- "is" within-sim: 0.60 (vs 32B's 0.24 — present but less differentiated)
- Signal INCREASES at coarser scales (apply > parse > type)

**Conclusion: The compressor is a viable v10 starting point.** It already
preserves most of the binding signal. The strided architecture naturally
amplifies compositional signal at coarser scales, which is exactly what
tree construction needs.

**Data:** `results/compressor-binding/compressor_binding_analysis.json`
**Script:** `scripts/v10/probe_compressor_binding.py`

## Combined implications for v10

1. **No type layer needed** — compression IS typing (Probe 1)
2. **Provide explicit trees** — the 32B doesn't build them (Probe 2)
3. **Use cosine proximity for parsing** — binding = typing signal (Probe 3)
4. **Start from proven compressor** — it already has 80-91% of signal (Probe 4)

These four constraints directly produced the v10 architecture: strided
compressor → tree of VSMs → exact kernel.
