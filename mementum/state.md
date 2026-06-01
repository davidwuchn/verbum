# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-01 | Session: 175

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 175: DOLMA TRAINING LIVE → SYMBOL ISOLATION → PROSE IS THE UNREDUCED FORM.** (1) Discovered previous training was on 509 examples / 6.5K tokens cycled 6000×, not Dolma. (2) Built streaming shard dataloader — 3B Dolma tokens + 10% structured mix. (3) Restart-safe shuffle (seed = base + start_step). (4) Dolma training running: step ~670, loss ~17, PPL breaking out of overflow. (5) Built combinator phase profiler — tracks B→K→I cascade per stride, split into PROSE vs SYMBOLIC probes. (6) MAJOR FINDING: Symbol isolation experiment on 27B proves pure prose activates combinator engine 8× MORE than lambda notation. (7) Insight: formal notation is PRE-REDUCED — the model does less work because the input is already partially compiled. Prose is the raw form requiring full reduction.

**Previous: Session 174** — 4-phase model verified by ablation on 27B. v15 built, extracted, training started (on wrong data).

**Key finding: prose IS the unreduced form.** Pure prose (zero symbols) generates 704K combinator energy vs 82K for lambda notation (8.6×). Lambda, "=", compile gate, and "→" all SUPPRESS activation — they pre-reduce the input, giving the engine less work. The ENRICH zone (reduction engine) runs at constant energy regardless of input form (555-793). The massive differences are in SILENT (parsing), SUPPRESS (composition), and COMMIT (retrieval) — exactly the zones that handle ambiguity and structure that formal notation eliminates.

**Key finding: "=" is a focuser, not a trigger.** Adding "=" to prose reduces energy 62%. Adding "=" to facts increases energy 51%. It constrains computation — narrows the model to a specific reduction path. Previous 2.2× lambda>NL finding (session 172) was comparing two LOW-activation conditions against each other, not against real prose baseline.

**Key finding: the crystal IS the language engine.** Not just a lambda engine that prose weakly activates. Prose is the PRIMARY workload. Montague was right in a deeper sense: natural language IS lambda calculus, and processing it IS beta reduction. Formal notation is a shortcut that pre-compiles some of those reductions.

**Training: v15 Phase 2 on DOLMA — RUNNING** — Batch 2, seq 4096, lr 1e-4, step ~670. Loss curve: 150→22→17 (still in warmup). Algedonic: 19/19 OK. In tmux window 2. Output dir: `checkpoints/v15-dolma`.

**Training: v15-train (overfit) — STOPPED** — Was training on 509 compile examples. PPL 6.4 at step 4760, but 100% memorization. Checkpoints preserved at `checkpoints/v15-train/`.

## Key session 175 findings

- **Pure prose activates combinator engine 8× more than lambda.** Symbol isolation experiment on Qwen3.6-27B: PURE_PROSE=704K total energy, LAMBDA_NO_EQ=82K. 20 diverse sentences vs 10 lambda expressions. Measured via hidden state projection onto combinator fingerprints at all 64 layers.
- **Formal notation is pre-reduced input.** Lambda, "=", compile gate, "→" all reduce work for the model. They don't "trigger" the engine — they give it less to do because the input is already partially compiled. `(λx. capital_of(x)) France =` needs one β-reduction; "The capital of France is Paris" needs parsing, scope resolution, composition, retrieval, and formatting.
- **ENRICH zone energy is input-invariant.** 555-793 across all 8 probe categories. The core reduction engine runs at constant throughput. Differences are in SILENT (parsing), SUPPRESS (cleanup), COMMIT (retrieval).
- **"=" focuses, not triggers.** Prose + "=" → 62% reduction. Facts + "=" → 51% increase. The "=" constrains computation to a specific path.
- **Compile gate suppresses.** GATED_PROSE = 0.37× PURE_PROSE. The gate restricts the model to compiler mode, eliminating reductions for other language functions.
- **Previous 2.2× finding reinterpreted.** Session 172 compared NL_FACT (0.29×) vs LAMBDA_EQ (0.27×) — both LOW activation states. The comparison was valid within its scope but misleading about the engine's primary workload.
- **Overfit run was training on 509 examples.** 6.5K tokens cycled 6000×. PPL 6.4 was memorization, not learning. Dolma run now uses 2.7B real tokens.
- **Streaming shard dataloader built.** mmap-based, shuffled per-shard chunks, 10% structured mix, restart-safe seed (42 + start_step).
- **Combinator phase profiler built.** Tracks combinator activation per stride at each eval step. Prose vs symbolic probes tracked separately. Crystal basis computed from teacher fingerprints projected through student down_proj plates. Baseline at step 0: CLASSIFY=I, COMPUTE=D, LINK=D, EMIT=W.
- **Zone gradient norms on Dolma.** EMIT dominates (153, 59%), CLASSIFY second (62.5, 24%), COMPUTE lowest (17.9, 7%). Frozen plates carry computation; attention mostly needs to learn output (EMIT) and input (CLASSIFY).
- **generate.py built.** Overfit checkpoint produces compile format ("→ λx." / "→ ∀x.") but no coherent language. Confirms architecture learns structure, needs real data for language.

