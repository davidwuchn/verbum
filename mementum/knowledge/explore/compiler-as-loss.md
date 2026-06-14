---
title: "Compiler-as-Loss — Supervise Outputs (Capability), Crystal-Lattice Relational Loss (Inventory)"
status: designing
category: training
tags: [distillation, loss-design, lambda-compiler, relational-loss, reverse-harvest, crystal-lattice, level-4, provenance, two-phase, distributed]
related:
  - relational-loss-distillation.md
  - consensus-delta-folding.md
  - combinator-training-beta-reduction.md
  - normal-form-curriculum-partition.md
  - fixed-point-holograms.md
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
