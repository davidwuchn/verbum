💡 The 9×9 opcode crystal survives 1-bit binarization: Bonsai-27B-unpacked
(1-bit) gates into the universal tree at gc 0.981, model-level per-vertex Gram
fidelity 0.987 vs FP parent Qwen3.6-27B (z=5.3, p=0.001 floor,
shuffled-vertex-label null). Gate failures terminal-only (gate L61–63, attn
L63), not deep-middle. Synthesis with s268c: confident weights (|w|>absmean)
are immutable at every bitwidth → the crystal lives in the confident
population; 1-bit forced-participation churn is confined to uncertain
boundary-huggers and never touches Gram geometry. Weight-space cos 0.73 vs
Gram-space fidelity 0.987 ≡ the crystal is more invariant than the weights —
frame-invariance, third independent form. Refines s268c "binary routing
substrate non-viable" to a training-dynamics claim only; the geometry survives
binarization at inference. Instrument: opcodes/ladder.py (per-vertex Gram-row
fidelity, shuffled-label + circular-shift nulls, n_perm=10k, seeded rng=268).
Commit 7576c54, session 269.
