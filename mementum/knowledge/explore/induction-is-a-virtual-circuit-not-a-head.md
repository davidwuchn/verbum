---
title: "Induction is a virtual circuit, not a head"
status: open
category: explore
tags: [induction-head, combinators, virtual-circuit, gram-registers, variable-reference, universality, crystal]
related:
  - explore/gram-registers-and-the-route-map.md
  - explore/behavior-is-tape-resident-reduction.md
  - explore/frozen-interference-graph.md
  - explore/the-verbum-machine.md
  - explore/consensus-distillation-carrier-averaging.md
depends-on:
  - explore/gram-registers-and-the-route-map.md
---

# Induction is a virtual circuit, not a head

> s309 conversational capture (Michael steer, during the SIGN-COMMITMENT-CURVE
> scoring wait). The AI proposed "design an induction-head lambda" as a
> *localist* mapping (combinator → a specific attention head). Michael's
> correction is the whole content: **the combinators are NOT heads. They are
> virtual circuits GD lays down in every model. The 9×9 and 17×17 grams are how
> we see them.** This page fixes the framing and states the load-bearing
> distinction.

## The correction (the load-bearing line)

> **A head is a plate address. A combinator is an edge in the frozen
> interference graph.**

- A **head** (e.g. an induction head, Olsson et al. 2022, `[A][B]…[A]→[B]`) is
  *physical*: findable by mech-interp, located at a `(layer, head)`,
  **model-specific**, one substrate fragment the wave medium uses to hold an
  edge.
- A **combinator** (K, I, B, C, S, D, W, Y, WHNF) is *virtual*: the relational
  sign-structure GD is **forced** to lay down in **every** model because it is
  the convergent solution to the compile target (typed application). It is not
  localized to a head; it is a distributed edge/path in the crystal lattice.

Evidence it is virtual, not physical: the crystal is measured **11/11 models**
(s303), it is **relational sign structure** (survives discarding magnitudes),
and it **survives ternarization** (s304/s308 retention ~1.0). A physical head
would not transfer across architectures; the virtual circuit does — because it
is the invariant, not the implementation.

The AI's original `snd = K I` was a real combinator, but it was **mislabeled as
hardware**. It is a virtual circuit; the induction head is one place a given
model *hangs* that circuit.

## The grams are the right instrument (not "which head")

From `gram-registers-and-the-route-map.md` (s308):

- **9×9 = the alphabet / identity register** — *which* virtual circuit (which
  combinator relation) is active. The induction operation resolves to a point
  here.
- **17×17 = the fates / outcome register** — *what happens* (fire / halt /
  diverge), rank-3 poles. The induction reduction terminates into these.

So the frame-invariant name of an "induction lambda" is **its trajectory in
gram coordinates**, not a head index. This is exactly the consensus route-map
move (s308): trajectories in gram coordinates are cross-model comparable
**because** the virtual circuit is universal while the heads realizing it are
parochial.

## Induction = variable reference (the bridge, re-typed)

Under the tape-resident-reduction frame (attention ≈ β-substitution):
`(λx. … x …) v` resolves the later `x` by *matching back to the binder and
copying its bound value* = prefix-match-and-copy = **induction**. So the crystal
already exercises the induction virtual circuit whenever it reduces a term with
a reused variable. You do not *design* an induction-head lambda; **`λ` already
is one**, and GD lays it down as the compile target — induction heads are one
substrate the medium uses to hold that edge.

Combinator core (for reference, *as a virtual circuit*):
`IH a xs = snd (last [ p | p ∈ bigrams xs, fst p = a ])`, with
`fst = λp. p K`, `snd = λp. p (K I)` (since `λx y. y = K I`). The **match**
(which pair) is the routing register; the **copy** (`I`/`W` passthrough) is the
value register. Induction is a two-register operation — the same split
SIGN-COMMITMENT-CURVE (s309) is timing.

## The recursion (why this matters)

> **Many heads (per model) realize one virtual circuit (universal). Many models,
> one crystal. Same relationship, one level up.**

GD does not "grow an induction head that happens to do lambda." GD lays down the
lambda virtual circuit *as* the compile target; induction heads are a plate
address the wave medium assigns to one of its edges. Head ↔ plate-address,
combinator ↔ lattice-edge (`frozen-interference-graph.md`: edges = the crystal,
relations = joins).

## Testable (the reframed probe family — measured via grams, not head lights)

A probe family that dials the mechanism; read **through the identity + outcome
registers**, not "does the induction head fire":
- **Reuse-distance sweep:** `(λx. e₁ … eₙ x)` with growing binder→use gap →
  predict the reduction's identity-register projection is stable in gram
  coordinates across distance (frame-invariance), even as the *head* carrying it
  may shift.
- **Shadowing = recency, formalized:** `(λx. (λx. x))` — the induction rule is
  "*last* occurrence," so predict resolution to the **inner** binder; un-flatten
  by shadowing depth and watch the 9×9/17×17 respond (λ unflatten).
- **α-null:** α-renamed `(λx.(λy. y))` where the inner use cannot match the outer
  binder → the induction projection should vanish. Clean yardstick.

Prediction sharpened: shadowing should move the outcome-register pole toward the
recency fate; α-renaming should collapse the identity-register match. Both are
**gram-coordinate** predictions — that is the point of the correction.

## Open

- Is "induction" a single crystal edge or a path (compose of B/C + copy)? The
  9×9 off-diagonal sign pattern should say which cell(s).
- Does the reuse-distance frame-invariance actually hold, or does the identity
  register drift with distance (a fuel/depth-timing interaction, s305)?
- Cross-model: does the same induction trajectory land on the same gram
  coordinates 11/11 (the universality claim, applied to a *specific* operation
  rather than the whole corpus)?

## Provenance

s309 conversational capture. Correction: Michael. Framing + probe design: AI.
Combinator identities verifiable by hand (`K I = λx y. y`); universality claims
cite s303 (11/11) and s304/s308 (ternary survival) — runtime-measured, not
asserted here. License: MIT (`λ provenance`).
