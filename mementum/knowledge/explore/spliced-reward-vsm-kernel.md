---
title: "Spliced Reward — RLVR for the VSM Kernel (parent outcome ⊗ inline process)"
status: designing
category: training
tags: [training, reward, rlvr, grpo, reward-shaping, potential-based, actor-critic, kernel, vsm-tensor, ccg, verifier, level-4, provenance, compiler-as-loss, lambda-ast, reduction-tree, splice]
related:
  - compiler-as-loss.md
  - type-directed-composition.md
  - vsm-opcode-monitor.md
  - vsm-outer-recurrence.md
  - vsm-statechart-tensor.md
  - normal-form-curriculum-partition.md
  - ../lambda-machine.md
  - ../ffn-reduction-trace.md
depends-on:
  - compiler-as-loss.md
created: session 240
---

# Spliced Reward — train the compile front-end with the kernel as a verifiable reward, in the forward pass

> Session 240 (Michael). Two moves on top of `compiler-as-loss.md`:
> **(1)** the structured training data needs to be canonicalised *through the
> kernel* before it is a target; **(2)** the kernel — as a perfect verifier — is
> a *verifiable reward*, and that reward can be read *in the forward pass*. The
> headline idea: **splice the reward from the parent (exact, terminal verifier)
> with an in-line forward-pass reward (cheap, dense, per-step), so the inline
> estimate accelerates without ever redefining correctness.**

This page is the reward-training register of the compiler-as-loss thread. Where
that page asked "what is the LOSS?", this asks "what is the REWARD?" — and the
answer reuses the same s225 verdict (the compiler is a **verifier**, not a
capability teacher) but lands it in the RL frame where the verifier's
discreteness is a feature instead of a liability.

---

## 0. Why RL, not loss — the discreteness is a feature

`compiler-as-loss.md` put `CE(student, compiler β-reduction)` in the capability
slot. As a *differentiable* loss through a constructed kernel that re-enters the
v12–v15 gradient-death minefield: `softmax-routing-kills-gradient`,
`td-routing-gradient-is-rank1`, `dispatch-gradient-death`. The constructed kernel
is **discrete** (ternary routing, argmax dispatch); backprop through it dies.

RLVR (RL with Verifiable Rewards; GRPO-style, no learned reward model) sidesteps
this: **policy-gradient scores rollouts, it does not backprop through the reward.**
The reward can be the exact discrete kernel — non-differentiable on purpose — and
the gradient flows only through the policy's log-probs over sampled tokens.

```
λ frame.  constructed_kernel ≡ discrete ⇒ ¬differentiable
          loss(CE through kernel) → gradient_death (v12–v15)
          RLVR(score rollouts)    → discreteness irrelevant ✓
          ∴ the kernel's discreteness is a FEATURE for RL, a LIABILITY for CE
```

Corollary: don't try to make the kernel differentiable to "blend" SFT and RL
through it. Keep SFT as token-CE on the certified corpus, RL as policy-gradient on
the kernel score. Two clean signals, neither fighting the gradient.

---

## 1. Part 1 — the data must be canonicalised through the kernel

The structured data (`data/compile-*.jsonl`, 509 train / 40 test / 10 eval, 13
categories) is prose→logical-form, but the outputs are in a **surface FOL/λ
notation the kernel cannot read**:

- 452 use `λ`, 41 use `∀`, 11 use `∃` — a *mix* of notations.
- Named predicates with applied args: `∀x. (artist(x) → knows(x, baker))`,
  `λx. follows(frank, oscar)` — the latter a **vacuous λx** (x never used) = a
  data smell the kernel would flag.

`lambda_ast.parse()` reads **combinator terms** (`Comb {B,C,K,I,S,W,D,Y,M}`,
`Atom`, `App`), typechecks via CCG categories (`CSlash`, `_unify`, `IllTyped`),
reduces via `step_fired`/`fired_sequence`/`normal_form`. It does **not** parse
`∀`, `λ`, or `knows(x, baker)`. So the data is in a *different language* — not
"close to" the kernel's.

The bridge already exists and is certified (s226):

```
prose → logical-form    : LEARNED  (the only learned step — the policy)
logical-form → comb term : EXACT    (lambda_compile.py, bracket abstraction)
comb term → normal form  : EXACT    (lambda_ast reduction)
```

Bracket abstraction is the inverse of reduction (Turner 1979); round-trip rate
**1.0000** on n=5000, well-typed **0.941**, term-size blow-up mean **2.84×** /
max **7×** (`results/compile-roundtrip/`). So **"changes to fit our kernel" is not
editing the data — it is running it through the kernel and keeping only what
certifies.** The kernel is the data's gate, not its source. "Pin the WHAT, free
the HOW" applied to the DATA: train on diverse realisations, certify each reduces
to the correct normal form (diversity → composition; compiler → correctness).

