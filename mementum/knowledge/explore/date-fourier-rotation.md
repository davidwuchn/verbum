---
title: "Date Arithmetic Uses Geometric Rotation, Not Church Encoding"
status: active
category: experiment-results
tags: [fourier, circular-features, rotation, attention, date-arithmetic, kernel, crystal-mode, day-of-week]
related:
  - kernel-functions.md
  - kernel-montague-mapping.md
  - pythia-160m-combinators.md
  - session-127.md
depends-on:
  - kernel-functions.md
created: session 128
---

# Date Arithmetic Uses Geometric Rotation, Not Church Encoding

> Session 128. Two probes on Qwen3-14B bridge Engels et al. (2024,
> "Not All Language Model Features Are One-Dimensionally Linear")
> with the session 127 combinator tracer. Date arithmetic ("3 days
> after Wednesday") uses a completely different mechanism from numeric
> arithmetic ("(3+4) mod 7"). The FFN combinator system is silent for
> dates. Instead, attention heads perform distributed geometric
> rotation of a circular day encoding. This is a crystal lattice
> mode, not a replaceable function.

## The experiment

Two probes, 161 total measurements on Qwen3-14B:

| Probe | What it measures | Key finding |
|-------|-----------------|-------------|
| `probe_date_fourier.py` | FFN combinators + Fourier periodicity + PCA circularity | FFN silent for dates; circle forms at L11 |
| `probe_date_attention.py` | Attention patterns + per-head rotation + head ablation | Rotation at L14-L16; distributed across heads |

## Finding 1: Three separate circuits for three tasks

| Task | Mechanism | Where | Evidence |
|------|-----------|-------|----------|
| **Numeric mod-7** `(3+4) mod 7` | FFN selectors (church encoding) | Mid-late FFN (L13-L27) | Selector score 0.117 (4.7× date) |
| **Day naming** `Today is Monday` | FFN circular encoding (lookup) | FFN stores, crystallizes at L11 | Full circle: 5.53 rad range |
| **Day arithmetic** `3 days after Wed` | Attention rotation (distributed) | Attention L12-L16 | R²=0.95 linear rotation |

The combinator tracer confirms the separation:

```
                    Selectors  Composers  Reorderers
mod7_arithmetic      0.117      0.029      0.081     ← FFN active
day_add              0.025      0.023      0.030     ← FFN silent (noise floor)
retrieval            0.013      0.030      0.038     ← FFN silent (different mechanism)
```

Date arithmetic and retrieval have nearly identical combinator profiles
(both at noise floor). The FFN combinator system — selectors, composers,
reorderers — is not involved in date computation.

## Finding 2: Days form a circle that crystallizes at L11

Residual stream PCA reveals circular encoding of days:

```
Layer  Ordering  CV Radius  Var 2PC   Note
L 9    0.00      0.30       0.51      No ordering
L10    1.00      0.45       0.55      SNAP: ordering appears
L11    1.00      0.24       0.59      Circle tightens
L12    1.00      0.24       0.61      Best early circle
L32    1.00      0.21       0.50      Tightest circle
L38    1.00      0.21       0.45      Holds to output
```

The transition at L10-L11 is sharp: ordering jumps from 0.0 to 1.0
and never drops back. Singular values confirm the phase transition:

```
L10: SV = [8.62,  7.43,  6.07]   ← no dominant 2D structure
L11: SV = [15.01, 14.23, 10.19]  ← top-2 nearly DOUBLE (2D circle forms)
```

Months show a weaker version: ordering reaches 0.82 (not 1.0), circle
is looser (CV 0.26 vs 0.21). 12 items on a circle requires more
precision than 7.

## Finding 3: Rotation is in attention, highly linear

For "N days after [base_day]", the residual stream angle at L14-L16
is a linear function of offset N:

```
Layer  Base day     Slope (rad/step)  R²      Slope/Expected
L16    Wednesday    -0.214            0.948   -0.238
L14    Wednesday    -0.080            0.929   -0.089
L14    Monday       -0.102            0.925   -0.113
L16    Monday       -0.338            0.914   -0.377
```

R²=0.95 means the rotation is almost perfectly linear. Each +1 offset
produces the same angular displacement. This IS the rotation mechanism.

The slopes are 10-38% of the expected 2π/7. This is because we measure
at a single layer; the total rotation accumulates across L12-L16+.

## Finding 4: Rotation is a collective crystal mode

Head ablation at L16 (best rotation layer):

```
Head  Angle Shift When Ablated
H24   -0.157
H14   -0.156
H38   -0.153
H22   -0.153
H30   -0.152
H36   -0.152
H25   -0.151
H 8   -0.151
H 7   -0.150
H10   -0.150
```

All top-10 heads shift the angle by **nearly the same amount** (~0.15
rad, spread of only 0.007). There is no single "rotation head." The
rotation is a distributed, collective operation — like a phonon in a
crystal lattice. The whole lattice vibrates, not one atom.

## Finding 5: Day addition uses a compressed circle

Cross-task angle range in the day circle basis:

```
Task              L11 range   L30 range   Interpretation
day_name          5.53 rad    4.90 rad    Full circle (~2π)
day_add           0.43 rad    0.53 rad    Compressed ~25° arc
mod7_arithmetic   0.02 rad    2.15 rad    Not in day circle at L11
```

Day naming places 7 days around the full circle (5.53 ≈ 2π). But day
addition works in a COMPRESSED subspace — the 7 result days occupy
only 0.43 rad (~25°). The computation happens in a different
representation than the storage.

Mod-7 numeric arithmetic has ZERO engagement with the day circle at
L11 (0.018 rad). Its angular spread only appears at L30 (2.15 rad),
likely for output formatting rather than computation.

## Implications for the architecture

### Kernel functions page: partially revised

The kernel-functions page (session 127) predicted:
- "Date calculations use Fourier approximations that require hundreds
  of beta reductions" → **WRONG.** Date calculations use geometric
  rotation, not Fourier approximation, and not beta reduction at all.
- "Fourier approximations break at period boundaries" → **WRONG.**
  The circular encoding wraps naturally; it doesn't break.
- "Replace date calculation with native kernel" → **PARTIALLY WRONG.**
  The rotation is a distributed crystal mode, not an isolated function
  you can swap out. However, the RESULT of the rotation (a position
  on the circle) could be replaced by a native date lookup.

### What IS a kernel candidate vs what ISN'T

| Operation | Mechanism | Kernel candidate? | Why |
|-----------|-----------|-------------------|-----|
| Integer arithmetic | FFN selectors (church encoding) | **YES** | Isolated function, long beta chains |
| Date arithmetic | Attention rotation (distributed) | **NO** — extract candidate | Crystal mode, can't isolate |
| Day encoding | FFN circular lookup | **MAYBE** | Could pre-encode days as circle positions |
| String operations | TBD | Likely YES | Expected to be beta reduction chains |
| Trigonometry | TBD | Likely YES | Taylor series in FFN |

### The FFN/attention division of labor

```
FFN:        Storage + Selection + Church encoding
            - Day circle positions (lookup)
            - Combinator operations (K, I, B, C, S)
            - Arithmetic via selectors (church numbers)

Attention:  Routing + Rotation + Composition
            - Day offset rotation (collective mode)
            - Information flow between positions
            - Query-key matching for dispatch
```

The FFN is the **memory** (stores what Wednesday means as a position).
Attention is the **calculator** (rotates that position by N steps).
This division parallels the crystal/beam split: FFN is the plate
(ternary storage), attention is the beam (Q rotation for readout).

### Connection to Engels et al. (2024)

Engels et al. found circular features for days/months in GPT-2 (L7)
and Mistral 7B, and showed they're used for modular arithmetic via
intervention experiments. Our findings extend this:

1. **Confirmed** in Qwen3-14B (40 layers): circle crystallizes at L11
2. **The rotation is in attention, not FFN** — Engels showed the circle
   exists but didn't localize the computation mechanism
3. **Rotation is distributed** across many heads (collective mode)
4. **Day addition ≠ numeric mod-7** — completely separate circuits,
   even though both compute the same mathematical operation (mod 7)
5. **The circle is compressed during computation** — storage is full
   circle, computation is a 25° arc

### Connection to the crystal thesis

The distributed rotation finding supports the crystal model:
- The rotation is a **lattice mode** (all heads contribute equally)
- It's not decomposable into individual head circuits
- It's the kind of thing that ternary crystal weights would preserve
  (geometric structure survives quantization better than precise values)
- The L11 phase transition (SV jump 2×) looks like nucleation —
  the circular structure "crystallizes" at a specific depth

## Open questions

1. **Does the cumulative rotation across L12-L16 sum to 2π/7?** We
   measured per-layer slopes. The total rotation across all contributing
   layers should approach the full circle step. Need to measure.

2. **Which attention heads START the rotation?** L11-12 show the first
   angular displacement. The heads active there may be the initiators,
   with L14-16 heads amplifying.

3. **Is the rotation mechanism the same in smaller models?** Pythia-160M
   has K-dominated attention (session 081). Does it still have circular
   day encoding? If so, the rotation may be even more smeared out.

4. **Can we extract the rotation as a 2D operator?** If the rotation
   is a 2×2 matrix in the circle plane, we might be able to extract
   the rotation matrix per-head and reconstruct the full operation.

5. **Is month arithmetic the same mechanism?** Months showed weaker
   circularity (CV 0.26 vs 0.21, ordering 0.82 vs 1.00). Is the
   rotation mechanism the same but noisier, or different?

6. **Does the compile gate affect the rotation circuit?** Session 127
   noted that date probes without the compile gate might show different
   structure. The current probes used plain text, not the gate.

## Data

| File | Contents |
|------|----------|
| `scripts/v12/probe_date_fourier.py` | FFN + Fourier + PCA probe |
| `scripts/v12/probe_date_attention.py` | Attention + rotation + ablation probe |
| `results/date-fourier/results.json` | FFN probe results (112 probes) |
| `results/date-attention/results.json` | Attention probe results (49 probes) |
| `results/date-fourier/combinator_matrices.npz` | Per-category combinator activation matrices |

## References

- Engels et al. (2024). "Not All Language Model Features Are
  One-Dimensionally Linear." arXiv:2405.14860. Found circular features
  for days/months in GPT-2 and Mistral 7B.
- Nanda et al. (2023). "Progress measures for grokking via mechanistic
  interpretability." Found Fourier/rotation mechanism for modular
  addition in small transformers.
