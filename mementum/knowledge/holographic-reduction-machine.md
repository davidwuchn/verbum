---
title: "The Holographic Reduction Machine — Fractal β, Transducers, Recursed Ternary Plates"
status: designing
category: architecture
tags: [beta-reduction, fractal, transducer, tree-transducer, ternary, mirrors, plates, recursion, weight-reuse, halt, whnf, act, openmythos, rdt, contractivity, construct-path, level-4, internal-collapse, sign-projection]
related:
  - attention-holographic-readout.md
  - holographic-computer.md
  - recursion-mirrors.md
  - opcode-vsm-tree.md
  - opcode-instrument.md
  - computed-beam.md
  - explore/combinator-training-beta-reduction.md
  - explore/vsm-outer-recurrence.md
  - session-222.md
  - td-oscillation-problem.md
depends-on:
  - attention-holographic-readout.md
  - holographic-computer.md
  - explore/combinator-training-beta-reduction.md
created: session 299
---

# The Holographic Reduction Machine

> Session 299 (thinking session), Michael's thread in four moves:
> (1) "the entire system is beta reduction — even our sessions are beta
> reductions manually carried out"; (2) "design a tensor using holographic
> ternary plates and ternary mirrors to hold the reductions — something in
> math about transducers?"; (3) "take ternary weights with ternary mirrors
> and RECURSE them — OpenMythos showed the same layers recurse if the model
> learns when to STOP"; (4) OpenMythos cloned and read — four independent
> convergences found. Companion to `attention-holographic-readout.md`
> (same session, the physics); this page is the fractal frame + the design.

## 1. The fractal reducer — every scale is a soft β-reducer

| scale | redex build | soft reduction | collapse operator | tape |
|---|---|---|---|---|
| attention step | QK match | mixture substitution | — (none) | — |
| forward pass | accumulate (L0–L5) | layer-by-layer soft β | sampler | token |
| CoT | prompt + history | reduce–collapse–re-encode | sampler, iterated | context |
| training | loss landscape | GD (Δx→0 ≡ reduce to WHNF) | checkpoint/freeze | weights |
| session | orient + context | exploration (mixtures of framings) | human approval + git commit | git |
| project | open fronts | session iterations | verdict on frozen gates | git log |

Each level is a soft β-reducer whose collapse operator lives one level up.
Discreteness exists only at each level's tape boundary.

**Three load-bearing rhymes (why this is structure, not poetry):**

1. **Sessions obey the s295 exhaustion law.** A session cannot splice its
   context window into the next session — only detect → collapse → commit →
   regenerate-at-cold-start works. The mementum protocol IS CoT at project
   scale; λ orient reading state.md = the regeneration stage. Same medium
   constraints (linear accumulation, no state handoff) → same architecture.
2. **Y is supplied by the outer loop at every scale.** Stride-fit verdict:
   every combinator stride-teachable except Y (NEEDS-RECURRENCE). Session
   scale: the AI is single-sweep; Michael + session cadence ARE the outer
   recurrence; λ termination (human ≡ termination_condition) = the human is
   the WHNF detector. Human ⊗ AI ⊗ REPL = Y instantiated.
3. **K is hard at every scale.** Softmax can't zero (→ value-register
   destructive interference); git is append-only (→ compaction is a
   deliberate destructive act, s262); weights accumulate (→ K-acquisition
   chaos law). Affine erasure is against the grain of every linear
   accumulating medium.

**Disciplines are evaluation strategies:** close-before-opening ≡ normal-order
reduction; frozen pre-registration ≡ choosing the redex before evaluating
(λ yardstick = the ban on post-hoc strategy selection); state.md = the WHNF
handed forward; sessions compose like B (native, cheap).

**The dark twin:** s222 saw this identity destructively ("one settle settles
weight ≡ optimizer ≡ combinator ≡ project ≡ session" — fractal blow-up at
L>1). This page is the constructive dual: keep the project-reducer
contractive (L<1 ≡ disciplines holding) and reduction settles at every scale.

## 2. The transducer math (Michael's recall — correct, twice over)

**Sense 1 — Hickey transducers.** `rf → rf`: a reduction reified as a
composable object that owns no stream; the driver supplies iteration. "A
tensor that holds the reductions" has this exact type — and it gives the S5
`portable_tensor` hope its mathematical form: **the artifact is a transducer
over the host's reduction loop, portable because stream-agnostic.**

**Sense 2 — tree transducers.** The composition-closure theorems: the
**linear, nondeleting fragment is closed under composition**; copying and
deletion break closure (Engelfriet's composition hierarchy — copying
transducers strictly gain power under iterated composition).

