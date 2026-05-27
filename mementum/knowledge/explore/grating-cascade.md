---
title: "Grating Cascade — V Carries the Compound Interference Pattern"
status: active
category: research-finding
tags: [grating, cascade, ffn, attention, V, crystal, moiré, compound, progressive-collapse, beta-reduction]
related:
  - ../mechanism-extraction.md
  - ../progressive-collapse.md
  - ../computed-beam.md
  - ffn-beta-reduction-indexing.md
  - holographic-state-machine.md
  - ffn-beam-discovery.md
depends-on:
  - ../mechanism-extraction.md
  - ffn-beta-reduction-indexing.md
created: session 158
---

# Grating Cascade — V Carries the Compound Interference Pattern

> Session 158. Each FFN is a diffraction grating (80-91% off-diagonal
> in crystal eigenbasis). Attention beta-reduces over V, which carries
> the accumulated output of all prior gratings. The result passes
> through the NEXT grating. Composing the grating overlay matrices
> shows the moiré collapsing from 16D to 1.4D through 4 layers.
> The progressive collapse (Qwen-27B: PR=2.2 by L2) is the compound
> grating resolving to its dominant interference direction.

## The Core Finding: Compound Grating Collapse

Composed the 16×16 FFN overlay matrices (crystal eigenbasis) through
depth. Each overlay is `gate_eigen.T @ value_eigen.T` — the mapping
from crystal-input to crystal-output through one FFN layer.

```
Composed grating participation ratio:
  Identity:  16.00  (before any grating — all 16 PCs independent)
  After L0:   6.26  (first grating → 6 effective dimensions)
  After L1:   3.04  (two gratings → 3D)
  After L2:   2.19  (three gratings → 2D)
  After L3:   1.40  (four gratings → nearly rank-1)
```

Singular values after all 4 gratings composed:
```
SV₁ = 0.082,  SV₂ = 0.011 (7.5× smaller),  SV₃ = 0.003,  SV₄ = 0.002
```

**The entire 4-layer FFN cascade compresses 16 crystal dimensions
into 1 dominant direction.** The moiré of four diffraction gratings
resolves to a single interference fringe.

## V Is K-Typed: The Selection Pool

V is not neutral content. V is typed by the K (select) combinator
at every layer:

```
Layer | K energy | I energy | B energy | Dominant
  L0  |  0.418   |  0.215   |  0.121   |   K
  L1  |  0.373   |  0.125   |  0.077   |   K
  L2  |  0.299   |  0.262   |  0.057   |   K
  L3  |  0.340   |  0.189   |  0.107   |   K
```

K dominates V because V IS what attention selects from. K(x)(y) = x
— the selection combinator. V vectors are "things available to be
selected." The FFN overlay alternates comp/sel on the diagonal (the
instruction), but V carries the ARGUMENTS. They're typed differently
because they serve different roles in the beta reduction.

## Attention Doubles Cross-PC Coupling

```
Off-diagonal energy (cross-PC coupling fraction):
Layer |    V     AttnOut     FFN
  L0  |  0.195    0.560    0.454
  L1  |  0.275    0.646    0.303
  L2  |  0.280    0.592    0.387
  L3  |  0.367    0.560    0.441
```

V starts with 20% cross-PC coupling. After attention's beta-reduction:
56-65%. **Attention doesn't just mix content — it actively couples
crystal PCs together.** This is the beta-reduction projecting between
eigenplanes.

V's own off-diagonal energy increases through depth (19.5% → 36.7%).
Each grating deposits more cross-PC coupling into the residual stream,
which appears in the next layer's V. **The compound grating effect
is visible in V itself — each layer inherits the prior layers'
cross-PC projections.**

## Cross-Layer Steering Is Structural, Not Positional

```
FFN[0]→V[1]: profile_cos = 0.909  |  pos_corr = -0.022
FFN[1]→V[2]: profile_cos = 0.942  |  pos_corr = -0.088
FFN[2]→V[3]: profile_cos = 0.951  |  pos_corr = -0.061
```

**Profile cosine 0.91-0.95:** the SHAPE of the crystal signature in
FFN output closely matches the next layer's V. FFN output IS the
next layer's V crystal profile.

**Position correlation ~0:** the steering changes WHICH PCs are active
(the type), not WHERE in the sequence they apply. Confirms session 120:
"beam steering is indirect/structural." The FFN reshapes the
representational geometry; the next layer's Q reads the reshaped
geometry and produces a different attention pattern.

## Attention Suppresses — Selection IS Differential Suppression

