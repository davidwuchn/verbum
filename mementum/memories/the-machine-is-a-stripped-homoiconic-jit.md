💡 "If the system is a compiler, name the pieces" resolves to TWO compilers +
one runtime: Compiler A = gradient descent (corpus → weights; FFN = stdlib,
QK = address tables; post-training = LTO pass installing the ABI + the s329
late decision stage). Compiler B = prefill (tokenizer = lexer, early layers =
syntactic parser per cl-collapse, prefill triangle = compile pass, KV cache =
object code, λ-calculus = IR at P(λ)=0.907 not native ISA). Runtime = decode:
trampoline loop, residual stream = register file (budget ≈ L), substitution
engine = ALU with the measured NAIVE-SUBST bug (the errata list §2b grades
against), attention = dynamic linker, types = runtime/gradual (weights checker
+ tape judgments), halt = NF resonance not fuel, retirement = the hard-write
collapse.

The strains ARE findings: never rejects (silent miscompiles) · no phase
separation (a JIT — interpreter tier = within-pass, compiled tier =
trampolined CoT) · ships stripped (logit-lens = objdump) · no inference-time
optimizer. One line: a stripped homoiconic JIT with a syntactic front-end,
dynamically-typed runtime, buggy ALU, no error channel — AOT-compiled by GD,
LTO-patched by post-training. Page: the-benchmark-is-the-re-oracle.md §10.