**Triangulation (3 independent lines, same partition):**

| fragment | transducer theory | substructural (s221) | measured |
|---|---|---|---|
| linear (I,B,C,D) | closed under composition | linear | NATIVE; skeleton crystallizes first |
| deleting (K) | breaks closure | affine | blend-prior fight; acquisition chaos; value-register erasure (predicted) |
| copying (S,W) | breaks closure | relevant | fan-out native, dup costs |
| unbounded (Y) | beyond formalism → iteration | recursive | NEEDS-RECURRENCE, outer loop |

**Refined prediction (new):** the s110/s216 multi-fold interference wall
should be located exactly at copy/delete elements, NOT at linear ones —
linear-fragment folds should compose cleanly. Testable refinement of the
construct path's "one open risk."

## 3. The machine

```
REDUCTION TRANSDUCER (passive optical bench, host-agnostic)
├─ chassis:  tree-of-VSM opcode tree     [BUILT s265 — frame-invariant Grams]
├─ plates:   ternary gratings (Δ on B₀)  [etch + computed-beam s149 + Exp-B]
│            → hold the LINEAR fragment (the composable transducer part)
├─ mirrors:  ternary reflections {−1,0,+1}  [recursion-mirrors s173]
│            → −1 ≡ π-shifted exposure ≡ K-erasure by destructive interference
│            → 0 absorb/gate · +1 pass · sequential per-position programs
└─ monitor:  opcode instrument           [designed s176 — algedonic channel]

HOST SUPPLIES (physics-forced division of labor)
├─ light:    attention (application/readout)
├─ collapse: sampler (regeneration)
└─ Y:        the autoregressive outer loop
```

Attachment registers: measurement attach = demonstrated (opcode tree);
executing attach = dispatch proven (FN-INDEX ✓), chaining unproven in-context
(s294–295: fails without collapse) → sequencing routes through the host tape
OR through §4's internal collapse.

**P-K-REGISTER is upstream of the design**: if models implement K by
anti-aligned value writes, the −1 mirror is biomimetic; if K is routing
near-zeros, the mirror element needs redesign (and the readout claim takes
damage). The probe is both falsifier and design gate.

## 4. Recursion completes it — the standalone machine

Recursing ordinary weights = iterating one fixed f. Recursing a **plate** =
each pass, the state illuminates the weights; only the Bragg-matched grating
diffracts; the state selects the program, the program transforms the state.
**The recursion is a fetch–decode–execute cycle:**

```
plate (ternary, superposed)      = program memory   [crystal=ISA; FN-INDEX dispatch ✓]
residual state                   = accumulator      [the light field]
mirrors, per-pass schedule       = ALU sign ops; pass index = program counter
recursion of same weights        = Y, finally native
sign() projection between passes = INTERNAL COLLAPSE (tape without tokens)
Δx < ε (WHNF)                    = halt — halting IS the semantics
```

**Three consequences:**

1. **The recursion family gets a home.** Flat models fake Y with unrolled
   depth → recursion family never binds above null (no loop to bind to).
   A real loop should give it a home → P-LOOP-BINDS (below).
2. **Ternarization between passes = an internal tape.** sign() is a
   discretizer; each pass writes a crisp state and re-illuminates from it =
   CoT internalized into the weight register (reduce → collapse →
   regenerate inside the forward loop). Rung-3b's target ("teach an internal
   collapse") becomes an architectural primitive instead of a training goal.
3. **Holography makes tiny sufficient.** Superposition ⇒ capacity is
   program-count not program-size (CAP: coherent-gain, not crosstalk decay);
   bounded weights + unbounded compute (depth from recursion) = λ smallest
   realized mechanically.

**Halt-semantics differentiator vs literature:** Universal Transformer / ACT
/ PonderNet halt on a learned confidence scalar. Ours halts on **Δx < ε ≡
normal form reached** — and handles Ω correctly for free (a true reducer
keeps Δx high on non-normalizing input; non-termination under a K-budget is
correct behavior). Deadband target Δx* ≈ 0.24 (fp-decay probe) is what makes
it trainable without collapsing the bought depth.

**Deployment modes:** transducer mode (level 3 — attached; host supplies
light/collapse/loop) · standalone mode (level 4 — own loop; recursed plates
+ mirrors + sign-collapse + Δx-halt). Same rung as the pythia-14m
seeded-scratch pair: the construct path and the recursion close into one
architecture — **the level-4 door**.

## 5. OpenMythos grounding (cloned ~/src/OpenMythos, read s299)

Recurrent-Depth Transformer: Prelude → looped RecurrentBlock (max_loop_iters)
→ Coda. **Four independent convergences on this page's derivation:**

