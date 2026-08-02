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

## §XM-LATENT-1 — Student latent / XMDLM (PRE-REG, s297)

> Status: DRAFT — frozen on Michael approval, before any model run.
> Port 2 of the gated list, Design B (mixture-of-experts, marginalize
> eval; Michael-approved s297). Attacks the REPRESENTATIONAL side that
> s296/s297 exposed: the etch loss `||teacher−student||²` is direct
> regression → per-prediction expressivity M=1 (minimizer = the mean =
> blur). Forward-XM (s296) and Reverse-XM (s297) both had nothing to grab
> because a single deterministic student can't REPRESENT multiple modes.
> XMDLM gives the student K discrete latent embeddings → M raised 1→K.
> The multimodality is real even for a deterministic token target: it
> lives in PATH space (many internal configs produce the right output;
> different pairs can use different paths — token register unimodal, path
> register multimodal, s294/holographic-mapping).

### Mechanism (Design B)

- **Latent bank** `Z ∈ ℝ^{K × n_layers × d}`, K=4 (frozen), learnable.
  Latent k injects a per-layer additive residual offset: in the full
  forward, `x_{l+1} = student_layer_l(x_l) + Z[k, l]` (= a learnable
  "mode vector" / reference-beam angle per candidate).
- **Forward-XM best-of-K etch** (per round, per layer, per pair): candidate
  k loss `= mean((layer(t_in) + Z[k] − t_out)²)`; winner = argmin_k
  (mode="best") or random k (mode="rand", the null). Plate sign-votes
  accumulate the WINNER's gradient (train the winner) → plates see a more
  consistent target because Z absorbs the cross-pair (mode) variance.
  Z is trained in the beam phase (Adam) with the same best-of-K loss.
  This is s296's `explore_layer_loss` with candidates = learnable OUTPUT
  offsets Z[k] instead of input jitter.
- **Eval, 3 modes** (`LatentHoloModel.__call__` returns the marginal):
  - **marginal** = `log(mean_k softmax(logits_k))` — the honest mixture,
    no oracle. **GATED.**
  - **argmax-latent** = per-input pick lowest-entropy latent — advisory
    self-routing.
  - **oracle-latent** = per-input best latent vs ground truth — advisory
    CEILING (how much capacity exists if routing were solved).

### Arms (× probe_counts {50, 800}, ≥5 init seeds)

- `baseline`   — K=1, no latent selection (≡ s297 baseline + learnable bias)
- `xmdlm`      — K=4, best-of-K assignment (TREATMENT)
- `xmdlm_rand` — K=4, RANDOM per-pair assignment (param+training-matched
                 NULL: same K experts, all trained, only assignment differs
                 — isolates SPECIALIZATION vs merely having K experts to
                 marginalize over). Load-bearing (G2).

### Frozen gates

- **G1** xmdlm(marginal) > baseline (oracle-recovery %). One-sided α=0.05/3.
- **G2** (λ yardstick, load-bearing) xmdlm(marginal) > xmdlm_rand(marginal):
  specialization, not K-expert-marginalization, must drive any gain.
  Fails ⟹ marginalization artifact (parallels s297 subsetting-artifact).
- **G3** (mechanistic) specialization is real — CAPACITY is the
  load-bearing sub-test: **oracle-latent(xmdlm) > marginal(xmdlm)** AND
  **oracle-latent(xmdlm) > oracle-latent(xmdlm_rand)** (specialized experts
  route to higher per-expert capacity than randomly-assigned ones).
  Assignment entropy H is reported ADVISORY only — H ≈ log K cannot
  distinguish balanced specialization from interchangeable latents, so it
  never gates; the oracle comparisons carry G3.
  Latents are init distinct-by-construction (z_scale=0.2, high-d
  ~orthogonal) so best-of-K is not tested from a collapsed strawman.

### Frozen verdicts

- **EXPRESSIVITY-UNBLOCKS** — G1 ∧ G2 pass ∧ G3 specialization: M=1 was
  the blocker; latent expressivity + exploration finally helps the etch.
  Promotes latent-scaffold distillation; the s295 backprop-compile /
  level-4 collapse becomes the artifact-shrinking follow-on.
