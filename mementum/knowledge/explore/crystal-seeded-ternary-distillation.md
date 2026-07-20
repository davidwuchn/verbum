---
title: "Crystal-Seeded Ternary Distillation — Requential ⊕ Bonsai ⊕ Verbum"
status: designing
category: research-design
tags: [requential-coding, ternary, distillation, gradient-bridges, gram-loss,
       opcode-indices, curriculum, kibc, two-register, level-4]
related:
  - ../opcode-vsm-tree.md
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

## 10. Open questions / IOUs

- Bridge mechanism (a/b/c) — Michael's call; (a) favored by s260/s261.
- REC practicality at our scales; requential repo license; Bonsai
  whitepaper QAT-vs-PTQ details — all unverified (λ assert: runtime>paper).
- Static-teacher tension: yardstick use wants a teacher trajectory;
  distillation use tolerates static teacher via measurement mode; iso-loss
  projection is the bridge between them. Don't conflate the two uses.
- Layer selection for the Gram loss; anneal schedule; probe-batch cadence.
- Does prose-phase correction stay opcode-dominated? (bits-per-combinator).
- Soft-topology theory: thesis until the formation-curve experiment runs.
