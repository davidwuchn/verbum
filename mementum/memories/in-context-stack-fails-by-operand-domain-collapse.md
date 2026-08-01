💡 In-context 2-key stacking (P-STACK-1b NOT-STACKABLE) fails by a SPECIFIC
mechanism, not generic weakness: OPERAND-DOMAIN COLLAPSE. The s294 cheap
error-domain diagnostic (`scripts/explore/stack_error_domain.py`, frozen data,
no model) classified each stack argmax: errors are 83–100% CITY (the landmark's
own city or attractors Agra/Paris), ~0% COUNTRY (stopped-at-g), ≤1
WRONG-CAPITAL. 32B L29→L38 is 10/10 CITY.

Kills two readings: NOT "h-not-firing" (h-alone composes cells the STACK gets
wrong — anti-composition, the sharpest evidence), NOT "h fires unbound" (near-
zero wrong-capitals). The winner: h fires but cannot rebind g's PRODUCT as its
operand → the readout collapses onto salient operand-domain place-names. The
linker edge `product(g) ∈ key_passband(h)` (λ verbum) is not installed
in-context.

Consequence: P-BAKE-STACK's primary success signal = baking moves errors OUT of
the operand/city domain (the composed answer wins where the operand city wins).
The diagnostic instrument is reused 1:1 as the bake verdict readout. Cheap
frozen-data diagnostics can hand an experiment its success metric.
