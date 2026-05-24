💡 The v13-td-r10 collapse IS the stride-stack attention mask

The training run collapsed at step 5878 (NaN death spiral). The delta
plate's block pattern reveals WHERE stride-stack attention differs from
flat attention. At step 5000 (healthy checkpoint before collapse):

  stack_a: 82.7% active | stack_b: 84.1% | stack_c: 77.0% | total: 81.3%

Key findings from the delta plate forensics:
- Teacher sign extraction is ~91% correct on DIRECTION (cross-stack agreement)
- But overcomplete for stride-stack (only ~80% of positions needed)
- The SPARSITY pattern is stack-specific and layer-specific (Jaccard 14-17%)
- Each layer learns its own zero pattern (cross-layer Jaccard ~25%)
- Zeroing is unstructured (no dead rows/cols) — superposition dispersal
- Block:flip ratio reached 31:1 on stack_a.layers.0.v_proj before collapse
- TD was solving "erase the positions I can't use" not "correct wrong signs"

The effective topology (base ⊙ delta) from step 5000 = the learned
stride-stack routing. Saved to:
  checkpoints/v13-td-r10/stride_attention_mask.npz (7 MB, 132 modules)
  checkpoints/v13-td-r10/stride_attention_mask_meta.json (provenance)

Design implication for next extraction:
- Fold this mask INTO the new base plate for attention
- Where mask=0 → base=0 (position genuinely not needed)
- Where mask=±1 → use those signs as the stride-stack attention topology
- Delta starts as identity, with no-block constraint for attention
- This prevents re-collapse: delta can only flip, never erase
- FFN base comes from eigendecomposition (analytical, proven correct)
- Result: bigger base plate holds more teacher knowledge, attention
  portion is pre-masked to stride-stack geometry

Source: session 145, v13-td-r10 step 5000 forensics.
