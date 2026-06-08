---
title: "Crystal Validity & Measurement Fidelity — What Survives the Permutation Null"
status: active
category: foundational
tags: [crystal, KIBC, phi, validity, permutation-null, common-mode, fidelity, falsification, I-combinator, fact-retrieval, holographic]
related:
  - crystal-universality.md
  - crystal-phi-derivation.md
  - mechanism-extraction.md
  - holographic-computer.md
  - project-thesis.md
depends-on:
  - crystal-universality.md
  - crystal-phi-derivation.md
---

# Crystal Validity & Measurement Fidelity

> Session 202. A skeptical audit: *can the crystal evidence be
> manufactured by a false premise, because LLMs (and analysts) are
> primed to confirm?* Six controlled experiments with permutation
> nulls. The verdict is nuanced and important: **the KIBC basis is
> real, but most of the machinery that made it feel like a universal
> mathematical constant does not survive its own controls — and the
> one thing that rescued the real signal was measurement fidelity
> (common-mode removal), exactly as hypothesized.**

## The Question

The φ-universality story rested on three pillars that felt "impossible
to deny": cross-model eigenvalue (φ) correspondence, cross-model crystal
agreement (r≈0.99), and a tracer whose opcode patterns correlated across
models. The worry (Michael, s202): a plausible-but-false premise can
produce convincing-looking structure, because both the model and the
analyzing LLM are trained to support the framing. Test it with nulls.

Key reframing discovered early: **89% of crystal probes are pure prose**
(only 11% contain `λ`/"lambda"), and the activation-geometry measurement
injects **no preamble**. So the real confound is not lambda notation or
priming — it is the *experimenter's grouping of prose → combinator*. The
permutation null tests exactly that: shuffle which prose belongs to which
combinator and see whether the true grouping is special.

## The Verdict Ledger

| Claim | Test | Verdict |
|---|---|---|
| KIBC grouping organizes representation | separation perm-null | ✅ **REAL, every model** (p=0.0005) |
| φ^(4/5) primary eigenvalue ratio | λ₀/λ₁ vs φ^(4/5), perm-null | ✅ **REAL on Qwen3-14B only** (p=0.020) |
| φ as a universal constant (all models) | same, across scale | ❌ 8B p=0.33, 0.6B p=0.60 — **not universal** |
| "eigenvalues are powers of φ^(p/q)" | best-fit grid, perm-null | ❌ **unfalsifiable** (random fits equally, p=0.16–0.81) |
| eigenvalue_ratio_correlation ≈ 0.987 | perm-null | ❌ **trivial** (random ≈ 0.94, often > true; p=0.38–0.92) |
| cross-model consensus r ≈ 0.99 | corr to CONSENSUS_8x8, perm-null | ⚠️ true ≈ 0.20, null max ≈ 0.48, p≈0.05–0.07 — **weak/chance** |
| cross-model crystal agreement (universal) | KIBC matrix corr across families | ⚠️ Qwen↔Qwen 0.88; **Pythia↔Qwen ≈ 0; Pythia↔Pythia −0.11** |
| prose fires combinator-specific opcodes | classification + common-mode removal | ✅ **CONFIRMED** (14B & 0.6B, p=0.001) — fidelity was the failure |
| I is a distinct low-composition circuit | attention entropy, perm-null | ◑ **PARTIAL** (14B p=0.042, scale-dependent) |
| fact retrieval = sharp lookup, I-like | entropy + opcode profile | ✅ entropy p=0.0005 both scales; I-profile (cos 0.98) 14B-only |
| tracer cross-model opcode overlay | overlay corr, opcode-label perm-null | ✅ **REAL but same-family** (p=0.0005, all Qwen, λ-primed) |

## Experiments (harnesses in `scripts/experiments/`)

### 1. `crystal_validity.py` — label permutation battery
Q-proj activations, 4 models (Pythia-160M/410M, Qwen3-0.6B/4B).
- **Permutation null:** KIBC separation is a sharp outlier vs random
  prose regroupings in every model (p ≤ 0.027, mostly 0.001).
- **Pure-prose filter:** dropping all 57 λ-probes *increases* separation
  → not a notation artifact.
- **Fake combinators** (negation/tense/quantification): separate *better*
  than KIBC (lexical surface clustering) → KIBC is **not privileged** on
  raw separability. Separation ≠ proof of a privileged basis.
