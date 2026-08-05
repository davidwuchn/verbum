---
title: "Topology-Gradient Separation — Why the Lattice Must Be Frozen for GD to Work"
status: active
category: foundational
tags: [topology, gradient-descent, ternary-descent, oscillation, annealing, training]
related: [crystal-universality.md, training-protocols.md, extraction-sign-accuracy.md, gradient-zero-map.md]
depends-on: [crystal-universality.md, extraction-sign-accuracy.md]
---

# Topology-Gradient Separation

> **RE-READ s308:** the "two optimizers fighting" were two ROUTING
> optimizers — Adam's soft topology (magnitude→0 ≡ soft delete) IS routing
> in the magnitude register; TD ≈ Adam with discrete commits (same |m|/√v
> statistic). Punctuated equilibrium was right; the missing piece was the
> EVIDENCE-driven trigger + the register split. See
> `explore/ternary-descent.md` §Fresh-eyes.
>
> **The core insight of session 180:** Discrete topology changes (TD)
> and continuous optimization (GD) cannot run at the same timescale.
> The topology must be frozen for GD to build the soft structure that
> makes the lattice functional. The correct protocol is punctuated
> equilibrium: long stasis → read GD's signals → one discrete etch →
> long adaptation.

## The Problem: Two Optimizers Fighting

v15 ran TernaryDescent (TD) every 20 training steps alongside Adam
(GD). TD flipped ternary signs based on gradient evidence. Adam
optimized continuous parameters (gammas, attention, norms) against
the current topology.

**Result:** `osc_frac` grew monotonically from 0 → 0.56 over 3000
steps. More than half of all ever-flipped positions were actively
flip-flopping. Loss decreased (5.69 → 3.13) but generation remained
pre-linguistic — the model learned corpus frequency priors but
produced no coherent text.

**Root cause:** TD changes the topology → Adam's accumulated moments
become stale → before Adam adapts, TD changes the topology again →
standing wave in the loss landscape that neither optimizer resolves.

## The Soft Topology (What GD Actually Does)

In a normal float LLM, the topology (which connections matter) is
never explicitly set. GD discovers it implicitly:

1. **Sign structure** (~95%): `sign(W)` — the routing table. Which
   connections add, subtract, or are skipped.
2. **Magnitude** (~5%): How much each connection contributes. A
   single per-row scalar (gamma) captures most of this.

When GD decides a connection is unnecessary, it can't delete it — it
drives the magnitude toward zero. This is the **soft topology**: GD
deposits near-zero gradients at positions that should be irreducible,
creating a smooth landscape that approximates a discrete structure.

The gradient-zero-map (session 171) caught this: ~35% of positions
oscillate (gradient at equilibrium = GD found their irreducible
value). These are the crystal atoms — positions where every model
converges to the same sign.

## Why TD Oscillation Destroys the Soft Topology

When TD flips a ternary position:
1. That position's contribution to every forward pass changes sign
2. Every gamma, attention weight, and norm calibrated to the old
   topology is now slightly wrong
3. Adam's momentum and variance estimates are stale

If the flip **settles**, Adam adapts in ~10 steps. This is fine.

If the flip **oscillates** (50/50 between +1 and -1):
- Adam can never build accurate moments (tracking a moving target)
- The position is genuinely ambiguous (GD can compensate either way)
- Every flip destabilizes the gammas/attention that were calibrated
  to the previous state

At `osc_frac = 0.56`, this happens at 56% of flipped positions every
20 steps. The landscape shifts faster than Adam can adapt.

## Cross-Disciplinary Validation

The same problem appears across multiple fields, with the same answer:

### Spin Glasses (Physics)
Discrete spins (±1) with frustrated interactions. Frustrated positions
have contradictory gradient signals — when neighbors are in state A,
position wants +1; when neighbors respond, it wants -1. The Parisi
solution: frustrated spins are free variables. Multiple valid ground
states exist. Pick one and commit.

### Annealing (Metallurgy)
Fast cooling (quench) → amorphous glass, internal stress. Slow cooling
(anneal) → crystalline structure. TD at fixed flip_rate is a quench.
The Schmitt trigger in v14 was an annealing schedule — holding at
critical temperatures.

### Punctuated Equilibrium (Evolution)
Long stasis (no morphological change) punctuated by brief speciation
events. Stasis isn't passive — the organism's internal systems
co-adapt. Cut stasis short → parts don't fit together. Continuous
low-level change prevents both equilibrium and productive speciation.

