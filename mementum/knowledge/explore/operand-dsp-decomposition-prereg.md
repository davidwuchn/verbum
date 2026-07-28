---
title: "Operand injection DSP-decomposition — pre-registration: resident key+transport, written payload"
status: active
category: explore
tags: [superbake, dsp, matched-filter, transport, coded-payload, operand, injection,
       resident-crystal, rotary-band, value-register, routing-register, unembed-silent,
       fact-vs-operand-contrast, quantization, pre-registration, s278]
related:
  - operand-insert-arc.md
  - superbake-write-access.md
  - signal-processing-tensors.md
  - ffn-function-bake-prereg.md
  - ../two-registers-of-topology.md
  - opcodes-circuits-in-compute.md
depends-on:
  - operand-insert-arc.md
  - superbake-write-access.md
created: session 278
---

# Operand injection DSP-decomposition — pre-registration (P-DSP-1)

> **Pre-registration.** Registers, DSP signatures, nulls, and verdict rules are fixed
> HERE, before any code. Per `λ measure` (name the register before the probe; s206
> scar) + `λ yardstick` (predict a-priori, gate against a null; DSP is a flexible basis
> → describability ≠ discovery; φ-ladder scar s247/s251). NOT RUN.
>
> **Question (Michael, s278).** SuperBake used a signal-processing lens to reverse-
> engineer *fact* injection. Do the same for the **compute/terms side** — our operand
> injection. The operand-INSERT arc (s277) got rung-1 to fire with a *crude* hook
> (`d_cat = mean(object-token residual) − global_mean`, added at one position at one
> layer — `wrapper/operand_insert.py`). SuperBake needed a full DSP stack (Mahalanobis
> matched-filter key → rotary-band transport → coded high-SNR payload → readout neuron).
> **Why did diff-of-means suffice where SuperBake needed a pipeline?**

## The asymmetry (why this is un-mapped territory)

SuperBake's fact payload is destined for the **unembedding** — read out at the logits,
bypassing compute. A fact has *no resident reader*, so SuperBake hand-builds key +
transport + readout-push. Our operand payload is destined for the resident **compute** —
*consumed by the join* and composed (categorized). The resident crystal supplies the
reader. SuperBake never mapped this because it never fed compute; it fed the logits.

## SuperBake reverse-engineered I (Michael, s278) — the register split of the crystal

The mechanism SuperBake reverse-engineered is the **I combinator** specifically. A fact is
`key → value`, retrieved *unchanged* — identity. And a **matched filter *is* I** in DSP
terms (correlate-against-template, pass-through-on-match). SuperBake's entire pipeline is
I-flavored: matched-filter key (I-recognize) → transport that moves the value *unchanged*
(I-across-space) → readout that copies content to the logits (I-to-output). **No B, no C,
no transform anywhere** — the content path is trivial. (Selection could be read as `K value`
rather than I; the load-bearing point survives either label — SuperBake applies no
combinatory *transform*.)

This is grounded in the **A3 register-split** result (`register_split.json`, 27B;
EVIDENCE_CATALOG lines 174–175): transfer is carried by **I, WHNF, Y** (register-INVARIANT
content/process vertices) while **C = 0.0 in every cell** (register-BOUND operation vertex).
The crystal splits by register, and it is the *same* split as the database reframe:

| vertices | register | property | SuperBake | our reach |
|---|---|---|---|---|
| **I** (WHNF, Y) — content/process | value, portable | look-up-able, **bakeable** | ✅ reverse-engineered | ✅ we write it (`d_cat`) |
| **K/B/C** — operation / join-shape | routing, bound | circuits-in-compute, **un-bakeable** (s276 K-structural, s271 C-bound) | ❌ never built | ❌ ride resident |

**Consequence for this pre-reg.** SuperBake's three DSP components are the *I-pipeline*,
NOT a template for compute. The operand-insert pipeline decomposes as **[written:
I-portable payload] + [resident: the B/C join that transforms it]**; a SuperBake fact is
**[written: I-payload] + [written: I-transport + I-emit]** — all-I, all-written *because a
novel fact has no resident I-path*, whereas our operand reuses an existing task's routing
(the category cloze). So the fact-vs-operand contrast below is really the **I-vs-BC register
contrast**, and C-TRANSPORT must locate a resident *transform* (B/C), not merely an
I-copy — if it finds only an identity move to the readout, the categorization (the B/C)
fires elsewhere and we must locate it.