- **MARGINALIZATION-ARTIFACT** — G1 passes, G2 fails: K experts help via
  averaging/capacity, not specialization (mirror of s297). Latent adds
  nothing exploration-shaped.
- **CAPACITY-BUT-UNROUTED** — G1 FAILS (marginal) BUT oracle-latent(xmdlm)
  beats baseline by a margin AND beats oracle-latent(xmdlm_rand): the
  specialization created usable capacity that marginal routing WASTES.
  Next = learn a router (input→latent) / the level-4 collapse. The
  oracle-ceiling only DISAMBIGUATES this failure branch — it never
  manufactures a G1 pass.
- **STILL-BLOCKED** — G1 fails AND oracle-latent(xmdlm) ≈ baseline ≈
  oracle-latent(xmdlm_rand): no capacity created even with latents → the
  deterministic teacher has no capturable path-multimodality → port 3
  (sampled-LLM-teacher, genuine multimodality) is the only remaining lever.

### Reproducibility (s296/s297 fixes, mandatory)

- `np.random.seed` AND `mx.random.seed` per arm×init (TernaryLinear init
  uses global np.random; nn.Linear + Z init use mx).
- integer seeds (NO salted hash()); ≥5 init seeds; grade INTERNALLY paired
  by init seed (MLX/MPS bit-repro is within-process only — all arms share
  one oracle per run). --validate asserts within-process bit-repro.
- K=4, etch_batch=8, n_rounds=8, z_scale=0.2 frozen & recorded in meta.

### §Result-latent — s297 VERDICT: STILL-BLOCKED

Full sweep (results/xm-latent-s297/, oracle 87.4%, 30 arm-runs, 5 init
seeds, K=4, gd=10500). Graded internally, paired by init seed. Mean
recovery (× oracle):

| arm         | probes=50 marg / oracle-lat | probes=800 marg / oracle-lat |
|-------------|-----------------------------|------------------------------|
| baseline    | **0.967** / 0.962           | **0.962** / 0.962            |
| xmdlm       | 0.858 / 0.852               | 0.930 / 0.934                |
| xmdlm_rand  | 0.918 / 0.908               | 0.906 / 0.907                |

Frozen gates:
- **G1 xmdlm(marginal) > baseline: FAIL** both — xmdlm is *below* baseline
  (Δ−0.110 @50, Δ−0.032 @800 n.s.). Baseline (K=1) is the best arm
  everywhere; adding latent experts HURTS.
- **G2 xmdlm > xmdlm_rand: FAIL/NULL** — @50 xmdlm < rand (Δ−0.061); @800
  xmdlm ≈ rand (Δ+0.024, t=0.69, n.s.). Specialization ≈ random assignment
  (echo of s297).
- **G3 capacity: NULL** — oracle-latent barely exceeds marginal (Δ+0.006
  @800, ~0 @50), and **oracle-latent(xmdlm) is itself BELOW baseline**
  (Δ−0.115 @50, Δ−0.028 @800). Assignment H≈logK (advisory).

