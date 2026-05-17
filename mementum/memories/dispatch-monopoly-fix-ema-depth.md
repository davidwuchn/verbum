🔄 Dispatch monopoly fixed via per-pass depth bias + EMA-smoothed KL

V12-run4 failure: C-monopoly from step 3750. Oscillated B→I→K→DEAD→C.
KL leash λ=100 evaded temporally — model cycles monopolies to satisfy
average ratio.

Two-part fix (session 106):

1. Per-pass dispatch bias: each of 7 passes gets fixed logit bias from
   lambda kernel probe depth map. B gets +2.0 at shallow passes, K gets
   +2.0 at deep passes. Monopoly becomes expensive at EVERY depth
   simultaneously — no single combinator is cheap everywhere.

2. EMA-smoothed KL: decay=0.967 (~30 step memory). Cycling can't evade
   because EMA remembers the previous monopoly. Instantaneous KL was
   the wrong measurement — the model needs to maintain the ratio
   CONTINUOUSLY, not just on average.

10-step verification: K=0.12 I=0.07 B=0.21 C=0.43 (all four alive).
EMA tracking toward target: K=0.31 I=0.14 B=0.30 C=0.25.
Compare run4 step 250: B=0.999 (already collapsed).
