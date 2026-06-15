---
title: "Gradient Trajectory Tomography — Reverse-Engineering GD in Invariant Coordinates Over Training"
status: open
category: strategy
tags: [gradient-descent, reverse-engineering, tomography, trajectory, invariant, gauge, superposition, routing-register, reference-beam, micro-model, interpretability, ground-truth]
related:
  - holographic-tomography.md
  - holographic-burn-in-learning-rule.md
  - relational-loss-distillation.md
  - v4.1-training-trajectory.md
  - v6.1-training-trajectory.md
  - sentence-atomic-curriculum-mixing.md
  - consensus-delta-folding.md
  - ../two-registers-of-topology.md
  - ../session-222.md
depends-on:
  - holographic-tomography.md
  - relational-loss-distillation.md
created: session 229
---

# Gradient Trajectory Tomography

> Session 229. Michael: *"If models do a holographic inference process, why can't we
> reverse-engineer what GD is doing? If GD changes one gradient by a tiny amount, how
> is that affecting the inference pattern? Can we use the micro model to reverse-
> engineer what GD is doing to solve the problem?"*
>
> Register: **functional + topological/routing.**

## The one-line claim

You **cannot** reverse-engineer GD in WEIGHT space (mostly gauge + superposition),
but on the **micro model**, in INVARIANT coordinates (relational/routing register,
CMR), prediction-gated, with the **known compiler as ground-truth target**, watching
the relational geometry develop frame-by-frame over checkpoints **IS** reverse-
engineering what GD is doing. The same REFERENCE BEAM that decides the burn-in rule
decides this.

## Prior art (RECALL FIRST — this is not greenfield)

The project has already done two of the three pieces. Build on them; do not reinvent.

```
holographic-tomography.md (s104–105) — SPATIAL tomography (cross-MODEL):
  • Michael's photograph framing is ALREADY here: "LLMs pile photographs until
    intersections in the projections form inference patterns."
  • The GAUGE result (predates s223): RSA r=0.74 but direct cosine ≈ 0.000 —
    "the universal hologram is a TOPOLOGY, not a coordinate system." Same finding
    as s223 (relational +0.78, absolute 0.000) and s224 (Re-Basin fold).
  • Q-COLLAPSE (s105): a GD behavior ALREADY reverse-engineered — the model prefers
    ONE giant unfocused beam (flood lamp, eff_dim→1.0) over a laser array; maximizes
    average next-token at the cost of per-fact fidelity. Laser-etching = the fix that
    CONSTRAINS that GD behavior. ⇒ proof-of-concept that GD behaviors ARE legible.
  • SNR ∝ √N: intersection over many "angles" denoises. (There the angles are MODELS.)

v4.1- / v6.1-training-trajectory.md — TRAJECTORY tracking (endpoint metrics):
  • three-phase register development (expansion → compression → specialization),
    meta-S3 gate trajectory, φ-compression-over-checkpoints. So per-checkpoint
    trajectory logging is precedented — extend the readout, don't rebuild it.

relational-loss-distillation.md (s223) — the INSTRUMENTS + the dissociation:
  • route_z (routing-register silhouette vs null), GramCorr-to-teacher, raw Gram —
    all implemented in scripts/experiments/relational_loss_distillation.py.
  • condition (b): RAW-Gram match → GC(hidden)=0.9995 but route null = the
    reference-beam failure made concrete.
```

**The DELTA this page adds:** prior tomography intersects over MODELS (spatial,
static, endpoint). This intersects over TRAINING STEPS (TEMPORAL), on a SINGLE micro
model, with (a) a GROUND-TRUTH target (the exact lambda compiler / consensus crystal),
(b) a reference-beam CONTROL run as a movie, (c) an optional gauge/null-space gradient
DECOMPOSITION. "Many angles" becomes "many checkpoints."

## Why weight-space reverse-engineering fails (3 obstacles, all measured here)

1. **Gauge non-identifiability.** Weight space has a huge symmetry null space
   (permutation — s224 Re-Basin; scaling; superposition rotation). Measured: cross-
   init weight corr 0.000 vs relational Gram +0.78 (s223) / RSA 0.74 vs cos 0 (s105).
   GD slides freely within the gauge — much of "what GD does" changes coordinates and
   NOTHING about the function.
