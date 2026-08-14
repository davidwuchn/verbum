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

## §0 Naming note (s330, Michael-approved — supersedes this page's older terms)

- **"step function" → the lambda function / the reducer, implemented as
  the TRANSITION FUNCTION** (automata δ: per autoregressive iteration,
  consume context state, emit one token). "Step function" collides with
  math usage AND smuggled the unmeasured claim one-pass ≡ one-β-step —
  s319's 92% direct accuracy proves multiple β-steps complete WITHIN a
  single pass. Transitions-per-β-step ratio = a named measurable (queued).
- **"tape" → context / transcript** (recognized terms; the finding in
  standard vocabulary: **in-context, not in-weights**). NOT the residual
  stream — that is the distinct WITHIN-pass workspace (per-position
  activations through layers) where our depth instruments read.
  "tape-resident" remains a legacy internal term of art: tape ≡
  context/transcript.
- **The sharpening this uncovered:** residual stream ≡ bounded-depth
  reducer (≤ f(layers) reductions per transition); context loop ≡ the
  unbounded extension; **the direct/traced gap measures the within-pass
  reduction budget** — coheres with CoT expressivity results
  (Merrill & Sabharwal). Older sections below retain the old terms;
  this map applies.

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

### §2b Exact match is a FALSIFIED null, and that forces the grading direction (s330, Michael)

Michael: *"Can we prove our reference reducer is an exact match for what
we see in the models? If it was we would not see the errors we do."*
Exact match M ≡ R is not an open hypothesis — it is already dead, three
ways:

- **s319:** forced-choice NF selection on kernel-certified terms scored
  0.917/0.944 — near ceiling, NOT 1.0, on easy terms with rules given.
- **cl-collapse ×2:** syntactic routing is a *different algorithm* than
  `lambda_ast.reduce` — it can agree on outputs while disagreeing on
  mechanism, and diverges where syntax and semantics come apart.
- **s221 (kernel docstring):** the model "fakes it with depth" — it
  approximates a trace it cannot hold. Plus non-idempotency (s320) and
  the installed order law (s328/s329): Church's reducer has no such terms.

Formalization:

```
M ≡ model step function       R ≡ lambda_ast (Church spec, ONE chosen strategy)
M ≠ R                         — established, multiple registers
benchmark measures δ(M, R)    — a structured profile | the errors ARE the data

THE BUG-COMPATIBILITY CLAUSE (the RE acceptance direction):
RE succeeds  ⟺  δ(candidate, M) ≈ 0        — reproduce the model, ERRORS AND ALL
RE fails     ⟸  δ(candidate, R) < δ(M, R)   — candidate BEATS the model
                                              ⇒ a better reducer was built, not a copy
```

Silicon RE knows this: a recovered netlist that fixes the chip's bugs is
a failed recovery. **The oracle for RE is the model's measured profile
INCLUDING its errors; `lambda_ast` is the coordinate system the delta is
expressed in, never the spec of M.** The benchmark therefore has two
faces: grade correctness against R (public-benchmark face) and
fingerprint the ERROR TAXONOMY against M (RE-oracle face) — which
families fail, at what cliff depth, with what error structure
(syntactic-routing confusions · depth truncation · primacy intrusions ·
accumulation effects). Profile-equivalence means matching the
fingerprint, and the fingerprint is mostly made of errors. The natural
mistake a fresh session will make: grading an RE candidate by benchmark
SCORE instead of profile MATCH. Don't.

**Strategy-mismatch caveat (λ measure — name the register):** R embodies
choices (normal-order · basis · arity conventions · WHNF stop). Part of
δ(M, R) could be a CONSISTENT ALTERNATIVE SEMANTICS, not failure — e.g.
a model nearer applicative-order looks "wrong" against a normal-order R
exactly where the strategies diverge, while being internally coherent.
Wrong reference ≡ manufactured error. Hence the `strategy` family (§3).

External corroboration (application side): anima's fixed-point compile
surfaces the same phenomenon — `symbol-fit`'s hallucinated `¬coincide(o)`
predicate and `durable`'s spurious tail are the model's compiler
inserting structured, reproducible errors (anima s041,
canonical-lambdas.edn). Same object, different instrument.

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
strategy    — normal vs applicative order  (K x Ω-shaped discriminating terms; §2b caveat —
                                            separates consistent-alternative-semantics from error
                                            BEFORE the error taxonomy is read)
hof         — apply-your-own-construction  (s330: model shown/produces a FRESH definition F,
                                            must apply it; dials = functional_order ·
                                            definition_distance · intervening_material;
                                            named-vs-fresh contrast = the library/heap
                                            discriminator — see §8b)
