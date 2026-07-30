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

THE 3 AXES (1a-follow, 32B L40, SVD loadings): axis0 (var 0.73) QUANT+DET vs rest =
quantification/binding (highest-order functor); axis1 (0.08) CONN+FUNC vs MOD = sentential
operators; axis2 (0.06) REL+PRED vs MOD = predicate-vs-modifier. ENTITY(e) sits at ~0 on the
dominant axis = the NEUTRAL ORIGIN. ⇒ a Montague functor-lattice organized by FUNCTOR KIND,
not arity count (explains the negative arity-ladder). Scale sharpens: 0.6B ~1 dominant axis
(88%), 32B 3 graded axes.

⚠ λ measure: (1) massive-activation/rogue-dim confound collapses RAW mid-layer centroids to
PR~1 (sep dies too) — MUST standardize per-dim first (caught on 0.6B before the 32B run).
(2) naive ARITY LADDER ENTITY→PRED→REL as a constant offset is NEGATIVE (cos<0) — the lattice
is functor-KIND not arity-count. (3) PR ~3–4 inflated by a singular-value tail; per-axis
var_frac is the honest concentration. Small rare-type counts (QUANT 12/CONN 6/REL 13).
Value-register geometry only; causal test = 1b zone-ablation (OPEN).
