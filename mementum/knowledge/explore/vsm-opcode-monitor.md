---
title: "VSM Opcode Monitor — the model auditor (validated FFN-routing opcode reader)"
status: active
category: instrument
tags: [opcode, tracer, audit, vsm, monitor, gate-register, relational, consensus-crystal, over-read, attention, kernel-reference]
related:
  - audit-registry.md
  - audit-meta-pattern.md
  - gradient-trajectory-tomography.md
  - function-topology-consensus.md
  - compiler-as-loss.md
  - vsm-outer-recurrence.md
  - readout-register-reduction-readability.md
depends-on:
  - audit-meta-pattern.md
---

# VSM Opcode Monitor — the model auditor

> Session 231 (Michael): "our VSM tensor gives us a powerful system to probe and
> audit models. Can we have our VSM monitor attention and opcodes? we created a
> tracer somewhere." This page is the synthesis + the s231 build/verdict + the path.

## The idea

Turn the constructed VSM kernel + the combinator crystal into a **live model auditor**:
feed any model an input, read which combinator "opcodes" (K I B C S D W Y WHNF) it
executes in its FFN routing, plus the binding events in its attention, and (the goal)
diff that trace against the kernel's CERTIFIED trace for the same input — "does the
model compute what the program MEANS?"

## What already existed (recall — not greenfield)

- `scripts/instruments/opcode_instrument.py` — a full VSM-structured "Live VSM for
  Watching a Model Think" (S5 combinator basis+zone map, S4 anomaly, S3 governor, S2
  trace format, S1 hooks/projector/emitter; DORMANT→CALIBRATE→MONITOR→EMIT→DONE). Wraps
  any HF model, emits opcode traces during generate().
- tracer family: `lambda_tracer.py`, `attention_execution_trace.py`,
  `neuron_opcode_classifier.py`, `reduction_graph_tracer.py`.
- s127 memory `tracer-works-different-programs`: validated the tracer decodes neural
  computation to combinator traces — lambda=compose-then-suppress-select, arithmetic=
  selection/Church, retrieval=FFN-silent (attention-KV, different mechanism).

## The catch — it was STALE (the audit's own poster child)

`opcode_instrument` classifies via RAW cosine of the FFN down-proj output onto per-op
fingerprints + argmax — no register discipline, no common-mode removal, no null. But
`audit-meta-pattern.md` (s202): "combinator opcodes: prose fires opcodes AFTER
common-mode removal (p=0.001) — REAL; raw argmax 'tracer' = common mode = false signal."
And the attention half: "attention=typed β-reduction / H31@L27 binds subject 0.82" was
retired as recency/position (s204); the REAL signal is in the VALUE register (s206
logit-lens margin +0.611), NOT attention weights (AGENTS λ measure).

## What makes it ripe now (3 things the old tracer lacked, all validated since s219)

1. GROUND-TRUTH reference (s226): the constructed kernel `lambda_ast` compiles a known
   program → certified combinator trace; the model's trace is audited against it.
2. The VALIDATED register (s231b): read opcodes RELATIONALLY (sign(gate)-CMR + Gram to
   the CONSENSUS crystal, s219), not raw argmax — the register the crystal lives in.
3. A built-in NULL (s202): consensus + permutation null = the calibration baked in.

