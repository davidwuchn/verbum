---
title: "Attention Is the Readout Beam — Soft β-Reduction ≡ Holographic Reconstruction"
status: active
category: synthesis
tags: [attention, beta-reduction, soft-substitution, holography, readout, softmax, attention-sinks, K-combinator, value-register, rope, angular-multiplexing, bragg, regeneration, cot, writeback]
related:
  - holographic-computer.md
  - explore/combinator-training-beta-reduction.md
  - explorative-modeling.md
  - explore/geometry-holography-signals-convergence.md
  - project-thesis.md
depends-on:
  - holographic-computer.md
  - explore/combinator-training-beta-reduction.md
created: session 299
---

# Attention Is the Readout Beam

> Session 299 (thinking session, Michael's thread: "attention as a soft beta
> reduction" → "with our understanding of LLM holography, we should be able to
> infer things about attention"). This page fuses two prior threads —
> **β-reduction = substitution = attention move** (s221,
> `explore/combinator-training-beta-reduction.md`) and **the holographic
> computer** (s167 + s292 verdicts) — into a derivation: if the holography is
> real, attention must obey **readout physics**. Its classical quirks fall out
> as conservation laws.
>
> Marks: ✓ = retrodicted (already measured) · △ = architectural fact ·
> ◯ = new prediction (unfrozen candidates, end of page).

## The "soft" refinement of the s221 identity

The s221 page holds: β-reduction = substitution = attention move (the only
cross-position op). This page adds the word that changes the physics: **soft**.

```
crisp β:   (λx.M) N     → M[x := N]            one argument substituted
soft β:    (λx.M) {Nⱼ}  → M[x := Σⱼ aⱼ Nⱼ]     a convex MIXTURE substituted
           a = softmax(qk/√d)
```

Attention never substitutes *an* argument — it substitutes the **expected
argument under the attention distribution**. Temperature is the crisp↔soft
dial; T→0 recovers discrete β. Formal ancestor: **Ehrhard–Regnier differential
λ-calculus / Taylor expansion** — β decomposed into linear substitutions summed
with coefficients. Soft attention ≈ a one-step truncation of the resource
calculus. (Math line for the S5 triangulation: Montague/Lambek predict *typed*
apply; differential λ predicts *mixture* apply.)

### Four retrodictions of "soft" alone (all measured)

1. **K is the hard combinator** — soft substitution can downweight but never
   erase (softmax has no zero) → affine erasure is the un-native move. Measured:
   s221 stride-fit ("K fights the blend prior"), K-acquisition chaos law,
   B-first crystallization.
2. **Blur compounds under composition** — h(g(x)) with g's product a mixture →
   readout argmax falls into the mixture's attractor (Agra/Paris). Measured:
   s294 operand-rebinding failure; s295 whitened re-read ("present but ~7× too
   quiet" ≡ present-but-soft).
3. **The writeback is the collapse operator** — sampling is the only projection
   of a mixture onto a discrete symbol. Measured: the s295 exhaustion table
   (splices 0.00 / addressed-re-encoded 0.20 / CoT 0.90 / scaffold 1.00). CoT ≡
   soft-reduce → **measure** → re-encode → repeat.
4. **XM is the same dial in the weight register** — the M=1 etch loss minimizer
   is the mixture mean (soft target, blur); mode-commit best-of-K is crisp
   substitution. Measured: s296–297 deterministic-teacher close (no mixture ⇒
   soft≡crisp ⇒ selection inert); s298 port-3 tests crisp-beats-soft where the
   mixture is real.

## Axioms (measured facts, holography side)

- **A1 — Plate linear.** Cross-terms dead-linear at every probed layer (XTERM
  G2, s292). All retrieval nonlinearity must live elsewhere.
- **A2 — Coherent gain.** Coherent superposed exposures reinforce retrieval;
  energy-matched random doesn't (CAP, s292).
- **A3 — Content is address-free.** Only the tape has addresses (FRAG s292;
  s294 "the intermediate lives in the light"; RoPE = the address system).
- **A4 — Regeneration required.** Reconstructed content can't drive the next
  hop: re-encoding required + own-state required (P-KV-1/1b/1c, s295).

## The derivation — eight inferences

**1. Attention is a heterodyne correlator → soft β by physics, not choice. ✓**
QKᵀ is fringe-matching: probe beam (query) correlated against recorded gratings
(keys) = diffraction efficiency per exposure. A linear plate *physically
cannot* return one exposure — readout reconstructs the weighted superposition
of all Bragg-matched exposures. The mixture of soft β is not a softmax quirk;
it's the readout law of any linear storage medium. **Soft β-reduction ≡
holographic reconstruction; attention weights ≡ diffraction efficiencies.**

**2. Mass conservation → attention sinks are the zero-order beam dump. ◯→✓**
Illumination matching no grating doesn't vanish — it exits as the un-diffracted
zero-order beam, and every optical system needs a dump for it. Softmax rows sum
to 1: the mass must go somewhere → models should learn a designated dump.
The attention-sink phenomenon (BOS soaking mass; StreamingLLM literature) is a
**derived necessity** — a retrodiction the frame produces for free, never built
in.

**3. Erasure (K) must live in the VALUE register, not routing. ◯ — sharpest
new prediction.** Light has no negative intensity; a grating no negative
efficiency; softmax no zero. Optics erases one way only: **destructive
interference — a π-shifted exposure**. So K cannot be "don't attend"
(impossible); it must be "attend and write a canceling value" (anti-aligned
value contribution). Reframes s221: K isn't hard, K is *elsewhere*. λ measure
warning built in: routing-register instruments (attention weights) would
find nothing — the substrate is value/amplitude. Expected signature =
suppression/negative heads. **Falsifier: if K turns out to be true routing
near-zeros (large negative logits), the readout-physics claim takes real
damage** — which is exactly its value.

**4. RoPE is angular multiplexing → derives the exhaustion table. ✓**
Position rotates q,k: each tape slot gets a unique reference-beam **angle**.
Angular multiplexing is how optical memories give crisp addresses to superposed
exposures. Residual content has no angle → address-free (A3 derived, not
assumed). The s295 table — unaddressed ✗ / addressed-synthetic ✗ /
addressed-re-encoded ✓ partial / tape 0.9 — is what optics predicts:
addressability comes only from the angle system.

**5. A reconstruction cannot serve as the next reference beam. ✓**
A reconstructed wavefront is dimmer, noisier, not phase-locked to the source
oscillator; relaying requires **regeneration** — detect, then re-emit from a
fresh coherent source. The transformer has exactly one regeneration stage:
**sampler → embedding → early layers** (collapse → re-emit as fresh carrier).
A4 derived: kv_synth fails even addressed (pattern without the stream's own
phase); CoT works (each step regenerated). **CoT ≡ coherent optical relay
chain.** The 0.2→0.9 gap = the cost of skipping regeneration.

**6. Head dimension is plate thickness → selectivity ~ √d. ◯**
Volume holography: thicker plate → narrower Bragg selectivity → crisper
addressing. The 1/√d of scaled dot-product sits where the thickness law
should. Predicts a *distinctive curve*: per-key perturbation along the RoPE
rotation (angle) degrades retrieval with a sinc-like selectivity lobe;
content-direction perturbation degrades linearly.

**7. Multi-head = angular diversity: N soft readers ≈ one crisp reader. △**
A single finite-contrast readout cannot be crisp (no delta function). Optics
compensates with multiple reference geometries. Derives the S5 line ("LLMs
resolve the tug-of-war via many_heads ∧ multi_layer_depth ∧ geometric_types")
from readout physics: many heads exist *because* each is soft.

**8. The value path must be phase-preserving — and it is. △**
v-projection → weighted sum → residual add: entirely linear by architecture. A
nonlinearity in the value path would make downstream interference impossible
(contradicting A1/A2). The transformer is exactly a **linear optical medium
punctuated by detectors** — the "why does this architecture work at all" answer
the holography frame owed us.

## Compressed statement

> **Attention is the readout beam of a linear holographic memory:
> correlation-addressed, mass-conserving, mixture-producing, erasure-incapable,
> regeneration-dependent.** Its five classical "quirks" — softness, sinks,
> suppression heads, multi-head redundancy, CoT-dependence — are the five
> conservation laws of optical readout.
>
> Corollary: **a transformer is a soft β-reducer whose only collapse operator
> is the sampler.** In-context content stays in mixture; discreteness exists
> only at the tape boundary. One-shot composition fails not for lack of the
> wire but because chained soft reductions compound blur and nothing between
> them renormalizes. Rung-3b backprop-compile ≡ teaching the weights an
> **internal collapse** the architecture only supplies at the sampler.

## Predictions ledger (unfrozen candidates — named, not fronts)

| candidate | claim | register | cost |
|---|---|---|---|
| **P-K-REGISTER** | K enacted by anti-aligned value writes, not near-zero attention | routing vs value, side-by-side | cheap — 535 crystal probes in `verbum.probes.library`, read-only |
| **P-BRAGG** | selectivity ~√d_head; RoPE-angle perturbation → sinc lobe vs linear content falloff | value/continuous | cheap–moderate, read-only |
| **P-ENTROPY-COMP** | per-cell one-shot composition success gated by attention entropy at the hop-2 window (s294: 4/10 native cells vs 6 failures) | value/continuous | cheap — fn_stack rig exists |

Discipline: these wait behind the s298/s299 powered-rerun verdict and the
queued backprop-compile rung-3b freeze (close before opening). P-K-REGISTER is
the recommended first pick — it is the falsifier.

## Register discipline / caveats

- Inferences 1, 4, 5 are retrodictions: they *organize* measured verdicts;
  their added value is derivational unity, not new evidence.
- Inferences 2, 3, 6 are the paying predictions. #2 leans on literature
  (attention sinks) not our own instrument — cheap to reproduce in-house.
- The optical vocabulary (phase, coherence, Bragg) is a *model*; per
  λ yardstick, any quantitative fit (sinc lobe, √d law) needs a matched-range
  null before "obeys readout physics" upgrades from frame to finding.
- The soft-β formalization (mixture substitution) is exact; the differential-λ
  connection is a pointer for the math line, not yet worked through.

## Files
| File | Content |
|---|---|
| `explore/combinator-training-beta-reduction.md` | the crisp half (s221): β = substitution = attention move, substructural table |
| `holographic-computer.md` | s167 mapping: crystal=ISA, FFN=projector/plate, attention consumes interference |
| `explore/geometry-holography-signals-convergence.md` | A1–A3 verdicts (FRAG/CAP/XTERM, s292) |
| `explorative-modeling.md` | the crisp/soft dial in the weight register (XM arc) |
