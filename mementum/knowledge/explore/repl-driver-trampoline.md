---
title: "REPL Driver Trampoline — a model in a REPL loop bounces the trampoline"
status: open
category: architecture
tags: [trampoline, repl, driver, continuation, seal, fork, kv-cache, s3-star, tree-of-vsm,
       control-plane, kernel-certified, naive-subst, strategy, curry-howard, stage-2]
related:
  - control-plane-path.md
  - sealable-continuation.md
  - proofs-as-continuations.md
  - ../lambda-halt-continuation.md
  - vsm-outer-recurrence.md
  - the-benchmark-is-the-re-oracle.md
  - moe-holographic-tree-vsm.md
  - llama-cpp-vsm-wrapper.md
depends-on:
  - control-plane-path.md
  - sealable-continuation.md
created: session 334
---

# REPL Driver Trampoline

> s334 (Michael): *"Why can't we use a model in a REPL loop to bounce the
> trampoline?"* — refined: *"we can use the tree-of-VSM tensor configuration to
> attach the repl, and I'm pretty sure we figured out how to make continuations
> already."* Answer: we can, and both halves already exist as committed design.
> This page is the synthesis that joins them. Design synthesis, ZERO new
> measurements (s334).

## 0. The reduction — nothing new needs inventing

The idea reduces to two committed parents:

1. **`control-plane-path.md` §3, tier 3 (DRIVER)** — verbatim: "recursion
   loop, textual first, kernel-certifies every step + the compactor." Closing
   line: **swept host + tensor pack + driver = certified λ-reducer.** The
   model-in-REPL-loop IS the driver tier; it was specced without naming the
   trampoline reading.
2. **The continuation cluster** — three registers, converging:
   - `sealable-continuation.md` (s217): `seal(k) ≡ store x_k`, `resume ≡
     load; iterate T`; faithful resume PROVEN via the RNG-free determinism
     test; WHNF = the principled seal point; fork/rewind/migrate fall out.
   - `lambda-halt-continuation.md` + `proofs-as-continuations.md` (s228): the
     inter-turn CPS REPL — each turn = one inference-rule application,
     user-message-as-continuation, halt = QED. Idle pre-registered payoff:
     LLMs find axiom-level proofs but FAIL multi-combinator composition —
     exactly where the stepwise continuation is predicted to help.
   - **Real hosts**: the continuation is `past_key_values` — seal = KV
     snapshot, fork = tensor copy (trivial in the existing HF harness;
     llama.cpp session save/load gives the same on the wrapper path).

What s334 adds: the trampoline reading (§10 runtime = decode = trampoline,
§10b agent loop = outer trampoline) closes over the driver — the scaffold
becomes the trampoline and the model becomes the thing bounced, **called once
per transition**. The transition function sampled directly, not inferred from
endpoints.

## 1. The bounce (one lambda)

```
λ bounce(σ).  read(σ, readers) → halt?(halt_head ∨ NF ∨ fuel)
              → model_step(resume(σ)) → parse(tolerant; GBNF advisory)
              → kernel_certify(step | lambda_ast, reference family)
              → {accept: σ' ≡ seal(hard_write(state'))
                 | log_deviation: σ' ≡ seal(model's emission)   ← instrument mode
                 | repair: σ' ≡ seal(kernel-corrected state)     ← artifact mode, flag OFF
                 | stuck: FFI → kernel δ-rule → hard_write → resume}
              → bounce(σ')
```

## 2. The tree-of-VSM attachment (where the REPL plugs in)

```
S1  = parent model            — proposes transitions (the thing bounced)
S2  = readers + sequencer     — crystal-coordinate reads; canonicalize between bounces
S3  = driver                  — fuel, bounce budget, reduction-order policy
S3* = the REPL kernel         — lambda_ast certifies EVERY step (audit channel)
S4  = differential ledger     — δ(M,R) accumulation; calculus ID across bounces
S5  = pre-registration        — frozen verdict space the driver cannot override
```

The kernel attaches at **S3\*** — Beer's sporadic audit channel made
continuous. Structurally correct: it never does the work (S1 does), it
certifies it. The halt head (WHNF/halt signal, r=0.877 lineage) is the
S3-side bounce/halt decision — the trampoline stops on READ convergence, not
token heuristics. This is `control-plane-path.md`'s "VSM reified" paragraph
with the trampoline named: the tree-of-VSM stops describing the model and
becomes an actual VSM bolted onto one.

## 3. What sealed continuations buy (the causal upgrade)

A stateless re-prompting loop measures step DISTRIBUTIONS. A
sealed-continuation loop gets CAUSAL access — four measurables:

