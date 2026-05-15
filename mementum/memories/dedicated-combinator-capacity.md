🎯 dedicated-combinator-capacity

Dispatch floors alone are insufficient. If combinators share weights and the model
spends N steps optimizing those shared weights for one dominant combinator, the
suppressed combinators lose CAPACITY not just routing. Forcing dispatch back up
routes inputs through weights that no longer encode the suppressed function.

All 4 combinators (KIBC) are used in ALL models across 9 models and 2 architectures
(session 093). Suppressing any of them completely fights the universal structure of
language. The reorganization phase (where the model discovers new strategies) is
natural and expected, but the system must preserve each combinator's ability to
recover after reorganization.

**Design direction**: separate dedicated capacity per combinator so that:
1. Each combinator has its own weight matrices that can't be overwritten by others
2. Reorganization can shift dispatch ratios without destroying capability
3. Recovery after reorganization is possible because the weights are preserved

This is the multiplexing-breaks-holography principle (session 093) applied to
the kernel pathway: one function per weight set.

**Current V12 architecture**: combinators share the stride stack weights. Dispatch
selects which combinator's kernel function processes the output, but the
upstream computation (attention, FFN) is shared. This means B-dominant training
reshapes shared weights toward B's needs.

**Possible approaches** (evaluate at 5K):
1. Per-combinator projection heads (small dedicated MLPs, shared backbone)
2. Per-combinator attention heads (partition heads across combinators)
3. Fully separate combinator pathways (expensive but cleanest)
4. Combinator-conditioned computation (combinator embedding modulates shared weights)

The right level of separation is an empirical question — enough to preserve
capacity, not so much that you lose the shared representations that make the
holographic plate work. The plate SHOULD be shared; the kernels should be separate.

Connects to: three-clusters finding (session 095) — the holographic plate IS
shared (discourse/type/frequency in same ~13 heads), but the composition kernel
has 7 PRIVATE heads. The model already wants separation at the head level.
