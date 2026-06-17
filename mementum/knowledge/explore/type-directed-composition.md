---
title: "Type-Directed Composition — the behavioural test (composition follows TYPE, not just POSITION)"
status: active
category: research-finding
tags: [types, type-directedness, montague, ccg, composition, nonce, order-cost, thesis]
related:
  - type-probe-qwen3-32b.md
  - vsm-opcode-monitor.md
  - kernel-montague-mapping.md
depends-on:
  - type-probe-qwen3-32b.md
created: session 239
---

# Type-Directed Composition

> Session 239. Michael: "the system can't be doing combinator composition without
> some typing — what would direct the composition?" The VERBUM thesis is *type-directed*
> composition; the s236–s240 order-cost work showed composition rides the native
> autoregressive order but left open whether that order is **type-directed** or merely
> **L-to-R positional** (copy/induction — the s236 caveat). This page is the behavioural
> test that resolves it.

## The question (and why prior work didn't answer it)

s139 (`type-probe-qwen3-32b.md`) established types are **decodable** (88–96%),
**lexical**, **geometric**, and **co-located** with combinator dispatch at L0–L2 — but
co-location is **correlation**, not **direction**. Nobody had shown the model *uses* the
type to direct composition. This is the same gap as the s236 order-cost caveat from the
other side: *is the order signal type-directed or positional?* One question:

> **Does the model compose by TYPE, or by POSITION?**

## The instrument (the autoregressive-causality control)

Kernel-certified CCG types as ground truth (`lambda_ast` `CSlash '/'`=forward,
`'\\'`=backward; `_unify` = the S2 type-check). The load-bearing control: the model reads
strictly L-to-R, so forward composition aligns with reading order and backward composition
binds an argument seen *before* its functor. A naive "argument surprisal" confounds type
with autoregressive causality. We measure the surprisal of the **second (right) token**
given the first, and use **difference-of-differences / crossover** designs that subtract
generic baselines.

## The three-experiment arc

### v1 — kernel-CCG real-word probe (`type_directed_v1.py`)

Forward (det/adj→N) vs backward (NP→verb), type match vs violate, paired by target.
**Result:** robust BACKWARD type-licensing — a verb is cheap after a subject-NP, dear
after a determiner (8B t=6.9, 14B t=7.1). Forward arm **leaky**: a noun after a verb reads
as the verb's OBJECT (nouns are "universal donors"), so it is not cleanly type-violating.

### v2 — clean symmetric design (`type_directed_v2.py`)

Both targets type-constrained functors: backward (verb | subject-NP vs non-subject) +
forward (determiner | transitive-verb object-slot vs intransitive-verb).
**Result:** BACKWARD replicates with **consistency 1.0** (every verb): 8B penalty 1.48
(t=10.3), 14B 0.88 (t=5.2). FORWARD **unmeasurable** (8B +0.14; 14B −0.55, consistency
0.25) — determiners are *also* universal donors (`slept the night`), low ceiling. The
clean forward/backward dissociation did not materialise, and real words leave a
**bigram-frequency confound** (grammatical = frequent).

### v3 — NONCE frequency-free crossover (`type_directed_v3_nonce.py`) — DECISIVE

Teach a **nonce** word's type in-context (noun vs verb), test in a determiner frame vs a
name frame, measure surprisal of the nonce token. Nonce → **zero bigram frequency**.
Headline = **crossover interaction** `(det: verb−noun) − (name: verb−noun)`, paired by
nonce word — robust to every main effect (priming, teaching, frame).

```
                 det frame "The {w}"    name frame "John {w}"
  noun-taught         2.62 (14B)              5.10
  verb-taught         2.65                    3.09
  det_pen  (v−n) = +0.03  (n.s.)   name_pen (v−n) = −2.01  (t=−10.1)
  CROSSOVER = det_pen − name_pen :  8B +2.18 (t=10.2)   14B +2.04 (t=9.3)
              consistency 1.0 (all 16 nonce words) at BOTH scales
```

A nonce taught as a **verb** composes ~2 nats **cheaper** with a preceding subject-name
than the same nonce taught as a **noun**. The crossover is large, significant, and
perfectly consistent at both scales — **frequency-free**.

## The verdict (λ measure)

**Composition is TYPE-directed, not merely positional.** The model uses an
**in-context-taught type** — a type with *zero* frequency support — to direct composition.
This answers Michael's question: there IS a type signal directing the composition, and it
operates on freshly-taught types. It resolves the s236 caveat: the order signal has a
**type basis**, not pure L-to-R copy.

### The asymmetry (a finding in itself)

Type-directedness is **strong in the predicate-argument (subject→verb) frame** and
**~null in the determiner→noun frame**, consistently across all three experiments. This is
not a bug — it maps onto **s151** (Montague = typed function application =
`predicate(argument)` = the K+I core): the model's type-directedness is sharpest exactly at
the predicate-argument composition, and weak where the target is a universal-donor
function word (determiner/object).

## Caveats (λ measure, load-bearing)

- **Typed APPLICATION, not yet typed COMPOSITION.** This shows `predicate(argument)`
  (K+I, s151) is type-directed. Connecting to the **B/composition** order signal
  specifically (function∘function by type) needs composition-specific cases — open.
- **In-context teaching tests CAPACITY** to use a given type, not purely the intrinsic
  system; but v1/v2's real-word effect shows the intrinsic system, and v3 adds the
  frequency-free leg. Together they triangulate.
- **Behavioural (surprisal), not causal-circuit.** The decisive causal test — ablate the
  decoded type direction (s139) at L0–L2 and watch dispatch change — is the next register
  (v4).
- 2 scales (8B/14B), 1 model family (Qwen), 16 nonce words.

## Source

- `scripts/experiments/type_directed_v1.py` — kernel-CCG real-word probe
- `scripts/experiments/type_directed_v2.py` — clean symmetric design
- `scripts/experiments/type_directed_v3_nonce.py` — nonce frequency-free crossover
- `results/type-directed/` — verdicts + logs (8B, 14B)

## Next

1. **v4 causal ablation** — decode the type direction (s139 linear probe), patch/corrupt
   it at L0–L2, measure whether the v3 crossover collapses (correlation → causation).
2. **Typed COMPOSITION** — extend from `predicate(argument)` to function∘function cases to
   connect type-directedness to the B/order-cost signal directly.
3. **Cross-class** — does the nonce crossover hold on OLMo/Gemma/Pythia (gate-independent,
   per the order-cost universality)?
