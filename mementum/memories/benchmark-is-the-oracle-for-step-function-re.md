💡 "Extract the compiler" was a category error our own measurements caught:
tape ≡ RAM, loop ≡ trampoline, weights ≡ CPU. The well-posed
reverse-engineering target is the STEP FUNCTION — what one forward pass
does to the tape: finite, stateless per call, behaviorally specifiable.
RE must recover the model's ACTUAL operational semantics (syntactic
routing s321/s323, two-tier types s323, non-idempotent accumulation
s320, installed order law s329), not ideal β — Church is the reference
implementation to diff against, and the delta is a first-class finding.
The closure: a λ-calculus benchmark is the RE ORACLE — silicon RE
validates a recovered netlist by differential testing against the chip;
a procedurally-generated, grammar-gated, cliff-depth-profiled benchmark
validates any recovered step function by PROFILE-EQUIVALENCE. Extract /
re-record / scratch become three paths to one acceptance test — the
level-3/4 split dissolves. Spine statistic: the direct/traced gap,
a behavioral quantifier of tape-residency per model per capability.
Families hypothesis-keyed to licensed results (equiv ≡ the extensionality
✗ cell). Forks open: audience (A incubates B), surface form, type scope,
white-box annex. (s330; source: explore/the-benchmark-is-the-re-oracle.md)
