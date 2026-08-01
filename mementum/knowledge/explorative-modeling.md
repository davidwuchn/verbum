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

## §XM-REVERSE-1 — Reverse-XM over the sign accumulator (PRE-REG, s297)

> Status: FROZEN (s297, Michael-approved) — gates locked before the run.
> Port 1 of the gated list. Attacks the s296 diagnosis at its stated
> locus: the conflict lives ACROSS pairs in the sign-vote accumulator.
> Forward-XM diversified the model side (jitter, deterministic pairs →
> no per-pair ambiguity → refuted). Reverse-XM diversifies the DATA
> side, which is where the multimodality actually is.

### The mechanism it targets

`holographic_etch` accumulates per-batch sign votes:
`acc += sign(grad)` over N batches, then flips weights where
`|acc|/N > 0.6`. **Contested weights** — where batches disagree so the
net vote washes to ~0 — never cross threshold and stay frozen forever.
Those contested weights ARE the multimodal ones (different pairs want
different signs). Averaging (Forward/baseline) = mass-covering blur that
leaves them stuck.

### Reverse-XM operationalization ("explore WHICH pairs vote per round")

A "voting unit" = one feature batch of `etch_batch` probes (default 8,
smaller than the s115 32 so there are enough units for coalitions:
50 probes → ~7 units, 800 → 100). Per round r, per layer, instead of
all units voting:
1. Build per-unit sign-vote vectors `V[b] ∈ {-1,0,+1}^W`, concatenated
   over the layer's 4 plates.
2. **Mode-coherent coalition** `S_r`: seed = least-covered unit (coverage
   driver); take the **top f·nb units by signed cosine agreement to the
   seed** (f = coalition fraction, frozen at 0.5). Top-fraction (not a
   θ threshold) so the random null is EXACTLY size-matched.
3. Flip confident-majority **within S_r only** (`|acc_{S_r}|/|S_r| > 0.6`)
   → sharp mode-commit instead of washout. This is reverse-KL /
   mode-seeking: the update commits to the coalition's mode.
4. **Coverage constraint**: seed = least-covered unit each round, so
   every unit leads across rounds (the per-epoch coverage term whose
   absence collapses Reverse-XM to precision-only entrenchment).

f frozen at 0.5; rounds R = 8 (recorded in meta). Beam training is
IDENTICAL across arms (all units, distill loss) — the sole treatment is
which units vote for plate flips.

### Arms (× probe_counts {50, 800}, ≥3 init seeds each)

- `baseline`     — all pairs vote every round (= current s115 etch)
- `revxm`        — mode-coherent coalition + coverage (TREATMENT)
- `revxm_rand`   — same-size coalition, RANDOMLY selected each round
                   (the load-bearing null: isolates coherence vs mere
                    subsetting)
