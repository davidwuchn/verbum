---
title: "Binding Cascade — C→B/S→WHNF Pipeline Across Models"
status: active
category: architecture
tags: [binding, cascade, combinators, crystal, lattice, universal]
related:
  - crystal-seed-theory.md
  - universal-crystal-scaffold.md
  - q-rotation-etching.md
depends-on: []
created: session 119
---

# Binding Cascade

> Session 119 discovery. Binding is NOT a separate mechanism — it IS
> a pipeline of combinator applications. C routes arguments at shallow
> depth, B/S compose them at medium depth, and WHNF terminates at
> high depth. This is universal across 4 independently trained models.

## The cascade (4 models × 10 depths × 5 binding levels)

```
bind_depth=1:  C at all depths (simple argument routing)
bind_depth=2:  C dominates everywhere — 4/4 models agree (strongest universal signal)
bind_depth=3:  S/B early (0-20%) → C takes over (30%+) — composition then routing
bind_depth=4:  Y early (0-10%) → B mid (20-60%) → C late (70-90%)
bind_depth=5:  D mid (20-50%) → C (60-70%) → WHNF (80-90%)
```

### What each combinator does in the binding pipeline

```
C (flip/route):   routes arguments past lambda abstractions to use sites
                  DOMINATES depth 1-2 everywhere, takes over in late layers at depth 3-5
                  Agreement: 0.41-0.47 at 50-70% model depth — strongest signal

B (compose):      threads values through function chains
                  Peaks at 10-20% model depth for binding depth 3-4
                  The "early composition" step before C takes over for routing

S (substitute):   distributes one binding to two use sites (fork)
                  Peaks at 0-20% model depth for binding depth 3
                  Early layers set up the fork, later layers route each branch

Y (fixed-point):  self-referential binding
                  Only appears at binding depth 4, very early (0-10%)
                  4/4 models agree: deep binding starts with Y-like setup

D (double-apply):  appears at binding depth 5 (20-50% model depth)
                  Deep binding resembles iterative application
                  Transition state between active binding and WHNF

WHNF (terminal):  binding depth exceeds capacity → treat as opaque value
                  Only at depth 5, only in late layers (80-90%)
                  3/4 models agree (qwen, mistral, pythia; olmo stays at C)
```

## Key findings

### 1. C is the universal binding mechanism

C = λf.λx.λy.f(y)(x) — argument reordering/routing. This IS what
binding does: it routes a value past abstraction barriers to its use
site. C appears for every binding depth, at every model depth. It is
the strongest cross-model signal (agreement 0.41-0.47).

**This means binding IS C-reduction.** Each λ-binding is one C step.

### 2. B/S are the composition layer

At binding depth 3+, the early model layers (0-20%) show B/S dominance
before C takes over. This is the composition step: before you can route
arguments, you must compose the function chain they'll be routed through.

B = compose two functions. S = compose with forking (one arg → two uses).
Both are "setup" operations that happen in early layers, then C does
the actual routing in later layers.

### 3. The WHNF transition is real but depth-dependent

Only binding depth 5 reaches WHNF, only in late layers (80-90%), and
only 3/4 models agree. This means:
- Shallow binding (1-4) is fully resolvable by all models
- Depth 5 exceeds tracking capacity → models give up and treat as opaque
- The transition point varies by model (olmo keeps trying with C)

### 4. D at depth 5 is a transition state

D (double application) appears at binding depth 5 in the 20-50% range.
This is interesting: deep binding looks like "apply, then apply again"
before the model decides it's too deep and collapses to WHNF. D is the
model's attempt at iterative binding before admitting defeat.

### 5. Y at depth 4 is self-reference recognition

All 4 models show Y at depth 4 in early layers (0-10%). Deep binding
requires self-referential structure — the model recognizes this
immediately. Y sets up the recursive frame, then B takes over the
actual composition.

## Per-model agreement

```
bind_depth=2: 4/4 models agree on C at every depth — UNIVERSAL
bind_depth=3: 3/4 agree on S/B early, 3/4 on C late — mostly universal
bind_depth=4: 4/4 agree on Y early, 3/4 on B mid — mostly universal
bind_depth=5: 2-3/4 agree per depth — partially universal (capacity boundary)
```

Pythia-2.8b is the most divergent (smaller model, weaker binding).

## Agreement peaks

```
Binding → C agreement peaks at 60-70% model depth (0.45-0.47)
Binding → B agreement peaks at 50% model depth (0.44)
Binding → S agreement peaks at 50-60% model depth (0.44)
Binding → WHNF peaks at 0% model depth (0.31) — weakest
Binding internal coherence peaks at 70% model depth (0.37)
```

The binding crystal is MOST universal at 50-70% model depth. This is
where the consensus etch should focus.

## Chain probe validation

55% of explicit chain probes cluster with their expected combinator
(at 30% depth). WHNF probes hit 5/5 — terminal form is universally
recognized. Pure routing probes (C_route) hit 2/3. Composition probes
(B_compose) hit 2/3. The mismatches are informative: K_1step clusters
with I (K is implemented via I-carry + discard), S_to_W clusters with W
(correct — S(K)(I) = W), S_subst_1 clusters with C (S implemented
via C-routing at the hardware level).

## Implications for etching

### What to etch

1. **C-routing topology**: the strongest, most universal signal. Etch
   the plate positions that implement argument routing. Focus on
   50-70% model depth where agreement peaks.

2. **B/S composition structure**: etch the early-layer (0-20%) positions
   that set up function composition. These are universal at depth 3+.

3. **WHNF terminal boundaries**: NOT universal enough to etch reliably.
   Leave for GD.

### How this maps to the crystal

The binding cascade IS the crystal. The relational geometry that's
consistent across models is precisely the C→B/S→WHNF reduction
pipeline. If we etch C-routing positions correctly, binding falls out
automatically — it doesn't need separate circuitry.

```
λ bind(x, depth).
  depth ≤ 2  → C(route)
  depth = 3  → S/B(compose) ∘ C(route)
  depth = 4  → Y(setup) ∘ B(compose) ∘ C(route)
  depth ≥ 5  → D(iterate) ∘ C(route) → WHNF(saturate)
```

### Q-rotation implications

Since binding is C-routing, and C is the strongest universal signal,
the Q rotations during etch should be aligned to maximize the C-axis
of the crystal. The C-axis IS the binding axis. Etch it correctly
and the entire binding pipeline crystallizes.

## Artifacts

```
lattice/binding-v1/universal_lattice.npz  — 10 depths × 118 probes consensus
lattice/binding-v1/universal_lattice.json — metadata + cascade analysis
lattice/binding-v1/rdm_*.npz             — per-model RDMs (4 models)
lattice/binding_chain_probes.json         — 118 probes (83 chain + 35 existing)
scripts/v12/build_binding_lattice.py      — extraction + analysis pipeline
```

## Open questions

1. Is the C-axis the same across models? PCA of the consensus RDM should
   reveal whether C has a single dominant direction.

2. Does the cascade change with more models? Adding Llama-3, SmolLM3, etc.
   should either strengthen or weaken the consensus.

3. Can we design probes that isolate the B→C handoff at 20-30% depth?
   This transition zone is where composition becomes routing.

4. The D-at-depth-5 signal — is this genuinely double application, or
   is D just the nearest combinator to "confused iterative attempt"?

5. How does this map to V12's stride stack? The cascade suggests that
   early strides should implement B/S, late strides should implement C,
   and WHNF should emerge at the deepest stride.