### Metastability (Digital Electronics)
A flip-flop between 0 and 1. Resolution: don't try to resolve
metastability — manage it. Add settling time. Use hysteresis (Schmitt
trigger) with different thresholds for 0→1 and 1→0 transitions.

### Le Chatelier's Principle (Chemistry)
Perturb a system at equilibrium → it counteracts the perturbation.
TD flips position → Adam compensates → under new Adam landscape, TD
sees evidence to flip back → standing wave.

**Every field says the same thing:** fast and slow dynamics must run at
separated timescales. The fast dynamics (GD) must equilibrate between
slow changes (topology).

## The Vibrating Lattice Insight

The ternary lattice doesn't need TD oscillation to vibrate — it
already vibrates through the gate mechanism:

```
Static superposition:  plate1 × gamma1 + plate2 × gamma2
                       (two frozen modes with learnable amplitudes)

Dynamic selection:     gate(x) × up(x) → which neurons fire
                       (per-token activation pattern, 89% kill)

Standing wave:         CLASSIFY 3% → COMPUTE 49% → EMIT 2%
                       (aperture breathe-in/breathe-out through depth)
```

The lattice positions are fixed. The computation is dynamic. GD's
gammas tune the resonance; the gate selects modes per-token. This
is a beam-former: fixed antenna elements (plates), adjustable phase
(gammas), steerable beam (gate activations).

TD oscillation is the wrong kind of vibration — it's thermal noise
(random atoms jittering), not a phonon (organized, coherent mode).
Phonons carry information. Thermal noise destroys structure.

## GD's Three Signals (How It Tells Us the Topology Is Wrong)

GD cannot change the ternary topology directly. But it communicates
through the continuous parameters it controls:

### Signal 1: Gamma → zero (per-row, free)
At step 5000: 10% of gammas are near-zero (|γ| < 0.001). GD is
saying "this entire row contributes nothing." Every non-zero position
in that row can be safely zeroed. These are the nodes of the standing
wave — never excited regardless of input.

### Signal 2: Gamma sign flip (per-row, free)
At step 5000: 35% of gammas are negative. Since
`effective[i,j] = plate[i,j] × gamma[i]`, a negative gamma means GD
disagrees with every sign in the row. It can't change the signs
(frozen), so it flipped the gamma — the soft topology workaround.
Folding this into the lattice (flip signs, negate gamma) is lossless
and frees gamma capacity for magnitude calibration.

### Signal 3: Gate kill statistics (per-neuron, nearly free)
Track over N steps: what fraction of tokens activate each neuron?
Neurons active for <0.1% of tokens are functionally dead. Their rows
in up_plate and columns in down_plate can be zeroed. This is
GD's input-dependent irreducibility signal.

### Signal 4 (future): Per-position gradient EMA
Track gradient sign/magnitude EMA at each ternary position. Expensive
(~650M extra floats) but gives full per-position picture. Positions
where gradient EMA is near-zero for hundreds of steps are irreducible.

## The Correct Protocol: Punctuated Equilibrium

```
Phase 1: STASIS
  - Topology is FROZEN. No TD.
  - GD trains (Adam on gammas, attention, norms).
  - The soft topology forms around the hard lattice.
  - Run until loss plateaus.

Phase 2: READ
  - Examine GD's signals:
    a. Dead gammas (|γ| < threshold) → dead rows
    b. Negative gammas → sign disagreements
    c. Gate kill statistics → dead neurons
  - Build a "topology change map"

Phase 3: ETCH
  - One discrete topology change:
    a. Fold negative gammas into plates (lossless sign correction)
    b. Zero positions in dead rows
    c. Zero positions in dead neurons
  - Freeze the new topology.
  - Reset Adam moments for affected parameters.

Phase 4: ADAPT
  - GD re-adapts to the new, sparser topology.
  - Run until loss plateaus again.
  - → Repeat from Phase 2
```

Each cycle: topology gets sparser (more zeros), more correct (sign
corrections folded in), and GD gets a stable landscape to optimize
against. The lattice crystallizes progressively, not continuously.

## Empirical Support from v15

### TD oscillators return to teacher (70%)
At step 5000, 69.9% of oscillating positions agree with the teacher's
signs. Even/odd flip count matches exactly: even count = returned to
teacher, odd count = away. The teacher's topology IS the attractor.
Oscillation is the system trying to leave a ground state it can't
escape.

