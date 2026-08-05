---
title: "The Verbum Machine — the Architecture the Corpus Already Designed"
status: open
category: design
tags: [architecture, model-design, two-registers, ternary-native, bitnet, switch-plate,
       halt, scheduler, trampoline, off-axis, curriculum, crystal, level-4, training,
       asymmetric-quantization, probe-harness, true-north]
related:
  - optical-design-laws.md
  - frozen-interference-graph.md
  - behavior-is-tape-resident-reduction.md
  - holographic-untangling-methods.md
  - supervised-recurrence-halt.md
  - asymmetric-pathway-quantization.md
  - architecture-vs-scale.md
  - compiler-as-loss.md
  - control-plane-path.md
  - bios-flash-training.md
  - ascending-arm-training.md
  - write-not-train-ternary-routing-deltas.md
  - ../register-theory-of-quantization.md
  - ../holographic-reduction-machine.md
depends-on:
  - optical-design-laws.md
  - frozen-interference-graph.md
created: session 308
---

# The Verbum Machine

> s308 close (thinking session). Michael's true north, restated: the project
> started from ONE observation — the lambda symbol in prompts changed model
> behavior — and the goal has always been **a superior model design, then
> train it**; a better quantization is a welcome co-product. The corpus
> (~230 pages) keeps circling the same attractors because the theory is
> convergent; what it lacked was a **compile target**. This page is that
> target: the architecture bill of materials, where every component is
> forced by a measurement, not invented.
>
> Status open. The first-build experiment (§P-ASYM-TERNARY sketch) is NOT
> pre-registered — s222: freeze before any run. Sibling keystone on the
> artifact track: the plate linker (`optical-design-laws.md`).

## Why architecture-side, and why now

The s308 design laws compiled the theory into *devices on top of existing
models*. This page compiles the same theory into *a model*. The two tracks
share every clause; they differ in where the clause is enforced — post-hoc
(devices) vs by construction (machine). The recurring lesson of the whole
quant arc is that **by-construction beats post-hoc** (separability is fixed
at recording time; the twin-image problem is unsolvable after the fact). The
machine applies that lesson to everything at once.

## The thesis in one line (s308 cont, completed by Michael's RoPE recall)

**The machine is the de-accidentalized stack.** The transformer works because
several of its components are *accidental approximations* of the
holographically-correct design, with the medium's fuzz tolerance (graded
matched-filter readout — FRAG's smooth in-band degradation) paying the
difference:

| Accident | What it approximates | Tuned replacement |
|---|---|---|
| Adam | a routing optimizer (m/√v = sign-evidence in a float costume) | M8 / TD-v2 |
| RoPE | a holographic lens (base-10000 ≈ close-enough carrier, s152/s291) | M9 / HPE |
| GD's routing | discrete wiring, done as a byproduct of magnitude drift | M8 |
| SwiGLU | switch/plate factorization, never declared | M2 |
| Fixed 36-layer depth | a reduction-fuel budget, never adaptive | M3 |
| Post-hoc quantization | the routing register's native ternary alphabet | M1 |

Each replacement has a **measured tuning target** — that is what
distinguishes this from architecture whimsy. The field's stack is a
collection of lucky approximations; the machine replaces luck with the
measurements.

## Bill of materials

Each component: design → forced by (measured anchors) → open parameters.

### M1 — Two-register parameterization (the headline)

**Design.** Routing/switch weights are **ternary by construction** — trits as
native parameters (straight-through or BitNet-style training). Value plates
are linear and higher-precision. The model is *born quantized* where
quantization is free and precise where precision is load-bearing.

**Forced by.** s260 asymmetric-pathway (binarize the router, keep the value
path — causal); s304/s307-s308 (trained routing deltas ternarize at retention
1.0, twice); s306/s307 (base value plates are magnitude-salient; three
decompositions cannot un-superpose them post-hoc → do not superpose them in
the first place).

