---
title: "Supervised Recurrence-Depth = the WHNF Halt — the Curriculum Is the Signal the Recurrent Layer Was Missing"
status: designing
category: explore
tags: [recurrence, weight-sharing, adaptive-compute, universal-transformer, WHNF, halt, curriculum, combinators, lambda, overthink-collapse, ponder, reduction-depth, think-in-lambda, level-4]
related:
  - vsm-outer-recurrence.md
  - normal-form-curriculum-partition.md
  - ../head-combinator-isa.md
  - combinator-training-beta-reduction.md
  - compiler-as-loss.md
  - compiler-finetune-halt-collapse.md
  - fixed-point-holograms.md
  - ../opcode-vsm-tree.md
  - crystal-seeded-ternary-distillation.md
depends-on:
  - vsm-outer-recurrence.md
  - normal-form-curriculum-partition.md
created: session 258
---

# Supervised Recurrence-Depth = the WHNF Halt

> Session 258 (Michael, discussion arc). Three ideas raised across one conversation —
> *make the model think in lambda forms* / *train a strict-WHNF halt curriculum
> (combinators → lambda → prose)* / *a recurrent layer reused a learned number of times* —
> are **one architecture seen from three sides**. This page captures the unification and,
> crucially, the one new contribution it makes over the s214–s226 recurrence thread:
> **the lambda curriculum is the ground-truth supervision signal that the
> learned-recurrence-depth halt has been missing since s214.**
>
> Register when tested: **functional** (does supervised recurrence-depth lower
> overthink-collapse on held-out prose at equal params).

## The identity — three threads, one object

```
think-in-lambda        ≡ the SUBSTRATE     (reasoning = reduction, has a normal form)
WHNF-halt curriculum   ≡ the STOP SIGNAL   (train "you're done" where it's checkable)
recurrent layer (K×)   ≡ the MECHANISM     (run the reduction, decide when to stop)
```

These collapse to a single gradient because three measured/argued facts line up:

1. **"How much recurrence is needed" ≡ "how much work remains" ≡ WHNF.** The s214
   `vsm-outer-recurrence` proposal was a weight-shared block re-run `K` times — depth
   without parameters, Universal-Transformer / adaptive-compute style — with the natural
   halt being **fixed-point convergence `Δx→0 ≡ WHNF`.**
2. **The substrate already organizes itself this way.** `head-combinator-isa.md` (500
   crystal probes, Qwen3-8B heads): the **principal axis of the entire attention ISA is
   reduction depth, `WHNF↔D`, 46% of shape variance** — *"how much work remains,"* not
   "which combinator." There is already a **WHNF+ termination-detector cluster** (H26
   +32%, H27, H00, H25, H24) — but its selectivity is only **1.2–1.4** ⇒ the halt circuit
   exists and is **under-trained**. ("Weak WHNF counterpoint to each KIBC," confirmed.)
