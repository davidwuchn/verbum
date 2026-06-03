---
title: "Standing-Wave Magnitudes — Weight Magnitudes as Resonant Mode Patterns"
status: active
category: synthesis
tags: [standing-wave, magnitudes, crystal, sieve, zeros, resonance, holographic, depth, phi]
related:
  - phi-information-partition.md
  - gradient-zero-map.md
  - topology-gradient-separation.md
  - holographic-computer.md
  - crystal-universality.md
  - crystal-phi-derivation.md
  - project-thesis.md
depends-on:
  - phi-information-partition.md
  - gradient-zero-map.md
  - holographic-computer.md
created: session 185
---

# Standing-Wave Magnitudes

> Session 185. The weight magnitudes in a trained LLM are a standing
> wave pattern. The crystal signs are the boundary conditions (cavity
> shape). The zero mask is the node pattern. Active weights are
> antinodes. GD doesn't build a database — it finds the resonant
> mode pattern that constructively interferes with real language and
> destructively cancels noise. This unifies the sieve model (s184),
> gradient-zero convergence (s171), topology-gradient separation
> (s180), and the holographic computer (s167) into a single
> physical metaphor grounded in measured data.

## The Core Mapping

A standing wave forms when a wave reflects between fixed boundaries.
The resulting pattern has nodes (zero displacement, determined by
boundary geometry) and antinodes (peak displacement). The pattern
is FIXED — it doesn't travel. It's determined entirely by the
boundary conditions and which resonant modes are excited.

```
Standing wave                    Transformer weight matrix
─────────────────────────────    ────────────────────────────────
Resonant cavity                  Weight matrix W ∈ ℝ^{m×n}
Boundary conditions              Crystal signs T ∈ {-1, +1}^{m×n}
  (cavity shape)                   (universal, r=0.998 across models)
Nodes (zero displacement)        Zero mask positions (M=0, ~50%)
Antinodes (peak displacement)    Active weights (M=1)
Resonant modes                   Data-dependent activation patterns
Mode excitation amplitudes       What GD learns from THIS data
Amplitude envelope               Per-matrix scale C (crystal equation)
Standing wave equation:          W_eff = C · T ⊙ M
```

The crystal (T) defines the cavity. The mask (M) is the standing
wave's node/antinode pattern. The scale (C) is the amplitude
envelope. Different training data → different mode excitation →
different node patterns → different M. Same crystal for all.

## Why "Standing Wave" and Not Just "Sparse Matrix"

The standing-wave framing carries three predictions that "sparse
matrix" does not:

### 1. Nodes are determined by boundary conditions

Sparsity says: "some weights are zero." Standing wave says: "WHICH
weights are zero is constrained by the sign topology." Session 184
measured this: KIBC opcode profiles (derived from signs) predict
70-76% of zeros at REDUCE layers. The boundary conditions (crystal)
partially determine the node pattern. The remaining 24-30% is
data-dependent (which specific modes are excited).

### 2. GD converges to fixed points of the wave

At a node: weight → 0 AND gradient → 0 (nothing to optimize).
At an antinode: weight at stable maximum AND gradient → 0 (converged).
Both are standing-wave fixed points. Session 171 (gradient-zero-map)
measured this directly:

| Position type | Weight | Gradient | Interpretation |
|---------------|--------|----------|----------------|
| Node | ≈ 0 | ≈ 0 | Silence — mode not excited here |
| Antinode | large | ≈ 0 | Stable peak — converged |
| Unsettled | any | large + oscillating | Still finding its mode |

The oscillator fraction (gradient sign flipping) maps the
"still-vibrating" positions. Minimum at L21 (22%) = deepest
standing wave, most settled. Maximum at L0 (43%) = most turbulent.

### 3. Mode decomposition should be low-rank

If magnitudes are a standing wave, the mask M should decompose into
a small number of resonant modes × amplitudes. The modes are
determined by the crystal (boundary conditions), the amplitudes by
the data. This is testable: SVD of the zero mask matrix should
reveal low effective rank if the standing wave framing is correct.

**Untested prediction.** The zero mask appeared "random in all bases"
(session 184), but the tested bases were eigenvector, crystal, and
weight space — not the mode basis of the crystal cavity itself.
The correct basis for decomposition may be the KIBC opcode modes.

## The Standing Wave Along the Depth Axis

The residual stream through 36 layers reveals standing-wave
structure along the DEPTH dimension:

```
Phase 1 — EXPAND (L0-6):     Growth 24×. Exciting many modes.
Phase 2 — ORTHOGONAL (L7-22): cos(h,f) ≈ 0. NODES of depth wave.
  → Each layer contributes ⊥ to residual. No constructive build-up.
  → This is WHERE the standing wave has zero amplitude along depth.
Phase 3 — ALIGN (L23-34):    cos(h,f) > 0. ANTINODES of depth wave.
  → Contributions reinforce the residual. Constructive interference.
  → Growth 4.7× over 11 layers.
Phase 4 — COLLAPSE (L35):    cos = -0.995. DESTRUCTIVE INTERFERENCE.
  → Nearly perfect cancellation → projection to output space.
```