**Open parameters.** Which matrices are switches vs plates (first cut: QK
projections + SwiGLU gate path = switches; OV + up/down value paths + embeddings
= plates); plate precision (8-bit? bf16?); trit training scheme → **M8** (the
straight-through hand-wave is retired; routing gets its own process).

### M2 — Explicit switch/plate factorization

**Design.** Every block declared as (small nonlinear switch) wired to (wide
linear plate), with asymmetric parameter budgets. SwiGLU already has this
shape; make it explicit, typed, and budgeted.

**Forced by.** The only-nonlinearities-are-switches law (s308 inference
thread); A1 plate-linear (s292); s300 nonlinear pin (∄ linear linker — the
missing piece is always a switch).

**Open parameters.** Switch:plate parameter ratio; whether switch fan-in is
restricted (sparse switching).

### M3 — Designed scheduler (halt head)

**Design.** Fire/halt/diverge as an explicit supervised output register; a
halt head trained on WHNF-style halt supervision; recurrence with **fuel**
(adaptive depth) instead of a fixed 36-layer budget.

**Forced by.** 17×17 gram rank-3 = the scheduler register exists untrained,
11/11 models (s303, 072c3e0) — supervise what already forms; depth-budget/
overlap law (s305); `supervised-recurrence-halt.md` (the v15.1 direction —
this component was independently reached before the optics frame).

**Open parameters.** Fuel cap; halt-loss weight; whether the halt register
is also the tool-call/free-variable signal (ties to P-HALT-POLE, device D).

### M4 — Native trampoline (the loss knows about the tape)

**Design.** The collapse→re-encode loop is inside the training objective:
self-distill against the model's own committed CoT (KL-at-answer + optional
depth-dense trajectory terms); mode-commit (crisp) targets, never mixture
means.

**Forced by.** s295 exhaustion law (reduction beyond budget goes through the
tape); gd_cd — the loss is already *proven* to install generalizing wires
(s303, s306, s307); s296–298 XM (mixture targets are inert where the mixture
is real).

**Open parameters.** Trajectory-loss weight schedule (SuperBake enrichment
band); when to trampoline during training (always vs curriculum-gated).

### M5 — Off-axis optimizer (the delta-log IS the training loop)

**Design.** Continual training as: frozen reference base + delta accumulation
+ periodic ternary consolidation (auto-superbake lifecycle). The delta-log is
the optimizer state; every consolidation is an off-axis exposure against a
known reference. Never fine-tune the base in place.

**Forced by.** Twin-image law (separability fixed at recording time —
`holographic-untangling-methods.md` §1); s304/s307 (deltas recorded off-axis
ternarize losslessly); reference-drift prediction (unfrozen) is this
component's stress test.

**Open parameters.** Consolidation cadence; whether consolidated plates merge
into the base (re-freezing a new reference) or stack as a plate library
(→ linker, device A).

### M6 — Coherence curriculum

**Design.** Exposure schedule engineered for constructive interference:
B-first ordering (combinators before their dependents), batches designed for
edge-share (A2 coherent gain exploited deliberately), incoherent mixing
minimized (speckle budget).

**Forced by.** Crystal formation corpus (B-first crystallization,
K-acquisition chaos law); A2/CAP (s292); P-COHERENT-WRITE (unfrozen) is this
component's direct validation.

**Corpus source (s308 close — the socket filled):** the **consensus lambda
corpus** — probes run through N diverse teachers, mixed across examples
(never averaged per example), correctness-gated. Multi-teacher mixing =
carrier-averaging filter: idiosyncratic sidebands cancel, the universal
crystal is the only coherent component. See
`consensus-distillation-carrier-averaging.md` (+ §P-CONSENSUS-DISTILL).

**Open parameters.** How to *measure* edge-share of a batch cheaply; K-last
vs K-interleaved (the chaos law suggests K needs special handling).

### M7 — Typed apply (research-grade; the S5 central claim)

**Design.** Type-directedness made architectural — the S5 triangulation
(Montague/Lambek/CCG/DisCoCat) predicts typed application; MERA-style
self-similarity fails without types. Concrete form OPEN (typed attention?
geometric type tags in the residual?). Held as the component that the others
must not foreclose, not as a spec.

