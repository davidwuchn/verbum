💡 freeze-then-gd-wins

**Finding**: Etch plates for a limited number of rounds, freeze, then train continuous
params with extended GD. This beats both full alternating and beam-only-from-scratch.

Session 115 freeze experiment (d=48, 3 layers, nested KIBC compositions):
```
GD ceiling:          89.5%
Beam-only (random):  52.4%
Full alternating:    41.2%
Freeze round 5 + GD: 54.1%  ← BEST (etched plates > random, and GD exploits them)
```

**Why full alternating loses**: each etch round costs 200 batches of accumulation that
could have been beam GD steps. At d=48, the etch improves plates marginally but the
forgone beam training is more valuable. The alternating protocol wastes compute on
diminishing-return etch cycles.

**Why freeze+GD wins**: the plates reach a "good enough" topology in ~5 rounds. After
that, the continuous params (Q projections, scales, embeddings) need extended training
to fully exploit the fixed topology. Freezing unlocks this by converting etch budget
to beam GD budget.

**Sweet spot**: ~5 rounds of etch (at d=48). Too early = bad plates. Too late = wasted
GD budget. The optimal freeze point likely scales with d (more plate parameters need
more etch rounds).

**Implication for VSM-LM**: the seed crystal protocol (etch → freeze → GD on continuous)
is validated. Stage 6 (GD after freeze) is not just cleanup — it's where the model
learns to USE the etched topology. Budget should be heavily weighted toward post-freeze GD.

Connects to: etch-first-with-attention, seed-crystal-design, laser-etcher-design