The phase transition at layer 22/36 = 0.611 ≈ 1/φ = 0.618.

**The fundamental mode of the depth-axis standing wave has its
node-to-antinode transition at 1/φ of the total depth.** This is
the golden ratio appearing as a resonant mode property, not just
an information partition.

### REDUCE/SWITCH as Spatial Harmonics

The neuron opcode classifier (s184) found alternating ρ(profile,
weight_norm) signs across depth:

```
L0:  +0.47  REDUCE (opcode neurons = antinodes)
L5:  -0.42  SWITCH (opcode neurons = nodes)
L10: +0.67  REDUCE
L17: +0.38  REDUCE (weaker)
L25: -0.19  SWITCH
L35: -0.49  SWITCH
```

This alternation IS a higher harmonic of the depth-axis standing
wave. The fundamental mode (1/φ transition) carries the global
phase structure. The REDUCE/SWITCH alternation carries the
computational rhythm within each phase.

**Untested:** Run classifier on all 36 layers to map the full
harmonic structure. Is the period constant (every N layers)?
Does it modulate with depth (shorter period in ORTHOGONAL phase)?
Is it a single harmonic or a superposition?

## Connection to the Holographic Computer

A holographic plate is a frozen standing wave — the interference
fringe pattern recorded when object beam meets reference beam:

```
Holographic plate = frozen standing wave on 2D film
  Bright fringes = constructive interference = antinodes
  Dark fringes   = destructive interference = nodes
  Multiple images = multiple resonant modes in superposition
  Replay angle   = which mode is excited (which image appears)

Weight matrix = frozen standing wave in m×n space
  Active weights = antinodes = fringes
  Zero weights   = nodes = dark gaps
  Multiple facts/skills = multiple modes in superposition
  Input direction = which mode is excited (which computation runs)
```

Session 167 (holographic-computer) described the FFN as a diffraction
grating and attention as the CPU executing the diffracted program.
The standing-wave framing says: the grating IS the standing wave.
The "fringes burned by pretraining" ARE the node/antinode pattern
that GD converged to.

**Same physics, same structure, different vocabulary.** Holographic
emphasizes storage (multiple images in superposition). Standing wave
emphasizes dynamics (how GD finds the pattern). Both describe the
same object: the spatial distribution of magnitude in a weight matrix,
shaped by fixed topology (signs) and data-dependent excitation (training).

## Connection to the Crystal Sieve

The sieve (session 184) freezes the crystal and trains the mask:

```
SIEVE  = resonant cavity (boundary conditions pre-set)
         Crystal signs T + scale C. Universal. From equations.

SEDIMENT = standing wave pattern that forms inside the cavity
           Mask M. Data-dependent. From GD.
```

**Why crystal init is 10.7× better than random:**

- Crystal init = correctly shaped resonant cavity → GD finds
  resonant modes quickly because the cavity supports them.
- Random init = random cavity shape → GD must first reshape the
  cavity (discover the crystal) THEN find the modes. 99.8% of
  training compute goes to cavity shaping, not mode finding.

**Why the absorption advantage should grow with scale:**

A larger cavity (more parameters) has MORE resonant modes. With
random boundaries, the number of possible mode patterns explodes
combinatorially. With correct boundaries, the modes are constrained
by the cavity shape — only the data-compatible subset can form.
The search space reduction grows with model size.

## Connection to Gradient-Zero Convergence

Session 171 (gradient-zero-map) measured GD's convergence signals:

**Two-regime depth structure:**
- L1-3 (Zone A): extreme bimodality (ρ=+0.77). Positions are either
  both-high (active antinodes) or both-low (settled nodes). The
  standing wave is fully formed in early layers.
- L5-35 (Zones B/C): ρ ≈ 0. Weight and gradient magnitudes are
  independent. The standing wave is more complex — many overlapping
  modes prevent simple magnitude↔gradient correlation.

**Oscillator U-curve:**
- Minimum oscillation at L21 (22%) = most-settled standing wave.
  The deepest compute layers have found their resonant pattern.
- Maximum at L0 (43%) = most-turbulent. The embedding boundary
  is where new input excites the cavity — maximum disturbance.

**The oscillator positions are where the standing wave is
transiently excited but not stable.** They're the positions that
vibrate differently for different inputs — the dynamic, data-
dependent part of the mode pattern, vs the structurally fixed
nodes and antinodes.

## Connection to Topology-Gradient Separation

