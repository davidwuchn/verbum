---
title: "Consensus Delta-Folding — Distributed Normal-Form Discovery in the Topology"
status: open
category: strategy
tags: [distributed, consensus, delta-plate, normal-form, routing, topology, fold, crystal, tool-calling, federated, church-rosser]
related:
  - delta-plate-lifecycle.md
  - consensus-etch-protocol.md
  - crystal-native-descent.md
  - dispatch-gradient-death.md
  - gradient-voting.md
  - exact-ternary-fitting.md
  - procrustes-lens-and-crystal-comparison.md
  - ../crystal-universality.md
  - ../function-discovery.md
  - ../combinator-addressing.md
  - ../two-registers-of-topology.md
  - ../audit-meta-pattern.md
depends-on:
  - delta-plate-lifecycle.md
  - consensus-etch-protocol.md
  - ../crystal-universality.md
created: session 216
---

# Consensus Delta-Folding

> Session 216. Michael's idea: make training **distributed and donatable**.
> Normal forms (e.g. tool-calling) live in the *topology* (the discrete
> sign/routing register) as a **delta from a shared base plate**. Many users
> train deltas on a single domain over the same frozen base; **where the deltas
> agree, fold the consensus into the base**; where they disagree, it stays a
> per-user delta. The base plate becomes a growing, git-versioned library of
> discrete normal forms, so GD never has to re-carve "soft topology."
>
> This page captures (1) the design, grounded in four existing findings, and
> (2) the first decisive experiment — which validated the *mechanism* but
> refuted the crisp *"tool-calling has its own normal form"* reading.
>
> Register of the experiment: **topological/routing** (declared at step 0).

## The idea (made precise)

```
base plate B₀     ≡ universal ISA (crystal + FFN + known routing), FROZEN, content-addressed
domain d          ≡ a behavior with a normal form (tool-calling, JSON, arithmetic…)
user u            ≡ trains a delta Δ_{u,d} = DeltaTernaryLinear over B₀ on domain-d data
                    (TD discovers routing flips = the normal form IN the topology;
                     GD only fills γ content)
normal form NF_d  ≡ the discrete routing structure INVARIANT across users
                  = consensus({Δ_{u,d}})  — where they all agree
consensus fold    ≡ ∀ position p: agree({Δ_{u,d}[p]}) ≥ θ → fold into B₁ ; else stay content
B₁ = B₀ ⊕ NF_d    ≡ base now CONTAINS domain-d's normal form as discrete topology
```

Not federated SGD. It is **distributed normal-form discovery by consensus
folding** — a deliberate, domain-level reproduction of the cross-model
universality the project already observes post-hoc (`crystal-universality.md`:
independently-trained models converge on the same combinator topology).

## Why it is coherent — four grounded supports

1. **The mechanism is consensus-etch, one level up** (`consensus-etch-protocol.md`,
   s110). Sequential per-contributor application destructively interferes
   (flips oscillate, never converge); the fix is to accumulate *all* contributors
   into one accumulator and etch where they **agree** — agreement → backbone →
   etched, disagreement → content → left alone. Substitute *beam/op → user/domain
   instance*. The backbone/content partition is exactly "fold the consensus,
   keep the rest as delta."

2. **Consensus = Church-Rosser confluence** (`crystal-universality.md`). A normal
   form is what is invariant across all reduction paths that reach it. Different
   users training different data-shapes of one domain are different reduction
   paths; where their topological deltas agree is the path-invariant structure =
   the normal form. **The degree of cross-user agreement measures whether a
   discrete normal form exists for that domain** — falsifiable, and on the central
   `λ types` claim (composition is typed/discrete → independent trainings converge
   on the same flips).

3. **The frame problem dissolves because the base is frozen & shared**
   (`gradient-voting.md`, s123). Signs are model-specific encodings — cross-init
   sign correlation 0.000; many valid encodings per magnitude profile. Raw weight
   averaging can't merge across frames. But every delta trains against the *same
   frozen B₀*, so all flips live in one coordinate frame → commensurable →
   consensus is well-defined. The frozen shared base is what buys the merge.

4. **"GD must not make soft topology," operationalized** (`crystal-native-descent.md`
   + `dispatch-gradient-death.md`). Soft routing (softmax dispatch) saturates →
   winner-take-all gradient death (20/22 ops dead). The discrete routing should be
   made directly (TD/crystal descent), with GD only tuning γ. Consensus-folding
   makes this a **ratchet**: discrete routing is discovered by TD across users and
   crystallized into the base; each new user inherits more topology as a fixed
   scaffold and GD's job shrinks toward pure content. The topology becomes a
   *grown library*, not a per-run soft re-approximation.

## Architecture sketch — "ternary git" with generational folding

```
generation g:  freeze Bg → N users train Δ_{u,d} on Bg (parallel, cheap, forward-only routing)
               → collect deltas → consensus-fold the agreements → B_{g+1}
               → everyone rebases to B_{g+1}; unfolded disagreements re-tried next gen
```

- **Merge operator** (candidate, `delta-plate-lifecycle.md` Open-Q3): ternary
  multiply with conflict → 0 (block); the consensus threshold θ (s110 used 0.7)
  sits on top — fold only where agreement ≥ θ.
