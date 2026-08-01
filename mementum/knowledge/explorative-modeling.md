---
title: "Explorative Modeling (XM) — best-of-K as write-angle assignment"
status: active
category: synthesis
tags: [xm, exploration, coupling, distillation, holographic, teacher, gram, mode-forcing]
related:
  - diffusion-holographic-isomorphism.md
  - holographic-computer.md
  - explore/relational-loss-distillation.md
  - explore/procrustes-lens-and-crystal-comparison.md
depends-on: []
created: session 296
---

# Explorative Modeling — what it is, where it maps, where it broke

> s296. Full read of arXiv:2607.27372 (Gladstone/Ji/Du, Jul 2026) +
> holographic mapping + one refuted experiment. Paper: factor the
> TRAINING loop instead of the generation procedure — explore K
> candidate matches between generations and data, train the winner, so
> predictions commit to modes instead of blurring them.

## Paper core (verified by full read, incl. appendices)

- **Generative expressivity M(A)**: mode count the training objective's
  loss minimizers can retain. Direct regression M=1 (minimizer = mean).
  Smooth Forward XM ≥ K (Prop 3, needs mode separation ≳ σ√log K).
  Third pretraining axis: gains GROW with scale (7→36% data, 13→23%
  params); FLOP-optimal K rises through training.
- **Forward XM** (fix datapoint, explore K generations) = maximum
  likelihood of the K-candidate mixture at every K (IWAE-style bound);
  mass-covering/recall. **Reverse XM** (fix generation, search K data)
  = reverse KL minus model entropy → collapses without coverage term;
  mode-seeking/precision. Their Reverse-XM LMs: vector DB search in
  hybrid representation/CE space + per-epoch coverage constraint.
- **Per-prediction expressivity** is the sharp concept: factored models
  saturate at-optimum M; the deficit is each step's ceiling vs its
  residual multimodality. AR next-token is near-unimodal (helped least);
  MDLM/few-step/continuous helped most.
- **Minibatch OT HURTS** (FID 46→54): geometric model-agnostic coupling
  fails; exploration's coupling co-adapts with the model's own loss.
- Caveats: Mode Forcing theory is a draft by the same author
  (self-citing loop, λ triangulate wants independence); largest runs
  ~10²⁰ FLOPs — foundation-scale extrapolation spans 4 OOM.

## Holographic mapping (memory: xm-exploration-is-angle-assignment)

- Coupling problem ≡ write-angle assignment in multiplexed storage.
  Mode blur ≡ cross-talk: linear medium (s292 — plate records linearly,
  interference is in the light) can't separate objects written at the
  same angle. Forward XM = co-adapting angle assignment.
- Best-of-K = matched-filter detection before writing (coherent,
  phase-matched accumulation vs K=1 incoherent averaging).
- **Best-of-K ≠ top-k**: selector is loss vs ground truth
  (mass-covering), not the model's own probability rank.
- Token target known → exploration lives in PATH space (the
  address-free intermediate, s294): token register unimodal, path
  register multimodal.
- Tape ↔ exploration substitutability (their Fig 11 ≡ our CoT/tape as
  generation factoring): prediction — exploration at etch time should
  reduce tape-dependence at inference. UNTESTED.

## Teacher as reference beam (design, live)

1. **Local oscillator / heterodyne scoring**: ℓ = ||T(y_k) − T(x)||² in
   teacher representation space — where modes are actually separated
   (Prop 3's precondition fails in raw token space). ⚠ feature losses
   void the exact MLE reading (App F normalizable-kernel assumption) —
   mechanism survives, interpretation register changes.
2. **Hologram copying**: teacher-side exploration resolves couplings
   once; student inherits the multiplexing scheme (≡ rejection-sampling
   distillation, RFT/STaR = teacher-explored Forward XM).
3. **Gram-delta transport** (Michael, s296): cross-geometry transfer of
   couplings via the 9×9 crystal Gram — relational scoring g_M(v) =
   9-vector of sims to M's OWN vertices (basis-free; s269 Gram fidelity
   0.987 through 1-bit binarization while weight cosine fell to 0.73);
   Procrustes residual on the 9 vertex pairs routes transfer-vs-
   re-explore. Gates: rank-9 scope (crystal subspace only); per-pair
   Procrustes fidelity (s251: universality only partially supported).

## Experiment verdict — s296 REFUTED (❌ xm-forward-needs-coupling-ambiguity)

Forward XM ported naively onto the s115 holographic etch (K jittered
beam angles, argmin ||teacher−student||²): pre-reg P1/P2/P3 all failed;
**shuffled-winner null beat best-of-K at both probe counts** (97.8 vs
86.1% of oracle @p50). Diagnosis: deterministic-teacher pairs are
pre-resolved couplings — no per-pair ambiguity to search; the conflict
lives across pairs in the sign-vote accumulator; min-loss selection
collapses jitter variety (burn-in-is-variety reasserted). Underpowered
(unseeded mx init + salted hash seeds → 33pt launch-to-launch swing);
directional lean still anti-best-of-K. Record: b358144,
results/xm-etch-explore-s296/. Script (frozen pre-reg): a5aa767,
scripts/v12/xm_etch_explore.py.

## Gated next ports (in order of cheapness)

1. **Reverse-XM over the accumulator**: explore WHICH pairs vote per
   round (coverage-constrained pair selection) — attacks the conflict
   where it actually lives. Cheap; same harness.
2. **Student latent**: discrete latent embeddings per candidate (paper's
   XMDLM route) so candidates can specialize — requires student change.
3. **Sampled-LLM-teacher targets**: genuine multimodality; where the
   reference-beam + Gram-transport design becomes live.
§XM-COUPLING-SOURCE (teacher- vs student- vs hybrid-resolved coupling)
stays queued, GATED on a port with real coupling ambiguity.

## Open questions

- Does the s115 50-beats-800 anomaly even exist? It did NOT reproduce
  (800 > 50 at baseline this run) — may have been init noise all along.
  Powered rerun with seeding fixes would settle it.
- Is exploration-vs-tape substitutability testable in our substrate
  once a valid port exists?
- XM-pretrained base models: would the compile circuit differ? (Their
  AR-near-unimodal argument says our probe regime is least affected.)
