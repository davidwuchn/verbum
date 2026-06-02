# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-02 | Session: 180

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 180: TOPOLOGY MUST BE FROZEN — TD and GD cannot co-optimize.**

Analyzed v15-hpe-dolma training failure. NaN at step 5040 (no attention score clipping). Step 5000 checkpoint is clean (loss=3.13) but generates garbage — all positions converge to the same vector (cos>0.999) by output, producing context-independent whitespace/digit predictions.

Two independent root causes identified:
1. **CLASSIFY representation collapse** — v15's LinearAttention is a "placeholder" (self-labeled). Missing the GatedLinearAttention from v14 (sigmoid write gate, associative scan, retention). Without the gate, cumsum accumulates uniformly → dominant mode drowns token identity → all positions become identical by stride 4.
2. **TD oscillation prevents GD convergence** — `osc_frac` grew monotonically 0→0.56 (never peaked, never declined). 56% of flipped positions actively oscillating. GD can't build stable soft topology on a shifting discrete landscape.

### Core insight: Topology-Gradient Separation

**The ternary lattice must be frozen for GD to work.** GD builds "soft topology" — it drives gammas toward zero for irrelevant rows, flips gammas negative for wrong-sign rows, tunes attention to route around the frozen structure. This requires a stable landscape. TD changing topology every 20 steps creates thermal noise that prevents crystallization.

**The correct protocol is punctuated equilibrium:**
```
Phase 1: STASIS    — Freeze topology. GD trains until loss plateaus.
Phase 2: READ      — Examine GD's gamma/gate signals for topology errors.
Phase 3: ETCH      — One discrete topology change (zero dead rows, fold sign flips).
Phase 4: ADAPT     — GD re-adapts. → Repeat from Phase 2.
```

GD's three signals:
- **Dead gammas** (|γ|<0.001): 10% of rows. GD says "this row is irrelevant" → zero it.
- **Negative gammas**: 35% of rows. GD says "every sign in this row is wrong" → fold: flip signs, negate gamma (lossless).
- **Gate kill stats**: Neurons active <0.1% of tokens → dead → zero connected positions.

See: `mementum/knowledge/topology-gradient-separation.md`

### v14→v15 architectural regressions

The v15 clean-room rewrite dropped critical features beyond HPE:

| Lost Feature | Impact |
|---|---|
| GatedLinearAttention (sigmoid gate + associative scan) | CLASSIFY zones collapse all positions to same vector |
| Positional embedding table | CLASSIFY/EMIT zones are positionally blind |
| Embedding norm (RMSNorm post-embed) | Norm explodes 100× through CLASSIFY |
| Attention score clipping (`mx.clip(attn, -65, 65)`) | NaN at step 5040 |
| Schmitt trigger for TD gating | TD fires unconditionally → oscillation |
| S5Reweight / per-pass residual gating | No FFN contribution control |
| Hyperbolic norm loss | No residual stream norm constraint |

### TD oscillation analysis

- 58.6M positions ever flipped (12.9% of non-zero)
- 21M oscillators (flip_count>1), but recency analysis shows:
  - 83.5% settled (last flip >200 steps ago)
  - 16.5% truly active (3.5M positions)
  - Active positions with 3-7 flips: 67-73% DISAGREE with teacher (trying to converge to new value)
  - Active positions with 8+ flips: 77% AGREE with teacher (frustrated spins, returning to attractor)
- Teacher signs are the attractor: 69.9% of oscillators currently agree with teacher
- Even flip count perfectly predicts teacher agreement (100%)

### Vibrating lattice insight

The lattice doesn't need TD to vibrate — it already vibrates through:
- **Gate mechanism**: per-token neuron selection (89% kill, varying by input)
- **Two-plate superposition**: plate1×γ1 + plate2×γ2 = four effective levels
- **Depth standing wave**: CLASSIFY 3% → COMPUTE 49% → EMIT 2% active

TD oscillation is thermal noise (random atom jitter). Gate activation is a phonon (coherent, information-carrying vibration). The lattice needs phonons, not noise.