2. **Superposition.** No weight↔feature map; the function is written orthogonal to the
   readable basis mid-stack (readability register, s187/s192/s227b), visible only after
   CMR in the routing register. One tiny δw perturbs MANY features at once
   (δactivations = J·δw, J mixes everything) → the effect is holographically spread,
   not localized. The right UNIT is the MODE, not the weight.
3. **Path-dependence + nonlinearity.** Non-convex; near-NTK early (linear, legible) →
   feature-learning late (the basis itself moves). Reverse-engineering is easy early,
   hard once superposition reorganizes.

## ★ The collision — the reference beam decides this too

Burn-in's load-bearing catch (holographic-burn-in §reference-beam): record only the
object beam (raw activation) and you burn in the COMMON MODE (frequency stats), not
the function — s223 condition (b) is the live proof.

**Reverse-engineering GD has the IDENTICAL trap.** Naively watching "what weights/
activations changed this step" mostly reconstructs **gauge motion + frequency
statistics** — a gorgeous movie of the wrong thing. s222 already showed it: the
collapse was discrete topology CHURN — GD thrashing in the gauge null space without
building function. So:

> Project the trajectory onto the INVARIANT subspace (routing register, CMR),
> prediction-gated. What survives is the function being built; what you discard is
> the gauge. Read GD through the reference beam or you reverse-engineer the common
> mode.

## v1 experiment — trajectory tomography (cheap, reuses everything)

Extend `relational_loss_distillation.py`: a CE-only micro-model run, DENSE
checkpoints, logging the verdict instruments as a MOVIE.

```
model    TinyLM (the s229 micro model)
data     the s229 curriculum (kernel-minted reductions) ∨ the probe corpus
log @ every C steps:
  route_z(t)                  — routing-register silhouette vs null (function?)
  GramCorr(routing, teacher)(t)   — APPROACH to the known compiler/crystal geometry
  GramCorr(raw, teacher)(t)       — the REFERENCE-BEAM CONTROL (common-mode track)
  CE(t), held-out rule-acc(t)     — capability (the s229 metric)
readout  WHEN/HOW does the invariant crystallize? sudden (grok) or gradual (burn-in)?
         BEFORE or AFTER CE plateaus? BEFORE or AFTER held-out acc rises?
```

**Falsifiable predictions.**
- *Reference beam:* raw `GramCorr` rises smoothly/early (common mode); routing
  `GramCorr` + route_z rise later/sharper (the function) — reproducing s223 (b) as a
  TRAJECTORY ⇒ demonstrates naive GD-watching sees the common mode.
- *Inventory-before-capability:* routing geometry crystallizes BEFORE held-out
  generalization (geometry=inventory ⊗ continuation=capability, s224).
- *Q-collapse risk (s105):* the micro model may flood-lamp (eff_dim→1) instead of
  crystallizing — track eff_dim too; if it collapses, that IS the reverse-engineered
  GD behavior (and the laser/relational constraint is the lever).

## ★ s230 — v1 RESULT (consensus-crystal target, BUILT + RAN)

