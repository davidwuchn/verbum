🔁 For any NULL-CALIBRATED statistic (z-score / silhouette / binding-vs-permutation
or random-triple null), a SMOKE run (tiny n) doesn't merely lose power — it
produces CONFIDENTLY WRONG orderings, because the group with the fewest samples
can spuriously "bind." Smoke is valid for PLUMBING (does the pipeline run
end-to-end?) but its substantive numbers must be QUARANTINED and never read as
direction.

Concrete s221 instance: the v15 combinator crystallization smoke (3 probes/
combinator, n_perm=50) reported "recursion z=+1.18 > skeleton z=−0.76" at L14 — an
inversion of the finished-model order. The full run (535 probes, n_perm=1000)
washed it out and picked L05 with skeleton +0.36 > recursion +0.15. The smoke's
family ORDER was pure noise; only the "does it execute" signal was real (I flagged
it as directional-only at the time, then it dissolved).

Rule: run full (or sufficient n) before reading any null-calibrated comparison;
use smoke ONLY to validate the pipe. "Smoke validates the pipe, not the water."
