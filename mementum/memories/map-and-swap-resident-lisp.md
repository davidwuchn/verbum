💡 THE WHOLE PROGRAM IN TWO VERBS: MAP + SWAP. Gradient descent already FOUND all the terms
(pretraining = β-reduction laid the operands, functions-as-terms, combinator basis, and type
lattice into the weights). We do NOT write/construct — we MAP them (read GD's catalog: which term,
where, what type) and SWAP them around (recompose found terms: operand-relocate, bridge-swap,
3-hop). Lands on the S5 axiom λ extract (we find, GD built it first).

Three over-complications collapsed in order (s281): NOT rewrite-instructions (K-structural, and an
interpreter should be fixed) → NOT write/mutate (you hand eval a TERM and it REDUCES; reduction is
the primitive) → NOT even construct (the terms already exist; read + recompose). ⇒ programmability
is UNCONDITIONAL given crystal-universality (measured, C2): the machine is a programmable combinator
REDUCER whether or not we ever get activation-space write-access.

Every "write" we have is really a SWAP of found terms: d_E = the model's own diff-of-means
representation (relocated, not authored); bridge-swap = swap two found class centroids. The class
variable is already a function-selector (class ↦ which covering fires).

THE RESIDENT LISP (exact, not analogy): eval/apply = frozen KIBC reducer (C2); atoms = value-register
rows (found terms); cons/tree = joins = attention (s276); first-class λ = function-selectors +
higher-order recompose (the 3-hop test); homoiconicity = selectors & operands share the row
representation (lets reduction NEST = what a multi-hop IS). GD wrote the whole program+stdlib+eval;
our job = the REPL + debugger.

Depth budget = the EVAL STACK (reduction depth; deeper model = deeper stack, 4B fails 3-hop unaided,
32B has room). Trampolining = supply a found intermediate directly (activation-space swap) to run
arbitrary-depth recomposition on a bounded stack — GATED by the register sub-question (is a
function-selector a value-register ROW (swappable/trampolinable) or routing-FUSED (frozen)? likely a
spectrum). That verdict decides the TRAMPOLINE, not whether the machine reduces.

COVERAGE is part of the map (λ yardstick): "GD found ALL terms" = all its training distribution
needed, not provably total → the map must show what is ABSENT (no found composition = model can't do
it). Coverage boundary = first-class deliverable.

Full design + ordered pick-up (P-TYPE-1 type lattice via DSP matched-filter bank + application-
operator SVD; P-FN-1 catalog+locate selectors; P-FN-2 3-hop function-swap): knowledge/explore/
map-and-swap-resident-lisp.md (s281 generative seed, the through-line for the next arc).