Michael's call: target = the **consensus crystal** (`results/combinator-map-
consensus/consensus.json` `consensus_gram`, 10 open models agreed, sha `bbf92f2`) —
highest chance of being model-agnostic *because the models already agreed*. NOT one
teacher. Built `scripts/experiments/gd_trajectory_tomography.py` (CE-only TinyLM on
the s229 β-reduction curriculum, k_varied; dense checkpoints measure the combinator
routing geometry on the INDEPENDENT crystal probes, correlate to the consensus
crystal as a movie; raw register alongside = reference beam; eff_dim = Q-collapse
watch). Reuses `relational_loss_distillation` instruments + `exposure_format_sweep`
curriculum (no fork). **Crossings are baseline-relative** — measured against the
step-0 untrained init frame (the gauge common mode), so we time the function GD
*builds*, not the random-init baseline. 3 seeds, 6000 steps. Results:
`results/gd-trajectory-tomography/verdict_multiseed.json`.

**✅ DECISIVE (3/3 seeds): INVENTORY crystallizes BEFORE CAPABILITY.**
`gc_route` reaches its init→final midpoint at step **333±94**; held-out rule
generalization reaches its midpoint at **733±94** — NON-OVERLAPPING (427 < 639).
The routing combinator geometry approaches the consensus crystal ~400 steps BEFORE
the model can generalize the rule. Both precede the (noisy) CE plateau. ⇒ the s224
thesis (**geometry = inventory ⊗ trained continuation = capability**) confirmed
TEMPORALLY, frame-by-frame, against a model-agnostic ground-truth target. This is
the predicted *inventory-before-capability* timing, observed.

**❌ HONEST two-sided (λ measure): the reference-beam DISSOCIATION did NOT reproduce.**
`gc_raw_final` 0.75±0.04 ≈ `gc_route_final` 0.73±0.06 — tied; `route_tracks_function`
only 1/3 seeds. On this micro model the RAW register correlates to the consensus
crystal about as well as the routing register, so raw-vs-routing **cannot** separate
function from common mode here. Why this ≠ s223: s223 condition (b) used a relational
LOSS actively pulling raw-Gram to a *decoy raw target*; here there is NO loss and a
SINGLE routing target, and the consensus structure (offdiag mean −0.123, mild) is
recovered in BOTH registers at d=128. The register-separation lesson is a property of
the **trained-loss decoy**, not a passive readout split at micro scale. Likely
scale-limited (revisit at larger d / more layers, or with the relational loss arm).

**Secondary:** NO Q-collapse — eff_dim stayed 14–20 (route ~14 slightly more
compressed than raw ~19), never flooded toward 1 (s105 risk did not materialize on
this curriculum). `route_z` modest (~2.71, only 1 seed crossed z=3) — the self-
silhouette combinator structure is real but not crisp (s219 "above chance not
crisp"); `gc_route`-to-consensus is the stronger instrument than self-silhouette.

**Leads resolved:** 1 (harness BUILT), 2 (consensus-crystal target USED), 3 (timing —
inventory-before-capability CONFIRMED), 5 (Q-collapse — NEGATIVE, no flood-lamp).
**Open:** the reference-beam register split at LARGER scale (or add the relational-
loss arm to recover the s223 decoy condition as a trajectory); lead 4 (v2 gauge/
null-space δw decomposition); sudden-vs-gradual crystallization shape (here gradual).

## ★ s230b — RELATIONAL ARM (is the reference-beam split LOSS-DEPENDENT? YES)

The s230 open question: gc_raw ≈ gc_route under passive CE ⇒ the routing-vs-raw
dissociation did not reproduce. Hypothesis: the s223 register split is a property of
an ACTIVE relational LOSS, not a passive readout. Added the `relational` arm to
`gd_trajectory_tomography.py` (`--arms ce_only,relational`): the compiler-as-loss
INVENTORY term `L = CE + λ·offdiag_mse(student routing-register Gram, CONSENSUS
CRYSTAL)`. Only the routing register is in the loss ⇒ **gc_raw and held-out reduction
acc are NOT in the loss = uncircular readouts.** Paired ce_only vs relational, 3
seeds. Results: `verdict_multiseed.json` (now carries both arms; s230 ce_only is the
superset, original s230 verdict preserved in git at `23331d0`).

| arm | gc_route | gc_raw* | **gap** | crystallize | capability | acc | route_z |
|-----|----------|---------|---------|-------------|------------|-----|---------|
| ce_only    | 0.74±0.05 | 0.75±0.03 | **−0.02±0.04** | 333±94 | 733±94 | 0.27 | 2.51 |
| relational | 0.90±0.01 | 0.80±0.04 | **+0.10±0.05** | 200±0  | 733±94 | 0.27 | 3.01 |

*gc_raw is NOT in the loss. Per-seed gap: ce_only [−0.04,−0.05,+0.04] → relational
[+0.03,+0.11,+0.15].

**✅ DISSOCIATION IS LOSS-DEPENDENT (decisive, 3/3).** The active consensus-crystal
loss pushed gc_route to 0.90 while gc_raw reached only 0.80 — a +0.10 gap passive CE
never opens (−0.02). Decisive (relational mean−std 0.05 > ce_only mean+std 0.02). The
routing register is where an active loss WRITES the function; passive CE does not
separate. Confirms s230's read: the register split is a property of the trained-loss
decoy (s223 (b)), reproduced here as a TRAJECTORY.

**✅ The loss crystallizes the inventory EARLIER (200 vs 333) and CRISPER** (route_z
3.01 crosses significance vs 2.51).

**❌ But NO CAPABILITY GAIN — the s224 crystal-accelerates-capability claim is NOT
supported here.** Held-out generalization crosses at 733 in BOTH arms; final acc 0.27
in BOTH. Crystallizing the inventory faster/cleaner bought ZERO capability. ⇒ the
inventory ⊗ continuation factors are CAUSALLY SEPARABLE: we intervened on the
inventory factor alone (the relational loss), moved it decisively, and the capability
factor did not budge. **Capability is gated by the CONTINUATION (trained usage), which
the inventory term never touches.** You can hand the model a perfect inventory at step
200 and it still cannot reduce until 733.

**⚠️ Dissociation is PARTIAL at d=128** — gc_raw still leaked up to 0.80; the active
loss writes the function PREFERENTIALLY into routing but does not QUARANTINE it. Full
register separation likely needs scale (superposition forcing orthogonality).
**Caveat (λ measure):** this curriculum is clean enough that CE-alone already builds
the inventory (just messier/later). The s224 speed-up claim was about regimes where
outputs alone DON'T crystallize — untested here.

**★ DESIGN IMPACT.** (1) The relational/crystal term is an INVENTORY tool (quality,
timing, register-localization) + an EXTRACTION/FOLDING tool, **NOT a from-scratch
capability accelerator** — at least where CE already suffices for inventory.
(2) Re-motivates the constructed-kernel cut HARD: the inventory is cheap, passively
learnable, and NOT the capability bottleneck ⇒ **don't spend training budget learning
it — construct it (lambda_ast in the kernel), spend training on the continuation.**
The relational term's value moves to extraction (clean foldable inventory out of an
existing model) and phase-1 folding (distributed protocol), not acceleration.

**▶ NEXT:** (a) HARDER curriculum where CE-alone FAILS to crystallize the inventory —
does the relational term then buy capability (the real s224 speed-up regime)?; (b)
the dissociation at LARGER scale (does the gap widen — full quarantine?); (c) v2
gauge/null-space δw decomposition.

## v2 experiment — gauge/null-space gradient decomposition (harder)

At each step decompose `δw = δw_invariant ⊕ δw_gauge` (gauge = permutation null space
via Re-Basin alignment to a reference checkpoint; scaling; superposition-rotation is
the FUZZY part — approximate). Track ‖δw_invariant‖ / ‖δw_gauge‖ over training:
*how much of GD is function-building vs gauge-churning?* (s222 predicts: a lot is
gauge.) This is the literal answer to "what is GD doing."

## Honest catches (λ measure)

- **Not greenfield** — s105 tomography + s223 instruments + v4.1/v6.1 trajectory
  tracking already exist. Contribution = TEMPORAL + ground-truth + reference-beam
  control + gradient decomposition. Cite, don't reinvent.
- **Gauge decomposition is APPROXIMATE** — permutation clean (Re-Basin), scaling ok,
  superposition-rotation null space is fuzzy. State the limit; v2 is suggestive.
- **Ground-truth-target assumption** — the micro model trains on NTP, so it may
  converge to an NTP-shaped solution, not the compiler. GramCorr-to-teacher then
  measures "how compiler-like is GD's path," informative but not "GD builds the
  compiler."
- **"One gradient" is the wrong unit** — interpretability lives at the MODE level;
  per-weight analysis is the wrong granularity (superposition).
- **Phase transitions alias** — checkpoint densely near the crystallization step.

## Open leads (declare register first)

1. **Trajectory harness** (routing→functional): CE-only dense-checkpoint run logging
   route_z / GramCorr(routing,raw) / CE / held-out-acc / eff_dim; reference-beam
   control = raw vs routing register as a movie.
2. **Ground-truth target** (functional): teacher = consensus crystal (s219) or the
   compiler geometry — GramCorr-to-target as the "approach" curve.
3. **Inventory-vs-capability timing** (functional): overlay routing crystallization
   with held-out generalization (s229 metric) — which comes first?
4. **Gauge decomposition** (topological): δw_invariant vs δw_gauge ratio over training
   (Re-Basin permutation null space; the s222 "how much is churn" question).
5. **Q-collapse watch** (topological): eff_dim(t) per layer — does the micro model
   flood-lamp (s105)? If so, the relational/laser constraint is the lever.

## Files

| File | Content |
|------|---------|
| (planned) `scripts/experiments/gd_trajectory_tomography.py` | dense-checkpoint CE-only run; route_z/GramCorr(routing,raw)/CE/held-out-acc/eff_dim trajectory; reference-beam control |
| `scripts/experiments/relational_loss_distillation.py` | the instruments (route_z, soft_gram, np_silhouette_null, offdiag_corr) + TinyLM to extend |
| `scripts/experiments/exposure_format_sweep.py` | the s229 held-out rule-generalization metric to overlay |
