💡 The constructor-grain TYPE register (kind=atom/fn/app as a cross-cutting
routing direction, §P-TYPE-GRAM-1) is REAL but NOT architecture-universal.
10-model registry sweep (s314): TYPE-REGISTER in 7/11 — Qwen3 across the
full ladder (0.6B→32B), OLMo-2-13B, Gemma; OPCODE-FLAVOR-ONLY in 4/11 — the
ENTIRE Pythia ladder (14m/160m/410m/2.8b).

The split is by FAMILY, not scale. Every modern code/math-heavy recipe
carries it; Pythia (Pile-2021) does not. TG1 passes for pythia (kind
structure exists) but TG2 CROSS-CUT fails — kind is opcode-BOUND, not an
independent register. Genuine negative, not underpowered: pythia-2.8b has
n_gated 32 and the HIGHEST coherence (0.867) in the sweep, yet TG2 p=0.17.
Read the negative from the well-powered members, not the small ones.

Contrast: the 9×9 routing crystal is 11/11 (present even in pythia) — it
makes a transformer a reducer. The TYPE register sits one layer up and is
CONTINGENT: types are LEARNED on the universal reducer when the training
distribution demands typed composition. Direct evidence for M7 (typed
apply is emergent, not given). +POLED sub-split is weaker/model-specific
(not monotone in scale) — don't over-read. S5 scorecard 2/4: discreteness✓
selectivity✓(now cross-family) compositionality✗ causality✗.
Results da8c1ba (qwen3-4b) + s314 sweep commit.
