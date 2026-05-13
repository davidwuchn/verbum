# Holographic Inversion — VSM-LM v11

> Status: **validated** (session 090). All 4 training predictions confirmed.
> Ascending arm holographic, descending arm bottleneck identified. Run continuing.

## Context

```
project: ~/src/verbum/scripts/v11/
architecture: Tree of VSMs, 5-pass bidirectional (L0↑ L1↑ L2_apex L1↓ L0↓)
framework: MLX (Apple Silicon), ternary weights
files modified: model.py, config.py, train.py, probe.py
```

## The Inversion

```
λ invert(loss).
  CURRENT:  loss = CE(proj(x_embed + Σ_n gate_n × delta_n), targets)
            ∂L/∂delta_n = gate_n × ∂L/∂x_final                    # FLAT — all passes equal
  
  INVERTED: loss = CE_final + λ_holo × Σ_n CE(proj(x_embed + Σ_{i≤n} gate_i × delta_i), targets)
            ∂L/∂delta_n ∝ Σ_{m≥n} w_m × ∂L_m/∂x_m                # SLOPE — pass 0 strongest
  
  gradient_magnitude(pass_n) = N_PASSES - n                        # 5,4,3,2,1 with uniform weights
  | slope emerges from topology, not from manual weighting
  | uniform weights sufficient — the structural decay IS the sieve
```

## Implementation (session 089)

```
λ config(holo).
  holo_lambda: float = 0.0        # 0.0 = disabled (preserves existing behavior)
  holo_warmup_steps: int = 0      # 0 = immediate. No warmup needed —
  holo_ramp_steps: int = 0        #   the gradient slope helps from step 1.
                                   #   Either the structure helps or it doesn't.

λ forward(holo).
  WHERE: model.py forward(), AFTER existing CE loss + reg loss, BEFORE return
  
  # Position subsampling: 1/8 of B*L positions (unbiased gradient, 8× cheaper)
  holo_idx = mx.random.randint(0, B*L, (max(256, B*L // 8),))
  targets_sample = targets.reshape(-1)[holo_idx]
  
  x_progressive = x_embed                    # base hologram = raw embedding
  holo_loss = 0
  for n in range(5):
      x_progressive += effective_gates[n] * pass_deltas[n]
      x_sample = x_progressive.reshape(B*L, -1)[holo_idx]   # subsample positions
      logits_n = embed.output_proj(output_norm(x_sample))     # shared projection
      holo_loss += cross_entropy(logits_n, targets_sample).mean()
  loss += holo_lambda_effective * holo_loss
  
  # Raw CE cached as model._last_ce BEFORE holo/reg terms added
  # Train loop reads both: CE = prediction quality, total_loss = optimizer target

λ train(holo).
  def holo_schedule(step, cfg):
      if holo_lambda <= 0: return 0.0
      if step < warmup: return 0.0
      if ramp <= 0: return holo_lambda          # default: immediate
      return holo_lambda * min(1.0, (step - warmup) / ramp)
  
  model._holo_lambda_effective = holo_schedule(step, cfg)
  # Log: CE={raw_ce} loss={total_loss} when holo active
  # JSONL: both "ce" and "total_loss" fields
```

## Constraints

```
λ constraint(holographic).
  pass_boundary_only: holographic loss fires at 5 points (after each complete pass)
  | NOT at cycle boundaries within descending passes
  | KIBC cycles (IDENTIFY→RESOLVE→PRODUCE) are free to be partial reductions
  | only the pass OUTPUT (after all cycles) must decode coherently
  
  shared_projection: ALL intermediate decodes use the SAME output_proj + output_norm
  | no auxiliary heads — holographic property requires shared coherent projection
  | the tied embedding IS the reference beam
  
  progressive_residual: x_n = x_embed + Σ_{i≤n} effective_gate_i × delta_i
  | each pass ADDS to embedding, never replaces
  | embedding IS the base hologram
  
  existing_behavior_preserved: holo_lambda=0.0 → identical to current v11
  | no architectural changes needed — only loss computation changes
  | all existing modules (S3, S4, S5, KIBC, algedonic) unchanged
  
  position_subsampling: 1/8 of positions for intermediate logits
  | 512→151936 projection is the bottleneck (5× extra without subsampling)
  | unbiased gradient — same direction, just noisier
  | reduces holo overhead from 5.0× to ~0.63× of one full decode
```

## Gradient Structure (why it works)

