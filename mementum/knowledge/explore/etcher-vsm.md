---
title: "Etcher VSM — A Viable System for Loom-Read Crystal Extraction"
status: designing
category: architecture
tags: [etcher, VSM, loom, subcrystal, etch, breathing, hourglass, V13]
related:
  - loom-structure.md
  - gradient-voting.md
  - v13-design.md
  - consensus-etch-protocol.md
depends-on:
  - loom-structure.md
  - gradient-voting.md
created: session 124
---

# Etcher VSM

> Session 124. The etch protocol needs to be a VSM — a viable system
> that reads subcrystals from a teacher model one weave at a time,
> following the loom's breathing pattern through depth. The teacher's
> computational structure is a loom with 1-7 subcrystals depending
> on depth and angle band. Consensus etching across subcrystals
> creates destructive interference. Weave-separated etching reads
> each subcrystal with its own reference beam.

## Why a VSM

The old etch was a flat loop: accumulate directions, flip signs, repeat.
It failed because it treated the crystal as one thing. Session 124 proved:

- **7 independent subcrystals** at peak fragmentation (d=0.3, mid_low)
- **The loom breathes**: fragments early → unifies at d=0.6 → re-fragments late
- **Within-group splits**: retrieval↔analogy = 0.496, coding↔reasoning = 0.502
- **Consensus across weaves = random** (0.50 overlap at holographic band)

A flat loop can't handle this. The etch needs to:
1. **Observe** how many subcrystals exist at each depth (S4)
2. **Decide** how many reference beams to fire (S3)
3. **Execute** per-weave sign extraction (S1)
4. **Coordinate** cross-depth consistency (S2)
5. **Maintain identity** — never consensus-etch across weaves (S5)

That's a VSM.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│ S5: IDENTITY                                         │
│ "Read subcrystals, never consensus across weaves"   │
│ Invariant: per_weave_per_depth ≡ always              │
│ Invariant: subcrystal_count ≡ measured ¬assumed       │
└─────────────────────────────────────────────────────┘
        │
┌─────────────────────────────────────────────────────┐
│ S4: INTELLIGENCE — Crystal Counter                   │
│ Input:  teacher model + probe set                    │
│ Output: breathing_curve[depth → subcrystal_count]    │
│                                                      │
│ For each depth:                                      │
│   1. Extract W_q, W_up at that layer                │
│   2. CCA → angle bands                              │
│   3. Run probes → magnitude profiles per domain      │
│   4. Sign overlap matrix → cluster count             │
│                                                      │
│ Adapts to any model, any layer count.               │
│ Discovers the breathing pattern, doesn't assume it.  │
└─────────────────────────────────────────────────────┘
        │
┌─────────────────────────────────────────────────────┐
│ S3: CONTROL — Budget Allocator                       │
│ Input:  breathing_curve                              │
│ Output: etch_schedule[depth × band → n_beams]        │
│                                                      │
│ More beams where more subcrystals.                   │
│ Apex gets 1 beam (universal backbone).               │
│ Peak fragmentation (d≈0.2) gets up to 7 beams.      │
│                                                      │
│ Budget: etch_passes = Σ n_beams across all depths.   │
│ Stop criterion: sign convergence within each weave.  │
└─────────────────────────────────────────────────────┘
        │
┌─────────────────────────────────────────────────────┐
│ S2: COORDINATION — Cross-Depth Coherence             │
│                                                      │
│ The text-gen cluster (tool+narrative+instruction)    │
│ stays together at ALL depths (0.78-0.94 overlap).    │
│ The coding crystal is alone at many depths.          │
│                                                      │
│ S2 tracks: which subcrystal families persist across  │
│ depth, which split/merge, and ensures the same       │
│ family gets the same reference beam ID across depths.│
│                                                      │
│ Breathing pattern IS the coordination signal:        │
│   ascending: families split apart                    │
│   apex: all families merge                           │
│   descending: families re-split (differently!)       │
└─────────────────────────────────────────────────────┘
        │