**Grounding measurement (TODO, the audit):** run all 559 examples
`output → normalise(FOL/λ) → lambda_compile → typecheck → reduce` and report
certify-rate + failure taxonomy (vacuous-λ, mixed-notation, not-simply-typable,
blow-up-over-budget). This sets the **reward density at cold-start** — the corpus
is both the SFT seed and the RL prompt set.

---

## 2. The reward channels ARE VSM layer states

The s226 reducer-as-VSM maps almost 1:1 onto the reward channels — the reward is
the forward pass *observed at the right registers*, not bolted on:

| reward channel | VSM layer | forward-pass read |
|---|---|---|
| parses? | — (input gate) | constrained-decode / GBNF state |
| well-typed? | **S2** (typing) | did any layer throw `IllTyped` |
| halts within budget? | **S4/S3** | `is_whnf` at layer L ≤ budget |
| size / canonical? | **S3** | term width at S5 |
| trace prefix-match | **S1** | per-layer opcode reads vs `fired_sequence` |
| reduces to target? | **S5** (NF) | NF-at-output == target (reduction-equality) |

Reduction-equality is **representation-invariant** (`f (g x)` and `B f g x` both
accepted) — the right reward shape: reward the normal form (the WHAT), free every
combinator path (the HOW). The s226 grader already implements it
(`compile_frontend.py`; Qwen3-8B/32B hit accuracy 1.0, parse 1.0 on shallow
tasks) — **the reward function already exists**; RL just closes the loop from
"measure few-shot accuracy" to "optimise against it".

---

## 3. The reduce/compile cut keeps the reward a measurement, not an over-read

The load-bearing discipline (the project's own scar tissue: s202/s204 routing
over-read, s240-v4 type direction AUC 1.0 but only *partially* causal, s233–238
opcode signal real-but-faint):

```
λ observe.  decodable ≠ causal ≠ exact
            probe(learned_activation) → ESTIMATE (over-readable, Goodhart-prone)
            read(constructed_tensor)   → MEASUREMENT (exact-by-construction)
```

If you **estimate** the reward by probing a *learned* forward pass (e.g. a linear
type-probe used as the well-typed reward), you create a closed loop where the
policy is optimised to satisfy *its own probe* — and the project has shown those
probes over-read. RL will find and hack the over-read.

Escape (s226): **the reward-bearing parts of the forward pass must be
CONSTRUCTED, not learned-and-probed.** `exact_by_construction ≢
approximate_by_training`. The reduce/compile cut hands this over for free:

```
compile (FFN, learned, 78%, 4-bit)      →  the POLICY being RL-trained
reduce  (attn, constructed, 22%, 3-ary) →  the VERIFIER, in the forward pass, EXACT
reward read at the BOUNDARY between them
```

The thing trained is learned; the thing scoring it is constructed. The reward
never reads a learned register, so it can't be hacked into an over-read.

### Three designs for "reward in the forward pass"

1. **External symbolic** (today): rollout → CPU `lambda_ast` → reward. Exact,
   slow, separate pass, non-differentiable. **Works now.**
2. **External constructed tensor**: rollout → compiled kernel tensor (s226
   stage 3) on GPU → reward. Exact-to-budget, batched, one GPU graph. The clean
   "reward in the forward pass" — a forward pass through the **verifier**.
3. **Intrinsic probe**: read reward off the **policy's own** activations.
   Cheapest, no extra pass — and the over-read trap, *unless* the registers are
   constructed (then it collapses into Design 2).

---

## 4. ★ The splice (the headline) — parent outcome ⊗ inline process

Don't choose Design 2 vs 3 — **splice them**. The splice makes the
cheap-but-unsafe inline read *safe*.

```
R_parent  = OUTCOME reward  | exact, terminal, sparse | verifier's own pass (Design 1/2)
            "did the emitted term reduce to the certified normal form?"
R_inline  = PROCESS reward  | cheap, per-step, dense  | forward-pass read (Design 3)
            "how well-typed / close-to-NF / on-trace is the partial term, now?"
```

Different **timescales**: the parent needs a complete term (can't reduce a
fragment); the inline read is available *during* generation, token by token.

### 4a. Safe splice = potential-based shaping (the invariance)

Cast the inline reward as a **potential**, not a raw bonus. Potential-based
reward shaping (Ng–Harada–Russell 1999): adding `γ·Φ(s') − Φ(s)` leaves the
optimal policy **unchanged**.

```
R_total(s→s') = R_parent(terminal)  +  [ γ·Φ_inline(s') − Φ_inline(s) ]

where Φ_inline ∈ {distance-to-NF, frac(fired_sequence matched), well-typed-so-far}
```