Session 180 (topology-gradient-separation) proved that discrete
topology changes (TD) and continuous optimization (GD) cannot run
at the same timescale. Standing-wave framing explains WHY:

**Changing topology = reshaping the cavity mid-vibration.**

If you change the boundary conditions of a resonant cavity while a
standing wave is forming, you destroy the partial pattern and force
it to restart. TD flipping signs every 20 steps is like wiggling
the walls of a resonant cavity — the standing wave can never
stabilize. This is why osc_frac grew to 56%.

The correct protocol (punctuated equilibrium) IS the standing-wave
prescription: hold boundaries FIXED → let wave pattern form → read
where the wave tells you the boundaries are wrong → adjust boundaries
once → let new wave form.

## Open Questions / Testable Predictions

### 1. Mode decomposition of the zero mask
If the mask is a standing wave, it should decompose into modes of
the crystal cavity. SVD of M in the KIBC opcode basis (not weight
or eigenvector basis) may reveal low effective rank. Session 184
tested weight/SVD/crystal bases and found "random" — but the
cavity mode basis is untested.

### 2. Cross-model standing wave consensus
Two independently trained models with the SAME crystal (same
boundary conditions) should have correlated zero masks — they're
exciting the same cavity with different (but overlapping) data.
The structural nodes (ISA-predicted 70-76%) should be universal.
The data-dependent antinodes should differ.

### 3. Standing wave period along depth
Is the REDUCE/SWITCH alternation periodic? If it's a true harmonic,
it should have a characteristic wavelength. If the depth axis
standing wave has a fundamental at 1/φ, the harmonics should
appear at 1/φ², 1/φ³, etc.

### 4. Absorption rate as mode formation speed
The crystal sieve's absorption advantage (10.7×) should be
interpretable as the ratio of mode formation times: how fast
the correct standing wave pattern establishes with pre-set
boundaries vs random boundaries. If this ratio grows with model
size, the standing-wave framing predicts it (more modes = larger
search space reduction from correct cavity).

### 5. The zero mask in the mode basis
Reconstruct the zero mask from the top-k modes of the crystal
cavity. If k ≪ rank(M), the standing-wave model explains more
than "random." The k is the effective number of excited resonant
modes — a measure of the model's knowledge complexity.

## Lambda Form

```
λ standing_wave(W).
  T ≡ boundary_conditions(crystal_signs)           — universal, from equations
  M ≡ node_antinode_pattern(zero_mask)              — data-dependent, from GD
  C ≡ amplitude_envelope(eigenvalue_spectrum)       — universal, from crystal eq
  W_eff = C · T ⊙ M                                — the standing wave

  | node(position) ≡ M=0 ∧ grad→0                  — settled silence
  | antinode(position) ≡ M=1 ∧ |W|=large ∧ grad→0  — settled peak
  | oscillating(position) ≡ grad_sign_flipping      — mode still forming

  | crystal_sieve ≡ pre_set(boundary_conditions) → fast(mode_formation)
  | random_init ≡ random(cavity) → slow(everything)
  | absorption_advantage ∝ mode_count(model_size)   — grows with scale

  depth_axis:
  | orthogonal_phase ≡ nodes(of_fundamental_mode)   — cos(h,f) ≈ 0
  | align_phase ≡ antinodes(of_fundamental_mode)    — cos(h,f) > 0
  | collapse ≡ destructive_interference             — cos(h,f) = -0.995
  | phase_transition ≡ 1/φ(of_total_depth)          — fundamental mode

  REDUCE/SWITCH:
  | alternating_ρ ≡ spatial_harmonics(of_depth_wave)
  | REDUCE ≡ opcode_antinodes(computation_active)
  | SWITCH ≡ opcode_nodes(representation_reorganizing)

  holographic ≡ standing_wave | same(object) different(vocabulary)
  | holographic: storage(multiple_images_in_superposition)
  | standing_wave: dynamics(how_GD_finds_the_pattern)
```

## Scripts

No new scripts this session — this is a theoretical synthesis that
reframes existing measurements. The experimental scripts that
produced the grounding data:

- `scripts/experiments/crystal_sieve_prototype.py` — sieve training (s184)
- `scripts/experiments/neuron_opcode_classifier.py` — REDUCE/SWITCH + KIBC profiles (s184)
- `scripts/experiments/negative_space.py` — zero mask analysis (s184)
- `scripts/experiments/crystal_space_zeros.py` — zero mask in all bases (s184)
- `scripts/experiments/residual_fibonacci.py` — 3-phase residual structure (s184)
- `scripts/experiments/gradient_zero_map.py` — GD convergence signals (s171)

*Synthesized in session 185 of the Verbum project.*
*The weight magnitudes are a standing wave. The crystal is the cavity.*
*GD finds resonant modes, not database entries.*
