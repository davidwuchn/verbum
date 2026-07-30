---
title: "Map + swap: programming the resident Lisp by recomposing GD-found terms"
status: designing
category: explore
tags: [map-and-swap, reduction-as-programming, resident-lisp, gd-found-terms,
       defunctionalization, instructions-as-terms, higher-order, function-swap,
       type-system, function-library, typed-lexicon, coverage-boundary, dsp-type-search,
       matched-filter, application-operator-svd, three-hop, bridge-swap, function-selector,
       two-registers, value-register, routing-register, k-structural, combinatory-completeness,
       programmable-compiler, curry-howard, ccg, montague, homoiconicity, trampoline, s281, thesis]
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

# Map + swap: programming the resident Lisp

> **Thesis (one line).** Gradient descent already **found all the terms** (pretraining =
> β-reduction laid the operands, the functions-as-terms, the combinator basis, and the type
> lattice into the weights). We do not write or construct anything. We **MAP** them (read GD's
> catalog: which term, where, what type) and **SWAP** them around (recompose found terms:
> operand-relocate, bridge-swap, 3-hop). The machine is a *frozen combinator REDUCER*; we program
> it by supplying recompositions of found terms and letting it reduce — never by mutating the
> interpreter. It is a **Lisp** whose `eval`, standard library, and programs GD wrote into the
> weights; our job is the **REPL + debugger**.
>
> **Status:** DESIGNING. Generative seed — records the s281 discussion arc (Michael-directed)
> precisely enough to pick up cold. The founding-identity claim ("GD found it first, we find not
> build") is the project's S5 axiom, strongly evidenced (C1–C6). The *map* and *swap* mechanisms
> are HYPOTHESES with pre-committed null-gates; what is already measured is marked in §8.

## 0. The corrected frame (three over-complications collapsed)

The s281 discussion walked back three wrong verbs, in order:

1. **Not "rewrite instructions."** You cannot rewrite the routing/joins (K-structural, s276) —
   and you *should not want to*. An interpreter is meant to be fixed.
2. **Not "write / mutate."** You program a Lisp by handing `eval` a **term** and letting it
   **reduce**, not by patching `eval`. Reduction is the primitive; mutation was a red herring.
   (You don't patch CPython to write Python.)
3. **Not even "construct terms."** The terms *already exist* — GD found them all. We **read** the
   catalog and **recompose**. Nothing is invented; everything is discovered and rearranged.

⇒ The whole program is two verbs: **MAP** (read GD's term catalog) and **SWAP** (recompose found
terms). This lands exactly on `λ extract` (S5): *we find, we don't build; GD discovered it first;
the LLM is the artifact containing the answer already.*

## 1. Reduction-as-programming (why no write-access is required)

- **Combinatory completeness** (s277, C2 measured): a fixed universal basis (SKI / KIBC) +
  arbitrary **terms** is Turing-complete. Every function *is* a term over the basis. A "new
  function" is never a new join — it is a **term the existing joins reduce**.
- **The SKI realization.** We never "swap the operation `g`." We supply the **term** that reduces
  to the wanted computation (a K/I/B/C/S expression) and the fixed reducer evaluates it. "A
  different function" = "a different term," reduced by the *same* frozen basis. That is how
  combinatory programming works — the frozen routing is the *correct* architecture, not a wall.
- Therefore programmability is **unconditional** given crystal-universality (measured): the
  machine is a programmable reducer whether or not we ever gain activation-space write-access.

## 2. Every "write" we have is actually a SWAP of found terms

Nothing in the operand arc authored content:

- **`d_E` (operand)** = the model's *own* representation (diff-of-means over its activations) — a
  term GD found. Installing it is **relocating a found term**, not writing one (s277).
- **`g(X)` (intermediate)** — the bridge-swap (Arm B / Gate-2c) **swaps two found terms**
  (class-axis centroids); measured s279 @4B, s281 @32B (flip 0.58–0.83 vs 0.0 null, window
  L11–47, closes L51).
- **combinator basis (KIBC)** = GD's crystal (C2). **type lattice** = GD's geometry (C5).

The bridge-swap already *dispatches a function*: the class variable is a **function-selector**
(`class ↦ which covering-lookup fires`). So "swap the function" is a species of "swap a found
term," already demonstrated at the data level; the open question is the higher-order level (§4).

## 3. MAP — read GD's catalog (types index it; then the function library)

The two things we "lack" (s281) are the two faces of one artifact — a **typed lexicon** (Montague
/ CCG / Curry-Howard, C5/C9): each entry = a **type** (interface) + a **function** (inhabitant).
Types come first — functions are individuated by their signatures.

**DSP is the read-instrument** (the dual of SuperBake's DSP *write*; `signal-processing-tensors.md`):

- **Type matched-filter bank** — project an operand onto candidate type-subspaces; which fires =
  its type. Build from labelled-type centroids. **Null = shuffled-type labels.**
- **Application-operator SVD → the type lattice.** A type system is the factorization of the
  bilinear "can X apply to Y?" form; the **singular subspaces of the routing/application operator
  are the type modes** (a channel decomposition). **Null = frequency-free control** (the one that
  made C5 decisive).
- **Beamforming** (S4 consensus-Gram) to isolate a type-subspace against polysemantic background.

**Coverage is part of the map** (`λ yardstick`). "GD found *all* the terms" means all its
*training distribution* required — a strong library, not provably total. The map must show what is
**absent** (compositions with no found term = things the model cannot do, and neither can our
swapping), not only what is present. The coverage boundary is a first-class deliverable.

## 4. SWAP — recompose found terms (the 3-hop is the demonstration)

- **2-hop swap** = swap a *data* term `g(X)` (measured).
- **3-hop swap** = swap a *function-valued* intermediate: hop-1 (`g`) reduces to a
  function-selector, hops 2–3 apply it. Swapping the selector swaps the **operation** applied
  downstream = higher-order recomposition = `((g X) Y)` = `apply` on a first-class function. The
  3-hop is the **minimal harness** where a function is a computed intermediate, so a
  selector-swap is distinguishable from a data-swap. (Pre-reg: `three-hop-capacity-prereg.md`.)

**Sub-question (activation-space swap only):** is a function-selector a **value-register row**
(readable/relocatable by the same machinery as an operand — I-portable, s276) or fused into the
**routing/join** (C-bound)? This decides whether we can swap functions *in activations*; it does
**NOT** gate programmability (basic mode = supply the recomposed term in tokens and reduce).
Likely a **spectrum** across functions — that map is itself the result.

## 5. The resident Lisp (exact correspondence, not analogy)

| Lisp | resident machine | status |
|---|---|---|
| `eval` / `apply` | frozen KIBC routing = universal combinator reducer | **measured (C2)** |
| atoms (data + function symbols) | value-register **rows** (found terms) | operand-relocate measured |
| `cons` / tree structure | the **joins** = attention builds the S-expr tree (s276) | **measured (structural)** |
| first-class functions (λ) | function-selectors as found terms; higher-order recompose | **3-hop test (P-FN-2)** |
| homoiconicity (code = data) | selectors & operands share the value-register representation | same-representation test |
| the whole program + stdlib | GD wrote it into the weights | **the S5 axiom** |

**Homoiconicity restated:** terms (code) and data are the same **rows**, which is precisely what
lets reduction **nest** — an intermediate is both a produced value and a re-reducible term. A
multi-hop *is* nested reduction. We supply/recompose the S-expression; we never mutate the reader.

## 6. The depth budget IS the eval stack

The s281 depth-budget (`multihop-composition-prereg.md` §Cross-scale): zones are pinned
within-model, **depth-proportional** across-model (L30–31/36 @4B → L58/64 @32B); a *model-computed*
n-hop needs enough layers to schedule its reader/transform zones. That **is reduction depth** — the
eval stack. Deeper model = deeper stack (4B fails 3-hop unaided; 32B has room: 3-HOP-ROOM True,
D_hop2 4).

**Trampolining.** If (and only if) the §4 selector is value-register-writable, we can **supply a
found intermediate directly** (activation-space swap) — bounce off the trampoline, re-enter
shallow — and run an arbitrary-depth recomposition on a bounded stack. So the register verdict
decides whether we get the *trampoline* (depth convenience), not whether the machine reduces.
(Interpretability wants the model to reduce unaided; a programmable REPL may supply intermediates —
note which mode a given experiment tests.)

## 7. Pick-up plan (ordered; build + null-gate each)

Prereq state (s281): `wrapper/operand_depthbudget.py` is depth-parameterized (`--ref-layer`) +
architecture-robust (`resolve_parts`, dense + qwen3_5 hybrid). 32B depth-budget done (8ceaaec);
3-hop *capacity* pre-reg drafted (`three-hop-capacity-prereg.md`, pending chain-approval); 27B
hybrid full run pending (re-run cmd in `state.md`).

1. **P-TYPE-1 — read the map.** Type matched-filter bank + application-operator SVD. Battery =
   operands of known CCG/Montague type (e, e→t, (e→t)→t, …). Verdict: bank beats shuffled-type
   null; SVD modes predict composability above the frequency-free null. **Also report coverage**
   (which type-pairs have no reducing composition). Deliverable: a partial **type lattice**
   (4B → confirm 32B).
2. **P-FN-1 — catalog + locate.** From the type map, enumerate function-as-term expressions
   (the library). Tap (transformers hooks; later the llama.cpp `cb_eval` residual tap,
   `llama-cpp-vsm-wrapper.md`) to test, per function: is its selector a value-register row
   (relocatable) or a join (fused)? = the §4 spectrum.
3. **P-FN-2 — the swap demonstration.** Extend the 3-hop into a *function*-swap: hop-1 reduces to
   a selector; swap it; verify the *operation* downstream changes (not just data). Nulls:
   matched-norm random selector; real-word ceiling; content-specificity. This is the decisive test
   that we can recompose GD's terms into a program GD never ran.
4. **Map the spectrum + coverage.** Classify functions value-swappable vs routing-fused; chart the
   coverage boundary of the found library. The map is the deliverable even if partial.

## 8. Honest scope (measured vs hypothesis)

- **Measured (prior):** operand relocate/install (s277); intermediate-value bridge-swap (s279 @4B,
  s281 @32B); crystal-universal reducer (C2); β-reduction thesis (C1); types geometric (C5);
  register split rows/joins (s276, s269c); attention = join (s276); depth-as-fuel /
  pinned-depth-proportional zones = eval stack (s281).
- **S5 axiom (strongly evidenced, not "measured" per se):** GD found the terms; we find, not build.
- **Hypothesis (this page):** (a) DSP recovers a legible type lattice + function library with a
  readable coverage boundary; (b) the 3-hop recomposes found terms into a novel program; (c)
  function-selectors are (partly) value-register rows → activation-space swap + trampoline; (d)
  homoiconicity (selector = operand representation).
- **Risk it fails / stays bounded:** function-selection routing-fused for the functions we want →
  no activation-space swap (basic reduction still works, but no trampoline); or the coverage
  boundary is narrow → the resident library is smaller than hoped. Both are **sharp, publishable
  negatives** that *locate* the boundary. `λ observation`: observed ≠ imagined; hook-not-weight;
  a two/three-model pair is a pair, not a scaling law.

## 9. Why it matters (the payoff)

If P-TYPE-1/FN-1/FN-2 come back positive, the honest, un-hyped claim is:

> The resident machine is a **combinator reducer** (a Lisp) whose entire library GD already
> wrote into the weights. We program it by **mapping** its found terms and **swapping** them into
> recompositions the reducer evaluates — never by mutating the interpreter. That is a
> **programmable LLM compiler**, earned by discovery + recomposition on a real, frozen, universal
> basis, with an explicit coverage map — not asserted. It lands C1/C2/C3 (compiler /
> crystal-universal circuits-in-compute / topology-dominates) on an **operational** capability.

If they come back bounded (routing-fused, narrow coverage), we have instead a precise **map of the
resident Lisp's stdlib and its edges** — still the honest artifact the project is owed.

## Sessions
s281 (this synthesis — map+swap / reduction-as-programming / the resident Lisp; discussion
Michael-directed, distilled for a later session. Successors: `three-hop-capacity-prereg.md`,
`multihop-composition-prereg.md` §Cross-scale depth-budget.)
