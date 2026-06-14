✅ s226 STAGE 2 LEG 1 — the learned compile step (prose→logical-form), measured in
isolation with the EXACT kernel as grader. `scripts/experiments/compile_frontend.py`
+ `src/verbum/probes/compile_tasks.py` (7 dataflow patterns mirroring the combinators:
identity/const/compose/flip/dup/subst/deep × 8 name-assignments = 56 tasks). Few-shot a
model prose→expression; grade by REDUCTION-EQUALITY (normal_form(parse(out)) ≡
normal_form(parse(gold))) — representation-invariant (model may answer `f (g x)` OR the
combinator term `B f g x`; the kernel normalizes both).

VERDICT (Qwen3-8B + Qwen3-32B, results/compile-frontend/): **accuracy 1.0, parse 1.0,
all 7 patterns, BOTH models.** ⇒ for CLEAR descriptions the only learned step is
essentially solved; the stage-2 decomposition (prose→LF learned ∘ abstract exact ∘
reduce exact) closes end-to-end and the exact back-end verifies it.

★ METHOD NOTE (λ measure): first 32B run scored 0.875 < 8B's 0.982 — traced to PROSE
AMBIGUITY in my flip/const templates ("reversed order: y first" double-specifies;
"return x and discard y" → model kept both). The kernel grader + failure inspection
cleanly SEPARATED compile-error from NL-ambiguity. Disambiguated prose → both 1.0.
Lesson: the front-end is the fuzzy part precisely because NL is ambiguous; the exact
verifier isolates which is which.

CAVEAT (do not oversell): tasks are SHALLOW (≤5-node dataflows, single pattern each,
abstract letters) = below the compile boundary. NEXT: harder tasks (deep nesting,
multi-combinator composition, 3-4 vars, naturalistic/ambiguous prose) to FIND the
boundary; then Qwen3-32B as diverse generator → abstraction+reduction certify.