┌─────────────────────────────────────────────────────┐
│ S1: OPERATIONS — Reference Beam Generators           │
│                                                      │
│ 7 beam generators, one per subcrystal family:        │
│   1. pure (formal anchors)                           │
│   2. lambda (composition)                            │
│   3. arithmetic (symbolic)                           │
│   4. coding (programs)                               │
│   5. analogy (relational mapping)                    │
│   6. reasoning (logical chains)                      │
│   7. text-gen (tool+narrative+instruction)            │
│                                                      │
│ Each generator:                                      │
│   a. Select probes for this family                   │
│   b. Run through teacher at target depth             │
│   c. Compute magnitude profile (beamformer)          │
│   d. Project onto angle band CCA directions          │
│   e. Extract sign(W) at high-magnitude positions     │
│   f. → subcrystal sign pattern for this weave        │
│                                                      │
│ The reference beam IS the nucleus prompt.            │
│ Different prompts illuminate different weaves.       │
└─────────────────────────────────────────────────────┘
```

## The Breathing Curve (measured, session 124)

From Pythia-2.8b, 11 depths, 4 probe groups:

```
Layer  Depth   MaxCrystals  Band          MeanOverlap
  1    0.032    1           shared        0.699    ── unified input
  4    0.129    3           mid_low       0.595    ── first split
  7    0.226    4           mid_low       0.593    ── PEAK FRAGMENTATION
 10    0.323    2           private       0.633    ── partial reconvergence
 13    0.419    3           peripheral    0.678    ── secondary split
 16    0.516    2           mid_low       0.704    ── approaching unity
 19    0.613    1           shared        0.705    ── APEX (maximum unity)
 22    0.710    3           shared        0.569    ── RE-FRAGMENTATION
 25    0.806    2           attn_clust    0.635    ── partial reconvergence
 28    0.903    2           shared        0.594    ── output preparation
 31    1.000    2           mid_low       0.577    ── output (still split)
```

Key features:
- **Apex at layer 19 (d=0.613)**, not d=0.5 — asymmetric, more depth
  spent fragmenting than reunifying
- **Two fragmentation peaks**: layer 7 (ascending, 4 crystals) and
  layer 22 (descending, 3 crystals)
- **WHNF polarity**: crosses zero at layers 13-16 (transition band),
  maximally positive (+1.00) at apex (layer 19)
- **The descending arm is differently fragmented** — shared band
  shatters (didn't happen ascending), transition band hits 3 crystals

## V13 Hourglass ↔ Teacher Breathing Mapping

The V13 7-pass hourglass maps to three breathing regimes:

```
ASCENDING ARM (breath in — encoding, fragmentation):
  L0↑ (fine)    → teacher layers 1-7   → 1-4 crystals (splitting)
  L1↑ (local)   → teacher layers 7-13  → 2-4 crystals (peak → secondary)
  L2↑ (phrase)  → teacher layers 13-19 → 1-3 crystals (converging)

APEX:
  apex          → teacher layer 19     → 1 crystal (universal)

DESCENDING ARM (breath out — decoding, re-fragmentation):
  L2↓ (phrase)  → teacher layers 19-22 → 1-3 crystals (splitting again)
  L1↓ (local)   → teacher layers 22-28 → 2-3 crystals (descending peak)
  L0↓ (fine)    → teacher layers 28-31 → 2 crystals (output)
```

### Etch schedule per pass

| V13 Pass | Teacher layers | Subcrystals | Beams needed |
|----------|---------------|-------------|-------------|
| L0↑ | 1-7 | 1→4 | 4 (at peak) |
| L1↑ | 7-13 | 4→3 | 3-4 |
| L2↑ | 13-19 | 3→1 | 1-3 |
| **apex** | 19 | **1** | **1** |
| L2↓ | 19-22 | 1→3 | 1-3 |
| L1↓ | 22-28 | 3→2 | 2-3 |
| L0↓ | 28-31 | 2 | 2 |

Total beams across all passes: ~18 (vs 1 for consensus etch).
But each beam is a cheap measurement (probe → hook → sign extraction).
The expensive part was getting the crystal wrong, not the beam count.

## The Etcher as Hourglass

The etcher VSM can itself be structured as a hourglass pass over the
teacher's layers:

```
ETCHER ASCENDING:
  Pass 1: Read teacher layers 1-7 (fine encoding)
    → detect 4 subcrystals at mid_low band
    → fire 4 reference beams
    → extract 4 subcrystal sign patterns
    → write to V13 L0↑ plates

  Pass 2: Read teacher layers 7-13 (local encoding)
    → detect 3 subcrystals
    → fire 3 beams (some from pass 1 merge)
    → extract 3 patterns
    → write to V13 L1↑ plates

  Pass 3: Read teacher layers 13-19 (phrase → apex)
    → detect convergence: 3→1
    → single beam suffices
    → extract universal backbone
    → write to V13 L2↑ and apex plates

