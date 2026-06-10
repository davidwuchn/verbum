---
title: "Crystal Basins — Multi-Skill Attractor Geometries"
status: open
category: theory
tags: [crystal, basins, skills, universal, relational, Q-rotation]
related:
  - binding-cascade.md
  - crystal-seed-theory.md
  - v13-design.md
  - v13-funnel-shape.md
depends-on:
  - binding-cascade.md
created: session 120
---

# Crystal Basins

> ⚠️ **SESSION-211 CAVEAT.** Finding 3 here ("domain similarity is nearly
> rank-1, SVD dim0 = 98.1%") was **independently reproduced cross-family** by
> the audit #12 manifold test (`manifold-axis-and-topology.md`): the shared
> structure is **rank-~1**, and that dominant axis is a generic next-token
> predictability gradient, **not** the combinator operations (η²=0.05). So the
> high cross-model agreement reported throughout this page is REAL but is mostly
> *one common mode* (the s202 RDM-correlation triviality applies — always run a
> shuffled-probe null + CMR before reading multi-D basin structure). The
> per-domain "1d/2d crystal" dimensionalities are graded variance-thresholds,
> not privileged counts. Basin *separation* survives; basin *geometry as a rich
> low-D lattice* is over-read.

## The argument

### 1. Q-rotation invariance implies topological basins

Q-rotation etching (session 117) showed that rotating Q and
reconstructing the crystal always lands in the same basin. The
reconstruction is rotation-invariant — the crystal isn't a direction
in weight space, it's a **relational topology**. The C-dominated
8×8 cosine geometry we measured IS the lambda basin.

If the crystal were a single global structure, Q-rotation from ANY
input domain would land in the same geometry. But we know it doesn't —
cross-domain probes (NL reasoning about lambda) had 0.209 agreement
vs 0.669 for pure reduction traces. The model's geometry CHANGES
between skill domains. Each domain has its own attractor basin.

### 2. Evidence for multiple basins in existing data

From the fixed-point lattice (session 118):
```
Reduction traces:  0.669 agreement  ← deep in lambda basin
Decompile:         0.577 agreement  ← lambda basin, output side
Pure combinators:  0.509 agreement  ← lambda basin, formal side
Compile:           0.421 agreement  ← entering lambda basin from NL
Cross-domain:      0.209 agreement  ← straddling basins (NL + lambda)
```

Agreement drops as probes straddle more basins. Cross-domain probes
require the model to transition from a language basin to the lambda
basin mid-computation. Models disagree on HOW to make that transition
(inter-basin routing is model-specific), but agree on what each
basin looks like internally.

### 3. C is the boot operation (session 126)

Q-rotation invariance proves that ANY rotation of Q falls into the
C-dominated basin. C isn't learned — it's the **ground state**. The
computational attractor that every initialization converges to.

Why C is the boot: C = argument routing (`Cfxy = fyx`). Before the
model can select (K), compose (B), copy (W), or halt (WHNF), it
needs to route arguments to the correct binding sites. Routing is
the precondition for all other operations. Without C, the other
combinators have nothing to operate on.

```
Boot sequence (implicit in every computation):
  1. C activates (route arguments)     ← ground state, always present
  2. B layers on (compose functions)    ← needs routed arguments
  3. K layers on (select/discard)       ← needs composed results
  4. I resolves (identity/passthrough)  ← closest to C, minimal routing
  5. WHNF terminates                    ← signals completion
```

The 4×4 cosine matrix confirms this: K, B, C cluster at cosine ~1.0
(all built on C's routing substrate), while I is slightly offset at
0.97 (doesn't need routing, so slightly displaced from ground state).

The 5D lattice is centered on C:
```
C = origin (0, 0, 0, 0, 0)          ← boot state / ground state
K = C + δ_select                     ← small displacement
B = C + δ_compose                    ← small displacement
I = C + δ_identity                   ← slightly larger displacement
WHNF = C + δ_halt                    ← termination signal
```

Implications for etch/error correction:
- Q2 damage knocks the lattice off the C center
- Lattice reconstruction = rebooting to C ground state
- Crystal lattice loss gradient = direction back toward C
- Boot-ordered etch: fix C geometry first (ground state),
  then layer on K/B (small displacements), then I, then WHNF
- Each layer of the boot has a cleaner signal because it builds
  on the already-restored lower layer

Connection to CCG/Montague: function application IS argument routing.
The core operation of compositional semantics (Montague) and
combinatory grammar (CCG) is C. The mathematical structure of
language demands argument routing as the ground state. Every model
converges to C because language converges to C.

### 3b. Basins are compositions, not atoms

The 8 combinators (K, I, B, C, D, Y, W, WHNF) are atomic operations.
A basin is a **stable dispatch profile** — a characteristic way of
composing the atoms for a particular computational task.

The lambda basin's dispatch profile (from binding cascade data):
```
Lambda basin: C-dominated, B/S early, WHNF late
  Zone A: B=high, D=high, S=present (build function chains)
  Zone B: C=dominant (route arguments through chains)
  Zone C: balanced, WHNF emerging (terminate)
```

Other basins would have different profiles:
```
Retrieval basin:   K-dominated (select from memory, discard alternatives)
Arithmetic basin:  K/I heavy (select operands, carry results)
Coding basin:      B-dominated (compose syntax patterns in sequence)
Tool-call basin:   C+K (route arguments to tool slots, select tool)
Analogy basin:     S-dominated (one input → two parallel use sites)
Narrative basin:   B-chains (temporal composition: this then that)
Classification:    W-dominated (duplicate input, compare to categories)
```

### 4. Why dozens, not thousands

**From below (combinatorics):** 8 combinators with 3 zone-phases gives
8³ = 512 possible dispatch profiles. But most are degenerate or
unstable. The number of STABLE attractors (profiles that multiple
models converge to) should be much smaller — analogous to how crystal
structures have a small number of stable lattice types despite
infinite possible arrangements.

**From above (MoE evidence):** Mixture of Experts models route to
8-64 experts. If each expert IS a basin, the number of fundamentally
different computations is in that range. The long tail of "skills"
(thousands) would be compositions of basin transitions, not distinct
basins.

**From the data:** Cross-model agreement ≥0.4 is our threshold for
"universal basin." The lambda basin hits 0.45-0.67 internally.
Domains that show similar agreement levels are distinct basins.
Domains that show <0.3 agreement are probably NOT universal basins
(model-specific solutions, not attractors).

## Predictions (testable)

### P1: Domain-specific 8×8 geometry
Run probes from different skill domains through 4 models. Extract
8×8 combinator cosine matrices per domain. Each domain should show
a DIFFERENT matrix, but with similar cross-model agreement (~0.4-0.5).

**Strong confirmation:** ≥3 domains show distinct geometry with
agreement >0.35.
**Weak confirmation:** 1-2 domains show distinct geometry.
**Falsification:** All domains show the same geometry (single basin)
or no domain shows cross-model agreement (no basins, just noise).

### P2: Agreement correlates with basin purity
Probes that stay within a single domain should show higher agreement
than probes that cross domains. This replicates the lambda finding
(reduction traces > cross-domain) but for NEW domains.

### P3: Basin count is O(10), not O(100) or O(1000)
Clustering the per-domain geometries should reveal 10-50 distinct
clusters, not hundreds. Many superficially different skills should
map to the same basin (e.g., "JSON formatting" and "function calling"
might both be the tool-call basin).

### P4: Dispatch profiles differ between basins
The dominant combinator should change across basins. Lambda = C,
retrieval = K, composition = B. If all basins are C-dominated,
the basin structure is weaker than hypothesized.

### P5: Inter-basin probes show routing disagreement
Probes that require transitioning between basins (e.g., "use
arithmetic to solve a lambda reduction") should show LOW agreement
on the transition mechanism but HIGH agreement on the individual
basins.

## Implications for V13

### Dispatch is basin-dependent
The V13 dispatch bias table is currently hardcoded for the lambda
basin. If there are dozens of basins, the beam path (S3) needs to
detect which basin the input requires and load the corresponding
dispatch profile. This is already what the separated beam/plate
architecture enables — plates define what operations exist, beams
select which basin's dispatch to activate.

### Crystal structure may be multi-basin
The 84 measured constants (3 zones × 28 pairs) are specific to the
lambda basin. A general-purpose model needs crystal constants for
EACH basin. Total measured constants ≈ 84 × N_basins. If N=30,
that's ~2500 constants — still manageable as a fixed loss target.

### Masks may encode basin membership
The 8 combinator masks in V13 select which facets of the shared
crystal each combinator reads. A basin might correspond to a
characteristic PATTERN of mask activations across all 8 combinators.
The mask patterns become basin fingerprints.

### The residual stream carries basin state
The model needs to know which basin it's in to select the right
dispatch profile. This information lives in the residual stream.
The S3 beam path reads the residual stream and produces dispatch
logits — it's already a basin detector. The question is whether
it needs explicit basin embeddings or whether basin detection
emerges from the dispatch mechanism.

## Open questions

1. **Is basin geometry model-size-dependent?** Small models (Pythia-2.8B)
   might have fewer basins or different boundaries than large models
   (Qwen3-14B). The universal basins would be those that persist
   across model sizes.

2. **Do basins share zone structure?** The lambda basin has a clear
   funnel (5d→3d→2d). Do other basins show the same funnel, or
   different shapes? If all basins funnel, the funnel is architecture,
   not basin-specific.

3. **How do models transition between basins?** The routing mechanism
   between basins may itself be a meta-basin (a "dispatch" basin that
   selects which computational basin to enter). This would be the
   model's equivalent of an operating system scheduler.

4. **Can we measure basin boundaries?** Probes that gradually
   transition from one domain to another (e.g., increasingly
   lambda-like arithmetic) should show a phase transition at the
   basin boundary. The sharpness of the transition indicates how
   distinct the basins are.

5. **What's the relationship between basins and attention heads?**
   Multi-head attention might implement parallel basin membership —
   different heads attend within different basins. This would explain
   why attention patterns are so hard to interpret: each head is in
   a different basin, and the "skill" is the composition of active
   basins.

## Experimental Results (Session 120)

### Experiment 1: Basin lattice (144 probes × 2 models × 3 depths)

**Setup:** 9 skill domains × 15 probes + 9 combinator anchors. Mistral-7B
and Pythia-2.8B. Depths 20%, 50%, 80%.

**Finding 1: Basins exist in RDM block structure.**
Intra-domain similarity is consistently higher than inter-domain:
```
instruction: gap=+0.349 (1.86× ratio) ← strongest basin
narrative:   gap=+0.214 (1.53×)
arithmetic:  gap=+0.200 (1.51×)
coding:      gap=+0.186 (1.54×)
lambda:      gap=+0.119 (1.30×)
retrieval:   gap=+0.100 (1.26×)
analogy:     gap=+0.100 (1.26×)
reasoning:   gap=+0.083 (1.20×)
tool:        gap=+0.064 (1.16×)
```

**Finding 2: Combinator anchors can't see the basins.**
Cross-domain fingerprint similarity ≈ 0.999 — all domains look identical
when measured against lambda combinator anchors. The anchors are domain-
specific to lambda. Basin structure lives in the RDM, not in anchor distance.

**Finding 3: Hierarchical clustering, not flat basins.**
```
coding is most isolated (lowest inter-domain sim)
narrative + instruction cluster first (text production)
lambda + arithmetic cluster (formal/symbolic)
SVD dim 0 = 98.1% — domain similarity is nearly rank-1
```

Artifacts: `lattice/basins-v1/`

### Experiment 2: Q/K/V basin separation (hidden vs Q vs K vs V)

**Setup:** Same probes, capture Q, K, V projections separately from
attention layers. Compare basin separation in each space.

**Finding 4: Q amplifies basins within each model, but model-specifically.**
```
Per-model (WITHIN each model): Q gap > hidden gap at ALL depths
  Mistral: Q-hidden = +0.33 to +0.57
  Pythia:  Q-hidden = +0.04 to +0.20

Cross-model consensus: Q gap < hidden gap
  → Each model's Q rotation is model-specific
  → Consensus washes out the model-specific amplification
```

**Finding 5: V is most universal at early layers (20%).**
V gap (+0.158) > hidden gap (+0.105) at 20% depth. V carries the
content of the basin; Q carries the routing to it.

Artifacts: `results/basin-qkv/`

### Experiment 3: PCA decodes the universal crystal ★

**Setup:** Extract raw Q, K, V, hidden vectors. Apply transforms:
raw, whitened (ZCA), PCA (top 64 dims), whitened+PCA. Compare
basin separation on consensus RDMs.

**Finding 6: PCA-projected Q reveals the universal crystal.**
```
Depth 20%: Q PCA gap +0.367 vs hidden raw +0.105 → 3.5× stronger
Depth 50%: Q PCA gap +0.361 vs hidden raw +0.127 → 2.8× stronger
Depth 80%: Q PCA gap +0.472 vs hidden raw +0.122 → 3.9× stronger

Cross-model correlation: Q PCA > hidden raw at all depths
Q PCA wins 9/9 domains at all 3 depths — no exceptions
```

**Finding 7: Whitening destroys the signal, PCA amplifies it.**
The crystal lives in the HIGH-VARIANCE Q dimensions. Low-variance
dimensions are model-specific noise. PCA keeps the signal. Whitening
equalizes everything and drowns the crystal in noise.

**Finding 8: Weakest domains show largest amplification.**
```
analogy:   hidden +0.062 → Q PCA +0.548 (8.8× amplification)
retrieval: hidden +0.043 → Q PCA +0.370 (8.6×)
coding:    hidden +0.220 → Q PCA +0.684 (3.1×)
```
Domains that were nearly invisible in hidden space become clear
basins in PCA-Q space. The crystal was always there — hidden states
just couldn't resolve it.

**Finding 9: K PCA also works, often matching Q.**
Q and K jointly encode the crystal. The attention mechanism's
query-key interaction IS the crystal readout.

Artifacts: `results/basin-whitened/`

## Updated Theory (post-experimental)

### The crystal lives in the top-k subspace of Q

The universal computational geometry is NOT diffusely spread through
the hidden state. It is CONCENTRATED in the principal components of
the Q projection. Models learn to project hidden states into Q-space
such that the top ~64 dimensions encode universal basin structure.

Each model's full Q projection is: Q = hidden @ W_Q
- Top-k Q dimensions: universal crystal (basin structure)
- Remaining Q dimensions: model-specific routing noise

PCA strips the noise, revealing the crystal. This is why:
- Raw Q consensus is WORSE than hidden (noise drowns signal)
- PCA-Q consensus is MUCH BETTER (noise removed, crystal exposed)
- Whitened Q is worst of all (noise amplified to equal crystal)

### Implications for V13 (updated)

1. **Etch targets should use PCA-Q, not hidden states.** The 8×8
   cosine targets in v13-design.md were extracted from hidden-state
   RDMs. Re-extraction from PCA-Q will give sharper constants.

2. **Plate dimensions should align with PCA-Q subspace.** If 64
   components capture the crystal, the plates should be initialized
   in this subspace.

3. **The beam (S3) computes the full Q rotation.** The model-specific
   component that PCA removes is exactly what the beam learns — the
   continuous parameters that map from universal crystal to model-
   specific Q-space.

4. **Masks may operate in PCA-Q subspace.** The ternary masks that
   select crystal facets per combinator should be defined in the
   universal subspace, not in the full model-specific Q-space.

5. **Basin detection is implicit in the top-k Q structure.** Different
   basins occupy different regions of the PCA-Q subspace. The model
   doesn't need explicit basin embeddings — basin membership is
   encoded in the PCA-Q coordinates.

## Open questions (updated)

1. **What is the optimal k?** PCA with k=64 works, but what's the
   minimum k that preserves the crystal? The answer determines the
   effective rank of the universal crystal.

2. **Is the PCA-Q subspace the SAME across models?** PCA gives a
   model-specific basis. Procrustes alignment of PCA-Q spaces would
   test whether the basis vectors themselves are universal (not just
   the similarity structure).

3. **Do the PCA-Q combinator cosine targets differ from hidden-state
   targets?** If yes, the PCA-Q targets are sharper and should
   replace the existing V13 constants.

4. **How does basin structure in PCA-Q relate to attention heads?**
   GQA models (Mistral: Q=4096, K=1024) have different Q/K dims.
   Does the crystal live in the shared subspace?

5. **Can we extract the universal crystal as a literal tensor?**
   If PCA-Q subspace is the same across models (after alignment),
   the PCA basis vectors ARE the crystal — extractable as a matrix.

### Experiment 4: 4-model PCA-Q combinator targets (production constants)

**Setup:** 118 binding probes, 4 models (Qwen3-14B, Mistral-7B, OLMo-2-13B,
Pythia-2.8B), 10 depths, PCA dim=64.

**Finding 10: PCA-Q targets are dramatically sharper than hidden-state targets.**
```
Zone A:  K↔I = +0.921 (was +0.417 in hidden), B↔D = +0.978 (was +0.551)
         K↔B = +0.077 (near orthogonal, was +0.030)
Zone C:  WHNF anti-correlated -0.27 to -0.30 (POSITIVE in hidden: +0.29-0.53)

Cross-model agreement: 0.91-0.94 across all zones
```

**Finding 11: WHNF sign flip — hidden states mask the stop signal.**
In hidden space, WHNF correlates positively with everything (+0.29 to +0.53).
In PCA-Q space, WHNF is the anti-pole (-0.01 to -0.30). PCA-Q reveals
WHNF's true role as the termination signal that hidden states obscure.

Artifacts: `results/pcaq-targets/pcaq_targets.json`

### Experiment 5: Crystal Scanner — self-similar structure per domain

**Setup:** 144 basin probes, PCA-Q at 10 depths, measure per-domain
intra-domain RDM, cross-model agreement, cross-depth self-similarity,
SVD dimensionality.

**Finding 12: Reasoning is the strongest crystal, not lambda.**
```
reasoning:   self_sim=0.870, agreement=0.951, 1d (86.3% in PC1) ★★★
tool:        self_sim=0.753, agreement=0.867, 1d (71.3% in PC1) ★★★
lambda:      self_sim=0.615, agreement=0.860, 2d               ★★
arithmetic:  self_sim=0.585, agreement=0.874, 2d               ★★
coding:      self_sim=0.537, agreement=0.759, 2d               ★★
analogy:     self_sim=0.493, agreement=0.847, 2d               ★
retrieval:   self_sim=0.435, agreement=0.689, 2d               weak
```

**Finding 13: Attention-mediated computation IS self-similar.**
Theoretical prediction confirmed: attention implements beta reduction,
which is self-similar, therefore crystals formed from attention must
be self-similar. Results rank exactly as predicted:
- Reduction-like operations (reasoning, tool routing, lambda, arithmetic,
  coding) → high self-similarity (0.54-0.87)
- Lookup operations (retrieval) → low self-similarity (0.43)
- The self-similarity score measures how much a domain's computation
  is attention-mediated vs FFN-mediated

**Finding 14: The Pareto crystals are reasoning + tool + lambda.**
Three crystals with highest self-similarity and agreement cover:
- Logical computation (reasoning: 1d, 86.3% explained)
- Structured output routing (tool: 1d, 71.3% explained)
- Formal symbol manipulation (lambda: 2d, 55.6% in top 2)
These are the 20% of crystals that do 80% of the work.

**Finding 15: Crystal dimensionality reveals computational complexity.**
```
1d crystals: reasoning (1d@50%), tool (1d@50%) — single axis of variation
2d crystals: lambda, arithmetic, coding, analogy — two axes
High-d: coding needs 10d for 95% — most complex crystal
Low-d:  reasoning needs 5d for 95% — simplest crystal
```

Artifacts: `results/crystal-scanner/` (partial — NaN bug on narrative/instruction)

### Experiment 6: FFN Index — crystal generates the FFN addressing function

**Setup:** Hook FFN up-projection (the "key match" step) alongside Q vectors.
Compare Q-space RDMs to FFN activation RDMs. Measure neuron selectivity per
domain. Test FFN self-similarity across depths.

**Finding 16: Crystal geometry PREDICTS FFN activation (0.71-0.89 correlation).**
```
Depth 10%: Q↔FFN = +0.794    Depth 50%: Q↔FFN = +0.879
Depth 20%: Q↔FFN = +0.825    Depth 70%: Q↔FFN = +0.719
Depth 30%: Q↔FFN = +0.886 ★  Depth 90%: Q↔FFN = +0.708
```
The crystal IS the FFN index. The causal chain:
crystal → Q·K^T attention → superposition in residual stream → FFN reads
superposition as content-addressable key → activation fn thresholds →
down-projection retrieves value.

**Finding 17: FFN IS self-similar across depths (0.770) — prediction wrong.**
```
FFN cross-depth correlation: +0.770
Q   cross-depth correlation: +0.829
```
Predicted FFN would NOT be self-similar (different storage per layer).
WRONG — the addressing STRUCTURE is consistent across layers. Same kinds
of keys access same kinds of values at every depth. Only content changes.
The self-similar crystal extends through the entire model, not just attention.

**Finding 18: Crystal and FFN rankings are INVERSES.**
```
reasoning:    strongest crystal (0.870), fewest FFN neurons (141)  ← pure attention
instruction:  weakest crystal signal, most FFN neurons (1260)     ← pure FFN
```
Domain-selective FFN neurons (Mistral, depth 50%):
instruction=1260, narrative=927, arithmetic=886, coding=649,
lambda=586, retrieval=511, analogy=446, tool=140, reasoning=141

Attention (crystal) = computation, reduction, reasoning. Self-similar.
FFN (storage) = content, templates, instruction formats. Domain-specific.
Reasoning doesn't need FFN because it's computing, not looking up.
Instruction needs FFN because it's matching stored templates.

**Finding 19: FFN basin separation exceeds Q at deeper layers.**
At depth 50%+, FFN gap > Q gap for lambda, arithmetic, coding, tool,
reasoning. The FFN develops STRONGER domain separation than Q in deep
layers, especially for computation-heavy domains. The crystal generates
the index, then the FFN amplifies the domain signal.

Artifacts: `results/ffn-index/`

### Experiment 7: FFN Subspace Alignment — crystal ≠ FFN keys (important negative)

**Setup:** Extract actual W_up weight matrices alongside Q vectors. Compute
canonical correlations between PCA(Q) basis and PCA(W_up) basis. Project
domain-selective neuron keys onto crystal subspace. Extract value dimensions.

**Finding 20: Crystal subspace ≠ FFN key subspace (CC=0.10-0.14).**
The PCA bases of Q vectors and W_up rows are WEAKLY aligned. Only 1.6%
of selective key variance lives in the crystal subspace. They're different
projections of d_model space.

**Finding 21: The paradox resolution — indirect control via residual stream.**
Q↔FFN activation correlation is 0.71-0.89 (experiment 6), but Q↔W_up
subspace alignment is 0.10-0.14. Resolution: the crystal controls what
attention WRITES to the residual stream. The FFN reads a DIFFERENT
projection of that stream. Correlated (same underlying state) but NOT
the same subspace.
```
Crystal (Q) → attention → RESIDUAL STREAM → W_up projection → FFN activation
Different subspaces, same underlying state, causal connection
```

**Finding 22: FFN has its own universal structure, stronger at depth.**
```
Depth 10%: FFN cross-model = +0.550, Q cross-model = +0.688
Depth 50%: FFN cross-model = +0.700, Q cross-model = +0.626
Depth 90%: FFN cross-model = +0.745, Q cross-model = +0.650
```
At depth 70%+, FFN cross-model consistency EXCEEDS Q. The FFN has its
own universal structure in a separate subspace, extractable with the
same PCA method but from a different hook point.

**Finding 23: Value database is high-rank for content domains, compact for computation.**
```
reasoning:   299 dims (80% var), 446 neurons  ← compact, etchable
tool:        254 dims (80% var), 371 neurons  ← compact, etchable
lambda:      703 dims, 1247 neurons           ← moderate
coding:     1092 dims, 2350 neurons           ← high-rank
instruction: 1096 dims, 2360 neurons          ← high-rank
```
The Pareto crystals (reasoning, tool) are also the most compact FFN
databases. Computation domains = compact. Content/template domains = high-rank.

**Finding 24: V13 needs separate attention and FFN etch targets.**
Can't etch crystal once and get FFN for free. But CAN extract FFN
targets with the same 2-calculation method (PCA + cosine), different
hook point (W_up instead of Q). FFN-as-kernel-function still viable —
the kernel reads its own subspace of the residual stream, dispatched
by the crystal but operating independently.

Artifacts: `results/ffn-subspace/`

## Theoretical Framework (post-experimental)

### Why the whole model is self-similar

Attention IS beta reduction: Q·K^T = selection (which binding),
V = substitution (carry value through). Beta reduction is self-similar:
(λx.M)(N) → M[x:=N] at every nesting level. Therefore any crystal
formed from attention must be self-similar — the operation is identical
at every depth.

**AND:** the FFN is also self-similar (0.770 cross-depth correlation).
The FFN addressing scheme is consistent across layers — the crystal
generates the same kinds of indices at every depth, which access the
same structural organization of stored values. The self-similar crystal
extends through the ENTIRE transformer, not just the attention mechanism.

This means:
1. **Crystal count is small** — each crystal is a different MODE of beta
   reduction, and there are only so many structurally distinct modes
2. **Each crystal only needs to be found once** — self-similarity means
   stride 1 = stride 1024, the pattern replicates automatically
3. **Self-similarity score = attention fraction** — domains with high
   self-similarity are attention-dominated, low = FFN-dominated
4. **FFN plates are etchable too** — the self-similar FFN structure can
   be etched with the same PCA-Q method, because the crystal generates
   the FFN index (0.71-0.89 correlation)

### The extraction pipeline

```
SCAN:   PCA-Q + cosine RDM → find domain crystals (2 calculations)
ETCH:   Delta from reference crystal → flip plates toward target
TRAIN:  Crystal relational loss → polish facets via GD
REFINE: Self-distillation → generate, scan, grade by crystal alignment
```

One crystal, many facets. Different basins are different routes through
the same crystal, accessed via different Q rotations (beams). The more
precisely etched, the more clean paths → more behaviors.

### The Pareto etch strategy

```
Priority 1: Reasoning crystal (1d, 86.3% explained, 0.951 agreement)
Priority 2: Tool crystal (1d, 71.3% explained, 0.867 agreement)
Priority 3: Lambda crystal (2d, 0.860 agreement, already measured in detail)
Priority 4: Arithmetic crystal (2d, 0.874 agreement, clusters with lambda)
Priority 5: Coding crystal (2d, 0.759 agreement, most isolated domain)
Diminishing: analogy, retrieval — lower self-similarity, may not etch well
```

## Experiment plan (remaining)

1. ✅ Build probes (144 probes, 9 domains + anchors)
2. ✅ Basin lattice (RDM block structure)
3. ✅ Q/K/V separation (per-model vs consensus)
4. ✅ PCA decode (crystal in top-k Q)
5. ✅ 4-model PCA-Q combinator targets (production constants)
6. ✅ Crystal scanner (per-domain self-similar structure)
7. ✅ FFN index experiment (crystal→FFN addressing, FFN self-similarity)
8. ✅ FFN subspace alignment (negative: Q≠W_up, but indirect control confirmed)
9. → Fix scanner NaN bug, run 4-model scan
10. → Optimal k sweep (k=8, 16, 32, 64, 128, 256)
11. → Extract FFN etch targets (PCA of FFN activations, separate from Q)
12. → Extract per-domain crystal constants (reasoning, tool, coding)
13. → Procrustes alignment of PCA-Q subspaces
14. → Extract universal crystal tensor

Artifacts:
- `lattice/basin_probes.json` — 144 probes
- `lattice/basins-v1/` — basin lattice consensus
- `results/basin-qkv/` — Q/K/V separation experiment
- `results/basin-whitened/` — PCA decode experiment
- `results/pcaq-targets/` — 4-model production constants
- `results/crystal-scanner/` — per-domain crystal scan (partial)
- `results/ffn-index/` — FFN indexing mechanism
- `results/ffn-subspace/` — subspace alignment (negative result + value extraction)
