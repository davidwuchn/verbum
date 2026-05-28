❌ NaN death loop: softmax overflow + broken rollback = 10h Sisyphus

**What happened:** Step 4369 hit NaN. Auto-rollback restored model weights to
step 4000 (npz) but NOT Adam state (still step 4360+), data position, or TD
moments. Model/optimizer mismatch → deterministic NaN every time → 154 rollbacks
in 10 hours, all landing on the same NaN at step ~4369.

**Root cause (NaN):** Attention softmax overflow. `(Q @ K^T) * scale` produces
unbounded logits. With ternary weights + learned gamma scales, attention scores
can exceed 88.7 (float32 exp limit). No clamping existed before softmax.

**Root cause (loop):** Auto-rollback was a partial restore — model weights only.
Adam moments carry directional memory from 360 steps of training. Snapping
weights back while keeping stale momentum = huge step in wrong direction = NaN
on first step after every rollback.

**Fix:** (1) `mx.clip(attn, -65, 65)` before softmax. (2) Remove auto-rollback
entirely — 3 NaN → stop + diagnostic report. (3) `restore_safetensors.py` for
clean full-state recovery from npz checkpoints. Recovery is a human decision.

**Data was clean.** Investigated shard 19, all chunks normal tokens. NaN was
model-internal, not data-driven.
