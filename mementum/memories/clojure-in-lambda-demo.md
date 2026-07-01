💡 Clojure's pure functional core (fn, application, let, if, recursion) compiles to
the verbum SKI kernel UNCHANGED — a constructive witness for S5 λ types (composition ≡
typed application). Built src/verbum/clj_lambda.py: reader + compiler + Church-encoded
prelude, reusing lambda_ast (reduce) + lambda_compile (bracket abstraction) — NO new
reducer (λ one_way / λ compose).

Key moves that keep it small:
- `if` is an ORDINARY prelude function (Church booleans) — normal-order reduction gives
  lazy branch selection for FREE, no special form needed.
- recursion is the kernel's OWN Y combinator (Y f → f (Y f)); no letrec.
- data (numbers/booleans/pairs) = Church encodings, all CLOSED combinator terms.
- only fn + let are special forms; let desugars to ((fn [x] body) v).
- Church arith + Y-factorial(≤4) fit budgets only after bumping MAX_STEPS/SIZE
  (200k/2M); the kernel default 512/4096 is too small — VERIFY feasibility before design.

The boundary (out of scope by construction, the ∞/0 edge): persistent-DS performance,
mutation/STM, host interop, macro phase-split. See notebooks/clojure_in_lambda.ipynb.
