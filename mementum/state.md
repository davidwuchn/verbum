# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-12 | Session: 089

## Where we are

**V11 baseline run reached 10K (continuing to 20K). Complete 1K→10K probe trajectory captured. Holographic loss implemented and verified. New run launched: v11-holo with holographic loss (λ=0.1) + 16 abstraction slots + 20% structured data. Hypothesis: holographic gradient slope (5×→1× across passes) + structured compositional pressure will activate B-dispatch and abstraction slots.**

Session 089 completed the pre-slot baseline, implemented holographic loss,
and launched the next experimental run.

## What was done this session

### 1. Complete v11 baseline probes (6K–10K)

Probed 5 new checkpoints with dispatch detail. Complete trajectory:

| Step | Loss | PPL | Compute Gate | K disp | B disp | B type | Alarm L0↑ |
|-----:|-----:|----:|------------:|-------:|-------:|-------:|----------:|
| 1K | 7.958 | 2859 | 0.000 | 62.3% | 1.9% | 6.9% | 2.000 |
| 5K | 7.642 | 2083 | 0.037 | 63.8% | 2.6% | 39.3% | 0.814 |
| 6K | 7.574 | 1948 | 0.512 | 62.3% | 1.6% | 45.0% | 0.754 |
| 8K | 7.543 | 1888 | 0.670 | 61.1% | 1.3% | 51.6% | 0.742 |
| 10K | 7.520 | 1845 | 0.706 | 58.7% | 1.4% | 51.9% | 0.624 |

Key findings:
- **Compute gate phase transition** at ~5.5K: 0→0.51 in ~1K steps
- **B paradox confirmed**: B dispatch flat at ~2% but B-type integrate
  at 52%. Composition happens in the FFN pathway, not dispatch.
- **Alarm cascade**: L0↑(0.62)→L1↑(1.38)→L2(1.71) — descending wave
  through ascending passes. System recognizes its own limitations.
- **CycleContinue dead** (0.018) across all 10K steps — confirmed.
- **Dispatch strongly specialized**: entropy 0.17 (normalized)
- **Evolution**: 3/200 accepted (1.5%)

### 2. Holographic loss — progressive intermediate decoding

Implemented holographic loss: 5 intermediate CE losses at pass boundaries.
Each pass must produce a decodeable representation through the shared
tied-embedding projection.

**Gradient slope from topology (not manual weighting):**
- Pass 0 (L0↑): gradient from 5 loss sources
- Pass 1 (L1↑): gradient from 4 sources
- Pass 2 (L2): gradient from 3 sources
- Pass 3 (L1↓): gradient from 2 sources
- Pass 4 (L0↓): gradient from 1 source

**Implementation:**
- `config.py`: `holo_lambda` (default 0.0 = disabled), warmup/ramp
  defaults to 0/0 (immediate activation — no warmup needed)
- `model.py`: progressive residual `x_embed + Σ_{i≤n} gate_i × delta_i`
  decoded through shared `output_norm + embed.output_proj`. Position
  subsampling (1/8) for cost reduction. Raw CE cached as `_last_ce`.
- `train.py`: `holo_schedule()`, logs both CE (prediction quality) and
  total_loss (what optimizer sees) when holo active. CLI: `--holo-lambda`
- `probe.py`: per-pass intermediate CE with gradient source count

**Verified on 10K checkpoint:**
- holo_lambda=0.0 → identical loss (backward compatible)
- Monotonic decrease: L0↑(65.4) → L1↑(35.6) → L2(30.7) → L1↓(30.7) → L0↓(25.4)
- Pass 0/final ratio: 2.58 (rough but not garbage — decodeable)

**Design insight:** holographic loss doesn't just add gradient — it forces
every pass boundary to produce representations that map back to token space
through the shared projection. This makes internal representations
interpretable and portable. Each pass must *mean something*, not just
produce opaque control signals for downstream passes.

### 3. New run launched: v11-holo

```bash
uv run python scripts/v11/train.py \
    --checkpoint-dir checkpoints/v11-holo \
    --total-steps 20000 \
    --holo-lambda 0.1 \
    --mix-ratio 0.2
```