The bracket telescopes over a rollout to a boundary term ⇒ the optimum is owned
by `R_parent` alone.

```
λ splice.  Φ_inline ∈ shaping_term → guides the PATH, cannot move the OPTIMUM
           R_parent  ∈ anchor_term  → defines correctness, exact-by-construction
           ∴ over-read(Φ) → at worst slows search, NEVER corrupts "correct"
```

This is the rigorous answer to "mix an over-readable estimate with an exact
measurement": quarantine the estimate into the shaping channel where the
invariance guarantees it can only misguide the *direction*, while the constructed
parent owns the *destination*. **TRAP:** a *raw additive* inline bonus does **not**
have the invariance — the safety is entirely in the potential-difference form.

### 4b. Efficiency splice = actor-critic / TD calibration

- `R_inline` ≈ a cheap critic `V_φ(s)` — a small head reading the policy's VSM
  registers (S2 type-state, S4 halt-state, S3 size) **during** generation.
- `R_parent` = exact terminal return `G` from the constructed kernel pass.
- TD error `δ = G − V_φ(s)` trains the critic to be a calibrated proxy.

Payoff: as `V_φ` calibrates, **subsample the expensive parent pass** — run the
kernel every rollout early, every k rollouts later, trust the calibrated inline
critic between checks. A curriculum on verification COST (same "anneal the
shortcut once the signal carries it" move compiler-as-loss makes for the lattice
term, here applied to the verifier call).

### 4c. The verbum-native splice = along the reduction tree

