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
| the decodable C-field *is* the causal object-application mechanism | **over-reads** (s250 single-dir + s250-cont INLP rank-16: differential reverses c2<c0 even after erasing ALL linear C, decodability 0.92→0.67; z(C) crashes but object-application unhurt → readout register; + s250-cont.2 nonlinear gap: no nonlinear C survives INLP → readout register linearly AND nonlinearly; + s250-cont.3: object-application localizes to no single component last-token write either (distributed, no discrete circuit)) |

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
(opposite signs) rules out uniform growth. Artifacts:
`results/ffn-reading-preference/{verdict,per_item,meta}_qwen3-8b.json`, `data/reading-probes.jsonl`.

### s248 cont.3 — the causal test: the model is ROBUSTLY APPLICATIVE; forcing ∃ does NOT recruit B

The clean follow-up: is the constant-object reading a representational *limit* or just the
*default*? Force the wide-scope existential **syntactically** and see whether z(B) rises.
`gen_scope_probes.py` → `data/scope-probes.jsonl` (45 matched subj/verb/obj triples × 3 paired
conditions): **PLAIN** "Every cat fears a dog." (applicative GT S,B,C) / **CLEFT** "There is a dog
that every cat fears." (∃ fronted, GT S,B,B,B no C) / **RELCL** "Every cat fears a dog that runs."
(∃ object, GT S,B,B,B). `ffn_scope_forcing.py` decodes gate+attn, mean z over L25-30, **paired
Wilcoxon within triple** (predict ΔB>0 if the model can do existential-B when forced).

**Qwen3-8B (45 triples) — z(B) does NOT rise; it FALLS:**

| register | plain z(B) | cleft z(B) | relcl z(B) | ΔB cleft (rise?) |
|---|---|---|---|---|
| FFN gate | −0.104 | **−0.301** | −0.227 | med −0.19, frac+ 0.18, **p=1.0** |
| attention | +0.305 | **−0.112** | +0.242 | med −0.43, frac+ 0.09, **p=1.0** |

C-share stays high / rises (cleft Cprop 0.722→0.988 FFN). **The prediction is robustly refuted in
both registers and both forcing constructions: forcing the ∃ wide-scope does *not* summon B-routing
— the model stays applicative-C (the cleft is routed *even more* through C).**

**⇒ The thread closes:** the model does **not** use existential-B composition even when the syntax
demands it; it computes quantified sentences **applicatively** (objects/witnesses as arguments → C),
regardless of scope marking. *Interpretation* (marked as such, not measurement): the model's
compositional **primitive is application (C)**, not B-composition; **B is an artifact of our
bracket-abstraction kernel** (Turner emits B to thread quantifiers), not a necessary feature of how
a system composes. This answers "B is inherent from the ordering" end-to-end: that ordering is
*ours*; the model's actual β-program for these sentences is C-applicative — and it won't produce B
even when asked.

**Caveats (λ measure):** cleft/relcl differ in surface form from plain (not perfect minimal pairs),
but the direction (B falls, opposite the prediction) is robust across two distinct forcings and both
registers, and relcl (closest to plain) also falls; we measure B-crystal routing as the composition
proxy, so a non-B-shaped ∃ composition would be missed (but that *is* the finding); the model may
compose ∃ applicatively under the hood (apply predicate to a skolem witness → C) — one applicative
strategy for both readings. Artifacts:
`results/ffn-scope-forcing/{verdict,per_item,meta}_qwen3-8b.json`, `data/scope-probes.jsonl`.