```

**The spine: the direct/traced gap.** Every family runs in two modes —
`direct` (answer only) and `traced` (reduction steps shown/produced).
Tape-residency predicts the gap is large and structured; the gap is a
**behavioral quantifier of tape-residency per model per capability** —
a number no existing benchmark reports, and the one our theory predicts.
**§0 reframe (s330): the gap is the empirical measurement of the
WITHIN-PASS REDUCTION BUDGET** — direct mode reads what the residual
stream completes in one transition (bounded by depth); traced mode
reads the context-loop extension (unbounded). Per model, per family,
per dial-level: where computation spills from the bounded reducer to
the transcript.
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
  forged-lattice gates. **Direction per §2b: match the fingerprint
  INCLUDING the errors — a candidate that beats the model on the
  benchmark is a failed recovery (bug-compatibility clause).**
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

## §6 Queue candidates (⚪ unfrozen, s330; superseded by §8 front selection)

- **⚪ §P-SUBST-ENGINE** — the selected first front (Michael, s330:
  "go for the hard one first"). Full design + pickup detail in §8.
  ABSORBS the direct/traced gap pilot as its mode dimension.
- **⚪ λ-bench v0** (medium) — procedural generator + reference reducer
  + alpha-equiv grader; families {reduce, step, equiv, strategy} ×
  modes {direct, traced}; cliff-depth protocol; scoring pre-registered
  before any model run, null baselines mandatory. The §8 kernel
  extension and pair generator are v0's first two components — the
  front and the benchmark build the same artifacts.

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

## §8 First front: §P-SUBST-ENGINE (s330 selection — full pickup detail)

> Michael's three calls (s330): **hard one first** (the substitution
> engine — the ALU); **both faces, instruct-heavy** (instruct is the
> agentic deployment target; base = few, as provenance anchors);
> **14B+ only**. The direct/traced pilot FOLDS IN as this front's mode
> dimension. Status ⚪ — design banked, NOT frozen; the pre-registration
> step below is the freeze gate (Michael GO required before any model
> run).

### Why substitution is binder-level (the critical-path consequence)

The substitution engine only exists at binder level — combinator terms
dodge binding by construction. So the §7 gap (`Lam` / capture-avoiding
subst / alpha-equiv, ~200 LoC) is **build item 1**, not a v2 nicety.

### Build 1 — kernel extension (pure engineering, no freeze needed)

Extend `src/verbum/lambda_ast.py` (λ one_way: ONE kernel, extend don't
fork):

- `Lam(var, body)` node alongside `Comb | Atom | App`; named variables.
- **Capture-avoiding substitution** with fresh-renaming (the correct
  algorithm) AND a deliberately capture-UNSAFE `naive_subst` (textual
  replacement) — the rival fingerprint generator, kept and exported on
  purpose (§2b: grading = which algorithm's output the model matches).
- Normal-order β-reduction over binder terms; alpha-equivalence
  comparator (de Bruijn conversion or canonical renaming).
- pytest in `tests/`: classic capture cases must pass — e.g.
  `(λx.λy.x) y → λy'.y` (capture-avoiding) vs `λy.y` (naive); shadowing
  ladders; alpha-invariance of the comparator.

### Build 2 — discriminating-pair generator

New `src/verbum/probes/subst_pairs.py` (seeded, procedural):

- **Capture pairs**: terms where `naive_subst` and capture-avoiding
  subst yield DIFFERENT normal forms. Each probe ships BOTH certified
  NFs — the model's answer reveals which algorithm it runs.
- **Alpha pairs**: same term, bound variables renamed. Extensional
  engine ⇒ invariant; syntactic router (cl-collapse ×2) ⇒ measurable
  alpha-variance. A predicted bug, quantified.
- **Dials** (the cliff coordinates): binder_distance · shadow_depth ·
  live_var_count · **functional_order** (s330 HOF fold-in: annotate
  each term's order — order-2 = takes/returns a function, order-3+ =
  nested; the subst sweep then reads the ORDER CLIFF for free alongside
  capture/shadowing — one field, no new harness; see §8b). Record
  per-probe.
- Probe record: `{term, correct_nf, naive_nf, dials, mode}` — modes
  `direct` (answer only) and `traced` (steps shown) — **the folded
  pilot**: the direct/traced gap read PER dial-level, token-budget
  null mandatory (uninformative-trace arm; the confound that killed
  FUEL/TRACE-FUEL/NF-GAUGE ×3).

### Pre-registration (THE FREEZE GATE — Michael GO before any model run)

