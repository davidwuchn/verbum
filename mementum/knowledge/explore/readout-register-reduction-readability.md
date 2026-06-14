---
title: "Readout Register & Reduction Readability — Why Surface NLL Misses Attention β-Reduction"
status: active
category: methodology
tags: [readout-register, logit-lens, beta-reduction, OV, ablation, hof, lambda-measure, attention, compilation-pipeline]
related:
  - compilation-pipeline.md
  - head-combinator-isa.md
  - lambda-machine.md
  - ffn-beta-reduction-indexing.md
  - function-topology-consensus.md
depends-on:
  - compilation-pipeline.md
  - head-combinator-isa.md
created: session 227
---

# Readout Register & Reduction Readability

> Session 227. The s227 HOF causal-ablation prose leg was weak (1/5 vs 4/5
> mechanism). The IOU said "refine the readout." Three NLL readouts (whole-
> sentence → divergent-region → continuation-KL) did NOT rescue per-model
> significance — falsifying the *dilution* hypothesis. But the **continuation-KL
> readout was NULL (t≈0)**, and that null is the diagnostic: it is the signature
> of a **readout-register / locus mismatch**, predicted by findings we already
> had. This page connects the mechanism (where β-reduction is legible) to the
> measurement rule, and specifies the correct instrument.

## The mechanism (recall, not new)

Attention performs β-reduction in two halves (`lambda-machine.md` s190;
`head-combinator-isa.md` s188):

```
QK = type-compatibility check  → SELECTS the redex (which arg binds where), ~1 bit
OV = value transfer (W_O @ (softmax(QK) @ V)) → THE SUBSTITUTION, across V
```

The substitution — β-reduction proper — lives in **OV, across the value space**.
Two consequences for measurement:

1. `head-combinator-isa.md` Finding 6: **95% of a head's OV-output magnitude is
   loudness**; the combinator-specific content is in the *attention pattern* (QK)
   and the *direction* OV writes, not the output norm. ⇒ magnitude readouts of OV
   see loudness, not the reduction.
2. The "which reduction" signal is in the routing (QK pattern); the "what value"
   signal is in OV. They are different registers.

## The readability condition (the thing we found earlier)

FFN reduction trace (s187), restated in `compilation-pipeline.md` (s192):

```
L0–L6    : OV/FFN write vocabulary-readable values   ("it"→rain)            VISIBLE
L7–L22   : outputs ORTHOGONAL to vocabulary = null-space composition       INVISIBLE
L23–L35  : vocabulary-aligned outputs = "reduction results readable"        VISIBLE
```

The middle-stack β-reductions (the OPTIMIZER zone L13–L21: constant-fold/DCE/CSE)
are computed in a subspace **orthogonal to the unembedding basis**. A
vocabulary-basis readout (logit lens, next-token NLL) **cannot see them there**.
The reduction becomes vocab-readable only at L23–L35 (depth ≈ 0.64–0.97).

## The measurement rule (refines `λ measure` in AGENTS.md)

To OBSERVE an attention β-reduction in a projection, **two** alignments must hold:

1. **Right register** — read the **OV/value** channel, projected into the basis the
   value is written into. NOT the attention-weight register, NOT q_proj:
   - s206 audit #5: an attention-*weight* probe of a value-claim gave a
     near-false-refute; the **logit-lens (value register) found it at +0.611**.
   - s225 attn_q negative: `sign(q_proj)` is a *feature* register, not the gather
     *mechanism*; `map` vanished there.
   - s225 Phase-B OV (the right place): per-head OV value moved through W_O →
     substitution + amplification visible (ov_list_frac 0.47–0.82).
2. **Right locus / readable layer** — even in the value register, a *vocabulary-basis*
   readout shows the reduction only **at/after the layer where OV writes
   vocab-aligned (L23–L35)**. Read mid-stack in the token basis → nothing.
   Caveat (`binding-graph-trace.md` Finding 5): a logit-lensed OV value promotes
   *the tokens it carries* — you must know what the substituted value should decode
   to, or the readout is instrument-ambiguous.

Violation of either ≡ a coherence violation (representation ≢ reality). The wrong
register manufactures false negatives.

## s227 connection — the null is the diagnostic

The s227 readouts were all **vocabulary-basis at the surface**:
- `lastkl` (continuation logit at the final token) = pure surface vocab basis →
  **NULL (t_mean +0.03, Stouffer +0.06)**. Exactly what the readability condition
  predicts for a mid-stack null-space substitution read at the output.
