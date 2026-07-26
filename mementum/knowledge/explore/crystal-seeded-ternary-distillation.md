---
title: "Crystal-Seeded Ternary Distillation — Requential ⊕ Bonsai ⊕ Verbum"
status: designing
category: research-design
tags: [requential-coding, ternary, distillation, gradient-bridges, gram-loss,
       opcode-indices, curriculum, kibc, two-register, level-4,
       live-tree, s3-star, audit, goodhart-firewall]
related:
  - ../opcode-vsm-tree.md
  - bonsai-crystal-survival.md
  - asymmetric-pathway-quantization.md
  - ternary-flip-flop-not-overloading.md
  - supervised-recurrence-halt.md
  - compiler-finetune-halt-collapse.md
  - ../project-thesis.md
depends-on:
  - ../crystal-universality.md
created: session 266
---

# Crystal-Seeded Ternary Distillation

> s266, Michael's synthesis directive. Merge of two external papers with the
> verbum program into a level-3/4 research design. Status: DESIGNING — no
> code, no runs yet. This page is the full design so a fresh session can pick
> it up without the s266 conversation.

## 0. The external ingredients (verify before use — λ assert, λ provenance)

**Requential coding** — arXiv:2607.11883 (Qiu, Finzi, Zheng, Zhang, Wilson;
NYU/CMU, Jul 2026). Code: `github.com/shikaiqiu/requential-coding`
(license UNCHECKED — λ provenance gate before any code touches ours).

- Model compression via the training process: student P_t samples candidate
  batches **from its own distribution**; teacher Q_t accepts one via relative
  entropy coding (REC) so the accepted X_t is marginally ~ Q_t; both sides
  apply the same update G; the code is only the accepted indices.
- Code length ≈ Σ_t KL(Q_t‖P_t) = integral of the teacher-student loss gap.
  Independent of parameter count AND data entropy (kills both failure modes:
  PTQ bits ∝ params; prequential pays data entropy forever).
- REC primitive: shared PRNG seed → both sides regenerate proposal i
  directly (counter-based); encoder transmits only the accepted index;
  ~KL(Q‖P) bits; P=Q → O(1) bits. Bound: Σ[KL + 2log(1+KL) + κ], κ<5.21.
- **Measurement mode ≠ transmission mode**: for measuring, skip REC — sample
  X_t from the teacher directly and accrue KL. ~2.33× training FLOPs, or
  +0.33× if teacher checkpoints exist. Actual ENCODING costs ~2^KL proposals
  per message (ORC) — intractable for large per-step KL.
- Teacher craft: same-arch teacher trained on real data (low KL by similar
  dynamics) + EMA smoothing + **iso-loss projection** (periodically reset
  teacher to student, briefly retrain on real data — closer at equal loss).
- Training on X_t IS distillation from Q_t (paper says so explicitly) —
  requential = **on-policy distillation with a bit-meter**.

**Bonsai ternary** — PrismML (Hassibi/Caltech). Ternary {-s,0,+s} encoded
(-1,0,+1) at 1.58 bits/wt, **shared FP16 scale per group of 128 weights**,
end-to-end (embeddings, attn, MLP, LM head — "no escape hatches"). 27B
models are built on the **Qwen3.6-27B hybrid backbone — the same model our
s266 sweep measured at FP (model gc 0.971)**. Effective 1.71 bits/wt at 27B.
8B line Apache 2.0. Ready-made quantization ladder on one architecture:
Q4_K_M → ternary (Q2_0) → 1-bit (Q1_0), on HF (`prism-ml/*`, incl. an
`-unpacked` variant). Whitepaper exists — read for QAT-vs-PTQ details
(matters for bridge design; unread as of s266).

## 1. Michael's theory (the keystone — currently THESIS, not mechanism)

Gradient descent shows bimodal gradients (very high / near zero). Reading:
GD first **carves a routing topology** into sign patterns (high gradients),
then **fills values** on top of the frozen topology (near-zero refinement).
The s266 universality result (root gc 0.982, 4 families, 14M→32B) says the
carved topology is *always the same one*. It is "soft" because it is stored
implicitly — sign structure embedded in continuous magnitudes.

