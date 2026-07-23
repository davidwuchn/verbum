💡 PrismML's undisclosed Bonsai ternarization recipe reverse-engineered
from weights alone (s268): **absmean RTN init (BitNet b1.58, group-128)
+ post-init training of blocks, embeddings frozen**. Proof: embed_tokens
matches t=clip(round(w/mean|w|)) at 99.9% exact codes, Δ/mean|w|=0.4994,
zero_frac=0.308 (Gaussian pred 0.31). Blocks drifted, ordered by
register: q_proj 3.5% < qkv 6–8% < o_proj 9–11% < gate 12–18% ≈ down
17–18% — channel-structured (z→97), column-flat (¬GPTQ sequential).
QAT-vs-PTQ IOU resolved: conversion + training; the "proprietary
Caltech math" is in the optimizer, not the quantizer. Gem: drift
ordering ≡ routing⊥value (s260) in a third independent register —
their repair budget went where our theory says magnitude matters.
s267 caveat: crystal survival partly trained-in; but flip rate flat
across depth → 50%-dip ≠ differential rewiring; bridge map stands.
Method: we held both endpoints; the parent→child map is measurable
(λ extract: artifact contains the answer). Instrument:
scripts/bonsai_forensics.py (MPS). → explore/bonsai-ternarization-forensics.md