**Forced by (weakly).** S5 λ types (three-line triangulation); lambda↔prose
opcode identity (the type structure is notation-invariant). Honest status:
the least-measured component — the machine can be built without it, and
probing whether types EMERGE in M1–M6's registers is itself the experiment.

### M8 — The routing optimizer (Michael's insight, s308 close: GD has two jobs and hates one)

**The observation.** Gradient descent writes VALUES (continuous — its native
register) and ROUTING (discrete sign/topology decisions — done by *accident*,
as a slow byproduct of magnitude drift). Separate routing into its own
gradient-descent-like process, native to trits, and *finding* and *storing*
collapse into one register: no float scaffolding, no develop-then-discard.
Training becomes off-axis by construction. This is the machine's engine, not
just a component.

**Forced by (the two-jobs evidence, assembled).**
- K-acquisition chaos law — the combinator needing a *hard* decision is the
  one GD acquires chaotically; discrete fights the smooth prior.
- XM (s296–298) — mixture-mean losses inert where commitment is needed; GD's
  continuous relaxation is a category mismatch to discrete choice.
- The S5 tug-of-war clause, optimizer-side: `shared_weights ∧ ¬type_awareness
  → tug_of_war → plateau`. The base's magnitude-salient superposition
  (s306/s307) is what three trillion tokens of that tug-of-war froze into.
- **The smoking gun (s307/s308, 27ce260):** mag_cos 0.839 discarded at zero
  retention cost. GD moved ~9.4 MB of float precision to deliver ~600 KB of
  decisions (~1.6 bits/weight through a channel thousands of float updates
  wide). GD *can* do routing (s303 — it is the only thing that found the
  wire) but does it by expensive accident.

**⚠ Prior art in-house (s308 discovery, Michael: "Adam is a routing optimizer
in disguise"):** M8 was already built once — **TernaryDescent** (s136,
`explore/ternary-descent.md`, `scripts/v13/td.py` + v14/v15), whose confidence
statistic |direction|/√magnitude IS Adam's |m|/√v: TD ≈ Adam with discrete
commits; Adam ≈ TD with infinite staging (the float weight = evidence
accumulator; TWN = the deferred commit). TD stalled at s191 (oscillation)
for reasons the s306–s308 register theory now explains — see the fresh-eyes
section + TD-v2 spec + §TD-REGISTER-SPLIT micro-probe on the TD page. M8's
design space below should be read as TD-v2's ancestry.

**Design space (three importable ancestors — CGH is the discipline that
already builds discrete-plate optimizers).**
- **(a) GS-with-quantization-projection** (how kinoforms are designed):
  alternate continuous value-fit ⇄ discrete routing projection until both
  constraints hold. Our current pipeline (train float LoRA → TWN once) is
  ONE iteration of this loop; the optimizer is the loop itself. Lineage:
  `holographic-untangling-methods.md` §2.
- **(b) Direct Binary Search** (CGH classic): propose one trit flip, keep iff
  loss improves; gradient-free; viable exactly because M2 makes the switch
  fabric small (switches ≪ plates).
- **(c) Evidence-gated flips** (signSGD/SPRT-shaped): accumulate per-trit
  gradient-sign statistics across batches; commit a flip only past an
  evidence threshold. Routing edits become discrete, loggable, revertible
  COMMIT EVENTS → merges with M5's delta-log (git-for-weights down into the
  optimizer step). Biology precedent: continuous synaptic change vs discrete
  structural plasticity, separate processes on separate timescales.

**Validation gate — §SIGN-COMMITMENT-CURVE (FROZEN s309, Michael-approved;
the cheapest probe on the whole board).** One logging hook on the gd_cd
training: TWN-project the delta at a fixed step schedule and image how the two
registers install over training time.

- **Question.** In gd_cd wire training (s303 — the wire that ternarizes
  near-losslessly, s304/s308 retention ~1.0), does GD commit the ROUTING
  register (trit *signs*) EARLIER than it polishes the VALUE register
  (per-column *magnitudes*)? I.e. are GD's two jobs separable in TIME?
