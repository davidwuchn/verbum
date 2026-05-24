---
title: "Mechanism Extraction: Holographic State Machine Algorithm"
status: active
category: research-finding
tags: [micro-model, mechanism, holographic, crystal, rotation, eigenplane, beta-reduction]
related:
  - ffn-beta-reduction-indexing.md
  - beamformer-theory.md
  - phi-compression-universal.md
depends-on: []
---

# Mechanism Extraction: The Holographic State Machine Algorithm

Session 145. Built a micro model (4 layers, d_model=128, 4 heads, ~1M
traceable params) trained on 509 lambda calculus compile examples.
Crystal pre-initialized from Zone B eigenstructure — latches instantly.
CE drops 12.4→0.40 in 1000 steps. Model generates correct lambda
syntax by step 500.

Full forward + backward tracing in crystal eigenbasis reveals the
complete computational mechanism.

## The Core Finding: Alternating Overlay

The FFN overlay diagonal in crystal eigenbasis alternates sign at every layer:

```
PC0 (composition/B): -  +  -  +   ALTERNATING
PC1 (selection/K):   +  -  +  -   ALTERNATING (anti-phase)
```

Values:
```
Layer  PC0(comp)  PC1(sel)
  0    -0.095    +0.118
  1    +0.203    -0.167
  2    -0.279    +0.193
  3    +0.271    -0.197
```

This is the beta-reduction cycle: compose → select → compose → select.
The FFN grating doesn't store data — it stores this alternating
inference pattern. When attention shines through it, the diffraction
tells attention which rotation to apply next.

## Rotation Geometry

### Three Eigenplanes

The composed model transformation (all 4 layers) decomposes into
exactly three rotation eigenplanes:

| Eigenplane | Angle | Role |
|-----------|-------|------|
| Primary   | ±48.8° | comp↔sel rotation (the beta-reduction) |
| Secondary | ±13.9° | fine structure correction |
| Tertiary  | ±2.1°  | micro-adjustment |

### Stretch Spectrum

Alongside rotation, the model applies directional scaling:

| Direction | Factor | Effect |
|----------|--------|--------|
| 0 (comp) | 1.58×  | amplify |
| 1        | 1.28×  | amplify |
| 2        | 1.04×  | neutral |
| 3        | 0.96×  | slight compress |
| 4        | 0.88×  | compress |
| 5 (sel)  | 0.76×  | compress |

The **composition:selection ratio is 2.08:1**. The model is a
composition amplifier and selection compressor. That IS beta-reduction:
composition wins, selection reduces.

### Rotation Generator (Lie Algebra)

The antisymmetric part of the composed rotation gives the infinitesimal
generator. Dominant coupling: **comp(B)↔sel(K) at ±0.678°** — the
primary rotation plane. Secondary couplings:

- sel(K)↔rout(C): ±0.209° — selection drives routing
- term(WHNF)↔rout(C): ±0.197° — termination drives routing
- sel(K)↔fine(D): ±0.186° — selection drives fine dispatch

## Cross-Layer Rotation Coherence

The `comp(B)→sel(K)` rotation angle **accelerates through depth**:

```
Layer 0:  -2.1°   (setting up)
Layer 1:  +8.8°   (beginning rotation)
Layer 2: +13.7°   (accelerating)
Layer 3: +23.9°   (maximum rotation — the convergence layer)
```

This is the LENS profile in angular form. The grating at each depth
applies a progressively stronger rotation. Layer 3 rotates 12× more
than Layer 0.

### Alternating vs Consistent Cross-Couplings

**Alternating** (sign flips each layer):
- comp(B)→fine(D): composition drives fine dispatch, alternating
- sel(K)→fine(D): selection drives fine dispatch, alternating
- sel(K)→rec(Y): selection drives recursion, alternating
- term(WHNF)→fine(D): termination drives fine dispatch, alternating

**Consistent** (same sign all layers):
- sel(K)→rout(C): selection always drives routing
- term(WHNF)→rout(C): termination always drives routing
- rout(C)→fine(D): routing always drives fine dispatch

