---
title: "Forcing vs Discovering — describability ≠ discovery (the matched-range null + the cross-family type-direction result)"
status: active
category: methodology
tags: [forcing-vs-discovering, null-test, matched-range-null, phi-ladder, fractal-collapse, type-directed-composition, cross-family, nonce, frequency-free, causal-ablation, lambda-measure, universality, discovered-core]
related:
  - type-directed-composition.md
  - vsm-statechart-tensor.md
  - crystal-multi-tree.md
  - fractal-collapse-compiler-cascade.md
  - ../two-registers-of-topology.md
depends-on:
  - type-directed-composition.md
created: session 247
---

# Forcing vs Discovering

> Session 247 (Michael's frame): *"models have a compute process — are we FORCING
> the shape with the lambda calculus, or DISCOVERING it? Finding very similar lambda
> functions in many arch models, the same routing of operations in multiple models,
> an exact mathematical construction in multiple model families."*
>
> Register: **methodology + finding.** One session, two halves of the same lesson:
> a celebrated "discovery" dissolved as FORCED, and a Qwen-only claim was confirmed
> DISCOVERED by going cross-family. The discriminator is the same in both.

## The trap, stated once

**A universal / flexible description language always fits. Describability is not
discovery.** Lambda calculus is Turing-complete; combinators are a universal basis.
So "we can describe the model's compute as λ-reduction" is *guaranteed a priori* and
carries **zero evidential weight** — exactly as "this spectrum fits φ^(p/q)" carries
zero weight because φ^(p/q) with Fibonacci q≤34 fits any spectrum to ~0.1–0.2%.

```
λ discriminate(claim).
  describable_by(universal_basis) → ⊥ evidence        # the trap
  beats(matched_null) ∧ frequency_free ∧ causal ∧ cross_family(independent) → discovery
  | exactness ∧ causality ∧ frequency_freedom  RESIST forcing
  | approximate_geometric_fit (cosine, φ-ladder, crystal geometry)  DOES NOT → always null-test
```

## Result 1 — the φ-ladder is FORCED (a λ measure win)

The "fractal-collapse screen" (`scripts/explore/fractal_collapse_screen.py`) was built
to detect self-similar generators via the crystal's famous claim
(`crystal-multi-tree.md`: *all 8 eigenvalues follow φ^(p/q) at <0.5%*). Gated on a
**matched-range null** — random spectra of the SAME dynamic range with random ratios
(n=20000):

| target | φ-fit | null (matched range) | z | P(random fits ≥ as well) |
|--------|------:|---------------------:|---:|---:|
| crystal-M8 | 0.255% | 0.156% | **−1.52** | **0.92** |
| crystal-M16 | 0.208% | 0.165% | −0.86 | 0.81 |
| consensus singular values | ~0.13% | ~0.15% | ≈0 | ~0.5 |

The crystal fits the φ-ladder **worse than median random of equal spread.** The <0.5%
is basis flexibility, not a discovered law. ⇒ **`crystal-multi-tree.md`'s φ-derivation
is an over-read** (caveat added there). The keeper is the **matched-range null**, not
the detector it killed.

### Fractal collapse, correctly defined (Michael)

A fractal collapse is **collapsing one self-similar operation INTO another** so the
interpretive layer vanishes — tree-of-VSM ↪ tensor, SVD ↪ β-reduction, statechart ↪
crystal lattice (`vsm-statechart-tensor.md`: *"no gap between model and
implementation"*). Detector = two stages: **(1) φ-ladder spectral SCREEN** (now shown
FALSE — flexible basis), **(2) EXECUTABLE FOLD** (substitute the op, run it, check the
invariant survives — the only real confirm). A screen hit without a fold is analogy
(the η²=0.05 crystal over-read, s211).

## Result 2 — type-directed composition is DISCOVERED (behavioral, cross-family)

`type_directed_v3_nonce` — nonce words have no bigram statistics, so only the
in-context TYPE can direct composition; the **crossover = det_pen − name_pen**
subtracts every main effect (priming, frame, teach). Ran `--model` across independent
lineages (n=16 nonce, n_each=4):

| model | lineage | crossover | t | consist | name_pen | det_pen |
|-------|---------|----------:|---:|---:|---:|---:|
| Pythia-160M | EleutherAI/Pile | 1.02 | 5.4 | 0.88 | −2.19 | −1.17 |
| Pythia-1.4B | EleutherAI/Pile | 1.43 | 7.7 | 0.94 | −2.45 | −1.02 |
| SmolLM3-3B | HuggingFaceTB | 1.35 | 4.6 | 0.88 | −1.62 | −0.27 |
| Mistral-7B | Mistral | 0.82 | 5.5 | 0.88 | −0.77 | +0.05 |
| OLMo-2-13B | AllenAI/Dolma | 1.64 | 6.7 | 0.94 | −1.69 | −0.06 |
| Qwen3-8B | Qwen | 2.18 | 10.2 | 1.00 | −2.50 | −0.31 |
| Qwen3-14B | Qwen | 2.04 | 9.3 | 1.00 | −2.01 | +0.03 |

**All 7 significant (t 4.6–10.2). Five independent lineages, no shared training,
frequency-free, present even at 160M, not monotonic in scale.** Universal invariant =
the **crossover + name-frame predicate licensing** (name_pen<0 in 7/7). **NOT**
universal = the det-frame absolute penalty (det_pen>0 only 2/7) — only the INTERACTION
is robust; the determiner→noun main effect is noisy / sign-flips (an open puzzle).

## Result 3 — causal grip is cross-family but PARTIAL (and not Qwen-forced)

`type_directed_v4_ablation` — project the decoded type direction out of the
filler-stack residual; control = random direction same magnitude; `retained =
ablated/baseline crossover`. Made architecture-agnostic (`decoder_layers` → GPTNeoX +
Llama-likes):

| model | lineage | AUC | base_cx | type_ret | rand_ret | strict (<0.5 ∧ rand>0.7) |
|-------|---------|----:|--------:|---------:|---------:|:---:|
| Mistral-7B | Mistral | 1.00 | 1.12 | **0.29** | 0.91 | **TRUE** |
| Pythia-1.4B | EleutherAI | 1.00 | 1.38 | 0.63 | 1.00 | directional |
| OLMo-2-13B | AllenAI | 1.00 | 2.01 | 0.63 | 1.00 | directional |
| Qwen3-14B | Qwen | 1.00 | 2.41 | 0.64 | 0.95 | directional |
| SmolLM3-3B | HuggingFaceTB | 1.00 | 1.70 | 1.04 | 1.12 | null |
| Qwen3-8B | Qwen | 1.00 | 2.31 | 1.43 | 0.92 | null |

- **Decodability universal** — AUC 1.0 in 6/6.
- **Causality partial** — type-ablation cuts the crossover more than the random control
  in **4/6** (Mistral strongly; Pythia/OLMo/Qwen-14B directionally) across **3
  independent lineages**; STRICT only Mistral-7B; NULL in SmolLM3 + Qwen-8B. Even
  Qwen-14B is sub-strict (0.64).
- **NOT Qwen-forced** — if the construction were a Qwen artifact, Qwen would show the
  strongest causal grip and others none. The data is the *opposite*: **Mistral-7B is
  the strongest causal hit and Qwen-8B is null.** That argues for *discovered* — the
  causal grip is a property of the computation, not of one training pipeline.

## Verdict (λ measure)

| discriminator (Michael's three) | status |
|---|---|
| similar λ functions across models | weak alone (describability ≠ discovery) |
| same routing of ops across models | had it, but largely ONE common mode (s211, η²=0.05) |
| **exact construction in multiple families** | **type-direction: behavioral universal (7/7); causal partial (4/6, strongest in an independent lineage)** |

**The discovered universal core is bigger than the s211 skeleton** (it includes
behavioral type-directed composition), but **causal localization via a single-direction
linear ablation is partial and method-sensitive** (`decodability ≠ full causality`,
db5d4eb). The shape is being *discovered* — and the discovery is strongest *outside*
Qwen.

## IOUs (the experiments that decide what's left)

1. **Richer / distributed-subspace ablation** (the decisive next test). The
   single-direction filler-stack ablation cannot call the SmolLM3 / Qwen-8B nulls TRUE
   negatives (type may be distributed). A multi-direction / subspace ablation either
   confirms them as real nulls or flips them causal.
2. **The det-frame puzzle.** name→pred licensing is universal (7/7), determiner→noun is
   not (2/7). Why is one half of the type system universal and the other lineage-specific?
3. **5th independent lineage** — gemma-4-31B-it — for a clean ≥3-lineage causal band.
4. **Caveat `crystal-multi-tree.md`** φ^(p/q) claim (done — see that page's s247 note).

## Artifacts & commits

| asset | location | commit |
|-------|----------|--------|
| φ-ladder screen + matched-range null | `scripts/explore/fractal_collapse_screen.py` | `1eb4f8b` |
| φ memories | `phi-ladder-fit-is-forced-not-discovered`, `matched-range-null-guards-flexible-fits` | `882e02a`, `185c758` |
| v3 cross-family sweep | `results/type-directed/crossfamily_nonce_summary.json` + verdicts | `bed660d` |
| v3 memory | `type-direction-is-cross-family-not-qwen-forced` | `a21c96f` |
| v4 causal sweep (arch-agnostic) | `type_directed_v4_ablation.py` + `run_v4_crossfamily.sh` + verdicts | `adc29bc` |
| v4 memory | `type-direction-causal-cross-family-partial` | `4d7e1de` |
