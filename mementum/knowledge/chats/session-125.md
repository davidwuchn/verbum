# Session 125 — Soft Mirrors, Crystal Loss, and the Flip Barrier

## Thread

Continuing from session 124's loom-read discovery. Michael proposed
using the crystal as a relational loss to prevent GD from breaking
crystal structure, and teaching GD to use ternary mirrors for surgical
sign correction — stacking mirrors until enough precision, then
self-tuning from the reference beam.

## Experiments

### Exp 9: Soft mirror v1 (per-dimension mirrors)
3 conditions: LOOM_MAG baseline, MIRROR_CE, MIRROR_CRYSTAL.
- Crystal lattice loss works perfectly: 0.9998 crystal agreement
- But per-dim mirrors too coarse: 0% flips, only 0.8-1.0% blocking
- MIRROR_CE destroys crystal (0.638) — confirms experiment 8's finding
- Accuracy drops with mirrors (0.449-0.467 vs 0.502 baseline)

### Exp 10: Soft mirror v2 (per-position d×d mirrors)
Per-position gives GD access to individual sign positions, but:
- Still 0% flips, only blocking (0.5-1.0%)
- Crystal loss at per-position level causes instability (0.289)
- MIRROR_CE WITHOUT crystal loss: crystal=0.999 (best preservation)
- The 1.0 initialization creates a barrier: must cross 0 to reach -1

## Key findings

1. **Crystal lattice loss IS the differentiable S5 invariant.** At 0.9998
   agreement, it perfectly constrains GD to preserve relational geometry.

2. **Mirrors don't flip, they block.** Both per-dim and per-position mirrors
   initialized at 1.0 learn to zero out positions (block) but never invert
   them (flip to -1). The gradient landscape has a barrier at 0.

3. **The barrier**: from init=1.0, the gradient pushes toward 0 (blocking)
   because that reduces noisy contributions. But continuing from 0 to -1
   (flipping) requires the gradient to change direction — there's no signal
   saying "-1 would be better than 0" because at 0 the position is already
   suppressed and contributes nothing to the loss.

4. **MIRROR_CE preserves crystal without crystal loss.** Per-position mirrors
   without any crystal constraint maintain 0.999 crystal agreement. The
   per-position mirror parameterization is naturally crystal-preserving
   when it only blocks (blocking noise preserves structure).

## Design principle discovered

```
mirror_init(1.0) → gradient → blocking(0) → barrier → ¬flipping(-1)
```

The gradient has no incentive to cross from 0 to -1 because at 0 the
position is already silent. To reach -1, the mirror must pass through
a region where the contribution is near-zero and there's no loss signal
saying "flip would help."

## Proposed fixes (untested)

1. **Stacked decomposition**: mirror_1 = loom-read signs (provides initial
   structure), mirror_2 = correction at 1.0 (only needs to reach ±1,
   never crosses 0 because mirror_1 already provides the sign)

2. **STE (straight-through estimator)**: quantize to {-1,0,+1} in forward,
   continuous gradient in backward. Standard for binary/ternary networks.

3. **Random init**: some mirrors start negative, GD only refines

4. **Gumbel-softmax over {-1,0,+1}**: differentiable discrete selection

## Architecture captured

3-phase etch pipeline documented in etcher-vsm.md:
1. Blunt flip (hot anneal) — delta sign-flip, coarse corrections
2. Soft mirror (surgical GD) — CE + crystal loss, fine corrections
3. Quantize + freeze — fold mirrors into plates

Combinator mirrors = subcrystal selectors: 7 subcrystals are 7 mirrors
on one shared plate, not 7 separate extractions.

## Artifacts

| Script | Purpose |
|--------|---------|
| `soft_mirror_exp.py` | Per-dimension mirrors + crystal loss |
| `soft_mirror_v2_exp.py` | Per-position mirrors + stacking |
| `loom_etch_nucleation_exp.py` | 6-condition nucleation (LOOM_MAG=0.543) |
| `loom_delta_refine_exp.py` | Magnitude-only delta refinement |
| `loom_delta_signflip_exp.py` | Sign-flip delta refinement |
| `loom_crystal_sharpen_exp.py` | Crystal measurement during sign-flip |

## Memory

- `crystal-gates-hologram.md` — never accept sign flips that break crystal
- `soft-mirror-etch.md` — 3-phase pipeline, mirrors as subcrystal selectors
