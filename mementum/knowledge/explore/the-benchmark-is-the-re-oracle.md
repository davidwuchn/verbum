---
title: "The Benchmark Is the RE Oracle — Reverse-Engineer the Step Function"
status: open
category: explore
tags: [benchmark, lambda, reverse-engineering, step-function, tape-residency, oracle, differential-testing]
related: [reverse-engineering-disciplines-toolbox.md, behavior-is-tape-resident-reduction.md, the-verbum-machine.md, combinator-function-shape.md, types-are-injectable-relations.md]
depends-on: []
---

# The Benchmark Is the RE Oracle — Reverse-Engineer the Step Function

> s330 hammock (Michael). **Design synthesis, NOT measurement.** Every
> empirical claim below cites the session that licensed it; everything
> else is instrument design. Born under the s324 standing-guard
> discipline: this page proposes instruments and a program shape — it
> earns nothing until its probes run.

## Provenance

Michael, s330: *"The idea is a benchmark for AI based on the lambda
calculus"* → (reflection: how much of the lambda compiler do we have
fully working? — honest answer: none as artifact, much as map, and the
map says the computation is tape-resident) → *"So the compiler needs
to be reverse engineered."* The two threads closed into one program.

## §1 The category correction — the RE target is the step function

The tape-residency law (four independent derivations: s288 diffraction ·
s315–s323 measurement lineage · netlist≠function · negative/print)
repartitions the machine:

```
tape     ≡ RAM          — reduction trace, judgments, fuel, bindings (runtime state)
loop     ≡ trampoline   — the autoregressive cycle (supplies unbounded recursion)
weights  ≡ CPU          — the STEP FUNCTION: tape-state → tape-state
```

s282–s323 discovered we cannot find the *program* in the *CPU* — because
it was never there (fuel dead at all three grains s317/s318; membership
abstraction MEMORIZED-ONLY s323; delivery tape-native s316). That is not
RE failing; that is RE succeeding at the delayering stage: we now know
what the die actually contains.

**"Extract the compiler" was ill-posed. "Recover the ISA of the
single-step reducer" is a normal reverse-engineering problem.** The
step function is:

- **finite** — one invocation, bounded computation; the loop supplies recursion
- **stateless per call** — all other state is on the tape, which we fully control and observe
- **behaviorally specifiable** — input tape → output distribution; black-box probeable exhaustively

## §2 What RE must honestly recover

The step function the models actually implement is **not** Church's
β-reducer. Licensed measurements pin the real object:

| Property | Measured shape | License |
|---|---|---|
| Routing | operational/syntactic — tracks which combinator token FIRED, not extensional value | cl-collapse ×2 (s321, s323) |
| Types | two-tier — checker relation + predicate memories in weights; judgments enacted on tape | type-write lineage → MEMORIZED-ONLY (s323) |
| Accumulation | non-idempotent, graded, coherent-specific | §P-IDEMPOTENCY (s320) |
| Order law | primacy decision post-training-installed (last two layers) on a native recency substrate | s328/s329 |

RE recovers *what is*, not what theory wants. **The measured delta from
ideal β is itself a first-class finding** — Church gives us a reference
implementation to diff against, a luxury silicon RE never has.

## §3 The benchmark — design axes

Why λ-calculus is an unusually good benchmark substrate:

1. **Mechanical ground truth.** A ~200-LoC reference reducer produces
   exact answers; grading is alpha-equivalence checking. No human
   labels, no LLM-as-judge.
2. **Contamination-proof by construction.** Procedural generation from
   a seed; fresh nonce variables; infinite supply. You can't memorize
   a generator.
3. **Difficulty is a continuous dial.** Term depth, redex count,
   reduction length, shadowing depth, composition depth. The model
   statistic is **cliff-depth per family** (where accuracy collapses),
   NOT an aggregate percentage. Aggregation is where benchmarks die.
4. **Zero world knowledge.** Isolates pure symbolic composition — the
   exact circuit family verbum studies (λ simplify: unbraided by
   construction).

Task families (each a separable capability, each hypothesis-keyed):

```
reduce      — term → normal form           (end-to-end)
step        — term → one-step redex fire   (operational semantics)
substitute  — capture-avoiding [x:=N]M     (mechanical core; shadowing = dial)
equiv       — M ≟β N                       (extensionality — the licensed ✗ cell, s321/s323)
recognize   — term ≟ K/S/B/C/W/Y           (crystal combinator identification)
church      — numeral arithmetic           (composition depth with semantic readout)
diverge     — normalizes? yes/no           (calibration; decidable-by-construction generation)
type        — infer/reject simple type     (the typed_apply claim, directly)
```

