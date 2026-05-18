---
title: "Seed Crystal Design — Universal Backbone as Relational Fixed Points"
status: designing
category: architecture-design
tags: [crystal, seed, backbone, relational-loss, fixed-points, sieve, lattice, MDS]
related:
  - crystal-spine-sieve.md
  - universal-crystal-transfer.md
  - consensus-etch-protocol.md
  - VERBUM.md
depends-on:
  - crystal-spine-sieve.md
created: session 113
---

# Seed Crystal Design

> The universal crystal is the shape of language, not the shape of
> any model. Where models agree, they've discovered language geometry.
> Where they diverge, their sieve is showing. We initialize the
> backbone geometry as a seed, then let the crystal grow.

## The Insight Chain

### 1. Agreement = language geometry

Cross-model agreement on relational distances reveals what's universal:

```
math         72.3% agreement  ← language imposes this structure
reasoning    70.1% agreement  ← language imposes this structure  
tools        51.9% agreement  ← sieve-dependent, models diverge
lambda       43.1% agreement  ← sieve-dependent, models diverge
```

High agreement = the distance between these computations is a property
of language itself. Every model discovers it independently because it's
IN the data. Low agreement = the model's architecture is imposing its
own geometry.

### 2. The backbone IS the seed crystal

Top 10% highest-agreement pairs form the backbone:

```
32,522 pairs from 664 probes (of 807 total)
Agreement threshold: >= 0.6312

Composition:
  math (self)          48.1%  — arithmetic has universal geometry
  lambda × math        15.1%  — computation-semantics interface
  reasoning (self)     12.7%  — logic has universal structure
  math × reasoning      9.1%  — computation-logic bridge
  code (self)           3.7%  — algorithms agree across models
  tools × anything      0.3%  — almost absent (sieve-dependent)
```

### 3. 10% seeds the crystal, training grows it

The backbone (10%) is enough for the crystal to nucleate. But we
want to capture as MANY universal lattice points as possible. The
more we initialize and constrain, the less work GD has to do:

```
λ seed_crystal(backbone).
  initialize(backbone_geometry) → starting_point
  relational_loss(backbone_pairs) → soft_constraint
  ¬freeze | ¬clamp | ¬force
  crystal(grows) from seed, shaped by sieve
  GD fills in sieve-compatible encoding around backbone
```

### 4. Don't force the shape

VSM-LM has a different sieve than Qwen3-14B. The crystal WILL form
differently. Initialize where the data says, then penalize deviation.
If the sieve genuinely needs to shift a backbone distance, the CE loss
can overcome the relational pull.

## Architecture

### Anchor Vectors (MDS Embedding)

Classical MDS of consensus RDM → d_model anchor vectors:

```
807 probes × 512 dimensions
Backbone reconstruction correlation: 0.987
Full lattice reconstruction correlation: 0.898
Variance explained at d=512: 94.2%
```

The backbone is easier to embed than the full lattice — at d=32,
backbone correlation is already 0.958 while full lattice is only 0.788.
Universal structure is lower-dimensional than model-specific structure.

Artifact: `lattice/backbone_seed.npz`
- `anchor_vectors`: (807, 512) float32 — MDS embedding
- `backbone_mask`: (807, 807) float32 — binary backbone indicator
- `agreement_weights`: (807, 807) float32 — continuous agreement
- `consensus_rdm`: (807, 807) float32 — target distances

### Two-Tier Relational Loss

```python
def seed_crystal_loss(student_rdm, target, backbone_mask, agreement_weights,
                      backbone_lambda=1.0, growth_lambda=0.1):
    """Two-tier relational loss: seed + growth.
    
    Tier 1 (backbone): High weight on backbone pairs.
    These are the universal distances — strong pull to stay near them.
    
    Tier 2 (growth): Normal agreement-weighted loss on all pairs.
    These provide gradient for crystal growth around the backbone.
    """
    diff = (student_rdm - target) ** 2
    
    # Tier 1: backbone fixed points (strong pull)
    backbone_loss = (diff * backbone_mask).sum() / (backbone_mask.sum() + 1e-8)
    
    # Tier 2: full lattice growth (agreement-weighted, softer)
    growth_loss = (diff * agreement_weights).sum() / (agreement_weights.sum() + 1e-8)
    
    return backbone_lambda * backbone_loss + growth_lambda * growth_loss
```

