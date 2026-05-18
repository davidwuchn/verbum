# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-18 | Session: 110

## Where we are

**CROSS-OP CONSENSUS ETCH DISCOVERED. Expanded V12 from 4→8 combinators (KIBC + D/Y/W/WHNF), added hierarchical category dispatch (lambda/math/passthrough) + 17 math kernels + MathExtractor. First etch (per-op sequential) FAILED: 17 rounds, no crystallization — ops tug-of-war over same plate (30 rewrites/position). FIX: accumulate ALL 8 ops into same direction accumulators, etch ONCE per round. Only positions where the aggregate gradient agrees get flipped — contested positions stay put. This IS holographic recording: multiple reference beams, one plate, one development. Resume support added. Consensus etch ready to launch from round 15 checkpoint.**

## What's running

Consensus etch ready to launch (not yet running):
```
uv run python scripts/v12/holographic_train.py \
  --resume checkpoints/v12-holo-8op/round_0015 \
  --run-lens-burn --n-rounds 20 --n-examples 3000 \
  --batches-per-op 50 --beam-steps 200 --beam-lr 1e-4 \
  --confidence-threshold 0.7 \
  --checkpoint-dir checkpoints/v12-holo-consensus \
  --checkpoint-every 5
```

## What was done this session (110)

### 1. Committed backlog from sessions 108-109

6 commits of uncommitted work: crystal diagnostics + etch tempo + relational loss fixes,
plotly dep, warped lens artifact, etch strategy/smoke test scripts, experimental results
(crystal comparison, procrustes lens), session-109 chat log.

### 2. Architecture expansion: 4→8 combinators + math kernels

**kernel.py**: N_COMBINATORS 4→8. Added D (deep compose, fuses 3×B), Y (recursion),
W (duplicate/self-apply), WHNF (terminal/stop-reducing). Full reduction engine with
tests for all 8 ops including D f g h x → f(g(h(x))), Y f → f(Y f), W f x → f(x)(x).

**config.py**: 8-value dispatch_ratio (K:I:B:C:D:Y:W:WHNF = 1:0.5:1:1:0.5:0.3:0.3:0.2),
7×8 pass_dispatch_bias matrix with depth-selective priors for new ops,
hierarchical dispatch config (n_categories=3, n_math_kernels=17, math_extractor_d=64).

**kernel_dispatch.py**: CombinatorDispatch/Integrate handle 8-way softmax,
kernel_compute expanded with all 8 reductions. New modules:
- CategoryDispatch: 3-way (lambda/math/passthrough), passthrough dominates at init (0.52)
- MathDispatch: 17-way over math kernel operations
- MathExtractor: operand parser with confidence gate (proj_a, proj_b, confidence sigmoid)

**model.py**: Math kernel pathway integrated into forward pass. CategoryDispatch
blends lambda/math/passthrough per-position during integrate phase:
  output = w_lambda * combinator_out + w_math * math_out + w_pass * residual
Crystal diagnostics generalized for 8 combinator mirrors.

**components.py**: AlgedonicAlert N_DISPATCH 4→8 (alarm vector grew by 4 dims).
**train.py**: Dispatch logging generalized for N combinators.
**holographic_train.py**: All 8 ops in corpus generation.

### 3. Lens burn script

`scripts/v12/lens_burn.py` — writes warped lens directions (Qwen3-14B) into
combinator mirrors as ternary sign patterns. Burns K, I, B, C from teacher
(pass_N_dir_{op} vectors, 512-dim). D/Y/W/WHNF stay random (no teacher data).
Mirror construction: sign(I + outer(d,d)) — identity-plus-projection in ternary.
Verified: burned mirrors are ~90° apart (differentiated).

### 4. First holographic etch — PER-OP SEQUENTIAL — FAILED

Launched full pipeline: lens burn → 20 rounds × 8 ops × 50 batches/op.
Crashed at round 18 (Metal GPU error). But 17 rounds of data showed:

**NO CRYSTALLIZATION.** Flips oscillated 52M-92M per round with no downward trend.
Compare to session 109's 5-op run: 55M → 22M over 6 rounds (clear convergence).