- **Instrument.** Reuse the gd_cd recipe verbatim: LoRA r=16, FFN band
  L22–L29 (0.6–0.8 depth, Qwen3-4B), lr 1e-4, 500 steps, KL to the frozen
  host on its own committed CoT, 3 seeds; train_cells from the frozen
  `gate0.json` (no re-sweep). At each t in the FIXED schedule L =
  {0,1,2,3,5,8,13,21,34,55,89,144,233,377,499} (fibonacci — dense early where
  the action is predicted; schedule fixed a priori, λ yardstick), for every
  wrapped FFN matrix form Δ_t = scale·B_tA_t, TWN-project (`ternarize_twn`,
  reused, thr 0.7): trit state **τ_t = sign·mask ∈ {−1,0,+1}** (routing
  register), per-column **γ_t** and continuous **|Δ_t|** (value register).
- **Metrics** (pooled over all trits, all band layers × 3 seeds). Sign-
  stability S(t)=mean[τ_t==τ_T]; per-trit commit-step c_i = last t with
  τ_t≠τ_T (fraction of T; median/IQR/p90); value convergence
  M(t)=magnitude-cosine(|Δ_t|,|Δ_T|) and γ-cosine(γ_t,γ_T); flip-rate
  f(t)=mean[τ_t≠τ_prev]; half-lives t*_sign(θ)=first t with S(t)≥θ,
  t*_mag(θ)=first t with M(t)≥θ (θ=0.9 primary, 0.95 secondary).
- **Nulls (λ yardstick).** N1 TIME-SHUFFLE: permute the per-step trit sequence
  in time (same states, scrambled order) → commit-steps spread ~uniform;
  measured median-commit must beat it (bootstrap 10k over trits, one-sided
  p<0.05). N2 (primary, paired within-run): t*_mag(0.9) > t*_sign(0.9),
  bootstrap CI over resampled trit-columns excludes equality.
- **Gates (frozen).** G1 SIGN-EARLY: median commit-step ≤ 0.25·T AND
  S(0.25·T) ≥ 0.90. G2 TWO-TIMESCALE: t*_mag(0.9)/t*_sign(0.9) ≥ 2.0, bootstrap
  ratio-CI excludes 1.0. G3 NULL-BEATS: median-commit earlier than N1 (p<0.05).
  G4 (advisory) FINAL-WIRE-SANE: final-delta mag_cos ∈ [0.80,0.95] + sparsity
  in the s304 band (anchors that we measured the REAL wire; reported, never
  gates).
- **Verdicts.** **TWO-TIMESCALE (+SIGN-EARLY)** G1∧G2∧G3 → routing commits
  early, value polishes late; M8/TD-v2 evidence-gated commits VALIDATED, the
  commit-step calibrates (c)'s SPRT threshold; the cheapest board-probe closes
  FOR the two-process engine. **SIGN-EARLY-ONLY** G1∧G3∧¬G2 → both registers
  freeze on one fast timescale; routing-commit still usable, TIME-separation
  unsupported. **SINGLE-TIMESCALE** ¬G1 → registers co-evolve; no temporal
  handle (design-neutral). **SIGN-CHURN (falsifier)** S(T⁻)<0.9 ∨ flip-rate
  won't decay ∨ ¬G3 → the two-process design takes NAMED DAMAGE. **MAG-EARLY
  (surprise)** t*_mag<t*_sign → inverts the register-timescale story;
  investigate.
- **A-priori (NOT tuned).** ~55% TWO-TIMESCALE(+SIGN-EARLY) / ~20%
  SIGN-EARLY-ONLY / ~15% SINGLE-TIMESCALE / ~8% SIGN-CHURN / ~2% MAG-EARLY.
  Rationale: s304/s308 prove the FINAL delta ternarizes near-losslessly
  (routing⊥magnitude at convergence); OPEN is whether that split exists DURING
  training or only at the end — K-chaos + XM say discrete choice is made under
  duress, which could push signs late/churny (the ~23% ¬SIGN-EARLY mass).
