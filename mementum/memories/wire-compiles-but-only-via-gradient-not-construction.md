✅ WIRE-COMPILES (+GD-REQUIRED) @4B — the s295 backprop-compile door answered
POSITIVE. writeback_compile.py, Qwen3-4B, frozen gates (results 11092f7):

- **gd_cd** (backprop-compile, self-distill own CoT) installs a genuine linker
  wire: TRAIN 0.2→1.0, B1 held-landmark 0.125→0.938, B2 held-COUNTRY 0.545→1.0.
  G1 (B2 flip p=9e-4) / G2 (p=2.8e-3) / G3 (held p=1e-4) / G5 (ce≤base, g/h 1.0)
  all PASS.
- **construct** (zero-grad persistent product-keyed neurons) is INERT —
  byte-identical to base. The persistence-during-generation property did NOT
  install the wire → you cannot PLACE a wire by setting weights; gradient
  pressure is required.
- Not lookup: construct_lookup fails B2 (≈base ≪ gd_cd). Yardstick: gd_shuffle
  fails (0/0.167/0.167).
- **Tape NOT required**: gd_sft (answer-only, no CoT) also compiles
  (1.0/0.958/0.955); gd_cd edges it only on B2. Resolves gd_cd-vs-gd_sft = both.

CAVEATS: **G4 pin-mechanism UNMET** — predicted whitened-intermediate readout
did not rise (gd_cd det 0.156 ≤ base 0.169; ceiling makes "tracks success"
untestable) → behavioral wire without the internal signature; the HOW is open.
B2 not from-zero (base 0.545, famous capitals) — flip fills in, real & held-out.

CONVERGENCE (interpretation): construct=place magnitudes→inert;
gd=gradient/routing→wire. Confirms the s303 thesis "wires are a routing job,
not a magnitude one" from the weight-write side. Next: gd_cd@32B + a powered
mechanism probe (mid-training, before ceiling).
