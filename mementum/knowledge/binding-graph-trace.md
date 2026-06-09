---
title: "Attention IS the Binding Graph — Reversed by Causal Mask"
status: active
category: methodology
tags: [attention, binding, beta-reduction, causal-mask, mechanism, heads]
related: [ffn-reduction-trace, head-combinator-isa, holographic-computer]
depends-on: [ffn-reduction-trace, head-combinator-isa]
---

# Binding Graph Trace

> ⚠️ **Caveat (audit #4, session 204): the headline weights (H31@L27 = 0.82
> verb→subject; H03/H13/H15@L30) are largely POSITIONAL/RECENCY, not typed
> role-binding.** This page's probes are all simple SVO where the subject is
> *always* the earliest and nearest-preceding noun to the verb — so role,
> position, and recency are perfectly confounded; "verb attends to subject at
> 0.82" cannot distinguish typed β-reduction from a plain recency head. A
> control that dissociates them (subject-verb **agreement attraction**, where the
> number-distractor is the *nearer* noun: `attention_typed_binding.py`, 8B, 64
> PP+RC stimuli) found: **H31@L27 role-selectivity z = +0.54 (rank 5/32 — not an
> outlier; top head is H7), and ablating it changes agreement logit-diff by
> +0.001 (z=+0.06 vs a random-head null) — no causal effect.** Ablating *all*
> named binders (incl. H6@L33) is likewise indistinguishable from random heads
> (z=+0.01), even though the ablation bites (random 6-head sets reach −0.43).
> The *only* genuinely role-selective head is **H6@L33 (z=+4.08)** — but ~10×
> smaller than 0.82 and not causally load-bearing. **Read the 0.5–0.82 binding
> weights below as recency-dominated attention, not as evidence of typed
> β-application.** ("Attention is a weighted sum" is trivially true; "the sum is
> *type-driven* at these heads" is refuted.) Caveat scope: tested on plain-NL
> agreement *without* the compile gate the original used — a gate-context re-test
> is a named follow-up. See `audit-registry.md` #4 + `results/attention-typed-binding/`.

> ⚠️ **Caveat (audit #5, session 206): the depth-ordered "two-phase binding
> SCHEDULE" (Implication 2 — "subjects bind first at L27, objects at L30, coref at
> L33; the depth ordering IS the reduction schedule") is REFUTED — but the
> headline SEMANTIC value-transfer of Finding 7 (H31@L27 = the verb absorbs the
> subject's identity) is CONFIRMED and sharply L27-localized.** Tested two ways on
> 60–80 varied sentences/type (not 14 hand-annotated probes):
> - **Attention weight** (`binding_schedule_null.py`): dependent→head max-head
>   attention peaks at the **same early layers for all three types** (subj L6, obj
>   L4, coref L6), not L27<L30<L33; bootstrap **P(order)=0.000**; a random-pair
>   null peaks even earlier (L0) → early peak is generic local/positional
>   attention. *But this instrument tests routing/position (the #4 axis), not the
>   value transfer the claim is about, so it under-reads.*
> - **Semantic logit-lens** (`binding_schedule_semantic.py`, the faithful test of
>   Finding 7 — does the head's *output* decode to the bound entity): **H31@L27's
>   output points to the SUBJECT's token with margin +0.611 in a clean one-layer
>   spike (L26 +0.03 → L27 +0.61 → L28 +0.10; H31 z=+1.17, rank 2/32).** So
>   Finding 7's subject case is REAL and at exactly L27. *However:* it is ONE site,
>   not a schedule; the strongest L27 subject-transfer head is actually **H29
>   (+2.12)**, not H31; and (audit #4) it is **not causally load-bearing** for
>   agreement (ablation |z|≤0.35). The object leg (Implication 2 "object absorbs
>   the predicate at L30") does NOT hold semantically (margin@L30 ≈ −0.05; named H3
>   rank 29/32) — though that readout is instrument-ambiguous given Finding 5
>   (object V promotes object-tokens, not the verb). Coreference value-transfer
>   peaks at L27, not the claimed L33. **Bootstrap P(sem-peak subj<obj<coref)=0.191
>   ≈ chance (0.167)** — no depth schedule on the semantic instrument either.
>
> **Read Findings 4 & 7 / Implication 2 as: a real, L27-localized subject
> value-transfer head (H31, though not the strongest there, and not causally
> necessary), NOT a depth-ordered three-phase reduction schedule.** See
> `audit-registry.md` #5 + `results/binding-schedule-{null,semantic}/`.

> 14 probes with annotated β-reduction binding structure through 32
> attention heads at L27/L30/L33 of Qwen3-8B. The attention pattern
> literally IS the binding graph of the λ-expression — but reversed
> by the causal mask. Later positions attend back to earlier positions.
> Object→verb binding is direct single-head attention with weights
> 0.5-0.8. Subject→verb binding (forward direction) is blocked by the
> causal mask and must use a different mechanism.
>
> The binding heads at L30 are H03, H13, H15, H12 — consistently
> across all probes, all sentence types, active and passive voice.
> Minimal pair test confirmed: same words with reversed binding
> ("dog bit cat" vs "cat bit dog") produce flipped attention patterns
> via the same heads.

## Experiment

**Model:** Qwen3-8B (36 layers, 32 Q heads, GQA)
**Method:** 14 probes with hand-annotated expected bindings (which
positions should bind to which). At L27/L30/L33, capture full
attention matrix per head. Measure binding weight = attention from
argument position to function position. Compare to chance (uniform
attention). Ratio > 2 = binding detected.
**Probes:** subject-verb, reversed pairs, ditransitive, self-reference,
nested relative clause, quantifier scope, conditional, passive/active
pair, recursion, discard, long-distance dependency.
**Script:** `scripts/experiments/binding_graph_trace.py`
**Results:** `results/binding-graph-trace/`

## Finding 1: Causal Mask Partitions Binding Direction

| Binding direction | Position order | Result | Mechanism |
|-------------------|---------------|--------|-----------|
| arg → func | arg BEFORE func | 0/23 successful (L27) | **BLOCKED by causal mask** |
| arg → func | arg AFTER func | 12/14 successful (L27) | **Direct attention** |
| arg → func | arg BEFORE func | 2/23 successful (L30) | ~BLOCKED |
| arg → func | arg AFTER func | 14/14 successful (L30) | **Direct attention** |

The causal mask of autoregressive transformers means position N can
only attend to positions 0..N-1. Subject-verb binding (subject comes
first) is impossible via forward attention. The model MUST use one of:

1. **Verb attends back to subject** (func→arg direction) — not measured
   in this experiment but likely the mechanism
2. **Residual accumulation** — subject information flows through the
   residual stream to reach the verb position across layers
3. **FFN incorporation** — the FFN at the verb position already has
   access to the subject via the residual

This experiment measured arg→func direction. The reverse direction
(func→arg) is the natural one for causal transformers and should be
measured next.

## Finding 2: Object→Verb Binding Is Concentrated Attention

When the argument comes AFTER the function (allowed by causal mask),
the binding is unmistakable — single-head attention weights of 0.5-0.8:

### "The dog bit the cat" at L30 (bit(_,cat) binding)

| Head | Weight at "bit" | Ratio vs chance |
|------|----------------|-----------------|
| H13  | **0.785**      | 29.0×           |
| H03  | **0.774**      | 28.6×           |
| H15  | 0.366          | 13.5×           |
| H12  | 0.276          | 10.2×           |

Position "cat" attends 78.5% to "bit" via H13. This IS `bit(_, cat)` —
the argument (cat) binding to the function (bit) via concentrated
attention. The weight is not distributed; it's a near-deterministic
routing decision.

### "Every student reads a book" at L30 (reads(_,book) binding)

| Head | Weight at "reads" | Ratio |
|------|------------------|-------|
| H03  | **0.661**        | 24.5× |
| H12  | 0.322            | 11.9× |
| H15  | 0.209            | 7.7×  |

### "The dog bit itself" at L30 (bit(_,itself) binding)

| Head | Weight at "bit" | Ratio |
|------|----------------|-------|
| H13  | **0.715**      | 25.7× |
| H03  | **0.629**      | 22.6× |

Self-referential binding (itself→bit) uses the same heads as regular
object binding. No special "W combinator head" — consistent with
s188 finding of shared hardware.

### "The dog bit itself" at L30 (itself→dog coreference)

| Head | Weight at "dog" | Ratio |
|------|----------------|-------|
| H07  | **0.239**      | 8.6×  |
| H05  | 0.124          | 4.4×  |

Coreference binding uses DIFFERENT heads (H07, H05) than predicate-
argument binding (H03, H13, H15). There may be two sub-circuits:
predicate-argument heads and coreference heads.

## Finding 3: Minimal Pairs Confirm Binding Flips

### "The dog bit the cat" vs "The cat bit the dog" at L30

| Binding | Probe | Top heads |
|---------|-------|-----------|
| bit(_, **cat**) | rev1 | H13(0.785), H03(0.774), H15(0.366) |
| bit(_, **dog**) | rev2 | H03(0.766), H13(0.719), H15(0.496) |

Same heads, same weights, FLIPPED binding target. When "cat" is the
object, "cat" attends to "bit". When "dog" is the object, "dog" attends
to "bit". The routing is position-structural, not word-dependent.

### Active vs Passive at L30

| Binding | Sentence | Top heads |
|---------|----------|-----------|
| kicked(_, **ball**) | Active: "The boy kicked the ball" | H03(0.595), H13(0.525), H15(0.510) |
| kicked(**boy**, _)  | Passive: "The ball was kicked by the boy" | H12(0.373), H07(0.280), H03(0.268) |

Active patient binding (ball→kicked) uses H03/H13/H15 at high weight.
Passive agent binding (boy→kicked) uses H12/H07/H03 at moderate weight.
The semantic binding is preserved across voice — "boy" still binds to
"kicked" as agent in the passive — but through a partially different
head set and with lower weight.

## Finding 4: The Binding Heads at L30

Consistent across all probes:

| Head | Mean ratio | Bindings > 2× | Role |
|------|-----------|--------------|------|
| H03  | 5.59      | 12/32        | **Primary predicate-argument binder** |
| H13  | 3.91      | 10/32        | **Secondary predicate-argument binder** |
| H15  | 3.30      | 11/32        | **Tertiary binder** |
| H12  | 2.60      | 10/32        | **Ditransitive/passive specialist** |
| H00  | 1.36      | 8/32         | Weak binder (semantic association) |
| H20  | 1.28      | 9/32         | Weak binder (distributional) |

At L27, the binding heads shift: H05 (mean ratio 2.21), H08 (2.64).
At L33, H06 emerges (mean ratio 2.35) — the "universal engine" head
from s188. Binding migrates across layers: early binding at L27 via
H05/H08, peak binding at L30 via H03/H13/H15, late binding at L33
via H06.

## Finding 5: V Vectors at L30 (What FFN Compiled)

The V vectors confirm FFN compilation is context-dependent:

| Position | Token | V promotes (L30) |
|----------|-------|-------------------|
| dog (in "dog runs") | 眺, 一定, 确实 | (Chinese: gaze, certain, indeed) |
| cat (in "cat runs") | char, clicking, Lat | (different from "dog"!) |
| runs | toward, towards, away | (motion semantics, same across probes) |
| bit | nil, slightly, .boolean | (binary/small semantics) |
| cat (in "bit the cat") | char, clicked, atham | (slightly different from subject "cat") |

Same token "cat" produces different V vectors when it's a subject vs
object — context-dependent compilation confirmed at V level.

## Finding 6: Gate Attention Dominates at Early Positions

All subject-verb bindings (arg=position 0) show ALL attention going to
the gate prefix (~97-99%), with near-zero attention to any probe token.
This isn't just causal blocking of forward attention — even the backward
attention from position 0 to earlier positions goes to the gate, not
to other probe positions. Position 0 is an instruction-follower.

## Finding 7: Reverse Binding Confirmed — Verb Attends Back to Subject

The reverse binding experiment (same probes, measuring verb→subject
attention) closes the loop. **The verb DOES attend back to the subject,
with concentrated attention weights comparable to object→verb binding.**

### Reverse binding heads by layer

| Layer | Head | Mean weight | Max weight | Role |
|-------|------|-------------|------------|------|
| L27   | **H31** | **0.366** | **0.823** | Primary subject binder |
| L27   | H29  | 0.142 | 0.376 | Secondary |
| L27   | H12  | 0.128 | 0.226 | Tertiary |
| L30   | **H13** | **0.154** | **0.448** | Subject binder (same as object binder!) |
| L30   | H03  | 0.146 | 0.365 | Same as object binding |
| L30   | H07  | 0.137 | 0.291 | New at this layer |
| L33   | H07  | 0.118 | 0.308 | Late binding |
| L33   | H06  | 0.111 | 0.248 | Universal engine head |

### H31 at L27: The Subject-Binding Head

H31 at L27 is the star finding. "The cat runs" → H31 at "runs" attends
**82.3%** to "cat", and its head output through unembed produces
**"猫, 貓, cats"** — the subject entity in Chinese/Traditional/English.
The verb literally reads the subject and outputs the subject's identity.

| Probe | H31 weight at verb→subject | Head output (what verb "becomes") |
|-------|---------------------------|-----------------------------------|
| The cat runs | 0.823 (runs→cat) | 猫, 貓, cats |
| The dog runs | 0.588 (runs→dog) | 狗, dog, Dog |
| The dog bit the cat | 0.442 (bit→dog) | 狗, dog, Dog |
| The cat bit the dog | 0.429 (bit→cat) | 猫, 貓, cat |
| The dog ran and... | 0.471 (ran→dog) | — |

**The verb position absorbs the subject's identity.** This is the
reverse β-reduction: `(λx.verb(x))(subject)` → the verb reads
`subject` and incorporates it. After this head fires, the verb
position's residual contains information about BOTH the action
(from the V vector compiled by FFN) and the agent (from the
attention-routed subject).

### L30 uses the SAME heads for both directions

At L30, H03 and H13 are the top binding heads for BOTH:
- Object→verb binding (forward): H13=0.785, H03=0.774
- Verb→subject binding (reverse): H13=0.448, H03=0.365

The same heads handle both binding directions. The difference is
which position is doing the attending — determined by which comes
later in the sequence (causal mask).

### The complete picture: binding always flows backward

| Direction | Mechanism | When | Weight | Heads (L30) |
|-----------|-----------|------|--------|-------------|
| Verb → Subject | verb attends back to subject | L27 (early) | 0.37-0.82 | H31, H29, H12 |
| Object → Verb | object attends back to verb | L30 (mid) | 0.66-0.78 | H03, H13, H15 |
| Verb → Subject | verb attends back to subject | L30 (mid) | 0.15-0.45 | H13, H03, H07 |
| Object → Verb | object attends back to verb | L33 (late) | lower | H06, H07 |

All binding flows from later position to earlier position. The causal
mask doesn't block β-reduction — it determines the DIRECTION. The
model implements two-phase binding:
1. **L27**: verb reads subject (gets agent identity)
2. **L30**: object reads verb (gets predicate + binds to it)

### Forward vs reverse detection rates

| Layer | Forward (sub→verb, blocked) | Reverse (verb→sub) |
|-------|----------------------------|---------------------|
| L27   | 0/12 with weight>0.05      | **11/12** with weight>0.05 |
| L30   | 0/12                        | **11/12** |
| L33   | 0/12                        | **12/12** |

When the subject is AFTER the verb (reverse direction), forward binding
already works (10/10 detected). The verb→subject direction completes
the mechanism for the forward case.

## Implications

1. **β-reduction mechanism fully decoded**: Subject-verb binding =
   verb attends back to subject at L27 (H31, 0.82 weight). Object-verb
   binding = object attends back to verb at L30 (H03/H13, 0.78 weight).
   Both are backward attention through the causal mask. Both produce
   the bound entity at the attending position.

2. **Two-phase binding schedule**: L27 = subject binding (verb absorbs
   agent identity). L30 = object binding (argument absorbs predicate).
   The depth ordering IS the reduction schedule — subjects bind first,
   objects bind second.

3. **Shared hardware confirmed again**: H03 and H13 do BOTH directions
   at L30. The binding circuit is universal — same heads, same mechanism,
   just different positions attending depending on sequence order.

4. **Head output IS the reduction result**: H31 at L27 produces "猫"
   at position "runs" when it reads "cat". The head literally outputs
   the argument's identity at the function's position. This is not
   just "attention" — it's the VALUE TRANSFER step of β-reduction.

5. **Compression**: The full binding circuit is:
   - L27: H31 (subject→verb, ~1 head, near-deterministic)
   - L30: H03/H13/H15 (object→verb, ~3 heads, near-deterministic)
   - Each binding = 1 bit (which earlier position to attend to)
   - Total: ~4 heads out of 32 × 36 layers = 0.3% of the model

## Key Numbers

| Metric | Value | Significance |
|--------|-------|-------------|
| Max object→verb weight (L30) | 0.785 (H13, bit→cat) | Near-deterministic |
| Max verb→subject weight (L27) | **0.823 (H31, runs→cat)** | Even stronger |
| H31 output at "runs" for "cat" | 猫, 貓, cats | Subject identity transferred |
| H31 output at "bit" for "dog" | 狗, dog, Dog | Agent identity transferred |
| Reverse bindings detected | 11/12 (L27), 11/12 (L30), 12/12 (L33) | Universal |
| Forward bindings detected | 0/12 (L27), 0/12 (L30), 0/12 (L33) | Causal-blocked |
| Object→verb binding heads (L30) | H03, H13, H15 | 3 heads |
| Verb→subject binding heads (L27) | H31 | 1 dominant head |
| Verb→subject binding heads (L30) | H13, H03, H07 | Same heads as object→verb! |
| Binding circuit size | ~4 heads / 1152 total | 0.3% of model |
