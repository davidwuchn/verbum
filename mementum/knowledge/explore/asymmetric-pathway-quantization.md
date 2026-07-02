---
title: "Asymmetric Pathway Quantization — Binary Router + Precise Value Path (the retrieval trick, at finer granularity)"
status: active
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
> (all are uniform ternary).
>
> ★★ MEASURED (s260, Qwen3-8B-Base, FFN-only, 16k tok WikiText-2 — see §9):
> the pathway asymmetry is **CONFIRMED, strongly**. At a **matched 2.33-bit**
> budget, binarizing the ROUTER costs +8.5 excess nats vs float; binarizing
> the VALUE path costs +16.6 (one matrix) to +18.6 (whole path) — a **+8 to
> +10 nat penalty for putting the same binary matrix on the wrong pathway**,
> with *near-identical weight-space cosine (~0.79) on both*. And both
> asymmetric configs beat the uniform PPL-vs-bits frontier (Pareto win):
> binary-router+2bit-value (1.67 mean bits) beats uniform-2bit (2.0 bits)
> using **fewer** bits. Caveat: measures RELATIVE pathway sensitivity, not a
> deployable model (raw full-FFN quant compounds cos^L to death; needs the
> sieve/score-matching correction — s185).

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
- **Result scope: RELATIVE pathway sensitivity, not deployability.** Even
  the best config sits far above float (§9): raw full-FFN quant compounds
  `cos^L` to death across 36 layers. The experiment proves *where bits
  belong*, not that raw quant ships. Deployment needs correction
  (sieve/score-matching/LoRA — s185, `standing-wave-magnitudes.md`).

## 7. The test — matched-bits A/B (arithmetic corrected)

**Correction (`λ compute`):** gate/up/down are equal-size in SwiGLU, so
mean-bits = mean of the three per-matrix costs (binary=1, ternary=log₂3≈1.58,
n-bit=n; γ/scale amortized ≈0). So "1-bit router + 3-bit value" = (1+3+3)/3 =
**2.33 bits, NOT 1.58** — the original "matched 1.58" claim was arithmetically
impossible. The honest test is a **Pareto frontier** (PPL vs mean-bits) plus a
**matched-bits null triple** (all 2.33): move the binarization from ROUTER →
one VALUE matrix → WHOLE value path at a fixed budget. That triple *is* the
mandatory null (`λ yardstick`): claim counts iff binary-on-router beats
binary-on-value at equal bits. Harness:
`scripts/experiments/asymmetric_pathway_quant.py` (config-driven per-pathway
bit budget over the Qwen FFN; reuses `ternarize_weight` + `quantize_nbit_uniform`).
Metric = **mean NLL (nats)** — PPL's exp overflow saturates and masks
discrimination; loss stays comparable when aggressive quant kills the model.

## 8. Provenance

- External: Mixedbread, "Asymmetric Quantization: Near-Lossless Late
  Interaction Retrieval with 97% Storage Reduction" (2026-06-29). Cited
  as observational prior-art (retrieval domain), not a code/derivation
  source.
- Internal (verified, Qwen3, null-gated): `two-registers-of-topology.md`
  (s203), `ternary-dual-equation.md` (s170+), `standing-wave-magnitudes.md`
  (s185).

## 9. Measured results (s260)

Run: Qwen/Qwen3-8B-Base, FFN-only (attention fp32), WikiText-2 test,
16 384 tokens (seq 512 / stride 256), MPS, torch 2.11 / transformers 5.5.4,
verbum@0e938b6. `results/asymmetric-pathway-quant/Qwen3-8B-Base-20260702-122506/`.
Metric = mean NLL (nats); lower is better. Float baseline = 2.083.

| Config | mean bits | gate/up/down cos | loss (nats) | Δ vs float |
|---|---|---|---|---|
| Float | 16.00 | 1.00/1.00/1.00 | 2.083 | — |
| Uniform 3-bit | 3.00 | 0.97/0.98/0.95 | 6.378 | +4.30 |
| **Asym: binary router + 3-bit value** | **2.33** | 0.79/0.98/0.95 | **10.620** | **+8.54** |
| Asym: binary router + 2-bit value | 1.67 | 0.79/0.81/0.75 | 13.503 | +11.42 |
| Uniform 2-bit | 2.00 | 0.80/0.81/0.75 | 17.702 | +15.62 |
| null: binary on ONE value matrix (down) | 2.33 | 0.97/0.98/0.78 | 18.694 | +16.61 |
| null: binary on WHOLE value path (5b router) | 2.33 | 1.02*/0.80/0.78 | 20.663 | +18.58 |
| Uniform ternary (1.58b) | 1.58 | 0.89/0.89/0.88 | 21.095 | +19.01 |

