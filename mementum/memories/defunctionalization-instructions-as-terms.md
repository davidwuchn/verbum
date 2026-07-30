💡 The frozen-ISA transformer stays PROGRAMMABLE via DEFUNCTIONALIZATION: an instruction is a
term. You can't rewrite the routing/joins (K-structural, s276), but "which function to apply"
can be a VALUE (a selector/type-tag) the frozen routing dispatches on — swap the value, swap the
operation, using the value-write we already have (Reynolds defunctionalization; the routing = the
`apply` dispatcher). Combinatory completeness (s277): fixed basis + arbitrary terms is
Turing-complete, so a "new instruction" is just a term the joins interpret. The checklist's
"write-INSTRUCTIONS ✗" dissolves — it was the wrong level.

Proto-evidence: the bridge-swap ALREADY dispatches a function — the class-axis swap flips WHICH
covering-lookup fires (class = a function-selector). 2-hop swap = swap DATA g(X); 3-hop swap =
swap the FUNCTION-VALUED intermediate = swap the operation applied downstream (higher-order; the
3-hop is the minimal harness where the function is a computed intermediate).

CENTRAL EMPIRICAL CRUX (one register question): is function-selection VALUE-mediated (selector
row → writable → programmable) or ROUTING-mediated (join shape → frozen → blocked)? s276 rows
(I-portable, INSERT-able) vs joins (C-bound). Likely a spectrum; the map is the deliverable.

METHOD: DSP to find types (type matched-filter bank + application-operator SVD → type lattice;
null = shuffled-type + frequency-free) → types index the function library → tap the
function-selectors → 3-hop write-harness swaps them → register verdict. Bonus: writing typed
intermediates BYPASSES a hop's reader-zone cost → a COMPILED 3-hop can beat the depth budget even
at 4B (budget bounds hops the MODEL computes, not hops WE write).

Full design: knowledge/explore/defunctionalization-instructions-as-terms.md (s281 generative seed).
If value-mediated → the honest path to "programmable LLM compiler." If routing-mediated → sharp
negative (programmability bounded to data, not operations).