```
λ gradient(slope).
  pass_0_gradient ∝ loss_0 + loss_1 + loss_2 + loss_3 + loss_4   # 5 sources
  pass_1_gradient ∝          loss_1 + loss_2 + loss_3 + loss_4   # 4 sources
  pass_2_gradient ∝                   loss_2 + loss_3 + loss_4   # 3 sources
  pass_3_gradient ∝                            loss_3 + loss_4   # 2 sources
  pass_4_gradient ∝                                     loss_4   # 1 source
  
  | ascending arm (passes 0-2) gets 3-5× gradient of descending arm (passes 3-4)
  | ascending learns FIRST — must produce coherent representation independently
  | descending learns to REFINE — contradiction is uphill in gradient landscape
  | S2 anti-oscillation becomes trivial — gradient already prevents fighting
  | register banks earlier in tree become most information-dense (gradient pressure)
  | bank_0 and bank_1_asc → highest gradient → most valuable for domain banking

λ gradient(components).
  S3_gates:    learn "does delta help NOW and downstream?" not just "does delta help final?"
  S5_reweight: each pass has own signal about intermediate quality
  KIBC:        descending arm gets weakest gradient → learns refinement, not foundation
  registers:   earlier banks get more gradient → become most dense → worth saving to disk
  algedonic:   alarm metrics include intermediate loss quality (future: add to metrics vector)
```

## The Subtle Feedback (session 089 insight)

```
λ feedback(holographic).
  without_holo: passes produce opaque internal signals
  | pass 0 can encode arbitrary control vectors only pass 4 knows how to read
  | representations are coupled — pass 0 output meaningless without pass 4
  
  with_holo: every pass boundary must map back to token space
  | representations forced to MEAN SOMETHING at every stage
  | pass 0 can't just produce "stuff that helps pass 4"
  | must produce decodeable prediction AND stuff that helps pass 4
  | internal structure becomes interpretable — each stage's "thinking" is readable
  
  alarm_compound: alarm system can now see WHERE prediction quality degrades
  | if pass 2 decodes worse than pass 1 → apex destroying information
  | decodability IS the ground truth, not statistics about norms/gates
  
  slot_compound: slot activation + intermediate decode improvement → proof of real work
  | slot activates AND that pass decodes better → slot does real composition
  | slot activates BUT decode unchanged → slot is noise
```

## Verification (session 089 static, session 090 experimental)

```
λ verified(holographic).
  STATIC (session 089, 10K baseline checkpoint):
  1. ✓ holo_lambda=0.0 → loss identical to current v11
  2. ✓ holo_lambda=0.1 → loss correctly increases (CE + 0.1 × Σ intermediates)
  3. ✓ monotonic decrease: L0↑(65.4) → L1↑(35.6) → L2(30.7) → L1↓(30.7) → L0↓(25.4)
  4. ✓ pass_0/final ratio: 2.58 (rough but not garbage — decodeable even untrained)
  5. ✓ gradient slope: pass_0 gets ∂ from 5 losses, pass_4 from 1 (by construction)
  
  EXPERIMENTAL (session 090, v11-holo 1K-7K):
  6. ✓ early passes produce non-garbage: L0↑ CE=8.39 at 7K (eval=7.71)
  7. ✓ S3 gate divergence: L0↑ prep=0.55, L1↑=0.21, L2=0.16 at 7K (clear hierarchy)
  8. ✓ intermediate CE cascade decreases: all passes improve monotonically 1K→7K
       (3K spike = temporary reorganization during compute gate awakening, recovered by 5K)
  9. ✓ early exit quality: ratio=0.99 at 7K (pass_0 BETTER than final output)
       exceeded prediction — ascending arm captures >100% of final quality
```

## First Experiment: v11-holo

```
config:
  checkpoint_dir: checkpoints/v11-holo
  total_steps: 20000
  holo_lambda: 0.1
  mix_ratio: 0.2                    # 20% structured data
  n_abstraction_slots: 16           # (default)
  holo_warmup_steps: 0              # immediate
  holo_ramp_steps: 0                # immediate

command:
  uv run python scripts/v11/train.py \
      --checkpoint-dir checkpoints/v11-holo \
      --total-steps 20000 \
      --holo-lambda 0.1 \
      --mix-ratio 0.2

watch_for:
  - per-pass intermediate CE decrease (cascade: pass_0 first, then pass_1, ...)
  - CE vs total_loss divergence (how much holo contributes vs prediction improvement)
  - alarm pass 0 relief (gradient slope should help the struggling ascending arm)
  - B dispatch activation (structured data provides compositional pressure)
  - abstraction slot gate opening
  - CycleContinue activation (main hypothesis: slots + holo gradient may wake it)
  - tok/s (should be ~4000+ with position subsampling)

baseline_comparison: checkpoints/v11/ (no holo, no structured, same architecture)
```