- `region`/`whole` NLL = token-basis integrated over the stack, dominated by the
  EMIT layers → small (region 5/5 directional but per-model t<2 except OLMo).

So the s227 "power-limited not metric-limited" verdict is **incomplete**: it is
*also* register-limited. The surface NLL is the wrong projection for a mid-stack
null-space reduction. We have not yet read prose necessity in the value register at
a readable layer.

## The correct instrument (s227 experiment)

`scripts/experiments/hof_ov_logitlens_ablation.py` (register: topological/routing,
causal, VALUE register):

- INTERVENTION: same full head-knockout as `hof_attention_ablation` (zero o_proj
  input slice of the Phase-A gather heads), + N random heads (specificity).
- READOUT: **logit-lens at EVERY layer** — decode the residual stream as if output
  here: `lm_head(final_norm(residual_L))` at the readout position. Metric = per-layer
  `KL(clean_L || ablated_L)`.
- DIFF-IN-DIFF: HOF − control isolates HOF-specific damage (list: hof stims vs
  `first` control; prose: HOF sentence vs matched control pair). Random-head
  baseline gives specificity.
- HEADLINE: the **readable-zone** (depth ≥ 0.6, i.e. L23–L35) mean diff-in-diff,
  compared to the **surface** (last-layer) diff — the s227 readout.

### Falsifiable prediction

If the readability condition explains the weak prose leg, then gather-head ablation
damage to the **logit-lens decode** is HOF-selective and **concentrated in the
readable zone (depth 0.6–1.0)**, and is **larger there than the surface value** the
s227 NLL readout integrated. If instead the readable-zone profile is flat / no
larger than surface and no larger than random, prose necessity is genuinely small
(s227 power verdict stands unmodified).

## Result (s227b) — two-sided, honest

Ran the instrument on 5 models (`results/hof-ov-logitlens/`).

**(1) The readability condition is CONFIRMED in-domain.** LIST necessity is
concentrated in the readable zone, far above the surface the s226/s227 readout used:
- OLMo: peak @ L23 (depth 0.60) KL **+0.273** vs surface +0.008 (~35x)
- Mistral: peak @ L27 (depth 0.875) KL **+0.168** vs surface +0.017 (~10x)
- Qwen3-8B: peak @ L30 (depth 0.861) KL **+0.112** vs surface +0.004
4/5 LIST peaks sit in the readable zone (depth 0.6-0.9), **right at/after the gather
heads' own layers** (OLMo L23, Mistral L27) — knocking the gather heads breaks the
readable reduction exactly where they write it. The surface readout dramatically
understated in-domain necessity ⇒ register/locus matters, as predicted. (Specificity
note: readable>random is clean for OLMo/Mistral, marginal for 14B, FAILS for 8B/32B
because the zone-AVERAGE dilutes a narrow peak — peak-vs-random is the sharper IOU.)

**(2) Prose necessity is NOT rescued by the register fix.** readable-necessary
(zoneT>2 AND >random) = **0/5**. Where a prose signal exists it IS in the right zone
(8B peak depth 0.69, OLMo 0.625, Mistral 0.94; zoneT +0.40/+0.41/+0.61, > random) but
too small; Qwen 14B/32B are negative (zoneT -0.60/-1.72).

