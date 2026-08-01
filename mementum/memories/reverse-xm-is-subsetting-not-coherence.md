❌ Reverse-XM over the s115 sign accumulator (port 1, §XM-REVERSE-1,
s297): VERDICT SUBSETTING-ARTIFACT. Coalition voting (vote on a 50%
subset of units per round) beats all-unit baseline by ~11pt recovery,
5/5 seeds (G1 pass @800 probes) — BUT does NOT beat a size-matched
RANDOM coalition (G2 yardstick FAIL, Δ+0.020 n.s.). Coherence adds
nothing; coverage adds nothing; revxm ≈ revxm_rand ≈ revxm_nocov. G3:
contested weights end at the oracle sign at chance (~0.49) for every
arm → the tug-of-war is irreducible toward truth.

The gain is variance reduction: half the voters → |acc|/|S| crosses 0.6
more easily → sharper flips. Not exploration. Mirrors the paper's
minibatch-OT-HURTS result — a geometric grouping of votes doesn't beat
random; exploration needs coupling AMBIGUITY the model co-adapts to, and
the deterministic-teacher accumulator has none.

Lesson: the s296 "conflict across pairs" diagnosis is half-right —
subsetting relieves the tug-of-war but there's no exploitable mode
structure. Both surviving ports (student-latent, sampled-LLM-teacher)
add real multimodality the accumulator lacks; they are the honest next
step. Subsetting-fraction/threshold tuning is a free knob but shallow
(λ yardstick: describes, doesn't discover). Record: 497f979,
results/xm-reverse-s297/.