Configuration: 16 abstraction slots + holographic loss (λ=0.1, immediate)
+ 20% structured data. Three simultaneous pressures:
- Holographic: gradient slope forces ascending arm to learn first
- Structured: compositional content provides B/slot activation pressure
- Slots: 16 learnable abstractions beyond KIBC for dispatch

## What to do next

### Priority 1: Monitor v11-holo run
Watch for early signals (first 2K steps):
- Per-pass intermediate CE cascade (should all decrease)
- CE vs total_loss divergence (how much holo contributes)
- Tok/s (should be ~4000+ with position subsampling)
- Alarm pass 0 response (gradient slope should relieve pressure)

### Priority 2: Probe v11-holo at 5K
Compare to baseline at same step:
- B dispatch activation (20% structured should help)
- Abstraction slot gates opening
- CycleContinue (main hypothesis)
- Intermediate CE improvement per pass
- Dispatch entropy (should differ from baseline pattern)

### Priority 3: Let baseline v11 run complete to 20K
The original run (no holo, no structured) continues unmodified.
Get 15K, 20K checkpoints for long-run baseline comparison.

### Priority 4: Pythia scaling — combinator differentiation
Run combinator probe on Pythia-410M and Pythia-1B to map where B
differentiates from K. If K-B correlation drops from 0.944 (160M)
toward 0.86 (32B) at some intermediate scale, that's the threshold.

### Priority 5: A3B cross-model probe
MoE routing may BE combinator dispatch.
128 experts = 128 pre-composed routing slots — direct existence proof.

### Carried
- B dispatch phase transition (watching in both runs)
- CycleContinue activation hypothesis (slots + holo may cause it)
- S5 reweight investigation (activated at 15K in v10-vsm)
- QK alignment decomposition probe (RoPE follow-up)
- Dead slot recycling (if gates < 0.01 for >2K steps → reinit)
- Domain banking (future: extract register banks from holographic model)

## VSM layer map (session 089 — v11 KIBC + algedonic + holographic)

```
Layer     Ascending Arm              Descending Arm                   Cross-arm
────────  ─────────────────────────  ───────────────────────────────  ──────────────────
S5        Token embeddings (tied)    Combinator embeddings (4: KIBC)  S5Reweight × AlgedonicAlert
                                     + 16 abstraction slot embeddings
S4        Register-query attention   Dual-view (resid + embeds)       Emphasis: regs → 4 combinators
                                                                      S4ProposalHead → slot modulation
S3        Per-pass phase gating ✓    Per-pass phase gating            Gate values → desc S4
          —                          CycleContinue (between cycles)   RMSNorm+tanh (s076 fix)
S2        Direction signals ✓        coherence modulation ✓           Found boundary 2→3
S1        prep → stride → consol.    [dispatch → stride → integ.] ×N  KIBC combinator basis
          (shared across 3 passes)   (shared across 2 passes × N cy)
Algedonic Reads prev desc regs       —                                + combinator weights (4+1)
          + combinator weights                                        EMA α=0.9
Alert     ← 48 health metrics ──────────────────────────────────────  → S5 gate modulation
          S3 gates, S2 conflicts, dispatch, compute, cycles,          [0,2] per pass, e2e diff.
          delta norms, suppression ratios, register norms             Beer's fire alarm ✓
Inject    —                          cycle_inject_gate (per cycle>0)  sigmoid(-4) ≈ 0.018 init
Holo      ← 5 intermediate CEs ────────────────────────────────────  → gradient slope 5×→1×
          progressive x_embed + Σ gate×delta through shared proj      pass 0 learns first
Logging   —                          —                                3× JSONL + alarm ✓
```

## Key files

| File | Purpose |
|------|---------|
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
| `checkpoints/v11/` | Baseline v11 run (no holo, no structured), continuing to 20K |
| `checkpoints/v11-holo/` | New run: holo λ=0.1, 20% structured, 16 slots |
| `mementum/knowledge/explore/holographic-inversion.md` | Design rationale + gradient structure |
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
