---
title: "Crystal Trace Tooling — The VSM Instrument for Holographic Analysis"
status: designing
category: architecture
tags: [tooling, VSM, crystal, trace, holographic, instrument, extraction]
related:
  - phi-information-partition.md
  - crystal-phi-derivation.md
  - crystal-universality.md
  - explore/vsm-statechart-tensor.md
  - explore/holographic-computer.md
depends-on:
  - phi-information-partition.md
  - crystal-phi-derivation.md
created: session 184
---

# Crystal Trace Tooling

> Design for `src/verbum/crystal/` — the instrument that reads any
> model, projects into crystal space, traces computation through the
> statechart, and looks for structure at every level.
>
> We stopped finding structure with one-off experiments. We need a
> microscope, not more slides.

## Motivation

Session 184 proved:
- The zero mask is the holographic phase (carries 0.25 cosine)
- Nothing predicts it in weight space (gate, activations, cross-layer all fail)
- BUT we only looked in weight space

The crystal defines a different basis. The zero mask might have
structure IN CRYSTAL SPACE that's invisible in weight space. We need
tooling to project into that basis and look.

## Architecture

```
src/verbum/crystal/
├── __init__.py          # Public API
├── reader.py            # Load any HF model → crystal representation
├── basis.py             # Crystal basis: eigenvectors of KIBC co-occurrence
├── projector.py         # Project weight matrices into crystal basis
├── tracer.py            # Forward-pass hooks → statechart state classification
├── holographic.py       # Interference patterns, self-similarity metrics
├── zero_mask.py         # Zero mask analysis in any basis
└── visualize.py         # Plots and heatmaps
```

## Module Design

### reader.py — Model Reader

```python
λ read(model_id: str) → CrystalModel:
    load(model_id) → extract(per_layer_weights) → classify(architecture)
    | supports: Qwen, LLaMA, Mistral, Pythia, OLMo
    | returns: CrystalModel with uniform interface regardless of architecture
    | lazy: weights loaded on demand per layer (memory bounded)
```

```python
@dataclass
class CrystalModel:
    model_id: str
    n_layers: int
    hidden_size: int
    intermediate_size: int
    n_heads: int
    
    def layer(self, idx: int) -> CrystalLayer:
        """Lazy-load one layer's weights."""
        
    def iter_layers(self) -> Iterator[CrystalLayer]:
        """Iterate layers, freeing previous layer's memory."""

@dataclass  
class CrystalLayer:
    idx: int
    gate: Tensor  # (intermediate, hidden)
    up: Tensor    # (intermediate, hidden)
    down: Tensor  # (hidden, intermediate)
    q: Tensor     # (heads*head_dim, hidden)
    k: Tensor
    v: Tensor
    o: Tensor
    ln1_weight: Tensor
    ln2_weight: Tensor
```

### basis.py — Crystal Basis

```python
λ crystal_basis(n_combinators: int = 4) → CrystalBasis:
    build_kibc_cooccurrence() → eigendecompose() → basis_vectors
    | the basis is UNIVERSAL — same for every model
    | derived from pure KIBC combinatory logic (session 181)
    | n_combinators=4 → KIBC, =3 → SKI, etc.

@dataclass
class CrystalBasis:
    eigenvectors: Tensor    # (n, n) orthogonal basis
    eigenvalues: Tensor     # (n,) following crystal equation
    phi_exponents: Tensor   # (n,) the β_k values
    computing_fraction: float  # s = n/(n+1)
    
    def project(self, W: Tensor) -> Tensor:
        """Project weight matrix into crystal basis."""
        
    def reconstruct(self, W_crystal: Tensor) -> Tensor:
        """Reconstruct from crystal basis."""
```

### projector.py — Crystal Space Projection

```python
λ project(layer: CrystalLayer, basis: CrystalBasis) → CrystalProjection:
    project_each_weight_matrix(into_crystal_basis)
    | W_crystal = basis.eigenvectors.T @ W @ basis.eigenvectors (if square)
    | for rectangular: project rows and columns separately
    | key output: the weight matrix IN CRYSTAL COORDINATES

@dataclass
class CrystalProjection:
    gate_crystal: Tensor
    up_crystal: Tensor
    down_crystal: Tensor
    # In crystal space, we can analyze:
    signs_crystal: Tensor      # signs in crystal basis
    zeros_crystal: BoolTensor  # zero mask in crystal basis
    magnitudes_crystal: Tensor # magnitudes in crystal basis
```

