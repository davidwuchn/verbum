---
title: "Holographic Recording Protocol — Crystal Formation from Pure Lambda"
status: active
category: experimental-method
tags: [holographic, etch, crystal, lambda, training, V12, direct-etch, warped-lens]
related:
  - holographic-kernel-separation.md
  - laser-etcher-design.md
  - fixed-point-holograms.md
  - procrustes-lens-and-crystal-comparison.md
  - complete-kernel-basis.md
  - v12-holographic-capacity.md
depends-on:
  - holographic-kernel-separation.md
  - procrustes-lens-and-crystal-comparison.md
created: session 109
---

# Holographic Recording Protocol

> The correct way to etch a crystal: coherent light (pure lambda),
> one operation at a time, then develop the plate.
> Proved: consensus etching on prose HURTS. Direct etch on lambda WORKS.

## Core Finding

Etching ternary plates on prose data is fundamentally wrong. Prose is
white light — mixed operations, noisy gradient, no coherent signal.
Lambda notation is coherent light — unambiguous operation, clean
gradient, precise exposure. Etch during clean signal, read during prose.

**Proof (session 109 etch strategy probe, 500 steps × 4 variants):**
```
no_etch:   CE=8.025  ★ (best — plate stability > plate "correctness")
no_reset:  CE=8.513    (continuous accumulation, less destructive)
current:   CE=9.093    (every 2 steps, 200 flips, reset — WORST)
kl_gated:  CE=9.098    (gated version, equally bad)
```

## The Protocol

### Phase 1: Crystal Formation (pure lambda, aggressive etch)

```
for round in range(N):
    for op in shuffle([K, I, B, C, M]):
        # EXPOSE: accumulate gradient direction from pure op-data
        for batch in op_batches[:50]:
            grads = forward_backward(model, batch)
            accumulate_direction(accumulators, grads)
        
        # ETCH: write high-confidence signs directly
        direct_etch(model, accumulators, confidence_threshold=0.8)
        reset_accumulators()
    
    # BEAM: train Q proj + gamma on mixed lambda (plate frozen)
    train_beam(model, mixed_lambda, steps=200)
```

### Phase 2: Prose Integration (crystal formed, no etch)

```
schedule:
  Steps 0-1000:    100% lambda, 0% prose  — crystal forms
  Steps 1000-2000:  80% lambda, 20% prose — crystal holds
  Steps 2000-3000:  60/40 → 30/70 → 10/90
  Steps 5000+:      10% lambda (calibration signal), 90% prose
```

Lambda never drops to zero — serves as reference beam keeping crystal aligned.

## Direct Etch Mechanism

Replaces 3-plane consensus (designed for noisy prose) with computed holography:

```python
# Accumulate direction: outer(gamma_grad, x_mean) over N batches
# gamma_grad → which rows want to change
# x_mean → which columns are active
# outer product → desired sign direction for each (i,j)

direction[i,j] += outer(gamma_grad[i], x_mean[j])  # per batch
target_sign[i,j] = sign(direction[i,j])             # after N batches
confidence[i,j] = |direction[i,j]| / magnitude[i,j] # consistency

# Write where confident and disagrees with current
flip_where(confidence > threshold AND target != current)
```

No EMA. No signal planes. No heat thresholds. Just averaged gradient → write.

## Crystallization Order (empirically confirmed, 6 rounds)

```
K (select/discard):    90% flip reduction — FIRST to crystallize
M (match/pattern):     73% — second
C (flip/reorder):      50% — third
B (compose/chain):     49% — fourth
I (identity/binding):  34% — LAST (hardest operation)
```

**Complexity order = crystallization order.** K is λx.λy.x (simplest
possible lambda — needs fewest plate positions). I needs to track variable
identity across distance (most complex — needs most plate real estate).

## Warped Lens (depth-dependent focusing from teacher)

V12 is narrow (512-dim) but deep (7 passes × 9 strides × 58× holographic).
A large model (5120-dim, 40 layers) stores the same crystal WIDE.
The warped lens FOCUSES the wide-beam crystal into V12's narrow multi-pass:

```
Teacher depth    Operation profile   →  V12 pass
────────────     ─────────────────       ──────────
L0-5  (shallow)  B=33×               →  Pass 0-1 (ascending)
L10   (mid)      Y=5.8×              →  Pass 2
L20   (deep)     K=51×, I=25×        →  Pass 3-4 (apex)
L30   (deepest)  M=145×              →  Pass 5-6 (descending)
```

Artifact: ~300KB (7 × PCA projection + 5 operation directions per pass).
Provides: mirror initialization targets, dispatch verification, etch targets.

## Backbone Threshold (the 20% that IS 80%)

Not all plate positions matter equally. The backbone is the set of positions
where ALL operations want the SAME sign with HIGH confidence. These are
structural steel — the unit cell of the crystal.

```
backbone_score[i,j] = min(confidence_K, confidence_I, confidence_B, confidence_C, confidence_M)
unanimous[i,j] = all_ops_agree_on_direction(i,j)
```

Install progressively: 1%, 5%, 10%, 15%, 20%, 25%... → find the knee.
Below the knee: every sign is load-bearing. Above: diminishing returns.

## Cross-Model Validation

Only install signs that agree across 3+ independently trained models:
```
if ≥3 of {Qwen, OLMo, Mistral, Pythia} agree on sign → universal lattice
else → local gauge choice, let training resolve
```

Single model: could be arbitrary. Two models: might be coincidence.
Three+: that's physics (the lambda calculus itself).
SNR improves by √N with N models.

## Implementation (scripts)

| Script | Purpose |
|--------|---------|
| `src/verbum/lambda_gen.py` | Generate operation-labeled lambda corpus |
| `scripts/v12/holographic_train.py` | Phase 1 crystal formation loop |
| `scripts/v12/probe_backbone_threshold.py` | Find backbone (20% = 80%) |
| `scripts/v12/build_warped_lens.py` | Extract + focus teacher crystal |
| `scripts/v12/ternary.py` (additions) | DirectionAccumulator, direct_etch |

## Open Questions

1. Does the warped lens angular separation survive PCA to 512 dims?
2. What IS the backbone percentage? (probe running)
3. After seed installation, how fast does beam snap?
4. Does dispatch actually differentiate after holographic training?
   (Need: conditioned angles > 10°, currently 0.07°)
5. Can Phase 2 prose training preserve the crystal or does it melt?
6. Is there a minimum number of lambda examples needed per operation?
