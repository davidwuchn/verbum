---
title: "Latent Reasoning Models and the Prefill Triangle"
status: open
category: explore
tags: [latent-reasoning, prefill, registers, routing, logit-lens, counterfactual-cone, tape-interface, external-paper]
related: [the-benchmark-is-the-re-oracle.md, types-are-a-modulation-scheme.md, operator-geometry-la-toolkit.md, behavior-is-tape-resident-reduction.md]
depends-on: [the-benchmark-is-the-re-oracle.md]
---

# Latent Reasoning Models and the Prefill Triangle

> s333 capture (Michael GO "capture this to knowledge and the queue").
> Source paper: **arXiv:2604.04902v2** — Dilgren & Wiegreffe, "Are Latent
> Reasoning Models Easily Interpretable?", COLM 2026 (v2 2026-08-10, UMD).
> External read + design synthesis. **ZERO verbum measurements in this page.**
> Licensed-vs-imported markers throughout; every probe named here is ⚪
> unfrozen and owes its own pre-registration.

## §1 What the paper shows (their measurements, our compression)

Object: width-based LRMs — **Coconut** and **CODI**. The latent "reasoning
token" = final-layer hidden state fed directly back as the next input
embedding, **bypassing decode → re-embed**. GPT-2 Small + Llama-3.2-1B-Instruct,
fine-tuned on gold traces; GSM8k-Aug / PrOntoQA / ProsQA; 6 latent tokens.

1. **Necessity fails on logic tasks.** Early-stopping (inject end-of-thought
   at ℓ=0..5): LRMs almost never need ANY latent tokens for stable answers on
   PrOntoQA/ProsQA (ERMs need 47–98% of their explicit tokens). Killer
   control: multi-mode models (same weights trained no-CoT/CoT/latent on
   identical data) — the LRM advantage over no-CoT **vanishes** (their
   Table 2). The Coconut "parallel BFS in latent space" claim dies at the
   necessity gate: the win was the training regimen, not inference compute.
2. **Recoverability (GSM8k, where tokens ARE used).** Top-10 vocab projection
   (logit lens) + backtracking search: gold traces found in 65–93% of correct
   predictions vs 2–8% for length-matched random traces (their expressivity
   null), only 24–36% for incorrect predictions. **Operators almost never
   project — only operands and results.**
3. **Unsupervised extraction + verification.** Forward chaining: hypothesize
   step = top-1 integer at a latent position, enumerate arithmetic combos,
   then **verify by input counterfactual** (edit an operand in the prompt,
   check the projected result at that position moves as arithmetic predicts,
   r/3 threshold). Verified traces: majority of correct predictions, minority
   of incorrect → interpretability is itself a correctness signal.

Their own caveats: correlational (no patching of latents → answer);
gold-trace supervision may install the NL prior that makes any of this
readable; 124M–1B models only.

## §2 Ledger mapping — independent consilience on method

Consilience ≠ proof (s324 guard), but four of our disciplines appear here
independently derived:

- Their multi-mode control ≡ **λ provenance_check** (installed ≠ native; one
  controlled swap attributes a win to training vs architecture — same move as
  s329 base-vs-instruct).
- Their early-stopping ≡ **token-budget/necessity gate** (the confound that
  killed FUEL/TRACE-FUEL/NF-GAUGE ×3). Their "verify tokens are necessary
  before interpreting them" = our freeze-gate discipline as community norm.
- Their random-trace baseline ≡ **λ yardstick null** (search-power control).
- Their counterfactual verification ≡ differential testing against an
  executable semantics — the **§2b bug-compatibility direction** (δ(candidate,
  M), not δ(candidate, ideal)); "model skips steps when wrong" is an error
  fingerprint.

## §3 Our reading: the compile step is load-bearing (frame-level)

Expansion-reduce frame (§8c of the re-oracle page): thinking ≡ expansion into
context (write ≡ emit∘auto_compile, HARD — collapse to one symbol), attention
≡ the reduce (softmax(QKᵀ)V, SOFT holographic read). Coconut/CODI **delete the
compile step** — the latent token is an un-collapsed residual state used as an
input. In our register taxonomy that is not a tape write; it is a horizontal
extension of the residual-stream workspace (bounded within-pass reducer).

Read through that frame, their three findings become one finding: **the
reducer is intact; expansion-into-context only functions when writes are
compiled to symbols.**

- Finding 1: models rationally ignore a broken channel and fall back on the
  within-pass/prefill budget (coheres s319 direct 92% on shallow terms).
- Finding 2 (GSM8k dissociation): **hard writes beat soft writes at equal
  training** (+~29pt CoT>latent, training-controlled). The "decode bottleneck"
  framing of the LRM literature is backwards — discretization is what makes
  the tape a tape.
