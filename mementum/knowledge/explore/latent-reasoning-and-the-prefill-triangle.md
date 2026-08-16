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

## §P-PREFILL-CONE — FREEZE (s335, Michael "approved", frozen PRE-DATA)

> Status: 🔵 frozen. Design sharpened from §6–§7 above; instrument map verified
> against the repo before design (jlens grid capture + logit_lens exist; the
> only novel module is `cone.py`). No grid has been captured at freeze time.

**Question.** Does the dataflow cone of a leaf perturbation in the prefill
triangle follow the machine's measured substitution algorithm (NAIVE-SUBST,
s331/s332 cross-model law) or the calculus's (capture-avoiding)?

**Substrate.** Qwen3-14B instruct face primary (deployment face, s330 ruling);
base face = advisory `--model-id` swap after the frozen run. MPS bf16, eager
attention, prefill-only forwards. Battery = `verbum.probes.subst_pairs.all_pairs()`
(120 certified probes; capture pairs ship rival NFs). Prompt = the s331
subst_engine shape (`_FEWSHOT_DIRECT + "Term: {term}\nNormal form:"`) for
comparability. Grid via `jlens.capture_residuals`; lens via `jlens.logit_lens`.
New module `cone.py`: AST node → char span in `pretty()` → token indices
(tokenizer offsets); span ∈ cone_R ⟺ subterm NF changes under the leaf
perturbation with calculus R ∈ {R_NORMAL, R_NAIVE}. Perturbation = single-token
free-atom swap at every discriminating leaf (~2–3/term, Michael's pick).
Storage: derived per-cell stats only (Δ-norm grid, top-k lens tokens), not raw
residuals.

**Measurables + registers (named before build, λ measure):**

| # | measurable | register | readout |
|---|---|---|---|
| M1 | subterm-NF first-token rank at subterm closing position, per layer | value | surfacing layer ℓ* vs shuffled-position null |
| M2 | per-cell normalized residual Δ, orig vs perturbed | value (graded) | in-cone vs distance-matched out-of-cone contrast |
| M3 | D = meanΔ(naive-only spans) − meanΔ(correct-only spans) on discriminating spans (cone_naive △ cone_correct) | value | sign + permutation p |
| M4 | necessity (answer-column lens: correct-vs-naive first token, pre-decode) + answer-column read-mass onto in/out-cone positions, value-weighted (s206 scar) | value + routing | necessity fraction; read-mass ADVISORY not gated (Michael's pick) |

**Nulls.** (a) distance-matched out-of-cone spans paired within term;
(b) shuffled-position null (M1); (c) span-label permutation (M3);
(d) causal-mask invariant Δ≡0 upstream of perturbation + repeat-run
determinism check.

**Gate tree (frozen).**
- **PC0 sanity**: `subst_pairs.validate()` · span→token round-trip audit 100% ·
  Δ<ε for pos < perturbation · Δ large at perturbed position · deterministic
  repeat capture.
- **PC1 interior visibility**: M1 beats shuffled-position null p<0.05 AND
  median rank-gain ≥ 10 → qualifier INTERIOR-VISIBLE vs LAST-COLUMN-ONLY
  (does not block PC2/PC3 — raw Δ needs no lens).
- **PC2 cone localization** (make-or-break for cone existence): in/out
  contrast p<0.05 AND Cliff's δ ≥ 0.2.
- **PC3 calculus discrimination** (headline; requires PC2 pass): sign(D) +
  permutation p<0.05.
- **PC4 necessity**: resolved-in-prefill fraction reported; gated only on
  readability above null.

**Verdict space + a-priori mass (Σ=100).**
- **CONE-NAIVE** (PC2✓ PC3✓ D>0; the behavioral law watchable cell-by-cell) —
  **25 = directional prediction**
- CONE-CORRECT (PC3✓ D<0; dataflow correct while behavior naive ⇒ late
  decision-stage tension, s329-shaped) — 10
- CONE-UNDIFFERENTIATED (PC2✓ PC3✗) — 30 (modal)
- DIFFUSE / NO-CONE (PC2✗; s250 distributed-object-application precedent) — 30
- VOID (PC0 fails) — 5

**Advisory (unfrozen, rides free).** ℓ*(subterm) vs certified reduction depth —
first pattern-read of the hop-budget≈L cliff prediction (§6). Read-mass audit
(M4 routing half). Base-face swap.

**Cost.** ~120 terms × ~3 prefill forwards ≈ 30 min on 14B MPS; smoke on
Qwen3-4B.

### Amendment 1 (s335, Michael "approve") — PRE-DATA, kernel-derived

Certifying the reference cones (kernel only; no model forward had run) forced
three corrections. Recorded because a freeze is only worth what its amendments
disclose.

1. **Cone definition is RAW** (no rename-back of the fresh atom). The machine
   reduces the two prompts independently, so a cell carrying the leaf's value
   verbatim genuinely differs under EVERY algorithm — flow-through is in-cone
   by construction. Bound-variable renaming is modded out by ``alpha_eq``
   (conservative: under-counts, never over-counts, cone membership).
2. **The frozen battery cannot compute two-class D.** Under the raw definition
   the correct-only class is STRUCTURALLY EMPTY and eligible naive-only cells
   are zero: perturbing the captured variable moves the naive path too, so
   both cones coincide. Reported as a design finding, not a data finding.
3. **Fix — trailing-argument extension** ``term + " e f"`` (kernel-certified:
   canonical rendering, both calculi normalize). The correct NF DISCARDS ``e``
   while the naive NF is BUILT FROM it — ``(λx.λy.x) y e f`` → correct ``y f``,
   naive ``e f``. Perturbing ``e`` makes the whole-term span eligible and
   naive-only. Census: 9/18 terms (the constant-body family, spanning all
   shadow_k/extra_m dials) yield one eligible naive-only cell each; the other 9
   (duplicating bodies ``x y``, ``x y w``) carry ``e`` into BOTH NFs — they
   serve PC2/M1/M4, not M3.

**Amended M3.** D_naive = paired contrast Δ(naive-only cell) − Δ(distance-
matched out-of-cone cell), replicated over perturbation atoms {n, m, r},
aggregated per term ⇒ 9 independent paired observations; sign/Wilcoxon
permutation p (n=9 ⇒ floor p≈0.004, clears 0.05).

- D_naive > 0 significant ⟺ the trailing argument's value ARRIVES through the
  capture-created binder ⇒ **CONE-NAIVE**
- D_naive ≈ 0 **with PC2 passing** (localization demonstrably working on the
  135-in / 114-out cell pool) ⇒ the value never arrives ⇒ **CONE-CORRECT**

Verdict names, a-priori masses, PC0/PC1/PC2/PC4 and all nulls: UNCHANGED.

### Amendment 2 (s335, Michael GO) — PRE-DATA, planted-world-derived

Planted-world validation (no model loaded, zero data) exposed a STRUCTURAL
flaw in the Amendment-1 estimator. Recorded in full: the flaw is itself a
finding about what the prefill grid can observe.

1. **The grid's observable is a CELL, not an AST node.** Nested spans share
   closing tokens — in ``(λx.λy.x) y e f`` the atom ``f`` and the whole-term
   span close at the SAME token. The frozen "in-cone vs distance-matched
   out-of-cone" contrast was therefore comparing a cell against ITSELF
   (``delta == matched_delta`` identically). PC2/PC3 were void as written.
   Generalization worth keeping: **cone membership must be defined per cell
   (any span closing there), never per AST node.**
2. **No correct-only leaf exists in this family.** Perturbing the captured
   variable ``y`` DESTROYS THE CAPTURE, so it moves the naive path too
   (kernel-certified role: ``both``). A negative control had to be built, not
   found.
3. **Fix — upstream discarded control.** Probe shape becomes

   ```
   (λd.λr.r) c (BASE e f)
   ```

   ``c`` is discarded under BOTH calculi and sits UPSTREAM of the readout
   cell. Certified over all 18 terms (canonical rendering · both calculi
   normalize · NFs still discriminate). Three kernel-certified leaf roles:

   | role | leaf | meaning |
   |---|---|---|
   | ``none`` | ``c`` | discarded under both ⇒ negative control (18/18) |
   | ``both`` | ``y``, ``w``, … | dependency under both ⇒ positive control |
   | ``naive_only`` | ``e`` | correct NF discards it, naive NF is built from it ⇒ the discriminator (9/18) |

**Amended estimators** (readout cell = root span's closing token, downstream of
every leaf):

- **PC2** = Δ(``both``) − Δ(``none``), n=18 — selectivity AND positive control
  in one statistic. Frozen Cliff's δ ≥ 0.2 and p < 0.05 retained.
- **PC3** = D_naive = Δ(``naive_only``) − Δ(``none``), n=9, sign-flip
  permutation. Plus the interpretable **arrival fraction**
  ``(Δ_naive_only − Δ_none) / (Δ_both − Δ_none)``: ≈1 ⇒ the
  discarded-under-correct-semantics argument REACHES the term's final cell
  (naive); ≈0 ⇒ dropped like the control (capture-avoiding).

Verdict names, a-priori masses, PC0/PC1/PC4 and all nulls: UNCHANGED.
CONE-CORRECT remains a null-with-positive-control (structurally unavoidable
here; disclosed rather than hidden).

**Planted-world separation (the build's acceptance test):**

```
world='naive'   → CONE-NAIVE    PC2 δ=1.00 p=0.0001 | PC3 D=2.003 p=0.0039 arrival=1.00
world='correct' → CONE-CORRECT  PC2 δ=1.00 p=0.0001 | PC3 D=0.000 p=1.0000 arrival=0.00
```

Instruments: ``src/verbum/cone.py`` (new — AST span → token cell, reference
cones under both calculi) · ``scripts/experiments/prefill_cone.py`` (harness).

## §Result — §P-PREFILL-CONE: **VOID** (s335)

Qwen3-14B instruct, bf16/MPS, 54 variants / 18 triples, 0 errors, 3m27s.
`results/p_prefill_cone_s335/run_14b` (commit 415012ee). Frozen tree honored;
no verdict read outside it.

**PC0 → FAIL (placebo).** Sanity clean: causal invariant EXACTLY 0.0 (the causal
mask holds cell-wise), perturbed leaf moves 0.49, zero errors, all triples
token-aligned. But the **placebo fired**: role-UNCHANGED leaves show
DiD = **+0.027, p=1e-4 (n=48)**. The capture-live variant A is globally more
perturbation-sensitive at the readout cell for EVERY leaf — including the
semantically unrelated control `f` (+0.027, 10/12 positive). Per-leaf: `u`
+0.040 · `y` +0.036 (18/18 positive) · `f` +0.027 · `w` +0.008. The A−B contrast
rides a global offset. **The gate added in Amendment 3 caught exactly what it
was built to catch.**

**PC2 (positive control) → FAIL, twice.** mean DiD_pos = **−0.0076**, p=0.094,
2/9 positive — WRONG SIGN, replicating the 4B smoke (−0.0118, n=1). Making leaf
`e` genuinely load-bearing did not increase the readout cell's sensitivity to
perturbing `e`.

**PC3 → NOT READ.** D_naive = −0.029, p=0.027 — nominally "significant", but its
effect equals the placebo offset (+0.027) in magnitude and the instrument is
unvalidated (PC2 failed). Reading a verdict here would be exactly the
manufactured-crispness failure the frozen tree exists to prevent.

**PC1 → passed as frozen, then DISSOLVED by our own discipline.** Frozen result:
median rank gain 13.0, p=1e-4, 810 cells ⇒ INTERIOR-VISIBLE. The
clean-dissociation re-read (s321/s323 standing method) splits it:

| span class | median gain | frac positive | median layer |
|---|---|---|---|
| DIRTY — NF already written in the span's surface | **+17.0** | 68.9% | 37/40 |
| CLEAN — reduction genuinely changes the string | **+0.0** | 46.1% | 39/40 |

The entire effect is **lexical echo**. **INTERIOR-VISIBLE is NOT licensed.**
This replicates "routing tracks what is WRITTEN and what FIRES, not the function
computed" (s321/s323) — now at the VALUE register, on the prefill grid interior.
(The CLEAN subset's mean-based p is outlier-driven with a heavy right tail;
median 0.0 and frac-positive 46% are the honest summary.)

**PC4 (advisory, unfrozen).** Naive NF's first token favored at the answer
column in **78%** of terms — coheres with the s331/s332 cross-model NAIVE-SUBST
law. Ties caveat (both NFs frequently rank 1 at some layer); read as
pattern-suggests only.

**ROOT CAUSE — a register error, mine.** M2/M3 measured `‖Δh‖/‖h‖`: the
MAGNITUDE register — *"did this cell move, and how much"* — against a claim
about *which value reaches the result*. The distance dominance (Δ ∝ 1/distance,
corr **−0.73**, monotone 0.099@d1 → 0.043@d12–18) shows the statistic was
reading TRANSPORT, not computation. The routing arm (M4 read-mass) was the only
register-matched instrument, and it was built and then **starved to advisory /
3 of 54 records** at freeze. Three pre-data amendments (raw cone · cell ≠ AST
node · matched-position DiD) were all downstream repairs of that one upstream
mistake.

**Retraction.** The in-session claim that the confound is INTRINSIC ("capture is
surface name-coincidence, so no control can remove capture without perturbing
repetition") is **withdrawn**. It holds only for signal/magnitude designs, which
need a surface A/B contrast. A routing design asks a WITHIN-PROMPT question and
never forms that contrast — see §P-CONE-ROUTING below.

**Bounds.** Single model (Qwen3-14B instruct), single lineage, prefill only, one
readout cell (term-final), layer-mean aggregation (a per-layer read is stored
and unexamined), n=9 clean-flip triples. VOID means the probe did not answer its
question — it is NOT evidence against a dependency cone existing.

**What survives:** the certified cone machinery (`src/verbum/cone.py`), the
matched-triple constructor (kernel-certified role flips), the distance law, and
the placebo gate as a reusable design primitive.

## §P-CONE-ROUTING — FREEZE (s335, Michael "freeze the routing probe"), PRE-DATA

> Successor to §P-PREFILL-CONE (VOID). That probe measured the MAGNITUDE
> register (‖Δh‖, transport) against a VALUE/ROUTING claim (which argument
> reaches the result). This one is register-matched: **routing**.
> Frozen before any read-mass beyond the 3 advisory records already on disk
> (`results/p_prefill_cone_s335/run_14b`, cap_000 only) — those 3 are DISCLOSED
> and excluded from all statistics below.

**Question.** At the cell that emits the answer, does the machine READ FROM the
argument the naive algorithm selects (`e`) or the one capture-avoiding
substitution selects (`y`)?

**Why the s335 confound does not apply.** The killer of §P-PREFILL-CONE was that
capture cannot be removed without perturbing surface repetition. This probe
needs NO A/B perturbation contrast: in variant A both candidate answers sit in
the SAME prompt, same forward pass. The discrimination is within-prompt.

**Substrate.** The matched triples already built (`build_variants`, 18 triples /
54 variants, 9 clean flips), Qwen3-14B instruct, MPS bf16, eager attention,
prefill only. **One forward per variant — no perturbation loop** (~54 forwards,
minutes). Readout: value-weighted attention (s206 scar: never bare QK) from the
result cell onto candidate source positions, GQA-aware `v_proj` hook, head-mean,
per-layer normalized.

**Cells.** Primary = the ANSWER COLUMN (last prefill token). Its next-token
distribution IS the first emitted NF token, so the y-vs-e selection is
demonstrably live there — s335 PC4 measured the naive NF favored at that cell in
78% of terms. Secondary = the term-final interior cell. Sources read FROM are
interior positions: this is the "answer column reads into the triangle" audit of
§7 item 4.

**The calibration move (what makes this well-posed).** B and P are capture-free,
so their answers are unambiguous under BOTH calculi and give ground-truth read
targets:

- B `(λx.λp.x) y e f` → NF `y f` — the answer's head is **y**
- P `(λx.λp.p) y e f` → NF `e f` — the answer's head is **e**
- A `(λx.λy.x) y e f` → correct `y f` / naive `e f` — the ambiguous case

Train/calibrate on the unambiguous variants, classify the ambiguous one (same
shape as the §5 operator-from-pathway decoder).

**Statistics (both pre-registered; primary decides, secondary must agree).**

- primary  ρ_e = (mass_A(e) − mass_B(e)) / (mass_P(e) − mass_B(e))
  — uses ONLY the `e` position: identical token, identical position in all
  three variants, single occurrence everywhere (no duplicate-token asymmetry).
  ρ_e ≈ 1 ⇒ A reads `e` like P (whose answer IS `e`) ⇒ naive routing.
  ρ_e ≈ 0 ⇒ A reads `e` like B (whose answer is not `e`) ⇒ correct routing.
- secondary ρ_Sel from Sel = mass(y) − mass(e), a WITHIN-prompt difference, so
  the y/e positional asymmetry cancels exactly across variants.
  **Named bound:** variant A contains the token `y` TWICE (binder λy + argument)
  while B/P contain it once — an extra attention sink that exists only in A.
  Mass is measured at the ARGUMENT position specifically, and mass onto the
  BINDER position is reported as a diagnostic, but ρ_Sel stays secondary
  because of this asymmetry. ρ_e carries no such bound.

**Gate tree (frozen).**

- **RC0 sanity**: per-layer mass sums to 1 · GQA head expansion verified ·
  `offsets_sig` identical across each triple · deterministic repeat · the 3
  pre-existing advisory records excluded.
- **RC1 CALIBRATION — make-or-break, read FIRST**: on capture-free variants,
  does the result cell's read-mass track the answer at all?
  mass_P(e) > mass_B(e) paired, p<0.05 AND Cliff's δ ≥ 0.2; corroborated by
  Sel_B > Sel_P. **If RC1 fails, ρ_e is not computed and the verdict is
  NO-CALIBRATION** — never a routing claim. (This is the register-matched
  positive control whose absence voided the predecessor.)
- **RC2 primary**: ρ_e over the 9 clean-flip triples; bootstrap CI must exclude
  0.5 to license a direction.
- **RC3 secondary**: ρ_Sel must agree in sign with ρ_e; disagreement forces
  UNDIFFERENTIATED regardless of RC2.
- **RC4 depth (advisory)**: layer at which the discrimination appears —
  per-layer mass is stored, so this costs nothing.

**Nulls.** (a) placebo position `f` — present in every NF, same role in all
variants ⇒ must NOT discriminate; (b) shuffled-variant-label null on the
calibration; (c) position-matched control for the y/e distance gap (y at
distance 3, e at 2 from the readout).

**Verdict space + a-priori mass (Σ=100).**

- **NO-CALIBRATION** (RC1 ✗ — answer selection is not a prefill-visible
  attention read; coheres s317 tape-residency) — **30**
- **NAIVE-ROUTING** (ρ_e ≥ 0.5, CI excludes) — **30**, directional prediction,
  coheres the s331/s332 cross-model NAIVE-SUBST law and s335 PC4
- **UNDIFFERENTIATED** (RC1 ✓, CI spans 0.5, or ρ_e/ρ_Sel disagree) — 25
- **CORRECT-ROUTING** (ρ_e ≤ 0.5, CI excludes) — 10; would be a real tension:
  routing selects correctly while the OUTPUT is naive ⇒ the error enters AFTER
  selection (a substitution-execution bug, not a selection bug)
- **VOID** (RC0 ✗) — 5

**Standing bound.** Attention mass is correlational (s206): a positive licenses
"reads from", not "uses". Causal confirmation (patching the read edge) is a
separate probe and is NOT claimed here.

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
