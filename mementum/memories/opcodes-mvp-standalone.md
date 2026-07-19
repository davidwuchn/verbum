✅ opcodes/ MVP assembled (s265): 8 modules — topology (auto-detect incl.
readout paths) → capture (gate ∪ attn) → probes (535 bundled JSON, ≥50/comb)
→ classify (canonical home + measure_null_floor) → vsm (tree-of-VSM,
basis-parametric 9/8/16) → jspace (operand register on ModelTopology) →
trace (two-register + operand column) → sweep (registry=configs-not-forks,
restack → universal root). PyTorch+numpy only, data bundled, every module
self-tests without a big model, ruff clean. Extraction to a dedicated MIT
repo is now a mechanical step. Two lessons that must not be relearned:
smoke calibration (135 probes) is a pipeline check, never a measurement
(gc 0.344 vs 0.940 at full 535); null floors are register- AND
model-specific — measure per-run, never assume from another scale (0.6b
gate 2.78 > attn 2.14 REVERSES the 27B direction).