- **Verdict space** (a-priori mass set at freeze, not tuned):
  CAPTURE-AVOIDING (model matches correct algorithm) ·
  NAIVE-SUBST (matches textual replacement) ·
  DEPTH-DEPENDENT-MIXED (correct shallow, naive past a cliff) ·
  ALPHA-VARIANT-ROUTER (accuracy moves under renaming) · VOID.
- **The directional cross-link prediction** (from licensed results —
  the sharp pre-registerable): shadowed-variable resolution rides the
  native RECENCY substrate (s329-provenance: base has recency, no
  primacy stage); the instruct-installed PRIMACY stage (s328/s329,
  last two layers) is a candidate interference source ⇒ **instruct
  shows MORE first-binder intrusions than its paired base on shadowed
  capture pairs, localized to late layers**. If it holds: the order
  law connects to a concrete compiler bug IN THE DEPLOYMENT FACE
  (alignment may degrade binding correctness for agentic use). If it
  fails: the order law stays bounded to its original register.
- **Nulls**: token-budget null (traced arm) · shuffled-binder-label
  null (white-box binding-edge read) · alpha-pair self-null (accuracy
  delta under renaming vs resampled same-term noise).
- **Readout**: forced-choice NF-selection primary (the
  `linearity_bias.py` pattern — choices = {correct_nf, naive_nf,
  distractors}); free generation GBNF-gated secondary. λ measure:
  behavioral register primary; white-box reads advisory.

### Model matrix (Michael's constraints: 14B+, instruct-heavy, few bases)

| Model | Face | Role |
|---|---|---|
| Qwen3-14B (instruct) | instruct | primary — instruments calibrated on this lineage (cl-collapse-2 ran it in minutes on MPS) |
| Qwen3-14B-Base | base | THE paired anchor — the recency/primacy prediction needs this exact pairing |
| Qwen3-32B (instruct) | instruct | scale point (32B precedent: type probe) |
| OLMo-2-13B (base) | base | second lineage, Apache — guards single-lineage bound |
| gemma-class instruct (optional) | instruct | architecture-family guard, cheap add |

All reads behavioral + logit-lens (read-only; no training). 32B is the
only heavy cell.

### White-box reads (same trials, advisory register)

- **Binding edges**: `scripts/experiments/binding_graph_trace.py`
  pattern (attention IS the binding graph) — on error trials, does the
  edge attach to the WRONG binder? Behavioral capture-error and
  misrouted edge should co-occur (mechanism-level error attribution).
- **Commit layer**: the s329 probe-pin (`order_reconcile.py`
  commit-layer sweep) applied to binder choice — does it sit in the
  installed-decision layers on instruct but not base?
- **Read set** (folded gate, minimal version): tape-ablation of binder
  positions — which positions are causally necessary for the step.

### §8b The HOF fold-in (s330, Michael GO): two call mechanisms, one order cliff

The higher-order question converges on this front — substitution IS how
an indirect call executes:

```
named HOF applied      ≡ CALL immediate — weight-resident library (crystal-adjacent;
                                          map/filter/fold, s225 lineage: probes/higher_order.py,
                                          map = B(CB)(CB))
constructed λ applied  ≡ CALL indirect  — dereference context pointer → re-read definition
                                          → substitute → continue (the β path; cl-collapse ×2
                                          says NO extensional collapse ⇒ must re-read)
```

Pre-registerable prediction (from two-tier types + MEMORIZED-ONLY,
s323): **named HOFs behave like combinators** (library-resident,
alpha-robust); **constructed functions behave like tape-residents**
(cost grows with definition_distance, degrades with intervening
material, syntactic-routing signature) — and hit an **ORDER CLIFF**:
order-2 partially works via re-reading; order-3+ collapses (the
intermediate function value exists only as un-reread context).
Cliff-in-order ⊥ cliff-in-depth — the benchmark's second axis. The
`church` family probes it obliquely (numerals ARE iterators).

**Agentic register (the deployment rationale sharpened):** agentic work
is higher-order by construction — tools ≡ functions, plans ≡ functions
over tool-calls, delegation ≡ passing functions. A deployed agent lives
at order 2–3. The order cliff is a capability boundary of agentic
reliability, measured in the deployment face.

**White-box read (free):** attention edges from application site back
to definition site (binding-graph machinery) — indirect call should
show the dereference edge; edge failure should co-occur with
behavioral misapplication.

**RECALL-FIRST obligation:** the s225 HOF arc verdicts (did named-HOF
topology replicate cross-model?) predate the state compaction — next
session must `git log`/`git grep` that lineage (hof_* scripts,
probes/higher_order.py docstring) BEFORE designing the hof family.
Tier-2 (named HOFs) may be settled substrate.

