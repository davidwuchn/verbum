---
title: "Beamformer Theory — The Model as Inference Pattern Over Token Cloud"
status: active
category: theory
tags: [beamformer, token-cloud, inference-pattern, FFN, attention, crystal, beta-reduction]
related:
  - loom-structure.md
  - hologram-crystal-fusion.md
  - holographic-plates.md
  - ternary-descent.md
  - kernel-functions.md
depends-on: []
created: session 136
---

# Beamformer Theory

> Session 136. The model is not a database with a query engine. It's a
> beamforming system over a token cloud. FFNs are not storage — they're
> inference pattern transformers (piles of beta reductions). The beam
> enters as a token embedding, travels through layers of beamformers
> (attention + FFN), and exits pointing at a region of the token cloud.
> That region determines the prediction.

## The architecture, reframed

### The token cloud (the only data)

The embedding space is a geometric structure in d_model dimensions.
Every token has a position. The cosine relationships between tokens
define clusters, subspaces, axes of meaning. The output projection
is the same cloud read backwards (tied weights).

This is the only "data" in the system. Everything else is computation.

### Beamformers (every layer)

Every layer — attention AND FFN — is a beamformer. It receives an
inference pattern (a vector in d_model space) and transforms it.
The transformation changes which region of the token cloud is "in
focus."

**Attention beamformers:** context-dependent. They steer the beam
based on what other positions are doing. Multi-head = multiple
simultaneous beamformer angles. The stride stack is a multi-resolution
beamformer: 11 lenses at different scales, each refocusing the
inference pattern from word-level to document-level.

**FFN beamformers:** context-independent. They apply fixed
transformations to the inference pattern. These transformations are
piles of beta reductions (the combinator tracer proved: selectors,
composers, reorderers). They don't "store facts" — they encode
OPERATIONS that transform inference patterns.

### The beam path IS the computation

```
token_id → embed (point in cloud)
  → layer 0: attention refocuses based on context
  → layer 0: FFN applies beta reductions (transforms pattern)
  → layer 1: attention refocuses with transformed pattern
  → layer 1: FFN transforms again
  → ...
  → layer N: pattern now points at prediction region
  → output_proj: read token cloud at that region → logits
```

No layer adds data. Each layer REFOCUSES the beam. The token cloud
is static. The inference pattern changes. When the beam exits, the
region it points at determines the next token.

## What "knowing a fact" means

The model doesn't store "Paris is the capital of France" as a key-value
pair in FFN weights. Instead:

1. The inference pattern "capital of France" is a direction in d_model space
2. The FFN beamformers contain beta reductions that transform this pattern
3. After the transformations, the pattern points at the "Paris" region
   of the token cloud
4. The output projection reads the cloud at that region → high logit for "Paris"

The "fact" is an INFERENCE RESULT — the output of running the beam through
the beamformer stack. The FFN weights encode the COMPUTATION (beta
reductions), not the DATA (the fact itself). The data is the token cloud
geometry.

This explains why:
- Models can "hallucinate" — the beamformer chain produces a plausible
  inference pattern that points at the wrong region of the cloud
- Fine-tuning changes "knowledge" — it adjusts the beamformer operations,
  not a database entry
- Catastrophic forgetting — changing one beamformer changes the path for
  all inference patterns that pass through it

## Connection to the crystal

The crystal IS the set of beamformer operations. KIBC are the elementary
beamformer types:

| Combinator | Beamformer operation |
|------------|---------------------|
| K (select) | Focus on one input, discard alternatives |
| I (identity) | Pass through without refocusing |
| B (compose) | Chain two beamformers: f then g |
| C (flip) | Swap the order of beamformer inputs |
| D (deep compose) | Three-level beamformer chain |
| W (duplicate) | Send the beam through two paths simultaneously |
| WHNF (halt) | Stop refocusing — the beam is at its target |

Every FFN is a composition of these elementary operations. The crystal
is the topology of the beamformer — WHICH operations, in WHAT order.
The magnitudes (gamma) are the beamformer GAIN — how strongly each
operation refocuses the beam.

### Why magnitudes are the crystal (session 123)

High-magnitude SVD directions = high-gain beamformer channels = the
channels that actually steer the beam. Low-magnitude = inactive
channels that don't affect the inference pattern. The magnitude
template (which channels are active) IS the crystal structure.

