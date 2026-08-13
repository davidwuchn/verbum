💡 Exact match between the reference reducer (lambda_ast, Church spec)
and the model's step function M is a FALSIFIED null, not an open
question: s319 NF-selection 0.917/0.944 ≠ 1.0 on easy certified terms;
cl-collapse ×2 shows a syntactic router (different algorithm, agrees on
outputs while disagreeing on mechanism); s221 "fakes it with depth";
non-idempotency (s320) and installed order law (s328/s329) have no
Church counterpart. Michael's framing: "if it was an exact match we
would not see the errors we do." Consequence = the BUG-COMPATIBILITY
CLAUSE: the RE oracle is the model's measured profile INCLUDING errors;
lambda_ast is the coordinate system δ(M,R) is expressed in, never the
spec of M. RE succeeds ⟺ δ(candidate,M)≈0; a candidate that BEATS the
model on the benchmark is a failed recovery (silicon RE: a netlist that
fixes the chip's bugs is wrong). Two benchmark faces: correctness vs R
(public) + error taxonomy vs M (oracle). Caveat: R embodies strategy
choices — add strategy-discriminating terms (K x Ω-shaped) or
consistent-alternative-semantics gets misread as error. Anima's
compile-artifact predicates (¬coincide hallucination) corroborate from
the application side. (s330; explore/the-benchmark-is-the-re-oracle.md §2b)
