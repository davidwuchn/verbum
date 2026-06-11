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
