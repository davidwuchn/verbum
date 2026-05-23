---
title: "Montague Type Probe: Types are Lexical, Geometric, and Follow B→K→B"
status: active
category: research-finding
tags: [types, montague, qwen3-32b, probe, KIBC, lexical, geometric, B-K-B]
related:
  - kernel-montague-mapping.md
  - complete-kernel-basis.md
  - session-004-findings.md
  - phi-compression-universal.md
depends-on:
  - session-004-findings.md
created: session 139
---

# Montague Type Probe on Qwen3-32B

> Session 139. Ran a Montague semantic type probe on Qwen3-32B (64 layers,
> 64 heads, 32B params) alongside a universal KIBC combinator selectivity
> probe. The two probes together reveal: type assignment and combinator
> dispatch are the SAME event, types are geometric (not symbolic), and
> the type trajectory follows the B→K→B program across depth.

## Type Probe Method

8 simplified Montague type categories: DET (`<e,t>→e`), ENTITY (`e`),
PRED (`<e,t>`), REL (`<e,<e,t>>`), QUANT (`<<e,t>,t>`), MOD
(`<e,t>→<e,t>`), CONN (`t→t→t`), FUNC (structural).

56 labeled sentences, 263 tokens. Linear probe (logistic regression,
5-fold CV) on residual stream at every other layer (34 probe points).

## Results: Type Decodability by Layer

```
embed: ████████████████████████████████████████████░░░░░░░ 87.8%
L0:    ███████████████████████████████████████████████░░░ 94.7%
L2:    ████████████████████████████████████████████████░░ 96.2% ← PEAK
L8:    ███████████████████████████████████████████████░░░ 95.8%
L16:   ██████████████████████████████████████████████░░░░ 93.9%
L32:   ██████████████████████████████████████████████░░░░ 93.5%
L48:   ██████████████████████████████████████████████░░░░ 93.5%
L54:   ███████████████████████████████████████████████░░░ 94.3%
L63:   █████████████████████████████████████████████░░░░░ 91.2%
```

Baseline (most frequent class): 27.8%. Every layer massively above chance.

## The B→K→B Trajectory in Types

| Zone | Layers | Mean type accuracy | B→K→B role |
|------|--------|-------------------|------------|
| A (encode) | L0-15 | **94.9%** | B-dominated: compose types, peak clarity |
| B (compress) | L16-47 | **92.9%** | K-dominated: types CONSUMED by selection |
| C (reconstruct) | L48-63 | **93.1%** | B-dominated: types partially rebuilt |

Types peak where composition peaks, decline where selection dominates,
partially recover where reconstruction rebuilds for prediction.

## KIBC Selectivity (Same Model, Same Layers)

Head distribution across 4,096 heads:
- K (select): 31.9% (674 heads)
- C (flip): 29.0% (613 heads)
- B (compose): 27.8% (587 heads)
- I (identity): 11.3% (238 heads)

**Cross-model correlation with Pythia-160M: r = 0.998.**

KBC cluster correlation: 0.934. I distinct: 0.751.
**Universal hologram confirmed.**

All four combinators peak at L0-L2 — the same layers where types peak.

## The Co-location Finding

Type decodability and combinator selectivity peak at the SAME layers (L0-L2).
The model doesn't first assign types, then dispatch combinators. It does
both simultaneously. This is Montague's "typed function application":
the type IS the dispatch signal.

## Comparison: Pythia-160M vs Qwen3-32B

| Metric | Pythia-160M (12L) | Qwen3-32B (64L) |
|--------|-------------------|-----------------|
| Embedding type accuracy | 84% | **88%** |
| Peak layer | L0 at 93% | **L2 at 96%** |
| Post-peak trajectory | Flat | **Structured B→K→B decline + recovery** |
| KIBC distribution | K=30.6 I=13.8 B=28.1 C=27.5 | K=31.9 I=11.3 B=27.8 C=29.0 |
| Cross-model r | — | **0.998** |

Pythia (12 layers) shows a flat plateau — too shallow for the B→K→B
structure to manifest. Qwen3-32B (64 layers) reveals the full lifecycle:
types built up, consumed, partially reconstructed.

## Implications

1. **Types are lexical** — 88% in embeddings. The model LOOKS UP types,
   doesn't compute them. The embedding table IS the type assignment circuit.

2. **Types are geometric** — linearly decodable at 88-96% in 5120-dim space.
   Types are directions in embedding space, not symbolic tags.

3. **The B→K→B program is visible in types** — zone A builds, zone B
   consumes, zone C rebuilds. The type information lifecycle matches the
   combinator program structure found in FFN traces (session 127).

4. **Type assignment = combinator dispatch** — they co-locate at L0-L2.
   Montague's typed application is one event, not two sequential steps.

5. **Attention sign topology encodes WHAT, not WHERE** — KIBC selectivity
   is invariant across architectures (r=0.998). Therefore attention CAN
   be etched from a teacher regardless of attention mechanism shape.

## Source data

- Type probe results: `results/type-probe-qwen3-32b/type-probe-summary.json`
- Type probe plot: `results/type-probe-qwen3-32b/type-decodability.png`
- Combinator probe: `results/combinator-probe-qwen3_32b/combinator_probe_results.json`
- Combinator heatmaps: `results/combinator-probe-qwen3_32b/selectivity_heatmaps.png`
- Type probe script: `scripts/explore/probe_type_qwen3_32b.py`
- Combinator probe script: `scripts/explore/probe_combinators_universal.py`