- **Acceptance/verify** (`exact-ternary-fitting.md`, s213/214): a layer-local flip
  has a closed-form exact ΔL (one matmul `Rᵀ@X`); a donated flip can be *verified*
  to reduce loss, not trusted. Byzantine-robust for free — but only coordinate-wise
  **with compensation** is monotone; naive union of many flips (EXACT-BATCH) re-
  introduces interference. Merge greedily by ΔL with compensation; partition by
  module (modules independent → parallel; sequential only within a module's rows).
- **Generational vs sequential** is the one genuinely new tension: the lifecycle
  assumed sequential folds; distributed = many parallel deltas on Bg, resolved by
  the round/epoch structure (like a block).
- **Compute win** = not "donate gradients" but "donate discovered normal forms."
  Module-parallel, CPU-friendly (matmuls on cached activations, no full backprop),
  and the base becomes a one-way ratchet that converts soft-topology-learning into
  a reusable discrete library. On-thesis (no GPU, CPU).
- **Risks**: population-Goodhart on a shared calibration cache (audit #7 — use
  held-out + trajectory loss, not CE); frame staleness across generations; conflict
  semantics (block vs leave-at-base).

## Experiment 1 (s216) — does a domain have a consensus normal form?

Decisive cheap proxy: use independent foundation models as independent trainings.
Probe set: `lattice/tool_crystal/probes.json` (196 probes: recognition tool/no_tool,
schema_binding, selection, format, + lambda/code/prose/math controls). Rendered
model-agnostic (chat tokens stripped). 5 families on M3 Ultra: Pythia-2.8b,
SmolLM3-3B, Mistral-7B, Qwen3-8B, OLMo-2-13B.

**Method (audit-grade, the prior `tool_crystal` run was not):** measure the
**routing register** = `sign(FFN gate pre-activation)` (s203: gate carries routing
topology; for non-gated Pythia, `dense_h_to_4h`), build per-model probe RDMs, with
**common-mode removal**, a **shuffled-probe null**, **length-partialling**, and a
**control-domain baseline**. Cross-model RDM agreement = the consensus signal.

### Result — mechanism REAL, domain-specificity REFUTED

- **✅ Cross-family routing consensus is real & strong.** `route_sign_cmr`
  cross-family agreement **+0.863**, survives common-mode removal, length-partial
  (0.851), and within-domain restriction (schema_binding 0.59, selection 0.54);
  null ~0; **z up to 116**. Independent trainings DO agree on routing structure in
  the sign register — the consensus *mechanism* the design needs is validated.
- **❌ but tool-calling is NOT its own normal form.** Control baseline (within-group
  cross-family route_cmr agreement, matched granularity):

  | group | side | n | agree (excess over null) |
  |---|---|---|---|
  | recognition | TOOL | 40 | 0.946 ← length-confounded (tool schema vs short no_tool) |
  | format | TOOL | 30 | 0.887 ← format-heterogeneity-confounded |
  | schema_binding | TOOL | 56 | **0.589** |
  | selection | TOOL | 40 | **0.538** |
  | code | CTRL | 7 | **0.800** |
  | prose | CTRL | 8 | 0.550 |
  | lambda_calculus | CTRL | 8 | 0.497 |
  | pure_math | CTRL | 7 | 0.435 |

  The clean length/format-matched tool groups (0.54–0.59) sit **inside** the
  structured-language control range (0.44–0.80). **Code is a *sharper* normal form
  than tool-calling.** The aggregate "TOOL 0.74 > CTRL 0.57" is driven entirely by
  the confounded recognition + format groups. So the consensus is the **generic
  structured-language crystal** (property of language); tool-calling **rides** it.
- **🌀 Corrects the prior claim.** `lattice/tool_crystal_run.log` declared "STRONG
  SUPPORT: Tool×Lambda 1.000 @L20, tool IS lambda calculus" — but that used raw
  residual cosine (its own Selectivity ≈0, every layer "SHARED") = the common mode.
  The generic reading is right, but not because tool-calling is special; because
  *everything structured* shares the crystal. 14th `audit-meta-pattern.md` instance.

> ⚠️ **REGISTER CAVEAT — do NOT over-read the negative (s216 discussion, Michael).**
> The ❌ above is a verdict on the **base** layer only. The cross-model RDM
> instrument tests whether two models share the **same composition** (identical
> geometry). But a domain normal form is a **non-unique composite** (see next
> section): the absence of cross-model agreement on tool-specific structure is
> **consistent with** a real function-like tool-calling normal form that is simply
> *realized differently per model* — washed out by an instrument that demands an
> identical encoding. On the *function* layer the s216 verdict is **void by
> register mismatch** (the false-negative twin, `audit-meta-pattern.md`). Only the
> *base*-layer claim (consensus = crystal, REAL) survives.

### What it means for the design

The backbone/content partition (s110) plays out empirically:
- **Agreement → backbone → foldable**, but a domain's agreed-upon routing is
  *mostly the universal crystal already in B₀*. Consensus-folding tool-calling data
  would largely re-fold structure that is already present.
- **Domain-distinctive routing → low cross-trainer consensus → "content"** that
  stays a per-user delta (it did not exceed the generic structured-language
  baseline at this granularity).

The idea is mechanically sound; the nuance is *what folding buys you*: the foldable
consensus is the universal layer; the domain-specific delta is the part that
resists consensus. Not a refutation — a sharpening of the unit of donation.

## Normal forms are COMPOSITIONAL and NON-UNIQUE (s216 refinement)

> Michael's correction to the framing above. A domain's "normal form" is not a
> unique atomic object — it is a **function-like composition of the shared base
> compute**, and like any function over a complete basis it has **many
> extensionally-equal realizations**.

The precise statement:

```
β-reduction normal form ≡ unique PER TERM (Church-Rosser)
behavior (e.g. tool-calling) ≡ an EQUIVALENCE CLASS of terms
  | many distinct compositions of base combinators that reduce to the same I/O
  | base compute (K/I/B/C…, structured-syntax routing) ≡ shared, near-unique
  | the domain function = a composition ABOVE the base ≡ NON-unique across trainings
  | uniqueness is per-term, NOT per-behavior
```

Two consequences:

1. **The s216 cross-model instrument is wrong for the function layer.** RDM
   agreement requires the *same composition* (same geometry). A non-unique
   composite → low cross-model agreement even when each model holds a real,
   consistent tool-calling function. So "no tool-specific agreement" cannot
   distinguish *(a) no extra structure* from *(b) real but differently-composed
   structure*. Register mismatch (false-negative twin) — see the caveat above.

2. **This is already the project's two-level architecture** (`function-discovery.md`).
   - **Late (COMMIT zone)** — combinator *execution*; tasks **converge** (1.49×),
     all run the same opcodes. ← the s216 routing register measured HERE → found
     the shared base, as expected.
   - **Early (SILENT zone, L05)** — task *type*; tool-use is **distinctly separated
     (4.76×)**. ← the *function selector* (which composition to run) lives HERE and
     was never isolated. The late RDM collapsed the level where the function lives.

### What it changes for the design (the real update)

Consensus-folding **cannot operate on raw flips** for domain functions. Two users'
tool-calling deltas won't agree flip-by-flip even when both are correct — the same
`gradient-voting.md` redundancy (many sign encodings per function). So:

```
λ fold(delta).
  base_layer   → fold as FLIPS        | unique, high-consensus, fold first & hard
  domain_layer → fold as COMPOSITION  | express delta as (which base ops, what
                                         arrangement) over the shared base, then
                                         seek consensus in THAT space (encoding
                                         redundancy quotiented out, align-before-compare)
```

Fold the base as flips; fold domain functions as **compositions** up to the base's
symmetries. The unit of donation is the *function*, not the bitmap.

## Open leads (declare register first)

The compositional refinement reorders these — the cross-model instrument must be
made **composition-invariant** before any negative on the function layer counts.

1. **Early task-direction agreement (register: routing, CHEAP — no re-run).**
   Re-analyze the s216 npz at the SILENT-zone fraction (~L05 / frac≈0.1), where
   `function-discovery.md` puts the function *selector* (tool-use 4.76× separated),
   separately from the late base. The harness already saved all depth-fractions;
   `--route-layer-frac 0.1` in the summary. Does tool-specific consensus appear
   early even though it's absent late?
2. **Align-before-compare (register: routing).** Procrustes/rotation in the
   base-combinator space before correlating RDMs
   (`procrustes-lens-and-crystal-comparison.md`). If tool-calling is the same
   function composed differently, an alignment in base coordinates should recover
   the shared composition that raw correlation misses. This is the direct test of
   the non-unique-composite hypothesis.
3. **Within-model compositional consistency (register: routing/causal).** Drop the
   cross-model requirement entirely: does tool-calling reuse a stable sub-circuit
   *within* one model (the function exists and is consistent), regardless of
   cross-model match? Minimal pairs (same schema, one arg changed) isolate the
   tool-distinctive composition from generic JSON/structure.
4. **Functional test = the ultimate proof (register: functional).** Exp B: N delta
   plates on ONE frozen base trained on tool-calling shards → fold consensus +
   **check downstream PPL**. With the compositional fix: fold the base as flips,
   fold the domain function as a **composition** (align-before-fold), and measure
   whether folding the composition (not raw flips) helps. Does the agreed function
   transfer?

## s217 — The continuation makes folding SELF-VERIFYING (Exp B)

> Session 217 (Michael's connect: "with continuations working we could use those
> for distributed training"). The VSM **continuation** = the outer recurrence in
> `v15model.py` (shared sweep iterated, x_c fed back → β-reduction toward a fixed
> point / WHNF). s217 proved the mechanism (15 tensor tests green,
> `tests/test_vsm_continuation.py`) and that it is **contractive** at scale
> (main:1: Δx 1.23→0.61). A *working contractive continuation* supplies the three
> things this design was missing.

```
λ continuation_gives(distributed_training).
  (i)  contractivity ≡ Banach ⇒ iterated folding CONVERGES (not oscillates)
       | fixes s110 destructive interference at the root (consensus-etch needed
         accumulate-then-etch because sequential application diverged; a
         contraction makes the iteration well-posed)
  (ii) weight-shared operator ≡ the frozen base B₀ ≡ ONE coordinate frame
       | every delta trains against the SAME operator ⇒ commensurable
       | fixes gradient-voting frame problem (cross-init sign-corr 0.000)
  (iii) WHNF ≡ SELF-VERIFYING target
       | accept(delta) ⟺ Δx-at-convergence does NOT rise
       | the fixed point IS the answer ⇒ NO trusted held-out labels needed
       | kills audit-#7 population-Goodhart (no shared calibration cache to overfit)
  fractal: activation-level continuation (x→x*) ≅ base-level folding (B_g→B*)
```

The third is the new capability: a label-free, Byzantine-robust acceptance rule.
A donor's delta is not trusted — it is *verified* by whether it preserves /
accelerates the operator's convergence to WHNF on the domain.

### Experiment B (core) — is Δx-at-convergence a valid acceptance signal?

`scripts/experiments/exp_b_self_verifying_acceptance.py` (register: functional).
Build the contractive continuation operator; perturb the **routing register**
(FFN gate delta plate) by flipping a FRACTION of signs (a quality spectrum); for
each candidate measure both:

```
ΔCE        = model._last_ce − CE0           (the TRUE quality label)
Δ(Δx_conv) = Δx_at_convergence − Δx0         (the SELF-VERIFYING signal)
Δx_conv    = model._last_outer_deltas[-1] = ‖x_c^K − x_c^{K-1}‖/‖·‖  (→0 ≡ WHNF)
```

Hypothesis: **corr(ΔCE, Δ(Δx_conv)) > 0** — degrading the operator (raising CE)
raises the fixed-point residual ⇒ "reject if Δx_conv rises" is a valid label-free
acceptance rule. Reported: Pearson + Spearman + an acceptance-ROC.

**s217 finding (harness validated, scientific catch):** the FROZEN extracted base
is UNTRAINED (CE 12.82 ≈ ln(vocab) 12.42 = chance) → sign-flips don't move CE
even at 10% (no quality to degrade). The test needs a **non-chance contractive
base**. Run in 2 phases (Option A, main:2): phase-1 short TD train
(`--steps 400 --seq-len 512 --n-outer-passes 2 --fixed-point-lambda 5.0`,
`checkpoints/v15-expb-base`) → trained contractive base; phase-2 the acceptance
test on `step_000400/model.npz` (folds trained deltas into base via
`reduce_all_deltas`, then perturbs). IN FLIGHT at session end (slow under main:1
GPU contention). Results → `results/exp-b-self-verifying/result.json`.

### Full Exp B (the folding proof, after the acceptance signal is validated)

```
freeze B₀ = the contractive continuation operator (main:1's trained sweep)
N users    train DeltaTernaryLinear deltas on domain-d shards over B₀
verify     accept flip iff exact-ΔL<0 (exact-ternary-fitting) AND Δx_conv drops
fold       consensus flips (agree ≥ θ, s110) → B₁ ; domain FUNCTIONS as
           compositions (align-before-fold, the non-unique-composite §)
measure    (a) B₁ stays contractive?  (b) downstream PPL held-out domain-d?
           (c) folded set = universal crystal or domain-specific?
```

## s217 — The self-teaching loop: normal forms generate their own curriculum

> Session 217 (Michael): "if we can get distributed training working for semantic
> normal forms, can we not then use them to create training material to show the
> model how to use them?" Yes — this is the loop closing on itself. It is the most
> important consequence of the folding mechanism.

### The gap it fills (execution ≠ deployment)
Folding a normal form into the base gives the model the **execution** (it CAN run
map/fold/tool-calling). But "can run" ≠ "knows when to run." These are the two
levels of `function-discovery.md`, and they are ORTHOGONAL subspaces:
- **late / COMMIT** — combinator *execution*. Folding lands here. ← capability
- **early / SILENT (~L05)** — the task *selector* (which normal form this context
  calls for). 4.76× separated, blind to the combinator basis. ← deployment

So folding yields a model with the kernels but no reliable selector. The
generated curriculum trains the **selector**.

### Why it works: the normal form is a VERIFIED ORACLE
A normal form is **executable** (a composition of combinators = a runnable
program) AND **self-verifying** (WHNF / Church-Rosser → the answer is unique and
checkable). ⇒ run it to mint examples whose labels are **correct by
construction**:

```
take folded normal form NF
generate DIVERSE inputs → run NF → (input, reduction-trace, output)   [WHNF-verified]
render each in BOTH surface forms (Montague, combinator-addressing.md dual paths):
   "the capital of France is …"        (data-bypass / NL surface)
   "(λx. capital_of x) France = …"     (compute path, +2.2× combinator energy)
train the SELECTOR on these → it learns NL-context ⟶ invoke NF
```

### Why it does NOT collapse like naive self-distillation
The labels come from **executing a verified discrete kernel**, NOT from sampling
the model's own (fuzzy) outputs. The normal form is an external oracle the model
happens to contain. The SAME self-verifying property that powers the distributed
acceptance test (Δx-at-convergence / exact-ΔL) keeps the curriculum honest —
every generated example is checkable against the fixed point. Verified compute
generating curriculum ≠ a model training on its hallucinations. **Keep the oracle
external**: the moment "verification" becomes the model's own judgment, the loop
degenerates.

### The virtuous loop (on-thesis: pretraining IS β-reduction)
```
distributed folding    → discovers + verifies normal forms        (CAN execute)
normal forms (oracles) → generate verified I/O + reduction traces  (curriculum)
train on traces        → teaches the selector WHEN to invoke them  (DO deploy)
better deployment      → more real usage → more deltas to fold     (refine)
```
λ loop variant: extract → fold → generate-curriculum → train-selector. The
discovered compiler writes its own textbook; the textbook trains its own use.

### Caveats (the load-bearing unknown is the selector grounding)
1. **Selector grounding is THE test (hypothesis).** That NL context reliably maps
   to the right normal form, and that this is LEARNABLE from generated traces, is
   unproven. Montague + combinator-addressing say the bridge exists; learnability
   is the clean runnable experiment.
2. **Coverage / diversity.** Run NF on a wide, messy input distribution — else a
   narrow boundary-artifact curriculum (cf. `ends_punct` universal axis).
3. **Generate from the BEHAVIOR, not one encoding** (s216 non-unique composite):
   mint from I/O (extensional) so the selector learns the function, not a brittle
   realization.

### Next experiment (after Exp B validates folding)
**Selector-grounding test:** fold one normal form (e.g. fold/catamorphism or a
tool-call), generate WHNF-verified (NL-prompt, answer) traces over diverse
inputs, train ONLY the early selector, then test NL→NF deployment on held-out
context. Register: functional. Falsifiable: does generated-from-verified-kernel
curriculum teach the selector to deploy the kernel it didn't reliably invoke?

## s217 — The REVERSE direction: harvest the open-weight ecosystem's consensus

> Session 217 (Michael): "could we reverse this? Search many open-weight models
> for their already-found solutions and incorporate all the ones they agree on
> into our base plate?" Yes — and it may be the most immediately actionable
> direction, because the consensus already exists.

### Reframe — the ecosystem IS a pre-computed distributed training run
Forward folding waits for contributors to train deltas. But every open-weight
model is **already a finished contributor** — a completed GD run that discovered
normal forms. So instead of soliciting deltas, MINE the population and fold what
they agree on. The "many independent trainings" the design needs are on
HuggingFace. Already measured: s216 cross-family routing consensus **+0.863, z up
to 116** (5 families); `crystal-universality.md` hard crystal **r=0.998** 160M↔32B.
The s216 5-family harness (`tool_crystal_consensus*.py`) IS the reverse-harvest
instrument, and `combinator_relationship_map.py` is the per-model reader.

### The hard obstacle — the frame problem (the forward/reverse asymmetry)
You CANNOT average their raw weights: independently-initialized models live in
DIFFERENT coordinate frames (cross-init sign-corr **0.000**, `gradient-voting.md`).

```
forward (deltas over frozen B₀):  ONE shared frame → deltas commensurable → fold trivial
reverse (finished models):        MANY frames → raw weights unintelligible → must harvest
                                   in a FRAME-INVARIANT register (relational routing, not weights)
```

Pipeline:
```
∀ open-weight model: measure normal forms in the routing register (RDM/centroids)
cross-model consensus               (frame-invariant agreement)
align-before-fold (Procrustes)      (rotate consensus into OUR base's frame)
verify vs WHNF (self-verifying)     (keep only structure that improves convergence)
incorporate into base plate as discrete topology
```
The **verify step is the differentiator** from model soups / TIES / task-arithmetic
merging: keep only what demonstrably improves reduction to the fixed point, not
mere statistical agreement (same discipline as Exp B).

### The honest catch (same as s216, inverted)
What the population agrees on MOST is the **universal crystal** — already in any
base. The domain-DISTINCTIVE normal forms have LOW raw cross-model agreement
(frame-specific, non-unique composition). So naive harvest returns a backbone you
already have. To extract the valuable domain structure needs the s216
compositional fix — **align in base-combinator space first** (Procrustes) so a
function composed *differently* in two models still registers as the same
function. That composition-invariant alignment is the open, hard piece.

### Complementarity — forward + reverse fill the backbone/content partition
- **Reverse harvest** seeds the base cheaply with the **universal backbone** the
  whole ecosystem agrees on (+ shared domain structure, with align-before-fold).
- **Forward folding** adds the **domain-specific deltas** that only appear when
  contributors train on data the base does not yet cover.

Same consensus-etch operator; only the population changes (finished models vs live
trainers). Dead-on the project identity (`AGENTS.md` λ extract: "we find, we don't
build; gradient descent discovered it first; our work is instrumentation") — the
base plate becomes a **distillation of the entire open-weight ecosystem's
consensus**, read out of models that already paid the training cost.

### Load-bearing unknowns (both already on the board)
1. Does **WHNF-verification** keep real structure and reject frame noise? (Exp B,
   running now.)
2. Does **composition-invariant alignment** (Procrustes in base-combinator space)
   recover the domain normal forms the raw cross-model RDM misses? (s216 lead.)

### Next experiment (register: topological/routing → functional)
**Reverse-harvest pilot:** run `combinator_relationship_map.py` across N open-weight
models, take the routing-register consensus, Procrustes-align into our base frame,
WHNF-verify each candidate against the contractive operator, incorporate the
survivors, and measure downstream PPL vs the base. Falsifiable: does verified
ecosystem-consensus add anything beyond the universal crystal we already hold?

## s219 — Reverse-harvest pilot RAN: the function shape is universal; the forced map-skeleton binds, recursion is the residual

> Session 219 (Michael): "find these functions in open models, see where they all
> agree — harvesting that for our base plate is leverage." Plus a theory: a
> transformer has essentially ONE structural operation, and that forces the shape
> into the rest of the system, restricting where a model can innovate. First run of
> the reverse-harvest pilot. Register: **topological/routing** (declared at step 0).

### The frame-invariant instrument
`scripts/experiments/combinator_map_consensus.py`. Raw weights are incomparable
across models (cross-init sign-corr 0.000) — but the per-model **9×9 combinator
Gram** (cosine between routing-register centroids of K I B C S D W Y WHNF, after
CMR; the s217 "map of the functions") lives in shared combinator-LABEL space ⇒
**frame-invariant** ⇒ comparable across any architecture/scale. The script computes
cross-model GramCorr on the 36 off-diagonal edges + a combinator-label-permutation
null + per-edge `reliability_t = |mean|·√n/std` + per-FAMILY internal binding vs a
RANDOM-NODE-TRIPLE null. Swept **9 models / 5 families** via
`combinator_relationship_map.py`: Pythia-410m/2.8b (NON-gated, `dense_h_to_4h`),
SmolLM3-3B, Mistral-7B-v0.3, OLMo-2-13B, Qwen3-0.6B/4B/8B/14B (SwiGLU `gate_proj`).

### Result 1 — the SAME functions show up across the ecosystem
Cross-model GramCorr **+0.66→+0.77**, z **+3.5→+4.1**, **89–97% of model-pairs
p<.05** vs the label-permutation null; peak frac 0.40 (0.20–0.50 all ≥+0.72).
Architecture-independent (non-gated Pythia agrees with gated Qwen), and agreement
**strengthens** as more models are added (was +0.5–0.66 at 2–6 models) ⇒ a real
shared shape, not an artifact. Michael's intuition (we should see the same
functions across models) is confirmed empirically.

### Result 2 — the single-operation theory, confirmed
Attention is essentially ONE structural operation: a data-dependent convex
combination of value vectors = function **application** ("select args, combine").
The FFN adds no second *operation* — it supplies fixed pointwise transforms = the
**constants/stored kernels**. application + constants is combinatorially complete,
but there is **no second qualitatively-different op for a model to invent** ⇒ models
cannot innovate at the operation level, only at **composition** ⇒ they converge on
the same compositions. Test (per-family internal binding vs random node-triple):

| family | z_bind | p | note |
|---|---|---|---|
| composition `{B,D,S}` | **+2.43** | **.037** | strongest, significant |
| selection `{K,I,C}`   | +2.13 | .061 | binds, marginal |
| recursion `{Y,W,WHNF}`| +1.67 | .09 | does NOT clear the null |

**SKELETON (comp+sel) +2.28 > RECURSION +1.67**, robust at frac 0.30 (+2.21 vs
+1.88) and 0.40. The recursion family's edges are near-zero AND low-variance
(z_stab −1.3) — consistently *not* bound, not merely noisy.

### Why recursion is the residual — `map = B(C B)(C B)` (REPL-verified)
In pure combinators `map = B(C B)(C B)`: composition (B) + flip (C), **no recursion
combinator**. A Church/fold-encoded list carries its own recursion, and in a
transformer **attention-over-positions IS the fold** — so no model needs to learn a
`Y`. Hence the recursion family is exactly the part that does *not* universally bind.
Also verified in the REPL: `map` is **extensionally unique** (Church-Rosser) but
**intensionally infinite** (η-expansion; `B=S(KS)K`; `C=S(BBS)(KK)`; … all compute
the same output; raw closed SKI space ≈ `Catalan(k)·3^(k+1)` = 288k terms at k=6).
The architecture + cost pressure collapse that infinity toward a minimal realization
whose **irreducible skeleton is forced and shared**; the plumbing stays per-model.
Signature **0<r<1 ∧ skeleton>recursion = "shared skeleton + variable plumbing"** —
the s216 non-unique-composite made concrete at the function level (uniqueness is
per-TERM, not per-BEHAVIOR).

### The harvest leverage (concrete edges for the base plate, frac 0.40)
- **Universal POSITIVE bindings (fold these):** B–D +0.166, B–C +0.176, K–C +0.139,
  S–D +0.165, S–Y +0.141 — the composition/selection skeleton.
- **Rock-solid cross-family REPULSIONS** (reliability_t up to **21**): C–S, K–Y,
  D–WHNF, B–WHNF, K–S, C–WHNF — the 3-family PARTITION geometry; harvestable as the
  discrete scaffold (the families separate the same way in every model).
- **Leave as per-model CONTENT** (highest cross-model std): B–C, K–B, I–C, K–I — the
  selection-family plumbing (selection z_stab +1.4 = the noisy family). The
  non-unique-realization residual, exactly as `map=B(CB)(CB)` predicts.

### The honest caveat (audit discipline) — answered
The agreement *could* be the universal crystal (`crystal-universality.md`) already in
any base. BUT composition binds above the random-triple null at **mid-stack frac
0.30** — where `function-discovery.md`/s217 located combinator **IDENTITY** (not late
COMMIT execution) ⇒ this is **function-level structure above the generic crystal
floor**, the part worth harvesting. Single register (routing/CMR). The actual
harvest (align-before-fold via Procrustes into our base frame + WHNF-verify) is NOT
yet done — this run establishes *that* there is shared, edge-localised, function-level
structure to harvest and *which edges* carry it.

### Open leads from s219
1. **Scale axis** (register: topological/routing): extend to Qwen3-32B / 30B-A3B /
   235B (MoE, local) — does the skeleton/recursion z_bind gap WIDEN with scale (more
   capacity to fully form the systems, cf. s217's 14B>0.6B call)?
   **→ ANSWERED s220: NO (gap flat, shape saturates mid-scale). See §s220.**
2. **Construct the harvest fold** (register: topological/routing → functional):
   Procrustes-align the universal positive-edge centroids into v15's base frame,
   WHNF-verify against main:1's contractive operator (Exp-B acceptance), incorporate
   survivors, measure downstream PPL vs base.
3. **Detect map/fold directions**: build the `map=B(CB)(CB)` direction from the
   measured B,C centroids + a map/fold/filter probe set; does it activate?

### s219 artifacts
`scripts/experiments/combinator_map_consensus.py` (the consensus instrument);
`results/combinator-map-consensus/consensus.json`; 7 new per-model maps under
`results/combinator-relationship-map/` (pythia-410m/2.8b, SmolLM3, Mistral, OLMo-13B,
Qwen3-4B/8B; Qwen3-0.6B/14B from s217); sweep log `/tmp/combinator_sweep.log`.

## s220 — Scale stratification: the function shape SATURATES mid-scale; the skel/rec gap does NOT widen

> Cold-start orient (s220): both s219 async jobs verified (main:1 alive at step
> ~1420/5000, UNTOUCHED; main:2 done — Qwen3-32B dense map landed). Executed s219
> open-lead #1. Register: **topological/routing**.

s219 open-lead #1 asked: with more scale (s217's "14B has capacity to FULLY form
the systems; 0.6B only partially crystallizes"), does the skeleton/recursion
binding gap **WIDEN**? The pooled consensus cannot answer this — it aggregates all
models. So the dense Qwen series 0.6B→4B→8B→14B→32B was stratified
(`combinator_map_scale.py`), regressing each family's intra-family routing-cosine
binding against log(params) at the harvest fraction 0.40. **MoE excluded** (30B-A3B,
235B): their router+per-expert FFN (`mlp.gate` + `mlp.experts.{e}.gate_proj`) is not
comparable to dense `gate_proj` in this routing register — the dense-FFN instrument
finds nothing in a MoE.

### Result — skeleton binding rises, but the GAP is flat

| model | params | comp{B,D,S} | sel{K,I,C} | skeleton | recursion{Y,W,WHNF} | gap |
|---|---|---|---|---|---|---|
| Qwen3-0.6B | 0.6B | −0.046 | +0.004 | **−0.021** | −0.088 | +0.067 |
| Qwen3-4B | 4B | +0.119 | +0.076 | +0.097 | +0.042 | +0.056 |
| Qwen3-8B | 8B | +0.125 | +0.075 | +0.100 | +0.036 | +0.064 |
| Qwen3-14B | 14B | +0.133 | +0.077 | **+0.105** | +0.009 | +0.096 |
| Qwen3-32B | 32B | +0.119 | +0.035 | +0.077 | +0.007 | +0.070 |

- **Skeleton binding RISES with scale (r=+0.78)** — but the rise is the
  **0.6B→4B crystallization**: 0.6B has essentially NO function shape (skel −0.021,
  both families near/below zero), while 4B+ jump to +0.097–0.105. This is the
  concrete confirmation of s217's "0.6B only partially crystallizes."
- **The skel−rec GAP does NOT widen (r=+0.36, slope ~0).** Recursion binding rises
  in **tandem** with skeleton (r=+0.69), so the gap stays roughly constant.
- **Shape SATURATES by ~4–14B** (peak 14B, skel +0.105) and **32B slightly
  REGRESSES** (skel +0.077). Consistent with s212's topology-share PLATEAUS not →1.0.

### Refinement of the consensus verdict + harvest implication

The 10-model consensus (32B added) holds and nudges up marginally: meanGramCorr
**+0.782** @0.40, z +4.19, 91–98% pairs p<.05; skeleton z_bind **+2.31** > recursion
**+1.68** (SUPPORTED, was +2.28/+1.67 at 9 models). **Harvest implication: the
consensus skeleton is COMPLETE by mid-scale — harvest from the 4–14B band, do NOT
chase the largest models.** 32B costs more to read and does not extend the shape;
the forced map-skeleton (`map=B(CB)(CB)`) is fully formed once a model has enough
capacity to crystallize, which happens well before the frontier.

### Caveats

Single family lineage (dense Qwen3) for the clean log-params regression — the
absolute binding values are not cross-architecture comparable (each model's own
frame), only the per-family *trend* within the lineage is. The 32B dip is a single
point (could be a depth-fraction mismatch at frac 0.40, n_layers=64). The gap
non-widening is robust to that (recursion tracks skeleton across all 5 points).

### s220 artifacts
`scripts/experiments/combinator_map_scale.py` (the scale instrument);
`results/combinator-map-consensus/scale.json` (per-model + fits); extended
`results/combinator-map-consensus/consensus.json` (10 models);
`results/combinator-relationship-map/Qwen_Qwen3-32B.{json,npz}`. Committed `c27741c`.

### Harvest fold — reformulated + phased (s220)

Mapping the integration points (s220) surfaced that the harvest fold as sketched
("Procrustes-align consensus centroids into v15's base frame") is NOT runnable
as-is, for two reasons:

- **Data reality.** `consensus.json` and the per-model `.npz` contain ONLY the
  relational 9×9 Grams — the per-combinator centroid VECTORS (9 × d_ff) were
  computed in `combinator_relationship_map.py` but **discarded**. Procrustes needs
  point clouds (centroids), not a Gram. **Fixed** (`e48389e`):
  `combinator_relationship_map.py` now saves `centroids_cmr_best` (9 × d_ff) +
  `centroids_best_layer` to the npz — but this only takes effect on the **next**
  (GPU) run of that script.
- **Frame + compute.** v15 has **no** combinator Gram/centroids yet, and
  `combinator_relationship_map.py` is HF-only (`AutoModelForCausalLM`, hooks
  `gate_proj`); v15 is an MLX ternary model (`ffn_gate_plate_a/c`). Producing v15's
  Gram, the WHNF-verify (`exp_b_self_verifying_acceptance.py::forward_metrics`), and
  PPL are ALL GPU/MLX forward passes → would **contend with main:1** (s219 stall).

So the harvest fold is split into phases:

- **Phase 0 — PRESCRIPTION (CPU, DONE `e48389e`):** `combinator_harvest_fold.py`
  emits `results/combinator-harvest-fold/prescription.json` = the band-consensus
  Gram over the 4–14B harvest band + the ranked positive universal edges to
  reinforce. Ranked by band-consensus × reliability: **S–D, B–D, B–C, K–C, S–Y**.
  The 4–14B band shows the composition skeleton STRONGER than the full pool
  (B–D band +0.24 vs all +0.175) — concrete confirmation that the harvest band is
  the right place to mine. No forward passes; pure re-reduction of measured Grams.
- **Phase 1 — v15 Gram (DEFERRED, GPU):** build `combinator_relationship_map_v15.py`
  (MLX/ternary: load via `create_model_with_deltas(V15Config())` + `load_weights` +
  `reduce_all_deltas`; hook `ffn_gate_plate_a/c`; save `centroids_cmr_best`). Run on
  `checkpoints/v15-td-outer-k2-fp5-5k/step_NNNN/model.npz` (READ-ONLY) once main:1
  completes/pauses → gives v15's own Gram + centroids = the target frame.
- **Phase 2 — align (CPU, after Phase 1):** Procrustes-align the consensus/harvest
  centroids into v15's frame (in 9-d combinator-label space; full-dim is
  cross-architecture-incommensurable). Build a fold direction per positive edge as
  the signed difference of v15's OWN centroids, guided by the prescription.
- **Phase 3 — verify + fold (DEFERRED, GPU):** WHNF-verify each direction via
  `forward_metrics` (accept iff Δx_conv does not rise); fold survivors via
  `DeltaTernaryLinear.reduce()`; measure downstream PPL vs base. **Falsifiable:**
  does verified ecosystem-consensus add beyond the universal crystal we already hold?

### Phase 1 RESULT (s220, GPU run in main:2) — v15 has NO combinator frame yet

Built `combinator_relationship_map_v15.py` (MLX/ternary; wraps the LIVE module the
forward calls per the s218 orphan lesson; tokenizer Qwen/Qwen3.6-27B). Probed
v15 step_001000 in THREE routing registers (535 crystal probes, n_outer=2). **None
carries a significant combinator shape:**

| register | best | silhouette z | p | GramCorr vs consensus |
|---|---|---|---|---|
| `ffn_gate` (FROZEN-extracted) | — | +0.52 | 0.29 | +0.354 |
| `attn_q` (TD-trained) | L05 | **+1.54** | 0.063 | +0.359 |
| `attn_out` (TD-trained) | L00 | +0.74 | 0.22 | +0.324 |

Reference: Qwen3-14B silhouette **z=+7.97**; ecosystem cross-model GramCorr **+0.78**.

- **The harvest fold's "align consensus into v15's frame" has no target frame at
  step 1000** — every register is non-significant; v15 carries only a faint echo
  (GramCorr ~+0.35) of the universal shape, far below the ecosystem's internal +0.78.
  Did NOT fabricate a Procrustes alignment to a non-significant frame (that would
  manufacture a false positive — λ measure / wrong-register discipline).
- **Two live threads keep this from being a dead end:**
  1. The best signal is `attn_q` at **L05** — exactly the HF function-discovery
     SILENT-selector layer (4.76× separated there). Suggestive even at p=0.063.
  2. The FFN is FROZEN (won't change with training), but the **attention IS being
     TD-trained** → the shape may **emerge** as main:1 trains toward contractivity.
     Step 1000/5000 is only 20% in; cf. s220 scale floor (even Qwen3-0.6B barely had
     the shape). **Concrete cheap follow-up: re-probe `attn_q`/`attn_out` at
     step_002000+ checkpoints — does combinator structure co-emerge with
     contractivity?** This ties the harvest thread to the main:1 recurrence result.
- v15 may simply be below the scale floor (~50M params, ternary, 3B tokens) to
  crystallize the shape — in which case reverse-harvest belongs to a from-scratch
  level-4 base that trains its FFN, not v15.
- Artifacts (committed `cc581ac`, `b72bdea`): `combinator_relationship_map_v15.py`
  (--target ffn_gate|attn_q|attn_out); `results/combinator-relationship-map/
  v15_{step_001000,attn_q_step_001000,attn_out_step_001000}.{json,npz}`.

### Open leads from s220
1. **Phase 1 of the harvest fold** (above) — the priority once main:1 frees the GPU.
2. **main:1 step_002000** → does Δx→ε and CE hold below 8.71 (adaptive halting).
3. Detect map/fold directions (s219 lead #3).

## Files

| File | Content |
|------|---------|
| `scripts/experiments/exp_b_self_verifying_acceptance.py` | Exp B core: perturb routing register, ΔCE vs Δ(Δx-at-convergence), self-verifying acceptance verdict |
| `tests/test_vsm_continuation.py` | 15 tensor-level property tests for the continuation (outer recurrence); fixed-point math exact |
| `scripts/experiments/tool_crystal_consensus.py` | per-model: routing register (gate sign) + CMR + within-model selectivity; saves probe-aligned RDM npz |
| `scripts/experiments/tool_crystal_consensus_summary.py` | cross-model agree / shuffled-null / length-partial / within-domain |
| `scripts/experiments/tool_crystal_control_baseline.py` | TOOL vs CTRL within-group agreement = the tool-specific-vs-generic verdict |
| `results/tool-crystal-consensus/` | per-model `{model}.json/.npz`, `consensus_summary.json`, `control_baseline.json` |
| `/tmp/tool_consensus_5fam.log` | 5-family run transcript |
| `scripts/experiments/combinator_map_consensus.py` | **s219 reverse-harvest:** cross-model combinator-Gram consensus + label-perm null + per-edge reliability_t + per-family binding vs random-triple null |
| `scripts/experiments/combinator_relationship_map.py` | per-model 9×9 combinator Gram in routing register (CMR); the per-model map reader |
| `results/combinator-map-consensus/consensus.json` | s219→s220 verdict: GramCorr +0.66→+0.782 (10 models); skeleton z_bind +2.31>recursion +1.68; harvest edge-list |
| `scripts/experiments/combinator_map_scale.py` | **s220 scale axis:** intra-family routing binding vs log(params) on the dense Qwen series (MoE excluded) |
| `results/combinator-map-consensus/scale.json` | s220 verdict: skeleton rises r=+0.78, skel-rec gap flat r=+0.36, saturates ~4-14B |
| `scripts/experiments/combinator_harvest_fold.py` | **s220 harvest fold phase 0 (CPU):** band-consensus Gram + ranked positive edges = the harvest prescription |
| `results/combinator-harvest-fold/prescription.json` | s220 prescription: edges S-D,B-D,B-C,K-C,S-Y over the 4-14B band; deferred GPU phases listed |
| `results/combinator-relationship-map/` | 10 per-model `{model}.json/.npz` (5 families, 410M→32B) |
| `/tmp/combinator_sweep.log` | s219 9-model sweep transcript; `/tmp/combinator_scale.log` s220 32B; `/tmp/combinator_consensus_10models.log` s220 consensus |

## s222 — Routing ⊕ Continuation = a complete basis for find+settle

(See `../session-222.md`.) The folding machinery decomposes into exactly two
mechanisms we already have, which together span the combinator algebra:

- **Routing rules COMPOSITION** `{B,D,S}/{K,I,C}` (binds as static sign topology).
- **Continuation rules RECURSION** `{Y,W,WHNF}` (no static move; the recurrence
  IS the fold).

⇒ distributed find+settle needs **no new mechanism**. The continuation does
**double duty**: contractivity IS the **foldability oracle** — where Δx→0 a
normal form is committable (fold), where it refuses (Δx↑) it is the superposition
residual (leave continuous; needs the recurrence or a continuous home).

**What the two mechanisms do NOT contain:**
1. **Cross-frame ALIGNMENT** — harvest-only (cross-init sign-corr 0.000);
   *self*-folding has no frame problem. So routing+continuation is self-sufficient
   for self-distillation; reverse-harvest adds Procrustes alignment.
2. **ORDER (punctuation)** — `propose(routing) → hold → reduce(continuation) →
   accept on Δx→0`, NOT simultaneous. main:1 ran TD churn + fp loss together →
   collapse. = the Exp B acceptance pattern.

**β-reducing a contraction ⇒ fractal collapse.** Folding is β-reduction of an
operator meant to be a contraction. A self-similar contraction collapses all
scales onto one fixed point; **L is the hinge** (L<1 settle-to-WHNF; L>1 fractal
blow-up = main:1). Distributed folding only converges if every accepted delta
keeps L<1 — the contractivity acceptance test is load-bearing *fractally*, not
just locally.