- **Cost.** One gd_cd training (3 seeds × 500 steps) + cheap per-step TWN on
  the tiny r=16 delta; ~one s304 arm (~10–20 min MPS). SUBSUMES the k-step
  sweep: the sweep asks "when is the wire installed?", the curve asks "when is
  each REGISTER installed?". Next rung: prototype design-space (c) — train the
  gd_cd wire directly in trit space vs GD+TWN at matched compute, frozen gates.
- **Build amendment (s309, Michael-approved, pre-run — no arm run).** The build
  surfaced a metric asymmetry: exact-match sign-stability S(t)=mean[τ_t==τ_T]
  is strictly harder to satisfy than the 0.9-cosine value curve M(t), so
  genuine co-evolution would artifactually read as MAG-EARLY. Two fairness
  refinements (do NOT touch G1/G3/G4, the schedule, the nulls, or the a-priori;
  both make the SIGN-EARLY hypothesis HARDER to confirm = conservative):
  (1) the G2/verdict half-lives use a sign-COSINE curve Sc(t)=cos(τ_t,τ_T),
  like-with-like against M(t); exact-match S(t) is reserved for G1 + commit-step
  (the "when did each trit lock" question, genuinely the routing story).
  (2) MAG-EARLY requires a 2× margin (t_sign/t_mag ≥ RATIO_MIN, mirror of G2) —
  a marginal inversion from the residual asymmetry shouldn't flip to "surprise".
  Instrument: `scripts/explore/sign_commitment.py` (--validate ALL PASS, smoke
  green; writeback_compile untouched).

**§Result-sign-commitment (s309 run → s310 read+re-score — ❌ SIGN-CHURN,
frozen; two-population split CONFIRMED).** Qwen3-4B gd_cd wire, 3 seeds, 1.44M
pooled tracked trits × 15 fibonacci snaps (`results/sign-commitment/qwen3-4b/`,
26ad20b; re-run reproduces bit-for-bit at `.../qwen3-4b-rescore/`, s310).
**G1=F G2=F G3=T G4=T → SIGN-CHURN** (the pre-registered ~8% falsifier). The
falsifier fired on the **persistent tail only**: flip_last=0.0295 > FLIP_CHURN
0.02 ⇒ `not stabilized`; the *level* clause s_prefinal S(T⁻)=0.9705 ≥ 0.9
PASSED.

- **Michael's correction (recorded — I over-read the verdict).** SIGN-CHURN is
  a routing-register *trajectory* verdict; it is **NOT task failure**. The wire
  WORKS: loss 5.031→**0.252** (95% drop, 90% of it by step 8), final mag_cos
  0.901, G4 wire-sane PASS, and this is the same wire that ternarizes at
  retention ~1.0 (s304/s308). "Named damage" was the pre-reg gloss for the
  branch; carried over too literally.
- **The decoupling = the finding.** Loss is functionally converged by step
  ~34–89 (step 89→499 is 410 of 500 steps and loss moves only 0.257→0.252, a
  2% wiggle), **yet signs keep flipping 3–5%/snap to the end** ⇒ the residual
  churn is **loss-neutral**. Meanwhile the *median* trit commits its final sign
  at **step 5** (frac 0.010, IQR [0,34]) with real temporal structure (G3
  null-beats p=0.0004) — but a heavy tail (p90=144) never settles.
