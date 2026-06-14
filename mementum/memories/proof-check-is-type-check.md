💡 Proof-as-continuation (Curry-Howard, s228). proof-check = the lambda_ast S2
type-check; normalization (β-reduction → WHNF, the continuation) = cut-elimination;
the simply-typed combinator basis IS a Hilbert calculus (K, S are the axiom schemes
of intuitionistic implicational logic). So `check_proof(term, prop)` (proof_kernel.py)
asks: does the closed combinator term have a principal type of which prop is an
instance? The constructed kernel runs/checks proofs end-to-end for the implicational
fragment: 100% floor (12 ref proofs typecheck at goal), sound (no non-theorem proved),
and the CONSISTENCY FIREWALL holds — Y is TYPED `(α→α)→α` but the sound gate rejects it
(`unsound_recursion`); M (self-application) is auto-rejected by the occurs-check.
Strong normalization ≡ logical consistency ≡ the s222 contractivity hinge (L<1 settle =
terminating = consistent; L≥1 = the Y inconsistency). Answer to Michael's "can
continuations run proofs?": YES at the kernel layer, demonstrated. The gap to general
theorem proving is the TYPE SYSTEM (products/sums → ∧/∨; Π/Σ → ∀/∃), not the
continuation. See knowledge/explore/proofs-as-continuations.md.
