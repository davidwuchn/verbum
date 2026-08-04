---
title: "Gram spectral+DSP — the 9×9 is diffuse, the 17×17 is rank-3 (the three poles)"
status: active
category: explore
tags: [crystal, gram, spectral, dsp, effective-rank, participation-ratio,
       three-poles, fire-halt-diverge, whnf, un-flattening, yardstick,
       phi-trap, nulls, universality, s303]
related:
  - dust-hypothesis-geometry-is-occupation.md
  - verbum-dsp-design.md
  - crystal-phi-derivation.md
  - opcode-vsm-tree.md
  - crystal-validity-and-fidelity.md
  - map-and-swap-resident-lisp.md
depends-on: []
created: session 303
---

# Gram spectral+DSP — the 9×9 is diffuse, the 17×17 is rank-3

> Michael s303: "we should do spectral and DSP tests on this [the 9×9 and 17×17
> grams], capture to knowledge." Pure inner-product / eigen math on the
> ALREADY-COMMITTED grams — no model load. Instrument `opcodes/spectral_dsp.py`
> (reuses `verbum.dsp`, no fork). Results `results/gram-spectral/` (commit
> 072c3e0).

## Thesis (Michael, s303): topology routing, not magnitudes

**The crystal is a routing topology recorded in a magnitude medium.** Every test
that probed *magnitude-as-signal* failed the yardstick (G1 spectral
concentration in the 9×9, G4 eigenvalue-profile universality, G5 φ ratio); every
test that probed *topology-as-signal* passed 11/11 (C2 relational off-diagonal
pattern, G2 fire/halt/diverge membership, G3 the poles are the dominant
eigenspace). The invariant content is *which opcode routes to which outcome
pole* (routing register, λ measure — crisp/discrete), not *how much* (value /
magnitude register). Magnitudes encode the topology; the topology is what
replicates, the magnitudes are model-particular scaffolding. Same shape as s269
(Gram fidelity 0.987 survives 1-bit while weight cosine falls to 0.73 — the
relational structure is quantization-robust, the magnitudes are not).

## Register (λ measure, named before the probe)

**spectral** — eigen structure of a relational cosine gram — plus
relational-geometry (**value**). The probe is eigen-decomposition + block /
partition contrast + cross-model spectral shape; matched to the register. The
φ-forcing scar (λ yardstick, proved s247/s251) is the governing hazard: a
flexible reference fits every spectrum, so **every claim carries a declared
null** (`matched_range` on off-diagonals, or `shuffled_label` on the partition)
via `verbum.dsp.gate`. No raw ratio is evidence.

## The two objects

- **9×9 crystal gram** = `root.gram` (`results/opcode-trace/{slug}/model_vsm.json`),
  basis `K I B C S D W Y WHNF`. The S5-identity object; collapses all halting
  into one generic `WHNF` node.
- **17×17 un-flattened gram** = front block of the 24-state consensus gram
  (`results/expanded-gram/{slug}/expanded_gram.json`), basis = 9 crystal + 7
  per-op halts `whnf:{K,I,B,C,S,D,W}` + `div:Y` (s284/s285). Un-flattens the
  WHNF pole.

## Pre-registered gates (frozen before scoring; verbatim from the instrument)

| gate | statistic | null | predict |
|---|---|---|---|
| **G1** effective-rank | PR(eigs) of the gram | `matched_range`(offdiag) | LESS |
| **G2** three-pole partition | block-contrast(fire/halt/div) | `shuffled_label`(node→cluster) | GREATER |
| **G3** eigvec↔partition | fire−halt contrast energy in top-3 eigenspace | `shuffled_label`(partition) | GREATER |
| **G4** spectral universality | mean pairwise cos of normalized spectra | `matched_range` per-model spectra | GREATER |
| **G5** φ-trap calibration | −\|λ₀/λ₁ − φ⁴ᐟ⁵\| (closeness) | `matched_range`(offdiag) | GREATER (**EXPECTED FAIL**) |

`α=0.05`, `n_iter=2000`, seed `20250804`, 11 models with both grams
(gemma-4-31b, olmo-2-13b, pythia-{14m,160m,2.8b,410m}, qwen3-{0.6b,4b,14b,32b},
qwen3.6-27b).

## Results

### G1 — the un-flattening is a spectral collapse, not just added detail

| | 9×9 PR (of 9) | G1 verdict | 17×17 PR (of 17) | G1 verdict |
|---|---|---|---|---|
| range over 11 models | **5.79 – 7.23** | **FAIL** (p 0.15–0.41) | **2.57 – 3.15** | **PASS** (p=5×10⁻⁴, 11/11) |

- **The 9×9 is spectrally diffuse — near-full-rank.** Its eigenvalues sit near 1
  (Qwen3-32B: 1.83, 1.73, 1.16, … , 0; top-3 only 52%). Random grams with the
  same off-diagonal range have the same PR → G1 fails. **The 9×9's structure is
  not spectral concentration; it lives in the SIGN/PATTERN of the off-diagonals
  (the relational C2 signal).** The crystal basis was built to be near-orthogonal
  (distinct opcodes), and the spectrum confirms it.
