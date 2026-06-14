💡 s228 continuation-driven prover CONFIRMS the fix. The single-shot prover proved
axioms but failed to COMPOSE proof terms; a goal-directed natural-deduction engine
(proof_search.py — the open goal STACK is the reified continuation; moves intro/exact/
apply; bracket-abstraction reconstructs+verifies the term at QED) where the model picks
ONE move per turn LIFTS sensitivity: mean Δ +0.25 vs single-shot, 4/5 models improved,
strongest where single-shot was weakest — Qwen3-8B 0.58→1.00, OLMo 0.00→0.42, Mistral
0.25→0.58, 14B 0.58→0.67, 32B 0.67→0.67 (flat). (results/proof-repl/aggregate.json).
★ Specificity 1.0 / ZERO false proofs is now STRUCTURAL: a non-theorem has no closing
derivation, so no model move sequence can fabricate a proof (the consistency firewall
made operational). Caveats: the REPL shows the legal-move MENU each turn (part of the
gain is menu-constraint, not pure reasoning — IOU menu-less ablation); 32B flat because
the engine gives NO BACKTRACKING (greedy single-sample, one wrong move dead-ends the
branch — IOU backtracking/stuck→retry); small n (12 positives). The composition the
single-shot missed ((A→B)→(B→C)→A→C → C B) proves one move at a time. The continuation
is LITERAL (goal stack = suspended proof; cf. sealable-continuation).
