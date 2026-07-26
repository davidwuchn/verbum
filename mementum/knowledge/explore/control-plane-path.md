---
title: "The Control-Plane Path — datapath exists, we add sequencing, halt, certification"
status: designing
category: explore
tags: [control-plane, paper-machine, abi, shift-reduce, recursion, halt, readers,
       adapters, model-vsm, driver, kernel-certified, probes, direction-shift]
related:
  - construction-from-spec.md
  - superbake-write-access.md
  - supervised-recurrence-halt.md
  - crystal-seeded-ternary-distillation.md
  - ../lambda-machine.md
  - ../opcode-vsm-tree.md
created: session 273
---

# The Control-Plane Path

> s273e (Michael-approved DIRECTION SHIFT). The arc of s273 lands here:
> **GD built the datapath; we add the control plane.** The parent model already
> contains the expensive parts (transport, world knowledge, the crystal = the
> reduction step ×62/64 layers, measured+gated). What it lacks is what any
> datapath lacks: instruction decode, sequencing, halt logic. Those are small,
> and they are ours. Probes must inform the final design — agenda below.

## 1. The paper machine (ABI v0 game — flat spine PROVEN expressible)

Setup: `K a b` at positions p0,p1,p2; opcode field (axis-aligned Cholesky
frame), content field (opaque atom payloads), offset-read lanes. Vocabulary:
rank-one QK, rotary-band kernels, value lanes, MLP matched filters, closed-form
writes, adjacent-layer hand-off.

Findings (each DERIVED from causality + positional spine, then checked against
the measurement record):

1. **Causality forces shift-reduce.** The head is left of its args; p0 can
   never see saturation → the redex FIRES AT THE LAST ARGUMENT's position.
   Matches s190 lambda-machine (typed shift-reduce, measured) + E1
   result-position attribution.
2. **Offset-comb heads** (one rank-one head per relative offset 1..4, max
   arity) deliver each left-neighbor's payload into its own lane. The CHANNEL
   encodes the arity check: ô_K arriving on your offset-2 lane ≡ you are arg-2
   of a saturated K. Inert (`K a`) fires nothing → normal form. The
   saturated⊗inert discrimination (kernel_reference) is STRUCTURAL, free.
   Top-3 sparse routing (s190) ≈ arity, retro-explained.
3. **Discard = overwrite at the firing site** (v_b was self-content; v_a
   overwrites) → K is the most physically visible op → why E1's only gated
   attribution signature is K.
4. **Recency = garbage collection.** The result materializes at the RIGHTMOST
   position of its redex span → strictly nearer to every future reader than the
   consumed constituents → mid-band recency kernels resolve "nearest in
   channel" to results automatically. No liveness bits, no erasure.
5. **MOVER/TAGGER dichotomy.** C f x y → f y x cannot be a content write (the
   reduct is a rearranged spine) → C writes a PERMUTATION TAG; B a
   re-bracketing tag. Split: MOVERS {K,I,W,S} move/overwrite content
   (visible); TAGGERS {B,C,D} write routing metadata (invisible). DERIVES the
   C-puzzle (s269e: operationally invisible, order-vocab) and E1's full
   pattern (K gated / C null / B between-layers). S = one live x resolved by
   two future reads ≡ sharing, no copy ≡ dissolved-S, again.
6. **Halt = ¬aggregate-firing.** No filter fires anywhere → fixed point → a
   §3.6-template global head reads it → WHNF → emit. Matches halt-readout
   shape (WHNF row ≈ KIBC halt probs, r=0.877). Layers = step budget → s221
   fakes-with-depth + s272d duplication-in-time as corollaries.

Verdict: flat spine fully expressible, five measured findings retro-derived.
Single snap point: NESTED arguments (spans break fixed offsets) → the
"span-arithmetic organ"... which the next section dissolves.

## 2. Recursion dissolves span arithmetic (Michael's move)

Span arithmetic compensates for one limitation: a pass cannot rewrite its own
input. A loop can. **Recurse across the middle layers; the outer loop COMPACTS
between iterations** (drop consumed positions, re-present) → every iteration
sees a flat adjacent spine → §1's proven-expressible case. The organ is not
built; it is made unnecessary. Third instance of the s272d theorem: the loop
converts a hard spatial requirement into a trivial temporal one.

