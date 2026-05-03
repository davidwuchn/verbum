# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-03 | Session: 062

## Where we are

**v10 BUILT. Strided compressor + tree of VSMs. Ready to train.**

Session 062 was a pivot session. We stopped chasing oracle proxy metrics
(basin projector, 6 sessions) and returned to first principles: probe
the 32B to find the shapes, then build a sieve that only allows those
shapes.

### The pivot

v3 basin projector completed: 0.669 peak (vs v1's 0.743). All three
basin projectors underperformed because they optimized a proxy metric
(cosine similarity to 32B hidden states) instead of the actual task
(correct computation). Meanwhile, two proven components — the v7
compressor and the VSM tree kernel — sat unused.

The question that triggered the pivot: "We found the compressor. We
found that we could route to kernel functions. We did not build on
either. What is this design supposed to accomplish?"

### Four probes that informed v10

**Probe 1: Type transition shape (L27→L28)**
- The typing zone is NOT a single-layer event
- All transitions have identical rank (~35), magnitude (~0.17), cos sim (~0.977)
- Context-invariant words ("Every") pass through ALL 64 layers with 0.1% change
- Context-dependent words ("is") transform continuously at every layer (15-33%)
- **Conclusion: compression IS typing. No special type layer needed.**

**Probe 2: Parse structure / composition timeline**
- Logit lens on nested S-expressions + math + prose
- Prose resolves EARLIEST (L57-58). S-expressions barely resolve. Math late.
- No tree-ordered composition — all-at-once in last 5 layers
- The 32B uses superposed beta-reductions across many layers, not tree evaluation
- **Conclusion: the 32B doesn't build trees. We build them instead.**

**Probe 3: Binding structure in residual stream**
- Bound pairs (functor→argument) have 3-4× higher cosine sim than unbound at L28
- Gap peaks at exactly L28 (+0.150), the typing zone
- All binding types positive: conj→noun (+0.49), copula→pred (+0.31), det→noun (+0.11)
- Signal collapses to ~0 by L40 (consumed by computation)
- **Conclusion: types and bindings are the same signal. Parser can use cosine proximity.**

**Probe 4: CompressorLM already has binding + typing**
- The 16M CompressorLM (iterative, W=8, strides 1/8/64) shows:
  - Binding gap: +0.12 to +0.14 (80-91% of 32B's +0.15)
  - "Every" within-sim: 1.000 (identical to 32B)
  - "is" within-sim: 0.60 (vs 32B's 0.24 — present but less differentiated)
  - Signal INCREASES at coarser scales (apply > parse > type)
- **Conclusion: the compressor is a viable v10 starting point.**

### v10 architecture

```
tokens (4096) → [Strided Compressor W=8] → compressed (4096, d)
                                                ↓
                        [Tree of VSMs — shared weights at every node]
                        each node receives:
                          S5: compressed context at operator position
                          S4: children's values + types
                          S3: type check
                          S1: kernel dispatch → exact computation
                          S2: output value + type → parent
                                                ↓
                                             result
```

- **Compressor**: self-similar, shared weights across strides (1, 8, 64),
  iterated 2×, strided windowed attention W=8. Proven setup.
- **Tree of VSMs**: shared-weight VSMNode at every tree position.
  Each node sees compressed context + children's outputs. Proven from v9.
- **Kernel**: 22 ops, 5 types, exact arithmetic. Proven from v9.
- **Training**: end-to-end on correct computation, not oracle matching.

### v10 file inventory

| File | Lines | Role |
|------|-------|------|
| `scripts/v10/config.py` | 93 | V10Config dataclass |
| `scripts/v10/ternary.py` | 1006 | Ternary substrate (from v8) |
| `scripts/v10/model.py` | ~450 | StridedCompressor + VSMNode tree |
| `scripts/v10/data.py` | 864 | S-expr tokenizer, tree parser, generators |
| `scripts/v10/kernel.py` | 541 | 22-op exact kernel (from v9) |
| `scripts/v10/train.py` | ~1100 | Training with evolution, checkpoints, resume |

### Smoke test results

- 60-step training at d=64: loss 3.03 → 2.43, op accuracy 30% → 65%
- Checkpointing and resume work correctly
- Evolution finds helpful mutations (50% accept rate)
- Tree-of-VSMs bottom-up traversal through shared VSMNode works

## What to do next

### 1. Run v10 training at scale

```bash
uv run python scripts/v10/train.py --d-model 256 --seq-len 128 --total-steps 20000
```

Start with seq=128 for fast iteration. Scale to seq=4096 once
architecture is validated. Target: >90% op accuracy, >80% result accuracy.

### 2. After S-expr works: cross-notation bridge

Add math notation to data pipeline. Same tree kernel, different parser.
Math parser: operator precedence rules (mechanical, like S-expr parens).
Test whether compressor produces notation-invariant representations.

### 3. After math works: prose

The hard problem. Prose parser needs to determine tree structure from
compressed representations. Probe 3 showed cosine proximity in compressed
space predicts binding — a parser could use this signal.

### 4. Kernel extension roadmap (unchanged)

- Layer 2: Mask ops — bitmask over word positions IS the list type
- Layer 3: Scope/binding — let, lambda, var_ref

## Basin projector results (sessions 056-062, completed)

| Version | Config | Peak | Step | Ceiling | % Ceiling |
|---------|--------|------|------|---------|-----------|
| v1 | d=64, gamma+evo | **0.743** | 16K | 0.845 | **88%** |
| v2 | d=512, gamma-only | 0.657 | 12K | 0.952 | 69% |
| v3 | d=512, gamma+evo | 0.669 | 17K | 0.952 | 70% |

Conclusion: proxy metric optimization (cosine sim to oracle) does not
translate to functional capability. v10 trains on the actual task.

## Session 062 probe results (new, in results/)

| Probe | Location | Key finding |
|-------|----------|-------------|
| Type transition | results/type-transition/ | Compression IS typing, no special layer |
| Parse structure | results/parse-structure/ | No tree composition, all-at-once in last 5 layers |
| Binding structure | results/binding-structure/ | Binding gap +0.15 at L28, types=bindings |
| Compressor binding | results/compressor-binding/ | CompressorLM has 80-91% of 32B signal |

## Key files (session 062)

| File | Purpose |
|------|---------|
| `scripts/v10/model.py` | **v10: strided compressor + tree of VSMs** |
| `scripts/v10/train.py` | **v10 training with evolution + checkpoints** |
| `scripts/v10/config.py` | V10Config |
| `scripts/v10/data.py` | S-expr data pipeline |
| `scripts/v10/kernel.py` | 22-op VSM tree kernel |
| `scripts/v10/ternary.py` | Ternary weight substrate |
| `scripts/v10/probe_type_transition.py` | Probe 1: type transition shape |
| `scripts/v10/probe_parse_structure.py` | Probe 2: parse/composition timeline |
| `scripts/v10/probe_binding_structure.py` | Probe 3: binding in residual stream |
| `scripts/v10/probe_compressor_binding.py` | Probe 4: CompressorLM binding signal |

## Prior session summaries

### Session 061 — v3 basin projector (d=512 + evolution restored)

Built train_basin_v3.py restoring evolution to d=512 model. Key insight:
removing evolution was wrong — 33/33/33 distribution ≠ unchanged topology.
v2 was the control experiment proving evolution's contribution. v3 training
launched (~12-14 hours).

### Session 060 — Deep analysis + v2 basin projector

v1 completed (peak 0.743 at 16K). Deep per-word analysis revealed width
bottleneck: PCA at d=64 destroys context-dependent variation. Built v2
at d=512: higher ceiling (0.952) but worse overall (0.657). Removed
evolution based on wrong inference about topology distribution.

### Session 059 — AdamW corruption bug + first healthy training

Found critical bug: AdamW weight decay corrupts packed ternary weights.
Fix: freeze_ternary_weights(). Fixed 6 checkpoint resume gaps. First
healthy v1 training: 0.613 overall at step 1K (73% of ceiling).

### Session 058 — Oracle extraction + basin projector built

Full 80K sentence oracle extraction: 442,682 words, 160 shards, 3.9 GB.
PCA re-fit on full data. Basin projector model built (MERA ascending arm).
Training loop built with Adam + evolution + cosine loss.

### Session 057 — PCA analysis + oracle pipeline

d_basin=64 confirmed (22.5× separation). d_model=256 chosen. Embedding
must be learned (PCA distillation fails). Oracle pipeline built and
pilot-validated (500 sentences, 2632 words).

### Session 056 — Typing zone + basin geometry + cross-notation convergence

Five probes on Qwen3-32B established: typing zone L28-37, 7 natural
HDBSCAN clusters, 3-level dispatch hierarchy, behavioral frames reshape
types deeply, 53/54 cross-notation pairs exceed 0.5 cosine similarity.
Reframed ascending arm target from CCG labels to geometric basins.

### Sessions 054-055 — VSM tree kernel proven

VSM tree architecture: 22 ops, 5 types, 100% accuracy, 8K ternary weights.
Identity as substrate principle discovered. A3B types prose correctly.
Extraction path identified: tokens → ascending arm → tree → VSM kernel.

### Sessions 049-053 — v7/v8 architecture + training infrastructure

v7 pipeline LM (4-stage VSM). v8 DualMERA (compressor + pipeline), all
ternary, 559M params. Dolma re-tokenization. BIOS flash data. Evolutionary
mutation system. MLX quantized_matmul for ternary.
