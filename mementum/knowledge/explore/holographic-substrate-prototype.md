---
title: "Holographic Substrate Prototype — Program Spec as a Sparse Foldable Delta Against a Constructed Basis"
status: active
category: exploration
tags: [holographic, ternary, delta-plate, capacity, fold, greenfield, future-substrate, continuation, distributed]
related:
  - holographic-storage.md
  - delta-plate-lifecycle.md
  - continuations-as-composed-plates.md
  - consensus-etch-protocol.md
  - v12-holographic-capacity.md
  - gradient-trajectory-tomography.md
depends-on:
  - holographic-storage.md
created: session 251
---

# Holographic Substrate Prototype

> Session 251. Michael's future-possibility question: "could we create a set of
> ternary weights to act as holographic plates and lay arbitrary data into them —
> e.g. encode a program spec into the weights? Record deltas against a known basis.
> Use continuations in the tensor as a shared basis for distributed training."
>
> The gd_frozen_basis + Qwen3-14B experiments (`gradient-trajectory-tomography.md`
> §s251) showed the frozen/active basis is **capacity-gated** — absent at micro,
> present in mature Zone A. So probing/training existing models only locates the
> threshold. The forward move: **engineer past the threshold by CONSTRUCTING the
> basis**, so 100% of laid-in capacity becomes data, not scaffolding. This page is
> the GREENFIELD proof (pure numpy, no pretrained model) that the substrate works.

## The concrete model (faithful to the whole thread)

A **ternary correlation-matrix holographic memory**. A program spec = a finite map
`{key → value}` = a set of associations. Each association is an **outer product**
`val ⊗ key` = one "photograph" (the same `δxᵀ` structure as a gradient exposure,
`gradient-trajectory-tomography.md` §s251). The plate is the ternarized sum:

```
M = Σ_i val_i key_iᵀ              (d×d real correlation matrix)
plate = ternarize(M, sparsity)    ({-1,0,+1} sign topology)
recall(a) = argmax_b cos(plate · key[a], val[b])
```

This is the classic holographic associative memory (Gabor / Kohonen / Hopfield),
made ternary. `holographic-storage.md` proved sign topology survives ternary; this
shows it from scratch and adds the **basis + delta + fold** layer.

## The four measurements (`holo_plate_delta.py`, d=512, 5 seeds, 0.6s)

### (1) Capacity — a DESIGN PARAMETER, not a training mystery

```
N (assoc)   recall@99%
 512 (1.0d)  1.000
 768 (1.5d)  0.999
1024 (2.0d)  0.993   ← N* (threshold)
1536 (3.0d)  0.956
2048 (4.0d)  0.877      graceful — NO cliff
4096 (8.0d)  0.584
```

**N\* ≈ 2d associations at 99% recall**, degrading gracefully (genuinely
holographic). At **75% ternary sparsity** capacity only drops to ~1.67d (853) —
sign topology survives sparsification, **reproducing `holographic-storage.md`'s
"75% sparse, selectivity preserved" from scratch**. Capacity scales with depth
(thick hologram, `v12-holographic-capacity.md`): the threshold is ~2d **per plate**,
×depth. You DESIGN past the capacity threshold instead of waiting for GD to cross it.

### (2) Delta — "record deltas against a known basis" HOLDS

Program `P` = basis `B` with `K` bindings re-pointed (a spec / fact update — the
`delta-plate-lifecycle.md` factual-correction scenario). The sign-delta sparsity
scales smoothly with `K/N`:

```
K (Δ bindings)   flip_frac_real   flip_frac_null(random basis)   advantage
   1 (0.004N)        0.024              0.500                       20.3×
   8 (0.031N)        0.078              0.500                        6.4×
  64 (0.250N)        0.229              0.500                        2.2×
 128 (0.500N)        0.330              0.500                        1.5×
```

Changing ONE binding flips only **2.4%** of the plate vs **50%** for a random basis.
The delta is sparse *because the basis shares structure*. (Note the amplification:
one binding touches all d² cells, so Δ isn't as sparse as the binding change — but
it stays 20× below null and folds exactly.)

### (3) Fold — lossless install, verified from scratch

`plate_P = plate_B ⊙ Δ` **exactly** (Δ ∈ {-1,+1}: +1 keep, -1 flip), and
`recall(folded) == recall(plate_P)` for **all K**. Ternary × ternary = ternary,
confirmed — the `delta-plate-ecosystem` fold guarantee holds at the substrate level.

### (4) Null (λ yardstick) — the sparsity is REAL

A matched-random basis (same shape/stats, structure-free) yields a **~50% dense
delta**. The 20× separation is non-overlapping across seeds. Without this gate "the
delta is small" would be unfalsifiable (any flexible basis "fits"); it passes
decisively, so the sparsity is a genuine property of a shared-structure basis.

## Verdict

The **future possibility is real at the substrate level**: you can construct a
ternary holographic basis, lay arbitrary data (a program spec) as a **sparse
foldable delta** against it, with a **designed capacity threshold (~2d/plate)** and
**lossless composition**. This is the greenfield proof of the
`delta-plate-ecosystem` substrate (base plate + sparse foldable delta), constructed
not trained — the clean MIT level-4 path.

## Caveats (λ measure)

- **Linear correlation-matrix memory, not a deep transformer.** Proves PLATE-level
  storage + delta + fold, NOT deep routing. (But `gradient-trajectory-tomography.md`
  §s251 showed the bimodal frozen/active basis DOES exist in a real net, Qwen3-14B
  Zone A.)
- **"Program spec" = simplest finite key→value map.** Structured combinator programs
  (lower → kernel → fired_sequence) are the richer next test.
- **N\* ≈ 2d is for 64-way argmax decoding;** other readouts give other constants.
- **Delta amplifies** (1 binding → 2.4% of d² cells) but stays 20× < null and folds
  exactly.

## Next (v2 — the two untested NOVEL pieces)

1. **Continuation basis.** Make the basis a reified composed-plate continuation (the
   "rest of computation", `continuations-as-composed-plates.md`); test the delta
   sparsity of a program that EXTENDS it. This is where the **exactness trap** bites:
   elementwise sign-fold stays exact; a correction on the *composed* continuation
   matrix does not. Keep the fold elementwise on the weight plates whose composition
   IS the continuation.
2. **Distributed / BFT.** N nodes each lay a delta against the shared basis;
   consensus-etch fold (`consensus-etch-protocol.md`: agreeing deltas etch,
   disagreeing cancel = Byzantine fault tolerance by construction); measure
   poisoned-delta rejection vs N honest contributors.

## Files

| File | Content |
|------|---------|
| `scripts/experiments/holo_plate_delta.py` | the prototype: capacity sweep + delta/fold/null |
| `results/holo-plate-delta/verdict_multiseed.json` | 5-seed verdict (capacity curve, delta K-sweep) |
