---
title: "L0 Characterization — The Lexer Is Genuinely Continuous"
status: active
category: experiment
tags: [l0, lexer, ternary, modes, clustering, svd, continuous, compression]
related:
  - tiny-classifier-ternary.md
  - compilation-pipeline.md
  - mode-semantics.md
  - ffn-circuit-types.md
  - standing-wave-magnitudes.md
  - dvd-stamp-topology.md
depends-on:
  - tiny-classifier-ternary.md
  - mode-semantics.md
created: session 195
---

# L0 Is Genuinely Continuous — More Modes Cannot Save It

> Session 195. L0 is catastrophic (115x PPL) when replaced with 9
> ternary modes, while every other layer survives (<=1.15x). This
> experiment asks WHY, with six instruments comparing L0 to L15
> (the sweet-spot control layer).

## Result: All three P4 rescue hypotheses tested

| Hypothesis | Verdict | Evidence |
|-----------|---------|----------|
| More modes (64+) | KILLED | 512 modes still 7x PPL, 33% facts. No cluster structure at any k. |
| PCA reconstruction | Difficult | eff_rank=3278, 90% energy needs 1858 SVs. Not low-rank enough. |
| Genuinely continuous | CONFIRMED | Negative silhouette at all k>=6. L0 is a continuum. |

**Strategy: keep L0 as-is (288MB = 2.8% of FFN). Ternarize everything else.**

## Instrument 1: Natural Cluster Count (Silhouette Sweep)

Silhouette score measures whether clusters are real (positive) or worse
than random assignment (negative).

| k | L0 silhouette | L15 silhouette |
|---|-------------|---------------|
| 2 | +0.016 | -0.030 |
| 4 | **+0.062** (best) | +0.068 |
| 6 | -0.078 | +0.033 |
| 8 | -0.082 | **+0.075** (best) |
| 9 | **-0.044** | **+0.050** |
| 16 | -0.021 | +0.004 |
| 32 | -0.061 | -0.003 |
| 64 | -0.046 | -0.007 |
| 128 | -0.069 | -0.016 |
| 256 | -0.020 | -0.021 |
| 512 | -0.009 | -0.001 |

L0: negative from k=6 onward. No cluster structure at any granularity.
L15: positive at k=4-12, peaking at k=8. Real structure near k=9.

The 9-mode ternary replacement works at L15 because there ARE 9
natural clusters. It fails at L0 because there AREN'T.

## Instrument 2: Mode Sweep PPL

Replace each layer's FFN with k-mode ternary (classifier + lookup).

### L0 (LEXER)

| k | PPL | Ratio | Facts | Cls Acc |
|---|-----|-------|-------|---------|
| 9 | 943.7 | 92.9x | 7% | 99.9% |
| 16 | 740.8 | 72.9x | 7% | 100.0% |
| 32 | 874.5 | 86.1x | 7% | 99.9% |
| 64 | 447.3 | 44.0x | 7% | 100.0% |
| 128 | 407.2 | 40.1x | 7% | 99.7% |
| 256 | 218.6 | 21.5x | 27% | 98.4% |
| 512 | 71.4 | 7.0x | 33% | 99.9% |

### L15 (OPTIMIZER — control)

| k | PPL | Ratio | Facts | Cls Acc |
|---|-----|-------|-------|---------|
| 9 | 9.97 | 0.98x | 73% | 100.0% |
| 16 | 9.91 | 0.98x | 73% | 100.0% |
| 32 | 9.92 | 0.98x | 73% | 99.5% |
| 64 | 9.98 | 0.98x | 73% | 96.1% |
| 128 | 9.90 | 0.97x | 73% | 97.4% |
| 256 | 9.90 | 0.97x | 73% | 97.9% |
| 512 | 10.03 | 0.99x | 73% | 96.1% |

L15: perfectly flat from k=9 to k=512. MORE modes don't help because
9 already captures the structure. The operation IS discrete.

