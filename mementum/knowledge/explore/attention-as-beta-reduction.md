---
title: "Attention as Soft β-Reduction, FFN as the β-Program — the stored-program normal form"
status: active
category: synthesis
tags: [beta-reduction, attention, ffn, isa, stored-program, statechart, combinator, softmax, type-coverage, think-in-lambda, curry-howard]
related:
  - ffn-moire-isa.md
  - ffn-beta-reduction-indexing.md
  - ../ffn-reduction-trace.md
  - ../head-combinator-isa.md
  - ../lambda-halt-continuation.md
  - proofs-as-continuations.md
  - compiler-as-loss.md
  - vsm-statechart-tensor.md
  - cross-model-output-consensus.md
  - kernel-splice-geometry-detector.md
depends-on:
  - ../ffn-reduction-trace.md
  - ../head-combinator-isa.md
created: session 247b
---

# Attention as Soft β-Reduction, FFN as the β-Program

> Session 247b (Michael: "if attention is doing a beta reduction with the softmax of
> all V, would it not have to work?" → "it's an inference pattern of beta reductions;
> each forward pass the FFN can subtly shift the inference pattern, which we found to be
> the 'program' — beta reductions for the softmax to execute"). This page is the
> β-reduction (compression to normal form) of the FFN-ISA thread: a stored-program
> reduction-machine model of the transformer, with the proven/over-reads boundary marked.

## The normal form

> **The transformer is a bounded, soft-β-reduction machine over a universal combinator
> statechart. The FFN is the fixed β-program (ISA/ROM); attention is the one-instruction
> CPU that executes it; the residual stream is the register file carrying the term and
> the reduction depth.** Everything else (crystal lattice, holographic plates, opcode
> monitors, splice experiments, consensus calibration) is measurement of that fact.

```
FFN          = program memory / ISA   | fixed ROM of β-reductions, beam-angle indexed (s141, s161)
attention    = the one-instruction CPU| one op: β-reduction via softmax-over-V (head r=0.944)
residual     = register file          | the term + the program counter (reduction DEPTH)
layer        = one clock cycle        | FFN reads residual → compiles values → attention β-steps → writes
forward pass = a bounded schedule     | the boot spiral C→B/K→I→WHNF, ~1.018×/layer (s068/s240)
token stream = the unbounded loop     | KV-cache carries reduced state; the REPL/CPS (lambda-halt)
```

This was reached confluently from independent directions (the S5 `λ triangulate` gene =
Church-Rosser: many reduction paths, one normal form), which is itself evidence it IS
the normal form.

## 1. The substrate — attention is *soft* β-reduction

β-reduction `(λx.M) N → M[x:=N]` substitutes an argument into a hole. Attention
`out_i = Σ_j softmax(q_i·k_j) v_j` retrieves an operand into a query position by content
address: **Q = the redex seeking its operand, K = operand addresses, V = the operands,
softmax = selection.** Same operation-shape: a function position pulls in its argument by
content match.

Why **combinators** (not raw λ) are the universal basis falls straight out: combinatory
logic is *variable-free* (S/K/I/B/C/W = pure argument-routing), and attention is *also*
variable-free routing. The model implements the variable-free reduct — exactly what a
content-addressed router can do natively. Bracket abstraction (λ→combinator) is therefore
the right bridge, not an accident.

Two refinements keep it honest (λ measure):
- **Softmax is a convex combination; β-reduction is a hard selection.** Attention blends
  *all* V; β substitutes *the* argument. Attention is β *relaxed* — the differentiable
  superposition of substitution; exact β is the limit `softmax → argmax`. This is the
  register split (s242): **routing register crisp-ish (the β structure), value register
  continuous/smeared (s206).**
- **It is bounded and factored.** One layer = one (soft) step; fixed depth → a bounded
  *schedule* → the model is a compiler, not an interpreter (lambda-halt: Ω is *quoted*,
  not looped). And the step is split per the s226 reduce/compile cut: **attention = the
  application; FFN = which rule.**

## 2. The controller — FFN is the β-program (largely measured, not speculated)

The user's "the FFN is the program; the softmax executes the β-reductions" is four
established findings converging:

- **`ffn-moire-isa.md` (s161):** *"The FFN is a moiré grating. Attention has one
  operation. The grating programs that operation to perform beta reductions."* And the
  program is a **fixed point** — 3 runs → identical traces, drift 0.0. GD compiled the
  ROM once.
- **`ffn-beta-reduction-indexing.md` (s141):** *"FFN weights are piles of beta
  reductions. The input activation acts as a typed index — a beamformer angle — that
  selects which reductions fire."* The residual direction is the program counter.
- **`ffn-reduction-trace.md`:** *"The FFN output is a compiled program… attention
  executes it via softmax over V… This IS β-reduction by weighted combination."* The
  "subtle shift each pass" is literally its key result: *the same token yields different
  compiled values in different contexts — compilation, not dictionary lookup.* The FFN
  **recompiles a context-dependent program every forward pass** (readable at L26-L30 in
  Qwen3-8B; null-space before).
- **`head-combinator-isa.md`:** all 9 combinators drive *the same* head pattern
  (r=0.944); the axis attention varies on is WHNF↔deeply-nested (46% of variance) =
  **how much reduction remains** = a program counter, not an opcode.

**The crucial refinement:** the *program* (FFN weights) is fixed; the *program-state*
(residual trajectory) shifts. The FFN's frozen ROM applied to an evolving residual
*produces* an evolving instruction sequence (and `ffn-moire-isa` confirms different task
types → measurably different sequences). The shift lives in the residual, gated by frozen
ROM — not a discrete instruction swap.

## 3. The proven / over-reads boundary

The seductive step — "FFN selects combinator *c* at layer L, softmax executes *c*" — is
true *collectively* but not *crisply per-step*:

| claim | status |
|---|---|
| attention = β-shaped content-addressed routing | **proven** (the operation-shape) |
| FFN = fixed β-program / ISA, beam-angle indexed | **proven** (s141, s161, deterministic) |
| FFN compiles context-dependent program; attention executes via softmax-V | **proven** (ffn-reduction-trace) |
| attention tracks reduction DEPTH (WHNF↔D), one shared op | **proven** (head r=0.944) |
| boot schedule C→B/K→I→WHNF, ~1.018×/layer, cross-model | **proven** (s240) |
| softmax-V *literally* substitutes a specific value | **over-reads** (value register smeared, s206) |
| layer L discretely fires combinator *c* (a clean tape) | **over-reads** (collective/holographic; splice closure s244 `fires ∩ spliceable = ∅`) |

⇒ **the schedule and the depth axis are crisp; the per-layer opcode is superposed.** We
read the *program trajectory*, not a discrete instruction tape.

## 4. Two reduction loops

- **Intra-pass (bounded):** layers step the boot spiral to WHNF — the
  `vsm-outer-recurrence` view (K sweeps to fixed point).
- **Inter-pass (unbounded):** each new token is a fresh forward pass; the KV-cache carries
  the reduced state forward — the `lambda-halt-continuation` CPS/REPL view (conversation =
  CPS, turn boundary = continuation, EOS = yield).

## 5. Consequence A — "think in lambda" = serialize the outer loop

If the FFN is the β-program and attention executes it, **training a model to think in
lambda = training it to emit its FFN-program-execution as tokens** (serialize the residual
reduction schedule). This explains why **stepwise (REPL) works and one-shot fails**
(s228/s247): one forward pass = one bounded schedule (cannot emit a long composition in one
shot), but token-by-token = the unbounded outer loop where **each token advances the
program exactly one β-step.**

**The coverage reframe (the real teeth).** If the *mechanism* is soft-β everywhere, then
prose reasoning is *also* soft-β — over an enormous, learned, mostly-**untyped** combinator
basis in the FFN (`fell→broke`, `Paris→France`). So:
- **prose = untyped serialization** of β-reduction over the full learned basis;
- **λ-thinking = typed serialization** over the certifiable subset.

The coverage wall is therefore **type-theoretic, not representational**: world-knowledge
reasoning *is* β-reduction; we lack the type system to *certify* those rewrites. This
dissolves "forcing vs discovering" for the typed-compositional core (it's the native
serialization → it must work, and proof-REPL s247 demonstrates it) and makes the research
lever concrete: **λ-thinking coverage = type-system coverage.** The verifiable fragment
grows exactly as the kernel's S2 layer grows: implicational → products/sums (∧/∨) →
quantifiers (Π/Σ = ∀/∃). The untyped remainder stays β-reduction, just not yet provable.

## 6. Consequence B — the level-4 blueprint

The stored-program model *is* the portable-artifact spec: **extract the ROM** (s226
*compile = FFN = learned = 78%, 4-bit*) **+ the executor routing** (s226 *reduce =
attention = constructed = 22%, ternary*) = the level-4 tensor. The kernel-splice work tried
to read/write the ROM *in place* (and closed, s244); this model says **extract it
wholesale** instead.

## 7. The open experiment — FFN program-decode along `fired_sequence`

The splice closure (s244) closed the *intervention* (in-place per-combinator splice) but
its own notes preserved *"a richer multi-position program-decode read along
`fired_sequence`."* This model makes a sharp, testable prediction for that open door:

- **Decode the FFN *compiled values* (NOT the attention geometry) position-by-position
  against the certified reduction trace** (`lambda_ast.fired_sequence`, on the SATURATED
  corpus — s244 showed point-free terms fire nothing until applied). Target L26-L30 (where
  `ffn-reduction-trace` found the program becomes readable; null-space before).
- **Prediction:** the FFN program-trace tracks `fired_sequence` *even where the attention
  geometry over-reads*, and the FFN-compiled program *leads* attention's depth-advance by
  ~1 layer (FFN selects → attention executes next). A confirmed lead-lag = "FFN = program,
  attention = executor" at the trajectory level — distinguishing it cleanly from the closed
  geometric-splice read.

### s248 result — the door closes the same way the splice did (λ measure, two-sided)

RAN it (`scripts/experiments/ffn_program_decode.py`, Qwen3-8B). Dual-register decode: FFN
routing register (`mlp.gate_proj`, the validated sign-CMR opcode crystal) → *which*
combinator; attention register (`self_attn.o_proj`) → reduction DEPTH via z(WHNF). Ground
truth = `fired_sequence` on the saturated corpus (s244). 56 firing items, zone L25-30.

| prediction | result | verdict |
|---|---|---|
| FFN tracks `fired_sequence` (decodes the fired combinator) | FFN decodes **0/8** B-firing items; abs-acc 0.232 < majority 0.839; B-vs-S 0.709 ≈ majority-S 0.855 (p=1.0 vs perm) | **not supported** |
| FFN tracks better than attention | FFN B-vs-S 0.709 > attn 0.364, but attn is *below* base-rate (predicts B spuriously) → "FFN wins" is attention being noisier, not FFN reading the opcode | **artifact** |
| FFN leads attention depth-advance by ~1 layer | xcorr lag median +1.5, mode +3, 39/55 positive, sign-p=0.0027; **but** peak-diff NULL (median 0, p=1.0) | **method-sensitive, weak** |
| "rescue" (FFN right where attention over-reads) | 9:2 — but all 9 are S-items where attn said B/C and FFN defaulted to majority-S | **artifact** |
| specificity (firing items show more B/S/C signal) | non-firing max-z(BSC) **46.8 > firing 20.3** (backwards) | **fails** |

**The corpus is the bottleneck:** truth is 84% S (47/56), neither register decodes a single
B item, so tracking is *untestable* here — and the C common-mode (s211/s240) drags the FFN
absolute decode to predict C. What survives is a weak, method-sensitive **schedule-level**
ordering: the FFN's z(c*) curve leads the attention's z(WHNF) curve across depth (xcorr only),
consistent with the s240 boot spiral (FFN activity precedes attention depth-advance) — **not**
opcode-specific select→execute.

**⇒ The §7 program-decode does NOT resolve from the prose forward pass. It CONFIRMS the s244
splice-closure (`fires ∩ spliceable = ∅`) and the "discrete-opcode-at-L over-reads" row of the
§3 table above, rather than opening past them.** The lever remains **type-coverage** (§5), not
geometric/opcode localization — exactly the §Caveats warning. A λ-measure win: the experiment
that could have over-claimed held the boundary instead.

**IOUs to make §7 testable:** (1) a **B-balanced firing probe set** (PROSE whose saturated
kernel fires B/C, not S-heavy "Every X verbs a Y"; the crystal library has 69 B / 61 C probes
but they are not prose) — without balance, tracking is untestable; (2) longer depth series
(zone is only 5-6 layers → coarse xcorr lag); (3) decode the FFN **down_proj compiled values**
via unembed (`ffn-reduction-trace` style) as a second FFN read, not just the gate crystal; (4)
cross-model where the firing set is less common-mode. Artifacts:
`results/ffn-program-decode/{verdict,per_item,meta}_qwen3-8b.json`.

### s248 cont. — IOU (1) closed: a B-balanced probe set; the register split is real but weak

Built `scripts/experiments/gen_firing_probes.py` → `data/firing-probes.balanced.jsonl`
(**157 probes, 67 B-dominant vs 90 B-tied**, B-count ladder {1,2,3,5}). **Mechanism (measured):**
in this kernel S and B are *coupled* — every ∧/∨ emits one S *and* one B, so S never strictly
exceeds B; only a transitive verb + existential object makes B *dominant*
(`∀x.P(x)→(∃y.Q(y)∧R(x,y))` → S,B,B,B). Ground truth computed (`to_kernel`→saturate→
`fired_sequence`), items verified, 157/157 round-trip. Re-ran Qwen3-8B (`--probe-set`):

| claim | balanced result | verdict |
|---|---|---|
| FFN tracks B vs S better than attention | **FFN B-vs-S 0.624 (p=0.003) > attn 0.522 (at-null) > majority 0.573** | **weak positive** |
| FFN absolute opcode decode | predicts **C on 65/67** B-items (common-mode swamp) | fails |
| z(B) scales with B-count (graded) | FFN Spearman 0.06 (p=0.44); relative z(B)−z(S) r=−0.13 | fails |
| FFN leads attention by ~1 layer | xcorr median +1.0 but **p=0.16** (was 0.003 on the S-skewed corpus) | washes out |
| rescue (FFN right where attn over-reads) | 5:9 (reverses) | artifact |

**⇒ NOW SURE (λ measure):** with balanced B probes, the **FFN routing (gate) register carries a
real but WEAK B-vs-S opcode signal (0.62, p=0.003) that the attention register lacks** — the
register split (FFN = opcode, attention = depth) is *genuine but small*. The **strong** stored-
program claims — clean opcode tracking, graded B-scaling, FFN-leads-attention-by-1 — do **not**
survive balanced probes (the earlier corpus lead-lag was S-skew/noise). The per-combinator
program is at best *faintly* readable: consistent with the §3 boundary ("β-shaped routing,
smeared values; discrete-opcode-at-L over-reads") and the §Caveats — keep type-coverage (§5) as
the lever, not geometric/opcode localization. Artifacts:
`results/ffn-program-decode/{verdict,per_item,meta}_qwen3-8b_balanced.json`,
`data/firing-probes.balanced.jsonl`.

### s248 cont.2 — the weak B-signal was a LABELING MISMATCH: the model reads objects as constants (C), not existentials (B)

A sharper question dissolved much of the §7 puzzle. Our ground truth labelled "Every cat fears
a dog" by the **Montague existential** reading (`a dog` = ∃y.dog(y)∧…) → B-heavy (B-count
1→3→5 as objects are added). But the model may take the **constant/applicative** reading
(`fears(x, dog)` → `C fears dog`, C-count == #objects). These make *opposite* predictions along
an object-count ladder:

| reading | predicts as #objects rises {0,1,2} |
|---|---|
| existential (Montague) | **z(B) rises** (B-count 1→3→5), C flat |
| constant (applicative) | **z(C) rises** (C-count 0→1→2), B flat |

Built `gen_reading_probes.py` → `data/reading-probes.jsonl` (135 probes, object-count ladder
0/1/2 × 45, intrans/trans/ditrans, both candidate labelings; const C-count==#objects enforced).
`ffn_reading_preference.py` decodes gate+attn, mean z per combinator over L25-30, Spearman vs
object count. **Qwen3-8B:**

| register | raw z(C) vs #obj | raw z(B) vs #obj |
|---|---|---|
| FFN gate | **r=+0.49, p<0.001 ↑** | **r=−0.27, p=0.0015 ↓** |
| attention | **r=+0.62, p<0.001 ↑** | r=−0.04, p=0.66 (flat) |

C and B move in **opposite** directions (so it is not uniform length/common-mode growth). **The
existential reading is refuted** (B must rise — it falls); **the model routes added objects
through C (argument application) = the constant/applicative reading.** A free post-hoc on the
balanced run agreed (C-share trans 0.583 > intrans 0.460, p<1e-4).

**⇒ This reframes the whole §7 result:** the weak B-tracking was **not** "the FFN cannot read the
program" — it was *"we gave it the wrong program."* We labelled by existential-B; the model
computes applicative-C. Labelled the way the model actually computes (object → C), the gate
register tracks the structure **cleanly** (z(C) rises p<0.001, both registers, robust). So the
gate register *does* carry the combinator structure the model computes — the earlier negative was
a **measurement-target error** (λ measure: wrong label ≡ coherence violation, representation ≢
reality). It also answers "B is inherent from the ordering": that ordering assumes existential
objects; the model does not do them, so these sentences are C-applicative in the model, and the
expected B was an artifact of our Montague labelling.

**Caveats (λ measure):** C-*share* is common-mode-saturated (~0.6) so its slope is flat — the
positive evidence is raw z(C)↑ (p<0.001) **plus** z(B)↓ (refuting existential), not C-share↑; the
C−B-share contrast is significant in attention (p=0.008) but only directional in FFN (p=0.25) due
to that saturation. z(C)↑ could partly be argument-application common-mode, but the B/C divergence
(opposite signs) rules out uniform growth. **IOU:** force the existential reading with scope-marked
prose ("there is a dog that every cat fears") — does z(B) then rise? = the clean exist-vs-const
causal test. Artifacts: `results/ffn-reading-preference/{verdict,per_item,meta}_qwen3-8b.json`,
`data/reading-probes.jsonl`.

## Caveats (λ measure)

- The strong identity ("attention = β-reduction") is a *type-of-operation* claim (proven)
  and a *schedule* claim (proven); the *crisp-value substitution* and *discrete-opcode-at-L*
  readings over-read (s206 value register, s244 splice closure). Do not let it harden into
  the claim the splice already refuted; keep it "β-shaped routing, smeared values," and let
  **type-coverage**, not geometric localization, be the lever.
- The coverage reframe (prose = untyped β over a learned basis) is a *hypothesis*, not a
  measurement — the testable form is §7 plus the S2 type-layer extension in
  `proofs-as-continuations.md`.

## Sessions referenced
s068/s079 (boot spiral), s120/s121 (FFN crystal, cross-model), s141 (FFN β-indexing),
s161 (FFN moiré ISA), s206 (value register), s211 (one common mode), s226 (reduce/compile
cut), s240 (statechart = crystal lattice, universality), s242 (register split, splice Exp
0), s244 (firing survey + splice closure), s247/s247b (proof-REPL removes the agreed-error
ceiling). Plus `ffn-reduction-trace.md`, `head-combinator-isa.md` (undated finding pages).