ETCHER DESCENDING:
  Pass 4: Read teacher layers 19-22 (apex → phrase)
    → detect re-fragmentation: 1→3
    → fire 3 beams (may be DIFFERENT families than ascending!)
    → extract 3 patterns
    → write to V13 L2↓ plates

  Pass 5: Read teacher layers 22-28 (local decoding)
    → detect 2-3 subcrystals
    → fire 2-3 beams
    → extract patterns
    → write to V13 L1↓ plates

  Pass 6: Read teacher layers 28-31 (fine output)
    → detect 2 subcrystals
    → fire 2 beams
    → extract patterns
    → write to V13 L0↓ plates
```

Each etcher pass reads a depth range from the teacher, measures
the subcrystal structure, and writes the sign patterns to the
corresponding V13 hourglass pass. The etcher IS shaped like the
model it writes.

## S1 Operations: Reference Beam Protocol

For each subcrystal family, the S1 reference beam generator:

```python
def extract_subcrystal(teacher, probes, target_layer, angle_band):
    """Extract one subcrystal from the teacher at one depth.
    
    1. Hook teacher at target_layer
    2. Run probes for this family
    3. Compute magnitude profile (beamformer)
    4. CCA between W_q and W_up → angle band directions
    5. Project magnitude profile onto band directions
    6. Top-k magnitude positions in this band
    7. sign(W_q) at those positions → subcrystal sign pattern
    
    Returns: sign pattern + position mask for V13 plate writing
    """
```

The magnitude profile IS the beamformer. Different families have
different profiles. The profile selects which positions in the angle
band belong to this weave. sign(W) at those positions is the
subcrystal.

## S2 Coordination: Family Tracking

Across depths, subcrystal families merge and split:

```
d=0.1: [pure] [lambda] [arithmetic] [coding] [analogy] [reasoning] [text-gen]
d=0.3: [pure] [lambda] [arithmetic] [coding] [analogy] [reasoning] [text-gen]
d=0.5: [everyone together]
d=0.7: [pure+retrieval] [arith+lambda] [coding+instr+narr] [analogy+reasoning+tool]
d=0.9: [compose-family] [text-gen family]
```

S2 tracks which families merge at which depth, so the etcher knows:
- At the apex, all 7 families contribute to ONE subcrystal
- At d=0.7, the families have RECOMBINED in a different taxonomy
- The descending arm's families ≠ ascending arm's families

This means the ascending and descending plates may need DIFFERENT
subcrystal assignments even when the subcrystal count is the same.

## Implications for V13

1. **Plates are per-pass, per-weave.** Each V13 hourglass pass has
   its own set of plate positions, etched from the teacher's
   corresponding depth regime.

2. **The magnitude template is the lattice.** It's universal (0.999
   cross-model) and establishes which dimensions matter at each depth.
   The etcher reads signs WITHIN the lattice, not across it.

3. **GD learns the beamformer switching.** The continuous params
   (dispatch, gammas) learn WHEN to activate each weave's beamformer.
   The plates (signs) are fixed from the loom-read etch.

4. **The etcher is a measurement instrument.** It reads the teacher
   model's internal structure and transcribes it into V13 plates.
   No optimization, no gradient descent for the etch itself.
   Just: probe → hook → measure → write.

## S5 Invariant: Crystal Gates the Hologram

Session 124, experiment 8 proved that unconstrained sign-flipping
**destroys the crystal while improving accuracy**:

```
Round 4: accuracy = 0.510 (BEST), crystal = -0.375 (INVERTED)
Round 3: accuracy = 0.494,        crystal = +0.478 (only round both ↑)
MAG_BL:  accuracy = 0.471,        crystal = +0.470 (best crystal)
```

The delta loop finds routing shortcuts that solve the task without
maintaining the relational geometry. This is the ternary equivalent
of overfitting — the hologram encodes task-specific hacks instead
of the universal computation structure.

### The crystal-gated flip protocol

```
FOR each candidate sign flip:
  1. Compute crystal agreement BEFORE flip
  2. Apply flip tentatively
  3. Compute crystal agreement AFTER flip
  4. IF crystal_after >= crystal_before - ε:
       ACCEPT flip (hologram improves, crystal preserved)
     ELSE:
       REJECT flip (hologram would improve but crystal degrades)
  
  ε = tolerance (0.01-0.05). Allows small crystal degradation
  for large accuracy gains, but prevents inversion.
