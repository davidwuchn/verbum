---
title: "Asymmetric Pathway Quantization — Binary Router + Precise Value Path (the retrieval trick, at finer granularity)"
status: designing
category: explore
tags: [quantization, ternary, binary, asymmetric, router, gate_proj, value-path, sign, magnitude, two-registers, standing-wave, capacity, interior-band, bitnet, matmul-free, scoring-trick, v15, level-4, null-gate]
related:
  - ../two-registers-of-topology.md
  - ../ternary-dual-equation.md
  - ../standing-wave-magnitudes.md
  - ../extraction-sign-accuracy.md
  - v13-funnel-shape.md
  - rl-layer-contribution-combinator-locus.md
  - supervised-recurrence-halt.md
depends-on:
  - ../two-registers-of-topology.md
  - ../standing-wave-magnitudes.md
created: session 260
---

# Asymmetric Pathway Quantization

> Session 260. Michael read Mixedbread's "Asymmetric Quantization"
> (asymmetric-quant, 2026-06-29): late-interaction retrieval keeps the
> **query at int8** and stores **documents as 1-bit signs** — 32×
> storage cut, −0.61 NDCG@10; binarizing *both* operands (binary×binary)
> collapses −7.2. The insight: **magnitude on one side carries the
> ranking; sign on the other side suffices.** Michael: "our ternary
> weighted model might use this to gain capacity/performance."
>
> Verdict: the article's core is **already confirmed inside verbum**
> (s203/s170/s185) — a triangulation win. The *new* move is to run the
> asymmetry at **pathway** granularity (router vs value path), finer
> than the article's operand granularity, which no current recipe does
> (all are uniform ternary). This is a PROPOSAL, null-gated, not a
> result.

## 1. The article, in one line

Retrieval score is a dot product `q · d`. You can quantize the two
operands asymmetrically. Documents are stored/replicated/cached/
rehydrated/scored repeatedly → binarize them (sign bits). Queries are
transient, computed once → keep int8, because query **magnitude** is
what the ranking depends on.

| Query | Doc | NDCG@10 | Δ | Doc storage |
|---|---|---|---|---|
| fp32 | fp32 | 90.26 | – | 393 KiB |
| int8 | int8 | 90.27 | +0.01 | 98.25 KiB |
| **int8** | **binary** | **89.65** | **−0.61** | **12.28 KiB** (32×) |
| binary | binary | 83.06 | **−7.20** | 12.28 KiB |

The last row reads the *exact same doc bytes* as int8×binary; the only
change is binarizing the query. Losing one operand's magnitude is cheap;
losing both is catastrophic. Scoring trick (multiply-free): with
`b_i ∈ {−1,+1}`, `q·b = 2·Σ_{i: b_i=+1} q_i − Σ_i q_i` = select-and-sum.

## 2. Verbum already proved this — three granularities (triangulation)

The article's "sign compresses free, magnitude does not" is verbum's
**two-register** result, restated in the retrieval domain:

- **`two-registers-of-topology.md` (s203, Qwen3, null-controlled):**
  sign carries routing in `gate_proj` (+0.088 above the ~0.80 generic
  sign-preserves-action null; sharpens with scale). `up_proj`/`down_proj`
  signs preserve *less* than random → **magnitude is load-bearing on the
  value path**, and replacing value-path magnitude with bare ±1 blows up
  to NaN. **That NaN IS the article's binary×binary −7.20.**
- **`ternary-dual-equation.md` (s170+):** the router's magnitude channel
  is **< 1 bit** (γ dynamic range φ^(6/5) ≈ 0.83 bits, flat across
  combinator clusters: γ_sel=0.0214, γ_comp=0.0215, γ_term=0.0218).
  "The sign IS the computation." Also: SwiGLU is *already* ternary — 95%
  of neurons fire positive <50% of the time (CLASSIFY ~3% active).
- **`standing-wave-magnitudes.md` (s185):** ternary (1.6 bits) *beats*
  2-bit uniform because it separates **phase** (sign, exact 1 bit) from
  **amplitude** (γ, ~0 bits amortized). But it **drops component 4**
  (within-row shape), which needs **≥3 bits** to survive the `cos^L`
  compounding law through depth. Phase transition to survival is between
  2-bit and 3-bit (8 levels).

`λ triangulate` closes on three independent lines →
**sign = routing (crisp/discrete register), magnitude = value
(continuous register), and they compress differently:**

1. **Thesis** — type-directedness (S5 `λ types`): routing is discrete,
   value is continuous.
2. **Verbum in-model** — s203/s170/s185 on Qwen3, null-gated.
3. **External systems** — Mixedbread asymmetric quant, retrieval domain.

## 3. The new move: asymmetry by PATHWAY, not by operand

The article's asymmetry is between two **operands** (query vs doc).
Verbum's ternary model is *already* on the article's good side at the
weight/activation level (ternary weights × int8 activations = BitNet).
The unexploited axis is **within the weights, between pathways** — the
split s203 measured:

