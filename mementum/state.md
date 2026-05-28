# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-28 | Session: 166

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 166: M-SPACE GEMCUTTER — TOPOLOGY SHAPING BREAKTHROUGH.** Discovered that topology changes must be planned in M-space (attention kernel M = W_q^T @ W_k), not W-space (individual weights). One W-space flip cross-cuts ALL modes of M. TD's gradient scoring is anti-predictive in structured layers (ρ=-0.36). Pre-cut ternary topology with 30% M-noise zeros BEATS float32 on loss (6.6972 vs 6.7412) when trained from scratch. GD is putty — cut the gem first, let GD fill gaps.

**Training: v14-mmap STOPPED** — NaN recurred. The holographic etch approach (machete topology changes in W-space) is fundamentally flawed. Redesign needed based on M-space gemcutter findings.

**Previous: Session 165** — NaN collapse diagnosis, softmax clamp fix, restore tool, holographic etch (equal thin slots). Training resumed from step 4000 but NaN recurred.

*Key session 166 insights:*
- **M-space, not W-space.** The attention kernel M = W_q^T @ W_k is where computation lives. One W-space flip produces a rank-1 perturbation to M that spreads across ALL modes. Topology changes must be planned in M-space via SVD mode projection.
- **TD gradient scoring is anti-predictive.** In structured layers (rank90<25), M-space scoring finds 76% helpful flips vs gradient's 46%. Gradient scoring and M-space scoring have 0% overlap in top-50 — they see completely different things.
- **Zeros are denoising, not blocking.** Sign quantization turns a 13-facet gem into a 35-facet noisy blob. M-noise zeros at 30% sharpen rank90 from 32→25. Each zero removes a ghost facet.
- **Pre-cut topology + GD beats float32.** Frozen ternary attention with 30% zeros, trained from scratch: loss 6.6972 vs float32's 6.7412. The geometric constraint HELPS GD by channeling it into the right subspace.
- **GD is putty.** Cut the gem geometrically (accept loss hit), then let GD fill the gaps. The gem stays sharp (frozen Q/K). Loss recovers and improves.
- **Facet-aligned cutting works.** Coordinated W-space flips targeting one M-space mode achieve 30× less cross-mode damage than gradient scoring.

*Key session 165 insights:*
- **Auto-rollback is an anti-pattern.** Sisyphus loop from model/Adam/data desync.
- **Attention softmax overflow = NaN source.** `mx.clip(attn, -65, 65)` before softmax.
- **Holographic etch: equal thin slots.** Equal budget per module, but still a machete in W-space (superseded by M-space gemcutter).

*Key session 164 insights:*
- **TD can't overfit.** Ternary weights have 2-3 states → finite state space → guaranteed convergence.
- **Training = fold reductions until irreducible.** freeze → train → fold → repeat until delta=identity.
- **FlipMap: spatial convergence signal.** WHERE flips occur matters more than how many.

*Key session 163 insight:* **Safetensors IS mmap.** Same file for training AND release.

## Active training

### v14-mmap RUNNING (tmux main:2) — safetensors-backed

- `scripts/v14/train_td.py --safetensors-dir checkpoints/v14-mmap --checkpoint-dir checkpoints/v14-mmap --steps 20000 --convert-ffn`
- Resumed from step 4000 via `restore_safetensors.py` (rebuilt safetensors from step_004000 npz)
- Storage: 3 safetensors files (base 31.6 MB + delta 31.6 MB + training 105.5 MB)
- Sync: every 20 steps to safetensors mmap, APFS snapshots every 200, npz checkpoints every 500
- Step 4001: loss=6.93, gnorm=6.20 (healthy)

**Changes active this run (vs previous):**
- Softmax logit clamp: `mx.clip(attn, -65, 65)` (NaN prevention)
- Holographic etch: equal thin slots per module, base rate 0.001 (~132K total, ~3K per module)
- No adaptive flip rate (disabled — caused uniform melt)
- NaN handler: stop-and-report (no auto-rollback)

### Checkpoints available