**Branch:** G1 fails AND oracle-latent(xmdlm) < baseline (not > it) →
CAPACITY-BUT-UNROUTED is ruled out (no usable capacity exists — even
perfect per-input routing can't reach baseline). **Verdict = STILL-BLOCKED.**

**What it means.** Raising per-prediction expressivity M from 1→4 did NOT
unblock exploration — the blocker was never representational capacity. The
deterministic teacher has no capturable multimodality for best-of-K to
exploit, in token OR path space at this scale. The extra experts just
fragment the etch signal (each sees fewer/assigned pairs → weaker shared
plates) → recovery drops. Even oracle routing over specialized experts
can't beat the plain single-config baseline.

### §XM-DETERMINISTIC-TEACHER — the triangulated close (s296–s297)

Three independent operationalizations of Explorative Modeling on the
deterministic-teacher holographic etch now agree:
- **s296 Forward-XM** (diversify the model, jittered candidates) — REFUTED;
  deterministic pairs are pre-resolved couplings, no per-pair ambiguity.
- **s297 Reverse-XM** (diversify the data, coalition voting) —
  SUBSETTING-ARTIFACT; subsetting reduces variance (+11pt) but coherence
  adds nothing over random; contested weights irreducible toward truth.
- **s297 XMDLM** (diversify the student, K latent experts) — STILL-BLOCKED;
  added expressivity doesn't help, even at the oracle-routing ceiling.

**Convergent finding: exploration cannot improve holographic distillation
from a DETERMINISTIC teacher — there is no multimodality to explore.** The
mirror of the paper's minibatch-OT-HURTS: model-agnostic/geometric coupling
fails; XM needs coupling AMBIGUITY the model co-adapts to, and a
deterministic input→output map has none. The distillation ceiling is not an
exploration problem — the deterministic etch already extracts what is
extractable. **The only remaining XM lever is a genuinely multimodal target:
port 3 (sampled-LLM-teacher).** Distinct mechanisms (e.g. the s295
backprop-compile writeback wire) are separate research, not XM.

## §XM-SAMPLED-TEACHER — Port 3, sampled-LLM-teacher (PRE-REG, s298)

> Status: FROZEN (s298, Michael-approved) — gates locked before any etch run.
> Port 3 of the gated list, the last remaining XM lever. Design 1 (Michael-
> approved s298): keep the toy 26-token KIBC task + mini_holo student UNCHANGED;
> source multimodality from a real LLM (Qwen3-4B) SAMPLED at temp>0.

### The hinge it breaks

The s296–297 triangulated close established that exploration cannot improve
holographic distillation from a DETERMINISTIC teacher — no multimodality to
explore. Port 3 replaces the deterministic GDModel oracle with **Qwen3-4B
sampled at temp 1.3**, which the s298 characterization proved is genuinely
multimodal on KIBC (mode spread > 1 for depth ≥ 2; the deterministic teacher
had spread ≡ 1). This is the only remaining XM lever the arc identified.

### Teacher characterization (s298, prerequisite, non-gated)

`scripts/v12/xm_sampled_teacher_probe.py`, results
`results/xm-sampled-teacher-probe/teacher_cache.json`. Qwen3-4B reduces
combinator expressions, sampled K=8× per input; generations mapped back into
the 26-token vocab (97% parse rate; single-char recursive-descent parser +
`full_reduce` canonicalization). **Key finding — inverse relationship between
multimodality and correctness:**

| depth | mode spread | correct density | truth reachable (best-of-K ceiling) |
|-------|-------------|-----------------|--------------------------------------|
| 1 (easy) | ~1.0 unimodal | ~54% | ~54% |
| 2 | ~1.7 | ~20% | ~20–25% |
| 3 | ~1.8 | ~20% | ~20% |
| 4 (hard) | ~2.1 most-modal | ~0% | ~0–10% |

Where Qwen is confident (depth 1) it is unimodal (nothing to explore); where
uncertain (depth 3–4) it is multimodal but the correct mode is rarely present.
Sweet spot = depth 2–3 @ temp 1.3 (spread AND partial reachability). The
precondition ("teacher provides genuinely multimodal targets") is MET, so xm
vs xm_rand can now discriminate where the deterministic teacher could not.

### Etch-signal change (necessary, noted)

s296–297 distilled per-layer **activation-MSE** from the GDModel oracle. A
sampled LLM emits TOKENS, not commensurable activations (that was Design 2,
rejected). So port 3 distills via the **output-CE sign-vote etch**
(`etch_plates`: accumulate `sign(∇ masked_ce_loss)` over target batches, flip
plates where confidence > 0.6). The teacher's token outputs are the targets.
This is a legitimate holographic etch and is internally controlled (all arms
use it). It is a DIFFERENT etch signal than the deterministic-teacher arc; the
internal baseline/xm/xm_rand contrast is what carries the verdict.

### The paper's core contrast, instantiated

Forward-XM's claim: best-of-K (mode-commit) beats direct regression (M=1 =
mode-mixture blur). Mapped to the etch, per input we form **K training pairs**
(equal data budget across arms; only target CONTENT differs):

