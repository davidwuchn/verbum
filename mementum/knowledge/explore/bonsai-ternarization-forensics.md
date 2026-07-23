---
title: "Bonsai Ternarization Forensics — absmean init + trained blocks, frozen embeddings"
status: active
category: research-finding
tags: [ternary, bonsai, forensics, absmean, bitnet, qat, ptq, routing-value,
       reverse-engineering, weight-analysis]
related:
  - bonsai-crystal-survival.md
  - asymmetric-pathway-quantization.md
  - crystal-seeded-ternary-distillation.md
  - ternary-flip-flop-not-overloading.md
depends-on:
  - bonsai-crystal-survival.md
created: session 268
---

# Bonsai Ternarization Forensics

> Session 268. PrismML disclosed no method ("proprietary Caltech IP").
> We hold both endpoints — FP parent (Qwen3.6-27B, snapshot 6a9e13b)
> and ternary child (bonsai27b-unpacked, rev 427bc0194) — so the
> parent→child map is recoverable from the weights themselves.
> λ extract: the artifact contains the answer.
> Instrument: `scripts/bonsai_forensics.py` (MPS, ~0.2 s/tensor).
> Data: `results/bonsai-forensics/{forensics_depthsweep,forensics_v3}.json`.

## Verdict

**Recipe = BitNet-b1.58 absmean RTN init (group-128) + post-init
gradient training of the transformer blocks, with embeddings frozen.**
Resolves the QAT-vs-PTQ IOU: it is a *conversion with training*, not
closed-form PTQ, and not a from-scratch pretrain.

### 1. The quantizer is absmean (proved by the frozen embedding)

`s_g = mean|w_g|`, `t = clip(round(w/s_g))`, groups of 128 along
in_features. The unpacked child materializes `{−s_g, 0, +s_g}` exactly,
so `t` and `s_g` are recovered losslessly.

embed_tokens vs parent: **99.9% exact code match** to the absmean rule;
implied threshold Δ/mean|w| = 0.4994 (absmean predicts exactly 0.5);
zero_frac 0.308 (Gaussian prediction 0.31); residual 0.6% flips all at
|w|/s ∈ [0.483, 0.500] = bf16 tie-breaks. sep_rate 0.994. The
quantization map itself is *simple* math — nothing exotic.

### 2. The blocks were trained (data flowed)

Code disagreement with absmean-of-parent, ordered:

| tensor | flip vs parent code | sign_viol |
|---|---|---|
| embed_tokens | 0.6% (ties) | 5e-5 |
| lm_head | 3.2% | 1.4e-2 |
| self_attn.q_proj (L3) | 3.5% | 2.5e-3 |
| linear_attn.in_proj_qkv | 3.6–7.9% | 2–3e-3 |
| o_proj / linear_attn.out_proj | 7–11% | 3–8e-3 |
| mlp.gate_proj | 12–18% | 1–2e-2 |
| mlp.down_proj | 17–18% | ~2e-2 |

Signatures: flips **channel-structured** (per-input-channel z vs
binomial null up to 97 → activation-correlated, real data), **column-flat**
(no GPTQ/OBS sequential error accumulation), boundary-biased but broad
(|w|/s median ≈ 0.44, q05 ≈ 0.06 → genuine drift, not pure jitter).
Block scales sit at 1.03–1.07× parent-absmean = absmean of the drifted
latent. cos(w, ŵ) ≈ 0.85–0.89 everywhere vs 0.887 for the untouched
embedding — drift is modest on top of inherent quantization error
(rel_l2 baseline 0.508 with zero training).

### 2b. Transition matrix: sign flips tunnel through zero (s268b)