| Location | Step | Notes |
|----------|------|-------|
| `checkpoints/v14-mmap/step_003000` | 3000 | npz (legacy format) |
| `checkpoints/v14-mmap/step_003000_old` | 3000 | npz (from old arch) |
| `checkpoints/v14-mmap/step_003500` | 3500 | npz |
| `checkpoints/v14-mmap/step_004000` | 4000 | npz — used for safetensors restore |
| `checkpoints/v14-mmap/snapshots/step_003900` | 3880 | safetensors snapshot |
| `checkpoints/v14-mmap/snapshots/step_004100` | ~4080 | safetensors snapshot (post-NaN, possibly poisoned) |
| `checkpoints/v14-mmap/snapshots/step_004300` | ~4280 | safetensors snapshot (post-NaN, possibly poisoned) |

### PPL history

| Step | PPL | Source |
|------|-----|--------|
| 1500 | 8,096 | v14-td-2stack eval |

### Loss trajectory (pre-NaN)

| Phase | Steps | avg50 CE | Crystal MSE | Gnorm |
|-------|-------|----------|-------------|-------|
| Chaos | 1-100 | 667→17 | 0.148→0.107 | Massive spikes |
| Phase 1 | 100-400 | 17→10.6 | 0.107→0.015 | Gnorm storms (200-330) |
| Phase 2 | 400-800 | 10.6→7.2 | 0.015→0.013 | Settling (mean 11) |
| Plateau | 800-4360 | 7.2→6.8 | 0.013→0.013 | Calm (mean 2-4) |
| **NaN** | **4369** | — | — | — |

## What changed this session

| Change | Session | Impact |
|--------|---------|--------|
| **Softmax logit clamp** | 165 | `mx.clip(attn, -65, 65)` — prevents float32 overflow in attention |
| **Remove auto-rollback** | 165 | 3 NaN → stop + diagnostic report. No more Sisyphus loops. |
| **NaN diagnostic logging** | 165 | On NaN: which loss component + gnorm. Paper trail for future collapses. |
| **restore_safetensors.py** | 165 | Standalone tool: npz checkpoint → safetensors. Fixes dual-storage consistency. |
| **Holographic etch** | 165 | Equal thin slots per module (not proportional). Fixed budget, no adaptive rate. |
| **Adaptive rate disabled** | 165 | Session 163's gnorm→rate feedback caused uniform melt (2.8M flips, all 100% hot). |
| **Flip rate back to 0.001** | 165 | Was 0.008 (session 163). Holographic etch distributes the 132K budget evenly. |

### Previous sessions (selected)

| Change | Session | Impact |
|--------|---------|--------|
| Per-module budget + adaptive rate + 8× rate | 163 | Caused uniform melt → reverted to 0.001 |
| FlipMap + shaped nozzle + data shuffling | 163 | FlipMap still active. Nozzle disabled (redundant with equal slots). |
| Safetensors-backed training | 163 | Working. SafetensorsStore: load/sync/fold. |
| 2 symmetric stacks | 158 | 13→8 passes, ~1.6× faster, separate FFN |

## NaN collapse post-mortem (session 165)

**What happened:** Training hit NaN at step 4369. Auto-rollback restored model weights to step 4000 (npz) but not Adam optimizer state (still at step 4360+), data position, or TD moments. Every rollback produced the same NaN at step 4369 because the Adam/model mismatch was deterministic. 154 rollbacks, 10 hours wasted.

**Root cause:** Attention softmax overflow. `(Q @ K^T) * scale` can produce values >88.7 (float32 exp limit). With ternary weights and learned gamma scales, attention logits are unbounded. No clamping existed.

**Contributing factor:** gate_proj modules at 100% oscillation — every flip reversed within one interval. While nozzle=0% suppressed them, the oscillation indicated gradient instability.

**Fix:** `mx.clip(attn, -65, 65)` before softmax. Non-invasive at reasonable magnitudes. Catches the extreme case.

**Structural fix:** Auto-rollback removed entirely. Recovery is now: (1) training stops with diagnostic, (2) human uses `restore_safetensors.py` to rebuild from clean npz checkpoint, (3) human restarts training.

