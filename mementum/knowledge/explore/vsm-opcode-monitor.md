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

### v5 — next steps

- **Qwen3-32B scale test — DONE (s232): 14B is the outlier, C-locus shifts early.** 32B
  `composition_specific=False`; the lambda-specific C signal moved to L5–11 (early), which
  the fixed depth≥0.6 detector misses. Not scale-monotone. (`6bddcc2`)
- **locus-agnostic C detector** (the immediate methodological fix): per-model C-locus
  calibration or a full-profile lambda-vs-matched-control C compare across all layers,
  NOT a fixed depth≥0.6 zone (it found 14B but mislocates 32B/8B).
- **(b) kernel-as-reference** (priority): a single model's opcode read does NOT transfer
  (8B≠14B≠32B, locus shifts) ⇒ anchor the model trajectory against `lambda_ast`'s
  certified trace as the invariant; characterize per-model how composition maps to the
  routing register.
- bigger probe sets (more lambda sentences) for crisper fractions; investigate WHY 8B's
  gate_neutral routes C-late (the simple-copular-sentence confound).

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
| `scripts/instruments/opcode_instrument.py` | the legacy VSM monitor (raw-cosine = the over-read; to be wired with the validated classifier as a config mode, keeping raw as the matched control) |
