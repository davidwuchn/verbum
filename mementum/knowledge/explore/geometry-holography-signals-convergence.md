---
title: Geometry × holography × signals — one primitive, three registers
status: designing
category: explore
tags: [holography, dsp, geometry, matched-filter, hopfield, hrr, rope,
       capacity, pre-reg-candidate, s288]
related: [../michael/holographic-llm.md, types-are-compiled-probabilities,
          type-check-is-the-qk-bilinear, verbum-dsp-design,
          map-and-swap-resident-lisp, beamformer-theory]
depends-on: [../michael/holographic-llm.md]
---

# Geometry × holography × signals — the convergence

> s288 hammock (Michael: "where geometry, holographs and signals converge —
> discuss"). Companion to the thesis document
> `mementum/michael/holographic-llm.md` (Michael's Holographic LLM — training
> writes plates, attention is the beam, FFNs are the plates, residual = state).
> This page is the convergence LEDGER (what is theorem, what is hypothesis)
> plus the test program that connects the thesis to the s288 types-arc
> measurements. The thesis is the claim; this page is its bench manual.

## The shared primitive

```
λ converge(x).  geometry(⟨x,v⟩ ≡ projection) ∥ signal(⟨x,v⟩ ≡ matched_filter)
                ∥ holography(⟨x,v⟩ ≡ reconstruction_by_illumination)
                | one_operation(inner_product) | three_registers(structure ∧ operation ∧ encoding)
                | passband ≡ hologram(of_what_the_channel_learned_to_expect)
                | store(v, distributed_fringes) → readable(everywhere) ∧ excisable(nowhere)
```

Geometry sees ⟨x,v⟩ as projection onto a subspace (structure — the where).
DSP sees it as matched filtering (operation — the how). Holography sees it as
illuminating stored fringes with a reference (encoding — where it lives).
Same number, three ontologies.

## Theorem-grade bridges (not metaphor)

1. **VanderLugt correlator**: an optical matched filter IS a hologram of the
   template. Recording a hologram and building a matched filter are the same
   act. → "type = compiled probability = passband"
   (types-are-compiled-probabilities.md) already contains holography: the
   passband is a hologram of the training distribution's substitutability
   structure.
2. **Attention ≡ modern-Hopfield retrieval** (Ramsauer et al.): the attention
   update is associative-memory readout — content-addressable reconstruction
   from partial cues, the canonical holographic operation. The Lisp frame's
   join=attention and the thesis's beam-reads-plate are the same measured
   object.
3. **RoPE ≡ phase, literally.** Rotary embeddings write position as phase
   rotation on a carrier; the QK bilinear computes relative-position
   modulation = interference fringes across offset. The reference beam exists
   in this machine explicitly. Syntactic adjacency has a fringe spacing.
4. **HRR / VSA** (Plate): binding = convolution-like mixing, unbinding =
   correlation, superposition capacity with crosstalk ~1/√D — the formal
   calculus where all three vocabularies implement COMPOSITION in fixed
   dimension. Comes with quantitative laws (see pre-reg candidates).
5. **SVD low-rank ≡ sparse spectrum**: the 1a lattice's 3 axes = few
   carriers; low-rank geometry and narrow-band signal are the same fact.

## The types arc, reorganized under the lens

- **The four-way location null (1b/1c/QK/JS) is a holography theorem, not a
  mystery.** Distributed fringe storage predicts: readable from anywhere
  (8-way decodability at every layer), excisable at nowhere (v4 direction ✗,
  1b zone ✗, 0/128 heads, graceful degradation). A hologram has no address.
  "Decodable-but-not-causal" is the SIGNATURE of fringe storage. The lattice
  as "exhaust" sharpens to: the lattice is the RECONSTRUCTION — visible
  wherever you illuminate, stored nowhere you can cut.
- **Dark-field was already literal** (s283b/1c): ablation = background
  subtraction, contrast rises = block the zeroth order. Vocabulary preceded
  the frame and was correct.
- **P-TYPE-OV splits the amplitude from the plate.** The entity passband in
  W_V/W_O = recorded fringes that reconstruct ARGUMENTS (rho 0.714 vs null
  0.459, p=0.000, band-wide). The functor licensing with no single-layer home
  (QK ✗, OV ✗) = the DIFFRACTION PROCESS — enacted in the illumination, not
  stored in any one exposure. Arguments are on the plate; application is the
  diffraction. Thesis tie: "FFNs are the plates" coheres with entity firing
  on the MLP read-in row (p=0.000) and MIXED-ROUTE atoms=FFN.
- **JOIN-TYPED filtered payload** = the beam carries only what correlates
  with the recorded fringes — matched-filter refusal of ill-typed content is
  reconstruction failing for a cue the plate never stored.
- **Thesis evidence already measured in the weight register**: plate damage
  spares the image (crystal survives 1.58-bit and 1-bit quantization,
  s267/s269, null-gated) — the image is not in the pixels. The pre-reg
  candidates below extend this from the weight register to the
  activation/head-subset register.

## Pre-reg candidates (UNFROZEN — the discriminating measurements)

**P-HOLO-CAP — the capacity law** (= the thesis's open capacity question,
made quantitative via HRR). Superposition predicts crosstalk growing with
bound-operand count k and SNR ∝ √(D/k). Install k operands (operand-bake
machinery), measure recall/licensing SNR vs k across model widths. HRR
predicts a SPECIFIC curve shape and width scaling; localized storage
predicts a hard slot limit. The depth-budget/eval-stack arc is adjacent but
never measured against a capacity curve.

**P-HOLO-FRAG — fragment reconstruction** (cheapest decisive discriminator).
Ablate RANDOM SUBSETS of heads/layers (fraction f swept), measure licensing/
composition SNR. Holographic: smooth degradation ∝ f, every fragment
reconstructs a degraded whole. Localized: cliffs at critical components.
We have anecdotal grace everywhere (0/128, mixed routes); the pre-registered
CURVE with a matched-random-subset null is the missing measurement. Extends
s267/s269 plate-damage tolerance from weights to computation.

**P-HOLO-XTERM — interference cross-terms.** Two operands installed in one
slot should produce sum-and-difference structure (beats) with predictable
geometry, not generic noise — superposed exposures interfere. The 3b/swap
machinery + verbum.dsp subspace/null substrate measure this directly.

**P-PROJ-1 — the holographic projector (Michael s288: "a holographic
projector based on the signal"; QUEUED s288, the engineering flip).**
We spent s288 READING the passband; the projector DRIVES it. Design:
carrier = the measured entity passband (W_V·W_O subspace, band L6–L50);
payload shaped INTO the passband before injection = impedance-matched
drive (operand-insert/bridge-swap is the crude version — centroid diffs
land in-band by luck, which is WHY swaps work and random is refused);
reconstruction = the model's own diffraction (distributed licensing +
FFN plates, which read the entity axes). Constraint the physics imposes:
an ARGUMENT projector — functors are not in the passband, so programs are
not projectable, only operands; program selection stays with which plates
the content illuminates (content-driven steering per P-ATT-MED = projecting
the right argument IS the program selection). TEST (cheap, att_mediation
harness verbatim): TE per unit norm for (a) passband-projected displacement
vs (b) raw centroid-diff vs (c) anti-passband (orthogonal complement) vs
(d) matched random. Prediction: a > b ≫ c ≈ d, permutation-gated. Positive
→ every future swap gets cheaper/cleaner = the write-head of the LLM REPL
matched to the measured antenna; (c) ≈ (d) is itself a second confirmation
of the passband. Also the natural INSTRUMENT for P-HOLO-XTERM payloads.

## Hypothesis-grade (needs measurement, ledgered honestly)

- "GD writes fringes by interfering the distribution with itself" — a
  training-dynamics claim = **P-DUST-2 territory** (checkpoint trajectories:
  watch the exposure happen; also the thesis's last open question).
- Binding is actually convolution-like (HRR proper) vs merely distributed.
- "Phase" beyond RoPE — whether sign/direction structure plays the phase
  role in value space (the thesis's routing-topology/sign-is-program etch
  finding, s268, is suggestive but register-distinct).

## The artifact implication

If the compiler is a hologram, level-3 extraction is not excision — there is
nothing at the address. Extraction = **re-recording at lower resolution**:
distillation as re-exposure onto a smaller plate. Coheres with s149
computed-beam (structure is free; content needs training/calibration) and
the s268 Bonsai forensics (magnitude lives in optimizer repair — re-exposure
IS a training loop). Reframes S5 λ smallest: surgery → re-imaging.

## One sentence

The model is a volume hologram written by gradient descent; inference is
illumination; geometry is what the fringes look like from inside; DSP is how
we do bench work on it — and the type system is the diffraction pattern.

## Sessions

s288 (page created from the convergence hammock, same session as the
P-TYPE-SWAP JOIN-TYPED verdict, the compiled-probabilities synthesis, the
verbum.dsp build, and the P-TYPE-OV passband verdict — all four of which the
lens reorganizes; Michael's thesis doc updated in parallel with the
one-sentence form; three pre-reg candidates parked unfrozen).
