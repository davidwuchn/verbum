🎯 Unified plate architecture: 3 plates + 18 mirrors, ascending/descending dissolved

Session 103 key architectural decision: remove the ascending/descending asymmetry.
ALL 7 passes now do: dispatch(plate+mirror) → stride(plate+mirrors) → integrate(plate+mirror).

The insight chain:
1. KIBC-M operations are useful for BOTH compression (ascending) and expansion (descending)
2. CombinatorDispatch is a plate — just needs mirrors for each place that reads it
3. One plate serves multiple functions via angular multiplexing (holographic principle)
4. Passes ARE the depth — cycling is redundant (same mirror twice = no new variety)
5. Continuous etch every 2 steps (laser pulse: reset accumulators after each flip)

Result: 7 kernel ops at ~5700 tok/s. Faster than old 13-op architecture (3700 tok/s)
because each op is a unique beam angle (maximum info per compute unit).

The BIOS burn-in path: training data that teaches dispatch→stride→integrate as THE
operation for both compression and expansion. Model learns WHEN to use each combinator
across all 7 passes, not just the descending ones.