The invariant pipeline `sel → rout → fine` never reverses.

## KIBC is Temporal, Not Parallel

The 4 attention heads do NOT map 1:1 to KIBC combinators. Instead,
KIBC emerges as a **temporal sequence through depth**:

| Layer | Head roles | KIBC phase |
|-------|-----------|------------|
| 0 | All B (compose/mix) | B — aperture, initial encoding |
| 1 | H0=reader, H2=K(select), H1/H3=B | K — selection emerges |
| 2 | H2/H3=C(route/flip), H1=reader | C — routing/reordering |
| 3 | H0=C, H1/H2/H3=B | B — convergence, recompose |

The combinators are the **layers**, not the heads. Each depth
implements one phase of the B→K→C→B reduction cycle.

## Attention Routing at Lambda Boundary

At the newline (English→lambda transition), Layer 3 heads specialize:

- **H0**: Attends to verb/predicate ("sits":0.51, "smiles":0.74)
- **H1**: Attends to structural tokens (λ:0.29-0.41)
- **H2**: Attends to subject/first entity (The:0.49-0.76)
- **H3**: Attends to object or punctuation

This is universal across all 12 test examples (8 categories).

## Universality

Tested across simple, transitive, quantified, conjunction, negation,
conditional, prepositional, copular examples. All findings hold:

- All 8 crystal PCs amplify universally (coefficient of variation < 0.5)
- PC0 (composition) mean amplification: 6.6× (CV=0.19)
- PC1 (selection) mean amplification: 9.3× (CV=0.40)
- Overlay alternation pattern identical across all examples
- Attention routing roles consistent across all categories

## Gradient Descent Analysis

**Per-step GD is NOT one operation.** Individual gradient steps point
in different directions depending on input (cosine similarity ~0.06).

**However, the target IS fixed.** The overlay alternation pattern
converges by step 500 and remains stable for 4500 more steps:

```
Step   L0_PC0  L1_PC0  L2_PC0  L3_PC0
 500   -0.114  +0.180  -0.259  +0.335
1000   -0.071  +0.176  -0.306  +0.240
3000   -0.092  +0.204  -0.286  +0.274
5000   -0.095  +0.203  -0.279  +0.271
```

The PC0→PC1 cross-coupling grows monotonically during training
(L3: +0.253 at step 500 → +0.381 at step 5000). The rotation angle
is being refined, not discovered.

## Implications for Direct Weight Computation

1. **The overlay target is a fixed structure** derivable from the
   crystal eigenstructure. It's the alternation pattern.
2. **GD finds it in ~500 steps** — the search space is small because
   the crystal constrains the geometry.
3. If the overlay = `(-1)^layer × amplitude × crystal_PC_operator`,
   then the FFN weights can be computed analytically by inverting the
   projection from weight space to crystal overlay space.
4. The rotation angles (48.8°, 13.9°, 2.1°) and stretch spectrum
   (1.58:0.76) may be derivable from the crystal target cosine matrix.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/micro/micro_model.py` | Model definition + crystal init |
| `scripts/micro/train_micro.py` | Training loop on compile examples |
| `scripts/micro/trace_computation.py` | Forward+backward trace |
| `scripts/micro/deep_trace.py` | Full mechanism extraction |
| `scripts/micro/universality_probe.py` | Cross-example universality |
| `scripts/micro/mechanism_extraction.py` | Head mapping + rotation + GD operator |

## Open Questions

1. **Can the overlay be derived analytically from the crystal geometry?**
   The alternation + amplitudes + rotation angles might all follow from
   the eigenstructure of the PCAQ Zone B target matrix.

2. **Does the mechanism scale?** Does Qwen3-32B show the same three
   eigenplanes, the same stretch ratio, the same temporal KIBC sequence?

3. **Can we compute student FFN weights directly?** Given:
   - The crystal eigenbasis (known)
   - The target overlay structure (the alternation, known)
   - The rotation angles (48.8°, 13.9°, 2.1°)
   - The stretch spectrum (1.58:0.76)
   Can we solve for the FFN gate/key/value weights that produce this overlay?