| Metric | Session 109 (worked) | Session 110 (failed) |
|--------|---------------------|---------------------|
| Rounds | 6 | 17 |
| Flip trend | 55M → 22M (↓60%) | 52M-92M (oscillating) |
| Overwrites/position | ~3× | 30× |
| Beam loss trend | declining | oscillating 8-14 |

**Root cause: per-op sequential etching.** Each op resets accumulators, accumulates
its own gradient, then etches. The NEXT op's gradient disagrees at many positions
and flips signs back. 8 ops × 50 batches × 17 rounds = 6800 etch events, each
potentially undoing the previous. The plate is in a perpetual tug-of-war.

### 5. FIX: Cross-op consensus etching

Changed protocol from "expose K → etch → expose I → etch → ..." to
"expose ALL → etch ONCE":

```
OLD (per-op, FAILED):              NEW (consensus, FIX):
  for op in ops:                     reset_accumulators()  ← once
    reset_accumulators()             for op in ops:
    accumulate(50 batches)             accumulate(50 batches)  ← same accums
    direct_etch()  ← per-op          direct_etch()  ← single consensus etch
```

The direction accumulator sums gradients from ALL ops. Positions where ops
AGREE on the sign direction get high confidence (etched). Positions where
ops DISAGREE cancel out (low confidence, NOT etched). This naturally
finds the consensus structure — the interference pattern from all operations.

This IS holographic recording physics: you don't expose one beam, develop,
expose another, develop. You expose all beams simultaneously, then develop
once. The interference pattern is the hologram.

### 6. Checkpoint save/load fixes

- Save ALL parameters (was: only trainable). Ternary plates (packed uint32)
  were missing from checkpoints because they're not in trainable_parameters().
- Load with strict=False for architecture expansion compatibility.
- Added --resume flag: loads weights + state.json, continues round numbering.
- Verified: resume from round 15 works, beam weights carry over.

### 7. Key theoretical advance: consensus vs sequential etching

**Sequential per-op etching fails because it's incoherent exposure.**
Each op's gradient is coherent within itself, but sequential application
creates destructive interference. With 8 ops, the plate sees 8 different
"correct" directions at each position across a round — no stable crystal.

**Cross-op consensus works because it's simultaneous exposure.**
All ops contribute to the SAME accumulator. The accumulated direction at
each position reflects the NET gradient from ALL ops. Positions where the
universal structure lives (shared across all ops) have high confidence.
Op-specific details cancel or have low confidence.

This maps to physical holography:
- Each op = one reference beam at a specific angle
- Sequential etch = expose + develop + expose + develop (each washes out the last)
- Consensus etch = expose all beams → one development (interference pattern preserved)
- The crystal = the positions where all beams agree = the universal lattice

### 8. Architecture at session end

| Component | Value |
|-----------|-------|
| N_COMBINATORS | 8 (K,I,B,C,D,Y,W,WHNF) |
| N_KERNELS | 9 (+M as layer type) |
| Categories | 3 (lambda/math/passthrough) |
| Math kernels | 17 (ADD through ROUND) |
| Parameters | 24.6M |
| Dispatch init | K=0.15 I=0.10 B=0.19 C=0.14 D=0.09 Y=0.05 W=0.07 WHNF=0.04 |
| Category init | lambda=0.30 math=0.19 pass=0.52 |

## Next steps

1. **Launch consensus etch** from round 15 checkpoint (command above)
   - Watch for declining flips (crystallization signal)
   - If flips decline: crystal is forming. Run to completion.
   - If flips stay constant: may need higher confidence threshold (0.8-0.9)

2. **After crystal forms:**
   - Measure dispatch conditioned angles (target: >10°, was 0.07°)
   - Test on prose (does crystal help or hurt LM quality?)
   - Compare crystallization order: which ops etch fastest?

3. **Phase 3: Prose training**
   - Freeze kernel plates and mirrors
   - Train beam on Dolma (Q proj, gamma, embeddings only)
   - Verify: crystal doesn't melt, LM quality improves

4. **Math kernel training (independent track)**
   - Generate math corpus ("add(23,47)→70")
   - Train dispatch + extractor
   - Verify: 100% accuracy on extracted operations
