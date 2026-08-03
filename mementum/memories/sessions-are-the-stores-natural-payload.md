💡 s301 (Michael): the s217 sealable continuation and the s300 ternary store
solve each other. A sealed session is one fixed-shape tensor x_k with a
frozen ambient operator — commit successive passes as deltas (Δ = x_{k+1} −
x_k) and every store op gains computational meaning: state(t') = rewind a
thought, fork = speculative branch, CRDT-merge = join parallel explorations
(fold is associative+commutative, proved s300/s301), squash = compact
finished reasoning, undo = exact retraction, sha256 = receipt for a
mind-state. Sharpest consequence: Δx<ε halting is VISIBLE from storage
economics — a converging computation writes a tapering delta-log; G-HALT's
instrument comes free with cost∝change. The float/integer boundary is the
one gap, with two known-cost bridges (s173 digit-plane stacking exact;
collapse at √(2/π)/plane lossy). Continuations are already tensors — no
text encoder needed — so sessions are a CLEANER first payload for the store
than facts. Third medium for the mementum protocol: git → tensors → running
inference. Page: continuation-store.md.