## Experimental Findings (session 090, v11-holo 1K-7K)

### B-type acceleration: 5× ahead of baseline

B-type integration reached 59% at step 2K. Baseline didn't reach 52% until
step 10K. Holographic gradient forces the integration pathway to compose —
B(f,g,x) = f(g(x)) is the cheapest way to improve intermediate decodability.

The B paradox persists: B dispatch stays flat at ~2% while B-type dominates
integration at 55-62%. Composition happens in the FFN pathway regardless of
which combinator was dispatched.

### Compute gate: earlier and smoother transition

Baseline: dormant until ~5.5K, then 0→0.51 in ~500 steps (sharp phase transition).
Holo: gradual ramp 3K→5K, reaching 0.49 at 7K with 44% of positions >0.5.
Smoother because gradient comes from multiple passes, not just final output.

### Holographic ratio inversion: ascending > final at 7K

```
ratio trajectory: 1.22 → 1.10 → 1.25 → 1.17 → 1.15 → 1.03 → 0.99
                   1K     2K     3K     4K     5K     6K     7K

7K pass structure:
  L0↑: 8.39 → L1↑: 7.95 → L2: 7.87 → L1↓: 8.40 → L0↓: 8.47
                                BEST         ← descending DEGRADES
```

Ascending arm produces BETTER decodable representations than the full model
output. The apex (L2) is best at 7.87. The descending arm actively hurts
the representation — each descending pass adds noise.

### Descending arm bottleneck: kernel integration gap

The descending arm's architecture: stride_stack → kernel_integration (KIBC).
The stride stack must prepare representations that the kernel combinators
can act on productively. Currently it doesn't — B-composition fires on
poorly prepared inputs, degrading rather than refining.

Evidence:
- L1↓ integration gate closing defensively (0.884, trending down)
- Holographic CE increases through descending passes (7.87 → 8.40 → 8.47)
- L1↓ alarm coming off ceiling (2.0 → 1.86) = system beginning to address

Prediction: loss plateau while descending arm builds pressure, then drop
when it learns to prepare representations for kernel consumption.

### Phased structural discovery

Training proceeds as a staircase, not smooth descent:
- Phase 1 (0-2K): Raw capacity (K+B via FFN, structure ignored)
- Phase 2 (2K-3K): Plateau → reorganization (holo makes plateau intolerable)
- Phase 3 (3K-5K): Structural cascade (compute gate → C-dispatch → S3 → φ)
- Phase 4 (5K-7K): Ascending arm mastered, descending arm bottleneck
- Phase 4b (7K-?K, predicted): Descending arm pressure builds
- Phase 5 (?K, predicted): Descending arm discovers kernel, loss drops

Each phase = capacity exhaustion forces discovery of next VSM layer.
Holographic loss accelerates transitions by making plateaus intolerable —
every pass graded independently, can't hide a bad L0↑ behind a good L0↓.

### φ-compression convergence

Ascending arm converges on golden ratio compression:
- L1↑ φ-dev: 5.68 (1K) → 0.072 (7K) — near-perfect 1/φ
- L0↑ φ-dev: 0.461 (1K) → 0.158 (7K) — converging
- L2 φ-dev: 19.7 (3K) → 0.157 (7K) — converging

Descending arm chaotic (L1↓ φ-dev=3.0 at 7K), consistent with
reorganization during kernel integration learning.

## Future: Domain Banking (not implemented yet, design only)

```
λ domain(bank).
  extract: run domain corpus → capture register banks + slot embeddings → average → save
  format:  6 banks × 3 registers × 256 dims + 16 slots × 512 dims = ~50KB per domain
  load:    override register_inits + slot_embeddings → domain-specialized inference
  route:   S4 cross-attention already selects relevant banks → multiple domains loadable
  
  | requires holographic property: banks must be independently meaningful to be portable
  | without holographic loss, banks are opaque control vectors tied to specific training run
  | with holographic loss, banks ARE compressed domain representations in embedding space
```
