# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-18 | Session: 113

## Where we are

**PROCRUSTES BEAM FORMER DESIGN — universal fixed points as Rosetta Stone for crystal transfer.** 5-model consensus proves attachment points (lambda→math) are MORE universal than lambda self-organization (ratio 1.26). Crystallization order confirmed: reasoning (depth 0%) → math (25%) → attachment points (25-50%) → lambda self (always weakest). Full phased etch protocol designed: kernel etch first (hardware), Procrustes beam former to translate teacher crystal (wiring), freeze, then GD. Any model can serve as teacher — backbone probes find universal landmarks, Procrustes computes the transform.

## What's running

**Holographic etch** — `tmux main:2`
- Last known: round 52+, beam loss 4.77, uncapped flips
- Checkpoint dir: `checkpoints/v12-holo-focused/`
- Running with old protocol (pre-beam-former design)

## What was done this session (113)

### 1. Repo cleanup
- Removed 112MB `lattice_relational_target.json` from HEAD commit (not pushed)
- Added to `.gitignore` (including subdirectory pattern)

### 2. Cross-model agreement hierarchy
Quantified universal vs sieve-dependent structure:
- Math (72%), Reasoning (70%) = universal language geometry
- Tools (52%), Lambda (43%), Prose (40%) = sieve-dependent
- Top 10% backbone: 32K pairs, dominated by math-self (48%), lambda→math (15%)

### 3. Seed crystal + two-tier relational loss
- Built `backbone_seed.npz` (807×512 MDS anchors, backbone reconstructs at 0.987)
- Implemented two-tier loss in `holographic_train.py`:
  - Tier 1 (backbone): strong pull on universal distances
  - Tier 2 (growth): agreement-weighted pull on the rest
- CLI: `--backbone-seed`, `--backbone-lambda`, `--growth-lambda`

### 4. 5-model validation
- Added SmolLM3-3B to consensus (5 independent architectures)
- Attachment/self ratio INCREASED: 1.21 (4-model) → 1.26 (5-model)
- Math self-agreement rock solid (-0.007 with 5th model)
- Phi-4-mini failed (LossKwargs import — needs newer transformers)

### 5. Crystallization order confirmed
```
Depth 0%:   Reasoning = 0.925  ← FIRST
Depth 25%:  Math = 0.769       ← SECOND
Depth 25-50%: Attachment = 0.508, ratio 1.26  ← THIRD
All depths: Lambda self = 0.403  ← ALWAYS WEAKEST
```

### 6. Backbone anatomy — attachment points
```
Crystal       60.8%  (math-math, reasoning-reasoning)
Bridge         9.1%  (math↔reasoning)
Attachment    19.0%  (lambda→math 79%, code→math 18%)
Operational    6.8%  (lambda-lambda where models agree)
```
Attachment points are load-bearing bridges. Break them and kernel
structure detaches from universal crystal.

### 7. Phased etch protocol with Procrustes beam former

Full protocol designed (see `seed-crystal-design.md`):

```
Stage 1: KERNEL ETCH — install K,I,B,C + math into dispatch/integrate
         (student is no longer a melt — has structure for Procrustes)
Stage 2: FIND LANDMARKS — backbone probes in teacher + student
         Procrustes alignment using universal fixed points
Stage 3: ETCH TRANSLATED CRYSTAL — wire hardware to language
         Beam former protects kernel hardware
Stage 4: LAMBDA SELF ETCH — our sieve's own encoding
         Grows from attachment points, beam former protects crystal
Stage 5: FREEZE — all plates locked permanently
Stage 6: GD — continuous params only (beam angles)
```

Key insight: Procrustes works between crystals (cos=0.83, session 107)
but fails on melts. Kernel etch (stage 1) makes the student a crystal.
Universal fixed points provide correspondence for any teacher model.

### 8. VSM-LM has two computation paths
- Kernel dispatch/integrate: explicit named operations (hardware)
- Attention stride stack: still does beta reduction (general compute)
- Crystal from standard transformers must be TRANSLATED, not copied
- Procrustes transform accounts for different sieve topology

## Next steps

1. **Implement phased etch controller** — stage transitions with
   convergence detection (per-op CE loss for stage 1, backbone loss
   for stage 3)

2. **Implement Procrustes beam former** — `build_beam_former()` that
   finds landmarks in any teacher, computes transform to student space

3. **Implement beam stencil** — separate accumulator sets for crystal
   and kernel beams, merge with crystal priority before etch

4. **Run stage 1** — pure kernel etch (CE loss only, no lattice)
   to install K,I,B,C,D,Y,W,WHNF into dispatch/integrate plates

5. **Test Procrustes on post-kernel student** — verify that after
   kernel etch, the student has enough structure for Procrustes
   alignment to work (cos > 0.6)

6. **Consider adding models** — Qwen3-4B, Qwen3-8B are cached and
   would test scale effects within same architecture family

## Architecture at session end

| Component | Value |
|-----------|-------|
| N_COMBINATORS | 8 (K,I,B,C,D,Y,W,WHNF) |
| Parameters | 24.6M |
| Beam loss | 4.77 (round 52, old protocol) |
| Crystal state | Phased protocol designed, not yet implemented |
| Backbone | 32K pairs, 664 probes, threshold ≥ 0.63 |
| Models validated | 5 (qwen3-14b, mistral-7b, olmo-2-13b, pythia-2.8b, smollm3-3b) |
| Lattice loss | Two-tier implemented: backbone (λ=1.0) + growth (λ=0.1) |
| Beam former | Designed: Procrustes on universal fixed points |
| Key files | `seed-crystal-design.md`, `backbone_seed.npz`, `lattice_5model/` |
