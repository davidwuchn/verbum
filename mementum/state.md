# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-03 | Session: 064

## Where we are

**v10 rebuilt as prose LM. V6 compressor, Qwen3 tokenizer, Dolma training. Smoke tested.**

Session 064 fundamentally redesigned v10. The prior v10 (S-expr tokenizer,
3 strides, VSMNode tree dispatch) dropped everything that was proven in
v6-v9. The new v10 carries forward what worked:

### What was restored from v6
- **9 strides** (1, 8, 16, 32, 64, 128, 256, 512, 1024) — full scale hierarchy
- **StrideStack** — one SingleStrideAttention per stride, sequential composition
- **5-pass bidirectional VSM** — L0↑ → L1↑ → L2_apex → L1↓ → L0↓
- **Registers** — 3 named (type, scope, role), real-valued (d_register×2)
- **S4 intelligence** — register cross-attention scan per pass
- **S3 gating** — alignment-based phase gates per pass (5 instances)
- **Meta-S4 + Meta-S3** — retroactive pass reweighting + structural summary
- **Shared weights** across 5 passes (prep, stride_stack, consolidate, mod_projs, s4)
- **Spiral bias** α=1.18 — hyperbolic, scale-invariant
- **Additive modulation** — not multiplicative (prevents gradient explosion)
- **Relational loss** — r = (CE - E) / (log(V) - E) for phase awareness

### Key design decisions
1. **Qwen3 tokenizer** (vocab 151936, BBPE) — matches probes, real language
2. **Dolma prose** (3B tokens, 60 shards) — where the wavelet forms
3. **Next-token prediction** — the compressor IS the typing, trained via LM loss
4. **Single pipeline** — no parallel pathways needed (kernel provides ops, not pathways)
5. **Real-valued registers** — MLX autograd doesn't support complex in backward pass
6. **Kernel as future sieve target** — not integrated yet, comes after baseline

### Technical fix: TernaryLinear 1D autograd
MLX's `quantized_matmul` requires ≥2D input for backward pass. Components.py
uses `_ternary_1d()` helper to reshape 1D register projections to (1, dim).

## v10 architecture

```
tokens (Qwen3 BBPE) → [V6Compressor: 5-pass bidirectional, 9 strides]
                            │
                            ├── prep (TernaryFFN, d_ff=1536)
                            ├── converge (StrideStack, 9 strides, W=8)
                            ├── consolidate (TernaryFFN, d_ff=2048)
                            ├── S4 scan (register cross-attention)
                            ├── S3 gate (per-pass, alignment-based)
                            ├── Registers (type, scope, role × d=256)
                            ├── Meta-S3 (retroactive pass reweighting)
                            └── Meta-S4 (final structural summary)
                            │
                       → output_norm → tied embedding → logits
                       → CE loss (next-token prediction)
```

Smoke test: 60 steps, loss 13.8→11.5, r 1.19→0.95, 5K tok/s, 22M params.

## What to do next

### 1. Train v10 at scale
```bash
uv run python scripts/v10/train.py --seq-len 4096 --total-steps 20000
```
Watch for: φ-percolation across strides, Hilberg β convergence, S3 gate
differentiation, stratum analysis. This reproduces the v6 training at
scale with Qwen3 tokenizer.

### 2. Add sieve + kernel integration
After LM baseline is established, add the sieve pipeline between
compressor and output. Single pipeline, ternary topology routing to
kernel functions. The kernel (22 ops, proven) becomes a gravitational
attractor — easier than learning composition in weights.

Design: the sieve reads compressor multi-scale outputs, routes through
ternary topology constrained to kernel function families. Relational loss
steers topology. Next-token prediction provides the signal. The model
uses kernel functions because they're the path of least resistance.

### 3. Probing infrastructure
Port v6 probe.py for the new architecture:
- Per-stride compression ratios
- φ-deviation per pass
- Hilberg β estimation
- S3 gate values per pass
- Meta-S3 gate distribution
- Stratum analysis (prose, code, math, technical)
- Compile gate test

## Key files

| File | Purpose |
|------|---------|
| `scripts/v10/model.py` | V6Compressor as prose LM |
| `scripts/v10/attention.py` | StrideStack + SingleStrideAttention |
| `scripts/v10/components.py` | S4, S3, MetaS4, MetaS3 (real-valued registers) |
| `scripts/v10/config.py` | V10Config (Qwen3, 9 strides, v6 params) |
| `scripts/v10/data.py` | ShardedDataLoader for Qwen3 Dolma shards |
| `scripts/v10/train.py` | Training loop (LM loss, relational, evolution) |
| `scripts/v10/ternary.py` | TernaryLinear, TernaryEmbedding, evolution |
| `scripts/v10/kernel.py` | 22-op exact kernel (future sieve target) |

## Session history

→ See [session-history-049-062](knowledge/explore/session-history-049-062.md)
→ Session 063: pruned state.md, extracted history to knowledge pages
→ Session 064: rebuilt v10 as prose LM with v6 compressor + Qwen3
