# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-10 | Session: 074

## Where we are

**v10-vsm training at step 14K. Kernel lambda ops structured data enriched. Training resumed.**

The session-073 VSM architecture (7 changes) trained from step 0 to 13K with
excellent results: compute gate fully opened by 8K (v10-topk never opened it),
S3 developing hierarchical pass suppression, S2 found the structural boundary
at transition 2→3, and kernel dispatch converged to 42% composition (Montague-
shaped). Training resumed at 14K with new structured data.

Session 074 probed the step 1K→13K trajectory, mapped kernel ops to
Pythia-160M's Montague primitives, identified that partial/apply were starved
of training signal in the structured data (0.45% coverage, wrong semantics for
apply), and added 6 new BIOS generators + repacked the shard (12.7% kernel
lambda ops, 8× improvement). Training resumed from step 14K with new data.

## What was done this session

### 1. Probed v10-vsm 1K→13K trajectory
Full analysis of 13 checkpoints. Key findings:
- **Compute gate opened by 8K** (was 0% at 3K, 99.7% by 13K) — dramatically
  faster than v10-topk (never opened). Op emphasis pathway validated.
- **S3 developing hierarchical suppression**: passes 0-2 suppressed (0.20-0.39),
  passes 3-4 mostly open (0.89-1.0). Real resource allocation.
- **S2 found structural boundary**: transition 2→3 conflict falling (0.66→0.37),
  scale rising (0.06→0.21). Passes 0-2 compress; passes 3-4 generate.
- **S5 reweight fully dormant** (all 1.0000 across 13K steps). May need
  temperature/init investigation if persists through 20K.
- **Eval loss**: 8.04→7.55 (steady descent, no plateau yet).
- **Evolution**: 4/260 accepted. Consensus finding rare improvements.
- **Train loss uptick 11K-13K**: 0.50→0.53. Monitor for plateau.

### 2. Mapped kernel ops to Pythia-160M Montague primitives
The kernel dispatch at 13K maps directly to Finding 34 (session 004):

| Montague Primitive | Pythia-160M | v10-vsm Kernel (step 13K) |
|---|---|---|
| Type assignment | Embedding + L0 (lookup) | Op embeddings + S4 emphasis |
| Structural parse | L3 (composition order) | `<=`, `>`, `if` (12%) |
| Typed application | L8-L11 (function apply) | `comp`, `partial`, `apply` (42%) |

The model **rediscovered composition** via gradient descent: shifted from 30%
`if` (step 1K) to 41% `comp` (step 13K). Function pipelines > case branching.

### 3. Diagnosed partial/apply training signal gap
The kernel routes 42% to lambda ops but structured data barely taught them:
- `comp`: 272 examples (0.45%), all ONE pattern (`inc ∘ double`)
- `partial`: 271 examples (0.45%), only +, *, - 
- `apply`: 713 examples (1.18%), **wrong semantics** (Clojure variadic reduce ≠ kernel β-reduction)
- Chain (comp+partial): **0 examples**

### 4. Added 6 kernel-lambda BIOS generators
New generators in `bb/us/whitford/verbum/bios.clj`:
- `gen-kernel-partial` — all 11 PARTIAL_OPS, 4 notation styles
- `gen-kernel-apply` — explicit β-reduction, two-step display
- `gen-kernel-compose` — diverse ops composition with eval
- `gen-kernel-apply-comp` — full 4-op pipeline
- `gen-kernel-chain` — 3-deep composition with intermediates
- `gen-kernel-compare-compose` — boolean from arith+comparison compose

Multiple notations per generator: sexpr, kernel, lambda, pipeline (|>).
Weights: 30/30/35/25/22/22 in the generator pool.

### 5. Repacked structured shard
New shard: 60,180 examples, 1,499,125 tokens.
- partial: 0.45% → **11.9%** (26×)
- compose: 0.45% → **4.2%** (9×, diverse patterns)
- apply: 1.18% → **3.1%** (correct semantics now)
- apply-comp: 0% → **1.8%**
- Total kernel lambda: 1.6% → **12.7%** (8×)