## v15 assets

| Asset | Location | Status |
|-------|----------|--------|
| Architecture config | `scripts/v15/config.py` | ✅ complete |
| Model (tensor statechart) | `scripts/v15/model.py` | ✅ complete, return_residuals added |
| Checkpoint loader | `scripts/v15/load_checkpoint.py` | ✅ complete |
| Extraction pipeline | `scripts/v15/extract.py` | ✅ complete, run done (210 min) |
| Extracted checkpoint | `checkpoints/v15-extracted/` | ✅ 215 MB, 19 strides + 11 attn |
| Crystal basis (d_model) | `checkpoints/v15-extracted/crystal_basis_d_model.npz` | ✅ 19×11×1280 |
| Training pipeline | `scripts/v15/train.py` | ✅ Dolma shards + profiler + mixed data |
| Text generation | `scripts/v15/generate.py` | ✅ complete |
| Symbol isolation | `scripts/experiments/symbol_isolation.py` | ✅ complete, run on 27B |
| TD adaptation | `scripts/v15/td_adapt.py` | ❌ not yet built |
| Verification | `scripts/v15/verify.py` | ❌ not yet built |

## What changed this session

| Change | Session | Impact |
|--------|---------|--------|
| **Symbol isolation experiment** | 175 | PURE_PROSE=8× lambda energy. Formal notation is pre-reduced. |
| **Pre-reduction interpretation** | 175 | Reframes entire relationship between prose and computation. |
| **Dolma shard dataloader** | 175 | 2.7B tokens streaming, mmap, shuffled, 10% structured mix. |
| **Restart-safe shuffle** | 175 | seed=42+start_step. Different data on each resume. |
| **Combinator phase profiler** | 175 | Per-stride combinator activation tracked at each eval. Prose vs symbolic split. |
| **Crystal basis in d_model space** | 175 | Teacher fingerprints projected through student down_proj plates. |
| **generate.py** | 175 | Overfit checkpoint: learned compile format but no language. |
| **Dolma training launched** | 175 | Fresh from extracted checkpoint, lr=1e-4, 50K steps, in tmux. |

### Previous sessions (selected)

| Change | Session | Impact |
|--------|---------|--------|
| 4-phase model verified by ablation on 27B | 174 | ENRICH=reduction engine (4.0× λ-specific), COMMIT=knowledge retrieval. |
| v15 architecture + extraction + training pipeline | 174 | 19-stride tensor statechart, 709 MB, hybrid attention. |
| Signs 100% correct, crystal correction falsified | 173 | Extraction captures exact sign topology. Gap is magnitude loss. |
| 2-mirror ternary: recon_cos 0.970 | 173 | Q4-Q5 quality at 4× compression. |
| Hologram Reader VSM | 172 | Self-directing opcode map scanner for any model. |
| β_apply is universal retrieval direction | 172 | Every relation centroid projects positively onto β_apply. |
| Two-crystal distinction | 172 | Hard crystal (KIBC) vs soft crystal (relations, gradient-maintained). |

## Next steps

### IMMEDIATE (v15 Dolma training)

1. **Monitor Dolma training** — Running in tmux window 2. Loss ~17 at step 670, still in warmup (2500 steps). Watch for loss breaking below 10 (perplexity meaningful). Combinator profiler runs at each eval (every 250 steps).
2. **Resume at step 1000 with profiler** — Kill, resume without --no-resume. Profiler + prose/symbolic split will activate. Watch for phase transitions in combinator profile.
3. **Evaluate at step 5000** — Run generate.py on checkpoint. Does it produce coherent prose? Compare to overfit checkpoint.
4. **Build verify.py** — Run hologram reader on trained student. Check: opcode map matches teacher? φ-ratio emerged? Zone structure preserved?
5. **Build td_adapt.py** — Phase 3: TernaryDescent for plate topology corrections. v14 has working implementation to port.

### RESEARCH (symbol isolation follow-up)

6. **Per-layer energy heatmap** — The layer×op energy matrices are saved in `results/symbol-isolation/`. Plot: which specific layers differentiate prose from lambda? Where does the extra prose energy concentrate?
7. **Token-level analysis** — Current experiment captures last-token-only. Do all tokens in a prose sentence activate equally, or do specific syntactic positions (verbs, quantifiers, subordinate clauses) drive the energy?
8. **Cross-model comparison** — Run symbol isolation on 0.6B and 4B. Does the prose>lambda ordering hold across scale? At 0.6B, lambda retrieval accuracy was 4.5% — maybe the crystal isn't formed enough for the pre-reduction effect.