- Finding 3: soft writes work only insofar as they imitate hard writes —
  recoverable cases are the near-one-hot, decodable ones (read-entropy ≡
  fidelity, §8c). CODI+Llama smears mass over ~5000 tokens and their
  instrument strains exactly there.

The collapse does three things the latent pathway loses: **(a) error
correction** (snap to vocabulary lattice each cycle — the tape-face echo of
crystal/ternary survival-by-discretization; sign-is-the-decision, token-commit
is the tape's sign), **(b) addressability** (committed token → in-distribution
embedding → calibrated K/V pair; a raw final-layer state is OOD for the
address space), **(c) the program register** (an explicit step "3+5=8" writes
BOTH registers to tape; the latent token demonstrably carries only the value
register — the soft write drops the program, keeps the data).

Honest alternatives their data cannot exclude: under-trained (tiny fine-tuned
models) vs broken-by-construction; and register-blindness of their instrument
(see §4) cuts against reading "operators absent from projections" as
"operators absent from the latent state."

## §4 Their two instruments, precisely (for reuse)

**Substrate — the projection grid.** At each latent position: final-layer
residual (post-LN) × unembedding = logit lens; keep top-10. One instance → a
(positions × 10) token grid. Single-token concepts only; multi-token numbers
approximated by first digit-token. This grid is their entire observable.

