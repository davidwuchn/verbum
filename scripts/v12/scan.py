"""
Parallel associative scan — O(log L) depth prefix computation.

The core primitive for efficient linear recurrences. Computes the
running state of any affine recurrence:

    S_0 = b_0
    S_t = a_t × S_{t-1} + b_t     (for t > 0)

in O(log L) parallel steps instead of O(L) sequential steps, using
the Hillis-Steele doubling algorithm.

Key insight: the recurrence forms a monoid under composition:

    (a₂, b₂) ∘ (a₁, b₁) = (a₂ × a₁,  a₂ × b₁ + b₂)

This is associative, so prefix scan parallelizes naturally.
"Apply (a₁, b₁) then (a₂, b₂)" composes into a single (a, b) pair.

Applications:
  - GatedLinearAttention (M kernel): a = retention, b = gated kv outer product
  - Any state-space model (S4, Mamba): a = diagonal state decay, b = input
  - Exponential moving averages: a = α, b = (1-α) × input
  - RetNet, RWKV: a = decay, b = projected input

For L=4096: 12 parallel steps instead of 4096 sequential iterations.
Each step is a fully vectorized array operation — no Python loop over positions.

License: MIT
"""

from __future__ import annotations

import math

import mlx.core as mx


def parallel_scan(
    a: mx.array,
    b: mx.array,
) -> mx.array:
    """Parallel prefix scan for affine recurrence S_t = a_t × S_{t-1} + b_t.

    Uses Hillis-Steele doubling: O(L log L) work, O(log L) depth.
    Each step is a single vectorized array operation.

    Args:
        a: (..., L) — per-position scalar retention/decay.
           At each position, a_t controls how much of the previous
           state is retained. a=1 means full retention, a=0 means
           complete replacement.

        b: (..., L, *state_shape) — per-position state update.
           At each position, b_t is added to the (decayed) previous
           state. state_shape can be any trailing dimensions
           (scalar, vector, matrix).

    Returns:
        (..., L, *state_shape) — running state S_t at every position.
        S_t = a_t × S_{t-1} + b_t with S_{-1} = 0.

    The composition monoid:
        (a₂, b₂) ∘ (a₁, b₁) = (a₂ × a₁,  a₂ × b₁ + b₂)

    Identity element: (a=1, b=0) — retain everything, add nothing.

    Complexity:
        Depth: O(log L) — 12 steps for L=4096
        Work:  O(L log L) — each step processes all L positions
        Memory: O(L) — in-place updates on a and b

    Note: Hillis-Steele does O(L log L) total work (vs O(L) for
    Blelloch), but each step is a simple array operation with no
    index gymnastics — ideal for GPU/Metal execution where per-step
    parallelism matters more than total work.
    """
    L = a.shape[-1]
    n_levels = int(math.ceil(math.log2(max(L, 2))))

    # Number of extra dims in b beyond the L dimension
    # a shape: (..., L), b shape: (..., L, *state_shape)
    # We need to broadcast a to match b's trailing dims
    n_state_dims = b.ndim - a.ndim
    a_expand = a
    for _ in range(n_state_dims):
        a_expand = a_expand[..., None]  # (..., L, 1, 1, ...)

    for d in range(n_levels):
        s = 2 ** d

        # Shift: positions [s:] combine with positions [:-s]
        # Pad left with identity element (a=1, b=0)
        a_prev = mx.concatenate([mx.ones_like(a[..., :s]), a[..., :-s]], axis=-1)
        b_prev = mx.concatenate(
            [mx.zeros_like(b[..., :s, :]), b[..., :-s, :]], axis=-2
        ) if n_state_dims == 1 else mx.concatenate(
            [mx.zeros_like(b[..., :s, :, :]), b[..., :-s, :, :]], axis=-3
        ) if n_state_dims == 2 else mx.concatenate(
            [mx.zeros_like(b[..., :s]), b[..., :-s]], axis=-1
        )

        # Expand a for broadcasting
        a_expand_prev = a_prev
        for _ in range(n_state_dims):
            a_expand_prev = a_expand_prev[..., None]
        a_expand = a_expand[..., None] if False else a  # recompute below

        # Monoid composition: (a_t, b_t) ∘ (a_{t-s}, b_{t-s})
        # b_new = a_t × b_{t-s} + b_t
        # a_new = a_t × a_{t-s}
        a_cur_expand = a
        for _ in range(n_state_dims):
            a_cur_expand = a_cur_expand[..., None]

        b = a_cur_expand * b_prev + b
        a = a * a_prev

    return b