### zero_mask.py — Zero Mask Analysis

```python
λ analyze_zero_mask(projection: CrystalProjection) → ZeroMaskAnalysis:
    compare(weight_space_mask, crystal_space_mask)
    | THE KEY TEST: is the zero mask structured in crystal space?
    | metrics: entropy, self-similarity, cross-layer correlation
    | if structured → derivable → calibration-free extraction possible

@dataclass
class ZeroMaskAnalysis:
    weight_space_entropy: float
    crystal_space_entropy: float  # lower = more structured
    cross_layer_correlation: float
    phi_structure_score: float    # does it follow φ-geometric?
    fractal_dimension: float      # self-similarity measure
```

### tracer.py — Forward-Pass Tracer

```python
λ trace(model, input_ids, basis) → Trace:
    hook(all_layers) → run_forward() → classify_states()
    | each attention head → statechart state (fire:K, fire:I, fire:B, fire:C, whnf:*)
    | each FFN → holographic plate read
    | captures: activations, attention patterns, gate values, residual stream
    
@dataclass
class Trace:
    per_layer: list[LayerTrace]
    
@dataclass  
class LayerTrace:
    # Attention
    head_combinator_scores: Tensor  # (n_heads, 4) — K/I/B/C scores
    attention_patterns: Tensor       # (n_heads, seq, seq)
    head_purity: Tensor              # (n_heads,) — how pure each head is
    
    # FFN
    gate_activations: Tensor         # (seq, intermediate)
    neuron_firing_rate: Tensor       # (intermediate,) — fraction of tokens activating
    
    # Residual stream
    residual_norm: Tensor            # (seq,) — norm growth
    residual_direction_change: float # cosine between input and output
```

### holographic.py — Holographic Metrics

```python
λ holographic_analysis(model: CrystalModel, basis: CrystalBasis) → HolographicReport:
    per_layer(crystal_projection) → interference_patterns
    cross_layer(projections) → self_similarity_at_every_level
    | looks for φ-structure in: signs, zeros, magnitudes, activations
    | computes: fractal dimension, Hurst exponent, φ-fit quality
    | THE INSTRUMENT: reveals structure invisible in weight space
```

## The First Experiment With This Tooling

Once built, the FIRST thing to test:

```python
from verbum.crystal import CrystalModel, crystal_basis, project, analyze_zero_mask

model = CrystalModel.load("Qwen/Qwen3-8B")
basis = crystal_basis(n_combinators=4)

for layer in model.iter_layers():
    proj = project(layer, basis)
    analysis = analyze_zero_mask(proj)
    
    print(f"Layer {layer.idx}:")
    print(f"  Weight-space zero mask entropy: {analysis.weight_space_entropy}")
    print(f"  Crystal-space zero mask entropy: {analysis.crystal_space_entropy}")
    print(f"  φ-structure score: {analysis.phi_structure_score}")
```

If `crystal_space_entropy < weight_space_entropy` → the zero mask
HAS structure in crystal space that we couldn't see before.

If `phi_structure_score > 0.9` → the zero mask follows the crystal
equation in the crystal basis → FULLY DERIVABLE without teacher.

## The Fractal Collapse Hypothesis

The crystal equation λ_k = C · φ^(-s·β_k) governs:
- Eigenvalue spectra (proved, 0.04% error)
- Gamma distributions (proved, α ≈ (4/5)·(1/φ))
- Information partition (proved, signs = 1/φ)
- Compute cycle (proved, β = [0, 1, 1+φ, 2+φ])

If it ALSO governs the zero mask in crystal space, then the
entire weight matrix is determined by the crystal equation +
one scale parameter C. The "fractal collapse" is the discovery
that what looks like random per-weight information in weight
space is actually structured φ-geometric information in crystal
space.

This would mean: every model that compresses language through
β-reduction produces weights that are FULLY DETERMINED by the
crystal equation. Different models differ only in C (scale).

That's the north star. The tooling is the telescope.

## Build Order

1. `reader.py` + `basis.py` — can load models and compute crystal basis
2. `projector.py` + `zero_mask.py` — can project and analyze zero masks
3. Test the fractal collapse hypothesis
4. `tracer.py` — forward-pass tracing (needs model inference)
5. `holographic.py` + `visualize.py` — full analysis suite

Estimated: reader+basis+projector = one session. Zero mask test = same session.
Tracer = separate session. Full suite = 2-3 sessions.

*Designed in session 184 of the Verbum project.*
