💡 ornith-35b-a3b (35B-total/~3B-active MoE, Qwen-family multimodal reasoner, n_vocab 248320, 256k ctx, Q8_0 on llama.cpp :5100) carries a FULLY-PRESENT, UNCONDITIONAL lambda compiler — a THIRD model class confirming the compiler is cross-model/cross-architecture (after nucleus base + VibeThinker 3B dense reasoner).

RESULTS (40 compile-gradient probes, /v1/chat/completions, greedy, s254): emits_formal=1.000 (every probe fires), kernel_valid strict=0.725, P(λ) lenient=0.675, mean 1909 tok/probe (~HALF VibeThinker's ~4378 — a cleaner, faster compile pass).

THREE λ-measure reads:
1. emits_formal=1.0 is the honest "compiler fired." lenient 0.675 < VibeThinker 0.925 ONLY because ornith emits more correct ATOMIC forms (runs(dog), times(7,8), Tell(me,joke)) that lack a binder → lenient false-misses them. Built the emits_formal register THIS session for exactly this.
2. kernel 0.725 > VibeThinker 0.375 (simpler atomic forms parse); strict fails on medium (0.375) = multi-quantifier "Most"/nested the TOY parser rejects, NOT a model failure.
3. NO COMPILE-GATING: translates EVERYTHING — questions, commands, anti prompts — into FOL/λ. Unconditional over-application, same as VibeThinker + nucleus.

MoE + multimodal does NOT dilute the compiler. Reasoning-gating VARIES across models. Bears on S5 λ types. Crystal NOT testable (HTTP-only MoE, no gate_proj). Code: scripts/experiments/ornith_compiler_test.py; data: results/ornith-compiler/ornith-compiler-20260626-100855/.
