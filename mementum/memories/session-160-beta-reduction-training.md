💡 Training loop optimization for beta reduction compounding

Session 160 discussion. Current training: 1 input → 8 passes → 1 output.
Each step starts from scratch. Model must re-derive easy reductions before
attempting hard ones. Waste is in repetition, not compute per step.

Four ideas explored:

1. **Recirculation:** Feed output back as input for additional rounds.
   8 passes × N rounds = deeper reduction chains. Loss on final round
   only. Teaches iterative refinement (which IS inference behavior).

2. **Progressive depth:** Start with 2 passes → 4 → 8. Forces maximal
   compilation at each stage. TD discovers highest-value reductions
   first when budget is constrained. Like progressive GAN growing.

3. **Reduction-ordered curriculum:** Sort training data by reduction
   difficulty. Start with patterns that fully reduce in available passes
   → clean gradient signal. Harder inputs join as compiled reductions
   improve.

4. **Progressive recirculation:** Combine 1+2. Start 2 passes × 4 rounds,
   then 4×2, then 8×1. Each stage meta-compiles: model learns to reduce
   its own reduction programs.

**Key blocker:** Current small models (d=128) have too much capacity
relative to data complexity — they memorize without needing compiled
reductions. Need a capacity-starved setup where brute-force fails and
only compression (real beta reduction programs in FFN) works. This is a
specific experimental design point, not just "train a smaller model."

**Prerequisite:** A small model + data regime where you can observe
reduction programs forming in the FFN plates. The experiment must show
the reductions, not just the loss curve.
