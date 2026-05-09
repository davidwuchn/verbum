# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-09 | Session: 073

## Where we are

**VSM structural overhaul. 7 architectural changes to complete Beer's model. Training pending restart.**

Session 073 examined v10's VSM layer mapping against Beer (1972) and found gaps:
S2 was implicit/missing, MetaS3 was misplaced (should be S5), the descending arm's
S4 couldn't see original embeddings, S3 gate decisions didn't flow between arms,
kernel compute was invisible to the ascending arm, op embeddings were static when
S4 should modulate them, and S4 had no voice in evolution. All seven were fixed.

These are architectural changes that require a fresh training run from step 0.
The v10-topk run (which was at step 3K) used the pre-session-073 architecture.

## What was done this session

### 1. S2 Coordinator — anti-oscillation (NEW, was missing)
Beer's S2 prevents oscillation between S1 units. v10 had no explicit S2.
Added `S2Coordinator` in components.py:
- After each pass, computes a small direction signal (projected through TernaryLinear, ~0.01 scale)
- Feeds forward to the next pass's input: "Pass N moved THIS way"
- `coherence_factor()`: differentiable `1 + cos(prev, curr)` modulates signal strength
  - Agreement (cos=+1) → factor 2.0 → amplify signal
  - Conflict (cos=-1) → factor 0.0 → fully dampened
  - stop_gradient on prev delta (earlier pass sets direction, later learns to align)
- `conflict_score()`: diagnostic cosine similarity for instrumentation
- 4 transitions between 5 passes, learnable scales, gamma init ×0.01

### 2. S5Reweight — replaces MetaS3 with proper S5 positioning
MetaS3 only saw register banks (S2/S3-filtered). S5 needs ungated operational view.
- `_run_level_pass` now returns raw (ungated) phase deltas as 4th element
  - Each phase's `delta = phase_out - x` captured before S3 gating
  - Sum of 3 raw phase deltas = what S1 proposed, unfiltered
- `S5Reweight` takes both register banks AND raw deltas
  - Projects raw deltas through TernaryLinear (16 features/pass) 
  - Combined with register features → per-pass sigmoid gates
- A pass that S3 suppresses is still visible to S5 through its raw delta

### 3. Descending S4 dual view — sees original embeddings
By pass 3-4, compression has buried token identity under 3 transformation passes.
- Captures `x_embed = x` after embedding, before any passes
- Descending S4 attends over `concat(residual, x_embed)` along L dim (2L positions)
- Ascending S4 unchanged (sees near-embedding state naturally)
- Zero new parameters — S4Ternary handles variable L transparently

### 4. Kernel compute algedonic — dispatch/gate visible to ascending arm
The kernel's dispatch weights and compute gate were invisible after the forward pass.
- Packs mean dispatch weights (22 dims) + mean compute gate (1 dim) into register-shaped vector
- EMA-smoothed (α=0.9) across forward passes, same as register algedonic
- Added as additional readable bank for all 3 ascending passes
- No projection — S4's existing q_proj learns what to extract

### 5. Ascending S3 gates → descending arm
Ascending arm's S3 decisions (9 gate values: 3 passes × 3 phases) were invisible to descending.
- `_run_level_pass` now returns phase gate values as 5th element
- Ascending gates packed into register-shaped vector, added to descending readable banks
- NOT stop_gradient: gradient flows back to ascending S3, teaching it that gate decisions affect downstream dispatch

### 6. Op emphasis — S4 register state modulates kernel identity
Op embeddings were static. S4 should modulate which ops are emphasized.
- `emphasis_proj` (nn.Linear, zero-init → neutral start) maps ascending register state to 22 per-op values
- `1.0 + 0.5 * tanh(...)` → range [0.5, 1.5] — amplify or suppress, never kill
- Applied to L2-normalized op embeddings in KernelDispatch before routing
- EMA-tracked (α=0.95) across steps — slowly shifting landscape, not noise
- Gradient flows: loss → dispatch → modulated embeddings → emphasis_proj → register state → S4

### 7. Intelligence evolution strategy — S4→S5 proposals
S4 had no voice in topology evolution. In Beer's VSM, S4 proposes to S5.
- 5th mutation strategy "intelligence" (budget 0.5×, `guided_fraction=1.0`)
- Amplifies S4 module importance by `s4_boost` (default 3.0×), suppresses non-S4
- Participates in consensus (needs ≥3 of 5 strategies to agree)
- Configurable: `--s4-boost` on CLI

## What to do next

### Priority 1: Start fresh v10 training run with session-073 architecture
All 7 changes are architectural — requires training from step 0.
- New checkpoint dir to distinguish from v10-topk (pre-073)
- Same hyperparameters as v10-topk (proven to work)
- Watch first 500 steps for stability (S2, emphasis, new algedonic signals)

### Priority 2: Early stability probes (steps 250, 500, 1000)
The S2 coherence modulation and S3 gate signaling create new feedback paths.
Key signals:
- **S2 conflict scores**: should start random, trend toward positive as passes learn coherence
- **S5 reweight gates**: should differentiate (not all ~0.12 forever)
- **Op emphasis range**: should start at 1.0 (neutral), slowly differentiate
- **L2_apex ratio**: should NOT explode (algedonic + S2 should prevent it)
- **Loss trajectory**: should match or beat v10-topk baseline

### Priority 3: Probe compute gate + emphasis interaction
The op emphasis may accelerate compute gate opening:
- Emphasis on arithmetic ops → stronger modulation → clearer gradient for gate
- Watch for gate active fraction > 1% within first 3K steps (was 0.012% before)

### Priority 4: Monitor S4→S5 evolution proposals
The intelligence strategy adds a 5th voice to consensus mutation:
- Track how often intelligence strategy agrees with others
- Track which S4 modules get the most proposed flips
- If acceptance rate is very low, consider adjusting s4_boost or budget scale

## VSM layer map (session 073, complete)

```
Layer     Ascending Arm              Descending Arm              Cross-arm
────────  ─────────────────────────  ──────────────────────────  ──────────────────
S5        Token embeddings (tied)    Op embeddings × emphasis    S5Reweight (raw deltas)
S4        Register-query attention   Dual-view (resid + embeds)  Emphasis: regs → per-op
S3        Per-pass phase gating      Per-pass phase gating       Gate values → desc S4
S2        Direction signals + coherence modulation               Both arms
S1        prep → stride → consol.    dispatch → stride → integ.  —
Algedonic Reads prev desc regs       —                           + kernel compute
          + kernel compute                                       EMA α=0.9
Evolution                            S4→S5 intelligence strategy (5th voice in consensus)
```

## Key files

| File | Purpose |
|------|---------|
| `scripts/v10/components.py` | S4, S3, MetaS4, MetaS3, **S5Reweight**, **S2Coordinator** |
| `scripts/v10/kernel_dispatch.py` | KernelDispatch (top-k + **op_emphasis**), KernelIntegrate |
| `scripts/v10/model.py` | Tree of VSMs — all 7 session-073 changes integrated |
| `scripts/v10/train.py` | Training loop + **intelligence strategy** + S2/S5 metrics |
| `scripts/v10/config.py` | Config + **s4_boost** parameter |
| `scripts/v10/kernel.py` | Ground-truth kernel evaluator (22 ops, 5 types) |
| `scripts/v10/ternary.py` | Ternary substrate + consensus mutation pipeline |

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