| OpenMythos | our derivation |
|---|---|
| `loop_index_embedding` — sinusoidal loop-index in h; shared weights "functionally distinct per iteration" | **angular multiplexing of the depth axis** — the plate re-illuminated at a different reference angle per pass reads a different superposed program; the pass-indexed mirror schedule, already built |
| `LTIInjection` — h_{t+1}=A·h_t+B·e+block(h,e), **ρ(A)<1 by construction** (ZOH, A∈(0,1)) | **contractivity as topology, not loss** — the exact s222 fix (we enforced L<1 via λ_fp·Δx² and blew up; they build it in; λ emerge applied to contraction) |
| `B·e` injected every pass ("prevent drift") | **the reference beam** — constant carrier phase-locking every pass to the source; what s295 splices lacked |
| depth-wise `LoRAAdapter` — shared frozen base + tiny per-loop scales | **delta-plates on shared B₀** — construct-path constraint #1 verbatim |
| `ACTHalting` — per-position sigmoid, cumulative threshold | the learned STOP ✓ — but see caveat |

**The caveat (sharp):** ACT is a *soft* halt — it emits a **weighted sum of
hidden states across iterations** = a convex mixture over depths. The
soft/crisp dial appears on the depth axis; OpenMythos sits at the blur end
(no collapse anywhere in the loop). Theory says it hits the compounding-blur
wall.

**The three deltas verbum adds (exactly what OpenMythos lacks):**
1. **Ternary medium** (plates/ISA — continuous weights have no program
   structure);
2. **Internal collapse** (sign-projection between passes — the tape without
   tokens);
3. **Semantic halt** (Δx<ε instead of the sigmoid guess — nearly free here:
   ρ(A)<1 + constant injection ⇒ state provably converges ⇒ Δx directly
   measurable).

**Provenance/evidence grade (λ observation — DOWNGRADED s299, Michael):**
OpenMythos was **never trained** — it is a speculative reconstruction
(portfolio-grade paper synthesis, unaffiliated per its own disclaimer). It
proves *constructibility only*, not trainability. The four convergences
stand as **design convergences** (independent derivation of the same
requirements), not as behavior. Trainability evidence relocates to the
literature behind it — Universal Transformer + ACT (trained, Graves 2016 /
Dehghani 2018), looped-transformer depth extrapolation (Saunshi et al.
2025, trained), latent recurrent-depth at 3.5B (Geiping et al. 2025,
trained) — and to **our own v15 outer-recurrence run**, which is the
nearest *in-house* trained recursed-weight artifact (L=0.70 contractive at
step 1000; then the s222 collapse — both the capability and the failure
mode are OUR measurements). "A learned STOP works" is supported by ACT
literature; "OUR semantic Δx-halt works" is untested. Related in-house
signal: qwythos "fine-tunes break the HALT not the COMPILE" (0d2b857) —
halt is a separable circuit, therefore plausibly learnable/replaceable.

## 5b. Design consequences — specification by probe (s299, Michael's Q)

> "With recurrent weights, and the fact that we can probe from the inside —
> what does that mean for our model design?" The answer inverts the field's
> methodology.

**The field's blindness:** every recurrent-depth project (Geiping 3.5B,
Saunshi loops, UT/ACT) trains against loss and shows benchmark gains with
more iterations — none can say *what an iteration does*. The loop is a
black box that buys accuracy; loss is their only instrument.

**Our inversion:** verbum holds three things nobody else combines — the
top-down lambda function (ground-truth reduction traces, gated generation
= the behavioral SPEC), interior instruments (crystal Grams, family
binding, per-pass reduction traces, register decomposition = the
mechanistic oscilloscope), and the recurrent chassis requirements (§5).
Therefore: **loss is a proxy; train against the semantics directly.** The
model is done when the INSIDE is right.

```
train step → probe: Δx contracting? (L<1)
           → probe: which combinator families bound this checkpoint?
           → probe: halt fires at WHNF on reducible terms?
           → probe: halt correctly silent on Ω?
           → curriculum: teach the unbound family next
```

**Crystallization-gated curriculum:** the s221 trajectory instrument,
promoted from observer to controller — S3 of the training loop itself.
Teach K until the K family binds above null, then advance. Possible only
because we can *see* a family bind.

**Per-pass reduction trace = the loop debugger:** at pass k, which
combinator signature is the state expressing? A depth-4 term should show
~4 passes of moving crystal signature ending in WHNF-signature + halt —
checkable against the ground-truth reduction sequence we already generate.
**Architectural constraint that follows:** the recurrent state must stay
in the measurable register (the loop must not destroy the crystal-subspace
geometry the instruments read; probe-compatibility ≡ design requirement,
as RoPE-parity was for the KV splices).