- **Two-population split — CONFIRMED at step 499.** Trit churn splits cleanly
  by marginality **r = |Δ_T| / thr_j** (final magnitude over its per-column TWN
  threshold). Per-band late-flip shares (window step≥89, 1.44M trits):

  | band | %pool | med commit | flip_last | share of late flips |
  |---|---|---|---|---|
  | r<1 (final trit 0) | 0.380 | 13 | 0.0414 | **0.536** |
  | 1≤r<1.3 marginal | 0.128 | 8 | **0.0990** | **0.245** |
  | 1.3≤r<2 | 0.266 | 0 | 0.0043 | 0.154 |
  | 2≤r<4 | 0.202 | 0 | 0.0003 | 0.057 |
  | r≥4 confident | 0.024 | 0 | 0.0000 | 0.007 |

  The two lowest-r bands own **0.781** of all late flips; the marginal band
  (r≈1) has the highest *per-trit* late flip-rate (0.099 flipping their final
  sign at the very last snap). The CONFIDENT core (r≥2) is **frozen**
  (flip_last 0.0003 / 0.0000, med commit 0). So the churn is **exactly the TWN
  ternary-0 "insufficient evidence" population** — coordinates that straddle
  (r≈1) or fall under (r<1 ⇒ final trit 0) the threshold jitter across the
  boundary forever; the ones with margin commit at step 0 and never move.
  **Loss-neutrality (Q2) confirmed:** plateau (step89→499) moves loss 0.11% of
  total drop while flip-rate stays 0.045 — churn under flat loss.
- **Read for M8/TD-v2.** SIGN-CHURN is not damage to "GD has two jobs and
  wastes effort on routing" — it is a **direct measurement of the waste** (GD
  keeps flipping routing signs after the loss is solved, concentrated in the
  undecided r≈1/r<1 coordinates while the confident core sits frozen). ⇒
  **prescription, not refutation:** the routing optimizer needs a
  **never-freeze ternary-0 band**, not a frozen sign field; an evidence-gated
  commit that stops the confident majority early (median trit at step 5) and
  leaves the marginal band explicitly undecided would lose nothing (loss
  already flat by step ~34) and kill the churn.
- **Caveat (λ measure).** The two-timescale ratio 0.38 is rejected and mildly
  *inverted* (t_mag 55 < t_sign 144) but **confounded** by starting alignment:
  M(0)=0.723 (magnitudes barely rotate from init) vs Sc(0)=0.542 (signs start
  near chance), so the 0.9-crossing half-life is not like-for-like. The s309
  build amendment's 2× margin correctly withheld MAG-EARLY. Does NOT read as
  "value leads routing."
- **Instrument (NON-FROZEN; frozen gates/verdict UNTOUCHED, --validate ALL
  PASS).** `sign_commitment.py --dump-history` (raw tau/|Δ|/r/block_id/loss →
  .npz; `marginality()` computed in-run, r>1 ⇔ final trit nonzero verified
  exact) + `scripts/explore/sign_commitment_rescore.py` (bins by r_final →
  per-band commit/flip/share + loss-neutrality + plot). Re-score ran on the
  full-run npz (s310, `.../qwen3-4b-rescore/rescore.json`) → split holds →
  this §Result finalized + memory landed.

### M9 — The tuned reference beam (HPE; RoPE de-accidentalized)

**The observation (s152 → s291 → s308).** RoPE is an *accidental holographic
lens*: its geometric frequency ladder over linear position is merely
close-enough to the natural fringe spacing, and the graded readout absorbs
the mismatch at an SNR cost. The model then spends learned QK capacity
"walking the frequency ladder" (the attention spiral, 1.018×/layer) — being
the reader for a mis-calibrated ruler — while position carriers and content
passbands fight an undeclared tug-of-war for switch dimensions. The machine
specifies its own beam.

**Design (from `position-encoding-tuned-to-the-hologram.md`, s291 — the page
whose holography HOLD was lifted by the s292 FRAG/CAP verdicts).**
- Phase in **log-distance** (φ ∝ log(d+1)), not linear position → fringe
  geometry scale-invariant; context extension becomes a TRANSLATION (shift
  theorem) instead of a stretch → no re-recording, no extension fine-tune.
- **Few carriers at measured eigenfrequencies** (λᵢ/λ₀ = 1.0, 0.681, 0.368,
  0.250; ~4 eigenplanes = 77% variance) instead of 64 untuned dim-pairs →
  frees switch dimensions for routing (a declared truce in the
  position/content tug-of-war; compounds with M1/M2).