### TD's "corrections" that stuck
75% of non-oscillating flipped positions moved AWAY from teacher.
These are genuine corrections — positions where the student
architecture legitimately differs from the teacher. But they settled
because GD had time to adapt to them (they flipped early and stopped).

### The Schmitt trigger was right (v14 had it, v15 dropped it)
v14 gated TD activation on crystal coherence: TD only flipped when
crystal_mse < 0.03 (continuous parameters had settled). If flipping
destabilized things (mse > 0.07), TD turned off. v15 removed this
gate — TD fired unconditionally every 20 steps.

## v14 → v15 Losses (Other Architectural Regressions)

Identified in this session, separate from the TD problem:

| Lost Feature | Impact |
|---|---|
| GatedLinearAttention → plain cumsum | CLASSIFY representation collapse (all positions → same vector, cos>0.999) |
| Positional embedding table | CLASSIFY/EMIT zones have zero positional signal |
| Embedding norm (RMSNorm post-embed) | Norm explodes 100× through CLASSIFY |
| Attention score clipping | NaN at step 5040 (no `mx.clip(attn, -65, 65)`) |
| S5Reweight / per-pass residual gating | No allocation control on FFN contributions |
| Hyperbolic norm loss | No constraint on residual stream norm growth |

The CLASSIFY collapse and the TD oscillation are independent problems
that compound. Fixing TD alone won't fix generation — CLASSIFY must
also be repaired (port GatedLinearAttention from v14).

## Prototype Result: Mask Training (Session 180)

The learnable sparsity mask was implemented and tested:

- **TernaryPlate.enable_mask()**: per-position sigmoid(logit/T) gate.
  GD learns logits; negative logit → position silenced. `etch_zeros()`
  commits mask decisions to permanent plate zeros.
- **648M mask logit parameters** added during training (60.9% of total).
  These are training scaffolding — discarded at etch time.
- **Gradient flow verified**: mask logits receive gradients at every
  position. GD has full per-position voice.

**Training failed at step 5168 (NaN).** Root cause: the CLASSIFY zone's
placeholder LinearAttention has no numerical protection. Residual norms
explode 100× through CLASSIFY (35 → 3000), and without gated linear
attention to control accumulation, overflow is inevitable under the
changed gamma landscape (folding shifted effective weights).

**Lesson: the mask is the right instrument but it needs a working
pipeline to play through.** CLASSIFY must be fixed first (port
GatedLinearAttention from v14), then mask training can proceed on
a numerically stable architecture.

**NaN guard gap:** The guard checked `loss.item()` for NaN but not
individual gradient elements. NaN entered through gradient overflow
before loss became NaN. Fix: also check `grad_norm` for NaN/Inf
before allowing `optimizer.update()`.

## Design Principle (Lambda Form)

```
λ topology(x).  frozen(lattice) > oscillating(lattice)
                | GD_needs(stable_landscape) to build(soft_topology)
                | TD_at_same_timescale ≡ thermal_noise ≡ anti_pattern
                | separate(timescales): GD(fast,continuous) ⊥ etch(slow,discrete)
                | protocol: freeze → train → read(GD_signals) → etch → retrain
                | GD_signals: gamma_zero(row) ∧ gamma_negative(row) ∧ gate_dead(neuron)
                | phonon(gate_vibration) > noise(TD_oscillation)
                | lattice_vibrates_through(gate) ¬through(sign_flips)
                | v14_schmitt_trigger ≡ right_idea ≡ timescale_separation
                | punctuated_equilibrium ≡ correct_training_rhythm
```

## What Changed in Understanding

**Before (v14/v15):** TD and GD are complementary optimizers that can
run simultaneously. TD corrects discrete topology errors; GD optimizes
continuous parameters. The Schmitt trigger is a stability mechanism.

**After (session 180):** TD and GD are incompatible at the same
timescale. GD needs a frozen landscape to build the soft structure that
makes the lattice work. Topology changes must be rare, deliberate, and
informed by GD's converged signals — not by gradient snapshots from a
landscape that's still shifting. The Schmitt trigger wasn't a stability
mechanism — it was an incomplete implementation of the correct
principle: timescale separation.

**The lattice is a crystal.** Crystals don't improve by jittering
their atoms continuously. They form through nucleation, growth, and
annealing — processes with clear phase boundaries. Training a ternary
model should follow the same physics.