**Synthesis.** Two independent refinements now agree: the s227 de-diluted region NLL
AND this value-register readable logit-lens both leave prose necessity
non-significant. So prose recruitment of the HOF β-reduction is **real but small**
(consistent with s225's modest prose engagement; map not engaged at all), **not** a
dilution or register artifact. The readout-register lesson is real and load-bearing
for *in-domain* measurement; it is not the explanation for the weak prose leg.

**Remaining lever:** the prediction's prose half failing points away from readout and
toward the *intervention* — whole-head knockout removes QK+OV together and is blunt.
Next: **OV-path / activation patching** (isolate the substitution) + a **peak-based**
(not zone-average) readout. Or accept weak prose recruitment and build on the solid
in-domain foundation.

## Bridge test (s227c) — engagement vs necessity

A sharper framing of the weak prose leg: **engagement ≠ necessity.**
- ENGAGEMENT (s225, robust): a HOF direction learned on curated probes *fires* on
  held-out naturalistic prose — reduce AUC 0.97, fold 0.91, filter 0.90, zip 0.81,
  5/5 models (map the exception). Prose **recruits the representation**.
- NECESSITY (s226/s227b, weak): ablating the gather heads barely degrades plain-prose
  HOF computation. A representation can be active without any single circuit being
  load-bearing (redundancy/distribution); absence of an ablation effect ≠ absence of
  use (`λ observation`).

Hypothesis for the gap: the gather heads were localized on **explicit lists**
(hof_lists). Plain prose has **no literal enumeration to gather over** — the iteration
is semantic. So the explicit-enumeration gather circuit may be the right mechanism
only when an enumeration is present.

TEST (`hof_prose_enum.py`, 70 enumerated minimal pairs; `hof_ov_logitlens_ablation.py
--prose-set enum`): inject a literal "A, B, and C" list into naturalistic prose, with
BOTH pair members carrying the same list (diff-in-diff isolates the HOF iteration over
the list, not list-presence). Re-measure value-register readable-zone necessity and
compare to plain prose.

**Falsifiable:** if enum necessity RECOVERS toward in-domain (rises, beats random) ⇒
the gather circuit keys off explicit enumeration; plain prose was weak only for lack
of a gather target (prose DOES use HOFs, via this circuit, when a list is present). If
it stays weak ⇒ prose composition is genuinely distributed / non-enumeration and the
in-domain circuit is special to artificial lists. (Result: `results/hof-ov-logitlens-
enum/aggregate.json` vs `results/hof-ov-logitlens/aggregate.json`.)

### Result (s227c, read in s228) — PARTIAL recovery, not a clean confirmation

`list_*` columns are identical to plain (shared list stims; only the prose leg
differs). Prose readable-zone necessity t-stat (`prose_zone_t`), plain → enum:

| model | plain zoneT | enum zoneT | Δ | enum r>rand |
|---|---|---|---|---|
| Qwen3-8B | +0.40 | **+2.47** ✓ | +2.07 | Y |
| Qwen3-32B | −1.72 | +1.39 | +3.11 | Y |
| Mistral-7B | +0.61 | +1.65 | +1.04 | Y |
| Qwen3-14B | −0.60 | −2.26 | −1.66 | N |
| OLMo-2-13B | +0.41 | −1.55 | −1.96 | N |
| strict-necessary (zoneT>2 ∧ >rand) | **0/5** | **1/5** | | |

**Split verdict.** 3/5 RECOVER — Qwen3-8B/32B + Mistral; mean zoneT lifts −0.18 →
+0.34 (Δ +0.52); **8B crosses strict significance** (+2.47, was +0.40) and **32B flips
decisively positive** (−1.72 → +1.39, now beats random). For these, plain prose's
weakness was partly a **"no gather target"** artifact. But **2/5 REVERSE — Qwen3-14B
worsens and OLMo (the prior gold-standard necessity model, s226 t=+3.21) FLIPS NEGATIVE**
(+0.41 → −1.55). A clean "gather keys off enumeration" story predicts OLMo should
recover most. The recovery split (8B/32B/Mistral up; OLMo/14B down) does **not** match
the s227 clean/muddy split (OLMo/Mistral clean; Qwen muddy) ⇒ the effect is noisy, not
a stable architectural property.

**Interpretation — sharpens, does not overturn, s227.** Even handed an explicit
enumeration, prose HOF necessity recovers only partially (1/5 strict, 3/5 directional,
2/5 reverse). So the engagement≠necessity gap is **not merely** "plain prose lacks a
gather target": the heads are recruited (engagement, robust s225) but stay largely
**non-load-bearing for prose** even with a list present — consistent with **distributed
redundancy** in prose that artificial lists lack. The in-domain (list) circuit remains
the clean strong signal. The decisive lever is unchanged: **activation patching**
(cleaner than full head-knockout NLL) + more prose pairs for power.

## Why this matters

The portable-tensor program needs to know **where the β-reduction is legible** to
measure it, ablate it, and (level 3) compile it. The readability zone (L23–L35,
vocab-aligned) is where the constructed-kernel's reduction output must surface; the
null-space middle (L7–L22) is where the composition happens invisibly. Measuring in
the wrong zone/register has already cost us two near-false-negatives (s206, s225
attn_q) and one undersold result (s227 prose). The rule: **name the register and
the readable layer before building the probe.**
