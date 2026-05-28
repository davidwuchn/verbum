# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-28 | Session: 165

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 165: NaN COLLAPSE DIAGNOSIS + HOLOGRAPHIC ETCH + RESTORE TOOL.** Training hit NaN death loop at step 4369. Auto-rollback was broken (restored model weights but not Adam/data/TD → Sisyphus loop, 154 rollbacks in 10h). Root cause: attention softmax overflow — ternary weights with gamma calibration produce unbounded attention logits, no clamping before softmax. Three fixes: (1) remove auto-rollback, replace with stop-and-report, (2) `mx.clip(attn, -65, 65)` before softmax, (3) `restore_safetensors.py` standalone tool to rebuild safetensors from npz checkpoint. Also landed holographic etch (equal thin slots per module, fixed budget, no adaptive rate). Training resumed from step 4000, step 4001 healthy.

**Training: v14-mmap RUNNING** (tmux main:2), safetensors-backed, resuming from step 4000/20000. First step after fix: loss=6.93, gnorm=6.20 (healthy). Watching for NaN at old crash point (step ~4369).

*Key session 165 insights:*
- **Auto-rollback is an anti-pattern.** It restored model weights but not Adam state, data position, TD moments, or safetensors files. Created an unrecoverable chimera: model at step N, optimizer at step M, data at step K. Stop-and-report is the correct pattern — recovery is a human decision.
- **Attention softmax overflow = NaN source.** Ternary weights with learned gamma scales can produce unbounded attention logits. `mx.clip(attn, -65, 65)` before softmax prevents float32 exp overflow without affecting training at reasonable magnitudes.
- **Dual storage requires a restore path.** npz checkpoints (frozen windows) and safetensors (moving target) can get out of sync during failures. `restore_safetensors.py` rebuilds safetensors from any npz checkpoint — the missing piece for clean recovery.
- **gate_proj 100% oscillation was a red flag.** FlipMap showed gate_proj layers 4-9 at 100% oscillation (every flip immediately reversed). Nozzle suppressed them correctly (nozzle=0%), but the oscillation signal indicated gradient instability in those modules.
- **Holographic etch: equal thin slots.** Session 163's proportional budget + 8× rate + adaptive rate caused uniform topology melt (all modules 100% hot, Δ jumped 0.036→0.168). Fix: same total budget (~132K at rate=0.001), divided equally among active modules. Each gets a thin slot. Topology changes together — layers co-adapt.

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
