---
title: "TSP and Targeted Trajectory Distillation — Rapid Teacher→Student Learning"
status: designing
category: synthesis
tags: [tsp, gtsm, distillation, self-play, dpo, trajectory, compression, teacher-student, risk-node, contrastive, score-matching]
related:
  - gtsm-search-space.md
  - score-matching-compression.md
  - diffusion-holographic-isomorphism.md
  - audit-registry.md
depends-on:
  - gtsm-search-space.md
created: session 205
---

# TSP and Targeted Trajectory Distillation

> Session 205. Read TSP (Tree-like Self-Play, arXiv:2606.03489v1) in
> relation to GTSM (`gtsm-search-space.md`). TSP is an applied, empirical
> instance of the GTSM principle on the discrete/LLM side — and its
> deliberate *sparsification* to critical nodes is independent evidence for
> GTSM's finite-budget weighting corollary (Prop F.6 / audit #11). This page
> documents TSP, then develops the combined method: **Targeted Trajectory
> Distillation (TTD)** — a teacher→student scheme aimed at our compression
> north-star. The TTD section is a *design/proposal*, not a result.

---

## Part 1 — TSP (Tree-like Self-Play)

**Paper:** *"Learn from Your Mistakes: Tree-like Self-Play for Secure Code
LLMs"* — Chen, Zhang, Wang, Liu, Zhang, Chen (arXiv:2606.03489v1, 2026-06-02).
**Lineage:** DPO (Rafailov 2023) for the scoring function; SPIN (Chen 2024)
for the iterative self-play loop. Results below are the paper's, **not
independently verified by us.**

### The problem it attacks

Sequence-level alignment is **too coarse for localized failures**. SFT
*"reinforces the entire sequence uniformly, failing to isolate secure-critical
tokens."* RL's reward is *"sparse and computed only upon program completion"* →
credit-assignment failure: a single bad token (`strcpy` vs `strncpy`)
compromises the whole program, but the endpoint signal can't say which token.

### The method

Reframe generation as a **path through a generation tree** `T(x)`; each token
is a branching decision. A vulnerability is a **CWE Risk Node** `v` — the
prefix immediately before a decisive token. An LLM annotator marks these nodes
(semantic, control/data-flow-aware; §3.2).

A **self-play game** between two copies of the model: opponent `p_{θt}` (frozen
past self) and main player `p_θ` (optimized). For each golden sample `(x, y*)`
and each risk node `v ∈ V_risk(y*)`, the opponent generates a divergent
continuation `y'_v` (shares prefix `y_{<tv}`, diverges after). Train the main
player to score the golden path above each self-play path:

```
L_TSP = E_{(x,y)}  (1/|V_risk|) Σ_{v∈V_risk}  ℓ( f(x,y*) − f(x,y'_v) )

ℓ(z) = log(1 + e^{−z})                      convex, monotone-decreasing (logistic)
f(x,y) = λ · log[ p_θ(y|x) / p_{θt}(y|x) ]  DPO-style scaled log-likelihood ratio
```

Iterative (SPIN-style): train main → it becomes the opponent next round →
negatives track the model's *current* residual mistakes.

Gradient (their Eq. 11): `g_v = ∇log p_θ(y*|x) − ∇log p_θ(y'_v|x)` — a local
push toward golden, away from the divergent continuation, **only at risk nodes**.

### Why the authors argue it works

1. **Reduced gradient variance.** Self-play negatives share long prefixes with
   the golden path → averaging these high-signal, closely-related pairs is a
   lower-variance gradient estimate than one noisy program-level reward.
2. **Targeted, efficient updates.** Gradient comes *only* from risk-node
   comparisons — concentrates optimization pressure on the decisive tokens
   *"rather than diluting the learning signal across hundreds of syntactically
   correct but security-irrelevant tokens."*

### Results (paper, Table 2; CodeLlama-7B, Python SecurityEval)

