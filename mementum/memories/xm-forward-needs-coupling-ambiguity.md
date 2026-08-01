❌ xm-forward-needs-coupling-ambiguity

Forward XM (best-of-K, arXiv:2607.27372) requires ONE-TO-MANY coupling
ambiguity to have anything to search. Deterministic-teacher distillation
pairs (input→output) are PRE-RESOLVED couplings — no ambiguity at the
per-pair level, so best-of-K jitter selection has no mode conflict to
resolve and instead collapses beam variety: the min-loss winner is
systematically the smallest effective jitter.

s296 verdict (b358144, results/xm-etch-explore-s296/): pre-reg REFUTED —
P1 accuracy non-monotone/decreasing in K; P2 moot (s115 50-beats-800 did
not reproduce); P3 no depth-4 concentration. ★ Shuffled-winner null BEAT
best-of-K at both probe counts (97.8 vs 86.1% of oracle @p50; 97.3 vs
83.7 @p800) — random selection keeps variety, min-loss selection kills
it (coheres burn-in-is-variety-not-repetition).

The mode conflict in an etch lives ACROSS pairs in the sign-vote
accumulator, not within pairs. Ports that preserve XM's mechanism:
(a) Reverse-XM over the accumulator — explore WHICH pairs vote,
coverage-constrained; (b) give the student a latent so candidates can
specialize (XMDLM discrete-embedding route); (c) sampled-LLM-teacher
targets = genuine multimodality (reference-beam + Gram transport design).

Reproducibility lesson (❌): mx.random model init was unseeded AND
jitter_seed used salted hash() → 33pt between-launch swing on identical
config. Before any rerun: mx.random.seed per arm, explicit int seeds,
≥3 init seeds/arm.

Connects to: xm-exploration-is-angle-assignment,
holographic-distillation-works, burn-in-is-variety-not-repetition