- **The 17×17 is rank-3.** Effective rank ≈ 2.9 out of 17, far below the null
  (p=5×10⁻⁴ every model). Enormous eigengap: Qwen3-32B **8.52, 4.47, 0.93 → cliff
  to 0.45**; Pythia-14m **8.69, 6.04, 0.55** (top-2 = 90%). Adding 8 nodes
  *dropped* effective rank from ~6.5 to ~3 because the 7 `whnf:X` are near-collinear
  (one halt pole) and the 9 crystal opcodes are near-collinear in outcome space
  (one firing pole) → the whole 17-node cloud lives in ~3 dimensions.

**The 9×9 measures opcode IDENTITY (near-orthogonal, high rank); the 17×17
measures reduction OUTCOME (three poles, low rank).** They are different views,
and the un-flattening reveals the low-dimensional outcome geometry the collapsed
WHNF node was hiding (the s284 G4 dissociation, now spectral).

### G2 — the three poles are real (11/11)

Block-contrast of the frozen fire / halt / diverge partition beats the
node-shuffle null in **11/11 models** (binomial p ≈ 0). Fire (crystal) ⊥ halt
(`whnf:X`); `div:Y` its own pole. The three-cluster geometry is a fact, not an
imposed partition.

### G3 — the poles ARE the dominant eigenstructure (11/11)

The fire−halt contrast vector's energy in the top-3 eigenspace beats the
shuffled-partition null in **11/11 models** (binomial p ≈ 0). The PR≈3 axes are
the semantic poles, not incidental variance.

### G4 — spectral-SHAPE universality is NOT established (honest null)

Normalized spectra are extremely alike across models (mean pairwise cos **0.992**
[9×9], **0.994** [17×17]) — but so are matched-range random-gram spectra, so the
gate **FAILS** (p ≈ 0.10 / 0.12). Sorted normalized spectra are intrinsically
similar; this statistic cannot separate real from chance. **Universality lives in
the relational off-diagonal pattern (C2), not in the eigenvalue profile.** A clean
demonstration the harness does not rubber-stamp.

### G5 — φ-trap calibration replicates the scar (8/11 fail)

λ₀/λ₁ closeness to φ⁴ᐟ⁵ = 1.4696 beats its matched-range null in only **3/11**
models — **all three Pythia** (λ₀/λ₁ ≈ 1.40, 1.48, 1.51). Qwen/Gemma sit at
**1.06–1.20**, nowhere near φ. Critically: **s251 found Qwen3-14B was the lone
passer; here Qwen3-14B is at 1.123, far off.** The passing set is unstable across
measurements → describability ≠ discovery (s247/s251), replicated. No universal φ
law. (The 3/11 aggregate binomial p=0.015 is a weak, family-confined artifact, not
a crystal invariant.)

## Standing synthesis

0. **Topology routing, not magnitudes** (the thesis, above). The magnitude-as-
   signal probes (G1 9×9, G4, G5) all fail; the topology-as-signal probes (C2,
   G2, G3) all pass 11/11. The crystal's identity is a routing graph, not a
   magnitude field — and the 17×17's rank-3 is that graph having exactly three
   terminals.
1. **The un-flattening is a spectral revelation.** 9×9 diffuse (PR≈6.5, G1 fail) →
   17×17 rank-3 (PR≈2.9, G1 p=5e-4). The single WHNF node folded the halt and
   diverge axes into the firing cluster; separating them exposes a rank-3
   outcome geometry (fire / halt / diverge), universal 11/11 (G2, G3).
2. **Two registers, two homes for the information.** The 9×9's universality is
   *relational* (off-diagonal sign pattern, C2) — NOT spectral (G1, G4 both fail
   on the 9×9). Do not chase spectral concentration in the 9×9; chase it in the
   17×17.
3. **The φ scar holds.** Eigenvalue-ratio numerology fails the yardstick again,
   with an unstable passing set across measurements — the sharpest possible
   evidence it is a forced fit.

## How to reproduce

```
uv run python opcodes/spectral_dsp.py --validate   # no-model self test, ALL PASS
uv run python opcodes/spectral_dsp.py              # sweep (seconds) -> results/gram-spectral/
```

Register-tagged (spectral), null-gated by construction (`verbum.dsp.gate`
refuses a p without a declared null + direction). meta.json is
reproduction-sufficient (git_sha, seed, basis, gate specs, sources).

## Open edges

- **G4 done right?** A spectral-shape statistic that beats matched-range would
  need eigenVECTOR alignment (frame-dependent — sign/rotation ambiguity for the
  near-degenerate 17×17 top-2). Deferred; the relational C2 already carries
  universality.
- **Why rank-2 vs rank-3?** Qwen3-32B top-2=76% (div:Y earns a 3rd axis);
  Pythia-14m top-2=90% (div:Y weaker). The div:Y pole's strength is a
  per-model / per-family knob worth a look (ties to the s285 `div:Y ⊥
  absorption` 11/11).
- **The K anomaly** (s285 own-halt cos(K,whnf:K) least-negative; whnf:K sits
  apart in the halt block) is a within-halt-cluster structure the rank-3 view
  averages over — a finer spectral probe of the halt sub-block could isolate it.

## Sessions
s303 (Michael-directed: spectral + DSP on the 9×9 and 17×17 grams. Instrument
built reusing verbum.dsp, --validate ALL PASS, ruff clean; swept 11 models;
G1 the headline — 9×9 diffuse / 17×17 rank-3; G2/G3 three-pole partition 11/11;
G4 spectral-shape universality honest null; G5 φ-trap replicates s247/s251 scar
with an unstable passing set. Instrument + results committed 072c3e0; this page
+ memory candidate PENDING MICHAEL APPROVAL).