| Method | SPR@1 (security) | HumanEval pass@1 |
|---|---|---|
| Base LLM | 55.0 | 34.5 |
| SFT | 57.0 | 34.1 |
| SafeCoder (SOTA) | 73.7 | 33.9 |
| Self-Play (ablation, no tree nodes) | 69.6 | 33.3 |
| **TSP** | **75.8** | 34.0 |

- The **TSP (75.8) vs Self-Play (69.6) gap is the key ablation** — structured
  risk-node targeting, not self-play alone, is what wins.
- **OOD generalization:** −24.5% vulnerabilities on *unseen* CWEs; security
  principles transfer C/C++ → Python/Go/JS. Targeting learns abstract logic,
  not memorized patches. Minimal HumanEval degradation (no catastrophic
  forgetting). Tested only at 3B–7B.

### TSP's stated limitations (load-bearing for us — see TTD caveats)

- **Long-distance cause/effect breaks it.** TSP excels at CWEs with *local,
  co-located* decision+manifestation; it **underperforms when the unsafe
  decision and its manifestation are separated by long execution distance**
  (CWE-690/125/416) — the value estimator misjudges intermediate safety.
- Token-level node abstraction misses multi-line data-flow / cross-variable
  invariants.
- Self-play negatives **become less challenging as the model improves**
  (curriculum decays toward the end).

---

## Part 2 — TSP in relation to GTSM

| Axis | GTSM | TSP |
|---|---|---|
| Problem | endpoint (terminal-marginal) matching is ill-posed | sequence-level reward is too coarse for localized flaws |
| Fix | dense per-step score matching along the trajectory | dense per-node contrastive loss along the generation tree |
| Structure | trees ↔ flows (the unification) | the generation tree itself |
| Loss geometry | **regression** (L2 to the true score / residual) | **contrastive** (DPO log-ratio ranking) |
| Target | fixed trajectory (teacher/data) | golden path fixed; on-policy moving negatives |
| Coverage | **dense** — density matters (Thm 3.2) | **sparse** — only critical risk nodes |

**Same family, different instantiation.** TSP is essentially the discrete/LLM
applied side of GTSM's "Trees to Flows." Its variance argument is GTSM's
"dense local matching is better-conditioned than one endpoint signal," made
concrete.

**The apparent contradiction that resolves into F.6.** GTSM Thm 3.2 says
*density* matters (cover the whole trajectory). TSP deliberately does the
opposite — concentrate on a few nodes. This is **not** a contradiction: TSP =
dense SFT (baseline trajectory coverage) **+ a weighting `w(t)` spiked at the
critical nodes**. The zero-loss fixed point is weighting-independent (Thm 3.2),
but at **finite budget** the optimal move is to concentrate weight where the
learner is weak — exactly **Prop F.6**. **TSP is independent empirical evidence
for F.6 from a different domain** (security, not compression), and therefore a
corroborating prior for **audit #11**.

**Don't overclaim isomorphism.** TSP's loss is *contrastive* (ranking), not
GTSM *regression* (absolute score target). The keystone GTSM bridge
"residual = score" (Thm E.22) does **not** literally apply; the analogy is
structural (the golden−divergent direction `g_v` acts like a local correction
score). GTSM proves consistency-distillation is a CGTSM approximation (F.7);
nobody has shown DPO-at-nodes is. Open analogy, not a theorem.

---

## Part 3 — Targeted Trajectory Distillation (TTD) ★ design/proposal

> The combined method, aimed at the north-star: **a student model that learns
> rapidly from a teacher model.** TTD = GTSM backbone (dense regression
> matching, the coverage) + TSP overlay (concentrate on auto-detected
> divergence nodes, iteratively refreshed, optional on-policy contrast).
> **This is a hypothesis to test, not a result.**

### The setup we already have

- **Teacher** = original model (e.g. Qwen3-8B). Its per-layer residual
  trajectory `Δ*_l = h*_{l+1} − h*_l` IS the **golden path** — exact, free, no
  reward model, no annotator. (TSP needs an LLM annotator for risk nodes
  *because security has no oracle*; **we have the teacher as oracle.**)