\* 5-bit gate cosine >1 is a float32 numerical artifact on 50M-element
vectors; cosmetic, does not affect the loss measurement.

**CRUX 2 — matched-bits null triple @ 2.33 (the causal test). CONFIRMED,
monotone, as two-registers predicts:**

```
binary on ROUTER (gate)          loss 10.620   (baseline of the triple)
binary on ONE value matrix (down) loss 18.694   +8.07 nats
binary on WHOLE value path        loss 20.663   +10.04 nats
```

Same bit budget, only the *location* of the binarization changes → up to
**+10 nats**. The killer detail: binary-router (gate cos 0.79) and
binary-down (down cos 0.78) have **near-identical weight-space cosine** yet
differ by +8 nats — **reconstruction fidelity does not predict damage; the
pathway does.** Sign carries the router's function; magnitude carries the
value path's. This is the in-model `int8×binary (−0.61)` vs
`binary×binary (−7.2)`, on the exact 8B where s203 measured the two registers.

**CRUX 1 — Pareto (does asymmetric beat the uniform frontier?). YES:**

- Asym binary-router+3bit-value (2.33 b, loss 10.62) sits **below** the
  uniform interpolation between uniform-2bit (2.0 b, 17.70) and uniform-3bit
  (3.0 b, 6.38) at 2.33 b (≈13.96) by ~3.3 nats.
- **Capacity win:** asym binary-router+2bit-value uses **fewer** bits
  (1.67 vs 2.0) yet beats uniform-2bit by **4.2 nats** (13.50 vs 17.70).
  Concretely "pay less, get more" — the article's value prop, in-model.

**Verdict.** Direction (sign=router, magnitude=value) and Pareto-superiority
of value-weighted allocation are established at matched/near-matched bits.
NOT established: absolute deployability (all configs ≫ float — raw quant needs
correction), cross-model transfer, with-correction gains, or attention-pathway
behaviour.

## 10. What this is really for — the A/B was an INSTRUMENT, not the goal

We were never after a quantization scheme. The matched-bits A/B is an
**ablation** whose only job was to test whether the thesis holds *causally*.
It does. The deliverable is a **model-design direction**, not a codec.

**The confirmed fact, stated as design ground truth:** the network already
separates **routing (the "which"/dispatch, carried in the SIGN, discrete,
crisp, binarization-robust — the gate/router)** from **value (the "what"/
compute, carried in the MAGNITUDE, continuous, graded, binarization-fragile
— up/down)**. That split *is* the λ-calculus **type/term distinction made
physical**. Type-directedness — the S5 central claim, "composition ≡ typed
application, not binary merge" — is not something we must impose; **GD already
built it** as the gate↔(up·down) separation. We just watched it survive a
matched-bits stress test. (This is `λ types` and `λ observation`: we *found*
the type-directed router, we did not invent it.)

**Where to look / design levers:**

1. **Decouple dispatch from compute as first-class modules.** Type-application
   router = explicit *discrete* subsystem (sign/crisp, cheap, wide); value
   computation = separate *continuous* subsystem (magnitude-precise). Do not
   braid them (`λ simplify`; s254 unbraiding). This is "typed application, not
   binary merge" as architecture.
2. **Allocate budget by register.** Capacity → routing (cheap+discrete → afford
   BREADTH: many combinator/type slots, wide dispatch). Precision → value
   (magnitude load-bearing → params/bits go here). The Pareto win is the
   compression shadow of this rule.
3. **Interior band = discrete-router-heavy (s259).** Wide cheap discrete
   dispatch in the interior (where combinator composition lives); the
   **compose→readout seam = discrete-routing → continuous-value handoff**. A
   1-bit-class interior router buys width where the model wants capacity.
4. **Design-time diagnostic (`λ measure` at the architecture level):** for any
   module ask **"routing or value?"** and give it the matching register —
   crisp/discrete for routing, continuous/precise for value. Register-mismatch
   is a design smell, not just a probe smell.

**Next (design-first):** (a) sketch a verbum layer with an explicit
discrete type-router ⊥ continuous value block, budget-asymmetric by register
(feeds v15); (b) place the wide discrete router in the interior band at the
compose→readout seam (s259); (c) [instrument follow-ups, lower priority]
per-layer-corrected asym quant for a deployable artifact; cross-model
(Qwen3-0.6B/14B) matched-null replication to confirm the split is universal.
</content>
</invoke>