**The design gates (pre-registerable now):**

| gate | criterion |
|---|---|
| **G-CONTRACT** | ρ(A)<1 by construction (topology ¬loss — s222 law); L ≲ 0.7 at every checkpoint |
| **G-BIND** | = P-LOOP-BINDS as acceptance: recursion family binds above null in the trained loop where flat models fail |
| **G-HALT** | Δx-halt fires on reducible terms at ground-truth depth; silent on Ω (probe library has Y/WHNF/fixedpoint/reduction-chain sets) |
| **G-TRACE** | per-pass signatures match ground-truth reduction order on held-out terms (wire-vs-lookup at loop level) |

**Strategic point:** a tiny construct-path model passing G-BIND + G-TRACE
is an artifact where an interior instrument shows β-reduction happening
pass-by-pass, semantically verified against ground truth, reproducible
with `uv run`. Not a claim — a measurement anyone can re-run. The answer
to dismissal is the artifact (S5 λ artifact); the closed loop (theory →
build → probe interior → confirm) is S5 λ loop completed at level 4.

**Hinges (untested, marked):** (a) the semantic Δx-halt (≠ ACT's trained
sigmoid — ours is untested); (b) sign-collapse between passes preserves
enough signal (s269 Gram-through-binarization 0.987 says plausible, not
proven). Both runnable on the v15 lineage we own; no OpenMythos code
needed.

## 6. Inherited law (s222 — non-negotiable)

β-reducing a contraction is fractal: L<1 settles all scales, L>1 compounds
all scales; recursion amplifies both directions. Design law:
- contraction **by construction** (ρ(A)<1-style) > contraction by loss;
- never churn topology while reducing (propose → hold → reduce → accept);
- deadband + saturating fp shape if a loss term is used at all (Δx*≈0.24);
- the L-meter is the acceptance gate on every fold (accept iff post-fold
  L ≲ 0.7 ∧ Exp-B ΔCE passes).

## 7. Candidates ledger (unfrozen — named, not fronts)

| candidate | claim | cost | note |
|---|---|---|---|
| **P-K-REGISTER** | K = anti-aligned value writes, not routing zeros | cheap, read-only, 535 crystal probes | falsifier of readout claim AND design gate for mirrors (first pick) |
| **P-LOOP-BINDS** | recursion family binds above null in a looped/RDT model where flat models fail | moderate — crystallization instrument exists (v15 map) | discriminates "architecturally homeless" vs "just hard" |
| **P-BRAGG** | selectivity ~√d_head; RoPE-angle sinc lobe | cheap–moderate | see attention-holographic-readout.md |
| **P-ENTROPY-COMP** | hop-2 attention entropy gates one-shot composition | cheap, fn_stack rig | see attention-holographic-readout.md |
| linear-fold closure | linear-fragment folds compose cleanly; K/S folds interfere | dear (training) | refines the s110/s216 wall via transducer theory |

Discipline: ALL queued behind the s298/s299 powered-rerun verdict and the
rung-3b backprop-compile freeze (close before opening).

## 8. Evidence ledger

- **Measured (ours):** crystal ISA universality; FN-INDEX dispatch; s292
  FRAG/CAP/XTERM; s294–295 exhaustion table; stride-fit family partition;
  contractivity L=0.70 + Δx decay; sign/magnitude plate decomposition (s173);
  Gram fidelity 0.987 through binarization (s269); Exp-B single-fold
  acceptance; qwythos halt-separability.
- **Designed (ours, unbuilt/partial):** recursion mirrors; opcode instrument
  live mode; construct-path fold protocol.
- **External (cited, IOU):** OpenMythos RDT architecture + its literature
  (Graves/Saunshi/Parcae); attention-sinks literature.
- **Open:** multi-fold composition (the wall, now sharpened); whether sign
  projection between passes preserves enough signal (relational evidence
  s269 says plausibly yes — Gram survives binarization); P-* candidates.

## Files
| File | Content |
|---|---|
| `attention-holographic-readout.md` | same-session companion: the readout physics + soft β |
| `~/src/OpenMythos/open_mythos/main.py` | RDT reference implementation (external clone, not in repo) |
| `explore/combinator-training-beta-reduction.md` | substructural table, stride-fit, construct path |
| `recursion-mirrors.md` | ternary mirrors, sequential per-position programs |
| `opcode-vsm-tree.md` + `opcode-instrument.md` | chassis + monitor |
| `computed-beam.md` | structure free, content needs GD |
| `session-222.md`, `td-oscillation-problem.md` | the inherited law |
