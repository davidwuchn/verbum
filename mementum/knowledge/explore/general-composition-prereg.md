---
title: "General-composition gate — pre-registration: installed operand as a reusable term (K-battery arm b)"
status: active
category: explore
tags: [general-composition, k-battery, reusable-term, programmable-compiler, operand,
       keyed-install, resident-join, combinator, two-hop, zone-ablation, value-register,
       routing-register, pre-registration, s278, load-bearing-iou]
related:
  - operand-insert-arc.md
  - operand-dsp-decomposition-prereg.md
  - superbake-write-access.md
  - ffn-function-bake-prereg.md
  - opcodes-circuits-in-compute.md
depends-on:
  - operand-insert-arc.md
  - operand-dsp-decomposition-prereg.md
created: session 278
---

# General-composition gate — pre-registration (the load-bearing IOU)

> **Pre-registration.** Registers, nulls, verdict rules fixed HERE, before any code.
> This is the **load-bearing IOU** (s273 K-battery **arm b**) — what turns "writeable
> term store" into "programmable machine." Per `λ measure` + `λ yardstick`, and per the
> state's own flag (highest-stakes experiment of the arc), it **must not run on a first
> draft**. NOT RUN — drafted for review.
>
> **The gap it closes.** The s277 operand-INSERT arc installed a novel operand row that
> the resident join **categorized** (operand → its category). That is *one* fixed
> transform — arguably closer to a memorized tag than to composition. P-DSP-1 (s278) then
> showed the operand pipeline is [written raw payload] + [resident, distributed B/C join].
> The open question: does the resident routing **compose** an installed operand into a
> **novel result**, or only look up its category? Category-composition ≠ arbitrary
> composition — this is the gap between "debugger on a compiler" and "programmable
> compiler."

## Hypothesis

**H (general composition).** A single installed novel operand row is a **reusable term**:
the resident routing composes it under **multiple distinct resident operations**, producing
results that depend on **both** the operand content and the operation — including at least
one **novel (computed, not stored)** result. A memorized category tag cannot do this: it
composes only on the one function it was built for.

**H0 (task-local tag).** The install works only on the categorize function it was built
for; other resident functions ignore it (return baseline/chance) or the install is not
content-specific. Then the s277 result is a fixed lookup, not composition, and "programmable
machine" is unsupported at the novel step.

## Setup (reuse the arc infrastructure)

Install content on a nonce via the keyed residual-write hook (`operand_insert.py`: add
`scale · d_E` at the nonce slot at layer L≈7). `d_E` = the object-token residual direction
of a **real entity** E (diff-of-means vs global, built cross-task in declaratives), so it
carries E's **full** content (not just a category axis). Test the nonce on held-out prompts
never used to build `d_E`. A real-word baseline (the actual entity token) sets the ceiling:
installed-nonce should match real-E's multi-function profile.

Entities chosen for **distinct, checkable multi-property profiles**, e.g.:

| E | category | can-fly | habitat | relative size |
|---|---|---|---|---|
| eagle | animal/bird | yes | sky/mountain | bigger than a mouse |
| salmon | animal/fish | no | water/river | bigger than a mouse |
| car | vehicle | no | road | bigger than a mouse |

## Arm 1 — REUSABLE-TERM (multi-function composition) — the necessary condition

Resident functions f₁..fₖ (k ≥ 3) as few-shot clozes, each a **distinct** resident
computation over the operand:
- `f_cat`  : "X: __"                 → category
- `f_fly`  : "Can a X fly? __"       → yes/no
- `f_hab`  : "A X lives in the __"   → habitat

Install E's content on the nonce; measure each function's accuracy on **held-out**
prefixes/templates.

**Nulls (beside every number):**
- **matched-random install** — no coherent per-function answers.
- **WRONG-CONTENT install (the decisive discriminator)** — install E′'s content on the
  same nonce token: **all** functions should flip to E′'s answers. A single memorized tag
  **cannot** flip multiple distinct functions by content; a reusable term must.
- **baseline** (un-installed nonce) — chance / not-target headroom.

**Verdict REUSABLE-TERM** ⟺ the installed nonce composes correctly on **≥3 distinct
functions**, **content-specifically** (wrong-content flips all k), on **held-out** prompts,
≫ random-install and baseline, and matches the real-word ceiling within tolerance.