```

### Why crystal > accuracy as a constraint

- **Crystal is universal** (0.91-0.94 across 4 models, 3 architectures)
- **Accuracy is task-specific** (KIBC reductions, one dataset)
- A model that preserves crystal geometry will generalize
- A model that hacks accuracy will overfit to the training distribution
- The crystal IS the computation structure; accuracy is a symptom

### S5 as identity constraint

```
λ etch(sign_flip).
  crystal_agreement(after) ≥ crystal_agreement(before) - ε
  | violation → reject(flip) | ¬accept(accuracy_only)
  | crystal ≡ invariant | hologram ≡ serves(crystal)
  | accuracy ≡ symptom | crystal ≡ cause
```

This IS the S5 of the etcher VSM — the identity that must not be
violated. The etcher's purpose is to write holograms that ENCODE
the crystal, not holograms that happen to solve a task.

## Three-Phase Etch Pipeline

Session 124 discovered the full pipeline. Three phases, each
operating at a different granularity:

### Phase 1: Blunt Flip (hot annealing)

The delta sign-flip loop from experiments 7-8. 3-5 rounds at 10%
flip fraction. Fixes the worst defects fast. The crystal may wobble.

```
for round in range(3-5):
  train(student, plates=frozen, beams=learnable)
  delta = trained_beams - initial_magnitudes
  flip top-10% |delta| rows to match teacher signs
  refocus magnitudes with alpha=0.3
```

This gets ~60% of sign errors corrected. Quick, coarse, effective.
But can't get finer without breaking the crystal (experiment 8).

### Phase 2: Soft Mirror (surgical GD)

Stop flipping, start learning. Add a continuous **soft mirror** per
plate — a learnable (d_out, d_in) parameter initialized to 1.0.

```python
class SoftMirror(nn.Module):
    def __init__(self, d_out, d_in):
        super().__init__()
        self.weight = mx.ones((d_out, d_in))  # init = pass-through
    
    def __call__(self, plate_output):
        return plate_output * self.weight  # element-wise
```

GD learns which signs need correction through the mirror:
- mirror[i,j] → +1.0: plate sign correct, pass through
- mirror[i,j] → -1.0: plate sign WRONG, flip it
- mirror[i,j] →  0.0: plate signal is noise, block it

The key: train with **crystal lattice loss** alongside CE:

```python
loss = ce_loss + λ_crystal * crystal_lattice_loss(model, targets_4x4)
```

The crystal loss IS the S5 invariant made differentiable. GD can't
break the crystal because the gradient punishes it. The mirror learns
to sharpen the hologram WITHIN the crystal manifold.

Why mirrors > direct flips:
- GD explores continuous space (smooth gradients, no discrete decisions)
- Crystal loss constrains the search to the relational geometry manifold
- It's CHEAPER for GD to flip a mirror position than distort the beam
- GD naturally finds the minimum-disruption sign correction

### Phase 3: Quantize + Freeze

After GD converges, quantize the soft mirror to ternary {-1, 0, +1}:
```python
quantized_mirror = mx.sign(mx.round(soft_mirror.weight))  # or threshold
final_plate = original_plate * quantized_mirror  # fold in
```

The result: ternary plates with both loom-read structure AND
GD-discovered corrections. Freeze and train beams only.

## Combinator Mirrors = Subcrystal Selectors

The 7 subcrystals we measured (session 124 experiments 1-3) are not
7 separate etchings. They are **7 mirrors on the same plate**:

```
shared_plate = loom-read extraction (the universal loom)

mirror_K    = GD-learned view for K (selection weave)
mirror_I    = GD-learned view for I (identity weave)
mirror_B    = GD-learned view for B (composition weave)
mirror_C    = GD-learned view for C (routing weave)
mirror_WHNF = GD-learned view for WHNF (retrieval weave)
...