- **baseline (blur / mass-cover):** the K distinct Qwen samples — the etch sees
  the full mode mixture; sign-votes average across modes (the M=1 blur).
- **xm (best-of-K, mode-commit):** `[best] × K`, best = Qwen sample with min
  token-distance to ground truth (mass-covering selector = loss vs truth, NOT
  model probability rank).
- **xm_rand (random mode-commit, load-bearing null):** `[random] × K` —
  isolates selection-toward-truth vs merely committing to one mode.

### Training & recovery

The student learns ONLY from teacher-selected targets (etch + beam-fit both use
the arm's targets; no ground-truth GD). Ground truth is used ONLY by (a) the
best-of-K selector and (b) the eval. Recovery = student true-task acc /
true-task GDModel-oracle acc (the oracle is the yardstick only, never a
teacher). Teacher samples are generated once, seeded (torch), and cached —
fixed data across all arms/seeds; init-seed varies only student init + etch RNG.

### Frozen gates

- **G1** `xm > baseline` — mode-commit beats the mode-mixture blur (the paper's
  core claim). One-sided, α=0.05/3.
- **G2** (λ yardstick, load-bearing) `xm > xm_rand` — selection toward truth,
  not merely committing to one mode, drives the gain. Fails ⟹ selection-artifact
  (parallels s297). α=0.05/3.
- **G3** (mechanistic — the thesis) the `xm − xm_rand` recovery gain is GREATER
  in the multimodal band (depth 2–3, mean spread ~1.8) than in the unimodal band
  (depth 1, spread ~1.0), paired by seed. Tests that the exploration advantage
  tracks available multimodality. Depth 4 (truth unreachable) excluded from the
  contrast, reported advisory. Falsifiable both ways.

### Frozen verdicts

- **SAMPLED-TEACHER-UNBLOCKS** — G1 ∧ G2 ∧ G3: genuine multimodality unblocks
  exploration; the s296–297 close was determinism-specific; XM helps with a real
  multimodal teacher. Promotes sampled-teacher (STaR-like) holographic
  distillation.
- **SELECTION-HELPS-UNSTRUCTURED** — G1 ∧ G2, G3 fails: best-of-K helps but not
  via the multimodality gradient (generic target-cleanup, e.g. shorter/cleaner
  samples). Positive for XM-as-selection, does not confirm the mechanism.
- **MIXTURE-ARTIFACT** — G1 passes, G2 fails: having K samples helps but
  selection doesn't (mirror of s297 subsetting/marginalization).
- **STILL-BLOCKED** — G1 fails: even a genuinely multimodal teacher doesn't
  unblock; the holographic etch can't exploit multimodal token targets → the XM
  lever is exhausted across all teacher types.

### Config (frozen)

temp 1.3, K=8, depths 1–4 (spread gradient), top_p 0.95, max_new_tokens 32;
student d=48 / 3-layer; probe counts {50, 800}; ≥5 init seeds; graded internally
paired by init seed; oracle = GDModel on ground truth.

### Reproducibility (s296/s297 fixes, mandatory)

`np.random.seed` AND `mx.random.seed` per arm×init (TernaryLinear uses global
np.random; nn.Linear uses mx); integer seeds (no salted `hash()`); torch
`manual_seed` for teacher generation, cached; `--validate` asserts within-process
bit-repro or ABORT; K/temp/depths recorded in meta.

## Open questions

- Does the s115 50-beats-800 anomaly even exist? It did NOT reproduce
  (800 > 50 at baseline this run) — may have been init noise all along.
  Powered rerun with seeding fixes would settle it.
- Is exploration-vs-tape substitutability testable in our substrate
  once a valid port exists?
- XM-pretrained base models: would the compile circuit differ? (Their
  AR-near-unimodal argument says our probe regime is least affected.)