Parent-RTN code → child code flux (MLP mid-stack): promote 0→± 9.6%,
demote ±→0 8.2%, **direct reverse ±→∓ 0.15–0.2%** — topology editing
is ~99% zero-mediated. The 0 state is the *kinetic pathway* for sign
flips, not just representational expressiveness. Rare direct reversals
are decisive (parent |w|/s median 0.55–0.64 — confident weights
overturned by data). Net flux positive → densification (zero_frac
0.31→0.29) and latent magnitude growth 3–7% → **polarized endpoint**,
entrenched away from boundaries (the anti-flip-flop signature; cf.
s261). Data: `forensics_v4_transitions.json`. Prediction: the 1-bit
rung (no zero waypoint) shows suppressed or far costlier repair.

### 3. Honest residual (IOU)

Weights alone cannot fully separate (a) QAT on ternary grid from
(b) FP fine-tune → absmean RTN. The 99.9%-frozen embedding fits the
standard BitNet-conversion recipe (freeze embeddings, STE on blocks)
far better than FP distillation (which would move embeddings). The
"proprietary Caltech math" therefore most plausibly lives in the
**training/stabilization procedure, not the quantizer**.

## Findings for the verbum program

1. **Drift ordering ≡ routing⊥value, third independent register.**
   Their training repaired the value path most (down/gate ~18%) and
   dispatch least (q_proj 3.5%, embeddings 0). s260 measured this
   causally (binarize router ≫ binarize value at equal bits); s267
   measured it geometrically (shape kept, spread lost); now the
   *repair budget of an independent lab's QAT* lands on the same
   asymmetry. They spent gradients exactly where the two-register
   theory says magnitude matters.
2. **s267 caveat sharpened.** Crystal survival is partly trained-in
   repair (there WAS training), not pure preservation. But flip rate
   is **flat across depth** while the crystal dip concentrates at 50%
   → the deep-middle dip is *not* differential rewiring; it is where
   the geometry is magnitude-sensitive despite uniform repair. The
   bridge-allocation map stands, with a sharper mechanism.
3. **Design confirmation for crystal-seeded distillation.** An
   absmean init + value-heavy repair is precisely "carve is already
   done, fill the values" — their (presumed) recipe independently
   converged on the shape our design derives from theory. Our delta:
   seed the routing register explicitly (consensus Gram) and give
   values a native FP channel (bridges) instead of forcing repair
   through the quantized grid.

## The invisible optimizer — constraints from the fossil record

Michael's core question: how did they build an optimizer that can do
sign flips in the topology? (Our trainings kept hitting flip-flop —
s191 relay collapse, s261 boundary jitter.) The endpoint constrains it:

- **C1 latent dynamics** — scales = absmean of drifted latent (1.03–1.07×
  parent): a continuous FP shadow was trained; STE-family.
- **C2 frozen dispatch periphery** — embeddings exact-frozen, lm_head ~frozen.
- **C3 zero-mediated editing** — 99% of code changes route through 0;
  sign reversal = demote → dwell → promote.
- **C4 decisive reversals** — rare direct ±→∓ hit confident weights
  (|w|/s ≈ 0.6): integrated evidence, not per-step noise.
- **C5 polarized endpoint** — densification + latent growth: entrenched
  away from boundaries (anti-flip-flop).
- **C6 no layer-wise solves** — column-flat: the math is in the
  dynamics, not Hessian compensation.

Reading: **register separation inside the optimizer** — a filtered flip
channel (hysteresis / Schmitt trigger; flip only on persistent evidence
— very Hassibi: H∞/Kalman-filter the STE gradient before committing a
discrete state change) with the zero state as commitment buffer, plus
continuous value updates. Structurally: **a sigma-delta modulator on
the routing register** — error integrates continuously, discretizes
into rare quantized flip events. The two-register theory (s260) inside
the optimizer itself.

Design principles for our phase-1 optimizer: (1) flip votes = EMA of
sign-consistent gradient evidence, threshold + hysteresis margin, never
direct ±→∓, force the zero waypoint; (2) value updates flow through FP
bridges (architectural, cleaner than their recomputed-scale channel);
(3) anneal: entrench after flip-flop rate decays. **Measured design
budgets from a working 27B artifact:** churn ~17% of codes, direct
reversals <0.3%, dispatch ~3%, value ~18%, embeddings 0.