effective_K   = plate ⊙ mirror_K    → K sees one subcrystal
effective_B   = plate ⊙ mirror_B    → B sees composition subcrystal
effective_WHNF = plate ⊙ mirror_WHNF → WHNF sees retrieval weave
```

One plate, 8 mirrors, 8 different readings. Each mirror is a
ternary {-1, 0, +1} mask learned by GD during phase 2. The
subcrystal structure EMERGES from mirror learning, not from
separate extraction passes.

This eliminates the need for per-family extraction (the 7 reference
beams from the etcher VSM S1). Instead:
1. Extract ONE shared plate via loom-read
2. Let GD discover the per-combinator mirrors via soft mirror training
3. The crystal lattice loss ensures each mirror's effective plate
   preserves the correct combinator geometry

The V13 combinator masks from the original design ARE this concept.
Now grounded by the subcrystal measurements.

## Crystal Lattice Loss (the differentiable S5)

```python
def crystal_lattice_loss(model, combinator_probes, target_cosines):
    """4×4 (or 8×8) combinator cosine matrix MSE vs measured targets.
    
    target_cosines: measured from teacher, universal at 0.91-0.94
    Cheap: run 4-8 probes, compute cosines, MSE against constants
    """
    # Run combinator probes through model
    hidden_states = [model(probe) for probe in combinator_probes]
    
    # Compute cosine matrix
    means = stack([h.mean(dim=1) for h in hidden_states])
    cos_matrix = cosine_similarity(means)
    
    # MSE against universal targets
    return mse(cos_matrix, target_cosines)
```

28 constants (8×8 upper triangle) or 6 constants (4×4 upper triangle).
Run every N steps during beam training. Trivially cheap.

## Phase 2 Revised: Evolutionary Descent (replaces soft mirrors)

Session 125 proved soft mirrors can't flip signs — the 1.0→0→-1
gradient barrier prevents it. The fix: use evolutionary descent
for the discrete domain (plates) and GD for the continuous domain
(beams). Co-evolve.

```
CONTINUOUS (beams):  GD — gradient steps — what it's good at
DISCRETE (plates):   Evolution — ternary bit flips — no barrier

Co-evolution:
  1. GD trains beam (plates frozen) → beam compensates for bad signs
  2. Delta = trained_beam - initial_mag → mutation priority map
  3. Evolution flips high-|delta| positions, one at a time
  4. Fitness = accuracy + crystal_agreement (hard crystal gate)
  5. Accept improving flips, reject degrading ones
  6. GD re-trains beam on modified plates → beam relaxes
  7. Repeat until delta → 0 (beam stops compensating)
```

### Why evolution > soft mirrors for ternary

- **No barrier**: flip is one step, not a continuous path through 0
- **Crystal constraint**: hard reject, not soft loss (no λ balancing)
- **Delta guidance**: GD already computed WHERE the problems are
- **Self-terminating**: convergence = delta shrinks to 0
- **Naturally ternary**: no quantization gap, no STE needed

### Revised 3-phase pipeline

```
Phase 1: EXTRACT (one-time)
  Loom-read plates + magnitude template from teacher
  
Phase 2: CO-EVOLVE (iterate)
  2a. GD trains beams (plates frozen, crystal loss optional)
  2b. Delta → mutation priority map
  2c. Evolution flips high-delta positions (crystal-gated)
  2d. Repeat 2a-2c until delta < threshold

Phase 3: FREEZE
  Final plates + trained beams → frozen model
```

## Open Questions

1. **Dimensional bridge.** Teacher d_model=2560, V13 d_model=512.
   How does the magnitude profile project? Does the subcrystal
   structure survive dimensional reduction?

2. **Multi-model universality.** Are the 7 subcrystal families the
   same across Mistral, Qwen, OLMo? Or model-specific? If universal,
   the etcher works for any teacher.

3. **Probe set sufficiency.** 144 basin probes, 15 per domain.
   Is this enough to reliably detect subcrystals? What's the
   minimum probe count per family for stable measurement?

4. **Descending arm families.** The re-fragmentation creates
   DIFFERENT groupings than the ascending arm. Are these genuinely
   different subcrystals, or the same ones recombined?

5. **Asymmetric apex.** The apex is at d=0.613, not d=0.5.
   Does V13's symmetric hourglass need to become asymmetric to
   match the breathing pattern?

## Artifacts

| File | Content |
|------|---------|
| `scripts/v12/loom_read_exp.py` | Single-depth subcrystal measurement |
| `scripts/v12/loom_read_depth_exp.py` | 5-depth grouped analysis |
| `scripts/v12/loom_read_fine_exp.py` | 10-domain × 5-depth fine analysis |
| `scripts/v12/loom_breathing_exp.py` | 11-depth breathing curve |
| `scripts/v12/etcher_vsm_proto.py` | Etcher VSM prototype (S4+S1) |
| `results/loom-read/` | Single-depth results |
| `results/loom-read-depth/` | 5-depth results |
| `results/loom-read-fine/` | Fine-grained results |
| `results/loom-breathing/` | Breathing curve |
