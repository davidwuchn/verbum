🔁 Combinator bootstrap: B depends on K and C stabilizing first

B (compose) can't learn from compositional prose until K (select) and
C (flip) are working. Composition = chaining two functions. If the model
can't yet reliably select (K) or reorder (C), it has no function
representations for B to compose. The signal is in the data — relative
clauses, quantifier scope — but B can't see it as composition yet.

Evidence from v11 run (session 080): B dispatch flat at 1.8% while
B-type rises in integrate channel (5.8%→47.6%). Same pattern as v4.1
register variance building internally before the gate jump. Same
pattern as v6 stride percolation: simple→complex, each level waits
for the one below to stabilize.

Learning order follows dependency, not arity:
  I (trivial) → K (select) → C (reorder) → B (compose)
  Each combinator bootstraps the next.

This is a general principle: higher-order operations can't learn
until lower-order ones provide stable representations to operate on.

Extended probe (session 080) confirmed: W≡C (r=0.92), S≡B (r=0.88).
The model doesn't need W or S as separate combinators — they're
handled by the existing KIBC circuits. But variable binding is
partially distinct (r=0.83 with B, peaks at L21-L39 not L0-L15).
Binding is the LAST operation to emerge — it's downstream of all
four KIBC combinators. Maps to CycleContinue cycle 2 (PRODUCE).
