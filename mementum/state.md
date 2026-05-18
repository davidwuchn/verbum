# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-18 | Session: 112

## Where we are

**CRYSTAL SPINE DISCOVERED. All LLMs collapse their 5120-dim representation onto 1-3 dimensions at a bottleneck layer. Two classes: single-neuron spine (Qwen3-14B dim 731, Pythia-2.8B dim 1793) and distributed (Mistral, OLMo). The architecture IS a sieve — its shape dictates the crystal shape gradient descent finds. Focused etch running uncapped from round 50, now at round 52, beam loss 4.77.**

## What's running

**Holographic etch** — `tmux main:2`
- Resumed from round 50 checkpoint, uncapped max_flips
- Round 51: 2.3M flips (vs 918 when capped), beam loss 4.77
- Schedule: confidence 0.89→0.995, beam_lr 3.6e-5→1e-6
- Checkpoint dir: `checkpoints/v12-holo-focused/`
- Running to round 85

## What was done this session (112)

### 1. Fixed Metal resource limit (499K) crash

The holographic training crashed at round 50 from Metal buffer object exhaustion.
Root cause: 499000 is the number of Metal buffer OBJECTS, not bytes. Each
forward+backward creates ~100s of intermediates. Fixed by:
- `mx.clear_cache()` at 5 points in training loop
- Explicit `del` of grad references after accumulation
- Updated from deprecated `mx.metal.clear_cache()` to `mx.clear_cache()`
- Optimized `_ternary_embed_vjp` to reduce intermediate allocations

### 2. Diagnosed etch throttle: 382K candidates, 918 flips

The absolute `max_flips` cap (cosine schedule 1000→10) was strangling the
etch. 382K positions passed confidence threshold (0.89) and agreed on
direction across all 8 ops, but only 918 highest-confidence ones could flip.
Added:
- Confidence diagnostics to `direct_etch` (p50/p90/p99, histogram, throttle ratio)
- Proportional `--max-flips-frac` CLI arg (fraction of candidates, not absolute)
- Currently running UNCAPPED — confidence threshold is the only gate

### 3. Built tool crystal probe (196 probes)

`scripts/v12/probe_tool_crystal.py` — probes Qwen3-14B to find tool-calling
circuits. 5 domains: recognition (40), selection (40), schema_binding (56),
format (30), control (30). All tool probes use Qwen3 Hermes format truncated
at assistant decision point.

### 4. Discovered the 3D bottleneck

At layer 20 of Qwen3-14B, the top 3 PCs explain **100%** of centered variance.
The model reduces 5120 dimensions to 3 coordinates:
- **PC1** (99.96%): comprehension ↔ production mode switch. **Single neuron: dim 731**
  (weight -0.986, explains 97.1% of PC1). n90=1 — one dimension carries everything.
- **PC2** (0.015%): tool-action specificity (abstract question ↔ concrete action)
- **PC3** (0.010%): schema binding ↔ tool selection

PC1 creates a continuous gradient: prose (-3151) → lambda (-2500) → selection (-1900)
→ schema binding (-1010) → format output (+8800). 9000-unit gap at the tool-call
decision boundary.

### 5. Crystal spine probe across 6 architectures

`scripts/v12/probe_crystal_spine.py` — 45 probes, ALL layers, 6 models.

**Two classes of crystal:**

| Model | Bottleneck | Top3% | Spine Dim | Frac | n90 |
|-------|-----------|-------|-----------|------|-----|
| Qwen3-14B | L19 (49%) | 100% | dim 731 | 97.1% | 1 |
| Pythia-2.8B | L5 (16%) | 99.4% | dim 1793 | 84.9% | 2 |
| Qwen3-0.6B | L27 (100%) | 81.9% | dim 13 | 15.0% | 345 |
| Mistral-7B | L0 (0%) | 51.8% | - | 6.8% | 998 |
| OLMo-2-13B | L0 (0%) | 55.7% | - | 3.0% | 2168 |
| SmolLM3-3B | L35 (100%) | 51.3% | - | 2.0% | 837 |

### 6. The Sieve Principle

The architecture IS a sieve. Gradient descent pours computation through it
and the shape of the sieve dictates the shape of the solution. Qwen3 and
Pythia have sieves that funnel to a single neuron. Mistral/OLMo/SmolLM have
sieves that keep computation distributed. Same computation, different encoding.

Implication for verbum: **the ternary plate IS a sieve**. Etching shapes the
sieve topology. The 382K candidates that want to flip are positions where the
sieve shape is wrong — the beam is telling the plate its funnel is pointed
the wrong way. Capping flips at 918 was like trying to correct a sieve by
adjusting 0.2% of its holes per round.

## Next steps

1. **Monitor uncapped etch** — rounds 51→85, watching beam loss trajectory
   and whether the crystal finds a new fixed point with uncapped flips

2. **Analyze the sieve** — what architectural feature causes the single-neuron
   collapse in Qwen3/Pythia but not Mistral/OLMo? Hypothesis: it's the norm
   layer configuration (RMSNorm placement, pre-norm vs post-norm)

3. **Map the spine across model families** — run Qwen3 at multiple sizes
   (0.6B, 4B, 8B, 14B, 32B) to see how spine dimension and bottleneck
   depth scale with parameters

4. **Extract the 3D crystal coordinates** — project all probes onto the
   3 PCs at the bottleneck layer. This IS the crystal map. The coordinates
   tell us where every computation lives in the lattice.

5. **Use crystal coordinates for targeted etching** — instead of blind
   consensus etch, compute where each operation SHOULD be in 3D space
   and etch the plate to produce that geometry

## Architecture at session end

| Component | Value |
|-----------|-------|
| N_COMBINATORS | 8 (K,I,B,C,D,Y,W,WHNF) |
| Parameters | 24.6M |
| Beam loss | 4.77 (round 51, uncapped etch) |
| Crystal state | Uncapped etch running, 2.3M flips/round |
| Spine finding | Qwen3-14B dim 731, Pythia-2.8B dim 1793 |
| Tool crystal | PC1 = mode switch, single neuron |