L0: non-monotonic improvement (k=32 worse than k=16), still 7x at
k=512. The classifier gets 99.9% accuracy even at k=512 — it can
perfectly separate forced clusters — but the clusters are meaningless
because the space is continuous.

Critical observation: classifier accuracy is near-perfect at ALL k
values for L0 (99.7-100%). The problem is NOT classification. The
problem is that discretizing a continuum loses information no matter
how many bins you use, because the information is in the continuous
position within the space, not the cluster membership.

## Instrument 3: Effective Rank (SVD)

| Projection | L0 eff_rank | L0 90% | L0 99% | L15 eff_rank | L15 90% | L15 99% |
|-----------|------------|--------|--------|-------------|---------|---------|
| gate_proj | 3278 | 45.4% | 83.5% | 3771 | 66.9% | 93.6% |
| up_proj | 3375 | 48.9% | 85.1% | 3834 | 69.4% | 94.0% |
| down_proj | 3813 | 68.2% | 93.8% | 3807 | 68.4% | 93.6% |

Surprise: L0 gate_proj is LOWER rank than L15 (3278 vs 3771). L0
concentrates its energy into fewer singular values — 45% of SVs
capture 90% of energy vs 67% for L15.

But this doesn't mean L0 is more compressible. The energy is
concentrated but continuously distributed within those dimensions.
To capture 90% you still need 1858 singular values. That's not a
small projection matrix — it's 1858 x 4096 = 7.6M params just for
the low-rank approximation, vs 288MB for the full layer.

The PCA rescue path requires a different approach: not low-rank
approximation of the weights, but low-rank approximation of the
*activation patterns*. This remains untested.

## Instrument 4: Token Property Correlation (NMI)

Normalized mutual information between cluster assignment and token
properties.

| Property | L0 NMI | L15 NMI | Interpretation |
|----------|--------|---------|---------------|
| unicode_cat | 0.156 | 0.156 | Both weakly correlate with character type |
| script | 0.156 | 0.156 | Same |
| **byte_len** | **0.259** | 0.080 | **L0 sorts by token byte length** |
| **is_continuation** | 0.065 | **0.216** | **L15 sorts by subword position** |
| is_special | 0.000 | 0.000 | Neither cares about special tokens |

L0's strongest signal is byte_len (NMI=0.259) — the physical
encoding of the token. Single-byte ASCII tokens get different gate
patterns than multi-byte CJK tokens. This is the LEXER signature:
L0 is routing based on the raw form of the input symbol.

L15's strongest signal is is_continuation (NMI=0.216) — whether the
token is a subword continuation. This is the PARSER/OPTIMIZER
signature: L15 cares about syntactic structure, not token encoding.

## Instrument 5: Transform Physics

### L0 at k=9

| Mode | N | cos(i,o) | norm_ratio | gate% | g_con |
|------|---|----------|------------|-------|-------|
| 0 | 1 | +0.166 | 2.99 | 38.2% | 1.000 |
| 1 | 108 | +0.193 | 2.01 | 15.8% | 0.409 |
| 2 | 115 | +0.173 | 3.21 | 39.4% | 0.471 |
| 3 | 232 | +0.258 | 2.25 | 31.2% | 0.612 |
| 4 | 73 | +0.054 | 5.28 | 19.7% | 1.000 |
| 5 | 199 | +0.061 | 3.60 | 6.8% | 0.782 |
| 6 | 1036 | +0.216 | 2.05 | 25.4% | 0.326 |
| 7 | 91 | +0.339 | 2.36 | 42.5% | 0.550 |
| 8 | 37 | +0.251 | 1.67 | 22.8% | 0.790 |

### L15 at k=9