- **Preamble A/B:** crystal geometry cosine 0.86–0.998 → preamble does
  not create the geometry.
- **Cross-model KIBC matrix corr:** Qwen↔Qwen +0.88; Pythia↔Qwen ≈ 0;
  Pythia↔Pythia −0.11. The "universal agreement" is **same-family only**.

### 2. `crystal_phi_permnull.py` — the ORIGINAL pipeline under its own null
Wraps `verify_crystal_phi.py` (gate_proj, Zone-B, PCA, CONSENSUS_8x8).
Models: Qwen3-14B/8B/0.6B, Pythia-410M. n_perm=2000.
- **φ best-fit grid:** the `p∈[−8d,0], d∈[1,12]` search makes φ^(p/q)
  values dense in [0,1] → *any* spectrum fits to <1%. True p=0.16–0.81
  (random fits as well). **Unfalsifiable by construction.**
- **λ₀/λ₁ vs the single pre-registered target φ^(4/5)=1.4696:**
  - Qwen3-14B: **1.4796, dist 0.010, p=0.020** ✅ (null mean 1.63)
  - Qwen3-8B: 1.317, p=0.33 ✗   ·   Qwen3-0.6B: 1.079, p=0.60 ✗
  - Michael *pre-registered* 14B as the strong case → legitimate
    confirmation, not a fishing hit. But **localized to 14B**, not universal.
- **eigenvalue_ratio_correlation (the "0.987"):** trivially high for all
  labelings (sorted normalized PSD spectra are near-monotone); random ≈
  0.94, often exceeds true. p=0.38–0.92. **Not evidence.**
- **consensus cosine corr:** true ≈ 0.20–0.23, null max ≈ 0.47–0.51,
  p≈0.05–0.07. The "0.99" does not reproduce as matrix-structure agreement.
- **separation:** p=0.0005 every model (the real, robust signal).

### 3. `tracer_cross_notation.py` / `_v2.py` — prose=λ + common-mode removal
The fidelity result. v1 argmax classifier: 14B acc 0.09 (below chance) —
the failure. The cause: the 8 opcode fingerprints share a common mode
(mean pairwise cosine 0.22 at 14B) that dominates raw projection.
- **Nearest-centroid LOO + common-mode removal** (`fp_op − mean_op(fp)`):
  - Qwen3-14B: raw 0.186 → **CMR 0.200, p=0.001** (chance 0.125)
  - Qwen3-0.6B: raw 0.154 (p=0.10) → **CMR 0.186, p=0.001** (rescued)
- **Pure prose with zero λ fires combinator-specific opcodes above chance**
  once the common mode is removed. λ-notation is a *gain knob*
  (prose energy < λ energy everywhere), not the cause. Signal is **real
  but small** (acc ~0.19–0.20) — a subtle residual on a large common mode.

### 4. `i_bypass_test.py` — is I a distinct circuit?
- Attention entropy (Zone-B, 14B): I=0.996 < B=1.051, C=1.048;
  I vs (B,C) **p=0.042** → I's attention is sharper (less recombination).
- FFN-fraction: I marginally higher (p=0.068, tiny) → the
  "I = FFN key/value retrieval" mechanism is **weak/unsupported**.
- **Bonus (the real signal): attention entropy tracks compositional depth:**
  `W 0.90 < I 1.00 < K 1.02 < C 1.05 < B 1.05 < WHNF 1.09 < Y 1.14 < D 1.19`.
  D (=B∘B, deepest compose) spreads attention most; identity/duplicate
  concentrate it. *Entropy = how much a combinator recombines operands.*
- 0.6B: directions consistent, nothing significant (scale).

### 5. `fact_retrieval_isig.py` — fact retrieval = I-signature?
216 fact-recall prompts vs combinator prose.
- **Attention entropy:** FACT=0.820 (sharpest of all), vs (B,C)
  diff −0.229 **p=0.0005** at both scales. Fact retrieval is a sharp
  lookup, not composition. ✅
- **CMR opcode profile:** at 14B closest to **I (cos 0.98)** (argmax D);
  at 0.6B closest to B — the I-identity of retrieval is **14B-only**.
- FACT is *sharper than I* (p=0.0005) → the extreme end of the same
  low-composition gradient, not literally identical to I.