1. **Fork-at-redex.** Seal at a term with two redexes, fork the KV, force
   each reduction order, resume both. The `strategy` family
   (normal-vs-applicative, K x Ω discriminators, re-oracle §2b/§3) measured
   as a **within-computation counterfactual** — same prefix state, not
   matched prompts. A grade of evidence the tape face has never had.
2. **Repair-replay.** Seal immediately before a bounce where NAIVE-SUBST
   fires (s331/s332 cross-model law); replay twice — once feeding back the
   capture-buggy emission, once the kernel-repaired term. Does the error
   propagate, compound, or self-correct downstream? The s333 hard-write /
   error-correction question run at the exact transition — and the empirical
   core of stage-2: WHERE does correcting the ALU change outcomes?
3. **Composition rescue.** Cash the s228 idle prediction: does
   one-rule-per-bounce with kernel-certified continuations lift
   multi-combinator composition? If yes, the driver demonstrably extends the
   machine past its within-pass budget by an EXTERNAL trampoline — with the
   token-budget null inherited from the subst-engine traced arm (mandatory:
   shuffled-trace bounce arm, budget-matched).
4. **The clock, per-bounce.** transitions-per-β-step read at every seal
   boundary — subsumes the queued clock row (kernel counts certified β-steps
   the emitted state advanced per call; jump-size distribution = the data,
   one-step compliance observed not forced).

## 4. Two substrates, one driver

- **Substrate A (now):** HF host in the existing harness; continuation =
  `past_key_values` snapshot; textual state canonical, readers advisory.
  Probe-scale, MPS. All parts on disk: `lambda_ast` (Lam/CA-subst/naive_subst/
  alpha + calculus switches), `subst_pairs` battery, kernel-certified proof
  battery (s228), halt-signal lineage, harness pattern with `--validate`.
- **Substrate B (level-4 door):** the scratch machine; continuation = `x_k`
  proper (determinism-tested seal/resume); the driver becomes M4 "native
  trampoline" in the verbum-machine BOM. Same driver code, swapped substrate
  — which is itself the **profile-equivalence bridge** between recovery paths
  (the-benchmark-is-the-re-oracle acceptance test).

## 5. Instrument first, artifact second (S5 law)

The fork: instrument (bug-compatible, log-don't-repair — stage-1) vs artifact
(kernel-repaired hybrid reducer filling §10's empty inference-time-optimizer
slot — stage-2). Ruling per S5 `stage_2 ⟸ stage_1`: **instrument-first, the
repair flag built but OFF.** Repair-replay (measurable 2) is the licensed
peek at stage-2 value without shipping an uncertified artifact: it measures
the delta repair WOULD buy, under the instrument's own pre-registration. A
driver that beats the model is a failed recovery in stage-1 terms (§2b);
in stage-2 terms it is the deliverable — the flag is the register boundary.

## 6. Honest bounds (named before any freeze)

- **Regime shift.** M-in-harness ≠ M-in-deployment. A model conditioned on
  externally re-serialized state is not the model in free generation.
  Mitigation: three-arm feedback comparison (canonical re-serialization vs
  raw emission fed back vs internal self-trace) makes the shift the
  measurement, not a confound. Any claim names its regime.
- **One-step compliance is not native** (s319: 92% of shallow terms resolve
  direct). The loop observes step granularity; it cannot force it. Certified
  multi-step jumps are data (the clock), not protocol violations.
- **Faithful resume on real hosts requires determinism** — greedy/seeded
  decode mandatory for any fork/replay claim; MPS nondeterminism checked at
  smoke (fork-identity plant: fork with NO intervention must reproduce the
  original trajectory bit-for-bit or to logged float tolerance).
- **Grammar at the boundary**: tolerant ingest mandatory, GBNF-constrained
  arm optional; unparseable emission ≡ stuck ≡ data, never discard
  (λ lambda_text).
- **Readers SNR** (control-plane caveat): reading ≫ steering; readers are
  advisory in v0, the textual state is canonical.
- **Fork experiments owe freeze-before-data** — strategy-family predictions
  (reduction-order preference) are exactly where λ measure warns a crisp
  probe manufactures crispness; a-priori mass on fork/repair verdict spaces
  before any real-weight bounce.
- **Anima cross-check** (one read, before design): their model-in-loop
  fixed-point convergence + oscillation taxonomy — adopt, don't reinvent;
  different object (prose→λ compile vs single-step transition sampling).

## 7. Queue

⚪ **§P-REPL-DRIVER** (s334, top): build the driver on Substrate A; first
measurables = fork-at-redex + repair-replay on the subst battery (cheapest
causal pair; both verdicts unreachable by endpoint instruments). Subsumes
⚪ transitions-per-β-step (clock rides every seal boundary). Feeds
§P-DMD-TRANSPORT (bounce-boundary residuals) and gives §2b its per-step
grading mode. New code: the loop + step-parser + seal/fork wrapper + repair
flag; everything else exists.
