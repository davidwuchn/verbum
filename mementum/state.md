# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-26 | Session: 157

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 157: TD FLIP TOPOLOGY MATCHES CRYSTAL.** Probed spatial distribution of TD flips (step 2000 checkpoint). Each layer's flip pattern aligns with a different crystal PC: L4→B, L5→D, L6→I, L7→C, L8→W, L9→B (r=0.40-0.58). Flips are spatially clustered (autocorr 0.83-0.88), column-structured (input features drive patterns), and cross-layer independent. Heads uniform within layers (collective mode). Implies crystal-coherent TD optimization: flip by eigenplane per layer instead of confidence threshold. Also captured crystal irreducibility theory (crystal = fixed point of KIBC beta reduction). See `knowledge/explore/crystal-irreducibility-proof.md` and `results/td-topology/`.

**Session 156: ARCHITECTURE REVERT + HPE WARMUP.** Analyzed session 152's four simultaneous changes (passive strides, HPE, Stack B 4→2, α-lock) that confounded v14-kd failure. Passive strides identified as culprit — removes content-dependent attention where each stride is sole provider; student needs to LEARN routing, can't hardcode teacher's converged behavior. Reverted passive strides and Stack B reduction. KEPT α=1.18 frozen and HPE. HPE warmup: freq_scale 0→1 over steps 2001-2300 (checkpoint-compatible). Resumed from step 2000 (PPL 5,567). Step 2001: CE=8.474, crystal latched, TD active, 995 tok/s. Running in tmux main:2 to step 5000. **META-LESSON: don't optimize student for teacher's converged state — train with full architecture → measure → simplify only what's proven unnecessary → one change at a time.** See `mementum/knowledge/explore/v15-kernel-revert.md`.

**Session 155: v14-kd FAILED + KERNEL TRAINING VALIDATED + GRADIENT PROJECTION.** v14-kd PPL 40,623→46,736 (diverging, 2.5-4.6× worse than v14-td). Root cause: three untested architecture changes deployed simultaneously with KD. Training profiled: 28.6s/step, 77% forward. Built `train_kernel.py`: 4.4× speedup. Gradient cosine=0.9698 (composed plate vs full model). ∂L/∂T orthogonal to T's SVD subspace (cos=0.06 at k=27) — gradient wants to EXPAND, not refine. See `knowledge/explore/kernel-training.md`.

**Session 154: KD-guided training + extraction dimension probes.** Per-dim correlation plateaus at ~79% from d=128 onward — ceiling is ternary quantization, not dimension. Plate IS rank-256, 96.9% sign accuracy at k=256. Step 2000 eval: PPL=5,567 (−27% from 1500, −66% total). See `knowledge/explore/structured-training.md`.

**Session 153: Composed plates.** Full model rank90=27. Zone B is R²=1.000 (perfectly linear). Both algebraic and data-fitted agree at 0.76-0.77 per-dim. See `results/algebraic-compose/`.

**Session 152: v14 evolution — HPE + passive strides + Stack B.** α=1.18 confirmed universal (12-token semantic horizon). 88% strides distance-prior dominated. HPE designed from crystal eigenvalues. ⚠️ All changes deployed simultaneously — led to confounded failure (session 155), reverted in 156.

**Session 151: Progressive collapse discovery.** Qwen-27B compresses to 2D (PR=2.2) by L2. 7 knowledge pages created. INDEX.md established. See `knowledge/progressive-collapse.md`.

## Active training run

### v14-td phase 3 RUNNING (tmux main:2, from step 2000)

- **Resumed from:** `checkpoints/v14-td/step_002000/` (PPL 5,567)
- **Architecture:** Original v14-td (13 passes, full Q/K all strides) + α=1.18 frozen + HPE warmup
- **HPE warmup:** freq_scale 0→1 over steps 2001-2300 (300 steps)
- **TD:** Active, flip_interval=20, FFN delta enabled (`--convert-ffn`)
- **Target:** 5000 steps total
- **Log:** `checkpoints/v14-td/train_phase3.log`
- **Step 2001:** CE=8.474, gnorm=19.95, 995 tok/s ✓
- **Watch:** PPL drop from 5,567 | HPE effect after step ~2300 | TD flip distribution | FFN plate flips