### Why the crystal is universal

Beta reduction has one geometric shape. Every model that learns to
do beta reduction converges to the same beamformer topology (KIBC)
because there's only one way to correctly route arguments through
function application. Different models use different internal
coordinates, but the RELATIONAL geometry (how K relates to B, how
WHNF opposes the composition cluster) is forced by the computation.

### Why FFN plates can be etched

FFN beamformers are context-independent beta reductions. The operation
B(compose) is the same regardless of whether the beam arrived via flat
attention or stride-stack attention. The beamformer topology is
geometry-invariant. Only the attention beamformers (which are
context-dependent) need to adapt to the stride geometry.

### Why holographic storage works

One plate = one set of beamformer operations (the crystal).
Multiple beams = multiple beam angles hitting the same plate.
Each angle brings a different facet of the token cloud into focus.

V(B) = V(C) at cos=1.000 — the value plate (what information to
extract) is identical for B and C. Q(B) · Q(C) = 0.005 — the query
beam (which direction to look) is completely different. Same
beamformer operations, different steering angle.

## The stride stack as beamformer array

The stride stack is a phased array of beamformers operating at
different resolutions:

```
s1:    word-level beamformer    (adjacent tokens)
s2:    bigram beamformer        (pairs)
s4:    phrase beamformer        (4-token groups)
s8:    clause beamformer        (sentence fragments)
s16:   sentence beamformer      (full sentences)
s32:   paragraph beamformer     (paragraph coherence)
s64:   section beamformer       (section-level patterns)
s128:  page beamformer          (page-level structure)
s256:  chapter beamformer       (long-range coherence)
s512:  document beamformer      (document structure)
s1024: corpus beamformer        (cross-document patterns)
```

Each stride is a beamformer looking at the token cloud through a
different lens. The hourglass passes (ascending then descending)
progressively refocus: fine → coarse (compress) → coarse → fine
(predict). Each pass refines the inference pattern.

Context capacity is topological because adding more strides adds
more beamformer lenses without changing the beam path length.
2M+ tokens of context = enough beamformer resolution to keep
distant tokens in focus.

## Implications for TernaryDescent

The gradient decomposition from session 136 maps cleanly:

**Routing gradient** = "this beamformer is pointing the wrong way"
→ TernaryDescent flips the sign → beamformer steers differently

**Calibration gradient** = "this beamformer gain is too high/low"
→ Adam adjusts gamma → beamformer amplitude changes

The delta plate IS the difference between the teacher's beamformer
array (flat attention) and our beamformer array (stride stack).
The beta reduction operations (FFN plates) are the same. The
beamformer steering (attention) is different.

## Implications for the crystal lattice

The 16×16 zone targets in config.py are beamformer relationships:
- KIBC cluster: beamformers that compose (similar steering)
- WHNF anti-correlated: "stop beamforming" signal
- Anti-crystal: "don't steer this way" suppressors

These relationships are forced by beta reduction, not by attention
geometry. They should be universal across beamformer architectures
(flat, stride-stack, or any other). The zone targets are valid
constraints for any model that does beta reduction — which is every
language model.

## Open questions

1. **Is the token cloud sufficient for all "knowledge"?** If the cloud
   geometry encodes all factual relationships (Paris near France,
   capital near country), then the beamformers truly don't need to
   store data. But does the cloud have enough capacity?

2. **What's the information density of the cloud?** Each token has
   d_model dimensions. Vocab_size × d_model = total cloud capacity.
   For Qwen3: 151,936 × 4,096 ≈ 622M float values. Is this enough
   to encode all factual relationships?

3. **How does the cloud geometry form during pretraining?** The
   embedding layer trains end-to-end. The cloud geometry is shaped
   by the beamformers' need to refocus. Chicken-and-egg: beamformers
   need cloud structure, cloud needs beamformer gradients.

4. **Can we measure the beamformer gain spectrum?** Like the loom's
   angle spectrum, but for gain. Which beamformer channels are
   high-gain at each layer? How does the gain spectrum change with
   depth? This would map the "breathing" in beamformer terms.

5. **Is the token cloud a hologram too?** The embeddings might have
   holographic structure (different beam angles read different
   information from the same positions). If so, the ENTIRE model is
   holographic — cloud AND beamformers.