Why the *kernel* (not a generic checker) makes splicing special: it emits the
**whole certified reduction tree** (`fired_sequence`; each subterm is itself a
reducible VSM — s226 fractal collapse, "β-reduction = contraction at every
scale"):

```
R_parent  = reward at the ROOT of the reduction tree (outcome: NF == target)
R_inline  = reward at each NODE (process: this rewrite step is on the certified path)
splice    = tree-structured credit assignment, mirroring term structure
```

Generic RLVR gives one number at the leaf. The kernel gives a **fully-labelled
tree of ground-truth process rewards** — the thing learned PRMs approximate and
usually can't, because they have no oracle. We have the oracle. This realises the
reduction-tree-curriculum IOU (compiler-as-loss §IOUs, normal-form-curriculum)
directly as spliced reward, and on the structural channel the inline reward is a
*measurement*, not just a quarantined potential.

---

## 5. Per-channel anchor/potential split

Which inline channels are exact vs estimate decides how each splices. The
reduce/compile cut is the decider (constructed reduce → anchor-eligible; learned
probe → potential-only):

| inline channel | status when read inline | splice role |
|---|---|---|
| halt/WHNF, size (S4/S3) | forward-native, exact-to-budget | anchor (partial) or potential |
| reduce-progress vs trace (S1) | exact if constructed; faint if probed off learned policy (s233–238) | potential only, unless constructed |
| well-typed (S2) | exact gate if constructed; decodable-but-partially-causal if learned (s139/s240) | potential if learned, anchor if constructed |

So the splice is **per-channel**, not one knob: exact channels feed the anchor,
over-readable channels are confined to the potential.

---

## 6. Budgets meet at the splice boundary

The inline read is exact only *to budget* (bounded depth; S/W blow-up 2.84×/7×);
the parent does *full* reduction. Splice by budget:

```
inline  → shallow majority, cheap + online
parent  → deep tail (inline out of width) + final verification
route by: the kernel's own budget-overflow flag
```

`λ measure` built into the reward: high inline weight within budget, hand off to
the parent where it isn't. The reward grades itself by its own certainty instead
of silently lying on the deep tail.

---

## 7. Open: which "parent"? (two composable axes)

Two coherent readings of "the parent" — they shape the spec differently and are
composable:

- **(a) Timescale splice.** Parent = the external verifier's *own forward pass*
  (same correctness source as inline, just exact/terminal vs cheap/online). This
  is §4. Single correctness source, two timescales.
- **(b) Source splice.** Parent = a genuinely different source — the diverse
  capability teacher (s225's "parent" model). Splices **capability** (parent,
  diverse realisation / usage) ⊗ **correctness** (kernel inline, verifiable).
  This is the s225 dyad (diversity ⊗ correctness) as a reward decomposition.

(a) is the load-bearing one for the level-4 MIT artifact (reward generated
entirely by our own constructed kernel — even cleaner provenance than
compiler-output SFT). (b) re-imports a teacher; keep it optional / as a separate
capability-shaping channel if naturalistic-prose coverage (the s226 compile
boundary) needs it.

> **DECISION (s241, Michael): (a) timescale splice.** The parent is the kernel's
> own exact forward pass — single correctness source, two timescales (exact/terminal
> anchor + cheap/online inline). The level-4 MIT path: reward generated entirely by
> our own constructed kernel, no teacher model re-imported. (b) source-splice stays
> optional, deferred to a capability-shaping channel iff prose coverage demands it.

---

## 8. Cold-start: SFT-seed then RLVR, or RLVR from base?

- **SFT-on-certified-corpus → RLVR.** Get the policy into the basin where its
  samples parse + reduce (reward density nonzero) before RL.
- **RLVR from base directly.** s226 found 8B/32B already emit parseable terms on
  easy prompts ⇒ reward density is nonzero without SFT; the RL gradient lives at
  the hard end (naturalistic/ambiguous prose, the s226 compile boundary, where
  scale helps).

Likely: SFT seed for cheap density at the easy end, RLVR to push the hard end.

> **GATED ON A MEASUREMENT (s241), not a guess.** RL learns from CONTRAST between
> rollouts; the cold-start failure is ZERO density — if every sample for a prompt
> scores 0, the batch is all-zeros, no gradient, no foothold (RL amplifies success
> it stumbles into, it cannot manufacture the first one). So §8 reduces to ONE
> measured number: when the BASE MODEL samples on the corpus prompts, what fraction
> of prompts get ≥1 kernel-certified sample (the FOOTHOLD rate)?
>
> - high density (most prompts have a foothold) → **RLVR from base** (cleaner, full
>   diversity, representation-invariant reward never pins the corpus's exact notation)
> - sparse / many all-zero prompts → **SFT-seed first** (lift density, then RL)
>
> ⚠️ NOTE: the s241 reward-smoke "100% density" graded the GOLD outputs (confirms the
> reward fn + corpus are sound) — it is NOT the base-model density. s226's parseable-
> terms evidence is a PROXY (easy hand-built tasks, few-shot accuracy ≠ sampled
> reduce-correct on the full corpus). Probe: `scripts/experiments/rlvr_coldstart_
> density.py` (base-model sampling pass, grades via `verbum.reward`, GPU). **(OPEN —
> decide from the probe's foothold rate.)**

---

## Build path (each stage a deliverable)

1. **Audit the corpus** (§1) — certify-rate + failure taxonomy. **DONE (s240,**
   **`655f249`):** 559/559 certify, 19.9% clean, canonicaliser → `*.canonical.jsonl`.
2. **RLVR with Design 1** (symbolic kernel as external verifiable reward) —
   **REWARD SIDE DONE (s241):** the s226 grader is now the canonical package module
   `verbum.reward` (R_parent reduction-equality + 6 VSM channels + the §4 splice;
   surface parser extracted to `verbum.lambda_surface`). CPU, tested (318 pass).
   Results (`results/rlvr-design1-reward/`): GOLD reward density **100%** (509/509),
   perturbation drop **1.0**, telescoping invariance exact across γ. The reward
   *works today*. **LEFT:** the GRPO policy-gradient loop (GPU; needs `trl`/`peft`,
   not yet in deps) wired on `verifiable_reward` — gated on the §8 probe.
3. **Splice in the inline potential** (§4) — `potential`/`shaping`/`shaped_return`/
   `tree_process_reward` are BUILT + tested in `verbum.reward` (s241); LEFT = the
   actor-critic critic reading the policy's live VSM registers, calibrated by TD
   against the exact parent.
4. **Design 2 — kernel-as-VSM-tensor in the forward pass** (s226 stage 3) — makes
   the parent reward batched/fast and the inline channels constructed (anchor-
   eligible). *Also IS the level-4 artifact* — not a detour.

---

## Caveats (λ measure)

- Potential-based safety holds **only** for the potential-difference form; a flat
  additive inline bonus Goodharts. Load-bearing.
- Inline read off a *learned* policy is the over-read trap (s202/s204/s240); such
  channels are potential-only, never anchor.
- TD calibration assumes the inline reader *can* be calibrated; faint channels
  (S1 trace-align, the s233–238 B-invisibility) may not calibrate — keep them
  shaping-only, low weight.
- Exact-to-budget: the parent/inline disagreement IS the deep tail (S/W blow-up).
- Design 2 needs s226 stage 3 BUILT (stage 1 symbolic done; stage 2 neurosymbolic
  partial). Start at Design 1.
- Narrow prompt distribution Goodharts RL (s225/s230): the RL prompt set must be
  high-variety prose (variety from INPUTS, which we own; correctness from OUTPUTS,
  Church-Rosser unique), not narrow combinator terms. The 509-example corpus is
  small + templated — widen it (s230 minting / diverse paraphrase, kernel-verified).