**Backtracking (gold known).** Build operand→result DAG from the gold trace;
gate on final answer ∈ top-k at answer position; search assignments of
quantities to positions, constraint: operands precede results; branching over
multiple appearances. Dials: alternative gold traces; question numbers as free
operands (the 65%→93% dial). Null: same search, 5 random equal-length traces.
Operators never checked (they don't project) — it is a **value-register
skeleton match**.

**Forward chaining (gold unknown).** Phase 1 hypothesize: top-1 integer at
position = step result; operands from question ∪ top-k at pos−d (d=1 Coconut,
d=2 CODI) ∪ earlier top-1s; enumerate 2–3-operand combos over {+,−,×,÷};
priority-sort. Phase 2 verify: edit a question number the operand traces to,
rerun, check top-1 at the SAME position moves to the arithmetically expected
value (3 attempts, r∈{1,2,3}). Phase 3 assemble backwards from the answer;
trace verified ⟺ all steps verified.

**Epistemics ladder:** rung 1 presence-in-order (backtracking + null) → rung 2
input-covariation under intervention (forward chaining) → rung 3 causal use
downstream (NEITHER — no latent patching; a latent token can be a faithful
SHADOW of computation done elsewhere, e.g. during prefill — their §4 makes
this live). Verification failure is register-ambiguous: top-1-integer is a
crisp readout of a graded register (their r-dial is a blunt acknowledgment).

## §5 Routing extension — recover the program, not just the data (design)

Premise (licensed on our side: syntactic routing s321/s323; s206 register
scar; imported/unverified: operator-as-pathway decodability at small scale):
**the operator is not in the state, it is the shape of the read** — which
positions attended, which heads, which FFN dispatch. Their method reads the
RAM dump; the program is on the bus.

- **Phase-1 upgrade**: read operand provenance from attention edges at latent
  positions (value-weighted attention or path patching, NOT bare QK mass —
  s206). Candidate set collapses from combinatorial enumeration to observed
  addresses. This is `binding_graph_trace` pointed at their substrate.
- **Phase-1b**: decode the operator from the routing/pathway signature; train
  the decoder on the ERM sibling (every CoT step's operator visible — their
  multi-mode models are ideal), apply at latent positions.
- **Phase-2 upgrade — the register-separated 2×2 (the pre-registerable
  core)**:

  | intervene on | value register | routing register |
  |---|---|---|
  | data (5→7 in prompt) | moves (arithmetically) | **invariant** (same program) |
  | operation (+→− via text) | moves (new arithmetic) | **moves** (different pathway) |

  If it holds: program/data dissociated inside the latent channel — a direct
  test of routing-is-the-computation on their substrate. If data-edits move
  routing: the model re-plans per input, program/data not separated — a
  different machine, also informative. Op-edit arm needs matched lexical
  controls (surface text changes too).
- **Phase-3 upgrade**: dependency edges observed (does lat4 attend to lat2?)
  instead of numerically inferred. Artifact upgrades from equation list to
  **typed program graph** (nodes = results/value, edges = provenance/attention,
  labels = operators/pathway).
- **Attacks their standing weaknesses**: read-mass audit from answer position
  onto latent positions (shadow-vs-mechanism, per-instance necessity);
  mass-ratio/read-entropy per-trial prediction of verification success (§8c
  MASS-RATIO PREDICTOR — same shadowing-as-two-peaks structure as our binder
  problem).

Feasibility: Coconut/CODI code + checkpoints public; GPT-2-Small scale = MPS
probe-scale; their repo automates the ERM-sibling training.

## §6 The prefill triangle — the uninstrumented region

Prefill processes all n prompt tokens in ONE parallel pass (causal mask ⇒
mathematically identical to incremental decode; only scheduling differs).
The computation is a 2-D grid: cells (position i, layer ℓ) = residual states;
**vertical edges** = residual+MLP per column; **leftward edges at every
layer** = attention reading K/V of columns ≤ i.

```
layer L  ▢ ▢ ▢ ▢ ▢ ▢   ← every behavioral law we own was read HERE
   ...   ▢ ▢ ▢ ▢ ▢ ▢      (the last column: L-surprisal, T-axis, s329
layer 1  ▢ ▢ ▢ ▢ ▢ ▢       commit-layer sweeps — one column of the grid)
         t₁ t₂ t₃ … tₙ
```

Three structural facts:
1. Every prompt token gets a full L-layer workspace — prefill is n coupled
   within-pass reducers (a triangular systolic array), not one.
2. **The KV cache built during prefill IS the compiled tape** (§8c): at each
   layer each position's residual → (K,V). Prompt processing ≡ the
   auto_compile half of the write, for the whole prompt at once.
3. **The hop budget is L**: cross-position dereference costs one layer;
   serial depth ≤ L regardless of width. Width is cheap, depth is scarce.

This dissolves their finding 1 quantitatively: PrOntoQA/ProsQA need 3–6
is-a hops; L = 12–16 layers — the chase fits in the triangle, so latent
roll-out is redundant, not refused. Same shape as s319 (92% direct on
shallow certified terms). **Prediction: the direct-mode cliff sits where
required serial depth crosses ~L** — our cliff-depth protocol is already
built for exactly this.

**The gap named:** all our tape-face probes (idempotency, order laws,
tape-subtraction, subst-engine) manipulate prompt content and read the last
column. The interior of the triangle — where in (position, layer) space
subterm NFs appear, which interior cells the answer column reads, whether
s329's evidence-deep/decision-late structure tiles across columns — has
never been measured by this project.

## §7 What transfers to verbum (probe candidates, all unfrozen)

1. **Grid logit-lens**: vocab-project every cell (i, ℓ) for kernel-certified
   terms — does a subterm's NF surface at the subterm's closing position,
   partway up the stack? Localizes within-prefill reduction in space AND
   depth.
2. **Dependency-cone counterfactual (the sharp one — our edge over the
   paper)**: perturb one leaf of a term; diff the grid; the changed-cell set
   = the machine's dataflow cone. We own what they lacked: a certified
   reference reducer. **cone(machine) vs cone(calculus)** — both computable
   from `lambda_ast` — is a cell-resolved algorithm test, including a
   naive-subst signature (does a shadowed binder's perturbation cone leak
   into cells capture-avoiding substitution forbids? the s331/s332
   NAIVE-SUBST law becomes WATCHABLE in the grid).
3. **Per-instance necessity gate** (their §4, adopted): before interpreting
   generated-token behavior, measure how much resolved in prefill alone.
   Complements the token-budget null (was decode even needed?).
4. **Read-mass audit at the seam**: which interior cells does the answer
   column attend into — the reduce step of expansion-then-reduce, observed
   directly.
5. **DMD field extension** (hold until §P-DMD-TRANSPORT column version
   reports): the triangle transports state in TWO directions (depth,
   position); same T≈X'X⁺ machinery on the field; cross-column stationarity
   = a second independent test of one-reducer-unrolled.

## Queue rows spawned (s333)

- ⚪ **§P-PREFILL-CONE** — grid logit-lens + leaf-perturbation dependency
  cone on kernel-certified terms; cone(machine) vs cone(calculus);
  naive-subst leak signature; + per-instance necessity gate + answer-column
  read-mass audit. Register: value (grid lens) + routing (read-mass) —
  name-before-build honored in freeze.
- ⚪ **§P-ROUTING-TRACE** — the register-separated 2×2 (data-edit vs op-edit
  × value vs routing readout) + operator-from-pathway decoder trained on the
  ERM sibling; on public Coconut/CODI checkpoints or our substrate.

Both owe: freeze with a-priori mass, planted-world --validate, matched
lexical controls (op-edit arm), value-weighted attention not bare QK (s206),
shuffled-label nulls for any pathway decoder (λ yardstick).
