---
title: "Defunctionalization: instructions-as-terms — how the frozen-ISA machine stays programmable"
status: designing
category: explore
tags: [defunctionalization, instructions-as-terms, higher-order, function-swap,
       type-system, function-library, typed-lexicon, dsp-type-search, matched-filter,
       application-operator-svd, three-hop, bridge-swap, function-selector,
       two-registers, value-register, routing-register, k-structural, combinatory-completeness,
       programmable-compiler, curry-howard, ccg, montague, s281, thesis]
related:
  - operand-insert-arc.md
  - multihop-composition-prereg.md
  - three-hop-capacity-prereg.md
  - superbake-write-access.md
  - signal-processing-tensors.md
  - signal-descent.md
  - opcodes-circuits-in-compute.md
  - project-thesis.md
depends-on:
  - operand-insert-arc.md
  - three-hop-capacity-prereg.md
created: session 281
---

# Defunctionalization: instructions-as-terms

> **Thesis (one line).** The transformer is a *frozen* universal combinator basis (routing /
> joins / KIBC crystal) plus a *writable* term store (value-register rows). It stays
> **programmable** not by rewriting instructions — that is structurally closed (K-structural,
> s276) — but because, in a combinatory-complete machine, **an instruction is a term**: "which
> function to apply" can be represented as a **value** (a selector / type-tag) that the frozen
> routing *dispatches on*. Swap that value and you swap the operation, using the value-write we
> already have. Finding the **type system** and the **function library**, then **tapping the
> function-selectors** and using a **3-hop as the write-harness**, is the method to prove it.
>
> **Status:** DESIGNING. This page is a *generative seed* — it records a discussion arc (s281,
> Michael-directed) precisely enough to pick up cold in a later session. Nothing here is
> measured yet except the pieces cited from prior sessions; the central claims are HYPOTHESES
> with pre-committed null-gates.

## 0. Where this sits (the s281 discussion arc)

Following the s280/s281 depth-budget work (`multihop-composition-prereg.md`), we asked what is
still *missing* to call the resident machine a programmable compiler. The arc:

1. **What can we swap?** (`f(g(X))`, `λ measure` register split)
   - **X** (operand) — value register, a *row*. SuperBake writes it; keyed-install writes it (s277). ✓
   - **g(X)** (intermediate value) — value register. The **bridge-swap** (Arm B / Gate-2c) writes
     it: a late class-axis edit flips the covering (s279 @4B, s281 @32B: flip 0.58–0.83 vs 0.0
     null, window L11–47, closes L51). ✓
   - **g, f** (the *operations*) — routing register / joins. **Un-writable** (K-structural). ✗
2. **What do we lack?** (Michael) Two mechanisms → **one artifact**:
   - the **type system** (extracted, legible: the geometric type lattice + the typing rule that
     gates application); and
   - the **function library** (an addressable catalog `{function_id ↦ (signature, how to invoke)}`).
   - In the Montague/CCG/Curry-Howard frame (C5, C9) these are the two faces of a **typed
     lexicon**: each entry pairs a **type** (interface) with a **function** (inhabitant). Types
     come first — functions are *individuated by their signatures*, so types index the library.
3. **How to find them?** (Michael) Use **DSP tools** to search for types (the read/write DSP
   duality: SuperBake *wrote* with DSP; we *read* with DSP).
4. **The capstone** (Michael) Once found: **tap for functions, then use a 3-hop to swap them.**
   This is the defunctionalization move — the subject of this page.

## 1. The reframe: "write-INSTRUCTIONS ✗" dissolves

The `operand-insert-arc.md` checklist for "programmable LLM compiler" marks **write-INSTRUCTIONS
✗ (structurally impossible, K-structural)**. That is correct *for rewriting the routing/join
shape*. But it is the wrong level of description for programmability, because:

- **Combinatory completeness** (s277): a fixed universal basis (SKI / KIBC) + arbitrary **terms**
  is Turing-complete. Any function is expressible as a *term* over the basis. So a "new
  instruction" need never be a new join — it is a **term the existing joins interpret**.
