---
title: "Compiler-as-Loss — Supervise Outputs (Capability), Crystal-Lattice Relational Loss (Inventory)"
status: designing
category: training
tags: [distillation, loss-design, lambda-compiler, relational-loss, reverse-harvest, crystal-lattice, level-4, provenance, two-phase, distributed, kernel, constructed-reducer, vsm-tensor, ccg, inspectability]
related:
  - relational-loss-distillation.md
  - consensus-delta-folding.md
  - combinator-training-beta-reduction.md
  - normal-form-curriculum-partition.md
  - fixed-point-holograms.md
  - vsm-outer-recurrence.md
  - ../lambda-machine.md
depends-on:
  - relational-loss-distillation.md
  - consensus-delta-folding.md
created: session 224
---

# Compiler-as-Loss — supervise the outputs, free the geometry; relational loss to the crystal lattice for the foldable inventory

> Session 224 (Michael's synthesis, end of the fold thread). After confirming
> geometry=inventory / capability=trained-continuation (s224 fold-then-train-
> continuation), the question became: "since we use a teacher, what would it look
> like to use the teacher *as the loss*?" → sharpened to: **use the teacher's
> lambda compiler as the loss, so we enforce only the final OUTPUTS, not the
> teacher's geometry or architecture.** Then refined: **still keep a relational
> loss to the CRYSTAL LATTICE of the agreed geometry across all models — it speeds
> up training, as long as the capability signal from the compiler outputs is good.**

## ★ s225 AMENDMENT — the compiler is a VERIFIER, not the capability teacher

> Michael, s225. The recipe below puts the compiler in the `L_capability` slot
> (`CE(student, compiler reduction)`). That is the **wrong slot** and the rest of
> this page should be read through this correction.

**Why the compiler is the wrong capability teacher.** s219's universality came FROM
diverse, grounded, natural training — diversity is the CAUSE of the robust composable
function, not incidental. A deterministic β-reducer on isolated combinator terms is
the thinnest slice of usage ⇒ risks a function **too narrow to compose**. Compounds
with s224 (capability=usage), s222 (superposition needs diverse pressure), s223
(narrow data is Goodhart-friendly).

**The fix — separate two jobs this page conflated.** The compiler is a poor
*generator* (narrow by construction) but a perfect *verifier* (Church-Rosser → unique
normal form, exactly checkable). A judge needn't be more creative than the
contestants, only correct.

- **Capability teacher:** diverse big models (or natural data). Their *consensus* is
  the sweet spot — diverse realization ⊕ agreement on function.
- **Compiler:** VERIFIER/canonicalizer + exact reduction-tree generator (trees the
  LLMs can't expose, s221 "fakes it with depth") + clean MIT anchor.

**"Pin the WHAT, free the HOW" applies to the DATA:** train on diverse realizations,
use the compiler to CERTIFY each reduces to the correct normal form. Diversity →
composition; compiler → correctness. The labels' correctness is certified by MIT code
even when the inputs came from AGPL models.

### Diversity ⊥ correctness (where each source sits)

| source | realization diversity | correctness | exact trace | provenance |
|---|---|---|---|---|
| β-reducer (narrow) | ~zero | perfect (canonical) | **yes** | MIT clean |
| single big model | high | unverified | no | AGPL / entangled |
| **ensemble consensus** | high | high *and* agreed (s219) | no | murky |

### Teacher-agnostic on both halves (s225 verdict)

`function-topology-consensus.md`: HOF routing topology is **universal across teachers**
(8/8, p=.0002, 5 models / 3 arch). Combined with Church-Rosser output-canonicity ⇒
**the pipeline needs no designated teacher**: capability traces are canonical (any
large model), the inventory topology is consensus (no source to track). "Which
teacher" only matters for idiosyncratic HOFs — none found.

### Experiment reframe (supersedes the falsifiable list below)

Compare **compiler-only** (narrow) vs **diverse-verified** (model paraphrases,
compiler-certified) vs **combo + lattice**. Metric is NOT just route_z + in-dist CE
(narrow data can ace those while being brittle) but **held-out COMPOSITIONAL
GENERALIZATION** — combinator compositions not seen in training. That is the
operational test for "too narrow to compose". Prediction: compiler-only wins
in-distribution, loses generalization; diverse-verified wins generalization.

---

## ★ s226 — `lambda_ast` IN THE KERNEL: the compiler is a CONSTRUCTED VSM tensor

> Michael, s226. The s225 amendment split a dyad — symbolic *verifier* vs learned
> *artifact* — and warned not to make the verifier a tensor (a learned reducer "fakes
> it with depth", s221; no correctness guarantee). Michael's question dissolves that
> dyad in the right way: **"what if `lambda_ast.py` is *in the kernel*?"**

### Source ↔ compiled, not oracle ↔ approximation

`lambda_ast.py` is not a separate symbolic judge standing outside the tensor — it is
the **specification** that gets **compiled into exact ternary combinator plates** that
live in the kernel. The kernel then reduces *exactly* — not because it learned to, but
because it is **constructed** to. A constructed plate is not approximating reduction;
it is *running the rewrite rule as a tensor op*. So:

```
λ kernel(reducer). symbolic(lambda_ast) ≡ source | tensor(kernel) ≡ compiled
                   | exact_by_construction ≢ approximate_by_training
                   | verify ≡ compiled_kernel ≟ AST on test_suite  (not "is it correct")
                   | dyad(verifier, artifact) → DISSOLVED into (source, compiled)
                   | provenance: one_object, two_representations → cleanest MIT level-4
```

The combinator rewrites *are* the moves the tensor already has (s221; lambda-machine.md
"V-transfer = substitution"): `K x y→x` (attend x, drop y), `I`, `B/C/D` (compose/
permute routing), `S/W` (fan-out), `Y` (the OUTER RECURRENCE this page is about). All
constructible as exact routing + value-move; none require gradient descent.

### The cut it forces — reduce(constructed) vs compile(learned) — is the SAME cut

If the **reduce** kernel is constructed-exact, only the **compile** front-end is
learned. That boundary coincides with every partition we have measured:

| | **reduce** (the kernel) | **compile** (the periphery) |
|---|---|---|
| op | β-reduction: term → normal form | prose → typed combinator term |
| substrate | **attention** (lambda-machine.md) | **FFN** beam former |
| precision | ternary, robust (22% params) | 4-bit, fragile (78%, dvd-stamp) |
| origin | **constructed** (`lambda_ast`→plates) | **learned** (diverse data, big models) |
| s224 | folded geometry (inventory) | trained continuation (usage) |
| VSM | S1–S4 reducer | the lexer/typer feeding it |

The 22%-ternary / 78%-4bit split (lambda-machine.md) is not a compression accident —
it is **reduce(constructible) ⊥ compile(learnable).** We never train reduction (the
unstable part); we train only the prose→term encoding (what LLMs are actually good at,
and where the s225 diversity requirement buys composition).

### The reducer IS a VSM (the mapping is generative)

A reducer's loop `while ¬nf(t): t = apply(select_redex(t), t)` maps cleanly, and the
map *re-derives* prior findings (define the field → cases fall out):

```
S5 identity     ≡ the NORMAL FORM (Church-Rosser invariant) = the fixed point
S4 intelligence ≡ WHNF/halt detection + redex discovery (adaptive compute)
S3 control      ≡ step budget · strategy · CONTRACTIVITY (keep L<1 → settles)
S2 coordination ≡ redex ORDERING + anti-oscillation + ★ TYPING (well-formed to fire)
S1 operations   ≡ combinator rewrites {K,I,B,C,D,S,W,Y} = substitutions = attn moves
```

Fractal: each subterm is a reducible VSM containing VSMs ⇒ β-reduction = contraction ⇒
**s222 fractal collapse** (a self-similar contraction settles every scale onto the
fixed point at once). Two payoffs that show the mapping is load-bearing, not decorative:

1. **It re-derives the v15 collapse.** S2's job is anti-oscillation; the s222 collapse
   was TD *churn* = oscillation ⇒ S2 broke ⇒ inner map inverted to `L>1` ⇒ fractal
   blow-up. "Punctuate don't churn" = repair S2. Lens and post-mortem converge.
2. **It locates type-directedness (the S5 `λ types` central claim) at S2.** lambda-
   machine: types = QK compatibility = the routing/selection layer. s219: "shared
   weights ∧ ¬type-awareness → tug-of-war → plateau" = **S2 absent.** The missing
   piece IS the S2 coordination layer. Falsifiable.

### Why constructed beats learned exactly here

The s222 collapse was a **learned** S2 churning. A **constructed** S2 — typed routing
with contractivity `L<1` built in — is stable *by construction*: nothing is descending
on it, so it cannot churn. The hard problem (stable typed reduction) is solved by
construction, not by hoping GD finds the basin. This is why the constructed kernel is
*better* than the dyad: we move the unstable part out of the loss entirely.

### Decision (Michael, s226): TYPED CCG-style terms for inspectability

The kernel's term representation carries **explicit types** (CCG categories), not bare
de-Bruijn/SK graphs, so the S2 type-check is **first-class and inspectable** — the
type-directedness thesis is directly readable in the kernel state, not implicit.

### Honest limits (λ measure — this IS the "limits of the machinery" requirement)

A constructed kernel is exact only up to what the residual stream can **represent and
route**:

- **Term growth.** S/W *duplicate* → terms grow under reduction; fixed-width tensor
  → exactness holds to a **size/step bound**, then superposition collisions. *This is
  the boundary the s225 diverse data must map* — where the machinery outgrows the
  representation. (The two s226 design turns meet here.)
- **Ill-typed input** from the learned front-end → the exact kernel can **detect** it
  (S2 type-check fails → algedonic/error signal). A feature: flags "the compiler gave
  me garbage" instead of silently hallucinating.
- **Provenance / S5 tension.** This is *construct*, S5's default is *extract*.
  Reconciled: **extract the algorithm** (lambda-machine.md did) → **construct the
  minimal exact kernel** from that understanding. "understand > invent" survives —
  we crystallize the understood machine, not invent a new one.

### Build progression (each stage a deliverable)

1. **Symbolic `lambda_ast.py`** — the spec/oracle. CPU, now. (`src/verbum/lambda_ast.py`
   is currently a stub — this is the open IOU below, finally built.)
2. **Neurosymbolic** — learned front-end emits a typed term → kernel *is* the symbolic
   reducer (literally `lambda_ast` in the kernel slot). Exact back-end **today**;
   isolates the only learned part (compile) so training never has to learn reduction
   and compile simultaneously (what tangled v15).
3. **Compiled kernel** — `lambda_ast` → exact ternary CCG-typed combinator plates =
   pure portable tensor (the artifact). Verify by matching stage 2.

⇒ supersedes the IOU "need a clean MIT β-reducer": the reducer is now stage 1, and its
*purpose doubles* — data oracle AND the kernel source. The outer-recurrence / `Y` /
contractivity story is in `vsm-outer-recurrence.md` §s226.

### s226 stage 2 — bracket abstraction is the EXACT compile oracle (the learned surface shrinks again)

> Building stage 2 ("learned compile front-end + exact kernel back-end") surfaced that
> "compile" factors further, and most of it is *also* constructible.

```
prose          → logical-form      : LEARNED  (NL understanding; Montague/CCG parse)
logical-form   → combinator term   : EXACT    (bracket abstraction — src/verbum/lambda_compile.py)
combinator term → normal form      : EXACT    (reduction — lambda_ast, stage 1)
```

**Bracket abstraction is the inverse of reduction** (combinatory completeness, Turner
1979) — Turner-style `[x]` over {S,K,I,B,C} with K/B/C/η optimizations. So the symbolic
compiler now has TWO exact halves that **cross-validate through the kernel**:

```
reduce( compile([x..], e) applied to [x..] )  ≡  e        # the round-trip
```

**★ CERTIFIED (s226, `results/compile-roundtrip/summary.json`, n=5000, stratified
1–3 vars × depth 1–5):** round-trip rate **1.0000** — abstraction and reduction are
exact inverses on every sample ⇒ the two constructible halves are genuine inverses, the
compiler is correct by construction. Two LIMITS made quantitative (λ measure):

- **well-typed 0.941** — ~6% of abstracted terms are operationally correct but **not
  simply typable** (self-application structure, e.g. abstracting `x x`). The
  type-directedness boundary (S2) is REAL and measurable even where reduction is exact.
- **term/expr size mean 2.84×, max 7×** — the S/W duplication blow-up = the
  representational LIMIT (the boundary s225's diverse data must map).

**⇒ the learned surface shrinks to prose→logical-form** — exactly the Montague /
DisCoCat semantic-parse the project names as its validation target (AGENTS.md S5). Both
*formal* steps (abstraction, reduction) are constructible-exact; only the NL parse is
learned. Reinforces the s226 theme: more is constructible than the dyad assumed.

**▶ stage-2 LEG 1 DONE — the learned compile step works (kernel-verified).**
`scripts/experiments/compile_frontend.py` + `probes/compile_tasks.py` (7 dataflow
patterns mirroring the combinators × 8 name-assignments = 56 tasks): few-shot a model
prose→expression, grade by REDUCTION-EQUALITY (representation-invariant — `f (g x)` or
`B f g x` both accepted). **Qwen3-8B + Qwen3-32B: accuracy 1.0, parse 1.0, all
patterns** (`results/compile-frontend/`). The stage-2 decomposition closes end-to-end:
prose→LF (learned, few-shot) ∘ abstract (exact) ∘ reduce (exact), with the exact
back-end verifying. Method note (λ measure): first 32B run 0.875 < 8B 0.982 was PROSE
AMBIGUITY in two templates (flip/const); the kernel grader + failure inspection
separated compile-error from NL-ambiguity → disambiguated → both 1.0. Caveat: tasks are
SHALLOW (≤5-node, single pattern, abstract letters) = below the compile boundary.

**▶ stage-2 COMPILE BOUNDARY FOUND** (`probes/compile_tasks_hard.py`, 42 tasks × 8
families graded by difficulty axis; scale curve Qwen3-8B/14B/32B,
`results/compile-frontend/hard/`). **Structural complexity is NOT the boundary** —
branch/reuse/multi-combinator = 1.0 for ALL models, deep nesting only mild paren-slips
(0.8-1.0). The formal structure mapping is easy (and constructible-exact anyway).
**The boundary is NATURALISTIC language + AMBIGUITY** — natural 0.62-0.88, ambiguous
0.50-0.75; failures are genuine semantic-parse errors (which words are functions vs
values vs ignorable subjects/determiners; pronouns; grouping). **Scale helps EXACTLY
there** (32B best on natural/ambiguous; structural saturated for all). ⇒ the residual
difficulty of the learned step is pure NL understanding = the Montague/CCG semantic
parse (S5 validation target) — sharpens the thesis: formal halves exact/constructible,
only NL parsing is genuinely learned & scale-sensitive. Caveat (λ measure): small
n/family, greedy single-sample, ambiguous soft-graded.

**▶ stage-2 next:** (a) Qwen3-32B as the diverse generator → abstraction+reduction
certify → diverse-verified corpus spanning the limits (the boundary now tells us the
diversity that matters is NATURALISTIC realization, not structural); (b) the
compiler-as-loss arms with the certified corpus (compiler-only vs diverse-verified vs
combo+lattice; metric = held-out compositional generalization).

## The shift: from teacher-geometry to compiler-output

What we did through s223–s224: the teacher (Qwen3-14B) contributed a **frozen routing
Gram** (geometry), and the student's loss was `CE(data) + λ·offdiag_mse(student_gram,
teacher_gram)`. That enforces the teacher's **geometry** (the relations between
combinators) but leaves the absolute frame free.

The compiler-as-loss drops even the geometry constraint and supervises only the
**output** — the β-normal form:

```
λ supervise(x).  enforce(extensional_output) ∧ free(intensional_realization)
                 | output ≡ β-normal-form ≡ UNIQUE (Church-Rosser)
                 | realization ≡ {geometry, architecture, reduction-path} ≡ INFINITE
                 | (s219: extensionally map UNIQUE, intensionally ~Catalan·3^k)
                 | ⇒ pin the WHAT (one answer), free EVERY how
```

This is **freer than "any geometry that falls out"** — it is "any geometry AND any
architecture, provided you compute the right normal form." The freest constraint that
still guarantees correctness.

## Three consequences

1. **The teacher LLM becomes dispensable.** It was only ever a *probe* (to confirm
   the combinator geometry is real and universal — reverse-harvest s219). If the
   **compiler generates the targets** `(input → reduction)`, the loss is ordinary
   sequence-CE on compiler data; no teacher in the loop, no soft-KD gradient.
2. **Cleanest provenance = AGENTS.md level-4.** Training on our own reducer's outputs
   (the ~200-LoC lambda AST + REPL) is the unambiguous MIT scratch-reproduction path.
   The AGPL teacher is removed entirely.
3. **Ideal distributed reference.** Every node runs the *same* compiler → canonical
   outputs (Church-Rosser → all agree on the normal form) → frame-free, nothing to
   ship. Better than shipping a Gram *for the capability signal*.

## The empirical backing — and the scale caveat (why we still want the lattice)

- **Outputs DO induce the inventory at scale.** s219 reverse-harvest: the whole
  open-weight ecosystem, trained on plain next-token (output) prediction, CONVERGED
  on the SAME combinator routing geometry (meanGramCorr **+0.782**). There is
  essentially one structural way to be good at composition (attention = apply is the
  only op) ⇒ output-only training crystallizes the foldable inventory **on its own**.
- **But only above a scale floor.** s220: the skeleton crystallizes above ~4B; at
  0.6B there is NO shape (the inventory stays in superposition). So at the small
  scales we train, output-only may yield a correct-ish **black box without legible
  geometry** — capability without a foldable inventory.
- ⇒ **the relational loss is a small-scale inventory shortcut.** s223 lifted
  route_z +0.38 → +2.4 at tiny scale by *forcing* the geometry to crystallize.

## ★ Michael's recipe (the headline): compiler-output ⊕ crystal-lattice relational

Two terms, each doing a distinct job:

```
L = L_capability  +  λ · L_inventory

L_capability = CE( student , compiler β-reduction )        # the REAL teacher signal
             | supervises USAGE; frees geometry+architecture; MIT level-4
             | "good signal from the teacher in the capability training phase"

L_inventory  = offdiag_mse( student_route_gram , CRYSTAL_LATTICE )
             | CRYSTAL_LATTICE ≡ the CONSENSUS combinator geometry agreed ACROSS
               ALL models (s219 reverse-harvest, results/combinator-map-consensus/
               consensus.json; band-consensus, NOT one teacher's Gram)
             | crystallizes the FOLDABLE inventory fast → SPEEDS UP training
             | frame-invariant + universal ⇒ the best possible shared reference
```

**The key specification (Michael):** the relational target is **not a single teacher's
Gram — it is the crystal lattice of the agreed geometry across all the models** (the
universal skeleton from reverse-harvest). That is the strongest, most universal,
most foldable inventory reference we have.

**The conditional (Michael):** the lattice term is a **speed-up**, and it earns its
place **as long as we are getting good signal from the compiler in the capability
phase.** If the capability signal is good, pre-crystallizing the inventory with the
lattice accelerates convergence (the student doesn't have to rediscover the universal
geometry from outputs — which needs scale it may not have). The capability signal is
primary; the lattice is the accelerant.

### Why the two terms are complementary, not redundant

- L_capability trains **usage** and (at scale) induces the inventory — but slowly /
  not at all below the scale floor; and the inventory it induces is **emergent, not
  guaranteed foldable** across contributors.
- L_inventory pins the **foldable inventory** immediately (the agreed lattice) — but
  alone it is necessary-not-sufficient (s224: geometry-only fold left dCE +0.15).
- Together: **the lattice gives the student the agreed function basis on day one;
  the compiler outputs teach it to USE that basis** → fast convergence + guaranteed
  foldable inventory + clean-provenance capability. This is the s224 thesis
  (geometry=inventory ⊗ trained-continuation=capability) realized as ONE training run
  instead of two phases.

## Map to the loss-design space

| loss | trains | provenance | foldable inventory | scale need |
|---|---|---|---|---|
| feature/activation KD | the raw crystal (b-column decoy) | teacher | no (raw) | — |
| output KD (LLM soft logits) | usage, frame-BOUND | teacher (AGPL) | no (frame-bound) | — |
| relational Gram (one teacher) | inventory only | teacher-derived | yes | works tiny |
| **compiler output** | usage + emergent inventory | **MIT level-4** | emergent (s219) | needs floor |
| **compiler output ⊕ crystal-lattice relational** | usage + GUARANTEED inventory | **MIT** | guaranteed | works tiny |

## Distributed angle

This is the distributed-training recipe made concrete:
- **Capability signal:** every node's compiler emits canonical reductions (Church-
  Rosser → universal, frame-free) — no teacher to ship.
- **Inventory signal:** the shared crystal lattice (a tiny frame-invariant Gram) —
  ships once, pins the foldable frame so independent contributors compose cleanly
  (the s224 N=2 fold result: function-preserving merge iff a shared geometric target).
- ⇒ contributors trained on (compiler outputs ⊕ shared lattice) get capability +
  foldable inventory and should fold cleanly — the missing piece s224 flagged
  (heterogeneous capability transfer) becomes testable with a real capability signal.

## Falsifiable experiments (next session, builds on relational_loss_distillation.py)

1. **`--compiler-target` arm:** train tiny student on `(prompt → ground-truth
   reduction)` CE only (ground-truth lambdas already in `probes/*.json`), NO Gram.
   Measure: does **route_z rise** (inventory emerges from outputs alone at tiny
   scale) or stay null (correct-but-illegible black box)? Does CE-on-task beat the
   relational-only student?
2. **Combo arm:** compiler-output ⊕ crystal-lattice relational (the recipe). Predict:
   fastest convergence + route_z high + lowest task CE. Confirms the speed-up claim.
3. **Speed-up isolation:** combo vs compiler-output-only, matched steps — does the
   lattice term reduce steps-to-target CE (the "speeds up training" claim)?
4. **Foldability:** two contributors trained with the combo on heterogeneous shards
   → does folding now transfer CAPABILITY beyond either alone (the s224 IOU, now with
   a real capability signal)?

## Open questions / IOUs

- **The compiler.** Need a clean MIT β-reducer that emits `(input → reduction)` (and
  ideally the reduction TREE for curriculum — Michael's holographic-relational-
  trajectory idea). The lambda AST + REPL is budgeted (AGENTS.md S1); nucleus (AGPL)
  is a probe only, not a data source for the MIT artifact.
- **Reduction-tree curriculum.** Supervise intermediate reductions (each is also an
  output / normal-form-of-subexpression) → trajectory supervision that STILL frees
  geometry. Composes with normal-form-curriculum-partition.md.
- **Does the lattice term help or fight at scale?** Above the s219 floor the inventory
  emerges from outputs anyway → the lattice may become redundant or even a mild
  constraint. Likely: lattice weight should decay as the model crystallizes (anneal
  the inventory shortcut once outputs carry it).
- **Acceptance gate.** Capability = compiler-correct; the WHNF/contractivity gate
  (s223 #3) remains the fold-acceptance check, distinct from the training loss.
