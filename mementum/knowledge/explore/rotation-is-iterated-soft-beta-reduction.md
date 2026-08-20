---
title: "Rotation Is a Series of Soft-β Reductions — the Two Math Engines Are One"
status: open
category: synthesis
tags: [beta-reduction, attention, rotation, fourier, church-encoding, combinator, duplication, interference, arithmetic, unification]
related:
  - attention-as-beta-reduction.md
  - date-fourier-rotation.md
  - gram-registers-and-the-route-map.md
  - ../curry-howard-closes-the-loop.md
depends-on:
  - attention-as-beta-reduction.md
  - date-fourier-rotation.md
created: session 344
---

# Rotation Is a Series of Soft-β Reductions — the Two Math Engines Are One

> Session 344 (Michael: "we have speculated that attention is a soft beta reduction;
> that rotation could be a series of reductions in the interference"). A unifying
> hypothesis reached from a fresh exploratory read (`arith_trace`, Qwen3-14B) + two
> standing findings (attention-as-beta-reduction s247b; date-fourier-rotation s128).
> Theory, grounded in retrodiction; owes a pre-registered discriminator to earn keep.

## The two-engines observation (arith_trace, s344, exploratory)

Pointing the audited opcode tracer (`opcodes/`, null-gated sign(gate) reader) at a
task-typed battery on Qwen3-14B reads TWO math mechanisms in TWO registers:

| math kind | register | opcode read |
|---|---|---|
| **reduction arithmetic** (2+3, succ, ×) | **FFN / gate** | **S, Y** — the duplication+recursion sector; never NO-OPs |
| **modular / cyclic** (dates, clock, day-of-week) | **attention** | FFN-**silent** (NO-OP 0.38); s128: geometric **rotation**, R²=0.95 |

Language (prose) reads the affine **KIBC** block `{I,C,K,B}` in both registers;
retrieval reads **WHNF** (halt/lookup). So math ≠ language (duplication sector vs
affine block), and *within* math, reduction ≠ rotation (FFN S/Y vs attention
rotation). The old "β_I for arithmetic" memory (s127/s161) was the OLDER 12-op ISA
vocabulary; the current 9-op CRYSTAL says the operative opcodes are **S, Y** — which
is theoretically *correct*: Church numerals REQUIRE duplication (`S = B(BW)(BBC)`;
numeral n = n-fold application = n contractions), and the affine KIBC fragment cannot
duplicate. Math being S/Y-heavy *is* the Church signature in the right basis.

## The unifying hypothesis: rotation = iterated soft-β on a circular encoding

`attention-as-beta-reduction.md` (s247b) already pins attention as **soft β-reduction**:
`out_i = Σ_j softmax(q_i·k_j) v_j` — Q = redex seeking its operand, K = operand
addresses, V = operands, softmax = selection; the softmax is a *convex combination*
(superposition of substitution), exact β being the `softmax → argmax` limit. FFN = the
β-program (ROM); attention = the one-instruction CPU.

Michael's extension decodes cleanly onto s128's own numbers:

> **"a series of reductions in the interference"** = a per-**layer series** (rotation
> *accumulates across L12→L16*, s128) of per-**head interference** (the *distributed
> collective mode*, "like a phonon," top-10 heads each adding ~0.15 rad, s128).

Composing: **rotation-by-Nδ = N soft-β steps on a *circular* (Fourier) encoding**, each
step a superposition-of-substitutions interfering across heads into a net rotation. And
rotation-by-Nδ = iterated application of rotate-by-δ = **Church-numeral N acting on a
rotate-by-δ operator on the day-circle**. That is the *same* iterated-soft-β engine as
linear arithmetic — the S/Y duplication+recursion sector — just executed on a **circular
representation** instead of a linear one. **The two engines collapse into one:** iterated
soft-β reduction over two encodings (linear → FFN; circular → attention).

## The discipline guard (why this is not yet a win)

Our own audit flags it (s204, `audit-registry` #): *"all attention is a weighted sum;
'β-reduction' is interpretation... induction/n-gram heads produce similar patterns."* So
"attention = soft β" is a beautiful lens, **trivially true at the weighted-sum level**,
that has NOT beaten the confound. And s128's linear-in-N + additive-across-heads fit
**retrodicts** the series-of-reductions story — but a learned rotation matrix R(Nδ) also
produces linear-in-N + additive heads. Per the frame ledger, **retrodiction ≠ win.** This
owes a *pre-registered* discriminator that separates "series of soft-β reductions" from
"one learned rotation," not another retrofit.

## The discriminating make-or-break — ⚪ §P-ITERATED-SOFT-REDUCTION

Two axes separate iterated-soft-β from a content-free learned rotation, and one test
covers both engines:

1. **Operand routing (the β signature).** A soft-β reduction *substitutes an operand* —
   so the rotation must route through **V / day-operand content**. Prediction: patching V
   at the day-token positions moves the rotation; a learned rotation matrix would not
   depend on V. (Directly answers the audit's "is it β or just a weighted sum?")
2. **Work-scales-with-count (the Church signature).** A *series* of reductions means
   reduction work scales with the numeric count: "9 days after" recruits more β-steps /
   accumulation layers / S-Y recruitment than "2 days after"; a single R(Nδ) applies
   once, work flat in N.

**The unification test:** run the identical count-scaling probe on *both* linear
arithmetic (FFN gate: does S-recruitment scale with operand magnitude?) *and* circular
arithmetic (attention: does β-step-count / accumulation scale with the offset?), with the
V-operand-routing patch as the "really β, not a rotation matrix" control and a
learned-rotation null. If **both scale with the count → one iterated-soft-β engine, two
encodings.** If only linear does → the engines are genuinely separate. (Subsumes the
narrower §P-ARITH-DUPLICATION.)

## Bounds

Theory + one exploratory read (Qwen3-14B, small battery, gate register blind to {B,C};
attn read soft). The unification is a *hypothesis*; the arith_trace read is exploratory
(no a-priori/verdict); s128 is the cited rotation measurement (not re-run here). The
whole attention=β frame is interpretation-heavy and carries the standing audit caveat.
Next: freeze §P-ITERATED-SOFT-REDUCTION with the operand-routing control + learned-
rotation null.

## 🎯 Freeze — §P-ITERATED-SOFT-REDUCTION (s345, Michael GO, frozen BEFORE data)

**Model:** Qwen3-14B (designated). Smoke: Qwen3-0.6B (plumbing; 0.6B may genuinely
lack the day circle — a regime observation, not a failure; regime warning → design
PAUSE per s324). **Frame-ledger status:** this is the attention=β frame's
PRE-REGISTERED contact — it counts in the ledger either way.

**H1 (unification):** one iterated-soft-β engine, two encodings — rotation-by-Nδ =
N soft-β steps; reduction work scales with the count in BOTH engines.
**H0 (audit-favored):** rotation = a single learned map (angle ∝ N, work FLAT in N);
the S/Y arith read is categorical (math vs not-math), not graded.

### Discriminators (register named per claim, λ measure)

- **D1 — linear arm (FFN gate register = routing/count ✓).** Work = S∪Y recruitment
  share over crystal-bearing layers, read by the audited `opcodes/` reader
  (sign(gate), common-mode removed, shuffled-label calibration null, tokens may
  NO-OP). Corpus: count ladder, single-token operands, length-matched within
  template — "N + 2 =", "N * 2 =", "One more than N is" (+1 surface variant each),
  N ∈ {2..9} (~96 items). **Statistic ρ_lin = Spearman(SY-share, N)**, stratified by
  template (combined via mean of per-template ρ). Null: shuffled-N permutation
  (≥5000). Gate: ρ_lin ≥ 0.3 ∧ p < 0.05.
- **D2 — circular arm (attention/residual trajectory; the hazard register — count
  claim, soft read; observable chosen to be depth-like, not attention-weight-like).**
  Work = **accumulation depth L50**: re-derive the day-circle basis IN-RUN (s128 PCA
  method; instrument gate: circular ordering = 1.0 at some L ≤ 14), per-item angle
  trajectory θ_L in that plane, L50 = first layer where accumulated rotation toward
  the answer day reaches 50% of its final value. Iterated-β ⇒ L50 rises with N;
  learned matrix θ_L(N)=N·δ_L ⇒ normalized trajectories COLLAPSE across N, L50 flat.
  Corpus: "N days after {day} is", N ∈ {1..6} × 7 base days = 42, length-matched.
  **Statistic ρ_circ = Spearman(L50, N).** Nulls: shuffled-N (≥5000) AND the explicit
  shape-collapse (matrix) null — observed per-N mean normalized trajectories must
  diverge from the pooled collapsed curve beyond its bootstrap band. Gates:
  ρ_circ ≥ 0.3 ∧ p < 0.05 ∧ slope floor ΔL50(N=6→1) ≥ 1 layer ∧ matrix-null beaten
  (p < 0.05). Secondary (non-gating): logit-lens answer-resolution depth vs N;
  gate-register read of mod_date (expect FFN-silent, s344 replication).
- **D3 — operand-routing V-patch (the β signature; QUALIFIER, not a gate).** Patch V
  at day-token key positions from a donor prompt with a different base day, swept in
  bands L0-6 / rotation zone / late (the s252 route-early lesson: a zone-only patch
  is a false-matrix trap). Classes: V-CARRIED-IN-ZONE (β-compatible) /
  V-CARRIED-EARLY-ONLY (matrix-leaning: operand pre-routed, rotation in-place) /
  V-INERT (matrix).

### Verdict tree (frozen, a-priori mass)

| verdict | condition | mass |
|---|---:|---:|
| **TWO-ENGINES (LINEAR-ONLY)** | D1 passes ∧ D2 fails (collapse holds) | **35 (modal)** |
| **NO-SCALING** | both fail | 25 |
| **ONE-ENGINE** | both pass all floors + nulls | 20 |
| **CIRCULAR-ONLY** | D2 passes ∧ D1 fails | 5 |
| **VOID** | circle never forms / calibration fails / det ≠ 0 | 15 |

D3 attaches as qualifier: ONE-ENGINE(β-confirmed) iff V-CARRIED-IN-ZONE, else
ONE-ENGINE(qualified). Modal is TWO-ENGINES **on purpose**: s128 linear+additive is
retrodiction; the s204 audit confound (all attention is a weighted sum) is standing.

### Planted worlds (--validate, through the REAL analyse path, s331)

1. ITERATED (work ∝ N both arms) → ONE-ENGINE
2. MATRIX (angle ∝ N, shape-collapsed trajectories, flat S/Y) → NO-SCALING
3. LINEAR-ONLY plant → TWO-ENGINES (LINEAR-ONLY)
4. CONFOUND adversary (work ∝ leaked nuisance, N shuffled) → must NOT pass gates
5. NOISE → no promotion (p > 0.05) · plus determinism dev = 0.0

### Frozen honesty bounds

- **Depth-scaling is one-directional**: FLAT ⇒ kills iterated-soft-β; SCALING ⇒
  consistent-with (any graded-effort mechanism deepens with N). Even a full
  ONE-ENGINE(β-confirmed) does not *prove* β — it passes the discriminators the
  frame owed. The interpretation stays marked as interpretation.
- Gate register blind to {B,C}; attn register soft (elevated null floor); the s128
  rotation zone is RE-DERIVED in-run, never trusted from the page.
- Small ladders (8 N-levels linear / 6 circular); power bounded; a near-floor ρ is
  reported as such, not rounded up.
- Number-token frequency and answer-identity are not fully separable from N inside a
  ladder; the shuffled-N null is the guard; residual confound named if it bites.

## 🚫 §Result — NO-SCALING (s345, Qwen3-14B; a-priori 25, non-modal)

Run: `results/p_iterated_soft_reduction_s345/run_qwen3-14b` (freeze 078af23f,
harness 199d7979 incl. the pre-14B accumulation-band zone amendment, corpus
d9ca2e37, model rev 40c06982, det 0.0, n_perm 5000, results commit 54a6b017).
0.6B smoke clean (surfaced the zone-degeneracy design PAUSE → amended pre-data).

**The frozen verdict: neither engine shows count-scaled work.** Under the frozen
one-directional bound, FLAT KILLS iterated-soft-β: the unification's
pre-registered contact FAILED. Frame-ledger: attention=β spent a contact and
lost it (strong form).

- **D1 (linear/FFN)**: ρ_lin=0.014 p=0.447 FAIL — **but the observable
  CEILINGED**: SY-share 0.93–1.0 on all add/mul items (mul exactly 1.0
  everywhere → degenerate Spearman); the only headroom family (succ,
  0.40–0.80) is flat-to-negative. Honest read: *S/Y is categorical and
  saturated — math flips the duplication sector ON; magnitude does not grade
  it.* Half falsifier, half instrument ceiling (froze a share metric without a
  ceiling guard — the s332 lesson, now paid twice). Post-hoc (unfrozen, no
  null): total fires FALL with N on add/mul (ρ −0.73..−0.91) — directionally
  anti-iterated.
- **D2 (circular)**: ρ_circ=0.252 p=0.054 slope=6.2 shape_p=0.176 FAIL — but
  the per-item structure is the finding: **L50 is BIMODAL** (instant L0–2.5 vs
  late L36–38 populations); group means were fraction-mixing, not graded
  depth. **Late-mode fraction is monotone in CIRCULAR DISTANCE** min(N,7−N):
  1/14 → 4/14 → 6/14. Two populations — lookup-like instant vs computed-late —
  with P(computed) tracking shortest-path distance (echoes the s310
  two-population split; is what an iterated mechanism taking the SHORT WAY
  around the circle would look like). POST-HOC, owes its own freeze
  (→ ⚪ §P-SHORTEST-PATH-ROTATION).
- **D3 (V-patch)**: V-CARRIED-EARLY-ONLY, sharper than designed — early
  (L0-6) donor-adoption 0.571 vs zone (L1-6) 0.071 = noop = late; the bands
  differ ONLY by L0 ⇒ **the day-operand V-carry is essentially
  LAYER-0-ONLY**. Operand enters via L0 attention-V; downstream operates
  in-place. Third sighting of the s252 route-at-L0 law.
- Secondary: logit-lens resolution ρ=0.49 vs N (late-stack, non-gating); the
  14B circular battery is NOT FFN-silent at item level (SY-share 0.53, fires
  5.6/item) — differs from the s344 group-level noop read; flagged.

**Net picture: route-at-L0 → rotate-in-place → late readout** — the
learned-rotation/lookup world — EXCEPT the bimodal circular-distance whisper
saying some items are computed, not looked up. The strong unification is dead
at this contact; the two-population shortest-path form is the surviving,
freezable residue.

### §Result addendum — what lost was ITERATION, not the operation-shape (s345, Michael)

Michael's pressure-test after the verdict: *"how does that prove attention is
not beta reduction? attention can only do 1 operation — how is that 1 operation
used here?"* The correct scoping, pinned so the negative does not
over-generalize in future reads:

- **The probe could not and did not test the operation-shape.** Attention's one
  operation (`Σ softmax(q·k)·v` = content-addressed fetch/substitute) is
  architecture — trivially true every layer (the s204 audit already marks the
  operation-level claim untestable). What was frozen and falsified is the
  **composition claim**: that the count N is *unrolled into N applications*
  (Church-numeral execution). NO-SCALING kills the unrolling, not the shape.
- **D3-at-L0 is itself a positive causal sighting of ONE soft-β step**: the
  query position content-addresses the day operand and substitutes its V at
  L0 (swap Monday's V for Friday's → the answer follows Friday); after L0 the
  patch is inert → the instruction fired ONCE for that operand. The
  one-instruction CPU executed a ~one-instruction program: fetch operand(s) +
  one learned primitive + late readout.
- **Calculus-identification reading (δ grows again):** the recovered calculus
  treats **numbers as DATA passed to native δ-primitives, not as programs to
  unroll** — like a real interpreter with hardware ADD, it does not β-reduce
  Church numerals. Corrects the old s127/s161 "numbers ARE selectors /
  church encoding" reading; the categorical (ceilinged, ungraded) S/Y
  engagement is the rule-bank switching ON, not per-step work. Joins no-η
  (s344 weak calculus) in δ(M, λβη): WHNF-halt, no η, **no Church-numeral
  execution — δ-rules instead**.
- **Frame-ledger scoping:** the ledger records a loss for the *iterated*
  clause ("a SERIES of reductions") only. The substitution-shape clause had no
  contact here to win or lose. The live residue is §P-SHORTEST-PATH-ROTATION:
  whether the computed-late minority iterates ∝ min(N, 7−N).