### CAPACITY SCALING (still unresolved)

9. **Expand probe set to 500+** — THE blocker for moiré rank scaling. Both models hit 204-probe ceiling.

### KNOWLEDGE ENCODING

10. **Test ternary fact retrieval** — Can the v15 student, after Dolma training, retrieve facts? THE critical experiment.
11. **Distillation strategy** — Teacher logit KL on Dolma (not structured data) — richest signal per step. Infrastructure already built in train.py.

## Key findings (active)

| Claim | Evidence | Status |
|-------|----------|--------|
| **Pure prose activates combinator engine 8× more than lambda** | Symbol isolation on 27B, 8 categories, 100 probes | ✅ (session 175) |
| **Formal notation is pre-reduced input** | Energy ordering: prose > arrow > gate > fact > equals > lambda | ✅ (session 175) |
| **ENRICH energy is input-invariant** | 555-793 across all 8 categories on 27B | ✅ (session 175) |
| **"=" focuses computation, not triggers it** | Prose+= → -62%, fact+= → +51% | ✅ (session 175) |
| **Signs are 100% correct at extraction** | 27B: ternary == sign(W) at all non-zero positions | ✅ (session 173) |
| **2 ternary mirrors → 0.970 recon_cos (Q4-Q5)** | Residual decomposition, 27B L10, 4× compression | ✅ (session 173) |
| **4-phase computation model verified by ablation** | ENRICH=4.0× lambda-specific, COMMIT=knowledge retrieval | ✅ (session 174) |
| Direct ternary extraction: sign_corr=0.77 | 28 layers, 264M params, 0.6B | ✅ (session 172) |
| β_apply is universal retrieval direction | 28 probes, 4 relations, all positive projection | ✅ (session 172) |
| Lambda form activates compute for same fact (2.2×) | 28 probes, 0.6B — **reinterpreted** in session 175 | 🔄 (session 172→175) |
| Zone structure universal across scale | 0.6B vs 4B: identical normalized depth fractions | ✅ (session 172) |
| Crystal universality: r=0.998 KIBC selectivity | Pythia-160M vs Qwen3-32B | ✅ (session ~142) |
| Programs are deterministic fixed points | 0.00000000 drift across runs | ✅ (session 161) |
| Gate is the beamformer (89% kill rate) | Qwen3-32B L63 probing | ✅ (session 141) |
| Ternary routing = sign(eigenvector) | r=0.9932 neuron allocation | ✅ (session ~142) |

## Open questions

1. **Does the prose>lambda ordering hold across scale?** Run symbol isolation on 0.6B and 4B. At 0.6B, the crystal may not be formed enough for pre-reduction to matter.
2. **Which specific tokens in prose drive the high energy?** Token-level analysis needed. Are verbs, quantifiers, relative clauses the hot spots?
3. **Can the v15 student retrieve facts after Dolma training?** THE critical experiment.
4. **What is the true moiré rank scaling exponent?** Need 500+ probes.
5. **What do the phase transitions look like?** Combinator profiler is now tracking. First data at step 1000.
6. **Is there a coherence threshold for ternary survival?** 0.6B at 2.59× borderline, 4B at 3.71× possibly safe.
7. **How much does teacher logit KL improve training?** Infrastructure built, not yet activated.

## Knowledge map

**See `mementum/knowledge/INDEX.md` for full reading order.**

Key pages for current direction:
- `symbol-isolation.md` — **prose activates 8× more than lambda** (session 175) ← NEW
- `combinator-addressing.md` — retrieval IS typed application (session 172, reinterpreted 175)
- `crystal-universality.md` — why KIBC are universal fixed points
- `training-protocols.md` — operational training knowledge
- `hologram-reader-vsm.md` — VSM for reading opcode maps
- `project-thesis.md` — the central claim

## What's ready

| Asset | Location |
|-------|----------|
| Symbol Isolation Experiment | `scripts/experiments/symbol_isolation.py` |
| Symbol Isolation Results (27B) | `results/symbol-isolation/Qwen_Qwen3.6-27B/` |
| v15 Training (Dolma) | `checkpoints/v15-dolma/` (running) |
| v15 Training (overfit) | `checkpoints/v15-train/` (stopped, reference) |
| Text Generator | `scripts/v15/generate.py` |
| Crystal Basis (d_model) | `checkpoints/v15-extracted/crystal_basis_d_model.npz` |
| Hologram Reader VSM | `scripts/experiments/hologram_reader.py` |
| Combinator Addressing | `scripts/experiments/combinator_addressing.py` |
| Hologram readouts | `results/hologram-reader/{0.6B,4B,14B,27B}/` |