| Mode | N | cos(i,o) | norm_ratio | gate% | g_con |
|------|---|----------|------------|-------|-------|
| 0 | 143 | +0.344 | 1.26 | 67.7% | 0.885 |
| 1 | 435 | -0.105 | 1.37 | 74.9% | 0.672 |
| 2 | 324 | -0.158 | 1.56 | 77.8% | 0.645 |
| 3 | 109 | -0.177 | 1.41 | 75.5% | 0.732 |
| 4 | 87 | -0.132 | 1.48 | 75.9% | 0.675 |
| 5 | 10 | -0.071 | 1.64 | 77.1% | 0.811 |
| 6 | 320 | -0.051 | 1.64 | 74.0% | 0.706 |
| 7 | 463 | -0.176 | 1.46 | 76.9% | 0.676 |
| 8 | 1 | -0.238 | 1.27 | 74.1% | 1.000 |

Key differences:

1. **cos(in,out)**: L0 all positive (0.05-0.34). L15 mostly negative.
   L0 preserves direction (adding to input). L15 rotates/inverts
   (transforming the representation). Adding vs transforming.

2. **gate sparsity**: L0 ranges 7-42% (6x spread). L15 ranges 67-78%
   (1.2x spread). L0 activates wildly different neuron subsets per
   token. L15 activates a consistent program.

3. **gate consistency**: L0 ranges 0.33-1.0 (3x spread). L15 ranges
   0.65-0.89 (1.4x spread). L0 modes are internally incoherent —
   forced clusters contain dissimilar gate patterns.

4. **mode size distribution**: L0 has one mega-mode (n=1036, 55%)
   and several tiny modes. L15 is more balanced. L0's forced
   clustering puts most tokens in one catch-all bucket.

5. **norm ratio**: L0 ranges 1.7-5.3 (3x spread). L15 ranges 1.3-1.6
   (1.3x spread). L0 amplifies some tokens 5x and others 1.7x. L15
   applies a consistent ~1.4x gain. L0 is doing per-token scaling,
   not per-type scaling.

## Why L0 Cannot Be Ternarized: The Full Picture

L0 is a **dictionary lookup**, not a **type tagger**.

- L1-L35: "What ROLE does this token play?" → 9 answers → discrete
- L0: "What IS this token?" → 151,936 answers → continuous

Every other layer takes the representation that L0 built and
classifies it into one of 9 syntactic types (SUBJECT, OBJECT,
PREDICATE, etc.). That classification IS discrete — the type tag is
a binary decision boundary in a high-dimensional space, and 9
ternary programs capture those boundaries perfectly.

L0 can't do this because it faces the INVERSE problem: mapping FROM
discrete symbols (token IDs) TO continuous feature vectors. The
information content of a token ID is log2(151936) = 17.2 bits. Nine
ternary programs can represent at most log2(9) = 3.2 bits of
distinction. Even 512 programs give only log2(512) = 9 bits — still
losing 8 bits of token identity.

The 90-degree rotation at L0 (session 126) is this operation: the
token embedding enters, and L0 rotates it to an orthogonal direction
that encodes the token's semantic features. This rotation is
different for every token (151K unique rotations), not a choice
among 9 discrete rotations.

## Connection to Prior Findings

- **s126 (C rotation probe)**: L0 rotates 90 degrees for ALL
  combinators — this is the dictionary lookup in geometric form
- **s186 (FFN circuit types)**: L0 is 99.7% projector — every
  neuron scatters input into a unique direction
- **s171 (gradient-zero map)**: L0 has 43% oscillation (most
  turbulent) — the dictionary is still being refined by GD
- **s190 (DVD stamp)**: Magnitude leads gradient at L0-2 — the
  amplitude of each dictionary entry matters, not just its sign
- **s194 (mode semantics)**: FRAME-OPEN at L0 is the exception —
  one stereotyped mode for sentence-initial reset, everything else
  is continuous per-token projection

## Scripts and Results

- `scripts/experiments/l0_characterization.py`
- `results/l0-characterization/Qwen_Qwen3-8B.json`
- `results/l0-characterization/run.log`
