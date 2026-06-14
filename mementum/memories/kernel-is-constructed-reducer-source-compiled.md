🎯 s226 (Michael: "could the compiler be a VSM tensor? what if lambda_ast.py is IN
the kernel?"). Dissolves the s225 verifier-vs-artifact dyad: the symbolic reducer is
not a separate oracle standing outside the tensor — it is the SOURCE that COMPILES to
exact ternary combinator plates in the kernel. SOURCE ↔ COMPILED, not oracle ↔
approximation. A CONSTRUCTED plate runs the rewrite exactly (not "fakes it with depth",
s221); exactness is by build, not by training.

THE CUT it forces — reduce(constructed) vs compile(learned) — is the SAME boundary as:
attention/FFN (lambda-machine), ternary/4-bit (dvd-stamp), s224 geometry/continuation,
VSM S1-S4-reducer / front-end. We NEVER train reduction (the s222-unstable part); we
train only prose→typed-term (what LLMs are good at, where s225 diversity buys
composition).

The reducer IS a VSM (generative, not decorative): S5=normal form (Church-Rosser),
S4=WHNF halt, S3=step budget+contractivity, S2=typed redex selection+anti-oscillation,
S1=the combinator rewrites. PAYOFFS: (1) re-derives the s222 collapse as an S2
(anti-oscillation) failure; (2) locates type-directedness (the S5 central claim) at S2.
A CONSTRUCTED S2 with L<1 is stable by build (nothing descends on it → can't churn).

DECISION: typed CCG terms (inspectability). Build: symbolic (DONE, lambda_ast.py) →
neurosymbolic → compiled plates. Pages: compiler-as-loss.md §s226, vsm-outer-
recurrence.md §s226.