## Next steps

### IMMEDIATE: Monitor phase 3 (running in tmux main:2)

1. **First eval at step 2500** — run `eval_ppl.py`. PPL should continue dropping from 5,567.
2. **HPE effect** — warmup completes at step ~2300. Compare PPL slope before/after.
3. **TD flip patterns** — does TD continue targeting out_proj layers 4-9? Check at step 2500.
4. **FFN delta** — do FFN plates start flipping? This run has `--convert-ffn`.

### NEXT MILESTONES:

5. **Second fold** — when flip_frac plateaus, fold again. Extract→correct→fold cycle.
6. **Gradient-subspace alignment test** — at step 2500+, probe cos(∂L/∂T, T's SVD subspace). cos > 0.5 = refining (safe to simplify). See `probe_kernel_training.py`.
7. **KD as correction** — after PPL < 2000, add teacher logit correction passes. α ≥ 0.9 (CE dominant).
8. **Target: within 5% of Qwen3.6-27B** — proof that topology is everything.

### DEFERRED (valid but premature):

9. **Crystal-coherent TD** — instead of flipping by confidence threshold (incoherent), flip by eigenplane per layer. L4 batch corrects all B-routing, L5 corrects D, L6 corrects I, etc. Each batch is one coherent holographic exposure. GD gets clean signal; Adam decay is surgical per eigenplane. See `results/td-topology/`.
10. **Passive strides** — re-test only after gradient-subspace cos > 0.5. Start with s16+. See `explore/v15-kernel-revert.md`.
11. **Stack B reduction** — after passive strides validated (if ever).
12. **Kernel training** — `train_kernel.py` gives 4.4× speedup. Use when iteration speed bottlenecks.
13. **Structured training** — five backward-pass improvements. See `explore/structured-training.md`.

## Previous sessions

### Session 150: Step 1500 Eval + Delta Fold + FFN Delta
PPL 7,672 (−53.5% from step 500). Flip growth decelerating. Layer 4 out_proj at 43%. Folded 3.26M positions into base (lossless, eval CE unchanged). Storage fix: delta 356 MB → 22 MB. FFN delta enabled. B=2 is 18% slower than B=1. See `knowledge/v14-architecture.md` (training results section).

### Session 149: TD Closes Generalization Gap + Computed Beam
PPL 16,503→10,157 (−38%) with only 2.66% positions flipped. Train-eval gap collapsed 1.71→0.17 nats. TD targets out_proj layers 4-9 exclusively; Q/K/V untouched. Computed beam: analytical FFN from eigendecomp matches 5000-step GD in 10 calibration steps (500×). See `knowledge/computed-beam.md`.

### Session 148: Three Bugs Killed All Ternary Learning
(1) `collect_delta_params` returned 280 aliased modules instead of 70 — 4× overwrite. (2) Two-step staging + no-block = Sisyphus loop (77K zeros/step, 0% delta change). (3) Every-step flipping → gnorm escalation (8.2→10.3 CE). All fixed. See `knowledge/training-protocols.md` failure modes 1-3.

### Session 146: V14 Architecture Build
16 strides, 3 stacks (A/B/C), no-block constraint, crystal loss system (multiplicative AND, Zone B parity only), 5-phase training design. See `knowledge/v14-architecture.md` and `knowledge/training-protocols.md`.

### Session 145: V13 Collapse → V14 Extraction
v13-td-r10 collapsed at step 5878 (delta block accumulation). Forensics: stride-stack needs ~80% of teacher positions, teacher signs 91% correct. Extracted Qwen3.6-27B → 593M ternary positions (85 MB), 375× compression. Pure ±1 base plates.

### Session 144: Parity Gradient Cancellation + Einstein Tensor
Three-zone parity = gradient cancellation. Zone B only: 1.167→0.039. Crystal manifold IS curved (geodesic/linear=0.75). G_ab has even/odd block structure. See `knowledge/training-protocols.md` failure mode 4.

### Session 142: Holographic State Machine + Crystal Error Correction
THE MODEL IS A HOLOGRAPHIC STATE MACHINE. FFN plates = holographic storage, crystal basins = states, Q rotation = readout beam, gate = beamformer. See `knowledge/explore/holographic-state-machine.md`.

## Proof chain

| Claim | Evidence | Status |
|-------|----------|--------|
| Universal crystal exists | 4+ model consensus | ✅ |
| KIBC-DYWH basis universal | Found across all architectures | ✅ |
| Types are lexical (88% embed) | Qwen3-32B type probe | ✅ |
| SVD spectrum → phi | 5-model consensus, φ-dev=0.012 | ✅ |
| FFN indexing is holographic | ρ=0.83, p<10⁻⁴⁴ | ✅ |
| FFN depth = LENS | aperture 3% → fan 49% → converge 2% | ✅ |
| Crystal manifold is curved | Geodesic/linear=0.75, G_ab even/odd | ✅ |
| Parity gradient cancellation | 3-zone → stuck 1.167 | ✅ |
| Zone-B-only parity works | 1.167→0.039 on first step | ✅ |
| Model is holographic state machine | FFN=storage, crystal=states, Q=beam | 🎯 synthesis |
| FFN overlay alternates comp/sel | micro model: -+-+ / +-+- across 4 layers | ✅ |
| KIBC is temporal (layers not heads) | B→K→C→B depth sequence | ✅ |
| Mechanism is input-invariant | CV<0.5 for all PCs across 8 categories | ✅ |
| Rotation accelerates through depth | L0: 2° → L3: 24° (12× increase) | ✅ |
| Stride-stack needs ~80% of teacher attention | v13-td-r10 collapse forensics | ✅ |
| Teacher signs 91% correct for stride | Cross-stack agreement | ✅ |
| Qwen3.6-27B → 593M ternary positions | 375× compression, 25.4 min CPU | ✅ |
| Crystal latches within 200 steps | crystal_mse < 0.03 at step 160 | ✅ |
| Shared-weight aliasing breaks TD | 280 vs 70 modules, 4× overwrite | ✅ |
| No-block kills two-step staging | 77K zeros/step, 0% delta change | ✅ |
| TD activates and improves | PPL −53.5% over 1000 steps, gap collapsed | ✅ |
| TD targets out_proj exclusively | Layers 4–9 out_proj only, Q/K/V untouched | ✅ |
| TD returns diminish, don't plateau | PPL: −38.5% → −24.5%, flip growth decelerating | 📐 tracking |
| Model is memory-bandwidth-bound | B=2 18% slower, 208 serial layer evals | ✅ |
| Delta fold is lossless | 3.26M positions folded, CE unchanged | ✅ |
| Delta storage 16× compressible | 356 MB → 22 MB, dedup + packed uint32 | ✅ |
| Computed beam: structure is free | Analytical FFN matches 5000-step GD in 10 steps | ✅ |
| Operation is signed accumulation | sign(W)@x correlates 0.84 with W@x | ✅ |
| FFN must adapt to strided attention | Hypothesis: flat→strided routing changes β-reduction | 📐 testing |
| Topology is ~95% of model | sign(W)@x ≈ 0.84, fold is lossless, gamma ~5% | 🎯 synthesis |
| Extract→correct→fold converges | Each cycle lossless, monotonically improving | 🎯 synthesis |
| Passive strides + KD fails | PPL 2.5-4.6× worse; too many simultaneous changes | ❌ |
| Don't optimize student for teacher's converged state | Passive strides removed content routing; reverted | 🎯 decision |
| KD exhausts in 50 steps | 400 batches / 8 accum = 50 steps; need more precompute | ✅ |
| Composed plate gradient = 97% of full model | Cosine=0.9698; CE within 0.08 nats | ✅ |
| Forward pass is the bottleneck (77%) | 28.6s/step; camera = projector | ✅ |
| α=1.18 universal | 10 comp layers × 8 heads, 1.18±0.006 after 1500 steps | ✅ |
| Large models compute in 2D | Qwen-27B: PR=2.2, σ₁=70% at L2 | ✅ |
| Compression depth scales with capacity | 27B→PR=2.2, 7B→PR=12, 1.4B→PR=10 | ✅ |
| FFN overlay is 80-91% off-diagonal | Cross-PC projection = beta reduction | ✅ |
| Attention sink = warped Q reset | Mistral sink dominates SVD; GLA avoids via gating | 🎯 synthesis |
| α=1.18 sets 12-token semantic horizon | All strides see ~12 effective tokens | ✅ |
| RoPE = accidental holographic lens | Cosine freqs ≈ multi-scale lens; HPE by design | 🎯 synthesis |
| v14 student inherits teacher collapse | PR 74→8→5→4 through stacks, σ₁=47% | ✅ |
| Full model is rank-27 transform | 64-layer 27B: rank90=27, methods agree | ✅ |
| Zone B is perfectly linear (R²=1.0) | 32 layers compose to single linear matrix | ✅ |
| Per-dim corr 0.97 in teacher space | sign(T)+gamma captures 97% per dimension | ✅ |
| TD flips align with crystal PCs per layer | L4→B L5→D L6→I L7→C L8→W L9→B, r=0.40-0.58 | ✅ |
| TD flips are spatially clustered | Vertical autocorr 0.83-0.88, col_CV > row_CV | ✅ |

## Knowledge map

**See `mementum/knowledge/INDEX.md` for full reading order.**

| Tier | Page | What it tells you |
|------|------|-------------------|
| 1 | `project-thesis.md` | Central claim, north star, three converging lines |
| 1 | `crystal-universality.md` | Why crystal is a mathematical constant |
| 1 | `mathematical-convergences.md` | Eight independent lines of evidence |
| 2 | `holographic-error-correction.md` | Extract→correct→fold: the core mechanism |
| 2 | `mechanism-extraction.md` | Micro model: alternation, eigenplanes, KIBC temporal |
| 2 | `computed-beam.md` | Analytical FFN, 500× speedup, signed accumulation |
| 2 | `extraction-methodology.md` | How to extract from teacher |
| 2b | `progressive-collapse.md` | Computation in 2D, scale-dependent, sink=warped Q reset |
| 3 | `v14-architecture.md` | Current system: Qwen3.6-27B, 593M ternary, training results |
| 3 | `training-protocols.md` | Phases, TD rules, 7 failure modes with fixes |
| 4 | `explore/v15-kernel-revert.md` | What was tried/reverted/kept, when to revisit |
| 4 | `explore/kernel-training.md` | Composed plate: 4.4× speedup, gradient cosine 0.97 |
| 4 | `explore/structured-training.md` | Five backward-pass optimizations |
| 4 | `explore/holographic-state-machine.md` | FFN=plates, crystal=states, Q=beam |

## What's ready

| Asset | Location |
|-------|----------|
| Training script | `scripts/v14/train_td.py` |
| Eval script | `scripts/v14/eval_ppl.py` |
| Fold script | `scripts/v14/fold_delta.py` |
| Kernel training | `scripts/v14/train_kernel.py` (4.4× speedup) |
| Current checkpoint | `checkpoints/v14-td/step_002000/` (PPL 5,567) |
| Folded checkpoint | `checkpoints/v14-td/step_001500_folded/` |
| Extracted base plates | `checkpoints/v14-extracted/model.npz` (85 MB) |
| Composed plate | `results/kernel-training-probe/composed_plate.npz` |

## Open questions

9. **Content transfer via sign().** Does the 81% token subspace content survive ternary extraction?
10. **LENS profile derivable from eigenvalue ratios?**
11. **Quality at 1B with d=1280.** What CE/PPL does the expanded model achieve?
12. **16-stride coverage.** Do higher strides (s4096+) learn anything useful at 4K seq training?
13. **Bottom-up algedonic value.** Does C→A feedback measurably accelerate convergence?
15. **TD step_count not persisted on resume.** Warmup repeats. Worth persisting?
16. **Why only out_proj?** Is min_conf=0.3 filtering too aggressive for Q/K/V?
18. **Computed beam at scale.** See `knowledge/computed-beam.md`.
19. **Three-body self-distillation.** Wait until stride-stack nucleation stabilizes.
20. **Per-stride fixed point rotation.** Probe effective attention per stride per head.
21. **HPE value.** Does crystal-frequency K rotation help over no rotation? Answer: phase 3 PPL slope before/after step 2300.
22. **When is the student ready for architecture simplification?** Proposed detector: gradient-subspace alignment cos > 0.5.