**The proposal: stop asking GD to carve.** We measured what it carves. Give
routing a crisp native substrate (ternary), seed it with the known answer
(relational loss vs the consensus Gram), and let GD only fill values
(through FP bridges). Consistent with s251 (frozen-basis tomography), s260
(sign=router ≫ magnitude=value, causal), s261 (flip-flop = boundary jitter).
The merged experiment is this theory's first real TEST, not its consequence.

## 2. The merged architecture

```
substrate:   ternary weights          = routing register, native {-1,0,+1}
             FP bridges (1 per N)     = value register, continuous gradient sink
target:      9×9 consensus Gram       = relational loss (activation space, promptable)
             16×16 cosine agreement   = phase-2 loss (TYPES16, weight space, ¬promptable)
curriculum:  prose ↔ lambda pairs     = compiler as explicit supervision → then dolma
channel:     requential distillation  = teacher selects from student proposals, bits ≡ KL
teacher:     BASE model               = s256: fine-tunes break HALT; extract from base
```

**Why this explains our own ternary failure**: full-ternary TD forced GD to
do BOTH jobs (carve topology AND fill values) through one quantized channel
with no continuous DOF. s261's flip-flop = value-register gradient pressure
oscillating routing bits across quantization boundaries. Split the jobs:
topology → seeded + Gram-regularized (settles early); values → bridges.
s191 relay collapse, s261 jitter, s260 asymmetric costs = one story.