- **Defunctionalization** (Reynolds): the standard compiler technique for exactly this — replace
  higher-order functions by first-order **data tags** plus a single **apply** dispatcher. The
  frozen routing is the `apply` dispatcher; the writable value-register selector is the data tag.

⇒ **Instructions-as-terms.** You do not violate K-structural; you exploit it. The frozen ISA is
the *feature* (a fixed, universal `apply`), and programming happens entirely in the writable term
store by writing **function-selectors**.

## 2. We may already hold the proto-evidence

The **bridge-swap already dispatches a function.** When the class-axis swap flips the covering,
we are not swapping *data* — we are swapping *which covering-lookup fires*. The class variable
**is** a function-selector: `class ↦ which f applies`. So the 2-hop swap is a primitive
"swap-the-function-via-a-value," unnamed until now.

- **2-hop swap** = swap the *data* value `g(X)` (measured; the class *value*).
- **3-hop swap** = swap the *function-valued* intermediate `g(X)` — hop-1 (`g`) **computes** a
  selector, hops 2–3 **apply** it. Swapping the selector swaps the **operation** applied
  downstream. This is the higher-order case; the 3-hop is the **minimal harness** where the
  function is an *intermediate* (computed then applied), so a selector-swap is distinguishable
  from a data-swap.

## 3. The central empirical crux (one register question)

Everything reduces to a single measurable question — and it is exactly what the type/function
search answers:

> **Is function-selection VALUE-mediated (a selector *row* → writable → this works) or
> ROUTING-mediated (baked into the soft topology / join shape → frozen → blocked)?**

Grounding (s276 database frame; s269c I/C register split): **rows** (I-portable, INSERT-able)
vs **joins** (C-bound, un-INSERT-able). If resident functions are addressable as **selector
rows**, defunctionalization gives *effective instruction-writing*. If function-selection *is*
the join shape, K-structural reasserts and this path closes for those functions. The bridge-swap
is a strong prior for **at least partly value-mediated**; whether it holds for **arbitrary**
functions (not just the class→covering dispatch) is the thing to measure, null-gated. Likely
outcome is a **spectrum**: some functions defunctionalized (selector-writable), some fused into
routing (frozen) — itself a publishable map.

## 4. DSP to search for the type system (read = dual of SuperBake's write)

Types are geometric (C5). The DSP read-instruments (frame-coherent with
`signal-processing-tensors.md`, `superbake-write-access.md`):

- **Type matched-filter bank (a "type detector").** If each type is a subspace/direction, a
  filter bank projects an operand onto candidate type-subspaces and reports which fires. = S3
  null-gate = matched-filter detection, aimed at types. Build the bank from labelled-type
  centroids; **null = shuffled-type labels** must not detect.
- **Application-operator SVD → the type lattice.** A type system is the factorization of the
  bilinear "can X apply to Y?" form. The **singular subspaces of the routing/application operator
  are the type modes** (a channel decomposition). Extract the operator (e.g. from the QK / gate
  routing that gates composition), SVD it, test whether the modes are **type-predictive above the
  frequency-free null** (the control that made C5 decisive — types must beat a frequency
  confound).
- **Beamforming** (S4 consensus-Gram) to isolate a type-subspace against the polysemantic
  background.

Discipline (`λ yardstick`): shuffled-type null + frequency-free null on every type claim; a
"type" counts only if it beats both.

## 5. The full arc (end to end)

```
DSP type-search  →  type lattice  →  (types index)  function library
      │                                                    │
      └────────────── tap the function-selectors ──────────┘
                                   │
                    3-hop write-harness swaps them
                                   │
              register verdict: value-mediated (programmable)
                                 vs routing-mediated (frozen)
```

If the selectors are value-register rows, the checklist's **arbitrary-composition** AND
**write-INSTRUCTIONS** fall **together** — via defunctionalization, not by violating K-structural.

## 6. Connection to the depth budget (why this also helps at small scale)