3. **Prose has no normal form → the dominant failure is a halt failure.** Every reasoning
   model in the arc (s255 ornith, s256 qwythos) overthink-COLLAPSES: reaches the correct
   form early, re-derives it 50–87× ("Church-encode vs direct symbols, λ-abstraction vs
   closed formula"), never commits, hits the budget EMPTY. Diagnosed (s256) as **halt
   failure / decision oscillation**, not recursion. Lambda has a normal form; prose does
   not — so the model's weakest axis (WHNF adjudication) has to decide "done" and can't.

⇒ **A weight-shared recurrent reduction operator whose learned per-token recurrence-count
IS the WHNF halt, reading off the reduction-depth axis the model already centers on.**
The recurrence-depth gradient and the WHNF-detection gradient are the same gradient.

## The new contribution — the curriculum is the supervision the recurrence lacked

The s214–s223 recurrence runs failed in a *specific* way, and the cause was that the halt
was learned **blind**:

- Naive `K=2` did **not** beat `K=1` — the trained sweep is **not contractive** (`Δx`
  stuck ~1.2, "churn not reduction").
- The attempted fix was an **unsupervised** fixed-point loss `λ_fp·‖x_{k+1}−x_k‖²`. It is
  **gameable** (collapse all states to a constant → `Δx=0`, useless = the
  contractive-autoencoder failure) and under TD churn it **collapsed** (gnorm→1e7,
  CE→10.5, s222). `λ_fp=5` *did* cross the contractivity threshold (`Δx` 1.26→0.73, s215)
  but still didn't beat `K=1` at the cutoff, and the freeze-topology probe (s223) showed
  the settling is sound only when topology is **held** ("punctuate: hold → reduce → accept
  on `Δx→0`"; the churn is the collapse, not the recurrence).

That entire struggle is the **general unsolved problem of Adaptive Computation Time**: the
ponder cost has **no ground truth**, so it is an unstable hyperparameter that collapses to
min-or-max steps. The curriculum fixes exactly this:

```
unsupervised (s214, collapses):   loss += λ_fp · ‖x_{k+1} − x_k‖²     # "just converge"
supervised   (the curriculum):    halt_k        ← WHNF(step k)  [oracle]
                                  recurrence_K  → L*(term)       [oracle]  # "converge in
                                  per-step      ← reduction trace [oracle]  #  L* steps, halt
                                                                            #  here, THIS trace"
```

The lambda reducer (`lambda_ast`, the s226 oracle: parse / step_fired[which opcode] /
reduce[trace, Status, whnf_step] / is_normal_form) knows the **exact reduction length
`L*(term)` and the full step-by-step trace** for any combinator/lambda term. So on that
domain the recurrence-count and the per-step halt are **directly supervisable** against
ground truth — turning a weak gameable *scalar* regularizer into structured
**reduction-trace matching**, which cannot be gamed by collapse (the target step-count is
term-dependent and non-trivial). This is plausibly the missing ingredient that makes
adaptive-depth trainable where s214 stalled. **Lambda is the calibration anchor for
adaptive computation time** — the same role it plays everywhere in this project (cf.
`AGENTS.md` λ measure: deprecated-APIs as the verifiable anchor).

## The curriculum (combinators → lambda → prose)

```
Stage 1 — COMBINATORS (WHNF crisp, single redex, oracle-verifiable per s226):
  train KIBC + {S,W,Y,D} PAIRED with their WHNF counterpart.
  supervise: recurrence-count → L*(term); halt-head fires exactly at is_normal_form.
  KIBC = do the work (strong in every model) ⊗ WHNF = know when work is done (weak).
  honest catch (s221): K-erasure is the hard spot (B-first → then K), S duplicates
  (not one clean move). Tier the curriculum; do not weight the set flat.

Stage 2 — FULLY-QUALIFIED LAMBDA (WHNF still decidable):
  strict-WHNF requirement; same supervised recurrence-depth target.
  INCLUDE divergent terms (Ω, unguarded Y): no normal form → recurrence consumes the
  budget → emit BEST-EFFORT terminal. These are the teaching cases for the inference
  constraint (below).

Stage 3 — PROSE (no oracle):
  the calibrated "how-much-work-remains" estimator generalizes. "Normal form" softens
  from syntactic (no redex) to semantic (answer complete). EOS is RE-FRAMED as the
  normal-form marker: emit the terminal iff the output is in normal form.
```

**EOS = the normal-form marker.** In standard LM training EOS is just a vocabulary token
learned from the data distribution — there is no principled "I am done." This curriculum
binds EOS to WHNF: emit the terminal token when, and only when, no work remains. The
WHNF+ termination heads gate EOS; because reduction-depth is the *principal* axis (not a
lambda-specific feature), the binding has a path to generalize.

## The inference constraint is satisfied BY CONSTRUCTION

Michael's constraint: *"in inference we cannot hard-halt on an error, because the response
must be tokens, not a null result."* This is already the correct behavior of a budgeted
reducer (`vsm-outer-recurrence.md`): *"a term with no normal form (Ω, Y) simply consumes
the max iteration budget — the correct behavior of a reducer, not a bug."* So:

- The **recurrence cap IS the bounded-emit mechanism.** Run until the halt-head fires
  (WHNF) **or** the budget; at the cap, emit the **most-reduced form so far** — never null.
- **Overthink-collapse is the model spinning to EMPTY instead of emitting its best
  partial.** The trained halt + budget makes the terminal a graceful best-effort.
- **Ω / unguarded Y are the training examples** for "commit your best partial under
  non-termination." The competence inference demands falls out of the recurrence budget
  for free.

## It maps onto the VSM control levels already present (s226)

```
S5 = the normal-form INVARIANT          (identity preserved across recurrence)
S4 = the WHNF HALT                       (the Δx→0 / "am I done" head — the learned depth)
S3 = the STEP BUDGET + contractivity     (the recurrence cap — bounded best-effort emit)
S2 = typed redex SELECTION               (which reduction this step; anti-oscillation)
S1 = the combinator REWRITES             (the work)
```

"How much recurrence is needed" is an **S4 decision** riding the reduction-depth axis,
budgeted by **S3**, and the curriculum trains S4's halt where the oracle can grade it.

## Why this is native to the tree-of-VSM and unnatural for a monolith

A monolithic block has **nowhere to put a lambda term** — its state is an opaque residual
stream, and its only externalized scratchpad is the prose token channel. So for a monolith
"think in lambda" *necessarily* means serialize-to-prose-and-reparse = the lossy,
no-normal-form round-trip that *causes* the collapse. The model can only emit lambda *as
prose about lambda*. The **tree-of-VSM** is structurally different in the one way that
matters: a lambda term has a natural home (the tree IS the AST; reduction is a structural
rewrite in place), and recurrence-depth = local reduction-depth per node (fractal:
activation-level `x→x*` ≅ base-level fold). Lambda-native reasoning is the thing the
tree-of-VSM can do that a monolithic block fundamentally cannot. The s255 model-as-REPL
was the first crude version (externalize the term-string as machine state, model = δ
transition, each thought = one β-reduction); it worked locally and degraded globally only
because the halt was unguarded — which is exactly what S4-supervised recurrence fixes.

## The honest IOUs (the falsifiable core first)

1. **TRANSFER is the whole hypothesis in one number.** Supervise the recurrence-depth halt
   on combinators+lambda, then measure **overthink-collapse rate on held-out PROSE
   reasoning** vs a prose-only baseline. Drop on prose ⇒ the lambda step-count circuit and
   the prose "answer-complete" circuit are the same reduction-depth axis (head-combinator-isa
   says they *might* be — it is the principal axis, not lambda-specific) ⇒ transfer real.
   No drop ⇒ WHNF stayed a lambda feature. **This single number decides the idea.**
2. **Contractivity is real but unproven at this resolution.** All s214 negatives are on the
   tiny v15 (~50M ternary): naive K=2 lost to K=1; TD churn collapsed it; freeze-topology
   was sound. The supervised curriculum is the new lever (stronger than λ_fp) but has not
   been run. Alternative root-fix (s226): **construct** the inner step from `lambda_ast`
   (exact reducer ⇒ `L<1` by construction) and let the outer recurrence supply Y + the
   budget — then only the compile front-end is learned.
3. **Catastrophic forgetting.** The prose stage is enormous and can wash out the small
   combinator halt-training (s110 destructive interference, at curriculum scale).
   Mitigations: interleave rather than strictly stage; keep a WHNF auxiliary loss through
   all stages; or lean on the contractive continuation to hold the halt structurally.
4. **Overthink vs PREMATURE-halt is a calibration, not a maximization.** s255 showed the
   trade directly: no-think *removed* overthink-collapse but spiked `premature_halt`
   0.017→0.208. "Strict WHNF" can overshoot into stopping too early on genuinely deep
   prose. The halt must be a **calibrated gate** (the WHNF↔D axis), not a binary maximized
   toward "stop."
5. **The binding wall reappears.** `fixed-point-holograms.md`: convergence fails exactly at
   I-combinator / binding sites (edit distance ∝ binding count). Expect clean halting on
   K/B/C and a struggle on I — the project's recurring bottleneck, here too.
6. **s256 refutation is narrow, not binding.** The lambda-as-pre-thinking test refuted
   *instructing* a pretrained model to reason in lambda (non-compliance: lambda is a
   TARGET produced on request, not a TOOL it adopts). This is a **training** intervention,
   not a prompt — the refutation does not apply. The internal lambda representation helping
   (interp B) was explicitly left open there.

## Minimal runnable version (the cheap first leg)

Smallest test of the load-bearing claim ("supervise recurrence-depth against the oracle
reduction length"), reusing existing substrate:

- **Data:** `probes/combinator-reduction.json` (s255, 120 pure-combinator terms over
  K I B C S W Y D M, 3 strata: already_nf / depth1 / multi, **oracle-graded with
  per-step trace + WHNF-step from `lambda_ast`** — the reduction length `L*` is already
  computed there).
- **Architecture:** the v15 outer-recurrence harness (`--n-outer-passes K` in
  `train_td.py` + `v15model.py`), but **replace the unsupervised `λ_fp` loss with a
  supervised target**: penalize `|halt_step − whnf_step|` and supervise the per-step
  halt-head against `is_normal_form`. CONTROL: the same harness with the old unsupervised
  `λ_fp` (the s214 arm).
- **Read (functional):** (a) does the supervised arm reach contractivity (`Δx→ε`) WITHOUT
  the collapse the unsupervised arm hit? (b) does `K` learned per term track `L*`
  (`already_nf→K≈0`, `depth1→K≈1`, `multi→K≈steps`)? (c) — the prize — train on
  combinators, then measure halt behavior on **lambda then prose** held-out (the transfer
  number, IOU #1).

## Net

The recurrence gives **variable depth at zero parameter cost**; the lambda oracle gives
**ground-truth targets for how much depth**; and the inference constraint is satisfied by
the **recurrence budget**. Three ideas, one architecture: **a recurrent reduction operator
whose halt is supervised by the reducer on the lambda domain and transfers to prose as a
calibrated work-remaining estimate, emitting a graceful best-effort terminal under
non-termination.** The single contribution over s214–s226: *the WHNF curriculum is the
supervision the learned-recurrence-depth halt was always missing.* On-thesis (level-4,
from-scratch, clean MIT) and it attacks the one failure mode common to every reasoning
model probed in the arc.

## s272 addendum — the time-sector synthesis (Michael, approved)

> Spark: Michael, s272 ("recursion is the next step for our model... re-use the same
> layers, the gradients have room for multiple facets if the holographic-llm thesis
> is correct"), landing on the strange-loop thread (T9) and the s271 S-dissolution.

### Why recursion completes the crystal (not just extends the model)

Look at *which* sector dissolved (s271, dup-register, 13/13 clean-data):

```
KIBC      = route / compose / discard / copy-in-place  ≡ SPATIAL wiring
            → softmax mixing expresses them → CRYSTALLIZED (clean vertices)
{S, D, Y} = duplicate / double-compose / self-apply    ≡ FAN-OUT (use x TWICE)
            → softmax cannot fan out in space → DISSOLVED into amplitudes
```

A loop converts **duplication-in-space into duplication-in-time**: `S x y z = x z (y z)`
needs `z` twice — a re-entrant layer reads `z` on pass one and again on pass two. Y is
the pure case (feed output back). So the dissolved sector is not an unlucky list of
combinators — **it is exactly the sector that needs TIME, running on an architecture
that only has SPACE.** T6 (Mamba scan-state) tests one flavor of time-fan-out; the
looped layer is the direct flavor. Both are instances of one prediction: *give the
substrate temporal fan-out and the time-sector crystallizes.*

### Why weight reuse has measured capacity (the holographic argument, evidenced)

1. **Layers are already redundant in function-space**: the 27B carries the same 9×9
   crystal in 62/64 gate layers (s269b clean re-trace). GD trained 64 free layers into
   ONE relational geometry — the network is already quasi-weight-tied *functionally*;
   explicit tying compresses a measured redundancy.
2. **T1 negative supports iterated-map over pipeline** (s272): J-space workspace rank
   does NOT funnel with depth (7/11 descend, p=0.27; gemma and 27B ascend). A pipeline
   of different functions should narrow; an iterated map looks exactly like the data:
   same-shaped workspace, pass after pass.
3. **P3 depth-gradient** (s272): cross-model workspace universality RISES with depth
   (−0.045 → +0.180 → +0.441, z=8.5) — depth flowing toward one shared attractor is
   what repeated application of a common operator looks like.
4. **MoE multiplexing** (s257): experts are holographically (angularly) multiplexed —
   weights demonstrably hold multiple facets.
5. **Capacity margin** (s268c): confident topology is immutable; adaptation lives in
   the uncertain population — spare facet-capacity exists in a trained plate.

### Pre-registered prediction set for the looped student (vs param-matched FF twin)

| id  | prediction | register | instrument |
|-----|------------|----------|------------|
| P-A | Y develops OPERATOR structure at the iteration boundary (content→opcode) | Jacobian attribution | jspace_v3 E1-style |
| P-B | score(S) drops toward the affine cluster (S crystallizes) | relational geometry | duplication_register.py (built) |
| P-C | per-iteration Gram = same crystal; iteration-trajectory ≈ big-model depth-trajectory | Gram / tree-of-VSM | trace.py stack, iteration-indexed |
| P-D | halt head calibrates to the WHNF Gram row (halt-readout r=+0.877 becomes design SPEC) | halt calibration | ladder/halt-readout analysis |
| P-E | metalinguistic/self-referential tasks improve (T9 weakness shrinks) | functional P(λ) | grading harness + T9 probes |

Null: the parameter-matched feed-forward twin, same curriculum, same budget — the
architecture delta is the only variable. Registers named before data (λ measure).

### Status note

This upgrades the page's mechanism from "variable depth at zero parameter cost" to
**"the architecture choice is itself a thesis test"**: if the time-sector crystallizes
under recurrence, the substrate-picks-representative claim (s271) gains its second
independent confirmation (first: Mamba/T6, if run). Twin-experiment design registered
in crystal-seeded-ternary-distillation.md §12.