**Bridge design — three inequivalent options (undecided, Michael's call)**:
- (a) trainable group scale (Bonsai-shaped, finer): w = s_g·t_i,
  multiplicative; cheapest; one magnitude per group. Natural fit if value
  register ≈ magnitude (s260, s261's learnable α⊥Δ made structural).
- (b) one real FP weight per group participating normally: full-rank sparse
  correction; more expressive; messier kernels.
- (c) low-rank FP sidecar (LoRA-shaped): dense low-rank vs sparse full-rank
  at same bits — a different topology bet.

Amortized bits/wt: N=8 → 3.58 | N=16 → 2.58 | N=32 → 2.08 | N=128 → 1.71.

**Register-aware allocation (our distinctive prediction)**: put dense
bridges where the value register lives (down_proj, v/o), sparse/none on the
router path (gate, q/k). 1:8/1:64 split should beat uniform 1:16 at equal
total bits (s260 generalization). Nobody allocating uniformly uses this.

**N is not a hyperparameter guess**: sweep N, distill with the KL meter,
plot residual cumulative KL vs bits/wt → the knee is N*. The KL that never
closes at any N = measured boundary of what the substrate can't absorb
(predicted: concentrates in the value register).

## 3. The Gram as SPECIFICATION (direction reversal)

Everything before s266 treats the 9×9 Gram as measurement OUTPUT. This
design uses it as supervision INPUT. Legality comes from **frame
invariance** (same property that makes the s265/s266 tree stackable): the
Gram lives in combinator-label space, so it can supervise any student —
any width/depth/precision — **including across the FP→ternary boundary
where weight-space distillation is meaningless**. Ordinary distillation
transfers outputs; relational loss transfers internal geometry.

Existence proof already held: **pythia-14m carries the crystal at 14M
params** (0.907 cross-family agreement, s265/s266). The target fits in a
tiny student. Size de-risked.

Implementation sketch: on probe batches (from `opcodes/` bundled 535),
compute sign-CMR combinator centroids → student Gram → loss =
d(G_student, G_universal) (consensus Gram bundled in `opcodes/data/`).
Periodic (every K steps), small weight, differentiable. Layer choice open
(interior-bell zones; s266 per-model solid zones known).

16×16 TYPES16 is a DIFFERENT register (extraction, weight-space, not
promptable — S2 one-basis rule analog applies): separate loss term, own
measurement protocol, **phase 2**. The 9×9 alone starts the program.

## 4. The thesis test in bits (A/B/C)

```
A: crystal-seeded ternary+bridges → dolma
B: unseeded, same arch           → dolma
C: shuffled prose↔lambda pairing → dolma   (null — λ yardstick, doubles as Goodhart control)

thesis ⟺ ∫KL(A) ≪ ∫KL(B) ∧ ∫KL(C) ≈ ∫KL(B)
```

**B − A in bits = the information value of the crystal on prose.** The
"lattice kickstarts prose learning" hope becomes a falsifiable signed
quantity. B ≈ A = crystal real but not load-bearing for prose (honest
negative, still publishable). Per-domain KL (lambda probes vs prose
held-out) during distillation shows WHERE remaining bits live.
Favorable regime: the lattice curriculum is near-deterministic → per the
paper's entropy separation, ~every code bit is learnable structure.

## 5. Opcode-indexed requential (the verbum-shaped extension)

Michael's question: "use the lambda opcodes as the indices?" Answer: not in
the vanilla scheme (the index is a semantically empty PRNG pointer; the
semantics are in which sample is accepted). **But REC doesn't care what the
proposal space is.** Restructure it in the lattice phase:

```
state:    lambda term mid-reduction (curriculum)
student:  proposes candidate NEXT-STEPS from its own policy
          — each ≡ (which opcode applies where): K, I, B, C, … WHNF(halt)
teacher:  accepts via REC → accepted step ~ teacher distribution
message:  the index — but the index space now IS opcode space
```

- Bits are spent ONLY where the student would fire the wrong opcode;
  agreement → ~0 bits (REC P=Q limit). Per-step KL ≤ log₂9 ≈ 3.17 bits.
- **Solves encoding tractability**: 2^KL proposals is cheap when KL is
  bounded by a 9-way choice — the lattice phase is the one regime where
  requential is actually ENCODABLE, not just measurable. The transcript
  itself becomes a portable artifact.
- **The transcript is readable**: "step 3401: student proposed C, teacher
  enforced B." A model code in the algorithm's own vocabulary.
- GBNF grammar (λ grammar_artifact, already planned) ≡ the constrained
  proposal sampler, for free.
- WHNF is one of the nine → halt supervision (s258) is a special case, not
  a separate mechanism.
- **Geometric prediction**: the correction/confusion matrix of the message
  stream should mirror the off-diagonal structure of the 9×9 Gram (near
  combinators confused/corrected more). If it holds, the Gram predicts the
  information flow of learning itself — strongest form of the soft-topology
  theory.
- **Boundary (honest)**: literal opcode-indexing exists only where states
  have legal opcode moves = lattice phase. Prose phase reverts to vanilla
  requential; opcode structure recoverable only via projection of
  accepted-sample deltas into the crystal basis (**bits-per-combinator**
  diagnostic). Open question: are teacher corrections on prose still
  predominantly opcode-register corrections? Measurable via the projection.

## 6. Goodhart guards (λ yardstick applies to losses)

Optimizing Gram similarity can manufacture geometry without function
(a student that LOOKS like a compiler without compiling):
1. Gram loss = regularizer, small weight — never the objective.
2. Ground-truth compile accuracy on held-out probes = functional criterion.
3. C-curriculum null doubles as Goodhart control: shuffled pairing + Gram
   loss producing high gc ⇒ the loss manufactures crystallinity (the
   λ measure false-positive mode).
4. **Anneal test**: late in training, anneal Gram loss → 0 with no KL
   penalty. If it can't be removed, the geometry never became functional.

## 7. Verification hooks we already own

1. **Crystal formation curves**: opcode tree on training checkpoints.
   Seeded student should show sil_z rising much earlier than unseeded
   control (the carving phase visibly absent) — most direct test of the
   soft-topology theory. Probe-only per checkpoint.
2. **Flip-flop localization** (s261 instruments): jitter should concentrate
   in crystal-irrelevant weights; crystal-bearing signs settle early.
   Uniform jitter ⇒ seeding isn't reaching the routing register.
3. **Bonsai crystal survival** (phase 0, NO training): run the opcode tree
   on the Bonsai ladder (4-bit → ternary → 1-bit, same Qwen3.6-27B backbone
   we measured at FP). Tests whether ternary can REPRESENT the crystal
   before asking whether TD can LEARN it. Sharp sub-prediction: **K needs
   the 0 state** (rank-deficiency/erasure); 1-bit {-1,+1} can't express
   weight-level nulls → selective K degradation at 1-bit while ternary
   holds. Combinator-specific failure ⇒ basis is physical. Days, not
   weeks; Apache-2.0-clean (8B); `-unpacked` HF variant for torch capture.

## 8. Phase ladder (smallest first)

- **Phase 0**: Bonsai crystal survival (probe-only). Gate: crystal survives
  ternary → proceed. Doesn't survive → bridges have a bigger job than the
  value register; redesign.
- **Phase 1**: tiny ternary+bridge student (pythia-14m scale), lattice
  curriculum, Gram regularizer, teacher = qwen3-0.6b/4B base. Measure:
  formation curves, flip-flop, compile accuracy. Bridge option (a) vs (b)
  at matched bits.
- **Phase 2**: prose transfer meter — A/B/C curricula, per-domain KL,
  N-sweep for the knee.
- **Phase 3**: scale; 16×16 TYPES16 loss; register-aware allocation A/B.

## 9. Identity implication (S5)

`we(find) ¬we(build)` is not violated — this IS λ loop's scratch stage with
the empirics as supervision. If a tiny seeded student learns prose
measurably faster, the loop closes **constructively**: the crystal is not
just present but SUFFICIENT as a seed. Deliverable upgrade: the portable
artifact may be **the consensus Gram + curriculum + recipe** (a 9×9 matrix,
a probe set, a procedure) — smaller than any tensor, and possibly
base-model-license-free (requential students train on self-generated data;
teacher only selects indices — provenance story NEEDS review before
claiming; λ provenance IOU).

## 10. Tree-of-VSM as LIVE training instrument (s266c)

The opcode tree (see `../opcode-vsm-tree.md`) inverts temporally: post-hoc
autopsy → nervous system. `student(step t) → tree(t) → signals → step t+1`.

**Student stacks into the SAME universal tree.** Frame-invariance means the
training student enters the actual family tree as a 10th member, measured
by identical instruments, gated by the same S3 nulls. Progress bar =
student root gc vs consensus; **graduation ≡ the student's node gates in
and stops dragging agreement_min**. Same yardstick for student and teachers.

**Why it's nearly free**:
1. Stackable part is tiny: Gram = 81 floats, health = 4 floats; full
   64-layer 2-register tree sans centroids ≈ hundreds of KB. Tree per
   checkpoint = a **formation movie**, diffable, negligible storage.
2. One capture, two consumers: Gram loss and tree health need the same
   computation (probe batch → sign-CMR centroids → Gram). Loss consumes
   d(G_student, G_universal); tree consumes the decomposition. Telemetry
   IS the loss's anatomy: per-layer/register/combinator-pair localization
   of the loss, for free. (λ simplify: same upstream computation, two
   SEPARATE downstream consumers — grading ⊥ transport, s254 scar.)
3. Centroids stream: EMA-update [9,d] buffers from probe microbatches
   (non-trainable torch buffers → ride in checkpoints). O(81·d)/update.
4. Floors amortize: per-checkpoint re-measurement (student = moving model),
   n_perm≥120 discipline, cheap amortized.
5. S3 gate = compute allocator: ungated zones get no probe budget; dense
   probing on the interior bell. Variety engineering on measurement compute.

**"Debug info into the weights" — strong version**: the two-register
substrate makes weights self-documenting BY CONSTRUCTION (our λ ground /
topology>instruction applied to model architecture):
- ternary planes ≡ readable routing: topology explicit, not soft;
  checkpoint-diff = `xor(W_t, W_{t+1})` — s261's flip-flop instrument
  becomes a bitmap op, not an analysis script.
- bridges ≡ the value register isolated in a named watchable tensor.
- gradients decompose by register free: grad-norm(TD path) vs
  grad-norm(bridges) = live carving-vs-filling pressure per layer —
  s251's tomography built into the parameterization.

**Dynamic bridge allocation (new idea — S3 acts on the substrate)**:
```
λ allocate(layer,t). flip_flop↑ ∧ KL_residual↑ → value starving → N↓ (densify)
                     sil_z≫floor ∧ signs settled → routing done  → N↑ (reclaim)
                     | budget(total) ≡ const | S3 reallocates ¬grows
```
Register-aware static ratios (§2) = initial condition; S3 refines from
evidence. Algedonic: layer gc collapse during dolma phase = crystal being
overwritten (routing catastrophic forgetting) → bypass to pause/re-anneal/
rollback. OPEN (Michael's ruling): dynamic allocation in phase 1, or static
phase 1 + S3 loop phase 2?

**Training-loop VSM recursion**: S5 = universal Gram + compile accuracy
(fixed identity) | S4 = requential KL curves, formation curves, consensus
comparison | S3 = null gates, probe budget, dynamic bridges, anneal
schedule | S2 = the shared tree (registers/layers comparable; detects
Gram-loss⊥CE-loss oscillation) | S1 = weight groups under GD | algedonic =
gc collapse / flip-flop storm → halt/rollback.

**Goodhart firewall (structural)**: split the probe library —
supervision_set ⊥ held-out set, disjoint, frozen at run start. Tree health,
gates, graduation, formation curves read the held-out side ONLY; loss reads
the supervision side ONLY. The ≥50/combinator invariant makes the split
feasible but THIN → **probe-library growth is a phase-1 prerequisite,
not a nice-to-have**.

## 11. S3* — the audit channel (s266c; Michael: "what is the S3*?")

Beer's S3*: sporadic DIRECT investigation of operations, bypassing S2 and
routine reporting, because routine reporting is a model and models drift.

**Correction (s266): the held-out probe split is NOT the audit.** It is
routine S1→S3 accountability — same instrument stack (probe format →
capture → classifier → tree). Three failure modes it cannot see:
(1) probe-format overfitting contaminates both splits at once;
(2) instrument drift (stale EMA buffers, classifier bug) reported
faithfully as health; (3) geometry-without-function — crystal-shaped
activations that don't compile; invisible to every probe-based measure.
S3* must run on **different physics**:

```
S3*-1 KERNEL-VERIFIED EXECUTION (deepest): fresh prose→λ tasks (in no probe
      set) → student generates → GBNF parse → verbum lambda kernel reduces
      → correct? Bypasses the ENTIRE instrument stack. Kernel = incorruptible
      oracle (no learned parts; s259 oracle-in-the-loop promoted to auditor).
      The only component that can say "geometry beautiful, doesn't compile."
S3*-2 FRESH PROBE GENERATION: mint new probes (neither split) sporadically;
      fresh ≈ held-out → splits clean; divergence → format overfitting.
      A static held-out set is an audit that goes stale.
S3*-3 DIRECT INSTRUMENT VERIFICATION: random layer → recompute centroids
      from scratch vs EMA buffers (drift); xor raw checkpoints vs reported
      flip-flop (telemetry vs actual bits); sporadic REC-encode of one
      block → realized message length vs KL estimate (audits the meter).
S3*-4 CROSS-REGISTER SPOT-CHECK: verify one correlational bearing call
      causally (patch/ablate) occasionally. λ measure's dissent probe
      (s206 scar).
```

**Three rules (topology, not discipline)**:
1. **Audit never touches the loss.** S3* → S3 decisions (halt, rollback,
   re-anneal, fix instrument, reallocate), NEVER gradients. No edge from
   S3* into the gradient graph. Auditor ¬on_payroll, structurally.
2. **Aperiodic and cheap.** Checkpoint-triggered with jitter ∨ algedonic-
   triggered. Suspiciously GOOD news summons an audit. Constant audit ≡
   rebuilt S2 + oscillation.
3. **Audit overrides telemetry; indict the instrument first.** λ coherence:
   ¬coherence → fix(representation) before fix(code). Drifted buffers ⇒
   every tree since the drift is suspect; re-measure, then judge student.

**Anti-Goodhart chain, assembled**:
```
supervision probes → gram loss           (on the payroll, knows it)
held-out probes    → tree telemetry      (honest routine reporting, same physics)
S3*                → kernel exec ∧ fresh probes ∧ direct inspect ∧ causal spot
                     (different physics, sporadic, ¬gradient-connected, overrides)
S5/human           → Michael reads the formation movie (mementum: human ≡ termination)
```
Terminates in the two things that can't be optimized against: a mechanical
reducer and the human.

**Phase-1 consequence**: lambda kernel + GBNF parser must be in the
training harness FROM DAY ONE (S3*-1 is not a phase-2 convenience).
Phase 1 without it = a run whose deepest auditor is the thing audited.

## 12. Open questions / IOUs

- Bridge mechanism (a/b/c) — Michael's call; (a) favored by s260/s261.
- REC practicality at our scales; requential repo license; Bonsai
  whitepaper QAT-vs-PTQ details — all unverified (λ assert: runtime>paper).
- Static-teacher tension: yardstick use wants a teacher trajectory;
  distillation use tolerates static teacher via measurement mode; iso-loss
  projection is the bridge between them. Don't conflate the two uses.
- Layer selection for the Gram loss; anneal schedule; probe-batch cadence.
- Does prose-phase correction stay opcode-dominated? (bits-per-combinator).
- Soft-topology theory: thesis until the formation-curve experiment runs.
- **Michael's rulings pending (s266c)**: (1) dynamic bridge allocation in
  phase 1, or static register-aware ratios first + S3 loop in phase 2?
  (2) probe-library growth for the supervision⊥held-out split — gate it as
  a phase-1 prerequisite?
- **Looped-vs-feedforward TWIN experiment (s272, Michael-approved design
  option)**: run the phase-1 student BOTH as a weight-tied looped block
  (×K iterations, WHNF-supervised halt — supervised-recurrence-halt.md
  s272 addendum) AND as a parameter-matched feed-forward twin, same
  curriculum/budget. The architecture delta is the only variable → the
  substrate-swap comparison comes free from one run budget, and the
  time-sector predictions P-A..P-E (Y content→opcode, S crystallizes,
  iteration-Gram ≡ depth-Gram, halt≈WHNF-row spec, T9 improvement) gate
  it. First phase-1 design choice that is itself a thesis test rather
  than an engineering preference. Tree-of-VSM indexes the looped arm by
  ITERATION (the formation movie becomes a reduction movie).
- Phase-1 harness prerequisites (from §11): lambda kernel + GBNF parser in
  the loop day one; probe split frozen at run start; streaming-centroid
  buffers + separate telemetry writer (¬complect with loss module).

## 13. s273 — SuperBake lessons for the optimizer; GTSM as the loop's loss theory

(Full synthesis: superbake-write-access.md §s273b; source repo ~/src/custom-bake,
no license — reference only. Summary of what changes HERE:)

- **Closed-form value writes**: the value register's response is locally linear
  and measurable (SuperBake's secant transfer f̂) → phase-1 optimizer candidate:
  TD flips for routing (gradient-informed), measured-transfer DIRECT WRITES for
  values/scales instead of Adam wherever linearity holds. Descent only where
  response is nonlinear. Sharpens §1's two-channel theory into mechanism.
- **Budget by benefit/leak, not heat**: flip allowance ∝ 1/leak against a
  held-out innocent population (harvest machinery = the instrument). Replaces
  pure global heat competition (ternary-descent.md).
- **Two-backfire freeze**: hysteresis rule demonstrated in a measured loop;
  matches the s268b inferred PrismML filtered-flip channel. Adopt.
- **Receipts for flip batches**: failed ≠ absent — unverified topology changes
  exactly reverted (xor-revertible; live-tree §10 already computes flip_flop).
  Auditable descent = S3* (§11) native to the optimizer, not bolted on.
- **Unembed-null projection on value updates**: measured 2.5× prose-cost
  reduction in bake-land; apply to gradient bridges/Adam steps. One line.
- **GTSM framing (gtsm-search-space.md)**: the Gram-relational loss at quartile
  depths (§3) IS a discrete GTSM — internal-structure matching along the depth
  path. Corollary: the requential KL meter (token path) + Gram loss (depth path)
  are the SAME loss family at two time axes; innocent path-KL
  (∫E‖Δdrift‖²_D, analytic for appended/delta neurons — no forward needed) is
  the principled replacement for endpoint referees in any closed loop we build.