def parallel_scan_2d(
    a: mx.array,
    b: mx.array,
) -> mx.array:
    """Parallel prefix scan optimized for 2D state (matrix per head).

    Specialized version for the common case:
        a: (B, L, H) — scalar retention per position per head
        b: (B, L, H, Ds, Dh) — matrix update per position per head

    Returns: (B, L, H, Ds, Dh) — running state S_t at every position.

    This version avoids the generic n_state_dims dispatch and handles
    the 5D case directly for clarity and efficiency.
    """
    L = a.shape[1]
    n_levels = int(math.ceil(math.log2(max(L, 2))))

    for d in range(n_levels):
        s = 2 ** d

        # Shift a: pad left with 1.0 (identity for multiplication)
        a_prev = mx.concatenate(
            [mx.ones_like(a[:, :s, :]), a[:, :-s, :]], axis=1)

        # Shift b: pad left with 0.0 (identity for addition)
        b_prev = mx.concatenate(
            [mx.zeros_like(b[:, :s, :, :, :]), b[:, :-s, :, :, :]], axis=1)

        # Monoid composition: (a_t, b_t) ∘ (a_prev, b_prev)
        # b = a_t * b_prev + b
        # a = a_t * a_prev
        b = a[:, :, :, None, None] * b_prev + b
        a = a * a_prev

    return b