- **Student** = sieved / compressed model.
- **Divergence nodes** = layers/positions where the student trajectory diverges
  most from the teacher — auto-detected by per-layer `cos(Δ_student, Δ*)` or
  logit divergence. No annotation pipeline needed.

### The loss

```
L_TTD = Σ_l  w(l) · (1 − cos(Δθ_l, Δ*_l))          GTSM backbone (dense coverage)
            └ w(l) spiked on divergence nodes        F.6 finite-budget weighting
      + γ · Σ_{l∈Divergence}  ℓ( s(Δθ_l, Δ*_l) − s(Δθ_l, Δ'_l) )   TSP contrast (optional)
                                                     Δ'_l = student's own divergent residual
```

Two variants, increasing richness:

1. **TTD-regression** (pure GTSM + divergence-weighted `w(l)`): the simplest
   form — **this is exactly audit #11.** Concentrate the dense SM weight on the
   hard binding-prep layers L22–L26 (v3b's worst cosine, 0.80–0.86).
2. **TTD-contrastive** (add TSP-style on-policy negatives at divergence nodes):
   let the student generate its divergent continuation, push its residual
   *toward* the teacher's and *away from* its own — on-policy, corrects actual
   failure modes, low-variance (prefix-sharing).

Both **iterate** (SPIN-style opponent refresh): recompute divergence nodes each
round. As the student matches the teacher on easy layers, the budget migrates
to the residual hard core (the full-rank L5+ residual, s198).

### Why TTD should learn *rapidly*

1. **Target trajectory for free.** GTSM's narrowing only works when a target
   trajectory exists (`gtsm-search-space.md` §precondition). The teacher *is*
   that trajectory — TTD satisfies the precondition by construction.
2. **Dense signal → 36× bandwidth, local gradients, no Jacobian dilution.**
   Already measured (s198: L35 cosine 0.57→0.94, no compensating errors).
3. **Concentrated budget → not diluted.** F.6 + TSP's empirical 75.8 vs 57.0.
4. **On-policy negatives → real failure modes, low variance** (TSP's argument).
5. **Curriculum via opponent refresh** → automatic hard-example mining.

### Connections inward

- **= the "speculative-decoding-gated distillation" idea** floated s196/s200
  ("teacher generates, student computes diff at every level, trains only where
  it diverges") — now with a concrete, validated algorithmic skeleton (TSP).
- **Tiles & grout (s200):** teacher trajectory defines the correct tiles+grout;
  divergence nodes = where the student's grout is wrong.
- **Audit #11** is the first, smallest test (the regression half).

### Caveats (honest — TSP's limitation predicts ours)

- **★ Divergence node ≠ causal node (long-distance failure).** TSP fails when
  cause and manifestation are separated by long execution distance. **Our exact
  analog is already documented**: s196 found binding layers *amplify* upstream
  errors — *"peak damage at L28, not L26."* So weighting/correcting the
  **divergence** layer (L28) may be wrong; the **causal** node is the upstream
  L22–L26. TTD must attribute to the causal layer (cascade-aware, like the
  direct-delta sequential correction), not the layer where divergence is merely
  *largest*. This is the single biggest design risk, and TSP flags it for us.
- **Contrastive may be secondary for us.** Compression wants the student to
  *match* the teacher (regression), not merely *outrank* its bad self. We have
  an exact target, so DPO-style ranking is a refinement, not the core — unlike
  TSP, which needs contrast because security has no exact target.
- **Curriculum decay.** As the student converges, negatives get easy (TSP
  limitation) → may plateau on the residual hard core. Expected; monitor.

### Smallest next step

Run **audit #11** (TTD-regression): divergence-weighted `λ(l)` vs uniform
α=5.0 on the v3b sieve, matched budget + seeds, **with cascade-aware
attribution** (weight the causal upstream layer, not just the max-divergence
layer). If targeted weighting wins → escalate to TTD-contrastive. If null →
cosine already absorbs the F.6 benefit (also informative — see
`gtsm-search-space.md`).