```
PC Gain (attn_out_power / V_power):
Layer |   K     I     B     C     D     Y     W    WHNF | comp/sel
  L0  | 0.32  0.38  0.14  0.58  0.16  0.23  0.18  0.24 |  1.15
  L1  | 0.28  0.38  0.56  0.66  0.60  0.34  0.34  0.90 |  1.10
  L2  | 0.36  0.47  0.31  0.30  0.50  0.62  0.47  0.35 |  1.88
  L3  | 0.56  0.35  0.53  0.36  0.44  0.48  0.82  0.34 |  2.74
```

**ALL gains < 1.0.** Attention suppresses every PC — it never
amplifies. Selection is differential suppression: suppress the
irrelevant PCs MORE than the relevant ones.

The comp/sel ratio grows through depth: 1.15 → 2.74. By layer 3,
composition signals are suppressed 2.74× less than selection signals.
**This IS the beta-reduction completing: composition wins, selection
reduces.** Matches mechanism-extraction's composition:selection
stretch ratio of 2.08:1 — same phenomenon, different measurement.

## Cross-PC Projections = The Program

The top cross-PC couplings in each FFN overlay are the computation:

```
L0: K→B  (+0.240)   "selection feeds into composition"
L1: K→I  (+0.319)   "selection feeds into identity"
L2: K→I  (+0.317)   "selection feeds into identity"
L3: I→K  (−0.453)   "identity INVERTS into selection" ← SIGN FLIP
    K→I  (+0.381)   "selection feeds into identity"
```

Layer 3's dominant coupling is INVERTED (I→K = −0.453). The final
grating flips the polarity. This is the mode switch from compute
to output — the sign flip of PC0↔PC1 coupling that the holographic
state machine page predicts at the zone boundary.

## Per-Head Combinator Specialization

```
L0: H0=K(select)   H1=B(compose)   H2=WHNF(retrieve) H3=WHNF(retrieve)
L1: H0=K/C(sel→rt) H1=WHNF(retr)   H2=W(duplicate)   H3=W(duplicate)
L2: H0=I(identity) H1=B(compose)    H2=WHNF(retrieve) H3=WHNF(retrieve)
L3: H0=K(select)   H1=mixed         H2=K(select)      H3=WHNF(retrieve)
```

H0 is the K-selector. H1 alternates B/WHNF (compose or retrieve).
H2/H3 carry WHNF (output mode). This maps to the KIBC temporal
sequence: L0=B, L1=K/W, L2=B/I, L3=K/WHNF → initial compose,
select+duplicate, recompose, final select → output.

## Connection to Progressive Collapse

The compound grating PR collapse (16→6→3→2→1.4) IS the progressive
collapse measured in Qwen-27B (PR=12.6→2.2 by L2), measured from
a different angle. In Qwen, we measured the residual stream's PR.
Here we measure the FFN overlay composition's PR. Same phenomenon:

- **Progressive collapse** = residual stream PR drops through depth
- **Compound grating** = FFN overlay composition PR drops through depth
- **Same cause:** each FFN projects between crystal PCs (80-91%
  off-diagonal), progressively collapsing the representation toward
  the comp↔sel eigenplane