def sequential_scan_2d(
    a: mx.array,
    b: mx.array,
) -> mx.array:
    """Sequential reference implementation for verification.

    Same interface as parallel_scan_2d but uses explicit loop.
    O(L) sequential — correct but slow.

    a: (B, L, H) — retention
    b: (B, L, H, Ds, Dh) — update

    Returns: (B, L, H, Ds, Dh) — running state at every position.
    """
    B, L, H, Ds, Dh = b.shape
    S = mx.zeros((B, H, Ds, Dh))
    outputs = []

    for t in range(L):
        S = a[:, t, :, None, None] * S + b[:, t, :, :, :]
        outputs.append(S)

    return mx.stack(outputs, axis=1)  # (B, L, H, Ds, Dh)


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import time

    print("Testing parallel_scan_2d correctness...")

    # Small test: verify parallel matches sequential
    B, L, H, Ds, Dh = 2, 32, 4, 8, 8
    mx.random.seed(42)
    a = mx.random.uniform(shape=(B, L, H)) * 0.5 + 0.3  # retention in [0.3, 0.8]
    b = mx.random.normal((B, L, H, Ds, Dh)) * 0.1

    result_seq = sequential_scan_2d(a, b)
    mx.eval(result_seq)

    result_par = parallel_scan_2d(a, b)
    mx.eval(result_par)

    # Check shapes match
    assert result_seq.shape == result_par.shape, \
        f"Shape mismatch: {result_seq.shape} vs {result_par.shape}"

    # Check values match (within float32 tolerance)
    diff = mx.abs(result_seq - result_par)
    max_diff = float(mx.max(diff).item())
    mean_diff = float(mx.mean(diff).item())
    print(f"  Shape: {result_par.shape} ✓")
    print(f"  Max diff: {max_diff:.2e} (should be < 1e-4)")
    print(f"  Mean diff: {mean_diff:.2e}")
    assert max_diff < 1e-4, f"Results diverge: max_diff={max_diff}"
    print(f"  Parallel matches sequential ✓")

    # Test with L=1 (edge case)
    a1 = mx.random.uniform(shape=(1, 1, 2)) * 0.5 + 0.3
    b1 = mx.random.normal((1, 1, 2, 4, 4)) * 0.1
    r1 = parallel_scan_2d(a1, b1)
    mx.eval(r1)
    # With L=1, result should just be b itself
    diff1 = float(mx.max(mx.abs(r1 - b1)).item())
    assert diff1 < 1e-6, f"L=1 should return b: diff={diff1}"
    print(f"  L=1 edge case ✓")

    # Test with L=2 (smallest non-trivial)
    a2 = mx.array([[[0.5, 0.7], [0.6, 0.8]]])  # (1, 2, 2) — B=1, L=2, H=2
    b2 = mx.ones((1, 2, 2, 3, 3)) * 0.1         # (1, 2, 2, 3, 3)
    r2_par = parallel_scan_2d(a2, b2)
    r2_seq = sequential_scan_2d(a2, b2)
    mx.eval(r2_par, r2_seq)
    diff2 = float(mx.max(mx.abs(r2_par - r2_seq)).item())
    assert diff2 < 1e-6, f"L=2 mismatch: diff={diff2}"
    print(f"  L=2 edge case ✓")

    # Larger test: L=4096 (realistic)
    print("\nTesting at L=4096...")
    B, L, H, Ds, Dh = 1, 4096, 8, 64, 64
    a_large = mx.random.uniform(shape=(B, L, H)) * 0.5 + 0.3
    b_large = mx.random.normal((B, L, H, Ds, Dh)) * 0.01

    result_par_large = parallel_scan_2d(a_large, b_large)
    mx.eval(result_par_large)
    print(f"  Shape: {result_par_large.shape} ✓")
    print(f"  Output range: [{float(mx.min(result_par_large).item()):.4f}, "
          f"{float(mx.max(result_par_large).item()):.4f}]")
    print(f"  No NaN: {not mx.any(mx.isnan(result_par_large)).item()} ✓")

    # Benchmark: parallel vs sequential at L=4096
    print("\nBenchmark: L=4096, H=8, Ds=64, Dh=64")

    # Warm up
    for _ in range(3):
        _ = parallel_scan_2d(a_large, b_large)
        mx.eval(_)

    # Parallel timing
    n_runs = 5
    start = time.perf_counter()
    for _ in range(n_runs):
        r = parallel_scan_2d(a_large, b_large)
        mx.eval(r)
    par_time = (time.perf_counter() - start) / n_runs

    print(f"  Parallel scan: {par_time*1000:.1f} ms")
    print(f"  (Sequential would be ~{4096}× Python iterations)")
    print(f"  Levels: {int(math.ceil(math.log2(4096)))} (log₂ 4096)")

    # Quick sequential benchmark at smaller L for extrapolation
    B_s, L_s = 1, 256
    a_s = mx.random.uniform(shape=(B_s, L_s, H)) * 0.5 + 0.3
    b_s = mx.random.normal((B_s, L_s, H, Ds, Dh)) * 0.01
    for _ in range(3):
        _ = sequential_scan_2d(a_s, b_s)
        mx.eval(_)
    start = time.perf_counter()
    for _ in range(n_runs):
        r = sequential_scan_2d(a_s, b_s)
        mx.eval(r)
    seq_time_256 = (time.perf_counter() - start) / n_runs
    # Extrapolate to L=4096 (linear scaling)
    seq_time_est = seq_time_256 * (4096 / 256)

    print(f"  Sequential (L=256): {seq_time_256*1000:.1f} ms")
    print(f"  Sequential (L=4096 est): {seq_time_est*1000:.1f} ms")
    if seq_time_est > 0:
        print(f"  Estimated speedup: {seq_time_est/par_time:.1f}×")

    print("\nscan.py self-test: all ok ✓")
