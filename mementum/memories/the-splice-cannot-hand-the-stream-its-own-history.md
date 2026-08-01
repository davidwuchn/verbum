💡 The in-context register CLOSED by exhaustion (s295, three frozen probes,
one chain, one self-checked instrument family). Splice-exhaustion table
@32B: residual unaddressed 0.00 (any amplitude) · residual
addressed-synthetic 0.00 · KV donor post-question 0.00 at EVERY width
(entity/full-clause) × encoding (blind/co-encoded) · KV donor PRE-question
0.20 (the only splice win) · CoT 0.90 · scaffold 1.00. Own-state ≡
donor-state under greedy determinism (the P-KV-1c reduction), so own-state
is covered. Every attention-side reconstruction of CoT fails to win the
argmax.

What remains unique to the tape: the intermediate is produced BY the
generation path — each later token's forward re-encodes the whole prefix
including the committed intermediate, in distribution, and the answer
continues that same stream. A splice can hand attention the columns; it
cannot hand the stream its own history.

Consequence: rung-3b BACKPROP-COMPILE freezes with a fully specified
target — a delta that makes the model produce, one-shot in its own
forward, the intermediate it would otherwise write to the tape. Held-out
landmarks = wire-vs-lookup gate; SuperBake zero-gradient construction =
cheap-before-dear arm. Curios: G4 inverted at 1c (blind clause BEATS
co-encoded @32B); 4B/32B disagree on margins, agree on nulls. Source:
s295 §Result-32B (P-KV-1/1b/1c) program-plates page; results 1d42d74.