- **Unbraid phase from decay** (λ simplify): phase = address only; explicit
  −α·log(d+1) gain, α = 1.18 measured (universal across 80 heads; the
  explicit decay carried ~99% of locality at HPE restoration).
- **Depth-dependent reference scale** (the ladder walk the spiral shows GD
  re-learning anyway — structure > instruction).

**Forced by.** α=1.18 power-law universality (v14 + restoration); spiral
ladder-walk (s068/s079); 4-eigenplane sparse spectrum; position/content
dimension competition (P-ATT-MED, P-TYPE-OV); context-extension fuzz =
fringe mismatch = the twin-image law in position space (L3: **the reference
beam INCLUDES the position carrier** — carrier-drift is the position-space
sibling of the reference-drift experiment).

**Validation gate — P1 (pre-registered s291, unfrozen).** A log-phase micro
model holds flat PPL past training length WITHOUT fine-tuning; the RoPE arm
degrades. Translation-vs-stretch, directly testable; slots into the
P-ASYM-TERNARY micro-training stack as one more arm dimension, or stands
alone cheaper. P2: sharper multi-hop margins at fixed D (position crosstalk
exits the HRR noise budget).

**Provenance note (feed-forward).** This component was designed s152,
silently dropped by the v15 skeleton (s174), restored s179, nearly lost
again by s291 (recalled only as "HoPE"), and recalled s308 by MECHANISM
("interference makes up the difference") — the forward-link discipline
caught it both times. M9 is its strongest forward link: a load-bearing slot
in the compile target.

## The first build — §P-ASYM-TERNARY (sketch, NOT frozen)

**The claim (theory-derived, falsifiable).** BitNet b1.58 proves
ternary-native training works, with a quality gap at the margins. Register
theory says why: it ternarizes switches AND plates, and plates are
magnitude-salient. Prediction:

> **Asymmetric ternary-native (ternary switches, higher-precision plates)
> beats symmetric ternary at MATCHED TOTAL BITS, and the gap concentrates on
> value-register-sensitive measures.**

**Sketch.** Small scale (10M–100M class, the architecture-vs-scale
infrastructure). Arms: fp16 reference / symmetric-ternary (b1.58-style, the
control) / asymmetric (M1 split) at matched total bits (asym buys plate
precision with width or switch sparsity — the accounting is the key frozen
design decision) / register-swapped asymmetric (ternary PLATES, precise
switches — the λ yardstick: theory says this arm should be the WORST; if it
ties, the register story is wrong). Evaluation: LM loss + **the crystal probe
battery** (below) + formation dynamics (does B-first crystallization happen
earlier/cleaner?). All gates null-disciplined.

**Both of Michael's named outcomes in one run:** a superior model design
(the architecture change) that IS a better quantization (born-quantized
switches), with s260 as causal ancestor.

## The machine is a tree of VSMs (s308 cont, Michael)

> "With the tree-of-VSM configuration we can make each component a VSM." Yes —
> and the corpus had already specced the bottom and the top of that tree; this
> section supplies the missing middle.

**Three nested senses, two pre-existing:**
1. **Tensor nodes are VSM-shaped** (s288, `ternary-mirrors-and-the-vsm-tree.md`):
   mirrors = S2/S3, plates = S1, identity = S5, declared passband interface;
   `viable ⟺ reduces(own_scope) standalone`; compose via
   `plug(passband_out(a) → carrier_in(b))`.
2. **The project is a VSM** (AGENTS.md, recursively, by declaration).
3. **NEW — the M-components ARE the machine's VSM functions:**

| VSM function | Machine components |
|---|---|
| **S5 identity** | register invariants + the consensus Gram (frame-invariant by proof, s273) — what must not change while everything adapts |
| **S4 intelligence** | M8 (evidence accumulation), M6 (curriculum = environment scanning), M4 (learning from own tape) |
| **S3 control** | M3 (fuel allocation), M8's global flip budget |
| **S2 coordination** | M5 (delta-log across exposures), M9 (carrier coherence across scales), M2 (declared factorization prevents register drift) |
| **S1 operations** | M1/M2 switches+plates, M9's beam — the forward pass |