- `revxm_nocov`  — mode-seeking, NO coverage (same seed / greedy)
                   (isolates the coverage term's contribution)

### Frozen gates

- **G1** revxm > baseline in oracle-recovery % (mode-commit resolves
  contested weights → higher recovery). One-sided, α=0.05/3.
- **G2** (λ yardstick, load-bearing) revxm > revxm_rand null: coherence,
  not mere subsetting, must drive any gain. Fails ⟹ the effect is a
  subsetting artifact, verdict void. α=0.05/3.
- **G3** (mechanistic) contested-weight CORRECT-resolution toward the
  ORACLE crystal: of weights contested at round 0 (`|acc_all|/N < 0.6`),
  the fraction whose FINAL sign matches the oracle's `sign(W)` crystal
  (`extract_crystal`) is higher for revxm than baseline. Tests whether
  mode-commit resolves contested weights toward the TRUTH, not merely
  moves them (any-flip resolution is near-ceiling ~66% for all arms, so
  it can't discriminate; correct-resolution can). Diagnostics recorded:
  `fixed_frac` (of init-wrong contested, fraction fixed to oracle),
  `moved_frac` (legacy any-flip). Directly tests the s296 diagnosis.

### Frozen verdicts

- **REVERSE-COMPOSES** — G1 ∧ G2 pass ∧ G3 shows correct contested-weight
  resolution toward the oracle: data-side exploration resolves the
  accumulator tug-of-war toward the truth; port 1 is the right locus;
  promotes coverage-constrained etching as a method.
- **SUBSETTING-ARTIFACT** — G1 passes but G2 fails: any gain is from
  voting on fewer/noisier pairs, not mode-coherence. Reverse-XM in this
  form adds nothing; the accumulator conflict is not coherently modal.
- **NO-RELIEF** — G1 fails: mode-commit does not beat mass-averaging;
  the contested weights are genuinely irreducible at this scale (coheres
  a deeper "the conflict is not exploration-shaped" reading, → student
  latent / sampled-teacher ports).

### Mandatory s296 reproducibility fixes (baked in)

- Explicit `np.random.seed` AND `mx.random.seed` per arm×init — BOTH
  needed: `TernaryLinear.__init__` uses global `np.random.choice` (a
  second unseeded source beyond s296's `mx` note), nn.Linear uses `mx`.
- Integer seeds passed explicitly (NO salted `hash()` — the s296 bug
  that caused a 33pt launch-to-launch swing).
- ≥3 init seeds per arm; report mean ± std; gates scored on the mean
  with across-init variance as the noise floor (arm deltas must exceed
  the init noise to count).
- --validate reproduces identical logits/metrics on repeat with same
  seed or ABORT.

### §Result-full — s297 VERDICT: SUBSETTING-ARTIFACT

Full sweep (results/xm-reverse-s297/, oracle 71.1%, 40 arm-runs, 5 init
seeds, gd=10500; all recoveries >1.0 — frozen-plate+GD students beat the
GD oracle, orthogonal to the question). Graded internally, paired by init
seed. Mean recovery (× oracle):

| arm          | probes=50 (7 units) | probes=800 (100 units) |
|--------------|---------------------|------------------------|
| baseline     | 1.072 ± 0.126       | 1.060 ± 0.040          |
| revxm        | 1.072 ± 0.073       | **1.171 ± 0.069**      |
| revxm_rand   | 1.168 ± 0.060       | 1.151 ± 0.085          |
| revxm_nocov  | 1.135 ± 0.151       | 1.157 ± 0.071          |

Frozen gates (probes=800, the informative regime):
- **G1 revxm > baseline: PASS** — Δ=+0.111, t=+2.29, **5/5 seeds**.
  Coalition voting beats all-unit averaging by ~11 pts, robustly.
- **G2 revxm > revxm_rand (λ yardstick, load-bearing): FAIL** —
  Δ=+0.020, t=+0.42, 3/5. Mode-coherent selection does NOT beat a
  size-matched RANDOM coalition.
- **G3 contested correct-resolution: NULL** — all arms end contested
  weights at the oracle sign at ~chance (0.49; fixed_frac ~0.47–0.48).
  No arm resolves the tug-of-war toward the truth.
- probes=50 (7 units): G1 null (Δ=0.000), G2 **negative** (−0.096,
  random beat revxm) — too few units for coalitions; pure noise, as the
  smoke's sign-flip warned.

**Verdict = SUBSETTING-ARTIFACT (pre-registered).** G1 passes, G2 fails:
the gain is real but comes from voting on FEWER units per round, not from
mode-coherence. All three subset arms (revxm ≈ revxm_rand ≈ revxm_nocov,
~1.15–1.17) beat baseline (~1.06) and are indistinguishable from each
other → the only thing that matters is "vote on a 50% subset," not WHICH
subset (coherence adds nothing, coverage adds nothing). Mechanism: with
half the voters, `|acc|/|S|` crosses 0.6 more easily → sharper flips =
variance reduction, not exploration.

**What it means.** The s296 diagnosis ("conflict lives across pairs") is
half-right: reducing simultaneous voters relieves the accumulator
tug-of-war, but the residual conflict has NO exploitable mode structure —
G3 shows the contested weights are irreducible toward the oracle at
chance. This is the mirror of the paper's minibatch-OT result (geometric,
model-agnostic coupling HURTS): a geometric grouping of the votes
(cosine coalition) does not beat random. Exploration needs coupling
AMBIGUITY the model can co-adapt to; the deterministic-teacher sign
accumulator has variance to reduce, not modes to discover. Port 1 is
answered: **Reverse-XM in this form is not the mechanism; subsetting is a
free knob but a shallow one.**

**Fallout / next.** The remaining gated ports both add genuine
multimodality the accumulator lacks: (2) student latent (candidates can
specialize) and (3) sampled-LLM-teacher targets (targets genuinely
multimodal). Both are now the honest continuation. Also cheap: since
subsetting-as-variance-reduction is real (+11pt, 5/5), a follow-on could
sweep the coalition FRACTION f and the confidence threshold jointly —
but that is knob-tuning, not the exploration thesis, and should be marked
as such (λ yardstick: it describes, it doesn't discover).

## Open questions

- Does the s115 50-beats-800 anomaly even exist? It did NOT reproduce
  (800 > 50 at baseline this run) — may have been init noise all along.
  Powered rerun with seeding fixes would settle it.
- Is exploration-vs-tape substitutability testable in our substrate
  once a valid port exists?
- XM-pretrained base models: would the compile circuit differ? (Their
  AR-near-unimodal argument says our probe regime is least affected.)