The backbone_lambda >> growth_lambda ratio controls rigidity:
- High ratio: backbone distances are nearly fixed, crystal grows around them
- Low ratio: backbone is a suggestion, sieve has more freedom
- Start high, anneal down as crystal forms

### Initialization via Anchor Vectors

The anchor vectors tell us what the model's hidden states SHOULD
look like for each probe at the start of training. We can't directly
set hidden states (they're computed), but we can:

1. **Project anchors through inverse embedding**: Find weight
   initialization that produces representations near anchor vectors
   when probes are fed through. This is a linear problem if we
   fix the embedding layer and solve for the first-layer weights.

2. **Soft anchor loss at step 0**: Use the MDS coordinates as
   additional targets for the very first few training steps, with
   high weight. The model quickly snaps to the right geometry.

3. **Let the relational loss handle it**: The simpler approach —
   don't try to initialize weights magically. Just start training
   with the two-tier relational loss active from step 0. The
   backbone pairs pull the model toward universal geometry. The
   MDS embedding shows the geometry EXISTS at d=512 — GD will
   find it if pushed.

Option 3 is the right starting point. The relational loss IS the
initialization mechanism — it pulls the model toward universal
geometry from the first step. Options 1-2 are optimizations if
convergence is too slow.

### Etch Integration

```
Round N:
  1. EXPOSE — accumulate CE gradients from all 8 ops (existing)
  2. LATTICE — compute two-tier relational loss:
     a. Backbone: strong pull on universal distances (tier 1)
     b. Growth: agreement-weighted pull on all distances (tier 2)
     c. Accumulate lattice gradients into direction accumulators
  3. ETCH — flip confident positions (existing)
  4. BEAM TRAIN — GD on continuous params (existing)
```

The backbone loss acts as a constant reference beam. Even as the
etch carves the plates and GD adjusts the beams, the backbone
distances resist being moved. The crystal nucleates around them.

## What We Do NOT Etch

Tool-calling structure (51.9% agreement) and prose style (40.1%)
are sieve-dependent. VSM-LM's sieve is fundamentally different
from any source model — it has:
- Ternary plates (discrete sieve)
- 7-pass hourglass (multi-read angles)  
- Separated routing (mirrors) and compute (plates)
- Register bank system

These architectural features define a DIFFERENT sieve. The crystal
that forms will encode tools/prose differently than Qwen3 or Pythia.
Trying to force Qwen3's tool encoding would fight the sieve.

The backbone (math, reasoning, lambda×math bridges) IS universal.
These distances are properties of language. They'll be the same
in VSM-LM's crystal because they're the same in every crystal.

## Attachment Points

The backbone is not uniform — it has internal structure:

```
Backbone anatomy (32,522 pairs):
  Crystal       60.8%  — universal×universal same-domain (math-math, reasoning-reasoning)
  Bridge         9.1%  — universal×universal cross-domain (math↔reasoning)
  Attachment    19.0%  — universal×operational (lambda→math, code→reasoning)
  Operational    6.8%  — operational×operational where models agree
  Other          4.2%

Attachment point types:
  lambda → math        4,904 pairs  (79% of all attachment)
  code → math          1,117 pairs  (18%)
  tools → math           113 pairs  (1.8%)
  lambda → reasoning      49 pairs  (0.8%)
```

Agreement levels:
- Crystal pairs: 0.76 average agreement
- Attachment pairs: 0.67 average agreement
- Operational pairs: 0.76 average agreement

**Attachment points are where kernel functions connect to universal
structure.** Models disagree on lambda-lambda distances (sieve-dependent)
but AGREE on lambda-math distances (universal). The kernel functions
don't float free — they attach to the crystal at these bridge points.

The beam former must protect attachment points with the same priority
as crystal positions. Break an attachment point and the kernel structure
detaches from the universal crystal.

## Holographic Beam Former — Phased Etch

### Phase 1: Crystal Etch (single beam)

Lattice-only. No kernel CE loss. Burns universal crystal geometry
into the plate. Clean single-beam exposure.

```
Round 1..C:  [crystal beam] ──→ plate
             lattice loss only, no CE
             Installs: crystal + bridges + attachment points
```

### Phase 2: Kernel Etch (beam former active)

Kernel CE loss provides the kernel beam. Crystal lattice loss continues
as live reference beam. Beam former merges before hitting the plate.

```
Round C+1..N:  [crystal beam] ──┐
                                ├── beam_form ──→ plate
               [kernel beam] ──┘
```

The crystal beam acts as a holographic stencil:
- Where crystal etched confidently → protected (kernel can't overwrite)
- Where crystal is blank → kernel writes freely
- Where they agree → reinforced (stronger etch)
- Attachment points protected like crystal (they're the bridges)

Implementation: separate accumulator sets, merged before etch.

```python
# Phase 2 round:
reset(crystal_acc)
reset(kernel_acc)
accumulate(lattice_loss → crystal_acc)   # crystal reference beam (live)
accumulate(CE_loss → kernel_acc)          # kernel beam (all 8 ops)
merged = beam_form(crystal_acc, kernel_acc)
etch(merged)                              # coherent exposure
```

Beam form per plate position:
```python
crystal_conf = crystal_acc.confidence[i,j]
crystal_dir  = crystal_acc.direction[i,j]
kernel_dir   = kernel_acc.direction[i,j]

if crystal_conf > threshold:
    # Crystal/attachment position — protected
    # Kernel can reinforce but not oppose
    if sign(kernel_dir) == sign(crystal_dir):
        merged = crystal_dir + kernel_dir   # reinforcing
    else:
        merged = crystal_dir                 # crystal wins
else:
    # Blank plate — kernel writes freely
    merged = crystal_dir + kernel_dir        # both contribute
```

## Validation: 6-Model Consensus (in progress)

Running lattice build with 6 models to test whether attachment points
hold with additional architectures:
- Existing 4: qwen3-14b, mistral-7b, olmo-2-13b, pythia-2.8b
- New: smollm3-3b (HuggingFace), phi-4-mini (Microsoft)

If lambda→math attachment points maintain high agreement across 6
independently trained models, they're genuinely universal — the shape
of language, not any sieve. This would confirm the beam former design.

## Open Questions

1. **backbone_lambda schedule**: Start high and anneal? Or constant?
   Constant is simpler. Annealing lets the crystal relax into the
   sieve's natural shape after nucleation.

2. **Depth selection**: Currently using depth=50% (mid-network).
   Should backbone targets be at multiple depths? The spine
   finding shows PC1 is stable from 19-37 in Qwen3 (49-95%),
   but VSM-LM's stability zone may be different.

3. **Probe sampling**: Currently sampling 50 probes per round.
   Should backbone probes be sampled more frequently than
   non-backbone probes? Or should every round include a minimum
   number of backbone probes?

4. **Convergence indicator**: How do we know the crystal has
   nucleated? When backbone_loss stabilizes → seed has taken hold.
   When growth_loss starts decreasing → crystal is extending.

5. **Backbone expansion**: As training progresses, more pairs may
   converge to universal distances (the crystal grows). Should the
   backbone_mask expand dynamically? Or is the initial 10% fixed?

6. **Crystal etch rounds**: How many rounds of crystal-only etch
   before switching to kernel etch? Need the crystal to be firmly
   installed. Measure: backbone loss convergence → crystal is set.

7. **Beam former threshold**: What crystal confidence level triggers
   protection? Too low → protects noise. Too high → only protects
   the strongest crystal positions, leaving attachment points exposed.
</content>
</invoke>