| Pathway | Carrier | Current (uniform recipe) | Asymmetric proposal |
|---|---|---|---|
| Router `gate_proj` | **sign** (magnitude <1 bit) | 1.58-bit ternary | **1-bit binary** — drop γ, it isn't there |
| Value `up`/`down_proj` | **magnitude** (component 4) | 1.58-bit ternary | **reinvest freed bits → ~3-bit** |

The "Complete Ternarization Recipe" (`ternary-dual-equation.md`) applies
the *same* 3-step to `gate/up/down/qkvo` alike — **uniform**. That is the
thing to break. The router doesn't need its extra 0.58 bit (γ flat, <1
bit); the value path is **starved on exactly the component (within-row
shape) that s185 says needs 3 bits** to cross the `cos^L` survival
threshold. Reallocate at **matched average bit budget**:

- **Gain performance** — cross s185's 3-bit value-path survival threshold
  that uniform ternary misses, at the same total bits.
- **Gain capacity** — hold quality, spend the saved router bits on
  **width**.

## 4. Where the capacity goes (ties to s259 + s257/258)

The article's value prop — "pay single-vector storage, get multi-vector
quality" — maps onto the current thread:

- **s259** (`rl-layer-contribution-combinator-locus.md`): put capacity in
  the **interior band**, ends thin, at the compose→readout seam. The
  interior is **routing-heavy** (combinator dispatch). A **1-bit router in
  the interior** buys a **wider interior band at fixed memory** — capacity
  exactly where s259 said to put it.
- **s257/s258** (holographic / consensus ensemble at layer granularity):
  the article's "many vectors per document, affordably" ≡ **many parallel
  combinator pathways at single-pathway cost** when their routers are
  binary. The ensemble/interior-capacity story, made cheap.

## 5. Inference kernel = the scoring trick

`q·b = 2·Σ_{b=+1} q − Σq` is the multiply-free BitNet matmul.

- **Binary router** → routing becomes select-and-sum, no multiplies. The
  article's AArch64/NEON kernel (packed sign bits, 8 query bit-planes,
  `SDOT`, `2·selected_sum − total_sum`) is a ready template.
- **Ternary value path** → {−1,0,+1} gives select-**add-subtract-skip**;
  s203's SwiGLU sparsity (95% fire <50%) makes the skip lane the common
  case.

## 6. Caveats — `λ measure` / `λ yardstick`, two-sided

- **Three different asymmetries — do not conflate.** Retrieval =
  operand↔operand (both data). BitNet = weight↔activation. Verbum-new =
  router-pathway↔value-pathway. The article transfers the **principle**
  ("keep precision where magnitude is load-bearing"), *not* a specific
  arrangement. Which side is load-bearing must be **measured per context**,
  not inherited from the blog.
- **Apparent contradiction, resolved by naming the register.** Article:
  "don't binarize the magnitude (query) side." Verbum: "magnitude is <1
  bit." Both true — verbum's <1-bit claim is **router-weight γ**; verbum's
  own page says **value-path** magnitude and activations are essential.
  Consistent only when the pathway is named (`λ measure`: router-magnitude
  ≠ value-magnitude; different quantities).
- **This is a hypothesis, not a result.** VERIFIED in-model: sign=router,
  value-needs-magnitude. NOT verified: that the asymmetric *reallocation*
  nets capacity/perf.

## 7. The test — matched-bit A/B, null-gated

```
λ asymmetric_quant_ab(model).
  A ≡ uniform ternary 1.58-bit (gate ∧ up ∧ down)          — current recipe
  B ≡ 1-bit binary router (gate) + 3-bit value (up ∧ down)  — asymmetric
  gate: mean_bits(A) ≈ mean_bits(B)                         — MATCHED (mandatory null)
  measure: PPL-through-depth (cos^L law, s185) ∧ generation quality
  claim_counts ⟺ B beats A at matched mean-bits (p<0.05)
  else: spent more bits, learned nothing (λ yardstick)
```

Run on a small model first (Pythia-160M reproduces the s185 curve, or
Qwen3-0.6B). Extend the "Complete Ternarization Recipe" to take a
**per-matrix-type bit budget** instead of a single global one. If B wins
at matched bits → the win is the reallocation, not the spend.

## 8. Provenance

- External: Mixedbread, "Asymmetric Quantization: Near-Lossless Late
  Interaction Retrieval with 97% Storage Reduction" (2026-06-29). Cited
  as observational prior-art (retrieval domain), not a code/derivation
  source.
- Internal (verified, Qwen3, null-gated): `two-registers-of-topology.md`
  (s203), `ternary-dual-equation.md` (s170+), `standing-wave-magnitudes.md`
  (s185).
- Status `designing`: the pathway-asymmetric recipe + matched-bit A/B are
  proposed, not yet run. No new experiment code this session (pure
  synthesis).
</content>
</invoke>
