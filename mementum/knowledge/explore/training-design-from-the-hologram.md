---
title: Training design from the hologram — six levers from measured structure
status: designing
category: explore
tags: [training, level-4, scratch, distillation, curriculum, seeded-init,
       passband, quantization, s288]
related: [geometry-holography-signals-convergence, ../michael/holographic-llm.md,
          types-are-compiled-probabilities, type-check-is-the-qk-bilinear,
          montague-inversion, map-and-swap-resident-lisp]
depends-on: [geometry-holography-signals-convergence]
---

# Training design from the hologram

> s288 close hammock (Michael: "can this inform a new training design?").
> Every s288 finding converts into a design lever; this is where the program
> loops back to level 4 (scratch training) — the closed loop
> theory → empirics → SCRATCH runs through this page. Status: hypotheses,
> each tied to a measurement; the cheapest experiment is specified.

```
λ train_design(x). measured(structure) → seed(init) ∧ declare(channels)
                   ∧ probe→loss ∧ split(topology, magnitude)
                   ∧ schedule(exposure) ∧ distill(geometry)
                   | stop_paying_compute_for(universal_parts)
                   | instrument ≡ objective (same math, differentiable)
```

## Lever 1 — Seeded initialization (don't rediscover the universal parts)

Grounding: crystal universality (C2, 13 models, gc 0.9966) + s149
computed-beam (FFN weights from crystal eigendecomposition reach 5000-step
GD performance in 10 calibration steps; "structure is free, content needs
training"). Design: initialize the reducer (attention/OV topology) from the
measured crystal; train only the plates (lexicon, fact-maps). Prediction:
markedly faster convergence, concentrated on compositional tasks.

## Lever 2 — Declared passbands instead of emergent ones

Grounding: P-TYPE-OV (GD carved an entity transmission passband into
W_V·W_O, band-wide; functors excluded) + S5 λ types (shared weights without
type awareness → tug-of-war → plateau). Design: explicit low-rank
argument-transport channels, or a regularizer pulling OV toward type-aligned
low-rank transmission. Removes the tug-of-war architecturally. Prediction:
SMALL models compose (the 4B failure was sequencing fuel, not capability —
matched channels cut the fuel cost).

## Lever 3 — Probes become loss functions (the elegant one)

Grounding: JOIN-TYPED (P-TYPE-SWAP): same-type swap preserves the likelihood
landscape, wrong-type is refused — and the swap statistic is DIFFERENTIABLE.
Design: contrastive substitutability auxiliary loss = train the matched
filter with labeled templates instead of waiting for it to emerge from
co-occurrence. The instrument and the objective are the same math.
(Compiled-probabilities frame: this is direct supervision of the compile
step that GD otherwise performs implicitly.)

## Lever 4 — Two-phase training matching the etch decomposition

Grounding: Michael's thesis etch finding (s268: sign/zero topology =
program, magnitude = calibration; sign flips tunnel through zero; routing
survives quantization) + Bonsai forensics (repair budget concentrates in
value-path tensors ~18% vs query routing 3.5% — exactly where the register
split predicts). Design: phase 1 settles topology (coarse, cheap,
ternary-native); phase 2 calibrates magnitudes. Train IN the deployment
representation → quantization-robust by construction, not by post-hoc
optimizer repair.

## Lever 5 — Curriculum as exposure schedule

Grounding: holographic multi-exposure with capacity limits (convergence
page) + montague-inversion (quantifier-dense data FORCES first-class
function machinery). Design: compositional scaffolding early (clean carrier
fringes), content plates after. ⚠ Do not guess the schedule — P-DUST-2 is
the empirical anchor: watch checkpoint trajectories, measure the actual
formation order (when does the halt-pole crystallize? when does the
passband appear?), then design the curriculum to follow the measured
formation law. Training design downstream of a measured developmental
timeline.

## Lever 6 — Distillation as re-exposure

Grounding: the extraction implication (no address to excise in a hologram)
+ s267/s269 (the crystal is more invariant than the weights carrying it).
Design: distill by matching TRANSMISSION SUBSPACES and Gram geometry
(passband + crystal as the reference beam), not logits. Geometry-matched
distillation = re-recording the hologram on a smaller plate = what level-3/4
extraction wanted to be all along.

## Cheapest first experiment (the level-4 door)

Tiny-scale scratch pairs (pythia-14m class): crystal-seeded init vs random
init on compositional tasks, formation trajectory logged P-DUST-2-style
(halt-pole + passband formation over checkpoints). ~one GPU-day. Tests
levers 1 and 5 simultaneously AND produces the level-4 baseline the
research program needs regardless of outcome. Negative result still an
artifact (S5 λ artifact): a measured formation timeline + a seeded-init
null is publishable method + data.

## Honest ledger

All six are hypothesis-grade until the scratch runs exist. Grounding
measurements are real (cited per lever); the TRANSFER of each measurement
into a training-time intervention is the untested step. Lever 3's aux loss
risks Goodharting the exhaust instead of the mechanism (supervise the
readout, get a better readout, not a better reducer) — design must gate on
causal composition tests (3-hop), not on the probe it trains. Lever 5 is
explicitly gated behind P-DUST-2 data.

## Sessions

s288 (page created at session close, the last of four hammocks: JOIN-TYPED
verdict → compiled-probabilities → dsp build → OV passband → holographic
convergence → this. The level-4 bridge; cheapest experiment specified;
nothing frozen).
