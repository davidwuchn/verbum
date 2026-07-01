💡 A REPL where the CHAT MODEL is the evaluator (δ) and the clj_lambda KERNEL is the
ground-truth verifier — the s255 model-as-REPL with the oracle-in-the-loop upgrade,
applied to Clojure. src/verbum/clj_repl.py: oracle(form)=exact kernel reduction; the
model proposes `=> <value>`; verify against oracle; on mismatch feed the exact
reduction (value+steps+nf) back and retry once. Reuses harness.ModelConfig +
reasoning_extract_fn with a THIN multi-turn _chat (the harness run loop is
single-turn) — no fork of grading/HTTP (λ one_way / λ compose).

FALSE ≡ 0 (on-thesis, S5 λ types): untyped Church encoding makes boolean `false` and
numeral `0` the SAME term (K I). oracle decodes int-first so (zero? 5)→"0", but
OracleResult.acceptable = {"0","false"} accepts both. WITH types they differ; WITHOUT
types they are one value — type-directedness in miniature. (TRUE=K, church(1)=I are
distinct; false/0 is the only collision.) Surfaced by a failing test, kept as a
documented feature.

LIVE: qwen36-35b-a3b BASE reference (:5100, the s256 extract-from-base pivot; llama.cpp
ignores the request model field, /v1/models alias 'qwen35-35b-a3b') solved 10/10 forms
FIRST TRY incl. factorial via Y (kernel 440 steps). CAVEAT: easy set → correction loop
NOT exercised live (only stubbed tests). Next: harder set (deep Y/monus/pairs) to make
the model err, or per-STEP combinator verification (lambda_ast.step judges each rewrite).