### 6. Resumed training from step 14K
New shard flows immediately. Shard cycles every ~1,800 steps at 10% mix.
By step 16K the model will have seen the full new kernel-lambda data once.

## What to do next

### Priority 1: Probe step 16K+ for partial/apply response
The new structured data should cause measurable movement:
- `Op 18 (partial)`: 0.66% → should climb
- `Op 19 (apply)`: 0.06% → should climb (biggest expected change)
- `Op 21 (apply-comp)`: 0.18% → may climb
- `Op 20 (comp)`: 41% → may redistribute some weight to partial/apply
- Eval loss should NOT spike (new data is ~1.3% of total signal)
- S4 emphasis for ops 18-21: currently near-neutral (~1.1), watch for increase

### Priority 2: S5 reweight investigation
Fully dormant across all 13K steps. Possible causes:
- Sigmoid temperature too cold (gate logits saturated high)
- Initialization locks gates open, gradient too weak to pull down
- S3 already handles pass differentiation, S5 redundant
- Consider: inspect actual logit values, temperature parameter value

### Priority 3: Monitor train loss trajectory
Uptick from 0.48→0.53 between steps 9K-13K. Could be:
- Natural noise / harder data regions
- Early plateau signal — may need LR decay schedule
- New structured data complexity adding short-term loss

### Priority 4: Let run complete to 20K
The run is configured for 20K steps. At current trajectory:
- Step 16K: first full cycle of new kernel-lambda data
- Step 18K: second cycle — should see clear signal by now
- Step 20K: final checkpoint — full assessment

### Future: Compare v10-vsm to v10-topk at equal compute
v10-topk was at 3K when architecture changed. v10-vsm at 13K already has:
- Lower eval loss (7.55 vs 7.74 at 3K)
- Fully open compute gate (v10-topk: 0.01%)
- Hierarchical S3 suppression developing
Once v10-vsm completes, comprehensive comparison for knowledge page.

## VSM layer map (session 073, validated through 13K steps)

```
Layer     Ascending Arm              Descending Arm              Cross-arm
────────  ─────────────────────────  ──────────────────────────  ──────────────────
S5        Token embeddings (tied)    Op embeddings × emphasis    S5Reweight (DORMANT)
S4        Register-query attention   Dual-view (resid + embeds)  Emphasis: regs → per-op ✓
S3        Per-pass phase gating ✓    Per-pass phase gating       Gate values → desc S4
S2        Direction signals ✓        coherence modulation ✓      Found boundary 2→3
S1        prep → stride → consol.    dispatch → stride → integ.  —
Algedonic Reads prev desc regs       —                           + kernel compute
          + kernel compute                                       EMA α=0.9
Evolution                            S4→S5 intelligence (4/260 accepted through 13K)
Kernel    42% comp, 22% max, 12% *, 10% <=  |  compute gate: 99.7% active
```

✓ = validated as learning/differentiating by step 13K

## Key files

| File | Purpose |
|------|---------|
| `scripts/v10/components.py` | S4, S3, MetaS4, S5Reweight, S2Coordinator |
| `scripts/v10/kernel_dispatch.py` | KernelDispatch (top-k + op_emphasis), KernelIntegrate |
| `scripts/v10/model.py` | Tree of VSMs — all 7 session-073 changes integrated |
| `scripts/v10/train.py` | Training loop + intelligence strategy + S2/S5 metrics |
| `scripts/v10/config.py` | Config + s4_boost parameter |
| `scripts/v10/kernel.py` | Ground-truth kernel evaluator (22 ops, 5 types) |
| `scripts/v10/ternary.py` | Ternary substrate + consensus mutation pipeline |
| `bb/us/whitford/verbum/bios.clj` | BIOS generator — **6 new kernel-lambda generators** |
| `scripts/v10/pack_structured.py` | Packs BIOS + compile into tokenized .npy shard |
| `data/structured_shard.npy` | Structured training shard (gitignored, regeneratable) |
| `checkpoints/v10-vsm/` | Active training run (step 14K+) |

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