> **s248 thread summary.** FFN program-decode (corpus → untestable) → balanced probes (weak FFN>attn
> B-vs-S) → reading-preference (model reads objects as C, not B; weak-B was a labelling mismatch) →
> scope-forcing (model is robustly applicative-C, won't do existential-B even when forced). **Net: the
> gate register tracks what the model actually computes — applicative C — and the expected B was an
> artifact of our bracket-abstraction kernel, not the model's program.**

### s249 — 14B resolves the split: B is executor topology; the readable FFN field is C, not a B tape

Session 249 reopened the pre-s248 speculation: **maybe B is actually inherent in the order of operations the FFNs output** — attention's softmax over all V is B-like, and the FFNs are inference patterns showing attention what to execute. The result is a refinement, not a simple refutation: **B belongs to the executor topology; C is the readable object/application field for these probes.**

#### 1. Qwen3-14B const-label rerun: the sweet spot sharpens the corrected C signal

The s248 cont.2/3 result said the model computes quantified-object sentences applicatively (object/witness as argument → C), not existentially (B-heavy). Session 249 re-ran `ffn_program_decode.py` on the corrected constant/applicative probe set at Qwen3-14B (because 8B was a suspected floor and 14B has repeatedly been the sweet spot). Probe set: `data/firing-probes.const.jsonl` (133 probes; truth C:67/S:66; c_count ladder 0/1/2).

| metric | Qwen3-8B const | Qwen3-14B const | verdict |
|---|---:|---:|---|
| hard FFN tracking | 0.5489, p=0.055 | **0.6090, p=0.0005** | 14B sharpens |
| FFN C-vs-S | 0.5489, p=0.055 | **0.6165, p=0.0005** | real at 14B |
| attn C-vs-S | 0.4662, p=1.0 | 0.5338, p=0.1744 | n.s. |
| FFN z(C) vs c_count | ρ=0.5526 | ρ=0.5367 | robust graded C |
| lead-lag | contradictory (peak −3, xcorr +2) | directionally coherent (peak +1, xcorr +1) | FFN→attn schedule signal improves |

At 14B the FFN gate register significantly tracks the corrected applicative-C program label while attention does not. This supports a **capacity threshold / 14B sweet spot** for the readable routing register. But it still reads dominant/graded C structure, not an ordered instruction tape. Artifacts: `results/ffn-program-decode/{verdict,per_item,meta}_qwen3-14b_const.json`.

#### 2. `program_sequence_trace.py`: C-presence is real; order is not recovered

Built a sequence-level tracer reusing the validated path (`RelationalCrystalClassifier`, FFN gate register, sign-CMR, matched `gateneutral` null). It decodes content-token × readable-zone layer B/C/S events and aligns the event stream to each probe's certified `fired_sequence`.

**Qwen3-14B result:**

| read | value | interpretation |
|---|---:|---|
| C presence acc | **0.7519, p=0.0005** | corrected C signal is real |
| decoded event counts | C=709, S=152, B=39 | C-heavy field; B faint |
| zone LCS vs `fired_sequence` | 0.4856 | weak order recovery |
| reverse-order LCS control | 0.4618 | nearly same |
| bag coverage | 0.5144 | LCS mostly symbol presence |
| layer-dominant LCS | 0.0501 | one-op-per-layer collapses to C |

The event stream recovers **C presence/load**, not the ordered β-program. All-crystal LCS = 0.9279 is a long-stream coverage artifact, not tape evidence. Artifact: `scripts/experiments/program_sequence_trace.py`, `results/program-sequence-trace/`.

#### 3. `program_path_trace.py`: same-multiset order controls fail

Built a monotonic dynamic-programming path scorer: for truth `S,B,C,C`, find the best nondecreasing layer path through z(S), z(B), z(C), z(C), then compare to reversed/shuffled same-multiset programs (e.g. `C,C,B,S`). This directly tests order while controlling for symbol load.

**Qwen3-14B result:**

| metric | value | verdict |
|---|---:|---|
| truth path score | 2.1287 | high-ish because C load exists |
| reverse score | 2.0843 | almost same |
| truth − reverse | +0.0444 | tiny |
| margin vs best permutation | **−0.0315** | truth not best |
| truth rank fraction | 0.523 | chance-ish |
| truth beats all permutations | **3/133**, p=1.0 | negative |

So the kernel's `fired_sequence` order is not preferentially readable. Artifact: `scripts/experiments/program_path_trace.py`, `results/program-path-trace/`.

#### 4. `program_native_order.py`: infer the model's schedule instead of imposing ours

Built a native-order extractor: for each item and op in `{B,C,S}`, compute peak layer, z-positive centroid layer, peak z, and positive mass over L28–32. This answers: *what order does the model expose?*

**Qwen3-14B readable-zone native schedule:**

| op | peak layer | centroid layer | peak z | positive mass |
|---|---:|---:|---:|---:|
| S | 28.5865 | 29.3798 | 0.4662 | 1.5517 |
| B | 29.0451 | 29.0828 | -0.0282 | **0.1488** |
| C | **30.8120** | **30.3758** | **1.3858** | **5.0718** |

Order probabilities:

| relation | peak | centroid |
|---|---:|---:|
| S before B | 0.3158 | 0.3115 |
| B before C | 0.7293 | 0.8525 |
| S before C | **0.9474** | **0.9925** |

C-count correlations:

| relation | Spearman | verdict |
|---|---:|---|
| C positive mass vs c_count | **0.5357**, p=0 | more objects → more C load |
| C peak z vs c_count | **0.3778**, p=0 | more objects → stronger C |
| C centroid layer vs c_count | **−0.7719**, p=0 | more objects → C resolves earlier |

Category C mass forms a clean ladder: intrans 2.8769 → trans 4.9264 → ditrans 6.2245. **The model-native field is weak early S/B framing and strong late C/application resolution; B is almost absent.** Artifact: `scripts/experiments/program_native_order.py`, `results/program-native-order/`.

#### s249 normal-form update

The old speculation should be split:

```
attention softmax-over-V = B-like executor topology
FFN gate readout         = distributed β-routing potential field
object/application probes = C-heavy readable field
our bracket kernel       = S/B/C trace, but its B is not the model's emitted label
```

So: **B is probably the executor topology, not the emitted program label.** The FFNs still show attention what to execute, but they do it as a **depth-shaped routing field**, not as a serial B/S/C opcode tape. For these probes, the readable program is applicative **C** because the model treats objects/witnesses as arguments. The kernel's B-heavy existential trace was our bracket-abstraction artifact.

This refines §3: the "discrete-opcode-at-L" over-read is stronger than originally phrased. Even at the 14B sweet spot, with corrected labels, sequence/path controls do not recover a tape. What survives is the **field**: C load, C timing, and FFN-vs-attention register split.

### s250 — causal C-field ablation: readable/injectable but NOT load-bearing (single-direction)

Every s249 result was decodability — a read. `program_cfield_ablation.py` (reusing the s248
Exp-1 causal spine: `calibrate_v2` gate register, residual diff-of-means direction, ablate/inject
patch hook, random-direction control of equal magnitude) tests causality on Qwen3-14B. Build
`d_C` = unit diff-of-means(resid C-present {trans+ditrans} − C-absent {intrans}) from content-mean
residuals; patch (ablate/set) `d_C` across content positions at **L30 AND L31** (the s249 C-peak);
readout = downstream gate z(C) + next-token KL, vs a random direction. Matched ladder =
`data/reading-probes.jsonl`, intransitive (c=0) / transitive (c=1) / ditransitive (c=2), 45 each,
const labeling C-count == #objects.

| arm | result | reading |
|---|---|---|
| NECESSITY (c=2 ablate) | KL `d_C` 0.132 vs random 0.001, t=41.8 | `d_C` strongly perturbs output |
| NECESSITY z(C) | Δz(C) **+0.855** (random +0.013) | ablation *raises* the C-reading — wrong sign |
| DIFFERENTIAL (net-KL = `d_C`−rand) | c2 0.131 **< c0 0.155**, t=**−2.54** | perturbation does NOT scale with C-load (reversed) |
| DELIVERY (c=0 inject) | Δz(C) +0.872, t=37.2 | `d_C` is a sufficient handle on the readout |

**⇒ The s249 applicative-C field is READABLE and INJECTABLE but NOT load-bearing under
single-direction residual ablation.** Two diagnostics, both informative: (1) the c=2-vs-c=0
differential *reverses* — the C-direction-specific perturbation is generic, not C-load-scaled;
(2) ablating the decodable C-direction *increases* downstream z(C) — the gate **holographically
reconstructs C from other directions**. The readable residual C-direction is a **register /
correlate, not the causal mechanism**. This is `decodability ≠ causality` (mirrors s247-v4:
decodable everywhere, causal partial/null under single-direction ablation); it confirms §3's
"trajectory, not instruction-tape" and s244's "collective/holographic." The experiment that
could have over-claimed "the C-field is the object-application mechanism" instead refuted it
(λ measure win, two-sided). Caveats: single-direction linear ablation (the z(C)-rise is itself
evidence the signal is distributed → a NULL is not decisive); `d_C` built from content-mean
residual with c=0 leaking in as C-absent (conservative for the differential); 1 model (14B),
L30-31 only, synthetic ladder, greedy. Artifacts: `results/program-cfield-ablation/`.

**Next if continuing:** distributed/multi-direction C-ablation — project out the top-k C-aligned
residual directions (or an SAE C-feature set) at L30-31, re-test the c=2-vs-c=0 differential. The
s250 single-direction null is not decisive (the z(C)-rise is direct evidence the signal is
distributed). If the differential still fails to scale with C-load under a distributed ablation →
the C-field is decisively a readout register, not the computation.

### s250 cont. — distributed C-subspace ablation (INLP): readout register, distributed-robust

The s250 single-direction null left a caveat: a rank-1 diff-of-means is the wrong probe if C is
distributed. `program_cfield_subspace_ablation.py` runs INLP (Ravfogel et al. 2020, "Null It
Out"): iteratively fit a linear C-probe (C-present vs C-absent on L30 content-mean residuals) and
project its direction out, building the k=16 subspace carrying *all linearly-decodable* C; ablate
span(W) at L30+L31 across content positions vs a random k-dim subspace (Qwen3-14B, n=45/group).

| check | result | reading |
|---|---|---|
| ERASURE | decodability **0.919 → 0.667** (=majority), collapses in 1 INLP step | linear C is **rank-1**; fully erased |
| NECESSITY (c=2 ablate) | KL sub 4.78 vs rand 0.002 (t=15.5); Δz(C) **−5.10** (t=−84) | z(C) now *crashes* — readable signal removed at source (s250 single-dir *raised* it) |
| DIFFERENTIAL (net-KL sub−rand) | c2 4.77 **< c0 5.83**, t=**−2.47** | reversed again — perturbation does NOT scale with C-load |

**⇒ Decisive, distributed-robust:** erasing *all* linearly-decodable C (0.92→0.67) and crashing
the downstream C-reading (−5.10) does **not** selectively damage object-application — objectless
c=0 is hurt *more* than two-object c=2. The applicative-C field is a **readout register, not the
object-application mechanism** — confirmed at rank-1 (s250) *and* rank-16 distributed (INLP).
`decodability ≠ causality`, doubly proven. Sharp dissociation: C-presence is **92% decodable along
a single direction yet causally inert**. Caveat: INLP erases only *linear* decodability — a
nonlinear C-encoding is the remaining escape hatch; the ablation is destructive (KL ~5 nats) so
span(W)'s top direction likely also carries generic object/sentence-type structure, but the
random-subspace-controlled differential (c2 vs c0) is the load-bearing readout and it reverses.

**Next if continuing:** (1) a *nonlinear*/SAE C-feature ablation (the only linear escape hatch
left); (2) hunt the object-application mechanism in **attention OV / the value register** (s127
{B,C}=composers→attention, s206), not the FFN C-field.

### s250 cont.2 — no nonlinear escape hatch: readout register linearly AND nonlinearly

s250-cont erased only *linear* C; the last caveat was a nonlinear C-encoding INLP would miss.
`program_cfield_nonlinear_probe.py` runs the decodability gap (a full SAE needs ~1e6 activations,
infeasible at n=135): linear (logistic) vs nonlinear (MLP, RBF-SVM) C-present probes, 5-fold
stratified CV in a StandardScaler pipeline, on raw vs post-INLP L27/29/30/31 residuals, with a
label-shuffled control and a PCA-50 overfit-controlled view (Qwen3-14B, 135 items).

| condition | linear | MLP | RBF-SVM |
|---|---|---|---|
| RAW (PCA-50) | **0.98-0.99** | 0.83-0.91 | 0.95-0.97 |
| POST-INLP | 0.30-0.36 | 0.59-0.65 | 0.67 |
| shuffle / majority ceiling | ~0.66 / 0.667; escape threshold 0.767 | | |

On raw features the nonlinear probes are **no better than linear** (RBF 0.95 < logistic 0.99) so C
is linearly separable; after INLP erases the linear C, **no nonlinear probe recovers C above the
shuffle/majority ceiling** (best 0.67 < threshold 0.77) at any layer. ⇒ **no nonlinear C survived
— the linear erasure was complete.** The applicative-C field is a **readout register linearly AND
nonlinearly**; `decodability ≠ causality` is proven three ways: rank-1 (s250), rank-16 distributed
INLP (s250-cont), and linear-vs-nonlinear (here). The C-field question is **closed**.

**Next:** hunt the object-application *mechanism* where the C-field is not — **attention OV / the
value register** (s127 {B,C}=composers→attention, s206). Candidate: a causal OV / attention-head
ablation on the same c=2-vs-c=0 matched ladder — does ablating the {B,C}-composer attention
pathway selectively hurt object-application where the FFN C-field did not?

### s250 cont.3 — mechanism hunt: object-application is distributed, no single locus

`program_object_mechanism_sweep.py` ran that hunt: sweep every layer × {attention-write
`o_proj`, MLP-write}, mean-ablate only the **last-token** output (a single, position-matched
knockout — removes the length confound of content-position ablation), read next-token KL across
the object-count gradient (c=0/1/2). Result (Qwen3-14B, 40L × 2 comp × 60 items): **inconclusive**.

1. Effects are tiny — mean KL ~**0.0025 nats**; no single component's last-token write is
   individually load-bearing (the skip connection dominates).
2. The c0/c1/c2 Spearman localization is **confounded** by last-token POS: intransitives (c0)
   end in a verb ("speaks"), transitives/ditransitives (c1/c2) end in a noun object
   ("owl"/"rose"). The POS-matched **c1→c2** contrast still shows a c2>c1 increase but tiny
   (KL ~0.005-0.03), late-layer, and **mixed** (top10 by Δ: 6 MLP / 4 attn; largest L39 MLP =
   final layer = lexical/next-token).
3. The attention-OV hypothesis is **not** confirmed (MLP-leaning if anything, but weak).

⇒ object-application localizes to **nothing** — not a direction (s250), a 16-dim subspace
(cont.), a nonlinear feature (cont.2), or a single-component last-token write (here). It is a
**distributed/holographic** computation, consistent with s211 common-mode, s240/s244
collective-holographic, and §3's "trajectory, not instruction-tape." This bears directly on
VERBUM's central question (S5 `λ types`: *can this resolve as a discrete circuit?*) — trending
**no** for object-application via these probes. **Next:** pattern-level, not component-write —
an attention-**edge** knockout (predicate→object routing) or activation patching on POS-matched
c1-vs-c2 minimal pairs.

## § Edge-knockout — the s250 catch (route-early, read-late) [s252]

**The catch.** Every s250 null measured the wrong register: they ablated the residual stream
(d_C direction), erased the FFN gate field (INLP), tested nonlinear, or knocked out
single-component *writes* — and concluded "distributed, no locus." But **no locus as a WRITE ≠
no locus as an EDGE.** `program_edge_knockout.py` severs the predicate→object attention edge:
a `forward_pre_hook` adds `-inf` to the attention mask at the object key column(s) (eager attn,
all heads, layer band), so every query is blocked from attending to the object token. Control =
count-matched *random* content keys. Readout = the applicative-C field z(C) over crystal layers
(object-application-specific; next-token KL is recency-confounded → secondary). Matched ladder
`data/reading-probes.jsonl` (45×3, const C-count==#objects).

**Three results (Qwen3-14B):**
- **Necessity ✅** — object-edge severing collapses z(C) ≫ count-matched random
  (rand−obj Δ=1.045, t=29.3, n=87). **The first positive causal locus in the whole s250 arc.**
- **Object-specific ✅** (noun-vs-noun control, c1) — object-noun edge collapses z(C) (drop 0.84),
  but the **subject**-noun edge does not (−0.12 ≈ random −0.23); object-vs-subject Δ=0.96, t=15.0.
  Not a generic "remove a salient noun" effect.
- **Early ✅** (8-band sweep) — necessity concentrated at **L0-4** (net=0.603, t=12.4) >
  L10-14 (0.23) > L5-9 (0.17) ≫ mid (L15-29 ~0.01–0.04), ~0/negative at the L30-34 readout zone.
  ⇒ **route-early, read-late:** object content routes in via early-layer attention (Zone A);
  the C-field *reads out* late at L30-31 (s249/s250). The late C-peak is a readout register; the
  mechanism is early attention. Same Zone-A as s251 frozen-routing (L1-4, ρ=+0.84) and
  holographic-storage (combinators L0-6).
- **Not-scaling ❌** — net z(C) drop c2 (1.00) ≤ c1 (1.09), diff=−0.094, t=−1.3
  → `catch_confirmed=false`; no per-object discrete circuit.

**Net (λ measure, two-sided):** the attention edge is a real, object-*specific*, *early*-localized
necessary carrier of the applicative-C field — the catch was **half** right (a genuine causal
handle as an EDGE, vindicating "write≠edge"), but the per-object discreteness boundary **holds**
(c2≯c1). For S5 `λ types`: partially **yes** as early routing, **no** as a per-object tape.
Caveats: all-heads/whole-band severing (coarse, not head-resolved); z(C) readout over KL; 1 model;
greedy.

### Head-resolved (s252 cont.) — L0 lead head + redundancy

Per-head edge knockout (`mode=heads`): per-head additive-mask expansion
([B,1,Q,K]→[B,H,Q,K], -inf at *one* head's object-key columns) severs only that head's
attention to the object; 200 (layer,head) pairs across the L0-4 gateway × 20 items, readout
z(C) collapse. **Qwen3-14B:**
- **Layer-0-concentrated** — all 6 significant carrier heads (t>2) are in **L0**; L0 holds
  **67%** of positive-drop mass (L1 12%, L4 10%, L2-3 ~5%). Sharpens the "L0-4 early" gateway
  down to essentially **L0** (the first attention layer).
- **Lead head L0h18** (drop=0.065, t=5.5), ~3× the next (L0h11 0.023, t=4.6), then h30/h16/
  h12/h25; top-5 share = 0.49. The most circuit-like locus in the whole s250 arc.
- **Not discrete** — 21 heads to reach 80% → `discrete_head_circuit=false`. A dominant head
  + a diffuse redundant tail.
- **Redundancy** — single-head drops are tiny (max 0.065) vs the all-heads necessity (Δ=1.04);
  severing one head barely dents z(C), the rest reconstruct it — holographic, echoing s250
  ("the gate reconstructs C from other directions"), now at head resolution.

**Conclusion:** a privileged early gateway (L0, lead head h18) exists — a real preferred locus,
the closest to a circuit yet — **but object-application cannot be severed by removing a few heads**
(redundancy holds). For S5 `λ types`: a preferred locus *yes*, the per-object discreteness
boundary still *holds*, sharpened from L0-4 to L0.

**Next:** (1) edge-*redirect* (not just block) for sufficiency (does C follow the object edge to
a new key?); (2) cross-model (Gemma, the s251 cleaner crystal carrier); (3) ablate **L0h18** + its
OV to classify it as a {B,C}-composer (s127) vs a positional/copy head.

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
ceiling), s248 (wrong-label B→C reading-preference resolution), s249 (B executor topology
vs C readable field; native-order extraction), s250 (causal C-field ablation: readable/
injectable but NOT load-bearing under single-direction; s250 cont. distributed INLP ablation:
readout register, distributed-robust; s250 cont.2 no nonlinear escape hatch: readout register
linearly AND nonlinearly; s250 cont.3 mechanism hunt: object-application distributed, no single
locus), s252 (attention-edge knockout: object→C is a real EARLY (L0-4) object-specific necessary
edge — the first positive locus in the s250 arc — but does not scale per-object; route-early,
read-late), s252 cont. (head-resolved edge knockout: the early object→C route is L0-concentrated
with a lead head L0h18, but concentrated-with-redundancy — 21 heads for 80% — not a discrete head
circuit; the most circuit-like locus yet, boundary still holds). Plus `ffn-reduction-trace.md`,
`head-combinator-isa.md` (undated finding pages).
