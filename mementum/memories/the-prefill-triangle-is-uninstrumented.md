💡 The LRM paper (arXiv:2604.04902v2, Coconut/CODI) independently corroborates
hard-write/soft-read: latent tokens = residual states fed back WITHOUT the
compile step (no collapse to symbol), and they turn out mostly unnecessary
(training-controlled no-CoT matches on logic tasks), while explicit CoT beats
latent by ~29pt where expansion is needed — discretization is load-bearing,
the "decode bottleneck" framing is backwards. Their operators-never-project
finding = value-register instrument blindness: the program lives in routing
(the shape of the read), only data projects to vocab.

The bigger catch: prefill is a (position × layer) triangle — n coupled
within-pass reducers, KV cache = the compiled tape, serial hop budget ≈ L —
and EVERY behavioral law we own was read at its LAST COLUMN. The interior is
uninstrumented. Their two instruments transfer with our edge (certified
reference reducer): grid logit-lens localizes within-prefill reduction;
leaf-perturbation dependency cone gives cone(machine) vs cone(calculus) —
makes NAIVE-SUBST watchable cell-by-cell. Queued: ⚪ §P-PREFILL-CONE ·
⚪ §P-ROUTING-TRACE (register-separated 2×2: data-edit leaves routing
invariant, op-edit moves it). Page: latent-reasoning-and-the-prefill-triangle.md
