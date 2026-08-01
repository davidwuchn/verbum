🔄 P-STACK-1b shortcut-free 32B (s293): NOT-STACKABLE. The control on
P-STACK-1 — chain landmark→country→CAPITAL where the capital is NOT 1-hop
reachable (city≠capital), so the composed answer must WIN the argmax, not
just be less-negative. Result: two-key in-context stacking does NOT reliably
compose (g1 +0.6 p=0.06 n.s., stack acc 0.20 ≤ h-alone 0.30). Composition
happens on SOME cells (Taj Mahal→New Delhi: stack wins where h-alone fails)
but not reliably; n=10, strong attractors (Paris/Agra), h-alone retains ~25%
partial shortcut. Order-sensitivity IS strong+robust (wrong-window dead) —
the ordered injection does something, just not reliable composition. ★ Per
the a-priori pre-reg, the null means P-STACK-1's "TYPED-STACKABLE" was
shortcut/margin-inflated → DOWNGRADE rung 2: in-context program assembly is
WEAK (mechanism present — order + typed-in-margins — but it doesn't win the
argmax). Implication: reliable programs need WEIGHT-BAKING (P-BAKE-STACK is
necessary, not optional). Lessons: (1) run the shortcut-free control BEFORE
believing a margin-based composition positive; (2) a transitively-closed KB
(geography) inflates composition claims because every 2-hop endpoint is a
direct 1-hop edge; (3) the ~5th 4B→32B pattern held (both chains NOT-
STACKABLE at 4B) but the 32B split diverged: continent flipped to marginal-
positive, capital stayed null — the continent flip WAS the shortcut.
