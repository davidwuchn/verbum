💡 s228 proof-as-inhabitation, 5 models / 3 arch (results/proof-inhabitation/).
LLM as prover, kernel as verifier (compiler-as-loss / co-processor pattern). HEADLINE:
**specificity 1.00 across ALL 5 models, ZERO false proofs** — the model cannot bluff
past the kernel, including Peirce and the Y-trap `(A→A)→A`. Sensitivity (theorems
proved): Qwen3-32B 0.67, Qwen3-14B/8B 0.58, Mistral 0.25, OLMo 0.00. The model proves
the AXIOMS (I,K,S,B,C,W) but FAILS TO COMPOSE multi-combinator proofs — `K I`, `C B`,
`C I`, `B K K` come back as a single axiom (type_mismatch). This is the SAME
composition-failure signature as lambda-halt-continuation §"composition fails but
continuations solve it." Scale helps mildly (32B best). ⇒ the predicted fix is a
CONTINUATION-DRIVEN prover: prove sub-goals one rule/combinator per turn, chain via the
CPS REPL. Caveat: base-model scores CONFOUNDED — OLMo answered `none` 15/20 (the single
`none` few-shot anchors a raw base continuation; NOT proof-inability). Small n (12+8),
greedy single-sample. Implicational fragment only.
