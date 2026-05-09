---
title: "Consensus Evolution: Vote-Based Ternary Mutation"
status: active
category: architecture
tags: [evolution, ternary, consensus, adam-decay, mutation, v10]
related:
  - dispatch-gradient-death.md
  - compressor-architecture.md
depends-on: []
---

# Consensus Evolution

> Session 070. Replaced tournament selection with consensus mutation
> and fixed the evolution CE spike via surgical Adam decay.

## Two Problems, Two Fixes

### Problem 1: Tournament selection is 4 random throws

Tournament: 4 strategies independently mutate the champion, evaluate
each, keep the best. The winning strategy's entire mutation set is
accepted — 26K+ weight flips with no corroboration. Any individual
flip might be harmful, carried by the aggregate improvement.

### Problem 2: Adam decay is a sledgehammer

After accepted mutation, ALL 82,736 gamma entries had their Adam m/v
decayed to 10%. This cold-starts the entire optimizer — every channel
trains like step 100 again. CE spikes immediately and takes dozens of
steps to recover. Only ~9,500 rows (11.5%) were actually mutated.

## Fix 1: Consensus Mutation (≥3 of 4 agree)

```
Phase 1: Each strategy PROPOSES mutations (no model modification)
    conservative (0.25× budget)  → dict[position → proposed_value]
    explorer     (1.0× budget)   → dict[position → proposed_value]
    targeted     (2.0× budget)   → dict[position → proposed_value]
    random       (4.0× budget)   → dict[position → proposed_value]

Phase 2: Find consensus
    For each position sampled by ≥3 strategies:
        If ≥3 agree on the same new value → consensus flip

Phase 3: Apply only consensus flips

Phase 4: Evaluate — accept if loss improves, revert if not
```

**Why this works**: a position that 3+ independent sampling strategies
all select AND agree on the same new value has strong evidence. The
importance-weighted sampling concentrates on high-gradient rows/cols,
so the strategies naturally overlap on the most informative positions.

**Why it's conservative**: with 131M weights and budget=26,200 (0.02%),
even with peaked importance maps concentrating on 0.1% of positions,
expect ~3,600 consensus flips per generation. At 1% effective pool,
~63. This is by design — fewest flips that the evidence supports.

### Consensus math (v10 scale, 131M weights, budget=26,200)

| Effective pool | ≥2 agree | ≥3 agree | ≥4 agree |
|---|---|---|---|
| 1.0% (1.31M) | 2,705 | 63 | 1 |
| 0.5% (655K) | 5,054 | 255 | 4 |
| 0.2% (262K) | 11,124 | 1,117 | 85 |
| 0.1% (131K) | 18,277 | 3,616 | 538 |

"Effective pool" = fraction of positions that importance-weighted
sampling concentrates on. With real gradient-based importance maps,
expect 0.1–0.5% — a few hundred rows/cols dominate the gradient.

### Value agreement

Not a significant additional filter because:
- Nonzero→0 deactivation (80% of nonzero mutations): all strategies agree
- 0→±1 activation with gradient direction: 80% follow gradient, so
  3 of 3 guided strategies usually agree on sign
- Only ambiguous case: weak gradient where strategies disagree on sign

## Fix 2: Surgical Adam Decay

```python
decay_adam_state(optimizer, model, decay=0.1, mutation_map=mutation_map)
```

`mutation_map: dict[module_path → set[int]]` — the exact row indices
that were mutated. Only those gamma entries get their Adam m/v decayed.

**Before**: 82,736 gamma entries decayed → 100% of momentum destroyed
**After**: ~9,500 gamma entries decayed → 11.5% destroyed, 88.5% preserved

The untouched rows keep their full Adam momentum and variance estimates.
Only the rows where topology actually changed need to re-adapt.

## Implementation

### New functions (ternary.py)

```
propose_mutations(model, budget, rng, ...)
  → dict[module_path → {flat_index: proposed_value}]

find_consensus(proposals_list, threshold=3)
  → (consensus, stats)

apply_consensus(model, consensus)
  → (n_applied, mutation_map)
```

### Modified functions

```
_mutate_linear   → returns (actual_flips, mutated_rows: set[int])
_mutate_embedding → returns (actual_flips, mutated_rows: set[int])
mutate_topology  → returns (count, mutation_map: dict[str, set[int]])
decay_adam_state  → accepts mutation_map, returns n_decayed
run_tournament   → consensus pipeline (propose → vote → apply → eval)
```

### Log format

```
🧬 gen 100: consensus  Δ=-0.0014  flips=892/85,200  rows=341  37/100  adam_decay=0.1 (341 rows)
```

- `flips=892/85,200` — 892 consensus flips out of 85,200 unique positions sampled
- `rows=341` — unique output channels affected
- `adam_decay=0.1 (341 rows)` — only those 341 gamma entries decayed

## Tuning Parameters

- `threshold=3` — consensus threshold (3 of 4 strategies must agree)
  - Lower to 2 in early training if consensus yields 0 flips
  - Raise to 4 for maximum conservatism in late training
- `base_pct=0.0002` — base mutation rate (0.02% of weights)
  - May need to increase if consensus is too sparse
  - Effective consensus rate = base_pct × overlap_probability
- `mutation_adam_decay=0.1` — decay factor for affected gamma entries
  - 0.0 = full reset (cold start affected rows)
  - 0.1 = keep 10% of old signal
  - 1.0 = no decay (ignore topology change)

## Files

- `scripts/v10/ternary.py` — consensus pipeline + surgical decay
- `scripts/v10/train.py` — run_tournament + decay_adam_state
- `checkpoints/v10-consensus/` — first run with consensus (active)