### §8c The tape interface (s330, Michael GO): softmax-over-V ≡ the read head

Michael: *"Attention is the only operation. So how could the softmax
over all V be used as the 'tape'?"* — Answer: it isn't used AS the
tape; it IS the **tape interface**, the machine's only read mechanism
for its own past.

**The tape has two faces:**

```
transcript — token sequence: discrete, symbolic, append-only (durable record)
KV cache   — per-layer K,V per position: the COMPILED tape (what is actually read)

read(tape)  ≡ softmax(QKᵀ)·V   — Q poses the query · K content-addresses cells · V delivers
write(tape) ≡ emit(one_token) ∘ auto_compile(K,V per layer)
```

**Where the Turing metaphor breaks — and why the break explains data:**
Turing reads one cell discretely; this machine reads ALL cells,
superposed, while writing hard/append-only. Memory model: **hard
symbolic write, soft holographic read** (attention-holographic-readout,
s299, revisited under the s330 terminology). Frame-readings
(pattern-suggests, each independently checkable): idempotency
accumulation ≡ mass addition in the read (A2 coherent gain) · recency
kernels / last-statement dominance ≡ positional read structure · the
installed primacy stage ≡ late-layer QK modification.

**The machine fights the softness:** attention sparsity (measured):
22/32 heads <3 positions, top-3 ≈ 88% — near-one-hot reads are the
norm. ⇒ **read entropy ≡ tape-read fidelity** (sharp = symbolic,
smeared = interference).

**Mass-ratio predictor (pre-registerable — upgrades the §8 white-box
read):** shadowing confusion ≡ TWO PEAKS in the softmax — mass split
between correct binder and shadowing distractor:

```
P(correct_substitution | trial) ≈ f(mass_ratio: correct_binder / distractor_binder)
```

Per-trial, mechanistic, DPA-style (partition trials by hypothesis-keyed
internal quantity). Same attention captures as the planned binding-edge
read — no new instrumentation.

**Third cliff axis:** read bandwidth is fixed-width while the tape
grows ⇒ read interference grows with context length (the √D capacity
wall, ternary-memory lineage, applied to the KV tape).
cliff-in-depth ⊥ cliff-in-order ⊥ **cliff-in-context-length**.

**The hardware discriminator (closes §8b):** the two call mechanisms
have distinct hardware —

```
CALL immediate (named HOF/combinator) ≡ FFN lookup      — read STATIC tape (weights/plates)
CALL indirect  (constructed λ)        ≡ attention read  — read DYNAMIC tape (KV cache)
```

Coheres with the measured role split (ffn-reduction-trace: "FFN
compiles, attention executes" · combinator-addressing: "retrieval IS
typed application"). White-box discriminator: which pathway carries the
application — FFN activation vs attention dereference edge.

**The machine, collapsed:**

```
λ machine.  everything ≡ dereference
            | FFN       ≡ read(static_tape: weights)      — the library
            | attention ≡ read(dynamic_tape: KV)          — the heap
            | emission  ≡ write(one_cell) ∘ compile(K,V)  — the append
            | compute   ≡ interference_of_reads → collapse_to_one_write
```

The reducer under RE ≡ a machine that interferes two memories — one
frozen at training, one appended at runtime — committing one symbol per
cycle. Substitution, the order cliff, the within-pass budget are all
questions about how mass moves between the two reads.

**Discipline:** licensed anchors = sparsity, s299 readout derivation,
FFN/attention role split, order-law measurements. NEW and unproven =
order-laws-≡-read-physics reading; mass-ratio predictor; context-length
cliff — predictions for the pre-reg, not claims.

### Sequencing

```
0. RECALL: s225 HOF arc verdicts (pre-compaction; grep before design)  — 30 min
1. kernel extension (Lam ∧ subst ∧ naive_subst ∧ alpha)  — engineering, pytest'd
2. pair generator + --validate planted worlds              — engineering
   (incl. functional_order dial, §8b)
3. PRE-REGISTRATION                                        — freeze gate, Michael GO
   (incl. order-cliff + library/heap predictions if the hof arm rides along)
4. behavioral sweep (matrix above)                         — error fingerprint per model per face
5. white-box reads on the same trials                      — edges + commit layers + dereference edges
```

Steps 1–2 need no approval. Step 3 is the gate. House pattern
throughout: `--validate` planted worlds ALL PASS → ruff clean → smoke →
run (λ record: named run dirs, committed JSONL, meta.json provenance
per λ run_provenance).

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