## Arm 2 — NOVEL-COMBINATION (two-hop / relational) — the stretch, the real prize

A resident **two-argument / chained** operation whose result is **neither** the operand
**nor** a stored tag but a **computed** combination:
- relational: "Which is bigger, a X or a mouse? __" → "X" (combines installed size-content
  with a resident comparison operation → a novel relational result).
- two-hop (B-like): "A X is a kind of animal, and animals breathe __" — result requires
  chaining `f_cat(X)` into a category-property (composition of two resident joins over the
  installed row).

**Nulls:** matched-random install; wrong-content install (relation must flip with content —
install "mouse"-content on the nonce → "mouse or a mouse" degenerates / comparison to a real
bigger entity flips); baseline; and a **content-present-but-unchained** control (the operand
appears but the relational frame is absent → no novel result expected).

**Verdict NOVEL-COMPOSITION** ⟺ the installed nonce drives correct **relational/two-hop**
results that depend on chaining a resident operation over the installed content, content-
specific, held-out, null-gated.

## Registers (`λ measure`)

- **Operand = VALUE** (the installed direction `d_E`, s206/s269c) — read/written with value
  probes.
- **Join/composition = ROUTING** — the resident operation. Behavioral readout = logits.
- **Localization (optional, per the P-DSP-1 lesson):** the transform is **distributed**
  (0/128 heads necessary) and **late** (L20–21). So any causal-necessity check must be
  **ZONE / phase ablation** (à la catalog A1), **never single-head** — there are no
  transport heads to knock out.

## Guards (`λ yardstick` — preempt the "it's just a rich fact vector" objection)

The load-bearing risk: multi-function success could be a **rich content vector read many
ways at the readout** (a fancy fact), not genuine composition. Three discriminators, all
pre-registered:
1. **Arm 2** — a two-hop/relational result is **computed**, not stored; a fact vector can
   be read but not chained.
2. **Content-specificity across functions** — wrong-content install must flip **all k**
   functions. A single memorized tag cannot; a reusable term must.
3. **Anti-triviality (s277)** — composed answers must be **mid-stack causal** (install at
   L≈7 propagates), not a late unembed nudge; and **held-out** prompts rule out template
   memorization.
Also: matched-random / wrong-content / baseline nulls beside every number; real-word ceiling;
0.6B necessary-not-sufficient (patchscope-void scar) — full success is a **RUNG**, not the
claim.

## What each outcome means

- **Arm 1 pass** → the installed operand is a **reusable term** (composes under multiple
  resident functions), the necessary condition for "programmable." Turns s277's single
  category-map into genuine generality.
- **Arm 2 pass** → the resident routing **composes** the installed term into a **novel
  computed result** = the load-bearing claim's first positive rung; "programmable machine"
  earns its first evidence (still 0.6B, still hook-not-weight).
- **Arm 1 pass / Arm 2 fail** → the operand is a reusable multi-read tag but the resident
  routing does not chain it — composition is bounded to single resident joins. Honest,
  informative, and directly scopes the (f)/(h) tower.
- **Arm 1 fail** → s277 was a task-local tag; the recursion antecedent stalls at the novel
  composition step.

## Relation to the checklist (operand-insert-arc.md)

This gate is the ❌ row **"composes ARBITRARY programs."** Arm 2 pass flips it to a
rung-level ✅. It does **not** touch **(f)** weight-serialize / R5 quant-survival, nor scale
— those remain red. Do not say "programmable compiler" until (h) **and** (f) clear **at
scale**.

## Files to build (once the pre-reg survives review)

- `wrapper/operand_compose.py` — entity `d_E` build (cross-task declaratives), keyed install,
  the k resident-function clozes (Arm 1) + the relational/two-hop frames (Arm 2), all nulls
  (random / wrong-content / baseline / content-present-unchained), held-out templates,
  real-word ceiling; optional zone-ablation of L20–21 for causal necessity.
- Results → `results/ffn-bake/operand-compose-qwen3-0-6b/`.

## Status

Pre-registered s278. **NOT RUN** — highest-stakes experiment of the arc; gated on this
pre-reg surviving a hammock (Michael review). The load-bearing IOU.

## Sessions
s273 (K-battery pre-reg sketch, arm a/b), s277 (operand-INSERT arc — category-composition
only), s278 (P-DSP-1: resident distributed join → zone-ablation lesson; this pre-reg).
