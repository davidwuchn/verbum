---
title: "Optimization Negative Results — Why FP Techniques Fail on Apple Silicon"
status: active
category: methodology
tags: [optimization, negative-result, apple-silicon, mlx, ternary, sparsity, bandwidth, latency]
related:
  - fp-optimization-map.md
  - moire-training-shortcuts.md
  - ../v14-architecture.md
  - continuations-as-composed-plates.md
depends-on:
  - fp-optimization-map.md
created: session 158
---

# Optimization Negative Results

> Session 158. Systematically tested every FP optimization from the
> optimization map against the actual v14 model on M3 Ultra. ALL
> failed. This page documents why, so future sessions don't re-enter
> these dead ends.

## The Wrong Assumptions

The FP optimization map (session 158, early) assumed:
1. FFN is sparse (3-49% active like the teacher) → **FALSE**
2. Ternary matmul is cheaper than float matmul → **FALSE on AMX**
3. Fewer kernel launches = faster → **FALSE (MLX parallelizes)**
4. Model is memory-bandwidth-bound → **FALSE at d=1280**
5. Smaller tiles improve cache utilization → **FALSE (AMX needs large batches)**

Every optimization attacked a bottleneck that doesn't exist.

## Result 1: Lazy Neurons — Student FFN Not Sparse

**Technique:** Compute gate first, threshold, only compute key/value
for active neurons. Saves work proportional to sparsity.

**Benchmark (the mechanism works IF sparse):**

| Active % | Speedup |
|----------|---------|
| 2.5% | 2.3× |
| 5% | 2.3× |
| 20% | 1.9× |
| 50% | 1.3× |
| 100% | 0.89× (overhead) |

**Why it failed:** The v14 student's FFN has 100% active neurons at
threshold 0.1. Mean |gate| ≈ 0.37 with Gaussian distribution. Three
independent causes:

1. **Ternary extraction destroys sparsity.** The teacher's FFN sparsity
   lives in magnitudes (large negative pre-activation → dead neuron).
   sign(W) preserves topology but destroys magnitude patterns. The
   central limit theorem makes ternary matmul output Gaussian regardless
   of the teacher's sparsity structure.

2. **Shared FFN prevents specialization.** One plate for all 13 passes
   means no per-pass sparsity variation. The teacher had 64 different
   FFN layers with wildly different sparsity (3% to 49%).

3. **Batch-union kills per-token sparsity.** Even if individual tokens
   have 30% active (at threshold 0.3), the union across B×L tokens
   approaches 100%. quantized_matmul requires a fixed weight subset
   for all tokens in the batch.

**Resolution:** Redesigned to separate FFN plates per stack. If
per-stack plates develop different sparsity, revisit lazy neurons.

## Result 2: Index Sets — Can't Beat AMX

**Technique:** Pre-compute pos/neg index sets from ternary weights.
`sign(W) @ x = sum(x[pos]) - sum(x[neg])`. Zero multiplication.

**Why it failed on Apple Silicon:**
- `mx.quantized_matmul` at 2-bit is NOT faster than float32 matmul
- AMX accelerator treats multiply and add identically
- Gather-add-subtract creates huge intermediate tensors
  (B×L×out_f×max_indices = 1.6B floats for one FFN gate call)
- Sign-split (two binary matmuls) is 0.66× — slower than one full

**Benchmark (d=1280, d_ff=5120, B=4, L=1024):**

| Method | Time | vs qmatmul |
|--------|------|-----------|
| quantized_matmul | 3.02 ms | 1.00× |
| float32 matmul | 2.62 ms | 1.15× (!!) |
| sign-split (2 matmuls) | — | 0.66× |

Float matmul is actually 15% FASTER than quantized_matmul at these
dimensions. The ternary encoding saves storage, not compute.

**Key insight:** Ternary wins on CPU (no AMX, addition < multiplication,
2-bit fits in cache). It does NOT win on GPU/AMX where the matmul
accelerator doesn't distinguish value distributions.

## Result 3: QKV / Gate+Key Fusion — Already Parallel

**Technique:** Concatenate Q/K/V weight matrices into one fused matmul.
3 launches → 1 launch.

**Benchmark (isolated):** QKV fusion 1.28× faster.
**Benchmark (13 serial passes):** 0.99× — NO speedup.

**Why:** MLX uses lazy graph evaluation. Independent ops (Q, K, V on
same input) are already dispatched in parallel. Fusing them into one
larger matmul doesn't help because:
1. MLX already parallelizes the independent launches
2. The serial bottleneck is the data dependency BETWEEN passes
3. The fused matmul (3840×1280) has worse cache behavior than three
   parallel 1280×1280 matmuls

## Result 4: Stream Fusion — Smaller Tiles Are Slower

**Technique:** Process one position through all 13 passes (keep in L1
cache) instead of all positions through one pass.

**Analysis (theoretical):** Activation traffic is 94% of total memory
traffic (1490 MB vs 89 MB weights). Stream fusion would save most of it.

**Benchmark (actual):**

| Tile size | ms/token | vs baseline |
|-----------|----------|-------------|
| 1024 | 0.028 | 1.00× |
| 128 | 0.039 | 1.40× slower |
| 16 | 0.127 | 4.57× slower |

**Why:** At d=1280, the model is NOT memory-bandwidth-bound. Achieved
bandwidth is 20-31 GB/s on M3 Ultra (800 GB/s peak). The memory bus
is barely loaded. Smaller tiles can't saturate AMX execution units —
the overhead of many small matmuls dominates.

**Additional finding:** FFN weights (4.7 MB) fit in L2 cache (16 MB)
and stay warm across all 13 passes (per-pass cost = 0.92× single pass).
There's no weight reload penalty to save.

## Result 5: Float16 — Same Speed

**Benchmark:** float32 vs float16 activations through 13 FFN passes:
29.6 ms vs 29.8 ms. quantized_matmul dominates and runs at the same
speed regardless of activation dtype.

## The Actual Bottleneck

13 serial passes × (attention + FFN) per pass. Each pass must complete
before the next begins (data dependency). No per-operation optimization
can parallelize the passes.

At d=512 (v13): ~460ms per microbatch forward. Bearable.
At d=1280 (v14): ~2750ms per microbatch forward. 6× slower (d² scaling).

**The only fix is fewer passes.** → Redesigned to 8 passes (2 stacks).

## When These Techniques WOULD Work

1. **Lazy neurons:** After separate FFN plates develop per-stack sparsity
2. **Index sets:** On CPU inference (no AMX, addition genuinely cheaper)
3. **Fusion:** On architectures with many independent ops per pass
4. **Stream fusion:** At larger d where bandwidth becomes the bottleneck
5. **Float16:** On hardware where fp16 matmul is actually 2× faster

## Methodology Note

Each result was measured with controlled benchmarks:
- Isolated component timing (50 iterations, warmup)
- Full-pipeline timing with serial dependencies
- Multiple batch sizes (B=1, B=4)
- Correctness verification (max diff = 0.0 for exact methods)
- Sparsity measurement on actual model checkpoint (step 3000)

Hardware: Apple M3 Ultra, 512 GB unified memory, MLX framework.