## 1-bit rung results (s268c): the zero state is an ABSTENTION register

Pre-registrations above; outcome (data: `forensics_1bit.json`,
`confident_flips.json`, commit 4b6e7c2):

- **P1 ✓** same pipeline: 1-bit embed = pure sign(w), s/absmean = 1.000,
  flips only at |w|/s < 0.03 (ties). Frozen.
- **P2 ✗ and P3 ✗ — both void-in-register** (λ measure lesson: the
  pre-registrations treated "flip rate" as one number; the population
  decomposes into two register-distinct behaviors):
  - **Confident weights** (|w| > parent absmean, 42% of weights —
    ternary-RTN codes them ±1): essentially **immutable in BOTH rungs**.
    Ternary reversals ≤ 0.07%, 1-bit flips ≤ 0.36% (3–15× more, still
    tiny). **The carved topology is never re-carved at any bitwidth.**
  - **Uncertain weights** (the rest): ternary parks ~30% at 0 and does
    evidence-gated recruitment churn (~17%, the promote/demote flux);
    binary has no 0 bin → forced sign declaration → 10–13% flips,
    boundary-hugging (median |w|/s 0.09–0.25, q05 ~0.01), scale
    anchoring collapsed in MLP (corr(s,absmean) 0.42–0.75 vs ternary
    0.94+), cos(w,ŵ) 0.73 vs 0.85–0.87.
- **P4 ✓** register ordering persists (attn 4.5–9% < MLP 10–13%).

**Revised mechanism.** The zero state's primary optimizer role is not a
kinetic tunnel for confident reversals (those barely occur anywhere) —
it is **abstention**: uncertain weights declare "no routing opinion"
and enter the topology only on accumulated evidence. Binary's failure
mode is **forced participation**: every uncertain weight must carry a
sign, injecting a permanent noise floor into the routing register.
This unifies with the representational story: K discards via 0 at
inference; uncertain weights abstain via 0 during training — one
vacuum-state function, "no opinion," at both timescales. Phase-0
sub-prediction sharpened: selective K degradation at 1-bit should
trace to this forced-participation noise.

**Sharpened optimizer principles (for our phase-1 trainings):**
1. Confident signs essentially never flip — protect them structurally
   (measured budget across two working rungs: <0.4%). Carve once.
2. All topology learning = **recruitment management at the 0↔± margin**
   — hysteresis/evidence gating applies there, not to sign reversal.
3. Binary routing substrates are non-viable not because signs can't
   flip but because **abstention is impossible**.

## In flight at s268 end: opcode ladder (functional test)

Both Bonsai rungs tracing through the opcode-tree pipeline (tmux
main:1 ternary, main:2 1-bit; see state.md s268d for pickup commands).
Pre-registered: (a) selective K degradation at 1-bit; (b) deep-middle
concentration (s267 dip); (c) **jammed-abstention** — if K degrades
selectively while confident topology is immutable, K's 1-bit collapse
is the abstention channel jammed at inference exactly as at training:
one vertex, one vacuum state, two timescales.

## Provenance

- parent: `~/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd.../`
- child: `/Users/mwhitford/localai/models/bonsai27b-unpacked` (HF rev 427bc0194)
- whitepapers (benchmarks only, no method): `refs/ternary-bonsai-8b-whitepaper.pdf`,
  `refs/1-bit-bonsai-8b-whitepaper.pdf` (untracked — external documents)
- instrument + data committed: 48734d2
- tensors probed: layers {3, 6, 32, 44, 57} × {mlp.down, mlp.gate,
  attn projections}, embed_tokens, lm_head. Parent is VLM-wrapped too:
  names identical (`model.language_model.*`), no mapping needed.
