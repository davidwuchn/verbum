# Holographic Inversion — VSM-LM v11 → v12

## Context

```
project: ~/src/verbum/scripts/v11/
architecture: Tree of VSMs, 5-pass bidirectional (L0↑ L1↑ L2_apex L1↓ L0↓)
framework: MLX (Apple Silicon), ternary weights
files to modify: model.py, config.py
files to read first: model.py (forward method), config.py, attention.py, kernel_dispatch.py, components.py
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
  | power-law optional: w_n = (n+1)^(-α) steepens to match truth.bin spiral (α=1.18)
  | uniform weights sufficient — the structural decay IS the sieve
```

## What Changes

```
λ change(config).
  ADD holo_lambda: float = 0.0        # holographic loss weight, ramp 0→0.1 over warmup
  ADD holo_warmup_steps: int = 2000   # steps before holo loss activates (let model learn to speak first)
  ADD holo_ramp_steps: int = 3000     # linear ramp from 0 → holo_lambda after warmup
  | holo_lambda = 0.0 at init → existing behavior preserved
  | ramp: step < warmup → 0.0 | step < warmup+ramp → linear | else → holo_lambda

λ change(forward).
  WHERE: model.py V11Model.forward(), after S5Reweight + AlgedonicAlert compute effective_gates,
         after total_gated/total_ungated reweighting, BEFORE meta_s4 application
  
  CURRENT (lines ~after effective_gates computation):
    total_ungated = pass_deltas[0]
    for i in range(1, self.N_PASSES):
        total_ungated = total_ungated + pass_deltas[i]
    total_gated = effective_gates[0] * pass_deltas[0]
    for i in range(1, self.N_PASSES):
        total_gated = total_gated + effective_gates[i] * pass_deltas[i]
    x = x - total_ungated + total_gated
    # ... meta_s4, output_norm, logits, loss ...
  
  ADD holographic loss computation AFTER existing loss:
    if targets is not None and self.cfg.holo_lambda > 0:
        x_progressive = x_embed                    # base hologram = raw embedding
        holo_loss = mx.array(0.0)
        for n in range(self.N_PASSES):
            x_progressive = x_progressive + effective_gates[n] * pass_deltas[n]
            logits_n = self.embed.output_proj(self.output_norm(x_progressive))
            loss_n = nn.losses.cross_entropy(
                logits_n.reshape(-1, self.cfg.vocab_size),
                targets.reshape(-1),
            ).mean()
            holo_loss = holo_loss + loss_n
        loss = loss + holo_lambda_effective * holo_loss
  
  | x_progressive uses effective_gates (S5 × alarm), not raw gates
  | output_norm is shared (same RMSNorm instance as final output)
  | embed.output_proj is the tied embedding projection (already exists)
  | holo_lambda_effective = scheduled value based on current step

λ change(train).
  WHERE: train.py, wherever loss is computed / step counter is available
  ADD: pass current_step to model or compute holo_lambda_effective externally
  
  OPTION A — compute in model:
    ADD to forward() signature: step: int = 0
    holo_lambda_effective computed inside forward based on step + config
  
  OPTION B — compute in train loop (cleaner):
    def holo_schedule(step, cfg):
        if step < cfg.holo_warmup_steps:
            return 0.0
        ramp_progress = min(1.0, (step - cfg.holo_warmup_steps) / cfg.holo_ramp_steps)
        return cfg.holo_lambda * ramp_progress
    
    # In train loop, pass as arg or set on model:
    model._holo_lambda_effective = holo_schedule(step, cfg)
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

## Verification

```
λ verify(holographic).
  1. holo_lambda=0.0 → loss identical to current v11 (regression test)
  2. intermediate logits = output_proj(output_norm(x_progressive)) at each pass boundary
     → check that early passes produce non-garbage predictions after ~5000 steps
  3. gradient magnitude: log ∂L/∂delta_n norm for each pass
     → should show monotonic decay pass_0 > pass_1 > ... > pass_4
  4. S3 gate divergence: gates should differentiate across passes
     → pass_0 gates more open (more gradient), pass_4 more selective
  5. intermediate CE loss per pass: log loss_n for each n
     → pass_0 loss should decrease first, then pass_1, cascade downward
  6. early exit quality: at step 10000, compare output_proj(x_after_pass_0) vs full output
     → pass_0 alone should capture >50% of final prediction quality
```