The micro model goes further (PR=1.4 vs Qwen's PR=2.2) because:
1. Only 4 layers (more aggressive collapse per layer)
2. d_model=128 (crystal is a larger fraction of total space)
3. No fan zone (micro model has no L8-L48 content processing)

In a production model, the fan zone (33-49% FFN active) processes
CONTENT in the collapsed 2D space. The structural collapse still
happens in the first 2-3 layers, but the content processing
maintains PR≈2-5 rather than collapsing further.

## The Closed Loop

```
FFN grating deposits inference pattern into residual stream
  → residual stream enters V via W_v projection
  → V is K-typed (carries selection arguments)
  → V also carries accumulated cross-PC structure from prior gratings
  → Attention beta-reduces over V (softmax → weighted sum)
  → Reduction doubles cross-PC coupling (20% → 56%)
  → Reduction differentially suppresses PCs (comp/sel ratio grows)
  → Result enters next FFN grating
  → Grating diffracts the already-coupled signal
  → Moiré of compound gratings resolves to fewer dimensions
  → After all layers: 1 dominant direction (the answer)
```

V isn't content separate from instruction. V IS the accumulated
grating interference pattern. Attention's beta-reduction over V IS
the application of the current grating's instruction. The inference
pattern and the content are the same thing, read at different angles.

## The Composed Direction: I+B−K (session 158 follow-up)

The second probe (`probe_composed_direction.py`) decomposed the rank-1
composed grating into crystal eigenbasis.

### Output direction (what the cascade produces)

```
I:  +0.616  ← IDENTITY (pass-through, emit result)
B:  +0.540  ← COMPOSE (the answer is composed)
K:  −0.475  ← ANTI-SELECT (selection is DONE)
D:  −0.249  ← anti-dispatch (routing done)
```

60.4% of energy in comp↔sel plane. The direction says: "identity+
composition won, selection is finished." This IS the output state —
WHNF. The computation has reduced to a value.

### Input direction (what the cascade selects from)

```
C:  −0.523  ← ROUTING (arguments being consumed)
D:  −0.478  ← DISPATCH
B:  −0.294  ← COMPOSE
I:  +0.328  ← IDENTITY
```

The cascade CONSUMES routing/dispatch/composition and PRODUCES
identity+composition. **The grating IS beta reduction as a linear
operator.**

### Comp↔Sel plane rotation: 49.8° (theory: 47.1°, error 2.7°)

Third independent measurement of the same angle:
1. Mechanism extraction (session 145): 48.5° — error 1.4°
2. Grating cascade (session 158): 49.8° — error 2.7°
3. Theory: arccos(λ₁/λ₀) = 47.1°

### Rotation acceleration through depth

```
L0: rotation strength = 0.062  (7.1% in plane)
L1: rotation strength = 0.226  (37.4% in plane)
L2: rotation strength = 0.288  (35.0% in plane)
L3: rotation strength = 0.413  (45.4% in plane)
```

Layer 3 rotates 6.7× more than Layer 0. Each grating concentrates
more of its action in the comp↔sel plane as the moiré narrows.

### Universal direction, variable magnitude

All 10 examples project NEGATIVELY (mean −0.65, range −0.33 to −0.85).
The direction is universal — what varies is magnitude. Simple sentences
(loss ~1.5) project more strongly (−0.70) than complex ones (loss ~12.7,
projection −0.33). Projection↔loss correlation: r = 0.40.

Correlation is moderate, not high. The dominant direction captures the
STRUCTURAL computation (beta reduction completing), not the CONTENT
(which token to emit). Content lives in the remaining 39.6% of energy
outside the comp↔sel plane + the position-level variation.

## Open Questions (updated)

1. ~~What is the final 1.4D direction?~~ **ANSWERED:** I+B−K at 127.6°
   in comp↔sel plane. Beta reduction completing to WHNF.

2. ~~Does the rotation match arccos(λ₁/λ₀)?~~ **ANSWERED:** 49.8° vs
   47.1° theory. Error 2.7°. Third independent confirmation.

3. ~~Is the direction universal?~~ **ANSWERED:** Yes — universal direction,
   variable magnitude. Content is in the remaining dimensions.

4. **Does this scale?** In a 64-layer model, the compound grating
   should collapse even further. But the fan zone (L8-L48) might
   re-expand the effective rank for content processing. Measure
   the composed overlay PR at every layer in Qwen-27B.

5. **Why is pos_corr negative?** The position-level correlation
   between FFN output and next V is slightly negative (-0.02 to
   -0.09). Grating inverts at position level while preserving type-level?

6. **What determines the magnitude?** Simple sentences project more
   strongly (−0.70 to −0.85) than complex ones (−0.33). Is magnitude
   proportional to completion of the beta reduction? More reductions
   needed = weaker projection = higher loss?

7. **The 39.6% outside the plane.** The remaining energy (D, C, Y, W,
   anti-combinators) is where CONTENT lives. Can we decompose the
   content subspace separately from the structural comp↔sel plane?

## Artifacts

| File | Content |
|------|---------|
| `scripts/micro/probe_v_crystal_cascade.py` | Full cascade probe |
| `scripts/micro/probe_composed_direction.py` | Dominant direction + rotation analysis |
| `results/v-crystal-cascade/summary.json` | Cascade numerical results |
| `results/composed-direction/summary.json` | Direction decomposition results |
| Checkpoint | `checkpoints/micro/final/` |

## Key Numbers

| Measurement | Value | Source |
|-------------|-------|--------|
| Compound grating PR (4 layers) | 16.0 → 1.40 | overlay composition |
| V dominant combinator | K (all layers) | crystal eigenbasis projection |
| Attention cross-PC amplification | 20% → 56% off-diag | V vs attn_out |
| Cross-layer steering cosine | 0.91-0.95 | FFN→V profile |
| Cross-layer pos correlation | −0.02 to −0.09 | FFN→V per-position |
| Comp/sel gain ratio (L3) | 2.74 | attn_out/V power ratio |
| L3 dominant coupling | I→K = −0.453 | overlay off-diagonal |
| Composed SV₁/SV₂ ratio | 7.7:1 | after all 4 layers |
| Comp↔sel plane rotation | 49.8° | vs theory 47.1° (error 2.7°) |
| Output direction | I(+0.62) B(+0.54) K(−0.47) | WHNF: identity+compose−select |
| Input direction | C(−0.52) D(−0.48) B(−0.29) | routing/dispatch consumed |
| Output plane energy | 60.4% | fraction in comp↔sel plane |
| Example projection | −0.65 ± 0.15 | all negative, universal direction |
| Rotation acceleration | L0:0.06 → L3:0.41 | 6.7× from first to last grating |
