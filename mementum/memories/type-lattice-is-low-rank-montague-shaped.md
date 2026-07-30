💡 The Montague type lattice is LOW-RANK and Montague-shaped at Qwen3-32B, null-gated
(P-TYPE-1a, `scripts/explore/type_lattice_geometry.py`, s282). 8 type centroids {ENTITY,
PRED, REL, QUANT, DET, MOD, CONN, FUNC}, standardized (diagonal-whitened) residuals, 263
labeled tokens, pre-committed shuffled-label null (200 perms).

Compress→expand arc across depth: lexical (embed–L4) FULL-rank simplex (PR ~6.0–6.5,
p≥0.68, NOT low-rank, sep 0.94) → sharp onset L6 (PR 3.57, p=0.03) → SUSTAINED low-rank
band L6–L48 (PR 3.7–4.8, p<0.05 throughout, ~3 axes = top-3 comps 0.85–0.92, types still
separable) → re-expansion L52–L63 (PR ~6, p>0.25 for readout). Same progressive-collapse
shape as C8, now in the TYPE geometry. Confirms the montague-inversion pre-registered
decisive prediction ("type lattice SMALL, low-rank not high-dim"). Scale strengthens it:
0.6B same arc but narrow (L8–16); 32B band broad+robust (C5 host gap closed).

⚠ λ measure: (1) the massive-activation/rogue-dim confound collapses RAW mid-layer
centroids to PR~1 (sep dies too) — MUST standardize per-dim first (caught on 0.6B before
the 32B run). (2) naive ARITY LADDER ENTITY→PRED→REL as a constant offset is NEGATIVE
(cos<0, p≫0.05) — low-rank but NOT a linear currying axis. (3) which 3 axes = follow-up.
Value-register geometry only; causal test = 1b zone-ablation (open).