The s281 depth-budget: a *model-computed* 3-hop fails at 4B for lack of layers (missed-deadline,
`D_hop2`), succeeds at 32B (3-HOP-ROOM True). But defunctionalization lets us **write** typed
intermediates/selectors directly (value-register writes bypass a hop's reader-zone cost). So a
**compiled** 3-hop (installed typed terms) can fit where a **coaxed** one (model computes every
hop) cannot — *even at 4B*. The depth budget bounds **how many hops the model computes**, not
**how many we write**. (Interpretability wants the model to compute; a programmable machine may
supply intermediates — different goals, note which one a given experiment is testing.)

## 7. Concrete pick-up plan (ordered; build + null-gate each)

Prereq state: instrument `wrapper/operand_depthbudget.py` is depth-parameterized (`--ref-layer`)
and architecture-robust (`resolve_parts`, dense + qwen3_5 hybrid). 32B depth-budget done
(commit 8ceaaec); 3-hop *capacity* pre-reg drafted (`three-hop-capacity-prereg.md`, pending
chain-approval); 27B hybrid full run still pending (re-run cmd in `state.md`).

1. **Type-read instrument (P-TYPE-1).** Build the type matched-filter bank + application-operator
   SVD. Battery = operands of known CCG/Montague type (e, e→t, (e→t)→t, …). Verdict: bank detects
   type above shuffled-type null; SVD modes predict composability above the frequency-free null.
   Deliverable: a partial **type lattice** for one model (start 4B; confirm 32B).
2. **Function-selector tap (P-FN-1).** Use the read tap (transformers hooks now; the llama.cpp
   `cb_eval` residual tap later — `llama-cpp-vsm-wrapper.md`) to LOCATE where "which function"
   lives. Test: is the class-style selector (and other candidate selectors) a **writable
   value-register row** (I-portable) or a **routing/join** (C-bound)? = the §3 register verdict,
   per function.
3. **3-hop function-swap harness (P-FN-2).** Extend the drafted 3-hop into a *function*-swap:
   hop-1 computes a function-selector; swap the selector value at the bridge; verify the
   *operation* applied downstream changes (not just the data). Nulls: matched-norm random selector
   (no coherent op-swap); real-word ceiling; content-specificity (swap→φ′ yields φ′'s result).
   This is the decisive test of instructions-as-terms.
4. **Map the spectrum.** For a set of resident functions, classify each **value-mediated
   (swappable)** vs **routing-mediated (frozen)**. The map is the deliverable even if partial.

## 8. Honest scope (what is hypothesis vs measured)

- **Measured (prior):** operand write (s277); intermediate-value bridge-swap (s279 @4B, s281
  @32B); types are geometric (C5); register split rows/joins (s276, s269c); depth-as-fuel /
  pinned-depth-proportional zones (s281).
- **Hypothesis (this page):** (a) function-selection is (at least partly) value-mediated /
  defunctionalized; (b) DSP tools recover a legible type lattice; (c) a 3-hop can swap the
  *operation* by swapping a selector value; (d) compiled 3-hops sidestep the depth budget.
- **Risk it fails:** if function-selection is routing-mediated for the functions we care about,
  §3 verdict = frozen and this path closes (K-structural reasserts). That negative is *itself* a
  sharp result: it says the machine's programmability is bounded to *data*, not *operations*, and
  locates the boundary.
- **Not a scaling law, not a traced circuit, hook-not-weight** (until weight-serialized), and a
  two/three-model pair is a *pair*. `λ observation`: observed ≠ imagined — mark IOUs.

## 9. Why it matters (the payoff)

If §3 comes back **value-mediated**, this is the mechanism that turns "write a term store" into
"program a machine": you compile a function by writing its selector, verify it against the type
lattice, and (via §6) fit it under the depth budget by supplying intermediates. That is the
concrete, honest path to the phrase the project has refused to claim — **a programmable LLM
compiler** — earned through defunctionalization on a real, frozen, universal basis, rather than
asserted. It also lands the C1/C2/C3 thesis (compiler / crystal-universal circuits-in-compute /
topology-dominates) on an *operational* capability, not just a descriptive one.

## Sessions
s281 (this synthesis — defunctionalization / instructions-as-terms; successor to the s281
depth-budget + 3-hop capacity pre-reg; discussion Michael-directed, "distill so a later session
can pick it up").