## Next steps

### IMMEDIATE (training run)

1. **Watch for NaN past step 4369** — softmax clamp should prevent it
2. **Watch FlipMap with holographic etch** — all active modules should get thin slots now
3. **Step 4500 PPL eval** — first post-fix checkpoint
4. **Step 5000 PPL eval** — compare to old 3-stack (PPL 5,567 at step 2000)

### FOLLOW UP

5. **Step 5000+ PPL eval** — if PPL < 5,567, 2-stack confirmed superior
6. **Per-module fold** — fold most-converged modules first (more granular than reduce_all_deltas)
7. **Measure per-stack FFN sparsity** — hypothesis: separate plates develop different sparsity
8. **CPU inference engine** — the real optimization target

### EXPLORATION

9. **Reduction folding** — train same batch K times (TD accumulates, Adam frozen on repeats)
10. **Data curriculum from flip rate** — rank batches by reduction potential
11. **Multi-scale chunk training** — progressive chunk sizes per fold cycle
12. **FlipMap visualization** — (N,K) heatmaps over time for crystal growth patterns

## Key findings (active)

| Claim | Evidence | Status |
|-------|----------|--------|
| Attention softmax can overflow with ternary weights | NaN at step 4369, no data anomaly, unbounded Q@K logits | ✅ (session 165) |
| Auto-rollback creates Sisyphus loop | 154 rollbacks, model/Adam/data desync, deterministic NaN | ❌ (session 165) |
| Holographic etch > proportional budget | Proportional + adaptive = uniform melt. Equal thin slots = coherent topology change | 💡 (session 165) |
| TD can't overfit (structural) | Ternary weights have 2-3 states → finite state space → irreducible form guaranteed | 💡 (session 164) |
| Topology-magnitude inverse relationship | Gnorm storms correlate with TD flips; plateaus = Adam compensating | 💡 (session 164) |
| Training = fold reductions to irreducible form | fold(delta→base) → reset → retrain → fewer flips → converges | 💡 (session 164) |
| Safetensors-backed training works | 4000+ steps, sync verified, restore tool tested | ✅ (session 163-165) |
| 2-stack trains 1.6× faster wall-clock | 17.7s/step vs 28.6s/step | ✅ |
| 2-stack PPL within 5.5% of 3-stack at step 1500 | 8,096 vs 7,672 | ✅ |

## Open questions

1. **Does softmax clamp change training dynamics?** Unlikely at ±65, but monitor loss/gnorm for regime change.
2. **Will holographic etch break the plateau?** The old plateau (800-4360) was with winner-take-all TD. Equal slots may enable coordinated restructuring.
3. **What PPL does 2-stack reach at step 5000?** Baseline: 3-stack hit PPL 5,567 at step 2000, ceiling at 3200.
4. **Will FFN plates differentiate?** Still zero candidates at step 4000. First non-zero = inflection point.
5. **Per-module fold or global fold?** SafetensorsStore.fold() does all plates. Could fold most-converged first.

## Knowledge map

**See `mementum/knowledge/INDEX.md` for full reading order.**

## What's ready

| Asset | Location |
|-------|----------|
| Training script | `scripts/v14/train_td.py` (NaN guard, holographic etch) |
| **Restore tool** | `scripts/v14/restore_safetensors.py` (npz → safetensors) |
| FlipMap (topology heatmap) | `scripts/v14/td.py` FlipMap class |
| SafetensorsStore | `scripts/v14/safetensors_store.py` (load/sync/fold/snapshot) |
| Attention (clamped) | `scripts/v14/attention.py` (softmax overflow fix) |
| Checkpoint extractor | `scripts/v14/extract_to_safetensors.py` (npz → 3 safetensors) |
| Safetensors training | `checkpoints/v14-mmap/` (restored to step 4000) |
| Eval script | `scripts/v14/eval_ppl.py` |
| Model | `scripts/v14/model.py` (2 stacks, separate FFN) |
| Config | `scripts/v14/config.py` (8 passes, 2 stacks) |