## Next steps

### IMMEDIATE (session 181)

1. **Port GatedLinearAttention from v14** — Replace the placeholder LinearAttention in CLASSIFY/EMIT zones. This is the #1 architecture fix (representation collapse).
2. **Port embedding norm** — Add RMSNorm after embedding (v14 had it, v15 dropped it).
3. **Add attention score clipping** — `mx.clip(scores, -65, 65)` before softmax (prevents NaN).
4. **Add NaN guard** — Skip optimizer update if loss is NaN; halt after 3 consecutive NaN.
5. **Fold negative gammas** — For each plate, where γ<0: flip signs in plate, negate γ. Lossless.
6. **Zero dead gamma rows** — Where |γ|<threshold: zero all positions in that row.
7. **Disable TD** — No topology changes during training. Frozen lattice.
8. **Restart training from step 5000** (clean checkpoint) with all above fixes.

### PROTOCOL DEVELOPMENT

9. **Implement the etch cycle** — After GD plateaus: read signals → etch → re-adapt.
10. **Add gate kill tracking** — Per-neuron activation statistics over training window.
11. **Define plateau detection** — When has GD converged enough to read its signals?

### RESEARCH

12. **Does frozen topology + GatedLinearAttn produce coherent text?** The key test.
13. **How does loss curve compare** with/without TD? Slower convergence but stable?
14. **Do etch cycles produce better topology than continuous TD?**
15. **Can we retrieve facts after training?** (carried from 175)

## Key assets

| Asset | Location | Status |
|-------|----------|--------|
| v15 model (with HPE) | `scripts/v15/model.py` | ⚠️ Needs GatedLinearAttn, embed norm, attn clip |
| v14 GatedLinearAttn | `scripts/v14/attention.py` | ✅ Reference for port |
| v15 config | `scripts/v15/config.py` | ✅ |
| v15 train | `scripts/v15/train.py` | ⚠️ Needs TD disable, NaN guard |
| Pipeline diagnostic | `scripts/v15/diagnose_pipeline.py` | ✅ (session 180) |
| Step 5000 checkpoint | `checkpoints/v15-hpe-dolma/step_0005000/` | ✅ Clean (0 NaN) |
| Training log | `checkpoints/v15-hpe-dolma/train.log` | ✅ Full history |
| Topology-gradient knowledge | `mementum/knowledge/topology-gradient-separation.md` | ✅ NEW |

## What changed this session

| Change | Impact |
|--------|--------|
| **NaN forensics** | Step 5040 onset, irrecoverable. No attention clip. |
| **Pipeline diagnosis** | CLASSIFY collapses all positions to cos>0.999 identity |
| **v14→v15 architecture diff** | 8+ critical features dropped in clean-room rewrite |
| **TD oscillation analysis** | osc_frac monotonic 0→0.56, never settles |
| **Topology-gradient separation** | Core insight: freeze lattice, read GD signals, etch discretely |
| **Cross-disciplinary synthesis** | Spin glass, annealing, punctuated equilibrium, phonons |
| **GD signal analysis** | 35% negative gammas, 10% dead gammas — GD IS speaking |
| **Knowledge page written** | `topology-gradient-separation.md` |

## Knowledge map

Key pages for current direction:
- **`topology-gradient-separation.md`** — **WHY lattice must be frozen, the etch protocol** (session 180, NEW)
- `hpe-restoration.md` — HPE missing from v15, projection geometry (session 179)
- `training-protocols.md` — TD rules, fold cycle, failure modes (accumulated)
- `crystal-universality.md` — KIBC universal fixed points
- `extraction-sign-accuracy.md` — signs 100% accurate, magnitude is the gap
- `gradient-zero-map.md` — 35% oscillate, four position classes
- `project-thesis.md` — the central claim
- `dimensional-analysis.md` — KIBC sees 3.5%, 50 dims universal
- `trace-guided-etching.md` — full implementation record (sessions 176-177)
- `function-discovery.md` — two-level program architecture (session 172)