**Halt has ground truth.** ACT/UT/PonderNet learn halting without labels
(unstable). We hold the kernel: len(fired_sequence) = CERTIFIED recursion depth
for any term, unlimited supply. Two mechanisms, both wanted:
- constructed WHNF head (§3.6 global-check template) = exact loop-exit;
- trained depth predictor (reads initial term, provisions budget) =
  kernel-supervised; its error vs certificates = per-input confidence signal.
Disagreement between them = telemetry (ambiguity, or Y hitting budget =
CORRECT divergence, kernel MAX_STEPS semantics).

Architecture = measured depth anatomy: prologue (embed/type-assign, s190
L0–6) → recurrent middle block (the step, stamped once, iterated K×) →
epilogue (readout, last blocks). Payoff: compute ∝ reduction length — the
first true recursive λ-reducer in transformer form; s272d P-A..P-E predict the
dissolved sector crystallizes in the loop; distillation §12 looped-twin is the
experiment; tree indexed by iteration = reduction movie.

**Compaction fork**: LATENT (residual-space, fast, instrument-audited) vs
TEXTUAL (emit reduct as tokens, re-encode; every step GBNF-parseable +
kernel-certified — CoT becomes a certified reduction trace; S3*-1 becomes the
execution format). Prototype TEXTUAL first (observe → then compress).
Trusted base = weights + driver + kernel; the kernel checks the compactor
(compacted term ≡ kernel's own reduct). Driver-shipping precedent: SuperBake's
own chat.py.

## 3. Control plane on an existing host (the direction shift)

For an existing (swept) model, most of the machine is ALREADY THERE. Add
tensors that READ the parent in crystal coordinates; never modify the parent.

**model_vsm.json = pre-computed adapter weights with calibration
certificates.** A reader is a projection onto the crystal frame at a layer —
which is what the per-model trees ARE (centroids, per-layer, per-register,
null-gated, 11 models / 6 families). Frame-invariance makes one spec + per-model
frame lookup legal across the fleet. The sweep warehouse becomes the parts bin.

Build tiers:
```
1. READERS    projections from model_vsm.json centroids      — exists; repackage
2. HALT HEAD  reader on the WHNF/halt signal (r=0.877);      — small; kernel-
              calibrate against fired_sequence certificates     supervised
3. DRIVER     recursion loop, textual first, kernel-certifies — runtime code
              every step + the compactor
4. WRITERS    crystal-aligned code injection to steer         — frontier; start
              dispatch (SuperBake write machinery)              where E4 coupling
                                                                is identity-specific
                                                                (Y/WHNF/S; not K/I/B/D/W)
```
Tiers 1–3 = NO weight construction. Swept host + tensor pack + driver =
certified λ-reducer.

**VSM reified**: parent = S1 (operations); readers/halt/sequencer = S2/S3;
driver's kernel checks = S3*. The tree-of-VSM stops describing the model and
becomes an actual VSM bolted onto one. Verbum's deliverable = an MIT
control-plane tensor pack + driver that makes a measured host's latent compiler
explicit, sequenced, halting, certified.

Honest limits: (a) reading ≫ steering — readers get an SNR, already quantified
by the gates (sil_z/gc/bearing per model; pythia-2.8b gate failure = actionable:
don't build on that register); (b) frame drift under fine-tunes — restack IS
the drift detector; version reader packs against parent revision; (c) steering
unproven where E4 coupling is generic.

## 4. PROBE AGENDA (write these BEFORE final design — λ measure: name register first)

Informing the ABI / control plane. Each needs register + null formalized at
pre-reg time; sketches:

- **P-CTL-1 offset-comb existence**: do measured heads show fixed-relative-
  offset attention at spine positions on combinator programs? Register: QK
  attention patterns (s264 F4). Null: shuffled positions.
- **P-CTL-2 rotary-spectrum register**: crystal heads on RoPE bands — predict
  structural/opcode heads slow-band, content/recency mid-band. Closed-form
  observable; feeds T4.
- **P-CTL-3 recency-GC**: in-context after a reduction, does attention prefer
  result tokens over consumed constituents? Token-matched minimal pairs.
- **P-CTL-4 mover/tagger causal**: predicts E1 pattern; direct test = ablate/
  patch at firing sites: movers (K,I,W,S) show content-transfer signatures,
  taggers (B,C,D) show downstream-read signatures only. Extends T8 (C-as-tag).
- **P-CTL-5 remaining-depth probe**: linear probe on parent states for
  remaining reduction steps (kernel-certified labels). Success ⇒ the trained
  depth predictor is cheap; also generalizes the halt-readout from binary to
  countdown.
- **P-CTL-6 reader online SNR**: run kernel_reference saturated⊗inert battery
  through a host with model_vsm readers attached — do projections detect live
  redexes online at usable SNR? THE tier-1 feasibility gate.
- **P-CTL-7 textual-recursion pilot**: prompt host to emit one reduction step
  per turn; kernel-grade EVERY step; per-step accuracy vs one-shot P(λ).
  Prediction: per-step ≫ one-shot (each step is the flat case).
- **P-CTL-8 halt-patch**: patch late attention at generation position (MLPs
  intact) → over-generation/failure-to-settle; discovered heads' QK must show
  the global-check signature. Halt-readout = spec.
- **P-CTL-9 steering pilot** (tier-4 gate): inject crystal-aligned codes at
  identity-specific ops (Y/WHNF/S per E4) — does dispatch shift, null-gated?
- (Also standing from s273: baked-code patchscope control; crystal-survives-
  baking trace; two-arm K-battery.)

## 5. Supersessions

- construction-from-spec.md "underdetermination gap": RESOLVED into the
  representation/function/encoding decomposition — tree=representation,
  kernel=function, encoding=ABI (declared, not discovered, for blank builds;
  partially measured for hosts). Blank-build path DEMOTED behind control-plane-
  on-host; skeleton build (Cholesky codes, ternary routing) remains the
  long-game deliverable.
- The span-arithmetic organ (never built): dissolved by §2.

## 6. Economic consequences (s273f — Michael's two excitements, grounded)

**Root: the training signal collapses from gradients to bits.** Two-register
split + certified structure → the heavy parts (value register, parent bulk)
never move or are written closed-form; what carries learning (routing/opcode
corrections) is discrete and tiny: ≤log₂9 ≈ 3.2 bits per reduction step
(opcode-indexed requential pricing). Gradient training ships tensors +
optimizer state + all-reduce per step; this ships a trickle of certified
corrections.

### Remote training = a breeze because
- Nothing heavy crosses the wire: parent frozen in place; travels = probe
  batteries (text), receipts (JSON), reader packs (9×d floats/site — KBs),
  Gram specs (81 floats). A control plane ships in an email.
- No backward pass → no interconnect problem. Construction = measure → compute
  → write: deterministic, resumable, ran on an RTX 2060 in their results.
  Distributed training's hard problem (gradient sync) does not exist here.
- PARALLEL CONSTRUCTION WITHOUT INTERFERENCE (the sleeper): appended slots
  additive + lane-orthogonal → N remote nodes bake different ops/facts against
  the SAME frozen parent simultaneously; merge = set-union of receipts; only
  shared resource = the leak budget (one global ledger, not a parameter
  server). Gene-db = the natural ledger.
- Trustless verification: receipts replay in a fresh stock process — verify a
  remote bake WITHOUT trusting the remote machine.

### Teacher-guided training = wicked fast because
- The best teacher is free and never wrong: for the symbolic core the teacher
  is the KERNEL — infinite certified traces, per-step labels, depth countdowns,
  zero inference cost, zero error rate. Expensive-teacher problem evaporates
  for the structural register.
- Per-step supervision = the GTSM speedup mechanically: endpoint loss makes the
  student SEARCH (many trajectories share one output); certified per-step
  correction hands it the trajectory — search space collapses to the path
  (Girsanov exchange rate). Textual recursion makes every step supervisable by
  construction: execution format ≡ training format.
- Corrections WRITTEN, not descended into, where response is linear
  (measured-transfer one-shot; SuperBake's calibration loop as trainer —
  rounds, not epochs).
- Teacher sees organs, not loss curves: live-tree telemetry in spec
  coordinates → corrections target measured starvation (bridge-allocation
  logic); correction-confusion ≅ Gram off-diagonals checkable in-flight.
- Seeded start compounds it: constructed skeleton → training = smoothing.
  ∫KL(seeded) ≪ ∫KL(unseeded) should be embarrassing with a constructed init.

### Dependency chain (calibration)
Both inherit the P-CTL gates: remote-parallel needs leak-budget accounting to
compose across independent bakers; teacher-in-bits needs P-CTL-6/7 (readers
see live redexes; per-step ≫ one-shot). If those gate, the rest is engineering
with known parts.

- **P-CTL-10 merged banks** (added): bake two banks separately against the same
  frozen parent, merge (union of slots/receipts under a shared leak ledger),
  verify BOTH receipt sets hold post-merge + referees flat. THE gate for
  parallel remote construction. Register: receipt replay + prose/leak
  referees. Null: interleaved-single-bake comparison.