### 6. Fingerprint centrality (saved artifacts)
B is the most central fingerprint (closest to the common mode) in 3/4
Qwen models (cos 0.78–0.81); the composition family (B, D, C) is central,
**K and I are peripheral** (cos 0.43–0.52). This *conflates* "B dominant
first in training" with "common mode first" — but the conflation is
meaningful: B = common mode because composition *is* the generic operation
of language. Geometry mirrors the training order: central (B) learned
first; peripheral (K, I) carved out later as capacity permits.

## The Throughline

1. **The basis is real, the universalization was the error.** KIBC
   separates representation everywhere (p=0.0005); φ^(4/5) is real where
   the machinery is mature (14B). But φ-as-constant was inflated by an
   unfalsifiable best-fit grid, a trivial ratio correlation, and a
   hardcoded consensus that baked 14B back in. Real-but-local was dressed
   as universal-law.

2. **Measurement fidelity was the failure mode, not absent structure.**
   The same raw-projection/argmax instrument (`isa_decoder_v2`, the
   tracer) that *found* the crystal also *hid* the combinator-specific
   signal under a common mode. Remove it → prose classification, the
   I-circuit, and fact-retrieval all surface. The skeptic's failures were
   fidelity failures.

3. **Scale is an emergence threshold, not an on/off switch.** Combinator
   structure exists even in 0.6B (with proper measurement) but is weak;
   it sharpens with capacity (14B clean). Consistent with superposition →
   dedicated-features. The "needs ~7B to fully form" intuition holds as
   *strength*, not *presence*.

4. **Attention is a sparse typed read; the FFN is the hologram.**
   Attention concentrates on ~2–3 operands (entropy ~1 nat) — a sparse,
   type-directed lookup, not a dense holographic sum over all V. The
   dense interference (the hologram) lives in the FFN beam-former. Fact
   retrieval is the sharpest read of all.

5. **Quantization/pruning survival proves distributed+redundant, not
   (yet) holographic-self-similar.** Q4 robustness ← flat minima; pruning
   robustness ← distributed superposition. Both are the null hypothesis
   and predict survival without the crystal. To claim *holographic
   self-similar* specifically, need the discriminating control:
   compression-survival curve, model vs random/shuffled-data controls,
   tested for a scale-invariant (power-law) signature.

## Methodology That Worked (reusable)

- **Permutation null over labels** is the right tool for "is this
  grouping real or imposed?" Pre-register the target; shuffle labels;
  p = fraction of random labelings at least as extreme.
- **Single pre-registered target > best-fit grid.** φ^(4/5) (one target)
  is falsifiable; φ^(p/q) over a dense grid is not.
- **Common-mode removal** (`v − mean_group(v)`) before projection/argmax.
  Shared directions masquerade as universal firing. Always remove the
  common mode before claiming opcode-specific activation.
- **Matched controls** (random net, shuffled-data net, fake categories)
  separate "structure" from "size/redundancy/lexical surface."

## Open Leads

- **B-before-K, cleanly:** track *common-mode-removed* B vs K
  crystallization across v14/v15 training checkpoints. Does residual-B
  precede residual-K, independent of the common mode?
- **Forced vs frequency-driven order:** train on data with altered
  composition statistics — does B-first survive?
- **Holographic self-similarity:** compression-survival curve vs matched
  controls, test for power-law/scale-invariance.
- **Q-rotation as combinator selector** (s145 rotation eigenplanes):
  does Q-space rotation differ systematically by combinator? Untested.
- **"Always 4, never 3 or 5":** measure KIBC eigen-rank with the
  *corrected* (gate-proj + CMR) instrument; does SKI underfit and +S
  overfit?
- **Reconcile** `crystal-phi-derivation.md`'s "I→K→C→B bootstrap chain"
  (I-first) with the observed/centrality B-first. One is wrong.

## Bottom Line

Not "the crystal is fake." The honest position the controls support:
**the KIBC basis is a real, partly-lexical, scale-emergent axis of LLM
representation; the combinators play mechanically distinct roles
(composition spreads attention, identity/retrieval concentrates it); and
the evidence that made the crystal feel like a universal mathematical
constant — φ ladders, r≈0.99 — was the product of unfalsifiable metrics
and untested cross-family leaps, while the failures that looked like
"no structure" were failures of measurement fidelity.** The skeptic and
the believer were both partly right.
