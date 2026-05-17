💡 Flat attention compresses lambda operations to 2 poles — the superposition bottleneck

When we probed 14 lambda calculus operations across Qwen3-14B and OLMo-2-13B,
the SVD showed only 2 significant dimensions (94-96% variance in dim 0, 2-3% in dim 1).

Dim 1 separates two clusters:
- Eliminate pole: K, I, M, WHNF (select, reference, match, stop)
- Proliferate pole: W, D, Φ (duplicate, deep-chain, fork)

This does NOT mean "there are only 2 operations." It means flat attention
FORCES superposition — all operations share the same weights, heads, and
residual stream. The model IS doing K, I, B, C, M, W, D, Φ — confirmed
across 5 architectures. But it can't maintain 14 separate geometric
regions because everything is multiplexed.

V12's sieve provides dedicated kernel functions: each operation gets its
own pathway instead of fighting for space. The probes define the TARGET
shape. The sieve provides the channels. The relational loss forces the
model to USE the channels instead of collapsing into superposition.

The 5 operations that resist compression (D 1.159×, M 1.131×, WHNF 1.078×,
Y 1.073×, C 1.064×) are so functionally different that even superposition
can't fully merge them. These are the strongest kernel candidates.