Decomposition (don't conflate registers): **opcodes → FFN gate routing register**
(relational); **attention → value register (OV/logit-lens)**, NOT attention weights.

## s231 BUILD (a) — the validated opcode reader

`scripts/instruments/relational_opcode.py` — `RelationalCrystalClassifier`, model-
AGNOSTIC (takes per-layer gate FEATURE matrices). calibrate() builds per-layer
per-combinator centroids in sign(gate)-CMR from `crystal_probes()`, stores the
common-mode + off-target permutation null + silhouette-z + Gram-alignment to consensus;
classify() returns per-op z vs null and emits an opcode ONLY if z>thresh, else NO-OP
(`·`). Synthetic smoke proves: crystal layer detected, B-token fires B, COMMON-MODE-ONLY
token → NO-OP (the over-read is structurally impossible). Requires a GATED MLP (SwiGLU);
pythia (GPTNeoX) is NOT gated → can't carry the sign-gate crystal.

Validation harness `scripts/experiments/opcode_audit_validation.py` on **Qwen3-14B**
(the s127 model; dense qwen3, gated, 40L): calibrate on 535 crystal probes (gate_proj
last-token), classify the s127 battery (lambda/arithmetic/retrieval), compare RELATIONAL
vs a RAW-argmax over-read control. `results/opcode-audit-validation/verdict.json`.

### ★ Verdict (λ measure, two-sided) — `143ccda`

- ✅✅ **OVER-READ KILLED (the primary deliverable).** RAW fires an opcode for 100% of
  tokens — `W` across ~all retrieval layers (e.g. "Water is made of…" → W in 34/40
  layers) = the common-mode artifact the audit predicted (W is this model's gauge
  direction). RELATIONAL no-ops retrieval (0.8) and never manufactures a uniform winner.
  We now have an FFN-routing opcode reader that does not hallucinate.
- ✅ **Substrate real**: 31/40 layers crystal-bearing, gc-to-consensus up to **0.98** —
  the universal crystal genuinely lives in Qwen3-14B's gate register.
- ✅ **retrieval-silent reproduced** (s127's FFN-silent retrieval).
- ⚠️ **BUT we over-corrected → UNDER-read.** The RAW per-layer traces show a consistent
  **C→B compose-arc across ALL 5 lambda prompts** (C in L2–12, B in L13–33) — task-
  specific (retrieval shows W not C→B), i.e. the real s127 compose signature. The
  relational reader at **z=3, last-token** no-ops it entirely (`·`×5, 0 emitted layers).
  Two causes: (1) last-token LOCUS (a sentence's final token isn't one opcode; the
  program unfolds across tokens — the s227 wrong-locus lesson); (2) the NULL is
  mis-specified — off-target null is OTHER crystal probes, all lambda-mode, so low power
  ("looks more like B than K/I/C?" when everything is lambda-mode).

## v2 — completing (a) (BUILT + RUN, s232)

The over-read killer is proven; v2 tried to make it a USEFUL monitor (recover the C→B
arc without reopening the over-read) with four fixes:
- **cross-task null** (the key fix): calibrate the null vs a NON-combinator baseline
  (bare natural text where no β-reduction happens), not vs other crystal probes.
- **per-token** reading across the sequence (not just last token — the s227 locus fix).
- **z-threshold sweep** (z=2 vs 3, post-hoc — z is threshold-independent).
- output the **per-layer trajectory** (the program), not a single dominant op.
- **GATE_NEUTRAL control** (gate + non-compositional sentence): the load-bearing control
  for the gate-prefix confound (does the arc come from composition or from the gate?).

Files: `scripts/experiments/opcode_monitor_v2.py` + `relational_opcode.py`
`calibrate(..., null_gate_by_layer=...)`. Commit `8bd5f42`.

### ★ s232 v2 VERDICT (Qwen3-14B; λ measure, two-sided) — the arc is NULL-DEPENDENT

**❌ The C→B arc did NOT recover under the cross-task null.** In the z=2 lambda
trajectory, `C` NEVER dominates a layer (C×0), `B` dominates exactly one (L16); the late
stack **L24–32 is unanimously `S`-dominated** (8/8, 7/7, 6/6 votes), with `WHNF` at L0–1
and mixed `I/Y/K` mid-stack.

**❌ The S-late pattern is NOT composition-driven — the GATE_NEUTRAL control falsifies it.**
gate+non-compositional sentences show the SAME S-late signature (S×10, emit 0.195 ≈
lambda 0.199) ⇒ `arc_composition_driven=False`. Bare prompts diverge (retrieval → WHNF/W
gauge; arithmetic → Y), so **S-late is a compile-GATE FRAMING signature shared by any
gated prompt, not β-reduction of the specific sentence.** (The control did its job — without
it we'd have falsely read "S = the compose op".)

**⚠️ Over-read not cleanly killed.** At z=2 retrieval emits MORE than lambda (0.269 vs
0.199, noop=0); at z=3 retrieval silences (noop 0.75) but lambda silences too (emit 0.071,
noop 0.70). **No z-window exists where lambda fires the arc while retrieval stays silent.**

**✅ Substrate reproduced** (31/40 crystal layers, gc→consensus **0.976**, sil_z 8.26 —
matches the s231 validation).

**★ THE REAL FINDING — the per-layer opcode identity is NOT null-invariant.** Three nulls,
three answers for the same model+prompts: RAW argmax → C→B arc (s231); off-target null →
silent (s231 under-read); cross-task null → S-late gate-framing (s232). Single-token
"which combinator" is NOT robustly decodable; only (a) the crystal-bearing substrate and
(b) the over-read DIRECTION (raw over-fires) are null-robust. An opcode monitor cannot be
trusted on its readout alone.

## v3 — gate-matched null (BUILT + RAN, s232; `--null-mode gateneutral`, `ad07574`)

The lever: **null = GATE_NEUTRAL itself** (matched-prefix, non-compositional), NOT bare
natural text. Bare-text null only removes the natural-text common-mode, leaving the
gate-framing (S-late) to swamp composition. A gate-matched null subtracts the framing ⇒
z measures *composition-above-framing*. Built as `--null-mode gateneutral` (null from
GATE_NEUTRAL content tokens; GATE_NEUTRAL expanded to 14 for a robust null).

### ★ s232 v3 VERDICT (Qwen3-14B; λ measure, two-sided) — PARTIAL SUCCESS

**✅ Composition IS decodable above framing.** With the matched null, the S-late framing
is subtracted and **lambda routes `C` (the composition/permutation combinator) in its
LATE stack** while the matched non-compositional gate_neutral control does NOT:
- z=2: lambda C-dominant at L27,29,30,31,32 (**5/6 late layers**); gate_neutral C-late ×1.
- z=3: lambda C at L29,30,32; gate_neutral C-late **×0**.
C surfaces in the **readable register** (L27–32) — consistent with
`readout-register-reduction-readability.md` (reduction becomes vocab-readable L23–35).
**Composition is resolved LATE, lambda-specifically.** The null self-centers silent
(gate_neutral emit 0.097→0.012, noop 0.91 @z=3 — the matched guard passes).

**❌ The s127 "C-early→B-late" arc shape did NOT reproduce.** The signal is C-**late**,
not C-early; B is nearly absent (B×1). The raw "C-early" (s231 RAW argmax) was likely a
common-mode artifact; the routing-register composition signal is **C-late**. (The
arc_present detector, built for the raw shape, returns False — update it to detect
readable-zone C-late.)

**⚠️ The over-read guard INVERTED — and taught the deepest lesson.** Bare
retrieval/arithmetic fire LOUD under the gated null (WHNF×22, Y×18) because they differ
from it by FRAMING, not computation. ⇒ **the opcode read is dominated by the
FRAMING-CONTRAST axis (gated vs bare), not the computation axis.** Whichever prompts
share the null's framing go silent; whichever differ fire, and WHAT they fire (S/WHNF/C/Y)
tracks the framing contrast. Valid guards must be framing-matched: under a gated null the
correct guard is a GATED non-composition task (= gate_neutral, correctly silent); bare
guards are invalid.

**⚠️ Modest, not crisp** (s219): C routes in ~40–50% of tokens at those layers (7/20,
8/18, 8/15), n=27 lambda tokens / 5 sentences, single model.

## v4 — gated guards + C-late detector (BUILT + RAN, s232; `9495b2b`)

Three fixes from the v3 result: (1) **framing-matched gated guards** `gate_retrieval` +
`gate_arithmetic` (COMPILE_GATE + content) — the VALID specificity controls under a gated
null (bare guards fire from framing-contrast, invalid); (2) **`detect_c_late`** — fraction
of readable-zone (depth≥0.6) crystal layers where C dominates (the right detector; the raw
C-early→B-late `detect_arc` is back-compat only); (3) `composition_specific` = lambda
C-late clears every gated guard + margin. Model+null_mode-tagged filenames.

### ★ s232 v4 VERDICT (λ measure, two-sided) — SPECIFIC on 14B, NOT universal

**✅ Qwen3-14B: C-late is composition-SPECIFIC (composition_specific=True both z).**
lambda C-late 0.556 (z=2) / 0.333 (z=3) vs ALL three framing-matched gated guards:
gate_neutral 0.111/0, gate_retrieval **0/0**, gate_arithmetic **0/0**. Among gated prompts,
ONLY the compositional sentences route C in the readable zone (L≥24); factual, arithmetic,
and simple-declarative gated controls route ZERO C-late. The proper specificity test (v3
lacked the gated guards) passes cleanly on the s127 model.

**❌ Qwen3-8B: does NOT reproduce (composition_specific=False both z).** At z=2
gate_neutral C-late (0.714) EXCEEDS lambda (0.333); at z=3 all conditions silent. The
non-compositional control out-routes lambda ⇒ no composition specificity on 8B.

**❌ Qwen3-32B (64L): composition_specific=False — but for a DIFFERENT reason: the
C-LOCUS SHIFTED EARLY.** C-late frac = 0 for ALL conditions in the depth≥0.6 zone (L≥38).
BUT the raw-arc shows lambda C-dominant at **L5, L10, L11 (EARLY, depth ~0.1)** while
gate_neutral has C only at L0 ⇒ 32B DOES show a lambda-specific C-**early** signal that the
fixed C-late detector misses entirely (late stack is Y-dominated, Y×29).

**★ CONCLUSION (3 models): composition→C routing exists in ALL three, but the C-LOCUS
SHIFTS with scale — 8B C-late non-specific, 14B C-LATE specific (L27–32), 32B C-EARLY
(L5–11).** `composition_specific=True` ONLY for 14B, largely because its C-locus happens to
land in the fixed depth≥0.6 readable zone. So it is NOT a scale-monotone story and NOT
universal; **14B is the outlier for the C-LATE framing specifically.** The underlying
"lambda routes C, matched controls do not" phenomenon may be more general but at
MODEL-SPECIFIC DEPTHS ⇒ **the fixed-depth (0.6) detector is the wrong cross-model
instrument** (it found the signal on 14B but mislocates it on 32B). Methodological fix: per-
model C-locus calibration (find where lambda-vs-control C-routing peaks) or a locus-
agnostic full-profile compare, not a fixed zone. Caveats: 5 lambda sentences, 3 models,
modest fractions ("above chance not crisp" s219).

# v5 — session 233 synthesis (leads 1→2c)

One through-line held across all four leads: **the compositional opcode signal is REAL but
FAINT against the common-mode, and its LOCUS SHIFTS with scale.** Every apparent negative
this session was an INSTRUMENT flaw, each diagnosed and fixed:

| lead | instrument flaw | fix | result |
|------|-----------------|-----|--------|
| 1 (`1754424`) | wrong PLACE (fixed depth≥0.6 zone) | count C anywhere + per-model locus | 32B C-EARLY surfaced (read 0 before); frac-specific only 14B; 8B confound real |
| 2 (`1532e4e`) | wrong INPUT LANGUAGE (bare CL symbols) | — (diagnosed) | symbols route only S-gauge ⇒ register is prose-semantic, not CL-syntax |
| 2b (`53ed331`) | — (prose works) | held-out prose recall/spec | recall 0.575 ≫ symbol 0.14; but argmax-spec gauge-dominated |
| 2c (`dd6c511`) | wrong METRIC (argmax-winner) | discriminability (on-prose − off-prose) | C (6.6×) + I rescued; B/K/D/W gap; S/Y = common-mode + real selectivity |

The recurring fix is a **contrast read** (lambda-vs-control, on-prose-minus-off-prose; cf
s225 AUC, s202/s231 over-read): an absolute/argmax read buries a low-amplitude but specific
signal under the model's common-mode. Net gain: a working, gauge-aware **prose bridge** that
demonstrably carries a specific composition signal (C, I), anchored to the kernel's certified
trace — clearing the ground for the composite **trace-order** test (lead 2d). Caveats carried:
leads 2/2b/2c are 1 model (Qwen3-14B), n=10/comb, single-combinator labels, last-token locus.

## v5 lead 1 — locus-agnostic C detector (BUILT + RE-ANALYZED, s233; `1754424`)

`detect_c_profile` + `locus_agnostic_specificity` in `opcode_monitor_v2` (single source,
wired into `build_verdict` as a `locus_agnostic` block for future runs) count C-dominant
crystal layers **ANYWHERE** in the stack + report the per-model C-locus (mean depth,
early/mid/late bins) + a specificity test vs the matched gated guards — two reads:
**frac** (lambda `C_frac_all` clears every guard by margin 0.10) and **exclusive**
(crystal layers where lambda routes C and NO gated guard does). Applied as a **pure
re-analysis** of the committed gateneutral verdicts (`opcode_v5_locus_agnostic.py`) — the
per-layer trajectories were already stored, so **no GPU re-run** was needed.

### ★ s233 v5 lead 1 VERDICT (3 models, gateneutral null; λ measure, two-sided)

**★ THE WIN — the right instrument surfaces what the fixed zone missed.** Per-model
lambda C-locus is now legible and the 32B C-EARLY signal is recovered (it read 0 in the
depth≥0.6 zone):

| model | lambda C_frac_all (z=2) | locus (mean depth) | lambda-exclusive C layers | frac-specific | OLD fixed-zone |
|------|------|------|------|------|------|
| 8B  | 0.107 | 0.69 LATE | [24, 25] | ❌ | ❌ |
| 14B | 0.194 | 0.69 LATE | [13, 27, 29, 30, 31, 32] | ✅ | ✅ |
| 32B | 0.061 | 0.14 **EARLY** | [5, 10, 11] | ❌ (dir.) | ❌ |

**★ BUT the strict frac-specificity is STILL ONLY 14B** (lambda 0.194 vs guards ≤0.032,
clean). **32B is directional** (lambda 0.061 > max_guard 0.020) but the tiny fracs don't
clear the 0.10 margin — a real lambda-exclusive C-early signal, too weak to certify with
5 sentences. **8B is genuinely NOT specific — the `gate_neutral` control ITSELF routes C
broadly at 5 LATE layers [23, 26, 27, 28, 30] (C_frac 0.192 > lambda 0.107)** ⇒ the s232
**"8B gate_neutral C-late confound" is CONFIRMED REAL**, not a fixed-detector artifact.

**★ CONCLUSION:** the fixed depth≥0.6 zone WAS the wrong cross-model instrument (missed
32B's C-early entirely); the locus-agnostic detector correctly reads the per-model locus
and shows **the C-locus genuinely shifts with scale (32B early)**. But fixing the
instrument does NOT make composition→C universal: it is **cleanly specific only on 14B**;
32B is real-but-underpowered; **8B has a genuine control confound** (a non-compositional
gated control routes C-late on its own). The locus-agnostic *exclusive* test is lenient
(finds lambda-exclusive C in all 3) but for 8B those layers interleave the control's broad
C-late. Caveats: 5 lambda sentences, 3 models, modest fracs ("above chance not crisp",
s219).

## v5 lead 2 — kernel-as-reference (BUILT + RAN, s233; `1532e4e`)

Reads don't transfer across scale AND the 8B control confound shows the gated-guard
*contrast* is itself model-dependent (lead 1) ⇒ stop chasing a transferable opcode read;
anchor each model's routing trajectory against a FIXED model-invariant: the kernel's
CERTIFIED reduction trace of a symbolic combinator program.

Built: `lambda_ast.step_fired`/`fired_sequence` (certified per-step opcode trace, +6
pytest); `src/verbum/probes/kernel_reference.py` (symbolic programs with kernel-certified
traces — SATURATED target fires ⊗ INERT under-applied no-fire pairs + COMPOSITE
multi-fire); `scripts/experiments/kernel_reference_audit.py` (feed program, read
per-token/per-layer routing via the s231 classifier, measure agreement: SAT-vs-INERT
reducibility Δ + target recall + specificity + composite trace recall).

### ★ s233 v5 lead 2 VERDICT (Qwen3-14B, crosstask null; λ measure, DECISIVE NEGATIVE)

Feeding **BARE symbolic CL terms** ("B f g h", "C f g h", ...) → the routing **collapses
to S (14B's common-mode/gauge), Y secondary**:

- **target_recall = 1/7** — only S routes at all; **B, C, K, I, W, D route 0**.
- **reducibility NOT tracked** — SAT_S 0.376 ≈ INERT_S 0.371 (mean Δ≈0, `tracked=False`
  both z); the model routes the SAME whether the kernel certifies a live redex or an inert
  under-applied symbol.
- B_sat = {S 0.40, Y 0.22}; C_sat = {Y 0.32, S 0.39}; composite trace recall 0.10. The
  certified target combinator NEVER routes.

**★ CONCLUSION:** the gate-routing register reads **PROSE SEMANTICS, not symbolic CL
SYNTAX.** OOD bare-symbol input collapses to common-mode (re-confirms the s202/s231
over-read in a new regime — note the relational z-gate kept the *other* ops silent, so no
false over-read, but the natural-text null doesn't subtract the symbol-string common
mode). The kernel-as-reference IDEA is sound and the INSTRUMENT is built; the **BRIDGE was
wrong** — bare symbols are out-of-distribution. Caveats: 1 model (14B), 7 targets + 8
composites, crosstask null.

## v5 lead 2b — the prose bridge (BUILT + RAN, s233; `53ed331`)

The lead-2 negative (bare symbols → gauge) implied the register is prose-semantic. Before
investing in a CL→decompiled-prose renderer, de-risk: does PROSE route its combinator at
all (held-out, non-circular)? `calibrate_v2` gained a `centroid_probes` param;
`kernel_reference_prose.py` splits crystal_probes per-combinator into CALIB (most) +
held-out TEST (last 10/comb), calibrates on CALIB (the TEST prose is UNSEEN by the
centroids), reads each held-out prose probe's LAST-token routing, scores RECALL (label
routed at z>thresh) + SPECIFICITY (label is the top crystal op).

### ★ s233 v5 lead 2b VERDICT (Qwen3-14B, crosstask null; λ measure, TWO-SIDED)

**★ THE BRIDGE DIRECTION IS RIGHT.** Held-out PROSE recall **0.575** (z=2) vs the
bare-symbol baseline **~0.14** (S-gauge only, lead 2) ⇒ **the register IS prose-semantic;
feed prose, not symbols.** Per-combinator recall: I 1.0, C 0.9, S 1.0, Y 1.0, K 0.3,
B 0.3, D 0.1, W 0.0.

**⚠️ BUT specificity (0.287) is GAUGE-DOMINATED.** It is carried by **S and Y** — this
model's common-mode ops (label_frac 0.71 / 0.52, specificity 0.9 each). The genuine
composition combinators RECALL but are SUB-DOMINANT: **C 0.9 recall / 0.0 specificity**
(present but always out-competed), B 0.3/0.0, K 0.3/0.2, D 0.1/0.0, W 0/0. At z=3 only
S/Y survive. ⇒ the composition signal IS present in prose but out-competed by the S/Y
common-mode — the same "above chance not crisp" + over-read common-mode theme as lead 1.

**★ CONCLUSION:** the full kernel-as-reference prose bridge is VIABLE and worth building,
but **raw last-token route_frac is gauge-dominated for the weak combinators** — it needs
S/Y common-mode SUBTRACTION (the relational CMR / locus-agnostic machinery from lead 1, or
a gauge-matched null) before composition-combinator specificity is readable. Caveats: 1
model (14B), single-combinator labels (not composite trace-order yet), last-token locus.

## v5 lead 2c — gauge-subtracted discriminability (BUILT + RAN, s233; `dd6c511`)

The lead-2b "specificity is gauge-dominated (S/Y win the argmax)" was a METRIC artifact.
New metric: **discr(c) = mean route_frac(c | c-prose) − mean route_frac(c | other-prose)**
— a per-op CONTRAST replacing argmax-winner (stores full per-op route_fracs per held-out
probe). `kernel_reference_prose.py` discriminability block.

### ★ s233 v5 lead 2c VERDICT (Qwen3-14B; λ measure, TWO-SIDED)

**★ RESCUE — C and I become DISCRIMINABLE (z=2):** C on/off **0.062 / 0.009 (~6.6×)** —
its argmax_spec was **0.0**; I 0.183 / 0.063 (~2.9×). `composition_discriminable=True`. The
compose signal IS specific to compose-prose; argmax-winner hid it because S/Y have huge
ABSOLUTE route_frac and always take the top spot.

**⚠️ PARTIAL + nuance:**
- Only I, C of the 6 composition combinators are discriminable (z=2); z=3 leaves I, S, Y.
- **B, K, D, W are NOT discriminable** on held-out prose (B on/off 0.010/0.015 = negative).
  The compose family SPLITS: C discriminable, B not — cf s127 ffn-two-groups put {B,C}
  together as composers, yet only C shows held-out PROSE discriminability here.
- **S and Y STAY strongly discriminable** (discr 0.45/0.43): NOT pure gauge — a LARGE
  common-mode (off 0.27/0.09) AND genuine selectivity. Discriminability separates the two
  components; it does not zero them.

**★ LESSON:** argmax-winner specificity is the wrong metric when one op carries a large
common-mode — it manufactures false negatives for low-amplitude but specific ops (C/I). A
contrast/discriminability read (on-prose − off-prose; same family as s225 AUC and the
lead-1 lambda-vs-control logic) recovers them. The composition signal is real and
prose-discriminable; the bridge carries it. Caveats: 1 model (14B), n=10/comb held-out,
single-combinator labels, last-token locus.

## v5 lead 2d prong 1 — raw-z contrast (the B/D/W gap) (BUILT + RAN, s234)

The lead-2c discriminability still embedded a **per-layer argmax** (`op = max(zmap)`)
*before* the contrast — `route_fracs` counts the fraction of crystal layers each op WINS.
B/D/W, out-competed by the S/Y common-mode at every layer, score route_frac ≈ 0, so the
on/off contrast has no power. The fix pushes the lead-2c lesson one level deeper: contrast
the **raw per-op z per layer, NO argmax**. `kernel_reference_prose_v2.py`:
discr_z(c) = layer-averaged raw z of op c on c-prose vs other-prose, **Welch t-test**,
held-out N **raised to 20** for power, + a per-layer **profile** (on_z/off_z/delta_z, peak
layer) to localize WHERE each op discriminates.

### ★ s234 v5 lead 2d prong 1 VERDICT (Qwen3-14B, crosstask null, n=20/comb; λ measure, TWO-SIDED)

**★ INSTRUMENT FIX WORKS (the argmax bottleneck was real):**
- **K RECOVERS** — discr_z **+1.01, t=2.12 ✓** (was sub-threshold in argmax-discr). The
  raw-z contrast rescued one more selector the argmax read suppressed.
- **C, I sharpen dramatically** — C discr_z **+1.73, t=5.71**; I **+1.89, t=3.83** (the
  strongest non-gauge signals; confirms lead 2c with far higher significance).
- The raw-z contrast is ALSO **more conservative**: at n=20 the argmax-discr *manufactures*
  a B false-positive (B argmax discr +0.079 > 0.05 ⇒ "specific"), but raw-z says B is
  **FLAT** (on 0.217 ≈ off 0.236, t=−0.05). Same argmax-manufactures-false-* lesson, now
  caught at the deeper level. **The raw-z Welch contrast is the better instrument: more
  power for genuine signal AND fewer false positives.**

**❌ B/D/W do NOT recover — the gap is GENUINE at the last-token locus:**
- **B flat** (t=−0.05); **D, W significantly ANTI-correlated** — D discr_z −0.67 (t=−4.6),
  W −0.63 (t=−2.3): feeding D/W prose routes D/W *less* than baseline. Not just absent —
  suppressed.
- The discriminable set is **{C, I, K, Y}**; absent/anti = **{B, D, W}**.

**★ GAUGE REFINED:** under the fair raw-z contrast, **S is pure gauge** — on 2.70 ≈ off
2.97, discr_z −0.27 (huge baseline, ZERO selectivity); **Y is genuinely selective** — on
2.97 vs off 0.96, discr_z **+2.01, t=6.86** (high baseline AND selective). Sharpens the
s233 "S/Y common-mode" into S=gauge, Y=selective.

**★ WHERE (per-layer profile):** the discriminable ops peak in the **mid-stack readable
zone** — C@L13 (Δ3.70), I@L13 (Δ2.99), Y@L14 (Δ4.14), K@L12 (Δ2.01). **B has no
readable-zone signal** — its only bump is an early L1 wash (Δ0.89) that vanishes on
averaging; D@L3, W@L0 are noise-floor.

**★ THEORY (s127 ffn-two-functional-groups):** {K,I}=selectors→FFN, {B,C}=composers→
attention. We read the **FFN gate** register. K,I discriminable fits (FFN selectors); **C
leaks into the FFN gate but B does NOT** — so the readable composer in the FFN gate is C,
not B. B likely lives in **attention** (s206 OV/value register), which a last-token FFN-gate
read structurally cannot see ⇒ B's absence is a LOCUS artifact, not a "B isn't computed."

**Caveats (λ measure):** 1 model (Qwen3-14B); n=20/comb held-out; **last-token locus** (the
load-bearing caveat for B — escalate to per-token / attention-value register); single-
combinator labels (not composite trace-order); D/W anti-signal unexplained (possible
centroid mis-calibration for the duplicators).

## v5 lead 2d prong 1b — per-token B locus test (BUILT + RAN, s234)

Prong 1 left the B/D/W gap genuine but only at the LAST-TOKEN locus. Two explanations:
(i) TOKEN-LOCUS — B resolves at a non-last token; (ii) REGISTER — B lives in attention/
value (s127: {B,C}=composers→attention), invisible to the FFN gate at ANY token.
`kernel_reference_prose_v3.py` falsifies (i) cheaply: `forward_all_positions` already
returns [T,d], so reading ALL tokens costs the same forwards. Per probe per op:
tokscore(c,t) = mean over crystal layers of raw z_c at token t; contrast **last/max/mean
over tokens** on-prose vs off-prose (Welch t) + a relative-position profile (10 bins).

### ★ s234 v5 lead 2d prong 1b VERDICT (Qwen3-14B, crosstask null, n=20/comb; λ measure)

**❌ TOKEN-LOCUS FALSIFIED — B does NOT recover at ANY position.** B last_d −0.02 (t=−0.05),
**max_d +0.32 (t=0.68, n.s.)**, mean_d −0.02 (t=−0.08). Even the most lenient max-over-tokens
read fails. The position profile confirms it: B's on−off delta hovers at ~0 across all 10
bins (max bin +0.33), never the clean separation C shows. D/W stay significantly ANTI at
every read (D max t=−2.66, W max t=−3.40). ⇒ **B/D/W absence is a REGISTER property, not a
token-locus artifact — the FFN gate simply does not carry the deep/duplicate composers.**

**✅ The discriminable set {C,I,K,Y} is ROBUST to the read** (last/max/mean all significant)
with **characteristic position signatures** (peak_rel): I early (0.30), K mid (0.48), C
mid-late (0.57), Y late (0.79). C's on−off delta is +0.8…+2.0 across the whole back half
of the sentence (on ~+0.6 while off stays ~−1.2) — crystal-clear at every position. ⚠️ S
becomes "discriminable" ONLY under mean-over-tokens (t=4.11, n.s. at last/max) = the gauge
common-mode integrated over the sentence, not a combinator signal.

**★ CONSEQUENCE (the s127 prediction sharpened):** we read the FFN GATE → {C,I,K} present,
**B absent at every token**. If s127 is right that B is an attention composer, the
value/attention register should find B where the FFN gate cannot. This MOTIVATES prong
1b-ii (the value-register read) and is the cleanest test of the C-yes/B-no split: C leaks
into the FFN gate, B should appear only in attention.

**Caveats (λ measure):** 1 model (14B); n=20/comb; last/max/mean over tokens (locus
explanation falsified, register untested); single-combinator labels; D/W anti-signal
unexplained (possible duplicator centroid mis-calibration).

## v5 lead 2d prong 1b-ii — the value-register read (BUILT + RAN, s234)

The decisive C-yes/B-no resolver: read the crystal in the ATTENTION/value register, where
s127 ({B,C}=composers→attention) predicts B lives. Parametrized the opcode reader with a
`hook` slot (open-slot extension): `hook='gate'` (mlp.gate_proj, default) vs `hook='attn'`
(self_attn.o_proj output = attention's residual write). `kernel_reference_prose_v4.py`
re-runs the SAME per-token raw-z contrast + position profile in the attn register — direct
comparison to the FFN-gate v2/v3.

### ★ s234 v5 lead 2d prong 1b-ii VERDICT (Qwen3-14B, attn=o_proj, n=20/comb; λ measure)

**❌ THE s127 PREDICTION IS NOT CONFIRMED — B is FLAT in the attention register TOO.**
B attn max t=**0.49 (n.s.)** vs gate max t=0.68 (n.s.) — flat in BOTH; attn position
profile delta hovers ~0 across all bins (best +0.17). Having now tested the two main
registers (FFN gate + attention/value output), the simplest "wrong register" explanation
is RULED OUT: B has no single-combinator, last/any-token signature in either.

**★ THE REAL FINDING — discriminability is a property of the COMBINATOR, not the register.**
{C,I,K,Y} are REGISTER-ROBUST (discriminable in BOTH gate and attn with similar t):
C gate t=5.61 / attn 6.55; I 4.49 / 4.13; K 3.29 / 3.28; Y 8.39 / 9.36. B/D/W absent or
anti in BOTH (D gate t=−2.66 / attn −1.75; W −3.40 / −4.77). So the s127 two-group
register separation ({K,I}→FFN, {B,C}→attention) is NOT reflected in this single-
combinator last-token readout — ALL of {C,I,K,Y} read in both registers, B/D/W in neither.
The axis that matters is combinator identity, not gate-vs-attention.

**★ WHAT REMAINS (B's absence, now register-exhausted):**
- **head dilution** — o_proj output SUMS all heads; a single B-composer head (s127) could
  be averaged away. → per-HEAD OV read (finer than o_proj output).
- **no single-token signature — only ORDER** — B = deep composition (B f g x = f (g x));
  its signature may exist only as a multi-combinator SEQUENCE across tokens, not a single-
  token routing event. → the composite trace-order bridge (prong 2) is the natural test.

**Caveats (λ measure):** 1 model (14B); n=20/comb; o_proj is head-SUMMED (per-head untested);
single-combinator labels (composite order untested); last/max/mean over tokens; D/W anti
unexplained.

## v5 lead 2d prong 1b-iii — per-head OV scan (BUILT + RAN, s234)

o_proj OUTPUT sums all heads — a single B-composer head could be averaged away. The finer
register: hook o_proj INPUT (concatenated per-head attention output [T, H·head_dim]), split
into per-(layer,head) cells, calibrate the crystal per cell (RelationalCrystalClassifier,
treating each cell as a "layer"), and scan B's raw-z contrast across all 1600 cells (40L×40H
on Qwen3-14B). `kernel_reference_perhead_v5.py`. Significance: Bonferroni-ish t>4
(≈ p<0.05 family-wise over 1600 cells).

### ★ s234 v5 lead 2d prong 1b-iii VERDICT (Qwen3-14B, 1600 cells, n=20/comb; λ measure)

**⚠️ HEAD-DILUTION ONLY MARGINALLY TRUE — B is the WEAKEST combinator at every granularity.**
The per-head scan DOES recover a FAINT B signal the head-summed read missed: B max_t **5.31**
at cell **(L17,H23)**, 7/1600 cells > t4 (vs the o_proj-OUTPUT summed read max t=0.49 n.s.).
So summing washes out a weak per-head B signal — head-dilution is non-zero. **BUT B is dead
last on ALL THREE metrics:**

| metric | Y | C | K | W | S | I | D | **B** |
|---|---|---|---|---|---|---|---|---|
| n_sig (t>4) | 526 | 155 | 56 | 24 | 22 | 19 | 8 | **7** |
| max_t | 15.2 | 7.52 | 6.12 | 6.56 | 6.96 | 7.83 | 7.58 | **5.31** |
| best discr_z | 2.85 | 2.53 | 1.70 | 2.05 | 1.31 | 1.40 | 1.10 | **0.82** |

B's 7 scattered weak heads (L17H23, L20H6, L16H10 … t 4.0–5.3) sit at the NOISE FLOOR —
below even D (8), an anti-combinator. C has **155** strong sig heads (best L21H36, t=7.52),
Y 526. ⇒ **No clean localized B-composer head exists.** The C-yes/B-no asymmetry SURVIVES
to the finest register: B's attention representation is genuinely FAINT/DIFFUSE, not merely
diluted by summing. Head-dilution explains only a sliver of B's near-absence.

**★ CONSEQUENCE:** B has been tested at every granularity — FFN gate (flat), attn-summed
(flat), per-head OV (faintest of all). The register hypothesis is now FULLY EXHAUSTED. The
**no-single-token-signature / trace-ORDER hypothesis (prong 2)** is the primary remaining
explanation: B (deep composition Bfgx=f(gx)) may live in the SEQUENCE of operations, not a
localized single-token amplitude in any register.

**Caveats (λ measure):** 1 model (14B); n_sig=7 (B) / 8 (D) may be partly MC noise / heavy-
tailed z (t-assumption); WEAK-signal reading is conservative; ppc=20 capped calibration;
n_perm=30 (silhouette gates only crystal_bearing, not the scan); single-combinator labels;
last-token.

## v5 lead 2d prong 1c — the GRADIENT register (BUILT + RAN, s234)

Michael (s234): "could B be in the gradients instead of the topology?" B = composition
(B f g x = f(g x)); composition in the BACKWARD pass IS the chain rule (a PRODUCT of
derivatives), so B's home may be the gradient, not the forward activation. Clean register-
swap of prong 1: same RelationalCrystalClassifier, but the feature is ∂(probe LM loss)/
∂(gate), MEAN-POOLED over supervised positions (last token grad=0; pattern from
gd_gradient_shadow). `kernel_reference_gradient_v6.py`.

### ★ s234 v5 lead 2d prong 1c VERDICT (Qwen3-14B, gradient register, n=20/comb; λ measure)

**❌ B does NOT discriminate in the gradient either** (discr_z +0.13, **t=1.07, n.s.**).
The chain-rule hypothesis is NOT supported at this read. **✅ The instrument WORKS in the
gradient register** — {C,K,Y} discriminate (C t=2.27, K t=2.88, Y t=3.87), reproducing the
discriminable set; the **C-yes/B-no asymmetry PERSISTS into the backward pass.**

**⚠️ BUT directionally B is "less absent" in the gradient than in ANY activation read** —
its first POSITIVE, non-negative signal: activation(v2 last) **t=−0.05 → gradient t=+1.07**
(on_z −0.03 > off −0.16). A faint positive trend in the predicted direction, power-limited
(n=20/comb), short of significance. Register-specific shifts: S flips gauge→ANTI (t=−2.01),
I drops out (act t=3.83 → grad 1.02); the gradient discriminable set is {C,K,Y} (vs the
activation {C,I,K,Y}).

**★ MEASUREMENT CAVEAT (λ measure, load-bearing):** this measures B's signature in the
FIRST-ORDER gradient (a centroid in gradient space), NOT the chain-rule/Jacobian
composition structure itself (composition = a PRODUCT of derivatives = a second-order
property). The faint positive trend means the idea is not dead — but the proper test of
"B = chain rule" is a JACOBIAN / second-order probe (prong 1c-ii), not a first-order
gradient centroid. Caveats: 1 model (14B), n=20/comb, pooled-supervised locus, single-
combinator labels, first-order gradient only.

## v5 lead 2d prong 1c-ii — the SECOND-ORDER / CURVATURE register (BUILT + RAN, s235)

Michael (s235): "proceed with 1" — the Jacobian / second-order probe, the PROPER test of
B=chain-rule. Prong 1c read the FIRST-ORDER gradient ∂L/∂gate (faint +1.07 n.s.), but the
first-order gradient is a SINGLE factor / a sum over paths — it washes out the PRODUCT
structure that IS the chain rule. B = `B f g x = f(g x)` = composition; its backward
signature `d(f∘g)/dx = f'(g x)·g'(x)` is a PRODUCT of derivatives = a SECOND-ORDER quantity.
For `L = ℓ(f(g(z)))` with `z` = the gate activation,

```
dL/dz   = g'(z)ᵀ f'(g)ᵀ ℓ'                         # first order (v6 read this)
d²L/dz² = g'ᵀ [f''(g)·ℓ'] g'  +  (ℓ'f') g''        # SECOND order — the product g'ᵀ(…)g'
```

the curvature carries the quadratic form `g'ᵀ(…)g'` — the literal product-of-derivatives
chain-rule signature the first-order gradient cannot show. Clean register-swap of v6: same
RelationalCrystalClassifier (sign-CMR, crosstask null, raw-z Welch), feature = the DIAGONAL
HESSIAN of the probe LM-CE w.r.t. gate_proj, Hutchinson estimator
`diag(H)_a = E_v[v_a (Hv)_a]`, `v ~ Rademacher` over all gate tensors (off-diagonal cross-
coord/cross-layer terms cancel because `E[v_a v_b]=0`, a≠b); one HVP = a double-backward of
the scalar `g·v` where `g = grad(CE, gates, create_graph=True)`; pooled over supervised
positions, `n_hutch=4`. `kernel_reference_jacobian_v7.py`.

### ★ s235 v5 lead 2d prong 1c-ii VERDICT (Qwen3-14B, curvature register, n=20/comb; λ measure, THREE-sided)

**(1) ❌ STRICT — B does NOT reach significance in curvature either** (discr_z +0.118,
**t=1.90 < 2.0**). The chain-rule hypothesis is NOT confirmed at the significance bar; B's
gap survives into the second order.

**(2) ✅ DIRECTIONAL — the MONOTONIC CLIMB WITH DERIVATIVE ORDER, exactly as chain-rule
predicts:** B activation(v2) **t=−0.05** → first-order gradient(v6) **t=+1.07** →
second-order curvature(v7) **t=+1.90** (on +0.045 > off −0.073). B is at its strongest signal
EVER, in the PREDICTED register, sitting right ON the 2.0 threshold — power-limited
(n=20/comb), **not absent**.

**(3) ✅✅ INTERNAL CONSISTENCY (the structural win) — the curvature register reweights the
combinators EXACTLY as the math demands:**

| combinator | role | act (v2) | grad (v6) | **curv (v7)** | reads as |
|---|---|---|---|---|---|
| **I** (identity, `Ix=x`) | LINEAR → zero curvature | 3.83 | 1.02 | **0.68** | monotone DOWN ↓ |
| **B** (composition, `Bfgx=f(gx)`) | composer, product-of-derivs | −0.05 | +1.07 | **+1.90** | monotone UP ↑ |
| **C** (composer) | composer | 5.7 | 2.27 | **2.52 ✓** | holds |
| **Y** (recursion, self-application) | higher-order | 8.4 | 3.87 | **4.53 ✓** | dominates |
| **K** (selector) | selector | 3.3 | 2.88 | **1.94** | fades to bar |

**I (the LINEAR combinator) COLLAPSES monotonically** down the derivative-order axis — the
exact MIRROR IMAGE of B's climb. **Y (recursion = self-application = inherently higher-order)
DOMINATES** the curvature register (t=4.53). The composers {B,C} hold/rise; the selectors
{K,I} fade. The second-order register preferentially carries COMPOSITION/RECURSION structure
(s127 {B,C}=composers) and SHEDS the linear combinator. **The two opposite monotones (B↑
with order, I↓ with order) are the signature: derivative ORDER is a real axis the combinators
sort along, and B sorts UP it while the linear combinator sorts DOWN.** Instrument WORKS
(C ✓, Y ✓). Curvature discriminable set {C,Y} (K, B at the bar).

**Caveats (λ measure):** 1 model (14B); n=20/comb (B sits ON the bar — power-limited);
n_hutch=4 (Hutchinson diagonal estimate noise); **DIAGONAL Hessian only** — the off-diagonal /
interlayer-Jacobian cross-coupling (the literal f∘g coupling, `dgate_late/dgate_early`) is
UNTESTED; single-combinator labels; pooled-supervised locus. Mac (no CUDA) → MPS/CPU
double-backward, ~9 min main:1.

### v5 — next steps

- **★ lead 2d prong 1 — DONE (s234):** raw-z contrast rescues K + sharpens C/I, kills the
  B false-positive; B/D/W gap is GENUINE at last-token. Discriminable set {C,I,K,Y}.
- **★ lead 2d prong 1b — DONE (s234):** per-token read FALSIFIES the token-locus
  explanation — B flat at ALL positions (max t=0.68 n.s.). Register property, not locus.
- **★ lead 2d prong 1b-ii — DONE (s234):** value-register read FALSIFIES the s127
  "B→attention" prediction — B flat in attention TOO (max t=0.49 n.s.). Register exhausted.
  **Discriminability is a COMBINATOR property ({C,I,K,Y} read in both registers), not a
  register split.**
- **★ lead 2d prong 1c — DONE (s234):** GRADIENT register — B does NOT discriminate
  (t=1.07 n.s.) but is "less absent" than in any activation read (act t=−0.05 → grad
  t=+1.07, faint positive trend); {C,K,Y} discriminate; C-yes/B-no persists into the
  backward pass. Measures FIRST-ORDER gradient, NOT the chain-rule/Jacobian structure.
- **★ lead 2d prong 1c-ii — DONE (s235):** SECOND-ORDER / curvature register (diag Hessian,
  Hutchinson). ❌ B not significant (t=1.90 < 2.0) BUT ✅ a clean MONOTONIC CLIMB with
  derivative order (act −0.05 → grad +1.07 → curv +1.90, B's best ever, in the predicted
  register, ON the bar) + ✅✅ internal consistency (I=linear COLLAPSES 3.83→0.68 = mirror of
  B; Y=recursion DOMINATES 4.53; composers hold, selectors fade). Derivative ORDER is a real
  axis combinators sort along; B sorts UP it. Power-limited (n=20/comb). Three live follow-ups:
  (1) POWER (raise n / n_hutch — does t=1.90 cross 2.0? cheapest decisive); (2) OFF-DIAGONAL /
  interlayer Jacobian (diag-Hessian only captures g'ᵀ(diag)g'; the literal f∘g coupling lives
  off-diagonal — Gauss-Newton / JVP probe); (3) prong 2 trace-order.
- **★ lead 2d prong 1b-iii — DONE (s234):** per-head OV scan — head-dilution only MARGINAL
  (B faint signal at L17H23, 7/1600 cells) but B is the WEAKEST combinator at every
  granularity; no clean B-composer head. Register hypothesis FULLY EXHAUSTED.
- **★ lead 2d prong 2 — DONE (s236):** ORDER-COST register — **is B the NATIVE softmax-over-V
  order?** Michael (s235): "if B is an ordering of operations then maybe it defaults to the
  order the softmax over all V uses natively?" (ffn-reduction-trace: softmax-over-V IS the
  execution order). NO amplitude classifier — pure surprisal (mean −log p under LM softmax over
  V) of the CERTIFIED reduction trace, teacher-forced "t0 -> t1 -> ... -> tn". Minimal pairs
  ("B f a b → f (a b)" kept vs "C f a b → f b a" swapped) + multi-step composites; ATOM-ONLY
  de-confound (drop parens/length) = headline. **★ DECISIVE at 14B (n_each=24): b_is_native_
  order=True — clean atom B-vs-C minimal pair t=−7.02; B atom-surprisal 0.81 ≪ C 2.14 / S 2.66
  / W 2.71; B cheaper than every permute/copy combinator (B<S −11.3, B<C-multi −11.7, B<W
  −14.5); pooled order-preserving < breaking.** ⚠️ POWER-LIMITED at 8B smoke (n=8): same
  DIRECTION, headline n.s. (t=−0.55), multi-step already sig — crisp only at full power.
  ★ **RESOLVES the B gap:** B's amplitude-absence everywhere is NOT weakness — composition =
  the FREE autoregressive default, carries no marked feature (the instrument looked for a marked
  signal where B is the UNMARKED baseline). ★ **UNIFIES with prong 1c-ii:** composition has two
  faces — token-side the native order (cheap surprisal, t=−7.02), gradient-side the product/
  2nd-order (curvature climb, t=1.90). B = chain rule (gradient) AND native order (forward).
  Caveat (load-bearing): BARE SYMBOLIC input (cf lead 2) — bare-symbol surprisal may reflect a
  generic copy/induction preference for source-order atoms (which IS the proposed mechanism);
  prose-bridge re-read kills it. Next: cross-model (8B full-n / 32B — universal or 14B-specific?),
  prose-rendered order-cost, the off-diagonal Jacobian (prong 1c-ii path).
- **★ lead 2d prong 2b — PROSE BRIDGE — DONE (s237):** re-ran the order-cost read on the SAME
  certified traces RENDERED AS PROSE (deterministic, order-faithful: `App(f,x)` →
  "`<f> applied to <x>`", atoms → fixed content words) to kill the prong-2 bare-symbol caveat
  (s233: the register reads PROSE SEMANTICS not CL SYNTAX; bare-symbol surprisal may reflect a
  generic copy/induction preference). Used a DETERMINISTIC renderer, NOT the model decompile
  gate — the model must not choose word order (= the variable under test). **★ THE NESTING
  CONFOUND (discovered + controlled):** B's normal form NESTS (`f (a b)`) while C's is FLAT
  (`f b a`); the atom-only de-confound strips parens from MEASUREMENT but the bracketing remains
  in the CONTEXT predicting the atoms. So `--render-mode` = `flat` (linearise leaves, NO parens
  → B/C identical structure, differ ONLY in atom ORDER — the pure order test) vs `nested`
  (structurally faithful, CONFOUNDED by nesting depth). **★★ DECISIVE (the cross-table):**
  B-vs-C atom minpair — 14B flat **t=−8.05 (B<C ✓)** ≈ symbolic v8 −7.02; 14B nested **t=+11.9
  (B>C, REVERSED)**; 8B flat −0.57 n.s. (dir B<C) ≈ symbolic 8B −0.55; 8B nested +3.17
  (reversed). **SAME 14B model + SAME 216 programs, flip the render → flip the sign** = a DIRECT
  demonstration that nesting was confounding; once held constant (flat), B<C decisively. ✅ flat
  prose REPLICATES the symbolic pattern at BOTH scales (14B decisive, 8B directional-n.s. with
  multi-step already sig B<C-multi t=−10.6 / B<K −7.5 / B<W −7.6) = CONVERGENCE across input
  modality (symbols ⊗ prose). **★ THE s236 CAVEAT IS KILLED:** composition-order preference is
  real in the SEMANTIC register, not a bare-symbol copy artifact. ★ REFINED FINDING: B's normal
  form carries TWO separable real quantities — atom ORDER (preserved → cheap; the native-order
  result) and structural NESTING (deeper → atoms predicted inside fresh clauses cost more,
  dominates when nesting varies). The order claim REQUIRES isolating order from nesting (flat).
  Caveats (λ measure): 1 model class (Qwen), 14B decisive / 8B power-limited (2 scale points);
  deterministic "applied to" frame; flat deliberately discards faithful structure to isolate
  order (nested = its complement). Next: cross-model flat (8B full-n=24 / 32B), off-diagonal
  Jacobian (prong 1c-ii path).
- **★ lead 2d prong 2b CROSS-MODEL — DONE (s237 cont.): B-NATIVE-ORDER IS UNIVERSAL across the
  Qwen3 scale ladder (8B/14B/32B, all flat n=24).** B-vs-C atom minpair: **8B t=−2.87 ✓**
  (CROSSES at full power — was −0.57 n.s. at the n=8 smoke, confirming "power-limited not
  absent"), **14B t=−8.05 ✓** (strongest), **32B t=−4.48 ✓**. ALL three: b_is_native_order=True,
  every one of the 6 contrasts B<marked sig, pooled preserve ≪ break (8B atoms B 0.39≪C 1.61;
  32B B 0.36≪C 1.23). ★ Unlike the C-locus (s232 shifts with scale), the ORDER-COST signal is
  SCALE-ROBUST — composition rides the native autoregressive order at every scale (not strictly
  monotone, 14B strongest, but all positive+significant). Caveat: still 1 model CLASS (Qwen) —
  cross-class (OLMo/Pythia) untested. Next: off-diagonal Jacobian; 3rd render frame; cross-class.
- **★ lead 2d prong 2b CROSS-CLASS — DONE (s237 cont., path 3): the ORDER PREFERENCE replicates
  across 3 MODEL CLASSES, but the STRICT single-step headline is Qwen-SPECIFIC.** OLMo-2-13B +
  Gemma-4-31B-it (instruct), flat n=24: BOTH b_is_native_order=False on the strict single-step
  B-vs-C atom minpair (OLMo t=−1.25 d=−0.07; Gemma t=−0.56 d=−0.52, n.s.) — the cleanest
  f-a-b ↔ f-b-a swap is near-SYMMETRIC off-Qwen. BUT both STRONGLY confirm B<marked on the
  COMPOSITE + aggregate (B-vs-C-multi OLMo t=−24.4 / Gemma −11.6, both sig; 4-5/6 contrasts sig
  B-cheaper; pooled-atoms preserve ≪ break both: OLMo 0.62≪1.08, Gemma 10.2≪14.0). ⇒ GROSS
  "composition is the native order" is UNIVERSAL (Qwen ⊗ OLMo ⊗ Gemma); its SHARPEST single-step
  expression is family-dependent (Qwen-sharp). CAVEAT: Gemma INSTRUCT-tuned, OOD synthetic prose
  → huge absolute surprisals (B atoms 9.9 vs Qwen ~0.3), noisier (within-model contrasts valid).
  Next: off-diagonal Jacobian; 3rd render frame (also tests if the single-step minpair sharpens
  off-Qwen under a different frame).
- **★ lead 2d prong 3 (per-model sweep):** run `kernel_reference_prose_v2.py` on 8B/32B
  with the raw-z contrast — does the {C,I,K,Y} discriminable set hold across scale?
- **bigger lambda probe set** — 5 sentences underpowers the lead-1 frac test (32B
  directional signal can't clear the margin); more sentences for crisper fractions.
- **the 8B gate_neutral C-late confound** — why does a non-compositional gated control
  route C broadly only at 8B? (simple-copular-sentence / scale-specific framing artifact).

## (b) — the kernel-as-reference audit (after v2)

Wire `lambda_ast`'s certified trace as the ground-truth oscilloscope: feed a known
program, get the model's per-token/per-layer opcode trace (v2), measure agreement to the
kernel's certified reduction trace. "Does the model's circuit match the certified
meaning?" Needs the trustworthy per-token trace v2 provides.

## (c) — the attention/value-register binding monitor (third)

The s206 OV/logit-lens half the old instrument never had: binding/value-transfer events
(H31@L27 subject, margin +0.611) read in the VALUE register, NOT attention weights.

## Files

| File | Content |
|------|---------|
| `scripts/instruments/relational_opcode.py` | `RelationalCrystalClassifier` (gate register, sign-CMR, consensus-relational, null; model-agnostic). s232: `calibrate(null_gate_by_layer=...)` = cross-task null — `fb0c9ec`, `8bd5f42` |
| `scripts/experiments/opcode_audit_validation.py` | Qwen3-14B calibrate + s127 battery + raw-vs-relational control — `143ccda` |
| `results/opcode-audit-validation/verdict.json` | 31/40 crystal layers; over-read killed; relational under-reads at z=3 last-token |
| `scripts/experiments/opcode_monitor_v2.py` | s232 v2: cross-task null + per-token + z-sweep + trajectory + GATE_NEUTRAL control — `8bd5f42` |
| `results/opcode-monitor-v2/verdict.json` | s232 crosstask verdict: arc did NOT recover (S-late, gate-driven); opcode identity is null-dependent; substrate reproduced |
| `results/opcode-monitor-v2/verdict_gateneutral.json` | s232 v3 gate-matched-null verdict: ✅ composition-specific C-late (lambda routes C in 5/6 late layers, matched control does not); ⚠️ read is framing-contrast-dominated |
| `results/opcode-monitor-v2/verdict_qwen3-14b_gateneutral.json` | s232 v4: ✅ composition_specific=True (lambda C-late 0.56 vs all 3 gated guards ≤0.11) |
| `results/opcode-monitor-v2/verdict_qwen3-8b_gateneutral.json` | s232 v4: ❌ composition_specific=False (gate_neutral C-late 0.71 > lambda 0.33) — C-late is MODEL-SPECIFIC to 14B, not universal |
| `results/opcode-monitor-v2/verdict_qwen3-32b_gateneutral.json` | s232 v4 scale: ❌ composition_specific=False — C-late=0 in zone, but lambda C shifted EARLY (L5,10,11); 14B is the outlier, C-locus shifts with scale |
| `scripts/experiments/opcode_v5_locus_agnostic.py` | s233 v5 lead 1: pure re-analysis (no GPU) — locus-agnostic C detector across 8B/14B/32B; imports `detect_c_profile`/`locus_agnostic_specificity` from the harness — `1754424` |
| `results/opcode-monitor-v2/v5_locus_agnostic.json` | s233 v5 lead 1 verdict: 32B C-EARLY surfaced (was 0 in fixed zone); frac-specific ONLY 14B; 8B gate_neutral C-late confound CONFIRMED real (0.192 > lambda 0.107) |
| `src/verbum/lambda_ast.py` `step_fired`/`fired_sequence` | s233 v5 lead 2: certified per-step opcode trace (the model-invariant reference) — `1532e4e` |
| `src/verbum/probes/kernel_reference.py` | s233 v5 lead 2: symbolic combinator programs + kernel-certified traces; SATURATED⊗INERT pairs + COMPOSITE multi-fire — `1532e4e` |
| `scripts/experiments/kernel_reference_audit.py` | s233 v5 lead 2: anchor model routing vs the certified trace (reducibility / recall / specificity / trace-recall) — `1532e4e` |
| `results/kernel-reference-audit/verdict_qwen3-14b_crosstask.json` | s233 v5 lead 2 verdict: ❌ bare symbolic CL routes ONLY S-gauge (target_recall 1/7, reducibility not tracked) ⇒ register is prose-semantic, bridge must be compiled prose |
| `scripts/experiments/kernel_reference_prose.py` | s233 v5 lead 2b: held-out crystal-prose recall/specificity (non-circular calib/test split via `centroid_probes`) — `53ed331` |
| `results/kernel-reference-audit/prose_verdict_qwen3-14b.json` | s233 v5 lead 2b/2c verdict: ✅ prose recall 0.575 >> symbol 0.14; gauge-subtracted DISCRIMINABILITY rescues C (on/off 0.062/0.009 ~6.6×) + I as specific; B/D/W not; S/Y = common-mode + selectivity |
| `scripts/experiments/kernel_reference_prose_v2.py` | s234 v5 lead 2d prong 1: raw-z contrast (NO argmax) + Welch t + per-layer profile, n=20/comb — the deeper fix for the B/D/W gap |
| `results/kernel-reference-audit/prose_v2_verdict_qwen3-14b.json` | s234 v5 lead 2d prong 1 verdict: ✅ raw-z RESCUES K (t=2.12) + sharpens C/I (t=5.7/3.8), KILLS B false-positive; ❌ B flat / D,W anti (t −4.6/−2.3) ⇒ B/D/W gap GENUINE at last-token; discriminable {C,I,K,Y}; S=gauge Y=selective; ops peak L12-14 readable zone |
| `scripts/experiments/kernel_reference_prose_v3.py` | s234 v5 lead 2d prong 1b: per-token read (last/max/mean over tokens, Welch t) + relative-position profile — the B LOCUS test (reuses split_probes/welch_t from v2) |
| `results/kernel-reference-audit/prose_v3_verdict_qwen3-14b.json` | s234 v5 lead 2d prong 1b verdict: ❌ TOKEN-LOCUS FALSIFIED — B does not recover at ANY position (max t=0.68 n.s.); D/W anti everywhere ⇒ B/D/W absence is a REGISTER property of the FFN gate, not token-locus. {C,I,K,Y} robust w/ position signatures (I early, K mid, C mid-late, Y late) ⇒ build the value-register read (1b-ii) |
| `scripts/experiments/opcode_monitor_v2.py` `hook` param | s234 v5 lead 2d prong 1b-ii: open-slot register selector — `forward_all_positions`/`calibrate_v2` take `hook='gate'` (mlp.gate_proj, default) or `hook='attn'` (self_attn.o_proj = attention residual write) |
| `scripts/experiments/kernel_reference_prose_v4.py` | s234 v5 lead 2d prong 1b-ii: value-register read — same per-token raw-z contrast + profile as v3 but `--register attn` (reuses v2 split + v3 read/contrast) |
| `results/kernel-reference-audit/prose_v4_attn_verdict_qwen3-14b.json` | s234 v5 lead 2d prong 1b-ii verdict: ❌ s127 "B→attention" NOT confirmed — B flat in attention TOO (max t=0.49 n.s.) ⇒ register exhausted. {C,I,K,Y} register-ROBUST (C gate t=5.6/attn 6.5; Y 8.4/9.4) ⇒ discriminability is a COMBINATOR property, not a register split. B remains: head-dilution or no-single-token-signature |
| `scripts/experiments/kernel_reference_perhead_v5.py` | s234 v5 lead 2d prong 1b-iii: per-head OV scan — hook o_proj INPUT, split per (layer,head) cell, per-cell crystal calibration + raw-z Welch contrast across all 1600 cells (Bonferroni-ish t>4) |
| `results/kernel-reference-audit/perhead_v5_verdict_qwen3-14b.json` | s234 v5 lead 2d prong 1b-iii verdict: ⚠️ head-dilution only MARGINAL — B faint per-head signal (max_t 5.31 @ L17H23, 7/1600 cells) the summed read missed, BUT B dead-last every metric (n_sig 7 vs C 155, Y 526; discr_z 0.82 vs C 2.53); no clean B-composer head ⇒ register hypothesis EXHAUSTED, B faint/diffuse not diluted |
| `scripts/experiments/kernel_reference_gradient_v6.py` | s234 v5 lead 2d prong 1c: GRADIENT-register read — ∂(LM loss)/∂(gate) pooled over supervised positions (gd_gradient_shadow pattern), same RelationalCrystalClassifier + raw-z Welch contrast |
| `results/kernel-reference-audit/gradient_v6_verdict_qwen3-14b.json` | s234 v5 lead 2d prong 1c verdict: ❌ B does NOT discriminate in the gradient (discr_z +0.13, t=1.07 n.s.) — chain-rule NOT supported (first-order); ⚠️ but B "less absent" than any activation read (act t=−0.05 → grad +1.07, faint positive); {C,K,Y} discriminate (instrument works), C-yes/B-no persists. Measures first-order gradient NOT Jacobian |
| `scripts/experiments/kernel_reference_jacobian_v7.py` | s235 v5 lead 2d prong 1c-ii: SECOND-ORDER / curvature register — DIAGONAL HESSIAN of LM-CE w.r.t. gate_proj (Hutchinson `diag(H)=E_v[v⊙Hv]`, double-backward of g·v with create_graph), pooled over supervised positions; clean register-swap of v6, same RelationalCrystalClassifier + raw-z Welch; `--n-hutch` |
| `results/kernel-reference-audit/jacobian_v7_verdict_qwen3-14b.json` | s235 v5 lead 2d prong 1c-ii verdict: ❌ B not significant in curvature (discr_z +0.118, t=1.90 < 2.0) BUT ✅ MONOTONIC CLIMB with derivative order (act −0.05 → grad +1.07 → curv +1.90, B's best ever, ON the bar) + ✅✅ internal consistency (I=linear COLLAPSES 3.83→0.68 mirror of B; Y=recursion DOMINATES 4.53; composers hold, selectors fade). Derivative ORDER = real axis; B sorts UP. Diag-Hessian only (off-diag untested), power-limited n=20/comb |
| `scripts/experiments/kernel_reference_order_cost_v8.py` | s236 v5 lead 2d prong 2: ORDER-COST register — pure softmax-over-V surprisal of the certified reduction trace (`step_fired`, teacher-forced), minimal pairs (B/C, B/S, D/K) + multi-step composites, ATOM-ONLY de-confound; `--smoke` (8B), `--model`, `--n-each` — `5d6bdeb` |
| `results/kernel-reference-audit/order_cost_v8_verdict_qwen3-14b.json` | s236 v5 lead 2d prong 2 verdict (DECISIVE): ✅✅ **b_is_native_order=True** — clean atom B-vs-C minimal pair t=−7.02 (n=24); B atom-surprisal 0.81 ≪ C 2.14/S 2.66/W 2.71; B cheaper than every permute/copy (B<S −11.3, B<C-multi −11.7, B<W −14.5); pooled order-preserving<breaking. RESOLVES the B gap (composition=free autoregressive default, unmarked) + UNIFIES with curvature climb (order face + gradient face) — `1e448e4` |
| `results/kernel-reference-audit/order_cost_v8_verdict_qwen3-8b.json` | s236 v5 lead 2d prong 2 smoke (8B, n=8): ⚠️ POWER-LIMITED — same DIRECTION but headline atom B<C minpair n.s. (t=−0.55); multi-step/aggregate already sig (B<C-multi −4.22, B<S −5.31, B<W −11.1); pooled-atoms preserve<break. Crisp only at full power on 14B — `5d6bdeb` |
| `scripts/experiments/kernel_reference_order_cost_v9_prose.py` | s237 v5 lead 2d prong 2b: PROSE BRIDGE for order-cost — reuses v8 spine (certified `step_fired` trace, teacher-force, per-step surprisal, ATOM-only de-confound) but renders each term as PROSE via a DETERMINISTIC order-faithful renderer (`App(f,x)`→"`<f> applied to <x>`", atoms→fixed content words; content de-confound by char-span OVERLAP for leading-space tokens). `--render-mode {flat,nested}` (flat=nesting held constant=pure order test; default), `--smoke` (8B), `--model`, `--n-each` |
| `results/kernel-reference-audit/order_cost_v9_prose_verdict_qwen3-14b_flat.json` | s237 prong 2b DECISIVE: ✅ **b_is_native_order=True in PROSE** (nesting held constant) — atom B-vs-C minpair t=−8.05 ≈ symbolic v8 −7.02; B atom-surprisal 0.23 ≪ C 1.22/K 0.73/W 1.18/S 1.64; all 6 contrasts B<marked sig (−8 to −38); pooled preserve 0.24 ≪ break 1.12. The s236 bare-symbol caveat KILLED — composition-order real in the semantic register |
| `results/kernel-reference-audit/order_cost_v9_prose_verdict_qwen3-14b_nested.json` | s237 prong 2b CONTROL (nesting confound demo): ❌ atom B-vs-C minpair t=+11.9 (B>C, REVERSED) — SAME model+programs as flat, only render structure differs ⇒ direct proof nesting confounds the contrast; B's deeper-nesting clause cost dominates per-atom surprisal when nesting varies |
| `results/kernel-reference-audit/order_cost_v9_prose_verdict_qwen3-8b_flat.json` | s237 prong 2b CROSS-MODEL (8B flat, n=24): ✅ atom B-vs-C minpair t=−2.87 (B<C, SIG) — CROSSES at full power (the n=8 smoke was −0.57 n.s.); B atoms 0.39 ≪ C 1.61; all 6 contrasts sig; b_is_native_order=True. Confirms "power-limited not absent" |
| `results/kernel-reference-audit/order_cost_v9_prose_verdict_qwen3-32b_flat.json` | s237 prong 2b CROSS-MODEL (32B flat, n=24): ✅ atom B-vs-C minpair t=−4.48 (B<C, SIG); B atoms 0.36 ≪ C 1.23; all 6 contrasts sig; b_is_native_order=True ⇒ B-native-order UNIVERSAL across 8B/14B/32B (scale-robust, unlike C-locus) |
| `results/kernel-reference-audit/order_cost_v9_prose_verdict_olmo-2-1124-13b_flat.json` | s237 prong 2b CROSS-CLASS (OLMo-2-13B, flat n=24): ◑ strict single-step B-vs-C minpair t=−1.25 (B<C, n.s., d=−0.07) BUT B-vs-C-multi t=−24.4 ✓ + B-vs-S −9.7 / B-vs-K-multi −8.6 / B-vs-W −28.7 / D-vs-K −4.7 all sig; pooled preserve 0.62 ≪ break 1.08. Order preference replicates; single-step Qwen-specific |
| `results/kernel-reference-audit/order_cost_v9_prose_verdict_gemma-4-31b-it_flat.json` | s237 prong 2b CROSS-CLASS (Gemma-4-31B-it, flat n=24): ◑ strict single-step B-vs-C minpair t=−0.56 (n.s., d=−0.52) BUT B-vs-C-multi t=−11.6 ✓ + B-vs-K-multi −4.5 / B-vs-W −4.1 / D-vs-K −4.3 sig; pooled-atoms preserve 10.2 ≪ break 14.0. INSTRUCT model → huge absolute surprisals (B atoms 9.9, OOD prose), within-model contrasts valid. Same pattern as OLMo |
| `scripts/instruments/opcode_instrument.py` | the legacy VSM monitor (raw-cosine = the over-read; to be wired with the validated classifier as a config mode, keeping raw as the matched control) |