**The spine: the direct/traced gap.** Every family runs in two modes —
`direct` (answer only) and `traced` (reduction steps shown/produced).
Tape-residency predicts the gap is large and structured; the gap is a
**behavioral quantifier of tape-residency per model per capability** —
a number no existing benchmark reports, and the one our theory predicts.
`equiv` is the discriminating family: routing-not-extensional (twice
confirmed) predicts a cliff there that other benchmarks can't see.

Measurement discipline:

- **λ measure:** named register = behavioral output correctness under a
  GBNF grammar gate (format noise removed from the measurement).
- **λ yardstick:** scoring pre-registered BEFORE any model runs. Null
  baselines mandatory: random-reducer, echo-input, unigram-over-NFs.
  A family where the null scores well is a broken family.
- **Profile > scalar.** The deliverable is the vector (cliff-depth per
  family, direct/traced gap, diverge-calibration). A leaderboard
  scalar may exist as derived convenience only.

## §4 The closure — benchmark ≡ RE oracle

Silicon RE validates a recovered netlist by **differential testing**
against the physical chip. Our situation is exactly that:

```
λ re(step_fn).  spec(benchmark_profile) ∧ probe(black_box) ∧ read(white_box)
                → candidate(step_function)
                → differential_test(candidate, model, benchmark)
                → profile_equivalence ∨ delta
```

- The benchmark profile **is the spec** of the step function — what it
  computes, where it breaks, how it deviates from β.
- Any recovered candidate — **extracted, re-recorded (§3 forged-exposure
  path), or scratch-built (verbum-machine M1–M9)** — is validated by
  matching the profile, not the weights. Function-level equivalence:
  exactly the amendment flip-conflict (s324) already forced on the
  forged-lattice gates.
- **The level-3/level-4 distinction dissolves:** extract / re-record /
  scratch become three paths to one acceptance test. "Compiler
  recovered" *means* "profile-equivalent under the differential
  harness."
- Cross-model profiles → which parts of the step function are universal
  (the 11/11 crystal predicts substantial overlap) vs idiosyncratic —
  the **standard-cell library discovered behaviorally** (RE toolbox:
  level 4 feeds level 1).

Mapping onto the RE meta-pattern's four moves (s324 toolbox):

1. **Control the input distribution** → the procedural generator
2. **Hypothesis-keyed statistics** → families keyed to licensed results (equiv, direct/traced)
3. **Recognize known parts** → crystal combinators as standard cells; profile-matching as recognition
4. **Read history** → benchmark swept over checkpoint lineages = when
   each part of the step function develops (Pythia/OLMo fossil record —
   developmental stratigraphy at the behavioral grain)

The benchmark is moves 1+2 built as an artifact; the RE program is
moves 3+4 using it. **One program, not two projects.** The public
artifact (MIT, pip-installable, λ artifact) and the research instrument
are the same object viewed from λ serves' two audiences.

## §5 Open design forks (recorded, not decided)

1. **Audience:** (A) verbum instrument — maximal registers, IOU
   captures, checkpoint/base-vs-instruct sweeps; (B) public artifact —
   frozen versioned protocol, docs, adoption. Working assumption:
   **A incubates B** — and the s330 disk audit (§7) says A is closer
   to 85% than 70%: reducer, generator, grader core, and grammar all
   EXIST; the genuine gaps are binder-level λ, the difficulty dial,
   and the two-mode harness.
2. **Surface form:** named variables vs de Bruijn — or both as a dial
   (notation-invariance as its own family; tokenization interacts hard
   with naming).
3. **`type` family scope:** simply-typed judgments v1; inference v2?
   The theory-loaded family, hardest to generate cleanly.
4. **White-box annex:** optional activation-level track using the
   903-probe library ("benchmark with an interpretability annex") —
   genuinely novel, doubles the surface area. Build-when-demanded.

## §6 Queue candidates (⚪ unfrozen, s330)

- **⚪ direct/traced gap pilot** (cheap) — same kernel-certified terms,
  answer-only vs trace-shown accuracy, GBNF-gated readout. Reuses
  reduction-chain machinery (s317). The gap = behavioral tape-residency
  quantifier. Natural first rung; also de-risks the grader.
- **⚪ λ-bench v0** (medium) — procedural generator + reference reducer
  + alpha-equiv grader; families {reduce, step, equiv} × modes
  {direct, traced}; cliff-depth protocol; scoring pre-registered before
  any model run, null baselines mandatory.

