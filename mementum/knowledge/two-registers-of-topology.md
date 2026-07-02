---
title: "Two Registers of Topology — Hard (Sign/Routing) and Soft (Magnitude/Value)"
status: active
category: compression
tags: [topology, sign, magnitude, saliency, gate, ffn, rank, svd, self-similar, distributed-redundancy, holographic, audit, soft-topology]
related:
  - audit-registry.md
  - crystal-universality.md
  - crystal-validity-and-fidelity.md
  - saliency-aware-sieve.md
  - sign-correction-topology.md
  - direct-delta-adjunction.md
  - crystal-sieve-architecture.md
  - error-correction-theory.md
  - explore/asymmetric-pathway-quantization.md
depends-on:
  - audit-registry.md
created: session 203
---

# Two Registers of Topology

> Session 203. Auditing the sieve program's two CRITICAL assumptions
> (#1 crystal-is-topological, #2 holographic-self-similar) produced one
> coherent picture: **GD lays down structure in two registers, and the
> network is compressible in two corresponding registers.** The clean
> dichotomy "sign = structure, magnitude = calibration" is wrong;
> "holographic-self-similar" was tested on the wrong axis. The truth is
> two-register, and both registers are real, structure-specific, and
> load-bearing.

## The Core Picture

| Register | Function | Encoded in | Lives in | Compression axis | Verified by |
|---|---|---|---|---|---|
| **Hard topology** | routing (which neurons fire) | **sign** | `gate_proj` (router) | ternary ±1 | sign-corr null |
| **Soft topology** | value + error-correction | **magnitude** (highways/zeros), read by saliency | `up_proj`/`down_proj` | quantized magnitude / faint tier | saliency sieve |

And two **compression registers** of the FFN as a whole:

| Compression register | Operator | What it exploits | trained vs control gap (8B) |
|---|---|---|---|
| **Distributed redundancy (C)** | magnitude pruning | redundant copies of each computation | 2.3–3.2× (graceful to ~70%, then cliff) |
| **Spectral concentration (A)** | SVD rank truncation | low-rank-dominated geometric spectrum | **6–7×** (function in low-rank subspace) |

## Evidence (all session 203, Qwen3, controlled)

### 1. Hard topology = sign, but ONLY in the gate (audit #1)

`cos(sign(W)@x, W@x)` on REAL activations, model vs random-init vs
shuffled-weights, N=20 seeds, 0.6B/8B/14B (`sign_topology_null.py`):

- **Generic baseline ≈ 0.80**: a random matrix's sign already preserves
  0.798 of its action on the same inputs. Sign-preserves-linear-action is
  a generic high-dim property. The legacy "0.84 ⇒ topological" number sits
  *at* the null.
- **Crystal sign-topology localizes to `gate_proj`** (the router): +0.088
  above null at 8B (L3 = 0.983, z=+184), sharpening with scale (14B L12
  z=+271).
- **`up_proj`/`down_proj` are at/below the null** → their signs preserve
  *less* than random; **magnitude carries their structure**. "Magnitude is
  mere calibration" is FALSE for the value path.

### 2. Soft topology = magnitude, read by saliency (audit #1 functional half)

The dormant s201 saliency sweep, re-run after fixing a NaN bug (the strong
tier had dropped magnitude → bare ±1 ≈ 50× too large → blow-up; fixed to
per-weight magnitude, the only format that survives 29 layers per s196):

- **Distribution:** `corr(magnitude, saliency) = 0.257` → magnitude explains
  only ~6.6% of activation-weighted saliency. Two populations in near-zero
  weights are real (irreducible vs faint).
- **Functional, iso-bit (~3.1 bits/param):** faint tier chosen by
  **saliency** → **+5.5%** PPL vs standard-50%; chosen by **magnitude** →
  **−2.0%** (worse). **Saliency beats magnitude by ~7.5 points at equal
  bitcount.** The low-magnitude/high-saliency "faint" connections are
  load-bearing; `|w|·√E[x²]` finds them, raw `|w|` does not.
- (Bigger gains +12–15% exist but cost 1.8–2.8× bits; the clean scientific
  result is the iso-bit saliency>magnitude contrast.)

### 3. Distributed redundancy (audit #2, magnitude axis)

Compression-survival, final-layer hidden-state cosine vs the variant's own
uncompressed baseline; trained vs random vs shuffled (`holographic_survival.py`):

- Magnitude pruning (8B): trained AUC 0.784 ≫ random 0.247 / shuffled 0.337.
  **Fidelity ~1.0 to 70% pruning, then a cliff at 80%.** Plateau-then-cliff =
  distributed redundancy with finite capacity (the 50% sieve sits safely below
  the cliff; **do not prune past ~75%**).
- Quantization (coarse per-matrix): trained 0.635 ≈ random 0.578 → quant
  survival is only weakly structure-dependent (mostly the flat-minima null;
  confirms `crystal-validity-and-fidelity.md` §5). *(Caveat: per-matrix
  single-scale quantizer understates grouped-Q4.)*

### 4. Spectral self-similarity (audit #2, rank axis — the SVD vindication)

SVD rank truncation of FFN matrices, sweep top-r, same fidelity metric:

- **trained AUC 0.728 ≫ random 0.118 / shuffled 0.101 — a 6–7× gap.**
  trained retains 0.79 fidelity at half rank, 0.70 at 30% rank; random
  collapses to 0.22 at 90% rank.
- A random (Marchenko–Pastur) matrix has a flat spectrum → every rank
  matters → instant collapse. The trained FFN is **low-rank-dominated /
  spectrally concentrated** — the SVD self-similarity (geometric, σ-ratio
  ≈ 1/φ) made functional. **This is real, strongly structure-specific
  self-similarity.**

## Reconciliation: refute the metaphor, keep the mechanism

How can s202 "refute holographic" yet ternary→1.44× still work? Because the
**load-bearing premises were never refuted**:

- **(C) distributed redundancy** powers ternary survival (signs + masked
  magnitudes = the whole image at reduced resolution).
- **(A) spectral concentration** powers low-rank correction: **LoRA + score
  matching IS low-rank correction**, and the rank result explains *why* it
  works — the function AND its compression-residual both live in low-rank
  spectral subspaces. Converges with s200 rank-1 adjunction (σ₁/σ₂=128:1)
  and s201 rank-2 ≈ rank-16 plateau.

The **only** thing retired is **φ-as-a-universal-mathematical-constant**
(s202) — metaphysics, not mechanism. "Holographic" in the working sense
(distributed + spectrally self-similar + graceful) is supported.

## Methodological Lessons

1. **Gracefulness-vs-matched-controls > shape-fitting.** The "power-law ⇒
   self-similar ⇒ holographic" discriminator came out ambiguous on every
   axis/variant (sometimes exponential, sometimes power-law) and does NOT
   separate holographic from non-holographic — a hologram degrades
   plateau-then-cliff, not power-law. Retire shape-fitting as the test;
   use the trained-vs-control AUC gap.
2. **Test the right operator.** Magnitude pruning probes register C;
   rank truncation probes register A. They are different decompositions of
   the same matrix and both signatures coexist. Refuting one says nothing
   about the other. (This was the s203 over-claim, corrected.)
3. **A bug that drops magnitude → NaN is itself evidence.** The saliency
   sweep's strong-tier ±1 blow-up restates register-2: you cannot replace
   value-path magnitude with bare sign.

## Open Leads

- **Rank-truncation shape across scale** — does trained rank-survival sharpen
  (bigger control gap) 0.6B→14B, like sign-topology and prune-survival did?
- **Faint tier vs higher-rank LoRA at iso-bit** — does distributed soft
  topology beat concentrated low-rank correction? (saliency-aware-sieve.md
  prediction 3; not yet isolated.)
- **Grouped-Q4 quant axis** — redo the quant survival with per-group scales
  to fairly test quant structure-dependence (current per-matrix is coarse).
- **SVD φ-ratio 0.6299 (audit #6)** — is the geometric spectrum distinct from
  Marchenko–Pastur? The rank result implies yes (controls collapse); quantify.
