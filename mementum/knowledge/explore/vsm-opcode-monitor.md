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

### v5 — next steps

- **★ lead 2d:** (1) chase the **B/D/W gap** — why do deep/duplicate composers fail
  held-out prose discriminability while C/I succeed? (more prose/comb for power +
  per-layer breakdown of where C fires vs where B should). (2) the **composite trace-order
  bridge** (now justified for the discriminable combinators): CL program → certified trace
  (`fired_sequence`, DONE) → render PROSE (`lambda_gen` decompile) → align routing to the
  certified multi-combinator ORDER, focusing on C/I (+S/Y). (3) per-model sweep (8B/32B)
  with the discriminability metric.
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
| `scripts/instruments/opcode_instrument.py` | the legacy VSM monitor (raw-cosine = the over-read; to be wired with the validated classifier as a config mode, keeping raw as the matched control) |