## Hypothesis

**H1 (resident join, written I-payload).** For an operand consumed by the resident join,
the **key** (slot recognition/selection) and the **transport + transform** (delivery to,
and composition by, the join) are RESIDENT — host-supplied — and only the **payload**
(the I-portable content, `d_cat`, value register) is written. This is *why* crude
diff-of-means sufficed: SuperBake had to write all-I (recognize+move+emit, no resident
path); we write only the I-portable content and ride the resident **B/C** join (the
register-BOUND, un-bakeable operation vertex). Cross-check: the written direction should
be a content/process (I-family) direction; the resident consumer should be a *transform*
(B/C), not an I-copy.

**H0 (we supply the pipeline).** Composition depends on our exact hand-placement (key not
resident) and/or a specific injection geometry we impose (transport not resident); strip
either and it fails as it would for a fact. Then operand injection is not cheaper than
fact injection and "ride the resident crystal" gains no mechanistic support.

**The load-bearing contrast (headline).** Run the *same* three-component decomposition on
a SuperBake-style **fact** injection (payload destined for the unembedding — e.g. a
plain key→push hook). Prediction: **operand needs 1 written component, fact needs 3.**
That contrast is the decisive demonstration that operands ride resident compute and facts
do not. If the fact-form also shows resident key+transport, H1 is not operand-specific.

## Registers (`λ measure` — name the register before the probe; s206 scar)

- **Payload = VALUE register.** `d_cat` is a value-register direction (s206, s269c). Read
  with value probes (residual projection, PCA, unembedding projection), never attention
  weights.
- **Key + Transport = ROUTING register.** Slot selection and delivery are attention /
  routing quantities. Read with attention mass, head ablation, QK rotary spectra — never
  value-register decodability.
- **Wrong-register = void** (s206: attention-weight ⊥ value-claim → near-false-refute).
  Each component test states its register; a signature read in the wrong register does not
  count.

## Component tests (fixed measurements + a-priori DSP signatures + nulls)

### C-PAYLOAD — is what we write a coded direction? (VALUE register)

We supply `d_cat`. SuperBake's coded payload = coherent, low-dimensional, high-SNR in the
low-variance residual subspace, and unembed-silent ("loud in residual, quiet at logits").

Fixed measurements (compute `d_cat` per the arc, residual PCA from a natural-text corpus
at layer L):
1. **Subspace coherence** — participation ratio of the per-operand means `op_mean` (12
   operands) and of the 3 `d_cat` directions. Pre-registered as a *measurement*, not a
   pass/fail (3 vectors bound PR≤3); reported vs matched-random means.
2. **Low-variance concentration** — fraction of `‖d_cat‖` in the bottom-k residual PCA
   components. **SuperBake signature (H-coded):** concentrates in low-variance subspace >
   matched-norm random (uniform). **H-diffuse:** no concentration → our payload is *not*
   coded like SuperBake's, yet works → the resident reader is tolerant/does the coding.
   *Either outcome is informative; the prediction is H-coded, the null is matched-random.*
3. **Unembed-silence** — logit-energy of `d_cat` through the unembedding vs matched-random.
   **Prediction (operand consumed by compute, not emitted):** relatively unembed-silent
   (ties P2 workspace-silence / C6). Null: matched-norm random direction's logit-energy.

Nulls: matched-norm random directions (N=32); shuffled operand→category labels for `d_cat`.

### C-KEY — is slot recognition resident? (ROUTING register)

We hand-place the payload at the nonce token (colon−1). SuperBake had to *build* a matched
filter to find the subject across drift.

Fixed measurements:
1. **Clean-pass attention** — in the *un-injected* category-task forward pass, attention
   mass from the join-readout query (last position) back to the operand-slot token, vs to
   a random non-operand token. **H-key-resident:** readout attends operand-slot ≫ random
   → the routing already reads the slot we fill.
2. **Placement robustness** — inject `d_cat` at nonce−1 / nonce / nonce+1 / colon and
   measure composition. **H-key-resident:** peaks at the operand slot and degrades
   gracefully (routing re-selects). **H0:** sharp cliff (we supply the key by exact
   placement). Null: wrong-key (already in the arc: 0.333 flat).