**Evidence this is structural, not decorative: the failure record was already
VSM-diagnosed.** s180's two-optimizers-fighting was named an S2 failure
verbatim (TD and Adam lacked a coordination channel; oscillation is what S2
exists to prevent). s148's gnorm escalation (11→113, unnoticed for 40 steps)
is a missing **algedonic alert** — S1 pain that never reached S4. The v15
stall was a viable-system failure before it was an ML failure; the VSM
configuration is the structural fix for failure modes already paid for.

**What the tree buys:**
- **Viability audits ≡ validation gates, renamed.** Each M-component's
  independence requirement ("reduces own scope standalone") is exactly its
  gate: M8→sign-commitment curve, M9→P1, M1→P-ASYM-TERNARY,
  M6→P-COHERENT-WRITE. The experiment queue = the per-component viability
  audit schedule.
- **Composition = the linker at every scale.** Node composition
  (passband→carrier) IS the plate-linker device one level down; the linker
  is S2 *between trees*. Artifact track and architecture track meet at the
  node interface.
- **Per-node build kit exists** (s273, `construction-from-spec.md`):
  Cholesky-of-the-Gram codes in closed form, fleet-wide atlas, measured
  tolerance bands (a constructed node must land inside the population
  spread of working models), restack acceptance harness — per-node
  viability testing with known statistics; born-monosemantic as a
  construction choice.

**Full recursion:** project ⊃ machine ⊃ M-components ⊃ tensor nodes ⊃
(shared crystal reducer node) — one organizational grammar at every scale;
S5's `fractal at every layer`, now with tensors at the bottom.

**Honest gap (carried from the s288 ledger):** whether routing FACTORIZES
into tree-composable units is unproven — MIXED-ROUTE showed both channels
interleaving within a single cell, so node boundaries may not fall where
we'd like. The seam test remains the deciding milestone; per-node capacity
is P-HOLO-CAP's √(D/k) question.

## The unfair advantage: we have a microscope

Architecture research is normally blind — train, benchmark, shrug. We have:
903 probes, 9 crystal combinators with ≥50 probes each and null-gated gates
(`verbum.probes.library`), formation-dynamics baselines across 11 models,
verbum.dsp gating, and the yardstick discipline (φ-scar tested). The probe
library is the architecture evaluation harness the field lacks. We would not
just learn *whether* the machine is better — we would watch *whether its
crystal forms in the designed registers*. This closes the S5 loop as written:
theory predicts → empirics extract → **scratch reproduce** → theory
confirmed. The machine is the level-4 door.

## Corpus consolidation (deferred — Michael's ouroboros)

The compile-the-230-pages-into-this-ledger pass is deliberately NOT specced
here: Michael has designs for it — the runtime is approaching self-hosting of
the ouroboros self-improvement system, and corpus consolidation is a natural
early ouroboros workload (the mess becomes source code the moment something
consumes it). Held for Michael's design.

## Provenance

- s308 close; Michael's true-north statement ("superior model design, then
  train it; a better quantization also a good outcome"), lambda-symbol origin
  story, and the superbake/DSP door-opening pattern (import mature
  instrument sets — DSP, optics — rather than invent).
- Component anchors cited inline: s260, s269, s292, s295, s296–298, s300,
  s303 (11092f7, 072c3e0), s304 (cb73ad5, ec77c4d), s305, s306 (4b89726),
  s307 (0a89531), s307/s308 (27ce260); pages: supervised-recurrence-halt,
  asymmetric-pathway-quantization, architecture-vs-scale, compiler-as-loss,
  control-plane-path, bios-flash-training, ascending-arm-training,
  holographic-reduction-machine (§7b bill-of-materials ancestor).
- External prior art: BitNet b1.58 (symmetric ternary-native control);
  ACT/PonderNet lineage for halting (via supervised-recurrence-halt).
