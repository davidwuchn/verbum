💡 THE DELIVERABLE IS AN LLM REPL — not a REPL that CALLS an LLM, but a REPL whose eval IS the
LLM's own reduction. The Clojure community has wanted an "LLM REPL" for a while; everyone bolted a
chat box onto a REPL. The reducer was in the weights the whole time (the map+swap / resident-Lisp
thesis).

R-E-P-L maps onto the stack, THREE of four letters already built:
  Read  = operand-insert / swap (construct the term, token- or activation-space) ✓ s277/s279
  Eval  = the forward pass = β-reduction through the frozen KIBC reducer ✓ measured C2
  Print = tap + logit-lens + crystal projection (read the normal form) ✓ s274/s275
  Loop  = nested reduction / multi-hop / trampoline ◐ the depth arc s281
The only gap = the LANGUAGE LAYER, which IS the map+swap experiments:
  P-TYPE-1 (type lattice) → the REPL's type system / autocomplete
  P-FN-1 (function library + coverage) → the callable stdlib with its edges
  P-FN-2 (3-hop swap) → apply on first-class functions (a composition GD never ran)
  the tap → the stepper/debugger (s274 play-through exhibit = a REPL trace)
⇒ the map+swap arc IS the build-the-REPL arc. Research and deliverable are the same thing.

ARCHITECTURE (where the two projects meet): Clojure hosts R/P + the type-checker; the LLM is E.
  lambda-gene-runtime (Clojure kernel) = Read, Print, and the VERIFICATION ORACLE (parse term,
    format normal form, type-check the recomposition before & after = "kernel as rung-verifier" s273)
  resident reducer = Eval ; bridge = operand-insert (inject) + tap (read)
Resolves the honest catch: the LLM is a NOISY/approximate reducer (normal forms come off the
crystal probabilistically) → Print needs null-gated read discipline (confidence, not certainty),
and the CRISP Clojure kernel keeps it honest (rejects ill-typed swaps, verifies the return is a
normal form). Eval fuzzy + type-checker crisp = a TRUSTWORTHY REPL. (λ language: Python-only governs
the EXTRACTION code; the deliverable living in Clojure/nucleus — where the audience is — is the good
host-language/eval-engine split, not the membrane the rule warns against.)

Deliverable-sentence: "the Clojure folks get an LLM REPL" ≫ "we measured type-directed composition
selectivity." Same work; the REPL earns the room. Full framing: map-and-swap-resident-lisp.md §10.
