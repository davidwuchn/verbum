💡 Qwen3-14B FFN reveals THREE functional groups, not two. Different from toy model.

Session 127 real-model FFN mechanism probe. Three clear clusters:

1. SELECTORS {K, beta_K, beta_identity}: cos 0.85-0.97
   Pick one argument, discard the rest. K x y=x, (λx.λy.x)ab=a
   K combinator and lambda-K are THE SAME FFN function (0.900 at L39)

2. COMPOSERS {B, S}: cos 0.62-0.99
   Build new function applications. B f g x=f(gx), S f g x=fx(gx)
   Tightest cluster in early layers (0.99 at L0)

3. REORDERERS {C, beta_apply}: cos 0.43-0.75
   Shuffle argument order. C f x y=f y x, (λx.fx)a=fa

I combinator starts with selectors (K-I=0.82 at L4) but becomes
isolated by L39 (K-I=0.077). I may be a no-op, not an active function.

Key differences from toy model:
- ALL combinators have large FFN deltas (B/C were near-zero in toy)
- Three groups not two ({K,I}+{B,C} in toy → {K,βK,βI}+{B,S}+{C,βA} in real)
- Delta norms GROW with depth (B: 2.9→241, K: 1.4→501, 83-358× growth)
- Key fraction high for ALL types (>0.85 avg) — mechanism is highly stereotyped
- Selectors anti-correlate with composers at output layer (K-B=-0.42, K-C=-0.58)

Critical finding: combinator K and lambda (λx.λy.x) use THE SAME FFN circuit
(cos=0.900 at L39). The model treats them as identical operations regardless
of notation. The function IS the function, not the syntax.
