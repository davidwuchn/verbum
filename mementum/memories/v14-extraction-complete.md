✅ Qwen3.6-27B → 593M ternary positions (148 MB), 375× compression

Session 145. Built and ran v14 extraction pipeline. Teacher: Qwen3.6-27B
(Apache 2.0, 27.8B, 64 layers, d=5120, hybrid Gated DeltaNet + Gated
Attention in [L,L,L,F]×16 pattern). Student: d=1280, d_ff=5120, 3 stacks
× 11 layers, hybrid GLA/SSA in [G,G,G,S,G,G,G,S,G,G,S] pattern.

Results:
- 142 arrays: 1 embedding (248320×80) + 132 attention (1280×80 each) + 9 FFN
- 593M ternary positions, 148 MB at 2 bits, 81 MB compressed NPZ
- Sign distribution: 50.1% negative, 49.9% positive, 0.0% zero
- All plates pure ±1 — no zeros in the base (clean extraction)
- Compression: 375× from 27.8B float16 teacher
- Time: 25.4 minutes CPU (SVD tomographic voting, 8 rotations)

Key architectural match:
- Teacher Gated DeltaNet (48 layers) → student GLA strides (linear attn)
- Teacher Gated Attention (16 layers) → student SSA strides (full attn)
- Teacher SwiGLU FFN → student holographic plates (zone-voted from 3 layers)
- Same tokenizer (BBPE, vocab 248320) → direct embedding extraction

The sign topology crosses architecture boundaries (proven r=0.998). Teacher
full_attn layer feeds student GLA plate and vice versa — the extraction
dispatches based on teacher layer type (what tensors exist) not student
layer type (how they'll be used).

Location: checkpoints/v14-extracted/
Pipeline: scripts/v14/{config.py, extract_qwen36.py}