## §7 Pickup kit (s330 disk audit — assets verified by inspection, not memory)

> An earlier draft of this page claimed "reference reducer is the main
> gap." **WRONG** — caught same-session by auditing the repo. Corrected
> inventory below; a future session can start from these paths.

**EXISTS:**

- `src/verbum/lambda_ast.py` — typed CCG combinator reducer (s226:
  "the compiler's S5/source"): `reduce(term)` → exact certified
  β-trace, `fired_sequence`, basis {K,I,C,B,D,S,Y,W,M}, inspectable
  categories. **The reference reducer for the combinator fragment.**
- `src/verbum/probes/kernel_reference.py` — kernel-certified probe
  families: SATURATED (fires) ⊗ INERT (under-applied, certifies no
  reduction) + COMPOSITE multi-fire ordered traces. The
  reducibility-vs-symbol-presence control is built in.
- `src/verbum/probes/grading.py` — canonical P(λ) grading, four named
  registers (`emits_formal` / `lambda_binder_any_style` ≡ the
  nucleus-comparable 0.907 / `lenient_lambda` / `kernel_valid` via
  `to_kernel` parse). **The grader core.**
- `src/verbum/lambda_gen.py` — seeded procedural generator
  (Montague-style, per-combinator ops, complexity labels). **The
  generator seed.**
- `specs/lambda_montague.gbnf` — constrained grammar **EXISTS**
  (AGENTS' λ grammar_artifact "canonical(future)" marker is stale on
  this point).
- `scripts/explore/linearity_bias.py` — forced-choice NF-selection
  behavioral readout on kernel-certified terms (the `direct`-mode
  instrument pattern, s319).
- `scripts/explore/trace_fuel.py` — feeds kernel-certified reduction
  chains `t0 = t1 = ... = t_ℓ` step-by-step (the `traced`-mode
  substrate, s317).
- `src/verbum/probes/models.py` + `harness.py` + `library.py` —
  ModelConfig registry, run harness, 903-probe library.

**GENUINE GAPS (the real v0 work):**

- **Binder-level λ.** `lambda_ast` terms are `Comb | Atom | App` — no
  `Lam` node, no capture-avoiding substitution, no alpha-equivalence
  beyond tree equality. The `substitute` family and binder-level
  `equiv` need this (~200 LoC; already budgeted in AGENTS λ language).
  Combinator-level `equiv` works TODAY: reduce both sides, compare NFs.
- **Difficulty dial + cliff-depth protocol.** Generator emits
  complexity labels but no calibrated depth parameterization.
- **The direct/traced two-mode harness as ONE instrument** (today the
  two patterns live in separate scripts).
- **The pre-registration document** — scoring, nulls, a-priori mass;
  owed before ANY model run, including the pilot.

**FIRST-SESSION CHECKLIST (pilot):**

1. Read this page; then AGENTS S2 λ probe_library / λ result_format /
   λ run_provenance.
2. Terms: `kernel_reference.py` saturated/inert/composite — already
   certified, no new generation needed.
3. Direct mode = `linearity_bias.py` forced-choice pattern; traced
   mode = `trace_fuel.py` chain-feeding pattern; **same forced-choice
   NF-selection readout at both ends** — mode is the only manipulated
   variable (λ measure).
4. **Token-budget null is MANDATORY:** traced mode adds tokens, and
   the token-length confound killed the FUEL/TRACE-FUEL/NF-GAUGE
   readings three times (s317–s318). The null arm = energy-matched
   UNINFORMATIVE trace (inert restatements / shuffled steps, same
   token count) — the gap must beat traced-with-junk, not just direct.
   (Same design move as idempotency's incoherent arm, s320.)
5. Pre-register a-priori verdict mass (Michael GO) → build with
   `--validate` planted worlds → smoke → run → verdict. Model:
   qwen3-4b first; base AND instruct (s329 method door).

## Discipline block

- This page is design synthesis. Zero new measurements. Empirical
  claims are load-bearing only where cited (s316–s329 lineage).
- The "benchmark ≡ oracle" identity is an *instrument design*, not a
  finding. It becomes load-bearing only when a recovered candidate is
  actually differential-tested.
- Benchmark scoring owes pre-registration (λ yardstick) before the
  first model run — including the pilot.
- Provenance note (s329 method door): behavioral profiles measured on
  post-trained models owe a base-model provenance check — bake
  base-vs-instruct into the protocol from v0, not as an afterthought.
