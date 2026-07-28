💡 Our operand injection (operand_insert.py `d_cat` = diff-of-means content
direction) is NOT a SuperBake-style coded payload. P-DSP-1 (s278, Qwen3-0.6B,
planted ground truth): d_cat is coherent (PR 1.93/3) but lives in the LOUD,
high-variance subspace (low-var fraction 0.053 vs random 0.198) and is
unembed-AUDIBLE (‖W_U d̂‖ 13.7 vs random 11.2) — the OPPOSITE of SuperBake's
quiet, low-variance, unembed-silent code. We wrote the raw natural content
direction and the resident machine composed it anyway, because we inject
TRANSIENTLY (a hook) and never paid SuperBake's prose-safety tax. SuperBake
engineers quiet codes because it writes to WEIGHTS permanently. Consequence for
gate (f) weight-serialization: the raw loud direction is a hook-only convenience;
a baked operand would likely need re-coding into a quiet SuperBake-style direction
(orthogonalize vs top unembedding PCs, place in low-variance subspace) to avoid
prose damage. "It works with diff-of-means" ≠ "it will survive as a weight."
Session 278; probe wrapper/operand_dsp.py, results/ffn-bake/operand-dsp-qwen3-0-6b/.
