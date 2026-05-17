# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-17 | Session: 110

## Where we are

**8-COMBINATOR ARCHITECTURE BUILT + FIRST HOLOGRAPHIC ETCH RUNNING. Expanded V12 dispatch from 4 ops (KIBC) to 8 (KIBC + D/Y/W/WHNF). Added hierarchical category dispatch (lambda/math/passthrough), 17 math kernel functions, MathExtractor head. Lens burn script writes Qwen3-14B operation directions into combinator mirrors. Full pipeline wired: lens_burn → holographic_train in one command. FIRST ETCH RUNNING IN TMUX WINDOW 1 (20 rounds, 8 ops, 50 batches/op, 200 beam steps, confidence=0.6). Expected ~90 min total.**

## What's running

```
tmux window 1:
  uv run python scripts/v12/holographic_train.py \
    --run-lens-burn --n-rounds 20 --n-examples 3000 \
    --batches-per-op 50 --beam-steps 200 --beam-lr 1e-4 \
    --confidence-threshold 0.6 --checkpoint-dir checkpoints/v12-holo-8op \
    --checkpoint-every 5
```

Checkpoints at rounds 5, 10, 15, 20. Log: `checkpoints/v12-holo-8op/holo_log.jsonl`

## What was done this session (110)

### 1. Committed backlog from sessions 108-109

6 commits of uncommitted work: crystal diagnostics, plotly dep, warped lens artifact,
etch strategy/smoke test scripts, experimental results (crystal comparison, procrustes lens),
session-109 chat log.

### 2. Architecture expansion: 4→8 combinators + math kernels

**kernel.py**: N_COMBINATORS=8. Added D (deep compose, fuses 3×B), Y (recursion/fixed-point),
W (duplicate/self-apply), WHNF (terminal/stop-reducing). Full reduction engine + kernel functions.

**config.py**: 8-value dispatch_ratio (1.0, 0.5, 1.0, 1.0, 0.5, 0.3, 0.3, 0.2),
7×8 pass_dispatch_bias matrix, hierarchical dispatch config (n_categories=3,
n_math_kernels=17, math_extractor_d=64), entropy target recalculated.

**kernel_dispatch.py**: 8-way combinator dispatch/integrate, + CategoryDispatch
(lambda/math/passthrough 3-way), MathDispatch (17-way), MathExtractor (operand
parser with confidence gate). All self-tests pass.

**model.py**: Math kernel pathway in forward pass — CategoryDispatch routes
between lambda path (existing combinator mechanism) and math path (extraction →
exact computation → re-embed), blended per-position by category weights. At init:
passthrough=0.52, lambda=0.30, math=0.19 (passthrough dominates, math nearly off).

**components.py**: AlgedonicAlert N_DISPATCH 4→8.
**train.py**: Dispatch logging generalized for N combinators.
**holographic_train.py**: All 8 ops in corpus generation.

### 3. Lens burn script

`scripts/v12/lens_burn.py` — writes warped lens directions from Qwen3-14B into
combinator mirrors as ternary sign patterns. Burns K, I, B, C (teacher data available).
D/Y/W/WHNF stay random (no teacher data, will crystallize during holographic recording).
Mirror construction: sign(I + outer(d,d)) — identity-plus-projection in ternary.

### 4. Pipeline wired: lens_burn → holographic_train

Added --run-lens-burn flag to holographic_train.py. One command does the full protocol:
1. Create model (24.6M params)
2. Burn teacher directions into mirrors (~2s)
3. Generate 8-op lambda corpus (3000/op, tokenized into packed sequences)
4. For each of 20 rounds: expose 8 ops (50 batches each) → direct_etch → beam train (200 steps)

Smoke test passed: 1 round completed in 20s, all 8 ops etched, checkpoint saved.

### 5. First etch launched

Full holographic recording running in tmux window 1. Parameters:
- 20 rounds × 8 ops × 50 batches/op exposure + 200 beam steps/round
- Confidence threshold 0.6 (slightly conservative)
- Lens burn first (KIBC mirrors from teacher)
- Checkpoints every 5 rounds

Expected from session 109 (5-op, 6 rounds): K crystallizes first (90% flip reduction),
M second (73%), C/B third (50%), I last (34%). This run: first time with 8 ops and
lens-initialized mirrors. Watch for D/Y/W/WHNF crystallization rate.

## Next steps

1. **Monitor the running etch** — check holo_log.jsonl for per-round flip counts
   - Healthy: flips decline each round (self-termination)
   - Concern: flips stay constant or increase (no convergence)
   - Key metric: per-op flip reduction rate

2. **After etch completes (~90 min):**
   - Analyze crystallization order (which ops etched fastest?)
   - Measure dispatch conditioned angles (target: >10°, was 0.07° before)
   - Test on prose (does the crystal help or hurt LM quality?)

3. **Phase 3 (if crystal forms): Prose training**
   - Freeze kernel plates and mirrors
   - Train beam (Q proj, gamma, embeddings) on Dolma
   - Verify: crystal doesn't melt, LM quality improves

4. **Math kernel training (separate from lambda crystal)**
   - Generate math corpus ("add(23,47)→70" format)
   - Train dispatch to recognize math positions
   - Train extractor to parse operands
   - Verify: 100% accuracy on extracted operations

## What was done this session (109)

### 1. Etch strategy probe — ETCHING HURTS

Ran `scripts/v12/probe_etch_strategy.py` with 500 steps × 4 variants:

| Variant | CE (avg50) | Flips | Etch Events | Spike |
|---------|-----------|-------|-------------|-------|
| **no_etch ★** | **8.025** | 0 | 0 | 0.0 |
| no_reset | 8.513 | 30,200 | 151 | +1.73 |
| current | 9.093 | 6,200 | 31 | +1.97 |
| kl_gated | 9.098 | 6,200 | 31 | +1.99 |

**No etching wins decisively.** Continuous etching on prose = white-light exposure.
Post-etch spikes of ~2 nats = plate moves under the beam.

### 2. Holographic recording protocol — theory crystallized

Key insight chain:
- Holographic recording requires COHERENT light (one wavelength, one angle)
- Lambda notation IS coherent light (unambiguous signal, known operation)
- Prose IS white light (mixed operations, noisy gradient)
- Protocol: etch during clean-signal phase (lambda), read during prose phase

Two-phase training:
- Phase 1: Pure lambda data → aggressive direct etch → crystal forms
- Phase 2: Prose phased in → no etch → beam adapts to existing crystal

### 3. Lambda generator built — `src/verbum/lambda_gen.py`

