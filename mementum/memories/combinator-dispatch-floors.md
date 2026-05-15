🎯 combinator-dispatch-floors

Dispatch emphasis (S4) can crush combinators to near-zero — V12-run1 killed I
from 13.4% to 0.5% in one eval window (step 3000→3500) by flipping emphasis
bias from +1.44 to -1.88. The dispatch entropy regularizer fires but gradient
doesn't flow strongly enough to S4's emphasis pathway to prevent it.

**Design direction**: enforce minimum dispatch floors per combinator, derived from
the universal cross-model ordering (session 093, 9 models, 2 architectures):

```
B ≥ K ≥ C >> I    (invariant across Pythia-70M through Qwen3-32B)
```

The floors should reflect empirical ratios observed in production LLMs — what the
model naturally WANTS to do. The emphasis/alarm system then operates ABOVE the
floor, not below it. This is Beer's variety law: the controller shouldn't be able
to eliminate a viable subsystem.

Implementation options (to evaluate at V12 5K+ checkpoint):
1. Hard floor via clamped softmax (floor + (1-sum_floors) × softmax)
2. Soft floor via penalty term (like dispatch entropy but per-combinator)
3. Alarm-side floor (alarm detects below-floor and injects corrective bias)

The floor values should come from the cross-model data, not be arbitrary.
The I-weakness is real (I is always weakest) — its floor should be lowest but nonzero.