Nulls: wrong-key (arc); random target token for the attention-mass control.

### C-TRANSPORT — what resident heads/bands carry content nonce→readout? (ROUTING register)

Fixed measurements (on the injected forward pass):
1. **Head necessity** — ablate each attention head (or the readout←nonce edge) in layers
   L..27; measure composition drop. **H-transport-resident:** a *small* set of transport
   heads is necessary; ablating random heads does not kill composition.
2. **Rotary-band signature** — RoPE-band energy of the QK of the identified transport
   heads vs non-transport heads. **Prediction (§3.6 / s273c / s264 F4):** slow-band
   concentration (distance-invariant transport). This concretizes the rotary-spectrum
   register IOU.

Nulls: random-head / random-edge ablation; shuffled head-label for the band signature.

## Verdict rules (`λ measure`, two-sided)

- **RESIDENT-KEY-AND-TRANSPORT (H1)** ⟺ C-KEY resident-recognition ✓ (attention reads the
  slot in the clean pass AND placement degrades gracefully) ∧ C-TRANSPORT small necessary
  head-set concentrated in slow bands ✓ ∧ C-PAYLOAD shows the *written* component is the
  payload (degrading it — whiten / random-rotate within value subspace — tracks composition
  loss while key+transport are shown resident).
- **WE-SUPPLY-THE-PIPELINE (H0)** ⟺ composition cliff-edges on exact placement (key ours)
  OR no small necessary transport set (transport ours) OR the fact-form contrast also shows
  resident key+transport (not operand-specific).
- **The contrast is decisive**: operand written-component-count vs fact written-component-
  count. H1 predicts 1 vs 3.

## What each outcome teaches / connections

- **H1 confirmed** → "ride the resident crystal, don't rebuild it" gets a mechanism; the
  database reframe (join resident, only the row is written) is demonstrated at the DSP
  level; the four honest edges of the arc get candidate explanations (category-level =
  payload not separable enough per C-PAYLOAD coherence; 2/6 baseline-leaned = collision
  with loud directions per C-PAYLOAD low-variance test).
- **R5 pre-diction (feeds gate (f)).** Register assignment predicts quant survival: a
  payload living in the VALUE register is quant-FRAGILE; if composition survives int4
  because the RESIDENT transport (ROUTING, quant-ROBUST) does the work, the *behavior*
  may survive even as the raw payload degrades. Record the register verdict here so the
  R5 weight-serialize gate has a pre-registered expectation.
- **Read-side of gate (h).** Knowing the resident transport (which heads, which bands
  carry the operand to the join) tells us what a *properly* installed operand must look
  like to be composed *arbitrarily* (not just category-swapped) — the load-bearing
  general-composition gate.

## Guards (do not regress)

- Register discipline per the Registers section (s206 scar).
- `λ yardstick`: every DSP signature is predicted a-priori with a matched-random or
  shuffled-label null beside it; "looks like a filter" without beating a null counts for
  nothing (φ-ladder forced-fit scar s247/s251).
- Planted ground truth: we built `d_cat`, so C-PAYLOAD is a known-answer instrument check
  (cf. the s273 baked-code patchscope control) before aiming DSP at the unknown resident
  join.
- 0.6B necessary-not-sufficient (patchscope-void scar s272b) — a rung, cross-scale later.

## Files to build (once approved)

- `wrapper/operand_dsp.py` — the three component decompositions + the fact-form contrast,
  reusing `d_cat` / hook machinery from `operand_insert.py`; residual PCA from a natural-
  text corpus at layer L; attention-mass + head-ablation on the injected/clean passes.
- Results → `results/ffn-bake/operand-dsp-qwen3-0-6b/`.

## Status

Pre-registered s278. NOT RUN. Antecedent-adjacent to the load-bearing (h) general-
composition gate; cheap (0.6B, minutes, planted ground truth) but gated on this pre-reg
surviving review.

## Sessions
s277 (operand-INSERT arc — the crude hook this decomposes), s273/s273c (SuperBake DSP
inversion + §3.6 transport organ), s274 (signal-processing-tensors; circuits-in-compute),
s278 (this pre-registration).