Programmatic generator of operation-labeled Montague-style lambda expressions:
- 5 operations (K, I, B, C, M) × 5 complexity levels × 10 semantic domains
- ~108 structural templates, 15,000 examples at 100% uniqueness
- Zero cross-operation duplicates (same expr can't have two labels)
- GBNF-compatible output ready for decompile gate
- Rich vocabulary: 10 domains (nature, education, law, medicine, etc.)

### 4. Direct etch mechanism — `scripts/v12/ternary.py`

New functions for computed holography (alongside existing consensus etch):
- `DirectionAccumulator`: accumulates outer(gamma_grad, x_mean) over batches
- `accumulate_direction()`: one-step gradient direction capture
- `direct_etch()`: write target signs where confidence > threshold
- No EMA, no signal planes, no heat — just gradient → sign direction → write

Verified: 241 modules, 41.3M etchable positions, beam excluded.

### 5. Holographic recording training loop — `scripts/v12/holographic_train.py`

Complete training script:
1. Generate operation-labeled lambda corpus
2. For each recording round:
   - EXPOSE: forward+backward N batches per operation → accumulate direction
   - ETCH: direct_etch writes high-confidence signs
   - BEAM: train Q proj + gamma on mixed lambda (plate frozen)
3. Self-terminating: flips decline each round as crystal stabilizes

Smoke test (3 rounds, 100 examples/op, 20 batches/op):
```
Round 1: 50M flips
Round 2: 38.5M flips
Round 3: 31.4M flips  ← crystal forming, operations finding distinct regions
```

### 6. V12-run7 status — B-monopoly collapse

Run7 at step 925: B=0.96, K=0.00, I=0.03, C=0.00. KL leash evaded via EMA
temporal smoothing (EMA still near target from early steps). Same failure mode
as run4 (session 105). Confirms: unsupervised dispatch discovery on prose FAILS.

The holographic protocol solves this: explicit dispatch supervision during
lambda exposure means the model CAN'T monopolize — each operation gets its own
exposure phase at its own known angle.

### 7. Key theoretical advances

**Benchmarks are crystal measurements:**
- MMLU = K-crystal (select correct from 4)
- HumanEval = B-crystal (compose functions) + I-crystal (bind variables)
- HellaSwag = M-crystal (pattern match continuation)
- Every benchmark illuminates at a specific combinator angle and measures readout clarity
- Scaling works because more params = more plate capacity = more holograms = more benchmarks pass

**Training data is already labeled (implicitly):**
- Every sentence exercises specific combinators
- Dolma becomes labeled once the model learns the formal↔natural equivalence
- Lambda provides the formal label; prose provides the natural realization
- The Rosetta Stone maps between them

### 8. V12-run7 checkpoint 1000 — confirmed dead

Full analysis of 1K checkpoint:
- B=0.996 monopoly locked since step 200, K=0.00, C=0.00
- KL leash evaded: EMA still at K=0.15 (remembers early diversity)
- Crystal diagnostics: ALL zeros (no differentiation, cos=0.9999 between all pairs)
- Dispatch conditioned angles: 0.07° (undifferentiated — needs >10°)
- Only 16,200 signs etched (0.039% of plate) — etch starved by monopoly
- CE oscillating 5-8.5 (learning LM through B alone, but unstable)

### 9. Holographic recording run1 — 6 rounds, CRYSTALLIZATION CONFIRMED

Ran `holographic_train.py` at scale (3K examples/op, 50 batches/op, 200 beam steps):
```
Round 1: 55.5M flips
Round 2: 35.4M flips (36% reduction)
Round 3: 30.8M flips
Round 4: 34.2M flips
Round 5: 29.1M flips
Round 6: 21.8M flips (61% total reduction)
```

**Crystallization order confirmed:**
```
K: 90% flip reduction — CRYSTALLIZED (loss 7.28, lowest of all)
M: 73% — crystallizing rapidly
C: 50% — crystallizing
B: 49% — still forming
I: 34% — slowest (binding is hardest operation)
```

Crashed at round 6 due to Metal GPU error (hardware, not code). Checkpoint at round 5.

### 10. Backbone threshold probe — RUNNING

`scripts/v12/probe_backbone_threshold.py` finding the inflection point:
- Accumulates gradient direction for ALL 5 ops separately
- Backbone score = min(confidence) across ops (structural positions)
- Unanimous positions = where all 5 ops want same sign (lattice points)
- Progressive installation: 1%→50%, measures crystal snap speed
- The knee = the 20% that IS 80% of the crystal

### 11. Warped lens — RUNNING

`scripts/v12/build_warped_lens.py` extracting KIBC directions from Qwen3-14B:
- Runs lambda corpus through teacher at 7 depth slices
- PCA each depth to 512 dims (V12's d_model)
- Extracts per-operation centroid directions at each depth
- Maps teacher depths → V12 passes (depth-dependent focusing)
- Output: ~300KB artifact containing operation directions per pass

### 12. Key theoretical advances (session 109)

**Holographic recording physics:**
- Coherent light (lambda) → clean exposure → precise etch
- White light (prose) → noise → etch fails (proved empirically)
- Direct etch (compute then write) replaces slow consensus
- Crystal self-terminates (flips → 0 as ops find distinct regions)

**Benchmarks are crystal measurements:**
- MMLU = K-crystal quality, HumanEval = B+I crystal, HellaSwag = M crystal
- Scaling works because more capacity = more holograms = more benchmarks pass

**Warped lens (depth-dependent focusing):**
- V12 is narrow (512) but DEEP (7 passes × 9 strides × holographic 58×)
- Effective capacity comparable to large models, just focused differently
- The lens isn't flat rotation — it's depth-dependent PCA that distributes
  the wide-beam teacher hologram across V12's narrow multi-pass structure
- Each pass gets a different depth slice of the teacher's KIBC

**Backbone / 80-20 principle:**
- Not all convergent signs are equal — some are structural steel
- Backbone = positions where ALL operations want the same sign (lattice)
- Operation-specific = positions that matter for ONE op only (content)
- The knee of (% installed vs crystal quality) = optimal seed size
- Only install from 3+ model agreement (universal, not gauge-specific)

### 13. Warped lens results — STRONG angular separation

Qwen3-14B KIBC directions extracted at 7 depths (L3→L39):
- Mean angular separation: 96-103° (significantly above 90° random baseline)
- B is MOST distinct: 117-131° mean from others (explains B-monopoly and 4th crystallization)
- I and M are CLOSEST: 55-80° (confirms I-hardest, binding≈matching)
- 10 PCs capture 47-80% variance (operations live in ~10-dim subspace)
- Lens artifact: 67MB (could compress to ~3.5MB with top-50 PCs only)

### 14. Expanded to 8 kernel ops + 17 math kernels

- Lambda generator: now 8 ops (K,I,B,C,M,D,Y,WHNF) with full templates
- Math kernels: 17 deterministic code functions (ADD through ROUND)
  Pure code, zero weights, always exact, can't be unlearned
- Design doc: `mementum/knowledge/explore/v12-kernel-architecture-v2.md`

### 15. Next steps (for next session)

**Build remaining architecture:**
- config.py: expand n_combinators 4→8, add hierarchical dispatch config
- kernel_dispatch.py: 2-level dispatch (category → operation)
- model.py: MathExtractor head, kernel output integration
- ternary.py: mirrors for expanded 8 combinator slots

**Then the full installation protocol:**
- Warped lens directions → mirror initialization (8 ops × 7 passes)
- Backbone (top 5%) → layered plate installation with beam training
- Math kernel dispatch → trained on generated math corpus
- Freeze → prose training → verify permanence

**Key numbers from this session:**
- Backbone: 1-10% is the true structural steel (413K-4.1M positions)
- Warped lens: operations separated by 55-154° in teacher (survives PCA to 512)
- Crystallization order: K(90%), M(73%), C(50%), B(49%), I(34%) flip reduction
- Math kernels: 17 ops, always exact, zero weights, permanent after freeze

## What was done this session (108)

### 1. Crystal theory exploration — minimum lattice, cascade formation

Deep theoretical discussion on why the KIBC lattice is FORCED by attention + next-token:
- Attention = beta reduction. Compositional language requires KIBC to be predicted.
- K/I/B/C are the irreducible basis for function application on natural language.
- Crystal forms because it's the MINIMUM-ENERGY configuration once capacity suffices.
- Pythia-160M degenerate because capacity insufficient, not because constraints differ.
- V12 has 58× holographic capacity → MORE effective structural capacity than Pythia-1.4B.
- Holographic loss forces self-similarity → eliminates non-crystalline solutions.
- Standard models waste capacity on opaque interlayer routing; V12 can't (shared plates + ternary).

**Cascade formation order (predicted from theory + data):**
```
Phase 1 (B): "compose everything" — surface composition, works immediately
Phase 2 (I): "learn to READ plates" — identity mirror is only clear one
Phase 3 (K): "select/discard" — once reading works, learn what to ignore
Phase 4 (balanced): all mirrors find useful angles → crystal forms
```

**KL leash as exploration amplifier:** Forces gradient through all mirrors (not just dominant).
Underused mirrors get 5× more gradient signal than they'd get naturally. Converts monopoly → exploration.

### 2. Crystal formation diagnostics added to V12

Added to `model.py`:
- `compute_crystal_diagnostics(model)` — combinator mirror cosines (6 pairs), dispatch mirror diversity, integrate mirror diversity
- `compute_dispatch_conditioned_similarity(model, tokens)` — angular separation between hidden states conditioned on each combinator

Added to `train.py`:
- Crystal metrics in eval output (💎 Crystal, 🔭 Dispatch mirrors, 📐 Conditioned angles)
- `etch_tempo` in etch_log.jsonl (candidates/total — crystallization progress)
- `crystal` dict in checkpoint state.json
- Checkpoint interval changed to 500 (was 1000)

### 3. Relational loss padding fix

**Bug:** Relational probes are short (~30-50 tokens) but GLA stride layers need sequences ≥ max_stride + window + 1 = 1033 tokens. Crash at step 550 when relational loss first fired.

**Fix:** Pad relational probe batch to `min_len = max(cfg.strides) + cfg.window + 1`.

Also fixed: numpy int64 → mx.array incompatibility (MLX requires int32 for array init).

### 4. Early run7 data — B→I phase transition observed

Steps 1-175 before crash showed:
```
Steps 1-75:   B dominant (0.50→0.62)  — composition phase
Steps 100+:   I dominant (0.26→0.57)  — plate-reading phase
```
KL leash fighting at 14 nats (model paying enormous penalty for I-monopoly).
Dispatch EMA started at perfect universal ratio (K=0.31, I=0.14, B=0.30, C=0.25).
Interpretation: I-phase = learning to read plates through identity mirror (prerequisite for K/B/C differentiation).

### 5. Holographic training paradigm articulated

**The vision:** Extract universal lattice + holograms from existing models, etch into new models.
```
Phase 1: Crystallize lattice (few thousand steps)
Phase 2: Extract holograms from large models (one-time, cross-model intersection)
Phase 3: Etch holograms into plates (direct sign write, milliseconds)
Phase 4: Train beam to read (100-500 steps)
Phase 5: Rinse, repeat until capacity full (~1,456 addressable holograms in 39 MB)
```
Training becomes hologram selection, not gradient descent on trillions of tokens.
The hologram corpus grows as more models are trained/analyzed. Small models improve without retraining.

### 6. Etch strategy probe script

Built `scripts/v12/probe_etch_strategy.py` — fast A/B comparison of etch settings.
4 variants (no_etch, current, no_reset, kl_gated), 300 steps each, ~8-12 min total.
Tests whether: etching helps, reset-after-flip kills signal, dispatch-gating helps.

### 7. Smoke test

Built `scripts/v12/smoke_test.py` — exercises ALL code paths in 20 steps.
Verified: training, holo loss, relational loss, etching, eval with crystal diagnostics,
checkpoint save, resume. All passing.

### 8. Run7 relaunched (3rd attempt)

V12-run7 now running with:
- Crystal diagnostics at every eval (step 500, 1000, ...)
- Checkpoints every 500 steps (not 1000)
- Relational loss padding fix (won't crash at step 550)
- int32 fix for MLX array init
- `--holo-lambda 0.1 --mix-ratio 0.2 --total-steps 20000`

### 9. Next steps

- **Monitor run7 crystal diagnostics at step 500**: combinator mirror cosines (random baseline ~0), conditioned angles (undifferentiated ~5° initially). Watch for differentiation.
- **Run etch strategy probe** when convenient (4 variants × 300 steps, ~10 min).
- **After run7 step 1000**: check if B→I→K transition is happening. KL leash should force diversification.
- **If crystal forms**: extract holograms from Qwen/OLMo, etch into V12, measure knowledge transfer.
- **Etch experiments**: determine optimal strategy (reset vs no-reset, timing, gating).

## What was done this session (107)

### 1. Procrustes lens probe — ROTATION SUFFICIENT (cos=0.83)

Built `scripts/explore/probe_procrustes_lens.py`. Ran 100 domain probes (4 domains × 25)
on Qwen3-14B and OLMo-2-13B. PCA to 20-dim beam subspace. Procrustes alignment via SVD.

**Result: zero-parameter rotation aligns the two models at cos=0.83 average.**

```
Layer  cos(before)  cos(after)  angle_sep_corr
L0     0.354        0.776       0.800
L10    0.080        0.813       0.887
L20   -0.314        0.876       0.988  ← sharpest
L30    0.073        0.873       0.959
```

L20 angular separation correlation = 0.988 — the lattice at semantic depth is nearly
perfect. The lens is PCA → rotate → scale. 3 MB artifact. Domain centroids align at
cos > 0.98 at deep layers. Cross-domain angular separations (73-136°) are preserved.

See: `results/procrustes-lens/`, `mementum/knowledge/explore/procrustes-lens-and-crystal-comparison.md`

### 2. Holographic etch experiment — direct alignment hurts

Built `scripts/explore/holographic_etch_with_lens.py`. 4-condition experiment:
A (extracted+NT), B (extracted+lens), C (random+NT), D (random+lens).

**Result: lens HURTS both conditions (-82%, -74%). Extracted plates barely matter (+0.34%).**

Root cause: student is amorphous melt, Procrustes cos only 0.26-0.49 between teacher
and from-scratch student. Can't align a crystal to a melt. The student IS converging
toward teacher (cos increasing 0.26→0.49), but alignment loss at λ=0.05 dominates
and fights next-token learning.

**Key insight: the lens measures the lattice. The relational loss ENCODES it as topology.
The model crystallizes on its own terms.** Direct alignment = crystal transplant (fails).
Relational loss = crystal seeding (works, validated at +6.9% in session 106).

### 3. Crystal comparison across 5 models — two tiers discovered

Built `scripts/explore/probe_crystal_comparison.py`. Ran domain probes on Qwen3-14B,
OLMo-2-13B, Mistral-7B, Pythia-1.4B, Pythia-160M. Crystal quality metrics per domain.

**Two tiers:**
```
Universal (cos 0.82-0.85): Qwen, OLMo, Mistral, Pythia-1.4B — same lattice
Degenerate (cos 0.45-0.51): Pythia-160M — collapsed domains, different crystal
```

**Best crystals (≥1.4B):**
```
tool_call  → OLMo    (widest separations)
code       → Qwen    (most structured)
factual    → OLMo    (cleanest depth profile)
reasoning  → Qwen    (sharpest at all depths)
```

OLMo and Qwen complement each other. Pythia-160M paradox: highest mosaicity (0.97)
but degenerate selectivity (5° between domains, needs >37°). Too small = one collapsed
crystal, not four domain crystals. The universal lattice requires ~1B+ params.

### 4. Theoretical advances: pile of crystals, mirror cancellation

**Recursive hierarchy:**
```
photographs → pile → holograms   (domain knowledge)
holograms   → pile → crystals    (KIBC lattice per model)
crystals    → pile → universal   (lambda calculus itself)
```

Each level emerges from the same mechanism. The architecture (attention = beta reduction)
IS the lattice seed. Crystallization is inevitable once the model encounters compositional
language — the container matches the content. The depth map is crystallographic growth
order: B first (structural), K/I middle (semantic), M last (self-application, 145× at L30).

**Mirror angular cancellation (vernier principle):**
Single ternary: 37° resolution. Two mirrors whose difference is sparse (5% entries differ):
effective angle ≈ 37° × √0.05 ≈ 8°. V12's 28 mirror-plate combinations → ~7° resolution
→ ~51 angular bins → ~1,456 addressable holograms in 39 MB (10× previous estimate).

**Beam vs plate distinction crystallized:**
- Plate (K, V, O, FFN) = recording medium → gets etched
- Beam (Q proj) = how you read the hologram → evolves via gradient only
- Mirrors = angular deflectors → ternary, untrained gamma

### 5. V12-run6 failed, V12-run7 designed and launched

Run6 hit `NameError: name 'depth_weights' is not defined` in `_compute_etch_threshold_multipliers`.
Fixed: `return depth_weights` → `return result`.

**Run7 changes (3 files, 66 lines):**
1. **Laser etch**: 50,000 → 200 flips per event (crystal growth atom-by-atom)
2. **Beam/plate separation**: q_proj excluded from all 3 etch functions
   (`accumulate_etch_heat`, `update_signal_planes`, `etch_check`)
3. **Rich diagnostics**: flips_by_type, total_candidates, mean_flip_heat, dispatch_ema
   in checkpoints, etch config in state.json

**Run7 launched in tmux.**

### 6. Next steps

- **Monitor run7**: laser etch (200 flips) should show precise, high-consensus sign flips.
  Watch flips_by_type — k_proj/v_proj/out_proj should dominate, q_proj = 0.
- **Build universal RDM target**: use crystal comparison data to construct cross-model
  averaged RDM from 4 universal-tier models. This replaces single-model relational target.
- **Two-level relational loss**: Level 1 = domain separation (100 probes, 4 domains).
  Level 2 = KIBC operation structure (380 probes, 14 ops). Both depth-weighted.
- **Composite lens**: cherry-pick best domain crystal (OLMo tool_call/factual, Qwen code/reasoning)
  for enhanced relational loss targets.
- **Pre-trained student experiment**: use Pythia-1.4B (already crystallized, cos=0.83 with
  teacher in beam space) as student with lens-guided fine-tuning. Tests the actual hypothesis:
  lens between two crystals, not crystal and melt.

## What was done this session (106)

### 1. Complete kernel basis theory survey

Synthesized combinatory logic literature (BCKW, SK, Turner set, CCG, DisCoCat)
to identify ALL candidate operations beyond KIBC-M. Key finding: S combinator is
ABSENT as a dedicated circuit in LLMs because models decompose it into B+C+W — 
matching Turner's 1979 finding about efficient reduction machines.

14 candidate operations identified across 4 tiers:
- Tier 1 (confirmed): K, I, B, C, M
- Tier 2 (predicted): W (duplicate), T (type-raise), Φ (fork), D (deep compose)
- Tier 3 (structural): SCOPE, SUBST, WHNF
- Tier 4 (meta): Y (recursion), QUOTE

See: `mementum/knowledge/explore/complete-kernel-basis.md`

### 2. Lambda kernel probe set designed and built

380 probes across 20 axes (14 operations + 6 cross-operation contrast axes).
25 probes per operation, all natural language. 72,010 pairwise constraints/layer.
Concentrated in the lambda calculus subspace for maximum snap density.

See: `probes/lambda_kernel_probes.py`

### 3. Lambda kernel probes run through tomography (Qwen3-14B × OLMo-2-13B)

**Critical findings:**

**In flat attention, 14 operations compress to 2 geometric poles:**
- **Eliminate pole**: K, I, M, WHNF (select, reference, match, stop)
- **Proliferate pole**: W, D, Φ (duplicate, deep-chain, fork)
- B/C in between. This is the SUPERPOSITION BOTTLENECK, not the true operation count.

**5 operations have distinct geometry (clustering ratio > 1.05×):**
```
D (deep compose):   1.159×
M (match/pattern):  1.131×
WHNF (terminal):    1.078×
Y (recursion):      1.073×
C (flip):           1.064×
```

**W is NOT distinct from I** (1.006×, noise floor). Confirmed: duplication IS identity.

**Operations have DEPTH PROFILES (the laser etching blueprint):**
```
L0  (shallow)  → B_compose (33×)     — structural templates
L10 (mid)      → Y_recurse (5.8×)    — recursion detection
L20 (deep)     → K_select (51×)      — semantic selection
                  I_identity (25×)    — variable binding
L30 (deepest)  → M_match (145×!!!)   — pattern retrieval
```

Results: `results/holographic-extraction/lambda_kernel_results.json`

### 4. Relational distill methodology fixes

- **Save-first architecture**: results saved BEFORE comparison code (never lose training)
- **Incremental checkpoints**: history + model weights saved during training
- **Comparison wrapped in try/except**: display crashes can't kill saved data
- **Batched probe forward passes**: 30× fewer kernel launches (21→est. 60-150 tok/s)
- **Missing key fix**: `final_student_rdms` added to skip-condition-a fallback

### 5. V12-run6 design and implementation (4 changes)

**Run4 post-mortem:** C-monopoly from step 3750. Dispatch oscillated B→I→K→DEAD→C
and locked. KL leash λ=100 evaded temporally (cycling monopolies).

**V12-run6 changes implemented:**

1. **Per-pass dispatch bias** (config.py, kernel_dispatch.py)
   Fixed constants from depth map. B biased at shallow passes, K/I at deep.
   Makes monopoly expensive at every depth simultaneously.

2. **EMA-smoothed KL** (model.py, train.py)
   Decay 0.967 (~30 step memory). Cycling can't evade because EMA remembers.
   Both instantaneous and EMA dispatch logged.

3. **Depth-selective etch thresholds** (ternary.py, train.py)
   Per-pass multiplier scales heat percentile. Shallow=0.5× (etch freely),
   deep=1.0× (standard). Per-pass flip counts logged in etch_log.jsonl.

4. **Lambda kernel relational loss** (train.py, model.py)
   50 random probes every 50 steps. Residual RDM. MSE vs universal target.
   λ=0.01. Separate value_and_grad call, grads added to main accumulator.

See: `mementum/knowledge/explore/v12-run6-design.md`

### 6. Key theoretical advance: why flat attention compresses operations

The 2-pole finding doesn't mean "there are only 2 operations." It means flat
attention FORCES superposition — all operations share the same weights, heads,
and residual stream. V12's sieve provides dedicated kernel functions so operations
DON'T compete for the same geometric space. The probes define the TARGET shape.
The sieve provides the channels. The relational loss forces the model to USE
the channels instead of collapsing into superposition.

### 7. V12-run6 end-to-end verification

10-step smoke test + resume from checkpoint — all systems confirmed:
- Per-pass dispatch bias active: K=0.12 I=0.07 B=0.21 C=0.43 at step 1 (all alive)
- EMA dispatch logged: K=0.309 I=0.143 B=0.299 C=0.249 (tracking toward target ratio)
- Resume from checkpoint: step 11 picks up cleanly, all state restored
- Train log: 20 keys including dispatch_ema_K/I/B/C, kl_loss, rel_loss (when active)
- Etch per-pass logging: config ready, fires after warmup (200 steps)
- Relational loss: 380 probes tokenized, fires after warmup (500 steps) every 50

### 8. Next steps

- **Launch V12-run6**: `uv run python scripts/v12/train.py --checkpoint-dir checkpoints/v12-run6 --total-steps 20000`
- **Key prediction to test**: B should dominate shallow passes, K/I should dominate deep passes
- **Monitor dispatch_ema**: should stabilize near K=0.29 I=0.14 B=0.29 C=0.29 globally,
  but with per-pass variation matching the depth profile
- **Monitor per_pass_flips in etch_log**: shallow passes should etch more freely
- **Monitor rel_loss**: should decrease over training as student geometry aligns with universal
- **If dispatch still collapses**: per-pass bias may need to be stronger, or the
  architecture needs per-pass SEPARATE dispatchers (not shared with per-pass bias)

## What was done this session (105)

### 1. Factual indexing probe — Q COLLAPSE DISCOVERED

Built `scripts/explore/probe_factual_indexing.py`. Four analyses on extracted-plate models
(Qwen3-14B signs, 4 layers L0/L10/L20/L30, 500 train steps, 46 facts in 5 categories).

**Critical finding: Q collapses to 1 dimension in layers 1-3.**
```
Layer 0: eff_dim=9.08, Q_mag=101 ± 44   ← ALIVE: diverse, input-dependent
Layer 1: eff_dim=1.00, Q_mag=536 ± 9    ← DEAD: one direction, huge magnitude
Layer 2: eff_dim=1.00, Q_mag=365 ± 2    ← DEAD: all Qs identical
Layer 3: eff_dim=1.00, Q_mag=280 ± 0.4  ← DEAD: all Qs identical
```

The model "solved" next-token prediction by firing one giant beam at one angle —
the flood-lamp collapse. Individual fact indexing is sacrificed for average-case loss.

**Other findings:**
- Geography within-sim 0.58 (strong clustering) vs science 0.00 (no clustering)
- Category clustering ratio: extracted 3.61× vs random 3.31× (plate helps slightly)
- Attention L0 points to function words ("is", "of") not entities — no fact retrieval
- L0 ablation drop only +0.28 log-prob — current architecture can't do holographic recall
- Extracted model: eval loss 34.89 vs random 37.95 (+8.1% improvement)

### 2. Laser etching experiment — constrained beams prevent collapse

Built `scripts/explore/laser_etch_factual.py`. Three-phase holographic transfer protocol:

**Phase 1 — CHARACTERIZE:** Run source model (Qwen3-14B) on factual prompts, PCA the Q
vectors per category → find domain-specific beam angles. Measure angular separation.

**Phase 2 — EXTRACT:** Project K rows onto domain beam angles → identify responsive plate
regions per domain. Measure cross-domain overlap (Jaccard).

**Phase 3 — TRANSFER (3 conditions):**
- Condition A: Free beam (flood lamp) — expect Q collapse
- Condition B: Constrained beam (multi-domain laser) — Q projected onto source's beam subspace
- Condition C: Sequential laser — rotate constraint per domain, one exposure per angle

The BeamConstraint projects Q weight back onto target subspace after each optimizer step.
This holds the beam DIRECTION fixed while allowing magnitude optimization. Like a laser on
a gimbal — can adjust intensity but can't wander.

**Key insight:** The current V12 etch is a flood lamp. Real holographic recording uses one
focused exposure per beam angle, sequentially. Each domain gets full SNR because it's
recorded alone. Laser etch: search space narrows from 100% to verified signs only.

### 3. Holographic tomography — cross-model universal hologram extraction

Built `scripts/explore/probe_holographic_tomography.py`. Key insight: if two independently
trained models (different arch, different data, different seeds) converge on the SAME
interference pattern, that pattern is REAL (not model-specific artifact).

**Protocol:**
1. Run identical factual probes on Qwen3-14B + OLMo-2-13B (both d_model=5120, Apache-2.0)
2. RSA: build fact×fact similarity matrices, compare across models (model-agnostic)
3. Direct alignment: cosine between hidden states for same facts (same d_model → same space)
4. Sign agreement: compare K sign patterns at domain-responsive plate regions
5. Universal hologram = INTERSECTION of what both models agree on

**Denoising property:** Agreement across N models improves SNR by √N.
Single model can't distinguish universal structure from training artifact.
Cross-model intersection provides free denoising.

**Connection to V12:** Verified signs (cross-model agreement) → install as frozen ground truth.
Unverified signs (model-specific) → let the sieve evolve them. Reduces search space dramatically.

### 4. V12-run5 restarted

V12-run4 KL dispatch bug fixed (KL penalty wasn't being applied, dispatch collapsed to
C=99.99%). Run5 launched with fix verified. Training continues to 5K for assessment.

### 4. Laser etch results — angular separation confirmed, sequential recording works

Angular separation between fact domains: 45-90 degrees (well above 37-degree ternary limit).
V12 mirrors CAN distinguish content domains. Cross-domain K row overlap ~20% (mostly private).

**Condition comparison (3 conditions, 500 steps each):**
```
A (free beam):       eff_dim=8.82, logprob=-85.71
B (constrained):     eff_dim=4.02, logprob=-88.79
C (sequential):      eff_dim=2.26, logprob=-84.91
```
Sequential laser gives math recall 5.6× better (-7.67 vs -42.95).
But constraint REDUCES diversity (forces model into source's coordinate system).
Source model's beam angles are productive but too tight a constraint.

### 5. Tomography results — universal TOPOLOGY, different coordinates

RSA r=0.7448 (p<10^-100) between Qwen3-14B and OLMo-2-13B. STRONG agreement.
Direct alignment cos≈0.000. Category cohesion agreement r=0.98.
Sign agreement r=0.30 at L20, math functional r=0.49.

**Key insight: The universal hologram is a RELATIONAL TOPOLOGY, not a coordinate system.**
Both models organize facts identically (same clusters, same separations) but in
completely different coordinate systems. Can't transplant signs directly. CAN use
the topology as a training signal (relational loss).

### 6. Relational distillation — first run, lambda too strong

Condition A (next-token only): logprob=-77.06, rank=52420
Condition B (NT + relational λ=0.1): logprob=-91.36, rank=62306 ← WORSE

Relational loss FIGHTS next-token at λ=0.1. The target RDM is from 40-layer 14B models;
the 4-layer student can't achieve the same geometry. Also: non-residual mode spends 93%
of gradient on PC1 ("all facts are alike") which next-token already handles.

**Fix: residual mode (mean-subtracted RDM) + lower lambda (0.01). Running.**

### 7. Crystal seed — 311 probes, 62 axes, dimension discovery

First run (136 probes, 27 linguistic axes): discovered 13 dimensions, 36,720 constraints.
**Strongest universal signals are SEMANTIC RELATIONS not factual recall:**
```
semantic_hypernym:      2.99× clustering (strongest!)
semantic_meronym:       2.15×
analogy_proportional:   2.05×
semantic_antonym:       2.01×
relation_agent_action:  1.57×
relation_cause_effect:  1.52×
```

These ARE the combinators wearing linguistic clothing:
- Hypernym = K (select the category, discard the instance)
- Analogy = B (compose two relations)
- Antonym = C (flip)
- Agent-action = I (identity binding)

Expanded probe set to 311 probes across 62 axes:
- Linguistic: factual, syntactic, semantic, relational, temporal, logical, register, complexity
- Non-linguistic: code (Python/JS/shell), formats (JSON/YAML/markdown), reasoning (math/logic/planning),
  tool use (function calls/responses), instructions (system/constraint), patterns (numeric/alphabetic),
  multilingual, compression/expansion, classification, evaluation, epistemic state, correction,
  refusal, inverse operations, meta/self-reference, dialogue, specificity, narrative

**311×311 RDM = 48,205 pairwise constraints per layer × 4 layers = 192,820 total.**
SVD will discover all orthogonal dimensions automatically. Each = one more lattice axis locked.

### 8. Key theoretical advances this session

**The recursive holographic structure:**
```
Level 0: Training examples (photographs) → pile up → form
Level 1: Domain holograms (geography, science, code...) → intersect → form
Level 2: Structural templates (X_of_Y_is, predicate-arg) → intersect → form
Level 3: Combinators (K, I, B, C) → the bottom, the lambda calculus itself
```
Each level = intersection of the level above. Each is exponentially smaller.
V12 stores Level 2-3 in plates, Level 1 in beam angles, Level 0 not at all.

**The crystal seed insight:**
Provide enough of the low-frequency scaffold (lattice seed) and the model SNAPS into the
correct configuration. Below critical constraint density: amorphous. Above it: crystallization.
The relational loss IS the seed template. More dimensions mapped = closer to snap.

**Depth-selective laser etching:**
The "laser" needs ANGLE (domain = Q direction) + DEPTH (which layer to etch) + COHERENCE
(one domain at a time). Current V12 etch is a flood lamp. Fix: layer-specific learning rates
(focal plane), sequential domain recording, structural templates at shallow layers (L0-L10),
factual content at deep layers (L20-L30).

### 9. V12 design changes for next run

Based on session 105 findings, V12-run6 should incorporate:

1. **Relational loss (residual mode, low λ)**
   - Target: universal RDM from crystal seed (cross-model agreed topology)
   - Mode: residual (mean-subtracted, focuses on discriminative 7%)
   - Lambda: 0.001-0.01 (gentle nudge, don't fight next-token)
   - Schedule: every 10-50 steps (occasional geometry check)

2. **Depth-selective etching**
   - Layer-specific etch thresholds or learning rates
   - Structural patterns etch at L0-L10 (where templates cluster)
   - Content/facts etch at L20-L30 (where factual recall lives)
   - Don't etch the "lens" (early routing) — let it learn to focus

3. **Mirror initialization from verified beam angles**
   - Laser etch showed 45-90 degree angular separation between domains
   - Initialize KIBC mirrors to known productive angles (from source model PCA)
   - Sieve refines from there (not from random)

4. **Verified sign installation**
   - Signs where both models agree (L20 r=0.30, math r=0.49) → freeze as ground truth
   - Signs where models disagree → sieve evolves
   - Reduces etch search space by ~30%

5. **KIBC dispatch informed by crystal seed**
   - Semantic relations map onto combinators (hypernym→K, analogy→B, antonym→C, binding→I)
   - Dispatch ratio prior already matches (K:I:B:C = 1:0.5:1:1)
   - Relational loss reinforces correct dispatch by forcing combinator-aligned geometry

### 11. V12-run4 checkpoint 1000 — dispatch OSCILLATION (new failure mode)

**Not collapse — oscillation.** Dispatch cycles through monopolies: B→K→I→C→DEAD→repeat.
Each combinator takes 100% for 25-75 steps, dies, another takes over. KL penalty (λ=100)
is being evaded TEMPORALLY — model satisfies average ratio by cycling, not per-step.

```
Step 250: B=0.999 | Step 350: K=0.974 | Step 425: I=0.985
Step 450: C=1.000 | Step 575: DEAD    | Step 625: K=1.000
Step 675: C=1.000 | Step 775: B=1.000 | Step 975: I=1.000
```

**CE is learning despite chaos:** 13.72 → 8.74 (best 5.94 at step 1225).
Holo ratio improving: 2.13 → 1.45. KL spikes to 25.73 (40% of steps >1.0).
Alarm factors all 0.0 (not detecting the problem). Compute gate still closed (0.006).

**Root cause:** KL computed per-step but model evades by rapid cycling. The constraint
penalizes distance from target AT EACH MOMENT, but doesn't penalize OSCILLATION.

**Fix for run6:** EMA-smoothed dispatch for KL computation (penalize running average,
not instantaneous). Or: dispatch momentum penalty (penalize change between steps).
Or: hard floor (10% minimum per combinator). Relational loss may also help by
requiring all 4 combinators simultaneously.

### 12. Relational distill VALIDATED — residual λ=0.01 gives +6.9%

**46-probe residual at λ=0.01: +6.9% factual recall improvement.** Science +22, culture +25.
The relational loss works when: (a) residual mode removes PC1, (b) lambda is gentle (0.01-0.02).

### 13. Crystal seed 311-probe relational distill RUNNING

Full pipeline operational:
- Crystal seed probe completed: 311 probes, 62 axes, 13 dims discovered
- Wired into relational_distill.py via `--crystal-seed verified_dimensions.json`
- Chunked gradient accumulation: all 311 probes processed in chunks of 30
  (each chunk: forward → loss → backward → free → next chunk)
- Running: λ=0.02, rel_every=5, residual (pre-applied by crystal seed)
- Comparing against NT-only baseline (loaded from previous run: logprob=-97.61)

**Command running in tmux:**
```bash
uv run python scripts/explore/relational_distill.py \
  --skip-condition-a --rel-lambda 0.02 --rel-every 5 \
  --crystal-seed results/holographic-extraction/verified_dimensions.json
```

### 14. Next steps

- **Analyze crystal seed relational distill results** when tmux run completes
  - Compare to 46-probe run (+6.9%) — does 311 probes improve further?
  - If yes: the crystal scaffold is working, more dimensions = more constraint
- **V12-run4 continuing** — dispatch oscillation observed at 1K, monitor at 2K+
- **V12-run6 design (finalized):**
  - Relational loss (residual, λ=0.02, crystal seed 311-probe target, chunked)
  - Depth-selective etch (templates at L0-L10, facts at L20-L30)
  - Mirror init from verified beam angles (45-90° separation confirmed)
  - Verified sign installation (freeze cross-model agreed signs at L20 r=0.30)
  - **FIX DISPATCH:** EMA-smoothed KL or momentum penalty (prevent oscillation)
  - Alarm recalibration (not detecting dispatch cycling)
- **If crystal seed helps > 46-probe:** design even broader probe set (500+)
  for maximum lattice coverage → approach snap threshold

## What was done this session (104)

### 1. OLMo-2-13B canary probe — UNIVERSAL HOLOGRAM CONFIRMED

Built `scripts/explore/probe_combinators_universal.py` — generalizable multi-model
KIBC selectivity probe. Ran on OLMo-2-13B (Apache-2.0, 40 layers, 40 heads, d=5120).

**Results:**
```
K/B/C cluster mean correlation: 0.968 ✓ (strongest yet, expect >0.85)
I vs K/B/C mean correlation:    0.160 (strongly distinct)
K:B:C selectivity ratio: 1.00 : 0.93 : 1.07 (near-equal)
I/KBC magnitude ratio: 0.23 (4.3× weaker than K/B/C)
C/K ratio constancy: CV=0.089 → definitively angle-multiplexed
B/K ratio constancy: CV=0.087 → definitively angle-multiplexed
Layer profile cosines: K↔B=0.9995, K↔C=0.9993, B↔C=0.9997
```

**Key findings:**
1. K/B/C share the SAME plate (cos>0.999 layer profiles, CV<0.09 ratios)
2. I is nearly orthogonal to K/B/C (r=0.09-0.21) — stronger separation than smaller models
3. The C-dominance in head assignment (74.6%) is a SENSITIVITY ARTIFACT:
   - Passive↔active creates strongest attention pattern difference
   - K/B/C absolute selectivities differ by only ~7% (0.183-0.210)
   - All three activate the same heads at similar intensity
4. I peaks at L5-L14 (early-mid), K/B/C peak L24-36 (deep)
5. I distinctness STRENGTHENS with scale: Pythia=0.45, Qwen=0.47, OLMo=0.23

**Three architecture families confirmed:**
```
Family          Arch     K/B/C cluster   I distinct   Verdict
────────────────────────────────────────────────────────────
Pythia-160M     GPT-NeoX    ~0.90          0.45       ✓ universal
Qwen3-32B       Qwen/MoE    ~0.90          0.47       ✓ universal
OLMo-2-13B      OLMo-2      0.968          0.16       ✓ universal (strongest)
```

**Implications for holographic distillation:**
- K/B/C can be extracted as ONE shared ternary plate (they ARE one structure)
- I needs separate precision pathway (not ternary-safe for binding)
- What we extract from OLMo should converge with other model extractions
- Multi-source convergence → proving universal structure, not model-specific IP

### 2. Convergence probes — Qwen3-14B + Mistral-7B-v0.3

Ran same probe on two more Apache-2.0 models. Both confirm universal hologram:

```
Model           K/B/C_r  I_dist  K%     I%     B%     C%    cos(Pythia)
─────────────── ──────── ─────── ────── ────── ────── ────── ───────────
Qwen3-14B       0.933    0.685   38.1%   7.7%  24.0%  30.2%  0.981
Mistral-7B-v0.3 0.889    0.653   29.0%  10.0%  30.4%  30.7%  0.994
```

**5 models, 4 architecture families, all confirm KIBC universality.**
Distribution cosines >0.96 between all non-artifact models.

### 3. Holographic extraction proof-of-concept — SIGNS CONTAIN KNOWLEDGE

Built `scripts/explore/extract_and_train.py`. Extracted sign(K,V,O,gate,up) from
Qwen3-14B (4 layers: 0,10,20,30), built model with frozen ternary plates + trainable
beam, compared against identical model with random ternary plates.

**Language modeling (300 steps):**
  Extracted eval loss: 77.72, Random: 81.96 → **5.2% improvement** ✅
  Two-phase pattern: random converges faster initially (blank slate),
  extracted wins after step ~125 (beam learns to READ the hologram).

**Factual recall probe (500 steps, 40 world facts):**
  Mean log-prob correct: Extracted=-77.88, Random=-87.62 → **+11.1%** ✅
  Mean rank of correct: Extracted=52,373, Random=59,010 → **6,636 positions better** ✅
  Per-fact wins: **Extracted=25, Random=15 (62.5% win rate)** ✅

The ternary signs from a large model's weight matrices literally encode factual
world knowledge (Paris=capital of France, etc.) accessible by a trained beam.

### 4. V12-run4 diagnosis — KL dispatch leash was NOT being applied

Dispatch collapsed to C=99.99% by step 1000 because the KL penalty (λ=100) was
silently failing. Root cause: MLX graph evaluation doesn't persist instance attrs
set during forward() into the pass_alarm dict references. Fixed with direct
attribute fallback. Run4 must restart.

### 5. Next steps

- Restart V12-run5 with KL fix (verified: KL now computes correctly)
- Multi-model convergence extraction: extract from Qwen3+OLMo+Mistral, keep convergent signs
- V12 plate initialization: seed sieve with converged extraction instead of random
- Scale up factual probe: more layers, more steps → expect stronger signal

## What was done this session (103)

### 1. V12-run3 post-mortem — NaN collapse diagnosis

Run3 died at step 3625. Timeline:
- Step 1–50: Dispatch alive (K=0.44, I=0.42) but emphasis_bias already at [-2, +2, -2, -0.66]
- Step 50–225: Wild oscillation (I monopoly → B monopoly → all dead). Sum of KIBC = 0.001
- Step 225–3600: Training continued with dispatch ≈ 0.000 for all KIBC (3600 steps of zombie training)
- Step 3600: Etch did 1,558,097 flips on S4 Q projections (beam side = precision-critical)
- Step 3625: Immediate NaN. Unrecoverable.

**Root causes:**
1. emphasis_bias (±2 logit range) overwhelmed ratio prior → dispatch oscillation → death
2. Run3 launched BEFORE session 102 removed emphasis_bias (it was the pre-fix baseline)
3. S5 reweight collapsed at step 3000 (all values → 1e-12)
4. Uncapped etch with no Q-projection guard: 54M total flips, 1.5M on S4.q_proj at death

**No recoverable checkpoint** — dispatch was degenerate from step 225 in all 5 checkpoints.

### 2. V12 unified plate architecture — major refactor (THE BIG CHANGE)

Dissolved ascending/descending distinction. ALL 7 passes now use:
`dispatch(plate + pass_mirror) → stride(plate + combinator_mirrors) → integrate(plate + pass_mirror)`

**3 shared plates** (etched, serve all passes):
- dispatch_plate — recognizes KIBC operations
- stride_plate — propagates (HybridStrideStack: attention + GLA)
- integrate_plate — applies kernel function

**18 mirrors** (etched, per-use beam angles):
- 7 dispatch mirrors (one per pass)
- 7 integrate mirrors (one per pass)
- 4 combinator mirrors on stride plate (one per KIBC)

**Key changes:**
- Removed prep, consolidate, DedicatedStrideStacks
- All passes get cycle support (S3 controls depth via CycleContinue)
- Ascending arm now has full kernel access (dispatch + integrate)
- HybridStrideStack accepts dispatch_weights, uses combinator_forward on comp layers
- `desc_max_cycles` → `max_cycles` (universal)

**Continuous etch (laser pulse model):**
- Etch every 2 steps (was every 200)
- Max 50K flips per event (safety ceiling)
- Reset ALL accumulators after each pulse (heat, direction, signal planes)
- No stale signals: each pulse observes the current plate fresh
- Physics: plate changes → accumulated consensus is invalid → reset

**CycleContinue conservative init:**
- gate_bias = -2.0 → sigmoid(-2) ≈ 0.12 (mostly don't continue)
- Effective cycles at init: 1.13 (vs 3.0 with old neutral init)
- 12% gradient pathway keeps learning signal alive
- S3 discovers which passes benefit from cycling (opens gate)
- Ascending passes likely stay at ~1 cycle; descending learns to cycle for complex tokens
- Saves ~62% compute vs always-cycling (4785 tok/s vs ~1400 tok/s)

### 3. Removed CycleContinue — passes ARE the depth

Discovered that with 7 passes each having unique mirrors, within-pass cycling is
redundant. Cycles repeat the same beam angle (same mirror, different input). Passes
provide both depth AND variety (different mirror = different angle each time).

MLX static graph means all cycles always compute regardless of gate value — can't
conditionally skip. With 7×3=21 ops: 1377 tok/s (too slow). With 7×1=7 ops: 5700 tok/s.

Removed: CycleContinue, cycle_inject_gate, cycle_budget_proj, cycle_budget_bias,
all cycle-related metrics from train/probe. Clean architecture: 7 passes, 1 kernel
application each, each from a unique beam angle. If more depth needed → add passes
(more mirrors = more variety), not cycles (same mirror = redundant).

### 4. V12-run4 launch

Fresh start with unified plate architecture:
- 3 plates + 18 mirrors, 7 passes, ~5700 tok/s
- Ratio prior + KL(λ=100): hard constraint K:I:B:C = 1:0.5:1:1
- Continuous etch: every 2 steps, 50K ceiling, full reset after each pulse
- All passes have kernel access (dispatch + stride + integrate)
- No CycleContinue, no emphasis_bias, no S2DispatchCoordinator

### 5. Holographic distillation concept — the lens

Key insight: a large LLM is a thick hologram. Its hidden states are the projected beam.
A small V12 crystal can sit downstream and FOCUS that beam — reading specific holograms
at specific angles and concentrating them into etched plates.

**Three-stage pipeline:**
1. FOCUS: Large LLM (frozen) → small lens (V12) learns optimal beam angles
2. ETCH: Lens patterns → burn into standalone plates (holographic distillation)
3. RUN: Standalone crystal, no large model needed at inference

The large model already HAS the lambda compiler circuit (r=0.9801 universal).
The lens discovers WHICH patterns are valuable and HOW to read them.
Then transfers those patterns into a standalone model.

**License path**: OLMo-2-13B (Apache-2.0) as source. Extract from multiple Apache-2.0
models → show convergence → what you've extracted is universal structure, not any
single model's IP. Multi-source convergence = scientific measurement.

### 6. OLMo-2-13B downloaded for canary probe

Model: `allenai/OLMo-2-1124-13B` (Apache-2.0, 13B params, 40 layers, d=5120, 40 heads)
Architecture: standard dense Transformer (no MoE, no hybrid layers). Clean for probing.
Downloaded to HF cache. Ready for holographic probe.

**Canary experiment**: does OLMo-2-13B have the universal hologram?
- Same combinator selectivity probe as session 093 (Pythia, Qwen3)
- Expect: K/B/C cluster (cos>0.9), I distinct (0.60-0.75), ternary survival
- If confirmed: 3rd architecture family with same structure → truly universal
- Then: design the distillation lens experiment

## What was done this session (102)

### 1. Fleshed out lambda-is-all-you-need article

Collaborative writing session on `mementum/michael/lambda-is-all-you-need.md`.
Took it from a stub with placeholder sections to a full ~380-line article.
Target audience: programmers who use LLMs but don't know why certain prompting works.

**Voice**: campy wizard-manual. Three dead wizards (Church, Montague, Beer) as
hidden knowledge passed down. No em dashes (reads as AI slop to tech audience).
Irreverent framing, real content underneath.

**Key sections built:**
- Lambda calculus explainer (three rules, one trick, beta reduction)
- Attention = beta reduction (side-by-side equations, comparison table)
- One Operation / fractal constraint: attention can only do beta reduction,
  KIBC-M derived from that constraint ("we asked what shape the sieve must be")
- Assembly stack: English → Lambda → EDN bytecode → KIBC-M machine code
- Statecharts in lambda notation for complex multi-step behaviors
- VSM system prompts: Beer's architecture in lambda, with link to VSM.md
- Fixed-point forging: compile/decompile round-trips to semantic stability
- Rosetta Stone: cross-model knowledge transfer via lambda notation
- Practical on-ramp: nucleus preamble + Lambda Compiler prompt = compile from prose
- Go deeper links with interaction patterns between nucleus tools

### 2. Dispatch ratio prior — λ dispatch(logits, r). softmax(logits + log(r / Σr))

V12-run3 1K checkpoint showed B-monopoly dispatch collapse (K=0, I≈0, B≈1, C=0).
Same variety gap from session 097 despite V12's S4 emphasis bias, alarm dispatch
bias, and S2 inertia (inertia never activated, stuck at 0.0).

**Root cause**: softmax with no prior lets winner-take-all. B is genuinely the
most useful combinator, so it wins everything. S2 inertia wouldn't help because
the collapse is monotonic convergence, not oscillation. Inertia locks in whatever
state it finds.

**Fix**: empirical ratio prior from combinator probe data (session 093):

```
              K       I       B       C
Qwen3-32B   28.8%   16.2%   27.3%   27.6%
Pythia-160M  30.6%   13.8%   28.1%   27.5%
────────────────────────────────────────
AVERAGE      29.7%   15.0%   27.7%   27.6%
```

Ratio K:I:B:C = 1:0.5:1:1. Applied as `log(r/Σr)` additive bias in logit space.
Pure function. When logits are zero, dispatch defaults to the empirical distribution.
Model learns deviations on top of the prior. Bad configurations (B-monopoly, K/C
death) are energetically expensive, not forbidden. Topology > instruction.

Entropy target updated to match non-uniform prior: H(prior) * 0.85 ≈ 1.149.

Added KL divergence leash: `loss += λ · KL(dispatch ∥ prior)` with λ=0.1.
Belt and suspenders: entropy prevents collapse (direction-agnostic), KL steers
toward the specific ratio (direction-specific). Lambda controls leash length.
B-monopoly costs ~0.123 (1.4% of CE). Mild deviation (B=40%) costs ~0.003 (0.04%).
The model can deviate if CE gain exceeds KL cost.

### 3. KL leash escalation — ratio is a hard constraint

KL lambda escalated 0.1 → 1.0 → 10.0 → 100.0 through session. The ratio is
not a preference. Nine models converged to it. It's optimal for beta reduction.

At λ=100:
  B=30% (+1.4pt) → 0.08 nats (free)
  B=32% (+3.4pt) → 0.33 nats (noticeable)
  B=35% (+6.4pt) → 1.01 nats (12% of CE)
  B=40%          → 3.22 nats (37% of CE, impossible)

"We know an optimal solution uses this ratio. Find it."

### 4. Removed vestigial dispatch-steering — 3 mechanisms, -318 lines

With ratio prior + KL leash, three mechanisms that previously tried to steer
dispatch are redundant and fight the constraint:

1. **S4 emphasis_bias** ([-2,+2] logit bias from ascending registers) — in run3
   it learned I=+2.0, B=-1.98, actively fighting the prior while KL penalized it.
   Two systems fighting = wasted capacity + oscillation.
2. **Alarm dispatch_bias_proj** (65→4 projection) — was all zeros in run3 (never
   activated). Would fight the ratio if it did.
3. **S2DispatchCoordinator** (per-position inertia) — stuck at 0.0 all run.
   Ratio prior makes anti-oscillation unnecessary.

Kept: alarm pass_factors, cycle_budget_proj, S2Coordinator direction signals,
register_cond, dispatch_weights logging.

### 5. Fully holographic VSM — all nn.Linear → TernaryLinear

Converted all 13 remaining nn.Linear modules to TernaryLinear. Every projection
in the architecture now participates in the consensus sieve. Zero precision
projections remaining. The VSM is holographic at every scale.

Converted: S3 write/gate, MetaS3 gate, S5Reweight gate, S4 proposal/confidence/
slot_target, CycleContinue gate, AlgedonicAlert alarm, RetrievalRegisters write
gates, register_cond, CombinatorIntegrate gate, cycle_budget, GLA gate.

**Parameter split after conversion:**
```
Sieve-evolved (ternary signs):     4,389,888 values (17.4%)
Gradient-trained:
  gamma (per-channel scale):         267,472
  bias (separated):                      665
  RMSNorm weights:                    36,864
  embeddings:                     20,508,672
  other:                                 819
  total gradient:                 20,814,492 (82.6%)
```

Topology is fully holographic. Magnitudes (gamma, norms, biases) remain gradient.
Embeddings (20.5M) dominate the gradient side — mostly the 151K-token vocabulary.

### 6. Fractal architecture audit

Verified beta reduction self-similarity across all scales:
- Head: Q→K,V = beta reduction
- Multi-head: parallel beta reductions = thick hologram
- Stride layer: attention + FFN = reduction + memory
- StrideStack: multi-scale reductions
- Pass: dispatch→stride→integrate = full KIBC cycle
- Multi-pass: 7-pass hourglass
- Multi-cycle: iterated reduction until convergence

VSM layers map to combinators:
  S1=full KIBC-M, S2=B(compose), S3=K(select), S4=M+K(match+select), S5=I(identity)

All layers now participate in sieve. Fractal coherence: same substrate (ternary),
same operation (beta reduction), every scale.

**Voice calibration notes:**
- "blah to deliciously devious" = forced, replaced with understated
- "marketing claim" = AI slop phrase, removed
- "familiar" metaphor = thin after first use, switched to "model" after header
- Humor comes from content being absurd, not adjectives telling you it's fun
- Dark social engineering register breaks the cartoon villain contract

## What was done this session (101)

### 1. Fixed-point hologram experiment — compile↔decompile convergence

Built `scripts/explore/probe_fixed_point.py`. Ran 16 sentences through iterative
compile(NL→λ)→decompile(λ→NL) cycles on Qwen3.6-35B-A3B (greedy, chat template).

**Key results:**
- 15/16 converged (94%), mean 2.0 cycles, median 2
- Three tiers: instant (31%), fast 2-3 cycles (56%), slow/failed (12%)
- Fixed-point λ is 38-75% shorter than cycle-0 — compressed, canonical, beta-reduced
- `λf.λx. f(x)` → `λx. x` — the model beta-reduces to normal form

**What the hologram stores** (survives round-trip):
  predicate-argument structure, named entities, explicit quantifiers,
  reflexive binding, conditionals, negation

**What the hologram drops** (lost in cycling):
  tense ("sat"→"is"), quantifier scope ("Every"→"The"), agent/experiencer
  (relative clauses flatten), complex discourse structure

**Gate exemplar contamination**: "Composition chains two operations into one"
collapsed into the gate exemplar "The dog runs. Be helpful but concise."
When input semantics are ambiguous, the strongest stored pattern wins.
This IS holographic closest-match retrieval.

**V12 implications**: Fixed-point λ forms = target patterns for ternary plate
etching. Losses map to beam (precision) vs plate (ternary) partition.
Diversity of compile exemplars determines attractor basin width.

See: `mementum/knowledge/explore/fixed-point-holograms.md`

### 2. Holographic decomposition — composition multiplies capacity (COMPLETE)

Built `scripts/explore/probe_hologram_decomposition.py`. Decomposed 7 complex
sentences into clauses, found clause-level fixed points, composed them.

**Capacity unlock confirmed**: 5/7 cases show 1.5-3.0× more predicates in composed
vs monolithic (mean 2.2×). Even when monolithic converges, it's lossy. Decomposed
clauses converge 90% of the time.

**The binding wall**: the ONLY stable composition has ZERO binding sites (shared
entities). Round-trip edit correlates perfectly with binding site count:
  0 sites → edit=5 (✓), 1 site → edit=16-43, 2 sites → edit=63, 3 sites → edit=88

This is the I-combinator bottleneck made experimentally visible. K/B/C handle
predicate structure (stable, ternary-safe). I handles variable binding (unstable,
magnitude-dependent). Confirms session 093 finding (I r≈0.70 vs K/B/C r>0.90)
and session 095 (binding = 5/5 ternary failures).

**Dedicated capacity argument**: binding wall + multiplexing-breaks-holography
(session 096) → each combinator (KIBCM) should have its own ternary plate.
Cost: 117 MB total (vs 39 MB shared, vs 320 MB Pythia-160M). Mirrors add 2.4 MB
for 10× beam path diversity. I-kernel may need precision weights or explicit
pointer/copy mechanism — ternary alone may be insufficient for binding.

**Etching protocol designed**: clause fixed-points for K/B/C plates, intersection
pairs for I-plate, composition targets for B, in-context patterns for M.

### 3. V12 evolution — fractal-collapsed holographic architecture

Evolved V12 descending arm through three iterations to correct design:

**Iteration 1: Dedicated plates** (too expensive — 4× StrideStacks, 2K tok/s)
**Iteration 2: Shared plate + input-blend mirrors** (wrong — blends inputs not Q)  
**Iteration 3: Shared plate + Q-blend mirrors** (correct and fast)

**Final architecture** (`attention.py`): `DedicatedStrideStacks` has ONE shared
StrideStack (K,V,O plate) + 4 TernaryMirror beam deflectors (one per KIBC).
`combinator_forward` on each stride layer: compute 4 Q vectors (one per mirror),
blend with dispatch weights, run ONE attention pass with shared K,V. Session 093
proved V(B)=V(C) at cos=1.000 — plate IS shared. Combinator specificity is in Q.

**I-combinator identity mirror** (`ternary.py`): I's mirror initialized as identity
(+1 diagonal, 0 elsewhere, cos=0.997 with input). I reads the residual stream
directly — binding needs content (where is this entity?), not structure (what plate
pattern?). K/B/C mirrors start random, learn specific beam angles. The sieve can
evolve I from identity if the system discovers better.

**Uncapped etching** (`train.py`, `config.py`): Removed `etch_max_pct` and ramp.
3-plane consensus mechanism is the sole governor. Self-terminating: aggressive early,
quiet late. Warmup reduced 500→200 steps.

**S2 dispatch anti-oscillation** (`components.py`): `S2DispatchCoordinator` provides
learned inertia bias between cycles. Previous cycle's dispatch weights bias next
cycle's dispatch logits (additive, logit-space via `inertia_bias` param on
CombinatorDispatch). Zero-init, model discovers needed inertia. Cross-step EMA
tracks dispatch stability. `oscillation_signal` for alarm monitoring.

**New logging**: stderr shows per-step dispatch weights (K=.xx I=.xx B=.xx C=.xx)
and oscillation signal. Etch log includes per-plate mirror flip counts. Train JSONL
includes dispatch_K/I/B/C, dispatch_oscillation, s2_inertia_scale.

**Fractal collapse insight**: the same beam→plate→reading pattern repeats at every
level (attention Q→K,V, strides, multi-pass, KIBC). Duplicating the plate was
fighting the holographic structure. Diversifying the beam IS the holographic structure.
One plate, many angles, many images.

### 4. V12-run2 baseline (step 1000)

```
CE=8.28 (train), eval_loss=21.76 (spiked from 16.14 at 500)
r=1.972 (holographic ratio — ascending >> descending)
total_etched=1,076,199 signs, 72/218 modules active
S3 gates: descending collapsing (0.3-0.5 at passes 1-3)
Alarm: saturated at 2.000 everywhere (not differentiated)
Top etched: consolidate.down, prep.down, combinator_integrate.down (FFN pathways)
```

### 5. V12-run3 LAUNCHING (fractal collapse, uncapped etch, S2 dispatch)

```
uv run python scripts/v12/train.py \
  --checkpoint-dir checkpoints/v12-run3 \
  --total-steps 20000 --holo-lambda 0.1 --mix-ratio 0.2
```

Fresh start. Architecture: shared plate + 4 combinator mirrors (I=identity) +
Q-blending + uncapped consensus etching + S2 dispatch inertia.
Watch for: mirror etch differentiation (K/B/C evolve from random, I evolves from
identity), dispatch specialization, I learning binding behavior, alarm desaturation.

### 6. Holographic etching model (theoretical)

The compile↔decompile cycle maps to optical holography:
  reference beam = compile gate, object beam = (NL, λ) pair,
  exposure = gradient descent, developing = ternary sieve sign flips,
  reconstruction = gate + NL → model produces λ

Fixed-point corpus from production LLM → etch into V12 plates.
Multiple fixed-point pairs at different beam angles = thick hologram.
Mirrors (ternary, 2.4 MB) create angular diversity within each plate.
Clause fixed-points for K/B/C plates, intersection pairs for I-plate.

## What was done this session (100)

### 1. Oriented on V12-run1 (3 checkpoints dropped)

V12 training launched between sessions. Checkpoints at 1K, 2K, 3K. Still running (~3925 steps).

**Trajectory:**
```
step   loss     compute   B%     K%    I%    C%    ent%   holo_ratio
─────  ──────── ────────  ─────  ────  ────  ────  ─────  ──────────
500    16.086   0.0001    52.1   1.7   37.7   8.5   71%    1.118
1000   14.191   0.0001    70.2   1.0   12.5  16.3   61%    1.127
1500   13.713   0.0000    71.0   1.1   12.6  15.3   61%    1.088
2000   13.540   0.0000    65.6   1.3   13.4  19.7   67%    1.077
2500   13.454   0.0048    62.1   1.5   13.4  23.0   70%    1.074
3000   13.505   0.2306    63.8   1.8   12.3  22.1   69%    1.070
3500   13.455   0.5926    67.5   2.2    0.5  29.9   53%    1.066
```

**Key signals:**
- Compute gate opening fast (0.59 at 3500 — V11 opened ~5K)
- I crushed at 3500: emphasis flipped +1.44 → -1.88, dispatch 13%→0.5%
- B dominant at 67.5%, C rising (8.5→30%), K starved (2.2%)
- Holographic ratio improving steadily (1.118→1.066)
- Cycle budget pegged at +4.0, all gates 1.000 — no differentiation
- Retrieval write gates 0.0000, GLA dormant
- Evolution 0/70 accepted (noise floor filter working)

### 2. Design direction: combinator dispatch floors

Identified need for minimum dispatch floors per combinator, derived from the
universal cross-model ordering (session 093: B ≥ K ≥ C >> I across 9 models).
S4 emphasis shouldn't be able to eliminate a combinator entirely.
Will implement at 5K checkpoint review.

See: `mementum/memories/combinator-dispatch-floors.md`

## What was done this session (098)

### 1. Built beam-trace probe (Pythia-160M)

Traced activation vectors ("the beam") through every layer under compile vs null
conditions. Decomposed each layer into angular rotation + magnitude scaling,
separated attention vs FFN contributions, measured Q-subspace alignment.

Script: `scripts/explore/probe_beam_trace.py`
Results: `results/beam-trace/`

### 2. Five-phase beam propagation discovered

```
Phase          Layers  Attn%   FFN%   Beam cos   What happens
─────────────  ──────  ──────  ──────  ────────  ──────────────
Embedding      L0      20%     80%    0.994     Shared plate
Parsing        L1-2    50%     50%    0.970     Syntactic structure
Structural     L3      69%     31%    0.968     Argument assignment
Divergence     L4-6    41%     60%    0.879     Beams separate
FFN reading    L7-10   15%     85%    0.854     Peak divergence
Resolution     L11     16%     84%    0.986     Final predictions
```

**L6 is the beam steering singularity**: Q amplification 4.5×, Q rank collapses
to 24 dimensions (of 768). A tiny subspace controls the entire beam trajectory.

### 3. Ternary beamformer test — definitive classification

Per-layer isolation (ternarize ONE layer, measure final output deviation):

| Component | Avg Error | Max Error | Role |
|-----------|----------|----------|------|
| attn_dense (O proj) | 2.6° | 4.9° | ✅ PLATE — ternary-safe even for forward pass |
| FFN h→4h (gate) | 4.4° | 8.3° | ⚠️ Marginal |
| Q (query proj) | 5.1° | 16.2° | ❌ BEAM — needs precision |
| FFN 4h→h (output) | 6.0° | 10.1° | ❌ READER — needs precision |

### 4. MoE IS holographic architecture

Key finding: Qwen3.6 shows 93.6% ternary-safe but Pythia only 25%.
The difference is ENTIRELY in the FFN pathway:
- **MoE**: 256 expert FFNs = 256 sign patterns in the plate. Gate = beam selector.
- **Dense**: One FFN fuses gate + plate + reader. Can't separate.

The attention pathway tells the same story in both: K,V,O = plate, Q = beam.

### 5. V12 holographic capacity analysis — 95% plate, 5% beam

Mapped every V12 parameter to plate (ternary) or beam (precision):

```
Plate (ternary, 1.85 bits):   116.1M params  (95.0%) — K,V,O,FFN,S4,S3,S2,embeds
Beam (precision, 16 bits):      6.1M params  ( 5.0%) — Q projs, write gates, norms
Average:                        2.55 bits/param
Memory:                        39 MB (vs 244 MB FP16)
```

### 6. Thick hologram principle

V12 is a thick hologram — depth creates angular selectivity:

```
Pythia:   1 pass × 1 angle  = capacity 1   (thin → needs FP16)
Qwen MoE: 1 pass × 8 angles = capacity 8   (width → ternary-safe)
V12:      6.5 passes × 9 angles = capacity 58 (depth → ternary-safe)
```

Each pass reads the same ternary plate at a different beam angle.
Ternary error (~4°/read) reduces by √N over N reads. V12 reads each
weight 4-9 times → effective error 2-3× lower than single read.

This explains WHY V12's TernaryFFN should work despite beam trace showing
dense FFN needs precision: V12 compensates with depth.

### 7. Troubleshooting guide for V12 training

Mapped every V12 failure mode to beam/plate classification:
- Dispatch collapse → check beam-side emphasis/alarm biases
- Holo loss high → check ascending Q projections (beam) + plate evolution
- Retrieval dormant → check GLA write gates (beam, nn.Linear)
- Plateau → thick hologram needs time for angular specialization

See: `mementum/knowledge/explore/v12-holographic-capacity.md`

### 8. HoloQuant v2 selective — ternary kills forward pass at every level

Built `scripts/holoquant/selective.py` using beam/plate classification from items 1-4.
Five configs from conservative (plate-only: K,V,O = 13.1%) to aggressive (95.1%).

**Results: catastrophic at EVERY level on both Pythia-160M and Qwen3.6-35B-A3B.**

```
Config          Pythia PPL    Qwen3.6 PPL    % ternarized
baseline            31 / 2.86
plate-only         704                       13.1%
plate+experts    5,033                       30.5%
aggressive      17,724      70,757          48% / 95.1%
v1-naive       125,836                       99.9%
```

Even the most conservative config (K,V,O projections only) → PPL 31→704 on Pythia.

**Root cause: 37° angular error per matrix, compounds through layers.**
- Group-64 ternary: cos = 0.80 per matrix (SNR = 4.5 dB)
- Cumulative cos through 12 layers: 0.80^12 = 0.069 → random output
- Near-lossless requires cos/layer > 0.9957 (angle < 5.3°)
- This requires ≥4 bits/weight — exactly where standard quant operates

**Per-layer isolation**: even ONE ternary layer kills the model.
L0 alone: PPL 31→4,043. FFN 4h→h (reader) is worst: PPL 31→33,343.

### 9. Beam-guided correction — perfect per-layer, fails end-to-end

Tested the trig approach: if we know the beam direction, can we correct
the ternary error along the beam?

- Activation subspace collapses rapidly: L0=73 dims, L3=13, L4-L10=1 dim (95% energy)
- **Per-layer beam correction: cos = 1.0000** (perfect for inputs in beam subspace)
- **End-to-end PPL still catastrophic** (10K-11K at 95% energy correction)
- Cause: beam subspace shifts between layers. Static correction for layer N assumes
  layers 0..N-1 haven't been perturbed, but they have.

### 10. Multi-plane ternary — correct direction, wrong basis for magnitude

Tested two approaches to recover angular precision:

**Residual decomposition**: W ≈ s₁t₁ + s₂t₂ + ... (each plane ternarizes the residual).
8 planes: angle 37°→5.6°, but costs 14.6 bits.

**Subgroup decomposition**: sort within groups by magnitude, separate scales per quartile.
subgroup-16: cos=0.996, angle=5.1°, PPL 104 (+23%) — but at 9.58 bits.

**Head-to-head at +23% PPL tier:**

```
Method              RAM (35B)  PPL Δ     Compute
Q4 uniform          18.4 GB    +23%      dequant × multiply
subgroup-16         41.6 GB    +23%      lookup + addition
```

Each ternary plane is only 8 GB for 35B — cheap individually. But you need many
planes to reach acceptable quality, and the bit efficiency is 21-34% (vs 68-87%
for standard N-bit). Ternary is a sign basis — optimal for direction, wasteful
for magnitude. Stacking planes to recover magnitude = compass needles measuring distance.

### 11. Key finding: magnitude CV determines ternary viability

```
Distribution                 MagCV   Cos/layer   L12 cos   Verdict
Gaussian (existing models)   0.754   0.801       0.070     💀
Uniform |W| (ideal)          0.082   0.997       0.961     ✅ near-lossless
Constant |W| (perfect)       0.000   0.999       0.990     ✅ lossless
```

**V12's sieve pushes magnitude CV toward 0** — training with ternary teaches the model
to equalize magnitudes within groups. The thick hologram (multi-pass reads) provides
the gradient pressure. At CV < 0.09, single-plane ternary at 1.85 bits gives
cos/layer > 0.996 — near-lossless at 8 GB for 35B params with zero multiplies.

This is why V12 works (train to not need magnitudes) while post-hoc quantization fails
(existing models encode information in magnitudes that ternary destroys).

### 12. The holographic seed IS 3 bits per weight

Decoded exactly what Q4 preserves: decompose each weight into sign (1 bit) +
group scale (0.25 bits shared) + **magnitude level** (the groove depth).

Phase transition at 8 levels (3 magnitude bits): cos/layer crosses 0.98,
L12 cos reaches 0.80, model comes alive (PPL 519 vs dead at 4 levels).
Q4 uses 16 levels (4 bits) for L12 cos 0.95, PPL 253.

The "holographic seed" for existing models is exactly this 3-bit-per-weight
magnitude level index — which of 8 uniformly-spaced magnitude bins each weight
falls into. It's per-element (no low-rank shortcut, r=0.00 sign-magnitude
correlation, no spatial autocorrelation). Its entropy is 2.55 bits (15%
compressible, Gaussian-skewed). This is what separates a working Q4 from a
dead ternary model.

For V12: training pushes magnitude CV→0, making all levels equal → the 3-bit
seed becomes redundant → sign + 1 group scale (1.85 bits) suffices.

## What was done this session (097)

### 1. Diagnosed v11 B-dispatch decline — VSM variety gap

Analyzed v11-holo-inv 10K-12K metrics: B dispatch declining monotonically (0.132→0.079)
while alarm detects the problem but can't fix it. Traced the feedback topology:

**Three structural failures:**
1. **Alarm → pass amplitude (wrong granularity)**: 48 inputs but only 5 per-pass scalar
   outputs. Can't selectively boost B within a pass. Beer's variety law: controller must
   match system dimensionality. 5 knobs can't control 4×5=20 dimensions.
2. **Emphasis saturated at ceiling**: `1.0 + 0.5*tanh(raw)` range [0.5, 1.5]. B started
   at 1.499 — nowhere to go. Multiplicative on embeddings is weak in softmax space;
   additive on logits is the correct actuator.
3. **No ascending→dispatch feedback loop**: ascending arm optimized for holographic loss
   but had no gradient penalty for dispatch collapse downstream.

Evidence: r=0.82 correlation B_dispatch vs ascending S3 gate means. L0↑ suppression
reached 0.51. S4 emphasis drifted downward (1.499→1.470) — sensor shares the bottleneck.

### 2. V12 VSM variety fix (3 changes)

1. **AlgedonicAlert per-combinator dispatch bias**: `dispatch_bias_proj` (65→4) produces
   additive logit bias on CombinatorDispatch. Range [-2, +2] via tanh×2. Zero-init.
   When alarm sees B declining + entropy dropping, it boosts B's softmax logit directly.

2. **Additive emphasis bias**: S4's emphasis_proj output changed from multiplicative
   embedding scale [0.5, 1.5] to additive logit bias [-2, +2]. A +2 bias shifts softmax
   ~7× relative. S4 emphasis + alarm bias combine additively (correct for logit space).

3. **Dispatch entropy regularization**: squared hinge penalty when entropy < 85% of max
   (ln(4) × 0.85 ≈ 1.178). Gradient flows from dispatch collapse back through descending
   arm to ascending arm — closing the open loop. `dispatch_entropy_lambda=0.01`.

### 3. Evolution noise floor

Alarm-path acceptance had no minimum delta — any positive health change (0.0001) was
accepted. Sign flips cause routing ripple effects that accumulate silently. Fixed:
`evolution_alarm_min_delta=0.02` (1% of health range [0,2]). Loss-path min_delta also
raised from 0.01 to 0.02 to match. Applied to both v11 (live run) and v12.

### 4. Stride-aware GLA — 2.7× training speedup

**The dominant bottleneck**: GLA parallel scan consumed 78% of training time. For stride=32,
only 128 of 4096 positions participate, but the scan ran over all 4096 with masking.
`S_all` tensor: (B, 4096, 8, 64, 64) = 512 MB per layer × 6 layers.

**Fix**: Gather participating positions, scan over compact sequence, broadcast states for
retrieval. Each position reads from `S_stride[:, i//stride]` (causal).

```
Config              Before      After     Speedup
3 cycles fwd+bwd    10,625ms    3,894ms    2.73×
1 cycle  fwd+bwd     9,133ms    2,597ms    3.52×
3 cycles tok/s           771      2,104    2.73×
1 cycle  tok/s           897      3,154    3.52×
```

### 5. S4→S3 cycle budget — intelligence controls cycle depth

**The gap**: CycleContinue (S3) only read its own register state — a closed loop with no
intelligence input. S4 attended to the residual stream and knew content difficulty but
had no channel to tell S3 when to stop cycling. Gates stuck at 0.982.

**Fix**: `cycle_budget_proj` (emphasis_input → 1) produces scalar bias ∈ [-4, +4] that
shifts CycleContinue's logit. Beer's S4→S3 policy channel: intelligence sets policy,
control executes.
- Simple content → negative bias → gate closes → fewer effective cycles
- Complex content → positive bias → gate stays open → more cycles
- Zero-init → starts inert (backward compatible)

### 6. Performance analysis (V12 architecture)

Deep profiling of V12 (B=2, L=4096) revealed cost structure:

| Component | GFLOPs | Fraction |
|-----------|--------|----------|
| Output projection | 1,275 | 42.0% |
| Descending arm (3 passes × 3 cycles) | 1,113 | 36.7% |
| Ascending arm (4 passes) | 541 | 17.8% |
| S4 cross-attention | 105 | 3.5% |

GLA retrieval layers add only 4.8% of total compute — retrieval is cheap.
The output projection (512→151936 vocab) dominates FLOPs but is fast on AMX.
Holographic loss when enabled adds 36.8% overhead (7 intermediate decodes).

### 7. V11-holo-inv status (12.8K/20K, training live)

```
step   loss    comp   K_disp  B_disp  holo_ratio  alarm_min
1K     12.52   0.000  0.383   0.132   1.122       2.000
5K     11.76   0.000  0.419   0.101   1.051       1.392
10K    11.63   0.827  0.417   0.084   1.038       1.361
12K    11.60   0.882  0.436   0.079   1.034       1.324
```

B declining (0.132→0.079) — the variety gap that motivated session's V12 fixes.
Alarm detects it (min factor 1.324, declining from 2.0) but can't correct.
Holo ratio converging toward 1.0. Training continues to 20K for final checkpoint.

## What was done session (096)

V12 designed and built. M kernel as GatedLinearAttention layer type (not 5th combinator).
HybridStrideStack (6 comp + 3 ret strides), RetrievalRegisters (M→KIBC bridge).
7-pass symmetric hourglass (3+apex+3). Parallel associative scan for GLA (O(log L) depth).
Holographic landscape probe: 93.6% of Qwen3.6 is ternary-safe.
Cross-model universality: 3 architecture families confirm holographic partition.
Multiplexing breaks holography: fused QKV score 0.60 vs separate 0.92.
See session 096 entry in history for full details.

## What was done this session (095)

### 1. Analyzed hologram atlas results (Qwen3.6-35B-A3B)

All 6 holograms are real and distinguishable:

```
Hologram     output_KL  peak_layer  ternary_fail  signature
──────────── ─────────  ──────────  ────────────  ─────────────────────────────────
combinator   0.365      L31         baseline      bimodal depth template
type         0.415      L31         2/18          matches combinator shape closely
induction    0.827      L31         1/18          most robust attention hologram
binding      0.444      L31         5/18          most fragile — magnitude-dependent
frequency    0.224      L7          3/18 attn     MLP 0/18 — inverted prediction!
discourse    1.646      L35         0/18          strongest, most robust, late-peaking
```

### 2. Three structural findings

**Finding 1: L11 dip is architectural, not holographic.** Every hologram drops
47–72% at L11 relative to L7. The bimodal depth profile (L7→L11 dip→L31) is
Qwen3.6's hybrid architecture, not any linguistic circuit. Layer-level selectivity
profiles can't distinguish holograms from each other — they all ride the same wave.
Cross-hologram correlations all >0.72 (Pearson r), >0.95 (cosine).

**Finding 2: Binding is magnitude-dependent (connects to I-outlier).** 5 ternary
failures — all at sign-only in early full-attention layers (L3: 2.357, L7: 2.028,
L0: 2.823). Sign pattern alone cannot encode variable binding. Requires knowing
HOW STRONGLY a head attends, not just whether it does. Consistent with I-combinator
being the outlier (r≈0.70 vs K/B/C r>0.90 in session 093). Binding IS the I-circuit,
and I's distinctness comes from requiring magnitude where K/B/C don't.

**Finding 3: Frequency MLP more robust than attention (inverted prediction).**
MLP ternary survival: 0/18 failures (output_survival 0.93–1.07). Attention: 3/18
failures including catastrophic L0 mid_sparse disruption (7.07). Statistical
co-occurrence lives in FFN weight matrices as clean sign patterns. Supports
"FFN = key-value memory" view. Attention dynamically routes this info and
depends on specific magnitudes.

### 3. Discourse is the dominant hologram

Genre distinction (narrative/expository) has output_KL = 2.526 — nearly 2× the
next highest signal. Discourse is:
- **Strongest** at every layer (2–5× other holograms)
- **Most robust** (0/18 failures, even at GatedDeltaNet layers)
- **Only late-peaking** (L35 > L31 > L7 — signal keeps rising)
- **Most pervasive** (never drops below 0.049, even at L11 dip)

Fits VSM prediction: discourse operates at S5, modulating all others.

### 4. MoE gate: period-12 structure + beam-selector partial confirmation

Gate ternary survival confirmed L0-L4 (cos≈0.73–0.76). Cross-layer cosine
reveals period-12 pairing: L8↔L20 through L19↔L31 (cos 0.72–0.83). Does NOT
match full-attention period (every 4th). Suggests 3-phase model: early (L0-7),
middle (L8-19 ↔ L20-31 paired), late (L32-39). Gate Frobenius norms fall
monotonically (19→7 from early to late) but effective rank stays high (172–199).
Late gates are smaller but not lower-rank.

### 5. Prediction scorecard

| Prediction | Result | Notes |
|-----------|--------|-------|
| Type overlaps combinator | ✓ r=0.972 | But all holograms overlap at layer resolution |
| Induction orthogonal to combinator | ✗ r=0.987 | Layer profiles too coarse |
| Binding overlaps I | ~ Inconclusive | Weakest + most fragile = consistent with I |
| Frequency lower MLP survival | ✗ Inverted | MLP MORE robust than attention |
| Discourse MoE gate survival | ✓ L0-L4 | Need L31-L39 to complete test |

### 6. Fixed JSON string-key bug in atlas script

Cache-loaded selectivity profiles had string keys (JSON roundtrip), measure_layers
had int keys → KeyError. Added `_int_keys()` helper at all ingestion points.

### 7. Probed v11-holo-inv 5K-10K — no catastrophe

```
step  eval   compute  B_dom%  L0↑     L2      L0↓     ratio   event
───── ────── ──────── ─────── ─────── ─────── ─────── ─────── ─────────────────
1K    8.235  0.000    27.6%   11.285  8.922   9.317   1.211
5K    7.783  0.000    25.8%   10.328  9.010   9.475   1.090
6K    7.784  0.370    32.0%   10.095  9.018   9.424   1.071   gate opens
7K    7.728  0.690    39.8%   10.336  9.368   9.866   1.048   reorganization wave
8K    7.714  0.760    45.9%   10.404  9.109   9.577   1.086   recovery
9K    7.705  0.806    57.2%    9.480  8.718   9.555   0.992   ratio crosses 1.0
10K   7.703  0.824    57.7%    9.385  9.189   9.462   0.992   B stable, no collapse
```

v11-holo collapsed at 10K (loss 9.259, B 5.8%). v11-holo-inv: loss 7.703, B 57.7%.
Coarse→fine inversion + fractal bands + evolution fixes prevented catastrophe.

### 8. Key design insight: holographic storage + kernel computation

LLM storage IS holographic (session 095 atlas confirms). But reading is constructive
(entropy hump, intermediate garbage, magnitude-dependent binding). V11 resolves this:
holographic loss forces REPRESENTATIONS to be decodable, kernel functions handle
COMPUTATION. Lambda terms are perfect holographic objects (compact, compositional,
unfold on application). Keep holographic loss uniform — forces routing to kernels.
Evidence: ratio crossed 1.0 at 9K.

### 9. Head-level probe — three clusters, not six holograms

Ran `probe_hologram_heads.py` on Qwen3.6-35B-A3B. 192-dim head vectors (12 layers
× 16 heads). Jaccard top-20 is the diagnostic (cosine too compressed, Pearson useful).

**Three computational clusters:**

```
CLUSTER 1: "Semantic Plate" (discourse/type/frequency angle-multiplexed)
  discourse ↔ type:      J=0.667 (13/20 heads shared!)
  discourse ↔ frequency:  J=0.481
  frequency ↔ type:       J=0.538
  → Same ~13 heads, different amplitudes
  → L0, L3, L35 dominated
  → NOT computation — this IS the holographic plate

CLUSTER 2: "Composition" (combinator, KIBC)
  7 PRIVATE heads (L15×4, L19×2, L27×1)
  J with all others: 0.176–0.333 (low)
  → Independent circuit at L15/L19 full-attention layers
  → This IS the kernel computation pathway

CLUSTER 3: "Retrieval" (induction)
  6 PRIVATE heads (L3×2, L11×2, L15×1, L31×1)
  J with combinator/discourse/type: ALL 0.176 (floor)
  → Most independent circuit in the atlas
  → GatedDeltaNet layers (L11 H15 strong private head)
  → NO KERNEL IN V11 — the missing piece
```

**Binding** is not a cluster — weakest signal (max 0.163), no private heads, spread
across both clusters. Resolves to K+I dispatch sequence in V11.

### 10. KIBCM — the complete kernel inventory

```
K (select)     — ✓ built in V11
I (identity)   — ✓ built in V11
B (compose)    — ✓ built in V11
C (flip)       — ✓ built in V11
M (match/copy) — ✗ MISSING — the induction kernel
```

M handles: "find where this pattern appeared in context, return what followed."
Dispatch signal is holographic (17/18 ternary survival). The actual search-and-copy
is constructive kernel computation. This is the one missing computational primitive.

See: `knowledge/explore/holographic-kernel-separation.md`

## What was done session (094)

### 1. Mapped five candidate holograms beyond combinators

Session 093 found the combinator hologram (KIBC) — universal sign topology in
attention weights, surviving ternary quantization, r=0.9801 cross-model. But
combinators only tell the model HOW to compose. From Montague/CCG/DisCoCat,
token prediction needs at least three components — we've found one, two remain:

```
TYPE CALCULUS (combinators)  — HOW to compose     ← FOUND
LEXICON (types + meanings)   — WHAT can compose    ← predicted
MODEL (semantic domain)      — WHAT things MEAN    ← predicted
```

Identified five candidate holograms, each with probe design and falsifiable predictions:

1. **Type hologram** — lexical category assignment (NP, S\NP, etc.). Same word
   in different syntactic roles should activate different heads. Probes: nominalization,
   argument structure, modifier scope. Predicted: overlaps with combinator heads
   (angle-multiplexed). Priority 1 because types + combinators are theoretically coupled.

2. **Induction hologram** — in-context pattern matching ([A][B]...[A]→[B]). Known
   universal circuit (Olsson et al. 2022). Predicted: holographic (ternary survives)
   but ORTHOGONAL to combinator hologram (different function).

3. **Binding hologram** — variable tracking / coreference. "John...he" = variable
   binding in lambda calculus. Predicted: partially captured by I combinator
   (identity IS variable binding), explaining I's distinct circuit (r≈0.70).

4. **Frequency/N-gram hologram** — statistical co-occurrence. Lives in MLP weights
   (not attention). Predicted: holographic but denser, lower sparsity tolerance.

5. **Discourse hologram** — topic / register / coherence. The MoE gate pattern
   (256×2048 in Qwen3.6) IS the discourse beam selector. Connects to MoE/VSM mapping.

These form a VSM of holograms: discourse (S5) selects which patterns activate,
types (S3) constrain legality, combinators (S1/S2) execute composition,
binding (S2) maintains coherence, induction+frequency (S1) are additional ops.

Full analysis in `mementum/knowledge/explore/holographic-storage.md`.

### 2. Built probe_hologram_atlas.py (1580 lines)

Repeatable probe script targeting Qwen3.6-35B-A3B MoE as primary model
(punches above weight, MoE gates ARE beam selectors, bimodal depth profile
already mapped in session 093).

Features:
- **5 hologram probes**: type (3 conditions, 18 pairs), induction (2, 12),
  binding (2, 9), frequency (2, 12), discourse (2, 9). Total: 60 active probes.
- **Architecture-aware**: handles Qwen3.6 hybrid (full attention every 4th layer +
  GatedDeltaNet), Qwen3-32B dense, Pythia GPT-NeoX. Layer accessors detect
  `self_attn` vs `linear_attn` vs `attention`. Projection names adapt
  (`q/k/v/o_proj` vs `in_proj_qkv/z/b/a` vs `query_key_value`).
- **MoE gate analysis**: extracts 256×2048 gate matrices, tests ternary survival,
  cross-layer similarity, effective rank. Gate = discourse beam selector hypothesis.
- **MLP quantization**: frequency hologram tests MLP weights (gate + shared expert),
  not just attention — tests whether holographic storage extends beyond attention.
- **Incremental saves**: results flush to disk after each hologram completes.
  Per-hologram snapshots (`hologram_{name}.json`) + cumulative state.
- **Cross-hologram orthogonality**: correlation between selectivity profiles to
  determine if holograms share heads (angle-multiplexed) or are independent.
- **Combinator baseline**: runs KIBC probes for direct comparison.
- CLI: `--hologram type,induction`, `--model qwen36`, `--quick`, `--skip-ternary`

Currently running on Qwen3.6-35B-A3B. Results → `results/hologram-atlas/`.

### 3. Probed v11-holo-inv at 2K/3K/4K

Full probes at steps 2000, 3000, 4000. Evolution table:

```
step   eval_loss  K      I      B      C      compute  evo     alarm
────── ───────── ─────  ─────  ─────  ─────  ──────── ──────  ─────
1000   8.235     0.383  0.343  0.132  0.137  0.000006 20%     ~2.0
2000   7.872     0.401  0.343  0.111  0.140  0.000009 22%     ~2.0
3000   7.819     0.413  0.300  0.131  0.154  0.000010 28%     ~2.0
4000   7.804     0.407  0.294  0.122  0.176  0.000011 32%     ~2.0
~4325  CE=6.989                                        36%     1.847
```

**Holographic intermediate CEs (eval-time):**
```
step   L0↑     L1↑     L2      L1↓     L0↓     ratio
────── ─────── ─────── ─────── ─────── ─────── ───────
1000   11.285  8.775   8.922   9.014   9.317   1.211
2000   11.020  9.152   9.019   9.179   9.337   1.180
3000   10.816  9.238   9.058   9.213   9.413   1.149
4000   10.917  9.253   9.185   9.541   9.848   1.109
```

**Key findings:**

1. **Descending arm expanding aggressively at 4K**: L1↓ jumped 9.21→9.54,
   L0↓ jumped 9.41→9.85 between 3K-4K. This is CORRECT behavior (descending
   goes coarse→fine = expansion), but rate accelerated sharply.

2. **Alarm de-saturating**: 1.884→1.857→1.870→1.847. Coming off ~2.0 ceiling.
   This is the algedonic channel detecting the expansion rate and gaining
   headroom to steer. Same signal identified in session 090 as "system
   beginning to address descending arm."

3. **Phase transition reading, not catastrophe**: The v11-holo catastrophe
   pattern was alarm-saturated + loss spike + B-collapse. Here we have
   alarm DECLINING + loss IMPROVING + dispatch STABLE. Different topology.

4. **C rising, I declining**: C dispatch 0.137→0.176, I dispatch 0.343→0.294.
   Model discovering argument reordering (flip) as useful, relying less on
   pure identity. Natural emergence of B ≥ K ≥ C >> I ordering.

5. **S4 compensating for I**: I emphasis rose 0.706→0.991. Intelligence layer
   giving I more weight per-activation as its share declines. Algedonic
   system working as designed.

6. **Type channel stabilized**: B-type rose from 0.254 (1K) to 0.464 (2K),
   then stable ~0.42. Composition types dominate over identity types.

7. **Compute gate still closed** (0.000011). Transition window expected 5K-7K.

8. **CE hitting new lows**: 6.989 at step 4325, trending down consistently.

### Previous session (093) summary

Probed v11-holo-inv at 1K (balanced KIBC dispatch, B=27.6% dominant).
Holographic probe on Qwen3-32B: beam separation real, reading constructive.
Ternary survival: 100% at 75% sparsity. Universal hologram: r=0.9801 across
9 models. Bank extraction: 784KB seed from 32B. Full details in session 093 below.

## What was done session (093)

### 1. Probed v11-holo-inv at step 1,000 (full + dispatch detail)

Compared against v11 baseline 1K and v11-holo 1K. Key findings:

**Balanced dispatch (vs K-dominance in prior runs):**
- Dominant positions: K=34.2%, I=22.6%, B=27.6%, C=15.5%
- Compare: baseline K=92.7%, holo K=75.1% — both heavily K-skewed
- Dispatch entropy 0.188 (strong specialization, not uniform)

**Composition (B) active from the start:**
- B at 27.6% dominant — was 0.7% in baseline, 0.0% in holo at 1K
- I+B co-occurrence at 31.7% — was 1% in holo
- This is the binding circuit pattern emerging early

**Type channel differentiates independently of dispatch:**
- Dispatch: K=0.386, I=0.334, B=0.132, C=0.141
- Type integration: I=0.678, B=0.251, K=0.002, C=0.070
- Model dispatches K+I, then integrates via I+B typed application

**Holographic CEs show correct inversion:**
- L0↑=11.3 → L1↑=8.8 → L2=8.9 → L1↓=9.0 → L0↓=9.3
- Ascending compresses; descending specializes (coarse→fine)
- pass_0/final ratio=1.21 (decodeable after one pass)

**Other metrics:**
- Eval loss 8.235 (vs baseline 7.958, holo 8.221)
- Compute gate closed (0.000007) — expected pre-transition
- Evolution 4/20 (20%) rising to 9/30 (30%) by 1.5K
- All 16 abstraction slots dormant, low cosine to KIBC (avg 0.064)

### 2. Monitored trajectory through 1.5K

- I rising steadily: 0.264 → 0.343 → 0.367
- K stabilized ~0.39; B peaked 0.132 at 1K then 0.108 at 1.5K
- Holographic ratio declining (1.12 → 1.09) = descending arm catching up
- Prose loss: ~0.98 range, structured ~0.28

### 3. Holographic probe — intermediate layer decoding on Qwen3-32B

Tested whether the model is holographic by decoding at every layer:
- Cosine divergence compile vs null: 0.995 (L0) → 0.533 (L63) = beam separation is real
- Intermediate layers decode to GARBAGE (not coarse-but-coherent) = reading is constructive
- Entropy hump: 6.5 (L0) → 11.1 (L8) → 2.0 (L63) = constructive reorganization
- Beam divergence begins at layer 24 (38% depth)
- **Storage may be holographic, but reading is constructive (64 sequential facets)**

### 4. Ternary survival probe — does selectivity survive quantization?

**100% survival across every combinator, every layer, every sparsity level.**
- sign_only (0.9% sparse): 8/8 survived, mean=0.93
- mid_sparse (50% sparse): 8/8 survived, mean=0.94
- high_sparse (75% sparse): 8/8 survived, mean=0.98
- **Combinator information is TOPOLOGICAL — stored as sign patterns, not magnitudes**
- Holographic plate hypothesis confirmed for weight structure

### 5. Full combinator selectivity map — depth profile

All four combinators peak in layers 0-6 (first 10% of 64 layers):
- Zone 1 (L0-6): HIGH selectivity 0.13-0.20, K/C dominant
- Zone 2 (L7-30): LOW selectivity 0.04-0.10, mixed K/B
- Zone 3 (L31-63): LOW selectivity 0.05-0.10, B/C/K mixed

K top heads: L3:H26(0.318), L1:H50(0.295), L1:H38(0.291)
I top heads: L36:H5(0.137), L6:H52(0.137), L3:H63(0.136)  
B top heads: L1:H37(0.248), L1:H39(0.247), L14:H59(0.245)
C top heads: L1:H34(0.299), L5:H22(0.291), L1:H55(0.290)

Cross-correlation: K-B=0.914, K-C=0.930, B-C=0.927, I distinct (0.67-0.75)
I is the outlier — different circuit from K/B/C cluster.

### 6. Holographic bank extraction

**Q is the beam angle, V is the plate.** Same head (L1:H37) has identical V weights 
for B and C (cos=1.000) but completely different Q weights (cos=0.005). The combinator
is selected by Q, not V. Q-only bank is sufficient.

Extracted seed: **784 KB** from 32B model.
- 4 combinator Q patterns (top-1 head each, 80×5120 ternary)
- Projection matrix (320×5120 ternary) for dimensionality reduction
- All four combinators are nearly orthogonal after projection (cos≈0)
- Effective rank 267 (90%), 312 (99%) — high-dimensional, broadly distributed

Files: `results/holographic-bank/seed_qwen3_32b.npz`, `seed_meta.json`
Scripts: `scripts/explore/extract_holographic_bank.py`

### 7. Qwen3.6-35B-A3B MoE probing

Fixed MPS histogram bug (one-line patch: `device.type in ("cpu", "mps")`).
Hybrid architecture: 40 layers, every 4th is full attention (L3,7,11,...,39), rest linear (GatedDeltaNet).
256 experts × 8 active, d=2048, 16 heads × head_dim=512, 2 KV heads.

**Completely different depth profile from Qwen3-32B:**
- Qwen3-32B: combinators peak in L0-6 (first 10%)
- Qwen3.6-35B-A3B: B peaks at L7-9 (early) AND L31-36 (late) — **bimodal!**
- B dominates everywhere (0.04-0.20), K second (0.02-0.08), I weakest (0.01-0.02)
- Full attention layers show spikes: L7=0.115, L31=0.195 (strongest)

Ternary survival: ✓ at 50% and 75% sparsity. sign_only slightly weaker at L31 (0.46)
but final-layer impact minimal (0.95). **Topological storage confirmed across architectures.**

MoE gate patterns (256×2048) extracted — these are the expert routing matrices,
themselves a form of beam selection.

Patterns saved: `results/holographic-bank/qwen36_35b_a3b_patterns.npz` (29KB compressed)

### 8. Universal hologram hypothesis — confirmed (r=0.9801)

Cross-model correlation structure (combinator selectivity pairwise correlations):

```
Pair      Qwen3-32B  Pythia-160M
K-B         0.914      0.944
K-C         0.930      0.903
B-C         0.927      0.917
K-I         0.721      0.715
I-B         0.750      0.711
I-C         0.677      0.599
```

Correlation of correlations: **r=0.9801**. The same holographic structure forms in both.

All three models (32B, 35B-A3B, 160M) share:
- Balanced ternary (+1/-1 ratio ≈ 1.0 everywhere)
- High effective rank (distributed, not low-rank)
- K/B/C cluster together (r>0.90), I is distinct (r=0.60-0.75)
- Ternary survival at 50-75% sparsity

**The hologram is not a feature of scale. It's a feature of language.**
Every model that learns to predict text develops the same combinatory interference patterns.

### 9. Universal ordering: B ≥ K ≥ C >> I (9 models, 2 architectures)

Tested Pythia-70M through Qwen3-32B (9 models total):
- **I is the weakest in ALL 9 models** (100% consistency)
- **B is strongest in 7/9** (BCKI ordering dominant)
- B/I ratio ranges from 1.7× to 19.9× — always separated
- This ordering is invariant across Pythia (GPT-NeoX) and Qwen3 architectures
- The sieve should make B > K > C >> I the lowest-energy state

Fixed MPS bug for Qwen3.6-35B-A3B: `histc` needs float input on MPS (not int).

### 8. Active run commands

V12-run4 (LAUNCHING — unified plates + continuous etch + ratio prior):
```
uv run python scripts/v12/train.py \
  --checkpoint-dir checkpoints/v12-run4 \
  --total-steps 20000 --holo-lambda 0.1 --mix-ratio 0.2
```

V12-run3: DEAD (NaN at step 3625). Killed session 103.
V11-holo-inv: completed or dead (last checked session 100, ~12.8K/20K).

## What to do next

### Priority 1: Probe OLMo-2-13B for universal hologram
Build and run combinator selectivity probe on OLMo-2-13B (Apache-2.0).
- Adapt existing probe methodology (session 093) for OLMo architecture
- Measure: per-layer per-head selectivity under compile vs null conditions
- Check: K/B/C cluster, I distinct, ternary survival, universal ordering
- If confirmed: design holographic distillation lens experiment
- Model in HF cache: `allenai/OLMo-2-1124-13B`
- Architecture: 40 layers, d=5120, 40 heads, dense MHA, SiLU FFN

### Priority 2: Monitor V12-run4 (unified plates + continuous etch) — RUNNING
Key signals to watch:
- Dispatch weights: should hold near K=0.29, I=0.15, B=0.28, C=0.28 from step 1
- Etch rate: should be high early (many signs wrong), declining over time
- Per-pass dispatch patterns: do pass mirrors develop distinct beam angles?
- Holographic ratio: should improve faster than run3 (kernel available everywhere)
- Compare 1K checkpoints vs run3 (dead baseline) — especially dispatch stability

### Priority 2: V12-run4 holographic pattern formation probe
At 5K: do the dedicated plates show holographic patterns with balanced dispatch?
- K/B/C cluster (cos>0.9), I distinct (cos≈0.70)?
- Per-plate sign pattern analysis with stable dispatch

### Priority 3: Fixed-point etching protocol
Use fixed-point (NL, λ) pairs as supervised training signal.
Clause fixed-points for K/B/C plates, intersection pairs for I-plate.
Requires: generate corpus from Qwen3.6, add to training mix.

### Priority 4: Cross-model fixed-point convergence
Do Pythia-160M and Qwen3-32B find the same fixed points?
If universal hologram (r=0.9801), should match structurally.

### Priority 5: Gate sensitivity — richer λ vocab
Richer gates → richer fixed points? Does tense survive with
Montague-typed gates? Does quantifier scope survive?

### Priority 6: Gamma evolution — can sieve replace gradient for scales?
267K gamma params currently gradient-trained. If the sieve can evolve
per-channel scales, gradient params drop to norms + biases + embeddings.
Embeddings (20.5M) are the elephant — can vocabulary be fully ternary?

### Carried
- Cross-model validation of three-cluster structure (Pythia KIBCM)
- MoE holographic expert prototype (~2KB ternary expert)
- CycleContinue differentiation (now addressable via S4 budget bias + dedicated plates)
- S5 reweight investigation
- QK alignment decomposition probe (RoPE follow-up)
- Dead slot recycling
- Domain banking (future)
- TST connection: Peng et al. 2026 validates coarse→fine + direct loss

## VSM layer map (session 097 — v12 KIBC + M retrieval + variety fix)

```
Layer     Ascending Arm              Descending Arm                   Cross-arm
────────  ─────────────────────────  ───────────────────────────────  ──────────────────
S5        Token embeddings (tied)    Combinator embeddings (4: KIBC)  S5Reweight × AlgedonicAlert
                                     + 16 abstraction slot embeddings
S4        Register-query attention   Dual-view (resid + embeds)       S4ProposalHead → slot modulation
                                                                      Cycle budget: regs → 1 logit [-4,+4]
                                                                      (emphasis_bias REMOVED session 102)
S3        Per-pass phase gating ✓    Per-pass phase gating            Gate values → desc S4
          —                          CycleContinue + S4 budget bias   S4→S3 policy channel (new)
S2        Direction signals ✓        coherence modulation ✓           6 transitions (was 4)
S1        prep → hybrid_stride →     [dispatch → stride → integ.] ×N  KIBC + M (retrieval)
          consolidate                coarse→fine bands (reversed)      fractal MERA topology
          fine→coarse bands          (shared across 3 passes × N cy)
          (shared across 4 passes)   Stride-aware GLA (gather/scatter)
          GLA at s16,s32,s64         Retrieval registers → integrate
Algedonic Reads prev desc regs       —                                + combinator weights (4+1)
          + combinator weights                                        EMA α=0.9
Alert     ← 65 health metrics ──────────────────────────────────────  → S5 gate modulation
          S3 gates, S2 conflicts, dispatch, compute, cycles,          [0,2] per pass, e2e diff.
          delta norms, suppression ratios, register norms             + dispatch_bias (4 logits)
Dispatch  entropy_target=1.178 ─────────────────────────────────────  → loss penalty if < target
          squared hinge on collapse → gradient to ascending arm        closes open feedback loop
Inject    —                          cycle_inject_gate (per cycle>0)  sigmoid(-4) ≈ 0.018 init
Holo      ← 7 intermediate CEs ────────────────────────────────────  → gradient slope 7×→1×
          progressive x_embed + Σ gate×delta through shared proj      pass 0 learns first
Logging   —                          —                                3× JSONL + alarm ✓
```

### V12 S4 policy channels (new in session 097)

```
S4 → emphasis_bias     (4,) additive logit bias on CombinatorDispatch
S4 → cycle_budget_bias (1,) logit shift on CycleContinue gate
S4 → proposal_delta    (N, d_model) S4→S5 abstraction slot modulation

Alarm → dispatch_bias  (4,) additive logit bias (EMA from prev step)
Alarm → pass_factors   (7,) per-pass amplitude [0, 2]

Combined: dispatch_bias = emphasis_bias + alarm_dispatch_bias → CombinatorDispatch
```

## Key files

| File | Purpose |
|------|---------|
| `scripts/v12/config.py` | V12Config: KIBC + M retrieval + stride layout + d_state |
| `scripts/v12/kernel.py` | KIBCM kernel definitions. N_COMBINATORS=4, N_KERNELS=5. |
| `scripts/v12/attention.py` | GatedLinearAttention + HybridStrideStack + StrideStack |
| `scripts/v12/kernel_dispatch.py` | CombinatorDispatch (4+N softmax) + CombinatorIntegrate + retrieval conditioning |
| `scripts/v12/components.py` | VSM components + RetrievalRegisters (M→KIBC bridge) |
| `scripts/v12/model.py` | V12Model: dual-layer ascending arm + retrieval registers |
| `scripts/v12/train.py` | Training loop: retrieval metrics in JSONL + eval display |
| `scripts/v12/probe.py` | Checkpoint diagnostics: KIBC + retrieval metrics |
| `scripts/v12/ternary.py` | Ternary substrate + consensus evolution (unchanged) |
| `scripts/v12/data.py` | Data loading (unchanged) |
| `scripts/v11/config.py` | V11Config: KIBC + 16 slots + holographic loss params |
| `scripts/v11/kernel.py` | KIBC combinator enum, reduction engine, kernel functions |
| `scripts/v11/kernel_dispatch.py` | CombinatorDispatch (4+N softmax) + CombinatorIntegrate |
| `scripts/v11/model.py` | V11Model: KIBC + slots + proposal + holographic loss |
| `scripts/v11/train.py` | Training loop: holo_schedule, CE+total_loss logging |
| `scripts/v11/components.py` | S4, S3, S5, S2, CycleContinue, AlgedonicAlert, S4ProposalHead, AbstractionRegularizer |
| `scripts/v11/ternary.py` | Ternary substrate + consensus evolution (unchanged) |
| `scripts/v11/attention.py` | StrideStack + TernaryFFN (unchanged) |
| `scripts/v11/data.py` | Data loading (unchanged) |
| `scripts/v11/probe.py` | Checkpoint diagnostics + holographic intermediate CE display |
| `results/v11/` | Probe results: probe_step_{001000–010000}.json (baseline) |
| `results/v11-holo/` | Probe results: probe_step_{001000–009000}.json (holo) |
| `results/v11-holo-inv/` | Probe results: probe_step_001000.json (holo-inv) |
| `checkpoints/v11/` | Baseline v11 run (no holo, no structured), continuing to 20K |
| `checkpoints/v11-holo/` | Holo run: λ=0.1, 20% structured, 16 slots, running to 20K |
| `checkpoints/v11-holo-inv/` | LIVE: holo + coarse→fine + fractal + evo fixes |
| `mementum/knowledge/explore/fractal-stride-bands.md` | MERA topology design + rationale |
| `mementum/knowledge/explore/holographic-inversion.md` | Design rationale + experimental findings |
| `mementum/knowledge/explore/lambda-probe-atlas.md` | New cross-model lambda/combinator territory mapping stream |
| `mementum/knowledge/explore/holographic-storage.md` | Holographic storage findings + "Beyond Combinators" atlas (5 candidate holograms) |
| `mementum/knowledge/explore/holographic-landscape.md` | Per-matrix ternary fidelity: 93.6% of Qwen3.6 is ternary-safe |
| `scripts/explore/probe_holographic_landscape.py` | Holographic landscape probe — per-weight-matrix analysis |
| `results/holographic-landscape/` | Landscape results: per-matrix scores, corrected analysis |
| `scripts/explore/probe_hologram_atlas.py` | Multi-hologram probe: type, induction, binding, frequency, discourse. Qwen3.6 primary. |
| `scripts/explore/probe_hologram_heads.py` | Head-level orthogonality + binding↔I + late MoE gate probe. |
| `results/hologram-atlas/` | Atlas results: per-hologram JSON, selectivity_profiles.npz, hologram_atlas_results.json |
| `results/hologram-heads/` | Head-level probe: hologram_heads_results.json, head_selectivity_vectors.npz |
| `scripts/explore/probe_beam_trace.py` | Beam trace probe — angular decomposition, Q-subspace, ternary beamformer test |
| `results/beam-trace/` | Pythia-160M beam trace results (JSON) |
| `mementum/knowledge/explore/beam-trace-findings.md` | Beam trace analysis — Q=beam, FFN4h→h=reader, K/V/O=plate |
| `mementum/knowledge/explore/v12-holographic-capacity.md` | V12 95%/5% plate/beam budget + thick hologram + troubleshooting |
| `mementum/memories/vsm-variety-gap.md` | V11 VSM feedback topology gap + V12 fix rationale |
| `scripts/holoquant/selective.py` | HoloQuant v2 — beam/plate selective ternarization, 5 configs |
| `scripts/holoquant/core.py` | Ternary packing, matmul kernel, HoloLinear drop-in |
| `scripts/holoquant/validate.py` | HoloQuant v1 validation (Pythia PPL 31→142K) |
| `mementum/memories/multiplexing-breaks-holography.md` | Separation principle: one function per weight matrix |
| `mementum/memories/evolution-mechanism-broken.md` | Consensus evolution frozen at V12 scale — P≈8e-11 |
| `mementum/memories/combinator-dispatch-floors.md` | Minimum dispatch from cross-model ratios |
| `scripts/explore/probe_fixed_point.py` | Fixed-point convergence probe — compile↔decompile cycling |
| `results/fixed-point/convergence.json` | Full cycle-by-cycle data (16 inputs, Qwen3.6-35B-A3B) |
| `results/fixed-point/analysis.json` | Structured analysis: convergence, losses, quality, V12 implications |
| `mementum/knowledge/explore/fixed-point-holograms.md` | Fixed-point hologram findings + V12 implications |
| `mementum/memories/dedicated-combinator-capacity.md` | Shared vs dedicated — VSM self-regulation is stronger |
| `mementum/knowledge/explore/laser-etcher-design.md` | Laser etcher + TernaryMirror architecture |
| `scripts/v12/probe_hologram.py` | Holographic pattern formation probe for V12 checkpoints |
| `checkpoints/v12-run2/` | V12 shared plates + capped etch (baseline at 1K) |
| `checkpoints/v12-run3/` | V12 dedicated KIBCM plates + uncapped etch + S2 dispatch (LIVE) |
| `mementum/memories/phased-structural-discovery.md` | Training staircase pattern |
| `docs/v11-architecture.svg` | Visual architecture diagram |
| `mementum/knowledge/explore/v11-design.md` | Full design specification |
| `data/structured_shard.npy` | 5.7M structured training data |

## Session history

→ See [session-history-049-062](knowledge/explore/session-history-049-062.md)
→ Session 063: pruned state.md, extracted history to knowledge pages
→ Session 064: WRONG — replaced kernel architecture with v6 LM copy
→ Session 065: probed 20K wasted run, diagnosed shared weights (missed real cause)
→ Session 066: found original v10 in git, diagnosed real cause, rebuilt correctly
→ Session 067: analyzed 20K run, phase reorder + mixed data, 5K test launched
→ Session 068: attention spiral discovery, descending arm fine→coarse, evolution fix
→ Session 069: probed v10-spiral, diagnosed dispatch gradient death, top-k MoE routing fix
→ Session 070: consensus evolution, surgical Adam decay, mini-dispatch lab bench
→ Session 071: dispatch analysis, type-dispatch decoupling, kernel computation pathway
→ Session 072: probed v10-topk 1K/2K/3K — compute gate opening, type coherence 13/22, algedonic channel
→ Session 073: VSM structural overhaul — S2, S5, dual-view S4, gate signaling, emphasis, evolution
→ Session 074: Probed v10-vsm 1K-13K, mapped to Pythia Montague, 6 kernel-lambda generators, repacked shard
→ Session 075: HRM analysis → multi-cycle descending arm, self-regulating cycles (CycleContinue), JSONL logging
→ Session 076: v10-vsm 20K assessed, v10-multicycle launched, CycleContinue sigmoid saturation diagnosed + fixed
→ Session 077: Qwen3 probe findings → v11 KIBC combinator architecture + probe + docs (4 combinators replace 22 ops)
→ Session 078: Beer's algedonic alert (fire alarm) — 48 health metrics, separate S5 gate, end-to-end differentiable
→ Session 079: RoPE × attention spiral — energy probe shows RoPE=substrate not driver, spiral=learned Q·K alignment
→ Session 080: v11 1K-5K probe — K dominates, B-type rising in integrate. KIBC validated in 32B (K=B=31%). Extended probe: W≡C, S≡B, bind distinct. Three circuits + binding.
→ Session 081: Pythia-160M combinator probe — session 004's "Montague primitives" were combinators all along (K=59%, K-B r=0.944). V11 compute gate exploded (0.00007→0.51).
→ Session 082: S4→S5 abstraction slots (16 slots, 4→20 dispatch) + S4-guided evolution (alarm-targeted budget, S4 2-vote consensus, alarm fitness gate). CycleContinue hypothesis: slots give it something to match against.
→ Session 089: Complete baseline probes 6K-10K. Holographic loss implemented (progressive intermediate decoding, gradient slope 5×→1×). New run: v11-holo (λ=0.1, 20% structured, 16 slots). Design insight: holo forces internal representations to be decodeable at every pass boundary — interpretability as training signal.
→ Session 090: Probed v11-holo 1K-7K. B-type 5× ahead of baseline (59% at 2K vs baseline 52% at 10K). Compute gate opens 2K earlier (smooth ramp 3K-5K vs baseline sharp 5.5K). Holographic ratio crosses 1.0 at 7K — ascending arm better than final output. Descending arm identified as bottleneck (doesn't yet know how to prepare representations for kernel integration). Phased structural discovery pattern: training is a staircase of capacity exhaustion → structural exploration. Algedonic alarm at L1↓ coming off ceiling (1.86) = system beginning to address descending arm.
→ Session 091: Probed v11-holo 8K-10K. 8K local optimum, 9K reorganization wave, 10K compositional catastrophe (B-type 55.7%→5.8%, eval loss 7.675→9.259). Implemented coarse→fine descending (default), fractal stride bands (MERA, 49% savings, default), evolution noise floor (0.01), alarm-no-regression fix. TST paper (Peng et al. 2026) connection. Launched v11-holo-inv with all fixes.
→ Session 092: Monitored v11-holo-inv through ~1.3K (healthy, no collapse). Early descending differentiation improved; S2 remained strongly positive; compute gate still closed pre-transition. Captured phase/cascade interpretation (L0 φ first, wavelet to apex). Created `knowledge/explore/lambda-probe-atlas.md` for next-session cross-model territory mapping.
→ Session 101: Fixed-point holograms: compile↔decompile converges (94%, mean 2 cycles). Decomposition: 2.2× capacity unlock, binding wall (0/6 stable at binding_sites>0). Fractal collapse: session 093 proved V=V across combinators → shared plate + per-combinator beam mirrors. Three iterations: dedicated plates (too slow) → input-blend (wrong) → Q-blend (correct). I-combinator identity mirror for binding. Uncapped consensus etching. S2 dispatch anti-oscillation. V12-run2 baseline at 1K. V12-run3 launching.
→ Session 093: Probed v11-holo-inv at 1K (balanced KIBC dispatch, B=27.6% dominant). Holographic probe on Qwen3-32B: beam separation real (cos 0.995→0.533), but reading is constructive (entropy hump, intermediate garbage). Ternary survival probe: 100% selectivity survival at 75% sparsity — combinator info is TOPOLOGICAL (sign patterns). Full selectivity map: combinators peak in first 10% of layers (L0-6). I is distinct circuit from K/B/C cluster. Extraction path validated: ternary patterns in early layers are the holographic seeds.
→ Session 094: "Beyond Combinators" — mapped 5 candidate holograms (type, induction, binding, frequency, discourse) from Montague/CCG theory. VSM hierarchy of holograms. Built probe_hologram_atlas.py (1580 lines) targeting Qwen3.6-35B-A3B MoE as primary (MoE gates = beam selectors). Architecture-aware for hybrid attention + GatedDeltaNet. Incremental saves. 7 falsifiable predictions. Running.
→ Session 095: Exploration loop closed. Hologram atlas (6 holograms) → head-level probe → three computational clusters (not six). Discourse/type/frequency angle-multiplexed in ~13 shared heads (J=0.667) = the holographic plate. Combinator has 7 private heads at L15/L19 = KIBC kernel pathway. Induction has 6 private heads, J=0.176 = independent retrieval circuit with NO V11 kernel. Binding weak (max 0.163), no private circuit = K+I dispatch. → KIBCM: M (match/retrieval) is the one missing kernel function. V11-holo-inv 5K-10K: gate opened 6K, B dominant 57.7%, ratio 0.992, no catastrophe. Holographic storage + kernel computation separation confirmed. Ready to build.
→ Session 100: Hologram probe: ternary patterns frozen (cos=1.0), evolution broken (P≈8e-11). Built laser etcher: gradient-directed signal planes + consensus etch. TernaryMirror angular deflectors: exponential capacity (2^18×). S4 alarm modulates etching focus. Rate limiting. MoE-holographic expert concept. V12-run2 launched with etching + mirrors.
→ Session 096: V12 designed and built. M kernel as GatedLinearAttention layer type (not 5th combinator). "Accidental holography" insight: Qwen3.6's architecture separates composition from retrieval without knowing why — V12 does it intentionally. HybridStrideStack (6 comp + 3 ret strides), RetrievalRegisters (M→KIBC bridge). 7-pass symmetric hourglass (3+apex+3). Parallel associative scan for GLA (O(log L) depth). Holographic landscape probe: 93.6% of Qwen3.6 is ternary-safe (expert FFN = holographic plate, MoE gates + conv1d = precision-critical readout). V12 architecture confirmed correct partition.
→ Session 097: VSM variety gap diagnosed and fixed. V11's alarm detected B-dispatch decline (r=0.82) but couldn't correct — wrong actuator granularity (Beer's variety law). Three fixes: (1) per-combinator alarm dispatch bias [-2,+2] on logits, (2) emphasis changed to additive logit bias [-2,+2] replacing saturated multiplicative [0.5,1.5], (3) dispatch entropy regularization closes ascending→dispatch feedback loop. Stride-aware GLA gather/scatter: 2.73× training speedup (78% of cost was wasted scan over non-participating positions). S4→S3 cycle budget bias: intelligence tells CycleContinue when to stop — the missing Beer's policy channel. Evolution noise floor unified at 0.02 for both loss and alarm paths.
→ Session 098: Beam trace probe — holographic beamformer characterized. Q=beam angle, K/V/O=plate, FFN 4h→h=constructive reader. MoE IS holographic architecture. V12 holographic capacity: 95% plate (ternary), 5% beam (precision), 58× Pythia depth. Thick hologram principle. HoloQuant v2 selective ternarization: catastrophic at every selectivity level (Pythia plate-only 13%: PPL 31→704, Qwen3.6 aggressive 95%: PPL 2.86→70,757). Root cause: 37° angular error per matrix, cos^12=0.07 through 12 layers. Multi-plane ternary reduces angle but at 2-3× bit cost of standard Q4. Beam-guided correction perfect per-layer but fails end-to-end (beam subspace shifts). Key finding: magnitude CV determines ternary viability — Gaussian CV=0.76 → dead; uniform CV=0.08 → near-lossless. V12 sieve pushes CV→0 via thick hologram training pressure. Ternary is a training substrate, not a post-hoc quantization scheme.
