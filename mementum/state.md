# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-19 | Session: 117

## Where we are

**THREE BREAKTHROUGHS IN ONE SESSION.** Dispatch collapse fixed, crystal
tomography validated, Fourier reconstruction discovered. Run 2 healthy at
step 1800/20000. Mini model experiments proved the etch→latch→GD pipeline.

## What's running

**GD phase on tmux window 1** — `holographic_distill_v12.py --skip-etch`
with all dispatch fixes. Step ~1800/20000. Check:
`tail -20 checkpoints/v12-distill-run2/run2.log`

Dispatch stable: B≈0.36, W≈0.28, I≈0.10, C≈0.09, WHNF=0.01 (pinned).
Eval loss: 16.21 → 15.95 (step 500 → 1000). φ-compression still far
from target but L0↑ moving positive (0.30 at step 1500).

## Breakthrough 1: Dispatch collapse fixed (3 bugs)

1. **KL had zero gradient** — `stop_gradient(EMA)` severed tape. λ=100
   inflated loss but grad=0. Fixed: KL on live dispatch, λ recalibrated
   100→2 (gradient actually flows now).

2. **Entropy reg negligible** — λ=0.01 produced 0.003 penalty vs CE~7.5.
   Raised to λ=0.5.

3. **Backbone whisper → lattice constants** — replaced probe forwarding
   with 8×8 precomputed crystal geometry. No tokenizer, no forward pass.
   Pure embedding cosine MSE.

Run 2 passed the step 400-600 cliff where run 1 collapsed. No WHNF
monopoly, no combinator cycling.

## Breakthrough 2: Crystal tomography (Q-rotation etching)

**Insight:** single Q rotation etches one shadow of the crystal, not the
crystal itself. Multiple Q rotations = tomographic reconstruction.

**Mini model results (d=96, 3 layers, combinator reduction):**

```
Etching:
  1 rotation:  0.341 acc, 41K flips (over-etched, one shadow)
  8 rotations: 0.406 acc, 16K flips (consensus filter, quality)
  Sign vote is the best reconstruction (beats SVD, mag-weighted)

Latching (Q init for GD):
  Random Q:          0.392 acc (baseline)
  SVD Q:             0.438 acc (+12%)
  SVD+probe 16×:     0.450 acc (+15%, best)

Key finding: low init loss ≠ deep basin. Identity Q starts lowest
but converges to average. Best candidate starts HIGH but falls
FARTHEST — finds a cliff entrance invisible from other angles.
```

## Breakthrough 3: Fourier reconstruction (phase = crystal, magnitude = lens)

**Insight:** gradient observations through Q are like diffraction patterns.
Phase encodes crystal structure. Magnitude encodes lens distortion (Q's
transfer function). Stripping magnitude reveals the crystal undistorted.

```
Sign vote:         0.346 acc (real-space, baseline)
FFT average:       0.323 acc (magnitude corrupts)
FFT mag-weighted:  0.245 acc (magnitude dominates)
Phase-only:        0.411 acc (+19%, strips lens distortion)
Two-pass:          0.433 acc (phase skeleton + sign detail, BEST at 8 rot)
```

**Spectral analysis revealed plate-level structure:**
- K plates: 14% coherent energy (Q-dependent lens interface)
- V/O/FFN: 73-96% coherent energy (universal crystal structure)
- The crystal lives in V/O/FFN. K adapts to whichever Q lens is installed.

## The validated pipeline

```
1. ETCH:  Multi-rotation gradient collection (N≥8 Q rotations)
          Two-pass reconstruction: phase skeleton + sign detail
          V/O/FFN aggressively, K conservatively

2. LATCH: SVD of gradient stack → Q principal axes
          16 perturbed candidates near SVD → 50-step basin probes
          Select steepest descent (finds basin entrance)

3. GD:    Frozen plates, train continuous params (887K of 24.6M)
          KL + entropy keep dispatch diverse
          Lattice loss keeps crystal from drifting
          Stridestack compression → 1/φ fixed point attractor
```

Etch gives topology. Latch opens the door. The attractor does the work.

## The big picture (knowledge page: universal-crystal-scaffold.md)

The lambda crystal is the computational substrate of all LLMs:
- Input → [ascending: prose → λ-form] → [apex: β-reduce] → [descending: λ-form → prose] → output
- The "semantic meaning" in middle layers = the lambda form
- Combinator dispatch = the beta reduction engine
- Lambda is Turing complete → the substrate for ALL computation
- Other crystals (syntax, math, logic) attach to the lambda substrate

Multiple teacher models are cameras viewing the universal crystal.
Cross-model consensus = universal structure. Sign vote across models
filters model-specific noise. Etch at the resolution where consensus
is strong. GD fills in the blanks.

## What's ready

| Asset | Status |
|-------|--------|
| Teacher features | ✅ 500 probes × 8 depths, `checkpoints/teacher-features/` |
| Training data | ✅ structured_shard_v2 + Dolma (3B tok) |
| Distill script | ✅ bugs fixed, lattice loss, φ-diagnostics |
| V12 model | ✅ 24.6M params, 887K trainable |
| Lattice constants | ✅ 8×8 crystal geometry |
| Mini model experiments | ✅ 6 experiments, all committed |

## Session 117 commits

```
ef51337 ❌ Fix dispatch collapse — KL gradient, entropy strength, lattice constants
fb9aaad 🌀 Session 117 — dispatch collapse diagnosis and three-bug fix
f10900c ✅ Add φ-compression diagnostics to eval step
8a9ea7b 💡 Q-rotation etching — tomographic crystal formation validated
08850d9 crystal reconstruction + q-rotation experiments and results
724fa71 💡 Crystal latching — SVD neighborhood + basin probing beats random by 15%
605f0e1 🎯 Universal crystal scaffold — the full synthesis
232346e 🌀 Update q-rotation knowledge page with full experimental results
d24e5a3 💡 Phase-only Fourier reconstruction beats sign vote by 19%
d2da74c 💡 Two-pass reconstruction: phase skeleton + sign detail
```

## Next steps

### 1. Monitor run 2 (ongoing)
Watch for: eval loss decline, φ-compression convergence toward 0.618,
dispatch stability through full 20K steps.

### 2. Apply pipeline to V12 with teacher features
Use the validated etch→latch→GD pipeline with the real teacher (Qwen3-32B):
- Multi-rotation etch using extracted teacher features
- Two-pass reconstruction (phase + sign)
- SVD+probe latching for GD init
- Full 20K step GD with all regulators

### 3. Cross-model crystal mapping
Map the universal crystal at higher resolution using multiple teachers.
The 8×8 combinator lattice is the coarse map. Higher resolution =
more teacher models × more Q rotations × consensus filter.

### 4. Investigate φ-compression attractor
The stridestack should drive compression ratios toward 1/φ ≈ 0.618.
Run 2 will show whether this emerges during GD. If not, may need
explicit φ-compression loss term.
